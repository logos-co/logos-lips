# LOGOS-MODULE-INTERFACE

| Field        | Value                   |
|--------------|-------------------------|
| Name         | Logos Module Interface  |
| Slug         | 301                     |
| Status       | raw                     |
| Category     | Standards Track         |
| Editor       | ksr                     |
| Contributors | Jarrad, atd             |

## Abstract

This specification defines how Logos modules declare their interfaces and how
those interfaces map to both a C calling convention and Logos deterministic
CBOR encoding.

A module interface is defined in a **CDDL schema** (RFC 8610). From that
single schema, two equivalent representations are derived:

- A **C API** — for direct in-process calls (no serialisation)
- A **Logos deterministic CBOR encoding** — for inter-process and remote calls
  (serialised)

The mapping is **bidirectional and canonical**: given the same CDDL input, any
conformant implementation MUST produce the same C function signatures and the
same Logos deterministic CBOR byte sequences.
Conversely, given a C API that conforms to the allowed subset (section 3), any
conformant implementation MUST produce the same CDDL schema.

A module author may start from either end:

- **CDDL-first:** Write a `.cddl` file, generate the C header.
- **C-first:** Write a conformant C header, generate the `.cddl` file.

Both paths MUST produce identical artefacts for the same logical interface.

This spec does NOT cover how modules are loaded, discovered, or connected
(see LOGOS-MODULE-RUNTIME) or how deterministic CBOR messages are transported
over sockets (see LOGOS-MODULE-TRANSPORT).

Unless otherwise qualified, references to encoded payloads and wire bytes in
this specification mean Logos deterministic CBOR as defined in section 4.5.
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
- the compatibility rules implied by the schema version

In other words, transport and process placement are runtime concerns. The
interface contract itself remains the same object regardless of whether a
caller reaches a module by direct C invocation, local IPC, or remote RPC.

## 1. CDDL Schema Conventions

### 1.1 Schema File

Each module MUST have a single `.cddl` file that serves as the authoritative
definition of its interface. The file is named `<module-name>.cddl` (e.g.
`storage_module.cddl`).

The schema file defines:

- Schema metadata (name, version)
- Custom data types used by the module
- Request types (method inputs)
- Response types (method outputs)
- Event types (asynchronous notifications)

A module schema implicitly has access to the Logos prelude fixed-width integer
aliases and MAY reference common Logos schema definitions from
`logos_common.cddl` (section 5).

Note: this spec uses `storage.*` names repeatedly as a convenient running
example for method, event, codegen, and transport-shape illustrations. Those
snippets are explanatory examples unless they are explicitly being used to
state a general module-interface rule. They do not, by themselves, define
the real Storage module interface.

### 1.2 Schema Metadata

Every `.cddl` file MUST begin with a metadata block:

```cddl
; -- metadata --
_module = "storage_module"
_version = [1, 0]            ; [major, minor]
```

The `_module` field is the module's flat runtime module name.
It is used for runtime lookup, socket naming, and C ABI symbol derivation.
Its syntax is the module-name grammar defined by LOGOS-MODULE-RUNTIME
section 1.3.
It is not, by itself, a complete global package identity or cryptographic
schema identity.

The `_version` field is used for compatibility negotiation (see
LOGOS-MODULE-TRANSPORT).
It is compatibility and release-management metadata, not canonical schema
identity input.
LOGOS-MODULE-COMMITMENT-MODEL defines structural schema identity separately.

### 1.3 Logos Prelude

Every module schema is interpreted with a small Logos prelude in scope.
The prelude defines fixed-width integer aliases.
Reusable Logos-defined common types and well-known method surfaces are defined
separately in `logos_common.cddl` (section 5).
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
This rule applies to method names, event names, field names, and named type
names.
The metadata names `_module` and `_version`, the underscore-based runtime
module name carried in `_module`, prelude aliases such as `uint64`, and
exported C ABI symbols are not Logos module schema identifiers.

### 1.4 Methods as Request/Response Pairs

Methods are declared as pairs of named CDDL maps using the convention:

- `<module>.<method>_request` — the method input
- `<module>.<method>_response` — the method output

The `<module>.` prefix is the schema namespace for the module's own
schema-defined methods, events, and types.
It SHOULD correspond to the module's logical name, but it is distinct from the
flat runtime module name carried in `_module`, which is used for loading,
routing, and C ABI symbol derivation.
Runtime bindings between `_module`, schema namespace, and schema commitment
are defined by LOGOS-MODULE-RUNTIME.
This revision defines one primary schema namespace per module schema.

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
A method whose only output is success/failure uses an empty response map:
`storage.destroy_response = {}`. Success is indicated by `logos_result_t.code
== LOGOS_OK`; the empty response means no additional data.

Map keys MUST be bare CDDL identifiers (not quoted strings). Key names are
used directly as C parameter names and deterministic CBOR map keys.

### 1.5 Event Declarations

Events are asynchronous notifications published by a module. They are declared
as named maps with the suffix `_event`:

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

Events are NOT tied to specific methods. Any caller that subscribes to an
event receives it whenever the module publishes it. Event subscription is
managed by the runtime (see LOGOS-MODULE-RUNTIME section 4) and the transport
protocol (see LOGOS-MODULE-TRANSPORT section 5).

Events are an asynchronous one-way notification mechanism with schema-defined
payloads.
They are used for progress updates, completion notifications, state changes,
and similar one-way signals.
They are NOT a second method system:
events do not return values, do not carry per-call correlation semantics
beyond subscription, and MUST NOT be used as a general replacement for
request/response methods.

### 1.6 Custom Types

Custom types are declared using standard CDDL syntax:

```cddl
space_info = {
    quota: uint64,
    used: uint64,
    available: uint64,
}

peer_info = {
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
| Literal values | Scalar literals used as exact schema values, especially choice discriminators |
| Constrained strings | `tstr .size (min..max)`, `bstr .size n` |
| Arrays | `[* T]` (variable-length), `[T, T, T]` (fixed-length tuple) |
| Maps | `{ key: type, ... }` (struct-like maps with known keys) |
| Optional fields | `? key: type` (in maps only) |
| Choices | `T1 / T2 / T3` (tagged unions; arms MUST have deterministic, disjoint selection predicates) |
| Named types | Any type alias defined in the same schema or `logos_common.cddl` |

The following are **NOT allowed** in module schemas:

| Disallowed | Rule |
|-----------|------|
| Bare `uint`, `int`, `nint` | MUST NOT appear in module schemas except inside the Logos prelude definitions. Use fixed-width integer aliases instead. |
| `any` | MUST NOT appear in module schemas. Transport envelope uses `any` for generic payload fields; validation against concrete schema happens at the module layer. |
| `float16`, `float32`, `float64` | Reserved for a future deterministic numeric profile. |
| Unkeyed maps (`{ * tstr => any }`) | Reserved for transport envelope. |
| CBOR tags (beyond the transport envelope) | Reserved for protocol use. |
| `.regexp`, `.cbor`, `.bits` controls | Reserved for future versions. |

Commitment-model note:
LOGOS-MODULE-COMMITMENT-MODEL does not define schema identity or canonical
value roots for floating-point values in this revision.
Floating-point types are reserved for a future deterministic numeric profile.

### 1.8 Complete Example

This complete `storage` schema is illustrative only. It demonstrates the
module-interface format; it is not the normative specification of the real
Storage module API.

```cddl
; -- metadata --
_module = "storage_module"
_version = [1, 0]

; -- types --
space_info = {
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
    info: space_info,
}

storage.destroy_request = {}
storage.destroy_response = {}

