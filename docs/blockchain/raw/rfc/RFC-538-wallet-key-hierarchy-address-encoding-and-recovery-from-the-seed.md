# [RFC] Wallet: Key hierarchy, address encoding and recovery from the seed

**Motivation and proposal:** [PR #538](https://github.com/logos-co/logos-lips/pull/538)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-17 |
| v2 | Follows revision v5 of [RFC-486](RFC-486-mantle-post-quantum-note-encryption.md): the note encryption key derives from the ZK secret key `k_logos`, so the `sk_enc`, the `pk_enc` and the full address of the test vectors are regenerated. The key-only addresses and every other vector are unchanged | 2026-11-17 |

## Reviewer Orientation

Read the PR's Motivation first. The private ledger of [RFC-480](RFC-480-mantle-private-utxo-ledger.md), the key split of [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) and the note encryption of [RFC-486](RFC-486-mantle-post-quantum-note-encryption.md) are assumed. One document changes, the [Wallet Technical Standard](#affected-specifications). Nothing changes in the Operations, the circuits or the encodings.

| # | Priority | Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Address encoding](#1-address-encoding) | the byte layout, the checksum and what it guarantees at 2011 characters, the list of mandatory rejections; a wrong address loses the note |
| 2 | High | [Key hierarchy](#2-key-hierarchy) | the three roles and the rule that separates them, the keys a node holds online, the difference with the hierarchy the node already implements |
| 3 | High | [Recovery from the seed](#3-recovery-from-the-seed) | whether two wallets find the same notes, the gap rule, what stays outside the seed |
| 4 | Medium | [Leader reward nonce](#4-leader-reward-nonce) | privacy of the derived nonce, the secret that keys it, uniqueness per block |
| 5 | Low | [Test vectors](#5-test-vectors) | reproduce them |

# Discussion

## Roles follow where the public key appears

On the private ledger a commitment hides the public key of its note, so a key that only ever sits inside commitments can hold any number of notes without linking them. One-time receive and change keys, the reason for the hierarchy of the closed RFC-452, no longer buy anything on chain, and the vouchers are gone with RFC-480.

Some keys still leave the wallet in the clear: the `note_pk`, `note_stake_pk` and `zk_id` of a service declaration, the `public_key` of a proof of work claim, and the key a program pays to, whose note has a nonce that is a public function of its value and key. Two Operations carrying the same key are linked, and an address key carried by an Operation ties that Operation to everyone who was given the address. The roles separate the two cases: address leaves never appear in an Operation, one-time leaves do, once each. Node leaves are apart because a node keeps their `nf_sk` online and they hold no note.

The split also decides recovery. A key an Operation carries is found by scanning the chain, which costs hashes. A key inside commitments is found only through the notes delivered to it.

## One address leaf by default

No Operation shows an address leaf, so no scan of the chain tells how many a wallet used. A gap rule over address leaves would make every recovery try `GAP_LIMIT` leaves, at one decapsulation per ciphertext and leaf, including for the wallets that use one. The standard instead makes leaf `0'` the default and puts the number of further leaves among the records of the wallet. A wallet that lost its records and used several leaves has to be told how many.

Further leaves have one use: two payers holding the same address know they pay the same wallet. The encryption key cannot be shared between leaves to save the decapsulations, because the two addresses would then share 1216 bytes.

## Address encoding

The full address is 1249 bytes, 2011 characters in Bech32m. BIP-173 designs the code for strings of at most 90 characters and says other designs are preferable above that. What still holds at any length: the code is linear, so an undetected error is a multiple of the generator polynomial, and a change of a single character never is. Any other error passes with a probability lower than 1 in $`10^9`$. The four-character guarantee holds for the key-only form, 65 characters.

Bech32m is kept because it gives the human-readable part, which keeps an address of one network from being used on another, because wallets and libraries already implement it, and because ZIP 316 already uses it without the length limit for its unified addresses. Two alternatives were left out:

- A truncated BLAKE2b digest inside the bytes gives the same probability for every error, with no guarantee on a single character. It could be added under Bech32m at four bytes per address if reviewers want both.
- A short address carrying a digest of `pk_enc`, the key being read from a directory, needs a directory that no specification defines.

The human-readable parts `logos` and `tlogos` are a proposal. No specification names the networks today.

## Leader reward nonce

[RFC-480](RFC-480-mantle-private-utxo-ledger.md) lets the leader choose the nonce freely and recommends a random one, kept with the note in the wallet, so that recovery from the seed does not find a reward note. It rejects two public nonces, the slot and the entropy contribution, because a public nonce with a public value lets anyone holding a public key test it against a commitment. It also keeps the reward key unconstrained, so that a leader can be paid under a key whose secret stays offline.

The nonce here keeps both properties and adds the recovery. It is keyed by a secret, so nobody else can test a key against a commitment. The secret is the staking secret key of the note that leads, which the Proof of Leadership takes, so the leader always holds it, the reward key can stay offline, and a program note, whose nullifier key is public, leads without exposing the nonce. A node given `staking_sk` for cold staking recognises the reward notes it created, and nobody else does.

The cost is in recovery: two hashes per block for each pair of a staking secret key and a reward public key, one pair for a wallet with the defaults.

RFC-480 states no reason against a nonce keyed by a secret. That is the point to confirm in review.

## What this RFC leaves open

- The `provider_id` of a declaration is an Ed25519 key and is not derived here. Roles `3'` and above are reserved.
- A note a program pays is found from the seed only as far as its key. Its value comes from the program or from the records, and a leaf given to a program is not seen by the gap scan.
- [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) calls `zk_id` a one-time random key and [Key Types and Generation](../key-types-and-generation.md) says the node generates it. A key derived at a fresh leaf is random to anyone without the seed, so neither text is wrong, and neither is changed here. A pointer from them to the node role would help an implementer.

## Compatibility

The node already implements the path under `kms/keys/src/hd`, with roles `0'` receive, `1'` change and `2'` voucher master, the last without an index level. The derivation of the leaves of `0'` and `1'` does not change, only their meaning: the `k`, `c` and `k_logos` of the three leaves RFC-452 published are the ones in the vectors here. Role `2'` gains an index level. On the private ledger branch nothing outside that crate derives a key from the hierarchy yet, so no key in use moves.

# Details

## 1. Address encoding

[Address Encoding](../wallet-technical-standard.md#address-encoding) is new. An address is a string, the Bech32m encoding of:

```python
key_only = b"\x00" + public_key             # 33 bytes
full     = b"\x01" + public_key + pk_enc    # 1249 bytes
```

`public_key` is the 32-byte little-endian field element and `pk_enc` the 1216-byte X-Wing encapsulation key. The human-readable part is `logos` on mainnet and `tlogos` elsewhere, and the 90-character limit of BIP-173 does not apply.

A sender MUST reject, and create no note from, a string with mixed case or a wrong checksum, the human-readable part of another network, an unknown `version`, a length other than the one of its `version`, padding of 5 bits or more or with a non-zero bit, a `public_key` not lower than the modulus, or a `pk_enc` whose ML-KEM-768 key fails the modulus check of FIPS 203.

## 2. Key hierarchy

[Key Hierarchy](../wallet-technical-standard.md#key-hierarchy) is new. Every key is derived at a leaf of

```text
m / 154' / account' / role' / index'
```

with all levels hardened, `154'` the slug of the standard, and no account `a + 1` while account `a` has held no note and has no used leaf.

| `role` | Name | Rule |
| --- | --- | --- |
| `0'` | Address | Leaf `0'` by default, for received notes, change and leader rewards. Further leaves MAY be used, in order, and their number belongs to the records. Its public key MUST NOT be in a field an Operation carries in the clear |
| `1'` | One-time | The next unused leaf for each key an Operation carries in the clear or a program is given: `note_pk`, the `public_key` of a proof of work claim, a program payout key. SHOULD NOT serve a second key. No note encryption key |
| `2'` | Node | The next unused leaf for the `zk_id` of each declaration, whose Proof of Quota takes the `nf_sk` of the leaf. Holds no note |
| `3'` and above | Reserved | MUST NOT be derived |

The roles are a wallet convention. The ledger does not tell them apart.

## 3. Recovery from the seed

[Recovery from the Seed](../wallet-technical-standard.md#recovery-from-the-seed) replaces the closing paragraph of Note Discovery and Recovery with a normative procedure, `GAP_LIMIT = 20`, per account:

1. One-time and node leaves: a leaf is used if its public key is the `note_pk`, the `note_stake_pk` or the `zk_id` of a declaration, or the `public_key` of a proof of work claim, anywhere in the chain history. The scan stops after `GAP_LIMIT` consecutive unused leaves. A wallet MUST NOT leave `GAP_LIMIT` consecutive leaves that no Operation carries.
2. Address leaves: leaf `0'` and the further leaves the records or the user count. Delivered notes by trial decryption of the ciphertexts still available. Leader rewards by `is_own_reward` over the headers, for each address public key and each staking secret key the wallet leads with.
3. Account `a + 1` only if account `a` has a used leaf, or holds or held a note.

A table states, per kind of note, what the seed and the chain find and what needs the records. Two statements are new with it: the change of a wallet is a delivered note like any other, so a wallet relying on a layer it reads again publishes the ciphertexts of its own change there; and a note under a staking key other than its public key needs that key from the records.

## 4. Leader reward nonce

[Leader Reward Notes](../wallet-technical-standard.md#leader-reward-notes):

```diff
-A wallet should therefore draw the nonce of each reward at random.
+A wallet SHOULD therefore derive the nonce from the staking secret key `staking_sk` of the
+note it leads with, the `nf_sk` of that note by default, and the slot of the block.
```

```python
def derive_reward_nonce(staking_sk: ZkSecretKey, slot: int) -> NoteNonce:
    return zkhash(
        FiniteField(b"LEADER_REWARD_NONCE_V1", byte_order="little", modulus=p),
        staking_sk,
        FiniteField(slot, byte_order="little", modulus=p),
    )  # Poseidon2 hash mode
```

`is_own_reward(header, staking_sk, public_key)` recomputes the commitment from the `reward_value` and the `slot` of a header, at two hashes per block and pair of keys. The leader holds `staking_sk` whatever key the reward is paid to. The Proof of Leadership does not constrain the nonce, so the circuit and the header are unchanged. A random nonce stays allowed, and a note under one is not found from the seed.

## 5. Test vectors

[Test Vectors](../wallet-technical-standard.md#test-vectors) is new: the master key of the BIP-39 mnemonic `abandon … about`, five leaves across the three roles and two accounts with `k`, `c`, `k_logos`, `nf_sk` and `public_key`, the encryption key and the three address strings of leaf `m/154'/0'/0'/0'`, two reward nonces with their commitments, one of them at a slot and a value above $`2^{32}`$, and the DSTs as field elements.

## Chores

- Tags of the standard gain `address` and `Bech32m`.

# Implementation

- [ ] `kms/keys/src/hd`: rename the roles to address, one-time and node, give the node role an index level, remove the voucher master.
- [ ] Derive `nf_sk` and, for address leaves, `sk_enc` and `pk_enc` from a leaf.
- [ ] Encode and decode addresses with every rejection of the standard; the wallet API takes and returns address strings.
- [ ] Wallet service: take its keys from the hierarchy, a one-time leaf per declaration and per proof of work claim, a node leaf per `zk_id`, and persist the next index of each role and the number of address leaves.
- [ ] Wallet: derive the nonce of a new leader reward note from the staking secret key of the winning note and the slot, inside the KMS.
- [ ] Recovery from the seed: the gap scan over declarations and claims, `is_own_reward` over the headers, trial decryption over the available ciphertexts.
- [ ] Add the test vectors of the standard as tests.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.4.0 |
