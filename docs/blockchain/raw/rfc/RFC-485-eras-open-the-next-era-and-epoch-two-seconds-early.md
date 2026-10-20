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

## Reviewer Orientation

Read the PR's Motivation first. The Era Transition Period now starts `T_S` before the boundary. Blend's Transition Period still starts at the epoch, but from `T_S` before it a node opens the new epoch's connections, named by the epoch's digest, in place of two rules for the early side.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Blend Protocol](../blend-protocol.md) and [Service Declaration Protocol](../bedrock-service-declaration-protocol.md), [details](#1-blend-epochs) | the epoch digest in the protocol name, and what it binds; from `T_S` before an epoch: its connections opened and counted apart, bootstrapping and the SDP snapshot; each message validated against, and sent only on, connections of its epoch; the nullifier cache; `T_C < T_S`; the removed one-round bound and last-round exemption from blacklisting |
| 2 | High | [Bedrock Eras](../bedrock-eras.md), [details](#2-era-boundaries) | the Era Transition Period starting `T_S` before the boundary; the mempool following the era in force `T_S` ahead; a node that starts during the period; the boundary walk |

# Discussion

## The early side of a boundary

Nodes switch epochs and eras by their own clocks. The transition period after a boundary covers messages that arrive late. Nothing covered messages that arrive early, from a node whose clock runs ahead, except a one-round release delay for Blend messages a node generates. That delay required honest clocks to differ by less than one round, one second, and left two gaps:

- **Gossip.** A node ahead publishes on the new era's topics before a node behind subscribes to them, and gossipsub delivers a message only to subscribers. A transaction lost this way can also make a proposal that references it impossible to reconstruct at the node that missed it.
- **Relayed Blend messages.** An attacker can hand a valid new-epoch message to a node that has just switched, which relays it at once to a neighbor that has not. That neighbor saw an invalid proof of quota and blacklisted the honest relayer, so a second rule exempted such messages from blacklisting in an epoch's last round.

With the slack, every honest node has opened the next era's identifiers and the next epoch's connections before any honest node switches, as long as `T_C < T_S`.

## Removing the two rules

- The next epoch's public input (the epoch nonce, the membership snapshot and the Blend difficulty) is fixed before the epoch begins, so a node can compute the next epoch's protocol name and validate an early message. The SDP snapshot is taken `T_S` early for the same reason: its content, the registry at the last block of a finalized epoch, is fixed by then.
- Two epochs of one era share the fork digest, so without more a connection would not show its epoch. The protocol name of an epoch's connections therefore ends in a digest of the epoch number and every proof-of-quota public input fixed for the epoch. A node validates a message against its connection's epoch and sends it only on connections of that epoch, so a message of one epoch never meets a check of the other.
- A node whose window has not opened has no connection of the next epoch, so a next-epoch message an attacker sends early cannot reach it, and no honest relayer is blacklisted for it. The last-round exemption has nothing left to protect, and no message needs holding until its epoch begins.
- Nodes whose epoch inputs differ, such as nodes on different forks, never connect, so they no longer blacklist each other for proofs that are valid only on their own fork. Binding only the epoch number would separate epochs but not forks. The signing key and the nullifier change with each message, so the digest leaves them out.
- An attacker gains at most `T_S` of early relay, with no extra quota, since nullifiers are per epoch.

## Early transactions

The mempool validates against the era in force `T_S` ahead of the clock. A transaction carrying the new era's fork digest, published early by a node ahead, is therefore admitted, and waits. No block of the old era accepts a later digest ([Era of Chain Data](../bedrock-eras.md#era-of-chain-data)), and transaction maturity ([Block Construction](../bedrock-v1.1-block-construction.md)) takes longer than the slack. A transaction the new era refuses leaves the mempool `T_S` early, at a cost of at most two slots in which it could still have been included.

## The value of the slack

Two seconds is chosen to cover NTP jitter with high probability. It is in seconds, while `T_C` and `T` are in rounds; the comparison `T_C < T_S` relies on a round lasting one second.

## Compatibility

No network runs these rules yet. The implementation has neither the one-round rules nor the slack. At an epoch switch it keeps the old epoch's connections and validates a message against the epoch of the connection it arrives on, and it closes its edge connections. Its Blend protocol name has no epoch part, so it tells a connection's epoch only by when the connection was made. It switches topics at an era boundary with no overlap, and loads an epoch's Blend state at the epoch's first slot.

## Open questions

- No measurement of NTP synchronization among nodes backs the two seconds.
- An era that changes the length of a round must restate `T_C < T_S`.
- Block validation still rejects any block from a future slot ([Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation)), while honest clocks may now differ by up to `T_S`. Whether block acceptance should allow the same slack is left open.

# Details

## 1. Blend epochs

[Blend Protocol](../blend-protocol.md) §Transition Period:

```diff
-Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. A node releases a message it generates in the new epoch no earlier than one round after its own epoch changes ([Releasing](#releasing)). With a larger $`T_C`$, such a message can reach a node whose clock runs behind before that node's epoch changes, and that node discards it.
+From $`T_S = 2`$ seconds before a new epoch begins by its local clock, a node opens the connections of the new epoch, under its protocol name ([Connection Details](#connection-details)), and accepts those its neighbors open. It counts them towards the [Degree](#connectivity-maintenance) rules apart from the connections of the current epoch. The new epoch's public input is fixed before the epoch begins. Nodes must keep their clocks synchronized so that $`T_C`$ is below $`T_S`$, a round lasting one second ([Time](#time)). Otherwise a node whose clock runs ahead can send a message of the new epoch before a node whose clock runs behind has opened that epoch's connections.
```

- §Connection Details: the protocol name of an epoch's connections is `/logos-blockchain/<fork_digest>/blend/<epoch_digest>`, with the epoch digest in lowercase hexadecimal. A new §Epoch Digest defines it:

```python
def epoch_digest(epoch: EpochNumber, p: ProofOfQuotaPublic) -> hash:
    inputs = (p.core_quota, p.leader_quota, p.core_root, p.pow_quota, p.pol_ledger_aged,
              p.pow_blend_difficulty, p.pol_epoch_nonce, p.pol_t0, p.pol_t1)
    return hash(b"BLEND_EPOCH_V1", epoch.to_bytes(4, "little"),
                *(field_element(x) for x in inputs))
```

- The epoch-change list validates the proof of quota of each message against the public input of the epoch of the connection it arrived on: the new epoch's from `T_S` before the epoch begins, and the past epoch's until the end of the Transition Period. It processes new messages on the connections of the new epoch.
- §Releasing: a received or processed message is released only on connections of the epoch of the connection it arrived on, and a generated message only on connections of the epoch it was generated in.
- Connectivity Maintenance item 1 loses the last-round exemption: every invalid proof of quota closes the connection and blacklists the neighbor, as Relaying step 6 now says.
- Bootstrapping: core nodes retrieve the core nodes of an epoch, and build its network, `T_S` before it begins.
- The nullifier cache keeps an entry until the Transition Period after the epoch of its message ends, and its size bound is $`(E + T_S + T)`$ times the message rate.
- Notation gains `T_S`, the clock slack, in seconds.

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

- [ ] Name an epoch's Blend connections `/logos-blockchain/<fork_digest>/blend/<epoch_digest>`, the epoch digest taken over the epoch number and the nine proof-of-quota public inputs fixed for the epoch
- [ ] From `T_S` = 2 seconds before a Blend epoch begins by the local clock, open its connections and accept those of neighbors, counted towards the degree rules apart from the current epoch's; retrieve its core nodes and take its SDP snapshot by then
- [ ] Validate each message, edge messages included, against the epoch of its connection, and send it only on connections of that epoch; do not add the one-round release delay, and blacklist on any invalid proof of quota
- [ ] Keep a nullifier until the Transition Period after its message's epoch ends
- [ ] Open the next era's identifiers and subscribe to its topics `T_S` before the boundary, and keep the previous era's until `T` rounds after it; a node that starts during the period runs only the new era
- [ ] Validate the mempool against the era in force `T_S` ahead, and re-validate it when that era changes
- [ ] Add tests that switch epochs and eras with node clocks up to `T_S` apart, including gossip and Blend messages from a node whose clock runs ahead, a next-epoch message an attacker sends as a node's window opens, and nodes whose epoch inputs differ
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | clock slack at every epoch: per-epoch protocol names from the epoch digest, early connections counted apart, messages sent only on connections of their epoch, bootstrapping and the nullifier cache; one-round clock bound and last-round exemption from blacklisting removed |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Era Transition Period from the clock slack before the boundary; mempool under the era in force that slack ahead; a node starting during the period runs only the new era |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | snapshot taken the clock slack before its epoch |
