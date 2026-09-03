# LOGOS-MODULE-PACKAGE-MANAGER

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Package Manager                                         |
| Slug         | 311                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the Package Manager module contract.

The Package Manager contract is an intentionally limited Core baseline.
It provides the package verification, dependency-closure, materialization,
installed-state, and Runtime-handoff behavior needed by the Core architecture.
It defines a bounded dependency solver, not a general package ecosystem or
an arbitrary dependency-constraint language.
More advanced catalog policy, alternative or optional dependencies,
general transactions, rollback operations, progress reporting, and lifecycle automation may be defined separately.

Package Manager is responsible for package, catalog, install, update, removal, dependency, and package-state operations.
It is a Logos module contract for a runtime-adjacent responsibility.
A provider bound by runtime or deployment policy to this contract is a system service provider.
Every Package Manager provider MUST be a local module provider backed by a local module instance.
It uses the same contract, provider, route, and transport model as other local Logos module providers.
Runtime MUST maintain ordinary provider and lifecycle records for its module instance.
Package Manager providers are not a separate module class, ABI class, transport class, or lifecycle class.
An implementation MAY co-locate or statically link Package Manager code.
Runtime MUST represent that code as a direct-mode local module instance.
Remote facades MUST NOT be bound as Package Manager providers in this revision.
Host or deployment services that are not module providers MUST NOT be bound as Package Manager providers in this revision.
Implementing the Package Manager contract does not grant authority.
Authority comes from runtime or deployment policy.
Bootstrap policy may bind a provider to the package-manager responsibility.
It may grant the operations needed for that deployment.

The canonical flat runtime module name is `logos_package_manager`.
The canonical schema namespace is `logos.package_manager`.
The `logos.package_manager` CDDL blocks in this specification collectively
define the normative module contract.
`logos_package_manager.cddl` is an extracted machine-readable mirror of those blocks.
If the extracted artifact differs from this specification,
this specification governs.
The Package Manager module schema imports two supporting schemas: Package Manifest from Section 4 and Module Configuration Types from LOGOS-MODULE-CONFIGURATION.

Package Manager exposes Logos-level package records and operations.
It does not expose the internals of the underlying build or package tool.

This specification defines a small author-facing package manifest and an
expanded installed package record.
Package authors provide the manifest.
Package Manager derives installed records, local artifact records, and
Runtime handoff records after resolution or installation.

The package manifest is a CDDL-defined supporting schema.
It has schema identity and value commitment support.

Package Manager may materialize packages through the LGX or Nix realization profile.
LGX installs prebuilt package archives.
Nix realizes manifest-bearing flake outputs.
Both profiles consume the same canonical package manifest.
They produce the same package, artifact, and Runtime handoff records.

Package production is independent of the realization profile.
Any build system may produce an LGX package.
The LGX profile does not evaluate build definitions, build source code, or package-provided installation scripts.

This specification does not define module lifecycle semantics, routing semantics,
implementation realization mechanics, authorization policy, permission-grant semantics,
or a trust-store representation.
It defines the mandatory baseline package-signature container and algorithm
and Package Manager's responsibility to verify signed package material
before producing installed records or Runtime handoffs.
It also defines selection and enforcement boundaries for the optional SLSA package-provenance profile.
The excluded responsibilities belong to LOGOS-MODULE-RUNTIME, Module Loader,
Capability Authority, or security profiles.

## Scope

This specification defines:

- the canonical author-facing Logos package manifest;
- the manifest's role as a supporting schema with schema identity and
  value commitment support;
- the expanded installed package record derived by Package Manager;
- the LGX package structure used for prebuilt package material;
- the mandatory baseline package-signature container and algorithm;
- protected selection and fail-closed enforcement of the optional SLSA package-provenance profile;
- the LGX and Nix realization profiles;
- compatible platform-variant selection and local artifact materialization;
- package catalog query records;
- package inspect records;
- package source records;
- module declarations;
- implemented-interface and provider-requirement declarations carried in Runtime handoffs;
- artifact records;
- bounded deterministic transitive package dependency resolution;
- requested permission declarations as module metadata;
- install, update, and remove behavior;
- closed method-specific results and package errors;
- package-manager method request and response records;
- resolved runtime handoff records for LOGOS-MODULE-RUNTIME;
- the boundary between Package Manager, Runtime, Module Loader,
  Capability Authority, package producers, and Logos Storage.

This specification does not define:

- arbitrary version-range or Boolean dependency expressions;
- optional, alternative, feature-selected, or virtual dependencies;
- multi-objective optimization across dependency solutions;
- a Logos build language;
- a generic archive format;
- generic package installation scripts;
- package formats other than LGX;
- a package trust-policy language;
- a trust-store administration API;
- permission approval rules;
- a rollback API;
- a general package transaction state machine;
- a package lifecycle event stream;
- package install progress reporting;
- module lifecycle semantics;
- implementation realization mechanics.

## 1. Responsibility Split

Package Manager owns the Logos package contract.
It answers questions such as:

- which Logos packages are available or installed;
- which Logos modules a package declares;
- which optional primary module contract and implemented interface contracts
  are declared for a module;
- which package dependencies, module requirements, and requested permissions are declared by the package manifest;
- which local artifacts were produced or materialized for a package;
- which Runtime handoff records are derived for installed artifacts;
- which install, update, remove, and package method results are visible to
  the runtime host.

Package producers own the mechanics of building and assembling package artifacts.
The LGX profile consumes prebuilt packages.
The Nix profile delegates realization to Nix.
It does not expose Nix evaluation or store internals through ordinary Package Manager results.

Package Manager MUST NOT run package-provided installation scripts
while inspecting, resolving, installing, updating, or removing a package.
Package-controlled Nix work permitted by Section 7.3 is realization work rather than an installation script.
It is permitted only under that section's pre-verification rules.
It MUST materialize selected artifacts under Package Manager or deployment control
before Runtime or Module Loader uses them.

## 2. Logos Package Eligibility

Package material is installable only if it contains the canonical Logos package manifest.
It MUST also contain a compatible, complete artifact variant.
It MUST contain signature material accepted by the active package-signing profile.
LGX inputs MUST satisfy the LGX structure and validation rules defined by this specification.
Nix inputs MUST realize an output that satisfies the Nix profile defined in Section 7.3.

Package Manager is the verification owner for package signatures and manifest artifact hashes.
It MUST verify the package signature before reporting package material as installed
or producing Runtime handoffs from that material.
Runtime remains responsible for checking that executable bytes match the accepted artifact digest before realizing them.
Active authority policy separately decides whether a caller may install the package,
whether Runtime may execute its artifacts,
and whether requested permissions may be granted.
Successful signature or digest verification grants none of those authorities.

The package manifest is the source of author-declared Logos package facts.
Archive names, catalog metadata, Storage metadata,
and producer-specific build metadata MUST NOT override the canonical manifest.

The package manifest identifies:

- the package identity;
- the package Semantic Version;
- module declarations;
- artifact references;
- package dependency declarations;
- provider requirements and requested permissions declared for each module;
- platform and ABI constraints where needed.

The manifest MAY be authored directly or generated during package production.
Package Manager consumes the manifest from the selected realization profile.
It MUST NOT infer missing package facts from backend-specific metadata.

## 3. Manifest Location And Encoding

A conforming LGX package MUST contain the canonical manifest at:

```text
manifest.cbor
```

It MUST contain the corresponding package-signature container at:

```text
manifest.cose
```

The manifest file MUST be encoded as Logos deterministic CBOR.
Its decoded value MUST match `logos.package_manifest.manifest`.
It MUST be validated against the normative CDDL defined in Section 4.
Its encoded size MUST NOT exceed 4 MiB.
This bound leaves space within the Core 16 MiB Transport ceiling for derived installed records and configuration-bearing Runtime handoffs.

An LGX package MAY also contain a diagnostic JSON rendering at:

```text
manifest.json
```

The JSON rendering is not canonical.
If present, it MUST represent the same decoded value as `manifest.cbor`.
When the canonical CBOR manifest is present,
Package Manager MUST NOT use the JSON rendering as the source of package identity,
schema identity, artifact identity, or permission declarations.

The Nix profile defines the manifest location within a realized Nix output.

## 4. Manifest Schema Identity

`logos.package_manifest.manifest` is a CDDL-defined Logos data type.
It is authored in CDDL, processed through the Logos canonical schema model, and
assigned a Logos schema root according to LOGOS-MODULE-COMMITMENT-MODEL and
LOGOS-MODULE-HASH-PROFILE.

The package manifest schema namespace is:

```text
logos.package_manifest
```

This namespace is distinct from the Package Manager module API namespace:

```text
logos.package_manager
```

The `logos.package_manifest.manifest` type is the root manifest value type.
Its qualified schema definition name is:

```text
logos.package_manifest.manifest
```

