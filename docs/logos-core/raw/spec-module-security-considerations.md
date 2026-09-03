# LOGOS-MODULE-SECURITY-CONSIDERATIONS

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Security Considerations                          |
| Slug         | 314                                                           |
| Status       | raw                                                           |
| Category     | Informational                                                 |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This document consolidates the security model for the Logos module system.
It explains the system's trust boundaries, protected assets, attacker capabilities, platform assumptions, and residual risks.
It also maps security responsibilities to the normative Core specifications that define them.

This document is informational.
It does not create a second authorization model, package-trust model, transport profile, or execution profile.
Normative behavior remains in the specification that owns the relevant interface or enforcement boundary.

## 1. Scope

The Logos module system can load native executable code, realize providers across process and network boundaries, route typed calls and events, and expose privileged system services.
These capabilities make package acceptance, authority enforcement, isolation, transport authentication, and evidence handling part of one security model.

This document covers the following areas:

- the actors and assets protected by the Core module system;
- attacks by malicious packages, modules, consumers, publishers, remote peers, and network participants;
- package-signature, executable-acceptance, route-authorization, commitment, audit, and call-evidence boundaries;
- native desktop execution and its difference from browser-provided containment;
- process placement and platform-specific sandboxing;
- security differences across desktop and mobile platforms;
- residual risks that remain after conformance to the Core specifications.

This document does not define a new wire format, policy language, sandbox API, proof system, consensus system, or trusted-computation protocol.
It does not claim that a valid signature, schema, commitment, authority decision, or transport session proves that module behavior is safe.

### 1.1 Normative Ownership

This document summarizes requirements from the following normative owners:

| Security responsibility | Normative owner |
|---|---|
| Module contracts, typed values, method and event shapes, and ABI behavior | LOGOS-MODULE-INTERFACE |
| Canonical schema and value commitments and verified-view proofs | LOGOS-MODULE-COMMITMENT-MODEL |
| Hash profiles, hash suites, and commitment domain separation | LOGOS-MODULE-HASH-PROFILE |
| Executable acceptance, provider lifecycle, routing, Runtime Control, and enforcement at Runtime boundaries | LOGOS-MODULE-RUNTIME |
| Message validation, payload commitments on transported values, route-ticket redemption, and authenticated remote transport profiles | LOGOS-MODULE-TRANSPORT |
| Consumer authority, provider and method scope, decisions, grants, revocation, audit records, commitment retention, and call evidence | LOGOS-MODULE-CAPABILITY-AUTHORITY |
| Per-instance configuration-schema binding, authorized observation and mutation, retained configuration state, startup delivery, and live application | LOGOS-MODULE-CONFIGURATION |
| Package signatures, trust inputs, manifest validation, artifact verification, and package-to-Runtime handoff | LOGOS-MODULE-PACKAGE-MANAGER |
| Native binding, dynamic loading, symbol resolution, Module Host realization, endpoint handoff, realization status and release, and enforcement of assigned isolation and resource controls | LOGOS-MODULE-LOADER |

Concrete operating-system sandbox mechanisms, protected local provisioning, and deployment choices remain the responsibility of a selected platform or deployment profile where the normative Core specifications assign them there.
If this document conflicts with a normative owner, the normative owner controls.

## 2. Threat Model And Native Runtime Assumptions

The initial Logos runtime is a native desktop program, not code confined by a browser sandbox.
Native execution enables dynamic loading, process creation, local IPC, native networking, filesystem access, platform sandbox controls, package installation, desktop UI integration, and conventional system debugging.
It also means that Logos must establish its own authority and containment boundaries.

### 2.1 Protected Assets

The security model seeks to protect:

- Runtime and system-service control from unauthorized use;
- package-signing keys, trust anchors, enrollment state, authority policy, and other protected inputs;
- the integrity of accepted package manifests and executable artifacts;
- consumer identity and the provider, contract, method, and event scope granted to each route;
- module, Runtime, and user data from unauthorized reading, modification, or disclosure;
- route tickets, private keys, credentials, and other secret authorization material;
- the integrity and authorized disclosure of audit records and call evidence;
- availability within the resource limits that the selected deployment can enforce.

### 2.2 Trusted And Untrusted Actors

The local operator or deployment owner is trusted to provision policy, trust inputs, Runtime enrollment, and platform profiles correctly.
The host operating system and the isolation mechanisms selected by the deployment are trusted to enforce the boundaries attributed to them.
Compromise of the host kernel, firmware, local administrator account, or protected provisioning channel is outside the threat model of this specification.

A Runtime, Package Manager, Capability Authority, or Module Loader is trusted only for the responsibilities assigned to that concrete provider by deployment policy.
Exposing a module contract does not establish that trust.
A publisher signature identifies an accepted signing key and protects the signed package binding; it does not establish that the publisher or code is benign.

