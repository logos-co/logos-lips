# [RFC] Eras: Specify the form of an era migration

**Motivation and proposal:** [PR #476](https://github.com/logos-co/logos-lips/pull/476)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |

## Reviewer Orientation

Single-document change: read [Bedrock Eras](../bedrock-eras.md) §Era Migration, and focus on the three parts an era states and the five properties a migration preserves.

# Discussion

## The required parts

`migrate` is pseudocode, the form every other state transition in the specifications takes. The frame names the components an era redefines, so a reviewer checks only those against the identity rule that already governs the rest. Test vectors carry both the encoding and the digest of each state: the encoding lets an implementation run its own `migrate` on the same input, and the digest lets it compare outputs without carrying the whole state. The identity migration needs none of the three, so an era that changes only rules or parameters adds nothing.

## The preserved properties

Three properties hold of every state the current rules can reach:

- one note per leaf position, which the note tree requires;
- a note behind every channel note and every declaration's service note: a channel note stays in the ledger until it is consumed, and a service note is locked while a declaration names it;
- one declaration per service note and service, which step 5 of `SDP_DECLARE` enforces.

The other two relate the state before a migration to the state after it:

- the token sum: block execution changes it through fees and rewards, but `migrate` itself must not. It is stated over the components that hold amounts, so it can be checked on the two states alone;
- spent nullifiers: `voucher_nullifier_set` only grows, and `pow_nullifiers` loses entries only to the per-block pruning of [Proof of Work](../proof-of-work.md), which a migration does not perform.

The three state properties can stand in for "every reachable state" in the **Total** requirement: a migration defined for every state with these properties is defined for every reachable one.

Two candidates were left out. One `provider_id` and `zk_id` per service is not enforced by `SDP_DECLARE`, which checks only the declaration identifier and the service note. The lineage of a channel's configuration has no property a migration can be checked against.

## Open questions

- Whether the first migration that changes a component must also come with a machine-checked certificate: a proof, for example in Lean, that `migrate` is total, changes only its frame and preserves the properties, with the test vectors produced by the same function. Mandatory property testing on random states is the lighter alternative.
- Whether the properties should also cover `sdp_snapshot`, `next_sdp_snapshot` and the copies of epoch inputs in `blend_target`, which a migration could make inconsistent with the epoch states they were taken from.
- If [Block Rewards](../block-rewards.md)' pending pool and reserve become components, the token property must include them.

# Details

[Bedrock Eras](../bedrock-eras.md) §Era Migration, after the **Total** and **Identity by default** requirements:

- An era's specification states its migration as `migrate` in pseudocode, its frame (the components the era redefines), and test vectors: predecessor states and the states `migrate` returns for them, as encodings and state digests of [Bedrock Chain State](../bedrock-chain-state.md).
- An era whose migration changes no component states none of the three.
- `migrate` preserves, unless its era states a rule that breaks it:
    - the sum of the note values, `leaders_rewards`, `pending_leaders_rewards`, `blend_income`, the income of `blend_target`, `pow_reward_pool` and `pow_pool_refill`;
    - one note per leaf position;
    - a note in `notes` behind every channel note and every declaration's service note;
    - one declaration per service note and service;
    - every entry of `voucher_nullifier_set` and `pow_nullifiers`.

# Implementation

- [ ] For each era after the first, implement its `migrate` as specified and run it on the era's test vectors
- [ ] Check the five properties on the input and output of every test vector
- [ ] Add or extend tests that apply a migration at an era boundary, on the tip and on a block of the earlier era
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Bedrock Eras](../bedrock-eras.md) | Modified | required parts of a migration, preserved properties |
