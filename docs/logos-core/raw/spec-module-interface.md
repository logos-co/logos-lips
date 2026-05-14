# LOGOS-MODULE-INTERFACE

| Field    | Value                                      |
|----------|--------------------------------------------|
| Name     | Logos Module Interface                     |
| Slug     | LOGOS-MODULE-INTERFACE                     |
| Status   | raw                                        |
| Category | Standards Track                            |
| Editor   | ksr                                        |
| Contributors | Jarrad, atd                            |

## Abstract

This specification defines how Logos modules declare their interfaces and how
those interfaces map to both a C calling convention and a dCBOR wire encoding.

A module interface is defined in a **CDDL schema** (RFC 8610). From that
single schema, two equivalent representations are derived:

- A **C API** — for direct in-process calls (no serialisation)
- A **dCBOR encoding** — for inter-process and remote calls (serialised)

The mapping is **bidirectional and canonical**: given the same CDDL input, any
conformant implementation MUST produce the same C function signatures and the
same dCBOR byte sequences. Conversely, given a C API that conforms to the
allowed subset (section 3), any conformant implementation MUST produce the
same CDDL schema.

A module author may start from either end:

- **CDDL-first:** Write a `.cddl` file, generate the C header.
- **C-first:** Write a conformant C header, generate the `.cddl` file.

Both paths MUST produce identical artefacts for the same logical interface.

This spec does NOT cover how modules are loaded, discovered, or connected
(see LOGOS-MODULE-RUNTIME) or how dCBOR messages are transported over sockets
(see LOGOS-MODULE-TRANSPORT).

Unless otherwise qualified, references to encoded payloads and wire bytes in
this specification mean deterministic CBOR using the dCBOR profile defined in
section 4.5.
For brevity, some later sections may still say "CBOR" in explanatory prose.
In this specification, those references MUST be read as dCBOR unless the text
is explicitly talking about generic CBOR concepts such as major types,
RFC terminology, or envelope-level compatibility with CBOR itself.

### Execution-Boundary Invariance

The module contract defined by this specification is **execution-boundary
invariant**.

That means the same logical Logos method/event interface MUST remain valid
across all supported runtime realizations:

- **Direct mode** — in-process C calls using the derived/generated C API
- **Local IPC mode** — the same contract carried over local dCBOR transport
- **Remote mode** — the same contract carried over remote transport

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

A module schema MAY import common types from `logos_common.cddl` (section 5).

Note: this spec uses `storage.*` names repeatedly as a convenient running
example for method, event, codegen, and transport-shape illustrations. Those
snippets are explanatory examples unless they are explicitly being used to
state a general module-interface rule. They do not, by themselves, define or
freeze the real Storage module interface.

### 1.2 Schema Metadata

Every `.cddl` file MUST begin with a metadata block:

```cddl
; -- metadata --
_module = "storage_module"
_version = [1, 0]            ; [major, minor]
```

The `_module` field is the module's unique name. The `_version` field is used
for compatibility negotiation (see LOGOS-MODULE-TRANSPORT).

### 1.3 Methods as Request/Response Pairs

Methods are declared as pairs of named CDDL maps using the convention:

- `<module>.<method>-request` — the method input
- `<module>.<method>-response` — the method output

```cddl
storage.exists-request = {
    cid: tstr,
}

storage.exists-response = {
    exists: bool,
}
```

The codegen tool recognises `*-request` / `*-response` pairs by naming
convention and generates the corresponding C function signatures and wire
protocol dispatch.

A method with no input uses an empty map: `storage.space-request = {}`.
A method whose only output is success/failure uses an empty response map:
`storage.destroy-response = {}`. Success is indicated by `logos_result_t.code
== LOGOS_OK`; the empty response means no additional data.

Map keys MUST be bare CDDL identifiers (not quoted strings). Key names are
used directly as C parameter names and dCBOR map keys.

### 1.4 Event Declarations

Events are asynchronous notifications published by a module. They are declared
as named maps with the suffix `-event`:

```cddl
storage.upload-progress-event = {
    session: tstr,
    bytes-sent: uint,
    bytes-total: uint,
}

storage.upload-done-event = {
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

### 1.5 Custom Types

Custom types are declared using standard CDDL syntax:

```cddl
space-info = {
    quota: uint,
    used: uint,
    available: uint,
}

