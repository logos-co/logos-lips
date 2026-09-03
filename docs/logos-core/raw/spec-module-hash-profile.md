# LOGOS-MODULE-HASH-PROFILE

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Hash Profile                                     |
| Slug         | 303                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the canonical physical hash profile for Logos
schema and value commitments.
It consumes the semantic schema and value trees defined by
LOGOS-MODULE-COMMITMENT-MODEL and uses that specification's semantic path
language for verified-view proofs.

This specification defines how semantic commitments are hashed.
It covers physical layout, packing, chunking, hash suite binding, domain
separation, exact hash inputs, and proof material.
It does not redefine the semantic schema model, normalized value model, or
semantic value tree.

## 1. Introduction

LOGOS-MODULE-COMMITMENT-MODEL defines what Logos commits to.
This specification defines the canonical physical hash profile for those
commitments.

The semantic commitment model and the physical hash profile are versioned
separately.
The commitment model defines two semantic trees:
the semantic schema tree and the semantic value tree.
This hash profile defines one physical hash layout over both trees, with
separate domain tags and payload shapes for schema objects and value objects.
A hash profile MUST state which semantic commitment-model revision it supports
and which value-model revision it supports if the commitment model defines one.
Changing a module schema does not require changing this specification.
Changing the semantic commitment model in a way that adds new node kinds,
changes normalization, or changes semantic paths may require a new hash profile
or an explicit extension of an existing profile.
Changing the semantic commitment-model revision supported by this profile does
not by itself require changing the hash profile identifier, as long as the
physical hash inputs and verification rules defined by this profile remain
unchanged.

A direct semantic-tree hash is useful as an explanatory and conformance
reference.
It is not the canonical production value-root profile in this revision.
The canonical root is produced by the physical layout defined by this
specification.

## 2. Profile Scope And Version Binding

The hash profile identifier for this specification is:

```text
logos.hash-profile.2026-08.choice-index
```

This hash profile is assigned to the semantic commitment-model revision:

```text
logos.commitment-model.2026-08
```

This specification does not define a separate value-model revision identifier.
The value-model rules are the rules in LOGOS-MODULE-COMMITMENT-MODEL for the
same semantic commitment-model revision.
A future commitment-model revision may introduce an explicit value-model
revision identifier.
Any change to a normative numeric constant, canonical payload shape, or domain
tag in this profile MUST be accompanied by a new hash profile identifier.
This includes chunk sizes, branch fanout, direct-list thresholds, and
verified-view payload shapes.

The hash profile defines:

- the physical layout used to hash semantic schema and value objects;
- packing and chunking rules;
- hash suite binding;
- domain separation;
- exact hash input framing;
- proof material for verified views.

The hash profile does not change the semantic path language.
Verified views still refer to semantic paths such as fields, list indices,
tuple positions, choice arms, byte ranges, and text byte ranges.

## 3. Packing And Chunking

Packing and chunking are physical layout techniques.
They do not change the semantic value tree.

Chunking splits one large ordered value into canonical contiguous ranges.
It applies to long lists, large byte strings, and large text strings.
Chunks are ordered, contiguous, non-overlapping, and determined by canonical
rules rather than implementation choice.
Chunk labels include the start index or byte offset and the element count or
byte count.
The semantic value remains the original list or string, not a list of chunks.

Packing groups multiple small semantic values into one physical hash unit.
It may reduce hash overhead, but it MUST NOT erase semantic identity.
Each packed item retains the label, type, and schema identity needed to recover
or verify the semantic item being proven.

Packing and chunking MUST preserve semantic addressability.
A verifier must be able to reason about the same semantic path whether the
underlying physical layout is direct, packed, chunked, or balanced.

## 4. Canonical Packing And Chunking Rules

Scalar leaves are the default physical representation for scalar semantic
values.
This revision keeps scalar packing narrow.
It defines chunking for large ordered values and permits scalar packing only
where semantic proof boundaries remain clear.

Physical layout MUST NOT pack across these boundaries:

- map field boundaries;
- tuple position boundaries;
- choice arm boundaries;
- referenced-schema boundaries;
- unrelated parent semantic nodes.

Map fields remain individually committed semantic proof targets.
Even when a later profile packs scalar payloads inside maps, a verified view
for a single field must preserve the field semantic path and must not require
the verifier to treat the field as an unlabelled offset inside an opaque packed
blob.
This revision does not pack map fields.

Tuple elements remain individually committed semantic proof targets.
This revision does not pack tuple elements.

Future hash profiles may define an atomic whole-object layout for small maps,
requests, responses, events, tuples, or other bounded values where full-value
commitments are more important than field-level verified views.
Such a layout would hash a canonical whole-value payload under the relevant
schema root and schema subtree root instead of committing every field or tuple
position as a separate child record.
This revision deliberately does not define that optimization because it would
change value roots and proof material.
If added, the atomic-versus-structured choice MUST be a deterministic rule of
the hash profile, so the same schema, value, and hash profile always produce
the same root.
Implementations MUST NOT choose atomic or structured layout adaptively under
the same hash profile.

Commitment-layout hints SHOULD NOT be added to module CDDL merely as an
implementation optimization.
Putting atomic/tree/chunk preferences into the module contract would make a commitment-view concern affect module-contract schema identity.
Such hints are appropriate only if proof granularity is intentionally part of
the module contract.
Otherwise, layout policy belongs in the hash profile or in a separately bound
commitment profile that verifiers can identify explicitly.

The packable scalar kinds are `bool`, `uint8`, `uint16`, `uint32`, `uint64`, `int8`, `int16`, `int32`, and `int64`.
A homogeneous packable scalar list has one of those scalar kinds as its element schema.
Every element shares that scalar schema identity.
Lists of `tstr`, `bstr`, reference, choice, or composite values are not packable scalar lists.
This exclusion preserves each string's own chunking and each reference or composite value's semantic boundary.

Homogeneous packable scalar lists with length less than or equal to 256 elements use direct ordered element commitments.
Homogeneous packable scalar lists with length greater than 256 elements use packed scalar chunks of exactly 256 values.
The final chunk contains the remaining one to 256 values.
Packed scalar list chunks MUST commit to:

- the list schema identity;
- the element schema identity;
- the scalar kind;
- the chunk start index;
- the element count in the chunk;
- the ordered scalar values in the chunk.

A packed scalar list chunk is labelled in its parent by its start index and element count.
A verified view for a packed scalar list element still uses the semantic path
to the list element index.
The proof discloses the complete packed chunk that contains the element.

Every list that is not a homogeneous packable scalar list uses ordinary element commitments.
The canonical list chunk size is 256 elements.
Lists with length less than or equal to 256 elements use direct ordered element
commitments.
Lists with length greater than 256 elements use chunk nodes containing exactly 256 element records.
The final chunk contains the remaining one to 256 records.
Each list chunk commits to:

