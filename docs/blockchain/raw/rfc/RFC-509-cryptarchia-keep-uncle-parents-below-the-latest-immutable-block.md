# [RFC] Cryptarchia: Keep uncle parents below the latest immutable block

**Motivation and proposal:** [PR #509](https://github.com/logos-co/logos-lips/pull/509)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-29 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the retention rule](#1-a-node-keeps-the-uncle-parents-below-the-latest-immutable-block) in the [Cryptarchia Protocol](#affected-specifications). Check that the kept range holds every uncle parent below `B_imm`, and that the rule keeps only what the uncle rules read.

# Discussion

## Alternatives

A simple model compares the rule with two alternatives and with no rule. The chain has one block per occupied slot, and each slot is occupied with probability `f`. A validator's `B_imm` is `k` blocks below its tip. A block `A` forks `d` blocks below the tip, at the slot of the chain's next block, so `d = 0` is a block on the tip. Each cell is the share of tips at which the window of `A` reaches a block below `B_imm` that the node does not keep, over 3·10⁶ slots with `k = 10` and `f = 1/30`. A block also needs a fork block there to reference, so a cell measures when the failure can occur.

| Kept below `B_imm` | `W` | On the tip | Fork 2 deep | Fork 5 deep |
| --- | --- | --- | --- | --- |
| Nothing | 6 | 1.83% | 8.09% | 39.5% |
| The last `W·f⁻¹` slots before the tip | 6 | 0 | 5.41% | 38.7% |
| Slot greater than `sl_B_imm − W·f⁻¹` (this RFC) | 6 | 0 | 0 | 0 |
| Nothing | 12 | 53.9% | 76.0% | 95.6% |
| The last `W·f⁻¹` slots before the tip | 12 | 0 | 41.0% | 90.4% |
| Slot greater than `sl_B_imm − W·f⁻¹` (this RFC) | 12 | 0 | 0 | 0 |

`W = 6` is the largest value `⌊0.6k⌋` allows at `k = 10`. For a block on the tip, the first row matches the exact binomial tail `P(Bin(180, 1/30) ≥ 12) = 1.82%`.

- **A bound `W·f⁻¹ < k`.** A chain holds at most one block per slot, so the window then holds fewer than `k` blocks, and a block on the tip never reaches below `B_imm`. A block forking `d` blocks deep still can once `d ≥ k + 2 − W·f⁻¹`. At `k = 2160` that is 1802 blocks for `W = 12`, and 32 blocks for `W = 71`, the largest value the bound allows. A node must follow any fork up to `k` blocks deep, so only a bound that admits no uncle at all closes the case. The bound also forces `W = 0` for every `k ≤ 30` at `f = 1/30`.
- **Keeping the last `W·f⁻¹` slots before the tip.** This covers blocks on the tip only. A fork block's window starts at its own slot, which is older than the tip's.
- **No rule.** An honest proposer never references a fork it has pruned. Each validator checks against its own `B_imm`, so the rows for keeping nothing apply to honest blocks.

## What the rule keeps

The rule keeps what the uncle rules read at a parent below `B_imm`: the block, for the ancestry check and its slot, `ledger_LATEST` as of it, and the epoch state of its epoch. An uncle can lie in the epoch after its parent's. The window spans at most `s/5` slots under `W ≤ ⌊0.6k⌋`, and an epoch spans `10⌊k/f⌋` slots, so the window crosses at most one epoch boundary. The uncle's epoch is then the epoch of the referencing block, whose state the node needs for that block anyway.

The range spans `W·f⁻¹` slots below `B_imm` and holds about `W` blocks: 12 at the specification's values, and at most 360.

## Parameters

- `W ≤ ⌊0.6k⌋` stays as it is. It no longer guards validity. It bounds what the rule keeps, and it keeps most uncle candidates inside a proposer's block tree.
- At the specification's values (`k = 2160`, `f = 1/30`, `W = 12`) the window is 360 slots. A block on the tip would need 2162 blocks inside it, so the failure cannot occur on the tip, and needs a fork at least 1802 blocks deep. The rule removes the dependence on these values.
- With `W = 0` no uncle is valid and the range is empty, so the rule keeps nothing.

## Open question: nodes started from a checkpoint

A node that starts from a checkpoint sets `B_imm` to the checkpoint block. A checkpoint carries only that block and its ledger state ([Bootstrapping from Checkpoint](../cryptarchia-v1-bootstr-sync.md#bootstrapping-from-checkpoint)). Such a node holds none of the blocks this rule keeps, so it cannot validate an uncle whose parent lies below the checkpoint block until a checkpoint carries them.

## Compatibility

The rule adds no validity condition and changes no encoding. It asks a node to keep more below `B_imm`. A node that keeps nothing there rejects blocks that the specification accepts, and the rule makes such nodes agree with the specification and with each other. Bedrock has no deployed network, so no migration is needed.

# Details

## 1. A node keeps the uncle parents below the latest immutable block

A new paragraph in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references), after the rules that define `valid_uncle(U, σ_U, A)`:

```diff
 - The carried signature verifies over the header of U ...  # last uncle rule, unchanged
+
+A node keeps each block deeper than B_imm whose slot is greater than
+sl_B_imm - W·f⁻¹, with ledger_LATEST as of that block and the epoch state of
+its epoch. A block A that a node validates descends from B_imm by step 8 of
+Block Header Validation, so sl_A > sl_B_imm. The window rule above then gives
+sl_parent(U) > sl_B_imm - W·f⁻¹ for each uncle U that A carries. A parent
+deeper than B_imm is therefore one of the blocks kept.
```

- Blocks at or above `B_imm` stay in the block tree `T`, as before.
- The Cryptarchia Protocol revision is 1.3.0.

# Implementation

- [ ] When the latest immutable block advances, keep the blocks below it whose slot is greater than `sl_LIB − W·f⁻¹`, with their ledger states. Today the engine removes every block below the LIB (`prune_immutable_blocks`, `consensus/cryptarchia-engine/src/lib.rs`), and the chain service drops their ledger states (`prune_ledger_states`, `services/chain/chain-service/src/lib.rs`).
- [ ] Let the ancestry walk in `verify_uncles_ancestry` (`services/chain/chain-service/src/uncle.rs`) continue below the LIB into the kept blocks.
- [ ] Add tests: an uncle whose parent is the proposer's LIB, validated by a node whose tip is one block ahead; and a fork block whose window reaches below the LIB.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.0 |
