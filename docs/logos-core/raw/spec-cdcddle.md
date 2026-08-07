# cdCDDLe

| Field        | Value           |
|--------------|-----------------|
| Name         | cdCDDLe         |
| Slug         | 300             |
| Status       | raw             |
| Category     | Standards Track |
| Editor       | ksr             |
| Contributors | atd, Jarrad     |

## Abstract

This specification defines `cdCDDLe`, a deterministic schema-as-data
representation for CDDL.

`cdCDDLe` takes parsed and resolved CDDL as input and produces a canonical CDDL
schema model.
When bytes are needed, that canonical schema model is encoded as deterministic
CBOR using RFC 8949 deterministic encoding and CDE-style rules.

## 1. Introduction

CDDL defines a notation for describing CBOR and JSON data structures.
It does not define a canonical schema-as-data representation for CDDL schemas
themselves.

For systems that need stable schema identity, raw CDDL source text is not a
suitable identity input.
Whitespace, comments, and harmless formatting differences should not change a
schema identity.
At the same time, a generic deterministic CDDL layer must not erase information
that a consuming domain may treat as meaningful.

`cdCDDLe` fills this gap.
It defines a deterministic canonical CDDL schema model and a deterministic CBOR
encoding of that model.
The canonical model is the primary object.
The CBOR byte string is only the deterministic encoding of that object.

`cdCDDLe` is intentionally conservative.
It removes presentation information and normalizes only equivalences that are
unambiguous at the CDDL schema layer.
It preserves information that consuming specifications may reasonably use for
identity, binding, diagnostics, or domain interpretation unless this
specification explicitly classifies that information as non-semantic
presentation.

## 2. Scope

This specification defines:

- the boundary between CDDL parsing/resolution and `cdCDDLe`
  canonicalization;
- the canonical CDDL schema-as-data model;
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

## 3. Normative Dependencies

`cdCDDLe` depends on the following standards or drafts:

- RFC 8610, Concise Data Definition Language (CDDL);
- RFC 9165, Additional Control Operators for the Concise Data Definition
  Language (CDDL);
- RFC 8949, Concise Binary Object Representation (CBOR), including the core
  deterministic encoding requirements in Section 4.2.1;
- IETF CBOR Common Deterministic Encoding (CDE), draft-ietf-cbor-cde, or its
  successor RFC if one is published.

The CDE dependency is a byte-encoding dependency.
CDE supplies the common deterministic CBOR encoding discipline for the
canonical schema-as-data item.
It does not define CDDL schema equivalence.
It does not decide which CDDL names are meaningful to a consuming domain.

## 4. Terminology

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are to be
interpreted as described in BCP 14.

**CDDL source text** is the textual CDDL input before parsing.

**Parsed CDDL model** is the syntax and rule model produced by a conforming
CDDL parser and resolver.

**Canonical CDDL schema model** is the abstract schema-as-data object produced
by `cdCDDLe`.

**Canonical schema bytes** are the deterministic CBOR bytes produced by
encoding the canonical CDDL schema model.

**Bound rule name** means a CDDL rule name that binds a type or group
definition and can be referenced from other CDDL rules.

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
      CDE-based deterministic CBOR bytes
