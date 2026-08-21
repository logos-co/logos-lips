# LOGOS-MODULE-LOADER

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Loader                                           |
| Slug         | 310                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the Module Loader module contract.

Module Loader realizes one canonical native module ABI through direct static binding,
direct dynamic loading, or hosted dynamic loading.
Hosted dynamic loading starts one Module Host in a process, sandbox, or container.
The Module Host loads the selected dynamic library,
applies the native ABI for one Runtime-owned module instance,
and exposes a provider through the protected local Transport profile when the module provides a callable contract.

Every Module Loader provider MUST be a local module provider backed by a local module instance.
Runtime MUST maintain ordinary provider and lifecycle records for that instance.
An implementation MAY co-locate or statically link Module Loader code,
but Runtime MUST represent that code as a direct local module instance.
Remote facades and host or deployment services that are not module providers
MUST NOT be bound as Module Loader providers.

Implementing the Module Loader contract does not grant authority.
Runtime or deployment policy binds a provider to the Module Loader responsibility
and authorizes the operations required by the deployment.
LOGOS-MODULE-SYSTEM-BCP defines protected bootstrap and complete-system composition requirements for the initial Module Loader provider.

The canonical flat runtime module name is `logos_module_loader`.
The canonical schema namespace is `logos.module_loader`.
The CDDL blocks in this specification collectively define the normative machine-readable contract.
`logos_module_loader.cddl` is an extracted machine-readable mirror.
If the extracted artifact differs from this specification, this specification governs.

```cddl
_module = "logos_module_loader"
```

The Module Loader schema imports two supporting schemas: Runtime Types from LOGOS-MODULE-RUNTIME and Module Configuration Types from LOGOS-MODULE-CONFIGURATION.

## Scope

This specification defines:

- the three module-realization strategies;
- hosted process, sandbox, and container placement;
- Loader capability records;
- artifact and static-binding descriptors;
- Runtime-owned module-instance binding;
- configuration and state-directory delivery;
- protected hosted-provider endpoint handoff;
- realization, status, live-configuration, and release operations;
- realization records and operational failures;
- concurrency, resource, and security invariants at the Loader boundary.

This specification does not define:

- package catalogs, installation, or dependency resolution;
- module routing, provider selection, or Runtime readiness;
- a concrete dynamic linker, process supervisor, sandbox, or container backend;
- permission approval, grants, revocation, or security audit records;
- sandbox strength, resource policy, or concrete quota mechanisms;
- presentation handoffs or user-facing realization UX.

## 1. Responsibility Split

Runtime owns every logical module instance,
including its identity, lifecycle state, provider state, routing, readiness,
Runtime Control representation, and Runtime enforcement points.
Runtime decides when an accepted implementation is realized
and invokes the bound Module Loader provider.

Package Manager owns package catalogs, package installation state,
resolved local artifacts, and authenticated Runtime handoff records.
Runtime constructs a Module Loader request from an accepted Package Manager handoff
or protected bootstrap input and from its placement and authorization decisions.

Module Loader owns the concrete realization.
For direct realization, it binds or loads the implementation in the process-local ABI caller,
constructs the initialization input,
retains the implementation binding and module context,
and destroys the context during graceful release.
For hosted realization, it creates and supervises one Module Host for the Runtime-owned module instance.
The Module Host performs the process-local ABI operations,
retains the implementation binding and module context,
and destroys the context before orderly termination.

A Module Host is realization machinery.
It has no separate module identity, provider identity, route, authority, or logical lifecycle.
Runtime communicates with a hosted provider through the fixed protected local Transport profile.
The Module Host translates that Transport boundary to the same generic dispatch ABI used by other native hosts.

Module Loader reports operational realization status to Runtime.
It MUST NOT directly create or mutate Runtime-owned module identity,
logical lifecycle, provider, route, readiness, authority, or Runtime Control state.
Module Loader MUST NOT independently restart a failed realization.

Deployment configuration selects concrete dynamic-linker integration,
process supervision, sandbox backends, container runtimes,
filesystem mappings, and platform-specific process settings.
Those choices are not realization-descriptor fields.

Capability Authority, security profiles, and deployment policy own execution authorization,
permission grants, required isolation, dangerous host operations,
resource policy, and security audit semantics.
Module Loader and the selected platform mechanisms enforce the constraints assigned to the realization boundary.
Realization descriptors do not grant those constraints or authorize execution.

## 2. Terminology

