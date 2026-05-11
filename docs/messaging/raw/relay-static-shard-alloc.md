# RELAY-STATIC-SHARD-ALLOC

| Field | Value |
| --- | --- |
| Name | Waku v2 Relay Static Shard Allocation |
| Slug | 165 |
| Status | raw |
| Type | RFC |
| Category | Informational |
| Tags | waku/informational |
| Editor | Daniel Kaiser <danielkaiser@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-05-07** — [`48600b5`](https://github.com/logos-co/logos-lips/blob/48600b5b4fcdcb89f3d556ee0e4d417526f2919a/docs/messaging/informational/relay-static-shard-alloc.md) — Migrate logos-messaging/specs into docs/messaging/ (#315)

<!-- timeline:end -->

## Abstract

This document lists static shard flag index assignments (see [WAKU2-RELAY-SHARDING](relay-sharding.md)).

## Background

Similar to the [IANA port allocation](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml),
this document lists static shard index assignments (see [WAKU2-RELAY-SHARDING](relay-sharding.md).

## Assingment Process

> _Note_: Future versions of this document will specify the assignment process.

### List of Cluster Ids

| index | Protocol/App | Description                                                     |
| ----- | ------------ | --------------------------------------------------------------- |
| 0     | global       | global use                                                      |
| 1     | reserved     | [The Waku Network](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/draft/64/network.md) |
| 2     | reserved     |                                                                 |
| 3     | reserved     |                                                                 |
| 4     | reserved     |                                                                 |
| 5     | reserved     |                                                                 |
| 6     | reserved     |                                                                 |
| 7     | reserved     |                                                                 |
| 8     | reserved     |                                                                 |
| 9     | reserved     |                                                                 |
| 10    | reserved     |                                                                 |
| 11    | reserved     |                                                                 |
| 12    | reserved     |                                                                 |
| 13    | reserved     |                                                                 |
| 14    | reserved     |                                                                 |
| 15    | reserved     |                                                                 |
| 16    | Status       | Status main net                                                 |
| 17    | Status       |                                                                 |
| 18    | Status       |                                                                 |

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [WAKU2-RELAY-SHARDING](relay-sharding.md)
- [IANA port allocation](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)
- [The Waku Network](https://github.com/logos-co/logos-lips/blob/master/docs/messaging/draft/64/network.md)
