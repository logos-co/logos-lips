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
Given either accepted representation, a conforming implementation MUST recover the same Logos canonical schema model, the same canonical representation on the other side, and the same Logos deterministic CBOR bytes for every schema-typed value.

A module author may start from either end:

- **CDDL-first:** Write a `.cddl` file, generate the C header.
- **C-first:** Write a conformant C header, generate the `.cddl` file.

Both paths MUST produce identical artifacts for the same logical contract.

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
A concrete module schema may reference named types from zero or more explicitly supplied supporting schemas.
An interface contract schema MUST NOT reference a supporting schema.
A supporting schema MUST NOT reference a concrete module schema, interface contract schema, or another supporting schema.

Concrete module, interface contract, and supporting schemas implicitly have access to the Logos prelude fixed-width integer aliases.
They MAY reference the common Logos schema definitions in Section 5.

The normative construction input is an explicitly supplied set of ordinary RFC 8610 CDDL documents.
For a concrete module schema, that set contains the module document, every interface document selected by `_implements`, and every supporting schema that supplies a referenced named type.
The set MUST contain every required document and MUST NOT contain an unused interface or supporting schema.
Every supplied document MUST have a distinct schema root.

Local contract declarations and references use the explicit qualified names required by Sections 1.4 through 1.7 and LOGOS-MODULE-COMMITMENT-MODEL.
CDDL module `include` and `import` directives MUST NOT alter the resolved rule graph.
A schema that requires such a directive is unsupported even when the directive is encoded as a CDDL comment.
An external named-type reference in a concrete module schema MUST resolve to exactly one declaration in an explicitly supplied supporting schema or the pinned Logos common schema.
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
Using `snake_case` gives a direct, collision-free mapping between schema names
and generated C identifiers without lossy hyphen-to-underscore conversion or
escaped C symbol names.

Such identifiers MUST use lowercase ASCII letters, digits, and underscores.
They MUST begin with a lowercase ASCII letter, MUST end with a lowercase
ASCII letter or digit, and MUST NOT contain consecutive underscores.
For a qualified schema name, these requirements apply separately to each dot-separated segment; the dot separates segments and is not part of any segment.
This rule applies to method names, event names, field names, and named type
names.
The metadata names `_module`, `_interface`, and `_implements`, the underscore-based runtime module name carried in `_module`, prelude aliases such as `uint64`, and exported C ABI symbols are not Logos module schema identifiers.
The complete schema namespace, including its dot separators, MUST contain at most 128 ASCII bytes.

A supporting schema MUST NOT declare a local named definition whose name ends in `_request`, `_response`, or `_event`.
Those suffixes are reserved for callable declarations in concrete module and interface contract schemas.

### 1.4 Methods as Request/Response Pairs

Methods are declared as pairs of named CDDL maps using the convention:

- `<module>.<method>_request` — the method input
- `<module>.<method>_response` — the method output

Each method request and response declaration MUST have a CDDL map body.
The bare method name formed by removing the namespace prefix and the `_request` or `_response` suffix MUST contain at most 128 ASCII bytes.

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

Every method remains one request with one final response.
Concurrent dispatch invocations may return in any order,
but that execution behavior does not create an asynchronous method kind or change the method's request and response schemas.

Map keys MUST be bare CDDL identifiers (not quoted strings). Key names are
used directly as C parameter names and deterministic CBOR map keys.

### 1.5 Event Declarations

Events are one-way notifications published by a module.
Each event declaration MUST have a CDDL map body and the suffix `_event`:

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

Events are NOT tied to specific methods. Any caller that subscribes to an
event receives it whenever the module publishes it. Event subscription is
managed by the runtime (see LOGOS-MODULE-RUNTIME section 4) and the transport
protocol (see LOGOS-MODULE-TRANSPORT section 5).

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
| Named types | Any type alias defined in the same schema or the Logos common schema surface in Section 5. |

The following are **NOT allowed** in module schemas:

| Disallowed | Rule |
|-----------|------|
| Bare `uint`, `int`, `nint` | MUST NOT appear in module schemas except inside the Logos prelude definitions. Use fixed-width integer aliases instead. |
| `any` | MUST NOT appear in module schemas. Transport envelope uses `any` for generic payload fields; validation against concrete schema happens at the module layer. |
| `float16`, `float32`, `float64` | Reserved for a future deterministic numeric profile. |
| Unkeyed maps (`{ * tstr => any }`) | Reserved for transport envelope. |
| CBOR tags (beyond the transport envelope) | Reserved for protocol use. |
| `.regexp`, `.cbor`, `.bits` controls | Reserved for future versions. |

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
The result uses either the declaration-only C form or the metadata-extended C form.

The declaration-only C form represents every schema fact through canonical C names, declarations, types, and function signatures.
It contains no schema-metadata preprocessor constants.

The metadata-extended C form adds preprocessor constants for schema facts that cannot be represented or recovered unambiguously from the canonical C declarations.
Those constants are build-time schema input and add no runtime symbol, storage, function parameter, or caller obligation.
They MUST NOT restate a schema fact that the declaration-only mapping recovers unambiguously.

A generator MUST use the declaration-only C form when the complete accepted schema set is representable by that form.
Otherwise it MUST use the metadata-extended C form and emit only the required schema-metadata constants.
Every accepted schema set MUST be representable by one of the two forms.
Given the same accepted schema set, any two implementations of this specification MUST produce identical C header sets, modulo whitespace, comments, include layout, and include guards.

### 2.1 Naming Conventions

**Namespace projection.** A simple namespace consists of one segment that begins with a lowercase ASCII letter, continues with lowercase ASCII letters or digits, and contains no underscore.
The C namespace component for any schema namespace is its complete namespace with each dot replaced by one underscore.
Existing underscores are preserved, and no leading namespace segment is removed.

| Schema namespace | C namespace component |
| --- | --- |
| `storage` | `storage` |
| `metrics_provider` | `metrics_provider` |
| `logos.runtime_control` | `logos_runtime_control` |

**Module symbols.** Module identity, lifecycle, provider-control, and memory-management symbols use
`logos_<module>_<operation>`.
The `<module>` component is the concrete runtime module name from `_module`.
A header set containing exactly one non-common schema document with a simple namespace omits its document-role namespace constant when Section 3.2 can recover the document role.

A non-common schema document has exactly one document-role namespace constant when the header set contains multiple non-common schema documents, its namespace is not simple, or its role is not recoverable under Section 3.2.
A concrete module document uses `LOGOS_<MODULE>_PRIMARY_NAMESPACE`, an interface document uses `LOGOS_<NAMESPACE>_INTERFACE_NAMESPACE`, and a supporting document uses `LOGOS_<NAMESPACE>_SUPPORTING_NAMESPACE`.
`<MODULE>` is the uppercase runtime module name.
`<NAMESPACE>` is the uppercase C namespace component.
Each string value is the exact schema namespace before C namespace projection.

For example, a multi-document provider header set may contain:

```c
#define LOGOS_STORAGE_MODULE_PRIMARY_NAMESPACE "storage"
#define LOGOS_STORAGE_MODULE_IMPLEMENTS_0 "metrics_provider"
#define LOGOS_METRICS_PROVIDER_INTERFACE_NAMESPACE "metrics_provider"
#define LOGOS_STORAGE_TYPES_SUPPORTING_NAMESPACE "storage_types"
```

