# NETWORK-WIRE-FORMAT

| Field | Value |
| --- | --- |
| Name | Network Wire Format |
| Slug | 203 |
| Status | raw |
| Category | Standards Track |
| Editor | Daniel Sanchez Quiros <danielsq@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/network-wire-format.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2025-08-20 |
| 1.0.1 | Renamed Nomos to Logos Blockchain | 2026-04-17 |

# Introduction

The Logos Blockchain consists of multiple networks. Peers within these networks need a common language to exchange information effectively. This document defines the standardized language used for this communication.

This document outlines a clear strategy for writing and reading messages transmitted across various Logos Blockchain networks.

The key objectives of this wire format are to have message structures that are sharable across different implementations and languages, and to use a stable encoding and decoding processes that do not depend on interpretation.

# Overview

The Logos Blockchain relies on established message structures and standard encoding/decoding formats rather than creating new ones. All messages follow familiar patterns and utilize widely-adopted industry standards for encoding and decoding.

All data transmitted across Logos Blockchain networks adheres to a single consistent format and serialization structure. The schemas are designed to be compatible with or easily implementable in various programming languages.

# Construction

## Format

Logos Blockchain messages use C layout representation. This means that regardless of the programming language, the order, size, and alignment of fields follow the standardized C/C++ layout.

When you see a message in the specification (typically in Python format), you can easily translate it to its equivalent C-based structure.

For example:

Python

```python
@dataclass
class Foo:
    data: bytes
    size: int
```

Rust

```rust
#[repr(c)]
struct Foo {
    data: Vec<u8>,
    size: usize
}
```

C

```c
struct Foo
{
    data: *uint8_t
    size: size_t
}
```

## Encoding and Decoding

Logos Blockchain messages are encoded using bincode - a compact binary serialization format with zero overhead. The format is defined as "a compact encoder/decoder pair that uses a binary zero-fluff encoding scheme." Bincode has been battle-tested in other blockchain protocol implementations, making it production-ready.

The complete specification can be found in the [official documentation](https://docs.rs/bincode/latest/bincode/).

This applies to transport-level message framing. Consensus structures that must be byte-identical across implementations define their own canonical encoding instead, and where they do, that encoding takes precedence: see [Mantle Transaction Encoding](mantle-transaction-encoding.md) for transactions and [Canonical Encoding](bedrock-v1.1-block-construction.md#canonical-encoding) for the block proposal.

# Reference

- [C structure layout](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Structure-Layout.html)
- [Rust](https://doc.rust-lang.org/nomicon/other-reprs.html#reprc)[repr(c)](https://doc.rust-lang.org/nomicon/other-reprs.html#reprc)
- [Bincode serialization specification](https://docs.rs/bincode/latest/bincode/)
- [Bincode rust crate docs](https://docs.rs/bincode/2.0.1/bincode/)

