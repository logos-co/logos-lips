# LOGOS-MODULE-SYSTEM-BCP

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module System BCP                                       |
| Slug         | 313                                                           |
| Status       | raw                                                           |
| Category     | Best Current Practice                                         |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification describes how the Logos module specifications fit together when building a complete Logos module system.
The architecture has three main layers:
Interface and Commitment; Configuration, Runtime, and Transport; and Runtime-adjacent module services.
LOGOS-MODULE-SECURITY-CONSIDERATIONS provides cross-cutting security analysis across those layers.

The purpose is to keep ownership clear across interoperable implementations.
Interface and Commitment define contracts, method identity, typed value identity, schema roots, value roots, and proof paths.
Configuration defines schema-typed module configuration and its Runtime-owned state and delivery semantics.
Runtime and Transport select providers, establish routes, move typed values, and expose invocation paths.
Capability Authority, Package Manager, and Module Loader add authority, package, artifact, realization, and deployment behavior around those contracts and routes.

## 1. Three-Layer Stack

The Logos module system uses this three-layer stack:

```text
Cross-cutting security analysis
  LOGOS-MODULE-SECURITY-CONSIDERATIONS

Layer 1 — Interface and Commitment
  LOGOS-MODULE-INTERFACE
  LOGOS-MODULE-COMMITMENT-MODEL
  LOGOS-MODULE-HASH-PROFILE

Layer 2 — Configuration, Runtime, and Transport
  LOGOS-MODULE-CONFIGURATION
  LOGOS-MODULE-RUNTIME
  LOGOS-MODULE-TRANSPORT

Layer 3 — Runtime-adjacent module services
  LOGOS-MODULE-CAPABILITY-AUTHORITY
  LOGOS-MODULE-PACKAGE-MANAGER
  LOGOS-MODULE-LOADER
```

LOGOS-MODULE-SECURITY-CONSIDERATIONS is analysis across the stack rather than another layer.
The layer order is also the specification dependency direction:
a higher layer may consume identities and records from a lower layer,
while conformance to a lower-layer specification does not require a higher-layer module contract.

The stack is not an implementation sequence.
An implementation may build several layers together.
The stack is a responsibility map for deciding which specification owns a concept.
The complete-system composition requirements in this BCP do not add another layer or change individual-specification conformance.

`cdCDDLe` and Logos common schema material are schema inputs used by the first layer.
Host and product profiles apply the stack to a concrete product.
They may define presentation, deployment, platform integration, and product workflows.
They do not add a fourth Core layer.

Host-shell applications sit above the three-layer Core stack.
They may use modules to consume Core contracts,
but host shell is an application description rather than a Core role or participant class.
The Core specifications do not define host-shell-specific identity, lifecycle, authority, routing, or realization semantics.

## 2. System Roles

LOGOS-MODULE-RUNTIME Terminology defines the canonical system roles and invocation boundaries.
This BCP uses those definitions and states only the additional consequences for complete-system composition.

Every participant in the Logos module system is a module instance.
An application that invokes a Logos contract, including a command-line tool, automation client, or diagnostic tool,
therefore participates through ordinary module identity, lifecycle, authority, routing, and audit semantics.
The Runtime engine, Runtime host, bootstrap machinery, operating-system objects, protected inputs, humans, and unauthenticated peers remain outside the participant model.
They do not receive unconstrained consumer references.
If a later specification needs a human, user-session, device, organization, or agent identity, it must define that identity and its delegation relationship explicitly.

Something should be a separate module when it needs independent identity, lifecycle, provenance, permissions, state, route ownership, audit attribution, placement, isolation, update, or remote-execution behavior.
Objects that always share those properties may remain internal implementation objects.
Several unrelated primary concrete contracts should not be aggregated into one module.

The Runtime's own identity identifies its boundary and intrinsic Runtime Control exposure.
An enrolled source Runtime authenticates a remote boundary with that identity.
When a module performs an operation, Runtime binds that module instance as the consumer and active authority policy must permit the consumer and requested operation.

### 2.1 Presentation And Consumer-Only Modules

Presentation and consumer-only modules use the same identity, lifecycle, authority, routing, state, placement, and audit model as other modules.
Their facets do not create separate participant classes.

A presentation module may provide no callable contract.
It can declare provider requirements or acquire authorized routes as a consumer without inventing a schema, provider record, or no-op dispatch surface.
Runtime owns its module lifecycle and authority context.
Its local realization follows the complete-system composition rule in Section 5.1 when that conformance is claimed.

A Runtime Control operation may name another module instance as its target without making that target the consumer.
A presentation or consumer-only module acquires and uses routes under its own module-instance identity as consumer.

