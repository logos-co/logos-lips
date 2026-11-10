# LOGOS-MODULE-INTERFACE

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Interface                                        |
| Slug         | 301                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines equivalent CDDL and C representations of Logos module contracts
and their Logos deterministic CBOR value encoding.

A conforming contract has one Logos canonical schema model with two authoring representations:

- A **CDDL schema** for schema-oriented authoring and contract exchange.
- A **canonical C API** for C-oriented authoring and direct in-process calls.

The mapping is bidirectional and canonical.
Given either accepted representation, a conforming implementation of the bidirectional mapping MUST recover the same Logos canonical schema model, the same canonical representation on the other side, and the same Logos deterministic CBOR bytes for every schema-typed value.
A module implementation is not required to implement the authoring mappings; its contract artifacts and deterministic value encoding MUST conform to this specification.

A module author may start from either end:

- **CDDL-first:** Write a `.cddl` file, generate the C header.
- **C-first:** Write a conformant C header, generate the `.cddl` file.

Both paths MUST produce identical artifacts for the same logical contract and module binding, if any.

This specification does not define package discovery, module-instance admission or lifecycle, routing, local implementation realization, or message transport.
LOGOS-MODULE-SYSTEM-BCP assigns those responsibilities to higher-layer specifications and defines how they compose.
Conformance to this specification does not require conformance to a higher-layer specification or implementation of a higher-layer module contract.

In this specification, an **ABI caller** is the implementation component that invokes a native module ABI entry point.

Unless otherwise qualified, references to encoded payloads and wire bytes in
this specification mean Logos deterministic CBOR as defined in section 4.4.
For brevity, some later sections may still say "CBOR" in explanatory prose.
In this specification, those references MUST be read as Logos deterministic
CBOR unless the text is explicitly talking about generic CBOR concepts such as
major types, RFC terminology, or envelope-level compatibility with CBOR
itself.

### Execution-Boundary Invariance

The module contract defined by this specification is **execution-boundary
invariant**.

That means the same logical Logos method/event interface MUST remain valid
across all supported runtime realizations:

- **Direct mode** — in-process C calls using the derived/generated C API
- **Local transport mode** — the same contract carried over local IPC using
  Logos deterministic CBOR transport
- **Remote transport mode** — the same contract carried over remote transport

The execution boundary may change how a call is routed, serialised, scheduled,
or authorised, but it MUST NOT change:

- the module's method and event names
- the schema-defined request/response/event shapes
- the meaning of success and error results
- the exact selected schema identity

In other words, transport and process placement are runtime concerns. The
interface contract itself remains the same object regardless of whether a
caller reaches a module by direct C invocation, local IPC, or remote RPC.

## Requirements Language

Uppercase requirement keywords in this specification follow BCP 14 [RFC 2119] [RFC 8174].
Lowercase forms retain their ordinary English meanings.

## 1. CDDL Schema Conventions

### 1.1 Schema File

Concrete module contracts, reusable interface contracts, and supporting schemas have canonical CDDL representations.
This section defines the CDDL authoring form;
Section 3 defines how the equivalent form is recovered from canonical C.

Each CDDL-authored concrete module MUST have a single `.cddl` file that contains the canonical CDDL representation of its primary module contract.
The file is named `<module-name>.cddl` (e.g. `storage_module.cddl`).

The concrete module schema file defines:

- Module identity and implemented-interface references
- Custom data types used by the module
- Request types (method inputs)
- Response types (method outputs)
- Event types (asynchronous notifications)

An interface contract schema defines a reusable surface of methods, events, and types.
Concrete modules may implement that surface by exact reference.
An interface contract does not itself define a concrete module provider.

A supporting schema defines named types without defining a module, provider, callable method, or event surface.
It has no schema-role metadata marker.
Concrete module and interface contract schemas MAY reference named types from explicitly supplied supporting schemas.
A supporting schema MUST NOT reference a concrete module schema, interface contract schema, or another supporting schema.

Concrete module, interface contract, and supporting schemas implicitly have access to the Logos prelude fixed-width integer aliases.
They MAY reference the common Logos schema definitions in Section 5.

The normative construction input is an explicitly supplied set of ordinary RFC 8610 CDDL documents.
For a concrete module schema, that set contains the module document, every interface document selected by `_implements`, and every supporting schema that supplies a named type referenced by the module or those interfaces.
For an interface contract, the set contains its document and every supporting schema that supplies a named type it references.
A supporting schema required by more than one document appears only once in that input set.
The set MUST contain every required document and MUST NOT contain an unused interface or supporting schema.
Every supplied document MUST have a distinct schema root.

Local contract declarations and references use the explicit qualified names required by Sections 1.4 through 1.7 and LOGOS-MODULE-COMMITMENT-MODEL.
CDDL module `include` and `import` directives MUST NOT alter the resolved rule graph.
A schema that requires such a directive is unsupported even when the directive is encoded as a CDDL comment.
An external named-type reference in a concrete module or interface contract schema MUST resolve to exactly one declaration in an explicitly supplied supporting schema or the pinned Logos common schema.
An `_implements` entry is a whole-interface dependency and not a named-type import.
No schema document, filename, package location, network resource, or ambient resolver outside the explicit input set participates in schema resolution or identity.

Note: this spec uses `storage.*` names repeatedly as a convenient running
example for method, event, codegen, and transport-shape illustrations. Those
snippets are explanatory examples unless they are explicitly being used to
state a general module-interface rule. They do not, by themselves, define
the real Storage module interface.

### 1.2 Schema Metadata

Every concrete module `.cddl` file MUST begin with a metadata block:

```cddl
; -- metadata --
_module = "storage_module"
```

The `; -- metadata --` line is a non-semantic CDDL comment.
The metadata declarations are the underscore-prefixed declarations
defined by this specification.
Ordinary schema identifiers cannot begin with `_`.

A schema document MUST NOT declare both `_module` and `_interface`.
A document that declares `_module` is a concrete module schema.
A document that declares `_interface` is an interface contract schema.
Except for the pinned Logos common schema surface defined in Section 5,
a document that declares neither marker is a supporting schema and MUST NOT declare `_implements`.

The `_module` field is the module's flat runtime module name.
It is used for runtime lookup, socket naming, and C ABI symbol derivation.
Its syntax is the module-name grammar defined by LOGOS-MODULE-RUNTIME
section 1.3.
It is not, by itself, a complete global package identity or cryptographic
schema identity.

An interface contract schema MUST declare `_interface` instead of `_module`.
The `_interface` field names the reusable interface namespace.
It is human-readable metadata and a validation marker;
the canonical identity of the interface contract is its schema root.

```cddl
; -- metadata --
_interface = "metrics_provider"
```

A concrete module schema MAY declare `_implements`.
When present, its canonical rule body MUST be a nonempty fixed-content CDDL array whose elements are direct byte-string literals.
Each literal MUST contain exactly one 32-byte interface schema root.
A module that implements no interface MUST omit `_implements`; an empty array is invalid.
A module that implements exactly one interface MUST use a one-element array.
The roots MUST appear in strictly ascending lexicographic order by their raw 32-byte values.

Each root is an exact by-reference interface contract identity.
Unlike ordinary imports or references,
`_implements` makes the referenced interface's methods and events part of the
concrete module's exposed callable surface.

The root MUST match exactly one explicitly supplied interface document after that document is parsed and its schema root is recomputed.
The referenced document MUST declare `_interface`.
Its interface namespace is derived from that document and is already committed by its schema root.

Toolchains MAY accept local filenames, workspace labels, or catalog aliases before producing a canonical schema document.
They MUST resolve all such conveniences to the required fixed-content array of exact interface schema-root literals before the document is accepted as canonical input.
A concrete module schema with a missing, duplicate, unused, or mismatching interface document is invalid.

Runtime, package, and deployment records
MAY mirror resolved implemented-interface identities.
They are not required for a concrete module to implement an interface.

Interface contracts and supporting schemas MUST NOT declare `_implements`.
This revision does not define interface inheritance, interface composition,
default methods, method remapping, or structural duck typing.

Concrete module, interface contract, and supporting schemas do not carry release or compatibility versions.
An exact schema root identifies a contract.
Two different schema roots are not interchangeable unless another specification explicitly defines and selects a cross-root transformation.
This specification defines no such transformation.
Package and implementation release metadata is outside the schema contract and does not alter this rule.

A concrete module that declares `_implements` MUST implement the full Logos ABI
for its primary contract, when present, and for every implemented interface contract.
That ABI MAY be generated from CDDL or implemented by hand,
but handwritten implementations MUST expose behavior equivalent to the same
contract set.

An implementation may preserve an existing exact interface contract while exposing additional interfaces whose method names satisfy the uniqueness rules in Section 1.4.
Changing a concrete primary contract does not preserve that primary contract's identity.
Even unchanged source that references a different pinned common schema has a different constructed identity when its imported commitments change.
Overlapping contract revisions may be supplied by separate admitted providers or explicit adapters.
An adapter invokes its dependencies under its own authenticated module identity and separately authorized access; forwarding does not implicitly transfer the original consumer's authority.

#### 1.2.1 Sensitive Payload Declarations

A concrete module or interface contract schema MAY declare `_sensitive`.
When present, its body MUST be a nonempty fixed-content array of direct text-string literals naming local method request or response declarations.
The names MUST be distinct and sorted in ascending ASCII order.
A supporting schema MUST NOT declare `_sensitive`.
An absent `_sensitive` declaration marks no payloads; an empty array or a name that does not identify a local method request or response declaration is invalid.

```cddl
_sensitive = ["vault.store_request"]
```

Each listed declaration marks its complete payload as sensitive.
Request and response sensitivity are independent.
An implemented interface retains the sensitivity declarations of its defining contract; a concrete module MUST NOT remove or override them.
Sensitivity participates in canonical schema identity under LOGOS-MODULE-COMMITMENT-MODEL.
It is not a request field or a caller-controlled flag.

### 1.3 Logos Prelude

Every module schema is interpreted with a small Logos prelude in scope.
The prelude defines fixed-width integer aliases.
Reusable Logos-defined common types and well-known method surfaces are defined
by the Logos common schema surface in Section 5.
Module schemas MUST NOT redefine prelude names.

```cddl
uint8  = uint .size 1
uint16 = uint .size 2
uint32 = uint .size 4
uint64 = uint .size 8

int8  = -128..127
int16 = -32768..32767
int32 = -2147483648..2147483647
int64 = -9223372036854775808..9223372036854775807
```

The unprefixed integer aliases are provided for brevity because module
schemas are also ABI/codegen inputs.
They make integer width explicit without requiring every schema to repeat
CDDL range expressions.

Reserved Logos names:

- CDDL names beginning with `logos.`, `logos-`, or `logos_` are reserved for
  Logos-defined common-schema, runtime, and ABI surfaces unless this
  specification explicitly allows their use.
- `_module` values beginning with `logos_` are reserved for Logos-defined
  runtime and system modules.
- `_module` values containing `_call_` or `_publish_` are invalid under the Runtime module-name grammar.
- Exact flat module names assigned by a Logos specification, package catalog,
  or registry are reserved for that assigned module.
  For example, a Logos-defined module named `delivery` owns the flat runtime
  name `delivery`.
- The exported C symbol prefix `logos_` is owned by the Logos ABI.
  Module authors MUST NOT define additional exported `logos_*` symbols as
  module-specific API outside the symbols derived by this specification or by
  Logos-defined extension specifications.

The reserved Logos namespace is for system, runtime, ABI, and common-schema
surfaces.
It is not automatically assigned to every module authored by a Logos project.
An ordinary domain module, such as a Storage implementation, SHOULD use the
normal module namespace unless a Logos specification explicitly assigns it a
system/runtime surface.

Logos module schema identifiers that project to generated C identifiers use
lowercase `snake_case`.
This is intentionally less idiomatic CDDL than hyphenated names, but Logos
module schemas are also ABI and code-generation inputs.
The identifier grammar supports deterministic C naming while preserving schema spellings.

Such identifiers MUST use lowercase ASCII letters, digits, and underscores.
They MUST begin with a lowercase ASCII letter, MUST end with a lowercase
ASCII letter or digit, and MUST NOT contain consecutive underscores.
For a qualified schema name, these requirements apply separately to each dot-separated segment; the dot separates segments and is not part of any segment.
This rule applies to method names, event names, field names, and named type
names.
The metadata names `_module`, `_interface`, `_implements`, and `_sensitive`, the underscore-based runtime module name carried in `_module`, prelude aliases such as `uint64`, and exported C ABI symbols are not Logos module schema identifiers.
The complete schema namespace, including its dot separators, MUST contain at most 128 ASCII bytes.

A schema field name MUST NOT begin with `has_`.
This reservation applies to request, response, event, named-map, and inline-map fields.
It preserves the canonical C presence convention by ensuring that a generated `has_<field>` identifier cannot also represent schema data.

A schema field name MUST NOT end with `_len`, `_count`, or an underscore followed by one or more decimal digits.
This reservation applies to the same field kinds as the `has_` reservation.
It keeps generated length, count, and tuple-position members distinct from schema fields.

A schema field name MAY equal a C or C++ keyword, subject to the other field-name constraints.
Section 2.1 defines the corresponding C identifier escape.
CDDL emission MUST preserve field names as text keys and use quoted text-key syntax when a bare spelling would have another meaning.

A supporting schema MUST NOT declare a local named definition whose name ends in `_request`, `_response`, or `_event`.
Those suffixes are reserved for callable declarations in concrete module and interface contract schemas.

### 1.4 Methods as Request/Response Pairs

Methods are declared as pairs of named request and response declarations using the convention:

- `<module>.<method>_request` — the method input
- `<module>.<method>_response` — the method output

A map-valued body is either a CDDL map or a CDDL choice whose every arm is a CDDL map.
Each method request and response declaration MUST have a map-valued body.
The bare method name formed by removing the namespace prefix and the `_request` or `_response` suffix MUST contain at most 128 ASCII bytes.
A concrete module or interface contract MUST NOT declare a method whose bare method name equals a well-known method from the pinned Logos common schema.
In this revision, `schema`, derived from `logos.schema`, is the only such reserved bare method name.
Such a declaration makes the contract invalid.

The `<module>.` prefix is the schema namespace for the module's own
schema-defined methods, events, and types.
It SHOULD correspond to the module's logical name.
The flat runtime module name carried in `_module` is distinct from the schema namespace and is used for Runtime realization, routing, and C ABI symbol derivation.
Runtime bindings between `_module`, schema namespace, and schema commitment
are defined by LOGOS-MODULE-RUNTIME.
This revision defines one primary schema namespace per module schema.
Every local method, event, and named-type declaration MUST contain that explicit namespace prefix.
A reference to a local named type MUST use its qualified name.

For interface contract schemas,
the same request/response convention applies under the interface namespace.
Implemented interface methods remain in their interface namespace.
Declaring `_implements` does not copy, rename, or import those methods
into the concrete module's primary namespace.

For a concrete module that declares `_implements`,
the bare method names exposed by the primary module contract
and all implemented interface contracts MUST be unique.
A concrete module schema is invalid
if two exposed methods have the same bare method name.
This includes collisions between the primary module contract and an interface contract,
and collisions between two implemented interface contracts.

```cddl
storage.exists_request = {
    cid: tstr,
}

storage.exists_response = {
    exists: bool,
}
```

A codegen tool following this specification
recognises `*_request` / `*_response` pairs by naming
convention and generates the corresponding C function signatures
and wire protocol dispatch.

A method with no input uses an empty map: `storage.space_request = {}`.
A method with no contract result data uses an empty response map:
`storage.destroy_response = {}`.
Returning `LOGOS_OK` means that the invocation produced this valid empty response.
A method with an expected domain or application failure MUST represent that outcome in its response schema.
It MUST NOT use a nonzero shared `logos.error_code` for that contract outcome.

An invocation is one execution of a method for one request.
Every method remains one request with one final response.
Deferred completion permits that response to be supplied after the provider's submission entry returns; it does not declare another method kind or change the request and response schemas.
Independent invocations may complete in any order.

Map keys MUST be text keys satisfying the field-name requirements in Section 1.3.
A text key MAY use bareword colon-key syntax or quoted text-key syntax.
Both forms MUST have the same field identity for the same key text.
Key names are used directly as deterministic CBOR map keys and map to C parameter names under Section 2.4.

#### 1.4.1 Sensitive Payload Handling

For a marked payload, the caller, Runtime, invocation intermediaries, and provider SHOULD minimize temporary copies.
They MUST erase their owned temporary buffers containing payload data after their last use, before releasing or reusing their storage.
This requirement includes encoding, decoding, commitment processing, transport buffering, and partial processing on failure or cancellation.
Moving a buffer transfers the erasure obligation; copying its contents creates an additional obligation.
Cancellation MUST NOT release or erase a buffer while an operation still uses it.

Generated invocation code MUST preserve sensitivity through its temporary representations and cleanup paths.
Handwritten implementations have the same obligations.
An invocation path MUST NOT be established for a marked payload unless its participating implementations support these requirements.
An implementation MUST NOT silently downgrade a marked payload to ordinary handling.

Remote transports can retain plaintext in buffers owned by transport or cryptographic libraries.
Transport encryption alone does not satisfy the erasure requirements.
A remote path whose participating implementations cannot satisfy these requirements remains prohibited for marked payloads.

Marked payloads and their value-derived identifiers MUST NOT enter logs, audit records, or diagnostics.
Ordinary transient payload commitments remain required.
If active policy requires retaining a marked payload's value commitment, Runtime MUST reject the invocation before dispatch rather than retain it or omit the policy requirement.

These requirements do not prohibit intentional storage or subsequent use explicitly defined by the method's contract.
Each implementation remains responsible for the temporary copies it owns.
Sensitivity does not prove erasure by another implementation or protect plaintext from its intended recipient.
It does not grant authority or provide transport encryption.

Unmarked payloads acquire no erasure requirement from this property.
An implementation MAY conservatively protect shared or unclassified buffers that can contain marked payload data.

### 1.5 Event Declarations

Events are one-way notifications published by a module.
Each event declaration MUST have a map-valued body and the suffix `_event`:

```cddl
storage.upload_progress_event = {
    session: tstr,
    bytes_sent: uint64,
    bytes_total: uint64,
}

storage.upload_done_event = {
    cid: tstr,
}
```

The complete schema event identifier, including its namespace and `_event` suffix, MUST contain at most 128 ASCII bytes.

Event declarations are independent of method declarations.
Ordinary publication delivers an event to matching authorized subscriptions under LOGOS-MODULE-RUNTIME Section 7.3.
Invocation-scoped publication restricts the eligible subscriptions to the protected destination of one invocation under LOGOS-MODULE-RUNTIME Section 7.3.1.
Both publication modes use the same event declaration, payload schema, commitment and subscription mechanism.
An invocation-scoped event is not a separate contract declaration or message kind.
Event subscription is managed by Runtime and LOGOS-MODULE-TRANSPORT Section 5.

Events are a one-way notification mechanism with schema-defined payloads.
One-way means that an event has no response value
or per-publication reply path.
It does not require deferred execution, an intermediate queue, or a dedicated delivery thread.
They are used for progress updates, completion notifications, state changes,
and similar one-way signals.
They are NOT a second method system:
events do not return values, do not carry per-call correlation semantics
beyond subscription, and MUST NOT be used as a general replacement for
request/response methods.

Progress is an application meaning assigned to an intermediate event payload, not a distinct schema type.
A method used to watch a resource remains an ordinary method; it may publish invocation-scoped events before producing its final Response.
A job or stream session that spans invocations is a resource defined by the module contract, not an implicit resource created by deferred completion.
Ending a watch invocation does not by itself cancel the observed resource.

Restricting delivery does not add sensitivity metadata or erasure guarantees to an event.
The sensitive-payload requirements in Section 1.4.1 continue to apply to marked method requests and responses.

### 1.6 Custom Types

Custom types are declared using standard CDDL syntax:

```cddl
storage.space_info = {
    quota: uint64,
    used: uint64,
    available: uint64,
}

storage.peer_info = {
    id: tstr,
    addrs: [* tstr],
    ? name: tstr,
}
```

### 1.7 Type Restrictions

Module schemas MUST only use types from this set:

| Category | Allowed types |
|----------|--------------|
| Primitives | `bool`, `tstr`, `bstr` |
| Fixed-width integers | `uint8`, `uint16`, `uint32`, `uint64`, `int8`, `int16`, `int32`, `int64` |
| Literal values | Boolean, integer, and text literals used as exact schema values, including choice tag fields |
| Constrained strings | `tstr .size n`, `tstr .size (min..max)`, `bstr .size n`, `bstr .size (min..max)` |
| Arrays | `[* T]` (variable-length), `[T, T, T]` (fixed-length tuple) |
| Maps | `{ key: type, ... }` (struct-like maps with known keys) |
| Optional fields | `? key: type` (in maps only) |
| Choices | `T1 / T2 / T3` (tagged unions whose canonical arms satisfy the structural selection rules) |
| Named types | Named types resolved under Section 1.1. |

The following are **NOT allowed** in module schemas:

| Disallowed | Rule |
|-----------|------|
| Bare `uint`, `int`, `nint` | MUST NOT appear in module schemas except inside the Logos prelude definitions. Use fixed-width integer aliases instead. |
| `any` | MUST NOT appear in module schemas. Transport envelope uses `any` for generic payload fields; validation against concrete schema happens at the module layer. |
| `float16`, `float32`, `float64` | Reserved for a future deterministic numeric profile. |
| Unkeyed maps (`{ * tstr => any }`) | Reserved for transport envelope. |
| CBOR tags (beyond the transport envelope) | Reserved for protocol use. |
| `.regexp`, `.cbor`, `.bits` controls | Reserved for future versions. |

A contract may carry an external encoding in a `bstr` or `tstr` value and define its interpretation.
Generic Logos schema validation does not validate that embedded format.
Its boundary commitment covers the byte sequence or UTF-8 text without interpreting the embedded format or assigning semantic field paths inside it.
The byte-range commitment rules remain applicable.

A `tstr` schema type excludes U+0000 at every position.
This additional value constraint is required by the canonical NUL-terminated C representation defined in Section 2.2.

RFC 8610, Sections 1.1 through 1.7 of this specification,
and the resolution boundary in Section 5.3 determine whether source text is a valid Logos schema document.
After parsing and resolution,
`cdCDDLe` defines the canonical CDDL schema-as-data representation.
LOGOS-MODULE-COMMITMENT-MODEL applies the Logos domain interpretation to that representation
and defines schema identity and named-definition identities.
Section 4.4 of this specification defines the deterministic CBOR encoding of schema-typed values.
Source validity, canonical schema representation, schema identity,
and deterministic value encoding are distinct conformance boundaries.

Commitment-model note:
LOGOS-MODULE-COMMITMENT-MODEL does not define schema identity or canonical
value roots for floating-point values in this revision.
Floating-point types are reserved for a future deterministic numeric profile.

### 1.8 Complete Example

This interface contract schema defines a reusable metrics surface.
It does not itself define a concrete module provider.

```cddl
; -- metadata --
_interface = "metrics_provider"

metrics_provider.snapshot_request = {}
metrics_provider.snapshot_response = {
    count: uint64,
}
```

This complete `storage` schema is illustrative only. It demonstrates the
module-interface format; it is not the normative specification of the real
Storage module API.

```cddl
; -- metadata --
_module = "storage_module"

; -- types --
storage.space_info = {
    quota: uint64,
    used: uint64,
    available: uint64,
}

; -- methods --
storage.init_request = {
    data_dir: tstr,
}
storage.init_response = {}

storage.exists_request = {
    cid: tstr,
}
storage.exists_response = {
    exists: bool,
}

storage.space_request = {}
storage.space_response = {
    info: storage.space_info,
}

storage.destroy_request = {}
storage.destroy_response = {}

storage.upload_url_request = {
    chunk_size: uint64,
    url: tstr,
}
storage.upload_url_response = {
    accepted: bool,
}

storage.start_request = {}
storage.start_response = {}

; -- events --
storage.upload_progress_event = {
    session: tstr,
    bytes_sent: uint64,
    bytes_total: uint64,
}

storage.upload_done_event = {
    cid: tstr,
}

storage.started_event = {}
```

---

## 2. CDDL-to-C Canonical Mapping

This section defines the canonical derivation of C types, function signatures, and schema metadata from an accepted CDDL schema set.
Generated headers use the metadata-extended C form.
The declaration-only C form remains available for hand-written schema-authoring input.

A module binding identifies one runtime module name, its optional primary document, and its implemented interface set.
For a concrete module subject, the generator derives the binding from `_module` and `_implements`.
Generation of module-specific declarations without a concrete module subject requires an explicit module binding.
A standalone interface or supporting document does not establish a module binding.
A supplied binding MUST agree with the primary document's `_module` and `_implements`, when that document is present.
A binding MUST NOT change any supplied document or its schema identity.

Schema-derived C identifiers MUST have the same spelling in C17, C23, C++17, C++20, and C++23.
ABI function declarations and function types MUST have C language linkage when compiled as C++.
Native ABI participants MUST use compatible target C ABIs and calling conventions for all exchanged types, entry points, and callbacks.
Generated headers, including `logos_types.h`, MUST enclose those declarations in the following conditional linkage wrapper:

```c
#ifdef __cplusplus
extern "C" {
#endif

/* Declarations. */

#ifdef __cplusplus
}
#endif
```

Associated type declarations and inline helpers MAY be enclosed in the same wrapper.
Hand-written schema-authoring input MAY omit the wrapper.