- **Realization strategy:**
  one of the three ways Module Loader applies the canonical module ABI:
  direct static binding, direct dynamic loading, or hosted dynamic loading.
- **Hosted placement:**
  the execution envelope for hosted dynamic loading:
  a process, sandbox, or container.
- **Realization:**
  the Loader-owned operational binding between one Runtime-owned module instance
  and one concrete implementation binding.
- **Module instance:**
  the logical module instance owned and identified by Runtime.
- **Module Host:**
  the Loader-controlled execution envelope that applies the native module ABI
  for one hosted module realization.
- **State assignment:**
  the abstract Runtime-owned persistent-state assignment for one module instance.
- **Deployment configuration:**
  protected host input that selects concrete realization mechanisms and mappings
  without becoming module-contract data.

## 3. Realization Descriptors

`logos.module_loader.realization_descriptor` is the canonical realization handoff type.
Other specifications may consume it by schema reference,
but this specification owns its field semantics.

```cddl
logos.module_loader.realization_descriptor =
  {
    strategy: "direct_static",
    module: logos.runtime.module_name,
    static_binding: logos.module_loader.static_binding,
  } /
  {
    strategy: "direct_dynamic",
    module: logos.runtime.module_name,
    artifact: logos.module_loader.artifact,
  } /
  {
    strategy: "hosted_dynamic",
    module: logos.runtime.module_name,
    artifact: logos.module_loader.artifact,
    placement: logos.module_loader.hosted_placement,
  }

logos.module_loader.hosted_placement =
  "process" /
  "sandbox" /
  "container"

logos.module_loader.artifact = {
  id: tstr .size (1..128),
  local_path: tstr .size (1..4096),
  hash: bstr .size 32,
  hash_suite: "logos.hash-suite.blake3-256",
}

logos.module_loader.static_binding = {
  binding: tstr .size (1..128),
}
```

`module` is the flat Runtime module name of the implementation being realized.
It MUST satisfy the module-name syntax defined by LOGOS-MODULE-RUNTIME.
It is not a package, schema, provider, realization, or authority identity.

`direct_static` selects ABI code already linked and registered in the process-local caller.
`static_binding.binding` is a deployment-local identifier for the protected registration.
The registration MUST identify the ABI symbols for `module`.

`direct_dynamic` selects a dynamic library loaded into the process-local caller.
Calls may use the schema-derived typed ABI directly or the generic dispatch ABI.
No Transport endpoint is created for a direct realization.

`hosted_dynamic` starts one Module Host in the selected hosted placement.
The Module Host loads the same form of dynamic library used by `direct_dynamic`.
When the module provides a callable contract,
the Module Host exposes it through `logos.local.unix-stream` and dispatches requests through the generic native ABI.

A language implementation that cannot directly export the canonical C ABI
MUST include generated or handwritten adapter code that exports that ABI.
The adapter is part of the module implementation.
It does not create another module identity, contract, lifecycle, or realization strategy.

The artifact record identifies the exact accepted local dynamic library.
Runtime constructs it from authenticated Package Manager output or protected bootstrap input.
The `id`, `hash`, and `hash_suite` values MUST equal the accepted artifact record.
`local_path` MUST identify a local resource and MUST NOT identify a remote resource.

Before artifact-controlled code is mapped,
Module Loader MUST verify the exact library bytes against `hash` using `hash_suite`.
It MUST map the verified bytes without a path-replacement gap,
for example by retaining an operating-system handle or using a protected immutable artifact location.
A missing or unusable artifact produces `artifact-unavailable`.
A digest mismatch produces `artifact-integrity-failed`.

Dynamic loading may execute artifact-controlled initialization before a Logos ABI symbol is called.
Runtime MUST therefore complete execution authorization before invoking `realize`.
Digest verification establishes byte identity only.
It does not establish package trust, execution authorization, or containment strength.

Realization descriptors MUST NOT contain backend names,
process arguments, environment entries, working directories,
endpoint requests, permission decisions, package trust decisions,
concrete state paths, resource limits, sandbox-strength claims, or audit assertions.

## 4. Loader Capabilities

Runtime queries the strategies and hosted placements supported by the current Loader provider.

```cddl
logos.module_loader.capabilities = {
  ? direct_static: true,
  ? direct_dynamic: true,
  ? hosted_dynamic: {
    ? process: true,
    ? sandbox: true,
    ? container: true,
  },
  ? force_release: true,
}

logos.module_loader.list_capabilities_request = {}

logos.module_loader.list_capabilities_response = {
  capabilities: logos.module_loader.capabilities,
}
```