The Package Manifest is a supporting schema because it defines non-callable package data used by the Package Manager contract.
It defines no methods, events, provider surface, module identity, or lifecycle.
Keeping it separate from the Package Manager module schema gives manifest values an independent schema root,
so a Package Manager API change does not change the schema identity of signed manifests.

The following CDDL defines the normative canonical manifest schema:

```cddl
logos.package_manifest.package_name = tstr .size (1..128)
logos.package_manifest.package_version = tstr .size (1..128)
logos.package_manifest.package_variant_id = tstr .size (1..128)
logos.package_manifest.artifact_id = tstr .size (1..128)

logos.package_manifest.manifest = {
  package: logos.package_manifest.package_name,
  version: logos.package_manifest.package_version,
  modules: [* logos.package_manifest.module_declaration],
  variants: [* logos.package_manifest.package_variant],
  ? dependencies: [* logos.package_manifest.package_dependency],
}

logos.package_manifest.module_declaration = {
  module: tstr .size (1..64),
  artifact: logos.package_manifest.artifact_id,
  ? primary_contract: logos.schema_commitment,
  ? implements: [* logos.schema_commitment],
  ? requires: [* logos.package_manifest.provider_requirement],
  ? requested_permissions: [* logos.package_manifest.requested_permission],
  ? configuration: logos.package_manifest.configuration_declaration,
}

logos.package_manifest.configuration_declaration = {
  schema_artifact: logos.package_manifest.artifact_id,
  root: tstr .size (1..255),
  schema_commitment: logos.schema_commitment,
  ? default_artifact: logos.package_manifest.artifact_id,
  ? live_reconfiguration: true,
}

logos.package_manifest.provider_requirement = {
  contract: logos.schema_commitment,
  cardinality: "single" / "all-runtime-visible",
}

logos.package_manifest.requested_permission = {
  permission: tstr .size (1..128),
  constraints: bstr .size (1..1048576),
  ? reason: tstr .size (1..512),
}

logos.package_manifest.package_dependency = {
  package: logos.package_manifest.package_name,
  requirement: logos.package_manifest.package_version_requirement,
}

logos.package_manifest.package_version_requirement = {
  kind: "exact" / "compatible",
  version: logos.package_manifest.package_version,
}

logos.package_manifest.package_variant = {
  id: logos.package_manifest.package_variant_id,
  platform: logos.package_manifest.platform_constraint,
  artifacts: [* logos.package_manifest.manifest_artifact],
}

logos.package_manifest.platform_constraint = {
  ? os: tstr .size (1..64),
  ? architecture: tstr .size (1..64),
  ? abi: tstr .size (1..64),
}

logos.package_manifest.manifest_artifact = {
  id: logos.package_manifest.artifact_id,
  kind: "module-binary" / "resource" / "schema" / "data",
  path: tstr .size (1..4096),
  hash: bstr .size 32,
}
```

`logos_package_manifest.cddl` is an extracted machine-readable mirror of this block.
If the extracted artifact differs from this specification,
this specification governs.

`configuration`, when present, declares one configuration schema for the module.
`schema_artifact` identifies a `schema` artifact containing the UTF-8 CDDL document, and `root` names the configuration root in that document.
`schema_commitment` binds the complete schema document.
Package Manager derives the selected root's schema subtree root when it constructs the configuration-owned Runtime handoff defined by LOGOS-MODULE-CONFIGURATION.

`default_artifact`, when present, identifies a `data` artifact containing the exact deterministic-CBOR bytes of one complete default value.
The schema and default artifacts MUST exist in every package variant in which the module's implementation artifact exists.
Different module declarations MAY reference the same schema or default artifact.

`live_reconfiguration` is present only when the module declares support for the live-reconfiguration behavior defined by LOGOS-MODULE-CONFIGURATION.
It does not grant configuration or lifecycle authority.

A schema commitment identifies one exact module or interface contract by schema root.
The schema root already commits to the contract namespace.
Package release versions do not form part of contract identity.

Within one module declaration, implemented contract commitments, required contract commitments, and requested permission names MUST each be unique.
The implementation artifact referenced by each module declaration MUST occur in at least one package variant
and MUST have kind `module-binary` wherever it occurs.
The `constraints` field contains the exact deterministic-CBOR encoding of one value owned by the named permission definition.

Variant order is significant because it determines platform selection.
All other manifest arrays use canonical order:

- module declarations by `module` UTF-8 bytes;
- artifacts within each variant by `id` UTF-8 bytes;
- dependencies by `package` UTF-8 bytes;
- implemented contracts and provider requirements by the deterministic-CBOR bytes of their schema commitment; and
- requested permissions by `permission` UTF-8 bytes.

Package Manager MUST reject a manifest whose arrays violate these ordering or uniqueness rules.

Package Manager MUST verify each referenced artifact against its signed manifest hash before parsing or validating its content.
A missing artifact, incorrect artifact kind, or hash mismatch MUST fail with `artifact-integrity-failed`.
Invalid CDDL, a document schema-commitment mismatch, an absent or invalid root, an unresolved non-common schema reference, or an invalid default value MUST fail with `invalid-package`.

Under the fixed commitment and hash identifiers,
the assigned schema root is `108b1bab1bf87dfed2ca431bf0591e33e937bb553a489df46b0a9023b9a98af1`,
and the `logos.package_manifest.manifest` subtree root is
`a06c0c06d9493e19ab96baabd23b6520645195188af062f858f95f6922a128a1`.
These hexadecimal values decode to 32-byte roots and are normative.

When a manifest value commitment is required, the value commitment MUST bind
the decoded deterministic CBOR value to:

- the semantic commitment-model revision identifier;
- the schema root for `logos.package_manifest`;
- the schema subtree root for `logos.package_manifest.manifest`;
- the normalized Logos value model for the manifest value.

`manifest.cose` is a security container for a signed package claim.
It is not a CDDL schema and does not replace `manifest.cbor`.
The signed claim MUST bind the exact manifest value commitment,
including its commitment-model revision, schema roots, value root, hash profile, and hash suite.
Because the committed manifest contains every variant's artifact identifiers and hashes,
the signature transitively binds those declared artifact hashes.
Package Manager MUST still hash the selected materialized artifact bytes
and compare them with the signed manifest before use.

The selected package-signing profile defines the concrete security container,
signer and trust-anchor identification, algorithms, key requirements, and verification procedure.
Package Manager MUST reject a package when the signature is missing,
the signer is not accepted by active trust policy,
the signature is invalid,
or the signed commitment does not equal the commitment computed from `manifest.cbor`.
Catalog entries, Storage metadata, Nix metadata, archive names, and diagnostic JSON
MUST NOT override the signed manifest claim.

### 4.1 Package-Signing Trust

The active package-signing profile consumes protected trust input
supplied by the runtime host or deployment environment.
That input MUST bind each accepted trust-anchor identifier
to its public key or other profile-defined verification material.
It MUST also bind each accepted signer to a non-empty set of exact package names for which that signer is authorized.
Package-name authorization uses byte-for-byte equality of the package-name UTF-8 encoding.
It MUST NOT use case folding, Unicode normalization, prefixes, wildcard patterns, or an authorization covering every package name.
A bare identifier, package field, catalog entry, or downloaded key does not establish a trust anchor.
The concrete key encoding, signature algorithms, and signature-container processing
are defined by the selected package-signing profile.

Package Manager MUST verify each package against the currently accepted package-signing trust anchors
and require the authenticated signer to be authorized for the exact package name in the signed manifest.
If no accepted anchor validates the signer and signature,
or if that signer is not authorized for the exact package name,
Package Manager MUST reject the package with `signature-verification-failed`.
Package Manager MAY cache successful signature verification.
It MUST invalidate an affected cache entry when the corresponding signature profile,
trust anchor, signer, or exact-name authorization is no longer accepted.

One signer MAY be authorized for multiple exact package names,
and multiple signers MAY be authorized for the same exact package name.
Trust-anchor or signer rotation MAY accept old and new identities for that exact package name during a configured overlap period.
After an anchor is removed or revoked,
Package Manager MUST NOT use it for a new successful resolution, installation, update, or Runtime handoff.
Whether an already-running module is stopped is a separate Runtime and active-authority decision.

Package catalogs locate candidate package material.
Catalog trust MAY authenticate catalog claims,
but it MUST NOT replace verification of the package's own signature and artifact hashes.
Package material, catalog metadata, Storage content, and Nix metadata MUST NOT add,
replace, or reactivate a package-signing trust anchor.

Package-signing trust, remote Runtime enrollment trust,
and Capability Authority execution authorization are distinct decisions.
Configuring the same key material for more than one purpose does not merge those decisions.
A local development deployment MAY configure its own package-signing trust anchor
through the same protected trust-input path.

### 4.2 Catalog, External Anchoring, And Freshness

Protected package-signing trust input and verification of each package signature
are the mandatory baseline trust mechanism.
The baseline does not require an online catalog, transparency log, consensus system,
or other network trust service.