- the list schema identity;
- the element schema identity;
- the chunk start index;
- the element count in the chunk;
- the ordered element commitments in the chunk.

No empty chunk is encoded.
List chunks are labelled in their parent by element index ranges, not byte offsets.
A verified view for a list element still uses the semantic list index.

Large byte strings are chunked by bytes.
The canonical byte-string chunk size is 4096 bytes.
Byte strings with length less than or equal to 4096 bytes use a direct scalar
byte-string node.
Byte strings with length greater than 4096 bytes use byte-range chunks.
Each byte-string chunk commits to:

- the scalar schema identity;
- the total byte length;
- the chunk start byte offset;
- the byte count in the chunk;
- the exact bytes in the chunk.

No empty chunk is encoded.
Every chunk except the final chunk contains exactly 4096 bytes.
The final chunk contains the remaining one to 4096 bytes.
The chunk records are combined by one `logos.value.bstr` aggregate node.
Verified views over chunked byte strings may expose byte ranges.

Large text strings are chunked by bytes of their canonical UTF-8 encoding.
The canonical text-string chunk size is 4096 bytes.
Text strings with UTF-8 byte length less than or equal to 4096 bytes use a
direct text-string node.
Text strings with UTF-8 byte length greater than 4096 bytes use byte-range
chunks.
The full text value MUST be validated as UTF-8 before text-string chunking.
Chunks are byte ranges of the canonical UTF-8 encoding.
Chunks do not independently claim Unicode scalar, grapheme, normalization, or
substring semantics.
Every chunk except the final chunk contains exactly 4096 bytes.
The final chunk contains the remaining one to 4096 bytes.
The chunk records are combined by one `logos.value.tstr` aggregate node.

A verified view over a chunked text string may expose a byte range of the
canonical UTF-8 encoding.
A future Unicode-aware profile may define semantic substring paths, but this
revision does not.

Chunk sizes are canonical constants in this profile.
Implementations MUST NOT choose adaptive chunk sizes for the same profile.
Adaptive chunking, alternative arities, or proof-system-specific chunk sizes
require a distinct hash profile or explicit extension.

## 5. Physical Layout Nodes

The physical layout is the canonical hashable arrangement of semantic schema
and value objects.
It preserves the semantic identities and semantic paths defined by
LOGOS-MODULE-COMMITMENT-MODEL, but it may introduce physical nodes that do not
exist in the semantic value tree.

Schema objects use the schema object domains defined by
LOGOS-MODULE-COMMITMENT-MODEL and the structured hash input framework defined
in Section 6.
This section defines the physical value-object domains used by this hash
profile.
These domains are hash-layout objects.
They do not add semantic value-node kinds to
LOGOS-MODULE-COMMITMENT-MODEL.

| Physical value object | Domain tag |
|-----------------------|------------|
| Value root | `logos.value.root` |
| Map | `logos.value.map` |
| Field | `logos.value.field` |
| Absent optional field | `logos.value.absent` |
| List | `logos.value.list` |
| List range chunk | `logos.value.list-chunk` |
| Packed scalar list chunk | `logos.value.packed-scalar-list-chunk` |
| Tuple | `logos.value.tuple` |
| Tuple element | `logos.value.tuple-element` |
| Choice | `logos.value.choice` |
| Direct scalar | `logos.value.scalar` |
| Chunked byte string aggregate | `logos.value.bstr` |
| Direct byte string | `logos.value.bstr-direct` |
| Byte-string chunk | `logos.value.bstr-chunk` |
| Chunked text string aggregate | `logos.value.tstr` |
| Direct text string | `logos.value.tstr-direct` |
| Text-string chunk | `logos.value.tstr-chunk` |
| Reference value | `logos.value.reference` |
| Branch node | `logos.value.branch` |

Each physical value object commits to its domain tag, hash profile identifier,
hash suite identifier, semantic commitment-model revision identifier, and typed
payload.
The payload includes the schema root and schema subtree identity needed to
interpret the node.

The physical node-kind values are:

```cddl
node-kind =
    "map" /
    "field" /
    "absent" /
    "list" /
    "list-chunk" /
    "packed-scalar-list-chunk" /
    "tuple" /
    "tuple-element" /
    "choice" /
    "scalar" /
    "bstr" /
    "bstr-direct" /
    "bstr-chunk" /
    "tstr" /
    "tstr-direct" /
    "tstr-chunk" /
    "reference-value" /
    "branch"
```

Every `root-child-record` and `child-record` node kind MUST equal the discriminator in field `0` of the payload whose digest the record carries.
A verifier MUST reject an unknown node kind or a mismatch between a node kind, domain tag, and payload discriminator.

The following deterministic rules convert a normalized value object to physical payloads:

- a value root contains the physical record for its one child value;
- a map contains one field record for each schema field, with present values using a field payload and absent optional values using an absent payload;
- a list uses direct element records, ordinary list chunks, or packed scalar chunks exactly as required by Section 4;
- a tuple contains one tuple-element record for each position;
- a choice contains one record for its selected arm;
- a boolean or integer scalar uses a scalar payload;
- a byte string or text string uses a direct payload through 4096 bytes and an aggregate payload over canonical chunks above 4096 bytes; and
- a reference value contains the physical record for the value interpreted under the referenced schema.

No implementation choice participates in this conversion.
The child labels, node kinds, schema identities, counts, and ordering required by Sections 4, 5, and 7 are part of the canonical physical layout.

Small child collections use direct ordered child arrays.
Maps with at most 256 fields commit directly to ordered field child records.
Lists with at most 256 direct elements or chunks commit directly to ordered child records.
Tuples with at most 256 positions commit directly to ordered tuple-element child records.
Chunked byte-string and text-string aggregates with at most 256 chunks commit directly to ordered chunk records.
Choice nodes commit directly to the selected canonical arm index and selected child record.

Large child collections use canonical branch nodes.
A branch node groups an ordered child-record sequence into contiguous groups
of at most 256 child records.
Every group except the final group contains exactly 256 records.
The final group contains the remaining one to 256 records.
No empty branch node is encoded.
If a collection has more than 256 child records, the implementation groups all records, including the final group, into branch nodes.
It then recursively applies the same grouping rule to the resulting branch records until the collection payload can contain at most 256 records.
The collection payload contains only the branch records from that final grouping level.

Branch nodes are physical layout nodes only.
They are not semantic value-tree nodes and do not introduce semantic path
segments.
A verified view path continues to use fields, list indices, tuple positions,
choice arms, byte ranges, and text UTF-8 byte ranges.
Proof material carries branch metadata only to reconstruct the physical root.