Unless deployment policy establishes greater trust, the model treats modules, packages, consumers, remote Runtimes, catalogs, package sources, and network participants as potentially malicious or compromised.
An authenticated peer may still request unauthorized operations, misidentify its own consumers, send invalid values, exploit implementation defects, or return incorrect results.

### 2.3 Attacks In Scope

The model addresses package substitution and tampering, unauthorized executable loading, confused authority between consumers, route-ticket theft or replay, remote-peer impersonation, schema and method confusion, malformed encodings, payload-commitment mismatch, unauthorized method or event use, credential disclosure, audit leakage, unsafe downgrade, and time-of-check/time-of-use races.
It also considers malicious or vulnerable native code, insufficient process or sandbox isolation, overly broad policy, resource exhaustion, and abuse of legitimately authorized dangerous operations.

Cryptographic verification, authorization, and isolation reduce different risks and do not substitute for one another.
A conforming system can still execute malicious trusted code, authorize a dangerous action, expose data through an allowed interface, suffer a sandbox or implementation vulnerability, or produce an incorrect result behind a valid contract.

## 3. Independent Trust Decisions

The Core architecture does not assign one universal trust level to a module.
Instead, it keeps the following decisions distinct:

- whether a signing key is accepted for package signing;
- whether a package signature and manifest commitment are valid;
- whether materialized artifact bytes match the hashes authenticated by that manifest;
- whether a consumer may install, execute, stop, or remove the package or module;
- whether requested operating-system permissions may be granted and enforced;
- whether a consumer may reach a provider and use particular methods or events;
- whether code is trusted enough to share an address space with its host;
- whether a remote Runtime is enrolled, authenticated, and authorized for a requested operation;
- whether an evidence-signing key is accepted for a particular producer Runtime.

These are decisions within the existing Package Manager, Capability Authority, Runtime, Transport, Module Loader, and deployment boundaries.
They are not module classes and do not require one policy mechanism per list item.
A deployment can derive several decisions from the same protected configuration, but success at one boundary does not grant authority or establish trust at another.

### 3.1 Package And Executable Acceptance

Obtaining candidate package material is not package acceptance.
The LGX profile obtains prebuilt archive data without evaluating package-controlled build definitions.
The Nix profile may need to evaluate package-controlled input or execute builders
before the embedded manifest and package signature are available.
LOGOS-MODULE-PACKAGE-MANAGER therefore permits such work only inside its pre-verification isolation boundary,
unless protected deployment input supplies the exact immutable realized output without package-controlled evaluation or building.

After candidate material is obtained under the owning realization-profile rules,
for a dynamically loaded artifact obtained from a package,
the baseline package-authentication chain is:

1. protected package-signing trust input identifies an accepted Ed25519 public key;
2. Package Manager verifies `manifest.cose` and its signed manifest commitment;
3. Package Manager verifies the selected materialized artifact bytes against the artifact hash authenticated by the manifest;
4. Runtime receives the accepted digest through an authenticated Package Manager handoff, obtains execution authorization, and constructs the Module Loader realization descriptor from that accepted evidence; and
5. Module Loader verifies the exact artifact bytes without a path-replacement gap before it causes those bytes to be mapped or executed.

Catalog records, archive names, paths, package metadata, module names, and downloaded keys do not replace any step in this chain.
The baseline does not require a separate artifact signature because the signed manifest already authenticates the artifact hash.
Pre-verification isolation does not authenticate a Nix output or establish package trust.
It prevents unaccepted package-controlled work from inheriting Package Manager authority while the baseline checks remain pending.

Protected bootstrap input may instead supply an accepted digest for a dynamic artifact without claiming package acceptance.
Runtime still completes execution authorization,
and Module Loader still performs load-boundary digest verification.

Direct static binding has a different executable-acceptance boundary.
The code is already linked and identified by a protected deployment registration before a module instance is realized.
Runtime completes execution authorization before invoking `realize`,
and Module Loader validates the registered ABI binding before initialization.
The `direct_static` realization descriptor carries no artifact digest,
and Module Loader performs no load-time mapping for that strategy.

After dynamic artifact acceptance and execution authorization succeed,
Runtime can direct the bound Module Loader to realize the accepted implementation.
For direct or hosted dynamic loading,
Module Loader ensures that the applicable ABI caller invokes the platform loader and resolves the mandatory ABI symbols before initialization.
The applicable ABI caller may retain the resolved addresses for that implementation binding.
Runtime validates the returned realization and expected contract views before it marks the module instance ready.
Cryptographic verification is not repeated for every symbol lookup or method call.
Successful digest verification may also be cached for immutable content-addressed artifacts under the invalidation rules in LOGOS-MODULE-RUNTIME.

Loading a candidate library is not passive inspection because the platform loader may execute artifact-controlled initialization before the applicable ABI caller invokes a Logos symbol.
Unknown-artifact discovery must therefore remain limited to non-executable package, catalog, manifest, or deployment data.
A tool that must inspect unknown executable code requires a separately defined isolated analysis profile; it is not a second normal module-loading path.

