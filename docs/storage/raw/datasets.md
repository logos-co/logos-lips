# DATASETS

| Field | Value |
| --- | --- |
| Name     | Logos Storage Datasets               |
| Slug | 152 |
| Category | Standards Track                      |
| Status   | raw                                  |
| Editor   | Giuliano Mega <giuliano@status.im>   |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/raw/datasets.md) — chore: add math support (#287)
- **2026-02-05** — [`e008949`](https://github.com/logos-co/logos-lips/blob/e0089499204b1cd2b35bae9ffe35471f3bd830ca/docs/storage/raw/datasets.md) — feat: Logos Storage datasets spec (#277)

<!-- timeline:end -->

## Abstract

This spec defines the basic structure, constraints, and representation for Logos Storage **Datasets** and their metadata. Datasets are the unit of data which Logos Storage manipulates: those can be published, downloaded, or deleted. They could be compared to objects in S3 or, somewhat more loosely, to blocks in IPFS.

## Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Dataset

A _dataset_ is an ordered set of fixed-sized blocks, $F = \{b_1, \cdots b_n\}$. Different datasets MAY have different block sizes, but all blocks within a single dataset MUST have the same size. A valid dataset MUST have at least one block.

A dataset is comparable to a regular filesystem (e.g. ext4) file, in that blocks are totally ordered within the file. This allows us to identify a block within a file $F$ by an integer-valued index $1 \leq i \leq n$. This is in direct contrast with systems like, say, IPFS, in which blocks might not be ordered and block-dataset membership is much more fluid, requiring the use of unique block content identifiers (CID) per block instead.

### Manifest

Every dataset $F$ MUST have an associated _manifest_, which contains metadata describing $F$ and is required to correctly store, decode, and validate its blocks individually. It MAY also contain optional metadata such as a content type, and a file name. In CDDL:

```cddl
manifest = {
  version: uint,
  codec: bstr,
  block_size: uint,
  block_count: uint,
  merkle_root: bytes .size 32,
  ? content_type: tstr,
  ? file_name: tstr,
}
```

The content type, when present, MUST be a valid [RFC6838](https://datatracker.ietf.org/doc/html/rfc6838) media type string.

### Identifying Datasets and Blocks

A dataset MUST be identified by the hash of its serialized manifest, $m$. The encoding of this serialization is specified in its `codec` attribute, which MUST contain [a libp2p multicodec type](https://github.com/multiformats/multicodec/blob/master/table.csv). This means a block within a file MUST be uniquely addressable within the network by the tuple $(m, i)$, where $i$ is an integer $1 \leq i \leq n$.

It is important to note that different values for `file_name` and `content_type` will produce different datasets, even if the set of blocks contained in $F$ remains the same. If this turns out to be undesirable, future versions of this spec might adopt an approach in which a subset of the attributes of the manifest gets hashed instead; akin to how Bittorrent does with its [info dictionaries](https://www.bittorrent.org/beps/bep_0003.html).

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

1. [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt)
2. [RFC 6838](https://datatracker.ietf.org/doc/html/rfc6838)

### Informative

1. [libp2p multicodec](https://github.com/multiformats/multicodec/blob/master/table.csv)
2. [BEP 0003](https://www.bittorrent.org/beps/bep_0003.html)