This specification does not define a window system, rendering protocol, process-realization backend, container implementation, or product workflow.
Those details belong to the selected presentation, platform, deployment, and product profiles.

## 3. Layer Responsibilities

### 3.1 Interface and Commitment

LOGOS-MODULE-INTERFACE defines concrete and reusable interface contracts.
It owns the following concepts:

- CDDL schema conventions;
- flat concrete module contracts;
- flat reusable interface contracts;
- `_implements`;
- bare method names;
- events;
- C ABI mapping;
- dispatch ABI;
- deterministic CBOR value mapping.

LOGOS-MODULE-COMMITMENT-MODEL defines semantic schema identity, method identity, value identity, semantic paths, and normalized schema/value objects.
It says what is committed.

LOGOS-MODULE-HASH-PROFILE defines the physical hash profile, domain separation, packing, chunking, value roots, and verified-view proof material.
It says how the commitment model is hashed for this profile.

This layer owns contract identity and value identity.
It should not need Runtime Control records, provider addresses, route records, package-manager catalogs, Module Loader realization descriptors, capability decisions, or application policy.

### 3.2 Configuration, Runtime, and Transport

LOGOS-MODULE-CONFIGURATION defines configuration-schema bindings, configuration values, Runtime-owned configuration state, startup delivery, and live reconfiguration.
It assigns the exact configuration payload carried through the generic pointer-and-length ABI fields defined by LOGOS-MODULE-INTERFACE.

LOGOS-MODULE-RUNTIME defines how module instances are admitted and lifecycle-tracked.
It defines how providers are registered, selected, routed, observed, and revoked.
It owns the following runtime concepts:

- intrinsic Runtime Control exposure;
- module-instance admission and lifecycle;
- module-instance addresses;
- route establishment;
- selected-contract routing;
- runtime provider records;
- runtime input records;
- Runtime Control.

LOGOS-MODULE-TRANSPORT defines how schema-defined values move across local or remote transport boundaries.
It owns the following transport concepts:

- transport envelopes;
- Hello validation;
- request/response messages;
- events;
- cancellation;
- framing;
- transport-profile requirements and protocol evolution boundaries.

This layer consumes contract, method, and value identities and generic ABI mechanics from Interface and Commitment.
It does not redefine method identity or value-root identity.

### 3.3 Runtime-Adjacent Module Services

LOGOS-MODULE-CAPABILITY-AUTHORITY defines the Capability Authority module contract for authorization decisions, denials, grants, evidence, remote enrollment, and audit references.

LOGOS-MODULE-PACKAGE-MANAGER defines the Package Manager module contract for packages, catalogs, install/update/removal actions, dependency records, installed state, and Runtime handoff records.

LOGOS-MODULE-LOADER defines the Module Loader module contract for direct static binding,
direct dynamic loading, and hosted dynamic loading in a process, sandbox, or container.

A module implemented in a language that does not directly export the canonical C ABI
uses generated or handwritten adapter code in its static binding or dynamic library.
A module kit can generate that adapter from the canonical contract.
The adapter is part of the module implementation and does not define another contract,
participant, lifecycle, or realization strategy.

This layer consumes Interface/Commitment identities and Configuration/Runtime/Transport records.
It adds authority, package, artifact, realization, deployment, and audit behavior.
It does not redefine schema identity, method identity, or value-root identity.

### 3.4 Cross-Cutting Security Analysis

LOGOS-MODULE-SECURITY-CONSIDERATIONS analyzes threats, trust boundaries, enforcement points, and residual risks across all three layers.
Normative behavior remains with the specification that owns the affected contract, record, operation, or profile.
Selected security and platform profiles supply deployment-specific trust anchors, isolation mechanisms, and protected provisioning rules.
The analysis does not introduce another layer or decision surface.

## 4. Evidence Through the Stack

Evidence should follow the stack.
Interface and Commitment identify the contract, method, and value.
Runtime and Transport identify the selected contract, provider route, and invocation path.
Capability Authority, Package Manager, and Module Loader identify authority, package, artifact, realization, and deployment context.
Security Considerations analyzes the threats and controls that connect evidence across those layers.

For example, a concrete storage module may implement a metrics-provider interface.
Interface and Commitment define:

- the concrete storage schema root;
- the implemented metrics-provider schema root;
- the fact that the storage schema root commits to `_implements` metrics-provider;
- the metrics method identity under the metrics-provider schema root;
- the request and response value roots under the metrics-provider schema root.

Runtime and Transport can then identify:

- one provider record backed by the storage module instance;
- the selected provider route;
- the selected route contract;
- the selected provider contract commitment validated by Transport Hello;
- the invocation path used for the method call.

