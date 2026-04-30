# BEDROCK-SERVICE-DECLARATION-PROTOCOL

| Field | Value |
| --- | --- |
| Name | Bedrock Service Declaration Protocol |
| Slug | 87 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@status.im> |
| Contributors | Mehmet Gonen <mehmet@status.im>, Daniel Sanchez Quiros <danielsq@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Thomas Lavaur <thomaslavaur@status.im>, Gusto Bacvinka <augustinas@status.im>, David Rusu <davidrusu@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Service Declaration Protocol (SDP),
a mechanism enabling validators to declare their participation
in specific protocols that require a known and agreed-upon list of participants.
Examples include Data Availability (DA) and the Blend Network.
SDP creates a single repository of identifiers
used to establish secure communication between validators and provide services.
Before being admitted to the repository,
a validator proves that it has locked at least a minimum stake.

**Keywords:** service declaration, validator, stake, declaration, withdrawal,
session, minimum stake, provider, locator, Blend Network, Data Availability

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Definitions

<!-- markdownlint-disable MD013 -->

| Terminology | Description |
| ----------- | ----------- |
| SDP | Service Declaration Protocol for node participation in Nomos Services. |
| Declaration | A message confirming a validator's willingness to provide a specific service. |
| Service Type | The type of service being declared (e.g., BN for Blend Network, DA for Data Availability). |
| Minimum Stake | The minimum amount of stake a node MUST lock to declare for a service. |
| Session | A fixed-length window defined per service via `session_length`. |
| Lock Period | The minimum time during which a declaration cannot be withdrawn. |
| Inactivity Period | The maximum time during which an activation message MUST be sent. |
| Retention Period | The time after which a declaration can be safely deleted. |
| Provider ID | An Ed25519 public key used to sign SDP messages and establish secure links. |
| ZK ID | A public key used for zero-knowledge operations including rewarding. |
| Locator | The network address of a validator following the multiaddr scheme. |
| Declaration ID | A unique identifier for a declaration, computed as a hash. |

<!-- markdownlint-enable MD013 -->

## Background

In many protocols, a known and agreed-upon list of participants is required.
Examples include Data Availability and the Blend Network.
SDP enables nodes to declare their eligibility to serve a specific service
and withdraw their declarations.

### Requirements

The protocol requirements are:

- A declaration MUST be backed by confirmation
  that the sender owns a certain value of stake.
- A declaration is valid until it is withdrawn
  or is not used for a service-specific amount of time.

### Actions Overview

The protocol defines the following actions:

- **Declare**: A node sends a declaration confirming its willingness
  to provide a specific service, backed by locking a threshold of stake.
- **Active**: A node marks that its participation in the protocol is active
  according to the service-specific activity logic.
  This action enables the protocol to monitor the node's activity.
  It is crucial to exclude inactive nodes from the set of active nodes,
  as it enhances the stability of services.
- **Withdraw**: A node withdraws its declaration and stops providing a service.

### Protocol Flow

1. A node sends a declaration message for a specific service
   and proves it has a minimum stake.

1. The declaration is registered on the blockchain ledger,
   and the node can commence its service
   according to the service-specific logic.

1. After a service-specific service-providing time, the node confirms its activity.

1. The node MUST confirm its activity with a service-specific minimum frequency;
   otherwise, its declaration is inactive.

1. After the service-specific locking period,
   the node can send a withdrawal message,
   and its declaration is removed from the blockchain ledger
   (after the necessary retention period),
   meaning the node will no longer provide the service.

> **Note**: Protocol messages are subject to finality,
> meaning messages become part of the immutable ledger after a delay.
> The delay is defined by the consensus.

## Protocol Specification

### Service Types

The following services are defined for service declaration:

- `BN`: Blend Network service.
- `DA`: Data Availability service.

```python
class ServiceType(Enum):
    BN = "BN"  # Blend Network
    DA = "DA"  # Data Availability
```

A declaration can be generated for any of the services above.
Any declaration that is not one of the above MUST be rejected.
The number of services MAY grow in the future.

### Minimum Stake

The minimum stake is a global value
defining the minimum stake a node MUST have to perform any service.

The `MinStake` structure holds the value of the stake `stake_threshold`
and the block number at which it was set (`timestamp`).

```python
class MinStake:
    stake_threshold: StakeThreshold
    timestamp: BlockNumber
```

The `stake_thresholds` structure aggregates all defined `MinStake` values:

