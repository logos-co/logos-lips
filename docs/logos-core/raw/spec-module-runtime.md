# LOGOS-MODULE-RUNTIME

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Runtime                                          |
| Slug         | 304                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines Runtime-owned module admission, provider registry, logical lifecycle, routing, event delivery, and control semantics, including:

- Module admission and logical lifecycle
- Provider registration, discovery, and validation
- Route establishment and invocation across direct, local Transport, and remote Transport modes
- Event publication, subscription, and delivery
- Runtime Control operations for authorized Runtime observation and lifecycle control
- Threading and concurrency semantics
- Streaming and large data (acknowledged gap)

> **Note:** A complete Logos module system, as defined by LOGOS-MODULE-SYSTEM-BCP,
> uses Module Loader for canonical local module realization.
> This specification defines the Runtime semantics independently of that higher-layer module contract.
> An implementation may conform to this specification without implementing Module Loader.
> When composed, Runtime invokes Module Loader through its ordinary module contract;
> the two need not share a process, binary, or implementation-private API.

This spec does NOT define the module interface format (see
LOGOS-MODULE-INTERFACE) or the socket wire protocol (see
LOGOS-MODULE-TRANSPORT).

This specification also does NOT define implementation acquisition, concrete realization mechanisms, or platform presentation integration.
Package scanning, process creation, credential handoff into an execution environment, and GUI-framework integration belong to the applicable higher-layer module contracts and deployment, security, or presentation profiles.
An implementation conforming only to this specification MAY use implementation-local mechanisms for those concerns.
Such mechanisms do not become Logos participants or consumers and MUST NOT change Runtime-owned identity, lifecycle, routing, authority, observation, or audit semantics.

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
  applicable ABI caller resolves the mandatory C symbols with `dlopen` / `dlsym` or an
  equivalent platform mechanism.
- **Static direct mode:** the module implementation is linked into the applicable ABI caller's binary.
  That caller obtains addresses for the same mandatory C symbols through build-time or startup integration.

### Terminology

This specification uses the following terms:

- **Runtime engine:** The implementation substrate that creates and enforces a Runtime instance.
  It owns realization orchestration, lifecycle enforcement, routing,
  policy enforcement points, and the registry implementation.
  It is below the participant model and is not a consumer.
- **Runtime instance:** A concrete running Logos Runtime with its own identity, registry, lifecycle state, routing-selection state, route state, and policy enforcement points.
  It owns every local module instance admitted to that Runtime and intrinsically provides the Runtime Control contract.
  The Runtime instance is the authority boundary for ordinary module lifecycle, routing,
  provider selection, initialization-service binding, and route state.
- **Runtime Control:** The intrinsic contract surface exposed by a Runtime instance through the `logos_runtime_control` contract.
  Modules invoke Runtime-owned operations through this contract using the same authority, typed-value, commitment, evidence, and error semantics used for module contracts.
  When Runtime admits a module instance, it makes Runtime Control callable for that consumer without first requiring route establishment.
  The Runtime Control exposure is coextensive with the Runtime instance.
- **Runtime host:** The process or embedding environment that contains a Runtime instance and keeps it running.
  It is an implementation role rather than an independently identified Logos entity or participant.
- **Module:** The smallest independently identified participant whose execution or presentation is admitted and lifecycle-tracked by exactly one Runtime.
  A module has identity independent of any provided contract.
  It may provide no primary contract, or one primary concrete contract with zero or more exact implemented interface contracts.
- **Module implementation:** Code, resources, or built-in behavior that realizes a module's executable or presentation behavior.
  Provider ABI requirements apply only when the module provides callable contracts.
- **Module instance:** One Runtime-known realization of a module owned by exactly one Runtime.
  It has one Runtime-scoped instance identity, one Runtime-owned lifecycle, and optional persistent-state, placement, presentation, and provider state.
  The owning Runtime controls its Logos lifecycle semantics.
  A module instance identity MAY remain stable across stop/start cycles when the Runtime host or deployment preserves that identity.
- **Module state assignment:** An abstract Runtime-owned assignment of persistent state to a module instance within the Runtime model.
  It identifies the binding between a module instance and its assigned persistent state.
  It does not define the concrete storage realization or grant authority to allocate, inspect, share, retain, delete, or migrate that storage.
  Runtime or deployment implementation mechanisms realize the assignment as concrete storage according to active policy.
- **Module provider:** The Runtime-known, route-facing exposure of callable behavior from a module instance.
  One provider record may expose the module's primary concrete contract and exact implemented interface contract views.
  Every route selects exactly one of those contracts.
  A local provider is backed by a local module instance.
  A remote module facade is a local provider record that represents a module instance owned by another Runtime.
  A provider does not introduce a separate module implementation or lifecycle.
- **Requiring module:** A module that declares provider requirements.
  Provider requirements do not give the module another identity or lifecycle.
- **Consumer:** The module instance whose authority is used for an operation.
  Runtime authenticates the consumer at the invocation boundary.
  A route is established for exactly one consumer, and only that module instance may use it.
  Consumer is a relationship in an operation or route rather than a separately managed entity.
  A module-instance address identifies the consumer.
  The address does not authenticate the module instance or grant authority.
  Runtime MUST preserve the addressed module-instance identity while it is needed to keep active routes and retained authority or audit material unambiguous.
- **Presentation module:** A module that contributes one or more presentation surfaces through a selected presentation profile.
  Presentation is a module facet, not a separate participant class.
- **Consumer-only module:** A module that provides no callable contract.
  It retains ordinary module identity, lifecycle, requirements, routes, authority, state, placement, and audit attribution without a provider or dispatch implementation.
- **System service provider:** An ordinary local module provider that Runtime or deployment policy binds to a runtime-adjacent responsibility.
  The role does not create another entity, provider kind, lifecycle, route model, or source of authority.
- **Remote Runtime:** Another Runtime instance reachable over a transport boundary and authorized or enrolled according to active Runtime policy.
  Its enrolled Runtime identity authenticates that Runtime boundary according to the selected remote profile.
- **Remote module facade:** A local provider record that represents callable behavior of a module instance owned by a remote Runtime.
  The facade is routing state, not another local module instance or lifecycle owner.
- **Route:** A Runtime-authorized binding between a consumer and a provider invocation endpoint.
  Runtime Control establishes, tracks, and revokes routes.
  Ordinary module calls use the provider invocation path described by the route, not Runtime Control methods.
  A provider invocation path may be direct, local transport, or remote transport, but the route model does not make Runtime mediation a separate route kind.
- **Runtime-controlled invocation boundary:** The Runtime enforcement point that resolves the consumer, route, selected provider, selected contract, method, authority, commitments, and audit requirements for a call.
- **Process-local invocation boundary:** The ABI caller inside the execution form that owns a realized module context.
  For a hosted provider, it may also expose the provider endpoint and perform provider-side invocation.
- **Provider-side invocation boundary:** The final enforcement and scheduling boundary before provider method code.
  It enforces the selected provider session and route access and then invokes the provider through its applicable ABI or equivalent built-in path.

Provider and consumer are orthogonal roles.
A module instance may expose providers and act as a consumer without acquiring a second module identity or lifecycle.
The word caller describes a consumer while it performs a particular call, subscription, or other operation; it does not introduce another managed entity.

Every consumer is a module instance.
The Runtime engine, Runtime host, bootstrap machinery, operating-system objects, protected inputs, humans, and unauthenticated peers remain outside the participant model.
They do not receive unconstrained consumer references.
If a later specification needs a human, user-session, device, organization, or agent identity, it must define that identity and its delegation relationship explicitly.

The Runtime's own identity identifies its boundary and intrinsic Runtime Control exposure.
An enrolled source Runtime authenticates a remote boundary with that identity.
When a module performs an operation, Runtime binds that module instance as the consumer and active authority policy must permit the consumer and requested operation.

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

Module Loader, Package Manager, and Capability Authority define module contracts for runtime-adjacent responsibilities.
Every system service provider MUST be a local module provider backed by a local module instance.
System service providers use the same contract, provider, route, and transport model as other local Logos module providers.
Runtime MUST maintain ordinary provider and lifecycle records for their module instances.
They are not a separate module class, ABI class, transport class, or lifecycle class.
A provider becomes a system service provider only when runtime or deployment policy binds it to one of those responsibilities.
A system service provider MAY use direct mode or local transport mode according to active policy and the applicable profile.
An implementation MAY co-locate or statically link system service code, but Runtime MUST represent that code as a direct-mode local module instance and preserve the ordinary route and authority records.
Remote facades and external host or deployment services MUST NOT be bound as system service providers in this revision.
Implementing the corresponding module contract does not grant authority by itself.
Authority comes from runtime or deployment policy, including bootstrap policy and explicit grants.
Higher-layer specifications define the Module Loader, Package Manager, and Capability Authority module contracts.
Their contract operations and records are outside this specification.

### Runtime and System Service Boundary

Runtime is the enforcement and state authority for the Runtime semantics defined by this specification.
This responsibility boundary does not require a particular process structure, binary layout, internal API, or implementation architecture.

Runtime MUST remain authoritative for:

- module instance identity and lifecycle state;
- module implementation and realization-result acceptance;
- provider registration, readiness, selected-contract selection, and visibility enforcement;
- route establishment, state, renewal, and revocation;
- consumer, provider, selected-contract, and route enforcement at call, event, subscription, and route boundaries;
- validation of realization and Transport handoffs before a provider becomes ready or remotely exportable;
- the Runtime Control surface and its observation and control semantics;
- runtime-controlled resource-accounting and policy-enforcement hooks required by an active profile.

A system service provider MAY evaluate policy, supply records, or realize work on behalf of Runtime.
It MUST NOT directly replace or mutate Runtime-owned module lifecycle, provider, route, or Runtime Control state.
Runtime MUST validate the service result and apply any resulting Runtime-owned state transition through its own enforcement boundary.

An implementation-local realization mechanism or a bound Module Loader provider may realize accepted implementations,
report operational status, release them, and interact with concrete backends.
Runtime remains responsible for deciding when realization is required,
validating the resulting realization and handoff information,
and mapping the result into Runtime-owned module lifecycle and readiness state.

When present, Capability Authority may evaluate authorization policy and return decisions.
Runtime remains responsible for enforcing those decisions at Runtime-controlled boundaries.
When present, Package Manager may supply package, dependency, artifact, and Runtime handoff records,
but those records do not create Runtime lifecycle, provider, or route state by themselves.

Runtime Control is the sole contract surface through which a module invokes Runtime-owned operations or observes Runtime-owned state.
Runtime MUST apply authority to each requested Runtime Control method or event and to its requested scope.
Making a Runtime Control binding available to a module does not authorize any operation by itself.
A module consumes Runtime Control through a consumer-bound Runtime Control binding that preserves the contract's typed-value, authority, commitment, evidence, and error semantics.
That binding MAY use direct invocation or a Transport-backed invocation path according to the module's placement.
A direct binding MAY invoke the Runtime implementation without serializing the request or using Transport.
Provider-contract method calls and events remain operations of their selected provider contracts rather than Runtime Control operations.
An implementation is not required to perform its internal Runtime operations by invoking its own Runtime Control contract.

### System Service Availability

A runtime instance is not required to bind a provider for every runtime-adjacent module contract.
A Runtime MAY omit a system service provider when it can satisfy every applicable Runtime requirement without that provider.
Omission of a provider MUST NOT weaken or bypass Runtime lifecycle, readiness, routing, control, or enforcement requirements.
Runtime Control is part of the runtime instance and is not subject to this provider-availability rule.

Capability Authority is required when active policy or a selected profile externalizes an authorization decision through that contract.
A Runtime MAY evaluate authority policy internally when this specification or the selected profile permits it.

Package Manager is not required for Runtime to consume already resolved module facts from protected sources.
Package discovery, dependency resolution, installation, update, and removal remain outside Runtime even when no Package Manager provider is bound.

If active policy, a selected profile, or an accepted input requires an unavailable system service, Runtime MUST fail the dependent operation.
Runtime MUST NOT silently bypass the required service or substitute less constrained behavior.

## 1. Module Structure

### 1.1 What a Module Is

A module implementation conforms to the canonical native module ABI defined by LOGOS-MODULE-INTERFACE.
The ABI code may be bound statically,
loaded dynamically into a direct caller,
or loaded dynamically by a process-local invocation boundary that exposes hosted calls through Transport.
These realization choices do not change the module contract or ABI.
A module may provide no callable contract, one primary concrete contract,
one or more exact interface contracts, or a primary contract plus exact implemented interfaces.

### 1.2 Required Exports

LOGOS-MODULE-INTERFACE is the normative owner of the native module C
ABI.
A runtime implementation MUST require every identity and lifecycle symbol that
LOGOS-MODULE-INTERFACE makes mandatory for native implementations.
When resolved module input declares at least one callable contract,
Runtime MUST also require the provider symbols and schema-derived per-method
symbols applicable to that declared call surface.
When resolved input declares no callable contract,
Runtime MUST NOT reject the module merely because provider-only symbols are absent.
If an applicable mandatory symbol is missing, Runtime MUST reject the module
with a descriptive error.

In these symbol names, `<module>` is the module's flat runtime module name as
defined in section 1.3.

Runtime supplies instance-bound services through the structured initialization
input defined by LOGOS-MODULE-INTERFACE.
Runtime MUST NOT require or invoke post-initialization callback setters.

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

## 2. Native Implementation Loading

### 2.1 Dynamic ABI Binding

On platforms that support dynamic loading,
the applicable ABI caller uses the platform's dynamic linker.
For direct dynamic loading,
the ABI caller maps the accepted artifact into the process that performs direct invocation.
For hosted dynamic loading,
the process-local invocation boundary maps the accepted artifact inside the Module Host.
Common platform functions include:

- Linux/macOS: `dlopen(path, RTLD_NOW | RTLD_LOCAL)`
- Windows: `LoadLibrary(path)`

Dynamic loading maps executable artifact code into the applicable ABI caller's process.
A platform loader may execute artifact-controlled initialization before the applicable ABI caller resolves or invokes any Logos symbol.
Runtime MUST therefore complete the executable-artifact acceptance and module-execution checks in Section 3.6
before initiating realization of the artifact.

A resolved dynamic module record MUST identify the expected flat runtime module name before executable mapping.
The applicable ABI caller constructs the module-prefixed symbol names from the expected name:

```c
void* lib = dlopen("storage_module.so", RTLD_NOW | RTLD_LOCAL);

/* Known-name load path: storage_module is already known. */
typedef const uint8_t* (*call_surface_fn)(size_t* out_len);
call_surface_fn get_call_surface =
    (call_surface_fn)dlsym(lib, "logos_storage_module_call_surface");

/* ... etc for the remaining mandatory ABI symbols */
```

### 2.2 Module Symbol Resolution

After mapping an accepted artifact,
the applicable ABI caller MUST resolve the mandatory module-specific symbols defined by LOGOS-MODULE-INTERFACE using the expected module name from the resolved module record.
Runtime MUST fail the realization when any mandatory symbol is missing.

Before lifecycle initialization,
the applicable ABI caller MUST invoke `logos_<module>_name()` and return the expected module name.
When provider symbols apply,
Runtime MUST perform the call-surface and contract checks defined in Sections 2.4, 3.3, and 3.6.

The applicable ABI caller SHOULD resolve each mandatory symbol once for one loaded artifact
and MAY retain the resolved addresses for the lifetime of that load.
Symbol resolution checks that an accepted artifact exposes the required module ABI.
It is not registry discovery,
artifact-trust evaluation,
or module-execution authorization.