The declaration-only C form represents every schema fact through canonical C names, declarations, types, and function signatures.
It contains no schema-metadata preprocessor constants.

The metadata-extended C form adds document-role namespace constants and preprocessor constants for schema or module-binding facts that cannot be represented or recovered unambiguously from the canonical C declarations.
Those constants supply build-time schema or module-binding facts and add no runtime symbol, storage, function parameter, or caller obligation.
Except for document-role namespace constants, they MUST NOT restate a schema fact that the declaration-only mapping recovers unambiguously.

A generator MUST emit the document-role namespace constants specified in Section 2.1.
It MUST emit other schema-metadata constants only when required to preserve schema facts or the module binding.
Every accepted schema set MUST be representable by one of the two forms.
Given the same accepted schema set and module binding, if any, any two implementations of this specification MUST produce the same canonical declarations and constants, including their names, types, values, dependency relationships, field order, parameter order, and choice representation.
Whitespace, comments, declaration placement permitted by Section 2.1, include layout, and file-level include guards MAY differ.

This mapping is total from an accepted CDDL schema set to canonical C.
The reverse mapping accepts only the C subset defined in Section 3.
Consequently, a module may be authored from a conforming C contract without requiring every schema construct to be expressible through ordinary C declarations alone.
The metadata-extended form preserves schema facts that the declaration-only C form cannot represent.

`LOGOS_C_MAPPING_REVISION` identifies the compatibility generation of the canonical C declarations and fixed common-header environment.
Its value in this specification is `3u`.
An incompatible change to those declarations or their ABI semantics requires a new value.
A generator release or a change that preserves that compatibility MUST NOT by itself change the value.

Generated contract headers MUST include `logos_types.h` and check the generation they target before any declaration-suppressing guard.
For generation `3u`, the check is:

```c
#include "logos_types.h"
#if !defined(LOGOS_C_MAPPING_REVISION) || LOGOS_C_MAPPING_REVISION != 3u
#error "Incompatible Logos C mapping"
#endif
```

A generated contract header MUST NOT define or override `LOGOS_C_MAPPING_REVISION`.
Hand-written schema-authoring input MAY omit this check; a supplied check MUST agree with the mapping used for reconstruction.
The revision does not affect schema identity and MUST NOT be used as a requirement that all installed modules or serialized peers use the same C mapping generation.
The check does not establish native binary compatibility or replace initialization-input and vtable ABI checks.

The common header MUST define the following commitment-context markers with value `1`.
In each marker name, `<hex>` is the complete lowercase hexadecimal encoding of the identifier's ASCII bytes.

| Marker | Identifier |
|--------|------------|
| `LOGOS_C_CONTEXT_MODEL_<hex>` | `logos.commitment-model.2026-10` |
| `LOGOS_C_CONTEXT_PROFILE_<hex>` | `logos.hash-profile.2026-08.choice-index` |
| `LOGOS_C_CONTEXT_SUITE_<hex>` | `logos.hash-suite.blake3-256` |

Generated contract headers MUST check that each expected marker is defined and equals `1`, and issue `#error` otherwise.
These checks MUST precede any declaration-suppressing guard.
A generated contract header MUST NOT define or override the markers.
Hand-written schema-authoring input MAY omit these checks; supplied checks MUST agree with the commitment context used for reconstruction.
The checks are derived build-time assertions and MUST NOT affect reconstructed schema identity.

### 2.1 Naming Conventions

**Namespace projection.** The C namespace component is the complete schema namespace with each dot replaced by `_NS_`.
The reverse mapping replaces each `_NS_` with a dot and requires that re-encoding reproduce the complete component exactly.
Existing underscores are preserved, and no leading namespace segment is removed.

| Schema namespace | C namespace component |
| --- | --- |
| `storage` | `storage` |
| `metrics_provider` | `metrics_provider` |
| `logos.runtime_control` | `logos_NS_runtime_control` |

**Module-name projection.** The `<module-C>` component encodes the runtime module name from the module binding.
For each underscore in the runtime name, emit `_U` if the next source character is another underscore or the underscore is the final character; otherwise, preserve it.
Preserve every other character unchanged.
For example, `vault_module` remains `vault_module`, `a__b` becomes `a_U_b`, and `a_` becomes `a_U`.
To decode, replace each `_U` with one underscore, validate the recovered runtime module name, and require that re-encoding reproduces the complete component exactly.
This projection does not change the runtime module name or its admission rules.

**Module symbols.** Module identity, lifecycle, provider-control, and memory-management symbols use `logos_<module-C>_MODULE_<operation>`.
Generated headers MUST declare each non-common document's exact namespace and role using one document-role namespace constant.
An interface or supporting document's constant MUST be the same whether the document is generated alone or included by a provider.
Hand-written input MAY omit a document-role namespace constant only where Section 3.2 defines unambiguous inference.
A concrete module document uses `LOGOS_PRIMARY_NAMESPACE_<module-C>`, an interface document uses `LOGOS_INTERFACE_NAMESPACE_<namespace>`, and a supporting document uses `LOGOS_SUPPORTING_NAMESPACE_<namespace>`.
The module and namespace components use the projections above with their case preserved.
Each string value is the exact schema namespace before C namespace projection.

For example, a multi-document provider header set may contain:

```c
#define LOGOS_PRIMARY_NAMESPACE_storage_module "storage"
#define LOGOS_IMPLEMENTS_storage_module_INDEX0 "metrics_provider"
#define LOGOS_INTERFACE_NAMESPACE_metrics_provider "metrics_provider"
#define LOGOS_SUPPORTING_NAMESPACE_storage_types "storage_types"
```

Each implemented interface adds one zero-based `LOGOS_IMPLEMENTS_<module-C>_INDEX<index>` string constant.
The constants contain the exact interface namespaces in ascending raw interface-root order, with no missing index.
They select implemented interfaces whether or not the module has a primary document.
A dotted primary namespace is preserved in the string value while its C declarations use the projected namespace component:

```c
#define LOGOS_PRIMARY_NAMESPACE_logos_runtime_control \
    "logos.runtime_control"
```

Each sensitive payload adds one zero-based `LOGOS_SENSITIVE_<namespace>_INDEX<index>` string constant containing its exact qualified declaration name.
The constants follow the ASCII order of `_sensitive`, with contiguous indices beginning at zero.
Implementation and sensitivity indices use decimal without leading zeros, except for zero itself.
An unmarked contract emits no sensitivity constants.
These constants select the metadata-extended C form without changing method signatures.

**Method symbols.** A schema method uses
`logos_<module-C>_CALL_<namespace>_<Method>`.
The `<namespace>` component is the C namespace projection of the contract that defines the method, including when the concrete module implements that contract by reference.
The `<Method>` component capitalizes only the first ASCII letter of the bare schema method name and preserves all remaining characters.
The `<module-C>` component uses the module-name projection above.
For example, `storage.exists_request` exposed by `storage_module` maps to `logos_storage_module_CALL_storage_Exists`.
The `metrics_provider.snapshot_request` method exposed by the same module maps to `logos_storage_module_CALL_metrics_provider_Snapshot`.

The longer symbol records three distinct identities: the concrete provider module, the defining contract namespace, and the method within that contract.
Omitting the module component would cause collisions when multiple statically linked modules implement the same interface.
Omitting the namespace would prevent the reverse mapping from assigning the method to the primary contract or the correct implemented interface.
The explicit components make the exported ABI self-describing without a non-C annotation.

The bare method name, for example `"upload_url"`,
is the method-name string exposed by this specification.
It does not include the schema namespace prefix.
LOGOS-MODULE-TRANSPORT defines how this method-name string is carried
in transport envelopes.
For a concrete module that declares `_implements`,
the same bare method-name space covers the primary module contract
and all implemented interface contracts.
Because exposed bare method names are required to be unique,
the bare method name identifies at most one exposed method for that concrete module.


| Module | CDDL pair base | C function |
| --- | --- | --- |
| `storage_module` | `storage.init` | `logos_storage_module_CALL_storage_Init` |
| `storage_module` | `storage.upload_url` | `logos_storage_module_CALL_storage_Upload_url` |
| `telemetry_module` | `metrics_provider.snapshot` | `logos_telemetry_module_CALL_metrics_provider_Snapshot` |

The final C function component uses the `<Method>` spelling above; the schema method name remains unchanged.

**Reserved ABI names.** The `MODULE` component separates standard module exports from schema methods, which use the `CALL` component.
Schema methods such as `init` or `destroy` therefore do not collide with lifecycle symbols.
This affects only the generated C symbol names.
The wire method name remains the bare schema method name, for example
`"version"`.

**Semantic stems.** Capitalizing a schema atom changes only its first ASCII letter to uppercase and preserves every remaining character.
A named declaration's stem is its C namespace component, one underscore, and its capitalized local declaration name.
In named-type patterns, `<Type>` denotes that capitalized local declaration name.
An inline composite's stem appends its complete schema path to the nearest containing named declaration's stem.
The path contains every step from that declaration's body to the composite, in traversal order:

- A map field contributes `_` followed by its capitalized schema field name.
- A list element contributes `_LI`.
- A tuple position contributes `_TU<index>`.
- A choice arm contributes `_AR_<Label>` in symbolic form or `_AR<index>` in indexed form, as defined in Section 2.3.

Indices are zero-based decimal without leading zeros, except for zero itself.
The path includes list-element steps even when omitting one would not cause a collision in the supplied schema set.
Named references retain the defining declaration's namespace and name; using a reference does not create an inline declaration at the use site.
Structural paths use original schema names before C member keyword escaping.

Schema atoms contain no uppercase letters.
A capitalized atom has exactly one uppercase letter, at its start; structural tokens contain at least two consecutive uppercase letters.
The reverse mapper MUST recover the namespace, owner, and complete path using these component boundaries and validate them against aggregate containment and type use.
The mapper MUST reject a noncanonical spelling or a path that does not identify the represented schema node.
A symbolic choice-arm label is consumed as one component, including any namespace and declaration components in a reference label, before parsing subsequent path steps.

**Type and constant families.** The following families preserve the case of the complete stem:

| Declaration | C identifier |
| --- | --- |
| Schema value typedef, when emitted | `logos_<stem>_t` |
| Map aggregate tag | `logos_<stem>_MAP` |
| Byte-string aggregate tag | `logos_<stem>_BSTR` |
| List aggregate tag | `logos_<stem>_LIST` |
| Tuple aggregate tag | `logos_<stem>_TUPLE` |
| Choice aggregate tag | `logos_<stem>_CHOICE` |
| Map event aggregate tag | `logos_<stem>_EVENT` |
| Choice discriminant typedef | `logos_<stem>_KIND_t` |
| Symbolic choice arm constant | `LOGOS_ARM_<stem>_CASE_<Label>` |
| Indexed choice arm constant | `LOGOS_ARM_<stem>_CASE<index>` |
| Scalar literal constant | `LOGOS_LITERAL_<stem>` |

A literal's stem includes its complete schema path, including its choice-arm and map-field steps when applicable.
An aggregate tag identifies the represented schema construct independently of its member names.
The mapper removes a generated family suffix exactly once; for example, declaration `x_t` produces a typedef ending in `_X_t_t`, while `x_kind` produces `_X_kind_t`, distinct from `_X_KIND_t`.
A defining-contract method typedef retains the `logos_<namespace>_<Method>_FN_t` family specified in Section 2.4.

| CDDL type | C type |
| --- | --- |
| `storage.space_info` | `logos_storage_Space_info_t` |
| `storage.peer_info` | `logos_storage_Peer_info_t` |
| `logos.runtime_control.state` | `logos_logos_NS_runtime_control_State_t` |

**Inline composites.** An inline composite is a schema node that requires an aggregate under Section 2.3 and is not itself a named declaration body.
Except for the shared empty-value types in Section 2.3, inline composites use the same typedef family as named schema values, with their full path included in the stem.
Their tags use the corresponding aggregate family above.
An anonymous map arm therefore includes its containing choice's arm step in every associated type, tag, and literal-constant name.
Equal inline shapes at different schema paths retain distinct stems.
The mapper MUST NOT synthesize named CDDL declarations for inline composites.

If two schema nodes derive the same C identifier, the schema set is invalid for this C mapping.
A generator MUST NOT choose a different spelling to resolve the collision.

Types from the pinned Logos common schema use their exact predefined names from `logos_types.h`:

| CDDL type | C type |
| --- | --- |
| `logos.error_code` | `logos_error_code_t` |
| `logos.error_detail` | `logos_error_detail_t` |
| `logos.schema_commitment` | `logos_schema_commitment_t` |

`logos.error_code` reuses the shared `logos_error_code_t` status enum instead of receiving a separate choice declaration.
The fixed common declarations retain their specified names and layouts rather than receiving generated stem names.
This exception applies only to the pinned common document and the fixed mapping environment.
A non-common namespace such as `logos.runtime_control` retains its complete namespace projection.

`logos_result_t` is the shared C ABI invocation-status structure.
It is not a schema-defined contract value.

**Keyword escaping.** The following fixed set contains the identifier spellings requiring an escape in this mapping:

```text
alignas alignof and and_eq asm auto bitand
bitor bool break case catch char char16_t
char32_t char8_t class co_await co_return co_yield compl
concept const const_cast consteval constexpr constinit continue
decltype default delete do double dynamic_cast else
enum explicit export extern false float for
friend goto if inline int long mutable
namespace new noexcept not not_eq nullptr operator
or or_eq private protected public register reinterpret_cast
requires restrict return short signed sizeof static
static_assert static_cast struct switch template this thread_local
throw true try typedef typeid typename typeof
typeof_unqual union unsigned using virtual void volatile
wchar_t while xor xor_eq
```

For each schema-derived C identifier, first construct the complete identifier using the naming and field-expansion rules.
If that complete identifier is in the set above, append exactly one underscore; otherwise, leave it unchanged.
The escape MUST NOT depend on the compilation language.
For example, field `class` has member `class_`, while its presence flag `has_class`, length member `class_len`, and parameter `in_class` retain those spellings when emitted.
Schema names, metadata values, structural naming paths, and field ordering MUST use the original schema spelling.
The escape does not change schema identity or encoded map keys.

**Identifier significance and limits.** The C mapping imposes no additional fixed maximum identifier length beyond the schema-name constraints in Section 1.
Canonical identifiers MUST retain their complete spelling and case.
Tooling MUST NOT truncate them or substitute hashes or aliases to fit an implementation limit.
Supported native build and loading paths MUST preserve all identifier distinctions through preprocessing, compilation, linking, and symbol resolution.

Tooling implementing this mapping MUST document its identifier-length and resource limits.
An operation that exceeds a documented limit MUST fail explicitly and MUST NOT present a partial result as a conforming output.
Such a failure does not make the schema invalid or change its identity.
Tool-specific limits MUST NOT relax the schema-validation requirements of Section 5.3.

**Derived helper names.** Names of optional typed call, cleanup, event-publication, and subscription helpers and their associated typed handler typedefs are implementation-defined.
These declarations are derived conveniences and MUST remain outside the header set supplied for schema reconstruction under Section 3.
They MUST NOT affect schema identity.
Fixed common declarations and required provider symbols retain their specified names and mapping rules.

**Declaration dependencies and value order.** A generated header set MUST declare every name before a use that requires its declaration and define every type before a use that requires its complete definition.
Forward declarations satisfy pointer uses under Section 2.3.
The relative placement of otherwise independent declarations, macros, lifecycle functions, and provider functions is not part of the canonical mapping.
The required declaration names, types, values, metadata, and dependency relationships remain unchanged by source ordering.
Struct fields and the corresponding method parameters are ordered by ascending lexicographic order of their valid UTF-8 field-name bytes.
Choice representation uses the arm ordering and tag-to-canonical-index association specified in Section 2.3.
Source declaration order is not ABI-visible.
An accepted schema set MUST NOT produce two identical C identifiers or a namespace-projection collision.

### 2.2 Primitive Type Mapping

| CDDL type  | CBOR major type           | C type                          | Notes                              |
|------------|---------------------------|---------------------------------|------------------------------------|
| `bool`     | 7 (simple true/false)     | `bool`                          | `<stdbool.h>`                      |
| `uint8`    | 0 (unsigned integer)      | `uint8_t`                       | Range 0..255                       |
| `uint16`   | 0 (unsigned integer)      | `uint16_t`                      | Range 0..65535                     |
| `uint32`   | 0 (unsigned integer)      | `uint32_t`                      | Range 0..4294967295                |
| `uint64`   | 0 (unsigned integer)      | `uint64_t`                      | Range 0..2^64-1                    |
| `int8`     | 0 or 1 (signed integer)   | `int8_t`                        | Range -128..127                    |
| `int16`    | 0 or 1 (signed integer)   | `int16_t`                       | Range -32768..32767                |
| `int32`    | 0 or 1 (signed integer)   | `int32_t`                       | Range -2^31..2^31-1                |
| `int64`    | 0 or 1 (signed integer)   | `int64_t`                       | Range -2^63..2^63-1                |
| `tstr`     | 3 (text string)           | `const char*`                   | UTF-8, NUL-terminated              |
| `bstr`     | 2 (byte string)           | `const uint8_t*` + `size_t`    | Always pointer + length pair       |

The generated decoder MUST reject integer values outside the selected alias's
range.
The deterministic CBOR wire representation still uses the shortest integer
encoding; fixed-width aliases define the valid value range and C ABI type, not
a fixed wire width.

**Underlying CDDL definitions:**

| CDDL constraint  | C type      |
|-------------------|-------------|
| `uint .size 1`    | `uint8_t`   |
| `uint .size 2`    | `uint16_t`  |
| `uint .size 4`    | `uint32_t`  |
| `uint .size 8`    | `uint64_t`  |

Logos `tstr` values MUST NOT contain U+0000.
Canonical C represents `tstr` as a NUL-terminated string, so an embedded zero byte would be indistinguishable from the terminator and could be truncated by a conforming C implementation.
CDDL and C decoders MUST reject a `tstr` value containing U+0000 before exposing it through the canonical C API.

Constrained strings use ordinary C typedefs whose canonical names preserve the constraint:

```c
typedef const char* logos_tstr_size_64_t;       /* tstr .size 64 */
typedef const char* logos_tstr_size_1_64_t;     /* tstr .size (1..64) */
typedef const uint8_t* logos_bstr_size_1_4096_t; /* bstr .size (1..4096) */
```

The decimal components are written without leading zeroes.
An exact `tstr` size has one component;
a closed `tstr` or `bstr` range has its minimum and maximum components.
The generated validator enforces the constraint at runtime.
The reverse mapping recognizes only a typedef whose name and underlying pointer type agree with this rule.

An exact-size byte string with a positive size maps to an array so its size remains part of the C declaration:

```c
uint8_t digest[32]; /* bstr .size 32 */
```

An exact-size byte-string function input with a positive size uses a pointer to the complete array type such as `const uint8_t (*in_digest)[32]`, so ordinary C parameter adjustment does not erase the bound.
An exact-zero byte string uses the empty-value representation in Section 2.3.
An exact-size byte string MUST NOT use a pointer-valued constraint typedef.

### 2.3 Composite Type Mapping

**Maps (structs).** A CDDL map with identifier keys maps to a C struct:

```cddl
storage.space_info = {
    available: uint64,
    quota: uint64,
    used: uint64,
}
```

```c
typedef struct logos_storage_Space_info_MAP {
    uint64_t available;
    uint64_t quota;
    uint64_t used;
} logos_storage_Space_info_t;
```

C struct fields appear in canonical field-name order.

**Optional fields.** CDDL `? key` adds a `bool has_<field>` presence flag:

```cddl
storage.peer_info = {
    id: tstr,
    ? name: tstr,
}
```

```c
typedef struct logos_storage_Peer_info_MAP {
    const char* id;
    bool        has_name;
    const char* name;       /* valid only if has_name == true */
} logos_storage_Peer_info_t;
```

The generated presence flag is not a schema field.
In canonical C, an identifier beginning with `has_` is valid only as the exact `bool` presence flag for its adjacent field.

**Arrays.** Variable-length arrays map to pointer + count:

| CDDL type       | C type                                 |
|------------------|----------------------------------------|
| `[* tstr]`       | `const char* const* items, size_t count` |
| `[* uint64]`     | `const uint64_t* items, size_t count`  |
| `[* T]` (struct) | `const logos_T_t* items, size_t count` |

Fixed-length tuples preserve positional order.
A named tuple uses struct members `item_0`, `item_1`, and so on.
A nonempty tuple used inline as field `x` uses adjacent members `x_0`, `x_1`, and so on.
Method parameters use the same components with the direction prefix defined in Section 2.4.
The reverse mapper removes those generated components and reconstructs the tuple positions.
For an optional inline tuple field `x`, one `bool has_x` immediately precedes the first expanded member `x_0` and governs the complete adjacent tuple group.
The tuple components MUST NOT have separate presence flags.
When the flag is false, every component of that tuple field is ignored.
An optional empty tuple uses one presence flag immediately before its shared empty-value member.
Method parameters follow the same grouping with their input or output direction prefix and the parameter types specified in Section 2.4.

Unbounded and ranged byte strings use the same adjacent pointer-and-length representation in structs and function signatures.
For a bounded byte string, the pointer has the canonical constraint typedef from Section 2.2.
An implementation MUST treat a pointer-and-length pair as one schema field and MUST keep the pair adjacent.

**Named aliases and aggregates.** Every named CDDL type retains its declaration identity in C:

- A named scalar or constrained string uses a `typedef` to its canonical scalar or constraint type.
- A named map uses the canonical `_MAP` aggregate form above.
- A named byte string uses a struct with adjacent `data` and `len` members, except that a positive exact-size byte string uses one `data[N]` member and an exact-zero byte string uses the empty-value representation below.
- A named variable-length list uses a struct with adjacent `items` and `count` members.
- A named tuple uses a struct with `item_<index>` members.
- A named choice uses the fixed-discriminant form below.

**Inline aggregate values.** For tuple positions, list elements, and choice arms, an inline tuple, list, or byte string MUST be represented by one aggregate value.
The aggregate uses the corresponding named aggregate layout above, with names derived under Section 2.1.
An empty tuple or exact-zero byte string uses the shared empty-value type defined below instead.
A variable-length list of inline aggregates stores complete aggregate values by value in its contiguous element array.
A positive exact-size byte string in these positions uses the aggregate's `data[N]` member.
These aggregates remain subject to the recursive aggregate-reference rules.

**Empty values.** A generated struct for the schema `{}`, `[]`, or `bstr .size 0` MUST contain exactly one member, `uint8_t _empty;`.
This includes empty event payload structs.
The placeholder contributes no schema field or wire data.
Encoders and value validators MUST ignore its value; decoders MUST initialize it to zero.

The fixed mapping environment in `logos_types.h` supplies these types:

```c
typedef struct logos_bstr_size_0 {
    uint8_t _empty;
} logos_bstr_size_0_t;

typedef struct logos_tuple_size_0 {
    uint8_t _empty;
} logos_tuple_size_0_t;
```

An inline `bstr .size 0` uses `logos_bstr_size_0_t`.
An inline `[]` uses one `logos_tuple_size_0_t` value.
These representations apply in map fields, tuple positions, list elements, choice arms, and method parameters.
Named declarations with these empty bodies retain their own aggregate declarations and type names.
An empty request or response map has no corresponding method parameters, as specified in Section 2.4.

An inline composite uses the applicable owner, path, tag, discriminant, and typedef derivation defined in Sections 2.1 and 2.3.
A method input whose C representation is a struct is passed as `const <type>*`;
its output is passed as caller-allocated `<type>*`.

**Recursive aggregate references.** The canonical C mapping computes a directed by-value representation graph over every generated aggregate declaration.
The graph contains an edge from aggregate `A` to aggregate `B` for each schema occurrence that would otherwise embed the complete C representation of `B` directly in `A`.
An occurrence beneath a variable-length list does not add a by-value edge because the list representation already uses a pointer and count.

A by-value edge is recursive when its endpoints belong to the same strongly connected component and that component contains more than one node or the edge is a self-loop.
Every recursive by-value edge maps to `const B*` instead of an embedded `B` value.
Every other named aggregate occurrence retains its ordinary by-value representation.
This rule applies equally to map fields, tuple items, and choice union arms.

The generator emits a canonical forward typedef for each aggregate referenced by a recursive edge before any definition in that recursive component.
The generator MUST also emit a forward typedef whenever an aggregate type name is used before its complete definition, including uses through variable-length lists.
A pointer use does not require the complete aggregate definition to precede the use and does not add a by-value representation edge.
A required recursive pointer MUST be non-null in a conforming C value.
For an optional field, the adjacent `has_<field>` flag alone records presence;
when the flag is true, the recursive pointer MUST be non-null, and when the flag is false, the pointer value is ignored.
Recursive indirection does not add schema optionality, ownership transfer, or a wire-level reference.
Deterministic CBOR encoding recursively encodes the pointed-to value as the referenced schema type.

