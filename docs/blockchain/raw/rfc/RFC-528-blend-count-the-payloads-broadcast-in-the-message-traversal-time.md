# [RFC] Blend: Count the payload's broadcast in the message traversal time

**Motivation and proposal:** [PR #528](https://github.com/logos-co/logos-lips/pull/528)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |
| v2 | The transition period keeps the form the base now gives it, the larger of `⌊1/f⌋` and `T_M + 1` rounds, as the implementation computes it, so this RFC changes only the message traversal time `T_M`. Removed: the transition period of `T_M + 1` rounds, the reasoning for one round, and the alternatives for the transition period. Renamed from "Derive the transition period from the message traversal time", with the document's file. | 2026-11-10 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then the [Transition Period](../blend-protocol.md#transition-period) section of the [Blend Protocol](#affected-specifications). Check that [the traversal time counts every sending](#1-the-message-traversal-time-counts-every-sending). [What the change moves](#what-the-change-moves) lists the rules that read it.

# Discussion

## What the change moves

| Settings | Traversal time `T_M` | Transition period `T` |
| --- | --- | --- |
| Reference: β_max = 3, Δ_max = 3, η = 2, f = 1/30 | 15 → 17 rounds | 30 rounds, unchanged |
| One layer, Δ_max = 1, η = 2, f = 1/20, as in the implementation's era schedule | 3 → 5 rounds | 20 rounds, unchanged |
| Reference Blend settings, f = 1/10 | 15 → 17 rounds | 16 → 18 rounds |

`T` changes only where `T_M + 1` exceeds `⌊1/f⌋`. These rules read `T_M` and move with it:

- [Detection](../blend-protocol.md#detection) and [Direct Broadcast](../blend-protocol.md#direct-broadcast): a sender waits `T_M` before it broadcasts an undelivered payload itself, 2 rounds longer at the reference values.
- [Block Proposal Reconstruction](../bedrock-v1.1-block-construction.md#block-proposal-reconstruction) assumes the same delay for the transactions a proposal references.
- Where `T_M + 1` sets the transition period: the proof-of-quota nullifiers a node keeps for an epoch plus `T`, the release of active messages after the next epoch's transition period, and the [Era Transition Period](../bedrock-eras.md#era-transition-period), which lasts the previous era's `T`.

## Alternative

A separate broadcast delay could replace the final `η`, for the network the payload is broadcast on. That network holds all nodes and runs another protocol. A separate value would need a measurement and a new field in the era record.

## Compatibility

No encoding changes, so no fork digest changes. The change moves the detection deadline at every setting, and the transition period only where `T_M + 1` sets it. Bedrock has no deployed network, so the change needs no migration. The implementation's traversal time leaves out the broadcast, and it has no delivery-failure detection yet ([Implementation](#implementation)).

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

The worked value of the transition period follows:

```diff
-T = max(⌊1/f⌋, T_M + 1) = max(30, 16) = 30 rounds
+T = max(⌊1/f⌋, T_M + 1) = max(30, 18) = 30 rounds
```

In [Global Parameters](../blend-protocol.md#global-parameters):

```diff
-- T_M = 15 rounds, the message traversal time, as derived in the Transition Period section.
+- T_M = 17 rounds, the message traversal time, as derived in the Transition Period section.
```

# Implementation

- [ ] In `max_data_message_delay_in_rounds` (`services/blend/src/settings/mod.rs`), add the broadcast: `num_blend_layers · (maximum_release_delay_in_rounds + network_absorption_in_rounds) + network_absorption_in_rounds`. `epoch_transition_slots` (`nodes/node/binary/src/config/deployment/era/ruleset/v1/blend/mod.rs`) reads it for the floor `T_M + 1`.
- [ ] Time the delivery-failure detection, once it is implemented, with that `T_M`.
- [ ] Add tests: `T_M` is 17 rounds at the reference settings and 5 at one layer with a blending delay of 1 round and a dissemination delay of 2 rounds; `T` is 18 rounds at the reference Blend settings with `f` = 1/10.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.10.0 |