The resolved symbols describe one accepted implementation binding.
They do not themselves create a module instance.
For each native module instance that uses the binding,
the applicable ABI caller MUST construct the versioned initialization input defined by LOGOS-MODULE-INTERFACE and invoke `logos_<module>_init(input, out_context)`.
Each successful call MUST return a distinct non-null module context.
The applicable ABI caller MUST retain the implementation binding until every context created from that binding has been passed exactly once to `logos_<module>_destroy(context)`.

### 2.3 Direct Static Binding

On platforms where dynamic loading is unavailable or undesirable,
a module implementation MAY be statically linked and registered in the process-local ABI caller.

The applicable ABI caller MUST bind the same mandatory C symbols defined by
LOGOS-MODULE-INTERFACE.

The binding mechanism is implementation-defined and MAY be generated by a module
kit.
Common mechanisms include generated registration tables, generated static symbol
resolvers, linker-section registration, or application startup code that passes
known function pointers to the runtime.

Direct static binding MUST NOT define a second callee-side module interface.
It is a binding mechanism for the mandatory C module interface.
Direct/static callers MAY call schema-derived per-method C functions directly
instead of calling `logos_<module>_dispatch(context, ...)`.
Every instance-dependent call MUST receive the context returned for the
selected module instance.

Applications using direct static binding MUST make the module bindings available
to the applicable ABI caller before Runtime initiates realization.

### 2.4 Introspection

For every native provider, the applicable ABI caller obtains the complete deterministic-CBOR call-surface descriptor through `logos_<module>_call_surface()` before structured initialization.
That ABI call is not an ordinary module route and does not authorize provider access.
Runtime MUST validate the descriptor, every contained schema document, every
claimed contract commitment, and the complete primary/implemented-interface
set under LOGOS-MODULE-INTERFACE before provider registration.
The validated descriptor supplies the exact contract views retained on the Runtime provider record.
It does not create a combined contract identity or a multi-contract route.

Across an invocation boundary,
the well-known `logos.schema` method returns the route's selected contract and the exact interface and supporting documents required to reconstruct it,
as defined by LOGOS-MODULE-INTERFACE Section 5.1.
Runtime or the Runtime-controlled provider-side boundary MUST handle this method
before calling the concrete provider's
`logos_<module>_dispatch(context, ...)` entrypoint.
For an interface-selected route,
it MUST obtain the validated interface contract from the resolved contract inputs
and MUST NOT disclose the backing provider's primary contract or another implemented interface.

When Runtime or a language binding exposes a module-selected call binding,
that object MUST present the complete validated call surface to its caller.
Before disclosing that surface,
Runtime MUST obtain the per-contract `discover` allow decisions required by
LOGOS-MODULE-CAPABILITY-AUTHORITY for the selected provider.
If any exact contract view may not be disclosed,
Runtime MUST fail the module-selected object request rather than return a filtered surface.
Presenting that metadata does not establish or authorize any route.
Each callable contract view uses its own exact-contract route rather than one multi-contract route.
Its primary and interface methods remain bound to their respective route,
contract root, access scope, expiry, revocation, and audit records.

A consumer may call `logos.schema` only on a ready route
whose `route_access.methods` permits the well-known method declaration root.
The call does not enumerate providers, contracts outside the selected contract's required construction input, routes, or registry state.
Returned schema text remains untrusted input to the consumer
and is subject to the same Interface parsing and resolution limits.

---

## 3. Service Registry

### 3.1 Purpose

The service registry maps module names, and where needed module instance
identity, to module providers.
Provider records include the information needed to reach or realize the target:
direct bindings or local transport endpoints for local module instances, or remote transport and target material for remote module facades.
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
    primary_contract: <validated contract schema, when present>
    interfaces:  <validated interface contract schemas>
    pid:         <process id>                 (local transport mode only,
                                               when process-backed)
}
```

### 3.3 Runtime Module Binding

A runtime registry entry is a runtime module binding.
It binds the operational module name used for realization and routing to a module provider and to the exact contract views that Runtime expects that provider to expose.

The binding contains:

- the flat runtime module name;
- the module provider address;
- the module instance identity, when applicable;
- the execution mode and applicable realization or connection information;
- the optional primary contract schema and commitment;
- the implemented interface schemas and commitments;
- the validated provider call surface or another accepted way to obtain those
  exact contract inputs.

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

When a registry entry includes expected contract commitments,
Runtime MUST compare the provider's validated contract views against those expectations before treating the provider as ready.
Before treating any native provider as ready,
Runtime MUST obtain the complete declared surface from the applicable ABI caller.
For local or remote transport modules,
the Transport Hello `schema` field validates only the exact contract selected
for that invocation path.
Other contract views require their own exact-contract validation from accepted
module facts, protected provider metadata, or another invocation path.

If an expected contract is absent from the validated provider surface or has a different commitment,
Runtime MUST reject that provider view and MUST NOT route calls through it.
Runtime MAY retain validated contract views for diagnostics, later policy
decisions, caller-visible introspection, and module-selected call-binding construction.

This specification defines the runtime binding and the checks the runtime
performs against it.
It does not define package signatures, artifact digests, catalog trust,
update policy, or the on-disk manifest schema that may supply the binding.
Those topics belong to higher-layer module-contract specifications and deployment profiles.
LOGOS-MODULE-SECURITY-CONSIDERATIONS records threat analysis and hardening
guidance for these bindings.

### 3.4 Module States

```
  [unloaded] -- start / realize / attach --> [loaded] -- readiness --> [ready]
       ^                                          |                       |
       |                                          v                       v
       +--------------- cleanup ---------------- [error]              [stopping]
       ^                                                                  |
       +------------------------- stop and cleanup ------------------------+

  [error] -- policy permits / establish new realization --------------------> [loaded]
  [ready] -- unexpected realization failure -------------------------------> [error]
