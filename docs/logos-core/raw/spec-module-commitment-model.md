# LOGOS-MODULE-COMMITMENT-MODEL

| Field        | Value                           |
|--------------|---------------------------------|
| Name         | Logos Module Commitment Model   |
| Slug         | 302                             |
| Status       | raw                             |
| Category     | Standards Track                 |
| Editor       | ksr                             |
| Contributors | atd, Jarrad                     |

## Abstract

This specification defines the semantic commitment model for Logos schemas and
Logos values.
It defines how module schemas receive stable semantic identities, how concrete
typed values are normalized before commitment, and how semantic paths for
partial verified views are identified.

This specification defines what is being committed.
It does not define the canonical production hash function, physical hash
layout, packing, chunking, proof encoding, or byte-level value-root profile.
Those are defined by LOGOS-MODULE-HASH-PROFILE.

The commitment model is a third view of the same module contract defined by
LOGOS-MODULE-INTERFACE:

- the **interface view** maps CDDL schemas to C ABI surfaces;
- the **transport view** maps schema-defined values to Logos deterministic
  CBOR bytes;
- the **commitment view** maps schemas and typed values to semantic identities,
  value trees, and verified-view paths.

This specification does NOT define remote runtime management, plugin loading,
package trust, trusted computation protocols, challenge games, proving
circuits, or on-chain contracts.
Those topics may consume the commitment model defined here, but they are
specified elsewhere.

## 1. Introduction

Logos module schemas already define the shape of module methods, responses,
events, and common types.
The Interface specification defines how those schemas map to a C ABI and to
Logos deterministic CBOR transport values.

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
same CDDL-authored schema at a particular processing layer.
A parsed/resolved CDDL model is a parser-level representation.
A `cdCDDLe` canonical schema model is a generic canonical CDDL representation.
A Logos canonical schema model is the Logos-specific semantic representation
used for schema identity and commitment.
These are not separate schemas.
They are different models of the same authored schema at different layers,
similar to a compiler representing the same source program first as syntax and
then as semantic forms with resolved names and types.

CDDL, `cdCDDLe`, and Logos deterministic CBOR remain the input and interchange
surfaces:

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
  imports, common-schema references, and other identity-relevant
  module-contract semantics.
- Logos deterministic CBOR data is decoded under a known schema into the
  normalized Logos value model.
- Generated C, or other binding representations consume these
  models but do not define them.

The processing chain is:

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
| `cdCDDLe` canonical schema bytes | CDE-based deterministic CBOR bytes | `cdCDDLe` | Deterministic encoding of the generic model; not a Logos schema root by itself |
| Logos domain interpretation | interpretation rules | LOGOS-MODULE-COMMITMENT-MODEL | Maps generic CDDL schema data into Logos module-contract meaning |
| Logos canonical schema model | abstract semantic schema object | LOGOS-MODULE-COMMITMENT-MODEL | Input to Logos schema roots and schema subtree roots |
| Logos module contract | abstract contract object | LOGOS-MODULE-INTERFACE plus LOGOS-MODULE-COMMITMENT-MODEL | Interface, transport, and commitment views of the same method/event/type contract |
| Logos deterministic CBOR payload bytes | deterministic CBOR bytes | LOGOS-MODULE-INTERFACE | Transport/interchange encoding of concrete module values |
| normalized Logos value model | semantic typed value object | LOGOS-MODULE-COMMITMENT-MODEL | Input to value commitments and verified-view paths |
| hash-input records | deterministic CBOR records | LOGOS-MODULE-HASH-PROFILE | Exact bytes hashed by the selected hash suite |
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
"Schema-as-data representation" names the requirement that Logos module
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
leaf hashes, or schema-node paths by recursively inlining local, imported, or
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
- choice arms are ordered by Logos canonical arm discriminator;
- imports and references are ordered by canonical reference identity.

Only inherently positional constructs preserve order.
Tuple elements and fixed-length array positions are ordered by position.
Variable-length lists have one element-type child in the schema model;
the order of concrete list values is a value-model concern.

