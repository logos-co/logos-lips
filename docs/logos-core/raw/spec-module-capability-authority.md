# LOGOS-MODULE-CAPABILITY-AUTHORITY

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Capability Authority                                    |
| Slug         | 312                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the Capability Authority module contract.

Capability Authority evaluates authority policy and manages grants for consumers.
It covers provider access, Runtime Control, module execution, remote Runtime enrollment,
and operating-system and platform permissions.
It also carries commitment requirements attached to authorization decisions.
Runtime supplies authenticated call context
and remains responsible for module lifecycle, provider selection, routes, Runtime Control state, and enforcement.

Every Capability Authority provider MUST be a local module provider backed by a local module instance.
The provider MAY use direct mode or local transport mode.
An implementation MAY co-locate or statically link Capability Authority code,
but Runtime MUST still represent that code as a direct-mode local module instance.
Remote facades and host or deployment services that are not module providers MUST NOT be bound as Capability Authority providers.

The canonical flat runtime module name is `logos_capability_authority`.
The canonical schema namespace is `logos.capability_authority`.
The CDDL blocks in this specification collectively define the normative machine-readable contract.
`logos_capability_authority.cddl` is an extracted machine-readable mirror.
If the extracted artifact differs from this specification, this specification governs.
The Capability Authority module schema imports the Runtime Types supporting schema defined by LOGOS-MODULE-RUNTIME.

## 1. Scope

This specification defines:

- authority scopes;
- decision requests and decisions;
- grants and revocation;
- denial and evaluation-failure records;
- policy-change notification and decision-cache behavior;
- authorization audit records;
- the Capability Authority methods and events;
- the boundary between authorization and commitment requirements;
- the enforcement boundary between Capability Authority, Runtime, Module Loader, Transport,
  and deployment or platform controls.

This specification does not define a policy language, user interface, configuration-file format,
or package-signature policy.
It also does not define a trust-store format, public-key infrastructure, operating-system sandbox implementation,
or route-ticket encoding.
Capability Authority does not select providers, create routes, issue invocation descriptors, realize module implementations,
or mutate Runtime-owned state.
It does not issue the route ticket or session credential used on an invocation path.

Implementing this contract does not grant authority.
Runtime or deployment bootstrap policy binds a provider to the Capability Authority responsibility
and grants the minimum operations needed to use it.
The provider MUST satisfy the LOGOS-MODULE-RUNTIME system-service binding checks before use
and MUST NOT authorize its own initial binding.

## 2. Module-Instance Addresses And Authenticated Call Context

Every `consumer` field and every grant `target` field contains a module-instance address.
`consumer` names the module instance whose authority is used to authorize or evaluate the operation.
In a grant, `target` names the module instance to which that grant applies.
Consumer and target are relationships expressed through module-instance identity; neither creates another entity type.
Every module-instance address named by this contract MUST resolve to one Runtime-known module instance.
The Runtime engine, Runtime host, bootstrap machinery, operating-system objects, protected inputs, humans, and unauthenticated peers MUST NOT be represented as module instances.

`logos.runtime.module_instance_address` is the shared address of a Runtime-known module instance.
Its `runtime_instance_id` identifies the owning Runtime, and its `module_instance_id` identifies the module instance within that Runtime.
The address does not authenticate the module instance or grant authority.

Runtime MUST supply Capability Authority with authenticated context for the consumer.
Runtime MUST populate or validate the request's `consumer` against that context before dispatching a Capability Authority method.
For `evaluate`, Runtime supplies the module instance that initiated the attempted operation as consumer.
Runtime's protected invocation of the bound Capability Authority provider does not make the Runtime engine or Runtime host the consumer.
For other methods, the consumer is the module instance authenticated at the Capability Authority invocation boundary.
A request may separately name a target module instance.
A target does not supply the authority used to invoke the method and does not become the consumer.

Every decision identifies the consumer whose authority was evaluated.
Every grant identifies the target module instance to which its scopes apply.
Authority accepted for an inbound route or call applies only within its allowed scope.
It does not transfer the consumer's authority to the provider that handles the call.
When that provider initiates another operation, Runtime uses the provider's backing module instance as the consumer.

## 3. Authority Scopes

An authority scope is a value carried by a request, decision, or grant.
It has no identity or lifecycle of its own.
An allow decision MUST NOT broaden a requested scope and MAY narrow it.
A decision based on a grant MUST NOT exceed that grant's current scope.
For the Core scope shapes, required identity fields must be equal,
and every constrained list in the narrower scope must be a subset of the broader scope.
An optional identity absent from the broader scope is unconstrained;
if it is present, the narrower scope must contain the same identity.
An absent optional list is unconstrained, while an empty method or event list permits none of that declaration kind.
If a broader provider-access scope contains `access`, a narrower scope MUST also contain `access`
and narrow its method and event lists under the Runtime rules.
Every permission definition MUST specify equivalent containment rules for its decoded `constraints` value.
Every `actions`, `uses`, `scopes`, `providers`, `routes`, `modules`, `instances`, `modes`, `placements`, and `grant_ids` array
that is present in a Capability Authority record MUST be non-empty unless its field definition explicitly permits an empty list.
Every array whose elements are a set of scopes, actions, uses, providers, routes, modules, instances, modes,
placements, method roots, event roots, or supporting grant identifiers
MUST contain its elements in strictly ascending bytewise lexicographic order
of each element's complete Logos deterministic-CBOR encoding.
This uses the bytewise comparator defined for deterministic-CBOR map keys by LOGOS-MODULE-INTERFACE.
Such an array MUST NOT contain duplicate elements.
A receiver MUST reject an unordered or duplicate set-valued array
and MUST NOT silently sort or deduplicate a received, committed, or signed value.
Arrays with sequence semantics, including audit-query results and proof paths, retain their separately defined order.