```

- **unloaded:** The module instance is known to Runtime but has no active local realization or attached facade binding.
- **loaded:** Runtime has acquired or attached the selected realization and is performing the applicable initialization and readiness checks.
  The name is retained for the lifecycle state value even when no dynamic-library load occurs.
- **ready:** The module instance has completed its realization-specific lifecycle checks and is available for the roles declared for that instance.
- **stopping:** Runtime has begun logical shutdown and is waiting for applicable draining, lifecycle destruction, realization stop, detachment, and cleanup.
- **error:** Realization, initialization, readiness, execution, or cleanup failed.
  Error details are available through Runtime observation.

These are Runtime-owned logical module-instance states.
They apply to every module instance.
A provider is an optional facet of a module instance.
The `ready` module state therefore does not imply that a provider record exists.
An exact provider view becomes usable only after the module instance is `ready`
and Runtime has completed the applicable contract, invocation-path, and authority checks.

For a local realization, `loaded` means the selected realization mechanism has established the implementation binding or execution form.
For a native direct realization,
this state includes mapping or binding, metadata validation,
structured initialization, and Runtime readiness checks.
An operational local realization may still be waiting for Runtime contract validation,
provider-endpoint validation, registration, or profile-specific readiness evidence.
A locally realized consumer-only module does not need a provider endpoint or contract handshake;
its realization is ready after every applicable non-provider handoff and selected-profile readiness check succeeds.

Runtime lifecycle ownership does not imply ownership of the containing operating-system process.
An embedded application, daemon, runtime host, or deployment mechanism may own or supervise that process.
Runtime still owns the module-instance state transitions and MUST obtain an equivalent realization, readiness, stop, detachment, and cleanup outcome from the responsible boundary.
Stopping one static or embedded module instance does not require terminating a containing process that also hosts Runtime or other module instances.

A remote-module facade is not a local module instance and does not transfer lifecycle ownership from the remote Runtime.
When a facade record uses these state values,
they describe the local facade's availability together with the reflected remote state accepted by the local Runtime.
Starting or stopping that local facade does not start or stop the remote module unless a separate authorized remote lifecycle operation succeeds.
One remote module instance may serve multiple independently authorized routes,
provider sessions, or Transport connections.
Those access relationships do not create additional remote module instances or
additional module-instance contexts.
Ending one route, session, or connection does not destroy the remote module
instance or reset its shared instance state.
Stopping the remote module instance makes every dependent route, session, and
facade provider unusable through the ordinary revocation and failure rules.

There is no separate `active` module state.
An implementation may track operational realization status,
but Runtime maps that status and all other readiness evidence into the logical state above.
Runtime may track active calls, processes, connections, or presentation resources internally,
but those are not additional module states.

On stop, Runtime transitions the module instance to `stopping`,
marks its provider views unavailable for new routes and invocations,
prevents new outbound operations by that module instance,
drains or fails in-flight work according to active policy,
invokes lifecycle destruction when applicable,
stops or detaches the realization through the responsible boundary,
and releases Runtime-owned endpoint and provider state.
During an authorized stop, Runtime MUST close every route whose consumer is that module instance.
For an unexpected realization failure,
Runtime MUST fail every such route.
Runtime transitions to `unloaded` only after the required cleanup or detachment is complete.
After destruction or detachment completes,
Runtime MUST invalidate the module instance's consumer-bound Runtime Control binding and reject any later invocation through it.
A failed or partially realized module MUST NOT be reported as `ready`
and MUST use the same stop and cleanup boundary before its realization is forgotten.

**Important distinction: runtime-ready vs application-ready.**

For a module implementation, the `logos_<module>_init(input, out_context)` call is one Runtime initialization step.
Successful return with a non-null context establishes that the native
implementation created the instance state needed for that step;
Runtime must still complete every other readiness check required by the selected realization.
For hosted dynamic loading, Module Host performs the same ABI call
and Module Loader reports the resulting realization evidence to Runtime.

The logical `ready` state does **not** imply that all schema-defined methods will succeed immediately
or that every schema-defined method's application-level preconditions are satisfied.
A provider module MAY still require ordinary schema methods
such as `init`, `start`, login, or session establishment.
Until that setup is complete,
each expected unavailable outcome MUST be represented in the applicable method's response schema.
The provider MUST return `LOGOS_OK` when it produces that schema-defined response.
It MUST NOT use shared `LOGOS_ERR_NOT_READY` for application state.

The following consequences apply:

- Runtime transitions a module instance to `ready` only after every applicable lifecycle and realization check succeeds;
- a consumer-only module may be `ready` without a provider record or dispatch surface;
- Runtime may make an exact provider view routable only after both module and provider readiness checks succeed;
- callers MUST handle schema-defined unavailable outcomes according to the selected contract;
- Runtime MUST use `LOGOS_ERR_NOT_READY` only when Runtime-owned lifecycle, provider, or route readiness prevents a valid contract response; and
- method-level or application-level readiness is part of the module's own contract or selected profile,
  not a separate Runtime module state.

### 3.5 Discovery Sources

The runtime registry can be populated from several sources:

1. **Resolved host records.** A Runtime host, Package Manager, or deployment
   tool may hand Runtime a resolved module name, artifact path, runtime
   mode, optional primary-contract expectation,
   and implemented-interface expectations.
   A Runtime host or deployment tool may additionally supply resolved lifecycle-ordering constraints.
2. **Resolved local records.** A deployment-specific mechanism or local runtime
   setup may provide already-resolved module records for a concrete runtime
   instance.
3. **Runtime registration.** For static linking or test scenarios, modules
   may be registered programmatically via `logos_runtime_register_module()`.

The canonical package manifest, Package Manager catalog records, and Package Manager Runtime handoff are defined by LOGOS-MODULE-PACKAGE-MANAGER.
At this specification boundary, Runtime consumes the normalized handoff directly under Section 8.
Runtime MUST NOT define a second package manifest or override package facts authenticated by the Package Manager handoff.
Host- or deployment-specific source-record formats remain outside this specification.
Runtime consumes resolved records and maintains Runtime-owned module lifecycle state.

Implementations MAY enumerate artifact paths or parse non-executable package, catalog,
or deployment records before constructing resolved module records.
Such enumeration MUST NOT map or execute candidate artifact code
and does not establish artifact trust or module-execution authority.

### 3.6 Artifact Acceptance And Dynamic Loading

Dynamic module loading is an execution operation,
not passive metadata inspection.
Calling `dlopen()`, `LoadLibrary()`, or an equivalent platform loader
may execute artifact-controlled initialization.
Calling `logos_<module>_name()`,
`logos_<module>_call_surface()`,
or another exported metadata function also executes artifact code.

Before dynamically loading a module implementation,
Runtime MUST complete all of the following steps:

1. validate a resolved module record that identifies the expected module name,
   dynamic-library artifact,
   execution mode,
   and available contract expectations;
2. obtain accepted artifact evidence that binds the exact library bytes to a cryptographic digest
   through protected bootstrap input
   or an authenticated Package Manager handoff produced from an accepted package signature;
3. obtain the module-execution and permission authorization required by Section 9
   and LOGOS-MODULE-CAPABILITY-AUTHORITY,
   including the defined initial system-service bootstrap path where applicable; and
4. bind the accepted digest to the exact local artifact supplied to the realization mechanism.

After those checks succeed, Runtime MAY initiate realization of the accepted dynamic-library implementation.
The applicable ABI caller MUST invoke the normal platform loader and resolve the fixed module ABI symbols.
Runtime then validates the realization result, call surface, and contract expectations under Sections 2.4 and 3.3.
Runtime MUST NOT mark the module instance `ready` or expose its provider unless every required post-realization validation succeeds.

Loading an unknown library to inspect its name or call surface
is not a conforming artifact-discovery mechanism.
Calling `dlclose()` after inspection does not undo code that ran during executable mapping or symbol invocation.

Runtime MAY cache successful byte-digest verification for immutable content-addressed artifacts.
The cache key MUST include the exact digest and hash suite.
Runtime MUST invalidate the cached acceptance when its protected digest pin
or Package Manager verification is no longer accepted.

### 3.7 Package Dependencies and Lifecycle Ordering

Package dependencies are Package Manager-owned package facts.
They define package resolution, installation, update, and removal constraints.
They are not module-interface facts, provider requirements, or Runtime lifecycle dependencies.
Runtime MUST NOT infer module admission, startup, shutdown, provider selection, or route authority from a package dependency edge.

A Runtime host or deployment MAY separately supply resolved lifecycle-ordering constraints among Runtime module inputs.
Those constraints are protected deployment facts, not package dependency declarations.
This specification does not define their serialized representation or require Runtime to construct their graph.
When Runtime accepts such constraints,
every prerequisite module instance MUST be ready before Runtime initializes the dependent module instance.
Runtime MUST apply the constraints in reverse order during graceful shutdown.

The `requires` field declares provider requirements.
A provider requirement does not create a package dependency or a lifecycle-ordering constraint.

---

## 4. Module Routing and Handle Acquisition

### 4.1 Route Handles

A module requests a route through the Runtime Control `establish_route` method.
For each ready route returned to that consumer, the language binding MAY construct a process-local route handle.
The handle represents that consumer-bound, exact-contract route.
Closing the route uses the Runtime Control `close_route` method.
Releasing the handle afterward is local binding cleanup.

The language binding realizes the handle according to the selected route's invocation path:

- **Direct mode:** The handle wraps the selected module context and validated
  provider function pointers.
  Calls go through direct C function invocation with no serialization.
- **Local transport mode:** The handle wraps a local transport
  connection to the selected provider. Calls are serialised as Logos
  deterministic CBOR per LOGOS-MODULE-TRANSPORT.
  This revision defines Unix domain sockets as the local stream binding.
- **Remote transport mode:** The handle wraps a remote transport
  connection to the selected remote provider.
  Calls are serialised as Logos deterministic CBOR per LOGOS-MODULE-TRANSPORT.

The consumer does not need to know which mode is active.
The handle hides the invocation path.
Handle-based typed call helpers are the caller-side C API.
Such helpers take a `logos_route_handle_t*` as their first argument and route
calls through the handle.

The purpose of the handle abstraction is precisely to preserve the execution-
boundary equivalence stated above: the runtime may switch routing mode, but
the module contract observed by the caller remains the same.

For a module method such as `storage.exists`, a generated handle-based call
helper may have this shape:

```c
logos_result_t logos_storage_exists(
    logos_route_handle_t* h,
    const char*            cid,
    bool*                  out_exists
);
```

This caller-side helper is distinct from the callee-side Logos module C
function defined by LOGOS-MODULE-INTERFACE.

A language binding MAY also expose a generic dynamic call helper for callers
that discover schemas at runtime or do not have generated typed call helpers:

```c
logos_result_t logos_route_call(
    logos_route_handle_t* h,
    const char*            method,
    const uint8_t*         params_cbor,
    size_t                 params_len,
    uint8_t**              response_cbor,
    size_t*                response_len
);
```

`logos_route_call()` carries deterministic-CBOR method payloads using the same
request, response, and error shapes as LOGOS-MODULE-TRANSPORT.
Every handle-based typed helper and generic dynamic call uses the mandatory payload commitments
defined by LOGOS-MODULE-TRANSPORT.
For local or remote Transport,
the sender includes the compact commitment in the message
and the receiver independently recomputes it.
For direct mode, the Runtime-controlled boundary computes the same request and successful-response roots internally;
the per-method provider ABI receives no additional proof parameter.

A typed helper computes from its schema-typed input and output values.
A generic or dispatch path validates and decodes the deterministic-CBOR payload
before computing from the corresponding normalized Logos value.
An implementation MAY combine validation, normalization, encoding, and hashing,
but the resulting roots MUST equal LOGOS-MODULE-HASH-PROFILE for the selected contract.

Failure to validate or compute a request commitment produces `INVALID_PARAMS`
and MUST occur before provider method code executes.
Failure to validate or compute the commitment for a nominally successful direct or dispatch response
produces `MODULE_ERROR`, and Runtime MUST NOT return that response as successful.
Transport commitment failures use the fail-closed behavior defined by LOGOS-MODULE-TRANSPORT.

The handle binds one ready route, selected provider, selected contract,
consumer, and route-access scope.
Before calling `logos_<module>_dispatch(context, ...)` or a schema-derived per-method C function,
the Runtime-controlled invocation boundary MUST resolve the requested bare method name
to exactly one declaration allowed by that selected contract
and MUST enforce the corresponding declaration root against `route_access.methods`.
A method outside the selected contract produces `METHOD_NOT_FOUND`
even if the backing provider exposes a method with that name through another contract.
A selected-contract method outside the route's allowed method scope produces `NOT_AUTHORISED`.
Neither failure may invoke provider method code.
For a direct provider, Runtime MUST pass the context belonging to the route's selected module instance
and MUST NOT substitute a context from another initialization of the same implementation binding.

Direct-mode optimization MAY cache a validated per-method function address
or `logos_<module>_dispatch()` table entry for a route.
Runtime MUST NOT give the consumer a raw provider function pointer that bypasses
the route's selected-contract, access, expiry, or revocation checks.
Dynamic schema validation and successful request decoding do not replace those checks.

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
Runtime owns candidate resolution, final provider selection, selected-provider recording, route creation, and enforcement.
Routing-selection policy MAY be internal to Runtime or supplied through runtime-host, deployment, or configured policy inputs.
External policy output MAY constrain provider visibility, eligibility, continuity, pinning, or preference.
Such output is an input to Runtime selection and does not create a route or mutate Runtime-owned routing state by itself.
When Capability Authority evaluates provider visibility or access policy, it returns decision material to Runtime.
Capability Authority does not select the provider, create the route, or replace Runtime routing state.
Package Manager records and provider requirements may constrain candidate resolution, but they do not select a provider or grant route authority.
Runtime MUST validate every selected provider and enforce the applicable authority decision before making its route usable.
Route acquisition is contract-selected.
The selected contract is the exact concrete module contract or implemented
interface contract used for provider selection and route validation.
Generated typed helpers can carry this expectation by construction.
For example, a helper generated for the concrete storage contract requests that concrete contract.
A helper generated for a metrics-provider interface requests that interface contract.
Runtime APIs and runtime-host bindings may carry the selected contract
explicitly or derive it from deployment metadata.
Every route exposes only its one selected exact contract.
A route selected through the provider's primary concrete contract exposes only
methods and events defined by that primary contract.
A route selected through an implemented interface exposes only that exact interface contract.
The fact that one native dispatch ABI covers the complete provider call surface
does not widen any route.

A module-selected call binding aggregates independently authorized
exact-contract routes for its contract views.
An implementation MAY acquire those routes eagerly or lazily.
An interface-selected call binding uses only the route for that exact interface.
The aggregate object is an implementation or language-binding object;
it does not itself define or constitute a route, provider, contract, or authority record.
The runtime MAY update routing-selection state at runtime, for example when a
local provider becomes available or a remote provider becomes unreachable.
Such updates MUST NOT silently retarget an existing route.
A later route acquisition MAY select a different matching provider unless a
caller constraint, runtime-host constraint, deployment constraint, or active
policy constrains provider continuity.
If runtime policy performs automatic re-acquisition or reselection after route
failure, the runtime MUST create a new route identity or explicit renewal
relation visible through Runtime Control observation.

### 4.2.1 Runtime Control And Route Bindings For Out-Of-Process Native Modules

When a native module runs in **local transport mode**,
its process-local invocation boundary remains part of the same logical Runtime routing domain.
Runtime MUST make the consumer-bound Runtime Control binding available to the hosted module instance.
That binding MUST invoke the owning Runtime's intrinsic Runtime Control contract through a protected local invocation path.
The process-local invocation boundary MUST preserve the hosted module instance as consumer and MUST NOT permit consumer substitution.

Runtime retains ownership of registry state, routing selection, provider selection, authority enforcement, and route creation.
The process-local invocation boundary MUST NOT use a copied registry or routing-policy snapshot to make those decisions independently.
For each ready route returned through Runtime Control, the process-local invocation boundary MAY retain only the invocation material needed to realize that route handle and observe its terminal state.
It MUST NOT expose unrelated registry records, other consumers' routes, or other consumers' invocation material to the hosted module.
An invocation boundary that shares an address space with module code
MUST NOT place unrelated secrets or authority material in that address space.

Runtime Control calls from the hosted module MUST have the same typed values, authority decisions, errors, and observable state transitions as direct calls from an in-process module.
Ordinary provider calls through a returned route handle MUST have the same selected-contract behavior as the corresponding direct route.
Routing changes MUST NOT silently retarget an existing handle.

### 4.3 Capability Validation

Before returning a caller-side handle, helper binding, or invocation descriptor,
the runtime MUST verify that the caller is authorized to access the selected
provider according to runtime authority policy.
For providers owned by another runtime instance, the runtime that owns the
target provider is the enforcement point for the provider access decision.
The target runtime MAY evaluate the decision locally or consult its configured
Capability Authority provider.

Logos Core uses no generic capability-token format or capability-token issuance flow
for module-to-module access.
When route authority policy is externalized through Capability Authority,
that contract defines the decision, grant, and revocation records.
The selected Transport profile defines the provider-session route credential;
the mandatory remote profiles use `logos.route-ticket.random-256`.
Neither mechanism defines the authority policy language.
The runtime MUST treat authorization as an explicit route-establishment
decision and MUST NOT infer permission merely from module names, schema names,
provider ids, runtime ids, or successful transport connection.
Runtime MUST NOT make a route ready unless its caller-side and provider-side boundaries
can compute and verify payload commitments under the selected contract's commitment-model revision,
hash profile, and hash suite.
Before making a route ready,
Runtime MUST validate every requested method or event declaration root against the route's selected contract
or the explicitly permitted well-known common method surface.
A schema-declared method is not callable merely because Runtime parsed it,
the provider implements it,
or a caller supplied its name.

### 4.4 Event Subscription via Handle

The native caller-side subscription API,
its completion and callback semantics,
and generated typed helper rules are defined by LOGOS-MODULE-INTERFACE Section 2.5.
A language binding that exposes route handles MUST implement that surface
without changing its behavior by execution mode.

Before activating a subscription,
Runtime MUST resolve `event_name` under the route's selected contract
and enforce its event declaration root against `route_access.subscribe_events`.
In direct mode, Runtime registers the handler for synchronous delivery under LOGOS-MODULE-INTERFACE Section 2.8.
In local or remote Transport mode,
Runtime maps subscription operations and event delivery to LOGOS-MODULE-TRANSPORT.
A transported binding MUST NOT return `LOGOS_OK` from a subscription operation
before processing its matching successful `SubscriptionResult`.

Runtime owns route-lifecycle enforcement.
When a route enters a terminal state,
Runtime MUST deactivate its subscriptions
and enforce the callback quiescence defined by LOGOS-MODULE-INTERFACE Section 2.5.

---

## 5. Process Model

### 5.1 Local Realization

Runtime initiates realization of an accepted local implementation through the placement and mechanism selected by Runtime or deployment policy.
Runtime owns the resulting logical module lifecycle.
This specification does not require a particular realization contract, process structure, or backend.
Provider status does not decide which realization forms are available or required.

For every locally realized module instance,
including a consumer-only module instance,
the applicable ABI caller MUST:

1. map or bind the accepted implementation and resolve its context-free metadata;
2. construct the structured initialization input and call
   `logos_<module>_init(input, out_context)`; and
3. retain the accepted binding and context in its process-local invocation boundary.

For a direct static or direct dynamic realization,
the applicable ABI caller binds or maps the implementation in the process that performs direct invocation.
For a hosted dynamic realization,
the Module Host maps the accepted implementation and retains the implementation binding and context inside its execution envelope.
That process-local invocation boundary uses the same context for every instance-dependent ABI call for the initialized module instance.
When local Transport applies,
Runtime MUST ensure that the selected endpoint is bound after successful initialization.
Runtime completes contract validation before marking the provider ready.
The invocation boundary schedules independent synchronous `logos_<module>_dispatch(context, ...)`
calls and correlates their Transport responses.
It does not create a per-invocation module context.
On stop, Runtime prevents new calls, drains or fails in-flight work,
releases every transferred output,
and initiates orderly release through the selected realization mechanism.
For every live native context, including a context for a consumer-only module instance,
the applicable ABI caller MUST invoke
`logos_<module>_destroy(context)` exactly once
before discarding the direct binding or stopping the containing execution form.

A consumer-only module does not need a provider endpoint or dispatch loop.
Its realization uses the non-provider handoff and readiness evidence required by its selected profile.
The Runtime implementation obtains concrete realization status
and maps that status and the applicable readiness evidence into the
same logical module lifecycle used for callable modules.

In hosted local Transport mode,
Runtime communicates with the process-local invocation boundary over LOGOS-MODULE-TRANSPORT,
while that boundary executes the native provider through the C ABI defined by LOGOS-MODULE-INTERFACE.
Platform loading and symbol resolution occur inside the provider process, not across the Transport connection.

### 5.2 Single-Process (Mobile / Embedded)

In single-process mode, module implementations may be bound into the process that serves as the Runtime host.
Calls use direct C function pointers with the selected module context.
No serialization or socket is required for those direct calls.

The runtime still manages the registry, lifecycle, and capability validation.
Each successful initialization still creates one distinct context and logical module instance.
Sharing a containing process or implementation binding does not merge their
identity, lifecycle, state, routes, or authority.

### 5.2.1 Singleton Direct-Call Convenience Mode

A runtime implementation MAY define a singleton direct-call convenience mode
for direct mode.
This convenience mode MAY be used with dynamic direct mode or static direct
mode.

In this convenience mode, each module name has at most one live module instance
inside the runtime instance.
Generated typed call helpers MAY omit `logos_route_handle_t*` and route calls
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
- how the Runtime Control binding, route handles, and event publication preserve ordinary direct-mode semantics.

This is a convenience mode.
Code that needs multiple module instances, multiple Runtime instances in one process, Runtime-selected local or remote transport routing, or explicit test isolation SHOULD use handle-based typed call helpers.

### 5.3 Hybrid

Some modules may run in-process, such as small utility modules or providers trusted by the runtime host for a specific deployment.
Others may run in separate processes, such as storage or heavy computation modules.
In-process placement is a trust and containment decision.
It is not a separate module class and it is not created merely because a provider is used as a system service.
Execution mode is not a trust classification.
A direct or in-process provider has same-address-space effects even when it exposes an ordinary module contract.
A local-transport or remote-transport provider has a transport boundary, but that boundary does not by itself prove sandbox strength or authorization.
Routing-selection state (section 4.2) selects candidate providers and invocation
modes per module.

---

## 6. Threading and Concurrency

### 6.1 Module Threading Model

LOGOS-MODULE-INTERFACE Section 2.8 defines the native ABI concurrency contract.
Runtime MAY schedule independent provider calls concurrently within that contract.
It MUST NOT make a worker pool, event loop, fixed entry thread,
or caller-side serialization part of the module ABI.

### 6.2 Provider-Side Local Transport Scheduling

In local Transport mode, the provider-side invocation boundary MAY use an event loop,
a worker pool, or another scheduling mechanism.
Those mechanisms are implementation choices.
For a native hosted provider,
the boundary invokes `logos_<module>_dispatch(context, ...)`
with the context returned for that module instance.

The runtime MUST NOT mark a local-transport-hosted module as `ready` merely
because a local endpoint exists.
The host is ready only after the runtime can connect to that socket and
complete the LOGOS-MODULE-TRANSPORT Hello handshake for the hosted module.
If readiness is not reached before the startup timeout, Runtime MUST move the module instance to `error` and MUST NOT treat the provider or any dependent route as ready.
For a locally realized instance,
Runtime MUST initiate release through the same mechanism that established the realization.
That mechanism owns concrete termination and cleanup of provider-endpoint material that it prepared.
Runtime owns cleanup only for endpoint material that Runtime prepared.

The provider-side invocation boundary MAY schedule independent synchronous dispatch calls separately.
Regardless of its scheduling mechanism,
it MUST correlate each returned result with its originating Transport Request
and serialize Response writes as required by LOGOS-MODULE-TRANSPORT.
Multiple caller connections and provider sessions MAY invoke the same hosted
module context concurrently as permitted by LOGOS-MODULE-INTERFACE Section 2.8.
They remain distinct routes and sessions and do not create additional module instances.

### 6.3 Event Delivery Scheduling

LOGOS-MODULE-INTERFACE Section 2.8 defines direct callback threading,
backpressure, and re-entrancy.
Runtime MUST preserve those semantics
and MUST NOT substitute a Runtime event-delivery thread for direct callback execution.
For transported subscribers,
delivery scheduling is Runtime-internal
but MUST preserve the lifecycle, ordering, and failure behavior defined by LOGOS-MODULE-TRANSPORT.

### 6.4 Direct Mode Concurrency

Direct provider calls execute synchronously on the caller's thread.
Native ABI concurrency follows LOGOS-MODULE-INTERFACE Section 2.8.

---

## 7. Event Loop

### 7.1 Runtime Event Loop

The runtime provides an event loop that:

- Accepts incoming socket connections from local execution forms
- Dispatches incoming CBOR requests to the appropriate module
- Delivers events from modules to subscribers
- Handles module lifecycle transitions (start, stop, crash recovery)

The runtime event loop MAY integrate with an event loop owned by the host
application.
The integration mechanism is framework-specific and not part of this spec.
When no host event loop is provided, the runtime provides its own event loop.

### 7.2 Provider-Side Local Transport Event Loop

The provider-side invocation boundary runs its own event loop:

In the pseudocode below, `schedule_dispatch`, `invoke_module_dispatch`, and `enqueue_framed_response` are illustrative invocation-boundary behavior,
not required exported symbols.
Together, they mean that the boundary decodes the transport request, identifies the requested
schema method, selects the context for the hosted module instance, calls the
module's `logos_<module>_dispatch(context, ...)` entrypoint, and encodes the Transport response.

```
while running:
    msg = read_framed_cbor(socket)
    schedule_dispatch(msg)