**Literals.** A literal uses the C representation of its scalar base type and a canonical macro containing its exact required value, except that a direct literal choice arm omits redundant payload storage as specified below.
Every literal constant uses `LOGOS_LITERAL_<stem>`, preserving the case and complete schema path specified in Section 2.1.
Generated Boolean literals use `true` or `false`.
Generated nonnegative integer literals use `UINT64_C(n)`, where `n` is the unsigned decimal value without leading zeros except for zero itself.
Generated negative integer literals other than the minimum `int64` value use `(-INT64_C(n))`, where `n` is the positive decimal magnitude without leading zeros.
The minimum `int64` value uses `(-INT64_C(9223372036854775807) - INT64_C(1))`.
Generated text literals use one ordinary C string literal containing the exact UTF-8 bytes and one implicit terminating NUL.
The generator emits printable ASCII bytes directly, except that double quote, backslash, and question mark use `\"`, `\\`, and `\?` respectively.
Newline, carriage return, and tab use `\n`, `\r`, and `\t`; every other byte uses exactly three octal digits after a backslash.
Embedded NUL remains forbidden by the text-value rules.
Handwritten literal constants may use the equivalent forms specified in Section 3.5.
A generated encoder MUST emit the required literal, and a provider or decoder MUST reject another value.

**Choices (tagged unions).** Type choices map to tagged unions:

```cddl
storage.value = uint64 / tstr / bool
```

```c
typedef uint32_t logos_storage_Value_KIND_t;
#define LOGOS_ARM_storage_Value_CASE_Bool 0u
#define LOGOS_ARM_storage_Value_CASE_Tstr 1u
#define LOGOS_ARM_storage_Value_CASE_Uint64 2u

typedef struct logos_storage_Value_CHOICE {
    logos_storage_Value_KIND_t kind;
    union {
        bool        arm_Bool;
        const char* arm_Tstr;
        uint64_t    arm_Uint64;
    } value;
} logos_storage_Value_t;
```

The discriminant typedef MUST have underlying type `uint32_t`.
Arm constants use unsigned decimal integer literals with the suffix `u` and no leading zeros except for zero itself.
Every native discriminant value MUST identify one declared arm before its payload is accessed.
If the largest assigned discriminant exceeds `UINT32_MAX`, the operation MUST fail explicitly as a mapping-limit failure under Section 2.1; the schema does not become invalid solely for that reason.
The fixed common status enums retain their specified representation.

**Arm labels.** Derive a candidate label independently from each canonical arm without following named references.
Capitalization and namespace projection follow Section 2.1.
The following rules determine the label:

| Arm schema | Candidate label |
| --- | --- |
| Primitive, including constraints | Capitalized primitive kind from Section 2.2, such as `Int16` or `Bstr`. |
| Direct scalar literal | Capitalized literal token defined below. |
| Map with required direct-literal fields | Join those fields' literal tokens with single underscores, then capitalize the result once. |
| Map without required direct-literal fields | `Map` followed by each required field name prefixed with `_`; an empty or optional-only map yields `Map`. |
| List | `List`. |
| Tuple with n positions | `Tuple<n>`, with n in canonical decimal. |
| Named reference | The defining C namespace component, `_`, and the capitalized local declaration name. |
| Choice or any unlisted node kind | No candidate label. |

Boolean literal tokens are `true` and `false`.
A nonnegative integer literal uses `num` followed by its canonical decimal value; a negative integer uses `neg` followed by its unsigned decimal magnitude.
A text literal uses its exact text with each hyphen replaced by an underscore, but only when the result satisfies the schema-atom grammar in Section 1.3.
Other literals have no token.
Literal values and scalar kinds remain unchanged in their canonical literal constants.

Map fields participating in a label are ordered by ascending lexicographic order of their original UTF-8 field-name bytes.
Optional fields do not participate.
If any required direct-literal field has no token, the map has no candidate label; that field MUST NOT be silently omitted from label derivation.
A named reference retains its reference label even when its target is a literal or composite.

**Symbolic and indexed forms.** A choice MUST use symbolic form when every arm has a candidate label and all labels are distinct byte-for-byte.
Otherwise, the entire choice MUST use indexed form.
This decision is made independently at each nested choice.
A generator or author MUST NOT choose indexed form merely as an alternative spelling for a symbolically representable choice.

In symbolic form, sort labels by ascending ASCII byte order and assign consecutive C discriminant values starting at zero.
Arm labels appear in `LOGOS_ARM_<stem>_CASE_<Label>` constants, `arm_<Label>` union members when present, and `_AR_<Label>` support-path steps.
In indexed form, use each arm's zero-based canonical schema index as its C discriminant value, with `CASE<index>`, `arm_<index>`, and `_AR<index>` spellings.
Source CDDL order is not ABI-visible.

The canonical schema-arm order remains the order defined by LOGOS-MODULE-COMMITMENT-MODEL.
Native readers, writers, validators, encoders, decoders, and cleanup operations MUST associate each C discriminant with that arm's canonical schema index and matching payload representation.
They MUST NOT assume that a symbolic C discriminant equals the canonical index.
For example, `int16 / tstr` has C labels `Int16` and `Tstr` with values `0` and `1`, while its canonical schema order is `tstr`, then `int16`.
Wire values, commitments, and proof paths continue to use canonical schema indices.
The `bool`, `tstr`, and `uint64` example above happens to have the same C and canonical order.

**Choice payload storage.** Each arm other than a direct scalar literal has one union member with its canonical value representation.
A direct scalar literal arm has its literal constant but no union member; its discriminant determines the complete value.
A reference to a named literal retains its normal reference representation and is not treated as a direct literal arm.
When at least one arm has payload storage, the choice struct contains the discriminant member `kind` followed by the union member `value`.
When every arm is a direct scalar literal, the choice struct contains only `kind`; it MUST NOT contain an empty or dummy union.
Required literal fields inside map arms remain writable schema fields.

**Constraint:** Every choice MUST admit the structural selection plan defined by LOGOS-MODULE-COMMITMENT-MODEL.
Source declaration order MUST NOT be used to disambiguate choice arms.
For a decoded value, the plan selects at most one candidate arm, and the complete value MUST validate against that arm.
Failure to select a candidate or failure of complete arm validation makes the value invalid for the choice schema.
If a structural selection plan cannot be constructed, the choice schema is invalid.

Valid choices include arms with disjoint CBOR major types:

```cddl
storage.value = uint64 / tstr / bool
```

They also include tagged map unions whose arms are distinguished by a required literal tag field:

```cddl
storage.entry =
  { kind: "file", path: tstr } /
  { kind: "dir", path: tstr, entries: [* tstr] }
```

The two anonymous map arms use typedefs `logos_storage_Entry_AR_File_t` and `logos_storage_Entry_AR_Dir_t`, with aggregate tags `logos_storage_Entry_AR_File_MAP` and `logos_storage_Entry_AR_Dir_MAP`.
Their C discriminant values are `File = 1` and `Dir = 0`, following ASCII label order rather than canonical schema-arm order.
For the nested inline schema:

```cddl
storage.record = {
  sub: {
    inner: uint64 / tstr,
  },
}
```

the map at field path `sub` uses `logos_storage_Record_Sub_t`,
and the choice at field path `sub.inner` uses `logos_storage_Record_Sub_Inner_t`
with discriminant typedef `logos_storage_Record_Sub_Inner_KIND_t`.

The tag field is normal schema data.
It is encoded as part of the selected map alternative and is not an extra
transport wrapper.
The canonical C representation MUST retain a required literal tag field as a writable member of its map struct.
Encoders MUST still emit the literal tag field in the CBOR map.

An inline choice uses the deterministic name derived in Section 2.1.
Choice arm constants, union members, and support paths MUST all use the same symbolic or indexed form selected for that choice.
Each literal choice arm or literal tag field in a map arm additionally generates a C `#define` whose replacement value uses the generated literal form specified above.
The macro name is `LOGOS_LITERAL_<stem>`, using the literal node's complete semantic stem from Section 2.1.
This ordinary C constant preserves the literal value for reverse mapping.

For example, the tagged `storage.entry` choice above includes constants equivalent to:

```c
#define LOGOS_LITERAL_storage_Entry_AR_File_Kind "file"
#define LOGOS_LITERAL_storage_Entry_AR_Dir_Kind "dir"
```

### 2.4 Method Mapping

A request/response pair maps to a Logos module C function:

```cddl
storage.exists_request = {
    cid: tstr,
}
storage.exists_response = {
    exists: bool,
}
```

maps to:

```c
typedef logos_result_t (*logos_storage_Exists_FN_t)(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    const char*             in_cid,
    bool*                   out_exists
);

logos_result_t logos_storage_module_CALL_storage_Exists(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    const char*            in_cid,       /* from request map */
    bool*                  out_exists    /* from response map */
);
```

**Rules:**

1. First parameter is always `logos_module_context_t* module`.
   The module returned this opaque per-instance context from its lifecycle initializer.
   The ABI caller MUST pass the same context to every instance-dependent call for that initialized module instance.
   The second parameter is always `logos_response_owner_t* response_owner`, including for empty response maps.
   Both parameters are ABI state and do not represent schema fields.
2. When the request body is a map, its fields expand to input parameters in canonical field-name order.
   Names are derived from the CDDL key and prefixed with `in_`.
3. When the response body is a map, its fields expand to output parameters in canonical field-name order, appended after all input parameters and prefixed with `out_`.
4. When the request body is a choice of maps, the generator emits the request declaration as the named choice aggregate `logos_<namespace>_<Method>_request_t` and uses one `const logos_<namespace>_<Method>_request_t* in_request` input parameter instead of flattening its arms.
5. When the response body is a choice of maps, the generator emits the response declaration as the named choice aggregate `logos_<namespace>_<Method>_response_t` and uses one caller-allocated `logos_<namespace>_<Method>_response_t* out_response` output parameter instead of flattening its arms.
6. A scalar response field uses a pointer to its canonical C scalar type.
   An unconstrained `tstr` response field uses `const char** out_<name>`.
   An exact-size or ranged `tstr` response field uses a pointer to its canonical constrained typedef, such as `logos_tstr_size_1_64_t* out_<name>`.
   Both forms expose response storage governed by Section 2.7.
7. If the response map is empty (`{}`), there are no schema-derived output parameters.
   `result.code == LOGOS_OK` indicates that the invocation produced the valid empty response.
8. Unbounded and ranged `bstr` fields expand to adjacent pointer-and-length parameters.
   A ranged byte string uses its canonical constrained pointer typedef.
   A positive exact-size byte-string input uses `const uint8_t (*in_<name>)[N]`, and its caller-allocated output uses `uint8_t (*out_<name>)[N]`.
   An exact-size byte string has no length parameter.
9. A variable-length list input uses adjacent `const <type>* in_<name>` and `size_t in_<name>_count` parameters.
   Its output uses adjacent `<type>** out_<name>` and `size_t* out_<name>_count` parameters.
10. Method parameters with struct representations, including empty values, use the pointer forms defined in Section 2.3.
11. The function always returns `logos_result_t` as its invocation status.

Every parameter in a flattened field's representation uses its direction prefix, including presence flags, lengths, counts, and tuple components.
The prefix is applied once, after field expansion, and does not change schema field names or aggregate member names.
For example, request fields `module` and `out_value` use `in_module` and `in_out_value`, and `? data: bstr` uses `in_has_data`, `in_data`, and `in_data_len`.

The choice aggregate and all inline map arms use the declaration and inline-path naming rules in Sections 2.1 and 2.3.
The wrapper parameter belongs to the method ABI and does not add a map or field to the wire value.
If only one method half is choice-valued, only that half uses a wrapper; an ordinary map-valued half remains flattened.

For example, the following choice-valued request and map-valued response:

```cddl
storage.resolve_request =
    { kind: "by-id", id: uint64 } /
    { kind: "by-name", name: tstr }

storage.resolve_response = {
    matched: bool,
}
```

maps to a method signature using the generated request choice:

```c
typedef logos_result_t (*logos_storage_Resolve_FN_t)(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    const logos_storage_Resolve_request_t* in_request,
    bool* out_matched
);
```

Every method generates a defining-contract function typedef named
`logos_<namespace>_<Method>_FN_t`.
An interface contract header contains this typedef without claiming a concrete provider symbol.
A concrete provider header declares `logos_<module-C>_CALL_<namespace>_<Method>` with exactly the typedef's return type and parameters.
The provider declaration attaches that complete contract method to the concrete module;
the typedef makes the interface contract independently representable in ordinary C.

For an optional request field `x`, the input parameters are adjacent `bool in_has_x` and the ordinary input representation of `x`.
For an optional response field `x`, the output parameters are adjacent `bool* out_has_x` and the ordinary output representation of `x`.
The value parameter is ignored when its presence flag is false.
This is the function-parameter form of the same `has_<field>` convention used by structs.

Schema-defined outcomes, including expected failures, use the response output parameters
and require `result.code == LOGOS_OK`.

Before invoking a per-method provider function,
the ABI caller MUST initialize the response owner and every object designated by a response output parameter as if by a C `{0}` initializer.
The `response_owner` parameter MUST point to a distinct writable owner object.
A return with `result.code == LOGOS_OK` requires complete canonical response outputs and a valid response owner as defined in Section 2.7.1.
Successful completion transfers that owner to the ABI caller.
A response requiring no resource release MUST use an empty owner.
A return with a nonzero result code requires the owner and every response output to remain at their caller-initialized values and transfers no output ownership.
Before returning such a failure, the provider MUST release every allocation or other output resource created while processing the call.
The ABI caller MUST treat any other result/output combination as a module failure
and MUST NOT dereference or free an output pointer written by the failing call.
It MUST NOT invoke a release callback supplied by the failing call.

**Note on authoring convenience:** Module authors using a module kit may write
simpler implementation functions with native return types, existing state
parameters, or language-specific bindings.
The module kit wraps these into the canonical `logos_result_t`-returning form.
This is an implementation convenience:
the exported Logos module C functions MUST conform to the signatures specified
here.

**More examples:**

```cddl
storage.space_request = {}
storage.space_response = {
    info: storage.space_info,
}
```

```c
logos_result_t logos_storage_module_CALL_storage_Space(
    logos_module_context_t*     module,
    logos_response_owner_t* response_owner,
    logos_storage_Space_info_t* out_info
);
```

```cddl
storage.upload_url_request = {
    url: tstr,
    chunk_size: uint64,
}
storage.upload_url_response = {
    accepted: bool,
}
```

```c
logos_result_t logos_storage_module_CALL_storage_Upload_url(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    uint64_t               in_chunk_size,
    const char*            in_url,
    bool*                  out_accepted
);
```

### 2.5 Event Type Mapping

An event with a map body uses the map layout from Section 2.3 and the canonical `_EVENT` aggregate tag.
An event whose body is a choice of maps uses the ordinary choice representation from Section 2.3, including its `_CHOICE` aggregate tag, discriminant, arm constants, and map-arm types.
The owner retains its complete `_event` suffix in both forms.
The choice form adds no outer wrapper or wire field.

The following example has a map body:

```cddl
storage.upload_progress_event = {
    bytes_sent: uint64,
    bytes_total: uint64,
    session: tstr,
}
```

```c
typedef struct logos_storage_Upload_progress_event_EVENT {
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
    const char* session;
} logos_storage_Upload_progress_event_t;
```

The route-handle vtable in Section 5.2 defines
`subscribe` and `unsubscribe` operations,
`logos_subscription_id_t`,
and `logos_event_handler_t`.
These operations act on a consumer-bound exact-contract route.
They are caller-side binding operations,
not module ABI symbols exported by a provider implementation.
`event_name` MUST be the exact schema event identifier selected by the route.
The event MUST be allowed by the route's allowed event scope.

The route `subscribe` operation returns `LOGOS_OK` only after the subscription is active.
On success, it MUST write an identifier scoped to that route into `*out_subscription_id` before activation.
The caller MUST make `handler` and `user_data` ready for concurrent use before calling `subscribe`.
After activation, another thread MAY begin a handler invocation before `subscribe` returns.
The `subscribe` operation MUST NOT invoke that subscription's handler synchronously on the subscribing thread.
On failure, it creates no subscription, MUST NOT invoke `handler`, and MUST NOT modify `*out_subscription_id`.

For each subscription, handler invocations MUST begin in direct publication order or in Event commitment order for Transport delivery.
The binding MUST NOT begin a handler invocation on one thread
while an invocation for the same subscription remains active on another thread.
Same-thread handler re-entry is permitted only when an action during a callback
synchronously causes nested direct publication for the same subscription.
Handlers for distinct subscriptions MAY run concurrently.

The callback's `event_name` and `cbor_data` are borrowed only for that invocation.
`cbor_data` MUST contain exactly one complete Logos deterministic-CBOR map
that matches the selected event-data type.
A handler MUST copy borrowed data that it needs to retain.

An external route `unsubscribe` operation returns `LOGOS_OK` only after
the subscription is inactive,
every active handler invocation has returned,
and no later invocation can begin.
While an external unsubscription is pending, the binding MAY pause handler admission for that subscription.
If unsubscription succeeds, the binding MAY discard received events whose handler invocation has not begun.
If it fails while the route remains ready, the pending operation MUST NOT itself discard those events or remove their eligibility for handler delivery.
Transport protocol validation and correlation remain required even when local handler delivery is suppressed.
If a handler invokes the route `unsubscribe` operation
for its own subscription through the same route handle,
the binding MUST deactivate the subscription before returning
but MUST NOT wait for handler frames already active on the calling thread.
Those frames remain valid until they return.
An unsubscription failure MUST NOT itself change the subscription state.

A subscription exists only while its route is ready.
When the route enters a terminal state,
the binding MUST deactivate every subscription on that route
and MUST NOT begin another handler invocation.
Route-handle release MUST wait for every active handler invocation to return.

The caller MUST keep `handler` and `user_data` valid until an external unsubscription returns `LOGOS_OK`,
a self-unsubscription returns `LOGOS_OK` and every handler frame active during it has returned, or route-handle release returns.

Direct delivery follows Section 2.8.
A transported binding maps these operations to the subscription lifecycle
defined by LOGOS-MODULE-TRANSPORT.

The route handle also provides `observe_end` for local termination notification.
This binding operation reports loss of the handle's invocation path; it is not a provider event declaration or privileged Runtime Control observation.
It requires no additional observation authority and MUST be supported in every invocation mode.

`observe_end` accepts one non-null `logos_route_end_handler_t` and its user state.
`LOGOS_OK` installs one registration for the handle's existing invocation-path generation.
The binding MUST order installation with termination so a successful registration cannot miss an observed terminal transition while the consumer execution envelope remains live.
The caller MUST make callback state ready before registration.
The operation MUST NOT invoke the callback synchronously on the registering thread; another thread MAY begin it after installation and before the operation returns.
A null handler or a second registration returns `INVALID_PARAMS`; unavailable local registration capacity returns `MODULE_ERROR`.
A failed registration MUST NOT invoke or retain the supplied callback state or alter an existing registration.

When the bound invocation path first becomes terminal, the binding MUST stop admission of new event handlers and retain a nonzero termination code.
Known authority withdrawal or expiry uses `NOT_AUTHORISED`; otherwise explicit route closure or known provider/readiness loss uses `NOT_READY`.
Connection failure without a known authorization or readiness cause uses `TRANSPORT_ERROR`.
The binding MUST apply the caller-facing non-disclosure rules and MUST NOT infer a remote cause from connection loss.
The code records the first terminal transition and MUST NOT be replaced when a later cause becomes known.
Registration on an already-terminal handle returns that code without installing a registration or invoking its callback.

An installed callback receives the retained code exactly once unless handle release suppresses a callback that has not begun.
Notification MUST NOT require a subsequent call or polling by the consumer.
This requirement establishes no deadline for detecting a silent connection failure.
A replacement connection or provider MUST NOT revive the handle or its registration.
Termination notification does not imply that already admitted event handlers or asynchronous call completions have returned.
It imposes no ordering between their execution and the terminal callback.
The callback MAY run on the thread that detects termination, including during another binding operation.
It MUST NOT invoke operations on or release its own handle.

There is no separate unregister operation; callback state MUST remain valid until handle release returns.
Release MUST suppress terminal callbacks that have not begun and wait for active terminal callbacks as well as active event handlers.
It MUST NOT be invoked from an event or terminal callback for that handle or while holding a resource needed by those callbacks.
Local handle release does not itself emit a termination notification or close the logical route.
Prepared asynchronous calls retain their independent lifetime under Section 2.9.1.

A generator MAY produce a typed helper for each event, with implementation-defined helper and handler typedef names; for example:

```c
typedef void (*logos_storage_upload_progress_handler_t)(
    const logos_storage_Upload_progress_event_t* event,
    void*                                        user_data
);

logos_result_t logos_storage_on_upload_progress(
    logos_route_handle_t*                    route,
    logos_storage_upload_progress_handler_t  handler,
    void*                                    user_data,
    logos_subscription_id_t*                 out_subscription_id
);
```

A typed helper wraps the generic subscription surface,
uses the exact schema event identifier,
decodes each validated event map into the generated event struct,
and exposes that struct only for the typed callback invocation.

### 2.6 Module Lifecycle Symbols

This section classifies the C symbols that belong to the module ABI.

Every native module implementation MUST make these module identity and lifecycle symbols available to its ABI caller:

- `logos_<module-C>_MODULE_name()` returns the module name as a static string that
  remains valid for the implementation-binding lifetime.
- `logos_<module-C>_MODULE_init()` receives one structured initialization input and
  creates one module-owned context for one module instance.
- `logos_<module-C>_MODULE_destroy()` destroys one successfully initialized context.
The identity and lifecycle symbols do not make the module a provider.
`logos_<module-C>_MODULE_apply_configuration()` is the optional standard ABI hook for applying configuration after initialization.
A specification that assigns configuration semantics determines when the hook is required and defines its payload and outcome semantics.
A module that is not required to support live configuration application need not export it.

For native ABI classification, a provider contract is a concrete module or interface contract that declares at least one schema-defined method or event.

A native module that exposes at least one provider contract MUST additionally make these provider symbols available to its ABI caller:

- `logos_<module-C>_MODULE_call_surface()` returns one deterministic-CBOR provider
  call-surface descriptor containing the module's optional primary contract
  and every implemented interface contract;
- `logos_<module-C>_MODULE_free()` releases serialized response buffers transferred by this module instance through `_MODULE_dispatch()`;
- `logos_<module-C>_MODULE_dispatch()` dispatches a schema method name and deterministic
  CBOR request payload to the corresponding schema-defined method.
  It is a module ABI symbol, not a schema method.

Such a provider module MUST also make the schema-derived per-method C functions specified in section 2.4 available to its ABI caller.
The per-method C functions are the typed native provider ABI.
`logos_<module-C>_MODULE_dispatch()` is the generic deterministic-CBOR dispatch entrypoint.
It accepts a bare method name and deterministic-CBOR request bytes
and returns the final method result and response.
Provider modules MUST expose both surfaces,
which MUST implement the same request, response, error, and selected-contract semantics.
An events-only provider contract generates no schema-derived per-method functions.
For a provider whose complete contract set declares no methods, `_MODULE_dispatch()` MUST return `LOGOS_ERR_METHOD_NOT_FOUND` for every method argument.
A module with no provider contract MUST NOT be required to export
`_MODULE_call_surface()`, `_MODULE_free()`, `_MODULE_dispatch()`, or a schema-derived per-method function.

If a concrete module declares `_implements`,
its full Logos ABI MUST cover the primary module methods
and every implemented interface method.
Code generation is the expected path.
A hand-written module MUST expose behavior equivalent to the same concrete contract set.

`logos_<module-C>_MODULE_dispatch()` MUST NOT be listed as a method in the module schema,
`logos.schema` method listings, or generated call helpers.
It MUST NOT be used as the method identity for commitments, authorization,
audit records, or conformance vectors.
Those surfaces identify the target schema method selected by the `method` argument.
They also identify the contract root that defines that method
and the corresponding request, response, or error value.
For implemented interface methods, that defining contract root is the implemented interface contract root.
This remains true when the concrete module exports the ABI entrypoint that dispatches the call.

The well-known `logos.schema` method is defined by the pinned Logos common schema surface.
Its authorization identity is the `logos.schema` method declaration root under that common schema root.
The target provider and contract disclosed by the call remain bound to the selected route;
authorizing `logos.schema` on one route does not authorize introspection of another provider or contract.

Runtime Control access, the provider event-publication callback,
and the module-visible persistent-state directory are supplied in the structured initialization input.
Startup configuration, when present, is supplied in the structured initialization input.
The module MUST NOT export post-initialization callback setters.
Providing these bindings before initialization establishes one sequencing point and
prevents callback replacement while the module instance is processing work.

One accepted native implementation binding MAY be initialized more than once.
Each successful initialization creates a distinct live module instance and MUST
return a distinct non-null `logos_module_context_t*`.
The module owns the context and its ABI callers treat it as opaque.
The same pointer MUST be passed to every instance-dependent ABI call for that module instance.
During graceful release, the ABI caller MUST pass that pointer exactly once to `logos_<module-C>_MODULE_destroy()` and retain the implementation binding until the call returns.
Forced termination of the execution envelope MAY prevent `_MODULE_destroy()` from beginning or returning.
Termination of the execution envelope ends its process-local lifetimes.

For ABI preconditions, a module context is live from successful `_MODULE_init()` return
until the ABI caller begins that context's single `_MODULE_destroy()` call after quiescence or the execution envelope terminates.
`_MODULE_destroy()` consumes the live context.
The context is bound to that module instance and implementation binding.
Passing a null context, a context belonging to another instance or implementation,
or a context whose destruction has begun violates the caller's ABI precondition.
This specification assigns no `logos_error_code_t` value to that misuse
because no conforming ABI invocation occurs.
A higher-level binding MAY reject an invalid handle that it can identify
using its own precondition mechanism before entering the C ABI.
The native ABI does not require safe detection of an arbitrary forged or stale pointer.