```

The parse and resolve stages MUST follow CDDL semantics.
`cdCDDLe` starts at the resolved CDDL rule graph.

A `cdCDDLe` implementation MAY expose parsing and resolution as part of the
same tool.
If it does, parse or resolution errors MUST be reported before canonicalization.

The required CDDL language baseline is RFC 8610.
Control operators from RFC 9165 MUST be represented when supported by the
parser/resolver.
Other registered or future CDDL control operators MUST be represented as
extension control applications if their target and controller syntax can be
parsed and if the implementation can preserve their operator names and
operands without approximation.
If an implementation cannot preserve an operator exactly, it MUST reject the
schema.

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

## 6. Canonical Model Requirements

The canonical CDDL schema model MUST be a data model, not a byte string.

The model MUST be able to represent:

- type rules;
- group rules;
- generic rule parameters and applications;
- rule references;
- primitive CDDL types;
- arrays, maps, groups, choices, occurrences, and ranges;
- CDDL control operators;
- literal values;
- tags;
- sockets and cuts if they are present in the supported CDDL revision;
- extension points introduced by later CDDL revisions.

The model MUST preserve bound rule names.
A consuming domain may treat those names as semantic.
For example, a generic CDDL validator may treat two rule definitions as
structurally equivalent, while a domain interpretation may distinguish them
because their bound names become application-specific identifiers.

The model MUST preserve information that a consuming specification may
reasonably use for identity, binding, diagnostics, or domain interpretation
unless this specification explicitly classifies that information as
non-semantic presentation.

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
- a group occurrence;
- a choice alternative;
- a control operator application.

The model SHOULD be closed under CDDL parsing:
any valid CDDL construct in the supported CDDL revision should have a
corresponding canonical model representation.
If an implementation does not support a CDDL revision or extension, it MUST
reject schemas using unsupported constructs rather than approximate them.

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
Two named rules with the same structure MUST remain distinguishable in the
canonical model because the bound names remain present.
Structural equivalence MAY be exposed as an optional derived view if a future
revision or extension defines one, but such a view MUST NOT replace the
name-preserving canonical model.

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

- rule kind;
- bound rule name;
- generic parameter name sequence.

Rule kind order is:

1. type rule;
2. group rule.

Within the same rule kind, bound rule names are ordered by Unicode scalar
value sequence.
Within the same bound rule name, a non-generic rule sorts before a generic
rule.
Generic parameter names are compared lexicographically by Unicode scalar value
sequence.

If two top-level rules have the same canonical rule key after resolution, the
schema is invalid unless the CDDL resolver has combined them into a single
resolved rule according to CDDL rule-extension semantics.

Nested order is preserved unless this specification explicitly defines a
canonical sort for the construct.
In particular, tuple positions, array members, group entries, choice
alternatives, generic parameter lists, and generic argument lists preserve
their resolved order.

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
A future extension MAY define a derived structural-equivalence view for
validation or deduplication.
Such a view MUST be separately identified and MUST NOT replace the
name-preserving canonical model defined here.

## 8. Schema-As-Data Representation

The canonical model MUST have a deterministic schema-as-data representation.

This representation is a compact CBOR data model with integer keys and small
integer node-kind identifiers.

Every canonical model node is a CBOR map.
Key `0` is the required node-kind identifier.
Other keys are defined per node kind.
Unknown keys are invalid unless a future extension explicitly defines them.
Required extension nodes MUST be rejected by implementations that do not
support the extension.
Ignorable extension nodes MAY be preserved by implementations that do not
understand the extension, but they MUST NOT affect the interpretation of the
base node that carries them.

The node-kind identifiers are:

| Identifier | Node kind |
|------------|-----------|
| `0` | document |
| `1` | type rule |
| `2` | group rule |
| `3` | type reference |
| `4` | group reference |
| `5` | primitive |
| `6` | literal |
| `7` | array |
| `8` | map |
| `9` | group |
| `10` | member |
| `11` | occurrence |
| `12` | choice |
| `13` | range |
| `14` | control application |
| `15` | tag |
| `16` | generic parameter |
| `17` | generic application |
| `18` | socket |
| `19` | cut |
| `20` | extension |
| `21` | member key |

The canonical document node has this shape:

```cddl
cdcddle-document = {
    0: 0,
    1: [* cdcddle-rule],
}
```

The rule array is ordered as defined in Section 7.1.

Rules have these shapes:

```cddl
cdcddle-type-rule = {
    0: 1,
    1: rule-name,
    ? 2: [* generic-parameter],
    3: cdcddle-type,
}

cdcddle-group-rule = {
    0: 2,
    1: rule-name,
    ? 2: [* generic-parameter],
    3: cdcddle-group,
}

rule-name = tstr
```

The generic parameter array preserves parameter order.

Type and group references have these shapes:

```cddl
type-reference = {
    0: 3,
    1: rule-name,
    ? 2: [* cdcddle-type],
}

group-reference = {
    0: 4,
    1: rule-name,
    ? 2: [* cdcddle-type],
}
```

Primitive and literal nodes have these shapes:

```cddl
primitive = {
    0: 5,
    1: primitive-name,
}

literal = {
    0: 6,
    1: literal-kind,
    2: literal-value,
}

primitive-name = tstr
literal-kind = "uint" / "nint" / "int" / "float" / "bool" /
               "nil" / "undefined" / "tstr" / "bstr"
literal-value = any
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

Group member order is preserved.

Members and occurrences have these shapes:

```cddl
member = {
    0: 10,
    ? 1: member-key,
    2: cdcddle-type / cdcddle-group,
    ? 3: occurrence,
}

member-key = {
    0: 21,
    1: cdcddle-type / literal,
}

occurrence = {
    0: 11,
    1: occurrence-min,
    ? 2: occurrence-max,
}

occurrence-min = uint
occurrence-max = uint / "unbounded"
```

If an occurrence marker is absent, the occurrence is exactly one.