dispatch_worker(msg):
    response = invoke_module_dispatch(msg)
    enqueue_framed_response(msg.connection, response)
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

For each subscriber route,
the Runtime-controlled boundary MUST resolve `event_name` under that route's selected contract,
validate `cbor_data` against the exact event-data type,
and compute its payload commitment before delivery.
It MUST NOT deliver an event whose name, payload, or commitment cannot be validated.
Because `logos_publish_fn` has no result channel,
Runtime records that failure as an implementation diagnostic and drops the event.

The runtime delivers a validated event to all authorized subscribers, local or remote.
In local or remote transport mode,
the provider-side Transport boundary or Runtime includes the commitment in each Event message.
In direct mode, Runtime computes and verifies the same roots internally
without changing the subscriber callback payload.
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

The applicable ABI caller supplies `logos_publish_fn` and `publish_user_data` directly in `logos_module_init_input_t`.
There is no post-initialization publish setter.

When the accepted provider call surface declares any event,
the applicable ABI caller MUST supply a non-null publish function before invoking `logos_<module>_init(input, out_context)`.
The module MAY copy the function pointer and `publish_user_data`
into its returned context.
It MUST NOT retain the initialization-input pointer.

`publish_user_data` is opaque, process-local realization state.
The module MUST pass it back unchanged when it calls the publish function.
The module MUST NOT dereference it, compare it for semantic identity,
serialize it, persist it, expose it in schemas,
or send it across a Transport or network boundary.

For a successful initialization,
the publish function and `publish_user_data` remain valid and unchanged from `_init()`
entry until `_destroy(context)` returns.
Publication concurrency follows LOGOS-MODULE-INTERFACE Section 2.8.

### 7.5 Calling Other Modules

A module invokes another module through a ready route established by the Runtime Control `establish_route` method.
The module uses the route's process-local `logos_route_handle_t` with a typed call helper for the selected exact contract.
A declared provider requirement supplies the exact contract and cardinality used to construct the route request, but the declaration does not select a provider or authorize a route.

The Runtime Control binding identifies the calling module instance as consumer.
Every route and outbound call obtained through that binding uses that consumer's authority.
Authorization of an inbound call to the module does not delegate the inbound caller's authority to an outbound call made by the module.
Runtime MUST NOT reuse an inbound route, route ticket, or authority decision as authority for the outbound operation.

For direct mode, the route handle invokes validated provider function pointers without serialization.
For local transport mode, the process-local invocation boundary uses only the invocation material bound to that route and translates typed calls into LOGOS-MODULE-TRANSPORT messages.
For remote transport mode, the route handle uses the authenticated Runtime-to-Runtime path and provider session established for that route.
The typed call helper exposes the same method inputs, outputs, and errors in every mode.

A route handle remains usable only while its route is `ready` and its consumer module context is live.
When the route becomes closed, failed, revoked, or expired, later calls through the handle MUST fail.
Recovery requires another `establish_route` call and produces a new route handle.
The module closes a route through Runtime Control `close_route` and then releases its process-local handle.

Typed calls are synchronous at the call-helper boundary.
Route-handle concurrency and local output ownership follow LOGOS-MODULE-INTERFACE.
Route-establishment failures use the shared invocation-failure status defined by LOGOS-MODULE-INTERFACE Section 4.6.
Schema-defined provider outcomes, including expected failures,
use the selected contract's response schema.
Provider invocation failures use the shared invocation-failure status.
Unknown, hidden, or denied targets use the non-revealing authorization behavior defined in Section 4.

---

## 8. Runtime Module Inputs

Runtime does not define a configuration-file format or a general module-input schema.
When Package Manager supplies a module,
Runtime consumes `logos.package_manager.runtime_handoff` directly.
The authenticated handoff carries the selected installed artifact and the package facts defined by LOGOS-MODULE-PACKAGE-MANAGER.
Runtime MUST preserve its module name, `primary_contract`, `implements`, `requires`, and `requested_permissions` without addition or widening.
For each requested permission,
Runtime uses `permission` and `constraints` as policy inputs.
The explanatory `reason` does not alter the permission identity or constraints and does not grant authority.

When the handoff contains `configuration`,
Runtime MUST validate the declaration according to LOGOS-MODULE-CONFIGURATION before retaining it or accepting a configuration value.
The handoff's artifact hash and hash suite are accepted integrity evidence only because the record came from the authenticated Package Manager system service.
Copying those fields into another record does not preserve that provenance.

Protected bootstrap, static registration, deployment mechanisms, and test harnesses MAY supply equivalent accepted facts through implementation-local inputs.
Their formats are outside this specification.
Those inputs do not grant authority, approve permissions, or define sandbox strength.

Runtime combines accepted external facts with Runtime-owned decisions and state,
including execution mode, provider identity, module instance identity, state assignment, static binding, remote target, realization strategy and placement, and runtime-local options.
This combination is internal Runtime state and does not define another wire schema.
Runtime MUST validate the resulting resolved module record before creating or updating Runtime-owned state.

Before directing realization of an artifact,
Runtime MUST reject an unknown hash suite, an invalid digest length, or a hash mismatch.
Runtime MUST ensure that the selected realization path uses the exact accepted bytes.
Successful hash verification does not authorize execution or any requested permission.

Runtime-local options are interpreted only by the selected deployment profile.
When an implementation-local input encodes those options as CBOR,
Runtime MUST reject non-deterministic CBOR or options not accepted by that profile.
Runtime-local options do not create an untyped field inside a Logos module contract.

`primary_contract` and `implements` in accepted module facts are expected contract facts supplied by the input source.
They do not prove package trust or replace Runtime validation of the selected implementation.
When the runtime can compute or obtain the selected provider's contract identity,
it MUST NOT use an unvalidated `implements` claim to satisfy a provider
requirement.

An accepted input may omit `primary_contract`, `implements`, or both.
When both are absent, the record declares no callable contract,
and Runtime MUST NOT create a provider record merely because it creates the module instance.
Such a module may still declare provider requirements, requested permissions, and persistent-state needs.
When `implements` is present without `primary_contract`,
Runtime validates the selected implementation against every declared interface contract before exposing a provider path.
The `implements`, `requires`, and `requested_permissions` arrays MUST be non-empty when present.
Implemented schema commitments MUST be unique.

`requires` declares provider requirements for the module being registered.
Each requirement names an exact concrete or interface contract and the requested provider-set cardinality.
It does not select a provider or grant authority.

`requested_permissions` contains module-declared policy inputs.
Each `constraints` value contains one Logos deterministic-CBOR value
that conforms to the CDDL owned by the permission's defining specification or profile.
The declarations do not grant authority, approve execution, or prove that the selected execution path can enforce the requested constraints.
Runtime MUST preserve the exact declarations when presenting them to active policy.

When Runtime assigns persistent state to a module instance,
the state assignment is bound to the Runtime-owned module instance identity.
It is Runtime-owned realization context and Runtime Control observation material.
It is not a concrete host path, filesystem grant, storage capability, or cleanup policy.
Runtime MUST resolve the module instance to a stable `module_instance_id` before binding the state assignment or starting the module.
The same module instance identity MAY reuse the same state assignment across stop/start cycles.
Distinct module instances MUST NOT share a state assignment by default.
Shared persistent state requires an explicit deployment or policy rule.
Allocation, reuse across identities, sharing, inspection, retention, deletion, migration, and restoration of concrete state are authority-bearing policy decisions.
This specification does not define their policy language, configuration files, or concrete storage layout.
If Runtime assigns no persistent state, this specification gives the module no persistent-state guarantee.
If a locally realized module instance has a state assignment,
Runtime MUST make it available to the selected realization mechanism before module initialization.
Runtime MUST ensure that the corresponding module-visible state directory is exposed through the applicable realization handoff or fail the realization.
The applicable ABI caller MUST supply the module-visible directory through
`logos_module_init_input_t.state_dir` as defined by LOGOS-MODULE-INTERFACE.
The path does not imply authority to access any host path or another module instance's state.
The realization mechanism MUST preserve the module-instance binding
and MUST NOT use process-global environment as per-instance state.

A provider requirement does not name a provider address.
It describes the contract and provider-set cardinality needed by the module.
Runtime provider selection,
deployment pinning,
visibility filtering,
and authorization happen after providers are registered.
Resolved routes and Runtime Control records carry selected provider addresses.

`cardinality` describes the requested provider set.
`single` requests exactly one matching provider for a route acquisition.
If more than one runtime-visible provider matches and no provider constraint is
supplied, the runtime selects according to local routing-selection state or
deployment configuration.
This specification does not define an ordering among equivalent matching providers.
The selected provider MUST be recorded on the resulting route.
`all-runtime-visible` requests the matching providers visible to the named consumer under active policy.
Runtime MUST obtain an allow decision for the `discover` action under the exact requested contract
before disclosing that provider set through resulting route records.
Runtime establishes one independently authorized ordinary route for each provider it can make ready.
It is not a route-set primitive, and it does not allow one established route to move between providers.
The response's `partial` field is `false` only when every provider visible through that discovery decision
has a returned ready route.
It is `true` when Runtime returns a usable subset because another visible provider
could not be authorized, made ready, or included within the applicable resource limit.
The response does not identify an omitted provider or its failure reason.
A route omitted from the response MUST NOT remain usable for the consumer.
Registry changes after the response do not add providers to or remove providers from the returned routes.
A later request performs discovery and route establishment again.

A `single` request does not enumerate candidates and does not require a separate `discover` decision.
A request that supplies an exact provider also does not enumerate candidates.
The provider identity in a successful route record is disclosure necessary to that authorized route.
If no runtime-visible provider matches a `single` requirement,
route establishment for that requirement fails.
Runtime MUST perform contract validation and an independent authority check for every provider selected by `all-runtime-visible` before its route becomes usable.
Visibility or contract matching alone does not grant route authority.

The accepted module name is the same flat operational module identity for direct static,
direct dynamic, and hosted dynamic realization.
Static or built-in realization does not create a separate module kind.
A built-in or statically linked module uses a protected static binding and does not need a fake artifact record.
For direct mode, Runtime MUST select exactly one accepted dynamic artifact or protected static binding.
It MUST NOT select a remote target.
Runtime MUST select direct placement for that implementation.

For local-transport mode,
Runtime MUST use an accepted artifact for hosted dynamic loading and MUST NOT select a static binding or remote target.
Runtime combines the accepted artifact facts with its placement decision
and realizes the implementation through its selected mechanism.

When Runtime assigns persistent state to a locally realized module instance,
Runtime passes that assignment to the realization mechanism
as context for the same Runtime-owned module instance.
Runtime MUST NOT reinterpret realization fields as authority, package trust, or Runtime lifecycle state.

For remote-transport mode,
Runtime MUST use an accepted remote target and MUST NOT attach a local artifact, static binding, state assignment, or configuration declaration.
The target Runtime owns the remote module instance's accepted configuration declaration and state.

The runtime MUST validate resolved module records before routing calls through
them.
If a record includes `primary_contract` or `implements` expectations,
Runtime MUST apply the exact call-surface checks defined in Section 3.3 before
marking the corresponding provider views ready.
The runtime MUST reject or quarantine malformed resolved module records rather
than creating partially trusted registry entries from them.

This specification does not define package catalogs, install roots,
dependency-graph queries, capability decisions, action prompts, or persistent
configuration storage.
Those belong to higher-layer module-contract specifications, deployment profiles, or runtime-host implementation behavior.
LOGOS-MODULE-SECURITY-CONSIDERATIONS records related threat analysis and
hardening guidance.

### 8.1 Module Initialization Inputs

LOGOS-MODULE-INTERFACE defines the versioned
`logos_module_init_input_t`,
opaque `logos_runtime_control_binding_t`,
and opaque `logos_module_context_t` C ABI types.
For each module instance,
the applicable ABI caller MUST populate the initialization ABI version and structure size,
supply the consumer-bound Runtime Control binding,
supply the state-directory, event-publication, and configuration fields required by LOGOS-MODULE-INTERFACE,
set `*out_context` to null,
and invoke `logos_<module>_init(input, out_context)`.

The Runtime Control binding MUST identify the initialized module instance as consumer.
Each Runtime Control operation invoked through that binding is attributed to that consumer.
Each event emitted through the publish callback is attributed to the initialized module instance as publisher.
Neither path transfers the authority of an inbound caller or another context created from the same implementation binding.
For a successful initialization,
the Runtime Control binding, publish callback, and `publish_user_data` remain valid and unchanged from `_init()` entry until `_destroy(context)` returns.

The initialization input is borrowed only for the duration of `_init()`.
The module may copy the Runtime Control binding and event-publication fields into its returned context but
MUST NOT retain the initialization-input pointer.
The applicable ABI caller MUST reject any result/context combination that violates LOGOS-MODULE-INTERFACE.
Runtime MUST treat the reported rejection or a module's ABI-version or structure-size
rejection as an initialization failure.
A failed initialization does not create a live module instance context and
MUST NOT expose provider views or transition the module instance to `ready`.
When `_init()` returns failure with a null context,
the applicable ABI caller MUST NOT invoke `_destroy(context)` for that failed initialization.
Instead, the module is responsible for releasing its partial initialization
state before returning the failure.

Each successful initialization of one accepted implementation binding creates
a distinct context and module instance lifetime.
Initialization and provider-entry concurrency follow LOGOS-MODULE-INTERFACE Section 2.8.
Runtime MUST NOT initiate release while another instance-dependent call is in flight.
Before destruction, Runtime MUST prevent new calls through that context,
drain or fail in-flight work,
and release every transferred module-owned output.
It then initiates graceful release through the selected realization mechanism.
The applicable ABI caller MUST invoke `_destroy(context)` exactly once before discarding the direct binding or stopping the containing execution form.

The initialization input carries the Runtime Control binding,
event-publication fields,
optional module-visible state directory,
and optional schema-typed module configuration.
Runtime selects and snapshots the startup record according to LOGOS-MODULE-CONFIGURATION and supplies the resulting `configuration_input` through the selected realization mechanism.
A module instance without a configuration-schema binding receives the Interface absent representation.

Runtime-local options are not module initialization fields unless a deployment profile explicitly defines how a module observes them.
Runtime host directories, profile selection, concrete realization backends, and system service provider binding are deployment or security-profile inputs.

---

## 9. Runtime-Control Interface

The Runtime owns module lifecycle machinery.
This specification defines Runtime Control as an intrinsic contract surface of each Runtime instance.
Runtime Control exposes Runtime-owned lifecycle and observation operations through the same CDDL-defined contract model as module-provided contracts.
Runtime MUST accept a Runtime Control invocation only from an authenticated module instance.
Runtime derives the consumer from that authenticated invocation context.

