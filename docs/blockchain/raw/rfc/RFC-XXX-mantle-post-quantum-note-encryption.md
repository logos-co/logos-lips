# [RFC] Mantle: Post-quantum note encryption, optional per output

**Motivation and proposal:** [PR #XXX](https://github.com/logos-co/logos-lips/pull/XXX)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-19 |

## Reviewer Orientation

Read the PR's Motivation first. The private ledger of [RFC-480](RFC-480-mantle-private-utxo-ledger.md) and the programs of [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) are assumed; this document only adds how a recipient learns a note.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Common Cryptographic Components](#affected-specifications), [Note Encryption](#1-note-encryption) | the X-Wing KEM used as specified, the BLAKE2b key derivation, ChaCha20-Poly1305 with the commitment as associated data, the 1176-byte ciphertext |
| 2 | Critical | [Mantle](#affected-specifications), [Note Delivery](#2-note-delivery) | one optional ciphertext per output of the five Operations creating user notes; the ledger checks the count and the size only; the ciphertexts are permanent |
| 3 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#3-encoding) | the `Ciphertexts` list and its flag byte; canonical form |
| 4 | High | [Wallet Technical Standard](#affected-specifications), [key, address, discovery](#4-wallet-key-address-and-discovery) | the encryption key next to the ZK key, the two-key address, trial decryption, what recovery from the seed does and does not cover |

# Discussion

## Why encrypt on chain at all, and why optionally

The private ledger holds commitments only. A recipient has to learn the value and the nonce of a note before it can recompute the commitment, spend the note or count it toward the lottery. Every deployed shielded ledger delivers these two fields as a ciphertext next to the commitment, because it is the only delivery that survives the loss of the recipient's device: the seed re-derives the key, and the chain holds the ciphertexts.

The ciphertext is not free. The post-quantum encapsulation costs 1120 bytes per output, against 32 for an elliptic-curve one, and these bytes are permanent. The proposal therefore makes the ciphertext a choice of the sender, output by output: a sender holding the recipient's encryption key attaches it, a sender that does not, or a pair of users that delivers notes off chain, leaves it out. The ledger does not care which. What is specified is the one format a ciphertext has when it is present, so that every wallet can open every ciphertext addressed to it.

## Why a post-quantum hybrid now

A note ciphertext stays on chain for the life of the chain. An adversary recording the chain today reads every elliptic-curve ciphertext the day a cryptographically relevant quantum computer exists, and the plaintext (`value`, `nonce`) with a candidate public key recomputes the commitment, which attributes every note to its recipient. Changing the scheme later protects later notes only. The proof system and the signatures do not share this exposure: when they break, nothing already on chain becomes readable. The ledger is on testnet, so starting mainnet with a post-quantum encapsulation leaves no classically encrypted history behind.

The hybrid X-Wing (ML-KEM-768 and X25519) is used exactly as specified, with its registered sizes and test vectors, for the reason the transport specification chose the same pair: either component failing leaves the other. The key derivation is the domain-separated BLAKE2b the components already use, instead of the HKDF of HPKE, which registers no BLAKE2 KDF; the composition is therefore specified here as its own, not as HPKE. The combiner inside X-Wing is left as SHA3-256: changing it would produce a construction with no proof, no test vectors and no implementation to reuse, and SHA-3 is in the dependency set anyway through ML-KEM.

## Cost

Per output with a ciphertext, 1176 bytes against 88 with an elliptic-curve encapsulation. A payment with one external output and a change output the wallet delivers to itself is about 1.5 KB; the maximum of 8 outputs with ciphertexts is about 10 KB, within one Blend message. The bytes are priced by the Permanent Storage Gas like the rest of the transaction. Decapsulation costs about 100 µs per ciphertext on a laptop with an unoptimised implementation, so a wallet scans a million ciphertexts in about two minutes; the measurements and the comparison of implementations are in the research report ([logos-blockchain/research#23](https://github.com/logos-blockchain/research/pull/23)).

The cost that grows is the data a recovering wallet downloads: every ciphertext since the first block it may have received a note in, since no server can filter them without the viewing key. This is the same scan every shielded ledger has, at thirteen times the size of a classical one; making the ciphertext optional bounds it to the outputs that chose it. Detection tags and oblivious synchronisation, the two ways other ledgers reduce it, are left for a later specification.

## Assumptions and open points

- The encryption key is derived from the same leaf as the ZK key, so one leaf gives one address. The hierarchy of the wallet standard is otherwise unchanged.
- Nothing checks a ciphertext against its commitment. The ledger cannot, and a verifiable encryption inside the circuit would cost far more than the problem is worth: a wrong ciphertext deprives the recipient of a note the sender paid for, and no one else.
- The address with `pk_enc` is 1248 bytes. Payment requests and URIs carry it without difficulty; a directory of encryption keys published by inscription, letting an address carry a hash instead, is possible later and not specified here.
- The research report recommends keeping the expanded decapsulation key in memory; the library choice is an implementation matter.

# Details

## 1. Note Encryption

Common Cryptographic Components gains a Note Encryption scheme:

- KEM: X-Wing as specified in `draft-connolly-cfrg-xwing-kem`, encapsulation key 1216 bytes, decapsulation key a 32-byte seed, ciphertext 1120 bytes.
- Key: `BLAKE2b-256(LOGOS_NOTE_ENC_V1 || ss || ct)`.
- AEAD: ChaCha20-Poly1305 under that key, zero nonce, associated data the 32-byte little-endian note commitment.
- Plaintext: `value` (8 bytes, little-endian) `||` `nonce` (32 bytes, little-endian). Sealed, 56 bytes.
- `NOTE_CIPHERTEXT_SIZE = 1176`: the KEM ciphertext followed by the sealed plaintext.

Common Cryptographic Components is revision 1.4.0.

## 2. Note Delivery

Mantle gains a Note Delivery subsection under Notes, and the Operations creating user notes gain a `ciphertexts` field:

```python
class Transfer:
    inputs: list[NoteNf]
    outputs: list[NoteCm]
    ciphertexts: list[NoteCiphertext]  # new: one per output, the note ciphertext or empty
    cm_merkle_root: MerkleRoot
    excess_value: TokenValue
```

- The same field, with the same meaning, in `ChannelDeposit`, `ChannelWithdraw`, `UserStep` and `Payment`. Program steps create no user note the recipient cannot derive, and carry none.
- Validity: `len(ciphertexts) == len(outputs)`, and every non-empty entry has exactly `NOTE_CIPHERTEXT_SIZE` bytes. Nothing else is checked.
- Notes the ledger creates and the user notes a program pays derive their nonce from the Operation and need no ciphertext; a note created without a ciphertext is delivered off chain.
- The ciphertexts are part of the payload, covered by the operation identifier and the transaction hash, priced by the Permanent Storage Gas, and never pruned.
- Mantle is revision 2.2.0.

## 3. Encoding

- `Transfer = Inputs Outputs Ciphertexts CmMerkleRoot Value`, `ChannelDeposit = ChannelId Inputs CmMerkleRoot Outputs Ciphertexts Value DepositMetadata`, `ChannelWithdraw = ChannelId Inputs CmMerkleRoot Outputs Ciphertexts`, `UserStep = Inputs Outputs Ciphertexts CmMerkleRoot Buffered`, `Payment = Inputs Outputs Ciphertexts CmMerkleRoot Buffered Value Intent`.
- `Ciphertexts = *NoteCiphertext` with exactly `OutputCount` entries and no count of its own; `NoteCiphertext = CiphertextFlag [1176BYTE]`; `CiphertextFlag = Byte`, `0x00` for no ciphertext and `0x01` for one. Any other flag value is invalid.
- Mantle Transaction Encoding is revision 2.2.0.

## 4. Wallet: key, address and discovery

- `sk_enc = BLAKE2b-256(WALLET_ENC_SK_V1 || k_i)` is the X-Wing decapsulation key of the leaf that holds `k_logos`; `pk_enc` is its encapsulation key.
- The address is `(public_key, pk_enc)`. A wallet may hand out `public_key` alone, in which case its notes are delivered off chain. A sender holding `pk_enc` uses it and nothing else.
- Discovery: trial decryption of every note ciphertext in the sets the wallet may receive notes in, with the commitment check; derivation for ledger-created and program-paid notes; off-chain records for the rest.
- Recovery from the seed covers the first two and not the third; a wallet accepting notes without ciphertexts keeps a backup of its records.
- Wallet Technical Standard is revision 1.3.0.

## Chores

- The Mantle and encoding test vectors carry TODO markers until regenerated with the `ciphertexts` field.

# Implementation

- [ ] Add X-Wing (ML-KEM-768 + X25519) to the key management system, with deterministic key generation from a 32-byte seed and the expanded decapsulation key kept in memory.
- [ ] Implement `encrypt_note` and `decrypt_note`: BLAKE2b-256 key derivation, ChaCha20-Poly1305 with the commitment as associated data.
- [ ] Add the `ciphertexts` field to `Transfer`, `ChannelDeposit`, `ChannelWithdraw`, `UserStep` and `Payment`, its encoding and its validation (count and size).
- [ ] Derive `sk_enc` and `pk_enc` in the wallet next to the ZK key; expose the two-key address.
- [ ] Wallet discovery by trial decryption with the commitment check, and recovery from the seed.
- [ ] Regenerate the Mantle and encoding test vectors; add vectors for `encrypt_note` and `decrypt_note`.
- [ ] Benchmark decapsulation and the scan on the reference machine.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.4.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.2.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.2.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.3.0 |
