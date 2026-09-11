# cdCDDLe

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | cdCDDLe                                                       |
| Slug         | 300                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines `cdCDDLe`, a deterministic schema-as-data representation for a defined subset of CDDL.

`cdCDDLe` takes parsed and resolved CDDL within that subset as input and produces a canonical CDDL schema model.
When bytes are needed, that canonical schema model is encoded as deterministic CBOR
using the RFC 8949-based rules defined by this specification.

## 1. Introduction

CDDL defines a notation for describing CBOR and JSON data structures.
It does not define a canonical schema-as-data representation for CDDL schemas
themselves.

For systems that need stable schema processing, raw CDDL source text is not a suitable canonical input.
Whitespace, comments, and harmless formatting differences should not change the resulting schema model.
At the same time, a deterministic CDDL layer must not erase supported CDDL semantics
that a consuming domain may treat as meaningful.

`cdCDDLe` fills this gap for the CDDL construct subset defined in Section 5.1.
It defines a deterministic canonical CDDL schema model and a deterministic CBOR encoding of that model.
The canonical model is the primary object.
The CBOR byte string is only the deterministic encoding of that object.

`cdCDDLe` is intentionally conservative.
It removes presentation information and normalizes only equivalences that are unambiguous within the supported subset.
It preserves the supported information that consuming specifications may use for identity, binding,
diagnostics, or domain interpretation
unless this specification explicitly classifies that information as non-semantic presentation.

The supported subset covers the CDDL constructs consumed when constructing the Logos canonical schema model
and processing Logos configuration schemas.
Acceptance by `cdCDDLe` establishes canonical representability only.
It does not establish that an input is a valid Logos concrete module schema, interface contract schema,
configuration schema, or other application contract.
A future revision may extend the canonical model to cover all CDDL constructs.

## 2. Scope

This specification defines:

- the boundary between CDDL parsing and resolution and `cdCDDLe` canonicalization;
- the supported CDDL construct subset;
- the canonical CDDL schema-as-data model for that subset;
- canonicalization rules for CDDL presentation and equivalent syntax;
- the deterministic CBOR encoding of the canonical model;
- conformance requirements for encoders, decoders, and checkers.

This specification does not define:

- application contract validity;
- application-specific identity rules;
- language binding rules;
- protocol message envelopes;
- application-specific roots or hash-input records;
- package, runtime, security, or trust policy.

Those topics may consume `cdCDDLe`, but they are not part of `cdCDDLe`.
In particular, the Logos canonical schema model is a separate domain interpretation
of the canonical CDDL schema model defined here.

## 3. Normative Dependencies

`cdCDDLe` depends on the following standards:

- RFC 8610, Concise Data Definition Language (CDDL);
- RFC 8949, Concise Binary Object Representation (CBOR),
  including the core deterministic encoding requirements in Section 4.2.1.

RFC 8949 supplies the stable CBOR data model and core deterministic encoding requirements.
This specification states every additional encoding restriction directly,
so the canonical bytes do not depend on another encoding profile.

## 4. Terminology

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are to be
interpreted as described in BCP 14.

**CDDL source text** is the textual CDDL input before parsing.

**Resolved CDDL rule graph** is the syntax and rule model produced by a conforming CDDL parser and resolver.

**Canonical CDDL schema model** is the abstract schema-as-data object produced
by `cdCDDLe`.

**Canonical schema bytes** are the deterministic CBOR bytes produced by
encoding the canonical CDDL schema model.

**Bound rule name** means a CDDL rule name that binds a type definition and can be referenced from other CDDL rules.

**Presentation information** means information such as whitespace, comments,
line breaks, indentation, and source formatting.

**Domain interpretation** means a consuming specification's interpretation of a
generic CDDL schema as something more specific, such as a protocol message
set, credential format, file format, or application contract.

## 5. Processing Model

A conforming `cdCDDLe` implementation has four conceptual stages:

```text
source text
  -> parse
      parsed syntax
  -> resolve
      resolved CDDL rule graph
  -> canonicalize
      canonical CDDL schema model
  -> encode
      RFC 8949-based deterministic CBOR bytes
```

The parse and resolve stages MUST follow RFC 8610 semantics for the supported subset.
`cdCDDLe` starts at the resolved CDDL rule graph.

A `cdCDDLe` implementation MAY expose parsing and resolution as part of the
same tool.
If it does, parse or resolution errors MUST be reported before canonicalization.

Before canonicalization, an implementation MUST verify that the resolved CDDL rule graph
uses only the constructs in Section 5.1.
It MUST reject any other construct rather than omit it, approximate it,
or assign it an implementation-local representation.

The canonicalization stage MUST NOT depend on:

- source file byte offsets;
- comments;
- indentation;
- source line wrapping;
- non-semantic whitespace;
- implementation-specific parser object identity;
- host-language map iteration order.

The encoding stage MUST encode the canonical model as deterministic CBOR using
the rules in Section 9.

### 5.1 Supported CDDL Construct Subset

The supported input subset consists of:

- non-generic type rules defined with `=`;
- references to named type rules, including recursive and mutually recursive references;
- the primitive types `uint`, `bool`, `tstr`, and `bstr`;
- non-negative integer, negative integer, Boolean, text-string, and byte-string literals;
- parentheses around supported type expressions;
- fixed-length arrays and homogeneous variable-length arrays written as `[* T]`;
- maps with a finite set of bareword keys written with the colon member form;
- required and optional map members;
- ordered type choices written with `/`;
- inclusive integer ranges written with `..`; and
- the `.size` control with a non-negative integer or inclusive non-negative integer range as its controller.

The following constructs are unsupported:

- group rules, generic rules or applications, and rule extensions;
- group choices, sockets, unwrapped groups, and enumerations;
- tags and general `#` forms;
- explicit cuts, `=>` member keys, and non-bareword map keys;
- occurrences other than the supported `?` map-member and `*` array-member forms;
- exclusive ranges and control operators other than `.size`; and
- any other CDDL construct not listed as supported above.

The colon member form has the cut semantics defined by RFC 8610.
Because every supported keyed member uses that form,
cut behavior is invariant within this model and is not represented by a separate node.

RFC 8610 designates the first rule as the root of a CDDL specification.
The canonical model defined here instead represents a set of named rules
and does not retain that implicit root selection.
A consumer that requires a root rule MUST identify it separately by bound rule name
or construct a domain-specific root after canonicalization.

## 6. Canonical Model Requirements

The canonical CDDL schema model MUST be a data model, not a byte string.

The model MUST be able to represent:

- non-generic type rules and named references;
- the primitive types and literal values listed in Section 5.1;
- fixed-length arrays, homogeneous variable-length arrays, and finite maps;
- required and optional members;
- ordered type choices;
- inclusive integer ranges; and
- `.size` control applications.

The model MUST preserve bound rule names.
A consuming domain may treat those names as semantic.
For example, a generic CDDL validator may treat two rule definitions as
structurally equivalent, while a domain interpretation may distinguish them
because their bound names become application-specific identifiers.

The model MUST preserve all semantics of the supported constructs except RFC 8610 implicit root selection,
which is outside the model as specified in Section 5.1.

The model MUST preserve references as references unless an explicit
canonicalization rule in this specification requires expansion.
`cdCDDLe` MUST NOT silently replace all named references with their expanded
structure.

The model MUST distinguish at least these concepts:

- a rule definition;
- a reference to a rule;
- a primitive type;
- a literal value;
- a map entry;
- an array member;
- a member occurrence;
- a choice alternative;
- an inclusive range;
- a `.size` control application.