One program may both host a Runtime instance and contain admitted module implementations.
The Runtime engine and those module instances remain distinct implementation and participant roles.
Every Runtime Control invocation from such an implementation is attributed to the authenticated calling module and uses that module instance’s authority.

The runtime-control surface operates on runtime-known module records.
It does not define package catalogs, install roots, dependency graph
resolution, capability decisions, concrete module realization mechanics, or UI
state.
Those remain higher-layer module-contract specifications, deployment profiles, or runtime-host implementation behavior.

Runtime Control methods are privileged operations.
Runtime MUST authorize the consumer and requested method, target, and observation scope according to active policy before executing an operation.
Availability of a Runtime Control binding or endpoint grants no authority by itself.

Runtime authority is configuration and policy, enforced by the runtime
instance.
A runtime instance MUST have an authority policy for runtime-control
operations, route establishment, system service access, provider visibility, lifecycle control, and remote-runtime enrollment.
The authority policy may be internal to the runtime for local trusted
deployments or externalized through a `logos_capability_authority` provider that active policy binds for that responsibility.
Before Runtime binds an initial system service provider, Runtime MUST have bootstrap authority policy established by its runtime host or deployment inputs.
Bootstrap policy MAY identify initial system service providers and grant only the operations needed to validate and reach those providers.
A candidate provider MUST NOT select, bind, or authorize itself as an authority-bearing system service.
Runtime MUST authorize each initial system service binding from bootstrap policy rather than from the candidate provider or another provider that is not yet bound.

Before Runtime uses a provider as a system service, it MUST confirm that:

- the provider is a local provider backed by a local module instance;
- the module instance is ready under its selected execution mode;
- the provider exposes the module contract required for that responsibility;
- the invocation path is usable with the authority granted for that binding.

For a local-transport system service provider, readiness includes completing the Transport Hello exchange for the required module contract.
Runtime MUST NOT use the provider for dependent operations until all binding checks succeed.
The same readiness, contract, invocation-path, and authority checks apply when active policy replaces a system service binding after bootstrap.

Bootstrap policy does not authorize ordinary module routes, method calls, provider visibility, lifecycle control, or remote access unless it explicitly grants that operation.
If an external Capability Authority is unavailable, Runtime MUST deny operations that depend on it unless bootstrap policy defines a narrower recovery path.
Protected Runtime inputs, static registration, deployment configuration, and embedded runtime-host wiring may carry these bootstrap inputs, but they do not bypass runtime enforcement.
If no authority policy allows an operation, the runtime MUST deny the
operation.

Protected construction and deployment inputs may establish bootstrap policy and initial system-service bindings.
They are Runtime implementation inputs rather than consumer authority.
A module has only the operations granted to its module instance by active policy.
Module identity, implementation, provided contracts, and placement grant no Runtime Control authority, route authority, system-service access, or provider visibility by themselves.

For authority-policy evaluation, Runtime MUST authenticate the consumer at the enforcement boundary
and represent that consumer with `module_instance_address`.
Runtime MAY derive policy attributes from authenticated context.
Those attributes are policy inputs, not additional identities or authority by themselves.

Transport authentication, schema compatibility, runtime instance ids, module
names, provider ids, package identity, and successful connection establishment
are authority-policy inputs.
They are not authority by themselves.

LOGOS-MODULE-RUNTIME does not define a generic capability token,
policy language, or security trust-store format.
A runtime consumes authority decisions from its authority policy.
When authority policy is externalized through Capability Authority,
that contract defines decisions, grants, denials, revocation, audit records, and commitment requirements.
The applicable Transport profile defines route authorization material.
LOGOS-MODULE-CAPABILITY-AUTHORITY defines the baseline call-evidence container;
another selected security profile may define additional evidence requirements or formats.
The runtime treats those values as authority inputs and decision outputs and
enforces the resulting decisions at the runtime-control, route,
lifecycle-control, provider-visibility, system-service, and remote-facade
boundaries defined here.
Remote runtime-control access requires authority accepted by the runtime that
exposes the Runtime Control endpoint.

Runtime MUST populate or validate the Capability Authority request's `consumer`
against the module instance authenticated for the attempted operation.
Runtime MUST reject a returned decision whose consumer does not match the request.

The following operations require an allow decision from runtime authority
policy:

- invoking any Runtime Control method;
- observing Runtime Control state that is not visible to ordinary modules;
- starting, stopping, or otherwise controlling module lifecycle;
- using a system service provider;
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

An authorization denial is an explicit deny result from runtime authority policy.
An authority-evaluation failure occurs when Runtime cannot obtain or validate a required authority decision.
Runtime MUST fail closed for the attempted operation, but it MUST NOT record an authority-evaluation failure as an explicit policy denial unless policy returned a deny result.
The caller-facing error may remain an authorization failure, but retained observation or audit material MUST distinguish denial from evaluation failure.

Runtime owns enforcement of the authority result and its mapping to method, Transport, Runtime Control, and runtime API error channels.
LOGOS-MODULE-CAPABILITY-AUTHORITY owns authority-decision and denial-reason records when authority policy is externalized through that contract.
It also owns the baseline call-evidence container.
Selected security profiles own only additional audit requirements or evidence formats.
System-service operational errors MUST NOT be treated as authority decisions or denial reasons.

The runtime MUST retain enough authority-decision material to explain
allow/deny enforcement through Runtime Control observation or implementation
audit logs.
That material SHOULD include the consumer reference, the attempted operation,
the target provider or route when present, and the decision identifier when present.

Runtime MUST compute every request and successful-response payload commitment
at the Runtime-controlled invocation boundary,
independently of whether authority policy requires audit retention.
It MUST bind each root to the selected route, provider, contract, method declaration,
and exact request or response type for that call.
Direct per-method invocation, generic dispatch, and Transport use the same commitment semantics.

When the decision requires retention,
Runtime MUST produce the `call` audit record defined by LOGOS-MODULE-CAPABILITY-AUTHORITY.
It MUST derive each retained request or response commitment from the schema-typed value at the enforcement boundary,
not from an unverified root or contract identifier supplied by the provider or consumer.
Computing these roots does not require retaining the payload or audit record
when no applicable retention requirement exists.

Remote runtime enrollment is an authority-policy decision that makes a remote
runtime eligible for remote runtime-control access, remote-module facade
creation, or remote route establishment.
Enrollment does not by itself authorize any concrete runtime-control method,
module lifecycle operation, provider visibility, or ordinary module route.
Each such operation still requires its own allow decision from runtime authority
policy.
If a remote runtime is not enrolled or otherwise accepted by authority policy,
the local runtime MUST NOT use it for remote-module facades or remote routes.

When a target Runtime accepts an operation forwarded by an enrolled source Runtime,
the source Runtime MUST identify the module instance that it authenticated locally as the consumer.
The target Runtime MUST verify that the consumer reference's `runtime_instance_id`
matches the authenticated source Runtime identity and that active policy permits
that Runtime to forward operations for consumers it owns.
The target Runtime then authorizes the requested operation for the consumer.
The authenticated source Runtime identity establishes provenance for the consumer assertion but does not make the source Runtime the consumer.
The consumer reference does not independently authenticate the module instance.
Acceptance trusts the enrolled source Runtime to authenticate module instances it owns.
No additional per-module remote credential is required by this revision.

Runtime-to-Runtime coordination that is not performed for a module is an internal protocol concern.
It MUST NOT be represented using a fabricated consumer reference.

### 9.1 Concurrent Runtime Control Operations

Runtime MUST authenticate and authorize every Runtime Control invocation independently for its consumer before applying a state mutation.
Concurrent invocations from the same or different consumers MUST NOT share consumer identity, authority decisions, or request-key scope.

Runtime MUST apply mutations that affect the same module instance, route, listener, or provider export in one total order.
That order MUST respect completion order when one invocation completes before another begins.
Each mutation MUST observe the complete result of earlier mutations in that order and MUST change its target atomically.
Operations on independent targets MAY proceed concurrently.

Concurrent lifecycle requests MUST NOT create duplicate realizations, native contexts, destruction calls, or release operations.
A `start_module` request for an instance in `loaded` or `ready` MUST return its current module state and MUST NOT create another realization.
A `stop_module` request for an instance in `stopping` or `unloaded` MUST return its current module state and MUST NOT initiate another destruction or release.
If `stop_module` is ordered after an incomplete start,
Runtime MUST prevent that start from later making the instance `ready`.
If `start_module` is ordered while the instance is `stopping`,
it MUST fail and MUST NOT schedule an implicit restart.

Route mutations follow the same per-route order.
Once `close_route`, failure, or revocation places a route in a terminal state,
a later renewal MUST fail and MUST NOT revive it.
A renewal ordered before closure may complete,
but the later closure remains terminal.

An observation concurrent with a mutation MAY report the complete state before or after that mutation.
It MUST NOT combine fields from different versions of the same record.
Runtime MUST emit lifecycle and route-state events for one target in the same order as the corresponding committed state transitions.

### 9.2 Shared Runtime Types

The following CDDL is the `logos.runtime` supporting schema:

```cddl
logos.runtime.module_name = tstr .size (1..64)
logos.runtime.runtime_instance_id = tstr .size (1..128)
logos.runtime.module_instance_id = tstr .size (1..128)
logos.runtime.module_provider_id = tstr .size (1..128)
logos.runtime.route_id = tstr .size (1..128)
logos.runtime.module_state_assignment_id = tstr .size (1..128)

logos.runtime.module_instance_address = {
    runtime_instance_id: logos.runtime.runtime_instance_id,
    module_instance_id: logos.runtime.module_instance_id,
}

logos.runtime.module_provider_address = {
    ? runtime_instance_id: logos.runtime.runtime_instance_id,
    provider: logos.runtime.module_provider_id,
}
```

`logos_runtime_types.cddl` is an extracted machine-readable mirror of this block.
If the extracted artifact differs from this specification, this specification governs.

This is a supporting schema because it defines shared non-callable Runtime identities and addresses used by multiple module contracts.
It defines no methods, events, provider surface, module identity, or lifecycle.
Keeping these types separate from Runtime Control gives them one schema identity without making them a callable service or adding them to the pinned Logos common schema.
This specification owns their semantics.
Importing one of these types does not create a Runtime instance, module instance, provider, route, or authority.
The complete supporting schema has its own schema root,
and each imported declaration retains its schema subtree root within that schema.

### 9.3 Runtime-Control Module Contract

The runtime-control interface is a Logos-defined module contract intrinsically exposed by each Runtime instance.
Its flat runtime module name is `logos_runtime_control`.
Its schema namespace is `logos.runtime_control`.
The CDDL in this section defines the normative machine-readable contract.
`logos_runtime_control.cddl` is an extracted machine-readable mirror.
If the extracted artifact differs from this specification, this specification governs.
Because both names are Logos-defined, they are allowed uses of the reserved
`logos_` and `logos.` namespaces.

The Runtime Control module schema imports two supporting schemas: shared Runtime Types from Section 9.2 and Module Configuration Types from LOGOS-MODULE-CONFIGURATION.
It uses the following Runtime and Runtime Control addressing objects:

| Object | Purpose | Format | Scope |
|--------|---------|--------|-------|
| `module_name` | Flat operational runtime module name used for realization and routing. | `tstr .size (1..64)` | Runtime module namespace. |
| `runtime_instance_id` | Opaque identity for a concrete runtime instance. | `tstr .size (1..128)` | Addressing scope that uses the runtime instance. |
| `runtime_address` | Locator for opening a transport connection to a Runtime-controlled endpoint. | Transport-specific record. | Network, host, namespace, or deployment profile. |
| `runtime_endpoint` | Optional pairing of runtime identity and runtime locator. | `{ ? runtime_instance_id, address }` | Runtime-control records that need both identity context and reachability. |
| `module_provider_id` | Opaque identity for a runtime-known module provider. | `tstr .size (1..128)` | Runtime instance that owns the provider record. |
| `module_provider_address` | Address of a provider record inside a runtime instance. | `{ ? runtime_instance_id, provider }` | Runtime-control records that refer to a provider. |
| `module_instance_id` | Opaque identity for a runtime-known module instance. | `tstr .size (1..128)` | Runtime or provider scope that owns the module instance. |
| `module_instance_address` | Address of an existing module instance. | `{ runtime_instance_id, module_instance_id }` | Runtime instance that owns the module instance. |
| `module_state_assignment_id` | Opaque persistent-state assignment identity bound to a module instance. | `tstr .size (1..128)` | Runtime instance and deployment policy. |

