# [RFC] P2P Network: Remove unreachable peers from the routing table

**Motivation and proposal:** [PR #505](https://github.com/logos-co/logos-lips/pull/505)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-26 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the removal rule](#1-unreachable-peers-are-removed) in [P2P Network](#affected-specifications). Check its two exceptions: attempts made while the node has no connection, and bootstrap nodes.

# Discussion

## Why Kademlia does not remove these peers itself

libp2p's Kademlia removes a failed address from a peer only while the peer has another one. It keeps the last address, so that a short loss of connectivity does not flush the routing table. A peer then leaves the table only when its bucket is full, it is the least recently connected peer of the bucket, and another peer is waiting for its place.

## Why attempts made without any connection do not count

When the node's own network fails, every attempt fails, whatever the peer. Counting those attempts would empty the routing table during the outage, which is what Kademlia keeps the last address to avoid. The node cannot tell its own outage from a peer's, but it can see that it has no connection at all.

## Why bootstrap nodes are kept

Bootstrap nodes are the entry points an operator configures, as defined in [P2P Network Bootstrapping](../p2p-network-bootstrapping.md). A node that has lost its other peers rejoins the network through them.

# Details

## 1. Unreachable peers are removed

[Peer Discovery](../../draft/p2p-network.md#peer-discovery) gains the rule after the description of Kademlia and Identify:

```diff
 Complementing this, the Identify protocol supports the exchange of peer information, including details about the protocols each peer supports, thereby enhancing interoperability and network coordination.
+
+A node removes a peer from its Kademlia routing table after three consecutive failed attempts to connect to it. A failed attempt does not count while the node has no connection to any peer. The node does not remove a bootstrap node, as defined in [P2P Network Bootstrapping](../raw/p2p-network-bootstrapping.md). Implementers can choose a different number of attempts.
```

- The P2P Network revision is 1.1.0.

# Implementation

- [ ] Count each peer's failed connection attempts, whatever started them. Today `retry_connect` counts only the dials that `connect()` started, and a failure of any other dial removes an address only on `WrongPeerId` (`services/network/src/backends/libp2p/swarm/mod.rs`).
- [ ] After three failures in a row, remove the peer from the Kademlia routing table and drop what it advertised (`prune_peer_advertised_protocols`). Reset the count when a connection to the peer is established.
- [ ] Do not count a failure while the swarm has no connected peer, and never remove a peer listed in `initial_peers`.
- [ ] Add tests: three failed attempts remove a discovered peer; a connection in between resets the count; failures while the node has no connection do not count; an initial peer is kept.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [P2P Network](../../draft/p2p-network.md) | Modified | Revision 1.1.0 |
