# [RFC] Eras: Open the next era and epoch two seconds early

**Motivation and proposal:** [PR #485](https://github.com/logos-co/logos-lips/pull/485)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-20 |
| v2 | Two epochs of one era share the Blend identifier, so a connection does not show its epoch. From `T_S` before an epoch until its Transition Period ends, a node therefore validates every message against both epochs' public inputs, on any connection, and releases a message of the new epoch only once that epoch begins by its own clock. The new epoch's connections count towards the degree rules apart from the current epoch's. | 2026-10-20 |
|  | Core nodes retrieve the next epoch's core nodes, and every node takes the SDP snapshot, `T_S` before the epoch. The nullifier cache keeps an entry until the Transition Period after its message's epoch, and its size bound covers `T_S`. The boundary walk re-validates the mempool before it opens the next era, as Era Change does, and the Protocol tier names the clock slack instead of its value. A node that starts during the Era Transition Period into an era runs only that era. | 2026-10-20 |
|  | Removed: the claim that an honest node never sends a new-epoch message on an old-epoch connection, which no rule made true. Corrected: the Reviewer Orientation no longer says the change only moves the transition periods, and the implementation is asked not to add the one-round delay rather than to drop it. | 2026-10-20 |
| v3 | Blend's protocol name for an epoch's connections ends in the epoch digest, a hash of the epoch number and the proof-of-quota public inputs fixed for the epoch, so a connection shows its epoch. A node validates a message against the epoch of its connection and sends it only on connections of that epoch. Removed: validating every message against both epochs, and holding a next-epoch message until the node's own switch, which per-epoch connections make unnecessary. Nodes whose epoch inputs differ never connect. | 2026-10-20 |
| v4 | [Mempool](../mempool.md) follows the clock slack: admission, `preverify` and the retirement at an era change use the era in force `T_S` ahead, and block building leaves out the transactions whose fork digest the block's era does not accept, so a leader of an era's last blocks does not retire an early transaction as inapplicable. Removed: re-validating the mempool against the chain tip, which the era rules of Mempool replace. | 2026-10-21 |
| v5 | Rebuilt on specifications that already name each epoch's Blend connections by the epoch digest, open and accept connections only of a node's current epoch, validate and send each message on connections of its epoch, have no one-round release delay or last-round exemption, and keep a previous era only for what is in flight. Removed from this RFC: those rules and their discussion. It keeps the clock slack: the next epoch's and era's connections opened and accepted `T_S` early, early validation, bootstrapping and SDP snapshot, the nullifier cache, `T_C < T_S`, and the mempool. Until the era in force changes, both eras take new connections. | 2026-10-22 |

## Reviewer Orientation

Read the PR's Motivation first. The Era Transition Period now starts `T_S` before the boundary. Blend's Transition Period still starts at the epoch, but from `T_S` before it a node also opens and accepts the new epoch's connections.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Blend Protocol](../blend-protocol.md) and [Service Declaration Protocol](../bedrock-service-declaration-protocol.md), [details](#1-blend-epochs) | from `T_S` before an epoch: its connections opened, accepted and counted apart, messages validated on them, bootstrapping and the SDP snapshot; the nullifier cache; `T_C < T_S` |
| 2 | High | [Bedrock Eras](../bedrock-eras.md), [details](#2-era-boundaries) | the Era Transition Period, and the retirement of pending transactions at an era change, starting `T_S` before the boundary; both eras taking new connections until the era in force changes; a node that starts during the period; the boundary walk |
| 3 | High | [Mempool](../mempool.md), [details](#3-mempool) | admission, `preverify` and the era-change retirement under the era in force `T_S` ahead; block building leaving out the transactions whose fork digest the block's era does not accept |

# Discussion

## The early side of a boundary

Nodes switch epochs and eras by their own clocks. A node opens and accepts connections only of its current epoch and era, and after an era changes it keeps the previous era's identifiers only for what is in flight. The transition period after a boundary covers messages that arrive late. Nothing covers the switch itself, which leaves two gaps:

- **Refused connections.** A node whose clock runs ahead switches first. Its neighbors whose clocks run behind refuse its new-epoch connections until they switch too, and the messages it generates in that time reach none of them. Honest clocks within one round keep this short but do not remove it.
- **Gossip.** A node ahead publishes on the new era's topics before a node behind subscribes to them, and gossipsub delivers a message only to subscribers. A transaction lost this way can also make a proposal that references it impossible to reconstruct at the node that missed it.

With the slack, every honest node has opened the next era's identifiers and the next epoch's connections before any honest node switches, as long as `T_C < T_S`.

## Opening early

- The next epoch's public input (the epoch nonce, the membership snapshot and the Blend difficulty) is fixed before the epoch begins, so a node can compute the next epoch's protocol name and validate an early message. The SDP snapshot is taken `T_S` early for the same reason: its content, the registry at the last block of a finalized epoch, is fixed by then.
- Until the era in force changes, a node takes new connections on both eras. Only from the change on does it keep the previous era for what is in flight.
- An attacker gains at most `T_S` of early relay, with no extra quota, since nullifiers are per epoch.

## Early transactions

The mempool admits under the era in force `T_S` ahead of the clock. A transaction carrying the new era's fork digest, published early by a node ahead, is therefore admitted, and waits. No block of the old era accepts a later digest ([Era of Chain Data](../bedrock-eras.md#era-of-chain-data)), so block building leaves it out of the old era's last blocks, and a leader of those blocks does not retire it as inapplicable. Transaction maturity ([Block Construction](../bedrock-v1.1-block-construction.md)) takes longer than the slack. A transaction whose fork digest the new era refuses leaves the mempool `T_S` early, and one that arrives in that time passes `preverify` under the new era's rules. Each costs at most two slots in which the transaction could still have been included.

## The value of the slack

Two seconds is chosen to cover NTP jitter with high probability. It is in seconds, while `T_C` and `T` are in rounds; the comparison `T_C < T_S` relies on a round lasting one second.

## Compatibility

No network runs these rules yet. The implementation has no slack: it switches topics at an era boundary with no overlap, and loads an epoch's Blend state at the epoch's first slot.

## Open questions

- No measurement of NTP synchronization among nodes backs the two seconds.
- An era that changes the length of a round must restate `T_C < T_S`.
- Block validation still rejects any block from a future slot ([Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation)), while honest clocks may now differ by up to `T_S`. Whether block acceptance should allow the same slack is left open.

# Details

## 1. Blend epochs

[Blend Protocol](../blend-protocol.md) §Transition Period:

```diff
-A node opens and accepts connections only of its current epoch, by its local clock ([Connection Details](#connection-details)). Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. Otherwise the neighbors whose clocks run behind a node can refuse its connections of the new epoch for more than a round after its epoch changes, and the messages it generates in that time reach none of them.
+A node opens and accepts connections only of its current epoch, by its local clock, and from $`T_S = 2`$ seconds before a new epoch begins also those of the new epoch ([Connection Details](#connection-details)). It counts the new epoch's connections towards the [Degree](#connectivity-maintenance) rules apart from the connections of the current epoch. The new epoch's public input is fixed before the epoch begins. Nodes must keep their clocks synchronized so that $`T_C`$ is below $`T_S`$, a round lasting one second ([Time](#time)). Otherwise a neighbor whose clock runs behind a node can still refuse its connections of the new epoch after its epoch changes, and the messages it generates in that time reach none of those neighbors.
```

- The epoch-change list validates a message on a connection of the new epoch against that epoch's public input from `T_S` before the epoch begins.
- Bootstrapping: core nodes retrieve the core nodes of an epoch, and build its network, `T_S` before it begins.
- The nullifier cache keeps an entry until the Transition Period after the epoch of its message ends, and its size bound is $`(E + T_S + T)`$ times the message rate.
- Notation gains `T_S`, the clock slack, in seconds.

[Service Declaration Protocol](../bedrock-service-declaration-protocol.md) §Snapshots: a node takes the snapshot for epoch $`n`$ `T_S` seconds before the epoch starts.

## 2. Era boundaries

[Bedrock Eras](../bedrock-eras.md):

- §Era Transition Period: the period starts `T_S` seconds before the era in force changes and ends `T` rounds after it, `T_S` and `T` both of the previous era. A node opens and accepts connections on the identifiers of both eras until the era in force changes, and keeps the previous era only for what is in flight from then on. A node that starts during the period into an era runs only the protocols of that era.
- §Era Change: a node retires the pending transactions whose fork digest the new era does not accept, and starts the Era Transition Period, when `era_in_force_after(T_S)` changes rather than when the era in force does.
- §Era Boundaries: `era_in_force_after(seconds)` gives the era of the slot `seconds` ahead of the clock, and `era_in_force()` is `era_in_force_after(0)`. Notation gains `T_S`.
- The Protocol tier follows: the Network Layer text and state diagram, the boundary walk and its diagram (the pending transactions retired, then the next era opened, one clock slack early; early messages processed as the Era Transition Period specifies), the Node State mempool and identifier entries, and the Overview chart and text.

## 3. Mempool

[Mempool](../mempool.md):

- §Transaction Admission: `admit` checks the fork digest against the era in force `T_S` ahead, and `preverify` applies the rules of that era.

```diff
-    if not accepts_fork_digest(era_in_force(), tx.tx.fork_digest):
+    if not accepts_fork_digest(era_in_force_after(T_S), tx.tx.fork_digest):
```

- §Block Building View: `applicability` leaves out the pending transactions whose fork digest the era of the block's slot does not accept, so they stay pending instead of becoming inapplicable.

```python
    era = era_of_slot(header.slot)
    applied, remaining = [], [key for key in mempool.pending
                              if accepts_fork_digest(era, mempool.bodies[key].tx.fork_digest)]
```

- §Era Change: a pending transaction is retired when `era_in_force_after(T_S)` does not accept its fork digest, checked when that era changes and on recovery.
- The Overview, the Admission Pipeline, Block Building Input and Retirement Reasons follow, and Notation gains `T_S`.

## Chores

- Revision-history rows added to Bedrock Eras, Blend Protocol, Mempool and Service Declaration Protocol.

# Implementation

- [ ] From `T_S` = 2 seconds before a Blend epoch begins by the local clock, open its connections and accept those of neighbors, counted towards the degree rules apart from the current epoch's, and validate messages on them against that epoch; retrieve its core nodes and take its SDP snapshot by then
- [ ] Keep a nullifier until the Transition Period after its message's epoch ends
- [ ] Open the next era's identifiers and subscribe to its topics `T_S` before the boundary, take new connections on both eras until the boundary, and keep the previous era's identifiers, for what is in flight only, until `T` rounds after it; a node that starts during the period runs only the new era
- [ ] Admit and preverify transactions under the era in force `T_S` ahead, retire those whose fork digest it does not accept when it changes, and leave out of block building the transactions whose fork digest the block's era does not accept
- [ ] Add tests that switch epochs and eras with node clocks up to `T_S` apart, including gossip and Blend messages from a node whose clock runs ahead, and a next-epoch message an attacker sends as a node's window opens
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | clock slack at every epoch: the next epoch's connections opened and accepted early and counted apart, early validation, bootstrapping and the nullifier cache; `T_C < T_S` |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Era Transition Period and the era-change retirement of pending transactions from the clock slack before the boundary, with both eras taking new connections until the era in force changes; a node starting during the period runs only the new era |
| [Mempool](../mempool.md) | Modified | admission, `preverify` and the era-change retirement under the era in force the clock slack ahead; block building leaves out transactions whose fork digest the block's era does not accept |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | snapshot taken the clock slack before its epoch |