```python
stake_thresholds: list[MinStake]
```

### Service Parameters

The service parameters structure defines the parameters necessary
for handling interaction between the protocol and services.
Each service type MUST be mapped to the following parameters:

- `session_length`: The session length expressed as the number of blocks.
  Sessions are counted from block `timestamp`.
- `lock_period`: The minimum time (as a number of sessions)
  during which the declaration cannot be withdrawn.
  This time MUST include the period necessary for finalizing the declaration
  and provision of a service for at least a single session.
  It can be expressed as blocks by multiplying by `session_length`.
- `inactivity_period`: The maximum time (as a number of sessions)
  during which an activation message MUST be sent;
  otherwise, the declaration is considered inactive.
  It can be expressed as blocks by multiplying by `session_length`.
- `retention_period`: The time (as a number of sessions)
  after which the declaration can be safely deleted
  by the Garbage Collection mechanism.
  It can be expressed as blocks by multiplying by `session_length`.
- `timestamp`: The block number at which the parameter was set.

```python
class ServiceParameters:
    session_length: NumberOfBlocks
    lock_period: NumberOfSessions
    inactivity_period: NumberOfSessions
    retention_period: NumberOfSessions
    timestamp: BlockNumber
```

The `parameters` structure aggregates all defined `ServiceParameters` values:

```python
parameters: list[ServiceParameters]
```

### Session Tracking

A session is a fixed-length window defined per service
via `ServiceParameters.session_length`.
The session length MUST be at least `k`, the consensus finality parameter.

Session numbers start at 0 and are computed as follows:

```python
def get_session_number(current_block_number, service_parameters):
    return current_block_number // service_parameters.session_length
```

At the start of session `n`,
each node takes a snapshot (`get_snapshot_at_block`) of the SDP registry
at a specified block height from the finalized part of the chain:

```python
def get_session_snapshot(session_number, service_parameters):
    if session_number < 2:
        # Take the genesis block for the first two sessions
        return get_snapshot_at_block(0)
    # Take the last block of the previous session for the rest
    return get_snapshot_at_block(
        (session_number - 1) * service_parameters.session_length - 1
    )
```

The function `get_snapshot_at_block(block_number)` returns the state
of the SDP registry at `block_number`,
including state changes made by that block.
This snapshot defines the declaration state for the session—
each snapshot updates the common view of the registry.
Changes to the declaration registry take effect with a one-session delay:
messages sent during session `n` are included
in the next snapshot (for session `n+1`).

Sessions 0 and 1 read the snapshot at block 0,
because the chain has not yet progressed far enough
to provide a later finalized block.

### Identifiers

The following identifiers are used for service-specific cryptographic operations:

- `provider_id`: Used to sign SDP messages
  and establish secure links between validators.
  It is an `Ed25519PublicKey`.
- `zk_id`: Used for zero-knowledge operations by the validator,
  including rewarding (Zero Knowledge Signature Scheme).

### Locators

A `Locator` is the address of a validator
used to establish secure communication between validators.
It follows the multiaddr addressing scheme from libp2p,
but it MUST contain only the location part
and MUST NOT contain the node identity (`peer_id`).

The `provider_id` MUST be used as the node identity.
Therefore, the `Locator` MUST be completed
by adding the `provider_id` at the end of it,
making the `Locator` usable in the context of libp2p.

The length of the `Locator` is restricted to 329 characters.

The syntax of every `Locator` entry MUST be validated.

Common formatting of every `Locator` MUST be applied
to maintain its unambiguity and make deterministic ID generation work consistently.
The `Locator` MUST at least contain only lowercase letters
and every part of the address MUST be explicit (no implicit defaults).

### Declaration Message

The construction of the declaration message is as follows:

```python
class DeclarationMessage:
    service_type: ServiceType
    locators: list[Locator]
    provider_id: Ed25519PublicKey
    locked_note_id: NoteId
    zk_id: ZkPublicKey
```

The `locators` list length MUST be limited to reduce the potential for abuse.
The length of the list MUST NOT be longer than 8.

The message MUST be signed by the `provider_id` key
to prove ownership of the key used for network-level authentication.

The `locked_note_id` points to a locked note
used for minimum stake threshold verification purposes.

The message MUST also be signed by the `zk_id` key.

### Declaration Storage

Only valid declaration messages can be stored on the blockchain ledger.
The `DeclarationInfo` structure is defined as follows:

```python
class DeclarationInfo:
    service: ServiceType
    provider_id: Ed25519PublicKey
    locked_note_id: NoteId
    zk_id: ZkPublicKey
    locators: list[Locator]
    created: BlockNumber
    active: BlockNumber
    withdrawn: BlockNumber
    nonce: Nonce
```

Where:

- `service`: The service type of the declaration.
- `provider_id`: An `Ed25519PublicKey` used to sign the message by the validator.
- `locked_note_id`: A `NoteId` used for minimum stake threshold verification.
- `zk_id`: Used for zero-knowledge operations including rewarding.
- `locators`: A copy of the locators from the `DeclarationMessage`.
- `created`: The block number of the block that contained the declaration.
- `active`: The latest block number for which the active message was sent
  (set to `created` by default).
- `withdrawn`: The block number for which the service declaration was withdrawn
  (set to 0 by default).
- `nonce`: MUST be set to 0 for the declaration message
  and MUST increase monotonically by every message sent for the `declaration_id`.

The `declaration_id` (of type `DeclarationId`)
is the unique identifier of `DeclarationInfo`,
calculated as a hash of the concatenation of
`service`, `provider_id`, `zk_id`, and `locators`.
The hash function implementation is blake2b using 256 bits of output:

```python
declaration_id = Hash(service || provider_id || zk_id || locators)
```

The `declaration_id` is not stored as part of `DeclarationInfo`
but is used to index it.
All `DeclarationInfo` references are stored in `declarations`
and are indexed by `declaration_id`:

```python
declarations: list[declaration_id]
```

### Active Message

The construction of the active message is as follows:

```python
class ActiveMessage:
    declaration_id: DeclarationId
    nonce: Nonce
    metadata: Metadata
```

Where `metadata` is service-specific node activeness metadata.

The message MUST be signed by the `zk_id` key
associated with the `declaration_id`.

The `nonce` MUST increase monotonically
by every message sent for the `declaration_id`.

### Withdraw Message

The construction of the withdraw message is as follows:

```python
class WithdrawMessage:
    declaration_id: DeclarationId
    locked_note_id: NoteId
    nonce: Nonce
```

The message MUST be signed by the `zk_id` key from the `declaration_id`.

The `locked_note_id` is a `NoteId`
that was used for minimum stake threshold verification purposes
and will be unlocked after withdrawal.

The `nonce` MUST increase monotonically
by every message sent for the `declaration_id`.

### Indexing

Every event MUST be correctly indexed
to enable lighter synchronization of the changes.
Events are indexed by `EventType`, `ServiceType`, and `Timestamp`,
where `EventType = { "created", "active", "withdrawn" }`
corresponds to the type of message:

```python
events = {
    event_type: {
        service_type: {
            timestamp: {
                declarations: list[declaration_id]
            }
        }
    }
}
```

## Protocol Actions

### Declare

The Declare action associates a validator with a service it wants to provide.
It requires sending a valid `DeclarationMessage`,
which is then processed and stored.

The declaration message is considered valid when all of the following are met:

- The sender meets the stake requirements and its `locked_note_id` is valid.
- The `declaration_id` is unique.
- The sender knows the secret behind the `provider_id` identifier.
- The length of the `locators` list MUST NOT be longer than 8.
- The `nonce` increases monotonically.

If all conditions are fulfilled,
the message is stored on the blockchain ledger;
otherwise, the message is discarded.

### Active

The Active action enables marking the provider as actively providing a service.
It requires sending a valid `ActiveMessage`,
which is relayed to the service-specific node activity logic.

The Active action updates the `active` value of the `DeclarationInfo`,
which also activates inactive (but not expired) providers.

The SDP active action logic is:

1. A node sends an `ActiveMessage` transaction.

1. The `ActiveMessage` is verified by the SDP logic:
   1. The `declaration_id` returns an existing `DeclarationInfo`.
   1. The transaction containing `ActiveMessage` is signed by the `zk_id`.
   1. The `withdrawn` from the `DeclarationInfo` is set to zero.
   1. The `nonce` increases monotonically.

1. If any of these conditions fail, discard the message and stop processing.

1. The message is processed by the service-specific activity logic
   alongside the `active` value indicating the period
   since the last active message was sent.
   The `active` value comes from the `DeclarationInfo`.

1. If the service-specific activity logic approves the node active message,
   then the `active` field of the `DeclarationInfo`
   is set to the current block height.

