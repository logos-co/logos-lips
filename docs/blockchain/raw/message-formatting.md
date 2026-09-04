# MESSAGE-FORMATTING

| Field | Value |
| --- | --- |
| Name | Message Formatting |
| Slug | 89 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski |
| Contributors | Youngjoon Lee <youngjoon@logos.co>, Alexander Mozeika <alexander.mozeika@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/message-formatting.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/message-formatting.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/message-formatting.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/message-formatting.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-09 |
| 1.0.1 | Corrected `Max_Payload_Length` to 34577 bytes, so that it again matches the `Max_Body_Length` of [Payload Formatting](payload-formatting.md) plus the 3-byte payload header. | 2026-08-06 |
| 1.0.2 | Expressed `Max_Payload_Length` as `Max_Body_Length + 3` rather than a literal, so that it tracks the payload body size automatically; it is 18195 bytes at the `Max_Body_Length` that follows from the compressed transaction references of [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md). | 2026-08-18 |
| 1.1.0 | The `version` byte carries the era number ([Bedrock Eras](bedrock-eras.md)). | 2026-09-04 |
| 1.1.1 | Followed `Max_Payload_Length` to 18190 bytes after the removal of the `bedrock_version` header field ([Bedrock Eras](bedrock-eras.md)). | 2026-09-04 |

# Introduction

This document defines an implementation-friendly specification of the Message Formatting, which is introduced in the [Formatting](blend-protocol.md#formatting) section.

In this document we are reusing notation from [Notation](message-encapsulation.md#notation).

# Overview

The message contains a header and a payload. The header informs the protocol about the version of the protocol and the payload type. The message contains a drop or a non-drop payload. The length of a payload is fixed to prevent adversaries from distinguishing types of messages based on their length.

# Construction

## Message

The `Message` is a structure that contains a `public_header`, `private_header` and a `payload`.

```python
class Message:
    public_header: PublicHeader,
    private_header: Private_Header,
    payload: bytes
```

### Public Header

The `public_header` must be generated as the outcome of the [Message Encapsulation Mechanism](message-encapsulation.md).

The `public_header` is defined as follows:

```python
class PublicHeader:
    version: byte,
    public_key: PublicKey,
    proof_of_quota: ProofOfQuota,
    signature: Signature
```

Where:

- `version` is the era number of the epoch in which the message is generated ([Bedrock Eras](bedrock-eras.md#era-schedule)).
- `public_key` is $`K^{n}_i`$, a public key from the set $`\mathbf K^n_h`$ as defined in the [Message Encapsulation](message-encapsulation.md) spec.
- `proof_of_quota` is $`\pi^{K^{n}_i}_{Q}`$, a corresponding proof of quota for the key $`K^{n}_i`$ from the $`\mathbf K^n_h`$ it also contains the key nullifier.
- `signature` is $`\sigma_{K^{n}_{i}}(\mathbf {h|P}_i)`$, a signature of the concatenation of the $`i`$-th encapsulation of the payload $`\mathbf P`$ and the private header $`\mathbf h`$, that can be verified by the public key $`K^{n}_{i}`$.

### Private Header

The `private_header` must be generated as the outcome of the [Message Encapsulation Mechanism](message-encapsulation.md).

The private header contains a set of encrypted blending headers $`\mathbf h = (\mathbf b_1,...,\mathbf b_{h_{max}})`$.

```python
private_header: list[BlendingHeader]
```

The size of the set is limited to $`\beta_{max}=3`$ `BlendingHeader` entries, as defined in the [Global Parameters](blend-protocol.md#global-parameters).

The `BlendingHeader` ($`\mathbf b_l`$) is defined as follows:

```python
class BlendingHeader:
    public_key: PublicKey,
    proof_of_quota: ProofOfQuota,
    signature: Signature,
    proof_of_selection: ProofOfSelection
    is_last: byte
```

Where:

- `public_key` is $`K^{n}_{l}`$, a public key from the set $`\mathbf K^n_h`$.
- `proof_of_quota` is $`\pi^{K^{n}_l}_{Q}`$, a corresponding proof of quota for the key $`K^{n}_l`$ from the $`\mathbf K^n_h`$ it also contains the key nullifier.
- `signature` is $`\sigma_{K^{n}_{l}}(\mathbf {h|P}_l)`$, a signature of the concatenation of $`l`$-th encapsulation of the payload $`\mathbf P`$ and the private header $`\mathbf h`$, that can be verified by public key $`K^{n}_{l}`$.
- `proof_of_selection` is $`\pi^{K^{n}_{l+1},m_{l+1}}_{S}`$, a proof of selection of the node index $`m_{l+1}`$ assuming valid proof of quota $`\pi^{K^{n}_{l}}_{Q}`$.
- `is_last` is $`\Omega`$, a flag that indicates that this is the last encapsulation.

### Payload

The `payload` must be formatted according to the [Payload Formatting](payload-formatting.md). The formatted `payload` must be generated as the outcome of the [Message Encapsulation Mechanism](message-encapsulation.md).

## Maximum Payload Length

The `Max_Payload_Length` parameter defines the maximum length of the `payload`. It is not an independent parameter: a payload is a 3-byte header followed by a body of exactly `Max_Body_Length` bytes, so

&nbsp;&nbsp;&nbsp;&nbsp;`Max_Payload_Length = Max_Body_Length + 3`

which is 18190 bytes at the `Max_Body_Length` of 18187 currently set by [Payload Formatting](payload-formatting.md). Stating it as a derived value rather than a literal means that a change to the maximum block proposal size — which is what sets `Max_Body_Length` — reaches this parameter without an edit here. More information about payload formatting can be found in [Payload Formatting](payload-formatting.md).
