# LOGOS-MODULE-COMMITMENT-MODEL

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Commitment Model                                 |
| Slug         | 302                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the semantic commitment model for Logos schemas and
Logos values.
It defines how Logos schemas receive stable semantic identities, how concrete
typed values are normalized before commitment, and how semantic paths for
partial verified views are identified.

This specification defines what is being committed.
It does not define the canonical production hash function, physical hash
layout, packing, chunking, proof encoding, or byte-level value-root profile.
Those are defined by LOGOS-MODULE-HASH-PROFILE.

For concrete module and interface contracts,
the commitment model is a third view of the same contract defined by LOGOS-MODULE-INTERFACE:

- the **interface view** defines the module's schema and C ABI surfaces;
- the **transport view** maps schema-defined values to Logos deterministic
  CBOR bytes;
- the **commitment view** maps schemas and typed values to semantic identities,
  value trees, and verified-view paths.

Supporting schemas use the same commitment view without defining a module, provider, C ABI, method, or event surface.

This specification does NOT define remote runtime management, plugin loading,
package trust, trusted computation protocols, challenge games, proving
circuits, or on-chain contracts.
Those topics may consume the commitment model defined here, but they are
specified elsewhere.

## 1. Introduction

Logos schemas define module methods, responses, events, and named data types.
The Interface specification defines concrete module schemas, interface contract schemas, supporting schemas, and their permitted dependencies.
It also defines how callable contract schemas map to a C ABI and Logos deterministic CBOR transport values.

The commitment model adds a third view:
a canonical semantic commitment view.
The commitment view lets independent implementations compute the same schema
identity, derive the same semantic value tree for a concrete typed value, and
name the same semantic path for a verified view over part of that value.

A Merkle proof is only meaningful relative to a root.
This specification defines the semantic schema and value structures that roots
commit to.
It does not define which roots a verifier should trust, how roots are anchored,
or how non-Logos proof systems are authenticated.
Those concerns belong to trust, consensus, package, runtime, or application
profiles that consume the commitment model defined here.

This specification defines the semantic commitment plumbing such systems can build on.

## 2. Source Model

Commitment is defined over a Logos canonical schema model and a normalized
Logos value model.
It is not defined over raw CDDL text, raw `cdCDDLe` bytes, raw deterministic
CBOR bytes, generated C structs, or language-specific module-kit
representations.

This specification uses "schema model" for a structured representation of the
same contract schema at a particular processing layer.
A parsed/resolved CDDL model is a parser-level representation.
A `cdCDDLe` canonical schema model is a generic canonical CDDL representation.
A Logos canonical schema model is the Logos-specific semantic representation
used for schema identity and commitment.
These are not separate schemas.
They are different models of the same authored schema at different layers,
similar to a compiler representing the same source program first as syntax and
then as semantic forms with resolved names and types.

LOGOS-MODULE-INTERFACE owns the accepted authoring representations and their mapping to one canonical schema.
This specification begins from that schema's canonical CDDL representation and does not make raw authoring syntax an identity input.

CDDL, `cdCDDLe`, and Logos deterministic CBOR are the schema and value interchange surfaces used here:

- CDDL schema text is parsed and resolved into a CDDL rule graph.
- `cdCDDLe` canonicalizes that resolved CDDL rule graph into a generic
  canonical CDDL schema model.
  For clarity:
  `cdCDDLe` also defines deterministic CBOR bytes for that model when bytes
  are needed, but Logos schema-model construction consumes the abstract model.
- Logos-specific schema-model rules are then applied to the generic
  `cdCDDLe` canonical schema model to produce the Logos canonical schema
  model.
  These rules include the Logos domain interpretation:
  schema namespace, contract-bearing names, method and event declarations,
  schema role, namespace, callable declarations, named-definition references,
  implemented interfaces, and other identity-relevant Logos semantics.
- Logos deterministic CBOR data is decoded under a known schema into the
  normalized Logos value model.

The processing chain from the canonical CDDL representation is:

```text
CDDL source text
  -> CDDL parser / resolver
      resolved CDDL rule graph
  -> cdCDDLe
      generic canonical CDDL schema model
  -> Logos schema-model construction (applies Logos domain interpretation)
      Logos canonical schema model
  -> LOGOS-MODULE-HASH-PROFILE
      schema roots and schema subtree roots
```

### 2.1 Object And Encoding Boundaries

This specification distinguishes abstract objects, serialized bytes, and hash
outputs.
Conforming implementations MUST NOT treat one layer's bytes or identifiers as
another layer's canonical object unless this specification explicitly says so.

| Layer object | Kind | Owning specification | Identity role |
|--------------|------|----------------------|---------------|
| CDDL source text | source text | LOGOS-MODULE-INTERFACE | Authoring input; not a schema identity input by itself |
| resolved CDDL rule graph | parser/resolver output | CDDL parser/resolver plus `cdCDDLe` input rules | Input to `cdCDDLe`; not serialized identity by itself |
| `cdCDDLe` canonical CDDL schema model | abstract canonical CDDL schema object | `cdCDDLe` | Generic canonical CDDL object; not a Logos schema root by itself |
| `cdCDDLe` canonical schema bytes | RFC 8949-based deterministic CBOR bytes | `cdCDDLe` | Deterministic encoding of the generic model; not a Logos schema root by itself |
| Logos domain interpretation | interpretation rules | LOGOS-MODULE-COMMITMENT-MODEL | Maps generic CDDL schema data into Logos schema meaning |
| Logos canonical schema model | abstract semantic schema object | LOGOS-MODULE-COMMITMENT-MODEL | Input to Logos schema roots and schema subtree roots |
| Logos module contract | abstract contract object | LOGOS-MODULE-INTERFACE plus LOGOS-MODULE-COMMITMENT-MODEL | Interface, transport, and commitment views of the same method/event/type contract |
| Logos supporting schema | abstract data-schema object | LOGOS-MODULE-INTERFACE plus LOGOS-MODULE-COMMITMENT-MODEL | Commitment view of named non-callable data types |
| Logos deterministic CBOR payload bytes | deterministic CBOR bytes | LOGOS-MODULE-INTERFACE | Transport/interchange encoding of concrete Logos values |
| normalized Logos value model | semantic typed value object | LOGOS-MODULE-COMMITMENT-MODEL | Input to value commitments and verified-view paths |
| hash-input records | deterministic CBOR records | LOGOS-MODULE-HASH-PROFILE | Exact bytes hashed by the mandatory BLAKE3-256 suite |
| schema roots, schema subtree roots, and value roots | hash outputs | LOGOS-MODULE-HASH-PROFILE | Commitment identifiers, not encodings |

Raw `cdCDDLe` bytes and raw Logos deterministic CBOR payload bytes are not
semantic roots.
They must first be interpreted as the appropriate abstract object and then
processed by the owning Logos specification.

The Logos canonical schema model has a Logos-specific schema-as-data
representation.
In this specification, the unqualified phrase "schema-as-data representation"
refers to that Logos-specific data representation unless explicitly qualified
as the generic `cdCDDLe` schema-as-data representation.
"Schema-as-data representation" names the requirement that Logos
schemas must become deterministic data before hashing.
"Logos canonical schema model" names the abstract model defined by this
specification.
To compute a schema root, Logos starts from the Logos canonical schema model.
The relevant Logos canonical schema object is wrapped in the hash-input record
defined by LOGOS-MODULE-HASH-PROFILE, encoded as deterministic CBOR, and then
hashed.
Logos does not hash the generic `cdCDDLe` byte encoding as the Logos schema
root.
It must be deterministic enough to encode, hash, compare, and reference
without depending on the original CDDL text or on presentation details already
removed by `cdCDDLe`.

CDDL standardizes a notation for describing CBOR and JSON data structures.
It does not define a canonical CBOR serialization of CDDL schemas themselves.
`cdCDDLe` defines the generic canonical CDDL schema model and its deterministic
CBOR encoding.
This specification defines the Logos domain interpretation over `cdCDDLe` and
the Logos canonical schema model used for schema identity and commitment.

The Logos canonical schema model is needed for schema identity because raw
CDDL text is too unstable:
whitespace, comments, declaration order, and equivalent local spelling can
otherwise create accidental identity differences.

The normalized value model is needed for value commitments and verified views.
Raw deterministic CBOR bytes are deterministic serialization bytes, but their
byte boundaries are not necessarily the right semantic commitment boundaries.
Verified views need semantic boundaries such as fields, list elements, map
entries, typed scalar values, and possibly packed scalar groups in a physical
hash profile.

This specification uses conservative normalization.
It normalizes only cases whose equivalence is clear from the Logos schema
model and from the `cdCDDLe` canonical schema model it consumes.
It does not attempt arbitrary CDDL semantic equivalence.

## 3. Canonical Schema Model

