# 12/WAKU2-FILTER

| Field | Value |
| --- | --- |
| Name | Waku v2 Filter |
| Slug | 12 |
| Status | draft |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Dean Eigenmann <dean@status.im>, Oskar Thorén <oskar@status.im>, Sanaz Taheri <sanaz@status.im>, Ebube Ud <ebube@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/core/12/filter.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/12/filter.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/12/filter.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/12/filter.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/12/filter.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/12/filter.md) — ci: add mdBook configuration (#233)
- **2025-03-25** — [`e8a3f8a`](https://github.com/logos-co/logos-lips/blob/e8a3f8a77ddfc84894f4e1119380e90ca2dd0ab4/waku/standards/core/12/filter.md) — 12/WAKU2-FILTER: Update (#119)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/12/filter.md) — Fix Files for Linting (#94)
- **2024-02-01** — [`e4d8f27`](https://github.com/logos-co/logos-lips/blob/e4d8f27fd57d64512a482c669fb30d949c1afe90/waku/standards/core/12/filter.md) — Update and rename FILTER.md to filter.md
- **2024-01-27** — [`046a3b7`](https://github.com/logos-co/logos-lips/blob/046a3b77a53e01a34e5b71fc3aa7af731af366ce/waku/standards/core/12/FILTER.md) — Rename WAKU2-FILTER.md to FILTER.md
- **2024-01-27** — [`57124a7`](https://github.com/logos-co/logos-lips/blob/57124a766cb9e87a5ae6a81522c7725ffd888d61/waku/standards/core/12/WAKU2-FILTER.md) — Rename README.md to WAKU2-FILTER.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/12/README.md) — remove rfs folder
- **2024-01-25** — [`940d795`](https://github.com/logos-co/logos-lips/blob/940d7958a286701155f6e8739494e426490e14c4/waku/rfcs/standards/core/12/README.md) — Rename waku/12/README.md to waku/rfcs/standards/core/12/README.md
- **2024-01-22** — [`420adf1`](https://github.com/logos-co/logos-lips/blob/420adf1bd6fe714366bb11667400b923772835da/waku/12/README.md) — Vac RFC index initial structure

<!-- timeline:end -->

**Protocol identifiers**:

- _filter-subscribe_: `/vac/waku/filter-subscribe/2.0.0-beta1`
- _filter-push_: `/vac/waku/filter-push/2.0.0-beta1`

---

## Abstract

This specification describes the `12/WAKU2-FILTER` protocol,
which enables a client to subscribe to a subset of real-time messages from a Waku peer.
This is a more lightweight version of [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md),
useful for bandwidth restricted devices.
This is often used by nodes with lower resource limits to subscribe to full Relay nodes and
only receive the subset of messages they desire,
based on content topic interest.

## Motivation

Unlike the [13/WAKU2-STORE](/messaging/standards/core/13/store.md) protocol
for historical messages, this protocol allows for native lower latency scenarios,
such as instant messaging.
It is thus complementary to it.

Strictly speaking, it is not just doing basic request-response, but
performs sender push based on receiver intent.
While this can be seen as a form of light publish/subscribe,
it is only used between two nodes in a direct fashion. Unlike the
Gossip domain, this is suitable for light nodes which put a premium on bandwidth.
No gossiping takes place.

It is worth noting that a light node could get by with only using the
[13/WAKU2-STORE](/messaging/standards/core/13/store.md) protocol to
query for a recent time window, provided it is acceptable to do frequent polling.

## Semantics

The key words “MUST”, “MUST NOT”, “REQUIRED”,
“SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Content filtering

Content filtering is a way to do
[message-based filtering](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern#Message_filtering).
Currently the only content filter being applied is on `contentTopic`.

### Terminology

The term Personally identifiable information (PII)
refers to any piece of data that can be used to uniquely identify a user.
For example, the signature verification key, and
the hash of one's static IP address are unique for each user and hence count as PII.

### Protobuf

```protobuf
syntax = "proto3";

// Protocol identifier: /vac/waku/filter-subscribe/2.0.0-beta1
message FilterSubscribeRequest {
  enum FilterSubscribeType {
    SUBSCRIBER_PING = 0;
    SUBSCRIBE = 1;
    UNSUBSCRIBE = 2;
    UNSUBSCRIBE_ALL = 3;
  }

  string request_id = 1;
  FilterSubscribeType filter_subscribe_type = 2;

  // Filter criteria
  optional string pubsub_topic = 10;
  repeated string content_topics = 11;
}

message FilterSubscribeResponse {
  string request_id = 1;
  uint32 status_code = 10;
  optional string status_desc = 11;
}

// Protocol identifier: /vac/waku/filter-push/2.0.0-beta1
message MessagePush {
  WakuMessage waku_message = 1;
  optional string pubsub_topic = 2;
}
```

### Filter-Subscribe

A filter service node MUST support the _filter-subscribe_ protocol
to allow filter clients to subscribe, modify, refresh and
unsubscribe a desired set of filter criteria.
The combination of different filter criteria
for a specific filter client node is termed a "subscription".
A filter client is interested in receiving messages matching the filter criteria
in its registered subscriptions.

Since a filter service node is consuming resources to provide this service,
it MAY account for usage and adapt its service provision to certain clients.

#### Filter Subscribe Request

A client node MUST send all filter requests in a `FilterSubscribeRequest` message.
This request MUST contain a `request_id`.
The `request_id` MUST be a uniquely generated string.
Each request MUST include a `filter_subscribe_type`, indicating the type of request.

#### Filter Subscribe Response

When responding to a `FilterSubscribeRequest`,
a filter service node SHOULD send a `FilterSubscribeResponse`
with a `requestId` matching that of the request.
This response MUST contain a `status_code` indicating if the request was successful
or not.
Successful status codes are in the `2xx` range.
Client nodes SHOULD consider all other status codes as error codes and
assume that the requested operation had failed.
In addition,
the filter service node MAY choose to provide a more detailed status description
in the `status_desc` field.

#### Filter matching

In the description of each request type below,
the term "filter criteria" refers to the combination of `pubsub_topic` and
a set of `content_topics`.
The request MAY include filter criteria,
conditional to the selected `filter_subscribe_type`.
If the request contains filter criteria,
it MUST contain a `pubsub_topic`
and the `content_topics` set MUST NOT be empty.
A [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) matches filter criteria
when its `content_topic` is in the `content_topics` set
and it was published on a matching `pubsub_topic`.

#### Filter Subscribe Types

The filter-subscribe types are defined as follows:

##### SUBSCRIBER_PING

A filter client that sends a `FilterSubscribeRequest` with
`filter_subscribe_type` set to `SUBSCRIBER_PING`,
requests that the filter service node SHOULD indicate if it has any active subscriptions
for this client.
The filter client SHOULD exclude any filter criteria from the request.
The filter service node SHOULD respond with a success `status_code`
if it has any active subscriptions for this client
or an error `status_code` if not.
The filter service node SHOULD ignore any filter criteria in the request.

##### SUBSCRIBE

A filter client that sends a `FilterSubscribeRequest` with
`filter_subscribe_type` set to `SUBSCRIBE`
requests that the filter service node SHOULD push messages
matching this filter to the client.
The filter client MUST include the desired filter criteria in the request.
A client MAY use this request type to _modify_ an existing subscription
by providing _additional_ filter criteria in a new request.
A client MAY use this request type to _refresh_ an existing subscription
by providing _the same_ filter criteria in a new request.
The filter service node SHOULD respond with a success `status_code`
if it successfully honored this request
or an error `status_code` if not.
The filter service node SHOULD respond with an error `status_code` and
discard the request if the `FilterSubscribeRequest`
does not contain valid filter criteria,
i.e. both a `pubsub_topic` _and_ a non-empty `content_topics` set.

##### UNSUBSCRIBE

A filter client that sends a `FilterSubscribeRequest` with
`filter_subscribe_type` set to `UNSUBSCRIBE`
requests that the service node SHOULD _stop_ pushing messages
matching this filter to the client.
The filter client MUST include the filter criteria
it desires to unsubscribe from in the request.
A client MAY use this request type to _modify_ an existing subscription
by providing _a subset of_ the original filter criteria
to unsubscribe from in a new request.
The filter service node SHOULD respond with a success `status_code`
if it successfully honored this request
or an error `status_code` if not.
The filter service node SHOULD respond with an error `status_code` and
discard the request if the unsubscribe request does not contain valid filter criteria,
i.e. both a `pubsub_topic` _and_ a non-empty `content_topics` set.

##### UNSUBSCRIBE_ALL

A filter client that sends a `FilterSubscribeRequest` with
`filter_subscribe_type` set to `UNSUBSCRIBE_ALL`
requests that the service node SHOULD _stop_ pushing messages
matching _any_ filter to the client.
The filter client SHOULD exclude any filter criteria from the request.
The filter service node SHOULD remove any existing subscriptions for this client.
It SHOULD respond with a success `status_code` if it successfully honored this request
or an error `status_code` if not.

### Filter-Push

A filter client node MUST support the _filter-push_ protocol
to allow filter service nodes to push messages
matching registered subscriptions to this client.

A filter service node SHOULD push all messages
matching the filter criteria in a registered subscription
to the subscribed filter client.
These [`WakuMessage`s](/messaging/standards/core/14/message.md)
are likely to come from [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md),
but there MAY be other sources or protocols where this comes from.
This is up to the consumer of the protocol.

If a message push fails,
the filter service node MAY consider the client node to be unreachable.
If a specific filter client node is not reachable from the service node
for a period of time,
the filter service node MAY choose to stop pushing messages to the client and
remove its subscription.
This period is up to the service node implementation.
It is RECOMMENDED to set `1 minute` as a reasonable default.

#### Message Push

Each message MUST be pushed in a `MessagePush` message.
Each `MessagePush` MUST contain one (and only one) `waku_message`.
If this message was received on a specific `pubsub_topic`,
it SHOULD be included in the `MessagePush`.
A filter client SHOULD NOT respond to a `MessagePush`.
Since the filter protocol does not include caching or fault-tolerance,
this is a best effort push service with no bundling
or guaranteed retransmission of messages.
A filter client SHOULD verify that each `MessagePush` it receives
originated from a service node where the client has an active subscription
and that it matches filter criteria belonging to that subscription.

### Adversarial Model

Any node running the `WakuFilter` protocol
i.e., both the subscriber node and
the queried node are considered as an adversary.
Furthermore, we consider the adversary as a passive entity
that attempts to collect information from other nodes to conduct an attack but
it does so without violating protocol definitions and instructions.
For example, under the passive adversarial model,
no malicious node intentionally hides the messages
matching to one's subscribed content filter
as it is against the description of the `WakuFilter` protocol.

The following are not considered as part of the adversarial model:

- An adversary with a global view of all the nodes and their connections.
- An adversary that can eavesdrop on communication links
between arbitrary pairs of nodes (unless the adversary is one end of the communication).
In specific, the communication channels are assumed to be secure.

### Security Considerations

Note that while using `WakuFilter` allows light nodes to save bandwidth,
it comes with a privacy cost in the sense that they need to
disclose their liking topics to the full nodes to retrieve the relevant messages.
Currently, anonymous subscription is not supported by the `WakuFilter`, however,
potential solutions in this regard are discussed below.

#### Future Work
<!-- Alternative title: Filter-subscriber unlinkability -->
**Anonymous filter subscription**:
This feature guarantees that nodes can anonymously subscribe for a message filter
(i.e., without revealing their exact content filter).
As such, no adversary in the `WakuFilter` protocol
would be able to link nodes to their subscribed content filers.
The current version of the `WakuFilter` protocol does not provide anonymity
as the subscribing node has a direct connection to the full node and
explicitly submits its content filter to be notified about the matching messages.
However, one can consider preserving anonymity through one of the following ways:

- By hiding the source of the subscription i.e., anonymous communication.
That is the subscribing node shall hide all its PII in its filter request
e.g., its IP address.
This can happen by the utilization of a proxy server or by using Tor
<!-- TODO: if nodes have to disclose their PeerIDs
(e.g., for authentication purposes)
when connecting to other nodes in the WakuFilter protocol,
then Tor does not preserve anonymity since it only helps in hiding the IP.
So, the PeerId usage in switches must be investigated further.
Depending on how PeerId is used,
one may be able to link between a subscriber and
its content filter despite hiding the IP address-->.
Note that the current structure of filter requests
i.e., `FilterRPC` does not embody any piece of PII, otherwise,
such data fields must be treated carefully to achieve anonymity.

- By deploying secure 2-party computations in which
the subscribing node obtains the messages matching a content filter
whereas the full node learns nothing about the content filter as well as
the messages pushed to the subscribing node.
Examples of such 2PC protocols are
[Oblivious Transfers](https://link.springer.com/referenceworkentry/10.1007%2F978-1-4419-5906-5_9#:~:text=Oblivious%20transfer%20(OT)%20is%20a,information%20the%20receiver%20actually%20obtains.)
and one-way Private Set Intersections (PSI).

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## Previous versions

- [00](previous-versions/00/filter.md)

## References

- [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)
- [message-based filtering](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern#Message_filtering)
- [13/WAKU2-STORE](/messaging/standards/core/13/store.md)
- [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md)
- [Oblivious Transfers](https://link.springer.com/referenceworkentry/10.1007%2F978-1-4419-5906-5_9#:~:text=Oblivious%20transfer%20(OT)%20is%20a,information%20the%20receiver%20actually%20obtains)

### Informative

1. [Message Filtering (Wikipedia)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern#Message_filtering)
2. [Libp2p PubSub spec - topic validation](https://github.com/libp2p/specs/tree/master/pubsub#topic-validation)