Ambiguous choices whose arms cannot be distinguished by the Logos decoding
rules are invalid.
Source declaration order MUST NOT be used to disambiguate choices.
Section 3.1 defines choice-arm selection predicates and canonical choice-arm
discriminators.

The Logos prelude and the Logos common schema surface are conceptually
distinct.
Prelude fixed-width integer aliases such as `uint64` normalize directly to
built-in fixed-width primitive schema leaves.
Reusable Logos-defined common types and well-known method surfaces are normal
schema definitions in a well-known common schema namespace and are referenced
explicitly when used.

### 3.1 Logos Schema-Model Construction

This section defines the construction bridge from a valid Logos module schema,
as defined by LOGOS-MODULE-INTERFACE, into the Logos canonical schema model.
The rules here are normative for this revision.
A future revision may move these rules into a shared module-contract model
specification.
Implementations MUST use the rules in this specification for this revision.

The input to construction is the name-preserving `cdCDDLe` canonical schema
model for one valid Logos module schema.
The output is one Logos canonical schema root object with one primary schema
namespace.
The schema namespace is the qualified-name prefix used by the module's own
method, event, and type declarations in LOGOS-MODULE-INTERFACE Section 1.4.

Construction proceeds as follows:

1. Identify the primary schema namespace.
   Ignore the metadata declarations `_module` and `_version` for schema-model
   construction.
   They are compatibility and runtime metadata, not schema declarations.
   The primary schema namespace is the common prefix before the first `.`
   in local qualified declarations that are not metadata declarations and not
   imported or common-schema declarations.
   Exactly one primary schema namespace MUST be present in this revision.
   All local method, event, request, response, and named-type declarations
   MUST use that namespace.
   A local non-metadata declaration without a qualified name in the primary
   namespace is invalid.
   A reference to a definition outside that namespace is external and MUST be
   represented as an import or common-schema reference.
2. Classify local declarations by name:
   declarations ending in `_request` are method request declarations;
   declarations ending in `_response` are method response declarations;
   declarations ending in `_event` are event declarations;
   remaining local named declarations in the primary schema namespace are
   named type declarations.
   The metadata declarations `_module` and `_version` are not emitted as
   `schema-declaration` entries.
3. Pair each request declaration with the response declaration that has the
   same qualified base name.
   The qualified base name is produced by stripping the `_request` or
   `_response` suffix from a declaration in the primary schema namespace.
   For example, `storage.exists_request` and `storage.exists_response` produce
   the method declaration `storage.exists`.
   A request without a matching response, or a response without a matching
   request, is invalid.
4. Emit one `schema-declaration` for each local named type, method, method
   request, method response, and event.
   Method declaration bodies use `method-declaration`.
   Type, request, response, and event declaration bodies use `schema-node`.
5. Translate declaration bodies into `schema-node` values using the rules
   below.
6. Collect external and common-schema references into `schema-import` entries.
   Imports are canonical references and MUST include the referenced schema root
   and named schema subtree root when a named definition is referenced.
7. Sort imports, declarations, map fields, and choice arms according to
   Section 9.1 before hashing or comparison.

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

Primitive schema forms translate as follows:

- `bool`, `tstr`, `bstr`, and the Logos prelude fixed-width integer
  aliases translate to `primitive-schema`.
- A prelude integer alias translates to the corresponding scalar kind and does
  not create an import.
- Literal scalar values translate to `literal-schema`.
- `tstr .size (min..max)` translates to a `primitive-schema` with a
  `size-constraint`.
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
- a reference to an external or common-schema definition translates to an
  imported `reference-schema` and adds the corresponding `schema-import` entry.

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

Choice arms MUST be distinguishable by deterministic selection predicates.
For a decoded value, exactly one arm predicate MUST match.
If zero arms or more than one arm predicate match, the value is invalid for
that choice schema.
A schema containing a choice whose arm predicates cannot be proven mutually
exclusive by these rules is invalid.
Source declaration order MUST NOT participate in arm selection.

The supported selection predicates are:

- `major-set`:
  a finite set of CBOR major types accepted by the arm;
