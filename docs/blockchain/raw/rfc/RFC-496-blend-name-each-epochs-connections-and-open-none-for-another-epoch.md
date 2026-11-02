# [RFC] Blend: Name each epoch's connections and open none for another epoch

**Motivation and proposal:** [PR #496](https://github.com/logos-co/logos-lips/pull/496)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-22 |

## Reviewer Orientation

Read the PR's Motivation first. Each Blend epoch gets its own protocol name, so a connection shows its epoch, and a node opens and accepts connections only of its current epoch.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Blend Protocol](../blend-protocol.md), [details](#1-epoch-connections) | the epoch digest in the protocol name, and what it binds; connections opened and accepted only for the current epoch; each message validated against, and released only on, connections of its epoch; the one-round release delay and the last-round exemption from blacklisting removed; the new reason for keeping honest clocks within one round |
| 2 | Low | [Bedrock Eras](../bedrock-eras.md), [details](#2-era-boundary-walk) | the boundary walk without the release delay |

# Discussion

## A connection's epoch

At an epoch change, a node keeps the past epoch's connections only to deliver the messages in flight, and makes new connections for the new epoch. All epochs of an era share one protocol name, though, so a node tells a connection's epoch only by when the connection was made. A connection made between a node whose clock has switched and one whose clock has not is filed under the new epoch at one end and under the past epoch at the other. One end counts it towards its degree and keeps it after the Transition Period, and the other closes it when the period ends. Validating every message against both epochs during the period hides the mismatch for messages, but not for the connection.

With the epoch digest in the protocol name, both ends agree. A node that has switched refuses the past epoch's name, and a node that has not refuses the new epoch's.

## What the digest binds

The next epoch's public input, which includes the epoch nonce, the membership snapshot and the Blend difficulty, is fixed before the epoch begins. Every node can therefore compute the name. The digest binds every proof-of-quota public input fixed for the epoch, not only the epoch number. Nodes whose inputs differ, such as nodes on different forks, then never connect, and no longer blacklist each other for proofs that are valid only on their own fork. The signing key and the nullifier change with each message, so the digest leaves them out.

## The two rules removed

Two rules covered a new-epoch message reaching a node whose clock had not switched yet:

- a node released a message it generated in a new epoch only one round after its own epoch changed, with honest clocks within one round;
- in an epoch's last round, a next-epoch proof of quota did not get its sender blacklisted, which protected an honest node that had just switched and relayed such a message at once.

Neither situation can occur now. A new-epoch message travels only on new-epoch connections, and a node opens or accepts those only once its own epoch has changed. A next-epoch proof on a current-epoch connection can only come from a node that breaks the release rule, so it gets the normal reaction.

## Clocks

Honest clocks must still differ by less than one round, for a new reason. After a node's epoch changes, its neighbors whose clocks run behind refuse its new-epoch connections until their own epoch changes, and the messages it generates meanwhile reach none of them. These refusals are transient: they last at most the clock difference, and in a larger network it is less likely that every candidate neighbor refuses.

## Compatibility

No network runs these rules yet. The implementation keeps a past epoch's connections only for the Transition Period, opens new connections for the new epoch, validates a message against the epoch of the connection it arrives on, and closes its edge connections at the switch. It has neither the one-round release delay nor the last-round exemption. Its protocol name has no epoch part.

## Open questions

- A node builds each epoch's network from scratch. Until its neighbors have switched and the handshakes have completed, it holds no connection of the new epoch, and the messages it generates in that time reach no neighbor. Opening the next epoch's connections shortly before the epoch begins would close this gap.
- An edge node whose clock runs behind is refused by core nodes that have switched, and retries another core node within its retry budget.

# Details

## 1. Epoch connections

[Blend Protocol](../blend-protocol.md) §Connection Details:

```diff
-The libp2p protocol name is `/logos-blockchain/<fork_digest>/blend` ([Network Protocol Identity](bedrock-eras.md#network-protocol-identity)).
+The libp2p protocol name of the connections of an epoch is `/logos-blockchain/<fork_digest>/blend/<epoch_digest>` ([Network Protocol Identity](bedrock-eras.md#network-protocol-identity)), with `<epoch_digest>` the [epoch digest](#epoch-digest) of the epoch in lowercase hexadecimal.
```

A new §Epoch Digest defines it:

```python
def epoch_digest(epoch: EpochNumber, p: ProofOfQuotaPublic) -> hash:
    inputs = (p.core_quota, p.leader_quota, p.core_root, p.pow_quota, p.pol_ledger_aged,
              p.pow_blend_difficulty, p.pol_epoch_nonce, p.pol_t0, p.pol_t1)
    return hash(b"BLEND_EPOCH_V1", epoch.to_bytes(4, "little"),
                *(field_element(x) for x in inputs))
```

§Transition Period:

```diff
-Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. A node releases a message it generates in the new epoch no earlier than one round after its own epoch changes ([Releasing](#releasing)). With a larger $`T_C`$, such a message can reach a node whose clock runs behind before that node's epoch changes, and that node discards it.
+A node opens and accepts connections only of its current epoch, by its local clock ([Connection Details](#connection-details)). Nodes must keep their clocks synchronized so that $`T_C`$ is below one round. Otherwise the neighbors whose clocks run behind a node can refuse its connections of the new epoch for more than a round after its epoch changes, and the messages it generates in that time reach none of them.
```

- The epoch-change list validates the proof of quota of each message against the public input of the epoch of the connection it arrived on, the past epoch's until the end of the Transition Period, and processes new messages on the connections of the new epoch.
- §Releasing: a received or processed message is released only on connections of the epoch of the connection it arrived on, and a generated message only on connections of the epoch it was generated in.
- §Connectivity Maintenance, Blacklist rule 1, loses the last-round exemption, so every invalid proof of quota closes the connection and blacklists the neighbor.

## 2. Era boundary walk

[Bedrock Eras](../bedrock-eras.md) §An Era Boundary Step by Step: step 8 no longer delays a generated Blend message by one round.

## Chores

- Revision-history rows added to Blend Protocol and Bedrock Eras.

# Implementation

- [ ] Name an epoch's Blend connections `/logos-blockchain/<fork_digest>/blend/<epoch_digest>`, the epoch digest taken over the epoch number and the nine proof-of-quota public inputs fixed for the epoch
- [ ] Open and accept Blend connections only under the protocol name of the current epoch, and keep the past epoch's for the Transition Period
- [ ] Validate each message, edge messages included, against the epoch of its connection, and release it only on connections of that epoch
- [ ] Blacklist on every invalid proof of quota, and add no release delay after an epoch change
- [ ] Add tests that switch epochs with node clocks up to one round apart, including a next-epoch message an attacker sends to a node that has just switched, and nodes whose epoch inputs differ
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | per-epoch protocol names from the epoch digest; connections only of the current epoch; messages validated against, and released only on, connections of their epoch; one-round release delay and last-round exemption from blacklisting removed |
| [Bedrock Eras](../bedrock-eras.md) | Modified | boundary walk without the release delay |
