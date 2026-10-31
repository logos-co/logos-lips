# [RFC] Cryptarchia: Require an uncle to follow its parent

**Motivation and proposal:** [PR #471](https://github.com/logos-co/logos-lips/pull/471)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |
| v2 | Narrowed to the new rule: removed the editorial cleanup of Uncle References with its Chores and its Discussion entry, and the implementation task on duplicate entries | 2026-10-06 |
| v3 | Narrowed to the lower bound alone, added where the uncle rules are listed: removed the split of the rule bullet, "if and only if", the removal of the sentence citing step 5, and the references that replaced the rule lists in step 10 and the Total Stake Inference | 2026-10-06 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the new bound](#1-an-uncle-must-follow-its-parent) in the [Cryptarchia Protocol](#affected-specifications). Check that `sl_parent(U) < sl_U` is strict, and that it appears in all three places that list the uncle rules.

# Discussion

## Why the rule is stated, not left to the proof

The reference implementation already rejects these uncles. It verifies an uncle's proof by advancing the ledger state of the uncle's parent to the uncle's slot, and that step fails for any slot that is not after the parent's slot. This is how one implementation derives the epoch state, not a rule. The specification derives the epoch state of the uncle's slot on the chain of the referencing block, which works for any earlier slot. So the bound is stated as a rule, next to the other slot bounds.

## The uncle's slot now lies inside the window

With the new bound, `sl_A − W·f⁻¹ ≤ sl_parent(U) < sl_U < sl_A`. The uncle's own slot is therefore less than `W·f⁻¹` slots before the referencing block. Cryptarchia 1.2.4 claimed this already, but without the bound an uncle's slot could lie anywhere before its parent's slot.

## Compatibility

The change narrows validity. A block that carries an uncle with `sl_U ≤ sl_parent(U)` could be valid under the 1.2.4 text, and is invalid now. The reference implementation already rejects such a block, so its behavior does not change. Bedrock has no deployed network, so the change needs no migration.

# Details

## 1. An uncle must follow its parent

The uncle rules gain a lower bound on the uncle's slot. It goes into the definition of `valid_uncle(U, σ_U, A)` in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references):

```diff
-- The uncle precedes the referencing block, and the parent of the uncle lies
-  within the uncle reference window: sl_A > sl_U and
-  sl_A - sl_parent(U) <= W·f⁻¹.
+- The uncle follows its parent and precedes the referencing block, and the
+  parent of the uncle lies within the uncle reference window:
+  sl_parent(U) < sl_U < sl_A and sl_A - sl_parent(U) <= W·f⁻¹.
   The window is anchored to the parent ...  # rest of the bullet unchanged
```

- The bound is strict. An uncle in its parent's slot is invalid, as step 5 of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation) requires of every block.
- Step 10 of Block Header Validation and the [Total Stake Inference](../cryptarchia-v1-protocol.md#total-stake-inference) list the uncle rules again. Both lists gain the same bound: the uncle follows its parent and precedes the referencing block.
- The Cryptarchia Protocol revision is 1.2.5.

# Implementation

- [ ] Reject an uncle whose slot is not after its parent's slot with an explicit check and its own `UncleError` variant in `verify_uncles` (`services/chain/chain-service/src/uncle.rs`). Today the ledger's `update_epoch_state` rejects it as a side effect, and the error surfaces as `UncleError::InvalidProof`.
- [ ] Add tests for an uncle in its parent's slot and an uncle before its parent's slot.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.2.5 |
