# Stake-Weighted Mix RLN DoS Protection

| Field | Value |
| --- | --- |
| Name | Stake-Weighted Mix RLN DoS Protection |
| Slug | TBD |
| Status | raw |
| Category | Standards Track |
| Editor | Akshaya Mani <akshaya@status.im> |
| Contributors |                              |

<!-- timeline:start -->
<!-- timeline:end -->

## Abstract

This document specifies a registration policy extension for the [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) specification, introducing stake-proportional rate limits for mix nodes.
Two strategies are defined: Single-Membership and Multi-Membership.
While Single-Membership encodes rate directly as a per-node message limit, Multi-Membership issues multiple unit memberships proportional to stake to preserve full anonymity set integrity.
Both strategies are Sybil-neutral, require no changes to the [RLN-Diff circuit](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md), and enforce rate differentiation entirely through the membership registry.

## 1. Introduction

The [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) specification assigns a flat rate limit to all mix nodes that meet a minimum stake requirement. To accommodate high-capacity relay nodes, this limit must be set high — making the same rate headroom available to any minimally-staked attacker. This structural limitation is referred to as the [rate amplification gap](#3-1-rate-amplification-gap).

This document specifies an extension that replaces this flat limit with a stake-proportional mapping: a node claiming a higher rate must commit proportionally more stake, raising the economic cost of exploiting the gap. The extension mitigates but does not eliminate it.

[Section 2](#2-terminology) defines terms used in this specification. [Section 3](#3-background) provides background on the rate amplification gap and the RLN-Diff circuit. [Section 4](#4-approach) specifies the registration strategies. [Section 5](#5-strategy-comparison) compares them. [Section 6](#6-security-and-privacy-considerations) analyses security properties. [Section 7](#7-implementation-recommendations) covers implementation. [Section 8](#8-future-work) identifies limitations and future directions.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

The following terms are used throughout this specification.
Other terms are as defined in the [Mix Protocol](./mix.md), [Mix DoS Protection](./mix-dos-protection.md), and [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) specs.

- **`S_unit`**: The stake required per unit of `user_message_limit` (Single-Membership) or per membership slot (Multi-Membership).
  A system-wide constant defined at deployment time.

- **`R_min`**: The minimum rate limit a node may be registered with.
  The minimum stake required to participate is `R_min × S_unit`.
  Nodes with stake lower than that MUST be rejected at registration.

- **`R_max`**: The maximum rate limit any node may be assigned, regardless of stake, expressed as `k × R_base` where `R_base` is the flat per-node rate defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) and `k` is a deployment-defined multiplier `≥ 1`.
  Corresponds to `message_limit` in [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md)&mdash;the global ceiling above which no `user_message_limit` may be set.

- **`floor-stake`**: A node registered at the minimum stake `R_min × S_unit`.
  Under Single-Membership, a floor-stake node receives `user_message_limit = R_min`.
  Under Multi-Membership, a floor-stake node receives `N = R_min` membership slots.
  All floor-stake nodes share identical registry entries, forming the largest natural anonymity pool in both strategies.

- **Membership slot**: In Multi-Membership, a single RLN membership with `user_message_limit = 1` issued by the membership registry.
  A node with `N` membership slots holds `N` RLN identities, each with its own identity key and nullifier sequence, backed by a single pooled stake deposit&mdash;double-signalling on any one identity triggers slashing of the entire deposit.

## 3. Background

### 3.1 Rate Amplification Gap

The [RLN Per-Hop DoS Protection spec](./mix-spam-protection-rln.md) enforces a flat rate limit `R` per node per epoch.
Each mix node generates a fresh RLN proof for every outgoing packet, and double-signalling detection allows verifiers to slash any node exceeding `R`.

A structural limitation arises from the [Mix Protocol](./mix.md) unlinkability guarantees: forwarded packets and originated packets are cryptographically indistinguishable by design.
This means a node's rate limit `R` must be set high enough to cover its expected forwarding load.
As a result, a malicious node registered at minimal stake receives the same `R` as a high-capacity honest relay node, allowing it to exploit the entire forwarding rate allowance as originating capacity at no additional cost.

Raising `R` globally to accommodate high-traffic relay nodes directly increases the effective message rate available to a minimally-staked attacker.
This structural limitation is referred to as the rate amplification gap.

### 3.2 RLN-Diff Overview

[Rate Limiting Nullifiers (RLN)](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md) is a zero-knowledge construct that allows members to prove rate-limited group membership without revealing their identity.
Senders must register for membership backed by stake to generate proofs; exceeding the rate limit allows the sender's secret to be reconstructed and their stake to be slashed.
In [RLN-v1](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/32/rln-v1.md), all members share the same global rate limit.

This specification uses the RLN-Diff variant defined in [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md), which extends RLN-v1 to support per-member rate limits: each member is assigned a `user_message_limit` that bounds their message rate independently of other members.

**Membership.**
Each member holds an `identity_secret` and publicly registers an `id_commitment = Poseidon(identity_secret)` in the RLN membership Merkle tree.
The Merkle leaf encodes the member's assigned `user_message_limit` via:

```text
rate_commitment = Poseidon(id_commitment, user_message_limit)
```

The `rate_commitment` is written to the membership Merkle leaf at registration.
The `user_message_limit` is submitted publicly at `register()` and is observable to any party that can read the membership registry; it is a private input to the ZK circuit and not revealed in proofs.

**Rate limit.**
To send a packet, a member selects a unique `message_id` in the range `[0, user_message_limit)` and generates a ZK proof using the RLN-Diff circuit.
The proof proves membership&mdash;that the member knows an `identity_secret` whose `id_commitment` is committed in the Merkle tree&mdash;and enforces via a range constraint that `message_id < user_message_limit`, without revealing `identity_secret`, the leaf index, or `user_message_limit`.
Each `message_id` value may be used at most once per epoch; exhausting `[0, user_message_limit)` exhausts the member's rate allowance for that epoch.

**Double-signalling and slashing.**
A member that sends two packets with the same `message_id` and different signals in the same epoch produces two points on the same polynomial, sufficient to reconstruct `identity_secret`.
Any verifier holding these shares can remove the member from the group and seize its stake.
Reuse of the same `message_id` with the same signal is detectable as a duplicate without requiring secret reconstruction.

## 4. Approach

This specification addresses the rate amplification gap by tying rate limits to committed stake.
While the [Mix Protocol](./mix.md) unlinkability guarantees (explained in [Section 3.1](#3-1-rate-amplification-gap)) make eliminating the gap impossible at the RLN layer, stake-weighted rate limits raise the economic cost of exploiting it.
A node that wants a higher rate limit must commit proportionally more stake, making any exploitation of the gap subject to slashing of that stake.

The approach mirrors bandwidth-weighted relay selection in Tor, where relays are assigned traffic proportional to their declared capacity rather than treated as uniform participants.
The analogue here is economic: stake functions as a commitment to capacity, and rate limits scale accordingly.

To implement this mapping, two registration strategies are defined: Single-Membership and Multi-Membership.
Both conform to the [DoS Protection Interface](./mix-dos-protection.md#8-dos-protection-interface) defined in [Mix DoS Protection](./mix-dos-protection.md), and differ only in how `user_message_limit` is set at registration time.
All `GenerateProof` and `VerifyProof` logic is unchanged, and the `RateLimitProof` wire format defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) is unchanged.
Both strategies use the RLN-Diff circuit without modification.

Deployments MUST choose one strategy and apply it uniformly across all registered nodes.
Deployments MUST NOT mix strategies within a single deployment&mdash;nodes registered under Single-Membership have registry entries with `user_message_limit >= 1`, making them distinguishable from Multi-Membership nodes whose registry entries always carry `user_message_limit = 1`.

Deployments SHOULD use Multi-Membership unless the operational overhead of `N`-key management is prohibitive or mix node identity is not sensitive.
See [Section 6.6](#6-6-anonymity-set-fragmentation) for privacy implications of both strategies and deployment documentation requirements for Single-Membership.

**Why not discrete tiers.**
Discrete tiers (_e.g.,_ Bronze / Silver / Gold) are implemented as multiple membership groups, each with a different flat `message_limit` and its own membership Merkle tree requiring separate synchronisation.
They introduce a `k`-anonymity floor requirement to prevent small-set de-anonymization.
The `k`-floor is a binary switch: if a tier falls below `k` members, it is disabled, creating an attack vector where an attacker removes one member to disable an entire tier at `O(1)` cost.
Both strategies in this specification avoid tiers and `k`-floors.
Anonymity set fragmentation under Single-Membership is present but continuous.
Multi-Membership eliminates it entirely.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Mix DoS Protection](./mix-dos-protection.md)
- [RLN Per-Hop DoS Protection for Mixnet](./mix-spam-protection-rln.md)
- [Mix Cover Traffic](./mix-cover-traffic.md)
- [libp2p Mix Protocol](./mix.md)
- [Rate Limiting Nullifiers v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md)
