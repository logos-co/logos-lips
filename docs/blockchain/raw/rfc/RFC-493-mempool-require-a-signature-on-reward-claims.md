# [RFC] Mempool: Require a signature on reward claims

**Motivation and proposal:** [PR #493](https://github.com/logos-co/logos-lips/pull/493)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-21 |

## Reviewer Orientation

Single-document change — read [Decoding](../mempool.md#decoding), [Stateless Validation](../mempool.md#stateless-validation) and [Block Building View](../mempool.md#block-building-view) in the [Mempool](../mempool.md), and focus on the proof of a `CLAIM_POW_REWARD`, which the mempool now decodes and verifies as Mantle specifies.

# Discussion

## What the implementation does

[CLAIM_POW_REWARD](../bedrock-v1.1-mantle-specification.md#claim_pow_reward) names `public_key`, the key a reward is paid to. Its proof is a `ZkSignature` by the secret key of `public_key` over the transaction's hash, and step 6 of its validation checks that signature. [Mantle Transaction Encoding](../mantle-transaction-encoding.md) encodes the proof as a 128-byte `ZkSigProof`.

Until this change, the specification described what `logos-blockchain` does at `60744b8e7`. The implementation gives a claim an empty proof. It encodes the claim with no proof bytes, `preverify` accepts every claim, and the ledger runs steps 1 to 5 of the validation but not step 6. Two things follow:

- Claims are encoded two ways. A claim that carries the signature, as Mantle specifies, leaves 128 bytes that the implementation's decoder does not expect, so the implementation rejects it as malformed. A claim without the signature lacks the bytes that a decoder following Mantle reads, and fails there.
- The puzzle costs less than [Proof of Work](../proof-of-work.md) intends, where a miner searches public keys whose secret keys it knows. Without the signature, a solver can try public keys directly and skip deriving each one from a secret key. The reward then goes to a key that may have no known secret key. The claim still takes `epoch_pow_reward` from the pool, spends its ticket and raises `difficulty_reward`, so draining the pool and crowding out other miners cost less.

The claims the implementation itself publishes prove knowledge of the key anyway, since each transaction spends the reward notes to pay its fee, and that spend is signed. A claim whose fee another note pays proves nothing.

The signature does not guard against theft. The ticket hashes `public_key`, so changing the key a valid claim pays invalidates the claim.

## What changes

A claim's proof is treated like any other Operation's. It decodes as Mantle Transaction Encoding specifies. `preverify` verifies it, since it is bound only to the transaction hash and to the payload's `public_key`. Block building checks it through step 6 of the claim's validation. A claim without a valid signature is refused at admission.

The network has no genesis block yet, so the change to how claims are encoded needs no migration.

# Details

## A claim's proof decodes as Mantle specifies

[Decoding](../mempool.md#decoding) drops the exception for a claim's proof:

```diff
-The proof of a `CLAIM_POW_REWARD` is empty, in place of the `ZkSigProof` that Mantle Transaction Encoding gives it.
```

## Admission verifies a claim's signature

[Stateless Validation](../mempool.md#stateless-validation) drops the empty proof from rule 1:

```diff
-1. Rule 1 of [Validation](bedrock-v1.1-mantle-specification.md#validation) holds, with an empty proof for a `CLAIM_POW_REWARD`.
+1. Rule 1 of [Validation](bedrock-v1.1-mantle-specification.md#validation) holds.
```

Rule 2 then verifies the claim's signature, which is bound only to the transaction hash and the payload.

## Block building checks it

[Block Building View](../mempool.md#block-building-view) no longer skips the signature check:

```diff
-It skips step 6 of the [CLAIM_POW_REWARD](bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation, the signature check, since a claim's proof is empty.
```

# Implementation

- [ ]  Give `ClaimPowRewardOp` the `ZkSignature` proof, so that its proof is encoded and decoded as Mantle Transaction Encoding specifies
- [ ]  Verify a claim's signature in `preverify`, against `public_key` and the transaction hash
- [ ]  Check the signature in the ledger, as step 6 of the `CLAIM_POW_REWARD` validation specifies
- [ ]  Sign every claim the proof of work service publishes
- [ ]  Add or extend tests: a claim without a valid signature is refused at admission and makes a block invalid, and a signed one is admitted and applies
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | A reward claim's proof is decoded, verified at admission and checked in block building as Mantle specifies. |
