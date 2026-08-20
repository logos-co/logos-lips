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
| 1.4.0 | [RFC] The `zk_id` identifies a declaration; the derived `declaration_id` is removed | 2026-08-19 |

# Introduction

This document defines a mechanism enabling validators to declare their participation in specific protocols that require a known and agreed-upon list of participants. One example of this is the Blend Network. We create a single repository of identifiers which is used to establish secure communication between validators and provide services. Before being admitted to the repository, the validator proves that it locked at least a minimum stake.

## Requirements

The requirements for the protocol are defined as follows:

- A declaration must be backed by a confirmation that the sender of the declaration owns a certain value of the stake.
- A declaration is valid until it is withdrawn or is not actively used for a service-specific amount of time.

# Overview

The SDP enables nodes to declare their eligibility to provide a specific service in the system, and withdraw their declarations.

## Protocol

The protocol defines the following actions:

- **Declare:** A node sends a declaration that confirms its willingness to provide a specific service, which is confirmed by locking a stake above a certain threshold.
- **Active:** A node marks that its participation in the protocol is active according to the service-specific activity logic. This action enables the protocol to monitor the node’s activity. We utilize this as a non-intrusive differentiator of node activity. It is crucial to exclude inactive nodes from the set of active nodes, as it enhances the stability of services.
- **Withdraw:** A node withdraws its declaration and stops providing a service.

The logic of the protocol is straightforward.

1. A node sends a declaration message for a specific service and proves it has a minimum stake.
2. The declaration is registered on the Ledger, and the node can commence its service according to the service-specific service logic.
3. After a service-specific service-providing time, the node confirms its activity.
4. The node must confirm its activity with a service-specific minimum frequency; otherwise, its declaration is inactive.
5. After the service-specific locking period, the node can send a withdrawal message, and its declaration is removed from the Ledger, which means that the node will no longer provide the service.

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
    BN="BN" # Blend Network
```

A declaration can be generated for any of the services above. Any declaration that is not one of the above must be rejected. The number of services might grow in the future.

### Minimum Stake

The minimum stake is a global value that defines the minimum stake a node must have to perform any service.

The `MinStake` is a structure that holds the value of the stake `stake_threshold` and the `epoch`, which is an epoch number at which the threshold was set; it is `uint64`.

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

- `inactivity_period` defines the maximum time (as a number of epochs) during which an activation message must be sent; otherwise, the declaration is considered inactive. It must be at least 2 epochs long due to finalization reasons.
- `epoch` defines the epoch number at which the parameter was set; it is `uint64`.

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

### Identifiers

We define the following set of identifiers which are used for service-specific cryptographic operations:

- `provider_id`: used to sign the SDP messages and to establish secure links between validators; it is `Ed25519PublicKey`.
- `zk_id`: used for zero-knowledge operations by the validator that includes rewarding ([Zero Knowledge Signature Scheme (ZkSignature)](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature)). It is also the identifier of the declaration itself, as defined in [**Declaration Storage**](#declaration-storage).

### **Locators**

A `Locator` is the address of a validator which is used to establish secure communication between validators. It follows the [multiaddr addressing scheme from libp2p](https://docs.libp2p.io/concepts/fundamentals/addressing/), but it must contain only the location part and must not contain the node identity (`peer_id`).

The `provider_id` must be used as the node identity. Therefore, the `Locator` must be completed by adding the `provider_id` at the end of it, which makes the `Locator` usable in the context of libp2p.

The length of the `Locator` is restricted to 329 characters.

**The common formatting of every** `Locator` **must be applied to maintain its unambiguity, to make deterministic ID generation work consistently.** The `Locator` must at least contain only lowercase letters and every part of the address must be explicit (no implicit defaults).

Canonical formatting makes a single `Locator` unambiguous, but it does not make a *list* of them unambiguous. The byte form of a multiaddr is self-describing, so concatenating two `Locator`s yields the byte form of a single longer one: `[/ip4/203.0.113.10/tcp/4001]` and `[/ip4/203.0.113.10, /tcp/4001]` are the same byte string. A list of `Locator`s must therefore always be serialized as the [Mantle Transaction Encoding](mantle-transaction-encoding.md) defines it, prefixed with its element count and with each element prefixed by its byte length, so that the list is recoverable from its bytes.

### **Declaration Message**

The construction of the declaration message is as follows.

```python
class DeclarationMessage:
    service_type: ServiceType
    locators: list[Locator]
    provider_id: Ed25519PublicKey
    locked_note_id: NoteId
    zk_id: ZkPublicKey
