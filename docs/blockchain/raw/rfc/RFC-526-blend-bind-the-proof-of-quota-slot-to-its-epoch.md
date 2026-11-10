# [RFC] Blend: Bind the Proof of Quota slot to its epoch

**Motivation and proposal:** [PR #526](https://github.com/logos-co/logos-lips/pull/526)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-09 |
| v2 | The verifier passes the last slot of the epoch in place of the epoch length, so the check is two 64-bit range checks (128 constraints, was 193); removed the argument against a last slot | 2026-11-10 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Every proof carries a slot of the epoch](#1-every-proof-carries-a-slot-of-the-epoch), in the [Proof of Quota](#affected-specifications) | the check binds every branch; both differences are range-checked, so a slot outside the epoch fails |
| 2 | High | [Two public inputs carry the slots of the epoch](#2-two-public-inputs-carry-the-slots-of-the-epoch), in the [Proof of Quota](#affected-specifications) | the inputs follow `pol_t1`, so existing signal positions hold; their derivation from the epoch schedule |
| 3 | High | [Core and proof of work provers fill `pol_sl` with a slot of the epoch](#3-core-and-proof-of-work-provers-fill-pol_sl-with-a-slot-of-the-epoch), in both [specifications](#affected-specifications) | a prover that keeps filling `pol_sl` with arbitrary data now fails |

# Discussion

## Every branch or only the leader branch

The check binds `pol_sl` in every branch, although only the leader branch reads the slot. The alternative gates it to the leader branch: the circuit multiplies both differences by the leader selector before the range checks, so core and proof of work provers keep filling `pol_sl` with arbitrary data. The gate has to act on the differences themselves. The range checks are constraints in every branch, and would reject a core prover's arbitrary slot.

The gated form costs two more multiplications. The ungated form needs no selector arithmetic, and its cost falls on core and proof of work provers, which must now fill `pol_sl` with a slot of the epoch. An implementation that keeps a fixed filler such as `0` produces invalid core and proof of work proofs from epoch 1 onward.

## Privacy

Neither form reveals which branch a proof uses. The two new inputs are the same for every proof of an epoch. `pol_sl` stays a private witness, and the proof reveals nothing about the witness. A node cannot probe a proof by verifying it against a shifted range either: a Groth16 proof verifies only against the public inputs it was made for, so a changed range fails every proof alike.

## The range

The verifier passes the first and the last slot of the epoch, rather than the epoch length or an epoch number. Each bound then needs one range check. With the length, the circuit would need a comparison, or would rebuild the last slot from it. With an epoch number, the circuit would compute the slots itself and assume that every epoch has the same length. A length hard-coded into the circuit would need new keys whenever `k` or `f` changes. Both values come from the Cryptarchia epoch schedule, so the change adds no parameter.

Both values fit 64 bits, the width of the slot in the block header: the epoch with the largest epoch number, `2^32 − 1`, ends before slot `2^52`. Taking the differences in the scalar field makes the range checks sound. For a slot outside the epoch, one difference wraps around to a value near the field modulus and fails its 64-bit range check.

## Cost

With circomlib's `Num2Bits`, the check costs 128 constraints: one 64-bit range check per difference.

## Compatibility

The public signal vector grows from twelve to fourteen entries. The output and the eleven existing inputs keep their positions. The serialized proof stays 160 bytes, and no message format changes. The circuit needs new proving and verification keys, so the circuit and the node must upgrade together: each rejects the proofs of the other. Bedrock has no deployed network, so the change needs no migration.

# Details

## 1. Every proof carries a slot of the epoch

Step 1 of the [Constraints](../proof-of-quota.md#constraints) gains a rule for every branch:

> Whatever the branch, `pol_sl` must be a slot of the epoch: `pol_epoch_first_slot <= pol_sl <= pol_epoch_last_slot`.

The [Pseudocode](../proof-of-quota.md#pseudocode) checks it right after the quota check, outside any branch term:

```diff
 index < core_quota + (leader_quota - core_quota) * L1 + (pow_quota - core_quota) * L2
 
+# Verify pol_sl is a slot of the epoch, whatever the branch. Both differences
+# are taken in the scalar field and must fit 64 bits: for a slot outside the
+# epoch, one of them wraps around the field.
+pol_sl - pol_epoch_first_slot < 2**64
+pol_epoch_last_slot - pol_sl < 2**64
```

Step 3 now names the slot the leader's note would win: "the slot `pol_sl`" in place of "a slot".

## 2. Two public inputs carry the slots of the epoch

```diff
 class ProofOfQuotaPublic:
     # ... unchanged fields elided
     pol_t1: int           # PoL constant t1
+    pol_epoch_first_slot: int # First slot of the epoch (64 bits)
+    pol_epoch_last_slot: int  # Last slot of the epoch (64 bits)
```

For the epoch `ep`, `pol_epoch_first_slot` is `ep · EPOCH_LENGTH` and `pol_epoch_last_slot` is `(ep + 1) · EPOCH_LENGTH − 1`, where `EPOCH_LENGTH` is the [epoch length](../cryptarchia-v1-protocol.md#epoch-schedule) of `10⌊k/f⌋` slots, 648,000 at `k = 2160` and `f = 1/30`. In the [Message Encapsulation Mechanism](../message-encapsulation.md#keys-and-proof-generation), a prover reads both from the chain with the other public values.

## 3. Core and proof of work provers fill `pol_sl` with a slot of the epoch

`pol_sl` leaves the group of witness fields that core nodes and proof of work provers fill at random:

```diff
 class ProofOfQuotaWitness:
     index: int           # ...
     selector: int        # ...
+    pol_sl: int          # PoL slot: the winning slot for a leader, else any slot of the epoch (64 bits)
     # This part is filled randomly by potential leaders and by proof of work provers
     # ... core_sk, core_path, core_path_selectors
     # This part is filled randomly by core nodes and by proof of work provers
-    pol_sl: int          # PoL slot
     pol_secret_key: int  # PoL note secret key
```

The core and proof of work cases of the [Proof of Quota generation](../message-encapsulation.md#keys-and-proof-generation) say the same:

```diff
-4. The rest of the `ProofOfQuotaWitness` is filled with arbitrary data.
+4. The `pol_sl` is any slot of the epoch ([Constraints](proof-of-quota.md#constraints)), and the rest of the `ProofOfQuotaWitness` is filled with arbitrary data.
```

## Chores

- Removed a stray comma from the core case of the Proof of Quota generation in the Message Encapsulation Mechanism.

# Implementation

- [ ] In the PoQ circuit, add `pol_epoch_first_slot` and `pol_epoch_last_slot` as public inputs declared after `pol_t1`, so the existing public signals keep their positions.
- [ ] In the PoQ circuit, range-check `pol_sl - pol_epoch_first_slot` and `pol_epoch_last_slot - pol_sl` to 64 bits each (`Num2Bits(64)`), in every branch.
- [ ] Regenerate the circuit's sample inputs so that core and proof of work witnesses carry a slot of the epoch, and release new proving and verification keys.
- [ ] In the node, carry the two inputs through the PoQ prover and verifier inputs, which grow from 12 to 14 signals. Fill them from the same epoch as `pol_epoch_nonce` at every site that builds them, including the verification of messages from the previous epoch during the transition period.
- [ ] In the node, fill `pol_sl` with a slot of the epoch, such as its first slot, in core and proof of work proofs.
- [ ] Add tests: core, leader and proof of work proofs verify with a slot of the epoch; a leader proof for a winning slot outside the epoch fails; a core or proof of work proof with a slot outside the epoch fails.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Proof of Quota](../proof-of-quota.md) | Modified | Revision 1.3.0 |
| [Message Encapsulation Mechanism](../message-encapsulation.md) | Modified | Revision 1.3.0 |
