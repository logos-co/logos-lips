# NOMOS-PAYLOAD-FORMATTING

| Field | Value |
| --- | --- |
| Name | Nomos Payload Formatting Specification |
| Slug | 97 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@status.im> |
| Contributors | Youngjoon Lee <youngjoon@status.im>, Alexander Mozeika <alexander.mozeika@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-payload-formatting.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-payload-formatting.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Payload formatting for the Blend Protocol.
The Payload has a fixed length to prevent traffic analysis attacks,
with shorter messages padded using random data.

**Keywords:** Blend, payload formatting, padding, fixed length, traffic analysis

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Protocol Specification

### Construction

#### Payload

The `Payload` is a structure that contains a `Header` and a `body`.

```python
class Payload:
    header: Header
    body: bytes
```

#### Header

The `Header` is a structure that contains a `body_type` and a `body_length`.

```python
class Header:
    body_type: byte
    body_length: uint16
```

**Fields:**

- `body_type`: A single byte indicating the type of message in the body
- `body_length`: A uint16 (encoded as little-endian)
  indicating the actual length of the raw message

#### Type

Messages are classified into two types:

- **Cover message**: Traffic used to obscure network patterns and enhance privacy
- **Data message**: Traffic containing actual protocol data (e.g., block proposals)

The `body_type` field indicates the message classification:

- `body_type=0x00`: The body contains a cover message
- `body_type=0x01`: The body contains a data message

Implementations MUST discard messages with any other `body_type` value,
as this indicates the message was not decapsulated correctly.

#### Length

The `body_length` field is a uint16 (encoded as little-endian),
with a theoretical maximum of 65535 bytes.
The `body_length` MUST be set to the actual length of the raw message in bytes.

#### Body

The `MAX_BODY_LENGTH` parameter defines the maximum length of the body.
The maximal length of a raw data message is 33129 bytes (Block Proposal),
so `MAX_BODY_LENGTH=33129`.

The body length is fixed to `MAX_BODY_LENGTH` bytes.
If the length of the raw message is shorter than `MAX_BODY_LENGTH`,
it MUST be padded with random data.

```python
MAX_BODY_LENGTH = 33129
```

**Note:** The `MAX_BODY_LENGTH` (33129 bytes) defined here differs from
`MAX_PAYLOAD_LENGTH` (34003 bytes) in the [Message Formatting specification][message-formatting].
The Message Formatting specification includes additional Message headers
beyond the Payload body.

## Implementation Considerations

### Fixed-Length Design

**Payload Size Uniformity:**

- All payloads have a fixed total length to prevent traffic analysis attacks
- The body length is constant at MAX_BODY_LENGTH=33129 bytes
  regardless of actual content size
- Shorter messages must be padded with random data to fill unused space
- This design prevents adversaries from distinguishing message types based on size

**Padding Requirements:**

- If len(raw_message) < MAX_BODY_LENGTH, padding is required
- Padding must consist of random data (not zeros or predictable patterns)
- The body_length field indicates where the actual message ends and padding begins
- Implementations must use cryptographically secure random number generation
  for padding

### Header Structure

**Total Header Size:**

- body_type: 1 byte
- body_length: 2 bytes (uint16, little-endian)
- Total header size: 3 bytes

**Endianness:**

- The body_length field uses little-endian encoding
- Implementations must correctly encode/decode uint16 values in little-endian format
- This ensures consistent interpretation across different platforms and architectures

### Message Type Validation

**Valid Types:**

- 0x00: Cover message (dummy traffic for privacy)
- 0x01: Data message (actual protocol data or block proposals)

**Invalid Type Handling:**

- Any body_type value other than 0x00 or 0x01 indicates decapsulation failure
- Messages with invalid types must be discarded immediately
- Implementations should not attempt to process or forward invalid messages
- Invalid types may indicate cryptographic errors or malicious manipulation

### Body Length Constraints

**Length Validation:**

