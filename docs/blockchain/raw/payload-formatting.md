# PAYLOAD-FORMATTING

| Field | Value |
| --- | --- |
| Name | Payload Formatting |
| Slug | 97 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors | Youngjoon Lee <youngjoon@logos.co>, Alexander Mozeika <alexander.mozeika@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/payload-formatting.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/payload-formatting.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/payload-formatting.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/payload-formatting.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-09 |
| 1.1.0 | Updated `Max_Body_Length` to 34574 bytes, the maximum block proposal size once a proposal carries the signed headers of the uncles it references (see [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)). | 2026-08-06 |
| 1.1.1 | Updated `Max_Body_Length` to 18192 bytes, following the compression of transaction references to 16-byte prefixes and their encoding as a variable-length list (see [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)). | 2026-08-18 |
| 1.2.0 | Add the transaction `body_type`, bound a carried transaction to `Max_Body_Length`, and state the fixed-length padding cost it inherits | 2026-08-31 |

# Introduction

This document defines an implementation-friendly specification of the Payload Formatting, which is introduced in the [Formatting](blend-protocol.md#formatting) section.

# Overview

The payload contains a header and a body. The header informs the protocol about the way the body must be handled. The body contains a raw message (data/proposal or cover message). The payload must be of a fixed length to prevent adversaries from distinguishing types of messages based on their length. Therefore, shorter messages must be padded with random data.

# Construction

## Payload

The `Payload` is a structure that contains a `header` and a `body`.

```python
class Payload:
    header: Header,
    body: bytes
```

## Header

The `header` is a structure that contains a `body_type` and a `body_length`.

```python
class Header:
    body_type: byte,
    body_length: uint16
```

### Type

We define the following values of the `body_type`:

- `body_type=0x00`, informs that the `body` contains a cover message.
- `body_type=0x01`, informs that the `body` contains a data message carrying a block proposal.
- `body_type=0x02`, informs that the `body` contains a data message carrying a Mantle transaction.

Any other value of type means that the message was not decapsulated correctly and must be discarded.

The `body_type` determines where the content is delivered once a message is fully decapsulated, as defined in the [Blend Protocol](blend-protocol.md#processing): a block proposal is broadcast, and a transaction is both submitted to the node's mempool and broadcast.

The set of values above is therefore closed: a node that does not know a value drops the message rather than ignoring the field. Introducing a new `body_type` is a change to what the network accepts, not only to how a payload is encoded, and nodes must recognise a value before any node emits it.

### Length

We define the `body_length` as uint16 (encoded as little-endian). Therefore, the theoretical limit of the length of the `body` is 65535 bytes. The `body_length` must be set to the length of the body of the payload message (`body_length=len(raw_message)`).

## Body

The `Max_Body_Length` parameter defines the maximum length of the `body`. The maximal length of a raw data message is the maximum size of a [Block Proposal](bedrock-v1.1-block-construction.md#block-proposal) — 18192 bytes, reached when the proposal carries `MAX_UNCLES` signed uncle headers and references `MAX_BLOCK_TXS` transactions — so the `Max_Body_Length=18192`. Because the padding below fixes every `body` to this length, the variable size of a proposal (which depends on the number of referenced uncles and transactions) is not observable on the wire, which is what preserves the indistinguishability of proposals required by the [Blend Protocol](blend-protocol.md).

A transaction carried over the Blend network must not exceed `Max_Body_Length` once encoded. The body is a fixed-size field, so a longer payload cannot be represented at all: there is no fragmentation across messages and no larger body type. A transaction that does not fit is not sendable over this protocol and must reach the network by other means. A node must check the encoded length before constructing the message rather than discovering the limit at encapsulation, and must discard on receipt any payload whose `body_length` exceeds `Max_Body_Length`, since a well-formed message can never carry one.

The `body` length is fixed to `Max_Body_Length` bytes. Therefore, if the length of the raw message is shorter than the `Max_Body_Length`, then it must be padded with random data.

If the `body` length is less than the `Max_Body_Length`, then the last `Max_Body_Length - len(Raw_Message)` bytes must be filled with random data.

The fixed length makes payloads of different types indistinguishable on the wire, and it is the reason a cover message costs exactly as much to send as a block proposal. It applies equally to transactions, which are typically far smaller than the block proposal the parameter is derived from: every transaction sent through the Blend network occupies a full `Max_Body_Length` payload regardless of its own size. A node sending transactions this way therefore pays the bandwidth of a block proposal per transaction, and the network's bandwidth cost scales with the number of payloads carried rather than with the number of bytes those payloads contain. Any estimate of the cost of routing transactions through this protocol must use `Max_Body_Length`, not the encoded size of a transaction.

`body_length` is a `uint16` while `Max_Body_Length` is 18192, so the field can express any permitted length with room to spare. A future payload type larger than 65535 bytes would require widening the field, and therefore a change to the `Header` structure, not only to `Max_Body_Length`.
