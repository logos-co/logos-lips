# NOMOS-DIGITAL-SIGNATURE

| Field | Value |
| --- | --- |
| Name | Nomos Digital Signature |
| Slug | 150 |
| Status | raw |
| Category | Standards Track |
| Editor | Jimmy Debe <jimmy@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/blockchain/raw/digital-signature.md) — chore: add math support (#287)
- **2026-01-30** — [`99ca13a`](https://github.com/logos-co/logos-lips/blob/99ca13af02087ff94fabbf3e7fca7cb8e5320f46/docs/blockchain/raw/digital-signature.md) — New RFC: Nomos Digital Signature (#167)

<!-- timeline:end -->

## Abstract

This specification describes the digital signature schemes
used across different components in the Nomos system design.
Throughout the system, each Nomos layer shares the same signature scheme,
ensuring consistent security and interoperability.
The specification covers EdDSA for general-purpose signing
and ZKSignature for zero-knowledge proof of key ownership.

**Keywords:** digital signature, EdDSA, Ed25519, zero-knowledge proof,
ZKSignature, cryptography, elliptic curve, Curve25519

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119][rfc-2119].

### Definitions

| Term | Description |
| ---- | ----------- |
| EdDSA | Edwards-curve Digital Signature Algorithm, a signature scheme based on twisted Edwards curves. |
| Ed25519 | An instance of EdDSA using Curve25519, providing 128-bit security. |
| ZKSignature | A zero-knowledge signature scheme that proves knowledge of a secret key without revealing it. |
| Prover | An entity that generates a cryptographic proof or signature. |
| Verifier | An entity that validates a cryptographic proof or signature. |
| Public Key | The publicly shareable component of a key pair, used for verification. |
| Secret Key | The private component of a key pair, used for signing and proof generation. |

## Background

The Nomos Bedrock consists of a few key components that Nomos Network is built on.
See the [Nomos whitepaper][nomos-whitepaper] for more information.
The Bedrock Mantle component serves as the operating system of Nomos.
This includes facilitating operations like writing data to the blockchain or
a restricted ledger of notes to support payments and staking.
This component also defines how Nomos zones update their state and
the coordination between the Nomos zone executor nodes.
It is like a system call interface designed to provide a minimal set of operations
to interact with lower-level Bedrock services.
It is an execution layer that connects Nomos services
to provide the necessary functionality for sovereign rollups and zones.
See [Common Ledger specification][common-ledger] for more on Nomos zones.

In order for the Bedrock layer to remain lightweight, it focuses on data availability
and verification rather than execution.
Native zones on the other hand will be able to define their state transition function
and prove to the Bedrock layer their correct execution.
The Bedrock layer components share the same digital signature mechanism to ensure security and privacy.
This document describes the validation tools that are used with Bedrock services in the Nomos network.

## Protocol Specification

The signature schemes used by the provers and verifiers include:

- EdDSA Digital Signature Algorithm
- ZKSignature (Zero-Knowledge Signature)

### EdDSA

EdDSA is a signature scheme based on elliptic-curve cryptography,
defined over twisted [Edwards curves][edwards-curves].
Nomos uses the Ed25519 instance with Curve25519,
providing 128-bit security for general-purpose signing.
EdDSA SHOULD NOT be used for ZK circuit construction.

The prover computes the following EdDSA signature using twisted Edwards curve Curve25519:

$$-x^2 + y^2 = 1 - (121665/121666)x^2y^2 \mod{(2^{255} - 19)}$$

- The public key size MUST be 32 bytes.
- The signature size MUST be 64 bytes.
- The public key MUST NOT already exist in the system.

### ZKSignature

The ZKSignature scheme enables a prover to demonstrate cryptographic knowledge of a secret key,
corresponding to a publicly available key,
without revealing the secret key itself.
The following is the structure for a proof attesting public key ownership:

```python
class ZkSignaturePublic:
    public_keys: list[ZkPublicKey]  # The public keys signing the message
    msg: hash                        # The hash of the message
```

The prover knows a witness:

```python
class ZkSignatureWitness:
    # The list of secret keys used to sign the message
    secret_keys: list[ZkSecretKey]
```

Such that the following constraints hold:

1. The number of secret keys is equal to the number of public keys:

```python
assert len(secret_keys) == len(public_keys)
```

1. Each public key is derived from the corresponding secret key:

```python
assert all(
    notes[i].public_key == hash("NOMOS_KDF", secret_keys[i])
    for i in range(len(public_keys))
)
```

- The proof MUST be embedded in the hashed `msg`.

The ZKSignature circuit MUST take a maximum of 32 public keys as inputs.
To prove ownership when using fewer than 32 keys,
the remaining inputs MUST be padded with the public key corresponding
to the secret key `0`.
These padding entries are ignored during execution.
The outputs of the circuit have no size limit,
as they MUST be included in the hashed `msg`.

## Security Considerations

### Key Management

Secret keys MUST be stored securely and never transmitted in plaintext.
Implementations MUST use secure random number generators for key generation.

### EdDSA Security

EdDSA provides 128-bit security when used with Ed25519.
Implementations MUST validate public keys before use to prevent small subgroup attacks.
Signature verification MUST reject malformed signatures.

### ZKSignature Security

The ZKSignature scheme relies on the security of the underlying hash function
and the zero-knowledge proof system.
The hash function used for key derivation (`NOMOS_KDF`) MUST be collision-resistant.
Implementations MUST verify that proofs are well-formed before accepting them.

### Replay Protection

Signatures SHOULD include context-specific data (such as timestamps or nonces)
to prevent replay attacks across different contexts or time periods.

## References

### Normative

- [RFC 2119][rfc-2119] - Key words for use in RFCs to Indicate Requirement Levels

### Informative

- [Nomos whitepaper][nomos-whitepaper] - The Nomos Whitepaper
- [Common Ledger specification][common-ledger] - Common Ledger Specification
- [Edwards curves][edwards-curves] - Twisted Edwards Curves

[rfc-2119]: https://www.ietf.org/rfc/rfc2119.txt
[nomos-whitepaper]: https://nomos-tech.notion.site/The-Nomos-Whitepaper-1fd261aa09df81318690c6f398064efb
[common-ledger]: https://nomos-tech.notion.site/Common-Ledger-Specification-1fd261aa09df81088b76f39cbbe7c648
[edwards-curves]: https://eprint.iacr.org/2008/013.pdf

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
