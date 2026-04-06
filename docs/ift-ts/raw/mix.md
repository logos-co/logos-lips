# MIX

| Field | Value |
| --- | --- |
| Name | LIBP2P-MIX |
| Slug | 99 |
| Status | raw |
| Category | Standards Track |
| Editor | Akshaya Mani <akshaya@status.im> |
| Contributors | Prem Prathi <prem@status.im>, Daniel Kaiser <danielkaiser@status.im>, Hanno Cornelius <hanno@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-29** — [`925aeac`](https://github.com/vacp2p/rfc-index/blob/925aeac395050c948c1cceb1d5b0673836ebd442/docs/ift-ts/raw/mix.md) — chore: changes to how per-hop proof is added to sphinx packet which makes it simpler (#263)
- **2026-01-19** — [`f24e567`](https://github.com/vacp2p/rfc-index/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/mix.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/vacp2p/rfc-index/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/mix.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/mix.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/vacp2p/rfc-index/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/mix.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/vacp2p/rfc-index/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/mix.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/vacp2p/rfc-index/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/mix.md) — ci: add mdBook configuration (#233)
- **2025-12-15** — [`dabc317`](https://github.com/vacp2p/rfc-index/blob/dabc31786b4a4ca704ebcd1105239faff7ac2b47/vac/raw/mix.md) — fixing format errors in mix rfc (#229)
- **2025-12-12** — [`4f54254`](https://github.com/vacp2p/rfc-index/blob/4f54254706666e373b5987901d974dc40f109293/vac/raw/mix.md) — fix format errors in math sections for mix rfc (#225)
- **2025-12-11** — [`7f1df32`](https://github.com/vacp2p/rfc-index/blob/7f1df32779d5ff3fa57abc2e71ac2ad1b9662965/vac/raw/mix.md) — chore: use sembreaks for easy review and edits (#223)
- **2025-12-10** — [`e742cd5`](https://github.com/vacp2p/rfc-index/blob/e742cd519200a7cb0971936bd1dbbeb31397bce5/vac/raw/mix.md) — RFC Addition: Section 9 Security Considerations (#194)
- **2025-12-10** — [`9d11a22`](https://github.com/vacp2p/rfc-index/blob/9d11a22901ffe9c3ab0007f58baa55b0e08abfc9/vac/raw/mix.md) — docs: finalize Section 8 Sphinx Packet Construction and Handling (#202)
- **2025-10-05** — [`36be428`](https://github.com/vacp2p/rfc-index/blob/36be428cdd2f12e1c9a1dd0b984dc9a6fd4acfee/vac/raw/mix.md) —  RFC Refactor: Sphinx Packet Format (#173)
- **2025-06-27** — [`5e3b478`](https://github.com/vacp2p/rfc-index/blob/5e3b4788ec1c0ec07535efe321b103d52b118db5/vac/raw/mix.md) —  RFC Refactor PR: Modular Rewrite of Mix Protocol Specification (#158)
- **2025-06-02** — [`db90adc`](https://github.com/vacp2p/rfc-index/blob/db90adc94e9f69627dd1254159d33eb062f00867/vac/raw/mix.md) — Fix LaTeX errors (#163)
- **2024-11-08** — [`38fce27`](https://github.com/vacp2p/rfc-index/blob/38fce27d33ff11fcf15f947a9985c86b297c71b6/vac/raw/mix.md) — typo fix
- **2024-09-16** — [`7f5276e`](https://github.com/vacp2p/rfc-index/blob/7f5276e18c16e644ba6645d20854ce6e6dd82aad/vac/raw/mix.md) — libp2p Mix Protocol Spec Draft (#97)

<!-- timeline:end -->

## Abstract

The Mix Protocol defines a decentralized anonymous message routing layer for libp2p networks.
It enables sender anonymity by routing each message through a decentralized mix overlay network composed of participating libp2p nodes, known as mix nodes.
Each message is routed independently in a stateless manner, allowing other libp2p protocols to selectively anonymize messages without modifying their core protocol behavior.

## 1. Introduction

The Mix Protocol is a custom libp2p protocol that defines a message-layer routing abstraction designed to provide sender anonymity in peer-to-peer systems built on the libp2p stack.
It addresses the absence of native anonymity primitives in libp2p by offering a modular, content-agnostic protocol that other libp2p protocols can invoke when anonymity is required.

This document describes the design, behavior, and integration of the Mix Protocol within the libp2p architecture.
Rather than replacing or modifying existing libp2p protocols, the Mix Protocol complements them by operating independently of connection state and protocol negotiation.
It is intended to be used as an optional anonymity layer that can be selectively applied on a per-message basis.

Integration with other libp2p protocols is handled through external interface components&mdash;the Mix Entry and Exit layers&mdash;which mediate between these protocols and the Mix Protocol instances.
These components allow applications to defer anonymity concerns to the Mix layer without altering their native semantics or transport assumptions.

The rest of this document describes the motivation for the protocol, defines relevant terminology, presents the protocol architecture, and explains how the Mix Protocol interoperates with the broader libp2p protocol ecosystem.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

The following terms are used throughout this specification:

- **Origin Protocol**
  A libp2p protocol (_e.g.,_ Ping, GossipSub) that generates and receives the actual message payload.
  The origin protocol MUST decide on a per-message basis whether to route the message through the Mix Protocol or not.

- **Mix Node**
  A libp2p node that supports the Mix Protocol and participates in the mix network.
  A mix node initiates anonymous routing when invoked with a message.
  It also receives and processes Sphinx packets when selected as a hop in a mix path.

- **Mix Path**
  A non-repeating sequence of mix nodes through which a Sphinx packet is routed across the mix network.

- **Mixify**
  A per-message flag set by the origin protocol to indicate that a message should be routed using the Mix Protocol or not.
  Only messages with mixify set are forwarded to the Mix Entry Layer. Other messages SHOULD be routed using the origin protocol's default behavior.
  The phrases 'messages to be mixified', 'to mixify a message' and related variants are used informally throughout this document to refer to messages that either have the `mixify` flag set or are selected to have it set.

- **Mix Entry Layer**
  A component that receives messages to be _mixified_ from an origin protocol and forwards them to the local Mix Protocol instance.
  The Entry Layer is external to the Mix Protocol.

- **Mix Exit Layer**
  A component that receives decrypted messages from a Mix Protocol instance and delivers them to the appropriate origin protocol instance at the destination.
  Like the Entry Layer, it is external to the Mix Protocol.

- **Mixnet or Mix Network**
  A decentralized overlay network formed by all nodes that support the Mix Protocol.
  It operates independently of libp2p's protocol-level routing and origin protocol behavior.

- **Sphinx Packet**
  A cryptographic packet format used by the Mix Protocol to encapsulate messages.
  It uses layered encryption to hide routing information and protect message contents as packets are forwarded hop-by-hop.
  Sphinx packets are fixed-size and indistinguishable from one another, providing unlinkability and metadata protection.

- **Initialization Vector (IV)**
  A fixed-length input used to initialize block ciphers to add randomness to the encryption process.
  It ensures that encrypting the same plaintext with the same key produces different ciphertexts.
  The IV is not secret but must be unique for each encryption.

- **Single-Use Reply Block (SURB)**
  A pre-computed Sphinx header that encodes a return path back to the sender.
  SURBs are generated by the sender and included in the Sphinx packet sent to the recipient.
  It enables the recipient to send anonymous replies, without learning the sender's identity, the return path, or the forwarding delays.

## 3. Motivation and Background

libp2p enables modular peer-to-peer applications, but it lacks built-in support for sender anonymity.
Most protocols expose persistent peer identifiers, transport metadata, or traffic patterns that can be exploited to deanonymize users through passive observation or correlation.

While libp2p supports NAT traversal mechanisms such as Circuit Relay, these focus on connectivity rather than anonymity.
Relays may learn peer identities during stream setup and can observe traffic timing and volume, offering no protection against metadata analysis.

libp2p also supports a Tor transport for network-level anonymity, tunneling traffic through long-lived, encrypted circuits.
However, Tor relies on session persistence and is ill-suited for protocols requiring per-message unlinkability.

The Mix Protocol addresses this gap with a decentralized message routing layer based on classical mix network principles.
It applies layered encryption and per-hop delays to obscure both routing paths and timing correlations.
Each message is routed independently, providing resistance to traffic analysis and protection against metadata leakage.

By decoupling anonymity from connection state and transport negotiation, the Mix Protocol offers a modular privacy abstraction that existing libp2p protocols can adopt without altering their core behavior.

To better illustrate the differences in design goals and threat models, the following subsection contrasts the Mix Protocol with Tor, a widely known anonymity system.

### 3.1 Comparison with Tor

The Mix Protocol differs fundamentally from Tor in several ways:

- **Unlinkability**: In the Mix Protocol, there is no direct connection between source and destination.
  Each message is routed independently, eliminating correlation through persistent circuits.

- **Delay-based mixing**: Mix nodes introduce randomized delays (e.g., from an exponential distribution) before forwarding messages, making timing correlation significantly harder.

- **High-latency focus**: Tor prioritizes low-latency communication for interactive web traffic, whereas the Mix Protocol is designed for scenarios where higher latency is acceptable in exchange for stronger anonymity.

- **Message-based design**: Each message in the Mix Protocol is self-contained and independently routed.
  No sessions or state are maintained between messages.

- **Resistance to endpoint attacks**: The Mix Protocol is less susceptible to certain endpoint-level attacks, such as traffic volume correlation or targeted probing, since messages are delayed, reordered, and unlinkable at each hop.

To understand the underlying anonymity properties of the Mix Protocol, we next describe the core components of a mix network.

## 4. Mixing Strategy and Packet Format

The Mix Protocol relies on two core design elements to achieve sender unlinkability and metadata protection:
a mixing strategy and a cryptographically secure mix packet format.

### 4.1 Mixing Strategy

A mixing strategy defines how mix nodes delay and reorder incoming packets to resist timing correlation and input-output linkage.
Two commonly used approaches are batch-based mixing and continuous-time mixing.

In batching-based mixing, each mix node collects incoming packets over a fixed or adaptive interval, shuffles them, and forwards them in a batch.
While this provides some unlinkability, it introduces high latency, requires synchronized flushing rounds, and may result in bursty output traffic.
Anonymity is bounded by the batch size, and performance may degrade under variable message rates.

The Mix Protocol instead uses continuous-time mixing, where each mix node applies a randomized delay to every incoming packet, typically drawn from an exponential distribution.
This enables theoretically unbounded anonymity sets, since any packet may, with non-zero probability, be delayed arbitrarily long.
In practice, the distribution is truncated once the probability of delay falls below a negligible threshold.
Continuous-time mixing also offers improved bandwidth utilization and smoother output traffic compared to batching-based approaches.

To make continuous-time mixing tunable and predictable, the sender MUST select the mean delay for each hop and encode it into the Sphinx packet header.
This allows top-level applications to balance latency and anonymity according to their requirements.

### 4.2 Mix Packet Format

A mix packet format defines how messages are encapsulated and routed through a mix network.
It must ensure unlinkability between incoming and outgoing packets, prevent metadata leakage (e.g., path length, hop position, or payload size), and support uniform processing by mix nodes regardless of direction or content.

The Mix Protocol uses [Sphinx packets](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf) to meet these goals.
Each message is encrypted in layers corresponding to the selected mix path.
As a packet traverses the network, each mix node removes one encryption layer to obtain the next hop and delay, while the remaining payload remains encrypted and indistinguishable.

Sphinx packets are fixed in size and bit-wise unlinkable.
This ensures that they appear identical on the wire regardless of payload, direction, or route length, reducing opportunities for correlation based on packet size or format.
Even mix nodes learn only the immediate routing information and the delay to be applied.
They do not learn their position in the path or the total number of hops.

The packet format is resistant to tagging and replay attacks and is compact and efficient to process.
Sphinx packets also include per-hop integrity checks and enforce a maximum path length.
Together with a constant-size header and payload, this provides bounded protection against endless routing and malformed packet propagation.

It also supports anonymous and indistinguishable reply messages through [Single-Use Reply Blocks (SURBs)](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf), although reply support is not implemented yet.

A complete specification of the Sphinx packet structure and fields is provided in [Section 8](#8-sphinx-packet-format).

## 5. Protocol Overview

The Mix Protocol defines a decentralized, message-based routing layer that provides sender anonymity within the libp2p framework.
It is agnostic to message content and semantics.
Each message is treated as an opaque payload, wrapped into a [Sphinx packet](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf) and routed independently through a randomly selected mix path.
Along the path, each mix node removes one layer of encryption, adds a randomized delay, and forwards the packet to the next hop.
This combination of layered encryption and per-hop delay provides resistance to traffic analysis and enables message-level unlinkability.

Unlike typical custom libp2p protocols, the Mix Protocol is stateless&mdash;it does not establish persistent streams, negotiate protocols, or maintain sessions.
Each message is self-contained and routed independently.

The Mix Protocol sits above the transport layer and below the protocol layer in the libp2p stack.
It provides a modular anonymity layer that other libp2p protocols MAY invoke selectively on a per-message basis.

Integration with other libp2p protocols is handled through external components that mediate between the origin protocol and the Mix Protocol instances.
This enables selective anonymous routing without modifying protocol semantics or internal behavior.

The following subsections describe how the Mix Protocol integrates with origin protocols via the Mix Entry and Exit layers, how per-message anonymity is controlled through the `mixify` flag, the rationale for defining Mix as a protocol rather than a transport, and the end-to-end message interaction flow.

### 5.1 Integration with Origin Protocols

libp2p protocols that wish to anonymize messages MUST do so by integrating with the Mix Protocol via the Mix Entry and Exit layers.

- The **Mix Entry Layer** receives messages to be _mixified_ from an origin protocol and forwards them to the local Mix Protocol instance.

- The **Mix Exit Layer** receives the final decrypted message from a Mix Protocol instance and forwards it to the appropriate origin protocol instance at the destination over a client-only connection.

This integration is external to the Mix Protocol and is not handled by mix nodes themselves.

### 5.2 Mixify Option

Some origin protocols may require selective anonymity, choosing to anonymize _only_ certain messages based on their content, context, or destination.
For example, a protocol may only anonymize messages containing sensitive metadata while delivering others directly to optimize performance.

To support this, origin protocols MAY implement a per-message `mixify` flag that indicates whether a message should be routed using the Mix Protocol.

- If the flag is set, the message MUST be handed off to the Mix Entry Layer for anonymous routing.
- If the flag is not set, the message SHOULD be routed using the origin protocol's default mechanism.

This design enables protocols to invoke the Mix Protocol only for selected messages, providing fine-grained control over privacy and performance trade-offs.

### 5.3 Why a Protocol, Not a Transport

The Mix Protocol is specified as a custom libp2p protocol rather than a transport to support selective anonymity while remaining compatible with libp2p's architecture.

As noted in [Section 5.2](#52-mixify-option), origin protocols may anonymize only specific messages based on content or context.
Supporting such selective behavior requires invoking Mix on a per-message basis.

libp2p transports, however, are negotiated per peer connection and apply globally to all messages exchanged between two peers.
Enabling selective anonymity at the transport layer would therefore require changes to libp2p's core transport semantics.

Defining Mix as a protocol avoids these constraints and offers several benefits:

- Supports selective invocation on a per-message basis.
- Works atop existing secure transports (_e.g.,_ QUIC, TLS) without requiring changes to the transport stack.
- Preserves a stateless, content-agnostic model focused on anonymous message routing.
- Integrates seamlessly with origin protocols via the Mix Entry and Exit layers.

This design preserves the modularity of the libp2p stack and allows Mix to be adopted without altering existing transport or protocol behavior.

### 5.4 Protocol Interaction Flow

A typical end-to-end Mix Protocol flow consists of the following three conceptual phases.
Only the second phase&mdash;the anonymous routing performed by mix nodes&mdash;is part of the core Mix Protocol.
The entry-side and exit-side integration steps are handled externally by the Mix Entry and Exit layers.

1. **Entry-side Integration (Mix Entry Layer):**

   - The origin protocol generates a message and sets the `mixify` flag.
   - The message is passed to the Mix Entry Layer, which invokes the local Mix Protocol instance with the message, destination, and origin protocol codec as input.

2. **Anonymous Routing (Core Mix Protocol):**

   - The Mix Protocol instance wraps the message in a Sphinx packet and selects a random mix path.
   - Each mix node along the path:
     - Processes the Sphinx packet by removing one encryption layer.
     - Applies a delay and forwards the packet to the next hop.
   - The final node in the path (exit node) decrypts the final layer, extracting the original plaintext message, destination, and origin protocol codec.

3. **Exit-side Integration (Mix Exit Layer):**

   - The Mix Exit Layer receives the plaintext message, destination, and origin protocol codec.
   - It routes the message to the destination origin protocol instance using a client-only connection.

The destination node does not need to support the Mix Protocol to receive or respond to anonymous messages.

The behavior described above represents the core Mix Protocol.
In addition, the protocol supports a set of pluggable components that extend its functionality.
These components cover areas such as node discovery, delay strategy, exit abuse prevention, cover traffic generation, incentivization, and DoS protection.
Some are REQUIRED for interoperability; others are OPTIONAL or deployment-specific.
The next section describes each component.

### 5.5 Stream Management and Multiplexing

Each Mix Protocol message is routed independently, and forwarding it to the next hop requires opening a new libp2p stream using the Mix Protocol.
This applies to both the initial Sphinx packet transmission and each hop along the mix path.

In high-throughput environments (_e.g._, messaging systems with continuous anonymous traffic), mix nodes may frequently communicate with a subset of mix nodes.
Opening a new stream for each Sphinx packet in such scenarios can incur performance costs, as each stream setup requires a multistream handshake for protocol negotiation.

While libp2p supports multiplexing multiple streams over a single transport connection using stream muxers such as mplex and yamux, it does not natively support reusing the same stream over multiple message transmissions.
However, stream reuse may be desirable in the mixnet setting to reduce overhead and avoid hitting per protocol stream limits between peers.

The lifecycle of streams, including their reuse, eviction, or pooling strategy, is outside the scope of this specification.
It SHOULD be handled by the libp2p host, connection manager, or transport stack.

Mix Protocol implementations MUST NOT assume persistent stream availability and SHOULD gracefully fall back to opening a new stream when reuse is not possible.

## 6. Pluggable Components

Pluggable components define functionality that extends or configures the behavior of the Mix Protocol beyond its core message routing logic.
Each component in this section falls into one of two categories:

- Required for interoperability and path construction (_e.g.,_ discovery, delay strategy, DoS protection).
- Optional or deployment-specific (_e.g.,_ exit abuse prevention, cover traffic, incentivization).

The following subsections describe the role and expected behavior of each.

### 6.1 Discovery

The Mix Protocol does not mandate a specific peer discovery mechanism.
However, nodes participating in the mixnet MUST be discoverable so that other nodes can construct routing paths that include them.

To enable this, regardless of the discovery mechanism used, each mix node MUST make the following information available to peers:

- Indicate Mix Protocol support (_e.g.,_ using a `mix` field or bit).
- Its X25519 public key for Sphinx encryption.
- One or more routable libp2p multiaddresses that identify the mix node's own network endpoints.

To support sender anonymity at scale, the discovery mechanism SHOULD support _unbiased random sampling_ from the set of live mix nodes.
This enables diverse path construction and reduces exposure to adversarial routing bias.

While no existing mechanism provides unbiased sampling by default, [Waku's ambient discovery](https://rfc.vac.dev/waku/standards/core/33/discv5/)&mdash;an extension over [Discv5](https://github.com/ethereum/devp2p/blob/master/discv5/discv5.md)&mdash;demonstrates an approximate solution.
It combines topic-based capability advertisement with periodic peer sampling.
A similar strategy could potentially be adapted for the Mix Protocol.

A more robust solution would involve integrating capability-aware discovery directly into the libp2p stack, such as through extensions to `libp2p-kaddht`.
This would enable direct lookup of mix nodes based on protocol support and eliminate reliance on external mechanisms such as Discv5.
Such an enhancement remains exploratory and is outside the scope of this specification.

Regardless of the mechanism, the goal is to ensure mix nodes are discoverable and that path selection is resistant to bias and node churn.

### 6.2 Delay Strategy

The Mix Protocol uses per-hop delay as a core mechanism for achieving timing unlinkability.
For each hop in the mix path, the sender MUST specify a mean delay value, which is embedded in the Sphinx packet header.
The mix node at each hop uses this value to sample a randomized delay before forwarding the packet.

By default, delays are sampled from an exponential distribution.
This supports continuous-time mixing, produces smooth output traffic, and enables tunable trade-offs between latency and anonymity.
Importantly, it allows for unbounded anonymity sets: each packet may, with non-zero probability, be delayed arbitrarily long.

The delay strategy is considered pluggable, and other distributions MAY be used to match application-specific anonymity or performance requirements.
However, any delay strategy MUST ensure that:

- Delays are sampled independently at each hop.
- Delay sampling introduces sufficient variability to obscure timing correlation between packet arrival and forwarding across multiple hops.

Strategies that produce deterministic or tightly clustered output delays are NOT RECOMMENDED, as they increase the risk of timing correlation.
Delay strategies SHOULD introduce enough uncertainty to prevent adversaries from linking packet arrival and departure times, even when monitoring multiple hops concurrently.

### 6.3 Exit Abuse Prevention

The Mix Protocol supports optional exit abuse prevention mechanisms to defend
exits against flooding attacks routed through them.
These mechanisms are validated at the exit node, which is the final node in the mix path before the message is delivered to its destination via the respective libp2p protocol.

Exit nodes that enforce exit abuse prevention MUST validate the attached proof before forwarding the message.
If validation fails, the message MUST be discarded.

Common strategies include Proof of Work (PoW), Verifiable Delay Functions (VDFs), and Rate-limiting Nullifiers (RLNs).

The sender is responsible for appending the appropriate exit abuse prevention data (_e.g.,_ nonce, timestamp) to the message payload.
The format and verification logic depend on the selected method.

Note:
The exit abuse prevention mechanisms described above are intended to protect the exit from flooding attacks routed through them.
They do not provide protection against denial-of-service (DoS) or resource exhaustion attacks targeting the mixnet itself (_e.g.,_ flooding mix nodes with traffic, inducing processing overhead, or targeting bandwidth).

Protections against attacks targeting the mixnet itself are addressed in [Section 6.6](#66-dos-protection).

### 6.4 Cover Traffic

Cover traffic is an optional mechanism used to improve privacy by making the presence or absence of actual messages indistinguishable to observers.
It helps achieve _unobservability_ where a passive adversary cannot determine whether a node is sending real messages or not.

In the Mix Protocol, cover traffic is limited to _loop messages_&mdash;dummy Sphinx packets that follow a valid mix path and return to the originating node.
These messages carry no application payload but are indistinguishable from real messages in structure, size, and routing behavior.

Cover traffic MAY be generated by either mix nodes or senders.
The strategy for generating such traffic&mdash;such as timing and frequency&mdash;is pluggable and not specified in this document.

Implementations that support cover traffic SHOULD generate loop messages at randomized intervals.
This helps mask actual sending behavior and increases the effective anonymity set.
Timing strategies such as Poisson processes or exponential delays are commonly used, but the choice is left to the implementation.

In addition to enhancing privacy, loop messages can be used to assess network liveness or path reliability without requiring explicit acknowledgments.

### 6.5 Incentivization

The Mix Protocol supports a simple tit-for-tat model to discourage free-riding and promote mix node participation.
In this model, nodes that wish to send anonymous messages using the Mix Protocol MUST also operate a mix node.
This requirement ensures that participants contribute to the anonymity set they benefit from, fostering a minimal form of fairness and reciprocity.

This tit-for-tat model is intentionally lightweight and decentralized.
It deters passive use of the mixnet by requiring each user to contribute bandwidth and processing capacity.
However, it does not guarantee the quality of service provided by participating nodes.
For example, it does not prevent nodes from running low-quality or misbehaving mix instances, nor does it deter participation by compromised or transient peers.

The Mix Protocol does not mandate any form of payment, token exchange, or accounting.
More sophisticated economic models&mdash;such as stake-based participation, credentialed relay networks, or zero-knowledge proof-of-contribution systems&mdash;MAY be layered on top of the protocol or enforced via external coordination.

Additionally, network operators or application-layer policies MAY require nodes to maintain minimum uptime, prove their participation, or adhere to service-level guarantees.

While the Mix Protocol defines a minimum participation requirement, additional incentivization extensions are considered pluggable and experimental in this version of the specification.
No specific mechanism is standardized.

### 6.6 DoS Protection

The Mix Protocol supports a pluggable DoS protection mechanism to defend the mixnet against denial-of-service (DoS) or resource exhaustion attacks.
Without DoS protection, malicious actors could flood mix nodes with valid Sphinx packets, exhausting computational resources or bandwidth of the mix nodes, eventually making them unusable.
Deployments MUST implement a DoS protection mechanism to make the mixnet robust under adversarial conditions.

The DoS protection mechanism is pluggable because different deployments may require different trade-offs between computational overhead, attack resistance, and Sybil resistance.
For a specific mix deployment, the same DoS protection mechanism MUST be followed by all participating mix nodes to ensure interoperability.

Detailed design requirements, architectural approaches, packet structure considerations, node responsibilities, and recommendations are specified in [Mix DoS Protection](./mix-dos-protection.md).

## 7. Core Mix Protocol Responsibilities

This section defines the core routing behavior of the Mix Protocol, which all conforming implementations MUST support.

The Mix Protocol defines the logic for anonymously routing messages through the decentralized mix network formed by participating libp2p nodes.
Each mix node MUST implement support for:

- initiating anonymous routing when invoked with a message.
- receiving and processing Sphinx packets when selected as a hop in a mix path.

These roles and their required behaviors are defined in the following subsections.

### 7.1 Protocol Identifier

The Mix Protocol is identified by the protocol string `"/mix/1.0.0"`.

All Mix Protocol interactions occur over libp2p streams negotiated using this identifier.
Each Sphinx packet transmission&mdash;whether initiated locally or forwarded as part of a mix path&mdash;involves opening a new libp2p stream to the next hop.
Implementations MAY optimize performance by reusing streams where appropriate;
see [Section 5.5](#55-stream-management-and-multiplexing) for more details on stream management.

### 7.2 Initiation

A mix node initiates anonymous routing only when it is explicitly invoked with a message to be routed.
As specified in [Section 5.2](#52-mixify-option), the decision to anonymize a message is made by the origin protocol.
When anonymization is required, the origin protocol instance forwards the message to the Mix Entry Layer, which then passes the message to the local Mix Protocol instance for routing.

To perform message initiation, a mix node MUST:

- Select a random mix path.
- Assign a delay value for each hop and encode it into the Sphinx packet header.
- Wrap the message in a Sphinx packet by applying layered encryption in reverse order of nodes in the selected mix path.
- Forward the resulting packet to the first mix node in the mix path using the Mix Protocol.

The Mix Protocol does not interpret message content or origin protocol context.
Each invocation is stateless, and the implementation MUST NOT retain routing metadata or per-message state after the packet is forwarded.

### 7.3 Sphinx Packet Receiving and Processing

A mix node that receives a Sphinx packet is oblivious to its position in the path.
The first hop is indistinguishable from other intermediary hops in terms of processing and behavior.

After decrypting one layer of the Sphinx packet, the node MUST inspect the routing information.
If this layer indicates that the next hop is the final destination, the packet MUST be processed as an exit.
Otherwise, it MUST be processed as an intermediary.

#### 7.3.1 Intermediary Processing

To process a Sphinx packet as an intermediary, a mix node MUST:

- Extract the next hop address and associated delay from the decrypted packet.
- Wait for the specified delay.
- Forward the updated packet to the next hop using the Mix Protocol.

A mix node performing intermediary processing MUST treat each packet as stateless and self-contained.

#### 7.3.2 Exit Processing

To process a Sphinx packet as an exit, a mix node MUST:

- Extract the plaintext message from the final decrypted packet.
- Validate any attached exit abuse prevention proof.
- Discard the message if validation fails.
- Forward the valid message to the Mix Exit Layer for delivery to the destination origin protocol instance.

The node MUST NOT retain decrypted content after forwarding.

The routing behavior described in this section relies on the use of Sphinx packets to preserve unlinkability and confidentiality across hops.
The next section specifies their structure, cryptographic components, and construction.

## 8. Sphinx Packet Format

The Mix Protocol uses the Sphinx packet format to enable unlinkable, multi-hop message routing with per-hop confidentiality and integrity.
Each message transmitted through the mix network is encapsulated in a Sphinx packet constructed by the initiating mix node.
The packet is encrypted in layers such that each hop in the mix path can decrypt exactly one layer and obtain the next-hop routing information and forwarding delay, without learning the complete path or the message origin.
Only the final hop learns the destination, which is encoded in the innermost routing layer.

Sphinx packets are self-contained and indistinguishable on the wire, providing strong metadata protection.
Mix nodes forward packets without retaining state or requiring knowledge of the source or destination beyond their immediate routing target.

To ensure uniformity, each Sphinx packet consists of a fixed-length header and a payload that is padded to a fixed maximum size.
Although the original message payload may vary in length, padding ensures that all packets are identical in size on the wire.
This ensures unlinkability and protects against correlation attacks based on message size.

If a message exceeds the maximum supported payload size, it MUST be fragmented before being passed to the Mix Protocol.
Fragmentation and reassembly are the responsibility of the origin protocol or the top-level application.
The Mix Protocol handles only messages that do not require fragmentation.

The structure, encoding, and size constraints of the Sphinx packet are detailed in the following subsections.

### 8.1 Packet Structure Overview

Each Sphinx packet consists of three fixed-length header fields&mdash; $α$, $β$, and $γ$ &mdash;followed by a fixed-length encrypted payload $δ$.
Together, these components enable per-hop message processing with strong confidentiality and integrity guarantees in a stateless and unlinkable manner.

- **$α$ (Alpha)**: An ephemeral public value. Each mix node uses its private key and $α$ to derive a shared session key for that hop. This session key is used to decrypt and process one layer of the packet.
- **$β$ (Beta)**: The nested encrypted routing information. It encodes the next hop address, the forwarding delay, integrity check $γ$ for the next hop, and the $β$ for subsequent hops. At the final hop, $β$ encodes the destination address and fixed-length zero padding to preserve uniform size.
- **$γ$ (Gamma)**: A message authentication code computed over $β$ using the session key derived from $α$. It ensures header integrity at each hop.
- **$δ$ (Delta)**: The encrypted payload. It consists of the message padded to a fixed maximum length and encrypted in layers corresponding to each hop in the mix path.

At each hop, the mix node derives the session key from $α$, verifies the header integrity using $γ$, decrypts one layer of $β$ to extract the next hop and delay, and decrypts one layer of $δ$.
It then constructs a new packet with updated values of $α$, $β$, $γ$, and $δ$, and forwards it to the next hop.
At the final hop, the mix node decrypts the innermost layer of $β$ and $δ$, which yields the destination address and the original application message respectively.

All Sphinx packets are fixed in size and indistinguishable on the wire.
This uniform format, combined with layered encryption and per-hop integrity protection, ensures unlinkability, tamper resistance, and robustness against correlation attacks.

The structure and semantics of these fields, the cryptographic primitives used, and the construction and processing steps are defined in the following subsections.

### 8.2 Cryptographic Primitives

This section defines the cryptographic primitives used in Sphinx packet construction and processing.

- **Security Parameter**: All cryptographic operations target a minimum of $κ = 128$ bits of security, balancing performance with resistance to modern attacks.

- **Elliptic Curve Group $\mathbb{G}$**:

  - **Curve**: Curve25519
  - **Notation**: Let $g$ denote the canonical base point (generator) of $\mathbb{G}$.
  - **Purpose**: Used for deriving a Diffie–Hellman-style shared key at each hop using $α$.
  - **Representation**: Small 32-byte group elements, efficient for both encryption and key exchange.
  - **Scalar Field**: The curve is defined over the finite field $\mathbb{Z}_q$, where $q = 2^{252} + 27742317777372353535851937790883648493$. Ephemeral exponents used in Sphinx packet construction are selected uniformly at random from $\mathbb{Z}_q^*$, the multiplicative subgroup of $\mathbb{Z}_q$.

- **Hash Function**:

  - **Construction**: SHA-256
  - **Notation**: The hash function is denoted by $H(\cdot)$ in subsequent sections.

- **Key Derivation Function (KDF)**:

  - **Purpose**: To derive encryption keys, IVs, and MAC key from the shared session key at each hop.
  - **Construction**: SHA-256 hash with output truncated to $128$ bits.
  - **Key Derivation**: The KDF key separation labels (_e.g.,_ `"aes_key"`, `"mac_key"`) are fixed strings and MUST be agreed upon across implementations.

- **Symmetric Encryption**: AES-128 in Counter Mode (AES-CTR)

  - **Purpose**: To encrypt $β$ and $δ$ for each hop.
  - **Keys and IVs**: Each derived from the session key for the hop using the KDF.

- **Message Authentication Code (MAC)**:
  - **Construction**: HMAC-SHA-256 with output truncated to $128$ bits.
  - **Purpose**: To compute $γ$ for each hop.
  - **Key**: Derived using KDF from the session key for the hop.

These primitives are used consistently throughout packet construction and decryption, as described in the following sections.

### 8.3 Packet Component Sizes

This section defines the size of each component in a Sphinx packet, deriving them from the security parameter and protocol parameters introduced earlier.
All Sphinx packets MUST be fixed in length to ensure uniformity and indistinguishability on the wire.
The serialized packet is structured as follows:

```text
+--------+----------+--------+----------+
|   α    |     β    |   γ    |    δ     |
| 32 B   | variable | 16 B   | variable |
+--------+----------+--------+----------+
```

#### 8.3.1 Header Field Sizes

The header consists of the fields $α$, $β$, and $γ$, totaling a fixed size per maximum path length:

- **$α$ (Alpha)**: 32 bytes
  The size of $α$ is determined by the elliptic curve group representation used (Curve25519), which encodes group elements as 32-byte values.

- **$β$ (Beta)**: $(r(t + 1) + 1)κ$ bytes
  The size of $β$ depends on:

  - **Maximum path length ($r$)**: The recommended value of $r=5$ balances bandwidth versus anonymity tradeoffs.
  - **Combined address and delay width ($tκ$)**: The recommended $t=6$ accommodates standard libp2p relay multiaddress representations plus a 2-byte delay field. While the actual multiaddress and delay fields may be shorter, they are padded to $tκ$ bytes to maintain fixed field size. The structure and rationale for the $tκ$ block and its encoding are specified in [Section 8.4](#84-address-and-delay-encoding).

    Note:
    This expands on the original [Sphinx packet format](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf), which embeds a fixed $κ$-byte mix node identifier per hop in $β$.
    The Mix Protocol generalizes this to $tκ$ bytes to accommodate libp2p multiaddresses and forwarding delays while preserving the cryptographic properties of the original design.

  - **Per-hop $γ$ size ($κ$)** (defined below): Accounts for the integrity tag included with each hop's routing information.

  Using the recommended value of $r=5$ and $t=6$, the resulting $β$ size is $576$ bytes.
  At the final hop, $β$ encodes the destination address in the first $tκ-2$ bytes and the remaining bytes are zero-padded.

- **$γ$ (Gamma)**: $16$ bytes
  The size of $γ$ equals the security parameter $κ$, providing a $κ$-bit integrity tag at each hop.

Thus, the total header length is:

$`
\begin{aligned}
|Header| &= α + β + γ \\
  &= 32 + (r(t + 1) + 1)κ + 16
\end{aligned}
`$

Notation: $|x|$ denotes the size (in bytes) of field $x$.

Using the recommended value of $r = 5$ and $t = 6$, the header size is:

$`
\begin{aligned}
|Header| &= 32 + 576 + 16 \\
  &= 624 \ bytes
\end{aligned}
`$

#### 8.3.2 Payload Size

This subsection defines the size of the encrypted payload $δ$ in a Sphinx packet.

$δ$ contains the application message, padded to a fixed maximum length to ensure all packets are indistinguishable on the wire.
The size of $δ$ is calculated as:

$`
\begin{aligned}
|δ| &= TotalPacketSize - HeaderSize
\end{aligned}
`$

The recommended total packet size is $4608$ bytes, chosen to:

- Accommodate larger libp2p application messages, such as those commonly observed in Status chat using Waku (typically ~4KB payloads),
- Allow inclusion of additional data such as SURBs without requiring fragmentation,
- Maintain reasonable per-hop processing and bandwidth overhead.

Note:
When [DoS protection](#66-dos-protection) is enabled, the maximum packet size MUST be increased to accommodate the proof size of the chosen DoS protection mechanism.

This recommended total packet size of $4608$ bytes yields:

$`
\begin{aligned}
Payload &= 4608 - 624 \\
  &= 3984\ bytes
\end{aligned}
`$

Implementations MUST account for payload extensions, such as SURBs, when determining the maximum message size that can be encapsulated in a single Sphinx packet.
Details on SURBs are defined in [Section 8.7.1](#871-surb-component-sizes).

The following subsection defines the padding and fragmentation requirements for ensuring this fixed-size constraint.

#### 8.3.3 Padding and Fragmentation

Implementations MUST ensure that all messages shorter than the maximum payload size are padded before Sphinx encapsulation to ensure that all packets are indistinguishable on the wire.
Messages larger than the maximum payload size MUST be fragmented by the origin protocol or top-level application before being passed to the Mix Protocol.
Reassembly is the responsibility of the consuming application, not the Mix Protocol.

#### 8.3.4 Anonymity Set Considerations

The fixed maximum packet size is a configurable parameter.
Protocols or applications that choose to configure a different packet size (either larger or smaller than the default) MUST be aware that using unique or uncommon packet sizes can reduce their effective anonymity set to only other users of the same size.
Implementers SHOULD align with widely used defaults to maximize anonymity set size.

Similarly, parameters such as $r$ and $t$ are configurable.
Changes to these parameters affect header size and therefore impact payload size if the total packet size remains fixed.
However, if such changes alter the total packet size on the wire, the same anonymity set considerations apply.

The following subsection defines how the next-hop or destination address and forwarding delay are encoded within $β$ to enable correct routing and mixing behavior.

### 8.4 Address and Delay Encoding

Each hop's $β$ includes a fixed-size block containing the next-hop address and the forwarding delay, except for the final hop, which encodes the destination address and a delay-sized zero padding.
This section defines the structure and encoding of that block.

The combined address and delay block MUST be exactly $tκ$ bytes in length, as defined in [Section 8.3.1](#831-header-field-sizes), regardless of the actual address or delay values.
The first $(tκ - 2)$ bytes MUST encode the address, and the final $2$ bytes MUST encode the forwarding delay.
This fixed-length encoding ensures that packets remain indistinguishable on the wire and prevents correlation attacks based on routing metadata structure.

Implementations MAY use any address and delay encoding format agreed upon by all participating mix nodes, as long as the combined length is exactly $tκ$ bytes.
The encoding format MUST be interpreted consistently by all nodes within a deployment.

For interoperability, a recommended default encoding format involves:

- Encoding the next-hop or destination address as a libp2p multi-address:

  - To keep the address block compact while allowing relay connectivity, each mix node is limited to one IPv4 circuit relay multiaddress. This ensures that most nodes can act as mix nodes, including those behind NATs or firewalls.
  - In libp2p terms, this combines transport addresses with multiple peer identities to form an address that describes a relay circuit:
    `/ip4/<ipv4>/tcp/<port>/p2p/<relayPeerID>/p2p-circuit/p2p/<relayedPeerID>`
    Variants may include directly reachable peers and transports such as `/quic-v1`, depending on the mix node's supported stack.
  - IPv6 support is deferred, as it adds $16$ bytes just for the IP field.
  - Future revisions may extend this format to support IPv6 or DNS-based multiaddresses.

  With these constraints, the recommended encoding layout is:

  - IPv4 address (4 bytes)
  - Protocol identifier _e.g.,_ TCP or QUIC (1 byte)
  - Port number (2 bytes)
  - Peer IDs (39 bytes, post-Base58 decoding)

- Encoding the forwarding delay as an unsigned 16-bit integer (2 bytes), representing the mean delay in milliseconds for the configured delay distribution, using big endian network byte order.
The delay distribution is pluggable, as defined in [Section 6.2](#62-delay-strategy).

If the encoded address or delay is shorter than its respective allocated field, it MUST be padded with zeros.
If it exceeds the allocated size, it MUST be rejected or truncated according to the implementation policy.

Note:
Future versions of the Mix Protocol may support address compression by encoding only the peer identifier and relying on external peer discovery mechanisms to retrieve full multiaddresses at runtime.
This would allow for more compact headers and greater address flexibility, but requires fast and reliable lookup support across deployments.
This design is out of scope for the current version.

With the field sizes and encoding conventions established, the next section describes how a mix node constructs a complete Sphinx packet when initiating the Mix Protocol.

### 8.5 Packet Construction

This section defines how a mix node constructs a Sphinx packet when initiating the Mix Protocol on behalf of a local origin protocol instance.
The construction process wraps the message in a sequence of encryption layers&mdash;one for each hop&mdash;such that only the corresponding mix node can decrypt its layer and retrieve the routing instructions for that hop.

#### 8.5.1 Inputs

To initiate the Mix Protocol, the origin protocol instance submits a message to the Mix Entry Layer on the same node.
This layer forwards it to the local Mix Protocol instance, which constructs a Sphinx packet using the following REQUIRED inputs:

- **Application message**: The serialized message provided by the origin protocol instance. The Mix Protocol instance applies any configured exit abuse prevention mechanism and attaches one or two SURBs prior to encapsulating the message in the Sphinx packet. The initiating node MUST ensure that the resulting payload size does not exceed the maximum supported size defined in [Section 8.3.2](#832-payload-size).
- **Origin protocol codec**: The libp2p protocol string corresponding to the origin protocol instance. This is included in the payload so that the exit node can route the message to the intended destination protocol after decryption.
- **Mix Path length $L$**: The number of mix nodes to include in the path. The mix path MUST consist of at least three hops, each representing a distinct mix node.
- **Destination address $Δ$**: The routing address of the intended recipient of the message. This address is encoded in $(tκ - 2)$ bytes as defined in [Section 8.4](#84-address-and-delay-encoding) and revealed only at the last hop.

#### 8.5.2 Construction Steps

This subsection defines how the initiating mix node constructs a complete Sphinx packet using the inputs defined in [Section 8.5.1](#851-inputs).
The construction MUST follow the cryptographic structure defined in [Section 8.1](#81-packet-structure-overview), use the primitives specified in [Section 8.2](#82-cryptographic-primitives), and adhere to the component sizes and encoding formats from [Section 8.3](#83-packet-component-sizes) and [Section 8.4](#84-address-and-delay-encoding).

The construction MUST proceed as follows:

1. **Prepare Application Message**

   - Apply any configured exit abuse prevention mechanism (_e.g.,_ PoW, VDF, RLN) to the serialized message.
   Exit abuse prevention mechanisms are pluggable as defined in [Section 6.3](#63-exit-abuse-prevention).
   - Attach one or more SURBs, if required, following the steps in [Section 8.7.2](#872-surb-creation).
   - Append the origin protocol codec in a format that enables the exit node to reliably extract it during parsing. A recommended encoding approach is to prefix the codec string with its length, encoded as a compact varint field limited to two bytes. Regardless of the scheme used, implementations MUST agree on the format within a deployment to ensure deterministic decoding.
   - Pad the result to the maximum application message length of $3968$ bytes using a deterministic padding scheme. This value is derived from the fixed payload size in [Section 8.3.2](#832-payload-size) ($3984$ bytes) minus the security parameter $κ = 16$ bytes defined in [Section 8.2](#82-cryptographic-primitives). The chosen scheme MUST yield a fixed-size padded output and MUST be consistent across all mix nodes to ensure correct interpretation during unpadding. For example, schemes that explicitly encode the padding length and prepend zero-valued padding bytes MAY be used.
   - Let the resulting message be $m$.

2. **Select A Mix Path**

   - First obtain an unbiased random sample of live, routable mix nodes using some discovery mechanism. The choice of discovery mechanism is deployment-specific as defined in [Section 6.1](#61-discovery). The discovery mechanism MUST be unbiased and provide, at a minimum, the multiaddress and X25519 public key of each mix node.
   - From this sample, choose a random mix path of length $L \geq 3$. As defined in [Section 2](#2-terminology), a mix path is a non-repeating sequence of mix nodes.
   - For each hop $i \in \{0 \ldots L-1\}$:
     - Retrieve the multiaddress and corresponding X25519 public key $y_i$ of the $i$-th mix node.
     - Encode the multiaddress in $(tκ - 2)$ bytes as defined in [Section 8.4](#84-address-and-delay-encoding). Let the resulting encoded multiaddress be $\mathrm{addr\_i}$.

3. **Wrap Plaintext Payload In Sphinx Packet**

   a. **Compute Ephemeral Secrets**

   - Choose a random private exponent $x \in_R \mathbb{Z}_q^*$.
   - Initialize:

     $`
     \begin{aligned}
     α_0 &= g^x \\
     s_0 &= y_0^x \\
     b_0 &= H(α_0\ |\ s_0)
     \end{aligned}
     `$
   - For each hop $i$ (from $1$ to $L-1$), compute:

     $`
     \begin{aligned}
     α_i &= α_{i-1}^{b_{i-1}} \\
     s_i &= y_{i}^{x\prod_{\text{j=0}}^{\text{i-1}} b_{j}} \\
     b_i &= H(α_i\ |\ s_i)
     \end{aligned}
     `$

   Note that the length of $α_i$ is $32$ bytes, $0 \leq i \leq L-1$ as defined in [Section 8.3.1](#831-header-field-sizes).

   b. **Compute Per-Hop Filler Strings**

   Filler strings are encrypted strings that are appended to the header during encryption.
   They ensure that the header length remains constant across hops, regardless of the position of a node in the mix path.

   To compute the sequence of filler strings, perform the following steps:

   - Initialize $Φ_0 = \epsilon$ (empty string).
   - For each $i$ (from $1$ to $L-1$):

     - Derive per-hop AES key and IV:

       $`
       \begin{array}{l}
       Φ_{\mathrm{aes\_key}_{i-1}} =
       \mathrm{KDF}(\text{"aes\_key"} \mid s_{i-1})\\
       Φ_{\mathrm{iv}_{i-1}} =
       \mathrm{KDF}(\text{"iv"} \mid s_{i-1})
       \end{array}
       `$

     - Compute the filler string $Φ_i$ using $\text{AES-CTR}^\prime_i$, which is AES-CTR encryption with the keystream starting from index $((t+1)(r-i)+t+2)κ$ :

       $`
       \begin{array}{l}
       Φ_i = \mathrm{AES\text{-}CTR}'_i\bigl(Φ_{\mathrm{aes\_key}_{i-1}},
       Φ_{\mathrm{iv}_{i-1}}, Φ_{i-1} \mid 0_{(t+1)κ} \bigr)
       \end{array}
       `$

       where $0_x$ defines the string of $0$ bits of length $x$.

   Note that the length of $Φ_i$ is $(t+1)iκ$, $0 \leq i \leq L-1$.

   c. **Construct Routing Header**
   The routing header as defined in [Section 8.1](#81-packet-structure-overview) is the encrypted structure that carries the forwarding instructions for each hop.
   It ensures that a mix node can learn only its immediate next hop and forwarding delay without inferring the full path.

   Filler strings computed in the previous step are appended during encryption to ensure that the header length remains constant across hops.
   This prevents a node from distinguishing its position in the path based on header size.

   To construct the routing header, perform the following steps for each hop $i = L-1$ down to $0$, recursively:

   - Derive per-hop AES key, MAC key, and IV:

     $`
     \begin{array}{l}
     β_{\mathrm{aes\_key}_i} =
     \mathrm{KDF}(\text{"aes\_key"} \mid s_i)\\
     \mathrm{mac\_key}_i =
     \mathrm{KDF}(\text{"mac\_key"} \mid s_{i})\\
     β_{\mathrm{iv}_i} =
     \mathrm{KDF}(\text{"iv"} \mid s_i)
     \end{array}
     `$

   - Set the per hop two-byte encoded delay $\mathrm{delay}_i$ as defined in [Section 8.4](#84-address-and-delay-encoding):

     - If final hop (_i.e.,_ $i = L - 1$), encode two-byte zero padding.
     - For all other hop $i$, $i < L - 1$, select the mean forwarding delay for the delay strategy configured by the application, and encode it as a two-byte value. The delay strategy is pluggable, as defined in [Section 6.2](#62-delay-strategy).

   - Using the derived keys and encoded forwarding delay, compute the nested encrypted routing information $β_i$:

     - If $i = L-1$ (_i.e.,_ exit node):

       $`
       \begin{array}{l}
       β_i = \mathrm{AES\text{-}CTR}\bigl(β_{\mathrm{aes\_key}_i},
       β_{\mathrm{iv}_i}, Δ \mid \mathrm{delay}_i \mid 0_{((t+1)(r-L)+2)κ}
       \bigr) \bigm| Φ_{L-1}
       \end{array}
       `$

     - Otherwise (_i.e.,_ intermediary node):

       $`
       \begin{array}{l}
       β_i = \mathrm{AES\text{-}CTR}\bigl(β_{\mathrm{aes\_key}_i},
       β_{\mathrm{iv}_i}, \mathrm{addr}_{i+1} \mid \mathrm{delay}_i
       \mid γ_{i+1} \mid β_{i+1 \, [0 \ldots (r(t+1) - t)κ - 1]} \bigr)
       \end{array}
       `$

       where $X_{[a \ldots b]}$ denotes the substring of $X$ from byte offset $a$ to $b$, inclusive, using zero-based indexing.

     Note that the length of $\beta_i$ is $(r(t+1)+1)κ$, $0 \leq i \leq L-1$ as defined in [Section 8.3.1](#831-header-field-sizes).

     - Compute the message authentication code $γ_i$:

       $`
       \begin{array}{l}
       γ_i = \mathrm{HMAC\text{-}SHA\text{-}256}\bigl(\mathrm{mac\_key}_i,
       β_i \bigr)
       \end{array}
       `$

     Note that the length of $\gamma_i$ is $κ$, $0 \leq i \leq L-1$ as defined in [Section 8.3.1](#831-header-field-sizes).

   d. **Encrypt Payload**
   The encrypted payload $δ$ contains the message $m$ defined in step 1, prepended with a $κ$-byte string of zeros.
   It is encrypted in layers such that each hop in the mix path removes exactly one layer using the per-hop session key.
   This ensures that only the final hop (_i.e.,_ the exit node) can fully recover $m$, validate its integrity, and forward it to the destination.
   To compute the encrypted payload, perform the following steps for each hop $i = L-1$ down to $0$, recursively:

   - Derive per-hop AES key and IV:

     $`
     \begin{array}{l}
     δ_{\mathrm{aes\_key}_i} =
     \mathrm{KDF}(\text{"δ\_aes\_key"} \mid s_i)\\
     δ_{\mathrm{iv}_i} =
     \mathrm{KDF}(\text{"δ\_iv"} \mid s_i)
     \end{array}
     `$

   - Using the derived keys, compute the encrypted payload $δ_i$:

     - If $i = L-1$ (_i.e.,_ exit node):

       $`
       \begin{array}{l}
       δ_i = \mathrm{AES\text{-}CTR}\bigl(δ_{\mathrm{aes\_key}_i},
       δ_{\mathrm{iv}_i}, 0_{κ} \mid m
       \bigr)
       \end{array}
       `$

     - Otherwise (_i.e.,_ intermediary node):

       $`
       \begin{array}{l}
       δ_i = \mathrm{AES\text{-}CTR}\bigl(δ_{\mathrm{aes\_key}_i},
       δ_{\mathrm{iv}_i}, δ_{i+1} \bigr)
       \end{array}
       `$

     Note that the length of $\delta_i$, $0 \leq i \leq L-1$ is $|m| + κ$ bytes.

     Given that the derived size of $\delta_i$ is $3984$ bytes as defined in [Section 8.3.2](#832-payload-size), this allows $m$ to be of length $3984-16 = 3968$ bytes as defined in step 1.

   e. **Assemble Final Packet**
   The final Sphinx packet is structured as defined in [Section 8.3](#83-packet-component-sizes):

   ```text
   α = α_0      // 32 bytes
   β = β_0      // 576 bytes
   γ = γ_0      // 16 bytes
   δ = δ_0      // 3984 bytes
   ```

   Serialize the final packet using a consistent format and prepare it for transmission.

   f. **Transmit Packet**

   - Sample a randomized delay from the same distribution family used for per-hop delays (in step 3.c.) with an independently chosen mean.

   This delay prevents timing correlation when multiple Sphinx packets are sent in quick succession.
   Such bursts may occur when an upstream protocol fragments a large message, or when several messages are sent close together.

   - After the randomized delay elapses, transmit the serialized packet to the first hop via a libp2p stream negotiated under the `"/mix/1.0.0"` protocol identifier.

   Implementations MAY reuse an existing stream to the first hop as described in [Section 5.5](#55-stream-management-and-multiplexing), if doing so does not introduce any observable linkability between the packets.

Once a Sphinx packet is constructed and transmitted by the initiating node, it is processed hop-by-hop by the remaining mix nodes in the path.
Each node receives the packet over a libp2p stream negotiated under the `"/mix/1.0.0"` protocol.
The following subsection defines the per-hop packet handling logic expected of each mix node, depending on whether it acts as an intermediary or an exit.

### 8.6 Sphinx Packet Handling

Each mix node MUST implement a handler for incoming data received over libp2p streams negotiated under the `"/mix/1.0.0"` protocol identifier.
The incoming stream may have been reused by the previous hop, as described in [Section 5.5](#55-stream-management-and-multiplexing).
Implementations MUST ensure that packet handling remains stateless and unlinkable, regardless of stream reuse.

Upon receiving the stream payload, the node MUST interpret it as a Sphinx packet and process it in one of two roles&mdash;intermediary or exit&mdash; as defined in [Section 7.3](#73-sphinx-packet-receiving-and-processing).
This section defines the exact behavior for both roles.

#### 8.6.1 Shared Preprocessing

Upon receiving a stream payload over a libp2p stream, the mix node MUST first deserialize it into a Sphinx packet `(α, β, γ, δ)`.

The deserialized fields MUST match the sizes defined in [Section 8.5.2](#852-construction-steps) Step 3.e., and the total packet length MUST match the fixed packet size defined in [Section 8.3.2](#832-payload-size).

If the stream payload does not match the expected length, it MUST be discarded and the processing MUST terminate.

After successful deserialization, the mix node performs the following steps:

1. **Derive Session Key**

   Let $x \in \mathbb{Z}_q^*$ denote the node's X25519 private key.
   Compute the shared secret $s = α^x$.

2. **Check for Replays**

   - Compute the tag $H(s)$.
   - If the tag exists in the node's table of previously seen tags, discard the packet and terminate processing.
   - Otherwise, store the tag in the table.

   The table MAY be flushed when the node rotates its private key.
   Implementations SHOULD perform this cleanup securely and automatically.

3. **Check Header Integrity**

   - Derive the MAC key from the session secret $s$:

     $`
     \begin{array}{l}
     \mathrm{mac\_key} =
     \mathrm{KDF}(\text{"mac\_key"} \mid s)
     \end{array}
     `$

   - Verify the integrity of the routing header:

     $`
     \begin{array}{l}
     γ \stackrel{?}{=} \mathrm{HMAC\text{-}SHA\text{-}256}(\mathrm{mac\_key},
     β)
     \end{array}
     `$

     If the check fails, discard the packet and terminate processing.

4. **Decrypt One Layer of the Routing Header**

   - Derive the routing header AES key and IV from the session secret $s$:

     $`
     \begin{array}{l}
     β_{\mathrm{aes\_key}} =
     \mathrm{KDF}(\text{"aes\_key"} \mid s)\\
     β_{\mathrm{iv}} =
     \mathrm{KDF}(\text{"iv"} \mid s)
     \end{array}
     `$

   - Decrypt the suitably padded $β$ to obtain the routing block $B$ for this hop:

     $`
     \begin{array}{l}
     B = \mathrm{AES\text{-}CTR}\bigl(β_{\mathrm{aes\_key}},
     β_{\mathrm{iv}}, β \mid 0_{(t+1)κ}
     \bigr)
     \end{array}
     `$

     This step removes the filler string appended during header encryption in [Section 8.5.2](#852-construction-steps) Step 3.c. and yields the plaintext routing information for this hop.

   The routing block $B$ MUST be parsed according to the rules and field layout defined in [Section 8.6.2](#862-node-role-determination) to determine whether the current node is an intermediary or the exit.

5. **Decrypt One Layer of the Payload**

   - Derive the payload AES key and IV from the session secret $s$:

     $`
     \begin{array}{l}
     δ_{\mathrm{aes\_key}} =
     \mathrm{KDF}(\text{"δ\_aes\_key"} \mid s)\\
     δ_{\mathrm{iv}} =
     \mathrm{KDF}(\text{"δ\_iv"} \mid s)
     \end{array}
     `$

   - Decrypt one layer of the encrypted payload $δ$:

     $`
     \begin{array}{l}
     δ' = \mathrm{AES\text{-}CTR}\bigl(δ_{\mathrm{aes\_key}},
     δ_{\mathrm{iv}}, δ \bigr)
     \end{array}
     `$

   The resulting $δ'$ is the decrypted payload for this hop and MUST be interpreted depending on the parsed node's role, determined by $B$, as described in [Section 8.6.2](#862-node-role-determination).

#### 8.6.2 Node Role Determination

As described in [Section 8.6.1](#861-shared-preprocessing), the mix node obtains the routing block $B$ by decrypting one layer of the encrypted header $β$.

At this stage, the node MUST determine whether it is an intermediary or the exit based on the prefix of $B$, in accordance with the construction of $β_i$ defined in [Section 8.5.2](#852-construction-steps) Step 3.c.:

- If $B_{[(tκ-2)\ldots tκ-1]}$ contains a two-byte zero delay, process the packet as an exit.
- Otherwise, process the packet as an intermediary.

The following subsections define the precise behavior for each case.

#### 8.6.3 Intermediary Processing

Once the node determines its role as an intermediary following the steps in [Section 8.6.2](#862-node-role-determination), it MUST perform the following steps to interpret routing block $B$ and decrypted payload $δ'$ obtained in [Section 8.6.1](#861-shared-preprocessing):

1. **Parse Routing Block**

   Parse the routing block $B$ according to the $β_i$, $i \neq L - 1$ construction defined in [Section 8.5.2](#852-construction-steps) Step 3.c.:

   - Extract the first $(tκ - 2)$ bytes of $B$ as the next hop address $\mathrm{addr}$

     $`
     \begin{array}{l}
     \mathrm{addr} = B_{[0\ldots(tκ - 2) - 1]}
     \end{array}
     `$

   - Extract the next two bytes as the mean delay $\mathrm{delay}$

     $`
     \begin{array}{l}
     \mathrm{delay} = B_{[(tκ - 2)\ldots{tκ} - 1]}
     \end{array}
     `$

   - Extract the next $κ$ bytes as the next hop MAC $γ'$

     $`
     \begin{array}{l}
     γ' = B_{[tκ\ldots(t + 1)κ - 1]}
     \end{array}
     `$

   - Extract the next $(r(t+1)+1)κ$ bytes as the next hop routing information $β'$

     $`
     \begin{array}{l}
     β' = B_{[(t + 1)κ\ldots(r(t + 1) + t + 2)κ - 1]}
     \end{array}
     `$

   If parsing fails, discard the packet and terminate processing.

2. **Update Header Fields**

   Update the header fields according to the construction steps defined in [Section 8.5.2](#852-construction-steps):

   - Compute the next hop ephemeral public value $α'$, deriving the blinding factor $b$ from the shared secret $s$ computed in [Section 8.6.1](#861-shared-preprocessing) Step 1.

     $`
     \begin{aligned}
     b &= H(α\ |\ s) \\
     α' &= α^b
     \end{aligned}
     `$

   - Use the $β'$ and $γ'$ extracted in step 1. as the routing information and MAC respectively in the outgoing packet.

3. **Update Payload**

   Use the decrypted payload $δ'$ computed in [Section 8.6.1](#861-shared-preprocessing) Step 5. as the payload in the outgoing packet.

4. **Assemble Final Packet**
   The final Sphinx packet is structured as defined in [Section 8.3](#83-packet-component-sizes):

   ```text
   α = α'      // 32 bytes
   β = β'      // 576 bytes
   γ = γ'      // 16 bytes
   δ = δ'      // 3984 bytes
   ```

   Serialize $α'$ using the same format used in [Section 8.5.2](#852-construction-steps).
   The remaining fields are already fixed-length buffers and do not require further transformation.

5. **Transmit Packet**

   - Interpret the $\mathrm{addr}$ and $\mathrm{delay}$ extracted in step 1. according to the encoding format used during construction in [Section 8.5.2](#852-construction-steps) Step 3.c.

   - Sample the actual forwarding delay from the configured delay distribution, using the decoded mean delay value as the distribution parameter.

   - After the forwarding delay elapses, transmit the serialized packet to the next hop address via a libp2p stream negotiated under the `"/mix/1.0.0"` protocol identifier.

   Implementations MAY reuse an existing stream to the next hop as described in [Section 5.5](#55-stream-management-and-multiplexing), if doing so does not introduce any observable linkability between the packets.

6. **Erase State**

   - After transmission, erase all temporary values securely from memory, including session keys, decrypted content, and routing metadata.

   - If any error occurs&mdash;such as malformed header, invalid delay, or failed stream transmission&mdash;silently discard the packet and do not send any error response.

#### 8.6.4 Exit Processing

Once the node determines its role as an exit following the steps in [Section 8.6.2](#862-node-role-determination), it MUST determine the exit message type from the routing block $B$ obtained in [Section 8.6.1](#861-shared-preprocessing):

- If $B_{[0 \ldots tκ-3]}$ encodes zero address and $B_{[tκ \ldots tκ+κ-1]}$ is nonzero (_i.e.,_ contains a SURB identifier), the packet is a SURB reply.
  Process per [Section 8.7.4](#874-surb-reply-processing).

- Otherwise, the packet is a forward message.
  The node MUST perform the following steps to interpret routing block $B$ and decrypted payload $δ'$ obtained in [Section 8.6.1](#861-shared-preprocessing):

1. **Parse Routing Block**

   Parse the routing block $B$ according to the $β_i$, $i = L - 1$ construction defined in [Section 8.5.2](#852-construction-steps) Step 3.c.:

   - Extract the first $(tκ - 2)$ bytes of $B$ as the destination address $Δ$

     $`
     \begin{array}{l}
     Δ = B_{[0\ldots(tκ - 2) - 1]}
     \end{array}
     `$

2. **Recover Padded Application Message**

   - Verify the decrypted payload $δ'$ computed in [Section 8.6.1](#861-shared-preprocessing) Step 5.:

     $`
     \begin{array}{l}
     δ'_{[0\ldots{κ} - 1]} \stackrel{?}{=} 0_{κ}
     \end{array}
     `$

   If the check fails, discard $δ'$ and terminate processing.

   - Extract rest of the bytes of $δ'$ as the padded application message $m$:

     $`
     \begin{array}{l}
     m = δ'_{[κ\ldots]}
     \end{array}
     `$

     where $X_{[a \ldots]}$ denotes the substring of $X$ from byte offset $a$ to the end of the string, using zero-based indexing.

3. **Extract Application Message**

   Interpret recovered $m$ according to the construction steps defined in [Section 8.5.2](#852-construction-steps) Step 1.:

   - First, unpad $m$ using the deterministic padding scheme defined during construction.

   - Next, parse the unpadded message deterministically to extract:

     - optional exit abuse prevention proof
     - zero or more SURBs
     - the origin protocol codec
     - the serialized application message

   - Parse and deserialize the metadata fields required for exit abuse prevention validation, SURB extraction, and protocol codec identification, consistent with the format and extensions applied by the initiator.
     The application message itself MUST remain serialized.

   - If parsing fails at any stage, discard $m$ and terminate processing.

4. **Handoff to Exit Layer**

   - Hand off the serialized application message, the origin protocol codec, destination address $Δ$ (extracted in step 1.), and any SURBs extracted in step 3. to the local Exit Layer for further processing and delivery.

   - The Exit Layer is responsible for establishing a client-only connection and forwarding the message to the destination. Implementations MAY reuse an existing stream to the destination, if doing so does not introduce any observable linkability between forwarded messages.
     It is also responsible for storing any received SURBs and routing responses from the destination using them (see [Section 8.7.3](#873-using-a-surb)).

### 8.7 Single-Use Reply Blocks

A Single-Use Reply Block (SURB) allows the recipient of a Sphinx packet to send a reply without learning the sender's identity, the return mix path, or any forwarding delays.

A SURB MUST be used at most once. Reusing a SURB allows nodes on the return path to link multiple replies back to the original sender.

A SURB encodes a complete Sphinx header for a return path, a symmetric reply key, and a unique reply identifier. The initiating node constructs one or more SURBs and embeds them in the outgoing Sphinx packet payload. The recipient uses a SURB to reply — only the original sender can decrypt the reply.

This section defines SURB component sizes and total size ([Section 8.7.1](#871-surb-component-sizes)), how SURBs are created ([Section 8.7.2](#872-surb-creation)), used by the recipient ([Section 8.7.3](#873-using-a-surb)), processed by the exit node ([Section 8.7.4](#874-surb-reply-processing)), and recovered by the Exit Layer ([Section 8.7.5](#875-reply-recovery)).

#### 8.7.1 SURB Component Sizes

A SURB consists of the following components:

- **$\mathrm{hop}_0$**: $tκ - 2$ bytes. The address of the first mix node on the return path. Uses the same $tκ$ address block encoding defined in [Section 8.4](#84-address-and-delay-encoding), minus the 2-byte delay field, since no delay is encoded here.

- **$(α_0, β_0, γ_0)$**: A complete Sphinx header for the return path, with component sizes as defined in [Section 8.3.1](#831-header-field-sizes):
  - $α_0$: $32$ bytes. The ephemeral public value for the first hop.
  - $β_0$: $(r(t + 1) + 1)κ$ bytes.  The nested encrypted routing information for the return path.
  - $γ_0$: $κ$ bytes. The message authentication code computed over $β_0$ using the session key derived from $α_0$.

- **$\tilde{k}$**: $κ$ bytes. The reply key, sampled uniformly at random by the initiating node.

The total SURB size is:

$`
\begin{aligned}
|SURB| &= (tκ - 2) + 32 + (r(t + 1) + 1)κ + κ + κ \\
       &= 30 + (r(t + 1) + 3)κ + tκ
\end{aligned}
`$

Using the recommended parameters ($r = 5$, $t = 6$, $κ = 16$ bytes):

$`
\begin{aligned}
|SURB| &= 94 + 32 + 576 + 16 + 16 \\
       &= 734\ \text{bytes}
\end{aligned}
`$

Each SURB embedded in the message payload reduces the available application message space by $734$ bytes. With the allowable message size of $3968$ bytes derived in [Section 8.5.2](#852-construction-steps) Step 3.d, attaching $n$ SURBs leaves $3968 - (n \times 734)$ bytes for the application message, protocol codec, and any exit abuse prevention proof.

#### 8.7.2 SURB Creation

Depending on whether an application message requires a reply, the initiating node may create and attach one or more SURBs during its preparation ([Section 8.5.2](#852-construction-steps) Step 1) for Sphinx packet construction.
To construct each SURB, the initiating node MUST perform the following steps:

1. **Select Return Path and Compute Ephemeral Secrets**

   Select a return mix path of length $L \geq 3$ with the initiating node as the final hop. Compute the ephemeral public value $α_0$ and per-hop shared secrets $s_0, \ldots, s_{L-1}$ following the same procedure as [Section 8.5.2](#852-construction-steps) Steps 2 and 3.a.

2. **Sample SURB Identifier and Reply Key**

   Sample a unique SURB identifier $\mathrm{id}$ and a reply key $\tilde{k}$ of length $κ$ bytes uniformly at random.

3. **Construct Return Path Header**

   Compute per-hop filler strings and construct the routing header following the same procedure in [Section 8.5.2](#852-construction-steps) Steps 3.b and 3.c, with just $β_{L-1}$ computed as follows:

   $`
   \begin{array}{l}
   β_{L-1} = \mathrm{AES\text{-}CTR}\bigl(β_{\mathrm{aes\_key}_{L-1}},
   β_{\mathrm{iv}_{L-1}},
   0_{tκ} \mid \mathrm{id} \mid 0_{(((t+1)(r-L))+1)κ}
   \bigr) \bigm| Φ_{L-1}
   \end{array}
   `$

   That is, encode zero address and delay followed by the SURB identifier $\mathrm{id}$ in $β_{L-1}$. The SURB identifier is embedded so that the initiating node can match an incoming reply to the stored decryption keys in step 4 below.

   Use the same construction for the remaining routing blocks $β_i$, $0 \leq i < L-1$, and all per-hop MACs $γ_i$, $0 \leq i \leq L-1$.

   Note: A SURB construction follows the same steps for Sphinx packet construction in [Section 8.5.2](#852-construction-steps) Steps 2 and 3, with a modified exit routing block that signals a SURB reply.

4. **Assemble SURB**

   Assemble the SURB tuple $\mathrm{hop}_0, (α_0, β_0, γ_0), \tilde{k}$ as defined in [Section 8.7.1](#871-surb-component-sizes). Here $\mathrm{hop}_0$ is the address of the first hop on the return path. Embed the SURB in the message payload.

   The initiating node MUST store the tuple $(\tilde{k}, s_0, \ldots, s_{L-1})$ in a local table indexed by $\mathrm{id}$, for reply recovery defined in [Section 8.7.5](#875-reply-recovery).

#### 8.7.3 Using a SURB

When the Exit Layer receives any SURBs as part of the handoff defined in [Section 8.6.4](#864-exit-processing) Step 4, it MUST retain them for routing the destination's responses back to the sender.

Note: Each retained SURB consists of the hop address of the first node in the return path, a pre-computed Sphinx header, and a reply key, as defined in [Section 8.7.1](#871-surb-component-sizes).

Once the destination responds with a reply message, the Exit Layer MUST perform the following steps to use a SURB $(\mathrm{hop}_0, (α, β, γ), \tilde{k})$:

1. **Prepare Reply Message**

   Pad the reply message to $3968$ bytes using a deterministic padding scheme, consistent with [Section 8.5.2](#852-construction-steps) Step 1. Let the resulting message be $m$.

2. **Encrypt Reply Payload**

   Derive the AES key, IV, and compute the encrypted payload $δ$ following the same procedure in [Section 8.5.2](#852-construction-steps) Step 3.d for $i = L-1$, substituting $\tilde{k}$ for $s_{L-1}$.

   Note: Unlike the forward path ([Section 8.5.2](#852-construction-steps) Step 3.d), the reply payload is encrypted only once&mdash;using $\tilde{k}$ alone. Each mix node on the return path will apply one additional layer during Sphinx processing ([Section 8.6.1](#861-shared-preprocessing) Step 5), resulting in $L + 1$ layers total that the initiating node must remove during reply recovery (see [Section 8.7.5](#875-reply-recovery)).

3. **Assemble and Transmit Reply Packet**

   Assemble the Sphinx packet using the SURB header $(α, β, γ)$ and encrypted payload $δ$ from step 2, following the packet format defined in [Section 8.5.2](#852-construction-steps) Step 3.e. Serialize and transmit packet to $\mathrm{hop}_0$ (retrieved from the SURB) via a libp2p stream negotiated under the `"/mix/1.0.0"` protocol identifier.

#### 8.7.4 SURB Reply Processing

During Sphinx packet handling, once a node determines its role as an exit following the steps in [Section 8.6.2](#862-node-role-determination) and the message type as SURB reply from [Section 8.6.4](#864-exit-processing), it MUST perform the following steps to interpret the routing block $B$ and decrypted payload $δ'$ obtained in [Section 8.6.1](#861-shared-preprocessing):

1. **Extract SURB Identifier**

   Extract the SURB identifier $\mathrm{id}$ from $B$, at the position defined in [Section 8.7.2](#872-surb-creation) Step 3:

   $`
   \begin{array}{l}
   \mathrm{id} = B_{[tκ\ldots tκ+κ-1]}
   \end{array}
   `$

2. **Handoff to Exit Layer**

   Hand off the decrypted payload $δ'$ and the extracted SURB identifier $\mathrm{id}$ to the local Exit Layer for reply recovery, as defined in [Section 8.7.5](#875-reply-recovery).

#### 8.7.5 Reply Recovery

When the Exit Layer receives decrypted payload $δ'$ and the SURB identifier $\mathrm{id}$, as part of the handoff defined in [Section 8.7.4](#874-surb-reply-processing) Step 2, it MUST perform the following steps to recover the reply message:

1. **Retrieve Decryption Keys**

   Retrieve the decryption keys tuple $(\tilde{k}, s_0, \ldots, s_{L-1})$ indexed by $\mathrm{id}$ stored as defined in [Section 8.7.2](#872-surb-creation) Step 4.
   
   If no tuple is found, discard the reply and terminate processing.

2. **Recover Padded Reply Message**

   The encrypted payload $δ'$ contains the padded reply message $m$ defined in [Section 8.7.3](#873-using-a-surb) Step 1, prepended with a $κ$-byte string of zeros.
   It is encrypted in $L + 1$ layers&mdash;first using the reply key $\tilde{k}$, then with each hop on the return path adding exactly one layer using the per-hop session key $s_0, \ldots, s_{L-1}$.
   To recover the padded reply message, perform the following steps for each layer $i = 0$ to $L$, recursively:

   - Derive per-hop AES key and IV:

     - If $i = 0$ (_i.e.,_ first layer):

       $`
       \begin{array}{l}
       δ_{\mathrm{aes\_key}_i} = \mathrm{KDF}(\text{"δ\_aes\_key"} \mid \tilde{k})\\
       δ_{\mathrm{iv}_i} =
       \mathrm{KDF}(\text{"δ\_iv"} \mid \tilde{k})
       \end{array}
       `$

     - If $i = 1$ to $L$ (_i.e.,_ all other layers):

       $`
       \begin{array}{l}
       δ_{\mathrm{aes\_key}_i} = \mathrm{KDF}(\text{"δ\_aes\_key"} \mid s_{i-1})\\
       δ_{\mathrm{iv}_i} =
       \mathrm{KDF}(\text{"δ\_iv"} \mid s_{i-1})
       \end{array}
       `$

   - Using the derived keys, decrypt $δ'$:

     - If $i = 0$ (_i.e.,_ first layer):

       $`
       \begin{array}{l}
       δ_i = \mathrm{AES\text{-}CTR}\bigl(δ_{\mathrm{aes\_key}_i},
       δ_{\mathrm{iv}_i}, δ'
       \bigr)
       \end{array}
       `$

     - If $i = 1$ to $L$ (_i.e.,_ all other layers):

       $`
       \begin{array}{l}
       δ_i = \mathrm{AES\text{-}CTR}\bigl(δ_{\mathrm{aes\_key}_i},
       δ_{\mathrm{iv}_i}, δ_{i-1} \bigr)
       \end{array}
       `$

   - Verify the decrypted payload $δ_{L}$:

     $`
     \begin{array}{l}
     δ_L{}_{[0\ldots{κ} - 1]} \stackrel{?}{=} 0_{κ}
     \end{array}
     `$

     If the check fails, discard $δ_{L}$ and terminate processing.

3. **Recover Reply Message**

   - Extract rest of the bytes of $δ_{L}$ as the padded reply message $m$:

     $`
     \begin{array}{l}
     m = δ_L{}_{[κ\ldots]}
     \end{array}
     `$

   - Unpad $m$ using the deterministic padding scheme defined during construction in [Section 8.7.3](#873-using-a-surb) Step 1.
  
   - Erase all temporary values and the stored decryption keys $(\tilde{k}, s_0, \ldots, s_{L-1})$ from memory.

## 9. Security Considerations

This section describes the security guarantees and limitations of the Mix Protocol.
It begins by outlining the anonymity properties provided by the core protocol when routing messages through the mix network.
It then discusses the trust assumptions required at the edges of the network, particularly at the final hop.
Finally, it presents an alternative trust model for destinations that support Mix Protocol directly, followed by a summary of broader limitations and areas that may be addressed in future iterations.

### 9.1 Security Guarantees of the Core Mix Protocol

The core Mix Protocol&mdash;comprising anonymous routing through a sequence of mix nodes using Sphinx packets&mdash;provides the following security guarantees:

- **Sender anonymity**: Each message is wrapped in layered encryption and routed independently, making it unlinkable to the sender even if multiple mix nodes are colluding.
- **Metadata protection**: All messages are fixed in size and indistinguishable on the wire. Sphinx packets reveal only the immediate next hop and delay to each mix node. No intermediate node learns its position in the path or the total path length.
- **Traffic analysis resistance**: Continuous-time mixing with randomized per-hop delays reduces the risk of timing correlation and input-output linkage.
- **Per-hop confidentiality and integrity**: Each hop decrypts only its assigned layer of the Sphinx packet and verifies header integrity via a per-hop MAC.
- **No long-term state**: All routing is stateless. Mix nodes do not maintain per-message metadata, reducing the surface for correlation attacks.

These guarantees hold only within the boundaries of the Mix Protocol.
Additional trust assumptions are introduced at the edges, particularly at the final hop, where the decrypted message is handed off to the Mix Exit Layer for delivery to the destination outside the mixnet.
The next subsection discusses these trust assumptions in detail.

### 9.2 Exit Node Trust Model

The Mix Protocol ensures strong sender anonymity and metadata protection between the Mix Entry and Exit layers.
However, once a Sphinx packet is decrypted at the final hop, additional trust assumptions are introduced.
The node processing the final layer of encryption is trusted to forward the correct message to the destination and return any reply using the provided reply key.
This section outlines the resulting trust boundaries.

#### 9.2.1 Message Delivery and Origin Trust

At the final hop, the decrypted Sphinx packet reveals the plaintext message and destination address.
The exit node is then trusted to deliver this message to the destination application, and&mdash;if a reply is expected&mdash;to return the response using the embedded reply key.

In this model, the exit node becomes a privileged middleman.
It has full visibility into the decrypted payload.
Specifically, the exit node could tamper with either direction of communication without detection:

- It may alter or drop the forwarded message.
- It may fabricate a reply instead of forwarding the actual response from the destination.

This limitation is consistent with the broader mixnet trust model.
While intermediate nodes are constrained by layered encryption, edge nodes&mdash;specifically the initiating and the exit nodes in the path&mdash;are inherently more privileged and operate outside the cryptographic protections of the mixnet.

In systems like Tor, such exit-level tampering is mitigated by long-lived circuits that allow endpoints to negotiate shared session keys (_e.g.,_ via TLS).
A malicious exit cannot forge a valid forward message or response without access to these session secrets.

The Mix Protocol, by contrast, is stateless and message-based.
Each message is routed independently, with no persistent circuit or session context.
As a result, endpoints cannot correlate messages, establish session keys, or validate message origin.
That is, the exit remains a necessary point of trust for message delivery and response handling.

The next subsection describes a related limitation:
the exit's ability to pose as a legitimate client to the destination's origin protocol, and how that can be abused to bypass application-layer expectations.

#### 9.2.2 Origin Protocol Trust and Client Role Abuse

In addition to the message delivery and origin trust assumption, the exit node also initiates a client-side connection to the origin protocol instance at the destination.
From the destination's perspective, this appears indistinguishable from a conventional peer connection, and the exit is accepted as a legitimate peer.

As a result, any protocol-level safeguards and integrity checks are applied to the exit node as well.
However, since the exit node is not a verifiable peer and may open fresh connections at will, such protections are limited in their effectiveness.
A malicious exit may repeatedly initiate new connections, send well-formed fabricated messages and circumvent any peer scoring mechanisms by reconnecting.
These messages are indistinguishable from legitimate peer messages from the destination's point of view.

This class of attack is distinct from basic message tampering.
Even if the message content is well-formed and semantically valid, the exit's role as an unaccountable client allows it to bypass application-level assumptions about peer behavior.
This results in protocol misuse, targeted disruption, or spoofed message injection that the destination cannot attribute.

Despite these limitations, this model is compatible with legacy protocols and destinations that do not support the Mix Protocol.
It allows applications to preserve sender anonymity without requiring any participation from the recipient.

However, in scenarios that demand stronger end-to-end guarantees&mdash;such as verifiable message delivery, origin authentication, or control over client access&mdash;it may be beneficial for the destination itself to operate a Mix instance.
This alternative model is described in the next subsection.

### 9.3 Destination as Final Hop

In some deployments, it may be desirable for the destination node to participate in the Mix Protocol directly.
In this model, the destination operates its own Mix instance and is selected as the final node in the mix path.
The decrypted message is then delivered by the Mix Exit Layer directly to the destination's local origin protocol instance, without relying on a separate exit node.

From a security standpoint, this model provides end-to-end integrity guarantees.
It removes the trust assumption on an external exit.
The message is decrypted and delivered entirely within the destination node, eliminating the risk of tampering during the final delivery step.
The response, if used, is also encrypted and returned by the destination itself, avoiding reliance on a third-party node to apply the reply key.

This model also avoids client role abuse.
Since the Mix Exit Layer delivers the message locally, the destination need not accept arbitrary inbound connections from external clients.
This removes the risk of an adversarial exit posing as a peer and injecting protocol-compliant but unauthorized messages.

This approach does require the destination to support the Mix Protocol.
However, this requirement can be minimized by supporting a lightweight mode in which the destination only sends and receives messages via Mix, without participating in message routing for other nodes.
This is similar to the model adopted by Waku, where edge nodes are not required to relay traffic but still interact with the network.
In practice, this tradeoff is often acceptable.

The core Mix Protocol does not mandate destination participation.
However, implementations MAY support this model as an optional mode for use in deployments that require stronger end-to-end security guarantees.
The discovery mechanism MAY include a flag to advertise support for routing versus receive-only participation.
Additional details on discovery configurations are out of scope for this specification.

This trust model is not required for interoperability, but is recommended when assessing deployment-specific threat models, especially in protocols that require message integrity or authenticated replies.

### 9.4 Known Protocol Limitations

The Mix Protocol provides strong sender anonymity and metadata protection guarantees within the mix network.
However, it does not address all classes of network-level disruption or application-layer abuse.
This section outlines known limitations that deployments MUST consider when evaluating system resilience and reliability.

#### 9.4.1 Undetectable Node Misbehavior

The Mix Protocol in its current version does not include mechanisms to detect or attribute misbehavior by mix nodes.
Since Sphinx packets are unlinkable and routing is stateless, malicious or faulty nodes may delay, drop, or selectively forward packets without detection.

This behavior is indistinguishable from benign network failure.
There is no native support for feedback, acknowledgment, or proof-of-relay.
As a result, unreliable nodes cannot be penalized or excluded based on observed reliability.

Future versions may explore accountability mechanisms.
For now, deployments MAY improve robustness by sending each packet along multiple paths as defined in [Section X.X], but MUST treat message loss as a possibility.

#### 9.4.2 No Built-in Retry or Acknowledgment

The Mix Protocol does not support retransmission, delivery acknowledgments, or automated fallback logic.
Each message is sent once and routed independently through the mixnet.
If a message is lost or a node becomes unavailable, recovery is the responsibility of the top-level application.

Single-Use Reply Blocks (SURBs) (defined in [Section 8.7](#87-single-use-reply-blocks)) enable destinations to send responses back to the sender via a fresh mix path.
However, SURBs are optional, and their usage for acknowledgments or retries must be coordinated by the application.

Applications using the Mix Protocol MUST treat delivery as probabilistic.
To improve reliability, the sender MAY:

- Use parallel transmission across `D` disjoint paths.
- Estimate end-to-end delay bounds based on chosen per-hop delays (defined in [Section 6.2](#62-delay-strategy)), and retry using different paths if a response is not received within the expected window.

These strategies MUST be implemented at the origin protocol layer or through Mix integration logic and are not enforced by the Mix Protocol itself.

#### 9.4.3 No Sybil Resistance

The Mix Protocol does not include any built-in defenses against Sybil attacks.
All nodes that support the protocol and are discoverable via peer discovery are equally eligible for path selection.
An adversary that operates a large number of Sybil nodes may be selected into mix paths more often than expected, increasing the likelihood of partial or full path compromise.

In the worst case, if an adversary controls a significant fraction of nodes (_e.g.,_ one-third of the network), the probability that a given path includes only adversarial nodes increases sharply.
This raises the risk of deanonymization through end-to-end traffic correlation or timing analysis.

Deployments concerned with Sybil resistance MAY implement passive defenses such as minimum path length constraints.
More advanced mitigations such as stake-based participation or resource proofs typically require some form of trusted setup or blockchain-based coordination.

Such defenses are not built into the current version of the Mix Protocol, but are critical to ensuring anonymity at scale.
Deployments that enable DoS protection (see [Section 6.6](#66-dos-protection)) may gain Sybil resistance as a side effect, depending on the approach chosen.

#### 9.4.4 Vulnerability to Denial-of-Service Attacks

The Mix Protocol does not provide built-in defenses against denial-of-service (DoS) attacks targeting mix nodes.
A malicious mix node may generate a high volume of valid Sphinx packets to exhaust computational, memory, or bandwidth resources along random paths through the network.

This risk stems from the protocol's stateless and sender-anonymous design.
Mix nodes process each packet independently and cannot distinguish honest users from attackers.
There is no mechanism to attribute packets, limit per-sender usage, or apply network-wide fairness constraints.

While the Mix Protocol includes safeguards such as layered encryption, per-hop integrity checks, and fixed-size headers, these primarily defend against tagging attacks and structurally invalid or malformed traffic.
The Sphinx packet format also enforces a maximum path length $(L \leq r)$, which prevents infinite loops or excessively long paths being embedded.
However, these protections do not prevent adversaries from injecting large volumes of short, well-formed messages to exhaust mix node resources.

DoS protection&mdash;such as admission control, rate-limiting, or resource-bound access&mdash;can be plugged in as explained in [Section 6.6](#66-dos-protection).
Any such mechanism MUST preserve sender unlinkability and SHOULD be evaluated carefully to avoid introducing correlation risks.
