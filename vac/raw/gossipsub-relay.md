---
title: GOSSIPSUB-RELAY
name: GossipSub Relay Protocol
status: raw
editor: Akshaya Mani <akshaya@status.im>
contributors: Richard Ramos <richard@status.im>, Daniel Kaiser <danielkaiser@status.im>
---

**Protocol identifier**: `/gossipsub-relay/1.0.0`

## Motivation and Goals

The Gossipsub Relay Protocol defines a minimal request/response interface
that allows external clients to inject pre-constructed GossipSub messages
into the relay logic of a full GossipSub node, without requiring mesh
participation or GossipSub protocol support.

This enables lightweight or stateless clients and anonymity systems&mdash;such as
mixnets&mdash;to send messages into the GossipSub network without joining the mesh,
maintaining long-lived streams, or managing peer scoring.

## Use Case: Mixnet Integration

A motivating use case is the Mix Protocol, where a sender anonymously routes a
message through a mix network composed of participating libp2p nodes. The final
hop on the mix network (*i.e.,* the exit node) forwards the message to the
Gossipsub Relay Protocol at the destination node.

The Relay handler receives the message as a raw byte stream and passes it to
the handler of the local Gossipsub instance, which then processes and
disseminates the message as if it arrived from a regular mesh peer.

This design cleanly separates the anonymous routing layer, offered by Mix,
from the GossipSub relay logic.

## Protocol Overview

`/gossipsub-relay/1.0.0` is a unary request/response protocol where:

- The client sends a single request containing a serialized `RPC` protobuf
  message, as defined by the
  [Gossipsub specification](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub).
- The server passes this byte sequence directly the handler of the local
  GossipSub instance, without attempting to parse or interpret it.
- The server responds with a simple acknowledgment&mdash;`success` or `error`&mdash;
  and closes the stream.

The server node MUST run both the GossipSub and GossipSub Relay protocols. The
Relay Protocol is agnostic to the structure of the payload. It serves only as
an interface between the client and the local GossipSub logic.

Unlike `Waku Lightpush`, this protocol **does not** trigger a publish
operation directly. Instead, it defers all processing and relaying to the
local Gossipsub instance.

## Protobuf

The relay protocol uses a simple wrapper message for binary payload injection:

```protobuf
  syntax = "proto3";

  message Request {
    // Opaque byte sequence representing a serialized GossipSub RPC message.
    bytes data = 1;
  }

  message Response {
    // Indicates success or failure of message injection
    bool is_success = 1;

    // Optional error or status message
    string info = 2;
  }
```

## Protocol Requirements

libp2p nodes implementing `/gossipsub-relay/1.0.0` MUST:

- Run a full local GossipSub instance.
- Accept incoming streams using `/gossipsub-relay/1.0.0`.
- On receiving a `Request`, treat the data field as an opaque byte sequence.
- Invoke the local GossipSub handler with the `data`. The local GossipSub
  instance then validates and relays the `data` as if it was received from a
  mesh peer.
- Respond with a `Response` indicating whether the injection succeeded.

Clients may open a new stream for subsequent requests.

The relay protocol itself MUST NOT inspect or parse the payload. The local
GossipSub handler is responsible for parsing the received bytes and validating
that it conforms to a valid `RPC` message as defined by the Gossipsub spec.

## Security Considerations

This protocol enables arbitrary clients to inject raw payloads into the local
GossipSub handler without performing origin authentication or message
integrity checks.

Implementers SHOULD take steps to mitigate abuse, such as:

- Enforce per-IP or per-peer rate limits.
- Reject oversized payloads.

The relay node itself SHOULD remain stateless with respect to injected
messages.

## Compatibility

This protocol is transport-agnostic and can be mounted alongside other
Gossipsub-compatible protocols. It does not require any changes to the core
Gossipsub specification.

To receive messages via this protocol, a node MUST also mount the GossipSub protocol.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p Gossipsub specification](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub)