At least one realization strategy MUST be present.
When `hosted_dynamic` is present,
at least one hosted placement MUST be present.
A field MUST be present only when the Loader can satisfy every requirement of that strategy or operation in the current deployment.

Status reporting, state-directory delivery when requested,
graceful release, and the fixed hosted-provider Transport profile are required behavior.
They are not separately advertised capabilities.
`force_release` advertises the optional force-release operation.

## 5. Realization Handoffs

Realization handoffs carry instance-specific operational input.
They are not authority tokens and are not retained in public realization records.

### 5.1 State Assignment

```cddl
logos.module_loader.state_context = {
  assignment: logos.runtime.module_state_assignment_id,
}
```

`assignment` is the Runtime-owned state assignment for the supplied module instance.
Module Loader maps it to one module-visible directory according to protected deployment configuration and active policy.
The assignment is not a filesystem path, storage grant, cleanup instruction,
or authority to inspect existing module state.

When `state` is present in a realization request,
Module Loader MUST establish the mapping before native initialization
and MUST supply the module-visible path through the Interface `state_dir` initialization field.
For hosted realization, the Module Host MUST receive the mapped directory
and pass its module-visible path through the same field.
When `state` is absent, the ABI caller MUST use the Interface absent representation for `state_dir`.

Module Loader MUST NOT mutate a shared process environment to deliver per-instance state.
Concrete host paths, bind mounts, volumes, permissions, migration,
retention, and deletion remain deployment and policy concerns.

### 5.2 Configuration

```cddl
logos.module_loader.configuration_handoff = {
  input: logos.module_configuration.configuration_input,
  ? live_reconfiguration: true,
}
```

Runtime includes `configuration` exactly when the accepted module declaration has a configuration binding.
`input` is the immutable configuration selected for that startup attempt.
`live_reconfiguration` is present exactly when the accepted binding declares live reconfiguration.

The ABI caller deterministically encodes `input` and supplies it through the Interface initialization fields.
When the handoff is absent,
the ABI caller supplies the Interface absent representation.
The handoff MUST NOT appear in a public realization record or error message.

### 5.3 Hosted Provider Endpoint

```cddl
logos.module_loader.provider_endpoint = {
  profile: "logos.local.unix-stream",
  address: tstr .size (1..4096),
}
```

Module Loader creates the endpoint only for a hosted realization whose validated ABI exposes a callable contract.
The endpoint MUST implement the protected `logos.local.unix-stream` profile
and MUST identify the exact endpoint prepared for that Module Host.
Runtime MUST use that exact endpoint and perform every Transport and Runtime readiness check before exposing the provider.

A direct realization MUST omit `provider_endpoint`.
A consumer-only realization MUST omit `provider_endpoint`.
No endpoint mechanism is negotiated through this contract.

## 6. Realize Operation

```cddl
logos.module_loader.realize_request = {
  module_instance: logos.runtime.module_instance_id,
  descriptor: logos.module_loader.realization_descriptor,
  ? state: logos.module_loader.state_context,
  ? configuration: logos.module_loader.configuration_handoff,
}

logos.module_loader.realize_response =
  {
    status: "succeeded",
    realization: logos.module_loader.active_realization,
  } /
  {
    status: "failed",
    error: logos.module_loader.error,
  } /
  {
    status: "failed",
    realization: logos.module_loader.failed_realization,
  }
```

`module_instance` is the Runtime-owned identity of the logical module instance.
Module Loader MUST bind the realization to that exact identity
and MUST NOT derive another module-instance identity from a process,
container, endpoint, static binding, artifact, or realization identifier.

Module Loader MUST maintain at most one active or failed realization for one module instance.
If the same descriptor and private handoffs are already active for the instance,
`realize` MUST succeed and return that active realization without creating another context or Module Host.
If the instance has a different active realization or any failed realization,
`realize` MUST return `instance-conflict`.
A failed realization must be released before another realization can be created for that module instance.

Module Loader MUST reject a strategy or hosted placement that it did not advertise with `unsupported-strategy`.
It MUST do so before loading artifact-controlled code.

For direct static realization,
Module Loader is the ABI caller defined by LOGOS-MODULE-INTERFACE.
For direct dynamic realization,
Module Loader loads the verified artifact and is the ABI caller.
For hosted dynamic realization,
Module Loader creates one Module Host,
and that Module Host is the process-local ABI caller under Loader control.

