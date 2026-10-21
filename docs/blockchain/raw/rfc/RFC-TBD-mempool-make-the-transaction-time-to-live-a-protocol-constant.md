# [RFC] Mempool: Make the transaction time to live a protocol constant

**Motivation and proposal:** PR #TBD

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-21 |

## Reviewer Orientation

Single-document change — read [Parameters](../mempool.md#parameters) and [Expiry](../mempool.md#expiry) in the [Mempool](../mempool.md), and focus on `TRANSACTION_TTL`, which is now the same on every node, and on the bound this gives `RETIREMENT_GRACE`.

# Discussion

## What a node setting allows

A node retires a pending transaction once its age reaches `TRANSACTION_TTL`, the transaction's time to live. Until this change, the specification described what `logos-blockchain` does at `8eb8a05e5`. Each node sets the time to live itself, one hour by default, and a node that sets it to `None` retires no transaction for its age. Two things follow:

- A node that disables expiry and never leads retires a transaction only when a block that carries it enters its canonical chain, or when it carries a claim whose deadline has passed. Admission reads no ledger state, so anyone can submit, at no cost, transactions that can never apply. Such a node keeps all of them. Nothing else bounds how many its mempool holds, and the mempool persists across restarts.
- Nodes that set different values disagree about which transactions they hold. A leader can select a transaction until its own copy reaches the leader's time to live. A validator with a shorter time to live retires its copy earlier, and discards it `RETIREMENT_GRACE` later. If the leader's proposal arrives after the validator has discarded its copy, the validator cannot resolve the reference to that transaction. It rejects the proposal and does not build on it, as [Reference Resolution](../bedrock-v1.1-block-construction.md#reference-resolution) specifies, and can receive the block later, in full, through chain synchronisation. A leader that disables expiry can select a transaction of any age.

## Why one value

With one value, two nodes' copies of a transaction expire at times that differ only by when each node admitted it. For a transaction that both nodes received by gossip, that difference is the time gossip took between them. With a value per node, the difference also includes the difference between the two values, which can be of any length, while `RETIREMENT_GRACE` keeps a retired copy resolvable for only ten minutes.

One value does not remove every difference. After a fork switch, a node re-admits a displaced transaction at the current time and broadcasts it. A node that never retired the transaction drops that copy as a duplicate, and keeps its earlier admission time.

A constant also leaves no node without expiry. Every node retires a transaction that no block includes once its age reaches `TRANSACTION_TTL`, and discards it `RETIREMENT_GRACE` later.

The change alters no message, encoding or consensus rule. It removes a node setting.

## The bound one value gives `RETIREMENT_GRACE`

A leader can select a transaction for as long as its own copy is pending. A node retires an expired transaction only when it processes a block, or when it retires others ([Effects of Retirement](../mempool.md#effects-of-retirement)), so the leader's copy can stay pending until the first block after its age reaches `TRANSACTION_TTL`. A validator retires its own copy at the first block after that copy expires, and resolves it for `RETIREMENT_GRACE` more. With one value, the leader's proposal still resolves at the validator if `RETIREMENT_GRACE` exceeds the sum of three times:

- how much earlier the validator admitted the transaction, which for a transaction both nodes received by gossip is at most the time gossip takes to reach every node;
- the time between two consecutive blocks;
- the time the proposal takes to reach the validator.

[Parameters](../mempool.md#parameters) states this bound beside `RETIREMENT_GRACE`. With a value per node, no grace bounds it.

With a slot activation coefficient of 1/30, two consecutive blocks are more than nine and a half minutes apart with probability $`(29/30)^{570} \approx 4 \times 10^{-9}`$. Ten minutes therefore leaves 30 seconds for gossip and delivery in all but about one gap in 250 million. The bound does not cover a transaction re-admitted after a fork switch, whose two copies can differ by more than gossip takes.

## Why one hour

One hour is the implementation's default, so a node that runs the default behaves as before. A transaction that waits longer than an hour for a leader is retired, and its sender must submit it again. With the slot activation coefficient of 1/30 and the one-second slots of Cryptarchia's [Constants](../cryptarchia-v1-protocol.md#constants), a block arrives every 30 seconds on average, so an hour is about 120 blocks.

A longer value lets a transaction wait longer for a leader. It also makes every node keep a transaction that never applies for longer, and nothing else bounds how many such transactions a node keeps.

# Details

## One time to live for every node

`TRANSACTION_TTL` is a protocol constant, still one hour. [Parameters](../mempool.md#parameters) drops `None` from its type:

```diff
-TRANSACTION_TTL: Optional[uint64] = 60 * 60  # seconds a transaction may stay pending before it is retired
+TRANSACTION_TTL: uint64 = 60 * 60            # seconds a transaction may stay pending before it is retired
 RETIREMENT_GRACE: uint64 = 10 * 60           # seconds a retired transaction stays resolvable before it is discarded
 CLAIM_GRACE: uint64 = 2 * WINDOW             # slots a claim stays pending after its acceptance window closes
```

It also drops the sentence that made the value a node setting:

```diff
-`TRANSACTION_TTL` is a node setting, and the value above is its default. A node that sets it to `None` retires no transaction for its age.
```

[Expiry](../mempool.md#expiry) and [Retirement Reasons](../mempool.md#retirement-reasons) drop the exception for a node that disables expiry:

```diff
-A pending transaction whose age reaches `TRANSACTION_TTL` is retired, unless `TRANSACTION_TTL` is `None`.
+A pending transaction whose age reaches `TRANSACTION_TTL` is retired.
```

```diff
-- its age reaches `TRANSACTION_TTL`, unless the node disables expiry;
+- its age reaches `TRANSACTION_TTL`;
```

## A bound for `RETIREMENT_GRACE`

[Parameters](../mempool.md#parameters) states the constraint on `RETIREMENT_GRACE`:

```diff
 `CLAIM_GRACE` must exceed the time, in slots, that a block proposal takes to reach every node. Otherwise a node can retire a claim before a proposal that selected it in the last slot of its acceptance window arrives.
+
+`RETIREMENT_GRACE` must exceed the time a transaction takes to reach every node by gossip, plus the time between two consecutive blocks, plus the time a block proposal takes to reach every node. Otherwise a node can discard a transaction that it retired for its age before a proposal that selected it arrives.
```

# Implementation

- [ ]  Replace the `tx_ttl` setting, in the mempool settings and in the node configuration, with the constant `TRANSACTION_TTL` of one hour, so that no node can change the time to live or disable expiry
- [ ]  Add or extend tests: a transaction is evicted once its age reaches one hour, and `expired_tx_is_not_evicted_when_ttl_is_disabled` is removed
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Modified | `TRANSACTION_TTL` is a protocol constant of one hour, no node disables expiry, and `RETIREMENT_GRACE` states its bound. |
