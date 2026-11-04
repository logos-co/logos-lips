# [RFC] SDP: Advance the sequence of an active message by one

**Motivation and proposal:** [PR #513](https://github.com/logos-co/logos-lips/pull/513)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-04 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Service Declaration Protocol](#affected-specifications), [the sequence rule](#1-an-active-message-advances-the-sequence-by-one) | an active message carries the stored `sequence` plus one; a withdraw message keeps any greater one |
| 2 | Critical | [Mantle](#affected-specifications), [`SDP_ACTIVE` validation](#2-sdp_active-checks-the-increment) | the check matches the rule and does not wrap at 2³²−1 |

# Discussion

## Why the bound holds

A declaration's `sequence` changes only when the ledger accepts one of its active or withdraw messages. With an increment of one, each accepted active message adds one. The Blend Network accepts one active message per attested epoch, and only in the epoch after it ([Active Message](../blend-protocol.md#active-message)). The `sequence` therefore grows by at most one per epoch. An epoch is 10⌊k/f⌋ = 648,000 slots of one second, 7.5 days ([Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule)). Reaching 2³²−1 would take 2³²−1 epochs, about 88 million years. A withdraw message can therefore always carry a greater `sequence`.

The bound relies on that limit of the service. A service that accepted several active messages per epoch from one declaration would rely on the fees of 2³²−1 transactions instead.

## Why a withdraw message may still skip sequences

A withdraw message is accepted at most once, because the `withdraw_at` of its declaration must be `None`. A withdrawal signed with the stored `sequence` plus one fails if the node's next active message lands first. It must then be signed again, and its ZkTransfer proven again, since both cover the transaction hash. A withdrawal signed with a larger `sequence` stays valid while the node's active messages land, up to the number of sequences it skipped.

A withdraw message that skips to 2³²−1 leaves no `sequence` for the active messages that may follow it before `withdraw_at`. The declaration then loses the rewards of those epochs. Only the signer of the withdrawal makes that choice.

## Alternatives

- **Reserve 2³²−1 for withdraw messages.** An active message would need a `sequence` below 2³²−1 and could still skip. A withdrawal at 2³²−1 would then always pass. One active message at 2³²−2 would still end the declaration's active messages, and with them its rewards.
- **Drop the sequence check from withdraw messages.** `withdraw_at` and the nullifier of the service note already make a withdrawal single-use. An active message would then no longer invalidate a signed withdrawal that never landed. Such a withdrawal would stay valid for the whole life of the declaration.

## Compatibility

The reference node builds both active and withdraw messages with the ledger's `sequence` plus one (`next_message_nonce` in `services/sdp/src/lib.rs`). Its messages already meet the new rule, so only validation changes. The chain has not launched, so no stored declaration needs a migration.

# Details

## 1. An active message advances the sequence by one

[Declaration Storage](../bedrock-service-declaration-protocol.md#declaration-storage) states the `sequence` rule for each message:

```diff
 An active or withdraw message is valid only if its `nonce`:
 - has the `created` of the `DeclarationInfo` as its `lifecycle_epoch`;
-- has a `sequence` greater than the `sequence` of the `nonce` of the `DeclarationInfo`.
+- for an active message, has a `sequence` equal to the `sequence` of the `nonce` of the `DeclarationInfo` plus one;
+- for a withdraw message, has a `sequence` greater than the `sequence` of the `nonce` of the `DeclarationInfo`.
```

## 2. `SDP_ACTIVE` checks the increment

[`SDP_ACTIVE`](../bedrock-v1.1-mantle-specification.md#sdp_active) validation compares the `sequence` with the stored one plus one:

```diff
 assert active.nonce >> 32 == declaration_info.created
-assert active.nonce & 0xFFFFFFFF > declaration_info.nonce & 0xFFFFFFFF
+assert active.nonce & 0xFFFFFFFF == (declaration_info.nonce & 0xFFFFFFFF) + 1
```

The sum is not reduced to 32 bits. Once the stored `sequence` is 2³²−1, no active message is valid. `SDP_WITHDRAW` keeps its check.

- The Service Declaration Protocol revision is 1.10.0, and the Mantle revision is 2.3.0.

# Implementation

- [ ] Accept an `SDPActiveOp` only if its `sequence` is the declaration's `sequence` plus one. Compute the sum with checked addition, so that a stored `u32::MAX` rejects every active message instead of wrapping to 0. Today `validate_nonce` (`core/src/mantle/ops/sdp/mod.rs`) serves both operations and accepts any greater `sequence`. `SDPWithdrawOp` keeps that check.
- [ ] Add tests: an active message at the stored `sequence` plus one is accepted; one that skips a `sequence`, repeats the stored one, or jumps to `u32::MAX` is rejected; no active message is accepted once the stored `sequence` is `u32::MAX`; a withdraw message that skips sequences is still accepted.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.10.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.3.0 |
