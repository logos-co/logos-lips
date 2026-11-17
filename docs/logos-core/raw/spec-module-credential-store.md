# LOGOS-MODULE-CREDENTIAL-STORE

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Credential Store                                        |
| Slug         | 316                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines Credential Store ownership, protected persistence, and administrative boundaries.
The caller-owned contract creates opaque credentials and inspects their presence.
Administrative methods manage separately assigned credentials without transferring ownership to the administrator.
It is a Layer 3 Runtime-adjacent module service.

## Requirements Language

Uppercase requirement keywords in this specification follow BCP 14 [RFC 2119] [RFC 8174].
Lowercase forms retain their ordinary English meanings.

## 1. Scope and Ownership

The canonical module name is `logos_credential_store` and the schema namespace is `logos.credential_store`.
The CDDL block in Section 3 is the complete module contract schema.

Credential Store is an ordinary local module provider using the existing identity, lifecycle, authority, routing, and invocation model.
Implementing this contract grants no authority to access a backend or provision a credential.
Capability Authority supplies authorization decisions; Runtime enforces invocation authority; Credential Store enforces slot ownership and storage semantics.
Protected deployment input selects the provider, backend access, and slot assignments.

For caller-owned storage, a credential is an opaque byte string whose format and use belong to the consuming component.
The caller-owned methods are `create` and `status`.
These methods provide no credential retrieval, enumeration, replacement, deletion, key generation, signing, or startup-delivery operation.
Administrative methods belong to the same Credential Store contract and require separate authorization.
Support for administrative operations is optional; providers without that support return `unsupported` as defined in Section 4.1.
They may generate, import, and stage identity credentials, export them in encrypted form, and seal unlock material through the selected backend.
Certificate issuance is an optional administrative operation using an explicitly authorized certificate-authority assignment.
Administrative methods MUST NOT expose plaintext private keys or provide per-handshake signing through module calls.
Provisioning MUST NOT start a component, grant execution authority, or change inputs already delivered to a running realization.
Runtime and Capability Authority bootstrap MUST NOT depend on this service being available.
Credential Store is optional to implement and deploy.
Conformance to LOGOS-MODULE-RUNTIME, LOGOS-MODULE-TRANSPORT, or LOGOS-MODULE-SYSTEM-BCP does not require this contract.

## 2. Caller and Slot Binding

For `create` and `status`, a slot is identified by the authenticated caller's Runtime and module-instance identities together with a credential name.
Names contain 1–64 lowercase ASCII letters, digits, or hyphens.
The request name is a logical identifier, not a storage path.

The provider MUST obtain the caller from the protected invocation context and MUST NOT accept a request-supplied identity as authentication.
Runtime MUST authorize each requested method under active policy before dispatch.
The provider MUST reject a call without authenticated context or from a module instance owned by another Runtime with `NOT_AUTHORISED`.
The provider MUST reject an undeclared or unauthorized slot with `NOT_AUTHORISED` before accessing its backend or revealing its presence.

Protected deployment input MUST bind each permitted caller and name to one authoritative storage slot.
Different caller identities MUST NOT alias the same slot.
Module configuration, package declarations, and method authority MUST NOT create slot assignments or select host storage locations.
A slot assignment MUST remain associated with the same owner across provider and host restart.
Provider replacement or a different route MUST NOT silently select an empty store in place of that slot.

### 2.1 Administrative Assignments

The following requirements apply when administrative operations are supported.
Protected deployment input MUST assign each administrative credential a stable logical identifier, owner, backend, and permitted operations.
The owner MAY be the Runtime itself and MUST remain independent of the administering module's lifetime.
A request identifies an existing assignment; it MUST NOT create an assignment, select a backend, or supply a storage path.
Method authority alone MUST NOT authorize access to an assignment.
The provider MUST check the authenticated caller's current administrative permission for the exact assignment and operation before accessing backend material or revealing its presence.
Permission to administer an identity MUST NOT imply permission to issue certificates using a certificate-authority assignment.
Certificate issuance MUST be constrained by protected policy to authorized subject identities, names, certificate purposes, and validity periods.
Issuing a certificate MUST NOT enroll a peer, change trust anchors, or grant execution authority.
Encrypted export MUST require explicit export permission for the selected assignment and version.
Permission to generate, import, stage, or activate a credential MUST NOT imply export permission.
Administrative permissions MUST NOT broaden existing `create` or `status` permissions.