### 3.2 Structural Validation Is Not Trust

A valid schema establishes the shape and identity of a contract.
A matching module-name function and complete symbol set establish that the mapped artifact exposes the expected ABI entry points.
A valid payload commitment establishes that a typed value matches the committed schema subtree and value root.
None of these checks proves that the code is benign, that its result is correct, or that the caller is authorized.

Likewise, package and artifact identifiers are policy inputs rather than integrity proofs.
Requested permissions are declarations rather than grants.
Module contracts identify interfaces; they do not make a provider trusted or authorize an invocation.

### 3.3 Configuration And Retained State

A configuration value is accepted state for one module instance.
It can contain sensitive operational data even though LOGOS-MODULE-CONFIGURATION forbids credentials, protected trust input, requested permissions, authority grants, and live authority state.

Runtime authorizes every configuration observation and mutation for the exact module instance.
The configuration-schema and value commitments give independently reproducible identities for the accepted schema and value.
They do not provide confidentiality or grant authority.
LOGOS-MODULE-CONFIGURATION requires startup delivery through the structured initialization input or a protected executable-startup handoff rather than an implementation-specific configuration-file path.

The concrete storage and realization mechanisms are responsible for protecting retained current and staged configuration values against unauthorized observation or replacement.
Persistent module state has the same separation between Runtime-owned assignment and deployment-owned storage protection.
A configuration source, storage path, or state-assignment identifier does not grant authority to read, modify, share, retain, or delete the underlying data.

## 4. Execution Placement And Isolation

In-process code normally shares the host's memory, credentials, and ambient process authority.
The Core model therefore requires such code to be trusted for that deployment or confined by a separately defined in-process containment mechanism.
Route checks and Capability Authority decisions cannot contain malicious code that already shares the enforcing Runtime's address space.

A separate process creates a boundary at which the operating system can enforce filesystem, network, IPC, process, device, memory, CPU, and other resource constraints.
Process separation alone does not provide those constraints.
The hosted `process` placement is not equivalent to a sandbox,
and a transport boundary does not prove containment strength.

The Module Loader hosted placements `process`, `sandbox`, and `container` describe execution envelopes.
Deployment configuration and the selected platform profile map those classes to concrete mechanisms and enforceable constraints.
If required isolation or resource controls cannot be established, the realization fails rather than silently degrading to a weaker realization.
The public realization record contains none of the host process identifiers,
paths, isolation references, or container references that a deployment may retain internally.

Remote placement changes the administrative and transport boundaries but does not make the provider safer.
The local Runtime still relies on the authenticated remote Runtime to enforce the authorized provider route, while the remote deployment remains responsible for containing its local provider code.

## 5. Isolation Goals And Platform Profiles

These specifications identify where constraints must be selected and enforced, but they do not define one sandbox implementation usable across all operating systems.
A platform or deployment profile that permits untrusted native code should define enforceable constraints for:

- filesystem and persistent-state access;
- outbound and listening network access;
- process creation, signaling, and executable loading;
- IPC, device, credential, secret, clipboard, notification, and UI access;
- CPU, memory, process-count, file-descriptor, and storage-growth limits;
- access to Runtime, Package Manager, Capability Authority, Module Loader, and other privileged services;
- behavior when a required control is unavailable or is revoked.

The profile must identify the component that enforces each constraint.
Capability Authority can decide whether the constraint is allowed, but it cannot make an unavailable operating-system control enforceable.
Runtime is suited to lifecycle, routing, provider visibility, call, event, subscription, and Runtime-owned accounting constraints.
Transport is suited to connection, framing, replay, and pressure constraints.
Module Loader, deployment controls, and operating-system mechanisms enforce constraints on selected execution forms.

Conforming implementations MUST fail closed when they cannot realize the selected profile; these specifications do not require identical sandbox strength across platforms.
A deployment that cannot satisfy the selected profile must reject the dependent operation or explicitly select a different profile through trusted configuration.

## 6. Authority And Remote Runtime Access

Authentication establishes identity at the applicable invocation or transport boundary; it does not authorize an operation.
Runtime represents an authenticated consumer with `module_instance_address` and evaluates the requested operation against the provider, contract, method or event scope, lifecycle operation, permission constraints, and other applicable authority inputs.
A separately named target does not supply the authority used to invoke the operation and does not become the consumer.

Runtime Control is a privileged system-service surface.
Ordinary module status, a valid Runtime Control schema, or access to another system service does not grant Runtime Control authority.
Remote Runtime Control and ordinary remote provider traffic require independent enablement and authorization even when they share a physical address.

The Core model uses Capability Authority decisions and grants as policy results, not as bearer credentials.
Decision and grant identifiers are correlation values.
These specifications define no generic capability token, signed authority decision, or COSE authorization token.

