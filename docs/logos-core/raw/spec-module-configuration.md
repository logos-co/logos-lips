# LOGOS-MODULE-CONFIGURATION

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Configuration                                    |
| Slug         | 315                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines schema-typed configuration for module instances.
It defines configuration-schema binding, deterministic configuration values, retained current and staged state, authorized observation and mutation, startup delivery, optional live reconfiguration, and configuration-schema change behavior.

The shared canonical configuration records form a supporting schema.
Configuration behavior and callable operations remain Runtime responsibilities exposed through Runtime Control.

Module configuration controls module behavior.
It does not grant authority, select realization strength, carry protected trust input, or replace Runtime bootstrap configuration.

## Scope

This specification defines:

- one optional configuration root schema for a module declaration;
- one current value and at most one staged value for each module instance;
- schema and value commitments;
- whole-value source selection and provenance;
- authorized Runtime Control observation, mutation, and configuration-state events;
- startup validation, delivery, promotion, retry, failure, and optional live reconfiguration; and
- behavior when an accepted configuration schema changes.

This specification does not define package formats, configuration-file formats, concrete retained storage, module realization, authority policy, secrets, trust anchors, sandbox policy, or product workflows.

## 1. Responsibility And Invariants

Each module instance is owned by exactly one Runtime.
The owning Runtime owns that module instance's configuration state.
Configuration state is bound to the module-instance identity and is not shared merely because several instances use the same module implementation or package.

A module declaration MAY contain one configuration-schema binding.
A declaration without that binding defines a module with no configuration value under this specification.
Runtime MUST reject configuration operations for such a module instance.

A configuration value MUST be one complete value under the bound configuration root.
Core defines no field patch, implicit merge, or partially applied configuration value.

Configuration mutation MUST NOT grant or widen authority.
It MUST NOT authorize or initiate module start, stop, restart, or re-realization.
Module configuration MUST NOT contain requested permissions, authority grants, live authority state, credentials, or protected trust input.
A path, endpoint, provider preference, or other configured behavior remains unusable when active authority or operating-system enforcement denies the required access.

## 2. Configuration Schema

An application-specific configuration schema is a supporting schema interpreted under the CDDL and Logos deterministic-CBOR rules defined by LOGOS-MODULE-INTERFACE.
The configuration CDDL document MUST contain between 1 and 1,048,576 UTF-8 bytes and MUST satisfy the dynamic-schema processing limits defined by LOGOS-MODULE-INTERFACE.
It MUST be self-contained except for references to the pinned Logos common schema surface.
Configuration-schema resolution MUST use only that document and the pinned common schema.
Runtime MUST reject an unresolved external reference and MUST NOT fetch a network resource, read an arbitrary filesystem or package path, or invoke a provider-selected resolver while processing the schema.

The module declaration identifies one root rule in that document as the configuration root and carries a configuration-schema commitment.
That commitment contains the schema root for the complete document and the schema subtree root for the selected configuration root.

The accepted module declaration is Runtime's authoritative pre-start source of the schema document, root rule, and commitment.
A higher-layer package or protected deployment mechanism MAY supply that accepted declaration.
This specification does not require either mechanism for individual conformance.

Runtime MUST parse and validate the CDDL document and MUST recompute both roots before accepting the binding.
The recomputed configuration-schema commitment MUST equal the commitment in the declaration.
Runtime MUST reject the declaration on mismatch, unsupported schema content, an absent root rule, or a root that is not a valid configuration value schema.

For a remote-owned module instance, the target Runtime owns the accepted configuration schema and its disclosure.
Another Runtime MUST NOT substitute a local package schema or facade-provider schema for the target Runtime's accepted schema.

## 3. Configuration Values And State

Every accepted configuration value MUST be valid under the exact configuration-schema commitment recorded with that value.
The value MUST use the Logos deterministic-CBOR representation defined by LOGOS-MODULE-INTERFACE.
The exact deterministic-CBOR bytes of a complete configuration value MUST contain between 1 and 8,388,608 bytes.
Runtime MUST reject an oversized value before decoding or retaining it.

