# COMMON-CRYPTOGRAPHIC-COMPONENTS

| Field | Value |
| --- | --- |
| Name | Common Cryptographic Components |
| Slug | 200 |
| Status | raw |
| Category | Standards Track |
| Editor | Mehmet Gonen <mehmet@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/common-cryptographic-components.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2025-11-18 |
| 1.0.1 | Renamed Nomos to Logos Blockchain | 2026-04-23 |
| 1.0.2 | Clarification of the Poseidon2 function Add test values | 2026-05-07 |
| 1.1.0 | [RFC] Replace the BLAKE2b-Based PRNG with ChaCha20 (ChaCha20Rng) | 2026-08-28 |
| 1.2.0 | Strict EdDSA verification: reject small-order public keys and small-order `R` | 2026-09-22 |
| 1.3.0 | Removed the ZkSignature scheme, no longer used by any Operation. The three-element nullifier uses the hash function mode | 2026-10-07 |
| 1.3.1 | The nullifier key derivation `zkhash(NF_KDF_V1, spending_sk)` uses the compression mode, and the note nullifier hashes the nullifier key | 2026-11-06 |
| 1.4.0 | Added Public-Key Encryption: the X-Wing hybrid KEM and the Note Encryption construction over it, a BLAKE2b key derivation and ChaCha20-Poly1305, which delivers the contents of a note to its holder off chain | 2026-11-02 |

# Introduction

The Logos Blockchain relies on a variety of cryptographic primitives to ensure security, privacy, and verifiability across its components. This document defines the common cryptographic building blocks used throughout the Logos Blockchain design.

Its primary purpose is to standardize the selection and usage of these primitives, provide rationale for each choice, and establish consistency across implementations. It also offers guidance for developers and researchers working on different parts of the system so that all components rely on a coherent and interoperable cryptographic foundation.

# Overview

This document specifies the cryptographic primitives selected for the Logos Blockchain and explains how they interconnect across different layers of the protocol stack. It outlines their technical foundations, rationale, and security considerations to ensure consistent usage across Logos Blockchain components.

The primitives span multiple domains:

- Hash functions (Poseidon2, BLAKE2b) serve as the base layer for commitments, nullifier derivation, Merkle trees, signature key derivation and general purpose hashing.
- The stream cipher (ChaCha20) provides deterministic pseudorandom byte generation and keystream encryption.
- Signature schemes (EdDSA) authenticate messages and participants.
- Proof systems (Groth16) enable succinct and verifiable computation. Groth16 is used in hand-written circuits.
- Public-key encryption (X-Wing with ChaCha20-Poly1305) delivers the contents of a note to its holder, off chain.

Each primitive is chosen for its suitability in a particular context, balancing efficiency, cryptographic strength, and developer usability.

The table below summarizes the recommended component for each context:

| Context | Recommended Component |
| --- | --- |
| ZK Hashing | [Poseidon2](#poseidon2-zk-friendly-hash-function) |
| General Hashing | [BLAKE2b](#blake2bgeneral-purpose-hashing) |
| PRNG & Keystreams | [ChaCha20](#chacha20-based-prng-construction) |
| General Signatures | [EdDSA](#eddsa) |
| Proof System (SNARK) | [Groth16](#groth16-zk-snark) |
| Public-Key Encryption | [X-Wing](#x-wing), [Note Encryption](#note-encryption-construction) |

# 1. Hash Functions

The Logos Blockchain utilizes different hash functions depending on the use case context—primarily distinguishing between zero-knowledge circuit contexts and general usage scenarios. The Logos Blockchain selects hash functions based on their performance characteristics: Poseidon2 for arithmetic-oriented handwritten circuits, and Blake2 for bit-oriented operations in ZkVM and general computations. In specifications, we refer to these arithmetic hash function as zkhash and the general purpose hash function as Hash.

## [BLAKE2b](https://www.blake2.net/blake2.pdf)[(General-Purpose Hashing)](https://eprint.iacr.org/2013/322)

Description:

BLAKE2b is a cryptographic hash function providing strong security and high performance. It supports variable-length outputs through parameterization, making it flexible for different cryptographic contexts.

Technical Details:

- Construction: ARX-based (Addition, Rotation, XOR) design.
- Output Size: Configurable, typically 256-bit or 512-bit.
- Internal State: 64-bit words, utilizing ChaCha-inspired quarter-round operations.
- Performance: Faster than SHA-2/SHA-3 in software implementations.

Use in the Logos Blockchain:

BLAKE2b is used for cryptographic hashing outside of zk-circuits in the Logos Blockchain, such as in data integrity checks, identifier generation, and other non-zk cryptographic operations.

Throughout the Logos Blockchain specifications, BLAKE2b is referred to simply as Hash.

Domain separation tags (DSTs) are included by treating the DST as a byte string (by convention ASCII-compatible) and prefixing it to the input before hashing.

Rationale for Use:

- Proven cryptographic strength as a well-studied and mature construction, with BLAKE2b being a finalist in the NIST SHA-3 competition.
- It was selected because of its high software performance and efficiency compared to SHA-2/SHA-3, while providing comparable security guarantees.
- Its adjustable output length and ARX-based design offer flexibility and practical deployment advantages over the SHA family.

Security Considerations:

- Considered secure under standard cryptanalytic models.
- Resistant to collision, preimage, and second-preimage attacks at intended security levels.

### ChaCha20-Based PRNG Construction

The Logos Blockchain uses the [ChaCha20](https://cr.yp.to/chacha/chacha-20080128.pdf) stream cipher as a deterministic pseudorandom byte generator, suitable for different purposes, including keystream encryption.

Construction:

Given a 32-byte seed, the PRNG output is the ChaCha20 keystream:

```text
PRNG(seed) = ChaCha20Keystream(key = seed, nonce = 0, initial_counter = 0)
```

- ChaCha20 is used in its original variant: 20 rounds, 256-bit key, 64-bit nonce (fixed to zero), 64-bit block counter (starting at zero).
- seed: exactly 32 bytes, used directly as the ChaCha20 key (in the Logos Blockchain protocols, a domain-separated 32-byte BLAKE2b digest). A protocol deriving the seed from longer material MUST truncate it to 32 bytes explicitly before seeding; this construction performs no truncation itself.
- This construction is byte-for-byte the output of `ChaCha20Rng` (Rust crate [`rand_chacha`](https://docs.rs/rand_chacha)) seeded with the key, using the default stream identifier.

Output:

- For generating n bytes, take the first n bytes of the keystream.
- For generating k bits, take enough keystream bytes to cover at least k bits, then truncate the last byte to the required bit-length.

Notes:

- Seed choice and domain separation must be handled at the protocol level.
- A seed MUST NOT be reused across two different generation contexts: with the nonce fixed to zero, keystream security relies on each key producing a single stream.

Interoperability:

- Implementations MAY use the IETF variant of ChaCha20 ([RFC 8439](https://datatracker.ietf.org/doc/html/rfc8439): 32-bit block counter, 96-bit nonce) with the nonce set to zero. With a zero nonce the two variants produce identical keystreams for the first $`2^{32}`$ blocks (256 GiB) of output: the original variant's upper counter word is zero in that range and coincides with the IETF variant's zero nonce words.
- Every use of this construction in the Logos Blockchain generates far less than $`2^{32}`$ blocks per seed, so any RFC 8439 implementation with a zero nonce and an initial counter of zero is byte-for-byte compatible with the definition above.

## [Poseidon2 (](https://eprint.iacr.org/2023/323)[ZK Friendly Hash Function)](https://eprint.iacr.org/2023/323)

Description:

Poseidon2 is a cryptographic sponge permutation that can be used in different modes. It’s often used as a hash function or compression function designed specifically for arithmetic circuits, frequently used in zero-knowledge proofs. It follows the HADES permutation construction, consisting of multiple rounds of full and partial substitution-box (S-box) applications separated by linear layers.

Technical Details:

- Structure: HADES permutation (substitution-permutation network).
- Rounds: Clearly defined full and partial round structure, typically around 8 full rounds and ~60 partial rounds, depending on the security parameter.
- S-box: Nonlinear exponentiation-based S-box, typically of the form $`x \mapsto x^\alpha`$ over a finite field (often $\alpha = 5$ or $\alpha = 3$).
- Field: Operates over prime fields ($`\mathbb{F}_p`$), usually matching the field used in zk-SNARK circuits.

Use in the Logos Blockchain:

Used as the hash function and compression function for all hand-written zero-knowledge circuits (e.g., note commitments, membership proofs) in the Logos Blockchain. For these protocols, the Logos Blockchain relies on the BN254 elliptic curve, so the $`\mathbb{F}_p`$ elements are taken from the prime field corresponding to BN254. The parameters of the Poseidon2 permutation are the following in the Logos Blockchain:

- The rate = 1.
- The capacity = 3.
- 8 external rounds and 56 internal rounds.
- The rounds constants are derived following the original Poseidon paper following their [implementation referenced in the paper](https://extgit.isec.tugraz.at/krypto/hadeshash/-/blob/master/code/generate_params_poseidon.sage?ref_type=heads).
- The state of the sponge is initialized with three 0s.

We provide test values in [Poseidon2 Test Values](#poseidon2-test-values).

We use the 10* padding rule for the hash mode of Poseidon2. Since our rate is 1, this means a single field element with value 1 is appended to the input before absorption.

We modified the compression mode compared to the Poseidon2 paper: to compress two elements (with rate=1), we compute zkhash(a,b) instead of zkhash(a,b) + a.

Throughout the Logos Blockchain specifications, Poseidon2 is referred to as zkhash.

In the Logos Blockchain, bytes and $`\mathbb{F}_p`$ elements are frequently converted between formats (such as when interpreting DST byte strings as Poseidon2 inputs). To convert from an $`\mathbb{F}_p`$ element to bytes, we interpret the little-endian unsigned representation of the $`\mathbb{F}_p`$ number as 32 bytes. Conversely, we can interpret 32 bytes as an $`\mathbb{F}_p`$ element provided the resulting number is smaller than $p$.

> We use Poseidon2 in hash function mode everywhere except in Merkle proofs, public key derivation, the [nullifier key](bedrock-v1.1-mantle-specification.md#keys) derivation `zkhash(NF_KDF_V1, spending_sk)` and the Proof of Quota key nullifier `zkhash(KEY_NULLIFIER_V1, selection_randomness)`, where we use the modified compression mode. The [note nullifier](bedrock-v1.1-mantle-specification.md#note-commitment-and-nullifier) `zkhash(NOTE_NF_V1, commitment, nf_sk)` hashes three elements and uses the hash function mode.

Rationale for Use:

- Optimized for SNARK systems (minimizes constraint amount for hand-written circuit).
- Allows significantly fewer constraints compared to SHA or BLAKE, drastically reducing proving time. Reduces the number of constraints by a factor of approximately 100 compared to SHA256 or BLAKE2b, drastically lowering proving time and computational effort in zero-knowledge circuits.

Security Considerations:

- Subjected to ongoing cryptanalysis, including differential and algebraic attacks.
- Current research demonstrates security at 100-bit+ levels when using recommended round parameters.
- Resistant to collision, preimage, and second-preimage attacks at intended security levels.

## References

- Poseidon2: [https://eprint.iacr.org/2023/323](https://eprint.iacr.org/2023/323)
- Poseidon Cryptanalysis Initiative: [https://www.poseidon-initiative.info/](https://www.poseidon-initiative.info/)
- Algebraic Cryptanalysis of Poseidon: [https://eprint.iacr.org/2023/537](https://eprint.iacr.org/2023/537)
- BLAKE2b Specification: [https://eprint.iacr.org/2013/322](https://eprint.iacr.org/2013/322)

# 2. Digital Signature Schemes

## [EdDSA](https://datatracker.ietf.org/doc/html/rfc8032)

Description:

EdDSA is a digital-signature scheme built on twisted Edwards curves. Ed25519 is a widely used instantiation of EdDSA over the Edwards25519 curve that provides approximately 128 bits of security.

Technical Details:

- Curve: Twisted Edwards curve Edwards25519 (it is birationally equivalent to Curve25519):
  $`(x,y) \in \big(\mathbb{Z}/(2^{255}-19) \mathbb{Z}\big)^2`$ such that $`-x^2 + y^2 = 1 - (121665/121666)x^2y^2`$.
- Signature Size: 64 bytes.
- Public Key Size: 32 bytes.
- Security Level: Approximately 128 bits.
- Operations: Efficient scalar multiplications with Montgomery ladder for constant-time execution.
- Verification: a signature $`(R, S)`$ on a message $`M`$ under the public key $`A`$ is valid only if $`S < \ell`$, neither $`A`$ nor $`R`$ is a point of small order (order 1, 2, 4 or 8), and $`[S]B = R + [k]A`$ with $`k = \text{SHA-512}(R \| A \| M)`$. This is the cofactorless equation of [RFC 8032 §5.1.7](https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.7) with the small-order checks added (`verify_strict` in `ed25519-dalek`).

Use in the Logos Blockchain:

- General-purpose digital signatures: EdDSA is used for authenticating operations in the Logos Blockchain that require standard digital signatures outside of hand-written ZK circuits.

Rationale for Use:

- High-performance, constant-time implementations available.
- Well-studied cryptographic primitives, broadly adopted (e.g., TLS, SSH, blockchain ecosystems).

Security Considerations:

- Standard security assumptions: discrete logarithm hardness on Curve25519.
- Resistant to timing and side-channel attacks due to uniform implementation characteristics.
- Small-order public keys are rejected because anyone can produce a signature under them without knowing a secret key. Honestly generated keys are never of small order. Such a key may still appear where no signature is verified, e.g. the all-zero null key of the Genesis inscription.

## References

- IETF RFC for EdDSA: [https://datatracker.ietf.org/doc/html/rfc8032](https://datatracker.ietf.org/doc/html/rfc8032)
- EdDSA original paper: High-speed high-security signatures. Daniel J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe, Bo-Yin Yang.  [https://eprint.iacr.org/2011/368](https://eprint.iacr.org/2011/368)
- Curve25519: [https://iacr.org/archive/pkc2006/39580209/39580209.pdf](https://iacr.org/archive/pkc2006/39580209/39580209.pdf)

# 3. Proof Systems

## [Groth16 (zk-SNARK)](https://eprint.iacr.org/2016/260.pdf)

Description: Groth16 is a succinct zero-knowledge proof system that allows proving arbitrary statements about computations with very short proofs and fast verification.

Technical Details:

- Proof Size: Approximately 192 bytes per proof (128 bytes if compressed).
- Verification Complexity: Efficient pairing checks (typically ~3 pairing operations).
- Trusted Setup: Required.
- Curve Family: Pairing-friendly elliptic curves (e.g., BN254 or BLS12-381).

Use in the Logos Blockchain:

- Groth16 is the primary zk-SNARK proving system used in Bedrock.

Rationale for Use:

- Produces the shortest possible zk-SNARK proofs, a provably optimal size among practical zk-SNARK constructions.
- Minimal verifier cost makes it highly suitable for on-chain verification in resource-constrained environments.
- Extensive adoption and availability of well-supported libraries.

Security Considerations:

- Groth16 is a zk-SNARK in the Common Reference String (CRS) model. Its knowledge soundness is proved in the generic bilinear group model, under the assumption that the structured CRS was generated honestly and that the trapdoor was destroyed. In practice, producing such a CRS via a one-time multi-party trusted setup ceremony (see [Trusted Setup Ceremony](trusted-setup-ceremony.md)) relies on standard hardness assumptions for the chosen pairing groups and on the at-least-one-honest-participant with secure erasure.
- Groth16’s security has been thoroughly analyzed in the literature, and the protocol is widely used in production zk-blockchain stacks.

## References

- Groth16: [https://eprint.iacr.org/2016/260.pdf](https://eprint.iacr.org/2016/260.pdf)

# 4. Public-Key Encryption

The Logos Blockchain encrypts data to a public key for one purpose: to deliver the contents of a note to its holder. The ledger carries no ciphertext. The scheme is specified so that every wallet opens every ciphertext addressed to it, wherever the ciphertext is delivered.

## [X-Wing](https://datatracker.ietf.org/doc/html/draft-connolly-cfrg-xwing-kem-11)

Description:

X-Wing is a key encapsulation mechanism (KEM) combining ML-KEM-768 and X25519 into one hybrid, post-quantum and traditional, KEM. It is specified in draft-connolly-cfrg-xwing-kem, revision 11 being the one referenced here, and registered for HPKE as `MLKEM768-X25519`.

Technical Details:

- Components: ML-KEM-768 ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) and X25519 ([RFC 7748](https://datatracker.ietf.org/doc/html/rfc7748)).
- Shared secret: $`\text{SHA3-256}(ss_M \| ss_X \| ct_X \| pk_X \| \text{label})`$, 32 bytes, as the draft specifies. The combiner is part of the construction.
- Sizes: encapsulation key 1216 bytes, decapsulation key a 32-byte seed, ciphertext 1120 bytes.
- Security level: NIST level 3 from ML-KEM-768, about 128 bits from X25519.

Use in the Logos Blockchain:

- The key encapsulation of the [Note Encryption Construction](#note-encryption-construction).

Rationale for Use:

- A note ciphertext is kept by whoever serves it, for as long as its holder needs it. A key encapsulation on an elliptic curve alone would let an adversary record the ciphertexts now and decrypt them once a quantum computer exists, exposing the amounts and, through the recomputed commitments, the recipients of every note. The hybrid keeps the security of X25519 if ML-KEM-768 is broken and that of ML-KEM-768 if X25519 is.
- X-Wing is used exactly as specified, so its security proof, its test vectors and its implementations apply as they are.

Security Considerations:

- IND-CCA secure as long as either ML-KEM-768 or X25519 holds.
- Anonymous: a ciphertext reveals nothing about the encapsulation key it is encapsulated to, so two ciphertexts to the same recipient cannot be linked.

### Note Encryption Construction

Description:

The ledger holds only the commitment of a [note](bedrock-v1.1-mantle-specification.md#notes); its holder needs the `value` and the `nonce`, with its public key and the staking key of the note ([Mantle - Keys](bedrock-v1.1-mantle-specification.md#keys)), to recompute the commitment and to spend it. Note Encryption lets the sender of a note encrypt these two fields to the holder's encryption key, bound to the commitment, so that the ciphertext can be handed over through any channel and opened by the holder alone.

Technical Details:

- Key encapsulation: [X-Wing](#x-wing), $`(ct, ss) = \text{Encapsulate}(pk_{\text{enc}})`$.
- Key derivation: $`key = \text{BLAKE2b-256}(\texttt{LOGOS\_NOTE\_ENC\_V1} \| ss \| ct)`$, where $`ss`$ is the shared secret and $`ct`$ the 1120-byte KEM ciphertext.
- Authenticated encryption: ChaCha20-Poly1305 ([RFC 8439](https://datatracker.ietf.org/doc/html/rfc8439)) under $`key`$, with a zero nonce, since every key encrypts exactly once, and the note commitment `commitment` as associated data.
- Plaintext: `value` as 8 bytes little-endian followed by `nonce` as 32 bytes little-endian, 40 bytes. Sealed, 56 bytes with the tag.
- Note ciphertext: the KEM ciphertext followed by the sealed plaintext, `NOTE_CIPHERTEXT_SIZE = 1176` bytes.
- Delivery message: the 32-byte little-endian commitment followed by the note ciphertext, 1208 bytes, so that the recipient has the associated data it opens the ciphertext with.
- Decryption returns `None`, and nothing else, for a ciphertext of another length, a KEM ciphertext X-Wing rejects, or a sealed part that fails to open. X25519 is the function of [RFC 7748](https://datatracker.ietf.org/doc/html/rfc7748) Section 5 as X-Wing specifies it, with no check on an all-zero output: the combiner binds the X25519 ciphertext and public key into the shared secret, so every wallet opens the same messages.

```python
NOTE_CIPHERTEXT_SIZE = 1176

def encrypt_note(pk_enc: XWingEncapsulationKey, commitment: NoteCommitment, value: TokenValue, nonce: NoteNonce) -> bytes:
    (ct, ss) = xwing_encapsulate(pk_enc)
    key = blake2b_256(b"LOGOS_NOTE_ENC_V1" + ss + ct)
    plaintext = value.to_bytes(8, "little") + nonce.to_bytes(32, "little")
    return ct + chacha20poly1305_seal(key, nonce=bytes(12), aad=commitment.to_bytes(32, "little"), plaintext=plaintext)

def decrypt_note(sk_enc: XWingDecapsulationKey, commitment: NoteCommitment, ciphertext: bytes) -> (TokenValue, NoteNonce) | None:
    if len(ciphertext) != NOTE_CIPHERTEXT_SIZE:
        return None
    ct, sealed = ciphertext[:1120], ciphertext[1120:]
    try:
        ss = xwing_decapsulate(sk_enc, ct)
    except Exception:  # a KEM ciphertext X-Wing rejects
        return None
    key = blake2b_256(b"LOGOS_NOTE_ENC_V1" + ss + ct)
    plaintext = chacha20poly1305_open(key, nonce=bytes(12), aad=commitment.to_bytes(32, "little"), ciphertext=sealed)
    if plaintext is None:
        return None
    return (int.from_bytes(plaintext[:8], "little"), int.from_bytes(plaintext[8:], "little"))
```

Use in the Logos Blockchain:

- The recommended delivery of the user notes an Operation creates for another holder, as [Mantle - Note Delivery](bedrock-v1.1-mantle-specification.md#note-delivery) specifies: the sender hands the delivery message over through a direct channel or publishes it on a data availability layer the recipient reads. The recipient decrypts with the key it derives as the [Wallet Technical Standard](wallet-technical-standard.md#note-encryption-key-and-address) specifies, recomputes the commitment from the plaintext and its own public key, as the public key and the staking key of the note unless it asked the sender for another staking key, and keeps the note only if it matches.

Rationale for Use:

- The key derivation is the domain-separated BLAKE2b of the components, and the cipher the ChaCha20 they already use, with the Poly1305 authenticator of RFC 8439.
- The commitment as associated data binds a ciphertext to one note: a ciphertext opens for the commitment it was made for and no other, so it cannot be replayed for another output.

Security Considerations:

- Nothing checks a ciphertext against its commitment before the recipient opens it. A sender publishing a wrong ciphertext only prevents the recipient from learning a note the sender paid for; no other note and no other party is affected.
- What the decapsulation key reveals, and what recovery from the seed covers, is stated in the [Wallet Technical Standard](wallet-technical-standard.md#note-encryption-key-and-address).
- Test values are in the [Annex](#note-encryption-test-values).

## References

- X-Wing: general-purpose hybrid post-quantum KEM, draft-connolly-cfrg-xwing-kem-11. [https://datatracker.ietf.org/doc/html/draft-connolly-cfrg-xwing-kem-11](https://datatracker.ietf.org/doc/html/draft-connolly-cfrg-xwing-kem-11)
- ML-KEM, FIPS 203. [https://csrc.nist.gov/pubs/fips/203/final](https://csrc.nist.gov/pubs/fips/203/final)
- Elliptic Curves for Security, RFC 7748. [https://datatracker.ietf.org/doc/html/rfc7748](https://datatracker.ietf.org/doc/html/rfc7748)
- Post-quantum KEMs for HPKE. [https://datatracker.ietf.org/doc/html/draft-ietf-hpke-pq](https://datatracker.ietf.org/doc/html/draft-ietf-hpke-pq)
- ChaCha20 and Poly1305 for IETF Protocols, RFC 8439. [https://datatracker.ietf.org/doc/html/rfc8439](https://datatracker.ietf.org/doc/html/rfc8439)
- Maram, Xagawa. Post-Quantum Anonymity of Kyber. PKC 2023. [https://eprint.iacr.org/2022/1696](https://eprint.iacr.org/2022/1696)

# Annex

## Poseidon2 Test Values

### Hash Mode

| Input | Output |
| --- | --- |
| [0] | 0x1fed118d9f4466859761f22cad078722b8c4a743b5ebe90443b2dce6bbeb7b23 |
| [1] | 0x1eda5b2807bb78c5d061263409295d5115b7793a68c5220e37ea8ab2e94068f8 |
| [0,0] | 0x20579a2bf857cd36947250ec60f374c1faf02a40130b5fc867c2bde4da940fd2 |
| [1,2] | 0x1f36d032e4a519d0fbe1502fd8e4ad5fad61868c72c03f4294589f506bb52b6b |
| [2,1] | 0x26418d3cada2e7ad9e17b50731f6de916c80fc0ef88ea3ea6520dafbd37f4d7b |
| [1,0,0] | 0x129e88e8d9ae077e2e750222bc131da8b2268ad957cbf83d2b9beed6b9eed7c2 |
| [0,0,1] | 0x2a29cf254d2376ef660166c0647bcbed3decee8b3903eadeebecf304cd404dd0 |
| [0,1,0,1] | 0x793b1db3204a1bbb8cd7d06dac0b8ef98ae2664aa1ed57fccd37baf01682d3d |

### Compression Mode

| Input | Output |
| --- | --- |
| [0,0] | 0x2ed1da00b14d635bd35b88ab49390d5c13c90da7e9e3a5f1ea69cd87a0aa3e82 |
| [1,0] | 0x63c4e8cac9a858304f0035b069255b069288c2af698ececf362cd8ec8c96665 |
| [0,1] | 0x222816f2669279d4c256ed2f196e8b0d54df83d35d61811bac36ea4e858483fc |
| [1,1] | 0x277530b5f2b87dfe4535f43bb1998eda77736b4b05d15d983503566743c88031 |

## Note Encryption Test Values

The values are generated with the `x-wing`, `chacha20poly1305` and `blake2` crates, after checking X-Wing against the vectors of draft-connolly-cfrg-xwing-kem-11, and verified independently from the draft's reference pseudocode. `commitment` and `nonce` are chosen field elements, not Poseidon2 outputs, printed as their 32 little-endian bytes in order; the commitment check of discovery is not covered.

### Note Encryption Key

`sk_enc = BLAKE2b-256(WALLET_ENC_SK_V1 || k_i)`, the X-Wing seed; `pk_enc` its encapsulation key ([Wallet Technical Standard](wallet-technical-standard.md#note-encryption-key-and-address)).

Wallet A:

| Field | Value |
| - | - |
| `k_i` | 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f |
| `sk_enc` | 0x60d398d2a31872058c83c5777043bfecd04ecd94e033cba5bf43e2e5eeaa2b45 |
| `pk_enc` | 0x3f564c29c55841e5c1cc1bb72c913e1c629072433441136706c06431b5760d0074dc1c52d071718c2392896ba0b87979a8019b8ab81cde85710461013a424a9f19886465050ec6076206031da442efd74fed1a4166c27f683251ed462ba5a09ab6867c65e3394db60f0d7cc731aa82e05081b871a113c036e2809cdb95046331ca8c52afd9484ebdf91f87c374392accb6d99a51084eba5c4c9b704e95f6a54254435e84066fab63a0f98ea0393f69ec20618acaa00a44db4103f2e9c9bc2295ae720a5462299028c10ca3ab85b93fd018cb21f7b846b8773fd65fe4b6020c177bceb7687e58ac9c4bc306a35642f68462818828e49ac6a961daf2c33217cd3c014a9f19177fcb2a5788b163704ed58abccc989ed719c2a7e64662434465000a18f6a3b5454fc65617b7e1498127146b50047a20b44f5b2fdf368b40a3061850159da89e467984ef204fbc4a7f99604bd6bacf88bacab32ac238988474c5192a8088b850897c8531139a960226cc9c60b76e1b07cae19ff9445e677625bcac7ca5cb70b901970f5b92597b9e059474327752ef953930462de874425e34812ed0af5776cdc3f5bee2a3abad01c75ff91d3737a96ce4baeb8699929a426d10830796675c05c48b467f1a2c1ebae034599c5814612161b04c8ce76b19ebcd2e0117fe16b196d29866720f0a959759637a878327953acddf398841754797596eeeb07069c89b29150fe7ca1169346b2fa3452fc0baff6c6dad2a90e4750c609b93eeca3da617305e6ace9e684447e0950eb9277abab72c189820f55effaa57fe92b5475412d897cfb0e43b0c941033b74c48115343e6717c9b11ad4c3472b77de2632298ca6da9a4baaceb980f033c6a62027d7988bcb2aab521b7231151351b03138136d12b6b9e362dbd79becb591debb6cf16e5a66380217649b75cc136d7c569e792876803c4fd2a236e67a2fe34067bb7b83da55faa900edb696654c97853a0a684e709af3aa49f64b3b6023efcd75dec41be59e534d0e06778eb43e2b78ef24001b65ab867b92fa2662bb894069704ba5cbb9815ac9354fcb898923a8a6974253562dbb4659443b6b48949c99459bb0c5f1c18952f240a7e8c6c62c3372d4a82fefa7c67544bd85521d8c37b5b0872d63ba34876c2d4d974fddc1a7a09a063331537cb887dd24ecbd41930d9c6ea65096c891555ea6da04c43bf680aa4a9234cc366ad2aac40355a1942bbc8c457aac90e785220e6052f8a739490115023fcb916957f62c07ed43852da3c04ad3404c3c235832b80f1d7177e37471f621b21ac7d25b896af07c1c013009e819d1829305090a9fa002bdc91ccecca1d203ba27449529fa13b676440b596acc97c0d4e814fc094673b448751e89622e2c0d41c50640b758b3794f2a526c23c15830cb626a5630cd29cc985084b8c5b21cb6d3381073d572f2639abfb620e8da2c8f8ca5ef6167b44b6a535117d304447ca28a32b403eedd80e1a14b80367bffb1cb743439086b53b1282465b852f9b542a47ac1479d2aad338c005c59d9c118f8de24424900de4f72daeaacc69b65fa1fc7a65e2586daa5651d5a2d271a6c38281771086a4eb696a774925417edd283976c63315223994570efe8b5e769817bbec0cf5ae0dd87091be2f3c04814d257a99895fca62fa38340a113c0ecda95c3e41fe39d9ef09d09d03e59aedee79ecef0d9d3d |

Wallet B:

| Field | Value |
| - | - |
| `k_i` | 0x202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f |
| `sk_enc` | 0xc855ee56f1ea0ceb1e847f94ec4c98ec5b00d08336089ea07198cb948bb22180 |
| `pk_enc` | 0xaf038a12337daee50b7f538b00a3b6ff305d8b662f6e5c50d61c4e9dc58a3730254a7a0fd728ceaa96880b7533272b34aea1751c43127c9c68f2b572dea06313109f29c99c8c65c7fb20a071d35a52e590137936e5200a79ab83081a356fe3a84410b698604354ea4eb55c32582093cdab04a679798dd5870ec3c3d07b971b7b7dd3f4b02b190f5ce461861684b7b83dd55346eb3b7afb236007a673b5053c3b6763a34c127b2a75738946ac5862068bbe005018213101a2ea54ae15074872a2903b84000046b2922d66530a34411300b3cc5538335b57784e48c132e254bd50a6c2d1c271254720fb3823a70cc390c0ea066ee315952e6c769eb32a5c21b6dc25be5f1b8ae7a4a09c24cd5b9470a9e811266439cec06880d850302b1bca355023476f0c74386dc255bafb53886168ffb2bddc224d30b53eeaeb48fd286fef7ab005bc1df6aa079a58cb69a38609ba87420b019956c874facfb9c85d85541e7f35797599417491835ef29191c596a96a3d3ac1033e1baa52a468c068ad84227ba8d6caa477bc05c785e3d73c069a1c0a6144bb373b743455c93a689f4140d50913ece95570620b03ac57b7366db99b266bb9cd12ca161fac5f0a922a57ab46b2814481f4c10c6c75042c89dae9c5e3797d16d513e1ccb5579b52f6651cecc9a8fc96a27958bb0d56319f29255d23649c2c78c4735fe51b7b1544accb6383a913af422c8c70b95d33e171095954126262ec402dd26a6de5588e8554137482cd04a3393992248e7335eedcad2a03a6dca13d6d96bcb99ca112050b6e2cc506b70774e7c6795ca8d1ec525655555f4c15add51d552ab16fc24450bc2a09489608945c482cbf719b4ada7bb34a8a0ddcecccf73a843fb7a7323179b310806956b850966261bc5414532602d365d4c32ae18466e0f62b0ca81b80d71f93c0c40cdba93030135c585e3661b6c18a4c6c395372140109692bb7f37e11b701ae263072701cfb012976ab99fc3372d018b00c4c7accd42373172d99172747e24417c92ccdf63dbdb9a5638cc0b6b0983d873d97fa362850a05702d08ecaafe3a91158b13e126190f16113ca2ac1d14c3b58f2256e3cabaa4c0a97d1ca41fabd0d6b26d25923a274a18bdc9a8b649def6ba77e9278c1942af98523e46735e4700d25225969345ca7b51b6c98a578f87b1ac15d2f2292c987849e5b46ee590396284f25d584dae20d77ec413e44b8c9da96cc098594f55e2a3c48f3843fc0972af84531bfab757059acff4507de677982e692a40597f34a6d00b259f37c62cf869d1e591bc0e215ba27cfa294649a7b9e4b5c201bc5c156c28da3d19ea335ae153871ff6b376ad278a2e5640de82df5155c926a94e6b52abda717bdab54ec156065f799ff4b7f65242c96d55e2b4a2e9111066c9418c6582a17048fb6b47fedbc6327485a6f892df3d92828e221d508c26c338758fbcfff59c84dd61f66398cda644fe4c15db5691ac1478c2e10480e581e6e17b4557b3f714c5771666af98a9951722a9ebc7ce0eb2905d3cd35d74166737d0b39ac4e7429e5f157f5f5cdd989b536c2abba247716c99505fc4fe963af762ca44c13a7e152082e0c4b363b515e9b417ab303a96f0cff2ff6d16fef93668e1f1bacde5ed26a9fc9f1a5f40f831a97df1903908d2909822cd98929b181828972b13ecab082628f171e29b275bf37ba07af6f2a |

### `encrypt_note`

Every vector encrypts to wallet A. `eseed` is the 64-byte randomness of X-Wing's `EncapsulateDerand`: its first 32 bytes are the ML-KEM-768 message, the last 32 the X25519 ephemeral secret. `plaintext` is `value` (8 bytes, little-endian) followed by `nonce` (32 bytes, little-endian); `commitment` is the associated data; the AEAD nonce is 12 zero bytes. `commitment` and `nonce` are printed as their 32 bytes in order, the little-endian encoding of the field element, exactly as they enter the AEAD and the plaintext, like every other `0x` row of these tables; `value` is a decimal integer. Vector 3 has a nonce that differs from its reverse and a value above $`2^{32}`$.

Vector 1:

| Field | Value |
| - | - |
| `commitment` | 0x1111111111111111111111111111111111111111111111111111111111111111 |
| `value` | 1000000000 |
| `nonce` | 0x2222222222222222222222222222222222222222222222222222222222222222 |
| `plaintext` | 0x00ca9a3b000000002222222222222222222222222222222222222222222222222222222222222222 |
| `eseed` | 0x404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f |
| `ss` | 0x45e0e0fe0cd084f3746a1caa7bbc7e6109b3bad4cc122b1d3df28b64c5660258 |
| `key` | 0xff6a87d3b3de806a4356a76716f12d133911ebf814016a62d8757dbd8f01d026 |
| `kem_ct` | 0x100600c98d97a945a2e2574b40a7e2e8a96aa6fc3c132438fb0cab025f2bc445ac062ce2d8ebd3dc262e6439c9b4fe91977072697f0ace481f71552605ca70d9dffcebc9a04242647ffe33a3becb0000b9bc5937e101ad27b0f572a86b20da81ed7c82f1e6da1fbe93d96ede682ebabe4bf0910129ce462499310f2b2d5a04615b16784c64ad869f5117f5b471f9e13c99b3301619ad7b97c0041797cffd7886f0a4236626ea15037680db1671d18ed2a34525b4a23ff9cabc90f0a8bc33059d10a5a304af56211eea724ed9350438cadc6038baaf34b02bccdffe56b0608ab293149cbf31edbb7fa53ea43947e06889bf6a50281029f8103da6740c3b9cacb84abe24e232b115be8b38196d7dc33befa7ac2e033740dabc454aa4bbaa54af53fdb5287e0c6198f4d3a95392758e558f132857bb189644e16378e9b2da91ca7304e6b4abeb1e35457f8000d898577d83a7404968ecce6af0facf755dc0c9d13569c980fda6bf6ea52841315207fb6902b64981a37aba9a6bcec73b3799629d2286fa5e56f0353f54bc38bd40ca9f30e3e708027db2f0c5ce6a97709fd409f8bfb87b7de4c68bd9930b69790f42722c1fb21fdf3649efd950e3c50354ce30d5fc0e1672a4cb690834701c12d4c88f5c77352d5cf7cec386a74d160a4775a1adf6b5e9c35cf16a23f7feddaf6a269a810892886f6b7c3759f1c2c496c2022c3e43dd22df9e6fdbf1b86f1f98edf9321fabae321505f1831a2a9c26032837792387a32c64b8faf6000751196f744264d0301e95118da3d9bc087f00472b12c025b579a79618ece2caa3007528e4c027f7eef6732c96aa23edebdabc9e82cd80e925524110da4581b412f64a1f8b6f7645ef6fe7063dbf7398a9972f6f0c2ccd40f4ea5ea2b8442b557897c70471ceb477b48bf37b66358fe5a7c97bae778968307e4b2c9b49805c44fc4a1cc2efc94cbf5d3090456f576228e86dfb8de35bda91a19ff14c5ede08463cbbe3ecdba0175b1b8443435f54c07bc442256b67e9f5f5f563387bc09ac16b141ac8a062060ba16ac42282276bde2b972337fdadf7e2f611f37a27e3f899d3026297df261e5c67398f39edc225fd0a00bfb30b8bd5382af3dea7a26d2554f6ecabe275f37945a04b83d98d3634fdbbf4aa1c37c311549d8046e462b4a19db6eeab34ea3b6ca595a0bff079122f0f603d34121d9588c4a7b952428b87ccffa0ce1308d242b71f4313cc893838ca4964de4d43eacf71eb70a58bda5099fab5bb76713f3f5b091c5ebf40c8a8213264cd074847584b4cee5e2fd46195203081a9dc56f56d7668043362741f96575f55fded1c740f15c81f5d6961c05553b5212562ec0a17c5eb0fcbc297e5b6d15652debda6a466ef8f0c77a44523be6a85e4c6cc2475c1d79c705c5a31aed165d448ac3fb0bd742367255a8aeed4ef6402e64e111b1ffad8681c7f009f4943f2c6bd0285cd724a03588912738e3e8523d48c2f20f271352003e6af7b55dd42c9bf3ae0991e64cdcd34760107675dd574ed7789310b3d2e7681f3790b466c773b1521fecf36577958371ea52f |
| `sealed` | 0x87044ae61a27c5e573a0b4d4506c6a6eb47e4806597c8fea17db29f5f41d882954a740534c90809abf01592d0776b6ecc910820a9229dc71 |
| `ciphertext` | 0x100600c98d97a945a2e2574b40a7e2e8a96aa6fc3c132438fb0cab025f2bc445ac062ce2d8ebd3dc262e6439c9b4fe91977072697f0ace481f71552605ca70d9dffcebc9a04242647ffe33a3becb0000b9bc5937e101ad27b0f572a86b20da81ed7c82f1e6da1fbe93d96ede682ebabe4bf0910129ce462499310f2b2d5a04615b16784c64ad869f5117f5b471f9e13c99b3301619ad7b97c0041797cffd7886f0a4236626ea15037680db1671d18ed2a34525b4a23ff9cabc90f0a8bc33059d10a5a304af56211eea724ed9350438cadc6038baaf34b02bccdffe56b0608ab293149cbf31edbb7fa53ea43947e06889bf6a50281029f8103da6740c3b9cacb84abe24e232b115be8b38196d7dc33befa7ac2e033740dabc454aa4bbaa54af53fdb5287e0c6198f4d3a95392758e558f132857bb189644e16378e9b2da91ca7304e6b4abeb1e35457f8000d898577d83a7404968ecce6af0facf755dc0c9d13569c980fda6bf6ea52841315207fb6902b64981a37aba9a6bcec73b3799629d2286fa5e56f0353f54bc38bd40ca9f30e3e708027db2f0c5ce6a97709fd409f8bfb87b7de4c68bd9930b69790f42722c1fb21fdf3649efd950e3c50354ce30d5fc0e1672a4cb690834701c12d4c88f5c77352d5cf7cec386a74d160a4775a1adf6b5e9c35cf16a23f7feddaf6a269a810892886f6b7c3759f1c2c496c2022c3e43dd22df9e6fdbf1b86f1f98edf9321fabae321505f1831a2a9c26032837792387a32c64b8faf6000751196f744264d0301e95118da3d9bc087f00472b12c025b579a79618ece2caa3007528e4c027f7eef6732c96aa23edebdabc9e82cd80e925524110da4581b412f64a1f8b6f7645ef6fe7063dbf7398a9972f6f0c2ccd40f4ea5ea2b8442b557897c70471ceb477b48bf37b66358fe5a7c97bae778968307e4b2c9b49805c44fc4a1cc2efc94cbf5d3090456f576228e86dfb8de35bda91a19ff14c5ede08463cbbe3ecdba0175b1b8443435f54c07bc442256b67e9f5f5f563387bc09ac16b141ac8a062060ba16ac42282276bde2b972337fdadf7e2f611f37a27e3f899d3026297df261e5c67398f39edc225fd0a00bfb30b8bd5382af3dea7a26d2554f6ecabe275f37945a04b83d98d3634fdbbf4aa1c37c311549d8046e462b4a19db6eeab34ea3b6ca595a0bff079122f0f603d34121d9588c4a7b952428b87ccffa0ce1308d242b71f4313cc893838ca4964de4d43eacf71eb70a58bda5099fab5bb76713f3f5b091c5ebf40c8a8213264cd074847584b4cee5e2fd46195203081a9dc56f56d7668043362741f96575f55fded1c740f15c81f5d6961c05553b5212562ec0a17c5eb0fcbc297e5b6d15652debda6a466ef8f0c77a44523be6a85e4c6cc2475c1d79c705c5a31aed165d448ac3fb0bd742367255a8aeed4ef6402e64e111b1ffad8681c7f009f4943f2c6bd0285cd724a03588912738e3e8523d48c2f20f271352003e6af7b55dd42c9bf3ae0991e64cdcd34760107675dd574ed7789310b3d2e7681f3790b466c773b1521fecf36577958371ea52f87044ae61a27c5e573a0b4d4506c6a6eb47e4806597c8fea17db29f5f41d882954a740534c90809abf01592d0776b6ecc910820a9229dc71 |

Vector 2:

| Field | Value |
| - | - |
| `commitment` | 0x030507090b0d0f21232527292b2d2f21232527292b2d2f01030507090b0d0f01 |
| `value` | 0 |
| `nonce` | 0x0000000000000000000000000000000000000000000000000000000000000000 |
| `plaintext` | 0x00000000000000000000000000000000000000000000000000000000000000000000000000000000 |
| `eseed` | 0x808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf |
| `ss` | 0xaf0e799a3c8a9a8127bd0fd7d76fb2ccb49c70d0571a3b42ddf47eac31379ff9 |
| `key` | 0x7a54e2192105af4f3027272bc7195b1bc50e0cfb11d22edbad0dba54cd263ba5 |
| `kem_ct` | 0x879f6939ba920b33569fce8ab10084402166c7632cd149f5855cd5969c6a03a2776b4d7ceff5617b974cabbbc131d732b85f14567ce4aca108d70ae753e36a325c55e7cfba6e13cf026fdc8f58171c2eff8aa04068f2b47822b8a32317029b6c33298add3df10652826ce8a2c51c6a00b90e9b576b6943bc9b2ab58da59efab1ff7f9d49501d68219553b46773f435f3e22e66d08298e501f42a980f6dbd22cf43da22064b21b4e36b524064a19dad45641ccdfccecce2be58434a08c6e2a7ae9e0800efcbd4ad923a6489f99a4a20e2847dd5b918605e4b732a164181595880ff8cfb6fb021f316aaa51f6e1c2a6dbb47a3102d826158b8bb378e8abc6d274d83acf3de220fee1df2b7ea9757f316c4140c33306ec499612f8131c7503a1025e8b499ae822152b3ca0ed0362ff3dd4a4be41c53962a2c0d7959c7e1cb8f10c50962da75ac4e146d608acfed919a812ebc4a75ecc1a800dcb12af8af69b6f6d9d6bd9e08f9c5c758494c36d97d4027ebadcc6ad666955c537ec1384c60095798f1d6b74fe7301f16264df42ab48164cd0ddb52ed0d36dd99c9e271d3ca0d491b9f0aa3d70c57673476f4f15a898792758401bb5c4169c61fb95e51692d5d11728a0a2a31f6e7ee3feaf076a02d87c8dbc08fee44b72726e37074a6705d5408aaa451e84768fb5c5c3b49cff826bcbdd0845ac9cd8b114802dd61416ddbbcf12824a9e267a065a69e60b160642543c1dbf74a55b775ea36a87de54a5ddf9a8e9884fe0fc9c66ea8c90aed508864edea66ac6198d030b481068e34cdc158ec61e63afef942388d35c5135a47bb34e628251f1468f2cbaf42753d4742c7f24d8007b5c6e48df86a2d948b4a7186e1a8f5dbc112ded8e8e9d6680eacd1a88ea0e813c0abc72423dd9fd3555a84f21ce44866d61011f2282e0221b26bcb433634d34ab0d1bc75ae7c5468bb9f442d06894fced8c10f43a7539798eba34e44be0066d5387ad475634de2579579dc79d332edec41260c4e4fef018a7321aa41f50688bd23dbd7e522841265898e4700ba8ea5083059bd34ef970e938989a5722779b88fca252f3b5fbd47c0a8dd2cd776ae9014d3438a8f789599dfd52b608e8ccccdfb4d8b4e7e3718c83e44fc50ac8821672005a5e770afe22b40a1378d839ca1752deaab8efa09c0989c1132e7228270de9f01e3095463acec0544aa31e5bb6cda8709af5e2a27bd65eb377b59a84fb951f52dc260a23bde5b85191a13abb95b01533a7c32ad01b447ff58bccded1c4e75eeba149a15ab501b34e51ecb727c8be55547422db1b2b1c8a7d8f456b7a32549ccb95ed1bcf2c334f12db15d2350ea6abf071e977856ed8576ca2749e618ad2a38365ab02f8c5dbf5e7aea407e7ba689bdc2175966d052e594cb2abbd637e072bbe10b47d37845bf304e8a914681b9a6a649e64fa1f88aab4cc598853f26af48180cba8c790a3017486a58170d19ac02af2cad2e491465f2fcb9be6a6e8ed2e37e0e06cae470dc059b54db6ddf38b6d5e3605a725d2a4adfeeb1a29e17edd621c1b7593ee8cdbc44ac6c4ab6e2f805d23c |
| `sealed` | 0x9ed6f1066df3cf852c93101de292ab8ca91236a8cb3dab754724a0d981d940fdc30a26f51c7f720bb53df517dfe18148284e1520f633cb13 |
| `ciphertext` | 0x879f6939ba920b33569fce8ab10084402166c7632cd149f5855cd5969c6a03a2776b4d7ceff5617b974cabbbc131d732b85f14567ce4aca108d70ae753e36a325c55e7cfba6e13cf026fdc8f58171c2eff8aa04068f2b47822b8a32317029b6c33298add3df10652826ce8a2c51c6a00b90e9b576b6943bc9b2ab58da59efab1ff7f9d49501d68219553b46773f435f3e22e66d08298e501f42a980f6dbd22cf43da22064b21b4e36b524064a19dad45641ccdfccecce2be58434a08c6e2a7ae9e0800efcbd4ad923a6489f99a4a20e2847dd5b918605e4b732a164181595880ff8cfb6fb021f316aaa51f6e1c2a6dbb47a3102d826158b8bb378e8abc6d274d83acf3de220fee1df2b7ea9757f316c4140c33306ec499612f8131c7503a1025e8b499ae822152b3ca0ed0362ff3dd4a4be41c53962a2c0d7959c7e1cb8f10c50962da75ac4e146d608acfed919a812ebc4a75ecc1a800dcb12af8af69b6f6d9d6bd9e08f9c5c758494c36d97d4027ebadcc6ad666955c537ec1384c60095798f1d6b74fe7301f16264df42ab48164cd0ddb52ed0d36dd99c9e271d3ca0d491b9f0aa3d70c57673476f4f15a898792758401bb5c4169c61fb95e51692d5d11728a0a2a31f6e7ee3feaf076a02d87c8dbc08fee44b72726e37074a6705d5408aaa451e84768fb5c5c3b49cff826bcbdd0845ac9cd8b114802dd61416ddbbcf12824a9e267a065a69e60b160642543c1dbf74a55b775ea36a87de54a5ddf9a8e9884fe0fc9c66ea8c90aed508864edea66ac6198d030b481068e34cdc158ec61e63afef942388d35c5135a47bb34e628251f1468f2cbaf42753d4742c7f24d8007b5c6e48df86a2d948b4a7186e1a8f5dbc112ded8e8e9d6680eacd1a88ea0e813c0abc72423dd9fd3555a84f21ce44866d61011f2282e0221b26bcb433634d34ab0d1bc75ae7c5468bb9f442d06894fced8c10f43a7539798eba34e44be0066d5387ad475634de2579579dc79d332edec41260c4e4fef018a7321aa41f50688bd23dbd7e522841265898e4700ba8ea5083059bd34ef970e938989a5722779b88fca252f3b5fbd47c0a8dd2cd776ae9014d3438a8f789599dfd52b608e8ccccdfb4d8b4e7e3718c83e44fc50ac8821672005a5e770afe22b40a1378d839ca1752deaab8efa09c0989c1132e7228270de9f01e3095463acec0544aa31e5bb6cda8709af5e2a27bd65eb377b59a84fb951f52dc260a23bde5b85191a13abb95b01533a7c32ad01b447ff58bccded1c4e75eeba149a15ab501b34e51ecb727c8be55547422db1b2b1c8a7d8f456b7a32549ccb95ed1bcf2c334f12db15d2350ea6abf071e977856ed8576ca2749e618ad2a38365ab02f8c5dbf5e7aea407e7ba689bdc2175966d052e594cb2abbd637e072bbe10b47d37845bf304e8a914681b9a6a649e64fa1f88aab4cc598853f26af48180cba8c790a3017486a58170d19ac02af2cad2e491465f2fcb9be6a6e8ed2e37e0e06cae470dc059b54db6ddf38b6d5e3605a725d2a4adfeeb1a29e17edd621c1b7593ee8cdbc44ac6c4ab6e2f805d23c9ed6f1066df3cf852c93101de292ab8ca91236a8cb3dab754724a0d981d940fdc30a26f51c7f720bb53df517dfe18148284e1520f633cb13 |

Vector 3:

| Field | Value |
| - | - |
| `commitment` | 0x2b20252a2f04090e03080d22272c21262b00050a0f04090e23282d22272c0106 |
| `value` | 1250999896491 |
| `nonce` | 0x05080b0e0104070a0d202326292c2f2225282b2e0104070a0d000306090c0f22 |
| `plaintext` | 0xab8967452301000005080b0e0104070a0d202326292c2f2225282b2e0104070a0d000306090c0f22 |
| `eseed` | 0xc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff |
| `ss` | 0xfae23c8b38eb86b10cffe584198fd942055d59a27e5d94ce340abed761debd43 |
| `key` | 0x47107ada322e1c5f8b9e5901417cd4e23e39a3ad8185c07e46d7a380085d5f78 |
| `kem_ct` | 0xc191305554f3c7af5c760004101a8afc0aed83ed2604521e77f809a13e5fb1e0b3f787d1fedebe345c5b43e87f864fa2cbb7cdb75d26b9b61f9cba07e183f8d3ccb258540b5b7925a4ca55475781ab399a7f137061c0312af7ff00cebbc6228b19c7ddad1adfa29db587ac91b767187791f891f8d5896d956a696ef10ec0eaefbeaf35b87549576f326eced9a649c31cb93f84a048bb39b06a202eff8e5e7ea2383a8bb901dd0559846a12123487ab1bd65078715e77606153b054e2ffcb00b5d643a48fde0b9d92f125216fce9f954f689be0126a1bb001259d0d37a75f691c8b3e83b616f863a004532f1a48b45d00217293f5d3cb267bef3e3fff28b811026c91ec957807e5c4c1cfc38bbeb9daedfe84466541ad65989134db345e286f67c0a785a519a53851af36283144db0f0c79052d0e44bb81577d935874b39eeb8bbeae8a65e32dfc7d85410e79528f572cc374e99f4e06ab34c13d834dd96a383a2dd372bb2e653b0758958e4f975c724c099a509569c9e85d36b54cb57b1f97e9fee5359ba9d1700cc156dd862fd6dc16c7990f597018d18cfded943e288d2c79e3a60c627ead59408f70845b501748f2b59b0a6d4da5099c73b419a4a119abd052543e381cdca49067c501b18ea069c9f0ccaec6b93b8722bebdbca16d1c8b1e277f3935a8088a3f2f7c4380c874762f58fdf271cd496196056fccff747b5c8f104ad7d65dda298ef7cffa26306397c4241767ed8bf3076f30b3563d3dc7e2f015408e76b6eefa8da25bc0bf9eb1f63e7d237c5515d8ca6e42e6f679b190348bc9b56769c253aaaef41fa8b9aee7a7a12ae9ffbecba2dec81d8571e0ebc0213eb212b2231798d4bfee865a6cff854f9d2dd72dd67c74d1868064b4e973c970ad6466d16af4d49dfa6d243e880750a9f377461819ecba2d5b2f9a3c48978c8012248353770c42e71efa6f4d760e0174b5e41bf002fad8e4e8137911f01510538718128a1b68513ac23559f547b642a1bbfbeb48ab182da54b110e829651216d0b22a3fbb43a62d996bdf63096c0895f0286b3e4280ce42f1eadd38f6f21c312569761eb3bf085a5b68b2d30eea36266fd52b86c0a605d2951b8b134ad2a918401de26cc3b1ceba82e4e078b4a1d5bcf453550915c52ff6bfb12980ab1a3f38afb634cb5101c7cb2ecdff31ebfeecdbd3ebb9b44eed2cfb895da9672b40d318d0eab830b43cc2732e0b4ee5eaf6e8373ce12b0dee94871ec83f5a666adc4df65e992cadcee3f5ce9c1ef12bb71c8a8b2c4cc31716ff2599b36d1c21878b7d21d36183da3de96f4a96a88e7c2e9d218f2bc2fadff360d52fb5ade4b6b5279f6f05c7efea252c297910136d6ce51c55b8464b36b02f21f71bc1eedc6870da8773e042814449919a8c1b42f608b1ae124f578aee7f05034f25ebe69370815616d8caabdb4ccb48bdc70003aa1ac1d428b48d53ff3ccc87d8baf4f26b159d067c2d75e5b6682ff49deea6dda8263ae5ab84315d17808ae83727715fa12325cca0a9280736845d54e87de09d6bb114aa7042c50a4a015bd9901d1a0026f5956533a1519 |
| `sealed` | 0x3f326b084cd4972bd1dc16ed0e7446c94da7ce2cc7c28900cb1c649a1ca83f2405c667f85a81374b4d40463742ec8e1a0803b2769581d108 |
| `ciphertext` | 0xc191305554f3c7af5c760004101a8afc0aed83ed2604521e77f809a13e5fb1e0b3f787d1fedebe345c5b43e87f864fa2cbb7cdb75d26b9b61f9cba07e183f8d3ccb258540b5b7925a4ca55475781ab399a7f137061c0312af7ff00cebbc6228b19c7ddad1adfa29db587ac91b767187791f891f8d5896d956a696ef10ec0eaefbeaf35b87549576f326eced9a649c31cb93f84a048bb39b06a202eff8e5e7ea2383a8bb901dd0559846a12123487ab1bd65078715e77606153b054e2ffcb00b5d643a48fde0b9d92f125216fce9f954f689be0126a1bb001259d0d37a75f691c8b3e83b616f863a004532f1a48b45d00217293f5d3cb267bef3e3fff28b811026c91ec957807e5c4c1cfc38bbeb9daedfe84466541ad65989134db345e286f67c0a785a519a53851af36283144db0f0c79052d0e44bb81577d935874b39eeb8bbeae8a65e32dfc7d85410e79528f572cc374e99f4e06ab34c13d834dd96a383a2dd372bb2e653b0758958e4f975c724c099a509569c9e85d36b54cb57b1f97e9fee5359ba9d1700cc156dd862fd6dc16c7990f597018d18cfded943e288d2c79e3a60c627ead59408f70845b501748f2b59b0a6d4da5099c73b419a4a119abd052543e381cdca49067c501b18ea069c9f0ccaec6b93b8722bebdbca16d1c8b1e277f3935a8088a3f2f7c4380c874762f58fdf271cd496196056fccff747b5c8f104ad7d65dda298ef7cffa26306397c4241767ed8bf3076f30b3563d3dc7e2f015408e76b6eefa8da25bc0bf9eb1f63e7d237c5515d8ca6e42e6f679b190348bc9b56769c253aaaef41fa8b9aee7a7a12ae9ffbecba2dec81d8571e0ebc0213eb212b2231798d4bfee865a6cff854f9d2dd72dd67c74d1868064b4e973c970ad6466d16af4d49dfa6d243e880750a9f377461819ecba2d5b2f9a3c48978c8012248353770c42e71efa6f4d760e0174b5e41bf002fad8e4e8137911f01510538718128a1b68513ac23559f547b642a1bbfbeb48ab182da54b110e829651216d0b22a3fbb43a62d996bdf63096c0895f0286b3e4280ce42f1eadd38f6f21c312569761eb3bf085a5b68b2d30eea36266fd52b86c0a605d2951b8b134ad2a918401de26cc3b1ceba82e4e078b4a1d5bcf453550915c52ff6bfb12980ab1a3f38afb634cb5101c7cb2ecdff31ebfeecdbd3ebb9b44eed2cfb895da9672b40d318d0eab830b43cc2732e0b4ee5eaf6e8373ce12b0dee94871ec83f5a666adc4df65e992cadcee3f5ce9c1ef12bb71c8a8b2c4cc31716ff2599b36d1c21878b7d21d36183da3de96f4a96a88e7c2e9d218f2bc2fadff360d52fb5ade4b6b5279f6f05c7efea252c297910136d6ce51c55b8464b36b02f21f71bc1eedc6870da8773e042814449919a8c1b42f608b1ae124f578aee7f05034f25ebe69370815616d8caabdb4ccb48bdc70003aa1ac1d428b48d53ff3ccc87d8baf4f26b159d067c2d75e5b6682ff49deea6dda8263ae5ab84315d17808ae83727715fa12325cca0a9280736845d54e87de09d6bb114aa7042c50a4a015bd9901d1a0026f5956533a15193f326b084cd4972bd1dc16ed0e7446c94da7ce2cc7c28900cb1c649a1ca83f2405c667f85a81374b4d40463742ec8e1a0803b2769581d108 |

### `decrypt_note`

| Case | `sk_enc` | `commitment` | `ciphertext` | Result |
| - | - | - | - | - |
| vector 1 | A | as given | as given | `(1000000000, 0x2222222222222222222222222222222222222222222222222222222222222222)` |
| vector 1, other commitment | A | first byte flipped | as given | `None` |
| vector 1, other wallet | B | as given | as given | `None` |
| vector 1, KEM ciphertext altered | A | as given | first byte flipped | `None` |
| vector 1, tag altered | A | as given | last byte flipped | `None` |
| vector 1, truncated | A | as given | 1175 bytes | `None` |
| vector 1, extended | A | as given | 1177 bytes | `None` |
| vector 2 | A | as given | as given | `(0, 0x0000000000000000000000000000000000000000000000000000000000000000)` |
| vector 2, other commitment | A | first byte flipped | as given | `None` |
| vector 2, other wallet | B | as given | as given | `None` |
| vector 2, KEM ciphertext altered | A | as given | first byte flipped | `None` |
| vector 2, tag altered | A | as given | last byte flipped | `None` |
| vector 2, truncated | A | as given | 1175 bytes | `None` |
| vector 2, extended | A | as given | 1177 bytes | `None` |
| vector 3 | A | as given | as given | `(1250999896491, 0x05080b0e0104070a0d202326292c2f2225282b2e0104070a0d000306090c0f22)` |
| vector 3, other commitment | A | first byte flipped | as given | `None` |
| vector 3, other wallet | B | as given | as given | `None` |
| vector 3, KEM ciphertext altered | A | as given | first byte flipped | `None` |
| vector 3, tag altered | A | as given | last byte flipped | `None` |
| vector 3, truncated | A | as given | 1175 bytes | `None` |
| vector 3, extended | A | as given | 1177 bytes | `None` |
