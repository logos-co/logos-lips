# SERVICE-DECLARATION-PROTOCOL

| Field | Value |
| --- | --- |
| Name | Service Declaration Protocol |
| Slug | 87 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors | Mehmet Gonen <mehmet@logos.co>, Daniel Sanchez Quiros <danielsq@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Thomas Lavaur <thomas@logos.co>, Gusto Bacvinka <augustinas@logos.co>, David Rusu <davidrusu@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-service-declaration-protocol.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-09 |
| 1.1.0 | [RFC] Remove Concept of a Session | 2026-06-22 |
| 1.2.0 | [RFC] Per-service uniqueness of `provider_id` and `zk_id` | 2026-07-08 |
| 1.3.0 | Length-prefix the `locators` list in the `declaration_id` preimage | 2026-07-30 |
| 1.4.0 | [RFC] One canonical encoding for `ServiceType` and `Locator` | 2026-08-14 |
| 1.4.1 | Replaced the `uint64` width given to the `epoch` fields with a reference to [`EpochNumber`](cryptarchia-v1-protocol.md#epoch), which is 32 bits | 2026-08-25 |
| 1.4.2 | Renamed locked notes into service notes: `locked_note_id` becomes `service_note_id` in the declaration and withdraw messages and in `DeclarationInfo` | 2026-08-27 |
| 1.4.3 | Identifier uniqueness covers every stored declaration, not only activated ones, matching the implementation | 2026-09-01 |
| 1.5.0 | Defined `active` as the epoch of the block that contained the latest accepted active message, initialised to `created + 2`, and `withdraw_at` as the epoch at which the node stops providing the service, matching the implementation. Added the participant-set exclusion rule and [Message Timing](#message-timing) | 2026-09-02 |
| 1.6.0 | [RFC] The `zk_id` identifies a declaration; the derived `declaration_id` is removed | 2026-09-03 |

# Introduction

This document defines a mechanism enabling validators to declare their participation in specific protocols that require a known and agreed-upon list of participants. One example of this is the Blend Network. We create a single repository of identifiers which is used to establish secure communication between validators and provide services. Before being admitted to the repository, the validator proves that it locked at least a minimum stake through a service note.

## Requirements

The requirements for the protocol are defined as follows:

- A declaration must be backed by a confirmation that the sender of the declaration owns a certain value of the stake.
- A declaration is valid until it is withdrawn or is not actively used for a service-specific amount of time.

# Overview

The SDP enables nodes to declare their eligibility to provide a specific service in the system, and withdraw their declarations.

## Protocol

The protocol defines the following actions:

- **Declare:** A node sends a declaration that confirms its willingness to provide a specific service, which is confirmed by locking a stake above a certain threshold in a service note.
- **Active:** A node marks that its participation in the protocol is active according to the service-specific activity logic. This action enables the protocol to monitor the node’s activity. We utilize this as a non-intrusive differentiator of node activity. It is crucial to exclude inactive nodes from the active set, as it enhances the stability of services.
- **Withdraw:** A node withdraws its declaration and stops providing a service.

The logic of the protocol is straightforward.

1. A node sends a declaration message for a specific service and proves it has a minimum stake.
2. The declaration is registered on the Ledger, and the node can commence its service according to the service-specific service logic.
3. After a service-specific service-providing time, the node confirms its activity.
4. The node must confirm its activity with a service-specific minimum frequency; otherwise, its declaration is inactive.
5. The node sends a withdrawal message. It provides the service through the withdrawal epoch. Its declaration is removed and its service note released two epochs later.

> The protocol messages are subject to a finality that means messages become part of the immutable ledger after a delay. The delay at which it happens is defined by the consensus. Therefore, the protocol’s progress must be tracked from the perspective of the latest finalized block, not the tip of the chain. Otherwise, the protocol and services using it would need to handle chain reorganizations, which we must avoid due to their potential to break services. Hence, the services must use a snapshot from a fully finalized epoch: `finalized_epoch = current_epoch - 2`. For more details about finalization, refer to [Cryptarchia Protocol](cryptarchia-v1-protocol.md).

# Construction

In this section, we present the main constructions of the protocol. First, we start with data definitions. Second, we describe the protocol actions. Finally, we present part of the Bedrock Mantle design responsible for storing and processing SDP-related messages and data.

## Data

In this section, we discuss and define data types, messages, and their storage.

### **Service Types**

We define the following service type:

- `BN`: for Blend Network service.

```python
class ServiceType(Enum):
    BN=0 # Blend Network
```

A declaration can be generated for any of the services above. Any declaration that is not one of the above must be rejected. The number of services might grow in the future.

Each service type is assigned a one-byte discriminant, given by the enum value above. This byte is the canonical encoding of a `ServiceType` and is used wherever a `ServiceType` is serialized or hashed: the transaction wire form ([Mantle Transaction Encoding](mantle-transaction-encoding.md)) and the reward `op_id` preimage ([Service Reward Distribution](bedrock-service-reward-distribution.md)).

### Minimum Stake

The minimum stake is a global value that defines the minimum stake a node must have to perform any service.

The `MinStake` is a structure that holds the value of the stake `stake_threshold` and the `epoch`, which is an epoch number at which the threshold was set; it is an [`EpochNumber`](cryptarchia-v1-protocol.md#epoch).

```python
class MinStake:
    stake_threshold: StakeThreshold
    epoch: EpochNumber
```

The `stake_thresholds` is a structure aggregating all defined `MinStake` values.

```python
stake_thresholds: list[MinStake]
```

For more information on how the minimum stake is calculated, please refer to the [\[Analysis\] Static Minimum Stake Estimation for Service Declaration Protocol](analysis-static-minimum-stake-estimation-for-service-declaration-protocol.md).

### **Service Parameters**

The service parameters structure defines the parameters set necessary for correctly handling interaction between the protocol and services. Each of the service types defined above must be mapped to a set of the following parameters:

- `inactivity_period` defines the number of epochs after the epoch recorded in `active` for which the declaration remains active; after that, it is inactive and excluded from the service's participant set in the same way as a withdrawn declaration ([**Withdraw**](#withdraw)). A value of `2 + k` tolerates `k` consecutive missed reports ([Message Timing](#message-timing)). Any value below 2 excludes every declaration.
- `epoch` defines the epoch number at which the parameter was set; it is an [`EpochNumber`](cryptarchia-v1-protocol.md#epoch).

```python
class ServiceParameters:
    inactivity_period: NumberOfEpochs
    epoch: EpochNumber
```

The `parameters` is a structure aggregating all defined `ServiceParameters` values.

```python
parameters: list[ServiceParameters]
```

### Snapshots

At the start of epoch $`n`$, each node takes a snapshot of the SDP registry at the last block from the finalized epoch.
Each snapshot updates the common view of the registry. Changes to the declaration registry take effect with up to a two-epoch delay: messages sent during epoch `n` are included in the next snapshot (for epoch `n+2`).

Epochs 0 and 1 read the snapshot at the genesis block, because the chain has not yet progressed far enough to provide a later finalized block. While at epoch 2, the last block of epoch 0 is read, and so forth according to the above logic.

### Message Timing

The tables below trace each SDP message from the epoch `e` of the block that contained it. Reward timing follows the [Service Reward Distribution Protocol](bedrock-service-reward-distribution.md).

#### Declaration message

| Epoch | What happens |
| --- | --- |
| `e` | The message is included and the declaration is stored, with `created = e`. |
| `e+1` | The declaration is in no snapshot; the node does not provide the service. |
| `e+2` | The first snapshot containing the declaration is taken; the node starts providing the service. |
| `e+3` | The node's first report is included; `active = e+3`. |
| `e+4` | The epoch-`e+2` reward is distributed in the first block. |

#### Active message

| Epoch | What happens |
| --- | --- |
| `e-1` | The node provides the service. |
| `e` | The message is included, attesting to epoch `e-1`; on acceptance, `active = e`. |
| `e+1` | The epoch-`e-1` reward is distributed in the first block. |
| `e+2` | The report is included in a snapshot for the first time. |

At any epoch `n`, the most recent report a snapshot can contain was included in epoch `n-2` and attests to epoch `n-3`.

#### Withdraw message

| Epoch | What happens |
| --- | --- |
| `e` | The message is included, with `withdraw_at = e+2`. |
| `e+1` | The node is in the participant set (`n < withdraw_at`) and provides the service. It reports its epoch-`e` activity. |
| `e+2` | Every service excludes the declaration (`n >= withdraw_at`). The epoch-`e` reward is distributed and the declaration is removed in the first block ([SDP Epoch Finalization](bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization)). |

### Identifiers

We define the following set of identifiers which are used for service-specific cryptographic operations:

- `provider_id`: used to sign the SDP messages and to establish secure links between validators; it is `Ed25519PublicKey`.
- `zk_id`: used for zero-knowledge operations by the validator that includes rewarding ([Zero Knowledge Signature Scheme (ZkSignature)](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature)).

### **Locators**

A `Locator` is the address of a validator which is used to establish secure communication between validators. It follows the [multiaddr addressing scheme from libp2p](https://docs.libp2p.io/concepts/fundamentals/addressing/), but it must contain only the location part and must not contain the node identity (`peer_id`).

The `provider_id` must be used as the node identity. Therefore, the `Locator` must be completed by adding the `provider_id` at the end of it, which makes the `Locator` usable in the context of libp2p.

The canonical form of a `Locator` is the multiaddr **binary (byte) form**. Wherever a `Locator` is serialized — the transaction wire form ([Mantle Transaction Encoding](mantle-transaction-encoding.md)) — its binary form is used. The human-readable string form (e.g. `/ip4/203.0.113.10/tcp/4001`) is presentational only and must never appear in an encoding.

The length of the binary form of a `Locator` is restricted to 329 bytes.

**The canonical form makes deterministic ID generation work consistently.** The binary form carries no letter case and no textual shorthand, so two equal multiaddrs always share one byte representation; the string-form ambiguities (case, implicit defaults) cannot arise. Implementations that accept the string form as input must parse it into the binary form before any serialization or hashing, and every part of the address must be explicit (no implicit defaults).

The canonical form makes a single `Locator` unambiguous, but it does not make a *list* of them unambiguous. The byte form of a multiaddr is self-describing, so concatenating two `Locator`s yields the byte form of a single longer one: `[/ip4/203.0.113.10/tcp/4001]` and `[/ip4/203.0.113.10, /tcp/4001]` are the same byte string. A list of `Locator`s must therefore be serialized as the `Locators` production of the [Mantle Transaction Encoding](mantle-transaction-encoding.md#sdp-operations): prefixed with its element count and with each element prefixed by its byte length.

### **Declaration Message**

The construction of the declaration message is as follows.

```python
class DeclarationMessage:
    service_type: ServiceType
    locators: list[Locator]
    provider_id: Ed25519PublicKey
    zk_id: ZkPublicKey
    service_note_id: NoteId
```

The `locators` list must be non-empty and its length must be limited to reduce the potential for abuse. Therefore, the length of the list cannot be longer than 8.

The message must be signed by the `provider_id` key to prove ownership of the key that is used for network-level authentication of the validator.

The `service_note_id` points to the service note the validator puts up as collateral.

The message is also signed by the `zk_id` key.

### **Declaration Storage**

Only valid declaration messages can be stored on the ledger. A declaration covers exactly one service and is identified by the `zk_id` of the validator that created it. We define the `DeclarationInfo` as follows:

```python
class DeclarationInfo:
    service: ServiceType
    provider_id: Ed25519PublicKey
    locators: list[Locator]
    service_note_id: NoteId
    created: EpochNumber
    active: EpochNumber
    withdraw_at: EpochNumber | None
    nonce: Nonce
```

Where:

- `service` defines the service type of the declaration;
- `provider_id` is the `Ed25519PublicKey` the validator signs its messages with;
- `locators` is a copy of the `locators` from the `DeclarationMessage`;
- `service_note_id` is the `NoteId` of the note that meets the minimum stake threshold;
- `created` is the epoch of the block that contained the declaration;
- `active` is the epoch of the block that contained the latest accepted active message, initialised to `created + 2` ([Message Timing](#message-timing));
- `withdraw_at` is the epoch at which the node stops providing the service ([**Withdraw**](#withdraw)), and is `None` until the declaration is withdrawn;
- `nonce` is 0 for the declaration message, and increases monotonically with every message sent for the `zk_id`.

All `DeclarationInfo` entries are held in `declarations`, indexed by `zk_id`.

```python
declarations: dict[ZkPublicKey, DeclarationInfo]
```

### Identifier Uniqueness

Within `declarations`, each of the following is bound to at most one `DeclarationInfo`:

- the `zk_id`;
- the `provider_id`;
- the `service_note_id`.

An identifier becomes available for reuse once its declaration has been removed (see [**Withdraw**](#withdraw)).

### Active Set

The **active set** for an epoch $`n`$ is derived from the snapshot read for that epoch ([Snapshots](#snapshots)) by keeping the declarations for which both of the following hold:

- activity has been reported recently enough: `active + inactivity_period >= n`;
- the withdrawal has not taken effect: `withdraw_at` is `None`, or `n < withdraw_at`.

Both conditions are evaluated against the epoch $`n`$ the set is being derived for, not against the epoch the snapshot was taken in.

### Active Message

The construction of the active message is as follows:

```python
class ActiveMessage:
    zk_id: ZkPublicKey
    nonce: Nonce
    metadata: Metadata
```

where `metadata` is service-specific node activeness metadata, encoded as the `Metadata` production of the [Mantle Transaction Encoding](mantle-transaction-encoding.md#sdp-operations).

The message must be signed by the `zk_id` key.

The `nonce` must increase monotonically by every message sent for the `zk_id`.

An active message attests to a single past epoch during which the node provided the service. The service defines when the message may be sent (see [Active Message](blend-protocol.md#active-message) for the Blend Network).

The `metadata` layout is service-defined; the SDP does not parse it.

### Withdraw Message

The construction of the withdraw message is as follows:

```python
class WithdrawMessage:
    zk_id: ZkPublicKey
    nonce: Nonce
```

The message must be signed by the `zk_id` key.

The `nonce` must increase monotonically by every message sent for the `zk_id`.

### Indexing

Every event must be correctly indexed to enable lighter synchronization of the changes. Therefore, we index every `zk_id` according to `EventType`, `ServiceType`, and `Epoch`. Where `EventType = { "created", "active", "withdrawn" }` follows the type of the message.

The `Epoch` key is the epoch of the block that contained the message, for all three event types.

```python
events = {
    event_type: {
        service_type: {
            epoch: {
                declarations: list[zk_id]
            }
        }
    }
}
```

## Protocol

### Declare

The Declare action associates a validator with a service it wants to provide. It requires sending a valid `DeclarationMessage` (as defined in [**Declaration Message**](#declaration-message)), which is then processed (as defined below) and stored (as defined in [**Declaration Storage**](#declaration-storage)).

The declaration message is considered valid when all of the following are met:

- The `service_note_id` names an unspent note whose value meets the minimum stake threshold.
- The `zk_id`, the `service_note_id` and the `provider_id` are each unbound ([Identifier Uniqueness](#identifier-uniqueness)).
- The sender holds the private key corresponding to the `provider_id`.
- The `locators` list is non-empty and not longer than 8 entries.

If all of the above conditions are fulfilled, then the declaration is stored on the ledger under its `zk_id`; otherwise, the message is discarded.

### Active

The Active action marks a provider as actively providing its service. It requires sending a valid `ActiveMessage` (as defined in [Active Message](#active-message)), which is relayed to the service-specific node activity logic (as indicated by the service type in [Common SDP Structures](bedrock-v1.1-mantle-specification.md#common-sdp-structures)).

The Active action updates the `active` value of the `DeclarationInfo`. A declaration considered inactive is not removed from the registry, and an accepted active message makes it active again. A declaration is removed only by withdrawal ([**Withdraw**](#withdraw)); a removed declaration cannot become active again.

The SDP active action logic is:

1. A node sends an `ActiveMessage` transaction.
2. The `ActiveMessage` is verified by the SDP logic:
    1. The `zk_id` returns an existing `DeclarationInfo`.
    2. The transaction containing `ActiveMessage` is signed by the `zk_id`.
    3. The `nonce` increases monotonically.
3. If any of these conditions fail, discard the message and stop processing.
4. The message is processed by the service-specific activity logic, together with the epoch of the block that contained the message.
5. If the service-specific activity logic rejects the message, discard the message and stop processing.
6. The `active` field of the `DeclarationInfo` is set to that epoch.

An active message is valid only while the current epoch is below `withdraw_at` (see [**Withdraw**](#withdraw)).

### **Withdraw**

The Withdraw action withdraws a service declaration. It requires sending a valid `WithdrawMessage` (as defined in [Withdraw Message](#withdraw-message)). The withdrawal marks the intent to stop providing the service.

Let `e` be the epoch of the block that contained the `WithdrawMessage`; `withdraw_at` records `e+2` ([Snapshots](#snapshots)). A declaration whose `withdraw_at` an epoch has reached is excluded from that epoch's [Active Set](#active-set).

The node provides the service through epoch `withdraw_at - 1`; its last rewardable epoch is `withdraw_at - 2`. The declaration is removed and its service note released at epoch `withdraw_at` ([SDP Epoch Finalization](bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization)).

The logic of the withdraw action is:

1. A node sends a `WithdrawMessage` transaction.
2. The `WithdrawMessage` is verified by the SDP logic.
    1. The `zk_id` returns an existing `DeclarationInfo`.
    2. The transaction containing `WithdrawMessage` is signed by the `zk_id`.
    3. The `withdraw_at` of the `DeclarationInfo` is `None`.
    4. The `nonce` increases monotonically.
3. If any of the above is not correct, then discard the message and stop.
4. Set the `withdraw_at` of the `DeclarationInfo` to the current epoch number plus two.
5. At epoch `withdraw_at`, right after the final reward is paid out, the Mantle epoch finalization step removes the `DeclarationInfo` and releases its `service_note_id` ([SDP Epoch Finalization](bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization)).

### Query

The protocol must enable querying the ledger in at least the following manner:

- `GetAllProviderId(epoch)`, returns all `provider_id`s associated with the `epoch`.
- `GetAllProviderIdSince(epoch)`, returns all `provider_id`s since the `epoch`.
- `GetAllDeclarationInfo(epoch)`, returns all `DeclarationInfo` entries associated with the `epoch`.
- `GetAllDeclarationInfoSince(epoch)`, returns all `DeclarationInfo` entries since the `epoch`.
- `GetDeclarationInfo(zk_id)`, returns the `DeclarationInfo` entry identified by the `zk_id`.
- `GetDeclarationInfo(provider_id)`, returns the `DeclarationInfo` entry whose `provider_id` matches.
- `GetAllServiceParameters(epoch)`, returns all entries of the `ServiceParameters` store for the requested `epoch`.
- `GetAllServiceParametersSince(epoch)`, returns all entries of the `ServiceParameters` store since the requested `epoch`.
- `GetServiceParameters(service_type, epoch)`, returns the service parameter entry from the `ServiceParameters` store of a `service_type` for a specified `epoch`.
- `GetMinStake(epoch)`, returns the `MinStake` structure at the requested `epoch`.
- `GetMinStakeSince(epoch)`, returns a set of `MinStake` structures since the requested `epoch`.

The query must return an error if the requested information is not available.

The list of queries may be extended.

Every query must return information for a finalized state only.

## Mantle and ZK Proofs

For more information about Mantle and ZK proofs, please refer to [Mantle](bedrock-v1.1-mantle-specification.md).

# Default Service Parameters

## Blend Network

```python
class BlendNetworkServiceParameters:
    inactivity_period: 2
    epoch: 0
```