Runtime maintains one monotonically increasing configuration-state revision for each configurable module instance.
Runtime MUST initialize that revision to zero when it creates configuration state for a new module instance.
The revision is an unsigned configuration-state counter, not a module or package release version.
Module and package release versioning remains owned by Package Manager.
Runtime MUST preserve it across stop, start, implementation unload or reload, re-realization, and any Runtime restart that preserves the module-instance identity.
Runtime MUST NOT reset it while retaining that identity.
If Runtime cannot restore the revision for a preserved configuration state, it MUST use a new module-instance identity before creating new configuration state at revision zero.

Every successful mutation of the accepted binding, current record, or staged record advances the configuration-state revision.
An operation that observes or mutates configuration MUST report or compare the revision as required by its method semantics.
The revision MUST NOT wrap.
Runtime MUST reject a state mutation that would advance it beyond the maximum `uint64` value.
Before invoking module behavior for a startup or live-reconfiguration attempt whose success would require such a mutation, Runtime MUST ensure that the revision can advance and MUST reject the attempt without invoking that behavior when it cannot.

Runtime MAY retain the following records:

- one **current value**, which is the value most recently applied by a successful startup or live reconfiguration; and
- one **staged value**, which is the complete candidate for its next startup.

Each retained value record includes its configuration-schema commitment, value commitment, value revision, and provenance.
Its configuration-schema commitment and value commitment MUST contain the same schema subtree root.
The value revision is the configuration-state revision at which Runtime accepted that record's value and does not change when a staged record is promoted to current.
Stopping a module does not remove its current value.
A staged value does not change the behavior of the running realization.

If neither a current nor staged value exists and no valid source supplies a value, Runtime MUST NOT start a module whose declaration contains a configuration-schema binding.

## 4. Sources And Provenance

A package default, protected provisioning input, authorized Runtime Control update, or retained record MAY supply a configuration value.
Every supplied value MUST be one complete deterministic-CBOR value under the exact accepted configuration schema.
No source implicitly merges with another source.

Runtime determines the next-start value in the following order:

1. Runtime restores retained current and staged records.
2. If neither record exists, Runtime MAY accept a package default as the staged value.
3. Runtime commits each accepted protected provisioning input or authorized Runtime Control replacement as a complete staged-value mutation in its configuration-state mutation order.
4. Runtime selects the staged value when one exists and otherwise selects the current value.

A retained record under a different configuration-schema commitment is not eligible for startup and MUST NOT be treated as absence for package-default fallback.
The module instance requires an explicitly supplied complete replacement under the accepted schema before its next startup.

Runtime MUST validate a supplied value and compute its value commitment before changing retained state.
An invalid source MUST NOT partially change current or staged state.

Each accepted value record MUST identify one of the following provenance classes:

- `package-default`;
- `protected-provisioning`; or
- `runtime-control-update`.

Restoring or promoting a retained record MUST preserve its provenance.
Source paths, authoring formats, storage keys, and other acquisition mechanics do not cross the module boundary.

## 5. Runtime Control Operations

The Runtime Control contract includes exactly four configuration operations:

- `get_configuration_schema`;
- `get_configuration`;
- `update_configuration`; and
- `apply_configuration`.

Runtime MUST accept these operations only from an authenticated module instance.
Runtime MUST authorize each invocation for its exact method and target module instance before disclosing information or changing state.
Authority to invoke one configuration operation does not authorize either other configuration operation or any Runtime lifecycle operation.

`get_configuration_schema` returns one consistent snapshot containing the configuration-state revision, accepted CDDL document, configuration root, and configuration-schema commitment.

`get_configuration` returns one consistent snapshot containing the configuration-state revision, accepted configuration-schema commitment, and any current and staged value records.
Each returned record includes the complete value, configuration-schema commitment, value commitment, value revision, and provenance.

