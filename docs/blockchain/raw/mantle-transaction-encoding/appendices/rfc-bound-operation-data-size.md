# [RFC] Bound Mantle Operation Data Payloads

## Motivation

In Mantle Transaction Encoding, `UINT32 *BYTE` uses a four-byte unsigned length prefix. That prefix can encode lengths up to `2^32 - 1` bytes, but this is an encoding capability, not a sensible protocol payload limit. Payloads of that size are incompatible with the protocol's current 2 MiB maximum block-body capacity.

The implementation already applies a seven-eighths-derived bound to `ChannelInscribe.Inscription`, using its current 2 MiB transaction-byte capacity. `ChannelDeposit.Metadata` has the same `UINT32` grammar but no corresponding semantic limit. One shared limit makes both large opaque channel payloads consistent and leaves room for the rest of a transaction.

## Proposal

Define the protocol constant `MAX_OPERATION_DATA_SIZE` as **1,835,008 bytes**. This concrete value is currently seven eighths of the 2 MiB maximum block body (2,097,152 bytes):

```text
2,097,152 * 7 / 8 = 1,835,008 bytes
```

The remaining 262,144 bytes reserve headroom for transaction framing, other operations, inputs, proofs, and other transaction data. The value is specified directly in Mantle Transaction Encoding and does not require Mantle parsing to import the Cryptarchia `MAX_BLOCK_SIZE` constant. See [Cryptarchia's current maximum block-body size](../../cryptarchia-v1-protocol.md#constants).

`UINT32` continues to specify only the encoded byte-length prefix; its width is unchanged. `ChannelInscribe.Inscription` and `ChannelDeposit.Metadata` MUST each contain at most `MAX_OPERATION_DATA_SIZE` bytes. A decoder MUST reject either field when its declared or decoded length exceeds that limit. This change does not apply to `SDPActive.Metadata`.

## Compatibility

This is a protocol-validity change: values above the new limit are invalid, even though their lengths are representable by the existing prefix. The wire format and four-byte `UINT32` length prefixes remain unchanged.