A selected package-signing or catalog profile MAY additionally require
transparency-log inclusion, a consensus checkpoint, or equivalent external anchoring.
The profile MUST identify the accepted external trust root and verification rules
through protected trust input.
An address, log name, catalog field, downloaded key, or package-supplied checkpoint
MUST NOT establish that trust.

Verified external anchoring can show that an exact signed manifest commitment
was included, ordered, or finalized under the selected mechanism.
It does not by itself authorize the signer, make the package safe,
approve its requested permissions, or authorize installation or execution.
Catalog and external-anchor evidence MUST remain bound to the exact package signature
and manifest commitment to which it applies.

A valid package signature authenticates one immutable manifest claim.
It does not prove that the package is the newest release,
that it remains unrevoked, or that its version remains acceptable.
When active package-signing trust input requires revocation, a minimum accepted version,
or fresh external-anchor evidence,
Package Manager MUST enforce that requirement before a successful resolution, installation, update, or Runtime handoff.
The selected profile MUST define any version comparison, trusted checkpoint,
maximum evidence age, and rollback-detection rule it requires.

Package Manager MUST retain the trusted state needed to reject an older signer state,
checkpoint, or package state after accepting a newer one under such a profile.
After loss of that state, it MUST re-establish freshness from protected trust input
or fail operations that require freshness.
Failure to obtain fresh optional catalog data does not invalidate immutable installed bytes by itself,
but Package Manager MUST NOT produce a result or handoff whose active trust requirements it cannot verify.

### 4.3 Baseline Package-Signature Profile

Every conforming Package Manager MUST implement
`logos.package-signing.cose-sign1-ed25519`.
This profile uses tagged `COSE_Sign1` from RFC 9052
with the fully specified `Ed25519` COSE algorithm from RFC 9864.
It does not use the polymorphic `EdDSA` algorithm identifier.

The signed payload is this deterministic-CBOR claim:

```cddl
logos.package_manager.package_signing_profile =
  "logos.package-signing.cose-sign1-ed25519"

logos.package_manager.package_signing_key_id = bstr .size (1..128)

logos.package_manager.package_signature_claim = {
  profile: logos.package_manager.package_signing_profile,
  manifest_commitment: logos.package_manager.manifest_commitment,
}
```

`manifest.cose` MUST be one tagged `COSE_Sign1` object using CBOR tag 18.
The protected header map MUST contain exactly:

- `alg` with COSE label `1` and value `-19` for `Ed25519`;
- `kid` with COSE label `4` and a `logos.package_manager.package_signing_key_id` value.

The unprotected header map MUST be empty.
The outer `COSE_Sign1` object and serialized protected header map
MUST use the core deterministic encoding requirements of RFC 8949 Section 4.2.1.
The payload MUST be present as a byte string
containing the Logos deterministic-CBOR encoding of `logos.package_manager.package_signature_claim`.
Detached payloads, additional protected or unprotected headers,
multiple signatures, countersignatures, and critical-header extensions are not accepted by this profile.

The `Sig_structure` is the RFC 9052 `Signature1` structure
with the protected header bytes from the object,
a zero-length `external_aad`, and the exact embedded payload bytes.
This profile defines no nonce and no external signing context.
The profile identifier inside the signed payload provides application-level domain separation
without defining a private COSE header parameter or media type.

Protected package-signing trust input MUST map each accepted `kid`
to exactly one 32-byte Ed25519 public key encoded according to RFC 8032.
Two accepted trust anchors MUST NOT use the same `kid`.
The `kid` selects candidate verification material;
it does not establish trust without that protected mapping.
For this profile, the authenticated `kid` identifies the signer whose exact-name authorization is required by Section 4.1.
The signing private key is not package content or a Package Manager input.
Package producers MUST generate the 32-byte Ed25519 private seed with a cryptographically secure random generator
and MUST protect it against disclosure and unauthorized signing.
Its storage encoding is package-producer configuration outside this specification.

An Ed25519 signature is exactly 64 bytes.
Package Manager MUST reject an object with a malformed tag or structure,
non-deterministic CBOR, a missing or detached payload,
an unknown or duplicate `kid`, any header not permitted above,
an algorithm other than `-19`, an invalid public-key or signature length,
or a failed signature verification.
It MUST then decode the signed claim,
require the exact profile identifier,
recompute `manifest_commitment` from `manifest.cbor`,
and require every commitment field to match the signed value.
Any failure produces `signature-verification-failed`
and MUST occur before artifact material is accepted or a Runtime handoff is produced.

This signature profile contains no signing time, expiry, or validity interval.
Clock-skew processing therefore does not apply.
Signer revocation, trust-anchor rotation, minimum accepted versions,
and optional external freshness evidence use the active trust rules in Sections 4.1 and 4.2.
An implementation MUST NOT infer freshness from successful signature verification alone.

### 4.4 Artifact And Catalog Signature Boundaries

The baseline defines no separate signature container for each package artifact.
The package signature authenticates the complete manifest commitment,
and the committed manifest binds every field of every variant's artifact record.
Package Manager then verifies the exact materialized bytes against the signed hash.
This signature-to-manifest-to-bytes chain is the baseline artifact-authentication mechanism.
A detached artifact signature MUST NOT substitute for any step in that chain.

Catalog records are discovery and presentation inputs,
not package signatures or security containers.
The baseline therefore does not require a COSE signature over each catalog entry or catalog response.
A catalog-supplied manifest or commitment is not trusted package material
until Package Manager obtains the package's own signature and completes the verification in Sections 4.1 through 4.3.
Catalog metadata MUST NOT establish signer trust, artifact integrity, package freshness,
installation authority, or execution authority.

A deployment that requires authenticated catalog ordering, freshness, or external anchoring
must select a catalog profile satisfying Section 4.2.
That additional profile does not replace the baseline package signature,
materialized-byte verification, or Runtime's load-boundary digest check.

### 4.5 Optional Package-Provenance Enforcement

The baseline package signature and artifact checks do not establish how package artifacts were built.
This specification defines `logos.package-provenance.slsa-v1.2`,
an optional package-provenance profile based on [SLSA v1.2].
A Package Manager MAY implement this profile.

For an LGX source accepted under this profile, `provenance_object` MUST be present.
Package Manager MUST retrieve the identified object from the Logos Storage provider named by `storage`
and MUST use that detached object as the profile's provenance evidence.
It MUST NOT use an attestation embedded in the LGX archive to satisfy this profile.
An absent locator, an unavailable object, a retrieval failure, or an object that does not satisfy every profile requirement
MUST cause rejection without baseline-only fallback.

The provenance object for this profile MUST be a standard DSSE v1 JSON envelope [DSSE v1]
whose `payloadType` is exactly `application/vnd.in-toto+json`.
Its decoded `payload` MUST be one UTF-8 JSON in-toto Statement [in-toto Attestation v1]
whose `_type` is exactly `https://in-toto.io/Statement/v1`,
whose `predicateType` is exactly `https://slsa.dev/provenance/v1`,
and whose predicate conforms to SLSA Build Provenance v1 [SLSA v1.2].

The envelope and decoded Statement MUST each be valid UTF-8 JSON containing exactly one value,
contain no duplicate object member names, and have no trailing data.
The `payload` and every `sig` value MUST use a base64 form permitted by DSSE v1,
the `signatures` array MUST be nonempty,
and every decoded `sig` value MUST be nonempty.
Package Manager MUST apply the DSSE and in-toto rules for unrecognized fields.

Package Manager MUST verify each signature over the DSSE pre-authentication encoding of the exact `payloadType` and decoded `payload` bytes.
It MUST parse and evaluate the same payload bytes whose signature it verified.
It MUST NOT normalize, reserialize, translate, or substitute the payload before signature verification.
This profile uses native DSSE and in-toto evidence so Package Manager can verify producer attestations without translation.
A translated or re-encoded representation does not retain the DSSE authentication and MUST NOT satisfy this profile.
Another envelope or encoding requires a distinct package-provenance profile.

Protected provenance trust input MUST bind each accepted provenance signer identity to a nonempty set of exact builder identifiers.
Protected deployment policy MUST select every accepted provenance-signing profile.
Each provenance-signing profile MUST define its signature algorithms, authenticated signer-identity construction,
certificate or key requirements, revocation processing, and any required transparency verification.
The envelope, Statement, `keyid`, builder, package, source, catalog, or caller MUST NOT select or weaken a provenance-signing profile.

DSSE `keyid` is an unauthenticated key-selection hint and MUST NOT establish signer identity or trust.
Package Manager MUST evaluate each signature independently.
The signature boundary succeeds only when at least one signature verifies under an accepted provenance-signing profile
and its authenticated signer identity is authorized for the Statement's exact `builder.id`.
An additional invalid or unaccepted signature neither grants trust nor invalidates an otherwise accepted signer-builder pair.
Builder-identifier comparison is case-sensitive exact string equality.
A prefix, wildcard, redirect, case folding, Unicode normalization, or URI normalization MUST NOT establish equality.
Failure to obtain an accepted signer-builder pair MUST cause package rejection without baseline-only fallback.

