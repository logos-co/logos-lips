# [RFC] Blend: Tighten connection maintenance after implementation review

**Motivation and proposal:** [PR #468](https://github.com/logos-co/logos-lips/pull/468)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-30 |
| v2 | Numbered the Blend Protocol revision 1.7.0, since the connection rules change | 2026-09-30 |
| v3 | Gave every generated message the same number of copies, `R = 1`, which lowers `F_T` and `TARGET_TXS_PER_BLOCK` to 20; made `T_H` a core node parameter | 2026-10-02 |
| v4 | Held a pending edge handshake towards `Φ_CE^Max` from its identification, gave the 1.4.0 to 1.6.0 rows their merge dates, and answered the remaining review findings | 2026-10-02 |
| v5 | Counted only the messages a node verifies towards a connection's share, sized `F_1` against the shares of the connections a node opens, which raises `F_T` and `TARGET_TXS_PER_BLOCK` to 70, and put a nullifier in the cache from the start of its verification | 2026-10-02 |
| v6 | Left open the bandwidth that reading every copy whole costs | 2026-10-02 |
| v7 | Restored that `V` covers the proof of quota, which the review asked to confirm | 2026-10-02 |

## Reviewer Orientation

Read the PR's Motivation first. Most changes land in rules Blend 1.6.0 introduced: [Expected Traffic](../blend-protocol.md#expected-traffic) and [Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance). The number of copies also reaches the [Quota](../blend-protocol.md#quota).

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Blend Protocol](#affected-specifications): [the shares count verifications](#1-the-shares-count-verifications) | `r_1` counts the novel messages a node verifies, not every message it reads, and a node no longer caps what it sends; `F_1 = (Φ_CC − 2)·r_1·(1 − 1/η) = 20`, draining within `η` instead of `Δ_max + η`; the send deadline counts from the round a message was queued |
| 2 | Critical | [Blend Protocol](#affected-specifications): [one number of copies](#2-one-number-of-copies-for-every-message) | `R = 1` copy of every generated message, cover or data, replaces `R_C = 0` and `R_D = 1`; `F_T` is 70 transactions during 30 rounds, 140 messages with their copies; `Q_C` and `Q_W` double |
| 3 | Critical | [Proof of Work](#affected-specifications): [the reference load](#3-the-reference-load-of-the-blend-difficulty) | `TARGET_TXS_PER_BLOCK`, a consensus constant, from 130 to 70 |
| 4 | High | **Start here** — [Blend Protocol](#affected-specifications): [blacklisting](#4-blacklisting) | a stream that ends or fails no longer blacklists; blacklisting closes open connections; the size cap is gone |
| 5 | High | [Blend Protocol](#affected-specifications): [pending handshakes, the cap and liveness](#5-pending-handshakes-the-handshake-cap-and-liveness) | a pending handshake is held as opened or accepted, and a pending edge handshake towards `Φ_CE^Max`; the cap counts offered handshakes only, `3 + Φ_CE^Max`; liveness is judged at the end of a round |
| 6 | Medium | [Blend Protocol](#affected-specifications): [the nullifier cache](#6-the-nullifier-cache) | membership on the 64 least significant bits, from the start of a verification; the worst-case size |
| 7 | Medium | [Blend Protocol](#affected-specifications): [the receive window](#7-the-receive-window) | a transport requirement: at most `r_1` unread messages on a core connection |
| 8 | Low | [Blend Protocol](#affected-specifications): [the handshake time](#8-the-handshake-time) | `T_H` becomes a core node parameter, counted from the start of the transport handshake |
| 9 | Low | [Chores](#chores) | skim |

# Discussion

## Why a backlog drains within `η`

1.6.0 sized `F_T` so that a backlog drains within `Δ_max + η`, and discarded a queued message after `η`. The two measure the same allowance, so they must agree. A message spends the blending delay `Δ_max` at a blend node before it is released ([Delaying](../blend-protocol.md#delaying)), and only then enters a send queue. A send queue can therefore use no more than the network absorption of one hop, `η` ([Transition Period](../blend-protocol.md#transition-period)).

The other way, a deadline of `Δ_max + η`, lets one link use more than a hop's whole network absorption. The message traversal time `T_M` would no longer bound delivery, and a sender could broadcast a payload directly ([Failure Detection and Reaction](../blend-protocol.md#failure-detection-and-reaction)) while its message is still in flight.

On the share of a single connection, this lowers `F_1` from 16 to 10 messages per round. Counting verifications instead of reads ([below](#why-the-shares-count-verifications)) raises it to 20.

## Why the shares count verifications

1.6.0 counted every message a node reads towards a connection's share. Under flooding, a node reads each message from up to `Φ_CC` neighbors but verifies it once: a copy is discarded at the nullifier check, before any verification. The share therefore held `V` back for copies that cost nothing. In 1.6.0 the honest flood used 16 of the 156 verifications a round.

The share now counts novel messages only. A limit on reads would protect bandwidth alone, and a per-connection rule cannot: a neighbor that streams copies spends as much as it costs the node, and anyone can fill a node's link without a connection. Backpressure stays: a connection whose share is spent is not read, so its backlog waits at the sender, where the `η` deadline applies. The sender's own cap of `r_1` a round had no other job, and is gone.

A message is verified on whichever connection delivers it first, so the flood no longer has to pass through one connection's share. A novel message held back on a spent connection arrives on another. `F_1` is sized against the shares of the `Φ_CC − 2` connections a node opens itself, which no adversary chooses, with the drain margin of `η`: `F_1 = 2·20·(1 − 1/2) = 20`. If the connections a node opened deliver, it verifies the whole flood even when every connection it accepted is silent.

`V` is measured over the full check of a public header, its signature and its proof of quota ([benchmark](https://github.com/logos-blockchain/research/tree/blend-header-verification-benchmark/tools/benchmarks/blend-header-verification)). A nullifier now enters the cache when its verification starts. Otherwise the copies that reach a node from several neighbors while a proof is being verified would each be verified, and the load would climb back towards `Φ_CC·F_1`. A copy that arrives during a verification is checked again once the verification ends, so an invalid message carrying a copied nullifier cannot make a node drop the valid one.

The limit moves to bandwidth: at `F_1 = 20`, a node receives up to 1.5 MB/s and sends 1.2 MB/s.

## Why every message has the same number of copies

1.6.0 sent a block proposal in `1 + R_D = 2` messages and every other message once, with `R_C = 0`. A proposer releases both messages in the round after it generates them, while a node draws its cover messages uniformly over the epoch. A node that releases two messages in one round has therefore almost certainly proposed a block. The count did not balance either: Rewarding removed one cover message per block proposal, and Releasing removed one per data message.

One parameter, `R`, now sets the copies of every message a node generates: a cover message, a block proposal or a transaction. A transaction gets its copy for the same reason, since a single message stands out against paired cover messages. With one value, the proposal term of the `max` in `F_1` never exceeds the cover term. `F_1` is therefore `(F_C + F_T)·(1 + R)·β_max`, and `F_D ≤ F_C` is stated where `F_D` is defined.

`R = 1` keeps a block proposal on two paths. Cover messages then take 6 of the 20 messages a connection carries per round, against 3, so `F_T` is 70 transactions during 30 rounds, 140 messages with their copies, against 170 without copies. `Q_C` doubles, `Q_L` stays 6, and `Q_W` becomes `(1 + R)·β_max = 6`, so one proof of work solution pays for a message and its copy. The activity threshold rises by one bit with `Q_C`, through its formula.

`R = 0` would give `F_T = 170`, but a block proposal would travel one path, and one whose path fails falls back to a direct broadcast ([Failure Detection and Reaction](../blend-protocol.md#failure-detection-and-reaction)).

## Why 64 bits of the nullifier

A nullifier is a field element below `p ≈ 2^254`. Its least significant bits are uniform, while the leading bytes of a big-endian encoding are not, so the cache keeps the low bits and needs no further hash.

Two nullifiers that share those bits make the later message a duplicate, which a node discards and does not relay. For `n` entries the expected number of such pairs is `n² / 2^65`:

| Key | Pairs per epoch at `F_1 = 20` (13 M entries) | Pairs per epoch at 124 new messages a round (80 M entries) |
| --- | --- | --- |
| 32 bits | about 19,600 | about 750,000 |
| 48 bits | 0.3 | 11.5 |
| 64 bits | 4.6·10⁻⁶ | 1.75·10⁻⁴ |

At 64 bits, a collision is expected about once in 5,700 epochs in the worst case. A data message lost to one falls back to a direct broadcast. A peer cannot force a collision: a nullifier stays in the cache only once its proof of quota verifies, so matching a given 64-bit value takes about 2^64 valid proofs.

The cache holds 104 MB at `F_1 = 20`, against 332 MB in 1.6.0. It holds at most 643 MB when a node spends every share in every round, against 2.6 GB.

## Why a failed stream is not blacklisted

A Blend message has a fixed size, so the only framing violation a reader can observe is a message cut short. A peer that ends its stream on purpose, a path failure, an idle timeout, a killed process and the reader's own link failing all look alike at that point. At the end of a Transition Period every node closes its past-epoch connections at about the same moment, so a rule that blacklisted a truncated read would blacklist honest peers across the network at once.

The rule also gained nothing. A neighbor that stops mid-message delivers nothing and loses its slot at once, which is worse for it than staying silent until liveness closes the connection. A neighbor is still blacklisted for a complete message that fails a check its sender controls.

## Blacklisting closes every connection with the identity

1.6.0 closed the connection an offence arrived on and refused new ones. A connection with the same identity that was already open — from the past epoch, still in its handshake, or the other half of a mutual dial — stayed up and kept counting towards the peering degree.

## Pending handshakes, the handshake cap and liveness

A pending handshake counted towards `Φ_CC`, but nothing said whether it counted as accepted. Read the other way, five stalled inbound handshakes fill every slot, and the node ends up either above its maximum or without the `Φ_CC − 2` connections it must open itself. A pending handshake is now held, as opened or accepted, once the Neighbor Distinction Process identifies a core node. Its rounds then count towards the identity's liveness, so an identity that keeps stalling is not live once it has spent `W` connected rounds without delivering.

The handshake cap counted every handshake in progress, the node's own dials included. A handshake is not identified during its transport handshake, so unregistered peers could keep the cap full by restarting stalled TLS handshakes every `T_H`, and stop the node from dialing. The cap now counts handshakes offered to the node, one for each connection it may accept: the 3 accepted core connections of Degree rule 1 and the `Φ_CE^Max` edge connections.

1.6.0 did not say whether a pending edge handshake counts towards `Φ_CE^Max`. An edge connection is now accepted and held from the same point as a core one, once the Neighbor Distinction Process identifies it, so `T_E` runs from there and a pending edge handshake holds its slot for at most `T_E`.

Liveness is counted per identity for the epoch, so a neighbor closed as not live starts not live when it reconnects. 1.6.0 did not say when liveness is judged. Judged when a connection opens, it closes the reconnected neighbor before it can deliver, and shuts the identity out for the rest of the epoch. Judged at the end of a round, the neighbor has that round to deliver; an honest neighbor delivers about three messages a round on average, even in a quiet network.

## The receive window

The share of Admission rule 1 limits what a node verifies, not what its transport accepts. With a large receive window, a node that reads slowly buffers messages in its transport. Those messages have left the sender's queue, so the `η` deadline of rule 2 no longer reaches them. With the window bounded to `r_1` messages, a backlog stays in the sender's queue, where the deadline applies.

## Why `T_H` is a core node parameter

No other node acts on `T_H`, and no formula uses it. It only bounds how long a stalled handshake holds one of the node's own slots. Its value does not protect the node: an attacker restarts a stalled handshake every `T_H`, whatever `T_H` is. What keeps the node able to dial is that the cap counts only the handshakes offered to it.

`T_H` still counts from the start of the transport handshake. The cap counts handshakes before they are identified, so a transport handshake without a bound would hold a place in the cap indefinitely.

The reference implementation bounds the transport handshake by the QUIC handshake timeout, 5 seconds by default, and the protocol negotiation by a deadline of 2 rounds. Their sum is its `T_H`.

## Compatibility

No message format changes. `TARGET_TXS_PER_BLOCK` is a consensus constant, and the proof of quota checks `Q_C` and `Q_W`. Bedrock has no deployed network, so the change needs no migration.

## Review findings that need no change

| Finding | Why no change |
| --- | --- |
| Degree rule 3 closes every non-live connection at once | That needs `W` rounds in which no neighbor delivers anything, an outage of the network or of the node itself. Judging liveness at the end of a round keeps reconnection working afterwards. |
| A neighbor keeps its slot by replaying one message per `W` | Excluding echoes is beaten by forwarding any message from another connection once per `W`. Liveness detects dead peers, not contribution ([Relaying is enforced only by liveness](#relaying-is-enforced-only-by-liveness)). |
| A stalled handshake has no consequence | Bounded by the pending-handshake rule and per-identity liveness, above. |
| `Φ_CE^Max ≥ 2·r_E` budgets no time for teardown | A connection the node has closed holds no slot, so an edge connection frees its slot once `T_E` has elapsed. |
| A message once begun has no read deadline | A partial message is not a delivery, so liveness closes the connection after `W`. |
| Liveness restarts every epoch | `W = 30` rounds against an epoch of 648,000. |
| `Φ_CC = 3` lets peers choose three of four connections | Accepted at the bottom of the range. At `Φ_CC = 3` a node opens at least `Φ_CC − 2 = 1` of its 4 connections, so its peers choose up to three. At the specified `Φ_CC = 4` it opens at least 2 of 5. |
| Simultaneous connection | Core Network Bootstrapping step 5 specifies it. |
| A closer truncates the message in flight | A stream that ends carries no reaction. |
| The blacklist across epochs and roles | An entry is kept per identity, refuses it on any connection, and expires after `W` rounds. |
| Edge connections at an epoch change | Past-epoch connections are kept through the Transition Period, and an edge connection closes within `T_E` anyway. |
| Past-epoch peers as current neighbors | Either reading works, since a node can dial any other core node. |
| Refusing a connection or accepting and closing it | "Closed" covers both. |
| Liveness credited before the header checks | The outcome is the same: a message that fails a later check closes the connection and blacklists the neighbor. A message counts towards the share only once the nullifier check finds it novel. |
| A minimum network size | [Minimal Network Size](../blend-protocol.md#minimal-network-size) specifies it. |
| The 1.6.0 change-log row omits the removal of replacement-first, of the echo exclusion and of the edge quarantine | A change-log row states the core modification. "Replaced the per-window statistical threshold" and "Restricted blacklisting to attributable faults" cover all three. |

## What this RFC leaves open

### Relaying is enforced only by liveness

Liveness requires a neighbor to deliver one message per `W` connected rounds. A node's own messages, those it generates and those it releases as a blend node, reach each neighbor `W·F_1/N = 600/N` times per window on average. A node that forwards nothing else therefore needs to forward only a few messages per window to stay live, so relaying other nodes' messages is not enforced. The relaying motivation in Rewarding now says only what liveness enforces. An incentive for relaying is a separate change.

### Edge admission

Unregistered peers can exhaust the edge share `r_E`, and the cap on offered handshakes, by opening connections that send nothing. A per-identity measure cannot stop this, since an edge identity costs nothing. This RFC does not change edge admission.

### Bandwidth

With the verification share, bandwidth limits `F_1` before `V` does. A node receives each message from up to `Φ_CC` neighbors, and reads every copy whole before it can check the nullifier. Sending the public header ahead of the body, and fetching the body only when its nullifier is novel, would cut a node's traffic about three- to fourfold, at the cost of a round trip per hop. It changes the wire protocol, and is a separate change.

# Details

## 1. The shares count verifications

[Overview](../blend-protocol.md#maintenance), [Notation](../blend-protocol.md#notation) and [Global Parameters](../blend-protocol.md#global-parameters) make `r_1` a share of verifications:

```diff
-A core node reads at most a share of messages from each connection per round, sized to what the slowest node the protocol targets can process, sends at most the same share on each, and keeps a connection only while its neighbor delivers. ...
+A core node verifies at most a share of the novel messages from each connection per round, sized to what the slowest node the protocol targets can process, and keeps a connection only while its neighbor delivers. ...

-- $`r_1`$ denote the number of messages a node reads from a core connection in a round;
+- $`r_1`$ denote the number of novel messages a node verifies from a core connection in a round;

-- $`r_1 = 20`$ messages a node reads from a core connection per round, ... so a node at its peering degree reads two thirds of $`V`$, ...
+- $`r_1 = 20`$ novel messages a node verifies from a core connection per round, ... so a node at its peering degree verifies at most two thirds of $`V`$, ...
```

[Expected Traffic](../blend-protocol.md#expected-traffic) sizes `F_1` against the shares of the connections a node opens, draining within `η`:

```diff
-Flooding delivers each message once per neighbor, so $`F_1`$ must be below $`r_1`$; at $`r_1`$ a backlog on a connection never drains. $`F_T`$ is sized so that a backlog of one round's share drains, at $`r_1 - F_1`$ per round, within the time a message may spend at one hop, $`\Delta_{max} + \eta`$ ([Transition Period](#transition-period)): $`F_1 = r_1 \cdot (1 - 1 / (\Delta_{max} + \eta)) = 16`$. ...
+A node verifies each message once, from the first neighbor that delivers it. The shares of the $`\Phi_{CC} - 2`$ connections a node opens itself ([Connectivity Maintenance](#connectivity-maintenance)) must carry the flood, so $`F_1`$ must be below $`(\Phi_{CC} - 2) \cdot r_1`$; at that rate a backlog never drains. $`F_T`$ is sized so that a backlog of one round of these shares drains, at $`(\Phi_{CC} - 2) \cdot r_1 - F_1`$ per round, within the network absorption of one hop, $`\eta`$ ([Transition Period](#transition-period)): $`F_1 = (\Phi_{CC} - 2) \cdot r_1 \cdot (1 - 1 / \eta) = 20`$. ...

-A node reads at most $`(\Phi_{CC} + 1) \cdot r_1 + r_E = 124`$ messages in a round, which must not exceed $`V`$, and verifies the public header of novel messages only ([Relaying](#relaying)). At $`19318`$ bytes per message ([Message Formatting](message-formatting.md)) that is $`2.4`$ MB/s.
+A node verifies at most $`(\Phi_{CC} + 1) \cdot r_1 + r_E = 124`$ messages in a round, which must not exceed $`V`$. It receives each message from up to $`\Phi_{CC}`$ neighbors and forwards it to $`\Phi_{CC} - 1`$, so at $`F_1`$ and $`19318`$ bytes per message ([Message Formatting](message-formatting.md)) it receives up to $`1.5`$ MB/s and sends $`1.2`$ MB/s.
```

The `F_1` formula and `F_T` follow in [Details 2](#2-one-number-of-copies-for-every-message), and the reference load in [Details 3](#3-the-reference-load-of-the-blend-difficulty).

[Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance), Admission: a share counts novel messages, a node no longer caps what it sends, and the send deadline counts from the round a message was queued:

```diff
-The shares keep the messages a node reads in a round within what the slowest node the protocol targets can verify, $`V`$ ([Expected Traffic](#expected-traffic)).
+The shares keep the messages a node verifies in a round within what the slowest node the protocol targets can verify, $`V`$ ([Expected Traffic](#expected-traffic)).

-1. A node reads at most $`r_1`$ messages from a core connection in a round. A connection whose share is spent is not read until the next round.
-2. A node sends at most $`r_1`$ messages on a core connection in a round. A message that has waited $`\eta`$ rounds to be sent on a connection is discarded for that connection.
+1. A node verifies at most $`r_1`$ novel messages from a core connection in a round. A connection whose share is spent is not read until the next round. The receive window of a core connection holds at most $`r_1`$ messages.
+2. A message queued for a connection in round $`n`$ and not sent before round $`n + \eta`$ is discarded for that connection.
```

[Relaying](../blend-protocol.md#relaying-2), step 1.1:

```diff
-    1. If the neighbor is a core node, then the message counts towards the liveness of the connection and towards its share ([Connectivity Maintenance](#connectivity-maintenance)).
+    1. If the neighbor is a core node, then the message counts towards the liveness of the connection, and a novel message towards its share ([Connectivity Maintenance](#connectivity-maintenance)).
```

The nullifier cache takes a nullifier from the start of its verification ([Details 6](#6-the-nullifier-cache)).

## 2. One number of copies for every message

[Notation](../blend-protocol.md#notation):

```diff
-- $`R_C`$ denote a redundancy parameter for cover messages, defining the number of “replications” of the same message;
-- $`R_D`$ denote a redundancy parameter for block proposals, defining the number of “replications” of the same message;
+- $`R`$ denote the number of copies a node sends of each message it generates, besides the message itself, each encapsulated with its own keys;
```

[Global Parameters](../blend-protocol.md#global-parameters):

```diff
-- $`F_D=1/30`$, the network generates one block proposal every $`30`$ rounds on average ([Cryptarchia Protocol](cryptarchia-v1-protocol.md)).
-- $`F_T = 130/30`$, the network carries $`130`$ messages per slot of $`30`$ rounds, each carrying one transaction ([Payload Formatting](payload-formatting.md)), whatever quota backs them: $`\left(F_1 / \beta_{max} - \max(F_C \cdot (1 + R_C), F_D \cdot (1 + R_D))\right) \cdot 30 = 130`$ at $`F_1 = 16`$ ([Expected Traffic](#expected-traffic)).
-- $`R_C=0`$ and $`R_D=1`$: a cover message is not replicated, and a block proposal is replicated once. A transaction is not replicated.
+- $`F_D=1/30`$, the network generates one block proposal every $`30`$ rounds on average ([Cryptarchia Protocol](cryptarchia-v1-protocol.md)). $`F_D \le F_C`$: a block proposal replaces a cover message ([Releasing](#releasing)), so [Expected Traffic](#expected-traffic) counts it within $`F_C`$.
+- $`F_T = 70/30`$, the network carries $`70`$ transactions during $`30`$ rounds, one per message ([Payload Formatting](payload-formatting.md)), in $`(1 + R) \cdot 70 = 140`$ messages with their copies, whatever quota backs them: $`\left(F_1 / ((1 + R) \cdot \beta_{max}) - F_C\right) \cdot 30 = 70`$ at $`F_1 = 20`$ ([Expected Traffic](#expected-traffic)).
+- $`R=1`$: a node sends one copy of every message it generates, whatever its type. One value serves every type, since a different number of copies would reveal a message's type.
```

[Expected Traffic](../blend-protocol.md#expected-traffic):

```diff
 $$
-F_1 = \left( \max\left(F_C \cdot (1 + R_C),\ F_D \cdot (1 + R_D)\right) + F_T \right) \cdot \beta_{max} = 16.0
+F_1 = \left( F_C + F_T \right) \cdot (1 + R) \cdot \beta_{max} = 20.0
 $$
```

[Core Quota](../blend-protocol.md#core-quota) and [Leadership Quota](../blend-protocol.md#leadership-quota) use `R` in place of `R_C` and `R_D`. [Proof of Work Quota](../blend-protocol.md#proof-of-work-quota) pays for the copy:

```diff
-Q^{n}_W = y \cdot Q_W, \qquad Q_W = \beta_{max}
+Q^{n}_W = y \cdot Q_W, \qquad Q_W = (1 + R) \cdot \beta_{max}

-$`Q_W = \beta_{max}`$: one solution pays for exactly one message, since a message consumes one blending operation per encapsulation.
+$`Q_W = (1 + R) \cdot \beta_{max}`$: one solution pays for exactly one message and its copies, since each consumes one blending operation per encapsulation.
```

## 3. The reference load of the Blend difficulty

[Proof of Work](../proof-of-work.md#blend-difficulty) follows `F_T / F_D`:

```diff
-TARGET_TXS_PER_BLOCK: uint64 = 130              # Reference transactions per block, F_T / F_D
+TARGET_TXS_PER_BLOCK: uint64 = 70               # Reference transactions per block, F_T / F_D
```

## 4. Blacklisting

[Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance), Blacklist:

```diff
-A failure of the authenticated stream is a violation of the framing of the stream.
-
-1. A connection with a core node whose authenticated stream fails, or that carries a message with a malformed header, an invalid signature, or an invalid proof of quota, is closed and its neighbor is added to the **blacklist**. A message discarded as a duplicate carries no reaction.
-2. A blacklisted identity is refused on incoming and on outgoing connections. An entry expires after $`W`$ rounds.
-3. The blacklist holds at most $`2 \cdot \Phi_{CC}`$ entries, and the oldest is discarded when it is full.
+1. A connection with a core node that carries a message with a malformed header, an invalid signature, or an invalid proof of quota is closed and its neighbor is added to the **blacklist**. A message discarded as a duplicate carries no reaction.
+2. A blacklisted identity's connections are closed, and it is refused on incoming and on outgoing connections. An entry expires after $`W`$ rounds.
+3. A connection whose stream ends or fails is closed. Its neighbor is not blacklisted.
```

## 5. Pending handshakes, the handshake cap and liveness

[Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance), Degree:

```diff
-3. A connection that is not live is closed.
-4. A connection whose handshake is in progress counts towards $`\Phi_{CC}`$ once the [Neighbor Distinction Process](#neighbor-distinction-process) has identified the neighbor as a core node, and its peer is a current neighbor for rule 2. A handshake that has not completed within $`T_H`$ is abandoned and its slot released. At most $`\Phi_{CC} + 1 + \Phi_{CE}^{Max}`$ handshakes are in progress at once, and one offered above that is closed.
+3. A connection that is not live at the end of a round is closed.
+4. A connection whose handshake is in progress is held, as one the node opened or accepted, once the [Neighbor Distinction Process](#neighbor-distinction-process) has identified the neighbor as a core node, and its peer is a current neighbor for rule 2. A handshake that has not completed within $`T_H`$ is abandoned and its slot released. At most $`3 + \Phi_{CE}^{Max}`$ handshakes offered to the node are in progress at once, one for each connection it may accept, and one offered above that is closed.
```

[Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance), Edge Nodes:

```diff
-1. A core node holds at most $`\Phi_{CE}^{Max}`$ connections with edge nodes at once, and accepts at most $`r_E`$ of them in a round. A connection offered above either is closed.
+1. A core node holds at most $`\Phi_{CE}^{Max}`$ connections with edge nodes at once, and accepts at most $`r_E`$ of them in a round. A connection is accepted and held once the [Neighbor Distinction Process](#neighbor-distinction-process) has identified the peer as an edge node, whether or not its handshake has completed. A connection offered above either is closed.
```

## 6. The nullifier cache

[Relaying](../blend-protocol.md#relaying-2) in Details keeps the retention of step 1.4 and changes what is stored, and from when:

```diff
-The node must cache the PoQ nullifiers ($`\nu_i`$) for every message it relays for a duration of a single epoch plus the [Transition Period](#transition-period) (TP). Then the node can clear the cache.  That means that the size of the cache must be at least:
+The nullifier cache holds the $`64`$ least significant bits of the PoQ nullifier ($`\nu_i`$) of every message the node relays. A nullifier is in the cache when these bits are. A nullifier enters the cache when the node starts to verify its message, and leaves it if the verification fails. A copy that arrives during the verification is checked against the cache again once the verification ends. At the rate of [Expected Traffic](#expected-traffic) the cache holds:

 $$
-\begin{aligned}
-(E + T)\cdot \left( \max\left(F_C \cdot (1+R_C),\ F_D \cdot (1+R_D)\right) + F_T \right) \cdot \beta_{max} \cdot |\nu_i|
-\end{aligned}
+(E + T) \cdot F_1 \cdot 8 = (648000 + 30) \cdot 20 \cdot 8 = 103684800 \approx 104\,\mathrm{MB}
 $$

-At the rates above:
-
-$$
-\begin{aligned}
-(648000 + 30) \cdot \left(1 + \dfrac{130}{30}\right) \cdot 3 \cdot 32 = 331791360 \approx 332\,\mathrm{MB}
-\end{aligned}
-$$
+It holds at most $`(E + T) \cdot ((\Phi_{CC} + 1) \cdot r_1 + r_E) \cdot 8 \approx 643`$ MB, when the node spends every share in every round. Two nullifiers that share these bits make the later message a duplicate. At that size the expected number of such pairs, the square of the entries over $`2^{65}`$, is below $`2 \cdot 10^{-4}`$ per epoch.
```

## 7. The receive window

[Connectivity Maintenance](../blend-protocol.md#connectivity-maintenance), Admission rule 1 ends with the bound on the receive window. Its diff is in [Details 1](#1-the-shares-count-verifications).

## 8. The handshake time

`T_H` moves from [Global Parameters](../blend-protocol.md#global-parameters) to [Core Node Parameters](../blend-protocol.md#core-node-parameters):

```diff
-- $`T_H=2`$ rounds, the time a core node handshake is given to complete, which covers the round trips of the transport handshake and of the [Neighbor Distinction Process](#neighbor-distinction-process).
+- $`T_H`$ denotes the time a core node gives a handshake to complete, from the start of its transport handshake. $`T_H`$ must exceed the round trips of the transport handshake and of the protocol negotiation ([Connection Details](#connection-details)), or honest handshakes are abandoned.
```

The Neighbor Distinction Process reads the peer id the transport handshake already carries, so it adds no round trip.

## Chores

- Edge rule 3 drops "has its connection closed", which Relaying step 1.2 already requires.
- The relaying motivation in Rewarding says a node must deliver messages to its neighbors, which is what liveness enforces.
- The 1.6.0 change-log row says `Φ_CC − 2` of the connections are opened by the node, not two.
- The 1.4.0, 1.5.0 and 1.6.0 change-log rows carry their merge dates, so the dates follow the versions.
- Edge Network bootstrapping numbers its third sub-step 3, not 4, and "until it is sends" reads "until it sends".
- `F_T` is stated during 30 rounds, not per slot of 30 rounds, since a slot lasts one round.

# Implementation

- [ ] Count only novel messages towards a core connection's share, and stop reading the connection once its share for the round is spent. Remove the per-round cap on what a node sends on a connection.
- [ ] Discard a message queued for a core connection in round `n` that is not sent before round `n + η`.
- [ ] Send every generated message, whether a cover message, a block proposal or a transaction, with `R = 1` copy, each encapsulated with its own keys.
- [ ] Derive `Q_C`, `Q_L` and `Q_W` with `R = 1`: `Q_C` doubles, `Q_L` stays 6, and `Q_W` becomes 6.
- [ ] Set `TARGET_TXS_PER_BLOCK` to 70.
- [ ] Close a connection whose stream ends or fails, without blacklisting its neighbor.
- [ ] On blacklisting an identity, close every connection held with it, past-epoch and pending ones included; remove the blacklist size cap.
- [ ] Hold a pending handshake as an opened or accepted connection once the Neighbor Distinction Process identifies a core node, and count its rounds towards liveness.
- [ ] Count a pending edge connection towards `Φ_CE^Max` and `r_E` once the Neighbor Distinction Process identifies it, and run `T_E` from then.
- [ ] Cap the handshakes offered to the node at `3 + Φ_CE^Max`, leaving the node's own dials out of the count.
- [ ] Judge liveness, and close connections that are not live, at the end of each round.
- [ ] Limit the receive window of each core connection to `r_1` messages.
- [ ] Key the nullifier cache by the 64 least significant bits of each nullifier. Add a nullifier when its verification starts, remove it if the verification fails, and check a copy that arrived meanwhile again once the verification ends.
- [ ] Bound each handshake by the node's `T_H`, counted from the start of its transport handshake.
- [ ] Add tests for the verification share, copies arriving during a verification, truncated streams, blacklist scope, stalled handshakes, reconnection after a liveness closure, the send deadline, and the copies of each message type.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.7.0 |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.1.1 |
