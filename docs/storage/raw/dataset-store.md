# DATASET-STORE

| Field | Value |
| --- | --- |
| Name   | Dataset Store                        |
| Slug | 151 |
| Status | raw                                  |
| Category | Standards Track |
| Editor | Giuliano Mega <giuliano@status.im>   |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/raw/dataset-store.md) — chore: add math support (#287)
- **2026-02-05** — [`4d0ee49`](https://github.com/logos-co/logos-lips/blob/4d0ee4929bd2c5037f72e3ca544f116f4c6fe39d/docs/storage/raw/dataset-store.md) — feat: Logos Storage dataset store (#278)

<!-- timeline:end -->

## Abstract

This specification contains the interface for a simple local storage component, named the Dataset Store, which supports Logos Storage nodes in storing and keeping track of partial and complete datasets along with their metadata on-disk, and provides basic support for dataset caching.

**Keywords.** dataset, block, dataset storage, caching, local storage, Logos Storage

## Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Interface

The interface is specified as pseudo-Python. The focus here is on primitive semantics, not code realism. In particular, we will ignore:

1. whether the operations are run synchronously or asynchronously, in a single thread or in multiple threads;
2. error conditions which are not domain specific; e.g. `IOError` does not belong here, whereas `QuotaExceededError` perhaps does. Errors are presented as exceptions, but these can be mapped into result types in languages that support or have a preference for them;
3. methods which could be present for efficiency reasons. Those can be added at the discretion of the implementor.

A DatasetStore is typically mounted on a local folder. Implementations will therefore typically provide, at its simplest:

```python
def new_dataset_store(path: Path, quota: uint): DatasetStore
  """Creates a new `DatasetStore`, which can hold up to `quota`
  bytes worth of `Datasets`."""
  ...
```

**Listing 1.** Creating a new DatasetStore.

High-level `Dataset` creation/deletion operations, as well as quota management and caching operations, are provided at the `DatasetStore` interface, shown in Listing 2. Block-level operations are provided in the `Dataset` interface, shown in Listing 3.

The `DatasetStore`/`Dataset` interfaces rely on a few external pseudotypes:

1. `BytesIO` represents a generic read or write byte stream;
2. `Bitset` is a fixed-size set - typically represented as a bit array - which encodes an integer set. Bit $i$ in this array is set to $1$ if $i$ is in the set, or $0$ otherwise;
3. `CID` represents a libp2p [Content Identifier](https://github.com/multiformats/cid);
4. `Manifest` represents a [Logos Storage Manifest](./datasets.md);
5. `Block` represents an arbitrary chunk of data;
6. `MerkleProof` represents a Merkle inclusion proof for a `Block`.

We omit the `self` parameter from all method signatures for brevity.

```python
class DatasetStore:

  def remaining() -> uint:
    """Returns the free available space in this DatasetStore, in bytes.
    This MUST be equal to the quota minus the size of all Datasets
    in this store. Partially completed Datasets MUST count with their
    full size, even if not all of the Dataset blocks are available locally.
    """
    ...

  def create_dataset(
    stream: BytesIO,
    block_size: uint,
    file_name: Optional[string] = None,
    mime_type: Optional[MimeType] = None,
  ) -> Dataset:
    """Creates a new Dataset from a byte stream and stores
    it on disk. Store quota SHOULD be deducted as the stream gets
    processed. Errors in this method SHOULD cause the
    `DatasetStore` to clean up the partially created `Dataset`,
    and return the quota back to the pool.

    :raises QuotaExceededError: if quota is exceeded.
    """
    ...

  def create_empty(manifest: Manifest) -> Dataset:
    """Creates a `Dataset` with the size described in the
    `Manifest`, but no completed blocks; i.e., an empty
    `Dataset`.

    :raises DatasetExistsError: if the dataset already exists.
    :raises QuotaExceededError: if quota would be exceeded by creating this dataset.
    """
    ...

  def get_dataset(cid: CID) -> Optional[Dataset]:
    """Returns a `Dataset` previously stored on-disk, or
    None if the `Dataset` is not present.

    :param cid: The Manifest's CID.
    """
    ...

  def delete_dataset(cid: CID) -> bool:
    """Removes a `Dataset` from disk, along with all of its
    associated metadata.

    :return: `false` if no `Dataset` corresponding to the
    provided CID is found on-disk; `true` otherwise.
    """
    ...

  def lru() -> Iterator[Dataset]:
    """Returns datasets in Least-Recently Used order.
    Nodes can use this to implement cache eviction; e.g.,
    when the quota is about to run out.

    LRU order is defined by the last time a dataset was accessed
    (read or written, both at the dataset or block level).
    """
    ...
```

**Listing 2.** DatasetStore interface.

```python
class Dataset:
  def manifest() -> Manifest:
    """Returns the `Manifest` for this dataset.
    """
    ...

  def blockmap() -> Bitset:
    """Returns a `Bitset` in which the indexes of
    all completed blocks are set. Unset bits correspond
    instead to missing blocks.
    """
    ...

  def completion() -> Tuple[uint, uint]:
    """Returns a tuple (a, b) where:
      * a = blockmap.cardinality(), and;
      * b = manifest.block_count

    If a == b, then we have all the blocks on disk;
    i.e., the dataset is complete.
    """
    ...

  def put_block(
    block: Block,
    index: uint,
    proof: MerkleProof,
  ) -> None:
    """Stores the given `Block` as the index-th block
    of this `Dataset`, verifying and storing its Merkle
    inclusion as part of that process. Calling this method
    for a block that is already present is a no-op.

    :raises InvalidProofError: if the Merkle proof provided
      in `proof` fails to verify.
    """
    ...

  def get_block(
    index: uint,
  ) -> Optional[Tuple[Block, MerkleProof]]:
    """Retrieves and returns the block at index `index`, together
    with its Merkle proof, if present. Otherwise returns None.
    """
    ...

  def data() -> BytesIO:
    """Allows one to stream the contents of a dataset.
    The stream MUST block if it bumps into an incomplete
    block, until the block is again available.
    """
    ...

```

**Listing 3.** Dataset interface.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [DATASETS](/storage/raw/datasets.md)
2. [Content Identifier Specification](https://github.com/multiformats/cid)