### 6.1 Remote Runtime Authentication And Enrollment

The mandatory production remote profile is mutually authenticated TLS 1.3 over TCP under `logos.remote.tls-tcp`.
The optional `logos.remote.quic` profile provides equivalent Runtime authentication and authorization semantics over QUIC.
Neither production profile carries Logos application data in TLS or QUIC 0-RTT,
and neither permits fallback to an unauthenticated carrier.

The target Runtime binds the authenticated source Runtime identity to protected enrollment state.
Enrollment permits that Runtime boundary to be used for configured remote operations; it does not authorize a Runtime Control method, provider route, lifecycle operation, or provider visibility by itself.
The target Runtime independently authorizes each requested operation for the identified consumer.

When a source Runtime requests a route for one of its consumers, the target Runtime relies on the authenticated and authorized source Runtime to identify that consumer correctly.
This revision does not require a separate remote credential for every module.
That limitation makes compromise or malicious behavior of an enrolled source Runtime a residual risk for identities in its own consumer namespace.

### 6.2 Route Establishment And Session Credentials

After an allow decision fixes the consumer or authenticated session, provider, selected contract, method and event scope, endpoint, Runtime route, authority decision, freshness, and revocation constraints, the target Runtime issues the route credential.
Capability Authority does not issue the credential and does not proxy ordinary module traffic.

The mandatory remote profiles use `logos.route-ticket.random-256`.
The ticket is 32 uniformly random bytes, is valid for at most 60 seconds on the issuer's monotonic clock, is bound to the authenticated peer and complete route constraints, and can establish exactly one provider session.
The target Runtime uses only the ticket's BLAKE3-256 digest as the lookup key in its ticket state
and atomically consumes the record before creating a usable session.

Possession without the bound peer authentication is insufficient.
A missing, invalid, expired, revoked, replayed, or incorrectly bound ticket creates no usable session and dispatches no ordinary module message.
After redemption, the authenticated channel and consumed record bind the session; the raw ticket has no further protocol role.

The provider-side Runtime enforces the selected contract and allowed method and event scope for the session.
It resolves each bare method name only within the selected contract and rejects an out-of-scope method before calling provider code.
Expiration or revocation terminates affected subscriptions and prevents new operations.

Route tickets, private keys, proof-of-possession secrets, and reusable credentials are not audit or diagnostic data.
They must not appear in decision, grant, route-observation, package, Module Loader realization, lifecycle, audit, or error records.

## 7. Dangerous Operations And Authority Propagation

Schema-valid operations can still be dangerous.
Relevant permissions include process execution, executable loading, unrestricted filesystem or persistent-state modification, arbitrary network access, credential or secret access, package installation, Runtime Control, device access, and privileged UI integration.

Package manifests declare requested permissions but do not grant them.
The selected permission or platform profile defines the constraint shape and enforcement component.
Runtime rejects an operation when no active enforcement point can satisfy an allowed constraint.

An authorized component must not substitute its own broader authority for that of an untrusted caller.
Runtime therefore evaluates every operation under the authenticated consumer's authority.
A separately named target does not change the consumer or contribute authority.
A module's Runtime Control binding identifies that module instance's own `module_instance_address` as consumer for every outbound route acquisition.
That acquisition does not reuse a route ticket or authority decision from any inbound call that triggered it.
Each outbound provider route and method call receives its own authorization under the calling consumer's authority.

These rules prevent a less-authorized caller from obtaining a privileged effect merely by sending a valid request through a more-authorized Runtime or module component.
They do not determine whether an authorized operation is wise, safe for the user's data, or semantically correct.

## 8. Schemas, Dispatch, And Payload Commitments

Schema parsing establishes value shape and contract identity, not authority.
Runtime authorizes a route against one selected contract and its method and event declaration roots.
Selected-contract introspection exposes only the selected contract's required construction input.
Returning a required interface document does not select that interface contract or authorize its methods or events.
It does not expose an unrelated backing-provider contract, route, or registry state.

Every Transport Request, successful Response, and Event carries a compact payload commitment containing the applicable schema subtree root and value root.
The sender computes the commitment from the schema-typed value.
Before dispatch, acceptance, or delivery,
the schema-aware receiving boundary validates the value and independently
recomputes both roots under the fixed commitment-model revision,
hash profile, and BLAKE3-256 hash suite.
Commitment failure is fail-closed.
`response-err` and ProtocolError messages do not carry payload commitments.

Direct per-method calls and generic dispatch through `logos_<module>_dispatch()` compute the same commitments internally without changing the provider ABI.
Event commitments are computed for the selected contract on each subscriber route.
Commitment computation is mandatory independently of audit-retention policy.

A compact commitment authenticates neither endpoint and grants no authority.
It proves neither that native code avoided side effects nor that a returned result is semantically correct.
It gives independently reproducible identities for the exact schema-typed values that crossed a controlled boundary.