The initialization input is borrowed only for the duration of `_MODULE_init()`.
The Runtime Control binding, publish callback, and opaque publish state remain valid and unchanged from `_MODULE_init()` entry until `_MODULE_destroy()` returns.
The state-directory string is borrowed only for the duration of `_MODULE_init()`.
The module MAY copy it into its context,
but it MUST NOT retain the supplied pointer.
The corresponding module-visible directory mapping remains established until destruction begins.
Configuration bytes are borrowed only for the duration of `_MODULE_init()`.
The module MAY copy or decode them into its module context, but it MUST NOT retain their pointer.
A module MAY copy those fields into its module context,
but it MUST NOT retain the initialization-input pointer itself.
A null publish callback is unavailable for that instance and MUST NOT be called.

Before calling `_MODULE_init()`,
the ABI caller MUST set `*out_context` to `NULL`.
Success requires `result.code == LOGOS_OK` and a non-null context.
Failure requires a nonzero result code and a null context;
the module MUST release any partially initialized instance state before returning.
The ABI caller MUST reject any other result/context combination.

The initialization input and returned context are instance state.
They MUST NOT change the implementation name, provider call-surface descriptor, or exact contract set reported by the context-free metadata symbols.
Native ABI concurrency is defined in Section 2.8.

The following declarations show the mandatory and recommended symbol
signatures:

```c
/* Module name (static string, valid for implementation-binding lifetime) */
const char* logos_<module-C>_MODULE_name(void);

/* Create one module instance from one structured initialization input. */
logos_result_t logos_<module-C>_MODULE_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

/* Apply one complete configuration to a live-reconfigurable module instance. */
logos_result_t logos_<module-C>_MODULE_apply_configuration(
    logos_module_context_t* module,
    const uint8_t*          configuration_cbor,
    size_t                  configuration_cbor_len
);

/* Destroy one successfully initialized module instance. */
void logos_<module-C>_MODULE_destroy(logos_module_context_t* module);

/* Provider-only call-surface metadata and memory-management symbols. */
const uint8_t* logos_<module-C>_MODULE_call_surface(size_t* out_len);
void logos_<module-C>_MODULE_free(logos_module_context_t* module, void* ptr);

/* Provider-only deterministic-CBOR dispatch entrypoint. */
logos_result_t logos_<module-C>_MODULE_dispatch(
    logos_module_context_t* module,
    const char*             method,
    const uint8_t*          params_cbor,
    size_t                  params_len,
    uint8_t**               out_response_cbor,
    size_t*                 out_response_len
);
```

`logos_<module-C>_MODULE_call_surface()` returns the deterministic-CBOR encoding of
exactly one `provider-call-surface` value:

```cddl
provider-call-surface = {
    ? primary: provider-contract-schema,
    interfaces: [* provider-contract-schema],
}

provider-contract-schema = {
    commitment: logos.schema_commitment,
    document: tstr .size (1..1048576),
    supporting_schemas: [* provider-supporting-schema],
}

provider-supporting-schema = {
    namespace: tstr .size (1..128),
    commitment: logos.schema_commitment,
    document: tstr .size (1..1048576),
}
```

The field names shown above are the deterministic-CBOR map keys.
The value MUST use the Logos deterministic CBOR profile in Section 4.4.
The complete encoded descriptor MUST be no larger than 8,388,608 bytes,
and `interfaces` MUST contain no more than 256 entries.
The descriptor MUST contain a `primary` value, at least one `interfaces` entry, or both.

The caller MUST pass a non-null `out_len`.
The function writes the descriptor length there and returns a non-null pointer to immutable bytes that remain valid for the implementation-binding lifetime.
Its concurrency requirements are defined in Section 2.8.
It MUST return the same bytes on every call for one native provider implementation binding.
The caller MUST NOT modify or free those bytes.
A null return, a zero length, malformed deterministic CBOR, or a value that
violates the descriptor limits makes the provider invalid.

Each `provider-contract-schema` carries one complete UTF-8 CDDL contract document,
the exact schema commitment claimed for that document,
and the complete ordered set of supporting schemas required to construct it.
The `primary` document MUST be a concrete module schema whose `_module` value
matches `logos_<module-C>_MODULE_name()`.
Each `interfaces` document MUST be an interface contract schema.
Its `_interface` value MUST equal its derived primary schema namespace.
Interface documents MUST NOT declare `_implements`.

An interface entry's `supporting_schemas` array MUST contain all and only the supporting schemas referenced by that interface document.
The primary entry's `supporting_schemas` array MUST contain all and only the supporting schemas referenced by its module document or its implemented interfaces.
A supporting schema required by multiple contracts occurs in each applicable descriptor entry; those occurrences MUST identify the same validated schema identity and contribute only one document to a construction input set.
Existing conflicting-definition and namespace checks apply to the complete construction input set.
Each supporting entry MUST contain a valid supporting schema.
Its `namespace` MUST equal the namespace derived from its document,
and its commitment MUST equal the recomputed schema commitment for that document.
Supporting entries MUST have distinct namespaces and schema roots
and MUST be ordered by namespace UTF-8 bytes and then schema-root bytes.

The ABI caller MUST parse and resolve every contract and supporting document under Section 5.3,
recompute every schema root,
and compare each result with its descriptor commitment before the provider is registered or invoked.
It MUST reject an unknown profile identifier, a root mismatch, duplicate
contract identity, duplicate interface namespace, missing or unused supporting schema,
invalid schema-role metadata, a reserved common-schema bare method name,
a bare method-name collision across the described contracts,
or an interface list that is not ordered by derived namespace UTF-8 bytes and then schema-root bytes.
The interface entries provide the exact resolved `_implements` set used when
constructing and validating the primary contract.
When a package, Runtime input, static registration, or protected built-in
declaration supplies contract references, its optional primary contract and
implemented-interface set MUST exactly match the validated descriptor.

The descriptor is provider metadata.
It is not a module schema, a route, a schema method, or an additional commitment input.
The complete descriptor has no synthetic schema root.
Every method, event, request, and response retains the defining contract root
of its own `provider-contract-schema` entry.

In **direct mode** (in-process), the ABI caller MAY call per-method functions directly.
In deterministic-CBOR and transport invocation paths, the ABI caller MAY call `logos_<module-C>_MODULE_dispatch()`.
For dispatch calls, `method` is the bare schema method name after the target
module has already been selected.
`params_cbor` is the deterministic CBOR request map for that method, not the
full Transport Request envelope.
Before calling `_MODULE_dispatch()`, the ABI caller MUST set `*out_response_cbor` to `NULL` and `*out_response_len` to zero.
Success requires `result.code == LOGOS_OK`, a non-null response buffer, and a nonzero length containing exactly one valid deterministic-CBOR response map for the selected method.
Failure requires a nonzero result code, a null response buffer, and a zero response length.
Before returning such a failure, the module MUST release any response allocation created while processing the call.
The ABI caller MUST treat any other result/output combination as a module failure
and MUST NOT dereference or free an output pointer written by the failing call.
The returned response buffer is released with
`logos_<module-C>_MODULE_free(module, out_response_cbor)`.

Dispatch itself is synchronous.
An ABI invocation path handles independent requests asynchronously by invoking separate dispatch calls concurrently, commonly on a worker pool.
It correlates each returned response with its originating request.
Those calls may return in any order.
Both direct and dispatch paths are equivalent
only when they preserve the same target schema method and defining contract root.
They are not equivalent if they change the request value,
response value,
error behavior,
or authorization boundary.

**Important distinction: lifecycle `_MODULE_init()` vs schema method `init`.**

The lifecycle symbol `logos_<module-C>_MODULE_init(input, out_context)` is part of the native module ABI.
The ABI caller calls it after binding the native implementation and before any instance-dependent ABI entry point is invoked.
It creates instance state and receives the Runtime services available to that instance.

If a module schema also declares an ordinary method named `init` (for example
`storage.init_request` / `storage.init_response`), that method is a normal
schema-defined request/response method with C symbol
`logos_<module-C>_CALL_<namespace>_Init` and wire method name `"init"`. It is distinct from
the lifecycle symbol and MAY perform application-level setup
that remains necessary after lifecycle `_MODULE_init()` has succeeded.

Successful lifecycle `_MODULE_init()` therefore means:

- the module instance has created a valid context from the supplied initialization input;
- every Runtime service required during native initialization was available; and
- when provider ABI entry points apply,
  ABI callers may invoke them using that context.

It does **not** mean that every schema-defined method's application-level preconditions already hold.
A method that requires application-level setup MUST represent an expected unavailable outcome in its response schema.
It MUST NOT use `LOGOS_ERR_NOT_READY` for application state.
`LOGOS_ERR_NOT_READY` is reserved for an invocation failure caused by Runtime-owned readiness.

### 2.7 Memory Management

Memory-management behavior is normative wherever ownership crosses the module
boundary.
Without this, independently implemented runtimes and modules cannot safely
interoperate.

The provider ABI uses response owners for typed response storage and a module-owned deallocation function for serialized dispatch response buffers:

```c
void logos_<module-C>_MODULE_free(logos_module_context_t* module, void* ptr);
```

**Lifetime rules:**

- The module context remains owned by the module from successful `_MODULE_init()` until `_MODULE_destroy()`.
  ABI callers borrow it and MUST NOT dereference, modify, serialize, or free it.
- Synchronous request arguments are borrowed until the provider C function returns.
  The provider MUST NOT retain them.
  Deferred invocation inputs and completion owners follow Section 2.9 instead.
- The `message` and `detail` storage referenced by a returned `logos_result_t` MUST be isolated from ABI calls executing concurrently on other threads.
  It remains valid until the next ABI call into the implementation that returned the result begins on the calling thread, until `_MODULE_destroy()` begins for an instance-dependent provider result, or until the applicable implementation binding is released, whichever occurs first.
  The ABI caller MUST copy `message` and `detail` before that point if it needs to retain, encode, or forward them.
  A call on another thread does not shorten this lifetime or modify the referenced storage.
- A successful dispatch transfers ownership of `out_response_cbor` to the caller.
  The caller releases it with the same module instance's `logos_<module-C>_MODULE_free(module, ptr)`.
  A failed dispatch transfers no output ownership.
- For Runtime Control bindings, route handles, and generated caller helpers,
  `logos_result_t.message` and `.detail` follow the same calling-thread lifetime.
  Callers MUST copy these fields before the next call into the returning implementation on that thread if they need to retain them.
- On a successful typed provider call, the response owner governs all backing storage referenced by the response outputs, including nested and recursive values.
  The caller MUST clear that owner after its final use of the response.
  It MUST NOT pass individual typed response pointers to `logos_<module-C>_MODULE_free`.
  A failed typed provider call transfers no output ownership.
- Outer output objects are caller-allocated.
  The provider fills them on success; their referenced backing storage follows the response-owner lifetime.
  The response owner MUST NOT depend on the addresses of those outer output objects.
- The provider MUST NOT return references to expired input borrows or temporary storage.
  Retaining a library object is sufficient only when it preserves every referenced region for the response lifetime.
- If response validation, copying, or encoding fails after successful transfer, the caller MUST still clear the owner.
  The caller MUST copy any required invocation diagnostics before clearing the owner.
- `_MODULE_name()` returns a static string, and `_MODULE_call_surface()` returns static bytes.
  Callers MUST NOT free any of them.
- `logos_<module-C>_MODULE_free(module, NULL)` MUST be a no-op.

The response owner selects the release operation for typed response storage.
Serialized dispatch response buffers use the deallocator from the same module instance that produced them.
Across process, sandbox, container, or remote boundaries, raw pointers do not
cross the boundary; the side that decodes serialized data owns and frees its
own decoded allocations.

### 2.7.1 Response Owners

A response owner controls the lifetime of storage backing one completed response.
The shared `logos_types.h` environment MUST provide this fixed ABI type:

```c
typedef struct logos_response_owner {
    void* state;
    void (*release)(void* state);
} logos_response_owner_t;
```

A response owner is process-local ABI state, not a schema value.
It MUST NOT be serialized or included in schema identity.
An empty owner has both members set to null pointers.
A nonempty owner MUST have a non-null `release` function; its `state` MAY be null.
The release function MUST accept that owner's state and release all resources held by the owner without propagating an exception across the ABI.

The owner MAY retain library objects, reference-counted storage, an arena, or independently allocated values.
Pointers into that storage MAY alias or identify interior regions.
Every referenced region MUST remain readable and unchanged until the owner is cleared.
Static storage MAY back a response without a resource release operation.
These lifetime rules do not relax canonical value representation, validation, or resource limits.

The caller MUST retain the implementation binding and any module instance required by the response storage or release function until clearing completes.
The caller MUST NOT separately free storage governed by the owner.
The release function MUST NOT free caller-owned outer output objects.
Copying an owner does not acquire another ownership right.
The caller MUST NOT clear an owner concurrently with reading its response or with another operation on that owner.
Release functions for distinct owners MUST support concurrent invocation, including from threads other than the originating call thread.

The shared header MUST provide the following helper:

```c
static inline void logos_response_owner_clear(logos_response_owner_t* owner)
{
    logos_response_owner_t previous = *owner;
    owner->state = 0;
    owner->release = 0;
    if (previous.release != 0) {
        previous.release(previous.state);
    }
}
```

The helper requires a non-null pointer to a valid owner.
After clearing, pointers into released storage MUST NOT be used.
Clearing the same owner again without assigning another ownership right performs no release.
The helper resets only the owner; generated typed cleanup helpers also reset their response output locations.

### 2.7.2 Generated Typed Response Cleanup

A generated C call helper that exposes canonical response outputs MUST return a response owner through a caller-supplied `logos_response_owner_t* response_owner` parameter.
The initialization, successful transfer, and failure rollback requirements in Section 2.4 apply to that owner and the response outputs.

A helper that decodes a serialized response MUST provide an owner for its decoded storage.
It MUST NOT release decoded storage through the provider's `logos_<module-C>_MODULE_free` function.
It MUST release the serialized response buffer through the matching route or Runtime Control binding before returning.
Returned outputs MUST NOT reference that released buffer.
Decoded storage MUST remain valid independently of the route handle or Runtime Control binding used for the call.
Any allocator state and cleanup code required by the decoded owner MUST remain live until clearing completes.

A generator that provides such a call helper MUST also provide a matching typed cleanup helper.
The cleanup helper MUST clear the response owner and reset every response output object as if by a C `{0}` initializer.
It MUST NOT traverse or independently free response payload pointers.
Its arguments MUST identify the owner and output locations from the same completed call or their initialized empty state.
Calling it again on those reset locations MUST be harmless.
A cleared response need not be a schema-valid value.

Typed cleanup helpers follow the derived-helper boundary in Section 2.1.
The common `logos_response_owner_clear` helper releases ownership without resetting payload output locations.

### 2.8 Native ABI Concurrency

This section defines the complete concurrency contract visible to native module implementations and ABI callers.
Runtime scheduling mechanisms do not add requirements to that contract.

The context-free `_MODULE_name()` and `_MODULE_call_surface()` entry points MAY be called concurrently
with one another and with operations on any context from the same implementation binding.
The implementation MUST make those calls safe without caller-side serialization.

Distinct `_MODULE_init()` calls for the same implementation binding MAY execute concurrently.
Each successful call creates an independent context.
The implementation MUST synchronize state shared across contexts.
This concurrency permission does not shorten the diagnostic-result lifetime or relax the caller-side copy sequencing defined in Section 2.7.

After successful initialization,
the ABI caller MAY invoke schema-derived provider functions and `_MODULE_dispatch()` concurrently with the same live context.
`_MODULE_apply_configuration()` MAY execute concurrently with provider calls,
but the ABI caller MUST NOT invoke two `_MODULE_apply_configuration()` calls concurrently with the same context.
The module MUST synchronize its per-instance state.
A module that requires serial execution MAY implement internal serialization;
the ABI caller is not required to serialize provider calls.

`logos_<module-C>_MODULE_free(module, ptr)` MAY be called from any thread
and concurrently with other calls using the same live context.
The module MUST synchronize its allocator state.

Operations through one Runtime Control binding, except its release, MAY be initiated concurrently from multiple module threads.
The binding implementation MUST make those operations thread-safe
while preserving the operation ordering defined by LOGOS-MODULE-RUNTIME.

The module MAY invoke its publish callback concurrently from multiple threads while its context remains live.
The callback implementation MUST be thread-safe.

In direct mode, a publish call MUST invoke every applicable direct subscriber callback synchronously
on the publishing thread before the publish call returns.
The callback interval therefore applies natural backpressure to the publisher.
An implementation MUST NOT move a direct subscriber callback to another thread
or return from publication before that callback completes.
For invocation-scoped publication, applicability is determined separately before each callback admission under LOGOS-MODULE-RUNTIME Section 7.3.1.
An invocation cutoff reached during a re-entrant callback prevents admission of subsequent callbacks through that destination.

Direct publication is a re-entrancy boundary.
The publishing module MUST NOT assume
that its context cannot be entered through another allowed ABI path
before the publish call returns.
It MUST synchronize its state without deadlocking such conforming re-entry.

Transported delivery follows LOGOS-MODULE-TRANSPORT
and does not change the synchronous rule
for direct subscribers reached by the same publication.

These requirements do not make a route handle intrinsically thread-safe.
A caller MUST externally serialize operations on one route handle.
Operations through distinct route handles MAY execute concurrently.
The self-unsubscription operation defined in Section 2.5
is the only exception to same-handle serialization.
Every other operation initiated by a handler MUST use a distinct route handle
or wait until the handler returns.

Typed provider functions and `_MODULE_dispatch()` execute synchronously on their calling thread.
The optional submission capability and consumer asynchronous calls follow Section 2.9.
Transported invocation may enter the provider on different threads
and may complete independent calls out of order.
A module MUST NOT depend on a fixed provider-call thread
or on Runtime-provided call serialization.

Before `_MODULE_destroy(module)` begins,
the ABI caller MUST finish the deferred-invocation drain defined in Section 2.9.2,
stop new instance-dependent calls,
wait for every in-flight call to return,
and release every transferred output associated with the context.
`_MODULE_destroy()` MUST NOT execute concurrently with another call using that context.
Before `_MODULE_destroy()` returns,
the module MUST stop or join internal work
that could later use the context, Runtime Control binding, publish callback, or publish state.
The module MUST release every Runtime Control or route response buffer it owns before `_MODULE_destroy()` returns.
It MUST also unsubscribe every Runtime Control subscription it created and release every route handle it owns.
Releasing those handles deactivates their remaining route subscriptions.
After `_MODULE_destroy()` returns, none of those values remains valid.

---

### 2.9 Asynchronous Invocation and Protected Context

Asynchronous invocation changes native execution and completion, not the selected method, contract identity, payload schemas or commitment rules.
Runtime Control and route bindings MUST provide `prepare_call` through the version-2 vtables in Section 5.2.
The optional provider `_MODULE_async_api()` capability permits native provider completion after submission returns.
A Runtime MUST support asynchronous consumer calls even when a provider supplies only the synchronous provider ABI.
It MAY adapt that ABI using implementation-owned scheduling; it MUST NOT implement asynchronous submission by waiting for synchronous provider execution on the submitting thread.
This requirement does not prescribe an executor, worker count, queue or language future type.

**Invocation lifetimes (informative).**

These boundaries are distinct; Sections 2.7 and 2.9.1 through 2.9.3 define their requirements.

| Boundary | What ends | What may remain |
| --- | --- | --- |
| Consumer completion callback returns | That callback's execution | Provider execution and transferred response ownership |
| `execution_release` | Provider's retained invocation access and new entry admission through it | Already admitted native entries and residual backend work |
| Response owner is cleared | That owner's retention of response storage and cleanup code | Other owners, provider execution and the logical route |
| Consumer call `release` returns | Call-handle lifetime and its completion callback | Provider execution and independent event subscriptions |

#### 2.9.1 Consumer Calls

A consumer expecting invocation-scoped events for a call should subscribe and prepare that call through the same route handle.
Pooling separately materialized handles does not itself establish a shared invocation path.

`prepare_call` accepts the same method and deterministic-CBOR request as the binding's synchronous `call`, plus options, completion callback state and a caller-allocated output handle.
The caller MUST initialize the output handle's vtable and state pointers to null.
Preparation MUST copy the method, request bytes, options and callback descriptor that it retains.
It MUST NOT execute provider code or invoke the completion callback.
Success returns a non-null vtable and state for one unsubmitted call.
Failure returns no call, leaves both output pointers null and invokes no callback.
Preparation failures use the existing invocation-failure codes; unavailable local preparation capacity uses `MODULE_ERROR`.
Preparation grants no authority and does not reserve an authorization decision for later use.

The prepared call MUST retain its binding's consumer, selected provider, exact contract and invocation-path generation independently of the caller's handle storage.
For a route handle with an active subscription, preparing and submitting a call MUST use that subscription's existing invocation path or fail without provider dispatch.
It MUST NOT silently create another session, reconnect or substitute a provider.
Binding release does not close the logical route or release a prepared call; it retains its existing effects on subscriptions.
The caller MUST release every call before its own module destruction returns.

The caller invokes `submit` exactly once, except when discarding an unsubmitted call through `release`.
The callback and its user state MUST be ready before submission.
Submission has no result-return channel.
Every outcome after submission, including local rejection, is reported through exactly one completion callback while the consumer execution envelope remains live.
The callback MAY begin on any thread, including inline before `submit` returns.
It MUST NOT overlap another completion callback for the same call.
Returning from `submit` does not establish that the invocation completed.
Runtime MUST repeat the applicable route, admission and authority checks before dispatch.

When `has_timeout` is true, `timeout_ms` is a duration measured from submission using a monotonic clock.
A zero duration expires immediately without provider dispatch.
When `has_timeout` is false, this option adds no caller-selected deadline.
Applicable policy, route lifetime and execution-envelope failure may still end delivery earlier.
The timeout begins at submission, not preparation, and does not require clock synchronization across a Transport boundary.

Runtime MUST serialize acceptance of a valid final result with local cancellation, timeout and binding-failure outcomes for the call.
Only the first terminal decision may begin its completion callback.
Local cancellation produces `CANCELLED`; expiration of the caller-selected duration produces `TIMEOUT`.
Neither outcome waits for a remote acknowledgement or provider termination.
An already selected terminal outcome is not replaced by a later cancellation or timeout.
Cancelling an unsubmitted call records cancellation; subsequent submission completes it as cancelled without dispatch.
Cancelling a completed call has no effect.

When an admitted request still has a live Transport session, Runtime MUST arrange Cancel processing under LOGOS-MODULE-TRANSPORT or terminate the affected session under its existing failure rules.
Local abandonment does not remove protocol validation or correlation obligations for late traffic.
Runtime MUST retain bounded state and resources until their actual uses end, even after the consumer callback has completed.
A local timeout does not prove that the provider observed cancellation.
Existing event subscriptions remain independent: completing or releasing this call does not suppress their callbacks, and Event messages carry no automatic per-call correlation.

`submit` and `cancel` on one call MAY overlap; Runtime MUST make that overlap safe.
The caller MUST stop new call operations and wait for active `submit` and `cancel` entries to return before invoking `release`.
Release of an unsubmitted call discards it without invoking the completion callback.
Release of a submitted call establishes local cancellation if no terminal outcome exists and waits for that call's completion callback to return.
Release MUST NOT wait for provider execution or remote cancellation acknowledgement.
It MUST NOT be called from the call's own completion callback or while holding a resource needed by that callback.
After release begins, the caller MUST NOT use the call again.
Callback state may be reclaimed after release returns.
This rule does not replace subscription callback lifetimes from Section 2.5.

Successful completion supplies exactly one validated deterministic-CBOR response with a non-null pointer and nonzero length.
Failure supplies a nonzero result code, a null response pointer and zero response length.
The completion callback receives ownership of `owner`, covering every referenced response and diagnostic byte.
An owner may accompany failure diagnostics.
The receiver MUST clear that owner after its final use, including when it discards the result.
The owner MUST retain all necessary storage, allocator state and cleanup code independently of call or route-handle release.
A zero owner is valid only when all referenced storage and code remain valid without retained ownership.
The binding MUST wrap provider ownership when necessary to satisfy this lifetime.
Sensitive payload cleanup follows Section 1.4.1 through the last actual use.

#### 2.9.2 Provider Completion

When the provider-side boundary observes terminal loss of an outstanding invocation's route, provider session, consumer execution envelope, or protected system-service binding, it MUST mark that invocation cancelled and arrange the cancellation notification defined in this section.
Propagation MUST NOT depend on another publication or incoming request.
The indication does not establish backend termination or require rollback; existing ownership and in-flight completion rules still apply.
Loss of authority for an optional progress event alone MUST NOT cancel the method invocation.

A provider MAY export `logos_<module-C>_MODULE_async_api()` with the signature and descriptor in Section 5.2.
The getter is context-free and returns either null, indicating absence, or an immutable descriptor valid for the implementation-binding lifetime.
A non-null descriptor MUST have the supported version, sufficient initialized extent and a non-null `submit` operation.
`request_cancel` MAY be null.
The descriptor MUST remain unchanged and the getter MUST be safe under the metadata concurrency rules in Section 2.8.
An invalid supplied descriptor is an implementation-binding failure; it MUST NOT be invoked.

The capability applies to ordinary methods from the accepted provider call surface.
It MUST preserve their synchronous request, response, error and selected-contract semantics.
It does not replace mandatory typed functions or `_MODULE_dispatch()`.
Those synchronous surfaces MUST remain functional and MUST NOT fail merely because a deferred surface also exists.
A synchronous adapter MUST make progress without requiring the blocked ABI caller to service an executor.
Generated authoring helpers MAY derive these surfaces from shared provider logic.

