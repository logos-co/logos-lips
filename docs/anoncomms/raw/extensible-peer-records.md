# EXTENSIBLE-PEER-RECORDS

| Field | Value |
| --- | --- |
| Name         | Extensible Peer Records                   |
| Slug         | 74                                        |
| Status       | raw                                       |
| Category     | Standards Track                           |
| Editor       | Hanno Cornelius <hanno@status.im>         |
| Contributors | Simon-Pierre Vivier <simvivier@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/anoncomms/raw/extensible-peer-records.md) — chore: split ift ts specs
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/extensible-peer-records.md) — chore: add math support (#287)
- **2026-01-24** — [`ffca40a`](https://github.com/logos-co/logos-lips/blob/ffca40abfa6b42f239439550cd2fc47fc802f22a/docs/ift-ts/raw/extensible-peer-records.md) — Mix spam and sybil protection protocol using RLN (#252)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/extensible-peer-records.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/extensible-peer-records.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This RFC proposes Extensible Peer Records,
an extension of libp2p's [routing records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md),
that enables peers to encode an arbitrary list of supported services and essential service-related information
in distributable records.
This version of routing records allows peers to communicate capabilities such as protocol support,
and essential information related to such capabilities.
This is especially useful when (signed) records are used in peer discovery,
allowing discoverers to filter for peers matching a desired set of capability criteria.
Extensible Peer Records maintain backwards compatibility with standard libp2p routing records,
while adding an extensible service information field that supports finer-grained capability communication.

> **_A note on terminology:_** We opt to call this structure a "_peer record_", even though the corresponding libp2p specification refers to a "_routing record_".
> This is because the libp2p specification itself defines an internal [`PeerRecord` type](https://github.com/libp2p/specs/blob/master/RFC/0003-routing-records.md#address-record-format),
> and, when serialised into a signed envelope, this is most often called a "_signed peer record_" (see, for example, [go-libp2p identify protocol](https://github.com/libp2p/go-libp2p/blob/479b24baab77b4b99d7e31462b91cc04f89f1de4/p2p/protocol/identify/pb/identify.proto#L37)).

The keywords “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

## Motivation

We propose a new peer record as an extension of libp2p's [RFC003 Routing Records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md)
that allows encoding an arbitrary list of services,
and essential information pertaining to those services,
supported by the peer.

There are at least two reasons why a peer might want to encode service information in its peer records:

1. **To augment `identify` with peer capabilities:**
   The libp2p [`identify` protocol](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/identify/README.md) allows peers to exchange critical information,
   such as supported protocols,
   on first connection.
   The peer record (in a signed envelope) can also be exchanged during `identify`.
   However, peers may want to exchange finer-grained information related to supported protocols/services,
   that would otherwise require an application-level negotiation protocol,
   or that is critical to connect to the service in the first place.
   An example would be nodes supporting libp2p [`mix` protocol](https://rfc.vac.dev/vac/raw/mix) also needing to exchange the mix key
   before the service can be used.
2. **To advertise supported services:**
   If the peer record is used as the discoverable record for a peer
   (as we propose for various discovery methods)
   that peer may want to encode a list of supported services
   in its advertised record.
   These services may be (but is not limited to) a list of supported libp2p protocols
   and critical information pertaining to that service (such as the mix key, explained above).
   Discoverers can then filter discovered records for desired capabilities
   based on the encoded service information
   or use it to initiate the service.

## Wire protocol

### Extensible Peer Records

Extensible Peer Records MUST adhere to the following structure:

```protobuf
syntax = "proto3";

package peer.pb;

// ExtensiblePeerRecord messages contain information that is useful to share with other peers.
// Currently, an ExtensiblePeerRecord contains the public listen addresses for a peer
// and an extensible list of supported services as key-value pairs.
//
// ExtensiblePeerRecords are designed to be serialised to bytes and placed inside of
// SignedEnvelopes before sharing with other peers.
message ExtensiblePeerRecord {

  // AddressInfo is a wrapper around a binary multiaddr. It is defined as a
  // separate message to allow us to add per-address metadata in the future.
  message AddressInfo {
    bytes multiaddr = 1;
  }

  // peer_id contains a libp2p peer id in its binary representation.
  bytes peer_id = 1;

  // seq contains a monotonically-increasing sequence counter to order ExtensiblePeerRecords in time.
  uint64 seq = 2;

  // addresses is a list of public listen addresses for the peer.
  repeated AddressInfo addresses = 3;

  message ServiceInfo{
    string id = 1;
    optional bytes data = 2;
  }

  // Extensible list of advertised services
  repeated ServiceInfo services = 4;
}
```

A peer MAY include a list of supported services in the `services` field.
These services could be libp2p protocols,
in which case it is RECOMMENDED that the `ServiceInfo` `id` field
be derived from the libp2p protocol identifier.
In any case, for each supported service,
the `id` field MUST be populated with a string identifier for that service.
In addition, the `data` field MAY be populated with additional information about the service.
It is RECOMMENDED that each `data` field be no more than `33` bytes.
(We choose `33` here to allow for the encoding of `256` bit keys with parity.
Also see [_Size constraints_](#size-constraints) for recommendations on limiting the overall record size.)

The rest of the `ExtensiblePeerRecord`
MUST be populated as per the libp2p [`PeerRecord` specification](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md).
Due to the natural extensibility of protocol buffers,
serialised `ExtensiblePeerRecord`s are backwards compatible with libp2p `PeerRecord`s,
only adding the functionality related to service info exchange.

#### Size constraints

To limit the impact on resources,
`ExtensiblePeerRecord`s SHOULD NOT be used to encode information
that is not essential for discovery or service initiation.
Since these records are likely to be exchanged frequently,
they should be kept as small as possible while still providing all necessary functionality.
Although specific applications MAY choose to enforce a smaller size,
it is RECOMMENDED that an absolute maximum size of `1024` bytes is enforced for valid records.
Extensible Peer Records may be included in size-constrained protocols
that further limit the size (such as DNS).

### Wrapping in Signed Peer Envelopes

Extensible Peer Records MUST be wrapped in libp2p [signed envelope](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0002-signed-envelopes.md)s
before distributing them to peers.
The corresponding `ExtensiblePeerRecord` message is serialised into the signed envelope's `payload` field.

#### Signed Envelope Domain

Extensible Peer Records MUST use `libp2p-routing-state` as domain separator string
for the envelope signature.
This is the same as for ordinary libp2p [routing records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md#signed-envelope-domain).

#### Signed Envelope Payload Type

Extensible Peer Records MUST use the UTF8 string `/libp2p/extensible-peer-record/`
as the `payload_type` value.

> **_Note:_** this will make Extensible Peer Records a subtype of the "namespace" [multicodec](https://github.com/multiformats/multicodec/blob/0c6c7d75f1580af329847dbc9900859a445ed980/table.csv).
> In future we may define a more compact multicodec type for Extensible Peer Records.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p `identify`](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/identify/README.md)
- [libp2p mix](https://rfc.vac.dev/vac/raw/mix)
- [multicodec](https://github.com/multiformats/multicodec/blob/0c6c7d75f1580af329847dbc9900859a445ed980/table.csv)
- [RFC002 Signed Envelope](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0002-signed-envelopes.md)
- [RFC003 Routing Records](https://github.com/libp2p/specs/blob/7740c076350b6636b868a9e4a411280eea34d335/RFC/0003-routing-records.md)