storage.upload_url_request = {
    url: tstr,
    chunk_size: uint64,
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

This section defines the one canonical way to derive C types and function
signatures from a CDDL schema. Given the same `.cddl` file, any two
implementations of this spec MUST produce identical C headers (modulo
whitespace and comments).

### 2.1 Naming Conventions

**Module prefix.** All C symbols for a module are prefixed with
`logos_<module>_`.
The module name is taken from the `_module` metadata field.
Because the current module-name grammar is already underscore-based, no
escaping is needed for conformant module names in this revision.
If a later revision introduces dotted or otherwise namespaced module
identities, it MUST also define deterministic C-symbol escaping before those
identities can be used as ABI prefixes.

**Method names.** Derived from the request/response pair name by stripping
the `<module>.` prefix and the `_request`/`_response` suffix. Given
`storage.upload_url_request`, the method name is `upload_url`, which maps to
C function `logos_storage_call_upload_url`.

The bare method name, for example `"upload_url"`, is the module-contract method
selector used by dispatch and by transport bindings.
It does not include the schema namespace prefix.
A transport binding that carries calls to a selected module uses this bare
method selector after the target module has already been selected by the
connection, handle, or routing context.


| CDDL pair base     | C function                     |
|---------------------|--------------------------------|
| `storage.init`      | `logos_storage_call_init`      |
| `storage.upload_url`| `logos_storage_call_upload_url`|
| `storage.peer_id`   | `logos_storage_call_peer_id`   |

The schema method name is used directly in the generated C function suffix.

**Reserved lifecycle names.** The lifecycle/runtime exports
`logos_<module>_name`, `_schema`, `_version`, `_init`, `_destroy`, and
the bootstrap symbol `logos_module_name` occupy reserved ABI namespace.
Per-method C functions therefore use the canonical form
`logos_<module>_call_<method>` so schema methods such as `init`, `version`,
or `destroy` do not collide with required runtime symbols.
This affects only the generated C symbol names.
The wire method name remains the bare schema method name, for example
`"version"`.

**Type names.** CDDL named types map to `logos_<module>_<type_snake>_t`:

| CDDL type        | C type                              |
|------------------|-------------------------------------|
| `space_info`     | `logos_storage_space_info_t`        |
| `peer_info`      | `logos_storage_peer_info_t`         |

Types from `logos_common.cddl` are prefixed with `logos_` (no module):

| CDDL type           | C type                      |
|----------------------|-----------------------------|
| `logos_result`       | `logos_result_t`            |
| `logos_error_code`   | `logos_error_code_t`        |

**Event constants.** Event names map to C `#define` constants:

```c
#define LOGOS_STORAGE_UPLOAD_PROGRESS_EVENT  "storage.upload_progress_event"
#define LOGOS_STORAGE_UPLOAD_DONE_EVENT      "storage.upload_done_event"
```

Pattern: `LOGOS_<MODULE>_<EVENT_NAME_UPPER>`.
`<MODULE>` is the `_module` name converted to uppercase.
`<EVENT_NAME_UPPER>` is the event declaration name after removing the schema
namespace prefix and converting lowercase ASCII letters to uppercase.
The generator does not move the `_event` suffix:
`storage.upload_progress_event` maps to
`LOGOS_STORAGE_UPLOAD_PROGRESS_EVENT`.
The literal event name string remains the schema event name.

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
| `tstr`     | 3 (text string)           | `const char*`                   | UTF-8, null-terminated             |
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

**Constrained strings:** `tstr .size (1..64)` maps to `const char*` — the
size constraint is validated at runtime, not reflected in the C type.

**Fixed-size byte strings:** `bstr .size 16` maps to `uint8_t[16]` in structs
and `const uint8_t*` in function arguments (length is implied by the schema).

### 2.3 Composite Type Mapping

**Maps (structs).** A CDDL map with identifier keys maps to a C struct:

```cddl
space_info = {
    quota: uint64,
    used: uint64,
    available: uint64,
}
```

```c
typedef struct {
    uint64_t quota;
    uint64_t used;
    uint64_t available;
} logos_storage_space_info_t;
```

C struct fields appear in CDDL declaration order.

**Optional fields.** CDDL `? key` adds a `bool has_<field>` presence flag:

```cddl
peer_info = {
    id: tstr,
    ? name: tstr,
}
```

```c
typedef struct {
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

Fixed-length tuples `[T, U, V]` expand to individual struct fields or
function arguments with generated names (`_0`, `_1`, `_2` or taken from
context).

**Choices (tagged unions).** Type choices map to tagged unions:

```cddl
value = uint64 / tstr / bool
```

```c
typedef enum {
    LOGOS_VALUE_UINT = 0,
    LOGOS_VALUE_TSTR = 1,
    LOGOS_VALUE_BOOL = 2,
} logos_value_kind_t;

typedef struct {
    logos_value_kind_t kind;
    union {
        uint64_t    as_uint;
        const char* as_tstr;
        bool        as_bool;
    };
} logos_value_t;
```

Choice arms are first normalized into the canonical choice-arm order defined
by LOGOS-MODULE-COMMITMENT-MODEL.
The generated C discriminant order follows that canonical normalized order,
not the source CDDL declaration order.
Source order may be retained for diagnostics, but it is not ABI-visible.

**Constraint:** All arms of a choice MUST be distinguishable by the Logos
decoding rules.
Source declaration order MUST NOT be used to disambiguate choice arms.
Each choice arm MUST have a deterministic selection predicate as defined by
LOGOS-MODULE-COMMITMENT-MODEL.
For a decoded value, exactly one arm predicate MUST match.
If zero arms or more than one arm predicate match, the value is invalid for
that choice schema.

Valid choices include arms with disjoint CBOR major types:

```cddl
value = uint64 / tstr / bool
```

They also include tagged map unions whose arms are distinguished by a required
literal discriminator field:

```cddl
entry =
  { kind: "file", path: tstr } /
  { kind: "dir", path: tstr, entries: [* tstr] }
```

The discriminator field is normal schema data.
It is encoded as part of the selected map alternative and is not an extra
transport wrapper.
Generated bindings MAY represent a required literal discriminator field through
the generated choice discriminant instead of exposing it as a writable C field.
Encoders MUST still emit the literal discriminator field in the CBOR map.
If the selection predicates for two arms overlap, the choice schema is invalid.

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
logos_result_t logos_storage_call_exists(
    logos_call_context_t* ctx,
    const char*            cid,          /* from request map */
    bool*                  out_exists    /* from response map */
);
```

**Rules:**

1. First parameter is always `logos_call_context_t* ctx`.
   The runtime or module host supplies this opaque call context.
   Module implementations MAY ignore it.
2. Request map fields expand to input parameters, in CDDL declaration order.
   Names are derived directly from the CDDL key.
3. Response map fields expand to output parameters (pointers), appended after
   all input parameters. Prefixed with `out_`.
4. If the response map is empty (`{}`), there are no output parameters.
   Success is indicated by `result.code == LOGOS_OK`.
5. `bstr` fields expand to two parameters: `const uint8_t* <name>` and
   `size_t <name>_len` (input) or `uint8_t** out_<name>` and
   `size_t* out_<name>_len` (output).
6. Array fields in outputs expand to: `<type>** out_<name>` and
   `size_t* out_<name>_count`.
7. Struct fields in outputs are passed as a pointer to the struct type.
8. The function always returns `logos_result_t` for error reporting.

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
    info: space_info,
}
```

```c
logos_result_t logos_storage_call_space(
    logos_call_context_t*       ctx,
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
logos_result_t logos_storage_call_upload_url(
    logos_call_context_t* ctx,
    const char*            url,
    uint64_t               chunk_size,
    bool*                  out_accepted
);
```

### 2.5 Event Type Mapping

Event types generate a C struct for the event payload:

```cddl
storage.upload_progress_event = {
    session: tstr,
    bytes_sent: uint64,
    bytes_total: uint64,
}
```

```c
typedef struct {
    const char* session;
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
} logos_storage_upload_progress_event_t;
```

Event subscription and delivery are handled by the runtime (see
LOGOS-MODULE-RUNTIME section 4) via generic subscribe/unsubscribe functions.
The event struct is used by the codegen'd decode layer to convert
deterministic CBOR event payloads into typed C structs.

### 2.6 Module Lifecycle Symbols

This section classifies the C symbols that belong to the portable module ABI.

Every module shared library MUST export these mandatory module symbols:

- `logos_<module>_name()` returns the module name as a static string that
  remains valid for the library lifetime.
- `logos_<module>_schema()` returns the canonical CDDL schema text as a
  static string that remains valid for the library lifetime.
- `logos_<module>_version()` returns a concise schema version string such as
  `"1.0"`.
- `logos_<module>_init()` is called once after loading.
  It returns `0` on success or a nonzero Logos error code on failure.
- `logos_<module>_destroy()` is called once before unloading.
- `logos_<module>_free()` releases dynamic memory returned by this module
  across this ABI.
- `logos_<module>_dispatch()` dispatches a schema method name and deterministic
  CBOR request payload to the corresponding schema-defined method.
  It is a module ABI symbol, not a schema method.

Every module shared library MUST also export the schema-derived per-method C
functions specified in section 2.4.
The per-method C functions are the canonical typed native provider ABI.
`logos_<module>_dispatch()` is the canonical generic module-host and transport
entrypoint.
Both surfaces are mandatory in this revision and MUST be derived from, or
implemented consistently with, the same module schema.

`logos_<module>_dispatch()` MUST NOT be listed as a method in the module schema,
`logos.schema` method listings, or generated client bindings.
It MUST NOT be used as the method identity for commitments, authorization,
audit records, or conformance vectors.
Those surfaces identify the target schema method selected by the `method`
argument and the corresponding request, response, or error value.

Modules SHOULD export this recommended bootstrap symbol:

- `logos_module_name()` is the bootstrap symbol for runtimes that do not know
  the module name in advance.
  The runtime calls `dlsym("logos_module_name")` to discover the module
  name, then uses the module-specific prefix for all other symbols.
  This allows directory scanners to discover modules without sidecar metadata.
  Runtimes MUST also support loading modules whose name is already known from
  a manifest, static registration table, command-line argument, or equivalent
  host/deployment metadata.

Modules MAY export these optional well-known runtime callback setter symbols:

- `logos_<module>_set_publish()`
- `logos_<module>_set_call_module()`

These symbols are optional because not every module publishes events or makes
outbound calls to other modules.
When present, they MUST use the signatures and semantics defined by
LOGOS-MODULE-RUNTIME.
Runtimes MUST NOT reject a module solely because either callback setter is
absent.
Runtimes MAY bind and use these symbols when present.

The following declarations show the mandatory and recommended symbol
signatures:

```c
/* Module name (static string, valid for library lifetime) */
const char* logos_<module>_name(void);

/* CDDL schema (static string, valid for library lifetime) */
const char* logos_<module>_schema(void);

/* Schema version string (e.g. "1.0") */
const char* logos_<module>_version(void);

/* Initialise module (called once after loading).
 * Returns LOGOS_OK (0) on success, or a non-zero Logos error code on failure. */
int logos_<module>_init(void);

/* Shut down module (called once before unloading) */
void logos_<module>_destroy(void);

/* Generic module-host and transport dispatch entrypoint. */
logos_result_t logos_<module>_dispatch(
    logos_call_context_t* ctx,
    const char*           method,
    const uint8_t*        params_cbor,
    size_t                params_len,
    uint8_t**             out_response_cbor,
    size_t*               out_response_len
);

/* Bootstrap symbol — universal probe for unknown modules. */
const char* logos_module_name(void);

/* Module deallocator for dynamic memory returned across this ABI */
void logos_<module>_free(void* ptr);
```

**Note on `_version()`:** The current ABI keeps `logos_<module>_version()`
as a separate well-known symbol even though the schema text returned by
`logos_<module>_schema()` also contains version metadata. A future revision
MAY simplify the ABI by removing `_version()` and treating the schema as the
sole source of version metadata.
Version metadata remains separate from the structural schema identity defined
by LOGOS-MODULE-COMMITMENT-MODEL.

The benefits of keeping `_version()` in v0.1 are pragmatic:

- **Cheap probing:** the runtime can query a small, stable symbol without
  parsing the full schema text.
- **Compatibility checks:** version lookup is easy during discovery,
  loading, and connection setup.
- **Operational clarity:** logs, diagnostics, and crash reports can report a
  concise version string directly.
- **Low implementation cost:** codegen and hand-written modules can expose it
  trivially, while still keeping the schema authoritative for interface shape.

In **direct mode** (in-process), the runtime MAY call per-method functions
directly.
In generic module-host, local transport, and remote transport paths, the runtime
or module host MAY call `logos_<module>_dispatch()`.
For dispatch calls, `method` is the bare schema method name after the target
module has already been selected.
`params_cbor` is the deterministic CBOR request map for that method, not the
full Transport Request envelope.
On success, `out_response_cbor` receives the deterministic CBOR response map for
that method.
The returned response buffer is released with `logos_<module>_free()`.
Both direct and dispatch paths are equivalent only when they preserve the same
target schema method, request value, response value, error behavior, and
authorization boundary.

**Important distinction: lifecycle `_init()` vs schema method `init`.**

The lifecycle symbol `logos_<module>_init(void)` is part of the runtime ABI.
It is called by the runtime after loading the shared library and before the
module is exposed for calls. It is for runtime/loader initialisation only.

If a module schema also declares an ordinary method named `init` (for example
`storage.init_request` / `storage.init_response`), that method is a normal
schema-defined request/response method with C symbol
`logos_<module>_call_init` and wire method name `"init"`. It is distinct from
the lifecycle symbol and MAY perform application-level configuration or setup
that remains necessary after lifecycle `_init()` has succeeded.

Successful lifecycle `_init()` therefore means:

- the module has loaded correctly into the runtime
- the runtime or module host may invoke schema-defined methods through the
  native per-method C entry points

It does **not** mean every schema-defined method must already succeed.
Schema-defined methods MAY still return `LOGOS_ERR_NOT_READY` until the
module's own API-level setup sequence is complete.

### 2.7 Memory Management

Memory-management behavior is normative wherever ownership crosses the module
boundary.
Without this, independently implemented runtimes and modules cannot safely
interoperate.

The ABI therefore defines a module-owned deallocation function for dynamic
memory returned across the module ABI boundary:

```c
void logos_<module>_free(void* ptr);
```

**Lifetime rules:**

- For callee-side module C functions, `logos_result_t.message` and `.detail`
  are valid until the next Logos module call using the same
  `logos_call_context_t*`, or until the call context is destroyed, whichever
  comes first.
  Module hosts MUST copy these fields before that point if they need to encode,
  retain, or forward them later.
- For caller-side runtime handles or generated caller helpers,
  `logos_result_t.message` and `.detail` are valid until the next Logos call on
  the same handle or helper-owned call state.
  Callers MUST copy these fields to retain them.
- Output pointers (`out_*`) for dynamically-sized data (`tstr`, `bstr`,
  arrays) are allocated by the callee. Callers MUST free them with the same
  module's `logos_<module>_free()`.
- Output structs are caller-allocated (passed as pointer); the callee fills
  them in. Any dynamic fields within the struct (strings, arrays) are
  callee-allocated and freed with the same module's
  `logos_<module>_free()`.
- All `const` pointer input parameters are borrowed for the duration of the
  call. Modules MUST copy if they need to retain.
- `_name()` and `_schema()` return static strings. Callers MUST NOT free.
- `logos_<module>_free(NULL)` MUST be a no-op.

The module that allocates memory owns the corresponding deallocator.
In direct mode, the runtime or generated caller helper obtains the deallocator
from the same module binding that produced the output.
Across process, sandbox, container, or remote boundaries, raw pointers do not
cross the boundary; the side that decodes serialized data owns and frees its
own decoded allocations.

---

## 3. Canonical C-to-CDDL Mapping

This section defines the reverse direction: given a C header that conforms to
the allowed subset, how to derive a CDDL schema. This enables the "C-first"
workflow where a module author writes their C API and the tool generates the
`.cddl` file.

### 3.1 Allowed C Subset

Only these C types are permitted in module function signatures:

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
| `logos_<module>_<type>_t` | Named struct type |
| `const T*` + `size_t` (pair) | `[* T]` (array) |
| `logos_result_t` | (return type only; maps to error handling) |
| `logos_call_context_t*` | (first param only; not in CDDL) |

**Disallowed C constructs in the API surface:**

- `void*` (except in `logos_<module>_free`)
- Raw pointers that are not `const char*` or `const uint8_t* + size_t`
- Function pointers (no callbacks in module interfaces)
- `float` and `double` (reserved for a future deterministic numeric profile)
- Bitfields, bit-packed structs
- `enum` not declared as `logos_*_t` (use explicit integer types or declared enums)

### 3.2 Function Signature Recognition

The codegen tool recognises module functions by pattern:

```c
logos_result_t logos_<module>_<method>(
    logos_call_context_t* ctx,
    <input params...>,
    <output params...>        /* out_ prefix */
);
```

- The `logos_call_context_t*` first parameter is stripped (not in CDDL).
- Input parameters (no `out_` prefix) become request map fields.
- Output parameters (`out_` prefix, pointer types) become response map fields.
- `logos_result_t` return is stripped (error handling, not in CDDL data).

**Parameter name to CDDL key:** parameter names are used directly.
`chunk_size` -> `chunk_size`.

**Example:**

```c
logos_result_t logos_storage_upload_url(
    logos_call_context_t* ctx,
    const char*            url,
    uint64_t               chunk_size,
    bool*                  out_accepted
);
```

Generates:

```cddl
storage.upload_url_request = {
    url: tstr,
    chunk_size: uint64,
}
storage.upload_url_response = {
    accepted: bool,
}
```

### 3.3 Struct Recognition

C structs matching `logos_<module>_<name>_t` are recognised as custom types:

```c
typedef struct {
    uint64_t quota;
    uint64_t used;
    uint64_t available;
} logos_storage_space_info_t;
```

Generates:

```cddl
space_info = {
    quota: uint64,
    used: uint64,
    available: uint64,
}
```

Optional fields (those with a preceding `bool has_<field>`) generate
`? key: type` in CDDL.

### 3.4 Event Struct Recognition

C structs matching `logos_<module>_<name>_event_t` are recognised as events:

```c
typedef struct {
    const char* session;
    uint64_t    bytes_sent;
    uint64_t    bytes_total;
} logos_storage_upload_progress_event_t;
```

Generates:

```cddl
storage.upload_progress_event = {
    session: tstr,
    bytes_sent: uint64,
    bytes_total: uint64,
}
```

### 3.5 Lifecycle Symbol Recognition

The runtime symbols (`_name`, `_schema`, `_version`, `_init`, `_destroy`,
and `_free`) are recognised by name and excluded from the CDDL schema.
They are part of the runtime contract, not schema-defined module methods.
The `_free` suffix refers to the module-prefixed `logos_<module>_free` symbol.

### 3.6 Roundtrip Guarantee

For any conformant C header `H`:

```
H -> (C-to-CDDL) -> schema.cddl -> (CDDL-to-C) -> H'
```

`H'` MUST be semantically identical to `H` (same types, same function
signatures, same parameter order). Whitespace, comments, and `#include`
guards may differ.

