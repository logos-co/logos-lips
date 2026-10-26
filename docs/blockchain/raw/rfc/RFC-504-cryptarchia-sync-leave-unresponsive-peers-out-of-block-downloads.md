# [RFC] Cryptarchia-Sync: Leave unresponsive peers out of block downloads

**Motivation and proposal:** [PR #504](https://github.com/logos-co/logos-lips/pull/504)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-26 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the timeout](#1-a-peer-times-out) and [the selection rule](#3-unresponsive-peers-are-left-out) in [Cryptarchia Bootstrapping & Synchronization](#affected-specifications). Check that timeouts are counted in the order they happen, and that the node still selects peers when every peer is unresponsive.

# Discussion

## Why timeouts are counted in the order they happen

While a node downloads many blocks, it sends requests faster than `T_resp`, so several requests to the same peer are often in flight at once. A rule over the last `N_timeout` requests sent to a peer would always include one still waiting, and a silent peer would never qualify. In a model where the node sends a silent peer a request every 0.5 seconds, that rule never excludes the peer, which receives 7200 requests in an hour. Counting timeouts in the order they happen excludes it after 6 seconds, and it receives 122.

## Why the exclusion does not grow

A fixed `T_excl` needs one parameter. Once its exclusion ends, a silent peer is picked again, and a single further timeout excludes it again, since no answer has broken its run of timeouts. That costs the requests sent to the peer during one `T_resp`, once every `T_excl`. An exclusion that doubled with each run would need a cap, and would keep a peer that recovers out for longer.

## Why every peer stays selectable when all are unresponsive

A node whose own connection is poor can see every peer time out. Without the fallback, it would stop downloading for `T_excl` and fall behind. With it, the node selects peers as it did before this change.

## Why a rejection does not count

A peer rejects a request it cannot serve yet, for example while its own Initial Block Download runs. It answers at once, so it costs the request a slot but no waiting, and it becomes useful once it is ready.

## Why the specification states the timeout

Without a time limit, a node cannot tell a silent peer from a slow one, and two implementations would count different peers as unresponsive. 5 seconds is the reply timeout the reference implementation already uses, for a reply and for each streamed block.

# Details

## 1. A peer times out

[Downloading Blocks](../cryptarchia-v1-bootstr-sync.md#downloading-blocks) gains the timeout after the rule on rejections:

```diff
 The requesting node treats the rejection as a failed request.
+A peer **times out** on a request if it neither rejects the request nor begins its response within $`T_\text{resp}`$ of the node sending it.
+It also times out if the node is reading its `DownloadBlocksResponse` and the next item does not arrive within $`T_\text{resp}`$ of the previous one.
```

## 2. Three constants

[Constants](../cryptarchia-v1-bootstr-sync.md#constants) gains the values of the two rules:

```diff
 | $`N_\text{disc}`$ | Discovered Peers per Download | The maximum number of discovered but not connected peers a download request is sent to, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 16 (recommended) |
+| $`T_\text{resp}`$ | Response Timeout | The time a peer has to reject a request, begin its response, or send the next item of a response, as defined in [Downloading Blocks](#downloading-blocks). Implementers can choose a different value. | 5 seconds (recommended) |
+| $`N_\text{timeout}`$ | Timeout Limit | The number of consecutive timeouts after which a peer is unresponsive, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 3 (recommended) |
+| $`T_\text{excl}`$ | Exclusion Period | How long a peer stays unresponsive after its last timeout, as defined in [Selecting Peers for Downloading](#selecting-peers-for-downloading). Implementers can choose a different value. | 5 minutes (recommended) |
```

## 3. Unresponsive peers are left out

[Selecting Peers for Downloading](../cryptarchia-v1-bootstr-sync.md#selecting-peers-for-downloading) defines an unresponsive peer and leaves it out of the selection:

```diff
+A peer that has timed out $`N_\text{timeout}`$ times without answering a request in between is **unresponsive** for $`T_\text{excl}`$ after the last of those timeouts.
+
 For each `DownloadBlocksRequest`, including each repeated request of the same download, the node selects peers as follows:
 
-1. Consider only peers that support the sync protocol (i.e. that advertise the [Libp2p Protocol ID](#downloading-blocks) above).
+1. Consider only peers that support the sync protocol (i.e. that advertise the [Libp2p Protocol ID](#downloading-blocks) above). Leave out the unresponsive ones, unless all of them are unresponsive.
```

`select_peers` changes to match:

```diff
 def select_peers() -> List[Node]:
     eligible = sync_protocol_peers()
+    eligible = (eligible - unresponsive_peers()) or eligible
     connected = connected_peers() & eligible
```

- The Cryptarchia Bootstrapping & Synchronization revision is 1.1.0.

# Implementation

- [ ] Count each peer's timeouts on tip and block download requests in the order they happen, and reset the count when the peer answers a request. A peer with `N_timeout` timeouts in a row is unresponsive for `T_excl` after the last one. The network service builds the chain sync candidates in `chainsync_eligible_peers` (`services/network/src/backends/libp2p/swarm/mod.rs`), so leaving unresponsive peers out there covers block downloads and the tip poll alike.
- [ ] Keep reading the first item of every selected peer's response until it arrives or the peer times out, even after another peer's response is used. Today `select_ok` in `request_blocks_from_peers` drops the other streams as soon as one first item is valid (`services/chain/chain-network/src/network/adapters/libp2p.rs`).
- [ ] Count a `Failure` reply as an answer, not as a timeout.
- [ ] When every chain sync peer is unresponsive, select among all of them.
- [ ] Add tests: three timeouts in a row exclude a peer for `T_excl`; an answer between timeouts resets the count; one further timeout after the exclusion excludes the peer again; with every peer unresponsive, selection still returns peers.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | Revision 1.1.0 |
