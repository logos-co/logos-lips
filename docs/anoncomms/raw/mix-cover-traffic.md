# Mix Cover Traffic

| Field | Value |
| --- | --- |
| Name | Mix Cover Traffic |
| Slug | 161 |
| Status | raw |
| Category | Standards Track |
| Editor | Prem Prathi <prem@status.im> |
| Contributors |  |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`1ac7689`](https://github.com/logos-co/logos-lips/blob/1ac7689ee3fe1665d5d5d1bf9c180ed951cc660d/docs/anoncomms/raw/mix-cover-traffic.md) — chore: split ift ts specs (#334)
- **2026-05-11** — [`2aa2bcd`](https://github.com/logos-co/logos-lips/blob/2aa2bcd89c58ccc4453207edeb8269e66a631b48/docs/ift-ts/raw/mix-cover-traffic.md) — feat: Mix Cover Traffic specification (#311)

<!-- timeline:end -->

## Abstract

This document specifies the cover traffic architecture for the [libp2p Mix Protocol](mix.md).
It defines the Poisson-rate emission strategy,
the loop cover packets the strategy emits,
and how the rate-limit budget is divided between origination and forwarding.
Under this strategy, every packet a node originates leaves on a tick of a random clock
whose behaviour does not depend on the node's traffic,
so an observer of the node's outgoing link cannot tell whether it is sending its own messages,
how many,
or when.
An observer who also counts the node's incoming link can still infer how much it sends;
the mechanism that would close that channel is recorded as future work ([§11.5](#115-drop-cover)).

## 1. Introduction

The Mix Protocol provides sender anonymity through layered encryption and per-hop delays.
However, without cover traffic,
an adversary observing a mix node's emissions can mount several attacks:

- **Traffic analysis**: by correlating emission bursts with known events,
  an adversary can link a node's activity periods to specific senders or recipients.
- **Intersection attack**: by observing which nodes are active each time a message reaches its destination,
  an adversary can progressively narrow down the set of possible senders across multiple messages.
- **Timing correlation**: by matching idle and active periods across mix nodes,
  an adversary can correlate ingress and egress packets.
- **Counting**: by counting packets into and out of a node over a window,
  an adversary can recover how much the node sends,
  because forwarded packets and any cover that returns to the originator both cancel from the difference.

The first three attacks rely on the same weakness:
a node's emission pattern leaks whether it is carrying non-cover traffic,
either in how many packets it emits or in when it emits them.

Cover traffic addresses this by making a node's emission pattern independent of its non-cover traffic
in both volume and timing.
A node emits one packet on every tick of a clock with exponentially distributed gaps.
When the node has a message of its own to send, the message takes the next tick;
when it has none, a loop packet takes the tick instead.
The clock does not know which is which,
so neither does an observer of the outgoing link.

The counting attack is not closed by this revision.
Closing it requires cover that does not return to the originator,
which is recorded as future work ([§11.5](#115-drop-cover)).
[§10.5](#105-inbound-observability) states what remains visible,
to whom,
and what closing it would take.

The Mix Protocol defines cover traffic as a pluggable component (see [Mix Protocol §6.4](mix.md#64-cover-traffic)).
This specification provides a concrete instantiation of that component.
The architecture is designed to be compatible with the DoS protection mechanism defined in [Mix DoS Protection](mix-dos-protection.md)
and specifically with the [Mix RLN DoS Protection](mix-dos-protection-rln.md) mechanism.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Other terms used in this document are as defined in the [libp2p Mix Protocol](mix.md) and [Mix DoS Protection](mix-dos-protection.md).

The following additional terms are used throughout this specification:

- **Origination**
  Any packet a node emits:
  a locally originated message, a SURB reply the node produces as an exit, or a cover packet.
  Forwarded packets are not originations.

- **Epoch**
  A fixed time window of duration `P` seconds during which each mix node is permitted to emit at most `R_node` packets,
  as enforced by the DoS protection mechanism.
  Under [Mix RLN DoS Protection](mix-dos-protection-rln.md), `P` is that specification's `period`.

- **`R_node`**
  The node's own per-epoch rate-limit budget on outgoing packets, exposed by the DoS protection mechanism for this specific node.
  Under [Mix RLN DoS Protection](mix-dos-protection-rln.md), `R_node` is the flat rate limit configured for the deployment,
  the `user_message_limit` every node registers with, and is uniform across all nodes.
  Under [Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md), `R_node` equals the node's
  `user_message_limit ∈ [R_min, R_max]` derived from its registered stake, and may differ across nodes.

- **`R_base`**
  The deployment-wide anchor rate per epoch, published in the DoS protection mechanism's deployment configuration
  and identical across all nodes.
  Under [Mix RLN DoS Protection](mix-dos-protection-rln.md), `R_base` equals that same flat rate limit, so `R_base = R_node`.
  Under [Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md), `R_base` is the parameter defined in its
  [System Parameters](mix-dos-protection-rln-stake-weighted.md#44-system-parameters).
  Every node satisfies `R_node ≥ R_base` by construction.

- **Origination Clock**
  A per-node timer whose gaps between ticks are sampled independently from an exponential distribution
  with the deployment-wide mean `μ_tick` seconds.
  The clock runs continuously from node start and is not reset or aligned at epoch boundaries;
  the number of ticks that fall within one epoch is a Poisson random variable with mean `P / μ_tick`.
  Every origination leaves the node on a tick of this clock and never between ticks.

- **Tick**
  One firing of the origination clock.

- **Loop Packet**
  A cover packet whose path returns to the originating node.
  A loop packet is emitted on every tick that no locally originated message or SURB reply is waiting to use.

- **Slot**
  A single rate-limit token within an epoch's budget of `R_node` tokens, as defined by the DoS protection mechanism.
  Each outgoing packet — whether cover or non-cover — consumes exactly one slot
  and carries a proof bound to that slot's message index.

- **Slot Pool**
  The node's per-epoch record of its slots ([§5.5](#55-data-structures)).

- **Origination Share** and **Forwarding Share**
  The two parts into which an epoch's `R_node` slots are divided ([§4](#4-rate-limit-budget-model)).
  The origination share is the same for every node;
  the forwarding share is whatever remains of `R_node`.
  Ticks claim from the origination share;
  forwarded packets claim from the forwarding share.

## 3. Design Principles

The cover traffic architecture is guided by the following principles:

- **Sender unobservability on the outgoing link**: A node's emission pattern does not depend on its non-cover traffic,
  in either volume or timing.
  What the node receives is not made independent of its traffic by this specification ([§10.5](#105-inbound-observability)).
- **Substitution, not addition**: The clock emits exactly one packet per tick whether or not the node has anything to send.
  A tick carries a locally originated message or SURB reply if one is waiting,
  and a loop packet otherwise.
  Real traffic therefore replaces cover on a tick and never adds an emission the clock would not have produced,
  so the number and timing of a node's originations are fixed by the clock alone.
- **Indistinguishability**: Cover packets are structurally identical to non-cover Sphinx packets in size and routing behavior,
  preventing packet-level classification ([Mix Protocol §6.4](mix.md#64-cover-traffic)).
  Cover packets are built by the same path selector, under the same path constraints,
  as the locally originated messages they stand in for ([§5.1](#51-cover-packet-construction)).
  Every origination, cover or real, receives its rate-limit proof at the tick that emits it,
  so no origination is delayed by cryptographic work that another is not.
- **Uniformity**: The tick mean `μ_tick` is a deployment-wide constant.
  A node whose clock differs from its peers is identifiable by its rate alone ([§10.7](#107-uniformity-of-the-origination-clock)).
- **DoS protection compliance**: All cover traffic operates within the rate-limit budget `R_node` enforced per epoch.
  Proofs are epoch-bound and unused slots are discarded at epoch boundaries ([Mix DoS Protection](mix-dos-protection.md)).
- **Slot integrity**: Each rate-limit slot is spent on the wire at most once per epoch.
  A slot claim returns the message index the packet's proof is bound to,
  and the origination and forwarding shares draw from disjoint index ranges ([§5.2](#52-slot-claims)).
- **Mix node only**: Cover traffic is generated only by mix nodes that forward traffic for other nodes
  and participate continuously in the network.
  Initiating-only nodes are mostly short-lived with dynamic identifiers and do not forward traffic,
  making cover traffic neither practical nor beneficial for them ([§8](#8-initiating-only-node-considerations)).
- **Pre-computation**: As an optimization, loop packet bodies can be built ahead of the ticks that emit them,
  so that a tick does no Sphinx construction at emission time.

## Overview

A mix node plays multiple roles at once: it sends its own messages, relays messages for other nodes, and ideally hides which of these it is doing.
Without protection, an observer watching the node's outgoing packets can tell when it is active, how busy it is, and when it is idle —
enough to link users to their messages through traffic patterns.

This specification makes every origination leave on a tick of the origination clock.
The clock fires at random moments with exponentially distributed gaps.
On each tick the node sends exactly one packet:
a locally originated message or SURB reply if one is waiting,
and a loop packet otherwise.
An observer of the outgoing link sees the same stream of originations —
the same rate, the same random shape —
whether the node is idle or sending at capacity.

Forwarded packets do not use the clock.
They leave after the mixing delay the sender encoded for this hop,
which is exponentially distributed.
Originations leave on a clock that is independent of everything the node is doing,
so the node's output has the same distribution whatever its real traffic ([§7](#7-poisson-rate-emission-strategy)).

The node operates under a rate limit that bounds total packets emitted per epoch ([§4](#4-rate-limit-budget-model)).
Every packet — cover, locally originated, SURB reply, or forwarded — consumes one slot.
The budget is divided into an origination share, claimed by ticks,
and a forwarding share, claimed by forwarded packets;
neither can starve the other.

Loop packets return to the originator
and fill the ticks that nothing real is waiting to use.
For efficiency, loop packet bodies MAY be pre-built ahead of the clock ([§6.1](#61-at-epoch-boundary));
the rate-limit proof of every origination is generated at its tick.

Each epoch begins by discarding previous state and initializing a fresh slot budget.
Throughout the epoch the clock ticks;
each tick claims one slot and emits one packet,
or is silent if the origination share is spent.
Forwarded packets claim from the forwarding share as they arrive.
At epoch end, unused slots are discarded and the cycle repeats.

## 4. Rate Limit Budget Model

Each mix node receives a budget of `R_node` slots per epoch from the DoS protection mechanism.
Cover emission, locally originated message sending, SURB reply origination, and packet forwarding all draw from this budget.
Since each originated packet traverses `L` forwarding hops — where `L` is the mix path length
as defined in [Mix Protocol §6](mix.md#6-pluggable-components) —
forwarding consumes a significant portion of the budget.

If every node originates at rate `C` packets per epoch (cover, locally originated, and replies combined),
each node forwards approximately `C * L` packets per epoch.
Since origination and forwarding share the same budget:

```text
C + C * L ≤ R_node
C ≤ R_node / (1 + L)
```

`R_node / (1 + L)` is therefore the **upper bound on total origination** for that node.
For `L = 3`, approximately 25% of a node's slots are available for origination.

**Origination share.**
A node originates exactly one packet per tick,
so its per-epoch origination count is a Poisson random variable with mean `P / μ_tick`.
The origination share is `ceil(R_base / (1 + L))` slots and is the same for every node in the deployment,
since the tick mean is a deployment-wide constant ([§10.7](#107-uniformity-of-the-origination-clock))
and the share has to fit within the budget of the lowest-rate node.
The tick mean MUST be chosen so that the per-epoch tick count exceeds the share only rarely:

```text
Pr[ Poisson(P / μ_tick) > ceil(R_base / (1 + L)) ] ≤ 0.01
```

With `R_base = 100`, `L = 3`, and `P = 10 s`, the origination share is 25 slots
and `P / μ_tick = 15` — a tick mean of about `0.67 s` — satisfies the bound with a probability of about 0.6%.
A deployment whose `R_base / (1 + L)` is too small to admit a useful tick rate under this bound
MUST raise `R_base` rather than lower the bound.
When the count does exceed the share, the remaining ticks of that epoch are silent ([§6.2](#62-cover-emission)).
Because non-cover originations replace ticks rather than adding to them,
whether a tick is silent depends only on the node's own clock and never on its non-cover traffic.

**Forwarding share.**
The forwarding share is whatever remains of the node's budget after the origination share:
`R_node − ceil(R_base / (1 + L))` slots per epoch,
75 at the parameters above.
The two shares together never exceed `R_node`.
Under a flat rate limit it is the same for every node;
under stake-weighted rates a node with a larger `R_node` has a larger forwarding share and the same origination share,
so additional stake buys forwarding capacity and never a higher origination rate.
Forwarded packets claim from this share as they arrive
and are dropped once it is exhausted ([§6.4](#64-packet-forwarding)).
The cap is what keeps a forwarding flood from silencing the node's own origination ([§10.4](#104-forwarding-cap-and-forwarded-packet-drops)).
Origination-share slots left unused when the epoch ends are discarded;
they are never released to forwarding,
so that the split is a fixed property of the deployment rather than of the node's load.
At the parameters above, on average 10 of the 25 origination slots go unused each epoch;
that is the price of a share the node cannot know it will not need until the epoch is over.

**Cost of cover.**
Every origination, cover or real, costs the network the same:
one origination slot at the sender,
`L − 1` forwarding slots at relays,
and one terminal arrival that is received but not forwarded.
A loop costs exactly as much as a real message.
Cover is all of a node's originations when it is idle
and none of them when it originates at the tick rate.
This overhead is the price of making origination unobservable by substitution.
`μ_tick` sets the total rate of originations the node must sustain,
and the node's own real rate sets how much of that is cover.

The number of forwarded packets a node can carry therefore depends on:

- **Its rate limit `R_node`**: everything above the origination share is forwarding capacity.
- **Path length `L`**: longer paths consume more forwarding slots per originated packet.
- **Network size and forwarding variance**: with random path selection, forwarding load is not uniform.
  Some nodes receive more forwarding traffic than the equilibrium average.
  Under the cap, the excess is dropped rather than taken from origination.

**Note on DoS protection architecture:**
The budget model assumes per-hop generated proofs
([Mix DoS Protection §4.2](mix-dos-protection.md#42-per-hop-generated-proofs)),
where forwarding consumes slots from the node's own budget.
With sender-generated proofs ([Mix DoS Protection §4.1](mix-dos-protection.md#41-sender-generated-proofs)),
forwarding nodes only verify proofs and do not consume their own budget;
the budget model for that architecture is deferred to [§11.3](#113-budget-model-for-sender-generated-proofs).
Neither architecture enforces the origination clock cryptographically;
see [§10.6](#106-the-origination-cap-is-a-convention).

## 5. Integration with the Mix Protocol

The cover traffic mechanism integrates with the Mix Protocol at four points in packet processing.

Cover packets are identified by the reserved protocol codec `"/mix/cover/1.0.0"`.
This codec is used as the origin protocol codec during Sphinx packet construction
and is checked during exit processing to distinguish cover packets from application traffic.

All mix nodes in a deployment MUST use the same tick mean and the same reserved loop share
([§10.7](#107-uniformity-of-the-origination-clock)).
The configured path length `L` for cover packets
MUST match the path length used for locally originated messages
as defined in [Mix Protocol §6](mix.md#6-pluggable-components).

Where this specification refers to the path selector,
it means the path selection component configured for the Mix Protocol instance
([Mix Protocol §6](mix.md#6-pluggable-components)),
whose strategies are being specified in [Mix Path Selection](https://github.com/logos-co/logos-lips/pull/445).

### 5.1 Cover Packet Construction

**Trigger:** A tick of the origination clock fires and no locally originated message or SURB reply is waiting ([§6.2](#62-cover-emission)).

**[During Sphinx packet construction](mix.md#85-packet-construction):**
The mechanism constructs a loop Sphinx packet
following the same construction procedure as a locally originated message.
The differences are:

- The mix path returns to the originating node.
  The path MUST be requested from the path selector under the same constraints as locally originated messages,
  so that any hop positions the selector fixes for locally originated messages are fixed for loops as well.
  The request identifies the path as cover;
  the identifier for that purpose is defined by the path selection specification and is not fixed here.
  No constraint specific to the return leg is imposed here:
  fixing the closing position would change what an adversary learns from the loops it closes,
  a trade discussed in [§10.5](#105-inbound-observability) and belonging to path selection.
- The origin protocol codec MUST be set to the cover traffic codec defined in [§5](#5-integration-with-the-mix-protocol).
- The application message content MUST be filled with cryptographically random bytes.
- If pre-computation is enabled, a pre-built packet body is used without re-construction.

**Wire format:**
Cover packets use the exact Sphinx packet format defined in [Mix Protocol §8](mix.md#8-sphinx-packet-format).
No additional fields or framing are introduced.
A cover packet on the wire is indistinguishable from a non-cover traffic packet,
ensuring that intermediary nodes and external observers cannot classify packets as cover or non-cover.

The cover packet is transmitted to its first hop on the tick that selected it,
after its proof is generated ([§6.2](#62-cover-emission)).
No further delay is applied:
the wait for the tick is the pre-send delay ([§6.3](#63-locally-originated-message-sending)).

### 5.2 Slot Claims

**Procedure:** `ClaimSlot(kind) -> (success, message_index)`, where `kind ∈ { TICK, FORWARD }`

**Trigger:** The origination clock fires (`TICK`),
or the Mix Protocol needs to forward a packet (`FORWARD`).

The pool tracks the origination share and the forwarding share separately ([§4](#4-rate-limit-budget-model)),
and each share owns a contiguous range of the epoch's message indices:
the origination share owns indices `1 .. S`, where `S = ceil(R_base / (1 + L))`,
and the forwarding share owns indices `S + 1 .. R_node`.

1. A `TICK` claim takes the next unused index from the origination range and returns it.
   If the range is exhausted, the claim fails and the tick is silent ([§6.2](#62-cover-emission)).
2. A `FORWARD` claim takes the next unused index from the forwarding range and returns it.
   If the range is exhausted, the claim fails and the packet is dropped ([§6.4](#64-packet-forwarding)).

A `FORWARD` claim MUST NOT return an origination-range index,
and a `TICK` claim MUST NOT return a forwarding-range index.
An index MUST NOT be returned twice in an epoch.
The proof of every packet is generated with the index its claim returned,
so no two proofs in an epoch share an index ([§10.1](#101-message-index-integrity)).

Locally originated messages and SURB replies do not claim slots directly.
They are placed in the origination queue and take the next tick ([§6.3](#63-locally-originated-message-sending))
instead of the loop packet that tick would otherwise have carried.

On a successful claim, the caller generates the DoS protection proof
via `GenerateProof(binding_data)` ([Mix DoS Protection §8.2.1](mix-dos-protection.md#821-proof-generation)),
where `binding_data` is the packet-specific data as defined by the DoS protection mechanism
and the message index is the one returned by the claim.

### 5.3 Epoch Boundary

**Procedure:** `ResetEpoch(epoch) -> void`

**Trigger:** The DoS protection mechanism signals the start of a new epoch
via `OnEpochChange` ([Mix DoS Protection §8.2.3](mix-dos-protection.md#823-epoch-change-notification)).
The Mix Protocol MUST call `ResetEpoch` before processing any packets in the new epoch.

The mechanism refreshes the slot pool for the new epoch:
all remaining slots from the previous epoch are discarded,
and a new pool of `R_node` slots is initialized with its origination and forwarding index ranges.

The origination clock runs across epoch boundaries without reset.
A tick claims its slot in the epoch in which it fires,
so no origination is ever held across a boundary.
Packets emitted near epoch end may arrive at later hops in a subsequent epoch.
The DoS protection mechanism is responsible for accepting proofs within a configurable epoch window
(_e.g.,_ the `max_epoch_gap` parameter in [Mix RLN DoS Protection](mix-dos-protection-rln.md)).

### 5.4 Cover Packet Reception

**Trigger:** The Mix Protocol completes [exit processing](mix.md#864-exit-processing) on a received Sphinx packet
and extracts the origin protocol codec from the decrypted payload.

If the codec matches the cover traffic codec (see [§5](#5-integration-with-the-mix-protocol)),
the Mix Protocol MUST handle the packet internally without handing off to the Mix Exit Layer.
The packet MUST be silently discarded.

This is handled by the cover traffic codec check
in [Mix Protocol §8.6.4](mix.md#864-exit-processing) step 4,
which intercepts cover packets before handing off to the Mix Exit Layer.

The exit node of a loop packet is the originating node itself,
so the cover codec is never visible to any other party.
Implementations SHOULD use the reception event for path health monitoring ([§11.2](#112-path-health-monitoring)).

### 5.5 Data Structures

```text
PrebuiltLoopBody {
  packet:         bytes     // Pre-built Sphinx packet without its DoS protection proof
  path:           []bytes   // Ordered list of mix node identifiers on the loop path
  created_at:     uint64    // Unix timestamp (seconds) when this body was constructed; bounds body age (see §9.1)
}
```

```text
SlotPool {
  epoch:                  uint64   // The epoch this pool belongs to
  origination_next:       uint32   // Next unused index in the origination range 1 .. S
  forwarding_next:        uint32   // Next unused index in the forwarding range S + 1 .. R_node
  loop_bodies:            []PrebuiltLoopBody
}
```

```text
CoverTrafficConfig {
  tick_mean:      float64   // μ_tick, mean gap between ticks in seconds; deployment-wide (see §7)
  queue_limit:    uint32    // Max originations waiting for a tick; RECOMMENDED ceil(P / μ_tick) (see §6.3)
}
```

## 6. Node Responsibilities

This section defines what each mix node MUST do at each integration point.

The slot pool ([`SlotPool`](#55-data-structures)) is a token bucket of `R_node` slots per epoch,
divided into an origination share and a forwarding share.
Each outgoing packet — cover or non-cover — atomically claims one slot.
Slot claim operations MUST be atomic.

### 6.1 At Epoch Boundary

When the DoS protection mechanism signals the start of a new epoch,
the Mix Protocol instance MUST invoke `ResetEpoch` ([§5.3](#53-epoch-boundary)) on the cover traffic mechanism
to discard previous epoch state and initialize a new slot pool.

**If pre-computation is enabled (RECOMMENDED):**
The cover traffic mechanism keeps a supply of loop packet bodies built ahead of the clock
(see [§9.1](#91-pre-computation-scheduling) for sizing).
A body is a complete Sphinx packet built per [§5.1](#51-cover-packet-construction) without its proof;
the proof is generated at the tick that emits it, like every other origination.
Bodies are not bound to an epoch and carry over epoch boundaries.
A pre-built body whose path includes a node that has left the pool is discarded and rebuilt.

**Fallback caveat:**
Building a loop body on demand when the supply is empty adds construction time
after the tick that selected it.
Implementations SHOULD size the supply ([§9.1](#91-pre-computation-scheduling))
to avoid the fallback path in steady state.

### 6.2 Cover Emission

Emission timing is governed by the origination clock.
The clock is the only mechanism that decides when an origination leaves the node;
there is no separate cover schedule and no separate pre-send hold.

Slots are deducted at claim time, not at wire transmission:
forwarded packets within their mixing delay (see [§6.4](#64-packet-forwarding))
have already been deducted from the forwarding share,
so their slots are unavailable to any later forward claim.

**Algorithm: Origination Clock**

> The following steps repeat continuously, across epoch boundaries:
>
> 1. Sample a gap `g` from an exponential distribution with mean `μ_tick`
>    and wait `g` seconds.
>    The gap is sampled independently of every previous gap
>    and of whether any origination is waiting.
> 2. Call `ClaimSlot(TICK)` ([§5.2](#52-slot-claims)).
>    If the claim fails, the tick is silent: emit nothing and return to step 1.
> 3. Select the packet body:
>    - a. A locally originated message or SURB reply is waiting:
>      take the packet at the head of the origination queue.
>    - b. Nothing is waiting: take a pre-built loop body,
>      or build one on demand if the supply is empty ([§5.1](#51-cover-packet-construction)).
> 4. Generate the packet's DoS protection proof with the index the claim returned
>    ([§5.2](#52-slot-claims)),
>    and attach it.
> 5. Transmit the packet to its first hop.

**Proof at the tick:**
Every origination, cover or real, receives its proof in step 4,
so every origination leaves the node the same proving time after its tick.
A proof generated earlier would be bound to an epoch or a membership state that may have changed by the tick,
and regenerating it only for the packets that crossed a boundary
would delay real messages more often than cover.
Implementations SHOULD keep proving time small relative to `μ_tick`.

**A tick that fires while the previous one is still being proved:**
Gaps shorter than the proving time are not rare:
with exponential gaps of mean `μ_tick`,
a fraction `1 − exp(−t / μ_tick)` of them fall below a proving time `t`,
which is about 7% for `t = 50 ms` at the parameters of [§7](#7-poisson-rate-emission-strategy).
Implementations MUST serve such ticks in order
and MUST NOT drop, coalesce, or reorder them,
so that the number of originations still matches the number of ticks.
The emission times are then the tick times delayed by the prover's backlog.
That backlog is a function of the clock alone and never of what the ticks carry,
so the emission stream stays independent of the node's real traffic,
though its gaps are no longer exactly exponential ([§7](#7-poisson-rate-emission-strategy)).

**Indices are spent, not recycled:**
A tick claims its index at step 2,
before the packet body is selected and before the proof is generated.
If the body cannot be built or the proof cannot be generated,
the tick emits nothing and the claimed index is spent for that epoch.
An index MUST NOT be returned to the pool and reused:
a failure after the packet reached the wire is not reliably distinguishable from one before it,
and a second proof under a spent index is what [§10.1](#101-message-index-integrity) forbids.

**Silent ticks:**
In normal operation a tick is silent only when the origination share of the current epoch is exhausted.
Because every tick claims exactly one slot regardless of what it carries,
exhaustion depends on the node's own tick count in the epoch and on nothing else;
in particular it does not depend on how many real originations the node had.
With `μ_tick` chosen per [§4](#4-rate-limit-budget-model), silent ticks occur in fewer than 1% of epochs.

A failure to build a body or to generate a proof is the other way a tick can emit nothing,
and the two do not behave alike.
Proving happens on every tick, so a proving failure is independent of the node's load.
A body is needed only on a tick that carries a loop,
which is every tick while the node is idle and none while it originates at the tick rate,
so a body failure is reached more often the less the node sends.
Implementations MUST keep such failures rare enough that the silence they cause does not track load;
this is what the supply sizing of [§9.1](#91-pre-computation-scheduling) is for.

### 6.3 Locally Originated Message Sending

**[During Sphinx packet construction](mix.md#85-packet-construction):**
When the Mix Entry Layer submits a locally originated message for mixification,
the Mix Protocol instance MUST construct its Sphinx packet immediately
and place it in the origination queue.
The packet receives its proof and is transmitted on the next tick ([§6.2](#62-cover-emission), steps 3.a and 4).

**Pre-send delay:**
The wait from enqueueing to the next tick is exponentially distributed with mean `μ_tick`,
because the clock is memoryless.
This wait is the pre-send delay of [mix.md §8.5.2](mix.md#852-construction-steps) Step 3.f;
no additional delay is sampled,
and the Step 3.f distribution is this one.
This supersedes the delay sampled at that step for nodes running this specification,
as it does for SURB replies at [mix.md §8.7.3](mix.md#873-using-a-surb) Step 4;
both steps require a companion revision of the Mix Protocol specification.
End-to-end delay estimates ([mix.md §9.4.2](mix.md#942-no-built-in-retry-or-acknowledgment)) therefore include this mean
for the origination and reply pre-send terms.

**Queueing and backpressure:**
If real originations arrive faster than ticks fire,
the origination queue grows and latency increases;
no origination is ever sent off-tick.
The queue holds at most `queue_limit` packets.
When it is full, the Mix Protocol instance MUST reject further submissions from the Mix Entry Layer
and MUST NOT emit anything in response;
rejection is internal to the node and leaves no trace on the wire.
Surfacing that rejection to the submitting application requires an error path on the Mix Entry Layer interface,
which is a companion revision of the Mix Protocol specification.
The RECOMMENDED `queue_limit` is `ceil(P / μ_tick)`,
the expected number of ticks in one epoch,
which is 15 at the parameters of [§7](#7-poisson-rate-emission-strategy).
That bounds the queueing delay a submission can accumulate to about one epoch;
a larger limit trades latency for tolerance of bursts.
Applications SHOULD keep their sustained real rate below `1 / μ_tick` packets per second.

### 6.4 Packet Forwarding

**[During Sphinx packet handling](mix.md#86-sphinx-packet-handling):**
When the Mix Protocol instance acts as an intermediary and receives a Sphinx packet to forward,
it MUST first call `ClaimSlot(FORWARD)` ([§5.2](#52-slot-claims)) before applying the mixing delay.
This ensures no two forwarded packets consume the same slot regardless of how their mixing delays overlap.
If no slot can be claimed, the packet is dropped.
Otherwise, the Mix Protocol instance proceeds with
[intermediary processing](mix.md#863-intermediary-processing),
generating the forwarding proof with the index the claim returned.

**Slot consumption:**
The slot is consumed on successful `ClaimSlot(FORWARD)`, not on transmission.

**Send timing:**
The packet is dispatched when its mixing delay elapses,
independently of the origination clock.
Forwarded packets never use ticks.

### 6.5 SURB Reply Origination at the Exit

A SURB reply produced by an exit node is an origination of that node
([mix.md §8.7.3](mix.md#873-using-a-surb)).
The exit MUST build the reply when it is produced
and place it in its origination queue,
transmitting it on its next tick exactly as a locally originated message ([§6.3](#63-locally-originated-message-sending)).
The reply follows the return path the initiator built into the SURB.
The reply's pre-send delay is therefore the tick wait,
with the same mean as at the initiator.
Replies SHOULD be placed ahead of the exit's own locally originated messages in the queue,
so that a reply waits for one tick and not for the queue to drain;
this ordering is internal to the exit and is not observable.

**Reply timeouts:**
A round trip includes two tick waits — one at the initiator and one at the exit — in addition to the mixing delays.
Each wait exceeds `x` seconds with probability `exp(−x / μ_tick)`;
at the parameters of [§7](#7-poisson-rate-emission-strategy) a single wait exceeds 5 s about 0.06% of the time.
An initiator that times out before the reply has had that long to leave the exit will retransmit a request whose reply is still queued.
Duplicate requests spend ticks and SURBs on both sides
and are visible as duplicates to the exit and the destination.
Reply timeouts ([mix.md §9.4.2](mix.md#942-no-built-in-retry-or-acknowledgment)) therefore need to be sized to the tail of both tick waits,
not to their means,
and origin protocols SHOULD deduplicate requests, since the Mix Protocol is stateless and cannot.

A request carries at most two SURBs ([mix.md §8.5.1](mix.md#851-inputs)),
so serving one request costs the exit at most two ticks.
An exit serving many requests spends its ticks on replies
and originates fewer of its own messages;
its emission count and timing do not change.

## 7. Poisson-Rate Emission Strategy

The node runs the origination clock of [§6.2](#62-cover-emission):
inter-tick gaps are exponential with the deployment-wide mean `μ_tick`,
every tick emits exactly one packet,
and a locally originated message or SURB reply substitutes for the loop packet a tick would otherwise carry.

**Parameters:**

- `μ_tick`, the tick mean, chosen per [§4](#4-rate-limit-budget-model) against the lowest rate limit in the deployment,
  so that the per-epoch tick count exceeds the origination share with probability at most 1%.
  With `R_base = 100`, `L = 3`, `P = 10 s`: `μ_tick ≈ 0.67 s`, about 15 ticks per epoch.
- The node's maximum sustained rate of real originations is the tick rate `1 / μ_tick`, `1.5 /s` at the parameters above.
  A deployment that needs more real capacity raises `R_base`.

**Why the emission is unobservable:**
The origination clock samples every gap independently of the node's traffic,
and every tick emits exactly one packet whether or not anything real is waiting.
The stream of originations therefore has the same distribution whatever the node is doing:
its rate is `1 / μ_tick` and its gaps are exponential when the node is idle, when it is at capacity, and in between.
This holds even against an observer who can tell originations from forwarded packets perfectly;
the origination stream carries no information about real traffic because none went into it.
It holds for any tick mean and does not require `μ_tick` to equal the mixing delay mean,
and it does not depend on the shape of the forwarded stream ([§10.8](#108-interaction-with-fixed-hop-path-selection)).

Where proving time is not negligible against `μ_tick`,
the gaps are the tick gaps delayed by the prover's backlog rather than exactly exponential ([§6.2](#62-cover-emission)).
That backlog is a function of the clock alone,
so the distribution is still the same whatever the node is doing,
which is the property this section rests on.

**Characteristics:**
Per epoch, the node emits `Poisson(P / μ_tick)` originations,
of which the loops are those that no real origination was waiting to take.
Silent ticks occur only when the epoch's origination share is exhausted,
in fewer than 1% of epochs at the parameters above,
and their occurrence is independent of the node's real traffic.
A real origination waits for the next tick:
an exponential wait with mean `μ_tick`, about `0.67 s` at the parameters above,
with the same tail shape as a mixing delay.
Sustained real demand above `1 / μ_tick` queues rather than leaks ([§6.3](#63-locally-originated-message-sending)).

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

If an initiating-only node is promoted to a mix node and becomes long-lived,
it SHOULD start the origination clock immediately upon promotion
and build loop bodies on demand until its pre-built supply is established.

## 9. Implementation Recommendations

This section provides non-normative guidance for implementers.

### 9.1 Pre-computation Scheduling

Loop bodies are not bound to an epoch,
so the supply can be replenished continuously in the background
rather than in a burst before each epoch.
Implementations SHOULD interleave body construction with normal packet processing
(_e.g.,_ yielding to non-cover traffic between constructions) to avoid contention with ongoing packet handling.

**Sizing:**
Any tick may need a loop body,
so the demand per epoch is at most `P / μ_tick` bodies, a Poisson count;
implementations SHOULD keep the supply at that mean plus `3 × sqrt(mean)`
so that on-demand construction is rare.

**Body age:**
Because bodies are not bound to an epoch, a body can outlive the accuracy of the path it was built for.
Beyond discarding bodies whose paths have lost a node ([§6.1](#61-at-epoch-boundary)),
implementations SHOULD bound body age,
discarding any body older than a configured maximum,
so that a supply built during a quiet period is not still in use after the topology has moved on.
`created_at` ([§5.5](#55-data-structures)) records the construction time this bound applies to.

### 9.2 Pool Status Tracking

Implementations SHOULD maintain runtime counters for available slots, cover emissions, and non-cover consumptions.
These aid in diagnostics, monitoring, and tuning.

The non-cover consumption counter is subject to the exposure restriction of [§10.9](#109-exposure-of-real-traffic-counters).

### 9.3 Slot Exhaustion Logging

When a forwarded packet is dropped due to forwarding-share exhaustion, implementations SHOULD log a warning.
Persistent exhaustion may indicate that `R_node` is too low for the network's forwarding load,
or that the node is under a traffic flooding attack.

### 9.4 Synchronization

The atomicity of slot claims required by [§6](#6-node-responsibilities)
can be enforced using mutexes, lock-free atomic operations, or single-threaded event loops,
depending on the concurrency model.

## 10. Security Considerations

The design principles motivating slot integrity and DoS protection compliance
are described in [§3](#3-design-principles).
This section discusses the threat context behind those principles.

### 10.1 Message Index Integrity

Under [Mix RLN DoS Protection](mix-dos-protection-rln.md) and its stake-weighted extension,
a member MUST NOT use the same message index twice in an epoch:
two proofs under the same index with different signals let any verifier recover the member's secret,
and the member is slashed.
A node that originates and forwards in the same epoch generates proofs for both,
so the two shares MUST draw from disjoint index ranges,
and every proof MUST use the index its slot claim returned ([§5.2](#52-slot-claims)).
Without the partition, a tick and a forward could select the same index and the node would slash itself.

### 10.2 Origination Share Exhaustion

A tick that finds the origination share exhausted is silent ([§6.2](#62-cover-emission)).
Because a tick claims one slot whether it carries a loop or a real origination,
exhaustion is a function of the node's own tick count in the epoch only
and is independent of the node's real traffic.
The margin in [§4](#4-rate-limit-budget-model) keeps such epochs below 1%.

### 10.3 Why Emission Is Not Scheduled on a Fixed Interval

A strategy that emits cover at a fixed interval provides volume unobservability
(the emission count does not depend on real traffic)
but not timing unobservability.
Forwarded packets leave after random mixing delays;
cover on a fixed interval is the only periodic component of the node's output,
and a passive adversary recovers the interval by averaging over enough observations
and classifies packets near its grid points.
Blurring each emission with a sampled hold does not remove the constant mean spacing.
The origination clock has no interval and no hold:
its ticks are a Poisson process,
and there is no grid to recover.

### 10.4 Forwarding Cap and Forwarded Packet Drops

Forwarded packets are dropped once the forwarding share is exhausted ([§6.4](#64-packet-forwarding)).
Without the cap, an adversary who routes enough traffic through a node could consume its whole budget
and silence its origination clock,
muting the node's real and cover traffic together.
With the cap, such a flood costs the adversary dropped packets and leaves the node's origination untouched.

Drops are visible to the originators of the dropped packets as failed loop returns and missing replies.
Persistent forwarding-share exhaustion indicates that `R_node` is too low for the network's forwarding load
or that the node is under attack ([§9.3](#93-slot-exhaustion-logging)).

### 10.5 Inbound Observability

This specification fixes what a node **emits**.
It does not fix what a node **receives**,
and an observer who counts both of a node's links learns from the difference.

Consider an observer of one node's link who counts packets in and packets out over a window of several epochs.
Forwarded packets enter and leave, so they cancel.
Every loop the node sends returns to it, so loops cancel.
A real origination leaves and does not return;
a real arrival arrives and does not leave.
Over the window,

```text
in − out = received − sent
```

where `sent` counts the node's non-cover originations —
its locally originated messages and the SURB replies it produces as an exit ([§2](#2-terminology)) —
and `received` counts the messages and replies delivered to it.
The observer sees both `in` and `out`,
so it learns `received − sent`,
and for a node that mostly sends or mostly receives, that is its rate.
This holds against an observer of a single link,
needs no packet to be distinguishable from any other,
and converges within a few epochs.

Three terms blur the estimate without removing it.
Packets in flight at the window's edges are bounded by the path delay and do not accumulate.
Forwarded packets dropped when the forwarding share is exhausted ([§6.4](#64-packet-forwarding))
break the cancellation of forwarded traffic for as long as the exhaustion lasts.
Loops that fail to return — the condition the reception signal of [§5.4](#54-cover-packet-reception) exists to detect —
break the cancellation of loops.
All three widen the observer's error bars;
none of them is under the node's control,
and none of them is a defence.

The observer need not watch the node's link at all.
A node in the closing position of a loop forwards it to the originator,
but Sphinx does not tell that node whether the originator is the end of the path or a further hop,
so what it counts is a sample of the originator's loop returns
mixed inseparably with its own ordinary forwards to that node.
The returns in the sample number `ticks − sent` scaled by the share of loops this node closes,
and the tick rate is a deployment-wide constant ([§10.7](#107-uniformity-of-the-origination-clock)),
so an adversary holding a fraction of the network
occupies the closing position often enough to estimate `sent` from that sample.
The estimate is statistical, not a direct count,
and it sharpens with the fraction held.

Fixing the closing position to a small candidate set is not a defence against this
and is deliberately not required by [§5.1](#51-cover-packet-construction).
It would make the estimate exact and persistent for any adversary inside the set
rather than sampled across the network,
and a node whose terminal arrivals came from a small stable set of peers,
while every other node's came from many,
would be distinguishable by that alone on its own link and to topology analysis.
Whether that trade is worth making belongs to path selection.

Closing the channel requires that the packets standing in for real messages also fail to return,
which is the drop cover of [§11.5](#115-drop-cover),
deferred for the reasons given there.
Even with drop cover, SURB replies arrive in proportion to the requests a node sent,
at most two per request ([§6.5](#65-surb-reply-origination-at-the-exit)),
so a requester's rate would remain visible through its replies until inbound delivery is itself made constant ([§11.4](#114-inbound-cover)).

The property this specification delivers is therefore the following:
an observer of a node's outgoing link learns nothing about when or how much it sends;
an observer of both links learns `received − sent`;
and an adversary holding a fraction of nodes estimates `sent` from the loop returns it closes.

### 10.6 The Origination Cap Is a Convention

The origination clock bounds a node's origination rate by construction,
but nothing verifies another node's clock.
A node that originates faster than its tick mean allows — up to its whole budget `R_node` —
is not detectable by any single neighbor,
since the excess is spread across all first hops.
It is detectable by its forwarding behavior:
having spent its slots on origination, it drops the packets it should forward.
The clock therefore protects the anonymity of nodes that follow it
and does not by itself bound what a node that ignores it can impose on the network.
An origination proof verified at the exit,
drawn from a per-node origination quota separate from the forwarding budget,
would make the cap enforceable;
this belongs to the DoS protection specification ([§11.6](#116-enforced-origination-quota)).

### 10.7 Uniformity of the Origination Clock

The unobservability argument of [§7](#7-poisson-rate-emission-strategy) requires every mix node to run the same clock.
A node running a faster or slower clock is identifiable by its origination rate alone,
and its anonymity set shrinks to the nodes sharing its rate.
Accordingly:

- Every mix node that forwards traffic MUST run the origination clock.
  A node that forwards traffic without emitting cover has a visibly lower origination rate than its peers.
- `μ_tick` MUST be a deployment-wide constant,
  independent of a node's rate-limit budget `R_node`.
  It is derived from `R_base` ([§4](#4-rate-limit-budget-model)),
  so that every node, including one at the floor stake, can sustain it.
  Under a stake-weighted budget ([Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md)),
  a node with a larger `R_node` has a larger forwarding share and the same origination rate.
- A deployment that wishes to let higher-budget nodes originate faster MUST do so through deployment-wide rate classes,
  each defined by its own `μ_tick`.
  A node's rate class is observable, so the class is the anonymity set of its members;
  the fewer and larger the classes, the less the rate reveals.

The same applies to the mixing delay mean used by relays ([mix.md §6.2](mix.md#62-delay-strategy)):
it is a deployment-wide constant,
distinct from `μ_tick`,
and the two need not be equal.

### 10.8 Interaction with Fixed-Hop Path Selection

Under session- or time-based path selection ([Mix Path Selection](https://github.com/logos-co/logos-lips/pull/445)),
a node that is a fixed hop for a high-volume sender receives a concentrated stream from one predecessor.
The exponential mixing delay smooths that stream but does not make it memoryless,
so the node's forwarded output carries some structure from the fixed-hop stream.
This does not affect the node's own originations, which remain on the clock
and are unobservable on their own terms ([§7](#7-poisson-rate-emission-strategy));
it affects what an observer of that node can infer about the fixed-hop sender,
and is a consideration for the path selection specification rather than for this one.

### 10.9 Exposure of Real-Traffic Counters

The non-cover consumption counter ([§9.2](#92-pool-status-tracking)) reveals the exact per-epoch count of real traffic,
which is what traffic analysis aims to recover.
Implementations MUST keep this counter, and any per-epoch breakdown derived from it, in memory only,
and MUST NOT export it via metrics endpoints, structured logs, or any monitoring interface.

## 11. Future Work

### 11.1 Adaptive Tick Mean

`μ_tick` is currently a static deployment-wide configuration.
A future enhancement MAY define a method for a deployment to adapt `μ_tick` to network size and path length.
Any adaptive scheme MUST change `μ_tick` for all nodes together,
never per node ([§10.7](#107-uniformity-of-the-origination-clock)).

### 11.2 Path Health Monitoring

Loop packets follow a valid mix path and return to the originating node,
so their return confirms path liveness,
and failures to return indicate node failures or active attacks along the path.
A future revision of this specification MAY define an interface for exposing loop return status
to the path selector,
for example to decide when a fixed-hop candidate is unreachable.

A node originating at the tick rate sends no loops,
and so has no loop signal while it is leaning on its paths hardest;
it still learns of some failures from missing SURB replies.
A future revision MAY reserve a share `f_loop` of ticks for loops that real traffic never takes,
so that loops keep flowing at `f_loop / μ_tick` whatever the load,
at the cost of that share of real capacity.
The share would be sized by the detection the monitoring needs:
noticing that a fraction `p` of what a path carries is being dropped, with confidence `1 − α`,
takes `ln(α) / ln(1 − p)` loops through that path,
44 for `p = 0.1` and `α = 0.01`.
At `f_loop = 0.1` and the parameters of [§7](#7-poisson-rate-emission-strategy) a node accumulates 44 loops in about 5 minutes,
which is evidence about one particular hop only where the selector fixes it;
under uniform per-packet selection a given node lies on about `(L − 1) / N` of a node's loops,
so the same evidence about one node takes about 12 hours at `N = 300`.

### 11.3 Budget Model for Sender-Generated Proofs

The rate-limit budget model in [§4](#4-rate-limit-budget-model) assumes per-hop generated proofs,
where forwarding consumes from the node's own `R_node` budget.
With sender-generated proofs, the initiating node generates `L` proofs per originated packet from its own `R_node`,
while forwarding nodes only verify and do not consume their own budget.
A future revision MAY define an adapted budget model for this architecture,
including revised slot pool semantics and pre-computation sizing.

### 11.4 Inbound Cover

Inbound reply traffic varies with a node's requests ([§10.5](#105-inbound-observability)).
A future enhancement MAY define a constant request rate per node,
with unused SURBs answered by dummy replies,
or a provider-style model in which a trusted first hop delivers inbound traffic to the node at a constant rate.

### 11.5 Drop Cover

A drop packet is a loop whose final hop discards it instead of returning it:
built by the same selector under the same constraints,
carrying the cover codec,
and terminating at a mix node other than the originator.
If ticks with nothing waiting carried drops rather than loops,
the number of a node's originations that do not return would be fixed by the clock,
whatever its real traffic,
and the count of [§10.5](#105-inbound-observability) would no longer contain `sent`.
This is the payload-stream filler of Loopix,
on which its sender-unobservability argument rests.

Drop cover is deferred from this revision for three reasons.
A drop must carry every proof a real message carries at the exit,
including any exit abuse prevention proof ([Mix Protocol §6.3](mix.md#63-exit-abuse-prevention)),
since a packet the exit rejects is distinguishable by that rejection;
under a proof-of-work scheme that is continuous work for packets nobody reads,
and whether a deployment can afford it depends on the exit abuse scheme it chooses.
Under exit ≠ destination, the exit of a real message opens an onward connection and the exit of a drop does not,
so a passive observer at the exit classifies drops without controlling the exit,
thinning the cover by the fraction of exits it can watch.
And drops close the channel only for traffic that expects no reply;
a requester's rate remains visible through its replies until [§11.4](#114-inbound-cover) lands,
so the gain is partial until then.
A future revision MAY add drop packets on ticks with nothing waiting,
with the accounting above,
once the exit abuse scheme and inbound cover are settled.
Such a revision would also need a companion change to [Mix Protocol §6.4](mix.md#64-cover-traffic),
which limits cover traffic to loop messages;
the loop-only design of this revision satisfies that constraint as written.

### 11.6 Enforced Origination Quota

The origination clock is a convention ([§10.6](#106-the-origination-cap-is-a-convention)).
A future revision of the DoS protection specification MAY add an origination proof,
carried inside the Sphinx payload and verified at the exit,
drawn from a per-node origination quota.
This would bound origination cryptographically and independently of the forwarding budget.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p Mix Protocol](mix.md)
- [Mix DoS Protection](mix-dos-protection.md)
- [Mix RLN DoS Protection](mix-dos-protection-rln.md)
- [Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md)
- [Mix Path Selection (in progress)](https://github.com/logos-co/logos-lips/pull/445)
- [Loopix: Providing Anonymity in a Message Passing System](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska)
- [Nym: Mixnet for Network-Level Privacy](https://nymtech.net/nym-whitepaper.pdf)