The Logos canonical schema model is the Logos-specific logical schema that
conforming implementations hash, compare, and reference.
It is derived by applying Logos-specific schema-model rules to the `cdCDDLe`
canonical CDDL schema model.
It is not the raw source text, the generic `cdCDDLe` byte encoding, or a
generated language binding.

The Logos canonical schema model contains, at minimum:

- a schema root object;
- named type declarations;
- method declarations;
- method request declarations;
- method response declarations;
- event declarations;
- map, field, array, list, tuple, choice, primitive, literal, and reference
  nodes.

Section 3.1 defines how the Logos domain interpretation consumes the
name-preserving `cdCDDLe` canonical CDDL schema model and constructs those
declarations, imports, and references.

The Logos domain interpretation MUST NOT rely on structural equivalence alone
to merge contract-bearing declarations.
Two `cdCDDLe` rules with the same structure but different contract-bearing
qualified names can produce different Logos schema subtree roots.
For example, two method request declarations with the same map fields remain
different declarations if their qualified request names differ.

Names that are not contract-bearing MAY still be present in the `cdCDDLe`
canonical model for diagnostics, reference resolution, or tooling.
Such names affect Logos schema identity only if this specification maps them
into the Logos canonical schema model.

Event payload values use the same normalized value root, semantic value tree,
and hash-profile rules as method request and response values;
see Section 9.3.

The Logos canonical schema model is an abstract semantic object.
Its canonical schema-as-data representation is finite.
The whole schema has a schema root.
A named definition or structural subtree inside the schema has a schema subtree
root.
A schema leaf hash identifies a leaf in the canonical schema representation.
These identify related views of the same abstract schema model,
not unrelated identity systems.

Named references are terminal reference nodes in the canonical schema-as-data
representation.
The declaration/reference relation in the abstract model is a graph and MAY
contain recursive or cyclic references through named type declarations.
Those cycles are valid only through `reference-schema` nodes.
Implementations MUST NOT construct schema roots, schema subtree roots, schema
leaf hashes, or schema-node paths by recursively inlining local or
common-schema references.
Schema-node paths and schema leaf hashes stop at reference nodes.

Schema identity tracks the Logos canonical schema model, not authoring style.
Comments, whitespace, source formatting, source file layout, and source
declaration order are not identity inputs.
They MAY be retained by tooling as diagnostic metadata, but they do not affect
canonical schema identity.
These presentation details are removed before or during `cdCDDLe`
canonicalization and are not reintroduced by the Logos domain interpretation.

Unordered schema collections are canonicalized before hashing:

- top-level declarations are ordered by qualified schema name;
- method and event collections are ordered by qualified schema name;
- map fields are ordered by canonical field name;
- choice arms are ordered by the deterministic-CBOR encodings of their canonical arm schema nodes;
- imports and references are ordered by canonical reference identity.

Canonical qualified-name and field-name order is ascending lexicographic order over the values' valid UTF-8 byte strings.
Choice-arm schema-node encodings are ordered by ascending lexicographic byte-string order.
These collection-ordering rules are distinct from deterministic-CBOR map-key order over encoded text strings.

Only inherently positional constructs preserve order.
Tuple elements and fixed-length array positions are ordered by position.
Variable-length lists have one element-type child in the schema model;
the order of concrete list values is a value-model concern.

Ambiguous choices whose arms cannot be distinguished by the Logos decoding
rules are invalid.
Source declaration order MUST NOT be used to disambiguate choices.
Section 3.1 defines structural choice selection.
Section 9.1 defines canonical choice-arm order and indices.

The Logos prelude and the Logos common schema surface are conceptually
distinct.
Prelude fixed-width integer aliases such as `uint64` normalize directly to
built-in fixed-width primitive schema leaves.
Reusable Logos-defined common types and well-known method surfaces are normal
schema definitions in a well-known common schema namespace and are referenced
explicitly when used.

### 3.1 Logos Schema-Model Construction

This section defines the construction bridge
from a valid Logos concrete module schema, interface contract schema, supporting schema,
or the pinned Logos common schema surface,
as defined by LOGOS-MODULE-INTERFACE,
into the Logos canonical schema model.
The rules here are normative.

The construction input for one Logos schema document is its name-preserving `cdCDDLe` canonical schema model,
its schema-role metadata when present,
and the exact dependency documents accepted under LOGOS-MODULE-INTERFACE.
The output is one Logos canonical schema root object for that document.
Each interface or supporting dependency is constructed independently and retains its own schema root.
Construction does not produce a consolidated root over the complete input set.

Construction proceeds as follows:

1. Determine the schema role.
   A document marked by `_module` is a concrete module schema.
   A document marked by `_interface` is an interface contract schema.
   The pinned Logos common schema surface is the sole unmarked exception defined by LOGOS-MODULE-INTERFACE.
   Every other unmarked document is a supporting schema.
   Role metadata is validated under LOGOS-MODULE-INTERFACE and is not emitted as a schema declaration.
2. Identify the schema namespace.
   Ignore the metadata declarations `_module`, `_interface`, and `_implements`
   for schema-declaration construction.
   The primary schema namespace is the longest common dot-segment prefix
   shared by all local qualified declarations that are not metadata declarations
   and not common-schema declarations.
   It MUST contain at least one segment and MUST be a proper prefix of every local declaration name.
   If `_interface` is present, its value MUST match the primary schema namespace.
   Exactly one primary schema namespace MUST be present in this revision.
   Every local declaration MUST use that namespace.
   A local non-metadata declaration without a qualified name in the primary
   namespace is invalid.
3. Classify local declarations according to the schema role.
   In a concrete module or interface contract schema,
   declarations ending in `_request` are method request declarations,
   declarations ending in `_response` are method response declarations,
   declarations ending in `_event` are event declarations,
   and every remaining local declaration is a named type declaration.
   The pinned common schema surface uses the same callable-suffix classification for its assigned well-known declarations.
   Every local declaration in a supporting schema is a named type declaration.
   The metadata declarations `_module`, `_interface`, and `_implements`
   are not emitted as `schema-declaration` entries.
4. In a concrete module or interface contract schema,
   pair each request declaration with the response declaration that has the
   same qualified base name.
   The qualified base name is produced by stripping the `_request` or
   `_response` suffix from a declaration in the primary schema namespace.
   For example, `storage.exists_request` and `storage.exists_response` produce
   the method declaration `storage.exists`.
   A request without a matching response, or a response without a matching
   request, is invalid.
5. Emit one `schema-declaration` for each local named type, method, method
   request, method response, and event.
   Method declaration bodies use `method-declaration`.
   Type, request, response, and event declaration bodies use `schema-node`.
   The `schema-node` body of every method request, method response, and event declaration MUST be a `map-schema`.
   All emitted declarations MUST have distinct qualified names.
   A synthesized method name that collides with another declaration makes the contract invalid.
6. Translate declaration bodies into `schema-node` values using the rules below.
   A local named-type reference becomes a local reference.
   An accepted external named-definition reference becomes an imported reference containing the referenced schema root and declaration subtree root.
   A concrete module may import named types from explicitly supplied supporting schemas and may reference definitions in the pinned common schema.
   An interface contract or supporting schema may reference only local declarations and definitions in the pinned common schema.
   A supporting schema dependency of another supporting schema is invalid.
7. For a concrete module schema,
   use an empty implemented-interface-root collection when `_implements` is absent.
   Otherwise, read one root from each direct byte-string literal element of its nonempty fixed-content array, in array order.
   The `_implements` rule MUST satisfy the syntax and ordering requirements in LOGOS-MODULE-INTERFACE Section 1.2.
   Each root MUST resolve to exactly one explicitly supplied interface document whose recomputed root matches that entry.
   Exact duplicate roots and two roots whose interface documents declare the same namespace are invalid.
   Interface and supporting schemas have no implemented-interface roots.
8. Sort declarations, implemented-interface roots, map fields, and choice arms according to Section 9.1 before hashing or comparison.

The `logos.schema` introspection bootstrap is not automatically included in an
ordinary module's schema root.
It is a runtime-provided common-schema surface defined by
LOGOS-MODULE-INTERFACE.
It participates in a module schema only when that schema explicitly references
the corresponding common-schema definitions through the import/reference rules
in this specification.

The `logos_<module>_dispatch()` ABI symbol defined by LOGOS-MODULE-INTERFACE is
also not included in the Logos canonical schema model.
It is an ABI entrypoint for invoking schema-defined methods, not a schema
declaration, method declaration, request declaration, response declaration, or
event declaration.

The `logos_<module>_call_surface()` ABI symbol and its deterministic-CBOR
provider descriptor are also outside the Logos canonical schema model.
The descriptor is metadata that carries separately committed contract documents.
Its encoded bytes do not receive a schema root or create a synthetic root over
the complete provider surface.
Each contained schema document independently produces its own schema root under this specification.

Primitive schema forms translate as follows:

- `bool`, `tstr`, `bstr`, and the Logos prelude fixed-width integer
  aliases translate to `primitive-schema`.
- A prelude integer alias translates to the corresponding scalar kind and does
  not create an import.
- Boolean and text-string literals translate to `literal-schema` with the
  corresponding `scalar-kind`.
  A non-negative integer literal translates with scalar kind `uint64` and MUST fit that type.
  A negative integer literal translates with scalar kind `int64` and MUST fit that type.
  A byte-string literal in `_implements` is role metadata and is handled before declaration construction.
  A byte-string literal in a schema declaration body is invalid.
- `tstr .size (min..max)` and `bstr .size (min..max)` translate to a
  `primitive-schema` with a `size-constraint`.
- `tstr .size n` and `bstr .size n` translate to a `size-constraint` whose
  minimum and maximum are both `n`.

Compound schema forms translate as follows:

- a CDDL map with known fields translates to `map-schema`;
- an optional map field translates to a `schema-field` whose optional flag is
  `true`;
- a required map field translates to a `schema-field` whose optional flag is
  `false`;
- `[* T]` translates to `list-schema`;
- `[T, U, ...]` translates to `tuple-schema`;
- `T1 / T2 / ...` translates to `choice-schema`;
- a reference to a local named type declaration translates to a local
  `reference-schema`;
- a reference to a local method, method request, method response, or event
  declaration from inside a `schema-node` is invalid in this revision;
- an accepted reference to a named definition in a supporting schema or the pinned Logos common schema translates to an imported `reference-schema`.

Any `cdCDDLe` construct without a mapping in this section is invalid in a Logos schema document.

Local named references MUST preserve the referenced qualified name.
They MUST NOT be replaced by the referenced declaration body when constructing
the referring `schema-node`.
This preserves schema identity for local named types and prevents two
different local names with the same structure from collapsing at reference
sites.

Local named type references MAY be recursive or mutually recursive.
A local recursive reference is represented by the finite `local-reference`
node that names the referenced local type declaration.
It does not inline the referenced declaration body.
An implementation that provides an expanded diagnostic view over local
references MUST detect reference cycles.
That expanded view is not the Logos canonical schema model and MUST NOT be
used as the schema identity input.

Choice arms are interpreted by their complete arm schema nodes.
A decoded value matches an arm when the complete value is valid under that arm's schema node.
A decoded value is valid for a choice schema when exactly one arm matches it.
If no arm matches, the value is invalid for the choice schema.

A choice schema is valid only when the structural selection-plan construction in this section succeeds.
The resulting plan MUST prove that no decoded value can match more than one arm.
Source declaration order MUST NOT participate in plan construction or arm selection.

A structural selection plan is a finite decision tree whose leaves contain at most one candidate arm.
Construction begins with every arm of the choice as the candidate set.
When a node has more than one candidate, construction considers the following structural tests in order:

1. the decoded value's CBOR major type;
2. the decoded scalar's exact literal value;
3. the decoded array's element count for fixed tuples;
4. the presence and exact scalar value of a closed-map field; and
5. the presence or absence of a closed-map field.

The scalar-literal test partitions scalar values into one outcome for each distinct exact scalar literal constraint occurring among the candidate arms and one outcome for every other scalar value.
The tuple-length test partitions arrays into one outcome for each distinct fixed tuple length occurring among the candidate arms and one outcome for every other array length.
A map-field-literal test partitions maps into an absent outcome, one outcome for each distinct exact scalar literal constraint occurring for that field among the candidate arms, and one outcome for every other present field value.
A map-field-presence test partitions maps into present and absent outcomes.
Map-field tests are considered by canonical field-name order within each test kind.

Each kind-specific test also has a not-applicable outcome covering every decoded value for which its observation is unavailable: non-scalar values for the scalar-literal test, non-array values for the tuple-length test, and non-map values for either map-field test.
An arm remains a candidate for a not-applicable outcome when its schema can accept at least one value covered by that outcome.
The outcomes of every structural test, including its not-applicable outcome when defined, MUST assign every decoded value to exactly one outcome.

For each possible test outcome, an arm remains a candidate when its schema can accept a value having that observed structure.
A test makes progress when every outcome, including its not-applicable outcome when defined, retains a strict subset of the current candidate set.
Outcomes retaining no candidates are permitted.
Construction uses the first test in the order above that makes progress, creates a child for each outcome retaining candidates, and repeats the procedure for each child.
If no available test makes progress while more than one candidate remains, the choice schema is invalid.

Structural outcome computation is conservative.
An arm MUST remain a candidate unless its schema proves that it rejects the observed major type, scalar literal, tuple length, field value, or field presence.
In particular, an optional map field permits both the present and absent outcomes, and a field without an exact literal constraint permits every field-value outcome allowed by its field schema.
Because Logos maps are closed, a field not accepted by a map arm permits only the absent outcome for that arm.

Named references are followed when computing structural outcomes, but they remain terminal reference nodes in the canonical schema model.
Implementations MUST memoize reference results and detect recursive and mutually recursive reference components.
A reference cycle is valid when a finite structural outcome can be derived without recursively inlining the reference.
A non-productive reference cycle that yields no finite structural outcome cannot distinguish a choice arm.
If plan construction depends on such a cycle and no other test makes progress, the choice schema is invalid.

The structural selection plan is derived from the canonical arm schema nodes and is not an additional schema identity input.
Each selection-plan leaf identifies its candidate by the canonical arm index defined in Section 9.1.
An implementation MAY compile it into tables, branches, or another behaviorally equivalent dispatcher.
For a decoded value, the implementation follows the plan to either no candidate or one candidate.
It then MUST validate the complete value against the candidate arm schema.
Failure to select a candidate or failure of complete arm validation makes the value invalid for the choice schema.
An implementation need not validate the value independently against every arm.

The following choice schemas are normative plan-construction examples.
Map examples use closed maps, as required by this specification.

| Choice schema | First effective structural test | Result |
|---------------|---------------------------------|--------|
| `uint64 / tstr` | CBOR major type | Valid |
| `[uint64] / [uint64, uint64]` | Fixed tuple length | Valid |
| `{ status: "failed", error: bstr } / { status: "failed", realization: bstr }` | Presence of `error` | Valid |
| `{ request: bstr, ? response: bstr } / { response: bstr }` | Presence of `request` | Valid |
| `{} / { error: bstr }` | Presence of `error` | Valid |
| `{ operation: "evaluate", outcome: "allow" } / { operation: "evaluate", outcome: "deny" } / { operation: "issue-grant", outcome: "deny" }` | Exact `operation` literal, then exact `outcome` literal where needed | Valid |
| `tstr / "fixed"` | No test separates the overlapping arms | Invalid |
| `A / B`, where both definitions have distinct required `kind` literals and may refer recursively to either definition | Exact `kind` literal | Valid |
| `A / B`, where `A = B` and `B = A` provide no other structure | No finite structural test | Invalid |

The tagged recursive case is valid because its `kind` outcome is finite without expanding the recursive field.
The alias cycle is invalid because reference expansion yields no finite structural outcome.
These results apply identically when an arm is reached through a local or imported reference.

## 4. Schema Identity

A Logos schema identity is a hash over the Logos canonical schema model.
It is not a hash over raw CDDL text, generated C headers, generated dispatch
code, generic `cdCDDLe` canonical schema bytes, package metadata, or runtime
discovery records.

The schema identity is the schema root:
the root hash of the whole Logos canonical schema tree.
It commits to the semantic schema surface that a conforming implementation
needs in order to interpret module values:

- the semantic commitment-model revision identifier;
- the schema namespace;
- method request and response declarations;
- event declarations;
- named type declarations;
- explicit imports and references;
- the identities of referenced common-schema definitions.

The schema identity does not commit to comments, whitespace, source formatting,
or other raw text details that are removed by `cdCDDLe` and the Logos
canonical schema model.

Schema subtree roots identify named definitions or structural subtrees inside
the same Logos canonical schema tree.
Named type, method, method request, method response, event, and reusable
subschema identities are schema subtree roots.
They are not ad-hoc hashes over local text snippets.

Named schema subtree roots commit to:

- the semantic commitment-model revision identifier;
- the node kind;
- the qualified schema definition name;
- the Logos canonical definition body.

An anonymous structural schema node has a structural subtree root.
It is the `logos.schema.node` digest of the following payload:

```cddl
schema-structural-node-payload = {
    0: "schema-structural-node",
    1: semantic-commitment-model-revision,
    2: schema-declaration-kind,
    3: qualified-name,       ; nearest named declaration
    4: schema-node-path,
    5: schema-node,
}
```

The path resolves from the nearest named declaration body to the structural node in field `5`.
An empty path uses the named declaration's schema subtree root instead of this payload.
A primitive, literal, or reference node uses its schema leaf hash instead of this payload.
These rules assign exactly one schema identity to every schema node consumed by the normalized value model.

