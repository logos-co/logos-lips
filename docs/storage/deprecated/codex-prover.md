# CODEX-PROVER

| Field | Value |
| --- | --- |
| Name | Codex Prover Module |
| Slug | 81 |
| Status | deprecated |
| Type | RFC |
| Category | Standards Track |
| Editor | Codex Team |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-22** — [`e356a07`](https://github.com/vacp2p/rfc-index/blob/e356a076aea06653764515babc71c8d69b26358d/docs/storage/deprecated/codex-prover.md) — Chore/add makefile (#271)
- **2026-01-22** — [`af45aae`](https://github.com/vacp2p/rfc-index/blob/af45aae01271637142fa931e673dc7c8627f480e/docs/storage/deprecated/codex-prover.md) — chore: deprecate Marketplace-related specs (#268)
- **2026-01-19** — [`f24e567`](https://github.com/vacp2p/rfc-index/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/codex-prover.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/codex-prover.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Proving module for
[Codex](https://github.com/codex-storage/nim-codex),
which provides a succinct, publicly verifiable way to check that storage
providers still hold the data they committed to.
The proving module samples cells from stored slots,
and generates zero-knowledge proofs that tie those samples and Merkle paths
back to the published dataset root commitment.
The marketplace contract verifies these proofs on-chain and uses the result
to manage incentives such as payments and slashing.

## Background / Rationale / Motivation

In decentralized storage networks such as
[Codex](https://github.com/codex-storage/nim-codex),
one of the main challenges is ensuring durability and availability of data
stored by storage providers.
To achieve durability, random sampling combined with erasure coding is used
to provide probabilistic guarantees while touching only a tiny fraction of
the stored data per challenge.

The proving module addresses this challenge by:

- Checking for storage proof requests from the marketplace
- Sampling cells from slots in the stored dataset and constructing Merkle proofs
- Generating zero-knowledge proofs for randomly selected cells in stored slots
- Submitting proofs to the on-chain marketplace smart contract for verification

The proving module consists of three main sub-components:

1. **Sampler**: Derives random sample indices from public entropy and slot commitments, then generates the proof input
2. **Prover**: Produces succinct ZK proofs for valid proof inputs and verifies such proofs
3. **ZK Circuit**: Defines the logic for sampling, cell hashing, and Merkle tree membership checks

The proving module relies on `BlockStore` for block-level storage access
and `SlotsBuilder` to build initial commitments to the stored data.
`BlockStore` is Codex's local storage abstraction that provides
block retrieval by CID.
`SlotsBuilder` constructs the Merkle tree commitments for slots and datasets
(see [CODEX-SLOT-BUILDER](#references) for details).
The incentives involved, including collateral and slashing,
are handled by the marketplace logic.

## Theory / Semantics

### Terminology

| Term | Description |
| ---- | ----------- |
| **Storage Client (SC)** | A node that participates in Codex to buy storage. |
| **Storage Provider (SP)** | A node that participates in Codex by selling disk space to other nodes. |
| **Dataset** | A set of fixed-size slots provided by possibly different storage clients. |
| **Cell** | Smallest circuit sampling unit (e.g., 2 KiB), its bytes are packed into field elements and hashed. |
| **Block** | Network transfer unit (e.g., 64 KiB) consists of multiple cells, used for transport. |
| **Slot** | The erasure-coded fragment of a dataset stored by a single storage provider. Proof requests are related to slots. |
| **Commitment** | Cryptographic binding (and hiding if needed) to specific data. In Codex this is a Poseidon2 Merkle root (e.g., Dataset Root or Slot Root). It allows anyone to verify proofs against the committed content. |
| **Dataset Root / Slot Root** | Poseidon2 Merkle roots used as public commitments in the circuit. Not the SHA-256 content tree used for CIDs. |
| **Entropy** | Public randomness (e.g., blockhash) used to derive random sample indices. |
| **Witness** | Private zk circuit inputs. |
| **Public Inputs** | Values known to or shared with the verifier. |
| **Groth16** | Succinct zk-SNARK proof system used by Codex. |
| **Proof Window** | The time/deadline within which the storage provider must submit a valid proof. |

### Data Commitment

In Codex, a dataset is split into `numSlots` slots which are the ones sampled. Each slot is split into `nCells` fixed-size cells. Since networking operates on blocks, cells are combined to form blocks where each block contains `BLOCKSIZE/CELLSIZE` cells. The following describes how raw bytes become commitments in Codex (cells -> blocks -> slots -> dataset):

**Cell hashing:**

- Split each cell's bytes into chunks (31-byte for BN254), map to field elements (little-endian). Pad the last chunk with `10*`.
- Hash the resulting field-element stream with a Poseidon2 sponge.

**Block tree (cell -> block):**

- A network block in Codex is 64 KiB and contains 32 cells of 2 KiB each.
- Build a Merkle tree of depth 5 over the 32 cell hashes. The root is the block hash.

**Slot tree (block -> slot):**

- For all blocks in a slot, build a Merkle tree over their block hashes
  (root of block trees).
  The number of leaves is expected to be a power of two
  (in Codex, the `SlotsBuilder` pads the slots).
  The Slot tree root is the public commitment that is sampled.
  See [CODEX-SLOT-BUILDER](#references) for the detailed slot building process.

**Dataset tree (slot -> dataset):**

- Build a Merkle tree over the slot trees roots to obtain the dataset root
  (this is different from SHA-256 CID used for content addressing).
  The dataset root is the public commitment to all slots hosted by a single
  storage provider.

### Codex Merkle Tree Conventions

Codex extends the standard Merkle tree with a keyed compression that depends on
(a) whether a node is on the bottom (i.e. leaf layer) and
(b) whether a node is odd (has a single child) or even (two children).
These two bits are encoded as `{0,1,2,3}` and fed into the hash so tree shape
cannot be manipulated.

**Steps in building the Merkle tree (bytes/leaves -> root):**

Cell bytes are split into 31-byte chunks to fit in BN254,
each mapped little-endian into a BN254 field element.
`10*` padding is used.

Leaves (cells) are hashed with a Poseidon2 sponge with state size `t=3`
and rate `r=2`.
The sponge is initialized with IV `(0,0, domSep)` where:

```text
domSep := 2^64 + 256*t + rate
```

This is a domain-separation constant.

When combining two child nodes `x` and `y`, Codex uses the keyed compression:

```text
compress(x, y, key) = Poseidon2_permutation(x, y, key)[0]
```

where `key` encodes the two bits:

- **bit 0**: 1 if we're at the bottom layer, else 0
- **bit 1**: 1 if this is an odd node (only one child present), else 0

**Special cases:**

- **Odd node** with single child `x`: `compress(x, 0, key)` (i.e., the missing sibling is zero).
- **Singleton tree** (only one element in the tree): still apply one compression round.
- **Merkle Paths** need only sibling hashes:
  left/right direction is inferred from the binary decomposition of the
  leaf index, so you don't transmit direction flags.

### Sampling

**Sampling request:**

Sampling begins when a proof is requested containing the entropy
(also called `ProofChallenge`).
A `DataSampler` instance is created for a specific slot and then used to
produce `Sample` records.

The sampler needs:

- `slotIndex`: the index of the slot being proven.
  This is fixed when the `DataSampler` is constructed.
- `entropy`: public randomness (e.g., blockhash).
- `nSamples`: the number of cells to sample.

**Derive indices:**

The sampler derives deterministic cell indices from the challenge entropy and the slot commitment:

```text
idx = H(entropy || slotRoot || counter) mod nCells
```

where `counter = 1..nSamples` and `H` is the Poseidon2 sponge (rate = 2)
with `10*` padding.
The result is a sequence of indices in `[0, nCells)`,
identical for any honest party given the same `(entropy, slotRoot, nSamples)`.
Note that there is a chance however small that you would have multiple of
the same cell index samples purely by chance.
The chance of that depends on the slot and cell sizes;
the larger the slot and smaller the cell,
the lower the chance of landing on the same cell index.

**Generate per-sample data:**

- Fetch the `cellData` via the `BlockStore` and `builder`,
  and fetch the stored `cell -> block`, `block -> slot`, `slot -> dataset`
  Merkle paths.
  Note that `cell -> block` can be built on the fly and `slot -> dataset`
  can be reused for all samples in that slot.

**Collect Proof Inputs:**

The `DataSampler` collects the `ProofInputs` required for the zk proof system
which contains the following:

- `entropy`: the challenge randomness.
- `datasetRoot`: the root of the dataset Merkle tree.
- `slotIndex`: the index of the proven slot.
- `slotRoot`: the Merkle root of the slot tree.
- `nCellsPerSlot`: total number of cells in the slot.
- `nSlotsPerDataSet`: total number of slots in the dataset.
- `slotProof`: the `slot -> dataset` Merkle path.
- `samples`: a list where each element is:
  - `cellData`: the sampled cell encoded as field elements.
  - `merklePaths`: the concatenation `(cell -> block) || (block -> slot)`.

These `ProofInputs` are then passed to the prover to generate the succinct
ZK proof.

### Proof Generation

To produce a zk storage proof, Codex uses a pluggable proving backend.
In practice, Groth16 over BN254 (altbn128) is used with circuits written
in Circom.
The `Prover` with `ProofInputs` calls the backend to create a succinct proof,
and optionally verifies it locally before submission.

### ZK Circuit Specification

**Circuit parameters (compile-time constants):**

```text
MAXDEPTH     # max depth of slot tree (block -> slot)
MAXSLOTS     # max number of slots in dataset (slot -> dataset)
CELLSIZE     # cell size in bytes (e.g., 2048)
BLOCKSIZE    # block size in bytes (e.g., 65536)
NSAMPLES     # number of sampled cells per challenge (e.g. 100)
```

**Public inputs:**

```text
datasetRoot  # root of the dataset (slot -> dataset)
slotIndex    # index of the slot being proven
entropy      # public randomness used to derive sample indices
```

**Witness (private inputs):**

```text
slotRoot     # root of the slot (block -> slot) tree
slotProof    # Merkle path for slot -> dataset
samples[]:   # one entry per sampled cell:
  cellData     # the sampled cell encoded as field elements
  merklePaths  # (cell -> block) || (block -> slot) Merkle path
```

**Constraints (informal):**

For each sampled cell, the circuit enforces:

1. **Cell hashing:** recompute the cell digest from `cellData` using the Poseidon2 sponge (rate=2, `10*` padding).
2. **Cell -> Block:** verify inclusion of the cell digest in the block tree using the provided `cell -> block` path.
3. **Block -> Slot:** verify inclusion of the block digest in the slot tree using the `block -> slot` path.
4. **Slot -> Dataset:** verify inclusion of `slotRoot` in dataset tree using `slotProof`.
5. **Sampling indices:** recompute the required sample indices from `(entropy, slotRoot, NSAMPLES)` and check that the supplied samples correspond exactly to those indices.

**Output (proof):**

- **Groth16 proof** over BN254: the tuple (A ∈ G₁, B ∈ G₂, C ∈ G₁), referred to in code as `CircomProof`.

**Verification:**

- The verifier (on-chain or off-chain) checks the `proof` against the `public inputs` using the circuit's `verifying key` (derived from the `CRS` generated at setup).
- On EVM chains, verification leverages BN254 precompiles.

### Functional Requirements

**Data Commitment:**

- Fetch existing slot commitments using `BlockStore` and `SlotsBuilder`: `cell -> block -> slot` Merkle trees for each slot in the locally stored dataset.
- Fetch dataset commitment: `slot -> dataset` verification tree root.
- Proof material: retrieve cell data (as field elements).

**Sampling:**

- Checks for marketplace challenges per slot.
- Random sampling: Derive `nSamples` cell indices for the `slotIndex` from `(entropy, slotRoot)`.
- For each sampled cell, fetch: `cellData` (as field elements) and Merkle paths (all `cell -> block -> slot -> dataset`)
- Generate `ProofInputs` containing the public inputs (`datasetRoot`, `slotIndex`, `entropy`) and private witness (`cellData`, `slotRoot`, `MerklePaths`).

**Proof Generation:**

- Given `ProofInputs`, use the configured backend (Groth16 over BN254) to create a succinct Groth16 proof.
- The circuit enforces the same Merkle layout and Poseidon2 hashing used for commitments.

### Non-Functional Requirements

**Performance / Latency:**

- End-to-end (sample -> prove -> submit) completes within the on-chain proof window with some safety margin.
- Small Proof size, e.g. Groth16/BN254 plus public inputs.
- On-chain verification cost is minimal.
- Support concurrent proving for multiple slots.

**Security & Correctness:**

- Soundness and completeness: only accept valid proofs, invalid inputs must not yield accepted proofs.
- Commitment integrity: proofs are checked against the publicly available Merkle commitments to the stored data.
- Entropy binding: sample indices must be derived from the on-chain entropy and the slot commitment. This binds the proofs to specific cell indices and time period, and makes the challenge unpredictable until the period begins. This prevents storage providers from precomputing the proofs or selectively retaining a set of cells.

## Wire Format Specification / Syntax

### Data Models

#### SlotsBuilder

```nim
SlotsBuilder*[T, H] = ref object of RootObj
  store: BlockStore
  manifest: Manifest # current manifest
  strategy: IndexingStrategy # indexing strategy
  cellSize: NBytes # cell size
  numSlotBlocks: Natural
    # number of blocks per slot (should yield a power of two number of cells)
  slotRoots: seq[H] # roots of the slots
  emptyBlock: seq[byte] # empty block
  verifiableTree: ?T # verification tree (dataset tree)
  emptyDigestTree: T # empty digest tree for empty blocks
```

Contains references to the `BlockStore`, current `Manifest`, indexing strategy, cell size, number of blocks per slot, slot roots, empty block data, the verification tree (dataset tree), and empty digest tree for empty blocks.

#### DataSampler

```nim
DataSampler*[T, H] = ref object of RootObj
  index: Natural
  blockStore: BlockStore
  builder: SlotsBuilder[T, H]
```

Contains the slot index, reference to `BlockStore`, and reference to `SlotsBuilder`.

#### Prover

```nim
Prover* = ref object of RootObj
    backend: AnyBackend
    store: BlockStore
    nSamples: int
```

Contains the proving backend, reference to `BlockStore`, and number of samples.

#### Sample

```nim
Sample*[H] = object
  cellData*: seq[H]
  merklePaths*: seq[H]
```

Contains the sampled cell data as a sequence of hash elements and the Merkle paths as a sequence of hash elements.

#### PublicInputs

```nim
PublicInputs*[H] = object
  slotIndex*: int
  datasetRoot*: H
  entropy*: H
```

Contains the slot index, dataset root hash, and entropy hash.

#### ProofInputs

```nim
ProofInputs*[H] = object
  entropy*: H
  datasetRoot*: H
  slotIndex*: Natural
  slotRoot*: H
  nCellsPerSlot*: Natural
  nSlotsPerDataSet*: Natural
  slotProof*: seq[H]
  samples*: seq[Sample[H]]
```

Contains entropy, dataset root, slot index, slot root, number of cells per slot, number of slots per dataset, slot proof as a sequence of hashes, and samples as a sequence of `Sample` objects.

#### CircomCompat

```nim
CircomCompat* = object
  slotDepth: int # max depth of the slot tree
  datasetDepth: int # max depth of dataset  tree
  blkDepth: int # depth of the block merkle tree (pow2 for now)
  cellElms: int # number of field elements per cell
  numSamples: int # number of samples per slot
  r1csPath: string # path to the r1cs file
  wasmPath: string # path to the wasm file
  zkeyPath: string # path to the zkey file
  backendCfg: ptr CircomBn254Cfg
  vkp*: ptr CircomKey
```

Contains configuration for Circom compatibility including tree depths, paths to circuit artifacts (r1cs, wasm, zkey), backend configuration pointer, and verifying key pointer.

#### Proof

```rust
pub struct Proof {
    pub a: G1,
    pub b: G2,
    pub c: G1,
}
```

Groth16 proof structure containing three elements: `a` and `c` in G₁, and `b` in G₂.

#### G1

```rust
pub struct G1 {
    pub x: [u8; 32],
    pub y: [u8; 32],
}
```

Elliptic curve point in G₁ with x and y coordinates as 32-byte arrays.

#### G2

```rust
pub struct G2 {
    pub x: [[u8; 32]; 2],
    pub y: [[u8; 32]; 2],
}
```

Elliptic curve point in G₂ with x and y coordinates, each consisting of two 32-byte arrays.

#### VerifyingKey

```rust
pub struct VerifyingKey {
    pub alpha1: G1,
    pub beta2: G2,
    pub gamma2: G2,
    pub delta2: G2,
    pub ic: *const G1,
    pub ic_len: usize,
}
```

Groth16 verifying key structure containing `alpha1` in G₁, `beta2`, `gamma2`, and `delta2` in G₂, and an array of G₁ points (`ic`) with its length.

### Interfaces

#### Sampler Interfaces

| Interface | Description | Input | Output |
| --------- | ----------- | ----- | ------ |
| `new[T,H]` | Construct a `DataSampler` for a specific slot index. | `index: Natural`, `blockStore: BlockStore`, `builder: SlotsBuilder[T,H]` | `DataSampler[T,H]` |
| `getSample` | Retrieve one sampled cell and its Merkle path(s) for a given slot. | `cellIdx: int`, `slotTreeCid: Cid`, `slotRoot: H` | `Sample[H]` |
| `getProofInput` | Generate the full proof inputs for the proving circuit (calls `getSample` internally). | `entropy: ProofChallenge`, `nSamples: Natural` | `ProofInputs[H]` |

#### Prover Interfaces

| Interface | Description | Input | Output |
| --------- | ----------- | ----- | ------ |
| `new` | Construct a `Prover` with a block store and the backend proof system. | `blockStore: BlockStore`, `backend: AnyBackend`, `nSamples: int` | `Prover` |
| `prove` | Produce a succinct proof for the given slot and entropy. | `slotIdx: int`, `manifest: Manifest`, `entropy: ProofChallenge` | `(proofInputs, proof)` |
| `verify` | Verify a proof against its public inputs. | `proof: AnyProof`, `proofInputs: AnyProofInputs` | `bool` |

#### Circuit Interfaces

| Template | Description | Parameters | Inputs (signals) | Outputs (signals) |
| -------- | ----------- | ---------- | ---------------- | ----------------- |
| `SampleAndProve` | Main component in the circuit. Verifies `nSamples` cells (`cell->block->slot`) and the `slot->dataset` path, binding the proof to `dataSetRoot`, `slotIndex`, and `entropy`. | `maxDepth`, `maxLog2NSlots`, `blockTreeDepth`, `nFieldElemsPerCell`, `nSamples` | `entropy`, `dataSetRoot`, `slotIndex`, `slotRoot`, `nCellsPerSlot`, `nSlotsPerDataSet`, `slotProof[maxLog2NSlots]`, `cellData[nSamples][nFieldElemsPerCell]`, `merklePaths[nSamples][maxDepth]` | - |
| `ProveSingleCell` | Verifies one sampled cell: hashes `cellData` with Poseidon2 and checks the concatenated Merkle path up to `slotRoot`. | `nFieldElemsPerCell`, `botDepth`, `maxDepth` | `slotRoot`, `data[nFieldElemsPerCell]`, `lastBits[maxDepth]`, `indexBits[maxDepth]`, `maskBits[maxDepth+1]`, `merklePath[maxDepth]` | - |
| `RootFromMerklePath` | Reconstructs a Merkle root from a leaf and path using `KeyedCompression`. | `maxDepth` | `leaf`, `pathBits[maxDepth]`, `lastBits[maxDepth]`, `maskBits[maxDepth+1]`, `merklePath[maxDepth]` | `recRoot` |
| `CalculateCellIndexBits` | Derives the index bits for a sampled cell from `(entropy, slotRoot, counter)`, masked by `cellIndexBitMask`. | `maxLog2N` | `entropy`, `slotRoot`, `counter`, `cellIndexBitMask[maxLog2N]` | `indexBits[maxLog2N]` |

All parameters are compile-time constants that are defined when building the circuit.

#### Circuit Utility Templates

| Template | Description | Parameters | Inputs (signals) | Outputs (signals) |
| -------- | ----------- | ---------- | ---------------- | ----------------- |
| `Poseidon2_hash_rate2` | Poseidon2 fixed-length hash (rate = 2). Used for hashing cell field-elements. | `n`: number of field elements to hash. | `inp[n]`: array of field elements to hash. | `out`: Poseidon2 hash digest. |
| `PoseidonSponge` | Generic Poseidon2 sponge (absorb/squeeze). | `t`: sponge state width, `capacity`: capacity part of the state, `input_len`: number of elements to absorb, `output_len`: number of elements to squeeze | `inp[input_len]`: field elements to absorb. | `out[output_len]`: field elements squeezed. |
| `KeyedCompression` | Keyed 2->1 compression where key ∈ {0,1,2,3}. | - | `key`, `inp[2]`: left and right child node digests. | `out`: parent node digest |
| `ExtractLowerBits` | Extracts the lower `n` bits of `inp` (LSB-first). | `n`: number of low bits to extract | `inp`: field elements to extract. | `out[n]`: extracted bits. |
| `Log2` | Checks `inp == 2^out` with `0 < out <= n`. Also emits a mask vector with ones for indices `< out`. | `n`: max allowed bit width. | `inp`: field element. | `out`: exponent, `mask[n+1]`: prefix mask. |
| `CeilingLog2` | Computes `ceil(log2(inp))` and returns the bit-decomposition and a mask. | `n`: bit width of input and output. | `inp`: field element. | `out`: `ceil(log2(inp))`, `bits[n]`: bit decomposition, `mask[n+1]`: prefix mask |
| `BinaryCompare` | Compares two n-bit numbers `A` and `B` (LSB-first); outputs `-1` if `A<B`, `0` if equal, `+1` if `A>B`. | `n`: bit width of `A` and `B` | `A[n]`, `B[n]` | `out`: comparison result. |

## Security/Privacy Considerations

### Entropy Binding

Sample indices must be derived from the on-chain entropy and the slot commitment. This binds the proofs to specific cell indices and time period, and makes the challenge unpredictable until the period begins. This prevents storage providers from precomputing the proofs or selectively retaining a set of cells.

### Commitment Integrity

Proofs are checked against the publicly available Merkle commitments to the stored data. The proving module uses Poseidon2 Merkle roots as public commitments which allow anyone to verify proofs against the committed content.

### Soundness and Completeness

The zero-knowledge proof system must only accept valid proofs. Invalid inputs must not yield accepted proofs. The circuit enforces:

- Cell hashing using Poseidon2 sponge
- Merkle tree membership checks at all levels (cell -> block, block -> slot, slot -> dataset)
- Correct sampling index derivation from entropy and slot root

### Keyed Merkle Tree Compression

Codex extends the standard Merkle tree with a keyed compression that encodes whether a node is on the bottom layer and whether a node is odd or even. These bits are fed into the hash so tree shape cannot be manipulated.

### Proof Window

Storage providers must submit valid proofs within the proof window deadline. This time constraint ensures timely verification and allows the marketplace to manage incentives appropriately.

## Rationale

This specification is based on the Proving module component specification from the [Codex project](https://github.com/codex-storage/nim-codex).

### Probabilistic Verification

The proving module uses random sampling combined with erasure coding to provide probabilistic guarantees of data availability while touching only a tiny fraction of the stored data per challenge. This approach balances security with efficiency, as verifying the entire dataset for every challenge would be prohibitively expensive.

### Groth16 over BN254

The specification uses Groth16 zero-knowledge proofs over the BN254 elliptic curve. This choice provides:

- **Succinct proofs**: Small proof size enables efficient on-chain verification
- **EVM compatibility**: BN254 precompiles on EVM chains minimize verification costs
- **Strong security**: Groth16 provides computational zero-knowledge and soundness

### Poseidon2 Hash Function

Poseidon2 is used for all cryptographic commitments (cell hashing, Merkle tree construction). Poseidon2 is optimized for zero-knowledge circuits, resulting in significantly fewer constraints compared to traditional hash functions like SHA-256.

### Keyed Compression Design

The keyed compression scheme that depends on node position (bottom layer vs. internal) and child count (odd vs. even) prevents tree shape manipulation attacks. By feeding these bits into the hash function, the commitment binds to the exact tree structure.

### Pluggable Backend Architecture

The proving module uses a pluggable proving backend abstraction. While the current implementation uses Groth16 over BN254 with Circom circuits, this architecture allows for future flexibility to adopt different proof systems or curves without changing the core proving module logic.

### Entropy-Based Sampling

Deriving sample indices deterministically from public entropy (e.g., blockhash) and the slot commitment ensures that:

- Challenges are unpredictable until the period begins
- Storage providers cannot precompute proofs
- Storage providers cannot selectively retain only a subset of cells
- Any honest party can verify the sampling was done correctly

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- **Codex**: [GitHub - codex-storage/nim-codex](https://github.com/codex-storage/nim-codex)
- **Codex Prover Specification**: [Codex Docs - Component Specification - Prover](https://github.com/codex-storage/codex-docs-obsidian/blob/main/10%20Notes/Specs/Component%20Specification%20-%20Prover.md)
- **CODEX-SLOT-BUILDER**: Codex Slot Builder specification (defines `SlotsBuilder`
  and slot commitment construction)

### Informative

- **Codex Storage Proofs Circuits**: [GitHub - codex-storage/codex-storage-proofs-circuits](https://github.com/codex-storage/codex-storage-proofs-circuits) - Circom implementations of Codex's proof circuits targeting Groth16 over BN254
- **Nim Circom Compat**: [GitHub - codex-storage/nim-circom-compat](https://github.com/codex-storage/nim-circom-compat) - Nim bindings that load compiled Circom artifacts
- **Circom Compat FFI**: [GitHub - codex-storage/circom-compat-ffi](https://github.com/codex-storage/circom-compat-ffi) - Rust library with C ABI for running Arkworks Groth16 proving and verification on BN254
- **Groth16**: Jens Groth. "On the Size of Pairing-based Non-interactive Arguments." EUROCRYPT 2016
- **Poseidon2**: Lorenzo Grassi, Dmitry Khovratovich, Markus Schofnegger. "Poseidon2: A Faster Version of the Poseidon Hash Function." IACR ePrint 2023/323
