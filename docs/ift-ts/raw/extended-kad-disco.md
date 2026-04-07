# EXTENDED-KADEMLIA-DISCOVERY

| Field | Value |
| --- | --- |
| Name | Extended Kademlia Discovery with capability filtering |
| Slug | 143  |
| Status | raw |
| Category | Standards Track |
| Editor | Simon-Pierre Vivier <simvivier@status.im> |
| Contributors | Hanno Cornelius <hanno@status.im>|

<!-- timeline:start -->

## Timeline

- **2026-01-26** — [`8bba444`](https://github.com/vacp2p/rfc-index/blob/8bba4441aa3601cef6fb75ff5d48b1cd27350a5c/docs/ift-ts/raw/extended-kad-disco.md) — chore: fix lint (#275)
- **2026-01-23** — [`8164992`](https://github.com/vacp2p/rfc-index/blob/8164992534b14b2466fc1117bbeef2ae2d14f249/docs/ift-ts/raw/extended-kad-disco.md) — chore: fix lint

<!-- timeline:end -->

## Abstract

This specification defines a lightweight peer discovery mechanism
built on top of the libp2p Kademlia DHT.
It allows nodes to advertise themselves by storing a new type of peer record under
their own peer ID and enables other nodes to discover peers in the network via
random walks through the DHT.
The mechanism supports capability-based filtering of `services` entries,
making it suitable for overlay networks that
require connectivity to peers offering specific protocols or features.

## Motivation

The standard libp2p Kademlia DHT provides
content routing and peer routing toward specific keys or peer IDs,
but offers limited support for general-purpose random peer discovery
— i.e. finding *any well-connected peer* in the network.

Existing alternatives such as mDNS,
Rendezvous,
or bootstrap lists do not always satisfy the needs of
large-scale decentralized overlay networks that require:

- Organic growth of connectivity without strong trust in bootstrap nodes
- Discovery of peers offering specific capabilities (e.g. protocols, bandwidth classes, service availability)
- Resilience against eclipse attacks and network partitioning
- Low overhead compared to gossip-based or pubsub-based discovery

By leveraging the already-deployed Kademlia routing table and random-walk behavior,
this document define a simple, low-cost discovery primitive that reuses existing infrastructure while adding capability advertisement and filtering via a new record type.

## Semantic

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

Please refer to [libp2p Kademlia DHT specification](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md) (`Kad-DHT`)
and [extensible peer records specification](https://github.com/vacp2p/rfc-index/blob/31dfa0c8c2f3e7f7365156246c4eb7b7c390e76e/vac/raw/extensible-peer-records.md) (`XPR`) for terminology used in this document.

## Protocol

### Record Propagation

A node that wants to make itself discoverable,
also known as an _advertiser_,
MUST encode its discoverable information in an [`XPR`](https://github.com/vacp2p/rfc-index/blob/31dfa0c8c2f3e7f7365156246c4eb7b7c390e76e/vac/raw/extensible-peer-records.md#extensible-peer-records).
The encoded information MUST be sufficient for discoverers to connect to this advertiser.
It MAY choose to encode some or all of its capabilities (and related information)
as `services` in the `XPR`.
This will allow future discoverers to filter discovered records based on desired capabilities.

In order to advertise this record,
the advertiser SHOULD first retrieve the `k` closest peers to its own peer ID
in its own `Kad-DHT` [routing table](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md#kademlia-routing-table).
This assumes that the routing table has been previously initialised
and follows the regular [bootstrap process](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md#bootstrap-process) as per the `Kad-DHT` specification.
The advertiser SHOULD then send a `PUT_VALUE` message to these `k` peers
to store the `XPR` against its own peer ID.
This process SHOULD be repeated periodically to maintain the advertised record.
We RECOMMEND an interval of once every `30` minutes.

#### Use of `XPR` in `identify`

Advertisers SHOULD include their `XPR`s as the `signedPeerRecord`
in libp2p `Identify` [messages](https://github.com/libp2p/specs/blob/0762325f693afb2e620d32d4f55ba962d1293ff9/identify/README.md#the-identify-message).

> **Note:** For more information, see the `identify` protocol implementations,
such as [go-libp2p](https://github.com/libp2p/go-libp2p/blob/636d44e15abc7bfbd1da09cc9fef674249625ae6/p2p/protocol/identify/pb/identify.proto#L37),
as at the time of writing (Jan 2026)
the `signedPeerRecord` field extension is not yet part of any official specification.

### Record Discovery

A node that wants to discover peers to connect to,
also known as a _discoverer_,
SHOULD perform the following random walk discovery procedure (`FIND_RANDOM`):

1. Choose a random value in the `Kad-DHT` key space. (`R_KEY`).

2. Follow the `Kad-DHT` [peer routing](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md#peer-routing) algorithm,
with `R_KEY` as the target.
This procedure loops the `Kad-DHT` `FIND_NODE` procedure to the target key,
each time receiving closer peers (`closerPeers`) to the target key in response,
until no new closer peers can be found.
Since the target is random,
the discoverer SHOULD consider each _previously unseen_ peer in each response's `closerPeers` field,
as a randomly discovered node of potential interest.
The discoverer MUST keep track of such peers as `discoveredPeer`s.

3. For each `discoveredPeer`, attempt to retrieve a corresponding `XPR`.
This can be done in one of two ways:

    3.1 If the `discoveredPeer` in the response contains at least one multiaddress in the `addrs` field,
    attempt a connection to that peer and wait to receive the `XPR` as part of the [`identify` procedure](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/identify/README.md).

    3.2 If the `discoveredPeer` does not include `addrs` information,
    or the connection attempt to included `addrs` fails,
    or more service information is required before a connection can be attempted,
    MAY perform a [value retrieval](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md#value-retrieval) procedure to the `discoveredPeer` ID.

4. For each retrieved `XPR`, validate the signature against the peer ID.
In addition, the discoverer MAY filter discovered peers
based on the capabilities encoded within the `services` field of the `XPR`.
The discoverer SHOULD ignore (and disconnect, if already connected) discovered peers
with invalid `XPR`s
or that do not advertise the `services` of interest to the discoverer.

### Privacy Enhancements

To prevent network topology mapping and eclipse attacks,
`Kad-DHT` nodes MUST NOT disclose connection type in [response messages](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md#rpc-messages).
The `connection` field of every `Peer` MUST always be set to `NOT_CONNECTED`.

## API Specification

Implementers of this protocol,
SHOULD wrap the implementation in a functional interface similar to the one defined below.

In Extended Kademlia Discovery, the discovery protocol is based on a random DHT walk,
optionally filtering the randomly discovered peers by capability.
However, it's possible to define discovery protocols with better performance in finding peers with specific capabilities.
The aim is to define an API that is compatible with Extended Kademlia Discovery
and more sophisticated capability discovery protocols,
maintaining similar function signatures even if the underlying protocol differs.
This section may be extracted into a separate API specification once new capability discovery protocols are defined.

The API is defined in the form of C-style bindings.
However, this simply serves to illustrate the exposed functions
and can be adapted into the conventions of any strongly typed language.
Although unspecified in the API below,
all functions SHOULD return an error result type appropriate to the implementation language.

### `start()`

Start the discovery protocol,
including all tasks related to bootstrapping and maintaining the routing table
and advertising this node and its capabilities.

In the case of Extended Kademlia Discovery,
`start()` will kick off the periodic task of [refreshing the propagated `XPR`](#record-propagation).

### `stop()`

Stop the discovery protocol,
including all tasks related to maintaining the routing table
and advertising this node and its capabilities.

In the case of Extended Kademlia Discovery,
`stop()` will cancel the periodic task of [refreshing the propagated `XPR`](#record-propagation).

### `start_advertising(const char* service_id, const byte* advertisement)`

Start advertising this node against any capability
encoded as an input `service_id` string
and optionally an advertisement raw bytes.

In the case of Extended Kademlia Discovery,
`start_advertising()` will include the input `service_id`
in the [regularly propagated `XPR`](#record-propagation).

In the case of Service Discovery,
`start_advertising()` CAN include in addition to `service_id`
an already encoded advertisement in raw bytes form.

### `stop_advertising(const char* service_id)`

Stop advertising this node against the capability
encoded in the input `service_id` string.

In the case of Extended Kademlia Discovery,
`stop_advertising()` will exclude the `service_id`
from the [regularly propagated `XPR`](#record-propagation),
if it was previously included.

### `ExtensiblePeerRecords* lookup(const char* service_id, ...)`

Lookup and return records for peers supporting the capability encoded in the input `service_id` string,
using the underlying discovery protocol.

In the case of Extended Kademlia Discovery,
`service_id` MAY be included as an input argument.
If unset, it indicates a lookup for peers supporting any (or zero) capabilities.
`lookup()` will trigger the random walk [record discovery](#record-discovery),
filtering discovered records based on `service_id`, if specified.
If no `service_id` is specified,
Extended Kademlia Discovery will just return a random selection of peer records,
matching any capability.

In the case of Service Discovery,
`lookup()` MUST include a `service_id`.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [extended peer records specification](https://github.com/vacp2p/rfc-index/blob/31dfa0c8c2f3e7f7365156246c4eb7b7c390e76e/vac/raw/extensible-peer-records.md)
- [libp2p Kademlia DHT specification](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md)
- [RFC002 Signed Envelope](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0002-signed-envelopes.md)
- [RFC003 Routing Records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md)
- [capability discovery](https://github.com/vacp2p/rfc-index/blob/31dfa0c8c2f3e7f7365156246c4eb7b7c390e76e/vac/raw/logos-capability-discovery.md)
