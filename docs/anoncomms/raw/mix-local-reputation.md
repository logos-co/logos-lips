# Mix Local Reputation

| Field | Value |
| --- | --- |
| Name | Mix Local Reputation |
| Status | raw |
| Category | Standards Track |
| Editor | Akshaya Mani <akshaya@status.im> |
| Contributors |  |

<!-- timeline:start -->
<!-- timeline:end -->

## Abstract

This document specifies a local reputation record that each mix node keeps about its peers,
and the two effects of that record:
eligibility of peers for path selection,
and refusal of service to peers the node observes misbehaving.
Eligibility is computed only from inputs every node can verify,
so a peer's eligibility does not depend on which node evaluates it.
The record is never shared,
never ranks peers,
and never weights selection.
Eligibility excludes few of the peers a node has discovered,
so restricting path selection to the eligible ones
neither concentrates forwarding load
nor varies from sender to sender beyond the variation discovery already produces.
The record admits only current members of the DoS protection mechanism to path selection,
so that one membership can be held to one peer,
removes members that provably overspend ahead of the registry removing them,
and lets a node refuse service to peers that send it invalid traffic;
it does not lower the fraction of adversarial nodes among members.

## 1. Introduction

The [Mix Protocol](./mix.md#943-no-sybil-resistance) has no Sybil resistance of its own:
every discoverable node is equally eligible for path selection.
The DoS protection mechanism does not supply it either:
nothing binds a membership to a mix identity,
nor can anything published do so without naming the account that funded the membership
([Section 4.1](#41-membership-attestation)).
An adversarial hop may therefore hold no membership at all,
or share one with others and split its rate limit,
and either way it learns its predecessor and its successor
without a membership of its own.
Separately, the [Mix Protocol](./mix.md#941-undetectable-node-misbehavior) has no mechanism
to detect or attribute node misbehavior.

This document makes eligibility for path selection depend on a membership,
so that one membership can be held to one peer,
and records the misbehavior a node can attribute for itself.

The design follows Tor's [Guard flag](https://spec.torproject.org/dir-spec/assigning-flags-vote.html) rather than its guard choice:
peers are admitted by membership in a registry whose criteria cost an adversary time and stake,
and selection within the set stays uniform.
Local reputation scores that rank or weight peers can be gamed by [nodes that behave well until trusted](https://www.freehaven.net/anonbib/cache/mix-acc.pdf).
Even weights that every node agrees on [concentrate traffic on the highest-weighted nodes](https://www.freehaven.net/anonbib/cache/casc-rep.pdf),
and an adversary that holds a few of those nodes sees a disproportionate share of all paths.
Finally, any selection distribution that differs from sender to sender,
whether from local scores or from a personal set of preferred or avoided peers,
is a [route fingerprint](https://www.cl.cam.ac.uk/~rnc1/anonroute.pdf) that identifies the sender to any adjacent hop
([Section 7.2](#72-fingerprinting-through-the-eligible-set)).
The record introduces none of the three:
selection within the eligible set is uniform,
eligibility depends only on inputs every node evaluates identically,
and what a node observes on its own affects only whom it serves.
Nodes may still draw from different pools,
but any such difference comes from the discovery mechanism,
not from this specification,
which neither relies on it nor adds to it.

[Section 2](#2-terminology) defines terms used in this specification.
[Section 3](#3-design-principles) states the design principles.
[Section 4](#4-the-reputation-record) specifies the record, its inputs, eligibility, service, and effects.
[Section 5](#5-integration) specifies integration with path selection, cover traffic, and DoS protection,
and the capacity the eligible set must have.
[Section 6](#6-parameters) lists parameters.
[Section 7](#7-security-and-privacy-considerations) covers security and privacy considerations.
[Section 8](#8-out-of-scope) defines scope boundaries.
[Section 9](#9-future-work) identifies limitations and future directions.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

The following terms are used throughout this specification.
Other terms are as defined in the [Mix Protocol](./mix.md),
[Mix DoS Protection](./mix-dos-protection.md),
and [Mix Cover Traffic](./mix-cover-traffic.md) specs.

- **Reputation Record**: The per-peer state a node keeps locally under this specification:
  the peer's handle,
  verifiable evidence,
  and counters of invalid traffic received from the peer.
  It holds no score.
  One record per discovered mix node.

- **Mix Identity**: The durable identity a mix node is known by,
  carried in the multiaddresses it publishes through discovery
  ([Mix Protocol Section 6.1](./mix.md#61-discovery)).
  It does not include the node's X25519 key for Sphinx encryption,
  which a node may rotate without changing its mix identity.

- **Membership Attestation**: A credential, available for a peer,
  that binds the peer's mix identity to a current membership of the DoS protection mechanism
  while revealing nothing further about that membership.
  This specification states the properties an attestation must have,
  not how it is constructed ([Section 4.1](#41-membership-attestation)).

- **Handle**: An opaque identifier for the membership behind an attestation.
  It is determined by the membership,
  so a peer cannot change it without registering again,
  and one membership yields the same handle for as long as it lasts.
  It reveals nothing else:
  not the registry entry, not the stake, not the account that funded it.
  Verifiable evidence attaches to a peer through its handle ([Section 4.2.1](#421-verifiable-evidence)).

- **Verifiable Evidence**: A fact about a peer's membership that any node can check for itself,
  without trusting whoever relayed it,
  and that identifies the membership by its handle.

- **Observation**: An event involving a peer that the node itself witnessed:
  a proof it verified,
  and a packet it received from the peer.
  Observations are first-hand only.
  A report from another node is never an observation.

- **Global Inputs**: Membership attestations and verifiable evidence.
  Global because any node evaluates them the same way:
  each verifies on its own,
  against state the DoS protection mechanism gives every node,
  with no trust in whoever relayed it.
  Two nodes holding the same global inputs reach the same verdict on a peer.

- **Eligible**: A peer whose global inputs satisfy the eligibility conditions ([Section 4.3](#43-eligibility)).
  Path selection samples from eligible peers.

- **Network Size**: The number of mix nodes in the deployment, denoted `N`.
  It is used only to express fractions of the network.

- **Discovered Set**: The mix nodes a node currently knows of,
  through whatever discovery mechanism the deployment uses
  ([Mix Protocol Section 6.1](./mix.md#61-discovery)).
  Discovery returns a partial and changing sample of the network,
  so this set differs between nodes and is never the whole network.
  Its size is denoted `D`, with `D ≤ N`.

- **Eligible Set**: The eligible peers within the node's discovered set, at a given time.
  Its size is denoted `k`, with `k ≤ D ≤ N`.

- **Service**: The processing of a peer's packets by a node.
  A node refuses service to a peer on the basis of its own observations ([Section 4.4](#44-service)).

- **Epoch**: The rate-limit period of the DoS protection mechanism.
  Rate-limit budgets, observation counters, and their decay are all expressed per epoch.

## 3. Design Principles

- **Two decisions, two kinds of input.**
  Eligibility for path selection depends only on global inputs,
  so a peer's eligibility does not depend on which node evaluates it.
  Service depends on the node's own observations,
  which no other node needs to know or trust.

- **Exclude, never rank.**
  Each decision is a per-peer bit.
  The record never produces a score that influences how often an eligible peer is chosen.
  Uniform selection among eligible peers is preserved,
  so a peer that behaves well gains nothing over any other well-behaved peer.

- **Attestation is pluggable.**
  This specification defines what a membership attestation must do,
  not how it is built.
  Any mechanism with the required properties satisfies it ([Section 4.1](#41-membership-attestation)).

- **Local, never shared.**
  A node never shares its record or its observations,
  and never acts on another node's.
  What the DoS protection mechanism carries between nodes is proof, not opinion:
  an attestation, a handle, and evidence each verify on their own.
  This removes the channel through which reputation systems are gamed.

- **Large eligible set.**
  Only eligible nodes relay,
  so the fewer there are, the more each must forward.
  A deployment caps its origination rate to keep that within the rate-limit budget ([Section 5.4](#54-capacity)).

- **Fail closed on exhaustion, never fall back.**
  If the eligible set is too small to build a path,
  the node discovers more peers rather than relaxing the conditions.
  An adversary that can make a node relax its record can shape the node's paths.

- **No anonymity claim against passive adversaries.**
  A peer that holds a membership and behaves correctly is eligible,
  whether or not it is adversarial.
  The record does not detect intent ([Section 7.1](#71-what-the-record-does-not-do)).

## 4. The Reputation Record

### 4.1 Membership Attestation

A registry entry names the account that funded the stake.
A published mapping from membership to mix identity would therefore attach each node to that account,
and link to one another every node the same account funded.
That is a durable link the mix layer itself never leaks.
This specification publishes no such mapping,
and does not require a node to look a discovered peer up in the registry.
It requires instead that a membership attestation be available for every peer it considers,
binding the peer to a membership without naming which one.

This specification does not define how an attestation is constructed
([Section 8](#8-out-of-scope)).
A deployment MUST provide a mechanism with the following properties.

| Property | Requirement |
| --- | --- |
| Binding | An attestation binds one mix identity to one current membership of the DoS protection mechanism, and MUST be producible only by a node that controls that identity. |
| Uniqueness | One membership MUST yield at most one attested mix identity for the life of that membership. Two valid attestations carrying the same handle MUST be verifiable evidence ([Section 4.2.1](#421-verifiable-evidence)), so that the membership is made ineligible at every node and not at the detecting node alone. |
| Independent verifiability | Any node MUST be able to verify an attestation from the membership state it already holds, without trusting whoever relayed it, and without contacting the peer or the registry. |
| Minimal disclosure | An attestation MUST reveal nothing about the membership beyond its handle: not the registry entry, not the stake, not the account that funded it. |
| Handle | An attestation MUST carry a handle: an identifier determined by the membership and stable for its life, so the peer cannot change it without registering again. Verifiable evidence attaches to a peer through it ([Section 4.2.1](#421-verifiable-evidence)). |
| Bounded expiry | An attestation MUST stop verifying within a bound of its membership ending, expressed in time or in membership updates. The bound belongs to the mechanism and sets how long a node stays eligible after its membership ends. A deployment whose bound is counted in updates MUST advance its membership state often enough to bound it in time as well. |
| Availability before contact | An attestation MUST be obtainable for a discovered peer before any packet is routed through it, because path selection precedes contact ([Section 5.1](#51-with-path-selection)). |

A peer's attestation MUST be carried
on the same channel by which the DoS protection mechanism already carries evidence to every node
([Section 5.3](#53-with-dos-protection)).
Discovery gives each node a partial sample of the network ([Section 2](#2-terminology)),
so a duplicate presented to two parts of it might otherwise meet at no node at all.
Published, every node can verify every attestation,
and two valid attestations under one handle are evidence wherever they appear.

A construction of the following form is RECOMMENDED:
the peer proves in zero knowledge,
against the membership state every node already holds,
that it holds a membership in the DoS protection mechanism's set;
the proof is bound to the peer's mix identity and signed under it;
and the handle is derived from the membership secret.
This satisfies every property above:
a verifier learns that the peer is a member and nothing more,
the peer cannot change its handle without registering again,
and two identities attested under one membership carry the same handle.

Together these properties supply the Sybil resistance the Mix Protocol lacks:
they require a live membership for eligibility,
and limit a membership to one eligible peer
([Section 7.1](#71-what-the-record-does-not-do)).

A node MUST hold at most one attestation per peer,
the most recently verified.

A node that changes its mix identity requires a new membership,
since the old and the new identity under one handle are two valid attestations carrying it.
Eligibility follows the handle, not the peer.
A peer whose new attestation carries a different handle is attesting a different membership,
so evidence held against the old handle does not apply to it,
and the peer returns to the eligible set at the cost of that new membership
([Section 7.7](#77-whitewashing)).
The node's own observation counters are keyed by the peer and are not reset.

### 4.2 Inputs

#### 4.2.1 Verifiable Evidence

The node records, per peer:

- `slashed`: whether the node holds verifiable evidence against the peer's handle:
  that the membership violated its rate limit,
  or that two attestations carry that handle ([Section 4.1](#41-membership-attestation)).

A node MUST verify evidence itself before setting `slashed`.
A claim it cannot verify is a report and MUST be discarded.

A node MUST retain the handles it holds evidence against
independently of its peer records,
and MUST check each newly verified attestation against them,
so that evidence arriving before a peer is discovered is not lost.

#### 4.2.2 Proof and Packet Observations

The node counts, per peer:

- `proof_failures`: proofs received from the peer that failed verification
  ([Mix DoS Protection Section 8.2.2](./mix-dos-protection.md#822-proof-verification)).
- `framing_failures`: packets received from the peer that the node could not accept as Sphinx packets at all:
  wrong length,
  or transport-level framing errors.
- `replays`: packets received from the peer whose tag the node had already seen within its replay-detection window.

Each is recorded against the immediate predecessor,
which alone could have caused it ([Section 7.3](#73-manipulating-observations)).
Two limits follow:

- A replay is attributable only within the predecessor's own detection window,
  beyond which it could not have known the tag was a repeat.
- A failure of the per-hop integrity check or of decryption
  MUST NOT be recorded against the predecessor,
  since a malicious originator could also corrupt any hop's layer
  while leaving the layers before it intact.

This specification assumes the per-hop generated proof architecture
([Mix DoS Protection Section 4.2](./mix-dos-protection.md#42-per-hop-generated-proofs))
that [LOGOS-MIXNET](./logos-mixnet.md#architecture) mandates.
Under sender-generated proofs the proof came from the originator,
and proof failures MUST NOT be recorded against the predecessor.

#### 4.2.3 Loop Return Outcomes

Where cover traffic uses [Loopix](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska)-style loops,
a loop that does not return
implicates its path as a whole and no hop in particular.

Loop outcomes MUST NOT affect eligibility or service,
and a missing return MUST NOT be attributed to any single hop.
A single dropped loop says only that some hop dropped it,
and local statistics cannot separate a dropping hop from an honest hop that shares paths with it
([Section 7.3](#73-manipulating-observations)).
Isolating one requires evidence pooled across nodes,
as in [Miranda](https://www.usenix.org/conference/usenixsecurity19/presentation/leibowitz),
which this specification leaves to future work ([Section 9](#9-future-work)).
A node MAY record loop outcomes for its own diagnostics.

#### 4.2.4 Signals Not Used

The record MUST NOT include:

- Reports from other nodes about a peer that the node cannot verify.
- Latency, throughput, or delay measurements.
  A mix node's delays are sender-chosen,
  and a fast node is not a better node.
- Whether the peer forwards the node's own traffic reliably,
  measured through loop returns, SURB replies, or any other delivery signal.

### 4.3 Eligibility

A peer is eligible when both of the following hold:

1. The node holds a valid, unexpired membership attestation for the peer ([Section 4.1](#41-membership-attestation)).
2. `slashed` is false.

Eligibility depends on global inputs only.
Observations MUST NOT affect it.
A node MUST NOT relax these conditions,
and MUST continue discovery when too few peers satisfy them.
Two nodes with the same membership state and the same evidence therefore reach the same verdict on any peer both have discovered.

This specification adds no per-peer threshold of its own:
the registry's admission criteria are met before a membership exists ([Section 5.3](#53-with-dos-protection)),
so membership itself carries them.
Condition 2 anticipates the registry,
because evidence reaches a node before the membership state that removes the member does.

Eligibility is evaluated when the peer is discovered,
when it publishes a new attestation,
and when verifiable evidence about it arrives.
A node MUST re-verify the attestations it holds whenever its membership state updates,
since an attestation ceases to verify once that state advances past it.
A peer that becomes ineligible on `slashed` stays ineligible for the life of that membership.

### 4.4 Service

A node refuses service to a peer when any of the following holds within the current epoch:

- `proof_failures ≥ proof_failure_cap`.
- `framing_failures ≥ framing_cap`.
- `replays ≥ replay_cap`.

Counters decay at each epoch boundary by the factor `decay`, `0 < decay < 1`,
and a counter below 1 is treated as zero.
Refusal expires after `service_ttl`,
and the peer's counters are reset when it does,
so a further refusal requires fresh observations.

A node that refuses service to a peer MAY drop the peer's packets
before proof verification and before Sphinx processing,
sparing it even the cost of verifying a proof it would reject.
Packets from a peer include packets it forwards for others,
so refusing service drops traffic of honest senders whose paths crossed that peer for the duration of the refusal.

**Bounded refusal.**
The number of peers a node refuses service to MUST NOT exceed `θ · D`, `0 < θ < 1`.
When the cap is reached,
the node MUST keep the existing refusals
and MUST record further candidates without acting on them.
A node that refused service to a large fraction of its peers would isolate itself from the network,
which is the outcome an adversary feeding the record would seek ([Section 7.3](#73-manipulating-observations)).

Service refusal MUST NOT affect eligibility.
A peer the node refuses to serve remains eligible for the node's own paths if its global inputs qualify.

### 4.5 Effects

The record has exactly two effects.

1. **Path selection.**
   Candidates MUST be drawn uniformly from the eligible set,
   whether a strategy uses each draw once or holds it across packets
   ([Section 5.1](#51-with-path-selection)).
   This applies to every path purpose:
   forward paths,
   SURB return paths,
   and cover paths.

2. **Service.**
   Packets from a peer the node refuses to serve are dropped as specified in [Section 4.4](#44-service).
   This refusal is the record's only effect on packet handling.

The record MUST NOT affect delay selection, cover emission, rate limits, or proof generation.

### 4.6 Data Structures

A reputation record is the pair of an eligibility entry,
whose fields are global inputs and the eligibility they yield,
and a set of misbehavior counters,
whose fields are the node's own observations and the service decision they yield.
A node also holds two node-level sets:
the handle and identity of each published attestation it has verified ([Section 4.1](#41-membership-attestation)),
and the handles it holds evidence against ([Section 4.2.1](#421-verifiable-evidence)).

```text
Eligibility {
  peer_id:            PeerId
  handle:             bytes          // from the membership attestation
  attested_until:     Timestamp      // expiry, where the mechanism expresses it as a time
  slashed:            bool           // verifiable evidence against this handle
  eligible:           bool           // derived, Section 4.3
}

MisbehaviorCounters {
  peer_id:            PeerId
  proof_failures:     float          // decayed counter
  framing_failures:   float          // decayed counter
  replays:            float          // decayed counter
  refused_until:      Timestamp?     // absent when served
}

ReputationRecord {
  eligibility:        Eligibility
  misbehavior:        MisbehaviorCounters
}

PublishedHandles {
  by_handle:          map<bytes, PeerId>   // node-level; Section 4.1
}

SlashedHandles {
  handles:            set<bytes>           // node-level; evidence verified against each
}

ReputationConfig {
  proof_failure_cap:  uint
  framing_cap:        uint
  replay_cap:         uint
  service_ttl:        Duration
  decay:              float
  θ:                  float
}
```

## 5. Integration

### 5.1 With Path Selection

A strategy's pool of mix nodes is the node's discovered set,
and the eligible nodes it obtains from that pool are the eligible set.
A pool chosen for a strategy rather than taken from what the node discovered
is a sender-chosen set and is out of scope ([Section 8](#8-out-of-scope)).

Every position of every path MUST be drawn from the eligible set.
Where a strategy holds nodes across packets,
whether as fixed positions or as a local topology,
those nodes MUST be drawn uniformly when first selected,
and a node that becomes ineligible MUST be replaced according to the strategy's own rotation rules.

Liveness is the strategy's own concern;
this specification decides eligibility only.
A strategy MUST NOT use any field of the record other than the eligible bit.

### 5.2 With Cover Traffic

The record takes no input from cover traffic and alters no part of it.
Loop outcomes are excluded for the reason given in [Section 4.2.3](#423-loop-return-outcomes);
a node that records them for diagnostics needs each loop's path and whether it returned.

### 5.3 With DoS Protection

Membership attestations and verifiable evidence are both products of the DoS protection mechanism,
verified with its procedures against its membership state ([Section 4.1](#41-membership-attestation)).
Proof failures come from its per-packet verification.

The channel on which the mechanism distributes evidence carries one further item
under this specification:
each peer's attestation ([Section 4.1](#41-membership-attestation)).
This is one proof per peer per attestation refresh.
It makes the full set of participating identities enumerable,
which a determined observer could already approximate by crawling discovery,
and it is what makes one membership to one peer checkable at every node
rather than only where two attestations happen to meet.

This specification relies on the registry to enforce, before a member is admitted:

- a stake floor,
  so that a membership costs locked funds;
- an activation delay,
  so that a registration becomes a membership only after a deployment-defined delay,
  and a registration surge cannot produce usable memberships until it has passed;
  proof-of-stake systems apply the same rule at validator activation,
  and Tor's Guard flag requires a relay to have been known for a period before it counts;
- removal from the membership state on slashing.

A stake floor and removal on slashing are ordinary requirements of a staking registry.
The activation delay is not,
and is a requirement this specification places on the DoS protection mechanism.

The record does not modify rate limits;
reputation-differentiated rate limits are out of scope ([Section 8](#8-out-of-scope)).

### 5.4 Capacity

Restricting path selection to eligible nodes concentrates the network's forwarding onto those nodes.
This rule bounds how much a node may originate
before the eligible ones cannot carry what they are given.

Let `C` be the number of packets a node originates per epoch,
`F` its forwarding budget,
the rate-limit allowance left after the origination share
([Mix Cover Traffic Section 4](./mix-cover-traffic.md#4-rate-limit-budget-model)),
`L` the mix path length ([Mix Protocol Section 6](./mix.md#6-pluggable-components)),
and `e` the fraction of nodes currently eligible.
Where forwarding budgets differ,
`F` is the smallest among eligible nodes,
because selection is uniform and the load falls equally on each.

Every node originates, whether or not it has real traffic
([Mix Cover Traffic](./mix-cover-traffic.md)),
so a network of `N` nodes originates `N · C` packets per epoch,
each relayed `L` times,
spread over `e · N` eligible nodes.
`N` cancels, and each eligible node forwards `L · C / e` packets per epoch:

```text
L · C / e ≤ F
C ≤ e · F / L
```

At `L = 3` and `F = 75`,
a deployment in which every node is eligible may originate `C = 25`.
If only 60% are eligible it must drop to `C = 15`.
Above that bound eligible nodes reach their forwarding limit and drop the excess,
so paths fail at a rate that rises as the eligible fraction falls.
A deployment MUST set `C` to satisfy this at the eligible fraction it sustains.

No node can measure `e` directly.
Every node can verify every published attestation
([Section 4.1](#41-membership-attestation)),
so it can count the eligible nodes exactly,
but not the nodes that publish no attestation.
A node's own `k / D` estimates `e`.

## 6. Parameters

| Parameter | Recommended | Rationale |
|---|---|---|
| `proof_failure_cap` | 3 per epoch | One failure can be version skew; three in one epoch is not. |
| `framing_cap` | 3 per epoch | Same. |
| `replay_cap` | 3 per epoch | Same. |
| `service_ttl` | 24 hours | Long enough to matter; short enough to recover from a transient fault. |
| `decay` | 0.5 per epoch | Halves counters every epoch. |
| `θ` | 0.05 | At most 5% of `D` refused service; a node cannot isolate itself. |

The bound on how long an attestation outlives its membership ([Section 4.1](#41-membership-attestation))
belongs to the attestation mechanism and is not a parameter of this specification.
The registry's stake floor and activation delay are parameters of the DoS protection mechanism,
not of this specification.

## 7. Security and Privacy Considerations

### 7.1 What the Record Does Not Do

The record does not lower the fraction of adversarial nodes among eligible nodes
against an adversary that registers, stakes, waits out the activation delay, and forwards correctly.
What the record does is allow only peers holding a valid attestation to be drawn into paths,
and drop a peer from every node's eligible set once evidence against its membership arrives.

A hop need not forward to be useful to an adversary:
it receives packets,
decrypts its own layer,
and learns its predecessor and its successor.
The DoS protection mechanism only controls forwarding by a member and its rate:

- It stops a non-member forwarding, but not a non-member being selected.
- It bounds the rate a membership may spend,
  but not the number of mix identities that may share a membership,
  dividing the rate between them.

Eligibility closes both: it requires a membership,
and a membership buys one eligible peer.
The record also lets a node stop spending resources on peers that send it invalid traffic.

Let `p` be the adversarial fraction of eligible nodes.
For a path of `L = 3` hops sampled uniformly from the eligible set,
the probability that a packet is fully traced is `p^3` per packet,
and after `n` packets `1 − (1 − p^3)^n`.
The record does not change `p`;
the registry's admission criteria do, through the cost of membership.
The expression assumes a distinct membership behind each hop,
which holds only because one membership attests one mix identity
and a second is detected wherever it appears ([Section 4.1](#41-membership-attestation)).
Without it `p` would be the adversary's share of mix identities rather than of memberships,
and mix identities are free.

| `p` | median packets to full trace | `n = 300` | `n = 4000` | `n = 9000` |
|---|---|---|---|---|
| 0.10 | 693 | 26% | 98% | 100% |
| 0.05 | 5,545 | 3.7% | 39% | 68% |
| 0.02 | 86,643 | 0.2% | 3.1% | 6.9% |

The `p` an application should assume is the fraction of eligible peers a [realistic adversary](https://www.freehaven.net/anonbib/cache/ccs2013-usersrouted.pdf) can afford
after paying the registry's stake floor and activation delay for each.

### 7.2 Fingerprinting Through the Eligible Set

An adjacent hop sees which peers a node forwards to.
If the choice of next hop depended on something particular to the node choosing,
that node's set would be visible over time through the peers it never uses
and would name the node to every hop that sees it,
a [route fingerprint](https://www.cl.cam.ac.uk/~rnc1/anonroute.pdf).
Under this specification eligibility is computed from global inputs only,
so a peer's eligibility does not depend on which node evaluates it,
and the record adds no node-specific variation to the choice of next hop.

Nodes do nonetheless draw from different candidate pools.
Discovery returns a bounded, periodically refreshed sample of the network
([Mix Protocol Section 6.1](./mix.md#61-discovery)),
so two nodes rarely hold the same discovered peers.
That difference is a property of the discovery mechanism,
not of this record:
it is present whether or not a deployment runs this specification,
and it is why [Mix Protocol Section 6.1](./mix.md#61-discovery)
asks a discovery mechanism to support unbiased random sampling.
Applied to the same discovered peers,
this specification excludes the same peers at every node.

Service refusal is local and can differ between nodes,
but it affects only which peers a node accepts packets from,
never which peers it forwards to.
An adjacent hop observing a node's outgoing traffic learns nothing about its service refusals.

A small eligible set might seem to narrow who could have sent an observed packet.
However, since every sender draws every hop uniformly from its eligible peers,
an observed hop is equally likely under every sender that has discovered it,
and the anonymity set of any single observation is the set of those senders.
The size of the eligible set bears on forwarding load ([Section 5.4](#54-capacity)),
not on the anonymity of a sender.

### 7.3 Manipulating Observations

An adversary can try to shape what a node observes,
against an honest peer or in its own favour.

**Through loops.**
A node learns only whether a loop returned, never which hop dropped it.
An adversary can still bias the statistic by dropping whatever its nodes carry
to or from a targeted peer.
Every failure it manufactures implicates that peer,
while each of its own nodes appears in only its share of them,
so the target alone looks unreliable.
[Section 4.2.3](#423-loop-return-outcomes) keeps loop outcomes out of both decisions.

**Through malformed packets.**
An originator can corrupt the Sphinx layer of any hop while leaving earlier layers intact.
An honest predecessor then delivers a packet whose integrity check fails at the next hop,
at the cost of just one origination slot to the adversary.
If such failures were attributed to the predecessor,
the adversary could choose which honest peers each victim refuses to serve,
and could write a distinct refusal list into every victim for `service_ttl`.
[Section 4.2.2](#422-proof-and-packet-observations) therefore records only failures the predecessor must have caused.

**Through self-inflicted refusal.**
An adversarial peer can send invalid traffic to a chosen node until that node refuses it service.
This gains no influence over the node's paths:
refusal does not affect eligibility,
so the node's outgoing traffic is unaltered
([Section 7.2](#72-fingerprinting-through-the-eligible-set)).
It does consume one of the node's bounded refusals ([Section 9](#9-future-work)).

An adversary cannot feed positive signals,
because there are none:
a peer that behaves gains nothing beyond eligibility and service.

### 7.4 Steering Path Selection

Eligibility depends on global inputs only.
An adversary cannot alter a node's eligible set except through the membership state or through verifiable evidence,
and evidence of a rate-limit violation cannot be fabricated against an honest peer.
Path selection at a node is therefore not steerable through the record.

### 7.5 Eligible-Set Exhaustion

A node whose eligible set falls below the path length cannot build a path.
The node does not relax its conditions to recover,
and continues discovery instead ([Section 4.3](#43-eligibility)).

Exhaustion is ordinarily per-node and temporary,
since nodes draw from different candidate pools
([Section 7.2](#72-fingerprinting-through-the-eligible-set));
a bootstrapping node is the common case.
Exhaustion at every node at once is a deployment failure,
from an attestation mechanism that stops keeping members attested or from mass slashing,
and no node can recover from it locally.

### 7.6 Registry Trust

A registry that admits a member before it has met the admission criteria makes that member eligible early.
This is the trust the DoS protection mechanism already places in its membership state,
and an attestation does not change it:
a peer whose attestation does not verify is not eligible.

An attestation publishes a handle, a persistent pseudonym,
alongside a mix identity that is already persistent.
It does not link a peer to its registry entry or to the account that funded its stake,
and it does not make the peer's per-packet proofs linkable to its handle.

### 7.7 Whitewashing

A slashed member can register again,
attest the same mix identity under a new handle,
and return to the eligible set of every node that discovers it, once the activation delay has passed.
Evidence against the old handle does not carry over.
The penalty for an offence is therefore the price of a new membership:
fresh stake and the delay, set by the registry's admission criteria.
Following a member across registrations would require linking memberships
to the account that funds them,
which the minimal disclosure property forbids ([Section 4.1](#41-membership-attestation)).
The trade is deliberate: unlinkable registration over persistent penalties.

## 8. Out of Scope

The following are explicitly out of scope for this specification:

- Reputation-differentiated rate limits.
  Whether well-behaved nodes may carry a higher rate limit is a change to the DoS protection mechanism.
- Shared, gossiped, or third-party attested reputation.
- Trusted sets chosen by the sender.
  A sender-chosen set of preferred nodes is a fingerprint ([Section 7.2](#72-fingerprinting-through-the-eligible-set));
  shared [guard sets](https://petsymposium.org/2015/papers/05_Hayes.pdf) require many more senders than relays
  and are left to a deployment that has them.
- Detection of passive adversarial nodes.
- The registry's admission policy.
  The stake floor and activation delay this specification relies on ([Section 5.3](#53-with-dos-protection))
  are parameters of the DoS protection mechanism.
- The construction of the membership attestation.
  This specification states the properties one MUST have ([Section 4.1](#41-membership-attestation));
  how it is built and carried is out of scope.

## 9. Future Work

- **Loop outcomes as evidence**:
  Loop outcomes isolate a dropping hop only when nodes pool evidence
  and reason about links rather than nodes,
  as in [Miranda](https://www.usenix.org/conference/usenixsecurity19/presentation/leibowitz).
  That needs an interface from the cover traffic component reporting per-loop path and outcome,
  as [Mix Cover Traffic Section 11.2](./mix-cover-traffic.md#112-path-health-monitoring) anticipates,
  and a way to exchange outcomes that cannot be forged against an honest peer.
- **Contendable refusal bound**:
  The bound on refusals ([Section 4.4](#44-service)) can be consumed by an adversary's own nodes,
  whether the earliest refusals are kept or replaced.
  Whether the bound should exist,
  and whether it protects the node or the honest senders whose traffic a refusal drops,
  is unresolved.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [Mix Protocol](./mix.md)
- [Mix DoS Protection](./mix-dos-protection.md)
- [Mix Cover Traffic](./mix-cover-traffic.md)
- [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt)

### Informative

- [LOGOS-MIXNET](./logos-mixnet.md)
- [Tor Directory Protocol, Assigning flags in a vote](https://spec.torproject.org/dir-spec/assigning-flags-vote.html)
- [A Reputation System to Increase MIX-net Reliability](https://www.freehaven.net/anonbib/cache/mix-acc.pdf)
- [Reliable MIX Cascade Networks through Reputation](https://www.freehaven.net/anonbib/cache/casc-rep.pdf)
- [Route Fingerprinting in Anonymous Communications](https://www.cl.cam.ac.uk/~rnc1/anonroute.pdf)
- [No Right to Remain Silent: Isolating Malicious Mixes](https://www.usenix.org/conference/usenixsecurity19/presentation/leibowitz)
- [Users Get Routed: Traffic Correlation on Tor by Realistic Adversaries](https://www.freehaven.net/anonbib/cache/ccs2013-usersrouted.pdf)
- [Guard Sets for Onion Routing](https://petsymposium.org/2015/papers/05_Hayes.pdf)
- [The Loopix Anonymity System](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska)