Full verified-view proofs are used only for an intentional partial disclosure declared by the applicable method or event schema.
Sending the complete value does not require a redundant full proof path.

## 9. Audit, Call Evidence, And Trust Binding

Capability Authority owns the call audit record and the authority checks on audit queries.
Runtime retains request or response roots only when the applicable authority decision selects `retain-root` for that side of the call.
Commitment computation itself does not depend on that selection.

An ordinary audit query returns at most the most recent 1000 matching records.
Operators can review older records through deployment-specific log storage when the deployment retains them.
An attacker may deliberately generate enough newer activity to push relevant records outside this bounded interface, so security-sensitive deployments need external retention and monitoring appropriate to their threat model.

The mandatory call-evidence profile `logos.call-evidence.cose-sign1-ed25519` signs one complete call audit record and may include verified-view proofs for an intentionally disclosed request or response view.
The signing key has a distinct evidence-signing purpose and is bound through protected trust input to the producer Runtime identity.
Call evidence provides authenticity and integrity, not confidentiality, correctness, execution attestation, or authorization.
Its disclosure and storage still require confidentiality protection and audit authority.

Package authentication uses a separate signing purpose and container.
The package signature binds the manifest commitment, which binds package identity, provided contracts, artifact records and hashes, requested permissions, schema roots, the manifest value root, commitment-model revision, hash profile, and hash suite.
Package Manager verifies the exact artifact bytes, and Module Loader verifies them again at the realization boundary.

Trust comes from protected input that accepts a signing key, Runtime identity, enrollment, digest pin, or other profile-defined anchor for a particular purpose.
A root, key identifier, Runtime identifier, catalog entry, downloaded key, or network address does not establish trust by itself.
Package-signing trust, evidence-signing trust, remote Runtime enrollment, execution authorization, and provider-route authorization remain distinct even if a deployment derives them from related configuration.

## 10. Residual Risks And Accepted Limitations

Conformance reduces ambiguity, unauthorized access, substitution, replay, and downgrade risk, but it does not eliminate the following risks:

- **Authorized dangerous action:** policy can intentionally allow a destructive method or an overly broad filesystem, process, or network permission.
- **Malicious accepted publisher or artifact:** a valid signature authenticates accepted package provenance and bytes, not benign behavior.
- **Vulnerable trusted code:** memory-safety and logic defects can be exploited through schema-valid inputs.
- **Compromised enforcement component:** compromise of Runtime or of a bound Capability Authority, Package Manager, or Module Loader provider can defeat the security responsibilities assigned to that component.
- **Insufficient or vulnerable containment:** process placement, sandbox labels, and containers do not prevent escape or data access unless the selected platform controls actually enforce the required constraints.
- **Compromised enrolled Runtime:** an authenticated source Runtime can misuse its granted operations or misrepresent consumers within the namespace the target trusts it to administer.
- **Credential theft:** valid stolen credentials can satisfy authentication until revocation or another control detects the compromise.
- **In-process compromise:** code sharing the Runtime address space can corrupt memory, steal secrets, call host functions, or bypass route enforcement.
- **Time-of-check/time-of-use mismatch:** mutable paths, replaced files, symlinks, or external resources can differ between verification and use unless the deployment preserves the exact-byte and resource bindings.
- **Audit-window exhaustion:** malicious activity can move an older record outside the bounded audit-query result even when deployment storage retains it.
- **Resource exhaustion:** frame-size and event-buffering limits do not by themselves bound connection, call, route, ticket, subscription, or queued-response state.
- **Pre-verification realization compromise:** Package-controlled Nix evaluation or building can exploit defects in the selected isolation mechanism or consume resources permitted within that boundary before the package signature is available.
- **Configuration or state disclosure:** authorization protects the Logos operations that expose configuration and persistent-state assignments, but confidentiality and integrity also depend on the selected storage, handoff, isolation, and operating-system controls.
- **Incorrect computation:** schema and value roots identify what was supplied and returned; they do not prove that the result is correct.

Reproducible builds, transparency systems, remote attestation, deterministic recomputation, fraud proofs, validity proofs, stronger hardware roots, and platform review can address parts of these risks.
They are optional external mechanisms unless a selected profile defines and enforces them.

## 11. Platform Security Models

The Core module contract is platform-independent, but executable realization, installation, isolation, user consent, storage, IPC, updates, and background work are not.
A platform profile must describe how the Core enforcement responsibilities map to facilities that exist on that platform.

### 11.1 Linux Desktop

- **Execution and isolation:** Native dynamic loading and separate processes are broadly available.
  Ordinary desktop processes are not automatically sandboxed.
  A deployment can combine user and mount namespaces, restricted filesystem views, seccomp filters, Linux security modules, and cgroup v2 resource controls, but availability and permitted unprivileged use vary by kernel and distribution configuration.