For any conformant CDDL schema `S`:

```
S -> (CDDL-to-C) -> header.h -> (C-to-CDDL) -> S'
```

`S'` MUST be semantically identical to `S`.

---

## 4. CDDL-to-CBOR Canonical Encoding

When a method call is serialised for socket transport, the mapping from the
CDDL schema to Logos deterministic CBOR bytes is defined here.
This section and section 2 are two views of the same schema:
the C API is the in-process view, and Logos deterministic CBOR encoding is the
on-the-wire value view.

Logos deterministic CBOR is the module-boundary value encoding profile defined
by this specification.
It is based on the CBOR data model in RFC 8949, the core deterministic
encoding requirements in RFC 8949 Section 4.2.1, and the IETF CBOR Common
Deterministic Encoding (CDE) rules or their successor RFC.
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
Keys MUST be sorted using the CDE deterministic map-order rule defined in
section 4.5.

```
space_info -> {
    "available": 1073741824,    ; keys sorted: a < q < u
    "quota": 10737418240,
    "used": 9663676416,
}
```

Note: deterministic CBOR wire order differs from C struct order (declaration
order).
Encoders sort; decoders match by key name.

**Arrays:** deterministic CBOR array (major type 4), definite length.

**Optional fields:** Absent keys are simply omitted from the deterministic
CBOR map.
The `has_<field>` flag in the C struct is the decoded representation of key
presence.

