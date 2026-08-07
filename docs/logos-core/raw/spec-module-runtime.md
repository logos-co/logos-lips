# LOGOS-MODULE-RUNTIME

| Field        | Value                 |
|--------------|-----------------------|
| Name         | Logos Module Runtime  |
| Slug         | 304                   |
| Status       | raw                   |
| Category     | Standards Track       |
| Editor       | ksr                   |
| Contributors | Jarrad, atd           |

## Abstract

This specification defines how Logos modules are loaded, discovered,
connected, and managed at runtime. It covers:

- The dynamic module loading mechanism
- The service registry (how the runtime knows which modules exist)
- Module routing (how a call from module A reaches module B)
- Event subscription (how modules publish and receive events)
- Process isolation models (multi-process vs single-process)
- Module lifecycle (unloaded -> loaded -> ready -> stopping -> unloaded)
- Runtime-control interface for privileged runtime-host lifecycle control
- Threading and concurrency model
- Streaming and large data (acknowledged gap)

This spec does NOT define the module interface format (see
LOGOS-MODULE-INTERFACE) or the socket wire protocol (see
LOGOS-MODULE-TRANSPORT).

This spec also does NOT define host-application-specific launcher plumbing
such as package scanning policy, GUI-framework process management, or any
particular auth-token handoff mechanism between a runtime host and a spawned
module process. A concrete host MAY implement such mechanisms, but they are
deployment concerns rather than part of the reusable module-runtime contract.

### Execution-Boundary Preservation

LOGOS-MODULE-INTERFACE defines the execution-boundary invariant of the module
contract.

This runtime specification does not restate that invariant in full.
Its requirement is operational:

- the runtime MAY realize a module through direct mode, local transport mode,
  or remote transport mode,
- but it MUST preserve the same module contract semantics when doing so.

In other words, routing mode is a runtime concern.
Changing execution boundary MUST NOT silently change the interface contract
observed by callers.

Direct mode has two binding forms:

- **Dynamic direct mode:** the module is loaded from a dynamic library, and the
  runtime resolves the mandatory C symbols with `dlopen` / `dlsym` or an
  equivalent platform mechanism.
- **Static direct mode:** the module is linked into the application or runtime
  binary, and the runtime obtains addresses for the same mandatory C symbols
  through build-time or startup integration.

### Terminology

This specification uses the following terms:

- **Runtime instance:**
  a concrete running Logos runtime with its own registry, lifecycle state,
  routing-selection state, route state, policy enforcement points, and
  runtime-control surface.
  The runtime instance is the runtime authority boundary for ordinary module
  lifecycle, routing, provider selection, call-context creation, and route
  state.
- **Runtime Control:**
  the privileged module surface exposed by a runtime instance through the
  `logos_runtime_control` contract.
  Runtime Control is a surface of the runtime instance itself, not a separate
  module entity adjacent to the runtime.
- **Runtime host:**
  the external authority-bearing environment that creates, embeds, supervises,
  configures, or otherwise controls a runtime instance.
  A runtime host controls the runtime through Runtime Control.
  Its authority comes from the host/runtime relationship or an explicitly
  granted policy, not from ordinary Logos module status.
- **Host shell:**
  the product or application shell that presents runtime-backed capabilities to
  users.
  A host shell is responsible for user-facing app, window, package, status, and
  confirmation flows.
  A host shell may also act as a runtime host in a simple deployment, but the
  roles are distinct:
  runtime host is a control and authority role, while host shell is a product
  and user-experience role.
- **Module implementation:**
  the code or artifact that implements a module contract.
  A module implementation may be a dynamic library, statically linked code, a
  standalone transport endpoint, an operating-system process, a sandboxed or
  containerized workload, or code owned by a remote runtime.
- **Module instance:**
  a live runtime-known instance of a module implementation, with lifecycle
  state and routing identity.
  The runtime instance owns the portable Logos lifecycle semantics for module
  instances.
- **Module provider:**
  a runtime-known routing target that can satisfy calls for a module contract.
  A module provider may be backed by a local module instance, a standalone
  transport endpoint, or a remote module facade.
  This is a registry and routing concept, not a separate authority model or
  module ABI.
- **Remote runtime:**
  a runtime instance reachable over a transport boundary and authorized or
  enrolled according to active runtime policy.
- **Remote module facade:**
  a local runtime-side representation of a module whose implementation and
  lifecycle are owned by a remote runtime.
  A remote module facade is a module provider facade, not a second module ABI.
- **Route:**
  a runtime-authorized binding between a caller and a provider invocation
  endpoint.
  Runtime Control establishes, tracks, and revokes routes.
  Ordinary module calls use the provider invocation path described by the route,
  not runtime-control methods.
  A provider invocation path may be direct, local transport, or remote
  transport, but the route model does not make runtime mediation a separate
  portable route kind.

This specification uses the following execution-mode terms:

- **Direct mode:**
  caller and callee communicate through in-process C calls using the mandatory
  C module interface.
  Direct mode has dynamic and static binding forms, described in Sections 2.1
  and 2.3.
- **Local transport mode:**
  caller and callee communicate over a local IPC transport.
  This revision defines Unix domain sockets as the local stream binding.
- **Remote transport mode:**
  caller and callee communicate over a transport boundary to a remote runtime
  or remote module provider.

These execution modes are runtime realizations of the same module contract.
Changing execution mode MUST NOT silently change the module interface contract
observed by callers.

Privileged runtime modules are Logos-defined module entities with reserved
runtime module names and canonical Logos module contracts.
They provide privileged runtime-adjacent functions, but their authority comes
from runtime policy, host wiring, or explicit grant, not from ordinary module
status.
This revision names the following privileged runtime modules:

- **Module Launcher** (`logos_module_launcher`):
  realizes module implementations for a runtime instance by launching or
  supervising processes, sandboxed processes, containers, or other
  host-specific execution forms selected by Module Launcher.
  It prepares local endpoints and returns launch descriptors to the runtime.
- **Package Manager** (`logos_package_manager`):
  owns package, catalog, install, update, removal, dependency, and package
  state operations.
- **Capability Authority** (`logos_capability_authority`):
  supplies or evaluates authorization material for runtime-control operations,
  route establishment, remote enrollment, and privileged module access.

The Module Launcher is used by the runtime instance to realize module
implementations.
It may be internal to the runtime implementation or externalized through the
canonical `logos_module_launcher` module contract.
Ordinary modules do not call the Module Launcher directly.
The shape of Module Launcher launch descriptors is outside this specification
and is defined by the Module Launcher specification.

The detailed contracts for Module Launcher, Package Manager, and Capability
Authority are defined by their respective specifications.

## 1. Module Structure

### 1.1 What a Module Is

A module is a shared library (`.so`, `.dylib`, `.dll`) or a standalone
executable that:

1. Exports a set of well-known C symbols (defined in LOGOS-MODULE-INTERFACE
   section 2.6)
2. Ships a CDDL schema file describing its interface
3. Can be loaded by the runtime and connected to other modules

### 1.2 Required Exports

LOGOS-MODULE-INTERFACE is the normative owner of the module shared-library C
ABI.
A runtime implementation MUST treat every symbol classified there as mandatory
as a required load/bind symbol for native shared-library modules.
If any mandatory symbol is missing, the runtime MUST reject the module with a
descriptive error.

In these symbol names, `<module>` is the module's flat runtime module name as
defined in section 1.3.

Symbols classified as optional or well-known extension symbols are not required
for every module.
When present, the runtime MUST bind and use them according to their defining
Runtime section.

Version metadata is not canonical schema identity;
structural schema identity is defined by LOGOS-MODULE-COMMITMENT-MODEL.

### 1.3 Module Naming

Module names are non-empty UTF-8 strings matching `[a-z][a-z0-9_]*`, with a
maximum length of 64 bytes.
Examples: `storage_module`, `delivery_module`, `search_module`.

This revision intentionally uses flat runtime module names.
The module name is an operational runtime identifier used for lookup, socket
naming, and C ABI symbol derivation.
It is not, by itself, a complete global package identity or cryptographic
schema identity.

Names beginning with `logos_` are reserved for Logos-defined runtime and
system modules.
Exact flat module names assigned by a Logos specification, package catalog, or
registry are reserved for that assigned module.

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

When the runtime already knows the module name from a manifest, command-line
argument, package metadata, or another host record, it constructs the
module-prefixed symbol names directly:

```c
void* lib = dlopen("storage_module.so", RTLD_NOW | RTLD_LOCAL);

/* Known-name load path: storage_module is already known. */
typedef const char* (*schema_fn)(void);
schema_fn get_schema = (schema_fn)dlsym(lib, "logos_storage_module_schema");

/* ... etc for the remaining mandatory ABI symbols */
```

If any required symbol is missing, the module MUST be rejected with a
descriptive error.
If the runtime does not know the module name before loading, it uses the
bootstrap strategy in section 2.2.

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

### 2.3 Static Direct Mode

On platforms where dynamic loading is unavailable or undesirable, modules MAY be
statically linked into the application or runtime binary.
This is static direct mode.

Static direct mode MUST bind the same mandatory C symbols defined by
LOGOS-MODULE-INTERFACE.
If a module exposes optional well-known callback setters, static direct mode
MUST make those setters available through the selected binding mechanism.

The binding mechanism is implementation-defined and MAY be generated by a module
kit.
Common mechanisms include generated registration tables, generated static symbol
resolvers, linker-section registration, or application startup code that passes
known function pointers to the runtime.

Static direct mode MUST NOT define a second callee-side module interface.
It is a binding mechanism for the mandatory C module interface.
Direct/static callers MAY call schema-derived per-method C functions directly
instead of routing through the generic dispatch entrypoint.

Applications using static direct mode MUST make the module bindings available
before `logos_runtime_start()`.

### 2.4 Standalone Transport Module

A module MAY run as a standalone executable that implements
LOGOS-MODULE-TRANSPORT directly rather than as a shared library loaded by a
module host process.
In this mode:

