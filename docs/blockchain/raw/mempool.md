# MEMPOOL

| Field | Value |
| --- | --- |
| Name | Mempool |
| Slug | 245 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors |  |

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-09-01 |

# Introduction

The mempool is a node's store of Mantle Transactions that have been submitted but are not yet in the canonical chain. It disseminates those transactions, supplies them to block building, and resolves the references a block proposal carries in place of transaction bodies.

# Constants

| Constant | Name | Description | Value |
| --- | --- | --- | --- |
| `TRANSACTION_TTL` | Transaction Time To Live | How long a transaction may stay pending before it is retired. | 24 hours |
| `PULL_PROTOCOL` | Pull Protocol | The libp2p request-response protocol carrying confirmation queries. | `/logos-blockchain/mempool-pull/{version}` for mainnet, `/logos-blockchain-testnet/mempool-pull/{version}` for testnet |
| `PULL_DELAY` | Pull Delay | How long a transaction must have been pending before a node queries about it. | 10 seconds |
| `PULL_INTERVAL` | Pull Interval | The period between confirmation rounds. | 2 seconds |
| `PULL_SAMPLE_SIZE` | Pull Sample Size | Providers queried per round. | 32 |
| `PULL_MAX_BATCH` | Pull Batch Size | The most transactions one query may name. | 1024 |
| `PULL_MAX_ROUNDS` | Maximum Pull Rounds | Rounds a node spends on one transaction. | 8 |
| `PULL_CONFIRMATIONS` | Confirmation Threshold | Distinct providers that must attest before a transaction is confirmed. | 133 |

`PULL_SAMPLE_SIZE * PULL_MAX_ROUNDS` is the most providers one transaction is asked about. Two constraints bind it:

