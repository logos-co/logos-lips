# 66/WAKU2-METADATA

| Field | Value |
| --- | --- |
| Name | Waku Metadata Protocol |
| Slug | 66 |
| Status | draft |
| Category | Standards Track |
| Editor | Franck Royer <franck@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im>, Alvaro Revuelta <alrevuelta@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/core/66/metadata.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/66/metadata.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/66/metadata.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/66/metadata.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/66/metadata.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/66/metadata.md) — ci: add mdBook configuration (#233)
- **2025-07-31** — [`4361e29`](https://github.com/logos-co/logos-lips/blob/4361e2958f1c71269953206c7b09be7a88609d0c/waku/standards/core/66/metadata.md) — Add implementation recommendation for metadata (#168)
- **2025-05-13** — [`f829b12`](https://github.com/logos-co/logos-lips/blob/f829b12517476a054cbe5858de83c1d6ba303568/waku/standards/core/66/metadata.md) — waku/standards/core/66/metadata.md update (#148)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/66/metadata.md) — Fix Files for Linting (#94)
- **2024-04-17** — [`d82eacc`](https://github.com/logos-co/logos-lips/blob/d82eaccdc07b42e9b4d06d5127e560445e1e222a/waku/standards/core/66/metadata.md) — Update WAKU2-METADATA: Move to draft (#6)

<!-- timeline:end -->

## Abstract

This specification describes the metadata
that can be associated with a [10/WAKU2](/messaging/standards/core/10/waku2.md) node.

## Metadata Protocol

The keywords “MUST”, // List style “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”,
“NOT RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

Waku specifies a req/resp protocol that provides information about the node's capabilities.
Such metadata MAY be used by other peers for subsequent actions such as light protocol requests or disconnection.

The node that makes the request,
includes its metadata so that the receiver is aware of it,
without requiring another round trip.
The parameters are the following:

* `clusterId`: Unique identifier of the cluster that the node is running in.
* `shards`: Shard indexes that the node is subscribed to via [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md).

***Protocol Identifier***

> /vac/waku/metadata/1.0.0

### Request

```protobuf
message WakuMetadataRequest {
  optional uint32 cluster_id = 1;
  repeated uint32 shards = 2;
}
```

### Response

```protobuf
message WakuMetadataResponse {
  optional uint32 cluster_id = 1;
  repeated uint32 shards = 2;
}
```

## Implementation Suggestions

### Triggering Metadata Request

A node SHOULD proceed with metadata request upon first connection to a remote node.
A node SHOULD use the remote node's libp2p peer id as identifier for this heuristic.

A node MAY proceed with metadata request upon reconnection to a remote peer.

A node SHOULD store the remote peer's metadata information for future reference.
A node MAY implement a TTL regarding a remote peer's metadata, and refresh it upon expiry by initiating another metadata request.
It is RECOMMENDED to set the TTL to 6 hours.

A node MAY trigger a metadata request after receiving an error response from a remote note
stating they do not support a specific cluster or shard.
For example, when using a request-response service such as [`19/WAKU2-LIGHTPUSH`](/messaging/standards/core/19/lightpush.md).

### Providing Cluster Id

A node MUST include their cluster id into their metadata payload.
It is RECOMMENDED for a node to operate on a single cluster id.

### Providing Shard Information

* Nodes that mount [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md) MAY include the shards they are subscribed to in their metadata payload.
* Shard-relevant services are message related services,
  such as [`13/WAKU2-STORE`](/messaging/standards/core/13/store.md), [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)
  and [`19/WAKU2-LIGHTPUSH`](/messaging/standards/core/19/lightpush.md)
  but not [`34/WAKU2-PEER-EXCHANGE`](/messaging/standards/core/34/peer-exchange.md)
* Nodes that mount [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md) and a shard-relevant service SHOULD include the shards they are subscribed to in their metadata payload.
* Nodes that do not mount [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md) SHOULD NOT include any shard information

### Using Cluster Id

When reading the cluster id of a remote peer, the local node MAY disconnect if their cluster id is different from the remote peer.

### Using Shard Information

It is NOT RECOMMENDED to disconnect from a peer based on the fact that their shard information is different from the local node.

Ahead of doing a shard-relevant request,
a node MAY use the previously received metadata shard information to select a peer that support the targeted shard.

For non-shard-relevant requests, a node SHOULD NOT discriminate a peer based on medata shard information.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

* [10/WAKU2](/messaging/standards/core/10/waku2.md)
