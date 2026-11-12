# [RFC] Post-quantum note encryption

**Motivation and proposal:** [PR #486](https://github.com/logos-co/logos-lips/pull/486)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC: an optional note ciphertext per output of the Operations creating user notes | 2026-10-19 |
| v2 | The ciphertext leaves the chain: no change to the Operations or their encoding, the scheme is a recommendation for delivery through a direct channel or a data availability layer; X-Wing becomes its own entry of Common Cryptographic Components with the Note Encryption construction under it; test values added; Mantle gets a Note Delivery note only. The leader reward note, whose nonce its leader chooses privately, is kept by the wallet that created it | 2026-11-02 |
| v3 | The note gains a staking key ([RFC-481](RFC-481-mantle-programs-governing-channel-notes.md)): a delivered note takes the public key of its recipient as staking key unless the recipient asked the sender for another, so the ciphertext still carries `value` and `nonce` only and the recipient recomputes the commitment with its public key as both keys. A sender keeps the notes it creates for others and delivers them again on request | 2026-11-06 |
| v4 | Review of 2026-11-06: service notes and service reward notes take the `note_stake_pk` of their declaration, and a service reward note is found from Service Reward Distribution; SDP withdrawals and program deposits join the delivered notes; the sender rule on the staking key is a MUST and a note under another staking key belongs to the records; a delivery message is kept until its commitment is in a set and decapsulated then, one decapsulation per ciphertext per leaf; `decrypt_note` checks the length and returns `None` on a rejected KEM ciphertext, with no X25519 all-zero check; the Annex labels its byte rows and gains a vector with a non-palindromic nonce and a value above 2^32; X-Wing referenced at revision 11, public-key encryption in the Overview | 2026-11-09 |

## Reviewer Orientation

Read the PR's Motivation first. The private ledger of [RFC-480](RFC-480-mantle-private-utxo-ledger.md) and the programs of [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) are assumed; this document only adds how a recipient learns a note. Nothing changes in the Operations, their validation or their encoding.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Common Cryptographic Components](#affected-specifications), [X-Wing and Note Encryption](#1-x-wing-and-the-note-encryption-construction) | the X-Wing KEM used as specified, the BLAKE2b key derivation, ChaCha20-Poly1305 with the commitment as associated data, the 1176-byte ciphertext and the 1208-byte delivery message, the test values |
| 2 | High | [Wallet Technical Standard](#affected-specifications), [key, address, discovery](#2-wallet-key-address-and-discovery) | the encryption key next to the ZK key, the two-key address, trial decryption of the ciphertexts the wallet reads, what recovery from the seed does and does not cover |
| 3 | Low | [Mantle](#affected-specifications), [Note Delivery](#3-note-delivery) | a note under Notes saying how a holder learns a note, pointing at the two documents above; no change to any Operation |

# Discussion

## Why the ciphertext is not on chain

The private ledger holds commitments only. A recipient has to learn the value and the nonce of a note before it can recompute the commitment, spend the note or count it toward the lottery. The ledger itself has no use for these two fields: it verifies proofs over commitments and nullifiers and never decrypts anything.

The first revision of this proposal attached an optional ciphertext to each output of the Operations creating user notes, so that the chain would carry the data a wallet needs to recover from its seed. That puts 1176 permanent bytes per output on every node, priced as permanent storage, for data that one peer serving the recipient makes available just as well. Decentralised availability guarantees distribution; the recipient does not need distribution once it holds the note, it needs the ciphertext to be somewhere it can read. The ciphertext is therefore delivered off chain: through a direct channel between the sender and the recipient, or published on a data availability layer, such as Logos storage, that the recipient reads.

What the specification fixes is the one format a ciphertext has, so that every wallet opens every ciphertext addressed to it wherever it comes from, and the key a wallet derives for it. What it does not fix is the channel. The consequence for recovery is stated in the wallet standard: a wallet restoring from its seed finds the notes the ledger creates from the chain, and the notes it was paid from whoever still serves their ciphertexts, so it keeps a backup of its records or reads its notes from a layer it can read again from the seed alone. A leader reward note, whose nonce is private, depends on the backup of the notes of the wallet.

## Why a post-quantum hybrid

A note ciphertext published on a data availability layer is public and may be retained indefinitely. An adversary recording it today reads every elliptic-curve ciphertext the day a cryptographically relevant quantum computer exists, and the plaintext (`value`, `nonce`) with a candidate public key recomputes the commitment, which attributes the note to its recipient. Changing the scheme later protects later notes only. The proof system and the signatures do not share this exposure: when they break, nothing already published becomes readable.

The hybrid X-Wing (ML-KEM-768 and X25519) is used exactly as specified, with its registered sizes and test vectors, for the reason the transport specification chose the same pair: either component failing leaves the other. X-Wing is defined with ML-KEM-768 only; ML-KEM-512 would save 320 of the 1176 bytes at the price of a construction of our own, without the draft's proof, vectors or implementations, and with the ciphertext off chain the saving carries no weight. The key derivation is the domain-separated BLAKE2b the components already use, instead of the HKDF of HPKE, which registers no BLAKE2 KDF; the composition is therefore specified as its own, not as HPKE. The combiner inside X-Wing is SHA3-256 and ML-KEM uses SHA-3 internally; both belong to the KEM as specified and are never called by the Logos Blockchain itself, so SHA-3 is not listed among its hash functions.

## Cost

A delivery message is 1208 bytes: the 32-byte commitment, the 1120-byte KEM ciphertext and the 56-byte sealed value and nonce. A payment with one external output and a change output the wallet delivers to itself is about 2.4 KB of messages. Decapsulation costs about 100 µs per ciphertext on a laptop with an unoptimised implementation, so a wallet scans a million ciphertexts in about two minutes; the measurements and the comparison of implementations are in the research report ([logos-blockchain/research#23](https://github.com/logos-blockchain/research/pull/23)).

A wallet reading its ciphertexts from a shared data availability layer tries every ciphertext published there, since no server can filter them without the viewing key. Detection tags and oblivious synchronisation, the two ways other ledgers reduce that scan, are left for a later specification, as is the layout of the ciphertexts on the layer.

## Assumptions and open points

- The encryption key is derived from the same leaf as the ZK key, so one leaf gives one address. The hierarchy of the wallet standard is otherwise unchanged.
- Nothing checks a ciphertext against its commitment before the recipient opens it: a wrong ciphertext deprives the recipient of a note the sender paid for, and no one else. The sender keeps the note it created and delivers it again when asked, which also answers a claim of non-payment.
- The ciphertext carries `value` and `nonce` only. The staking key of RFC-481 is the public key of the recipient unless the recipient asked the sender for another, in which case that key belongs to its records, since neither the seed nor the ciphertext gives it. Carrying the staking key in the plaintext would add 32 bytes to every ciphertext for a case the rule covers, and a sender ignoring the rule withholds the note no more than one publishing a wrong ciphertext does.
- The address with `pk_enc` is 1248 bytes. Payment requests and URIs carry it without difficulty; a directory of encryption keys published by inscription, letting an address carry a hash instead, is possible later and not specified here. The encoding of the address, with its checksum, is specified with the wallet hierarchy that follows this proposal, as the bare `public_key` has none today.
- The delivery channel is not specified. A direct channel and a data availability layer are the two the wallet standard names; which layer, and how a wallet finds its ciphertexts on it, is for the specification of that layer.
- The research report recommends keeping the expanded decapsulation key in memory; the library choice is an implementation matter.

# Details

## 1. X-Wing and the Note Encryption construction

Common Cryptographic Components gains a section 4, Public-Key Encryption, with X-Wing as its entry and the Note Encryption construction under it:

- KEM: X-Wing as specified in `draft-connolly-cfrg-xwing-kem`, encapsulation key 1216 bytes, decapsulation key a 32-byte seed, ciphertext 1120 bytes.
- Key: `BLAKE2b-256(LOGOS_NOTE_ENC_V1 || ss || ct)`.
- AEAD: ChaCha20-Poly1305 under that key, zero nonce, associated data the 32-byte little-endian note commitment.
- Plaintext: `value` (8 bytes, little-endian) `||` `nonce` (32 bytes, little-endian). Sealed, 56 bytes.
- `NOTE_CIPHERTEXT_SIZE = 1176`: the KEM ciphertext followed by the sealed plaintext. The delivery message is the commitment followed by the note ciphertext, 1208 bytes.
- Test values in the Annex: the wallet keys of two leaves, two encryptions with their encapsulation randomness, and the decryption cases.

Common Cryptographic Components is revision 1.4.0.

## 2. Wallet: key, address and discovery

- `sk_enc = BLAKE2b-256(WALLET_ENC_SK_V1 || k_i)` is the X-Wing decapsulation key of the leaf that holds `k_logos`; `pk_enc` is its encapsulation key.
- The address is `(public_key, pk_enc)`. A wallet may hand out `public_key` alone, in which case the sender gives it the value and the nonce by other means. A sender holding `pk_enc` uses it and nothing else.
- Discovery: trial decryption of the ciphertexts the wallet receives over a direct channel or reads from a data availability layer, with the commitment check, under the wallet's public key as public key and staking key, against the note sets it may receive notes in; derivation for ledger-created notes and the notes a program pays in a step consuming a note of the program; records for notes received in the clear.
- Recovery from the seed replays the derivation over the chain, for the public keys and values it can re-derive, and the trial decryption over the ciphertexts still available; the one-time public key and the value of a program payout belong to the records of the wallet when the seed does not give them, and so does a leader reward note, whose nonce is private; a wallet keeps a backup of its records or reads its notes from a layer it can read again from the seed alone.
- Wallet Technical Standard is revision 1.3.0.

## 3. Note Delivery

Mantle gains a Note Delivery subsection under Notes stating that the ledger holds nothing of a note but its commitment, that the notes the ledger creates and the notes a program pays in a step consuming a note of the program derive their nonce from the Operation or the inscription, that the leader of a block chooses the nonce of its reward note, and that the other user notes are delivered off chain, the recommended delivery being the Note Encryption construction through a direct channel or a data availability layer. No Operation, validation rule or encoding changes. Mantle is revision 2.1.1.

# Implementation

- [ ] Add X-Wing (ML-KEM-768 + X25519) to the key management system, with deterministic key generation from a 32-byte seed and the expanded decapsulation key kept in memory.
- [ ] Implement `encrypt_note` and `decrypt_note`: BLAKE2b-256 key derivation, ChaCha20-Poly1305 with the commitment as associated data; check against the test values of the Annex.
- [ ] Derive `sk_enc` and `pk_enc` in the wallet next to the ZK key; expose the two-key address.
- [ ] Wallet discovery by trial decryption of the delivery messages it receives or reads, with the commitment check, and recovery from the seed.
- [ ] Benchmark decapsulation and the scan on the reference machine.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.4.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.3.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.1.1 |