Runtime constructs one provider invocation before calling the descriptor's `submit` operation.
The method, request bytes and protected context are Runtime-owned and remain available until provider execution ownership is released and every admitted native entry using them has returned.
The provider MUST NOT modify their storage or use them after those borrows end.
Submission may complete inline or return while backend work remains active.
Returning from native submission does not complete the invocation or release its execution ownership.

The provider MUST invoke `complete` exactly once, including when it observes cancellation, and MUST release execution ownership exactly once through `execution_release` after that completion.
Cancellation may already have ended consumer delivery; provider completion still discharges native ownership obligations.
`complete` consumes the supplied response owner on every path, including discarded late completion and failed result validation.
The supplied response owner governs the lifetime of every backing region referenced by `response_cbor`, `result.message` and `result.detail`, including when `result.code` is nonzero.
Those regions MUST remain readable and unchanged until the owner is cleared under Section 2.7.1.
The calling-thread lifetime for diagnostics returned by synchronous ABI functions does not apply to diagnostics transferred through `complete`.
It MUST NOT produce another consumer completion or Transport Response when the corresponding terminal outcome already exists.
A successful provider result is validated and committed through the ordinary Runtime boundary.
Provider success does not itself prove that the result was authorized, committed or received.
Use of a released invocation, or a second provider completion, violates the provider ABI preconditions.

`execution_release` relinquishes the provider's retained invocation access; it is not evidence that arbitrary backend callbacks or provider code have returned.
It MUST NOT synchronously destroy the module or unload its implementation binding.
Runtime MUST retain the invocation and module context through every already admitted native submission, cancellation hook, invocation operation and context operation.
The provider MUST synchronize its backend state with those entries and MUST NOT free state still used by one of them.
Ordinary lifecycle ownership still requires `_MODULE_destroy()` to stop or join residual internal work before returning.

Cancellation is a sticky state observable through the invocation context.
If `request_cancel` is present, Runtime MUST arrange one notification after cancellation becomes known and after native submission returns, unless execution ownership has already ended.
Cancellation-hook admission MUST be serialized with `execution_release`.
Runtime MUST claim an entry guard when admitting the hook; release closes admission to new guards.
An already admitted hook may enter afterward and retains the invocation, context and implementation binding until it returns.
The hook MUST tolerate completion or removal of its backend operation before entry and acquire a protected reference before using provider-private state.
It MUST return harmlessly when that operation no longer exists.
`execution_release` MUST NOT wait synchronously for an admitted cancellation hook; the entry guard defers reclamation independently.
Runtime MUST invoke the hook outside locks needed by completion or release and without requiring an ordinary provider-execution slot.
The hook MUST NOT wait for backend termination.
The provider SHOULD request cancellation of backend work when that work supports it; cancellation does not promise rollback.

Before module destruction begins, Runtime MUST stop new submissions, request cancellation or apply the permitted drain policy, and wait for retained invocation ownership and admitted native entries to end.
A provider MUST NOT depend on entering `_MODULE_destroy()` to make that invocation drain possible.
When work cannot quiesce, graceful release remains incomplete and the existing forced-termination and cleanup rules apply.
Neither a delivered cancellation nor a deadline permits reuse or destruction of still-referenced native state.

#### 2.9.3 Protected Invocation Context

The initialization input supplies an instance-bound `invocation_access` closure.
Its state and `current` operation remain valid through `_MODULE_destroy()` return, like the other initialization bindings.
The `current` operation MUST be safe when called concurrently from multiple module threads.
The module passes that state back unchanged and MUST NOT serialize it or use it as an identity.
`current` returns the borrowed context of the active authenticated provider entry for that instance, or null when no such entry exists.
Authenticated provider entries include schema-derived synchronous provider calls, `_MODULE_dispatch`, and the asynchronous provider descriptor's `submit` and `request_cancel` operations.
During `submit` and `request_cancel`, `current` MUST return the context supplied by that operation's provider invocation.
Nested entries MUST restore the preceding context when they return.
Unrelated threads and consumer callback execution MUST NOT inherit a provider's active invocation context.
The module MUST NOT retain a context returned by `current` beyond that provider entry.
Deferred provider work uses the explicitly supplied provider invocation's context instead.
No thread-local permission callback or borrowed synchronous frame may escape through that substitution.

The context's `caller`, `is_cancelled` and `publish` operations MAY execute concurrently while the caller holds a valid context borrow.
The implementation MUST retain invocation state through each admitted context operation, including direct publication that re-enters completion or execution release.
Before releasing retained execution ownership, the provider MUST prevent new uses of that ownership by its threads; already admitted operations retain their borrows until return.
Execution release closes admission through that retained ownership but MUST NOT synchronously wait for active context operations.
A cancellation query reports a stop request known at this boundary; it is not a query for current authorization or proof of stopped effects.

The context's `caller` operation supplies immutable authenticated origin information.
For `LOGOS_CALLER_MODULE`, Runtime and module-instance identifier views identify the ordinary consumer.
For `LOGOS_CALLER_SYSTEM_SERVICE`, the Runtime identifier identifies the invoking Runtime and the module-instance view is null with zero length.
Runtime defines these identity semantics; the native views do not create a schema declaration or another participant kind.
Identifier views contain UTF-8 bytes, without requiring a terminating null byte, and remain borrowed for the context lifetime.
A copied identity is factual information, not retained permission, a delegated capability or proof that a route remains usable.
Engine invocations retain their protected system-service binding authority and MUST NOT acquire a fabricated module identity.

The context's `publish` operation performs invocation-scoped publication under LOGOS-MODULE-RUNTIME Section 7.3.1.
It borrows its event identifier and payload only for the call.
`LOGOS_OK` means a valid publication was admitted through a live destination; zero matching subscriptions is permitted and success does not prove receipt.
Every direct callback actually admitted by this publication MUST return before `publish` returns.
A valid event outside the selected contract or permitted event scope produces `NOT_AUTHORISED`.
Malformed identifiers or payloads produce `INVALID_PARAMS`.
A known authority failure produces `NOT_AUTHORISED`; otherwise a closed invocation destination produces `NOT_READY`.
A surfaced connection failure uses `TRANSPORT_ERROR`, and an internal processing failure uses `MODULE_ERROR`.
A failure does not roll back delivery already committed to an earlier subscriber.
When the destination closes during fan-out, the operation reports the applicable failure after completing any active direct callback.
Returned diagnostic storage follows the synchronous lifetime rules in Section 2.7.

---

## 3. Canonical C-to-CDDL Mapping

This section defines the reverse direction from canonical C declarations to the Logos canonical schema model and CDDL.
The mapping input is an explicitly supplied set of header sources, identified by logical names, with one subject document or one module selected under Section 3.2.
The mapper MUST resolve contract-header includes under Section 3.2 and retain each supplied schema-bearing body and its macro definitions for validation.
It is a source-level C profile.
ABI-equivalent declarations are not interchangeable for reverse mapping when they erase a canonical typedef name, array bound, presence pair, or literal constant.

Both the declaration-only C form and the metadata-extended C form are valid schema-authoring inputs.
The reverse mapper MUST derive every unambiguous schema fact from canonical C declarations and MUST require schema-metadata constants only for the remaining facts identified by this section.
CDDL is the recommended authoring form when a contract requires substantial schema metadata, but the metadata-extended C form remains a complete C representation of every accepted schema set.
The reverse mapping is partial over the C language: a C header outside the allowed subset is not a conforming C contract.
This restriction does not limit the accepted CDDL schema set or the generated C representation of that set.

The fixed declarations supplied by `logos_types.h` form a predefined mapping environment, like the fixed-width types supplied by `<stdint.h>`.
They are available to every C contract but are not schema-authoring declarations in that contract.
The reverse mapper recognizes their canonical names without reconstructing their definitions.

### 3.1 Allowed C Subset

The reverse mapper accepts the canonical declaration forms specified by Section 2, excluding its optional derived helpers.
The mapper MUST reject declarations outside the allowed subset rather than silently treating them as helpers.

The following table lists the accepted type mappings:

| C type | CDDL equivalent |
|--------|----------------|
| `bool` | `bool` |
| `uint8_t` | `uint8` |
| `uint16_t` | `uint16` |
| `uint32_t` | `uint32` |
| `uint64_t` | `uint64` |
| `int8_t` | `int8` |
| `int16_t` | `int16` |
| `int32_t` | `int32` |
| `int64_t` | `int64` |
| `const char*` | `tstr` |
| `const uint8_t*` + `size_t` (pair) | `bstr` |
| `logos_tstr_size_<n>_t` | `tstr .size n` |
| `logos_tstr_size_<min>_<max>_t` | `tstr .size (min..max)` |
| `logos_bstr_size_<min>_<max>_t` + `size_t` | `bstr .size (min..max)` |
| `uint8_t[N]`, where `N > 0` | `bstr .size N` |
| `logos_bstr_size_0_t` | `bstr .size 0` |
| `logos_tuple_size_0_t` | `[]` |
| `logos_<namespace>_<Type>_t` | Named schema type |
| Fixed `logos_<common-name>_t` from `logos_types.h` | Reference to the corresponding pinned common type |
| `const logos_<namespace>_<Type>_t*` in a recursive aggregate component | Recursive named aggregate reference |
| `const T*` + `size_t` (pair) | `[* T]` (array) |
| `logos_result_t` | (return type only; maps to invocation status) |
| `logos_module_context_t*` | (first param only; not in CDDL) |
| `logos_response_owner_t*` | (second method param only; not in CDDL) |

The mapper recognizes canonical choice discriminant typedefs, arm constants and unions, tuple members, and constrained typedefs only in the forms defined by Section 2.
Literal macros also admit the equivalent scalar forms specified in Section 3.5.
It also accepts the C mapping revision and commitment-context checks defined in Section 2 and the document identity checks defined in Section 3.2, and validates them without suppressing schema-bearing declarations.
It validates the complete declaration group before deriving schema nodes.
The mapper MUST accept the conditional linkage wrapper from Section 2 as non-schema syntax.

**Disallowed C constructs in the API surface:**

- `void*` (except for `logos_module_init_input_t.publish_user_data` and `logos_<module-C>_MODULE_free`)
- Raw pointers that are not part of a canonical text, byte-string, list, exact-array, recursive aggregate, output, context, or opaque-handle representation defined by this specification
- Function pointers other than the canonical generated method-signature typedefs
- `float` and `double` (reserved for a future deterministic numeric profile)
- Bitfields, bit-packed structs
- Authored enum declarations; fixed common enums belong to the predefined mapping environment.

Every accepted text argument is a valid UTF-8 NUL-terminated string.
An implementation that receives or constructs a text value containing U+0000 does not have a conforming canonical C value.
Schema-bearing declarations and constants MUST NOT vary with the compilation language or depend on conditional compilation other than a declaration guard.
The conditional linkage wrapper from Section 2 does not change those declarations or constants.

### 3.2 Contract and Namespace Recognition

Header packaging MUST NOT change schema identity.
An interface or supporting document MAY be supplied as a reusable header included by multiple provider headers.
The reusable header contains that document's schema declarations and required document metadata.
Provider-specific module metadata, lifecycle symbols, and provider function declarations belong to the provider header.

Schema reconstruction MUST identify one subject document and its complete required dependency set.
Module reconstruction MUST identify one module and reconstruct its optional primary document and each implemented interface with their complete required dependency sets.
The mapper MUST retain the recovered module binding alongside those documents.
Including multiple provider headers in a consumer compilation does not merge their subject documents.
Those providers are reconstructed independently.

Each supplied contract header MUST have a unique logical name.
Logical names are nonempty, case-sensitive, slash-separated relative paths with no empty, `.` or `..` components and no backslashes.
Contract-header includes MUST use literal quoted header names.
Each include name MUST be nonempty and relative, with no empty path components or backslashes.
The mapper resolves the name relative to the including header's logical directory, removes `.` components, and resolves `..` components.
Resolution above the logical root MUST be rejected.
The resolved name MUST match exactly one supplied logical name, byte for byte.
The mapper MUST NOT consult the filesystem, network, or compiler include-search paths.
Missing or ambiguous include targets MUST be rejected.
Repeated includes of one logical name refer to the same supplied header and MUST NOT bypass validation of its body.
The fixed common-header and allowed standard-header includes remain governed by Section 3.1 and are recognized before contract-header resolution.

Before suppressing repeated declaration groups, the reverse mapper MUST validate every supplied schema-bearing header body and reconstruct the relevant document identities.
Include guards and declared identity constants MUST NOT substitute for that validation.
Repeated groups for the same namespace MAY be reused only when their complete validated document identities and C mapping requirements agree.
Conflicting groups for the same namespace MUST be rejected within that reconstruction input.
Generated headers MUST also detect conflicting document identities when included in the same C translation unit; a truncated identity comparison is insufficient.

Document identity checks in generated headers are derived build-time checks, not schema metadata.
They MUST NOT affect reconstructed schema identity.
Hand-written C contracts MAY omit those checks.
When a supplied header contains such a check, the reverse mapper MUST reject any identity assertion that disagrees with the reconstructed document.
Tooling MUST be able to generate identity-checked headers from accepted C authoring inputs without requiring manually supplied schema roots.
Identity conflict checks MUST be evaluated before a guard can suppress a declaration group.

Generated headers MUST use `LOGOS_DOCUMENT_<namespace>_DEFINED` as the guard for each non-common document's declaration group.
Here, `<namespace>` is the document's C namespace component from Section 2.1, with its case preserved.
The group's complete schema root MUST be represented by four macros named `LOGOS_DOCUMENT_<namespace>_ROOT_<i>`, where `<i>` is `0`, `1`, `2`, or `3`.
Macro `<i>` encodes root bytes `8*i` through `8*i+7`, with byte zero being the first byte of the root and the first byte of each group being the most significant.
Each macro's replacement MUST be an unsigned hexadecimal integer literal consisting of `0x`, exactly sixteen lowercase hexadecimal digits, and the suffix `ULL`.

When the document guard is already defined, the header MUST check that all four root macros are defined and equal the corresponding expected literals.
It MUST issue `#error` if any macro is missing or differs, including when a missing macro's expected value is zero.
The header MUST then suppress the repeated declaration group.
When the guard is not defined, the header MUST define it with value `1`, define all four root macros, and emit the declaration group.
Root checks MUST use the commitment context checked under Section 2 and MUST NOT compare roots across different contexts.

Contract-header dependency includes and the mapping, context, and document identity checks MUST remain outside any enclosing guard that could suppress their evaluation.
Provider-specific module metadata, lifecycle symbols, and provider function declarations MUST NOT be suppressed by a shared interface or supporting-document guard.

These composition requirements apply to source reconstruction and compilation.
They MUST NOT impose a shared installed-header location, a runtime header dependency, or a global restriction on installed module contract versions.
Module installation, lifecycle, and route compatibility remain governed by their respective specifications.

A namespace group is the complete set of schema-derived declarations assigned to one exact schema namespace.
Declarations supplied by `logos_types.h` are excluded from namespace grouping because they belong to the predefined mapping environment.
An exact use of a fixed common type name reconstructs a reference to the corresponding declaration in the pinned `logos` common schema.
A C contract MUST include `logos_types.h` rather than redeclare a fixed common type.

When no document-role namespace constant is supplied and the header set contains exactly one non-common namespace group, the reverse mapper obtains the exact namespace by decoding the semantic stems under Section 2.1.
Every declaration MUST yield the same namespace.
The mapper derives the document role from its contents:

- A consistent `logos_<module-C>_MODULE_` lifecycle symbol family makes the document a concrete module schema and supplies `_module`.
- Without lifecycle symbols, at least one method or event makes the document an interface contract schema and supplies `_interface` from the inferred namespace.
- Without lifecycle symbols, methods, or events, the document is a supporting schema.

A types-only interface therefore requires interface-role metadata.
The declaration-only form cannot express `_implements` or more than one non-common schema document.

For every namespace group not covered by that inference rule, a document-role namespace constant supplies its exact namespace and role.
The reverse mapper MUST also accept an explicit document-role namespace constant when the namespace and role are recoverable from the declarations.
Provider lifecycle declarations MUST NOT override an explicit document role.
The projection of the constant's string value MUST equal the C namespace component of every declaration in that group.
For a primary-namespace constant, the macro's module component MUST equal the canonical module-name projection recovered from the lifecycle symbol family.
The mapper uses that name as the primary document's `_module` value.
For an interface- or supporting-namespace constant, the macro's namespace component MUST equal the case-preserving C namespace projection of its string value.

Each `LOGOS_IMPLEMENTS_<module-C>_INDEX<index>` constant names one complete interface group by its exact namespace.
The reverse mapper computes that interface's schema root and records the interface in the module binding.
When a primary document is present, the mapper emits the selected roots in its `_implements`.
Without a primary document, the mapper MUST NOT synthesize one or add `_module` or `_implements` to an interface document.
Each implementation constant's module component MUST equal the canonical module-name projection recovered from the lifecycle symbol family.
The indices MUST be contiguous and follow ascending raw interface-root order.
A referenced namespace group is not implemented unless an implementation constant names it.
A provider method declaration for a non-primary namespace requires the corresponding implementation constant.

The reverse mapper reconstructs `_sensitive` from each namespace group's sensitivity constants.
It MUST reject missing indices, incorrect ordering, duplicate names, or a name that does not identify a local request or response declaration in that group.
Absent sensitivity constants reconstruct an absent `_sensitive` declaration.

A primary- or interface-group reference to a type in a supporting group reconstructs an imported named-type reference to that supporting schema.
The reverse mapper computes the supporting schema root from the reconstructed group.
A fixed common type use always maps to a common-schema reference and never generates `_implements`.

The reverse mapper MUST reject any of the following:

- an incomplete namespace group;
- two conflicting definitions of the same qualified name;
- a method whose request or response half is missing;
- a missing required or conflicting document-role namespace constant;
- a document-role namespace constant whose exact value, projection, prefix, or role does not match its declaration group;
- inconsistent runtime module names in one module reconstruction;
- an implemented-interface constant without one complete matching group;
- a duplicate implemented interface;
- a provider declaration for a non-primary contract that lacks the corresponding implemented-interface constant;
- a supporting-schema group that contains a method or event declaration;
- a supporting-schema group supplied as a dependency but not referenced by the subject document or, during module reconstruction, its primary document or an implemented interface;
- a missing or non-contiguous implemented-interface index; or
- a generated-identifier or namespace-projection collision.

After recovering named aggregate references from canonical type names, the reverse mapper constructs the by-value representation graph defined in Section 2.3.
A `const logos_<namespace>_<Type>_t*` aggregate member is valid only when replacing that member with an ordinary by-value edge places its source and target in the same recursive component.
The mapper reconstructs that pointer as an ordinary named schema reference;
the pointer does not create optionality or a wire-level reference.
The mapper MUST reject an embedded value on a recursive edge and MUST reject recursive-pointer spelling on a non-recursive edge.

### 3.3 Function Signature Recognition

The codegen tool recognizes contract method typedefs by pattern:

```c
typedef logos_result_t (*logos_<namespace>_<Method>_FN_t)(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    <input params...>,
    <output params...>
);
```

The typedef reconstructs the defining request/response pair.
A concrete provider function is recognized by pattern:

```c
logos_result_t logos_<module-C>_CALL_<namespace>_<Method>(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    <input params...>,       /* in_ prefix */
    <output params...>        /* out_ prefix */
);
```

Every parameter after `response_owner` MUST use `in_` for the request or `out_` for the response.
All request parameters MUST precede all response parameters.

- The `logos_module_context_t*` first parameter is stripped (not in CDDL).
- The second parameter MUST be exactly `logos_response_owner_t* response_owner` and is stripped without creating a schema field.
- An exact `const logos_<namespace>_<Method>_request_t* in_request` parameter reconstructs a choice-valued request from its complete canonical named-choice declaration.
- An exact `logos_<namespace>_<Method>_response_t* out_response` parameter reconstructs a choice-valued response from its complete canonical named-choice declaration.
- Other input parameters with an `in_` prefix become request map fields.
- Other output parameters with an `out_` prefix and canonical output pointer types become response map fields.
- `logos_result_t` return is stripped (invocation status, not CDDL data).
- An adjacent `bool in_has_<field>` and ordinary input representation of `in_<field>` makes that request field optional.
- An adjacent `bool* out_has_<field>` and ordinary output representation of `out_<field>` makes that response field optional.
- Adjacent `_len` and `_count` parameters are consumed as part of their byte-string or list field.
- The namespace and method components identify the request/response qualified names; reverse the first-letter capitalization of `<Method>` and require canonical re-encoding.

A choice wrapper is valid only when its type name, qualifier, pointer form, parameter name, choice declaration, and inline arm declarations all match Sections 2.1 through 2.4.
The mapper MUST reject a wrapper mixed with flattened parameters for the same method half.
It MUST also reject a request or response choice declaration that is not consumed by the corresponding wrapper parameter.

A provider function MUST exactly match the corresponding defining-contract typedef.
Its decoded runtime module name attaches that contract method to the concrete provider but does not create another schema declaration.
The mapper MUST decode and validate `<module-C>` under Section 2.1.

**Parameter name to CDDL key:** validate and reverse any keyword escape on the complete identifier, remove exactly one direction prefix, then reverse the field expansion rules in Section 2.4.
The mapper MUST reject an unnecessary escape, including `in_class_` in place of `in_class`.
For example, `in_chunk_size` maps to request field `chunk_size`, `in_out_value` maps to request field `out_value`, and `out_value` maps to response field `value`.

**Example:**

```c
logos_result_t logos_storage_module_CALL_storage_Upload_url(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    uint64_t               in_chunk_size,
    const char*            in_url,
    bool*                  out_accepted
);
```

Generates:

```cddl
storage.upload_url_request = {
    chunk_size: uint64,
    url: tstr,
}
storage.upload_url_response = {
    accepted: bool,
}
```

Parameters MUST appear in the canonical field order required by Section 2.1.
The mapper MUST reject an unmatched presence, length, count, or output parameter.
A parameter identifier beginning with `in_has_` or `out_has_` MUST form the exact typed and adjacent presence pair above.
The mapper MUST reject any other such parameter and MUST NOT reconstruct it as a schema field.

### 3.4 Named Type and Struct Recognition

Canonical schema-value declarations with a namespace and owner but no inline path reconstruct named schema types.
An aggregate tag's kind suffix from Section 2.1 determines which schema construct it represents.
A `_MAP` struct with schema fields reconstructs a named map:

```c
typedef struct logos_storage_Space_info_MAP {
    uint64_t available;
    uint64_t quota;
    uint64_t used;
} logos_storage_Space_info_t;
```

Generates:

```cddl
storage.space_info = {
    available: uint64,
    quota: uint64,
    used: uint64,
}
```

Before reconstructing fields, the mapper MUST reverse the keyword escape on each complete member identifier.
A trailing underscore is an escape only when removing it yields a spelling in the fixed set from Section 2.1.
The mapper MUST reject an unescaped spelling from that set or an unnecessary trailing underscore.
Presence, length, count, tuple, and field-order checks MUST use the decoded identifiers and reconstructed schema field names.

Optional fields (those with a preceding `bool has_<field>`) generate
`? key: type` in CDDL.
Adjacent pointer-and-length or pointer-and-count members generate one byte-string or list field.
Members MUST appear in canonical field-name order, with each presence, length, or count member adjacent to the value it qualifies.
A struct member identifier beginning with `has_` MUST have type `bool`
and MUST immediately precede the member whose decoded name follows the prefix, or the first `x_0` member of the inline tuple field `x` identified by that decoded name.
For a nonempty inline tuple, the mapper MUST consume the complete adjacent positional group before reconstructing another field.
It MUST reject a presence flag on a later tuple component, a missing position, or an interleaved field.
The mapper MUST reject any other such member and MUST NOT reconstruct it as a schema field.
A canonical `_BSTR`, `_LIST`, or `_TUPLE` aggregate tag MUST contain only its corresponding `data` and `len`, `data[N]`, `items` and `count`, or `item_<index>` members, except for the empty-value forms in Section 2.3.
The mapper reconstructs an empty map, empty tuple, or exact-zero byte string from the aggregate tag and sole canonical `_empty` member.
It MUST reject an empty struct, a zero-length array, or any other use of `_empty` as a member name.

### 3.5 Choice and Literal Recognition

A canonical `uint32_t` discriminant typedef `logos_<stem>_KIND_t`, its complete arm constants, and matching `logos_<stem>_t` reconstruct one choice.
The mapper MUST reconstruct the arm schemas from their complete declarations and literal constants before deriving the labels and required symbolic or indexed form under Section 2.3.
It MUST validate the discriminant type, constant spellings and values, union members or their required omission, and all support paths against that form.
It MUST reject indexed form when symbolic form is required, symbolic form when indexed fallback is required, a duplicate or missing tag, or an out-of-range tag value.
The reconstructed schema uses canonical choice-arm order; C tag order does not change schema identity.
An inline composite type name reconstructs its owner and complete inline path rather than a new named CDDL declaration.
For every inline composite, the reverse mapper MUST reconstruct the candidate owner and path from aggregate containment and type use,
derive the exact canonical names under Sections 2.1 and 2.3, and require every tag, typedef, discriminant, arm constant, literal macro, and use site to match.
It MUST NOT recover a path merely by splitting a flattened identifier on underscores.
If containment yields no candidate path, more than one candidate path,
or two paths with the same derived identifier,
the mapper MUST reject the header set.

