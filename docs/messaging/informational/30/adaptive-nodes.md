# 30/ADAPTIVE-NODES

| Field | Value |
| --- | --- |
| Name | Adaptive nodes |
| Slug | 30 |
| Status | draft |
| Type | RFC |
| Category | Informational |
| Editor | Oskar Thorén <oskarth@titanproxy.com> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/informational/30/adaptive-nodes.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/informational/30/adaptive-nodes.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/informational/30/adaptive-nodes.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/informational/30/adaptive-nodes.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/informational/30/adaptive-nodes.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/informational/30/adaptive-nodes.md) — ci: add mdBook configuration (#233)
- **2025-04-29** — [`91c9679`](https://github.com/logos-co/logos-lips/blob/91c9679bc89f146e6f50a2bb3a26fe4d5daa1ade/waku/informational/30/adaptive-nodes.md) — update waku/informational/30/adaptive-nodes.md (#147)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/informational/30/adaptive-nodes.md) — Fix Files for Linting (#94)
- **2024-01-31** — [`b35846a`](https://github.com/logos-co/logos-lips/blob/b35846a546c1a6dc4bac3d5e5457f812f56c7707/waku/informational/30/adaptive-nodes.md) — Update and rename README.md to adaptive-nodes.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/informational/30/README.md) — remove rfs folder
- **2024-01-25** — [`04036ad`](https://github.com/logos-co/logos-lips/blob/04036adcabf888f6ca764b50680694b07539e89d/waku/rfcs/informational/30/README.md) — Create README.md

<!-- timeline:end -->

This is an informational spec that show cases the concept of adaptive nodes.

## Node types - a continuum

We can look at node types as a continuum,
from more restricted to less restricted,
fewer resources to more resources.

![Node types - a continuum](images/adaptive_node_continuum2.png)

### Possible limitations

- Connectivity: Not publicly connectable vs static IP and DNS
- Connectivity: Mostly offline to mostly online to always online
- Resources: Storage, CPU, Memory, Bandwidth

### Accessibility and motivation

Some examples:

- Opening browser window: costs nothing, but contribute nothing
- Desktop: download, leave in background, contribute somewhat
- Cluster: expensive, upkeep, but can contribute a lot

These are also illustrative,
so a node in a browser in certain environment might contribute similarly to Desktop.

### Adaptive nodes

We call these nodes *adaptive nodes* to highlights different modes of contributing,
such as:

- Only leeching from the network
- Relaying messages for one or more topics
- Providing services for lighter nodes such as lightpush and filter
- Storing historical messages to various degrees
- Ensuring relay network can't be spammed with RLN

### Planned incentives

Incentives to run a node is currently planned around:

- SWAP for accounting and settlement of services provided
- RLN RELAY for spam protection
- Other incentivization schemes are likely to follow and is an area of active research

## Node protocol selection

Each node can choose which protocols to support, depending on its resources and goals.

![Protocol selection](images/adaptive_node_protocol_selection2.png)

Protocols like [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md),
as well as [12], [13], [19], and [21], correspond to libp2p protocols.

However, other protocols like 16/WAKU2-RPC
(local HTTP JSON-RPC), 25/LIBP2P-DNS-DISCOVERY,
Discovery v5 (DevP2P) or interfacing with distributed storage,
are running on different network stacks.

This is in addition to protocols that specify payloads, such as 14/WAKU2-MESSAGE,
26/WAKU2-PAYLOAD, or application specific ones.
As well as specs that act more as recommendations,
such as 23/WAKU2-TOPICS or 27/WAKU2-PEERS.

## Waku network visualization

We can better visualize the network with some illustrative examples.

### Topology and topics

This illustration shows an example topology with different PubSub topics
for the relay protocol.

![Waku Network visualization](images/adaptive_node_network_topology_protocols2.png)

### Legend

This illustration shows an example of content topics a node is interested in.

![Waku Network visualization legend](images/adaptive_node_network_topology_protocols_legend.png)

The dotted box shows what content topics (application-specific)
a node is interested in.

A node that is purely providing a service to the network might not care.

In this example, we see support for toy chat,
a topic in Waku v1 (Status chat), WalletConnect, and SuperRare community.

### Auxiliary network

This is a separate component with its own topology.

Behavior and interaction with other protocols specified in Logos LIPs,
e.g. [25/LIBP2P-DNS-DISCOVERY](/anoncomms/deleted/25/libp2p-dns-discovery.md)
and [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md).

### Node Cross Section

This one shows a cross-section of nodes in different dimensions and
shows how the connections look different for different protocols.

![Node Cross Section](images/adaptive_node_cross_section2.png)

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)
- [25/LIBP2P-DNS-DISCOVERY](/anoncomms/deleted/25/libp2p-dns-discovery.md)
- [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md)