The ABI caller MUST satisfy every applicable LOGOS-MODULE-INTERFACE requirement.
Before initialization, it MUST:

1. resolve the mandatory ABI symbols for the expected module name;
2. require `logos_<module>_name()` to return `descriptor.module`;
3. obtain, parse, and validate the provider call surface when provider symbols apply;
4. populate the initialization ABI version and structure size;
5. supply the consumer-bound Runtime Control binding;
6. supply the required event-publication binding;
7. supply `state_dir` and configuration using the handoffs defined above; and
8. set `*out_context` to `NULL` before calling `logos_<module>_init()`.

Missing, contradictory, or invalid ABI symbols and metadata produce `abi-invalid`.
The ABI caller MUST reject every initialization result and context combination that LOGOS-MODULE-INTERFACE does not permit.
A successful initialization creates one distinct live module context for the module instance.
The ABI caller MUST retain the accepted binding and use that same context for every instance-dependent ABI operation.

For hosted provider realization,
the Module Host MUST establish the protected provider endpoint after successful initialization
and before Module Loader returns an active realization.
The host applies the generic dispatch ABI to Transport requests
and applies the Interface concurrency and memory-ownership requirements.

`realize` is complete when it returns.
Success MUST return an active realization that satisfies every requested Loader-owned handoff.
The operation MUST NOT return an intermediate state.

If realization fails before becoming active,
Module Loader MUST clean every partial context, binding, endpoint, and execution envelope that it can safely clean.
When cleanup completes, it returns the error without a realization record.
When cleanup remains necessary,
it retains and returns a failed realization so Runtime can invoke `release`.

Outside protected initial system-service bootstrap,
Runtime MUST obtain authorization for module execution and every required permission before invoking `realize`.
Module Loader MUST accept security and deployment constraints only from a boundary trusted by the selected profile.
It MUST fail rather than substitute a weaker strategy, placement, isolation mechanism, state mapping, or resource control.

## 7. Realization Records And Status

```cddl
logos.module_loader.realization =
  logos.module_loader.active_realization /
  logos.module_loader.failed_realization

logos.module_loader.active_realization = {
  realization: logos.module_loader.realization_id,
  module_instance: logos.runtime.module_instance_id,
  status: "active",
  ? call_surface: bstr .size (1..8388608),
  ? provider_endpoint: logos.module_loader.provider_endpoint,
}

logos.module_loader.failed_realization = {
  realization: logos.module_loader.realization_id,
  module_instance: logos.runtime.module_instance_id,
  status: "failed",
  failure: logos.module_loader.error,
}

logos.module_loader.realization_id = tstr .size (1..128)

logos.module_loader.get_status_request = {
  realization: logos.module_loader.realization_id,
  module_instance: logos.runtime.module_instance_id,
}

logos.module_loader.get_status_response =
  {
    status: "succeeded",
    realization: logos.module_loader.realization,
  } /
  {
    status: "failed",
    error: logos.module_loader.error,
  }
```

A realization identifier is issued by the Module Loader provider
and is scoped to that provider and Runtime deployment.
Each newly created realization MUST receive an identifier that the Loader has not previously issued within that deployment.
A new realization after release or failure uses a fresh identifier and a fresh native context.
The Loader retains the realization descriptor and private handoffs internally for idempotency and cleanup.
The public realization record does not repeat them.

An active realization has completed native initialization and every requested Loader-owned handoff.
For a provider, `call_surface` contains the exact deterministic-CBOR bytes
returned by `logos_<module>_call_surface()`.
Module Loader MUST NOT rewrite or combine the contained contracts.
A provider realization MUST contain `call_surface`.
A consumer-only realization MUST omit it.

An active hosted provider realization MUST contain `provider_endpoint`.
Every other realization MUST omit it.
Neither an active realization nor an endpoint establishes Runtime-owned readiness.
Runtime validates the expected contracts,
authenticates hosted Transport,
and completes every authority and readiness check before exposing the provider.

A failed realization is unusable and requires release before replacement.
Its `failure` records the current operational reason.
It MUST omit call-surface and endpoint fields.
Unexpected Module Host termination,
loss of a required direct binding,
or an indeterminate live-configuration outcome changes an active realization to failed.

`get_status` MUST return one complete active or failed record for a matching realization.
It MUST return `realization-not-found` when no realization matches both supplied identifiers.
It MUST NOT disclose whether either identifier matches a different record.

## 8. Live Configuration

