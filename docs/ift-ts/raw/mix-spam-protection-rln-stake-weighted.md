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
Two strategies are defined for mapping stake to rate limit: Single-Identity and Multi-Identity.
In Single-Identity each node holds a single RLN identity with a stake-proportional rate limit. In contrast, in Multi-Identity each node holds multiple unit-rate RLN identities with count proportional to stake, avoiding rate-level fragmentation.
Both strategies are Sybil-resistant, use circuits already defined in [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md), and enforce rate differentiation entirely through the membership registry.

## 1. Introduction

The [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) assigns a flat rate limit to all mix nodes that meet a minimum stake requirement. To accommodate high-capacity relay nodes, this limit must be set high&mdash;making the same rate headroom available to any minimally-staked attacker. This structural limitation is referred to as the rate amplification gap, defined in [Section 3.1](#31-rate-amplification-gap).

This document specifies an extension that replaces this flat limit with a stake-proportional mapping: a node claiming a higher rate must commit proportionally more stake. This raises the economic cost of exploiting the gap but does not eliminate it.

[Section 2](#2-terminology) defines terms used in this specification. [Section 3](#3-background) provides background on the rate amplification gap and the RLN-v2 circuits. [Section 4](#4-approach) specifies the registration strategies. [Section 5](#5-strategy-comparison) compares them. [Section 6](#6-security-and-privacy-considerations) analyses security properties. [Section 7](#7-implementation-recommendations) covers implementation. [Section 8](#8-future-work) identifies limitations and future directions.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

The following terms are used throughout this specification.
Other terms are as defined in the [Mix Protocol](./mix.md), [Mix DoS Protection](./mix-dos-protection.md), [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md), [RLN-v1](./32/rln-v1.md), and [RLN-v2](./rln-v2.md) specs.

- **unit-rate**: A rate of 1 message per epoch.

- **`S_unit`**: The stake required per unit-rate.
  A system-wide constant defined at deployment time.

- **`R_base`**: The flat per-node rate limit defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md).

- **`R_min`**: The minimum rate limit a node may be registered with.

- **`R_max`**: The maximum rate limit any node may be assigned, regardless of stake, expressed as `f × R_base` where `f` is a deployment-defined multiplier `≥ 1`.

- **floor-stake**: The minimum stake required to register, `R_min × S_unit`.
  Nodes with stake below floor-stake are rejected at registration.

- **Membership**: The result of a single node registration, backed by one stake deposit.
  Each node holds exactly one membership.

- **Identity slot**: One entry in the membership Merkle tree, corresponding to one identity commitment submitted during registration&mdash;one Merkle leaf.
  Double-signalling on any one identity slot triggers slashing of the entire membership stake deposit.

  Note: in RLN-v1/v2, each registration produces one Merkle leaf. This specification allows a single registration to produce one or more identity slots.

- **Sybil-resistant**: A property of a stake-based membership mechanism in which registering `N` nodes requires `N` times the stake of one, ensuring no rate advantage from splitting stake across multiple nodes.
  Each unit of rate costs exactly `S_unit` of stake, regardless of how that stake is distributed across registrations.

## 3. Background

This section provides background on the rate amplification gap in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md), and the RLN-v2 circuits.

### 3.1 Rate Amplification Gap

[RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md) enforces a flat rate limit `R_base` per node per epoch on outgoing packets. Two properties combine to make this exploitable:

- `R_base` must be set high enough to accommodate the forwarding load of high-capacity relay nodes. As a result, all nodes receive the same high `R_base` regardless of stake.
- The [Mix Protocol](./mix.md)'s unlinkability guarantees make forwarded and originated packets cryptographically indistinguishable by design, so any node can use its `R_base` allowance entirely for origination.

Together, these give a minimally-staked attacker the same effective origination budget as the forwarding budget intended for a high-capacity honest relay.

Raising `R_base` to accommodate higher-capacity relays widens this budget proportionally. This structural limitation is referred to as the rate amplification gap.

### 3.2 RLN-v2 Circuits

[Rate Limiting Nullifiers (RLN)](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md) is a zero-knowledge construct that allows message rate limits to be set and cryptographically enforced for members of a group, without revealing their identity.
To participate, senders must register for a membership, typically backed by stake, to generate valid proofs.
If a sender exceeds the defined rate limit within a given epoch, the protocol allows for the reconstruction of their secret and subsequent slashing of their stake.
RLN-v2 defines two circuits: RLN-Same and RLN-Diff. The following sub-sections describe each.

#### 3.2.1 RLN-Diff Circuit