Credential versions MUST be immutable and retain the assignment's owner across administrator, provider, and host restart.
Generation and import stage a version without replacing an active credential.
Rotation MUST preserve the established Runtime identity.
An uncertain result MUST NOT be interpreted as absence or permission to overwrite existing material.
Generation and import retries MUST identify the original operation and distinguish matching retained work from conflicting input.

When these administrative methods are used, the applicable deployment profile defines protected deployment selection and public trust updates.
Credential Store MUST NOT activate Runtime credentials or change public trust as a side effect of credential administration.
Activation MUST be explicit and MUST preserve the active credential when replacement fails.
The host integration that performs activation under Section 5 MUST check concurrent deployment changes against the caller's expected revision.
Its outcomes MUST distinguish credential staging, protected deployment publication, and Runtime acceptance.
The Credential Store methods define no activation operation and carry no deployment revision.
These operations provide no transaction spanning credential storage, deployment publication, and Runtime activation.
Stopping an administrative provider MUST NOT by itself invalidate an active Runtime credential or prevent its continued use.

### 2.2 Administrative Authorization

Administrative operations use the `logos.credential-store.administration` permission through the existing `permission_scope` defined by LOGOS-MODULE-CAPABILITY-AUTHORITY.
This permission is required when an administrative operation is supported.
Its deterministic-CBOR constraints MUST conform to `logos.credential_administration.scope` below.
It does not change the ownership or authorization rules of `create` and `status`.
The following CDDL block is the complete `logos.credential_administration` supporting schema.

```cddl
logos.credential_administration.name = tstr .size (1..64)
logos.credential_administration.version = tstr .size (1..128)

logos.credential_administration.scope = {
    runtime_instance_id: tstr .size (1..128),
    assignment: logos.credential_administration.name,
    operation: "inspect" / "generate" / "import" / "export" / "seal-unlock",
    ? version: logos.credential_administration.version,
} / {
    runtime_instance_id: tstr .size (1..128),
    assignment: logos.credential_administration.name,
    operation: "issue",
    ? version: logos.credential_administration.version,
    subjects: [* tstr .size (1..128)],
    allow_unnamed: bool,
    names: [* tstr .size (1..255)],
    purposes: [* tstr .size (1..64)],
    validity_seconds: uint64,
}
```

The Runtime identity and assignment identify one protected assignment within that Runtime.
All providers serving that assignment MUST resolve it to the same owner and authoritative backend.
Assignment names follow the name grammar in Section 2; version identifiers are opaque and MUST NOT be interpreted as paths.
Permission scopes MUST NOT create assignments, establish ownership, or replace provider-method authorization.
The `version` field MUST be absent for `generate` and `import`; those operations cannot select an existing version.
For operations selecting an existing version, the evaluated scope MUST name that exact version.
An `inspect` operation without a version authorizes operation-status inspection, not disclosure of credential versions.

The protected invocation integration MUST evaluate the original authenticated caller's permission for the exact operation and assignment.
It MUST NOT substitute the provider's authority or authenticate a caller from request fields.
The provider MUST reject the operation if that caller binding or an enforceable authorization result is unavailable.
Permission MUST be checked before backend access and rechecked before durable publication or a secret-bearing response.
Rejection MUST preserve existing credentials and MUST NOT report an uncertain operation as absent.

Issuance requires an `issue` scope for the certificate-authority assignment in addition to permissions for operations on the target assignment.
The evaluated issuance scope MUST contain exactly one subject, the complete requested name and purpose sets, requested validity, and the selected issuer version when one already exists.
Creating a self-signed certificate-authority credential also requires issuance permission.
The selected certificate profile MUST define canonical subject, name, and purpose encodings and their enforcement against the protected assignment and resulting certificate.
Unknown or unenforceable encodings MUST fail closed.
A request MUST NOT obtain broader issuance authority by omitting or substituting certificate fields.

