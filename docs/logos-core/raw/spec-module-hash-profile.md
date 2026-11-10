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

## Requirements Language

Uppercase requirement keywords in this specification follow BCP 14 [RFC 2119] [RFC 8174].
Lowercase forms retain their ordinary English meanings.

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
logos.commitment-model.2026-10
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
A homogeneous packable scalar list has a primitive or literal element schema with a packable scalar kind.
For example, `[* true]`, `[* 5]`, and `[* -5]` are homogeneous packable scalar lists.
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

The `logos.schema.reference` domain hashes a standalone `schema-import` pair using `schema-reference-payload`.
This digest does not participate in schema or value commitment construction or verified views in this revision.
An implementation MUST NOT substitute it for a schema root, schema subtree root, or `schema-import` pair.

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

`root-child-record` represents the sole child of a payload whose shape in Section 7.4 uses that record.
It has no path label; the enclosing payload determines the child's semantic position.
A `child-record` identifies a child in an ordered collection or a selected choice arm with an explicit typed label.
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

Field `1` of every value payload MUST be the root of the schema document that defines the schema identity in field `2`.
For a `value-root-payload`, this is the schema root of the committed value.
A `reference-value-payload` MUST retain the importing document's root in field `1` and carry the referenced document's root in field `3`.
Its child and that child's descendants MUST use the referenced document's root in field `1` until a further imported reference changes the document context.
The wrapper for that further reference retains the current context; its child uses the newly referenced document's root.
Local references MUST NOT change the document context.

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

When a path ends in a `field`, `list-index`, or `tuple-position` segment selecting a present value,
the disclosed item MUST be the contained normalized value.
For a path ending at a present field or tuple position, its `field-payload` or `tuple-element-payload`, respectively, MUST appear in the proof material.

An empty path proves the whole value.
For a whole-value verified view, the disclosed value is the full normalized value and the proof material MUST be empty.
The verifier MUST recompute the value root directly from the disclosed value and MUST reject a whole-value view that carries proof material.

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

Verification requires the schema construction input defined by LOGOS-MODULE-COMMITMENT-MODEL Section 3.1, including its required dependency documents, separately from the verified view.
The verifier MUST validate that input and compute the schema root and selected schema subtree root for comparison with the view in step 2.
Previously validated construction results and computed roots MAY be reused under the same commitment-model revision, hash profile, and hash suite as the view.

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
   Derive the expected document context from the selected schema and its resolved imports according to LOGOS-MODULE-COMMITMENT-MODEL Section 5 and Section 7.4 above.
4. Normalize the disclosed value, disclosed range, or absent marker under the
   schema selected by the typed path.
5. For an ordinary disclosed value or absence marker, recompute its physical leaf or subtree digest using Sections 4 through 7.
   For a packed scalar element or string range, validate and hash the complete containing payload in the first proof step as specified above.
6. Apply each remaining proof step from the reconstructed node toward the root.
   At every ordinary step, require the complete payload's uniquely selected child record to match the previously reconstructed node, then hash the payload using its required domain.
7. Require the final reconstructed payload to be the `value-root-payload`, require that no steps remain, and compare its digest with the verified view's value root.

For every reconstructed or disclosed physical payload, the verifier MUST require field `1` to match the document context assigned by Section 7.4.
For each `reference-value-payload`, it MUST also require fields `3` and `4` to match the referenced document and declaration resolved from the schema.
These checks apply to complete disclosed subtrees and all proof steps, including containing chunks and branches.
A document root supplied in proof material MUST NOT override the context derived from the schema.

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
A verified-view implementation MUST accept the valid Appendix B views and reject mutations that change a disclosed value, path, range, label, count, schema identity, payload schema root, node kind, child digest, payload discriminator, domain tag, step order, or expected value root.

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
- field `3`: `logos.commitment-model.2026-10`;
- field `4`: the Appendix A `normalized-schema-root` object from
  LOGOS-MODULE-COMMITMENT-MODEL.

The deterministic CBOR hash-input byte length is `796` bytes.
The deterministic CBOR hash-input bytes, in hexadecimal, are:

