# [RFC] Blend: Size the observation window by cover traffic and readmit not-live neighbors

**Motivation and proposal:** [PR #499](https://github.com/logos-co/logos-lips/pull/499)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-23 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then the two changes to Connectivity Maintenance in the [Blend Protocol](#affected-specifications): [the refusal of a not-live neighbor](#1-a-neighbor-closed-as-not-live-is-refused-for-w-rounds) first, then [the size of `W`](#2-w-is-sized-by-cover-traffic). Check that a neighbor that disconnects itself still resumes its count, and weigh what the refusal gives up against a silent neighbor ([Discussion](#what-the-epoch-long-shutout-protected)).

# Discussion

## The size of the window

The liveness test works only if an honest neighbor almost never goes `W` connected rounds without delivering. With no transactions, a core connection carries `F_C·(1 + R_C)·β_C` messages a round, one per blending operation of each cover message. Block proposals take the place of cover messages, and transactions add to them. A neighbor forwards each message to every neighbor except the one it received it from, so it delivers roughly half to three quarters of them to the node.

For deliveries arriving at random at a rate `λ` per round, the mean time before a gap of `W` rounds is `(e^(λW) − 1)/λ` rounds. For a neighbor that forwards half of the cover messages:

| Deployment | Cover messages per round | `W`, 1.6.1 → 1.7.0 | Deliveries expected per window | Mean time to a false reading per connection |
| --- | --- | --- | --- | --- |
| Reference | 3 | 30 → 30 | 45 → 45 | over 10⁵ years in both |
| Testnet (`F_C = 1`, one layer) | 1 | 10 → 90 | 5 → 45 | 4.9 min → over 10⁵ years |
| Testnet, if a third of its members emit nothing | 0.67 | 10 → 90 | 3.3 → 30 | 1.4 min → over 10⁵ years |

The constant `90` keeps `W` at 30 rounds at the reference parameters, so neither the liveness test nor the blacklist expiry changes there. A deployment with less cover traffic gets a proportionally longer window, and the same expected number of deliveries in it.

The model is crude, and how far it holds is an open question. Arrivals are not independent, and the share of messages a neighbor forwards depends on the topology and on latency. A slow node that receives nearly every message first from one fast neighbor forwards little back to that neighbor. If it forwards a tenth of the cover messages, the fast neighbor reads it as not live about every 7.5 hours at the reference parameters, and about every 22.5 hours on the testnet with the new `W`. The refusal below bounds what such a reading costs.

## What the epoch-long shutout protected

Counting liveness per identity for the epoch stopped a neighbor that delivers nothing from renewing its grace by reconnecting. This still holds for a neighbor that disconnects itself, because its count resumes. A neighbor closed as not live now gets a fresh grace after `W` rounds of refusal. A silent identity can therefore hold a connection slot for at most `W` of every `2·W` rounds.

This gives up little. Under 1.6.0, a neighbor already holds a slot for as long as it likes by replaying one duplicate per `W`. The epoch-long shutout only stopped a neighbor unwilling to send one message per `W`. The defense against eclipse is unchanged: at least `Φ_CC − 2` live connections are ones the node opened, to nodes drawn at random.

The refusal reuses `W`, as the blacklist expiry does, so no parameter is added. A node redials a truly silent neighbor at most once every `2·W` rounds, and only when the draw picks it again.

## Alternatives

- **Skip for the epoch.** Skipping not-live identities when dialing and accepting, for the rest of the epoch, stops the reconnection churn. A node that has read every peer it can reach as not live then has nobody left to dial until the epoch ends.
- **A larger `Δ_max` on the testnet.** `W` becomes 30 rounds there, and a neighbor that forwards half of the cover messages delivers 15 per window. `W` still does not follow the traffic, so a deployment with fewer layers or less cover traffic fails the same way.
- **Per-connection counting.** A neighbor that delivers nothing renews its grace with every reconnection, with no wait.

## Compatibility

The change is local to each node: no message, wire format or consensus rule changes, and nodes following 1.6.1 and 1.7.0 interoperate. Where cover traffic is lower than at the reference parameters, `W` grows, and with it the blacklist expiry and the time a dead neighbor holds a slot: 90 rounds on the testnet. Bedrock has no deployed network, so the change needs no migration.

# Details

## 1. A neighbor closed as not live is refused for `W` rounds

In Connectivity Maintenance, the liveness count of a neighbor restarts when the node closes its connection for not being live, and the neighbor is refused for `W` rounds instead of for the rest of the epoch:

```diff
 **Liveness**

 1. A connection with a core node is live when the neighbor has delivered a message,
    duplicate or not, within its last W connected rounds, or has been connected for
    fewer than W rounds in total.
 2. Connected rounds and deliveries are counted per identity, for the epoch, over every
    connection the node has held with it.
+   The count restarts when the node closes a connection with the identity for not
+   being live.
 3. A neighbor whose connection is not live is not blacklisted.
+   It is refused on incoming and on outgoing connections for W rounds after the node
+   closes the connection.
```

A node now refuses blacklisted identities and identities under this refusal. The draw of the nodes it opens excludes both, in Degree rule 2 and in step 3.1 of Core Network bootstrapping:

```diff
 2. It draws the nodes it opens uniformly at random and without replacement from the set
-   returned by the SDP protocol, excluding itself, blacklisted identities and its current
-   neighbors.
+   returned by the SDP protocol, excluding itself, the identities it refuses and its
+   current neighbors.
```

## 2. `W` is sized by cover traffic

In Global Parameters, `W` no longer depends on `Δ_max`. It keeps both of its uses, the liveness window and the blacklist expiry:

```diff
-W = 10·Δ_max = 30, the observation window is 30 rounds.
+W = ⌈90 / (F_C·(1 + R_C)·β_C)⌉ = 30 rounds, the observation window: the rounds in which
+a core connection carries 90 messages from cover traffic alone. With fewer messages in
+the window, a node more often reads an honest neighbor as not live and closes its
+connection.
```

# Implementation

- [ ] Compute the observation window as `⌈90 / (message_frequency_per_round · num_blend_layers)⌉` in `rounds_per_observation_window` (`nodes/node/binary/src/config/blend/deployment.rs`), in place of `10 · maximum_release_delay_in_rounds`. No deployment replicates cover messages, so `R_C = 0`. The testnet window becomes 90 rounds.
- [ ] When `close_unhealthy_connections` (`blend/network/src/core/with_core/behaviour/mod.rs`) closes a connection as not live, clear that identity's observation in `PeerLivenessMap` and refuse the identity for `W` rounds. Keep the refusal apart from the blacklist: it takes no blacklist entry and is not reported as a blacklisting.
- [ ] Refuse an identity under that refusal on inbound and outbound connections, and when its handshake completes, wherever `handle_established_inbound_connection`, `handle_established_outbound_connection` and `handle_negotiated_connection` refuse a blacklisted one.
- [ ] Exclude refused identities from the draw in `dial_random_peers_except` (`services/blend/src/core/backends/libp2p/swarm.rs`).
- [ ] Add tests: a neighbor closed as not live is refused for `W` rounds and then settles afresh; a neighbor that disconnects itself still resumes its count (`reconnecting_does_not_earn_a_fresh_window`); dialing skips refused identities; the window is 30 rounds at the reference settings and 90 at the testnet's.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.7.0 |