- The module binary starts, binds a Unix domain socket or TCP port, and
  listens for Logos deterministic CBOR requests per LOGOS-MODULE-TRANSPORT.
- The runtime connects to the module as a client.
- The module does not need to expose the shared-library C ABI, because it
  implements the transport endpoint itself.

This mode is useful for modules written in languages that don't produce
shared libraries (e.g. a Go module, a JVM module).

Security requirements for standalone transport modules are the same as for any
out-of-process transport module:

- the runtime MUST authenticate the peer according to the active runtime
  security policy,
- the transport connection MUST satisfy the requirements of
  LOGOS-MODULE-TRANSPORT for local or remote transport mode, and
- the execution mode MUST NOT weaken the module contract or bypass normal
  authorization and routing rules.

### 2.5 Introspection

A running module's interface can be introspected at runtime through its module
schema.
In direct mode, the runtime obtains that schema by calling
`logos_<module>_schema()`, which returns the CDDL schema as a string.
This enables:

- Runtime type checking of calls
- Auto-generation of client stubs
- UI-based module browsers
- Remote module contract discovery

Across module invocation boundaries, the schema is available through the
well-known `logos.schema` introspection bootstrap defined in
`logos_common.cddl`; see LOGOS-MODULE-INTERFACE section 5.1.
This method is provided automatically by the runtime and codegen tool.
Module authors do not declare it.

Method listings, event listings, request/response shapes, and type information
are derived from the module schema and its canonical schema model.
Runtime module listings are runtime-control state, not ordinary module
introspection state.

---

## 3. Service Registry

### 3.1 Purpose

The service registry maps module names, and where needed module instance
identity, to module providers.
Provider records include the information needed to reach or realize the target:
in-process bindings, local transport endpoints, remote transport endpoints,
standalone transport endpoints, or remote module facades.
It is the runtime's answer to the question:
"Which provider currently satisfies module contract X?"

### 3.2 Registry Implementation

The registry is a simple in-memory table maintained by the runtime:

```
module_name  ->  {
    state:       unloaded | loaded | ready | stopping | error
    provider:    <module provider address>
    instance:    <module instance identity, when applicable>
    mode:        direct | local-transport | remote-transport
    location:    <function pointers>          (direct mode)
                 <local transport endpoint>   (local transport mode)
                 <remote transport endpoint>  (remote transport mode)
                 <remote module facade>       (remote transport mode)
    schema:      <CDDL string>
    schema_namespace: <schema namespace>
    schema_commitment: <schema commitment, when known>
    version:     [major, minor]
    pid:         <process id>                 (local transport mode only,
                                               when process-backed)
}
```

### 3.3 Runtime Module Binding

A runtime registry entry is a runtime module binding.
It binds the operational module name used for loading and routing to a module
provider and to the schema contract that the runtime expects that provider to
implement.

The binding contains:

- the flat runtime module name;
- the module provider address;
- the module instance identity, when applicable;
- the execution mode and load or connection location;
- the compatibility version expectation, when known;
- the module schema text or another way to obtain it;
- the primary schema namespace for the module schema;
- the expected schema commitment, when known.

The flat runtime module name is the operational identifier defined in Section
1.3.
The schema namespace and schema commitment are structural contract identifiers
defined by LOGOS-MODULE-COMMITMENT-MODEL.
They are distinct identifiers and MUST NOT be treated as interchangeable.

A runtime MUST NOT infer schema compatibility from spelling similarity between
the runtime module name and the schema namespace.
For example, `storage_module` and `storage` are related only if the registry
entry, host record, package metadata, or another trusted configuration source
binds them to the same module contract.

When a registry entry includes an expected schema commitment, the runtime MUST
compare the loaded or connected module's declared schema commitment against the
expected commitment before treating the module as ready.
For direct modules, the runtime derives or obtains the module's schema
commitment from the schema returned by `logos_<module>_schema()`.
For local or remote transport modules, the runtime obtains the peer's declared
schema commitment from the Transport Hello `schema` field.

If the expected schema commitment is present and the loaded or connected
module declares a different schema commitment, the runtime MUST reject the
module for that registry entry and MUST NOT route ordinary calls to it.
If no expected schema commitment is present, the runtime MAY record the
module's declared schema commitment for diagnostics, later policy decisions,
or caller-visible introspection.

This specification defines the runtime binding and the checks the runtime
performs against it.
It does not define package signatures, artifact digests, catalog trust,
update policy, or the on-disk manifest schema that may supply the binding.
Those topics belong to the privileged module specs:
Package Manager, Capability Authority, and Module Launcher.
LOGOS-MODULE-SECURITY-CONSIDERATIONS records threat analysis and hardening
guidance for these bindings.

### 3.4 Module States

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
correctly and is ready to participate in the runtime contract, including
method invocation, publish hook installation, and outbound-call hook
installation.

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

### 3.5 Discovery Sources

The runtime registry can be populated from several sources:

1. **Resolved host records.** A runtime host, package manager, or deployment
   tool may hand the runtime a resolved module name, artifact path, runtime
   mode, version expectation, schema namespace expectation, schema commitment
   expectation, and dependency closure.
2. **Resolved local records.** A deployment-specific mechanism or local runtime
   setup may provide already-resolved module records for a concrete runtime
   instance.
3. **Self-describing plugin scan.** A runtime may scan one or more directories
   for `.so`/`.dylib` files and probe each using the bootstrap symbol
   (see section 3.6).
4. **Runtime registration.** For static linking or test scenarios, modules
   may be registered programmatically via `logos_runtime_register_module()`.

The on-disk package or module manifest schema is outside this specification.
It belongs to a future deployment specification or to package-manager input
contracts.
The package-manager catalog output shape also belongs outside this runtime
specification.
The runtime consumes resolved records and maintains loaded runtime state.

### 3.6 Plugin Directory Scanning

When scanning a plugin directory without trusted sidecar metadata, the runtime
probes each `.so`/`.dylib` file to extract metadata. The probe uses `dlopen`
+ `dlsym` — no framework-specific metadata embedding is required.

**Probe procedure:**

```
for each .so file in plugin_dir:
    1. handle = dlopen(path, RTLD_NOW | RTLD_LOCAL)
       if failed: skip (not a valid shared library)

    2. name_fn = dlsym(handle, "logos_module_name")
       if not found: dlclose, skip (not self-describing)

    3. name = name_fn()
       if empty or invalid: dlclose, skip

    4. Look up optional metadata symbols:
       - logos_<name>_version()  -> compatibility version metadata
       - logos_<name>_schema()   -> CDDL schema text

    5. Register in service registry:
       { name, path, version, schema, state: unloaded }

    6. dlclose(handle)  -- module is not loaded yet, only discovered
```

This self-describing scan path has no dependency on application-framework
plugin loaders or embedded JSON metadata.
Any shared library that exports `logos_module_name()` is discoverable without
knowing its module name in advance.

**The bootstrap symbol `logos_module_name()` is the sole requirement for
self-describing discovery.** Version and schema symbols are optional at
discovery time (they can be queried after loading). This keeps the bar low for
module authors: export one function, and the runtime finds you.

This does not make `logos_module_name()` mandatory for every load path.
If the runtime already knows the module name from a resolved host record,
static registration table, command-line argument, or equivalent
host/deployment metadata, it MAY construct the prefixed lifecycle symbol names
directly as described in section 2.2.

### 3.7 Module Dependencies

Module dependencies are deployment facts, not CDDL interface facts.
A package manifest or package-manager catalog may declare dependencies on
other modules.
Such fields are outside this runtime specification until a deployment
specification or package-manager CDDL defines them.

The dependency field name for new Logos manifests and catalogs should be
`dependencies`.
Implementations MAY accept `depends` as a deprecated compatibility alias in
private or transitional tooling.

When the runtime is asked to start a dependency closure, every dependency in
that resolved closure MUST be loaded and initialised before the dependent
module's `_init()` is called.
Dependency graph construction, missing-dependency detection, and cycle
detection belong to Package Manager or deployment-specific mechanisms unless a
future specification assigns those responsibilities differently.

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
- **Local transport mode:** Returns a handle wrapping a local transport
  connection to the target module provider. Calls are serialised as Logos
  deterministic CBOR per LOGOS-MODULE-TRANSPORT.
  This revision defines Unix domain sockets as the local stream binding.
- **Remote transport mode:** Returns a handle wrapping a remote transport
  connection to a remote runtime or remote module provider.
  Calls are serialised as Logos deterministic CBOR per LOGOS-MODULE-TRANSPORT.

The caller does not know or care which mode is active. The handle abstraction
hides the transport.
Handle-based typed client helpers are the portable caller-side C API.
Such helpers take a `logos_module_handle_t*` as their first argument and route
calls through the handle.

The purpose of the handle abstraction is precisely to preserve the execution-
boundary equivalence stated above: the runtime may switch routing mode, but
the module contract observed by the caller remains the same.

For a module method such as `storage.exists`, a generated handle-based client
helper may have this shape:

```c
logos_result_t logos_storage_exists(
    logos_module_handle_t* h,
    const char*            cid,
    bool*                  out_exists
);
```

This caller-side helper is distinct from the callee-side Logos module C
function defined by LOGOS-MODULE-INTERFACE.

A runtime MAY also expose a generic dynamic call API for callers that discover
schemas at runtime or do not have generated typed client helpers:

```c
logos_result_t logos_runtime_call(
    logos_module_handle_t* h,
    const char*            method,
    const uint8_t*         params_cbor,
    size_t                 params_len,
    uint8_t**              response_cbor,
    size_t*                response_len
);
```

The generic call API carries deterministic-CBOR method payloads using the same
request, response, and error shapes as LOGOS-MODULE-TRANSPORT.

A singleton direct-call convenience mode MAY additionally generate no-handle
helpers as described in section 5.2.1.

### 4.2 Routing Selection

The runtime maintains routing-selection state that maps caller context and
callee module contract expectations to candidate module providers and
invocation modes:

