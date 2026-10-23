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
| v6 | Recovery rebuilds `included`, with the bodies of its transactions, from the stored blocks instead of the saved state. A fork switch re-admits a displaced transaction only if it was admitted within `TRANSACTION_TTL`. Added why a restart must not undo a retirement, with the implementation tasks and tests. | 2026-10-20 |
|  | Merged the mempool specification's expired-claim rule. An expired claim is released as soon as it expires, whether pending or retained, and the diffs that quote the mempool specification follow its current text. | 2026-10-13 |
|  | Removed `BLEND_DELAY`, which restated Blend's message traversal time $`T_M`$. `TRANSACTION_MATURITY` is now $`T_M`$ rounds plus `BROADCAST_DELAY`, and the retention and `CLAIM_GRACE` constraints read it. Dropped the statement that Blend derives 11 rounds, which no longer holds. | 2026-10-13 |
|  | Merged the restructured mempool specification, and extended its Overview and Protocol to maturity, retention and release. The constants diff follows the Parameters block, and maturity must be shorter than the claim window. | 2026-10-13 |
|  | Released an included transaction once its block is `k` blocks deep rather than immutable, which bounds `included` while a node bootstraps, and measured a displaced transaction's age from its block's slot when no admission time is held. | 2026-10-20 |
|  | Merged the mempool specification's reference code, which the Details diffs now quote. | 2026-10-20 |
|  | A transaction that a fork switch re-admits is no longer broadcast. | 2026-10-23 |
|  | Replaced `TRANSACTION_RETENTION` with the specification's `RETIREMENT_GRACE`, now counted from `TRANSACTION_TTL` rather than from retirement, and took the specification's one-hour `TRANSACTION_TTL`. | 2026-10-23 |

## Reviewer Orientation

Single-document change — read [Mempool](../mempool.md) top to bottom. Focus on the maturity gate in `Block Building View`, on `Release`, which replaces pruning, and its two triggers, on `RETIREMENT_GRACE`, which `release_due` counts from `TRANSACTION_TTL`, on `included` in `Inclusion in a Canonical Block` and in `admit`, on the admission time and position `admit` keeps for a retained transaction, on which displaced transactions `Reorganisation` re-admits, on `Dissemination`, which does not broadcast them, on how `Persistence and Recovery` rebuilds `included`, on the release of an expired claim, and on the constraints under `Parameters`, which are what make a compliant selection reconstructable at every node.

# Discussion

## The retained set does not depend on the node's branch

Resolution reads `by_prefix` and `bodies`. A transaction leaves `pending` for four reasons, and two of them, inclusion in a canonical block and inapplicability, depend on which branch the node follows. The specification kept a retired transaction for `RETIREMENT_GRACE`, ten minutes, after its retirement, so two honest nodes could resolve the same reference differently. A node that had included a transaction more than ten minutes earlier could not reconstruct a competing proposal that referenced it, and had to wait for a fork switch to re-admit it. A node that had found a transaction inapplicable on its own branch lost it ten minutes later, while a leader on another branch could still select it.

Retention removes that dependence. Until it is released, a transaction resolves whatever the node's own branch did with it. An included transaction is released only when its block is `k` blocks deep, and from then on every fork that the Online fork choice rule accepts carries that block, so no block on such a fork can reference the transaction again. Any other retained transaction is released at an age that no branch decides, as [Why the grace counts from the time to live](#why-the-grace-counts-from-the-time-to-live) describes. A node observes a transaction by admitting it or by holding a canonical block that carries it, so a node that caught up by downloading blocks resolves what the last `k` of those blocks carry.

## Why an included transaction is released at depth `k`

Under the grace alone, an included transaction could stop resolving ten minutes after its block entered the canonical chain, about 20 blocks later. The Online fork choice rule can adopt a branch that lacks its block until `k` blocks follow that block. That takes `k/f` slots on average, 18 hours, and no time bounds it: `s = 3k/f` slots, 54 hours, only suffices with high probability. A proposal on such a branch would not resolve, and a fork switch to it would re-admit the transaction without its admission time.

Depth `k` is the exact bound under the Online fork choice rule, which makes a block immutable at that depth. Before it, a competing branch can carry the transaction, so the node keeps it. After it, no fork that rule accepts can reference the transaction. It needs no new constant, and it holds however fast the chain runs.