Capability Authority, Package Manager, and Module Loader can then identify:

- the authority decision for the route or method call;
- package and artifact provenance;
- the realization and sandbox context;
- audit records that connect the call to its request/response roots.

These records are linked through shared contract and value identities.
They do not move an implemented interface method into the provider's concrete schema tree.
They also do not replace method identity or value identity with provider, route, package, authority, or realization identity.

## 5. Core Profiles, Identifiers, And Conformance

The following identifiers are assigned by their normative owners:

| Kind | Identifier |
|------|------------|
| `cdCDDLe` canonical model | `cdcddle` |
| Commitment model | `logos.commitment-model.2026-08` |
| Hash profile | `logos.hash-profile.2026-08.choice-index` |
| Hash suite | `logos.hash-suite.blake3-256` |
| Protected local transport | `logos.local.unix-stream` |
| Mandatory remote transport | `logos.remote.tls-tcp` |
| Optional remote transport | `logos.remote.quic` |
| Route ticket | `logos.route-ticket.random-256` |
| Package signature | `logos.package-signing.cose-sign1-ed25519` |
| Call evidence | `logos.call-evidence.cose-sign1-ed25519` |
| Runtime Control | `logos_runtime_control` |
| Capability Authority module | `logos_capability_authority` |
| Module Loader module | `logos_module_loader` |
| Package Manager module | `logos_package_manager` |

### 5.1 Individual And Complete-System Conformance

An implementation may claim conformance to an individual Core specification without implementing a module contract from a later layer.
Accordingly, conformance to LOGOS-MODULE-RUNTIME or LOGOS-MODULE-TRANSPORT does not require implementation of LOGOS-MODULE-LOADER.

A deployment claiming conformance to this BCP as a complete Logos module system MUST establish its initial Module Loader provider through protected, non-recursive bootstrap.
After Runtime binds that provider,
Runtime MUST use it to realize every subsequent local module implementation
and MUST NOT substitute an independently started implementation or pre-existing provider endpoint for Module Loader realization.
Remote-module facade creation does not invoke Module Loader because it creates no local module implementation or lifecycle.

### 5.2 Profile Terminology

A named Core profile is a complete, interoperable behavior selected by a stable identifier and defined by one normative owning specification.
Its owner MUST define the profile's scope, required algorithms or mechanisms, validation rules, failure behavior, and relationship to other profiles.
A profile identifier is not a generic extension name or an invitation to interpret opaque data without a defining specification.

Some identifiers in this section select fixed formats or mechanisms rather than choices among alternatives.
An implementation does not select among hash, package-signature, call-evidence, or route-ticket profiles.
It implements the required identifier and rejects unsupported alternatives where the owning specification requires rejection.

Profile decisions occur at three distinct levels:

- the owning specification fixes mandatory rules and baseline profiles;
- an implementation decides which profiles classified as optional it supports;
- a deployment, Runtime policy, or typed request selects among the supported alternatives at the selection point defined by the owning specification.

An implementation MUST NOT replace a specification-fixed profile with another mechanism.
It also MUST NOT override an explicit deployment or request selection merely because it supports another profile.

A deployment profile is different from a named Core profile.
It records concrete host choices such as trust provisioning, isolation mechanisms, filesystem placement, resource limits, and platform integration where the Core specifications deliberately leave those choices to deployment.
A deployment profile has no globally interoperable meaning unless a normative specification assigns it an identifier and complete semantics.

Terms such as product profile, host profile, security profile, isolation profile, audit profile, or platform profile MUST NOT create independent Core selection layers merely by being named.
Unless a normative specification defines one as a named Core profile,
such a term denotes part of the deployment profile or local policy.

### 5.3 Defined Profile Matrix

The `Support requirement` column states what a conforming implementation must implement.
The `Selection authority` column states who chooses the behavior for a concrete operation or deployment.

