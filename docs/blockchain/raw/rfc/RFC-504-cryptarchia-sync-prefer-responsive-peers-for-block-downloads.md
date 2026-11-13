# [RFC] Cryptarchia-Sync: Prefer responsive peers for block downloads

**Motivation and proposal:** [PR #504](https://github.com/logos-co/logos-lips/pull/504)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-26 |
| v2 | An unresponsive peer is chosen after every other peer instead of being left out, and an IBD peer is never unresponsive, so that an attacker who drops some of a node's requests cannot keep honest peers out of its downloads | 2026-10-26 |
| v3 | A peer also times out when the node cannot connect to it, unless a different peer answers the connection, so that a discovered peer that cannot be reached is chosen last | 2026-10-29 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the timeout](#1-a-peer-times-out) and [the selection rule](#3-unresponsive-peers-come-last) in [Cryptarchia Bootstrapping & Synchronization](#affected-specifications). Check that timeouts are counted in the order they happen, that a connection a different peer answers is not a timeout, and that an unresponsive peer still takes any place that no other peer can fill.

# Discussion

## Why timeouts are counted in the order they happen

While a node downloads many blocks, it sends requests faster than `T_resp`, so several requests to the same peer are often in flight at once. A rule over the last `N_timeout` requests sent to a peer would always include one still waiting, and a silent peer would never qualify. Take a node that has enough responsive peers to fill every place, and would send a silent peer a request every 0.5 seconds. Under that rule the peer never becomes unresponsive and receives 7200 requests in an hour. Counting timeouts in the order they happen makes it unresponsive after 6 seconds, and it receives 122.

## Why unresponsive peers come last instead of being left out

A node cannot tell a peer that does not answer from a network path that drops its requests. An attacker on the node's path, such as its internet provider, can make an honest peer time out by dropping three requests to it. The attacker caused the timeouts, so it knows when the unresponsive period ends, and one more dropped request then starts a new period. If unresponsive peers were left out, the attacker would have to drop a request to that peer only about once every five minutes to keep it out of about 98% of the node's requests, in a model where the node sends a request every 2 seconds. If it did this to every honest peer and kept one of its own peers responsive, its peers would be the only ones the node selects, and it could stall the node's downloads.

Choosing unresponsive peers last removes that lever. An honest peer the attacker made unresponsive still takes every place that responsive peers leave, so the attacker has to drop every request to keep it out, as it would without this rule. Only an attacker with at least as many responsive peers as a request has places can push it out. The same rule covers a node whose own connection is poor: if every peer is unresponsive, the node selects among all of them, as before.

A silent peer costs little where it still takes a place. A request goes to all selected peers at once and the node uses the first usable response, so a silent peer delays nothing.

## Why an IBD peer is never unresponsive

The node's operator configures the IBD peers and trusts them to report the chain tips the node must reach. Since they are never unresponsive, an attacker who drops requests to them cannot push them behind its own peers. It can still outnumber them with responsive peers of its own. A silent IBD peer costs a place, and an operator lists only a few.

## Why the unresponsive period does not grow

A fixed `T_unresp` needs one parameter. When the period ends, a silent peer competes as an equal again, and a single further timeout makes it unresponsive again, since no answer has broken its run of timeouts. A period that doubled with each run would need a cap, and would keep a peer that recovers behind the others for longer.

## Why a rejection does not count

A peer rejects a request it cannot serve yet, for example while its own Initial Block Download runs. It answers at once, so it costs the request a place but no waiting, and it becomes useful once it is ready. In the reference implementation, a peer over its limit of concurrent requests also rejects at once, so an attacker who floods an honest peer with requests makes it reject, not time out.

## Why a failed connection counts

The node connects to a discovered peer to send it the request. If the peer has left the network, the connection fails and the request is never sent. Counting the failure as a timeout lets the node choose such a peer last, instead of spending a place and a 5-second QUIC handshake on it in every request that selects it.

A connection that a different peer answers does not count. A dial also tries the addresses that other peers sent for the peer in answer to the node's ongoing Kademlia queries, and the first handshake to complete ends it. If such dials counted, any peer the node queries could list honest peers at its own address and make them time out without being on the node's path. In the reference implementation, a dial that a different peer answers already removes that address from the routing table, so a peer whose only address now answers under another key leaves the table at the first such dial. A connection that the node cancels or refuses itself is not the peer's doing and does not count either.

## What the rule does not defend against

The rule limits the cost of faulty peers. A malicious peer can avoid becoming unresponsive by answering one request in three, by sending each block just under `T_resp` after the previous one, or by returning under a new peer identity.

## Why the specification states the timeout

Without a time limit, a node cannot tell a silent peer from a slow one, and two implementations would count different peers as unresponsive. 5 seconds is the reply timeout the reference implementation already uses, for a reply and for each streamed block.

# Details

## 1. A peer times out

[Downloading Blocks](../cryptarchia-v1-bootstr-sync.md#downloading-blocks) gains the timeout after the rule on rejections:

```diff
 The requesting node treats the rejection as a failed request.
+A peer **times out** on a request if it neither rejects the request nor begins its response within $`T_\text{resp}`$ of the node sending it.
+It also times out if the node is reading its `DownloadBlocksResponse` and the next item does not arrive within $`T_\text{resp}`$ of the previous one.
+It also times out if the node cannot connect to it to send the request.
+It does not time out if a different peer answers the connection, or if the node itself cancels or refuses the connection.
```

## 2. Three constants

[Constants](../cryptarchia-v1-bootstr-sync.md#constants) gains the values of the two rules:

```diff
 | $`N_\text{disc}`$ | Discovered Peers per Download | The maximum number of discovered but not connected peers a download request is sent to, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 16 (recommended) |
+| $`T_\text{resp}`$ | Response Timeout | The time a peer has to reject a request, begin its response, or send the next item of a response, as defined in [Downloading Blocks](#downloading-blocks). Implementers can choose a different value. | 5 seconds (recommended) |
+| $`N_\text{timeout}`$ | Timeout Limit | The number of consecutive timeouts after which a peer is unresponsive, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 3 (recommended) |
+| $`T_\text{unresp}`$ | Unresponsive Period | How long a peer stays unresponsive after its last timeout, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 5 minutes (recommended) |
```

## 3. Unresponsive peers come last

[Selecting Peers for Downloading](../cryptarchia-v1-bootstr-sync.md#selecting-peers-for-downloading) defines an unresponsive peer:

```diff
+A peer that has timed out $`N_\text{timeout}`$ times without answering a request in between is **unresponsive** for $`T_\text{unresp}`$ after the last of those timeouts. An IBD peer is never unresponsive.
+
 For each `DownloadBlocksRequest`, including each repeated request of the same download, the node selects peers as follows:
```

It selects an unresponsive peer only for a place that no other peer can take:

```diff
 3. Randomly select up to $`N_\text{disc}`$ peers from the peers that are discovered (e.g. via the peer discovery protocol) but not connected. The node connects to them to send the request.
+
+In steps 2 and 3, the node selects an unresponsive peer only when no other peer is left to select.
```

`select_peers` fills its places in that order:

```diff
 def select_peers() -> List[Node]:
     eligible = sync_protocol_peers()
     connected = connected_peers() & eligible
     discovered = (discovered_peers() & eligible) - connected
-    return random.sample(connected, min(N_conn, len(connected))) \
-        + random.sample(discovered, min(N_disc, len(discovered)))
+    return select_up_to(connected, N_conn) + select_up_to(discovered, N_disc)
+
+def select_up_to(peers: Set[Node], n: int) -> List[Node]:
+    unresponsive = peers & unresponsive_peers()
+    others = list(peers - unresponsive)
+    chosen = random.sample(others, min(n, len(others)))
+    return chosen + random.sample(list(unresponsive), min(n - len(chosen), len(unresponsive)))
```

- The Cryptarchia Bootstrapping & Synchronization revision is 1.1.0.

# Implementation

- [ ] Count each peer's timeouts on tip and block download requests in the order they happen, and reset the count when the peer answers a request. A peer with `N_timeout` timeouts in a row is unresponsive for `T_unresp` after the last one. The network service builds the chain sync candidates in `chainsync_eligible_peers` (`services/network/src/backends/libp2p/swarm/mod.rs`), so marking unresponsive peers there reaches block downloads and the tip poll alike.
- [ ] Never mark an IBD peer unresponsive. The IBD peers are configured in `IbdConfig::peers` (`services/chain/chain-network/src/bootstrap/config.rs`), so the network service needs that list.
- [ ] Select responsive peers first and fill the remaining places with unresponsive ones, both in `choose_peers_to_request_download` and in the tip poll's `sample_tips` (`services/chain/chain-network/src/network/adapters/libp2p.rs`).
- [ ] Keep reading the first item of every selected peer's response until it arrives or the peer times out, even after another peer's response is used. Today `select_ok` in `request_blocks_from_peers` drops the other streams as soon as one first item is valid.
- [ ] Count a `Failure` reply, and a stream the peer closes, as an answer, not as a timeout.
- [ ] Count a failed connection as a timeout on the request it was opened for, except a dial that ends with `WrongPeerId` or `LocalPeerId`, or that the node aborts or denies. Today a failed dial comes back as an `OpenStreamError` from `send_blocks_request` (`consensus/cryptarchia-sync/src/libp2p/downloader.rs`), and `peer_response_timeout` starts only once the request is written (`on_blocks_request_sent`).
- [ ] Drop a peer's record once it is neither connected nor in the Kademlia routing table, so that new peer identities cannot grow the state.
- [ ] Add tests: three timeouts in a row make a peer unresponsive for `T_unresp`; an answer between timeouts resets the count; one further timeout after the period makes the peer unresponsive again; a failed connection counts as a timeout, and one that a different peer answers does not; an unresponsive peer fills a place that no responsive peer takes; an IBD peer is never unresponsive.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | Revision 1.1.0 |