- `literal`:
  one exact scalar literal value;
- `map-field-literal`:
  a required map field name and exact scalar literal value.

The canonical predicate for an arm is selected as follows:

1. A literal schema node uses a `literal` predicate.
2. A map schema node with one or more required literal fields uses a
   `map-field-literal` predicate.
   If more than one required literal field is present, the canonical predicate
   uses the first field by canonical field-name order whose predicate makes the
   surrounding choice valid.
   If no such field exists, the choice schema is invalid.
3. Other schema nodes use a `major-set` predicate when a finite major-type set
   can be computed.

A `major-set` predicate is available when an arm's accepted CBOR major types
can be computed as a finite set from its schema node.
Primitive, list, tuple, map, literal, and choice schema nodes have finite
major-type sets.
Local references are resolved by following the referenced local named type
declaration.
Imported and common-schema references use the selection predicate metadata
published for the referenced schema subtree.
Implementations MUST compute referenced predicates with cycle detection.
A local reference cycle that cannot be reduced to a finite selection predicate
makes any choice arm depending on that cycle invalid.

A `literal` predicate is available for a literal schema node.
Two literal predicates are disjoint when their canonical scalar values differ.

A `map-field-literal` predicate is available for a map arm when the arm has a
required field whose schema is a literal schema node.
Two `map-field-literal` predicates over the same field name are disjoint when
their canonical scalar values differ.
For example, these arms are disjoint:

```cddl
entry =
  { kind: "file", path: tstr } /
  { kind: "dir", path: tstr, entries: [* tstr] }
```

The canonical choice-arm discriminator identifies the predicate used for arm
selection:

- `major-set.` followed by ascending decimal CBOR major-type numbers separated
  by `+`;
- `literal.` followed by the deterministic diagnostic form of the canonical
  scalar literal;
- `map-field-literal.` followed by the deterministic diagnostic form of the
  field name, `.`, and the deterministic diagnostic form of the canonical
  scalar literal.

The discriminator string is a canonical label, not a free-form diagnostic
message.
Implementations MUST generate it from the selected predicate components using
the rules above and MUST compare it byte-for-byte.

Choice arms are sorted by canonical choice-arm discriminator.
If two arms have the same discriminator, or if their selection predicates
overlap, the choice schema is invalid.
The discriminator is a decoding, ordering, and path-label field.
The full choice arm identity is the canonical `choice-arm` object, including
both the discriminator and the arm schema node.

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
- the identities of referenced common or external schema definitions.

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

ABI entrypoints that dispatch to schema-defined methods, including
`logos_<module>_dispatch()`, do not have method identities in this commitment
model.
Commitments, verified views, audit material, authorization material, and
conformance vectors identify the target schema method and the corresponding
request or response value, not the dispatch entrypoint used to invoke it.

Schema identity uses schema namespaces and qualified schema definition names,
not runtime module names, socket names, C ABI symbol prefixes, or package and
deployment identities.
A schema namespace names an interface contract.
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

`_version` and `_version()` remain compatibility and release-management
metadata.
They are useful for human release management, package compatibility, migration
policy, and diagnostics, but they are not canonical schema identity input.
Two schemas with the same `_version()` string can have different schema
identities.
Two schemas with different `_version()` strings can have the same schema
identity if their Logos canonical schema model is identical.

A runtime, package manager, catalog, or trust profile MAY bind package,
version, artifact, signer, or provider metadata to a schema root elsewhere.
For example, a package catalog may state that package version `1.4.2`
implements a particular schema root.
That binding is outside the structural schema identity algorithm defined here.

Interface versioning is expected to use the schema identity model.
The version-relevant object is the Merkle tree over the Logos canonical schema
model and its reusable definitions, not the raw CDDL source text.

## 5. Imports And Common Prelude

Schemas MUST declare their external schema dependencies explicitly.
A common schema or common module may exist in the Logos environment, but using
one of its definitions in another module schema requires an explicit schema
reference.