**Choices:** Encoded as the raw deterministic CBOR value of the selected
alternative.
The decoder determines which alternative was sent by applying the
schema-defined deterministic selection predicates.
Choice selection MUST NOT depend on source declaration order.

### 4.3 Method Call and Event Encoding

Method params, response results, and event data are each encoded as
deterministic CBOR maps per sections 4.1 and 4.2.
The Transport envelope wraps these maps; see LOGOS-MODULE-TRANSPORT section
1.3 for the full envelope format.

**Example — `storage.exists` request params:**
```
{"cid": "bafy..."}     ; deterministic CBOR map, keys sorted per §4.5
```

**Example — `storage.exists` response result:**
```
{"exists": true}
```

For methods with empty responses, the result is an empty map `{}`.
For events, the `data` field encodes the event schema map.

### 4.5 Logos Deterministic CBOR Requirement

All encoded payloads at the module boundary MUST use Logos deterministic CBOR.
This profile is based on RFC 8949 deterministic encoding and CDE.
It requires:

1. Map keys MUST be sorted according to the CDE deterministic map-order rule.
   For this specification, that means bytewise lexicographic comparison of the
   complete deterministic CBOR encoding of each map key.
   Sorting by key length before key byte content MUST NOT be used.
2. Integers MUST use the shortest possible encoding.
3. Indefinite-length encodings MUST NOT be used.
4. Duplicate map keys MUST NOT appear.
5. Floating-point values are not part of Logos module schemas in this
   revision.