```cddl
logos.module_loader.apply_configuration_request = {
  realization: logos.module_loader.realization_id,
  module_instance: logos.runtime.module_instance_id,
  configuration: logos.module_configuration.configuration_input,
}

logos.module_loader.apply_configuration_response =
  { status: "succeeded" } /
  {
    status: "failed",
    error: logos.module_loader.error,
  } /
  {
    status: "failed",
    realization: logos.module_loader.failed_realization,
  }
```

Runtime invokes `apply_configuration` only for an active realization
whose startup handoff declared live reconfiguration.
An unknown or nonmatching realization produces `realization-not-found`.
An invalid request for a realization without declared live-reconfiguration support produces `invalid-request`.
Those cases MUST NOT invoke module behavior.

For direct realization, Module Loader invokes `logos_<module>_apply_configuration()`
through the retained context.
For hosted realization, the Module Host invokes the same ABI hook under Loader control.

`LOGOS_OK` produces `succeeded` and leaves the realization active.
A valid module rejection produces `configuration-rejected` and leaves the realization active.
If Module Loader cannot establish whether the module accepted the value,
the operation returns `realization-failed` with the failed realization.
The operation does not mutate Runtime-owned configuration or lifecycle state.

## 9. Release Operation

```cddl
logos.module_loader.release_request = {
  realization: logos.module_loader.realization_id,
  module_instance: logos.runtime.module_instance_id,
  ? force: true,
}

logos.module_loader.release_response =
  { status: "succeeded" } /
  {
    status: "failed",
    realization: logos.module_loader.failed_realization,
  }
```

Omission of `force` requests graceful release.
Runtime invokes graceful release only after it prevents new instance-dependent work
and drains or fails in-flight work according to LOGOS-MODULE-RUNTIME.

For a live native context,
the ABI caller MUST invoke `logos_<module>_destroy(context)` exactly once
before discarding the binding or stopping its execution envelope.
Beginning destruction consumes the live context.
A later cleanup attempt MUST NOT invoke destruction again for that context.

`force` is valid only when the Loader advertised `force_release`.
It requests the strongest available local termination and cleanup path.
Successful force release establishes only that the Loader retains no realization.
It does not prove that module code completed cooperative cleanup or that destruction returned.

Successful release removes the realization record and establishes absence.
Releasing an already absent matching realization is successful and MUST NOT affect another realization.
If cleanup cannot establish absence,
Module Loader MUST retain and return a failed realization.

## 10. Results And Errors

```cddl
logos.module_loader.error = {
  code: logos.module_loader.error_code,
  ? message: tstr .size (0..512),
}

logos.module_loader.error_code =
  "invalid-request" /
  "unsupported-strategy" /
  "artifact-unavailable" /
  "artifact-integrity-failed" /
  "abi-invalid" /
  "realization-failed" /
  "instance-conflict" /
  "realization-not-found" /
  "configuration-rejected"
```

Every method response is a closed success or failure variant.
A success variant MUST NOT contain an error or failed realization.
A failure variant contains either one error or one failed realization whose `failure` is the operation error.

`invalid-request` identifies a semantically invalid request that MUST NOT be retried unchanged.
`unsupported-strategy` permits Runtime to select another advertised strategy or hosted placement.
`artifact-unavailable` means the accepted local library could not be located or loaded.
`artifact-integrity-failed` means its exact bytes did not match the accepted digest.
`abi-invalid` means verified bytes did not expose the required ABI or valid declared call surface.
`realization-failed` covers initialization, Module Host creation,
state delivery, endpoint establishment, indeterminate configuration,
unexpected realization failure, and incomplete release.
`instance-conflict` requires release of the retained realization before replacement.
`realization-not-found` identifies a stale or nonmatching pair of identifiers without disclosing another realization.
`configuration-rejected` is a definitive module rejection that leaves the realization active.

The ordinary Interface and Transport invocation-error channels report inability to obtain a valid Loader contract response.
Such failures MUST NOT be encoded as another Loader-specific error value.

An error message is diagnostic text only.
It MUST NOT expose credentials, policy inputs, hidden realization existence,
host paths, backend configuration, endpoint secrets, or information the caller is not authorized to observe.
Loader errors are operational results and MUST NOT be interpreted as authorization decisions.

## 11. Concurrency And Ordering

Module Loader MUST apply realization mutations atomically per module instance.
For one instance, `realize`, `apply_configuration`, and `release` execute in one total order.
The Loader MUST serialize live-configuration application
and MUST exclude it from release and other instance-dependent mutation.