Scope containment requires equal Runtime identities, assignments, and operations.
An absent version in a policy scope permits any version; a present version requires the same version in the evaluated scope.
For issuance, each evaluated set MUST be a subset of its policy set, and evaluated validity MUST be positive and no greater than the policy limit.
Policy validity limits MUST also be positive.
Subject sets MUST contain 1–64 values, name sets at most 64 values, and purpose sets 1–16 values.
`allow_unnamed` permits issuance without certificate names; a policy scope with an empty name set MUST set it to true.
An evaluated issuance scope MUST set `allow_unnamed` to true exactly when the requested certificate has no names.
A scope permitting unnamed certificates MUST NOT be contained by a scope that forbids them.
Sets MUST contain distinct values in ascending bytewise order of their complete deterministic-CBOR encodings.
Identifiers and set elements compare exactly; they are not wildcard or prefix patterns.
Two scopes overlap only if their Runtime identities, assignments, and operations match and their version constraints are compatible.
Issuance overlap additionally requires intersecting subject and purpose sets, and either intersecting name sets or both scopes permitting unnamed certificates.
The existing Capability Authority denial, expiry, revocation, and decision-validation rules apply.

## 3. Module Contract

```cddl
_module = "logos_credential_store"
_sensitive = [
    "logos.credential_store.create_request",
    "logos.credential_store.export_request",
    "logos.credential_store.export_response",
    "logos.credential_store.generate_request",
    "logos.credential_store.import_request",
    "logos.credential_store.issue_request",
    "logos.credential_store.seal_unlock_request",
    "logos.credential_store.seal_unlock_response",
]

logos.credential_store.name = tstr .size (1..64)
logos.credential_store.value = bstr .size (1..65536)
logos.credential_store.error = "unavailable" / "capacity"

logos.credential_store.create_request = {
    name: logos.credential_store.name,
    value: logos.credential_store.value,
}

logos.credential_store.create_response =
    { result: "created" / "already-exists" } /
    { error: logos.credential_store.error }

logos.credential_store.status_request = {
    name: logos.credential_store.name,
}

logos.credential_store.status_response =
    { state: "absent" / "present" } /
    { error: logos.credential_store.error }

logos.credential_store.identifier = tstr .size (1..128)
logos.credential_store.unlock = bstr .size (1..4096)
logos.credential_store.encrypted = bstr .size (1..131072)
logos.credential_store.public_data = bstr .size (1..65536)
logos.credential_store.administration_error =
    "unsupported" / "unavailable" / "capacity" / "conflict" / "invalid-credential" / "not-found"

logos.credential_store.credential_version = {
    version: logos.credential_store.identifier,
    profile: logos.credential_store.identifier,
    public_data: logos.credential_store.public_data,
}

logos.credential_store.certificate_parameters = {
    subject: tstr .size (1..128),
    names: [* tstr .size (1..255)],
    purposes: [* tstr .size (1..64)],
    validity_seconds: uint64,
}

logos.credential_store.inspect_request = {
    assignment: logos.credential_store.name,
    query: "version",
    version: logos.credential_store.identifier,
} / {
    assignment: logos.credential_store.name,
    query: "operation",
    operation_id: logos.credential_store.identifier,
}

logos.credential_store.inspect_response =
    { kind: "version", credential: logos.credential_store.credential_version } /
    {
        kind: "operation",
        state: "absent" / "pending" / "complete" / "failed",
        ? version: logos.credential_store.identifier,
    } /
    { error: logos.credential_store.administration_error }

logos.credential_store.generate_request = {
    assignment: logos.credential_store.name,
    operation_id: logos.credential_store.identifier,
    ? unlock: logos.credential_store.unlock,
    ? certificate: logos.credential_store.certificate_parameters,
}

logos.credential_store.generate_response =
    { result: "staged", credential: logos.credential_store.credential_version } /
    { error: logos.credential_store.administration_error }

logos.credential_store.issue_request = {
    assignment: logos.credential_store.name,
    version: logos.credential_store.identifier,
    target_assignment: logos.credential_store.name,
    target_version: logos.credential_store.identifier,
    certificate: logos.credential_store.certificate_parameters,
    ? unlock: logos.credential_store.unlock,
}

logos.credential_store.issue_response =
    {
        result: "issued",
        profile: logos.credential_store.identifier,
        public_data: logos.credential_store.public_data,
    } /
    { error: logos.credential_store.administration_error }

logos.credential_store.import_request = {
    assignment: logos.credential_store.name,
    operation_id: logos.credential_store.identifier,
    format: logos.credential_store.identifier,
    encrypted: logos.credential_store.encrypted,
    passphrase: logos.credential_store.unlock,
    ? unlock: logos.credential_store.unlock,
}

logos.credential_store.import_response =
    { result: "staged", credential: logos.credential_store.credential_version } /
    { error: logos.credential_store.administration_error }

logos.credential_store.export_request = {
    assignment: logos.credential_store.name,
    version: logos.credential_store.identifier,
    format: logos.credential_store.identifier,
    passphrase: logos.credential_store.unlock,
    ? unlock: logos.credential_store.unlock,
}

logos.credential_store.export_response =
    {
        result: "exported",
        format: logos.credential_store.identifier,
        encrypted: logos.credential_store.encrypted,
    } /
    { error: logos.credential_store.administration_error }

logos.credential_store.seal_unlock_request = {
    assignment: logos.credential_store.name,
    version: logos.credential_store.identifier,
    unlock: logos.credential_store.unlock,
}

logos.credential_store.seal_unlock_response =
    {
        result: "sealed",
        format: logos.credential_store.identifier,
        encrypted: logos.credential_store.encrypted,
    } /
    { error: logos.credential_store.administration_error }
```