The Logos deterministic CBOR profile is a Logos-owned application profile over
RFC 8949 and CDE.

### 4.6 Validation

Implementations MUST:

1. Reject any incoming deterministic CBOR that violates the determinism rules
   in section 4.5 with error code `INVALID_PARAMS`.
2. Validate all outgoing deterministic CBOR in debug builds.
3. Reject unknown method names -> error code `METHOD_NOT_FOUND`.
4. Reject wrong parameter types or missing required fields ->
   error code `INVALID_PARAMS`.

For module method payloads, schema validation is owned by the module dispatch
layer generated from or implemented against the module's CDDL schema.
The runtime and transport layers validate envelopes and routing fields.
They MUST NOT be required to introspect module payload schemas while forwarding
local or remote transport calls.

### 4.7 Error Propagation

In local or remote transport mode,
the error path from module to caller spans all three specs:

```
Module C function returns logos_result_t with code != LOGOS_OK
    |
    v
Module host or generated adapter encodes error as deterministic CBOR error-payload:
{code, message, ?detail}
    |
    v
Module host wraps in Transport Response: {0: 2, id, error: {code, message, ?detail}}
    |
    v
Caller's handle decodes Response, reconstructs logos_result_t
    |
    v
Per-method C function on caller side returns logos_result_t with the error
```

**Direct mode shortcut:** In direct mode, the per-method function returns
`logos_result_t` directly. No encoding or transport is involved. The error
code passes through unchanged.

**Protocol-level errors** are distinct from method errors.
Protocol errors indicate connection/framing problems, such as malformed
deterministic CBOR or an unknown transport message kind.
Method errors are carried in Response messages with the `error` field. A
module returning `LOGOS_ERR_METHOD_NOT_FOUND` produces a Response error, not
a protocol error.

---

## 5. Logos Common Schema Surface (`logos_common.cddl`)

`logos_common.cddl` contains the Logos prelude aliases for source-authoring
convenience and the reusable Logos common schema surface.
For schema identity, LOGOS-MODULE-COMMITMENT-MODEL treats those two groups
differently:
prelude integer aliases normalize to built-in primitive schema leaves, while
common schema definitions are referenced definitions in the Logos common schema
surface.

### 5.1 CDDL Definitions

```cddl
; logos_common.cddl

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
logos_error_code = &(
    ok:                0,
    method_not_found:  1,
    invalid_params:    2,
    module_error:      3,
    not_authorised:    4,
    transport_error:   5,
    timeout:           6,
    version_mismatch:  7,
    not_ready:         8,
    cancelled:         9,
)

; -- result type --
logos_result = {
    code: logos_error_code,
    ? message: tstr,
    ? detail: bstr,
}

; -- module handle (opaque, not on wire) --
; logos_module_handle_t is a runtime concept, not serialised.

; -- introspection bootstrap (well-known method, available on all modules) --
logos.schema_request = {}
logos.schema_response = {
    schema: tstr,
}
```

`logos.schema` is the universal module-introspection bootstrap.
It returns the raw CDDL text via the `_schema()` lifecycle symbol.
Module authors do not declare it.

Module introspection is schema-first:
method listings, event listings, request/response shapes, and type information
are derived from the module schema and its canonical schema model.
Runtime module listings are runtime introspection state and are exposed through
the runtime-control contract defined by LOGOS-MODULE-RUNTIME.

`logos_error_code` is the shared Logos module-boundary error-code registry.
LOGOS-MODULE-INTERFACE owns allocation of this registry.
Other Logos specifications may cite these values, but they do not allocate
additional shared error codes.

Values `0` through `9` are allocated in this revision.
A conforming implementation of this revision MUST NOT emit any other
`logos_error_code` value.
When a serialized Logos value contains an unknown shared error-code value,
the receiver MUST treat the enclosing value or message as invalid for this
revision.
For local or remote transport, that invalid value is handled through the
transport or method validation path that rejected the message.
When a direct-mode C function returns an integer outside the allocated
`logos_error_code_t` range, the runtime or generated caller helper MUST treat
the call as a module failure and MUST NOT serialize the unknown integer as a
shared Logos error code.

### 5.2 C Definitions (`logos_types.h`)