Choice, range, control, and tag nodes have these shapes:

```cddl
choice = {
    0: 12,
    1: [* cdcddle-type],
}

range = {
    0: 13,
    1: range-lower,
    2: range-upper,
    3: bool,          ; true if lower bound is inclusive
    4: bool,          ; true if upper bound is inclusive
}

control-application = {
    0: 14,
    1: control-operator-name,
    2: cdcddle-type,
    3: cdcddle-type,
}

tag = {
    0: 15,
    1: uint,
    2: cdcddle-type,
}

control-operator-name = tstr
range-lower = literal
range-upper = literal
```

Choice alternative order is preserved.
Control operator names do not include the leading dot.
For example, `.size` is represented with control operator name `"size"`.

Generic parameters and generic applications have these shapes:

```cddl
generic-parameter = {
    0: 16,
    1: rule-name,
}

generic-application = {
    0: 17,
    1: cdcddle-type / cdcddle-group,
    2: [* cdcddle-type],
}
```

The generic argument array preserves argument order.

Socket, cut, and extension nodes have these shapes:

```cddl
socket = {
    0: 18,
    1: socket-name,
}

cut = {
    0: 19,
}

extension-node = {
    0: 20,
    1: extension-name,
    2: bool,          ; true if ignorable
    ? 3: any,
}

socket-name = tstr
extension-name = tstr
```

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
    control-application /
    tag /
    generic-application /
    socket /
    extension-node

cdcddle-group =
    group /
    group-reference /
    generic-application /
    extension-node

cdcddle-member = member

cdcddle-rule = cdcddle-type-rule / cdcddle-group-rule
```

The representation is defined by this specification.
An implementation MUST NOT infer alternative canonicalization semantics from
local tool versions, publication dates, file names, or implementation-specific
metadata.

Any update that changes canonicalization semantics, node-kind identifiers,
required fields, or byte encoding in a way that can change canonical schema
bytes is a change to this specification.
Such a change requires a revised specification or an explicitly named
extension.

## 9. Deterministic CBOR Encoding

When the canonical CDDL schema model is encoded as bytes, it MUST be encoded
as deterministic CBOR.

The encoding MUST follow RFC 8949 core deterministic encoding requirements.
The encoding MUST follow IETF CDE rules, draft-ietf-cbor-cde, or the successor
RFC if one is published.

The encoding MUST use shortest-form integer encodings.
The encoding MUST use definite-length strings, arrays, and maps.
The encoding MUST NOT use indefinite-length items.
The encoding MUST sort map keys according to the CDE deterministic map-order
rule.
For this specification, that means bytewise lexicographic comparison of the
complete deterministic CBOR encoding of each map key.
Sorting by key length before key byte content MUST NOT be used.

The canonical schema bytes are not themselves an application root.
They are an input that a consuming profile may hash, bind, transmit, or store.

## 10. Decoding And Checking

A `cdCDDLe` decoder MUST reject CBOR bytes that are not valid deterministic
CBOR under the CDE/RFC 8949 rule set used by this specification.

A `cdCDDLe` decoder MUST reject unknown required node kinds, invalid required
fields, duplicate map keys, malformed references, and unsupported required
extensions.

A `cdCDDLe` decoder MAY preserve unknown extension nodes only if the extension
node is explicitly marked ignorable by the specification or extension that
introduced it.

A `cdCDDLe` checker MUST be able to verify that a byte string is the
deterministic encoding of a valid canonical CDDL schema model.

## 11. Conformance

A conforming `cdCDDLe` canonicalizer MUST:

- accept resolved CDDL input for the supported CDDL revision;
- reject unsupported CDDL constructs explicitly;
- remove presentation information;
- preserve bound rule names;
- preserve named references unless a future rule explicitly defines a safe
  derived expansion view;
- preserve information that a consuming specification may reasonably use for
  identity, binding, diagnostics, or domain interpretation unless this
  specification explicitly classifies it as non-semantic presentation;
- produce the same canonical model for inputs that differ only in presentation;
- produce deterministic CBOR bytes for the canonical model using Section 9.

A conforming `cdCDDLe` encoder MUST:

- encode only valid canonical CDDL schema models;
- use the CDE/RFC 8949 deterministic CBOR rules required by this
  specification;
- produce a single byte string for a given canonical model.

A conforming `cdCDDLe` decoder/checker MUST:

- reject non-deterministic CBOR encodings;
- reject malformed canonical model objects;
- reject unsupported required extensions or node kinds;
- expose the canonical model without assigning application-specific identity.

## 12. Conformance Vectors

Conformance vectors for this specification SHOULD use this structure:

```cddl
cdcddle-vector = {
    "name": tstr,
    "input-cddl": tstr,
    "expect": "valid" / "invalid",
    ? "canonical-diagnostic": tstr,
    ? "canonical-cbor-hex": tstr,
    ? "notes": tstr,
}
```

`input-cddl` is the source text under test.
`canonical-diagnostic` is a deterministic diagnostic notation for the
canonical CDDL schema model.
`canonical-cbor-hex` is the hexadecimal encoding of the CDE-based
deterministic CBOR bytes.

A vector MAY omit `canonical-cbor-hex` while the CBOR diagnostic notation and
byte-level fixture format are being developed.
Publication-quality vectors MUST include canonical bytes.

The first vector set SHOULD include at least:

- presentation equivalence for whitespace, comments, numeric spelling, and
  string escaping;
- top-level rule-order equivalence;
- preservation of distinct bound rule names with identical structure;
- preservation of choice alternative order;
- preservation of named references rather than full inlining;
- rejection of unsupported required extension nodes;
- rejection of non-deterministic CBOR encodings of the canonical model.

## 13. Open Issues

This revision deliberately leaves the following decisions open:

- exact coverage of CDDL modules or other future CDDL extension documents;
- whether additional registered CDDL control operators should receive
  operator-specific canonical forms rather than generic control-application
  nodes;
- whether a future extension should define a structural-equivalence view in
  addition to the required name-preserving canonical model;
- final conformance-vector publication format and additional byte examples.

These issues should be resolved before this specification advances beyond
its current raw maturity level.

## Appendix A. Storage-Like cdCDDLe Vector (Informative)

This appendix gives an informative `cdCDDLe` vector for the Storage-like
schema used by LOGOS-MODULE-COMMITMENT-MODEL Appendix A.
It shows the generic `cdCDDLe` canonical CDDL schema model before Logos domain
interpretation.
It does not synthesize Logos method declarations, choose a schema namespace, or
assign Logos schema roots.

Input CDDL:

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

Construction notes:

- `_module` and `_version` are ordinary CDDL type rules at this generic layer.
- Top-level rules are sorted by canonical rule key.
- Local references are preserved as reference nodes and are not inlined.
- The choice alternative order in `storage.lookup_key` is preserved.
- The `.size` controls are represented as control-application nodes with
  operator name `"size"`.

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
      1: "_version",
      3: {
        0: 7,
        1: {
          0: 9,
          1: [
            {
              0: 10,
              2: {
                0: 6,
                1: "uint",
                2: 1,
              },
            },
            {
              0: 10,
              2: {
                0: 6,
                1: "uint",
                2: 0,
              },
            },
          ],
        },
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
}
```

