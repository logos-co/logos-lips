# P2P-NETWORK

| Field | Value |
| --- | --- |
| Name | P2P Network |
| Slug | 135 |
| Status | draft |
| Type | RFC |
| Category | networking |
| Editor | Daniel Sanchez-Quiros <danielsq@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/draft/p2p-network.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/draft/p2p-network.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-05-11** — [`1ac7689`](https://github.com/logos-co/logos-lips/blob/1ac7689ee3fe1665d5d5d1bf9c180ed951cc660d/docs/blockchain/draft/p2p-network.md) — chore: split ift ts specs (#334)
- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/blockchain/raw/p2p-network.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/p2p-network.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/p2p-network.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/nomos/raw/p2p-network.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/nomos/raw/p2p-network.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/nomos/raw/p2p-network.md) — ci: add mdBook configuration (#233)
- **2025-09-25** — [`a3a5b91`](https://github.com/logos-co/logos-lips/blob/a3a5b91df3e06bb9ad737056ccd2c2f1fd20af3c/nomos/raw/p2p-network.md) — Created nomos/raw/p2p-network.md file (#169)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-01-20 |
| 1.0.1 | Rename Nomos to Logos Blockchain | 2026-04-17 |
| 1.1.0 | Added the Transport Security section: TLS 1.3, cipher suites, peer authentication, and the hybrid post-quantum key exchange `X25519MLKEM768`. | 2026-08-28 |

# Introduction

The Logos Blockchain peer-to-peer (P2P) network serves as the comprehensive communication layer connecting Logos Blockchain nodes. Its primary functions include facilitating the mempool for transaction dissemination and enabling block propagation. This specification leverages established, publicly available protocols to ensure robust performance. The Logos Blockchain P2P network is designed to scale according to the project's requirements, supporting efficient communication with low bandwidth and minimal latency.

Participants, or peers, operating Logos Blockchain nodes encompass a diverse array of machine specifications, ranging from laptops to dedicated servers,  as well as various operating systems and geographic locations. A key priority is to streamline communication for non-technical users, ensuring accessibility. This entails enabling peers to remain reachable—ideally even with limited connectivity or when situated behind a router—thereby enhancing inclusivity and usability across the network.

# Overview

The Logos Blockchain network constitutes a foundational element of the communication infrastructure, addressing several critical challenges:

- **Peer Connectivity**: Establishing mechanisms for peers to join and connect to the network.
- **Peer Discovery**: Enabling peers to locate and identify other participants within the network.
- **Message Transmission**: Facilitating the efficient exchange of messages among peers across the network.

The Logos Blockchain network uses production-tested protocols to ensure all of the above is achieved.

# Network Protocols Details

## Transport

The Logos Blockchain network extensively leverages the [libp2p](https://docs.libp2p.io/) suite of plug-and-play protocols, which forms a foundational component for delivering the essential functionalities outlined previously.

At its core, the Logos Blockchain network employs the [*QUIC*](https://docs.libp2p.io/concepts/transports/quic/) transport protocol. QUIC provides rapid connection establishment and offers several advantages, including enhanced NAT traversal capabilities stemming from its UDP foundation. Additionally, its default multiplexing feature simplifies configuration processes.

## Transport Security

This section states the canonical TLS configuration of the stack: the TLS
version, the peer authentication model, and the key exchange. It applies to
every libp2p connection a node establishes, regardless of the protocol carried
over it.

The key words **MUST**, **MUST NOT**, **SHOULD** and **MAY** in this section
are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Handshake

The QUIC handshake is TLS 1.3
([RFC 9001](https://www.rfc-editor.org/rfc/rfc9001)).

Nodes **MUST** use TLS 1.3. Earlier TLS versions **MUST NOT** be offered or
accepted.

Nodes **MUST** support the TLS 1.3 AEAD cipher suites:

- `TLS_CHACHA20_POLY1305_SHA256`
- `TLS_AES_256_GCM_SHA384`
- `TLS_AES_128_GCM_SHA256`

### Peer Authentication

Peers authenticate as specified by the
[libp2p TLS handshake](https://github.com/libp2p/specs/blob/master/tls/tls.md).
Each peer presents a self-signed certificate carrying its identity public key
in the libp2p Public Key Extension (OID `1.3.6.1.4.1.53594.1.1`). The identity
key signs the concatenation of the string `libp2p-tls-handshake:` and the
public key of the certificate, which proves possession of the identity key at
the time the certificate was signed.

The node identity key is **Ed25519**. It is the same key that the
[Service Declaration Protocol](../raw/bedrock-service-declaration-protocol.md)
declares as `provider_id`, which is what allows a node to verify that the peer
it has connected to is the peer whose declaration it holds.

The certificate's own key pair is unrelated to the identity key and carries no
protocol meaning beyond the binding above. Its algorithm is deliberately not
specified: it is an implementation choice with no protocol consequence, and
constraining it would create an interoperability requirement without a
corresponding benefit.

### Key Exchange

Nodes **MUST** offer the hybrid key exchange group `X25519MLKEM768`
([draft-ietf-tls-ecdhe-mlkem](https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/),
IANA named group `0x11EC`), and **MUST** offer it as the most-preferred group.

Nodes **MUST** continue to offer `X25519`, so that peers which do not yet
support the hybrid group remain reachable.

`X25519MLKEM768` combines an X25519 key exchange with an ML-KEM-768
encapsulation ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) and
derives the shared secret from both. The result is secure unless **both**
components are broken: a classical adversary is defeated by X25519, and an
adversary with a quantum computer by ML-KEM-768.

Requiring the hybrid group to be *preferred* rather than merely *offered* is
deliberate. A node that offers the group but prefers the classical one would
negotiate away the property this requirement exists to provide, and would do
so silently.

Key exchange material is **ephemeral per handshake**. It **MUST NOT** be
persisted, reused across connections, or transmitted in any protocol message
outside the handshake.

No new wire structure is introduced: the key exchange group is negotiated in
the TLS `supported_groups` extension and carried in `key_share`, as specified
by [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446); the hybrid group's
codepoint and share encoding are specified by
[draft-ietf-tls-ecdhe-mlkem](https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/).

| Group | IANA codepoint | Client share | Server share |
| --- | --- | --- | --- |
| `X25519MLKEM768` | `0x11EC` | 1216 B | 1120 B |
| `X25519` | `0x001D` | 32 B | 32 B |

### Post-Quantum Scope

The hybrid requirement is the first phase of the post-quantum transition. It
addresses harvest-now-decrypt-later: an adversary who records network traffic
today can decrypt it once a cryptographically-relevant quantum computer
exists, so the exposure is already accruing and is only realised later. The
sharpest consumer of this property is the
[Blend Protocol](../raw/blend-protocol.md#connection-details), whose privacy
guarantees would otherwise be retroactively degraded by recorded traffic
becoming decryptable.

This phase changes the key exchange and nothing else. In particular, the
following are unchanged by it:

| | changed by this phase |
| --- | --- |
| node identity signature (`provider_id`, Ed25519) | no |
| certificate signature | no |
| `declaration_id`, locators, declaration size | no |
| Service Declaration Protocol messages | no |
| service reward distribution | no |
| record-layer AEAD | no |

The key exchange is ephemeral and never leaves the handshake, so no value
declared on-chain and no value derived from one is affected.

Authentication is deliberately deferred, not overlooked: a signature cannot be
forged retroactively, so an adversary who breaks Ed25519 in the future cannot
impersonate a peer in a handshake that has already completed. Migrating the
node identity to a post-quantum signature is the subject of a later phase.

Because `X25519` is retained for interoperability, a handshake between a
conforming node and a non-conforming peer agrees on the classical group. This
is intentional and is what allows the network to migrate without a coordinated
upgrade, but it means the property is obtained per-connection, in proportion
to adoption. An active adversary cannot force a downgrade beyond what the peer
already supports: the group is negotiated inside the handshake, and the
negotiation is covered by the transcript.

The hybrid key exchange increases the size of the handshake. On QUIC this is
not amplification-relevant: a server may not send more than three times what
it has received before validating the peer's address, and the larger client
flight raises that allowance rather than consuming it.

## Peer Discovery

Following an evaluation of existing protocols and network requirements, the optimal approach for the Logos Blockchain is to leverage the established libp2p stack, incorporating libp2p-kad for peer discovery. This provides a robust, modular, and scalable solution that seamlessly integrates with other libp2p protocols (e.g., gossipsub, identify, ping), enabling support for large-scale, dynamic networks with eventual consistency and resilience.

The Logos Blockchain P2P network integrates a combination of libp2p's [Kademlia](https://docs.libp2p.io/concepts/discovery-routing/kaddht/) and [Identify](https://github.com/libp2p/specs/blob/master/identify/README.md) protocols to facilitate peer discovery. Kademlia enables the identification and connection to new peers by employing proximity-based heuristics, optimizing the discovery process. Complementing this, the Identify protocol supports the exchange of peer information, including details about the protocols each peer supports, thereby enhancing interoperability and network coordination.

The specific protocols to be negotiated are:

- Kademlia: `/logos-blockchain/kad/{version}` for main network and `/logos-blockchain-testnet/kad/{version}` for public testnet.
- Identify: `/logos-blockchain/identify/{version}` and `/logos-blockchain-testnet/identify/{version}` for public testnet.

Current versions are `1.0.0`.

The Logos Blockchain team acknowledges that the current Kademlia DHT implementation is only optimal for the V1 solution, as it is a heavier protocol for the limited utility the Logos Blockchain actually requires. However, it remains a viable interim approach. An ideal protocol would feature:

- A lightweight design, excluding the DHT which is of no use for the Logos Blockchain network.
- Lightweight and highly-scalable eventual consistency for network membership, supporting +10k nodes (ideally unbounded in practice).

This will be worked on in the future.

## NAT Traversal

Network Address Translation (NAT) poses a common challenge in peer-to-peer networks. The Logos Blockchain network prioritizes seamless, configuration-free connections among peers to accommodate participants with varying levels of technical expertise, ranging from none to advanced. Simplicity is a critical objective, given the goal of enabling nodes to operate on standard hardware, such as laptops.

To achieve this, the Logos Blockchain employs a tailored set of solutions adapted to the user's specific configuration. Comprehensive details are provided in the NAT Solution Specification.

[P2P Nat Solution](../raw/p2p-nat-solution.md)

## Gossiping

The Logos Blockchain leverages [`gossipsub`](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub) for its messaging capabilities. This works in combination with the above exposed [peer discovery protocol](p2p-network.md#peer-discovery) and [NAT traversal solution](p2p-network.md#nat-traversal) as they are members of the same libp2p stack. It automatically leverages `kademlia` connections to keep an updated list of available peers in the network.

Logos Blockchain gossiping uses two major topics. One dedicated to *mempool* and one for *block dissemination*:

- Mempool: `/logos-blockchain/mempool/{version}` for mainnet. `/logos-blockchain-testnet/mempool/{version}` for testnet. Current version is `1.0.0`.
- Blocks: `/logos-blockchain/cryptarchia/{version}` for mainnet. `/logos-blockchain-testnet/cryptarchia/{version}`for testnet. Current version is `1.0.0`.

  gossipsub is openly customizable but it is encouraged to have a peering degree of at least 8 peers.

## Bootstrapping

The Logos Blockchain P2P network is engineered for simplicity and ease of use. Upon initial connection, nodes in the network connect to publicly designated nodes to acquire the essential information required to become fully operational. Further details regarding this process are elaborated in the bootstrapping specification.

[P2P Network Bootstrapping](../raw/p2p-network-bootstrapping.md)

## Message Encoding

Messages that goes through wire follow a specific encoding scheme defined in the following specification.

[Network Wire Format](../raw/network-wire-format.md)
