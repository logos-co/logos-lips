# [RFC] SDP: Identify declarations by service and `zk_id`

**Motivation and proposal:** [PR #407](https://github.com/logos-co/logos-lips/pull/407)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-08-19 |
| v2 | Recorded that the change is pre-genesis, so no state migration is required | 2026-08-20 |
| v3 | Simplified to one declaration per service, each backed by its own note; the per-service state map, the `ServiceType` field on the active and withdraw messages, and the per-note declaration set are all removed | 2026-08-20 |
| v4 | The `provider_id` is unique across the registry rather than within a service | 2026-08-20 |
| v5 | `WithdrawMessage` drops the redundant note; the genesis declarations are aligned with the declaration protocol | 2026-08-20 |
| v6 | The unspecified locking period is removed in favour of the existing withdrawal delay, and `created` with it | 2026-08-20 |
| v7 | The active set and the initial value of `active` are specified, closing two rules that existed only in the reference implementation | 2026-08-20 |
| v8 | Rebased onto master: adopts the `service_note` naming, renumbers every revision, and removes four references to `declaration_id` that master added meanwhile. The specifications are trimmed to rules, values and derivations, each stated once — the reasoning behind them now lives only here | 2026-09-01 |
| v9 | Reconciles the declaration message field order across the three documents, prices the identifier checks the proposal introduces, and resolves three statements the change left stale | 2026-09-02 |
| v10 | The declarations are indexed by provider identity, so declaring is three lookups and no step of it grows with the registry | 2026-09-02 |
| v11 | Merged master, which defined what `active` and `withdraw_at` record; this PR adopts that definition, and `created` returns as the anchor of `active`. From review, uniqueness is checked within a service rather than across the registry: the registry is one map per service, identifiers may be reused across services, a note may back one declaration per service, and the active and withdraw messages name the service again. Documents the diff leaves untouched are dropped from the affected list | 2026-09-09 |
| v12 | The `declaration_id` is retained and derived as `Hash(service \|\| zk_id)`: the registry is one map keyed by it, `DeclarationInfo` carries `service` and `zk_id` again, and the active and withdraw messages address it as before. `SDPActive` returns to its previous wire form and keeps its `op_id`; `SDPWithdraw` still drops the note. The `declaration_id` test vector is regenerated, and the key-types document is no longer touched | 2026-09-11 |
| v13 | Merged master, which removes a declaration at `withdraw_at + 1` so that its last served epoch is rewarded; this PR adopts that and renumbers every revision | 2026-09-11 |
| v14 | Restored the conditional note unlock in the SDP Withdraw cost, which v3 had folded into the removal step, and dated the release by `withdraw_at + 1` | 2026-09-11 |
| v15 | Restored the `DeclarationInfo` field order of master in the declaration protocol; only `DeclarationMessage` was meant to be reordered | 2026-09-11 |
| v16 | `DeclarationInfo` lists its fields in the order of the implementation's `Declaration` struct, in both documents | 2026-09-11 |
| v17 | `declarations` holds one map per service keyed by `declaration_id`, as the implementation does, and a declaration named by its identifier alone is found by searching the services. The note on the regenerated test vectors is dropped from Mantle | 2026-09-11 |
| v18 | The Query section is reduced to the two queries that have a consumer, served from finalized state with an error for an absent result; the history, `provider_id`, `ServiceParameters` and `MinStake` queries are recorded as an open item | 2026-09-11 |
| v19 | Serialization stated precisely: each message maps to its Mantle Operation and encoding production, signatures cover the transaction hash, and the `declaration_id` hash is BLAKE2b with a 32-byte digest, unkeyed, over the 33-byte `ServiceType \|\| ZkId` preimage. The locator-list paragraph, which restated the `Locators` production, is removed | 2026-09-11 |
| v20 | Merged master and renumbered the Blend and Mantle Transaction Encoding revisions. From review, a `nonce` is split into a `lifecycle_epoch`, which must be the `created` epoch of its declaration, and a `sequence`, as in the reference implementation draft, so a message signed for a removed declaration is not valid for a later one with the same `declaration_id`. The Motivation no longer calls `locators` mutable, the `SDP_WITHDRAW` `op_id` and the combined transaction, now with eleven operations, are regenerated, the Withdraw example pays its fee from a note that is not the service note, and the Withdraw and Active examples build their `nonce` from the `lifecycle_epoch` and a `sequence` | 2026-10-01 |
| v21 | Merged master, which re-measured the Ed25519 verification cost; the Mantle and Gas Cost Determination revisions are renumbered past it | 2026-10-05 |
| v22 | Split the submission into this RFC document and a PR description that holds only the Motivation, the Proposal and the status tracker, per the current template, and retitled it `[RFC] SDP: Identify declarations by service and zk_id` | 2026-10-06 |
|  | Removed what the diff no longer supports: the Details entry on re-anchoring the locator-list serialization, which the specification now drops; the claim that the initial value of `active` is new, which master defines; the chore on the `ActiveMessage` metadata type, which the diff does not change; and the note on two broken anchors unrelated to this change | 2026-10-06 |
|  | Corrected the revisions the Motivation cites, the nonce and Declare snippets against master, and the Implementation task on when a withdrawn declaration leaves the active set. Moved the test vectors into Details, and added the `DeclarationInfo` field order to Chores, nonce values to Backwards compatibility, and the queries to the Reviewer Orientation | 2026-10-06 |

## Reviewer Orientation

Read the PR's Motivation first. The rewarding and quota constructions are assumed and unchanged.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Service Declaration Protocol](#affected-specifications): [the `declaration_id`](#1-the-declaration_id-is-derived-from-the-service-and-the-zk_id) | `declaration_id = Hash(service \|\| zk_id)`; check that nothing still needs the identifier to commit to `provider_id` or `locators` |
| 2 | Critical | [Service Declaration Protocol](#affected-specifications): [uniqueness](#2-uniqueness-is-per-service) | `zk_id`, `provider_id` and the service note are unique within a service and may be reused across services; confirm that the reward and quota constructions, both per service, need nothing stronger |
| 3 | Critical | **Start here** — [Service Declaration Protocol](#affected-specifications): [the nonce](#3-a-nonce-belongs-to-one-declaration) | a message signed for a removed declaration must fail against a later one with the same `declaration_id`; check the `created + 3` bound that keeps two declarations apart |
| 4 | Critical | [Mantle Transaction Encoding](#affected-specifications): [`SDPWithdraw`](#4-sdpwithdraw-drops-the-note) | 72 → 40 bytes, the note taken from the declaration; not backwards compatible |
| 5 | High | [Mantle](#affected-specifications): [the SDP operations](#5-the-mantle-sdp-operations-follow) | `providers` and `service_notes` are per service; confirm that epoch finalization frees all three identifiers of a removed declaration, and a note only once no service holds it |
| 6 | High | [Service Declaration Protocol](#affected-specifications): [the active set](#6-the-active-set-is-defined) | `active + inactivity_period >= n` and `n < withdraw_at`, evaluated against the epoch the set is derived for; check the boundary against [Message Timing](../bedrock-service-declaration-protocol.md#message-timing) |
| 7 | High | [Service Declaration Protocol](#affected-specifications): [the queries](#7-the-queries-are-reduced-to-two) | two queries, answered from the finalized state, with an error for an absent result |
| 8 | Medium | [Mantle](#affected-specifications): [test vectors](#8-test-vectors) | the `declaration_id`, `SDP_WITHDRAW` and combined-transaction vectors are regenerated |
| 9 | Low | [Chores](#chores) | skim |

# Discussion

## What the narrower preimage buys

The three corrections the PR's Motivation cites disappear rather than being carried forward:

- Per-service uniqueness of the `zk_id` was a rule that had to be checked because the hash could not guarantee it. The identifier is now the hash of the service and the `zk_id`, so two declarations of one service cannot share a `zk_id` without sharing a `declaration_id`. The existence check on the identifier is the rule.
- The length prefix and the canonical encodings were needed so that the preimage bound what it committed to. The preimage is now two fixed-size components, one byte and a 32-byte key. There is no list to length-prefix and no encoding left to choose.

The `locators` are no longer part of the identity of a declaration: a validator that redeclares with a new address keeps its `declaration_id`.

## A stable identifier needs a nonce scoped to the declaration

A stable `declaration_id` comes back unchanged when a validator withdraws and later redeclares with the same `zk_id` in the same service. With a plain counter, the stored `nonce` restarts at 0. A signed active or withdraw message for the earlier declaration that never reached the chain then passes the check `nonce > stored` against the new declaration. A replayed withdrawal removes the validator from the service. The replay needs only the fee input of the stale transaction to be unspent. A wallet cannot prevent it, because it cannot invalidate a message it has already signed.

The 64-bit `nonce` is now split: the high 32 bits are a `lifecycle_epoch` and the low 32 bits a `sequence`. The stored `nonce` starts with `created` as its `lifecycle_epoch` and a `sequence` of 0. A message is valid only if its `lifecycle_epoch` is the `created` of the declaration it addresses and its `sequence` is greater than the stored one. A declaration is removed at `withdraw_at + 1`, which is no earlier than `created + 3`, so two declarations with the same `declaration_id` never share a `created` epoch. The wire form is unchanged.

The alternatives were rejected:

- carrying `created` in the active and withdraw messages costs bytes on every message;
- keeping each nonce after removal leaves state that never shrinks;
- putting `created` into the preimage makes the identifier change on redeclaration again.

## Why the identifier is kept

The messages, the event index, the queries and the reference implementation address a declaration by one 32-byte identifier. Deriving it from the service and the `zk_id` keeps that interface unchanged, and a client computes it from two values it already holds, without a lookup. `SDPActive` keeps its wire form and its test vector.

## Why uniqueness is per service

Uniqueness across the registry would give the simplest storage layout: one map, three lookups. Nothing downstream needs it. A reward distribution covers one service, and the Proof of Quota core root is built over one service's providers, so no consumer needs a `zk_id` to be unique beyond its service. The same holds for the `provider_id`, which Blend resolves against the Blend declarations, and for the service note, which a validator may put up for each service it provides, as it can on master.

The service is part of the identifier rather than of the messages. `Hash(service || zk_id)` names a declaration on its own, so the active and withdraw messages keep their shape. A node that holds only the identifier finds the declaration by searching the services, as the implementation does today. A validator providing several services keeps one `zk_id`, one network identity and one note, and a future service type adds no identifiers.

## The withdrawal delay is the locking period

The Overview said that a node may withdraw "after the service-specific locking period", and the gas analysis priced withdrawal as verifying "that the note has exceeded its lock period". No such period was defined. `inactivity_period` is the only period `ServiceParameters` carries, the **Withdraw** action listed no criterion for a lock, and the reference implementation checks the declaration, the note binding, the signature and the nonce and nothing else. Both statements are removed.

The existing withdrawal delay does what a locking period would. A node that withdraws in epoch `e` has `withdraw_at = e+2`, stays in the active set through `e+1`, and its note stays held until `e+3`, the epoch in which its last served epoch is rewarded and the declaration is removed. The collateral is held for as long as the node can still serve or be paid. There is no slashing in these specifications or in the implementation, so no penalty needs a longer window, and the minimum stake resists Sybil attacks by what is held at the same time rather than for how long.

Should slashing be introduced later, or a service want a minimum commitment, the rule would need a parameter in `ServiceParameters`, measured from `created`.

## Why the active set needed specifying

The specification described a snapshot of the registry and stopped there, which reads as though membership is whatever the snapshot block contained. It is not. A declaration withdrawn in epoch `e` leaves every service's set at `e+2` and has its note released at `e+3`. If membership were the raw snapshot, that declaration would stay in the active set for the length of the snapshot lag after it should have left. It could provide the service, and prove membership through the Proof of Quota core root, with no stake at risk. The reference implementation avoids this by filtering the snapshot against the epoch the set is derived for, not the epoch it was taken in. Master states the withdrawal exclusion in **Withdraw**; this PR keeps the whole derivation in **Active Set** and links to it from **Withdraw**.

## The query interface is reduced to what nodes serve

The Query section listed eleven queries. None exists in the reference implementation under its name or shape. The node serves the current declarations and the current epoch's snapshot, both keyed by `declaration_id` and without an epoch parameter, and looks a declaration up by identifier or by service internally. Nothing in these specifications consumes the rest. There is no lookup by `provider_id`, since Blend's neighbor distinction is a membership test over the service's declarations, no epoch-addressed history, and `ServiceParameters` and `MinStake` are node configuration.

The section now requires the two queries a consumer exists for, keeps the rule that they answer from the finalized state, and keeps the error for an absent result. The implementation meets neither rule today, so both are implementation tasks.

**Open question.** The dropped queries — the `…(epoch)` and `…Since(epoch)` history forms, the `provider_id` lookups, and the `ServiceParameters` and `MinStake` queries — are to be specified with the node API if a consumer appears.

## Backwards compatibility

This is a breaking change:

- **Serialization.** `SDPWithdraw` loses `ServiceNoteId` and goes from 72 to 40 bytes, so an old decoder rejects it. `SDPActive` and `SDPDeclare` keep their wire form.
- **Nonce values.** The `nonce` keeps its 64-bit wire form, but its high 32 bits must now be the `created` epoch of the declaration. A client that counts a declaration's nonces from 1 is rejected for any declaration created after epoch 0.
- **Ledger state.** The `declaration_id` of every declaration changes with its preimage, and the note index changes shape. State written under the old layout cannot be read under the new one.

All three are pre-genesis changes. No chain state exists under the old layout and no operation has been encoded under the old grammar, so there is nothing to migrate and no coordinated upgrade to schedule. The change must merge before genesis, and any implementation or test vector written against the old preimage is updated rather than supported alongside the new form.

# Details

## 1. The `declaration_id` is derived from the service and the `zk_id`

In [Declaration Storage](../bedrock-service-declaration-protocol.md#declaration-storage), the preimage drops `provider_id` and `locators`, and `declarations` is stated as the map it is:

```diff
-declaration_id = Hash(service||provider_id||zk_id||locators)
+declaration_id = Hash(service||zk_id)

-declarations: list[declaration_id]
+declarations: dict[ServiceType, dict[DeclarationId, DeclarationInfo]]
```

- The preimage is the one-byte `ServiceType` production followed by the 32-byte `ZkId` production, 33 bytes in all.
- `Hash` is BLAKE2b with a 32-byte digest, unkeyed, without salt or personalization.
- A declaration covers exactly one service, and `declarations` holds one map per service, keyed by `declaration_id`.

A new **Serialization** subsection maps each message to its Mantle Operation and its encoding production, with the fields in message order: `DeclarationMessage` to `SDP_DECLARE` and `SDPDeclare`, `ActiveMessage` to `SDP_ACTIVE` and `SDPActive`, and `WithdrawMessage` to `SDP_WITHDRAW` and `SDPWithdraw`. The signatures a message requires are carried in the Operation's proof and cover the Mantle transaction hash.

## 2. Uniqueness is per service

[Identifier Uniqueness](../bedrock-service-declaration-protocol.md#identifier-uniqueness) becomes three rules. Within the declarations of one service, each of `zk_id`, `provider_id` and `service_note_id` is bound to at most one `DeclarationInfo`. The `zk_id` rule is the uniqueness of the `declaration_id`. The same identifier may be bound in several services, and becomes available for reuse in a service once its declaration there is removed.

Declare validation carries the rule as one criterion that links to that section:

```diff
-- The `declaration_id` is unique.
-- The `provider_id` and the `zk_id` are each unique in the context of the `service` (as defined in [Identifier Uniqueness](#identifier-uniqueness)).
+- The `zk_id`, the `service_note_id` and the `provider_id` are each unbound in the `service_type` of the message ([Identifier Uniqueness](#identifier-uniqueness)).
```

## 3. A nonce belongs to one declaration

[Declaration Storage](../bedrock-service-declaration-protocol.md#declaration-storage) states the rule once. The active and withdraw message definitions, and the Active and Withdraw checks, link to it:

```diff
-- The `nonce` must be set to 0 for the declaration message and must increase monotonically by every message sent for the `declaration_id`.
+- `nonce` is the `nonce` of the latest accepted active or withdraw message, initialised with `created` as its `lifecycle_epoch` and a `sequence` of 0.
+
+A `Nonce` is a 64-bit unsigned integer, `lifecycle_epoch · 2^32 + sequence`:
+
+- `lifecycle_epoch` is the high 32 bits, an [`EpochNumber`](cryptarchia-v1-protocol.md#epoch);
+- `sequence` is the low 32 bits.
+
+An active or withdraw message is valid only if its `nonce`:
+
+- has the `created` of the `DeclarationInfo` as its `lifecycle_epoch`;
+- has a `sequence` greater than the `sequence` of the `nonce` of the `DeclarationInfo`.
+
+Two declarations with the same `declaration_id` never share a `created` epoch, because a declaration is removed no earlier than epoch `created + 3` ([**Withdraw**](#withdraw)). If they could, a message signed for the earlier declaration would be valid for the later one.
```

[Mantle](../bedrock-v1.1-mantle-specification.md#service-declaration-protocol-sdp-operations) follows. `SDP_ACTIVE` checks `active.nonce` the same way `SDP_WITHDRAW` checks `withdraw.nonce`:

```diff
 # SDP_DECLARE execution
-nonce=0
+nonce=current_epoch << 32,  # lifecycle_epoch = created, sequence = 0

 # SDP_WITHDRAW validation
-assert withdraw.nonce > declare_info.nonce
+assert withdraw.nonce >> 32 == declare_info.created
+assert withdraw.nonce & 0xFFFFFFFF > declare_info.nonce & 0xFFFFFFFF
```

The Withdraw and Active examples build their `nonce` as `alice_declaration_created << 32 | 1579532`.

## 4. `SDPWithdraw` drops the note

In [Mantle Transaction Encoding](../mantle-transaction-encoding.md#sdp-operations):

```diff
-SDPWithdraw   = DeclarationId Nonce ServiceNoteId
+SDPWithdraw   = DeclarationId Nonce
 DeclarationId = Hash32
```

`WithdrawMessage` drops the field in the declaration protocol and in Mantle:

```diff
 class WithdrawMessage:
     declaration_id: DeclarationId
-    service_note_id: NoteId
     nonce: Nonce
```

A declaration holds exactly one note, so the declaration determines it. Carrying the note as well meant Mantle had to assert that the two agreed, and the reference implementation carries an `InvalidServiceNote` error whose only purpose is that mismatch. `SDP_WITHDRAW` now takes the note from the declaration and asserts that it is unspent and held by that declaration in its service. `ServiceNoteId` stays defined for `SDPDeclare`, and `SDPActive` and `SDPDeclare` are unchanged.

## 5. The Mantle SDP operations follow

The `ServiceNote` structure gives way to two indexes, each keyed by an identifier that is not the declaration's own:

```diff
-service_notes: dict[NoteID, ServiceNote]
-declarations: dict[DeclarationID, DeclarationInfo]
-
-class ServiceNote:
-    declarations: set[DeclarationID]
+service_notes: dict[NoteId, dict[ServiceType, DeclarationId]]
+providers: dict[ServiceType, dict[Ed25519PublicKey, DeclarationId]]
+declarations: dict[ServiceType, dict[DeclarationId, DeclarationInfo]]
```

`service_notes` stays keyed by note, so the Ledger's spendability check remains one membership test. Its value records the declaration the note backs in each service. `SDP_DECLARE` validation keeps the existence check on the identifier, which is now the `zk_id` rule, and adds the two index lookups:

```diff
-assert declaration_id(declaration) not in declarations
+declare_id = declaration_id(declaration)
+assert declare_id not in declarations[declaration.service_type]
+assert declaration.service_type not in service_notes.get(declaration.service_note_id, {})
+assert declaration.provider_id not in providers[declaration.service_type]
```

- `SDP_DECLARE` execution writes both index entries and stores the declaration under its service and `declaration_id`.
- `SDP_ACTIVE` and `SDP_WITHDRAW` find a declaration by searching the services for its identifier, through a new `find_declaration` helper.
- SDP Epoch Finalization releases the note for the service and the provider identity, drops the note's entry once no service holds it, and removes the declaration. The note is spendable again once no service holds it.

## 6. The active set is defined

A new [Active Set](../bedrock-service-declaration-protocol.md#active-set) section follows the storage and uniqueness rules whose fields it reads. The active set of a service for an epoch `n` keeps that service's declarations, in the snapshot read for `n`, for which `active + inactivity_period >= n` and for which `withdraw_at` is `None` or `n < withdraw_at`. Both conditions are evaluated against `n`, not against the epoch the snapshot was taken in. The withdrawal exclusion that master states in **Withdraw** moves into this section, and **Withdraw** links to it ([Discussion](#why-the-active-set-needed-specifying)).

## 7. The queries are reduced to two

[Query](../bedrock-service-declaration-protocol.md#query) requires `GetDeclarationInfo(declaration_id)` and `GetAllDeclarationInfo(service_type)`. Both answer from the finalized state, and a query for a `declaration_id` or a `service_type` the finalized state does not hold returns an error. `GetAllDeclarationInfo` takes a `service_type` in place of an epoch, and the other nine queries are removed ([Discussion](#the-query-interface-is-reduced-to-what-nodes-serve)).

## 8. Test vectors

In [Mantle](../bedrock-v1.1-mantle-specification.md):

- The **Declaration Id** vector is regenerated for the preimage `service || zk_id`, from the same `SDP_DECLARE` fields. The `declaration_id` is `0x67fa7d1fe7f1391195fdd479bba30dd97c9e6d2e1525436ac2427f2bf8567a0d`.
- The `SDP_WITHDRAW` payload drops the note, leaving 40 bytes. Its `op_id` is `0xa9f938ca71aa93a05f19aff553757b2707041daf0630b7c2d6d3da0705be8aaa`.
- The transaction with one of each operation carries all eleven Operations, `CLAIM_POW_REWARD` included, so its operation count is `0x0b`. Its hash is `0x4e1307fb13446da7aba6b60f5d8bd899a6d5f68dab8993d00c671f3ccb0ffc6c`. The vector on master carries ten.
- `SDP_ACTIVE` is unchanged and keeps its `op_id`.

## Chores

- [Service Declaration Protocol](../bedrock-service-declaration-protocol.md):
  - **Locators** no longer lists the `declaration_id` preimage among the places the canonical form is used. Its statement that the canonical form "makes deterministic ID generation work consistently" is reduced to the rule it carried: parse the string form into the binary form before serialization. Its paragraph on serializing a list of locators restated the `Locators` production of the encoding and is removed.
  - The other Declare criteria name what they check: an unspent note that meets the minimum stake threshold, the private key of the `provider_id`, and a non-empty list of at most 8 locators. The `nonce` criterion is removed, since `DeclarationMessage` carries no `nonce`.
  - `DeclarationMessage` lists `service_note_id` after `zk_id`, the order Mantle and the wire grammar use. `DeclarationInfo` lists its fields in the order of the implementation's `Declaration` struct, in both documents, and each field description states what the field holds.
  - The Overview no longer promises a locking period ([Discussion](#the-withdrawal-delay-is-the-locking-period)).
- [Mantle](../bedrock-v1.1-mantle-specification.md): the note check in `SDP_DECLARE` built a list of `DeclarationInfo` objects and tested a `ServiceType` for membership in it, so it could never fail. The `SDP_DECLARE` execution snippet was not valid Python. The Withdraw example paid its fee from the service note, which stays held until the declaration is removed; it now pays from a separate note. "Unlocking" the stake is now "releasing" the service note, the term the declaration protocol uses.
- [Analysis: Gas Cost Determination](../analysis-gas-cost-determination.md): the SDP Withdraw cost priced a lock-period check that does not exist, and described removing a declaration from a note's set. The SDP Declaration cost lists the `provider_id` lookup beside the existence check, and the index entries declaring writes.
- [Genesis Block](../bedrock-genesis-block.md): the initial service declarations named `ServiceType.BLEND` where the enum defines `BN`, wrapped the message in a `Declaration` type no specification defines, omitted the note the message carries, and used `ip://1.1.1.1:3000` where a `Locator` must be a multiaddr. They are now `SDP_DECLARE` Operations carrying a full `DeclarationMessage`.
- [Blend Protocol](../blend-protocol.md): the minimal network size and the reward schema counted "unique `ProviderId`s from declarations". Within the Blend declarations a `provider_id` is unique, so the qualifier distinguished nothing. The neighbor distinction names the Blend declarations as the set it reads.

# Implementation

- [ ] Derive `declaration_id` as `Hash(service || zk_id)`, keeping the registry one map per service keyed by it, and `DeclarationInfo` with its `service` and `zk_id`.
- [ ] Replace the per-note declaration set with the `service_notes` and `providers` indexes. Keep both in step with `declarations` on declare and on epoch finalization, and release a note for spending only once no service holds it.
- [ ] Enforce the three per-service uniqueness rules at declaration validation, the `zk_id` rule being the existence check on the `declaration_id`.
- [ ] Drop the service note from the withdraw operation and take it from the declaration, removing the `InvalidServiceNote` error it needed; update the `SDPWithdraw` encoder and decoder.
- [ ] Store `created << 32` as the initial `nonce`. Reject an active or withdraw message whose `lifecycle_epoch` is not the declaration's `created`, or whose `sequence` is not greater than the stored one.
- [ ] Confirm that the active-set filter matches the specification at the boundary epoch: a declaration leaves the set at `withdraw_at`, one epoch before its note is released for the service.
- [ ] Serve `GetDeclarationInfo(declaration_id)` and `GetAllDeclarationInfo(service_type)` from the finalized state, returning an error when the identifier or the service is not held.
- [ ] Check the Mantle test vectors against the implementation: the `declaration_id`, the `SDP_WITHDRAW` `op_id`, and the combined transaction with `CLAIM_POW_REWARD` and an operation count of `0x0b`.
- [ ] Add or extend tests: an encoding round-trip for `SDPWithdraw`; an active or withdraw message signed for a removed declaration is rejected against a later declaration with the same `declaration_id`; a second declaration reusing a `zk_id`, a service note or a `provider_id` within one service is rejected, and the same identifiers are accepted in another service; withdrawal removes the declaration and releases its note after the final reward.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.7.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 1.17.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 1.10.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.2.1 |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.6.1 |
| [Analysis: Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 1.7.1 |