- **Installation, signing, and updates:** Linux has no single desktop-wide application-signing, installation, or update authority.
  A distribution package manager, container or sandbox system, application bundle, or private deployment may add those controls.
  The Logos package signature and protected Logos trust input therefore remain necessary and independent of the selected distribution mechanism.
- **Storage, IPC, and background work:** Native processes can normally use the user's filesystem, Unix-domain sockets, inherited file descriptors, and long-running user or system services.
  The selected profile must narrow those facilities when code is not trusted with the user's ambient authority.
- **Logos consequence:** Linux can implement the complete desktop Runtime model,
  including direct loading and hosted local Transport,
  but `sandbox` placement requires a concrete profile rather than a generic claim that a child process is isolated.

### 11.2 macOS

- **Execution and isolation:** macOS supports native dynamic libraries, child processes, XPC services, App Sandbox, and Hardened Runtime protections.
  App Sandbox restricts filesystem, network, device, and other access through signed entitlements, while Hardened Runtime restricts code injection, library loading, and executable-memory behavior unless specific exceptions are granted.
- **Installation, signing, and updates:** Mac App Store distribution requires App Sandbox.
  Software distributed outside the store normally uses Developer ID signing, Hardened Runtime, notarization, and Gatekeeper assessment.
  Store-managed and independently distributed applications have different update paths.
  Logos package signing does not replace Apple code signing or notarization.
- **Storage, IPC, and background work:** A sandboxed application receives a container and uses entitlements or user-selected file access for resources outside it.
  XPC provides process separation and on-demand service lifecycle; persistent agents and daemons require platform-specific installation and service-management configuration.
- **Logos consequence:** A macOS profile must state whether the Runtime is sandboxed, which host or service entitlements apply, how library validation permits approved modules, and whether a provider is an embedded library, XPC service, or separately installed process.

### 11.3 Windows Desktop

- **Execution and isolation:** Traditional Win32 processes and dynamic libraries normally run with the user's broad desktop authority.
  Restricted tokens, AppContainer, Job Objects, process mitigations, and access-control lists can reduce authority or constrain resources, but an MSIX-packaged desktop application is not automatically an AppContainer application.
- **Installation, signing, and updates:** MSIX provides signed packages, package identity, protected installation, clean removal, and managed update mechanisms.
  Traditional installers and unpackaged applications remain possible and have different trust and update properties.
  Logos package verification remains independent of Authenticode, MSIX signing, or Store trust.
- **Storage, IPC, and background work:** Full-trust applications can use normal filesystem, registry, named-pipe, socket, service, and process facilities.
  MSIX and AppContainer can redirect or restrict storage and registry access, and packaged app services or background tasks require package identity and declared capabilities.
- **Logos consequence:** A Windows profile must distinguish full-trust process placement from AppContainer placement and must identify which token, capability, Job Object, storage, IPC, and update controls enforce the selected Logos permissions.

### 11.4 Android

- **Execution and isolation:** Android assigns each application a UID and kernel-enforced application sandbox, with SELinux adding mandatory access control.
  Java, Kotlin, and native code inside one application share that application's authority; loading a module into the Runtime application's process does not create another application sandbox.
- **Installation, signing, and updates:** Every APK must be signed, and signing identity participates in update continuity and signature-level permissions.
  Distribution can use Google Play, another store, enterprise management, or user-approved installation from another source.
  Android discourages dynamic code loading from outside the installed application, and some distribution policies restrict it.
- **Storage, IPC, and background work:** Applications use app-specific or scoped storage and communicate through permission-checked platform components and Binder-based services.
  Background services and implicit broadcasts are restricted; scheduled jobs and user-visible foreground services cover defined background cases.
- **Logos consequence:** An Android profile can statically include trusted modules in one application, run native providers in ordinary application-owned processes that share the application UID, use an Android-specific isolated-process service, or place providers in separately installed applications with platform IPC.
  The last option gains an application sandbox boundary but introduces platform package, signing, lifecycle, and user-consent requirements.

### 11.5 iOS And iPadOS

- **Execution and isolation:** All third-party applications are sandboxed and executable code is subject to mandatory Apple code signing and signed entitlements.
  General loading of downloaded native plug-ins or self-modifying executable code is not part of the ordinary third-party application model.
- **Installation, signing, and updates:** Applications and executable components must use platform-authorized signing and distribution paths.
  The available store, marketplace, direct, development, or managed-distribution path depends on platform rules, region, and deployment context.
  Logos package signing remains useful for Logos package identity and manifest integrity but cannot replace platform authorization to execute code.
- **Storage, IPC, and background work:** Each application has its own data container.
  Related applications and extensions can share selected storage and IPC through signed App Group entitlements, while other interactions use platform-mediated APIs.
  Background execution is limited to declared modes and scheduled or system-managed work.
