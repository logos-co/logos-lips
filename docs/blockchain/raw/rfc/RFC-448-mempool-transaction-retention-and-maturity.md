# [RFC] Mempool: Transaction retention and maturity

**Motivation and proposal:** [PR #448](https://github.com/logos-co/logos-lips/pull/448)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-10 |
| v2 | Added `TRANSACTION_MATURITY`, the age `BLEND_DELAY + BROADCAST_DELAY` (15 s + 5 s) a transaction must reach before block building sees it, and restated the retention constraint in those terms. | 2026-09-11 |
| v3 | Renamed to cover maturity, and moved the RFC document to the matching path. | 2026-09-11 |
| v4 | Hardened retention against competing branches. An included transaction is released when its block becomes immutable rather than at `TRANSACTION_RETENTION`, a transaction a canonical block carries is retained even if this node never admitted it, and an included hash is a duplicate at admission. `admit` loses its `at` argument, which a fork switch no longer needs. | 2026-10-07 |
| v5 | Took over from [#413](https://github.com/logos-co/logos-lips/pull/413) the rule that a fork switch re-admits a transaction at its original admission time, with the time-ordered `pending` and the `insert_by` it needs. #413's retirement discards that time before a fork switch needs it, so the rule could not stay there. | 2026-10-07 |
|  | Added the rule's rationale and implementation task. The admission diffs now start from #413's `admit`, which no longer has an `at` argument. | 2026-10-07 |

## Reviewer Orientation

Single-document change — read [Mempool](../mempool.md) top to bottom. Focus on the maturity gate in `Block Building View`, on the new `Release` stage and its two triggers, on `included` in `Inclusion in a Canonical Block` and in `admit`, on the admission time and position `admit` keeps for a retained transaction, and on the constraints under `Constants`, which are what make a compliant selection reconstructable at every node.

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

Retention removes that dependence. Until it is released, a transaction resolves whatever the node's own branch did with it. An included transaction is released only when its block becomes immutable, and from then on every branch the node can still adopt carries that block, so no valid block can reference the transaction again. A node observes a transaction by admitting it or by holding a canonical block that carries it, so a node that caught up by downloading blocks resolves what those blocks carry.

## Why an included transaction is released at immutability

`TRANSACTION_RETENTION` is measured from admission, and a transaction can be included up to `TRANSACTION_TTL` after it. Under the time bound, an included transaction could therefore be released 24 hours after its inclusion. Its block becomes immutable once `k` blocks follow it. That takes `k/f` slots on average, 18 hours, but no time bounds it: `s = 3k/f` slots, 54 hours, only suffices with high probability. A slow chain, which is when forks run deep, could release a transaction while a branch that lacks its block can still be adopted. A proposal on that branch would not resolve, and a fork switch to it would re-admit the transaction without its admission time.

Immutability is the exact bound. Before it, a competing branch can carry the transaction, so the node keeps it. After it, no valid block can reference the transaction. It needs no new constant, and it holds however fast the chain runs.

The bound also covers the reorganisation. A fork switch displaces only blocks that are not immutable, so every transaction it re-admits is still retained, and `admit` keeps its admission time. A transaction this node never admitted has no time to keep, and is admitted at the current one.

An included hash is a duplicate at admission. Admitting it again would return it to `pending`. Block building would then retire it as inapplicable, and the time bound would release it, possibly before its block is immutable.

## Why a re-admitted transaction keeps its place

A transaction that a fork switch displaces goes back to the position its admission time gives it in `pending`, not to the end. Otherwise a displaced block's worth of transactions is queued behind everything admitted since. That penalises exactly the transactions the reorganisation already disadvantaged, and selection carries no fee signal that could buy the position back.

The order also matters beyond fairness. The implementation's TTL eviction scans the front of the sequence and stops at the first transaction that has not expired. An old timestamp appended at the back would never be reached, and nothing behind it would be examined either. `insert_by` keeps `pending` sorted by admission time, which the scan relies on. Gossip that re-admits a retained transaction puts an old timestamp back as well.

The rule was [#413](https://github.com/logos-co/logos-lips/pull/413)'s until [review](https://github.com/logos-co/logos-lips/pull/413#discussion_r4078757027) found that #413 discards the admission time at retirement, before a fork switch needs it. The rule needs the time to outlive retirement, so it moved here.

## What retention costs

At most `k` canonical blocks are not yet immutable, so the included transactions hold at most `k · MAX_BLOCK_SIZE`, about 4.2 GiB. The time bound would have held 48 hours of blocks at one block per `f^{-1}` slots, about 11 GiB. A node that stores included bodies as an index into the blocks it already holds pays nothing extra for them.

The pool has no capacity bound, so transactions that no block carries are bounded only by what admission accepts. Holding them for `TRANSACTION_RETENTION` rather than `TRANSACTION_TTL` doubles that exposure.

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
-### Effects of Retirement
-
-Retirement removes the hash from `pending` and from `by_prefix`, and discards its `admitted_at` entry and its body.
-
-A retired transaction that is gossiped again is admitted again.
+## Release
+
+When a block becomes immutable, as defined in [Latest Immutable Block](cryptarchia-v1-protocol.md#latest-immutable-block), the transactions it carries are released.
+
+A retained transaction that is not in `included` is released when its age exceeds `TRANSACTION_RETENTION`.
+
+Release removes the hash from `included` and from `by_prefix`, and discards its `admitted_at` entry and its body.
```

Retirement and the time bound both measure a transaction's age from its admission. A transaction is therefore selectable for `TRANSACTION_TTL`, and resolvable for `TRANSACTION_RETENTION` unless a canonical block carries it. An included transaction is released when its block becomes immutable. `Effects of Retirement` goes, because `admit` already states which retired transactions are admitted again.

## The constants and their constraints

```diff
 | `TRANSACTION_TTL` | Transaction Time To Live | How long a transaction may stay pending before it is retired. | 24 hours |
+| `TRANSACTION_RETENTION` | Transaction Retention | How long a transaction that no canonical block carries stays resolvable before it is released. | `2 * TRANSACTION_TTL` |
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

`pending` holds the selectable transactions. It is now ordered by admission time rather than by insertion, which [Admission preserves the admission time](#admission-preserves-the-admission-time) needs. `included` holds the retained transactions that a canonical block carries, which the release and duplicate rules treat apart. `bodies`, `admitted_at` and `by_prefix` hold the retained transactions as well.

```diff
 class Mempool:
-    pending: OrderedSet[TxHash]         # admitted, not yet retired, in admission order
+    pending: TimeOrderedSet[TxHash]     # admitted, not yet retired, in admission order
+    included: Set[TxHash]               # retained, carried by a canonical block not yet immutable
     bodies: Map[TxHash, SignedMantleTx] # transaction bodies
-    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
-    by_prefix: Map[bytes, Set[TxHash]]  # pending hashes, keyed by reference prefix
+    admitted_at: Map[TxHash, Timestamp] # admission time
+    by_prefix: Map[bytes, Set[TxHash]]  # hashes keyed by reference prefix
```

[Reference Resolution](../mempool.md#reference-resolution) is unchanged: it already read `by_prefix` and `bodies`, and those now carry the retained transactions.

## Inclusion and reorganisation

A block that enters the canonical chain adds its transactions to `included`, including a transaction the mempool never held:

```diff
-When a block enters the node's canonical chain, the transactions it carries are retired.
+When a block enters the node's canonical chain, the transactions it carries are retired and added to `included`. For a transaction the mempool does not hold, the body is taken from the block and the hash is added to `by_prefix`.
```

A fork switch takes the displaced transactions out of `included` before it re-admits them, so `admit` does not report them as duplicates:

```diff
-When a fork switch displaces blocks from the canonical chain, the node re-admits the transactions they carried that the blocks now in the canonical chain do not carry.
+When a fork switch displaces blocks from the canonical chain, the transactions they carried that the blocks now in the canonical chain do not carry leave `included`. The node re-admits each.
```

## Admission preserves the admission time

A retained transaction that is admitted again keeps the time it was first admitted, and goes back to the position that time gives it in `pending`. Keeping the time stops anyone from holding a transaction alive indefinitely by re-gossiping it before each release. [Why a re-admitted transaction keeps its place](#why-a-re-admitted-transaction-keeps-its-place) gives the reason for the position. An included transaction is not admitted again at all, because its hash is a duplicate.

```diff
     key = mantle_txhash(tx)
-    if key in mempool.pending:
+    if key in mempool.pending or key in mempool.included:
         return Duplicate(key)
 
     mempool.bodies[key] = tx
-    mempool.admitted_at[key] = now()
-    mempool.pending.add(key)
+    mempool.admitted_at[key] = mempool.admitted_at.get(key, now())
+    mempool.pending.insert_by(key, mempool.admitted_at[key])
```

```diff
+`insert_by` places a hash at the position its admission time gives it.
```

A fork switch re-admits only transactions that are still retained, so the same lines keep their time and position on the [Reorganisation](../mempool.md#reorganisation) path. A displaced transaction this node never admitted has no entry, and is admitted at the current time.

## Subscription to the mempool topic

A node subscribes when it starts [Listening for New Blocks](../cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks), which is when the Prolonged Bootstrap Period begins. This is what the first constraint rests on: the transactions a node holds are the ones gossiped since it subscribed.

## Persistence and status

A restart must not release a transaction early, so the retained hashes, `included`, their admission times and their bodies are persisted alongside the pending ones, and `by_prefix` is rebuilt from all of them. The mempool status endpoint reports `retained` as a third state beside `pending` and unknown.

## Chores

- Narrowed the `admitted_at` and `by_prefix` comments, which said "per pending transaction" and "pending hashes".
- Added the Blend Protocol and Cryptarchia Bootstrapping & Synchronization to the References list, which the constraints now link to.
- Corrected the Introduction, which said the mempool holds transactions not yet in the canonical chain. It holds them until their block is immutable.
- Transaction Admission now says the three entry points admit a transaction, not that they are how one reaches the mempool, since a canonical block also adds the transactions it carries.

# Implementation

- [ ]  Supply block building with mature transactions only, and retire for inapplicability only a mature transaction
- [ ]  Keep a retired transaction's body, admission time and prefix index until it is released
- [ ]  Add the transactions of every block that enters the canonical chain to `included`, taking the body from the block when the mempool does not hold it
- [ ]  Release the transactions a block carries when the block becomes immutable, and any other retained transaction once its age exceeds `TRANSACTION_RETENTION`
- [ ]  Report a hash in `included` as a duplicate at admission
- [ ]  Preserve the admission time when a retained transaction is admitted again, on the reorganisation path too, and use the current time for a displaced transaction this node never admitted
- [ ]  Insert a re-admitted transaction at the position its admission time gives it, which the current `IndexMap` cannot express, and keep TTL eviction correct across that insertion
- [ ]  Subscribe to the mempool topic when listening for new blocks starts
- [ ]  Persist the retained hashes, `included`, admission times and bodies, and rebuild `by_prefix` from every recovered hash
- [ ]  Report `retained` from the mempool status endpoint
- [ ]  Add or extend tests / test vectors: a transaction younger than `TRANSACTION_MATURITY` is neither selected nor retired for inapplicability, a proposal selecting a transaction just under `TRANSACTION_TTL` reconstructs after the Blend transit, a released transaction does not resolve, re-gossiping a retained transaction does not extend its life, a competing proposal referencing a transaction this node already included reconstructs, an included transaction is released when its block becomes immutable and not before, and a fork switch re-admits a displaced transaction at its original admission time and position
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | Block building waits for `TRANSACTION_MATURITY`; retirement no longer discards, and `Release` does, at immutability for an included transaction; a re-admitted transaction keeps its admission time and position; the document does not yet exist on master |