```cddl
; -- metadata --
_module = "logos_runtime_control"

logos.runtime_control.reason = tstr .size (0..512)
logos.runtime_control.address_profile = tstr .size (1..128)
logos.runtime_control.decision_id = tstr .size (1..128)
logos.runtime_control.failure_code = tstr .size (1..64)
logos.runtime_control.host_name = tstr .size (1..255)
logos.runtime_control.port = uint16
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
    logos.runtime_control.tls_tcp_runtime_address /
    logos.runtime_control.quic_runtime_address

logos.runtime_control.runtime_endpoint = {
    ? runtime_instance_id: logos.runtime.runtime_instance_id,
    address: logos.runtime_control.runtime_address,
}

logos.runtime_control.remote_identity_profile =
    "logos.remote.tls-tcp" /
    "logos.remote.quic"

logos.runtime_control.trust_anchor_id = bstr .size (1..128)
logos.runtime_control.subject_public_key_info = bstr .size (1..8192)

logos.runtime_control.remote_runtime_enrollment =
    {
        runtime_instance_id: logos.runtime.runtime_instance_id,
        profile: logos.runtime_control.remote_identity_profile,
        revision: uint64,
        status: "active",
        trust_anchor: logos.runtime_control.trust_anchor_id,
        subject_public_keys: [logos.runtime_control.subject_public_key_info] /
                             [logos.runtime_control.subject_public_key_info,
                              logos.runtime_control.subject_public_key_info],
    } /
    {
        runtime_instance_id: logos.runtime.runtime_instance_id,
        profile: logos.runtime_control.remote_identity_profile,
        revision: uint64,
        status: "revoked",
    }

logos.runtime_control.remote_listener_address =
    logos.runtime_control.tls_tcp_runtime_address /
    logos.runtime_control.quic_runtime_address

logos.runtime_control.remote_listener_record = {
    address: logos.runtime_control.remote_listener_address,
    enabled: bool,
    runtime_control_enabled: bool,
}

logos.runtime_control.provider_export_record = {
    listener: logos.runtime_control.remote_listener_address,
    provider: logos.runtime.module_provider_address,
    enabled: bool,
}

logos.runtime_control.remote_provider_target = {
    runtime: logos.runtime_control.runtime_endpoint,
    ? provider: logos.runtime.module_provider_id,
    ? module: logos.runtime.module_name,
}

logos.runtime_control.module_record = {
    module: logos.runtime.module_name,
    ? provider: logos.runtime.module_provider_address,
    ? remote: logos.runtime_control.remote_provider_target,
    ? instance: logos.runtime.module_instance_id,
    ? state_assignment: logos.runtime.module_state_assignment_id,
    state: logos.runtime_control.state,
    mode: logos.runtime_control.mode,
    ? primary_contract: logos.schema_commitment,
    ? implements: [* logos.schema_commitment],
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.invocation_descriptor =
    {
        kind: "local-transport",
        profile: "logos.local.unix-stream",
        path: logos.runtime_control.path,
        ticket: bstr .size 32,
    } /
    {
        kind: "remote-transport",
        runtime: logos.runtime.runtime_instance_id,
        provider: logos.runtime.module_provider_id,
        endpoint: logos.runtime_control.remote_listener_address,
        ticket: bstr .size 32,
    }

logos.runtime_control.route_failure = {
    code: logos.runtime_control.failure_code,
    ? message: logos.runtime_control.reason,
}

logos.runtime_control.route_access = {
    ? methods: [* bstr .size 32],
    ? publish_events: [* bstr .size 32],
    ? subscribe_events: [* bstr .size 32],
}

logos.runtime_control.provider_requirement_cardinality =
    "single" /
    "all-runtime-visible"

logos.runtime_control.route_record = {
    route: logos.runtime.route_id,
    consumer: logos.runtime.module_instance_address,
    target_provider: logos.runtime.module_provider_address,
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
    ? expected_contract: logos.schema_commitment,
    access: logos.runtime_control.route_access,
    state: logos.runtime_control.route_state,
    ? invocation: logos.runtime_control.invocation_descriptor,
    ? decision_id: logos.runtime_control.decision_id,
    ? expires_at: uint64,
    ? failure: logos.runtime_control.route_failure,
}

logos.runtime_control.establish_route_request = {
    request_key: tstr .size (1..128),
    contract: logos.schema_commitment,
    cardinality: logos.runtime_control.provider_requirement_cardinality,
    ? provider: logos.runtime.module_provider_address,
    access: logos.runtime_control.route_access,
}

logos.runtime_control.establish_route_response = {
    routes: [* logos.runtime_control.route_record],
    partial: bool,
}

logos.runtime_control.renew_route_request = {
    request_key: tstr .size (1..128),
    route: logos.runtime.route_id,
}

logos.runtime_control.renew_route_response = {
    route: logos.runtime_control.route_record,
}

logos.runtime_control.list_modules_request = {}

logos.runtime_control.list_modules_response = {
    modules: [* logos.runtime_control.module_record],
    partial: bool,
}

logos.runtime_control.list_routes_request = {
    ? module: logos.runtime.module_name,
    ? provider: logos.runtime.module_provider_address,
}

logos.runtime_control.list_routes_response = {
    routes: [* logos.runtime_control.route_record],
    partial: bool,
}

logos.runtime_control.list_remote_listeners_request = {}

logos.runtime_control.list_remote_listeners_response = {
    listeners: [* logos.runtime_control.remote_listener_record],
    partial: bool,
}

logos.runtime_control.set_remote_listener_request = {
    listener: logos.runtime_control.remote_listener_record,
}

logos.runtime_control.set_remote_listener_response = {
    listener: logos.runtime_control.remote_listener_record,
}

logos.runtime_control.list_provider_exports_request = {
    ? listener: logos.runtime_control.remote_listener_address,
    ? provider: logos.runtime.module_provider_address,
}

logos.runtime_control.list_provider_exports_response = {
    exports: [* logos.runtime_control.provider_export_record],
    partial: bool,
}

logos.runtime_control.set_provider_export_request = {
    export: logos.runtime_control.provider_export_record,
}

logos.runtime_control.set_provider_export_response = {
    export: logos.runtime_control.provider_export_record,
}

logos.runtime_control.close_route_request = {
    route: logos.runtime.route_id,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.close_route_response = {
    route: logos.runtime.route_id,
    state: logos.runtime_control.route_state,
}

logos.runtime_control.start_module_request = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
}

logos.runtime_control.start_module_response = {
    module: logos.runtime.module_name,
    instance: logos.runtime.module_instance_id,
    state: logos.runtime_control.state,
}

logos.runtime_control.stop_module_request = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
}

logos.runtime_control.stop_module_response = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
    state: logos.runtime_control.state,
}

logos.runtime_control.get_readiness_request = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
}

logos.runtime_control.get_readiness_response = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
    state: logos.runtime_control.state,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.get_configuration_schema_request = {
    target: logos.runtime.module_instance_address,
}

logos.runtime_control.get_configuration_schema_response = {
    target: logos.runtime.module_instance_address,
    state_revision: uint64,
    schema: logos.module_configuration.schema_binding,
}

logos.runtime_control.get_configuration_request = {
    target: logos.runtime.module_instance_address,
}

logos.runtime_control.get_configuration_response = {
    target: logos.runtime.module_instance_address,
    state: logos.module_configuration.configuration_state,
}

logos.runtime_control.update_configuration_request =
    {
        target: logos.runtime.module_instance_address,
        expected_state_revision: uint64,
        expected_schema_commitment: logos.module_configuration.schema_commitment,
        action: "stage",
        value: logos.module_configuration.configuration_value,
    } /
    {
        target: logos.runtime.module_instance_address,
        expected_state_revision: uint64,
        expected_schema_commitment: logos.module_configuration.schema_commitment,
        action: "discard",
    }

logos.runtime_control.update_configuration_response = {
    target: logos.runtime.module_instance_address,
    state_revision: uint64,
    ? staged: logos.module_configuration.value_record,
}

logos.runtime_control.apply_configuration_request = {
    target: logos.runtime.module_instance_address,
    expected_state_revision: uint64,
}

logos.runtime_control.apply_configuration_response = {
    target: logos.runtime.module_instance_address,
    state_revision: uint64,
    applied_value_revision: uint64,
}

logos.runtime_control.configuration_state_changed_event = {
    target: logos.runtime.module_instance_address,
    state: logos.module_configuration.configuration_state_summary,
}

logos.runtime_control.module_state_changed_event = {
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
    old_state: logos.runtime_control.state,
    new_state: logos.runtime_control.state,
    ? reason: logos.runtime_control.reason,
}

logos.runtime_control.route_state_changed_event = {
    route: logos.runtime.route_id,
    old_state: logos.runtime_control.route_state,
    new_state: logos.runtime_control.route_state,
    ? module: logos.runtime.module_name,
    ? provider: logos.runtime.module_provider_address,
    ? reason: logos.runtime_control.reason,
}
```

Runtime-control methods use the ordinary Logos method error channel defined by
LOGOS-MODULE-INTERFACE.
Method-specific failure conditions are described with each method.

`expected_contract` carries a `logos.schema_commitment` for a complete selected callable contract, whereas `expected_schema_commitment` carries a `logos.module_configuration.schema_commitment` for a complete configuration schema document and its selected configuration root; the two record shapes MUST NOT be substituted for one another.

The four configuration methods and `configuration_state_changed_event` reference the canonical types owned by LOGOS-MODULE-CONFIGURATION.
Their method and event identities belong to the Runtime Control schema root, while the referenced configuration types retain their own schema identities and semantics.
Runtime MUST implement those methods and the event according to LOGOS-MODULE-CONFIGURATION, including its authorization, concurrency, startup, live-reconfiguration, state-transition, and failure requirements.

For every configuration request, `target.runtime_instance_id` MUST identify the Runtime instance exposing the invoked Runtime Control contract.
Runtime MUST reject a target owned by another Runtime rather than forwarding the operation or substituting a local facade instance.

`runtime_instance_id` identifies the runtime instance exposing the
runtime-control interface.
It is distinct from `module_instance_id`, which identifies a runtime-known module
instance managed by that runtime.

`module_instance_id` identifies a runtime-known module instance owned by a runtime
instance.
It is opaque and scoped to the runtime instance that owns the module lifecycle
record.
The same `module_instance_id` MAY be reused across stop/start cycles when the runtime host or deployment preserves that instance identity.
When a module has persistent state, the state assignment is bound to this module instance identity.
It is lifecycle identity, not module contract identity, provider identity,
package identity, schema identity, authorization identity, route identity, or
transport reachability.

`module_state_assignment_id` identifies an abstract persistent-state assignment visible through Runtime Control.
It is observation and realization-context material, not a concrete host path.
It is not a storage grant, cleanup decision, or right to inspect or modify persistent state.
Runtime makes this assignment available to the selected realization mechanism
when realizing a local module instance.
That mechanism owns its concrete state-directory handoff.

Multiple runtime-known instances of the same flat runtime module name MAY exist in one
runtime instance.
When a runtime-control record carries both `module` and `instance`, the
`instance` field disambiguates the lifecycle target for that module name.
If a provider is not bound to a local module instance, the provider record
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

For `logos.remote.tls-tcp` and `logos.remote.quic`,
the Runtime identity MUST be a lowercase canonical UUID version 4 string generated according to RFC 9562.
The runtime host or authorized provisioning system generates it once and preserves it
for the lifetime of that logical Runtime identity.
It is not derived from a certificate or public key,
so certificate and key rotation do not change the Runtime identity.
Assigning a new Runtime identity requires a new enrollment.

`remote_runtime_enrollment` binds that stable Runtime identity to the TLS public keys accepted for one remote identity profile.
It is a provisioning and Runtime input record,
not a new Runtime Control method or a record disclosed to ordinary modules.
`trust_anchor` is an identifier looked up in protected trust input;
the identifier does not establish trust by itself.
Each `subject_public_keys` item is the exact DER encoding
of the X.509 `SubjectPublicKeyInfo` structure defined by RFC 5280.
An ordinary module, remote peer, package, catalog, or presented certificate
MUST NOT create or alter an accepted enrollment.
Runtime accepts enrollment changes only through protected deployment input
or an authorized provisioning operation.

The enrollment key is the pair of `runtime_instance_id` and `profile`.
A higher revision replaces a lower revision for that key.
A lower revision is stale and MUST NOT replace the current record.
Two different records with the same key and revision conflict;
Runtime MUST reject that remote identity until authorized provisioning resolves the conflict.
A `revoked` record supersedes lower active revisions and permits no new or existing authenticated session.

Public-key rotation uses a higher active revision containing both old and new keys during overlap.
A later higher revision removes the old key.
Replacing a certificate without changing its public key does not require an enrollment revision,
provided certificate and trust-anchor validation still succeeds.
The baseline uses one Runtime credential for the Runtime identity;
ordinary modules and providers do not receive separate long-lived certificates.

Enrollment revision checks prevent rollback only relative to the newest accepted state retained by Runtime.
If a remote identity profile obtains enrollment records through a transparency log,
consensus system, catalog, or other external source,
that profile MUST bind the exact enrollment key, revision, status, and contents
to a trust root or checkpoint supplied through protected trust input.
External inclusion or consensus does not by itself authorize Runtime Control or provider access.

The baseline remote identity profiles do not require an external log or consensus system.
Protected local provisioning of trust anchors and enrollment records is sufficient.
After loss of the newest accepted enrollment state,
Runtime MUST re-establish it from protected trust input or a profile-defined trusted checkpoint
before accepting a remote identity whose rollback status cannot otherwise be determined.

`runtime_address` describes how to open a transport connection to a Runtime-controlled endpoint.
A Runtime-controlled endpoint can expose Runtime Control, ordinary provider traffic, or both.
The address alone does not indicate which logical endpoints are enabled.
It is a locator, not the runtime identity, trust policy, schema identity,
authorization grant, package identity, module identity, or route state.

This specification defines three runtime address transports:

- `unix-stream`, a local stream endpoint addressed by filesystem path;
- `tls-tcp`, a TLS-protected stream endpoint addressed by host and port;
- `quic`, a QUIC endpoint addressed by host and port.

`unix-stream` addresses MUST contain `path` and MUST NOT contain `host`,
`port`, `server_name`, or `alpn`.
`tls-tcp` addresses MUST contain `host` and `port`, MUST NOT contain `path`,
and MAY contain `server_name`.
`quic` addresses MUST contain `host` and `port`, MUST NOT contain `path`, and
MAY contain `server_name` and `alpn`.
If a QUIC deployment profile requires a specific ALPN value, the address MUST
carry that value or the profile MUST define how the value is supplied.

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

Runtime owns `remote_listener_record` and `provider_export_record` state.
The complete listener address identifies a listener;
this specification does not define a separate listener identifier.
The listener address and provider address together identify a provider export;
this specification does not define a separate export identifier.

`enabled` controls whether Runtime accepts new remote connections at the listener.
`runtime_control_enabled` has effect only while the listener is enabled.
It permits the Runtime Control logical endpoint to be reached,
but does not authorize any Runtime Control operation.

An enabled provider export permits remote sessions for only its selected provider.
It has effect only while its listener is enabled.
The exported provider MUST be owned by the Runtime that owns the export record.
Export state does not select a contract or grant provider access;
those remain properties of route establishment and authorization.

Runtime Control and ordinary provider traffic remain independently enabled.
An implementation may serve them at the same network address.
The selected transport profile MUST separate their logical endpoints deterministically.
Runtime MUST reject traffic that cannot be assigned unambiguously before dispatch.

A remote runtime-control surface is exposed as the `logos_runtime_control`
Logos endpoint over LOGOS-MODULE-TRANSPORT.
The Transport Hello `module` field identifies that endpoint as
`logos_runtime_control`.
The Transport Hello `schema` field carries the structural schema identity of
the Runtime Control contract selected for that endpoint.
Both peers MUST use that same selected contract as required by LOGOS-MODULE-TRANSPORT.
This specification does not define a separate remote-runtime identity
handshake.
Runtime identity remains the opaque `runtime_instance_id` carried in Runtime
Control records and interpreted under deployment or enrollment policy.
A successful Transport Hello for `logos_runtime_control` proves only that the
peer presented a compatible Runtime Control endpoint schema under the selected
transport policy.
It does not by itself authorize runtime-control operations or ordinary module
routes.

Remote provider access requires three independent conditions:

- an active Runtime-controlled remote listener;
- an explicit export of the selected provider through that listener;
- an allow decision for the authenticated consumer and requested provider access.

No condition implies either of the others.
A listener MUST NOT make every provider remotely available.
A provider export MUST NOT authorize a consumer or create a route.
An allow decision MUST NOT activate a listener or export a provider.
For a request forwarded by an authenticated and enrolled source Runtime, provider discovery through a listener includes only providers with an enabled export through that listener whose disclosure is allowed for the identified consumer and exact contract.
Runtime MUST NOT disclose unexported or disclosure-denied local providers through remote discovery.

Remote listeners and provider exports MUST be disabled by default.
Deployment configuration or authorized Runtime Control may explicitly enable them.
Runtime MUST NOT accept a remote provider session until all three conditions hold.
Runtime MUST also redeem the route ticket
at the provider endpoint before accepting the session.

The provider endpoint is controlled by Runtime.
It has no separate identity, lifecycle, or Runtime Control record.
It authenticates as the target Runtime under the selected remote security profile.
Runtime Control establishes the route and returns its invocation descriptor;
it does not carry ordinary provider calls.

A listener may serve multiple exported providers.
Before dispatching any ordinary module message,
Runtime MUST bind the accepted session to exactly one route and selected provider
through the redeemed ticket.
The session MUST NOT switch to another provider or route.
A caller that requires another provider or route must establish another session.

Runtime dispatches authorized messages to the selected provider
through its protected local invocation path.
Runtime MUST enforce the route's method and event access at the provider-side endpoint
and react to expiry or revocation as required by LOGOS-MODULE-TRANSPORT.
The mandatory remote profile MUST NOT expose an individual module process or container
in a way that bypasses this enforcement boundary.

Exporting a provider does not change its module instance or lifecycle owner.
It does not change provider identity or system-service status.
A remote-module facade does not become a local realization of a system service.
This remains true regardless of which module contract the facade exposes.

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

A module provider address MAY identify a provider backed by a local module instance or a remote module facade in the local Runtime registry.
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

The flat runtime module name, module instance id, execution mode, contract
commitments, transport endpoint, and remote-facade targeting
metadata are descriptive facts about provider records or routes.
They are intentionally not part of `module_provider_address`.

