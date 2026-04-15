# NOMOS-MESSAGE-FORMATTING

| Field | Value |
| --- | --- |
| Name | Nomos Message Formatting Specification |
| Slug | 89 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski |
| Contributors | Youngjoon Lee <youngjoon@status.im>, Alexander Mozeika <alexander.mozeika@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-message-formatting.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-message-formatting.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document specifies the Message Formatting for the Blend Protocol.
The Message contains a header and a payload,
where the header informs the protocol about the version and the payload type.
The Message contains either a drop or a non-drop payload,
with fixed-length payloads to prevent adversaries from
distinguishing message types based on length.
This specification reuses notation from the Notation document
and integrates with the Message Encapsulation Mechanism.

**Keywords:** Blend, message formatting, header, payload, drop, non-drop

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## Document Structure

This specification is organized into two distinct parts
to serve different audiences and use cases:

**Protocol Specification** contains the normative requirements
necessary for implementing an interoperable Blend Protocol node.
This section defines the cryptographic primitives, message formats, network protocols,
and behavioral requirements that all implementations MUST follow
to ensure compatibility and maintain the protocol's privacy guarantees.
Protocol designers, auditors,
and those seeking to understand the core mechanisms should focus on this part.

**Implementation Details** provides non-normative guidance for implementers.
This section offers practical recommendations, optimization strategies,
and detailed examples that help developers build efficient and robust implementations.
While these details are not required for interoperability,
they represent best practices learned from reference implementations
and can significantly improve performance and reliability.

## Protocol Specification

### Construction

#### Message

The Message is a structure that contains a public_header, private_header and a payload.

```python
class Message:
    public_header: PublicHeader
    private_header: PrivateHeader
    payload: bytes
```

#### Public Header

The public_header must be generated as the outcome of the Message Encapsulation Mechanism.

The public_header is defined as follows:

```python
class PublicHeader:
    version: byte
    public_key: PublicKey
    proof_of_quota: ProofOfQuota
    signature: Signature
```

**Fields:**

- version=0x01 is version of the protocol.
- public_key is $K^{n}_{i}$,
  a public key from the set $\mathbf{K}^{n}_{h}$
  as defined in the Message Encapsulation spec.
- proof_of_quota is $\pi^{K^{n}_{i}}_{Q}$,
  a corresponding proof of quota for the key $K^{n}_{i}$ from the $\mathbf{K}^{n}_{h}$;
  it also contains the key nullifier.
- signature is $\sigma_{K^{n}_{i}}(\mathbf{h|P}_{i})$,
  a signature of the concatenation of the $i$-th encapsulation
  of the payload $\mathbf{P}$ and the private header $\mathbf{h}$,
  that can be verified by the public key $K^{n}_{i}$.

#### Private Header

The private_header must be generated as the outcome of
the Message Encapsulation Mechanism.

The private header contains a set of encrypted BlendingHeader entries
$\mathbf{h} = (\mathbf{b}_{1},...,\mathbf{b}_{h_{max}})$.

```python
private_header: list[BlendingHeader]
```

The size of the set is limited to $\beta_{max}=3$ BlendingHeader entries,
as defined in the Global Parameters.

**Blending Header:**

The BlendingHeader ($\mathbf{b}_{l}$) is defined as follows:

```python
class BlendingHeader:
    public_key: PublicKey
    proof_of_quota: ProofOfQuota
    signature: Signature
    proof_of_selection: ProofOfSelection
    is_last: byte
```

**Fields:**

- public_key is $K^{n}_{l}$,
  a public key from the set $\mathbf{K}^{n}_{h}$.
- proof_of_quota is $\pi^{K^{n}_{l}}_{Q}$,
  a corresponding proof of quota for the key $K^{n}_{l}$ from the $\mathbf{K}^{n}_{h}$;
  it also contains the key nullifier.
- signature is $\sigma_{K^{n}_{l}}(\mathbf{h|P}_{l})$,
  a signature of the concatenation of $l$-th encapsulation
  of the payload $\mathbf{P}$ and the private header $\mathbf{h}$,
  that can be verified by public key $K^{n}_{l}$.
- proof_of_selection is $\pi^{K^{n}_{l+1},m_{l+1}}_{S}$,
  a proof of selection of the node index $m_{l+1}$
  assuming valid proof of quota $\pi^{K^{n}_{l}}_{Q}$.