Every resolved rule graph within the supported subset MUST have a corresponding canonical model representation.
A canonical model document MUST contain at least one rule.
Every bound rule name and reference name MUST be a syntactically valid RFC 8610 CDDL identifier.
Bound rule names MUST be unique within one canonical document and MUST NOT equal a primitive name listed in Section 5.1.
Every reference MUST have been resolved successfully before canonicalization.

## 7. Canonicalization Rules

`cdCDDLe` MUST remove presentation information.
Whitespace, comments, source indentation, and line wrapping MUST NOT affect the
canonical model.

`cdCDDLe` MUST normalize syntactic forms that are unambiguously equivalent in
CDDL.
Examples include numeric spelling differences where the parsed numeric value is
the same, and string escaping differences where the parsed text or byte value
is the same.

`cdCDDLe` MUST NOT normalize by arbitrary structural equivalence.
Two named rules with the same structure MUST remain distinguishable in the canonical model
because the bound names remain present.
An implementation MAY expose structural equivalence as a derived view,
but that view MUST NOT replace the name-preserving canonical model.

`cdCDDLe` MUST NOT derive a universal schema identifier from canonical bytes as
part of this specification.
Applications MAY hash canonical schema bytes for their own purposes, but the
meaning of that hash belongs to the consuming application profile.

`cdCDDLe` MUST NOT decide that two schemas are the same merely because they
accept the same set of data items.
General CDDL semantic equivalence is outside the scope of this specification.

### 7.1 Rule Ordering

Top-level rule order is not an identity input.
After parsing and resolution, top-level rules MUST be ordered by their
canonical rule key before encoding.

The canonical rule key is:

- the bound rule name, ordered by Unicode scalar value sequence.

Two top-level rules with the same canonical rule key are invalid.

Nested order is preserved unless this specification explicitly defines a
canonical sort for the construct.
In particular, tuple positions, array members, and choice alternatives preserve their resolved order.
Map members MUST be sorted by their text key in Unicode scalar value order.
Two map members with the same text key are invalid.

### 7.2 Choice Ordering

Choice alternative order is preserved.
`cdCDDLe` MUST NOT reorder choice alternatives by structural identity, encoded
bytes, diagnostic order, or implementation-specific matching behavior.

If an order can affect diagnostics, matching behavior, or a domain
interpretation, the order should remain represented.

### 7.3 Reference Expansion

`cdCDDLe` MUST NOT fully inline all references by default.
Inlining erases the difference between a bound name and an anonymous structure.

The name-preserving canonical model is finite even when the resolved CDDL rule
graph contains recursive or cyclic references.
References are represented as reference nodes.
They are not replaced by the referenced rule body during canonicalization.

The resolved rule/reference relation MAY form a graph.
That graph MAY contain cycles if the underlying CDDL schema and resolver accept
them.
Such cycles do not create cycles in the canonical schema-as-data item because
the canonical item stores references by name.

Any diagnostic or derived expanded view that follows references recursively
MUST detect cycles and mark or reject the expansion according to that derived
view's own rules.
Such an expanded view is not the canonical model defined by this
specification.

`cdCDDLe` defines only the name-preserving canonical model.
A derived structural-equivalence view MUST be separately identified
and MUST NOT replace the name-preserving canonical model defined here.

### 7.4 Construct Mapping

A canonicalizer MUST map every supported source construct as follows:

- a type rule maps to a type-rule node containing its bound name and canonicalized body;
- a named reference maps to a type-reference node, while a primitive keyword maps to a primitive node;
- a non-negative integer, negative integer, Boolean, text-string,
  or byte-string value maps to the corresponding literal node;
- parentheses around a supported type expression are removed;
- an array or map maps to an array or map node whose group contains its canonicalized members;
- a bareword colon key maps to a member-key node containing a text-string literal with the parsed key text;
- an absent occurrence maps to no occurrence field,
  `?` maps to an occurrence with bounds zero and one,
  and `*` maps to an occurrence with lower bound zero and upper bound `"unbounded"`;