Requests and responses use the ordinary Logos method contract, deterministic CBOR, and invocation-error channel.
Invalid request shapes, names, identifiers, and certificate constraint sets MUST fail with `INVALID_PARAMS`.
Authorization failures use `NOT_AUTHORISED`; malformed or denied requests MUST NOT mutate storage.
Backend unavailability and storage capacity are domain outcomes represented by the response schema.
They MUST NOT be represented as Runtime-owned readiness failures.
`unavailable` covers locked or inaccessible storage, integrity failures, and uncertain backend outcomes without disclosing backend details.
`capacity` means the provider cannot admit the operation within its configured resource limits.
The provider MUST bound request concurrency, retained secret bytes, backend work, and operation duration.

## 4. Creation, Status, and Recovery

`create` MUST atomically create a credential only when the selected slot is absent.
The provider MUST persist the exact submitted bytes with confidentiality and integrity protection before reporting `created`.
A reported creation MUST survive provider and host restart, including process or power loss after acknowledgement, under the deployment's documented storage failure model.
A backend that cannot establish this persistence MUST NOT report `created`.

An occupied slot MUST remain unchanged and return `already-exists`.
This result MUST NOT depend on comparing the submitted value with the stored value and does not assert that they match.
Concurrent creators MUST be serialized at the authoritative slot, including calls through multiple provider instances.
Retries, cancellation, response loss, backend errors, and recovery MUST NOT overwrite or remove an existing credential.
Provider cleanup MUST NOT remove a credential merely because its caller disconnected or its realization stopped.

`status` MUST report `present` only for a committed credential and `absent` only for a confirmed empty slot.
It MUST NOT return the credential, its length, or a value-derived identifier.
Status and creation MUST observe one consistent order for that slot.
A locked, inaccessible, corrupt, partially written, or uncertain slot MUST NOT be reported as absent.
Recovery MUST reconcile an incomplete creation or leave the slot unavailable; it MUST NOT silently reset the slot.

A failure or missing response does not establish that creation failed to commit.
A caller may query status to resolve presence, but MUST NOT infer a stored credential's value from `present` or `already-exists`.
Component setup owns the consistency of its public configuration with the credential it generated.
This contract provides no transaction spanning component configuration and credential storage.

### 4.1 Administrative Methods

Administrative requests select an assignment owned by the authenticated caller's Runtime.
The provider MUST reject requests without authenticated local caller context with `NOT_AUTHORISED`.
Assignment names follow Section 2; version and operation identifiers are opaque values compared exactly and MUST NOT be interpreted as paths.
Protected deployment input selects the assignment's credential profile, backend, permitted operations, and sealing recipient.
Requests MUST NOT select a different owner, backend, storage path, or sealing recipient.