Anonymous structural child nodes commit to their role inside the nearest named
parent and to their Logos canonical structure.
For example, two method request maps with the same field shape but different
qualified names have different named schema subtree roots.
`storage.upload_url_request = { cid: tstr }` and
`storage.download_url_request = { cid: tstr }` are different semantic
definitions even though their map bodies are structurally identical.

The whole-schema identity commits to the schema namespace and the identities
of the top-level named schema nodes.
Named schema subtree identity commits to the qualified schema definition name
and the Logos canonical definition.
This is a hierarchy:
schema roots and schema subtree roots are different levels of the same schema
identity tree.

Schema leaf hashes identify leaf schema nodes inside that same hierarchy.
A schema leaf hash is computed for a leaf schema node under the nearest named
schema declaration.
It commits to the semantic commitment-model revision identifier, the nearest named
declaration kind and qualified name, the canonical schema path from that
declaration to the leaf, and the Logos canonical leaf node.
It is not an independent naming system and MUST NOT be accepted as a whole
schema root or named schema subtree root.

A method identity is the schema subtree root of the `schema-declaration` whose
kind is `"method"`.
It commits to the qualified method name, the qualified request declaration
name, and the qualified response declaration name under the selected semantic
commitment-model revision.
Method identity is computed under the existing `logos.schema.node` domain from
the `schema-node-payload` of the method declaration.
It is not a separate hash domain.

For a primary module method,
the defining schema root is the concrete module schema root.
For an implemented interface method,
the defining schema root is the implemented interface schema root.
The concrete module schema root commits to the fact that the interface is implemented,
but the method identity remains the method identity from the interface contract.
Method identity is independent of the path used to invoke the method.
The concrete provider may realize an implemented interface call through its
generic dispatch ABI or a schema-derived per-method C function.
Neither provider ABI path changes the implemented interface schema root that defines the method.
Invocation, attribution, authorization, package, and audit records may link
the call to other system evidence outside this commitment model.
They do not replace the defining schema root of the target method.

ABI entrypoints that dispatch to schema-defined methods, including
`logos_<module>_dispatch()`, do not have method identities in this commitment
model.
Commitments, verified views, audit material, authorization material, and
conformance vectors identify the target schema method,
the defining schema root,
and the corresponding request or response value.
They do not identify the dispatch entrypoint used to invoke it.
When external attribution is needed,
other specifications may link external records to the defining schema root and value root.
Those records may include concrete module schema roots, package records,
runtime routes, authorization decisions, or audit records.
This specification does not define that attribution evidence.
Such evidence does not make a concrete module schema root the defining schema
root for an implemented interface method.

Schema identity uses schema namespaces and qualified schema definition names,
not runtime module names, socket names, C ABI symbol prefixes, or package and
deployment identities.
A schema namespace names a schema-defined contract namespace.
A runtime module name names an operational load and routing target.
These names commonly correspond by convention, but they are separate identity
axes.

For example, `storage` may be the schema namespace,
`storage.exists_request` may be a qualified schema definition name,
`storage_module` may be a runtime module name,
`logos_storage_module_*` may be the C ABI symbol family,
and a package catalog may assign a separate deployment identity.
Changing runtime placement, socket naming, C symbol escaping, or package
identity does not change the schema identity.

A runtime, package manager, catalog, or trust profile MAY bind package,
version, artifact, signer, or provider metadata to a schema root elsewhere.
For example, a package catalog may state that package version `1.4.2`
implements a particular schema root.
That binding is outside the structural schema identity algorithm defined here.

## 5. Imported Definitions And Prelude

A Logos schema may reference its local named types and named definitions in the pinned Logos common schema.
A concrete module schema may additionally reference named types in explicitly supplied supporting schemas.
Interface contract and supporting schemas cannot reference supporting schemas.

An imported reference contains one `schema-import` value consisting of the complete referenced schema root and the exact referenced declaration subtree root.
The complete root supplies schema context and provenance.
The subtree root identifies the selected declaration and commits to its qualified name, declaration kind, and body.
No separate import-summary list is included in the canonical schema root.

For a supporting-schema import,
the processor MUST recompute both roots from the explicitly supplied supporting document.
The referenced declaration MUST be a named type.
For a common-schema reference,
both roots MUST match the pinned registry in this section.

An imported reference is a canonical by-reference identity.
It is not an ambient source include, filesystem lookup, package-manager record, or runtime discovery record.
Source include layout, local file paths, package-manager state, and runtime module discovery MUST NOT participate in schema identity.

The normative input set consists of the ordinary RFC 8610 CDDL documents accepted under LOGOS-MODULE-INTERFACE.
CDDL module `include` and `import` directives MUST NOT affect parsing, resolution, or schema identity.
A processor MUST NOT treat a directive encoded as a CDDL comment as authority to search an ambient source directory.

`_implements` entries defined by LOGOS-MODULE-INTERFACE are not imports.
An `_implements` entry is a whole-interface contract reference
that makes the referenced interface surface callable through a concrete module.
Implemented interface references participate in the concrete module's schema root
as exposed-surface metadata.
They do not inline the referenced interface declarations
into the concrete module schema.
They also do not create imported-reference nodes.
An implemented interface reference proves that the concrete module schema root
commits to exposing the referenced interface contract.
It does not copy the referenced interface methods into the concrete module's primary schema tree.
It also does not change the defining schema root for those interface methods.

The Logos prelude and Logos common schema surface are treated differently.
The prelude fixed-width integer aliases normalize to built-in primitive schema
leaves and do not create common-schema references.
The Logos common schema surface contains reusable Logos-defined schema definitions such as `logos.error_code`, `logos.schema_request`, and `logos.schema_response`.
These definitions belong to a well-known common schema namespace.
The well-known common schema namespace for this revision is `logos`.
For the pinned common schema surface, the input rule set for namespace derivation and schema-declaration construction MUST be exactly the pinned common schema document assigned by LOGOS-MODULE-INTERFACE Section 5.
The prelude fixed-width integer aliases MUST NOT participate in namespace derivation or produce schema declarations.
Unqualified common names in source CDDL are interpreted as names in that
namespace when they are represented as qualified schema definition names.
The common schema surface is a pinned Logos schema dependency.
Its canonical schema root and named schema subtree roots are computed from the
common schema definitions in LOGOS-MODULE-INTERFACE Section 5 using this
specification.
When another schema depends on one of those definitions, the Logos canonical
schema model uses the explicit reference form defined in this section.
The imported reference commits to the specific common schema root and named schema subtree root that define the referenced item.
It does not reference an extracted `logos_common.cddl` mirror.
The following registry assigns the common schema root and every named subtree root under `logos.hash-profile.2026-08.choice-index` and `logos.hash-suite.blake3-256`:

| Definition | Kind | Root, hexadecimal |
|------------|------|-------------------|
| Common schema | schema | `7e0236018aed522455dfbdba19f81fd67a050a61f2a05cb8d1027eda35107ca6` |
| `logos.error_code` | type | `f0efecb7f5f270919523d00dd977e5c0ca04b429e022a1a66856353831fd76a7` |
| `logos.error_detail` | type | `a6a0bed0a560ed0499a7e1d4708741e0b6dce32f379cdbbf29d74637cb0ea3ff` |
| `logos.invalid_params_detail` | type | `4a8b55144d4f00f42c19ffd90cb9c4173388c1ec00bafcf71df79b32a14163d9` |
| `logos.invalid_params_path_segment` | type | `6fc94679ad488099793d930fec7eaf2fb200a0e117c85c28188f8f2458b0d451` |
| `logos.invalid_params_reason` | type | `c55a3c96f6306a438e357b35d7cedbeca054ceb68cc1188eb38b036da7ac6816` |
| `logos.schema` | method | `8997083caebf86ede43a744e16ac7018eacc3a51e4e603af4ef0ed8bd14158c3` |
| `logos.schema_commitment` | type | `b9adbab7aea835c64a3b89031c45d7868d21069be0943f0581d527234812d064` |
| `logos.schema_request` | method request | `b6f1788290d01092fba9e956e405ecd6bd5c5584f64ceeab8a60df92a52ae585` |
| `logos.schema_response` | method response | `3fde7207bddb450e0a7583953b7db2cf393382cc971a67ca8394bfa6b1896e18` |

These values are normative.
They are 32-byte BLAKE3 digests and MUST be decoded from hexadecimal before use as roots.
An implementation MUST NOT substitute roots derived from a different extracted mirror.

`logos_common.cddl` may be distributed as an extracted machine-readable mirror of LOGOS-MODULE-INTERFACE Section 5 for source-authoring convenience.
That mirror layout does not make prelude aliases and common schema definitions
the same identity category.
For identity purposes, `uint64` normalizes to a primitive fixed-width unsigned
integer leaf, while `logos.error_code` is a reference to a named definition in the well-known common schema namespace.
The mirror is an authoring and distribution convenience.
The schema root and named subtree root are the identity.

