# [RFC] Mempool: Transaction retention and maturity

**Motivation and proposal:** [PR #448](https://github.com/logos-co/logos-lips/pull/448)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-10 |
| v2 | Added `TRANSACTION_MATURITY`, the age `BLEND_DELAY + BROADCAST_DELAY` (15 s + 5 s) a transaction must reach before block building sees it, and restated the retention constraint in those terms. | 2026-09-11 |
| v3 | Renamed to cover maturity, and moved the RFC document to the matching path. | 2026-09-11 |

## Reviewer Orientation

Single-document change — read [Mempool](../mempool.md) top to bottom. Focus on the maturity gate in `Block Building View`, on the new `Release` stage, and on the constraints under `Constants`, which are what make a compliant selection reconstructable at every node.

# Discussion

## Why resolution must outlast selection

One constant bounded both stages. `Expiry` retires a transaction whose age exceeds `TRANSACTION_TTL`, and retirement discarded the body, so a transaction stopped resolving at the instant it stopped being selectable.

A block proposal is not instantaneous. It crosses the Blend network and then reaches every node by gossip, which `BLEND_DELAY + BROADCAST_DELAY` puts at 20 seconds. A leader that selects a transaction just under `TRANSACTION_TTL` therefore sends a proposal that arrives when the transaction is up to 20 seconds past that bound, and every validator has discarded it.

The block is valid. Nothing in Block Proposal Validation reads a transaction's age, and a validator that cannot reconstruct a proposal records no verdict against the block, so the same block still validates on its merits if it later arrives in full through chain synchronisation. What the leader loses is the slot, with no signal that anything went wrong.

## Why block building waits for maturity

The young end has the mirror problem. [Block Proposal Reconstruction](../bedrock-v1.1-block-construction.md#block-proposal-reconstruction) assumes transaction maturity: a proposal references only transactions that have had enough time to reach every node. The mempool offered a transaction to block building the moment it was admitted, so nothing made the assumption hold.

Maturity is a light form of confirmation. It carries no evidence that another node holds the transaction, only that enough time has passed for it to have spread: the time a proposal itself takes to cross the Blend network and reach every node. A leader that selects a mature transaction adds it to the proposal knowing that every node has had at least the proposal's own transit time to receive it, so reconstruction will most likely succeed at every validator. The cost is that no transaction is selectable for its first 20 seconds.

The gate sits before applicability rather than at selection. Selecting the mature subset of the applicable sequence could include a transaction that spends an output an immature one creates, and the block would be invalid. Retirement for inapplicability is narrowed to mature transactions for the same reason: an immature transaction is not passed over, so it has not failed to apply.

Maturity is a property of the leader's mempool, and Block Proposal Validation does not read it.

## The retained set does not depend on the node's branch

Resolution reads `by_prefix` and `bodies`. A transaction leaves `pending` for three reasons, and two of them — inclusion in a canonical block, and inapplicability — depend on which branch the node follows. While retirement also emptied `bodies`, two honest nodes could resolve the same reference differently: a node that had already included a transaction could not reconstruct a competing proposal referencing it, and had to wait for a fork switch to re-admit it.

Retention removes that dependence. A transaction resolves for `TRANSACTION_RETENTION` after its admission, whatever the node's own branch did with it in between, so resolution is a function of what the node observed.

## What retention costs

A node holds each body for twice as long. A chain carries at most one block per `f^{-1}` slots at `MAX_BLOCK_SIZE`, so the included transactions alone reach about 11 GiB over 48 hours, against 5.6 GiB over 24. The pool has no capacity bound, so transactions that no block carries are bounded only by what admission accepts, and retention doubles that exposure too.

A node that stores retained bodies as an index into the blocks it already holds pays the doubling only for the transactions no block carries.

## Why the retention is twice the time to live

The constraint requires only that retention exceed the time to live by more than `BLEND_DELAY + BROADCAST_DELAY` — 20 seconds against 24 hours. Every margin above that covers the spread between nodes' admission times, which no specification bounds: a node admits a transaction when it first receives it, and gossip reaches nodes at different moments.

Doubling is the smallest integer multiple of the time to live that clears the constraint without the specification having to quantify that spread. A tighter value becomes available if the spread is ever bounded.

## The bootstrap constraint holds with no margin

`TRANSACTION_TTL` is 24 hours and the Prolonged Bootstrap Period is 24 hours, so the first constraint holds exactly. A node that has just completed the period holds precisely the transactions a leader may select, and a change to either value in either direction breaks it. Neither constant was chosen with the other in mind.

This RFC states the constraint and leaves both values as they are. Raising the period, or lowering the time to live, would give it a margin.

# Details

## Release

A transaction now leaves the mempool in two stages. Retirement removes it from `pending`, which is the set [Block Building View](../mempool.md#block-building-view) offers a leader. Release discards it.

```diff
 ### Effects of Retirement

-Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at` entry and its body.
-
 A retired transaction that is gossiped again is admitted again.
+
+## Release
+
+A retained transaction whose age exceeds `TRANSACTION_RETENTION` is released.
+
+Release removes the hash from `by_prefix`, and discards its `admitted_at` entry and its body.
```

Both stages measure a transaction's age from its admission, so a transaction is selectable for `TRANSACTION_TTL` and resolvable for `TRANSACTION_RETENTION`.

## The constants and their constraints

```diff
 | `TRANSACTION_TTL` | Transaction Time To Live | How long a transaction may stay pending before it is retired. | 24 hours |
+| `TRANSACTION_RETENTION` | Transaction Retention | How long a transaction stays resolvable before it is released. | `2 * TRANSACTION_TTL` |
+| `BLEND_DELAY` | Blend Delay | How long a block proposal takes to cross the Blend network. | 15 seconds |
+| `BROADCAST_DELAY` | Broadcast Delay | How long a block proposal takes to reach every node once it leaves the Blend network. | 5 seconds |
+| `TRANSACTION_MATURITY` | Transaction Maturity | How long a transaction must have been pending to be mature. | `BLEND_DELAY + BROADCAST_DELAY` |
```

`BLEND_DELAY` and `BROADCAST_DELAY` are fixed rather than derived, so this document does not move when the Blend parameters do. 15 seconds is `3 · (3 + 2)` rounds at one second a round: three blends, each holding a message for at most three rounds, and two rounds of network delay a hop. The Transition Period derives 11 rounds from half a round of network delay, so the constraint on `BLEND_DELAY` holds with a margin. 5 seconds is a gossip broadcast at one second a hop: with a peering degree of 8 it covers up to 32 768 nodes, and a larger network needs a larger `BROADCAST_DELAY`.

Four constraints follow the table, each with what breaks when it is violated:

- `TRANSACTION_TTL` must not exceed the Prolonged Bootstrap Period. A node that has just completed that period cannot resolve a reference to a transaction admitted before the period began.
- `TRANSACTION_RETENTION` must exceed `TRANSACTION_TTL` by more than `BLEND_DELAY + BROADCAST_DELAY`. Otherwise a proposal that selects a transaction just under `TRANSACTION_TTL` arrives after that transaction was released.
- `BLEND_DELAY` must not be less than the time a message takes to cross the Blend network. Otherwise a mature transaction has had less time to spread than the proposal carrying it takes to arrive.
- `TRANSACTION_MATURITY` must be less than `TRANSACTION_TTL`. Otherwise a transaction is retired before it is mature, and nothing is ever selected.

## The maturity gate

Block building sees a transaction only once it is mature:

```diff
+A pending transaction is **mature** once its age reaches `TRANSACTION_MATURITY`.
+
-The mempool supplies the bodies of every pending transaction in admission order.
+The mempool supplies the bodies of every mature transaction in admission order.
```

Applicability passes over the mature transactions, and [Inapplicability](../mempool.md#inapplicability) retires a mature transaction only. Selection is unchanged.

## The retained state

`pending` holds the selectable transactions. The other three maps hold the retained transactions as well.

```diff
 class Mempool:
     pending: TimeOrderedSet[TxHash]     # admitted, not yet retired, in admission order
     bodies: Map[TxHash, SignedMantleTx] # transaction bodies
-    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
-    by_prefix: Map[bytes, Set[TxHash]]  # pending hashes, keyed by reference prefix
+    admitted_at: Map[TxHash, Timestamp] # admission time
+    by_prefix: Map[bytes, Set[TxHash]]  # hashes keyed by reference prefix
```

[Reference Resolution](../mempool.md#reference-resolution) is unchanged: it already read `by_prefix` and `bodies`, and those now carry the retained transactions.

## Admission preserves the admission time

A retained transaction that is gossiped again keeps the time it was first admitted. Without this, anyone could hold a transaction alive indefinitely by re-gossiping it after each release.

```diff
-    mempool.admitted_at[key] = at if at is not None else now()
+    mempool.admitted_at[key] = at if at is not None else mempool.admitted_at.get(key, now())
```

The `at` argument still carries the original admission time on the [Reorganisation](../mempool.md#reorganisation) path, where the transaction may already have been released.

## Subscription to the mempool topic

A node subscribes when it starts [Listening for New Blocks](../cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks), which is when the Prolonged Bootstrap Period begins. This is what the first constraint rests on: the transactions a node holds are the ones gossiped since it subscribed.

## Persistence and status

A restart must not release a transaction early, so the retained hashes, their admission times and their bodies are persisted alongside the pending ones, and `by_prefix` is rebuilt from all of them. The mempool status endpoint reports `retained` as a third state beside `pending` and unknown.

## Chores

- Narrowed the `admitted_at` and `by_prefix` comments, which said "per pending transaction" and "pending hashes".
- Added the Blend Protocol and Cryptarchia Bootstrapping & Synchronization to the References list, which the constraints now link to.

# Implementation

- [ ]  Supply block building with mature transactions only, and retire for inapplicability only a mature transaction
- [ ]  Keep a retired transaction's body, admission time and prefix index until it is released
- [ ]  Release a retained transaction once its age exceeds `TRANSACTION_RETENTION`
- [ ]  Preserve the admission time when a retained transaction is admitted again
- [ ]  Subscribe to the mempool topic when listening for new blocks starts
- [ ]  Persist the retained hashes, admission times and bodies, and rebuild `by_prefix` from every recovered hash
- [ ]  Report `retained` from the mempool status endpoint
- [ ]  Add or extend tests / test vectors: a transaction younger than `TRANSACTION_MATURITY` is neither selected nor retired for inapplicability, a proposal selecting a transaction just under `TRANSACTION_TTL` reconstructs after the Blend transit, a released transaction does not resolve, and re-gossiping a retained transaction does not extend its life
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | Block building waits for `TRANSACTION_MATURITY`; retirement no longer discards, and `Release` does; the document does not yet exist on master |