`update_configuration` accepts exactly one of the following actions:

- stage one complete replacement value; or
- discard the staged value.

Every request includes the expected configuration-state revision and expected accepted configuration-schema commitment.
Runtime MUST reject the request without mutation when either expectation is stale.
For a replacement, Runtime MUST validate the complete value and compute its value commitment before committing it as staged.

Staging a replacement advances the configuration-state revision even when its value commitment equals that of an existing record.
Discarding an existing staged value advances the revision.
Discarding when no staged value exists succeeds without changing the revision.
The operation returns the resulting configuration-state revision and staged record, when one exists.

Runtime MUST apply each successful mutation atomically in the Runtime Control mutation order for the target module instance.
An observation concurrent with a mutation reports either the complete state before that mutation or the complete state after it.

`update_configuration` does not change the current value, affect the running realization, or invoke a lifecycle operation.

`apply_configuration` applies the staged value to a ready module instance only when both its accepted binding and the binding used to initialize the current realization declare live reconfiguration support.
It has separate authority from configuration observation, staging, and Runtime lifecycle control.

## 6. Startup Delivery And Promotion

Before initialization, Runtime MUST select and snapshot one configuration record as the immutable value for that startup attempt.
Runtime MUST supply its complete value, configuration-schema commitment, and value revision to the applicable realization mechanism for delivery through the structured initialization input or protected executable-startup handoff.
The module configuration boundary MUST NOT receive an implementation-specific configuration-file path.
For the native module ABI,
the realization mechanism MUST deterministically encode exactly one `logos.module_configuration.configuration_input` value and supply it through `logos_module_init_input_t.configuration_cbor` and `configuration_cbor_len`.
When the accepted module declaration has no configuration-schema binding,
the ABI caller MUST use the absent representation defined by LOGOS-MODULE-INTERFACE.

Generated initialization glue MUST embed the complete configuration-schema commitment for which it was generated.
Before decoding the value or invoking module-owned library behavior, the glue MUST compare that commitment with the delivered configuration-schema commitment and reject a mismatch.
It MUST then decode and validate the complete value before passing the typed configuration to module-owned initialization.
A handwritten implementation MUST provide equivalent behavior.

A later configuration mutation does not change the value used by an in-progress startup.
If the module instance reaches `ready`, Runtime MUST make the attempted record current.
It MUST clear the staged record only when that record still has the attempted value revision.
A concurrently replaced staged record remains staged for the next startup, and a concurrently discarded staged record remains absent.

If initialization or readiness fails, Runtime MUST preserve the previous current record.
It MUST leave staged state as established by the latest accepted mutation, so the attempted record remains staged only when it was not subsequently replaced or discarded.

Any mutation of current or staged state caused by successful startup MUST be atomic and advance the configuration-state revision.
A failed startup using the current record does not remove or revise that record.

## 7. Configuration-Schema Changes

Every retained configuration record remains bound to the exact configuration-schema commitment under which Runtime accepted it.
An accepted declaration update that preserves the commitment MAY retain current and staged records unchanged.

When an accepted update changes the commitment, Runtime MUST NOT reinterpret or migrate an existing record automatically.
Successful structural validation under the new schema is not sufficient to establish unchanged meaning.
Existing records remain ineligible for startup or live reconfiguration until an explicit complete replacement is accepted under the new schema.

Runtime MUST order replacement of an accepted binding with configuration mutations, startup attempts, and live-reconfiguration attempts for that module instance.
Replacing a binding in a way that changes its configuration-schema commitment or live-reconfiguration declaration MUST atomically advance the configuration-state revision.

An already-running realization MAY continue with the configuration and implementation under which it reached `ready`.
Starting or re-realizing the module instance under the changed schema requires a complete value accepted under that schema.
Runtime MUST NOT live-apply a value under the changed configuration-schema commitment to the existing realization.
The module instance must restart or be re-realized under the changed commitment before live reconfiguration can resume.

