# [RFC] P2P Network: Remove unreachable peers from the routing table

**Motivation and proposal:** [PR #505](https://github.com/logos-co/logos-lips/pull/505)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-26 |
| v2 | A failed attempt counts only if every address in the routing table fails, and the failures must span at least an hour, so that other peers and short outages cannot make a node remove an honest peer | 2026-10-26 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the removal rule](#1-unreachable-peers-are-removed) in [P2P Network](#affected-specifications). Check which attempts count as failed, that the failures must span at least an hour, and the two exceptions: attempts made while the node has no connection, and bootstrap nodes.

# Discussion

## Why Kademlia does not remove these peers itself

libp2p's Kademlia removes a failed address from a peer only while the peer has another one. It keeps the last address, so that a short loss of connectivity does not flush the routing table. A peer then leaves the table only when its bucket is full, it is the least recently connected peer of the bucket, and another peer is waiting for its place.

## Why only the routing table's addresses count

A dial to a peer also tries the addresses that other peers sent for it in answer to the node's ongoing Kademlia queries. libp2p tries up to eight addresses at once, and the first handshake to complete ends the dial. If that handshake is with another peer, the dial fails. A peer that answers the node's queries can therefore list honest peers with the address of a node that answers quickly, such as its own, and make the node's dials to them fail. If those dials counted, any peer the node queries could make it remove honest peers.

In the reference implementation, the routing table holds only the addresses that a peer announced itself through Identify, the addresses at which the node connected to it, and the configured addresses of the bootstrap nodes. Another peer can make the node fail at all of them only by making the peer unreachable.

## Why the failures must span an hour

The node attempts a connection only when something needs the peer. While it downloads blocks, every request can pick the peer as a discovered peer. Each attempt at an unreachable peer waits out the 5-second QUIC handshake timeout, so three attempts can fail within about 15 seconds. Without a minimum duration, every node that needed a peer while it restarted would remove it, and an attacker could do the same by making the peer unreachable for 15 seconds. A removed peer returns only when one of the node's Kademlia queries leads it to the peer again, or when the peer connects to the node.

An hour is longer than a restart or a short outage. A peer that has left the network is removed at the first failed attempt an hour or more after the first one.

## Why attempts made without any connection do not count

When the node's own network fails, every attempt fails, whatever the peer. The hour keeps a short outage from removing peers, but an outage of more than an hour would empty the routing table, which is what Kademlia keeps the last address to avoid. The node cannot tell its own outage from a peer's, but it can see that it has no connection at all.

## Why bootstrap nodes are kept

Bootstrap nodes are the entry points an operator configures, as defined in [P2P Network Bootstrapping](../p2p-network-bootstrapping.md). A node that has lost its other peers rejoins the network through them.

## What the rule does not defend against

An attacker on the node's network path, such as its internet provider, can block the node's connections to an honest peer for an hour and make the node remove it. Such an attacker can keep the node from that peer for as long as it blocks it, with or without this rule. The rule makes the effect outlast the blocking, until a Kademlia query leads the node to the peer again or the peer connects to the node. The attempts it blocks count as long as the node keeps any connection, and the attacker can leave one of its own open. The bootstrap nodes stay in the table, so the node can rejoin the network through them once the blocking ends.

# Details

## 1. Unreachable peers are removed

[Peer Discovery](../../draft/p2p-network.md#peer-discovery) gains the rule after the description of Kademlia and Identify:

```diff
 Complementing this, the Identify protocol supports the exchange of peer information, including details about the protocols each peer supports, thereby enhancing interoperability and network coordination.
+
+A node removes a peer from its Kademlia routing table when at least three attempts to connect to it have failed since the node was last connected to it, and the latest failed at least one hour after the first. Implementers can choose a different number of attempts and a different duration.
+
+- An attempt fails if the node tries every address that its routing table holds for the peer and cannot connect to the peer at any of them.
+- A failed attempt does not count while the node has no connection to any peer.
+- The node does not remove a bootstrap node, as defined in [P2P Network Bootstrapping](../raw/p2p-network-bootstrapping.md).
```

- The P2P Network revision is 1.1.0.

# Implementation

- [ ] Count each peer's failed connection attempts, whatever started them. Today `retry_connect` counts only the dials that `connect()` started, and a failure of any other dial removes an address only on `WrongPeerId` (`services/network/src/backends/libp2p/swarm/mod.rs`).
- [ ] Count a dial only if its `DialError::Transport` errors cover every address that the routing table holds for the peer. A dial that ends with `WrongPeerId` or `LocalPeerId` at an address a Kademlia query reported, and an aborted or denied dial, do not count.
- [ ] Reset the count when a connection to the peer is established, and drop it when the peer leaves the routing table. Once at least three failures are counted and the latest is at least an hour after the first, remove the peer from the Kademlia routing table and drop what it advertised (`prune_peer_advertised_protocols`).
- [ ] Do not count a failure while the swarm has no connected peer, and never remove a peer listed in `initial_peers`. Today `retry_connect` removes a bootstrap node's address after `MAX_RETRY` failed retries.
- [ ] Add tests: three failed attempts over an hour remove a discovered peer; three within the hour do not; a connection in between resets the count; a dial that another peer's answer ends at an address a query reported does not count; failures while the node has no connection do not count; an initial peer is kept.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [P2P Network](../../draft/p2p-network.md) | Modified | Revision 1.1.0 |
