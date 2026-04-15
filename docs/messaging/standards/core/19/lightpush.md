# 19/WAKU2-LIGHTPUSH

| Field | Value |
| --- | --- |
| Name | Waku v2 Light Push |
| Slug | 19 |
| Status | draft |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |
| Contributors | Daniel Kaiser <danielkaiser@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/core/19/lightpush.md) — chore: add math support (#287)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/19/lightpush.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/19/lightpush.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/19/lightpush.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/19/lightpush.md) — ci: add mdBook configuration (#233)
- **2024-11-20** — [`ff87c84`](https://github.com/logos-co/logos-lips/blob/ff87c84dc71d4f933bab188993914069fea12baa/waku/standards/core/19/lightpush.md) — Update Waku Links (#104)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/19/lightpush.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/core/19/lightpush.md) — Broken Links + Change Editors (#26)
- **2024-02-01** — [`c88680a`](https://github.com/logos-co/logos-lips/blob/c88680ab64084b578230f56e20fc21413457852c/waku/standards/core/19/lightpush.md) — Update and rename LIGHTPUSH.md to lightpush.md
- **2024-01-27** — [`f9efd29`](https://github.com/logos-co/logos-lips/blob/f9efd294fa3161f8ccc3e32df68be62413a655d8/waku/standards/core/19/LIGHTPUSH.md) — Rename README.md to LIGHTPUSH.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/19/README.md) — remove rfs folder
- **2024-01-25** — [`c90013b`](https://github.com/logos-co/logos-lips/blob/c90013bf2f6ed51ea4c72f1dec30f092c508f676/waku/rfcs/standards/core/19/README.md) — Create README.md

<!-- timeline:end -->

**Protocol identifier**: `/vac/waku/lightpush/2.0.0-beta1`

## Motivation and Goals

Light nodes with short connection windows and
limited bandwidth wish to publish messages into the Waku network.
Additionally,
there is sometimes a need for confirmation
that a message has been received "by the network"
(here, at least one node).

`19/WAKU2-LIGHTPUSH` is a request/response protocol for this.

## Payloads

```protobuf
syntax = "proto3";

message PushRequest {
    string pubsub_topic = 1;
    WakuMessage message = 2;
}

message PushResponse {
    bool is_success = 1;
    // Error messages, etc
    string info = 2;
}

message PushRPC {
    string request_id = 1;
    PushRequest request = 2;
    PushResponse response = 3;
}
```

### Message Relaying

Nodes that respond to `PushRequests` MUST either
relay the encapsulated message via [11/WAKU2-RELAY](../11/relay.md) protocol
on the specified `pubsub_topic`,
or forward the `PushRequest` via 19/LIGHTPUSH on a [WAKU2-DANDELION](https://github.com/waku-org/specs/blob/master/standards/application/dandelion.md)
stem.
If they are unable to do so for some reason,
they SHOULD return an error code in `PushResponse`.

## Security Considerations

Since this can introduce an amplification factor,
it is RECOMMENDED for the node relaying to the rest of the network
to take extra precautions.
This can be done by rate limiting via [17/WAKU2-RLN-RELAY](../17/rln-relay.md).

Note that the above is currently not fully implemented.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

* [11/WAKU2-RELAY](../11/relay.md)
* [WAKU2-DANDELION](https://github.com/waku-org/specs/blob/master/standards/application/dandelion.md)
* [17/WAKU2-RLN-RELAY](../17/rln-relay.md)