Implicit availability is not enough for canonical identity.
Imports are explicit Logos canonical references.
They are not ambient source includes, filesystem lookups, package-manager
state, or runtime discovery records.
Source include layout, local file paths, package-manager state, and runtime
module discovery MUST NOT participate in import identity.

Imports are by reference.
An importing schema commits to referenced schema and schema subtree
identities.
It does not embed external definitions by value into its own schema root.
This revision defines only by-reference imports.
By-value expansion is not a canonical import form.

A Logos canonical reference to a named external definition contains:

- the semantic commitment-model revision identifier;
- the referenced schema namespace;
- the referenced schema root;
- the referenced qualified definition name;
- the referenced definition kind;
- the referenced schema subtree root.

A reference to an entire external schema MAY omit the named-definition fields
and commit only to the semantic commitment-model revision identifier, the
referenced schema namespace, and the referenced schema root.

The referenced schema root gives whole-schema context and provenance.
The referenced schema subtree root identifies the exact named definition being
used.
The referenced qualified definition name and definition kind make the
reference explicit and human-checkable.
They also prevent a verifier from accepting a subtree root as the wrong
semantic category.
Together they support partial verification:
a verifier can check a referenced definition and an inclusion proof against
the referenced schema root without requiring the full referenced schema in
every local check.

Conforming tools MAY provide a fully expanded diagnostic view that recursively
resolves references and displays imported definitions inline.
That expanded view is for inspection and debugging.
It is not the canonical identity input unless a later specification defines a
separate by-value import form.

The Logos prelude and Logos common schema surface are treated differently.
The prelude fixed-width integer aliases normalize to built-in primitive schema
leaves and do not create external references.
The Logos common schema surface contains reusable Logos-defined schema
definitions such as `logos_result`, `logos.schema_request`,
and `logos.schema_response`.
These definitions belong to a well-known common schema namespace.
The well-known common schema namespace for this revision is `logos`.
Unqualified common names in source CDDL are interpreted as names in that
namespace when they are represented as qualified schema definition names.
The common schema surface is a pinned Logos schema dependency.
Its canonical schema root and named schema subtree roots are computed from the
common schema definitions in LOGOS-MODULE-INTERFACE Section 5 using this
specification.
When another schema depends on one of those definitions, the Logos canonical
schema model uses the explicit reference form defined in this section.
It commits to the specific common schema root and named schema subtree root
that define the imported item.
It does not reference whatever local copy of `logos_common.cddl` happens to be
available.
Conformance profiles and vector sets for this revision MUST publish the
canonical common schema root and the named subtree roots for the common
definitions they use.
Until those roots are published, an implementation can construct local common
schema references but cannot claim cross-implementation conformance for schema
roots that depend on common-schema definitions.

The physical file `logos_common.cddl` may continue to hold both prelude aliases
and common schema definitions for source-authoring convenience.
That file layout does not make prelude aliases and common schema definitions
the same identity category.
For identity purposes, `uint64` normalizes to a primitive fixed-width unsigned
integer leaf, while `logos_result` is a reference to a named definition in the
well-known common schema namespace.
The file is an authoring and distribution convenience.
The schema root and named subtree root are the identity.

Import references use schema namespaces and qualified schema definition names.
They do not use runtime module names, C ABI symbol prefixes, socket names,
package names, artifact names, or deployment identities.

## 6. Commitment Model Versioning

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
logos.commitment-model.2026-06
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

Defaults are not part of Logos module schemas.
The value model does not materialize default values.
A schema author that wants default-like behavior must model it explicitly in
the module contract or application logic.

List values are ordered sequences.
Each list element is decoded under the list element schema, and element order
is part of the normalized value.
Tuple values are ordered fixed-position values.
Tuple positions are part of the normalized value even when two positions have
the same type and value.

Choice values include the selected schema arm discriminator and selected arm
schema identity.
The normalized value model MUST NOT represent a choice only as the decoded
payload.
Including the selected arm prevents different schema meanings from collapsing
onto the same value representation.

Scalar values normalize by semantic value and schema type.
Fixed-width integers normalize to mathematical integer values constrained by
their schema alias.
Boolean values normalize to `true` or `false`.
Text strings normalize to valid UTF-8 text.
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