```cddl
_module = "logos_capability_authority"

logos.capability_authority.decision_id = tstr .size (1..128)

logos.capability_authority.route_access = {
    ? methods: [* bstr .size 32],
    ? publish_events: [* bstr .size 32],
    ? subscribe_events: [* bstr .size 32],
}

logos.capability_authority.execution_mode =
    "direct" /
    "local-transport"

logos.capability_authority.hosted_placement =
    "process" /
    "sandbox" /
    "container"

logos.capability_authority.artifact_id = tstr .size (1..128)

logos.capability_authority.provider_access_scope = {
    kind: "provider-access",
    contract: logos.schema_commitment,
    actions: [* (
        "discover" /
        "establish-route" /
        "renew-route" /
        "call" /
        "publish-event" /
        "subscribe-event"
    )],
    ? providers: [* logos.runtime.module_provider_address],
    ? routes: [* logos.runtime.route_id],
    ? access: logos.capability_authority.route_access,
}

logos.capability_authority.runtime_control_scope = {
    kind: "runtime-control",
    runtime: logos.runtime.runtime_instance_id,
    contract: logos.schema_commitment,
    ? methods: [* bstr .size 32],
    ? events: [* bstr .size 32],
    ? modules: [* logos.runtime.module_name],
    ? instances: [* logos.runtime.module_instance_id],
    ? providers: [* logos.runtime.module_provider_address],
    ? routes: [* logos.runtime.route_id],
}

logos.capability_authority.module_execution_scope = {
    kind: "module-execution",
    runtime: logos.runtime.runtime_instance_id,
    module: logos.runtime.module_name,
    ? instance: logos.runtime.module_instance_id,
    actions: [* ("load" / "start" / "stop" / "unload")],
    ? modes: [* logos.capability_authority.execution_mode],
    ? placements: [* logos.capability_authority.hosted_placement],
    ? package: tstr .size (1..128),
    ? version: tstr .size (1..128),
    ? artifact: logos.capability_authority.artifact_id,
}

logos.capability_authority.remote_enrollment_scope = {
    kind: "remote-enrollment",
    remote_runtime: logos.runtime.runtime_instance_id,
    actions: [* ("enroll" / "refresh" / "remove")],
    uses: [* ("runtime-control" / "provider-access")],
}

logos.capability_authority.permission_scope = {
    kind: "permission",
    permission: tstr .size (1..128),
    constraints: bstr .size (1..1048576),
}

logos.capability_authority.scope =
    logos.capability_authority.provider_access_scope /
    logos.capability_authority.runtime_control_scope /
    logos.capability_authority.module_execution_scope /
    logos.capability_authority.remote_enrollment_scope /
    logos.capability_authority.permission_scope
```

Each `contract` field is a `logos.schema_commitment`.
Its schema root commits to the complete schema, including its namespace, so Capability Authority does not carry a separate namespace wrapper.

An omitted `runtime_instance_id` in `logos.runtime.module_provider_address` identifies a provider on the Runtime
whose local context interprets the address.
Omission is not a wildcard and MUST NOT match a provider on another Runtime.
The Runtime identifier MUST be present when the interpreting local Runtime is not otherwise unambiguous.

### 3.1 Provider Access

`provider_access_scope` covers visibility, route establishment or renewal, method calls, event publication,
and event subscription under one exact concrete module contract or interface contract.
It also covers access to a system service provider; a separate system-service grant type is not required.
The `actions` field distinguishes provider discovery, route establishment or renewal,
calls, event publication, and event subscription.
A `discover` allow decision permits Runtime to disclose providers matching the exact `contract`
within the allowed provider constraints.
It does not select a provider, establish a route, or authorize a method or event operation.
Runtime MUST obtain this decision before satisfying an `all-runtime-visible`
request or disclosing a provider's complete call surface through a
module-selected call binding.
For module-selected disclosure,
Runtime MUST obtain one `discover` allow decision for the selected provider and
each exact primary or interface contract in its validated call surface.
If any contract view may not be disclosed,
Runtime MUST fail the module-selected object request rather than omit that view
or return a filtered surface.
These decisions authorize metadata visibility only.
They do not establish or authorize any of the exact-contract routes aggregated by the object.

An ordinary `single` request for one exact known contract remains
non-enumerating and does not require `discover` in addition to its
route-establishment decision.
This includes a primary-contract-selected or interface-selected object that
exposes only that exact contract.

`access` uses the Capability Authority contract's projection of Runtime route access.
Its method and event roots are interpreted under `contract`.
The sole common-surface exception in this revision is the well-known `logos.schema` method root
permitted by LOGOS-MODULE-RUNTIME for selected-contract introspection.
That root remains bound to the requested provider, route, and exact `contract` in this scope.
When authorized, `logos.schema` returns the selected contract document and the exact interface and supporting documents required to reconstruct it.
Method-level or event-level route access may narrow which operations the consumer may perform,
but it MUST NOT produce a filtered construction input, disclose an unrelated contract, or change the selected contract identity.
An interface document returned as reconstruction input does not select or authorize a route under that interface.
An implementation that needs a separately visible subset of a concrete
contract MUST expose that subset as its own exact interface contract.
If `providers` is absent, the scope does not further restrict providers that Runtime and active policy find eligible.
If `routes` is absent, the scope does not further restrict the Runtime routes that may rely on it.
If `access` is absent, the scope does not further restrict method or event access.
When it is present, Runtime's absent-list and empty-list semantics apply.

Runtime selects the provider and requests a decision for that provider and requested scope.
For route creation or renewal, Runtime MUST include the allocated route identifier in the requested scope.
It MUST also include the `access` requested for the route.
Allocating the identifier does not make the route usable.
For a call, publication, or subscription on an existing route,
Runtime MUST include that route and an `access` value containing the one method or event declaration being checked.
An allow decision permits Runtime to create or renew a route within the allowed scope; it does not create the route.
An allow decision used to keep a route or provider session usable MUST contain `valid_until`.
Runtime MUST NOT keep the route or session usable after that time without a new allow decision.
Runtime and the provider-side invocation boundary MUST reject calls, publications, subscriptions,
and event deliveries outside the allowed scope.
A schema or interface declaration proves only that an operation has a defined shape and identity.
It MUST NOT be treated as a grant, an allow decision,
or evidence that the consumer may invoke the declared operation.

### 3.2 Runtime Control

`runtime_control_scope` covers calls, observations, and subscriptions
under the Runtime Control contract exposed by one Runtime instance.
The `contract` field MUST identify that Runtime Control contract.
The `methods` and `events` fields use the same method and event identity rules as `provider_access_scope`.

The remaining optional fields constrain the module, module instance, provider,
or route records that may be observed or targeted.
Every present constraint MUST match the attempted operation or returned observation.
Referenced module instances, providers, and routes MUST belong to the Runtime named in `runtime`.
Local and remote Runtime Control use the same scope shape.

### 3.3 Module Execution And The Loader Boundary