An authorized module instance MAY obtain an old value, transform it outside Core, and submit the complete replacement through `update_configuration`.
This specification defines no general configuration-migration language.

## 8. Live Reconfiguration And Configuration Events

A configuration-schema binding MAY declare live reconfiguration support.
Without that declaration, the module instance is startup-only and Runtime MUST reject `apply_configuration`.
A live-enabled realization MUST expose the standard configuration-application hook for its realization mode.
A module that does not declare live reconfiguration support need not expose that hook or provide a library callback.
For the native module ABI,
that hook is `logos_<module>_apply_configuration()`.
The ABI caller MUST pass the deterministic encoding of exactly one `logos.module_configuration.configuration_input` value selected for the application attempt.
`LOGOS_OK`, a valid nonzero result, and failure to obtain a valid result mean success, rejection, and an indeterminate outcome respectively.

An `apply_configuration` request includes the expected configuration-state revision.
Runtime MUST reject the request when the expectation is stale, no staged record exists, the module instance is not `ready`, either applicable binding does not declare live reconfiguration, or the accepted configuration-schema commitment differs from the commitment used to initialize the current realization.
The staged record MUST carry that same commitment.
Runtime MUST permit at most one live-reconfiguration attempt per module instance and MUST order it with lifecycle transitions for that instance.

Runtime snapshots the staged record as the immutable value for the application attempt.
A later configuration mutation does not change that attempt.
Generated application glue MUST perform the same configuration-schema-commitment comparison and complete-value decoding and validation required during startup before invoking the typed library callback.

The callback MUST report success only after the complete attempted value governs module behavior.
On rejection, it MUST leave behavior governed by the previous current value.
On success, Runtime MUST make the attempted record current.
It MUST clear the staged record only when that record still has the attempted value revision.
A concurrently replaced staged record remains staged, and a concurrently discarded staged record remains absent.

On rejection, Runtime preserves the previous current record and the latest staged state.
If the application outcome is indeterminate, Runtime MUST place the module instance in `error` and prevent further provider work through that realization.
Runtime preserves the previous current record and latest staged state for a later startup or re-realization.

Every live-reconfiguration mutation of current or staged state MUST be atomic and advance the configuration-state revision.
Successful live reconfiguration does not otherwise change lifecycle state and MUST NOT by itself emit `module_state_changed_event`.

Runtime Control defines `configuration_state_changed_event` for authorized observation of configuration-state changes.
Runtime MUST emit it after every configuration-state revision change.
Runtime MUST emit events for one module instance in the same order as their committed configuration-state revisions.
The event identifies the target module instance and configuration-state revision, always includes the accepted configuration-schema commitment, and includes the value commitment, value revision, and provenance of each current or staged record that exists.
It MUST NOT include either complete configuration value.
Runtime MUST authorize subscription and delivery for the exact target module instance and configuration-state observation scope.

## 9. Canonical Configuration Types

This specification owns the shared configuration types below.
Runtime Control, Package Manager, and Module Loader own their method, declaration, and realization envelopes and import the named types they use without changing their semantics.
LOGOS-MODULE-INTERFACE owns the configuration pointer-and-length ABI fields,
while this specification assigns the exact `configuration_input` payload and its validation semantics.

The CDDL block is the `logos.module_configuration` supporting schema.
It is a supporting schema because it defines shared non-callable configuration records used by several module contracts.
It defines no methods, events, provider surface, module identity, or lifecycle.
Runtime owns the behavior represented by these records,
and Runtime Control remains the callable module contract for configuration operations.
Importing a type from this schema does not create a configuration service, module instance, or provider.
The complete supporting schema has its own schema root,
and each imported declaration retains its schema subtree root within that schema.