Common-schema references use the common schema namespace and qualified schema definition names.
They do not use runtime module names, C ABI symbol prefixes, socket names,
package names, artifact names, or deployment identities.

## 6. Commitment Model Revision Identifier

The Logos canonical schema model itself has a schema.
The semantic commitment-model revision identifier is therefore part of canonical
schema identity.

This identifier must be explicit because future semantic commitment-model
revisions may add schema constructs, change normalization rules, add import
forms, or define new subschema identity rules.
Without an explicit semantic commitment-model revision identifier, old and new
schema identities could become ambiguous even when the original CDDL text has
not changed.

The semantic commitment-model revision identifier is not a semantic-versioning
number.
It does not encode major, minor, or patch compatibility.
Implementations MUST NOT infer compatibility, ordering, or feature support from
the spelling of the identifier unless a specification or compatibility profile
explicitly defines that meaning.
Compatibility is a verifier-policy question, not a property inferred from a
version-number range.

The semantic commitment-model revision identifier is an ASCII text token with
this syntax:

```abnf
semantic-commitment-model-revision = "logos.commitment-model." date-label
                                    [ "." revision-label ]
date-label = 4DIGIT "-" 2DIGIT
revision-label = 1*( %x61-7A / DIGIT / "-" )
```

The initial identifier defined by this specification is:

```text
logos.commitment-model.2026-08
```

The date label is an assignment label.
It does not imply ordering, recency preference, compatibility, or feature
support.
The optional revision label is for a future specification that needs more than
one assigned semantic commitment model in the same month.
Implementations MUST encode the identifier as UTF-8 text in canonical schema
objects and MUST compare identifiers byte-for-byte.
Unknown identifiers MUST be rejected unless the verifier explicitly supports
the identifier or has an applicable compatibility profile.

The semantic commitment-model revision identifier binds the canonical schema
foundation consumed by the Logos domain interpretation.
The initial semantic commitment-model revision is defined over the `cdCDDLe`
specification referenced by this document.

A future update to `cdCDDLe` that changes the Logos canonical schema model
or the canonical schema bytes consumed by Logos MUST either define a new Logos
semantic commitment-model revision identifier or define an explicit
compatibility profile.

Changing the semantic commitment-model revision identifier is a compatibility
event for schema identity.
A future semantic commitment-model revision must define whether it can verify
old schema roots directly, translate old schema models into a newer model, or
keep old roots in their original domain.

The semantic commitment-model revision identifier is included in schema roots,
schema subtree roots, schema leaf hashes, and schema references.
It is not merely metadata on the whole schema root.
This prevents future commitment-model revisions from accidentally sharing hash
domains with earlier Logos canonical schema objects.

Every hashed schema object also includes an object-kind domain tag.
The object-kind domain tag is an ASCII text token that identifies the kind of
schema object being hashed.
This specification defines these object-kind domain tags:

| Object | Domain tag |
|--------|------------|
| Whole schema root | `logos.schema.root` |
| Schema subtree root | `logos.schema.node` |
| Schema leaf hash | `logos.schema.leaf` |
| Schema reference | `logos.schema.reference` |

The hash input for each hashed schema object MUST commit to both the
object-kind domain tag and the semantic commitment-model revision identifier
before committing to the Logos canonical object payload.
A hash computed for one object kind MUST NOT be accepted as a hash for another
object kind, even if the normalized payloads are otherwise identical.

Schema roots, schema subtree roots, schema leaf hashes, and schema references
from different semantic commitment-model revision identifiers are distinct and
non-equivalent by default.
Apparent source-text or structural similarity across revisions does not make
the resulting roots interchangeable.

Schema references MAY identify schemas or schema subtrees defined under a
different semantic commitment-model revision identifier.
A verifier MUST NOT accept such a reference merely because the referenced hash
matches.
The verifier MUST either support the referenced semantic commitment-model
revision directly or support an explicit compatibility profile that defines how
objects from the referenced revision are verified in relation to objects from
the referring revision.

A compatibility profile is part of the verification policy.
It must name the semantic commitment-model revisions it connects and the exact
verification or translation rule it permits.
If no applicable compatibility profile is available, the verifier MUST keep the
referenced object in its original semantic domain and MUST NOT treat it as an
object in the referring schema's semantic domain.

Compatibility profiles MUST NOT weaken verifier policy.
A verifier or trust profile that requires a specific semantic commitment-model
revision identifier, or a specific set of allowed identifiers, for a schema,
package, method, value proof, or remote-runtime evidence MUST reject a
different identifier unless the policy explicitly allows that identifier or an
explicit compatibility profile for that identifier.
This prevents an attacker from replacing an expected schema commitment with a
commitment from another semantic commitment-model revision whose semantics are
weaker, less precise, or differently normalized.

## 7. Canonical Value Model

CBOR and deterministic CBOR profiles define a data model and canonical byte
encoding.
CDDL defines validation shapes for those data items.
This specification defines an additional normalized Logos value model because
value commitments and verified views need typed semantic structure that
CBOR/CDDL do not define:
schema binding, field and element boundaries, optional-field representation,
selected choice arms, and proof-path labels.

The normalized Logos value model is derived from Logos deterministic CBOR bytes
decoded and validated under a known Logos schema identity.
It is the canonical representation of ordinary module values and payloads
before value hashing and proof construction.
It is not the schema-as-data representation;
the schema-as-data representation is derived from the Logos canonical schema
model defined above.
The Logos canonical schema model is analogous to a type definition.
The normalized Logos value model is analogous to a typed instance of that
definition.

Every normalized Logos value is schema-typed.
A value model instance is derived by decoding Logos deterministic CBOR bytes
under a known schema root and a known schema definition or schema subtree
identity.
For example, a request payload is interpreted under the schema root that
defines the module contract and under the specific method request definition
subtree.
The value model MUST retain that schema binding.
Value commitments and verified views built from the value model MUST commit to
the schema root and to the relevant schema definition or subtree identity.

The value model is semantic, not byte-oriented.
It represents typed values such as maps, fields, lists, tuples, choices, and
scalars.
It is not raw deterministic CBOR bytes, a generated C struct layout, or a
language-specific binding representation.

Map values are schema-defined field sets.
Each field entry is identified by its schema field name.
Deterministic CBOR map order and source declaration order do not define value
identity.
The canonical value model orders map fields by canonical field name.
Required fields MUST be present.
Unknown fields MUST be rejected unless a future schema construct explicitly
defines an extension field.

Optional fields have explicit presence.
If an optional field is present, the normalized value model contains the typed
field value.
If an optional field is absent, the normalized value model contains an explicit
absent marker for that field.
This distinguishes "absent" from "not checked" and supports proofs of
absence.

Defaults are not part of Logos schemas.
The value model does not materialize default values.
A schema author that wants default-like behavior must model it explicitly in
the schema or application logic.

List values are ordered sequences.
Each list element is decoded under the list element schema, and element order
is part of the normalized value.
Tuple values are ordered fixed-position values.
Tuple positions are part of the normalized value even when two positions have
the same type and value.

Choice values include the selected canonical arm index and selected arm schema identity.
The normalized value model MUST NOT represent a choice only as the decoded
payload.
Including the selected arm prevents different schema meanings from collapsing
onto the same value representation.

Scalar values normalize by semantic value and schema type.
Fixed-width integers normalize to mathematical integer values constrained by
their schema alias.
Boolean values normalize to `true` or `false`.
Text strings normalize to valid UTF-8 text and MUST NOT contain U+0000.
Byte strings normalize to exact byte sequences.

Floating-point values are not part of the canonical Logos value model or the
Logos canonical schema model in this revision.
A future deterministic numeric profile may define fixed-point, decimal, or
constrained binary floating-point types, but such a profile is outside this
specification.

This section defines the normalized typed value.
It does not define the concrete Merkle tree layout, scalar embedding, list
chunking, or proof-path encoding.
Those are defined by LOGOS-MODULE-HASH-PROFILE.

## 8. Semantic Value Tree

The commitment model separates three concepts:

- the abstract semantic schema model and its canonical schema representation;
- the semantic value tree;
- the physical hash layout.

The abstract semantic schema model is the Logos canonical schema model defined
in Sections 3 through 6.
Its canonical schema representation is the finite schema-as-data form used to
define schema roots, schema subtree roots, schema leaf hashes, and schema
references.

The semantic value tree is the normalized Logos value model from Section 7
arranged as a typed tree.
It defines what concrete value is being committed and which schema identity
gives that value its meaning.

The physical hash layout defines how the semantic value tree is committed by a
concrete hashing algorithm.
A physical hash layout may use the semantic value tree directly, or it may use
an optimized layout that packs, chunks, balances, or otherwise arranges the
same semantic information differently.
The physical hash layout is not the same concept as the semantic value tree.
Different physical layouts are not assumed to be root-compatible with each
other.

