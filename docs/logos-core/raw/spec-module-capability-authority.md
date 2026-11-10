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

## Requirements Language

Uppercase requirement keywords in this specification follow BCP 14 [RFC 2119] [RFC 8174].
Lowercase forms retain their ordinary English meanings.

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

Every grant `target` field contains a module-instance address.
Every `consumer` field contains a module-instance address.
`consumer` identifies whose authority is used to authorize or evaluate the operation.
In a grant, `target` names the module instance to which that grant applies.
Consumer and target are authorization roles; neither creates another module entity type.
An address used to authenticate a consumer, issue a grant to a target, or apply authority MUST resolve to the exact Runtime-known module instance concerned.
Retained grant and audit records MAY name historical module-instance addresses that no longer resolve.
Query filters MAY name those historical addresses; disclosure still requires current authorization for the querying consumer and the records.
A historical reference MUST NOT authenticate a current instance, establish its liveness, or transfer authority to another address.
The Runtime engine, Runtime host, bootstrap machinery, operating-system objects, protected inputs, humans, and unauthenticated peers MUST NOT be represented as module instances.

`logos.runtime.module_instance_address` identifies a module instance, including in retained historical references.
Its `runtime_instance_id` identifies the owning Runtime, and its `module_instance_id` identifies the module instance within that Runtime.
The address does not authenticate the module instance or grant authority.

Runtime MUST supply Capability Authority with authenticated context for the consumer.
Runtime MUST populate or validate the request's `consumer` against that context before dispatching a Capability Authority method.
For `evaluate`, Runtime supplies the module instance whose authority is required for the attempted operation under LOGOS-MODULE-RUNTIME.
Runtime's protected invocation on behalf of a module MUST preserve that module as consumer.
For other methods, the consumer is the module instance authenticated at the Capability Authority invocation boundary.
A request may separately name a target module instance.
A target does not supply the authority used to invoke the method and does not become the consumer.

Every decision identifies the consumer whose authority was evaluated.
Every grant identifies the target module instance to which its scopes apply.
Authority accepted for an inbound route or call applies only within its allowed scope.
It does not transfer the consumer's authority to the provider that handles the call.
When that provider initiates another operation, Runtime uses the provider's backing module instance as the consumer.

When policy evaluation requires attributes beyond the contract's consumer and scopes, the deployment MUST define a protected attribute-source integration.
It MUST identify authoritative sources, bind each required fact to the evaluated consumer or target and operation, and specify disclosure, freshness, and failure rules.
A caller-supplied attribute or claimed identity MUST NOT establish those facts without independent validation.
Capability Authority does not receive unrestricted Runtime Control visibility by virtue of its role; any module invocation used to obtain facts requires its own authority.
Obtaining evaluation prerequisites MUST NOT recursively depend on the same evaluation whose prerequisites are being obtained.
Missing, unverifiable, or stale required facts MUST produce an evaluation failure rather than an allow or an invented deny decision.

Attribute snapshots used by evaluation and changes or source loss that can invalidate decisions MUST be ordered with the policy-revision transitions and `policy_changed` event commitment required by Section 8.
An evaluation after such a transition MUST NOT issue a decision from the preceding attribute snapshot.
Freshness expiry MUST cause the same invalidation no later than the required fact's validity end.
An allow decision depending on these facts MUST contain `valid_until` no later than the earliest authoritative validity end of any required fact.
If the integration cannot establish the required change-notification, ordering, and freshness guarantees, a dependent evaluation MUST fail.
Omitting `valid_until` MUST NOT bypass these requirements.
Runtime MUST apply Section 8 invalidation and execution-enforcement rules to those transitions, including source or notification-path loss.
Attribute acquisition encoding is deployment-specific; this contract defines no generic attribute bag or interoperable attribute-query protocol.

## 3. Authority Scopes

An authority scope is a value carried by a request, decision, or grant.
It has no identity or lifecycle of its own.
An allow decision MUST NOT broaden a requested scope and MAY narrow it.
A decision based on a grant MUST NOT exceed that grant's current scope.
For the Core scope shapes, required identity fields MUST be equal, and every constrained list in the narrower scope MUST be a subset of the broader scope.
An optional identity absent from the broader scope is unconstrained;
if it is present, the narrower scope MUST contain the same identity.
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
    actions: [* ("start" / "stop")],
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

`publish-event` authorizes a provider to publish an event to a subscriber on an existing route.
For this action, the evaluation's `consumer` MUST identify the publishing module instance, and the requested `providers` and `routes` MUST identify the event source and subscriber route.
`access.publish_events` constrains which events that provider may publish on the route; it does not define a consumer-to-provider event path.
Event delivery also requires the subscriber's `subscribe-event` authority and MUST satisfy both route event lists.

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

`module_execution_scope` covers Runtime-owned module execution through the `start` and `stop` actions.
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
For both direct and hosted execution, `start` covers loading or realization, initialization, readiness processing, and authorization to continue executing.
A newly accepted `start_module` execution attempt uses the authenticated requesting execution origin's authority.
Recovery or resumption of retained intent and renewal of continued execution use that retained origin's current `start` authority.
The controller invoking recovery separately requires authority for its Runtime Control request; its authority MUST NOT replace the execution origin's.
A `start_module` invocation that only returns an already loaded or ready instance's current state does not create a new execution attempt or renew its authorization.

