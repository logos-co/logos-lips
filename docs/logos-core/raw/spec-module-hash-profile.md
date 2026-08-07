# LOGOS-MODULE-HASH-PROFILE

| Field        | Value                       |
|--------------|-----------------------------|
| Name         | Logos Module Hash Profile   |
| Slug         | 303                         |
| Status       | raw                         |
| Category     | Standards Track             |
| Editor       | ksr                         |
| Contributors | atd, Jarrad                 |

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
logos.hash-profile.2026-05
```

This hash profile is assigned to the semantic commitment-model revision:

```text
logos.commitment-model.2026-06
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
Putting atomic/tree/chunk preferences into the module contract would make a
commitment-view concern affect interface and transport schema identity.
Such hints are appropriate only if proof granularity is intentionally part of
the module contract.
Otherwise, layout policy belongs in the hash profile or in a separately bound
commitment profile that verifiers can identify explicitly.

Homogeneous scalar lists use packed scalar chunks when they exceed the direct
list threshold.
A homogeneous scalar list is a list whose element schema is a scalar type and
whose elements all share the same scalar schema identity.
Homogeneous scalar lists with length less than or equal to 256 elements use
direct ordered element commitments.
Homogeneous scalar lists with length greater than 256 elements use packed
scalar chunks.
Packed scalar list chunks MUST commit to:

- the list schema identity;
- the element schema identity;
- the scalar kind;
- the chunk start index;
- the element count in the chunk;
- the ordered scalar values in the chunk.

A verified view for a packed scalar list element still uses the semantic path
to the list element index.
The physical proof may include the packed chunk that contains the element.

Long non-scalar lists are chunked into ordered element ranges.
The canonical list chunk size is 256 elements.
Lists with length less than or equal to 256 elements use direct ordered element
commitments.
Non-scalar lists with length greater than 256 elements use chunk nodes.
Each list chunk commits to:

- the list schema identity;
- the element schema identity;
- the chunk start index;
- the element count in the chunk;
- the ordered element commitments in the chunk.

The final chunk MAY contain fewer than 256 elements.
No empty chunk is encoded.
List chunks are labelled by element index ranges, not byte offsets.
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

The final byte-string chunk MAY contain fewer than 4096 bytes.
No empty chunk is encoded.
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
| Direct byte string | `logos.value.bstr-direct` |
| Byte-string chunk | `logos.value.bstr-chunk` |
| Direct text string | `logos.value.tstr-direct` |
| Text-string chunk | `logos.value.tstr-chunk` |
| Reference value | `logos.value.reference` |
| Branch node | `logos.value.branch` |

Each physical value object commits to its domain tag, hash profile identifier,
hash suite identifier, semantic commitment-model revision identifier, and typed
payload.
The payload includes the schema root and schema subtree identity needed to
interpret the node.

Small child collections use direct ordered child arrays.
Maps with at most 256 fields commit directly to ordered field child records.
Lists with at most 256 direct elements or chunks commit directly to ordered
child records.
Tuples commit directly to ordered tuple-element child records.
Choice nodes commit directly to the selected arm discriminator and selected
child record.

Large child collections use canonical branch nodes.
A branch node groups an ordered child-record sequence into contiguous groups
of at most 256 child records.
The final group MAY contain fewer than 256 child records.
No empty branch node is encoded.
If a collection has more than 256 child records, the implementation groups the
records into 256-record branch nodes, then recursively applies the same rule
to the resulting branch records until the collection root can commit to at
most 256 child records.

Branch nodes are physical layout nodes only.
They are not semantic value-tree nodes and do not introduce semantic path
segments.
A verified view path continues to use fields, list indices, tuple positions,
choice arms, byte ranges, and text UTF-8 byte ranges.
Proof material carries branch metadata only to reconstruct the physical root.

The branch payload commits to:

- the parent physical node kind;
- the parent schema identity;
- the zero-based start child-record index represented by the branch;
- the number of child records represented by the branch;
- the ordered child records or child branch records.

For map branches, child-record indices are positions in canonical field-name
order.
For list branches, child-record indices are element indices for direct lists
or chunk indices for chunked lists.
For byte-string and text-string branches, child-record indices are chunk
indices.