```cddl
logos.module_configuration.schema_commitment = {
  commitment_model: "logos.commitment-model.2026-08",
  schema_root: bstr .size 32,
  schema_subtree_root: bstr .size 32,
  hash_profile: "logos.hash-profile.2026-08.choice-index",
  hash_suite: "logos.hash-suite.blake3-256",
}

logos.module_configuration.value_commitment = {
  schema_subtree_root: bstr .size 32,
  value_root: bstr .size 32,
}

logos.module_configuration.configuration_value =
  bstr .size (1..8388608)

logos.module_configuration.schema_binding = {
  document: tstr .size (1..1048576),
  root: tstr .size (1..255),
  schema_commitment: logos.module_configuration.schema_commitment,
  ? live_reconfiguration: true,
}

logos.module_configuration.configuration_declaration = {
  schema: logos.module_configuration.schema_binding,
  ? default_value: logos.module_configuration.configuration_value,
}

logos.module_configuration.provenance =
  "package-default" /
  "protected-provisioning" /
  "runtime-control-update"

logos.module_configuration.value_record = {
  value: logos.module_configuration.configuration_value,
  schema_commitment: logos.module_configuration.schema_commitment,
  value_commitment: logos.module_configuration.value_commitment,
  value_revision: uint64,
  provenance: logos.module_configuration.provenance,
}

logos.module_configuration.value_record_metadata = {
  schema_commitment: logos.module_configuration.schema_commitment,
  value_commitment: logos.module_configuration.value_commitment,
  value_revision: uint64,
  provenance: logos.module_configuration.provenance,
}

logos.module_configuration.configuration_state = {
  state_revision: uint64,
  schema_commitment: logos.module_configuration.schema_commitment,
  ? current: logos.module_configuration.value_record,
  ? staged: logos.module_configuration.value_record,
}

logos.module_configuration.configuration_state_summary = {
  state_revision: uint64,
  schema_commitment: logos.module_configuration.schema_commitment,
  ? current: logos.module_configuration.value_record_metadata,
  ? staged: logos.module_configuration.value_record_metadata,
}

logos.module_configuration.configuration_input = {
  value: logos.module_configuration.configuration_value,
  schema_commitment: logos.module_configuration.schema_commitment,
  value_revision: uint64,
}
```

`logos_module_configuration_types.cddl` is an extracted machine-readable mirror of this block.
If the extracted artifact differs from this specification, this specification governs.

`document` contains the accepted CDDL text, and `root` names its configuration root.
Within `schema_commitment`, `schema_root` commits to the complete document and `schema_subtree_root` commits to that selected root.
`default_value` and every `value` field contain the exact deterministic-CBOR bytes of one complete configuration value.
`live_reconfiguration` is present only when the module declaration opts into live reconfiguration.

`value_commitment` is interpreted only with the adjacent `schema_commitment`; their `schema_subtree_root` fields must match, and together they bind the value to the accepted configuration root under the Commitment Model and Hash Profile.
`configuration_state` is the complete authorized configuration snapshot.
`configuration_state_summary` omits the complete values and is used by configuration-state events.
`configuration_input` is the value delivered through startup and live-reconfiguration boundaries.

## References

### Normative

- LOGOS-MODULE-INTERFACE -- CDDL schema conventions, C ABI mapping, and Logos deterministic CBOR.
- LOGOS-MODULE-COMMITMENT-MODEL -- Schema and typed-value identity.
- LOGOS-MODULE-HASH-PROFILE -- Schema and value commitment construction.
- LOGOS-MODULE-RUNTIME -- Module-instance lifecycle, Runtime Control, concurrency, and readiness.

### Informative

- LOGOS-MODULE-SYSTEM-BCP -- Complete module-system composition and code-generation guidance.
- LOGOS-MODULE-PACKAGE-MANAGER -- Packaged schema and default acquisition.
- LOGOS-MODULE-LOADER -- Local implementation realization and startup handoff.
- LOGOS-MODULE-CAPABILITY-AUTHORITY -- Method-level authority and audit integration.
- LOGOS-MODULE-SECURITY-CONSIDERATIONS -- Configuration threat analysis and hardening guidance.

## Copyright

Copyright and related rights waived via
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
