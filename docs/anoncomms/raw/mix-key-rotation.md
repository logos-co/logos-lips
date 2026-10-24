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
Each mix node replaces the X25519 key it uses for Sphinx processing at fixed intervals common to all nodes,
publishes each public key during the preceding interval,
accepts each key for a short window before and after its interval,
and then destroys the key together with its replay table.
Compromise of a node then reveals at most the packets it processed under the keys it still accepts.
The mix identity and the Sphinx packet format are unchanged.

## 1. Introduction

The [Mix Protocol](./mix.md) assumes that nodes rotate the X25519 key they use for Sphinx processing:
a node MAY flush its replay table when it rotates its key
([Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 2),
and a SURB becomes unusable once a node on its return path rotates
([Mix Protocol Section 8.7.2](./mix.md#872-surb-creation)).
However, it does not define how nodes rotate keys,
how they publish new public keys,
or how initiating nodes select them.

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
the key schedule,
how nodes publish public keys,
how initiating nodes select keys,
and how nodes process packets across a key change.
It limits the packets a compromised node exposes
to those processed under the keys it still accepts ([Section 11.1](#111-forward-secrecy)),
and each replay table to the packets processed under one key.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Other terms used in this document are as defined in the [Mix Protocol](./mix.md),
[Mix DoS Protection](./mix-dos-protection.md),
[Mix Cover Traffic](./mix-cover-traffic.md),
and [Mix Local Reputation](https://github.com/logos-co/logos-lips/pull/463) specs.

The following additional terms are used throughout this specification:

- **Mix Key**: The X25519 key pair a node uses to derive the per-hop shared secret
  ([Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 1).
  A node publishes only its public key;
  the private key never leaves the node.
  A packet is built for a mix key
  if the initiating node derived the node's per-hop shared secret from that key's public key
  ([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 3.a).
- **Key Period**: A fixed interval of `U` seconds,
  during which each node uses one mix key.
  Like the RLN `epoch` ([Mix RLN DoS Protection](./mix-dos-protection-rln.md#messaging-rate)),
  nodes agree on them without coordination:
  the key period at Unix time `t` is `key_period(t) = floor(t / U)`,
  and key period `p` starts at `start(p) = p · U`.
- **Current, Previous, Next Key**: The keys for `key_period(t)`, `key_period(t) - 1`, and `key_period(t) + 1`,
  where `t` is the node's local time.
- **Key Entry**: A pair (`p`, public key) that a node publishes for key period `p`.
- **Replay Table**: The tags a node has seen under one mix key.
- **`max_clock_offset`**: The largest difference between any node's local time and true time
  that a deployment assumes.
- **`max_transit`**: A bound on the time from when an initiating node starts transmitting a packet
  ([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 3.f),
  or an exit starts transmitting a SURB reply ([Mix Protocol Section 8.7.3](./mix.md#873-using-a-surb) Step 3),
  until the last hop processes it,
  including pre-send and per-hop delays.
  These delays are unbounded ([Mix Protocol Section 6.2](./mix.md#62-delay-strategy)),
  so this is a bound the transit time exceeds with negligible probability.
- **Early Window**: The last `Q` seconds of key period `p - 1`, `[start(p) - Q, start(p))`,
  during which a node already accepts the key for key period `p`.
  `Q ≥ 2 · max_clock_offset`,
  since the clocks of two nodes can differ by at most twice the offset.
- **Grace Window**: The first `V` seconds of key period `p`, `[start(p), start(p) + V)`,
  during which a node still accepts the key for key period `p - 1`.
  `V > 2 · max_transit + 2 · max_clock_offset`,
  so that a SURB built just before a change survives until the reply returns
  ([Section 8](#8-single-use-reply-blocks)).
  `Q + V < U`,
  so that the early and grace windows do not overlap.

## 3. Design Principles

The design follows the key rotation of the [Katzenpost mix network](https://katzenpost.network/docs/specs/mixnet/),
with public keys published through discovery.

1. **Common schedule**:
   All nodes change keys at the start of each key period,
   so an initiating node can tell which key any node uses at any time from its own clock.
   Since clocks differ and packets take time to arrive,
   the early and grace windows let nodes accept packets built on either side of a change.
2. **Publish before use**:
   A node publishes the public key of each mix key through discovery ([Mix Protocol Section 6.1](./mix.md#61-discovery))
   during the preceding key period,
   so that initiating nodes hold it when it becomes current.
3. **Identity separate from key**:
   Rotation changes the mix key only.
   Anything bound to the mix identity persists across key periods.
4. **One key per key period**:
   Each node has exactly one key per key period ([Section 5.1](#51-key-entries)).
5. **At most two keys accepted**:
   The current key,
   the previous key during the grace window,
   and the next key during the early window.
6. **Destroy on expiry**:
   A key and its replay table are destroyed together,
   when the grace window that follows the key's period ends.
7. **No packet format change**:
   Packets carry no key identifier.
   A node tries the current key,
   followed by the previous or next key if it accepts it in that window.
   The header integrity check ([Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 3)
   passes only under the key the packet was built for.

## 4. Key Schedule

### 4.1 Lifecycle

On the node's local clock,
the key for key period `p` passes through the following states:

| State | Interval | The node |
|---|---|---|
| Next | `[start(p - 1), start(p) - Q)` | publishes its public key ([Section 5.1](#51-key-entries)) but does not accept it. |
| Next, early window | `[start(p) - Q, start(p))` | also accepts it, trying it after the key for `p - 1` ([Section 7](#7-node-processing)). |
| Current | `[start(p), start(p + 1))` | accepts it. |
| Previous | `[start(p + 1), start(p + 1) + V)` | still accepts it, trying it after the key for `p + 1` ([Section 7](#7-node-processing)). |
| Destroyed | from `start(p + 1) + V` | has made it unrecoverable ([Section 4.3](#43-destruction)). |

A node holds at most three private keys and accepts packets built for at most two.
This requires `Q + V < U`.

### 4.2 Generation

Each mix key is an X25519 key pair as defined in the [Mix Protocol](./mix.md#82-cryptographic-primitives).

- **Independence**: A node MUST generate each mix key independently of the mix identity and of every other mix key.
- **Timing**: A node MUST NOT generate the key for a key period before the preceding key period starts,
  and MUST persist it securely before publishing its public key ([Section 5.1](#51-key-entries)).
- **No replacement**: A node MUST NOT generate a key for a key period for which it has published a public key
  ([Section 5.1](#51-key-entries)),
  including after a restart ([Section 4.5](#45-start-and-restart)).

### 4.3 Destruction

When the grace window of key period `p + 1` ends,
a node MUST make the private key for key period `p` and its replay table unrecoverable,
including any persisted copies.
After that,
no party can process a packet built for that key.

A node MUST make each shared secret it derives,
and the keys derived from it,
unrecoverable once it has sent the packet it built,
or processed the packet it received.

The shared secrets of a SURB are stored for reply recovery instead
([Mix Protocol Section 8.7.2](./mix.md#872-surb-creation) Step 4).
A node MUST make them unrecoverable once it has recovered the reply
([Mix Protocol Section 8.7.5](./mix.md#875-reply-recovery)),
or when the grace window that follows the SURB's key period ends,
whichever is first ([Section 8](#8-single-use-reply-blocks)).

### 4.4 Replay Tables

A node keeps a separate replay table for each mix key ([Section 7](#7-node-processing)),
and destroys it together with that key ([Section 4.3](#43-destruction)).
A node MUST NOT remove a tag from a replay table while the table's key is accepted,
and MUST size each replay table for the packets it accepts over the `Q + U + V` seconds the key is accepted.
If a replay table is full,
the node MUST discard received packets built for that key rather than remove old tags,
and SHOULD make the condition observable to its operator
([Section 11.3](#113-replay-table-exhaustion)).

### 4.5 Start and Restart

A node MUST NOT process packets under a key without the key's complete replay table.
After a restart,
a key has its complete table only if the node persisted each tag
before forwarding or delivering the packet that produced it.
Otherwise,
packets processed before the restart could be replayed through the node.

A node that holds no private key for the current or next key period
MUST generate a mix key for it,
unless it has published a public key for that period ([Section 4.2](#42-generation)).
A node that has lost its persistent storage
MUST assume it has published public keys for the current and next key periods,
unless discovery shows otherwise,
and so cannot process packets until the key period after next starts,
up to `2 · U` seconds later.
A node whose clock runs ahead by more than `max_clock_offset`
destroys its keys early ([Section 4.3](#43-destruction)),
and once its clock is corrected,
cannot process packets until a key period whose key it has not published starts.

A node MUST NOT publish key entries while it cannot process packets under its current or next key,
since initiating nodes would send it packets it can only discard.
Once it can process packets under both,
it MUST publish its key entries without waiting for its randomized change time ([Section 5.1](#51-key-entries)).

## 5. Key Publication

### 5.1 Key Entries

A node MUST publish its key entries through discovery ([Mix Protocol Section 6.1](./mix.md#61-discovery)),
authenticated under its mix identity.
In each key period `p`,
it MUST change its published entries from those for `p - 1` and `p`
to those for `p` and `p + 1`,
at a time chosen uniformly at random from `[start(p) + Q, start(p) + U / 2)` on its local clock.
Between changes,
it republishes the same entries as often as the discovery mechanism requires.
It MUST NOT publish entries for any other key period,
nor two different public keys for the same key period, including across restarts.
A node that cannot yet process packets under its current and next keys publishes no entries
([Section 4.5](#45-start-and-restart)).

Changing no earlier than `start(p) + Q` keeps the entry for `p - 1` published
while initiating nodes whose clocks lag the node's still use it ([Section 6.1](#61-key-selection)).
If all nodes changed their entries at the same instant,
the discovery mechanism would receive every change at once
and could delay some until after initiating nodes need them.
A random time spreads the changes over the first half of the key period.
Since this specification assumes that a change reaches all nodes within `U / 4` seconds ([Section 9](#9-integration)),
every change has reached them by the last quarter of the key period,
when they refresh ([Section 6.2](#62-entry-refresh-and-cache)).

### 5.2 Encoding in Extensible Peer Records

A deployment that advertises mix nodes with [Extensible Peer Records](./extensible-peer-records.md),
such as the [Logos Mixnet](./logos-mixnet.md#discovery),
MUST carry the key entries in the `data` field of the Mix Protocol's `ServiceInfo` as:

```protobuf
syntax = "proto3";

message MixKeyEntries {
  uint64 key_period = 1; // key period of `key`
  bytes key = 2;         // X25519 public key for `key_period`, 32 bytes
  bytes next_key = 3;    // X25519 public key for `key_period + 1`, 32 bytes
}
```

The entries MUST be authenticated under the node's mix identity ([Section 5.1](#51-key-entries)).
A receiver MUST discard a `MixKeyEntries` whose keys are not 32 bytes each,
and MUST NOT parse a `data` field of exactly 32 bytes,
which is a single unrotated key,
as `MixKeyEntries`.
An encoding is at most 79 bytes,
a deliberate deviation from the 33 bytes [Extensible Peer Records](./extensible-peer-records.md#wire-protocol) RECOMMENDS for `data`.

## 6. Initiating Node Behavior

### 6.1 Key Selection

An initiating node MUST build each packet,
including the SURBs it carries,
with each hop's key for `q = key_period(t)`,
where `t` is its local time when it selects the packet's mix path
([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 2).
It MUST NOT place a node on the path unless it holds that node's key entry for `q`;
it needs no entry for itself,
such as when it is the last hop of a loop or of a SURB's return path.
A packet whose transmission ([Mix Protocol Section 8.5.2](./mix.md#852-construction-steps) Step 3.f)
starts in a later key period than `q`,
such as a pre-built cover packet or a queued message,
MUST be rebuilt with its SURBs before it is transmitted.

Initiating nodes and hops switch on their own clocks,
so a packet can reach a hop shortly before or after that hop's own change.
The early and grace windows ([Section 2](#2-terminology)) cover this:
a packet built for a hop's next key reaches it no earlier than its early window,
and one built for a hop's previous key reaches it within its grace window.

### 6.2 Entry Refresh and Cache

In each key period `p`,
nodes change their entries before `start(p) + U / 2` ([Section 5.1](#51-key-entries)),
and the changes are assumed to reach all nodes within a further `U / 4` seconds ([Section 9](#9-integration)).
An initiating node SHOULD therefore refresh the entries of the nodes it has discovered after `start(p) + 3 · U / 4`,
so that it holds their next entries when the key period changes.

When a refresh returns an entry for a key period the initiating node already holds,
it MUST compare the two.
If the public keys differ,
the publishing node has violated [Section 5.1](#51-key-entries),
and the initiating node MUST NOT place it on a path
until that key period has ended.

An initiating node SHOULD discard each entry it has verified once the entry's key period ends on its local clock.

## 7. Node Processing

This section replaces Steps 1 to 3 of [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing).

Let `t` be the node's local time and `p = key_period(t)`.
The candidate keys are the key for `p`,
the key for `p - 1` if `t < start(p) + V`,
and the key for `p + 1` if `t ≥ start(p + 1) - Q`.
At most two apply at any time,
since `Q + V < U` ([Section 2](#2-terminology)).
For each candidate,
starting with the key for `p`,
the node MUST:

1. Derive the shared secret `s` from `α` and the candidate's private key.
2. If the tag `H(s)` is in the candidate's replay table,
   discard the packet and stop.
3. If the header integrity check passes under `s`,
   store the tag in the candidate's replay table
   and continue from [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 4.

The check passes only under the key the packet was built for.
Unlike [Mix Protocol Section 8.6.1](./mix.md#861-shared-preprocessing) Step 2,
which stores the tag before the check,
a node stores the tag only after the check passes,
and only in the table of the key under which it passes.
If the check fails under every candidate,
the node MUST discard the packet without storing a tag,
since the packet has no effect,
and junk tags would fill the replay tables.

When two keys are candidates,
a node SHOULD perform the same computations under both for every packet,
even when the first passes,
so that processing time does not reveal which key a packet used.

## 8. Single-Use Reply Blocks

A SURB is built together with the packet that carries it ([Section 6.1](#61-key-selection)),
so it uses the keys for that packet's key period,
and stays usable until the grace window that follows that key period ends.
How much of that time remains depends on when in the key period the SURB was built,
which its holder cannot tell.
In the worst case,
a SURB built just before a key change has only `V` seconds,
of which clock offset can take `2 · max_clock_offset`,
and the forward message and the reply up to `max_transit` each.

An exit MUST therefore drop held SURBs ([Mix Protocol Section 8.7.3](./mix.md#873-using-a-surb))
no later than `V - 2 · max_transit - 2 · max_clock_offset` after receiving them.
Otherwise,
a reply sent later could reach a node on the return path that no longer accepts the SURB's keys,
and be lost.
Since `V > 2 · max_transit + 2 · max_clock_offset` ([Section 2](#2-terminology)),
this bound is always positive.

The creator discards the tuple it stores for reply recovery
([Mix Protocol Section 8.7.2](./mix.md#872-surb-creation) Step 4)
once it recovers the reply,
or when the grace window that follows the SURB's key period ends,
whichever is first ([Section 4.3](#43-destruction)).

## 9. Integration

Key rotation affects the following components of a mix deployment.

- **Discovery**:
  Each node publishes key entries ([Section 5.1](#51-key-entries))
  in place of the single X25519 public key of [Mix Protocol Section 6.1](./mix.md#61-discovery).
  This specification assumes that a node's changed entries reach all nodes
  within `U / 4` seconds of the change.
  A discovery mechanism that can read key entries
  SHOULD reject a record whose public key for a key period
  differs from one it already holds for that node and key period ([Section 5.1](#51-key-entries)).
- **Path selection**:
  A path-selection strategy can keep state about a node across key periods under its mix identity.
  It places the node on a path only while it holds the node's key entry for that key period ([Section 6.1](#61-key-selection)).
- **Cover traffic**:
  Loop packets return to the node that sends them,
  so their last hop needs no published entry.
  A loop packet built in advance is rebuilt
  if it is sent in a later key period than the one it was built for ([Section 6.1](#61-key-selection)).
- **DoS protection**:
  Key periods are independent of the epochs of the DoS protection mechanism,
  and its proofs do not depend on mix keys.
- **Local reputation**:
  Records kept under the mix identity persist across key periods.
  The replay-detection window within which [Mix Local Reputation](https://github.com/logos-co/logos-lips/pull/463) counts a peer's replays
  is the lifetime of one key's replay table,
  `Q + U + V` seconds ([Section 4.4](#44-replay-tables)).

## 10. Parameters

This specification has three parameters,
with the following recommended values:

| Parameter | Recommended | Rationale |
|---|---|---|
| `U` | 3 hours | Key period. Balances exposure after a compromise and replay table size against time for discovery, as below. |
| `V` | 15 minutes | Grace window. Exceeds `2 · max_transit + 2 · max_clock_offset`, so that a SURB built just before a change survives until its reply returns ([Section 8](#8-single-use-reply-blocks)). |
| `Q` | 1 minute | Early window. At least `2 · max_clock_offset`, the most by which the clocks of two nodes can differ ([Section 2](#2-terminology)). It needs no allowance for transit, which only delays a packet. |

A shorter key period reduces the past traffic a compromise exposes, `Q + U + V` seconds,
and the size of each replay table ([Section 4.4](#44-replay-tables)).
A longer one gives discovery more time, `U / 4`, to deliver each change of entries ([Section 9](#9-integration)).
At 3 hours,
a compromise exposes at most 3 hours 16 minutes of past traffic,
a node accepting 10 packets per second stores 117,600 tags per replay table,
and each change of entries has 45 minutes to reach all nodes.
[Katzenpost](https://katzenpost.network/docs/specs/mixnet/) uses the same period for its mix keys.

The recommended `V` and `Q` assume the following bounds,
which are properties of a deployment rather than choices:

| Bound | Assumed | Rationale |
|---|---|---|
| `max_clock_offset` | 15 seconds | Typical of nodes that synchronize their clocks over the network. A DoS protection mechanism that compares epochs across nodes, such as [Mix RLN DoS Protection](./mix-dos-protection-rln.md), already requires clocks to agree closely. |
| `max_transit` | 1 minute | Covers pre-send and per-hop delays ([Section 2](#2-terminology)). Mean delays of under a second keep a path's transit well below this, except with negligible probability. |

For its own bounds,
a deployment MUST choose `Q` and `V` that satisfy the constraints of the early and grace windows,
and `U` greater than `Q + V` ([Section 2](#2-terminology)).
The recommended values satisfy them for the bounds above,
and cap the exit's SURB timeout ([Section 8](#8-single-use-reply-blocks)) at 12.5 minutes.

## 11. Security and Privacy Considerations

### 11.1 Forward Secrecy

A node compromised at time `t` reveals the keys it holds at `t`.
Only the keys it accepts at `t` have processed packets,
and each was first accepted no more than `Q + U + V` seconds before `t`,
so at most that much past traffic is exposed.
The next key, if accepted, has processed only packets from its early window.
Shared secrets add nothing,
since they are erased after processing ([Section 4.3](#43-destruction)).
Rotation does not recover from an undetected compromise,
since the adversary can obtain each new key as it is generated.

A key exposes one hop:
the next hop of each packet,
and the payload where the node was the last hop.

### 11.2 Replays

Sphinx packets carry no timestamp,
and a replayed packet can carry a fresh, valid proof of the DoS protection mechanism,
so only the replay table and key destruction prevent replays.
While its key is accepted,
the key's replay table detects a replayed packet ([Section 4.4](#44-replay-tables)),
including across restarts ([Section 4.5](#45-start-and-restart)).
Once the key is destroyed,
the node can no longer process packets built for the key,
and discards them ([Section 7](#7-node-processing)).

### 11.3 Replay Table Exhaustion

A replay table holds the tag of every packet a node accepts under its key,
so no single membership's rate limit bounds how fast the table fills.
An adversary with several memberships can therefore direct packets at one node to fill a table.
Once the table is full,
the node discards every new packet built for that key until the key is destroyed ([Section 4.4](#44-replay-tables)).
It does not make room by removing old tags,
since the packets whose tags were removed could then be replayed.
The node's other traffic already fills part of the table,
so the adversary needs only enough memberships to fill the rest,
each sending at no more than its per-hop rate limit ([Mix DoS Protection](./mix-dos-protection.md)).
Sizing a table with headroom above the node's expected traffic leaves more for the adversary to fill,
and so raises the number of memberships the attack needs.

### 11.4 Key Equivocation

A node that publishes conflicting public keys for one key period
can tell apart initiating nodes that obtained different keys,
by the key their packets use.
Initiating nodes detect such conflicts by comparing the entries they obtain,
and then exclude the node for that key period ([Section 6.2](#62-entry-refresh-and-cache)).
A discovery mechanism that follows [Section 9](#9-integration) also rejects conflicting records it receives.
A node that gives different keys to different parts of the discovery mechanism
escapes both checks for any initiating node that obtains entries from only one part,
but learns no more than which part that initiating node used.

### 11.5 Key Choice Near a Change

An initiating node switches keys when its own clock reaches a key change ([Section 6.1](#61-key-selection)),
so a clock that runs ahead or behind makes it switch early or late.
Packets it builds in that gap use a different key than a node with an exact clock would,
and each hop sees which key a packet uses.
The gap is at most `max_clock_offset` ([Section 2](#2-terminology)),
packets built outside it reveal nothing,
and hops after the first do not know which initiating node built a packet.

### 11.6 Missing and Stale Entries

- **Fixed nodes**: Some path-selection strategies keep the same nodes across many paths.
  To keep using those nodes after a key change,
  such a strategy needs their next entries,
  but a discovery mechanism that returns random samples of nodes might not return them,
  so the strategy can lose those nodes at a key change ([Section 6.1](#61-key-selection)).
  Asking a node directly for its entries avoids this,
  but reveals to that node that the initiating node uses it.
- **Lost keys**: A node that loses a key whose public key it has published
  cannot process packets built for that key.
  Initiating nodes that still hold the key's entry keep placing the node on paths
  until the key periods of those entries end,
  and the packets they send through it are lost without notice.
  To any monitoring of whether nodes forward packets,
  the loss looks like the node dropping traffic.
  Persisting keys and their replay tables avoids this for a node that restarts ([Section 4.5](#45-start-and-restart)).
  For a node that loses its persistent storage,
  or whose clock jumps ahead ([Section 4.5](#45-start-and-restart)),
  this specification provides no remedy,
  since initiating nodes keep the entries they have already obtained.

## 12. Out of Scope

- Rotation of the mix identity,
  which this specification leaves unchanged.
- Protocols that hold SURBs longer than the bound of [Section 8](#8-single-use-reply-blocks),
  such as hidden-service introduction points.
- Migration from nodes that publish a single unrotated public key,
  beyond not misreading their entries ([Section 5.2](#52-encoding-in-extensible-peer-records)).
- The keys of the libp2p connections between nodes,
  which have their own forward secrecy.

## 13. Future Work

- **Key period in the header**:
  Would remove trial decryption,
  and let long-held SURBs outlive one key period,
  at the cost of a packet format change.
- **Equivocation as evidence**:
  Conflicting entries are verifiable by any node,
  and could be treated as evidence under [Mix Local Reputation](https://github.com/logos-co/logos-lips/pull/463).
- **Targeted refresh**:
  A way for an initiating node to refresh the entries of specific nodes
  without revealing its interest in them.
- **Record size**:
  A more compact encoding of key entries.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [Mix Protocol](./mix.md)
- [Extensible Peer Records](./extensible-peer-records.md)
- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119)

### Informative

- [Logos Mixnet](./logos-mixnet.md)
- [Mix DoS Protection](./mix-dos-protection.md)
- [Mix RLN DoS Protection](./mix-dos-protection-rln.md)
- [Mix Cover Traffic](./mix-cover-traffic.md)
- [Mix Local Reputation (PR #463)](https://github.com/logos-co/logos-lips/pull/463)
- [Katzenpost Mix Network Specification](https://katzenpost.network/docs/specs/mixnet/)