A canonical `LOGOS_LITERAL_<stem>` macro supplies the exact scalar value for every literal node,
including a choice arm or tagged-map tag field.
The reverse mapper MUST reject a missing literal macro, a replacement value of the wrong scalar type, or a macro whose arm and tag-field components do not match the associated choice declaration.

**Literal recognition.** The mapper MUST accept the generated forms from Section 2.3 and the handwritten forms below.
It MUST recover the same scalar kind and value from equivalent spellings, without changing the canonical schema model or schema identity.

| Scalar kind | Accepted handwritten forms |
| --- | --- |
| Boolean | `true` or `false`. |
| Integer | A decimal, octal, or hexadecimal integer constant, an `INTN_C` or `UINTN_C` invocation for `N` equal to 8, 16, 32, or 64, or one of the signed forms defined below. |
| Text | One or more adjacent ordinary C string literals, decoded and concatenated as specified below. |

Integer constants use decimal digits without a leading zero, a leading `0` followed by octal digits, or `0x`/`0X` followed by hexadecimal digits; `0` itself is valid.
A constant may have one `u`/`U` suffix and one `l`/`L` or `ll`/`LL` suffix in either order, or either suffix alone.
Digit separators and other integer prefixes or suffixes are outside this subset.
The value MUST fit `uint64`; outside a macro invocation, a decimal constant without `u`/`U` MUST also fit `int64`.
An `INTN_C` or `UINTN_C` argument MUST be one unsuffixed integer constant whose value fits the corresponding signed or unsigned N-bit range.

An integer constant or integer-macro invocation may have one unary `+` or `-`.
For unary minus, a bare constant MUST use decimal digits without a leading zero except for zero itself and MUST omit an unsigned suffix; alternatively, the operand may be an `INTN_C` invocation.
For unary minus, the magnitude MUST NOT exceed the maximum `int64` value.
These restrictions prevent unsigned negation from changing the reconstructed value.
The minimum `int64` value may also use `INT64_MIN` or the exact generated expression from Section 2.3.
Whitespace and comments between tokens and redundant parentheses around a complete scalar expression or unary operand are permitted; macro arguments remain single constant tokens.

String tokens have no encoding prefix and use UTF-8 source characters, C simple escapes, octal byte escapes of one to three digits, hexadecimal byte escapes, or C `\u`/`\U` universal character names.
An octal or hexadecimal escape MUST have a value from 0 through 255; hexadecimal escapes consume every following hexadecimal digit within that token.
Universal character names MUST be valid under the C17 rules and encode their Unicode scalar value as UTF-8.
The mapper concatenates the decoded token bytes before checking UTF-8 validity and the prohibition on embedded NUL.
Only the final implicit terminating NUL is omitted from the schema value.
Trigraph sequences are outside this literal subset.
Compilation of these headers MUST use UTF-8 source and ordinary string literal encodings.

The mapper MUST reject any literal replacement outside these forms, including casts, other identifiers or macro invocations, and arithmetic other than the specified minimum-integer expression.
It MUST recognize the permitted standard macros by their specified meanings without evaluating user-defined macro expansions.
A header MUST NOT redefine those standard macros.

### 3.6 Event Struct Recognition

A named aggregate whose owner ends in `_event` reconstructs an event declaration.
A canonical `_EVENT` tag reconstructs a map body.
A canonical `_CHOICE` tag reconstructs a choice body under Section 3.5, and every reconstructed arm MUST be a map.
The mapper MUST reject any other aggregate tag or body form for an event, and MUST reject an `_EVENT` tag whose owner does not end in `_event`.

The following example has a map body:

```c
typedef struct logos_storage_Upload_progress_event_EVENT {
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
    const char* session;
} logos_storage_Upload_progress_event_t;
```

Generates:

```cddl
storage.upload_progress_event = {
    bytes_sent: uint64,
    bytes_total: uint64,
    session: tstr,
}
```

### 3.7 Lifecycle Symbol Recognition

The module ABI symbols (`_MODULE_name`, `_MODULE_call_surface`, `_MODULE_init`, `_MODULE_apply_configuration`, `_MODULE_destroy`, `_MODULE_free`, `_MODULE_dispatch`, and `_MODULE_async_api`) are recognised by name and excluded from the CDDL schema.
They are identity, lifecycle, or provider-control symbols,
not schema-defined module methods.
The `_MODULE_free` suffix refers to the module-prefixed `logos_<module-C>_MODULE_free` symbol.

Module reconstruction MUST recover the runtime module name by decoding `<module-C>` from a consistent lifecycle symbol family conforming to Sections 2.1 and 2.6.
Its primary document, when present, is selected under Section 3.2; lifecycle symbols MUST NOT override an explicit interface or supporting-document role.
The implemented interface set is selected by the implementation constants, not by inclusion of interface declarations alone.
A module with no primary document and no implemented interface reconstructs no schema document and MUST NOT be classified as a provider merely because it has lifecycle symbols.

### 3.8 Roundtrip Guarantee

The round-trip guarantee preserves the Logos canonical schema model.
It does not preserve the spelling or layout of hand-authored C source.

For any conformant C header set `H`:

```
H -> (C-to-CDDL) -> (schema documents, module binding if any)
  -> (CDDL-to-C) -> H'
```

`H'` MUST be the canonical metadata-extended C representation of the schema documents and module binding recovered from `H`, including the document-role namespace constants required by Section 2.1.
Mapping `H'` back to CDDL MUST reproduce that same schema model.
Regeneration of module-specific declarations MUST also use the recovered module binding and preserve it on subsequent reconstruction.
The binding is retained tooling data; no additional schema document, serialized format, or authored sidecar file is required.

For any conformant CDDL schema `S`:

```
S -> (CDDL-to-C) -> header.h -> (C-to-CDDL) -> S'
```

`S'` MUST produce the same Logos canonical schema model as `S`.
Comments, whitespace, source declaration order, and source file layout may differ because they are not schema identity inputs.

### 3.9 Required C Mapping Conformance Cases

The cases in this section are normative.
They define schema-model and canonical-declaration results rather than source-file formatting.
The shared C ABI types from Section 5.2 are in scope for every C fragment and are not repeated.

The optional-tuple conformance cases MUST include absent and present nonempty tuples, an optional empty tuple, and a nested tuple component in both struct and method-parameter forms.
They MUST preserve one presence flag for each optional schema field and reject independently optional tuple positions.

The conformance set MUST also include a choice-valued event body.
Its C representation MUST use the ordinary choice layout without an additional event wrapper.
Generating C and reconstructing CDDL MUST preserve its event role, map arms, canonical schema model, and schema identity.

The literal conformance cases MUST include zero, the maximum `uint64` value, negative one, the minimum `int64` value, equivalent bases and suffixes, standard integer macros, parentheses, and concatenated UTF-8 strings with equivalent escapes.
They MUST include an escaped byte immediately followed by a digit or hexadecimal letter and reject unsigned negation, malformed suffixes, out-of-range macro arguments, embedded NUL, invalid UTF-8, and expressions outside Section 3.5.
Generated and handwritten equivalents MUST preserve their scalar kind, value, canonical schema model, and schema identity through C-to-CDDL reconstruction.
Generated literal values MUST also survive compilation in each supported language mode without changing their scalar values.

#### 3.9.1 Declaration-Only Module

The following concrete module schema uses one namespace and can be authored using the declaration-only C form:

```cddl
; -- metadata --
_module = "meter_module"

meter.changed_event = {
  value: uint64,
}

meter.reading = {
  ? label: tstr,
  value: uint64,
}

meter.read_request = {
  channel: uint32,
}

meter.read_response = {
  label: tstr .size (1..64),
  reading: meter.reading,
}
```

Its declaration-only C authoring form is:

```c
typedef const char* logos_tstr_size_1_64_t;

typedef struct logos_meter_Changed_event_EVENT {
    uint64_t value;
} logos_meter_Changed_event_t;

typedef struct logos_meter_Reading_MAP {
    bool        has_label;
    const char* label;
    uint64_t    value;
} logos_meter_Reading_t;

typedef logos_result_t (*logos_meter_Read_FN_t)(
    logos_module_context_t*    module,
    logos_response_owner_t* response_owner,
    uint32_t                   in_channel,
    logos_tstr_size_1_64_t*   out_label,
    logos_meter_Reading_t*    out_reading
);

logos_result_t logos_meter_module_CALL_meter_Read(
    logos_module_context_t*    module,
    logos_response_owner_t* response_owner,
    uint32_t                   in_channel,
    logos_tstr_size_1_64_t*   out_label,
    logos_meter_Reading_t*    out_reading
);

const char* logos_meter_module_MODULE_name(void);

logos_result_t logos_meter_module_MODULE_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

void logos_meter_module_MODULE_destroy(logos_module_context_t* module);

const uint8_t* logos_meter_module_MODULE_call_surface(size_t* out_len);
void logos_meter_module_MODULE_free(logos_module_context_t* module, void* ptr);

logos_result_t logos_meter_module_MODULE_dispatch(
    logos_module_context_t* module,
    const char*             method,
    const uint8_t*          params_cbor,
    size_t                  params_len,
    uint8_t**               out_response_cbor,
    size_t*                 out_response_len
);
```

The C declaration set MUST reconstruct the schema model shown above.
The lifecycle and provider-control declarations supply `_module` and do not create schema declarations.
The first namespace component in every schema-derived identifier supplies the exact `meter` namespace.
The event struct reconstructs `meter.changed_event`, and the method typedef reconstructs the `meter.read` request and response pair.
The concrete provider function attaches that method to `meter_module` without creating another method declaration.

The declaration-only variant omits document-role namespace constants.
The mapper MUST also accept the same declarations with `#define LOGOS_PRIMARY_NAMESPACE_meter_module "meter"` and reconstruct the same schema model.
A generated header for this document MUST contain that constant.
Neither variant contains an implementation constant, an event-name constant, or a literal constant.
Generating C from the schema and then reconstructing CDDL from the generated declarations MUST produce the same canonical schema model.

#### 3.9.2 Metadata-Extended Construction Set

The following construction input set contains one concrete module document, one implemented interface document, and one supporting document.
It exercises metadata that canonical C declarations cannot recover by themselves.

The concrete module document is:

```cddl
; -- metadata --
_module = "sensor_module"
_implements = [
  h'6abd62efd7835d78114f988733977d9d766c9cce56aef7e8b117c45b2955fc22',
]

sensor.control.settings = {
  kind: "sensor",
  limit: metrics_types.counter,
}

sensor.control.configure_request = {
  settings: sensor.control.settings,
}

sensor.control.configure_response = {}
```

The implemented interface document is:

```cddl
; -- metadata --
_interface = "metrics_provider"

metrics_provider.snapshot_request = {}

metrics_provider.snapshot_response = {
  count: uint64,
}
```

The supporting document is:

```cddl
metrics_types.counter = uint64
```

The interface document's schema root under LOGOS-MODULE-COMMITMENT-MODEL is `6abd62efd7835d78114f988733977d9d766c9cce56aef7e8b117c45b2955fc22`.
That root is the direct byte-string literal in the module document's `_implements` array.

The canonical module-specific C declarations and schema-metadata constants are:

```c
#define LOGOS_PRIMARY_NAMESPACE_sensor_module "sensor.control"
#define LOGOS_IMPLEMENTS_sensor_module_INDEX0 "metrics_provider"
#define LOGOS_INTERFACE_NAMESPACE_metrics_provider "metrics_provider"
#define LOGOS_SUPPORTING_NAMESPACE_metrics_types "metrics_types"
#define LOGOS_LITERAL_sensor_NS_control_Settings_Kind "sensor"

typedef uint64_t logos_metrics_types_Counter_t;

typedef struct logos_sensor_NS_control_Settings_MAP {
    const char*                  kind;
    logos_metrics_types_Counter_t limit;
} logos_sensor_NS_control_Settings_t;

typedef logos_result_t (*logos_metrics_provider_Snapshot_FN_t)(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    uint64_t*               out_count
);

logos_result_t logos_sensor_module_CALL_metrics_provider_Snapshot(
    logos_module_context_t* module,
    logos_response_owner_t* response_owner,
    uint64_t*               out_count
);

typedef logos_result_t (*logos_sensor_NS_control_Configure_FN_t)(
    logos_module_context_t*                module,
    logos_response_owner_t* response_owner,
    const logos_sensor_NS_control_Settings_t* in_settings
);

logos_result_t logos_sensor_module_CALL_sensor_NS_control_Configure(
    logos_module_context_t*                module,
    logos_response_owner_t* response_owner,
    const logos_sensor_NS_control_Settings_t* in_settings
);

const char* logos_sensor_module_MODULE_name(void);

logos_result_t logos_sensor_module_MODULE_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

void logos_sensor_module_MODULE_destroy(logos_module_context_t* module);

const uint8_t* logos_sensor_module_MODULE_call_surface(size_t* out_len);
void logos_sensor_module_MODULE_free(logos_module_context_t* module, void* ptr);

logos_result_t logos_sensor_module_MODULE_dispatch(
    logos_module_context_t* module,
    const char*             method,
    const uint8_t*          params_cbor,
    size_t                  params_len,
    uint8_t**               out_response_cbor,
    size_t*                 out_response_len
);
```

The document-role constants reconstruct the three exact namespace boundaries and roles.
The C namespace component `sensor_NS_control` reconstructs `sensor.control`; the primary-namespace constant supplies its exact dotted spelling and document role.
The implementation constant selects the complete `metrics_provider` interface group, whose recomputed root MUST equal the `_implements` literal shown above.
The reference to `logos_metrics_types_Counter_t` reconstructs an imported reference to `metrics_types.counter` rather than an inline `uint64` node.
The literal constant constrains `sensor.control.settings.kind` to the text value `"sensor"`.

Generating C from the three documents and then reconstructing CDDL from the generated header set MUST reproduce all three canonical schema models and the exact implementation relationship.
The generated header set MUST NOT contain an event-name constant or any other schema-metadata constant not shown above.

The interface and supporting documents MUST retain the same document-role namespace constants when generated independently.
Reconstructing either document from its header alone or as a required dependency of this module MUST produce the same canonical schema model and document identity.

An interface-only provider case consists of the interface-role constant, implementation constant, interface method typedef, concrete interface method declaration, and module lifecycle and provider-control declarations shown above.
It contains no primary or supporting document declarations or constants.
The mapper MUST recover the `metrics_provider` interface unchanged and a binding for `sensor_module` with no primary document and exactly that implemented interface.
Regeneration with that binding MUST preserve the concrete provider declarations and the interface identity.
Reconstructing the interface-role constant and interface method typedef alone MUST recover the same interface without a module binding.

The conformance set MUST also cover an interface-only provider whose interface declares only events, a types-only primary document with an implemented callable interface, and a module with lifecycle declarations but no contracts.
These cases MUST preserve the explicit document roles and module binding without synthesizing schema documents.

#### 3.9.3 Recursive Aggregate References

The following supporting schema contains one self-recursive aggregate, one mutually recursive component, and one ordinary non-recursive aggregate reference:

```cddl
recursive.branch = {
  node: recursive.node,
}

recursive.left = {
  ? right: recursive.right,
}

recursive.node = {
  ? next: recursive.node,
  value: uint64,
}

recursive.right = {
  ? left: recursive.left,
}
```

Its canonical declarations are:

```c
typedef struct logos_recursive_Left_MAP logos_recursive_Left_t;
typedef struct logos_recursive_Node_MAP logos_recursive_Node_t;
typedef struct logos_recursive_Right_MAP logos_recursive_Right_t;

struct logos_recursive_Left_MAP {
    bool                          has_right;
    const logos_recursive_Right_t* right;
};

struct logos_recursive_Node_MAP {
    bool                         has_next;
    const logos_recursive_Node_t* next;
    uint64_t                     value;
};

struct logos_recursive_Right_MAP {
    bool                         has_left;
    const logos_recursive_Left_t* left;
};

typedef struct logos_recursive_Branch_MAP {
    logos_recursive_Node_t node;
} logos_recursive_Branch_t;
```

The `node` self-loop and both edges between `left` and `right` are recursive by-value edges and therefore use pointers.
The edge from `branch` to `node` crosses recursive components and remains an embedded value.
Generating C from the schema and then reconstructing CDDL from the generated declarations MUST reproduce the same canonical schema model.

#### 3.9.4 Choice-Valued Method Halves

The conformance set MUST include one method with a choice-valued request and map-valued response and one method with a map-valued request and choice-valued response.
For each choice-valued half, the canonical C form MUST contain the complete named-choice declaration and exactly one wrapper parameter from Section 2.4.
Generating C and reconstructing CDDL MUST preserve the canonical schema model in both cases.

#### 3.9.5 Required Rejections

Each case in the following table starts from the complete C declaration set named in the Input column and applies only the stated mutation.
The mapper MUST reject the resulting header set before emitting CDDL.
The required condition identifies the normative reason for rejection; diagnostic text is implementation-defined.

| Case | Input | Mutation | Required rejection condition |
| --- | --- | --- | --- |
| `C-DECL-WRONG-PRESENCE-TYPE` | Section 3.9.1 | Replace `bool has_label` with `uint32_t has_label`. | An identifier beginning with `has_` is not the exact `bool` presence flag required for the adjacent field. |
| `C-DECL-UNMATCHED-PRESENCE-MEMBER` | Section 3.9.1 | Delete the `label` member following `has_label`. | The presence member has no adjacent field whose name exactly matches the suffix after `has_`. |
| `C-DECL-CONFLICTING-ROLE` | Section 3.9.1 | Add `#define LOGOS_SUPPORTING_NAMESPACE_meter "meter"`. | A supporting schema cannot contain the method and event declarations in this input. |
| `C-EXT-MISSING-PRIMARY` | Section 3.9.2 | Delete `LOGOS_PRIMARY_NAMESPACE_sensor_module`. | A multi-document header set requires a document-role namespace constant for every non-common document. |
| `C-EXT-BAD-PRIMARY-PROJECTION` | Section 3.9.2 | Replace the primary-namespace value with `"sensor.runtime"`. | The value projects to `sensor_NS_runtime`, which does not match the `sensor_NS_control` declaration group. |
| `C-EXT-MISSING-INTERFACE-ROLE` | Section 3.9.2 | Delete `LOGOS_INTERFACE_NAMESPACE_metrics_provider`. | The implemented interface group has no document-role namespace constant. |
| `C-EXT-MISSING-IMPLEMENTS` | Section 3.9.2 | Delete `LOGOS_IMPLEMENTS_sensor_module_INDEX0`. | The concrete provider declares a non-primary interface method without the required implementation relationship. |
| `C-EXT-WRONG-LITERAL-TYPE` | Section 3.9.2 | Replace the settings literal value with `7u`. | The literal replacement has unsigned-integer type, but the associated C field has text-string type. |
| `C-EXT-UNSUPPORTED-DOUBLE` | Section 3.9.2 | Add `typedef double logos_sensor_NS_control_Temperature_t;`. | `double` is outside the allowed schema-bearing C subset. |
| `C-RECURSIVE-EMBEDDED-SELF` | Section 3.9.3 | Replace the `node.next` pointer with an embedded `logos_recursive_Node_t` value. | A recursive by-value edge does not use its required pointer representation. |
| `C-RECURSIVE-POINTER-NONRECURSIVE` | Section 3.9.3 | Replace the embedded `branch.node` value with `const logos_recursive_Node_t*`. | A non-recursive by-value edge incorrectly uses recursive-pointer spelling. |
| `C-CHOICE-WRONG-WRAPPER-NAME` | Section 3.9.4 | Replace the choice request parameter name `in_request` with `in_value`. | A choice-valued method half does not use its exact wrapper parameter name. |
| `C-CHOICE-MIXED-REQUEST-FORM` | Section 3.9.4 | Add a flattened request parameter after the choice request wrapper. | One method half mixes the wrapper and flattened forms. |

The following header set distinguishes dotted and underscored namespaces:

```c
#define LOGOS_INTERFACE_NAMESPACE_a_NS_b "a.b"
#define LOGOS_SUPPORTING_NAMESPACE_a_b "a_b"

typedef uint64_t logos_a_NS_b_Value_t;
typedef uint64_t logos_a_b_Value_t;
```

The mapper MUST distinguish the exact namespaces `a.b` and `a_b` and reconstruct either document when selected as the subject.
Replacing the first constant's name with `LOGOS_INTERFACE_NAMESPACE_a_b` MUST be rejected because its name no longer matches the projection of its string value.

#### 3.9.6 Keyword Escaping and C Linkage

The conformance set MUST cover every spelling in the fixed escape set as a schema field name and preserve that name through CDDL-to-C-to-CDDL reconstruction.
It MUST include optional byte-string and list fields and direct method parameters to verify that escaping follows complete identifier construction.
A map containing fields `class` and `class0` MUST retain that schema order while emitting members `class_` and `class0`.
The mapper MUST reject unescaped keyword members and unnecessary escapes such as `ordinary_`, `has_class_`, and `in_class_`.

The common header and these generated test headers MUST compile as C17, C23, C++17, C++20, and C++23.
Their ABI functions and callback types MUST retain C language linkage in C++.
Reconstruction with or without the conditional linkage wrapper MUST preserve the same schema documents and module binding.

#### 3.9.7 Identifier Significance and Limits

Within supported limits, conformance cases MUST preserve identifiers with long common prefixes that differ only near the end or in letter case.
They MUST cover macros, types, and exported functions.
Native-toolchain qualification MUST verify the exported function distinctions through linking and symbol resolution; successful source compilation alone is insufficient.
For each documented identifier-length limit, tests MUST cover the longest supported canonical identifier and an identifier exceeding that limit.
The latter case MUST fail explicitly without substituting a shorter name or presenting a partial result as a conforming output.

#### 3.9.8 Module and Method Symbol Names

The conformance set MUST cover runtime module names with single, repeated, and trailing underscores and reject noncanonical encodings such as `a_Ub`.
It MUST preserve each decoded runtime module name through module reconstruction and regeneration.
Method cases MUST include `init`, `destroy`, and `upload_url`, with corresponding `Init`, `Destroy`, and `Upload_url` components in provider symbols and defining-contract function typedefs.
Lifecycle and method declarations MUST remain distinct and reconstruct the original schema method names without changing document identity.

#### 3.9.9 Choice Labels and Fixed Discriminants

The conformance set MUST include symbolic primitive, literal, tagged-map, untagged-map, list, tuple, and fully qualified reference labels.
It MUST cover a required literal field with no valid token and duplicate labels that force whole-choice indexed fallback.
It MUST include nested choices whose outer and inner forms differ, and maps whose UTF-8 field-name order differs from encoded-CBOR key order.
The mapper MUST reject the wrong symbolic or indexed form, inconsistent support paths, incorrect literal constants, and discriminant storage other than `uint32_t`.

Native conformance MUST cover a symbolic tag order different from canonical schema-arm order, both conversion directions, invalid-tag rejection before payload access, and cleanup of the selected payload.
Direct-literal-only choices MUST omit the value union; mixed choices MUST omit only direct-literal members, while references to named literals retain members.
Generated headers MUST preserve the specified discriminant width in the supported C and C++ modes, including when compiler options alter enum storage.

#### 3.9.10 Complete Semantic Paths

The conformance set MUST distinguish a declaration named `left_right` from a field `right` inside declaration `left`, including their literal constants.
It MUST preserve every list-element and tuple-position step in nested aggregate names.
Named references MUST retain their defining document and declaration, while equal inline shapes at different paths MUST retain distinct stems without becoming named schema declarations.
The mapper MUST reject omitted path steps, altered atom capitalization, noncanonical index spellings, and family suffixes inconsistent with the represented schema kind.
Standalone callable interfaces and supporting documents with dotted or underscored namespaces MUST reconstruct without document-role constants when the single-document inference rule in Section 3.2 applies.
A types-only interface still requires its explicit interface-role constant.

---

## 4. CDDL-to-CBOR Canonical Encoding

When a method call is serialised for socket transport, the mapping from the
CDDL schema to Logos deterministic CBOR bytes is defined here.
This section and section 2 are two views of the same schema:
the C API is the in-process view, and Logos deterministic CBOR encoding is the
on-the-wire value view.

Logos deterministic CBOR is the module-boundary value encoding profile defined by this specification.
It is based on the CBOR data model and core deterministic encoding requirements in RFC 8949 Section 4.2.1.
This specification states the complete profile so two conforming implementations do not need another encoding specification to agree on bytes.

It is the normative Logos profile for module request, response, event, error,
transport-envelope, normalized-value, and commitment hash-input bytes unless a
more specific Logos specification explicitly defines a narrower profile.

### 4.1 Primitive Encoding

| CDDL type  | Logos deterministic CBOR encoding     |
|------------|---------------------------------------|
| `bool`     | Simple value: true (0xf5) / false (0xf4) |
| `uint8`, `uint16`, `uint32`, `uint64` | Major type 0, shortest encoding within the alias range |
| `int8`, `int16`, `int32`, `int64` | Major type 0 for non-negative values or major type 1 for negative values, shortest encoding within the alias range |
| `tstr`     | Major type 3 (text string)            |
| `bstr`     | Major type 2 (byte string)            |

### 4.2 Composite Encoding

**Maps (structs):** deterministic CBOR map (major type 5) with text string
keys.
Keys MUST be sorted using the map-order rule defined in section 4.4.