Immutability itself would not bound `included` while a node bootstraps. Under the [Bootstrap Fork Choice Rule](../fork-choice.md#bootstrap-fork-choice-rule), the [Latest Immutable Block](../cryptarchia-v1-protocol.md#latest-immutable-block) does not advance through Initial Block Download and the 24-hour Prolonged Bootstrap Period. That rule applies to a node that starts from genesis or from a checkpoint, and to one that restarts after more than 20 minutes offline. Released at immutability, `included` would hold every block such a node downloads. [What retention costs](#what-retention-costs) gives the size.

Releasing at depth `k` while bootstrapping costs only delay. Nothing reads what the node keeps from Initial Block Download until that download ends: downloaded blocks carry their own transactions, the node subscribes to the mempool topic only when it starts listening for new blocks, and it proposes only under the Online rule. After that, a proposal can reference a transaction from a block more than `k` deep only on a fork that leaves this node's chain more than `k` blocks back. That is an attacker's chain, or the honest chain when this node's own chain is the isolated one. A proposal that does not resolve records no verdict, and its block arrives in full when the node downloads the missing blocks of a later orphan.

Under the Online rule the bound also covers the reorganisation. A fork switch displaces only blocks fewer than `k` deep, so every transaction it re-admits is still retained, and `admit` keeps its admission time. Under the Bootstrap rule a fork switch can displace deeper blocks, whose transactions were released together with their admission times. A transaction this node holds no admission time for, because it learned the transaction only from a block or has released it, is admitted at the current time.

A displaced transaction older than `TRANSACTION_TTL` is not re-admitted. This node would not select it. It stays retained until its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`. For a transaction without an admission time, the node measures the age from the start of the displaced block's slot, since a transaction is at least as old as the block that carries it. Without that, a deep fork switch while bootstrapping would re-admit every displaced transaction the new chain lacks, however old. A retained copy that is not re-admitted keeps the slot start as its time, which the time bound then measures. With the one-hour `TRANSACTION_TTL`, a fork switch returns to block building only the displaced transactions admitted in the last hour, about 120 blocks. The sender of an older one must submit a different transaction. Submitted again, the same one is dropped by every node that relayed it in the last `SEEN_TTL`, a day by default, since such a node remembers its identity.

An included hash is a duplicate at admission. Admitting it again would return it to `pending`. Block building would then retire it as inapplicable, and the time bound would release it, possibly before its block is `k` blocks deep.

## Why the grace counts from the time to live

The specification counted `RETIREMENT_GRACE` from retirement, which comes at different moments for different reasons: at inclusion, when the node leads and finds a transaction inapplicable, and for age at the first block after the transaction expires. A transaction retired early was released early, although a leader that holds it can select it until its own copy expires. `release_due` therefore counts the grace from the age `TRANSACTION_TTL`. A retained transaction that no canonical block carries is released once its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`, whatever retired it. Nothing reads the retirement time any more, so the state drops it.

Counting from the admission time also stops re-admission from extending the grace. Admission keeps the time of a retained transaction, so one admitted again by gossip or by local submission is released at the same age as before. Counted from retirement, each re-admission followed by expiry at the next block would have started the grace again.

`RETIREMENT_GRACE` keeps its ten minutes and its bound. The bound in [Parameters](../mempool.md#parameters) takes the worst case of a validator that retires its copy for its age at the moment it expires, and so releases it when its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`. That is now when `release_due` releases every copy that no canonical block carries. The bound reads `TRANSACTION_MATURITY` for the time a block proposal takes to reach every node, which is the time maturity is set to.

## Why block building waits for maturity

The young end has the mirror problem. [Block Proposal Reconstruction](../bedrock-v1.1-block-construction.md#block-proposal-reconstruction) assumes transaction maturity: a proposal references only transactions that have had enough time to reach every node. The mempool offered a transaction to block building the moment it was admitted, so nothing made the assumption hold.

Maturity is a light form of confirmation. It carries no evidence that another node holds the transaction, only that enough time has passed for it to have spread: the time a proposal itself takes to cross the Blend network and reach every node. A leader that selects a mature transaction adds it to the proposal knowing that every node has had at least the proposal's own transit time to receive it, so reconstruction will most likely succeed at every validator. The cost is that no transaction is selectable for its first 20 seconds.

The gate sits before applicability rather than at selection. Selecting the mature subset of the applicable sequence could include a transaction that spends an output an immature one creates, and the block would be invalid. Retirement for inapplicability is narrowed to mature transactions for the same reason: an immature transaction is not passed over, so it has not failed to apply.

Maturity is a property of the leader's mempool, and Block Proposal Validation does not read it.

## Why an expired claim is released at once

No block can include a claim once its acceptance window has closed, and `CLAIM_GRACE` keeps the claim until any proposal that selected it in time has reached every node. Nothing reads it after that, so a retained claim is released as soon as `claim_expired` holds, and a pending one once [Expired Claim](../mempool.md#expired-claim) has retired it. Otherwise a claim that no canonical block carries would be kept until its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`, and an included one until its block is `k` blocks deep. An included claim goes too: a fork switch could not re-admit it, because admission refuses an expired claim.

`release_due` leaves a pending claim to Expired Claim, which does not retire a claim that has been pending since the node recovered it from persisted state. Such a claim is retired for its age, and released at once after that.

## Why a re-admitted transaction keeps its place

A transaction that a fork switch displaces goes back to the position its admission time gives it in `pending`, not to the end. Otherwise a displaced block's worth of transactions is queued behind everything admitted since. That penalises exactly the transactions the reorganisation already disadvantaged, and selection carries no fee signal that could buy the position back.

The order also matters beyond fairness. The implementation's TTL eviction scans the front of the sequence and stops at the first transaction that has not expired. An old timestamp appended at the back would never be reached, and nothing behind it would be examined either. `insert_by` keeps `pending` sorted by admission time, which the scan relies on. Gossip that re-admits a retained transaction puts an old timestamp back as well.

The rule was [#413](https://github.com/logos-co/logos-lips/pull/413)'s until [review](https://github.com/logos-co/logos-lips/pull/413#discussion_r4078757027) found that #413 discards the admission time at retirement, before a fork switch needs it. The rule needs the time to outlive retirement, so it moved here.

## Why a re-admitted transaction is not broadcast

A fork switch displaces the same blocks on every node that makes it, and each of those nodes re-admits the displaced transactions itself. A node that followed the adopted branch, and received a transaction by gossip, still holds it. The nodes that lack it are those that joined, or were cut off, when it was gossiped.

A broadcast would not reach them either. A node remembers the identity of each message it receives or publishes on the mempool topic for `SEEN_TTL`, and a broadcast of a message it remembers sends nothing. A re-admitted transaction is at most `TRANSACTION_TTL` old, one hour, and `SEEN_TTL` is a day by default, so every node that received it by gossip still remembers its identity. A broadcast would go out only from a node that learned the transaction from a block, or that has restarted since. Most of its peers would drop it as a duplicate.

`SEEN_TTL` is a node setting, so the cost of a broadcast would also rest on it. A node that sets it below `TRANSACTION_TTL` would broadcast every re-admitted transaction older than that, to peers that mostly hold it already.

## A restart must not undo a retirement

The implementation saves the mempool's recovery state only after it admits a transaction. A restart restores that state, and the chain service replays its stored blocks without notifying the mempool. Every retirement since the last admission is therefore undone.

Inclusion is the retirement that retention cannot lose. A transaction missing from `included` is released by the time bound rather than at depth `k`, which [Why an included transaction is released at depth `k`](#why-an-included-transaction-is-released-at-depth-k) shows can be too early. One that this node took from a block does not resolve at all.

Recovery therefore rebuilds `included` from the chain rather than from the saved state. Every canonical block after the latest immutable block is stored, so applying inclusion to each of those fewer than `k` blocks deep recovers `included` exactly, whatever the last save held. It also retires the recovered pending transactions those blocks carry, and it needs no write per applied block.

The other retirements since the last save come back pending. Expiry retires such a transaction again when the node next processes a block, since every admission time is saved when it is set, and inapplicability when the node next builds a block. The same holds for a transaction whose block reached depth `k` since the last save, which the rebuild does not reach. A release by the time bound since the last save happens again the next time `release_due` runs.

## What retention costs

`included` covers at most `k` canonical blocks, so its transactions hold at most `k · MAX_BLOCK_SIZE`, about 4.2 GiB, under either fork choice rule. Released at immutability, they would have held every block a bootstrapping node downloads: about 5.6 GiB of full blocks for each day of chain history, at one block per `f^{-1}` slots, and as much again for the Prolonged Bootstrap Period. Released `RETIREMENT_GRACE` after inclusion, they held about 20 blocks, 40 MiB. Each of them is also in a block the node stores, so a node that keeps included bodies as an index into its stored blocks pays nothing extra for the bodies. Under immutability that index would still grow with the chain.

The pool has no capacity bound, so transactions that no block carries are bounded only by what admission accepts. A node now holds each of them until its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`, seventy minutes. A transaction retired for its age was held about as long before, and one retired as inapplicable for `RETIREMENT_GRACE` after the node led.

# Details

## Release

Retirement now only removes a transaction from `pending`, which is the set [Block Building View](../mempool.md#block-building-view) offers a leader:

```diff
-A node retires a transaction by running `retire`. It runs `prune` before it admits a transaction, retires one, or processes a block. It retires the transactions that [Expiry](#expiry) and [Expired Claim](#expired-claim) select when it processes a block, and after it retires transactions for [Inclusion in a Canonical Block](#inclusion-in-a-canonical-block) or [Inapplicability](#inapplicability).
+A node retires a transaction by removing it from `pending`. It retires the transactions that [Expiry](#expiry) and [Expired Claim](#expired-claim) select when it processes a block, and after it retires transactions for [Inclusion in a Canonical Block](#inclusion-in-a-canonical-block) or [Inapplicability](#inapplicability).
```

Release, a new section after [Retirement](../mempool.md#retirement), discards a transaction. Its functions replace `retire` and `prune`:

```diff
-def retire(mempool, key: TxHash) -> None:
-    mempool.pending.remove(key)
-    del mempool.admitted_at[key]
-    mempool.retired[key] = now()
-
-def prune(mempool) -> None:
-    for key, retired_at in list(mempool.retired.items()):
-        if now() - retired_at >= RETIREMENT_GRACE:
-            del mempool.retired[key]
-            mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].discard(key)
-            del mempool.bodies[key]
+def release(mempool, key: TxHash) -> None:
+    mempool.included.discard(key)
+    mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].discard(key)
+    mempool.admitted_at.pop(key, None)
+    del mempool.bodies[key]
+
+def release_block(mempool, block: Block) -> None:
+    for tx in block.transactions:
+        if mantle_txhash(tx) in mempool.included:
+            release(mempool, mantle_txhash(tx))
+
+def release_due(mempool) -> None:
+    for key in list(mempool.bodies):
+        if key in mempool.pending:
+            continue
+        if claim_expired(mempool, mempool.bodies[key]) or (
+                key not in mempool.included
+                and now() - mempool.admitted_at[key] >= TRANSACTION_TTL + RETIREMENT_GRACE):
+            release(mempool, key)
```

```diff
+A node runs `release_block` on each block of its canonical chain once the block is $`k`$ blocks deep, after it has run `include` on that block. It runs `release_due` before it admits a transaction, retires one, or processes a block.
```

Retirement and release both measure a transaction's age from its `admitted_at` entry. A transaction is therefore selectable until its age reaches `TRANSACTION_TTL`, and resolvable for `RETIREMENT_GRACE` more unless a canonical block carries it. An included transaction is released when its block is `k` blocks deep, and a retained claim as soon as it expires. `release_due` runs when `prune` ran. `release_block` follows `include` on the same block because a fork switch can adopt blocks that are already `k` deep, and releasing one of them first would leave its transactions in `included` for good.

The constraints on `CLAIM_GRACE` and `RETIREMENT_GRACE` now guard the release, and read the time a proposal takes to reach every node from `TRANSACTION_MATURITY`:

```diff
-`CLAIM_GRACE` must exceed the time, in slots, that a block proposal takes to reach every node. Otherwise a node can retire a claim before a proposal that selected it in the last slot of its acceptance window arrives.
+`CLAIM_GRACE` slots must last longer than `TRANSACTION_MATURITY`. Otherwise a node can release a claim before a proposal that selected it in the last slot of its acceptance window arrives.
```

```diff
-`RETIREMENT_GRACE` must exceed the time a transaction takes to reach every node by gossip, plus the time between two consecutive blocks, plus the time a block proposal takes to reach every node. Otherwise a node can discard a transaction that it retired for its age before a proposal that selected it arrives.
+`RETIREMENT_GRACE` must exceed the time a transaction takes to reach every node by gossip, plus the time between two consecutive blocks, plus `TRANSACTION_MATURITY`. Otherwise a node can release an expired transaction before a proposal that selected it arrives.
```

## The constants and their constraints

Parameters gains `BROADCAST_DELAY` and `TRANSACTION_MATURITY`, and `RETIREMENT_GRACE` counts from `TRANSACTION_TTL`. The comment of `CLAIM_GRACE` is reworded, and the others move only to stay aligned:

```diff
-TRANSACTION_TTL: uint64 = 60 * 60            # seconds a transaction may stay pending before it is retired
-RETIREMENT_GRACE: uint64 = 10 * 60           # seconds a retired transaction stays resolvable before it is discarded
-CLAIM_GRACE: uint64 = 2 * WINDOW             # slots a claim stays pending after its acceptance window closes
-SEEN_TTL: uint64 = 24 * 60 * 60              # seconds a node remembers a message identity on the mempool topic
-BROADCAST_RETRIES: uint64 = 3                # retries of a broadcast that finds no peer on the mempool topic
-BROADCAST_BACKOFF: uint64 = 5                # base, in seconds, of the wait before each retry
+TRANSACTION_TTL: uint64 = 60 * 60                     # seconds a transaction may stay pending before it is retired
+RETIREMENT_GRACE: uint64 = 10 * 60                    # seconds a transaction that no canonical block carries stays resolvable after its age reaches TRANSACTION_TTL
+BROADCAST_DELAY: uint64 = 5                           # seconds a block proposal takes to reach every node once it leaves the Blend network
+TRANSACTION_MATURITY: uint64 = T_M + BROADCAST_DELAY  # seconds of age at which a transaction is mature
+CLAIM_GRACE: uint64 = 2 * WINDOW                      # slots a node keeps a claim after its acceptance window closes
+SEEN_TTL: uint64 = 24 * 60 * 60                       # seconds a node remembers a message identity on the mempool topic
+BROADCAST_RETRIES: uint64 = 3                         # retries of a broadcast that finds no peer on the mempool topic
+BROADCAST_BACKOFF: uint64 = 5                         # base, in seconds, of the wait before each retry
```

```diff
-With `WINDOW` at 300 slots, `CLAIM_GRACE` is 600 slots.
+With `WINDOW` at 300 slots, `CLAIM_GRACE` is 600 slots. With $`T_M`$ at 15 rounds of one second and `BROADCAST_DELAY` at 5 seconds, `TRANSACTION_MATURITY` is 20 seconds.
```

Notation gains the Blend value that maturity reads, the Cryptarchia value that release reads, and the slot clock that a fork switch reads:

```diff
 | `REFERENCE_PREFIX_LENGTH` | reference prefix length | The length of a reference in bytes, from [References](bedrock-v1.1-block-construction.md#references). |
+| $`k`$ | security parameter | From [Constants](cryptarchia-v1-protocol.md#constants). |
+| `SLOT_LENGTH` | slot length | The length of a slot in seconds, from [Constants](cryptarchia-v1-protocol.md#constants). |
+| `genesis_time` | genesis time | The time at which slot 0 starts, from [Cryptarchia Parameters](bedrock-genesis-block.md#cryptarchia-parameters). |
+| $`T_M`$ | message traversal time | The message traversal time of [Transition Period](blend-protocol.md#transition-period), converted from rounds to seconds by the length of a round given in [Time](blend-protocol.md#time). |
```

Maturity reads Blend's message traversal time $`T_M`$, 15 rounds of one second, instead of fixing a value of its own, so it follows the Blend parameters. 5 seconds is a gossip broadcast at one second a hop: with a peering degree of 8 it covers up to 32 768 nodes, and a larger network needs a larger `BROADCAST_DELAY`.

This RFC adds four constraints after the Parameters block, each with what breaks when it is violated:

- `TRANSACTION_TTL` must not exceed the Prolonged Bootstrap Period. A node that has just completed that period cannot resolve a reference to a transaction admitted before the period began. With a one-hour time to live and a 24-hour period, it holds with 23 hours to spare.
- `BROADCAST_DELAY` must not be less than the time a block proposal takes to reach every node by gossip. Otherwise a mature transaction has had less time to spread than the proposal carrying it takes to arrive.
- `TRANSACTION_MATURITY` must be less than `TRANSACTION_TTL`. Otherwise a transaction is retired before it is mature, and nothing is ever selected.
- `TRANSACTION_MATURITY` must be shorter than `WINDOW` slots. Otherwise a claim never matures while a block may still include it, and no claim is ever selected.

## The maturity gate

Block building sees a transaction only once it is mature:

```diff
+A pending transaction is mature once its age reaches `TRANSACTION_MATURITY`.
+
-The mempool supplies the bodies of every pending transaction in admission order.
+The mempool supplies the bodies of every mature transaction in admission order.
```

Applicability passes over the mature transactions only:

```diff
     state = apply_header(parent_state, header)       # the working state
-    applied, remaining = [], list(mempool.pending)   # remaining in admission order
+    applied = []
+    remaining = [key for key in mempool.pending       # the mature ones, in admission order
+                 if now() - mempool.admitted_at[key] >= TRANSACTION_MATURITY]
```

Only a mature transaction can then be found inapplicable, so [Inapplicability](../mempool.md#inapplicability) retires a mature transaction only. Selection is unchanged.

## The retained state

`pending` holds the selectable transactions. It is now ordered by admission time rather than by insertion, which [Admission preserves the admission time](#admission-preserves-the-admission-time) needs. `included` holds the retained transactions that a canonical block fewer than `k` blocks deep carries, which the release and duplicate rules treat apart. `bodies`, `admitted_at` and `by_prefix` hold the retained transactions as well. `retired` goes, since release reads the admission time instead of the retirement time.

```diff
 class Mempool:
-    pending: OrderedSet[TxHash]         # admitted, not yet retired, in admission order
-    retired: Map[TxHash, Timestamp]     # retirement time, per retired transaction still held
+    pending: TimeOrderedSet[TxHash]     # admitted, not yet retired, in admission order
+    included: Set[TxHash]               # retained, carried by a canonical block after the latest immutable block and fewer than k blocks deep
     bodies: Map[TxHash, SignedMantleTx] # transaction bodies
-    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
-    by_prefix: Map[bytes, Set[TxHash]]  # pending and retired hashes, keyed by reference prefix
+    admitted_at: Map[TxHash, Timestamp] # admission time
+    by_prefix: Map[bytes, Set[TxHash]]  # pending and retained hashes, keyed by reference prefix
     highest_slot: Optional[SlotNumber]  # highest slot of a block added since the node started
```

A `Timestamp` now counts from the Unix epoch, the clock of `genesis_time`, so that a fork switch can compare `now()` with the start of a slot:

```diff
-A `Timestamp` is a time in seconds, as an unsigned 64-bit integer, and `now()` is the node's current time as a `Timestamp`.
+A `Timestamp` is a time in seconds since the Unix epoch, as an unsigned 64-bit integer, and `now()` is the node's current time as a `Timestamp`.
```

[Reference Resolution](../mempool.md#reference-resolution) is unchanged: it already read `by_prefix` and `bodies`, and those now carry every retained transaction, including one learned only from a block.

## Inclusion and reorganisation

A block that enters the canonical chain adds its transactions to `included`, including a transaction the mempool never held, whose body it takes from the block:

```diff
-When a block enters the node's canonical chain, each pending transaction it carries is retired.
+def include(mempool, block: Block) -> None:
+    for tx in block.transactions:
+        key = mantle_txhash(tx)
+        if key in mempool.pending:
+            mempool.pending.remove(key)
+        elif key not in mempool.bodies:
+            mempool.bodies[key] = tx
+            mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
+        mempool.included.add(key)
```

```diff
+A node runs `include` on each block that enters its canonical chain.
```

A fork switch takes the displaced transactions out of `included` before it re-admits them, so `admit` does not report them as duplicates. It re-admits only those whose age is within `TRANSACTION_TTL`, and measures the age from the start of the displaced block's slot when the node holds no admission time:

```diff
     for block in displaced:
         for tx in block.transactions:
-            if mantle_txhash(tx) not in carried:
-                admit(mempool, encode_signed_mantle_tx(tx))
+            key = mantle_txhash(tx)
+            if key in carried:
+                continue
+            mempool.included.discard(key)
+            # A transaction is at least as old as the start of the slot of a block that carries it.
+            admitted = mempool.admitted_at.get(key, genesis_time + block.header.slot * SLOT_LENGTH)
+            if now() - admitted > TRANSACTION_TTL:
+                if key in mempool.bodies:
+                    # A retained copy keeps the time its release is measured from.
+                    mempool.admitted_at[key] = admitted
+                continue
+            admit(mempool, encode_signed_mantle_tx(tx))
```

A transaction that a fork switch re-admits is not broadcast, and a duplicate it meets is dropped:

```diff
-A node broadcasts a transaction it admits by local submission or by re-insertion. It does not broadcast a transaction it received by gossip.
+A node broadcasts a transaction it admits by local submission. It does not broadcast a transaction it received by gossip or by re-insertion.
```

```diff
-- A duplicate received by gossip is dropped.
+- A duplicate received by gossip or by re-insertion is dropped.
 - A duplicate received by local submission is answered as success, and the transaction is broadcast again.
-- A duplicate received by re-insertion is broadcast again.
```

```diff
-A transaction that is already pending is a duplicate. It is dropped if it came by gossip, and broadcast again otherwise, and a local client is answered as success.
+A transaction that fails the fourth check is a duplicate. It is broadcast again if it came by local submission, and dropped otherwise, and a local client is answered as success.
```

## Admission preserves the admission time

A retained transaction that is admitted again keeps the time it was first admitted, and goes back to the position that time gives it in `pending`. Keeping the time stops anyone from holding a transaction alive indefinitely by re-gossiping it before each release. [Why a re-admitted transaction keeps its place](#why-a-re-admitted-transaction-keeps-its-place) gives the reason for the position. An included transaction is not admitted again at all, because its hash is a duplicate. `admit` no longer clears a retirement time, since the state keeps none.

```diff
     key = mantle_txhash(tx)
-    if key in mempool.pending:
+    if key in mempool.pending or key in mempool.included:
         return Duplicate(key)
 
     if claim_expired(mempool, tx):
         return Reject(ExpiredClaim)
 
-    mempool.retired.pop(key, None)
     mempool.bodies[key] = tx
-    mempool.admitted_at[key] = now()
-    mempool.pending.add(key)
+    mempool.admitted_at[key] = mempool.admitted_at.get(key, now())
+    mempool.pending.insert_by(key, mempool.admitted_at[key])
```

```diff
+`insert_by` places a hash at the position its admission time gives it.
```

On the [Reorganisation](../mempool.md#reorganisation) path the same lines keep the time and position of a displaced transaction that is still retained. One this node holds no admission time for, because it learned the transaction only from a block or has released it, is admitted at the current time.

## Subscription to the mempool topic

A node subscribes when it starts [Listening for New Blocks](../cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks), which is when the Prolonged Bootstrap Period begins. This is what the first constraint rests on: the transactions a node holds are the ones gossiped since it subscribed.

```diff
 Transactions are gossiped on the mempool topic defined in [Gossiping](../draft/p2p-network.md#gossiping).
+
+A node subscribes to the topic when it starts [Listening for New Blocks](cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks).
```

## Persistence and status

A restart must not release a transaction early. The other retained transactions and every admission time are persisted alongside the pending ones, and `included` is rebuilt from the chain:

```diff
-A node persists the pending hashes with their admission timestamps, the retired hashes with their retirement times, and the bodies of both.
+A node persists the pending hashes, the retained hashes that are not in `included`, the bodies of those transactions, and every admission timestamp.
 
-A node does not persist `by_prefix` or `highest_slot`. It rebuilds `by_prefix` on recovery, and `highest_slot` starts at `None`:
+A node does not persist `included`, `by_prefix` or `highest_slot`. It rebuilds `included` and `by_prefix` on recovery, and `highest_slot` starts at `None`:
```

```diff
-def recover(saved) -> Mempool:
-    by_prefix = defaultdict(set)
-    for key in list(saved.pending) + list(saved.retired):
-        by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
-    return Mempool(pending=saved.pending, retired=saved.retired, bodies=saved.bodies,
-                   admitted_at=saved.admitted_at, by_prefix=by_prefix,
-                   highest_slot=None)
+def recover(saved, recent: list[Block]) -> Mempool:
+    mempool = Mempool(pending=TimeOrderedSet(), included=set(), bodies=dict(saved.bodies),
+                      admitted_at=dict(saved.admitted_at), by_prefix=defaultdict(set),
+                      highest_slot=None)
+    for key in saved.pending:
+        mempool.pending.insert_by(key, saved.admitted_at[key])
+    for key in mempool.bodies:
+        mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
+    for block in recent:
+        include(mempool, block)
+    return mempool
```

```diff
-`saved` holds what the node persisted.
+`saved` holds what the node persisted. `recent` holds the blocks of its canonical chain after the [Latest Immutable Block](cryptarchia-v1-protocol.md#latest-immutable-block) and fewer than $`k`$ blocks deep, in chain order. `include` is defined in [Inclusion in a Canonical Block](#inclusion-in-a-canonical-block).
```

The status endpoint reports a retained transaction as retained rather than unknown, and the transaction endpoint serves the body of every retained transaction:

```diff
-| Status | For each queried hash, whether the transaction is pending. Any other hash is reported as unknown. |
+| Status | For each queried hash, whether the transaction is pending or retained. Any other hash is reported as unknown. |
```

```diff
-| Transaction | The body of a pending or retired transaction that the node holds, by its hash. |
+| Transaction | The body of a pending or retained transaction that the node holds, by its hash. |
```

## Chores

- The `admitted_at` comment no longer says "per pending transaction", and the `by_prefix` comment and description say retained rather than retired hashes, since a transaction learned only from a block is retained without ever being retired.
- Reworded the `CLAIM_GRACE` comment, which said a claim stays pending. A claim that a block carries is retained instead.
- Corrected the Introduction, which said the mempool holds transactions not yet in the canonical chain. It holds them until they are final.
- Transaction Admission now says the three entry points admit a transaction, not that they are how one reaches the mempool, since a canonical block also adds the transactions it carries.
- Extended the Overview and Protocol to maturity, retention and release. The worked example matures the claim before node B leads and keeps it until its deadline, and a state diagram shows a transaction moving between the pending and retained sets.

# Implementation

- [ ]  Supply block building with mature transactions only, and retire for inapplicability only a mature transaction
- [ ]  Keep a retired transaction's body, admission time and prefix index until it is released
- [ ]  Add the transactions of every block that enters the canonical chain to `included`, taking the body from the block when the mempool does not hold it
- [ ]  Release the transactions a block carries once the block is `k` blocks deep in the canonical chain, after inclusion has run on it, including while the node bootstraps and its latest immutable block stays put
- [ ]  Release any other retained transaction once its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`, in place of pruning it `RETIREMENT_GRACE` after its retirement, and drop the retirement time
- [ ]  Release a retained claim as soon as it expires
- [ ]  Report a hash in `included` as a duplicate at admission
- [ ]  Preserve the admission time when a retained transaction is admitted again, on the reorganisation path too, and use the current time for a displaced transaction this node holds no admission time for
- [ ]  Re-admit a displaced transaction on a fork switch only if its age is within `TRANSACTION_TTL`, measured from the start of the displaced block's slot when the node holds no admission time, and keep that time for a retained copy that is not re-admitted
- [ ]  Do not broadcast a transaction that a fork switch re-admits
- [ ]  Keep admission times in seconds since the Unix epoch, the clock of `genesis_time`
- [ ]  Insert a re-admitted transaction at the position its admission time gives it, which the current `IndexMap` cannot express, and keep TTL eviction correct across that insertion
- [ ]  Subscribe to the mempool topic when listening for new blocks starts
- [ ]  Persist the pending and the other retained hashes, their bodies and every admission time, and rebuild `by_prefix` from every recovered hash
- [ ]  On recovery, apply inclusion to each canonical block after the latest immutable block that is fewer than `k` blocks deep, taking the bodies from the stored blocks
- [ ]  Report `retained` from the mempool status endpoint, and serve the body of any retained transaction from the transaction endpoint
- [ ]  Add or extend tests / test vectors: a transaction younger than `TRANSACTION_MATURITY` is neither selected nor retired for inapplicability, a proposal selecting a transaction just under `TRANSACTION_TTL` reconstructs after the Blend transit, a released transaction does not resolve, an inapplicable transaction resolves until its age reaches `TRANSACTION_TTL` plus `RETIREMENT_GRACE`, re-gossiping a retained transaction does not extend its life, a competing proposal referencing a transaction this node already included reconstructs, an included transaction is released when its block is `k` blocks deep and not before, also while the node bootstraps, a retained claim is released at its deadline and a pending one once it is retired, a fork switch re-admits a displaced transaction at its original admission time and position, a fork switch does not re-admit a displaced transaction admitted more than `TRANSACTION_TTL` ago, nor one learned only from a block whose slot started more than `TRANSACTION_TTL` ago, and a restart rebuilds `included` from the stored blocks and retires the recovered pending transactions they carry
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | Block building waits for `TRANSACTION_MATURITY`; release replaces pruning, at depth `k` for an included transaction and at `RETIREMENT_GRACE` past `TRANSACTION_TTL` for any other; a re-admitted transaction keeps its admission time and position and is not broadcast, and a fork switch re-admits only one within `TRANSACTION_TTL`, measured from its block's slot when no admission time is held; recovery rebuilds `included` from the chain; a retained claim is released as soon as it expires; the document does not yet exist on master |
