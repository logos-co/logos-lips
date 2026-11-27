# [RFC] Mantle: Solve the reward puzzle with HashWX

**Motivation and proposal:** [PR #447](https://github.com/logos-co/logos-lips/pull/447)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC. The reward puzzle is HashWX. It replaces the Equi-X design the PR described before | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first. HashWX itself is defined in Common Cryptographic Components by the change that prices Blend edge admission with HashWX. This change links to that definition and does not restate it.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle](#affected-specifications), [the claim](#1-the-claim) | `nonce` becomes a `uint64`; validation steps 4 and 5 derive the challenge, the HashWX ticket and a tagged nullifier |
| 2 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the reward puzzle](#2-the-reward-puzzle-and-its-threshold) | two puzzles with separate thresholds; `difficulty_reward` is a 64-bit integer; `REWARD_TARGET_CAP` comes from the target machine's rate |
| 3 | Critical | [Mantle Transaction Encoding](#affected-specifications), [the encoding](#3-the-encoding) | `PowNonce = UINT64`, 24 bytes smaller |
| 4 | Medium | [Cryptarchia](#affected-specifications) and [Mantle](#affected-specifications), [test vectors](#5-test-vectors) | the vectors that hold a claim, regenerated; the new Reward Claim Ticket vector |
| 5 | Medium | [Gas Cost Determination](#affected-specifications), [the gas](#4-the-gas-of-a-claim) | the cost of the ticket is `TBD` until measured |

# Discussion

## Why HashWX for the reward

The Blend puzzle keeps `zkhash`, because a Blend solution is proven inside the Proof of Quota circuit. HashWX runs random programs over a 16 KB scratchpad, and no circuit holds that at a sensible cost.

A reward claim is checked by validators in ordinary code, so nothing there needs a circuit-friendly hash. `zkhash` is a small arithmetic kernel over a fixed field, which is what dedicated hardware does best. HashWX builds a new program for every 463 nonces, so its work stays on general-purpose processors. Checking a claim costs one HashWX hash.

The PR first proposed Equi-X. Its author deprecated it on 2026-10-15. HashWX's own form is `H(N) < T`, the same form as the current `ticket < threshold`. So the retarget keeps its shape and changes only its types.

## The cap

`REWARD_TARGET_CAP` keeps the time to a claim that the `zkhash` cap gave: about 1,620 seconds, 27 minutes, on all four cores of the target machine. It derives from `HASHWX_MACHINE_RATE`, the measured rate of a Raspberry Pi 5, rather than being written as a field element.

## The nullifier

A ticket has 64 bits and no collision resistance, so it must not be an identifier. The nullifier is therefore a 32-byte hash of the challenge and the nonce. It carries the tag `POW_NULLIFIER_V1`. Without the tag, the nullifier of a nonce would equal the seed of the group with that number under the same challenge. No attack follows from that, but the two hashes should not share a domain.

## Open questions

- **The definition.** HashWX is defined by the edge-admission change. Until that change lands, this change's link to the definition has no target, and this change cannot merge before it.
- **The licence.** The known implementations of HashWX are under the LGPL, which the node's licence policy does not allow. A permissive reimplementation is planned.
- **The author's caution.** HashWX's author advises against using it for proof-of-work consensus. Here it prices rewards, not consensus.
- **Audit.** No audit of HashWX is known.
- **Gas.** The cost of one HashWX ticket is to be measured on the gas analysis's machine and method.

## Compatibility

Bedrock has no genesis yet, so the change needs no migration. The encoding of `CLAIM_POW_REWARD` changes, and so does every test vector that holds a claim.

# Details

## 1. The claim

The claim carries a 64-bit nonce. Validation step 4 derives a challenge from the public key, the referenced block and the epoch nonce, and takes the HashWX ticket of the nonce for it. Step 5 checks a nullifier that hashes the challenge and the nonce.

```diff
 class ClaimPowRewardOp:
     # ...
-    nonce: zkhash              # Value searched for a ticket satisfying the reward threshold
+    nonce: uint64              # Value searched for a ticket satisfying the reward threshold
```

```diff
-puzzle_ticket = zkhash(FiniteField(b"POW_CLAIM_V1", byte_order="little", modulus=p),
-                       claim.public_key,
-                       claim.nonce,
-                       FiniteField(claim.block_hash, byte_order="little", modulus=p),
-                       claim.epoch_nonce)
+challenge = Hash(b"POW_CLAIM_V1" + encode(claim.public_key) + claim.block_hash
+                 + encode(claim.epoch_nonce))
+puzzle_ticket = hashwx_ticket(challenge, claim.nonce)
 # ...
-# 5. The solution must not have been claimed before. The nullifier is the ticket.
-assert puzzle_ticket not in pow_nullifiers
+# 5. The solution must not have been claimed before.
+pow_nullifier = Hash(b"POW_NULLIFIER_V1" + challenge + encode(claim.nonce))
+assert pow_nullifier not in pow_nullifiers
```

Execution adds `pow_nullifier` to `pow_nullifiers`. The state types change to match:

```diff
-difficulty_reward: PowTarget     # the reward threshold, retargeted every block
-pow_nullifiers: set[zkhash]      # Spent solutions, retained for the acceptance window
+difficulty_reward: uint64        # the reward threshold, retargeted every block
+pow_nullifiers: set[hash]        # Spent solutions, retained for the acceptance window
```

## 2. The reward puzzle and its threshold

Proof of Work holds two puzzles. The Blend puzzle is unchanged: `zkhash` over a private nonce and the epoch nonce, below `difficulty_blend` in $`\mathbb{F}_p`$. The reward puzzle is the HashWX ticket of a 64-bit nonce, below `difficulty_reward`, an unsigned 64-bit integer.

```diff
-REWARD_TARGET_CAP: PowTarget = p // 2**26       # largest target the retarget returns, and its genesis value
+REWARD_TARGET_CAP: uint64 = 2**64 // (HASHWX_MACHINE_RATE * 1_620)  # largest target the retarget returns, and its genesis value
```

The reward retarget keeps its rule. Its types become `uint64`, and its product stays below $`2^{71}`$, so it needs 128-bit arithmetic rather than 512-bit.

```diff
 def compute_new_reward_difficulty(claims_in_block: uint64,
-                                  current_target: PowTarget) -> PowTarget:
-    # 512-bit integers over canonical representatives; see Puzzle Target.
+                                  current_target: uint64) -> uint64:
+    # 128-bit integers; see Puzzle Target.
     # ...
```

## 3. The encoding

```diff
-PowNonce       = FieldElement ; value searched for a ticket satisfying the reward threshold
+PowNonce       = UINT64       ; value searched for a ticket satisfying the reward threshold
```

## 4. The gas of a claim

Re-deriving the ticket costs one HashWX ticket, `TBD` until it is measured. The `zkhash` measure of five field elements, 138,681, goes.

## 5. Test vectors

The block vectors of Cryptarchia and the operation vectors of Mantle hold a claim, so they are regenerated with the 64-bit nonce. Mantle gains a Reward Claim Ticket vector: the `challenge`, the `puzzle_ticket` and the `pow_nullifier` of the vector's claim.

## Chores

- The Introduction and Overview of Proof of Work describe two puzzles, each with its own use and threshold.
- "Ticket spent" becomes "solution spent" throughout.
- The Notation's $`p`$ row covers only the Blend ticket and threshold.

# Implementation

- [ ] Land this after the edge-admission change that defines HashWX.
- [ ] Implement HashWX under a licence the node's policy allows.
- [ ] Change the nonce of `CLAIM_POW_REWARD` to a `uint64`, encoded as `UINT64`.
- [ ] Derive the challenge, the HashWX ticket and the tagged nullifier in validation, and store the nullifier as a 32-byte hash.
- [ ] Make `difficulty_reward` a `uint64` with 128-bit retarget arithmetic, and set `REWARD_TARGET_CAP` from `HASHWX_MACHINE_RATE`.
- [ ] Measure the gas of one HashWX ticket and fill the `TBD`.
- [ ] Regenerate the test vectors that hold a claim, and add tests for nonces 462 and 463, which use different seeds, and for a nonce above $`2^{32}`$.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.4.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.3.0 |
| [Cryptarchia](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.3, test vectors |
| [\[Analysis\] Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 2.2.0 |