`module_execution_scope` covers Runtime-owned module load, start, stop, and unload operations.
It may bind the decision to a module instance,
execution mode, hosted placement, package and optional version,
or artifact already resolved by Runtime and Package Manager.
The placement, package, version, and artifact fields are Capability Authority wire projections
of values selected by Runtime from Module Loader and Package Manager records.
Their values have the same operational meaning,
but their Capability Authority subtree roots are distinct from Module Loader, Package Manager, and Runtime subtree roots.
The scope applies to local `direct` and `local-transport` module execution
and MUST NOT contain `remote-transport` in `modes`.
`placements` constrains hosted process, sandbox, or container placement and therefore requires `local-transport`.
Direct execution MUST omit `placements`.
`version` MUST NOT be present unless `package` is present.
If `artifact` is present, `package` MUST also be present because the artifact identifier is package-scoped.
Package, version, and artifact identifiers are policy inputs and do not prove integrity or trust by themselves.
For a non-direct Loader-realized module instance,
`start` includes execution-form realization and subsequent Runtime initialization and readiness processing.

Outside the initial system-service bootstrap authorized under Section 1,
Runtime MUST obtain an allow decision before asking Module Loader to realize a direct native implementation.
The decision MUST cover the module execution operation and every required permission scope.
Runtime MAY allocate the module instance identifier used by the module consumer before loading code;
allocation does not make the module loaded or ready.

Outside that initial bootstrap,
Runtime MUST obtain an allow decision before asking Module Loader to realize a process, sandboxed process, or container.
The decision MUST cover the module execution operation,
selected hosted placement,
and required permission scopes.
Authorization to call the Module Loader provider does not authorize an arbitrary module execution operation.
The module execution decision and the provider-access decision for Module Loader are distinct checks over existing scopes, not distinct grant types.

Module Loader and deployment or platform controls enforce the selected execution
and operating-system constraints that they own.
Runtime and the selected security profile MUST apply those constraints through their enforcement configuration;
authority decisions and grants are not added to the Module Loader-owned realization descriptor.
Runtime MUST reject the operation if the selected execution path cannot enforce a required constraint.
Route checks and Capability Authority decisions do not contain malicious direct same-address-space code.
Runtime MUST NOT claim containment against code that can access Runtime memory or unrestricted process resources.
Such code requires trust or a profile-defined in-process containment mechanism.

A package or module manifest's requested permissions are policy inputs.
They do not create a grant or authorize realization, initialization, provider access, or operating-system access.
Capability Authority maps each declared permission into one or more authority scopes
according to the permission's defining specification or profile.

### 3.4 Remote Runtime Enrollment

`remote_enrollment_scope` covers enrolling, refreshing, or removing an identified remote Runtime
for Runtime Control or provider-access eligibility.
Enrollment does not authorize a concrete Runtime Control method or provider route;
that operation requires its corresponding scope.
The remote Runtime identifier does not authenticate the remote Runtime by itself.
An allow decision for an enrollment change authorizes that change,
but it does not validate the enrollment record, certificate, public key, or trust anchor.
Runtime and the selected remote identity profile remain responsible for those checks.

### 3.5 Operating-System And Profile-Defined Permissions

`permission_scope` covers authority that is not represented by the preceding Core scope shapes.
The `permission` field MUST unambiguously identify a specification or selected profile
that defines the permission and its constraint schema.
The `constraints` byte string contains one Logos deterministic-CBOR value
that MUST conform to that definition's CDDL.
Capability Authority MUST reject an unknown permission or invalid constraints.

A profile that permits operating-system or platform access MUST define permission names and constraints
for every facility it exposes.
Relevant facilities include:

- network connection, listening, protocol, destination, and port access;
- filesystem read, write, create, delete, enumerate, and execute access;
- persistent-state allocation, use, sharing, inspection, retention, deletion, migration, and restoration;
- process creation, signaling, and execution;
- device, credential, secret, clipboard, notification, and UI integration access;
- CPU, memory, process-count, file-descriptor, storage-growth, and similar resource limits;
- placement, isolation, sandbox, and dangerous host or platform operations.

The permission definition MUST identify the enforcement component
and the behavior required when the constraint cannot be enforced or is revoked.
Capability Authority decides policy;
it does not turn an unenforceable operating-system constraint into an enforceable one.

Runtime enforcement is suitable for lifecycle, routing, provider visibility, route churn, calls, events, subscriptions,
and Runtime-owned resource accounting.
Transport enforcement is suitable for connection, frame-size, replay, and pressure controls.
Module Loader, deployment controls, and operating-system mechanisms enforce the applicable constraints for selected execution forms.
If no active enforcement point can satisfy an allowed permission scope, Runtime MUST fail the dependent operation.

## 4. Commitment Requirements

Authorization and commitment requirements are distinct.
An allow decision states that an operation is permitted;
commitment requirements state which request or successful-response roots must be retained for audit.
Commitment evidence does not grant authority, and a decision identifier is not commitment evidence.

```cddl
logos.capability_authority.commitment_retention = "retain-root"

logos.capability_authority.commitment_requirements = {
    ? request: logos.capability_authority.commitment_retention,
    ? response: logos.capability_authority.commitment_retention,
}
```

`retain-root` requires the Runtime-controlled invocation boundary
to retain the corresponding compact root in the call audit record defined in Section 9.
When `request` or `response` is absent,
the decision adds no retention requirement for that direction.
These fields do not enable commitment computation or add evidence to a method payload.
Runtime and Transport compute and verify the mandatory payload commitments independently of authority policy.

Contract schema roots and method or event declaration roots enter authorization
through `provider_access_scope`, `runtime_control_scope`, and Runtime's exact route-access values.
They MUST be resolved and validated before Capability Authority evaluates them.
A mutable catalog alias, package name, module name, version string, or caller-supplied schema text
MUST NOT substitute for an exact root required by policy.

Package signatures and artifact digests are verified by Package Manager and Runtime
at their respective integrity boundaries.
The `package`, `version`, and `artifact` fields in `module_execution_scope`
identify the verified package facts presented to policy;
the fields are not signatures, digest proofs, or trust anchors.
Capability Authority MUST NOT turn an unverified identifier into trusted package or artifact evidence.

An authenticated remote Runtime identity enters policy only after the selected remote identity profile
has validated its credential and current enrollment.
Provider identity remains the provider address selected and validated by Runtime.
Neither identity grants authority by itself.

Request and response value roots normally do not exist when an allow decision is made.
Commitment requirements tell the enforcement boundary which roots or proofs to compute,
verify, and retain for the operation.
The resulting roots are linked to the decision, exact call scope, and enforcement outcome
through the audit rules in Section 9.

Trust stores, catalogs, transparency logs, consensus systems,
and equivalent mechanisms may supply verified policy inputs under a selected profile.
They do not create a grant or allow decision merely by containing a root or claim.
Capability Authority MUST consume only inputs accepted through active protected trust input
and MUST NOT add a trust anchor from an evaluation request or evidence supplied by its caller.

