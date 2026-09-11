# P2P-NETWORK

| Field | Value |
| --- | --- |
| Name | P2P Network |
| Slug | 135 |
| Status | draft |
| Type | RFC |
| Category | networking |
| Editor | Daniel Sanchez-Quiros <danielsq@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/draft/p2p-network.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/draft/p2p-network.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-05-11** — [`1ac7689`](https://github.com/logos-co/logos-lips/blob/1ac7689ee3fe1665d5d5d1bf9c180ed951cc660d/docs/blockchain/draft/p2p-network.md) — chore: split ift ts specs (#334)
- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/blockchain/raw/p2p-network.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/p2p-network.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/p2p-network.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/nomos/raw/p2p-network.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/nomos/raw/p2p-network.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/nomos/raw/p2p-network.md) — ci: add mdBook configuration (#233)
- **2025-09-25** — [`a3a5b91`](https://github.com/logos-co/logos-lips/blob/a3a5b91df3e06bb9ad737056ccd2c2f1fd20af3c/nomos/raw/p2p-network.md) — Created nomos/raw/p2p-network.md file (#169)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-01-20 |
| 1.0.1 | Rename Nomos to Logos Blockchain | 2026-04-17 |
| 1.1.0 | Protocol identifiers and gossipsub topics carry the era number in place of the version ([Bedrock Eras](../raw/bedrock-eras.md)). | 2026-09-04 |

# Introduction

The Logos Blockchain peer-to-peer (P2P) network serves as the comprehensive communication layer connecting Logos Blockchain nodes. Its primary functions include facilitating the mempool for transaction dissemination and enabling block propagation. This specification leverages established, publicly available protocols to ensure robust performance. The Logos Blockchain P2P network is designed to scale according to the project's requirements, supporting efficient communication with low bandwidth and minimal latency.

Participants, or peers, operating Logos Blockchain nodes encompass a diverse array of machine specifications, ranging from laptops to dedicated servers,  as well as various operating systems and geographic locations. A key priority is to streamline communication for non-technical users, ensuring accessibility. This entails enabling peers to remain reachable—ideally even with limited connectivity or when situated behind a router—thereby enhancing inclusivity and usability across the network.

# Overview

The Logos Blockchain network constitutes a foundational element of the communication infrastructure, addressing several critical challenges:

- **Peer Connectivity**: Establishing mechanisms for peers to join and connect to the network.
- **Peer Discovery**: Enabling peers to locate and identify other participants within the network.
- **Message Transmission**: Facilitating the efficient exchange of messages among peers across the network.

The Logos Blockchain network uses production-tested protocols to ensure all of the above is achieved.

# Network Protocols Details

## Transport

The Logos Blockchain network extensively leverages the [libp2p](https://docs.libp2p.io/) suite of plug-and-play protocols, which forms a foundational component for delivering the essential functionalities outlined previously.

At its core, the Logos Blockchain network employs the [*QUIC*](https://docs.libp2p.io/concepts/transports/quic/) transport protocol. QUIC provides rapid connection establishment and offers several advantages, including enhanced NAT traversal capabilities stemming from its UDP foundation. Additionally, its default multiplexing feature simplifies configuration processes.

## Peer Discovery

Following an evaluation of existing protocols and network requirements, the optimal approach for the Logos Blockchain is to leverage the established libp2p stack, incorporating libp2p-kad for peer discovery. This provides a robust, modular, and scalable solution that seamlessly integrates with other libp2p protocols (e.g., gossipsub, identify, ping), enabling support for large-scale, dynamic networks with eventual consistency and resilience.

The Logos Blockchain P2P network integrates a combination of libp2p's [Kademlia](https://docs.libp2p.io/concepts/discovery-routing/kaddht/) and [Identify](https://github.com/libp2p/specs/blob/master/identify/README.md) protocols to facilitate peer discovery. Kademlia enables the identification and connection to new peers by employing proximity-based heuristics, optimizing the discovery process. Complementing this, the Identify protocol supports the exchange of peer information, including details about the protocols each peer supports, thereby enhancing interoperability and network coordination.

The specific protocols to be negotiated are:

- Kademlia: `/logos-blockchain/<era>/kad` for mainnet and `/logos-blockchain-testnet/<era>/kad` for testnet.
- Identify: `/logos-blockchain/<era>/identify` and `/logos-blockchain-testnet/<era>/identify` for testnet.

`<era>` is defined in [Network Protocol Identity](../raw/bedrock-eras.md#network-protocol-identity).

The Logos Blockchain team acknowledges that the current Kademlia DHT implementation is only optimal for the V1 solution, as it is a heavier protocol for the limited utility the Logos Blockchain actually requires. However, it remains a viable interim approach. An ideal protocol would feature:

- A lightweight design, excluding the DHT which is of no use for the Logos Blockchain network.
- Lightweight and highly-scalable eventual consistency for network membership, supporting +10k nodes (ideally unbounded in practice).

This will be worked on in the future.

## NAT Traversal

Network Address Translation (NAT) poses a common challenge in peer-to-peer networks. The Logos Blockchain network prioritizes seamless, configuration-free connections among peers to accommodate participants with varying levels of technical expertise, ranging from none to advanced. Simplicity is a critical objective, given the goal of enabling nodes to operate on standard hardware, such as laptops.

To achieve this, the Logos Blockchain employs a tailored set of solutions adapted to the user's specific configuration. Comprehensive details are provided in the NAT Solution Specification.

[P2P Nat Solution](../raw/p2p-nat-solution.md)

## Gossiping

The Logos Blockchain leverages [`gossipsub`](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub) for its messaging capabilities. This works in combination with the above exposed [peer discovery protocol](p2p-network.md#peer-discovery) and [NAT traversal solution](p2p-network.md#nat-traversal) as they are members of the same libp2p stack. It automatically leverages `kademlia` connections to keep an updated list of available peers in the network.

Logos Blockchain gossiping uses two major topics. One dedicated to *mempool* and one for *block dissemination*:

- Mempool: `/logos-blockchain/<era>/mempool` for mainnet. `/logos-blockchain-testnet/<era>/mempool` for testnet.
- Blocks: `/logos-blockchain/<era>/cryptarchia` for mainnet. `/logos-blockchain-testnet/<era>/cryptarchia` for testnet.

  gossipsub is openly customizable but it is encouraged to have a peering degree of at least 8 peers.

## Bootstrapping

The Logos Blockchain P2P network is engineered for simplicity and ease of use. Upon initial connection, nodes in the network connect to publicly designated nodes to acquire the essential information required to become fully operational. Further details regarding this process are elaborated in the bootstrapping specification.

[P2P Network Bootstrapping](../raw/p2p-network-bootstrapping.md)

## Message Encoding

Messages that goes through wire follow a specific encoding scheme defined in the following specification.

[Network Wire Format](../raw/network-wire-format.md)
