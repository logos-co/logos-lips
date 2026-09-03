# WALLET-TECHNICAL-STANDARD

| Field | Value |
| --- | --- |
| Name | Wallet Technical Standard |
| Slug | 154 |
| Status | raw |
| Category | Standards Track |
| Tags | wallet, key derivation, HD wallet, mnemonic, BIP-32, BIP-39, Poseidon2, one-time keys, reward voucher, recovery |
| Editor | Giacomo Pasini <giacomo@logos.co> |
| Contributors | Thomas Lavaur <thomas@logos.co>, Mehmet Gonen <mehmet@logos.co>, Daniel Sanchez Quiros <daniel@logos.co>, Alvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/wallet-technical-standard.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/wallet-technical-standard.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-02-13** — [`b7813dc`](https://github.com/logos-co/logos-lips/blob/b7813dce5a7413f7d7c430d9f2c2bbee367fbeef/docs/blockchain/raw/wallet-technical-standard.md) — feat: add Logos Blockchain Wallet Technical Standard specification (#292)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-02-05 |
| 1.0.1 | Updated project references to Logos Blockchain | 2026-04-17 |
| 1.1.0 | Fixed the master key generation personalization string to a valid 16-byte value; aligned the public key derivation with the [Mantle specification](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature) (`KDF` DST, compression mode, applied to the Logos key); specified the final Poseidon2 step as hash mode with the `WALLET_ZK_SK_V1` DST; clarified that extended public keys derive no children | 2026-09-03 |
| 1.2.0 | Hierarchical key management for one-time keys: fixed the key hierarchy `m / 154' / account' / role' / index'` with the receive, change and voucher roles; specified one-time note keys and the derivation of reward voucher secrets from a per-account voucher master; specified the recovery procedure (history scan, gap limit); stated the freshness requirements for keys the wallet does not derive; added test vectors | 2026-09-03 |

# Introduction

The main motivation behind this spec is avoiding being locked into a wallet software. By specifying the algorithms used to derive keys, we allow users to easily migrate from one implementation to the other.

The second motivation is to support one-time keys. The [Mantle](bedrock-v1.1-mantle-specification.md) ledger is transparent: every `Note` carries its owner's `ZkPublicKey` in clear and a `TRANSFER` reveals the public keys of the notes it consumes, so a public key reused across notes links every payment a user ever received and every spend they ever made. Likewise every proposed block commits to a fresh [reward voucher](bedrock-anonymous-leaders-reward.md) whose secret is the only way to claim the reward. Both call for a hierarchy that produces an unbounded supply of keys deterministically from one seed, so that fresh keys cost nothing and are all recoverable from the mnemonic.

# Overview

This document mostly follows pre-existing standards in Bitcoin and adapts it to Logos’ needs when necessary. This is also the choice of other Bitcoin-inspired projects like Cardano or Zcash. For this reason, this document will not go over the entire spec itself, and just highlight differences with existing standards.

## Mnemonic codes for key generation

Mnemonic codes are far easier to interact with as humans than raw binary or hex strings and are the standard for wallets. In this regard we can reuse [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) entirely, as it’s just operations on strings and bytes.

## Hierarchical Deterministic wallet

Hierarchical Deterministic (HD) wallets are nowadays the standard. Using a single source of entropy (usually obtained through the process above), it’s possible to generate many different addresses and share all or part of it.

The industry standard is [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki). However, we can’t use it as it is, as we use different keys and cryptographic components. In addition, some of the BIP32 features are only possible thanks to homomorphic properties of ECC, which we don’t have in the Logos Blockchain since we use hash-based sk/pk.

![Diagram](wallet-technical-standard/assets/216261aa-09df-808f-bbc0-f402be5e66f8.png)

BIP-32 specifies two kinds of child keys:

- Normal: you can derive a child public key from the parent public key
- Hardened: you need the parent private key to derive a child private and public key

Unfortunately, ‘normal’ children are possible thanks to specific properties of the keys used in Bitcoin that we don’t have in the Logos Blockchain (namely, homomorphism).

To maintain compatibility, we will still use the same structure but non-hardened children will not be available.

  **Extended Keys (from BIP32)**

  In what follows, we will define a function that derives a number of child keys from a parent key. In order to prevent these from depending solely on the key itself, we extend both private and public keys first with an extra 256 bits of entropy. This extension, called the chain code, is identical for corresponding private and public keys, and consists of 32 bytes.

  We represent an extended private key as $`(k, c)`$, with $`k`$ the normal private key, and $`c`$ the chain code. An extended public key is represented as $`(K, c)`$, with $`K`$ the public key derived from $`k`$ as described in [ZK-Compatible Secret Key Derivation in the Logos Blockchain](#zk-compatible-secret-key-derivation-in-the-logos-blockchain) and $`c`$ the chain code. Since only hardened children exist, an extended public key cannot derive any child key: it is an identifier and export format, not a derivation input.

  Each extended key has $`2^{31}`$ hardened children keys. Each of these child key has an index. The hardened child keys use indices from $`2^{31}`$ through $`2^{32} -1`$.

# Details

The main novelty with respect to the aforementioned protocols is one last additional step before obtaining a secret key that can be used in the Logos Blockchain network, described in [ZK-Compatible Secret Key Derivation in the Logos Blockchain](#zk-compatible-secret-key-derivation-in-the-logos-blockchain).

For the remaining procedures, we only highlight the differences instead of going over all the details again as they’re already covered extensively elsewhere.

## **Notation:**

- $`(k_{par}, c_{par})`$: the parent extended key, composed of the private key $`k_{par}`$ and the chain code $`c_{par}`$.
- $`ser_{32}(i)`$: serialize a 32-bit unsigned integer i as a 4-byte sequence, most significant byte first.
- $`Blake2b\_512(p, x)`$: refers to unkeyed BLAKE2b-512 in sequential mode, with an output digest length of 64 bytes, 16-byte personalization string *p*, and input *x.*
- $`PRF^{expand}(x, y): Blake2b\_512("Logos\_ExpandSeed", x || y)`$, a pseudo-random function.

## Child Key Derivation

$`CDKpriv((k_{par}, c_{par}), i) \rightarrow (k_i, c_i):`$

  - Check whether $`i \geq 2^{31}`$ (whether the child is a hardened key).
    - If so (hardened child): let $`I = PRF^{expand}(c_{par}, 0x00 ||k_{par} || ser_{32}(i))`$.
    - If not (normal child): failure.

  - Split $`I`$ into two 32-byte sequences, $`I_L, I_R`$.
  - The returned child key $`k_i`$ is $`I_L`$.
  - The returned chain code $`c_i`$ is $`I_R`$.

## Master Key Generation

- Generate a seed byte sequence $`S`$ of a chosen length (e.g. with BIP0039)
- Calculate $`I = Blake2b\_512("Logos\_MasterKGen", S)`$ (the personalization string is exactly 16 bytes, the maximum BLAKE2b allows)
- Split $`I`$ into two 32-byte sequences, $`I_L`$ and $`I_R`$.
- Use $`I_L`$ as master secret key, and $`I_R`$ as master chain code.

## Key Hierarchy

All keys used by a wallet are derived along the following path, where every level is a hardened child (the notation $`i'`$ stands for the index $`i + 2^{31}`$):

```text
m / 154' / account' / role' / index'
```

- `154'` is the purpose, fixed to the slug of this specification, following the BIP-43 convention. It never changes, even if the specification is renumbered.
- `account'` separates independent sets of keys for the same user (e.g. personal and business), numbered from 0. Wallets MUST support account 0 and MAY expose more.
- `role'` selects what the leaves under it are used for, according to the table below.
- `index'` enumerates the leaves of a role, from 0, without gaps.

| `role` | Name | Leaf usage | One-time |
| --- | --- | --- | --- |
| `0'` | Receive | one leaf, hence one set of note keys, per received note, see [One-Time Note Keys](#one-time-note-keys) | yes |
| `1'` | Change | one leaf, hence one set of note keys, per change note, see [One-Time Note Keys](#one-time-note-keys) | yes |
| `2'` | Voucher | the voucher master of the account, see [Voucher Secret Derivation](#voucher-secret-derivation); this role has no `index'` level | n/a |
| `3'` – `(2^{31}-1)'` | Reserved | reserved for future roles (e.g. node identity keys); wallets MUST NOT derive keys under them | |

Every leaf is a 32-byte extended private key $`(k, c)`$ produced by `CDKpriv`. How the 32 bytes of $`k`$ become network keys is specified by the derivation sections below, starting with [ZK-Compatible Secret Key Derivation in the Logos Blockchain](#zk-compatible-secret-key-derivation-in-the-logos-blockchain); every key the protocol derives from a leaf belongs to that leaf. The leaf, not any single key, is the unit of use and of recovery in this specification.

  **Why no `coin_type` level?** BIP-44 inserts a `coin_type'` level so that wallets sharing one BIP-32 tree across several chains produce unrelated keys per chain. This specification does not share a tree with any other chain: `CDKpriv` and the master key generation are already personalized with `Logos_ExpandSeed` and `Logos_MasterKGen`, so a Logos key never coincides with a key another chain derives from the same mnemonic and path, whatever `coin_type` that chain uses. A `coin_type` level would add nothing but a registration dependency.

## ZK-Compatible Secret Key Derivation in the Logos Blockchain

Since we make extensive use of ZK proofs, we need our secret → public derivation to be efficient. For this purpose, we use a ZK-optimized hash function: Poseidon2.

However, Poseidon2 operates on field elements rather than raw bytes, so we cannot simply input $`k_i`$ as specified above. Instead, we must encode these bytes into field elements. Using the parameters described in [**Use in the Logos Blockchain:**](common-cryptographic-components.md), we need two field elements to encode 32 bytes (the size of $`k_i`$). This creates inefficiency because although a single field element provides adequate security, we must use twice as many, increasing computation costs to accommodate the entire key.

To reduce this additional cost inside the proof, we apply one final hash function that compresses these two field elements into a single one, which becomes the actual key used in the Logos Blockchain network:

Let $`k_L, k_R`$ be 16-byte sequences such that $`k_i = k_L || k_R`$ and $`n_L, n_R`$ be their values when interpreted as little-endian unsigned integers. Let $`e_L, e_R`$ be scalar field elements in BN254 such that $`e_L := n_L \in \mathbb F_r, e_R := n_R \in \mathbb F_r`$. The Logos key is obtained with Poseidon2 in hash mode, domain separated from every other use of Poseidon2 in the protocol:

```python
k_logos = zkhash(
    FiniteField(b"WALLET_ZK_SK_V1", byte_order="little", modulus=p),
    e_L,
    e_R,
)  # Poseidon2 hash mode, a single field element
```

$`k_{\text{logos}}`$ is the `ZkSecretKey` used on the network. The corresponding public key is derived exactly as the [Mantle specification](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature) prescribes, with Poseidon2 in compression mode and the `KDF` DST:

```python
public_key = zkhash(FiniteField(b"KDF", byte_order="little", modulus=p), k_logos)  # compression mode
```

This wallet-side step is not part of any circuit, so the DST costs nothing in proving time while preventing $`k_{\text{logos}}`$ from colliding with any other Poseidon2 output computed over the same field elements. Only the `KDF` derivation of the public key is evaluated inside proofs, and it hashes a single field element thanks to this compression.

  **Why not use Poseidon2 for the full derivation?** While Poseidon2 is optimized for ZK circuits, its long-term stability and parameterization are still evolving. General-purpose hash functions like Blake2b offer a more stable and audited base layer. By introducing Poseidon2 only at the last compression step we isolate ZK-dependencies from the rest of the key derivation path. This ensures the wallet hierarchy remains valid even if Poseidon2 parameters are updated.

## One-Time Note Keys

A note leaf is a leaf under the receive (`0'`) or change (`1'`) role. Its keys are the note keys: the `ZkSecretKey` $`k_{\text{logos}}`$, whose `ZkPublicKey` is the `public_key` field of the notes it owns, and every further key the protocol derives from the same leaf. A payment request carries every public key of one leaf, and a note is owned by the leaf whose keys it carries.

- A wallet MUST use a fresh receive leaf, i.e. the next unused `index'` under `0'`, for every payment request it hands out. It MAY reuse a leaf whose public keys have been published but which has not yet received a note.
- A wallet MUST use a fresh change leaf, the next unused `index'` under `1'`, for every change output it creates. It MUST NOT send change back to the keys of a consumed input by default.
- A wallet MAY spend notes owned by different leaves in one `TRANSFER`: the [ZkSignature](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature) proves up to 32 secret keys in a single proof, so one-time keys do not add proofs to a transaction with at most 32 inputs.
- One-time keys change nothing for consensus: the Proof of Leadership eligibility (note ageing) is attached to the `NoteId`, not to the public key, and the Proof of Leadership and Proof of Quota circuits use the note secret key only as a secret input.

  **What one-time keys do and do not hide.** A fresh leaf per note prevents an observer from linking the notes a user receives over time and from recognising the same recipient across payments. It does not hide the transaction graph: a `TRANSFER` still shows which notes are consumed together and which notes it creates, and every `Note` remains public, as the Mantle specification states. Wallets MUST NOT present one-time keys as transaction privacy.

## Voucher Secret Derivation

Each block a leader proposes commits to a reward voucher whose secret is required to claim the reward with a `LEADER_CLAIM` Operation. A voucher secret that is lost cannot be recovered from the chain, so a wallet derives voucher secrets deterministically from the seed.

The voucher leaf of an account is `m / 154' / account' / 2'`; its keys are derived exactly as a note leaf's. The voucher master $`vm`$ is the `ZkSecretKey` of the voucher leaf, and if the protocol derives keys in more than one field from a leaf, the voucher leaf yields one voucher master per field in the same way. The $`i`$-th voucher secret of the account is:

```python
def voucher_secret(vm: ZkSecretKey, i: int) -> Fr:  # i is a uint64
    return zkhash(
        FiniteField(b"VOUCHER_SECRET_V1", byte_order="little", modulus=p),
        vm,
        FiniteField(i, byte_order="little", modulus=p),
    )  # Poseidon2 hash mode
```

- A wallet MUST keep a single counter `next_voucher_index` per account, whatever field the voucher is issued in, use `voucher_secret(vm, next_voucher_index)` for the next block it proposes and increment the counter before the block is released. A voucher secret MUST never be used for two blocks.
- The voucher commitment `voucher_cm` and the nullifier `voucher_nf` are computed from the voucher secret exactly as specified in the [Anonymous Leaders Reward Protocol](bedrock-anonymous-leaders-reward.md); this specification only fixes where the secret comes from and does not change their derivation, the Proof of Claim circuit, or any validation rule.
- The voucher master(s) MAY be handed to a block-producing node without the rest of the hierarchy. Their compromise exposes the account's unclaimed rewards and nothing else.

  **Why a master plus a Poseidon2 counter rather than one leaf per voucher?** A node produces a voucher for every block it proposes, and keeping the derivation inside Poseidon2 lets a key management system hold a single field element for the whole role and stay free of the byte-oriented `CDKpriv` machinery; the counter is also not bounded to $`2^{31}`$ indices. The DST separates voucher secrets from every other Poseidon2 use, in particular from `KDF` and from note keys.

## Wallet Recovery

Since only hardened children exist, a wallet cannot enumerate its keys from public material; it recovers them by deriving candidate keys from the seed and looking them up on chain. Two wallets recovering from the same mnemonic MUST find the same funds, so the procedure is normative.

Let `GAP_LIMIT = 20`.

1. **Note keys.** For each of the roles `0'` and `1'` of an account, derive the leaves `index' = 0', 1', 2', …` and their public keys. A leaf is *used* if any of its public keys appears in any `Note` created at any point in the chain history, spent or not. Stop after `GAP_LIMIT` consecutive unused leaves; every used leaf found is part of the wallet, and `next_index` of the role is one past the last used leaf.
    - The lookup MUST cover the chain history and not only the current set of unspent notes: a leaf whose notes were all spent is used, and skipping it would misplace the gap and hide the funds of later leaves.
    - A note that carries one public key of the leaf but not its others still marks the leaf as used: the leaf was published, and skipping it would misplace the gap. Whether the wallet counts such a note as received is decided by the acceptance rules of the key derivation sections, not by recovery.
    - Wallets MAY scan beyond `GAP_LIMIT` on user request but MUST NOT stop earlier.
2. **Vouchers.** Derive `voucher_secret(vm, i)` and its `voucher_cm` for `i = 0, 1, 2, …`. A voucher is *issued* if its commitment is in the voucher commitment set (an append-only Merkle Mountain Range, so an issued voucher is always found) and *claimed* if its nullifier is in the voucher nullifier set. Stop after `GAP_LIMIT` consecutive unissued indices; `next_voucher_index` is one past the last issued index. Vouchers of the current epoch are not yet in the set, so a recovering wallet that is also producing blocks MUST also account for the vouchers it issued since the last epoch boundary. If the protocol has migrated to a new proof system and retains a legacy voucher set, the scan MUST cover both the legacy set, using the voucher master and commitment derivation in force when those vouchers were issued, and the current set, with the single counter running across both.
3. **Accounts.** Recover account 0; recover account `a + 1` only if account `a` has at least one used leaf or issued voucher.

## Keys This Specification Does Not Derive

Two further kinds of one-time keys exist in the protocol. Neither carries value, so neither needs recovery, and they are outside this hierarchy:

- The one-time Ed25519 key $`P_\text{LEAD}`$ that signs a block proposal, bound to the [Proof of Leadership](cryptarchia-proof-of-leadership.md#linking-the-proof-of-leadership-to-a-block). It MUST be generated fresh for every proposal, since reusing it would link the proposals of a leader, and MAY be drawn at random.
- The ephemeral signing and encryption keys of the Blend protocol, one per encapsulation, as required by [Key Types and Generation](key-types-and-generation.md); their number is bounded by the Proof of Quota.

The long-lived node identity keys of [Key Types and Generation](key-types-and-generation.md) (`zk_id`, `provider_id`) are also not covered; the reserved roles leave room to add them.

## Test Vectors

The vectors below use the BIP-39 mnemonic `abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about` with an empty passphrase (64-byte seed). Byte strings are written in hex. Field elements are written as their 32-byte little-endian encoding as defined in [Common Cryptographic Components](common-cryptographic-components.md), which is also the wire form of a `ZkPublicKey`. Poseidon2 values were produced with the `logos-blockchain-poseidon2` crate of the reference implementation.

### Master Key

| Quantity | Value |
| --- | --- |
| seed `S` | 0x5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4 |
| master secret key `I_L` | 0x72a5d51d61b1ea9f6ec4bb2287aa26d229443726788bc38440012c44eda58ae8 |
| master chain code `I_R` | 0xc67234c2aebc79aaaa2f79caa66325b86932079331a60f36004658d20d06c3e8 |

### Note Keys

| Path | `k` (leaf) | `c` (leaf) | `k_logos` | `public_key` |
| --- | --- | --- | --- | --- |
| `m/154'/0'/0'/0'` | 0xdfd5e34a2ffad38e96540489551e0ce5ef10792bd660cf413a9f6dd28a77c016 | 0x672eeedfdc70109e33ca57b79e1b6fa62f279a162fa203d1ba0163cd70b3d072 | 0x5e09bf4ce6b3f42970104a6f5940104407f98da0eb946104c13fb4f94c011f16 | 0xce562a751eed5181fc6679bb8b9d87a219591cd91e1c1daa947e7880231de62d |
| `m/154'/0'/0'/1'` | 0x0baeddd9dc5d60ed0dc64597d2b0f49d486e5448cd8ac94fe2515c80fbf5d67c | 0x802cdbc751687844cf324e883fa024d80e29d35b4de5d51f151afa5d3c6d2232 | 0x070b4df159a3bc13e9663f39f5e71afda9b68626c49e48c85a16b8ec55ef162f | 0x937888953090c19753e32497a426d37a97aef226a675fbe2bc6d8d24d2ab082f |
| `m/154'/0'/1'/0'` | 0x4f3acc80a0fecc95bf8d8cd16435803c5cee29783a6d2809e9fc10840dadb57c | 0xa85b8265092527323173c6ab624e29faa848dc5cda409a7fbe1d4ec80e8c4130 | 0x0e00954c65e6495a92cebf12b058232e770bcf933dd1cfd5d28071f367639a1f | 0x7445f28b95f7f12f6b7e5b55ccc82eb8c41bfdd9dc83d6f730a9e03b2f288c1f |

### Vouchers

| Quantity | Value |
| --- | --- |
| `m/154'/0'/2'` leaf `k` | 0xcbbb7fde40e8971d22a7557c890b2d9f00e765bb2475a2588aaba675e6754403 |
| `m/154'/0'/2'` leaf `c` | 0x775509a7384f889155c37948b8e2677b75975a0f20bd37b0708125d23933aa5d |
| voucher master `vm` | 0x0962b39836dcac5d984c4c771b78b0ad5572c3cdd14d0f75c9c367f365b0b908 |
| `voucher_secret(vm, 0)` | 0x4b92e4cf4caa3731e0b0dd9005620cb73abc7a56220db0b81a25e9e06671ab00 |
| `voucher_cm`, i = 0 | 0x4d1a9c149153079046d8fdb372b2e5c8dfa45ed0746b35697a9e39d535dea313 |
| `voucher_nf`, i = 0 | 0xd2efbfe0faa9e58e389caaf71c02e8a9026b2cabaaa187688a10811b4dc32f0f |
| `voucher_secret(vm, 1)` | 0xe185e33265ed476e3b30ee8b5f16c85f0de065efd42cb39fa77d193e4ccf8f1d |
| `voucher_cm`, i = 1 | 0x83d0e075613d431b9660fcd93ad830fe3a8a1f4dcdab531abd962decebaa251c |
| `voucher_nf`, i = 1 | 0xaa2b01af32d9c638318919d9b368d8a6cbd58038fda88fdf80fff3016a6f5104 |

### Domain Separation Tags as Field Elements

| DST | `FiniteField(DST, byte_order="little", modulus=p)` |
| --- | --- |
| `WALLET_ZK_SK_V1` | 0x57414c4c45545f5a4b5f534b5f56310000000000000000000000000000000000 |
| `KDF` | 0x4b44460000000000000000000000000000000000000000000000000000000000 |
| `VOUCHER_SECRET_V1` | 0x564f55434845525f5345435245545f5631000000000000000000000000000000 |
| `REWARD_VOUCHER` | 0x5245574152445f564f5543484552000000000000000000000000000000000000 |
| `VOUCHER_NF` | 0x564f55434845525f4e4600000000000000000000000000000000000000000000 |

# References

[ZIP 32: Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032)

[CIP-0003](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0003/README.md)

[slip-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

[bip-0039](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

[bip-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
