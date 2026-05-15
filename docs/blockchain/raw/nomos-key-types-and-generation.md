# NOMOS-KEY-TYPES-GENERATION

| Field | Value |
| --- | --- |
| Name | Nomos Key Types and Generation |
| Slug | 84 |
| Status | raw |
| Category | Standards Track |
| Editor | Mehmet Gonen <mehmet@logos.co> |
| Contributors | Marcin Pawlowski <marcin@logos.co>, Youngjoon Lee <youngjoon@logos.co>, Alexander Mozeika <alexander@logos.co>, Thomas Lavaur <thomaslavaur@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-key-types-and-generation.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-key-types-and-generation.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document defines the key types used in the Blend protocol
and describes the process of generating them.

**Keywords:** cryptography, keys, Blend, encryption, signing,
NQK, NSK, ESK, NEK, EEK

## Background

The Blend protocol is a mix network protocol
that provides anonymous communication in the Nomos network.
It uses layered encryption and message mixing
to prevent traffic analysis and ensure sender anonymity.
For more details, see [Blend Protocol](#references).

This document ensures that the keys are used and generated in a common manner,
which is necessary for making the Blend protocol work.

**Core nodes** are nodes that participate in the Blend network
by mixing and forwarding messages.
They are registered through the Service Declaration Protocol (SDP)
and store their credentials on the Nomos blockchain ledger.

**Blend messages** are encrypted messages
that are routed through the mix network.
Each message is encapsulated with multiple layers of encryption,
one for each hop in the network.

The keys defined in this specification include:

- **Non-ephemeral Quota Key (NQK)** —
  used for proving that a node is a core node.
- **Non-ephemeral Signing Key (NSK)** —
  used to authenticate the node on the network level
  and derive the Non-ephemeral Encryption Key.
- **Ephemeral Signing Key (ESK)** —
  used for signing Blend messages, one per encapsulation.
- **Non-ephemeral Encryption Key (NEK)** —
  used for deriving shared secrets for message encryption.
- **Ephemeral Encryption Key (EEK)** —
  used for encrypting Blend messages, one per encapsulation.

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Document Structure

This specification is organized into two distinct parts
to serve different audiences and use cases:

**Protocol Specification** contains the normative requirements necessary
for implementing an interoperable Blend Protocol node.
This section defines the cryptographic primitives, message formats,
network protocols, and behavioral requirements that all implementations
must follow to ensure compatibility and maintain the protocol's
privacy guarantees.
Protocol designers, auditors, and those seeking to understand the core
mechanisms should focus on this part.

**Implementation Considerations** provides non-normative guidance
for implementers.
This section offers practical recommendations, optimization strategies,
and detailed examples that help developers build efficient and robust
implementations.
While these details are not required for interoperability,
they represent best practices learned from reference implementations
and can significantly improve performance and reliability.

## Protocol Specification

This section defines the normative cryptographic protocol requirements
for interoperability.

### Construction

#### Non-ephemeral Quota Key

A node generates a Non-ephemeral Quota Key (NQK)
that is a ZkSignature (Zero Knowledge Signature Scheme).
The NQK is stored on the Nomos blockchain ledger
as the `zk_id` field in the `DeclarationInfo`
(see [Service Declaration Protocol](#references))
of the node's outcome of the participation in the
Service Declaration Protocol (SDP).

The NQK is used to prove that the node is part of the set of core nodes
as indicated through the SDP.

**Properties:**

- **Type**: ZkSignature (Zero Knowledge Signature Scheme)
- **Storage**: Nomos blockchain ledger (`zk_id` field in `DeclarationInfo`)
- **Purpose**: Prove core node membership
- **Lifecycle**: Non-ephemeral (persistent across sessions)

#### Non-ephemeral Signing Key

A node generates a Non-ephemeral Signing Key (NSK)
using the Ed25519 algorithm (see [RFC 8032](#references)).
The NSK is stored on the Nomos blockchain ledger
as the `provider_id` field in the `DeclarationInfo`
(see [Service Declaration Protocol](#references))
of the node's outcome of the participation in the
Service Declaration Protocol (SDP).

The NSK is used to authenticate the node on the network level
and to derive the Non-ephemeral Encryption Key.

**Properties:**

- **Type**: Ed25519 (see [RFC 8032](#references))
- **Storage**: Nomos blockchain ledger (`provider_id` field in `DeclarationInfo`)
- **Purpose**:
  - Network-level node authentication
  - Derivation of Non-ephemeral Encryption Key (NEK)
- **Lifecycle**: Non-ephemeral (persistent across sessions)

#### Ephemeral Signing Key

A node generates Ephemeral Signing Keys (ESK) that are proved to be limited
in number by the Proof of Quota (PoQ).
The PoQ for core nodes requires a valid NQK for the session for which the
PoQ is generated.

A unique signing key MUST be generated for every encapsulation as required
by the Message Encapsulation Mechanism.

**Properties:**

- **Type**: Ed25519
- **Quantity**: Limited by Proof of Quota (PoQ)
- **Requirements**: Valid NQK for the session
- **Purpose**: Signing Blend messages
- **Lifecycle**: Ephemeral (one per encapsulation)

**Security Requirements:**

- The key MUST NOT be reused.
  Otherwise, the messages that reuse the same key can be linked together.
- The node is responsible for not reusing the key.
- A unique signing key MUST be generated for every encapsulation.

#### Non-ephemeral Encryption Key

A node generates a Non-ephemeral Encryption Key (NEK).
It is an X25519 curve key (see [RFC 7748](#references))
derived from the NSK (Ed25519) public key retrieved from the `provider_id`,
which is stored on the Nomos blockchain ledger
when the node executes the SDP protocol.

The NEK key is used for deriving a shared secret
(alongside EEK defined below) for the Blend message encapsulation purposes.

**Properties:**

- **Type**: X25519 (see [RFC 7748](#references))
- **Derivation**: Derived from NSK (Ed25519) public key
- **Source**: `provider_id` field from Nomos blockchain ledger
- **Purpose**: Deriving shared secrets for message encryption
- **Lifecycle**: Non-ephemeral (persistent across sessions)

**Derivation Process:**

1. Retrieve NSK (Ed25519) public key from `provider_id` on Nomos blockchain ledger
2. Derive X25519 curve key from Ed25519 public key
3. Use resulting NEK for shared secret derivation

#### Ephemeral Encryption Key

A node derives an Ephemeral Encryption Key (EEK) pair
using the X25519 curve (see [RFC 7748](#references)) from the ESK.

A unique encryption key MUST be generated for every encapsulation
as required by the Message Encapsulation Mechanism.

**Properties:**

- **Type**: X25519 (see [RFC 7748](#references))
- **Derivation**: Derived from ESK (Ed25519)
- **Purpose**: Encrypting Blend messages
- **Lifecycle**: Ephemeral (one per encapsulation)

**Shared Secret Derivation:**

The derivation of a shared secret for the encryption of an encapsulated
message requires:

- **Sender**: EEK (Ephemeral Encryption Key of sender)
- **Recipient**: X25519 key derived from NEK
  (Non-ephemeral Encryption Key of recipient)

The shared secret is computed using the X25519 Diffie-Hellman key exchange
between the sender's EEK and the recipient's derived NEK.

### Security Considerations

#### Key Reuse

- **CRITICAL**: Ephemeral keys (ESK, EEK) MUST NOT be reused across
  different encapsulations
- Key reuse enables message linking, breaking anonymity guarantees
- Implementations MUST enforce unique key generation per encapsulation

#### Key Derivation

- NEK derivation from NSK MUST use standard Ed25519 to X25519 conversion
- EEK derivation from ESK MUST use standard Ed25519 to X25519 conversion
- Derivations MUST be deterministic for the same input

#### Proof of Quota

- ESK generation MUST be limited by valid Proof of Quota (PoQ)
- PoQ MUST include valid NQK for the current session
- Implementations MUST verify PoQ before accepting ephemeral signatures

#### Ledger Storage

- NQK and NSK MUST be retrievable from Nomos blockchain ledger via SDP protocol
- Ledger data MUST be integrity-protected
- Implementations SHOULD verify ledger data authenticity before use

## Implementation Considerations

This section provides guidance for implementing the protocol specification.

### Key Hierarchy Summary

```text
┌─────────────────────────────────────────────────────────────┐
│              Nomos Blockchain Ledger (SDP Protocol)         │
├─────────────────────────────────────────────────────────────┤
│  DeclarationInfo:                                           │
│    - zk_id: NQK (ZkSignature)                              │
│    - provider_id: NSK (Ed25519)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Derivation
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Non-ephemeral Keys (Persistent)            │
├─────────────────────────────────────────────────────────────┤
│  NQK (ZkSignature) ──► Proves core node membership          │
│  NSK (Ed25519)     ──► Network authentication               │
│  NEK (X25519)      ──► Derived from NSK for encryption      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Per-encapsulation
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Ephemeral Keys (Per Encapsulation)             │
├─────────────────────────────────────────────────────────────┤
│  ESK (Ed25519) ──► Signs Blend messages (via PoQ + NQK)     │
│  EEK (X25519)  ──► Derived from ESK for encryption          │
└─────────────────────────────────────────────────────────────┘
```

### Key Usage Matrix

| Key Type | Algorithm | Storage | Lifecycle | Primary Use | Derived From |
| -------- | --------- | ------- | --------- | ----------- | ------------ |
| **NQK** | ZkSignature | Nomos blockchain (`zk_id`) | Non-ephemeral | Core node proof | Generated |
| **NSK** | Ed25519 | Nomos blockchain (`provider_id`) | Non-ephemeral | Authentication | Generated |
| **NEK** | X25519 | Derived | Non-ephemeral | Shared secret derivation | NSK public key |
| **ESK** | Ed25519 | Memory | Ephemeral | Message signing | Generated (PoQ-limited) |
| **EEK** | X25519 | Memory | Ephemeral | Message encryption | ESK |

### Implementation Requirements

Implementations of this specification MUST:

1. Generate NQK as ZkSignature and store in `DeclarationInfo.zk_id`
2. Generate NSK as Ed25519 and store in `DeclarationInfo.provider_id`
3. Derive NEK from NSK using Ed25519 to X25519 conversion
4. Generate unique ESK per encapsulation, limited by PoQ
5. Derive EEK from ESK using Ed25519 to X25519 conversion
6. Never reuse ephemeral keys across encapsulations
7. Verify PoQ includes valid NQK before generating ESK

Implementations SHOULD:

1. Securely erase ephemeral keys after use
2. Implement key generation auditing
3. Validate all derived keys before use
4. Monitor for key reuse attempts

### Best Practices

#### Secure Key Management

- Store non-ephemeral keys in secure storage
  (HSM, secure enclave, or encrypted memory)
- Implement secure key erasure for ephemeral keys immediately after use
- Use constant-time operations for key comparisons to prevent timing attacks

#### Operational Security

- Log key generation events (without logging key material)
- Monitor for anomalous key usage patterns
- Implement rate limiting on key generation to prevent resource
  exhaustion
- Regularly audit key lifecycle management

## References

### Normative

- Blend Protocol - Mix network protocol for anonymous communication in Nomos
- Service Declaration Protocol (SDP) - Protocol for registering core nodes
  and storing `DeclarationInfo` on the Nomos blockchain ledger
- Proof of Quota Specification (PoQ)
- Message Encapsulation Mechanism
- Zero Knowledge Signature Scheme (ZkSignature)

### Informative

- [Key Types and Generation Specification](https://nomos-tech.notion.site/Key-Types-and-Generation-Specification-215261aa09df81088b8fd7c3089162e8)
  \- Original Key Types and Generation documentation
- [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) - Edwards-Curve Digital Signature Algorithm (EdDSA)
- [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748) - Elliptic Curves for Security (X25519)
- Ed25519 to Curve25519 conversion: Standard practice for deriving X25519 keys from Ed25519 keys

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