- is_last is $\Omega$,
  a flag that indicates that this is the last encapsulation.

#### Payload

The Payload is formatted according to the
[Payload Formatting Specification][payload-formatting].
The formatted Payload is generated as the outcome of
the [Message Encapsulation Mechanism][message-encapsulation].

#### Maximum Payload Length

The `MAX_PAYLOAD_LENGTH` parameter defines the maximum length of the payload,
which for version 1 of the Blend Protocol is fixed as `MAX_PAYLOAD_LENGTH=34003`.
That is, 34kB for the payload body (`MAX_BODY_LENGTH`)
and 3 bytes for the payload header.
More information about payload formatting can be found in
[Payload Formatting Specification][payload-formatting].

```python
MAX_PAYLOAD_LENGTH = 34003
MAX_BODY_LENGTH = 34000
PAYLOAD_HEADER_SIZE = 3
```

## Implementation Considerations

### Message Size Uniformity

**Fixed-Length Design:**

- All messages have a fixed total length to prevent traffic analysis attacks
- The payload length is constant regardless of actual content size
- Padding is used to fill unused space in the payload body
- This design prevents adversaries from distinguishing message types based on size

### Protocol Version

**Version Field:**

- The current protocol version is 0x01
- The version field is a single byte in the public header
- Future protocol versions may introduce breaking changes to the message format
- Implementations must validate the version field before processing messages

### Header Generation

**Dependency on Encapsulation:**

- Both public_header and private_header are generated by
  the Message Encapsulation Mechanism.
- Implementations must not manually construct headers
- The encapsulation mechanism ensures proper cryptographic properties
- Headers include signatures, proofs, and encryption
  as specified in the Message Encapsulation spec.

### Blending Header Limit

**Maximum Encapsulation Layers:**

- The protocol limits the private header to $\beta_{max}=3$ BlendingHeader entries
- This limit is defined in the Global Parameters
- Each BlendingHeader represents one layer of Message encapsulation
- The limit balances privacy (more layers) with performance and overhead

### Integration Points

**Required Specifications:**

- Message Encapsulation Mechanism: Generates the public and private headers
- Payload Formatting Specification: Defines how to format the payload content
- Notation: Provides mathematical and cryptographic notation used throughout
- Global Parameters: Defines protocol-wide constants like $\beta_{max}$

### Security Considerations

**Traffic Analysis Protection:**

- Fixed message lengths prevent size-based traffic analysis
- All messages appear identical in size on the network
- Cover traffic can be indistinguishable from real data messages

**Cryptographic Integrity:**

- Signatures in both public and private headers ensure message authenticity
- Proof of Quota prevents spam and resource exhaustion
- Proof of Selection ensures correct node routing

**Message Validation:**

- Implementations must verify all signatures before processing
- Proof of Quota must be validated to prevent quota violations
- The is_last flag must be checked to determine final message destination

## References

### Normative

- [Message Encapsulation Mechanism](https://nomos-tech.notion.site/Message-Encapsulation-Mechanism-215261aa09df81309d7fd7f1c2da086b)
  \- Cryptographic operations for building and processing messages
- [Payload Formatting Specification](https://nomos-tech.notion.site/Payload-Formatting-215261aa09df81b2a3e1d913a0df9ad9)
  \- Defines payload structure and formatting rules
- [Blend Protocol](https://nomos-tech.notion.site/Blend-Protocol-215261aa09df81ae8857d71066a80084)
  \- Protocol-wide constants and configuration values

### Informative

- [Message Formatting Specification](https://nomos-tech.notion.site/Message-Formatting-Specification-215261aa09df81c79e3acd9e921bcc30)
  \- Original Message Formatting documentation
- [Blend Protocol Formatting](https://nomos-tech.notion.site/Formatting-215261aa09df81a3b3ebc1f438209467)
  \- High-level overview of message formatting in Blend Protocol

[payload-formatting]: https://nomos-tech.notion.site/Payload-Formatting-215261aa09df81b2a3e1d913a0df9ad9
[message-encapsulation]: https://nomos-tech.notion.site/Message-Encapsulation-Mechanism-215261aa09df81309d7fd7f1c2da086b

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
