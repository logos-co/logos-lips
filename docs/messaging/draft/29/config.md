# 29/WAKU2-CONFIG

| Field | Value |
| --- | --- |
| Name | Waku v2 Client Parameter Configuration Recommendations |
| Slug | 29 |
| Status | draft |
| Type | RFC |
| Category | Informational |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/messaging/informational/29/config.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/informational/29/config.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/informational/29/config.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/informational/29/config.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/informational/29/config.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/informational/29/config.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/informational/29/config.md) — ci: add mdBook configuration (#233)
- **2025-04-22** — [`7408956`](https://github.com/logos-co/logos-lips/blob/740895661662ac5f73a8bce726333d93acf5fa23/waku/informational/29/config.md) — update waku/informational/29/config.md (#146)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/informational/29/config.md) — Fix Files for Linting (#94)
- **2024-01-31** — [`c506eac`](https://github.com/logos-co/logos-lips/blob/c506eac87d37bf264fa001e83b80477bd93ca727/waku/informational/29/config.md) — Update and rename CONFIG.md to config.md
- **2024-01-31** — [`930f84d`](https://github.com/logos-co/logos-lips/blob/930f84d4bfc5095db197d78dde2d4dcc36739794/waku/informational/29/CONFIG.md) — Update and rename README.md to CONFIG.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/informational/29/README.md) — remove rfs folder
- **2024-01-25** — [`e6396b9`](https://github.com/logos-co/logos-lips/blob/e6396b9b8a0807d134caf8905e903731160fdcf0/waku/rfcs/informational/29/README.md) — Create README.md

<!-- timeline:end -->

`29/WAKU2-CONFIG` describes the RECOMMENDED values
to assign to configurable parameters for Waku v2 clients.
Since Waku v2 is built on [libp2p](https://github.com/libp2p/specs),
most of the parameters and reasonable defaults are derived from there.

Waku v2 relay messaging is specified in [`11/WAKU2-RELAY`](/messaging/stable/11/relay.md),
a minor extension of the [libp2p GossipSub protocol](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/README.md).
GossipSub behaviour is controlled by a series of adjustable parameters.
Waku v2 clients SHOULD configure these parameters to the recommended values below.

## GossipSub v1.0 parameters

GossipSub v1.0 parameters are defined in the [corresponding libp2p specification](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.0.md#parameters).
We repeat them here with RECOMMMENDED values for `11/WAKU2-RELAY` implementations.

| Parameter            | Purpose                                               | RECOMMENDED value |
|----------------------|-------------------------------------------------------|-------------------|
| `D`                  | The desired outbound degree of the network            | 6                 |
| `D_low`              | Lower bound for outbound degree                       | 4                 |
| `D_high`             | Upper bound for outbound degree                       | 8                 |
| `D_lazy`             | (Optional) the outbound degree for gossip emission    | `D`               |
| `heartbeat_interval` | Time between heartbeats                               | 1 second          |
| `fanout_ttl`         | Time-to-live for each topic's fanout state            | 60 seconds        |
| `mcache_len`         | Number of history windows in message cache            | 5                 |
| `mcache_gossip`      | Number of history windows to use when emitting gossip | 3                 |
| `seen_ttl`           | Expiry time for cache of seen message ids             | 2 minutes         |

## GossipSub v1.1 parameters

GossipSub v1.1 extended GossipSub v1.0 and
introduced [several new parameters](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#overview-of-new-parameters).
We repeat the global parameters here
with RECOMMMENDED values for `11/WAKU2-RELAY` implementations.

| Parameter      | Description                                                            | RECOMMENDED value |
|----------------|------------------------------------------------------------------------|-------------------|
| `PruneBackoff` | Time after pruning a mesh peer before we consider grafting them again. | 1 minute          |
| `FloodPublish` | Whether to enable flood publishing                                     | true              |
| `GossipFactor` | % of peers to send gossip to, if we have more than `D_lazy` available  | 0.25              |
| `D_score`      | Number of peers to retain by score when pruning from oversubscription  | `D_low`           |
| `D_out`        | Number of outbound connections to keep in the mesh.                    | `D_low` - 1       |

`11/WAKU2-RELAY` clients SHOULD implement a peer scoring mechanism
with the parameter constraints as
[specified by libp2p](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#overview-of-new-parameters).

## Other configuration

The following behavioural parameters are not specified by `libp2p`,
but nevertheless describes constraints that `11/WAKU2-RELAY` clients
MAY choose to implement.

| Parameter          | Description                                                               | RECOMMENDED value |
|--------------------|---------------------------------------------------------------------------|-------------------|
| `BackoffSlackTime` | Slack time to add to prune backoff before attempting to graft again       | 2 seconds         |
| `IWantPeerBudget`  | Maximum number of IWANT messages to accept from a peer within a heartbeat | 25                |
| `IHavePeerBudget`  | Maximum number of IHAVE messages to accept from a peer within a heartbeat | 10                |
| `IHaveMaxLength`   | Maximum number of messages to include in an IHAVE message                 | 5000              |

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p](https://github.com/libp2p/specs)
- [11/WAKU2-RELAY](/messaging/stable/11/relay.md)
- [libp2p GossipSub protocol](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/README.md)
- [corresponding libp2p specification](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.0.md#parameters)
- [several new parameters](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#overview-of-new-parameters)
