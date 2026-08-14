# SERVICE-REWARD-DISTRIBUTION-PROTOCOL

| Field | Value |
| --- | --- |
| Name | Service Reward Distribution Protocol |
| Slug | 86 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors | David Rusu <davidrusu@logos.co>, Mehmet Gonen <mehmet@logos.co>, Marcin Pawlowski <marcin@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/bedrock-service-reward-distribution.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/bedrock-service-reward-distribution.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-service-reward-distribution.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-service-reward-distribution.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revisions History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial version. | 2025-11-03 |
| 1.1.0 | Removed references to DA Replaced references to Nomos with Logos Blockchain | 2026-04-17 |
| 1.2.1 | [[RFC] Enforce NoteId uniqueness](mantle-transaction-encoding/appendices/rfc-enforce-noteid-uniqueness.md). | 2026-04-24 |
| 1.3.0 | [RFC] Remove Concept of a Session | 2026-06-22 |
| 1.4.0 | [RFC] One canonical encoding for `ServiceType` and `Locator` | 2026-08-14 |

# Introduction

Logos Blockchain relies on the Blend Network service to operate. The service requires an independent set of known nodes. For sustainability and fairness, these services must compensate service validators based on their participation. Validators first declare their participation through [Service Declaration Protocol](bedrock-service-declaration-protocol.md). The **Service Reward Distribution Protocol** enables deterministic, efficient, and verifiable reward distribution to validators based on their activity within each service.

Each service defines:

- The validator activity rule that distinguishes between active and inactive validators.
- The reward formula for distributing the epoch’s rewards at the end of the epoch.

This document describes the protocol's logic for deterministically distributing rewards through Mantle Transactions for services.

# Overview

The protocol unfolds over three key phases, aligned with validator epochs:

1. **Service Activity Tracking** (epoch N+1): Service validators submit signed activity messages to attest to their participation of epoch N through a Mantle Transaction, including an activity message (see [SDP_ACTIVE](bedrock-v1.1-mantle-specification.md#sdp_active)).
2. **Service Reward Derivation** (End of epoch N+1): Nodes compute each validator’s reward based on validated activity messages and the different service reward policies.
3. **Service Reward Distribution** (First block of epoch N+2): Rewards are distributed to validators marked as active for the service. This is done by inserting new notes in the ledger corresponding to the reward amount for each active validator.

![Diagram](bedrock-service-reward-distribution/assets/341261aa-09df-804b-ae7f-cec3cb5d830c.png)

**Core Properties:**

- Service rewards are distributed to the `zk_id` from validator [SDP declarations](bedrock-service-declaration-protocol.md).
- Minimal Block Overhead: rewards are directly added to the ledger without involving Mantle Transactions.

# Protocol

## Activity tracking

Throughout epoch **N+1**, the block proposers integrate Mantle Transactions containing [SDP_ACTIVE Operations](bedrock-v1.1-mantle-specification.md#sdp_active). These transactions originate from service validators and are used to [derive their activity according to the service provided policy](bedrock-service-declaration-protocol.md). The protocol does not prescribe a unique activity rule: each service defines what qualifies as valid participation, enabling flexibility across different services.

Service validators are economically incentivized to participate actively since only active validators will be rewarded. Moreover, by decoupling activity submission from reward calculation, the system remains robust to network latency.

This generalized mechanism accommodates a wide range of services without requiring specialized infrastructure. It enables services to evolve their own activity rules independently while preserving a shared framework for reward distribution.

## Service Reward Calculation

At the end of epoch **N+1**, service rewards for the validator `n` for the epoch **N** are computed by the different services taking as input the rewards of the epoch:

$$
Rewards^n := serviceReward(n,Rewards\_Epoch)
$$

Where $`Rewards\_Epoch`$ are the total rewards of epoch **N**. The $`Rewards\_Epoch`$ is determined by the linked reference, which calculates how much each service receives based on fees burnt during epoch N and the blockchain's state. $`Rewards^n`$ is stored as an array that maps each validator's `zk_id` to their allocated reward.

## Service Reward Distribution

Starting immediately after epoch **N+1**, service rewards are distributed in the first block of epoch **N+2.** The rewards are inserted directly in the ledger without triggering any Mantle validation. The `NoteId` is computed using the result of `hash(`[`ServiceType`](bedrock-service-declaration-protocol.md)`|| epoch_number)` as the `op_id`, where `ServiceType` is serialized as its canonical one-byte discriminant ([Service Types](bedrock-service-declaration-protocol.md#service-types)). The output number corresponds to the position of the `zk_id` when sorted in ascending order.

The reward must:

  - Transfer the correct reward amount according to [Service Reward Calculation](#service-reward-calculation).2
  - Be sent to the public key `zk_id` of the validator registered during [declaration of the service](bedrock-service-declaration-protocol.md).
  - Be distributed into a single note if several rewards share the same `zk_id`.
  - Be executed identically by every node processing the first block of epoch N+2. This happens by inserting notes in the ledger in ascending order of `zk_id`.

Nodes indirectly verify the correct inclusion of rewards because all consensus-validating nodes must maintain the same ledger view to derive the latest ledger root, which serves as input for verifying the [Proof of Leadership](cryptarchia-proof-of-leadership.md).

After the epoch-**N** rewards are distributed, withdrawn declarations whose last rewardable epoch was **N** are removed by Mantle as part of the same epoch transition (see [SDP Epoch Finalization](bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization)).