The branch payload commits to:

- the parent physical node kind;
- the parent schema identity;
- the zero-based base-record index at which the represented range starts;
- the total number of base records represented by the branch;
- the ordered child records or child branch records.

Base records are the collection's records before branch grouping.
At every grouping level, branch ranges are contiguous and non-overlapping.
They cover the complete base-record sequence exactly once and appear in increasing start-index order.
The branch record in its parent uses a `branch-label` with the same base-record start index and represented count as the branch payload.
These rules determine one branch tree for every ordered child-record sequence.

For map branches, child-record indices are positions in canonical field-name
order.
For list branches, child-record indices are element indices for direct lists
or chunk indices for chunked lists.
For byte-string and text-string branches, child-record indices are chunk
indices.
For tuple branches, child-record indices are tuple positions.

Direct scalar nodes commit to the scalar schema identity, scalar kind, and
canonical scalar value.
Direct byte-string and text-string nodes are used only at or below the chunking thresholds from Section 4.
Chunk nodes commit to the relevant total length, start offset or index, count, schema identities, and ordered payload or child commitments described in Section 4.
A semantic `scalar-value` of kind `bstr` is realized physically as `bstr-direct` if its total byte length is less than or equal to 4096 bytes, otherwise as one `bstr` aggregate whose children are `bstr-chunk` or branch records.
A semantic `scalar-value` of kind `tstr` is realized physically as `tstr-direct` if its total UTF-8 byte length is less than or equal to 4096 bytes, otherwise as one `tstr` aggregate whose children are `tstr-chunk` or branch records.
Other scalar kinds are realized physically as `logos.value.scalar`.

This layout is intentionally simple.
It gives small values shallow proofs, gives large values deterministic bounded
fanout, and keeps alternative arities or proof-system-specific layouts behind
future hash profiles or explicit extensions.

## 6. Hashing And Domain Separation

The hash profile uses structured, domain-separated hash inputs.
It does not define hashes by ad hoc byte concatenation.

A hash suite defines the concrete digest algorithm and digest size used by a
hash profile.
This specification defines one hash suite.
The suite is identified by the stable ASCII token
`logos.hash-suite.blake3-256`.
It applies BLAKE3 with a 256-bit output and therefore produces a 32-byte digest.
Every conforming implementation MUST use this suite.
There is no hash-suite selection or negotiation.

Every canonical hash input commits to:

- the hash domain tag;
- the hash profile identifier;
- the hash suite identifier;
- the semantic commitment-model revision identifier;
- the typed payload for the hashed object.

Hash domain tags are ASCII text tokens.
They identify the semantic or physical object being hashed.
A digest computed for one domain MUST NOT be accepted as a digest for another
domain, even if the payloads are otherwise identical.

The hash profile identifier is an ASCII text token assigned by this
specification.
It identifies the physical layout, packing rules, chunking rules, domain
rules, and hash input framing used to produce roots and proofs.
For this specification, the hash profile identifier is
`logos.hash-profile.2026-08.choice-index`.
Implementations MUST NOT compare roots across different hash profile
identifiers unless an explicit compatibility profile defines that comparison.

The hash suite identifier is an ASCII text token fixed by this specification.
It identifies the concrete hash function, digest length, and any suite-specific
constraints needed to interpret digest bytes.
Implementations MUST reject an unknown hash suite identifier.
Implementations MUST reject a digest whose length does not match the declared
hash suite.

The semantic commitment-model revision identifier is the revision identifier from
LOGOS-MODULE-COMMITMENT-MODEL.
It binds the hash input to the semantic schema and value model being committed.
Implementations MUST reject an unknown semantic commitment-model revision unless
their verifier policy explicitly supports it or an applicable compatibility
profile exists.

Hash inputs are structured records.
The canonical hash input record has this logical shape:

```cddl
hash-input = {
    0: domain-tag,
    1: hash-profile-id,
    2: hash-suite-id,
    3: semantic-commitment-model-revision,
    4: payload,
}

domain-tag = tstr
hash-profile-id = tstr
hash-suite-id = tstr
semantic-commitment-model-revision = tstr
payload = hash-payload
```

The hash input record is encoded using the Logos deterministic CBOR profile
required by LOGOS-MODULE-INTERFACE Section 4.4 before hashing.
The canonical digest is the mandatory BLAKE3-256 hash suite applied to that
deterministic CBOR encoding.
An implementation MAY stream, cache, precompute, or otherwise optimize hash
construction, but the resulting digest MUST be identical to hashing the
canonical deterministic-CBOR hash input record.
A profile-conformant implementation MAY precompute a constant-prefix hash
state for fixed hash-input fields such as the domain tag, hash profile
identifier, hash suite identifier, and semantic commitment-model revision
identifier, then apply only payload-specific bytes per node.
The resulting digest MUST match canonical hashing of the full structured hash
input.

Pre-seeded hash states, custom initialization vectors, implementation-private
prefix states, or equivalent shortcuts are not canonical hash inputs.
They are implementation optimizations only.
They MUST NOT change the digest and MUST NOT appear in proofs or root
identifiers as independent consensus data.

Child digests are structured payload values.
Branch-like payloads MUST encode child digests together with the labels,
indices, field names, offsets, schema identities, or other typed metadata that
make those child digests meaningful.
They MUST NOT rely on unlabelled digest concatenation to define child order or
boundary semantics.

Verifiers MUST reject:

- unknown hash profile identifiers;
- unknown hash suite identifiers;
- unknown semantic commitment-model revision identifiers unless explicitly allowed
  by verifier policy;
- digest lengths that do not match the hash suite;
- hash inputs with the wrong domain tag for the object being verified;
- malformed hash input records;
- non-deterministic or non-canonical CBOR encodings where a canonical hash
  input is required.

### 6.1 Mandatory BLAKE3-256 Hash Suite

The mandatory BLAKE3-256 suite has these parameters:

- hash suite identifier: `logos.hash-suite.blake3-256`;
- algorithm: BLAKE3 as specified by [BLAKE3];
- digest length: 32 bytes;
- BLAKE3 mode: ordinary unkeyed hashing;
- output: the first 32 bytes of the BLAKE3 extendable output.

Implementations MUST NOT use keyed hashing, key derivation mode, a context string, or a digest length other than 32 bytes for this suite.
All roots and proofs produced under this hash profile MUST identify this suite.
A future specification may assign another suite identifier but MUST NOT change the meaning of `logos.hash-suite.blake3-256`.

## 7. Canonical Hash Payload Shapes

This section defines the exact deterministic CBOR payload shapes for the hash
domains defined by this profile.
These shapes are independent of BLAKE3's internal processing.
The mandatory BLAKE3-256 suite determines the digest algorithm and the 32-byte digest length.

