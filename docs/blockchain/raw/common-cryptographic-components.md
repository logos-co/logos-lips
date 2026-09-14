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
| 1.1.0 | Replace the BLAKE2b-Based PRNG with ChaCha20 (ChaCha20Rng) | 2026-08-28 |
| 1.2.0 | Added Rescue-Prime Optimized over the Goldilocks field as the STARK-field hash function (`starkhash`), with test values | 2026-09-07 |

# Introduction

The Logos Blockchain relies on a variety of cryptographic primitives to ensure security, privacy, and verifiability across its components. This document defines the common cryptographic building blocks used throughout the Logos Blockchain design.

Its primary purpose is to standardize the selection and usage of these primitives, provide rationale for each choice, and establish consistency across implementations. It also offers guidance for developers and researchers working on different parts of the system so that all components rely on a coherent and interoperable cryptographic foundation.

# Overview

This document specifies the cryptographic primitives selected for the Logos Blockchain and explains how they interconnect across different layers of the protocol stack. It outlines their technical foundations, rationale, and security considerations to ensure consistent usage across Logos Blockchain components.

The primitives span multiple domains:

- Hash functions (Poseidon2, Rescue-Prime Optimized, BLAKE2b) serve as the base layer for commitments, nullifier derivation, Merkle trees, signature key derivation and general purpose hashing.
- The stream cipher (ChaCha20) provides deterministic pseudorandom byte generation and keystream encryption.
- Signature schemes (EdDSA, ZkSignature) authenticate messages and participants, with ZkSignature designed specifically for ownership verification within zero-knowledge circuits.
- Proof systems (Groth16) enable succinct and verifiable computation. Groth16 is used in hand-written circuits.

Each primitive is chosen for its suitability in a particular context, balancing efficiency, cryptographic strength, and developer usability.

The table below summarizes the recommended component for each context:

| Context | Recommended Component |
| --- | --- |
| ZK Hashing | [Poseidon2](#poseidon2-zk-friendly-hash-function) |
| STARK-Field Hashing | [Rescue-Prime Optimized](#rescue-prime-optimized-stark-field-hash-function) |
| General Hashing | [BLAKE2b](#blake2bgeneral-purpose-hashing) |
| PRNG & Keystreams | [ChaCha20](#chacha20-based-prng-construction) |
| General Signatures | [EdDSA](#eddsa) |
| ZK Signatures | [ZkSignature](#zksignature-zero-knowledge-signature) (see [Mantle - Zero Knowledge Signature Scheme (ZkSignature)](bedrock-v1.1-mantle-specification.md)) |
| Proof System (SNARK) | [Groth16](#groth16-zk-snark) |

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

Used as the hash function and compression function for all hand-written zero-knowledge circuits (e.g., note IDs, membership proofs) in the Logos Blockchain. For these protocols, the Logos Blockchain relies on the BN254 elliptic curve, so the $`\mathbb{F}_p`$ elements are taken from the prime field corresponding to BN254. The parameters of the Poseidon2 permutation are the following in the Logos Blockchain:

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

> We use Poseidon2 in hash function mode everywhere except in: Merkle proofs, public key derivation, nullifier derivation and reward voucher derivation where we use the modified compression mode.

Rationale for Use:

- Optimized for SNARK systems (minimizes constraint amount for hand-written circuit).
- Allows significantly fewer constraints compared to SHA or BLAKE, drastically reducing proving time. Reduces the number of constraints by a factor of approximately 100 compared to SHA256 or BLAKE2b, drastically lowering proving time and computational effort in zero-knowledge circuits.

Security Considerations:

- Subjected to ongoing cryptanalysis, including differential and algebraic attacks.
- Current research demonstrates security at 100-bit+ levels when using recommended round parameters.
- Resistant to collision, preimage, and second-preimage attacks at intended security levels.

## [Rescue-Prime Optimized (](https://eprint.iacr.org/2022/1577)[STARK-Field Hash Function)](https://eprint.iacr.org/2022/1577)

Description:

Rescue-Prime Optimized (RPO) is an arithmetization-oriented sponge hash function of the Rescue family, defined over the Goldilocks prime field. It is designed to be cheap to prove in STARK-based proof systems, where the cost of a hash is driven by the number of rounds rather than by the number of multiplications. Every round applies a power-map S-box in its first half and the inverse power map in its second half, so the permutation has a low-degree description in both directions.

Technical Details:

- Field: the Goldilocks prime field $`\mathbb{F}_q`$ with $`q = 2^{64} - 2^{32} + 1`$.
- Structure: sponge over a state of $`m = 12`$ field elements, with capacity $`c = 4`$ (positions 0–3) and rate $`r = 8`$ (positions 4–11).
- Rounds: 7. Each round is an MDS matrix multiplication, a round-constant addition, the S-box $`x \mapsto x^{7}`$ on every state element, a second MDS multiplication, a second round-constant addition and the inverse S-box $`x \mapsto x^{1/7}`$. The exponent 7 is the smallest integer coprime with $`q - 1`$.
- Digest: the four rate elements at positions 4–7, i.e. 256 bits.
- Security level: 128 bits classical (collision and preimage), as claimed by the RPO specification for these parameters. Against a quantum adversary the generic bounds of a 256-bit digest apply: $`2^{128}`$ for preimage (Grover) and $`2^{85}`$ for collision (BHT, with a matching quantum-memory requirement that makes it impractical); no quantum speed-up of the algebraic attacks on the Rescue family is known.
- MDS matrix and round constants: those fixed by the RPO specification for $`(m, c) = (12, 4)`$ at the 128-bit level; they are not restated here and MUST be taken from the specification or from a reference implementation that reproduces its test vectors.

Use in the Logos Blockchain:

RPO is the hash function of the STARK-field keys: the `stark_public_key` of a `Note` ([Mantle - Notes](bedrock-v1.1-mantle-specification.md#notes)) and the `stark_zk_id` of a service declaration ([Service Declaration Protocol](bedrock-service-declaration-protocol.md#declaration-storage)) are RPO digests, derived as the [Wallet Technical Standard](wallet-technical-standard.md#stark-field-key-derivation) specifies. No circuit evaluates RPO; wallets compute it when deriving keys and nodes only parse its digests. Throughout the Logos Blockchain specifications RPO is referred to as `starkhash`.

`starkhash` takes a list of Goldilocks field elements and returns four:

1. Initialize the state to twelve zeros, then set the first capacity element (position 0) to the number of input elements modulo 8.
2. Absorb the input eight elements at a time, writing each element over the rate positions 4–11 in order (overwrite mode, the element replaces the value held there), and apply the permutation after every full block of eight.
3. If the number of input elements is not a multiple of eight, write the remaining elements over positions 4, 5, …, set the rate positions left to zero and apply the permutation once more. No padding element is appended: the capacity value set in step 1 separates inputs of different lengths.
4. Return the state elements at positions 4–7.

This is the `hash_elements` procedure of the RPO specification and of its reference implementation. An empty input runs no permutation and returns four zeros; `starkhash` is never applied to one, every input starting with a domain separation tag. Some libraries have since moved the rate to positions 0–7 and the capacity to 8–11 with the same permutation, which yields different digests: an implementation MUST follow the layout above and reproduce the [Rescue-Prime Optimized Test Values](#rescue-prime-optimized-test-values).

Domain separation tags are byte strings (ASCII by convention) converted to field elements by `dst_elements`: the string is zero-padded on the right to a multiple of 8 bytes and every 8-byte block is read as a little-endian unsigned integer. The most significant byte of an ASCII block is below `0x80`, so every value is below $`2^{63} \lt q`$ and canonical. The elements of the tag are the first inputs of `starkhash`. Every tag used under `starkhash` carries the `STARK_` prefix and its own `_V1` suffix (`STARK_KDF_V1`, `STARK_WALLET_SK_V1`).

```python
def dst_elements(tag: bytes) -> list[GoldilocksElement]:
    tag = tag + b"\x00" * (-len(tag) % 8)
    return [int.from_bytes(tag[i:i + 8], "little") for i in range(0, len(tag), 8)]
```

We provide test values in [Rescue-Prime Optimized Test Values](#rescue-prime-optimized-test-values).

Bytes and Goldilocks elements are converted as follows: an element is serialized as 8 bytes little-endian, and 8 bytes are a valid element only if their value is strictly smaller than $`q`$ (canonical form). A `StarkPublicKey` ([Mantle Transaction Encoding](mantle-transaction-encoding.md#common-structures)) is the 32-byte serialization of a four-element digest, and every rule that parses one rejects a non-canonical element.

Rationale for Use:

- Native to the Goldilocks field of STARK-based proof systems, so a key derived today can be proven natively in one, without emulating a foreign field inside a circuit.
- Rescue-family designs need few rounds, which is what STARK proving cost tracks; RPO fixes concrete parameters with public reference implementations and test vectors.
- A four-element digest is 256 bits, the size of a `ZkPublicKey`, so a STARK-field key costs the same 32 bytes on the wire and in the ledger.

Security Considerations:

- The 128-bit claim rests on the algebraic cryptanalysis of the Rescue family (Gröbner basis and interpolation attacks); RPO includes a security margin above the minimal round count and remains under analysis in the STARK ecosystem.
- Keys derived with `starkhash` are hash-based: their security against a quantum adversary reduces to preimage resistance, exactly as for the Poseidon2-based keys.
- The field and the hash are a protocol-wide commitment. Because notes commit to STARK-field keys from the start, changing either after the network launches would require a key migration; the choice must be made together with the proof-system roadmap.

## References

- Poseidon2: [https://eprint.iacr.org/2023/323](https://eprint.iacr.org/2023/323)
- Rescue-Prime Optimized: [https://eprint.iacr.org/2022/1577](https://eprint.iacr.org/2022/1577)
- Rescue-Prime: [https://eprint.iacr.org/2020/1143](https://eprint.iacr.org/2020/1143)
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

Use in the Logos Blockchain:

- General-purpose digital signatures: EdDSA is used for authenticating operations in the Logos Blockchain that require standard digital signatures outside of hand-written ZK circuits.

Rationale for Use:

- High-performance, constant-time implementations available.
- Well-studied cryptographic primitives, broadly adopted (e.g., TLS, SSH, blockchain ecosystems).

Security Considerations:

- Standard security assumptions: discrete logarithm hardness on Curve25519.
- Resistant to timing and side-channel attacks due to uniform implementation characteristics.

## [ZkSignature (Zero-Knowledge Signature)](bedrock-v1.1-mantle-specification.md)

Description:

The ZkSignature scheme enables a prover to demonstrate cryptographic knowledge of a secret key corresponding to a publicly available key, without revealing the secret key itself. Specifically designed for efficient verification within zero-knowledge circuits, it provides both authentication and privacy, binding proofs securely to particular messages.

Technical Details:

Public Parameters:

- Public Key:
    A cryptographic commitment derived from the secret key using a secure collision-resistant hash function. This public key acts as a verifier’s reference to authenticate the prover without disclosing secrets.
- Message Hash:
    A cryptographic hash of the specific message intended to be signed. Binding the proof directly to this hash ensures that the signature is valid only for this exact message, providing protection against replay attacks and unauthorized reuse.

Private Parameters (Witness):

- Secret Key:
    A securely generated secret scalar value that must remain confidential. The secret key serves as the prover’s private witness input within the zero-knowledge circuit.

Security Level:

The security level of a ZKSignature depends on the concrete instantiations of its underlying primitives—namely the hash function, the zero-knowledge proof system, and the elliptic curve used. Since different instantiations may offer varying security guarantees and may be evaluated under different metrics (e.g., soundness, knowledge extraction, or cryptanalytic resistance), we do not commit to a fixed bit-level security.

The zk-circuit enforcing the validity of ZkSignature imposes the following conditions through arithmetic constraints:

- Key Ownership Constraint:
    The prover must demonstrate that they possess the secret key corresponding precisely to the provided public key. Within the circuit, this is validated by recomputing the public key using the secret key and the specified cryptographic hash function, then checking equivalence with the given public key.
- Message Binding Constraint:
    The signature is explicitly tied to a particular message by embedding its cryptographic hash into the circuit constraints. As a result, the zk-proof validity inherently ensures the prover’s knowledge of the secret key specifically with respect to this message.

Use in the Logos Blockchain:

ZkSignature is used to sign every object that are linked at some point to a hand-written circuit and if the signature is included in a bigger circuit.

Rationale for Use:

- Critically, the proof generation is fast, allowing rapid transaction processing and state updates in the Logos Blockchain without bottlenecks, which is essential for scalable systems.
- Allows anonymous and secure verification of message ownership within zero-knowledge circuits.
- Efficiently verifiable with minimal constraints in zk-SNARK circuits, ensuring performance in cryptographic operations.

Security Considerations:

- Dependent on the security properties (collision resistance and preimage resistance) of the default [hash function](#poseidon2-zk-friendly-hash-function) for zk-circuits utilized for key derivation and verification.
- Robust against signature forgery, replay attacks, and impersonation, assuming the correct implementation of constraints and binding to the specific message hash.

## References

- IETF RFC for EdDSA: [https://datatracker.ietf.org/doc/html/rfc8032](https://datatracker.ietf.org/doc/html/rfc8032)
- EdDSA original paper: High-speed high-security signatures. Daniel J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe, Bo-Yin Yang.  [https://eprint.iacr.org/2011/368](https://eprint.iacr.org/2011/368)
- Curve25519: [https://iacr.org/archive/pkc2006/39580209/39580209.pdf](https://iacr.org/archive/pkc2006/39580209/39580209.pdf)
- ZkSignature: [Mantle - Zero Knowledge Signature Scheme (ZkSignature)](bedrock-v1.1-mantle-specification.md)​

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

## Rescue-Prime Optimized Test Values

`starkhash` over Goldilocks elements, with the digest given as its four elements and as the 32-byte serialization (each element 8 bytes little-endian). Generated with the permutation constants of the RPO reference implementation and cross-checked against the `hash_elements` test vectors of miden-crypto 0.13 (capacity-first layout, as specified here).

### starkhash

| Input | Output (elements) | Output (serialized) |
| --- | --- | --- |
| [0] | [18126731724905382595, 7388557040857728717, 14290750514634285295, 7852282086160480146] | 0xc302cad976168ffbcd46097f7b6d8966efe0819ee0f152c69237c245f4e8f86c |
| [1] | [3846236276142386450, 5034591595140902852, 4565868838168209231, 6740431856120851931] | 0x122db0d183936035c46f8aa16176de454fa70a6e84395d3fdb6dcf900fd38a5d |
| [0,1,2,3,4,5,6,7] | [2242391899857912644, 12689382052053305418, 235236990017815546, 5046143039268215739] | 0x44833e5e8d931e1f4ac8dabfbebd19b0fa430bcccbba4303bb5b64cd5b800746 |
| [0,1,2,3,4,5,6,7,8] | [5218076004221736204, 17169400568680971304, 8840075572473868990, 12382372614369863623] | 0x0c55a0b27a546a48287c9e8ed9f645eebeb2e97ce541ae7ac7670ac44906d7ab |

### dst_elements

| Tag | Elements |
| --- | --- |
| `STARK_WALLET_SK_V1` | [4708336712546341971, 6866673725757279308, 12630] |
| `STARK_KDF_V1` | [4921131794939597907, 827744070] |

The [Wallet Technical Standard](wallet-technical-standard.md#stark-field-key-derivation) gives an end-to-end STARK-field key derived from a fixed leaf with these two tags.
