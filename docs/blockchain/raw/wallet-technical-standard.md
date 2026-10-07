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
| 1.2.0 | Added the note tracking a wallet keeps to spend its notes and to participate in the leadership lottery | 2026-10-07 |

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

$`k_{\text{logos}}`$ is the `ZkSecretKey` used on the network. The corresponding public key is derived exactly as the [Mantle specification](bedrock-v1.1-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) prescribes, with Poseidon2 in compression mode and the `KDF` DST:

```python
public_key = zkhash(FiniteField(b"KDF", byte_order="little", modulus=p), k_logos)  # compression mode
```

This wallet-side step is not part of any circuit, so the DST costs nothing in proving time while preventing $`k_{\text{logos}}`$ from colliding with any other Poseidon2 output computed over the same field elements. Only the `KDF` derivation of the public key is evaluated inside proofs, and it hashes a single field element thanks to this compression.

  **Why not use Poseidon2 for the full derivation?** While Poseidon2 is optimized for ZK circuits, its long-term stability and parameterization are still evolving. General-purpose hash functions like Blake2b offer a more stable and audited base layer. By introducing Poseidon2 only at the last compression step we isolate ZK-dependencies from the rest of the key derivation path. This ensures the wallet hierarchy remains valid even if Poseidon2 parameters are updated.

## Note Tracking

The [Mantle Ledger](bedrock-v1.1-mantle-specification.md#mantle-ledger) only holds note commitments and nullifiers. To spend its notes and to participate in the leadership lottery, a wallet keeps the data its proofs need for every note it owns.

To spend a note with a [ZkTransfer](bedrock-v1.1-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer), the wallet keeps:

- The note `(value, nonce, public_key)` and its commitment `cm = derive_note_cm(note)`.
- The Merkle path of `cm` to the root of the MMR peak holding it. With the other peaks of the MMR, which are public and served by any node, this path proves `cm` in the MMR root. A ZkTransfer is proven against the commitment root of one of the last 1024 blocks, so the wallet keeps the path up to date with the commitments appended to the MMR.
- The nullifier `nf = derive_note_nf(cm, sk)`. The note is spent once `nf` is in the nullifier set, whichever wallet instance spent it.

To prove its leadership with a shielded note ([Proof of Leadership](cryptarchia-proof-of-leadership.md#eligible-sets)), the wallet also keeps:

- The Merkle path of `cm` to the shielded eligible set root of the epoch snapshot, fixed for the epoch.
- The leaf of the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree) holding the greatest nullifier lower than `nf`, and its Merkle path to the latest root. This leaf and its path change whenever a nullifier is inserted, so the wallet updates them before each proof.

For a transparent note (a service note or a channel note under one of its keys), the wallet keeps the Merkle paths of `cm` to the transparent eligible set roots of the epoch snapshot and of the latest state instead.

Requesting these paths from a third party reveals which commitments and nullifiers the wallet owns. A wallet that follows every commitment appended to the MMR and every nullifier inserted in the IMT computes its paths locally.

A peak of the MMR is a perfect Merkle tree, which never changes once built: appending a commitment only adds a peak of height 0, and merges the last two peaks while they have the same height. The path of `cm` inside its peak therefore only grows, by one node each time its peak is merged, which happens at most 32 times. The wallet keeps a copy of the peaks, with their heights given by the binary decomposition of the number of commitments, and updates the paths of its notes while appending the commitments of each block:

```python
class OwnedNote:
    note: Note
    cm: NoteCm
    nf: NoteNf
    peak: int                   # index of the peak holding cm
    path: list[zkhash]          # Merkle path of cm to the root of its peak
    selectors: list[bool]       # whether each node of the path is left (0) or right (1)

def append_commitment(peaks: list[(zkhash, int)], notes: list[OwnedNote], cm: NoteCm):
    # peaks holds the (root, height) of every peak, from left to right
    peaks.append((cm, 0))
    while len(peaks) > 1 and peaks[-1][1] == peaks[-2][1]:
        (left, height), (right, _) = peaks[-2], peaks[-1]
        for note in notes:
            if note.peak == len(peaks) - 2:
                # cm is in the left peak, its new complementary node is the right peak
                note.path.append(right)
                note.selectors.append(1)
            elif note.peak == len(peaks) - 1:
                # cm is in the right peak, its new complementary node is the left peak
                note.path.append(left)
                note.selectors.append(0)
                note.peak -= 1
        peaks[-2:] = [(zkhash(left, right), height + 1)]
```

A note the wallet owns joins `notes` with `peak = len(peaks) - 1` and an empty path right after `peaks.append((cm, 0))`, before the merges of its own append. Only the notes whose peak is merged are updated, so following a block costs one hash per merge. The path of a note to the shielded eligible set root of the epoch snapshot is the path it holds at the snapshot, completed with the peaks of the snapshot.

Inserting a nullifier changes exactly two leaves of the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree): the appended leaf and the leaf of the greatest nullifier lower than the inserted one. Every insertion is public, so a wallet fetching the leaves and Merkle paths of these two positions, as they stand after each insertion, reveals nothing about the notes it owns. From them, it updates the low leaf of each of its shielded notes and its path with at most 32 hashes per changed leaf:

```python
class TrackedLowLeaf:
    nf: NoteNf                  # nullifier of the owned note
    index: int                  # index of the IMT leaf holding the greatest nullifier lower than nf
    leaf: NullifierLeaf
    path: list[zkhash]          # Merkle path of the leaf to the IMT root (len = 32)

def branch_nodes(leaf_hash: zkhash, index: int, path: list[zkhash]) -> list[zkhash]:
    # nodes of the branch of index, from the leaf up to the root
    nodes = [leaf_hash]
    for height in range(32):
        if (index >> height) & 1:
            nodes.append(zkhash(path[height], nodes[-1]))
        else:
            nodes.append(zkhash(nodes[-1], path[height]))
    return nodes

def update_path(tracked: TrackedLowLeaf, index: int, leaf: NullifierLeaf, path: list[zkhash]):
    # replace the nodes of tracked.path that lie on the branch of the changed leaf
    nodes = branch_nodes(nullifier_leaf_hash(leaf), index, path)
    for height in range(32):
        if (index >> height) == ((tracked.index >> height) ^ 1):
            tracked.path[height] = nodes[height]

def on_nullifier_inserted(tracked: TrackedLowLeaf, inserted_nf: NoteNf,
                          low_index: int, low_leaf: NullifierLeaf, low_path: list[zkhash],
                          new_index: int, new_leaf: NullifierLeaf, new_path: list[zkhash]):
    if low_index == tracked.index and inserted_nf < tracked.nf:
        # the inserted nullifier is now the greatest one lower than tracked.nf
        tracked.index, tracked.leaf, tracked.path = new_index, new_leaf, new_path
    elif low_index == tracked.index:
        # only the pointer of the tracked leaf moved to the inserted nullifier
        tracked.leaf, tracked.path = low_leaf, low_path
    else:
        update_path(tracked, low_index, low_leaf, low_path)
        update_path(tracked, new_index, new_leaf, new_path)
```

# References

[ZIP 32: Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032)

[CIP-0003](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0003/README.md)

[slip-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

[bip-0039](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

[bip-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
