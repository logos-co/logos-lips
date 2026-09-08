# MEMPOOL
| Field | Value |
| --- | --- |
| Name | Mempool |
| Slug | 245 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors |  |

<!-- timeline:start -->

## Timeline
- **2026-09-04** — [`5de1e93`](https://github.com/logos-co/logos-lips/blob/5de1e9348b010157222d99fbac2649e5e68aa278/docs/blockchain/raw/mempool.md) — docs(blockchain): retire on joining the chain, not on becoming the tip
- **2026-09-02** — [`15e9269`](https://github.com/logos-co/logos-lips/blob/15e92695a7a5b3c23b0b1528a2dd33beb42eceb9/docs/blockchain/raw/mempool.md) — docs(blockchain): drop mempool state that nothing reads
- **2026-09-01** — [`6a9d9c9`](https://github.com/logos-co/logos-lips/blob/6a9d9c98df738c49489a1911abff1741fb5d1ae0/docs/blockchain/raw/mempool.md) — docs(blockchain): remove restated and non-normative text
- **2026-08-24** — [`8e11a5f`](https://github.com/logos-co/logos-lips/blob/8e11a5f027660e97c925c4d0fc6d645f1673d4bd/docs/blockchain/raw/mempool.md) — docs(blockchain): add the mempool specification

<!-- timeline:end -->

# Revision History
| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-09-01 |

# Introduction

The mempool is a node's store of Mantle Transactions that have been submitted but are not yet in the canonical chain.

# Overview

Each node keeps its own mempool. Nodes admit and retire independently, so their pending sets differ.

A transaction is admitted, disseminated, offered to block building, and retired.

# Construction
## Constants
| Constant | Name | Description | Value |
| --- | --- | --- | --- |
| `TRANSACTION_TTL` | Transaction Time To Live | How long a transaction may stay pending before it is retired. | 24 hours |
| `PULL_PROTOCOL` | Pull Protocol | The libp2p request-response protocol carrying confirmation queries. | `/logos-blockchain/mempool-pull/1.0.0` for mainnet, `/logos-blockchain-testnet/mempool-pull/1.0.0` for testnet |
| `PULL_HOP_ALLOWANCE` | Pull Hop Allowance | Time allowed for a transaction to cross one gossip hop. | 2 seconds |
| `PULL_DELAY` | Pull Delay | How long a transaction must have been pending before a node queries about it. | `PULL_HOP_ALLOWANCE * ceil(log_D(N))`, where `N` is the size of the [attester set](#attester-set) and `D` the peering degree of [P2P Network](../draft/p2p-network.md#gossiping) |
| `PULL_INTERVAL` | Pull Interval | The period between confirmation rounds. | 2 seconds |
| `PULL_SAMPLE_SIZE` | Pull Sample Size | Providers queried per round. | 16 |
| `PULL_MAX_ROUNDS` | Maximum Pull Rounds | Rounds a node spends on one transaction. | 8 |
| `PULL_SAMPLE` | Pull Sample | Distinct providers asked about one transaction. | `min(PULL_SAMPLE_SIZE * PULL_MAX_ROUNDS, N - 1)` |
| `PULL_MAX_BATCH` | Maximum Pull Batch | The most transactions one query may name. | 1024 |

`PULL_SAMPLE` is sized for an adversary holding at most one third of the attester set. At a larger share a transaction delivered to one node and a transaction the network holds return the same share of positive answers, and the rule below cannot tell them apart.

## Mempool State
```python
class Mempool:
    provider_id: ProviderId                      # this node's declared identity, if it has one
    pending: TimeOrderedSet[TxHash]              # admitted, not yet retired, in admission order
    bodies: Map[TxHash, SignedMantleTx]          # transaction bodies
    admitted_at: Map[TxHash, Timestamp]          # admission time, per pending transaction
    by_prefix: Map[bytes, Set[TxHash]]           # pending hashes, keyed by reference prefix
    commitment: Map[TxHash, Hash]                # this node's body commitment, at admission
    attesters: Map[TxHash, Set[ProviderId]]      # providers that attested to holding it
    queried: Map[TxHash, Set[ProviderId]]        # providers that answered a query about it
    received_from: Map[TxHash, Set[ProviderId]]  # providers the transaction arrived from
    rounds: Map[TxHash, uint8]                   # confirmation rounds spent
```

A transaction is keyed by `mantle_txhash(tx)`, defined in [Mantle](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash).

`by_prefix` maps `prefix(hash, REFERENCE_PREFIX_LENGTH)` to the pending hashes carrying that prefix, where `REFERENCE_PREFIX_LENGTH` is defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#references).

`insert_by` places a hash at the position its admission time gives it, which is not the end when a [Reorganisation](#reorganisation) re-admits a transaction.

A transaction is **confirmed** when `len(attesters[key]) > PULL_SAMPLE / 2`.

A node that holds no declaration in the [attester set](#attester-set) answers no query and stores no `commitment`.

A node adds the sender of a gossiped copy to `received_from`, including a copy `admit` reports as a duplicate. The sender is identified by the `provider_id` that [Locators](bedrock-service-declaration-protocol.md#locators) makes its node identity. A sender outside the attester set is not recorded.

A node holds two further tables outside `Mempool`. One records, for each query in flight, the provider it went to and the transactions it named, in the order it named them. The other records the providers sampled in each of the previous `PULL_MAX_ROUNDS - 1` rounds. A restart discards both.

## Transaction Admission
A transaction reaches the mempool by local submission through the [Node API](#node-api), by gossip on the mempool topic, or by re-insertion after a [Reorganisation](#reorganisation). All three follow this procedure.

```python
def admit(mempool, encoded: bytes, at: Timestamp = None) -> Result:
    if len(encoded) > MAX_BLOCK_SIZE:
        return Reject(TransactionTooLarge)

    tx = decode_signed_mantle_tx(encoded)
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
    mempool.commitment[key] = Hash("LOGOS_MEMPOOL_BODY_V1" || mempool.provider_id || encode(tx.tx))
    return Accept(key)
```

Admission reads the transaction and the mempool, and no other state. A node must not treat membership of the mempool as evidence that a transaction can be applied.

`MAX_BLOCK_SIZE` is defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants).

### Decoding
The payload is the canonical encoding defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md), carried in the envelope defined in [Network Wire Format](network-wire-format.md). Decoding must consume the payload exactly.

### Stateless Validation
`preverify` applies the subset of the [Mantle validation rules](bedrock-v1.1-mantle-specification.md#validation) that reads no ledger state:

1. The transaction carries one proof entry per operation, which may be the `None` entry where the opcode admits one.
2. Each proof entry has the type its operation's opcode requires.
3. Each proof bound only to the transaction hash and the operation payload verifies.

### Reorganisation

When a fork switch displaces blocks from the canonical chain, the node re-admits the transactions they carried that the blocks now in the canonical chain do not carry. It re-admits each with its original admission time.

### Duplicates
`admit` reports a duplicate. The caller decides what follows:

- A duplicate received by gossip is dropped.
- A duplicate received by local submission is answered as success, and the transaction is broadcast again.

## Dissemination

Transactions are gossiped on the mempool topic defined in [P2P Network](../draft/p2p-network.md#gossiping).

A message's identity on that topic is the Blake2b-256 digest of its payload. Implementations must not use gossipsub's default source-and-sequence-number identity.

A node relays a received message to its mesh neighbours on receipt, before admission.

A node broadcasts a transaction it admits by local submission or by re-insertion. It does not broadcast a transaction it received by gossip.

A node admits a transaction it originates at the moment it broadcasts it, and not before.

## Confirmation
A node confirms a transaction by asking sampled providers whether they hold it.

### Attester Set
The attester set is the Blend Network declarations active in the [Service Declaration Protocol](bedrock-service-declaration-protocol.md) snapshot of the current epoch, defined in [Snapshots](bedrock-service-declaration-protocol.md#snapshots). A declaration supplies the `provider_id` and `locators` a querier uses to reach the provider.

### The Pull Exchange
A query and its response are carried over `PULL_PROTOCOL`.

```python
class PullQuery:
    tx_hashes: list[TxHash]         # at most PULL_MAX_BATCH entries

class PullResponse:
    held: bitmap
    witness: Digest
```

`held` carries one bit per entry of `tx_hashes`, in query order, packed least significant bit first and padded with zero bits to a whole number of bytes. A transaction whose bit is set is **held**. `Hash` is the general-purpose hash function of [Common Cryptographic Components](common-cryptographic-components.md), taken with 256-bit output, and `Digest` is its result.

```python
witness = Hash("LOGOS_MEMPOOL_PULL_WITNESS_V1"
               || held
               || concat(commitment[tx] for tx in query.tx_hashes where held))
```

A querier accepts a response when both of the following hold:

1. The response answers an outstanding query on the stream that carried it. That stream is authenticated to the provider's `provider_id`, as [Locators](bedrock-service-declaration-protocol.md#locators) requires.
2. `witness` equals the value the querier recomputes from `held` and the commitments of that `provider_id` over the held transactions.

An accepted response attests to each of its held transactions.

A provider that does not hold a queried transaction leaves its bit clear. It must not request the transaction, and the querier must not send it.

A provider rate-limits queries per querier. It may decline to answer.

### Confirmation Rounds
Every `PULL_INTERVAL`, a node:

1. Collects every pending transaction that is unconfirmed, has been pending for at least `PULL_DELAY`, has spent fewer than `PULL_MAX_ROUNDS` rounds, and has fewer than `PULL_SAMPLE - floor(PULL_SAMPLE / 2)` providers in `queried` that are not in `attesters`. Where more than `PULL_MAX_BATCH` transactions qualify, it collects the `PULL_MAX_BATCH` oldest by admission time. A round that collects nothing sends no query.
2. Samples `PULL_SAMPLE_SIZE` providers from the [attester set](#attester-set), uniformly at random and without replacement, excluding itself and every provider it sampled in the previous `PULL_MAX_ROUNDS - 1` rounds. Where fewer remain, it samples all of them. The sample must be drawn from local randomness and never from a chain-derived seed.
3. Sends each sampled provider a query naming the collected transactions for which that provider is in neither `queried` nor `received_from`. It sends no query to a provider excluded by every transaction it collected.
4. Increments `rounds` for every transaction it collected.
5. On each response it accepts, adds the provider to the `queried` set of every transaction that query named, and to `attesters` for every transaction the response attests to.

A node must not re-evaluate an accepted attestation against a later snapshot.

## Block Building View
The mempool supplies the bodies of every pending transaction in admission order.

**Applicability.** The leader determines which transactions apply:

1. Apply the block header to the ledger state. This is the working state.
2. Pass over all pending transactions in admission order. Apply each transaction that succeeds to the working state.
3. Repeat step 2 until a pass applies no transaction.

No block limit applies to this computation.

**Selection.** The leader fills the block from the applicable transactions in the same order, stopping at the first transaction that would exceed `MAX_BLOCK_TXS` or `MAX_BLOCK_SIZE`, both defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants).

Confirmation is not a condition of block validity. A validator must not evaluate it when it validates a block.

## Reference Resolution
A block proposal carries a `REFERENCE_PREFIX_LENGTH`-byte prefix of each transaction hash, as defined in [References](bedrock-v1.1-block-construction.md#references). A validator resolves each reference against the mempool.

```python
def resolve(mempool, reference) -> Optional[SignedMantleTx]:
    matches = mempool.by_prefix.get(reference, empty_set)
    if len(matches) != 1:
        return None
    return mempool.bodies[single(matches)]
```

A non-unique match must not be searched.

Resolution reads the proposal, `by_prefix` and `bodies`, and nothing else.

How a validator uses the result, and what a failure to resolve establishes about the block, are specified in [Block Proposal Reconstruction](bedrock-v1.1-block-construction.md#block-proposal-reconstruction) and [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation).

## Retirement
A transaction leaves `pending` for one of three reasons.

### Inclusion in a Canonical Block
When a block enters the node's canonical chain, the transactions it carries are retired.

### Inapplicability
A transaction that the applicability determination of [Block Building View](#block-building-view) never applies is retired.

### Expiry
A pending transaction whose age exceeds `TRANSACTION_TTL` is retired.

### Effects of Retirement
Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at`, `attesters`, `queried`, `received_from` and `rounds` entries, its body and its `commitment`.

A retired transaction that is gossiped again is admitted again.

## Persistence and Recovery
A node persists the pending hashes, their admission timestamps, their `attesters`, `queried`, `received_from` and `rounds` entries, and the transaction bodies.

A node does not persist `by_prefix` or `commitment`. It rebuilds both from the recovered pending set and its own `provider_id`.

## Node API

A node exposes the mempool to local clients through endpoints that carry no consensus meaning.

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