All payload records use deterministic CBOR maps with unsigned integer keys.
Unknown keys are invalid unless a later hash profile or explicit extension
defines them.
Optional fields MUST be omitted when not applicable.
Arrays whose ordering is semantic MUST preserve that order.
Arrays whose ordering is canonicalized by LOGOS-MODULE-COMMITMENT-MODEL or
this profile MUST be encoded in canonical order.

The following common aliases are used in this section:

```cddl
domain-tag = tstr
hash-profile-id = tstr
hash-suite-id = tstr
semantic-commitment-model-revision = tstr
schema-root = bstr
schema-subtree-root = bstr
digest = bstr
field-name = tstr
scalar-kind = tstr
choice-arm-index = uint64
uint64 = uint .size 8
int64 = -9223372036854775808..9223372036854775807
```

The length of `digest`, `schema-root`, and `schema-subtree-root` is 32 bytes
under the mandatory BLAKE3-256 suite.
The `uint64` and `int64` definitions are repeated here for reading convenience
and MUST be identical in meaning to the Logos prelude aliases of the same
names defined by LOGOS-MODULE-INTERFACE.
The Logos prelude integer-alias rule from LOGOS-MODULE-INTERFACE governs
module schemas.
The integer aliases in this section describe canonical hash payload shapes,
not module schemas.
Counters, indices, lengths, and offsets in these shapes use `uint64`.
Integer scalar values use `uint64` or `int64` at the CDDL level and are further
constrained by their `scalar-kind`.
`node-kind` is the closed registry defined in Section 5.

### 7.1 Canonical Hash Input

The canonical hash input record is:

```cddl
hash-input = {
    0: domain-tag,
    1: hash-profile-id,
    2: hash-suite-id,
    3: semantic-commitment-model-revision,
    4: hash-payload,
}

hash-payload = schema-hash-payload / value-hash-payload
```

For this profile, field `1` is always `logos.hash-profile.2026-08.choice-index`.
Field `2` is `logos.hash-suite.blake3-256` in this revision.

### 7.2 Schema Payloads

Schema hash domains use the semantic schema identity payloads defined by
LOGOS-MODULE-COMMITMENT-MODEL Section 9.2.
This profile wraps those payloads in `hash-input`.
It does not redefine the Logos canonical schema model or the schema identity
objects:

| Domain tag | Payload shape |
|------------|---------------|
| `logos.schema.root` | `schema-root-payload` |
| `logos.schema.node` | `schema-node-payload` or `schema-structural-node-payload` |
| `logos.schema.leaf` | `schema-leaf-payload` |
| `logos.schema.reference` | `schema-reference-payload` |

Those payloads are encoded as field `4` of `hash-input`.

```cddl
schema-hash-payload =
    schema-root-payload /
    schema-node-payload /
    schema-structural-node-payload /
    schema-leaf-payload /
    schema-reference-payload
```

### 7.3 Child Records

Parent payloads do not contain unlabelled digest lists.
They contain typed child records:

```cddl
root-child-record = {
    0: node-kind,
    1: digest,
    2: schema-subtree-root,
}

child-record = {
    0: child-label,
    1: node-kind,
    2: digest,
    3: schema-subtree-root,
}

child-label =
    field-label /
    index-label /
    index-range-label /
    tuple-label /
    choice-label /
    byte-range-label /
    branch-label

field-label = {
    0: "field",
    1: field-name,
}

index-label = {
    0: "index",
    1: uint64,
}

index-range-label = {
    0: "index-range",
    1: uint64,  ; start element index
    2: uint64,  ; element count
}

tuple-label = {
    0: "tuple-position",
    1: uint64,
}

choice-label = {
    0: "choice-arm",
    1: choice-arm-index,
}

byte-range-label = {
    0: "byte-range",
    1: uint64,  ; start byte offset
    2: uint64,  ; byte count
}

branch-label = {
    0: "branch",
    1: uint64,  ; start base-record index
    2: uint64,  ; base-record count represented by branch
}
```

`root-child-record` is used only for the one semantic value node below a value root.
It has no path label because the empty semantic path selects that whole node.
Every other parent-child relation uses `child-record` with an explicit typed label.
The schema identity is mandatory in both record shapes,
so an implementation never infers it from a local schema traversal.
Each record's schema identity MUST equal field `2` of the complete payload whose digest that record carries.

The schema identity field is always present.
It re-binds the child digest to its schema identity even when that identity
would be unambiguous from the child label and parent schema identity.
This intentional redundancy prevents a verifier from inferring schema identity
from implementation-local traversal state.

### 7.4 Value Payloads

Value payloads are physical hash payloads derived from the normalized value
objects defined by LOGOS-MODULE-COMMITMENT-MODEL Section 9.3.
They are not an alternate normalized value model.
Their purpose is to bind each digest to its physical layout domain, schema
root, schema subtree identity, child labels, and any chunk or branch metadata
required by this profile.

Unless a field explicitly names a referenced schema identity, each
`schema-subtree-root` in this section is the schema identity for the semantic
value object represented by the physical payload.

The value root payload is:

```cddl
value-root-payload = {
    0: "value-root",
    1: schema-root,
    2: schema-subtree-root,
    3: root-child-record,
}
```

Map and field payloads are:

```cddl
map-payload = {
    0: "map",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,            ; field count
    4: [* child-record],  ; field records or branch records
}

field-payload = {
    0: "field",
    1: schema-root,
    2: schema-subtree-root,
    3: field-name,
    4: root-child-record,
}

absent-payload = {
    0: "absent",
    1: schema-root,
    2: schema-subtree-root,
    3: field-name,
}
```

The map field count is the number of fields defined by the map schema, including optional fields that are absent from the encoded value.
The map contains exactly one child record for each schema-defined field in canonical field-name order.
For a present field, that record has node kind `field` and carries the digest of its `field-payload`.
For an absent optional field, that record has node kind `absent` and carries the digest of its `absent-payload` directly.
In both cases the record label is the field-path component for the field,
and the record carries the identity of the field's value schema.

List and list-chunk payloads are:

```cddl
list-payload = {
    0: "list",
    1: schema-root,
    2: schema-subtree-root,
    3: schema-subtree-root, ; element schema identity
    4: uint64,              ; list length
    5: [* child-record],    ; element, range-chunk, or branch records
}

list-chunk-payload = {
    0: "list-chunk",
    1: schema-root,
    2: schema-subtree-root, ; list schema identity
    3: schema-subtree-root, ; element schema identity
    4: uint64,              ; chunk start element index
    5: uint64,              ; element count in this chunk
    6: [* child-record],    ; ordered element records
}

packed-scalar-list-chunk-payload = {
    0: "packed-scalar-list-chunk",
    1: schema-root,
    2: schema-subtree-root, ; list schema identity
    3: schema-subtree-root, ; element schema identity
    4: scalar-kind,
    5: uint64,              ; chunk start element index
    6: uint64,              ; element count in this chunk
    7: [* scalar-data],     ; ordered scalar values
}

scalar-data = bool / uint64 / int64 / tstr / bstr
```

