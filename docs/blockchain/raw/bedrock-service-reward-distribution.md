# BEDROCK-SERVICE-REWARD-DISTRIBUTION

| Field | Value |
| --- | --- |
| Name | Bedrock v1.2 Service Reward Distribution Protocol |
| Slug | 86 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomaslavaur@logos.co> |
| Contributors | David Rusu <davidrusu@logos.co>, Mehmet Gonen <mehmet@logos.co>, Marcin Pawlowski <marcin@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-service-reward-distribution.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-service-reward-distribution.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Service Reward Distribution Protocol
for distributing rewards to validators based on their participation
in Nomos services such as Data Availability and Blend Network.
The protocol enables deterministic, efficient, and verifiable reward distribution
to validators based on their activity within each service.

**Keywords:** Bedrock, rewards, services, validators, Data Availability,
Blend Network, session, activity

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Definitions

| Terminology | Description |
| ----------- | ----------- |
| Session | A fixed number of blocks during which the validator set remains unchanged. |
| Service Validator | A node participating in a service (DA or Blend Network). |
| Activity Message | A signed message attesting to a validator's participation. |
| zk_id | The zero-knowledge identity of a validator from SDP declarations. |
| SDP_ACTIVE | A Mantle Operation used to submit activity attestations. |

## Background

Nomos relies on multiple services,
including the Data Availability and Blend Network -
each operated by independent validator sets.
For sustainability and fairness,
these services must compensate service validators based on their participation.
Validators first declare their participation through
[Service Declaration Protocol][sdp].

Each service defines:

- The session length, a fixed number of blocks
  during which its validator set remains unchanged.
- The validator activity rule that distinguishes
  between active and inactive validators.
- The reward formula for distributing the session's rewards
  at the end of the session.

The protocol unfolds over three key phases, aligned with validator sessions:

1. **Service Activity Tracking** (Session N+1):
   Service validators submit signed activity messages
   to attest to their participation of session N through a Mantle Transaction,
   including an activity message
   (see [Mantle Specification - SDP_ACTIVE][mantle-sdp-active]).

1. **Service Reward Derivation** (End of Session N+1):
   Nodes compute each validator's reward based on validated activity messages
   and the different service reward policies.

1. **Service Reward Distribution** (First block of session N+2):
   Rewards are distributed to validators marked as active for the service.
   This is done by inserting new notes in the ledger
   corresponding to the reward amount for each active validator.

**Core Properties:**

- Service rewards are distributed to the `zk_id` from validator SDP declarations.
- Minimal Block Overhead: rewards are directly added to the ledger
  without involving Mantle Transactions.

## Protocol

### Sessions

Each service defines its own session length (e.g., 10000 blocks), during which:

- The service validator set remains static.
- Activity criteria and reward policy are fixed.

### Activity Tracking

Throughout session N+1, the block proposers integrate Mantle Transactions
containing `SDP_ACTIVE` Operations.
These transactions originate from service validators
and are used to derive their activity
according to the service provided policy.
The protocol does not prescribe a unique activity rule:
each service defines what qualifies as valid participation,
enabling flexibility across different services.

Service validators are economically incentivized to participate actively
since only active validators will be rewarded.
Moreover, by decoupling activity submission from reward calculation,
the system remains robust to network latency.

This generalized mechanism accommodates a wide range of services
without requiring specialized infrastructure.
It enables services to evolve their own activity rules independently
while preserving a shared framework for reward distribution.

### Service Reward Calculation

At the end of session N+1,
service rewards for the validator `n` for the session N
are computed by the different services
taking as input the rewards of the session:

```text
Rewards^n := serviceReward(n, Rewards_Session)
```

Where `Rewards_Session` are the total rewards of session N.
The `Rewards_Session` is determined by the service,
which calculates how much each service receives
based on fees burnt during session N and the blockchain's state.
`Rewards^n` is stored as an array that maps each validator's `zk_id`
to their allocated reward.

### Service Reward Distribution

Starting immediately after session N+1,
service rewards are distributed in the first block of session N+2.
The rewards are inserted directly in the ledger
without triggering any Mantle validation.

The note ID is computed using the result of
`zkhash(FiniteField(ServiceType, byte_order="little", modulus=p) || session_number)`
as the transaction hash.
The output number corresponds to the position of the `zk_id`
when sorted in ascending order.

The reward MUST:

- Transfer the correct reward amount
  according to [Service Reward Calculation](#service-reward-calculation).
- Be sent to the public key `zk_id` of the validator
  registered during declaration of the service.
- Be distributed into a single note if several rewards share the same `zk_id`.
- Be executed identically by every node processing the first block of session N+2.
  This happens by inserting notes in the ledger in ascending order of `zk_id`.

Nodes indirectly verify the correct inclusion of rewards
because all consensus-validating nodes must maintain the same ledger view
to derive the latest ledger root,
which serves as input for verifying the [Proof of Leadership][pol].

## References

### Normative

- [Service Declaration Protocol][sdp] - Protocol for declaring service participation
- [Mantle Specification][mantle-sdp-active] - SDP_ACTIVE operation specification
- [Proof of Leadership][pol] - Proof of Leadership specification

### Informative

- [v1.2 Service Reward Distribution Protocol][origin-ref] - Original specification document

[sdp]: https://nomos-tech.notion.site/Service-Declaration-Protocol
[mantle-sdp-active]: https://nomos-tech.notion.site/Mantle-Specification
[pol]: https://nomos-tech.notion.site/Proof-of-Leadership
[origin-ref]: https://nomos-tech.notion.site/v1-2-Service-Reward-Distribution-Protocol-26b261aa09df8032861dddf01182e242

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