An allow decision MAY add a request or response `retain-root` requirement.
It MUST NOT remove a retention requirement carried by the request or a supporting grant.
Failure to satisfy an allow decision's commitment requirements is an enforcement failure, not a policy denial.

## 5. Decisions

Capability Authority evaluates one attempted operation for one consumer against active policy.
A request may carry more than one scope when the operation requires multiple simultaneous constraints,
such as module execution plus network and persistent-state permissions.
An evaluation request MUST NOT combine independent operations.
Each action-bearing scope in an evaluation request MUST name only the action being evaluated;
method and event lists may additionally bound the route or operation.
A grant may contain multiple actions and scopes.

The result is `allow` or `deny`.
An allow decision applies only to the requested operation and allowed scopes.
It does not create a grant, route, invocation descriptor, provider selection, module lifecycle transition,
or operating-system permission.
A denial is an explicit policy outcome.
Inability to evaluate a request is an evaluation failure and MUST be returned as an error rather than a deny decision.

```cddl
logos.capability_authority.timestamp = uint64
logos.capability_authority.grant_id = tstr .size (1..128)
logos.capability_authority.cursor = tstr .size (1..512)

logos.capability_authority.decision_result = "allow" / "deny"

logos.capability_authority.denial_code =
    "not-granted" /
    "scope-denied" /
    "consumer-denied" /
    "target-denied" /
    "approval-required" /
    "grant-expired" /
    "grant-revoked"

logos.capability_authority.denial = {
    code: logos.capability_authority.denial_code,
    ? message: tstr .size (0..512),
}

logos.capability_authority.evaluate_request = {
    consumer: logos.runtime.module_instance_address,
    scopes: [* logos.capability_authority.scope],
    ? commitment: logos.capability_authority.commitment_requirements,
}

logos.capability_authority.decision = {
    decision_id: logos.capability_authority.decision_id,
    result: logos.capability_authority.decision_result,
    consumer: logos.runtime.module_instance_address,
    requested_scopes: [* logos.capability_authority.scope],
    ? allowed_scopes: [* logos.capability_authority.scope],
    issued_at: logos.capability_authority.timestamp,
    ? valid_until: logos.capability_authority.timestamp,
    ? grant_ids: [* logos.capability_authority.grant_id],
    ? commitment: logos.capability_authority.commitment_requirements,
    ? denial: logos.capability_authority.denial,
}

logos.capability_authority.evaluate_response =
    { decision: logos.capability_authority.decision } /
    { error: logos.capability_authority.error }
```

`timestamp` is the number of whole milliseconds since 1970-01-01T00:00:00Z.
The `decision_id` identifies the decision for use by Runtime route and audit records.
It is an opaque correlation value, not a bearer credential or proof of authority.

An allow decision MUST contain `allowed_scopes` and MUST NOT contain `denial`.
A deny decision MUST contain `denial` and MUST NOT contain `allowed_scopes`, `valid_until`, `grant_ids`, or `commitment`.
An allow decision MUST list every grant on which it depends.
Its `valid_until`, when present, MUST be later than `issued_at`
and MUST NOT be later than the expiry of any expiring supporting grant.
Runtime MUST verify that the decision's consumer and requested scopes match its request.
Every allowed scope MUST be equal to or narrower than at least one requested scope.
For every requested scope, an allow decision MUST contain at least one equal or narrower allowed scope.
Runtime MUST enforce every allowed scope and MUST verify that the attempted operation satisfies every narrowing
introduced by those scopes.
An allow decision that omits coverage for a requested scope, broadens a requested scope,
or contains an allowed scope that Runtime cannot enforce is malformed and MUST fail closed as an evaluation failure.

If `valid_until` is absent, Runtime MUST NOT reuse the decision for another operation.
If `valid_until` is present, Runtime may cache the decision only under the rules in Section 8
and MUST treat it as expired when the current time is greater than or equal to `valid_until`.

## 6. Grants And Revocation

A grant is durable authority policy state for one target module instance.
It may support more than one decision until it expires or is revoked.
Not every allow decision requires a grant; Capability Authority may decide directly from active policy.

The `grant_id` identifies the grant for lookup and revocation.
It is not a bearer credential and MUST NOT be accepted as proof of authority.
A grant does not create Runtime lifecycle, provider, route, transport-session, or operating-system state.

```cddl
logos.capability_authority.grant_status = "active" / "expired" / "revoked"

logos.capability_authority.grant = {
    grant_id: logos.capability_authority.grant_id,
    target: logos.runtime.module_instance_address,
    scopes: [* logos.capability_authority.scope],
    issued_at: logos.capability_authority.timestamp,
    ? expires_at: logos.capability_authority.timestamp,
    status: logos.capability_authority.grant_status,
    ? commitment: logos.capability_authority.commitment_requirements,
    ? revoked_at: logos.capability_authority.timestamp,
    ? revocation_reason: tstr .size (0..512),
}

logos.capability_authority.issue_grant_request = {
    consumer: logos.runtime.module_instance_address,
    target: logos.runtime.module_instance_address,
    scopes: [* logos.capability_authority.scope],
    ? expires_at: logos.capability_authority.timestamp,
    ? commitment: logos.capability_authority.commitment_requirements,
}

logos.capability_authority.issue_grant_response =
    { grant: logos.capability_authority.grant } /
    { denial: logos.capability_authority.denial } /
    { error: logos.capability_authority.error }

logos.capability_authority.revoke_grant_request = {
    consumer: logos.runtime.module_instance_address,
    grant_id: logos.capability_authority.grant_id,
    ? reason: tstr .size (0..512),
}

logos.capability_authority.revoke_grant_response =
    { grant: logos.capability_authority.grant } /
    { error: logos.capability_authority.error }

logos.capability_authority.get_grant_request = {
    consumer: logos.runtime.module_instance_address,
    grant_id: logos.capability_authority.grant_id,
}

logos.capability_authority.get_grant_response =
    { grant: logos.capability_authority.grant } /
    { error: logos.capability_authority.error }

logos.capability_authority.list_grants_request = {
    consumer: logos.runtime.module_instance_address,
    ? target: logos.runtime.module_instance_address,
    ? status: logos.capability_authority.grant_status,
    ? cursor: logos.capability_authority.cursor,
    ? limit: uint16,
}

logos.capability_authority.list_grants_response =
    {
        grants: [* logos.capability_authority.grant],
        ? next_cursor: logos.capability_authority.cursor,
    } /
    { error: logos.capability_authority.error }
```

On `issue_grant`, `consumer` is the authenticated invoker and `target` is the module instance to which the resulting grant would apply.
Authority to invoke `issue_grant` does not itself permit the requested grant; active policy must allow the consumer to issue the requested scopes to that target.

