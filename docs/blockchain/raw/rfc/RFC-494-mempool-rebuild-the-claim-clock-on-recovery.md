# [RFC] Mempool: Rebuild the claim clock on recovery

**Motivation and proposal:** [PR #494](https://github.com/logos-co/logos-lips/pull/494)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-20 |

## Reviewer Orientation

Single-document change — read [Expired Claim](../mempool.md#expired-claim) and [Persistence and Recovery](../mempool.md#persistence-and-recovery) in the [Mempool](../mempool.md), and focus on `highest_slot`, which `recover` now takes from the block tree.

# Discussion

## What a restart does to the claim rule

The mempool retires a claim, and admission refuses it, once `highest_slot` is more than `CLAIM_GRACE` slots past the end of the claim's acceptance window. Until this change, the specification described what `logos-blockchain` does at `8eb8a05e5`. The clock advances only when the chain reports a processed block, and it has no value until the first one after the node starts. The claim policy keeps no persistent state, and it learns about a claim only when the pool admits it. Two things follow:

- Until the node processes a block after it starts, admission refuses no expired claim. The node holds a claim that no block can include, and broadcasts it if a local client submitted it.
- A claim that was pending before the restart is never retired as a claim. Once its deadline passes, only `TRANSACTION_TTL` or a failed [applicability determination](../mempool.md#block-building-view) retires it. A node that disables expiry and never leads keeps it.

## Why the block tree is the clock

[Setting the Fork Choice Rule](../cryptarchia-v1-bootstr-sync.md#setting-the-fork-choice-rule) covers a node that restarts while preserving its block tree. `recover` reads `highest_slot` from that tree, so the clock has the value it had before the restart. The clock still never passes the current slot, because [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation) accepted no block in the tree before its slot had begun. A node that was offline for a long time rebuilds a clock that lags the current slot. It retires a claim later than it otherwise would, and never earlier.

Persisting `highest_slot` instead would keep a second copy of a value the block tree already holds. The copy can disagree with the tree, and it needs a write on every block the node adds to stay current.

`recover` reads the slot of every block in the tree. Slots increase along every branch, so the highest slot is the slot of one of the branch tips, and an implementation can read the tips alone.

The change is local to each node. It changes no message, encoding or consensus rule.

# Details

## The claim clock survives a restart

`highest_slot` is the highest slot in the node's block tree, rather than the highest slot of a block added since the node started, and it is never unset. [Persistence and Recovery](../mempool.md#persistence-and-recovery) rebuilds it from the block tree:

```diff
-def recover(saved) -> Mempool:
+def recover(saved, block_tree) -> Mempool:
     by_prefix = defaultdict(set)
     for key in list(saved.pending) + list(saved.retired):
         by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
     return Mempool(pending=saved.pending, retired=saved.retired, bodies=saved.bodies,
                    admitted_at=saved.admitted_at, by_prefix=by_prefix,
-                   highest_slot=None)
+                   highest_slot=max(block.header.slot for block in block_tree))
```

`block_tree` holds the blocks of the node's block tree. [Mempool State](../mempool.md#mempool-state) types the field to match:

```diff
-    highest_slot: Optional[SlotNumber]  # highest slot of a block added since the node started
+    highest_slot: SlotNumber            # highest slot in the block tree
```

[Admission Pipeline](../mempool.md#admission-pipeline) and [Node State](../mempool.md#node-state) describe `highest_slot` in the same terms, and the Admission Pipeline no longer says that no deadline passes before the node adds a block.

## A recovered claim expires at its deadline

[Expired Claim](../mempool.md#expired-claim) drops the unset clock and the exemption for a claim pending since recovery:

```diff
 def claim_expired(mempool, tx) -> bool:
     slots = [block_slot(claim.block_hash) for claim in claims(tx)]
     known = [slot for slot in slots if slot is not None]
-    if not known or mempool.highest_slot is None:
+    if not known:
         return False
```

```diff
-A pending transaction for which `claim_expired` holds is retired, unless it has been pending since the node recovered it from persisted state.
+A pending transaction for which `claim_expired` holds is retired.
```

# Implementation

- [ ]  Seed the policy clock with the highest slot in the block tree when the mempool starts, instead of leaving it unset until the first processed block
- [ ]  Track each transaction recovered from persisted state in the claim policy, as on admission, so a recovered claim is retired at its deadline
- [ ]  Add or extend tests: after a restart, admission refuses an expired claim before the node processes a block, and a recovered claim is retired once the clock reaches its deadline
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | The claim clock is the highest slot in the block tree, rebuilt on recovery, and a recovered claim expires like any other. |
