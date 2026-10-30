# [RFC] Blend: Derive M_W from expected deliveries

**Motivation and proposal:** [PR #510](https://github.com/logos-co/logos-lips/pull/510)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-30 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the derivation of `M_W`](#1-m_w-is-derived-from-the-expected-deliveries) in the Global Parameters of the [Blend Protocol](#affected-specifications). Check the share of messages a neighbor delivers, which turns `λ` into `M_W` ([Discussion](#the-share-a-neighbor-delivers)), and that no deployment's window changes ([Compatibility](#compatibility)).

# Discussion

## The share a neighbor delivers

A neighbor sends a node every message except the ones it first received from that node. Suppose each connection of the neighbor is equally likely to bring a message first. With `d` connections, one message in `d` then reaches the neighbor first from the node, and the neighbor delivers the rest: the share `(d − 1)/d` of what the connection carries. A neighbor holds at least `Φ_CC − 1` connections, so the share is at least `(Φ_CC − 2)/(Φ_CC − 1)`, and `M_W` messages carry at least `λ` deliveries:

| `Φ_CC` | Share | `M_W` | `W` at the reference parameters | `W` on the testnet | Deliveries with `M_W` fixed at 90 |
| --- | --- | --- | --- | --- | --- |
| 3 | 1/2 | 120 | 40 | 120 | 45 |
| 4 | 2/3 | 90 | 30 | 90 | 60 |
| 5 | 3/4 | 80 | 27 | 80 | 67.5 |

For deliveries arriving at random, a window that expects `n` deliveries holds none with probability `e^−n`. A gap of `W` rounds then comes on average every `(e^n − 1)·W/n` rounds, which at `n = 60` is over 10⁵ years per connection. `λ = 60` keeps `M_W` at 90 at a peering degree of 4.

Only `W` is rounded, up, so a window carries at least `M_W` messages. Rounding `M_W` up as well would not raise this bound. It can add a round when neither `M_W` nor the cover traffic of a round is a whole number.

## How far the model holds

The model is crude, and how far it holds is an open question. Three effects make false readings more frequent than it predicts:

- **Grouped releases.** At three layers, the releases of a cover message arrive within a few rounds of each other. A reference window therefore holds 30 independent cover messages rather than 90 independent releases. A slow node that receives nearly every message first from one fast neighbor forwards little back to it. If it forwards a tenth of the messages, the fast neighbor reads it as not live about every 4 hours at the reference parameters, against 7.5 hours for independent arrivals. On the testnet, with one layer and `W = 90`, it is about every 22.5 hours.
- **Uneven shares.** Latency makes some links deliver far less than two thirds. In a simulation of flooding over 1,000 nodes connected by the Degree rules, with varied latencies and a tenth of the nodes slow, the mean share was 0.79, but 1% of links delivered less than 0.4.
- **Offline nodes.** A declared node that is offline emits nothing. At three layers it also stops the later releases of every message routed through it. With half the declared nodes offline, a reference window still expects about 17 deliveries, and the simulation gives each node a false reading about every 12 hours.

Each false reading closes the connection and refuses the neighbor for `W` rounds.

## Alternatives

- **A fixed `M_W`.** `M_W = 90` gives the same windows today, but it states no target. A deployment with another peering degree gets another number of deliveries per window: 45 at `Φ_CC = 3` and 67.5 at `Φ_CC = 5`.
- **Counting cover messages instead of their releases.** This follows the grouped releases at three layers. With the reference window kept at 30 rounds, it would also give the one-layer testnet 30 rounds. A neighbor that forwards a tenth of the messages would then be read as not live about every 3 minutes instead of every 22.5 hours.
- **Measuring the delivery rate at each node.** A node could size `W` from the messages it receives. That rate falls when the node's own neighbors go silent, so the window would grow exactly when the node needs to replace them. An average also lags behind an outage.

## Compatibility

The change is local to each node: no message, wire format or consensus rule changes. Every deployment uses a peering degree of 4, so `M_W` stays 90, no window changes, and nodes following 1.8.0 and 1.8.1 interoperate. A deployment with another peering degree gets another `M_W`, and with it another `W`. Bedrock has no deployed network, so the change needs no migration.

# Details

## 1. `M_W` is derived from the expected deliveries

In Notation, `λ` is added:

```diff
 M_W denote the number of messages a core connection carries from cover traffic alone
 in an observation window;
+λ denote the number of messages a neighbor is expected to deliver to a node in an
+observation window;
```

In Global Parameters, `M_W` follows from `λ` and the peering degree, and the effects of a larger value move from `M_W` to `λ`. `W` keeps its formula, so only `W` is rounded:

```diff
 W = ⌈M_W / (F_C·(1 + R_C)·β_C)⌉ = 30 rounds, the observation window: the rounds in which
 a core connection carries M_W messages from cover traffic alone.
-M_W = 90 messages. With a smaller M_W, a node more often reads an honest neighbor as not
-live and closes its connection. With a larger one, a neighbor that delivers nothing
-holds a connection slot for longer, a neighbor closed as not live is refused for longer,
-and a blacklist entry lasts longer.
+M_W = λ·(Φ_CC − 1) / (Φ_CC − 2) = 90 messages. A neighbor sends a node every message
+except the ones it first received from that node. A neighbor holds at least Φ_CC − 1
+connections, so on average at most one message in Φ_CC − 1 reaches it first from that
+node.
+λ = 60 messages. For deliveries arriving at random, an honest neighbor delivers nothing
+within W rounds with probability at most e^−λ, and is closed as not live. A larger λ
+lengthens W: a neighbor that delivers nothing holds a connection slot for longer, a
+neighbor closed as not live is refused for longer, and a blacklist entry lasts longer.
```

# Implementation

- [ ] Replace `cover_messages_per_observation_window` in the Blend `CoreSettings` with `λ`, 60 in every deployment. In `rounds_per_observation_window` (`nodes/node/binary/src/config/deployment/era/ruleset/v1/blend/mod.rs`), compute `W = ⌈λ·(Φ_CC − 1) / ((Φ_CC − 2)·message_frequency_per_round·num_blend_layers)⌉` with `Φ_CC` from `target_peering_degree`, rounding once. No deployment replicates cover messages, so `R_C = 0`.
- [ ] Add tests: the window is 30 rounds at the reference settings and 90 at the testnet's, and `M_W` is 120, 90 and 80 at a peering degree of 3, 4 and 5.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.8.1 |