```text
a500716c6f676f732e736368656d612e726f6f740178276c6f676f732e686173
682d70726f66696c652e323032362d30382e63686f6963652d696e6465780278
1b6c6f676f732e686173682d73756974652e626c616b65332d32353603781e6c
6f676f732e636f6d6d69746d656e742d6d6f64656c2e323032362d313004a500
6b736368656d612d726f6f7401781e6c6f676f732e636f6d6d69746d656e742d
6d6f64656c2e323032362d3130026773746f726167650387a300647479706501
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
2321d43e09fed8b6357300b505750b03ec0f9e392f4bbfb3b013c7078a7a2cca
```

Under the mandatory suite, that digest is the schema root for the construction vector's whole schema.

## Appendix B. Normative Physical-Layout Boundary Vectors

This appendix defines vectors for packing, string chunk aggregation, branch construction, imported schema context, and verified-view reconstruction.
All vectors use the profile, suite, and commitment-model revision assigned by this specification.

The vectors in Sections B.1 through B.3 use these synthetic 32-byte schema identities:

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
| First packed chunk | `564e7aebed309e0e972c1889dcd390844586e4e9431ee84cd47f485a8017ca97` |
| Final packed chunk | `4f9e220a7ff848b15af6f16d86706970fd287453b78ccf05df3913f859abc3e8` |
| List | `56b8b8e7af2afba36b71f2c39f53187e587d57fcfb85f18d7e1457320c36b15c` |
| Value root | `b4dfb5043f0ad9edcc6368b9a929534c27c2fc17628a0c50dcc50a2d6924c16f` |

A verified view for semantic path `[{0: "list-index", 1: 256}]` discloses the `uint16` value `256`.
Its proof steps are the complete final packed-chunk payload, list payload, and value-root payload in that order.
The verified view MUST validate against the value root above.

### B.2 Byte-String Chunk Boundary

The normalized byte string has length `4097`.
The byte at zero-based index `i` is `i` modulo `251`.
The physical layout contains one 4096-byte chunk and one one-byte chunk under one byte-string aggregate.

| Object | Digest, hexadecimal |
|--------|---------------------|
| First byte-string chunk | `f378adc5640d24e0f35d18973285dfe7c79c3038194f2962ed9139cb225efd3c` |
| Final byte-string chunk | `b65c079c992e20f9ce1e454702871bebf7aebab36a549642258288e2e309baa2` |
| Byte-string aggregate | `4a4c19f9613c2540b87696879f622301709b8a7134cce4e68d0d9c65b906f206` |
| Value root | `223a41867e3b21922714da7985214c2e5381b472b26a171f1b3b768a6e65d0c2` |

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
| Records 0 through 255 | `a0950d2273cdebc149a068abbcf5c6622c78437fe3b0c49d109c968f4aef324d` |
| Record 256 | `77a2a1cd2ab83b80d8681eaade31d29eab7ee042a4c1eebcaa8f3434e919668d` |

The collection payload contains those two branch records in that order.

### B.4 Imported Reference Context

The two concrete module schemas below each use the same explicitly supplied supporting schema.
Prelude aliases and the pinned common schema are those required by LOGOS-MODULE-COMMITMENT-MODEL Section 5.

```cddl
_module = "a"
a.alias = a.import
a.import = types.alias
a.value = { amount: a.alias, z: uint64 }
```

```cddl
_module = "c"
c.value = { amount: types.alias, z: uint64 }
```

```cddl
types.alias = types.record
types.count = uint64
types.record = { detail: logos.error_detail, value: types.count }
```

The following table assigns each document root used by these vectors.

| Symbol | Document | Root, hexadecimal |
|--------|----------|-------------------|
| `A` | `a` | `dae3aa65668f9d0c1ed0d6aadd0b53a0e24dcb2180a909472c6b2f3b9361fec1` |
| `B` | `types` | `f0419adddaea91e732c408a794358a0ca541fa03bc2c7a1b18c1b6809054f2eb` |
| `C` | `c` | `c3cf126ce62c5006421cfb4c9b3ebf87eb9ef48fa71ca8b73f74097b55724636` |
| `L` | Pinned common schema | `fc3a3558912d474cdb37fbc4fedd5b11dd785d69e9c033c7f9dc077ac49040ca` |