If `limit` is absent, the default is 100 records.
If it is present, it MUST be in the inclusive range from 1 through 1000.
Each cursor is opaque, bound to the authenticated consumer and original query, and does not grant authority.
Capability Authority MUST filter grants to those the authenticated consumer may inspect before applying the limit or creating a cursor.
A cursor and result count MUST NOT reveal whether additional hidden grants exist.

At a check time `now`, a grant with `expires_at` is expired when `now` is greater than or equal to `expires_at`.
There is no expiry grace interval.
Capability Authority and Runtime use the local Unix-time domain defined for `timestamp`;
this contract defines no distributed clock-synchronization or clock-skew protocol.

An issued grant MUST initially be `active`.
Its `expires_at`, when present, MUST be later than `issued_at` and later than the time at which the grant becomes active.
An `active` grant MUST omit `revoked_at` and `revocation_reason`,
and its `expires_at` MUST be absent or later than `now`.
An `expired` grant MUST contain `expires_at`, MUST satisfy `now >= expires_at`,
and MUST omit `revoked_at` and `revocation_reason`.
A `revoked` grant MUST contain `revoked_at` that is not earlier than `issued_at`.
It MAY contain `revocation_reason`.
If a revoked grant has `expires_at`, `revoked_at` MUST be earlier than `expires_at`.

The only grant-state transitions are `active` to `expired` and `active` to `revoked`.
The first terminal transition wins.
A revoked grant remains `revoked` after its original expiry time,
and an expired grant cannot subsequently become `revoked`.
Capability Authority MUST treat a grant as expired at the expiry boundary
even if persistence or event-publication work for the transition is still pending.

Revoking or expiring a grant prevents it from supporting new decisions
and invalidates every cached decision that lists that grant.
Revoking an already revoked grant is idempotent and returns its current record.
Attempting to revoke an expired grant returns `grant-not-active`.

Grant administration methods MUST be available only through explicitly authorized provider access.
Capability Authority MUST use Runtime-supplied authenticated call context
to determine who requested issuance, inspection, or revocation.
It MUST NOT trust a policy-source or administrator identity supplied as an unverified method field.

Deployment policy, protected local configuration, an authorized module invocation,
or an administrator action may cause grants to be issued.
This specification does not define their user interface or configuration syntax.
Every resulting grant MUST have the same record and revocation semantics.

## 7. Errors And Denials

```cddl
logos.capability_authority.error_code =
    "invalid-request" /
    "not-authorised" /
    "unsupported-scope" /
    "unknown-permission" /
    "invalid-constraints" /
    "grant-not-found" /
    "grant-not-active" /
    "authority-unavailable" /
    "internal-error"

logos.capability_authority.error = {
    code: logos.capability_authority.error_code,
    ? message: tstr .size (0..512),
}
```

`denial` records an explicit policy result for the attempted operation.
`error` records inability to process or evaluate the request.
Capability Authority MUST NOT return a deny decision merely because it is unavailable, lacks required state,
encounters an internal error, or cannot validate the request.
Runtime MUST fail closed for the attempted operation in both cases
while retaining the distinction for observation and audit.

Messages are diagnostic and MUST NOT expose secrets, credentials, full route tickets,
policy internals, or sensitive host paths.
They MUST NOT expose information the authenticated consumer is not authorized to observe.
When Runtime maps a discovery or route outcome to a caller-facing error,
it MUST apply the non-disclosure rules in LOGOS-MODULE-RUNTIME.

## 8. Change Notification, Caching, And Enforcement

```cddl
logos.capability_authority.grant_changed_event = {
    grant: logos.capability_authority.grant,
}

logos.capability_authority.policy_changed_event = {
    changed_at: logos.capability_authority.timestamp,
}
```

`changed_at` is the time at which the new active policy takes effect.
The corresponding `policy-change` audit record MUST use the same timestamp.

Runtime may reuse an allow decision only while all of the following remain true:

- `valid_until` is present and the current time is earlier than it;
- every supporting grant remains active and unexpired;
- the consumer, target, operation, and requested scope still match;
- every enforcement point required by the allowed scopes remains active;
- Runtime has a working grant and policy change notification path to Capability Authority.

If the notification path is lost, Runtime MUST invalidate every cached decision from that Capability Authority.
It MUST NOT perform another protected operation in reliance on an invalidated decision.
Runtime MAY retain allocated routes or sessions while obtaining a fresh decision,
but they MUST remain unusable for protected operations until reauthorized.

Runtime MUST re-establish and confirm the grant and policy change notification path
before a fresh evaluation may seed its decision cache.
It MUST rebuild cache entries from fresh evaluations as protected operations require them
and MUST NOT depend on reconstructing a snapshot of policy or grant state.
If the re-established notification path is lost, Runtime MUST invalidate every newly cached decision again.

Capability Authority MUST emit `grant_changed` when a grant is issued, revoked, or becomes expired.
It MUST emit `policy_changed` whenever active policy changes in a way that may affect an authority result.
Capability Authority MUST order each grant or policy state transition with its corresponding event.
The new state MUST become active before the event can be observed,
and the event MUST be committed to each applicable active Runtime notification path as part of that ordered transition.
An evaluation ordered before the transition may observe the old state,
in which case the later event invalidates its cached decision.
An evaluation ordered after the transition MUST observe the new state.
Event delivery MUST either succeed according to the subscription rules
or cause Runtime to detect notification-path loss and invalidate all cached decisions.

On `policy_changed`, Runtime MUST invalidate every cached decision from that Capability Authority.
On grant revocation or expiry, Runtime MUST invalidate every cached decision that lists the changed grant.
Grant issuance does not make a prior decision broader and does not authorize an operation by itself.
Emission does not by itself authorize delivery to every subscriber.
Capability Authority and Runtime MUST deliver a change event only while the subscriber
remains authorized for that event and the included grant or policy-change information.
An event payload, subscription result, or diagnostic MUST NOT reveal a hidden grant.
A Runtime notification path is working for cache reuse only if it remains authorized
to receive every change that can invalidate the cached decision.
Loss of that visibility is notification-path loss and requires full cache invalidation.

After a policy change, Runtime MUST re-evaluate dependent operations
before performing another protected operation.
Protected operations include new calls, route creation or renewal,
observations, lifecycle changes, and enrollment changes.
It MUST make a dependent route unusable when the new decision denies the route
or narrows its scope below the route's bound scope.

After grant revocation or expiry, Runtime MUST prevent new dependent operations.
It MUST terminate dependent provider sessions and subscriptions when their continued use would exceed current authority.
When a required operating-system permission is revoked,
its enforcement component MUST withdraw the permission or Runtime MUST stop the execution form.
An implementation SHOULD cancel in-flight work when safe and supported.
If cancellation is impossible, it MUST prevent follow-on operations and retain an audit record of the limitation.