Direct scalar nodes commit to the scalar schema identity, scalar kind, and
canonical scalar value.
Direct byte-string and text-string nodes are used only below the chunking
thresholds from Section 4.
Chunk nodes commit to the relevant total length, start offset or index, count,
schema identities, and ordered payload or child commitments described in
Section 4.
A semantic `scalar-value` of kind `bstr` is realized physically as
`bstr-direct` if its total byte length is less than or equal to 4096 bytes,
otherwise as `bstr-chunk`.
A semantic `scalar-value` of kind `tstr` is realized physically as
`tstr-direct` if its total UTF-8 byte length is less than or equal to 4096
bytes, otherwise as `tstr-chunk`.
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
The exact hash suite for this draft remains an explicit profile parameter.
This section defines how hash suites are identified and bound into canonical
hash inputs.

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
`logos.hash-profile.2026-05`.
Implementations MUST NOT compare roots across different hash profile
identifiers unless an explicit compatibility profile defines that comparison.

The hash suite identifier is an ASCII text token selected for a concrete
verification context.
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
required by LOGOS-MODULE-INTERFACE Section 4.5 before hashing.
The canonical digest is the selected hash suite applied to that deterministic
CBOR encoding.
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

### 6.1 Informative Example Hash Suite

This subsection is informative, not normative.

For local experimentation, conformance scaffolding, and draft test vectors, an
implementation may use this example hash suite:

- hash suite identifier: `logos.hash-suite.example.blake3-256`
- algorithm: BLAKE3
- digest length: 32 bytes

This example suite is not a final production or chain-verification
requirement.
It MAY be selected by draft conformance vector sets so independent
implementations can reproduce the same roots and digests during interoperability
testing.
Roots produced under this suite are valid only for contexts that explicitly
choose this suite.
Roots from different hash suites are not interchangeable.

## 7. Canonical Hash Payload Shapes

This section defines the exact deterministic CBOR payload shapes for the hash
domains defined by this profile.
These shapes are independent of the selected hash suite.
The selected hash suite determines only the digest algorithm and digest
length.

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
node-kind = tstr
choice-arm-discriminator = tstr
uint64 = uint .size 8
int64 = -9223372036854775808..9223372036854775807
```

The length of `digest`, `schema-root`, and `schema-subtree-root` is determined
by the selected hash suite.
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

For this profile, field `1` is always `logos.hash-profile.2026-05`.
Field `2` is the selected hash suite identifier.
This specification does not select a production hash suite.

### 7.2 Schema Payloads

Schema hash domains use the semantic schema identity payloads defined by
LOGOS-MODULE-COMMITMENT-MODEL Section 9.2.
This profile wraps those payloads in `hash-input`.
It does not redefine the Logos canonical schema model or the schema identity
objects:

| Domain tag | Payload shape |
|------------|---------------|
| `logos.schema.root` | `schema-root-payload` |
| `logos.schema.node` | `schema-node-payload` |
| `logos.schema.leaf` | `schema-leaf-payload` |
| `logos.schema.reference` | `schema-reference-payload` |

Those payloads are encoded as field `4` of `hash-input`.

```cddl
schema-hash-payload =
    schema-root-payload /
    schema-node-payload /
    schema-leaf-payload /
    schema-reference-payload
```

### 7.3 Child Records

Parent payloads do not contain unlabelled digest lists.
They contain typed child records:

```cddl
child-record = {
    0: child-label,
    1: node-kind,
    2: digest,
    ? 3: schema-subtree-root,
}

child-label =
    field-label /
    index-label /
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

tuple-label = {
    0: "tuple-position",
    1: uint64,
}

choice-label = {
    0: "choice-arm",
    1: choice-arm-discriminator,
}

byte-range-label = {
    0: "byte-range",
    1: uint64,  ; start byte offset
    2: uint64,  ; byte count
}

branch-label = {
    0: "branch",
    1: uint64,  ; start child-record index
    2: uint64,  ; child-record count represented by branch
}
```

The optional schema identity field is present when the parent payload needs to
re-bind the child digest to a child schema identity that is not already
unambiguous from the child label and parent schema identity.

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
    3: child-record,
}
```

Map and field payloads are:

```cddl
map-payload = {
    0: "map",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,            ; field count
    4: [* child-record],  ; field records in canonical field-name order
}

field-payload = {
    0: "field",
    1: schema-root,
    2: schema-subtree-root,
    3: field-name,
    4: child-record,
}

absent-payload = {
    0: "absent",
    1: schema-root,
    2: schema-subtree-root,
    3: field-name,
}
```

List and list-chunk payloads are:

```cddl
list-payload = {
    0: "list",
    1: schema-root,
    2: schema-subtree-root,
    3: schema-subtree-root, ; element schema identity
    4: uint64,              ; list length
    5: [* child-record],    ; element, chunk, packed chunk, or branch records
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
    4: [* child-record],  ; tuple-position records
}

tuple-element-payload = {
    0: "tuple-element",
    1: schema-root,
    2: schema-subtree-root,
    3: uint64,            ; zero-based tuple position
    4: child-record,
}

choice-payload = {
    0: "choice",
    1: schema-root,
    2: schema-subtree-root,
    3: choice-arm-discriminator,  ; selected arm discriminator
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
    5: child-record,
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
    3: node-kind,          ; parent physical node kind
    4: uint64,             ; start child-record index
    5: uint64,             ; child-record count represented by this branch
    6: [* child-record],   ; child or child-branch records
}
```

The child record array in a branch payload MUST contain between 1 and 256
records.
Branch records are ordered by their represented child-record index.

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
    bstr-direct-payload /
    bstr-chunk-payload /
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
| `logos.value.bstr-direct` | `bstr-direct-payload` |
| `logos.value.bstr-chunk` | `bstr-chunk-payload` |
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
    0: node-kind,
    1: domain-tag,
    2: hash-payload,
    3: [* sibling-record],
}