Every provider MUST expose all methods in Section 3.
A provider that supports no administration MUST reject deployment input assigning it administrative credentials or retained administrative work.
For well-formed administrative requests, that provider MUST return `unsupported` after ordinary method authorization, without resolving assignments or accessing a backend.
This response MUST be independent of assignment, version, and operation existence.
Otherwise, the provider MUST enforce Section 2.2 before inspecting an assignment or reporting an unsupported operation or format for it.
`unsupported` MUST NOT substitute for denied authority, a locked backend, or an uncertain operation outcome.
A previously admitted operation MUST retain its recovery semantics if support changes.
`unsupported` MUST NOT be returned for retained work whose outcome is uncertain.

`inspect` requires an `inspect` permission for the requested assignment and, for a version query, the exact version.
A version query returns only that version's identifier, profile, and public data.
An operation query returns generation or import status for the exact operation identifier without returning its request or value-derived identifiers.
Operation status MAY include the created version identifier; it MUST NOT include public credential data without version-specific inspection authority.
`absent` means no operation was admitted under that identifier; uncertainty MUST return `unavailable`.
`pending` means an admitted operation has no established terminal result.
`complete` means its success result is durably established; `failed` means recovery has established that it produced no success result and will not publish one.
The `version` field MUST be absent for `absent` and `failed`, and MUST identify the result version for completed generation or import.

`generate` creates new private material according to the protected assignment's profile and stages an immutable version.
`import` decrypts and validates the supplied encrypted credential before staging an immutable version under the target assignment's existing owner.
The provider MUST verify that imported private and public material correspond and satisfy the assignment's profile and identity constraints.
Neither operation selects an existing version or changes deployment selection.
The provider assigns the version identifier; it MUST be independent of credential values and MUST NOT be reused within the assignment.
`staged` MUST be reported only after the credential and retry record are durably committed under the deployment's documented storage failure model.
The returned `public_data` MUST contain only public material in the encoding defined by the selected credential profile.
A profile MAY keep issued certificates separate from the immutable key version; the applicable deployment profile then defines their association and validates it before activation.

`certificate` contains the complete requested subject, name set, purpose set, and validity limit.
Name and purpose arrays follow the cardinality, uniqueness, and ordering rules in Section 2.2.
When `generate` includes `certificate`, it creates a self-signed certificate-authority credential and requires both `generate` and `issue` permission on the target assignment, without a version.
The selected profile MUST permit that operation; omitting required certificate parameters MUST fail with `INVALID_PARAMS`.

`issue` signs a certificate for the public key of `target_assignment` and `target_version` using the certificate-authority credential selected by `assignment` and `version`.
Both assignments belong to the same Runtime.
It requires `issue` permission on the exact issuer version and `inspect` permission on the exact target version.
The provider MUST resolve the target's public key and identity through protected assignment integration; request data MUST NOT substitute another key or owner.
Issuance MUST NOT require access to the target's private key, including when the assignments are served by different provider instances.
The target's selected certificate profile MUST bind the subject to its protected identity and validate the resulting certificate against every issuance constraint.
The provider MUST NOT substitute an issuer or target, add names or purposes, or exceed the requested validity.
The response contains the issued public certificate material in the encoding defined by the target profile.
Issuance MUST NOT modify either credential version or select the certificate for deployment.

`export` requires `export` permission for the exact version and produces an encrypted credential in the requested format using the supplied export passphrase.
The export MUST include the public material and profile information required for subsequent import and MUST protect the private material's confidentiality and integrity.
The provider MUST reject a format that cannot provide these properties; it MUST NOT fall back to plaintext or a different format.
`seal_unlock` requires `seal-unlock` permission for the exact version.
It MUST verify that the supplied material unlocks that version before sealing it for the protected deployment-selected recipient.
It MUST NOT seal arbitrary supplied bytes or return plaintext unlock material.
Export and sealing do not change the credential, activate it, or publish deployment input.
Their successful responses identify the actual output format.

