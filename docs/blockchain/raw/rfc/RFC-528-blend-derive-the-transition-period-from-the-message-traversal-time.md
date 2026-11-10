# [RFC] Blend: Derive the transition period from the message traversal time

**Motivation and proposal:** [PR #528](https://github.com/logos-co/logos-lips/pull/528)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then the [Transition Period](../blend-protocol.md#transition-period) section of the [Blend Protocol](#affected-specifications). Check that [the traversal time counts every sending](#1-the-message-traversal-time-counts-every-sending) and that [the transition period covers the clock difference](#2-the-transition-period-is-the-traversal-time-plus-one-round). [What the change moves](#what-the-change-moves) lists the rules that read both values.

# Discussion

## What the change moves

| Settings | Traversal time `T_M` | Transition period `T` |
| --- | --- | --- |
| Reference: β_max = 3, Δ_max = 3, η = 2 | 15 → 17 rounds | 30 → 18 rounds |
| One layer, Δ_max = 1, η = 2, as in the implementation's era schedule | 3 → 5 rounds | 30 → 6 rounds |

These rules read the two values, and move with them:

- [Detection](../blend-protocol.md#detection) and [Direct Broadcast](../blend-protocol.md#direct-broadcast): a sender waits `T_M` before it broadcasts an undelivered payload itself, 2 rounds longer at the reference values.
- [Block Proposal Reconstruction](../bedrock-v1.1-block-construction.md#block-proposal-reconstruction) assumes the same delay for the transactions a proposal references.
- A node keeps the PoQ nullifiers it relays for one epoch plus `T`, 12 rounds less at the reference values.
- An active message is released after the next epoch's transition period, 12 rounds earlier.
- The [Era Transition Period](../bedrock-eras.md#era-transition-period) lasts the previous era's `T`, measured in time: 18 rounds in place of 30 when the slot length does not change.

## Why one round

Blend requires `T ≥ T_M + T_C`, and the clock difference `T_C` between two honest nodes below one round. `T_M + 1` is the smallest whole number of rounds that meets both. It leaves no margin. If a sending takes longer than `η` to reach every node, or a blend node holds a message longer than `Δ_max`, the slowest messages of the past epoch are dropped.

## Alternatives

- **`T = 2·T_M`**, 34 rounds at the reference values. It follows the Blend settings and leaves a margin, but the factor 2 has no stated target.
- **`T = ⌊1/f⌋` slots**, which the implementation uses: 30 at the reference values. It follows the block rate rather than the Blend settings. At `f = 1/10` it gives 10 rounds, against a traversal time of 17.
- **A separate broadcast delay** in place of the final `η`, for the network the payload is broadcast on. That network holds all nodes and runs another protocol. A separate value would need a measurement and a new field in the era record.

## Compatibility

No encoding changes, so no fork digest changes. The values change the timing of every node. Bedrock has no deployed network, so the change needs no migration. The implementation computes `T` from the block rate and has no delivery-failure detection yet ([Implementation](#implementation)).

# Details

## 1. The message traversal time counts every sending

In the [Transition Period](../blend-protocol.md#transition-period), `T_M` counts the broadcast of the payload, a sending that the old formula left out:

```diff
-A message crosses β_max blend nodes, each holding it for at most Δ_max and the network
-carrying it for η:
-
-T_M = β_max · (Δ_max + η) = 3 · (3 + 2) = 15 rounds
+A message is sent by its sender and by each of the β_max blend nodes it crosses, the
+last of which sends its payload to every node (Broadcasting). Each sending reaches every
+node within η, and each blend node holds the message for at most Δ_max:
+
+T_M = β_max · (η + Δ_max) + η = 3 · (2 + 3) + 2 = 17 rounds
```

In [Global Parameters](../blend-protocol.md#global-parameters):

```diff
-- T_M = 15 rounds, the message traversal time, as derived in the Transition Period section.
+- T_M = 17 rounds, the message traversal time, as derived in the Transition Period section.
```

## 2. The transition period is the traversal time plus one round

In the [Transition Period](../blend-protocol.md#transition-period), `T` follows from `T_M` in place of a fixed 30 rounds. The consequence of a larger clock difference moves to the paragraph that bounds it:

```diff
-After T_M rounds, all messages for the past epoch should have been processed and
-disseminated. To provide an additional safety buffer, we round the transition period up
-to T=30 rounds. After this period, all old connections can be safely terminated, and
-messages for the past epoch must not be processed anymore.
-
-The transition period must be at least the message traversal time plus the largest clock
-difference between two honest nodes: T ≥ T_M + T_C. Otherwise a node whose clock runs
-ahead stops processing past-epoch messages while some are still crossing the network, and
-their senders wait for a delivery that can no longer happen (Detection).
+The transition period is the message traversal time plus one round:
+
+T = T_M + 1 = 18 rounds
+
+After this period, all old connections can be safely terminated, and messages for the
+past epoch must not be processed anymore.

-Nodes must keep their clocks synchronized so that T_C is below one round. A node releases
-a message it generates in the new epoch no earlier than one round after its own epoch
-changes (Releasing). With a larger T_C, such a message can reach a node whose clock runs
-behind before that node's epoch changes, and that node discards it.
+Nodes must keep their clocks synchronized so that T_C is below one round. T then exceeds
+T_M + T_C. With a larger T_C, a node whose clock runs ahead can stop processing past-epoch
+messages while some are still crossing the network, and their senders wait for a delivery
+that can no longer happen (Detection). A node releases a message it generates in the new
+epoch no earlier than one round after its own epoch changes (Releasing). With a larger
+T_C, such a message can also reach a node whose clock runs behind before that node's epoch
+changes, and that node discards it.
```

# Implementation

- [ ] In `epoch_transition_slots` (`nodes/node/binary/src/config/deployment/era/ruleset/v1/blend/mod.rs`), compute `T = num_blend_layers · (network_absorption_in_rounds + maximum_release_delay_in_rounds) + network_absorption_in_rounds + 1` rounds, in place of the slots per block. `era_transition_slots` (`nodes/node/binary/src/config/deployment/era/ruleset/mod.rs`) then no longer passes the slots per block.
- [ ] Time the delivery-failure detection, once it is implemented, with `T_M = num_blend_layers · (network_absorption_in_rounds + maximum_release_delay_in_rounds) + network_absorption_in_rounds` rounds.
- [ ] Add tests: `T` is 18 rounds at the reference settings and 6 at one layer with a blending delay of 1 round and a dissemination delay of 2 rounds.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.10.0 |