Each implemented interface adds one zero-based `LOGOS_<MODULE>_IMPLEMENTS_<INDEX>` string constant.
The constants contain the exact interface namespaces in the ascending raw interface-root order required for `_implements`, with no missing index.
A dotted primary namespace is preserved in the string value while its C declarations use the projected namespace component:

```c
#define LOGOS_LOGOS_RUNTIME_CONTROL_PRIMARY_NAMESPACE \
    "logos.runtime_control"
```

**Method symbols.** A schema method uses
`logos_<module>_call_<namespace>_<method>`.
The `<namespace>` component is the C namespace projection of the contract that defines the method, including when the concrete module implements that contract by reference.
For example, `storage.exists_request` exposed by `storage_module` maps to `logos_storage_module_call_storage_exists`.
The `metrics_provider.snapshot_request` method exposed by the same module maps to `logos_storage_module_call_metrics_provider_snapshot`.

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
| `storage_module` | `storage.init` | `logos_storage_module_call_storage_init` |
| `storage_module` | `storage.upload_url` | `logos_storage_module_call_storage_upload_url` |
| `telemetry_module` | `metrics_provider.snapshot` | `logos_telemetry_module_call_metrics_provider_snapshot` |

The schema method name is used directly in the final C function component.

**Reserved ABI names.** The standard exports `logos_<module>_name`, `_call_surface`, `_init`, `_apply_configuration`, and `_destroy` occupy reserved ABI namespace.
Per-method C functions use the `call` component so schema methods such as `init`
or `destroy` do not collide with required module symbols.
This affects only the generated C symbol names.
The wire method name remains the bare schema method name, for example
`"version"`.

**Type names.** CDDL named types map to `logos_<namespace>_<type_snake>_t`, using the complete C namespace projection:

| CDDL type            | C type                           |
|----------------------|----------------------------------|
| `storage.space_info` | `logos_storage_space_info_t`     |
| `storage.peer_info`  | `logos_storage_peer_info_t`      |
| `logos.runtime_control.state` | `logos_logos_runtime_control_state_t` |

Aggregate struct tags additionally use `logos_<kind>_<namespace>_<name>`, where `<kind>` is `map`, `bstr`, `list`, `tuple`, `choice`, or `event`.
The tag lets the reverse mapper distinguish an aggregate representation from a map that happens to use the same member names.

Types from the Logos common schema surface are prefixed with `logos_` (no module):

| CDDL type           | C type                      |
|----------------------|-----------------------------|
| `logos.error_code`   | `logos_error_code_t`        |

`logos_result_t` is the shared C ABI invocation-status structure.
It is not a schema-defined contract value.

**Canonical order.** Generated forward declarations are ordered by qualified schema name.
Type definitions place dependencies before dependents and break independent ties by qualified schema name.
All remaining declarations are ordered by qualified schema name.
Struct fields and the corresponding method parameters are ordered by ascending lexicographic order of their valid UTF-8 field-name bytes.
Choice arms use the canonical arm order defined by LOGOS-MODULE-COMMITMENT-MODEL.
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

An exact-size byte string maps to an array so its size remains part of the C declaration:

```c
uint8_t digest[32]; /* bstr .size 32 */
```

An exact-size byte-string function input uses a pointer to the complete array type such as `const uint8_t (*digest)[32]`, so ordinary C parameter adjustment does not erase the bound.

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
typedef struct logos_map_storage_space_info {
    uint64_t available;
    uint64_t quota;
    uint64_t used;
} logos_storage_space_info_t;
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
typedef struct logos_map_storage_peer_info {
    const char* id;
    bool        has_name;
    const char* name;       /* valid only if has_name == true */
} logos_storage_peer_info_t;
```

**Arrays.** Variable-length arrays map to pointer + count:

| CDDL type       | C type                                 |
|------------------|----------------------------------------|
| `[* tstr]`       | `const char* const* items, size_t count` |
| `[* uint64]`     | `const uint64_t* items, size_t count`  |
| `[* T]` (struct) | `const logos_T_t* items, size_t count` |

Fixed-length tuples preserve positional order.
A named tuple uses struct members `item_0`, `item_1`, and so on.
A tuple used inline as field `x` uses adjacent members or parameters `x_0`, `x_1`, and so on.
The reverse mapper removes those generated components and reconstructs the tuple positions.

Byte strings use the same adjacent pointer-and-length representation in structs and function signatures.
For a bounded byte string, the pointer has the canonical constraint typedef from Section 2.2.
An implementation MUST treat a pointer-and-length pair as one schema field and MUST keep the pair adjacent.

**Named aliases and aggregates.** Every named CDDL type retains its declaration identity in C:

- A named scalar or constrained string uses a `typedef` to its canonical scalar or constraint type.
- A named map uses the canonical `logos_map_` struct form above.
- A named byte string uses a struct with adjacent `data` and `len` members, except that an exact-size byte string uses one `data[N]` member.
- A named variable-length list uses a struct with adjacent `items` and `count` members.
- A named tuple uses a struct with `item_<index>` members.
- A named choice uses the enum-and-union form below.

An inline map or choice receives a deterministic path-derived type name using the same representation.
A named aggregate or inline map-or-choice method input is passed as `const <type>*`;
its output is passed as caller-allocated `<type>*`.

**Literals.** A literal uses the C representation of its scalar base type and a canonical macro containing its exact required value.
Outside a choice, the macro name is the uppercase qualified owner and field path followed by `_LITERAL`.
A generated encoder MUST emit the required literal, and a provider or decoder MUST reject another value.

**Choices (tagged unions).** Type choices map to tagged unions:

```cddl
storage.value = uint64 / tstr / bool
```

```c
typedef enum {
    LOGOS_STORAGE_VALUE_ARM_0 = 0,
    LOGOS_STORAGE_VALUE_ARM_1 = 1,
    LOGOS_STORAGE_VALUE_ARM_2 = 2,
} logos_storage_value_kind_t;

typedef struct logos_choice_storage_value {
    logos_storage_value_kind_t kind;
    union {
        bool        arm_0;
        const char* arm_1;
        uint64_t    arm_2;
    } value;
} logos_storage_value_t;
```

Choice arms are first normalized into the canonical choice-arm order defined
by LOGOS-MODULE-COMMITMENT-MODEL.
The generated C discriminant order follows that canonical normalized order,
not the source CDDL declaration order.
Source order may be retained for diagnostics, but it is not ABI-visible.
The canonical arm order in this example is `bool`, `tstr`, and `uint64`.

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

The tag field is normal schema data.
It is encoded as part of the selected map alternative and is not an extra
transport wrapper.
Generated bindings MAY represent a required literal tag field through the generated choice discriminant instead of exposing it as a writable C field.
Encoders MUST still emit the literal tag field in the CBOR map.

A choice used inline receives the deterministic C type name formed from its enclosing qualified definition name and field path followed by `_choice_t`.
Choice arms and union members use `ARM_<index>` and `arm_<index>`, where the zero-based index is the canonical arm position.
Each literal choice arm or literal tag field in a map arm additionally generates a C `#define` whose replacement value is the exact C scalar literal.
The macro name is the choice type prefix followed by `ARM_<index>`, the tag field name when applicable, and `_LITERAL`.
This ordinary C constant preserves the literal value for reverse mapping even when the writable C representation omits a fixed tag field.

For example, the tagged `storage.entry` choice above includes constants equivalent to:

```c
#define LOGOS_STORAGE_ENTRY_ARM_0_KIND_LITERAL "file"
#define LOGOS_STORAGE_ENTRY_ARM_1_KIND_LITERAL "dir"
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
typedef logos_result_t (*logos_storage_call_exists_fn)(
    logos_module_context_t* module,
    const char*             cid,
    bool*                   out_exists
);

logos_result_t logos_storage_module_call_storage_exists(
    logos_module_context_t* module,
    const char*            cid,          /* from request map */
    bool*                  out_exists    /* from response map */
);
```

**Rules:**

1. First parameter is always `logos_module_context_t* module`.
   The module returned this opaque per-instance context from its lifecycle initializer.
   The ABI caller MUST pass the same context to every instance-dependent call for that initialized module instance.
2. Request map fields expand to input parameters in canonical field-name order.
   Names are derived directly from the CDDL key.
3. Response map fields expand to output parameters in canonical field-name order, appended after all input parameters and prefixed with `out_`.
4. A scalar response field uses a pointer to its canonical C scalar type.
   A `tstr` response field uses `const char** out_<name>` and transfers the returned string under Section 2.7.
5. If the response map is empty (`{}`), there are no output parameters.
   `result.code == LOGOS_OK` indicates that the invocation produced the valid empty response.
6. Unbounded and ranged `bstr` fields expand to adjacent pointer-and-length parameters.
   A ranged byte string uses its canonical constrained pointer typedef.
   An exact-size byte-string input uses `const uint8_t (*<name>)[N]`, and its caller-allocated output uses `uint8_t (*out_<name>)[N]`.
   An exact-size byte string has no length parameter.
7. A variable-length list input uses adjacent `const <type>* <name>` and `size_t <name>_count` parameters.
   Its output uses adjacent `<type>** out_<name>` and `size_t* out_<name>_count` parameters.
8. Named aggregates and inline map or choice values use the pointer forms defined in Section 2.3.
9. The function always returns `logos_result_t` as its invocation status.

Every method generates a defining-contract function typedef named
`logos_<namespace>_call_<method>_fn`.
An interface contract header contains this typedef without claiming a concrete provider symbol.
A concrete provider header declares `logos_<module>_call_<namespace>_<method>` with exactly the typedef's return type and parameters.
The provider declaration attaches that complete contract method to the concrete module;
the typedef makes the interface contract independently representable in ordinary C.

For an optional request field `x`, the input parameters are adjacent `bool has_x` and the ordinary input representation of `x`.
For an optional response field `x`, the output parameters are adjacent `bool* out_has_x` and the ordinary output representation of `x`.
The value parameter is ignored when its presence flag is false.
This is the function-parameter form of the same `has_<field>` convention used by structs.