- a type choice maps to one choice node containing its alternatives in resolved order;
- an inclusive integer range maps to a range node whose inclusive fields are both `true`; and
- a `.size` application maps to a `.size` control-application node.

After parentheses are removed,
canonicalization MUST recursively flatten any type choice that is an alternative of another type choice into the enclosing choice node while preserving resolved alternative order.
A choice node MUST contain at least two alternatives.
Canonicalization MUST reject an inclusive integer range whose lower bound exceeds its upper bound,
including a range used as a `.size` controller.
An inclusive range with equal bounds MUST canonicalize to its single literal value rather than a range node.
A `.size` range controller with equal bounds MUST canonicalize to one non-negative integer literal.

## 8. Schema-As-Data Representation

The canonical model MUST have a deterministic schema-as-data representation.

This representation is a compact CBOR data model with integer keys and small
integer node-kind identifiers.

Every canonical model node is a CBOR map.
Key `0` is the required node-kind identifier.
Other keys are defined per node kind.
Unknown keys and unknown node-kind identifiers are invalid.

The node-kind identifiers are:

| Identifier | Node kind |
|------------|-----------|
| `0` | document |
| `1` | type rule |
| `3` | type reference |
| `5` | primitive |
| `6` | literal |
| `7` | array |
| `8` | map |
| `9` | group |
| `10` | member |
| `11` | occurrence |
| `12` | choice |
| `13` | range |
| `14` | `.size` control application |
| `21` | member key |

Node-kind identifiers not listed in this table are unassigned and MUST be rejected.

The canonical document node has this shape:

```cddl
cdcddle-document = {
    0: 0,
    1: [+ cdcddle-type-rule],
    2: "cdcddle",
}
```

`cdcddle` is the canonical-model identifier assigned by this specification.
It is part of every canonical document node and is compared byte-for-byte.
An implementation MUST reject an unknown revision unless it implements a specification that defines it.

The rule array is ordered as defined in Section 7.1.

Rules have the following shape:

```cddl
cdcddle-type-rule = {
    0: 1,
    1: rule-name,
    3: cdcddle-type,
}

rule-name = tstr
```

Rule names MUST satisfy the RFC 8610 identifier syntax and MUST NOT be empty.

Type references have this shape:

```cddl
type-reference = {
    0: 3,
    1: rule-name,
}
```

Primitive and literal nodes have these shapes:

```cddl
primitive = {
    0: 5,
    1: primitive-name,
}

uint-literal = {
    0: 6,
    1: "uint",
    2: uint,
}

nint-literal = {
    0: 6,
    1: "nint",
    2: nint,
}

bool-literal = {
    0: 6,
    1: "bool",
    2: bool,
}

tstr-literal = {
    0: 6,
    1: "tstr",
    2: tstr,
}

bstr-literal = {
    0: 6,
    1: "bstr",
    2: bstr,
}

primitive-name = "uint" / "bool" / "tstr" / "bstr"
integer-literal = uint-literal / nint-literal
literal = integer-literal / bool-literal / tstr-literal / bstr-literal
```

Literal values are parsed values, not source spelling.
For example, numeric base notation and string escape spelling are not
preserved.

Arrays, maps, and groups have these shapes:

```cddl
array-type = {
    0: 7,
    1: cdcddle-group,
}

map-type = {
    0: 8,
    1: cdcddle-group,
}

group = {
    0: 9,
    1: [* cdcddle-member],
}
```

The group node is an internal member container for an array or map and does not represent a source group rule.
An array group's member order is preserved.
A map group's members are sorted as defined in Section 7.1.

Members and occurrences have these shapes:

```cddl
member = {
    0: 10,
    ? 1: member-key,
    2: cdcddle-type,
    ? 3: occurrence,
}

member-key = {
    0: 21,
    1: tstr-literal,
}

occurrence = {
    0: 11,
    1: 0,
    2: 1 / "unbounded",
}
```

