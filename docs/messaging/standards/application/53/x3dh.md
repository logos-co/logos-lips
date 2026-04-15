# 53/WAKU2-X3DH

| Field | Value |
| --- | --- |
| Name | X3DH usage for Waku payload encryption |
| Slug | 53 |
| Status | draft |
| Category | Standards Track |
| Editor | Aaryamann Challani <p1ge0nh8er@proton.me> |
| Contributors | Andrea Piana <andreap@status.im>, Pedro Pombeiro <pedro@status.im>, Corey Petty <corey@status.im>, Oskar Thorén <oskarth@titanproxy.com>, Dean Eigenmann <dean@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/application/53/x3dh.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/application/53/x3dh.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/application/53/x3dh.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/application/53/x3dh.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/application/53/x3dh.md) — ci: add mdBook configuration (#233)
- **2025-07-01** — [`b60abdb`](https://github.com/logos-co/logos-lips/blob/b60abdb2fff9b4e70d862eb2550b5225b417a311/waku/standards/application/53/x3dh.md) — update waku/standards/application/53/x3dh.md (#150)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/application/53/x3dh.md) — Fix Files for Linting (#94)
- **2024-08-05** — [`eb25cd0`](https://github.com/logos-co/logos-lips/blob/eb25cd06d679e94409072a96841de16a6b3910d5/waku/standards/application/53/x3dh.md) — chore: replace email addresses (#86)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/application/53/x3dh.md) — Broken Links + Change Editors (#26)
- **2024-02-01** — [`51567b1`](https://github.com/logos-co/logos-lips/blob/51567b183115c0300c9760a104fceac7e9329475/waku/standards/application/53/x3dh.md) — Rename X3DH.md to x3dh.md
- **2024-01-31** — [`9fd3266`](https://github.com/logos-co/logos-lips/blob/9fd32660a085cc8b0a8fb16affd834f031c4c7c7/waku/standards/application/53/X3DH.md) — Update and rename README.md to X3DH.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/application/53/README.md) — remove rfs folder
- **2024-01-25** — [`5e95a1a`](https://github.com/logos-co/logos-lips/blob/5e95a1af46b2261b550e99f9b6e79dc5fa56b69e/waku/rfcs/standards/application/53/README.md) — Rename README.md to README.md
- **2024-01-25** — [`555eb20`](https://github.com/logos-co/logos-lips/blob/555eb2093afb06c2e39b29951606dc14a9dd6448/waku/rfcs/standards/application/53-X3DH/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

This document describes a method that can be used to provide a secure channel
between two peers, and thus provide confidentiality, integrity,
authenticity and forward secrecy.
It is transport-agnostic and works over asynchronous networks.

It builds on the [X3DH](https://signal.org/docs/specifications/x3dh/)
and [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/) specifications,
with some adaptations to operate in a decentralized environment.

## Motivation

Nodes on a network may want to communicate with each other in a secure manner,
without other nodes network being able to read their messages.

## Specification

### Definitions

- **Perfect Forward Secrecy** is a feature of specific key-agreement protocols
which provide assurances that session keys will not be compromised
even if the private keys of the participants are compromised.
Specifically, past messages cannot be decrypted by a third-party
who manages to obtain those private key.

- **Secret channel** describes a communication channel
where a Double Ratchet algorithm is in use.

### Design Requirements

- **Confidentiality**:
The adversary should not be able to learn what data is being exchanged
between two Status clients.
- **Authenticity**:
The adversary should not be able to cause either endpoint
to accept data from any third party as though it came from the other endpoint.
- **Forward Secrecy**:
The adversary should not be able to learn what data was exchanged
between two clients if, at some later time,
the adversary compromises one or both of the endpoints.
- **Integrity**:
The adversary should not be able to cause either endpoint
to accept data that has been tampered with.

All of these properties are ensured by the use of [Signal's Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)

### Conventions

Types used in this specification are defined using the
[Protobuf](https://developers.google.com/protocol-buffers/) wire format.

### End-to-End Encryption

End-to-end encryption (E2EE) takes place between two clients.
The main cryptographic protocol is a Double Ratchet protocol,
which is derived from the
[Off-the-Record protocol](https://otr.cypherpunks.ca/Protocol-v3-4.1.1.html),
using a different ratchet.
[The Waku v2 protocol](/messaging/standards/core/10/waku2.md)
subsequently encrypts the message payload, using symmetric key encryption.
Furthermore, the concept of prekeys
(through the use of [X3DH](https://signal.org/docs/specifications/x3dh/))
is used to allow the protocol to operate in an asynchronous environment.
It is not necessary for two parties to be online at the same time
to initiate an encrypted conversation.

### Cryptographic Protocols

This protocol uses the following cryptographic primitives:

- X3DH
  - Elliptic curve Diffie-Hellman key exchange (secp256k1)
  - KECCAK-256
  - ECDSA
  - ECIES
- Double Ratchet
  - HMAC-SHA-256 as MAC
  - Elliptic curve Diffie-Hellman key exchange (Curve25519)
  - AES-256-CTR with HMAC-SHA-256 and IV derived alongside an encryption key

    The node achieves key derivation using [HKDF](https://www.rfc-editor.org/rfc/rfc5869).

### Pre-keys

Every client SHOULD initially generate some key material which is stored locally:

- Identity keypair based on secp256k1 - `IK`
- A signed prekey based on secp256k1 - `SPK`
- A prekey signature - `Sig(IK, Encode(SPK))`

More details can be found in the `X3DH Prekey bundle creation` section of [2/ACCOUNT](https://specs.status.im/spec/2#x3dh-prekey-bundles).

Prekey bundles MAY be extracted from any peer's messages,
or found via searching for their specific topic, `{IK}-contact-code`.

The following methods can be used to retrieve prekey bundles from a peer's messages:

- contact codes;
- public and one-to-one chats;
- QR codes;
- ENS record;
- Decentralized permanent storage (e.g. Swarm, IPFS).
- Waku

Waku SHOULD be used for retrieving prekey bundles.

Since bundles stored in QR codes or
ENS records cannot be updated to delete already used keys,
the bundle MAY be rotated every 24 hours, and distributed via Waku.

### Flow

The key exchange can be summarized as follows:

1. Initial key exchange: Two parties, Alice and Bob, exchange their prekey bundles,
and derive a shared secret.

2. Double Ratchet:
The two parties use the shared secret to derive a new encryption key
for each message they send.

3. Chain key update: The two parties update their chain keys.
The chain key is used to derive new encryption keys for future messages.

4. Message key derivation:
The two parties derive a new message key from their chain key, and
use it to encrypt a message.

#### 1. Initial key exchange flow (X3DH)

[Section 3 of the X3DH protocol](https://signal.org/docs/specifications/x3dh/#sending-the-initial-message)
describes the initial key exchange flow, with some additional context:

- The peers' identity keys `IK_A` and `IK_B` correspond to their public keys;
- Since it is not possible to guarantee that a prekey will be used only once
in a decentralized world, the one-time prekey `OPK_B` is not used in this scenario;
- Nodes SHOULD not send Bundles to a centralized server,
but instead provide them in a decentralized way as described in the [Pre-keys section](#pre-keys).

Alice retrieves Bob's prekey bundle, however it is not specific to Alice.
It contains:

([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L12))

**Wire format:**

``` protobuf
// X3DH prekey bundle
message Bundle {
  // Identity key 'IK_B'
  bytes identity = 1;
  // Signed prekey 'SPK_B' for each device, indexed by 'installation-id'
  map<string,SignedPreKey> signed_pre_keys = 2;
  // Prekey signature 'Sig(IK_B, Encode(SPK_B))'
  bytes signature = 4;
  // When the bundle was created locally
  int64 timestamp = 5;
}
```

([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L5))

``` protobuf
message SignedPreKey {
  bytes signed_pre_key = 1;
  uint32 version = 2;
}
```

The `signature` is generated by sorting `installation-id` in lexicographical order,
and concatenating the `signed-pre-key` and `version`:

`installation-id-1signed-pre-key1version1installation-id2signed-pre-key2-version-2`

#### 2. Double Ratchet

Having established the initial shared secret `SK` through X3DH,
it SHOULD be used to seed a Double Ratchet exchange between Alice and Bob.

Refer to the [Double Ratchet spec](https://signal.org/docs/specifications/doubleratchet/)
for more details.

The initial message sent by Alice to Bob is sent as a top-level `ProtocolMessage`
([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L65))
containing a map of `DirectMessageProtocol` indexed by `installation-id`
([reference wire format](https://github.com/status-im/status-go/blob/1ac9dd974415c3f6dee95145b6644aeadf02f02c/services/shhext/chat/encryption.proto#L56)):

``` protobuf
message ProtocolMessage {
  // The installation id of the sender
  string installation_id = 2;
  // A sequence of bundles
  repeated Bundle bundles = 3;
  // One to one message, encrypted, indexed by installation_id
  map<string,DirectMessageProtocol> direct_message = 101;
  // Public message, not encrypted
  bytes public_message = 102;
}
```

``` protobuf
message EncryptedMessageProtocol {
  X3DHHeader X3DH_header = 1;
  DRHeader DR_header = 2; 
  DHHeader DH_header = 101;
  // Encrypted payload
  // if a bundle is available, contains payload encrypted with the Double Ratchet algorithm;
  // otherwise, payload encrypted with output key of DH exchange (no Perfect Forward Secrecy).
  bytes payload = 3;
}
```

Where:

- `X3DH_header`: the `X3DHHeader` field in `DirectMessageProtocol` contains:

    ([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L47))

```protobuf
message X3DHHeader {
  // Alice's ephemeral key `EK_A`
  bytes key = 1;
  // Bob's bundle signed prekey
  bytes id = 4;
}
```

- `DR_header`: Double ratchet header ([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L31)).
Used when Bob's public bundle is available:

``` protobuf
message DRHeader {
  // Alice's current ratchet public key
  bytes key = 1;
  // number of the message in the sending chain
  uint32 n = 2;
  // length of the previous sending chain
  uint32 pn = 3;
  // Bob's bundle ID
  bytes id = 4;
}
```

Alice's current ratchet public key (above) is mentioned in
[DR spec section 2.2](https://signal.org/docs/specifications/doubleratchet/#symmetric-key-ratchet)

- `DH_header`: Diffie-Hellman header (used when Bob's bundle is not available):
    ([reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L42))

``` protobuf
message DHHeader {
  // Alice's compressed ephemeral public key.
  bytes key = 1;
}
```

#### 3. Chain key update

The chain key MUST be updated according to the `DR_Header`
received in the `EncryptedMessageProtocol` message,
described in [2.Double Ratchet](#2-double-ratchet).

#### 4. Message key derivation

The message key MUST be derived from a single ratchet step in the symmetric-key ratchet
as described in [Symmetric key ratchet](https://signal.org/docs/specifications/doubleratchet/#symmetric-key-ratchet)

The message key MUST be used to encrypt the next message to be sent.

## Security Considerations

1. Inherits the security considerations of [X3DH](https://signal.org/docs/specifications/x3dh/#security-considerations)
and [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/#security-considerations).

2. Inherits the security considerations of the [Waku v2 protocol](/messaging/standards/core/10/waku2.md).

3. The protocol is designed to be used in a decentralized manner, however,
it is possible to use a centralized server to serve prekey bundles.
In this case, the server is trusted.

## Privacy Considerations

1. This protocol does not provide message unlinkability.
It is possible to link messages signed by the same keypair.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [X3DH](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)
- [Signal's Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)
- [Protobuf](https://developers.google.com/protocol-buffers/)
- [Off-the-Record protocol](https://otr.cypherpunks.ca/Protocol-v3-4.1.1.html)
- [The Waku v2 protocol](/messaging/standards/core/10/waku2.md)
- [HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [2/ACCOUNT](https://specs.status.im/spec/2#x3dh-prekey-bundles)
- [reference wire format](https://github.com/status-im/status-go/blob/a904d9325e76f18f54d59efc099b63293d3dcad3/services/shhext/chat/encryption.proto#L12)
- [Symmetric key ratchet](https://signal.org/docs/specifications/doubleratchet/#symmetric-key-ratchet)