`issue`, `export`, and `seal_unlock` do not create credential versions and do not use retained operation identifiers.
Each retry is a new invocation requiring current authorization for the exact versions and may produce different valid output bytes.
The contract does not require durable retention of requests or results for these methods.

The selected credential profile MUST define generation requirements, public-data encoding, identity validation, supported encrypted import/export formats, and unlock handling.
Each encrypted format MUST define its encoding, cryptographic protection, passphrase interpretation, and required validation.
The sealing profile MUST define the output encoding, recipient binding, and validation needed for protected delivery.
Profile and format identifiers compare exactly and MUST NOT be interpreted as paths or executable names.
These identifiers do not make a profile mandatory for other implementations; interoperability requires a mutually supported definition.
Unknown profiles or formats MUST NOT select an implicit default.
Unlock material and import/export passphrases MUST NOT be interchanged or used for another assignment.
This requirement constrains provider and host handling; an encrypted bundle format is not required to bind an assignment, version, or purpose.
The provider MUST NOT prompt for operator input; host-shell modules own prompts and submission.

For `generate` and `import`, `operation_id` identifies one retained operation within an assignment, across caller, provider, and host restart.
The provider MUST atomically reserve it before credential generation or import publication and serialize competing uses at the authoritative backend.
The retained record MUST bind the method and complete request, including secret inputs, under confidentiality and integrity protection.
It MUST also bind the protected assignment's owner, authoritative backend, selected credential profile, and identity constraints applicable at admission, including certificate constraints when present.
Recovery MUST preserve those bindings; if it cannot, the provider MUST return `unavailable` without substituting changed deployment input.
A retry with an identical request MUST resume that operation or return its retained result; it MUST NOT create another version or repeat a completed publication.
A conflicting request using the same identifier MUST return `conflict` without altering the original operation.
Every retry MUST satisfy current authorization for all involved assignments, including issuance permission and authorization before secret-bearing output.
Success MUST NOT be reported before the result is durably retained for matching retries.
Operation records MUST NOT be placed in ordinary module state, logs, diagnostics, or audit records.
The provider MUST bound retained operation data and reject new admission with `capacity` before exhausting that bound.
A provider that retires an operation's request or result MUST keep, under the same protection, the operation identifier, the information needed to compare a retried request, and the last established outcome state.
Inspection of a retired operation and an identical retry MUST return `unavailable`; a conflicting retry MUST return `conflict`.
A retired operation MUST NOT be reported as `absent`, as pending, or with a newly generated result.
Retiring a record MUST NOT make its identifier available for a new operation or turn an uncertain outcome into `absent`.

`not-found` means an authorized version query or operation selecting an existing version has established that the version does not exist.
It MUST NOT disclose undeclared or unauthorized assignments.
`invalid-credential` means supported credential or unlock input failed validation; it MUST NOT disclose secret values or detailed decryption failures.
`conflict` means an admitted operation identifier is already bound to a different request.
`unavailable` and `capacity` retain their meanings from Section 3.
A failure or missing response does not establish that generation or import failed; callers MUST retain the operation identifier for recovery.

## 5. Protection and Delivery Boundary

The provider receives submitted credential plaintext and is trusted to handle it.
A deployment MUST protect invocation traffic and secret-bearing buffers from unauthorized observation or modification.
Method authority and payload commitments do not provide confidentiality by themselves.

The backend MUST provide encrypted persistent storage and integrity protection for the credential and its owner/slot association.
The provider MUST NOT fall back to plaintext persistence or encryption without secret key protection.
Plaintext credentials MUST NOT enter ordinary module configuration, assigned persistent state, logs, audit records, diagnostics, responses, or events.
Logs and audit records MUST NOT contain credential hashes or other value-derived identifiers.
The ordinary commitment requirements still apply to invocation processing; they do not authorize retention or disclosure of secret-bearing payloads or their commitments in diagnostic records.

Implementations SHOULD minimize plaintext copies.
They MUST erase owned temporary secret buffers after their last use, before releasing or reusing their storage, as required by LOGOS-MODULE-INTERFACE.
Deployment controls MUST protect secret-bearing memory against unauthorized access and plaintext persistence through swap or crash dumps.
An implementation MUST NOT claim erasure of copies owned by another process or backend.

