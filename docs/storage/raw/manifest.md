# CODEX-MANIFEST

| Field | Value |
| --- | --- |
| Name | Codex Manifest |
| Slug | 145 |
| Status | raw |
| Category | Standards Track |
| Tags | codex, manifest, metadata, cid |
| Editor | Jimmy Debe <jimmy@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-30** — [`0ef87b1`](https://github.com/logos-co/logos-lips/blob/0ef87b1ba9491c854e48c8dfd7574d34ec69c704/docs/storage/raw/manifest.md) — New RFC: CODEX-MANIFEST (#191)

<!-- timeline:end -->

## Abstract

This specification defines the Codex Manifest,
a metadata structure that describes datasets stored on the Codex network.
The manifest contains essential information such as the Merkle tree root CID,
block size, dataset size, and optional attributes like filename and MIME type.
Similar to BitTorrent's metainfo files,
the Codex Manifest enables content identification and retrieval
but is itself content-addressed and announced on the Codex DHT.

**Keywords:** manifest, metadata, CID, Merkle tree, content addressing,
BitTorrent, DHT, protobuf

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119][rfc-2119].

### Definitions

| Term | Description |
| ---- | ----------- |
| Manifest | A metadata structure describing a dataset stored on the Codex network. |
| CID | Content Identifier, a self-describing content-addressed identifier used in IPFS and Codex. |
| Codex Tree | A Merkle tree structure computed over the blocks in a dataset. See [CODEX-MERKLE-TREE][merkle-tree]. |
| treeCid | The CID of the root of the Codex Tree corresponding to a dataset. |
| Block | A fixed-size chunk of data in the dataset. |
| Multicodec | A self-describing protocol identifier from the [Multicodec][multicodec] table. |

## Background

The Codex Manifest provides the description of the metadata uploaded to the Codex network.
It is in many ways similar to the BitTorrent metainfo file, also known as .torrent files.
For more information, see [BEP3][bep3] from BitTorrent Enhancement Proposals (BEPs).
While the BitTorrent metainfo files are generally distributed out-of-band,
the Codex Manifest receives its own content identifier ([CIDv1][cidv1])
that is announced on the Codex DHT.
See the [CODEX-DHT specification][codex-dht] for more details.

In version 1 of the BitTorrent protocol,
when a user wants to upload (seed) some content to the BitTorrent network,
the client chunks the content into pieces.
For each piece, a hash is computed and
included in the pieces attribute of the info dictionary in the BitTorrent metainfo file.
In Codex,
instead of hashes of individual pieces,
a Merkle tree is computed over the blocks in the dataset.
The CID of the root of this Merkle tree is included as the `treeCid` attribute in the Codex Manifest.
See [CODEX-MERKLE-TREE][merkle-tree] for more information.
Version 2 of the BitTorrent protocol also uses Merkle trees and
includes the root of the tree in the info dictionary for each .torrent file.

The Codex Manifest CID has the ability to uniquely identify the content and
enables retrieval of that content from any Codex client.

## Protocol Specification

### Manifest Encoding

The manifest is encoded using Protocol Buffers (proto3) and
serialized with multibase base58btc encoding.
Each manifest has a corresponding CID (the manifest CID).

### Manifest Attributes

```protobuf
syntax = "proto3";

message Manifest {
  optional bytes treeCid = 1;        // CID (root) of the tree
  optional uint32 blockSize = 2;     // Size of a single block
  optional uint64 datasetSize = 3;   // Size of the dataset
  optional uint32 codec = 4;         // Dataset codec
  optional uint32 hcodec = 5;        // Multihash codec
  optional uint32 version = 6;       // CID version
  optional string filename = 7;      // Original filename
  optional string mimetype = 8;      // Original mimetype
}
```

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `treeCid` | bytes | A hash based on [CIDv1][cidv1] of the root of the [Codex Tree][merkle-tree], which is a form of a Merkle tree corresponding to the dataset described by the manifest. Its multicodec is `codex-root` (`0xCD03`). |
| `blockSize` | uint32 | The size of each block for the given dataset. The default block size used in Codex is 64 KiB. |
| `datasetSize` | uint64 | The total size of all blocks for the original dataset. |
| `codec` | uint32 | The [Multicodec][multicodec] used for the CIDs of the dataset blocks. Codex uses `codex-block` (`0xCD02`). |
| `hcodec` | uint32 | The [Multicodec][multicodec] used for computing the multihash used in block CIDs. Codex uses `sha2-256` (`0x12`). |
| `version` | uint32 | The version of CID used for the dataset blocks. |
| `filename` | string | When provided, it MAY be used by the client as a file name while downloading the content. |
| `mimetype` | string | When provided, it MAY be used by the client to set a content type of the downloaded content. |

### DHT Announcement

The manifest CID SHOULD be announced on the [CODEX-DHT][codex-dht],
so that nodes storing the corresponding manifest block can be found
by other clients requesting to download the corresponding dataset.

From the manifest,
providers storing relevant blocks SHOULD be identified using the `treeCid` attribute.
The manifest CID in Codex is similar to the `info_hash` from BitTorrent.

## Security Considerations

### Content Integrity

The `treeCid` attribute provides cryptographic binding between the manifest and the dataset content.
Implementations MUST verify that retrieved blocks match the expected hashes
derived from the Merkle tree root.

### Manifest Authenticity

The manifest CID provides content addressing,
ensuring that any modification to the manifest will result in a different CID.
Implementations SHOULD verify manifest integrity by recomputing the CID
from the received manifest data.

## References

### Normative

- [CODEX-MERKLE-TREE][merkle-tree] - Codex Merkle tree specification
- [CODEX-DHT][codex-dht] - Codex DHT specification

### Informative

- [BEP3][bep3] - The BitTorrent Protocol Specification
- [CIDv1][cidv1] - Content Identifier version 1 specification
- [Multicodec][multicodec] - Self-describing protocol identifiers
- [Codex Manifest Spec][origin-ref] - Original specification

[rfc-2119]: https://www.ietf.org/rfc/rfc2119.txt
[merkle-tree]: ./merkle-tree.md
[codex-dht]: ./dht.md
[bep3]: http://bittorrent.org/beps/bep_0003.html
[cidv1]: https://github.com/multiformats/cid#cidv1
[multicodec]: https://github.com/multiformats/multicodec
[origin-ref]: https://github.com/logos-storage/logos-storage-docs-obsidian/blob/main/10%20Notes/Specs/Codex%20Manifest%20Spec.md

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