| Caller | Callee | Candidate mode | Notes |
|--------|--------|----------------|-------|
| (any) | storage_module | local-transport | Default: separate process |
| presenter | storage_module | direct | Mobile: same process |
| (any) | logos_capability_authority | direct | Privileged runtime module selected by local policy |

Routing-selection state is an input to route establishment.
It is not itself a route record, authorization grant, or data-plane descriptor.
The runtime MAY update routing-selection state at runtime, for example when a
local provider becomes available or a remote provider becomes unreachable.
Such updates MUST NOT silently move an existing caller-side binding to a
different provider unless runtime authority policy allows reselection and the
runtime creates a new route identity or explicit renewal relation visible
through Runtime Control observation.

### 4.2.1 Routing View For Local Transport Module Hosts

When a module runs in **local transport mode**, the module host process is
still part of the same logical runtime routing domain.
Therefore, if that host exposes
`logos_<module>_set_call_module()`, it MUST be able to resolve outbound calls
using a routing view that is consistent with the runtime's current registry,
routing-selection state, and route-establishment semantics.

This requirement is semantic, not architectural. The spec does **not** require
a specific mechanism. A conforming implementation MAY satisfy it by, for
example:

- giving the module host a local copy or snapshot of the relevant routing data
- providing the module host a runtime-managed lookup/control channel
- embedding the host in a larger runtime process that already has the relevant
  routing-selection state in memory

What matters normatively is:

- a local-transport-hosted module MUST NOT need to invent its own independent
  routing policy
- outbound calls from a local-transport-hosted module MUST be resolved
  according to the same runtime registry, routing-selection, and
  route-establishment rules that would apply if the caller were in-process
- if the implementation allows routing changes at runtime, it MUST define a
  consistency model such that hosts do not silently route according to stale or
  contradictory information

The consistency mechanism itself is implementation-defined. The interoperable
requirement is the observable behavior at the module boundary, not the control
plane used to achieve it.

### 4.3 Capability Validation

Before returning a caller-side handle, helper binding, or invocation descriptor,
the runtime MUST verify that the caller is authorized to access the selected
provider according to runtime authority policy.
For providers owned by another runtime instance, the runtime that owns the
target provider is the enforcement point for the provider access decision.
The target runtime MAY evaluate the decision locally or consult its configured
Capability Authority provider.

This specification does not define the capability token format, capability
issuance flow, or policy language for module-to-module access.
When route authority policy is externalized through Capability Authority, those
formats and decisions are defined by the Capability Authority contract.
The runtime MUST treat authorization as an explicit route-establishment
decision and MUST NOT infer permission merely from module names, schema names,
provider ids, runtime ids, or successful transport connection.

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

In **local transport mode**, subscriptions are translated to Subscribe messages
(message kind 3) per LOGOS-MODULE-TRANSPORT.
Incoming Event messages (message kind 5) are decoded and delivered to the
handler.

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

In the default desktop process model, each shared-library module runs in its
own OS process.
The runtime instance realizes the module through the Module Launcher path,
which starts a **module host** process for the module implementation:

```
logos_host --module <path-to-module.so> --socket <socket-path>
```

The module host:

1. `dlopen`s the module shared library
2. Calls lifecycle `_init()` (this revision passes no typed configuration)
3. Binds the Unix domain socket
4. Enters an event loop, reading CBOR requests from the socket, creating an
   opaque `logos_call_context_t` for each invocation, invoking the module's
   generic dispatch entrypoint, and writing responses

In this process-backed local transport mode, the runtime communicates with the
module host over LOGOS-MODULE-TRANSPORT, while the module host executes the
module through the C ABI symbols defined by LOGOS-MODULE-INTERFACE.
`dlopen`/`dlsym` are used inside the module host process, not across the socket
connection.

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

### 5.2.1 Singleton Direct-Call Convenience Mode

A runtime implementation MAY define a singleton direct-call convenience mode
for direct mode.
This convenience mode MAY be used with dynamic direct mode or static direct
mode.

In this convenience mode, each module name has at most one live module instance
inside the runtime instance.
Generated client helpers MAY omit `logos_module_handle_t*` and route calls
through the runtime's default binding for that module name.

This convenience mode is intended for mobile, embedded, and simple packaged
applications where the module set is known at build or packaging time.

This convenience mode MUST NOT change the module contract:
method names, request and response shapes, event names, error codes, lifecycle
rules, and authorization semantics remain the same as in the handle-based
runtime model.

A singleton direct-call convenience mode MUST define:

- how the default runtime instance is selected;
- how module initialization order is determined;
- how duplicate module names are rejected;
- how generated no-handle helpers fail when the default module binding is not
  ready;
- whether outbound calls and event publishing use the same runtime callbacks as
  ordinary direct mode.

This is a convenience mode.
Portable code that needs multiple module instances, multiple runtimes in one
process, runtime-selected local or remote transport routing, or explicit test
isolation SHOULD use handle-based client helpers.

### 5.3 Hybrid

Some modules may run in-process (small utility modules or selected privileged
runtime modules)
while others run in separate processes (storage, heavy computation).
Routing-selection state (section 4.2) selects candidate providers and invocation
modes per module.

---

## 6. Threading and Concurrency

### 6.1 Module Threading Model

Modules MUST be safe to call from multiple threads. The runtime MAY dispatch
requests to a module from different threads concurrently (e.g. when multiple
callers invoke the same module simultaneously).

Modules that cannot handle concurrent calls MUST implement their own internal
serialisation (e.g. a mutex). The runtime does not provide call serialisation.

### 6.2 Module Host Threading

In local transport mode, the module host process runs an event loop that:

- Accepts connections from multiple callers
- Reads requests from all connections (via `poll`/`epoll`/`kqueue`)
- Supplies a `logos_call_context_t*` and invokes the module's generic dispatch
  entrypoint for each request

The runtime MUST NOT mark a local-transport-hosted module as `ready` merely
because a local endpoint exists.
The host is ready only after the runtime can connect to that socket and
complete the LOGOS-MODULE-TRANSPORT Hello handshake for the hosted module.
If readiness is not reached before the startup timeout, the runtime MUST
terminate the host process, remove any stale socket file it owns, and MUST NOT
treat the module provider or any dependent route as ready.

The module host SHOULD use a thread pool for dispatching requests, so that
a slow method does not block other callers. The default pool size is
implementation-defined (recommended: number of CPU cores).

### 6.3 Event Delivery Threading

