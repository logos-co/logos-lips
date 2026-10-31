# [RFC] Blend: Size the observation window by cover traffic

**Motivation and proposal:** [PR #499](https://github.com/logos-co/logos-lips/pull/499)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-23 |
| v2 | Narrowed to the size of `W`: removed the refusal of a neighbor closed as not live, with its Details entry, its Discussion, its alternatives and its implementation tasks. Renamed the document from `RFC-499-blend-size-the-observation-window-by-cover-traffic-and-readmit-not-live-neighbors.md` to match the new title, and added a larger fixed `W` as an alternative. | 2026-10-23 |
| v3 | Merged master, which added Blend Protocol 1.6.2. Re-dated the 1.7.0 revision, and compared it with 1.6.2 in place of 1.6.1 in the window table and Compatibility. | 2026-10-27 |
| v4 | Named the constant `90` in `W` as the parameter `M_W`, and stated what a smaller and a larger value change. Re-dated the 1.7.0 revision, and corrected the path in the implementation task. | 2026-10-29 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the new `W`](#1-w-is-sized-by-cover-traffic) in the Global Parameters of the [Blend Protocol](#affected-specifications). Check that `W` stays 30 rounds at the reference parameters, and how many deliveries per window it gives where cover traffic is lower ([Discussion](#the-size-of-the-window)).

# Discussion

## The size of the window

The liveness test works only if an honest neighbor almost never goes `W` connected rounds without delivering. With no transactions, a core connection carries `F_C·(1 + R_C)·β_C` messages a round, one per blending operation of each cover message. Block proposals take the place of cover messages, and transactions add to them. A neighbor forwards each message to every neighbor except the one it received it from, so it delivers roughly half to three quarters of them to the node.

For deliveries arriving at random at a rate `λ` per round, the mean time before a gap of `W` rounds is `(e^(λW) − 1)/λ` rounds. For a neighbor that forwards half of the cover messages:

| Deployment | Cover messages per round | `W`, 1.6.2 → 1.7.0 | Deliveries expected per window | Mean time to a false reading per connection |
| --- | --- | --- | --- | --- |
| Reference | 3 | 30 → 30 | 45 → 45 | over 10⁵ years in both |
| Testnet (`F_C = 1`, one layer) | 1 | 10 → 90 | 5 → 45 | 4.9 min → over 10⁵ years |
| Testnet, if a third of its members emit nothing | 0.67 | 10 → 90 | 3.3 → 30 | 1.4 min → over 10⁵ years |

`M_W = 90` keeps `W` at 30 rounds at the reference parameters, so neither the liveness test nor the blacklist expiry changes there. A deployment with less cover traffic gets a proportionally longer window, and the same expected number of deliveries in it.

The model is crude, and how far it holds is an open question. Arrivals are not independent, and the share of messages a neighbor forwards depends on the topology and on latency. A slow node that receives nearly every message first from one fast neighbor forwards little back to that neighbor. If it forwards a tenth of the cover messages, the fast neighbor reads it as not live about every 7.5 hours at the reference parameters, and about every 22.5 hours on the testnet with the new `W`. Each such reading still shuts the slow node out of that neighbor for the rest of the epoch.

## Alternatives

- **A larger `Δ_max` on the testnet.** `W` becomes 30 rounds there, and a neighbor that forwards half of the cover messages delivers 15 per window. `W` still does not follow the traffic, so a deployment with fewer layers or less cover traffic fails the same way.
- **A larger fixed `W`.** `W = 90` everywhere also covers the testnet. It triples the reference window, the blacklist expiry and the time a dead neighbor holds a slot, which the reference rates do not need, and it still fails a deployment with less cover traffic than the testnet.

## Compatibility

The change is local to each node: no message, wire format or consensus rule changes, and nodes following 1.6.2 and 1.7.0 interoperate. Where cover traffic is lower than at the reference parameters, `W` grows, and with it the blacklist expiry and the time a dead neighbor holds a slot: 90 rounds on the testnet. Bedrock has no deployed network, so the change needs no migration.

# Details

## 1. `W` is sized by cover traffic

In Notation, `M_W` is added for the messages that size `W`:

```diff
 W denote the observation window expressed in the number of rounds;
+M_W denote the number of messages a core connection carries from cover traffic alone
+in an observation window;
```

In Global Parameters, `W` no longer depends on `Δ_max`. It keeps both of its uses, the liveness window and the blacklist expiry:

```diff
-W = 10·Δ_max = 30, the observation window is 30 rounds.
+W = ⌈M_W / (F_C·(1 + R_C)·β_C)⌉ = 30 rounds, the observation window: the rounds in which
+a core connection carries M_W messages from cover traffic alone.
+M_W = 90 messages. With a smaller M_W, a node more often reads an honest neighbor as not
+live and closes its connection. With a larger one, a neighbor that delivers nothing
+holds a connection slot for longer, and a blacklist entry lasts longer.
```

# Implementation

- [ ] Add `M_W` to the Blend `CoreSettings` as `cover_messages_per_observation_window`, 90 in every deployment. Compute the observation window as `⌈M_W / (message_frequency_per_round · num_blend_layers)⌉` in `rounds_per_observation_window` (`nodes/node/binary/src/config/deployment/era/ruleset/v1/blend/mod.rs`), in place of `10 · maximum_release_delay_in_rounds`. No deployment replicates cover messages, so `R_C = 0`. The testnet window becomes 90 rounds.
- [ ] Add tests: the window is 30 rounds at the reference settings and 90 at the testnet's.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.7.0 |
