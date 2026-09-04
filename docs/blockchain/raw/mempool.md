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

# Mempool State

```python
class Mempool:
    pending: TimeOrderedSet[TxHash]     # admitted, not yet retired, in admission order
    bodies: Map[TxHash, SignedMantleTx] # transaction bodies
    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
    by_prefix: Map[bytes, Set[TxHash]]  # pending hashes, keyed by reference prefix
```

A transaction is keyed by `mantle_txhash(tx)`, defined in [Mantle](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash).

`by_prefix` maps `prefix(hash, REFERENCE_PREFIX_LENGTH)` to the pending hashes carrying that prefix, where `REFERENCE_PREFIX_LENGTH` is defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#references).

`pending` holds each hash once, ordered by admission time. `insert_by` places a hash at the position its admission time gives it, which is not the end when a [Reorganisation](#reorganisation) re-admits a transaction.

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

# Block Building View

The mempool supplies the bodies of every pending transaction in admission order.

A leader makes two determinations over that view.

**Applicability.** The leader determines which transactions apply:

1. Apply the block header to the ledger state. This is the working state.
2. Pass over all pending transactions in admission order. Apply each transaction that succeeds to the working state.
3. Repeat step 2 until a pass applies no transaction.

No block limit applies to this computation. A transaction that never applies is retired, as specified in [Inapplicability](#inapplicability).

**Selection.** The leader fills the block from the applicable transactions in the same order, stopping at the first transaction that would exceed `MAX_BLOCK_TXS` or `MAX_BLOCK_SIZE`, both defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants). A transaction left unselected is not retired.

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

Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at` entry and its body.

A retired transaction that is gossiped again is admitted again.

# Persistence and Recovery

A node persists the pending hashes, their admission timestamps, and the transaction bodies.

A node does not persist `by_prefix`. It rebuilds the index from the recovered pending set.

# Node API

A node exposes the mempool to local clients. These endpoints are operational and carry no consensus meaning.

| Operation | Description |
| --- | --- |
| Submit transaction | Admit a transaction by local submission and broadcast it. Returns the outcome of [Transaction Admission](#transaction-admission). |
| View | The hashes of the pending transactions. |
| Status | For each queried hash, whether the transaction is pending or unknown to this node. |
| Metrics | The number of pending transactions and the time of the most recent admission. |

# References

- [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)
- [Cryptarchia Protocol](cryptarchia-v1-protocol.md)
- [Mantle](bedrock-v1.1-mantle-specification.md)
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
- [Network Wire Format](network-wire-format.md)
- [P2P Network](../draft/p2p-network.md)
