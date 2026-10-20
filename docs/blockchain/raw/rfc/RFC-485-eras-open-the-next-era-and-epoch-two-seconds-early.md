# [RFC] Eras: Open the next era and epoch two seconds early

**Motivation and proposal:** [PR #485](https://github.com/logos-co/logos-lips/pull/485)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-20 |
| v2 | Two epochs of one era share the Blend identifier, so a connection does not show its epoch. From `T_S` before an epoch until its Transition Period ends, a node therefore validates every message against both epochs' public inputs, on any connection, and releases a message of the new epoch only once that epoch begins by its own clock. The new epoch's connections count towards the degree rules apart from the current epoch's. | 2026-10-20 |
|  | Core nodes retrieve the next epoch's core nodes, and every node takes the SDP snapshot, `T_S` before the epoch. The nullifier cache keeps an entry until the Transition Period after its message's epoch, and its size bound covers `T_S`. The boundary walk re-validates the mempool before it opens the next era, as Era Change does, and the Protocol tier names the clock slack instead of its value. A node that starts during the Era Transition Period into an era runs only that era. | 2026-10-20 |
|  | Removed: the claim that an honest node never sends a new-epoch message on an old-epoch connection, which no rule made true. Corrected: the Reviewer Orientation no longer says the change only moves the transition periods, and the implementation is asked not to add the one-round delay rather than to drop it. | 2026-10-20 |

## Reviewer Orientation

Read the PR's Motivation first. The Era Transition Period now starts `T_S` before the boundary. Blend's Transition Period still starts at the epoch, but from `T_S` before it a node opens the new epoch's connections, validates messages against both epochs and holds new-epoch messages until its own switch, in place of two rules for the early side.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Blend Protocol](../blend-protocol.md) and [Service Declaration Protocol](../bedrock-service-declaration-protocol.md), [details](#1-blend-epochs) | from `T_S` before an epoch: its connections opened and counted apart, every message validated against both epochs' public inputs, new-epoch messages held until the node's own switch, bootstrapping and the SDP snapshot; the nullifier cache; `T_C < T_S`; the removed one-round bound and last-round exemption from blacklisting |
| 2 | High | [Bedrock Eras](../bedrock-eras.md), [details](#2-era-boundaries) | the Era Transition Period starting `T_S` before the boundary; the mempool following the era in force `T_S` ahead; a node that starts during the period; the boundary walk |

# Discussion

## The early side of a boundary

Nodes switch epochs and eras by their own clocks. The transition period after a boundary covers messages that arrive late. Nothing covered messages that arrive early, from a node whose clock runs ahead, except a one-round release delay for Blend messages a node generates. That delay required honest clocks to differ by less than one round, one second, and left two gaps:

- **Gossip.** A node ahead publishes on the new era's topics before a node behind subscribes to them, and gossipsub delivers a message only to subscribers. A transaction lost this way can also make a proposal that references it impossible to reconstruct at the node that missed it.
- **Relayed Blend messages.** An attacker can hand a valid new-epoch message to a node that has just switched, which relays it at once to a neighbor that has not. That neighbor saw an invalid proof of quota and blacklisted the honest relayer, so a second rule exempted such messages from blacklisting in an epoch's last round.

With the slack, every honest node has opened the next era's identifiers and the next epoch's connections, and validates the next epoch's messages, before any honest node switches, as long as `T_C < T_S`.

## Removing the two rules

- The next epoch's public input (the epoch nonce, the membership snapshot and the Blend difficulty) is fixed before the epoch begins, so a node can validate an early message. The SDP snapshot is taken `T_S` early for the same reason: its content, the registry at the last block of a finalized epoch, is fixed by then.
- Two epochs of one era share the Blend identifier, so a connection does not show its epoch, and a node releases a received message to every neighbor. A node therefore validates every message against both epochs' public inputs, whatever connection it arrives on, from `T_S` before the epoch until the Transition Period ends. Telling the epochs apart by connection would need an epoch number in the identifier, and a rule to send a message only on connections of its epoch.
- Before its own epoch begins, a node validates and caches a new-epoch message, but releases it only when the epoch begins. By then every honest node's window is open, because honest clocks differ by less than `T_S`, so no honest relayer is blacklisted for a message an attacker sent early. Releasing at once would let that message reach a neighbor whose window has not opened: the attack the last-round exemption covered, one window earlier.
- An attacker that sends a new-epoch message early gets it, at most `T_S` early, to the nodes it reaches directly, and no further until they switch. It gains no quota, since nullifiers are per epoch.

## Early transactions

The mempool validates against the era in force `T_S` ahead of the clock. A transaction carrying the new era's fork digest, published early by a node ahead, is therefore admitted, and waits. No block of the old era accepts a later digest ([Era of Chain Data](../bedrock-eras.md#era-of-chain-data)), and transaction maturity ([Block Construction](../bedrock-v1.1-block-construction.md)) takes longer than the slack. A transaction the new era refuses leaves the mempool `T_S` early, at a cost of at most two slots in which it could still have been included.

## The value of the slack

Two seconds is chosen to cover NTP jitter with high probability. It is in seconds, while `T_C` and `T` are in rounds; the comparison `T_C < T_S` relies on a round lasting one second.

## Compatibility

No network runs these rules yet. The implementation has neither the one-round rules nor the slack. At an epoch switch it keeps the old epoch's connections and validates a message against the epoch of the connection it arrives on, and it closes its edge connections. It switches topics at an era boundary with no overlap, and loads an epoch's Blend state at the epoch's first slot.

## Open questions

- No measurement of NTP synchronization among nodes backs the two seconds.
- An era that changes the length of a round must restate `T_C < T_S`.
- Block validation still rejects any block from a future slot ([Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation)), while honest clocks may now differ by up to `T_S`. Whether block acceptance should allow the same slack is left open.

# Details

## 1. Blend epochs

[Blend Protocol](../blend-protocol.md) §Transition Period:

```diff
-Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. A node releases a message it generates in the new epoch no earlier than one round after its own epoch changes ([Releasing](#releasing)). With a larger $`T_C`$, such a message can reach a node whose clock runs behind before that node's epoch changes, and that node discards it.
+From $`T_S = 2`$ seconds before a new epoch begins by its local clock, a node opens the connections of the new epoch and accepts those its neighbors open. It counts them towards the [Degree](#connectivity-maintenance) rules apart from the connections of the current epoch. The new epoch's public input is fixed before the epoch begins. Until the new epoch begins by its local clock, a node releases no message that is valid only against the new epoch's public input, and it releases such a message when the epoch begins. Otherwise a message an attacker sends to a node as its window opens can reach a neighbor whose window has not opened, and that neighbor blacklists the honest relayer. Nodes must keep their clocks synchronized so that $`T_C`$ is below $`T_S`$, a round lasting one second ([Time](#time)). Otherwise a message that a node whose clock runs ahead generates or releases in the new epoch can reach a node that does not yet validate against that epoch's public input.
```

- The epoch-change list validates message proofs against both epochs' public inputs, on every connection, from `T_S` before the epoch begins until the end of the Transition Period, and processes new messages on the connections of the new epoch.
- Connectivity Maintenance item 1 loses the last-round exemption: every invalid proof of quota closes the connection and blacklists the neighbor, as Relaying step 6 now says.
- Bootstrapping: core nodes retrieve the core nodes of an epoch, and build its network, `T_S` before it begins.
- The nullifier cache keeps an entry until the Transition Period after the epoch of its message ends, and its size bound is $`(E + T_S + T)`$ times the message rate.
- §Releasing points to the Transition Period for the release of a next-epoch message, and Notation gains `T_S`, the clock slack, in seconds.

[Service Declaration Protocol](../bedrock-service-declaration-protocol.md) §Snapshots: a node takes the snapshot for epoch $`n`$ `T_S` seconds before the epoch starts.

## 2. Era boundaries

[Bedrock Eras](../bedrock-eras.md):

- §Era Transition Period: the period starts `T_S` seconds before the era in force changes and ends `T` rounds after it, `T_S` and `T` both of the previous era. A node that starts during the period into an era runs only the protocols of that era.
- §Era Change: the mempool keeps the transactions valid under the era in force `T_S` ahead, and a node re-validates it and starts the Era Transition Period when that era changes.

```diff
 def revalidate_mempool(tip: Block, mempool: list[Transaction]) -> list[Transaction]:
-    era = era_in_force()
+    era = era_in_force_after(T_S)
     # ... unchanged lines elided
```

- §Era Boundaries: `era_in_force_after(seconds)` gives the era of the slot `seconds` ahead of the clock, and `era_in_force()` is `era_in_force_after(0)`. Notation gains `T_S`.
- The Protocol tier follows: the Chain State mempool entry, the Network Layer text and state diagram, the boundary walk and its diagram (the mempool re-validated, then the next era opened, one clock slack early; early messages processed as the Era Transition Period specifies; no one-round release delay), the Node State mempool entry, and the Overview chart and text.

## Chores

- Revision-history rows added to Bedrock Eras, Blend Protocol and Service Declaration Protocol.

# Implementation

- [ ] From `T_S` = 2 seconds before a Blend epoch begins by the local clock, open its connections and accept those of neighbors, counted towards the degree rules apart from the current epoch's; retrieve its core nodes and take its SDP snapshot by then
- [ ] From then until the Transition Period ends, validate every Blend message against both epochs' public inputs on any connection, edge connections included; release a new-epoch message only once the epoch begins by the local clock; do not add the one-round release delay, and blacklist on any invalid proof of quota
- [ ] Keep a nullifier until the Transition Period after its message's epoch ends
- [ ] Open the next era's identifiers and subscribe to its topics `T_S` before the boundary, and keep the previous era's until `T` rounds after it; a node that starts during the period runs only the new era
- [ ] Validate the mempool against the era in force `T_S` ahead, and re-validate it when that era changes
- [ ] Add tests that switch epochs and eras with node clocks up to `T_S` apart, including gossip and Blend messages from a node whose clock runs ahead, and a next-epoch message an attacker sends as a node's window opens
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | clock slack at every epoch: early connections counted apart, validation against both epochs, new-epoch messages held until the epoch begins, bootstrapping and the nullifier cache; one-round clock bound and last-round exemption from blacklisting removed |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Era Transition Period from the clock slack before the boundary; mempool under the era in force that slack ahead; a node starting during the period runs only the new era |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | snapshot taken the clock slack before its epoch |