```

The `locators` list must be non-empty and its length must be limited to reduce the potential for abuse. Therefore, the length of the list cannot be longer than 8.

The message must be signed by the `provider_id` key to prove ownership of the key that is used for network-level authentication of the validator.

The `locked_note_id` points to a locked note used for minimum stake threshold verification purposes.

The message is also signed by the `zk_id` key. The `zk_id` becomes the identifier of the resulting declaration, so a message whose `zk_id` is already registered must be rejected (see [**Declaration Storage**](#declaration-storage)).

### **Declaration Storage**

Only valid declaration messages can be stored on the ledger. A declaration covers exactly one service and is identified by the `zk_id` of the validator that created it. We define the `DeclarationInfo` as follows:

```python
class DeclarationInfo:
    service: ServiceType
    provider_id: Ed25519PublicKey
    locators: list[Locator]
    locked_note_id: NoteId
    created: EpochNumber
    active: EpochNumber | None
    withdraw_at: EpochNumber | None
    nonce: Nonce
```

Where:

- `service` defines the service type of the declaration;
- `provider_id` is an `Ed25519PublicKey` used to sign the message by the validator;
- `locators` is a copy of the `locators` from the `DeclarationMessage`;
- `locked_note_id` is a `NoteId` used for minimum stake threshold verification purposes;
- `created` refers to the epoch number of the block that contained the declaration;
- `active` refers to the latest epoch number for which the active message was sent (it is set to `None` by default);
- `withdraw_at` refers to the epoch number for which the service declaration will be withdrawn (it is set to `None` by default);
- The `nonce` must be set to 0 for the declaration message and must increase monotonically by every message sent for the `zk_id`.

All `DeclarationInfo` entries are stored in the `declarations` and are indexed by `zk_id`.

```python
declarations: dict[ZkPublicKey, DeclarationInfo]
```

The `zk_id` is not stored as a field of the `DeclarationInfo` because it is the key under which the entry is held.

A declaration is a self-contained unit: one service, one `zk_id`, one locked note. A validator that provides two services holds two independent declarations, each with its own `zk_id` and its own locked note, and each declared, activated, and withdrawn on its own. Nothing is shared between them except, optionally, the `provider_id`.

### Identifier Uniqueness

Each `zk_id` identifies at most one declaration. This holds structurally rather than by enforcement: the `zk_id` is the key of `declarations`, so there is no derivation under which two entries could carry the same one. A `DeclarationMessage` whose `zk_id` is already registered must be rejected, whichever service it names.

Each `locked_note_id` backs at most one declaration. A note that already collateralizes a declaration must not be offered as collateral again, so the minimum stake is met independently for every service a validator provides rather than a single locked value counting towards several. A `DeclarationMessage` whose `locked_note_id` is already locked must be rejected.

The `provider_id` must be unique in the context of a service: within a given `service`, it must be bound to at most one `DeclarationInfo`. It is scoped this way, rather than across the whole registry, because it is the network identity of the validator, and a validator that provides two services is one peer that may present the same identity in both. Two declarations for the *same* service sharing a `provider_id`, on the other hand, are two validators claiming to be the same peer, and must be rejected.

All three identifiers are held for the entire lifetime of the declaration, and become available for reuse only once it has been removed after its final reward has been paid (see [**Withdraw**](#withdraw)).

The `zk_id` uniqueness is a protocol invariant that the rest of the system builds on, not a convenience. It is the key under which downstream protocols index per-provider state: the [Service Reward Distribution Protocol](bedrock-service-reward-distribution.md) maps a service's epoch rewards by `zk_id` and derives each reward note's position from the ascending order of those `zk_id`s, and the [Proof of Quota](proof-of-quota.md) builds the core Merkle tree over the same values, sorted, one per leaf. Both constructions require the set to be duplicate-free, and neither defines a meaning for a repeated key.

### Active Message

The construction of the active message is as follows:

```python
class ActiveMessage:
    zk_id: ZkPublicKey
    nonce: Nonce
    metadata: Metadata
```

where `metadata` is service-specific node activeness metadata.

The `zk_id` determines the declaration, and the declaration determines the service, so the message does not name a service of its own.

The message must be signed by the `zk_id` key.

The `nonce` must increase monotonically by every message sent for the `zk_id`.

### Withdraw Message

The construction of the withdraw message is as follows:

```python
class WithdrawMessage:
    zk_id: ZkPublicKey
    locked_note_id: NoteId
    nonce: Nonce
