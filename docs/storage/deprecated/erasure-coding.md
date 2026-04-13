# CODEX-ERASUE-CODING

| Field | Value |
| --- | --- |
| Name | Codex Erasue Coding |
| Slug | 79 |
| Status | deprecated |
| Type | RFC |
| Category | Standards Track |
| Editor | Giuliano Mega <giuliano@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-22** — [`e356a07`](https://github.com/vacp2p/rfc-index/blob/e356a076aea06653764515babc71c8d69b26358d/docs/storage/deprecated/erasure-coding.md) — Chore/add makefile (#271)
- **2026-01-22** — [`af45aae`](https://github.com/vacp2p/rfc-index/blob/af45aae01271637142fa931e673dc7c8627f480e/docs/storage/deprecated/erasure-coding.md) — chore: deprecate Marketplace-related specs (#268)
- **2026-01-19** — [`f24e567`](https://github.com/vacp2p/rfc-index/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/erasure-coding.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/vacp2p/rfc-index/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/storage/raw/erasure-coding.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/erasure-coding.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification describes the erasure coding technique used by Codex clients.
A Codex client will encode a dataset before it is stored on the network.

## Background

The Codex protocol uses storage proofs to verify whether a storage provider (SP) is storing a certain dataset.
Before a dataset is retrieved on the network,
SPs must agree to store the dataset for a certain period of time.
When a storage request is active,
erasure coding helps ensure the dataset is retrievable from the network.
This is achieved by the dataset that is chunked,
which is restored in retrieval by erasure coding.
When data blocks are abandoned by storage providers,
the requester can be assured of data retrievability.

## Specification

The keywords “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

A client SHOULD perform the erasure encoding locally before providing a dataset to the network.
During validation, nodes will conduct error correction and decoding based on the erasure coding technique known to the network.
Datasets using encodings not recognized by the network MAY be ignored during decoding and
validation by other nodes in the network.

The dataset SHOULD be split into data chunks represented by `k`, e.g. $(k_1, k_2, k_3, \ldots, k_{n})$.
Each chunk `k` MUST be encoded into `n` blocks, using an erasure encoding technique like the Reed Solomon algorithm.
Including a set of parity blocks that MUST be generated,
represented by `m`.
All node roles on the Codex network use the [Leopard Codec](https://github.com/catid/leopard).

Below is the encoding process:

1. Prepare the dataset for the marketplace using erasure encoding.
2. Derive a manifest CID from the root encoded blocks
3. Error correction by validator nodes once the storage contract begins
4. Decode data back to the original data.

### Encoding

A client MAY prepare a dataset locally before making the request to the network.
The data chunks, `k`, MUST be the same size, if not,
the smaller chunk MAY be padded with empty data.

The data blocks are encoded based on the following parameters:

```js

struct encodingParms {
  ecK: int, // Number of data blocks (K)
  ecM: int, // Number of parity blocks (M)
  rounded: int, // Dataset rounded to multiple of (K)
  steps: int, // Number of encoding iterations (steps)
  blocksCount: int, // Total blocks after encoding
  strategy: enum, // Indexing strategy used
}

```

After the erasure coding process,
a protected manifest SHOULD be generated for the dataset, which would store the CID of the root Merkle tree.
The content of the protected manifest below, see CODEX-MANIFEST for more information:

```js

  syntax = "proto3";

   message verifiable {
      string verifyRoot = 1                 // Root of verification tree with CID
      repeated string slot_roots = 2              // List Individual slot roots with CID
      uint32 cellSize = 3                 // Size of verification cells
      string verifiableStrategy = 4 // Strategy for verification
   }

   message ErasureInfo {
     optional uint32 ecK = 1;                            // number of encoded blocks
     optional uint32 ecM = 2;                            // number of parity blocks
     optional bytes originalTreeCid = 3;                 // cid of the original dataset
     optional uint32 originalDatasetSize = 4;            // size of the original dataset
     optional VerificationInformation verification = 5;  // verification information
   }

   message Manifest {
     optional bytes treeCid = 1;        // cid (root) of the tree
     optional uint32 blockSize = 2;     // size of a single block
     optional uint64 datasetSize = 3;   // size of the dataset
     optional codec: MultiCodec = 4;    // Dataset codec
     optional hcodec: MultiCodec = 5    // Multihash codec
     optional version: CidVersion = 6;  // Cid version
     optional ErasureInfo erasure = 7;  // erasure coding info
   }

```

After the encoding process,
is ready to be stored on the network via the [CODEX-MARKETPLACE](./codex-marketplace.md).
The Merkle tree root SHOULD be included in the manifest so other nodes are able to locate and
reconstruct a dataset from the erasure encoded blocks.

### Data Repair

Storage providers may have periods during a storage contract where they are not storing the data.
A validator node MAY store the `treeCid` from the `Manifest` to locate all the data blocks and
reconstruct the merkle tree.
When a missing branch of the tree is not retrievable from an SP, data repair will be REQUIRED.
The validator will open a request for a new SP to reconstruct the Merkle tree and
store the missing data blocks.
The validator role is described in the [CODEX-MARKETPLACE](./codex-marketplace.md) specification.

### Decode Data

During dataset retrieval, a node will use the `treeCid` to locate the data blocks.
The number of retrieved blocks by the node MUST be greater than `k`.
If less than `k`, the node MAY not be able to reconstruct the dataset.
The node SHOULD request missing data chunks from the network and
wait until the threshold is reached.

## Security Considerations

### Adversarial Attack

An adversarial storage provider can remove only the first element from more than half of the block,
and the slot data can no longer be recovered from the data that the host stores.
For example, with data blocks of size 1TB, erasure coded into 256 data and parity shards.
An adversary could strategically remove 129 bytes, and
the data can no longer be fully recovered with the erasure-coded data that is present on the host.

The RECOMMENDED solution should perform checks on entire shards to protect against adversarial erasure.
In the Merkle storage proofs, the entire shard SHOULD be hashed,
then that hash is checked against the Merkle proof.
Effectively, the block size for Merkle proofs should equal the shard size of the erasure coding interleaving.
Hashing large amounts of data will be expensive to perform in an SNARK, which is used to compress proofs in size in Codex.

### Data Encryption

If data is not encrypted before entering the encoding process, nodes, including storage providers,
MAY be able to access the data.
This may lead to privacy concerns and the misuse of data.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Leapard Codec](https://github.com/catid/leopard)
- CODEX-MANIFEST
- [CODEX-MARKETPLACE](./codex-marketplace.md)