The same decoded CBOR data under different schema roots or different schema
subtree identities MUST NOT be treated as the same canonical value commitment.

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
For nodes whose meaning is defined by an imported or common definition, the
node carries the referenced schema root and referenced schema subtree root.

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
A choice node contains the choice schema identity, the selected arm
discriminator, the selected arm schema identity, and the selected value.
The selected arm discriminator and selected arm schema identity MUST be part of
the semantic value tree.

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

Values interpreted under imported or common definitions use reference value
nodes.
A reference value node commits to the referring schema location, the referenced
schema root, the referenced schema subtree root, and the value interpreted
under that referenced definition.
This preserves stable identity for common values while still proving where the
reference occurred in the importing schema.

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
choice-arm-discriminator = tstr
schema-root = bstr
schema-subtree-root = bstr
schema-leaf-hash = bstr
uint64 = uint .size 8
int64 = -9223372036854775808..9223372036854775807
```

The digest lengths of `schema-root`, `schema-subtree-root`, and
`schema-leaf-hash` are determined by the hash suite selected by the hash
profile.
The semantic shapes defined here do not select that suite.
The `uint64` and `int64` definitions are repeated here for reading
convenience and MUST be identical in meaning to the Logos prelude aliases of
the same names defined by LOGOS-MODULE-INTERFACE.

The Logos prelude integer-alias rule from LOGOS-MODULE-INTERFACE governs
module schemas.
The integer aliases in this section describe canonical semantic data shapes,
not module schemas.
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
    3: [* schema-import],
    4: [* schema-declaration],
}
```

`schema-import` entries are sorted by referenced namespace, referenced schema
root, qualified definition name when present, and definition kind when present.
`schema-declaration` entries are sorted by qualified declaration name.

```cddl
schema-import = {
    0: "import",
    1: semantic-commitment-model-revision,
    2: schema-namespace,
    3: schema-root,
    ? 4: qualified-name,
    ? 5: schema-declaration-kind,
    ? 6: schema-subtree-root,
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
    1: [* choice-arm],
}

choice-arm = {
    0: choice-arm-discriminator,
    1: schema-node,
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

Map fields are sorted by canonical field name.
Choice arms are sorted by Logos canonical arm discriminator.
Tuple elements preserve source position.

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
    1: choice-arm-discriminator,
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
Choice-arm path segments use the canonical choice-arm discriminator.
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
    2: choice-arm-discriminator,  ; selected arm discriminator
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
    2: schema-root,          ; referenced schema root
    3: schema-subtree-root,  ; referenced schema subtree root
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
Text strings encode as valid UTF-8 text strings.
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
    1: choice-arm-discriminator,
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
for each valid construction vector and MUST reject every malformed semantic
object listed by a vector set.

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
_version = [1, 0]

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

- `_module` and `_version` are metadata and are not schema declarations.
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
- The choice arms in `storage.lookup_key` use discriminators
  `major-set.2` and `major-set.3`.

The resulting `normalized-schema-root` object is shown in CBOR diagnostic
notation:

```cbor-diag
{
  0: "schema-root",
  1: "logos.commitment-model.2026-06",
  2: "storage",
  3: [],
  4: [
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
            0: "major-set.2",
            1: {
              0: "local-reference",
              1: "storage.blob_hash",
            },
          },
          {
            0: "major-set.3",
            1: {
              0: "local-reference",
              1: "storage.cid",
            },
          },
        ],
      },
    },
  ],
}
```

The declaration array is sorted by qualified declaration name:
`storage.blob_hash`, `storage.changed_event`, `storage.cid`,
`storage.exists`, `storage.exists_request`, `storage.exists_response`, and
`storage.lookup_key`.
The map fields are sorted by canonical field name.
The choice arms are sorted by canonical choice-arm discriminator.

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
_version = [1, 0]

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
  1: "logos.commitment-model.2026-06",
  2: "demo",
  3: [],
  4: [
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
  1: "logos.commitment-model.2026-06",
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
