# 23/WAKU2-TOPICS

| Field | Value |
| --- | --- |
| Name | Waku v2 Topic Usage Recommendations |
| Slug | 23 |
| Status | draft |
| Type | RFC |
| Category | Informational |
| Editor | Oskar Thoren <oskarth@titanproxy.com> |
| Contributors | Hanno Cornelius <hanno@status.im>, Daniel Kaiser <danielkaiser@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/informational/23/topics.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/informational/23/topics.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/informational/23/topics.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/informational/23/topics.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/informational/23/topics.md) — ci: add mdBook configuration (#233)
- **2025-04-22** — [`4df2d5f`](https://github.com/logos-co/logos-lips/blob/4df2d5f78797cd591d0fbe835444be6c3a596810/waku/informational/23/topics.md) — update waku/informational/23/topics.md (#144)
- **2025-01-02** — [`dc7497a`](https://github.com/logos-co/logos-lips/blob/dc7497a3123623f2834d80ebd3a7c77e0d605074/waku/informational/23/topics.md) — add usage guidelines for waku content topics (#117)
- **2024-11-20** — [`ff87c84`](https://github.com/logos-co/logos-lips/blob/ff87c84dc71d4f933bab188993914069fea12baa/waku/informational/23/topics.md) — Update Waku Links (#104)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/informational/23/topics.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/informational/23/topics.md) — Broken Links + Change Editors (#26)
- **2024-02-07** — [`e63d8a0`](https://github.com/logos-co/logos-lips/blob/e63d8a0e67d1a32cbca1aeea072c0293a117beb5/waku/informational/23/topics.md) — Update topics.md
- **2024-01-31** — [`b8f088c`](https://github.com/logos-co/logos-lips/blob/b8f088c89611d117b58883663c55e3b402e95846/waku/informational/23/topics.md) — Update and rename README.md to topics.md
- **2024-01-31** — [`2b693e8`](https://github.com/logos-co/logos-lips/blob/2b693e8551c228418be07c0c764f18df8dcc8b5e/waku/informational/23/README.md) — Update README.md
- **2024-01-29** — [`055c525`](https://github.com/logos-co/logos-lips/blob/055c5254f675fdd7227772d0f371386c41201384/waku/informational/23/README.md) — Update README.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/informational/23/README.md) — remove rfs folder
- **2024-01-25** — [`a11dfed`](https://github.com/logos-co/logos-lips/blob/a11dfed6e2622d8c71b1d5ba41f236b69192d9dc/waku/rfcs/informational/23/README.md) — Create README.md

<!-- timeline:end -->

This document outlines recommended usage of topic names in Waku v2.
In [10/WAKU2 spec](/messaging/standards/core/10/waku2.md) there are two types of topics:

- Pubsub topics, used for routing
- Content topics, used for content-based filtering

## Pubsub Topics

Pubsub topics are used for routing of messages (see [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)),
and can be named implicitly by Waku sharding (see [RELAY-SHARDING](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/relay-sharding.md)).
This document comprises recommendations for explicitly naming pubsub topics
(e.g. when choosing *named sharding* as specified in [RELAY-SHARDING](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/relay-sharding.md)).

### Pubsub Topic Format

Pubsub topics SHOULD follow the following structure:

`/waku/2/{topic-name}`

This namespaced structure makes compatibility, discoverability,
and automatic handling of new topics easier.

The first two parts indicate:

1) it relates to the Waku protocol domain, and
2) the version is 2.

If applicable, it is RECOMMENDED to structure `{topic-name}`
in a hierarchical way as well.

> *Note*: In previous versions of this document, the structure was `/waku/2/{topic-name}/{encoding}`.
The now deprecated `/{encoding}` was always set to `/proto`,
which indicated that the [data field](/messaging/standards/core/11/relay.md#protobuf-definition)
in pubsub is serialized/encoded as protobuf.
The inspiration for this format was taken from
[Ethereum 2 P2P spec](https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/p2p-interface.md#topics-and-messages).
However, because the payload of messages transmitted over [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)
must be a [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md),
which specifies the wire format as protobuf,`/proto` is the only valid encoding.
This makes the `/proto` indication obsolete.
The encoding of the `payload` field of a WakuMessage
is indicated by the `/{encoding}` part of the content topic name.
Specifying an encoding is only significant for the actual payload/data field.
Waku preserves this option by allowing to specify an encoding
for the WakuMessage payload field as part of the content topic name.

### Default PubSub Topic

The Waku v2 default pubsub topic is:

`/waku/2/default-waku/proto`

The `{topic name}` part is `default-waku/proto`,
which indicates it is default topic for exchanging WakuMessages;
`/proto` remains for backwards compatibility.

### Application Specific Names

Larger apps can segregate their pubsub meshes using topics named like:

```text
/waku/2/status/
/waku/2/walletconnect/
```

This indicates that these networks carry WakuMessages,
but for different domains completely.

### Named Topic Sharding Example

The following is an example of named sharding, as specified in [RELAY-SHARDING](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/relay-sharding.md).

```text
waku/2/waku-9_shard-0/
...
waku/2/waku-9_shard-9/
```

This indicates explicitly that the network traffic has been partitioned into 10 buckets.

## Content Topics

The other type of topic that exists in Waku v2 is a content topic.
This is used for content based filtering.
See [14/WAKU2-MESSAGE spec](/messaging/standards/core/14/message.md)
for where this is specified.
Note that this doesn't impact routing of messages between relaying nodes,
but it does impact using request/reply protocols such as
[12/WAKU2-FILTER](/messaging/standards/core/12/filter.md) and
[13/WAKU2-STORE](/messaging/standards/core/13/store.md).

This is especially useful for nodes that have limited bandwidth,
and only want to pull down messages that match this given content topic.

Since all messages are relayed using the relay protocol regardless of content topic,
you MAY use any content topic you wish
without impacting how messages are relayed.

### Content Topic Format

The format for content topics is as follows:

`/{application-name}/{version-of-the-application}/{content-topic-name}/{encoding}`

The name of a content topic is application-specific.
As an example, here's the content topic used for an upcoming testnet:

`/toychat/2/huilong/proto`

### Content Topic Naming Recommendations

Application names SHOULD be unique to avoid conflicting issues with other protocols.
Application version (if applicable) SHOULD be specified in the version field.
The `{content-topic-name}` portion of the content topic is up to the application,
and depends on the problem domain.
It can be hierarchical, for instance to separate content, or
to indicate different bandwidth and privacy guarantees.
The encoding field indicates the serialization/encoding scheme
for the [WakuMessage payload](/messaging/standards/core/14/message.md#payloads) field.

### Content Topic usage guidelines

Applications SHOULD be mindful while designing/using content topics
so that a bloat of content-topics does not happen.
A content-topic bloat causes performance degradation in Store
and Filter protocols while trying to retrieve messages.

Store queries have been noticed to be considerably slow
(e.g doubling of response-time when content-topic count is increased from 10 to 100)
when a lot of content-topics are involved in a single query.
Similarly, a number of filter subscriptions increase,
which increases complexity on client side to maintain
and manage these subscriptions.

Applications SHOULD analyze the query/filter criteria for fetching messages from the network
and select/design content topics to match such filter criteria.
e.g: even though applications may want to segregate messages into different sets
based on some application logic,
if those sets of messages are always fetched/queried together from the network,
then all those messages SHOULD use a single content-topic.

## Differences with Waku v1

In [5/WAKU1](/messaging/deprecated/5/waku0.md) there is no actual routing.
All messages are sent to all other nodes.
This means that we are implicitly using the same pubsub topic
that would be something like:

```text
/waku/1/default-waku/rlp
```

Topics in Waku v1 correspond to Content Topics in Waku v2.

### Bridging Waku v1 and Waku v2

To bridge Waku v1 and Waku v2 we have a [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md).
For mapping Waku v1 topics to Waku v2 content topics,
the following structure for the content topic SHOULD be used:

```text
/waku/1/<4bytes-waku-v1-topic>/rfc26
```

The `<4bytes-waku-v1-topic>` SHOULD be the lowercase hex representation
of the 4-byte Waku v1 topic.
A `0x` prefix SHOULD be used.
`/rfc26` indicates that the bridged content is encoded according to RFC [26/WAKU2-PAYLOAD](/messaging/standards/application/26/payload.md).
See [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md)
for a description of the bridged fields.

This creates a direct mapping between the two protocols.
For example:

```text
/waku/1/0x007f80ff/rfc26
```

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [10/WAKU2 spec](/messaging/standards/core/10/waku2.md)
- [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)
- [RELAY-SHARDING](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/standards/core/relay-sharding.md)
- [Ethereum 2 P2P spec](https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/p2p-interface.md#topics-and-messages)
- [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md)
- [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)
- [13/WAKU2-STORE](/messaging/standards/core/13/store.md)
- [6/WAKU1](/messaging/deprecated/5/waku0.md)
- [15/WAKU-BRIDGE](/messaging/standards/core/15/bridge.md)
- [26/WAKU-PAYLOAD](/messaging/standards/application/26/payload.md)
