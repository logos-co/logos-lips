# WALLET-TECHNICAL-STANDARD

| Field | Value |
| --- | --- |
| Name | Wallet Technical Standard |
| Slug | 154 |
| Status | raw |
| Category | Standards Track |
| Tags | wallet, key derivation, HD wallet, mnemonic, BIP-32, BIP-39, Poseidon2 |
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
| 1.2.0 | STARK-field key derivation from a one-way image of the same leaf as the `ZkSecretKey`; both keys in every payment request; a note is the wallet's only when both keys are | 2026-09-07 |

# Introduction

The main motivation behind this spec is avoiding being locked into a wallet software. By specifying the algorithms used to derive keys, we allow users to easily migrate from one implementation to the other.

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

## STARK-Field Key Derivation

Every key that owns notes exists twice, in the two fields the protocol proves over: the `ZkSecretKey` of the previous section, whose public key is the `public_key` of a [Mantle](bedrock-v1.1-mantle-specification.md#notes) `Note`, and a STARK-field secret key whose public key is the note's `stark_public_key`. Both come from the same leaf, so a leaf is found once and owns its notes under both keys, but they share no input bytes: the STARK-field key is derived from a one-way image of the leaf.

Let $`k_i`$ be the 32-byte leaf. Its STARK-field seed is $`s_i = Blake2b\_256("Logos\_StarkSeed", k_i)`$ (the personalization string is 15 bytes). The STARK-field hash `starkhash` ([Common Cryptographic Components](common-cryptographic-components.md#rescue-prime-optimized-stark-field-hash-function)) operates on Goldilocks field elements, so $`s_i`$ is split into four 8-byte limbs: let $`s_i = b_0 || b_1 || b_2 || b_3`$, $`n_j`$ the value of $`b_j`$ as a little-endian unsigned integer and $`g_j := n_j \bmod q`$ with $`q = 2^{64} - 2^{32} + 1`$. A limb is reduced only when $`n_j \ge q`$, which happens with probability $`2^{-32}`$ per limb; the bias is irrelevant since the limbs only seed a hash.

```python
sk_stark         = starkhash(*dst_elements(b"STARK_WALLET_SK_V1"), g_0, g_1, g_2, g_3)  # four Goldilocks elements
stark_public_key = starkhash(*dst_elements(b"STARK_KDF_V1"), *sk_stark)                # four Goldilocks elements, 32 bytes
```

- $`sk_{stark}`$ is the STARK-field secret key of the leaf and MUST be protected exactly as the `ZkSecretKey`: it is the secret that proves ownership of the leaf's notes under a STARK-field proof system. Exposure of the leaf exposes both keys; exposure of one key exposes neither the leaf nor the other key, since both derivations are one-way and the STARK-field seed is itself a one-way image of the leaf.
- `stark_public_key` is the field of the same name in every note the leaf owns and in the `LEADER_CLAIM` payload; `STARK_KDF_V1` plays for the STARK-field key the role `KDF` plays for the BN254 key. The `stark_zk_id` of a service declaration is derived the same way from the leaf that holds the `zk_id`.
- Recovery needs nothing new: scanning by index derives both keys of a leaf together, and a wallet never stores a mapping between them.

**Test vector.** For the leaf $`k_i`$ = `0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20` (the bytes `0x01` to `0x20`):

| Step | Value |
| --- | --- |
| $`s_i`$ | `0xab7ef4bbc69f4dc568262a33994f780ac17d75ffcd6b687ef3b3b205b00cb9cc` |
| $`g_0, g_1, g_2, g_3`$ | [14217195274584227499, 754440456991549032, 9108648778855185857, 14751836004578145267] (no limb reduced) |
| $`sk_{stark}`$ | `0x9aa42c410f141e5e0d7b250152304b4c6f6f023c4cdd81822ce7ddc9d68d5f76` |
| `stark_public_key` | `0xe1e74415b44f65781efa99656fe5df93916b6072ce87e2144eb79bbe81549364` |

**Both keys or neither.** Nothing on the ledger proves that the two keys of a note belong to the same party; the ledger commits to the pair, and the wallet is the only place the pair is checked. Therefore:

- A payment request MUST carry the `public_key` and the `stark_public_key` of the same leaf; a sender MUST copy both into the output note.
- A wallet MUST treat a note as received, spendable and part of its balance only if both keys are those of one of its leaves.
- A note whose `public_key` is the wallet's but whose `stark_public_key` is not is spendable with the BN254 key but not owned under the STARK-field key. A wallet MUST NOT count it as received and SHOULD warn the user, who may still spend it.

This wallet-side check is what binds the two keys, and it is what lets the second key cost one derivation instead of one proof.

# References

[ZIP 32: Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032)

[CIP-0003](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0003/README.md)

[slip-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

[bip-0039](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

[bip-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