For this profile, at least one entry in the Statement's `subject` array MUST identify the complete gzip-compressed LGX archive bytes obtained from the package source.
That entry's `digest` map MUST contain a `sha256` entry equal to SHA-256 [RFC 6234] over those exact bytes.
Package Manager MUST determine this subject match only from that `sha256` entry.
Subject `name`, `uri`, and digest entries using other algorithms MUST NOT establish the match.
Additional conforming subject entries are permitted and MUST NOT prevent a match established by any entry's required `sha256` digest.
Package Manager MUST compute that digest before decompression, extraction, normalization, or any other transformation.
The digest identifies one distributed LGX object;
it is not the package identity or manifest identity.
A manifest commitment, decompressed-archive digest, artifact digest, or module-binary digest MUST NOT substitute for the exact LGX digest.

Conforming LGX writers may produce different DEFLATE bitstreams for the same archive content.
A recompressed LGX is therefore a different SLSA subject even when its manifest and artifacts are unchanged.
Provenance naming the digest of one LGX object MUST NOT authorize another LGX object.
This profile requires no additional whole-LGX digest;
the existing Logos BLAKE3 manifest commitments and artifact hashes remain independently mandatory.

Build provenance for this profile MUST bind the LGX subject to the package source.
Protected deployment policy MUST associate each exact package name with a nonempty set of accepted `buildType` definitions.
Each accepted `buildType` definition MUST bind one exact `buildType` identifier to the external parameter that supplies the package source.
It MUST define a deterministic mapping from that parameter to exactly one `resolvedDependencies` resource descriptor.
The provenance predicate's `buildDefinition.buildType` value MUST equal the identifier of one definition associated with the exact package name in the signed manifest.
Matching MUST use case-sensitive exact string equality.
A prefix, wildcard, redirect, case folding, Unicode normalization, or URI normalization MUST NOT establish equality.
Only protected deployment policy may supply or select an accepted `buildType` definition and its mapping.
The provenance object, Statement, package, manifest, catalog, source, and caller MUST NOT do so.
Package Manager MUST apply the associated definition's mapping.
It MUST reject provenance when the mapping selects no descriptor or more than one descriptor.
An otherwise accepted repository appearing only as another resolved dependency does not satisfy source binding.

Protected deployment policy MUST associate each exact package name with a nonempty set of accepted source repository identifiers and accepted immutable source-identity rules.
The selected source descriptor's `uri` MUST equal one of those identifiers as an exact case-sensitive string.
A redirect, repository mirror, alternate transport URI, case folding, Unicode normalization, or other alias does not establish equality unless protected policy lists that exact identifier separately.

The selected source descriptor's `digest` MUST contain at least one entry that protected policy recognizes as either a complete immutable source revision identifier or a source-tree digest.
For Git, a `gitCommit` value MUST be the complete Git object identifier;
an abbreviated object name does not satisfy this profile.
A source-tree digest is accepted only when protected policy or a selected source-evidence profile defines its algorithm and canonical tree construction.
A mutable branch or tag name MAY be retained as diagnostic information but MUST NOT substitute for an accepted immutable source identity.

The exact source repository identifier and immutable source identity form the binding for additional source evidence.
This profile does not require a source-evidence format.
An additional protected source-evidence profile MAY require a Git commit signature,
a SLSA Source Verification Summary Attestation [SLSA Source v1.2], or other independently authenticated evidence.
Such a profile MUST bind the evidence to exactly the same source repository identifier and immutable source identity,
verify it under trust rules distinct from build-provenance and package-signing trust,
and fail closed when required evidence is absent or invalid.
Source evidence MUST NOT replace build provenance or the package signature.
The source-evidence signer or issuer, build-provenance signer, builder identity, and package signer are distinct identities,
even when protected policy authorizes the same credential for more than one role.

Source binding establishes only what source the accepted provenance claims the builder used.
It does not prove source safety, prove compliance with a source-control process without independently verified source evidence,
or protect against a malicious or compromised accepted build platform.

Only protected deployment policy may select an active package-provenance profile.
A manifest, package sidecar, catalog, Storage object, Nix metadata, provenance object, or caller MUST NOT select, disable, or weaken that profile.

When no package-provenance profile is selected,
Package Manager applies the mandatory package-signature and artifact-verification baseline
and MUST NOT claim that package provenance was verified.
When protected deployment policy selects a package-provenance profile,
Package Manager MUST enforce every requirement of that profile before a successful inspection, resolution, installation, update, or Runtime handoff.
An implementation that does not support the selected profile MUST reject the protected policy configuration before accepting package material under it.

Missing, malformed, untrusted, stale, revoked, or otherwise non-qualifying provenance evidence
MUST NOT cause fallback to baseline-only acceptance while a package-provenance profile remains selected.
Successful provenance verification does not replace the baseline package signature,
artifact-hash verification, signer authorization, or Runtime's load-boundary digest check.

## 5. Package Records

The package manifest is the small author-facing Logos package object.
It is independent of the realization profile used to materialize local artifacts.
The normative signed-manifest schema is defined in Section 4.
Package Manager records reference that canonical schema directly.

```cddl
logos.package_manager.package_identity = {
  package: logos.package_manifest.package_name,
  version: logos.package_manifest.package_version,
}
```

The `variants` array MUST be non-empty.
Each variant's `artifacts` array MUST be non-empty.

`package_version` values MUST be Semantic Versioning 2.0.0 strings.
They MUST NOT include a leading `v` or build metadata.
Pre-release versions are allowed and use SemVer precedence.
Package identity uses the complete version text,
while version selection uses SemVer precedence.

The expanded installed package record is Package Manager output.
It is derived from a manifest, a source record, the realization backend, and the
local install state.

```cddl
logos.package_manager.installed_package_record = {
  identity: logos.package_manager.package_identity,
  source: logos.package_manager.package_source,
  variant: logos.package_manifest.package_variant_id,
  manifest_commitment: logos.package_manager.manifest_commitment,
  modules: [* logos.package_manifest.module_declaration],
  artifacts: [* logos.package_manager.installed_artifact],
  resolved_dependencies: [* logos.package_manager.resolved_package_dependency],
}

logos.package_manager.package_source =
  {
    kind: "lgx",
    storage: tstr .size (1..128),
    object: bstr .size (1..4096),
    ? provenance_object: bstr .size (1..4096),
  } /
  {
    kind: "nix",
    flake_ref: tstr .size (1..4096),
    ? attr: tstr .size (1..255),
    ? locked_ref: tstr .size (1..4096),
  }

logos.package_manager.manifest_commitment = {
  commitment_model: "logos.commitment-model.2026-08",
  schema_root: bstr .size 32,
  schema_subtree_root: bstr .size 32,
  value_root: bstr .size 32,
  hash_profile: "logos.hash-profile.2026-08.choice-index",
  hash_suite: "logos.hash-suite.blake3-256",
}

```

The `modules` array contains only module declarations whose implementation artifact occurs in the selected variant,
in manifest declaration order.
It MUST NOT contain a module declaration whose implementation artifact is absent from the selected variant.

The source record gives Package Manager enough information to locate or realize
the package.
It does not expose backend evaluation as a Logos module API.
An installed record is installed by definition.
Package Manager MUST retain the selected artifact bytes while their installed record remains present.
For one package identity, the installed set MUST NOT contain records with different manifest commitments.

## 6. Catalog And Source Records

Catalog records expose package availability in Logos terms.
They do not expose the backend dependency graph or package-manager internals.

```cddl
logos.package_manager.package_catalog_entry = {
  identity: logos.package_manager.package_identity,
  source: logos.package_manager.package_source,
}

logos.package_manager.package_inspect_record = {
  source: logos.package_manager.package_source,
  manifest: logos.package_manifest.manifest,
  manifest_commitment: logos.package_manager.manifest_commitment,
}
```

An LGX source's `storage` and `object` fields identify the Storage object containing the package archive.
Its optional `provenance_object` field identifies one detached package-provenance object in the same Logos Storage provider.
When present, `provenance_object` MUST differ from `object`.
The field is untrusted location data only;
its presence neither selects a package-provenance profile nor establishes that provenance was verified.
A Nix source identifies the input consumed by the Nix realization profile.
When `locked_ref` is present,
it identifies the concrete locked input selected from `flake_ref`.
Every catalog identity contains an exact package version.
Catalog entries contain location data only;
they do not carry another manifest or trusted package metadata projection.

An inspection record is returned only after the manifest, signature, and commitment have been verified.
Its commitment MUST correspond to its manifest value under the `logos.package_manifest` schema.

## 7. Realization Profiles

A conforming Package Manager implementation MUST support at least one realization profile defined by this specification.
An implementation may conform through LGX only, Nix only, or both profiles.

