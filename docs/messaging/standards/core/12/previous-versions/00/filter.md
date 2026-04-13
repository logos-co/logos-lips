# 12/WAKU2-FILTER

| Field | Value |
| --- | --- |
| Name | Waku v2 Filter |
| Slug | 12 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Dean Eigenmann <dean@status.im>, Oskar Thorén <oskarth@titanproxy.com>, Sanaz Taheri <sanaz@status.im>, Ebube Ud <ebube@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-21** — [`a00f16e`](https://github.com/vacp2p/rfc-index/blob/a00f16ed60dc8479361f247328ccd2d25338c5f1/docs/messaging/standards/core/12/previous-versions/00/filter.md) — chore: mdbook fixes (#265)
- **2026-01-16** — [`f01d5b9`](https://github.com/vacp2p/rfc-index/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/12/previous-versions/00/filter.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/12/previous-versions/00/filter.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/vacp2p/rfc-index/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/12/previous-versions/00/filter.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/vacp2p/rfc-index/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/12/previous-versions/00/filter.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/vacp2p/rfc-index/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/12/previous-versions/00/filter.md) — ci: add mdBook configuration (#233)
- **2025-03-25** — [`e8a3f8a`](https://github.com/vacp2p/rfc-index/blob/e8a3f8a77ddfc84894f4e1119380e90ca2dd0ab4/waku/standards/core/12/previous-versions/00/filter.md) — 12/WAKU2-FILTER: Update (#119)
- **2024-09-13** — [`3ab314d`](https://github.com/vacp2p/rfc-index/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/12/previous-versions00/filter.md) — Fix Files for Linting (#94)
- **2024-02-05** — [`d41f106`](https://github.com/vacp2p/rfc-index/blob/d41f1060d33f614947abbae5104a47a732d2c630/waku/standards/core/12/previous-versions00/filter.md) — Update filter.md
- **2024-02-05** — [`8436a31`](https://github.com/vacp2p/rfc-index/blob/8436a310d984a094990321dba4aa2bb3fa9dc96b/waku/standards/core/12/previous-versions00/filter.md) — Update and rename README.md to filter.md
- **2024-01-27** — [`eef961b`](https://github.com/vacp2p/rfc-index/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/12/previous-versions00/README.md) — remove rfs folder
- **2024-01-25** — [`420a51b`](https://github.com/vacp2p/rfc-index/blob/420a51bacc4e2e8ff87662952b9dc550f91d78fb/waku/rfcs/standards/core/12/previous-versions00/README.md) — Rename waku/rfcs/core/12/previous-versions00/README.md to waku/rfcs/standards/core/12/previous-versions00/README.md
- **2024-01-25** — [`755fea9`](https://github.com/vacp2p/rfc-index/blob/755fea937177ba73c3ee0f03af5f7af0545b7a0a/waku/rfcs/core/12/previous-versions00/README.md) — Rename waku/12/previous-versions/00/README.md to waku/rfcs/core/12/previous-versions00/README.md
- **2024-01-22** — [`420adf1`](https://github.com/vacp2p/rfc-index/blob/420adf1bd6fe714366bb11667400b923772835da/waku/12/previous-versions/00/README.md) — Vac RFC index initial structure

<!-- timeline:end -->

`WakuFilter` is a protocol that enables subscribing to messages that a peer receives.
This is a more lightweight version of `WakuRelay`
specifically designed for bandwidth restricted devices.
This is due to the fact that light nodes subscribe to full-nodes and
only receive the messages they desire.

## Content filtering

**Protocol identifier***: `/vac/waku/filter/2.0.0-beta1`

Content filtering is a way to do [message-based
filtering](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern#Message_filtering).
Currently the only content filter being applied is on `contentTopic`. This
corresponds to topics in Waku v1.

## Rationale

Unlike the `store` protocol for historical messages, this protocol allows for
native lower latency scenarios such as instant messaging. It is thus
complementary to it.

Strictly speaking, it is not just doing basic request response, but performs
sender push based on receiver intent. While this can be seen as a form of light
pub/sub, it is only used between two nodes in a direct fashion. Unlike the
Gossip domain, this is meant for light nodes which put a premium on bandwidth.
No gossiping takes place.

It is worth noting that a light node could get by with only using the `store`
protocol to query for a recent time window, provided it is acceptable to do
frequent polling.

## Design Requirements

The effectiveness and reliability of the content filtering service
enabled by `WakuFilter` protocol rely on the *high availability* of the full nodes
as the service providers.
To this end, full nodes must feature *high uptime*
(to persistently listen and capture the network messages)
as well as *high Bandwidth* (to provide timely message delivery to the light nodes).

## Security Consideration

Note that while using `WakuFilter` allows light nodes to save bandwidth,
it comes with a privacy cost in the sense that they need to disclose their liking
topics to the full nodes to retrieve the relevant messages.
Currently, anonymous subscription is not supported by the `WakuFilter`, however,
potential solutions in this regard are sketched below in [Future Work](#future-work)
section.

### Terminology

The term Personally identifiable information (PII)
refers to any piece of data that can be used to uniquely identify a user.
For example, the signature verification key, and
the hash of one's static IP address are unique for each user and hence count as PII.

## Adversarial Model

Any node running the `WakuFilter` protocol i.e.,
both the subscriber node and the queried node are considered as an adversary.
Furthermore, we consider the adversary as a passive entity
that attempts to collect information from other nodes to conduct an attack but
it does so without violating protocol definitions and instructions.
For example, under the passive adversarial model,
no malicious node intentionally hides the messages matching
to one's subscribed content filter as it is against the description
of the `WakuFilter` protocol.

The following are not considered as part of the adversarial model:

- An adversary with a global view of all the nodes and their connections.
- An adversary that can eavesdrop on communication links
between arbitrary pairs of nodes (unless the adversary is one end of the communication).
In specific, the communication channels are assumed to be secure.

### Protobuf

```protobuf
message FilterRequest {
  bool subscribe = 1;
  string topic = 2;
  repeated ContentFilter contentFilters = 3;

  message ContentFilter {
    string contentTopic = 1;
  }
}

message MessagePush {
  repeated WakuMessage messages = 1;
}

message FilterRPC {
  string requestId = 1;
  FilterRequest request = 2;
  MessagePush push = 3;
}
```

#### FilterRPC

A node MUST send all Filter messages (`FilterRequest`, `MessagePush`)
wrapped inside a `FilterRPC` this allows the node handler
to determine how to handle a message as the Waku Filter protocol
is not a request response based protocol but instead a push based system.

The `requestId` MUST be a uniquely generated string. When a `MessagePush` is sent
the `requestId` MUST match the `requestId` of the subscribing `FilterRequest`
whose filters matched the message causing it to be pushed.

#### FilterRequest

A `FilterRequest` contains an optional topic, zero or more content filters and
a boolean signifying whether to subscribe or unsubscribe to the given filters.
True signifies 'subscribe' and false signifies 'unsubscribe'.

A node that sends the RPC with a filter request and `subscribe` set to 'true'
requests that the filter node SHOULD notify the light requesting node of messages
matching this filter.

A node that sends the RPC with a filter request and `subscribe` set to 'false'
requests that the filter node SHOULD stop notifying the light requesting node
of messages matching this filter if it is currently doing so.

The filter matches when content filter and, optionally, a topic is matched.
Content filter is matched when a `WakuMessage` `contentTopic` field is the same.

A filter node SHOULD honor this request, though it MAY choose not to do so. If
it chooses not to do so it MAY tell the light why. The mechanism for doing this
is currently not specified. For notifying the light node a filter node sends a
MessagePush message.

Since such a filter node is doing extra work for a light node, it MAY also
account for usage and be selective in how much service it provides. This
mechanism is currently planned but underspecified.

#### MessagePush

A filter node that has received a filter request SHOULD push all messages that
match this filter to a light node. These [`WakuMessage`'s](../../../14/message.md)
are likely to come from the
`relay` protocol and be kept at the Node, but there MAY be other sources or
protocols where this comes from. This is up to the consumer of the protocol.

A filter node MUST NOT send a push message for messages that have not been
requested via a FilterRequest.

If a specific light node isn't connected to a filter node for some specific
period of time (e.g. a TTL), then the filter node MAY choose to not push these
messages to the node. This period is up to the consumer of the protocol and node
implementation, though a reasonable default is one minute.

---

## Future Work
<!-- Alternative title: Filter-subscriber unlinkability -->
**Anonymous filter subscription**:
This feature guarantees that nodes can anonymously subscribe for a message filter
(i.e., without revealing their exact content filter).
 As such, no adversary in the `WakuFilter` protocol would be able to link nodes
to their subscribed content filers.
The current version of the `WakuFilter` protocol does not provide anonymity
as the subscribing node has a direct connection to the full node and
explicitly submits its content filter to be notified about the matching messages.
However, one can consider preserving anonymity through one of the following ways:

- By hiding the source of the subscription i.e., anonymous communication.
That is the subscribing node shall hide all its PII in its filter request e.g.,
its IP address.
This can happen by the utilization of a proxy server or by using Tor
<!-- TODO: if nodes have to disclose their PeerIDs (e.g., for authentication purposes)
when connecting to other nodes in the WakuFilter protocol,
then Tor does not preserve anonymity since it only helps in hiding the IP.
So, the PeerId usage in switches must be investigated further.
Depending on how PeerId is used, one may be able to link between a subscriber and
its content filter despite hiding the IP address-->.
Note that the current structure of filter requests i.e.,
`FilterRPC` does not embody any piece of PII, otherwise,
such data fields must be treated carefully to achieve anonymity.

- By deploying secure 2-party computations in which the subscribing node obtains
the messages matching a content filter whereas the full node learns nothing
about the content filter as well as the messages pushed to the subscribing node.
Examples of such 2PC protocols are [Oblivious Transfers](https://link.springer.com/referenceworkentry/10.1007%2F978-1-4419-5906-5_9#:~:text=Oblivious%20transfer%20(OT)%20is%20a,information%20the%20receiver%20actually%20obtains.)
and one-way Private Set Intersections (PSI).

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [Message Filtering (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern#Message_filtering)

2. [Libp2p PubSub spec - topic validation](https://github.com/libp2p/specs/tree/master/pubsub#topic-validation)