```
space_info -> {
    "used": 9663676416,
    "quota": 10737418240,
    "available": 1073741824,    ; encoded key heads: 0x64 < 0x65 < 0x69
}
```

Deterministic CBOR wire order can differ from canonical C field-name order.
Encoders apply the deterministic-CBOR map order, and decoders match fields by key name.

**Arrays:** deterministic CBOR array (major type 4), definite length.

**Optional fields:** Absent keys are simply omitted from the deterministic
CBOR map.
The `has_<field>` flag in the C struct is the decoded representation of key
presence.

**Choices:** Encoded as the raw deterministic CBOR value of the selected
alternative.
The decoder determines the selected alternative by applying the schema-defined structural selection plan.
It validates the complete decoded value against the selected arm.
Choice selection MUST NOT depend on source declaration order.

### 4.3 Method Call and Event Encoding

Method params, response results, and event data are each encoded as
deterministic CBOR maps per sections 4.1 and 4.2.
The Transport envelope wraps these maps; see LOGOS-MODULE-TRANSPORT section
1.3 for the full envelope format.

**Example — `storage.exists` request params:**
```
{"cid": "bafy..."}     ; deterministic CBOR map, keys sorted per §4.4
```

**Example — `storage.exists` response result:**
```
{"exists": true}
```

For methods with empty responses, the result is an empty map `{}`.
For events, the `data` field encodes the event schema map.

### 4.4 Logos Deterministic CBOR Requirement

All encoded payloads at the module boundary MUST use Logos deterministic CBOR.
This profile is based on RFC 8949 Section 4.2.1.
It requires:

1. Map keys MUST be sorted by bytewise lexicographic comparison of the complete deterministic CBOR encoding of each map key.
   Sorting by key length before key byte content MUST NOT be used.
2. The argument in the initial byte sequence of every CBOR data item MUST use the shortest possible encoding.
   This includes integer values and the lengths of byte strings, text strings, arrays, and maps.
3. Indefinite-length encodings MUST NOT be used.
4. Duplicate map keys MUST NOT appear.
5. Floating-point data items MUST NOT appear at any nesting depth.

The Logos deterministic CBOR profile is a Logos-owned application profile over
the CBOR data model and core deterministic encoding requirements in RFC 8949.

### 4.5 Validation

Implementations MUST:

1. Reject incoming CBOR that violates the determinism rules in Section 4.4 with error code `INVALID_PARAMS`.
2. Produce outgoing deterministic CBOR that satisfies section 4.4 in every build mode.
   An implementation MAY elide a separate validation pass when its encoder guarantees those requirements by construction.
   Debug and release builds MUST NOT emit different bytes for the same schema-typed value.
3. Reject unknown method names -> error code `METHOD_NOT_FOUND`.
4. Reject wrong parameter types or missing required fields ->
   error code `INVALID_PARAMS`.

An incoming CBOR major-type-3 item whose content bytes are not well-formed UTF-8 MUST be rejected with error code `INVALID_PARAMS`.
When `logos.invalid_params_detail` is returned for this failure, its `reason` MUST be `schema-mismatch`.
The rejected bytes MUST NOT be passed to provider code as a C text value.

For module method payloads, schema validation is owned by the module dispatch
layer generated from or implemented against the module's CDDL schema.
The runtime and transport layers validate envelopes and routing fields.
They MUST NOT be required to introspect module payload schemas while forwarding
local or remote transport calls.

A module dispatch rejection is reported as an invocation failure under Section 4.6.
Failure of Transport message validation is reported under LOGOS-MODULE-TRANSPORT Section 2.3.
Transport deterministic-CBOR validation includes the embedded payload maps and does not require their schemas.
A floating-point data item in `params`, `result`, or `data` is a Transport validation failure and MUST NOT be deferred to schema validation.

Contract-defined value constraints that are not expressed in the schema remain requirements of that contract.
The contract MUST define their enforcement and failure outcomes consistently with Section 4.6.

#### 4.5.1 Value Nesting

Payload depth is the maximum number of array or map containers on any path through the payload.
A root container has depth one; scalar values add no level.
The Transport envelope is excluded, and byte-string contents are not traversed.

Implementations MUST enforce a documented, finite, configurable maximum payload depth of at least 128.
Module interfaces MUST NOT require payloads deeper than 128 unless deployment-specific configuration specifies a larger supported limit.
Internal schema, normalization, or hashing structures MUST NOT reduce the supported payload depth.

The limit MUST be checked before descending into or allocating a container beyond it.
Encoding, decoding, schema validation, commitment processing, and cleanup MUST remain resource-bounded at every supported depth.
A payload exceeding the limit MUST NOT be dispatched, accepted, or delivered.
A module dispatch rejection caused solely by this limit MUST use `INVALID_PARAMS` without structured detail.

### 4.6 Contract Outcomes and Invocation Failures

A schema-defined method invocation has exactly one of these results:

- A valid contract response.
  The provider returns `LOGOS_OK`, and the response value conforms to the selected method response schema.
  This remains a valid contract response when it represents an expected domain or application failure.
- An invocation failure.
  A nonzero shared `logos.error_code` reports that the invocation did not produce a valid contract response.

An expected domain or application failure is therefore part of the schema-typed response.
The provider MUST return `LOGOS_OK` and populate that response.
In local or remote Transport mode, the adapter MUST carry it in `response-ok.result` with its payload commitment.

When an invocation failure occurs and the responder can return a Response,
it MUST carry the shared error code in `response-err.error`.
If a Transport failure prevents receipt of a Response,
the caller-side adapter MUST return the corresponding nonzero invocation status without constructing a contract response.

In direct mode, the per-method function returns `logos_result_t` directly.
No encoding or Transport message is involved.
The invocation status passes through unchanged.

Protocol errors are distinct from correlated invocation failures.
A protocol error reports a connection or framing failure,
such as malformed or non-deterministic CBOR in a Transport message or an unknown Transport message kind.
A correlated invocation failure is carried in `response-err` with the Request identifier.
For example, `LOGOS_ERR_METHOD_NOT_FOUND` is an invocation failure and not a protocol error.

---

## 5. Logos Common Schema Surface

The CDDL in this section defines the normative Logos prelude aliases and reusable Logos common schema surface.
The pinned common schema surface is the sole unmarked schema document that is not a supporting schema.
Its well-known callable declarations and named types are fixed by this section.
`logos_common.cddl` is an extracted machine-readable mirror for source-authoring convenience.
If the extracted artifact differs from this specification, this specification governs.
For schema identity, LOGOS-MODULE-COMMITMENT-MODEL treats those two groups
differently:
prelude integer aliases normalize to built-in primitive schema leaves, while
common schema definitions are referenced definitions in the Logos common schema
surface.
For schema construction, the pinned common schema document consists exactly of the Section 5.1 rules whose qualified names belong to the `logos` namespace.
The fixed-width integer aliases belong to the Logos prelude and are not rules of that document.

### 5.1 CDDL Definitions

```cddl
; Normative Logos prelude and common schema surface.

; -- Logos prelude integer aliases --
uint8  = uint .size 1
uint16 = uint .size 2
uint32 = uint .size 4
uint64 = uint .size 8

int8  = -128..127
int16 = -32768..32767
int32 = -2147483648..2147483647
int64 = -9223372036854775808..9223372036854775807

; -- error codes --
logos.error_code =
    0 / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9

; -- bounded encoded invocation-failure detail --
logos.error_detail = bstr .size (1..4096)

logos.invalid_params_reason =
    "malformed-cbor" /
    "non-deterministic-cbor" /
    "schema-mismatch" /
    "configuration-schema-mismatch"

logos.invalid_params_path_segment = tstr / uint64

logos.invalid_params_detail = {
    reason: logos.invalid_params_reason,
    ? path: [* logos.invalid_params_path_segment],
}

; -- exact schema commitment --
logos.schema_commitment = {
    commitment_model: "logos.commitment-model.2026-10",
    schema_root: bstr .size 32,
    hash_profile: "logos.hash-profile.2026-08.choice-index",
    hash_suite: "logos.hash-suite.blake3-256",
}

; -- route handle (process-local, not on wire) --
; logos_route_handle_t is a process-local binding concept, not serialised.

; -- selected-contract introspection (well-known method) --
logos.schema_request = {}
logos.schema_response = {
    schema: tstr .size (1..1048576),
    interface_schemas: [* {
        namespace: tstr .size (1..128),
        commitment: logos.schema_commitment,
        document: tstr .size (1..1048576),
    }],
    supporting_schemas: [* {
        namespace: tstr .size (1..128),
        commitment: logos.schema_commitment,
        document: tstr .size (1..1048576),
    }],
}
```

`logos.schema_commitment` identifies one complete schema under the fixed commitment-model revision, hash profile, and hash suite.
The schema root already commits to the schema namespace.
A separate namespace field is not part of schema identity.

`logos.schema` is the well-known selected-contract introspection method.
Concrete module and interface contract schemas MUST NOT declare its bare method name `schema`, as required by Section 1.4.
The provider-side Runtime boundary supplies this method rather than dispatching it to module code.
It is callable only through a ready route whose method access includes the
`logos.schema` declaration root from the pinned Logos common schema surface.

The response MUST contain the CDDL schema document for the route's selected contract and every interface and supporting schema document required to reconstruct that contract.
For a route selected through the provider's primary concrete contract,
the response contains that concrete contract, all and only the interface documents selected by its `_implements` entries, and the exact supporting-schema set validated for it.
For a route selected through an implemented interface contract,
the response contains that interface contract and MUST NOT expose the provider's primary concrete schema
or another implemented interface merely because the same provider implements it.
Its `interface_schemas` array MUST be empty, and its `supporting_schemas` array MUST contain all and only the supporting schemas required by the selected interface.
It MUST NOT include supporting schemas needed only by the primary contract or another implemented interface.

Each returned interface entry MUST contain a valid interface contract schema.
Its `namespace` MUST equal the namespace derived from its document,
and its commitment MUST equal the recomputed schema commitment for that document.
Interface entries MUST have distinct namespaces and schema roots and MUST be ordered by namespace UTF-8 bytes and then schema-root bytes.
Each returned supporting entry follows the same namespace, commitment, uniqueness, and ordering rules as `provider-supporting-schema`.
The selected document and both dependency sets MUST reconstruct the schema identity bound to the route.
The response MUST NOT contain an unused interface or supporting schema.
The complete Logos deterministic-CBOR encoding of a `logos.schema_response` value MUST be no larger than 8 MiB.
The exact document set required for a selected contract MUST fit within this limit; otherwise that contract MUST NOT be exposed through a ready route.
This bound matches the `provider-call-surface` limit in Section 2.6 and leaves room for a complete `logos.transport.response-ok` envelope under the mandatory 16 MiB stream-frame support ceiling in LOGOS-MODULE-TRANSPORT Section 2.1.

The module ABI function `logos_<module-C>_MODULE_call_surface()` has a different purpose.
It supplies the complete provider descriptor to the ABI caller during implementation binding and provider validation.
A route-level `logos.schema` implementation MUST use the exact contract selected by that route.
It MUST NOT return the complete provider descriptor or disclose a contract that is not required to reconstruct the selected contract merely because the backing provider implements it.

Module introspection is schema-first:
method listings, event listings, request/response shapes, and type information
are derived from the module schema and its canonical schema model.
Runtime module listings are runtime introspection state and are exposed through
the runtime-control contract defined by LOGOS-MODULE-RUNTIME.

`logos.error_code` is the shared Logos module-boundary status-code registry.
LOGOS-MODULE-INTERFACE owns allocation of this registry.
Other Logos specifications may cite these values, but they do not allocate
additional shared status codes.

For a schema-defined method invocation,
value `0` means that the invocation produced a valid contract response.
A nonzero value means that the invocation did not produce a valid contract response.
The registry is not a vocabulary for schema-defined domain or application outcomes.
A contract MUST represent those outcomes in its response schema.

Values `0` through `9` are allocated in this revision.
A conforming implementation of this revision MUST NOT emit any other
`logos.error_code` value.
When a serialized Logos value contains an unknown shared error-code value,
the receiver MUST treat the enclosing value or message as invalid for this
revision.
For local or remote transport, that invalid value is handled through the
transport or method validation path that rejected the message.
When a provider returns or completes with an integer outside the allocated
`logos_error_code_t` range,
the ABI invocation path or generated adapter MUST treat the invocation as a module failure and MUST NOT serialize the unknown integer as a shared Logos error code.

An invocation failure MAY include a human-readable diagnostic message containing at most 512 UTF-8 bytes.
The message has no machine-readable semantics.
An invocation that returns `LOGOS_OK` MUST NOT include a diagnostic message or structured failure detail.

**Structured invocation-failure detail.**

When `detail` is present,
its byte string MUST contain exactly one complete Logos deterministic-CBOR value.
The encoded value MUST have no trailing bytes
and MUST validate against the root assigned to the error code.
The encoded byte string MUST contain between 1 and 4096 bytes.

| Status code | Allowed detail |
| --- | --- |
| `LOGOS_ERR_INVALID_PARAMS` | Optional `logos.invalid_params_detail` |
| `LOGOS_OK` and every other allocated status | Absent |

`logos.invalid_params_detail.reason` classifies the validation failure.
`malformed-cbor` means that the input is not one complete CBOR value.
`non-deterministic-cbor` means that it violates Section 4.4.
`schema-mismatch` means that a deterministic value does not conform to the selected request schema.
`configuration-schema-mismatch` means that a decoded deterministic configuration value fails the accepted configuration schema under LOGOS-MODULE-CONFIGURATION.
It applies only to that configuration validation, not to arbitrary opaque byte-string fields.

When `path` is present, its segments identify a path from the rejected value's root.
For `configuration-schema-mismatch`, that root is the decoded configuration value.
For the other reasons, it is the selected invocation request value.
An empty path identifies the rejected value itself.
A text segment identifies a map key,
and an unsigned-integer segment identifies an array index.

An implementation MUST validate detail before forwarding it or presenting it as structured data.
It MUST reject an enclosing result or error payload whose detail is not allowed or does not validate.
An ABI caller MUST validate a native provider result's status code, message and detail before forwarding them.
A provider result violating these rules MUST be treated as `LOGOS_ERR_MODULE`, without forwarding its diagnostics or contract-response outputs.
This rule applies to synchronous, dispatch and asynchronous completion paths and does not remove the cleanup obligations for transferred response ownership in Sections 2.7 and 2.9.
`message` and decoded detail MUST NOT disclose information that the caller is not authorized to observe.
In particular, authorization failures MUST NOT expose policy inputs, matching rules, credentials, provider identities, or host details.

Other expected domain and application failures continue to use the selected contract's typed response.
They MUST NOT use this detail channel.

### 5.2 C Definitions (`logos_types.h`)

These C definitions are the C-side common ABI surface used by generated and
hand-written modules and caller-side bindings.
For C-first modules, the reverse mapping in section 3 recognizes these shared
C types and maps them to the corresponding schema or ABI concepts defined by this specification.

`logos_types.h` also supplies the canonical C declarations for every named type in the pinned common schema surface from Section 5.1 and any constraint or inline support declarations required by those types.
Those declarations are derived by Sections 2.1 through 2.3, including the dedicated common-name projection and the `logos.error_code` exception.
Generated contract headers include `logos_types.h` and MUST NOT redeclare its fixed common types.
The common declarations are mapping inputs in the same sense as `uint64_t`: a reverse mapper recognizes their fixed names but does not reconstruct their definitions as part of the authored C contract.

- `logos_error_code_t` defines the shared status-code space used at the module boundary.
- `logos_result_t` reports the status of an ABI operation.
  For a schema-defined method invocation,
  `LOGOS_OK` means that the operation produced a valid contract response.
- `logos_result_t.message` is human-readable diagnostic text and MAY be `NULL`.
  When non-null, it MUST contain at most `LOGOS_ERROR_MESSAGE_MAX_LEN` UTF-8 bytes before its terminating null byte.
  It MUST be `NULL` when `code` is `LOGOS_OK`.
- `logos_result_t.detail`, when present, contains one validated structured value as specified in Section 5.1.
  Detail is absent exactly when `detail` is null and `detail_len` is zero.
  Detail is present exactly when `detail` is non-null and `detail_len` is between 1 and `LOGOS_ERROR_DETAIL_MAX_LEN` inclusive.
  Every other pointer/length combination is invalid.
- `logos_module_context_t` is an opaque per-instance type owned by the module implementation.
- The module creates one distinct live context during each successful `_MODULE_init()` call.
- Context lifetime and destruction follow Section 2.6.
- The module context is process-local.
  It MUST NOT be serialized, used as a module identity, or treated as a caller-side routing handle.
- `logos_module_init_input_t` is the size- and version-delimited initialization input supplied to the module by the ABI caller.
- `logos_runtime_control_binding_t` is the process-local binding through which the initialized module invokes the intrinsic Runtime Control contract.
- A Runtime Control binding contains a versioned vtable and opaque binding state.
  It supports generic deterministic-CBOR calls, response release, event subscription, unsubscription, route-handle materialization, remote binding acquisition, and owned-binding release.
- The Runtime Control binding identifies the initialized module instance as consumer but grants no authority by itself.
- The publish callback attributes published events to the initialized module instance and does not transfer the authority of an inbound caller.
- `logos_module_init_input_t.state_dir`, when non-null, identifies the module-visible persistent-state directory assigned to this module instance.
  It is a NUL-terminated UTF-8 string without an embedded NUL.
  A null value means that no persistent-state directory was assigned.
  The path is coordination data and grants no filesystem authority by itself.
- `logos_route_handle_t` contains a versioned vtable and opaque route state.
  Callers MUST NOT inspect or modify the state.
- A route handle is a process-local representation of one consumer-bound, exact-contract route.
- A language binding constructs it from a ready route returned by Runtime Control.
- In direct mode, a handle may wrap function pointers or equivalent
  in-process dispatch state.
  In local transport mode, it may wrap a transport connection or equivalent
  runtime state.
- The execution mode behind a handle is runtime-internal and MUST NOT change
  the module contract seen by callers.
- Releasing a route handle releases only the local binding state.
  Logical route closure remains the Runtime Control `close_route` operation.
- Route-handle concurrency is defined in Section 2.8.
- `logos_subscription_id_t` identifies one subscription within one route handle.
- `logos_event_handler_t` receives validated encoded event data through a caller-side route binding.
- `logos_<module-C>_MODULE_free(module, ptr)` releases serialized dispatch response buffers returned by that module instance.
- Typed response storage is released through `logos_response_owner_clear` as defined in Section 2.7.1.

```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LOGOS_C_MAPPING_REVISION 3u

#define LOGOS_C_CONTEXT_MODEL_6c6f676f732e636f6d6d69746d656e742d6d6f64656c2e323032362d3130 1
#define LOGOS_C_CONTEXT_PROFILE_6c6f676f732e686173682d70726f66696c652e323032362d30382e63686f6963652d696e646578 1
#define LOGOS_C_CONTEXT_SUITE_6c6f676f732e686173682d73756974652e626c616b65332d323536 1

#ifdef __cplusplus
extern "C" {
#endif

/* -- Error codes -- */

typedef enum {
    LOGOS_OK                    = 0,
    LOGOS_ERR_METHOD_NOT_FOUND  = 1,
    LOGOS_ERR_INVALID_PARAMS    = 2,
    LOGOS_ERR_MODULE            = 3,
    LOGOS_ERR_NOT_AUTHORISED    = 4,
    LOGOS_ERR_TRANSPORT         = 5,
    LOGOS_ERR_TIMEOUT           = 6,
    LOGOS_ERR_VERSION_MISMATCH  = 7,
    LOGOS_ERR_NOT_READY         = 8,
    LOGOS_ERR_CANCELLED         = 9,
} logos_error_code_t;

/* -- Result type -- */

#define LOGOS_ERROR_MESSAGE_MAX_LEN 512u
#define LOGOS_ERROR_DETAIL_MAX_LEN 4096u

typedef struct {
    logos_error_code_t  code;
    const char*         message;      /* human-readable; may be NULL */
    const uint8_t*      detail;       /* optional encoded detail; may be NULL */
    size_t              detail_len;
} logos_result_t;

/* -- Response ownership -- */

typedef struct logos_response_owner {
    void* state;
    void (*release)(void* state);
} logos_response_owner_t;

static inline void logos_response_owner_clear(logos_response_owner_t* owner)
{
    logos_response_owner_t previous = *owner;
    owner->state = 0;
    owner->release = 0;
    if (previous.release != 0) {
        previous.release(previous.state);
    }
}

/* -- Module initialization and per-instance context -- */

/*
 * Module-owned opaque state for one initialized module instance.
 * ABI callers never dereference or free this value.
 */
typedef struct logos_module_context logos_module_context_t;
typedef struct logos_runtime_control_binding logos_runtime_control_binding_t;
typedef struct logos_runtime_control_vtable logos_runtime_control_vtable_t;
typedef struct logos_route_handle logos_route_handle_t;
typedef struct logos_route_vtable logos_route_vtable_t;

#define LOGOS_ASYNC_CALL_ABI_VERSION 1u
#define LOGOS_ASYNC_PROVIDER_ABI_VERSION 1u
#define LOGOS_INVOCATION_CONTEXT_ABI_VERSION 1u
#define LOGOS_CALLER_MODULE 1u
#define LOGOS_CALLER_SYSTEM_SERVICE 2u

typedef struct logos_async_call logos_async_call_t;
typedef struct logos_async_call_vtable logos_async_call_vtable_t;
typedef struct logos_invocation_context logos_invocation_context_t;
typedef struct logos_invocation_context_vtable logos_invocation_context_vtable_t;
typedef struct logos_provider_invocation logos_provider_invocation_t;

typedef struct {
    const uint8_t* data;
    size_t len;
} logos_utf8_view_t;

typedef struct {
    uint32_t kind;
    logos_utf8_view_t runtime_instance_id;
    logos_utf8_view_t module_instance_id;
} logos_caller_view_t;

struct logos_invocation_context {
    const logos_invocation_context_vtable_t* vtable;
    void* state;
};

struct logos_invocation_context_vtable {
    uint32_t abi_version;
    size_t struct_size;
    logos_result_t (*caller)(
        const logos_invocation_context_t* invocation,
        logos_caller_view_t* out_caller
    );
    bool (*is_cancelled)(const logos_invocation_context_t* invocation);
    logos_result_t (*publish)(
        const logos_invocation_context_t* invocation,
        const char* event_name,
        const uint8_t* cbor_data,
        size_t cbor_data_len
    );
};

typedef struct {
    void* state;
    const logos_invocation_context_t* (*current)(void* state);
} logos_invocation_access_t;

typedef void (*logos_async_complete_fn)(
    void* user_data,
    logos_result_t result,
    const uint8_t* response_cbor,
    size_t response_cbor_len,
    logos_response_owner_t owner
);

typedef struct {
    uint32_t abi_version;
    size_t struct_size;
    bool has_timeout;
    uint64_t timeout_ms;
} logos_async_options_t;

typedef struct {
    uint32_t abi_version;
    size_t struct_size;
    logos_async_complete_fn complete;
    void* user_data;
} logos_async_callbacks_t;

struct logos_async_call {
    const logos_async_call_vtable_t* vtable;
    void* state;
};

struct logos_async_call_vtable {
    uint32_t abi_version;
    size_t struct_size;
    void (*submit)(logos_async_call_t* call);
    void (*cancel)(logos_async_call_t* call);
    void (*release)(logos_async_call_t* call);
};

struct logos_provider_invocation {
    uint32_t abi_version;
    size_t struct_size;
    const char* method;
    const uint8_t* params_cbor;
    size_t params_cbor_len;
    const logos_invocation_context_t* context;
    void (*complete)(
        logos_provider_invocation_t* invocation,
        logos_result_t result,
        const uint8_t* response_cbor,
        size_t response_cbor_len,
        logos_response_owner_t owner
    );
    void (*execution_release)(logos_provider_invocation_t* invocation);
};

typedef struct {
    uint32_t abi_version;
    size_t struct_size;
    void (*submit)(
        logos_module_context_t* module,
        logos_provider_invocation_t* invocation
    );
    void (*request_cancel)(
        logos_module_context_t* module,
        logos_provider_invocation_t* invocation
    );
} logos_async_provider_api_t;

#define LOGOS_MODULE_INIT_ABI_VERSION 2u

typedef void (*logos_publish_fn)(
    void*          user_data,
    const char*    event_name,
    const uint8_t* cbor_data,
    size_t         cbor_data_len
);

typedef struct {
    uint32_t                               abi_version;
    size_t                                 struct_size;
    const logos_runtime_control_binding_t* runtime_control;
    void*                                  publish_user_data;
    logos_publish_fn                       publish;
    const char*                            state_dir;
    const uint8_t*                         configuration_cbor;
    size_t                                 configuration_cbor_len;
    logos_invocation_access_t              invocation_access;
} logos_module_init_input_t;

/* -- Runtime Control binding and route handle -- */

#define LOGOS_RUNTIME_CONTROL_VTABLE_ABI_VERSION 2u
#define LOGOS_ROUTE_VTABLE_ABI_VERSION 2u

typedef uint64_t logos_subscription_id_t;

typedef void (*logos_event_handler_t)(
    const char*    event_name,
    const uint8_t* cbor_data,
    size_t         cbor_data_len,
    void*          user_data
);

typedef void (*logos_route_end_handler_t)(
    logos_error_code_t reason,
    void* user_data
);

struct logos_runtime_control_binding {
    const logos_runtime_control_vtable_t* vtable;
    void*                                 state;
};

struct logos_route_handle {
    const logos_route_vtable_t* vtable;
    void*                       state;
};

struct logos_runtime_control_vtable {
    uint32_t abi_version;
    size_t   struct_size;

    logos_result_t (*call)(
        const logos_runtime_control_binding_t* binding,
        const char*                            method,
        const uint8_t*                         params_cbor,
        size_t                                 params_cbor_len,
        uint8_t**                              out_response_cbor,
        size_t*                                out_response_cbor_len
    );

    void (*release_response)(
        const logos_runtime_control_binding_t* binding,
        uint8_t*                               response_cbor,
        size_t                                 response_cbor_len
    );

    logos_result_t (*subscribe)(
        const logos_runtime_control_binding_t* binding,
        const char*                            event_name,
        logos_event_handler_t                  handler,
        void*                                  user_data,
        logos_subscription_id_t*               out_subscription_id
    );

    logos_result_t (*unsubscribe)(
        const logos_runtime_control_binding_t* binding,
        logos_subscription_id_t                subscription_id
    );

    logos_result_t (*materialize_route)(
        const logos_runtime_control_binding_t* binding,
        const char*                            route_id,
        const uint8_t                          expected_contract_root[32],
        const uint8_t*                         schema_cbor,
        size_t                                 schema_cbor_len,
        logos_route_handle_t*                  out_route
    );

    logos_result_t (*connect_remote)(
        const logos_runtime_control_binding_t* binding,
        const uint8_t*                         endpoint_cbor,
        size_t                                 endpoint_cbor_len,
        const uint8_t                          expected_contract_root[32],
        logos_runtime_control_binding_t*       out_binding
    );

    void (*release)(
        logos_runtime_control_binding_t* binding
    );

    logos_result_t (*prepare_call)(
        const logos_runtime_control_binding_t* binding,
        const char* method,
        const uint8_t* params_cbor,
        size_t params_cbor_len,
        const logos_async_options_t* options,
        const logos_async_callbacks_t* callbacks,
        logos_async_call_t* out_call
    );
};

struct logos_route_vtable {
    uint32_t abi_version;
    size_t   struct_size;

    logos_result_t (*call)(
        logos_route_handle_t* route,
        const char*           method,
        const uint8_t*        params_cbor,
        size_t                params_cbor_len,
        uint8_t**             out_response_cbor,
        size_t*               out_response_cbor_len
    );

    void (*release_response)(
        logos_route_handle_t* route,
        uint8_t*              response_cbor,
        size_t                response_cbor_len
    );

    logos_result_t (*subscribe)(
        logos_route_handle_t*    route,
        const char*              event_name,
        logos_event_handler_t    handler,
        void*                    user_data,
        logos_subscription_id_t* out_subscription_id
    );

    logos_result_t (*unsubscribe)(
        logos_route_handle_t*   route,
        logos_subscription_id_t subscription_id
    );

    void (*release)(logos_route_handle_t* route);

    logos_result_t (*prepare_call)(
        logos_route_handle_t* route,
        const char* method,
        const uint8_t* params_cbor,
        size_t params_cbor_len,
        const logos_async_options_t* options,
        const logos_async_callbacks_t* callbacks,
        logos_async_call_t* out_call
    );

    logos_result_t (*observe_end)(
        logos_route_handle_t* route,
        logos_route_end_handler_t handler,
        void* user_data
    );
};

/* Optional provider completion capability. */
const logos_async_provider_api_t* logos_<module-C>_MODULE_async_api(void);

/* -- Memory management -- */

void logos_<module-C>_MODULE_free(logos_module_context_t* module, void* ptr);

#ifdef __cplusplus
}
#endif
```