In the tables below, `S(name)` denotes the named declaration's subtree root.
`S(name, field)` denotes the schema leaf hash at that declaration's `field` path.
All schema identities are computed from the documents above and the pinned common schema.
`P(kind, document, schema, fields)` denotes the payload map `{0: kind, 1: document, 2: schema}` extended with `fields`.
For a payload named `x`, `R(x)` denotes its root-child record and `F(name, x)` denotes its child record with label `{0: "field", 1: name}`.
Both record forms use `x`'s discriminator, digest, and field `2` exactly as specified in Section 7.3.
These symbols are notation only and MUST be replaced by their values before CBOR encoding.

The value selected through either `a.value` or `c.value` is:

```cbor-diag
{ "amount": { "detail": h'00', "value": 5 }, "z": 7 }
```

The payloads and their digests are:

| Name | Payload | Digest, hexadecimal |
|------|---------|---------------------|
| `e` | `P("bstr-direct", L, S("logos.error_detail"), {3: 1, 4: h'00'})` | `866b00f6b2fa598cba282173e8cbb091b42f0f9fa2a986f031901ac4a3d67654` |
| `r` | `P("reference-value", B, S("types.record", "detail"), {3: L, 4: S("logos.error_detail"), 5: R(e)})` | `4cbbdabd1225ee32d73b7cd1d98ff95f0229494b4c942152eaf1ae7c6b4402c6` |
| `d` | `P("field", B, S("types.record", "detail"), {3: "detail", 4: R(r)})` | `c8f9628164ee88bd6b835aa6c834643d292e79299085c9b763616286bd8f6ade` |
| `n` | `P("scalar", B, S("types.count"), {3: "uint64", 4: 5})` | `dd70050599e53badc184347edb91c185d231180028273f1e81adff3e0bbe84ba` |
| `v` | `P("field", B, S("types.record", "value"), {3: "value", 4: R(n)})` | `bdddd74eaadcde4c8046879f9bd7cdf5bafd535300ccb6b9beb7a89775f7ee22` |
| `b` | `P("map", B, S("types.record"), {3: 2, 4: [F("detail", d), F("value", v)]})` | `fdabde59238e10c0fc1dfb965e4459ece9aaf298c1b9f5d17da3adf096f14ff4` |
| `b0` | `P("value-root", B, S("types.alias"), {3: R(b)})` | `9337bfbdfa1d8bb0bc8fcf58a1ff2db1dad4a920a0e146d45b77090eb5f0ebe2` |
| `ar` | `P("reference-value", A, S("a.import"), {3: B, 4: S("types.alias"), 5: R(b)})` | `9ecbd8b41e7f406f48894c4ccb573ea041845f8af61703d4535ec8d35476f6ea` |
| `af` | `P("field", A, S("a.value", "amount"), {3: "amount", 4: R(ar)})` | `2dd1504f6b9b0ef9a3ee58e16372e773ad63f088577f9a53a9421d4342d66ede` |
| `az` | `P("scalar", A, S("a.value", "z"), {3: "uint64", 4: 7})` | `591a4fa4aaae426c7a3388468de1a20bc51946f77cb4c3ca63a4f866b3086d86` |
| `aq` | `P("field", A, S("a.value", "z"), {3: "z", 4: R(az)})` | `211be949b703f72e93faf563b8f1bc2eb203b30354ff3bd0d703ddb649bb30e7` |
| `am` | `P("map", A, S("a.value"), {3: 2, 4: [F("amount", af), F("z", aq)]})` | `ea4239c2b05070b397a8158c4c8fbc1547a5060e63391cc02e0155fdc7537800` |
| `a0` | `P("value-root", A, S("a.value"), {3: R(am)})` | `9257722a3eb401a86000ff65371d751636d1f6e6a0771a1c5e4786d98d56147e` |
| `cr` | `P("reference-value", C, S("c.value", "amount"), {3: B, 4: S("types.alias"), 5: R(b)})` | `96a19fd543b430c941f684f88864927c93d11cd640a6396caa236ee3d9ebab75` |
| `cf` | `P("field", C, S("c.value", "amount"), {3: "amount", 4: R(cr)})` | `e0f45fa6cf6dacfa5e6d2bcfd981b62b823bc25cebf0f12288c382a8855b3d14` |
| `cz` | `P("scalar", C, S("c.value", "z"), {3: "uint64", 4: 7})` | `62a370e9d9d8ca45d8f8defc781e1ecd39510e5fc78d2f98803ac7972d411330` |
| `cq` | `P("field", C, S("c.value", "z"), {3: "z", 4: R(cz)})` | `f3f369b1d4f4e5a4e3b43195b1f3d2295ee5af2859109e156f49a972e5d9d632` |
| `cm` | `P("map", C, S("c.value"), {3: 2, 4: [F("amount", cf), F("z", cq)]})` | `3e77b5b8666bdfd08bc1d78cd4171c6c007bfd70caa195a3da903122e92ea0ec` |
| `c0` | `P("value-root", C, S("c.value"), {3: R(cm)})` | `58bf0541f221388df4e0f27b4af618859b44e9d142fc80ebf5d189fbec7a1982` |