Tuple and choice payloads are:

```cddl
tuple-payload = {
    0: "tuple",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,            ; tuple arity
    4: [* child-record],  ; tuple-position or branch records
}

tuple-element-payload = {
    0: "tuple-element",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,            ; zero-based tuple position
    4: root-child-record,
}

choice-payload = {
    0: "choice",
    1: schema-root,
    2: schema-subtree-root,
    3: choice-arm-index,     ; selected canonical arm index
    4: schema-subtree-root,  ; selected arm schema identity
    5: child-record,
}
```

Scalar, byte-string, text-string, and reference payloads are:

```cddl
scalar-payload = {
    0: "scalar",
    1: schema-root,
    2: schema-subtree-root,
    3: scalar-kind,
    4: scalar-data,
}

bstr-payload = {
    0: "bstr",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,          ; total byte length
    4: [* child-record],  ; byte-range chunk or branch records
}

bstr-direct-payload = {
    0: "bstr-direct",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,  ; total byte length
    4: bstr,
}

bstr-chunk-payload = {
    0: "bstr-chunk",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,  ; total byte length
    4: uint64,  ; chunk start byte offset
    5: uint64,  ; byte count in this chunk
    6: bstr,
}

tstr-payload = {
    0: "tstr",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,          ; total UTF-8 byte length
    4: [* child-record],  ; byte-range chunk or branch records
}

tstr-direct-payload = {
    0: "tstr-direct",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,  ; total UTF-8 byte length
    4: tstr,
}

tstr-chunk-payload = {
    0: "tstr-chunk",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,  ; total UTF-8 byte length
    4: uint64,  ; chunk start byte offset
    5: uint64,  ; byte count in this chunk
    6: bstr,    ; exact UTF-8 bytes in this chunk
}

reference-value-payload = {
    0: "reference-value",
    1: schema-root,
    2: schema-subtree-root,  ; referring schema location
    3: schema-root,          ; referenced schema root
    4: schema-subtree-root,  ; referenced schema subtree root
    5: root-child-record,
}
```

For `tstr-chunk-payload`, field `6` is a byte string rather than a text string
because chunks are byte ranges of the already validated canonical UTF-8
encoding and may not independently form valid UTF-8 text.

Branch payloads are:

```cddl
branch-payload = {
    0: "branch",
    1: schema-root,
    2: schema-subtree-root,
    3: branch-parent-kind,
    4: uint64,             ; start base-record index
    5: uint64,             ; represented base-record count
    6: [* child-record],   ; child or child-branch records
}

branch-parent-kind = "map" / "list" / "tuple" / "bstr" / "tstr"
```

The child record array in a branch payload MUST contain between 1 and 256 records.
Branch records are ordered by their represented child-record index.

The child arrays and labels are constrained as follows:

- a map payload contains field-labelled `field` or `absent` records in canonical field-name order, or the branch records over that sequence;
- a direct list contains index-labelled element records in increasing index order;
- a chunked list contains index-range-labelled `list-chunk` or `packed-scalar-list-chunk` records in increasing start-index order, or the branch records over that sequence;
- a list-chunk payload contains index-labelled element records for its exact contiguous range;
- a tuple contains tuple-position-labelled records in increasing position order, or the branch records over that sequence;
- a choice contains one choice-arm-labelled record for the selected arm;
- a chunked byte-string or text-string aggregate contains byte-range-labelled chunk records in increasing byte-offset order, or the branch records over that sequence; and
- a branch payload contains the child or branch records for its exact contiguous base-record range.

The count and range fields in a parent payload, child labels, chunk payloads, and branch payloads MUST agree.
Records MUST cover the required field set, element range, tuple positions, or byte range exactly once.
They MUST contain no gaps, overlaps, duplicates, or trailing records.
The scalar payload is valid only for the packable scalar kinds defined in Section 4.
A packed scalar chunk MUST use one of those kinds, contain between 1 and 256 values, and have an element count equal to its value-array length.
A direct byte-string or text-string payload MUST contain at most 4096 bytes, and its length field MUST equal the contained byte length.
A byte-string or text-string aggregate MUST contain more than 4096 bytes.
Its chunks MUST satisfy Section 4 and cover the aggregate's complete byte range exactly.

### 7.5 Domain-To-Payload Mapping

Each value domain tag maps to exactly one payload shape:

```cddl
value-hash-payload =
    value-root-payload /
    map-payload /
    field-payload /
    absent-payload /
    list-payload /
    list-chunk-payload /
    packed-scalar-list-chunk-payload /
    tuple-payload /
    tuple-element-payload /
    choice-payload /
    scalar-payload /
    bstr-payload /
    bstr-direct-payload /
    bstr-chunk-payload /
    tstr-payload /
    tstr-direct-payload /
    tstr-chunk-payload /
    reference-value-payload /
    branch-payload
```

| Domain tag | Payload shape |
|------------|---------------|
| `logos.value.root` | `value-root-payload` |
| `logos.value.map` | `map-payload` |
| `logos.value.field` | `field-payload` |
| `logos.value.absent` | `absent-payload` |
| `logos.value.list` | `list-payload` |
| `logos.value.list-chunk` | `list-chunk-payload` |
| `logos.value.packed-scalar-list-chunk` | `packed-scalar-list-chunk-payload` |
| `logos.value.tuple` | `tuple-payload` |
| `logos.value.tuple-element` | `tuple-element-payload` |
| `logos.value.choice` | `choice-payload` |
| `logos.value.scalar` | `scalar-payload` |
| `logos.value.bstr` | `bstr-payload` |
| `logos.value.bstr-direct` | `bstr-direct-payload` |
| `logos.value.bstr-chunk` | `bstr-chunk-payload` |
| `logos.value.tstr` | `tstr-payload` |
| `logos.value.tstr-direct` | `tstr-direct-payload` |
| `logos.value.tstr-chunk` | `tstr-chunk-payload` |
| `logos.value.reference` | `reference-value-payload` |
| `logos.value.branch` | `branch-payload` |

Verifiers MUST reject a hash input whose domain tag and payload shape do not
match this table.

### 7.6 Verified-View Data Shapes

A verified view has this envelope shape:

```cddl
verified-view = {
    0: "verified-view",
    1: schema-root,
    2: schema-subtree-root,
    3: digest,                         ; value root
    4: hash-profile-id,
    5: hash-suite-id,
    6: semantic-commitment-model-revision,
    7: semantic-path,
    8: disclosed-item,
    9: proof-material,
}

disclosed-item =
    disclosed-value /
    disclosed-absence /
    disclosed-bstr-range /
    disclosed-tstr-utf8-range

disclosed-value = {
    0: "value",
    1: normalized-value-root / value-node,
}

disclosed-absence = {
    0: "absence",
}

disclosed-bstr-range = {
    0: "bstr-range",
    1: uint64,  ; total byte length
    2: uint64,  ; start byte offset
    3: uint64,  ; byte count
    4: bstr,
}

disclosed-tstr-utf8-range = {
    0: "tstr-utf8-range",
    1: uint64,  ; total UTF-8 byte length
    2: uint64,  ; start byte offset
    3: uint64,  ; byte count
    4: bstr,
}
```

`normalized-value-root` and `value-node` are defined by
LOGOS-MODULE-COMMITMENT-MODEL Section 9.3.
`semantic-path` is the path shape defined by
LOGOS-MODULE-COMMITMENT-MODEL Section 9.4.
The disclosed value is a semantic value object from the commitment model.
It is converted to the physical hash payloads in this specification only when
the verifier recomputes the proof.
When `disclosed-item` is a `disclosed-value` containing a
`normalized-value-root`, its schema root and schema subtree root MUST equal
the verified-view envelope's fields 1 and 2 respectively.
Its semantic commitment-model revision MUST equal the envelope's field 6.
These are the verified-view envelope fields, not the per-child-record
rebinding field.

Proof material is an ordered sequence of reconstruction steps from the
disclosed item toward the value root:

```cddl
proof-material = [* proof-step]

proof-step = {
    0: domain-tag,
    1: value-hash-payload,
}
```

Each proof step contains one complete canonical payload.
The domain tag MUST match the payload shape according to Section 7.5.
For an ordinary reconstruction step, the typed path and canonical physical layout identify exactly one child record in that payload.
That record's node kind, digest, schema identity, and label MUST match the previously reconstructed child.
The verifier hashes the complete payload as a canonical `hash-input` and proceeds to the next proof step.
Proof payloads never omit the selected record or contain a placeholder digest.

For a packed scalar list proof, the first proof step contains the complete `packed-scalar-list-chunk-payload` that contains the selected element.
The verifier checks the selected scalar kind and value at the path's list index, then hashes that complete payload.
The proof therefore discloses the whole packed chunk without adding another disclosed-item variant.

For a byte-string or text-string range proof, the first proof step contains the complete direct-string or string-chunk payload that contains the selected range.
The verifier checks that the disclosed bytes equal the exact selected range within that complete payload before hashing it.
For branch proofs, proof steps include the relevant `branch-payload` objects
needed to ascend from the disclosed child to the collection root.

## 8. Verified Views

Verified views are typed partial disclosures over a committed value root.
A verified view proves that a disclosed semantic value, byte range, text byte
range, or absence marker exists at a typed semantic path under a specific
schema, hash profile, hash suite, and value root.

Verified views are intentionally limited in this specification.
They are conventional Merkle inclusion or absence proofs over the semantic
value tree and physical hash layout defined by this profile.
They do not define zero-knowledge proofs, encrypted selective disclosure,
range predicates, semantic Unicode substring proofs, multi-root aggregate
proofs, or trust policy.

Every verified view contains:

- the schema root;
- the schema definition or schema subtree root under which the whole value was
  decoded;
- the value root;
- the hash profile identifier;
- the hash suite identifier;
- the semantic commitment-model revision identifier;
- the typed path being proven;
- the disclosed value, disclosed byte range, disclosed text byte range, or
  disclosed absence marker;
- the proof material needed to recompute the value root.

For method request and response values,
the schema root is the method's defining schema root specified by
LOGOS-MODULE-COMMITMENT-MODEL.
For a primary concrete method, that root is the concrete module schema root.
For an implemented interface method, that root is the implemented interface schema root.
This remains true when external system records attribute the call to a concrete
provider or to other runtime, package, authority, audit, or launch context.
Those attribution records are outside the verified view and outside the value
root payload defined by this profile.

The typed path is an ordered list of semantic path segments.
Path segments are structured values, not slash-delimited strings.
The canonical path segment data shapes and their semantic meaning are defined
by LOGOS-MODULE-COMMITMENT-MODEL Section 9.4.
This profile consumes those path segment kinds when selecting the physical
payloads and proof steps needed to verify a view:

| Segment kind | Meaning |
|--------------|---------|
| `field` | A named map field |
| `list-index` | A zero-based list element index |
| `tuple-position` | A zero-based tuple element position |
| `choice-arm` | A selected canonical choice-arm index |
| `bstr-range` | A byte range inside a byte string |
| `tstr-utf8-range` | A byte range inside the canonical UTF-8 encoding of a text string |

A `field` segment contains the canonical field name.
A `list-index` segment contains the zero-based element index.
A `tuple-position` segment contains the zero-based fixed tuple position.
A `choice-arm` segment contains the selected canonical arm index.
A `bstr-range` segment contains a start byte offset and byte length.
A `tstr-utf8-range` segment contains a start byte offset and byte length in
the canonical UTF-8 encoding of the text string.

Text-string byte ranges do not claim Unicode scalar, grapheme, normalization,
or substring semantics.
They prove bytes of the canonical UTF-8 encoding only.

An empty path proves the whole value.
For a whole-value verified view, the disclosed value is the full normalized
value and proof material MAY be empty if the verifier can recompute the value
root directly from the disclosed value.

Absence proofs use the same path language.
Because absent optional fields are explicit semantic nodes in
LOGOS-MODULE-COMMITMENT-MODEL, a proof of absence is a verified view whose path
selects the optional field and whose disclosed item is the absent marker.
Absence is different from non-disclosure:
a field omitted from a verified view is not proven absent unless an explicit
absent marker is disclosed and verified.

Proof material is profile-specific, but it MUST be sufficient for a verifier
to recompute the value root from the disclosed item and the typed path.
Each proof step carries the complete canonical payload for one physical node.
Across the ordered steps, those payloads carry:

- the node kind and schema identity for each reconstructed node;
- the selected child and sibling digests needed at each level;
- labels, field names, indices, tuple positions, offsets, or choice-arm identities needed to identify the selected child;
- chunk metadata when the proof crosses chunked lists, byte strings, or text strings;
- packed-chunk material when the proof crosses a packed scalar list chunk;
- the child ordering information needed to reconstruct each parent payload.