| Area | Identifier or selector | Support requirement | Selection authority |
|------|------------------------|---------------------|---------------------|
| Module-boundary encoding | Logos deterministic CBOR rules in LOGOS-MODULE-INTERFACE | Mandatory for every implementation encoding module-boundary values. | Fixed by LOGOS-MODULE-INTERFACE; there is no implementation or deployment choice. |
| Physical commitments | `logos.hash-profile.2026-08.choice-index` with `logos.hash-suite.blake3-256` | Mandatory for every implementation producing or verifying Logos commitments. | Fixed by LOGOS-MODULE-HASH-PROFILE; there is no implementation or deployment choice. |
| Package signatures | `logos.package-signing.cose-sign1-ed25519` | Mandatory for every conforming Package Manager. | Fixed by LOGOS-MODULE-PACKAGE-MANAGER wherever that specification requires a package signature. |
| Call evidence | `logos.call-evidence.cose-sign1-ed25519` | Mandatory for every conforming Runtime. | The format is fixed by LOGOS-MODULE-CAPABILITY-AUTHORITY. Audit policy selects whether call evidence is produced. |
| Route tickets | `logos.route-ticket.random-256` | Mandatory for Runtime and Transport when using the protected local or production remote profiles below. | Fixed by LOGOS-MODULE-TRANSPORT after one of those transport profiles is selected. |
| Protected local transport | `logos.local.unix-stream` | Mandatory for a conforming local-transport implementation on a system that supports Unix-domain stream sockets. | Runtime placement or deployment selects local transport; the profile is then fixed. |
| Production remote transport | `logos.remote.tls-tcp` | Mandatory for an implementation supporting production remote Runtime transport. | Deployment or Runtime policy selects the remote endpoint; this is the mandatory supported production choice. |
| Production remote transport | `logos.remote.quic` | Optional to implement. | Deployment or Runtime policy may select it only when both endpoints support it. Selection MUST be explicit. |
| Package realization | `lgx` | Optional individually; a conforming Package Manager MUST implement at least one package realization profile. | A request selects it with `source.kind` equal to `"lgx"`. |
| Package realization | `nix` | Optional individually; a conforming Package Manager MUST implement at least one package realization profile. | A request selects it with `source.kind` equal to `"nix"`. |
| Deployment behavior | No Core-wide identifier | The implementation supplies the mechanisms required by its claimed deployment. | The deployment owner chooses and documents the applicable behavior listed in Section 5.4. |
| Presentation interoperability | No profile assigned | No support requirement is defined. | No implementation or deployment may infer presentation behavior required of other conforming implementations from a generic profile name or opaque input. |
| Future numeric, compatibility, audit, or isolated-analysis behavior | No profile assigned | No support requirement is defined. | No selection exists until a normative owning specification defines one. |

A conforming Package Manager MUST implement at least one of the `lgx` or `nix` realization profiles.
When an owning specification defines a default,
omitting an explicit selection invokes only that default.
Failure of a selected profile MUST NOT cause fallback to another profile unless the owning specification explicitly defines that fallback as safe.

The remote identity and channel-security choice is part of the selected remote transport profile.
It is not an independent profile selection.
For example, `logos.remote.tls-tcp` selects its transport, mutual authentication, Runtime enrollment, channel binding, and route-ticket requirements as one interoperable behavior.

### 5.4 Deployment Profile Requirements

A complete deployment MUST document every applicable choice that the Core specifications assign to deployment.
At minimum, that documentation MUST identify:

- supported Package Manager source kinds;
- enabled local and remote transport profiles;
- protected trust inputs and provisioning rules for package signing, remote Runtime enrollment, and call-evidence signing;
- Module Loader realization mappings and the concrete process, sandbox, or container mechanisms used;
- permission definitions, constraint mappings, and the component that enforces each constraint;
- isolation, filesystem, network, device, process, credential, and resource-control behavior;
- Runtime directories, module state realization, retention, cleanup, and recovery policy;
- concrete resource bounds required by Package Manager, Runtime, Transport, Module Loader, and schema processing;
- any selected presentation profile and its platform integration.

Documenting a deployment choice does not require another conforming implementation to recognize or support it.
A deployment MUST fail a dependent operation when it cannot satisfy the selected profile or enforce a required constraint.
It MUST NOT silently replace the selected behavior with a weaker mechanism.

### 5.5 Rules For Additional Profiles

A normative specification SHOULD introduce another named profile only when a complete interoperable behavior cannot be expressed by an existing profile, ordinary typed field, or local deployment policy.
The specification MUST define:

- one stable identifier and its normative owner;
- the exact selection point and any default;
- whether support is mandatory, conditional, optional, development-only, or prohibited in production;
- the complete data schema, algorithms, validation rules, and failure behavior;
- how the profile composes with or excludes every related profile;
- downgrade, fallback, and unknown-profile behavior;
- the conformance tests or vectors needed for independent implementations.

A generic string, opaque byte string, configuration key, backend name, or policy label MUST NOT define a Core profile by itself.
Implementation-local diagnostics and test hooks are not Core profiles and do not require Core identifiers.
They MUST NOT appear in addresses, discovery results, or negotiation fields defined by these specifications.
Unknown or unsupported profile identifiers MUST fail the dependent operation unless the owning specification explicitly permits the identifier to be ignored.
A future profile does not affect current conformance until a normative specification assigns its identifier and complete semantics.

