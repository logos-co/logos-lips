# CODEX-COMMUNITY-HISTORY

| Field | Value |
| --- | --- |
| Name | Codex Community History |
| Slug | 76 |
| Status | raw |
| Category | Standards Track |
| Editor | Jimmy Debe <jimmy@status.im> |
| Contributors | Jimmy Debe <jimmy@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/storage/raw/community-history.md) — chore: add math support (#287)
- **2026-01-30** — [`d5a9240`](https://github.com/logos-co/logos-lips/blob/d5a9240c6c6c859eddd30742b2251f8a13480cf9/docs/storage/raw/community-history.md) — chore: removed archived (#283)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/storage/raw/community-history.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/storage/raw/community-history.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/storage/raw/community-history.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document describes how nodes in Status Communities archive historical message data of their communities.
Not requiring to follow the time range limit provided by [13/WAKU2-STORE](../../messaging/standards/core/13/store.md)
nodes using the [BitTorrent protocol](https://www.bittorrent.org/beps/bep_0003.html).
It also describes how the archives are distributed to community members via the [Status network](https://status.network/),
so they can fetch them and
gain access to a complete message history.

## Background

Messages are stored permanently by [13/WAKU2-STORE](../../messaging/standards/core/13/store.md) nodes for a configurable time range,
which is limited by the overall storage provided by a [13/WAKU2-STORE](../../messaging/standards/core/13/store.md) nodes.
Messages older than that period are no longer provided by [13/WAKU2-STORE](../../messaging/standards/core/13/store.md) nodes,
making it impossible for other nodes to request historical messages that go beyond that time range.
This raises issues in the case of Status communities,
where recently joined members of a community are not able to request complete message histories of the community channels.

### Terminology

| Name | Description |
| ---- | -------------- |
| Waku node | A [10/WAKU2](../../messaging/standards/core/10/waku2.md) node that implements [11/WAKU2-RELAY](../../messaging/standards/core/11/relay.md) |
| Store node | A [10/WAKU2](../../messaging/standards/core/10/waku2.md) node that implements [13/WAKU2-STORE](../../messaging/standards/core/13/store.md) |
| Waku network | A group of [10/WAKU2](../../messaging/standards/core/10/waku2.md) nodes forming a graph, connected via [11/WAKU2-RELAY](../../messaging/standards/core/11/relay.md) |
| Status user | A Status account that is used in a Status consumer product, such as Status Mobile or Status Desktop |
| Status node | A Status client run by a Status application |
| Control node| A Status node that owns the private key for a Status community |
| Community member | A Status user that is part of a Status community, not owning the private key of the community|
| Community member node | A Status node with message archive capabilities enabled, run by a community member |
| Live messages | [14/WAKU2-MESSAGE](../../messaging/standards/core/14/message.md) received through the Waku network |
| BitTorrent client | A program implementing the BitTorrent protocol |
| Torrent/Torrent file | A file containing metadata about data to be downloaded by BitTorrent clients |
| Magnet link | A link encoding the metadata provided by a torrent file (Magnet URI scheme) |

## Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Message History Archive

Message history archives are represented as `WakuMessageArchive` and
created from a [14/WAKU2-MESSAGE](../../messaging/standards/core/14/message.md) exported from the local database.
The following describes the protocol buffer for `WakuMessageArchive` :

``` protobuf

syntax = "proto3";

message WakuMessageArchiveMetadata {
  uint8 version = 1;
  uint64 from = 2;
  uint64 to = 3;
  repeated string content_Topic = 4;
}

message WakuMessageArchive {
  uint8 version = 1;
  WakuMessageArchiveMetadata metadata = 2;
  repeated WakuMessage messages = 3; // `WakuMessage` is provided by 14/WAKU2-MESSAGE
  bytes padding = 4;
}

```

The `from` field SHOULD contain a `timestamp` of the time range's lower bound.
This type parallels to the `timestamp` of a `WakuMessage`.
The `to` field SHOULD contain a `timestamp` of the time range's the higher bound.
The `contentTopic` field MUST contain a list of all community channel `contentTopic`s.
The `messages` field MUST contain all messages that belong in the archive, given its `from`,
`to`, and `contentTopic` fields.

The `padding` field MUST contain the amount of zero bytes needed for the protobuf encoded `WakuMessageArchive`.
The overall byte size MUST be a multiple of the `pieceLength` used to divide the data into pieces.
This is needed for seamless encoding and
decoding of archival data when interacting with BitTorrent,
as explained in [creating message archive torrents](#creating-message-archive-torrents).

#### Message History Archive Index

Control nodes MUST provide message archives for the entire community history.
The entire history consists of a set of `WakuMessageArchive`,
where each archive contains a subset of historical `WakuMessage` for a time range of seven days.
All the `WakuMessageArchive` are concatenated into a single file as a byte string, see [Ensuring reproducible data pieces](#ensuring-reproducible-data-pieces).

Control nodes MUST create a message history archive index,
`WakuMessageArchiveIndex` with metadata,
that allows receiving nodes to only fetch the message history archives they are interested in.

##### WakuMessageArchiveIndex

``` protobuf

syntax = "proto3"

message WakuMessageArchiveIndexMetadata {
  uint8 version = 1
  WakuMessageArchiveMetadata metadata = 2
  uint64 offset = 3
  uint64 num_pieces = 4
}

message WakuMessageArchiveIndex {
  map<string, WakuMessageArchiveIndexMetadata> archives = 1
}

```

A `WakuMessageArchiveIndex` is a map where the key is the KECCAK-256 hash of the `WakuMessageArchiveIndexMetadata`,
is derived from a 7-day archive
and the value is an instance of that `WakuMessageArchiveIndexMetadata` corresponding to that archive.

The `offset` field MUST contain the position at which the message history archive starts in the byte string
of the total message archive data.
This MUST be the sum of the length of all previously created message archives in bytes, see [creating message archive torrents](#creating-message-archive-torrents).

The control node MUST update the `WakuMessageArchiveIndex` every time it creates one or
more `WakuMessageArchive`s and bundle it into a new torrent.
For every created `WakuMessageArchive`,
there MUST be a `WakuMessageArchiveIndexMetadata` entry in the archives field `WakuMessageArchiveIndex`.

### Creating Message Archive Torrents

Control nodes MUST create a .torrent file containing metadata for all message history archives.
To create a .torrent file, and
later serve the message archive data on the BitTorrent network,
control nodes MUST store the necessary data in dedicated files on the file system.

A torrent's source folder MUST contain the following two files:

- `data`: Contains all protobuf encoded `WakuMessageArchive`'s (as bit strings)
concatenated in ascending order based on their time
- `index`: Contains the protobuf encoded `WakuMessageArchiveIndex`

Control nodes SHOULD store these files in a dedicated folder that is identifiable via a community identifier.

### Ensuring Reproducible Data Pieces

The control node MUST ensure that the byte string from the protobuf encoded data
is equal to the byte string data from the previously generated message archive torrent.
Including the data of the latest seven days worth of messages encoded as `WakuMessageArchive`.
Therefore, the size of data grows every seven days as it's append-only.

Control nodes MUST ensure that the byte size,
for every individual `WakuMessageArchive` encoded protobuf,
is a multiple of `pieceLength` using the padding field.
If the `WakuMessageArchive` is not a multiple of `pieceLength`,
its padding field MUST be filled with zero bytes and
the `WakuMessageArchive` MUST be re-encoded until its size becomes a multiple of `pieceLength`.

This is necessary because the content of the data file will be split into pieces of `pieceLength` when the torrent file is created,
and the SHA1 hash of every piece is then stored in the torrent file and
later used by other nodes to request the data for each individual data piece.

By fitting message archives into a multiple of `pieceLength` and
ensuring they fill the possible remaining space with zero bytes,
control nodes prevent the next message archive from occupying that remaining space of the last piece,
which will result in a different SHA1 hash for that piece.

Example: Without padding
Let `WakuMessageArchive` "A1" be of size 20 bytes:

``` text
 0 11 22 33 44 55 66 77 88 99
10 11 12 13 14 15 16 17 18 19
```

With a `pieceLength` of 10 bytes, A1 will fit into 20 / 10 = 2 pieces:

```text
 0 11 22 33 44 55 66 77 88 99 // piece[0] SHA1: 0x123
10 11 12 13 14 15 16 17 18 19 // piece[1] SHA1: 0x456
```

Example: With padding
Let `WakuMessageArchive` "A2" be of size 21 bytes:

```text
 0 11 22 33 44 55 66 77 88 99
10 11 12 13 14 15 16 17 18 19
20
```

With a `pieceLength` of 10 bytes,
A2 will fit into 21 / 10 = 2 pieces.

The remainder will introduce a third piece:

```text
 0 11 22 33 44 55 66 77 88 99 // piece[0] SHA1: 0x123
10 11 12 13 14 15 16 17 18 19 // piece[1] SHA1: 0x456
20                            // piece[2] SHA1: 0x789
```

The next `WakuMessageArchive` "A3" will be appended ("#3") to the existing data and
occupy the remaining space of the third data piece.

The piece at index 2 will now produce a different SHA1 hash:

```text
 0 11 22 33 44 55 66 77 88 99 // piece[0] SHA1: 0x123
10 11 12 13 14 15 16 17 18 19 // piece[1] SHA1: 0x456
20 #3 #3 #3 #3 #3 #3 #3 #3 #3 // piece[2] SHA1: 0xeef
#3 #3 #3 #3 #3 #3 #3 #3 #3 #3 // piece[3]
```

By filling up the remaining space of the third piece with A2 using its padding field,
it is guaranteed that its SHA1 will stay the same:

```text
 0 11 22 33 44 55 66 77 88 99 // piece[0] SHA1: 0x123
10 11 12 13 14 15 16 17 18 19 // piece[1] SHA1: 0x456
20  0  0  0  0  0  0  0  0  0 // piece[2] SHA1: 0x999
#3 #3 #3 #3 #3 #3 #3 #3 #3 #3 // piece[3]
#3 #3 #3 #3 #3 #3 #3 #3 #3 #3 // piece[4]
```

### Seeding Message History Archives

The control node MUST seed the generated torrent until a new `WakuMessageArchive` is created.

The control node SHOULD NOT seed torrents for older message history archives.
Only one torrent at a time SHOULD be seeded.

### Creating Magnet Links

Once a torrent file for all message archives is created,
the control node MUST derive a magnet link,
following the Magnet URI scheme using the underlying [BitTorrent protocol](https://www.bittorrent.org/beps/bep_0003.html) client.

#### Message Archive Distribution

Message archives are available via the BitTorrent network as they are being seeded by the control node.
Other community member nodes will download the message archives, from the BitTorrent network,
after receiving a magnet link that contains a message archive index.

The control node MUST send magnet links containing message archives and
the message archive index to a special community channel.
The `content_Topic` of that special channel follows the following format:

``` text

/{application-name}/{version-of-the-application}/{content-topic-name}/{encoding}
```

All messages sent with this special channel's `content_Topic` MUST be instances of `ApplicationMetadataMessage`,
with a [62/STATUS-PAYLOADS](https://github.com/status-im/status-specs/tree/master/specs/status/62/payloads.md) of `CommunityMessageArchiveIndex`.

Only the control node MAY post to the special channel.
Other messages on this specified channel MUST be ignored by clients.
Community members MUST NOT have permission to send messages to the special channel.
However, community member nodes MUST subscribe to a special channel,
to receive a [14/WAKU2-MESSAGE](../../messaging/standards/core/14/message.md) containing magnet links for message archives.

#### Canonical Message Histories

Only control nodes are allowed to distribute messages with magnet links,
via the special channel for magnet link exchange.
Status nodes MUST ignore all messages in the special channel that aren't signed by a control node.
Since the magnet links are created from the control node's database
(and previously distributed archives),
the message history provided by the control node becomes the canonical message history and
single source of truth for the community.

Community member nodes MUST replace messages in their local database with the messages extracted from archives
within the same time range.
Messages that the control node didn't receive MUST be removed and
are no longer part of the message history of interest,
even if it already existed in a community member node's database.

### Fetching Message History Archives

The process of fetching message history:

1. Receive message archive index magnet link as described in [Message archive distribution](#message-archive-distribution),
2. Download the index file from the torrent, then determine which message archives to download
3. Download individual archives

Community member nodes subscribe to the special channel of the control nodes that publish magnet links for message history archives.
Two RECOMMENDED scenarios in which community member nodes can receive such a magnet link message from the special channel:

1. The member node receives it via live messages, by listening to the special channel.
2. The member node requests messages for a time range of up to 30 days from store nodes
(this is the case when a new community member joins a community.)
3. Downloading message archives

When community member nodes receive a message with a `CommunityMessageHistoryArchive` [62/STATUS-PAYLOADS](https://github.com/status-im/status-specs/tree/master/specs/status/62/payloads.md),
they MUST extract the `magnet_uri`.
Then SHOULD pass it to their underlying BitTorrent client to fetch the latest message history archive index,
which is the index file of the torrent, see [Creating message archive torrents].

Due to the nature of distributed systems,
there's no guarantee that a received message is the "last" message.
This is especially true when community member nodes request historical messages from store nodes.
Therefore, community member nodes MUST wait for 20 seconds after receiving the last `CommunityMessageArchive`,
before they start extracting the magnet link to fetch the latest archive index.

Once a message history archive index is downloaded and
parsed back into `WakuMessageArchiveIndex`,
community member nodes use a local lookup table to determine which of the listed archives are missing,
using the KECCAK-256 hashes stored in the index.

For this lookup to work,
member nodes MUST store the KECCAK-256 hashes,
of the `WakuMessageArchiveIndexMetadata` provided by the index file,
for all of the message history archives that have been downloaded into their local database.

Given a `WakuMessageArchiveIndex`, member nodes can access individual `WakuMessageArchiveIndexMetadata` to download individual archives.

Community member nodes MUST choose one of the following options:

1. Download all archives: Request and download all data pieces for the data provided by the torrent
(this is the case for new community member nodes that haven't downloaded any archives yet.)
2. Download only the latest archive: Request and
download all pieces starting at the offset of the latest `WakuMessageArchiveIndexMetadata`
(this is the case for any member node that already has downloaded all previous history and
is now interested in only the latest archive).
3. Download specific archives: Look into from and
to fields of every `WakuMessageArchiveIndexMetadata` and
determine the pieces for archives of a specific time range
(can be the case for member nodes that have recently joined the network and
are only interested in a subset of the complete history).

#### Storing Historical Messages

When message archives are fetched,
community member nodes MUST unwrap the resulting `WakuMessage` instances into `ApplicationMetadataMessage` instances
and store them in their local database.
Community member nodes SHOULD NOT store the wrapped `WakuMessage` messages.

All messages within the same time range MUST be replaced with the messages provided by the message history archive.

Community members' nodes MUST ignore the expiration state of each archive message.

### Security Considerations

#### Multiple Community Owners

It is possible for control nodes to export the private key of their owned community and
pass it to other users so they become control nodes as well.
This means it's possible for multiple control nodes to exist for one community.

This might conflict with the assumption that the control node serves as a single source of truth.
Multiple control nodes can have different message histories.
Not only will multiple control nodes multiply the amount of archive index messages being distributed to the network,
but they might also contain different sets of magnet links and their corresponding hashes.
Even if just a single message is missing in one of the histories,
the hashes presented in the archive indices will look completely different,
resulting in the community member node downloading the corresponding archive.
This might be identical to an archive that was already downloaded,
except for that one message.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [13/WAKU2-STORE](../../messaging/standards/core/13/store.md)
- [BitTorrent protocol](https://www.bittorrent.org/beps/bep_0003.html)
- [Status network](https://status.network/)
- [10/WAKU2](../../messaging/standards/core/10/waku2.md)
- [11/WAKU2-RELAY](../../messaging/standards/core/11/relay.md)
- [14/WAKU2-MESSAGE](../../messaging/standards/core/14/message.md)
- [62/STATUS-PAYLOADS](https://github.com/status-im/status-specs/tree/master/specs/status/62/payloads.md)