sibling-record = {
    0: child-label,
    1: node-kind,
    2: digest,
    ? 3: schema-subtree-root,
}
```

The proof step payload is the parent payload reconstructed at that step.
The proof step domain tag MUST match the payload shape according to Section
7.5.
The verifier replaces the disclosed child or previously reconstructed child
digest into the payload position identified by the typed path and sibling
records, hashes the resulting canonical `hash-input`, and proceeds to the
next proof step.

For packed scalar list proofs, the disclosed item MUST include the whole
packed scalar chunk that contains the requested element.
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
| `choice-arm` | A selected choice arm discriminator |
| `bstr-range` | A byte range inside a byte string |
| `tstr-utf8-range` | A byte range inside the canonical UTF-8 encoding of a text string |

A `field` segment contains the canonical field name.
A `list-index` segment contains the zero-based element index.
A `tuple-position` segment contains the zero-based fixed tuple position.
A `choice-arm` segment contains the selected arm discriminator.
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
At minimum, proof material carries:

- the node kind and schema identity for each reconstructed node;
- sibling digests needed at each level;
- labels, field names, indices, tuple positions, offsets, or choice-arm
  identities needed to place the disclosed item among its siblings;
- chunk metadata when the proof crosses chunked lists, byte strings, or text
  strings;
- packed-chunk material when the proof crosses a packed scalar list chunk;
- the child ordering information needed to reconstruct each parent payload.

Proofs MUST NOT rely on unlabelled digest concatenation.
Sibling digests are interpreted only together with their labels, indices,
offsets, schema identities, and parent node kind.

For a map field proof, the proof material includes the disclosed field value or
absent marker, the field name, the field schema identity, and the sibling field
digests with their field names or canonical field positions.
The verifier reconstructs the map node using canonical field-name ordering.

For a list element proof in an unchunked list, the proof material includes the
list length, the element index, the element schema identity, the disclosed
element value, and the sibling element digests with their indices.

For a list element proof in a chunked list, the proof material also includes
the chunk size, chunk start index, element offset inside the chunk, sibling
element digests or packed chunk material inside the chunk, and sibling chunk
digests above the chunk.
The semantic path remains the list element index.
Chunk indices and offsets are physical proof details, not semantic path
segments.

For a byte-string range proof, the proof material includes the total byte
length, chunk size, chunk start byte offset, byte count, disclosed bytes, and
sibling chunk digests needed to reconstruct the byte-string commitment.
The semantic path uses a `bstr-range` segment.

For a text-string byte-range proof, the proof material includes the total UTF-8
byte length, chunk size, chunk start byte offset, byte count, disclosed UTF-8
bytes, and sibling chunk digests needed to reconstruct the text-string
commitment.
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
3. Validate the typed path against the schema.
4. Normalize the disclosed value, disclosed range, or absent marker under the
   schema selected by the typed path.
5. Recompute the disclosed item's leaf or subtree digest using the hash input
   rules from Section 6.
6. Apply proof steps from the disclosed item toward the root, checking node
   kinds, schema identities, labels, field names, indices, offsets, chunk
   metadata, packed-chunk material, and sibling ordering at each step.
7. Compare the recomputed root with the verified view's value root.

If any check fails, the verified view is invalid.
If the recomputed root equals the value root and all schema, profile, suite,
path, and proof checks succeed, the verified view is valid relative to that
value root.

Validity relative to a value root does not imply that the root is trusted.
Trust in roots, signers, packages, runtimes, remote providers, audit logs, or
consensus systems is outside this specification.

## 9. Conformance

A conforming implementation of this hash profile MUST construct canonical hash
inputs and payloads according to Sections 6 and 7, encode them using the Logos
deterministic CBOR profile required by LOGOS-MODULE-INTERFACE Section 4.5, and
apply the selected hash suite exactly as declared by the verification context.
It MUST reject malformed hash inputs, unknown identifiers, wrong digest
lengths, wrong domain tags, non-canonical CBOR encodings, and mismatched
domain-to-payload shapes as described by this specification.

An implementation conforms to a published hash-profile vector set when it
produces identical digests for the declared hash suite and rejects every
malformed input listed by that vector set.

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
The benefit is that roots, paths, proof material, runtime negotiation, and
module-interface compatibility all refer to the same schema-bound contract
objects.
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

## Appendix A. Example Schema-Root Vector (Informative)

This appendix gives an informative hash-profile vector for the construction
vector in LOGOS-MODULE-COMMITMENT-MODEL Appendix A.
It uses the informative BLAKE3-256 example suite from Section 6.1.
The production hash suite remains a verification-context parameter.

The vector hashes one `logos.schema.root` hash input whose payload is the
`normalized-schema-root` object from LOGOS-MODULE-COMMITMENT-MODEL
Appendix A.

Hash input fields:

- field `0`: `logos.schema.root`;
- field `1`: `logos.hash-profile.2026-05`;
- field `2`: `logos.hash-suite.example.blake3-256`;
- field `3`: `logos.commitment-model.2026-06`;
- field `4`: the Appendix A `normalized-schema-root` object from
  LOGOS-MODULE-COMMITMENT-MODEL.

The deterministic CBOR hash-input byte length is `831` bytes.
The deterministic CBOR hash-input bytes, in hexadecimal, are:

```text
a500716c6f676f732e736368656d612e726f6f7401781a6c6f676f732e686173
682d70726f66696c652e323032362d30350278236c6f676f732e686173682d73
756974652e6578616d706c652e626c616b65332d32353603781e6c6f676f732e
636f6d6d69746d656e742d6d6f64656c2e323032362d303604a5006b73636865
6d612d726f6f7401781e6c6f676f732e636f6d6d69746d656e742d6d6f64656c
2e323032362d3036026773746f7261676503800487a300647479706501717374
6f726167652e626c6f625f6861736802a300697072696d697469766501646273
747202a3006473697a65011820021820a300656576656e74017573746f726167
652e6368616e6765645f6576656e7402a200636d61700182a3006363696401f4
02a2006f6c6f63616c2d7265666572656e6365016b73746f726167652e636964
a3006664696765737401f402a2006f6c6f63616c2d7265666572656e63650171
73746f726167652e626c6f625f68617368a3006474797065016b73746f726167
652e63696402a300697072696d697469766501647473747202a3006473697a65
0101021880a300666d6574686f64016e73746f726167652e65786973747302a3
00666d6574686f64017673746f726167652e6578697374735f72657175657374
027773746f726167652e6578697374735f726573706f6e7365a3006e6d657468
6f642d72657175657374017673746f726167652e6578697374735f7265717565
737402a200636d61700181a300636b657901f402a2006f6c6f63616c2d726566
6572656e6365017273746f726167652e6c6f6f6b75705f6b6579a3006f6d6574
686f642d726573706f6e7365017773746f726167652e6578697374735f726573
706f6e736502a200636d61700181a3006665786973747301f402a20069707269
6d69746976650164626f6f6ca3006474797065017273746f726167652e6c6f6f
6b75705f6b657902a2006663686f6963650182a2007063626f722d6d616a6f72
2d7365742e3201a2006f6c6f63616c2d7265666572656e6365017173746f7261
67652e626c6f625f68617368a2007063626f722d6d616a6f722d7365742e3301
a2006f6c6f63616c2d7265666572656e6365016b73746f726167652e636964
```

The BLAKE3-256 digest of those bytes is:

```text
b206df968f4d7024dd62e55da0308be42587dc3b72d4e48e8d9d9f3390e8c3f4
```

Under the informative example suite, that digest is the schema root for the
construction vector's whole schema.

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-COMMITMENT-MODEL -- Semantic commitment model specification.

### Informative

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
