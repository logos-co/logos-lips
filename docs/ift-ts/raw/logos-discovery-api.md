# LOGOS-DISCOVERY-API

| Field | Value |
| --- | --- |
| Name | Logos Discovery API |
| Slug | 145  |
| Status | raw |
| Category | Standards Track |
| Editor | Simon-Pierre Vivier <simvivier@status.im> |
| Contributors | Hanno Cornelius <hanno@status.im>|

## Abstract

TODO

## Motivation

TODO

## Semantic

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

Please refer to [libp2p Kademlia DHT specification](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md) (`Kad-DHT`)
and [extensible peer records specification](https://github.com/vacp2p/rfc-index/blob/513d8eae6be8b7b30bf427023ac686df2f2918c0/docs/ift-ts/raw/extensible-peer-records.md) (`XPR`) for terminology used in this document.

## API Specification

The aim is to define an API that is compatible with most discovery protocols,
maintaining similar function signatures even if the underlying protocol differs.

The API is defined in the form of C-style bindings.
However, this simply serves to illustrate the exposed functions
and can be adapted into the conventions of any strongly typed language.
Although unspecified in the API below,
all functions SHOULD return an error result type appropriate to the implementation language.

### `start()`

Start the discovery protocol,
including all tasks related to bootstrapping, maintenance
and advertising of this node and its services.

### `stop()`

Stop the discovery protocol,
including all tasks related to node maintenance
and advertising of its services.

### `start_advertising(const char* service_id, const byte* advertisement)`

Start advertising this node against the service
encoded as an input `service_id` string
and an `advertisement` raw bytes.

### `stop_advertising(const char* service_id)`

Stop advertising this node against the service
encoded in the input `service_id` string.

### `ExtensiblePeerRecords* lookup(const char* service_id)`

Lookup and return records for peers supporting
the service encoded in the input `service_id` string,
using the underlying discovery protocol.

### `ExtensiblePeerRecords* lookup_random()`

Reserved for future use.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [extended peer records specification](https://github.com/vacp2p/rfc-index/blob/513d8eae6be8b7b30bf427023ac686df2f2918c0/docs/ift-ts/raw/extensible-peer-records.md)
- [libp2p Kademlia DHT specification](https://github.com/libp2p/specs/blob/e87cb1c32a666c2229d3b9bb8f9ce1d9cfdaa8a9/kad-dht/README.md)
- [RFC002 Signed Envelope](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0002-signed-envelopes.md)
- [RFC003 Routing Records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md)
- [logos service discovery](https://github.com/vacp2p/rfc-index/blob/155c310d7bfad6ea3cd9f68e45c68dad731ff629/docs/ift-ts/raw/logos-service-discovery.md)