When a `module_record` includes `provider`, the field identifies the
runtime-known provider that currently satisfies or is expected to satisfy the
record's module contract.
The `module` field remains the flat operational runtime module name.
The `provider` field is not a substitute for the module name, and the module
name is not a provider address.

Module contract identity is represented by contract fields on runtime records,
not by a separate address object.
Each contract field is a `logos.schema_commitment`.
Its schema root commits to the complete schema, including its namespace, so Runtime Control does not carry a separate namespace wrapper.
The flat runtime `module` name is the operational name used for realization and routing.
`primary_contract` is the resolved concrete module contract when the runtime
knows the exact schema root.
`implements` lists resolved interface contracts implemented by that concrete
module contract when the runtime reports them.
If `implements` is absent, the runtime is not reporting implemented-interface
metadata; absence does not assert that the module implements no interfaces.
These fields are runtime observations or expectations derived from contract
resolution.
They are not package-manager requirements and are not a source of method
dispatch semantics.

On a `route_record`, `expected_contract` names the exact concrete module
contract or implemented interface contract that the route was established to
satisfy.
It is validation, diagnostics, and audit context.
Route records use `expected_contract` as the selected contract identity.
It is not a method dispatch selector; ordinary module calls still carry the
bare method name as defined by Module Interface and Transport.
If it is the provider's primary concrete contract, the route exposes only that primary contract.
If it is an implemented interface contract, the route exposes only that exact interface contract.
Calls to methods outside the selected contract are not valid on that route.

Runtime addresses, module provider addresses, and module instance ids do not
prove module contract compatibility.
A runtime that connects to or selects a provider MUST validate the expected module contract using the relevant schema commitment and the Transport Hello schema commitment where Transport is used.

A route is the runtime-authorized binding between a consumer and a selected
provider invocation path.
The `consumer` field on a `route_record` identifies the consumer whose authority the route represents.
It may refer to runtime addresses, provider addresses, module instance
identities, authorization material, and transport connections, but it does not
replace them.

Runtime Control establishes and manages routes; it is not the ordinary module
invocation protocol.
After establishment, ordinary transported calls use the route's `invocation_descriptor`,
which identifies a local or remote transport invocation path.

The mandatory local descriptor uses `logos.local.unix-stream`.
It carries the Unix-domain-socket path and one-time 32-byte route ticket directly.
It does not contain an opaque nested descriptor.
Direct-mode callers obtain a process-local `logos_route_handle_t` from the language binding and do not serialize that handle into Runtime Control.

A remote-transport invocation directly identifies the expected target Runtime,
the selected remote provider, the provider-side listener,
and the one-time route ticket.
It does not contain another encoded descriptor.

`runtime` is the Runtime identity that the caller MUST authenticate at `endpoint`.
`provider` is scoped to that Runtime and identifies the selected remote provider.
The endpoint's `profile` field MUST be present
and selects the remote transport and security profile.
`ticket` MUST be non-empty.
The caller carries it in the first Transport Hello as `token`
and MUST NOT reuse it for another connection.

For a ready remote route returned by `establish_route` or `renew_route`,
the enclosing `route_record` MUST contain `expected_contract` and `expires_at`.
Its consumer, provider, module, contract, access, route, and expiry
define the authorization and session constraints for the invocation.
The caller MUST reject the invocation
if the endpoint profile is unsupported
or the authenticated target Runtime does not match `runtime`.
Runtime MUST bind the ticket to those route fields
and to the authenticated transport channel
using the selected remote profile's channel-binding procedure.
For a remote route, this binds the authenticated Runtime identity and selected remote provider
to the route's expected contract, allowed method and event roots, authority decision, and expiry.

The `route_record` CDDL defines the representation used when routes are exposed, committed, audited, or exchanged through Runtime Control.
Implementations are not required to serialize, allocate, or consult that record
on every ordinary call.
Direct-mode implementations MAY compile, cache, or elide route records
internally, provided they preserve the externally observable route lifecycle,
authorization, revocation, and error semantics required by the selected
profile.

`invocation` MUST be present when a ready transported route is returned to its consumer by `establish_route` or `renew_route`.
Runtime Control MUST NOT return an invocation descriptor for a direct-mode route.
A same-process caller acquires that route through the Runtime handle API,
and an out-of-process caller requires a local or remote transport route.
It MAY be absent from observation records and events.
Runtime MUST disclose route authorization material only for delivery to the route's consumer through an authenticated invocation context.
`list_routes`, audit records, and route-state events MUST NOT expose a one-time route ticket
or reusable bearer credential.

`route_access` is the method and event scope bound to one route.
An ordinary method or event item is the schema subtree root of a declaration under the route's selected contract.
The `methods` list may additionally contain the `logos.schema` method declaration root
from the pinned Logos common schema surface.
That root authorizes selected-contract introspection only for this route.
Runtime MUST reject a route request containing a declaration root
that is neither valid under the selected contract nor an allowed well-known method root.

Every present `methods`, `publish_events`, and `subscribe_events` list MUST order its elements in strictly ascending bytewise lexicographic order of each element's complete Logos deterministic-CBOR encoding and MUST NOT contain duplicates.
Runtime MUST reject an unordered or duplicate list and MUST NOT silently sort or deduplicate a received `route_access` value.

An absent method list permits every method in the selected contract and the well-known `logos.schema` method.
An absent event list permits every event declaration of that kind under the selected contract.
An empty list permits no declaration of that kind.
The route and its invocation path MUST reject operations outside this scope.
`expires_at`, when present, is the number of whole milliseconds since 1970-01-01T00:00:00Z.
Runtime MUST NOT keep the route usable after that time without a successful renewal.

The route model does not define a separate "runtime-mediated" route kind.
If Runtime, a process-local invocation boundary, or a facade provider remains on the invocation path,
that is an implementation property of the selected provider or descriptor.
Regardless of implementation topology, the authorized invocation path MUST preserve the module contract observed by callers.

For a remote-transport invocation path, the Transport endpoint used for ordinary
module calls exposes the selected module contract, not the Runtime Control
contract, unless the selected module is itself `logos_runtime_control`.
The Transport Hello `schema` field on that invocation path carries the
selected structural schema identity of the ordinary module endpoint being invoked.
Both peers MUST use the route's `expected_contract` in that field.
Runtime Control schema commitments identify runtime-control endpoints only;
they do not identify every ordinary module provider behind a remote runtime.

Route states have the following meanings:

- `establishing`: not usable for ordinary calls;
- `ready`: usable through its selected invocation path;
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
When that policy is externalized through Capability Authority,
that contract defines the decision and grant semantics.
The applicable Transport profile defines route authorization material.
LOGOS-MODULE-CAPABILITY-AUTHORITY defines the baseline call-evidence container.
Protected Runtime inputs, static registration, deployment configuration, and
embedded runtime-host wiring may bootstrap local authority policy, but do not
bypass route enforcement.
The optional `decision_id` field identifies an authority decision known to the
runtime or its configured Capability Authority provider.
It is an opaque correlation identifier, not a token format or caller-presented bearer credential.
Callers present authority inputs through the selected method, transport, or
runtime API surface;
the runtime evaluates those inputs through authority policy and records the
resulting decision identifier when needed.

Route establishment follows these steps:

1. The consumer invokes the Runtime Control `establish_route` method.
2. Runtime determines the selected contract expectation and requested provider-set cardinality from the method request.
3. For `single`, the consumer's Runtime resolves matching candidates internally without exposing the candidate set.
   For `all-runtime-visible`, it first obtains the required `discover` allow decision
   and then resolves the providers visible through that decision.
4. For `single`, the runtime selects one matching provider according to local
   routing-selection state or deployment configuration.
   For `all-runtime-visible`, Runtime treats each matching provider visible through
   the discovery decision as selected and attempts an independent route for each one.
5. For each selected provider, the runtime validates the selected contract
   using the module name, schema namespace, schema commitment, compatibility
   metadata, and Transport Hello `schema` commitment where Transport is used.
6. If the selected provider is owned by another Runtime instance, the consumer's
   Runtime contacts the target Runtime.
   The target runtime remains responsible for validating providers it owns.
7. When the invocation path will accept a remote provider session,
   the target runtime selects the remote listener for that path.
   It verifies that the listener is enabled
   and that the selected provider has an enabled export through that listener.
   Runtime Control exposure on the listener does not satisfy the provider-export requirement.
8. The target runtime performs the route authority check and may consult its
   configured Capability Authority.
9. If listener validation, export validation, contract validation,
   or authority checking fails,
   Runtime creates no usable route for that provider.
   For `single`, the request fails.
   For `all-runtime-visible`, Runtime may omit that provider,
   return the other ready routes, and set `partial` to `true`.
10. If validation and authority checking succeed,
    the runtime creates or exposes
    a `route_record` and binds the consumer-side handle, helper, or transport
    session to the route.
11. The route becomes `ready` only after the selected invocation path is usable and
    the target provider still satisfies the selected contract.
12. Ordinary module calls use the selected invocation path, not Runtime Control methods.

Route establishment and renewal are Runtime-owned operations.
Runtime exposes them to modules only through the typed Runtime Control `establish_route` and `renew_route` methods.
A language binding MAY represent a ready route returned by those methods as a process-local handle or Transport session.
That representation does not define another route-acquisition operation.
The resulting route belongs to and may be used only by its consumer module.
Ordinary provider calls use the invocation path of the resulting route and are not Runtime Control operations.

The authenticated Runtime Control consumer is the consumer for an `establish_route` request.
Runtime derives each returned route's `consumer` from the authenticated invocation context.
An `establish_route_request` does not carry a separately named consumer.
Authority to invoke `establish_route` does not itself grant provider access.

`contract` identifies the exact contract selected for every resulting route.
If `provider` is present, `cardinality` MUST be `single`, and Runtime MUST select that provider or fail.
If `provider` is absent, Runtime selects providers according to `cardinality` and active visibility policy.
For `single`, a successful response contains one route and `partial` MUST be `false`.
For `all-runtime-visible`, each returned route is independently authorized and ready.
If no provider can produce a ready route, establishment fails rather than returning an empty success response.
Provider visibility and provider access are evaluated for the authenticated consumer.

A caller without matching provider-discovery or Runtime Control observation authority
MUST NOT be able to distinguish an unknown target from an existing but hidden or denied target.
Runtime MUST report `NOT_AUTHORISED` with a non-revealing diagnostic for those cases.
Authorized Runtime observation and Capability Authority audit material MAY retain the precise reason.

When Capability Authority supplies the provider-access decision,
Runtime allocates each route identifier before evaluation and includes it in the authority request.
An allow decision used for an established route MUST have a validity end,
and `expires_at` MUST NOT be later than that end.
The returned route's `access` MUST equal the allowed provider access or be narrower than it.

`request_key` is an idempotency value scoped to the authenticated consumer and Runtime instance.
Reusing it with the same request while the result remains retained MUST return the same result
and MUST NOT create additional routes.
Reusing it with different request fields MUST fail as an invalid request.

`renew_route` preserves the route identity, consumer, selected provider, contract, and access scope.
It performs a new authority check and may extend `expires_at` and replace `decision_id`.
A consumer cannot change a route's consumer through renewal.
Acquisition by another consumer requires a new `establish_route` request authenticated as that module.
Changing the provider, contract, or access scope requires a new `establish_route` request.
Renewal MUST fail if the route is unknown, closed, failed, or revoked,
or no longer satisfies provider and contract validation.

A runtime MAY combine, cache, or precompute these steps when the selected
profile allows it, for example by binding direct-mode generated helper function
pointers during startup or first use.
Such optimization MUST NOT bypass provider selection, contract validation,
authority checks, route lifecycle, or revocation semantics.

Route establishment failure is distinct from route failure after readiness.
If establishment fails, the Runtime MUST NOT return a consumer-side handle,
helper binding, or invocation descriptor usable for ordinary calls.
If a ready route later fails, the runtime MUST invalidate or transition the
route according to the route-state rules and report ordinary call failures
through the selected invocation path.
An implementation that exposes asynchronous route notifications to ordinary
modules MUST report them as lifecycle changes for the consumer's own routes.
It MUST NOT require exposing global provider inventory or unrelated provider
state to ordinary consumers.
Runtime Control is the contract for privileged observation of route records and route-state events.

The target Runtime remains the enforcement point for providers it owns.
A consumer's Runtime MAY assist with discovery, local policy, cached grants, or
transport setup, but it MUST NOT unilaterally authorize access to a provider
owned by another runtime.
Delegation of provider-access authority MUST be represented as an allow decision
accepted by the target runtime's authority policy.

Route enforcement is a runtime responsibility; route policy is not.
The runtime owns the minimal state needed to enforce whether an established
route may still be used: route identity, selected provider, invocation
path material, authority result reference, and failure state.
Policy decisions that allow, deny, expire, revoke, retry, or reselect routes
come from runtime authority policy.
The runtime enforces the resulting decision on its route table and caller-side
bindings.

The runtime MUST revoke or fail routes whose selected provider is no longer usable, including provider removal, module-instance stop, incompatible schema change, loss of the contract schema commitment required by Transport, remote runtime disconnect, authority expiry, or explicit policy revocation.
When a route is revoked, failed, or closed, the runtime MUST prevent new
ordinary calls through that route.
In-flight call behavior, timeout policy, idle expiry, and retry policy are
profile or implementation policy; if such policy invalidates a route, the
runtime enforces the resulting route revocation or failure.

Automatic retargeting of an established route is forbidden.
A new route acquisition after failure MAY select a different matching provider
unless a caller constraint, runtime-host constraint, deployment constraint, or
active policy constrains provider continuity.
If runtime authority policy allows automatic re-acquisition,
the replacement provider MUST satisfy the same selected contract expectation.
The runtime MUST create a new route identity or an explicit renewal relation
defined by runtime authority policy and visible through Runtime Control
observation.

For audit and observation, the runtime MUST retain enough route material for a
privileged observer to reconstruct the enforcement decision through the
runtime-control contract.
The minimum material is the route identity, consumer reference, selected provider address,
expected module name, selected contract when known,
authority result reference when present, route state transition, and failure
code when present.
Runtime Control exposes route observation through `list_routes` and
`route_state_changed_event`.
Retention selection remains an authority-policy or deployment concern.
If authority policy is externalized through Capability Authority,
that contract defines decision identifiers, retention requirements,
audit records, and the baseline call-evidence container.

Remote enforcement outcomes MUST remain distinguishable
in retained audit or observation material.
At minimum, Runtime MUST distinguish:

- transport authentication or Runtime enrollment failure;
- a disabled listener or a provider that is not exported;
- an authority denial from inability to obtain or validate an authority decision;
- a missing, invalid, expired, revoked, replayed, or incorrectly bound route ticket; and
- session termination caused by route expiry, revocation,
  listener or export disablement, or connection loss.

The retained material MUST identify the consumer when established and, for a remote operation, the authenticated source Runtime.
It MUST also identify the endpoint, provider, route, and authority decision when those values have been established.
Runtime MUST NOT attribute a failure to a claimed Runtime identity or route
that it has not authenticated or validated.

Listener and provider-export changes made through Runtime Control MUST identify the authenticated consumer and resulting state.
Changes supplied through deployment inputs
MUST remain distinguishable from changes made through Runtime Control.
Capability Authority audit records MAY satisfy the authority-decision portion,
but Runtime MUST retain the enforcement outcome for Runtime-owned state.

