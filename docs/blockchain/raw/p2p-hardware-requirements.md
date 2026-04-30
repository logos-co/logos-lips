# P2P-HARDWARE-REQUIREMENTS

| Field | Value |
| --- | --- |
| Name | Nomos p2p Network Hardware Requirements Specification |
| Slug | 137 |
| Status | raw |
| Category | infrastructure |
| Editor | Daniel Sanchez-Quiros <danielsq@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/p2p-hardware-requirements.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/p2p-hardware-requirements.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/nomos/raw/p2p-hardware-requirements.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/nomos/raw/p2p-hardware-requirements.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/nomos/raw/p2p-hardware-requirements.md) — ci: add mdBook configuration (#233)
- **2025-09-25** — [`34bbd7a`](https://github.com/logos-co/logos-lips/blob/34bbd7af90df4baefd6dfeb89c625e846b2db14a/nomos/raw/p2p-hardware-requirements.md) — Created nomos/raw/hardware-requirements.md file (#172)

<!-- timeline:end -->

## Abstract

This specification defines the hardware requirements for running various types of Nomos blockchain nodes. Hardware needs vary significantly based on the node's role, from lightweight verification nodes to high-performance Zone Executors. The requirements are designed to support diverse participation levels while ensuring network security and performance.

## Motivation

The Nomos network is designed to be inclusive and accessible across a wide range of hardware configurations. By defining clear hardware requirements for different node types, we enable:

1. **Inclusive Participation**: Allow users with limited resources to participate as Light Nodes
2. **Scalable Infrastructure**: Support varying levels of network participation based on available resources
3. **Performance Optimization**: Ensure adequate resources for computationally intensive operations
4. **Network Security**: Maintain network integrity through properly resourced validator nodes
5. **Service Quality**: Define requirements for optional services that enhance network functionality

**Important Notice**: These hardware requirements are preliminary and subject to revision based on implementation testing and real-world network performance data.

## Specification

### Node Types Overview

Hardware requirements vary based on the node's role and services:

- **Light Node**: Minimal verification with minimal resources
- **Basic Bedrock Node**: Standard validation participation
- **Service Nodes**: Enhanced capabilities for optional network services

### Light Node

Light Nodes provide network verification with minimal resource requirements, suitable for resource-constrained environments.

**Target Use Cases:**

- Mobile devices and smartphones
- Single-board computers (Raspberry Pi, etc.)
- IoT devices with network connectivity
- Users with limited hardware resources

**Hardware Requirements:**

| Component | Specification |
|-----------|---------------|
| **CPU** | Low-power processor (smartphone/SBC capable) |
| **Memory (RAM)** | 512 MB |
| **Storage** | Minimal (few GB) |
| **Network** | Reliable connection, 1 Mbps free bandwidth |

### Basic Bedrock Node (Validator)

Basic validators participate in Bedrock consensus using typical consumer hardware.

**Target Use Cases:**

- Individual validators on consumer hardware
- Small-scale validation operations
- Entry-level network participation

**Hardware Requirements:**

| Component | Specification |
|-----------|---------------|
| **CPU** | 2 cores, 2 GHz modern multi-core processor |
| **Memory (RAM)** | 1 GB minimum |
| **Storage** | SSD with 100+ GB free space, expandable |
| **Network** | Reliable connection, 1 Mbps free bandwidth |

### Service-Specific Requirements

Nodes can optionally run additional Bedrock Services that require enhanced resources beyond basic validation.

#### Data Availability (DA) Service

DA Service nodes store and serve data shares for the network's data availability layer.

**Service Role:**

- Store blockchain data and blob data long-term
- Serve data shares to requesting nodes
- Maintain high availability for data retrieval

**Additional Requirements:**

| Component | Specification | Rationale |
|-----------|---------------|-----------|
| **CPU** | Same as Basic Bedrock Node | Standard processing needs |
| **Memory (RAM)** | Same as Basic Bedrock Node | Standard memory needs |
| **Storage** | **Fast SSD, 500+ GB free** | Long-term chain and blob storage |
| **Network** | **High bandwidth (10+ Mbps)** | Concurrent data serving |
| **Connectivity** | **Stable, accessible external IP** | Direct peer connections |

**Network Requirements:**

- Capacity to handle multiple concurrent connections
- Stable external IP address for direct peer access
- Low latency for efficient data serving

#### Blend Protocol Service

Blend Protocol nodes provide anonymous message routing capabilities.

**Service Role:**

- Route messages anonymously through the network
- Provide timing obfuscation for privacy
- Maintain multiple concurrent connections

**Additional Requirements:**

| Component | Specification | Rationale |
|-----------|---------------|-----------|
| **CPU** | Same as Basic Bedrock Node | Standard processing needs |
| **Memory (RAM)** | Same as Basic Bedrock Node | Standard memory needs |
| **Storage** | Same as Basic Bedrock Node | Standard storage needs |
| **Network** | **Stable connection (10+ Mbps)** | Multiple concurrent connections |
| **Connectivity** | **Stable, accessible external IP** | Direct peer connections |

**Network Requirements:**

- Low-latency connection for effective message blending
- Stable connection for timing obfuscation
- Capability to handle multiple simultaneous connections

#### Executor Network Service

Zone Executors perform the most computationally intensive work in the network.

**Service Role:**

- Execute Zone state transitions
- Generate zero-knowledge proofs
- Process complex computational workloads

**Critical Performance Note**: Zone Executors perform the heaviest computational work in the network. High-performance hardware is crucial for effective participation and may provide competitive advantages in execution markets.

**Hardware Requirements:**

| Component | Specification | Rationale |
|-----------|---------------|-----------|
| **CPU** | **Very high-performance multi-core processor** | Zone logic execution and ZK proving |
| **Memory (RAM)** | **32+ GB strongly recommended** | Complex Zone execution requirements |
| **Storage** | Same as Basic Bedrock Node | Standard storage needs |
| **GPU** | **Highly recommended/often necessary** | Efficient ZK proof generation |
| **Network** | **High bandwidth (10+ Mbps)** | Data dispersal and high connection load |

**GPU Requirements:**

- **NVIDIA**: CUDA-enabled GPU (RTX 3090 or equivalent recommended)
- **Apple**: Metal-compatible Apple Silicon
- **Performance Impact**: Strong GPU significantly reduces proving time

**Network Requirements:**

- Support for **2048+ direct UDP connections** to DA Nodes (for blob publishing)
- High bandwidth for data dispersal operations
- Stable connection for continuous operation

*Note: DA Nodes utilizing [libp2p](https://docs.libp2p.io/) connections need sufficient capacity to receive and serve data shares over many connections.*

## Implementation Requirements

### Minimum Requirements

All Nomos nodes MUST meet:

1. **Basic connectivity** to the Nomos network via [libp2p](https://docs.libp2p.io/)
2. **Adequate storage** for their designated role
3. **Sufficient processing power** for their service level
4. **Reliable network connection** with appropriate bandwidth for [QUIC](https://docs.libp2p.io/concepts/transports/quic/) transport

### Optional Enhancements

Node operators MAY implement:

- Hardware redundancy for critical services
- Enhanced cooling for high-performance configurations
- Dedicated network connections for service nodes utilizing [libp2p](https://docs.libp2p.io/) protocols
- Backup power systems for continuous operation

### Resource Scaling

Requirements may vary based on:

- **Network Load**: Higher network activity increases resource demands
- **Zone Complexity**: More complex Zones require additional computational resources
- **Service Combinations**: Running multiple services simultaneously increases requirements
- **Geographic Location**: Network latency affects optimal performance requirements

## Security Considerations

### Hardware Security

1. **Secure Storage**: Use encrypted storage for sensitive node data
2. **Network Security**: Implement proper firewall configurations
3. **Physical Security**: Secure physical access to node hardware
4. **Backup Strategies**: Maintain secure backups of critical data

### Performance Security

1. **Resource Monitoring**: Monitor resource usage to detect anomalies
2. **Redundancy**: Plan for hardware failures in critical services
3. **Isolation**: Consider containerization or virtualization for service isolation
4. **Update Management**: Maintain secure update procedures for hardware drivers

## Performance Characteristics

### Scalability

- **Light Nodes**: Minimal resource footprint, high scalability
- **Validators**: Moderate resource usage, network-dependent scaling
- **Service Nodes**: High resource usage, specialized scaling requirements

### Resource Efficiency

- **CPU Usage**: Optimized algorithms for different hardware tiers
- **Memory Usage**: Efficient data structures for constrained environments
- **Storage Usage**: Configurable retention policies and compression
- **Network Usage**: Adaptive bandwidth utilization based on [libp2p](https://docs.libp2p.io/) capacity and [QUIC](https://docs.libp2p.io/concepts/transports/quic/) connection efficiency

## References

1. [libp2p protocol](https://docs.libp2p.io/)
2. [QUIC protocol](https://docs.libp2p.io/concepts/transports/quic/)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