The package source kind selects the realization profile and changes how package material is obtained and materialized.
It does not change manifest semantics, installed package records, dependency declarations,
requested permissions, or Runtime handoffs.
If a request selects a source kind whose profile is not implemented,
the implementation MUST return `unsupported-source`.

### 7.1 LGX Profile

The LGX profile installs prebuilt package material and MUST NOT build source code or run package-provided installation scripts.

An LGX package is a gzip-compressed USTAR archive with the following structure:

```text
package.lgx
├── manifest.cbor
├── manifest.cose
├── manifest.json          optional diagnostic rendering
└── variants/
    └── <variant-id>/
        └── <artifact files>
```

Only `manifest.cbor`, `manifest.cose`, `manifest.json`, and `variants/` may appear at the archive root.
The `variants/` directory MUST contain exactly one directory for each manifest variant.
It MUST NOT contain files directly.
Each variant directory name MUST equal the corresponding manifest `id`.
Variant ids MUST be lowercase ASCII strings containing only letters, digits, `.`, `_`, and `-`.
Each variant id MUST form one non-empty path segment.

Archive paths MUST be relative, UTF-8, and Unicode NFC-normalized.
They MUST NOT contain an empty segment, a `.` or `..` segment, a backslash, or a NUL byte.
The archive MUST NOT contain duplicate normalized paths, symbolic links, or hard links.
It MUST NOT contain device nodes, FIFOs, or other special files.
Package Manager MUST reject a selected variant whose paths collide under the selected platform's path-comparison rules.
Before writing an extracted entry,
Package Manager MUST verify that its resolved destination remains within the selected installation root.

LGX writers MUST order entries lexicographically by normalized path bytes.
USTAR user and group identifiers and modification times MUST be zero.
User and group names MUST be empty.
Directory modes MUST be `0755`, and regular-file modes MUST be `0644`.
Gzip headers MUST omit the original filename, use modification time zero, and use operating-system byte `255`.
The compressed DEFLATE bitstream is not package identity and may differ between conforming writers.

Package Manager MUST bound compressed input size, decompressed size, archive entry count,
individual entry size, and extracted output size before processing untrusted LGX input.
The deployment profile defines the concrete limits.
Package Manager MUST reject an archive before installation when any limit is exceeded.

An absent platform field imposes no constraint for that field.
A present platform field MUST match the corresponding value supplied by the selected platform profile.
Package Manager evaluates manifest variants in their declared order.
It selects the first variant compatible with the local platform and selected runtime profile.
It MUST return `incompatible-platform` when no variant is compatible.
The selected variant id is recorded in the installed package record.

Artifact paths are relative to the selected variant directory.
Every regular file in a variant directory MUST be declared by exactly one artifact record in that variant.
Every declared artifact path MUST identify one regular file.
A module declaration whose implementation artifact occurs in the selected variant is a selected module declaration.
Every artifact referenced by a selected module declaration MUST occur exactly once in the selected variant.
A module declaration whose implementation artifact is absent from the selected variant is not selected.
Package Manager MUST omit it from the installed package record
and MUST NOT produce a Runtime handoff for it.
Package Manager MUST verify required artifact hashes before exposing or installing the package.
It MUST extract selected artifacts into a Package Manager or deployment-controlled location
before Runtime or Module Loader uses them.
Runtime and Module Loader MUST NOT execute code directly from an LGX archive or remote Storage object.

### 7.2 Profile Equivalence

LGX and Nix are peer realization profiles.
An implementation conforming through either profile MUST satisfy the same manifest, validation,
installed-record, and handoff requirements.

### 7.3 Nix Profile

A Nix source uses `source.kind` equal to `"nix"`.
`flake_ref` identifies the flake to realize.
`attr` selects the package output when the flake exposes more than one.
`locked_ref` records the concrete locked flake input when one is available.
Package Manager MUST resolve `attr` using the Nix flake output rules for the selected target system.
When `attr` is absent, it MUST select the flake's default package output for that system.

The selected flake output MUST represent exactly one Logos package.
A flake MAY expose more than one package output,
but Package Manager realizes one selected output for each package operation.
Before installation, Package Manager MUST resolve the source to an immutable realized output.
The installed package source MUST record `locked_ref`
unless `flake_ref` already identifies an immutable realized output.

For this profile, package-controlled Nix work means evaluating the selected flake or an input it controls,
or executing a builder, hook, or evaluation-triggered derivation selected or influenced by that material,
before Package Manager has accepted the embedded package signature.

Package Manager MAY obtain the exact immutable realized output without a pre-verification isolation boundary
only when protected deployment input selects that exact output and obtaining it performs no package-controlled Nix work.
A substituter configuration, cache hit, locked flake input, or immutable flake reference does not by itself establish this condition.

When obtaining the output requires package-controlled Nix work,
Package Manager MUST establish a deployment-defined pre-verification isolation boundary before any such work begins.
The boundary MUST contain the evaluator, every induced builder or hook,
and every Nix service or store operation influenced by the unaccepted material.
Protected deployment input MUST define and enforce the boundary's filesystem, process, network, credential, IPC,
CPU, memory, storage, and time access.
The work MUST NOT read or modify package-signing or provenance trust input,
Package Manager installed state, deployment credentials, Runtime, Capability Authority, or Module Loader control surfaces,
or other protected host state.
It MUST NOT modify state outside its isolated store and disposable working state.
Only an immutable realized output and bounded non-sensitive diagnostics may leave the boundary.

Package Manager MUST treat the realized output as untrusted candidate material.
It MUST verify the package signature, manifest, selected variant, and artifact hashes
before reporting successful inspection, resolution, installation, update, or Runtime handoff.
Nix store-object authentication may support protected output selection,
but it does not verify the Logos package signature or make the output accepted package material.

If no protected pre-resolved output is available and the required isolation boundary cannot be established,
Package Manager MUST return `package-unavailable` before starting package-controlled Nix work.
It MUST NOT fall back to unconfined local or remote evaluation or building.

The realized output MUST contain the canonical manifest at:

```text
share/logos/package.cbor
```

It MUST contain the corresponding package-signature container at:

```text
share/logos/package.cose
```

The decoded manifest MUST validate as `logos.package_manifest.manifest`.
The manifest is the authoritative source for package identity, module
declarations, contracts, variants, artifacts, dependencies, requested
permissions, and handoff derivation.
Flake attributes and Nix package metadata MUST NOT define a second Logos package manifest.
They MUST NOT override the embedded manifest.

Manifest artifact paths are relative to the realized output.
Package Manager MUST select a compatible manifest variant and verify its declared artifacts.
It MUST produce the same installed package and Runtime handoff records required by the LGX profile.

Nix evaluation, dependency closures, builders, substituters, store layout,
profiles, generations, and garbage collection are backend internals.
They MUST NOT appear in ordinary Package Manager results.
Their status as backend internals does not weaken the pre-verification requirements above.

Package Manager MUST NOT install packages into the user's ordinary Nix profile.
It MUST maintain the roots or equivalent reachability needed to keep installed artifacts available
while their installed package records remain active.
It MAY use an existing Nix installation or a deployment-provided compatible service.
A conforming host need not run NixOS.

The Nix profile and LGX profile may coexist in one implementation.
A package produced with Nix but distributed and installed as an LGX archive uses the LGX profile.

## 8. Validation Rules

Package Manager MUST validate package material before exposing it as installable
or installed.

A package MUST be rejected with `invalid-package` when the required canonical manifest is absent.

A package MUST be rejected with `invalid-package` when the manifest:

- is not Logos deterministic CBOR;
- does not validate against `logos.package_manifest.manifest`;
- declares a package name or version that conflicts with the selected package
  reference;
- declares a package version or dependency requirement version that is not a
  permitted `package_version`;
- declares duplicate variant ids;
- declares duplicate artifact ids within a variant;
- references a module implementation artifact that is absent from every manifest variant;
- references a schema or default artifact that is not present exactly once in every manifest variant containing the referencing module's implementation artifact;
- declares duplicate package dependency names;
- declares duplicate module identities;
- assigns one artifact to more than one module declaration;
- contains an invalid schema commitment record.

An LGX package MUST be rejected with `invalid-package`
when its archive structure, entry types, paths, or encoding do not satisfy Section 7.1.

A package MUST be rejected with `incompatible-platform` when its platform or ABI
constraints exclude the local host or selected runtime profile.

A package MUST be rejected with `package-unavailable` when the selected profile cannot materialize the selected package.

A package MUST be rejected with `artifact-integrity-failed` when:

- a required artifact is missing from the selected variant or realized output;
- a manifest artifact path escapes its selected variant or realized output;
- an artifact omits its required hash;
- an artifact hash does not match the materialized artifact.

A package MUST be rejected with `signature-verification-failed` when its required signature is missing,
invalid, rooted in an unaccepted signer or trust anchor,
or bound to a manifest commitment other than the commitment computed from its canonical manifest.