An explicit `stop_module` invocation targeting a local module instance requires `stop` authority for the calling controller and that execution target, in addition to Runtime Control method/target authority.
Starting, stopping, or detaching only a local remote-module facade uses Runtime Control authorization for that routing state; it does not create a local execution target or authorize lifecycle control at the remote owner.
`stop` includes teardown, unloading, and realization release required by that operation.
Mandatory withdrawal of authority, failed-attempt cleanup, and cleanup under an accepted Runtime shutdown MUST NOT depend on a fresh ordinary `stop` grant or the target module's consent.
Those are Runtime enforcement obligations, including when Capability Authority is unavailable.
Creating or retiring a quiescent instance and administering configuration or permission settings require their own management authorization; they do not introduce execution actions.
Required realization access and permission scopes remain independently applicable.

Outside the initial system-service bootstrap authorized under Section 1 or explicit protected recovery under LOGOS-MODULE-RUNTIME Section 9,
Runtime MUST obtain an allow decision before asking Module Loader to realize a direct native implementation.
The decision MUST cover the module execution operation and every required permission scope.
Runtime MAY allocate the module instance identifier used by the module consumer before loading code;
allocation does not make the module loaded or ready.

Outside those protected bootstrap and recovery paths,
Runtime MUST obtain an allow decision before asking Module Loader to realize a process, sandboxed process, or container.
The decision MUST cover the module execution operation,
selected hosted placement,
and required permission scopes.
Authorization to call the Module Loader provider does not authorize an arbitrary module execution operation.
The module execution decision and authorization of the Module Loader invocation are distinct checks.
For an engine invocation, the latter follows the Runtime-owned system-service binding policy in LOGOS-MODULE-RUNTIME Section 9.
An ordinary module caller requires its own provider-access decision.
Neither invocation authority substitutes for the required execution and permission decision.

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
A profile claiming per-module device restrictions MUST identify the consent principal and the controls preventing a denied module from bypassing the enforcement component.
Process separation, executable signing, or a granted application permission alone MUST NOT establish that claim.
Capability Authority decides policy;
it does not turn an unenforceable operating-system constraint into an enforceable one.

Runtime enforcement is suitable for lifecycle, routing, provider visibility, route churn, calls, events, subscriptions,
and Runtime-owned resource accounting.
Transport enforcement is suitable for connection, frame-size, replay, and pressure controls.
Module Loader, deployment controls, and operating-system mechanisms enforce the applicable constraints for selected execution forms.
If no active enforcement point can satisfy an allowed permission scope, Runtime MUST fail the dependent operation.

A permission enforced by a module provider MUST define how the authenticated enforcing provider obtains the applicable authorization for the checked subject, resource, and operation.
That integration MUST restrict the permissions and subjects the provider may check, define decision validity and invalidation, order revocation against protected effects, and fail closed when required authorization cannot be established.
An ordinary module contract may supply that integration; the checking provider remains its authenticated consumer and MUST NOT impersonate the checked subject.
Grant inspection, grant identifiers, and possession of a module-instance address MUST NOT substitute for authorization.
This rule does not grant ordinary providers access to the Runtime's protected `evaluate` binding.

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
Commitment requirements tell the enforcement boundary which request or successful-response roots to retain for audit.
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
    ? execution_renewal: true,
    ? commitment: logos.capability_authority.commitment_requirements,
}

