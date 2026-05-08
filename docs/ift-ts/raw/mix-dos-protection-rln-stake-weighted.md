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

This document specifies a registration policy extension for the [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md) specification, introducing stake-proportional rate limits for mix nodes.
Under this extension, each node's rate limit is computed as a linear function of its committed stake and enforced via the RLN-Diff circuit defined in [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md).
The mapping is Sybil-resistant, requires no circuit changes, and enforces rate differentiation entirely through the membership registry.

## 1. Introduction

The [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md) assigns a flat rate limit to all mix nodes that meet a minimum stake requirement. To accommodate high-capacity relay nodes, this limit must be set high &mdash; making the same rate headroom available to any minimally-staked attacker. This structural limitation is referred to as the rate amplification gap, defined in [Section 3.1](#31-rate-amplification-gap).

This document specifies an extension that replaces this flat limit with a stake-proportional mapping: a node claiming a higher rate must commit proportionally more stake. This raises the economic cost of exploiting the gap but does not eliminate it.

[Section 2](#2-terminology) defines terms used in this specification. [Section 3](#3-background) provides background on the rate amplification gap and RLN-Diff. [Section 4](#4-approach) specifies the stake-to-rate mapping, registration, and verification mechanics. [Section 5](#5-security-and-privacy-considerations) covers security and privacy considerations. [Section 6](#6-out-of-scope) defines scope boundaries. [Section 7](#7-future-work) identifies limitations and future directions.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

The following terms are used throughout this specification.
Other terms are as defined in the [Mix Protocol](./mix.md), [Mix DoS Protection](./mix-dos-protection.md), [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md), [RLN-v1](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/32/rln-v1.md), and [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md) specs.

- **`S_unit`**: The stake required per message per epoch.
  A system-wide constant defined at deployment time.

- **`R_base`**: The flat per-node rate limit per epoch on outgoing packets, referred to as the messaging rate in [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md).

- **`R_min`**: The minimum rate limit a node may be registered with. `1 ≤ R_min ≤ R_base`.

- **`R_max`**: The maximum rate limit any node may be assigned, regardless of stake, expressed as `f × R_base` where `f ≥ 1` is a deployment-defined multiplier.

- **floor-stake**: The minimum stake required to register, `R_min × S_unit`.
  Nodes with stake below floor-stake are rejected at registration.

- **Membership**: The result of a single node registration, backed by one stake deposit.
  Each node holds exactly one membership.

- **Sybil-resistant**: A property of a stake-based membership mechanism in which registering `N` nodes requires `N` times the stake of one, ensuring no rate advantage from splitting stake across multiple nodes.
  Each unit of rate costs exactly `S_unit` of stake, regardless of how that stake is distributed across registrations.

## 3. Background

This section provides background on the rate amplification gap in [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md), and RLN-Diff.

### 3.1 Rate Amplification Gap

[RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md) enforces a flat rate limit `R_base` per node per epoch on outgoing packets. Two properties combine to make this exploitable:

- `R_base` must be set high enough to accommodate the forwarding load of high-capacity relay nodes. As a result, all nodes receive the same high `R_base` regardless of stake.
- The [Mix Protocol](./mix.md)'s unlinkability guarantees make forwarded and originated packets cryptographically indistinguishable by design, so any node can use its `R_base` allowance entirely for origination.

Together, these give a minimally-staked attacker the same effective origination budget as the forwarding budget intended for a high-capacity honest relay.

Raising `R_base` to accommodate higher-capacity relays widens this budget proportionally. This structural limitation is referred to as the rate amplification gap.

### 3.2 RLN-Diff

[Rate Limiting Nullifiers (RLN)](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md) is a zero-knowledge construct that allows message rate limits to be set and cryptographically enforced for members of a group, without revealing their identity.
This specification uses the RLN-Diff variant, which supports per-member rate limits set individually at registration. The full mechanics are defined in [RLN-v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md); only the parts required to follow [Section 4.2](#42-registration) and [Section 5](#5-security-and-privacy-considerations) are summarised below.

**Registration**:
A member generates an `identity_secret` and derives `id_commitment = Poseidon(identity_secret)`. It submits `id_commitment` and a `user_message_limit` to the membership registry.

The registry writes a Merkle leaf encoding both as a `rate_commitment`:

```text
rate_commitment = Poseidon(id_commitment, user_message_limit)
```

`user_message_limit` is observable to any party that can read the registry.

**Rate limit**:
Each member's rate is bounded by the `user_message_limit` set at registration.
For each outgoing packet, a member selects an unused `message_id` in `[1, user_message_limit]` for the current epoch and generates an RLN-Diff proof. 
The proof binds the packet to that `message_id` and epoch, attests that the member holds a `rate_commitment` in the Merkle tree, and enforces `message_id ≤ user_message_limit` via a range constraint.

`user_message_limit` is not revealed by the proof.

**Double-signalling and slashing**:
Reusing the same `message_id` with different signals in an epoch allows any verifier to reconstruct the member's `identity_secret` and slash its stake.

## 4. Approach

This specification raises the economic cost of exploiting the rate amplification gap defined in [Section 3.1](#31-rate-amplification-gap), by tying rate limits to committed stake.

The approach mirrors bandwidth-weighted relay selection in Tor, where relays are assigned traffic proportional to their capacity. The analogue here is economic: stake functions as a commitment to capacity, and rate limits scale accordingly.

The following sections specify the mapping, registration, and verification mechanics.

### 4.1 Mapping Function

A node's rate limit `user_message_limit` is computed from its registered stake `S` as follows:

```text
user_message_limit = min( floor( S / S_unit ), R_max )
```

where `R_max = f × R_base` as defined in [Section 4.4](#44-system-parameters).

This mapping MUST be computed and enforced by the membership registry at the time of registration.
It MUST NOT be modifiable after registration without re-registration.

The mapping is linear: doubling stake doubles `user_message_limit`, subject to `R_max`.

**Rationale for linear mapping**:
Any sub-linear mapping `g` where `g(S)/S` decreases with `S` is subadditive: `g(S₁) + g(S₂) > g(S₁ + S₂)`, meaning an attacker gains aggregate rate by splitting stake across multiple registrations.
Linear mapping is the unique Sybil-resistant boundary &mdash; it is additive (`g(S₁ + S₂) = g(S₁) + g(S₂)`), ensuring no rate advantage from splitting.
Super-linear mappings are Sybil-resistant but reward stake concentration, exacerbating the rate amplification gap.
Rate concentration is capped by `R_max`.

### 4.2 Registration

The node generates an `identity_secret` and derives `id_commitment`, as described in [Section 3.2](#32-rln-diff).

The membership registry MUST enforce the following at the time of registration:

1. Verify that `S ≥ R_min × S_unit`. Reject registrations below floor-stake.
2. Compute `user_message_limit = min( floor( S / S_unit ), R_max )`.
3. Complete registration as described in [Section 3.2](#32-rln-diff) using the computed `user_message_limit`.
4. Lock the stake for the duration of membership.
   Stake MUST NOT be withdrawable while membership is active.

Stake top-ups MUST NOT be accepted while a membership is active.
Any change in stake requires deregistration followed by re-registration.

### 4.3 Packet Sending and Verification

Packet sending follows the rate limit and double-signalling mechanics described in [Section 3.2](#32-rln-diff). The node selects a `message_id` in `[1, user_message_limit]` that has not been used in the current epoch and generates an RLN-Diff proof.

`user_message_limit` is observable at the registry layer but is not revealed by proofs; verifiers learn only that the sender has not exceeded their registered limit.

All per-hop verification and slashing logic are as defined in [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md).

### 4.4 System Parameters

| Parameter | Description |
| --- | --- |
| `S_unit` | Stake required per message per epoch. Deployment-defined. |
| `R_min` | Minimum rate, `1 ≤ R_min ≤ R_base`. Nodes with stake `S < R_min × S_unit` MUST be rejected. |
| `R_max` | `f × R_base`. Maximum rate regardless of stake. |
| `f` | Deployment multiplier `f ≥ 1`. Controls the maximum rate relative to the base rate. |

`S_unit` SHOULD be set such that a floor-stake node generating only mandatory cover traffic at the rate specified in [Mix Cover Traffic](./mix-cover-traffic.md) can sustain operation at `R_min`.

`f` MUST be set such that a single node operating at `R_max` cannot individually saturate the network's forwarding capacity.
`f = 10` is a reasonable starting point: it allows a high-stake operator to handle `10×` the base forwarding load without dominating the network.
Values above `f = 50` SHOULD be avoided without careful analysis of the deployment's expected node count and forwarding load distribution.

`S_unit`, `R_base`, `R_min`, `R_max`, and `f` MUST be published in a deployment configuration accessible to all participants before the network accepts registrations.
The membership registry MUST reject registrations inconsistent with the published parameters.
Verifiers trust the membership registry to enforce the correct value of these parameters at registration time.

## 5. Security and Privacy Considerations

### 5.1 Sybil-Resistance

The stake-to-rate mapping is Sybil-resistant: each unit of rate costs exactly `S_unit` of stake, regardless of how that stake is distributed across registrations.

For any partition of stake `S` across `N` nodes with individual stakes `S_1, ..., S_N` (∑ `S_i = S`), the aggregate `user_message_limit` satisfies:

```text
∑ floor( S_i / S_unit ) ≤ floor( S / S_unit )
```

Splitting stake across nodes cannot produce more aggregate `user_message_limit` than a single registration with equal total stake.
Equality holds when each `S_i` is an exact multiple of `S_unit`.

The above holds for stake up to `R_max × S_unit` per node.
Above this ceiling, the per-node `R_max` cap creates a residual incentive to register across additional nodes &mdash; each further `R_max × S_unit` of stake can claim an additional `R_max` of rate by registering a new node.
Each additional registration also incurs transaction fees and coordination overhead, providing an economic deterrent beyond the protocol guarantee.

### 5.2 Residual Rate Amplification Gap

The stake-to-rate mapping raises the economic cost of exploiting the rate amplification gap defined in [Section 3.1](#31-rate-amplification-gap), but does not eliminate the gap.
A malicious node that wants a high message rate must commit proportionally more stake, which is subject to slashing on detection.

The gap is structural: the [Mix Protocol](./mix.md) unlinkability guarantees make forwarding and origination indistinguishable, so any forwarding rate allowance is simultaneously an origination budget.
This is an explicitly acknowledged limitation of per-hop RLN regardless of the rate mapping function.

### 5.3 Registry-Layer Observability

`user_message_limit` is observable at the registry layer but is a private witness in the RLN-Diff circuit &mdash; not revealed by proofs.
All proofs are structurally identical regardless of the sender's registered rate.
Registry-level stake observability does not enable linking proofs to specific members.

## 6. Out of Scope

The following are explicitly out of scope for this specification:

- Dynamic rate adjustment without re-registration
- Reputation-based rate multipliers
- Stake token selection and blockchain infrastructure
- Detailed migration procedures and tooling for networks upgrading from flat-rate RLN
- Voluntary deregistration mechanisms (a [RLN Per-Hop DoS Protection](./mix-dos-protection-rln.md) responsibility)
- Membership registry implementation (smart contract, coordination layer, or other)

## 7. Future Work

- **Registry-layer privacy**: The registration publicly reveals the node's effective rate. A shielded membership registry &mdash; where the stake-to-identity link is concealed via ZK &mdash; would close this gap. One approach is multi-identity registration: a node registers multiple unit-rate identities, hiding its total rate from registry observers. However, slashing requires linking all identities to the committed stake: double-signalling on any identity must make the entire stake slashable. Achieving such an unlinkable registration with linked slashing requires circuit-level changes not available in current RLN-v2.

- **Dynamic stake top-up**: A mechanism for incrementally increasing stake without full deregistration would improve operational ergonomics.

- **Rate-weighted path selection**: The [Mix Protocol](./mix.md) currently specifies uniform random path selection. Under stake-weighted rate limits, this distributes forwarding load equally regardless of node capacity, causing low-rate nodes to hit their limits and drop forwarding traffic. Adapting the [Mix Protocol](./mix.md) to weight path selection proportional to registered rates &mdash; similar to Tor &mdash; would address this.

- **Cover traffic under non-uniform rates**: The [Mix Cover Traffic](./mix-cover-traffic.md) specification derives per-node cover emission bounds assuming uniform rate limits. Under stake-weighted rates, the forwarding load depends on the network's stake distribution, and the cover budget derivation does not directly apply.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Mix DoS Protection](./mix-dos-protection.md)
- [RLN Per-Hop DoS Protection for Mixnet](./mix-dos-protection-rln.md)
- [Mix Cover Traffic](./mix-cover-traffic.md)
- [libp2p Mix Protocol](./mix.md)
- [Rate Limiting Nullifiers v1](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/32/rln-v1.md)
- [Rate Limiting Nullifiers v2](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/rln-v2.md)
