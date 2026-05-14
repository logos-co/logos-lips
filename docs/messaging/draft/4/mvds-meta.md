# 4/MVDS-META

| Field | Value |
| --- | --- |
| Name | MVDS Metadata Field |
| Slug | 4 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Sanaz Taheri <sanaz@status.im> |
| Contributors | Dean Eigenmann <dean@status.im>, Andrea Maria Piana <andreap@status.im>, Oskar Thorén <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/messaging/standards/core/4/mvds-meta.md) — chore: split ift ts specs
- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/ift-ts/raw/4/mvds-meta.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/4/mvds-meta.md) — chore: add math support (#287)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/4/mvds-meta.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/4/mvds-meta.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/4/mvds-meta.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/4/mvds-meta.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/4/mvds-meta.md) — Fix Files for Linting (#94)
- **2024-02-01** — [`3a396b5`](https://github.com/logos-co/logos-lips/blob/3a396b5fb111e73750046afb2ca10d0c28e72e83/vac/4/mvds-meta.md) — Update and rename README.md to mvds-meta.md
- **2024-01-30** — [`2e80c3b`](https://github.com/logos-co/logos-lips/blob/2e80c3bb3dc69c45fb7a932bbfaedded3f116f71/vac/4/README.md) — Create README.md

<!-- timeline:end -->

In this specification, we describe a method to construct message history that
will aid the consistency guarantees of [2/MVDS](../../stable/2/mvds.md).
Additionally,
we explain how data sync can be used for more lightweight messages that
do not require full synchronization.

## Motivation

In order for more efficient synchronization of conversational messages,
information should be provided allowing a node to more effectively synchronize
the dependencies for any given message.

## Format

We introduce the metadata message which is used to convey information about a message
and how it SHOULD be handled.

```protobuf
package vac.mvds;

message Metadata {
  repeated bytes parents = 1;
  bool ephemeral = 2;
}
```

Nodes MAY transmit a `Metadata` message by extending the MVDS [message](../../stable/2/mvds.md#payloads)
with a `metadata` field.

```diff
message Message {
  bytes group_id = 6001;
  int64 timestamp = 6002;
  bytes body = 6003;
+ Metadata metadata = 6004;
}
```

### Fields

| Name                   |   Description                                                                                                                    |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `parents`               |   list of parent [`message identifier`s](../../stable/2/mvds.md#payloads) for the specific message. |
| `ephemeral`         |   indicates whether a message is ephemeral or not.                                                             |

## Usage

### `parents`

This field contains a list of parent [`message identifier`s](../../stable/2/mvds.md#payloads)
for the specific message.
It MUST NOT contain any messages as parent whose `ack` flag was set to `false`.
This establishes a directed acyclic graph (DAG)[^2] of persistent messages.

Nodes MAY buffer messages until dependencies are satisfied for causal consistency[^3],
they MAY also pass the messages straight away for eventual consistency[^4].

A parent is any message before a new message that
a node is aware of that has no children.

The number of parents for a given message is bound by [0, N],
where N is the number of nodes participating in the conversation,
therefore the space requirements for the `parents` field is O(N).

If a message has no parents it is considered a root.
There can be multiple roots, which might be disconnected,
giving rise to multiple DAGs.

### `ephemeral`

When the `ephemeral` flag is set to `false`,
a node MUST send an acknowledgment when they have received and processed a message.
If it is set to `true`, it SHOULD NOT send any acknowledgment.
The flag is `false` by default.

Nodes MAY decide to not persist ephemeral messages,
however they MUST NOT be shared as part of the message history.

Nodes SHOULD send ephemeral messages in batch mode.
As their delivery is not needed to be guaranteed.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## Footnotes

1: [2/MVDS](../../stable/2/mvds.md)
2: [directed_acyclic_graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
3: Jepsen. [Causal Consistency](https://jepsen.io/consistency/models/causal)
Jepsen, LLC.
4: <https://en.wikipedia.org/wiki/Eventual_consistency>