- `PULL_CONFIRMATIONS` must not exceed it. A larger threshold confirms nothing, and no transaction is ever selected.
- The active [attester](#attesters) set must be large enough that `PULL_SAMPLE_SIZE * PULL_MAX_ROUNDS` draws reach `PULL_CONFIRMATIONS` distinct providers that hold the transaction. A sample drawn from a small set repeats providers already in `queried`, which the round then omits from the query, so the reachable count falls below the draw count. The values above are calibrated for 5000 active declarations and an adversary holding one third of them.

Raising `PULL_SAMPLE_SIZE * PULL_MAX_ROUNDS` without raising `PULL_CONFIRMATIONS` gives an adversary more draws against the same threshold.

# Mempool State

```python
class Mempool:
    pending: TimeOrderedSet[TxHash]              # admitted, not yet retired, in admission order
    bodies: Map[TxHash, SignedMantleTx]          # transaction bodies
    admitted_at: Map[TxHash, Timestamp]          # admission time, per pending transaction
    by_prefix: Map[bytes, Set[TxHash]]           # pending hashes, keyed by reference prefix
    commitment: Map[TxHash, Hash]                # body commitment, computed at admission
    attesters: Map[TxHash, Set[ProviderId]]      # providers that attested to holding it
    queried: Map[TxHash, Set[ProviderId]]        # providers that answered a query about it
    received_from: Map[TxHash, Set[ProviderId]]  # providers the transaction arrived from
    rounds: Map[TxHash, uint8]                   # confirmation rounds spent
```

A transaction is keyed by `mantle_txhash(tx)`, defined in [Mantle](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash).

`by_prefix` maps `prefix(hash, REFERENCE_PREFIX_LENGTH)` to the pending hashes carrying that prefix, where `REFERENCE_PREFIX_LENGTH` is defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#references).

`pending` holds each hash once, ordered by admission time. `insert_by` places a hash at the position its admission time gives it, which is not the end when a [Reorganisation](#reorganisation) re-admits a transaction.

A transaction is **confirmed** when `len(attesters[key]) >= PULL_CONFIRMATIONS`.

`queried` records a provider once it answers a query naming the transaction, whether it answered yes or no. A provider that does not answer is not recorded, and a later round may sample and ask it again.

A node adds a provider to `received_from` when a copy of the transaction arrives from it by gossip. A provider's `provider_id` is its node identity, as required by [Locators](bedrock-service-declaration-protocol.md#locators), so the peer a message arrives from is a provider exactly when that identity is in the active snapshot. A peer that is not is never sampled and is not recorded.

A node keeps its outstanding queries outside `Mempool`: the nonce of each query in flight, the provider it went to, and the transactions it named. A restart discards them.

# Transaction Admission

A transaction reaches the mempool by local submission through the [Node API](#node-api), by gossip on the mempool topic, or by re-insertion after a [Reorganisation](#reorganisation). All three follow this procedure.

```python
def admit(mempool, encoded: bytes, at: Timestamp = None) -> Result:
    if len(encoded) > MAX_BLOCK_SIZE:
        return Reject(TransactionTooLarge)

    tx = decode_signed_mantle_tx(encoded)     # rejects trailing bytes
    if tx is None:
        return Reject(Malformed)

    if not preverify(tx):
        return Reject(FailedStatelessValidation)

    key = mantle_txhash(tx)
    if key in mempool.pending:
        return Duplicate(key)

    mempool.bodies[key] = tx
    mempool.admitted_at[key] = at if at is not None else now()
    mempool.pending.insert_by(key, mempool.admitted_at[key])
    mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
    mempool.commitment[key] = Hash("LOGOS_MEMPOOL_BODY_V1" || encode(tx.tx))
    return Accept(key)
```

Admission reads the transaction and the mempool. It must not read ledger state. A node must not treat membership of the mempool as evidence that a transaction can be applied.

`MAX_BLOCK_SIZE` is defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants).

## Decoding

The payload is the canonical encoding defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md), carried in the envelope defined in [Network Wire Format](network-wire-format.md). Decoding must consume the payload exactly.

## Stateless Validation

`preverify` applies the subset of the [Mantle validation rules](bedrock-v1.1-mantle-specification.md#validation) that reads no ledger state:

1. The transaction carries one proof entry per operation, which may be the `None` entry where the opcode admits one.
2. Each proof entry has the type its operation's opcode requires.
3. Each proof bound only to the transaction hash and the operation payload verifies.

## Reorganisation

When a fork switch displaces blocks from the canonical chain, the node re-admits the transactions they carried that the blocks now in the canonical chain do not carry, and broadcasts them. It re-admits each with its original admission time.

## Duplicates

`admit` reports a duplicate. The caller decides what follows:

- A duplicate received by gossip is dropped.
- A duplicate received by local submission is answered as success, and the transaction is broadcast again.

# Dissemination

Transactions are disseminated by gossipsub on the mempool topic defined in [P2P Network](../draft/p2p-network.md#gossiping).

The message identity of a message on that topic is the Blake2b-256 digest of its payload bytes. Implementations must not use gossipsub's default source-and-sequence-number identity.

A node relays a received message to its mesh neighbours on receipt, before admission.

A node broadcasts a transaction it admits by local submission or by re-insertion. It does not broadcast a transaction it received by gossip.

# Confirmation

A node confirms a transaction by asking sampled providers whether they hold it.

## Attesters

The attesters are the Blend Network (`BN`) declarations active in the [Service Declaration Protocol](bedrock-service-declaration-protocol.md) snapshot of the current epoch, defined in [Snapshots](bedrock-service-declaration-protocol.md#snapshots). A declaration supplies the `provider_id` and `locators` a querier uses to reach the provider.

## The Pull Exchange

```python
class PullQuery:
    nonce: bytes32                  # fresh, chosen by the querier
    tx_hashes: list[TxHash]         # at most PULL_MAX_BATCH entries

class PullResponse:
    nonce: bytes32
    held: bitmap                    # one bit per queried hash, in query order
    signature: Ed25519Signature
```

`held` carries one bit per entry of `tx_hashes`, in query order, packed least significant bit first and padded with zero bits to a whole number of bytes. `Hash` is the general-purpose hash function of [Common Cryptographic Components](common-cryptographic-components.md).

```python
witness = Hash("LOGOS_MEMPOOL_PULL_WITNESS_V1"
            || nonce
            || uint16(count(held))
            || concat(commitment[tx] for tx in query.tx_hashes where held))

signature = Ed25519.sign(provider_sk,
                         Hash("LOGOS_MEMPOOL_PULL_RESPONSE_V1"
                           || nonce || held || witness))
```

The witness is not carried in the response. The querier recomputes it from its own copies of the marked transactions, and a provider that does not hold one of them cannot produce a signature over the value the querier recomputes.

A querier accepts a response as an attestation for a transaction when all of the following hold:

1. `nonce` matches an outstanding query, and no response to that query has been accepted.
2. `signature` verifies, under the `provider_id` that query was sent to, over the value recomputed from `nonce`, `held` and the querier's own copies of the marked transactions.
3. The bit for that transaction is set.

A provider that does not hold a queried transaction answers that it does not. It must not request the transaction, and the querier must not send it.

A provider rate-limits queries per peer and may decline to answer.

## Confirmation Rounds

Every `PULL_INTERVAL`, a node:

1. Collects every pending transaction that is unconfirmed, has been pending for at least `PULL_DELAY`, and has spent fewer than `PULL_MAX_ROUNDS` rounds. If more than `PULL_MAX_BATCH` qualify, it takes the oldest by admission time.
2. Samples `PULL_SAMPLE_SIZE` providers uniformly at random from the active snapshot, excluding itself. The sample must be drawn from local randomness and never from a chain-derived seed.
3. Sends each sampled provider a query with a fresh nonce, naming the collected transactions for which that provider is in neither `queried` nor `received_from`. It sends no query to a provider excluded by every transaction in the batch.
4. Increments `rounds` for every transaction it collected in step 1.
5. On each response whose signature verifies, adds the provider to the `queried` set of every transaction that query named, and to `attesters` for every transaction whose bit is set.

A node must not exclude the union of `queried` across the batch. Exclusions apply per transaction.

An accepted attestation stays valid while the transaction is pending, and is not re-evaluated against a later snapshot.

# Block Building View

The mempool supplies the bodies of every pending transaction in admission order.

A leader makes two determinations over that view.

**Applicability.** The leader determines which transactions apply:

1. Apply the block header to the ledger state. This is the working state.
2. Pass over all pending transactions in admission order. Apply each transaction that succeeds to the working state.
3. Repeat step 2 until a pass applies no transaction.

No block limit applies to this computation. A transaction that never applies is retired, as specified in [Inapplicability](#inapplicability).

**Selection.** The leader fills the block from the applicable transactions that are confirmed, in the same order, stopping at the first transaction that would exceed `MAX_BLOCK_TXS` or `MAX_BLOCK_SIZE`, both defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants). A transaction left unselected is not retired.

Confirmation governs selection only. Applicability, retirement and [Reference Resolution](#reference-resolution) must not read it.

Confirmation is not a condition of block validity. A block carrying an unconfirmed transaction is valid, and a validator must not evaluate confirmation when it validates one.

# Reference Resolution

A block proposal carries a `REFERENCE_PREFIX_LENGTH`-byte prefix of each transaction hash, as defined in [References](bedrock-v1.1-block-construction.md#references). A validator resolves each reference against the mempool.

```python
def resolve(mempool, reference) -> Optional[SignedMantleTx]:
    matches = mempool.by_prefix.get(reference, empty_set)
    if len(matches) != 1:
        return None
    return mempool.bodies[single(matches)]
```

A reference resolves only when the match is unique. Zero matches and two or more matches are both unresolved. A non-unique match must not be searched.

Resolution reads the proposal, `by_prefix` and `bodies`. It must not read the node's chain state, its peer set, or the order in which transactions were admitted.

How a validator uses the result, and what a failure to resolve establishes about the block, are specified in [Block Proposal Reconstruction](bedrock-v1.1-block-construction.md#block-proposal-reconstruction) and [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation).

# Retirement

A transaction leaves `pending` for one of three reasons.

## Inclusion in a Canonical Block

When a block enters the node's canonical chain, the transactions it carries are retired.

## Inapplicability

A transaction that the applicability determination of [Block Building View](#block-building-view) never applies is retired.

## Expiry

A pending transaction whose age exceeds `TRANSACTION_TTL` is retired.

## Effects of Retirement

Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at`, `attesters`, `queried`, `received_from` and `rounds` entries, its body and its `commitment`.

A retired transaction that is gossiped again is admitted again.

# Persistence and Recovery

A node persists the pending hashes, their admission timestamps, their `attesters`, `queried`, `received_from` and `rounds` entries, the body commitments, and the transaction bodies. It persists these for every pending transaction, confirmed or not.

A node does not persist `by_prefix`. It rebuilds the index from the recovered pending set.

# Node API

A node exposes the mempool to local clients. These endpoints are operational and carry no consensus meaning.

| Operation | Description |
| --- | --- |
| Submit transaction | Admit a transaction by local submission and broadcast it. Returns the outcome of [Transaction Admission](#transaction-admission). |
| View | The hashes of the pending transactions. |
| Status | For each queried hash, whether the transaction is unknown to this node, pending, or pending and confirmed. |
| Metrics | The number of pending transactions, how many are confirmed, and the time of the most recent admission. |

# References

- [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)
- [Common Cryptographic Components](common-cryptographic-components.md)
- [Cryptarchia Protocol](cryptarchia-v1-protocol.md)
- [Mantle](bedrock-v1.1-mantle-specification.md)
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
- [Network Wire Format](network-wire-format.md)
- [Service Declaration Protocol](bedrock-service-declaration-protocol.md)
- [P2P Network](../draft/p2p-network.md)