Each digest uses the domain assigned to that payload kind by Section 5 and the hash input in Section 7.1.
The imported subtree `b` is identical under both importers and direct selection of `types.alias` in the supporting schema.
That direct selection commits `{ "detail": h'00', "value": 5 }` and has value root `b0`.
Local aliases add no payloads: `ar` uses `S("a.import")`, while its child `b` uses `S("types.record")`.

Complete verified views with empty paths MUST validate for `a.value`, `c.value`, and `types.alias` against `a0`, `c0`, and `b0`, respectively.
The following partial views select `a.value` and MUST validate against `a0`.
Disclosures are normalized under the schema selected by each path; the payload names below identify their physical construction and ordered proof steps.

| Typed path | Disclosed value | Proof payloads, in order |
|------------|-----------------|--------------------------|
| `[{0: "field", 1: "amount"}, {0: "field", 1: "value"}]` | `uint64` value `5`, payload `n` | `v, b, ar, af, am, a0` |
| `[{0: "field", 1: "amount"}, {0: "field", 1: "detail"}]` | Reference value containing `bstr` value `h'00'`, subtree `r` | `d, b, ar, af, am, a0` |
| `[{0: "field", 1: "amount"}, {0: "field", 1: "detail"}, {0: "bstr-range", 1: 0, 2: 1}]` | Byte range `h'00'` | `e, r, d, b, ar, af, am, a0` |
| `[{0: "field", 1: "z"}]` | `uint64` value `7`, payload `az` | `aq, am, a0` |

Each negative case below starts independently from the valid `a.value` tree.
Apply the stated mutation, recompute every affected digest and ancestor child record, and advertise the resulting value root shown below.
Keep the selected schema, disclosed value, and typed path unchanged.
For each case, both the complete view and the indicated partial view MUST be rejected despite their internally consistent hashes.
The partial-view column names the field sequence from the table above; `range` selects the additional byte-range segment.

| Case | Mutation | Partial view | Recomputed value root, hexadecimal |
|------|----------|--------------|------------------------------------|
| N1 | `n` field `1` becomes `A` | `amount, value` | `d16c14d03939be1139aee1594e5ffc4a427abeb4db539e15684216b9187d1d6d` |
| N2 | `e` field `1` becomes `B` | `amount, detail, range` | `db808768d6560f501c11034b8ad6b38d4445ab3f1e282d3c206a0b27c725935d` |
| N3 | `ar` field `1` becomes `B` | `amount, value` | `4514b409018467048df7fb1e2588291ddf0692614b8c3b3bb926744d8e05e838` |
| N4 | `r` field `1` becomes `L` | `amount, detail, range` | `e61036b0510a304691b9b71b259b5e4a72036662c2fb394f6b0c52a4239ee15e` |
| N5 | `ar` field `3` becomes `C` | `amount, value` | `2c80c56053a6e253cf4469928fa112b8b7d880ba660bc1676b717be9bca93e08` |
| N6 | `ar` field `4` becomes `S("types.record")` | `amount, value` | `f353267517bf17ef09acd4f1c6dbb240920b96c84bbf57be14712428d6ab6639` |
| N7 | `aq` field `1` becomes `B` | `z` | `843b6c34a3ee49677b66f4fc725d64da7513367d1cd00a1b0694e98b4799a0b1` |
| N8 | Fields `1` of `e, r, d, n, v, b` all become `A` | `amount, detail, range` | `b730096beea22fd6b0fb9ad48c69d65600a5cd6f181309b3b2bd616d2d42a5fd` |

---

## References

### Normative

- [RFC 2119] -- Key words for use in RFCs to Indicate Requirement Levels.
  https://www.rfc-editor.org/rfc/rfc2119
- [RFC 8174] -- Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
  https://www.rfc-editor.org/rfc/rfc8174
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