- body_length must be ≤ MAX_BODY_LENGTH (33129 bytes)
- body_length indicates the actual length of the raw message before padding
- Implementations must verify body_length is within valid range before processing
- The theoretical maximum is 65535 bytes (uint16 limit),
  but the protocol constrains it to 33129

**Message Extraction:**

- To extract the raw message: raw_message = body[0:body_length]
- Padding data beyond body_length should be discarded
- The padding serves only to maintain fixed payload size

### Maximum Message Size

**Block Proposal Size:**

- The current MAX_BODY_LENGTH=33129 is based on the maximum size of a Block Proposal
- This value may be adjusted in future protocol versions
- Implementations should use the constant rather than hardcoding the value
- Total payload size = 3 bytes (header) + 33129 bytes (body) = 33132 bytes

**Total Payload Calculation:**

```python
HEADER_SIZE = 3  # 1 byte type + 2 bytes length
MAX_BODY_LENGTH = 33129
MAX_PAYLOAD_LENGTH = HEADER_SIZE + MAX_BODY_LENGTH  # 33132 bytes
```

### Cover Traffic

**Cover Messages (body_type=0x00):**

- Cover messages provide traffic obfuscation to enhance privacy
- They appear indistinguishable from data messages at the network level
- The body of a cover message should contain random data
- Cover messages are discarded after decapsulation

**Indistinguishability:**

- Cover and data messages have identical size due to fixed-length design
- Both types follow the same formatting and encryption procedures
- Network observers cannot distinguish cover traffic from real data

### Integration Points

**Required Specifications:**

- [Message Formatting Specification][message-formatting]: Defines the overall message structure
  that contains the payload
- [Message Encapsulation Mechanism][message-encapsulation]: Handles encryption and encapsulation
  of the formatted payload
- [Blend Protocol][blend-protocol]: Provides high-level overview of payload formatting

**Relationship to Message Formatting:**

- The Payload Formatting specification defines the internal structure of the payload
- The Message Formatting specification defines how the payload is included
  in the complete message
- The MAX_PAYLOAD_LENGTH in Message Formatting (34003 bytes)
  accounts for this payload structure

### Security Considerations

**Cryptographic Randomness:**

- Padding must use cryptographically secure random number generation
- Predictable padding could leak information about message types or content
- Never use zeros, repeated patterns, or pseudo-random generators for padding

**Length Information Leakage:**

- The fixed-length design prevents length-based traffic analysis
- The body_length field is encrypted as part of the payload
- Only after successful decapsulation can the actual message length be determined

**Type Field Security:**

- The body_type field is encrypted within the payload
- Invalid types indicate potential security issues (failed decryption, tampering)
- Implementations must discard invalid messages without further processing

**Message Validation Sequence:**

1. Decrypt and extract the payload
2. Parse the 3-byte header
3. Validate body_type is 0x00 or 0x01
4. Validate body_length ≤ MAX_BODY_LENGTH
5. Extract raw_message using body_length
6. Process or discard based on body_type

## References

### Normative

- [Message Formatting Specification][message-formatting]
  \- Defines the overall message structure containing the Payload
- [Message Encapsulation Mechanism][message-encapsulation]
  \- Cryptographic operations for encrypting and encapsulating the Payload
- [Blend Protocol][blend-protocol]
  \- Protocol-wide constants and configuration values

### Informative

- [Payload Formatting Specification][payload-formatting-origin]
  \- Original Payload Formatting documentation

[message-formatting]: https://nomos-tech.notion.site/Message-Formatting-Specification-215261aa09df81c79e3acd9e921bcc30
[message-encapsulation]: https://nomos-tech.notion.site/Message-Encapsulation-Mechanism-215261aa09df81309d7fd7f1c2da086b
[blend-protocol]: https://nomos-tech.notion.site/Blend-Protocol-215261aa09df81ae8857d71066a80084
[payload-formatting-origin]: https://nomos-tech.notion.site/Payload-Formatting-Specification-215261aa09df8153a456c555b7dcbe1c

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