## 6. Module Contract Code Generation (Informative)

Code generation is an implementation technique rather than a conformance requirement.
A module contract generator can accept a Logos CDDL schema set or equivalent C declarations that conform to the canonical mapping in LOGOS-MODULE-INTERFACE.
When C declarations are the authoring input, the generator produces the equivalent CDDL and verifies that it maps back to the same canonical C declarations.

The schema input can contain:

- the module's primary concrete contract, when present;
- its implemented interface contracts;
- its referenced supporting schema documents; and
- its optional module configuration schema.

The generator also uses the pinned Logos common schema surface when an input document references one of its definitions.
These schema documents are the contract and configuration inputs to generation.
Generation uses the models and mappings defined by their owning specifications.
A module with no callable contract can use configuration and initialization generation without receiving provider ABI or dispatch output.

An authoring tool can accept CDDL module syntax or a local-namespace shorthand as non-normative input.
That approach preserves interoperability only when the tool emits the complete ordinary CDDL documents with explicit qualified names before `cdCDDLe` canonicalization and commitment-model construction.
The emitted CDDL remains the specification and conformance input.
Core does not define or require such a preprocessor in this specification.

From those inputs, one generator can produce:

- the canonical C declarations;
- typed values and Logos deterministic CBOR codecs;
- provider ABI and dispatch glue for callable contracts;
- typed consumer call and event bindings;
- call-surface descriptors, contract identities, and commitments;
- structured initialization glue; and
- typed startup-configuration decoding and, when requested, live-reconfiguration adapter glue.

Generated initialization and provider code supplies adapter points for module-owned behavior.
It does not define module business logic or infer the semantic mapping to an independently designed library API.
The underlying library can retain its own public API and internal types behind that adapter.

A separately specified language mapping can provide idiomatic bindings or a language-native authoring form.
Such a mapping must map deterministically and without loss to the same Logos CDDL contract, canonical C ABI, deterministic CBOR values, and commitment semantics.
It must reject language constructs that cannot be represented by that contract model.
It does not define an alternative module contract, native ABI, encoding, or schema-identity system.

Generated code is not required for conformance.
A handwritten implementation conforms when it produces the same required artifacts and observable behavior.

## 7. Host-Shell Applications Above The Core Stack (Informative)

This section is informative.
It illustrates how a command-line or graphical host-shell application can apply the Core stack.
It defines no host-shell contract, role, identity, lifecycle, authority, route, realization kind, or conformance requirement.

A host-shell application can be implemented by an ordinary module implementation with terminal or graphical presentation.
The participating implementation receives ordinary module identity and uses that module instance as consumer.
It does not obtain distinct Core semantics from being described as a host shell.
This permits a deployment in which every application that participates in Core,
including each command-line or graphical host shell,
is realized by Module Loader as an ordinary module instance.

Before that module instance exists,
protected deployment activation can request activation of an accepted application module.
The activation input is not a Logos contract invocation,
does not identify a consumer,
and does not introduce a launcher or controller participant.
A deployment can keep Runtime running before activation,
activate the Runtime host on demand,
or report that Runtime is unavailable.
Runtime completes its required bootstrap authority establishment and initial Module Loader binding before realizing another local module.

The protected activation resolves to an accepted module declaration.
Runtime validates that declaration and active policy,
creates the module-instance identity,
selects the required realization,
and asks Module Loader to realize the implementation.
The activation source does not choose an arbitrary artifact, module-instance identity, weaker realization, permission grant, or Runtime authority.

Runtime supplies consumer-bound Runtime Control access for the new module instance.
Module Loader ensures that the selected realization makes the corresponding process-local binding available through the selected implementation form.
A selected presentation or deployment profile can additionally supply a terminal session,
graphical presentation surface, or another presentation handoff.
These presentation resources do not identify the consumer or grant Runtime authority.

Application code receives its Runtime Control binding and presentation handoff through the selected initialization and presentation profiles.
It can then run a terminal command loop, one-shot command, or graphical event loop without performing a separate self-admission step.

After admission, the application module uses Runtime Control to establish routes to Package Manager and other providers according to active policy.
It can use Package Manager to inspect or install a package
and then request module startup through Runtime Control.
Runtime owns the lifecycle decision and invokes Module Loader when realization is required.
The application module does not call Module Loader directly to bypass Runtime lifecycle, placement, or authority enforcement.

A one-shot application return, process exit, or authorized stop follows the ordinary module teardown defined by LOGOS-MODULE-RUNTIME.
It creates no host-shell-specific cleanup path.
Retained observation and audit material remains attributed to the module instance as required by the owning specifications.

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