If an occurrence marker is absent, the occurrence is exactly one.
The value `1` for key `2` represents the optional `?` form, and `"unbounded"` represents the variable-length `*` form.
A map member MUST contain a member key, and an array member MUST NOT contain one.
An optional map member MUST use the `?` occurrence, and no other occurrence is valid on a map member.
An array group MUST either contain only members without occurrences, defining a fixed-length array,
or contain exactly one member with the `*` occurrence, defining a homogeneous variable-length array.
No other occurrence is valid on an array member.

Choice, range, and `.size` control nodes have these shapes:

```cddl
choice = {
    0: 12,
    1: [cdcddle-type, cdcddle-type, * cdcddle-type],
}

range = {
    0: 13,
    1: integer-literal,
    2: integer-literal,
    3: true,
    4: true,
}

size-control-application = {
    0: 14,
    1: "size",
    2: primitive,
    3: uint-literal / range,
}
```

Choice alternative order is preserved.
The lower bound of a range node MUST be less than its upper bound.
The target of a `.size` control MUST be `uint`, `tstr`, or `bstr`.
When the `.size` controller is a range, both bounds MUST be non-negative.

The type and group nonterminals are:

```cddl
cdcddle-type =
    type-reference /
    primitive /
    literal /
    array-type /
    map-type /
    choice /
    range /
    size-control-application

cdcddle-group = group

cdcddle-member = member

cdcddle-rule = cdcddle-type-rule
```

The representation is defined by this specification.
An implementation MUST NOT infer alternative canonicalization semantics from
local tool versions, publication dates, file names, or implementation-specific
metadata.

Any update that changes canonicalization semantics, node-kind identifiers, required fields, or byte encoding
in a way that can change canonical schema bytes is a change to this specification.
Such a change requires a new canonical-model identifier and new conformance vectors.

## 9. Deterministic CBOR Encoding

When the canonical CDDL schema model is encoded as bytes, it MUST be encoded
as deterministic CBOR.

The encoding MUST follow the core deterministic encoding requirements in RFC 8949 Section 4.2.1.

The encoding MUST use shortest-form integer encodings.
The encoding MUST use definite-length strings, arrays, and maps.
The encoding MUST NOT use indefinite-length items.
The encoding MUST sort map keys by bytewise lexicographic comparison
of the complete deterministic CBOR encoding of each map key.
Sorting by key length before key byte content MUST NOT be used.

The canonical schema bytes are not themselves an application root.
They are an input that a consuming profile may hash, bind, transmit, or store.

## 10. Decoding And Checking

A `cdCDDLe` decoder MUST reject CBOR bytes that are not valid deterministic
CBOR under the RFC 8949-based rules in Section 9.

A `cdCDDLe` decoder MUST reject unknown node kinds, unknown fields, absent or invalid required fields,
forbidden optional fields, duplicate map keys, an empty document rule array, an empty choice,
invalid rule or reference names, duplicate bound rule names, a literal whose value does not match its literal kind,
an invalid range or occurrence, an unsupported primitive or control operator,
and any other violation of Section 8.

The decoder MUST verify that top-level rules and map members occur in canonical order.
It MUST NOT accept and silently reorder a non-canonical model.

A `cdCDDLe` checker MUST verify that a byte string is the unique deterministic encoding
of a valid canonical CDDL schema model.
Re-encoding the decoded model and comparing the result byte-for-byte is one conforming check.

## 11. Conformance

A conforming `cdCDDLe` canonicalizer MUST:

- accept every resolved CDDL rule graph within the supported subset;
- reject unsupported CDDL constructs explicitly;
- remove presentation information;
- preserve bound rule names;
- preserve named references;
- preserve the supported semantics identified in Section 6;
- produce the same canonical model for inputs that differ only in presentation;
- produce deterministic CBOR bytes for the canonical model using Section 9.

A conforming `cdCDDLe` encoder MUST:

- encode only valid canonical CDDL schema models;
- use the RFC 8949-based deterministic CBOR rules required by this
  specification;
- produce a single byte string for a given canonical model.

A conforming `cdCDDLe` decoder/checker MUST:

- reject non-deterministic CBOR encodings;
- reject malformed canonical model objects;
- reject unsupported node kinds or fields;
- expose the canonical model without assigning application-specific identity.

## 12. Conformance Vectors

Machine-readable conformance vectors for this specification MUST use this structure:

```cddl
cdcddle-vector = {
    "name": tstr,
    ? "input-cddl": tstr,
    ? "input-cbor-hex": tstr,
    "expect": "valid" / "invalid",
    ? "canonical-diagnostic": tstr,
    ? "canonical-cbor-hex": tstr,
    ? "error-class": tstr,
    ? "notes": tstr,
}
```

Exactly one of `input-cddl` and `input-cbor-hex` MUST be present.
`input-cddl` is source text supplied to a canonicalizer.
`input-cbor-hex` is an encoded canonical-model candidate supplied to a decoder or checker.
`canonical-diagnostic` is a deterministic diagnostic notation for the
canonical CDDL schema model.
`canonical-cbor-hex` is the hexadecimal encoding of the RFC 8949-based
deterministic CBOR bytes.
`error-class` identifies the expected rejection category without prescribing diagnostic wording.

A valid normative vector MUST include `canonical-cbor-hex`
containing the lowercase hexadecimal encoding of the complete deterministic-CBOR `cdCDDLe` document node.
It MAY also include diagnostic notation for review.
The hexadecimal bytes are the implementation-comparison value when a rendering and the bytes disagree.

An invalid normative vector MUST include `error-class`
and MUST NOT include `canonical-diagnostic` or `canonical-cbor-hex`.
No canonical model or canonical bytes exist for invalid input.

A conformance vector set claiming complete coverage MUST include at least:

- presentation equivalence for whitespace, comments, numeric spelling, and
  string escaping;
- top-level rule-order equivalence;
- preservation of distinct bound rule names with identical structure;
- preservation of choice alternative order;
- preservation of named references rather than full inlining;
- rejection of every unsupported construct category listed in Section 5.1;
- rejection of empty documents and empty choices;
- rejection of duplicate rule names, invalid reference names, invalid literal-kind and value pairs,
  invalid ranges, and invalid occurrences;
- rejection of unknown node kinds and fields;
- rejection of non-canonical rule and map-member ordering;
- rejection of non-deterministic CBOR encodings of the canonical model.

## 13. Extension Boundaries

This revision is complete for the CDDL construct subset in Section 5.1.
An unsupported construct is an error and MUST NOT be assigned an implementation-local canonical form.

A future revision may extend the canonical model to cover all of CDDL,
including constructs and registered control operators outside the current subset.
Such an extension requires a new canonical-model identifier and new conformance vectors.
It MUST NOT reinterpret a document whose canonical-model identifier is `cdcddle`.

## Appendix A. Storage-Like cdCDDLe Vector (Normative)

This appendix gives a normative `cdCDDLe` vector for the Storage-like schema
used by LOGOS-MODULE-COMMITMENT-MODEL Appendix A.
It shows the generic `cdCDDLe` canonical CDDL schema model before Logos domain
interpretation.
It does not synthesize Logos method declarations, choose a schema namespace, or
assign Logos schema roots.

The vector name is `storage-like`, and its expected result is `valid`.

Input CDDL:

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

Construction notes:

- `_module` is an ordinary CDDL type rule at this generic layer.
- Top-level rules are sorted by canonical rule key.
- Map members are sorted by their text keys.
- Local references are preserved as reference nodes and are not inlined.
- The choice alternative order in `storage.lookup_key` is preserved.
- The `.size` controls are represented as `.size` control-application nodes.

The canonical diagnostic notation for the `cdCDDLe` document node is:

```cbor-diag
{
  0: 0,
  1: [
    {
      0: 1,
      1: "_module",
      3: {
        0: 6,
        1: "tstr",
        2: "storage_module",
      },
    },
    {
      0: 1,
      1: "storage.blob_hash",
      3: {
        0: 14,
        1: "size",
        2: {
          0: 5,
          1: "bstr",
        },
        3: {
          0: 6,
          1: "uint",
          2: 32,
        },
      },
    },
    {
      0: 1,
      1: "storage.changed_event",
      3: {
        0: 8,
        1: {
          0: 9,
          1: [
            {
              0: 10,
              1: {
                0: 21,
                1: {
                  0: 6,
                  1: "tstr",
                  2: "cid",
                },
              },
              2: {
                0: 3,
                1: "storage.cid",
              },
            },
            {
              0: 10,
              1: {
                0: 21,
                1: {
                  0: 6,
                  1: "tstr",
                  2: "digest",
                },
              },
              2: {
                0: 3,
                1: "storage.blob_hash",
              },
            },
          ],
        },
      },
    },
    {
      0: 1,
      1: "storage.cid",
      3: {
        0: 14,
        1: "size",
        2: {
          0: 5,
          1: "tstr",
        },
        3: {
          0: 13,
          1: {
            0: 6,
            1: "uint",
            2: 1,
          },
          2: {
            0: 6,
            1: "uint",
            2: 128,
          },
          3: true,
          4: true,
        },
      },
    },
    {
      0: 1,
      1: "storage.exists_request",
      3: {
        0: 8,
        1: {
          0: 9,
          1: [
            {
              0: 10,
              1: {
                0: 21,
                1: {
                  0: 6,
                  1: "tstr",
                  2: "key",
                },
              },
              2: {
                0: 3,
                1: "storage.lookup_key",
              },
            },
          ],
        },
      },
    },
    {
      0: 1,
      1: "storage.exists_response",
      3: {
        0: 8,
        1: {
          0: 9,
          1: [
            {
              0: 10,
              1: {
                0: 21,
                1: {
                  0: 6,
                  1: "tstr",
                  2: "exists",
                },
              },
              2: {
                0: 5,
                1: "bool",
              },
            },
          ],
        },
      },
    },
    {
      0: 1,
      1: "storage.lookup_key",
      3: {
        0: 12,
        1: [
          {
            0: 3,
            1: "storage.cid",
          },
          {
            0: 3,
            1: "storage.blob_hash",
          },
        ],
      },
    },
  ],
  2: "cdcddle",
}
```

The deterministic CBOR byte length is `522` bytes.
The deterministic CBOR bytes, in hexadecimal, are:

```text
a300000187a3000101675f6d6f64756c6503a30006016474737472026e73746f
726167655f6d6f64756c65a30001017173746f726167652e626c6f625f686173
6803a4000e016473697a6502a2000501646273747203a30006016475696e7402
1820a30001017573746f726167652e6368616e6765645f6576656e7403a20008
01a200090182a3000a01a2001501a30006016474737472026363696402a20003
016b73746f726167652e636964a3000a01a2001501a300060164747374720266
64696765737402a20003017173746f726167652e626c6f625f68617368a30001
016b73746f726167652e63696403a4000e016473697a6502a200050164747374
7203a5000d01a30006016475696e74020102a30006016475696e7402188003f5
04f5a30001017673746f726167652e6578697374735f7265717565737403a200
0801a200090181a3000a01a2001501a3000601647473747202636b657902a200
03017273746f726167652e6c6f6f6b75705f6b6579a30001017773746f726167
652e6578697374735f726573706f6e736503a2000801a200090181a3000a01a2
001501a30006016474737472026665786973747302a200050164626f6f6ca300
01017273746f726167652e6c6f6f6b75705f6b657903a2000c0182a20003016b
73746f726167652e636964a20003017173746f726167652e626c6f625f686173
68026763646364646c65
```

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