The deterministic CBOR byte length is `566` bytes.
The deterministic CBOR bytes, in hexadecimal, are:

```text
a200000188a3000101675f6d6f64756c6503a30006016474737472026e73746f
726167655f6d6f64756c65a3000101685f76657273696f6e03a2000701a20009
0182a2000a02a30006016475696e740201a2000a02a30006016475696e740200
a30001017173746f726167652e626c6f625f6861736803a4000e016473697a65
02a2000501646273747203a30006016475696e74021820a30001017573746f72
6167652e6368616e6765645f6576656e7403a2000801a200090182a3000a01a2
001501a30006016474737472026363696402a20003016b73746f726167652e63
6964a3000a01a2001501a30006016474737472026664696765737402a2000301
7173746f726167652e626c6f625f68617368a30001016b73746f726167652e63
696403a4000e016473697a6502a2000501647473747203a5000d01a300060164
75696e74020102a30006016475696e7402188003f504f5a30001017673746f72
6167652e6578697374735f7265717565737403a2000801a200090181a3000a01
a2001501a3000601647473747202636b657902a20003017273746f726167652e
6c6f6f6b75705f6b6579a30001017773746f726167652e6578697374735f7265
73706f6e736503a2000801a200090181a3000a01a2001501a300060164747374
72026665786973747302a200050164626f6f6ca30001017273746f726167652e
6c6f6f6b75705f6b657903a2000c0182a20003016b73746f726167652e636964
a20003017173746f726167652e626c6f625f68617368
```

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- [RFC 9165] -- Additional Control Operators for the Concise Data Definition
  Language (CDDL).
  https://www.rfc-editor.org/rfc/rfc9165
- IETF CBOR Common Deterministic Encoding (CDE),
  draft-ietf-cbor-cde, or its successor RFC if one is published.

### Informative

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