Schema-defined outcomes, including expected failures, use the response output parameters
and require `result.code == LOGOS_OK`.

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
logos_result_t logos_storage_module_call_storage_space(
    logos_module_context_t*     module,
    logos_storage_space_info_t* out_info
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
logos_result_t logos_storage_module_call_storage_upload_url(
    logos_module_context_t* module,
    uint64_t               chunk_size,
    const char*            url,
    bool*                  out_accepted
);
```

### 2.5 Event Type Mapping

Event types generate a C struct for the event payload:

```cddl
storage.upload_progress_event = {
    bytes_sent: uint64,
    bytes_total: uint64,
    session: tstr,
}
```

```c
typedef struct logos_event_storage_upload_progress_event {
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
    const char* session;
} logos_storage_upload_progress_event_t;
```

The common C declarations in Section 5.2 define
`logos_route_subscribe()`,
`logos_route_unsubscribe()`,
`logos_subscription_id_t`,
and `logos_event_handler_t`.
These functions operate on a consumer-bound exact-contract route.
They are caller-side binding operations,
not module ABI symbols exported by a provider implementation.
`event_name` MUST be the exact schema event identifier selected by the route.
The event MUST be allowed by the route's allowed event scope.

`logos_route_subscribe()` returns `LOGOS_OK` only after the subscription is active.
On success, it writes an identifier scoped to that route into `*out_subscription_id`.
No handler invocation for that subscription may begin before the function returns.
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

An external `logos_route_unsubscribe()` call returns `LOGOS_OK` only after
the subscription is inactive,
every active handler invocation has returned,
and no later invocation can begin.
If a handler calls `logos_route_unsubscribe()`
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

The caller MUST keep `handler` and `user_data` valid
until an external unsubscription returns,
until every handler frame active during self-unsubscription has returned,
or until route-handle release returns.

Direct delivery follows Section 2.8.
A transported binding maps these operations to the subscription lifecycle
defined by LOGOS-MODULE-TRANSPORT.

A generator MAY produce a typed helper for each event:

```c
typedef void (*logos_storage_upload_progress_handler_t)(
    const logos_storage_upload_progress_event_t* event,
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

- `logos_<module>_name()` returns the module name as a static string that
  remains valid for the implementation-binding lifetime.
- `logos_<module>_init()` receives one structured initialization input and
  creates one module-owned context for one module instance.
- `logos_<module>_destroy()` destroys one successfully initialized context.
The identity and lifecycle symbols do not make the module a provider.
`logos_<module>_apply_configuration()` is the optional standard ABI hook for applying configuration after initialization.
A specification that assigns configuration semantics determines when the hook is required and defines its payload and outcome semantics.
A module that is not required to support live configuration application need not export it.

A native module that exposes at least one callable contract MUST additionally make these provider symbols available to its ABI caller:

- `logos_<module>_call_surface()` returns one deterministic-CBOR provider
  call-surface descriptor containing the module's optional primary contract
  and every implemented interface contract;
- `logos_<module>_free()` releases dynamic response values transferred by this
  module instance across the provider ABI;
- `logos_<module>_dispatch()` dispatches a schema method name and deterministic
  CBOR request payload to the corresponding schema-defined method.
  It is a module ABI symbol, not a schema method.

Such a provider module MUST also make the schema-derived per-method C functions specified in section 2.4 available to its ABI caller.
The per-method C functions are the typed native provider ABI.
`logos_<module>_dispatch()` is the generic deterministic-CBOR dispatch entrypoint.
It accepts a bare method name and deterministic-CBOR request bytes
and returns the final method result and response.
Provider modules MUST expose both surfaces,
which MUST implement the same request, response, error, and selected-contract semantics.
A module with no callable contract MUST NOT be required to export
`_call_surface()`, `_free()`, `_dispatch()`, or a schema-derived per-method function.

If a concrete module declares `_implements`,
its full Logos ABI MUST cover the primary module methods
and every implemented interface method.
Code generation is the expected path.
A hand-written module MUST expose behavior equivalent to the same concrete contract set.

`logos_<module>_dispatch()` MUST NOT be listed as a method in the module schema,
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
The same pointer MUST be passed to every instance-dependent ABI call for that module instance and MUST be passed exactly once to `logos_<module>_destroy()`.

For ABI preconditions, a module context is live from successful `_init()` return
until the ABI caller begins that context's single `_destroy()` call after quiescence.
`_destroy()` consumes the live context.
The context is bound to that module instance and implementation binding.
Passing a null context, a context belonging to another instance or implementation,
or a context whose destruction has begun violates the caller's ABI precondition.
This specification assigns no `logos_error_code_t` value to that misuse
because no conforming ABI invocation occurs.
A higher-level binding MAY reject an invalid handle that it can identify
using its own precondition mechanism before entering the C ABI.
The native ABI does not require safe detection of an arbitrary forged or stale pointer.

The initialization input is borrowed only for the duration of `_init()`.
The Runtime Control binding, publish callback, and opaque publish state remain valid and unchanged from `_init()` entry until `_destroy()` returns.
The state-directory string is borrowed only for the duration of `_init()`.
The module MAY copy it into its context,
but it MUST NOT retain the supplied pointer.
The corresponding module-visible directory mapping remains established until destruction begins.
Configuration bytes are borrowed only for the duration of `_init()`.
The module MAY copy or decode them into its module context, but it MUST NOT retain their pointer.
A module MAY copy those fields into its module context,
but it MUST NOT retain the initialization-input pointer itself.
A null publish callback is unavailable for that instance and MUST NOT be called.

Before calling `_init()`,
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
const char* logos_<module>_name(void);

/* Create one module instance from one structured initialization input. */
logos_result_t logos_<module>_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

/* Apply one complete configuration to a live-reconfigurable module instance. */
logos_result_t logos_<module>_apply_configuration(
    logos_module_context_t* module,
    const uint8_t*          configuration_cbor,
    size_t                  configuration_cbor_len
);

/* Destroy one successfully initialized module instance. */
void logos_<module>_destroy(logos_module_context_t* module);

/* Provider-only call-surface metadata and memory-management symbols. */
const uint8_t* logos_<module>_call_surface(size_t* out_len);
void logos_<module>_free(logos_module_context_t* module, void* ptr);

/* Provider-only deterministic-CBOR dispatch entrypoint. */
logos_result_t logos_<module>_dispatch(
    logos_module_context_t* module,
    const char*             method,
    const uint8_t*          params_cbor,
    size_t                  params_len,
    uint8_t**               out_response_cbor,
    size_t*                 out_response_len
);
```

`logos_<module>_call_surface()` returns the deterministic-CBOR encoding of
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
matches `logos_<module>_name()`.
Each `interfaces` document MUST be an interface contract schema.
Its `_interface` value MUST equal its derived primary schema namespace.
Interface documents MUST NOT declare `_implements`.

An interface entry's `supporting_schemas` array MUST be empty.
The primary entry's `supporting_schemas` array MUST contain all and only the supporting schemas referenced by its module document.
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
invalid schema-role metadata, a bare method-name collision across the described contracts,
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
In deterministic-CBOR and transport invocation paths, the ABI caller MAY call `logos_<module>_dispatch()`.
For dispatch calls, `method` is the bare schema method name after the target
module has already been selected.
`params_cbor` is the deterministic CBOR request map for that method, not the
full Transport Request envelope.
On success, `out_response_cbor` receives the deterministic CBOR response map for that method.
The returned response buffer is released with
`logos_<module>_free(module, out_response_cbor)`.

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

**Important distinction: lifecycle `_init()` vs schema method `init`.**

The lifecycle symbol `logos_<module>_init(input, out_context)` is part of the native module ABI.
The ABI caller calls it after binding the native implementation and before any instance-dependent ABI entry point is invoked.
It creates instance state and receives the Runtime services available to that instance.

If a module schema also declares an ordinary method named `init` (for example
`storage.init_request` / `storage.init_response`), that method is a normal
schema-defined request/response method with C symbol
`logos_<module>_call_<namespace>_init` and wire method name `"init"`. It is distinct from
the lifecycle symbol and MAY perform application-level setup
that remains necessary after lifecycle `_init()` has succeeded.

Successful lifecycle `_init()` therefore means:

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

The provider ABI therefore defines a module-owned deallocation function for
dynamic response values whose ownership crosses the module boundary:

```c
void logos_<module>_free(logos_module_context_t* module, void* ptr);
```

**Lifetime rules:**

- The module context remains owned by the module from successful `_init()` until `_destroy()`.
  ABI callers borrow it and MUST NOT dereference, modify, serialize, or free it.
- Request arguments are borrowed until the provider C function returns.
  The provider MUST NOT retain them.
- The `message` and `detail` storage referenced by a `logos_result_t` returned from an instance-dependent provider C function remains valid until the next ABI call using the same module context begins or until `_destroy()` begins, whichever occurs first.
  The ABI caller MUST copy `message` and `detail` before that point if it needs to retain, encode, or forward them.
  The ABI caller MUST NOT begin another call using that context until any required copy is complete.
  A call already in progress when the result is returned does not shorten this lifetime.
- The corresponding storage returned by `_init()` remains valid until the next `_init()` call for the same implementation binding begins or until that binding is released, whichever occurs first.
- A successful dispatch transfers ownership of `out_response_cbor` to the caller.
  The caller releases it with the same module instance's `logos_<module>_free(module, ptr)`.
- For caller-side runtime handles or generated caller helpers,
  `logos_result_t.message` and `.detail` are valid until the next Logos call on
  the same handle or helper-owned call state.
  Callers MUST copy these fields to retain them.
- Output pointers (`out_*`) for dynamically-sized data (`tstr`, `bstr`,
  arrays) are allocated by the typed provider.
  Callers MUST free them with the same module instance's
  `logos_<module>_free(module, ptr)`.
- Output structs are caller-allocated.
  The typed provider fills them in.
  Any dynamic fields within the struct are provider-allocated and freed with
  the same module instance's `logos_<module>_free(module, ptr)`.
- `_name()` returns a static string, and `_call_surface()` returns static bytes.
  Callers MUST NOT free any of them.
- `logos_<module>_free(module, NULL)` MUST be a no-op.

The module that allocates memory owns the corresponding deallocator.
In direct mode, the ABI caller or generated caller helper obtains the deallocator from the same module binding that produced the response output.
Across process, sandbox, container, or remote boundaries, raw pointers do not
cross the boundary; the side that decodes serialized data owns and frees its
own decoded allocations.

### 2.8 Native ABI Concurrency

This section defines the complete concurrency contract visible to native module implementations and ABI callers.
Runtime scheduling mechanisms do not add requirements to that contract.

The context-free `_name()` and `_call_surface()` entry points MAY be called concurrently
with one another and with operations on any context from the same implementation binding.
The implementation MUST make those calls safe without caller-side serialization.

Distinct `_init()` calls for the same implementation binding MAY execute concurrently.
Each successful call creates an independent context.
The implementation MUST synchronize state shared across contexts.

After successful initialization,
the ABI caller MAY invoke schema-derived provider functions and `_dispatch()` concurrently with the same live context.
`_apply_configuration()` MAY execute concurrently with provider calls,
but the ABI caller MUST NOT invoke two `_apply_configuration()` calls concurrently with the same context.
The module MUST synchronize its per-instance state.
A module that requires serial execution MAY implement internal serialization;
the ABI caller is not required to serialize provider calls.

`logos_<module>_free(module, ptr)` MAY be called from any thread
and concurrently with other calls using the same live context.
The module MUST synchronize its allocator state.

Operations through one Runtime Control binding MAY be initiated concurrently from multiple module threads.
The binding implementation MUST make those operations thread-safe
while preserving the operation ordering defined by LOGOS-MODULE-RUNTIME.

The module MAY invoke its publish callback concurrently from multiple threads while its context remains live.
The callback implementation MUST be thread-safe.

In direct mode, a publish call MUST invoke every applicable direct subscriber callback synchronously
on the publishing thread before the publish call returns.
The callback interval therefore applies natural backpressure to the publisher.
An implementation MUST NOT move a direct subscriber callback to another thread
or return from publication before that callback completes.

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

Direct provider calls execute synchronously on the calling thread.
Transported invocation may enter the provider on different threads
and may complete independent calls out of order.
A module MUST NOT depend on a fixed provider-call thread
or on Runtime-provided call serialization.

Before `_destroy(module)` begins,
the ABI caller MUST stop new instance-dependent calls,
wait for every in-flight call to return,
and release every transferred output associated with the context.
`_destroy()` MUST NOT execute concurrently with another call using that context.
Before `_destroy()` returns,
the module MUST stop or join internal work
that could later use the context, Runtime Control binding, publish callback, or publish state.
After `_destroy()` returns, none of those values remains valid.

---

## 3. Canonical C-to-CDDL Mapping

This section defines the reverse direction from canonical C declarations to the Logos canonical schema model and CDDL.
The mapping input is the complete accepted header set after resolving ordinary C includes but before macro definitions are discarded.
It is a source-level C profile.
ABI-equivalent declarations are not interchangeable for reverse mapping when they erase a canonical typedef name, array bound, presence pair, or literal constant.

Both the declaration-only C form and the metadata-extended C form are valid schema-authoring inputs.
The reverse mapper MUST derive every unambiguous schema fact from canonical C declarations and MUST require schema-metadata constants only for the remaining facts identified by this section.
CDDL is the recommended authoring form when a contract requires substantial schema metadata, but the metadata-extended C form remains a complete C representation of every accepted schema set.

### 3.1 Allowed C Subset

The reverse mapper accepts the exact declaration forms produced by Section 2:

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
| `uint8_t[N]` | `bstr .size N` |
| `logos_<namespace>_<type>_t` | Named schema type |
| `const T*` + `size_t` (pair) | `[* T]` (array) |
| `logos_result_t` | (return type only; maps to invocation status) |
| `logos_module_context_t*` | (first param only; not in CDDL) |

The mapper recognizes canonical choice enums and unions, literal macros, tuple members, and constrained typedefs only in the forms defined by Section 2.
It validates the complete declaration group before deriving schema nodes.

**Disallowed C constructs in the API surface:**

- `void*` (except for `logos_module_init_input_t.publish_user_data` and `logos_<module>_free`)
- Raw pointers that are not part of a canonical text, byte-string, list, exact-array, output, context, or opaque-handle representation defined by this specification
- Function pointers other than the canonical generated method-signature typedefs
- `float` and `double` (reserved for a future deterministic numeric profile)
- Bitfields, bit-packed structs
- `enum` not declared as `logos_*_t` (use explicit integer types or declared enums)

Every accepted text argument is a valid UTF-8 NUL-terminated string.
An implementation that receives or constructs a text value containing U+0000 does not have a conforming canonical C value.
Schema-bearing declarations and constants MUST NOT depend on conditional compilation other than an include guard.

### 3.2 Contract and Namespace Recognition

A namespace group is the complete set of schema-derived declarations assigned to one exact schema namespace.
The pinned `logos` common group is recognized from the fixed common-schema declarations and does not use document-role namespace metadata.

For a header set containing exactly one non-common namespace group whose namespace is simple, the reverse mapper obtains the exact namespace from the first underscore-delimited component in each schema-derived C name.
Every declaration MUST yield the same namespace.
The mapper derives the document role from its contents:

- A consistent `logos_<module>_` lifecycle symbol family makes the document a concrete module schema and supplies `_module`.
- Without lifecycle symbols, at least one method or event makes the document an interface contract schema and supplies `_interface` from the inferred namespace.
- Without lifecycle symbols, methods, or events, the document is a supporting schema.

A simple types-only interface therefore requires interface-role metadata.
The declaration-only form cannot express `_implements` or more than one non-common schema document.

For every namespace group not covered by that inference rule, a document-role namespace constant supplies its exact namespace and role.
The projection of the constant's string value MUST equal the C namespace component of every declaration in that group.
For a primary-namespace constant, the macro's module component MUST equal the `_module` value derived from the lifecycle symbol family.
For an interface- or supporting-namespace constant, the macro's namespace component MUST equal the uppercase C namespace projection of its string value.

Each `LOGOS_<MODULE>_IMPLEMENTS_<INDEX>` constant names one complete interface group by its exact namespace.
The reverse mapper computes that interface's schema root and emits it in `_implements`.
The indices MUST be contiguous and follow ascending raw interface-root order.
A referenced namespace group is not implemented unless an implementation constant names it.
A provider method declaration for a non-primary namespace requires the corresponding implementation constant.

A primary-group reference to a type in a supporting group reconstructs an imported named-type reference to that supporting schema.
The reverse mapper computes the supporting schema root from the reconstructed group.
The pinned common group always maps to common-schema references and never generates `_implements`.

The reverse mapper MUST reject any of the following:

- an incomplete namespace group;
- two conflicting definitions of the same qualified name;
- a method whose request or response half is missing;
- a missing or unnecessary document-role namespace constant;
- a document-role namespace constant whose exact value, projection, prefix, or role does not match its declaration group;
- an implemented-interface constant without one complete matching group;
- a provider declaration for a non-primary contract that lacks the corresponding implemented-interface constant;
- a supporting-schema group that contains a method or event declaration;
- when the input contains a concrete provider header, a supporting-schema group not referenced by its primary group;
- a missing or non-contiguous implemented-interface index; or
- a generated-identifier or namespace-projection collision.

### 3.3 Function Signature Recognition

The codegen tool recognizes contract method typedefs by pattern:

```c
typedef logos_result_t (*logos_<namespace>_call_<method>_fn)(
    logos_module_context_t* module,
    <input params...>,
    <output params...>
);
```

The typedef reconstructs the defining request/response pair.
A concrete provider function is recognized by pattern:

```c
logos_result_t logos_<module>_call_<namespace>_<method>(
    logos_module_context_t* module,
    <input params...>,
    <output params...>        /* out_ prefix */
);
```

- The `logos_module_context_t*` first parameter is stripped (not in CDDL).
- Input parameters (no `out_` prefix) become request map fields.
- Output parameters (`out_` prefix, pointer types) become response map fields.
- `logos_result_t` return is stripped (invocation status, not CDDL data).
- An adjacent `has_<field>` and value pair makes a request field optional.
- An adjacent `out_has_<field>` and output-value pair makes a response field optional.
- Adjacent `_len` and `_count` parameters are consumed as part of their byte-string or list field.
- The namespace and method components identify the request/response qualified names.

A provider function MUST exactly match the corresponding defining-contract typedef.
Its module component attaches that contract method to the concrete provider but does not create another schema declaration.

**Parameter name to CDDL key:** parameter names are used directly.
`chunk_size` -> `chunk_size`.

**Example:**

```c
logos_result_t logos_storage_module_call_storage_upload_url(
    logos_module_context_t* module,
    uint64_t               chunk_size,
    const char*            url,
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

### 3.4 Named Type and Struct Recognition

Canonical typedefs and aggregate declarations matching `logos_<namespace>_<name>_t` reconstruct named schema types.
An aggregate tag's `logos_<kind>_` component determines which schema construct it represents.
A `logos_map_` struct with schema fields reconstructs a named map:

```c
typedef struct logos_map_storage_space_info {
    uint64_t available;
    uint64_t quota;
    uint64_t used;
} logos_storage_space_info_t;
```

Generates:

```cddl
storage.space_info = {
    available: uint64,
    quota: uint64,
    used: uint64,
}
```

Optional fields (those with a preceding `bool has_<field>`) generate
`? key: type` in CDDL.
Adjacent pointer-and-length or pointer-and-count members generate one byte-string or list field.
Members MUST appear in canonical field-name order, with each presence, length, or count member adjacent to the value it qualifies.
A canonical `logos_bstr_`, `logos_list_`, or `logos_tuple_` tag MUST contain only its corresponding `data` and `len`, `data[N]`, `items` and `count`, or `item_<index>` members.

### 3.5 Choice and Literal Recognition

A canonical `logos_<namespace>_<name>_kind_t` enum followed by its matching union-bearing `logos_<namespace>_<name>_t` reconstructs one choice.
Enum order MUST equal canonical choice-arm order.
An inline choice type name reconstructs its enclosing field path rather than a new named CDDL declaration.

A canonical `_LITERAL` macro supplies the exact scalar value for every literal node,
including a choice arm or tagged-map tag field.
The reverse mapper MUST reject a missing literal macro, a replacement value of the wrong scalar type, or a macro whose arm and tag-field components do not match the associated choice declaration.

### 3.6 Event Struct Recognition

C structs matching `logos_<namespace>_<name>_event_t` are recognised as events:

```c
typedef struct logos_event_storage_upload_progress_event {
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
    const char* session;
} logos_storage_upload_progress_event_t;
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

The module ABI symbols (`_name`, `_call_surface`, `_init`, `_apply_configuration`, `_destroy`, `_free`, and `_dispatch`) are recognised by name and excluded from the CDDL schema.
They are identity, lifecycle, or provider-control symbols,
not schema-defined module methods.
The `_free` suffix refers to the module-prefixed `logos_<module>_free` symbol.

### 3.8 Roundtrip Guarantee

The round-trip guarantee preserves the Logos canonical schema model.
It does not preserve the spelling or layout of hand-authored C source.

For any conformant C header set `H`:

```
H -> (C-to-CDDL) -> schema.cddl -> (CDDL-to-C) -> H'
```

`H'` MUST be the canonical declaration-only or metadata-extended C representation of the schema model reconstructed from `H`.
Mapping `H'` back to CDDL MUST reproduce that same schema model.

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

#### 3.9.1 Declaration-Only Module

The following concrete module schema uses a simple namespace and requires no schema metadata beyond its C declarations:

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
  reading: meter.reading,
}
```

Its canonical module-specific C declarations are:

```c
typedef struct logos_event_meter_changed_event {
    uint64_t value;
} logos_meter_changed_event_t;

typedef struct logos_map_meter_reading {
    bool        has_label;
    const char* label;
    uint64_t    value;
} logos_meter_reading_t;

typedef logos_result_t (*logos_meter_call_read_fn)(
    logos_module_context_t* module,
    uint32_t                channel,
    logos_meter_reading_t* out_reading
);

logos_result_t logos_meter_module_call_meter_read(
    logos_module_context_t* module,
    uint32_t                channel,
    logos_meter_reading_t* out_reading
);

const char* logos_meter_module_name(void);

logos_result_t logos_meter_module_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

void logos_meter_module_destroy(logos_module_context_t* module);

const uint8_t* logos_meter_module_call_surface(size_t* out_len);
void logos_meter_module_free(logos_module_context_t* module, void* ptr);

logos_result_t logos_meter_module_dispatch(
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

The declaration set MUST NOT contain a document-role namespace constant, an implementation constant, an event-name constant, or a literal constant.
Generating C from the schema and then reconstructing CDDL from the generated declarations MUST produce the same canonical schema model.

#### 3.9.2 Metadata-Extended Construction Set

The following construction input set contains one concrete module document, one implemented interface document, and one supporting document.
It exercises metadata that canonical C declarations cannot recover by themselves.

The concrete module document is:

```cddl
; -- metadata --
_module = "sensor_module"
_implements = [
  h'ca004a96bbbce568ab0e7f996020e12d0dca353603671d5d6d8d5e364b830d32',
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

The interface document's schema root under LOGOS-MODULE-COMMITMENT-MODEL is `ca004a96bbbce568ab0e7f996020e12d0dca353603671d5d6d8d5e364b830d32`.
That root is the direct byte-string literal in the module document's `_implements` array.

The canonical module-specific C declarations and schema-metadata constants are:

```c
#define LOGOS_SENSOR_MODULE_PRIMARY_NAMESPACE "sensor.control"
#define LOGOS_SENSOR_MODULE_IMPLEMENTS_0 "metrics_provider"
#define LOGOS_METRICS_PROVIDER_INTERFACE_NAMESPACE "metrics_provider"
#define LOGOS_METRICS_TYPES_SUPPORTING_NAMESPACE "metrics_types"
#define LOGOS_SENSOR_CONTROL_SETTINGS_KIND_LITERAL "sensor"

typedef uint64_t logos_metrics_types_counter_t;

typedef struct logos_map_sensor_control_settings {
    const char*                  kind;
    logos_metrics_types_counter_t limit;
} logos_sensor_control_settings_t;

typedef logos_result_t (*logos_metrics_provider_call_snapshot_fn)(
    logos_module_context_t* module,
    uint64_t*               out_count
);

logos_result_t logos_sensor_module_call_metrics_provider_snapshot(
    logos_module_context_t* module,
    uint64_t*               out_count
);

typedef logos_result_t (*logos_sensor_control_call_configure_fn)(
    logos_module_context_t*                module,
    const logos_sensor_control_settings_t* settings
);

logos_result_t logos_sensor_module_call_sensor_control_configure(
    logos_module_context_t*                module,
    const logos_sensor_control_settings_t* settings
);

const char* logos_sensor_module_name(void);

logos_result_t logos_sensor_module_init(
    const logos_module_init_input_t* input,
    logos_module_context_t**         out_context
);

void logos_sensor_module_destroy(logos_module_context_t* module);

const uint8_t* logos_sensor_module_call_surface(size_t* out_len);
void logos_sensor_module_free(logos_module_context_t* module, void* ptr);

logos_result_t logos_sensor_module_dispatch(
    logos_module_context_t* module,
    const char*             method,
    const uint8_t*          params_cbor,
    size_t                  params_len,
    uint8_t**               out_response_cbor,
    size_t*                 out_response_len
);
```

The document-role constants reconstruct the three exact namespace boundaries and roles.
The C namespace component `sensor_control` reconstructs `sensor.control` because the primary-namespace constant supplies the dotted spelling.
The implementation constant selects the complete `metrics_provider` interface group, whose recomputed root MUST equal the `_implements` literal shown above.
The reference to `logos_metrics_types_counter_t` reconstructs an imported reference to `metrics_types.counter` rather than an inline `uint64` node.
The literal constant constrains `sensor.control.settings.kind` to the text value `"sensor"`.

Generating C from the three documents and then reconstructing CDDL from the generated header set MUST reproduce all three canonical schema models and the exact implementation relationship.
The generated header set MUST NOT contain an event-name constant or any other schema-metadata constant not shown above.

#### 3.9.3 Required Rejections

Each case in the following table starts from the complete C declaration set named in the Input column and applies only the stated mutation.
The mapper MUST reject the resulting header set before emitting CDDL.
The required condition identifies the normative reason for rejection; diagnostic text is implementation-defined.

| Case | Input | Mutation | Required rejection condition |
| --- | --- | --- | --- |
| `C-DECL-REDUNDANT-ROLE` | Section 3.9.1 | Add `#define LOGOS_METER_MODULE_PRIMARY_NAMESPACE "meter"`. | The document role and simple namespace are already recoverable, so the schema-metadata constant is unnecessary. |
| `C-EXT-MISSING-PRIMARY` | Section 3.9.2 | Delete `LOGOS_SENSOR_MODULE_PRIMARY_NAMESPACE`. | A multi-document header set requires a document-role namespace constant for every non-common document. |
| `C-EXT-BAD-PRIMARY-PROJECTION` | Section 3.9.2 | Replace the primary-namespace value with `"sensor.runtime"`. | The value projects to `sensor_runtime`, which does not match the `sensor_control` declaration group. |
| `C-EXT-MISSING-INTERFACE-ROLE` | Section 3.9.2 | Delete `LOGOS_METRICS_PROVIDER_INTERFACE_NAMESPACE`. | The implemented interface group has no document-role namespace constant. |
| `C-EXT-MISSING-IMPLEMENTS` | Section 3.9.2 | Delete `LOGOS_SENSOR_MODULE_IMPLEMENTS_0`. | The concrete provider declares a non-primary interface method without the required implementation relationship. |
| `C-EXT-WRONG-LITERAL-TYPE` | Section 3.9.2 | Replace the settings literal value with `7u`. | The literal replacement has unsigned-integer type, but the associated C field has text-string type. |
| `C-EXT-UNSUPPORTED-DOUBLE` | Section 3.9.2 | Add `typedef double logos_sensor_control_temperature_t;`. | `double` is outside the allowed schema-bearing C subset. |

The following isolated header set is the required namespace-projection-collision case:

```c
#define LOGOS_A_B_INTERFACE_NAMESPACE "a.b"
#define LOGOS_A_B_SUPPORTING_NAMESPACE "a_b"

typedef uint64_t logos_a_b_value_t;
```

Both exact namespaces project to the same `a_b` C namespace component and claim the same declaration group.
The mapper MUST reject the header set as a namespace-projection collision.

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
2. Integers MUST use the shortest possible encoding.
3. Indefinite-length encodings MUST NOT be used.
4. Duplicate map keys MUST NOT appear.
5. Floating-point values are not part of Logos module schemas in this
   revision.

The Logos deterministic CBOR profile is a Logos-owned application profile over
the CBOR data model and core deterministic encoding requirements in RFC 8949.

### 4.5 Validation

Implementations MUST:

1. Reject any incoming deterministic CBOR that violates the determinism rules
   in section 4.4 with error code `INVALID_PARAMS`.
2. Produce outgoing deterministic CBOR that satisfies section 4.4 in every build mode.
   An implementation MAY elide a separate validation pass when its encoder guarantees those requirements by construction.
   Debug and release builds MUST NOT emit different bytes for the same schema-typed value.
3. Reject unknown method names -> error code `METHOD_NOT_FOUND`.
4. Reject wrong parameter types or missing required fields ->
   error code `INVALID_PARAMS`.

For module method payloads, schema validation is owned by the module dispatch
layer generated from or implemented against the module's CDDL schema.
The runtime and transport layers validate envelopes and routing fields.
They MUST NOT be required to introspect module payload schemas while forwarding
local or remote transport calls.

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
such as malformed deterministic CBOR or an unknown Transport message kind.
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
    "schema-mismatch"

logos.invalid_params_path_segment = tstr / uint64

logos.invalid_params_detail = {
    reason: logos.invalid_params_reason,
    ? path: [* logos.invalid_params_path_segment],
}

; -- exact schema commitment --
logos.schema_commitment = {
    commitment_model: "logos.commitment-model.2026-08",
    schema_root: bstr .size 32,
    hash_profile: "logos.hash-profile.2026-08.choice-index",
    hash_suite: "logos.hash-suite.blake3-256",
}

; -- route handle (opaque, not on wire) --
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
Module authors do not declare it.
It is callable only through a ready route whose method access includes the
`logos.schema` declaration root from the pinned Logos common schema surface.

The response MUST contain the CDDL schema document for the route's selected contract and every interface and supporting schema document required to reconstruct that contract.
For a route selected through the provider's primary concrete contract,
the response contains that concrete contract, all and only the interface documents selected by its `_implements` entries, and the exact supporting-schema set validated for it.
For a route selected through an implemented interface contract,
the response contains that interface contract and MUST NOT expose the provider's primary concrete schema
or another implemented interface merely because the same provider implements it.
Its `interface_schemas` and `supporting_schemas` arrays MUST be empty.

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

The module ABI function `logos_<module>_call_surface()` has a different purpose.
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

When `path` is present, its segments identify a path from the rejected value's root.
An empty path identifies the rejected value itself.
A text segment identifies a map key,
and an unsigned-integer segment identifies an array index.

An implementation MUST validate detail before forwarding it or presenting it as structured data.
It MUST reject an enclosing result or error payload whose detail is not allowed or does not validate.
`message` and decoded detail MUST NOT disclose information that the caller is not authorized to observe.
In particular, authorization failures MUST NOT expose policy inputs, matching rules, credentials, provider identities, or host details.

Expected domain and application failures continue to use the selected contract's typed response.
They MUST NOT use this detail channel.

### 5.2 C Definitions (`logos_types.h`)

These C definitions are the C-side common ABI surface used by generated and
hand-written modules and caller-side bindings.
For C-first modules, the reverse mapping in section 3 recognizes these shared
C types and maps them to the corresponding schema or ABI concepts defined by this specification.

- `logos_error_code_t` defines the shared status-code space used at the module boundary.
- `logos_result_t` reports the status of an ABI operation.
  For a schema-defined method invocation,
  `LOGOS_OK` means that the operation produced a valid contract response.
- `logos_result_t.message` is human-readable diagnostic text and MAY be `NULL`.
  When non-null, it MUST contain at most `LOGOS_ERROR_MESSAGE_MAX_LEN` UTF-8 bytes before its terminating null byte.
  It MUST be `NULL` when `code` is `LOGOS_OK`.
- `logos_result_t.detail`, when present, contains one validated structured value as specified in Section 5.1.
  Its length MUST NOT exceed `LOGOS_ERROR_DETAIL_MAX_LEN`.
- `logos_module_context_t` is an opaque per-instance type owned by the module implementation.
- The module creates one distinct live context during each successful `_init()` call.
- The same context is passed to every instance-dependent ABI call and to `_destroy()` exactly once.
- The module context is process-local.
  It MUST NOT be serialized, used as a module identity, or treated as a caller-side routing handle.
- `logos_module_init_input_t` is the size- and version-delimited initialization input supplied to the module by the ABI caller.
- `logos_runtime_control_binding_t` is the opaque process-local binding through which the initialized module invokes the intrinsic Runtime Control contract.
- The Runtime Control binding identifies the initialized module instance as consumer but grants no authority by itself.
- The publish callback attributes published events to the initialized module instance and does not transfer the authority of an inbound caller.
- `logos_module_init_input_t.state_dir`, when non-null, identifies the module-visible persistent-state directory assigned to this module instance.
  It is a NUL-terminated UTF-8 string without an embedded NUL.
  A null value means that no persistent-state directory was assigned.
  The path is coordination data and grants no filesystem authority by itself.
- `logos_route_handle_t` is opaque to callers.
- A route handle is a process-local representation of one consumer-bound, exact-contract route.
- A language binding constructs it from a ready route returned by Runtime Control.
- In direct mode, a handle may wrap function pointers or equivalent
  in-process dispatch state.
  In local transport mode, it may wrap a transport connection or equivalent
  runtime state.
- The execution mode behind a handle is runtime-internal and MUST NOT change
  the module contract seen by callers.
- Route-handle concurrency is defined in Section 2.8.
- `logos_subscription_id_t` identifies one subscription within one route handle.
- `logos_event_handler_t` receives validated encoded event data through a caller-side route binding.
- `logos_<module>_free(module, ptr)` deallocates memory returned by that module
  instance across the module ABI boundary.

```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

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

/* -- Module initialization and per-instance context -- */

/*
 * Module-owned opaque state for one initialized module instance.
 * ABI callers never dereference or free this value.
 */
typedef struct logos_module_context logos_module_context_t;
typedef struct logos_runtime_control_binding logos_runtime_control_binding_t;

#define LOGOS_MODULE_INIT_ABI_VERSION 1u

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
} logos_module_init_input_t;

/* -- Route handle -- */

/*
 * A route handle is the process-local representation of one
 * consumer-bound, exact-contract route returned by Runtime Control.
 *
 * In direct mode, the handle wraps validated provider function pointers.
 * In local or remote transport mode, it wraps the selected invocation path.
 *
 * Concurrency requirements are defined in
 * LOGOS-MODULE-INTERFACE Section 2.8.
 */
typedef struct logos_route_handle {
    /* opaque to callers — fields are binding-internal */
    void* _impl;
} logos_route_handle_t;

/* -- Event subscription -- */

typedef uint64_t logos_subscription_id_t;

typedef void (*logos_event_handler_t)(
    const char*    event_name,
    const uint8_t* cbor_data,
    size_t         cbor_data_len,
    void*          user_data
);

logos_result_t logos_route_subscribe(
    logos_route_handle_t*     route,
    const char*               event_name,
    logos_event_handler_t     handler,
    void*                     user_data,
    logos_subscription_id_t*  out_subscription_id
);

logos_result_t logos_route_unsubscribe(
    logos_route_handle_t*    route,
    logos_subscription_id_t  subscription_id
);

/* -- Memory management -- */

void logos_<module>_free(logos_module_context_t* module, void* ptr);
```

Throughout Logos specifications and conformance assertions, a bare error name denotes the corresponding `logos_error_code_t` enumerator without its `LOGOS_ERR_` prefix; the `LOGOS_ERR_MODULE` and `LOGOS_ERR_TRANSPORT` enumerators use the bare names `MODULE_ERROR` and `TRANSPORT_ERROR`, respectively.

Memory lifetime rules: see section 2.7.

The versioned initialization struct uses `abi_version == 1` in this revision.
`struct_size` is the number of initialized bytes available in that struct.
A receiver MUST NOT read beyond `struct_size`.
Future compatible revisions MAY append fields and increase `struct_size`,
but MUST NOT reorder, remove, or change the meaning of existing fields.
An incompatible layout requires a new `abi_version`.

Before calling `_init()`, the ABI caller MUST populate the ABI version and structure size.
A module that does not support the version or receives a structure too
small to contain the fields defined by that version MUST return
`LOGOS_ERR_VERSION_MISMATCH` and a null context.
Unknown appended fields within a supported version are ignored.

The configuration fields are absent exactly when `configuration_cbor` is `NULL` and `configuration_cbor_len` is zero.
When present, they MUST contain a non-null pointer and nonzero length for exactly one deterministic-CBOR value.
All other pointer-and-length combinations are invalid.
The specification that assigns configuration semantics defines when the fields are absent or present and defines the exact value type and validation requirements.

The ABI caller passes one deterministic-CBOR value to `logos_<module>_apply_configuration()` using a non-null pointer and nonzero length.
The assigning specification defines that value and the operation's outcome semantics.
The bytes are borrowed only for the duration of the call.

The `runtime_control` pointer MUST be non-null and identify the Runtime Control binding for the initialized module instance.
The module MAY invoke authorized Runtime Control methods through that binding during `_init()` and throughout the live context.
The `publish_user_data` value is opaque callback-provider state.
The module MUST pass it back unchanged to `publish`.
When the provider call surface declares any event,
the initialization input MUST contain a non-null `publish` callback.
The Runtime Control binding, callback, and opaque state are process-local and MUST NOT cross a Transport boundary.

### 5.3 Dynamic Schema Validation

Schema text obtained from a module, package, catalog, Runtime, or remote peer is untrusted structured input.
Successful artifact acceptance, provider authorization, or Transport authentication
does not make that text valid and does not authorize any method described by it.

Before using dynamic schema text for dispatch, call-helper generation, validation, routing, or user presentation, an implementation MUST parse and resolve it under the following limits:

- at most 1,048,576 UTF-8 bytes in one schema document;
- at most 8,388,608 UTF-8 bytes across all documents in one schema-construction input set;
- at most 65,536 nodes across all Logos canonical schema models constructed from one schema-construction input set; and
- at most 128 levels of structural nesting in the parsed or canonical model.

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
A cached parsed model MUST be keyed by the exact selected schema identity,
semantic commitment-model revision, hash profile and suite,
and the complete accepted schema input set.

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

| Output file               | Contents                                         |
|--------------------------|--------------------------------------------------|
| `<module>.h`             | C header: contract types and method typedefs, provider declarations, identity constants, generic dispatch declaration, and event publish helper declarations. The module author implements the provider functions. |
| `<module>_adapter.c`     | Optional generated adapter support: deterministic CBOR decode -> C provider call -> deterministic CBOR encode, plus applicable identity, lifecycle, call-surface, and dispatch symbols. |
| `<module>_events.c`      | Typed event publish helpers (Appendix A.4). |
| `<module>_calls.h`       | Typed call-helper declarations (Appendix A.5). |
| `<module>_calls.c`       | Typed call-helper implementations. |

### A.2 C-to-CDDL Artifacts

A generator may also derive the primary module schema and implemented interface schemas from a C header set that conforms to Section 3.
After deriving those schemas, it may produce the same artifact family listed
in Appendix A.1.

### A.3 Generated Dispatch Implementation

A provider module's mandatory `logos_<module>_dispatch()` ABI symbol is commonly generated from the module's exposed contract set and the C mapping rules in this specification.
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
    /* Call logos_<module>_call_<namespace>_M(...) (per §2.4) */
    /* Encode result as M_response map (per §4.2) */
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

The generated `_init()` implementation creates a distinct module context,
copies the Runtime Control binding and event-publication fields used by the generated adapter,
and invokes an optional author-provided initialization hook.
The generated `_destroy()` implementation invokes an optional author-provided
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

The helper name uses the concrete module and defining namespace for the same collision and reverse-mapping reasons as method symbols.

The implementation deterministic-CBOR-encodes
`{bytes_sent, bytes_total, session}` per section 4.2
and calls the `publish` callback and `publish_user_data` retained in `module`
with event name `"storage.upload_progress_event"`.

Module authors call the typed helper instead of encoding deterministic CBOR
manually.
The module context remains process-local as defined in Section 5.2.

### A.5 Generated Typed Call Helpers

For each method, a generator may produce a typed call helper that invokes the method through a `logos_route_handle_t`:

```c
/* From: storage.exists_request = { cid: tstr }
 *       storage.exists_response = { exists: bool } */
logos_result_t logos_storage_invoke_exists(
    logos_route_handle_t* route,
    const char*           cid,
    bool*                 out_exists
);
```

The helper requires a route whose selected contract defines `storage.exists`.
For direct mode, it invokes the validated typed provider function without serialization.
For local or remote Transport mode, it deterministic-CBOR-encodes the request, invokes the route's selected Transport path, decodes the response, and writes `out_exists`.
The helper does not select a provider, acquire a route, or name another consumer.

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
