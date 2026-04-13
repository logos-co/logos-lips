# 22/TOY-CHAT

| Field | Value |
| --- | --- |
| Name | Waku v2 Toy Chat |
| Slug | 22 |
| Status | draft |
| Type | RFC |
| Category | Informational |
| Editor | Franck Royer <franck@status.im> |
| Contributors | Hanno Cornelius <hanno@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/informational/22/toy-chat.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/vacp2p/rfc-index/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/informational/22/toy-chat.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/vacp2p/rfc-index/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/informational/22/toy-chat.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/vacp2p/rfc-index/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/informational/22/toy-chat.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/vacp2p/rfc-index/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/informational/22/toy-chat.md) — Fix Files for Linting (#94)
- **2024-01-31** — [`722c3d2`](https://github.com/vacp2p/rfc-index/blob/722c3d2bcfcc260f25c10b19a7bb57f1bd6127ba/waku/informational/22/toy-chat.md) — Rename TOY-CHAT.md to toy-chat.md
- **2024-01-29** — [`5c5ea36`](https://github.com/vacp2p/rfc-index/blob/5c5ea36a47d9a364a4c0dd930cf22974029d20c7/waku/informational/22/TOY-CHAT.md) — Update TOY-CHAT.md
- **2024-01-27** — [`411e135`](https://github.com/vacp2p/rfc-index/blob/411e1354d7ff125c5cf996e8813c3f29a321f716/waku/informational/22/TOY-CHAT.md) — Create TOY-CHAT.md

<!-- timeline:end -->

**Content Topic**: `/toy-chat/2/huilong/proto`.

This specification explains a toy chat example using Waku v2.
This protocol is mainly used to:

1. Dogfood Waku v2,
2. Show an example of how to use Waku v2.

Currently, all main Waku v2 implementations support the toy chat protocol:
[nim-waku](https://github.com/status-im/nim-waku/blob/master/examples/v2/chat2.nim),
js-waku ([NodeJS](https://github.com/status-im/js-waku/tree/main/examples/cli-chat)
 and [web](https://github.com/status-im/js-waku/tree/main/examples/web-chat))
and [go-waku](https://github.com/status-im/go-waku/tree/master/examples/chat2).

Note that this is completely separate from the protocol the Status app
is using for its chat functionality.

## Design

The chat protocol enables sending and receiving messages in a chat room.
There is currently only one chat room, which is tied to the content topic.
The messages SHOULD NOT be encrypted.

The `contentTopic` MUST be set to `/toy-chat/2/huilong/proto`.

## Payloads

```protobuf
syntax = "proto3";

message Chat2Message {
   uint64 timestamp = 1;
   string nick = 2;
   bytes payload = 3;
}
```

- `timestamp`: The time at which the message was sent, in Unix Epoch seconds,
- `nick`: The nickname of the user sending the message,
- `payload`: The text of the messages, UTF-8 encoded.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