Runtime owns enforcement and the mapping of decisions to Runtime, Transport,
Module Loader, and platform error channels.
Capability Authority MUST NOT directly mutate Runtime lifecycle, provider, route, Runtime Control,
or transport-session state.

## 9. Audit Records

The common audit record covers Capability Authority policy activity
and retained evidence from Runtime-enforced calls without defining a separate audit identity.
One decision, grant, route, or call may correspond to multiple audit records.

```cddl
logos.capability_authority.audit_value_commitment = {
    schema_subtree_root: bstr .size 32,
    value_root: bstr .size 32,
}

logos.capability_authority.call_commitments = {
    request: logos.capability_authority.audit_value_commitment,
    ? response: logos.capability_authority.audit_value_commitment,
} / {
    response: logos.capability_authority.audit_value_commitment,
}

logos.capability_authority.audit_record =
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "evaluate",
        outcome: "allow",
        consumer: logos.runtime.module_instance_address,
        decision_id: logos.capability_authority.decision_id,
        scopes: [* logos.capability_authority.scope],
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "evaluate",
        outcome: "deny",
        consumer: logos.runtime.module_instance_address,
        decision_id: logos.capability_authority.decision_id,
        scopes: [* logos.capability_authority.scope],
        denial: logos.capability_authority.denial,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "evaluate",
        outcome: "failure",
        consumer: logos.runtime.module_instance_address,
        ? scopes: [* logos.capability_authority.scope],
        error: logos.capability_authority.error_code,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "call",
        outcome: "success",
        consumer: logos.runtime.module_instance_address,
        decision_id: logos.capability_authority.decision_id,
        scopes: [logos.capability_authority.scope],
        commitments: logos.capability_authority.call_commitments,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "call",
        outcome: "failure",
        consumer: logos.runtime.module_instance_address,
        decision_id: logos.capability_authority.decision_id,
        scopes: [logos.capability_authority.scope],
        ? commitments: logos.capability_authority.call_commitments,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "issue-grant",
        outcome: "success",
        ? consumer: logos.runtime.module_instance_address,
        target: logos.runtime.module_instance_address,
        grant_id: logos.capability_authority.grant_id,
        scopes: [* logos.capability_authority.scope],
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "issue-grant",
        outcome: "deny",
        consumer: logos.runtime.module_instance_address,
        target: logos.runtime.module_instance_address,
        scopes: [* logos.capability_authority.scope],
        denial: logos.capability_authority.denial,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "issue-grant",
        outcome: "failure",
        consumer: logos.runtime.module_instance_address,
        target: logos.runtime.module_instance_address,
        scopes: [* logos.capability_authority.scope],
        error: logos.capability_authority.error_code,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "revoke-grant",
        outcome: "success",
        ? consumer: logos.runtime.module_instance_address,
        target: logos.runtime.module_instance_address,
        grant_id: logos.capability_authority.grant_id,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "revoke-grant",
        outcome: "failure",
        consumer: logos.runtime.module_instance_address,
        ? target: logos.runtime.module_instance_address,
        grant_id: logos.capability_authority.grant_id,
        error: logos.capability_authority.error_code,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "grant-expired",
        outcome: "success",
        target: logos.runtime.module_instance_address,
        grant_id: logos.capability_authority.grant_id,
    } /
    {
        timestamp: logos.capability_authority.timestamp,
        operation: "policy-change",
        outcome: "success",
    }

logos.capability_authority.query_audit_request = {
    consumer: logos.runtime.module_instance_address,
    ? record_consumer: logos.runtime.module_instance_address,
    ? target: logos.runtime.module_instance_address,
    ? decision_id: logos.capability_authority.decision_id,
    ? grant_id: logos.capability_authority.grant_id,
    ? since: logos.capability_authority.timestamp,
    ? until: logos.capability_authority.timestamp,
}

logos.capability_authority.query_audit_response =
    {
        records: [* logos.capability_authority.audit_record],
    } /
    { error: logos.capability_authority.error }
```

`query_audit` returns at most the 1000 most recent retained records that match the request and are visible to the authenticated consumer.
The records are ordered newest first.

`consumer` in `query_audit_request` is the authenticated invoker.
`record_consumer` and `target` are optional record filters; they do not supply query authority.
In an audit record, `consumer` identifies the module instance whose authority was used for the recorded operation.
`target` identifies a separate module instance affected by that operation when one exists.
The CDDL variants define the complete common field set for each operation and outcome.
A field not admitted by the selected variant is forbidden.
`denial` appears only with `deny`, and `error` appears only with `failure`.

The valid operation and outcome combinations are:

| Operation | Outcomes |
|-----------|----------|
| `evaluate` | `allow`, `deny`, `failure` |
| `call` | `success`, `failure` |
| `issue-grant` | `success`, `deny`, `failure` |
| `revoke-grant` | `success`, `failure` |
| `grant-expired` | `success` |
| `policy-change` | `success` |

An `evaluate` allow record contains its exact allowed scopes.
An `evaluate` deny record contains its requested scopes and denial.
An `evaluate` failure record MAY contain the requested scopes only when they were successfully decoded and validated.
Because a failure produces no decision, it contains neither `decision_id` nor `denial`.

Successful grant issuance contains the issued grant identifier, target, and exact issued scopes.
Grant denial contains the requested target, scopes, and denial but no grant identifier.
An authenticated grant-administration attempt identifies its consumer.
A successful grant issuance or revocation caused by protected policy or an administrative action
without an invoking module instance omits `consumer`.
A revocation failure MAY contain `target` only when the grant resolved and its target is known.
Grant expiry and policy change have no invoking contract consumer in the common record.

Capability Authority MUST produce an audit record for each evaluation result or failure, grant issuance,
grant revocation, grant expiry, and policy change.
Retention duration and storage realization are deployment or audit-profile policy.

When an applied allow decision requires request or response retention for a call,
the Runtime-controlled invocation boundary MUST produce a `call` audit record
after the corresponding enforcement outcome.
The record MUST contain the decision's `decision_id` and exact allowed call scope.
Its `scopes` array MUST contain exactly one of these call scopes:

- a `provider_access_scope` with the `call` action,
  one route, one selected provider, the selected contract, and one method declaration root; or
- a `runtime_control_scope` naming the invoked Runtime and Runtime Control contract,
  with `methods` containing exactly one method declaration root and `events` absent.
  Every other present constraint MUST equal the constraint applied to the call.

