# 54/WAKU2-X3DH-SESSIONS

| Field | Value |
| --- | --- |
| Name | Session management for Waku X3DH |
| Slug | 54 |
| Status | draft |
| Category | Standards Track |
| Editor | Aaryamann Challani <p1ge0nh8er@proton.me> |
| Contributors | Andrea Piana <andreap@status.im>, Pedro Pombeiro <pedro@status.im>, Corey Petty <corey@status.im>, Oskar Thorén <oskarth@titanproxy.com>, Dean Eigenmann <dean@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/application/54/x3dh-sessions.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/application/54/x3dh-sessions.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/application/54/x3dh-sessions.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/application/54/x3dh-sessions.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/application/54/x3dh-sessions.md) — ci: add mdBook configuration (#233)
- **2025-04-24** — [`db365cb`](https://github.com/logos-co/logos-lips/blob/db365cb756716fb76731c7988d41e9af9a850bc2/waku/standards/application/54/x3dh-sessions.md) — update waku/standards/application/54/x3dh-sessions.md (#151)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/application/54/x3dh-sessions.md) — Fix Files for Linting (#94)
- **2024-08-05** — [`eb25cd0`](https://github.com/logos-co/logos-lips/blob/eb25cd06d679e94409072a96841de16a6b3910d5/waku/standards/application/54/x3dh-sessions.md) — chore: replace email addresses (#86)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/application/54/x3dh-sessions.md) — Broken Links + Change Editors (#26)
- **2024-02-01** — [`0e490d4`](https://github.com/logos-co/logos-lips/blob/0e490d46bb99c2fbae1ac193fbdfc11d84fb080d/waku/standards/application/54/x3dh-sessions.md) — Rename X3DH-sessions.md to x3dh-sessions.md
- **2024-01-31** — [`7f8b187`](https://github.com/logos-co/logos-lips/blob/7f8b187f1b8b77af0c88c9fb154144494a7dfb7d/waku/standards/application/54/X3DH-sessions.md) — Update and rename README.md to X3DH-sessions.md
- **2024-01-27** — [`a22c2a0`](https://github.com/logos-co/logos-lips/blob/a22c2a0d79058ab435fcd38fe17a9f19021d5cd4/waku/standards/application/54/README.md) — Rename README.md to README.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/application/56/README.md) — remove rfs folder
- **2024-01-25** — [`484df92`](https://github.com/logos-co/logos-lips/blob/484df92848f90025fc538c19616fff904d72bc26/waku/rfcs/standards/application/56/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

This document specifies how to manage sessions based on an X3DH key exchange.
This includes how to establish new sessions,
how to re-establish them, how to maintain them, and how to close them.

[53/WAKU2-X3DH](/messaging/standards/application/53/x3dh.md) specifies the Waku `X3DH` protocol
for end-to-end encryption.
Once two peers complete an X3DH handshake, they SHOULD establish an X3DH session.

## Session Establishment

A node identifies a peer by their `installation-id`
which MAY be interpreted as a device identifier.

### Discovery of pre-key bundles

The node's pre-key bundle MUST be broadcast on a content topic
derived from the node's public key, so that the first message may be PFS-encrypted.
Each peer MUST publish their pre-key bundle periodically to this topic,
otherwise they risk not being able to perform key-exchanges with other peers.
Each peer MAY publish to this topic when their metadata changes,
so that the other peer can update their local record.

If peer A wants to send a message to peer B,
it MUST derive the topic from peer B's public key, which has been shared out of band.
Partitioned topics have been used to balance privacy and
efficiency of broadcasting pre-key bundles.

The number of partitions that MUST be used is 5000.

The topic MUST be derived as follows:

```js
var partitionsNum *big.Int = big.NewInt(5000)
var partition *big.Int = big.NewInt(0).Mod(peerBPublicKey, partitionsNum)

partitionTopic := "contact-discovery-" + strconv.FormatInt(partition.Int64(), 10)

var hash []byte = keccak256(partitionTopic)
var topicLen int = 4

if len(hash) < topicLen {
    topicLen = len(hash)
}

var contactCodeTopic [4]byte
for i = 0; i < topicLen; i++ {
    contactCodeTopic[i] = hash[i]
}
```

### Initialization

A node initializes a new session once a successful X3DH exchange has taken place.
Subsequent messages will use the established session until re-keying is necessary.

### Negotiated topic to be used for the session

After the peers have performed the initial key exchange,
they MUST derive a topic from their shared secret to send messages on.
To obtain this value, take the first four bytes of the keccak256 hash
of the shared secret encoded in hexadecimal format.

```js
sharedKey, err := ecies.ImportECDSA(myPrivateKey).GenerateShared(
    ecies.ImportECDSAPublic(theirPublicKey),
    16,
    16,
)

hexEncodedKey := hex.EncodeToString(sharedKey)

var hash []byte = keccak256(hexEncodedKey)
var topicLen int = 4

if len(hash) < topicLen {
    topicLen = len(hash)
}

var topic [4]byte
for i = 0; i < topicLen; i++ {
    topic[i] = hash[i]
}
```

To summarize,
following is the process for peer B to establish a session with peer A:

1. Listen to peer B's Contact Code Topic to retrieve their bundle information,
including a list of active devices
2. Peer A sends their pre-key bundle on peer B's partitioned topic
3. Peer A and peer B perform the key-exchange using the shared pre-key bundles
4. The negotiated topic is derived from the shared secret
5. Peers A & B exchange messages on the negotiated topic

### Concurrent sessions

If a node creates two sessions concurrently between two peers,
the one with the symmetric key first in byte order SHOULD be used,
this marks that the other has expired.

### Re-keying

On receiving a bundle from a given peer with a higher version,
the old bundle SHOULD be marked as expired and
a new session SHOULD be established on the next message sent.

### Multi-device support

Multi-device support is quite challenging
as there is not a central place where information on which and how many devices
(identified by their respective `installation-id`) a peer has, is stored.

Furthermore, account recovery always needs to be taken into consideration,
where a user wipes clean the whole device and
the node loses all the information about any previous sessions.
Taking these considerations into account,
the way the network propagates multi-device information using X3DH bundles,
which will contain information about paired devices
as well as information about the sending device.
This means that every time a new device is paired,
the bundle needs to be updated and propagated with the new information,
the user has the responsibility to make sure the pairing is successful.

The method is loosely based on [Signal's Sesame Algorithm](https://signal.org/docs/specifications/sesame/).

### Pairing

A new `installation-id` MUST be generated on a per-device basis.
The device should be paired as soon as possible if other devices are present.

If a bundle is received, which has the same `IK` as the keypair present on the device,
the devices MAY be paired.
Once a user enables a new device,
a new bundle MUST be generated which includes pairing information.

The bundle MUST be propagated to contacts through the usual channels.

Removal of paired devices is a manual step that needs to be applied on each device,
and consist simply in disabling the device,
at which point pairing information will not be propagated anymore.

### Sending messages to a paired group

When sending a message,
the peer SHOULD send a message to other `installation-id` that they have seen.
The node caps the number of devices to `n`, ordered by last activity.
The node sends messages using pairwise encryption, including their own devices.

Where `n` is the maximum number of devices that can be paired.

### Account recovery

Account recovery is the same as adding a new device,
and it MUST be handled the same way.

### Partitioned devices

In some cases
(i.e. account recovery when no other pairing device is available, device not paired),
it is possible that a device will receive a message
that is not targeted to its own `installation-id`.
In this case an empty message containing bundle information MUST be sent back,
which will notify the receiving end not to include the device in any further communication.

## Security Considerations

1. Inherits all security considerations from [53/WAKU2-X3DH](/messaging/standards/application/53/x3dh.md).

### Recommendations

1. The value of `n` SHOULD be configured by the app-protocol.
    - The default value SHOULD be 3,
    since a larger number of devices will result in a larger bundle size,
    which may not be desirable in a peer-to-peer network.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [53/WAKU2-X3DH](/messaging/standards/application/53/x3dh.md)
- [Signal's Sesame Algorithm](https://signal.org/docs/specifications/sesame/)
