# WALLET-TECHNICAL-STANDARD

| Field | Value |
| --- | --- |
| Name | Wallet Technical Standard |
| Slug | 154 |
| Status | raw |
| Category | Standards Track |
| Tags | wallet, key derivation, HD wallet, mnemonic, address, BIP-32, BIP-39, Bech32m, Poseidon2 |
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
| 1.2.0 | Added the note tracking a wallet keeps to spend its notes and to participate in the leadership lottery, over the note sets of depth 40, the root a wallet proves against, a fixed number of blocks below its tip, and the leader reward notes, which it keeps with their private nonce, recovery from the seed alone not finding them | 2026-10-07 |
| 1.2.1 | The public key derives from a nullifier key derived from the spending secret key, and a note has a staking key, the wallet using the nullifier key as staking secret key and the public key of the recipient of a payment by default, and keeping the keys of a service declaration cold | 2026-11-06 |
| 1.3.0 | Added the note encryption key derived from the ZK secret key, the address a sender needs, and the discovery of notes by trial decryption of the note ciphertexts delivered off chain, with what the recovery from the seed covers. A delivered note has the public key of its recipient as staking key unless the recipient asked for another, and a sender keeps the notes it creates | 2026-11-02 |
| 1.4.0 | Added the key hierarchy `m / 154' / account' / role' / index'`, with the address, one-time and node roles; the encoding of an address, with its checksum; the nonce of a leader reward note derived from the staking secret key of the leading note and the slot, so that recovery from the seed finds the note; the recovery from the seed, with what it finds for each kind of note; the delivery inscription, by which a sender commits to its delivery messages in an `INSCRIBE` Operation of its Mantle Transaction; and test vectors | 2026-11-17 |

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

## Key Hierarchy

Every key of a wallet is derived along the following path, where each level is a hardened child (the notation $`i'`$ stands for the index $`i + 2^{31}`$):

```text
m / 154' / account' / role' / index'
```

