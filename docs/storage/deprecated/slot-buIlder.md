# CODEX-SLOT-BUILDER

| Field | Value |
| --- | --- |
| Name | Codex Slot Builder |
| Slug | 78 |
| Status | deprecated |
| Category | Standards Track |
| Editor | Jimmy Debe <jimmy@status.im> |
| Contributors | Jimmy Debe <jimmy@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/deprecated/slot-buIlder.md) — chore: add math support (#287)
- **2026-01-22** — [`e356a07`](https://github.com/logos-co/logos-lips/blob/e356a076aea06653764515babc71c8d69b26358d/docs/storage/deprecated/slot-buIlder.md) — Chore/add makefile (#271)
- **2026-01-22** — [`af45aae`](https://github.com/logos-co/logos-lips/blob/af45aae01271637142fa931e673dc7c8627f480e/docs/storage/deprecated/slot-buIlder.md) — chore: deprecate Marketplace-related specs (#268)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/slot-buIlder.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/storage/raw/slot-buIlder.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/slot-buIlder.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document describes the Codex slot builder mechanism.
Slots used in the Codex protocol are an important component of node collaboration in the network.

## Background

The Codex protocol places a dataset into blocks before sending a storage request to the network.
Slots control and facilitate the distribution of the data blocks to participating storage providers.
The mechanism builds individual Merkle trees for each slot, enabling cell-level proof generation, and
constructs a root verification tree over all slot roots.

## Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

A Codex client wanting to present a dataset to the network will present a set of erasure encoded data blocks,
as described in the [CODEX-ERASURE-CODING](erasure-coding.md) specification.
These data blocks will be placed into slots for storage providers to access.
The slot building process MUST construct a block digest Merkle tree from the data blocks.
The root hashes from this tree are used as the leaves in a slot merkle tree.

The prepared dataset is presented to storage providers in the form of slots.
A slot represents the location of a data block cell with an open storage contract.
Storage providers SHOULD be able to locate a specific data block and
all the details of the storage contract.
See, the [CODEX-MARKETPLACE](./codex-marketplace.md) specification.

### Construct a Slot Tree

#### Block Digest Tree

A slot stores a list of root hashes that help with the retrieval of a dataset.
The block digest tree SHOULD be constructed before building any slots.
A data block is divided into cells that are hashed.
The block size MUST be divisible by the cell size for the block digest tree construction.

$$
\text{Cell size} \mid \text{Block size (in bytes)}
$$

A block digest tree SHOULD contain the unique root hashes of blocks of the entire dataset,
which MAY be based on the [Poseidon2](https://eprint.iacr.org/2023/323) algorithm.
The result of one digest tree will be represented by the root hash of the tree.

#### Slot Tree

A slot tree represents one slot,
which includes the list of digest root hashes.
If a block is empty,
the slot branch SHOULD be a hash of an empty block.
Some slots MAY be empty,
depending on the size of the dataset.

$$
\text{Blocks per slot} = \frac{\text{Total blocks}}{\text{Number of slots}}
$$

The cells per slot tree branch MUST be padded to a power of two.
This will ensure a balanced slot Merkle tree.

$$
\text{Cells per slot} = \text{Blocks per slot} \times \text{Cells per block}
$$

Below are the REQUIRED values to build a slot.

``` nim

type SlotsBuilder*[T, H] = ref object of RootObj
 store: BlockStore              # Storage backend for blocks
 manifest: Manifest             # Current dataset manifest
 strategy: IndexingStrategy     # Block indexing strategy
 cellSize: NBytes               # Size of each cell in bytes
 numSlotBlocks: Natural         # Blocks per slot (including padding)
 slotRoots: seq[H]              # Computed slot root hashes
 emptyBlock: seq[byte]          # Pre-allocated empty block data
 verifiableTree: ?T             # Optional verification tree
 emptyDigestTree: T             # Pre-computed empty block tree

```

### Verification Tree

Nodes within the network are REQUIRED to verify a dataset before retrieving it.
A verification tree is a Merkle proof derived from the `slotRoot`.
The entire dataset is not REQUIRED to construct the tree.

The following are the inputs to verify a proof:

```nim

type
 H = array[32, byte]
 Natural = uint64

type ProofInputs*[H] = object
 entropy*: H                    # Randomness value
 datasetRoot*: H                # Dataset root hash
 slotIndex*: Natural            # Slot identifier
 slotRoot*: H                   # Root hash of slot
 nCellsPerSlot*: Natural        # Cell count per slot
 nSlotsPerDataSet*: Natural     # Total slot count
 slotProof*: seq[H]             # Inclusion proof for slot in dataset
 samples*: seq[Sample[H]]       # Cell inclusion proofs

```

To verify, a node MUST recompute the root hash,
based on `slotProof` and the hash of the `slotIndex`,
to confirm that the `slotIndex` is a member of the dataset represented by `datasetRoot`.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [CODEX-ERASURE-CODING](erasure-coding.md)
- [CODEX-MARKETPLACE](./codex-marketplace.md)
- [Poseidon2](https://eprint.iacr.org/2023/323)
