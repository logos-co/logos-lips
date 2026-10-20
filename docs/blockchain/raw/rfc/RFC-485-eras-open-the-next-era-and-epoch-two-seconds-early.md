# [RFC] Eras: Open the next era and epoch two seconds early

**Motivation and proposal:** [PR #485](https://github.com/logos-co/logos-lips/pull/485)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-20 |

## Reviewer Orientation

Read the PR's Motivation first. The Era Transition Period and Blend's Transition Period are assumed; this change only moves their start earlier.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Blend Protocol](../blend-protocol.md), [details](#1-blend-epochs) | a new epoch's connections opened `T_S` early and early messages validated against the new epoch's public input; `T_C < T_S`; the removed one-round bound and last-round exemption from blacklisting |
| 2 | High | [Bedrock Eras](../bedrock-eras.md), [details](#2-era-boundaries) | the Era Transition Period starting `T_S` before the boundary; the mempool following the era in force `T_S` ahead; the boundary walk |

# Discussion

## The early side of a boundary

Nodes switch epochs and eras by their own clocks. The transition period after a boundary covers messages that arrive late. Nothing covered messages that arrive early, from a node whose clock runs ahead, except a one-round release delay for Blend messages a node generates. That delay required honest clocks to differ by less than one round, one second, and left two gaps:

- **Gossip.** A node ahead publishes on the new era's topics before a node behind subscribes to them, and gossipsub delivers a message only to subscribers. A transaction lost this way can also make a proposal that references it impossible to reconstruct at the node that missed it.
- **Relayed Blend messages.** An attacker can hand a valid new-epoch message to a node that has just switched, which relays it at once to a neighbor that has not. That neighbor saw an invalid proof of quota and blacklisted the honest relayer, so a second rule exempted such messages from blacklisting in an epoch's last round.

With the slack, every honest node has opened the next era's identifiers and the next epoch's connections before any honest node switches, as long as `T_C < T_S`. Early messages then arrive on connections that expect them.

## Removing the two rules

- The next epoch's public input (the epoch nonce, the membership snapshot and the Blend difficulty) is fixed before the epoch begins, so a node can validate an early message.
- An honest node never sends a new-epoch message on an old-epoch connection: it generates under its own epoch and relays on the epoch of the connection a message arrived on. A next-epoch message on an old connection is therefore attributable, and the exemption from blacklisting has nothing left to protect.
- A message sent before its recipient's window opens is not delivered at all, so no honest node is blacklisted for it.
- An attacker gains at most two seconds of early relay, with no extra quota, since nullifiers are per epoch.

## Early transactions

The mempool validates against the era in force `T_S` ahead of the clock. A transaction carrying the new era's fork digest, published early by a node ahead, is therefore admitted, and waits. No block of the old era accepts a later digest ([Era of Chain Data](../bedrock-eras.md#era-of-chain-data)), and transaction maturity ([Block Construction](../bedrock-v1.1-block-construction.md)) takes longer than the slack. A transaction the new era refuses leaves the mempool `T_S` early, at a cost of at most two slots in which it could still have been included.

## The value of the slack

Two seconds is chosen to cover NTP jitter with high probability. It is in seconds, while `T_C` and `T` are in rounds; the comparison `T_C < T_S` relies on a round lasting one second.

## Compatibility

No network runs these rules yet. The implementation has neither the one-round rules nor the slack: it switches topics at the boundary with no overlap, and loads an epoch's Blend state at the epoch's first slot.

## Open questions

- No measurement of NTP synchronization among nodes backs the two seconds.
- An era that changes the length of a round must restate `T_C < T_S`.
- Block validation still rejects any block from a future slot ([Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation)), while honest clocks may now differ by up to `T_S`. Whether block acceptance should allow the same slack is left open.

# Details

## 1. Blend epochs

[Blend Protocol](../blend-protocol.md) §Transition Period:

```diff
-Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. A node releases a message it generates in the new epoch no earlier than one round after its own epoch changes ([Releasing](#releasing)). With a larger $`T_C`$, such a message can reach a node whose clock runs behind before that node's epoch changes, and that node discards it.
+From $`T_S = 2`$ seconds before a new epoch begins by its local clock, a node opens the connections of the new epoch and accepts those its neighbors open. It validates a message that arrives on such a connection against the new epoch's public input, which is fixed before the epoch begins. Nodes must keep their clocks synchronized so that $`T_C`$ is below $`T_S`$, a round lasting one second ([Time](#time)). Otherwise a message that a node whose clock runs ahead generates in the new epoch can reach a node that has not yet opened its connections for that epoch.
```

- The epoch-change list processes new messages on the connections opened for the new epoch.
- Connectivity Maintenance item 1 loses the last-round exemption: a message whose proof of quota is valid only against the next epoch's public input is treated as any other invalid proof of quota. Relaying step 6 closes the connection and blacklists the neighbor.
- Notation gains `T_S`, the clock slack.

## 2. Era boundaries

[Bedrock Eras](../bedrock-eras.md):

- §Era Transition Period: the period starts `T_S` seconds before the era in force changes and ends `T` rounds after it, `T_S` and `T` both of the previous era.
- §Era Change: the mempool keeps the transactions valid under the era in force `T_S` ahead, and a node re-validates it and starts the Era Transition Period when that era changes.

```diff
 def revalidate_mempool(tip: Block, mempool: list[Transaction]) -> list[Transaction]:
-    era = era_in_force()
+    era = era_in_force_after(T_S)
     # ... unchanged lines elided
```

- §Era Boundaries: `era_in_force_after(seconds)` gives the era of the slot `seconds` ahead of the clock, and `era_in_force()` is `era_in_force_after(0)`. Notation gains `T_S`.
- The Protocol tier follows: the Network Layer text and state diagram, the boundary walk and its diagram (the next era opened early, early messages processed under it, no one-round release delay), the Node State mempool entry, and the Overview chart and text.

## Chores

- Revision-history rows added to Bedrock Eras and Blend Protocol.

# Implementation

- [ ] Open a new Blend epoch's connections, and accept those of neighbors, `T_S` = 2 seconds before the epoch begins by the local clock, with the next epoch's public input loaded by then
- [ ] Validate messages on new-epoch connections against the new epoch's public input; drop the one-round release delay and blacklist on any invalid proof of quota
- [ ] Open the next era's identifiers and subscribe to its topics `T_S` before the boundary, and keep the previous era's until `T` rounds after it
- [ ] Validate the mempool against the era in force `T_S` ahead, and re-validate it when that era changes
- [ ] Add tests that switch epochs and eras with node clocks up to `T_S` apart, including gossip and Blend messages from a node whose clock runs ahead
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | clock slack at every epoch; one-round clock bound and last-round exemption from blacklisting removed |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Era Transition Period from the clock slack before the boundary; mempool under the era in force that slack ahead |