- **Logos consequence:** The normal iOS baseline is statically linked or bundled trusted module code using direct mode inside one application.
  Separate application or extension providers require an iOS-specific transport and lifecycle profile.
  A deployment conforming to these specifications MUST NOT assume that arbitrary post-install native module loading is available.

### 11.6 Security And Operational Tradeoffs

| Choice | Benefit | Security and operational cost |
|---|---|---|
| In-process direct mode | Lowest call overhead, simple deployment, and conventional same-process debugging | Expands the host's trusted computing base and normally provides no memory or ambient-authority boundary |
| Separate local process | Crash separation, independent lifecycle, and an OS enforcement point | Adds launch, IPC, supervision, state handoff, and cross-process debugging complexity |
| Sandboxed process or application | Least-authority filesystem, network, device, process, and resource control | Requires platform-specific profiles, permission mapping, packaging, diagnostics, and failure handling |
| Native platform integration | Access to OS storage, credentials, notifications, UI, networking, and background facilities | Adds user-consent, entitlement, privacy, lifecycle, and revocation requirements |
| Logos and platform signing | Authenticates exact Logos package bindings while also satisfying platform execution rules | Requires distinct trust anchors, protected signing keys, rotation, revocation, and update continuity |

The desktop-first Core architecture chooses native capability and inspectability as its starting point.
It does not treat the absence of a browser sandbox as permission for ambient access.
Deployments that accept third-party code must select enforceable placement and permission profiles, and mobile deployments must adapt realization rather than weakening the Core authorization and commitment boundaries.

## 12. Baseline Security Properties

The consolidated Core security model has the following baseline properties:

- dynamically loaded artifact acceptance and execution authorization complete before native code is mapped;
- direct static binding uses a protected deployment registration and completes execution authorization before module initialization;
- normal loading, retained symbol resolution, and ordinary method dispatch can proceed after acceptance without a trust check for each symbol or call;
- package signatures authenticate manifest commitments and artifact hashes but do not grant installation, execution, permission, or route authority;
- schemas, identifiers, commitments, signatures, and authenticated connections are policy inputs rather than authority by themselves;
- authority is evaluated for an authenticated consumer, exact operation, and bounded scope;
- Runtime enforces lifecycle, provider visibility, route, selected-contract, method, event, and Runtime Control decisions at its controlled boundaries;
- Capability Authority decisions and grants are not bearer credentials, and the target Runtime issues the one-time route ticket used for protected provider-session establishment;
- production remote profiles mutually authenticate Runtimes, prohibit cleartext fallback, and independently authorize Runtime Control and provider access;
- every Request, successful Response, and Event has a compact payload commitment that the receiving boundary independently recomputes;
- audit-retention policy can select which computed request or response roots are retained but cannot disable commitment computation;
- call evidence authenticates one retained call record and optional verified views without granting authority or proving computation correctness;
- in-process native code is trusted for the deployment or confined by an explicitly defined in-process mechanism;
- process, sandbox, and container labels do not establish isolation strength without a selected enforceable platform profile;
- inability to obtain, validate, or enforce a required trust, authority, transport, commitment, or isolation result fails the dependent operation closed.

These properties form one enforcement chain rather than interchangeable security mechanisms.
For example, a signed package still requires execution authorization, and an authorized module still requires containment appropriate to its permissions and code trust.

## 13. Safe Deployment Defaults

A production deployment should begin from these defaults unless protected configuration selects a stricter or explicitly different profile:

- reject dynamically loaded executable material that lacks accepted package evidence or a protected bootstrap digest,
  and reject direct static binding that lacks a protected deployment registration;
- configure package-signing, evidence-signing, and remote-enrollment trust separately by purpose;
- permit direct in-process loading only for code trusted to share the Runtime's address space;
- place third-party native code behind a selected process or application isolation profile whose required controls are available;
- deny requested filesystem, network, process, device, credential, persistent-state, and privileged service permissions unless active authority allows them and a named component can enforce them;
- keep remote Runtime Control exposure, remote provider listeners, and provider exports disabled until protected deployment input enables the required surface;
- never fall back from a production remote profile to an unauthenticated carrier;
- expose only the provider, selected contract, methods, events, grants, routes, and audit records visible to the authenticated consumer;
- keep route tickets, private keys, proof-of-possession secrets, and reusable credentials out of logs and records returned or exchanged through Logos contracts;
- fail a launch rather than silently substituting weaker isolation or resource controls;
- invalidate cached verification and authority results when their trust anchor, signer, active policy, grant, enrollment, freshness state, or enforcement precondition no longer remains accepted;
- make development trust anchors, relaxed debugging entitlements, implementation-local transport test hooks, and unknown-artifact analysis explicit non-production configuration.

A local development deployment can use a locally generated package-signing trust anchor and locally signed test packages through the same verification path as production packages.
This supports implementation and conformance testing without weakening the production format or adding an unsigned compatibility path.