RLN-Diff supports per-member rate limits set individually at registration.
The mechanics described below&mdash;registration, rate limit, and double-signalling and slashing&mdash;are shared with RLN-Same except where noted in [Section 3.2.2](#322-rln-same-circuit).

**Registration.**
To join the group, a member:

1. Generates an `identity_secret` and derives `id_commitment = Poseidon(identity_secret)`.
2. Submits `id_commitment` and a `user_message_limit` to the membership registry.

The registry computes the Merkle leaf:

```text
rate_commitment = Poseidon(id_commitment, user_message_limit)
```

and writes `rate_commitment` to the RLN membership Merkle tree.
`user_message_limit` is observable to any party that can read the registry.

All members of a group share a single Merkle tree.
The Merkle root compactly represents the current group state and changes whenever a member joins or is slashed; a proof must reference a recent root to be considered valid.

**Rate limit.**
Each member's rate is bounded by the `user_message_limit` set at registration.
To send a packet, a member selects a `message_id` in the range `[1, user_message_limit]` that has not been used in the current epoch, and generates a ZK proof that:

- proves membership&mdash;that the member holds a `rate_commitment` in the Merkle tree, without revealing `identity_secret`, `user_message_limit`, or the leaf index;
- enforces `message_id ≤ user_message_limit` via a range constraint, with `user_message_limit` as a private witness&mdash;not revealed in the proof;
- produces a Shamir secret share of `identity_secret` bound to the current `epoch` and the proof signal;
- computes an `internal_nullifier` unique per `(member, epoch, message_id)` tuple, without revealing `identity_secret`.

Each `message_id` value may be used at most once per epoch; using all values in `[1, user_message_limit]` exhausts the member's rate allowance for that epoch.

**Double-signalling and slashing.**
A member that sends two packets with the same `message_id` and different signals in the same epoch produces two shares with the same `internal_nullifier`, sufficient to reconstruct `identity_secret` by polynomial interpolation.
Any verifier holding these shares can remove the member from the group and seize its stake.
Reuse of the same `message_id` with the same signal is detectable as a duplicate without requiring secret reconstruction.

#### 3.2.2 RLN-Same Circuit

RLN-Same provides a simpler alternative when per-member rate differentiation is not required. It differs from RLN-Diff as follows:

- `user_message_limit` is replaced by a deployment-wide public `message_limit` that applies the same global rate limit to all members.
- The Merkle leaf is `id_commitment` directly rather than `rate_commitment`.
- Slashing, Shamir secret sharing, and nullifier derivation are unchanged.

## 4. Approach

This specification raises the economic cost of exploiting the rate amplification gap (defined in [Section 3.1](#31-rate-amplification-gap)) by tying rate limits to committed stake.

The approach mirrors bandwidth-weighted relay selection in Tor, where relays are assigned traffic proportional to their capacity. The analogue here is economic: stake functions as a commitment to capacity, and rate limits scale accordingly.

To implement this stake-to-rate mapping, two strategies are defined: Single-Identity and Multi-Identity. The following sections specify the registration, rate limit mapping, and verification mechanics of each.

### 4.1 Single-Identity

In Single-Identity, each node holds one RLN identity, registered as a single identity slot with a rate limit proportional to its committed stake. It requires the RLN-Diff circuit ([Section 3.2.1](#321-rln-diff-circuit)), as per-member rate differentiation is not supported by RLN-Same.

#### 4.1.1 Mapping Function

A node's rate limit `user_message_limit` is computed from its registered stake `S` as follows:

```text
user_message_limit = min( floor( S / S_unit ), R_max )
```

where `R_max = f × R_base` as defined in [Section 4.4](#44-system-parameters).

This mapping MUST be computed and enforced by the membership registry at the time of registration.
It MUST NOT be modifiable after registration without re-registration.

The mapping is linear: doubling stake doubles `user_message_limit`, subject to `R_max`.
This property ensures Sybil-resistance&mdash;see [Section 6.3](#63-sybil-resistance).

**Rationale for linear over log-scale.**
Log-scale mapping (`user_message_limit ∝ log(stake)`) is not Sybil-resistant: `N × log(S/N) > log(S)` for any `N > 1`, meaning an attacker gains a higher aggregate rate by splitting stake across `N` registrations.
Linear mapping is Sybil-resistant&mdash;splitting yields no rate gain.
Rate concentration is capped by `R_max`, which is a simpler and more auditable guarantee than log-scale diminishing returns.

#### 4.1.2 Registration

The node generates an `identity_secret` and derives `id_commitment`, as described in [Section 3.2.1](#321-rln-diff-circuit).

The membership registry MUST enforce the following at the time of registration:

1. Verify that `S ≥ R_min × S_unit`. Reject registrations below floor-stake.
2. Compute `user_message_limit = min( floor( S / S_unit ), R_max )`.
3. Complete registration as described in [Section 3.2.1](#321-rln-diff-circuit) using the computed `user_message_limit`.
4. Lock the stake for the duration of membership.
   Stake MUST NOT be withdrawable while membership is active.

A node that wishes to increase its `user_message_limit` MUST deregister and re-register with the new stake amount, following the deregistration procedure defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md).
Partial stake top-ups that would change `user_message_limit` without re-registration MUST NOT be accepted, as they would invalidate the existing identity slot.

#### 4.1.3 Packet Sending and Verification

Packet sending follows the rate limit and double-signalling mechanics described in [Section 3.2.1](#321-rln-diff-circuit). The node selects a `message_id` in `[1, user_message_limit]` that has not been used in the current epoch and generates an RLN-Diff proof for its single identity slot.

All per-hop verification and slashing logic are as defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md).

### 4.2 Multi-Identity

In Multi-Identity, each node holds `N` RLN identities, registered as `N` identity slots each with unit-rate, where `N` is proportional to its committed stake.

Although Multi-Identity supports both RLN-Diff and RLN-Same ([Section 3.2](#32-rln-v2-circuits)), the following sub-sections describe it using RLN-Diff for uniformity with [Section 4.1](#41-single-identity).

#### 4.2.1 Mapping Function

The number of identity slots `N` allocated to a node is computed from its registered stake `S`:

```text
N = min( floor( S / S_unit ), R_max )
```

where `R_max = f × R_base` as defined in [Section 4.4](#44-system-parameters).

This mapping MUST be computed and enforced by the membership registry at the time of registration.
It MUST NOT be modifiable after registration without re-registration.

The mapping is linear and Sybil-resistant, identical to [Section 4.1.1](#411-mapping-function): splitting stake across multiple registrations yields no aggregate rate gain.

#### 4.2.2 Registration

The node generates `N` independent RLN identity key pairs: for each slot `i` in `[1, N]`, it generates `identity_secret_i` and derives `id_commitment_i`, as described in [Section 3.2.1](#321-rln-diff-circuit).

The membership registry MUST enforce the following at the time of registration:

1. Verify that `S ≥ R_min × S_unit`. Reject registrations below floor-stake.
2. Compute `N = min( floor( S / S_unit ), R_max )`.
3. The registrant SHOULD submit all `N` identity commitments in a single transaction.
   The registry MUST verify `len(id_commitments) == N` before writing any Merkle leaf.
   The registry MUST be able to identify all `N` identity slots belonging to the same stake deposit, so that double-signalling on any one slot triggers slashing of the full pooled stake and invalidation of all `N` slots.
4. For each slot `i` in `[1, N]`, complete registration as described in [Section 3.2.1](#321-rln-diff-circuit) with `user_message_limit = 1`.
5. Lock the stake for the duration of all `N` identity slots.
   Stake MUST NOT be withdrawable while any slot is active.

The membership registry MUST enforce `user_message_limit = 1` on all identity slots.
Self-registration with `user_message_limit > 1` MUST be rejected.

A node that wishes to increase `N` MUST deregister all existing identity slots and re-register with the new stake amount, following the deregistration procedure defined in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md).
Partial stake top-ups that would change `N` without re-registration MUST NOT be accepted, as the registration flow does not support adding or removing identity slots from an existing membership.

#### 4.2.3 Key Management

A node operating under Multi-Identity maintains `N` independent RLN identity key pairs, one per identity slot.
The node MUST track which key has been used in the current epoch to avoid double-signalling on any single slot, which would trigger slashing of the entire pooled stake&mdash;not a `1/N` fraction.

Operating `N` keys increases the surface area for accidental slashing: software bugs, clock drift, or key management errors on any one key carry the same consequence as deliberate double-signalling.
Operators MUST implement per-epoch usage tracking before deploying at high `N` values.

Keys SHOULD be selected randomly per packet to avoid observable patterns in nullifier sequences.
Round-robin selection is permissible but creates predictable patterns observable when the node operates below full capacity.

#### 4.2.4 Packet Sending and Verification

To send a packet, the node selects one unused identity slot for the current epoch and generates an RLN-Diff proof for that slot, following the rate limit mechanics in [Section 3.2.1](#321-rln-diff-circuit). Each slot may be used at most once per epoch; `message_id` values reset each epoch.

All per-hop verification, double-signalling detection, and slashing logic remain as specified in [RLN Per-Hop DoS Protection](./mix-spam-protection-rln.md), applied independently to each identity slot.

A node with `N` identity slots participates in the coordination layer as `N` independent nullifier streams, each broadcasting its own nullifier metadata per epoch.
This multiplies coordination layer load by `N` for high-stake nodes.
For example, with `f = 10` and `R_base = 10`, `R_max = 100`: a single high-stake node broadcasts up to 100 nullifiers per epoch, equivalent to the coordination load of 100 floor-stake nodes.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Mix DoS Protection](./mix-dos-protection.md)
- [RLN Per-Hop DoS Protection for Mixnet](./mix-spam-protection-rln.md)
- [Mix Cover Traffic](./mix-cover-traffic.md)
- [libp2p Mix Protocol](./mix.md)
- [Rate Limiting Nullifiers v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md)
