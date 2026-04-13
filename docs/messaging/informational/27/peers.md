# 27/WAKU2-PEERS

| Field | Value |
| --- | --- |
| Name | Waku v2 Client Peer Management Recommendations |
| Slug | 27 |
| Status | draft |
| Type | RFC |
| Category | Informational |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`f01d5b9`](https://github.com/vacp2p/rfc-index/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/informational/27/peers.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/informational/27/peers.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/vacp2p/rfc-index/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/informational/27/peers.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/vacp2p/rfc-index/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/informational/27/peers.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/vacp2p/rfc-index/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/informational/27/peers.md) — ci: add mdBook configuration (#233)
- **2025-04-22** — [`af7c413`](https://github.com/vacp2p/rfc-index/blob/af7c413e64bf1e9f57a68c22b7237883b080939a/waku/informational/27/peers.md) — update waku/informational/27/peers.md (#145)
- **2024-09-13** — [`3ab314d`](https://github.com/vacp2p/rfc-index/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/informational/27/peers.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/vacp2p/rfc-index/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/informational/27/peers.md) — Broken Links + Change Editors (#26)
- **2024-01-31** — [`4b77d10`](https://github.com/vacp2p/rfc-index/blob/4b77d10404952e0409f68a41620ea73c82bd644c/waku/informational/27/peers.md) — Update and rename README.md to peers.md
- **2024-01-31** — [`e65c359`](https://github.com/vacp2p/rfc-index/blob/e65c3591d7991e2f24a4632a6186ed1cef970326/waku/informational/27/README.md) — Update README.md
- **2024-01-31** — [`4a78cac`](https://github.com/vacp2p/rfc-index/blob/4a78cacb58706e1bb6f5b9b8d40e3fb27bc77cba/waku/informational/27/README.md) — Update README.md
- **2024-01-27** — [`eef961b`](https://github.com/vacp2p/rfc-index/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/informational/27/README.md) — remove rfs folder
- **2024-01-25** — [`7daec2f`](https://github.com/vacp2p/rfc-index/blob/7daec2f2f940535b38cc4e6d00c059a706ace3c9/waku/rfcs/informational/27/README.md) — Create README.md

<!-- timeline:end -->

`27/WAKU2-PEERS` describes a recommended minimal set of peer storage and
peer management features to be implemented by Waku v2 clients.

In this context, peer _storage_ refers to a client's ability to keep track of discovered
or statically-configured peers and their metadata.
It also deals with matters of peer _persistence_,
or the ability to store peer data on disk to resume state after a client restart.

Peer _management_ is a closely related concept and
refers to the set of actions a client MAY choose to perform
based on its knowledge of its connected peers,
e.g. triggering reconnects/disconnects,
keeping certain connections alive, etc.

## Peer store

The peer store SHOULD be an in-memory data structure
where information about discovered or configured peers are stored.
It SHOULD be considered the main source of truth
for peer-related information in a Waku v2 client.
Clients MAY choose to persist this store on-disk.

### Tracked peer metadata

It is RECOMMENDED that a Waku v2 client tracks at least the following information
about each of its peers in a peer store:

| Metadata | Description  |
| --- | --- |
| _Public key_  | The public key for this peer. This is related to the libp2p [`Peer ID`](https://docs.libp2p.io/concepts/peer-id/). |
| _Addresses_ | Known transport layer [`multiaddrs`](https://docs.libp2p.io/concepts/addressing/) for this peer. |
| _Protocols_ | The libp2p [`protocol IDs`](https://docs.libp2p.io/concepts/protocols/#protocol-ids) supported by this peer. This can be used to track the client's connectivity to peers supporting different Waku v2 protocols, e.g. [`11/WAKU2-RELAY`](../../standards/core/11/relay.md) or [`13/WAKU2-STORE`](../../standards/core/13/store.md). |
| _Connectivity_ | Tracks the peer's current connectedness state. See [**Peer connectivity**](#peer-connectivity) below. |
| _Disconnect time_ | The timestamp at which this peer last disconnected. This becomes important when managing [peer reconnections](#reconnecting-peers) |

### Peer connectivity

A Waku v2 client SHOULD track _at least_ the following connectivity states
for each of its peers:

- **`NotConnected`**: The peer has been discovered or configured on this client,
 but no attempt has yet been made to connect to this peer.
 This is the default state for a new peer.
- **`CannotConnect`**: The client attempted to connect to this peer, but failed.
- **`CanConnect`**: The client was recently connected to this peer and
disconnected gracefully.
- **`Connected`**: The client is actively connected to this peer.

This list does not preclude clients from tracking more advanced connectivity metadata,
such as a peer's blacklist status (see [`18/WAKU2-SWAP`](/messaging/deprecated/18/swap.md)).

### Persistence

A Waku v2 client MAY choose to persist peers across restarts,
using any offline storage technology, such as an on-disk database.
Peer persistence MAY be used to resume peer connections after a client restart.

## Peer management

Waku v2 clients will have different requirements
when it comes to managing the peers tracked in the [**peer store**](#peer-store).
It is RECOMMENDED that clients support:

- [automatic reconnection](#reconnecting-peers) to peers under certain conditions
- [connection keep-alive](#connection-keep-alive)

### Reconnecting peers

A Waku v2 client MAY choose to reconnect to previously connected,
managed peers under certain conditions.
Such conditions include, but are not limited to:

- Reconnecting to all `relay`-capable peers after a client restart.
This will require [persistent peer storage](#persistence).

If a client chooses to automatically reconnect to previous peers,
it MUST respect the
[backing off period](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#prune-backoff-and-peer-exchange)
specified for GossipSub v1.1 before attempting to reconnect.
This requires keeping track of the [last time each peer was disconnected](#tracked-peer-metadata).

### Connection keep-alive

A Waku v2 client MAY choose to implement a keep-alive mechanism to certain peers.
If a client chooses to implement keep-alive on a connection,
it SHOULD do so by sending periodic [libp2p pings](https://docs.libp2p.io/concepts/fundamentals/protocols/#ping)
as per `10/WAKU2` [client recommendations](/messaging/standards/core/10/waku2.md#recommendations-for-clients).
The recommended period between pings SHOULD be _at most_ 50%
of the shortest idle connection timeout for the specific client and transport.
For example, idle TCP connections often times out after 10 to 15 minutes.

> **Implementation note:**
the `nim-waku` client currently implements a keep-alive mechanism every `5 minutes`,
in response to a TCP connection timeout of `10 minutes`.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [`Peer ID`](https://docs.libp2p.io/concepts/peer-id/)
- [`multiaddrs`](https://docs.libp2p.io/concepts/addressing/)
- [`protocol IDs`](https://docs.libp2p.io/concepts/protocols/#protocol-ids)
- [`11/WAKU2-RELAY`](/messaging/standards/core/11/relay.md)
- [`13/WAKU2-STORE`](/messaging/standards/core/13/store.md)
- [`18/WAKU2-SWAP`](/messaging/deprecated/18/swap.md)
- [backing off period](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md/#prune-backoff-and-peer-exchange)
- [libp2p pings](https://docs.libp2p.io/concepts/fundamentals/protocols/#ping)
- [`10/WAKU2` client recommendations](/messaging/standards/core/10/waku2.md#recommendations-for-clients)
