# 15/WAKU-BRIDGE

| Field | Value |
| --- | --- |
| Name | Waku Bridge |
| Slug | 15 |
| Status | draft |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/core/15/bridge.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/core/15/bridge.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/core/15/bridge.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/core/15/bridge.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/core/15/bridge.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/core/15/bridge.md) — ci: add mdBook configuration (#233)
- **2025-01-28** — [`c3d5fe6`](https://github.com/logos-co/logos-lips/blob/c3d5fe6f882dbda6e01abe17adb864ae522c2f3b/waku/standards/core/15/bridge.md) — 15/WAKU2-BRIDGE: Update (#113)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/core/15/bridge.md) — Fix Files for Linting (#94)
- **2024-02-01** — [`d637b10`](https://github.com/logos-co/logos-lips/blob/d637b10156cbf6cf21f36fc090c267a33d8bafcd/waku/standards/core/15/bridge.md) — Update and rename BRIDGE.md to bridge.md
- **2024-01-27** — [`4bf2f6e`](https://github.com/logos-co/logos-lips/blob/4bf2f6ece9d077b31e8bd2833b47b0931aed5d4d/waku/standards/core/15/BRIDGE.md) — Rename README.md to BRIDGE.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/core/15/README.md) — remove rfs folder
- **2024-01-25** — [`f883f26`](https://github.com/logos-co/logos-lips/blob/f883f26a87230274eb00b960f9a4974a95e466d5/waku/rfcs/standards/core/15/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

This specification describes how [6/WAKU1](/messaging/standards/legacy/6/waku1.md)
traffic can be used with [10/WAKU2](/messaging/standards/core/10/waku2.md) networks.

## Wire Format

The keywords “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

A bridge requires supporting both Waku versions:

* [6/WAKU1](/messaging/standards/legacy/6/waku1.md) - using devp2p RLPx protocol
* [10/WAKU2](/messaging/standards/core/10/waku2.md) - using libp2p protocols

## Publishing Packets

Packets received on [6/WAKU1](/messaging/standards/legacy/6/waku1.md) networks
SHOULD be published just once on [10/WAKU2](/messaging/standards/core/10/waku2.md) networks.
More specifically, the bridge SHOULD publish
this through [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md) (PubSub domain).

When publishing such packet,
the creation of a new `Message` with a new `WakuMessage` as data field is REQUIRED.
The `data` and
`topic` field, from the [6/WAKU1](/messaging/standards/legacy/6/waku1.md) `Envelope`,
MUST be copied to the `payload` and `content_topic` fields of the `WakuMessage`.
See [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md#wire-format)
for message format details.
Other fields such as `nonce`, `expiry` and
`ttl` will be dropped as they become obsolete in [10/WAKU2](/messaging/standards/core/10/waku2.md).

Before this is done, the usual envelope verification still applies:

* Expiry & future time verification
* PoW verification
* Size verification

Bridging SHOULD occur through the [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md),
but it MAY also be done on other [10/WAKU2](/messaging/standards/core/10/waku2.md) protocols
(e.g. [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)).
The latter is however not advised as it will
increase the complexity of the bridge and
because of the [Security Considerations](#security-considerations) explained further below.

Packets received on [10/WAKU2](/messaging/standards/core/10/waku2.md) networks,
SHOULD be posted just once on [6/WAKU1](/messaging/standards/legacy/6/waku1.md) networks.
The [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md) contains only the `payload` and
`contentTopic` fields.
The bridge MUST create a new [6/WAKU1](/messaging/standards/legacy/6/waku1.md) `Envelope` and
copy over the `payload` and `contentFilter`
fields to the `data` and `topic` fields.
Next, before posting on the network,
the bridge MUST set a new `expiry`, `ttl` and do the PoW `nonce` calculation.

### Security Considerations

As mentioned above,
a bridge will be posting new [6/WAKU1](/messaging/standards/legacy/6/waku1.md) envelopes,
which requires doing the PoW `nonce` calculation.

This could be a DoS attack vector,
as the PoW calculation will make it more expensive to post the message
compared to the original publishing on [10/WAKU2](/messaging/standards/core/10/waku2.md) networks.
Low PoW setting will lower this problem,
but it is likely that it is still more expensive.

For this reason, it is RECOMMENDED to run bridges independently of other nodes,
so that a bridge that gets overwhelmed does not disrupt regular Waku v2 to v2
traffic.

Bridging functionality SHOULD also be carefully implemented so that messages do
not bounce back and forth between the [10/WAKU2](/messaging/standards/core/10/waku2.md) and
[6/WAKU1](/messaging/standards/legacy/6/waku1.md) networks.
The bridge SHOULD properly track messages with a seen filter,
so that no amplification occurs.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

* [6/WAKU1](/messaging/standards/legacy/6/waku1.md)
* [10/WAKU2](/messaging/standards/core/10/waku2.md)
* [11/WAKU2-RELAY](/messaging/standards/core/11/relay.md)
* [14/WAKU2-MESSAGE](/messaging/standards/core/14/message.md)
* [12/WAKU2-FILTER](/messaging/standards/core/12/filter.md)
