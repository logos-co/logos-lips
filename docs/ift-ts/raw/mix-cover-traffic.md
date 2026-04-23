# Mix Cover Traffic

| Field        | Value                        |
| ------------ | ---------------------------- |
| Name         | Mix Cover Traffic            |
| Slug         | TBD                          |
| Status       | raw                          |
| Category     | Standards Track              |
| Editor       | Prem Prathi <prem@status.im> |
| Contributors |                              |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

This document specifies the cover traffic architecture for the [libp2p Mix Protocol](./mix.md).
The architecture ensures that an observer cannot distinguish cover traffic from locally originated messages
by observing a node's emission pattern.
It defines how cover packets are generated and emitted,
how the rate-limit budget is shared across cover and non-cover traffic,
and specifies the Constant-Rate cover traffic strategy, with Poisson-Rate as a future consideration in §11.5.

## 1. Introduction

The Mix Protocol provides sender anonymity through layered encryption and per-hop delays.
However, without cover traffic,
an adversary observing a mix node's emission rate can mount several attacks:

- **Traffic analysis**: by correlating emission bursts with known events,
  an adversary can link a node's activity periods to specific senders or recipients.
- **Intersection attack**: by observing which nodes are active each time a message reaches its destination,
  an adversary can progressively narrow down the set of possible senders across multiple messages.
- **Timing correlation**: by matching idle and active periods across mix nodes,
  an adversary can correlate ingress and egress packets.

All three attacks rely on the same weakness:
a node's emission pattern leaks information about whether it is carrying non-cover traffic.

Cover traffic addresses this by ensuring a node's emission pattern does not depend on non-cover traffic volume,
making it indistinguishable to an observer whether the node is sending locally originated messages or none at all.

