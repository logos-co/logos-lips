# MEMPOOL

| Field | Value |
| --- | --- |
| Name | Mempool |
| Slug | 251 |
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
| 1.0.0 | Initial revision. | 2026-10-13 |

# Introduction

The mempool is a node's store of Mantle Transactions that have been submitted but are not yet in the canonical chain.

# Overview

Each node keeps its own mempool. Nodes admit and retire independently, so their pending sets differ.

A transaction is admitted, disseminated, offered to block building, and retired.

# Details

## Notation

| Symbol | Name | Description |
| --- | --- | --- |
| `WINDOW` | acceptance window | The window of [Acceptance Window](proof-of-work.md#acceptance-window), in slots. |
| `MAX_BLOCK_SIZE` | maximum block size | From [Constants](cryptarchia-v1-protocol.md#constants). |
| `MAX_BLOCK_TXS` | maximum block transactions | From [Constants](cryptarchia-v1-protocol.md#constants). |
| `REFERENCE_PREFIX_LENGTH` | reference prefix length | The length of a reference in bytes, from [References](bedrock-v1.1-block-construction.md#references). |

## Parameters

```python
TRANSACTION_TTL: uint64 = 24 * 60 * 60  # seconds a transaction may stay pending before it is retired
CLAIM_GRACE: uint64 = 2 * WINDOW        # slots a claim stays pending after its acceptance window closes
```

`CLAIM_GRACE` must exceed the time, in slots, that a block proposal takes to reach every node. Otherwise a node can retire a claim before a proposal that selected it in the last slot of its acceptance window arrives.

## Mempool State

```python
class Mempool:
    pending: OrderedSet[TxHash]         # admitted, not yet retired, in admission order
    bodies: Map[TxHash, SignedMantleTx] # transaction bodies
    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
    by_prefix: Map[bytes, Set[TxHash]]  # pending hashes, keyed by reference prefix
    highest_slot: SlotNumber            # highest slot in the block tree
```

A transaction is keyed by `mantle_txhash(tx)`, defined in [Mantle](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash).

`by_prefix` maps `prefix(hash, REFERENCE_PREFIX_LENGTH)` to the pending hashes carrying that prefix.

`highest_slot` is the highest slot of any block that [Chain Maintenance](cryptarchia-v1-protocol.md#chain-maintenance) has added to the node's block tree.

## Transaction Admission

A transaction reaches the mempool by local submission through the [Node API](#node-api), by gossip on the mempool topic, or by re-insertion after a [Reorganisation](#reorganisation). All three follow this procedure.

```python
def admit(mempool, encoded: bytes) -> Result:
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

    if claim_expired(mempool, tx):
        return Reject(ExpiredClaim)

    mempool.bodies[key] = tx
    mempool.admitted_at[key] = now()
    mempool.pending.add(key)
    mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
    return Accept(key)
```

Admission reads the transaction, the mempool and the node's block tree, and no other state. A node must not treat membership of the mempool as evidence that a transaction can be applied.

`claim_expired` is defined in [Expired Claim](#expired-claim).

### Decoding

The payload is the canonical encoding defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md), carried in the envelope defined in [Network Wire Format](network-wire-format.md). Decoding must consume the payload exactly.

### Stateless Validation

`preverify` applies the subset of the [Mantle validation rules](bedrock-v1.1-mantle-specification.md#validation) that reads no ledger state:

1. The transaction carries one proof entry per operation, which may be the `None` entry where the opcode admits one.
2. Each proof entry has the type its operation's opcode requires.
3. Each proof bound only to the transaction hash and the operation payload verifies.

### Reorganisation

When a fork switch displaces blocks from the canonical chain, the node re-admits the transactions they carried that the blocks now in the canonical chain do not carry.

### Duplicates

`admit` reports a duplicate. The caller decides what follows:

- A duplicate received by gossip is dropped.
- A duplicate received by local submission is answered as success, and the transaction is broadcast again.

## Dissemination

Transactions are gossiped on the mempool topic defined in [P2P Network](../draft/p2p-network.md#gossiping).

A message's identity on that topic is the Blake2b-256 digest of its payload. Implementations must not use gossipsub's default source-and-sequence-number identity.

A node relays a received message to its mesh neighbours on receipt, before admission.

A node broadcasts a transaction it admits by local submission or by re-insertion. It does not broadcast a transaction it received by gossip.

## Block Building View

The mempool supplies the bodies of every pending transaction in admission order.

The leader's **applicability determination** finds the transactions that apply:

1. Apply the block header to the ledger state. This is the working state.
2. Pass over all pending transactions in admission order. Apply each transaction that succeeds to the working state.
3. Repeat step 2 until a pass applies no transaction.

No block limit applies to this computation.

In **selection**, the leader fills the block from the applicable transactions in the same order, stopping at the first transaction that would exceed `MAX_BLOCK_TXS` or `MAX_BLOCK_SIZE`.

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

A transaction leaves `pending` for one of four reasons.

### Inclusion in a Canonical Block

When a block enters the node's canonical chain, the transactions it carries are retired.

### Inapplicability

A transaction that the applicability determination of [Block Building View](#block-building-view) never applies is retired.

### Expiry

A pending transaction whose age exceeds `TRANSACTION_TTL` is retired.

### Expired Claim

A claim is the payload of a `CLAIM_POW_REWARD` Operation, defined in [CLAIM_POW_REWARD](bedrock-v1.1-mantle-specification.md#claim_pow_reward).

```python
def claim_expired(mempool, tx) -> bool:
    slots = [block_slot(claim.block_hash) for claim in claims(tx)]
    known = [slot for slot in slots if slot is not None]
    if not known:
        return False
    # One claim the ledger rejects invalidates the whole transaction, so the
    # earliest referenced block decides. A block at slot s + WINDOW is the last
    # that can include a claim referencing a block at slot s.
    return mempool.highest_slot >= min(known) + WINDOW + 1 + CLAIM_GRACE
```

A pending transaction for which `claim_expired` holds is retired.

`claims(tx)` is the list of claims in `tx`. `block_slot(h)` is the slot of the block with hash `h` in the node's block tree, or `None` if the block tree holds no such block.

### Effects of Retirement

Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at` entry and its body.

## Persistence and Recovery

A node persists the pending hashes, their admission timestamps, and the transaction bodies.

A node does not persist `by_prefix` or `highest_slot`. It rebuilds `by_prefix` from the recovered pending set and `highest_slot` from its block tree.

## Node API

A node exposes the mempool to local clients through endpoints that carry no consensus meaning.

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
- [Proof of Work](proof-of-work.md)
