# [RFC] Mantle: Bind a stake of vested notes to its miner

**Motivation and proposal:** [PR #516](https://github.com/logos-co/logos-lips/pull/516)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-04 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle](#affected-specifications), [the binding constraint of the ZkStake](#2-the-zkstake-proves-the-binding) | the `zk_id` and every input with a non-zero `data` derive from one stake secret; inputs with `data` `0` stay free |
| 2 | High | [Mantle](#affected-specifications), [the derivation functions](#1-keys-derived-from-a-stake-secret) | domain separation between claim keys and `zk_id` keys; compression mode |
| 3 | High | [Service Declaration Protocol](#affected-specifications), [the `zk_id`](#3-the-zk_id-of-a-declaration) | the `zk_id` is now proven by every spend |
| 4 | Medium | [Wallet Technical Standard](#affected-specifications), [mining wallets](#4-mining-wallets) | the stake secret; recovery of claims |
| 5 | Low | [Common Cryptographic Components](#affected-specifications) | skim — one more use of the compression mode |

# Discussion

## What the binding prevents

Without it, `SDP_DECLARE` creates the service note under any `zk_id` it names. A seller can stake its vested notes under a buyer's `zk_id` and `provider_id`, in one transaction with a Transfer paying the seller, and the buyer then holds the locked stake. With the binding, the `zk_id` derives from the stake secret of the vested notes, so only the miner can hold its secret key. In the same swap, the seller keeps the `zk_id` secret, and with it the service rewards and the Proof of Quota of the declaration, while the buyer holds the `provider_id`. Withdrawing takes both keys, so neither can withdraw alone. A sale then needs the seller to hand over a secret off chain, which needs trust, and no protocol can prevent it.

## Why one stake secret

Requiring the key of every vested input to equal the `zk_id` would make each claim name the public key of the `zk_id`, which links every claim of a provider in public. A key derived from the stake secret reveals nothing about the secret or about the other keys, so claims stay unlinkable and nothing new becomes public.

## Cost

Measured by compiling the check with the compression of the circuits repository (branch `tl/private_utxo`): 4,864 constraints for 16 inputs, 243 per vested input plus 972 once for the `zk_id`. That is 2.4% of the 202,928 constraints of the ZkStake. The hash mode of Poseidon2 would cost about 963 constraints per input instead of 243. The compression mode already derives every public key from its secret key.

The ZkStake gains one public input, which adds a term to the fixed part of its batch and leaves the cost per proof unchanged.

## What it costs the miner

- A miner derives the key of every claim it may stake from its stake secret, before it mines. A vested note claimed under another key can still lead and be spent once vested, but no declaration can stake it.
- Every declaration's `zk_id` derives from a stake secret, also one that stakes no vested note, since every ZkStake checks it. Any wallet can derive one.
- A wallet recovering from its seed finds its claims by deriving their public keys for increasing indices.

Notes whose `data` is `0` stay free of the check, since liquid tokens move anyway.

## Compatibility

The chain has not launched, so no migration is needed. The ZkStake gets a new public input and verification key, and the encoding does not change: the `zk_id` is already in the declaration.

# Details

## 1. Keys derived from a stake secret

Mantle's Vested Notes section defines the two derivations, in Poseidon2 compression mode:

```python
def claim_secret_key(stake_secret: ZkSecretKey, index: int) -> ZkSecretKey:
    return zkhash(zkhash(FiniteField(b"CLAIM_SECRET_KEY_V1", byte_order="little", modulus= p), stake_secret),
                  FiniteField(index, byte_order="little", modulus= p))

def zk_id_secret_key(stake_secret: ZkSecretKey, index: int) -> ZkSecretKey:
    return zkhash(zkhash(FiniteField(b"ZK_ID_SECRET_KEY_V1", byte_order="little", modulus= p), stake_secret),
                  FiniteField(index, byte_order="little", modulus= p))
```

A miner pays each claim to the public key of `claim_secret_key(stake_secret, i)`, with a fresh `i` per claim, and declares with the public key of `zk_id_secret_key(stake_secret, j)`.

## 2. The ZkStake proves the binding

```diff
 class ZkStakePublic:
     # ... inputs, flags, excess_value, tx_cm_root unchanged
     vested_by: Slot
+    zk_id: ZkPublicKey             # the zk_id of the declaration
     msg: zkhash

 class ZkStakeWitness:
     # ... inputs_sk, inputs_nonce, inputs_value, inputs_data and the paths unchanged
+    stake_secret: ZkSecretKey
+    zk_id_index: int
+    inputs_index: list[int]        # (len = 16)
```

```python
assert zk_id == zkhash(FiniteField(b"KDF", byte_order="little", modulus= p),
                       zk_id_secret_key(stake_secret, zk_id_index))
assert all(
    inputs_sk[i] == claim_secret_key(stake_secret, inputs_index[i])
    or not inputs_active[i]
    or inputs_data[i] == 0
    for i in range(len(inputs_sk))
)
```

`SDP_DECLARE` passes `declaration.zk_id` to `verify_stake`, and `zk_id` follows `vested_by` in the public signal vector.

## 3. The `zk_id` of a declaration

The Service Declaration Protocol no longer calls the `zk_id` a random key the declaration does not prove: it derives from the stake secret of the declarer, and every spend of the declaration proves it.

## 4. Mining wallets

A wallet that mines keeps a stake secret, the `k_logos` of a hardened child key it reserves for staking, derives its claim keys and `zk_id`s from it with fresh indices, and recovers its claims from the seed by their derived public keys.

## Chores

- Common Cryptographic Components lists the keys derived from a stake secret among the uses of the compression mode.
- Common Cryptographic Components writes the less-than of the strict EdDSA check as `\lt`, so GitHub renders the inline math.

# Implementation

- [ ] Add the `zk_id` public input, the stake secret, the indices and the derivation checks to the ZkStake circuit, and generate its key.
- [ ] Pass the `zk_id` of the declaration to the ZkStake verification of `SDP_DECLARE`.
- [ ] Derive claim keys and `zk_id`s from a stake secret in mining wallets, and recover claims by their derived public keys.
- [ ] Measure the fixed part of the ZkStake batch with its new public input.
- [ ] Add tests: a declaration staking vested notes under a `zk_id` of their stake secret is accepted; one under another `zk_id`, or with a vested input under an underived key, is rejected; a liquid input under any key is accepted.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.12.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.5.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.4.1 |
