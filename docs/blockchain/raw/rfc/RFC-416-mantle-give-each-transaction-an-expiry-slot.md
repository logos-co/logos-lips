# [RFC] Mantle: Give each transaction an expiry slot

**Motivation and proposal:** [PR #416](https://github.com/logos-co/logos-lips/pull/416)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-09-01 |
| v2 | Genesis carries a deadline, the window is evaluated against the including block on every path, `TRANSACTION_TTL` is removed as unreachable, and the transaction-hash vectors are regenerated against the current payloads. | 2026-09-02 |
| v3 | Laid the document out like the other specifications: timeline, overview, and the rules under one Construction heading. | 2026-09-09 |
| v4 | Carries the base's removal of restated text. | 2026-09-10 |
| v5 | Rewritten on the current mempool and era rules, with the reasoning moved from the PR description into this RFC document. The sender draws the expiry slot uniformly from `MIN_LIFETIME`, 191 s, to the lifetime it chooses, at most `TRANSACTION_TTL`, which stays. | 2026-11-27 |
|  | Each origin of a transaction has its own lower bound, gossip drops a transaction that is too far ahead before relaying it, retirement and release follow the expiry slot, and Blend carries a transaction only while it is in range for submission. | 2026-11-27 |
|  | Removed the fixed validity window, the rounded deadlines, the removal of `TRANSACTION_TTL` and the note-release rule. | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first. The change builds on the Mempool and Bedrock Eras specifications of this branch's base: the maturity, retirement and release rules of the mempool, and the time to live and retirement grace as era parameters.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle: the field and rule 5](#expiry-slot-in-the-mantle-transaction) | `expiry_slot` under the transaction hash; rule 5 reads the slot of the block that includes the transaction. |
| 2 | Critical | [Mantle Transaction Encoding](#encoding) | `ExpirySlot` as the second field of `MantleTx`, which changes every transaction's encoding and hash. |
| 3 | Critical | **Start here** — [Mempool: the upper bound on gossip](#gossip-and-the-upper-bound) | the bound read by the slot clock; a message dropped before it is relayed or remembered; the one-round hold-back. |
| 4 | High | [Mempool: the lower bound by origin](#admission-and-the-lower-bound) | `least` for each origin, and none on gossip. |
| 5 | High | [Mempool: parameters and constraints](#parameters-and-constraints) | `MIN_LIFETIME` and its derivation; the changed constraints on `RETIREMENT_GRACE`, `BROADCAST_DELAY` and `TRANSACTION_TTL`. |
| 6 | High | [Mempool: retirement, release and reorganisation](#retirement-release-and-reorganisation) | the expiry slot in place of the age-based time to live; which displaced transactions come back. |
| 7 | High | [Mempool: the sender](#the-sender) | the draw, the bounds on `max_lifetime`, and when a transaction is dead. |
| 8 | High | [Blend Protocol](#blend-protocol) | a data message carries a transaction only while it is in range for submission. |
| 9 | Medium | [Genesis](#genesis), [test vectors](#test-vectors) | `expiry_slot = 0` meets rule 5 at slot 0; recomputed hashes. |
| 10 | Medium | [Bedrock Eras](#bedrock-eras) | the mempool fields of the era record meet the Mempool constraints. |
| 11 | Low | [Chores](#chores) | skim. |

[Affected Specifications](#affected-specifications) lists the documents.

# Discussion

## A bound read by the slot clock

The time to live was each node's own: an hour from the moment the transaction reached that node. A bound counted from arrival makes two honest nodes disagree about one transaction. So does a check of the upper bound at admission, because each node runs it at its own moment of arrival. An adversary can then make one chosen node hold and offer a transaction that the other nodes refuse, and a block that carries it names its proposer.

Both bounds are therefore read against the slot clock, and gossip applies the upper bound before it does anything else. A node drops a message whose transaction is too far ahead one round from now, and neither relays the message nor remembers its identity. It holds back a message that comes into range within one round, which covers the largest clock difference between honest nodes.

A network model ran each rule 700 times, with clock offsets, restarts, three encodings of one transaction and era boundaries. Checking the upper bound at admission, after the relay as today's order has it, ended 242 runs with a proposal that some node could not resolve, or with nodes disagreeing about the transaction for up to 3,582 s. Under the draft no run ended so, and nodes disagreed for at most 2 s.

The upper bound uses the `TRANSACTION_TTL` of the era of the expiry slot, so it does not jump at an era boundary. In the same model, a control that uses the era in force fails at the boundary.

## Lower bounds by origin

A transaction that crossed the Blend network arrives with less time left than its sender gave it, so one lower bound cannot hold on every path. Each origin has its own: `MIN_LIFETIME` where the sender submits the transaction, `TRANSACTION_MATURITY` where it leaves the Blend network or is broadcast directly, and only that the expiry slot has not passed on gossip and re-insertion. At selection, the 20 s of maturity let a leader use only a transaction that every node has had time to receive.

A lower bound on gossip would split the nodes. The adversary hands the transaction to a target node in the last second that the bound allows. The target takes it. Its neighbours receive it a moment later and refuse it, and none of them can tell that the target was in time. On the reference code, with 30 honest nodes and 40 network graphs, a bound of `D` seconds on gossip, for `D` of 20 s or more, leaves the target the only node that can include the transaction for `D - 19` slots, and no other node can rebuild its block. Up to 14 s the bound has no effect. Used against every node at once, with 100 nodes of equal stake, a bound of 60 s let 14 % of the blocks won reach the chain that two thirds of the nodes hold, against 70 % without it.

## The minimum lifetime

`MIN_LIFETIME` is the latest time at which a submitted transaction reaches every node, plus `TRANSACTION_MATURITY`, plus the slots in which five blocks are made on average. The latest delivery takes one round until the message is released, `T_M` until the Blend network's deadline passes and the sender broadcasts the transaction directly, and `BROADCAST_DELAY` for that broadcast to reach every node: 21 s. With 20 s of maturity and 150 slots of one second for five blocks at `f = 1/30`, `MIN_LIFETIME` is 191 s. Each second added to `T_M` adds two.

Five blocks make it unlikely that a transaction submitted with the minimum left expires before a block can include it. After the latest delivery this happens with probability 0.60 %, whatever `T_M` is, and after a typical delivery with 0.41 %. Counting one block instead gives 71 s and 35 %, three blocks 131 s and 4.6 %, seven blocks 251 s and 0.08 %.

## The draw

An expiry slot at a fixed distance from submission names the round in which the message was made. In the timing model, the messages an observer cannot tell apart fall from about 9 to 1 when no other transaction travels, and from 45 to 5 at full load.

The sender therefore draws the slot uniformly from `MIN_LIFETIME` to its `max_lifetime`. At the default hour, the slot gives away 0.0015 of the 3.04 bits of uncertainty about the round, 0.005 % of transactions expire unincluded after the latest delivery, the mean lifetime is 31.6 minutes, and 12 % of transactions have less than 10 minutes. At the shortest choice, `2 * MIN_LIFETIME`, the slot gives away 0.027 bits, and 0.093 % expire unincluded after the latest delivery. Drawing from the second half of the chosen lifetime instead gives away 0.0029 bits at the default hour, with a mean lifetime of 45 minutes. The model does not fill blocks, where short lifetimes cost more.

## The one-slot proposer tag

A leader may include a transaction once it has held it for `TRANSACTION_MATURITY`, and each node counts from its own receipt. An adversary that hands a transaction to a target node a moment before every other node can give it an expiry slot that leaves one slot in which the target, and no other node, may include it. A block that carries the transaction then names its proposer, at one fee per identified block. Every node can still rebuild that block.

The tag does not need expiry. A channel inscription is valid only in its sequencer's turn, and a turn may last a single slot, since Mantle sets no lower bound on `posting_timeframe`. On the reference code of the current mempool, the target's block carries such an inscription in its one slot and no other node's block ever does.

No rule built from a transaction's arrival time and its expiry slot leaves fewer than one such slot, and the draft leaves exactly one. A private random wait per block in block building would raise the price of the tag. It does not depend on expiry, and is left to a separate change.

## When a transaction is dead

An expired transaction is not yet dead: a block of a slot up to its expiry slot can still join the canonical chain later. No block can include the transaction once the latest immutable block is past its expiry slot, about 18 hours after the expiry slot. A sender that replaces the transaction before then spends one of its notes in the replacement, so the two conflict and at most one lands.

A rule that keeps a pending transaction's notes locked until it is final or dead is left out. It would forbid that replacement, and it would lock the notes of a failed transaction for about 18 hours after its expiry. A wallet that spends a pending note in another transaction only makes the two conflict, so it cannot pay twice.

## Compatibility

The field changes the encoding and the hash of every Mantle Transaction. Bedrock has no genesis yet, so nothing needs migrating.

Every proof that can pay a fee signs the transaction hash, so only the signers can change a transaction's expiry slot. Operation IDs, note IDs and channel tips do not contain the transaction hash, so a transaction signed again with a new expiry slot leaves the transactions that depend on it valid.

## Open questions

- The one-slot tag stays at one fee per identified block until block building prices it.
- A node that discards a queued transaction because its expiry slot came too near tells the submitter nothing.
- A sender whose quota allowance comes `w` seconds earlier than it assumed finds its expiry slot more than `TRANSACTION_TTL` ahead with probability `w/3410` at the default lifetime. It must then wait until the slot is in range, which shows the slot.
- Outside this change, Mantle sets no lower bound on `posting_timeframe`, and the round-robin computation divides by it, although `0` stands for infinity.

# Details

## Expiry slot in the Mantle Transaction

`MantleTx` gains `expiry_slot`, the last slot at which a block may include the transaction. `mantle_txhash` covers it. Its sender chooses it as [Expiry Slot](../mempool.md#expiry-slot) specifies.

```diff
 class MantleTx:
     fork_digest: hash
+    expiry_slot: SlotNumber
     ops: list[Op]
```

[Validation](../bedrock-v1.1-mantle-specification.md#validation) takes the slot of the block that includes the transaction, and adds rule 5:

```python
block_slot: SlotNumber  # new: slot of the block that includes the transaction

# 5. new: the slot of the block does not exceed the expiry slot
assert block_slot <= signed_tx.tx.expiry_slot
```

## Encoding

[Mantle Tx](../mantle-transaction-encoding.md#mantle-tx) encodes the expiry slot after the fork digest:

```diff
-MantleTx   = ForkDigest OpCount *Op
+MantleTx   = ForkDigest ExpirySlot OpCount *Op
 ForkDigest = Hash32
+ExpirySlot = UINT64
 OpCount    = Byte
```

## Mempool

### The sender

A sender should set the `expiry_slot` of its transaction to `draw_expiry_slot(submission, max_lifetime)` ([Expiry Slot](../mempool.md#expiry-slot)):

```python
def draw_expiry_slot(submission: Timestamp, max_lifetime: uint64 = TRANSACTION_TTL) -> SlotNumber:  # new
    return uniform(slot_of_time(submission + MIN_LIFETIME), slot_of_time(submission + max_lifetime))
```

- `submission` is the time at which the sender expects to generate the data message that carries the transaction, or to submit the transaction to a node.
- `max_lifetime` is the longest time after `submission` for which the sender lets a block include the transaction. It is at least `2 * MIN_LIFETIME` and at most `TRANSACTION_TTL`.
- `uniform(a, b)` draws a slot uniformly from `a` to `b`, both included. `slot_of_time` is that of [Era Boundaries](../bedrock-eras.md#era-boundaries).

No block can include a transaction once the slot of the [Latest Immutable Block](../cryptarchia-v1-protocol.md#latest-immutable-block) is after its expiry slot. Until then, a sender that replaces the transaction must spend one of the transaction's notes in the replacement.

### Parameters and constraints

[Parameters](../mempool.md#parameters) adds `MIN_LIFETIME`, and `TRANSACTION_TTL` and `RETIREMENT_GRACE` count to and from the expiry slot:

```diff
-TRANSACTION_TTL: uint64 = 60 * 60                     # seconds a transaction may stay pending before it is retired
-RETIREMENT_GRACE: uint64 = 10 * 60                    # seconds a transaction that no canonical block carries stays resolvable after its age reaches TRANSACTION_TTL
+TRANSACTION_TTL: uint64 = 60 * 60                     # longest time, in seconds, that a transaction may have left until its expiry slot
+RETIREMENT_GRACE: uint64 = 10 * 60                    # seconds a transaction that no canonical block carries stays resolvable after its expiry slot
 BROADCAST_DELAY: uint64 = 5                           # seconds a block proposal takes to reach every node once it leaves the Blend network
 TRANSACTION_MATURITY: uint64 = T_M + BROADCAST_DELAY  # seconds of age at which a transaction is mature
+MIN_LIFETIME: uint64 = SLOT_LENGTH + 2 * TRANSACTION_MATURITY + 5 * f.den // f.num * SLOT_LENGTH  # shortest time, in seconds, that a transaction may have left until its expiry slot when its sender submits it
 # ... unchanged parameters elided
```

- [Notation](../mempool.md#notation) adds `f`, the `slot_activation_coeff` of the era in force, and `SLOT_LENGTH`, the slot length of the era in force in seconds.
- A submitted transaction reaches every node at the latest one round, plus `T_M`, plus `BROADCAST_DELAY` after its submission, when its sender broadcasts it directly. `MIN_LIFETIME` adds `TRANSACTION_MATURITY` and `⌊5/f⌋` slots, and is 191 s with `T_M` at 15 rounds of one second and `f` at 1/30.
- The `TRANSACTION_TTL` of a transaction is that of the era of its expiry slot. `RETIREMENT_GRACE` is that of the era in force.

The constraints change:

| Constraint | Was | What breaks without it |
| --- | --- | --- |
| `RETIREMENT_GRACE` exceeds one round plus `TRANSACTION_MATURITY`. | It exceeded the gossip time, plus the time between two consecutive blocks, plus `TRANSACTION_MATURITY`. | A node can release a transaction before a proposal that selected it in its expiry slot arrives. |
| `BROADCAST_DELAY` is not less than the time a block proposal or a transaction takes to reach every node by gossip. | A block proposal only. | A transaction submitted with `MIN_LIFETIME` left can mature later than `MIN_LIFETIME` counts. |
| `TRANSACTION_TTL` is at least `2 * MIN_LIFETIME`. | `TRANSACTION_MATURITY` was less than `TRANSACTION_TTL`. | A sender can choose no `max_lifetime`. |

### Admission and the lower bound

[Transaction Admission](../mempool.md#transaction-admission) refuses a transaction whose expiry slot is not in range, after the duplicate check and before the claim check. `admit` takes the shortest time the transaction must have left, `least`, and admission now reads the node's clock:

```diff
-def admit(mempool, encoded: bytes) -> Result:
+def admit(mempool, encoded: bytes, least: uint64) -> Result:
     # ... size, decoding, fork digest and preverify checks unchanged
     if key in mempool.pending or key in mempool.included:
         return Duplicate(key)

+    if not expiry_in_range(tx.tx.expiry_slot, least):
+        return Reject(ExpiryOutOfRange)
+
     if claim_expired(mempool, tx):
         return Reject(ExpiredClaim)
```

```python
def too_far(expiry_slot: SlotNumber, at: Timestamp) -> bool:  # new
    return expiry_slot > slot_of_time(at + ttl(expiry_slot))

def expiry_in_range(expiry_slot: SlotNumber, least: uint64) -> bool:  # new
    return slot_of_time(now() + least) <= expiry_slot and not too_far(expiry_slot, now())
```

`ttl(sl)` is the `TRANSACTION_TTL` of the era of slot `sl`. `least` depends on the transaction's origin:

| Origin | `least` |
| --- | --- |
| The Node API, or the node's own services | `MIN_LIFETIME` |
| A data message, or a direct broadcast in its place | `TRANSACTION_MATURITY` |
| Gossip or re-insertion | `0` |

A transaction broadcast directly in place of a data message is a local submission. An expiry slot is in range for submission while `expiry_in_range(expiry_slot, MIN_LIFETIME)` holds, and too near for submission once it is before `slot_of_time(now() + MIN_LIFETIME)`.

### Gossip and the upper bound

[Dissemination](../mempool.md#dissemination) applies the upper bound before a node relays a message or remembers its identity:

- A node drops a received message if `too_far` holds for its transaction's expiry slot one round from now. It neither relays the message nor remembers its identity.
- A node holds back a received message if `too_far` holds now but not one round from now. It handles the message as received once `too_far` no longer holds.
- One round is more than the largest clock difference between honest nodes, `T_C` of [Transition Period](../blend-protocol.md#transition-period).

### Retirement, release and reorganisation

[Expiry](../mempool.md#expiry) retires a pending transaction whose `expiry_slot` is before the current slot, `slot_of_time(now())`, in place of one whose age reaches `TRANSACTION_TTL`.

[Release](../mempool.md#release) frees a retained transaction that no canonical block carries `RETIREMENT_GRACE` after the start of its expiry slot:

```diff
-        if claim_expired(mempool, mempool.bodies[key]) or (
+        tx = mempool.bodies[key]
+        if claim_expired(mempool, tx) or (
                 key not in mempool.included
-                and now() - mempool.admitted_at[key] >= TRANSACTION_TTL + RETIREMENT_GRACE):
+                and now() >= slot_start(tx.tx.expiry_slot) + RETIREMENT_GRACE):
             release(mempool, key)
```

[Reorganisation](../mempool.md#reorganisation) re-admits a displaced transaction as gossip does, with `least` of `0`. It skips one that it never held and whose expiry slot was too far ahead at the start of the displaced block's slot:

```diff
             mempool.included.discard(key)
-            # A transaction is at least as old as the start of the slot of a block that carries it.
-            admitted = mempool.admitted_at.get(key, slot_start(block.header.slot))
-            if now() - admitted >= TRANSACTION_TTL:
+            # Without this, leaving a long fork would re-admit what old blocks carried.
+            if key not in mempool.bodies and too_far(tx.tx.expiry_slot, slot_start(block.header.slot)):
                 continue
-            admit(mempool, encode_signed_mantle_tx(tx))
+            admit(mempool, encode_signed_mantle_tx(tx), least=0)
```

In [Block Building View](../mempool.md#block-building-view), `apply_transaction` returns `None` when a transaction is not valid against the state in a block with the given header, since rule 5 reads the block's slot.

## Blend Protocol

Both Generation lists of [Message Lifecycle](../blend-protocol.md#message-lifecycle) let a node put a transaction in a data message only while its expiry slot is in range for submission:

```diff
-3. A node has a Mantle transaction to submit and holds an unused quota allowance. The payload of the message is the transaction.
+3. A node has a Mantle transaction to submit whose expiry slot is in range for submission, and holds an unused quota allowance. The payload of the message is the transaction.
```

A node discards a transaction to submit once its expiry slot is too near for submission.

## Genesis

The [Genesis Mantle Transaction](../bedrock-genesis-block.md#genesis-mantle-transaction) expires at the Genesis slot, so rule 5 holds at slot 0:

```diff
 GENESIS_MANTLE_TX = MantleTx(
     fork_digest=bytes(32),
+    expiry_slot=0,
     ops=[STAKE_DISTRIBUTION, GENESIS_INSCRIPTION] + SERVICE_DECLARATIONS,
 )
```

## Bedrock Eras

[Era Parameters](../bedrock-eras.md#era-parameters) requires the `transaction_ttl_in_seconds` and `retirement_grace_in_seconds` of every record to meet the constraints of the Mempool's Parameters, in place of a lower bound of 1.

## Test vectors

Both transaction-hash vectors of Mantle's [Test Vectors](../bedrock-v1.1-mantle-specification.md#test-vectors) encode the expiry slot `0x0102030405060708`. Cryptarchia's [Test Vectors](../cryptarchia-v1-protocol.md#test-vectors) are recomputed from them: the eleven leaves, the Merkle root, both body roots and the block ID. A script reproduced the 19 values published before the change before computing the new ones, and two further independent scripts agree on them.

## Chores

- Every `MantleTx` in Mantle's examples and in the atomic transfer example of the Cross-Channel Messaging template sets `expiry_slot`. The template's note on coordination failure asks the sequencers to finish before the expiry slot.
- Mantle's [Message Ordering](../bedrock-v1.1-mantle-specification.md#message-ordering) says that honest channel messages are re-included in a new transaction when the one that carried them has expired, and that the inscriptions a sequencer keeps posting do not invalidate a pending reconfiguration.
- The Mempool's Introduction, Overview and Protocol describe the expiry slot, its admission sequence diagram lists the expiry check, and its unused notation row for `k` is removed.
- Revision rows: Mantle 1.21.0, Mantle Transaction Encoding 1.13.0, Mempool 1.3.0, Blend Protocol 1.10.0, Bedrock Genesis Block 1.4.0, Cryptarchia Protocol 1.4.1, Bedrock Eras 1.2.0, and the Cross-Channel Messaging template 1.2.2.

# Implementation

- [ ]  Add `expiry_slot` to the Mantle Transaction: field, codec, hash, builder, genesis check and fixtures (`core/src/mantle/transactions`).
- [ ]  Check rule 5 in the ledger beside the fork digest check, so that block building finds an expired transaction inapplicable.
- [ ]  Pass each transaction's origin to mempool admission for `least`, make the era timing mandatory, index pending transactions by expiry slot, and release by expiry slot (`services/tx-service`).
- [ ]  Drop a too-far message on the mempool topic in the inbound transform, which in libp2p-gossipsub returns before the duplicate cache is written, and hold back one that comes into range within a round through message validation.
- [ ]  Let the Blend queue see the expiry slot, check it when the data message is generated, and discard a transaction that is too near (`services/blend`).
- [ ]  Draw the expiry slot when signing, in the wallet, proof of work, SDP, API, C bindings and zone SDK.
- [ ]  In the wallet, make a replacement spend one of the replaced transaction's notes until that transaction is dead, in place of freeing its inputs after a number of blocks.
- [ ]  Recompute the fixtures and test vectors, and test admission for each origin, the gossip drop and hold-back, retirement, release and re-insertion, across an era boundary.
- [ ]  Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | `expiry_slot`, Validation rule 5, examples, test vectors |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | `ExpirySlot` |
| [Mempool](../mempool.md) | Modified | the draw, the lower bound by origin, the upper bound on gossip, retirement and release by expiry slot |
| [Blend Protocol](../blend-protocol.md) | Modified | a data message carries a transaction only while it is in range for submission |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | `expiry_slot` of 0 |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | block test vectors |
| [Bedrock Eras](../bedrock-eras.md) | Modified | the mempool fields meet the Mempool constraints |
| [\[Template\] Cross-Channel Messaging](../template-cross-channel-messaging.md) | Modified | `expiry_slot` in the atomic transfer example |