Manifest artifact paths MUST be relative paths.
They MUST NOT be absolute paths.
They MUST NOT contain parent-directory traversal.
They MUST NOT identify remote resources.

Diagnostic JSON renderings MUST NOT be used to override the canonical CBOR
manifest.

## 9. Module Declarations

A package manifest declares zero or more canonical `logos.package_manifest.module_declaration` values.

The `module` field is the flat runtime module name used by
LOGOS-MODULE-RUNTIME.
It identifies the module independently of any contract.
`artifact` identifies the one selected realization artifact for that packaged module.
Two module declarations in one manifest MUST NOT identify the same module or artifact.

`primary_contract`, when present, identifies the module's primary concrete contract.
`implements` lists exact implemented interface contracts.
A module declaration may omit `primary_contract`, `implements`, or both.
A module with neither field declares no contract and requires no
provider behavior merely because it is a module.
A module may implement interface contracts without declaring a primary concrete contract.
When `implements` is present, its schema commitments MUST be unique.

`requires` declares provider requirements for the module.
`requested_permissions` declares permissions requested for that module.
Neither field grants authority or creates a route.
The `implements`, `requires`, and `requested_permissions` arrays MUST be non-empty when present.

`configuration` is the signed package declaration from which Package Manager constructs Runtime configuration input.
It preserves the schema and default artifact identifiers, root, schema commitment, and live-reconfiguration declaration until that construction.

Schema commitments and provider requirements use their canonical Package Manifest shapes.
Runtime, Interface, Transport, Commitment Model, and Hash Profile do not depend on Package Manager to define them.
If `primary_contract` is present and Package Manager can compute or obtain that
contract's schema identity,
Package Manager MUST reject any `implements` entry that is not committed by that concrete contract.
If Package Manager cannot validate the declared contract metadata during
inspection, Runtime still MUST validate selected providers before exposing
ready invocation paths.

The schema commitments in a module declaration are exact signed expectations.
They do not contain the CDDL schema documents or deterministic provider
call-surface descriptor defined by LOGOS-MODULE-INTERFACE.
A package may carry declared schema artifacts as ordinary hashed package
material, but Package Manager MUST NOT treat a schema commitment or schema
artifact as proof that the selected executable exposes that call surface.

## 10. Artifact Records

Manifest artifact records describe author-declared artifact references.
Installed artifact records describe local or source-addressed package outputs in
Logos terms.

```cddl
logos.package_manager.installed_artifact = {
  id: logos.package_manifest.artifact_id,
  kind: "module-binary" / "resource" / "schema" / "data",
  local_path: tstr .size (1..4096),
  hash: bstr .size 32,
}
```

For the LGX profile, manifest artifact paths are relative to the corresponding variant directory.
For the Nix profile, manifest artifact paths are relative to the realized output.
The hash suite named by the manifest commitment defines the artifact-digest algorithm and digest length.
The artifact hash is that hash suite applied to the artifact's exact file bytes.
It is not a schema or value root produced by the Logos Hash Profile.

An artifact id identifies the same logical artifact role across variants.
It may occur once in each variant, with a different path and hash for that variant.
Module scope is variant-specific and is determined by the presence of the module's implementation artifact.
The installed artifact list contains only artifacts from the selected variant.
Platform profiles define the registered `os`, `architecture`, and `abi` values and their matching rules.
Variant ids do not define platform compatibility.

`local_path` is the resolved local artifact location produced by Package Manager.
Runtime and Module Loader consume resolved local artifacts.
They MUST NOT execute code directly from a remote Storage object.
Package Manager MUST keep each installed path bound to the verified bytes while the installed record remains present.

## 11. Dependencies And Requested Permissions

Package dependencies are Logos-level declarations.
They are independent of build-time dependency metadata and backend-internal dependency closures.

```cddl
logos.package_manager.resolved_package_dependency = {
  identity: logos.package_manager.package_identity,
  manifest_commitment: logos.package_manager.manifest_commitment,
}
```

The `dependencies` array MUST be non-empty when present.
Dependency package names MUST be unique within one manifest.
Each dependency identifies one package name and one structured version requirement.

An `exact` requirement is satisfied only by identical package-version text.
A `compatible` requirement names a normal-release minimum version and is
satisfied by a normal release at or above that minimum
without changing the left-most non-zero version component.
For example, `1.2.3` accepts versions from `1.2.3` up to but excluding `2.0.0`,
`0.2.3` accepts versions up to but excluding `0.3.0`,
and `0.0.3` accepts only `0.0.3`.
The `0.0.0` minimum accepts only `0.0.0`.
A `compatible` requirement MUST NOT contain a pre-release version.
An `exact` requirement may select a pre-release version.

Protected deployment policy MUST supply a resolver-limit set containing positive integer limits for:

- distinct package names in one partial closure;
- dependency depth;
- candidate records considered for one package name; and
- candidate-assignment attempts in one root operation.

A deployment may provision those values as one preset or policy bundle.
The resolved values are protected policy input,
not another named Core profile.
Package Manager MUST reject a protected policy configuration that omits a limit or supplies a non-positive value.
A package, manifest, catalog, source, or caller MUST NOT select, raise, or disable a resolver limit.

The root package counts toward the partial-closure limit and has dependency depth zero.
Dependency depth is the number of manifest dependency edges from the root.
Before adding a package name to a partial closure or inspecting a manifest at a greater depth,
Package Manager MUST verify that the corresponding limit permits the operation.

A candidate consideration occurs when Package Manager examines one satisfying candidate in the required order
for possible assignment and dependency exploration.
Each candidate record is charged at most once for that package name in one root operation,
including when a cached result is reused after backtracking.
Package Manager MUST consider candidates in the order defined below
and MUST NOT consider another candidate for that package name after its limit is reached.
The existence of additional unexamined catalog versions does not itself cause failure
when an examined candidate produces a complete closure.

A candidate-assignment attempt occurs whenever Package Manager tentatively binds a package name to a candidate,
including an assignment retained in the final closure and a repeated assignment after backtracking.
The attempt counter spans the complete root operation and MUST NOT decrease during backtracking.

If resolution would exceed any resolver limit before finding a complete closure,
Package Manager MUST terminate the root operation with `dependency-unavailable`.
It MUST NOT install a partial closure or modify installed package state.
Limit exhaustion and all counter values are determined by the installed state, catalog inputs, and protected policy
and MUST NOT depend on implementation-local resource thresholds.

To resolve, install, or update a root package,
Package Manager MUST recursively inspect the selected dependency manifests
and construct the transitive package closure.
One closure MUST select at most one version of each package name.
Package Manager MUST detect a dependency cycle and fail the root operation with `dependency-unavailable`.

A candidate is an installed package record or catalog package whose version
satisfies every accumulated requirement for its package name.
A candidate MUST also satisfy the applicable manifest-commitment,
realization-profile, platform-variant, signature, and artifact rules for the requested operation.
Its signature MUST validate under an accepted trust anchor,
and its authenticated signer MUST be authorized for its exact package name.
Package Manager MUST exclude a candidate that fails this requirement before ordering candidate versions by SemVer precedence or exploring its dependency closure.
An installed candidate with matching exact identity and manifest commitment
MAY satisfy a dependency without being materialized again.

Resolution MUST be deterministic for the same installed state,
catalog inputs, and protected policy.
When an operation supplies a package source,
the verified source manifest fixes the root package's exact version.
When a root package reference omits `version` and no source is supplied,
Package Manager MUST select the highest available normal release under SemVer precedence.
A pre-release root version MUST be selected by an explicit version or source.
When a choice is required,
Package Manager MUST select the unresolved package name that is first in UTF-8 byte order.
It MUST consider that package's satisfying candidate versions in descending SemVer precedence.
It MUST select the first candidate for which the complete transitive closure can be resolved,
backtracking to lower candidates when a candidate's dependencies make the closure unsatisfiable.
If multiple acceptable manifests claim the same package name and version with
different manifest commitments,
protected catalog policy MUST select one exact commitment or resolution MUST fail.
If no complete solution exists, the root operation MUST fail with `dependency-unavailable`.

The `resolved_dependencies` array in an installed package record
MUST contain one exact entry for every direct manifest dependency,
in manifest declaration order.
It MUST be empty when the manifest declares no dependencies.
Each entry binds the selected package name and version to its exact manifest commitment.
Catalog changes MUST NOT alter the recorded dependency edges of an installed package.
Different installed closures MAY contain different versions of one package name,
but one closure MUST NOT select more than one.

Package Manager MUST NOT infer a Logos package dependency from a module provider requirement,
build metadata, or a realization backend's internal dependency closure.