Throughout Logos specifications and conformance assertions, a bare error name denotes the corresponding `logos_error_code_t` enumerator without its `LOGOS_ERR_` prefix; the `LOGOS_ERR_MODULE` and `LOGOS_ERR_TRANSPORT` enumerators use the bare names `MODULE_ERROR` and `TRANSPORT_ERROR`, respectively.

Memory lifetime rules: see section 2.7.

The versioned initialization struct uses `abi_version == 2` in this revision.
`struct_size` is the number of initialized bytes available in that struct.
A receiver MUST NOT read beyond `struct_size`.
Future compatible revisions MAY append fields and increase `struct_size`,
but MUST NOT reorder, remove, or change the meaning of existing fields.
An incompatible layout requires a new `abi_version`.

Before calling `_MODULE_init()`, the ABI caller MUST populate the ABI version and structure size.
A module that does not support the version or receives a structure too
small to contain the fields defined by that version MUST return
`LOGOS_ERR_VERSION_MISMATCH` and a null context.
Unknown appended fields within a supported version are ignored.

The Runtime Control and route vtables use ABI version `2` in this revision.
Each `struct_size` is the number of initialized bytes available in that vtable.
A binding consumer MUST reject a null vtable, a null state pointer, an unsupported version, a structure too small to contain every field defined by that version, or a null required operation pointer.
A binding consumer MUST NOT read beyond `struct_size`.
Future compatible revisions MAY append fields and increase `struct_size`, but MUST NOT reorder, remove, or change the meaning of existing fields.
An incompatible layout requires a new vtable ABI version.
The vtable and state pointers remain valid and unchanged for the complete binding or handle lifetime.
The current route vtable includes the required `observe_end` operation; a shorter version-2 vtable MUST be rejected with `VERSION_MISMATCH`.

When a binding-validation failure is reported through the shared result channel, an unsupported vtable version or insufficient versioned structure extent MUST use `VERSION_MISMATCH`.
A null vtable, null state, or null required operation in a binding supplied by its producer MUST use `MODULE_ERROR`.
The consumer MUST report the failure locally and MUST NOT call an operation through the rejected vtable, including `release`.
These checks assume valid readable storage for the binding and the vtable version-and-size prefix, with the required object and code lifetimes.
They do not require safe detection of forged, dangling, or unreadable pointers, and do not authorize use after release.

The Runtime Control `call` operation accepts an exact Runtime Control method name and one complete deterministic-CBOR request map for that method.
The route `call` operation accepts an exact method name selected by that route and one complete deterministic-CBOR request map for that method.
Before either call, the caller MUST set `*out_response_cbor` to `NULL` and `*out_response_cbor_len` to zero.
Success requires a non-null response buffer and a nonzero length containing exactly one valid deterministic-CBOR response map for the selected method.
Failure requires a nonzero result code, a null response pointer, and a zero response length.
The caller MUST reject every other result and output combination.
A successful call transfers the response buffer to the caller, which MUST pass the exact pointer and length exactly once to the matching vtable's `release_response` operation before releasing the binding or handle.
The generic route `call` operation uses deterministic CBOR at the caller-side binding boundary in every execution mode, including direct mode.
For a direct route, this encoding is not a Transport message and creates no Transport connection.
The direct binding invokes `logos_<module-C>_MODULE_dispatch()` or an equivalent validated adapter against the selected provider context.
An ABI caller that independently owns an accepted direct implementation binding MAY instead invoke its typed provider functions directly under Sections 2.6 through 2.8.

The Runtime Control `subscribe` and `unsubscribe` operations apply the subscription semantics in Section 2.5 to events selected from the Runtime Control contract.
The corresponding route operations apply those semantics to events selected by that route.

The `connect_remote` operation acquires a process-local binding to the intrinsic Runtime Control contract of an explicitly selected remote Runtime.
It MUST be invoked through the initialized module's local Runtime Control binding.
Invoking it through a remote binding MUST fail with `LOGOS_ERR_INVALID_PARAMS`.
The endpoint bytes MUST contain exactly one deterministic-CBOR `logos.runtime_control.runtime_endpoint` value as defined by LOGOS-MODULE-RUNTIME, with `runtime_instance_id` present and an address selecting `logos.remote.tls-tcp` or `logos.remote.quic`.
The selected Runtime MUST differ from the consumer's owning Runtime.
A schema-valid endpoint that omits the required Runtime identity, selects a non-remote address, or names the consumer's owning Runtime MUST be rejected with `INVALID_PARAMS` without validation detail.
Endpoint decoding or schema-validation failures MUST use `INVALID_PARAMS` with only the applicable validation detail permitted by Section 5.1.
Authentication, authorization, Hello compatibility, and transport failures MUST retain their applicable error classifications rather than being reclassified as invalid endpoint input.
The endpoint bytes and `expected_contract_root` are borrowed only for the operation.
The owning Runtime MUST authenticate the selected Runtime and validate Transport Hello against the supplied 32-byte Runtime Control schema root before reporting success.
The remote binding MUST retain the initialized module's complete consumer identity and MUST NOT substitute another module or a Runtime consumer.
Acquisition grants no authority; the target Runtime MUST enforce its enrollment, forwarding and operation-authorization requirements.
The binding's target and consumer MUST remain unchanged throughout its lifetime.

Before calling `connect_remote`, the caller MUST set `out_binding->vtable` and `out_binding->state` to `NULL`.
Success requires both fields to be non-null and transfers ownership of the acquired binding to the caller.
Failure MUST leave both fields null and MUST NOT retain a live acquired binding.
The output structure is caller-owned; its vtable and opaque state are Runtime-owned.
Remote `call`, `subscribe`, `unsubscribe` and `materialize_route` operations preserve their existing consumer, contract, validation and ownership requirements.

The caller MUST invoke each acquired binding's `release` operation exactly once, before the initialized module's `_MODULE_destroy()` returns.
If `_MODULE_init()` fails, the module MUST release every binding it acquired before returning that failure.
Before release, the caller MUST stop new operations, wait for outstanding operations to return, and release every transferred response buffer.
Release MUST NOT be invoked from a callback belonging to that binding.
Release deactivates remaining subscriptions, waits for the callback quiescence required by Section 2.5, and releases the Runtime-owned binding state.
After release begins, the caller MUST NOT use or inspect the binding again.
Release does not close independent provider sessions, release their route handles, or close their logical routes.
Execution-envelope termination MUST reclaim outstanding acquired bindings without requiring module cleanup to run.
The Runtime Control binding supplied in the initialization input is borrowed; the module MUST NOT invoke its `release` operation.

To materialize a route handle, the caller MUST provide the exact `route_id` and 32-byte `schema_root` from the `expected_contract` of a ready route returned through the same Runtime Control binding as `expected_contract_root`.
`schema_cbor` MUST be non-null and contain one `logos.schema_response` value encoded as Logos deterministic CBOR, with `schema_cbor_len` between 1 and 8,388,608 bytes.
The bytes are borrowed for the duration of the call.
The caller may construct this value from contract documents embedded in generated bindings or supplied with the application.
An authorized `describe_provider` response may also supply the required documents, but its complete provider descriptor MUST be projected to the selected contract and encoded as `logos.schema_response`; the descriptor bytes are not valid construction input themselves.
A previously obtained authorized `logos.schema` response for the exact selected contract is another valid source.
The caller does not need a call to `logos.schema` to materialize its first handle.
Every source remains subject to the same exact-document-set and root validation.
Runtime MUST validate the construction input under Sections 5.1 and 5.3 and verify that the reconstructed selected-contract root equals `expected_contract_root` before returning a handle.
Supplying this input does not require permission to call `logos.schema`.
Before calling `materialize_route`, the caller MUST set `out_route->vtable` and `out_route->state` to `NULL`.
Runtime MUST revalidate that the binding's consumer owns the route, that the route is currently ready, that the route still selects the exact expected contract recorded at establishment or renewal, and that the contract's schema root matches `expected_contract_root`.
Success requires non-null `out_route->vtable` and `out_route->state` values that represent that route without changing its selected contract or consumer.
Failure MUST leave both output fields null and MUST NOT create a live handle.
Route materialization does not create, renew, or retarget a logical route.

Malformed construction input, invalid schema documents, unresolved or conflicting dependencies, and input exceeding Section 5.3 limits MUST produce `INVALID_PARAMS`.
Validation detail is permitted only for a qualifying CBOR decoding or schema-validation failure; semantic CDDL, document-set, and resource-limit failures MUST omit it.
An unknown route, a route owned by another consumer, or a hidden or denied route MUST produce non-revealing `NOT_AUTHORISED`.
After the ownership and non-disclosure checks, a successfully reconstructed schema root that differs from `expected_contract_root`, or a recorded route contract root that differs from it, MUST produce `VERSION_MISMATCH`.
Route readiness and authorization failures MUST follow LOGOS-MODULE-RUNTIME Section 7.5; an invalidated but still-live Runtime Control binding follows its Section 3.4.
For a local or remote transport route, successful materialization requires completed provider-session establishment under LOGOS-MODULE-RUNTIME Section 4.1.
Hello rejection and other establishment failures MUST follow that section's error classifications.
All failures retain the null-output and no-live-handle requirements above.

The caller MUST invoke a successfully materialized route handle's `release` operation exactly once.
Before release, the caller MUST stop new operations through the handle and release every transferred response buffer.
Release deactivates every remaining subscription, waits for the callback quiescence required by Section 2.5, and releases the local binding state.
After release begins, the caller MUST NOT use or inspect the handle again.
Handle release does not close the logical route; an authorized caller closes that route through the Runtime Control `close_route` method.

The initialization input's `invocation_access.state` and `invocation_access.current` MUST be non-null.
The closure follows Section 2.9.3; it does not itself identify a caller outside an active provider entry.
The async call, option and callback structures use `LOGOS_ASYNC_CALL_ABI_VERSION`.
The provider descriptor and provider invocation use `LOGOS_ASYNC_PROVIDER_ABI_VERSION`.
The invocation-context vtable uses `LOGOS_INVOCATION_CONTEXT_ABI_VERSION`.
Each version-bearing descriptor, option structure, callback structure, provider invocation and vtable MUST have its supported version and sufficient initialized extent before an operation reads its fields.
The call and invocation-context wrappers are validated through their vtables; the caller views and initialization closure contain no separate version prefix.
Required operations and invocation-context state MUST be non-null; only the provider descriptor's `request_cancel` operation is optional.
For a failed caller-view query, the operation MUST leave the output view unchanged.
The caller-view output is caller-owned and its identifier bytes are borrowed.
Malformed callback or option input is rejected during preparation with `INVALID_PARAMS`; unsupported versions or insufficient versioned extent use `VERSION_MISMATCH`.
Call operations and their ownership rules are defined in Section 2.9.

The configuration fields are absent exactly when `configuration_cbor` is `NULL` and `configuration_cbor_len` is zero.
When present, they MUST contain a non-null pointer and nonzero length for exactly one deterministic-CBOR value.
All other pointer-and-length combinations are invalid.
The specification that assigns configuration semantics defines when the fields are absent or present and defines the exact value type and validation requirements.

The ABI caller passes one deterministic-CBOR value to `logos_<module-C>_MODULE_apply_configuration()` using a non-null pointer and nonzero length.
The assigning specification defines that value and the operation's outcome semantics.
The bytes are borrowed only for the duration of the call.

The `runtime_control` pointer MUST be non-null and identify the Runtime Control binding for the initialized module instance.
The module MAY invoke authorized Runtime Control methods through that binding during `_MODULE_init()` and throughout the live context.
The `publish_user_data` value is opaque callback-provider state.
The module MUST pass it back unchanged to `publish`.
When the validated provider call surface declares any event, including when it declares no methods,
the initialization input MUST contain a non-null `publish` callback.
The Runtime Control binding, callback, and opaque state are process-local and MUST NOT cross a Transport boundary.

### 5.3 Dynamic Schema Validation

Schema text obtained from a module, package, catalog, Runtime, or remote peer is untrusted structured input.
Successful artifact acceptance, provider authorization, or Transport authentication
does not make that text valid and does not authorize any method described by it.

Before using dynamic schema text for dispatch, call-helper generation, validation, routing, or user presentation, an implementation MUST parse and resolve it under the following limits:

- at most 1,048,576 UTF-8 bytes in one schema document;
- at most 8,388,608 UTF-8 bytes across all documents in one schema-construction input set;
- at most 65,536 `schema-node` occurrences across the Logos canonical schema models of one schema-construction input set; and
- at most 128 levels of `schema-node` nesting in those models.

For these limits, `schema-node` is the production defined by LOGOS-MODULE-COMMITMENT-MODEL Section 9.1.
Only explicitly supplied document models contribute to these limits.
Each such document is counted once, and named references are not expanded.
A declaration-body `schema-node` has nesting level one; each contained child `schema-node` increases the level by one.
Representation wrappers and serialization containers do not increase this nesting level.

A conforming implementation MUST support valid schemas up to these limits
and MUST reject an input that exceeds any limit before using a partial result.
It MUST also bound parser work, allocation, diagnostics, and reference traversal
so malformed input or cyclic references cannot evade those limits.

Dynamic schema resolution MUST NOT fetch a network resource or read an arbitrary filesystem path.
It MUST NOT load executable code or invoke a provider-selected resolver
because schema text names a source location.
The resolver may use only the pinned Logos common schema surface
and the exact interface and supporting schema documents explicitly supplied for the schema being constructed.
Source filenames, catalog aliases, and package paths are resolution conveniences,
not authority to perform input/output.

The implementation MUST reject schema text that is malformed,
uses an unsupported CDDL feature,
violates the Logos naming or type restrictions,
has unresolved or conflicting definitions,
contains a forbidden dependency,
includes an unused supplied interface or supporting schema,
or does not produce the expected namespace and structural schema identity.
An implementation MAY reuse cached parsed models or components only if it validates the complete supplied schema input set for each construction.
The resulting model MUST be consistent with the exact selected schema identity, semantic commitment-model revision, hash profile and suite.
Cached validation results MAY satisfy these checks when they establish every applicable requirement for the supplied construction.

A parsed schema describes value shape and declaration identity only.
It MUST NOT create a route, widen route access, authorize dispatch,
select a provider, or establish trust in code or data.

---

## Appendix A. Generated Artifacts (Informative)

The mapping rules in sections 2 through 4 can be applied mechanically to
produce C headers, adapter implementations, event helpers, and typed call helpers.
This appendix describes common derived artifacts and implementation patterns.
The normative requirements are the ABI, mapping, method-call, and encoding
rules defined in the main body of this specification.

### A.1 CDDL-to-C Artifacts

The following filenames illustrate generator defaults; except for `logos_types.h`, they are not required by the mapping.
`<stem>` is a generator output label, and `<namespace>` is the exact schema namespace, including its dots.
Neither filename determines module identity, document role, or schema identity.
Independent bundles can reside in separate directories, with relative includes resolved within each bundle.
A standalone interface or supporting document can be consumed directly without an entry wrapper.
The module author implements the provider functions declared by the entry header.
Optional helper declarations reside in separate convenience headers that may include the canonical contract headers.
Only the canonical contract headers and their required dependencies are supplied for schema reconstruction.

| Output file               | Contents                                         |
|--------------------------|--------------------------------------------------|
| `logos_types.h` | Fixed common C definitions (Section 5.2). |
| `logos_document_<namespace>.h` | Reusable interface or supporting-document declarations, metadata, and identity checks. |
| `logos_contract_<stem>.h` | Entry header: primary document declarations when present, reusable-document includes, and provider metadata and declarations when applicable. |
| `<module>_adapter.c`     | Optional generated adapter support: deterministic CBOR decode -> C provider call -> deterministic CBOR encode, plus applicable identity, lifecycle, call-surface, and dispatch symbols. |
| `<module>_events.h` | Typed event helper and handler declarations (Section 2.5 and Appendix A.4). |
| `<module>_events.c` | Typed event helper implementations. |
| `<module>_calls.h` | Typed call and cleanup helper declarations (Appendix A.5). |
| `<module>_calls.c`       | Typed call-helper implementations. |

### A.2 C-to-CDDL Artifacts

A generator may also derive the primary module schema and implemented interface schemas from a C header set that conforms to Section 3.
After deriving those schemas, it may produce the same artifact family listed
in Appendix A.1.

### A.3 Generated Dispatch Implementation

A provider module's mandatory `logos_<module-C>_MODULE_dispatch()` ABI symbol is commonly generated from the module's exposed contract set and the C mapping rules in this specification.
It MAY also be implemented by hand.
A handwritten implementation MUST behave as if derived from the same exposed contract set.
It dispatches only to exposed methods and validates request payloads
against the target method request schema.
It calls the corresponding per-method provider function or equivalent provider logic
and encodes responses according to the target method response schema.

The dispatch function is not a schema method.
It is a generic ABI entrypoint for hosts that carry method names and encoded
payloads.
The typed per-method C functions remain mandatory and form the native provider
surface for direct/static integrations and generated bindings.

For each exposed method `M`,
such an adapter commonly has a branch with this shape:

```c
if (strcmp(method, "M") == 0) {
    /* Decode params_cbor as M_request map (per §4.2) */
    /* Call logos_<module-C>_CALL_<namespace>_<Method>(...) (per §2.4) */
    /* Encode result as M_response map (per §4.2) */
    /* Clear the response owner after encoding, including on encoding failure */
    /* Write to *out_response_cbor, *out_response_len */
}
```

Such an adapter commonly:

- looks up the method in a generated dispatch table,
- returns `LOGOS_ERR_METHOD_NOT_FOUND` for an unknown method,
- decodes the deterministic CBOR request payload according to the method
  request schema,
- returns `LOGOS_ERR_INVALID_PARAMS` if decode fails,
- calls the corresponding per-method C function,
- encodes a valid contract response as a deterministic CBOR map matching the
  method response schema, and
- returns a nonzero invocation status without response bytes
  when the typed provider returns an invocation failure.

A generated adapter may handle the `logos.schema` well-known method only when it receives the route's selected contract from the Runtime-controlled invocation boundary.
It MUST return that selected contract as specified in Section 5.1
and MUST NOT substitute the backing module's complete call-surface descriptor
for the route-selected contract.
Unknown methods return `LOGOS_ERR_METHOD_NOT_FOUND`.

Because dispatch is an ABI entrypoint rather than a schema method,
commitment-model, hash-profile, authorization, audit, and conformance material
MUST identify the target schema method and the defining contract root.
That material MUST also identify the request/response values for that method.
They MUST NOT identify a synthetic dispatch method.

The generated `_MODULE_init()` implementation creates a distinct module context,
copies the Runtime Control binding and event-publication fields used by the generated adapter,
and invokes an optional author-provided initialization hook.
The generated `_MODULE_destroy()` implementation invokes an optional author-provided
cleanup hook and releases that context.
Even a stateless module needs a distinct live context token for each successful
initialization so instance lifetime can be enforced unambiguously.

### A.4 Generated Event Publish Helpers

For each event `<namespace>.<name>_event` exposed by a concrete module, a generator may produce a typed helper that encodes the event payload as deterministic CBOR and calls the runtime-provided publish function:

```c
/* From: storage.upload_progress_event = { session: tstr, bytes_sent: uint64, bytes_total: uint64 } */
void logos_storage_module_publish_storage_upload_progress(
    logos_module_context_t* module,
    uint64_t                bytes_sent,
    uint64_t                bytes_total,
    const char*             session
);
```

The helper name is illustrative and is not used for schema reconstruction.

The implementation deterministic-CBOR-encodes
`{bytes_sent, bytes_total, session}` per section 4.2
and calls the `publish` callback and `publish_user_data` retained in `module`
with event name `"storage.upload_progress_event"`.

Module authors call the typed helper instead of encoding deterministic CBOR
manually.
The module context remains process-local as defined in Section 5.2.

### A.5 Generated Typed Call Helpers

For each method, a generator may produce a typed call helper with an implementation-defined name that invokes the method through a `logos_route_handle_t`; for example:

```c
/* From: storage.exists_request = { cid: tstr }
 *       storage.exists_response = { exists: bool } */
logos_result_t logos_storage_invoke_exists(
    logos_route_handle_t* route,
    logos_response_owner_t* response_owner,
    const char*           in_cid,
    bool*                 out_exists
);
```

The helper requires a route whose selected contract defines `storage.exists`.
It deterministic-CBOR-encodes the request, invokes the route vtable's generic `call` operation, decodes the response, and writes `out_exists`.
The route binding invokes the validated direct provider or selected Transport path as defined in Section 5.2 without changing this caller-side surface.
The helper does not select a provider, acquire a route, or name another consumer.

The helper returns decoded storage under Section 2.7.2 and releases the encoded route response before returning.
Its paired cleanup helper can have this implementation-defined name and shape:

```c
void logos_storage_clear_exists(
    logos_response_owner_t* response_owner,
    bool* out_exists
)
{
    logos_response_owner_clear(response_owner);
    *out_exists = false;
}
```

The caller uses this cleanup helper after its final use of the response, including an empty-owner scalar response.
For compound responses, the generated helper also resets all output locations without traversing their payload storage.

### A.6 Framework-Specific UI Bindings

Generators may produce UI-framework-facing bindings derived from the same CDDL
schema.
Such bindings are derived views over the canonical module contract, not
parallel interfaces.

The Logos canonical schema model remains the contract definition.
Framework-specific binding details are out of scope for this specification.

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
- `cdCDDLe` -- Deterministic CDDL schema-as-data representation.
- LOGOS-MODULE-COMMITMENT-MODEL -- Logos schema and value semantic commitment model.
- LOGOS-MODULE-TRANSPORT -- Socket protocol specification.
- LOGOS-MODULE-RUNTIME -- Module admission, lifecycle, and routing specification.

### Informative

- [COSS] -- Consensus-Oriented Specification System.
  https://rfc.vac.dev/spec/1/
- LOGOS-MODULE-LOADER -- Module Loader module contract for module realization.

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