- `154'` is the purpose, fixed to the slug of this specification, following the BIP-43 convention. It never changes, even if the specification is renumbered.
- `account'` separates independent sets of keys of the same user, numbered from 0. Wallets MUST support account 0 and MAY expose more. A wallet MUST NOT create account `a + 1` while account `a` has held no note and has no used leaf, since recovery stops at the first such account ([Recovery from the Seed](#recovery-from-the-seed)).
- `role'` selects what the leaves under it are used for, according to the table below.
- `index'` enumerates the leaves of a role, from 0, without gaps.

| `role` | Name | Keys of a leaf | Where its public key appears |
| --- | --- | --- | --- |
| `0'` | Address | the ZK keys and the note encryption key of one [address](#note-encryption-key-and-address) | in no Operation: the commitments of its notes hide it |
| `1'` | One-time | the ZK keys of one key the wallet gives out in the clear: the `note_pk` of a service declaration, the `public_key` of a proof of work claim, the key a program pays a note to | in the Operation, or with the program |
| `2'` | Node | the ZK keys of the `zk_id` of one service declaration | in the declaration |
| `3'` – `(2^{31}-1)'` | Reserved | wallets MUST NOT derive keys under them | |

Every leaf is an extended private key $`(k, c)`$ produced by `CDKpriv`. Its ZK keys are derived from its $`k`$ as [ZK-Compatible Secret Key Derivation in the Logos Blockchain](#zk-compatible-secret-key-derivation-in-the-logos-blockchain) specifies, and the note encryption key of an address leaf as [Note Encryption Key and Address](#note-encryption-key-and-address) does. The roles are a convention of the wallet: the ledger does not tell them apart, and a note under a key of any leaf is spent the same way.

- **Address leaves.** The public key of an address leaf is in no Operation, so any number of notes under it link nothing on the chain. A wallet uses the leaf `0'` by default, for the notes it receives, for its change and for its leader rewards. It MAY use further leaves, in order, to give different payers different addresses, since two payers holding the same address know they pay the same wallet. Each leaf in use costs one decapsulation per ciphertext the wallet reads ([Note Discovery and Recovery](#note-discovery-and-recovery)), and their number is part of the records of the wallet. A wallet MUST NOT put the public key of an address leaf in a field an Operation carries in the clear: it would tie the address, which every payer of the wallet holds, to that Operation.
- **One-time leaves.** A wallet takes the next unused leaf each time it needs a key that an Operation carries in the clear or that it gives to a program, and SHOULD NOT use that leaf for a second key, since two Operations carrying the same key are linked. The `note_stake_pk` of a declaration is the public key of the same leaf as its `note_pk`, unless the wallet stakes under another key ([Staking Keys](#staking-keys)). The notes under a one-time key have a nonce the ledger or the program derives, so no ciphertext delivers them and the leaf has no note encryption key.
- **Node leaves.** The `zk_id` of a declaration is the public key of a node leaf, and the secret its [Proof of Quota](proof-of-quota.md) takes is the `nf_sk` of that leaf. A wallet takes the next unused leaf for each declaration. The leaf holds no note. The node keeps its `nf_sk` online, and nothing above the leaf.

  **Why no `coin_type` level?** BIP-44 uses it to keep chains sharing one BIP-32 tree apart. This tree is already personalized with `Logos_MasterKGen` and `Logos_ExpandSeed`, so no other chain derives the same keys from the same mnemonic and a `coin_type` level would add nothing.

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

$`k_{\text{logos}}`$ is the `ZkSecretKey` used on the network, the spending secret key `spending_sk` of the notes under its public key. The nullifier key and the public key are derived exactly as the [Mantle specification](bedrock-v1.1-mantle-specification.md#keys) prescribes, with Poseidon2 in compression mode and the `NF_KDF_V1` and `KDF` DSTs:

```python
nf_sk = zkhash(FiniteField(b"NF_KDF_V1", byte_order="little", modulus=p), k_logos)  # compression mode
public_key = zkhash(FiniteField(b"KDF", byte_order="little", modulus=p), nf_sk)   # compression mode
```

This wallet-side step is not part of any circuit, so the DST costs nothing in proving time while preventing $`k_{\text{logos}}`$ from colliding with any other Poseidon2 output computed over the same field elements. Only the `NF_KDF_V1` and `KDF` derivations are evaluated inside proofs, each hashing a single field element thanks to this compression.

  **Why not use Poseidon2 for the full derivation?** While Poseidon2 is optimized for ZK circuits, its long-term stability and parameterization are still evolving. General-purpose hash functions like Blake2b offer a more stable and audited base layer. By introducing Poseidon2 only at the last compression step we isolate ZK-dependencies from the rest of the key derivation path. This ensures the wallet hierarchy remains valid even if Poseidon2 parameters are updated.

## Note Encryption Key and Address

From its ZK secret key $`k_{\text{logos}}`$, a wallet derives the key under which senders encrypt the contents of the notes they pay it ([Note Encryption](common-cryptographic-components.md#note-encryption-construction)). The decapsulation key is the 32-byte X-Wing seed

```python
sk_enc = blake2b_256(b"WALLET_ENC_SK_V1" + k_logos)   # the X-Wing decapsulation key, 32 bytes
pk_enc = xwing_encapsulation_key(sk_enc)              # 1216 bytes
```

where $`k_{\text{logos}}`$ is hashed as the 32-byte little-endian encoding of the field element ([Common Cryptographic Components](common-cryptographic-components.md)). The key is recovered from the seed with the ZK key, and every holder of a ZK secret key has one, whether or not the key comes from the hierarchy. It derives from the spending secret key and not from the nullifier key, so a node given `nf_sk` to stake ([Staking Keys](#staking-keys)) opens no ciphertext.

The **address** a sender needs is the pair `(public_key, pk_enc)`: the `ZkPublicKey` the notes are committed to and the encryption key their ciphertexts are encapsulated to. A wallet MAY hand out `public_key` alone; a sender holding only that gives the recipient `value` and `nonce` by other means. A sender MUST NOT fall back to another encryption when it holds `pk_enc`.

$`sk_{\text{enc}}`$ is a decryption key and nothing more: it opens every note ciphertext addressed to the wallet, past and future, and derives no nullifier, so it reveals what the wallet received, not what it spent or what it may spend.

### Address Encoding

An address is exchanged as a string, the encoding of the following bytes:

| Form | `version` | Bytes | Length |
| --- | --- | --- | --- |
| Key only | `0x00` | `version \|\| public_key` | 33 |
| Full | `0x01` | `version \|\| public_key \|\| pk_enc` | 1249 |

`public_key` is the 32-byte little-endian encoding of the field element ([Common Cryptographic Components](common-cryptographic-components.md)), and `pk_enc` the 1216 bytes of the X-Wing encapsulation key, the ML-KEM-768 key followed by the X25519 key.

The string is the Bech32m encoding of these bytes ([BIP-350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)): the bytes are regrouped into 5-bit values, most significant bit first, the last value padded with zero bits, and the human-readable part is `logos` on mainnet and `tlogos` on every other network. The 90-character limit of [BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki) does not apply, as for the unified addresses of [ZIP 316](https://zips.z.cash/zip-0316). A key-only address is 65 characters long on mainnet and a full address 2011.

A sender MUST reject a string, and create no note from it, when any of the following holds:

- it mixes upper and lower case, or its checksum is not valid;
- its human-readable part is not the one of the network of the sender;
- its `version` is neither `0x00` nor `0x01`, or the length of its bytes is not the one of its `version`;
- its padding is 5 bits or more, or holds a non-zero bit;
- `public_key` does not encode an integer lower than the modulus `p`;
- the ML-KEM-768 key of `pk_enc` fails the modulus check [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) requires before encapsulating.

A note committed to a public key nobody holds is lost for good, and so is a note whose ciphertext nobody can open when the ciphertext is its only delivery, which is why the checks are mandatory. The checksum detects any error in a single character at any length, and any other error except with a probability lower than 1 in $`10^9`$. The stronger guarantee of BIP-173, any error in up to four characters, holds for the key-only form, the code being designed for strings of at most 90 characters.

## Note Discovery and Recovery

The ledger holds the commitment of a note and nothing of its contents ([Mantle - Note Delivery](bedrock-v1.1-mantle-specification.md#note-delivery)). A wallet learns the user notes it receives in one of three ways, and keeps every note it learns, with its set, as [Note Tracking](#note-tracking) describes:

1. From a note ciphertext, received over a direct channel from the sender or read from a data availability layer the wallet follows. The delivery message carries the commitment and the ciphertext ([Note Encryption](common-cryptographic-components.md#note-encryption-construction)). The wallet first looks the commitment up: a message whose commitment is in no note set yet is kept, not decapsulated, until the commitment appears, since a sender hands the message over when it posts its Operation, at least a block before the note is in a set, and the outputs of a withdrawal wait in `pending_withdrawals` for longer. Once the commitment is in a set, the wallet decapsulates with $`sk_{\text{enc}}`$ and opens the sealed part with the commitment as associated data. If it opens, the wallet recomputes `derive_note_commitment(Note(value, nonce, public_key, stake_public_key))` with the decrypted `value` and `nonce`, its own `public_key`, and that same `public_key` as `stake_public_key`, the staking key of a delivered note unless the wallet named another key to the sender ([Staking Keys](#staking-keys), [Mantle - Note Delivery](bedrock-v1.1-mantle-specification.md#note-delivery)), which it then tries as well; the note is its own only if the result is the commitment and the commitment is in a note set the wallet may receive notes in. A ciphertext that fails to open, or opens to another commitment, is not the wallet's and is discarded.
2. From the Operation alone, for the notes the ledger creates and the user notes a program pays in a step consuming a note of the program, whose nonce the wallet derives from the Operation or the inscription and whose value it knows. A leader reward note comes from no Operation: the wallet creates it and keeps it with its nonce ([Leader Reward Notes](#leader-reward-notes)). A service reward note comes from no Operation either: the wallet derives its value and nonce as in [Service Reward Distribution](bedrock-service-reward-distribution.md), and reads its keys, `note_pk` and `note_stake_pk`, from the declaration.
3. In the clear, when the sender gives the recipient `value` and `nonce` by other means; the wallet records the note when it receives them.

A sender SHOULD keep the `value`, `nonce`, `public_key` and `stake_public_key` of each note it creates for a recipient among its records, and deliver the note again when the recipient asks. The ledger holds only the commitment, so the sender and the recipient alone know the note: the sender's copy is all that remains of a delivery that was lost or wrongly encrypted, and given the four fields anyone recomputes the commitment and finds its first occurrence in its note set, which answers a claim of non-payment.

### Delivery Inscription

A sender MAY commit to the delivery messages of a Mantle Transaction in an [`INSCRIBE`](bedrock-v1.1-mantle-specification.md#inscribe) Operation of that transaction, whose inscription is the tag `NOTE_DELIVERY_V1` followed by the delivery hash:

```python
def derive_delivery_hash(delivery_messages: list[bytes]) -> Hash:
    # The delivery messages of the outputs of the Mantle Transaction, in the order of its
    # Operations and of their outputs. An output delivered by other means has none, and
    # the list is not empty.
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"NOTE_DELIVERY_V1")
    for delivery_message in delivery_messages:
        h.update(delivery_message)
    return h.digest()

def delivery_inscription(delivery_messages: list[bytes]) -> bytes:  # 48 bytes
    return b"NOTE_DELIVERY_V1" + derive_delivery_hash(delivery_messages)
```

A delivery message is the 1208 bytes of [Note Encryption](common-cryptographic-components.md#note-encryption-construction), the commitment of its note followed by its ciphertext, so the hash fixes which outputs are delivered this way and with which ciphertexts. A Mantle Transaction holds at most one such inscription.

The inscription serves whoever carries delivery messages for others. A carrier holds no key, so without it a carrier cannot tell the delivery messages of a transaction from any other bytes. Handed delivery messages for a Mantle Transaction, it checks that each starts with the commitment of an output of the transaction, in the order of the outputs, and that their `delivery_inscription` is an inscription of the transaction.

- The inscription commits to one encryption of each note. Another encryption of the same note, made to deliver it again, is not the one the inscription covers: a sender that wants a second delivery to be checked keeps the delivery message.
- A user step and a program deposit are signed by their holder before their Mantle Transaction exists, so an `INSCRIBE` Operation of the transaction does not speak for them: their holder commits to a delivery in the `inscription` of the step, in the format of its zone.
- The inscription shows that outputs of its transaction are delivered by delivery messages, and nothing of their contents or of their recipients.

### Recovery from the Seed

Two wallets recovering from the same mnemonic MUST find the same notes, given the same chain and the same ciphertexts, so the procedure is normative. Let `GAP_LIMIT = 20`. For each account, starting with account 0:

1. **One-time and node leaves.** For each of the roles `1'` and `2'`, derive the leaves `0', 1', 2', …` and their public keys. A leaf is *used* if its public key is the `note_pk`, the `note_stake_pk` or the `zk_id` of a service declaration, or the `public_key` of a proof of work claim, in any Operation of the chain history. Stop after `GAP_LIMIT` consecutive unused leaves. The notes of a used leaf are those its Operations create, the service note, the service rewards and the proof of work reward, which the wallet recomputes as in 2 of [Note Discovery and Recovery](#note-discovery-and-recovery).
    - The lookup MUST cover the chain history and not only the declarations still stored: a leaf whose declaration was withdrawn is used.
    - A leaf whose key was given to a program is in no Operation, so the scan does not see it. A wallet MUST NOT leave `GAP_LIMIT` consecutive leaves that no Operation carries. It finds the note of such a leaf from the steps of the program, with the value the program or its records give.
    - Wallets MAY scan beyond `GAP_LIMIT` on user request but MUST NOT stop earlier.
2. **Address leaves.** Derive the leaf `0'`, and the further leaves the records of the wallet, or the user, count. For each leaf, find the delivered notes by trial decryption of the ciphertexts still available to the wallet. Find the leader reward notes with `is_own_reward` over the headers of the chain ([Leader Reward Notes](#leader-reward-notes)), for the public key of each address leaf and each staking secret key the wallet leads with, by default the `nf_sk` of its address leaves and of its used one-time leaves.
3. **Accounts.** Recover account `a + 1` only if account `a` has a used leaf, or holds or held a note.

What this finds depends on how each note reached the wallet:

| Note | From the seed and the chain | Otherwise |
| --- | --- | --- |
| Service note and service rewards | found, by the one-time key of the declaration | |
| Proof of work reward | found, by the one-time key of the claim | |
| Leader reward | found, when its nonce is derived | the records, when its nonce is random |
| Note delivered by a ciphertext, the change of the wallet included | not found | the ciphertext, when the wallet reads it again from a data availability layer, else the records |
| Note delivered in the clear | not found | the records |
| Note a program pays | its key, at a one-time leaf | its value, from the program or the records |
| Note under a staking key other than its public key | not found | that key, from the records |

A wallet MUST therefore keep a backup of its records that survives the loss of the device, or receive its notes through a layer it can read again from the seed alone. The change of a wallet, and the other notes it creates for itself, are delivered notes like any other: a wallet relying on such a layer publishes their ciphertexts there as well, to its own address. Publishing an encryption of those records under a key derived from the seed, as an inscription on a channel the wallet controls, is one way to tie that backup to the chain, and is not specified here.

Trial decryption costs one decapsulation per ciphertext the wallet reads, per leaf whose $`sk_{\text{enc}}`$ it holds, and only for the ciphertexts whose commitment is in a note set. A wallet following a data availability layer decrypts each new ciphertext once; a wallet recovering from its seed decrypts every ciphertext the layer holds since the first one it may have received a note in.

## Note Tracking

The [Mantle Ledger](bedrock-v1.1-mantle-specification.md#ledger) only holds note commitments and nullifiers, in note sets: the ledger note set, the SDP note set and one note set per channel but the null channel, each with its own commitment [Merkle Mountain Range](bedrock-v1.1-mantle-specification.md#commitment-merkle-mountain-range) (MMR) and [nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree) (IMT). To spend its notes and to participate in the leadership lottery, a wallet keeps the data its proofs need for every note it owns, in the note set the note belongs to.

To spend a note with a [ZkTransfer](bedrock-v1.1-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer), the wallet keeps:

- The note `(value, nonce, public_key, stake_public_key)`, its note set, and its `commitment = derive_note_commitment(note)`, derived as in [Note Commitment and Nullifier](bedrock-v1.1-mantle-specification.md#note-commitment-and-nullifier).
- The Merkle path of `commitment` to the root of the MMR peak holding it. With the other peaks of the MMR, which are public and served by any node, this path proves `commitment` in the MMR root. A ZkTransfer is proven against the commitment root of the note set at one of the last [`ROOT_WINDOW`](bedrock-v1.1-mantle-specification.md#ledger) blocks, so the wallet keeps the path up to date with the commitments appended to the MMR of the set. The root a proof names is public, and every block makes the root at its height specific to its fork, so a proof against the tip root is lost with that block. A wallet should prove against the root a fixed number of blocks below its tip, the same number for every wallet, for example 4, or the root of the latest immutable block if that is shallower, so that the root points at none of its notes and the proof survives a fork up to that depth. A note of a block younger than that one is not under this root, and the wallet should not spend it until it is, since a root younger than the fixed depth would reveal when the note was created. The cost is that a note waits, change included. A note created earlier in the same Mantle Transaction does not wait, since it reaches the proof through the commitment buffer on that same root: when an earlier Operation of the transaction adds commitments to the set, such as a proof of work claim followed by the Transfer spending its note, the proof is against that root extended with the commitment buffer of the set ([Validation](bedrock-v1.1-mantle-specification.md#validation)), and the wallet appends the buffered commitments with `append_commitment`, defined below, to copies of its peaks and of the paths of its notes in that set before proving, and keeps its own peaks and paths unchanged. A proof in a mini-block of an inscription is against that root extended with the buffer before the mini-block, whose commitments the sequencer provides.
- The `nullifier = derive_note_nullifier(commitment, nf_sk)`, where `nf_sk` is the nullifier key of the note. The note is spent once `nullifier` is in the nullifier set of its note set, whichever wallet instance spent it. Two identical notes share their nullifier and only one of them can be spent, so a wallet should count a received note only at the first occurrence of its commitment in its note set.

To prove its leadership with a note ([Proof of Leadership](cryptarchia-proof-of-leadership.md#eligible-sets)), the wallet, or the node it stakes through, needs the nullifier key and the staking secret key of the note, and also keeps:

- The Merkle path of `commitment` to the commitment root of its note set at the epoch snapshot, fixed for the epoch, and the path of the leaf of the set in the eligible tree of the snapshot. For the [Proof of Quota](proof-of-quota.md), it also keeps the leaf of the nullifier IMT of its note set at the snapshot holding the greatest nullifier lower than `nullifier`, and its Merkle path, fixed for the epoch.
- The leaf of the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree) of its note set holding the greatest nullifier lower than `nullifier`, and its Merkle path to the latest root of that IMT, with the path of the leaf of the set in the latest eligible tree. This leaf and its path change whenever a nullifier is inserted in the set. A wallet should update them at every block, whether or not one of its notes wins: the data must be fresh at the winning slot, so requests made only when a note wins tell the serving node when the wallet wins.

Requesting these paths from a third party reveals which commitments and nullifiers the wallet owns. A wallet that follows every commitment appended to the MMR and every nullifier inserted in the IMT of the note sets it holds notes in computes its paths locally. Following only some note sets still reveals, to the node serving them, which sets the wallet holds notes in and since when; a wallet that follows every set reveals nothing. The roots of the other note sets, which the paths in the eligible tree need, are public. A service provider could also serve the paths through private information retrieval, without learning which ones the wallet requests, once the wallet knows the index to request. The first low leaf of a note is the predecessor of `nullifier` among all the nullifiers of its set, and its index depends on `nullifier`, so a wallet finds it locally only if it holds all the nullifiers of the set.

The wallet should keep its peaks, the paths of its notes and their low leaves as of every block that is not yet immutable. On a reorganization, it restores those of the fork block, then applies the new branch.

A peak of the MMR is a perfect Merkle tree, which never changes once built: appending a commitment only adds a peak of height 0, and merges the last two peaks while they have the same height. The path of `commitment` inside its peak therefore only grows, by one node each time its peak is merged, which happens at most [`NOTE_SET_DEPTH`](bedrock-v1.1-mantle-specification.md#ledger) times. The wallet keeps a copy of the peaks, with their heights given by the binary decomposition of the number of commitments, and updates the paths of its notes while appending the commitments of each block:

```python
class OwnedNote:
    note: Note
    commitment: NoteCommitment
    nullifier: NoteNullifier
    peak: int                   # index of the peak holding commitment
    path: list[zkhash]          # Merkle path of commitment to the root of its peak, from the leaf up
    selectors: list[bool]       # at each level, 1 when the path node is on the left, as in Mantle

def append_commitment(peaks: list[(zkhash, int)], notes: list[OwnedNote], commitment: NoteCommitment,
                      owned: OwnedNote | None = None):
    # peaks holds the (root, height) of every peak, from left to right
    # owned is the note of commitment, with an empty path, when the wallet owns it
    peaks.append((commitment, 0))
    if owned is not None:
        owned.peak = len(peaks) - 1
        notes.append(owned)
    while len(peaks) > 1 and peaks[-1][1] == peaks[-2][1]:
        (left, height), (right, _) = peaks[-2], peaks[-1]
        for note in notes:
            if note.peak == len(peaks) - 2:
                # commitment is in the left peak, its new complementary node is the right peak
                note.path.append(right)
                note.selectors.append(0)
            elif note.peak == len(peaks) - 1:
                # commitment is in the right peak, its new complementary node is the left peak
                note.path.append(left)
                note.selectors.append(1)
                note.peak -= 1
        peaks[-2:] = [(zkhash(left, right), height + 1)]
```

A note the wallet owns is passed as `owned` with an empty path, and joins `notes` right after `peaks.append((commitment, 0))`, before the merges of its own append. Only the notes whose peak is merged are updated, so following a block costs one hash per merge. The path of a note to the commitment root of its note set at the epoch snapshot is the path it holds at the snapshot, completed with the peaks of the snapshot.

Inserting a nullifier changes exactly two leaves of the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree): the appended leaf and the leaf of the greatest nullifier lower than the inserted one. Every insertion is public, so a wallet fetching the leaves and Merkle paths of these two positions, as they stand after each insertion, reveals nothing about the notes it owns when it fetches them at every block. From them, it updates the low leaf of each of its notes in that set and its path with at most `NOTE_SET_DEPTH` hashes per changed leaf:

```python
class TrackedLowLeaf:
    nullifier: NoteNullifier    # nullifier of the owned note
    index: int                  # index of the IMT leaf holding the greatest nullifier lower than nullifier
    leaf: NullifierLeaf         # that leaf, as Mantle defines it
    path: list[zkhash]          # Merkle path of the leaf to the IMT root (len = NOTE_SET_DEPTH)

def branch_nodes(leaf_hash: zkhash, index: int, path: list[zkhash]) -> list[zkhash]:
    # nodes of the branch of index, from the leaf up to the root
    nodes = [leaf_hash]
    for height in range(NOTE_SET_DEPTH):
        if (index >> height) & 1:
            nodes.append(zkhash(path[height], nodes[-1]))
        else:
            nodes.append(zkhash(nodes[-1], path[height]))
    return nodes

def update_path(tracked: TrackedLowLeaf, index: int, leaf: NullifierLeaf, path: list[zkhash]):
    # replace the nodes of tracked.path that lie on the branch of the changed leaf
    nodes = branch_nodes(nullifier_leaf_hash(leaf), index, path)
    for height in range(NOTE_SET_DEPTH):
        if (index >> height) == ((tracked.index >> height) ^ 1):
            tracked.path[height] = nodes[height]

def on_nullifier_inserted(tracked: TrackedLowLeaf, inserted_nullifier: NoteNullifier,
                          low_index: int, low_leaf: NullifierLeaf, low_path: list[zkhash],
                          new_index: int, new_leaf: NullifierLeaf, new_path: list[zkhash]):
    # low_ is the leaf of the greatest nullifier lower than the inserted one and new_ the appended
    # leaf, each with its index and its path after the insertion
    if low_index == tracked.index and inserted_nullifier < tracked.nullifier:
        # the inserted nullifier is now the greatest one lower than tracked.nullifier
        tracked.index, tracked.leaf, tracked.path = new_index, new_leaf, new_path
    elif low_index == tracked.index:
        # only the pointer of the tracked leaf moved to the inserted nullifier
        tracked.leaf, tracked.path = low_leaf, low_path
    else:
        update_path(tracked, low_index, low_leaf, low_path)
        update_path(tracked, new_index, new_leaf, new_path)
```

### Staking Keys

Every [note](bedrock-v1.1-mantle-specification.md#keys) has a public key `pk` and a staking key `stake_pk`. The ZkTransfer enforces `nf_sk = zkhash(NF_KDF_V1, spending_sk)` and `pk = zkhash(KDF, nf_sk)`, and leading with the note takes `nf_sk` and the staking secret key `staking_sk`. The recommended default, which the ledger does not enforce, is that a wallet uses `staking_sk = nf_sk`, so that `stake_pk = pk` and its notes keep one key, and creates transfer outputs with the `pk` of the recipient as staking key unless the recipient asks for another. With this default, giving a node `nf_sk` lets it lead with the notes of the wallet without being able to spend them, the spending secret key staying offline, and the node learns when they are spent: this is cold staking.

A service declaration is made cold the same way. Its `note_pk` and `note_stake_pk` ([Declaration Storage](bedrock-service-declaration-protocol.md#declaration-storage)) should be keys of a cold wallet, which alone spends the service note at withdrawal and the service rewards, paid to the same two keys. The node keeps online only what it needs: the secret key of its `zk_id` for the Proof of Quota, its `provider_id` key, and, to lead with the service note and its rewards, the `nf_sk` of `note_pk` and the `staking_sk` of `note_stake_pk`, none of which spends them.

### Leader Reward Notes

The leader of a block chooses the public key and the nonce of its reward note ([Block Execution](bedrock-v1.1-block-construction.md#block-execution)), the public key being also the staking key of the note. The key can be any key of the wallet and can be reused for any number of blocks. The nonce has to be private and unpredictable, since a guessable nonce with a known key links its blocks: given the public value of a reward, anyone holding the key can test the nonce against the commitment. Two rewards of the same value under the same key and nonce are identical notes, of which only one can be spent. A wallet SHOULD therefore derive the nonce from the staking secret key `staking_sk` of the note it leads with, the `nf_sk` of that note by default ([Staking Keys](#staking-keys)), and the slot of the block, a slot holding at most one block of a chain:

```python
def derive_reward_nonce(staking_sk: ZkSecretKey, slot: int) -> NoteNonce:
    return zkhash(
        FiniteField(b"LEADER_REWARD_NONCE_V1", byte_order="little", modulus=p),
        staking_sk,
        FiniteField(slot, byte_order="little", modulus=p),
    )  # Poseidon2 hash mode
```

Only a holder of `staking_sk` computes this nonce, so it is private and unpredictable to anyone else, and the commitment still hides the key. The leader holds `staking_sk` whatever note leads and whatever key the reward is paid to, since its Proof of Leadership takes it, so the reward key can be a key whose secrets stay offline. The nonce is a private input the proof does not constrain, so this choice changes nothing in the circuit or on the chain.

A wallet recovering from its seed finds these reward notes without any record. For each staking secret key it leads with and each public key it is paid under, it recomputes the commitment of each block, at two hashes per block and pair, from what the header makes public:

```python
def is_own_reward(header: Header, staking_sk: ZkSecretKey, public_key: ZkPublicKey) -> bool:
    nonce = derive_reward_nonce(staking_sk, header.slot)
    note = Note(header.proof_of_leadership.reward_value, nonce, public_key, public_key)
    return derive_note_commitment(note) == header.proof_of_leadership.reward_commitment
```

The wallet keeps the note it created, with its nonce, and tracks it in the ledger note set, as it keeps any note. A wallet that draws the nonce at random instead keeps it private and unpredictable too, but the header holds only the value and the commitment of the note, so recovery from the seed alone does not find such a reward note: it depends on the wallet's backup of its notes. A reward note of value `0` can pay nothing, so a wallet has no need to keep it.

# Test Vectors

The vectors use the BIP-39 mnemonic `abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about` with an empty passphrase (64-byte seed). Byte strings are written in hex. A field element is written as the hex of its 32-byte little-endian encoding, as defined in [Common Cryptographic Components](common-cryptographic-components.md), which is also the wire form of a `ZkPublicKey`: the rows are bytes, not numbers. Poseidon2 values were produced with the `logos-blockchain-poseidon2` crate of the reference implementation, and X-Wing keys with the `x-wing` crate, which reproduces the `pk_enc` of the [Note Encryption Test Values](common-cryptographic-components.md#note-encryption-test-values).

## Master Key

| Quantity | Value |
| --- | --- |
| seed `S` | 0x5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4 |
| master secret key `I_L` | 0x72a5d51d61b1ea9f6ec4bb2287aa26d229443726788bc38440012c44eda58ae8 |
| master chain code `I_R` | 0xc67234c2aebc79aaaa2f79caa66325b86932079331a60f36004658d20d06c3e8 |

## Leaf Keys

| Path | Role | `k` (leaf) | `c` (leaf) | `k_logos` | `nf_sk` | `public_key` |
| --- | --- | --- | --- | --- | --- | --- |
| `m/154'/0'/0'/0'` | address | 0xdfd5e34a2ffad38e96540489551e0ce5ef10792bd660cf413a9f6dd28a77c016 | 0x672eeedfdc70109e33ca57b79e1b6fa62f279a162fa203d1ba0163cd70b3d072 | 0x5e09bf4ce6b3f42970104a6f5940104407f98da0eb946104c13fb4f94c011f16 | 0x9301f8d0f4c13565063baf9b261c001522c47ea4d8cf54c9945b297d6da14724 | 0xa05de446592d0396462b1788d3a01c1e4ad3a2102e58e541502b37391c7abc1c |
| `m/154'/0'/0'/1'` | address | 0x0baeddd9dc5d60ed0dc64597d2b0f49d486e5448cd8ac94fe2515c80fbf5d67c | 0x802cdbc751687844cf324e883fa024d80e29d35b4de5d51f151afa5d3c6d2232 | 0x070b4df159a3bc13e9663f39f5e71afda9b68626c49e48c85a16b8ec55ef162f | 0xd6833fb550ed13b66caf51cc810cabf4006c35f364806a8026a59c8dbc85a80a | 0xd979f23092d476a288c9843ed63148f4f430cb5ae69737248f6b543561ca142a |
| `m/154'/0'/1'/0'` | one-time | 0x4f3acc80a0fecc95bf8d8cd16435803c5cee29783a6d2809e9fc10840dadb57c | 0xa85b8265092527323173c6ab624e29faa848dc5cda409a7fbe1d4ec80e8c4130 | 0x0e00954c65e6495a92cebf12b058232e770bcf933dd1cfd5d28071f367639a1f | 0xa83dccff7a8ff357d0f82981e8f9160a950efa41ea3985ed8f6d6e221ecb432d | 0xac494c4cdb52b103149c12ad399feafc6064ea04f3e975efb953b441fe9d3e26 |
| `m/154'/0'/2'/0'` | node | 0x9d309152b9ae941a1dcd75a58084075a920f36374edc6059328d66e1af586cd5 | 0x6f940b35f1f2317d423bebf8152a8e249b67fca4223d5f7f9962d6002e53d7f0 | 0x9e112f71b31108b1af622476e6b6f17b70995a815fda9abbf1e4e51a22b90a07 | 0xdf397a7ac8cbc4b99df277bf4b619aaa03573750ef4dd9c538881a8402511e0c | 0xbb447fe31614cc22518ec7c53c5c8a055c11c7f9430bd7c0bb10f408f636820c |
| `m/154'/1'/0'/0'` | address | 0x0761a669ac959a0e302b0cda9b5b3db6e36c3b120b8aacda0090b43e419728c8 | 0xb56ff3a881176e7ccff4e96f4cad0bda7cc2408f945ffb9858d619733e3c7e56 | 0xf4365814fc85dc8fdd84594cc4cbcbc2031e58dadf63e28215edc0c9a0aba12f | 0x9bfab956c5cf343d0e466c1cef45930c3d1f29128ac8d193592196838d09e205 | 0x4b6fb991c649e279db892fdbab36af66673a7c0030793c8bb6846f861fe90101 |

## Address

The address of the leaf `m/154'/0'/0'/0'`, in its two forms on mainnet, and its key-only form on another network.

| Quantity | Value |
| --- | --- |
| `sk_enc` | 0x4e39ee07eabec76b57d28e17be0b030759e89aa7dae5b522c1097e6b2566eb12 |
| `pk_enc` | 0xbcf633e5f1b1f337b4789b32ecc51045a77ec35464cf95a326068e67d0060d2a79d4f17fdf0047988ac2ba02595d0048a7a9331f379b47c7173d1ac26016253c69b2df5b1dc3985d271cbe41b66654812dfe88579806cba5953b08e72c2db59e9d72193cc3570fdb759e67418ac682e8c7996f30148276563d17b33f228398d695fa1b582e97266898a99b417e4caa5fa5a6bd4a20b96d63050738774b032648399b23ca562a1b1d80c1a792d55faaf6b9b1010d02468de4a2b385d03c705b934d4c63c15a3242c75dd42a6612fa0c3584b160fa9307aa2a487aa12bcc2cb98c232e3b091e9c543d9c4663a6500815244452a2737b6fe7325cde6b78349155b5245b96669c61c722c3b31969b8293e01c53434442adb1e1ec5b4c7bb2fb80424f4052b150568ead74127e1334a447562a7c4cddb00ea1b5fdd7b1adc47149831afbabb369ab59dd4e569a13a43a12a63542562aef1b329b2c18895acf2c0853421c628292ae3c6b42f29c25b2686a7cabf67d0c08ddb28117a1ed06103e04188f094503c3aa384c7b7414826ba3250aa5787323750e522728a162afd730a6499577c1278ee89565ec585e0d50dd966c5bfcb779a140383aa2d5190a2cb6a7cfd614da7411147593de1cc168dcaca182520c7c013588b9018db4b0d11cf632138922a51d8515007474c798a4065e6b5ee72bbb0d91f54b524a9b4a12364a40c7055d4738896111c1b5a33d6642da5a71a54708d47d31ed8bb63d31cc1d70b15876c7385d966bd190ce047112dd8675c721705f183dc862a3d033b1ad1567309ca7642add8b07c53134c44214bc9b5a2c6209378c6a3a9725868526f841973c2ea5b23e70dd3302cdf24bdc41aa0eed998e3124dc46a48291ac79e9112e6a687695b3007e55a7ae32a9c16301f6c3ec8368de780b3f83a79ce4733dfb02a324044e9c2c00f5902b65c4342f8bf53577820d1914e710e8b6148d2ec5b891cc34b09ce6850024fdab798767c62e277a5a65989633a05eb2773797c7ee9a9aeb7156b145d1f46cca54494eb3ba8a9483bc1d6930165856bac7a497ba7a103b9b3e1446080aedef1577ada7c8c3014ef773590a978ea840940d05ba3da63119a44dd0aa0ca1b8de112cd9e390a5d59873e811c5193836aa92ab4db7e7f5c7418f8b816f987d1f5b5d0064972095b581a09150905ca17a04116bf7e83b57d685a260737c4e82b70f61ef2b31e937174720c4d8c0c34f94a1736c0b5f1ac4922f03531aaa1874a11535c949dd174a325746d3c2e6385346bb60e0988b7ac714560d74831274bbf712416eab931f152e23302a325a6e93172998240d617b08cf038eb9a66b1a93a642ca60eba2fb8f79c92bbb8c36c6e93e1053d1289cdca291a8371836c42993b80bebc0506813c2ad4802cd1cdbeab6b89f13df3f10ea2204ef84a9e30266c5ec054d00437aa0556bee4022e39a2007d7295820ccbfb9a2832277af486bb398db248ca1e4a94e4e282ef615fa9ebb30391380808305e7a8bcfb6318ef014e8a8419d3c73405a47bee82f431b2700cd00600ccd186c26431b1602a39576a53b311a3a352c71888391e5a79b20b3719ec251a9ab2ed7771506080596156f1ba98223846cd309fb31049fc64ef8d5633edde30914075e9180cc6a794a717f9d6da9649ac422e8ce8520ba43d6ae40cf8f189dfa62431e90f064abdb1a7b0f |
| key-only address, `logos` | logos1qzs9mezxtyks89jx9vtc35aqrs0y45azzqh93e2p2q4nwwgu027pcwp3kqn |
| key-only address, `tlogos` | tlogos1qzs9mezxtyks89jx9vtc35aqrs0y45azzqh93e2p2q4nwwgu027pcd62lj4 |
| full address, `logos` | logos1qxs9mezxtyks89jx9vtc35aqrs0y45azzqh93e2p2q4nwwgu027pe08kx0jlrv0nx7683xejanz3q3d80mp4gex0jk3jvp5wvlgqvrf20820zl7lqpre3zkzhgp9jhgqfzn6jvclx7d503ch85dvycqky57xnvkltvwu8xzayuwtusdkve2gzt073ptespkt5k2nkz889skmt85awgvnes6hpldht8n8gx9vdqhgc7vk7vq5sfm9v0ghkvlj9quc662l5x6c96tjv6yc4xd5zljv4f06tf4afgstjmtrq5rnsa6tqvnyswvmy099v2smrkqvrfuj64064a4ekyqs6qjx3hj29vu96q78qkunf4xx8s26xfpvwhw59fnp97svxkztzc86jvr652jg02sjhnpvhxxzxt3mpy0fc4pan3rx8fjspq2jg3zj5fehkml8xfwdu6mcxjg4tdfytwtxd8rpcu3v8vcedxuzj0spc56rg3p2mv0pa3d5c7ajlwqyyn6q22c4q45w446pylsnxjjyw43203xdmvqw5x6lm4a34hz8zjvrrta6hvmf4dva6njkngf6gwsj5c65y432audn9xevrzy44nevppf5y8rzs2f2u0rtgtefcfdjdp48e2lk05xq3hdjsyt6rmgxzqlqgxy0p9zs8sa28px8kaq5sf46xfg254u8xgm4pefzw29pv2hawv9xfx2h0sf83m5f2e0vtp0q65xajek9hl9h0xs5qwp65t23jz3vk6nul4s5mf6pz9r4j00pestgmjk2rqjjp37qzdvghyqcmd9s6yw0vvsn3y3228v9z5q8gax8nzjqvhnttmnjhwcdj865k5j2nd9pydj2grrs2h288zykzywpkk3n6ejzmfd8rf28pr286v0d3wmr6vwvr4ctzkrkcuu9m9nt6xgvupr3ztwcvaw8y9c97xpaep3285pnkxk32eesnjnkg2ka3vru2vf5c3ppf0ymtgkxyzfh334r49e9s6zjd7zpju7zafdj8ecd6vczeheyhhzp4g8wmxvwxyjdc34ys2g6c70fzyhx56rkjkesqlj457hr92wpvvqldslvsd5du7qt87p6088ywv7lkq4ryszya8pvqr6eq2m9cs6zlzl4x4mcyrgeznn3p69kzjxja3dcj8xrfvyuu6zsqf8a4ducwe7x9cnh5kn9nztr8gz7kfmn0978a6df46m326c5t505dn99gj2wkwag49yrhswkjvqktptt43ayj7a85ypmnvlpg3sgptk779th4knu3scpfmmhxkg2j782ssy5p5zm50dxxyv6gnws4gx2rwx7zykdncus5h2esulgz8z3jwpk42f2kndhul6uwsv03wqklxrarad46qryjusftdvp5zg4pyzu59aqgytt7l5rk47ksk3xqumuf6ptwrmpau4nr6fhzarjp3xccrp5l99pwdkqkhc6cjfz7q6nr24psa9pz56ujjwaza9ry46x60pwvwzng6akpcyc3davw9zkp46gxyn5h0m3ystw4wf379fwyvcz5vj6d6f3w2vcysxkz7cgeupcawdxdvdf8fjzefswhghm3auuj2am3smvd6f7zpfaz2yumj3fr2phrqmvg2vnhq97hszsdqfu9t2gqtx3ekl2k6uf7y7l8ugw5gsya7z2ncczvmz7cp2dqpph4gz4d0hyqghrngsq04eftqsve0ae52pjyaa0fp4m8xxmyjx2re9ffe8zsthkzhafawes8yfcpqyrqhn6308mvvvw7q2w32zpn578xsz6g7lwst6rrvnspngqvqxv6xrvyep3k9sz5w2hdffmxydr5dfvwxyg8y0957djpvm3nmp9r2dt9mthw9gxpqzev9t0rw5cyguydnfsn7e3qj0uvnhc643nah0rpy2qwh53srxx5722w9le6mdfvjdvgghge6zjpwjr66hypnu0rzwl5cjrr6g0qe9tmvd8krcskm2q3 |

## Delivery Inscription

The `delivery_inscription` of one delivery message, the `commitment` of vector 1 of the [Note Encryption Test Values](common-cryptographic-components.md#note-encryption-test-values) followed by its `ciphertext`.

| Quantity | Value |
| --- | --- |
| `delivery_hash` | 0xa352841f541aba1aab7d3abbb1eb4487e71756050f5c5acb757a62f8d8a14f91 |
| `delivery_inscription` | 0x4e4f54455f44454c49564552595f5631a352841f541aba1aab7d3abbb1eb4487e71756050f5c5acb757a62f8d8a14f91 |

## Leader Reward Nonce

The reward notes of a wallet leading with a note of the leaf `m/154'/0'/0'/0'` and paid under the `public_key` of that leaf: `staking_sk` is the `nf_sk` of the leaf, and `public_key` is also the staking key of the reward note. `slot` and `reward_value` are numbers.

| `slot` | `reward_value` | `derive_reward_nonce(staking_sk, slot)` | `reward_commitment` |
| --- | --- | --- | --- |
| 1 | 1000 | 0x8adbe762f38ad51d1c2888054f5719365b4ef41d9b0d3ffb45c04e0f62a7722b | 0x3c14a6f0d8868bfe8b626a23fbc60829f5b8536b54b5d71a8fdcac13eaf99f18 |
| 4886718345 | 1250999896491 | 0xaa6249ac6bd90570c96c60512beba512614d8d37156641e4dfb7deccbb99f317 | 0x31e021cb7207b14e1f911b4653ead305821428fad26bd7ad061d31c15d6b0f0c |

## Domain Separation Tags as Field Elements

| DST | `FiniteField(DST, byte_order="little", modulus=p)` |
| --- | --- |
| `WALLET_ZK_SK_V1` | 0x57414c4c45545f5a4b5f534b5f56310000000000000000000000000000000000 |
| `NF_KDF_V1` | 0x4e465f4b44465f56310000000000000000000000000000000000000000000000 |
| `KDF` | 0x4b44460000000000000000000000000000000000000000000000000000000000 |
| `LEADER_REWARD_NONCE_V1` | 0x4c45414445525f5245574152445f4e4f4e43455f563100000000000000000000 |
| `NOTE_CM_V1` | 0x4e4f54455f434d5f563100000000000000000000000000000000000000000000 |

# References

[ZIP 32: Shielded Hierarchical Deterministic Wallets](https://zips.z.cash/zip-0032)

[CIP-0003](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0003/README.md)

[slip-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

[bip-0039](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

[bip-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