These C definitions are the C-side common ABI surface used by generated and
hand-written modules.
For C-first modules, the reverse mapping in section 3 recognizes these shared
C types and maps them to the corresponding Logos common schema and runtime
concepts defined above.

- `logos_error_code_t` defines the shared error-code space used at the
  module boundary.
- `logos_result_t.message` is human-readable text and MAY be `NULL`.
- `logos_result_t.detail` is an optional deterministic CBOR detail payload and
  MAY be `NULL`.
- `logos_call_context_t` is opaque to module implementations.
- The runtime or module host supplies a call context when invoking a Logos
  module C function.
- Module implementations MAY ignore the call context.
- The call context is not serialized and is not a caller-side routing handle.
- `logos_module_handle_t` is opaque to callers.
- A handle represents a connection to a specific module instance.
- The runtime allocates handles and callers obtain them through the runtime
  API defined in LOGOS-MODULE-RUNTIME.
- In direct mode, a handle may wrap function pointers or equivalent
  in-process dispatch state.
  In local transport mode, it may wrap a transport connection or equivalent
  runtime state.
- The execution mode behind a handle is runtime-internal and MUST NOT change
  the module contract seen by callers.
- Handles are not intrinsically thread-safe.
  A single handle MUST NOT be used concurrently from multiple threads
  without external synchronization.
- `logos_<module>_free()` deallocates memory returned by that module across
  the module ABI boundary.

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

typedef struct {
    logos_error_code_t  code;
    const char*         message;      /* human-readable; may be NULL */
    const uint8_t*      detail;       /* optional deterministic CBOR detail; may be NULL */
    size_t              detail_len;
} logos_result_t;

/* -- Call context -- */

/*
 * Opaque inbound-call context supplied by the runtime or module host.
 * Module implementations may ignore this pointer.
 */
typedef struct logos_call_context logos_call_context_t;

/* -- Module handle -- */

/*
 * A handle represents a connection to a specific module instance.
 * The runtime allocates handles; callers obtain them via
 * logos_runtime_connect() (see LOGOS-MODULE-RUNTIME section 4.1).
 *
 * In direct mode, the handle wraps function pointers to the target
 * module's C API. In local transport mode, it wraps a local transport
 * connection.
 * The caller does not know or care which mode is active.
 *
 * Handles are NOT thread-safe: a single handle MUST NOT be used
 * concurrently from multiple threads without external synchronisation.
 * Create one handle per thread, or serialise access.
 */
typedef struct logos_module_handle {
    /* opaque to callers — fields are runtime-internal */
    void* _impl;
} logos_module_handle_t;

/* -- Memory management -- */