The record MUST contain the `request` or `response` commitment
for each applicable `retain-root` requirement whose value was produced and successfully committed.
If a required value was not produced or could not be committed,
the record MUST use the `failure` outcome and MUST NOT claim a commitment for that value.
A successful call record MUST contain non-empty `commitments`.
A failed call record MAY omit `commitments` when no required value was successfully produced and committed.
If a failed call record contains `commitments`, they MUST contain only successfully retained sides.
The CDDL forbids an empty `call_commitments` value and forbids `commitments` on every non-call record.

The call scope records the invoked contract.
A provider-access call scope records the selected provider contract,
and a Runtime Control call scope records the invoked Runtime Control contract.
For a method defined by that contract, the contract also supplies the defining schema root, commitment-model revision, hash profile, and hash suite.
For the well-known `logos.schema` method, the pinned Logos common schema supplies those defining-contract inputs while the call scope's contract continues to identify the selected contract being introspected.
Each `schema_subtree_root` identifies the request or response type under the defining contract,
and `value_root` is the corresponding root computed or verified under those exact inputs.
An `audit_value_commitment` is therefore not meaningful without the exact call scope in the same record.
For an implemented interface method, the defining contract remains the implemented interface contract.
The audit record identifies the schema method, not the generic dispatch entrypoint.

`retain-root` stores the applicable `audit_value_commitment`.
Commitment requirements do not require a verified-view proof
and do not add proof fields to ordinary Requests, Responses, Events, or `audit_record`.
If an authorized audit integration retains a verified-view proof for later disclosure,
the call-evidence profile defines how that proof is bound to the audit record.
This keeps routine audit queries bounded and avoids disclosing proof contents to callers authorized to see only roots.

### 9.1 Call-Evidence Profile

Every conforming Runtime MUST implement `logos.call-evidence.cose-sign1-ed25519` for call evidence.
Local audit retention does not require a signed container,
and an implementation need not export call evidence unless selected audit policy requires it.
The profile binds one complete `call` audit record to zero or more retained verified-view proofs.
It does not define another audit record, query method, evidence identity, or batch format.

The signed payload is this Logos deterministic-CBOR claim:

```cddl
logos.capability_authority.call_evidence_profile =
    "logos.call-evidence.cose-sign1-ed25519"

logos.capability_authority.evidence_key_id = bstr .size (1..128)

logos.capability_authority.call_evidence_proofs = {
    ? request: [* bstr],
    ? response: [* bstr],
}

logos.capability_authority.call_evidence_claim = {
    profile: logos.capability_authority.call_evidence_profile,
    producer: logos.runtime.runtime_instance_id,
    record: logos.capability_authority.audit_record,
    ? proofs: logos.capability_authority.call_evidence_proofs,
}
```

The container MUST be one tagged `COSE_Sign1` object using CBOR tag 18 from RFC 9052
and the fully specified `Ed25519` COSE algorithm `-19` from RFC 9864.
The protected header map MUST contain exactly `alg`, with COSE label `1` and value `-19`,
and `kid`, with COSE label `4` and a `logos.capability_authority.evidence_key_id` value.
The unprotected header map MUST be empty.
The outer object and serialized protected header map MUST use the core deterministic encoding requirements
of RFC 8949 Section 4.2.1.

The payload MUST be embedded as a byte string containing the exact deterministic-CBOR claim.
Detached payloads, additional protected or unprotected headers,
multiple signatures, countersignatures, and critical-header extensions are not accepted.
The RFC 9052 `Signature1` structure uses the protected header bytes from the object,
a zero-length `external_aad`, and the exact embedded payload bytes.
The profile defines no nonce or external signing context.
Its signed profile identifier provides application-level domain separation.

Protected trust input MUST map each accepted `kid`
to exactly one producer Runtime identity and one exact 32-byte Ed25519 public key encoded according to RFC 8032.
It MUST authorize that key specifically for call-evidence signing.
The same key material MUST NOT be used for package signing or TLS authentication.
Two accepted evidence keys MUST NOT use the same `kid`.
The `kid` selects candidate verification material and does not establish trust by itself.

An evidence-signing private key uses a 32-byte Ed25519 seed generated with a cryptographically secure random generator.
The Runtime host or its protected signing integration MUST keep the evidence-signing private key secret and protect it against unauthorized signing.
An Ed25519 signature is exactly 64 bytes.
Rotation installs a new key under a new `kid` before the producer begins using it;
both keys may be accepted during a bounded operational overlap.
Evidence under an unknown or revoked `kid` MUST be rejected.
In this baseline, revocation invalidates all evidence under that key.
The profile has no signing time, expiry, or clock-skew processing
and does not claim that a signed record is fresh.

The signed `record` MUST satisfy every `call` audit-record rule in this section.
The `producer` MUST equal the Runtime identity authorized for the selected `kid`
and MUST identify the Runtime whose controlled invocation boundary produced the record.
If `proofs` is present, it MUST contain at least one request or response proof.
Each proof byte string MUST contain exactly one Logos deterministic-CBOR `verified-view`
defined by LOGOS-MODULE-HASH-PROFILE.
Every proof MUST correspond to an existing commitment on the same side of the signed record.

For each proof, the verified-view schema root, hash-profile identifier, hash-suite identifier,
and commitment-model revision MUST equal the corresponding fields of the method's defining contract.
The verifier MUST determine that contract from the signed call scope's selected contract and single method declaration root according to Section 9.
For a `logos.schema` proof, the verified-view schema root is therefore the pinned Logos common schema root while the signed scope's contract remains the selected contract.
Its schema subtree root and value root MUST equal the corresponding signed `audit_value_commitment`.
The verifier MUST then validate the complete verified view according to LOGOS-MODULE-HASH-PROFILE.
An absent commitment, side mismatch, root or profile mismatch, malformed proof,
or failed proof verification invalidates the whole container.

The verifier MUST reject a malformed or non-deterministic container or claim,
an unknown or duplicate `kid`, an unaccepted header or algorithm,
an invalid key or signature length, a failed signature,
an incorrect profile identifier, an unauthorized producer,
or any record or proof mismatch described above.
The container authenticates the retained evidence as a statement by the authorized producer.
It does not grant authority, prove package or provider trust, or establish freshness.

This baseline provides authenticity and integrity, not confidentiality.
Before disclosing a container,
the producer MUST apply the same audit authorization and visibility rules as `query_audit`.
Sensitive evidence requires confidentiality-protected transport and storage.
This specification does not define a second encrypted evidence format.

Capability Authority need not participate in ordinary module data flow.
Runtime may retain call records and proofs directly or deliver them through a protected audit integration.
When a Capability Authority implementation stores those records,
`query_audit` returns them under the same authorization, visibility, ordering,
and result-bound rules as its other records.