### Withdraw

The Withdraw action enables withdrawal of a service declaration.
It requires sending a valid `WithdrawMessage`.
The withdrawal cannot happen before the end of the locking period,
defined as the number of blocks counted since `created`.
This lock period is stored as `lock_period` in the Service Parameters.

The logic of the withdraw action is:

1. A node sends a `WithdrawMessage` transaction.

1. The `WithdrawMessage` is verified by the SDP logic:
   1. The `declaration_id` returns an existing `DeclarationInfo`.
   1. The transaction containing `WithdrawMessage` is signed by the `zk_id`.
   1. The `withdrawn` from `DeclarationInfo` is set to zero.
   1. The `nonce` increases monotonically.

1. If any of the above is not correct, discard the message and stop.

1. Set the `withdrawn` from the `DeclarationInfo` to the current block height.

1. Unlock the stake (release the `locked_note_id`).

### Garbage Collection

The protocol requires a garbage collection mechanism
that periodically removes unused `DeclarationInfo` entries.

The logic of garbage collection is:

For every `DeclarationInfo` in the `declarations` set,
remove the entry if either:

1. The entry is past the retention period:
   `withdrawn + (retention_period * session_length) < current_block_height`.

1. The entry is inactive beyond the inactivity and retention periods:
   `active + (inactivity_period + retention_period) * session_length < current_block_height`.

### Query Interface

The protocol MUST enable querying the blockchain ledger
with at least the following queries:

- `GetAllProviderId(timestamp)`:
  Returns all `provider_id`s associated with the timestamp.
- `GetAllProviderIdSince(timestamp)`:
  Returns all `provider_id`s since the timestamp.
- `GetAllDeclarationInfo(timestamp)`:
  Returns all `DeclarationInfo` entries associated with the timestamp.
- `GetAllDeclarationInfoSince(timestamp)`:
  Returns all `DeclarationInfo` entries since the timestamp.
- `GetDeclarationInfo(provider_id)`:
  Returns the `DeclarationInfo` entry identified by the `provider_id`.
- `GetDeclarationInfo(declaration_id)`:
  Returns the `DeclarationInfo` entry identified by the `declaration_id`.
- `GetAllServiceParameters(timestamp)`:
  Returns all entries of the `ServiceParameters` store for the timestamp.
- `GetAllServiceParametersSince(timestamp)`:
  Returns all entries of the `ServiceParameters` store since the timestamp.
- `GetServiceParameters(service_type, timestamp)`:
  Returns the service parameter entry for a `service_type` at a timestamp.
- `GetMinStake(timestamp)`:
  Returns the `MinStake` structure at the requested timestamp.
- `GetMinStakeSince(timestamp)`:
  Returns a set of `MinStake` structures since the requested timestamp.

The query MUST return an error
if the retention period for the declaration has passed
and the requested information is not available.

The list of queries MAY be extended.

Every query MUST return information for a finalized state only.

## Security Considerations

### Stake Requirements

Validators MUST lock a minimum stake before declaring for a service.
This prevents Sybil attacks
by ensuring economic commitment to the network.

### Message Authentication

All SDP messages MUST be cryptographically signed:

- `DeclarationMessage` MUST be signed by both `provider_id` and `zk_id`.
- `ActiveMessage` MUST be signed by `zk_id`.
- `WithdrawMessage` MUST be signed by `zk_id`.

### Nonce Monotonicity

The `nonce` MUST increase monotonically for each `declaration_id`
to prevent replay attacks.

### Locator Validation

The syntax of every `Locator` entry MUST be validated
to prevent malformed addresses from being registered.
The length restriction of 329 characters
and the limit of 8 locators per declaration
prevent resource exhaustion attacks.

## References

### Normative

- [BEDROCK-MANTLE-SPECIFICATION][mantle] - Mantle Transaction and Operation specification

### Informative

- [Service Declaration Protocol][origin-ref] - Original specification document
- [libp2p multiaddr][multiaddr] - Multiaddr addressing scheme

[mantle]: https://nomos-tech.notion.site/v1-1-Mantle-Specification-269261aa09df80dda501f568697930fd
[origin-ref]: https://nomos-tech.notion.site/Service-Declaration-Protocol-1fd261aa09df819ca9f8eb2bdfd4ec1d
[multiaddr]: https://github.com/multiformats/multiaddr

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
