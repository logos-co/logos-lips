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
| 1.2.0 | Add Equi-X, the asymmetric client puzzle, with its token serialization and effort function | 2026-09-04 |

# Introduction

The Logos Blockchain relies on a variety of cryptographic primitives to ensure security, privacy, and verifiability across its components. This document defines the common cryptographic building blocks used throughout the Logos Blockchain design.

Its primary purpose is to standardize the selection and usage of these primitives, provide rationale for each choice, and establish consistency across implementations. It also offers guidance for developers and researchers working on different parts of the system so that all components rely on a coherent and interoperable cryptographic foundation.

# Overview

This document specifies the cryptographic primitives selected for the Logos Blockchain and explains how they interconnect across different layers of the protocol stack. It outlines their technical foundations, rationale, and security considerations to ensure consistent usage across Logos Blockchain components.

The primitives span multiple domains:

- Hash functions (Poseidon2, BLAKE2b) serve as the base layer for commitments, nullifier derivation, Merkle trees, signature key derivation and general purpose hashing.
- The stream cipher (ChaCha20) provides deterministic pseudorandom byte generation and keystream encryption.
- Signature schemes (EdDSA, ZkSignature) authenticate messages and participants, with ZkSignature designed specifically for ownership verification within zero-knowledge circuits.
- Proof systems (Groth16) enable succinct and verifiable computation. Groth16 is used in hand-written circuits.

Each primitive is chosen for its suitability in a particular context, balancing efficiency, cryptographic strength, and developer usability.

The table below summarizes the recommended component for each context:

| Context | Recommended Component |
| --- | --- |
| ZK Hashing | [Poseidon2](#poseidon2-zk-friendly-hash-function) |
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

# 4. Client Puzzles

## [Equi-X](https://github.com/tevador/equix) [(Asymmetric Client Puzzle)](https://spec.torproject.org/hspow-spec/index.html)

Description:

Equi-X is an asymmetric proof of work: finding a solution for a challenge is expensive, and verifying one is cheap and independent of the difficulty. It is [Equihash](https://eprint.iacr.org/2015/946) with parameters $`n=60`$, $`k=3`$ over [HashX](https://github.com/tevador/hashx), a per-input pseudo-random hash function, as used by the Tor onion-service proof of work ([proposal 327](https://spec.torproject.org/hspow-spec/index.html)).

Technical Details:

- Puzzle input: $`C \| nonce`$, where $`C`$ is the challenge, a byte string set by the verifier, and $`nonce`$ is $`8`$ bytes, little-endian.
- Solution: $`8`$ indices of $`16`$ bits, serialized as each index in little-endian, $`16`$ bytes in total. A solution is valid for a puzzle input when Equi-X verification accepts it for that input.
- Achieved effort: $`\text{effort}(C, nonce, sol) = \lfloor (2^{32}-1) / h_{32} \rfloor`$, where $`h_{32}`$ is the first $`4`$ bytes, big-endian, of the unkeyed BLAKE2b-256 of $`C \| nonce \| sol`$; when $`h_{32} = 0`$ the effort is $`2^{32}-1`$.
- Token: the pair $`(nonce, sol)`$, serialized as the nonce followed by the solution, $`24`$ bytes. A token satisfies an effort target $`d`$ for a challenge $`C`$ when its solution is valid for $`C \| nonce`$ and $`\text{effort}(C, nonce, sol) \geq d`$.
- The expected cost of producing a satisfying token grows linearly with $`d`$. The cost and the size of verifying one are independent of $`d`$.
- Solving needs about $`2`$ MB of working memory per instance; verification does not.

Use in the Logos Blockchain:

Equi-X prices admission at the edge of the Blend network: a core node sets the effort target an edge node must satisfy to be served ([Edge Admission](blend-protocol.md#edge-admission)).

Rationale for Use:

- Verification runs in microseconds and does not grow with the target, so a node under load can raise the price of admission at no cost to itself.
- HashX generates a fresh random program per nonce, so fixed-function hardware cannot bake the hash in; solving remains CPU-bound.
- The token is $`24`$ bytes at every target, so difficulty has no bandwidth consequence.

Security Considerations:

- The puzzle is stateless and nothing in it prevents replay of a valid token. Single-use enforcement is an obligation of the protocol consuming the token.
- Published solve rates are CPU measurements; a deployment must assume headroom for better-optimized solvers.

## References

- [Equi-X reference implementation](https://github.com/tevador/equix)
- [HashX reference implementation](https://github.com/tevador/hashx)
- [Tor onion-service proof of work (proposal 327)](https://spec.torproject.org/hspow-spec/index.html)
- [Equihash](https://eprint.iacr.org/2015/946)

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
