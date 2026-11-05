# [RFC] P2P Network: Remove unreachable peers from the routing table

**Motivation and proposal:** [PR #505](https://github.com/logos-co/logos-lips/pull/505)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-26 |
| v2 | A failed attempt counts only if every address in the routing table fails, and the failures must span at least an hour, so that other peers and short outages cannot make a node remove an honest peer | 2026-10-26 |
| v3 | A node keeps a peer's only remaining address even if a different peer answers at it, so that one redirected connection cannot remove an honest peer | 2026-10-26 |
| v4 | Explain why the rule needs three failed attempts as well as the hour | 2026-10-29 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the removal rule](#1-unreachable-peers-are-removed) in [P2P Network](#affected-specifications). Check which attempts count as failed, that the failures must span at least an hour, and the three exceptions: attempts made while the node has no connection, a different peer answering at a peer's only remaining address, and bootstrap nodes.

# Discussion

## Why Kademlia does not remove these peers itself

libp2p's Kademlia removes a failed address from a peer only while the peer has another one. It keeps a peer's only remaining address, so that a short loss of connectivity does not flush the routing table. A peer then leaves the table only when its bucket is full, it is the least recently connected peer of the bucket, and another peer is waiting for its place.

## Why only the routing table's addresses count

A dial to a peer also tries the addresses that other peers sent for it in answer to the node's ongoing Kademlia queries. libp2p tries up to eight addresses at once, and the first handshake to complete ends the dial. If that handshake is with a different peer, the dial fails. A peer that answers the node's queries can therefore list honest peers with the address of a node that answers quickly, such as its own, and make the node's dials to them fail. If those dials counted, any peer the node queries could make it remove honest peers.

In the reference implementation, the routing table holds only the addresses that a peer announced itself through Identify, the addresses at which the node connected to it, and the configured addresses of the bootstrap nodes. Another peer can make the node fail at all of them only by making the peer unreachable.

## Why the failures must span an hour

The node attempts a connection only when something needs the peer. While it downloads blocks, every request can pick the peer as a discovered peer. Each attempt at an unreachable peer waits out the 5-second QUIC handshake timeout, so three attempts can fail within about 15 seconds. Without a minimum duration, every node that needed a peer while it restarted would remove it, and an attacker could do the same by making the peer unreachable for 15 seconds. A removed peer returns only when one of the node's Kademlia queries leads it to the peer again, or when the peer connects to the node.

An hour is longer than a restart or a short outage. A peer that has left the network is removed at the first failed attempt an hour or more after the first one.

## Why three attempts

A node that keeps picking a peer for block downloads reaches three failed attempts within seconds, so for that peer only the hour decides. A peer the node needs less often may be tried only twice in an hour. It stays until a third attempt also fails, so that two isolated failures do not remove a peer that was reachable in between.

## Why a redirected connection does not remove a peer

In the reference implementation, a node removes an address at once when a different peer answers at it, and Kademlia removes a peer together with its only remaining address. An attacker who redirects the node's packets for a peer's only remaining address to its own libp2p node could therefore remove the peer with a single connection. Its node completes the handshake under its own identity. It cannot pose as the peer without the peer's key, and it does not need to. libp2p's QUIC transport accepts any identity during the handshake, and the swarm compares it with the expected one only afterwards. Blocking the packets instead only makes attempts fail, and the hour decides.

Redirecting takes someone who can intercept and rewrite the traffic between the node and the address:

- the node's internet or hosting provider;
- a router or Wi-Fi access point on the path;
- someone on the node's local network;
- someone on the peer's side, such as its hosting provider or whoever hijacks the route to its address range. Every node that dials the peer meanwhile would remove it.

If the address is a DNS name, whoever controls the node's DNS answers can redirect it as well. [P2P Network Bootstrapping](../p2p-network-bootstrapping.md) allows bootstrap nodes to be configured that way.

Keeping the only remaining address turns such an answer into an ordinary failed attempt. A node still removes an address at which a different peer answers while the peer has another one. The first handshake to complete ends a dial, so that address could otherwise end every dial to the peer.

## What happens when an operator changes a node's key

A node whose operator changes its key at the same address stays reachable under the new key. The routing table is keyed by peer ID, so the new key gets an entry of its own, and the entry of the old key does not block or delay it. Other nodes learn the new key as they learn any peer. The node connects to its bootstrap nodes and to the peers its queries reach. Each of them learns the new key and the node's addresses through Identify, and Kademlia answers spread them from there.

A dial to the old key reaches the node but fails, because the node answers under the new key. Today a node removes the old entry as soon as such a dial reaches its only remaining address. With this rule, it keeps the entry for at least an hour after the first such dial, which costs:

- A place in each block download request that picks the entry. It delays nothing, since a request goes to all selected peers at once.
- A QUIC handshake on the node for every such dial, which the dialing node then drops. A node that downloads blocks can dial the entry on every request. Other nodes dial it when a Kademlia query or an occasional download picks it.

A configured bootstrap address carries the peer ID. A node configured with the old key therefore cannot reach the node through that address until its operator updates it, as today. Since bootstrap nodes are never removed, such a node keeps the entry, and every attempt at it fails.

## Why attempts made without any connection do not count

When the node's own network fails, every attempt fails, whatever the peer. The hour keeps a short outage from removing peers, but an outage of more than an hour would empty the routing table, which is what Kademlia keeps a peer's only remaining address to avoid. The node cannot tell its own outage from a peer's, but it can see that it has no connection at all.

## Why bootstrap nodes are kept

Bootstrap nodes are the entry points an operator configures, as defined in [P2P Network Bootstrapping](../p2p-network-bootstrapping.md). A node that has lost its other peers rejoins the network through them.

## What the rule does not defend against

An attacker on the node's network path, such as its internet provider, can block or redirect the node's connections to an honest peer for an hour and make the node remove it. Such an attacker can keep the node from that peer for as long as it blocks it, with or without this rule. The rule makes the effect outlast the blocking, until a Kademlia query leads the node to the peer again or the peer connects to the node. The attempts it blocks count as long as the node keeps any connection, and the attacker can leave one of its own open. The bootstrap nodes stay in the table, so the node can rejoin the network through them once the blocking ends.

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
+- The node keeps a peer's only remaining address even if a different peer answers at it.
+- The node does not remove a bootstrap node, as defined in [P2P Network Bootstrapping](../raw/p2p-network-bootstrapping.md).
```

- The P2P Network revision is 1.1.0.

# Implementation

- [ ] Count each peer's failed connection attempts, whatever started them. Today `retry_connect` counts only the dials that `connect()` started, and a failure of any other dial removes an address only on `WrongPeerId` (`services/network/src/backends/libp2p/swarm/mod.rs`).
- [ ] Count a dial only if it tried every address that the routing table holds for the peer and reached the peer at none of them. That is a `DialError::Transport` whose errors cover them all, or a `WrongPeerId` at the peer's only remaining address. A dial that ends with `WrongPeerId` or `LocalPeerId` at an address a Kademlia query reported, and an aborted or denied dial, do not count.
- [ ] On `WrongPeerId`, remove the address only while the peer has another one in the routing table. Today `remove_kademlia_address_for_dial` removes it in every case, and Kademlia then removes a peer together with its only remaining address.
- [ ] Reset the count when a connection to the peer is established, and drop it when the peer leaves the routing table. Once at least three failures are counted and the latest is at least an hour after the first, remove the peer from the Kademlia routing table and drop what it advertised (`prune_peer_advertised_protocols`).
- [ ] Do not count a failure while the swarm has no connected peer, and never remove a peer listed in `initial_peers`. Today `retry_connect` removes a bootstrap node's address after `MAX_RETRY` failed retries.
- [ ] Add tests: three failed attempts over an hour remove a discovered peer; three within the hour do not; a connection in between resets the count; a dial that a different peer's answer ends at an address a query reported does not count; a different peer answering at a peer's only remaining address counts as a failed attempt and leaves the address in place; failures while the node has no connection do not count; an initial peer is kept.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [P2P Network](../../draft/p2p-network.md) | Modified | Revision 1.1.0 |
