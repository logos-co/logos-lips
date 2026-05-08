# 10/WAKU2

| Field | Value |
| --- | --- |
| Name | Waku v2 |
| Slug | 10 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Sanaz Taheri <sanaz@status.im>, Hanno Cornelius <hanno@status.im>, Reeshav Khan <reeshav@status.im>, Daniel Kaiser <danielkaiser@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/core/10/waku2.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/10/waku2.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/10/waku2.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/10/waku2.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/10/waku2.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/10/waku2.md) — ci: add mdBook configuration (#233)
- **2025-04-15** — [`34aa3f3`](https://github.com/logos-co/logos-lips/blob/34aa3f3647cd5f0ae6a9af7fad47c3c8ee32c866/waku/standards/core/10/waku2.md) — Fix links 10/WAKU2 (#153)
- **2025-04-09** — [`cafa04f`](https://github.com/logos-co/logos-lips/blob/cafa04fb93c461034e1754cf750409a6236cf6ee/waku/standards/core/10/waku2.md) — 10/WAKU2: Update (#125)
- **2024-11-20** — [`ff87c84`](https://github.com/logos-co/logos-lips/blob/ff87c84dc71d4f933bab188993914069fea12baa/waku/standards/core/10/waku2.md) — Update Waku Links (#104)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/10/waku2.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/core/10/waku2.md) — Broken Links + Change Editors (#26)
- **2024-02-01** — [`8e14d58`](https://github.com/logos-co/logos-lips/blob/8e14d584bf90f59aab790c9b8e62dd6adf5da100/waku/standards/core/10/waku2.md) — Update waku2.md
- **2024-02-01** — [`6cf68fd`](https://github.com/logos-co/logos-lips/blob/6cf68fd03e35f5889a827d0e7d053879e2162a4e/waku/standards/core/10/waku2.md) — Update waku2.md
- **2024-02-01** — [`6734b16`](https://github.com/logos-co/logos-lips/blob/6734b1690817d1647feeccc07f28c13fc1c3b789/waku/standards/core/10/waku2.md) — Update waku2.md
- **2024-01-31** — [`356649a`](https://github.com/logos-co/logos-lips/blob/356649a5b690dd56f7de42961eeeeb676dd71b88/waku/standards/core/10/waku2.md) — Update and rename WAKU2.md to waku2.md
- **2024-01-27** — [`550238c`](https://github.com/logos-co/logos-lips/blob/550238ca71eb03506d400db579d8fdbab1acd6ad/waku/standards/core/10/WAKU2.md) — Rename README.md to WAKU2.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/10-WAKU2/README.md) — remove rfs folder
- **2024-01-26** — [`d6651b7`](https://github.com/logos-co/logos-lips/blob/d6651b7f2a72974685871b3c25c7514dd5a4e679/waku/rfcs/standards/core/10-WAKU2/README.md) — Update README.md
- **2024-01-25** — [`6e98666`](https://github.com/logos-co/logos-lips/blob/6e98666f71f01fd5fa348ba71d8d55a265891a80/waku/rfcs/standards/core/10-WAKU2/README.md) — Rename README.md to README.md
- **2024-01-25** — [`9b740d8`](https://github.com/logos-co/logos-lips/blob/9b740d887522349f8d9c80c580d3777d7f6f63af/waku/specs/standards/core/10-WAKU2/README.md) — Rename waku/10/README.md to waku/specs/standards/core/10-WAKU2/README.md
- **2024-01-24** — [`330c35b`](https://github.com/logos-co/logos-lips/blob/330c35b56eecf3876c8246fbddb9e40b5211b566/waku/10/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

Waku is a family of modular peer-to-peer protocols for secure communication.
The protocols are designed to be secure, privacy-preserving, censorship-resistant
and being able to run in resource-restricted environments.
At a high level, it implements Pub/Sub over [libp2p](https://github.com/libp2p/specs)
and adds a set of capabilities to it.
These capabilities are things such as:
(i) retrieving historical messages for mostly-offline devices
(ii) adaptive nodes, allowing for heterogeneous nodes to contribute to the network
(iii) preserving bandwidth usage for resource-restriced devices

This makes Waku ideal for running a p2p protocol on mobile devices and
other similar restricted environments.

Historically, it has its roots in [6/WAKU1](/messaging/standards/legacy/6/waku1.md),
which stems from [Whisper](https://eips.ethereum.org/EIPS/eip-627),
originally part of the Ethereum stack.
However, Waku acts more as a thin wrapper for Pub/Sub and has a different API.
It is implemented in an iterative manner where initial focus
is on porting essential functionality to libp2p.
See [rough road map (2020)](https://vac.dev/waku-v2-plan) for more historical context.

## Motivation and Goals

Waku, as a family of protocols, is designed to have a set of properties
that are useful for many applications:

1.**Useful for generalized messaging.**

Many applications require some form of messaging protocol to communicate
between different subsystems or different nodes.
This messaging can be human-to-human, machine-to-machine or a mix.
Waku is designed to work for all these scenarios.

2.**Peer-to-peer.**

Applications sometimes have requirements that make them suitable
for peer-to-peer solutions:

- Censorship-resistant with no single point of failure
- Adaptive and scalable network
- Shared infrastructure

3.**Runs anywhere.**

Applications often run in restricted environments,
where resources or the environment is restricted in some fashion.
For example:

- Limited bandwidth, CPU, memory, disk, battery, etc.
- Not being publicly connectable
- Only being intermittently connected; mostly-offline

4.**Privacy-preserving.**

 Applications often have a desire for some privacy guarantees, such as:

- Pseudonymity and not being tied to any personally identifiable information (PII)
- Metadata protection in transit
- Various forms of unlinkability, etc.

5.**Modular design.**

Applications often have different trade-offs when it comes to what properties they
and their users value.
Waku is designed in a modular fashion where an application protocol or
node can choose what protocols they run.
We call this concept *adaptive nodes*.

For example:

- Resource usage vs metadata protection
- Providing useful services to the network vs mostly using it
- Stronger guarantees for spam protection vs economic registration cost

For more on the concept of adaptive nodes and what this means in practice,
please see the [30/ADAPTIVE-NODES](/messaging/informational/30/adaptive-nodes.md) spec.

## Specification

The keywords “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Network Interaction Domains

While Waku is best thought of as a single cohesive thing,
there are three network interaction domains:

(a) gossip domain
(b) discovery domain
(c) request/response domain

#### Protocols and Identifiers

Since Waku is built on top of libp2p, many protocols have a libp2p protocol identifier.
The current main [protocol identifiers](https://docs.libp2p.io/concepts/protocols/)
are:

1. `/vac/waku/relay/2.0.0`
2. `/vac/waku/store-query/3.0.0`
3. `/vac/waku/filter/2.0.0-beta1`
4. `/vac/waku/lightpush/2.0.0-beta1`

This is in addition to protocols that specify messages, payloads, and
recommended usages.
Since these aren't negotiated libp2p protocols,
they are referred to by their RFC ID.
For example:

- [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) and
[26/WAKU-PAYLOAD](/messaging/standards/application/26/payload.md) for message payloads
- [23/WAKU2-TOPICS](/messaging/informational/23/topics.md) and
[27/WAKU2-PEERS](/messaging/informational/27/peers.md) for recommendations around usage

There are also more experimental libp2p protocols such as:

1. `/vac/waku/waku-rln-relay/2.0.0-alpha1`
2. `/vac/waku/peer-exchange/2.0.0-alpha1`

The semantics of these protocols are referred to by RFC ID [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md) and [34/WAKU2-PEER-EXCHANGE](/messaging/standards/core/34/peer-exchange.md).

#### Use of libp2p and Protobuf

Unless otherwise specified,
all protocols are implemented over libp2p and use Protobuf by default.
Since messages are exchanged over a [bi-directional binary stream](https://docs.libp2p.io/concepts/protocols/),
as a convention,
libp2p protocols prefix binary message payloads with
the length of the message in bytes.
This length integer is encoded as a [protobuf varint](https://developers.google.com/protocol-buffers/docs/encoding#varints).

#### Gossip Domain

Waku is using gossiping to disseminate messages throughout the network.

**Protocol identifier**: `/vac/waku/relay/2.0.0`

See [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md) specification for more details.

For an experimental privacy-preserving economic spam protection mechanism,
see [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md).

See [23/WAKU2-TOPICS](/messaging/informational/23/topics.md)
for more information about the recommended topic usage.

#### Direct use of libp2p protocols

In addition to `/vac/waku/*` protocols,
Waku MAY directly use the following libp2p protocols:

- [libp2p ping protocol](https://docs.libp2p.io/concepts/protocols/#ping)
with protocol id

```text
/ipfs/ping/1.0.0
```

for liveness checks between peers, or
to keep peer-to-peer connections alive.

- [libp2p identity and identity/push](https://docs.libp2p.io/concepts/protocols/#identify)
with protocol IDs

```text
/ipfs/id/1.0.0
```

and

```text
/ipfs/id/push/1.0.0
```

respectively, as basic means for capability discovery.
These protocols are anyway used by the libp2p connection
establishment layer Waku is built on.
We plan to introduce a new IFT-TS capability discovery protocol
with better anonymity properties and more functionality.

#### Transports

Waku is built in top of libp2p, and like libp2p it strives to be transport agnostic.
We define a set of recommended transports in order to achieve a baseline of
interoperability between clients.
This section describes these recommended transports.

Waku client implementations SHOULD support the TCP transport.
Where TCP is supported it MUST be enabled for both dialing and listening,
even if other transports are available.

Waku nodes running in environments that do not allow the use of TCP directly,
MAY use other transports.

A Waku node SHOULD support secure websockets for bidirectional communication streams,
for example in a web browser context.

A node MAY support unsecure websockets if required by the application or
running environment.

### Discovery Domain

#### Discovery Methods

Waku can retrieve a list of nodes to connect to using DNS-based discovery
as per [EIP-1459](https://eips.ethereum.org/EIPS/eip-1459).
While this is a useful way of bootstrapping connection to a set of peers,
it MAY be used in conjunction with an [ambient peer discovery](https://docs.libp2p.io/concepts/publish-subscribe/#discovery)
procedure to find other nodes to connect to,
such as [Node Discovery v5](https://github.com/ethereum/devp2p/blob/8fd5f7e1c1ec496a9d8dc1640a8548b8a8b5986b/discv5/discv5.md).
It is possible to bypass the discovery domain by specifying static nodes.

#### Use of ENR

[WAKU2-ENR](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/enr.md)
describes the usage of [EIP-778 ENR (Ethereum Node Records)](https://eips.ethereum.org/EIPS/eip-778)
for Waku discovery purposes.
It introduces two new ENR fields, `multiaddrs` and
`waku2`, that a Waku node MAY use for discovery purposes.
These fields MUST be used under certain conditions, as set out in the specification.
Both EIP-1459 DNS-based discovery and Node Discovery v5 operate on ENR,
and it's reasonable to expect even wider utility for ENR in Waku networks in the future.

### Request/Response Domain

In addition to the Gossip domain,
Waku provides a set of request/response protocols.
They are primarily used in order to get Waku to run in resource restricted environments,
such as low bandwidth or being mostly offline.

#### Historical Message Support

**Protocol identifier***: `/vac/waku/store-query/3.0.0`

This is used to fetch historical messages for mostly offline devices.
See [13/WAKU2-STORE spec](/messaging/standards/core/13/store.md) specification for more details.

There is also an experimental fault-tolerant addition to the store protocol
that relaxes the high availability requirement.
See [21/WAKU2-FAULT-TOLERANT-STORE](/messaging/deprecated/fault-tolerant-store.md)

#### Content Filtering

**Protocol identifier***: `/vac/waku/filter/2.0.0-beta1`

This is used to preserve more bandwidth when fetching a subset of messages.
See [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md) specification for more details.

#### LightPush

**Protocol identifier***: `/vac/waku/lightpush/2.0.0-beta1`

This is used for nodes with short connection windows and
limited bandwidth to publish messages into the Waku network.
See [19/WAKU2-LIGHTPUSH](/messaging/standards/core/19/lightpush.md) specification for more details.

#### Other Protocols

The above is a non-exhaustive list,
and due to the modular design of Waku,
there may be other protocols here that provide a useful service to the Waku network.

### Overview of Protocol Interaction

See the sequence diagram below for an overview of how different protocols interact.

![Overview of how protocols interact in Waku.](images/overview.png)

0. We have six nodes, A-F.
The protocols initially mounted are indicated as such.
The PubSub topics `pubtopic1` and
`pubtopic2` is used for routing and
indicates that it is subscribed to messages on that topic for relay,
see [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md) for details.
Ditto for [13/WAKU2-STORE](/messaging/standards/core/13/store.md)
where it indicates that these messages are persisted on that node.

1. Node A creates a WakuMessage `msg1` with a ContentTopic `contentTopic1`.
See [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) for more details.
If WakuMessage version is set to 1,
we use the [6/WAKU1](/messaging/standards/legacy/6/waku1.md) compatible `data` field with encryption.
See [7/WAKU-DATA](/messaging/standards/legacy/7/data.md) for more details.

2. Node F requests to get messages filtered by PubSub topic `pubtopic1` and
ContentTopic `contentTopic1`.
Node D subscribes F to this filter and
will in the future forward messages that match that filter.
See [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md) for more details.

3. Node A publishes `msg1` on `pubtopic1` and
subscribes to that relay topic.
It then gets relayed further from B to D, but
not C since it doesn't subscribe to that topic.
See [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md).

4. Node D saves `msg1` for possible later retrieval by other nodes.
See [13/WAKU2-STORE](/messaging/standards/core/13/store.md).

5. Node D also pushes `msg1` to F,
as it has previously subscribed F to this filter.
See [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md).

6. At a later time, Node E comes online.
It then requests messages matching `pubtopic1` and
`contentTopic1` from Node D.
Node D responds with messages meeting this (and possibly other) criteria.
See [13/WAKU2-STORE](/messaging/standards/core/13/store.md).

## Appendix A: Upgradability and Compatibility

### Compatibility with Waku Legacy

[6/WAKU1](/messaging/standards/legacy/6/waku1.md) and Waku are different protocols all together.
They use a different transport protocol underneath;
[6/WAKU1](/messaging/standards/legacy/6/waku1.md) is devp2p RLPx based while Waku uses libp2p.
The protocols themselves also differ as does their data format.
Compatibility can be achieved only by using a bridge
that not only talks both devp2p RLPx and libp2p,
but that also transfers (partially) the content of a packet from one version
to the other.

See [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md) for details on a bidirectional bridge mode.

## Appendix B: Security

Each protocol layer of Waku provides a distinct service and
is associated with a separate set of security features and concerns.
Therefore, the overall security of Waku
depends on how the different layers are utilized.
In this section,
we overview the security properties of Waku protocols
against a static adversarial model which is described below.
Note that a more detailed security analysis of each Waku protocol
is supplied in its respective specification as well.

### Primary Adversarial Model

In the primary adversarial model,
we consider adversary as a passive entity that attempts to collect information
from others to conduct an attack,
but it does so without violating protocol definitions and instructions.

The following are **not** considered as part of the adversarial model:

- An adversary with a global view of all the peers and their connections.
- An adversary that can eavesdrop on communication links
between arbitrary pairs of peers
(unless the adversary is one end of the communication).
Specifically, the communication channels are assumed to be secure.

### Security Features

#### Pseudonymity

Waku by default guarantees pseudonymity for all of the protocol layers
since parties do not have to disclose their true identity
and instead they utilize libp2p `PeerID` as their identifiers.
While pseudonymity is an appealing security feature,
it does not guarantee full anonymity since the actions taken under the same pseudonym
i.e., `PeerID` can be linked together and
potentially result in the re-identification of the true actor.
  
#### Anonymity / Unlinkability

At a high level,
anonymity is the inability of an adversary in linking an actor
to its data/performed action (the actor and action are context-dependent).
To be precise about linkability,
we use the term Personally Identifiable Information (PII)
to refer to any piece of data that could potentially
be used to uniquely identify a party.
For example, the signature verification key, and
the hash of one's static IP address are unique for each user and
hence count as PII.
Notice that users' actions can be traced through their PIIs
(e.g., signatures) and hence result in their re-identification risk.
As such, we seek anonymity by avoiding linkability between actions and
the actors / actors' PII. Concerning anonymity, Waku provides the following features:

**Publisher-Message Unlinkability**:
This feature signifies the unlinkability of a publisher
to its published messages in the 11/WAKU2-RELAY protocol.
The [Publisher-Message Unlinkability](/messaging/standards/core/11/relay.md#security-analysis)
is enforced through the `StrictNoSign` policy due to which the data fields
of pubsub messages that count as PII for the publisher must be left unspecified.

**Subscriber-Topic Unlinkability**:
This feature stands for the unlinkability of the subscriber
to its subscribed topics in the 11/WAKU2-RELAY protocol.
The [Subscriber-Topic Unlinkability](/messaging/standards/core/11/relay.md#security-analysis)
is achieved through the utilization of a single PubSub topic.
As such, subscribers are not re-identifiable from their subscribed topic IDs
as the entire network is linked to the same topic ID.
This level of unlinkability / anonymity is known as [k-anonymity](https://www.privitar.com/blog/k-anonymity-an-introduction/)
where k is proportional to the system size (number of subscribers).
Note that there is no hard limit on the number of the pubsub topics, however,
the use of one topic is recommended for the sake of anonymity.

#### Spam protection

This property indicates that no adversary can flood the system
(i.e., publishing a large number of messages in a short amount of time),
either accidentally or deliberately, with any kind of message
i.e. even if the message content is valid or useful.
Spam protection is partly provided in `11/WAKU2-RELAY`
through the [scoring mechanism](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#spam-protection-measures)
provided for by GossipSub v1.1.
At a high level,
peers utilize a scoring function to locally score the behavior
of their connections and remove peers with a low score.
  
#### Data confidentiality, Integrity, and Authenticity

Confidentiality can be addressed through data encryption whereas integrity and
authenticity are achievable through digital signatures.
These features are provided for in [14/WAKU2-MESSAGE (version 1)](/messaging/standards/core/14/message.md#version-1)`
through payload encryption as well as encrypted signatures.

### Security Considerations

Lack of anonymity/unlinkability in the protocols involving direct connections
including `13/WAKU2-STORE` and `12/WAKU2-FILTER` protocols:

The anonymity/unlinkability is not guaranteed in the protocols like `13/WAKU2-STORE`
and `12/WAKU2-FILTER` where peers need to have direct connections
to benefit from the designated service.
This is because during the direct connections peers utilize `PeerID`
to identify each other,
therefore the service obtained in the protocol is linkable
to the beneficiary's `PeerID` (which counts as PII).
For `13/WAKU2-STORE`,
the queried node would be able to link the querying node's `PeerID`
to its queried topics.
Likewise, in the `12/WAKU2-FILTER`,
a full node can link the light node's `PeerID`s to its content filter.

<!-- TODO: to inspect the nim-libp2p codebase and
figure out the exact use of PeerIDs in direct communication,
it might be the case that the requester does not have to disclose its PeerID-->

<!--TODO: might be good to add a figure visualizing the Waku protocol stack and
the security features of each layer-->

## Appendix C: Implementation Notes

### Implementation Matrix

There are multiple implementations of Waku and its protocols:

- [nim-waku (Nim)](https://github.com/status-im/nim-waku/)
- [go-waku (Go)](https://github.com/status-im/go-waku/)
- [js-waku (NodeJS and Browser)](https://github.com/status-im/js-waku/)

Below you can find an overview of the specifications that they implement
as they relate to Waku.
This includes Waku legacy specifications, as they are used for bridging between the two networks.

| Spec | nim-waku (Nim) | go-waku (Go) | js-waku (Node JS) | js-waku (Browser JS) |
| ---- | -------------- | ------------ | ----------------- | -------------------- |
|[6/WAKU1](/messaging/standards/legacy/6/waku1.md)|✔||||
|[7/WAKU-DATA](/messaging/standards/legacy/7/data.md)|✔|✔|||
|[8/WAKU-MAIL](/messaging/standards/legacy/8/mail.md)|✔||||
|[9/WAKU-RPC](/messaging/standards/legacy/9/rpc.md)|✔||||
|[10/WAKU2](/messaging/standards/core/10/waku2.md)|✔|🚧|🚧|✔|
|[11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)|✔|✔|✔|✔|
|[12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)|✔|✔|||
|[13/WAKU2-STORE](/messaging/standards/core/13/store.md)|✔|✔|✔\*|✔\*|
|[14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md))|✔|✔|✔|✔|
|[15/WAKU2-BRIDGE](/messaging/standards/core/15/bridge.md)|✔||||
|[16/WAKU2-RPC](/messaging/deprecated/16/rpc.md)|✔||||
|[17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md)|🚧||||
|[18/WAKU2-SWAP](/messaging/deprecated/18/swap.md)|🚧||||
|[19/WAKU2-LIGHTPUSH](/messaging/standards/core/19/lightpush.md)|✔|✔|✔\**|✔\**|
|[21/WAKU2-FAULT-TOLERANT-STORE](/messaging/deprecated/fault-tolerant-store.md)|✔|✔|||

*js-waku implements [13/WAKU2-STORE](/messaging/standards/core/13/store.md) as a querying node only.
**js-waku only implements [19/WAKU2-LIGHTPUSH](/messaging/standards/core/19/lightpush.md) requests.

### Recommendations for Clients

To implement a minimal Waku client,
we recommend implementing the following subset in the following order:

- [10/WAKU2](/messaging/standards/core/10/waku2.md) - this specification
- [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md) - for basic operation
- [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) - version 0 (unencrypted)
- [13/WAKU2-STORE](/messaging/standards/core/13/store.md) - for historical messaging (query mode only)

To get compatibility with Waku Legacy:

- [7/WAKU-DATA](/messaging/standards/legacy/7/data.md)
- [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) - version 1 (encrypted with `7/WAKU-DATA`)

For an interoperable keep-alive mechanism:

- [libp2p ping protocol](https://docs.libp2p.io/concepts/protocols/#ping),
with periodic pings to connected peers

## Appendix D: Future work

The following features are currently experimental,
under research and initial implementations:

**Economic Spam Resistance**:

We aim to enable an incentivized spam protection technique
to enhance `11/WAKU2-RELAY` by using rate limiting nullifiers.
More details on this can be found in [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md).
In this advanced method,
peers are limited to a certain rate of messaging per epoch and
an immediate financial penalty is enforced for spammers who break this rate.

**Prevention of Denial of Service (DoS) and Node Incentivization**:
Denial of service signifies the case where an adversarial node
exhausts another node's service capacity (e.g., by making a large number of requests)
and makes it unavailable to the rest of the system.
DoS attack is to be mitigated through the accounting model as described in [18/WAKU2-SWAP](/messaging/deprecated/18/swap.md).
In a nutshell, peers have to pay for the service they obtain from each other.
In addition to incentivizing the service provider,
accounting also makes DoS attacks costly for malicious peers.
The accounting model can be used in `13/WAKU2-STORE` and
`12/WAKU2-FILTER` to protect against DoS attacks.

Additionally, this gives node operators who provide a useful service to the network
an incentive to perform that service.
See [18/WAKU2-SWAP](/messaging/deprecated/18/swap.md)
for more details on this piece of work.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [libp2p specs](https://github.com/libp2p/specs)

2. [6/WAKU1](/messaging/standards/legacy/6/waku1.md)

3. [Whisper spec (EIP627)](https://eips.ethereum.org/EIPS/eip-627)

4. [Waku v2 plan](https://vac.dev/waku-v2-plan)

5. [30/ADAPTIVE-NODES](/messaging/informational/30/adaptive-nodes.md)

6. [Protocol Identifiers](https://docs.libp2p.io/concepts/protocols/)

7. [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md)

8. [26/WAKU-PAYLOAD](/messaging/standards/application/26/payload.md)

9. [23/WAKU2-TOPICS](/messaging/informational/23/topics.md)

10. [27/WAKU2-PEERS](/messaging/informational/27/peers.md)

11. [bi-directional binary stream](https://docs.libp2p.io/concepts/protocols/)

12. [Protobuf varint encoding](https://developers.google.com/protocol-buffers/docs/encoding#varints)

13. [11/WAKU2-RELAY spec](/messaging/standards/core/11/relay.md)

14. [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md)

15. [EIP-1459](https://eips.ethereum.org/EIPS/eip-1459)

16. [Ambient peer discovery](https://docs.libp2p.io/concepts/publish-subscribe/#discovery)

17. [Node Discovery v5](https://github.com/ethereum/devp2p/blob/8fd5f7e1c1ec496a9d8dc1640a8548b8a8b5986b/discv5/discv5.md)

18. [WAKU2-ENR](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/enr.md)

19. [EIP-778 ENR (Ethereum Node Records)](https://eips.ethereum.org/EIPS/eip-778)

20. [13/WAKU2-STORE spec](/messaging/standards/core/13/store.md)

21. [21/WAKU2-FT-STORE](/messaging/deprecated/fault-tolerant-store.md)

22. [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)

23. [19/WAKU2-LIGHTPUSH](/messaging/standards/core/19/lightpush.md)

24. [7/WAKU-DATA](/messaging/standards/legacy/7/data.md)

25. [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md)

26. [k-anonymity](https://www.privitar.com/blog/k-anonymity-an-introduction/)

27. [GossipSub v1.1](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md)

28. [nim-waku (Nim)](https://github.com/status-im/nim-waku/)

29. [go-waku (Go)](https://github.com/status-im/go-waku/)

30. [js-waku (NodeJS and Browser)](https://github.com/status-im/js-waku/)

31. [8/WAKU-MAIL](/messaging/standards/legacy/8/mail.md)

32. [9/WAKU-RPC](/messaging/standards/legacy/9/rpc.md)

33. [16/WAKU2-RPC](../../../deprecated/16/rpc.md)

34. [18/WAKU2-SWAP spec](/messaging/deprecated/18/swap.md)

35. [21/WAKU2-FAULT-TOLERANT-STORE](/messaging/deprecated/fault-tolerant-store.md)