void logos_<module>_free(void* ptr);
```

Memory lifetime rules: see section 2.7.

---

## 6. Schema Versioning

### 6.1 Version Format

Schema versions are `[major, minor]` pairs.

- **Minor** version increment: new methods added, new optional fields added
  to existing types, new events added. All existing calls remain valid.
- **Major** version increment: methods removed, method signatures changed,
  required fields added to existing types. Every new major version is
  effectively a new interface.

### 6.2 Compatibility Rules

A callee at version `[M, n]` MUST accept calls valid under any version
`[M, m]` where `m <= n` (backward-compatible within a major version).

New fields in request/response maps MUST be optional (`?`) for minor version
bumps. This ensures older callers can still send valid requests.

Methods removed in a new major version MUST go through a deprecation period:
they must be present (but may return `METHOD_NOT_FOUND`) for at least one
major version before removal.

Version metadata applies in all execution modes.
In direct mode, the runtime MAY query `logos_<module>_version()` during
loading, registration, or connection setup and apply its compatibility policy
before routing calls.
In local or remote transport mode, version negotiation is carried in the
Transport Hello exchange.
In all modes, `_version` and `logos_<module>_version()` are compatibility
metadata only; structural schema identity is defined by
LOGOS-MODULE-COMMITMENT-MODEL.

## 8. Streaming and Chunked Data (Future)

This version of the spec does NOT address streaming or chunked transfer of
large payloads. A 100MB file cannot be sent as a single `bstr` within a
single deterministic CBOR message (given default message size limits).

Future versions will specify a streaming mechanism. Options under
consideration:

- Chunked transfer as a sequence of Request/Response messages
- A dedicated stream message type in the transport protocol
- Out-of-band data channels referenced by handle

Module authors needing large data transfer in this version should use filesystem paths
or external references (URLs, CIDs) rather than inline byte strings.

---

## Appendix A. Generated Artifacts (Informative)

The mapping rules in sections 2 through 4 can be applied mechanically to
produce C headers, adapter implementations, event helpers, and client stubs.
This appendix describes common derived artifacts and implementation patterns.
The normative requirements are the ABI, mapping, method-call, and encoding
rules defined in the main body of this specification.

### A.1 CDDL-to-C Artifacts

| Output file               | Contents                                         |
|--------------------------|--------------------------------------------------|
| `<module>.h`             | C header: typedefs, per-method function declarations, event publish helper declarations. Module author implements the per-method functions. |
| `<module>_adapter.c`     | Optional generated adapter support: deterministic CBOR decode -> C call -> deterministic CBOR encode, plus `_name()`, `_version()`, `_schema()`, `_init()` stub, `_destroy()` stub, `logos_module_name()` bootstrap symbol. |
| `<module>_events.c`      | Typed event publish helpers (Appendix A.4). |
| `<module>_client.h`      | Typed client stub declarations (Appendix A.5). |
| `<module>_client.c`      | Client stub implementations. |

### A.2 C-to-CDDL Artifacts

A generator may also derive a module CDDL schema from a C header that conforms
to the allowed subset in section 3.
After deriving the CDDL schema, it may produce the same artifact family listed
in Appendix A.1.

### A.3 Generated Dispatch Implementation

The mandatory `logos_<module>_dispatch()` ABI symbol is commonly generated from
the module schema and the C mapping rules in this specification.
It MAY also be implemented by hand, but handwritten implementations MUST behave
as if derived from the same schema:
they dispatch only to schema methods, validate request payloads against the
target method request schema, call the corresponding per-method implementation
or equivalent provider logic, and encode responses according to the target
method response schema.

The dispatch function is not a schema method.
It is a generic ABI entrypoint for hosts that carry method names and encoded
payloads.
The typed per-method C functions remain mandatory and form the native provider
surface for direct/static integrations and generated bindings.

For each method `M` declared in the schema, such an adapter commonly has a
branch with this shape:

```c
if (strcmp(method, "M") == 0) {
    /* Decode params_cbor as M_request map (per §4.2) */
    /* Call logos_<module>_call_M(...) (per §2.4) */
    /* Encode result as M_response map (per §4.2) */
    /* Write to *response, *response_len */
}
```

Such an adapter commonly:

- looks up the method in a generated dispatch table,
- returns `LOGOS_ERR_METHOD_NOT_FOUND` for an unknown method,
- decodes the deterministic CBOR request payload according to the method
  request schema,
- returns `LOGOS_ERR_INVALID_PARAMS` if decode fails,
- calls the corresponding per-method C function,
- encodes a successful response as a deterministic CBOR map matching the
  method response schema, and
- encodes a module-level error as the error payload described in section 4.4.

The generated adapter may also handle the `logos.schema` well-known method
by returning `_schema()`, and unknown methods by returning
`LOGOS_ERR_METHOD_NOT_FOUND`.

Because dispatch is an ABI entrypoint rather than a schema method,
commitment-model, hash-profile, authorization, audit, and conformance material
MUST identify the target schema method and its request/response values.
They MUST NOT identify a synthetic dispatch method.

The generated `_init()` and `_destroy()` stubs are empty — module authors
override them if they need initialisation/cleanup.

### A.4 Generated Event Publish Helpers

For each event `<module>.<name>_event` in the schema, a generator may produce a
typed helper that encodes the event payload as deterministic CBOR and calls the
runtime-provided publish function:

```c
/* From: storage.upload_progress_event = { session: tstr, bytes_sent: uint64, bytes_total: uint64 } */
void logos_storage_publish_upload_progress(
    logos_publish_fn  publish,
    void*             publish_user_data,
    const char*       session,
    uint64_t          bytes_sent,
    uint64_t          bytes_total
);
```

The implementation deterministic-CBOR-encodes
`{session, bytes_sent, bytes_total}` per
section 4.2 and calls
`publish(publish_user_data, "storage.upload_progress_event", cbor, cbor_len)`.

Module authors call the typed helper instead of encoding deterministic CBOR
manually.
`publish_user_data` is the process-local callback context installed by the
runtime or module host, as defined by LOGOS-MODULE-RUNTIME.

### A.5 Generated Client Stubs

For each method, a generator may produce a typed client function that encodes a
deterministic CBOR request, calls the runtime-provided module call function, and
decodes the response:

```c
/* From: storage.exists_request = { cid: tstr }
 *       storage.exists_response = { exists: bool } */
logos_result_t logos_storage_client_exists(
    logos_call_module_fn  call,
    void*                 call_user_data,
    const char*           cid,
    bool*                 out_exists
);
```

The implementation deterministic-CBOR-encodes `{cid}`, calls
`call(call_user_data, "storage_module", {"method":"exists","params":{cid}}, len,
&resp, &resp_len)`,
decodes the response map, and writes `out_exists`.
The signature is a client-side helper shape for use with the runtime-provided
module-call callback.
`call_user_data` follows the same process-local callback context rules as
the runtime-provided call-module hook.

### A.6 Framework-Specific UI Bindings

Generators may produce UI-framework-facing bindings derived from the same CDDL
schema.
Such bindings are derived views over the canonical module contract, not
parallel interfaces.

The CDDL schema remains the canonical interface definition.
Framework-specific binding details are out of scope for this specification.

### A.7 Future Floating-Point Support

Floating-point types are not part of Logos module schemas in this revision.
A future revision may define a deterministic numeric profile that introduces
floating-point, fixed-point, decimal, or other numeric types.
Such a profile must define schema identity, deterministic encoding,
cross-language value semantics, and commitment-model behavior before those
types can be used in portable Logos module contracts.

One possible future floating-point profile is to expose only `float64` at the
schema level, map it to C `double`, and reserve `float16` and `float32` as
wire encodings rather than schema types.

If such a profile is adopted, its type tables could include:

| Surface | Future mapping |
|---------|----------------|
| Module schema type | `float64` |
| CBOR major type | 7, double-precision semantic type |
| C type | `double` |
| C-first mapping | `double` maps to `float64` |
| Reserved schema spellings | `float16`, `float32` |

Its deterministic-CBOR rule could be:

1. Module schemas use `float64` as the type.
2. Encoders use the shortest floating-point CBOR width that preserves the
   value exactly:
   `float16` if lossless, otherwise `float32` if lossless, otherwise
   `float64`.
3. The shorter encoding is a wire optimization only.
4. Decoders accept any CBOR floating-point width and promote the result to
   `double` in C.

This appendix does not define that profile.

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- IETF CBOR Common Deterministic Encoding (CDE),
  draft-ietf-cbor-cde, or its successor RFC if one is published.
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- LOGOS-MODULE-TRANSPORT -- Socket protocol specification.
- LOGOS-MODULE-RUNTIME -- Module loading and lifecycle specification.

### Informative

- [COSS] -- Consensus-Oriented Specification System.
  https://rfc.vac.dev/spec/1/

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