This section defines the semantic value tree.
It does not define the final canonical physical hash layout.
The direct semantic tree is useful as an explanatory and conformance reference:
an implementation can conceptually hash each semantic node and combine child
hashes according to the tree described here.
However, the direct semantic tree hash is not assigned a canonical value-root
profile in this section.
The canonical production layout for this specification is defined by
LOGOS-MODULE-HASH-PROFILE.

A value root is separate from a schema root.
The value root commits to a concrete typed value.
The schema root commits to the schema under which that value is interpreted.
A value commitment MUST bind to:

- the semantic commitment-model revision identifier;
- the schema root;
- the schema definition or schema subtree identity under which the value is
  decoded;
- the semantic value tree for the decoded value.

For a value selected through a named declaration in a supporting schema,
the schema root is that supporting schema's root and the selected schema identity is that declaration's subtree root.
For method request and response values,
the schema root is the method's defining schema root.
For a primary concrete method,
that root is the concrete module schema root.
For an implemented interface method,
that root is the implemented interface schema root.
External attribution evidence may link the value commitment to a concrete
module schema root or to other system records,
but those links are outside the normalized value root.

The same decoded CBOR data under different schema roots or different schema
subtree identities MUST NOT be treated as the same canonical value commitment.

`logos.transport.payload-commitment`, `logos.module_configuration.value_commitment`,
and `logos.capability_authority.audit_value_commitment` are contract-local representations of the same two-root value-commitment record.
Their `schema_subtree_root` and `value_root` fields have the semantics defined here.
The local record names do not define different commitment constructions.

The semantic value tree uses typed structural nodes.
This specification defines the following semantic value node kinds:

| Node kind | Purpose |
|-----------|---------|
| Value root | Binds the whole value to schema identity and the child value node |
| Map | Represents a schema-defined field set |
| Field | Represents one named map field |
| Absent | Represents an absent optional field |
| List | Represents an ordered variable-length sequence |
| List element | Represents one list element at a concrete index |
| Tuple | Represents an ordered fixed-length sequence |
| Tuple element | Represents one tuple element at a fixed position |
| Choice | Represents a selected choice arm and its value |
| Scalar | Represents a typed scalar value |
| Reference value | Represents a value interpreted under a referenced schema definition |

Each semantic value node carries its node kind and the schema identity needed
to interpret that node.
For nodes whose meaning is defined by a schema subtree, the node carries the
relevant schema subtree root.
For nodes whose meaning is defined by a common-schema definition, the node
carries the common schema root and referenced schema subtree root.

Map nodes represent schema-defined field sets.
A map node contains one field node for each field defined by the schema.
Map fields are ordered by canonical field name.
They are not ordered by source declaration order or by the order in which a
deterministic CBOR map happened to encode them.

Required fields MUST be present.
Unknown fields MUST be rejected before value-tree construction.
Optional fields are represented explicitly:
if an optional field is present, its field node contains the typed child value;
if it is absent, its field node contains an absent node.
Absent optional fields MUST NOT be omitted from the semantic value tree.
This supports proofs of absence and distinguishes an absent value from a value
that was merely not disclosed in a verified view.

Field nodes commit to the field name and to the field schema identity.
Two fields with the same value but different field names or different field
schema identities are different semantic nodes.

List nodes represent ordered variable-length sequences.
A list node commits to the list schema identity and to the list length.
Each list element is represented by a list element node.
Each list element node commits to its zero-based element index, the element
schema identity, and the element value.
Element order is part of the semantic value.

Tuple nodes represent ordered fixed-length sequences.
A tuple node commits to the tuple schema identity and to its arity.
Each tuple element is represented by a tuple element node.
Each tuple element node commits to its fixed zero-based position, the position
schema identity, and the element value.
Two tuple positions with identical values and identical element types remain
different semantic nodes because their positions are part of the schema
meaning.

Choice nodes commit to the selected schema arm.
A choice node contains the choice schema identity, selected canonical arm index, selected arm schema identity, and selected value.
The selected arm index and selected arm schema identity MUST be part of the semantic value tree.

Scalar nodes are leaves in the semantic value tree.
A scalar node contains the scalar schema identity, the scalar kind, and the
canonical scalar value.
Values decoded under literal schema nodes are represented as scalar nodes
whose canonical scalar value equals the required literal value.
The scalar kind is the Logos schema type, not merely the CBOR major type.
For example, `uint8` value `5` and `uint64` value `5` are different typed
scalar values.

Raw deterministic CBOR byte slices are not semantic value leaves.
Logos deterministic CBOR is the deterministic transport encoding from which
values are decoded.
It does not define the semantic proof boundaries for Logos value commitments.
Semantic proof boundaries are schema-defined values such as fields, list
elements, tuple elements, selected choice arms, absent optional fields, and
typed scalar values.

A value interpreted through a local named reference is normalized under the referenced local declaration within the same schema root.
The normalized value root or containing structural value node retains the schema identity of the referring location,
and the child value carries the referenced local declaration's schema identity.
A local reference does not add a `reference-value` node.

A value interpreted through an imported reference uses a reference value node.
That node commits to the referring schema location, the complete referenced schema root, the referenced declaration subtree root,
and the value interpreted under that declaration.
This preserves the imported declaration's identity while proving where the reference occurred in the importing schema.

Physical layout optimizations are layered below the semantic value tree.
Packing scalar groups, chunking large lists or byte strings, balancing branch
nodes, using proof-system-specific arities, or precomputing domain-separated
hash states may be useful optimizations.
They do not change the semantic path language:
a verified view still refers to schema-defined paths such as fields, list
indices, tuple positions, and choice arms.
If a later physical layout is not root-compatible with another layout, it MUST
be identified by a distinct hash-layout rule or domain.
No optimized layout may silently replace another layout under the same
canonical root interpretation.

## 9. Canonical Semantic Data Shapes

This section defines the deterministic CBOR data shapes for the semantic
objects defined by this specification.
These shapes are the canonical data inputs consumed by
LOGOS-MODULE-HASH-PROFILE.

The shapes below use deterministic CBOR maps with unsigned integer keys.
Unknown keys are invalid unless a later semantic commitment-model revision
explicitly defines them.
Optional fields MUST be omitted when not applicable.
Arrays whose ordering is semantic MUST preserve that order.
Arrays whose ordering is canonicalized by this specification MUST be encoded in
canonical order before hashing or comparison.

The following common aliases are used in this section:

```cddl
semantic-commitment-model-revision = tstr
schema-namespace = tstr
qualified-name = tstr
field-name = tstr
scalar-kind = tstr
choice-arm-index = uint64
schema-root = bstr
schema-subtree-root = bstr
schema-leaf-hash = bstr
uint64 = uint .size 8
int64 = -9223372036854775808..9223372036854775807
```

The digest lengths of `schema-root`, `schema-subtree-root`, and
`schema-leaf-hash` are determined by the mandatory BLAKE3-256 suite defined by the hash profile.
The semantic shapes defined here do not select that suite.
The `uint64` and `int64` definitions are repeated here for reading
convenience and MUST be identical in meaning to the Logos prelude aliases of
the same names defined by LOGOS-MODULE-INTERFACE.

The Logos prelude integer-alias rule from LOGOS-MODULE-INTERFACE governs Logos schemas.
The integer aliases in this section describe canonical semantic data shapes,
not authored Logos schemas.
Counters, indices, lengths, and offsets in these shapes use `uint64`.
Integer scalar values use `uint64` or `int64` at the CDDL level and are further
constrained by their `scalar-kind`.

### 9.1 Logos Canonical Schema Objects

The Logos canonical schema root object has this shape.
The CDDL label `normalized-schema-root` is the payload label retained by this
revision for the canonical data shape:

```cddl
normalized-schema-root = {
    0: "schema-root",
    1: semantic-commitment-model-revision,
    2: schema-namespace,
    3: [* schema-declaration],
    4: [* schema-root],       ; implemented interface roots
}
```

`schema-declaration` entries are sorted by qualified declaration name.
Implemented-interface roots are sorted by their 32-byte root values and MUST NOT contain duplicates.
Every implemented-interface root MUST resolve to an explicitly supplied interface document.
Two implemented-interface roots whose documents declare the same interface namespace are invalid.
Field `4` MUST be empty for an interface contract, supporting schema, or the pinned common schema surface.

```cddl
schema-import = {
    0: schema-root,
    1: schema-subtree-root,
}

schema-declaration-kind =
    "type" / "method" / "method-request" / "method-response" / "event"

schema-declaration = {
    0: schema-declaration-kind,
    1: qualified-name,
    2: schema-declaration-body,
}

schema-declaration-body = schema-node / method-declaration

method-declaration = {
    0: "method",
    1: qualified-name,       ; request declaration name
    2: qualified-name,       ; response declaration name
}
```

