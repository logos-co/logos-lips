# [RFC] Cryptarchia: Reduce Uncle References to its rules

**Motivation and proposal:** [PR #472](https://github.com/logos-co/logos-lips/pull/472)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |
| v2 | Added "if and only if", the slot bound as a bullet of its own, the removal of the sentence citing step 5, and references in place of the rule list in step 10 and the Total Stake Inference | 2026-10-06 |

## Reviewer Orientation

Single-document change with no rule change. First check the wording of the uncle rules: the definition reads "if and only if", and the slot bound is a bullet of its own. Then read [Chores](#chores) against the diff of the [Cryptarchia Protocol](#affected-specifications). For each removed statement, check that it is analysis, kept in [Discussion](#what-the-removed-analysis-said), or that the place its Chores entry names still states it.

# Discussion

## What the removed analysis said

Two removed passages were analysis rather than restatement:

- The uncle reference window is anchored to the uncle's parent because the uncle's proof is verified against `ledger_LATEST` as of its parent. Anchoring there bounds how far back a validator must keep the chain. Anchoring to the uncle's own slot would not bound it, because a leader may build on a stale tip.
- The owner of a winning note can sign a header for that win later and have it carried as an uncle. The proof still attests a real lottery win in that slot, and the Total Stake Inference counts each occupied slot once, so such a header adds no slot that was not won.

## The bound on `W`

The bound itself is unchanged. The removed Note stated it as `W ≤ ⌊0.6k⌋`, equivalently `W·f⁻¹ ≤ s/5`. The Constants row keeps the second form, which counts slots, as the window does.

# Details

This RFC changes no rule. Every edit is listed in [Chores](#chores).

## Chores

All in [Cryptarchia Protocol](../cryptarchia-v1-protocol.md).

- The definition of a valid uncle reads "if and only if", so the listed rules are the complete definition. Revision 1.2.5 reads "only if".
- The slot bound `sl_parent(U) < sl_U < sl_A` becomes a bullet of its own, separate from the window rule.
- The sentence that attributed `sl_U > sl_parent(U)` to step 5 of Block Header Validation is removed. Step 5 checks only the block being validated, and the slot bound states it.
- Uncle References no longer carries the purpose of uncle references, the argument that requiring valid uncles is safe, the rationale for anchoring the window to the parent, the caveat on late-signed headers, or the two Notes.
- The rule bullets keep only their rules. The consequences and justifications that followed each rule are removed.
- The Proof of Leadership rule lists its public inputs without claiming that all of them derive from the chain of the referencing block, since the slot and keys come from the uncle's header.
- Uncle References no longer restates what other sections and documents state: the list encoding ([Canonical Encoding](../bedrock-v1.1-block-construction.md#canonical-encoding)), padding for Blend ([Payload Formatting](../payload-formatting.md)), the commitment to the carried headers (step 4 of Block Header Validation), and that an uncle is not executed, has no fork-choice weight, and serves only the Total Stake Inference ([Block Execution](../bedrock-v1.1-block-construction.md#block-execution), [Fork Choice](../fork-choice.md)).
- The opening of Uncle References no longer calls an uncle "a valid fork block", which no validator can check. It says how a block carries an uncle.
- Duplicate entries are permitted, stated once in Uncle References.
- Step 10 refers to the rules of Uncle References instead of listing them. It no longer repeats the duplicate permission, the `MAX_UNCLES` bound, which the [Canonical Encoding](../bedrock-v1.1-block-construction.md#canonical-encoding) enforces at decode time, or that a block with a failing entry is rejected. It no longer argues that all nodes agree on uncle validity.
- The Total Stake Inference no longer lists the uncle rules, nor notes that a carried entry was validated with its referencing block, which step 10 states.
- `uncle_candidates` in Uncle Selection calls `valid_uncle` instead of repeating four of its rules. Blocks in the block tree already satisfy the rules this adds, so the selection is unchanged. The text around the two functions keeps one rule: validators do not check a block's selection.
- The bound on `W` moved from a Note into the `W` row of Constants, with what breaks when it is exceeded. The row no longer restates the window rule.
- The Total Stake Inference, Block ID and step 4 of Block Header Validation no longer restate consequences of the rules.
- The Cryptarchia Protocol revision is 1.2.6.

# Implementation

- [ ] No implementation required (specification-only change): no rule changes.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.2.6 |
