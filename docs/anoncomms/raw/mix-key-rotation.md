# Mix Key Rotation

| Field | Value |
| --- | --- |
| Name | Mix Key Rotation |
| Status | raw |
| Category | Standards Track |
| Editor | Akshaya Mani <akshaya@status.im> |
| Contributors |  |

<!-- timeline:start -->
<!-- timeline:end -->

## Abstract

This document specifies key rotation for the [Mix Protocol](./mix.md).
Each mix node replaces its mix key at a fixed interval on its own clock,
publishes each new public key through discovery,
keeps accepting its old key for a grace window,
and then destroys that key together with its replay table.
Compromise of a node's keys then reveals at most the packets processed under the keys the node still accepts.
The mix identity, the Sphinx packet format, and the published record format are unchanged.

## 1. Introduction

In the [Mix Protocol](./mix.md),
each node derives per-hop shared secrets from its X25519 key
and detects replays from the tags it has seen under that key
([Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Steps 1 and 2).
The Mix Protocol itself does not define how nodes rotate that key,
or how long an old key remains accepted.

Without rotation,
an adversary that records the packets a node receives,
and later obtains its key,
can process them as the node did,
learning each packet's next hop,
or its payload where the node is the last hop.
The node's replay tags also accumulate without bound,
and a node that expires tags to bound them
lets an adversary replay any packet whose tag has expired.

This specification defines that rotation:
how a node generates, publishes, and destroys its keys,
how it processes packets while it still accepts old keys,
and how initiating nodes build packets with the keys they discover.
Each key and its replay table are then kept only for a bounded time ([Section 3.1](#31-lifecycle)),
which limits what a key compromise exposes ([Section 9.1](#91-forward-secrecy)).

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Other terms used in this document are as defined in the [Mix Protocol](./mix.md)
and [Mix Cover Traffic](./mix-cover-traffic.md) specs.

The following additional terms are used throughout this specification:

- **Mix Key**: The X25519 key pair a node uses to derive the per-hop shared secret
  ([Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 1).
  A node publishes only its public key;
  the private key never leaves the node.
  A packet is built for a mix key
  if the initiating node derived the node's per-hop shared secret from that key's public key
  ([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 3.a).
- **Rotation Interval `U`**: The `U` seconds between two key generations of a node, measured on its own clock.
- **Grace Window `G`**: The `G` seconds after a key is replaced during which the node still accepts it.
  It is longer than `U` ([Section 8](#8-parameters)).
- **Current Key**: The mix key a node generated most recently.
- **Old Key**: A mix key that the node has replaced with a newer one,
  and whose grace window has not yet ended.
- **Replay Table**: The tags a node has seen under one mix key.
- **Record**: The information a node publishes through discovery ([Mix Protocol Section 6.1](./mix.md#61-discovery)),
  including its current public key,
  authenticated under the node's mix identity.
- **`D`**: The longest time nodes can still obtain a record whose key has been replaced,
  from the discovery mechanism or any cache they obtain records from,
  such as records relayed by other nodes.
- **`max_transit`**: A bound on the time from when an initiating node starts transmitting a packet
  ([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 3.f),
  or an exit starts transmitting a SURB reply ([Mix Protocol Section 8.7.3](./mix.md#873-using-a-surb) Step 3),
  until the last hop processes it,
  including pre-send and per-hop delays.
  These delays are unbounded ([Mix Protocol Section 6.2](./mix.md#62-delay-strategy)),
  so this is a bound the transit time exceeds with negligible probability.

## 3. Mix Keys

### 3.1 Lifecycle

On the node's own clock,
each mix key passes through the following states:

| State | Interval | The node |
|---|---|---|
| Current | `U` seconds from its generation | publishes its public key if it relays packets for others ([Section 4](#4-key-publication)), and accepts it. |
| Old | the next `G` seconds | still accepts it, trying it after the current key ([Section 6](#6-node-processing)). |
| Destroyed | from then on | has made it unrecoverable ([Section 3.3](#33-destruction)). |

Since `G > U` ([Section 8](#8-parameters)),
a key is still accepted after the next rotation,
so a node that rotates every `U` seconds accepts up to `⌈G / U⌉ + 1` keys at once.
With `U` = 1 hour and `G` = 1 hour 30 minutes,
keys generated at 0:00, 1:00, and 2:00 are all accepted between 2:00 and 2:30.

### 3.2 Generation

Each mix key is an X25519 key pair as defined in the [Mix Protocol](./mix.md#82-cryptographic-primitives).
A node MUST generate each mix key independently of the mix identity and of every other mix key,
and MUST generate a new mix key every `U` seconds on its own clock.
A node MAY persist its mix keys ([Section 3.5](#35-start-and-restart)).
A node that does MUST persist them securely,
and a node that also publishes its public keys ([Section 4](#4-key-publication))
MUST persist each key before publishing its public key.

### 3.3 Destruction

When the grace window of an old key ends,
a node MUST make that private key and its replay table unrecoverable,
including any persisted copies.
After that,
no party can process a packet built for that key.

A node MUST make each shared secret it derives,
and the keys derived from it,
unrecoverable once it has sent the packet it built,
or processed the packet it received.
The shared secrets of a SURB are discarded as [Section 7](#7-single-use-reply-blocks) specifies.

### 3.4 Replay Tables

A node MUST keep a separate replay table for each mix key it accepts ([Section 6](#6-node-processing)).
It destroys each table together with its key ([Section 3.3](#33-destruction)).
A node MUST NOT remove a tag from a replay table while the table's key is accepted.
It MUST size each replay table for the packets it accepts under that key
over the `U + G` seconds the key is accepted.
If a replay table is full,
the node MUST discard received packets built for that key rather than remove old tags,
and SHOULD make the condition observable to its operator.

### 3.5 Start and Restart

A node keeps its keys' complete replay tables across a restart
only if it persisted each tag before acting on the packet that produced it.
A node MUST NOT process packets under a key without its complete replay table.
Otherwise, packets processed before the restart could be replayed through it.

A node that persists its keys
MUST also persist when each was generated and replaced.
This allows it to measure `U` and `G` on its wall clock across restarts.

When a node restarts,
it MUST destroy every key whose grace window has ended
or that lacks its complete replay table ([Section 3.3](#33-destruction)),
and MUST replace its current key if `U` seconds have passed since it was generated.
If this leaves it without a current key,
as for a node that does not persist its keys or has lost its persistent storage,
it MUST generate a new one,
publish it if it relays packets for others ([Section 4](#4-key-publication)),
and start a new rotation interval from then.

## 4. Key Publication

A node that relays packets for others publishes its current public key through discovery
([Mix Protocol Section 6.1](./mix.md#61-discovery)),
authenticated under its mix identity.
When it generates a new key,
it MUST publish the new public key in place of the old one,
and MUST stop publishing the record with the old key,
including any publication of it still in progress,
so that discovery stops returning that record within `D` seconds.
The record is otherwise unchanged:
it carries only the current public key.

A node that only initiates packets also rotates its key ([Section 3.2](#32-generation)),
since it uses the key for its own hop ([Section 5](#5-initiating-node-behavior)),
but MUST NOT publish it, as it does not relay packets.

## 5. Initiating Node Behavior

A record's age is the time since an initiating node last obtained it from discovery.
Obtaining the same record again resets its age;
loading it from the node's own storage does not.

An initiating node:

- MUST use the record it obtained most recently for each node.
- MUST obtain mix public keys only through discovery.
- MUST NOT build a packet, including the SURBs it carries,
  with a public key from a record more than `U` seconds old.
  It treats any node whose record is more than `U` seconds old like an offline one
  until discovery returns its record.
- MUST rebuild a packet built in advance,
  such as a cover packet or a queued message,
  if it would be transmitted once a record it was built from is more than `U` seconds old.
- MUST use its own current key for its own hop,
  such as the last hop of a loop or of a SURB's return path.

## 6. Node Processing

This section replaces Steps 1 to 3 of [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing).

The candidate keys are the current key and every old key.
For each candidate,
starting with the current key and then the old keys, newest first,
the node MUST:

1. Derive the shared secret `s` from `α` and the candidate's private key.
2. If the tag `H(s)` is in the candidate's replay table,
   discard the packet and stop.
3. If the header integrity check passes under `s`,
   store the tag in the candidate's replay table
   and continue from [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 4.

The check passes only under the key the packet was built for.
Unlike [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 2,
a node stores the tag only after the check passes,
so that packets built for other keys add no tags to a table.
If the check fails under every candidate,
the node MUST discard the packet without storing a tag.
A node SHOULD perform the same computations under every candidate for every packet,
so that processing time does not reveal which key a packet used.

## 7. Single-Use Reply Blocks

A SURB is built with the keys of the initiating node's records at that time.
In the worst case,
a record was obtained `D` seconds after its key was replaced ([Section 4](#4-key-publication)),
and the SURB was built as late as `U` seconds after that ([Section 5](#5-initiating-node-behavior)),
so the key remains accepted for only `G - U - D` more seconds.
The request and the reply take up to `max_transit` each,
and what remains is the time the destination has to respond.

An exit MUST therefore drop held SURBs ([Mix Protocol Section 8.7.3](./mix.md#873-using-a-surb))
no later than `G - U - D - 2 · max_transit` seconds after receiving them,
which is the longest the destination can take to respond.
The creator MUST make the tuple it stores for reply recovery
([Mix Protocol Section 8.7.2](./mix.md#872-surb-creation) Step 4)
unrecoverable once it recovers the reply,
or `G - U - D` seconds after building the SURB,
whichever is first.

## 8. Parameters

This specification has two parameters,
with the following recommended values:

| Parameter | Recommended | Rationale |
|---|---|---|
| `U` | 1 hour | Rotation interval. A shorter interval reduces the past traffic a key compromise exposes and the size of each replay table, but requires initiating nodes to obtain records more often ([Section 5](#5-initiating-node-behavior)). |
| `G` | 1 hour 30 minutes | Grace window. Exceeds `U + D + 2 · max_transit` for the bounds assumed below, and gives the destination up to 13 minutes to respond to a request ([Section 7](#7-single-use-reply-blocks)). |

The recommended `G` assumes the following bounds,
which are properties of a deployment rather than choices:

| Bound | Assumed | Rationale |
|---|---|---|
| `D` | 15 minutes | Covers a discovery mechanism that stops returning a node's old record within this time ([Section 4](#4-key-publication)). A mechanism that keeps returning old records for longer needs a correspondingly larger `G`. |
| `max_transit` | 1 minute | Covers pre-send and per-hop delays ([Section 2](#2-terminology)). Mean delays of under a second keep a path's transit well below this, except with negligible probability. |

A record does not say when its key will be replaced,
so a deployment MUST choose `G` greater than `U + D + 2 · max_transit` ([Section 7](#7-single-use-reply-blocks)),
and SHOULD choose it larger by at least the response times of its applications.

Since nodes rotate keys, drop records, and hold SURBs using these values,
every node in a deployment MUST use the same `U`, `G`, `D`, and `max_transit`.
With the recommended values,
a key is accepted for 2 hours 30 minutes,
and a node accepting 10 packets per second stores 90,000 tags per replay table.

## 9. Security and Privacy Considerations

### 9.1 Forward Secrecy

An adversary that obtains a node's keys at time `t` obtains only the keys the node still holds at `t`.
Each was generated no more than `U + G` seconds before `t`,
so at most that much past traffic is exposed.
Since `G > U` ([Section 8](#8-parameters)),
this is more than twice `U`.
Shared secrets do not extend this,
since a node erases each one once it has processed its packet ([Section 3.3](#33-destruction)).
Neither do the SURB tuples a node holds for its own pending replies,
since it discards each within `G - U - D` seconds ([Section 7](#7-single-use-reply-blocks)).

### 9.2 Replays

Rotation does not open a gap for replays.
While a key is accepted,
its replay table detects every replay of a packet built for it ([Section 3.4](#34-replay-tables)),
including across restarts ([Section 3.5](#35-start-and-restart)).
Once the key is destroyed,
a replayed packet built for it can no longer be processed ([Section 3.3](#33-destruction)).

### 9.3 Sender Partitioning

The key a packet uses tells a node when, or through which part of the discovery mechanism,
its sender last obtained the node's record.
Even with honest rotation,
for up to `U + D` seconds after each rotation,
this separates initiating nodes that have obtained the new record from those that have not.
Nothing limits how often a node rotates,
or stops it from publishing different keys through different parts of the discovery mechanism,
so a node can split initiating nodes further,
and with a colluding discovery node or cache it can single out one.
An initiating node cannot detect this,
even if it obtains several of the node's records,
since a different key can always be a rotation.

### 9.4 Silent Loss

If discovery serves an old record for longer than `D`,
an initiating node keeps a record for longer than `U` seconds,
or the node loses its keys,
or its wall clock steps forward across a restart and makes it destroy keys early ([Section 3.5](#35-start-and-restart)),
packets built for a key the node no longer holds are lost without notice,
which looks like the node dropping traffic.
An old record remains validly authenticated,
so a malicious discovery node or cache can also cause this deliberately,
by serving it beyond `D`.

## 10. Operational Considerations

Rotation has the following operational costs:

- **Pool shrinkage**:
  An initiating node keeps only the nodes whose records it obtains again within every `U` seconds ([Section 5](#5-initiating-node-behavior)).
  A discovery mechanism that returns random samples cannot target specific nodes,
  so an initiating node loses the nodes it does not find again,
  and needs to look up more often to keep its pool full.
- **More work per packet**:
  Up to `⌈G / U⌉ + 1` keys are tried on every packet ([Section 6](#6-node-processing)),
  three with the recommended values.
- **Synchronized rotation**:
  Nodes started at the same time rotate at the same time,
  so the discovery mechanism receives their new records together.

## 11. Future Work

- **Validity in records**:
  Publishing when each key is accepted, such as `activates_at` and `not_after`,
  would let initiating nodes tell a live key from an old one,
  so the grace window would only need to cover clock offset, transit, and response time,
  at the cost of a bound on clock offset between nodes.
- **Scheduled rotation**:
  A common key schedule with each next key published in advance
  ([Scheduled Mix Key Rotation](https://github.com/logos-co/logos-lips/pull/502))
  would also let initiating nodes obtain a node's next key before it is used,
  and detect a node that publishes two keys for the same period,
  at the cost of a larger record and a clock bound between nodes.
- **Key identifier in the header**:
  Would remove trial decryption,
  at the cost of a packet format change.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [Mix Protocol](./mix.md)
- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119)

### Informative

- [Mix Cover Traffic](./mix-cover-traffic.md)
- [Scheduled Mix Key Rotation (PR #502)](https://github.com/logos-co/logos-lips/pull/502)
