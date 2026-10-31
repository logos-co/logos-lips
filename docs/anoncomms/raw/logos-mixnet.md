# LOGOS-MIXNET

| Field | Value |
| --- | --- |
| Name | LOGOS-MIXNET |
| Status | raw |
| Type | RFC |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | |

## Abstract

This specification describes an opinionated instantiation of the [LIBP2P-MIX](https://lip.logos.co/anoncomms/raw/mix.html) protocol suite.
This instantiation forms the Logos Mixnet, an anonymisation layer for Logos services.
A node that obeys this specification can operate as a Logos Mixnet node and interoperate with other Logos Mixnet nodes.

## Background / Rationale / Motivation

_To be defined._

## Scope

This specification defines how a node participates in the Logos Mixnet.
Within this context all nodes are considered equal participants.
In other words, for a given message, each node can be the sender, an intermediary node, or the exit node.

In practice, there may be further requirements for nodes that originate or process responses for specific applications over mix.
This falls outside the scope of this specification.
Refer to [WAKU-MIX](https://lip.logos.co/messaging/core/raw/mix.html) for an example of application integration with mix.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

This document uses the terms defined in [LIBP2P-MIX](https://lip.logos.co/anoncomms/raw/mix.html),
[Mix DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection.html), and
[Mix RLN DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection-rln.html).

## Protocol Composition

The Logos Mixnet is an overlay network of libp2p nodes that implement the [LIBP2P-MIX](https://lip.logos.co/anoncomms/raw/mix.html) protocol,
with common validation rules,
collaborative Sybil and DoS protection,
and a shared discovery layer for interconnection.

This document does not define these protocols again,
but describes their instantiation for compatibility within the Logos Mixnet.

## Base Mix Protocol

Each Logos Mixnet node MUST implement [LIBP2P-MIX](https://lip.logos.co/anoncomms/raw/mix.html),
mounting the libp2p protocol with identifier `/mix/1.0.0` ([LIBP2P-MIX §7.1](https://lip.logos.co/anoncomms/raw/mix.html#71-protocol-identifier)).
Each node SHOULD at least support sender and intermediary processing as defined in [LIBP2P-MIX §7](https://lip.logos.co/anoncomms/raw/mix.html#7-core-mix-protocol-responsibilities).
In addition, nodes MAY support destination-as-final-hop processing for specific applications (_still to be defined_).
It is possible that forward-to-destination exit processing (_still to be defined_) is supported in future.

### Path Selection and Length

The mix path length MUST be 3.
Future versions of this specification can change this value.

The sender SHOULD select each mix node in the path distinctly and
at random from the discovered pool of Logos Mixnet nodes.

## Sphinx Packet Encoding

Logos Mixnet nodes MUST use the Sphinx packet format defined in [LIBP2P-MIX §8](https://lip.logos.co/anoncomms/raw/mix.html#8-sphinx-packet-format).

### Packet and Message Size

The total packet size MUST be 4909 bytes ([LIBP2P-MIX §8.3.2](https://lip.logos.co/anoncomms/raw/mix.html#832-payload-size)).

The Sphinx header has a total of 624 bytes.
The applicable maximum Sphinx payload size is 3984 bytes,
for a total Sphinx packet size of 4608 bytes.
In addition, a 301 byte [RLN DoS protection](#dos-protection) proof is appended after the Sphinx packet,
bringing the total packet size to 4909 bytes.
The Sphinx payload contains the application message, the origin protocol codec, the payload integrity prefix, and optional SURBs.
Nodes MUST pad each payload to the maximum payload size ([LIBP2P-MIX §8.3.3](https://lip.logos.co/anoncomms/raw/mix.html#833-padding-and-fragmentation)).
Origin protocols SHOULD fragment messages that are too large for one payload before they submit them to mix.

### Cryptographic Primitives

Nodes MUST use the cryptographic primitives defined in [LIBP2P-MIX §8.2](https://lip.logos.co/anoncomms/raw/mix.html#82-cryptographic-primitives):

- Curve25519 (X25519) for the key agreement
- SHA-256 for hashes and key derivation
- AES-128-CTR for header encryption
- HMAC-SHA-256, truncated to 16 bytes, for the per-hop integrity check.

The security parameter κ MUST be 128 bits.

### Payload Encryption

Nodes MUST encrypt the Sphinx payload with LIONESS as defined in [LIONESS-PAYLOAD-ENCRYPTION-FOR-MIX](https://lip.logos.co/anoncomms/raw/mix-lioness.html).

## Exit Node Behaviour and Replies

A Logos Mixnet node MAY support operation as an exit node for destination-as-final-hop ("exit==destination") delivery.

> *_Note:_* supported delivery modes are [currently (2026-08) being revised](https://github.com/logos-co/logos-lips/pull/351).
This specification will pin the permitted delivery modes when that revision is complete.

A node identifies its exit role through node role determination ([LIBP2P-MIX §8.6.2](https://lip.logos.co/anoncomms/raw/mix.html#862-node-role-determination)).

An exit node SHOULD deliver the decrypted message to the destination.
It MUST use the origin protocol codec contained in the payload ([LIBP2P-MIX §8.6.4](https://lip.logos.co/anoncomms/raw/mix.html#864-exit-processing)).

Exit nodes MUST support SURB reply processing ([LIBP2P-MIX §8.7](https://lip.logos.co/anoncomms/raw/mix.html#87-single-use-reply-blocks)).
SURB replies let request-response origin protocols receive a response without knowledge of the sender identity.

## Discovery

Logos Mixnet nodes SHOULD use [Logos Service Discovery](https://lip.logos.co/anoncomms/raw/logos-service-discovery.html) with
[Extensible Peer Records](https://lip.logos.co/anoncomms/raw/extensible-peer-records.html) to advertise mix capability and to find other nodes in the Logos Mixnet.
Nodes MAY augment discovery with other discovery methods.

Each node MUST advertise its mix capability, its X25519 public key, and one or more reachable multiaddresses ([LIBP2P-MIX §6.1](https://lip.logos.co/anoncomms/raw/mix.html#61-discovery)).

> *_Note:_* Logos Mixnet currently (2026-08) supports only IPv4 addresses over TCP/QUIC-v1 transports.

The anonymity of the mixnet depends on the integrity of the discovered node pool.
Discovery methods that give a biased node sample, or that are open to sybil attacks, decrease the anonymity of all paths.
Nodes SHOULD NOT use such methods as their primary discovery method.

## DoS Protection

The Logos Mixnet MUST use DoS protection as defined in [Mix DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection.html).

### Architecture

Nodes MUST use the per-hop generated proof architecture ([Mix DoS Protection §4.2](https://lip.logos.co/anoncomms/raw/mix-dos-protection.html#42-per-hop-generated-proofs)).
Nodes MUST use Rate Limiting Nullifiers (RLN) as the proof mechanism, as defined in [Mix RLN DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection-rln.html).

Each node MUST have an RLN membership to send or to forward messages.
Each node in the path MUST verify the incoming RLN proof before Sphinx packet processing.
After verification, an intermediary node MUST generate a new RLN proof and attach it to the outgoing packet.
A node MUST derive the epoch for each proof it generates from its own local clock.
In particular, an intermediary node MUST NOT simply propagate the epoch of the incoming proof.
The exit node verifies the incoming proof
and does not generate a new one for the message it forwards.

### RLN Parameters

| Parameter | Value | Description |
| --- | --- | --- |
| `period` | `10` | The length of an epoch in seconds |
| messaging rate | `100` | The number of messages permitted for each membership in each epoch |
| `max_epoch_gap` | `3` | The maximum permitted gap between the epoch of a node and an incoming message |
| `acceptable_root_window_size` | 5 | The maximum number of past Merkle roots that a node keeps |
| `staked_fund` | `TBD` | The amount that a node stakes at registration |

### Membership and Slashing

_To be defined._
This section will define the registration blockchain, the membership contract, the membership criteria, and the slashing procedure.

### Coordination Layer

Intermediary nodes and exit nodes MUST participate in the coordination layer
([Mix RLN DoS Protection, Coordination Layer](https://lip.logos.co/anoncomms/raw/mix-dos-protection-rln.html#coordination-layer)).

The Logos Mixnet MUST use [RLN Relay](https://lip.logos.co/messaging/core/draft/17/rln-relay.html) for its coordination layer.
Nodes MUST send and receive messaging metadata on the content topic `TBD`,
within the Logos Delivery network defined by cluster `TBD`.

RLN Relay applies its own RLN protection
and requires a separate membership and rate-limit registration
via the Logos Delivery module.
This satisfies the requirement that the coordination layer protects itself against spam.

### Stake-Weighted Rate Limits

_To be defined._
Research on stake-weighted rate limits for the Logos Mixnet continues.
Refer to the [stake-weighted RLN proposal](https://github.com/logos-co/logos-lips/pull/327)
and the related [cover traffic extension](https://github.com/logos-co/logos-lips/pull/341).

## Cover Traffic

Nodes SHOULD implement [Mix Cover Traffic](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html).

The `strategy_type` SHOULD be `CONSTANT_RATE` ([Mix Cover Traffic §7](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html#7-recommended-strategy)).
When implementing this strategy, the `cover_rate_fraction` MUST be 0.7.

> *_Note:_* different cover traffic generation strategies are currently being investigated.

Cover loop paths MUST have length 3, equal to the mix path length.
Cover packets use the reserved codec `/mix/cover/1.0.0`.
Cover traffic shares the RLN rate limit budget with local messages and forwarded packets.
See ([Mix Cover Traffic §4](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html#4-rate-limit-budget-model)).

## Hidden Services

_To be defined._
Research on hidden services for mix continues.
Refer to the [hidden service proposal](https://github.com/logos-co/logos-lips/pull/330).

## Security/Privacy Considerations

_To be defined._
This section will collect the security considerations of the composed protocols and the considerations specific to the Logos Mixnet configuration.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [LIBP2P-MIX](https://lip.logos.co/anoncomms/raw/mix.html)
- [LIONESS-PAYLOAD-ENCRYPTION-FOR-MIX](https://lip.logos.co/anoncomms/raw/mix-lioness.html)
- [Mix DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection.html)
- [Mix RLN DoS Protection](https://lip.logos.co/anoncomms/raw/mix-dos-protection-rln.html)
- [Mix Cover Traffic](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html)
- [Logos Service Discovery](https://lip.logos.co/anoncomms/raw/logos-service-discovery.html)
- [Extensible Peer Records](https://lip.logos.co/anoncomms/raw/extensible-peer-records.html)
- [RLN-V2](https://lip.logos.co/anoncomms/raw/rln-v2.html)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
- Logos Delivery RLN Relay — _reference to be added_

### Informative

- [WAKU-MIX](https://lip.logos.co/messaging/core/raw/mix.html)
- [64/WAKU2-NETWORK](https://lip.logos.co/messaging/core/draft/64/network.html)
- [Sphinx: A Compact and Provably Secure Mix Format](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf)
- [Mix hidden service proposal (PR #330)](https://github.com/logos-co/logos-lips/pull/330)
- [Stake-weighted Mix RLN DoS protection proposal (PR #327)](https://github.com/logos-co/logos-lips/pull/327)
- [Cover traffic extension for stake-weighted RLN (PR #341)](https://github.com/logos-co/logos-lips/pull/341)