logos.capability_authority.decision = {
    decision_id: logos.capability_authority.decision_id,
    policy_revision: uint64,
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
It is an opaque correlation value, not a bearer credential, proof of authority, or live-binding selector.
Capability Authority MUST allocate collision-resistant decision identifiers across independent issuers, restarts, replacements, and restoration or cloning of persisted application state.
A restored counter or pseudorandom-generator state alone MUST NOT establish identifier separation from earlier decisions or other issuers.
Allocation MUST use independent protected entropy or an issuer namespace and allocation mechanism that preserve that separation.
An identifier known to identify another decision MUST NOT be reused; if reliable allocation is unavailable, evaluation MUST fail without issuing a decision.
The identifier format and allocation algorithm are implementation choices within the declared field limits.

An allow decision MUST contain `allowed_scopes` and MUST NOT contain `denial`.
A deny decision MUST contain `denial` and MUST NOT contain `allowed_scopes`, `valid_until`, `grant_ids`, or `commitment`.
An allow decision MUST list every grant on which it depends.
Its `valid_until`, when present, MUST be later than `issued_at`
and MUST NOT be later than the expiry of any expiring supporting grant.
An allow decision that depends on an expiring grant MUST contain `valid_until` no later than the earliest expiry of its supporting grants.
This requirement applies even when Runtime will use the decision for only one operation.
Runtime MUST verify that the decision's consumer and requested scopes match its request.
Every allowed scope MUST be equal to or narrower than at least one requested scope.
For every requested scope, an allow decision MUST contain at least one equal or narrower allowed scope.
Runtime MUST enforce every allowed scope and MUST verify that the attempted operation satisfies every narrowing introduced by those scopes.
For Runtime Control scopes that differ only in their subject selectors, those selectors are alternatives.
Runtime MUST require a subject to satisfy at least one complete alternative and every narrowing shared by those alternatives.
Runtime MUST NOT combine selector fields from different alternatives to admit a subject that no individual alternative permits.
An allow decision that omits coverage for a requested scope, broadens a requested scope,
or contains an allowed scope that Runtime cannot enforce is malformed and MUST fail closed as an evaluation failure.

If `valid_until` is absent, Runtime MUST NOT reuse the decision for another operation.
If `valid_until` is present, Runtime may cache the decision only under the rules in Section 8
and MUST treat it as expired when the current time is greater than or equal to `valid_until`.

### 5.1 Execution Renewal Admission

The `execution_renewal` field identifies Runtime's renewal of an existing execution authorization.
Runtime MUST set it only while that authorization remains valid under Section 8 and only for the retained consumer, execution target, and requested scopes.
Runtime MUST reject this field on evaluation requests supplied by ordinary callers, including routed calls.
Capability Authority MUST receive the indication through the Runtime-enforced invocation boundary required by Section 2.
An absent field identifies an ordinary evaluation.
The indication does not grant authority, extend authorization validity, or change policy evaluation.

When deployment policy requires protected execution renewal, Capability Authority MUST reserve finite, nonzero admission capacity for execution-renewal requests that ordinary requests cannot consume.
This protection MUST cover queued and executing work and retained request and response resources owned by Capability Authority.
Renewal requests MAY fail when their reserved capacity is exhausted.
Reserved admission does not guarantee evaluation completion before authorization expiry.
The reservation sizes and scheduling policy are implementation or protected deployment choices.

When deployment policy requires protected execution renewal through this contract, Runtime MUST establish that the selected provider and invocation path support this protection before starting dependent executions.
Runtime MUST set `execution_renewal` for these renewals according to the eligibility rules above.
Module-requested lifecycle operations MUST NOT consume the reserved renewal allowance.

Protection MUST cover every shared allocation, queue, and dispatch boundary on the selected invocation path, including boundaries before the request reaches Capability Authority.
Ordinary request saturation MUST NOT consume reserved renewal capacity or prevent dispatch progress for admitted renewal work.
Reserved admission MUST depend on Runtime-controlled eligibility; the request field alone MUST NOT be treated as proof of that eligibility.
Runtime MUST bound admitted execution demand according to available renewal capacity, including demand from executions sharing a consumer.

Each resource owner on that path MUST retain charges while the charged work or resources remain owned.
Caller timeout, cancellation, connection loss, or binding replacement MUST NOT reclaim capacity still occupied by that work or those resources.
Uncertain charges MUST remain reserved until the charged work and resources are confirmed ended or released, or their owning instance is confirmed terminated.

Runtime MUST reject dependent execution when the required protection cannot be established and invalidate dependent authorization if that protection is lost.
Exhaustion of a configured allowance does not by itself constitute loss of protection.
Runtime MUST continue to enforce authorization expiry and invalidation under Section 8.

## 6. Grants And Revocation

A grant is durable authority policy state for one target module instance.
It may support more than one decision until it expires or is revoked.
Not every allow decision requires a grant; Capability Authority may decide directly from active policy.

The `grant_id` identifies the grant for lookup and revocation.
It is not a bearer credential and MUST NOT be accepted as proof of authority.
A grant does not create Runtime lifecycle, provider, route, transport-session, or operating-system state.

```cddl
logos.capability_authority.grant_status = "active" / "expired" / "revoked"

logos.capability_authority.grant_issuer =
    {
        kind: "module",
        module: logos.runtime.module_instance_address,
    } /
    {
        kind: "protected-policy",
        source: tstr .size (1..128),
    }

logos.capability_authority.grant = {
    grant_id: logos.capability_authority.grant_id,
    issuer: logos.capability_authority.grant_issuer,
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
Authority to invoke `issue_grant` does not itself permit the requested grant; active policy MUST allow the consumer to issue the requested scopes to that target.

Capability Authority MUST derive `issuer` from the authenticated issuing module or the protected policy operation that created the grant.
An issuance request MUST NOT supply or override it.
For protected-policy issuance, `source` is a protected deployment-local origin identifier, not a module principal, credential, or filesystem path.
Issuer attribution MUST remain immutable throughout grant retention, independently of audit-query retention.
A retained module issuer is a historical address and MUST NOT authenticate a later instance or confer authority.
Existing grants with unavailable issuance provenance MUST NOT be assigned an invented issuer.
Migration may populate `issuer` only from authenticated evidence of the original issuance.
Otherwise, an explicitly authorized replacement requires a new grant identifier and records its own issuer; it MUST NOT rewrite historical grant provenance.

If `limit` is absent, the default is 100 records.
If it is present, it MUST be in the inclusive range from 1 through 1000.
`list_grants` MUST order matching visible grants by ascending grant-id UTF-8 bytes.
Each cursor is opaque, bound to the authenticated consumer and original query, including its effective filters and limit, and does not grant authority.
Continuation MUST select only grant IDs strictly greater than the last returned ID, using the current grant state and current observation authority.
This is a live query, not a snapshot across pages; grants added at or before that ID need not appear in the continuation.
Capability Authority MUST filter grants to those the authenticated consumer may inspect before applying the limit or creating a cursor.
Each response returns at most the applicable limit and MAY return fewer records to remain within the Core Transport message-size ceiling.
A response MUST contain `next_cursor` only when another matching visible record remains.
A cursor and result count MUST NOT reveal whether additional hidden grants exist.
Capability Authority MAY expire cursors under a documented retention policy.
An expired, unknown, foreign-consumer, or changed-query cursor MUST produce `invalid-request` without revealing another consumer's query or records.

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

Grant status describes the policy record, not whether its target is currently Runtime-known or running.
An `active` grant whose exact target is absent cannot support authority for another instance.
Capability Authority MUST NOT transfer a grant's target or rewrite its scopes because another instance has the same module name, package, contract, or state assignment.
A provider replacement may be covered by an unchanged consumer's existing scopes; a constraint naming the previous provider does not match a different provider address.

The only grant-state transitions are `active` to `expired` and `active` to `revoked`.
The first terminal transition wins.
A revoked grant remains `revoked` after its original expiry time,
and an expired grant cannot subsequently become `revoked`.
Capability Authority MUST treat a grant as expired at the expiry boundary
even if persistence or event-publication work for the transition is still pending.

Revoking or expiring a grant prevents it from supporting new decisions and requires invalidation of dependent cached decisions under Section 8.
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

A deployment replacing the Authority contract MUST define how retained grants, decisions, and audit records bound to the previous contract remain interpretable.
Historical records MUST retain their original contract attribution and MUST NOT be rewritten as if a decision had been made under different scope semantics.
An active grant may be migrated or reissued only through an authorized policy that revalidates its meaning and does not silently widen authority.
Records not representable under the replacement contract MUST remain available through the deployment's documented historical-retention mechanism, subject to their original disclosure rules, for the required retention period.
A query under the replacement contract MUST NOT claim complete historical coverage when retained records require a different contract.
This requirement does not require the replacement provider to expose incompatible contracts through one dispatch surface.

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
    previous_policy_revision: uint64,
    policy_revision: uint64,
    ? affected_executions: [* logos.runtime.module_instance_address],
}
```

`changed_at` is the time at which the new policy becomes active at Capability Authority.
The corresponding `policy-change` audit record MUST use the same timestamp.

Capability Authority applies grant and policy transitions in its own state ordering.
Notification-driven invalidation at Runtime takes effect when Runtime processes the authenticated notification or detects loss of the required notification path.
Runtime MUST order that processing with admission of dependent protected operations and MUST apply invalidation before subsequent admission.
Time-based expiry remains effective at its defined deadline and MUST NOT wait for notification.
A successful grant-administration response acknowledges Authority state mutation and required notification commitment; it does not acknowledge Runtime enforcement or termination of dependent execution.
Before processing a notification, Runtime may continue admitting operations under a decision that otherwise satisfies this section's cache and validity requirements.
Notification commitment does not establish a maximum propagation delay or extend the decision's validity deadline.
Runtime MUST NOT use an allow decision invalidated by an already processed notification to authorize an operation, populate a cache or establish execution authorization.
Response commitment for work already admitted remains subject to the existing in-flight policy.

An Authority binding is Runtime's protected association with a selected local Capability Authority provider realization and its required invocation and notification paths under LOGOS-MODULE-RUNTIME Section 9.
Runtime MUST distinguish each establishment, replacement, or re-establishment after required-path loss by a fresh protected binding generation.
This generation is local enforcement state and is not a serialized contract field.
Loss or replacement of a binding MUST close admission under its generation, invalidate its cached decisions, and end its dependent execution authorizations under this section before replacement authorization can be used.
Runtime MUST associate evaluations and notifications with their delivering generation and MUST NOT let stale results or callbacks affect a replacement binding.
Equal provider addresses or policy revision values MUST NOT establish binding continuity.

Policy revisions are positive, strictly increase on policy changes, and are scoped to the selected Authority binding.
A new binding MAY begin with any positive policy revision; it MUST NOT revive authority from an earlier binding.
A decision's `policy_revision` identifies the policy evaluated.
A policy event identifies the exact transition from `previous_policy_revision` to `policy_revision`.
Grant changes do not advance the policy revision.

When present, `affected_executions` is a complete set of execution targets whose existing authorizations may be affected by that policy transition.
Capability Authority MUST verify against the committed transition that authorizations for every unlisted target remain valid for every consumer and enforcement context, including scope and commitment requirements.
Caller-supplied target information alone MUST NOT establish this guarantee.
If completeness cannot be established, Capability Authority MUST omit the field.
The set MAY be empty and MUST use the deterministic-CBOR ordering and uniqueness rules for set-valued arrays.
The event MUST NOT expose targets the subscriber is not authorized to observe; filtering the set does not preserve its completeness guarantee.

Runtime MAY retain an existing execution authorization across the transition only when the authenticated event belongs to the same Authority binding, its previous revision matches that authorization's current policy revision, and its complete set excludes the exact execution target.
Runtime MUST then advance the retained authorization to the event's policy revision without extending its lifetime or scope.
Each retained authorization MUST account for every intervening policy transition; missing, inconsistent, or unverifiable transition information MUST end the authorization.
A listed target's existing execution authorization MUST end.
A fresh decision evaluated after a transition does not depend on that transition's retention guarantee.
Expiry, a processed notification of supporting-grant revocation or expiry, enforcement loss, and Authority-binding or notification-path loss MUST still end the authorization under the effect points defined above.
A change to an unrelated grant does not by itself end an execution authorization; grant issuance MUST NOT widen or revive one.
Retaining execution does not permit reuse of an invalidated decision for other protected operations.

When an execution authorization ends, Runtime MUST withdraw the dependent execution access and initiate required termination without waiting for re-evaluation or a renewal response.
Retaining an unusable route or session while seeking a fresh decision does not permit continued execution under an ended authorization.
A retryable failure during proactive renewal MAY leave the existing authorization in force only while it independently remains valid under this section.
It MUST NOT extend that authorization, override an explicit denial or invalidation, or create an expiry grace interval.
A denial of continued execution, expired authorization, or loss of a required validity condition MUST stop dependent execution according to Runtime's enforcement and cleanup rules.
Execution intent remains retained, and any later recovery requires fresh authority and completed cleanup under LOGOS-MODULE-RUNTIME.

Runtime may reuse an allow decision only while all of the following remain true:

- `valid_until` is present and the current time is earlier than it;
- no processed notification reports revocation or expiry of a supporting grant;
- the consumer, target, operation, and requested scope still match;
- every enforcement point required by the allowed scopes remains active;
- Runtime has a working grant and policy change notification path to Capability Authority.

If the notification path is lost, Runtime MUST invalidate every cached decision from that Capability Authority.
It MUST NOT perform another protected operation in reliance on an invalidated decision.
Runtime MAY retain allocated routes or sessions while obtaining a fresh decision,
but they MUST remain unusable for protected operations until reauthorized.

Runtime MUST establish or re-establish and confirm the grant and policy change notification path before initiating an evaluation whose result may seed its decision cache or establish execution authorization.
Runtime confirms the path when its `grant_changed` and `policy_changed` subscriptions have both successfully completed activation and remain active under the same current Authority-binding generation, with notification and path-loss processing established for that generation.
Confirmation does not require previously committed notifications or active notification callbacks to finish processing.
The evaluation and use of its result MUST remain associated with that confirmed path and Authority-binding generation.
Later confirmation MUST NOT make an earlier evaluation result eligible for those uses.
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
The `grant_changed` and `policy_changed` events are enforcement notifications for authorized Runtime-owned system-service bindings under LOGOS-MODULE-RUNTIME Section 9.
Ordinary consumer routes MUST NOT authorize subscriptions to these events, including through an unconstrained event scope.
Authority to invoke grant-query or grant-administration methods does not authorize receiving these notifications.
The protected binding MUST authorize the complete information required for its notification coverage.
An event payload, subscription result, or diagnostic MUST NOT disclose information outside that binding's authority.
A Runtime notification path is working for cache reuse only if it remains authorized
to receive every change that can invalidate the cached decision.
Loss of that visibility is notification-path loss and requires full cache invalidation.

After processing a policy-change notification, Runtime MUST re-evaluate dependent operations before admitting another protected operation.
Protected operations include new calls, route creation or renewal,
observations, new event-delivery commitments, lifecycle changes, and enrollment changes.
Existing commitment and connection-failure rules continue to govern events already committed.
It MUST make a dependent route unusable when the new decision denies the route
or narrows its scope below the route's bound scope.

After processing a notification of grant revocation or expiry, or reaching an applicable expiry deadline, Runtime MUST prevent new dependent operations.
It MUST terminate dependent provider sessions and subscriptions when their continued use would exceed current authority.
When a required operating-system permission is revoked,
its enforcement component MUST withdraw the permission or Runtime MUST stop the execution form.
An implementation SHOULD cancel in-flight work when safe and supported.
If cancellation is impossible, it MUST prevent follow-on operations and retain an audit record of the limitation.

Runtime owns enforcement and the mapping of decisions to Runtime, Transport,
Module Loader, and platform error channels.
Capability Authority MUST NOT directly mutate Runtime lifecycle, provider, route, Runtime Control,
or transport-session state.

### 8.1 Ordinary Change Observation

```cddl
logos.capability_authority.watch_changes_request = {
    consumer: logos.runtime.module_instance_address,
}

logos.capability_authority.watch_changes_response =
    {} /
    { error: logos.capability_authority.error }

logos.capability_authority.observed_change_event =
    { grant: logos.capability_authority.grant } /
    {
        changed_at: logos.capability_authority.timestamp,
        previous_policy_revision: uint64,
        policy_revision: uint64,
        ? affected_executions: [* logos.runtime.module_instance_address],
    }
```

`watch_changes` observes subsequent grant and policy changes visible to its authenticated module consumer.
The invocation origin MUST be an authenticated module consumer; an engine system-service invocation MUST NOT be admitted to this method.
Runtime MUST validate `consumer` against protected invocation context before dispatch.
The method requires its own provider-access authority; the consumer also requires authority to subscribe to `observed_change`.
Neither permission grants visibility of every grant or policy-change record.
Capability Authority MUST publish `observed_change` only through the watch invocation's protected destination.
It MUST NOT publish this event through the ordinary broadcast operation or use the enforcement event declarations for ordinary observation.

A watch remains an outstanding ordinary method invocation while observation continues.
Its final Response ends the watch; an empty success response is not a registration acknowledgement.
Cancellation, completion or loss of the destination ends publication eligibility under LOGOS-MODULE-RUNTIME Section 7.3.1.
The provider MUST retire observation work when it observes cancellation or destination loss and discharge its invocation ownership under LOGOS-MODULE-INTERFACE.
Ending a watch MUST NOT revoke grants or cancel unrelated work.
The mandatory synchronous provider surfaces remain functional; this method does not require an asynchronous-only provider class.

Consumers activate the event subscription before starting the watch on the same invocation path.
Submitting the call does not establish that provider-side observation has begun.
This contract provides live change notifications without an initial snapshot, replay, readiness acknowledgement or race-free state-reconstruction guarantee.
Consumers use authorized queries to obtain current state.
Equivalent concurrent watches MAY produce duplicate notifications to matching subscriptions on the same invocation path.
The event does not identify a particular watch, and consumers MUST NOT infer registration readiness or per-watch correlation from it.
Each watch retains independent cancellation and resource accounting.

For each ordinary notification, Capability Authority MUST atomically check the consumer's current payload visibility and admit one immutable recipient-specific publication in its own state-transition ordering.
The check MUST account for permission expiry at that admission time.
A copied identity, watch-admission decision or earlier queued change MUST NOT substitute for this check.
Capability Authority MUST release synchronization needed by reentrant calls before invoking scoped publication.
Loss of payload-inspection permission after admission does not retract that publication; the admitted payload may be delivered after that permission expires.
Runtime MUST still check destination and event authority at each delivery commitment under LOGOS-MODULE-RUNTIME Section 7.3.1.
Payload admission is not proof of delivery and does not extend the invocation's publication lifetime.

A grant notification MUST disclose the complete semantic grant fields only when the consumer may inspect them under Section 10 at publication admission.
A hidden grant MUST produce no ordinary notification, placeholder or identifier at publication admission.
At publication admission, policy-change notifications require authority to inspect the included policy-change information.
The `affected_executions` completeness guarantee from Section 8 also applies to ordinary notifications.
If the consumer cannot inspect the complete set at publication admission, Capability Authority MUST omit the field; it MUST NOT disclose a filtered set as complete.

Capability Authority MUST bound retained watches, queued observation work and in-flight publications.

The provider MUST arrange cancellation observation independently of further state changes or publication attempts.
Ordinary observation MUST NOT block or consume capacity reserved for required engine evaluation, renewal or enforcement-notification progress.
An implementation unable to continue a watch within its limits MUST end the affected watch through an ordinary completion or invocation failure, retaining already committed Event obligations.
Direct publication MUST retain the synchronous callback rules; observation scheduling and resource isolation remain implementation-owned.
The ordinary observation stream MUST NOT replace the complete, confirmed notification path required for Runtime decision-cache reuse.
Its disclosure-admission rule does not alter enforcement-binding validity, ordered state transitions or notification-path-loss handling.

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
        ? scopes: [* logos.capability_authority.scope],
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
The records MUST be ordered by descending `timestamp`, with equal timestamps ordered in reverse recording order.
`since` is inclusive and `until` is exclusive.
Equal bounds select no records; if `since` exceeds `until`, Capability Authority MUST return `invalid-request`.
This bounded query does not provide pagination or guarantee a complete audit export.

`consumer` in `query_audit_request` is the authenticated invoker.
`record_consumer` and `target` are optional record filters; they do not supply query authority.
In an audit record, `consumer` identifies whose authority was used for the recorded operation.
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
Rejection before evaluation begins, including rejection by a deadline, size limit, or queue limit, is an admission failure and does not require an audit record.
Once evaluation begins, every result or failure remains subject to the audit requirement.

When an applied allow decision requires request or response retention for a call,
the Runtime-controlled invocation boundary MUST produce a `call` audit record
after the corresponding enforcement outcome.
The record MUST contain the `decision_id` of the allow decision actually applied to authorize the call and the exact enforced call scope.
At successful call admission, Runtime MUST capture that decision, the enforced scope, and its applicable retention requirements as one consistent snapshot and retain them through the enforcement outcome.
The enforced scope MUST be covered by that decision's allowed scopes and include every applicable narrowing constraint.
A still-valid cached call decision MAY be used; a decision authorizing only route establishment or renewal does not authorize a call.
Subsequent renewal or revocation MUST NOT replace the captured decision or scope in the call record.
This recording rule does not defer required revocation enforcement.
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

Every conforming Runtime MUST implement `logos.call-evidence.cose-sign1-slh-dsa-sha2-192s` for call evidence.
Local audit retention does not require a signed container,
and an implementation need not export call evidence unless selected audit policy requires it.
The profile binds one complete `call` audit record to zero or more retained verified-view proofs.
It does not define another audit record, query method, evidence identity, or batch format.

The signed payload is this Logos deterministic-CBOR claim:

```cddl
logos.capability_authority.call_evidence_profile =
    "logos.call-evidence.cose-sign1-slh-dsa-sha2-192s"

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

The container MUST be one tagged `COSE_Sign1` object using CBOR tag 18 from RFC 9052 with the fixed implicit algorithm `SLH-DSA-SHA2-192s` from FIPS 205.
This profile uses the application-context mechanism in RFC 9052 Appendix A and assigns no COSE algorithm identifier.
The protected header map MUST contain exactly `kid`, with COSE label `4` and a `logos.capability_authority.evidence_key_id` value.
An explicit `alg` header MUST be rejected, including one that identifies the algorithm fixed by this profile.
The unprotected header map MUST be empty.
The outer object and serialized protected header map MUST use the core deterministic encoding requirements
of RFC 8949 Section 4.2.1.

The payload MUST be embedded as a byte string containing the exact deterministic-CBOR claim.
Detached payloads, additional protected or unprotected headers,
multiple signatures, countersignatures, and critical-header extensions are not accepted.
The `Sig_structure` is the deterministic-CBOR encoding of the RFC 9052 `Signature1` structure, using the protected header bytes from the object and the exact embedded payload bytes.
Its `external_aad` MUST be the UTF-8 bytes of `logos.call-evidence.cose-sign1-slh-dsa-sha2-192s`, without a terminator.
The verifier MUST derive this value and the fixed algorithm from its protected evidence-verification context before signature verification, not from the received claim or headers.
The context MUST bind the expected profile, algorithm, `COSE_Sign1` structure, call-evidence purpose, accepted `kid`, exact public key, and authorized producer Runtime identity.
The profile identifier inside the signed payload MUST equal the expected profile after verification.
This profile defines no nonce or algorithm negotiation.
A verifier MUST NOT retry with another algorithm, context, or profile after verification fails.

Protected trust input MUST map each accepted `kid` to exactly one producer Runtime identity and one exact 48-byte `SLH-DSA-SHA2-192s` public key.
The public-key encoding is the FIPS 205 concatenation `PK.seed || PK.root`, with 24 bytes in each component.
It MUST authorize that key specifically for call-evidence signing.
The same key material MUST NOT be used for package signing, provenance signing, TLS authentication, or another signature algorithm.
Two accepted evidence keys MUST NOT use the same `kid`.
The `kid` selects candidate verification material and does not establish trust by itself.

Evidence-signing keys MUST be generated using FIPS 205 key generation and its randomness requirements.
The Runtime host or its protected signing integration MUST keep the evidence-signing private key secret and protect it against unauthorized signing.
Signatures MUST use pure `SLH-DSA-SHA2-192s` with the zero-length FIPS 205 context.
The message supplied to FIPS 205 `slh_sign` or `slh_verify` is the exact encoded `Sig_structure`.
The FIPS 205 pure-mode prefix is applied by those operations and MUST NOT be added again to their message input.
HashSLH-DSA, an additional prehash, another parameter set, and a nonempty context MUST NOT be used.
Signers SHOULD use FIPS 205 hedged signing with fresh randomness and MUST fail signing if required randomness cannot be obtained.
Verifiers MUST accept both deterministic and hedged signatures that satisfy the same FIPS 205 verification procedure.
A signature is exactly 16,224 bytes.
The verifier MUST apply FIPS 205 `slh_verify` and accept only its successful result; it MUST NOT truncate, pad, normalize, or otherwise repair a key or signature.
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
Empty side arrays MUST be omitted, and `proofs` MUST be omitted when neither side has a proof.
Each proof byte string MUST contain exactly one Logos deterministic-CBOR `verified-view` defined by LOGOS-MODULE-HASH-PROFILE.
Within each side, proofs MUST be ordered by strictly ascending bytewise lexicographic order of the complete Logos deterministic-CBOR encoding of their decoded semantic path, the verified-view field `7`.
A side MUST NOT contain two proofs for the same semantic path, even if their proof representations differ.
The same semantic path MAY occur once on each side.
The verifier MUST reject duplicate paths or nonascending order and MUST NOT sort or deduplicate a received claim.
This rule orders the selected proofs; it does not require every valid disclosure of a call to contain the same proofs.
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
an unknown or duplicate `kid`, an unaccepted header or protected verification context,
an invalid key or signature length, a failed signature,
an incorrect profile identifier, an unauthorized producer,
or any record or proof mismatch described above.
The container authenticates the retained evidence as a statement by the authorized producer.
It does not grant authority, prove package or provider trust, or establish freshness.

This baseline provides authenticity and integrity, not confidentiality.
Evidence export uses a protected deployment-defined integration whose selection, authorization, limits, and delivery policy MUST be documented.
Before disclosing a container, the producer MUST authorize disclosure of its complete record under the audit authorization and visibility rules and separately authorize every included proof.
Permission to inspect a commitment does not grant permission to inspect its proof contents.
If the complete record cannot be disclosed, export MUST be denied.
The producer MAY create a new valid container containing that complete record and only the authorized optional proofs; it MUST NOT redact an already signed claim in place.
`query_audit` returns audit records, not signed evidence containers.
Sensitive evidence requires confidentiality-protected transport and storage.
This specification does not define a second encrypted evidence format.

Capability Authority need not participate in ordinary module data flow.
Runtime may retain call records and proofs directly or deliver them through a protected audit integration.
When a Capability Authority implementation stores those records,
`query_audit` returns them under the same authorization, visibility, ordering,
and result-bound rules as its other records.

Audit queries MUST require explicit authorization and MUST disclose only information the authenticated consumer is allowed to observe.
Every returned audit record MUST satisfy its CDDL variant and semantic requirements, including required attribution, exact recorded scopes and applicable commitments.
Optional fields MAY be omitted only when those requirements permit omission.
If authorized disclosure cannot produce such a record, Capability Authority MUST omit the whole record.
Audit records MUST NOT contain full route tickets, bearer credentials, private keys, or secrets.
Sensitive constraint values require protection and explicit audit authorization before retention.
Protected deployment or audit-profile policy supplies that authorization; permission to invoke `evaluate` does not by itself authorize retention.
If an admitted evaluation cannot produce its required allow or deny audit record without retaining unauthorized sensitive constraint values, Capability Authority MUST fail the evaluation without issuing an allow or deny decision.
The failure record MUST omit those values and preserve its otherwise required attribution.
The existing evaluation-error and diagnostic-disclosure rules apply.
If a grant-issuance request cannot produce its required success or denial audit record without violating these retention restrictions, Capability Authority MUST fail the request with `authority-unavailable` without issuing a grant or grant denial.
The required `issue-grant` failure record MUST preserve every other required field.
When the complete requested scopes were successfully decoded and validated and their retention is permitted, an `issue-grant` failure record MUST contain them.
Otherwise, it MUST omit `scopes` in its entirety.
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
- `query_audit`;
- `watch_changes`.

The contract defines these events:

- `grant_changed`;
- `policy_changed`;
- `observed_change`.

`evaluate` is the Runtime-facing policy-decision method.
Runtime MUST be authorized to invoke it through the protected system-service binding defined by LOGOS-MODULE-RUNTIME Section 9.
Ordinary consumers MUST NOT gain direct authority to call `evaluate`
merely because they can request a provider route or invoke another Capability Authority method.

`grant_changed` and `policy_changed` are restricted to the protected engine notification path in Section 8.
Ordinary consumers observe changes through `watch_changes` and `observed_change` under Section 8.1.

The grant and audit methods require their own provider-access authorization.
A consumer authorized to inspect grants whose target equals that consumer does not thereby gain authority to inspect or modify grants targeting another module instance.
Authority to invoke `get_grant` or `list_grants` does not by itself authorize every matching record.
Capability Authority MUST apply target and scope visibility before returning a grant.
The issuer, target, scopes, time bounds, status, commitment requirements, and revocation time are semantic grant fields.
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

For an ordinary module-provider route, a protected transport profile MUST bind its route ticket or session credential to the consumer or authenticated session,
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

Runtime-owned local system-service credentials instead follow LOGOS-MODULE-TRANSPORT Section 8.1.2.
Their authority comes from the protected binding policy, without creating a module consumer or substituting for any execution or permission authorization.

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
| Commitment retention | Capability Authority or internal Runtime policy | Runtime-controlled invocation boundary |

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

- [RFC 2119] -- Key words for use in RFCs to Indicate Requirement Levels.
  https://www.rfc-editor.org/rfc/rfc2119
- [RFC 8174] -- Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
  https://www.rfc-editor.org/rfc/rfc8174
- [FIPS 205] -- Stateless Hash-Based Digital Signature Standard.
  https://csrc.nist.gov/pubs/fips/205/final
- [RFC 8949] -- Concise Binary Object Representation (CBOR).
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 9052] -- CBOR Object Signing and Encryption (COSE): Structures and Process.
  https://www.rfc-editor.org/rfc/rfc9052
- LOGOS-MODULE-INTERFACE -- Shared values, native invocation, deterministic encoding and contract-outcome rules.
- LOGOS-MODULE-RUNTIME -- Consumer identities, protected service bindings, routes and enforcement semantics.
- LOGOS-MODULE-TRANSPORT -- Protected invocation paths and route-authorization profiles.
- LOGOS-MODULE-HASH-PROFILE -- Verified views and proof validation.

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