The Mix Protocol defines cover traffic as a pluggable component (see [Mix Protocol §6.4](./mix.md#64-cover-traffic)).
This specification provides a concrete instantiation of that component,
defining the cover traffic architecture, the rate-limit budget model, and two concrete scheduling strategies.
The architecture is designed to be compatible with the DoS protection mechanism defined in [Mix DoS Protection](./mix-dos-protection.md)
and specifically with the [Mix RLN DoS Protection](./mix-spam-protection-rln.md) mechanism.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Other terms used in this document are as defined in the [libp2p Mix Protocol](./mix.md) and [Mix DoS Protection](./mix-dos-protection.md).

The following additional terms are used throughout this specification:

- **Cover Packet**
  A dummy Sphinx packet that carries no application payload
  and is indistinguishable from non-cover Sphinx packets in structure, size, and routing behavior.

- **Slot**
  A single rate-limit token within an epoch's budget of `R` tokens, as defined by the DoS protection mechanism.
  Each outgoing packet — whether cover or non-cover — consumes exactly one slot.

- **Slot Pool**
  The collection of rate-limit slots available for a given epoch.

- **Epoch**
  A fixed time window of duration `P` seconds during which each mix node is permitted to emit at most `R` packets,
  as enforced by the DoS protection mechanism.

## 3. Design Principles

The cover traffic architecture is guided by the following principles:

- **Sender unobservability**: A node's emission pattern must not depend on non-cover traffic volume,
  making it indistinguishable to an observer whether the node is carrying non-cover traffic or not.
- **Indistinguishability**: Cover packets are structurally identical to non-cover Sphinx packets in size and routing behavior,
  preventing packet-level classification. ([Mix Protocol §6.4](./mix.md#64-cover-traffic))
- **Self-exit**: Cover packets SHOULD use loop paths where the originating node is also the exit node.
  This ensures the dummy payload is never decrypted by an external party,
  eliminating the risk of cover classification at the exit.
- **DoS protection compliance**: All cover traffic operates within the rate-limit budget `R` enforced per epoch.
  Proofs are epoch-bound and unused slots are discarded at epoch boundaries. ([Mix DoS Protection](./mix-dos-protection.md))
- **Slot integrity**: Each rate-limit slot is consumed at most once on the wire per epoch.
  When a slot is claimed for non-cover use, its pre-computed cover proof is discarded immediately to prevent reuse.
- **Mix node only**: Cover traffic is generated only for mix nodes that act as intermediate nodes forwarding mix traffic
  and participate continuously in the network.
  Initiating-only nodes are mostly short-lived with dynamic identifiers and do not forward traffic,
  making cover traffic neither practical nor beneficial for them.
- **Pre-computation**: As an optimization, cover packets and their proofs MAY be generated during epoch `N-1`,
  so they are ready to emit at the start of epoch `N` without any cryptographic work at emission time.

## Overview

A mix node plays multiple roles at once: it sends its own messages, relays messages for other nodes, and ideally hides which of these it is doing.
Without protection, an observer watching the node's outgoing packets can tell when it is active, how busy it is, and when it is idle —
enough to link users to their messages through traffic patterns.

Cover traffic addresses this by emitting additional dummy packets that look identical to real mix traffic from the outside.
An observer still sees packets leaving the node,
but can no longer tell from the pattern alone whether those packets are real or dummy.

The node operates under a rate limit that bounds total packets emitted per epoch ([§4](#4-rate-limit-budget-model)).
Every packet — cover, locally originated, or forwarded — consumes one slot from this shared budget.
Forwarding typically takes a large share of the budget because each originated packet traverses multiple hops,
so the maximum cover rate is naturally bounded below the total.

Cover is emitted at a steady configurable rate, up to this bound ([§7.1](#71-constant-rate-cover-traffic)).
A `cover_rate_fraction` parameter scales cover down from the maximum,
leaving headroom in the budget for spikes in real traffic.
Real traffic (locally originated and forwarded) claims slots from the same pool as it arrives;
cover yields whatever slots remain.

Cover packets follow round-trip paths — the sender is also the final destination,
so the dummy payload is never decrypted by another party ([§5.1](#51-cover-packet-transmission)).
For efficiency, cover packets and their rate-limit proofs MAY be pre-built during the previous epoch ([§6.1](#61-at-epoch-boundary))
and revalidated at send time in case the underlying state has changed ([§6.5](#65-pre-computed-proof-validation-at-send-time)).

Each epoch begins by discarding previous state and initializing a fresh slot budget,
loading any pre-built cover packets prepared during the prior epoch.
Throughout the epoch, cover, locally originated, and forwarded packets independently claim slots.
Near the midpoint, the node starts pre-computing cover packets for the next epoch.
At epoch end, unused slots are discarded and the cycle repeats.

The specification focuses on the Constant-Rate strategy.
An alternative Poisson-Rate strategy, where cover emission times are randomized, is kept for future consideration in [§11.5](#115-poisson-rate-cover-traffic).

## 4. Rate Limit Budget Model

Each mix node receives a budget of `R` slots per epoch from the DoS protection mechanism.
Cover emission, locally originated message sending, and packet forwarding all draw from the same pool.
Since each originated packet traverses `L` forwarding hops — where `L` is the mix path length
as defined in [Mix Protocol §6](./mix.md#6-pluggable-components) —
forwarding traffic naturally consumes a significant portion of the budget.

If every node originates at rate `C` packets per epoch (cover plus locally originated combined),
each node forwards approximately `C * L` packets per epoch.
Since origination and forwarding share the same budget `R`:

```
C + C * L ≤ R
C ≤ R / (1 + L)
```

`R / (1 + L)` is therefore the **upper bound on total origination**,
not a target for cover emission alone.
Cover rate does not need to be explicitly reduced by a node's locally originated rate,
because the slot pool is self-balancing (see below).

This means the actual cover traffic emitted by a node is always less than `R` and depends on:

- **Path length `L`**: longer paths consume more forwarding slots, leaving fewer for cover.
  For `L=3`, approximately 25% of slots are available for cover and locally originated message sending.
- **Network size `N` and forwarding variance**: with random path selection, forwarding load is not uniform.
  Some nodes receive more forwarding traffic than the equilibrium average, leaving even fewer slots for cover.
  The actual cover output per node therefore varies with network conditions.

The slot pool is self-balancing — no explicit origination rate constraint is needed.
Heavier forwarding load automatically leaves fewer slots for cover; lighter load leaves more.

**Note on DoS protection architecture:**
The self-balancing pool model assumes per-hop generated proofs
([Mix DoS Protection §4.2](./mix-dos-protection.md#42-per-hop-generated-proofs)),
where forwarding consumes slots from the node's own `R` budget.
With sender-generated proofs ([Mix DoS Protection §4.1](./mix-dos-protection.md#41-sender-generated-proofs)),
forwarding nodes only verify proofs and do not consume their own `R`,
but cover emission must still account for forwarding load to maintain constant total output.
The budget model and slot pool semantics for sender-generated proofs require separate analysis
and are deferred to [§11.4](#114-budget-model-for-sender-generated-proofs).

## 5. Integration with the Mix Protocol

The cover traffic mechanism integrates with the Mix Protocol at four points in packet processing.

Cover packets are identified by the reserved protocol codec `"/mix/cover/1.0.0"`.
This codec is used as the origin protocol codec during Sphinx packet construction
and is checked during exit processing to distinguish cover packets from application traffic.

All mix nodes in a deployment SHOULD use the same strategy type and parameters
to ensure uniform emission patterns across the anonymity set.
The configured path length `L` for cover packets
MUST match the path length used for locally originated messages
as defined in [Mix Protocol §6](./mix.md#6-pluggable-components).

### 5.1 Cover Packet Transmission

**Trigger:** The configured strategy schedules a cover emission.

**[During Sphinx packet construction](./mix.md#85-packet-construction):**
The mechanism constructs a cover Sphinx packet
following the same construction procedure as a locally originated message,
with the following differences:

- The mix path is a loop path — the final hop routes the packet back to the originating node.
- The origin protocol codec MUST be set to the cover traffic codec defined in [§5](#5-integration-with-the-mix-protocol).
  This codec is recognized by the Mix Protocol during exit processing
  to identify returning cover packets (see [§5.4](#54-cover-packet-reception)).
- The application message content SHOULD be filled with cryptographically random bytes.
  Random payloads provide defense-in-depth against partial path compromise
  and ensure that cover packets remain indistinguishable from non-cover traffic
  if the design evolves to support non-loop cover paths in the future.
- If pre-computation is enabled, the pre-built cover packet is used directly without re-construction.

**Wire format:**
Cover packets use the exact Sphinx packet format defined in [Mix Protocol §8](./mix.md#8-sphinx-packet-format).
No additional fields or framing are introduced.
A cover packet on the wire is indistinguishable from a non-cover traffic packet,
ensuring that intermediary nodes and external observers cannot classify packets as cover or non-cover.

The cover packet is then transmitted to the first hop following the standard Mix Protocol transmission procedure.

### 5.2 Non-Cover Slot Claim

**Procedure:** `ClaimSlot() -> success`

**Trigger:** The Mix Protocol needs to send a message or forward a packet and requires a slot from the budget.

The mechanism atomically claims an available slot from the pool.
The caller then generates a DoS protection proof
via `GenerateProof(binding_data)` ([Mix DoS Protection §8.2.1](./mix-dos-protection.md#821-proof-generation)),
where `binding_data` is the packet-specific data as defined by the DoS protection mechanism.
If no slot is available, the packet SHOULD be handled as follows to avoid hitting DoS protection limits:

- **Locally originated messages**: queued for the next epoch.
- **Forwarded packets**: dropped.

When a slot is claimed for non-cover use,
the pre-built cover packet associated with that slot MUST be discarded immediately.
Its proof MUST NOT be sent on the wire.

### 5.3 Epoch Boundary

**Procedure:** `ResetEpoch(epoch) -> void`

**Trigger:** The DoS protection mechanism signals the start of a new epoch
via `OnEpochChange` ([Mix DoS Protection §8.2.3](./mix-dos-protection.md#823-epoch-change-notification)).
The Mix Protocol MUST call `ResetEpoch` before processing any packets in the new epoch.

The mechanism refreshes the slot pool for the new epoch:
all remaining slots from the previous epoch are discarded,
and a new pool of `R` slots is initialized.
If pre-computation is enabled, the pre-built cover packets prepared during the previous epoch
are loaded into the new pool.

Cover packets emitted near epoch end may arrive at later hops in a subsequent epoch.
The DoS protection mechanism is responsible for accepting proofs within a configurable epoch window
(_e.g.,_ the `max_epoch_gap` parameter in [Mix RLN DoS Protection](./mix-spam-protection-rln.md)).

### 5.4 Cover Packet Reception

**Trigger:** The Mix Protocol completes [exit processing](./mix.md#864-exit-processing) on a received Sphinx packet
and extracts the origin protocol codec from the decrypted payload.

If the codec matches the cover traffic codec (see [§5](#5-integration-with-the-mix-protocol)),
the Mix Protocol MUST handle the packet internally without handing off to the Mix Exit Layer.
The packet SHOULD be silently discarded.
Implementations MAY use this reception event for diagnostics such as path health monitoring
(see [§11.2](#112-path-health-monitoring)).

This is handled by the cover traffic codec check
in [Mix Protocol §8.6.4](./mix.md#864-exit-processing) step 4,
which intercepts cover packets before handing off to the Mix Exit Layer.

Since cover packets use loop paths (see the self-exit principle in [§3](#3-design-principles)),
the exit node is always the originating node itself.
The cover traffic codec is therefore never visible to any external party.
If a cover packet were routed to a different exit node,
that node would detect the cover traffic codec during exit processing
and classify the packet as cover traffic.
Although the Sphinx construction prevents the exit from identifying the sender,
a malicious exit could accumulate cover-to-non-cover traffic ratios over time,
leaking information about network-wide cover strategy and volume.

### 5.5 Data Structures

```
PrebuiltCoverPacket {
  slot_id:        bytes                 // Slot identifier within the epoch
  packet:         bytes                 // Pre-built wire-format packet (Sphinx packet + DoS protection proof), ready to transmit
  path:           []bytes               // Ordered list of mix node identifiers on the cover path
  created_at:     uint64                // Unix timestamp (seconds) when this packet was constructed
}
```

```
SlotPool {
  epoch:              uint64            // The epoch this pool belongs to
  cover_queue:        []PrebuiltCoverPacket  // Pre-built cover packets, dequeued on emission
}
```

```
CoverTrafficConfig {
  strategy_type:  enum { CONSTANT_RATE, POISSON, NONE }
  cover_rate_fraction:  float64    // f ∈ (0.0, 1.0], scales cover rate relative to the maximum safe rate (see §7); RECOMMENDED default 0.7
  // Strategy-specific parameters (see §7):
  // For CONSTANT_RATE: emission_rate (float64, packets per second)
  // For POISSON:       lambda_cover (float64, packets per second)
}
```

## 6. Node Responsibilities

This section defines what each mix node MUST do at each integration point.

The slot pool ([`SlotPool`](#55-data-structures)) is a token bucket of `R` slots per epoch.
Each outgoing packet — cover or non-cover — atomically claims one slot.
Slot claim operations MUST be atomic.

### 6.1 At Epoch Boundary

When the DoS protection mechanism signals the start of a new epoch,
the Mix Protocol instance MUST invoke `ResetEpoch` ([§5.3](#53-epoch-boundary)) on the cover traffic mechanism
to discard previous epoch state and initialize a new slot pool.

**If pre-computation is enabled (RECOMMENDED):**
The cover traffic mechanism pre-builds cover packets during epoch `N-1` for use in epoch `N`.
For each slot to be pre-computed (at most `R`; see [§11.1](#111-cover-emission-rate-estimation) for sizing guidance),
construct a cover Sphinx packet following the procedure in [§5.1](#51-cover-packet-transmission)
and generate a DoS protection proof for the **next** epoch
via `GenerateProof(binding_data)` ([Mix DoS Protection §8.2.1](./mix-dos-protection.md#821-proof-generation)).
Store the result as a [`PrebuiltCoverPacket`](#55-data-structures).
Slots without a pre-built packet will require on-demand generation if selected for cover emission.
Pre-computed proofs are bound to a specific epoch and MUST NOT be reused in subsequent epochs.

**Proof validity over time:**
Pre-computed proofs may be invalidated within their target epoch, not just across epochs.
For example, in [Mix RLN DoS Protection](./mix-spam-protection-rln.md),
accumulating membership updates can push the root used at generation time
out of the current `acceptable_root_window_size` before the epoch ends.
Implementations MUST therefore validate pre-computed proofs at send time
(see [§6.5](#65-pre-computed-proof-validation-at-send-time)).

**Fallback caveat:**
On-demand generation when pre-computation falls behind introduces timing jitter,
which shifts emissions off-grid for deterministic strategies (_e.g.,_ [§7.1](#71-constant-rate-cover-traffic))
and weakens timing unobservability.
Implementations SHOULD size the pre-computation pipeline ([§9.1](#91-pre-computation-scheduling))
to avoid the fallback path in steady state.

### 6.2 Cover Emission

The cover emission loop runs continuously as a background process.
Emission timing is governed by the configured strategy ([`CoverTrafficConfig`](#55-data-structures)).

A slot is **available** until it is claimed from the `R`-slot token bucket ([§6](#6-node-responsibilities)).
Claim is the point of consumption, not transmission:
forwarded packets within their mixing delay (see [§6.4](#64-packet-forwarding))
hold their claimed slot and are unavailable to the cover loop.

**Algorithm: Cover Emission**

> The following steps repeat continuously throughout each epoch:
>
> 1. Wait for the next emission event as determined by the configured strategy.
> 2. If the strategy schedules an emission **and** the pool has available slots (as defined above):
>    - a. Dequeue the next pre-built cover packet and atomically claim its slot.
>    - b. Validate the proof per [§6.5](#65-pre-computed-proof-validation-at-send-time).
>    - c. Transmit the `packet` field of [`PrebuiltCoverPacket`](#55-data-structures) to the first hop
>      (other fields are internal and MUST NOT be sent).
> 3. If no slots remain, suppress cover emission for the remainder of the epoch.

### 6.3 Locally Originated Message Sending

**[During Sphinx packet construction](./mix.md#85-packet-construction):**
When the Mix Entry Layer submits a locally originated message for mixification,
the Mix Protocol instance MUST first call `ClaimSlot()` ([§5.2](#52-non-cover-slot-claim)).
If no slot can be claimed, the message is queued for the next epoch.
Otherwise, the Mix Protocol instance proceeds with
[Sphinx packet construction](./mix.md#85-packet-construction).

### 6.4 Packet Forwarding

**[During Sphinx packet handling](./mix.md#86-sphinx-packet-handling):**
When the Mix Protocol instance acts as an intermediary and receives a Sphinx packet to forward,
it MUST first call `ClaimSlot()` ([§5.2](#52-non-cover-slot-claim)) before applying the mixing delay.
This ensures no two forwarded packets consume the same slot regardless of how their mixing delays overlap.
If no slot can be claimed, the packet is dropped.
Otherwise, the Mix Protocol instance proceeds with
[intermediary processing](./mix.md#863-intermediary-processing).

**Slot consumption:**
The slot is consumed on successful `ClaimSlot()`, not on transmission (see [§6.2](#62-cover-emission)).

**Send timing:**
The packet is dispatched when its mixing delay elapses,
independently of the cover emission schedule.

### 6.5 Pre-Computed Proof Validation at Send Time

Before transmitting a pre-built cover packet,
the mechanism MUST validate the carried DoS protection proof against the current state
(see [§6.1](#61-at-epoch-boundary) for rationale).
For [Mix RLN DoS Protection](./mix-spam-protection-rln.md),
this means verifying the `merkle_root` bound into the proof
is still within the node's `acceptable_root_window_size`.

If validation fails, implementations MUST either:

- **Regenerate** the proof against the current anchor, keeping the Sphinx packet body unchanged; or
- **Skip** the emission if regeneration is infeasible.

A pre-built packet with a stale proof MUST NOT be sent.
When regenerating, implementations MAY reuse the message identifier bound to the cover packet
where the DoS protection mechanism permits (see [Mix RLN DoS Protection](./mix-spam-protection-rln.md)).

## 7. Recommended Strategy

This section defines the Constant-Rate cover emission strategy, which is the normative strategy for this specification.
An alternative Poisson-Rate strategy is documented as a future consideration in [§11.5](#115-poisson-rate-cover-traffic).
Cover emission operates over the `R`-slot pool and produces irregular total output
because forwarding traffic claims slots at unpredictable times.
Cover is emitted at up to `R / (1 + L)` packets per epoch —
a maximum, not a target;
the self-balancing pool ([§4](#4-rate-limit-budget-model))
accommodates locally originated messages without explicit adjustment.

**Cover rate fraction `f`:**
The strategy takes a configurable `cover_rate_fraction` `f ∈ (0.0, 1.0]` ([§5.5](#55-data-structures))
that scales the configured cover rate relative to the maximum safe rate `R / ((1 + L) × P)`.
A value of `f = 1.0` emits cover at the maximum; lower values reduce cover output
and leave more headroom in the slot budget for locally originated messages and forwarded traffic.
The RECOMMENDED default is `f = 0.7`,
which reserves roughly 30% of the per-node slot budget as headroom against forwarding variance.
All mix nodes in a deployment SHOULD use the same `f` to preserve a uniform anonymity set across the network.

### 7.1 Constant-Rate Cover Traffic

The cover traffic mechanism emits cover packets at a fixed interval of `1 / emission_rate` seconds,
where `emission_rate = f × R / ((1 + L) × P)` packets per second.
`f` is the configured `cover_rate_fraction` ([§5.5](#55-data-structures)),
and `R / ((1 + L) × P)` is the maximum safe cover rate (achieved at `f = 1.0`).
Non-cover traffic claims slots via `ClaimSlot()` ([§5.2](#52-non-cover-slot-claim)) as it arrives,
making total output inherently irregular even though the cover emission rate is constant.

At the configured rate, up to `f × R / (1 + L)` cover packets are emitted per epoch;
the actual count is lower when locally originated messages or forwarding variance claim slots first.
The originated cover emission rate is perfectly constant,
so an adversary cannot distinguish epochs with heavy locally originated traffic from idle epochs
by observing cover timing alone.

**Tradeoff — timing separability:**
Cover packets fire on a fixed grid,
while forwarded packets fire at arrival time plus mixing delay —
always off-grid relative to the cover schedule.
Over enough observations, an adversary can separate cover from non-cover by timing alone,
regardless of forwarding load.
Constant-Rate therefore provides **volume unobservability**
(the node's emission count does not leak non-cover activity)
but not **timing unobservability**
(individual packets remain classifiable by timing).

Full timing unobservability requires the pre-scheduled emission timing enhancement
([§11.3](#113-pre-scheduled-emission-timing)),
where all traffic types share the same timing grid.
Constant-Rate is the only strategy compatible with this upgrade path,
as it requires deterministic emission times known at epoch start.

**Characteristics:**
Constant-Rate emits exactly `N = f × R / (1 + L)` cover packets per epoch (deterministic).
Pre-computation sizing is exact; no safety margin is needed.
An observer who knows `f` can infer the per-epoch forwarding count as `total_emissions - N`,
so volume unobservability holds only against observers unaware of `f` or watching aggregate rates.

## 8. Initiating-Only Node Considerations

Initiating-only nodes are short-lived with dynamic identifiers and do not forward traffic.
They SHOULD NOT generate cover traffic,
as cover traffic is only meaningful for nodes that participate continuously in the network with a stable identity —
a briefly connected node has no sustained emission pattern to protect or contribute.

**Residual privacy for initiating-only nodes:**
Without cover traffic, initiating-only nodes still retain:

- **Path anonymity**: Sphinx layered encryption prevents any single intermediary or exit
  from learning both sender and recipient.
- **Identity unlinkability**: dynamic identifiers prevent cross-session linking.

However, an adversary on the link to the first hop — or a malicious first hop itself —
can directly observe session volume and timing,
since no cover or forwarded packets are blended with originated traffic.

Deployments where this matters SHOULD route initiating-only traffic through trusted first hops.

If an initiating-only node is promoted to a mix node and becomes long-lived,
it SHOULD activate cover traffic using the Constant-Rate strategy.
During the first epoch after promotion, pre-computed cover packets are unavailable;
the node SHOULD fall back to on-demand cover packet generation for that epoch
and begin pre-computation immediately upon promotion.

## 9. Implementation Recommendations

This section provides non-normative guidance for implementers.

### 9.1 Pre-computation Scheduling

The pre-computation pipeline SHOULD be initiated at the midpoint of the current epoch
to allow sufficient time for slots to be processed before the next epoch begins.
Implementations SHOULD interleave pre-computation with normal packet processing
(_e.g.,_ yielding to non-cover traffic between slot generations) to avoid contention with ongoing packet handling.

Rather than pre-computing all cover packets in the previous epoch,
implementations MAY batch pre-computation across epochs:
an initial batch during epoch `N-1` to ensure cover packets are available at the start of epoch `N`,
with subsequent batches computed incrementally during epoch `N` itself, staying ahead of the emission schedule.
This reduces peak computational load and memory usage.

### 9.2 Pool Status Tracking

Implementations SHOULD maintain runtime counters for available slots, cover emissions, and non-cover consumptions.
These aid in diagnostics, monitoring, and tuning the emission strategy.

**Exposure restrictions:**
The non-cover consumption counter reveals the exact per-epoch count of real traffic,
which is what traffic analysis aims to recover.

Implementations MUST keep this counter (and any derived per-epoch breakdowns) in-memory only
and MUST NOT export it via metrics endpoints, structured logs, or any monitoring interface.

### 9.3 Slot Exhaustion Logging

When a forwarded packet is dropped due to slot exhaustion, implementations SHOULD log a warning.
Persistent slot exhaustion may indicate that `R` is too low for the network's forwarding load,
or that the node is under a traffic flooding attack.

### 9.4 Synchronization

Slot claim operations MUST be atomic.
Implementations may enforce this using mutexes, lock-free atomic operations, or single-threaded event loops,
depending on the concurrency model.

## 10. Security Considerations

The design principles motivating slot integrity and DoS protection compliance
are described in [§3](#3-design-principles).
This section discusses the threat context behind those principles.

### 10.1 Proof Reuse via Proof Leakage

If a pre-computed cover proof and a freshly generated non-cover proof for the same slot are both sent on the wire,
the DoS protection mechanism detects a reuse.
Depending on the mechanism, this may result in slashing or reputation loss for the node.
The slot integrity principle ([§3](#3-design-principles)) prevents this
by ensuring the cover proof is discarded before the slot is reused.

### 10.2 Slot Exhaustion Under Heavy Non-Cover Traffic

If non-cover traffic consumes all `R` slots before the epoch ends,
the node cannot emit further cover traffic.
This is a natural consequence of DoS protection compliance ([§3](#3-design-principles)).
Locally originated messages that arrive after slot exhaustion MUST be queued for the next epoch.
Cover emission ceases when no slots remain.

### 10.3 Network-Wide Cover-Rate Correlation

When a message traverses multiple mix nodes,
each node on the path claims one slot for forwarding,
slightly reducing its available cover capacity for the remainder of the epoch.
A global passive adversary observing all nodes simultaneously could in principle
detect correlated cover-rate perturbations across nodes and use them to trace message paths.

In practice, each forwarded message consumes only one slot out of `R`,
making the perturbation negligible for sufficiently large `R`.
The pre-scheduled emission timing enhancement ([§11.3](#113-pre-scheduled-emission-timing))
would eliminate this concern entirely by fixing all emission times at epoch start,
making individual slot consumption events unobservable.

### 10.4 Timing Separability of Cover and Non-Cover Packets

The default Constant-Rate strategy ([§7.1](#71-constant-rate-cover-traffic))
emits cover packets on a fixed grid while forwarded packets are dispatched at arrival time plus mixing delay.
With enough observations, a passive adversary can classify individual packets by timing alone,
regardless of forwarding load.

Constant-Rate therefore provides volume unobservability but not timing unobservability.
Under Constant-Rate, the pre-scheduled emission timing enhancement ([§11.3](#113-pre-scheduled-emission-timing))
is the only design that closes this gap,
by assigning all outgoing packets — cover, locally originated, and forwarded —
to a shared fixed-time grid determined at epoch start.

### 10.5 Cover Priority and Forwarded Packet Drops

Cover emissions occur on a schedule independent of forwarding load,
so slots consumed by cover early in an epoch are unavailable to forwarded packets arriving later.
Under uneven forwarding load, this can cause honest forwards to be dropped ([§6.4](#64-packet-forwarding))
even when total traffic stays within the `R` budget.

The `cover_rate_fraction` `f` ([§7](#7-recommended-strategy)) reduces this risk
by holding back a fraction of the per-node slot budget from cover emission,
leaving headroom for forwarding spikes.
With the RECOMMENDED `f = 0.7`, approximately 30% of the budget is reserved as headroom.
Deployments SHOULD adjust `f` based on observed network behavior;
see [§11.1](#111-adaptive-cover-rate-fraction) for adaptive tuning as a future enhancement.

## 11. Future Work

### 11.1 Adaptive Cover Rate Fraction

The `cover_rate_fraction` `f` ([§7](#7-recommended-strategy)) is currently a static deployment-wide configuration.
A future enhancement MAY define a method for nodes to adapt `f` based on observed forwarding load,
network size `N`, and path length `L`,
allowing cover rate to be tuned closer to the node's actual available budget
and reducing unnecessary cryptographic work.
Any adaptive scheme MUST preserve uniformity of `f` across the anonymity set
to avoid leaking per-node load through emission rate differences.

### 11.2 Path Health Monitoring

When cover packets are implemented as loop packets —
dummy Sphinx packets that follow a valid mix path and return to the originating node —
their return confirms path liveness.
Failures to return indicate potential node failures or active attacks along the path.
A future revision of this specification MAY define an interface for exposing loop return status
to enable path health monitoring.

### 11.3 Pre-Scheduled Emission Timing

Inspired by the [Blend Protocol](../../blockchain/raw/nomos-blend-protocol.md), a future enhancement MAY define pre-scheduled emission slots
where all outgoing packets — cover, locally originated, and forwarded — are assigned to
fixed time slots determined at epoch start.
All traffic types would share the same timing grid,
producing a perfectly periodic total output regardless of traffic mix.
This would eliminate the periodic emission pattern tradeoff noted in [§7.1](#71-constant-rate-cover-traffic),
as an observer would see uniform intervals with no way to classify individual packets.
When using Constant-Rate, this is the only design path to full timing unobservability
(see [§10.4](#104-timing-separability-of-cover-and-non-cover-packets)).

This approach is only compatible with the Constant-Rate strategy,
which provides deterministic emission times known at epoch start.
Poisson-Rate, where emission times are sampled at runtime, cannot support pre-scheduled slots.
Note that pre-scheduled slots would require changes to the mixing delay strategy
in the Mix Protocol, as forwarded packets would need to be held until their assigned slot time
rather than forwarded after the sampled delay elapses.

### 11.4 Budget Model for Sender-Generated Proofs

The rate-limit budget model in [§4](#4-rate-limit-budget-model) assumes per-hop generated proofs,
where forwarding consumes from the node's own `R` budget and the slot pool self-balances.
With sender-generated proofs, the initiating node generates `L` proofs per originated packet from its own `R`,
while forwarding nodes only verify and do not consume their own budget.
A future revision MAY define an adapted budget model for this architecture,
including revised slot pool semantics, an explicit emission rate target that accounts for observed forwarding load,
and updated pre-computation sizing.

### 11.5 Poisson-Rate Cover Traffic

Poisson-Rate is a candidate alternative strategy retained here for future consideration.

The node emits cover packets according to a Poisson process with rate `λ_cover` packets per second,
producing random memoryless inter-emission gaps.
`λ_cover` would be set to `f × R / ((1 + L) × P)` packets per second,
where `f` is the configured `cover_rate_fraction` ([§5.5](#55-data-structures)).
Emissions are suppressed when no slots are available.

**Potential strengths:**

- **Timing unobservability:** both cover and forwarded emissions are exp-distributed,
  making it statistically hard for an observer to classify individual packets by timing
  (addressing the separability concern in [§10.4](#104-timing-separability-of-cover-and-non-cover-packets)).
- **Short-window volume unobservability:** per-epoch cover count is `Poisson(N)` rather than deterministic,
  so forwarding-count estimates from total emissions carry at least `±√N` uncertainty per epoch.

**Costs:**

- **Per-epoch variance:** cover emissions per epoch are `Poisson(N)` — some epochs are thin and weaken in-epoch mixing.
- **Front-loading:** random clustering can consume cover budget early, starving late-arriving non-cover traffic.
- **Pre-computation margin:** pipelines need a safety margin (e.g., `N + 3√N`) to avoid running dry.
- **Budget coupling:** cover rate drops with non-cover load as the pool nears exhaustion.

**Interaction with `R`:**

Poisson-Rate's per-epoch variance shrinks relative to its mean as `R` grows (`√N / N` → 0).
At small `R`, front-loading and thin-cover epochs are pronounced.
At large `R`, these effects become negligible.

Simulation of real traffic distributions is required before adopting Poisson-Rate as a normative option.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p Mix Protocol](./mix.md)
- [Mix DoS Protection](./mix-dos-protection.md)
- [Mix RLN DoS Protection](./mix-spam-protection-rln.md)
- [Loopix: Providing Anonymity in a Message Passing System](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska)
- [Nym: Mixnet for Network-Level Privacy](https://nymtech.net/nym-whitepaper.pdf)
- [Blend Protocol](../../blockchain/raw/nomos-blend-protocol.md)