Remote lifecycle ownership is not transferred by facade or route creation.
The Runtime instance that owns a live module instance owns that instance's transitions among `unloaded`, `loaded`, `ready`, `stopping`, and `error`.
A local remote-module facade reflects remote lifecycle and connectivity state
for local provider selection and route enforcement, but it does not become the
lifecycle owner of the remote module instance.

Authority accepted for a module’s local Runtime Control operation is not transitive.
Runtime MUST NOT infer from it that the consumer may control a remote Runtime or start or stop remote-owned module instances.
Remote lifecycle-control operations require explicit authority accepted by the
runtime that owns the target module instance.

Server-side lifecycle workflows may be performed by an authorized module owned by the server Runtime.
A local runtime may establish authorized routes to providers exposed by the
server runtime, and may observe reflected readiness or failure through its local
facade provider state.
That invocation authority does not imply remote lifecycle-control authority.
A module owned by the local Runtime may invoke remote Runtime Control only when the source Runtime authenticates the transport boundary and the remote Runtime accepts authority for that consumer.

A remote-module facade has local provider state and reflected remote state.
The local provider state describes whether the facade provider is available to
the local runtime for provider selection and route establishment.
The reflected remote state describes the last lifecycle/readiness/failure state
reported or proven by the runtime that owns the remote module instance.
A facade provider MUST NOT be treated as ready for ordinary calls unless both
the local facade provider is usable and the reflected remote target state is
compatible with readiness for the selected contract.
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
module name, schema namespace, schema commitment, and the reflected readiness or failure state used for local provider selection.
The mapped local facade provider record MUST expose the local facade provider
address as its `provider`.
It MAY expose the remote target through `remote`.

Reflected remote state is advisory unless it is fresh according to transport
state, Runtime Control observation, and runtime authority policy.
If the local runtime cannot refresh or validate remote state when required, it
MUST treat dependent facade providers and routes as not ready, failed, or
revoked according to runtime authority policy.
A local facade MUST NOT continue to report ready state for new ordinary calls after the remote module stops, becomes `unloaded`, fails, becomes contract-incompatible, or becomes unreachable.

Remote lifecycle and facade failures MUST be classified at the runtime boundary
before they are reported to consumers or Runtime Control observers.
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

An authorized module observes the local runtime's provider, route, and facade state
through the local runtime-control contract.
The module is not required to contact the remote runtime directly to learn
that a local facade provider is unavailable, stale, failed, or not ready.
If the local runtime cannot determine fresh remote state, it MUST expose that
uncertainty as local reflected state rather than reporting the facade provider
as ready.

The `list_modules` method returns the runtime-known module records visible to
the authorized runtime-control caller.
Its response is Runtime introspection state, not an ordinary-module discovery mechanism.
The returned records describe local provider records, local module instances,
and local remote-module facade providers known to this runtime instance.
The method does not install packages, resolve dependency graphs, establish
routes, or grant authority to call any listed provider.

The `list_routes` method returns route records visible to the authorized
runtime-control caller.
If `module` or `provider` is present, the runtime filters the returned records
to matching routes.
The response is runtime-control observation state.
It does not establish, renew, revoke, or authorize routes.
`list_routes` MUST omit `invocation` from every returned observation record.

`list_remote_listeners` returns the listener records visible to the authorized caller.
`list_provider_exports` returns the visible export records
and applies the requested listener and provider filters when present.
Neither method changes exposure or grants access.

For every Runtime Control list method,
Runtime applies method authorization, scope constraints, record visibility,
and optional-field redaction before constructing the response.
A record whose required fields cannot be disclosed is omitted.
An optional field the caller may not observe is omitted.
If the complete caller-visible result exceeds the applicable response resource limit,
Runtime returns a usable subset and sets `partial` to `true`.
Otherwise, it sets `partial` to `false`.
Hidden records do not affect `partial`, and the response does not disclose their number.

`set_remote_listener` idempotently assigns the requested listener state.
When enabling a listener,
Runtime MUST validate and activate its address and selected transport profile
before returning success.
If activation fails, the method MUST fail without reporting the listener as enabled.

Disabling a listener MUST stop new connections at that address.
Disabling Runtime Control on a listener MUST stop new Runtime Control requests there.
Runtime may finish the `set_remote_listener` response on the current control session,
but it MUST reject later requests on a session that no longer satisfies the listener state.

`set_provider_export` idempotently assigns the requested export state.
Runtime MUST reject an export whose listener has no corresponding listener record
or whose provider is not owned by that Runtime.
An export may be enabled while its listener is disabled,
but it does not become remotely usable until the listener is enabled.

Disabling a listener or provider export MUST prevent new routes and provider sessions
that depend on that state.
Runtime MUST revoke affected ready routes through the ordinary route-state rules.
In-flight call behavior follows the existing route-revocation policy.

Bootstrap and deployment inputs may provide the same listener and export records.
Runtime MUST apply the same validation and enforcement rules
whether state comes from deployment input or authorized Runtime Control.
Package installation, module realization, and provider registration
MUST NOT create an enabled listener or export.

The `establish_route` method applies the route-establishment algorithm in this section
and returns one or more independently authorized route records.
Each returned route MUST be `ready`.
A transported route MUST contain a usable invocation descriptor for its selected profile.
A direct-mode route MUST omit `invocation` and use the Runtime handle API.
For `single`, failure to produce that route fails the method and returns no usable route.
For `all-runtime-visible`, Runtime may return the ready subset with `partial` set to `true`.
If no route is ready, the method fails.

The `renew_route` method rechecks the existing route without changing its consumer, provider, contract, or access scope.
Successful renewal returns the updated route record.
The returned record MUST be `ready` and follow the same invocation-field rules as an established route.
Renewal does not revive a closed, failed, or revoked route.

The `close_route` method asks Runtime to close an established route.
The route's consumer may close its own route.
A different consumer may close that route only when active policy authorizes the `close_route` method for that route.
If successful, Runtime MUST set the route state to `closed` and prevent new ordinary calls through it.
In-flight call behavior is governed by runtime authority policy.
The response reports the resulting route state.
Closing a route does not revoke an authorization grant or change another route.

The `start_module` method starts a module record already known to the runtime.
If the module record is not known, the runtime returns the ordinary
schema-defined error result for "module not found" or equivalent runtime
failure.
The method does not install packages, resolve package dependencies, or create
new runtime records by itself.
For a local module implementation, success means Runtime has performed the lifecycle work needed to move the selected module instance toward `ready`, including native artifact loading and lifecycle initialization where applicable.
For a remote-module facade provider,
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
An authorized module may coordinate those workflows before invoking `stop_module`.
For a local module implementation, success means Runtime has performed the lifecycle work needed to move the selected module instance toward `stopping` or `unloaded`, including lifecycle destruction where applicable.
For a remote-module facade provider,
`stop_module` does not stop the remote implementation unless a separate
authorized remote-runtime operation is performed.
It may only stop, detach, or mark unavailable the local provider/facade state
owned by this runtime instance.
The response reports the resulting local runtime lifecycle state.

The `get_readiness` method reports the runtime lifecycle state for the
selected module instance.
For local module instances, the reported state is the local runtime-owned
lifecycle state.
For remote-module facade providers, the
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
For remote-module facade providers, the
event reports changes in local provider/facade state, including reflected
remote state changes that affect local readiness.
The event does not prove remote lifecycle authority or remote state freshness
by itself; callers interpret it according to the selected runtime-control,
transport, and deployment policy.

The `route_state_changed_event` event reports route state transitions visible
through this control surface.
It is observation state only.
It does not establish, renew, revoke, or authorize routes by itself.
Runtime MUST deliver Runtime Control state events only while the authenticated subscriber
remains authorized to observe the referenced module, provider, or route.
A Runtime Control subscription MUST NOT reveal unrelated provider inventory,
route state, event publishers, or subscribers.

Because the runtime-control interface is an ordinary Logos module contract at
the schema layer, its schema and values are subject to
LOGOS-MODULE-COMMITMENT-MODEL and LOGOS-MODULE-HASH-PROFILE in the same way
as other module contracts.
When Runtime Control records are committed, audited, or included in call evidence,
the committed value is the schema-typed value for the relevant
runtime-control record, such as `module_record`, `route_record`,
`runtime_endpoint`, or `module_provider_address`.
Implementations MAY use different internal structures, but call evidence
MUST be derived from the CDDL-defined runtime-control value.
This specification does not require every transient runtime-control response to
be committed.

---

## 10. Error Handling and Recovery

### 10.1 Module Failure and Restart

Runtime owns evaluation and enforcement of the active restart policy.
The Runtime host or deployment MAY supply that policy as protected input.
The mechanism responsible for a failed realization performs recovery only when Runtime requests it.
Runtime requests cleanup and a new realization through the same mechanism that established the failed realization.
That mechanism MUST NOT independently decide whether a failed module is restarted.

Every Runtime MUST apply an active restart policy to unexpected failures of local module realizations.
Disabling automatic restart is a valid policy.
When automatic restart is enabled,
the policy MUST bound retry frequency and MAY limit the number of attempts.
An authorized stop or Runtime shutdown MUST NOT trigger automatic restart.

When Runtime observes an unexpected realization failure through Transport closure, realization status, or process supervision, Runtime:

1. Marks the module as `error` in the registry.
2. Fails routes backed by the failed realization according to the route-failure rules.
3. Consults the active restart policy.
4. If the policy permits another attempt,
   requests recovery through the mechanism responsible for that realization.
5. Treats recovery as a new realization and,
   for a native implementation, uses a new native context.
6. Runs the full lifecycle again before returning the module to `ready`.
7. Leaves the module in `error` when the policy declines or exhausts recovery attempts,
   or when the new realization fails.

A successful recovery MUST NOT reactivate routes that failed with the previous realization.
Callers require new route acquisition to use the recovered provider.

If the failed module is a bound system service provider,
Runtime MUST apply restart policy through the mechanism that established it.
Runtime MUST complete the ordinary system-service binding and readiness checks before using the restarted provider.
The failed provider MUST NOT be invoked to restart itself.

While a required system service is unavailable,
Runtime MUST fail every operation that requires it.
That unavailability alone MUST NOT change the lifecycle state of an otherwise healthy module realization.
If restart policy permits a later attempt,
Runtime MAY retry a dependent operation after the required system service becomes available.

Operating-system signals, service-manager operations,
container-runtime commands, and other concrete supervision mechanisms
are realization and deployment implementation details.

### 10.2 Graceful Shutdown

On runtime shutdown:

1. Runtime transitions affected module instances to `stopping`,
   prevents new routes and instance-dependent calls,
   and quiesces or closes their invocation paths.
2. Runtime drains or fails in-flight work and releases every transferred
   module-owned output.
3. In the reverse order required by accepted lifecycle-ordering constraints,
   Runtime initiates graceful release for each local realization through the same mechanism that established it.
4. During graceful release of a live native context,
   the applicable ABI caller invokes `_destroy(context)` exactly once
   before discarding its binding or stopping its containing execution form.
5. If an ordinary realization does not complete cleanup within the active grace period,
   Runtime MAY request forced cleanup through the responsible realization, Runtime host, or deployment mechanism.
6. Runtime continues shutdown after every realization has been released,
   or its cleanup failure has been recorded according to shutdown policy.

The selected realization mechanism owns the concrete best-effort realization of graceful and forced cleanup for local implementations.
Runtime maps the resulting realization and cleanup failures
into Runtime-owned module lifecycle state.

If a locally realized module fails during startup before it reaches `ready`,
Runtime MUST use the same realization mechanism to release and clean up the partially realized implementation.
Runtime MUST NOT leave a failed startup realization available as an unregistered or ready module provider.

---

## 11. Presentation Boundary

Presentation data planes, compositor protocols, and toolkit integration are outside this specification.
A presentation module is an ordinary module instance and uses the module identity, lifecycle, realization, routing, authority, and audit rules defined here.
Runtime MUST NOT create a separate presentation participant, consumer identity, lifecycle, or authority path for it.
Any selected presentation profile MUST preserve the canonical module contract defined by LOGOS-MODULE-INTERFACE and the execution semantics defined by this specification.
Concrete presentation handoffs and compositing behavior belong to the selected presentation profile.

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

Provider-side local Transport boundaries receive LOGOS-MODULE-TRANSPORT requests as method names and deterministic CBOR request payloads.
For a dynamically loaded implementation,
the generic provider-side invocation path is the dispatch ABI defined by LOGOS-MODULE-INTERFACE.

A foreign-function interface such as `libffi` could theoretically derive native
C calls from schema information at runtime, but this revision does not define
that as the interoperable native-host path.

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
runtime behavior such as lifecycle management, initialization-service binding, event delivery,
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

## Appendix B. Runtime Control Record Examples

This appendix gives informative examples of selected Runtime Control records.
They show schema-shaped values for implementers and reviewers.
They do not define deterministic CBOR bytes, hash inputs, or digest values.
Those values follow from the deterministic encoding and hash-suite rules in
LOGOS-MODULE-INTERFACE and LOGOS-MODULE-HASH-PROFILE.

### B.1 Runtime Endpoint

```cddl
{
  runtime_instance_id: "rt-local-001",
  address: {
    transport: "unix-stream",
    path: "/run/logos/runtime-control.sock",
    profile: "logos.local.unix-stream"
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

This value conforms to `logos.runtime.module_provider_address`.
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
  primary_contract: {
    commitment_model: "logos.commitment-model.2026-08",
    schema_root: h'00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-08.choice-index",
    hash_suite: "logos.hash-suite.blake3-256"
  }
}
```

This value conforms to `logos.runtime_control.module_record`.
The `provider` field names the local runtime-known provider.
The `primary_contract` field uses the mandatory hash suite;
the root bytes remain illustrative record-construction data.

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
        profile: "logos.remote.tls-tcp"
      }
    },
    provider: "provider-storage-remote"
  },
  state: "ready",
  mode: "remote-transport",
  primary_contract: {
    commitment_model: "logos.commitment-model.2026-08",
    schema_root: h'00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-08.choice-index",
    hash_suite: "logos.hash-suite.blake3-256"
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
  consumer: {
    runtime_instance_id: "rt-local-001",
    module_instance_id: "instance-consumer-example-001"
  },
  target_provider: {
    runtime_instance_id: "rt-local-001",
    provider: "provider-storage-remote-facade"
  },
  module: "storage_module",
  expected_contract: {
    commitment_model: "logos.commitment-model.2026-08",
    schema_root: h'00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff',
    hash_profile: "logos.hash-profile.2026-08.choice-index",
    hash_suite: "logos.hash-suite.blake3-256"
  },
  access: {},
  state: "ready",
  decision_id: "decision-route-001"
}
```

This value conforms to `logos.runtime_control.route_record`.
The `consumer` identifies the Runtime-scoped consumer for which the route was authorized.
The `target_provider` is the local remote-facade provider.
The `decision_id` is a decision identifier,
not a caller-presented bearer token.
This is an observation record,
so it omits the invocation information and its one-time route ticket.

---

## References

### Normative

- [RFC 5280] -- Internet X.509 Public Key Infrastructure Certificate and CRL Profile.
  https://www.rfc-editor.org/rfc/rfc5280
- [RFC 9562] -- Universally Unique IDentifiers (UUIDs).
  https://www.rfc-editor.org/rfc/rfc9562
- LOGOS-MODULE-CONFIGURATION -- Per-instance configuration state, operations, startup, and live-reconfiguration semantics.
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-TRANSPORT -- Socket protocol specification.

### Informative

- LOGOS-MODULE-LOADER -- Module Loader module contract for module realization.
- LOGOS-MODULE-SYSTEM-BCP -- Complete Logos module-system composition and conformance requirements.

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