Proofs MUST NOT rely on unlabelled digest concatenation.
Child digests are interpreted only together with their labels, indices, offsets, schema identities, and parent node kind.
The verifier MUST reject an incomplete parent payload, an omitted selected record, a placeholder digest, duplicate or overlapping records, an out-of-order step, or any step not required by the canonical physical path.

For a map field proof, the proof material includes the disclosed field value or absent marker and complete parent payloads containing the field name, field schema identity, and sibling field records.
The verifier reconstructs the map node using canonical field-name ordering.

For a list element proof in an unchunked list, the proof material includes the complete list payload with the list length, element index, element schema identity, selected element digest, and sibling element records.

For a list element proof in a chunked list, the proof material also includes the complete containing chunk, branch, and list payloads needed by the canonical layout.
The semantic path remains the list element index.
Chunk indices and offsets are physical proof details, not semantic path
segments.

Byte-string and text-string range paths MUST select a non-empty range whose end does not exceed the total byte length.
For a direct string, the first proof step discloses the complete direct-string payload.
For a chunked string, the selected range MUST lie entirely within one canonical 4096-byte chunk.
The first proof step discloses that complete chunk payload.
A range that crosses a chunk boundary requires one verified view for each intersected chunk; this profile does not define a multiproof envelope.

For a byte-string range proof, the first proof step includes the total byte length, containing chunk start byte offset and byte count when chunked, and the complete direct value or containing chunk bytes.
Later steps include the complete aggregate, branch, and ancestor payloads needed to reconstruct the value root.
The semantic path uses a `bstr-range` segment.

For a text-string byte-range proof, the proof material includes the total UTF-8 byte length, the complete direct value or containing chunk bytes, and the remaining complete payloads needed to reconstruct the value root.
The verifier checks the proof as a byte-range proof over the canonical UTF-8
encoding.
This specification does not define semantic substring proofs.

For a packed scalar list proof, this specification requires disclosure of the
whole packed scalar chunk that contains the requested element.
The verifier validates the packed chunk, extracts the requested list index from
that chunk, and then reconstructs the parent list commitment.
A future profile may define finer-grained private proofs inside packed scalar
chunks, but this profile does not.

The verification procedure is:

1. Reject unknown hash profile identifiers, hash suite identifiers, or semantic
   commitment-model revision identifiers unless verifier policy explicitly allows
   them.
2. Check that the schema root and schema subtree root identify the schema under
   which the value root is interpreted.
   For method request and response values,
   this schema root is the method's defining schema root.
   A concrete provider schema root is checked here only when the method itself
   is defined by that concrete provider schema.
3. Validate the typed path against the schema.
4. Normalize the disclosed value, disclosed range, or absent marker under the
   schema selected by the typed path.
5. For an ordinary disclosed value or absence marker, recompute its physical leaf or subtree digest using Sections 4 through 7.
   For a packed scalar element or string range, validate and hash the complete containing payload in the first proof step as specified above.
6. Apply each remaining proof step from the reconstructed node toward the root.
   At every ordinary step, require the complete payload's uniquely selected child record to match the previously reconstructed node, then hash the payload using its required domain.
7. Require the final reconstructed payload to be the `value-root-payload`, require that no steps remain, and compare its digest with the verified view's value root.

If any check fails, the verified view is invalid.
If the recomputed root equals the value root and all schema, profile, suite,
path, and proof checks succeed, the verified view is valid relative to that
value root.

Validity relative to a value root does not imply that the root is trusted.
Trust in roots, signers, packages, runtimes, remote providers, audit logs, or
consensus systems is outside this specification.
Those systems may link their own evidence to the verified view's schema root,
schema subtree root, and value root.
They do not change the proof checked by this profile.

## 9. Conformance

A conforming implementation of this hash profile MUST construct canonical hash
inputs and payloads according to Sections 6 and 7, encode them using the Logos
deterministic CBOR profile required by LOGOS-MODULE-INTERFACE Section 4.4, and
apply `logos.hash-suite.blake3-256` exactly as defined in Section 6.1.
It MUST reject malformed hash inputs, unknown identifiers, wrong digest
lengths, wrong domain tags, non-canonical CBOR encodings, and mismatched
domain-to-payload shapes as described by this specification.
It MUST produce the Appendix A schema-root vector and every Appendix B physical-layout digest exactly.
A verified-view implementation MUST accept the valid Appendix B views and reject mutations that change a disclosed value, path, range, label, count, schema identity, node kind, child digest, payload discriminator, domain tag, step order, or expected value root.

## 10. Comparison And Non-Goals

The Logos commitment model and hash profile are intentionally narrow.
They define canonical commitments and verified views for schema-defined Logos
module values.
They do not define a general semantic object envelope, a blockchain state
tree, a trust system, a remote-computation protocol, or a zero-knowledge proof
system.

Gordian Envelope is a general semantic envelope and selective-disclosure model.
Logos deliberately uses a narrower commitment model for module contracts.
In Logos, the module schema is part of the committed interpretation:
it defines the allowed value shape, method/event meaning, field identity,
choice-arm selection, and semantic path language.
This lets Logos define roots and verified-view proof material directly over
schema-bound module values instead of first representing every value as a
general envelope object.

The tradeoff is that Logos puts more contract-specific rules into the
specifications.
The benefit is that roots, paths, proof material, runtime validation, and module-interface compatibility all refer to the same schema-bound contract objects.
Logos may interoperate with envelope-like systems through later profiles, but
this specification does not adopt Gordian Envelope as the primary commitment
object model.

Ethereum SSZ is a serialization and merkleization format for Ethereum
consensus objects.
Logos shares the goal of stable typed commitments and proof paths, but the
types, paths, and roots are defined by Logos module schemas rather than by
Ethereum consensus containers.
Logos also separates the semantic commitment model from the physical hash
profile so future environments can define different hash suites or layouts
without redefining the schema and value semantics.

External systems may anchor, wrap, translate, or attest to Logos roots.
Examples include blockchains, transparency logs, trusted-execution
attestations, zero-knowledge proof systems, consensus protocols, package trust
systems, and remote runtime trust profiles.
Those systems are outside this specification.
This specification defines the roots and verified-view proof material those
systems may consume.

Non-goals:

- trusted computation protocols;
- challenge games or fraud proofs;
- ZK proving circuits;
- on-chain contract formats;
- remote runtime enrollment;
- plugin loader or package-manager control APIs;
- package trust policy;
- authorization policy;
- runtime call policy.

## Appendix A. Normative Schema-Root Vector

This appendix gives a normative hash-profile vector for the construction
vector in LOGOS-MODULE-COMMITMENT-MODEL Appendix A.
It uses the mandatory BLAKE3-256 suite from Section 6.1.

