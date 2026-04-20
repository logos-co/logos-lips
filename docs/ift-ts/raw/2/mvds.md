# 2/MVDS

| Field | Value |
| --- | --- |
| Name | Minimum Viable Data Synchronization |
| Slug | 2 |
| Status | stable |
| Type | RFC |
| Category | Standards Track |
| Editor | Sanaz Taheri <sanaz@status.im> |
| Contributors | Dean Eigenmann <dean@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/2/mvds.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/2/mvds.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/2/mvds.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/2/mvds.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/2/mvds.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/2/mvds.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/2/mvds.md) — Fix Files for Linting (#94)
- **2024-06-28** — [`a5b24ac`](https://github.com/logos-co/logos-lips/blob/a5b24ac0a27da361312260f9da372a0e6e812212/vac/2/mvds.md) — fix_: broken image links (#81)
- **2024-02-01** — [`0253d53`](https://github.com/logos-co/logos-lips/blob/0253d534ffa9b7994cf0c6c31a5591309dc336d3/vac/2/mvds.md) — Rename MVDS.md to mvds.md
- **2024-01-30** — [`70326d1`](https://github.com/logos-co/logos-lips/blob/70326d135bf660f2ec171aeba9eacd51eaadcd6b/vac/2/MVDS.md) — Rename MVDS.md to MVDS.md
- **2024-01-27** — [`472a7fd`](https://github.com/logos-co/logos-lips/blob/472a7fd440882c195898d025c14357d875db6ff3/vac/02/MVDS.md) — Rename vac/rfcs/02/README.md to vac/02/MVDS.md
- **2024-01-25** — [`4362a7b`](https://github.com/logos-co/logos-lips/blob/4362a7b221ceb4e1f1a82536f350c8e77d8f03d4/vac/rfcs/02/README.md) — Create README.md

<!-- timeline:end -->

In this specification, we describe a minimum viable protocol for
data synchronization inspired by the Bramble Synchronization Protocol ([BSP](https://code.briarproject.org/briar/briar-spec/blob/master/protocols/BSP.md)).
This protocol is designed to ensure reliable messaging
between peers across an unreliable peer-to-peer (P2P) network where
they may be unreachable or unresponsive.

We present a reference implementation[^2]
including a simulation to demonstrate its performance.

## Definitions

| Term       | Description                                                                         |
|------------|-------------------------------------------------------------------------------------|
| **Peer**   | The other nodes that a node is connected to.                                        |
| **Record** | Defines a payload element of either the type `OFFER`, `REQUEST`, `MESSAGE` or `ACK` |
| **Node**   | Some process that is able to store data, do processing and communicate for MVDS.    |

## Wire Protocol

### Secure Transport

This specification does not define anything related to the transport of packets.
It is assumed that this is abstracted in such a way that
any secure transport protocol could be easily implemented.
Likewise, properties such as confidentiality, integrity, authenticity and
forward secrecy are assumed to be provided by a layer below.

### Payloads

Payloads are implemented using [protocol buffers v3](https://developers.google.com/protocol-buffers/).

```protobuf
syntax = "proto3";

package vac.mvds;

message Payload {
  repeated bytes acks = 5001;
  repeated bytes offers = 5002;
  repeated bytes requests = 5003;
  repeated Message messages = 5004;
}

message Message {
  bytes group_id = 6001;
  int64 timestamp = 6002;
  bytes body = 6003;
}
```

*The payload field numbers are kept more "unique" to*
*ensure no overlap with other protocol buffers.*

Each payload contains the following fields:

- **Acks:** This field contains a list (can be empty)
of `message identifiers` informing the recipient that sender holds a specific message.
- **Offers:** This field contains a list (can be empty)
of `message identifiers` that the sender would like to give to the recipient.
- **Requests:** This field contains a list (can be empty)
of `message identifiers` that the sender would like to receive from the recipient.
- **Messages:** This field contains a list of messages (can be empty).

**Message Identifiers:** Each `message` has a message identifier calculated by
hashing the `group_id`, `timestamp` and `body` fields as follows:

```js
HASH("MESSAGE_ID", group_id, timestamp, body);
```

**Group Identifiers:** Each `message` is assigned into a **group**
using the `group_id` field,
groups are independent synchronization contexts between peers.

The current `HASH` function used is `sha256`.

## Synchronization

### State

We refer to `state` as set of records for the types `OFFER`, `REQUEST` and
`MESSAGE` that every node SHOULD store per peer.
`state` MUST NOT contain `ACK` records as we do not retransmit those periodically.
The following information is stored for records:

- **Type** - Either `OFFER`, `REQUEST` or `MESSAGE`
- **Send Count** - The amount of times a record has been sent to a peer.
- **Send Epoch** - The next epoch at which a record can be sent to a peer.

### Flow

A maximum of one payload SHOULD be sent to peers per epoch,
this payload contains all `ACK`, `OFFER`, `REQUEST` and
`MESSAGE` records for the specific peer.
Payloads are created every epoch,
containing reactions to previously received records by peers or
new records being sent out by nodes.

Nodes MAY have two modes with which they can send records:
`BATCH` and `INTERACTIVE` mode.
The following rules dictate how nodes construct payloads
every epoch for any given peer for both modes.

> ***NOTE:** A node may send messages both in interactive and in batch mode.*

#### Interactive Mode

- A node initially offers a `MESSAGE` when attempting to send it to a peer.
This means an `OFFER` is added to the next payload and state for the given peer.
- When a node receives an `OFFER`, a `REQUEST` is added to the next payload and
state for the given peer.
- When a node receives a `REQUEST` for a previously sent `OFFER`,
the `OFFER` is removed from the state and
the corresponding `MESSAGE` is added to the next payload and
state for the given peer.
- When a node receives a `MESSAGE`, the `REQUEST` is removed from the state and
an `ACK` is added to the next payload for the given peer.
- When a node receives an `ACK`,
the `MESSAGE` is removed from the state for the given peer.
- All records that require retransmission are added to the payload,
given `Send Epoch` has been reached.

![notification](images/interactive.png)

Figure 1: Delivery without retransmissions in interactive mode.

#### Batch Mode

1. When a node sends a `MESSAGE`,
it is added to the next payload and the state for the given peer.
2. When a node receives a `MESSAGE`,
an `ACK` is added to the next payload for the corresponding peer.
3. When a node receives an `ACK`,
the `MESSAGE` is removed from the state for the given peer.
4. All records that require retransmission are added to the payload,
given `Send Epoch` has been reached.

<!-- diagram -->

![notification](images/batch.png)

Figure 2: Delivery without retransmissions in batch mode.

> ***NOTE:** Batch mode is higher bandwidth whereas interactive mode is higher latency.*

<!-- Interactions with state, flow chart with retransmissions? -->

### Retransmission

The record of the type `Type` SHOULD be retransmitted
every time `Send Epoch` is smaller than or equal to the current epoch.

`Send Epoch` and `Send Count` MUST be increased every time a record is retransmitted.
Although no function is defined on how to increase `Send Epoch`,
it SHOULD be exponentially increased until reaching an upper bound
where it then goes back to a lower epoch in order to
prevent a record's `Send Epoch`'s from becoming too large.

> ***NOTE:** We do not retransmission `ACK`s as we do not know when they have arrived,
therefore we simply resend them every time we receive a `MESSAGE`.*

## Formal Specification

MVDS has been formally specified using TLA+: <https://github.com/vacp2p/formalities/tree/master/MVDS>.

## Acknowledgments

- Preston van Loon
- Greg Markou
- Rene Nayman
- Jacek Sieka

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## Footnotes

[^2]: <https://github.com/vacp2p/mvds>
