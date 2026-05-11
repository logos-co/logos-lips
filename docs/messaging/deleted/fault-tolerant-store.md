# 21/WAKU2-FAULT-TOLERANT-STORE

| Field | Value |
| --- | --- |
| Name | Waku v2 Fault-Tolerant Store |
| Slug | 21 |
| Status | deleted |
| Type | RFC |
| Category | Standards Track |
| Editor | Sanaz Taheri <sanaz@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/messaging/deprecated/fault-tolerant-store.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/deprecated/fault-tolerant-store.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/deprecated/fault-tolerant-store.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/deprecated/fault-tolerant-store.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/deprecated/fault-tolerant-store.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/deprecated/fault-tolerant-store.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/deprecated/fault-tolerant-store.md) — ci: add mdBook configuration (#233)
- **2025-11-04** — [`cb4d0de`](https://github.com/logos-co/logos-lips/blob/cb4d0de84f64b37539af64b6de1e3084ffd74c6a/waku/deprecated/fault-tolerant-store.md) — Update 21/WAKU2-FAULT-TOLERANT-STORE: Deleted (#181)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/application/21/fault-tolerant-store.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/application/21/fault-tolerant-store.md) — Broken Links + Change Editors (#26)
- **2024-01-31** — [`5da8a11`](https://github.com/logos-co/logos-lips/blob/5da8a111ca9856ee53ee5b8598a7d5ecf5a2dce4/waku/standards/application/21/fault-tolerant-store.md) — Update and rename FAULT-TOLERANT-STORE.md to fault-tolerant-store.md
- **2024-01-27** — [`206133e`](https://github.com/logos-co/logos-lips/blob/206133edd978d85993f7680bd2ce384ba0079c1f/waku/standards/application/21/FAULT-TOLERANT-STORE.md) — Create FAULT-TOLERANT-STORE.md

<!-- timeline:end -->

 The reliability of [13/WAKU2-STORE](../draft/13/store.md)
protocol heavily relies on the fact that full nodes i.e.,
those who persist messages have high availability and
uptime and do not miss any messages.
If a node goes offline,
then it will risk missing all the messages transmitted
in the network during that time.
In this specification,
we provide a method that makes the store protocol resilient
in presence of faulty nodes.
Relying on this method,
nodes that have been offline for a time window will be able to fix the gap
in their message history when getting back online.
Moreover, nodes with lower availability and
uptime can leverage this method to reliably provide the store protocol services
as a full node.

## Method description

 As the first step
towards making the [13/WAKU2-STORE](../draft/13/store.md) protocol fault-tolerant,
we introduce a new type of time-based query through which nodes fetch message history
from each other based on their desired time window.
This method operates based on the assumption that the querying node
knows some other nodes in the store protocol
which have been online for that targeted time window.  

## Security Consideration

The main security consideration to take into account
while using this method is that a querying node
has to reveal its offline time to the queried node.
This will gradually result in the extraction of the node's activity pattern
which can lead to inference attacks.

## Wire Specification

We extend the [HistoryQuery](../draft/13/store.md#payloads) protobuf message
with two fields of `start_time` and `end_time` to signify the time range to be queried.

### Payloads

```diff
syntax = "proto3";

message HistoryQuery {
  // the first field is reserved for future use
  string pubsubtopic = 2;
  repeated ContentFilter contentFilters = 3;
  PagingInfo pagingInfo = 4;
  + sint64 start_time = 5;
  + sint64 end_time = 6;
}

```
  
### HistoryQuery

RPC call to query historical messages.

- `start_time`:
this field MAY be filled out to signify the starting point of the queried time window.
This field holds the Unix epoch time in nanoseconds.  
The `messages` field of the corresponding
[`HistoryResponse`](../draft/13/store.md#HistoryResponse)
MUST contain historical waku messages whose
[`timestamp`](../stable/14/message.md#Payloads)
is larger than or equal to the `start_time`.
- `end_time`:
this field MAY be filled out to signify the ending point of the queried time window.
This field holds the Unix epoch time in nanoseconds.
The `messages` field of the corresponding
[`HistoryResponse`](../draft/13/store.md#HistoryResponse)
MUST contain historical waku messages whose
[`timestamp`](../stable/14/message.md#Payloads) is less than or equal to the `end_time`.

A time-based query is considered valid if
its `end_time` is larger than or equal to the `start_time`.
Queries that do not adhere to this condition will not get through e.g.
an open-end time query in which the `start_time` is given but
no  `end_time` is supplied is not valid.
If both `start_time` and
`end_time` are omitted then no time-window filter takes place.

In order to account for nodes asynchrony, and
assuming that nodes may be out of sync for at most 20 seconds
(i.e., 20000000000 nanoseconds),
the querying nodes SHOULD add an offset of 20 seconds to their offline time window.
That is if the original window is [`l`,`r`]
then the history query SHOULD be made for `[start_time: l - 20s, end_time: r + 20s]`.

Note that `HistoryQuery` preserves `AND` operation among the queried attributes.
As such, the `messages` field of the corresponding
[`HistoryResponse`](../draft/13/store.md#HistoryResponse)
MUST contain historical waku messages that satisfy the indicated  `pubsubtopic` AND
`contentFilters` AND the time range [`start_time`, `end_time`].

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [13/WAKU2-STORE](../draft/13/store.md)
- [`timestamp`](../stable/14/message.md#Payloads)
