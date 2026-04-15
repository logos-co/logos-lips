# CODEX-DHT

| Field | Value |
| --- | --- |
| Name | Codex Discovery |
| Slug | 75 |
| Status | raw |
| Category | Standards Track |
| Editor | Jimmy Debe <jimmy@status.im> |
| Contributors | Jimmy Debe <jimmy@status.im>, Giuliano Mega <giuliano@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/raw/dht.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/dht.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/dht.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document explains the Codex DHT (Distributed Hash Table) component. The DHT maps content IDs (CIDs) into providers of that
content.

## Background and Overview

Codex is a network of nodes, identified as providers,
participating in a decentralized peer-to-peer storage protocol.
The decentralized storage solution offers data durability guarantees,
incentive mechanisms and data persistence guarantees.

The Codex DHT is the service responsible for helping providers find other peers hosting both dataset and standalone blocks[^2] in the Codex network. It maps content IDs -- which identify blocks and datasets -- into lists of providers -- which identify and provide the information required to connect to those providers.

The Codex DHT is a modified version of
[discv5](https://github.com/ethereum/devp2p/blob/master/discv5/discv5.md), with the following differences:

1. it uses [libp2p SPRs](https://github.com/libp2p/specs/blob/master/RFC/0002-signed-envelopes.md) instead of Ethereum's [ENRs](https://eips.ethereum.org/EIPS/eip-778) to identify peers and convey connection information;
2. it extends the DHT message interface with `GET_PROVIDERS`/`ADD_PROVIDER` requests for managing provider lists;
3. it replaces [discv5 packet encoding](https://github.com/ethereum/devp2p/blob/master/discv5/discv5-wire.md#packet-encoding) with protobuf.

The Codex DHT is, indeed, closer to the [libp2p DHT](https://github.com/libp2p/specs/blob/master/kad-dht/README.md) than to discv5 in terms of what it provides. Historically, this is because the Nim version of libp2p did not implement the [Kad DHT spec](https://github.com/libp2p/specs/tree/master/kad-dht) at the time, so project builders opted to adapt the [nim-eth](https://github.com/status-im/nim-eth) Kademlia-based discv5 DHT instead.

A Codex provider will support this protocol at no extra cost other than the use of resources to store node records, and the bandwidth to serve queries and process data advertisements. As it is usually the case with DHTs, any publicly reachable node running the DHT protocol can be used as a bootstrap node into the Codex network.

## Service Interface

The two core primitives provided by the Codex DHT on top of discv5 are:

```python
def addProvider(cid: NodeId, provider: SignedPeerRecord)
def getProviders(cid: NodeId): List[SignedPeerRecord]
```

where `NodeId` is a 256-bit string, [obtained from the keccak256 hash function of the node's public key](https://github.com/ethereum/devp2p/blob/master/enr.md#v4-identity-scheme), the same used to sign peer records.

By convention, we convert from libp2p CIDs to `NodeId` by taking the keccak256 hash of the CID's contents. For reference, the Nim implementation of this conversion looks like:

```nim
proc toNodeId*(cid: Cid): NodeId =
  ## Cid to discovery id
  ##

  readUintBE[256](keccak256.digest(cid.data.buffer).data)
```

## Wire Format

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

As in discv5, all messages in the Codex DHT MUST be encoded with a `request_id`, which SHALL be serialized before the actual message data, as per the message envelope below:

```protobuf
message MessageEnvelope {
  bytes request_id = 1;    // RequestId (max 8 bytes)
  bytes message_data = 2;  // Encoded specific message
}
```

Signed peer records are simply libp2p [peer records](https://github.com/libp2p/specs/blob/master/RFC/0003-routing-records.md#address-record-format) wrapped in a [signed envelope](https://github.com/libp2p/specs/blob/master/RFC/0002-signed-envelopes.md#wire-format) and MUST be serialized according to the libp2p protobuf wire formats.

Providers MUST[^1] support the standard discv5 messages, with the following additions:

### ADD_PROVIDER request (0x0B)

```protobuf
message AddProviderMessage {
  bytes content_id = 1; // NodeId - 32 bytes, big-endian
  Envelope signed_peer_record = 2;
}
```

Registers the peer in `signed_peer_record` as a provider of the content identified by `content_id`.

### GET_PROVIDERS request (0x0C)

```protobuf
message GetProvidersMessage {
  bytes content_id = 1; // NodeId - 32 bytes, big-endian
}
```

Requests the list of providers of the content identified by `content_id`.

### PROVIDERS response (0x0D)

```protobuf
message ProvidersMessage {
  uint32 total = 1;
  repeated Envelope signed_peer_records = 2;
}
```

Returns the list of known providers of the content identified by `content_id`. `total` is currently always set to $1$.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [DiscV5 DHT](https://github.com/ethereum/devp2p/blob/master/discv5/discv5.md)
- [Ethereum Node Record](https://github.com/ethereum/devp2p/blob/master/enr.md)

[^1]: This is actually stronger than necessary, but we'll refine it over time.
[^2]: This should link to the block exchange spec once it's done.
