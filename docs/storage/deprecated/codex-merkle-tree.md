# CODEX-MERKLE-TREE

| Field | Value |
| --- | --- |
| Name | Codex Merkle Tree |
| Slug | 82 |
| Status | deprecated |
| Category | Standards Track |
| Editor | Codex Team |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/deprecated/codex-merkle-tree.md) — chore: add math support (#287)
- **2026-02-06** — [`af4cd78`](https://github.com/logos-co/logos-lips/blob/af4cd78ffaeb12026c166df80d7c9fec5c2efb86/docs/storage/deprecated/codex-merkle-tree.md) — feat: revamped Merkle tree spec (#281)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/codex-merkle-tree.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/codex-merkle-tree.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Merkle tree implementation
for [Codex](https://github.com/codex-storage/nim-codex).
The purpose of this component is to deal with Merkle trees
(and Merkle trees only;
except that certain arithmetic hashes constructed via the sponge construction
use the same encoding standards).

## Background / Rationale / Motivation

Merkle trees and Merkle tree roots are used for:

- content addressing (via the Merkle root hash)
- data authenticity (via a Merkle path from a block to the root)
- remote auditing (via Merkle proofs of pieces)

Merkle trees can be implemented in quite a few different ways,
and if naively implemented, can be also attacked in several ways.

Some possible attacks:

- **Data encoding attacks**: occur when different byte sequences
  can be encoded to the same target type, potentially creating collisions
- **Padding attacks**: occur when different data
  can be padded to produce identical hashes
- **Layer abusing attacks**: occur when nodes from different layers
  can be substituted or confused with each other

These all can create root hash collisions for example.

Hence, a concrete implementation is specified
which should be safe from these attacks through:

1. **Injective encoding**: The `10*` padding strategy ensures
   that different byte sequences always encode to different target types
2. **Keyed compression**: Using distinct keys for different node types
   (even/odd, bottom/other layers) prevents node substitution attacks
3. **Deterministic construction**: The layer-by-layer construction
   with explicit handling of singleton nodes ensures consistent tree building

The specification supports multiple hash function types
(SHA256, Poseidon2, Goldilocks)
while maintaining these security properties across all implementations.

Storing Merkle trees on disc is out of scope here
(but should be straightforward,
as serialization of trees should be included in the component).

## Theory / Semantics

## Vocabulary

A Merkle tree, built on a hash function `H`,
produces a Merkle root of type `T` ("Target type").
This is usually the same type as the output of the hash function
(this is assumed below).
Some examples:

- SHA1: `T` is 160 bits
- SHA256: `T` is 256 bits
- Keccak (SHA3): `T` can be one of 224, 256, 384 or 512 bits
- Poseidon: `T` is one or more finite field element(s) (based on the field size)
- Monolith: `T` is 4 [Goldilocks](https://github.com/codex-storage/nim-goldilocks-hash) field elements

The hash function `H` can also have different types `S` ("Source type") of inputs.
For example:

- SHA1 / SHA256 / SHA3: `S` is an arbitrary sequence of bits
- some less-conforming implementation of these
  could take a sequence of bytes instead (but that's often enough in practice)
- binary compression function: `S` is a pair of `T`-s
- Poseidon: `S` is a sequence of finite field elements
- [Poseidon2](https://github.com/codex-storage/nim-poseidon2) compression function:
  `S` is at most `t-k` field elements,
  where `k` field elements should be approximately 256 bits
  (in our case `t=3`, `k=1` for BN254 field;
  or `t=12`, `k=4` for the [Goldilocks](https://github.com/codex-storage/nim-goldilocks-hash) field;
  or `t=24`, `k=8` for a ~32 bit field)
- as an alternative,
  the "[Jive compression mode](https://eprint.iacr.org/2022/840)" for binary compression
  can eliminate the "minus `k`" requirement (you can compress `t` into `t/2`)
- A naive Merkle tree implementation could for example
  accept only a power-of-two sized sequence of `T`

Notation: Let's denote a sequence of `T`-s by `[T]`;
and an array of `T`-s of length `l` by `T[l]`.

## Data Models

- `H`, the set of supported hash functions, is an enumeration
- `S := Source[H]` and `T := Target[H]`
- `MerklePath[H]` is a record, consisting of
  - `path`: a sequence of `T`-s
  - `index`: a linear index (int)
  - `leaf`: the leaf being proved (a `T`)
  - `size`: the number of elements from which the tree was created
- `MerkleTree[H]`: a binary tree of `T`-s;
  alternatively a sequence of sequences of `T`-s

## Tree Construction

We want to avoid the following kind of attacks:

- padding attacks
- layer abusing attacks

Hence, instead of using a single compression functions,
a _keyed compression function_ is used, which is keyed by two bits:

- whether the new parent node is an even or odd node
  (that is, has 2 or 1 children;
  alternatively, whether compressing 2 or 1 nodes)
- whether it's the bottom (the widest, initial) layer or not

This information is converted to a number `0 <= key < 4`
by the following algorithm:

```haskell
data LayerFlag
  = BottomLayer   -- ^ it's the bottom (initial, widest) layer
  | OtherLayer    -- ^ it's not the bottom layer

data NodeParity
  = EvenNode      -- ^ it has 2 children
  | OddNode       -- ^ it has 1 child

-- | Key based on the node type:
--
-- > bit0 := 1 if bottom layer, 0 otherwise
-- > bit1 := 1 if odd, 0 if even
--
nodeKey :: LayerFlag -> NodeParity -> Int
nodeKey OtherLayer  EvenNode = 0x00
nodeKey BottomLayer EvenNode = 0x01
nodeKey OtherLayer  OddNode  = 0x02
nodeKey BottomLayer OddNode  = 0x03
```

This number is used to key the compression function
(essentially, 4 completely different compression functions).

When the hash function is a finite field sponge based,
like [Poseidon2](https://github.com/codex-storage/nim-poseidon2) or Monolith,
the following construction is used:
The permutation function is applied to `(x,y,key)`,
and the first component of the result is taken.

When the hash function is something like SHA256,
the following is done: `SHA256(key|x|y)` (here `key` is encoded as a byte).
SHA256 implementation uses [bearssl](https://bearssl.org/).

Remark: Since standard SHA256 includes padding,
adding a key at the beginning doesn't result in extra computation
(it's always two internal hash calls).
However, a faster (twice as fast) alternative would be
to choose 4 different random-looking initialization vectors,
and not do padding.
This would be a non-standard SHA256 invocation.

Finally, the process proceeds from the initial sequence in layers:
Take the previous sequence,
apply the keyed compression function for each consecutive pairs `(x,y) : (T,T)`
with the correct key:
based on whether this was the initial (bottom) layer,
and whether it's a singleton "pair" `x : T`,
in which case it's also padded with a zero to `(x,0)`.

Note: If the input was a singleton list `[x]`,
one layer is still applied,
so in that case the root will be `compress[key=3](x,0)`.

## Encoding and (De)serialization from/to Bytes

This has to be done very carefully to avoid potential attacks.

Note: This is a rather special situation,
in that encoding and serialization are **NOT THE INVERSE OF EACH OTHER**.
The reason for this is that they have different purposes:
In case of encoding from bytes to `T`-s,
it MUST BE injective to avoid trivial collision attacks;
while when serializing from `T`-s to bytes,
it needs to be invertible
(so that what is stored on disk can be loaded back;
in this sense this is really 1+2 = 3 algorithms).

The two can coincide when `T` is just a byte sequence like in SHA256,
but not when `T` consists of prime field elements.

Remark: The same encoding of sequence of bytes to sequence of `T`-s
is used for the sponge hash construction, when applicable.

### Encoding into a Single T

For any `T = Target[H]`,
fix a size `M` and an injective encoding `byte[M] -> T`.
For SHA256 etc, this will be standard encoding (big-endian; `M=32`).

For the BN254 field (`T` is 1 field element),
`M=31`, and the 31 bytes interpreted as a _little-endian_ integer modulo `p`.

For the [Goldilocks](https://github.com/codex-storage/nim-goldilocks-hash) field,
there are some choices:
`M=4*7=28` can be used, as a single field element can encode 7 bytes but not 8.
Or, for more efficiency,
`M=31` can still be achieved by storing 62 bits in each field element.
For this some convention needs to be chosen;
the implementation is the following:

```c
#define MASK 0x3fffffffffffffffULL

// NOTE: we assume a little-endian architecture here
void goldilocks_convert_31_bytes_to_4_field_elements(const uint8_t *ptr, uint64_t *felts) {
  const uint64_t *q0  = (const uint64_t*)(ptr   );
  const uint64_t *q7  = (const uint64_t*)(ptr+ 7);
  const uint64_t *q15 = (const uint64_t*)(ptr+15);
  const uint64_t *q23 = (const uint64_t*)(ptr+23);

  felts[0] =  (q0 [0]) & MASK;
  felts[1] = ((q7 [0]) >> 6) | ((uint64_t)(ptr[15] & 0x0f) << 58);
  felts[2] = ((q15[0]) >> 4) | ((uint64_t)(ptr[23] & 0x03) << 60);
  felts[3] = ((q23[0]) >> 2);
}
```

This simply chunks the 31 bytes = 248 bits into 62 bits chunks,
and interprets them as little endian 62 bit integers.

### Encoding from a Sequence of Bytes

First, the _byte sequence_ is padded with the `10*` padding strategy
to a multiple of `M` bytes.

This means that a `0x01` byte is _always_ added,
and then as many `0x00` bytes as required for the length to be divisible by `M`.
If the input was `l` bytes,
then the padded sequence will have `M*(floor(l/M)+1)` bytes.

Note: the `10*` padding strategy is an invertible operation,
which will ensure that there is no collision
between sequences of different length.

This padded byte sequence is then chunked to pieces of `M` bytes
(so there will be `floor(l/M)+1` chunks),
and the above fixed `byte[M] -> T` is applied for each chunk,
resulting in the same number of `T`-s.

Remark: The sequence of `T`-s is not padded
when constructing the Merkle tree
(as the tree construction ensures
that different lengths will result in different root hashes).
However, when **using the sponge construction,**
the sequence of `T`-s needs to be further padded
to be a multiple of the sponge rate;
there again the `10*` strategy is applied,
but there the `1` and `0` are finite field elements.

### Serializing / Deserializing

When using SHA256 or similar,
this is trivial (use the standard, big-endian encoding).

When `T` consists of prime field elements,
simply take the smallest number of bytes the field fits in
(usually 256, 64 or 32 bits, that is 32, 8 or 4 bytes),
and encode as a little-endian integer (mod the prime).

This is obvious to invert.

### Tree Serialization

Just add enough metadata that the size of each layer is known,
then the layers can simply be concatenated,
and serialized as above.
This metadata can be as small as the size of the initial layer,
that is, a single integer.

## Wire Format Specification / Syntax

## Interfaces

At least two types of Merkle tree APIs are usually needed:

- one which takes a sequence `S = [T]` of length `n` as input,
  and produces an output (Merkle root) of type `T`
- and one which takes a sequence of bytes
  (or even bits, but in practice only bytes are probably needed): `S = [byte]`

The latter can be decomposed into the composition
of an `encodeBytes` function and the former
(it's safer this way, because there are a lot of subtle details here).

| Interface        | Description                | Input                   | Output                  |
|------------------|-----------------------------|-------------------------|-------------------------|
| computeTree()   | computes the full Merkle tree | sequence of `T`-s | a MerkleTree[T] data structure (a binary tree) |
| computeRoot()   | computes the Merkle root of a sequence of `T`-s | sequence of `T`-s | a single `T` |
| extractPath() | computes a Merkle path | MerkleTree[T] and a leaf index | MerklePath[T] |
| checkMerkleProof() | checks the validity of a Merkle path proof | root hash (a `T`) and MerklePath[T] | a bool (ok or not) |
| encodeBytesInjective()| converts a sequence of bytes into a sequence of `T`-s, injectively | seqences of bytes | sequence of `T`-s |
| serializeToBytes() | serializes a sequence of `T`-s into bytes | sequence of `T`-s | sequence of bytes |
| deserializeFromBytes() | deserializes a sequence of `T`-s from bytes | sequence of bytes | sequence of `T`-s, or error |
| serializeTree() | serializes the Merkle tree data structure (to be stored on disk) | MerkleTree[T] | sequence of bytes |
| deserializeTree() | deserializes the Merkle tree data structure (to be load from disk) | sequence of bytes | error or MerkleTree[T] |

## Dependencies

Hash function implementations, for example:

- [bearssl](https://bearssl.org/) (for SHA256)
- [nim-poseidon2](https://github.com/codex-storage/nim-poseidon2) (which should be renamed to `nim-poseidon2-bn254`)
- [nim-goldilocks-hash](https://github.com/codex-storage/nim-goldilocks-hash)

## Security/Privacy Considerations

### Attack Mitigation

The specification addresses three major attack vectors:

1. **Data encoding attacks**: Prevented by using injective encoding
   from bytes to target types with the `10*` padding strategy.
   The strategy always adds a `0x01` byte followed by `0x00` bytes
   to reach a multiple of `M` bytes,
   ensuring that different byte sequences of different lengths
   cannot encode to the same target type.

2. **Padding attacks**: Prevented by the keyed compression function
   that distinguishes between even and odd nodes.
   When a node has only one child (odd node),
   it is padded with zero to form a pair `(x,0)`,
   but the compression function uses a different key (0x02 or 0x03)
   than for even nodes (0x00 or 0x01),
   preventing confusion between padded and non-padded nodes.

3. **Layer abusing attacks**: Prevented by the keyed compression function
   that distinguishes between bottom layer and other layers.
   The bottom layer uses keys with bit0 set to 1 (0x01 or 0x03),
   while other layers use keys with bit0 set to 0 (0x00 or 0x02),
   preventing nodes from different layers from producing identical hashes.

### Keyed Compression Function

The keyed compression function uses four distinct keys
(0x00, 0x01, 0x02, 0x03) based on two bits:

- **bit0**: Set to 1 if bottom layer, 0 otherwise
- **bit1**: Set to 1 if odd node (1 child), 0 if even node (2 children)

This ensures that different structural positions in the tree
cannot produce hash collisions, as:

- For finite field sponge hash functions (Poseidon2, Monolith):
  The permutation is applied to `(x,y,key)` and the first component is extracted
- For standard hash functions (SHA256):
  The hash is computed as `SHA256(key|x|y)` where `key` is encoded as a byte

### Hash Function Flexibility

The specification is parametrized by the hash function,
allowing different implementations to use appropriate hash functions
for their context while maintaining consistent security properties.
All supported hash functions must maintain the injective encoding property
and support the keyed compression function pattern.

## Rationale

### Keyed Compression Design

The use of a keyed compression function with four distinct keys
is the primary defense mechanism against theoretical attacks.
By encoding both the layer position (bottom vs. other)
and node parity (even vs. odd) into the compression function,
the design ensures that:

- Nodes at different layers cannot be confused
- Even and odd nodes produce different hashes even with the same input data
- Padding attacks are prevented by distinguishing singleton nodes from pair nodes

### Encoding vs. Serialization Separation

The specification explicitly separates encoding and serialization
as distinct operations:

- **Encoding** (bytes to `T`-s) must be injective to prevent collision attacks
- **Serialization** (`T`-s to bytes) must be invertible to enable storage and retrieval

This separation is necessary because they serve different purposes.
The two operations only coincide when `T` is a byte sequence (as in SHA256),
but differ when `T` consists of prime field elements.

### 10* Padding Strategy

The `10*` padding strategy
(always adding `0x01` followed by `0x00` bytes)
is an invertible operation
that ensures no collision between sequences of different lengths.
This is applied at the byte level before chunking into `M`-byte pieces.

### Parametrized Hash Function Design

The design is parametrized by the hash function, supporting:

- Standard hash functions (SHA256, SHA3)
- Finite field-based sponge constructions
  ([Poseidon2](https://github.com/codex-storage/nim-poseidon2), Monolith)
- Binary compression functions

This flexibility allows easy addition of new hash functions
while maintaining security guarantees.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### normative

- **Codex Merkle Tree Implementation**: [GitHub - codex-storage/nim-codex](https://github.com/codex-storage/nim-codex)

### informative

- **Merkle Tree Conventions**: [GitHub - codex-storage-proofs-circuits](https://github.com/codex-storage/codex-storage-proofs-circuits/blob/master/README.md#merkle-tree-conventions) - Merkle tree specification in codex-storage-proofs-circuits
- **nim-poseidon2**: [GitHub - codex-storage/nim-poseidon2](https://github.com/codex-storage/nim-poseidon2) - Poseidon2 hash function for BN254
- **nim-goldilocks-hash**: [GitHub - codex-storage/nim-goldilocks-hash](https://github.com/codex-storage/nim-goldilocks-hash) - Goldilocks field hash functions
- **BearSSL**: [bearssl.org](https://bearssl.org/) - BearSSL cryptographic library
- **Jive Compression Mode**: [Anemoi Permutations and Jive Compression Mode](https://eprint.iacr.org/2022/840) - Efficient arithmetization-oriented hash functions
