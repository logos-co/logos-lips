# 8/WAKU-MAIL

| Field | Value |
| --- | --- |
| Name | Waku Mailserver |
| Slug | 8 |
| Status | stable |
| Category | Standards Track |
| Editor | Andrea Maria Piana <andreap@status.im> |
| Contributors | Adam Babik <adam@status.im>, Dean Eigenmann <dean@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/legacy/8/mail.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/legacy/8/mail.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/legacy/8/mail.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/legacy/8/mail.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/legacy/8/mail.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/legacy/8/mail.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/legacy/8/mail.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/legacy/8/mail.md) — Broken Links + Change Editors (#26)
- **2024-02-12** — [`fa77279`](https://github.com/logos-co/logos-lips/blob/fa77279cd0a85432f1f1e96083c0e775b9a89bfd/waku/standards/legacy/8/mail.md) — Rename mail.md to mail.md
- **2024-01-31** — [`0c8e39b`](https://github.com/logos-co/logos-lips/blob/0c8e39bac9eeae649a9cca4c4e2b1b3f83d5b605/waku/standards/application/8/mail.md) — Rename MAIL.md to mail.md
- **2024-01-27** — [`de5cfa2`](https://github.com/logos-co/logos-lips/blob/de5cfa275a106eb1eee3961eba8dd35074746683/waku/standards/application/8/MAIL.md) — Rename README.md to MAIL.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/application/08/README.md) — remove rfs folder
- **2024-01-25** — [`28e7862`](https://github.com/logos-co/logos-lips/blob/28e786282c2843070c096aa0103578f50db68177/waku/rfcs/standards/application/08/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

In this specification, we describe Mailservers.
These are nodes responsible for archiving envelopes and
delivering them to peers on-demand.

## Specification

A node which wants to provide mailserver functionality MUST store envelopes
from incoming Messages packets (Waku packet-code `0x01`).
The envelopes can be stored in any format,
however they MUST be serialized and deserialized to the Waku envelope format.

A mailserver SHOULD store envelopes for all topics
to be generally useful for any peer,
however for specific use cases it MAY store envelopes for a subset of topics.

### Requesting Historic Envelopes

In order to request historic envelopes,
a node MUST send a packet P2P Request (`0x7e`)
to a peer providing mailserver functionality.
This packet requires one argument which MUST be a Waku envelope.

In the Waku envelope's payload section,
there MUST be RLP-encoded information about the details of the request:

```abnf
; UNIX time in seconds; oldest requested envelope's creation time
lower  = 4OCTET

; UNIX time in seconds; newest requested envelope's creation time
upper  = 4OCTET

; array of Waku topics encoded in a bloom filter to filter envelopes
bloom  = 64OCTET

; unsigned integer limiting the number of returned envelopes
limit  = 4OCTET

; array of a cursor returned from the previous request (optional)
cursor = *OCTET

; List of topics interested in
topics = "[" *1000topic "]"

; 4 bytes of arbitrary data
topic = 4OCTET

payload-without-topic = "[" lower upper bloom limit [ cursor ] "]"

payload-with-topic = "[" lower upper bloom limit cursor [ topics ] "]"

payload = payload-with-topic | payload-without-topic
```

The `Cursor` field SHOULD be filled in if a number of envelopes between `Lower` and
`Upper` is greater than `Limit` so that the requester can send another request
using the obtained `Cursor` value.
What exactly is in the `Cursor` is up to the implementation.
The requester SHOULD NOT use a `Cursor` obtained from one mailserver in a request
to another mailserver because the format or the result MAY be different.

The envelope MUST be encrypted with a symmetric key agreed between the requester
and Mailserver.

If `Topics` is used the `Cursor` field MUST be specified
for the argument order to be unambiguous.
However, it MAY be set to `null`.
`Topics` is used to specify which topics a node is interested in.
If `Topics` is not empty,
a mailserver MUST only send envelopes that belong to a topic from `Topics` list and
`Bloom` value MUST be ignored.

### Receiving Historic Envelopes

Historic envelopes MUST be sent to a peer as a packet with a P2P Message code (`0x7f`)
followed by an array of Waku envelopes.
A Mailserver MUST limit the amount of messages sent,
either by the `Limit` specified in the request or
limited to the maximum [RLPx packet size](../../../README.md#maximum-packet-size),
whichever limit comes first.

In order to receive historic envelopes from a mailserver,
a node MUST trust the selected mailserver,
that is allow to receive expired packets with the P2P Message code.
By default, such packets are discarded.

Received envelopes MUST be passed through the Whisper envelope pipelines
so that they are picked up by registered filters and passed to subscribers.

For a requester, to know that all envelopes have been sent by mailserver,
it SHOULD handle P2P Request Complete code (`0x7d`).
This code is followed by a list with:

```abnf
; array with a Keccak-256 hash of the envelope containing the original request.
request-id = 32OCTET

; array with a Keccak-256 hash of the last sent envelope for the request. 
last-envelope-hash = 32OCTET

; array of a cursor returned from the previous request (optional)
cursor = *OCTET

payload = "[" request-id last-envelope-hash [ cursor ] "]"
```

If `Cursor` is not empty,
it means that not all envelopes were sent due to the set `Limit` in the request.
One or more consecutive requests MAY be sent with `Cursor` field filled
in order to receive the rest of the envelopes.

### Security considerations

There are several security considerations to take into account when running or
interacting with Mailservers.
Chief among them are: scalability, DDoS-resistance and privacy.

**Mailserver High Availability requirement:**

A mailserver has to be online to receive envelopes for other nodes,
this puts a high availability requirement on it.

**Mailserver client privacy:**

A mailserver client fetches archival envelopes from a mailserver
through a direct connection.
In this direct connection,
the client discloses its IP/ID as well as the topics/ bloom filter
it is interested in to the mailserver.
The collection of such information allows the mailserver to link clients' IP/IDs
to their topic interests and build a profile for each client over time.
As such, the mailserver client has to trust the mailserver with this level of information.
A similar concern exists for the light nodes and
their direct peers which is discussed in the security considerations of [6/WAKU1](../6/waku1.md).

**Mailserver trusted connection:**

A mailserver has a direct TCP connection, which means they are trusted to send traffic.
This means a malicious or malfunctioning mailserver can overwhelm an individual node.

## Changelog

| Version                                                                                        | Comment |
| :--------------------------------------------------------------------------------------------: | ------- |
| [1.0.0](https://github.com/vacp2p/specs/commit/bc7e75ebb2e45d2cbf6ab27352c113e666df37c8)       | marked stable as it is in use.                                                   |
| 0.2.0                                                                                          | Add topic interest to reduce bandwidth usage |
| [0.1.0](https://github.com/vacp2p/specs/blob/06d4c736c920526472a507e5d842212843a112ed/wms.md)  | Initial Release |

### Difference between wms 0.1 and wms 0.2

- `topics` option

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