User-facing approval can create or modify protected policy or grants, but the prompt itself is not an authority result.
Turning approval into trusted policy input requires an authenticated approving principal, accurate presentation of the requested scope, and delivery through a trusted administrative path.

## 14. Security Boundary Summary

The following table summarizes required security treatment and the owning specification or deployment boundary.

| Concern | Required treatment | Normative owner or boundary |
|---|---|---|
| Minimal authority model for local third-party modules | Package verification, module-execution scope, requested permission scopes, provider access, and enforceable placement remain distinct checks using the existing decision and grant model. | Capability Authority, Package Manager, Runtime, and Module Loader |
| Minimal authority model for remote Runtime access | Mutually authenticated Runtime identity and enrollment establish the source-to-target Runtime boundary; each Runtime Control or provider operation identifies a consumer and requires scoped authorization; the target Runtime issues a bound one-time route ticket. | Runtime, Transport, and Capability Authority |
| Ordinary versus administrative Runtime Control methods | Core defines no fixed user, operator, or administrator classes. Every Runtime Control method requires explicit provider and method authority, and ordinary modules receive none merely from module status. | Runtime and Capability Authority |
| Package binding to schemas, artifacts, and requested permissions | The package COSE signature authenticates the complete manifest commitment, and Package Manager verifies the exact materialized bytes against the signed artifact hashes. | Package Manager |
| Sandbox profiles across platforms | These specifications require fail-closed realization of a selected profile, not identical sandbox strength across operating systems. A deployment may claim containment for untrusted code only when its platform profile names the controls, permission mapping, enforcement components, and unavailable-control behavior. | Concrete platform or deployment profile; no identical cross-platform sandbox strength is specified |
| Modules acceptable for in-process hosting | There is no ABI or package class that makes in-process code safe. The code is trusted for that deployment or a selected profile defines an enforceable in-process containment mechanism. | Runtime and Capability Authority |
| User inspection and approval | Capability Authority represents the resulting allow or deny decision and grant or revocation records, including the `approval-required` denial reason. Prompt presentation and administrator UX are application or deployment concerns. | Capability Authority owns records; approval presentation is outside this specification |
| Audit record for remote calls | Remote calls use the common call audit record rather than a remote-specific type. The record binds the exact call scope, decision identifier, outcome, and selected request or response commitments; the common shape identifies the consumer and a separate target module instance when applicable. Audit queries return at most the 1000 most recent visible matching records. | Capability Authority and Runtime |
| Unknown executable inspection | Normal discovery uses non-executable metadata and never maps an unknown library. Executing code for analysis requires a separately defined isolated analysis environment outside the normal loading path. | Package Manager and Runtime establish accepted evidence; Module Loader verifies the artifact at the loading boundary; analysis tooling remains outside the normal loading path |

## Informative References

### Core Specifications

- LOGOS-MODULE-INTERFACE;
- LOGOS-MODULE-COMMITMENT-MODEL;
- LOGOS-MODULE-HASH-PROFILE;
- LOGOS-MODULE-RUNTIME;
- LOGOS-MODULE-TRANSPORT;
- LOGOS-MODULE-CAPABILITY-AUTHORITY;
- LOGOS-MODULE-CONFIGURATION;
- LOGOS-MODULE-PACKAGE-MANAGER;
- LOGOS-MODULE-LOADER;
- LOGOS-MODULE-SYSTEM-BCP.

### Platform Documentation

- Linux Kernel documentation for [seccomp filters](https://docs.kernel.org/userspace-api/seccomp_filter.html), [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), and [namespaces](https://docs.kernel.org/admin-guide/namespaces/index.html);
- Apple documentation for [macOS App Sandbox](https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox), [Hardened Runtime](https://developer.apple.com/documentation/security/hardened-runtime), [notarization](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution), [XPC](https://developer.apple.com/documentation/xpc), [iOS runtime security](https://support.apple.com/guide/security/sec15bfe098e/web), and [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups);
- Microsoft documentation for [MSIX](https://learn.microsoft.com/windows/msix/overview), [MSIX containerization](https://learn.microsoft.com/windows/msix/msix-containerization-overview), [application capabilities](https://learn.microsoft.com/windows/apps/package-and-deploy/app-capability-declarations), and [app services](https://learn.microsoft.com/windows/apps/develop/launch/app-services);
- Android documentation for [platform security features](https://source.android.com/docs/security/features), [application fundamentals](https://developer.android.com/guide/components/fundamentals), [app signing](https://developer.android.com/studio/publish/app-signing), [dynamic code loading](https://developer.android.com/privacy-and-security/risks/dynamic-code-loading), [background execution limits](https://developer.android.com/about/versions/oreo/background), and [isolated services](https://developer.android.com/guide/topics/manifest/service-element).

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
