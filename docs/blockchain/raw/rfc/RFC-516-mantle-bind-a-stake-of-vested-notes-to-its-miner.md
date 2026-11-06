# [RFC] Mantle: Bind a stake of vested notes to its miner

**Motivation and proposal:** [PR #516](https://github.com/logos-co/logos-lips/pull/516)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-04 |
| v2 | Binds the `note_pk`, which now holds the stake, in place of the `zk_id`; corrects the cost per input | 2026-11-05 |
| v3 | The `note_pk` secret alone withdraws, so a sale of the stake needs trust; every declaration with a spend is bound; wallets recover their declarations | 2026-11-05 |
| v4 | Follows the nullifier and staking keys of the stack; one derivation function for the keys of claims and of the `note_pk`; the binding drops the active flag | 2026-11-06 |
| v5 | Follows the staking key of a declaration and the service rewards going to its two keys: binding the `note_pk` now covers the rewards, the `zk_id` holds no funds, and the `note_stake_pk` stays free | 2026-11-06 |
| v6 | A declaration names only its `note_pk`, as public key and staking key, so a sale of the lottery of a locked stake needs trust too; the index of the `note_pk` is bounded, so a sale of claimed notes always needs trust | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle](#affected-specifications), [the binding constraint of the ZkStake](#2-the-zkstake-proves-the-binding) | the `note_pk` and every input with a non-zero `data` derive from one stake secret; inputs with `data` `0` stay free; the index of the `note_pk` is below `2^32` |
| 2 | Critical | **Start here** — [Mantle](#affected-specifications), [Service Declaration Protocol](#affected-specifications), [withdrawal by the `note_pk` secret](#5-withdrawal-by-the-note_pk-secret-alone) | `SDP_WITHDRAW` no longer takes the `provider_id` signature |
| 3 | High | [Mantle](#affected-specifications), [Service Declaration Protocol](#affected-specifications), [the staking key of a declaration](#6-the-staking-key-of-a-declaration) | a declaration names only the `note_pk`, and its service note and rewards take it as their staking key too |
| 4 | High | [Mantle](#affected-specifications), [the derivation function](#1-keys-derived-from-a-stake-secret) | one function for the keys of claims and of the `note_pk`; compression mode |
| 5 | High | [Service Declaration Protocol](#affected-specifications), [the `note_pk`](#3-the-note_pk-of-a-declaration) | the `note_pk` is now proven by every spend |
| 6 | Medium | [Wallet Technical Standard](#affected-specifications), [wallets that mine or declare](#4-wallets-that-mine-or-declare) | the stake secret; recovery of claims and declarations; a cold declaration keeps one key |
| 7 | Low | [Mantle Transaction Encoding](#affected-specifications), [Gas Cost Determination](#affected-specifications) | the withdrawal proof and its Execution Gas lose the signature; an `SDPDeclare` loses its `NoteStakePk` |
| 8 | Low | [Genesis Block](#affected-specifications), [Service Reward Distribution](#affected-specifications), [Cryptarchia](#affected-specifications) | skim — one key for a declaration and its rewards; regenerated test vectors |
| 9 | Low | [Common Cryptographic Components](#affected-specifications) | skim — one more use of the compression mode |

# Discussion

## What the binding prevents

Without it, `SDP_DECLARE` creates the service note under any `note_pk` it names. The holder of the spending secret key of the `note_pk` spends the service rewards and withdraws the service note once the lock ends. A seller can stake its vested notes under a buyer's `note_pk`, in one transaction with a Transfer paying the seller, and the buyer then holds the locked stake.

With the binding, the `note_pk` derives from the stake secret of the vested notes, so only the miner can declare them, and the miner can derive the spending secret key of the `note_pk` again. That key alone withdraws the declaration. A seller can still hand it to a buyer off chain, but it can also withdraw the stake itself once it unlocks, so the buyer has to trust the seller. No protocol can prevent such a sale.

Withdrawing used to take a `provider_id` signature as well. A seller could then name the buyer's `provider_id`, hand over the key, and be shut out of the withdrawal, so the sale needed no trust. Without the signature, a leaked spending secret key of the `note_pk` is enough to withdraw. The host of a node, which holds the `provider_id`, the key of the `zk_id` and at most the nullifier key of the service note, still cannot.

The binding covers notes already claimed. A buyer can still hand a miner public keys derived from its own stake secret. The puzzle binds the key of a claim, so the miner's claims then vest under the buyer's keys, and no rule tells this apart from the buyer mining.

The index of the `note_pk` is below `2^32`. With an unbounded index, a buyer could choose a random index, keep it secret and prove the ZkStake jointly with the miner, neither revealing its secret. The miner could then not derive the keys of the `note_pk`, so it could neither withdraw the stake nor lead with it, and the sale would need no trust. With the bound, the miner finds the index from the stake secret and the `note_pk` in at most `3 * 2^32` Poseidon2 compressions, about a day of one core at the 23,197 cycles of Gas Cost Determination.

## A declaration names one key

The service rewards of a declaration go to its `note_pk`, so binding the `note_pk` covers them too: the miner can derive the key that spends them. The `zk_id` holds no funds and needs no binding.

A separate staking key would leave the lottery open to sale. A miner could name a buyer's staking key and hand over the nullifier key of the `note_pk`. Only the buyer could then lead with the service note and the service rewards, and the leader rewards go to any key it chooses. That is a sale without trust, until the lock ends.

A declaration therefore names no `note_stake_pk`: the service note and the rewards take the `note_pk` as their staking key too. Their staking secret key is then their nullifier key, which the miner can derive. A miner can still hand that key to a buyer off chain, but it can also lead with the notes itself, so the buyer has to trust the seller.

## Why one stake secret

Requiring the key of every vested input to equal the `note_pk` would make each claim name the public key of the service note. That links every claim of a provider to the others and to its declaration in public. One secret key for all of them, with a second public key derivation for the declaration, is not available: the ZkTransfer that withdraws the service note derives its public key like that of any note. A key derived from the stake secret reveals nothing about the secret or about the other keys, so claims stay unlinkable and nothing new becomes public.

## Cost

Measured by compiling the check with the Poseidon2 of the circuits repository (branch `tl/private_utxo`): 4,848 non-linear constraints for 16 inputs. Each input costs 241: one compression of 240 and 1 for the selection, `inputs_data[i] * (derived - inputs_spending_sk[i]) == 0`. Four compressions, 960 constraints, are paid once: the first step of every key, the step of the index of the `note_pk`, and its nullifier key and public key. The bound on that index costs 32. That is 2.3% of the about 211,000 non-linear constraints of the ZkStake. A derivation step in the hash mode of Poseidon2, a hash of two elements, would cost 720 constraints instead of 240. The compression mode already derives every public key from its secret key.

The ZkStake gains one public input, which adds a term to the fixed part of its batch and leaves the cost per proof unchanged.

## What it costs the miner

- A miner derives the key of every claim it may stake from its stake secret, before it mines. A vested note claimed under another key can still lead and be spent once vested, but no declaration can stake it.
- The `note_pk` of every declaration with a spend derives from a stake secret, even when it stakes no vested note, since every ZkStake checks it. Any wallet can derive one.
- A declaration has no separate staking key, even when it stakes no vested note, since the ledger does not see which notes are vested. The holder of the nullifier key of the `note_pk` can always lead with the service note and the service rewards. A wallet keeps one key for a note by default anyway.
- A wallet recovering from its seed finds its claims and its declarations by deriving their public keys for increasing indices.
- A ZkStake takes the stake secret as a witness, so a declarer who delegates its proving reveals every claim key derived from it, and with them the link between its claims.

Notes that never vest, whose `data` is `0`, stay free of the check, since they move anyway. A vested note stays bound after its vesting ends, until a Transfer turns it into a note with `data` `0`.

## Compatibility

The chain has not launched, so no migration is needed. The ZkStake gets a new public input and verification key. An `SDPDeclare` loses its `NoteStakePk`, 32 bytes, and the proof of an `SDPWithdraw` loses its signature. Notes keep their staking key, so the Proof of Leadership and the ZkTransfer do not change.

# Details

## 1. Keys derived from a stake secret

Mantle's Vested Notes section defines the derivation, in Poseidon2 compression mode:

```python
def derive_spending_sk(stake_secret: ZkSecretKey, index: int) -> ZkSecretKey:
    return zkhash(zkhash(FiniteField(b"STAKE_SPENDING_SK_V1", byte_order="little", modulus= p), stake_secret),
                  FiniteField(index, byte_order="little", modulus= p))
```

A miner pays each claim to the public key of `derive_spending_sk(stake_secret, i)`, with a fresh `i` per claim, and declares with the public key of `derive_spending_sk(stake_secret, j)`, with another fresh index, as its `note_pk`.

## 2. The ZkStake proves the binding

```diff
 class ZkStakePublic:
     # ... inputs, flags, excess_value, tx_commitment_root unchanged
     spending_slot: Slot
+    note_pk: ZkPublicKey            # the key of the service note of the declaration
     msg: zkhash

 class ZkStakeWitness:
     # ... inputs_spending_sk, inputs_stake_pk, inputs_nonce, inputs_value, inputs_data and the paths unchanged
+    stake_secret: ZkSecretKey
+    note_index: int
+    inputs_index: list[int]         # (len = 16)
```

```python
assert note_index < 2**32
note_nf_sk = zkhash(FiniteField(b"NF_KDF", byte_order="little", modulus= p),
                    derive_spending_sk(stake_secret, note_index))
assert note_pk == zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), note_nf_sk)
assert all(
    inputs_spending_sk[i] == derive_spending_sk(stake_secret, inputs_index[i])
    or inputs_data[i] == 0
    for i in range(len(inputs_spending_sk))
)
```

`SDP_DECLARE` passes `declaration.note_pk` to `verify_stake`, and `note_pk` follows `spending_slot` in the public signal vector.

The binding reads no input flag: the prover sets the `data` of an inactive input to `0`, which exempts it.

## 3. The `note_pk` of a declaration

A valid declaration has a `note_pk` derived from a stake secret of the sender, from which the keys of the vested notes of its spends also derive. The Service Declaration Protocol lists this among the conditions of a valid declaration, and neither specification says any longer that no check reads the `note_pk`.

## 4. Wallets that mine or declare

A wallet that mines or declares keeps a stake secret, the `k_logos` of a hardened child key it reserves for staking. It derives the keys of its claims and of the `note_pk` of its declarations from it, taking the indices in order. It recovers its claims and its declarations from the seed by their derived public keys, until 1,000 consecutive indices match nothing.

## 5. Withdrawal by the `note_pk` secret alone

`SDP_WITHDRAW` drops the `provider_id` signature. The ZkTransfer consuming the service note, by the holder of the spending secret key of the `note_pk`, authorizes the withdrawal.

```diff
 class WithdrawProof:
     zk_proof: ZkTransfer             # consuming the service note
-    provider_sig: Ed25519Signature   # signature proving ownership of provider key
```

- Validation drops its signature step, and the nonce and ZkTransfer checks become steps 3 and 4.
- Execution Gas: `EXECUTION_SDP_WITHDRAW_GAS + spend_gas([service_note], outputs)`, without `EXECUTION_SIGNATURE_GAS`.
- Encoding: an `SDPWithdraw` is proven by a `ZkTransferProof`. `ZkTransferAndEd25519SigProof`, which no Operation uses any more, is removed.
- The Service Declaration Protocol no longer requires the withdraw message to be signed by the `provider_id`.

## 6. The staking key of a declaration

`DeclarationMessage`, `DeclarationInfo` and the encoding of an `SDPDeclare` lose the `note_stake_pk`. The service note and the service reward notes take the `note_pk` as their staking key:

```diff
 service_note = Note(
     value=stake,
     nonce=derive_note_nonce(declaration_op_id, 0, stake, declaration.note_pk),
     public_key=declaration.note_pk,
-    stake_public_key=declaration.note_stake_pk
+    stake_public_key=declaration.note_pk
 )
```

The declarations of the Genesis Block name one key in the same way. In the Wallet Technical Standard, a cold declaration keeps one key, and its node leads with the nullifier key of the `note_pk`. The `SDP_DECLARE` test vectors of Mantle, and the vectors of Cryptarchia that depend on them, are regenerated.

## Chores

- Common Cryptographic Components lists the keys derived from a stake secret among the uses of the compression mode.
- Common Cryptographic Components writes the less-than of the strict EdDSA check as `\lt`, so GitHub renders the inline math.
- Mantle no longer says that a sequencer can stake every note whose staking key it chooses. It can stake only the notes whose nullifier key it knows, which excludes a payout to a payee's key.

# Implementation

- [ ] Add the `note_pk` public input, the stake secret, the indices, the bound on the `note_index` and the derivation checks to the ZkStake circuit, and generate its key.
- [ ] Pass the `note_pk` of the declaration to the ZkStake verification of `SDP_DECLARE`.
- [ ] Drop the `note_stake_pk` from `SDP_DECLARE`, its encoding and `DeclarationInfo`, and create the service note and the service reward notes with the `note_pk` as their staking key.
- [ ] Drop the `provider_id` signature from `SDP_WITHDRAW`, from the encoding of its proof and from its Execution Gas.
- [ ] Derive claim keys and the `note_pk` of declarations from a stake secret in wallets that mine or declare, and recover claims and declarations by their derived public keys.
- [ ] Measure the fixed part of the ZkStake batch with its new public input.
- [ ] Add tests: a declaration staking vested notes under a `note_pk` of their stake secret is accepted; one under another `note_pk`, with a vested input under an underived key, or with a `note_index` of `2^32` or more, is rejected; a liquid input under any key is accepted; a withdrawal proven by the spending secret key of the `note_pk` alone is accepted.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.12.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.5.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.3.0 |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 2.2.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.4.1 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.3.3 |
| [Service Reward Distribution](../bedrock-service-reward-distribution.md) | Modified | Revision 1.4.2 |
| [Cryptarchia](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.3 |