`get_status` returns one internally consistent snapshot.
Concurrent status observation returns either the complete record before a mutation
or the complete record after that mutation.
It MUST NOT combine fields from different states.

Module Loader MUST ensure at-most-once destruction for every successfully initialized context.
Operations for different module instances MAY proceed concurrently
subject to the Interface concurrency contract and active resource policy.

## 12. Security Requirements

Module Loader MUST verify dynamic-library bytes before mapping them
and MUST prevent path replacement between verification and mapping.
It MUST reject unsupported strategies before artifact-controlled code executes.

Direct realization places module code in the ABI caller's address space.
It provides no process memory boundary and MUST be selected only when active policy permits that trust relationship.
A hosted placement name does not prove isolation strength.
Module Loader MUST establish every control required by the selected security profile
and MUST fail rather than silently use a weaker mechanism.

The hosted Unix-stream endpoint MUST be protected according to the local Transport profile.
Endpoint possession alone MUST NOT grant provider, route, or method authority.
Runtime remains responsible for peer authentication,
route-ticket handling, contract validation, and provider readiness.

State assignments and module-visible state paths are non-authority coordination data.
Module Loader MUST obtain mappings and access controls from protected deployment input
and MUST NOT accept replacements supplied by the module artifact.

Realization records MUST NOT contain configuration values,
state assignments, artifact or state paths, process identifiers,
sandbox or container references, credentials, grants, policy decisions, or audit material.

## 13. Loader Methods

The Module Loader contract defines these methods:

- `list_capabilities`;
- `realize`;
- `apply_configuration`;
- `get_status`;
- `release`.

## 14. Shared Type Ownership

This specification owns realization descriptors,
Loader capabilities, realization identifiers and records,
hosted placement, operational errors, and release behavior.

LOGOS-MODULE-INTERFACE owns the canonical native ABI,
including identity, initialization, state-directory and configuration input,
Runtime Control and event-publication bindings,
per-instance contexts, provider dispatch, memory release, and destruction.
Module implementations own their contexts.
Opaque context pointers and process-local bindings MUST NOT be serialized through this contract.

LOGOS-MODULE-CONFIGURATION owns configuration-input and live-reconfiguration semantics.
Module Loader owns delivery and operational invocation without owning Runtime configuration state.

LOGOS-MODULE-PACKAGE-MANAGER owns package and installed-artifact records.
LOGOS-MODULE-RUNTIME constructs Loader requests from those records
and owns logical lifecycle, readiness, provider routing, and enforcement.
LOGOS-MODULE-CAPABILITY-AUTHORITY and security profiles own authorization,
permission, isolation, and audit semantics.

## 15. Boundary With Other Core Specifications

LOGOS-MODULE-RUNTIME owns module-instance identity,
lifecycle, provider state, routing, readiness,
Runtime Control, restart policy, and Runtime enforcement points.

LOGOS-MODULE-INTERFACE owns native implementation metadata,
initialization, context, dispatch, memory, and destruction semantics.

LOGOS-MODULE-TRANSPORT owns hosted local message framing,
the protected Unix-stream profile, and Transport behavior.

LOGOS-MODULE-PACKAGE-MANAGER owns package manifests,
installed artifacts, package trust, and Runtime handoff records.

LOGOS-MODULE-CAPABILITY-AUTHORITY owns authorization decisions,
permission grants, revocation, and security audit material.

LOGOS-MODULE-SECURITY-CONSIDERATIONS and security profiles own the integrated threat model,
platform mappings, containment claims, and residual-risk analysis.

---

## References

### Normative

- LOGOS-MODULE-CONFIGURATION -- Configuration input and live-reconfiguration semantics.
- LOGOS-MODULE-INTERFACE -- Canonical native module ABI.
- LOGOS-MODULE-RUNTIME -- Runtime lifecycle, routing, and enforcement semantics.
- LOGOS-MODULE-TRANSPORT -- Protected local Transport profile.

### Informative

- LOGOS-MODULE-SYSTEM-BCP -- Complete module-system composition requirements.
- LOGOS-MODULE-PACKAGE-MANAGER -- Package and installed-artifact contract.
- LOGOS-MODULE-CAPABILITY-AUTHORITY -- Capability and authorization contract.
- LOGOS-MODULE-SECURITY-CONSIDERATIONS -- Integrated security analysis.

---

## Copyright

Copyright and related rights waived via
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