Event handlers (registered via `logos_runtime_subscribe`) are called on an
unspecified thread. Handlers MUST be thread-safe. Handlers MUST NOT block
for extended periods (they run on the runtime's event delivery thread).

For host applications with a dedicated UI thread, the runtime MAY provide a
mechanism to marshal event delivery to that thread.
The integration mechanism is framework-specific and not part of this spec.

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

The runtime event loop MAY integrate with an event loop owned by the host
application.
The integration mechanism is framework-specific and not part of this spec.
When no host event loop is provided, the runtime provides its own event loop.

### 7.2 Module Event Loop

Module host processes run their own event loop:

In the pseudocode below, `invoke_module_dispatch` is illustrative host behavior,
not a required exported symbol.
It means that the host decodes the transport request, identifies the requested
schema method, creates or reuses the call context for the invocation, calls the
module's generic dispatch entrypoint, and encodes the transport response.

```
while running:
    msg = read_framed_cbor(socket)
    response = invoke_module_dispatch(msg)
    write_framed_cbor(socket, response)
```

### 7.3 Module Event Publishing

A module publishes events by calling a runtime-provided function:

```c
typedef void (*logos_publish_fn)(
    void*          user_data,
    const char*    event_name,
    const uint8_t* cbor_data,
    size_t         cbor_data_len
);
```

`event_name` MUST be the exact schema event identifier from the module's
CDDL, for example `storage.started_event` or
`storage.upload_progress_event`.

The runtime delivers the event to all subscribers (local or remote). In local
transport mode, the module host translates `logos_publish_fn` calls into Event
messages (message kind 5) on all connections with matching subscriptions.
If multiple caller connections have matching subscriptions, each connection
MUST receive an Event message for its own matching subscription IDs.

This publish path is for asynchronous one-way notifications with
schema-defined event payloads.
Modules use it for progress, completion, state-change, and similar signals.
It is not a general outbound method mechanism and does not replace normal
request/response dispatch.
Publishing an event does not create a response obligation for subscribers, and
modules MUST NOT model request/reply flows through events.

### 7.4 How Modules Receive the Publish Function

The publish function is provided via a **well-known symbol** that the
runtime calls after `_init()` succeeds:

The module stores the function pointer and user data internally.
If the module does not publish any events, it MAY omit this symbol — the
runtime MUST NOT fail if the symbol is absent.

```c
/* Exported by the module. Called by runtime/host after _init() returns OK. */
void logos_<module>_set_publish(logos_publish_fn fn, void* user_data);
```

`user_data` is opaque, process-local callback state supplied by the runtime or
module host.
The module MUST pass the value back unchanged when it calls `fn`.
The module MUST NOT dereference it, compare it for semantic identity, serialize
it, persist it, expose it in schemas, or send it across a transport or network
boundary.
It is meaningful only inside the process that installed the callback.

For compatibility with older generated modules that may still publish short
event names such as `started`, a runtime MAY normalize those legacy names
to the canonical schema event name before putting them on the wire. New
modules and code generators MUST use the canonical schema event name
directly.

For static direct mode, the selected binding mechanism makes the publish setter
available to the runtime before `logos_runtime_start()` (see section 2.3).
The runtime calls the publish setter after `_init()` succeeds and before the
module is considered ready.

Modules MUST NOT rely on the publish function being installed during `_init()`.

**Lifetime:** The publish function and its `user_data` are valid from the
time they are set until `_destroy()` returns or until the hook is replaced.
Modules MUST NOT call a previous hook after replacement and MUST NOT call any
hook after `_destroy()`.

**Thread safety:** The publish function is thread-safe. Modules MAY call
it from any thread.

### 7.5 Outbound Calls (Calling Other Modules)

A module that needs to call another module can do so through a runtime-
provided callback, without linking the SDK or implementing the transport
protocol's client side:

```c
/* Provided by the runtime to the module after _init() */
typedef void (*logos_free_response_fn)(void* user_data, void* ptr);

typedef logos_result_t (*logos_call_module_fn)(
    void*           user_data,
    const char*     target_module,
    const uint8_t*  request_cbor,    /* CBOR: {"method": tstr, "params": {...}} */
    size_t          request_len,
    uint8_t**       response_cbor,   /* runtime/callback allocates */
    size_t*         response_len
);

/* Exported by the module. Called by runtime/host after _init() returns OK. */
void logos_<module>_set_call_module(
    logos_call_module_fn   fn,
    logos_free_response_fn free_response,
    void*                  user_data
);
```

The module encodes a CBOR request map (`{method, params}`) for the target
module, calls the function, and receives a CBOR response.
The callback represents the runtime-owned outbound-call service for the
module's current placement.
It hides whether the target is in-process, hosted by another local process, or
remote.

This specification requires that outbound calls follow the runtime routing
model from sections 4.2 and 4.2.1.
It does not require every call to pass through a single central broker process.
For in-process modules, the callback may dispatch directly through cached
function pointers, generated stubs, or equivalent local dispatch state.
For local-transport-hosted modules, the callback may be installed by the
per-module host process and may translate the outbound call into transport
requests using a routing view supplied by, synchronized with, or otherwise
authorized by the runtime.
For remote targets, the callback may route through the appropriate remote
runtime binding.

The callback is runtime-owned in authority and semantics even when the concrete
function pointer is installed by a per-module host process.
A module MUST treat the callback as its only portable outbound-call mechanism
and MUST NOT infer topology from the callback implementation.

If `logos_call_module_fn` returns a non-null `response_cbor`, the module MUST
free it with the paired `logos_free_response_fn`.
This deallocator is owned by the runtime or module host that installed the
callback.
It is distinct from the callee module's `logos_<module>_free()` function.

If the module does not call other modules, it MAY omit this symbol. The
runtime MUST NOT fail if the symbol is absent.

`user_data` follows the same process-local callback-state rules as
`logos_publish_fn`.
For Level 1 transport placement, it remains inside the module host process:
the host callback translates the outbound call into transport requests and
responses, and only CBOR envelopes and payloads cross the process or network
boundary.
For Level 2 and Level 3 local placement, it similarly remains local glue state
for the runtime or host that installed the callback.

**Lifetime:** Same as `logos_publish_fn`.

**Thread safety:** The function is thread-safe. Modules MAY call it from
any thread. Calls are synchronous — the function blocks until the target
module responds.

**Error handling:** If the target module is not found, returns
`LOGOS_ERR_MODULE` with `*response_cbor = NULL`. If the target returns an
error, the error is encoded in `response_cbor` as an error-payload map
(`{code, message, ?detail}`).

---

## 8. Runtime Input Records

The runtime does not define a configuration file format.

A runtime instance consumes resolved module input records supplied by a runtime
host, Package Manager, deployment-specific mechanism, static registration API,
or test harness.
The producer and storage format of those records are outside this specification.

Runtime input records are non-security records.
They do not grant authority, prove package trust, approve permissions, or define
sandbox strength.

A resolved module record supplies the information needed to create or update a
runtime registry entry:

- the flat runtime module name;
- the execution mode;
- the provider id or module instance id, when assigned by the runtime host;
- a dynamic artifact, static binding, local transport endpoint, remote target,
  or launch descriptor;
- compatibility version expectations, when known;
- schema namespace expectation, when known;
- schema commitment expectation, when known;
- runtime-local options needed by the selected implementation.

```cddl
logos_runtime_module_input = {
  module: tstr .size (1..64),
  mode: "direct" / "local-transport" / "remote-transport",
  ? provider: tstr .size (1..128),
  ? instance: tstr .size (1..128),
  ? artifact: logos_runtime_artifact_input,
  ? static: logos_runtime_static_binding,
  ? endpoint: logos_runtime_transport_endpoint,
  ? remote: logos.runtime_control.remote_provider_target,
  ? launch: logos_launch_descriptor,
  ? schema_namespace: tstr .size (1..128),
  ? schema: logos.runtime_control.schema_commitment,
  ? version: [uint, uint],
  ? options: {* tstr => any},
  ? extensions: {* tstr => any},
}

logos_runtime_artifact_input = {
  ? id: tstr,
  ? local_path: tstr,
  ? store_path: tstr,
  ? executable: bool,
  ? media_type: tstr,
}

logos_runtime_static_binding = {
  binding: tstr,
  ? symbol_prefix: tstr,
  ? table: tstr,
  ? extensions: {* tstr => any},
}

logos_runtime_transport_endpoint = {
  kind: tstr .size (1..64),
  ? descriptor: bstr,
  ? extensions: {* tstr => any},
}
```

For `direct` mode, a module input MUST provide either `artifact` for dynamic
direct loading or `static` for static direct binding.

For `local-transport` mode, a module input MUST provide `launch`, `endpoint`,
or another deployment-defined local transport binding.
When `launch` is present, it is the Launcher-owned `logos_launch_descriptor`
defined by LOGOS-MODULE-LAUNCHER.
Runtime passes the descriptor to Module Launcher when it needs to realize the
module implementation.
Runtime MUST NOT reinterpret launcher-specific fields as authority or package
trust.

For `remote-transport` mode, a module input MUST provide `remote` or `endpoint`
sufficient to construct a remote-module facade or remote invocation path.

The runtime MUST validate resolved module records before routing calls through
them.
If a record includes a schema commitment expectation, the runtime MUST apply
the schema-commitment checks defined in Section 3.3 before marking the module
ready.
The runtime MUST reject or quarantine malformed runtime input records rather
than creating partially trusted registry entries from them.

This specification does not define package catalogs, install roots,
dependency-graph queries, capability decisions, action prompts, or persistent
configuration storage.
Those belong to Package Manager, Capability Authority, Module Launcher,
runtime-host, or deployment specifications.
LOGOS-MODULE-SECURITY-CONSIDERATIONS records related threat analysis and
hardening guidance.

### 8.1 Module Initialization Inputs

This revision defines the lifecycle initializer as `_init(void)`.
It does not define a typed runtime-configuration handoff through the lifecycle
ABI.

If a module needs configuration, the selected deployment-specific or
host-specific mechanism must arrange that configuration outside the lifecycle
ABI, for example through environment, local files, provider-specific startup
data, or module-specific methods.

Runtime input `options` are runtime-local options unless a deployment profile
explicitly defines how a module observes them.
Runtime host directories, profile selection, concrete launcher backends, and
privileged-module wiring are deployment or security-profile inputs, not portable
Runtime input fields in this revision.

---

## 9. Runtime-Control Interface

The runtime owns module lifecycle machinery.
This specification also defines Runtime Control, a privileged Logos module
surface exposed by the runtime instance.
Runtime Control exposes runtime-owned lifecycle and observation operations
through the same CDDL-defined contract model as other Logos module interfaces.
Runtime hosts may consume Runtime Control, subject to active runtime policy.

A runtime host is the external authority-bearing environment that creates,
embeds, supervises, configures, or otherwise controls a runtime instance.
A host shell is a product or application shell that provides user-facing
runtime-backed capabilities.
A standalone application MAY also be a runtime host for its own runtime
instance.
The runtime host is not required to be a Logos module.
It MAY expose Logos module interfaces, but its runtime-control authority comes
from the local host/runtime relationship or an explicitly granted policy, not
from ordinary module status.

The runtime-control surface operates on runtime-known module records.
It does not define package catalogs, install roots, dependency graph
resolution, capability decisions, concrete module launch mechanics, or UI
state.
Those remain Package Manager, Capability Authority, Module Launcher,
deployment-specific, or runtime-host concerns.

Runtime-control methods are privileged operations.
A runtime MUST authorize a caller according to the active runtime policy
before executing any runtime-control method.
A runtime MUST NOT expose this surface to ordinary modules or remote peers by
default.

Runtime authority is configuration and policy, enforced by the runtime
instance.
A runtime instance MUST have an authority policy for runtime-control
operations, route establishment, privileged runtime-module access, provider
visibility, lifecycle control, and remote-runtime enrollment.
The authority policy may be internal to the runtime for local trusted
deployments or externalized through the privileged
`logos_capability_authority` module.
Runtime input records, static registration, deployment configuration, and
embedded runtime-host wiring may bootstrap the runtime host and identify the
Capability Authority provider.
They do not bypass runtime enforcement.
If no authority policy allows an operation, the runtime MUST deny the
operation.

Runtime-host authority is a local relationship established when the runtime is
created, embedded, or configured.
A host shell has runtime-host authority only when it is also the runtime host or
when runtime authority policy delegates that authority to it.
Privileged runtime modules such as Module Launcher, Package Manager, and
Capability Authority have only the privileged operations granted to them by
runtime authority policy.
Ordinary module status never grants runtime-control authority, privileged
runtime-module access, route authority, or provider visibility by itself.

For authority-policy evaluation, the runtime MUST be able to classify the
caller using the information available at the enforcement boundary.
This revision uses the following caller classes:

- runtime host;
- host shell with delegated runtime-host authority;
- ordinary module;
- privileged runtime module;
- local runtime acting as a client of another runtime;
- remote runtime-control client;
- remote ordinary module caller.

Caller class is an input to authority policy.
It is not authority by itself.

Transport authentication, schema compatibility, runtime instance ids, module
names, provider ids, package identity, and successful connection establishment
are authority-policy inputs.
They are not authority by themselves.

LOGOS-MODULE-RUNTIME does not define capability token formats, token issuance
flows, policy languages, or security trust-store formats.
A runtime consumes authority decisions from its authority policy.
When authority policy is externalized through Capability Authority, token,
grant, evidence, and decision formats are defined by the Capability Authority
contract.
The runtime treats those values as authority inputs and decision outputs and
enforces the resulting decisions at the runtime-control, route,
lifecycle-control, provider-visibility, privileged-module, and remote-facade
boundaries defined here.
Remote runtime-control access requires authority accepted by the runtime that
exposes the Runtime Control endpoint.

The following operations require an allow decision from runtime authority
policy:

- invoking any Runtime Control method;
- observing Runtime Control state that is not visible to ordinary modules;
- starting, stopping, loading, unloading, or otherwise controlling module
  lifecycle;
- using Module Launcher, Package Manager, Capability Authority, or another
  privileged runtime module;
- establishing, renewing, reselecting, or revoking a route;
- exposing a provider record or route record to a caller;
- enrolling, refreshing, or using a remote runtime or remote-module facade.

When authority policy denies an operation, the runtime MUST NOT perform the
operation and MUST report an authorization failure through the method,
transport, or runtime API error channel used for the attempted operation.
For Runtime Control methods, denial is reported through the ordinary Logos
method error channel.
For Transport Hello authorization failure, denial is reported as
`NOT_AUTHORISED` and the connection is closed.

The runtime MUST retain enough authority-decision material to explain
allow/deny enforcement through Runtime Control observation or implementation
audit logs.
That material SHOULD include the caller identity known to the runtime, the
operation class, target provider or route when present, authority decision
reference when present, and audit reference when present.

Remote runtime enrollment is an authority-policy decision that makes a remote
runtime eligible for remote runtime-control access, remote-module facade
creation, or remote route establishment.
Enrollment does not by itself authorize any concrete runtime-control method,
module lifecycle operation, provider visibility, or ordinary module route.
Each such operation still requires its own allow decision from runtime authority
policy.
If a remote runtime is not enrolled or otherwise accepted by authority policy,
the local runtime MUST NOT use it for remote-module facades or remote routes.

### 9.1 Runtime-Control Module Contract

The runtime-control interface is a Logos-defined system module surface.
Its flat runtime module name is `logos_runtime_control`.
Its schema namespace is `logos.runtime_control`.
Because both names are Logos-defined, they are allowed uses of the reserved
`logos_` and `logos.` namespaces.

This section defines the following runtime-control addressing objects:

| Object | Purpose | Format | Scope |
|--------|---------|--------|-------|
| `module_name` | Flat operational runtime module name used for loading and routing. | `tstr .size (1..64)` | Runtime module namespace. |
| `runtime_instance_id` | Opaque identity for a concrete runtime instance. | `tstr .size (1..128)` | Addressing scope that uses the runtime instance. |
| `runtime_address` | Locator for opening a transport connection to a runtime-control-capable endpoint. | Transport-specific record. | Network, host, namespace, or deployment profile. |
| `runtime_endpoint` | Optional pairing of runtime identity and runtime locator. | `{ ? runtime_instance_id, address }` | Runtime-control records that need both identity context and reachability. |
| `module_provider_id` | Opaque identity for a runtime-known module provider. | `tstr .size (1..128)` | Runtime instance that owns the provider record. |
| `module_provider_address` | Address of a provider record inside a runtime instance. | `{ ? runtime_instance_id, provider }` | Runtime-control records that refer to a provider. |
| `module_instance_id` | Opaque identity for a live module instance. | `tstr .size (1..128)` | Runtime or provider scope that owns the live instance. |
| `schema_namespace` | Structural schema namespace for a module contract. | `tstr .size (1..128)` | Schema model, not runtime addressing. |
| `schema_commitment` | Commitment to the structural schema contract. | Commitment record. | Hash and commitment profile scope. |

```cddl
; -- metadata --
_module = "logos_runtime_control"
_version = [1, 0]

logos.runtime_control.module_name = tstr .size (1..64)
logos.runtime_control.runtime_instance_id = tstr .size (1..128)
logos.runtime_control.module_provider_id = tstr .size (1..128)
logos.runtime_control.module_instance_id = tstr .size (1..128)
logos.runtime_control.route_id = tstr .size (1..128)
logos.runtime_control.schema_namespace = tstr .size (1..128)
logos.runtime_control.reason = tstr .size (0..512)
logos.runtime_control.address_profile = tstr .size (1..128)
logos.runtime_control.descriptor_kind = tstr .size (1..64)
logos.runtime_control.authority_ref = tstr .size (1..128)
logos.runtime_control.audit_ref = tstr .size (1..128)
logos.runtime_control.failure_code = tstr .size (1..64)
logos.runtime_control.host_name = tstr .size (1..255)
logos.runtime_control.port = uint .le 65535
logos.runtime_control.path = tstr .size (1..4096)
logos.runtime_control.server_name = tstr .size (1..255)
logos.runtime_control.alpn = tstr .size (1..255)

logos.runtime_control.state =
    "unloaded" /
    "loaded" /
    "ready" /
    "stopping" /
    "error"

logos.runtime_control.mode =
    "direct" /
    "local-transport" /
    "remote-transport"

logos.runtime_control.route_state =
    "establishing" /
    "ready" /
    "draining" /
    "revoked" /
    "failed" /
    "closed"

logos.runtime_control.unix_stream_runtime_address = {
    transport: "unix-stream",
    path: logos.runtime_control.path,
    ? profile: logos.runtime_control.address_profile,
}

logos.runtime_control.tcp_runtime_address = {
    transport: "tcp",
    host: logos.runtime_control.host_name,
    port: logos.runtime_control.port,
    ? profile: logos.runtime_control.address_profile,
}

logos.runtime_control.tls_tcp_runtime_address = {
    transport: "tls-tcp",
    host: logos.runtime_control.host_name,
    port: logos.runtime_control.port,
    ? server_name: logos.runtime_control.server_name,
    ? profile: logos.runtime_control.address_profile,
}

logos.runtime_control.quic_runtime_address = {
    transport: "quic",
    host: logos.runtime_control.host_name,
    port: logos.runtime_control.port,
    ? server_name: logos.runtime_control.server_name,
    ? alpn: logos.runtime_control.alpn,
    ? profile: logos.runtime_control.address_profile,
}

logos.runtime_control.runtime_address =
    logos.runtime_control.unix_stream_runtime_address /
    logos.runtime_control.tcp_runtime_address /
    logos.runtime_control.tls_tcp_runtime_address /
    logos.runtime_control.quic_runtime_address

logos.runtime_control.runtime_endpoint = {
    ? runtime_instance_id: logos.runtime_control.runtime_instance_id,
    address: logos.runtime_control.runtime_address,
}

logos.runtime_control.remote_provider_target = {
    runtime: logos.runtime_control.runtime_endpoint,
    ? provider: logos.runtime_control.module_provider_id,
    ? module: logos.runtime_control.module_name,
}

logos.runtime_control.module_provider_address = {
    ? runtime_instance_id: logos.runtime_control.runtime_instance_id,
    provider: logos.runtime_control.module_provider_id,
}

logos.runtime_control.schema_commitment = {
    commitment_model: tstr,
    schema_root: bstr,
    hash_profile: tstr,
    hash_suite: tstr,
}

logos.runtime_control.module_record = {
    module: logos.runtime_control.module_name,
    ? provider: logos.runtime_control.module_provider_address,
    ? remote: logos.runtime_control.remote_provider_target,
    ? instance: logos.runtime_control.module_instance_id,
    state: logos.runtime_control.state,
    mode: logos.runtime_control.mode,
    ? schema_namespace: logos.runtime_control.schema_namespace,
    ? schema: logos.runtime_control.schema_commitment,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.invocation_descriptor = {
    kind: logos.runtime_control.mode,
    descriptor_kind: logos.runtime_control.descriptor_kind,
    ? descriptor: bstr,
}

logos.runtime_control.route_authority = {
    ? authority_provider: logos.runtime_control.module_provider_address,
    ? authority_ref: logos.runtime_control.authority_ref,
    ? expires_at: uint64,
    ? audit_ref: logos.runtime_control.audit_ref,
}

logos.runtime_control.route_failure = {
    code: logos.runtime_control.failure_code,
    ? message: logos.runtime_control.reason,
}

logos.runtime_control.route_record = {
    route: logos.runtime_control.route_id,
    caller_runtime: logos.runtime_control.runtime_instance_id,
    target_provider: logos.runtime_control.module_provider_address,
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
    ? schema_namespace: logos.runtime_control.schema_namespace,
    ? schema: logos.runtime_control.schema_commitment,
    state: logos.runtime_control.route_state,
    invocation: logos.runtime_control.invocation_descriptor,
    ? authority: logos.runtime_control.route_authority,
    ? failure: logos.runtime_control.route_failure,
}

logos.runtime_control.list_modules_request = {}

logos.runtime_control.list_modules_response = {
    modules: [* logos.runtime_control.module_record],
}

logos.runtime_control.list_routes_request = {
    ? module: logos.runtime_control.module_name,
    ? provider: logos.runtime_control.module_provider_address,
}

logos.runtime_control.list_routes_response = {
    routes: [* logos.runtime_control.route_record],
}

logos.runtime_control.revoke_route_request = {
    route: logos.runtime_control.route_id,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.revoke_route_response = {
    route: logos.runtime_control.route_id,
    state: logos.runtime_control.route_state,
}

logos.runtime_control.start_module_request = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
}

logos.runtime_control.start_module_response = {
    module: logos.runtime_control.module_name,
    instance: logos.runtime_control.module_instance_id,
    state: logos.runtime_control.state,
}

logos.runtime_control.stop_module_request = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
}

logos.runtime_control.stop_module_response = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
    state: logos.runtime_control.state,
}

logos.runtime_control.get_readiness_request = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
}

logos.runtime_control.get_readiness_response = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
    state: logos.runtime_control.state,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.module_state_changed_event = {
    module: logos.runtime_control.module_name,
    ? instance: logos.runtime_control.module_instance_id,
    old_state: logos.runtime_control.state,
    new_state: logos.runtime_control.state,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.route_state_changed_event = {
    route: logos.runtime_control.route_id,
    old_state: logos.runtime_control.route_state,
    new_state: logos.runtime_control.route_state,
    ? module: logos.runtime_control.module_name,
    ? provider: logos.runtime_control.module_provider_address,
    ? reason: logos.runtime_control.reason,
}
```

Runtime-control methods use the ordinary Logos method error channel defined by
LOGOS-MODULE-INTERFACE.
Method-specific failure conditions are described with each method.

`runtime_instance_id` identifies the runtime instance exposing the
runtime-control interface.
It is distinct from `module_instance_id`, which identifies a live module
instance managed by that runtime.

`module_instance_id` identifies a live module instance owned by a runtime
instance.
It is opaque and scoped to the runtime instance that owns the module lifecycle
record.
It is lifecycle identity, not module contract identity, provider identity,
package identity, schema identity, authorization identity, route identity, or
transport reachability.

Multiple live instances of the same flat runtime module name MAY exist in one
runtime instance.
When a runtime-control record carries both `module` and `instance`, the
`instance` field disambiguates the lifecycle target for that module name.
If a provider is not bound to a local live module instance, the provider record
MAY omit `instance`.
This is expected for local remote-module facade providers whose backing live
module instance is owned by a remote runtime.

A runtime instance id is an opaque string chosen or accepted by the runtime
host for a concrete runtime instance.
It is unique within the addressing scope that uses it.
Specifications MUST NOT infer trust, authorization, package identity, schema
compatibility, or network reachability from the runtime instance id alone.

A runtime instance id MAY be host-assigned or runtime-generated.
If the runtime generates the id, the runtime host MUST accept it before the id
is used in runtime-control, addressing, or route records owned by that host.

`runtime_address` describes how to open a transport connection to a
runtime-control-capable runtime endpoint.
It is a locator, not the runtime identity, trust policy, schema identity,
authorization grant, package identity, module identity, or route state.

This revision defines four runtime address transports:

- `unix-stream`, a local stream endpoint addressed by filesystem path;
- `tcp`, a cleartext stream endpoint addressed by host and port;
- `tls-tcp`, a TLS-protected stream endpoint addressed by host and port;
- `quic`, a QUIC endpoint addressed by host and port.

`unix-stream` addresses MUST contain `path` and MUST NOT contain `host`,
`port`, `server_name`, or `alpn`.
`tcp` addresses MUST contain `host` and `port`, and MUST NOT contain `path`,
`server_name`, or `alpn`.
`tls-tcp` addresses MUST contain `host` and `port`, MUST NOT contain `path`,
and MAY contain `server_name`.
`quic` addresses MUST contain `host` and `port`, MUST NOT contain `path`, and
MAY contain `server_name` and `alpn`.
If a QUIC deployment profile requires a specific ALPN value, the address MUST
carry that value or the profile MUST define how the value is supplied.

The cleartext `tcp` transport is a raw-draft development and conformance
scaffolding transport.
It MUST NOT be used for production remote runtime-control access.
Unless later review identifies a production use case, `tcp` is expected to be
removed or made non-normative before this specification advances beyond raw
draft maturity.

For `tls-tcp` and `quic`, transport authentication establishes transport trust
only.
Transport trust does not by itself prove runtime authorization, module
authorization, package identity, schema compatibility, or route authority.
Transport authentication material MAY be used as input to runtime policy,
capability policy, enrollment policy, or route policy.
It MUST NOT authorize runtime-control operations or ordinary module routes
unless an explicit Logos deployment profile defines that binding.

Logos Transport messages over QUIC use bidirectional QUIC streams in this
revision.
QUIC datagrams are out of scope unless a later route or data-plane profile
defines them.
QUIC connection migration MUST NOT change the runtime identity or authorization
state inferred by Logos.
Runtime policy decides whether migration is allowed for a deployment.

`runtime_endpoint` pairs an optional `runtime_instance_id` with a
`runtime_address`.
The runtime instance id remains opaque and does not prove that the reached
runtime is trustworthy.
A peer that connects to a `runtime_address` MUST still validate Transport
Hello, schema commitment, runtime-control authorization policy, and any
deployment trust policy before treating the endpoint as usable.
A runtime MAY publish multiple runtime addresses for the same runtime instance,
because reachability can differ by host, namespace, network, or profile.

A remote runtime-control surface is exposed as the `logos_runtime_control`
Logos endpoint over LOGOS-MODULE-TRANSPORT.
The Transport Hello `module` field identifies that endpoint as
`logos_runtime_control`.
The Transport Hello `schema` field carries the structural schema identity of
the Runtime Control contract for that endpoint.
If a caller requires a specific Runtime Control schema, it uses the Transport
Hello `expect_schema` field.
This specification does not define a separate remote-runtime identity
handshake.
Runtime identity remains the opaque `runtime_instance_id` carried in Runtime
Control records and interpreted under deployment or enrollment policy.
A successful Transport Hello for `logos_runtime_control` proves only that the
peer presented a compatible Runtime Control endpoint schema under the selected
transport policy.
It does not by itself authorize runtime-control operations or ordinary module
routes.

`module_provider_id` identifies a runtime-known module provider inside a
runtime instance.
It is opaque and scoped to the runtime instance that owns the provider record.
Specifications MUST NOT infer trust, authorization, schema compatibility,
package identity, network reachability, transport endpoint, route authority, or
module lifecycle state from the provider id alone.

`module_provider_address` identifies a provider record inside a runtime
instance.
It is the stable address form for referring to that provider from
runtime-control records.

If `runtime_instance_id` is present in a `module_provider_address`, it names
the runtime instance whose registry owns the provider id.
If it is absent, the provider id is interpreted in the local runtime-control
context that carried the record.
The runtime instance id remains opaque and does not prove trust or authority.

A module provider address MAY refer to a provider backed by a local module
instance, a standalone transport endpoint, or a remote module facade.
For a remote module facade, the provider address names the local facade
provider owned by the local runtime.
It does not by itself name the remote runtime's live module instance.
When a provider record represents a remote module facade, `remote` records the
remote runtime endpoint and remote target known to the local runtime.
Within `remote_provider_target`, `provider` is scoped to the remote runtime
identified by `runtime`.
It is not a local provider id.
The remote target SHOULD include `provider` when the remote runtime has exposed
a provider id for the target.
It MAY include `module` when the local runtime targets the remote module
contract before or instead of a concrete remote provider id.
This metadata is descriptive targeting material for the facade.
It is not a separate local provider address and does not transfer lifecycle
ownership from the remote runtime.

The flat runtime module name, module instance id, execution mode, schema
namespace, schema commitment, transport endpoint, and remote-facade targeting
metadata are descriptive facts about provider records or routes.
They are intentionally not part of `module_provider_address`.

When a `module_record` includes `provider`, the field identifies the
runtime-known provider that currently satisfies or is expected to satisfy the
record's module contract.
The `module` field remains the flat operational runtime module name.
The `provider` field is not a substitute for the module name, and the module
name is not a provider address.

Module contract identity is represented by existing contract fields on runtime
records, not by a separate address object.
The flat runtime `module` name is the operational name used for loading and
routing.
`schema_namespace`, `schema`, and compatibility version metadata describe the
module contract that the runtime expects a provider or module instance to
implement.
Those fields are not runtime addresses, provider addresses, module instance
identities, route identities, authorization grants, or transport locators.

Runtime addresses, module provider addresses, and module instance ids do not
prove module contract compatibility.
A runtime that connects to or selects a provider MUST validate the expected
module contract using the relevant schema namespace, schema commitment,
compatibility version expectation, and Transport Hello schema commitments where
Transport is used.

A route is the runtime-authorized binding between a caller and a selected
provider invocation path.
It may refer to runtime addresses, provider addresses, module instance
identities, authorization material, and transport connections, but it does not
replace them.

Runtime Control establishes and manages routes; it is not the ordinary module
invocation protocol.
After establishment, ordinary calls use the route's `invocation_descriptor`,
which identifies a direct, local-transport, or remote-transport invocation path
and the descriptor kind required to interpret any descriptor bytes.
Descriptor bytes are profile-defined and MUST NOT be interpreted without the
accompanying `descriptor_kind`.

The `route_record` CDDL is the portable representation used when routes are
exposed, committed, audited, or exchanged through Runtime Control.
Implementations are not required to serialize, allocate, or consult that record
on every ordinary call.
Direct-mode implementations MAY compile, cache, or elide route records
internally, provided they preserve the externally observable route lifecycle,
authorization, revocation, and error semantics required by the selected
profile.

The route model does not define a separate portable "runtime-mediated" route
kind.
If a runtime, module host, or facade provider remains on the invocation path,
that is an implementation property of the selected provider or descriptor.
The portable requirement is that the authorized invocation path preserve the
module contract observed by callers.

For a remote-transport invocation path, the Transport endpoint used for ordinary
module calls exposes the selected module contract, not the Runtime Control
contract, unless the selected module is itself `logos_runtime_control`.
The Transport Hello `schema` field on that invocation path carries the
structural schema identity of the ordinary module endpoint being invoked.
If the caller requires a specific module contract, the caller uses
`expect_schema` for that module contract.
Runtime Control schema commitments identify runtime-control endpoints only;
they do not identify every ordinary module provider behind a remote runtime.

Route states have the following portable meanings:

- `establishing`: not usable for ordinary calls;
- `ready`: usable through its invocation descriptor;
- `draining`: rejects new calls but may allow bounded in-flight work to
  complete according to runtime policy;
- `revoked`, `failed`, and `closed`: not usable for new calls.

Before a route becomes `ready`, the runtime that owns the target provider MUST
perform the route authority check for that provider.
For remote providers, the caller or caller runtime presents authorization
material to the target runtime, not to the raw module C function.
The runtime that owns the target provider may evaluate the check locally or
consult its configured Capability Authority provider.
It owns enforcement of the result, including denial, expiry, revocation, and
audit recording.

Route authority uses the runtime authority policy defined in Section 9.
When that policy is externalized through Capability Authority, token, grant,
evidence, and decision formats are defined by the Capability Authority
contract.
Runtime input records, static registration, deployment configuration, and
embedded runtime-host wiring may bootstrap local authority policy, but do not
bypass route enforcement.
The optional `authority` field carries opaque references to the check result
and audit material.
It is not a portable token format or bearer credential.
In this revision, `authority_ref` identifies an authority decision known to the
runtime or its configured Capability Authority provider.
It is not presented by callers as proof of authority.
Callers present authority inputs through the selected method, transport, or
runtime API surface;
the runtime evaluates those inputs through authority policy and records the
resulting decision reference when needed.

Route establishment follows these portable steps:

1. A caller asks its runtime for access to a module contract, provider, or
   generated helper binding.
2. The caller runtime resolves the request to a `module_provider_address`.
3. The runtime validates the expected module contract using the module name,
   schema namespace, schema commitment, compatibility metadata, and Transport
   Hello `schema` commitment where Transport is used.
4. If the selected provider is owned by another runtime instance, the caller
   runtime contacts the target runtime.
5. The target runtime performs the route authority check and may consult its
   configured Capability Authority.
6. If the check fails, no usable route is created and the caller sees a
   route-establishment failure.
7. If the check succeeds, the runtime creates or exposes a `route_record` and
   binds the caller-side handle, helper, or transport session to the route.
8. The route becomes `ready` only after the invocation descriptor is usable and
   the target provider still satisfies the expected module contract.
9. Ordinary module calls use the invocation descriptor, not runtime-control
   methods.

Route establishment is a runtime operation.
It may be triggered by caller-side handle acquisition, generated helper
binding, transport session setup, runtime-host wiring, or another runtime API
surface.
This revision exposes route observation and revocation through Runtime Control.
An implementation-specific route creation surface MUST preserve the provider
selection, contract validation, authority check, route lifecycle, and revocation
semantics defined here.

A runtime MAY combine, cache, or precompute these steps when the selected
profile allows it, for example by binding direct-mode generated helper function
pointers during startup or first use.
Such optimization MUST NOT bypass provider selection, contract validation,
authority checks, route lifecycle, or revocation semantics.

Route establishment failure is distinct from route failure after readiness.
If establishment fails, the runtime MUST NOT return a caller-side handle,
helper binding, or invocation descriptor usable for ordinary calls.
If a ready route later fails, the runtime MUST invalidate or transition the
route according to the route-state rules and report ordinary call failures
through the selected invocation path.

The target runtime remains the enforcement point for providers it owns.
A caller runtime MAY assist with discovery, local policy, cached grants, or
transport setup, but it MUST NOT unilaterally authorize access to a provider
owned by another runtime.
Delegation of provider-access authority MUST be represented as an allow decision
accepted by the target runtime's authority policy.

Route enforcement is a runtime responsibility; route policy is not.
The runtime owns the minimal state needed to enforce whether an established
route may still be used: route identity, selected provider, invocation
descriptor, authority result reference, and failure state.
Policy decisions that allow, deny, expire, revoke, retry, or reselect routes
come from runtime authority policy.
The runtime enforces the resulting decision on its route table and caller-side
bindings.

The runtime MUST revoke or fail routes whose selected provider is no longer
usable, including provider removal, module-instance stop or unload, incompatible
schema change, loss of required Transport schema commitment, remote runtime
disconnect, authority expiry, or explicit policy revocation.
When a route is revoked, failed, or closed, the runtime MUST prevent new
ordinary calls through that route.
In-flight call behavior, timeout policy, idle expiry, and retry policy are
profile or implementation policy; if such policy invalidates a route, the
runtime enforces the resulting route revocation or failure.

Automatic provider reselection is not a runtime default.
If runtime authority policy allows reselection, the replacement provider MUST
satisfy the same module contract expectation.
The runtime MUST create a new route identity or an explicit renewal relation
defined by runtime authority policy and visible through Runtime Control
observation.

For audit and observation, the runtime MUST retain enough route material for a
privileged observer to reconstruct the enforcement decision through the
runtime-control contract.
The minimum material is the route identity, caller runtime identity, selected
provider address, expected module name, expected schema commitment when known,
authority result reference when present, route state transition, and failure
code when present.
Runtime Control exposes route observation through `list_routes` and
`route_state_changed_event`.
Retention policy and external evidence formats are authority-policy and
deployment concerns.
If authority policy is externalized through Capability Authority, authority
decision references and audit references are defined by the Capability
Authority contract.

Remote lifecycle ownership is not transferred by facade or route creation.
The runtime instance that owns a live module instance owns that instance's
portable lifecycle transitions, including load, start, readiness, stop, failure,
and unload.
A local remote-module facade reflects remote lifecycle and connectivity state
for local provider selection and route enforcement, but it does not become the
lifecycle owner of the remote module instance.

Authority to control a local runtime is not transitive.
A host shell or runtime host that may use Runtime Control on a local runtime
MUST NOT infer authority to control a remote runtime, load modules in that
remote runtime, or stop remote-owned module instances.
Remote lifecycle-control operations require explicit authority accepted by the
runtime that owns the target module instance.

The default remote-provider pattern is that the server-side runtime host or
headless host shell controls the server runtime through that runtime's local
Runtime Control surface.
A local runtime may establish authorized routes to providers exposed by the
server runtime, and may observe reflected readiness or failure through its local
facade provider state.
That invocation authority does not imply remote lifecycle-control authority.
A local runtime or local host shell may act as a remote runtime-control client
only when it presents authority accepted by the remote runtime according to the
remote runtime's policy.

A remote-module facade has local provider state and reflected remote state.
The local provider state describes whether the facade provider is available to
the local runtime for provider selection and route establishment.
The reflected remote state describes the last lifecycle/readiness/failure state
reported or proven by the runtime that owns the remote module instance.
A facade provider MUST NOT be treated as ready for ordinary calls unless both
the local facade provider is usable and the reflected remote target state is
compatible with readiness for the expected module contract.
When a local runtime refreshes reflected remote state through a remote Runtime
Control endpoint, it uses the remote runtime's Runtime Control contract over
LOGOS-MODULE-TRANSPORT.
The local runtime may query the remote runtime's `list_modules` or
`get_readiness` methods, or observe remote runtime-control events, subject to
authority accepted by the remote runtime.
The returned remote records are interpreted as remote runtime-control records.
They do not become local provider records until the local runtime maps them into
local facade provider state.
When mapping remote Runtime Control records into a local facade provider record,
the local runtime MUST preserve the remote runtime endpoint or identity used for
refresh, the remote target provider id or module name when known, the expected
module name, schema namespace, schema commitment, compatibility metadata, and
the reflected readiness or failure state used for local provider selection.
The mapped local facade provider record MUST expose the local facade provider
address as its `provider`.
It MAY expose the remote target through `remote`.

Reflected remote state is advisory unless it is fresh according to transport
state, Runtime Control observation, and runtime authority policy.
If the local runtime cannot refresh or validate remote state when required, it
MUST treat dependent facade providers and routes as not ready, failed, or
revoked according to runtime authority policy.
A local facade MUST NOT hide remote stop, unload, failure, contract mismatch,
or loss of remote reachability by continuing to report ready state for new
ordinary calls.

Remote lifecycle and facade failures MUST be classified at the runtime boundary
before they are reported to callers, host shells, or Runtime Control observers.
At minimum, an implementation MUST preserve the distinction between local facade
failure, remote runtime unreachable, remote module not ready, remote module
stopped or unloaded, remote module failed, authority failure, and module
contract mismatch.
Runtime Control reports these classifications through readiness state, route
state, reason strings, and runtime-control events.

Remote lifecycle state changes that make a reflected provider unusable MUST be
propagated to the local runtime's facade provider state before the local runtime
establishes new routes to that provider.
If such a state change affects existing routes, the local runtime MUST apply
the route enforcement rules defined by this specification and revoke, fail,
drain, or close dependent routes according to runtime authority policy.

A host shell observes the local runtime's provider, route, and facade state
through the local runtime-control contract.
The host shell is not required to contact the remote runtime directly to learn
that a local facade provider is unavailable, stale, failed, or not ready.
If the local runtime cannot determine fresh remote state, it MUST expose that
uncertainty as local reflected state rather than reporting the facade provider
as ready.

The `list_modules` method returns the runtime-known module records visible to
the authorized runtime-control caller.
Its response is runtime introspection state, not a portable ordinary-module
discovery mechanism.
The returned records describe local provider records, local module instances,
standalone transport providers, and local remote-module facade providers known
to this runtime instance.
Policy MAY restrict which records or fields are visible to a caller.
The method does not install packages, resolve dependency graphs, establish
routes, or grant authority to call any listed provider.

The `list_routes` method returns route records visible to the authorized
runtime-control caller.
If `module` or `provider` is present, the runtime filters the returned records
to matching routes.
The response is runtime-control observation state.
It does not establish, renew, revoke, or authorize routes.
Policy MAY restrict which route records or fields are visible to a caller.

The `revoke_route` method asks the runtime to revoke an established route that
it owns or controls.
If successful, the runtime MUST prevent new ordinary calls through that route.
In-flight call behavior is governed by runtime authority policy.
The response reports the resulting route state.
The method does not revoke authorization grants outside the runtime route
record unless the runtime authority policy or Capability Authority decision
defines that effect.

The `start_module` method starts a module record already known to the runtime.
If the module record is not known, the runtime returns the ordinary
schema-defined error result for "module not found" or equivalent runtime
failure.
The method does not install packages, resolve package dependencies, or create
new runtime records by itself.
For a local module implementation, success means the runtime has performed the
portable lifecycle work needed to move the selected module instance toward
`ready`, including loading and lifecycle initialization where applicable.
For a standalone transport provider or remote-module facade provider,
`start_module` does not take ownership of the remote implementation lifecycle;
it may only start or refresh the local provider/facade state owned by this
runtime instance.
The response reports the resulting local runtime lifecycle state.

If a runtime may have multiple live instances for the same module name, the
`instance` field disambiguates the target.
If no ambiguity exists, the caller MAY omit `instance`.

The `stop_module` method stops the selected module instance.
It does not perform package uninstall, dependency cascade confirmation, or
user prompting.
A runtime host may perform those workflows before calling `stop_module`.
For a local module implementation, success means the runtime has performed the
portable lifecycle work needed to move the selected module instance toward
`stopping` or `unloaded`, including lifecycle destruction where applicable.
For a standalone transport provider or remote-module facade provider,
`stop_module` does not stop the remote implementation unless a separate
authorized remote-runtime operation is performed.
It may only stop, detach, or mark unavailable the local provider/facade state
owned by this runtime instance.
The response reports the resulting local runtime lifecycle state.

The `get_readiness` method reports the runtime lifecycle state for the
selected module instance.
For local module instances, the reported state is the local runtime-owned
lifecycle state.
For standalone transport providers and remote-module facade providers, the
reported state is the local provider/facade state owned by this runtime
instance, including any reflected remote target state that the runtime has
accepted as fresh.
If the runtime cannot determine fresh remote state, it MUST report uncertainty
through `state` and `reason` rather than reporting the provider as `ready`.
Method-level application readiness remains part of the module's own schema
semantics, as described in Section 3.4.

The `module_state_changed_event` event reports runtime lifecycle transitions
observed through this control surface.
It is not a replacement for schema-defined events published by ordinary
modules.
For local module instances, the event reports transitions in local
runtime-owned lifecycle state.
For standalone transport providers and remote-module facade providers, the
event reports changes in local provider/facade state, including reflected
remote state changes that affect local readiness.
The event does not prove remote lifecycle authority or remote state freshness
by itself; callers interpret it according to the selected runtime-control,
transport, and deployment policy.

The `route_state_changed_event` event reports route state transitions visible
through this control surface.
It is observation state only.
It does not establish, renew, revoke, or authorize routes by itself.
Policy MAY restrict which route events are visible to a caller.

Because the runtime-control interface is an ordinary Logos module contract at
the schema layer, its schema and values are subject to
LOGOS-MODULE-COMMITMENT-MODEL and LOGOS-MODULE-HASH-PROFILE in the same way
as other module contracts.
When Runtime Control records are committed, audited, or exchanged as portable
evidence, the committed value is the schema-typed value for the relevant
runtime-control record, such as `module_record`, `route_record`,
`runtime_endpoint`, `module_provider_address`, or `schema_commitment`.
Implementations MAY use different internal structures, but portable evidence
MUST be derived from the CDDL-defined runtime-control value.
This specification does not require every transient runtime-control response to
be committed.

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

If a local-transport-hosted module fails during startup before it reaches ready
state, the same cleanup rule applies to the partially started host process.
The runtime MUST NOT leave failed startup children running as unregistered
modules.

---

## 11. UI Bridge (UI Modules)

UI bridge details are out of scope for this specification.
They belong in downstream specifications or framework-specific documents.

The only runtime-level requirement is that any such bridge preserve the
canonical module contract defined by LOGOS-MODULE-INTERFACE and the execution
semantics defined by this runtime specification.

---

## 12. Large Payload Boundary

The runtime lifecycle model does not define a generic streaming or
chunked-transfer facility.
Ordinary module calls may be routed directly or through a transport binding,
but the runtime does not make request, response, or event payloads unbounded.

Message framing and message-size limits are transport-binding concerns.
For stream transports, they are defined by LOGOS-MODULE-TRANSPORT.

Module interfaces that need large data transfer in this version should model
that explicitly in their schema, for example with:

- filesystem paths for co-located modules
- external references (URLs, CIDs) that the caller can fetch separately
- multiple smaller requests if the data can be chunked at the
  application level

Future specifications may define generic streaming or large-object transfer
profiles.
That transport extension belongs primarily in LOGOS-MODULE-TRANSPORT, while
any schema-level conventions for chunked methods or stream references belong
in LOGOS-MODULE-INTERFACE.

---

## Appendix A. Implementation Notes (Informative)

Generic module hosts receive LOGOS-MODULE-TRANSPORT requests as method names and
deterministic CBOR request payloads.
For shared-library modules, the generic host invocation path is the dispatch ABI
defined by LOGOS-MODULE-INTERFACE.

A foreign-function interface such as `libffi` could theoretically derive native
C calls from schema information at runtime, but this revision does not define
that as the interoperable module-host path.

### A.1 Fixed Static Applications

The Logos module architecture also supports fully static application packaging.
In this packaging style, the module set is curated at build or packaging time,
and runtime discovery MAY be reduced or omitted by the selected implementation.

Both patterns below still use the same mandatory callee-side C symbols defined
by LOGOS-MODULE-INTERFACE.
Neither pattern defines a second module API.

**Generated runtime facade library.**
A generated runtime facade library is the lowest-friction static packaging form.
The application driver links one generated library and includes one generated
facade header.

The facade links the curated modules and MAY include or link the runtime
components needed by the generated caller-side APIs.
The application driver does not include individual module headers, perform
module binding, or manage module lifecycle ordering directly.

A generated runtime facade library differs from ordinary direct C embedding.
In ordinary direct C embedding, the application includes module headers and
calls each module API itself.
The facade instead consolidates the curated module set behind one app-facing API.

If the facade includes the relevant runtime components, it can provide Logos
runtime behavior such as lifecycle management, callback wiring, event delivery,
outbound module calls, and policy checks.
A facade that omits those runtime components is only a generated direct-call
wrapper and does not provide the omitted runtime behavior.

This pattern is useful when the module set is fixed and the application driver
should remain small.

**Fixed embedded-runtime app.**
A fixed embedded-runtime app links the runtime library and the curated modules
directly.
The application uses the runtime API explicitly.
The application or generated startup glue makes static direct-mode bindings
available to the runtime before `logos_runtime_start()`.

Compared with a generated runtime facade library, this pattern leaves runtime
setup visible to the application.
The application can choose the registered module set, initialization order,
policy configuration, test bindings, and other runtime options exposed by the
runtime API.
It still avoids dynamic loading and transport serialization for curated modules.

Build-time or package-time schema checks MAY replace runtime discovery or schema
negotiation where the module set and versions are fixed.

---

## Appendix B. Runtime Control Record Construction Vectors

This appendix gives informative construction vectors for selected Runtime
Control records.
These vectors are schema-shaped examples for implementers and reviewers.
They do not define deterministic CBOR bytes, hash inputs, or digest values.
Those require an accepted deterministic encoding and hash-suite vector set.

### B.1 Runtime Endpoint

```cddl
{
  runtime_instance_id: "rt-local-001",
  address: {
    transport: "unix-stream",
    path: "/run/logos/runtime-control.sock",
    profile: "local-dev"
  }
}
```

This value conforms to `logos.runtime_control.runtime_endpoint`.
The `runtime_instance_id` is opaque and does not prove trust or authority.

### B.2 Module Provider Address

```cddl
{
  runtime_instance_id: "rt-local-001",
  provider: "provider-storage-local"
}
```

This value conforms to `logos.runtime_control.module_provider_address`.
The `provider` id is scoped to the runtime instance identified by
`runtime_instance_id`.

### B.3 Local Module Record

```cddl
{
  module: "storage_module",
  provider: {
    runtime_instance_id: "rt-local-001",
    provider: "provider-storage-local"
  },
  instance: "instance-storage-001",
  state: "ready",
  mode: "direct",
  schema_namespace: "storage",
  schema: {
    commitment_model: "logos.commitment-model.2026-06",
    schema_root: h'00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-05",
    hash_suite: "example-suite"
  }
}
```

This value conforms to `logos.runtime_control.module_record`.
The `provider` field names the local runtime-known provider.
The `schema` field is illustrative and does not define a production hash suite.

### B.4 Remote Facade Module Record

```cddl
{
  module: "storage_module",
  provider: {
    runtime_instance_id: "rt-local-001",
    provider: "provider-storage-remote-facade"
  },
  remote: {
    runtime: {
      runtime_instance_id: "rt-remote-001",
      address: {
        transport: "tls-tcp",
        host: "remote.example",
        port: 443,
        server_name: "remote.example",
        profile: "remote-dev"
      }
    },
    provider: "provider-storage-remote"
  },
  state: "ready",
  mode: "remote-transport",
  schema_namespace: "storage",
  schema: {
    commitment_model: "logos.commitment-model.2026-06",
    schema_root: h'00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-05",
    hash_suite: "example-suite"
  }
}
```

This value conforms to `logos.runtime_control.module_record`.
The outer `provider` names the local facade provider.
The nested `remote.provider` is scoped to the remote runtime identified by
`remote.runtime`.

### B.5 Remote Facade Route Record

```cddl
{
  route: "route-storage-remote-001",
  caller_runtime: "rt-local-001",
  target_provider: {
    runtime_instance_id: "rt-local-001",
    provider: "provider-storage-remote-facade"
  },
  module: "storage_module",
  schema_namespace: "storage",
  schema: {
    commitment_model: "logos.commitment-model.2026-06",
    schema_root: h'00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-05",
    hash_suite: "example-suite"
  },
  state: "ready",
  invocation: {
    kind: "remote-transport",
    descriptor_kind: "transport-session"
  },
  authority: {
    authority_provider: {
      runtime_instance_id: "rt-local-001",
      provider: "provider-capability-authority"
    },
    authority_ref: "decision-route-001",
    audit_ref: "audit-route-001"
  }
}
```

This value conforms to `logos.runtime_control.route_record`.
The `target_provider` is the local remote-facade provider.
The `authority_ref` is an authority decision reference,
not a caller-presented bearer token.
The `descriptor_kind` identifies how runtime-local code interprets the
invocation descriptor.
No descriptor bytes are shown in this construction vector.

---

## References

### Normative

- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-TRANSPORT -- Socket protocol specification.

### Informative

- logos-liblogos -- Current runtime implementation (Qt-based).
  https://github.com/logos-co/logos-liblogos

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