Under the LGX profile, each selected dependency is an independently located and validated Logos package.
The root LGX archive does not need to contain its dependency archives.
Package Manager obtains dependency sources through active catalog or deployment policy
and applies the same LGX manifest, signature, variant, and artifact rules to each selected package.
Merely embedding another archive or artifact in the root package does not satisfy a dependency declaration.
When no catalog source is available,
an LGX operation can resolve a dependency only from a satisfying installed package;
otherwise it MUST fail with `dependency-unavailable`.

Requested permissions are declared module data.
Their approval, denial, grant scope, revocation, and enforcement semantics are
defined by Capability Authority, Runtime, and security profiles.
Package Manager MUST preserve requested permission declarations as module facts,
but it MUST NOT convert them into runtime authority.
A requested permission declaration is not evidence that the permission has been reviewed, approved, or granted.

`permission` identifies the specification or selected profile that defines the permission.
`constraints` contains one Logos deterministic-CBOR value
that MUST conform to the CDDL owned by that definition.
A permission without parameters uses the deterministic-CBOR encoding of an empty map.
The defining permission maps the declaration to one or more Capability Authority scopes.
`reason` is explanatory package metadata and MUST NOT change the requested or granted scope.

`requires` in a module declaration uses the Package Manifest provider-requirement shape.
Each entry declares an exact concrete or interface contract and a provider-set cardinality.
It does not select a provider or grant authority.
Package Manager may use these requirements for dependency graph presentation,
install-time diagnostics, or runtime-handoff construction.
Runtime remains responsible for provider selection and validation.

## 12. Runtime Handoff Records

For an installed package, Package Manager can return a record that Runtime consumes.

```cddl
logos.package_manager.runtime_artifact = {
  id: logos.package_manifest.artifact_id,
  local_path: tstr .size (1..4096),
  hash: bstr .size 32,
  hash_suite: "logos.hash-suite.blake3-256",
}

logos.package_manager.runtime_handoff = {
  module: tstr .size (1..64),
  package: logos.package_manager.package_identity,
  artifact: logos.package_manager.runtime_artifact,
  manifest_commitment: logos.package_manager.manifest_commitment,
  ? primary_contract: logos.schema_commitment,
  ? implements: [* logos.schema_commitment],
  ? requires: [* logos.package_manifest.provider_requirement],
  ? requested_permissions: [* logos.package_manifest.requested_permission],
  ? configuration: logos.module_configuration.configuration_declaration,
}

```

A Runtime handoff MUST carry the selected installed module artifact
and the exact manifest commitment accepted during package-signature verification.
Its package identity and artifact id MUST equal the corresponding installed-record fields.
Package Manager MUST derive the handoff artifact hash from the signed manifest
and MUST NOT emit the handoff if the package is no longer accepted by active signing trust.

When the signed module declaration contains `configuration`, the Runtime handoff MUST contain the corresponding configuration-owned `configuration_declaration`.
Package Manager constructs `schema.document` from the verified schema artifact and copies the declared root and live-reconfiguration support.
It constructs the configuration-owned `schema.schema_commitment` by copying the declared document commitment fields and adding the schema subtree root derived for that root.
It includes `default_value` only when the signed declaration references a verified default artifact.

The handoff MUST contain the schema document and default value rather than their package artifact identifiers, package paths, or installed paths.
Package Manager MUST NOT emit the handoff unless the resolved declaration satisfies LOGOS-MODULE-CONFIGURATION and exactly matches the signed artifact references and declaration fields.
Runtime MUST independently verify both roots in the configuration-schema commitment and every supplied value before use.

A handoff received from the authenticated Package Manager system service
is accepted artifact-integrity evidence for Runtime.
Copying the same field values into another record does not reproduce that provenance.
The handoff is not approval to realize, route to, or expose the module.
Security properties of the realization, including sandbox strength, permission enforcement, dangerous host operations, and audit requirements, are defined by LOGOS-MODULE-LOADER, Capability Authority, Runtime, and security profiles.
Before a runtime host starts or exposes a module,
active policy must decide whether the package and artifact may be used for the requested placement.
That decision may consume package and artifact identity, requested permissions, and declared provider requirements.
It may also consume isolation requirements, resource bounds, and local deployment policy.
This specification does not define the policy language, consent flow, grant record, or audit record for that decision.

The handoff MUST preserve the module declaration's `primary_contract`,
`implements`, `requires`, and `requested_permissions` without adding or widening any declaration.
Its `module` field MUST equal the module declaration's flat runtime module name.
Runtime consumes the handoff fields directly and combines them with Runtime-owned decisions and state.
The handoff record is not the source of runtime truth.
Runtime MUST validate selected providers against the relevant contract
expectations before exposing ready invocation paths.
For every local provider realized through Module Loader, Runtime MUST obtain the complete descriptor from the `call_surface` field of an active Module Loader realization record.
It MUST require the descriptor's optional primary contract and implemented-interface set to match the handoff exactly.
Package Manager does not construct, modify, or authorize that provider descriptor.

The handoff does not select Runtime execution mode, provider identity, module instance identity,
state assignment, static binding, transport endpoint, remote target, Module Loader realization descriptor, or runtime-local options.
Those values belong to Runtime, the runtime host, or deployment inputs.

Runtime constructs a Module Loader realization request from the authenticated Runtime handoff and its own placement and authorization decisions.
Package Manager does not construct or return a Module Loader-owned realization descriptor.

## 13. Storage Distribution Role

Logos Storage is a package distribution and source layer.
Package Manager MAY retrieve package catalogs, source references, and LGX packages from Logos Storage.
Catalog entries may also identify Nix sources for an implementation supporting the Nix profile.

Package Manager is responsible for converting Storage-retrieved package material
into local installed artifacts before Runtime or Module Loader uses it.
Runtime and Module Loader MUST consume local resolved artifacts, not remote
Storage objects.

## 14. Results And Errors

Each Package Manager method returns a closed method-specific success or error variant.
A success variant MUST NOT contain an error, and an error variant MUST contain exactly one package error.

```cddl
logos.package_manager.package_error = {
  code: logos.package_manager.package_error_code,
  ? message: tstr .size (0..512),
}

logos.package_manager.package_error_code =
  "invalid-request" /
  "unsupported-source" /
  "package-unavailable" /
  "package-not-installed" /
  "package-conflict" /
  "package-in-use" /
  "invalid-package" /
  "incompatible-platform" /
  "dependency-unavailable" /
  "artifact-integrity-failed" /
  "signature-verification-failed"
```

`invalid-request` identifies a semantically invalid request that MUST NOT be retried unchanged.
`unsupported-source` permits the caller to choose a source kind implemented by the provider.
`package-unavailable` means the requested package or source could not be located or materialized.
`package-not-installed` means an update or handoff target has no installed record.
`package-conflict` means the installed set already contains the same package identity with another manifest commitment.
`package-in-use` means another installed package's recorded dependency edge prevents removal or replacement.
`invalid-package` covers an absent or invalid manifest, invalid archive or realized-output structure, and invalid package-carried configuration material.
`incompatible-platform` permits selection of another package version or source with a compatible variant.
`dependency-unavailable` means no valid complete dependency closure could be selected
or resolution exhausted a protected resolver limit.
`artifact-integrity-failed` means required artifact bytes were absent, escaped their realization root, or did not match the signed digest.
`signature-verification-failed` means the signature container, signer trust, freshness requirement, or signed manifest commitment was not accepted.

An error message is diagnostic text only.
It MUST NOT expose credentials, protected policy input, private source data, host paths, backend configuration, or information the caller is not authorized to observe.
Package errors are operational results and MUST NOT be interpreted as authorization decisions.
The ordinary Interface and Transport invocation-error channels report inability to obtain a valid Package Manager response.
Such failures MUST NOT be encoded as another Package Manager error value.

Package Manager MAY use backend-specific cache, root, or garbage-collection mechanics internally.
Those mechanics are not exposed as package operation states by this specification.

## 15. Package Manager Methods

This contract defines these methods:

- `list_packages`;
- `inspect_package`;
- `install_package`;
- `remove_package`;
- `update_package`;
- `list_installed_packages`;
- `get_runtime_handoff`.

