# [RFC] Mantle: Bound channel operation data payloads

**Motivation and proposal:** [PR #467](https://github.com/logos-co/logos-lips/pull/467)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-08 |
|  | Moved the existing proposal from the Mantle Transaction Encoding appendix into the canonical RFC directory and reorganized it to this template. | 2026-10-08 |

## Reviewer Orientation

Read the PR's Motivation first for context.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Encoding and decoder bound](#encoding-and-decoder-bound) · [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Check the new payload-validity limit and decoder rejection rule; confirm the four-byte prefix remains unchanged. |
| 2 | High | [Mantle operation validation](#mantle-operation-validation) · [Mantle specification](../bedrock-v1.1-mantle-specification.md) | Check that all three affected operations reject oversized data during validation. |
| 3 | Low | [Grammar production names](#grammar-production-names-and-scope) · [Affected Specifications](#affected-specifications) | Confirm the channel and service metadata productions are distinct and the history entries retain their assigned versions. |

## Discussion

### Length width and semantic limit

`UINT32` is the encoded length width, not the protocol's semantic maximum. It can represent lengths through `2^32 - 1`, while a `u16` prefix would stop at 65,535 bytes and could not represent the proposed limit. The four-byte prefix therefore remains in place, with a separate field-level validity limit.

The same semantic limit applies to all three opaque `UINT32 *BYTE` operation-data payloads, so the length-prefix width does not imply different protocol maxima for them.

The limit is seven eighths of the current 2 MiB capacity available to transaction data:

```text
2,097,152 * 7 / 8 = 1,835,008 bytes
```

The remaining 262,144 bytes leave headroom for the rest of a transaction, including framing, other operations, inputs, and proofs. That headroom does not guarantee that a complete transaction fits. Overall transaction and block limits apply independently.

### Scope and compatibility

The bound covers all three variable-sized opaque operation-data fields: `ChannelInscribe.Inscription`, `ChannelDeposit.Metadata`, and `SDPActive.Metadata`. It changes which operations are valid, but does not change their wire format or four-byte `UINT32` prefixes.

## Details

### Encoding and decoder bound

Mantle Transaction Encoding defines `MAX_OPERATION_DATA_SIZE` as exactly **1,835,008 bytes**. The canonical encoded payloads of `ChannelInscribe.Inscription`, `ChannelDeposit.Metadata`, and `SDPActive.Metadata` MUST each contain no more than this many bytes, excluding each outer `UINT32` length prefix. A decoder MUST reject any of these fields when its declared or decoded payload length exceeds the limit.

```diff
-Inscription     = UINT32 *BYTE
+Inscription     = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes
-ChannelDeposit    = ChannelId Inputs Metadata
+ChannelDeposit   = ChannelId Inputs DepositMetadata
+DepositMetadata  = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes
```

`UINT32` remains the four-byte encoded length prefix. Its width does not set the semantic payload maximum.

### Mantle operation validation

Mantle operation validation explicitly checks the same limit. The inscription assertion comes before channel-state and signature checks:

```diff
+assert len(msg.inscription) <= MAX_OPERATION_DATA_SIZE
```

The first `CHANNEL_DEPOSIT` validation step checks metadata size:

```diff
+assert len(deposit.metadata) <= MAX_OPERATION_DATA_SIZE
```

The existing checks for channel existence, spendable inputs, and note ownership follow this step.

`SDP_ACTIVE` validation also bounds the canonical encoded metadata payload, excluding its `UINT32` length prefix:

```diff
+assert len(active.metadata) <= MAX_OPERATION_DATA_SIZE
```

### Grammar production names and scope

The deposit and service-activeness productions have distinct names. The rename does not change the fields' byte encodings or meanings.

```diff
-SDPActive        = DeclarationId Nonce Metadata
-Metadata         = UINT32 *BYTE ; Service-specific node activeness metadata
+SDPActive        = DeclarationId Nonce ActivityMetadata
+ActivityMetadata = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes; service-specific node activeness metadata
```

The bound applies to all three fields, including service-specific activeness metadata. The `UINT32` prefixes remain unchanged and are excluded from the bounded payload size.

## Chores

- Update the LIP-202 revision history to `1.10.0` and the Mantle revision history to `1.17.0` for this proposal.

## Implementation

- [ ] Apply the shared bound to `ChannelDeposit.Metadata` and `SDPActive.Metadata` in [logos-blockchain#2805](https://github.com/logos-blockchain/logos-blockchain/issues/2805).
- [ ] Ensure `ChannelInscribe.Inscription` uses the same canonical shared bound.
- [ ] Enforce the limit consistently during decode and Mantle operation validation.
- [ ] Add boundary tests for all three fields, including exactly-at-limit and over-limit cases.
- [ ] Verify the implementation matches this specification.

## Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Defines the shared field limit and decoder rejection rule for all three payloads. |
| [Mantle specification](../bedrock-v1.1-mantle-specification.md) | Modified | Adds explicit validation checks for inscription, deposit metadata, and SDP activity metadata. |
