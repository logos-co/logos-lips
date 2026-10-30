# [RFC] Blend: Readmit a not-live neighbor after W rounds

**Motivation and proposal:** [PR #500](https://github.com/logos-co/logos-lips/pull/500)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-23 |
| v2 | Merged master, which added Blend Protocol 1.6.2. Re-dated the 1.8.0 revision. | 2026-10-27 |
| v3 | Merged the amended 1.7.0 revision, which names the constant `90` in `W` as `M_W`, and added the refusal to what a larger `M_W` lengthens. Re-dated the 1.8.0 revision. | 2026-10-29 |
| v4 | Merged master, which added Blend Protocol 1.7.0. Re-dated the 1.8.0 revision. | 2026-10-30 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the refusal](#1-a-neighbor-closed-as-not-live-is-refused-for-w-rounds) in Connectivity Maintenance of the [Blend Protocol](#affected-specifications). Check that a neighbor that disconnects itself still resumes its count, and weigh what the refusal gives up against a silent neighbor ([Discussion](#what-the-epoch-long-shutout-protected)).

# Discussion

## What the epoch-long shutout protected

Counting liveness per identity for the epoch stopped a neighbor that delivers nothing from renewing its grace by reconnecting. This still holds for a neighbor that disconnects itself, because its count resumes. A neighbor closed as not live now gets a fresh grace after `W` rounds of refusal. A silent identity can therefore hold a connection slot for at most `W` of every `2·W` rounds.

This gives up little. Duplicates count as deliveries, so a neighbor can already hold a slot for as long as it likes by replaying one message per `W`. The epoch-long shutout only stopped a neighbor unwilling to send one message per `W`. The defense against eclipse is unchanged: at least `Φ_CC − 2` live connections are ones the node opened, to nodes drawn at random.

The refusal reuses `W`, as the blacklist expiry does, so no parameter is added. A node redials a truly silent neighbor at most once every `2·W` rounds, and only when the draw picks it again.

## What a false reading costs

A node forwards each message to every neighbor except the one it received it from. A slow node that receives nearly every message first from one fast neighbor therefore forwards little back to that neighbor. If it forwards a tenth of the cover messages, the fast neighbor reads it as not live about every 7.5 hours at the reference parameters, where `W` is 30 rounds and a core connection carries 3 cover messages a round. With the epoch-long shutout, each reading costs the slow node that neighbor for the rest of the epoch. With the refusal, it costs `W` rounds, 30 seconds at the reference parameters. The figures assume deliveries that arrive at random, and how small a slow node's share gets on a real network is an open question.

## Alternatives

- **Skip for the epoch.** Skipping not-live identities when dialing and accepting, for the rest of the epoch, stops the reconnection churn. A node that has read every peer it can reach as not live then has nobody left to dial until the epoch ends.
- **Per-connection counting.** A neighbor that delivers nothing renews its grace with every reconnection, with no wait.

## Compatibility

The change is local to each node: no message, wire format or consensus rule changes, and nodes following 1.7.0 and 1.8.0 interoperate. Bedrock has no deployed network, so the change needs no migration.

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

The refusal lasts `W` rounds, so in Global Parameters a larger `M_W` lengthens it too:

```diff
 M_W = 90 messages. With a smaller M_W, a node more often reads an honest neighbor as not
 live and closes its connection. With a larger one, a neighbor that delivers nothing
-holds a connection slot for longer, and a blacklist entry lasts longer.
+holds a connection slot for longer, a neighbor closed as not live is refused for longer,
+and a blacklist entry lasts longer.
```

# Implementation

- [ ] When `close_unhealthy_connections` (`blend/network/src/core/with_core/behaviour/mod.rs`) closes a connection as not live, clear that identity's observation in `PeerLivenessMap` and refuse the identity for `W` rounds. Keep the refusal apart from the blacklist: it takes no blacklist entry and is not reported as a blacklisting.
- [ ] Refuse an identity under that refusal on inbound and outbound connections, and when its handshake completes, wherever `handle_established_inbound_connection`, `handle_established_outbound_connection` and `handle_negotiated_connection` refuse a blacklisted one.
- [ ] Exclude refused identities from the draw in `dial_random_peers_except` (`services/blend/src/core/backends/libp2p/swarm.rs`).
- [ ] Add tests: a neighbor closed as not live is refused for `W` rounds and then settles afresh; a neighbor that disconnects itself still resumes its count (`reconnecting_does_not_earn_a_fresh_window`); dialing skips refused identities.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.8.0 |