The vector hashes one `logos.schema.root` hash input whose payload is the
`normalized-schema-root` object from LOGOS-MODULE-COMMITMENT-MODEL
Appendix A.

Hash input fields:

- field `0`: `logos.schema.root`;
- field `1`: `logos.hash-profile.2026-08.choice-index`;
- field `2`: `logos.hash-suite.blake3-256`;
- field `3`: `logos.commitment-model.2026-08`;
- field `4`: the Appendix A `normalized-schema-root` object from
  LOGOS-MODULE-COMMITMENT-MODEL.

The deterministic CBOR hash-input byte length is `796` bytes.
The deterministic CBOR hash-input bytes, in hexadecimal, are:

```text
a500716c6f676f732e736368656d612e726f6f740178276c6f676f732e686173
682d70726f66696c652e323032362d30382e63686f6963652d696e6465780278
1b6c6f676f732e686173682d73756974652e626c616b65332d32353603781e6c
6f676f732e636f6d6d69746d656e742d6d6f64656c2e323032362d303804a500
6b736368656d612d726f6f7401781e6c6f676f732e636f6d6d69746d656e742d
6d6f64656c2e323032362d3038026773746f726167650387a300647479706501
7173746f726167652e626c6f625f6861736802a300697072696d697469766501
646273747202a3006473697a65011820021820a300656576656e74017573746f
726167652e6368616e6765645f6576656e7402a200636d61700182a300636369
6401f402a2006f6c6f63616c2d7265666572656e6365016b73746f726167652e
636964a3006664696765737401f402a2006f6c6f63616c2d7265666572656e63
65017173746f726167652e626c6f625f68617368a3006474797065016b73746f
726167652e63696402a300697072696d697469766501647473747202a3006473
697a650101021880a300666d6574686f64016e73746f726167652e6578697374
7302a300666d6574686f64017673746f726167652e6578697374735f72657175
657374027773746f726167652e6578697374735f726573706f6e7365a3006e6d
6574686f642d72657175657374017673746f726167652e6578697374735f7265
717565737402a200636d61700181a300636b657901f402a2006f6c6f63616c2d
7265666572656e6365017273746f726167652e6c6f6f6b75705f6b6579a3006f
6d6574686f642d726573706f6e7365017773746f726167652e6578697374735f
726573706f6e736502a200636d61700181a3006665786973747301f402a20069
7072696d69746976650164626f6f6ca3006474797065017273746f726167652e
6c6f6f6b75705f6b657902a2006663686f6963650182a2006f6c6f63616c2d72
65666572656e6365016b73746f726167652e636964a2006f6c6f63616c2d7265
666572656e6365017173746f726167652e626c6f625f686173680480
```

The BLAKE3-256 digest of those bytes is:

```text
9befcab3f47617bacbfaa212f1dc8f4f4494678c4536162fb53c3acbcfeafd47
```

Under the mandatory suite, that digest is the schema root for the construction vector's whole schema.

## Appendix B. Normative Physical-Layout Boundary Vectors

This appendix defines boundary vectors for packing, string chunk aggregation, branch construction, and verified-view reconstruction.
All vectors use the profile, suite, and commitment-model revision assigned by this specification.

The vectors use these synthetic 32-byte schema identities:

| Identity | Bytes, hexadecimal |
|----------|--------------------|
| Schema root | `1010101010101010101010101010101010101010101010101010101010101010` |
| List schema subtree root | `1111111111111111111111111111111111111111111111111111111111111111` |
| List-element schema subtree root | `1212121212121212121212121212121212121212121212121212121212121212` |
| Byte-string schema subtree root | `1313131313131313131313131313131313131313131313131313131313131313` |

### B.1 Packed Scalar List Boundary

The normalized value is a `uint16` list containing the integers `0` through `256` inclusive.
The physical layout contains one packed chunk for indices `0` through `255` and one packed chunk for index `256`.

| Object | Digest, hexadecimal |
|--------|---------------------|
| First packed chunk | `96ea377758aec5c446cec80b60088d129ff971b85bda591c6f77d7c99fb23eab` |
| Final packed chunk | `90ba0b2241f89f427a321b4a94cf250f1b65f048d3134834381694db174d671f` |
| List | `f30f3f87a545f0095791f47933ceeea5c8ad51cf0aa820d9661481de71ff7c10` |
| Value root | `3a0b366ac7d16600d4f92fcdbfa0706c9e86c0be2e3286595cb2e832ab6efec2` |

A verified view for semantic path `[{0: "list-index", 1: 256}]` discloses the `uint16` value `256`.
Its proof steps are the complete final packed-chunk payload, list payload, and value-root payload in that order.
The verified view MUST validate against the value root above.

### B.2 Byte-String Chunk Boundary

The normalized byte string has length `4097`.
The byte at zero-based index `i` is `i` modulo `251`.
The physical layout contains one 4096-byte chunk and one one-byte chunk under one byte-string aggregate.

| Object | Digest, hexadecimal |
|--------|---------------------|
| First byte-string chunk | `53e97f4a652ac68c6173c121d8d33d9cd72f99210d34d7d258b0c2c78658a6ac` |
| Final byte-string chunk | `19e3901251b3fbe18522fad6fd70e54c5a33ffea704fb5edf3a07c5e51f31cd9` |
| Byte-string aggregate | `189229d6d24ae83aa2b29293c4660ee4450758b33b4407c564bdb6290988c876` |
| Value root | `da2ce350cd03b669d6f53ba5fb4387b3fd23db92181a19d58475527ab83c7b74` |

A verified view for semantic path `[{0: "bstr-range", 1: 4096, 2: 1}]` discloses the final byte.
Its proof steps are the complete final chunk payload, aggregate payload, and value-root payload in that order.
The verified view MUST validate against the value root above.

### B.3 Branch Boundary

This vector begins with 257 synthetic packed-chunk child records.
Record `i` has an `index-range` label with start `i * 256` and count `256`.
Its node kind is `packed-scalar-list-chunk`, its schema identity is the list-schema identity above, and its 32-byte digest is zero except for the final four bytes, which encode `i` as an unsigned big-endian integer.

Canonical branch construction produces one branch for records `0` through `255` and one branch for record `256`.

| Branch | Digest, hexadecimal |
|--------|---------------------|
| Records 0 through 255 | `d0b8d2fd5fd40e5d5a9ee29e7f93a0423e8366a3b9f0307b0fc72585a0e12b46` |
| Record 256 | `0da1c5d1cb53c679d3e7863a0b9856fab9513fa2408d6c181f1c2d402b9d0abd` |

The collection payload contains those two branch records in that order.

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- [BLAKE3] -- BLAKE3 specification.
  https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-COMMITMENT-MODEL -- Semantic commitment model specification.

### Informative

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
