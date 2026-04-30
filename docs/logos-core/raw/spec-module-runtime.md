# LOGOS-MODULE-RUNTIME

| Field    | Value                                      |
|----------|--------------------------------------------|
| Name     | Logos Module Runtime                       |
| Slug     | LOGOS-MODULE-RUNTIME                       |
| Status   | raw                                        |
| Category | Standards Track                            |
| Editor   | ksr                                        |
| Contributors | Jarrad, atd                            |

## Abstract

This specification defines how Logos modules are loaded, discovered,
connected, and managed at runtime. It covers:

- The plugin loading mechanism (replacing Qt's `QPluginLoader`)
- The service registry (how the runtime knows which modules exist)
- Module routing (how a call from module A reaches module B)
- Event subscription (how modules publish and receive events)
- Process isolation models (multi-process vs single-process)
- Module lifecycle (unloaded -> loaded -> ready -> stopping -> unloaded)
- Threading and concurrency model
- Packaging (how module code + schema + metadata are bundled)
- Streaming and large data (acknowledged gap)

An implementor who reads this document and LOGOS-MODULE-INTERFACE
should be able to write a complete alternative module runtime in any language.

In particular, an implementation in Nim, Rust, or another language MUST
NOT need Qt in order to satisfy this specification. Qt-based launcher or host
integration code may exist in a specific application, but that is not part of
the normative runtime model here.

This spec does NOT define the module interface format (see
LOGOS-MODULE-INTERFACE) or the socket wire protocol (see
LOGOS-MODULE-TRANSPORT).

This spec also does NOT define host-application-specific launcher plumbing
such as package scanning policy, GUI-framework process management, or any
particular auth-token handoff mechanism between a host shell and a spawned
module process. A concrete host MAY implement such mechanisms, but they are
deployment concerns rather than part of the reusable module-runtime contract.

### Execution-Boundary Equivalence

The runtime MAY realize the same module contract through different execution
boundaries:

- **Direct mode** — in-process C calls
- **Socket mode** — local IPC using LOGOS-MODULE-TRANSPORT
- **Remote mode** — remote RPC using the same transport model

These are different runtime/transport realizations of the same interface
contract, not three different APIs.

A conforming runtime MUST preserve the same observable module semantics across
those modes:

- the same module, method, and event identifiers
- the same schema-defined request, response, and event shapes
- the same success/error meaning at the module boundary
- the same schema-version compatibility rules

The runtime MAY change routing, framing, process placement, scheduling,
connection management, capability enforcement, or reconnection behavior by
mode. It MUST NOT silently change the module contract itself when switching a
callee between direct, local IPC, or remote execution.

## 1. Module Structure

### 1.1 What a Module Is

A module is a shared library (`.so`, `.dylib`, `.dll`) or a standalone
executable that:

1. Exports a set of well-known C symbols (defined in LOGOS-MODULE-INTERFACE
   section 2.6)
2. Ships a CDDL schema file describing its interface
3. Can be loaded by the runtime and connected to other modules

### 1.2 Required Exports

Every module shared library MUST export these symbols with C linkage:

| Symbol | Purpose |
|--------|---------|
| `logos_<module>_name()` | Returns the module's unique name |
| `logos_<module>_schema()` | Returns the CDDL schema as a string |
| `logos_<module>_version()` | Returns the schema version string |
| `logos_<module>_init()` | Initialise the module |
| `logos_<module>_destroy()` | Shut down the module |
| `logos_<module>_dispatch()` | Handle a CBOR RPC request |

Plus all per-method C functions declared in the CDDL schema (see
LOGOS-MODULE-INTERFACE section 2.4 for the signature mapping).

### 1.3 Module Naming

Module names are non-empty UTF-8 strings matching `[a-z][a-z0-9_]*`, with a
maximum length of 64 bytes. Examples: `storage_module`, `capability_module`,
`delivery_module`.

The name is used to:
- Derive socket paths: `<runtime-dir>/logos_<name>.sock`
- Derive C symbol prefixes: `logos_<name>_*`
- Look up modules in the service registry

---

## 2. Plugin Loading

### 2.1 Dynamic Loading

On platforms that support dynamic loading (Linux, macOS, Windows desktop), the
runtime loads modules using the platform's dynamic linker:

- Linux/macOS: `dlopen(path, RTLD_NOW | RTLD_LOCAL)`
- Windows: `LoadLibrary(path)`

After loading, the runtime looks up the required symbols:

```c
void* lib = dlopen("storage_module.so", RTLD_NOW | RTLD_LOCAL);

/* Look up the name function to identify the module */
typedef const char* (*name_fn)(void);
name_fn get_name = (name_fn)dlsym(lib, "logos_storage_module_name");
const char* name = get_name();  /* "storage_module" */

/* Look up remaining lifecycle symbols */
typedef const char* (*schema_fn)(void);
schema_fn get_schema = (schema_fn)dlsym(lib, "logos_storage_module_schema");

/* ... etc for _version, _init, _destroy, _dispatch */
```

If any required symbol is missing, the module MUST be rejected with a
descriptive error.

### 2.2 Symbol Discovery Convention

Because the module prefix contains the module name (which the runtime may not
know before loading), there are two discovery strategies:

**Strategy A: Known name.** The runtime knows the module name (from a
manifest, command-line argument, or package metadata) and constructs the
symbol names directly: `logos_<known_name>_name`, etc.

**Strategy B: Bootstrap symbol.** For cases where the runtime loads an
unknown `.so`, the module MAY export a generic bootstrap symbol:

```c
/* Optional: allows loading without knowing the module name in advance */
const char* logos_module_name(void);
```

This returns the module name, which the runtime then uses to look up the
remaining prefixed symbols.

Modules SHOULD export the bootstrap symbol. The runtime MUST support both
strategies.

### 2.3 Static Linking (Mobile / iOS)

On platforms where dynamic loading is unavailable (iOS), modules are
statically linked into the application binary. The runtime discovers them
via a registration table:

- The registration table is a static module vtable whose fields correspond to
  the lifecycle and dispatch symbols defined in
  LOGOS-MODULE-INTERFACE section 2.6.
- For statically linked modules, the runtime uses these function pointers
  instead of resolving symbols with `dlsym`.
- The module author owns the vtable object.
  The runtime copies the pointers it needs during registration, so the caller
  does not need to preserve the registration struct after the call returns.
- Applications MUST register statically linked modules before
  `logos_runtime_start()`.

```c
/* Module vtable for static registration.
 *
 * Each field corresponds to a lifecycle symbol from LOGOS-MODULE-INTERFACE
 * section 2.6. For statically linked modules, these are function pointers
 * instead of dlsym'd symbols.
 *
 * The vtable is owned by the module author (typically a static const).
 * The runtime copies the pointers during registration — the vtable
 * struct itself does not need to remain valid after the register call.
 */
typedef struct {
    const char*         name;       /* -> logos_<module>_name() */
    const char*         (*schema)(void);
    const char*         (*version)(void);
    int                 (*init)(void);
    void                (*destroy)(void);
    int                 (*dispatch)(const char* method,
                                    const uint8_t* params_cbor, size_t params_len,
                                    uint8_t** response, size_t* response_len);
    logos_publish_fn    publish;    /* may be NULL; runtime sets it during init */
} logos_module_vtable_t;

/* Application registers modules at startup.
 * Must be called before logos_runtime_start(). */
void logos_runtime_register_module(const logos_module_vtable_t* vtable);
```

### 2.4 Standalone Process Mode

A module MAY run as a standalone executable (rather than a shared library
loaded by the runtime). In this mode:

- The module binary starts, binds a Unix domain socket or TCP port, and
  listens for CBOR RPC requests (per LOGOS-MODULE-TRANSPORT).
- The runtime connects to the module as a client.
- The module still exports the dispatch function internally, but calls arrive
  over the socket rather than via `dlopen`.

This mode is useful for modules written in languages that don't produce
shared libraries (e.g. a Go module, a JVM module).

Security requirements for standalone process mode are the same as for any
socket-hosted module:

- the runtime MUST authenticate the peer according to the active runtime
  security policy,
- the transport connection MUST satisfy the requirements of
  LOGOS-MODULE-TRANSPORT for local or remote mode, and
- the execution mode MUST NOT weaken the module contract or bypass normal
  authorization and routing rules.

### 2.5 Introspection

A running module's interface can be introspected at runtime by calling
`logos_<module>_schema()`, which returns the CDDL schema as a string. This
enables:

- Runtime type checking of calls
- Auto-generation of client stubs
- UI-based module browsers
- Remote module discovery

In socket mode, the schema is also available via the well-known
`logos.schema` method (defined in `logos_common.cddl`, see
LOGOS-MODULE-INTERFACE section 5.1). This method is provided automatically
by the runtime and codegen tool — module authors do not declare it.

---

## 3. Service Registry

### 3.1 Purpose

The service registry maps module names to their locations (socket paths,
in-process vtables, or remote addresses). It is the runtime's answer to the
question: "Where is module X?"

### 3.2 Registry Implementation

The registry is a simple in-memory table maintained by the runtime:

```
module_name  ->  {
    state:       unloaded | loaded | ready | stopping | error
    mode:        direct | socket | remote
    location:    <function pointers>  (direct mode)
                 <socket path>        (socket mode)
                 <host:port>          (remote mode)
    schema:      <CDDL string>
    version:     [major, minor]
    pid:         <process id>         (socket mode only)
}
```

### 3.3 Module States

```
                 load()              init() returns OK
  [unloaded] ──────────> [loaded] ──────────────────> [ready]
                             |                           |
                             v                           v
                          [error]                    [stopping]
                                                        |
                                          destroy()     v
                                                    [unloaded]
```

- **unloaded:** Module is known (from config/manifest) but not loaded.
- **loaded:** `dlopen` succeeded; `_init()` not yet called or in progress.
- **ready:** `_init()` returned `LOGOS_OK`. The module is now runtime-ready:
  the runtime MAY route calls to it and the module MUST be able to accept
  requests and return protocol-valid success or error responses.
- **stopping:** `_destroy()` has been called; waiting for cleanup.
- **error:** Loading or initialisation failed. Error details available.

There is no separate "running" state. A module in `ready` state accepts
calls. The runtime tracks active call count internally for graceful shutdown
but this is not a module state.

**Important distinction: runtime-ready vs application-ready.**

The lifecycle symbol `logos_<module>_init(void)` is runtime/loader
initialisation only. It establishes that the shared library has loaded
correctly and is ready to participate in the runtime contract (dispatch,
publish hook installation, outbound-call hook installation, etc.).

It does **not** imply that all schema-defined methods will succeed
immediately. A module MAY still require one or more ordinary schema methods
such as `init`, `start`, login/session establishment, or similar
application-level setup before its full business functionality is available.
Until that setup is complete, schema-defined methods MAY return
`LOGOS_ERR_NOT_READY`.

Therefore:

- the runtime transitions to `ready` after successful lifecycle `_init()`
- the runtime MAY route requests to the module in that state
- callers MUST still handle per-method `LOGOS_ERR_NOT_READY` responses
- method-level readiness is part of the module's schema/API semantics, not a
  separate runtime lifecycle state

### 3.4 Discovery Sources

The runtime discovers modules from these sources, in order:

1. **Configuration file.** A CBOR or JSON config listing module names,
   paths, and options.
2. **Plugin directories.** The runtime scans one or more directories for
   `.so`/`.dylib` files and probes each using the bootstrap symbol
   (see section 3.5).
3. **Package manifests.** LGX packages contain a `manifest.json` that lists
   the module name, version, and entry point.
4. **Runtime registration.** For static linking or test scenarios, modules
   are registered programmatically via `logos_runtime_register_module()`.

### 3.5 Plugin Directory Scanning

When scanning a plugin directory, the runtime probes each `.so`/`.dylib`
file to extract metadata. The probe uses `dlopen` + `dlsym` — no framework-
specific metadata embedding is required.

**Probe procedure:**

```
for each .so file in plugin_dir:
    1. handle = dlopen(path, RTLD_NOW | RTLD_LOCAL)
       if failed: skip (not a valid shared library)

    2. name_fn = dlsym(handle, "logos_module_name")
       if not found: dlclose, skip (not a Logos module)

    3. name = name_fn()
       if empty or invalid: dlclose, skip

    4. Look up optional metadata symbols:
       - logos_<name>_version()  -> schema version
       - logos_<name>_schema()   -> CDDL schema text

    5. Register in service registry:
       { name, path, version, schema, state: unloaded }

    6. dlclose(handle)  -- module is not loaded yet, only discovered
```

This approach has no dependency on Qt's `QPluginLoader` or embedded JSON
metadata. Any shared library that exports `logos_module_name()` is
discoverable.

**The bootstrap symbol `logos_module_name()` is the sole requirement for
discovery.** Version and schema symbols are optional at discovery time
(they can be queried after loading). This keeps the bar low for module
authors: export one function, and the runtime finds you.

### 3.6 Module Dependencies

A module MAY declare dependencies on other modules in its package manifest
(not in the CDDL schema -- the schema describes the interface, not deployment
requirements):

```json
{
    "name": "delivery_module",
    "depends": ["storage_module", "capability_module"]
}
```

The runtime MUST ensure dependencies are loaded and initialised before the
dependent module's `_init()` is called.

Circular dependencies are an error. The runtime MUST detect and reject them.

---

## 4. Module Routing and Handle Acquisition

### 4.1 Connecting to a Module

A module (or the application) obtains a handle to another module via the
runtime:

```c
logos_module_handle_t* logos_runtime_connect(const char* module_name);
void                   logos_runtime_disconnect(logos_module_handle_t* h);
```

The runtime consults the registry to determine the target module's mode:

- **Direct mode:** Returns a handle wrapping function pointers to the target
  module's C API. Calls go through direct C function invocation. No
  serialisation.
- **Socket mode:** Returns a handle wrapping a socket connection to the
  target module's host process. Calls are serialised as CBOR per
  LOGOS-MODULE-TRANSPORT.
- **Remote mode:** Same as socket mode, but over TCP/TLS to a remote host.

The caller does not know or care which mode is active. The handle abstraction
hides the transport. Per-method C functions (e.g. `logos_storage_exists()`)
take a `logos_module_handle_t*` as their first argument; the handle
dispatches to the correct transport internally.

The purpose of the handle abstraction is precisely to preserve the execution-
boundary equivalence stated above: the runtime may switch routing mode, but
the module contract observed by the caller remains the same.

### 4.2 Routing Table

The runtime maintains a routing table mapping (caller, callee) pairs to
transport configurations:

| Caller | Callee | Mode | Notes |
|--------|--------|------|-------|
| (any) | storage_module | socket | Default: separate process |
| qml_ui | storage_module | direct | Mobile: same process |
| (any) | capability_module | direct | Always in-process for security |

The routing table is populated from configuration. The runtime MAY change
routes at runtime (e.g. switching from remote to local when a module becomes
available locally).

### 4.2.1 Routing View For Socket-Hosted Module Processes

When a module runs in **socket mode**, the module host process is still part of
the same logical runtime routing domain. Therefore, if that host exposes
`logos_<module>_set_call_module()`, it MUST be able to resolve outbound calls
using a routing view that is consistent with the runtime's current registry and
routing-table semantics.

This requirement is semantic, not architectural. The spec does **not** require
a specific mechanism. A conforming implementation MAY satisfy it by, for
example:

- giving the module host a local copy or snapshot of the relevant routing data
- providing the module host a runtime-managed lookup/control channel
- embedding the host in a larger runtime process that already has the routing
  table in memory

What matters normatively is:

- a socket-hosted module MUST NOT need to invent its own independent routing
  policy
- outbound calls from a socket-hosted module MUST be resolved according to the
  same runtime registry/routing rules that would apply if the caller were
  in-process
- if the implementation allows routing changes at runtime, it MUST define a
  consistency model such that hosts do not silently route according to stale or
  contradictory information

The consistency mechanism itself is implementation-defined. The interoperable
requirement is the observable behavior at the module boundary, not the control
plane used to achieve it.

### 4.3 Capability Validation

Before returning a handle, the runtime MUST verify that the caller is
authorised to access the callee. This is done via the Capability Module:

1. Caller requests access: `logos_capability_request(caller, callee)`
2. Capability Module returns a token (or denies)
3. Token is embedded in the handle
4. For socket mode: token is sent in the Hello handshake
5. For direct mode: token is validated once at handle creation time

### 4.4 Event Subscription via Handle

The handle provides generic event subscription:

```c
logos_result_t logos_runtime_subscribe(
    logos_module_handle_t* h,
    const char*            event_name,
    logos_event_handler_t  handler,
    void*                  user_data,
    uint64_t*              out_subscription_id
);

logos_result_t logos_runtime_unsubscribe(
    logos_module_handle_t* h,
    uint64_t               subscription_id
);
```

Where:

```c
typedef void (*logos_event_handler_t)(
    const char*    event_name,
    const uint8_t* cbor_data,       /* CBOR-encoded event map */
    size_t         cbor_data_len,
    void*          user_data
);
/* cbor_data is valid only for the duration of the callback.
 * Handlers MUST copy the data if they need to retain it. */
```

In **direct mode**, the module publishes events by calling a runtime-provided
publish function. The runtime delivers to local subscribers by invoking their
handlers directly.

In **socket mode**, subscriptions are translated to Subscribe messages (tag
103) per LOGOS-MODULE-TRANSPORT. Incoming Event messages (tag 105) are decoded
and delivered to the handler.

The codegen tool MAY generate typed event subscription helpers that decode
the CBOR and call a typed callback:

```c
/* Generated typed helper */
logos_result_t logos_storage_on_upload_progress(
    logos_module_handle_t* h,
    void (*handler)(const logos_storage_upload_progress_event_t*, void*),
    void* user_data,
    uint64_t* out_subscription_id
);
```

These are convenience wrappers over the generic subscription API.

---

## 5. Process Model

### 5.1 Multi-Process (Desktop Default)

Each module runs in its own OS process. The runtime (`liblogos`) spawns a
**module host** process for each module:

```
logos_host --module <path-to-module.so> --socket <socket-path>
```

The module host:

1. `dlopen`s the module shared library
2. Calls lifecycle `_init()` (no typed config is passed in the current ABI)
3. Binds the Unix domain socket
4. Enters an event loop, reading CBOR requests from the socket, dispatching
   to `_dispatch()`, and writing responses

Benefits:
- Process isolation: a crashing module doesn't bring down others
- Resource accounting: per-module CPU/memory tracking via OS tools
- Security: modules can be sandboxed (seccomp, AppArmor, etc.)

### 5.2 Single-Process (Mobile / Embedded)

All modules are loaded into one process. Calls go through direct C function
pointers. No serialisation, no sockets.

The runtime still manages the registry, lifecycle, and capability validation.
The difference is only in the transport: direct calls instead of CBOR-over-
socket.

### 5.3 Hybrid

Some modules may run in-process (capability module, small utility modules)
while others run in separate processes (storage, heavy computation). The
routing table (section 4.2) determines the mode per-module.

---

## 6. Threading and Concurrency

### 6.1 Module Threading Model

Modules MUST be safe to call from multiple threads. The runtime MAY dispatch
requests to a module from different threads concurrently (e.g. when multiple
callers invoke the same module simultaneously).

Modules that cannot handle concurrent calls MUST implement their own internal
serialisation (e.g. a mutex). The runtime does not provide call serialisation.

### 6.2 Module Host Threading

In socket mode, the module host process runs an event loop that:

- Accepts connections from multiple callers
- Reads requests from all connections (via `poll`/`epoll`/`kqueue`)
- Dispatches requests to `_dispatch()` or per-method functions

The module host SHOULD use a thread pool for dispatching requests, so that
a slow method does not block other callers. The default pool size is
implementation-defined (recommended: number of CPU cores).

### 6.3 Event Delivery Threading

Event handlers (registered via `logos_runtime_subscribe`) are called on an
unspecified thread. Handlers MUST be thread-safe. Handlers MUST NOT block
for extended periods (they run on the runtime's event delivery thread).

For UI integration (Qt, etc.), the runtime provides a mechanism to marshal
event delivery to the UI thread. This is runtime-specific and not part of
this spec.

### 6.4 Direct Mode Concurrency

In direct mode (in-process), calls execute on the caller's thread. The
module receives calls on whatever thread the caller is running on. This is
why modules MUST be thread-safe (section 6.1).

---

## 7. Event Loop

### 7.1 Runtime Event Loop

The runtime provides an event loop that:

- Accepts incoming socket connections from module host processes
- Dispatches incoming CBOR requests to the appropriate module
- Delivers events from modules to subscribers
- Handles module lifecycle transitions (start, stop, crash recovery)

For Qt-based UI applications, the runtime event loop integrates with Qt's
event loop (`QCoreApplication::exec()`). For non-Qt applications, the
runtime provides its own event loop based on `poll()`/`epoll()`/`kqueue()`.

### 7.2 Module Event Loop

Module host processes run their own event loop:

```
while running:
    msg = read_framed_cbor(socket)
    response = logos_<module>_dispatch(msg)
    write_framed_cbor(socket, response)
```

### 7.3 Module Event Publishing

A module publishes events by calling a runtime-provided function:

```c
typedef void (*logos_publish_fn)(
    const char*    event_name,
    const uint8_t* cbor_data,
    size_t         cbor_data_len
);
```

`event_name` MUST be the exact schema event identifier from the module's
CDDL, for example `storage.started-event` or
`storage.upload-progress-event`.

The runtime delivers the event to all subscribers (local or remote). In
socket mode, the module host translates `logos_publish_fn` calls into Event
messages (tag 105) on all connections with matching subscriptions.

This publish path is for **narrow asynchronous notifications** only. Modules
use it for progress, completion, and state-change signals. It is not a
general outbound method mechanism and does not replace normal
request/response dispatch.

### 7.4 How Modules Receive the Publish Function

The publish function is provided via a **well-known symbol** that the
runtime calls after `_init()` succeeds:

```c
/* Exported by the module. Called by runtime/host after _init() returns OK. */
void logos_<module>_set_publish(logos_publish_fn fn);
```

The module stores the function pointer internally. If the module does not
publish any events, it MAY omit this symbol — the runtime MUST NOT fail
if the symbol is absent.

For compatibility with older generated modules that may still publish short
event names such as `started`, a runtime MAY normalize those legacy names
to the canonical schema event name before putting them on the wire. New
modules and code generators MUST use the canonical schema event name
directly.

For statically linked modules, the publish function is set via the
`logos_module_vtable_t.publish` field (see section 2.3). The runtime sets
this field before calling `init`.

**Lifetime:** The publish function is valid from the time it is set until
`_destroy()` returns. Modules MUST NOT call it after `_destroy()`.

**Thread safety:** The publish function is thread-safe. Modules MAY call
it from any thread.

### 7.5 Outbound Calls (Calling Other Modules)

A module that needs to call another module can do so through a runtime-
provided callback, without linking the SDK or implementing the transport
protocol's client side:

```c
/* Provided by the runtime to the module after _init() */
typedef logos_result_t (*logos_call_module_fn)(
    const char*     target_module,
    const uint8_t*  request_cbor,    /* CBOR: {"method": tstr, "params": {...}} */
    size_t          request_len,
    uint8_t**       response_cbor,   /* callee allocates; caller frees with logos_free() */
    size_t*         response_len
);

/* Exported by the module. Called by runtime/host after _init() returns OK. */
void logos_<module>_set_call_module(logos_call_module_fn fn);
```

The module encodes a CBOR request map (`{method, params}`) for the target
module, calls the function, and receives a CBOR response. The runtime
handles routing — it determines whether the target is in-process, in
another process, or remote. The module does not need to know.

For socket-hosted modules, this implies that the host process supplying
`logos_call_module_fn` MUST have access to a routing view consistent with
section 4.2 and 4.2.1. The callback is a runtime function conceptually, even
when the concrete function pointer is installed by a per-module host process.

If the module does not call other modules, it MAY omit this symbol. The
runtime MUST NOT fail if the symbol is absent.

**Lifetime:** Same as `logos_publish_fn` — valid from set until `_destroy()`.

**Thread safety:** The function is thread-safe. Modules MAY call it from
any thread. Calls are synchronous — the function blocks until the target
module responds.

**Error handling:** If the target module is not found, returns
`LOGOS_ERR_MODULE` with `*response_cbor = NULL`. If the target returns an
error, the error is encoded in `response_cbor` as an error-payload map
(`{code, message, ?detail}`).

---

## 8. Packaging

Packaging is not part of the core runtime protocol.
This section is therefore informative.

The runtime requires deployable module artifacts plus enough metadata to
discover them, identify the entry point, and evaluate compatibility.
How those artifacts are packaged, signed, installed, or distributed is a
downstream concern.

An implementation MAY use LGX packages, unpacked local directories,
system packages, reproducible local builds, or other deployment formats,
provided the runtime ultimately receives the module binary and the metadata it
needs.

### 8.1 Module Package Format

One possible distribution format is an **LGX package**
(the existing `logos-package` format).
An LGX package may contain:

```
<module>.lgx/
+-- manifest.json        # Module metadata
+-- <module>.cddl        # Interface schema
+-- lib/
|   +-- <module>.so      # Shared library (Linux)
|   +-- <module>.dylib   # Shared library (macOS)
|   +-- <module>.dll     # Shared library (Windows)
+-- manifest.cose        # (Future) COSE signature for attestation
```

### 8.2 Manifest

A deployment manifest may contain:

```json
{
    "name": "storage_module",
    "version": [1, 0],
    "description": "Codex-based decentralised storage",
    "entry_point": "lib/storage_module.so",
    "schema": "storage_module.cddl",
    "depends": ["capability_module"],
    "min_runtime_version": [1, 0]
}
```

### 8.3 Package Attestation (Future)

An implementation MAY attach a COSE (RFC 9052) signature or equivalent
attestation material over the packaged contents.
For an LGX package, that could be carried in `manifest.cose`.
This enables:

- **Build reproducibility verification:** Proof that the binary was compiled
  from specific source code.
- **TEE attestation:** Proof that the module was built inside a trusted
  execution environment.
- **ZK compilation proofs:** Zero-knowledge proof that the binary corresponds
  to the source, without revealing the source.

This is a future feature.
The exact attestation format is not specified here.

---

## 9. Configuration

### 9.1 Runtime Configuration

The runtime is configured via a CBOR or JSON file:

```json
{
    "runtime_dir": "/run/user/1000/logos",
    "plugin_dirs": ["/usr/lib/logos/modules", "~/.logos/modules"],
    "modules": {
        "storage_module": {
            "mode": "socket",
            "config": { "data_dir": "/var/logos/storage" }
        },
        "capability_module": {
            "mode": "direct"
        }
    },
    "log_level": "info"
}
```

### 9.2 Module Configuration

Per-module runtime configuration is not yet part of the v0.1 module ABI.
The current ABI uses `_init(void)`.

Configuration remains a runtime concern: implementations MAY load per-module
configuration from manifests, environment variables, or host-specific config
files before calling `_init()`. A future spec revision MAY add a typed config
handoff once that ABI is settled.

---

## 10. Error Handling and Recovery

### 10.1 Module Crash Recovery

When a module host process crashes (detected via socket close or SIGCHLD),
the runtime:

1. Marks the module as `error` in the registry.
2. Notifies all connected callers with a `TRANSPORT_ERROR`.
3. Optionally restarts the module (configurable: restart policy with
   exponential backoff).
4. On restart, the module goes through the full lifecycle again
   (load -> init -> ready).

### 10.2 Graceful Shutdown

On runtime shutdown:

1. All modules receive `_destroy()` in reverse dependency order.
2. Socket connections are closed.
3. Module host processes are sent `SIGTERM`, then `SIGKILL` after a timeout.

---

## 11. CBOR-to-Qt Bridge (UI Modules)

Qt/QML bridge details are out of scope for this specification.
They belong in downstream specifications or framework-specific documents.

The only runtime-level requirement is that any such bridge preserve the
canonical module contract defined by LOGOS-MODULE-INTERFACE and the execution
semantics defined by this runtime specification.

---

## 12. Streaming and Large Data (Future)

This version of the spec does NOT address streaming or chunked transfer of
large payloads. The default message size limit (16 MB, configurable) is
sufficient for most RPC calls but not for large file transfers.

Module authors needing large data transfer in this version should:

- Use filesystem paths (for co-located modules)
- Use external references (URLs, CIDs) that the caller can fetch separately
- Use multiple smaller requests if the data can be chunked at the
  application level

Future versions may specify a streaming mechanism at the transport layer.
That transport extension belongs primarily in LOGOS-MODULE-TRANSPORT, while
any schema-level conventions for chunked methods or stream references belong
in LOGOS-MODULE-INTERFACE.

---

## References

### Normative

- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-TRANSPORT -- Socket protocol specification.

### Informative

- logos-package -- LGX package format implementation.
  https://github.com/logos-co/logos-package
- logos-liblogos -- Current runtime implementation (Qt-based).
  https://github.com/logos-co/logos-liblogos

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