Deployment MUST restrict the provider's backend privileges to its assigned scope and document any access to existing credential plaintext.
Administrative credentials and caller-owned slots MUST support assignment to separate provider instances with independently restricted backend privileges.
Sharing a module implementation MUST NOT require sharing backend access.
The absence of a retrieval method MUST NOT be treated as evidence that the provider cannot read or decrypt backend contents.
Any process with such backend privileges belongs to the credential trust boundary.
Untrusted modules MUST NOT share that process's address space or have equivalent backend access.

The host integration owns protected credential delivery to the selected component.
Delivery and activation MUST preserve the credential owner and selected version and use only an authorized protected delivery mechanism.
Administration and delivery MUST resolve an assignment and version to the same authoritative credential.
Delivery does not use this contract's response channel.
The storage format, encryption and unlock mechanism, host-delivery interface, and any required restart are deployment choices.
Neither the provider nor its callers obtain authority over Runtime bootstrap credentials merely by implementing or invoking this contract.

## 6. Security Considerations

This contract protects provisioning and persistence within the declared trust boundary.
It does not hide a submitted credential from Credential Store, an authorized recipient, or a host capable of inspecting their memory.
Compromise of the provider can expose submitted credentials and any existing credentials accessible through its backend privileges.
A separate process provides isolation only to the extent that operating-system access controls enforce it.

Encryption at rest does not establish protection against a compromised running host or against theft of both ciphertext and usable decryption material.
Protecting keys from the consuming component requires a separate cryptographic-operation interface and component support for that interface.
This contract makes no guarantee of recovery after destruction of the backend or its unlocking material, or detection of rollback of the entire trusted storage state.
Deployment documentation MUST state those limitations and the storage durability and recovery assumptions.

## Appendix A. Implementation Considerations (Informative)

This appendix illustrates implementations; it imposes no backend or platform requirement.
A provider can adapt an existing operating-system secret store rather than implement a new cryptographic format.
Its module interface remains the same when the backend changes.

A systemd-based deployment can encrypt credentials using host or TPM-backed protection and arrange decryption at service activation through `LoadCredentialEncrypted`.
The provisioning adapter still needs atomic creation, durable publication, slot ownership, and protected input handling.
The service manager's credential mechanism does not supply those module-level semantics by itself.
See [systemd credentials](https://systemd.io/CREDENTIALS/).

A desktop deployment can use a selected Secret Service collection.
Such an implementation needs verified storage protection, owner/slot mapping, coordinated creation, and explicit handling of locked collections.
Selecting a Secret Service API alone does not establish all of this contract's guarantees.
See the [Secret Service API](https://specifications.freedesktop.org/secret-service/latest/).

Separating a restricted provisioning process from a host delivery process can reduce access to existing credentials when the backend enforces that separation.
Where backend permissions cannot enforce it, both processes remain trusted for the credentials they can access.
Backup, recovery, administrative replacement, and key rotation require separately authorized operations that preserve credential ownership, component identity, and configuration consistency.

## References

### Normative

- [RFC 2119] — Key words for use in RFCs to Indicate Requirement Levels.
  https://www.rfc-editor.org/rfc/rfc2119
- [RFC 8174] — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
  https://www.rfc-editor.org/rfc/rfc8174
- LOGOS-MODULE-INTERFACE — Module contracts, generated ABI, deterministic CBOR, and invocation errors.
- LOGOS-MODULE-RUNTIME — Module-instance identity, authenticated invocation, routing, and lifecycle.
- LOGOS-MODULE-TRANSPORT — Protected invocation carriers and payload commitments.
- LOGOS-MODULE-CAPABILITY-AUTHORITY — Method authorization and enforcement boundaries.
- LOGOS-MODULE-CONFIGURATION — Separation of ordinary configuration and credentials.

### Informative

- LOGOS-MODULE-SYSTEM-BCP — Layer 3 placement and complete-system composition.
- LOGOS-MODULE-SECURITY-CONSIDERATIONS — Cross-cutting threat model and deployment controls.

## Copyright

Copyright and related rights waived via [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