The `0` key in `method-declaration` is local to that nested map shape.
It is not a schema node-kind field.

A Logos canonical schema node has this shape:

```cddl
schema-node =
    primitive-schema /
    literal-schema /
    map-schema /
    list-schema /
    tuple-schema /
    choice-schema /
    reference-schema

primitive-schema = {
    0: "primitive",
    1: scalar-kind,
    ? 2: schema-constraint,
}

literal-schema = {
    0: "literal",
    1: scalar-kind,
    2: scalar-data,
}

schema-constraint = size-constraint

size-constraint = {
    0: "size",
    1: uint64,       ; minimum size
    2: uint64,       ; maximum size
}

map-schema = {
    0: "map",
    1: [* schema-field],
}

schema-field = {
    0: field-name,
    1: bool,          ; true if optional
    2: schema-node,
}

list-schema = {
    0: "list",
    1: schema-node,
}

tuple-schema = {
    0: "tuple",
    1: [* schema-node],
}

choice-schema = {
    0: "choice",
    1: [* schema-node],
}

reference-schema = local-reference-schema / imported-reference-schema

local-reference-schema = {
    0: "local-reference",
    1: qualified-name,       ; referenced local type declaration name
}

imported-reference-schema = {
    0: "imported-reference",
    1: schema-import,
}
```

An `imported-reference-schema` represents an accepted named definition in a supporting schema or the pinned Logos common schema.
Its `schema-import` pair MUST resolve to exactly one declaration of the permitted kind in that schema.
Map fields are sorted by canonical field name.
Choice arms are sorted by ascending lexicographic order over the complete deterministic-CBOR encodings of their canonical arm schema nodes.
Nested schema nodes are canonicalized before the containing choice is ordered, and reference schema nodes remain terminal.
Two arms with identical canonical schema-node encodings make the choice schema invalid.
The zero-based position of an arm in the resulting array is its canonical arm index.
A canonical arm index is meaningful only within its containing choice schema.
Tuple elements preserve source position.
A `size-constraint` is valid only on a `tstr` or `bstr` primitive,
and its minimum MUST NOT exceed its maximum.
A `literal-schema` is valid only for a Boolean, `uint64`, `int64`, or `tstr` literal accepted by Section 3.1.

`scalar-kind` values for this revision are:

```cddl
scalar-kind =
    "bool" /
    "uint8" / "uint16" / "uint32" / "uint64" /
    "int8" / "int16" / "int32" / "int64" /
    "tstr" / "bstr"
```

Floating-point types are intentionally absent from this list.
This revision does not define schema identity or canonical value roots for
floating-point values.

### 9.2 Schema Identity Objects

Schema roots, subtree roots, leaf hashes, and references are hashes over the
Logos canonical schema objects above using the hash input rules from
LOGOS-MODULE-HASH-PROFILE.
The semantic payload shapes are:

```cddl
schema-root-payload = normalized-schema-root

schema-node-payload = {
    0: "schema-node",
    1: semantic-commitment-model-revision,
    2: qualified-name,
    3: schema-declaration-kind,
    4: schema-declaration-body,
}

schema-structural-node-payload = {
    0: "schema-structural-node",
    1: semantic-commitment-model-revision,
    2: schema-declaration-kind,
    3: qualified-name,
    4: schema-node-path,
    5: schema-node,
}

schema-leaf-payload = {
    0: "schema-leaf",
    1: semantic-commitment-model-revision,
    2: schema-declaration-kind,
    3: qualified-name,       ; nearest named declaration
    4: schema-node-path,
    5: schema-node,          ; leaf node
}

schema-reference-payload = schema-import

schema-node-path = [* schema-node-path-segment]

schema-node-path-segment =
    schema-field-segment /
    schema-list-element-segment /
    schema-tuple-position-segment /
    schema-choice-arm-segment

schema-field-segment = {
    0: "field",
    1: field-name,
}

schema-list-element-segment = {
    0: "list-element",
}

schema-tuple-position-segment = {
    0: "tuple-position",
    1: uint64,
}

schema-choice-arm-segment = {
    0: "choice-arm",
    1: choice-arm-index,
}
```

A `schema-leaf-payload` is valid only when field `5` contains a leaf schema
node.
A leaf schema node is a `primitive-schema`, `literal-schema`, or
`reference-schema`.
Map, list, tuple, and choice schema nodes are not leaf schema nodes.
The `schema-node-path` MUST resolve from the nearest named declaration body to
the leaf schema node in field `5`.
The empty path `[]` is valid when the named declaration body is itself a leaf
schema node.
Method declarations do not have schema leaf hashes in this revision because
their bodies are `method-declaration` values, not `schema-node` values.
Field path segments use canonical field names.
Tuple-position path segments use zero-based tuple positions.
Choice-arm path segments use canonical zero-based arm indices.
Reference schema nodes are leaves for this purpose;
schema leaf hashes do not follow references into the referenced definition.

### 9.3 Normalized Value Objects

Event payload values, when committed, are normalized value roots whose schema
subtree identity is the event declaration's schema subtree root.
They use the same value-tree and hashing rules that apply to method request
and response values.

A normalized value object binds a concrete value to the schema identity under
which it was decoded:

```cddl
normalized-value-root = {
    0: "value-root",
    1: semantic-commitment-model-revision,
    2: schema-root,
    3: schema-subtree-root,
    4: value-node,
}

value-node =
    map-value /
    field-value /
    absent-value /
    list-value /
    list-element-value /
    tuple-value /
    tuple-element-value /
    choice-value /
    scalar-value /
    reference-value

map-value = {
    0: "map",
    1: schema-subtree-root,
    2: [* field-value],
}

field-value = {
    0: "field",
    1: field-name,
    2: schema-subtree-root,
    3: value-node,
}

absent-value = {
    0: "absent",
    1: schema-subtree-root,
}

list-value = {
    0: "list",
    1: schema-subtree-root,
    2: uint64,               ; list length
    3: [* list-element-value],
}

list-element-value = {
    0: "list-element",
    1: uint64,               ; zero-based element index
    2: schema-subtree-root,
    3: value-node,
}

tuple-value = {
    0: "tuple",
    1: schema-subtree-root,
    2: uint64,               ; tuple arity
    3: [* tuple-element-value],
}

tuple-element-value = {
    0: "tuple-element",
    1: uint64,               ; zero-based tuple position
    2: schema-subtree-root,
    3: value-node,
}

choice-value = {
    0: "choice",
    1: schema-subtree-root,
    2: choice-arm-index,     ; selected canonical arm index
    3: schema-subtree-root,  ; selected arm schema identity
    4: value-node,
}

scalar-value = {
    0: "scalar",
    1: schema-subtree-root,
    2: scalar-kind,
    3: scalar-data,
}

reference-value = {
    0: "reference-value",
    1: schema-subtree-root,  ; referring schema location
    2: schema-root,          ; complete referenced schema root
    3: schema-subtree-root,  ; referenced declaration subtree root
    4: value-node,
}

scalar-data = bool / uint64 / int64 / tstr / bstr
```

The `scalar-data` type MUST match `scalar-kind`.
When `scalar-kind` is a `uintN` alias, the value MUST be encoded as a
non-negative integer.
When `scalar-kind` is an `intN` alias, the value MAY be encoded as a
non-negative or negative integer, but the deterministic-CBOR shortest-encoding
rule still
applies.
The fixed-width range of the named alias is the additional constraint on the
value beyond the CDDL `uint64` or `int64` surface type.
Unsigned scalar kinds encode as non-negative CBOR integers within the fixed
width range named by the kind.
Signed scalar kinds encode as CBOR integers within the fixed width range named
by the kind.
Text strings encode as valid UTF-8 text strings and MUST NOT contain U+0000.
Byte strings encode as exact byte strings.

Map field values are sorted by canonical field name.
List element values are sorted by zero-based element index and MUST cover
exactly the range from `0` to `length - 1`.
Tuple element values are sorted by zero-based tuple position and MUST cover
exactly the range from `0` to `arity - 1`.

### 9.4 Semantic Path Objects

Semantic paths are arrays of structured path segments:

```cddl
semantic-path = [* path-segment]

path-segment =
    field-segment /
    list-index-segment /
    tuple-position-segment /
    choice-arm-segment /
    bstr-range-segment /
    tstr-utf8-range-segment

field-segment = {
    0: "field",
    1: field-name,
}

list-index-segment = {
    0: "list-index",
    1: uint64,
}

tuple-position-segment = {
    0: "tuple-position",
    1: uint64,
}

choice-arm-segment = {
    0: "choice-arm",
    1: choice-arm-index,
}

bstr-range-segment = {
    0: "bstr-range",
    1: uint64,  ; start byte offset
    2: uint64,  ; byte length
}

tstr-utf8-range-segment = {
    0: "tstr-utf8-range",
    1: uint64,  ; start UTF-8 byte offset
    2: uint64,  ; byte length
}
```

