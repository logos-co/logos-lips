# NOMOS-P2P-NETWORK

| Field | Value |
| --- | --- |
| Name | Nomos P2P Network Specification |
| Slug | 135 |
| Status | draft |
| Type | RFC |
| Category | networking |
| Editor | Daniel Sanchez-Quiros <danielsq@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/blockchain/draft/p2p-network.md) — chore: split ift ts specs
- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/blockchain/raw/p2p-network.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/p2p-network.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/p2p-network.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/nomos/raw/p2p-network.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/nomos/raw/p2p-network.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/nomos/raw/p2p-network.md) — ci: add mdBook configuration (#233)
- **2025-09-25** — [`a3a5b91`](https://github.com/logos-co/logos-lips/blob/a3a5b91df3e06bb9ad737056ccd2c2f1fd20af3c/nomos/raw/p2p-network.md) — Created nomos/raw/p2p-network.md file (#169)

<!-- timeline:end -->

## Abstract

This specification defines the peer-to-peer (P2P) network layer for Nomos blockchain nodes. The network serves as the comprehensive communication infrastructure enabling transaction dissemination through mempool and block propagation. The specification leverages established libp2p protocols to ensure robust, scalable performance with low bandwidth requirements and minimal latency while maintaining accessibility for diverse hardware configurations and network environments.

## Motivation

The Nomos blockchain requires a reliable, scalable P2P network that can:

1. **Support diverse hardware**: From laptops to dedicated servers across various operating systems and geographic locations
2. **Enable inclusive participation**: Allow non-technical users to operate nodes with minimal configuration
3. **Maintain connectivity**: Ensure nodes remain reachable even with limited connectivity or behind NAT/routers
4. **Scale efficiently**: Support large-scale networks (+10k nodes) with eventual consistency
5. **Provide low-latency communication**: Enable efficient transaction and block propagation

## Specification

### Network Architecture Overview

The Nomos P2P network addresses three critical challenges:

- **Peer Connectivity**: Mechanisms for peers to join and connect to the network
- **Peer Discovery**: Enabling peers to locate and identify network participants  
- **Message Transmission**: Facilitating efficient message exchange across the network

### Transport Protocol

#### QUIC Protocol Transport

The Nomos network employs **[QUIC protocol](https://docs.libp2p.io/concepts/transports/quic/)** as the primary transport protocol, leveraging the [libp2p protocol](https://docs.libp2p.io/) implementation.

**Rationale for [QUIC protocol](https://docs.libp2p.io/concepts/transports/quic/):**

- Rapid connection establishment
- Enhanced NAT traversal capabilities (UDP-based)
- Built-in multiplexing simplifies configuration
- Production-tested reliability

### Peer Discovery

#### Kademlia DHT

The network utilizes libp2p's Kademlia Distributed Hash Table (DHT) for peer discovery.

**Protocol Identifiers:**

- **Mainnet**: `/nomos/kad/1.0.0`
- **Testnet**: `/nomos-testnet/kad/1.0.0`

**Features:**

- Proximity-based peer discovery heuristics
- Distributed peer routing table
- Resilient to network partitions
- Automatic peer replacement

#### Identify Protocol

Complements Kademlia by enabling peer information exchange.

**Protocol Identifiers:**

- **Mainnet**: `/nomos/identify/1.0.0`
- **Testnet**: `/nomos-testnet/identify/1.0.0`

**Capabilities:**

- Protocol support advertisement
- Peer capability negotiation
- Network interoperability enhancement

#### Future Considerations

The current Kademlia implementation is acknowledged as interim. Future improvements target:

- Lightweight design without full DHT overhead
- Highly-scalable eventual consistency
- Support for 10k+ nodes with minimal resource usage

### NAT Traversal

The network implements comprehensive NAT traversal solutions to ensure connectivity across diverse network configurations.

**Objectives:**

- Configuration-free peer connections
- Support for users with varying technical expertise
- Enable nodes on standard consumer hardware

**Implementation:**

- Tailored solutions based on user network configuration
- Automatic NAT type detection and adaptation
- Fallback mechanisms for challenging network environments

*Note: Detailed NAT traversal specifications are maintained in a separate document.*

### Message Dissemination

#### Gossipsub Protocol

Nomos employs **gossipsub** for reliable message propagation across the network.

**Integration:**

- Seamless integration with Kademlia peer discovery
- Automatic peer list updates
- Efficient message routing and delivery

#### Topic Configuration

**Mempool Dissemination:**

- **Mainnet**: `/nomos/mempool/0.1.0`
- **Testnet**: `/nomos-testnet/mempool/0.1.0`

**Block Propagation:**

- **Mainnet**: `/nomos/cryptarchia/0.1.0`
- **Testnet**: `/nomos-testnet/cryptarchia/0.1.0`

#### Network Parameters

**Peering Degree:**

- **Minimum recommended**: 8 peers
- **Rationale**: Ensures redundancy and efficient propagation
- **Configurable**: Nodes may adjust based on resources and requirements

### Bootstrapping

#### Initial Network Entry

New nodes connect to the network through designated bootstrap nodes.

**Process:**

1. Connect to known bootstrap nodes
2. Obtain initial peer list through Kademlia
3. Establish gossipsub connections
4. Begin participating in network protocols

**Bootstrap Node Requirements:**

- High availability and reliability
- Geographic distribution
- Version compatibility maintenance

### Message Encoding

All network messages follow the Nomos Wire Format specification for consistent encoding and decoding across implementations.

**Key Properties:**

- Deterministic serialization
- Efficient binary encoding
- Forward/backward compatibility support
- Cross-platform consistency

*Note: Detailed wire format specifications are maintained in a separate document.*

## Implementation Requirements

### Mandatory Protocols

All Nomos nodes MUST implement:

1. **Kademlia DHT** for peer discovery
2. **Identify protocol** for peer information exchange
3. **Gossipsub** for message dissemination

### Optional Enhancements

Nodes MAY implement:

- Advanced NAT traversal techniques
- Custom peering strategies
- Enhanced message routing optimizations

### Network Versioning

Protocol versions follow semantic versioning:

- **Major version**: Breaking protocol changes
- **Minor version**: Backward-compatible enhancements
- **Patch version**: Bug fixes and optimizations

## Configuration Parameters

### Implementation Note

**Current Status**: The Nomos P2P network implementation uses hardcoded libp2p protocol parameters for optimal performance and reliability. While the node configuration file (`config.yaml`) contains network-related settings, the core libp2p protocol parameters (Kademlia DHT, Identify, and Gossipsub) are embedded in the source code.

### Node Configuration

The following network parameters are configurable via `config.yaml`:

#### Network Backend Settings

```yaml
network:
  backend:
    host: 0.0.0.0
    port: 3000
    node_key: <node_private_key>
    initial_peers: []
```

#### Protocol-Specific Topics

**Mempool Dissemination:**

- **Mainnet**: `/nomos/mempool/0.1.0`
- **Testnet**: `/nomos-testnet/mempool/0.1.0`

**Block Propagation:**

- **Mainnet**: `/nomos/cryptarchia/0.1.0`
- **Testnet**: `/nomos-testnet/cryptarchia/0.1.0`

### Hardcoded Protocol Parameters

The following libp2p protocol parameters are currently hardcoded in the implementation:

#### Peer Discovery Parameters

- **Protocol identifiers** for Kademlia DHT and Identify protocols
- **DHT routing table** configuration and query timeouts
- **Peer discovery intervals** and connection management

#### Message Dissemination Parameters  

- **Gossipsub mesh parameters** (peer degree, heartbeat intervals)
- **Message validation** and caching settings
- **Topic subscription** and fanout management

#### Rationale for Hardcoded Parameters

1. **Network Stability**: Prevents misconfigurations that could fragment the network
2. **Performance Optimization**: Parameters are tuned for the target network size and latency requirements
3. **Security**: Reduces attack surface by limiting configurable network parameters
4. **Simplicity**: Eliminates need for operators to understand complex P2P tuning

## Security Considerations

### Network-Level Security

1. **Peer Authentication**: Utilize libp2p's built-in peer identity verification
2. **Message Validation**: Implement application-layer message validation
3. **Rate Limiting**: Protect against spam and DoS attacks
4. **Blacklisting**: Mechanism for excluding malicious peers

### Privacy Considerations

1. **Traffic Analysis**: Gossipsub provides some resistance to traffic analysis
2. **Metadata Leakage**: Minimize identifiable information in protocol messages
3. **Connection Patterns**: Randomize connection timing and patterns

### Denial of Service Protection

1. **Resource Limits**: Impose limits on connections and message rates
2. **Peer Scoring**: Implement reputation-based peer management
3. **Circuit Breakers**: Automatic protection against resource exhaustion

### Node Configuration Example

[Nomos Node Configuration](https://github.com/logos-co/nomos/blob/master/nodes/nomos-node/config.yaml) is an example node configuration

## Performance Characteristics

### Scalability

- **Target Network Size**: 10,000+ nodes
- **Message Latency**: Sub-second for critical messages
- **Bandwidth Efficiency**: Optimized for limited bandwidth environments

### Resource Requirements

- **Memory Usage**: Minimal DHT routing table overhead
- **CPU Usage**: Efficient cryptographic operations
- **Network Bandwidth**: Adaptive based on node role and capacity

## References

Original working document, from Nomos Notion: [P2P Network Specification](https://nomos-tech.notion.site/P2P-Network-Specification-206261aa09df81db8100d5f410e39d75).

1. [libp2p Specifications](https://docs.libp2p.io/)
2. [QUIC Protocol Specification](https://docs.libp2p.io/concepts/transports/quic/)
3. [Kademlia DHT](https://docs.libp2p.io/concepts/discovery-routing/kaddht/)
4. [Gossipsub Protocol](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub)
5. [Identify Protocol](https://github.com/libp2p/specs/blob/master/identify/README.md)
6. [Nomos Implementation](https://github.com/logos-co/nomos) - Reference implementation and source code
7. [Nomos Node Configuration](https://github.com/logos-co/nomos/blob/master/nodes/nomos-node/config.yaml) - Example node configuration

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
