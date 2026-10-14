# [RFC] Mantle: Bound operation data payloads

**Motivation and proposal:** [PR #467](https://github.com/logos-co/logos-lips/pull/467)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-08 |
| v2 | Moved the existing proposal from the Mantle Transaction Encoding appendix into the canonical RFC directory and reorganized it to this template. | 2026-10-08 |
| v3 | Temporarily included SDP activity metadata in the shared payload bound; superseded by v5. | 2026-10-08 |
| v4 | Simplified the normative payload-bound wording and kept derivation and rationale in the RFC. | 2026-10-09 |
| v5 | Restricted the shared bound to channel inscription and deposit payloads; aligned SDP activity metadata, Blend's 229-byte layout, and Mantle test vectors with the canonical tagged encoding. | 2026-10-13 |

## Reviewer Orientation

Read the PR's Motivation first for context.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Encoding and decoder bound](#encoding-and-decoder-bound) · [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Check the shared channel-payload limit and decoder rejection rule; confirm the two four-byte length prefixes remain unchanged. |
| 2 | High | [Tagged activity metadata](#tagged-activity-metadata) · [Blend Protocol](../blend-protocol.md#active-message) | Check the one-byte discriminant and fixed Blend layout, with no generic length prefix or separate version byte. |
| 3 | High | [Mantle operation validation](#mantle-operation-validation) · [Mantle specification](../bedrock-v1.1-mantle-specification.md) | Check the two channel size assertions and variant-specific SDP metadata validity; confirm the corrected vectors match the wire layout. |
| 4 | Low | [Affected Specifications](#affected-specifications) | Confirm the history entries retain the assigned Mantle and encoding versions and record the Blend encoding correction. |

## Discussion

### Length width and semantic limit

`UINT32` is the encoded length width, not the protocol's semantic maximum. It can represent lengths through `2^32 - 1`, while a `u16` prefix would stop at 65,535 bytes and could not represent the proposed limit. The four-byte prefix therefore remains in place, with a separate field-level validity limit.

The same semantic limit applies to the two variable-sized opaque `UINT32 *BYTE` channel payloads, so the length-prefix width does not imply different protocol maxima for them.

The limit is seven eighths of the current 2 MiB capacity available to transaction data:

```text
2,097,152 * 7 / 8 = 1,835,008 bytes
```

The remaining 262,144 bytes leave headroom for the rest of a transaction, including framing, other operations, inputs, and proofs. That headroom does not guarantee that a complete transaction fits. Overall transaction and block limits apply independently.

### Scope and compatibility

The bound covers `ChannelInscribe.Inscription` and `ChannelDeposit.Metadata`. It changes which channel operations are valid, but preserves their wire format and four-byte `UINT32` length prefixes.

`SDPActive.Metadata` is a tagged closed type, with encoding and validation determined by its one-byte discriminant. The current `0x01` Blend variant has a fixed 229-byte encoding including the tag. It does not share the generic channel-payload bound. Future activity-metadata variants may specify their own encodings, validation, and appropriate size limits.

The previous Mantle grammar described activity metadata as `UINT32 *BYTE`, unlike the current [Logos codec](https://github.com/logos-blockchain/logos-blockchain/blob/f376f9547e7c7d4d4a78adcb9e0bdfa8d383842c/core/src/sdp/mod.rs#L610-L680) and [wire fixture](https://github.com/logos-blockchain/logos-blockchain/blob/f376f9547e7c7d4d4a78adcb9e0bdfa8d383842c/core/src/mantle/fixtures/ops/op_values.rs#L136). An independent implementation following that grammar would encode `SDP_ACTIVE` differently, causing decoding failures and different hashes. The Blend spec and Mantle vectors also included a separate version byte absent from the codec. This RFC corrects those specification discrepancies; no generic `UINT32` activity-metadata prefix is introduced.

## Details

### Encoding and decoder bound

Mantle Transaction Encoding defines `MAX_OPERATION_DATA_SIZE` as exactly **1,835,008 bytes**. The canonical encoded payloads of `ChannelInscribe.Inscription` and `ChannelDeposit.Metadata` MUST each contain no more than this many bytes, excluding each outer `UINT32` length prefix. A decoder MUST reject either field when its declared or decoded payload length exceeds the limit.

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

`SDP_ACTIVE` metadata validity follows the selected variant's encoding and validation rules, without a generic size assertion.

### Tagged activity metadata

The `DepositMetadata` production retains the channel deposit's length-prefixed byte encoding. `ActivityMetadata` instead describes the existing tagged wire type:

```schema
SDPActive               = DeclarationId Nonce ActivityMetadata
ActivityMetadata        = ActivityMetadataType ActivityMetadataPayload
ActivityMetadataType    = Byte ; 0x01 = Blend
ActivityMetadataPayload = BlendActivityProof ; Selected by ActivityMetadataType
```

Unknown discriminants are invalid. The current Blend encoding is the tag `0x01` followed directly by a 4-byte little-endian epoch, 32-byte Ed25519 signing key, 160-byte proof of quota, and 32-byte proof of selection, as defined in [Blend Protocol — Active Message](../blend-protocol.md#active-message). The 228-byte proof plus the tag totals 229 bytes, with no separate version byte or generic length prefix.

The Mantle semantic payload type and example use the tagged variant. Its `SDP_ACTIVE` operation-id and combined-transaction vectors remove the stale version byte and update their hashes accordingly.

## Chores

- Retain the LIP-202 revision `1.10.0` and Mantle revision `1.17.0`, updating their descriptions to cover the channel bounds and tagged SDP metadata correction. Record the Blend wire-encoding correction as `1.6.1`.

## Implementation

- [ ] Apply the shared bound to `ChannelDeposit.Metadata` in [logos-blockchain#2805](https://github.com/logos-blockchain/logos-blockchain/issues/2805).
- [ ] Ensure `ChannelInscribe.Inscription` uses the same canonical shared bound.
- [ ] Enforce the limit consistently during decode and Mantle operation validation.
- [ ] Add boundary tests for both channel fields, including exactly-at-limit and over-limit cases.
- [ ] Verify tagged `SDP_ACTIVE` interoperability against the existing codec fixtures without adding length or version prefixes.
- [ ] Verify the implementation matches this specification.

## Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Defines the channel-payload limit and decoder rejection rule; aligns activity metadata with the tagged encoding. |
| [Mantle specification](../bedrock-v1.1-mantle-specification.md) | Modified | Bounds inscription and deposit payloads; uses variant-specific SDP metadata validity and corrects its example and vectors. |
| [Blend Protocol](../blend-protocol.md) | Modified | Removes the stale activity-proof version byte and defines the fixed 229-byte tagged metadata layout. |
