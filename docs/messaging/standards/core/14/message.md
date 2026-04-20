# 14/WAKU2-MESSAGE

| Field | Value |
| --- | --- |
| Name | Waku v2 Message |
| Slug | 14 |
| Status | stable |
| Type | RFC |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Sanaz Taheri <sanaz@status.im>, Aaryamann Challani <p1ge0nh8er@proton.me>, Lorenzo Delgado <lorenzo@status.im>, Abhimanyu Rawat <abhi@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-01-30** — [`d5a9240`](https://github.com/logos-co/logos-lips/blob/d5a9240c6c6c859eddd30742b2251f8a13480cf9/docs/messaging/standards/core/14/message.md) — chore: removed archived (#283)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/14/message.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/14/message.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/14/message.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/14/message.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/14/message.md) — ci: add mdBook configuration (#233)
- **2025-04-09** — [`8052808`](https://github.com/logos-co/logos-lips/blob/805280880a1c68b002c23b0bfbcded86eabe68ba/waku/standards/core/14/message.md) — 14/WAKU2-MESSAGE: Move to Stable (#120)
- **2024-11-20** — [`ff87c84`](https://github.com/logos-co/logos-lips/blob/ff87c84dc71d4f933bab188993914069fea12baa/waku/standards/core/14/message.md) — Update Waku Links (#104)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/14/message.md) — Fix Files for Linting (#94)
- **2024-08-05** — [`eb25cd0`](https://github.com/logos-co/logos-lips/blob/eb25cd06d679e94409072a96841de16a6b3910d5/waku/standards/core/14/message.md) — chore: replace email addresses (#86)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/core/14/message.md) — Broken Links + Change Editors (#26)
- **2024-02-01** — [`8e70159`](https://github.com/logos-co/logos-lips/blob/8e70159669b48c37e6934a5d24dbbc600fafde87/waku/standards/core/14/message.md) — Update and rename MESSAGE.md to message.md
- **2024-01-27** — [`88df5d8`](https://github.com/logos-co/logos-lips/blob/88df5d8a40101301c529799fefee6949732766a4/waku/standards/core/14/MESSAGE.md) — Rename README.md to MESSAGE.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/14/README.md) — remove rfs folder
- **2024-01-25** — [`9cd48a8`](https://github.com/logos-co/logos-lips/blob/9cd48a881189dcba3a7681a618731e40a2d38bcc/waku/rfcs/standards/core/14/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

[10/WAKU2](/messaging/standards/core/10/waku2.md) is a family of modular peer-to-peer protocols
for secure communication.
These protocols are designed to be secure, privacy-preserving,
and censorship-resistant and can run in resource-restricted environments.
At a high level,
[10/WAKU2](/messaging/standards/core/10/waku2.md) implements a publish/subscribe messaging pattern over libp2p and
adds capabilities.

The present document specifies the [10/WAKU2](/messaging/standards/core/10/waku2.md) message format.
A way to encapsulate the messages sent with specific information security goals,
and Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) backward compatibility.

## Motivation

When sending messages over Waku, there are multiple requirements:

- One may have a separate encryption layer as part of the application.
- One may want to provide efficient routing for resource-restricted devices.
- One may want to provide compatibility with [6/WAKU1](/messaging/standards/legacy/6/waku1.md) envelopes.
- One may want encrypted payloads by default.
- One may want to provide unlinkability to get metadata protection.

This specification attempts to provide for these various requirements.

## Semantics

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Waku Message

A `WakuMessage` is constituted by the combination of data payload and
attributes that, for example, a *publisher* sends to a *topic* and
is eventually delivered to *subscribers*.

The `WakuMessage` attributes are key-value pairs of metadata associated with a message.
The message data payload is the part of the transmitted `WakuMessage`
that is the actual message information.
The data payload is also treated as a `WakuMessage` attribute for convenience.

### Message Attributes

- The `payload` attribute MUST contain the message data payload to be sent.

- The `content_topic` attribute MUST specify a string identifier
that can be used for content-based filtering,
as described in [23/WAKU2-TOPICS](/messaging/informational/23/topics.md).

- The `meta` attribute, if present,
contains an arbitrary application-specific variable-length byte array
with a maximum length limit of 64 bytes.
This attribute can be utilized to convey supplementary details
to various [10/WAKU2](/messaging/standards/core/10/waku2.md) protocols,
thereby enabling customized processing based on its contents.

- The `version` attribute, if present,
contains a version number to discriminate different types of payload encryption.
If omitted, the value SHOULD be interpreted as version 0.

- The `timestamp` attribute, if present,
signifies the time at which the message was generated by its sender.
This attribute MAY contain the Unix epoch time in nanoseconds.
If the attribute is omitted, it SHOULD be interpreted as timestamp 0.

- The `rate_limit_proof` attribute, if present,
contains a rate limit proof encoded as per [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md).

- The `ephemeral` attribute, if present, signifies the transient nature of the message.
For example, an ephemeral message SHOULD not be persisted by other nodes on the same network.
If this attribute is set to `true`, the message SHOULD be interpreted as ephemeral.
If, instead, the attribute is omitted or set to `false`,
the message SHOULD be interpreted as non-ephemeral.

## Wire Format

The `WakuMessage` wire format is specified using [protocol buffers v3](https://developers.google.com/protocol-buffers/).

```protobuf
syntax = "proto3";

message WakuMessage {
  bytes payload = 1;
  string content_topic = 2;
  optional uint32 version = 3;
  optional sint64 timestamp = 10;
  optional bytes meta = 11;
  optional bytes rate_limit_proof = 21;
  optional bool ephemeral = 31;
}
```

An example proto file following this specification can be found [here (vacp2p/waku)](https://github.com/vacp2p/waku/blob/main/waku/message/v1/message.proto).

## Payload encryption

The `WakuMessage` payload MAY be encrypted.
The message `version` attribute indicates
the schema used to encrypt the payload data.

- **Version 0:**
  The payload SHOULD be interpreted as unencrypted; additionally,
  it CAN indicate that the message payload has been encrypted
  at the application layer.

- **Version 1:**
The payload SHOULD be encrypted using [6/WAKU1](/messaging/standards/legacy/6/waku1.md) payload encryption specified in [26/WAKU-PAYLOAD](/messaging/standards/application/26/payload.md).
This provides asymmetric and symmetric encryption.
The key agreement is performed out of band.
And provides an encrypted signature and padding for some form of unlinkability.

- **Version 2:**
The payload SHOULD be encoded according to [WAKU2-NOISE](https://github.com/waku-org/specs/blob/master/standards/application/noise.md).
The Waku Noise protocol provides symmetric encryption and asymmetric key exchange.

Any `version` value not included in this list is reserved for future specification.
And, in this case, the payload SHOULD be interpreted as unencrypted by the Waku layer.

## Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) envelope compatibility

Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) envelopes are compatible with Waku messages format.

- Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) `topic` field
SHOULD be mapped to Waku message's `content_topic` attribute.
- Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) `data` field SHOULD be mapped to Waku message's `payload` attribute.

[10/WAKU2](/messaging/standards/core/10/waku2.md) implements a publish/subscribe messaging pattern over libp2p.
This makes some Whisper/[6/WAKU1](/messaging/standards/legacy/6/waku1.md) envelope fields redundant
(e.g., `expiry`, `ttl`, `topic`, etc.), so they can be ignored.

## Deterministic message hashing

In Protocol Buffers v3,
the deterministic serialization is not canonical across the different implementations
and languages.
It is also unstable across different builds with schema changes due to unknown fields.

To overcome this interoperability limitation,
a [10/WAKU2](/messaging/standards/core/10/waku2.md) message's hash MUST be computed following this schema:

```js
message_hash = sha256(concat(pubsub_topic, message.payload, message.content_topic, message.meta, message.timestamp))
```

If an optional attribute, such as `meta`, is absent,
the concatenation of attributes SHOULD exclude it.
This recommendation is made to ensure that the concatenation process proceeds smoothly
when certain attributes are missing and to maintain backward compatibility.

This hashing schema is deemed appropriate for use cases
where a cross-implementation deterministic hash is needed,
such as message deduplication and integrity validation.
The collision probability offered by this hashing schema can be considered negligible.
This is due to the deterministic concatenation order of the message attributes,
coupled with using a SHA-2 (256-bit) hashing algorithm.

### Test vectors

The `WakuMessage` hash computation (`meta` size of 12 bytes):

```js
pubsub_topic = "/waku/2/default-waku/proto" (0x2f77616b752f322f64656661756c742d77616b752f70726f746f)
message.payload = 0x010203045445535405060708
message.content_topic = "/waku/2/default-content/proto" (0x2f77616b752f322f64656661756c742d636f6e74656e742f70726f746f)
message.meta = 0x73757065722d736563726574
message.timestamp = 0x175789bfa23f8400

message_hash = 0x64cce733fed134e83da02b02c6f689814872b1a0ac97ea56b76095c3c72bfe05
```

The `WakuMessage` hash computation (`meta` size of 64 bytes):

```js
pubsub_topic = "/waku/2/default-waku/proto" (0x2f77616b752f322f64656661756c742d77616b752f70726f746f)
message.payload = 0x010203045445535405060708
message.content_topic = "/waku/2/default-content/proto" (0x2f77616b752f322f64656661756c742d636f6e74656e742f70726f746f)
message.meta = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f
message.timestamp = 0x175789bfa23f8400

message_hash = 0x7158b6498753313368b9af8f6e0a0a05104f68f972981da42a43bc53fb0c1b27
```

The `WakuMessage` hash computation (`meta` attribute not present):

```js
pubsub_topic = "/waku/2/default-waku/proto" (0x2f77616b752f322f64656661756c742d77616b752f70726f746f)
message.payload = 0x010203045445535405060708
message.content_topic = "/waku/2/default-content/proto" (0x2f77616b752f322f64656661756c742d636f6e74656e742f70726f746f)
message.meta = <not-present>
message.timestamp = 0x175789bfa23f8400

message_hash = 0xa2554498b31f5bcdfcbf7fa58ad1c2d45f0254f3f8110a85588ec3cf10720fd8
```

The `WakuMessage` hash computation (`payload` length 0):

```js
pubsub_topic = "/waku/2/default-waku/proto" (0x2f77616b752f322f64656661756c742d77616b752f70726f746f)
message.payload = []
message.content_topic = "/waku/2/default-content/proto" (0x2f77616b752f322f64656661756c742d636f6e74656e742f70726f746f)
message.meta = 0x73757065722d736563726574
message.timestamp = 0x175789bfa23f8400

message_hash = 0x483ea950cb63f9b9d6926b262bb36194d3f40a0463ce8446228350bd44e96de4
```

## Security Considerations

### Confidentiality, integrity, and authenticity

The level of confidentiality, integrity, and
authenticity of the `WakuMessage` payload is discretionary.
Accordingly, the application layer shall utilize the encryption and
signature schemes supported by [10/WAKU2](/messaging/standards/core/10/waku2.md),
to meet the application-specific privacy needs.

### Reliability of the `timestamp` attribute

The message `timestamp` attribute is set by the sender.
Therefore, because message timestamps aren’t independently verified,
this attribute is prone to exploitation and misuse.
It should not solely be relied upon for operations such as message ordering.
For example, a malicious actor can arbitrarily set the `timestamp` of a `WakuMessage`
to a high value so that it always shows up as the most recent message
in a chat application.
Applications using [10/WAKU2](/messaging/standards/core/10/waku2.md) messages’ `timestamp` attribute
are RECOMMENDED to use additional methods for more robust message ordering.
An example of how to deal with message ordering against adversarial message timestamps
can be found in the Status protocol,
see [62/STATUS-PAYLOADS](https://github.com/status-im/status-specs/tree/master/specs/status/62/payloads.md#clock-vs-timestamp-and-message-ordering).

### Reliability of the `ephemeral` attribute

The message `ephemeral` attribute is set by the sender.
Since there is currently no incentive mechanism
for network participants to behave correctly,
this attribute is inherently insecure.
A malicious actor can tamper with the value of a Waku message’s `ephemeral` attribute,
and the receiver would not be able to verify the integrity of the message.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [10/WAKU2](/messaging/standards/core/10/waku2.md)
- [6/WAKU1](/messaging/standards/legacy/6/waku1.md)
- [23/WAKU2-TOPICS](/messaging/informational/23/topics.md)
- [17/WAKU2-RLN-RELAY](/messaging/standards/core/17/rln-relay.md)
- [64/WAKU2-NETWORK](/messaging/standards/core/64/network.md)
- [protocol buffers v3](https://developers.google.com/protocol-buffers/)
- [26/WAKU-PAYLOAD](/messaging/standards/application/26/payload.md)
- [WAKU2-NOISE](https://github.com/waku-org/specs/blob/master/standards/application/noise.md)
- [62/STATUS-PAYLOADS](https://github.com/status-im/status-specs/tree/master/specs/status/62/payloads.md#clock-vs-timestamp-and-message-ordering)
