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
The architecture ensures that an observer of a mix node's emissions
cannot tell whether the node is sending its own messages,
how many,
or when.
Every packet the node originates leaves on a tick of a random clock
whose behaviour does not depend on the node's traffic.
It defines the Poisson-Rate emission strategy,
the two kinds of cover packet the strategy emits,
and how the rate-limit budget is divided between origination and forwarding.

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

All three attacks rely on the same weakness:
a node's emission pattern leaks whether it is carrying non-cover traffic,
either in how many packets it emits or in when it emits them.

Cover traffic addresses this by making a node's emission pattern independent of its non-cover traffic
in both volume and timing.
A node emits one packet on every tick of a clock with exponentially distributed gaps.
When the node has a message of its own to send, the message takes the next tick;
when it has none, a dummy packet takes the tick instead.
The clock does not know which is which,
so neither does an observer.

The Mix Protocol defines cover traffic as a pluggable component (see [Mix Protocol §6.4](mix.md#64-cover-traffic)).
This specification provides a concrete instantiation of that component.
The architecture is designed to be compatible with the DoS protection mechanism defined in [Mix DoS Protection](mix-dos-protection.md)
and specifically with the [Mix RLN DoS Protection](mix-dos-protection-rln.md) mechanism.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in BCP 14
([RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119), [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174))
when, and only when, they appear in all capitals, as shown here.

Other terms used in this document are as defined in the [libp2p Mix Protocol](mix.md) and [Mix DoS Protection](mix-dos-protection.md).

The following additional terms are used throughout this specification:

- **Origination**
  Any packet a node emits as the first hop of its path:
  a locally originated message, a SURB reply the node produces as an exit, or a cover packet.
  Forwarded packets are not originations.

- **Origination Clock**
  A per-node timer whose gaps between ticks are sampled independently from an exponential distribution
  with the deployment-wide mean `μ_tick` seconds.
  The clock runs continuously from node start and is not reset or aligned at epoch boundaries;
  the number of ticks that fall within one epoch is a Poisson random variable with mean `P / μ_tick`.
  Every origination leaves the node on a tick of this clock and never between ticks.

- **Tick**
  One firing of the origination clock.
  Each tick is labelled, independently of every other tick and of any pending traffic,
  as a *loop tick* with probability `f_loop` or as a *real-eligible tick* otherwise.

- **Loop Packet**
  A cover packet whose path returns to the originating node.
  Loop packets are emitted only on loop ticks
  and real traffic never takes a loop tick.

- **Drop Packet**
  A cover packet whose final hop is a mix node other than the originator,
  which discards it during exit processing.
  Drop packets fill real-eligible ticks that no locally originated message or SURB reply is waiting to use.

- **Reserved Loop Share `f_loop`**
  The deployment-wide probability that a tick is labelled a loop tick,
  and therefore the expected fraction of a node's ticks that carry loop packets.
  Loop ticks are reserved: real traffic never takes them.

- **`R_node`**
  A node's rate limit per epoch on outgoing packets, as assigned by the DoS protection mechanism.
  Under a flat rate limit every node has `R_node = R_base`;
  under [Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md) `R_node` is the node's `user_message_limit`,
  which is at least `R_min`.

- **`R_min`**
  The smallest rate limit any mix node in the deployment may hold.
  Under a flat rate limit `R_min = R_base`;
  under stake-weighted rates it is the `R_min` of that specification.

- **Slot**
  A single rate-limit token within an epoch's budget of `R_node` tokens, as defined by the DoS protection mechanism.
  Each outgoing packet — whether cover or non-cover — consumes exactly one slot.

- **Origination Share** and **Forwarding Share**
  The two parts into which an epoch's `R_node` slots are divided ([§4](#4-rate-limit-budget-model)).
  The origination share is the same for every node;
  the forwarding share is whatever remains of `R_node`.
  Ticks claim from the origination share;
  forwarded packets claim from the forwarding share.

- **Epoch**
  A fixed time window of duration `P` seconds during which each mix node is permitted to emit at most `R_node` packets,
  as enforced by the DoS protection mechanism.

## 3. Design Principles

The cover traffic architecture is guided by the following principles:

- **Sender unobservability**: A node's emission pattern does not depend on its non-cover traffic,
  in either volume or timing.
  The node's inbound pattern does not depend on its non-cover traffic
  as far as cover traffic can influence it ([§10.5](#105-inbound-observability)).
- **Substitution, not addition**: The clock emits exactly one packet per tick whether or not the node has anything to send.
  A real-eligible tick carries a locally originated message or SURB reply if one is waiting,
  and a drop packet otherwise.
  Real traffic therefore replaces cover on a tick and never adds an emission the clock would not have produced,
  so the number and timing of a node's originations are fixed by the clock alone.
- **Indistinguishability**: Cover packets are structurally identical to non-cover Sphinx packets in size and routing behavior,
  preventing packet-level classification ([Mix Protocol §6.4](mix.md#64-cover-traffic)).
  Cover packets are built by the same path selector, under the same path constraints,
  as the locally originated messages they stand in for ([§5.1](#51-cover-packet-construction)).
- **Two cover types**: Loop packets return to the originator and are emitted only on loop ticks,
  which real traffic never uses ([§5.2](#52-slot-claims));
  the loop return rate is therefore constant.
  Drop packets terminate at another node and are emitted on real-eligible ticks not taken by real traffic;
  they do not return,
  so real traffic does not affect what the node receives.
- **Uniformity**: The tick mean `μ_tick` and the reserved loop share `f_loop` are deployment-wide constants.
  A node whose clock differs from its peers is identifiable by its rate alone ([§10.8](#108-uniformity-of-the-origination-clock)).
- **DoS protection compliance**: All cover traffic operates within the rate-limit budget `R_node` enforced per epoch.
  Proofs are epoch-bound and unused slots are discarded at epoch boundaries ([Mix DoS Protection](mix-dos-protection.md)).
- **Slot integrity**: Each rate-limit slot is spent on the wire at most once per epoch.
  A pre-built drop packet whose real-eligible tick is taken by a real message is discarded together with its pre-computed proof;
  that proof is never sent ([§5.2](#52-slot-claims)),
  and the real message carries a fresh proof for the slot the tick claimed.
- **Mix node only**: Cover traffic is generated only by mix nodes that forward traffic for other nodes
  and participate continuously in the network.
  Initiating-only nodes are mostly short-lived with dynamic identifiers and do not forward traffic,
  making cover traffic neither practical nor beneficial for them ([§8](#8-initiating-only-node-considerations)).
- **Pre-computation**: As an optimization, cover packets and their proofs can be generated during epoch `N-1`,
  so they are ready to emit at the start of epoch `N` without any cryptographic work at emission time.

## Overview

A mix node plays multiple roles at once: it sends its own messages, relays messages for other nodes, and ideally hides which of these it is doing.
Without protection, an observer watching the node's outgoing packets can tell when it is active, how busy it is, and when it is idle —
enough to link users to their messages through traffic patterns.

This specification makes every origination leave on a tick of the origination clock.
The clock fires at random moments with exponentially distributed gaps.
On each tick the node sends exactly one packet:
on a real-eligible tick, a locally originated message or SURB reply if one is waiting, and a drop packet otherwise;
on a loop tick, a loop packet.
An observer sees the same stream of originations —
the same rate, the same random shape —
whether the node is idle or sending at capacity.

Forwarded packets do not use the clock.
They leave after the mixing delay the sender encoded for this hop,
which is exponentially distributed,
so a node's forwarded output is already a memoryless random stream.
Originations emitted on an exponential clock have the same shape,
and the merge of the two streams is a single memoryless stream
in which no packet can be attributed to either source by timing ([§7](#7-poisson-rate-emission-strategy)).

The node operates under a rate limit that bounds total packets emitted per epoch ([§4](#4-rate-limit-budget-model)).
Every packet — cover, locally originated, SURB reply, or forwarded — consumes one slot.
The budget is divided into an origination share, claimed by ticks,
and a forwarding share, claimed by forwarded packets;
neither can starve the other.

Cover packets come in two kinds.
Loop packets return to the originator and occupy a reserved share of ticks that non-cover traffic cannot take,
which keeps the rate of returning loops constant.
Drop packets terminate at another node and fill the remaining ticks when nothing real is waiting;
they are the only cover a real message ever takes the place of ([§5.1](#51-cover-packet-construction)).
For efficiency, cover packets and their rate-limit proofs MAY be pre-built during the previous epoch ([§6.1](#61-at-epoch-boundary))
and revalidated at send time in case the underlying state has changed ([§6.5](#65-pre-computed-proof-validation-at-send-time)).

Each epoch begins by discarding previous state and initializing a fresh slot budget,
loading any pre-built cover packets prepared during the prior epoch.
Throughout the epoch the clock ticks;
each tick claims one slot and emits one packet,
or is silent if the origination share is spent.
Forwarded packets claim from the forwarding share as they arrive.
Near the midpoint, the node starts pre-computing cover packets for the next epoch.
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
The origination share is `ceil(R_min / (1 + L))` slots and is the same for every node in the deployment,
since the tick mean is a deployment-wide constant ([§10.8](#108-uniformity-of-the-origination-clock))
and the share has to fit within the budget of the lowest-rate node.
The tick mean MUST be chosen so that the per-epoch tick count exceeds the share only rarely:

```text
Pr[ Poisson(P / μ_tick) > ceil(R_min / (1 + L)) ] ≤ 0.01
```

With `R_min = 100`, `L = 3`, and `P = 10 s`, the origination share is 25 slots
and `P / μ_tick = 15` — a tick mean of about `0.67 s` — satisfies the bound with a probability of about 0.6%.
A deployment whose `R_min / (1 + L)` is too small to admit a useful tick rate under this bound
MUST raise `R_min` rather than lower the bound.
When the count does exceed the share, the remaining ticks of that epoch are silent ([§6.2](#62-cover-emission)).
Because non-cover originations replace ticks rather than adding to them,
whether a tick is silent depends only on the node's own clock and never on its non-cover traffic.

**Forwarding share.**
The forwarding share is whatever remains of the node's budget after the origination share:
`R_node − ceil(R_min / (1 + L))` slots per epoch,
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
([§10.8](#108-uniformity-of-the-origination-clock)).
The configured path length `L` for cover packets
MUST match the path length used for locally originated messages
as defined in [Mix Protocol §6](mix.md#6-pluggable-components).

### 5.1 Cover Packet Construction

**Trigger:** A tick of the origination clock fires and no locally originated message or SURB reply is waiting,
or the tick is a loop tick ([§6.2](#62-cover-emission)).

**[During Sphinx packet construction](mix.md#85-packet-construction):**
The mechanism constructs a cover Sphinx packet
following the same construction procedure as a locally originated message.
Cover paths MUST be requested from the same path selector, under the same path constraints,
as locally originated messages ([Mix Path Selection](mix-path-selection.md)).
The differences are:

- **Loop packet** (loop tick): the mix path returns to the originating node.
  The path is requested from the configured path selector with purpose `COVER`
  ([Mix Path Selection](mix-path-selection.md)),
  so that any hop positions the selector fixes for locally originated messages are fixed for loops as well.
  The hop adjacent to the originator on the return leg
  MUST be drawn from the same candidate set as the fixed first hop, when one is configured;
  otherwise the returning packet reveals the originator to an arbitrary node
  as the successor of a fixed-hop node.
  This requires at least two candidates in that set.
- **Drop packet** (real-eligible tick with nothing waiting): the final hop is a mix node other than the originator,
  selected by the same path selector under the same constraints as a locally originated message,
  and the packet is built as an exit-at-final-hop packet whose payload carries the cover codec,
  so that the final hop discards it during exit processing ([§5.4](#54-cover-packet-reception)).
  A drop packet MUST carry every proof a locally originated message would carry at the exit,
  including any exit abuse prevention proof ([Mix Protocol §6.3](mix.md#63-exit-abuse-prevention));
  a packet the final hop would reject is distinguishable from real traffic by that rejection.
- The origin protocol codec MUST be set to the cover traffic codec defined in [§5](#5-integration-with-the-mix-protocol).
- The application message content MUST be filled with cryptographically random bytes.
- If pre-computation is enabled, the pre-built cover packet is used directly without re-construction.

**Wire format:**
Cover packets use the exact Sphinx packet format defined in [Mix Protocol §8](mix.md#8-sphinx-packet-format).
No additional fields or framing are introduced.
A cover packet on the wire is indistinguishable from a non-cover traffic packet,
ensuring that intermediary nodes and external observers cannot classify packets as cover or non-cover.

The cover packet is transmitted to its first hop on the tick that selected it.
No further delay is applied:
the wait for the tick is the pre-send delay ([§6.3](#63-locally-originated-message-sending)).

### 5.2 Slot Claims

**Procedure:** `ClaimSlot(kind) -> success`, where `kind ∈ { TICK, FORWARD }`

**Trigger:** The origination clock fires (`TICK`),
or the Mix Protocol needs to forward a packet (`FORWARD`).

The pool tracks the origination share and the forwarding share separately ([§4](#4-rate-limit-budget-model)).

1. A `TICK` claim takes one slot from the origination share and returns success.
   If the origination share is exhausted, the claim fails and the tick is silent ([§6.2](#62-cover-emission)).
2. A `FORWARD` claim takes one slot from the forwarding share and returns success.
   If the forwarding share is exhausted, the claim fails and the packet is dropped ([§6.4](#64-packet-forwarding)).

A `FORWARD` claim MUST NOT take an origination-share slot,
and a `TICK` claim MUST NOT take a forwarding-share slot.

Locally originated messages and SURB replies do not claim slots directly.
They are placed in the origination queue and take the next real-eligible tick ([§6.3](#63-locally-originated-message-sending))
instead of the drop packet that tick would otherwise have carried.
If a pre-built drop packet was queued for that tick, it is discarded;
its pre-computed proof MUST NOT be sent on the wire.
The message index bound into the discarded proof MAY be reused by the real message's proof
where the DoS protection mechanism permits ([§6.5](#65-pre-computed-proof-validation-at-send-time));
otherwise it is left unspent.
In either case at most one proof per index reaches the wire.
Real traffic MUST NOT take a loop tick.

On a successful claim, the caller either uses the pre-computed proof of a pre-built packet
or generates a DoS protection proof
via `GenerateProof(binding_data)` ([Mix DoS Protection §8.2.1](mix-dos-protection.md#821-proof-generation)),
where `binding_data` is the packet-specific data as defined by the DoS protection mechanism.

### 5.3 Epoch Boundary

**Procedure:** `ResetEpoch(epoch) -> void`

**Trigger:** The DoS protection mechanism signals the start of a new epoch
via `OnEpochChange` ([Mix DoS Protection §8.2.3](mix-dos-protection.md#823-epoch-change-notification)).
The Mix Protocol MUST call `ResetEpoch` before processing any packets in the new epoch.

The mechanism refreshes the slot pool for the new epoch:
all remaining slots from the previous epoch are discarded,
and a new pool of `R_node` slots is initialized with its origination and forwarding shares.
If pre-computation is enabled, the pre-built cover packets prepared during the previous epoch
are loaded into the new pool.

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

For a loop packet, the exit node is the originating node itself.
Implementations SHOULD use the reception event of loop packets for path health monitoring ([§11.2](#112-path-health-monitoring));
because real traffic never takes a loop tick,
the loop return rate per path is a steady signal.

For a drop packet, the exit node is another mix node,
which learns that the packet its predecessor forwarded was cover.
The Sphinx construction prevents that node from identifying the originator.
The consequences are discussed in [§10.7](#107-drop-packet-classification-by-the-terminating-node).

### 5.5 Data Structures

```text
PrebuiltCoverPacket {
  kind:           enum { LOOP, DROP }   // Which tick label this packet is built for
  slot_id:        bytes                 // Message index the pre-computed proof is bound to
  packet:         bytes                 // Pre-built wire-format packet (Sphinx packet + DoS protection proof), ready to transmit
  path:           []bytes               // Ordered list of mix node identifiers on the cover path
  created_at:     uint64                // Unix timestamp (seconds) when this packet was constructed
}
```

```text
SlotPool {
  epoch:                  uint64                 // The epoch this pool belongs to
  origination_remaining:  uint32                 // Origination-share slots still spendable in this epoch
  forwarding_remaining:   uint32                 // Forwarding-share slots still spendable in this epoch
  loop_queue:             []PrebuiltCoverPacket  // Pre-built loop packets
  drop_queue:             []PrebuiltCoverPacket  // Pre-built drop packets, discarded when a real message takes their tick
}
```

```text
CoverTrafficConfig {
  tick_mean:      float64   // μ_tick, mean gap between ticks in seconds; deployment-wide (see §7)
  loop_fraction:  float64   // f_loop ∈ (0.0, 1.0); deployment-wide; RECOMMENDED default 0.5 (see §7)
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
The cover traffic mechanism pre-builds loop and drop packets during epoch `N-1` for use in epoch `N`
(see [§9.1](#91-pre-computation-scheduling) for sizing).
For each packet, construct a cover Sphinx packet following the procedure in [§5.1](#51-cover-packet-construction)
and generate a DoS protection proof for the **next** epoch
via `GenerateProof(binding_data)` ([Mix DoS Protection §8.2.1](mix-dos-protection.md#821-proof-generation)).
Store the result as a [`PrebuiltCoverPacket`](#55-data-structures).
Ticks for which no pre-built packet of the required kind is available require on-demand generation.
Pre-computed proofs are bound to a specific epoch and MUST NOT be reused in subsequent epochs.

**Proof validity over time:**
Pre-computed proofs may be invalidated within their target epoch, not just across epochs.
For example, in [Mix RLN DoS Protection](mix-dos-protection-rln.md),
accumulating membership updates can push the root used at generation time
out of the current `acceptable_root_window_size` before the epoch ends.
Implementations MUST therefore validate pre-computed proofs at send time
(see [§6.5](#65-pre-computed-proof-validation-at-send-time)).

**Fallback caveat:**
On-demand generation when pre-computation falls behind adds load-dependent delay
after the tick that selected the packet,
skewing emission timing in a way that correlates with pre-computation load
and weakens timing unobservability.
Implementations SHOULD size the pre-computation pipeline ([§9.1](#91-pre-computation-scheduling))
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
> 2. Label the tick: a loop tick with probability `f_loop`, otherwise a real-eligible tick.
>    The label is sampled independently of every previous label and of the origination queue.
> 3. Call `ClaimSlot(TICK)` ([§5.2](#52-slot-claims)).
>    If the claim fails, the tick is silent: emit nothing and return to step 1.
> 4. Select the packet:
>    - a. Loop tick: dequeue the head of `loop_queue`,
>      or build a loop packet on demand if the queue is empty ([§5.1](#51-cover-packet-construction)).
>    - b. Real-eligible tick with a locally originated message or SURB reply waiting:
>      take the ready packet at the head of the origination queue.
>      If a pre-built drop packet would have used this tick, discard it ([§5.2](#52-slot-claims)).
>    - c. Real-eligible tick with nothing waiting: dequeue the head of `drop_queue`,
>      or build a drop packet on demand if the queue is empty.
> 5. Validate the packet's proof per [§6.5](#65-pre-computed-proof-validation-at-send-time),
>    whether the packet was pre-built cover or a message built on enqueue.
> 6. Transmit the packet to its first hop immediately.
>    Only the `packet` field of a [`PrebuiltCoverPacket`](#55-data-structures) is sent;
>    other fields are internal and MUST NOT be sent.

**Readiness:**
Every packet a tick can select MUST be ready to transmit before the tick fires.
Loop and drop packets are pre-built ([§6.1](#61-at-epoch-boundary));
locally originated messages and SURB replies are built, proof included, when they are enqueued ([§6.3](#63-locally-originated-message-sending)).
A packet built after its tick would leave later than a pre-built one by its construction and proving time,
which would distinguish real originations from cover by timing alone.
On-demand construction (steps 4.a and 4.c) is the exception this rule tolerates,
and [§9.1](#91-pre-computation-scheduling) sizes the pipeline so that it is rare.

**Silent ticks:**
A tick is silent only when the origination share of the current epoch is exhausted.
Because every tick claims exactly one slot regardless of what it carries,
exhaustion depends on the node's own tick count in the epoch and on nothing else;
in particular it does not depend on how many real originations the node had.
With `μ_tick` chosen per [§4](#4-rate-limit-budget-model), silent ticks occur in fewer than 1% of epochs.

### 6.3 Locally Originated Message Sending

**[During Sphinx packet construction](mix.md#85-packet-construction):**
When the Mix Entry Layer submits a locally originated message for mixification,
the Mix Protocol instance MUST construct its Sphinx packet and DoS protection proof immediately
and place the ready packet in the origination queue ([§6.2](#62-cover-emission), readiness).
The packet is transmitted on the next real-eligible tick ([§6.2](#62-cover-emission), step 4.b),
after send-time proof validation ([§6.5](#65-pre-computed-proof-validation-at-send-time)),
since the proof may have been generated in an earlier epoch or against a root that has since rotated.

**Pre-send delay:**
The wait from enqueueing to the next real-eligible tick is exponentially distributed
with mean `μ_tick / (1 − f_loop)`,
because the real-eligible ticks form a thinned exponential clock.
This wait is the pre-send delay of [mix.md §8.5.2](mix.md#852-construction-steps) Step 3.f;
no additional delay is sampled,
and the Step 3.f distribution is this one.
End-to-end delay estimates ([mix.md §9.4.2](mix.md#942-no-built-in-retry-or-acknowledgment)) therefore include this mean
for the origination and reply pre-send terms.

**Queueing:**
If real originations arrive faster than real-eligible ticks fire,
the origination queue grows and latency increases;
no origination is ever sent off-tick.
Applications SHOULD keep their sustained real rate below `(1 − f_loop) / μ_tick` packets per second.

### 6.4 Packet Forwarding

**[During Sphinx packet handling](mix.md#86-sphinx-packet-handling):**
When the Mix Protocol instance acts as an intermediary and receives a Sphinx packet to forward,
it MUST first call `ClaimSlot(FORWARD)` ([§5.2](#52-slot-claims)) before applying the mixing delay.
This ensures no two forwarded packets consume the same slot regardless of how their mixing delays overlap.
If no slot can be claimed, the packet is dropped.
Otherwise, the Mix Protocol instance proceeds with
[intermediary processing](mix.md#863-intermediary-processing).

**Slot consumption:**
The slot is consumed on successful `ClaimSlot(FORWARD)`, not on transmission.

**Send timing:**
The packet is dispatched when its mixing delay elapses,
independently of the origination clock.
Forwarded packets never use ticks.

### 6.5 Pre-Computed Proof Validation at Send Time

Before transmitting a pre-built cover packet,
the mechanism MUST validate the carried DoS protection proof against the current state
(see [§6.1](#61-at-epoch-boundary) for rationale).
For [Mix RLN DoS Protection](mix-dos-protection-rln.md),
this means verifying the `merkle_root` bound into the proof
is still within the node's `acceptable_root_window_size`.

If validation fails, implementations MUST either:

- **Regenerate** the proof against the current anchor, keeping the Sphinx packet body unchanged; or
- **Skip** the emission if regeneration is infeasible.

A pre-built packet with a stale proof MUST NOT be sent.
When regenerating, implementations MAY reuse the message identifier bound to the cover packet
where the DoS protection mechanism permits (see [Mix RLN DoS Protection](mix-dos-protection-rln.md)).

### 6.6 SURB Reply Origination at the Exit

A SURB reply produced by an exit node is an origination of that node
([mix.md §8.7.3](mix.md#873-using-a-surb)).
The exit MUST build the reply, proof included, when it is produced
and place the ready packet in its origination queue,
transmitting it on its next real-eligible tick exactly as a locally originated message ([§6.3](#63-locally-originated-message-sending)).
The reply follows the return path the initiator built into the SURB;
the constraints that path is subject to are those of [Mix Path Selection](mix-path-selection.md).
The reply's pre-send delay is therefore the tick wait,
with the same mean as at the initiator.
Replies SHOULD be placed ahead of the exit's own locally originated messages in the queue,
so that a reply waits for one real-eligible tick and not for the queue to drain;
this ordering is internal to the exit and is not observable.

**Reply timeouts:**
A round trip now includes two tick waits — one at the initiator and one at the exit — in addition to the mixing delays.
Each wait exceeds `x` seconds with probability `exp(−x × (1 − f_loop) / μ_tick)`;
at the parameters of [§7](#7-poisson-rate-emission-strategy) a single wait exceeds 5 s about 2% of the time and 9 s about 0.1% of the time.
An initiator that times out before the reply has had that long to leave the exit will retransmit a request whose reply is still queued.
Duplicate requests spend real-eligible ticks and SURBs on both sides,
and the interval at which a node retransmits is itself observable.
Reply timeouts ([mix.md §9.4.2](mix.md#942-no-built-in-retry-or-acknowledgment)) therefore need to be sized to the tail of both tick waits,
not to their means,
and origin protocols SHOULD deduplicate requests, since the Mix Protocol is stateless and cannot.

A request carries at most two SURBs ([mix.md §8.5.1](mix.md#851-inputs)),
so serving one request costs the exit at most two real-eligible ticks.
An exit serving many requests spends its real-eligible ticks on replies
and originates fewer of its own messages;
its emission count and timing do not change.

## 7. Poisson-Rate Emission Strategy

The node runs the origination clock of [§6.2](#62-cover-emission):
inter-tick gaps are exponential with the deployment-wide mean `μ_tick`,
every tick emits exactly one packet,
a locally originated message or SURB reply substitutes for the drop packet a real-eligible tick would otherwise carry,
and loop ticks are never substituted.

**Parameters:**

- `μ_tick`, the tick mean, chosen per [§4](#4-rate-limit-budget-model) against the lowest rate limit in the deployment,
  so that the per-epoch tick count exceeds the origination share with probability at most 1%.
  With `R_min = 100`, `L = 3`, `P = 10 s`: `μ_tick ≈ 0.67 s`, about 15 ticks per epoch.
- `f_loop`, the reserved loop share.
  The RECOMMENDED default is `0.5`.
  Real-eligible ticks then fire at `(1 − f_loop) / μ_tick = 0.75 /s`,
  which is the node's maximum sustained rate of real originations.
  Any positive share keeps the loop return rate constant;
  the value trades real capacity against the density of the path-health signal ([§11.2](#112-path-health-monitoring))
  and has not been validated by simulation.

**Why the emission is unobservable:**
A stream of events with independent exponential gaps is a Poisson process.
Forwarded packets leave the node after independent exponential mixing delays,
so the node's forwarded output is a Poisson process to the extent that its forwarding arrivals are one
(see [§10.9](#109-interaction-with-fixed-hop-path-selection)).
Two Poisson processes merged form a single Poisson process,
whatever their rates,
and a single Poisson process carries no information about which of its events came from which source.
An observer of the node's output therefore sees one memoryless stream
whose rate is the forwarding rate plus `1 / μ_tick`,
and cannot classify any packet as originated or forwarded by timing.
Because real originations substitute for ticks, the origination rate is `1 / μ_tick` whether the node is idle or busy;
the observer learns neither when nor how much the node sends.
This holds for any tick mean and does not require `μ_tick` to equal the mixing delay mean.

**Why loops are reserved:**
If real originations could take any tick,
a busy node would send fewer loop packets and receive fewer loop returns,
and an observer of its inbound link would see the drop.
Reserving loop ticks fixes the loop return rate at `f_loop / μ_tick` regardless of load ([§10.5](#105-inbound-observability)).
The price is that only `(1 − f_loop)` of the clock is available to real traffic.

**Why the remaining cover is drops:**
A dummy that stands in for a real message must not return,
or the node's inbound would rise whenever it is idle and fall whenever it is busy.
Drop packets terminate at another node and never come back.
They cost a per-hop proof at every hop and an exit proof at the final hop, like any real message ([§5.1](#51-cover-packet-construction)).

**Characteristics:**
Per epoch, the node emits `Poisson(P / μ_tick)` originations,
of which `Poisson(f_loop × P / μ_tick)` are loops.
Silent ticks occur only when the epoch's origination share is exhausted,
in fewer than 1% of epochs at the parameters above,
and their occurrence is independent of the node's real traffic.
A real origination waits for the next real-eligible tick:
an exponential wait with mean `μ_tick / (1 − f_loop)`, about `1.3 s` at the parameters above,
with the same tail shape as a mixing delay.
Sustained real demand above `(1 − f_loop) / μ_tick` queues rather than leaks ([§6.3](#63-locally-originated-message-sending)).

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

Deployments where this matters SHOULD route initiating-only traffic through trusted first hops
([Mix Path Selection](mix-path-selection.md)).

If an initiating-only node is promoted to a mix node and becomes long-lived,
it SHOULD start the origination clock immediately upon promotion.
During the first epoch after promotion, pre-computed cover packets are unavailable;
the node SHOULD fall back to on-demand cover packet generation for that epoch
and begin pre-computation immediately upon promotion.

## 9. Implementation Recommendations

This section provides non-normative guidance for implementers.

### 9.1 Pre-computation Scheduling

The pre-computation pipeline SHOULD be initiated at the midpoint of the current epoch
to allow sufficient time for packets to be built before the next epoch begins.
Implementations SHOULD interleave pre-computation with normal packet processing
(_e.g.,_ yielding to non-cover traffic between packet generations) to avoid contention with ongoing packet handling.

Rather than pre-computing all cover packets in the previous epoch,
implementations MAY batch pre-computation across epochs:
an initial batch during epoch `N-1` to ensure cover packets are available at the start of epoch `N`,
with subsequent batches computed incrementally during epoch `N` itself, staying ahead of the clock.
This reduces peak computational load and memory usage.

**Sizing:**
Loop and drop packets are pre-built separately.
The expected demand per epoch is `f_loop × P / μ_tick` loop packets and `(1 − f_loop) × P / μ_tick` drop packets,
each a Poisson count;
implementations SHOULD pre-build each kind to its mean plus `3 × sqrt(mean)`
so that on-demand construction is rare.
A pre-built drop packet whose final hop has left the node pool is discarded and rebuilt.

### 9.2 Pool Status Tracking

Implementations SHOULD maintain runtime counters for available slots, cover emissions, and non-cover consumptions.
These aid in diagnostics, monitoring, and tuning.

The non-cover consumption counter is subject to the exposure restriction of [§10.10](#1010-exposure-of-real-traffic-counters).

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

### 10.1 Proof Reuse via Proof Leakage

If a pre-computed cover proof and a freshly generated non-cover proof for the same slot are both sent on the wire,
the DoS protection mechanism detects a reuse.
Depending on the mechanism, this may result in slashing or reputation loss for the node.
The slot integrity principle ([§3](#3-design-principles)) prevents this
by ensuring that a pre-built drop packet's proof is discarded whenever a real message takes its tick,
so that only one proof per slot ever reaches the wire.

### 10.2 Origination Share Exhaustion

A tick that finds the origination share exhausted is silent ([§6.2](#62-cover-emission)).
Because a tick claims one slot whether it carries a loop, a drop, or a real origination,
exhaustion is a function of the node's own tick count in the epoch only.
An observer who sees an epoch end in silence learns that the node's clock fired unusually often,
which is independent of the node's real traffic.
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
its ticks are a Poisson process, like the forwarded output it merges with,
and there is no grid to recover.

### 10.4 Forwarding Cap and Forwarded Packet Drops

Forwarded packets are dropped once the forwarding share is exhausted ([§6.4](#64-packet-forwarding)).
Without the cap, an adversary who routes enough traffic through a node could consume its whole budget
and silence its origination clock,
muting the node's real and cover traffic together.
With the cap, such a flood costs the adversary dropped packets and leaves the node's origination untouched.

Drops are visible to the originators of the dropped packets as failed loop returns and missing replies,
and are an input to local reputation.
Persistent forwarding-share exhaustion indicates that `R_node` is too low for the network's forwarding load
or that the node is under attack ([§9.3](#93-slot-exhaustion-logging)).

### 10.5 Inbound Observability

This specification fixes what a node **emits**.
What a node **receives** is only partly under its control:

- Forwarded packets arrive at the network's forwarding rate, independent of the node's own activity.
- Loop packets return at `f_loop / μ_tick` per second, because real traffic never takes a loop tick.
  Without the reservation, a node whose real originations took every tick would send no loops and receive none,
  and its inbound rate would fall by up to `1 / μ_tick` per second as it became busy —
  a change an observer of the inbound link detects within a few epochs.
- SURB replies arrive in proportion to the requests the node has sent:
  at most two per request ([§6.6](#66-surb-reply-origination-at-the-exit)).
  This component is not covered by this specification.
  Its magnitude is small per epoch and becomes observable only over long sessions,
  once the accumulated excess exceeds the natural fluctuation of the inbound count.
  Making inbound reply traffic constant requires a constant request rate with dummy replies,
  which is left to future work ([§11.4](#114-inbound-cover)).

The same holds at an exit: its own inbound reply rate varies with the requests it has made,
while its emission does not vary with the replies it serves.

### 10.6 The Origination Cap Is a Convention

The origination clock bounds a node's origination rate by construction,
but nothing verifies another node's clock.
A node that originates faster than its tick mean allows — up to its whole budget `R_node` —
is not detectable by any single neighbor,
since the excess is spread across all first hops.
It is detectable by its forwarding behavior:
having spent its slots on origination, it drops the packets it should forward,
and local reputation excludes it from paths.
The clock therefore protects the anonymity of nodes that follow it
and does not by itself bound what a node that ignores it can impose on the network.
An origination proof verified at the exit,
drawn from a per-node origination quota separate from the forwarding budget,
would make the cap enforceable;
this belongs to the DoS protection specification ([§11.5](#115-enforced-origination-quota)).

### 10.7 Drop Packet Classification by the Terminating Node

The final hop of a drop packet learns that the packet was cover.
It cannot learn who originated it:
the Sphinx construction reveals only the predecessor hop,
and the predecessor is a relay chosen by the same selector as for real traffic.
An adversary controlling a fraction `β` of nodes can therefore classify a fraction `β` of drop packets
and discount them from any correlation it attempts,
which thins the effective drop cover by that fraction and no more.
Loop packets are never classifiable by any party other than the originator,
which is why the reserved loop share is kept even though drops alone would suffice for emission unobservability.

### 10.8 Uniformity of the Origination Clock

The unobservability argument of [§7](#7-poisson-rate-emission-strategy) requires every mix node to run the same clock.
A node running a faster or slower clock is identifiable by its origination rate alone,
and its anonymity set shrinks to the nodes sharing its rate.
Accordingly:

- Every mix node that forwards traffic MUST run the origination clock.
  A node that forwards traffic without emitting cover has a visibly lower origination rate than its peers.
- `μ_tick` and `f_loop` MUST be deployment-wide constants,
  independent of a node's rate-limit budget `R_node`.
  They are derived from `R_min` ([§4](#4-rate-limit-budget-model)),
  so that every node, including one at the floor stake, can sustain them.
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

### 10.9 Interaction with Fixed-Hop Path Selection

The argument of [§7](#7-poisson-rate-emission-strategy) treats a node's forwarding arrivals as a Poisson process,
which holds when they are the merge of many independent senders' traffic.
Under session- or time-based path selection ([Mix Path Selection](mix-path-selection.md)),
a node that is a fixed hop for a high-volume sender receives a concentrated stream from one predecessor.
The exponential mixing delay smooths that stream but does not make it memoryless,
so the merged output of such a node carries some structure from the fixed-hop stream.
This does not affect the node's own originations, which remain on the clock;
it affects what an observer of that node can infer about the fixed-hop sender,
and is a consideration for the path selection specification rather than for this one.

### 10.10 Exposure of Real-Traffic Counters

The non-cover consumption counter ([§9.2](#92-pool-status-tracking)) reveals the exact per-epoch count of real traffic,
which is what traffic analysis aims to recover.
Implementations MUST keep this counter, and any per-epoch breakdown derived from it, in memory only,
and MUST NOT export it via metrics endpoints, structured logs, or any monitoring interface.

## 11. Future Work

### 11.1 Adaptive Tick Mean

`μ_tick` is currently a static deployment-wide configuration.
A future enhancement MAY define a method for a deployment to adapt `μ_tick` to network size and path length.
Any adaptive scheme MUST change `μ_tick` for all nodes together,
never per node ([§10.8](#108-uniformity-of-the-origination-clock)).

### 11.2 Path Health Monitoring

Loop packets follow a valid mix path and return to the originating node,
so their return confirms path liveness.
Because real traffic never takes a loop tick, the return rate per path is steady,
and failures to return indicate node failures or active attacks along the path
rather than the node's own load.
A future revision of this specification MAY define an interface for exposing loop return status
to the path selector ([Mix Path Selection](mix-path-selection.md)),
for example to decide when a fixed-hop candidate is unreachable.

### 11.3 Budget Model for Sender-Generated Proofs

The rate-limit budget model in [§4](#4-rate-limit-budget-model) assumes per-hop generated proofs,
where forwarding consumes from the node's own `R_node` budget.
With sender-generated proofs, the initiating node generates `L` proofs per originated packet from its own `R_node`,
while forwarding nodes only verify and do not consume their own budget.
A future revision MAY define an adapted budget model for this architecture,
including revised slot pool semantics and updated pre-computation sizing.

### 11.4 Inbound Cover

Inbound reply traffic varies with a node's requests ([§10.5](#105-inbound-observability)).
A future enhancement MAY define a constant request rate per node,
with unused SURBs answered by dummy replies,
or a provider-style model in which a trusted first hop delivers inbound traffic to the node at a constant rate.

### 11.5 Enforced Origination Quota

The origination clock is a convention ([§10.6](#106-the-origination-cap-is-a-convention)).
A future revision of the DoS protection specification MAY add an origination proof,
carried inside the Sphinx payload and verified at the exit,
drawn from a per-node origination quota.
Drop packets would carry the same proof.
This would bound origination cryptographically and independently of the forwarding budget.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p Mix Protocol](mix.md)
- [Mix DoS Protection](mix-dos-protection.md)
- [Mix RLN DoS Protection](mix-dos-protection-rln.md)
- [Stake-Weighted Mix RLN DoS Protection](mix-dos-protection-rln-stake-weighted.md)
- [Mix Path Selection](mix-path-selection.md)
- [Loopix: Providing Anonymity in a Message Passing System](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska)
- [Nym: Mixnet for Network-Level Privacy](https://nymtech.net/nym-whitepaper.pdf)