```

The message must be signed by the `zk_id` key.

The `locked_note_id` is a `NoteId` that was used for minimum stake threshold verification purposes and will be unlocked after withdrawal. It is the note the declaration locked, since a declaration locks exactly one.

The `nonce` must increase monotonically by every message sent for the `zk_id`.

### Indexing

Every event must be correctly indexed to enable lighter synchronization of the changes. Therefore, we index every `zk_id` according to `EventType`, `ServiceType`, and `Epoch`. Where `EventType = { "created", "active", "withdrawn" }` follows the type of the message.

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

- The sender meets the stake requirements and its `locked_note_id` is valid.
- The `zk_id` is not already registered in `declarations`.
- The `locked_note_id` does not already back another declaration.
- The `provider_id` is not already bound to a declaration for the same `service` (as defined in [Identifier Uniqueness](#identifier-uniqueness)).
- The sender knows the secret behind the `provider_id` identifier.
- The `locators` list is non-empty and not longer than 8 entries.

If all of the above conditions are fulfilled, then the declaration is stored on the ledger under its `zk_id`, with its `nonce` initialised to 0; otherwise, the message is discarded. The `DeclarationMessage` carries no nonce of its own: the sequence starts here and is followed by the active and withdraw messages sent for the same `zk_id`.

### Active

The Active action enables marking the provider as actively providing a service. It requires sending a valid `ActiveMessage` (as defined in [Active Message](#active-message)), which is relayed to the service-specific node activity logic (as indicated by the service type in [Common SDP Structures](bedrock-v1.1-mantle-specification.md#common-sdp-structures)).

The Active action updates the `active` value of the `DeclarationInfo`, which means that it also activates inactive (but not expired) providers.

The SDP active action logic is:

1. A node sends an `ActiveMessage` transaction.
2. The `ActiveMessage` is verified by the SDP logic:
    1. The `zk_id` returns an existing `DeclarationInfo`.
    2. The transaction containing `ActiveMessage` is signed by the `zk_id`.
    3. The `nonce` increases monotonically.
3. If any of these conditions fail, discard the message and stop processing.
4. The message is processed by the service-specific activity logic alongside the `active` value indicating the period since the last active message was sent. The `active` value comes from the `DeclarationInfo`, and the service is the one the declaration was made for.
5. If the service-specific activity logic approves the node active message, then the `active` field of the `DeclarationInfo` is set to the epoch number indicated by metadata.

### **Withdraw**

The withdraw action enables a withdrawal of a service declaration. It requires sending a valid `WithdrawMessage` (as defined in [Withdraw Message](#withdraw-message)). The withdrawal marks the intent to stop providing the service: the node provides the service through the withdrawal epoch `e` and stops afterwards. The `withdraw_at` field records this withdrawal epoch `e`, which is the node's last rewardable epoch. The declaration is removed and its note unlocked at epoch `e+2`, right after the epoch-`e` reward is paid out, by the Mantle epoch finalization step (see [SDP Epoch Finalization](bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization)). Removing the declaration only after its final reward is paid guarantees it is never removed before the payout.

Because a declaration covers one service and locks one note, removing it releases everything it held: the note becomes spendable again, and the `zk_id` and the `provider_id` become available for reuse. A validator withdrawing from one of two services withdraws that service's declaration; the other declaration, and the note it locked, are untouched.

The logic of the withdraw action is:

1. A node sends a `WithdrawMessage` transaction.
2. The `WithdrawMessage` is verified by the SDP logic.
    1. The `zk_id` returns an existing `DeclarationInfo`.
    2. The transaction containing `WithdrawMessage` is signed by the `zk_id`.
    3. The `withdraw_at` from `DeclarationInfo` is set to `None`.
    4. The `nonce` increases monotonically.
3. If any of the above is not correct, then discard the message and stop.
4. Set the `withdraw_at` from the `DeclarationInfo` to the current epoch number (the withdrawal epoch `e`).
5. The `DeclarationInfo` is removed and its note unlocked (releasing the `locked_note_id`) at epoch `e+2` by the Mantle epoch finalization step, right after the final reward is paid out.

### Query

The protocol must enable querying the ledger in at least the following manner:

- `GetAllProviderId(epoch)`, returns all `provider_id`s associated with the `epoch`.
- `GetAllProviderIdSince(epoch)`, returns all `provider_id`s since the `epoch`.
- `GetAllDeclarationInfo(epoch)`, returns all `DeclarationInfo` entries associated with the `epoch`.
- `GetAllDeclarationInfoSince(epoch)`, returns all `DeclarationInfo` entries since the `epoch`.
- `GetDeclarationInfo(zk_id)`, returns the `DeclarationInfo` entry identified by the `zk_id`.
- `GetDeclarationInfo(provider_id, service_type)`, returns the `DeclarationInfo` entry for that `provider_id` in that `service_type`. The service must be given because a `provider_id` is unique only within a service.
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
