# NOMOS-DA-NETWORK

| Field | Value |
| --- | --- |
| Name | NomosDA Network |
| Slug | 136 |
| Status | raw |
| Category | Standards Track |
| Editor | Daniel Sanchez Quiros <danielsq@logos.co> |
| Contributors | Álvaro Castro-Castilla <alvaro@logos.co>, Daniel Kashepava <danielkashepava@logos.co>, Gusto Bacvinka <augustinas@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/blockchain/raw/nomosda-network.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomosda-network.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomosda-network.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/nomos/raw/nomosda-network.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/nomos/raw/nomosda-network.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/nomos/raw/nomosda-network.md) — ci: add mdBook configuration (#233)
- **2025-09-25** — [`51ef4cd`](https://github.com/logos-co/logos-lips/blob/51ef4cd533d8824291d9e2884bb467235b32a450/nomos/raw/nomosda-network.md) — added nomos/raw/nomosda-network.md (#160)

<!-- timeline:end -->

## Introduction

NomosDA is the scalability solution protocol for data availability within the Nomos network.
This document delineates the protocol's structure at the network level,
identifies participants,
and describes the interactions among its components.  
Please note that this document does not delve into the cryptographic aspects of the design.
For comprehensive details on the cryptographic operations,
a detailed specification is a work in progress.

## Objectives

NomosDA was created to ensure that data from Nomos zones is distributed, verifiable, immutable, and accessible.
At the same time, it is optimised for the following properties:

- **Decentralization**: NomosDA’s data availability guarantees must be achieved with minimal trust assumptions
and centralised actors. Therefore,
permissioned DA schemes involving a Data Availability Committee (DAC) had to be avoided in the design.
Schemes that require some nodes to download the entire blob data were also off the list
due to the disproportionate role played by these “supernodes”.

- **Scalability**: NomosDA is intended to be a bandwidth-scalable protocol, ensuring that its functions are maintained as the Nomos network grows. Therefore, NomosDA was designed to minimise the amount of data sent to participants, reducing the communication bottleneck and allowing more parties to participate in the DA process.

To achieve the above properties, NomosDA splits up zone data and
distributes it among network participants,
with cryptographic properties used to verify the data’s integrity.
A major feature of this design is that parties who wish to receive an assurance of data availability
can do so very quickly and with minimal hardware requirements.
However, this comes at the cost of additional complexity and resources required by more integral participants.

## Requirements

In order to ensure that the above objectives are met,
the NomosDA network requires a group of participants
that undertake a greater burden in terms of active involvement in the protocol.
Recognising that not all node operators can do so,
NomosDA assigns different roles to different kinds of participants,
depending on their ability and willingness to contribute more computing power
and bandwidth to the protocol.
It was therefore necessary for NomosDA to be implemented as an opt-in Service Network.

Because the NomosDA network has an arbitrary amount of participants,
and the data is split into a fixed number of portions (see the [Encoding & Verification Specification](https://www.notion.so/NomosDA-Encoding-Verification-4d8ca269e96d4fdcb05abc70426c5e7c)),
it was necessary to define exactly how each portion is assigned to a participant who will receive and verify it.
This assignment algorithm must also be flexible enough to ensure smooth operation in a variety of scenarios,
including where there are more or fewer participants than the number of portions.

## Overview

### Network Participants

The NomosDA network includes three categories of participants:

- **Executors**: Tasked with the encoding and dispersal of data blobs.  
- **DA Nodes**: Receive and verify the encoded data,
subsequently temporarily storing it for further network validation through sampling.  
- **Light Nodes**: Employ sampling to ascertain data availability.

### Network Distribution

The NomosDA network is segmented into `num_subnets` subnetworks.
These subnetworks represent subsets of peers from the overarching network,
each responsible for a distinct portion of the distributed encoded data.
Peers in the network may engage in one or multiple subnetworks,
contingent upon network size and participant count.

### Sub-protocols

The NomosDA protocol consists of the following sub-protocols:

- **Dispersal**: Describes how executors distribute encoded data blobs to subnetworks.
[NomosDA Dispersal](https://www.notion.so/NomosDA-Dispersal-1818f96fb65c805ca257cb14798f24d4?pvs=21)
- **Replication**: Defines how DA nodes distribute encoded data blobs within subnetworks.
[NomosDA Subnetwork Replication](https://www.notion.so/NomosDA-Subnetwork-Replication-1818f96fb65c80119fa0e958a087cc2b?pvs=21)
- **Sampling**: Used by sampling clients (e.g., light clients) to verify the availability of previously dispersed
and replicated data.
[NomosDA Sampling](https://www.notion.so/NomosDA-Sampling-1538f96fb65c8031a44cf7305d271779?pvs=21)
- **Reconstruction**: Describes gathering and decoding dispersed data back into its original form.
[NomosDA Reconstruction](https://www.notion.so/NomosDA-Reconstruction-1828f96fb65c80b2bbb9f4c5a0cf26a5?pvs=21)
- **Indexing**: Tracks and exposes blob metadata on-chain.
[NomosDA Indexing](https://www.notion.so/NomosDA-Indexing-1bb8f96fb65c8044b635da9df20c2411?pvs=21)

## Construction

### NomosDA Network Registration

Entities wishing to participate in NomosDA must declare their role via [SDP](https://www.notion.so/Final-Draft-Validator-Role-Protocol-17b8f96fb65c80c69c2ef55e22e29506) (Service Declaration Protocol).
Once declared, they're accounted for in the subnetwork construction.

This enables participation in:

- Dispersal (as executor)
- Replication & sampling (as DA node)
- Sampling (as light node)

### Subnetwork Assignment

The NomosDA network comprises `num_subnets` subnetworks,
which are virtual in nature.
A subnetwork is a subset of peers grouped together so nodes know who they should connect with,
serving as groupings of peers tasked with executing the dispersal and replication sub-protocols.
In each subnetwork, participants establish a fully connected overlay,
ensuring all nodes maintain permanent connections for the lifetime of the SDP set
with peers within the same subnetwork.
Nodes refer to nodes in the Data Availability SDP set to ascertain their connectivity requirements across subnetworks.

#### Assignment Algorithm

The concrete distribution algorithm is described in the following specification:
[DA Subnetwork Assignation](https://www.notion.so/DA-Subnetwork-Assignation-217261aa09df80fc8bb9cf46092741ce)

## Executor Connections

Each executor maintains a connection with one peer per subnetwork,
necessitating at least num_subnets stable and healthy connections.
Executors are expected to allocate adequate resources to sustain these connections.
An example algorithm for peer selection would be:

```python
def select_peers(
    subnetworks: Sequence[Set[PeerId]],
    filtered_subnetworks: Set[int],
    filtered_peers: Set[PeerId]
) -> Set[PeerId]:
    result = set()
    for i, subnetwork in enumerate(subnetworks):
        available_peers = subnetwork - filtered_peers
        if i not in filtered_subnetworks and available_peers:
            result.add(next(iter(available_peers)))
    return result
```

## NomosDA Protocol Steps

### Dispersal

1. The NomosDA protocol is initiated by executors
who perform data encoding as outlined in the [Encoding Specification](https://www.notion.so/NomosDA-Encoding-Verification-4d8ca269e96d4fdcb05abc70426c5e7c).
2. Executors prepare and distribute each encoded data portion
to its designated subnetwork (from `0` to `num_subnets - 1` ).
3. Executors might opt to perform sampling to confirm successful dispersal.
4. Post-dispersal, executors publish the dispersed `blob_id` and metadata to the mempool. <!-- TODO: add link to dispersal document-->

### Replication

DA nodes receive columns from dispersal or replication
and validate the data encoding.
Upon successful validation,
they replicate the validated column to connected peers within their subnetwork.
Replication occurs once per blob; subsequent validations of the same blob are discarded.

### Sampling

1. Sampling is [invoked based on the node's current role](https://www.notion.so/1538f96fb65c8031a44cf7305d271779?pvs=25#15e8f96fb65c8006b9d7f12ffdd9a159).
2. The node selects `sample_size` random subnetworks
and queries each for the availability of the corresponding column for the sampled blob. Sampling is deemed successful only if all queried subnetworks respond affirmatively.

- If `num_subnets` is 2048, `sample_size` is [20 as per the sampling research](https://www.notion.so/1708f96fb65c80a08c97d728cb8476c3?pvs=25#1708f96fb65c80bab6f9c6a946940078)

```mermaid
sequenceDiagram
    SamplingClient ->> DANode_1: Request
    DANode_1 -->> SamplingClient: Response
    SamplingClient ->>DANode_2: Request
    DANode_2 -->> SamplingClient: Response
    SamplingClient ->> DANode_n: Request
    DANode_n -->> SamplingClient: Response
```

### Network Schematics

The overall network and protocol interactions is represented by the following diagram

```mermaid
flowchart TD
subgraph Replication
    subgraph Subnetwork_N
        N10 -->|Replicate| N20
        N20 -->|Replicate| N30
        N30 -->|Replicate| N10
    end
    subgraph ...
    end
    subgraph Subnetwork_0
        N1 -->|Replicate| N2
        N2 -->|Replicate| N3
        N3 -->|Replicate| N1
    end
end
subgraph Sampling
    N9 -->|Sample 0| N2
    N9 -->|Sample S| N20
end
subgraph Dispersal
    Executor -->|Disperse| N1
    Executor -->|Disperse| N10
end
```

## Details

### Network specifics

The NomosDA network is engineered for connection efficiency.
Executors manage numerous open connections,
utilizing their resource capabilities.
DA nodes, with their resource constraints,
are designed to maximize connection reuse.

NomosDA uses [multiplexed](https://docs.libp2p.io/concepts/transports/quic/#quic-native-multiplexing) streams over [QUIC](https://docs.libp2p.io/concepts/transports/quic/) connections.
For each sub-protocol, a stream protocol ID is defined to negotiate the protocol,
triggering the specific protocol once established:

- Dispersal: /nomos/da/{version}/dispersal
- Replication: /nomos/da/{version}/replication
- Sampling: /nomos/da/{version}/sampling

Through these multiplexed streams,
DA nodes can utilize the same connection for all sub-protocols.
This, combined with virtual subnetworks (membership sets),
ensures the overlay node distribution is scalable for networks of any size.

## References

- [Encoding Specification](https://www.notion.so/NomosDA-Encoding-Verification-4d8ca269e96d4fdcb05abc70426c5e7c)
- [Encoding & Verification Specification](https://www.notion.so/NomosDA-Encoding-Verification-4d8ca269e96d4fdcb05abc70426c5e7c)
- [NomosDA Dispersal](https://www.notion.so/NomosDA-Dispersal-1818f96fb65c805ca257cb14798f24d4?pvs=21)
- [NomosDA Subnetwork Replication](https://www.notion.so/NomosDA-Subnetwork-Replication-1818f96fb65c80119fa0e958a087cc2b?pvs=21)
- [DA Subnetwork Assignation](https://www.notion.so/DA-Subnetwork-Assignation-217261aa09df80fc8bb9cf46092741ce)
- [NomosDA Sampling](https://www.notion.so/NomosDA-Sampling-1538f96fb65c8031a44cf7305d271779?pvs=21)
- [NomosDA Reconstruction](https://www.notion.so/NomosDA-Reconstruction-1828f96fb65c80b2bbb9f4c5a0cf26a5?pvs=21)
- [NomosDA Indexing](https://www.notion.so/NomosDA-Indexing-1bb8f96fb65c8044b635da9df20c2411?pvs=21)
- [SDP](https://www.notion.so/Final-Draft-Validator-Role-Protocol-17b8f96fb65c80c69c2ef55e22e29506)
- [invoked based on the node's current role](https://www.notion.so/1538f96fb65c8031a44cf7305d271779?pvs=25#15e8f96fb65c8006b9d7f12ffdd9a159)
- [20 as per the sampling research](https://www.notion.so/1708f96fb65c80a08c97d728cb8476c3?pvs=25#1708f96fb65c80bab6f9c6a946940078)
- [multiplexed](https://docs.libp2p.io/concepts/transports/quic/#quic-native-multiplexing)
- [QUIC](https://docs.libp2p.io/concepts/transports/quic/)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
