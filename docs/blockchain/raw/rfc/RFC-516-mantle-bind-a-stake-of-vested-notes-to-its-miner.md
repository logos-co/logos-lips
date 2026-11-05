# [RFC] Mantle: Bind a stake of vested notes to its miner

**Motivation and proposal:** [PR #516](https://github.com/logos-co/logos-lips/pull/516)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-04 |
| v2 | Binds the `note_pk`, which now holds the stake, in place of the `zk_id`; corrects the cost per input | 2026-11-05 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle](#affected-specifications), [the binding constraint of the ZkStake](#2-the-zkstake-proves-the-binding) | the `note_pk` and every input with a non-zero `data` derive from one stake secret; inputs with `data` `0` stay free |
| 2 | High | [Mantle](#affected-specifications), [the derivation functions](#1-keys-derived-from-a-stake-secret) | domain separation between claim keys and service note keys; compression mode |
| 3 | High | [Service Declaration Protocol](#affected-specifications), [the `note_pk`](#3-the-note_pk-of-a-declaration) | the `note_pk` is now proven by every spend |
| 4 | Medium | [Wallet Technical Standard](#affected-specifications), [wallets that mine or declare](#4-wallets-that-mine-or-declare) | the stake secret; recovery of claims |
| 5 | Low | [Common Cryptographic Components](#affected-specifications) | skim — one more use of the compression mode |

# Discussion

## What the binding prevents

Without it, `SDP_DECLARE` creates the service note under any `note_pk` it names. The holder of the secret of the `note_pk` leads with the service note and withdraws it once the lock ends. A seller can stake its vested notes under a buyer's `note_pk` and `provider_id`, in one transaction with a Transfer paying the seller, and the buyer then holds the locked stake.

With the binding, the `note_pk` derives from the stake secret of the vested notes, so its secret key comes from the miner. In the same swap, the seller keeps the secret of the `note_pk` while the buyer holds the `provider_id`. Withdrawing takes both keys, so neither can withdraw alone. A sale of the stake then needs the seller to hand over the secret key of the `note_pk` off chain. The seller can still derive that key, so the buyer has to trust the seller. No protocol can prevent such a handover.

## The `zk_id` stays free

The `zk_id` receives the service rewards of the declaration and is the key of its Proof of Quota. A miner can therefore direct the service rewards of its locked stake to another party, without trust. Binding the `zk_id` as well would make such a sale need trust too, for one more key derivation in every ZkStake.

## Why one stake secret

Requiring the key of every vested input to equal the `note_pk` would make each claim name the public key of the service note. That links every claim of a provider to the others and to its declaration in public. A key derived from the stake secret reveals nothing about the secret or about the other keys, so claims stay unlinkable and nothing new becomes public.

## Cost

Measured by compiling the check with the Poseidon2 of the circuits repository (branch `tl/private_utxo`): 4,864 non-linear constraints for 16 inputs. Each input costs 244: one compression of 240 and 4 for the selection. Four compressions, 960 constraints, are paid once: three derive the `note_pk`, and one is the first step of every claim key. That is 2.4% of the about 203,000 non-linear constraints of the ZkStake. A derivation in the hash mode of Poseidon2 would cost 960 constraints instead of 240. The compression mode already derives every public key from its secret key.

The ZkStake gains one public input, which adds a term to the fixed part of its batch and leaves the cost per proof unchanged.

## What it costs the miner

- A miner derives the key of every claim it may stake from its stake secret, before it mines. A vested note claimed under another key can still lead and be spent once vested, but no declaration can stake it.
- The `note_pk` of every declaration with a spend derives from a stake secret, even when it stakes no vested note, since every ZkStake checks it. Any wallet can derive one.
- A wallet recovering from its seed finds its claims by deriving their public keys for increasing indices.

Notes whose `data` is `0` stay free of the check, since liquid tokens move anyway.

## Compatibility

The chain has not launched, so no migration is needed. The ZkStake gets a new public input and verification key, and the encoding does not change: the `note_pk` is already in the declaration.

# Details

## 1. Keys derived from a stake secret

Mantle's Vested Notes section defines the two derivations, in Poseidon2 compression mode:

```python
def claim_secret_key(stake_secret: ZkSecretKey, index: int) -> ZkSecretKey:
    return zkhash(zkhash(FiniteField(b"CLAIM_SECRET_KEY_V1", byte_order="little", modulus= p), stake_secret),
                  FiniteField(index, byte_order="little", modulus= p))

def service_note_secret_key(stake_secret: ZkSecretKey, index: int) -> ZkSecretKey:
    return zkhash(zkhash(FiniteField(b"SERVICE_NOTE_SECRET_KEY_V1", byte_order="little", modulus= p), stake_secret),
                  FiniteField(index, byte_order="little", modulus= p))
```

A miner pays each claim to the public key of `claim_secret_key(stake_secret, i)`, with a fresh `i` per claim, and declares with the public key of `service_note_secret_key(stake_secret, j)` as its `note_pk`.

## 2. The ZkStake proves the binding

```diff
 class ZkStakePublic:
     # ... inputs, flags, excess_value, tx_commitment_root unchanged
     vested_by: Slot
+    note_pk: ZkPublicKey            # the key of the service note of the declaration
     msg: zkhash

 class ZkStakeWitness:
     # ... inputs_sk, inputs_nonce, inputs_value, inputs_data and the paths unchanged
+    stake_secret: ZkSecretKey
+    note_index: int
+    inputs_index: list[int]         # (len = 16)
```

```python
assert note_pk == zkhash(FiniteField(b"KDF", byte_order="little", modulus= p),
                         service_note_secret_key(stake_secret, note_index))
assert all(
    inputs_sk[i] == claim_secret_key(stake_secret, inputs_index[i])
    or not inputs_active[i]
    or inputs_data[i] == 0
    for i in range(len(inputs_sk))
)
```

`SDP_DECLARE` passes `declaration.note_pk` to `verify_stake`, and `note_pk` follows `vested_by` in the public signal vector.

## 3. The `note_pk` of a declaration

The Service Declaration Protocol no longer says that no proof covers the `note_pk`: it derives from the stake secret of the declarer, and every spend of the declaration proves it.

## 4. Wallets that mine or declare

A wallet that mines or declares keeps a stake secret, the `k_logos` of a hardened child key it reserves for staking. It derives its claim keys and the `note_pk` of its declarations from it with fresh indices, and recovers its claims from the seed by their derived public keys.

## Chores

- Common Cryptographic Components lists the keys derived from a stake secret among the uses of the compression mode.
- Common Cryptographic Components writes the less-than of the strict EdDSA check as `\lt`, so GitHub renders the inline math.

# Implementation

- [ ] Add the `note_pk` public input, the stake secret, the indices and the derivation checks to the ZkStake circuit, and generate its key.
- [ ] Pass the `note_pk` of the declaration to the ZkStake verification of `SDP_DECLARE`.
- [ ] Derive claim keys and the `note_pk` of declarations from a stake secret in wallets that mine or declare, and recover claims by their derived public keys.
- [ ] Measure the fixed part of the ZkStake batch with its new public input.
- [ ] Add tests: a declaration staking vested notes under a `note_pk` of their stake secret is accepted; one under another `note_pk`, or with a vested input under an underived key, is rejected; a liquid input under any key is accepted.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.12.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.5.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.4.1 |