```cddl
_module = "logos_package_manager"

logos.package_manager.cursor = tstr .size (1..512)

logos.package_manager.list_packages_request = {
  ? package: logos.package_manifest.package_name,
  ? cursor: logos.package_manager.cursor,
  ? limit: uint16,
}

logos.package_manager.list_packages_response =
  {
    packages: [* logos.package_manager.package_catalog_entry],
    ? next_cursor: logos.package_manager.cursor,
  } /
  { error: logos.package_manager.package_error }

logos.package_manager.inspect_package_request = {
  ? package: logos.package_manifest.package_name,
  ? version: logos.package_manifest.package_version,
  ? source: logos.package_manager.package_source,
}

logos.package_manager.inspect_package_response =
  { inspection: logos.package_manager.package_inspect_record } /
  { error: logos.package_manager.package_error }

logos.package_manager.install_package_request = {
  package: logos.package_manifest.package_name,
  ? version: logos.package_manifest.package_version,
  ? source: logos.package_manager.package_source,
}

logos.package_manager.install_package_response =
  { installed: logos.package_manager.installed_package_record } /
  { error: logos.package_manager.package_error }

logos.package_manager.remove_package_request = {
  identity: logos.package_manager.package_identity,
}

logos.package_manager.remove_package_response =
  {} /
  { error: logos.package_manager.package_error }

logos.package_manager.update_package_request = {
  current: logos.package_manager.package_identity,
  ? target_version: logos.package_manifest.package_version,
  ? source: logos.package_manager.package_source,
}

logos.package_manager.update_package_response =
  { installed: logos.package_manager.installed_package_record } /
  { error: logos.package_manager.package_error }

logos.package_manager.list_installed_packages_request = {
  ? package: logos.package_manifest.package_name,
  ? cursor: logos.package_manager.cursor,
  ? limit: uint16,
}

logos.package_manager.list_installed_packages_response =
  {
    packages: [* logos.package_manager.installed_package_record],
    ? next_cursor: logos.package_manager.cursor,
  } /
  { error: logos.package_manager.package_error }

logos.package_manager.get_runtime_handoff_request = {
  package: logos.package_manager.package_identity,
  module: tstr .size (1..64),
}

logos.package_manager.get_runtime_handoff_response =
  { handoff: logos.package_manager.runtime_handoff } /
  { error: logos.package_manager.package_error }

```

If `limit` is absent, the default is 100 records.
If present, it MUST be in the inclusive range from 1 through 1000.
Each cursor is opaque and bound to the authenticated caller and original query.
The provider MUST filter records to those the caller may inspect before applying the limit or creating a cursor.
Each response returns at most the applicable limit and MAY return fewer records to remain within the Core Transport message-size ceiling.
A response contains `next_cursor` only when that filtered snapshot contains another record.
Cursor continuation MUST preserve the ordering and remaining records of the original snapshot without duplication.
It MUST reapply current observation authority and omit any remaining record the caller may no longer inspect.
A cursor and result count MUST NOT reveal additional hidden records.
The provider MAY expire a cursor and return `invalid-request` rather than retain the snapshot indefinitely.

`list_packages` returns only exact catalog identities whose source kind the provider implements.
Results are ordered by package-name UTF-8 bytes, descending Semantic Version precedence, and the deterministic-CBOR bytes of the source record.

`list_installed_packages` returns one internally consistent installed-state snapshot.
Results are ordered by package-name UTF-8 bytes, descending Semantic Version precedence, and manifest-commitment bytes.

`get_runtime_handoff` returns one handoff derived from the exact installed package and module.
It MUST return `package-not-installed` when that package identity is absent.
An unknown module is an `invalid-request`.
An absent or mismatched installed module artifact is an `artifact-integrity-failed` error.

`inspect_package` validates and reports package material without installing it.
It MUST NOT change the installed package set.
The request MUST include `package`, `source`, or both.
`version` MUST NOT be present unless `package` is present.
When `package` and `source` are both present, the verified source manifest MUST match the package and optional version constraint in the request.
Inspection MUST resolve and validate the complete transitive dependency closure without installing it.
It MAY retain verified package material in an implementation-local cache.

`install_package` MUST resolve and validate the complete transitive dependency closure
before making the root package visible as installed.
It MUST install missing dependencies before their dependents.
An already-installed package satisfies a selected dependency only when
its package name, version, and manifest commitment match the recorded resolution.
The operation MUST NOT report success for the root package unless every selected dependency is installed.
If installation fails after a dependency becomes installed,
that dependency MAY remain installed,
but the root package MUST remain uninstalled.
Automatically installed dependencies are visible through `list_installed_packages`.
Installing an already-installed package identity with the same manifest commitment succeeds with the current installed record and creates no duplicate.
Installing the same package identity with another commitment fails with `package-conflict`.

`remove_package` removes the selected package from the Logos installed package
set.
It MUST fail with `package-in-use` when another installed package has the selected exact package and manifest commitment in its recorded dependency closure.
It MUST NOT automatically remove dependencies that become unused.
It MAY leave backend cache or store material reachable through backend-specific
garbage-collection policy.
Removing an absent package identity succeeds and MUST NOT affect another identity.

`update_package` selects a version strictly greater than `current` under Semantic Version precedence.
When `target_version` is present, it fixes that exact target version.
When `source` is present, its verified manifest MUST identify the same package name and selected target version.
A target fixed by either field that is not strictly greater than `current` is an `invalid-request`.
When neither fixes a target version, Package Manager selects the highest available newer normal release.
If no applicable newer version exists, the operation succeeds with the current installed record and changes nothing.

Before replacement, Package Manager MUST resolve and validate the selected update's complete transitive dependency closure.
It installs missing dependencies under the same dependency-first rules as `install_package`.
It MUST record the update's newly selected direct dependency edges.
It MUST fail with `package-not-installed` when `current` is absent
and with `package-in-use` when another installed package depends on that exact current package and commitment.
If the update fails, the previously installed root package version MUST remain installed.
On success, replacement of the current root record with the updated root record MUST be atomic.

Package Manager MUST serialize installed-state mutations whose affected package identities or dependency closures overlap.
An observer sees either the complete installed state before such a mutation or the complete state after it.
It MUST NOT observe a partially created, removed, or replaced root record.
Operations over disjoint package identities and dependency closures MAY proceed concurrently.

## 16. Shared Type Ownership

Package-specific records are owned by this specification.
Other Core specs consume them by schema reference when they need package facts.

The Package Manifest supporting schema is owned by the `logos.package_manifest` schema
namespace.
Package Manager catalog, inspect, source, installed-artifact, resolved-dependency, error, and handoff records are owned by the `logos.package_manager` schema namespace.

Package Manager records reference canonical Package Manifest declarations when they report signed package facts.
Runtime consumes validated schema commitments, provider requirements, requested permissions, and artifacts from the handoff.
That consumption does not make Package Manifest subtree roots Runtime type roots.

Runtime consumes `logos.package_manager.runtime_handoff` records as Package Manager output.
Runtime supplies Module Loader realization requests after applying placement and authorization decisions.
Capability Authority and security profiles consume signed `logos.package_manifest.requested_permission`
values as package-declared inputs to authorization policy.

Runtime, Interface, Transport, Commitment Model, and Hash Profile MUST NOT depend on Package Manager
to define contract identity, implemented interfaces, or provider requirements.

This specification does not move additional package-specific fields into the Logos common schema surface defined by LOGOS-MODULE-INTERFACE.

## 17. Boundary With Other Core Specs

LOGOS-MODULE-RUNTIME owns module lifecycle, provider state, routing, readiness,
Runtime Control, and runtime enforcement points.

LOGOS-MODULE-LOADER owns the contract for realizing Runtime-selected artifacts as concrete execution forms.

LOGOS-MODULE-CAPABILITY-AUTHORITY owns authorization decisions, permission
grants, denial reasons, grant revocation, and security audit material.

LOGOS-MODULE-PACKAGE-MANAGER owns package-signing trust input,
signature verification, and package and artifact integrity semantics.
LOGOS-MODULE-SECURITY-CONSIDERATIONS summarizes the integrated threat model.
Selected security and platform profiles own only the additional trust,
permission-mapping, sandbox, or deployment requirements that they explicitly define.

---

## References

- [RFC 6234]: US Secure Hash Algorithms (SHA and SHA-based HMAC and HKDF).
- [RFC 8032]: Edwards-Curve Digital Signature Algorithm (EdDSA).
- [RFC 8949]: Concise Binary Object Representation (CBOR).
- [RFC 9052]: CBOR Object Signing and Encryption (COSE): Structures and Process.
- [RFC 9864]: Fully-Specified Algorithms for JOSE and COSE.
- [DSSE v1]: Dead Simple Signing Envelope, version 1.
- [in-toto Attestation v1]: in-toto Attestation Framework, version 1.
- [SLSA v1.2]: Supply-chain Levels for Software Artifacts, version 1.2.
- [SLSA Source v1.2]: Supply-chain Levels for Software Artifacts, Source Track, version 1.2.

[RFC 6234]: https://www.rfc-editor.org/rfc/rfc6234
[RFC 8032]: https://www.rfc-editor.org/rfc/rfc8032
[RFC 8949]: https://www.rfc-editor.org/rfc/rfc8949
[RFC 9052]: https://www.rfc-editor.org/rfc/rfc9052
[RFC 9864]: https://www.rfc-editor.org/rfc/rfc9864
[DSSE v1]: https://github.com/secure-systems-lab/dsse/blob/master/envelope.md
[in-toto Attestation v1]: https://github.com/in-toto/attestation/blob/main/spec/v1/
[SLSA v1.2]: https://slsa.dev/spec/v1.2/
[SLSA Source v1.2]: https://slsa.dev/spec/v1.2/source-requirements

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