Audit queries MUST require explicit authorization and MUST filter or redact information the authenticated consumer is not allowed to observe.
Audit records MUST NOT contain full route tickets, bearer credentials, private keys, or secrets.
Sensitive constraint values require protection and explicit audit authorization before retention.
Implementations MAY retain additional local audit detail, but the fields above define the common observation shape.

Because `query_audit` returns only the 1000 most recent matching records, a consumer that generates many auditable operations could push an earlier record outside the bounded query window.
This does not remove the record from retained audit storage.
Operators can review older records in the retained audit storage.

## 10. Capability Authority Methods And Events

The Capability Authority contract defines these methods:

- `evaluate`;
- `issue_grant`;
- `revoke_grant`;
- `get_grant`;
- `list_grants`;
- `query_audit`.

The contract defines these events:

- `grant_changed`;
- `policy_changed`.

`evaluate` is the Runtime-facing policy-decision method.
Runtime MUST be authorized to invoke it through the bound system-service route.
Ordinary consumers MUST NOT gain direct authority to call `evaluate`
merely because they can request a provider route or invoke another Capability Authority method.

The grant and audit methods require their own provider-access authorization.
A consumer authorized to inspect grants whose target equals that consumer does not thereby gain authority to inspect or modify grants targeting another module instance.
Authority to invoke `get_grant` or `list_grants` does not by itself authorize every matching record.
Capability Authority MUST apply target and scope visibility before returning a grant.
The target, scopes, time bounds, status, commitment requirements, and revocation time are semantic grant fields.
Capability Authority MUST return those fields unchanged or omit the grant.
If those fields cannot be disclosed,
the grant is omitted from a list response or the lookup fails.
After method authorization,
an unknown grant and a grant hidden from the consumer both produce `grant-not-found`.
Grant issuance and revocation do not themselves authorize a protected operation.
A grant may support a protected operation only when its target is the operation's consumer and its scopes cover the attempted operation.

## 11. Route And Credential Boundary

Decision identifiers and grant identifiers are correlation values, not credentials.
They MUST NOT be presented by consumers as proof of authority and MUST NOT be accepted as bearer tokens.

After an allow decision for provider access, Runtime creates or renews the route and binds its allowed scope.
Runtime supplies the invocation descriptor and route authorization material required by the selected transport profile.
Capability Authority does not issue that descriptor or ticket and does not become a proxy for ordinary module data.

A protected transport profile MUST bind its route ticket or session credential to the consumer or authenticated session,
selected provider, selected contract, and allowed method and event scope.
It MUST also bind the target endpoint, Runtime route, authority decision, freshness, and revocation state.
When the profile uses a one-time route ticket, the ticket is consumed to establish one authenticated session;
it is not consumed separately by each call on that session.
The provider-side invocation boundary validates that material before dispatch
and enforces the bound scope for the session.
Missing, empty, invalid, expired, revoked, replayed, or incorrectly bound authorization material
MUST produce no usable protected session and no ordinary module dispatch.
After session establishment, ordinary module data flows between the consumer and the provider-side boundary
without passing through Capability Authority.
The mandatory remote-transport profiles use
`logos.route-ticket.random-256` from LOGOS-MODULE-TRANSPORT
for provider-session establishment.
Logos Core defines no generic bearer capability, signed authority decision, or COSE authorization token.
Package-signature and call-evidence COSE objects MUST NOT be accepted as authorization material.

Runtime MUST NOT place secret route tickets, private keys, or reusable bearer credentials
in grant, decision, audit, Module Loader realization, package, or module lifecycle records.

## 12. Enforcement Summary

| Scope or requirement | Decision owner | Enforcement owner |
|----------------------|----------------|-------------------|
| Provider visibility, route creation, method calls, and events | Capability Authority or internal Runtime policy | Runtime and the provider-side invocation boundary |
| Runtime Control and lifecycle observation | Capability Authority or internal Runtime policy | Runtime |
| Direct native realization and initialization | Capability Authority or internal Runtime policy | Runtime before handoff; Module Loader during realization |
| Process, sandbox, or container realization | Capability Authority or deployment policy | Runtime before handoff; Module Loader and deployment controls during realization |
| Remote Runtime enrollment | Capability Authority or internal Runtime policy | Runtime and the selected remote-trust profile |
| Network, filesystem, process, device, credential, and platform access | Capability Authority or selected profile policy | Module Loader, deployment controls, operating-system mechanisms, or another enforcement point named by the permission definition |
| Runtime-owned route, event, subscription, and resource limits | Capability Authority or selected profile policy | Runtime or Transport, according to the controlled resource |
| Commitment and proof requirements | Capability Authority or commitment policy | Runtime, Transport, or verifier named by the selected profile |

An allow decision is usable only when every required enforcement owner can enforce its part of the allowed scope.
Successful schema validation, package resolution, artifact lookup, provider discovery,
or transport connection does not grant authority.
Neither module admission, Module Loader realization, nor commitment verification grants authority by itself.

## 13. Security And Privacy Requirements

Capability Authority is security-critical local code.
Runtime MUST treat an unavailable, malformed, mismatched, expired, or unverifiable decision
as an evaluation failure and fail closed.
Runtime MUST validate every decision before enforcement
and MUST NOT let a module bypass the decision path through a direct SDK, loader, Transport, or provider-host API.

Grant administration and audit observation MUST follow least privilege.
Permission constraints and audit records may reveal filesystem paths, network destinations, installed modules,
remote Runtimes, user choices, or security posture.
Implementations MUST minimize disclosure
and apply the same authority checks to query results as to the underlying operations.

Full route tickets, proof-of-possession secrets, private keys, and reusable credentials MUST NOT be logged.
Diagnostic correlation SHOULD use non-secret decision, grant, route, and consumer references.

Capability Authority policy does not make direct same-address-space code safe
against memory corruption or deliberate policy bypass.
Untrusted code requires a selected execution and isolation profile
whose controls can enforce the permissions granted to it.

---

## References

### Normative

- [RFC 8032] -- Edwards-Curve Digital Signature Algorithm (EdDSA).
  https://www.rfc-editor.org/rfc/rfc8032
- [RFC 8949] -- Concise Binary Object Representation (CBOR).
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 9052] -- CBOR Object Signing and Encryption (COSE): Structures and Process.
  https://www.rfc-editor.org/rfc/rfc9052
- [RFC 9864] -- Fully-Specified Algorithms for JOSE and COSE.
  https://www.rfc-editor.org/rfc/rfc9864

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