An empty `semantic-path` identifies the whole normalized value.

## 10. Conformance

A conforming implementation of this specification MUST construct normalized
schema objects, normalized value objects, and semantic paths according to the
canonical data shapes in Section 9.
It MUST reject malformed semantic objects whose shape, ordering, references,
paths, or normalized value semantics violate this specification.

Construction vectors in this specification define semantic conformance
requirements for the inputs they cover.
A conforming implementation MUST produce the same canonical semantic objects
for each valid construction vector in this specification.
It MUST reject malformed semantic objects according to the rules in Sections 8 through 10.
Conformance material for implemented interface methods MUST identify the
implemented interface schema root as the method's defining schema root.
Conformance material for a concrete module MAY separately show that the
concrete module schema root commits to implementing that interface root.
That separate provider-contract evidence does not change the schema root used
for method request or response value commitments.

Hash-input bytes, digest values, roots, and hash-suite-specific vectors are
defined by LOGOS-MODULE-HASH-PROFILE, not by this specification.

## 11. Comparison And Non-Goals

This specification defines the semantic commitment model that a hash profile
commits to.
It deliberately does not choose the only possible physical Merkle layout.
External systems may use different Merkle trees, light-client protocols,
certificate chains, trusted-execution attestations, or consensus roots.
Interoperability with those systems belongs to trust/authentication profiles,
not to the semantic commitment model.

Non-goals:

- hash function selection;
- byte-level hash input framing;
- physical packing or chunking layout;
- proof wire format;
- trusted computation protocols;
- challenge games or fraud proofs;
- ZK proving circuits;
- on-chain contract formats;
- remote runtime enrollment;
- plugin loader or package-manager control APIs;
- package trust policy;
- authorization policy;
- runtime call policy.

## Appendix A. Construction Vector

This appendix gives a construction vector for the Logos canonical schema
model.
A conforming implementation MUST produce the canonical schema object shown
below from the input Logos module schema after applying LOGOS-MODULE-INTERFACE,
`cdCDDLe`, and this specification.
It is not a hash-suite conformance vector and does not include deterministic
CBOR bytes or hash outputs.

Input Logos module schema:

```cddl
_module = "storage_module"

storage.cid = tstr .size (1..128)
storage.blob_hash = bstr .size 32
storage.lookup_key = storage.cid / storage.blob_hash

storage.exists_request = {
    key: storage.lookup_key,
}

storage.exists_response = {
    exists: bool,
}

storage.changed_event = {
    cid: storage.cid,
    digest: storage.blob_hash,
}
```

Construction:

- `_module` is runtime metadata and is not a schema declaration.
- The primary schema namespace is `storage`.
- `storage.cid`, `storage.blob_hash`, and `storage.lookup_key` are local named
  type declarations.
- `storage.exists_request` is a method request declaration.
- `storage.exists_response` is a method response declaration.
- `storage.exists` is the method declaration paired from the request and
  response declarations.
- `storage.changed_event` is an event declaration.
- References to local named types are local reference nodes and are not
  inlined.
- After canonical ordering, the `storage.lookup_key` arm referencing `storage.cid` has index 0 and the arm referencing `storage.blob_hash` has index 1.

The resulting `normalized-schema-root` object is shown in CBOR diagnostic
notation:

```cbor-diag
{
  0: "schema-root",
  1: "logos.commitment-model.2026-08",
  2: "storage",
  3: [
    {
      0: "type",
      1: "storage.blob_hash",
      2: {
        0: "primitive",
        1: "bstr",
        2: {
          0: "size",
          1: 32,
          2: 32,
        },
      },
    },
    {
      0: "event",
      1: "storage.changed_event",
      2: {
        0: "map",
        1: [
          {
            0: "cid",
            1: false,
            2: {
              0: "local-reference",
              1: "storage.cid",
            },
          },
          {
            0: "digest",
            1: false,
            2: {
              0: "local-reference",
              1: "storage.blob_hash",
            },
          },
        ],
      },
    },
    {
      0: "type",
      1: "storage.cid",
      2: {
        0: "primitive",
        1: "tstr",
        2: {
          0: "size",
          1: 1,
          2: 128,
        },
      },
    },
    {
      0: "method",
      1: "storage.exists",
      2: {
        0: "method",
        1: "storage.exists_request",
        2: "storage.exists_response",
      },
    },
    {
      0: "method-request",
      1: "storage.exists_request",
      2: {
        0: "map",
        1: [
          {
            0: "key",
            1: false,
            2: {
              0: "local-reference",
              1: "storage.lookup_key",
            },
          },
        ],
      },
    },
    {
      0: "method-response",
      1: "storage.exists_response",
      2: {
        0: "map",
        1: [
          {
            0: "exists",
            1: false,
            2: {
              0: "primitive",
              1: "bool",
            },
          },
        ],
      },
    },
    {
      0: "type",
      1: "storage.lookup_key",
      2: {
        0: "choice",
        1: [
          {
            0: "local-reference",
            1: "storage.cid",
          },
          {
            0: "local-reference",
            1: "storage.blob_hash",
          },
        ],
      },
    },
  ],
  4: [],
}
```

The declaration array is sorted by qualified declaration name:
`storage.blob_hash`, `storage.changed_event`, `storage.cid`,
`storage.exists`, `storage.exists_request`, `storage.exists_response`, and
`storage.lookup_key`.
The map fields are sorted by canonical field name.
The choice arms are sorted by the deterministic-CBOR encodings of their canonical arm schema nodes.

## Appendix B. Schema And Value Tree Vector

This appendix gives a small semantic vector that shows the relationship between
a module schema, the schema tree, one concrete value, and semantic paths.
A conforming implementation MUST produce the canonical schema object,
normalized value object, and semantic paths shown below from the input module
schema and concrete value.
The object instances shown below use the canonical data shapes defined in
Section 9:
schema objects from Section 9.1, schema identity and path payloads from
Section 9.2, value objects from Section 9.3, and semantic paths from
Section 9.4.
It does not define hash-input bytes or digest values.

Input Logos module schema:

```cddl
_module = "demo_module"

demo.ping_request = {
    nonce: uint64,
}

demo.ping_response = {
    ok: bool,
}
```

The schema tree is represented by the resulting Section 9.1
`normalized-schema-root` object, shown here in CBOR diagnostic notation:

```cbor-diag
{
  0: "schema-root",
  1: "logos.commitment-model.2026-08",
  2: "demo",
  3: [
    {
      0: "method",
      1: "demo.ping",
      2: {
        0: "method",
        1: "demo.ping_request",
        2: "demo.ping_response",
      },
    },
    {
      0: "method-request",
      1: "demo.ping_request",
      2: {
        0: "map",
        1: [
          {
            0: "nonce",
            1: false,
            2: {
              0: "primitive",
              1: "uint64",
            },
          },
        ],
      },
    },
    {
      0: "method-response",
      1: "demo.ping_response",
      2: {
        0: "map",
        1: [
          {
            0: "ok",
            1: false,
            2: {
              0: "primitive",
              1: "bool",
            },
          },
        ],
      },
    },
  ],
  4: [],
}
```

This schema tree has one whole-schema root and three named schema subtree
roots:
`demo.ping`, `demo.ping_request`, and `demo.ping_response`.
The `ok` field's boolean schema node is a schema leaf under
`demo.ping_response`.
Its schema-node path from `demo.ping_response` is:

```cbor-diag
[
  {
    0: "field",
    1: "ok",
  },
]
```

One concrete response value is:

```cbor-diag
{
  "ok": true,
}
```

Decoded under the `demo.ping_response` schema subtree, that value produces the
value tree.
The value tree is represented by this Section 9.3 `normalized-value-root`
object.
The placeholder byte strings stand for schema identities computed by
LOGOS-MODULE-HASH-PROFILE:

```cbor-diag
{
  0: "value-root",
  1: "logos.commitment-model.2026-08",
  2: h'...schema-root...',
  3: h'...demo.ping_response-subtree-root...',
  4: {
    0: "map",
    1: h'...demo.ping_response-subtree-root...',
    2: [
      {
        0: "field",
        1: "ok",
        2: h'...ok-field-schema-identity...',
        3: {
          0: "scalar",
          1: h'...ok-field-schema-identity...',
          2: "bool",
          3: true,
        },
      },
    ],
  },
}
```

The empty semantic path identifies the whole response value:

```cbor-diag
[]
```

The semantic path to the `ok` field value is:

```cbor-diag
[
  {
    0: "field",
    1: "ok",
  },
]
```

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- cdCDDLe -- Deterministic CDDL schema-as-data representation.
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-HASH-PROFILE -- Physical hash profile and verified-view proof
  specification.

### Informative

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
