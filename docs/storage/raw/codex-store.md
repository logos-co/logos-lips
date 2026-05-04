# CODEX-STORE

| Field | Value |
| --- | --- |
| Name | Codex Store Module |
| Slug | 80 |
| Status | raw |
| Category | Standards Track |
| Editor | Codex Team |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/codex-store.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/codex-store.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification describes the Store Module,
the core storage abstraction in [Codex](https://github.com/codex-storage/nim-codex),
providing a unified interface for storing and retrieving content-addressed blocks
and associated metadata.

The Store Module decouples storage operations from underlying datastore semantics
by introducing the `BlockStore` interface,
which standardizes methods for storing and retrieving both ephemeral
and persistent blocks across different storage backends.
The module integrates a maintenance engine responsible for cleaning up
expired ephemeral data according to configured policies.

The Store Module is built on top of the generic
[DataStore (DS) interface](https://github.com/codex-storage/nim-datastore/blob/master/datastore/datastore.nim),
which is implemented by multiple backends such as SQLite, LevelDB,
and the filesystem.

## Background / Rationale / Motivation

The primary design goal is to decouple storage operations from the underlying
datastore semantics by introducing the `BlockStore` interface.
This interface standardizes methods for storing and retrieving both ephemeral
and persistent blocks,
ensuring a consistent API across different storage backends.

The DataStore provides a KV-store abstraction with `Get`, `Put`, `Delete`,
and `Query` operations, with backend-dependent guarantees.
At a minimum, row-level consistency and basic batching are expected.

The DataStore supports:

- Namespace mounting for isolating backend usage
- Layering backends (e.g., caching in front of persistent stores)
- Flexible stacking and composition of storage proxies

The current implementation has several limitations:

- No dataset-level operations or advanced batching support
- Lack of consistent locking and concurrency control,
  which may lead to inconsistencies during crashes or long-running operations
  on block groups (e.g., reference count updates, expiration updates)

## Theory / Semantics

### BlockStore Interface

The `BlockStore` interface provides the following methods:

| Method | Description | Input | Output |
| --- | --- | --- | --- |
| `getBlock(cid: Cid)` | Retrieve block by CID | CID | `Future[?!Block]` |
| `getBlock(treeCid: Cid, index: Natural)` | Retrieve block from a Merkle tree by leaf index | Tree CID, index | `Future[?!Block]` |
| `getBlock(address: BlockAddress)` | Retrieve block via unified address | BlockAddress | `Future[?!Block]` |
| `getBlockAndProof(treeCid: Cid, index: Natural)` | Retrieve block with Merkle proof | Tree CID, index | `Future[?!(Block, CodexProof)]` |
| `getCid(treeCid: Cid, index: Natural)` | Retrieve leaf CID from tree metadata | Tree CID, index | `Future[?!Cid]` |
| `getCidAndProof(treeCid: Cid, index: Natural)` | Retrieve leaf CID with inclusion proof | Tree CID, index | `Future[?!(Cid, CodexProof)]` |
| `putBlock(blk: Block, ttl: Duration)` | Store block with quota enforcement | Block, optional TTL | `Future[?!void]` |
| `putCidAndProof(treeCid: Cid, index: Natural, blkCid: Cid, proof: CodexProof)` | Store leaf metadata with ref counting | Tree CID, index, block CID, proof | `Future[?!void]` |
| `hasBlock(...)` | Check block existence (CID or tree leaf) | CID / Tree CID + index | `Future[?!bool]` |
| `delBlock(...)` | Delete block/tree leaf (with ref count checks) | CID / Tree CID + index | `Future[?!void]` |
| `ensureExpiry(...)` | Update expiry for block/tree leaf | CID / Tree CID + index, expiry timestamp | `Future[?!void]` |
| `listBlocks(blockType: BlockType)` | Iterate over stored blocks | Block type | `Future[?!SafeAsyncIter[Cid]]` |
| `getBlockExpirations(maxNumber, offset)` | Retrieve block expiry metadata | Pagination params | `Future[?!SafeAsyncIter[BlockExpiration]]` |
| `blockRefCount(cid: Cid)` | Get block reference count | CID | `Future[?!Natural]` |
| `reserve(bytes: NBytes)` | Reserve storage quota | Bytes | `Future[?!void]` |
| `release(bytes: NBytes)` | Release reserved quota | Bytes | `Future[?!void]` |
| `start()` | Initialize store | — | `Future[void]` |
| `stop()` | Gracefully shut down store | — | `Future[void]` |
| `close()` | Close underlying datastores | — | `Future[void]` |

### Store Implementations

The Store module provides three concrete implementations of the `BlockStore`
interface,
each optimized for a specific role in the Codex architecture:
RepoStore, NetworkStore, and CacheStore.

#### RepoStore

The RepoStore is a persistent `BlockStore` implementation
that interfaces directly with low-level storage backends,
such as hard drives and databases.

It uses two distinct DataStore backends:

- FileSystem — for storing raw block data
- LevelDB — for storing associated metadata

This separation ensures optimal performance,
allowing block data operations to run efficiently
while metadata updates benefit from a fast key-value database.

Characteristics:

- Persistent storage via datastore backends
- Quota management with precise usage tracking
- TTL (time-to-live) support with automated expiration
- Metadata storage for block size, reference count, and expiry
- Transaction-like operations implemented through reference counting

Configuration:

- `quotaMaxBytes`: Maximum storage quota
- `blockTtl`: Default TTL for stored blocks
- `postFixLen`: CID key postfix length for sharding

```text
┌─────────────────────────────────────────────────────────────┐
│                        RepoStore                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐              ┌──────────────────────────┐  │
│  │  repoDs     │              │       metaDs             │  │
│  │ (Datastore) │              │  (TypedDatastore)        │  │
│  │             │              │                          │  │
│  │ Block Data: │              │ Metadata:                │  │
│  │ - Raw bytes │              │ - BlockMetadata          │  │
│  │ - CID-keyed │              │ - LeafMetadata           │  │
│  │             │              │ - QuotaUsage             │  │
│  │             │              │ - Block counts           │  │
│  └─────────────┘              └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### NetworkStore

The NetworkStore is a composite `BlockStore` that combines local persistence
with network-based retrieval for distributed content access.

It follows a local-first strategy —
attempting to retrieve or store blocks locally first,
and falling back to network retrieval via the Block Exchange Engine
if the block is not available locally.

Characteristics:

- Integrates local storage with network retrieval
- Works seamlessly with the block exchange engine for peer-to-peer access
- Transparent block fetching from remote sources
- Local caching of blocks retrieved from the network for future access

```text
┌────────────────────────────────────────────────────────────┐
│                      NetworkStore                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────┐           ┌──────────────────────┐    │
│  │ LocalStore - RS │           │   BlockExcEngine     │    │
│  │ • Store blocks  │           │ • Request blocks     │    │
│  │ • Get blocks    │           │ • Resolve blocks     │    │
│  └─────────────────┘           └──────────────────────┘    │
│           │                              │                 │
│           └──────────────┬───────────────┘                 │
│                          │                                 │
│                   ┌─────────────┐                          │
│                   │BS Interface │                          │
│                   │             │                          │
│                   │ • getBlock  │                          │
│                   │ • putBlock  │                          │
│                   │ • hasBlock  │                          │
│                   │ • delBlock  │                          │
│                   └─────────────┘                          │
└────────────────────────────────────────────────────────────┘
```

#### CacheStore

The CacheStore is an in-memory `BlockStore` implementation
designed for fast access to frequently used blocks.

This store maintains two separate LRU caches:

1. Block Cache — `LruCache[Cid, Block]`
    - Stores actual block data indexed by CID
    - Acts as the primary cache for block content
2. CID/Proof Cache — `LruCache[(Cid, Natural), (Cid, CodexProof)]`
    - Maps `(treeCid, index)` to `(blockCid, proof)`
    - Supports direct access to block proofs keyed by `treeCid` and index

Characteristics:

- O(1) access times for cached data
- LRU eviction policy for memory management
- Configurable maximum cache size
- No persistence — cache contents are lost on restart
- No TTL — blocks remain in cache until evicted

Configuration:

- `cacheSize`: Maximum total cache size (bytes)
- `chunkSize`: Minimum block size unit

### Storage Layout

| Key Pattern | Data Type | Description | Example |
| --- | --- | --- | --- |
| `repo/manifests/{XX}/{full-cid}` | Raw bytes | Manifest block data | `repo/manifests/Cd/bafy...Cd → [data]` |
| `repo/blocks/{XX}/{full-cid}` | Raw bytes | Block data | `repo/blocks/Ab/bafy...Ab → [data]` |
| `meta/ttl/{cid}` | BlockMetadata | Expiry, size, refCount | `meta/ttl/bafy... → {...}` |
| `meta/proof/{treeCid}/{index}` | LeafMetadata | Merkle proof for leaf | `meta/proof/bafy.../42 → {...}` |
| `meta/total` | Natural | Total stored blocks | `meta/total → 12039` |
| `meta/quota/used` | NBytes | Used quota | `meta/quota/used → 52428800` |
| `meta/quota/reserved` | NBytes | Reserved quota | `meta/quota/reserved → 104857600` |

### Workflows

The following flow charts summarize how put, get, and delete operations
interact with the shared block storage, metadata store,
and quota management systems.

#### PutBlock

The following flow chart shows how a block is stored
with metadata and quota management:

```text
putBlock: blk, ttl
  │
  ├─> Calculate expiry = now + ttl
  │
  ├─> storeBlock: blk, expiry
  │
  ├─> Block empty?
  │   ├─> Yes: Return AlreadyInStore
  │   └─> No: Create metadata & block keys
  │
  ├─> Block metadata exists?
  │   ├─> Yes: Size matches?
  │   │   ├─> Yes: Return AlreadyInStore
  │   │   └─> No: Return Error
  │   └─> No: Create new metadata
  │
  ├─> Store block data
  │
  ├─> Store successful?
  │   ├─> No: Return Error
  │   └─> Yes: Update quota usage
  │
  ├─> Quota update OK?
  │   ├─> No: Rollback: Delete block → Return Error
  │   └─> Yes: Update total blocks count
  │
  ├─> Trigger onBlockStored callback
  │
  └─> Return Success
```

#### GetBlock

The following flow chart explains how a block is retrieved by CID
or tree reference,
resolving metadata if necessary,
and returning the block or an error:

```text
getBlock: cid/address
  │
  ├─> Input type?
  │   ├─> BlockAddress with leaf
  │   │   └─> getLeafMetadata: treeCid, index
  │   │       ├─> Leaf metadata found?
  │   │       │   ├─> No: Return BlockNotFoundError
  │   │       │   └─> Yes: Extract block CID from metadata
  │   └─> CID: Direct CID access
  │
  ├─> CID empty?
  │   ├─> Yes: Return empty block
  │   └─> No: Create prefix key
  │
  ├─> Query datastore: repoDs.get
  │
  ├─> Block found?
  │   ├─> No: Error type?
  │   │   ├─> DatastoreKeyNotFound: Return BlockNotFoundError
  │   │   └─> Other: Return Error
  │   └─> Yes: Create Block with verification
  │
  └─> Return Block
```

#### DelBlock

The following flow chart shows how a block is deleted
when it is unused or expired,
including metadata cleanup and quota/counter updates:

```text
delBlock: cid
  │
  ├─> delBlockInternal: cid
  │
  ├─> CID empty?
  │   ├─> Yes: Return Deleted
  │   └─> No: tryDeleteBlock: cid, now
  │
  ├─> Metadata exists?
  │   ├─> No: Check if block exists in repo
  │   │   ├─> Block exists?
  │   │   │   ├─> Yes: Warn & remove orphaned block
  │   │   │   └─> No: Return NotFound
  │   │   └─> Return NotFound
  │   └─> Yes: refCount = 0 OR expired?
  │       ├─> No: Return InUse
  │       └─> Yes: Delete block & metadata → Return Deleted
  │
  ├─> Handle result
  │
  ├─> Result type?
  │   ├─> InUse: Return Error: Cannot delete dataset block
  │   ├─> NotFound: Return Success: Ignore
  │   └─> Deleted: Update total blocks count
  │               └─> Update quota usage
  │                   └─> Return Success
  │
  └─> Return Success
```

### Data Models

#### Stores

```nim
RepoStore* = ref object of BlockStore
  postFixLen*: int
  repoDs*: Datastore
  metaDs*: TypedDatastore
  clock*: Clock
  quotaMaxBytes*: NBytes
  quotaUsage*: QuotaUsage
  totalBlocks*: Natural
  blockTtl*: Duration
  started*: bool

NetworkStore* = ref object of BlockStore
  engine*: BlockExcEngine
  localStore*: BlockStore

CacheStore* = ref object of BlockStore
  currentSize*: NBytes
  size*: NBytes
  cache: LruCache[Cid, Block]
  cidAndProofCache: LruCache[(Cid, Natural), (Cid, CodexProof)]
```

#### Metadata Types

```nim
BlockMetadata* {.serialize.} = object
  expiry*: SecondsSince1970
  size*: NBytes
  refCount*: Natural

LeafMetadata* {.serialize.} = object
  blkCid*: Cid
  proof*: CodexProof

BlockExpiration* {.serialize.} = object
  cid*: Cid
  expiry*: SecondsSince1970

QuotaUsage* {.serialize.} = object
  used*: NBytes
  reserved*: NBytes
```

### Functional Requirements

#### Available Today

- Atomic Block Operations
  - Store, retrieve, and delete operations must be atomic.
  - Support retrieval via:
    - Direct CID
    - Tree-based addressing (`treeCid + index`)
    - Unified block address

- Metadata Management
  - Store protocol-level metadata (e.g., storage proofs, quota usage).
  - Store block-level metadata (e.g., reference counts, total block count).

- Multi-Datastore Support
  - Pluggable datastore interface supporting various backends.
  - Typed datastore operations for metadata type safety.

- Lifecycle & Maintenance
  - BlockMaintainer service for removing expired data.
  - Configurable maintenance intervals (default: 10 min).
  - Batch processing (default: 1000 blocks/cycle).

#### Future Requirements

- Transaction Rollback & Error Recovery
  - Rollback support for failed multi-step operations.
  - Consistent state restoration after failures.

- Dataset-Level Operations
  - Handle Dataset level meta data.
  - Batch operations for dataset block groups.

- Concurrency Control
  - Consistent locking and coordination mechanisms to prevent inconsistencies
    during crashes or long-running operations.

- Lifecycle & Maintenance
  - Cooperative scheduling to avoid blocking.
  - State tracking for large datasets.

### Non-Functional Requirements

#### Currently Implemented

- Security
  - Verify block content integrity upon retrieval.
  - Enforce quotas to prevent disk exhaustion.
  - Safe orphaned data cleanup.

- Scalability
  - Configurable storage quotas (default: 20 GiB).
  - Pagination for metadata queries.
  - Reference counting–based garbage collection.

- Reliability
  - Metrics collection (`codex_repostore_*`).
  - Graceful shutdown with resource cleanup.

#### Planned Enhancements

- Performance
  - Batch metadata updates.
  - Efficient key lookups with configurable prefix lengths.
  - Support for both fast and slower storage tiers.
  - Streaming APIs optimized for extremely large datasets.

- Security
  - Finer-grained quota enforcement across tenants/namespaces.

- Reliability
  - Stronger rollback semantics for multi-node consistency.
  - Auto-recovery from inconsistent states.

## Wire Format Specification / Syntax

The Store Module does not define a wire format specification.
It provides an internal storage abstraction
for [Codex](https://github.com/codex-storage/nim-codex)
and relies on underlying datastore implementations for serialization
and persistence.

## Security/Privacy Considerations

- Block Integrity: The Store Module verifies block content integrity
  upon retrieval to ensure data has not been corrupted or tampered with.

- Quota Enforcement: Storage quotas are enforced
  to prevent disk exhaustion attacks.
  The default quota is 20 GiB, but this is configurable.

- Safe Data Cleanup: The maintenance engine safely removes expired
  ephemeral data and orphaned blocks without compromising data integrity.

- Reference Counting: Reference counting–based garbage collection ensures
  that blocks are not deleted while they are still in use by other components.

Future security enhancements include finer-grained quota enforcement
across tenants/namespaces and stronger rollback semantics
for multi-node consistency.

## Rationale

The Store Module design prioritizes:

- Decoupling: By introducing the `BlockStore` interface,
  the Store Module decouples storage operations from underlying
  datastore semantics,
  allowing for flexible backend implementations.

- Performance: The separation of block data (filesystem) and metadata (LevelDB)
  in RepoStore ensures optimal performance for both types of operations.

- Flexibility: The three store implementations
  (RepoStore, NetworkStore, CacheStore) provide different trade-offs
  between persistence, network access, and performance,
  allowing Codex to optimize for different use cases.

- Scalability: Reference counting, quota management, and pagination enable
  the Store Module to scale to large datasets
  while preventing resource exhaustion.

The current limitations (lack of dataset-level operations, inconsistent locking)
are acknowledged and will be addressed in future versions.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### normative

- [Codex](https://github.com/codex-storage/nim-codex)
- [Component Specification - Store](https://github.com/codex-storage/codex-docs-obsidian/blob/main/10%20Notes/Specs/Component%20Specification%20-%20Store.md)

### informative

- [nim-datastore](https://github.com/codex-storage/nim-datastore)
- [DataStore Interface](https://github.com/codex-storage/nim-datastore/blob/master/datastore/datastore.nim)
- [chronos](https://github.com/status-im/nim-chronos) - Async runtime
- [libp2p](https://github.com/status-im/nim-libp2p) - P2P networking and CID types
- [questionable](https://github.com/codex-storage/questionable) - Error handling
- [lrucache](https://github.com/status-im/lrucache) - LRU cache implementation