peer-info = {
    id: tstr,
    addrs: [* tstr],
    ? name: tstr,
}
```

### 1.6 Type Restrictions

Module schemas MUST only use types from this set:

| Category | Allowed types |
|----------|--------------|
| Primitives | `bool`, `uint`, `int`, `float64`, `tstr`, `bstr` |
| Constrained integers | `uint .size 1`, `uint .size 2`, `uint .size 4`, `int .size 1`, etc. |
| Constrained strings | `tstr .size (min..max)`, `bstr .size n` |
| Arrays | `[* T]` (variable-length), `[T, T, T]` (fixed-length tuple) |
| Maps | `{ key: type, ... }` (struct-like maps with known keys) |
| Optional fields | `? key: type` (in maps only) |
| Choices | `T1 / T2 / T3` (tagged unions; arms MUST have distinct CBOR major types) |
| Named types | Any type alias defined in the same schema or `logos_common.cddl` |

The following are **NOT allowed** in module schemas:

| Disallowed | Rule |
|-----------|------|
| `any` | MUST NOT appear in module schemas. Transport envelope uses `any` for generic payload fields; validation against concrete schema happens at the module layer. |
| `float16`, `float32` | Use `float64`. dCBOR encoding MAY use shorter wire representation if lossless; decoders MUST promote to `double`. |
| Unkeyed maps (`{ * tstr => any }`) | Reserved for transport envelope. |
| CBOR tags (beyond the transport envelope) | Reserved for protocol use. |
| `.regexp`, `.cbor`, `.bits` controls | Reserved for future versions. |

### 1.7 Complete Example

This complete `storage` schema is illustrative only. It demonstrates the
module-interface format; it is not the normative specification of the real
Storage module API.

```cddl
; storage_module.cddl

; -- metadata --
_module = "storage_module"
_version = [1, 0]

; -- types --
space-info = {
    quota: uint,
    used: uint,
    available: uint,
}

; -- methods --
storage.init-request = {
    data-dir: tstr,
}
storage.init-response = {}

storage.exists-request = {
    cid: tstr,
}
storage.exists-response = {
    exists: bool,
}

storage.space-request = {}
storage.space-response = {
    info: space-info,
}

storage.destroy-request = {}
storage.destroy-response = {}

storage.upload-url-request = {
    url: tstr,
    chunk-size: uint,
}
storage.upload-url-response = {
    accepted: bool,
}

storage.start-request = {}
storage.start-response = {}

; -- events --
storage.upload-progress-event = {
    session: tstr,
    bytes-sent: uint,
    bytes-total: uint,
}

storage.upload-done-event = {
    cid: tstr,
}

storage.started-event = {}
```

---

## 2. CDDL-to-C Canonical Mapping

This section defines the one canonical way to derive C types and function
signatures from a CDDL schema. Given the same `.cddl` file, any two
implementations of this spec MUST produce identical C headers (modulo
whitespace and comments).

### 2.1 Naming Conventions

**Module prefix.** All C symbols for a module are prefixed with
`logos_<module>_`. The module name is taken from the `_module` metadata field,
with hyphens replaced by underscores.

**Method names.** Derived from the request/response pair name by stripping
the `<module>.` prefix and the `-request`/`-response` suffix. Given
`storage.upload-url-request`, the method name is `upload-url`, which maps to
C function `logos_storage_call_upload_url`.

The bare method name (e.g. `"upload-url"`) is also the value used in the
Transport protocol's Request `method` field. The module prefix is NOT
included in the wire `method` field — the connection already identifies the
target module via the Hello handshake.

| CDDL pair base     | C function                     |
|---------------------|--------------------------------|
| `storage.init`      | `logos_storage_call_init`      |
| `storage.upload-url`| `logos_storage_call_upload_url`|
| `storage.peer-id`   | `logos_storage_call_peer_id`   |

Hyphens are replaced by underscores.

**Reserved lifecycle names.** The lifecycle/runtime exports
`logos_<module>_name`, `_schema`, `_version`, `_init`, `_destroy`, and
`_dispatch` occupy the plain `logos_<module>_*` namespace. Per-method C
functions therefore use the canonical form `logos_<module>_call_<method>` so
schema methods such as `init`, `version`, or `destroy` do not collide with the
required lifecycle symbols. This affects only the generated C symbol names;
the wire method name remains the bare schema method name (for example
`"version"`).

**Type names.** CDDL named types map to `logos_<module>_<type_snake>_t`:

| CDDL type        | C type                              |
|------------------|-------------------------------------|
| `space-info`     | `logos_storage_space_info_t`        |
| `peer-info`      | `logos_storage_peer_info_t`         |

Types from `logos_common.cddl` are prefixed with `logos_` (no module):

| CDDL type           | C type                      |
|----------------------|-----------------------------|
| `logos-result`       | `logos_result_t`            |
| `logos-error-code`   | `logos_error_code_t`        |

**Event constants.** Event names map to C `#define` constants:

```c
#define LOGOS_STORAGE_EVENT_UPLOAD_PROGRESS  "storage.upload-progress-event"
#define LOGOS_STORAGE_EVENT_UPLOAD_DONE      "storage.upload-done-event"
```

Pattern: `LOGOS_<MODULE>_EVENT_<NAME_UPPER>` where hyphens become underscores.

### 2.2 Primitive Type Mapping

| CDDL type  | CBOR major type           | C type                          | Notes                              |
|------------|---------------------------|---------------------------------|------------------------------------|
| `bool`     | 7 (simple true/false)     | `bool`                          | `<stdbool.h>`                      |
| `uint`     | 0 (unsigned integer)      | `uint64_t`                      | Always 64-bit for ABI stability    |
| `int`      | 0 or 1 (signed integer)   | `int64_t`                       | Always 64-bit                      |
| `float64`  | 7 (double-precision)      | `double`                        |                                    |
| `tstr`     | 3 (text string)           | `const char*`                   | UTF-8, null-terminated             |
| `bstr`     | 2 (byte string)           | `const uint8_t*` + `size_t`    | Always pointer + length pair       |

**Constrained integers:**

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
space-info = {
    quota: uint,
    used: uint,
    available: uint,
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
peer-info = {
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
| `[* uint]`       | `const uint64_t* items, size_t count`  |
| `[* T]` (struct) | `const logos_T_t* items, size_t count` |

Fixed-length tuples `[T, U, V]` expand to individual struct fields or
function arguments with generated names (`_0`, `_1`, `_2` or taken from
context).

**Choices (tagged unions).** Type choices map to tagged unions:

```cddl
value = uint / tstr / bool
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

The discriminant order matches CDDL declaration order.

**Constraint:** All arms of a choice MUST have distinct CBOR major types so
the decoder can unambiguously determine which arm was sent. For example,
`uint / tstr / bool` is valid (major types 0, 3, 7). `uint / int` is NOT
valid because both use major type 0 for non-negative values. If two arms
would collide, use a wrapping map with a discriminant key instead.

### 2.4 Method Mapping

A request/response pair maps to a single C function:

```cddl
storage.exists-request = {
    cid: tstr,
}
storage.exists-response = {
    exists: bool,
}
```

maps to:

```c
logos_result_t logos_storage_call_exists(
    logos_module_handle_t* h,
    const char*            cid,          /* from request map */
    bool*                  out_exists    /* from response map */
);
```

**Rules:**

1. First parameter is always `logos_module_handle_t* h`.
2. Request map fields expand to input parameters, in CDDL declaration order.
   Names are derived from the CDDL key (hyphens to underscores).
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

**Note on codegen abstraction:** The C signatures above are the **wire-facing
API** — what the runtime and transport layer see. Module authors using a
codegen tool may write simpler signatures with native return types (e.g. `int64_t add(int64_t a, int64_t b)`).
The codegen wraps these into the canonical `logos_result_t`-returning form.
This is an implementation convenience, not a spec concern — the generated code MUST conform to the signatures specified here.

**More examples:**

```cddl
storage.space-request = {}
storage.space-response = {
    info: space-info,
}
```

```c
logos_result_t logos_storage_call_space(
    logos_module_handle_t*          h,
    logos_storage_space_info_t*     out_info
);
```

```cddl
storage.upload-url-request = {
    url: tstr,
    chunk-size: uint,
}
storage.upload-url-response = {
    accepted: bool,
}
```

```c
logos_result_t logos_storage_call_upload_url(
    logos_module_handle_t* h,
    const char*            url,
    uint64_t               chunk_size,
    bool*                  out_accepted
);
```

### 2.5 Event Type Mapping

Event types generate a C struct for the event payload:

```cddl
storage.upload-progress-event = {
    session: tstr,
    bytes-sent: uint,
    bytes-total: uint,
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
The event struct is used by the codegen'd decode layer to convert dCBOR event
payloads into typed C structs.

### 2.6 Module Lifecycle Symbols

Every module shared library MUST export these C symbols:

- `logos_<module>_name()` returns the module name as a static string that
  remains valid for the library lifetime.
- `logos_<module>_schema()` returns the canonical CDDL schema text as a
  static string that remains valid for the library lifetime.
- `logos_<module>_version()` returns a concise schema version string such as
  `"1.0"`.
- `logos_<module>_init()` is called once after loading.
  It returns `0` on success or a nonzero Logos error code on failure.
- `logos_<module>_destroy()` is called once before unloading.
- `logos_<module>_dispatch()` is the socket-mode entry point.
  It receives the bare method name plus the dCBOR-encoded request payload.
  It does not parse the outer transport envelope.
- `logos_free()` releases typed dynamic outputs and module-kit helper
  allocations returned across this ABI.
- `logos_<module>_dispatch()` MUST:
  - look up the method in the generated dispatch table,
  - return `METHOD_NOT_FOUND` for an unknown method,
  - decode `params_cbor` according to the method request schema,
  - return `INVALID_PARAMS` if decode fails,
  - call the corresponding per-method C function,
  - encode a successful response as a dCBOR map matching the method response
    schema, and
  - encode a module-level error as the error payload described in section 4.4.
- The caller frees any non-null `_dispatch()` response buffer with `free()`.
  This is a narrow dispatch-buffer rule:
  `_dispatch()` response buffers are allocated with the C allocator because
  the dispatch ABI is the lowest common denominator used by independent
  module hosts.
  Typed per-method outputs and module-kit helper allocations use
  `logos_free()` as described in section 2.7.
- `logos_module_name()` is the bootstrap symbol for runtimes that do not know
  the module name in advance.
  Modules SHOULD export this symbol so directory scanners can discover them
  without sidecar metadata.
  Runtimes MUST also support loading modules whose name is already known from
  a manifest, static registration table, command-line argument, or equivalent
  host/deployment metadata.

```c
/* Module name (static string, valid for library lifetime) */
const char* logos_<module>_name(void);

/* CDDL schema (static string, valid for library lifetime) */
const char* logos_<module>_schema(void);

/* Schema version string (e.g. "1.0") */
const char* logos_<module>_version(void);

/* Initialise module (called once after loading).
 * Returns LOGOS_OK (0) on success, or a non-zero logos-error-code on failure. */
int logos_<module>_init(void);

/* Shut down module (called once before unloading) */
void logos_<module>_destroy(void);

/* Dispatch a method call (socket-mode entry point).
 *
 * The module host extracts the method name and params from the Transport
 * Request envelope and passes them separately. Dispatch does NOT parse
 * the envelope.
 *
 * Behaviour:
 * 1. Look up `method` in the dispatch table (generated by codegen).
 *    If not found: return LOGOS_ERR_METHOD_NOT_FOUND, *response = NULL.
 * 2. Decode `params_cbor` according to the method's `-request` schema.
 *    If invalid: return LOGOS_ERR_INVALID_PARAMS, *response = NULL.
 * 3. Call the corresponding per-method C function.
 * 4. On success: encode return values as a dCBOR map matching the
 *    method's `-response` schema. Write to *response / *response_len.
 * 5. On module error: encode error-payload {code, message, ?detail}
 *    to *response. The module host wraps this in a Transport Response
 *    with the `error` field.
 *
 * The caller (module host) frees *response with free().
 * This rule applies only to the raw dispatch response buffer.
 * Typed dynamic outputs use logos_free().
 */
int logos_<module>_dispatch(
    const char*     method,         /* bare method name (e.g. "exists") */
    const uint8_t*  params_cbor,    /* dCBOR-encoded params map */
    size_t          params_len,
    uint8_t**       response,       /* callee allocates with malloc() */
    size_t*         response_len
);

/* Bootstrap symbol — universal probe for unknown modules.
 * The runtime calls dlsym("logos_module_name") to discover the module
 * name, then uses the module-specific prefix for all other symbols. */
const char* logos_module_name(void);

/* Shared deallocator for typed dynamic outputs and module-kit helpers */
void logos_free(void* ptr);
```

Plus all per-method C functions derived from the CDDL schema (section 2.4).

**Note on `_version()`:** The current ABI keeps `logos_<module>_version()`
as a separate well-known symbol even though the schema text returned by
`logos_<module>_schema()` also contains version metadata. A future revision
MAY simplify the ABI by removing `_version()` and treating the schema as the
sole source of version information.

The benefits of keeping `_version()` in v0.1 are pragmatic:

- **Cheap probing:** the runtime can query a small, stable symbol without
  parsing the full schema text.
- **Compatibility checks:** version lookup is easy during discovery,
  loading, and connection setup.
- **Operational clarity:** logs, diagnostics, and crash reports can report a
  concise version string directly.
- **Low implementation cost:** codegen and hand-written modules can expose it
  trivially, while still keeping the schema authoritative for interface shape.

In **direct mode** (in-process), the runtime calls per-method functions
directly. In **socket mode**, the runtime calls `_dispatch()` which decodes
the dCBOR request and delegates to the appropriate per-method function. The
`_dispatch()` implementation is generated by the codegen tool.

**Important distinction: lifecycle `_init()` vs schema method `init`.**

The lifecycle symbol `logos_<module>_init(void)` is part of the runtime ABI.
It is called by the runtime after loading the shared library and before the
module is exposed for calls. It is for runtime/loader initialisation only.

If a module schema also declares an ordinary method named `init` (for example
`storage.init-request` / `storage.init-response`), that method is a normal
schema-defined request/response method with C symbol
`logos_<module>_call_init` and wire method name `"init"`. It is distinct from
the lifecycle symbol and MAY perform application-level configuration or setup
that remains necessary after lifecycle `_init()` has succeeded.

Successful lifecycle `_init()` therefore means:

- the module has loaded correctly into the runtime
- the runtime may call `_dispatch()` or direct per-method entry points

It does **not** mean every schema-defined method must already succeed.
Schema-defined methods MAY still return `LOGOS_ERR_NOT_READY` until the
module's own API-level setup sequence is complete.

### 2.7 Memory Management

Memory-management behavior is normative wherever ownership crosses the module
boundary.
Without this, independently implemented runtimes and modules cannot safely
interoperate.

The ABI therefore defines one shared deallocation function for typed dynamic
outputs and module-kit helper allocations:

```c
void logos_free(void* ptr);
```

**Lifetime rules:**

- `logos_result_t.message` and `.detail` are valid until the next call to any
  `logos_*` function on the same handle. Callers MUST copy to retain.
- Output pointers (`out_*`) for dynamically-sized data (`tstr`, `bstr`,
  arrays) are allocated by the callee. Callers free with `logos_free()`.
- Output structs are caller-allocated (passed as pointer); the callee fills
  them in. Any dynamic fields within the struct (strings, arrays) are
  callee-allocated and freed with `logos_free()`.
- All `const` pointer input parameters are borrowed for the duration of the
  call. Modules MUST copy if they need to retain.
- `_name()` and `_schema()` return static strings. Callers MUST NOT free.
- Raw `_dispatch()` response buffers are the one exception to the
  `logos_free()` rule:
  they are allocated with `malloc()` and freed by the module host with
  `free()` as specified in section 2.6.

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
| `uint8_t` | `uint .size 1` |
| `uint16_t` | `uint .size 2` |
| `uint32_t` | `uint .size 4` |
| `uint64_t` | `uint` |
| `int8_t` | `int .size 1` |
| `int16_t` | `int .size 2` |
| `int32_t` | `int .size 4` |
| `int64_t` | `int` |
| `double` | `float64` |
| `const char*` | `tstr` |
| `const uint8_t*` + `size_t` (pair) | `bstr` |
| `logos_<module>_<type>_t` | Named struct type |
| `const T*` + `size_t` (pair) | `[* T]` (array) |
| `logos_result_t` | (return type only; maps to error handling) |
| `logos_module_handle_t*` | (first param only; not in CDDL) |

**Disallowed C constructs in the API surface:**

- `void*` (except in `logos_free`)
- Raw pointers that are not `const char*` or `const uint8_t* + size_t`
- Function pointers (no callbacks in module interfaces)
- `float` (use `double`)
- Bitfields, bit-packed structs
- `enum` not declared as `logos_*_t` (use explicit integer types or declared enums)

### 3.2 Function Signature Recognition

The codegen tool recognises module functions by pattern:

```c
logos_result_t logos_<module>_<method>(
    logos_module_handle_t* h,
    <input params...>,
    <output params...>        /* out_ prefix */
);
```

- The `logos_module_handle_t*` first parameter is stripped (not in CDDL).
- Input parameters (no `out_` prefix) become request map fields.
- Output parameters (`out_` prefix, pointer types) become response map fields.
- `logos_result_t` return is stripped (error handling, not in CDDL data).

**Parameter name to CDDL key:** underscores become hyphens.
`chunk_size` -> `chunk-size`.

**Example:**

```c
logos_result_t logos_storage_upload_url(
    logos_module_handle_t* h,
    const char*            url,
    uint64_t               chunk_size,
    bool*                  out_accepted
);
```

Generates:

```cddl
storage.upload-url-request = {
    url: tstr,
    chunk-size: uint,
}
storage.upload-url-response = {
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
space-info = {
    quota: uint,
    used: uint,
    available: uint,
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
storage.upload-progress-event = {
    session: tstr,
    bytes-sent: uint,
    bytes-total: uint,
}
```

### 3.5 Lifecycle Symbol Recognition

The lifecycle symbols (`_name`, `_schema`, `_version`, `_init`, `_destroy`,
`_dispatch`) are recognised by name and excluded from the CDDL schema. They
are part of the runtime contract, not the module interface.

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

## 4. CDDL-to-dCBOR Canonical Encoding

When a method call is serialised for socket transport, the mapping from the
CDDL schema to dCBOR bytes is defined here. This section and section 2 are
two views of the same schema — the C API is the in-process view, the dCBOR
encoding is the on-the-wire view.

### 4.1 Primitive Encoding

| CDDL type  | dCBOR encoding                        |
|------------|---------------------------------------|
| `bool`     | Simple value: true (0xf5) / false (0xf4) |
| `uint`     | Major type 0, shortest encoding       |
| `int`      | Major type 0 (positive) or 1 (negative), shortest |
| `float64`  | Major type 7; dCBOR uses shortest lossless encoding |
| `tstr`     | Major type 3 (text string)            |
| `bstr`     | Major type 2 (byte string)            |

### 4.2 Composite Encoding

**Maps (structs):** dCBOR map (major type 5) with text string keys. Keys MUST
be sorted using the length-first ordering defined in section 4.5.

```
space-info -> {
    "available": 1073741824,    ; keys sorted: a < q < u
    "quota": 10737418240,
    "used": 9663676416,
}
```

Note: dCBOR wire order (key-sorted) differs from C struct order (declaration
order). Encoders sort; decoders match by key name.

**Arrays:** dCBOR array (major type 4), definite length.

**Optional fields:** Absent keys are simply omitted from the dCBOR map. The
`has_<field>` flag in the C struct is the decoded representation of key
presence.

**Choices:** Encoded as the raw dCBOR value of the selected alternative. The
decoder determines which alternative was sent by inspecting the dCBOR major
type.

### 4.3 Method Call and Event Encoding

Method params, response results, and event data are each encoded as dCBOR
maps per §4.1-4.2. The Transport envelope (tags 101, 102, 105) wraps
these maps — see LOGOS-MODULE-TRANSPORT §1.3 for the full envelope format.

**Example — `storage.exists` request params:**
```
{"cid": "bafy..."}     ; dCBOR map, keys sorted per §4.5
```

**Example — `storage.exists` response result:**
```
{"exists": true}
```

For methods with empty responses, the result is an empty map `{}`.
For events, the `data` field encodes the event schema map.

### 4.5 dCBOR Requirement

All encoded payloads at the module boundary MUST use dCBOR.
At minimum, this implies the RFC 8949 Section 4.2.1 deterministic encoding
rules:

1. Map keys MUST be sorted using the Length-First Map Key Ordering of
   RFC 8949 Section 4.2.1:
   keys are first compared by the length of their encoded forms, with shorter
   keys preceding longer keys;
   ties are broken by byte-wise lexicographic comparison of the encoded forms.
2. Integers MUST use the shortest possible encoding.
3. Indefinite-length encodings MUST NOT be used.
4. Duplicate map keys MUST NOT appear.
5. Floating-point values MUST use the shortest encoding that preserves the
   value (float16 if lossless, else float32, else float64). Note: module
   schemas use `float64` as the type; the shorter encoding is a wire
   optimisation only. Decoders MUST accept any float width and promote to
   `double` in C.

### 4.6 Validation

Implementations MUST:

1. Reject any incoming dCBOR that violates the determinism rules in section
   4.5 with error code `INVALID_PARAMS`.
2. Validate all outgoing dCBOR in debug builds.
3. Reject unknown method names -> error code `METHOD_NOT_FOUND`.
4. Reject wrong parameter types or missing required fields ->
   error code `INVALID_PARAMS`.

For module method payloads, schema validation is owned by the module dispatch
layer generated from or implemented against the module's CDDL schema.
The runtime and transport layers validate envelopes and routing fields.
They MUST NOT be required to introspect module payload schemas while forwarding
socket or remote calls.

### 4.7 Error Propagation

The error path from module to caller spans all three specs:

```
Module C function returns logos_result_t with code != LOGOS_OK
    |
    v
_dispatch() encodes error as dCBOR error-payload: {code, message, ?detail}
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
`logos_result_t` directly. No encoding, no transport, no dispatch. The error
code passes through unchanged.

**Protocol-level errors** are distinct from method errors.
Protocol errors indicate connection/framing problems, such as malformed dCBOR
or an unknown transport message kind.
Method errors are carried in Response messages with the `error` field. A
module returning `LOGOS_ERR_METHOD_NOT_FOUND` produces a Response error, not
a protocol error.

---

## 5. Common Types (`logos_common.cddl`)

The following types are shared by all modules and the transport protocol.
They are defined in `logos_common.cddl` and available to all module schemas.

### 5.1 CDDL Definitions

```cddl
; logos_common.cddl

; -- error codes --
logos-error-code = &(
    ok:                0,
    method-not-found:  1,
    invalid-params:    2,
    module-error:      3,
    not-authorised:    4,
    transport-error:   5,
    timeout:           6,
    version-mismatch:  7,
    not-ready:         8,
    cancelled:         9,
)

; -- result type --
logos-result = {
    code: logos-error-code,
    ? message: tstr,
    ? detail: bstr,
}

; -- module handle (opaque, not on wire) --
; logos_module_handle_t is a runtime concept, not serialised.
; It appears only in C signatures as the first parameter.

; -- introspection (well-known method, available on all modules) --
logos.schema-request = {}
logos.schema-response = {
    schema: tstr,
}
```

All three well-known methods are provided automatically by the runtime and
codegen. Module authors do not declare them.

`logos.schema` returns the raw CDDL text via the `_schema()` lifecycle
symbol. `logos.methods` returns a structured method list (derived from
the CDDL schema, not a parallel structure). `logos.modules` is provided
by the runtime (not individual modules) and returns all known modules.

```cddl
; -- method listing (well-known, on all modules) --
logos.methods-request = {}
logos.methods-response = {
    methods: [* method-info],
}

method-info = {
    name:    tstr,
    params:  [* param-info],
    returns: [* param-info],
}

param-info = {
    name: tstr,
    type: tstr,                 ; CDDL type name ("int", "tstr", etc.)
}

; -- module listing (well-known, provided by runtime) --
logos.modules-request = {}
logos.modules-response = {
    modules: [* module-info],
}

module-info = {
    name:    tstr,
    version: [uint, uint],
    state:   tstr,              ; "ready", "loaded", "error", etc.
}
```

### 5.2 C Definitions (`logos_types.h`)

The following C definitions are normative:

- `logos_error_code_t` defines the shared error-code space used at the
  module boundary.
- `logos_result_t.message` is human-readable text and MAY be `NULL`.
- `logos_result_t.detail` is an optional dCBOR detail payload and MAY be
  `NULL`.
- `logos_module_handle_t` is opaque to callers.
- A handle represents a connection to a specific module instance.
- The runtime allocates handles and callers obtain them through the runtime
  API defined in LOGOS-MODULE-RUNTIME.
- In direct mode, a handle may wrap function pointers or equivalent
  in-process dispatch state.
  In socket mode, it may wrap a transport connection or equivalent runtime
  state.
- The execution mode behind a handle is runtime-internal and MUST NOT change
  the module contract seen by callers.
- Handles are not intrinsically thread-safe.
  A single handle MUST NOT be used concurrently from multiple threads
  without external synchronization.
- `logos_free()` deallocates memory returned across the module ABI boundary.

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
    const uint8_t*      detail;       /* optional dCBOR detail; may be NULL */
    size_t              detail_len;
} logos_result_t;

/* -- Module handle -- */

/*
 * A handle represents a connection to a specific module instance.
 * The runtime allocates handles; callers obtain them via
 * logos_runtime_connect() (see LOGOS-MODULE-RUNTIME section 4.1).
 *
 * In direct mode, the handle wraps function pointers to the target
 * module's C API. In socket mode, it wraps a socket connection.
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

void logos_free(void* ptr);
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

Version negotiation happens in the Hello exchange (see LOGOS-MODULE-TRANSPORT).

---

## 7. Codegen Tool

A conformant codegen tool (`logos-cddl-gen`) applies the mapping rules from
sections 2-4 mechanically. Given the same `.cddl` input, any two
implementations MUST produce equivalent C output (same types, same
signatures, same dispatch behaviour).

### 7.1 CDDL-to-C (CDDL-first)

```
logos-cddl-gen --from-cddl <input.cddl> --output-dir <dir>
```

| Output file               | Contents                                         |
|--------------------------|--------------------------------------------------|
| `<module>.h`             | C header: typedefs, per-method function declarations, event publish helper declarations. Module author implements the per-method functions. |
| `<module>_dispatch.c`    | `_dispatch()`: dCBOR decode → C call → dCBOR encode. Also `_name()`, `_version()`, `_schema()`, `_init()` stub, `_destroy()` stub, `logos_module_name()` bootstrap symbol. |
| `<module>_events.c`      | Typed event publish helpers (section 7.4). |
| `<module>_client.h`      | Typed client stub declarations (section 7.5). |
| `<module>_client.c`      | Client stub implementations. |

### 7.2 C-to-CDDL (C-first)

```
logos-cddl-gen --from-header <input.h> --output-dir <dir>
```

Emits `<module>.cddl` (derived from the C header per section 3) plus all
files from 7.1 above. The C header MUST conform to the allowed subset
(section 3).

### 7.3 Generated Dispatch

The generated `_dispatch()` function implements the behaviour specified in
section 2.6. For each method `M` declared in the schema:

```c
if (strcmp(method, "M") == 0) {
    /* Decode params_cbor as M-request map (per §4.2) */
    /* Call logos_<module>_call_M(...) (per §2.4) */
    /* Encode result as M-response map (per §4.2) */
    /* Write to *response, *response_len */
}
```

The generated dispatch also handles the `logos.schema` well-known method
(returns `_schema()`) and unknown methods (`LOGOS_ERR_METHOD_NOT_FOUND`).

The generated `_init()` and `_destroy()` stubs are empty — module authors
override them if they need initialisation/cleanup.

### 7.4 Generated Event Publish Helpers

For each event `<module>.<name>-event` in the schema, the codegen produces
a typed helper that encodes the event payload as dCBOR and calls the
runtime-provided publish function:

```c
/* From: storage.upload-progress-event = { session: tstr, bytes-sent: uint, bytes-total: uint } */
void logos_storage_publish_upload_progress(
    logos_publish_fn  publish,
    void*             publish_user_data,
    const char*       session,
    uint64_t          bytes_sent,
    uint64_t          bytes_total
);
```

The implementation dCBOR-encodes `{session, bytes-sent, bytes-total}` per
section 4.2 and calls
`publish(publish_user_data, "storage.upload-progress-event", cbor, cbor_len)`.

Module authors call the typed helper instead of encoding dCBOR manually.
`publish_user_data` is the process-local callback context installed by the
runtime or module host, as defined by LOGOS-MODULE-RUNTIME.

### 7.5 Generated Client Stubs

For each method, the codegen produces a typed client function that encodes
a dCBOR request, calls the runtime-provided module call function, and
decodes the response:

```c
/* From: storage.exists-request = { cid: tstr }
 *       storage.exists-response = { exists: bool } */
logos_result_t logos_storage_client_exists(
    logos_call_module_fn  call,
    void*                 call_user_data,
    const char*           cid,
    bool*                 out_exists
);
```

The implementation dCBOR-encodes `{cid}`, calls
`call(call_user_data, "storage_module", {"method":"exists","params":{cid}}, len,
&resp, &resp_len)`,
decodes the response map, and writes `out_exists`. The signature mirrors
the per-method function (section 2.4) but takes `logos_call_module_fn`
instead of `logos_module_handle_t*`.
`call_user_data` follows the same process-local callback context rules as
the runtime-provided call-module hook.

### 7.6 Framework-Specific UI Bindings

A codegen tool MAY produce UI-framework-facing bindings derived from the same
CDDL schema.
Such bindings are derived views over the canonical module contract, not
parallel interfaces.

The CDDL schema remains the canonical interface definition.
Framework-specific binding details are out of scope for this specification.

### 7.7 Integration with logos-module-builder

`logos-module-builder` and similar tooling are downstream integrations over
this specification.
They are not normative parts of the interface contract.

A builder MAY invoke `logos-cddl-gen` automatically as part of its build
pipeline so that module authors do not need to run code generation manually.
That is an implementation convenience, not a protocol requirement.

---

## 8. Streaming and Chunked Data (Future)

This version of the spec does NOT address streaming or chunked transfer of
large payloads. A 100MB file cannot be sent as a single `bstr` within a
single dCBOR message (given default message size limits).

Future versions will specify a streaming mechanism. Options under
consideration:

- Chunked transfer as a sequence of Request/Response messages
- A dedicated stream message type in the transport protocol
- Out-of-band data channels referenced by handle

Module authors needing large data transfer in this version should use filesystem paths
or external references (URLs, CIDs) rather than inline byte strings.

---

## 9. References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
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
