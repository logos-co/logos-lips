# [RFC] Cryptarchia: Complete the block test vectors and correct the active message vector

**Motivation and proposal:** PR #TBD

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |

## Reviewer Orientation

Every value can be recomputed from the inputs in [Details](#details) and the encodings of the two documents.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | High | **Start here**: [Mantle](../bedrock-v1.1-mantle-specification.md), [details](#1-active-message-vector) | the `UINT32` length `0xe5000000` before the 229-byte metadata, no `version` byte; the new `op_id` and the transaction hash that contains the operation |
| 2 | Medium | [Cryptarchia Protocol](../cryptarchia-v1-protocol.md), [details](#2-block-test-vectors) | each leaf is a one-operation transaction with the test fork digest; `merkle_root`, both `body_root` values and `block_id` follow from the leaves |

# Discussion

## How the values were checked

A script implements the encodings and hashes as the specifications define them. Before computing any new value, it reproduced every value it depends on:

- all 15 values of the Cryptarchia table as it stands on master, which the implementation generated: the ten leaves, both `merkle_root` values, both `body_root` values and `block_id`;
- the Ed25519 signatures of the two carried uncle headers on master, over their headers;
- the ten `op_id` vectors and the two transaction-hash vectors of Mantle.

The 296-byte header encoding also matches the implementation's `Header` fixture byte for byte.

## Open questions

- **The Merkle node hash is not stated.** Step 3 of Block Header Validation says the transaction Merkle tree pads its leaves with zeros to a power of two, but not how two children combine. The implementation, and all vectors here, use `Hash(left || right)` with no tag; a tree of one leaf is that leaf. Step 3 could state it in one clause.
- **`derive_op_id` hashes the payload alone.** It is written as `Hash(b"OPERATION_ID_V1" || encode(op))`, and `Op` is the opcode followed by the payload. All ten `op_id` vectors hash the payload without the opcode, so `encode(op)` there means the payload only. The definition could say so.
- **The carried uncle headers keep their old signatures.** The two `uncle_headers` entries were re-laid-out for the 296-byte header, but their signatures were made over the earlier 297-byte headers and do not verify over the new ones. The `body_root` with two uncles is computed over the entries as written. Re-signing them with the same keys, the Ed25519 seeds `0x66` and `0x77` repeated 32 times, changes both signatures and that `body_root`.

## Implementation divergence

The implementation writes the active message metadata without the `UINT32` length prefix: its `ActiveMessage` fixture is 269 bytes, the 229-byte metadata directly after the nonce. It does write the prefix for `CHANNEL_DEPOSIT` metadata. [Mantle Transaction Encoding](../mantle-transaction-encoding.md) defines both as `Metadata = UINT32 *BYTE`, so the specification governs and the implementation needs the prefix.

# Details

## 1. Active message vector

[Mantle](../bedrock-v1.1-mantle-specification.md) §Test Vectors. The `SDP_ACTIVE` payload follows `SDPActive = DeclarationId Nonce Metadata` and `Metadata = UINT32 *BYTE`, and its metadata is the 229-byte Blend metadata of [Active Message](../blend-protocol.md#active-message):

```diff
 declaration_id      1e1e…1e                  # 32 bytes
 nonce               1f00000000000000         # UINT64
+metadata length     e5000000                 # UINT32, 229
 metadata_type       01
-version             01
 epoch_number        0a000000                 # UINT32, 10
 signing_key         8a88e3dd…6f5c            # 32 bytes
 proof_of_quota      0202…02                  # 160 bytes
 proof_of_selection  0303…03                  # 32 bytes
```

The payload is 273 bytes.

| Vector | Before | After |
| --- | --- | --- |
| `SDP_ACTIVE` `op_id` | 0x76afa55f5733db75a982dc5ccabb5c6a7dab992eda78cdfd5f657f314e388354 | 0xc86eb27e15f6c70dc7406422636f33ee1c4c978288c9ae0f6c8231545a7d4e36 |
| hash of the transaction with one of each operation | 0x1684ede0483cefadeae009995a6e70a8b8740dc0073f9cdaa513f71c976f4564 | 0x26a63ecfdd47f3026506571cc5dcdcb1f15e58de5384246b6c42973d7f10c9c6 |

The transaction's payload changes in the same bytes as the operation's.

## 2. Block test vectors

[Cryptarchia Protocol](../cryptarchia-v1-protocol.md) §Test Vectors. Each leaf is the [Mantle Transaction Hash](../bedrock-v1.1-mantle-specification.md#mantle-transaction-hash) of a transaction that holds a single operation. There is one such transaction per operation kind, in table order:

```python
fork_digest = bytes([0x11]) * 32
tx = fork_digest + bytes([1, opcode]) + payload  # payload from Mantle's Operation Id vectors
leaf = Hash(b"MANTLE_TXHASH_V1" + tx)
```

The table now names the fork digest and the source of each operation.

| Value | Result |
| --- | --- |
| `leaf[0]` Transfer | 0xdcd51bc455151d8c9928556f2c91892ba5485124b72f88130c0cab3c39c922f9 |
| `leaf[1]` ChannelConfig | 0x9cb3569d8f0d92cadd26392e5056701dd1d3304b44315452dd254be8825143ce |
| `leaf[2]` ChannelInscribe | 0x0f3a666589ac2e6d77b18e261e47659dac7048b045c4d2e1cf1cf799ebc811c1 |
| `leaf[3]` ChannelDeposit | 0xc6beafed536029b3275db03731c3a4bad91a3b717b692a2ff6d1a33e1e1d129e |
| `leaf[4]` ChannelWithdraw | 0xf187a0ea956243e8fde25f36551afef7a06f74b8a37b8ee30fdba9e6b03b71b3 |
| `leaf[5]` ChannelTransfer | 0xa265377e0251954fbeb0174cfd62826989eaa4838aa2c0be1020a27daab442e2 |
| `leaf[6]` SDPDeclare | 0x5105d0d1f429bbf97c75f5d7d67626a5ed419f27a4d1838f88ef032e45d98d3d |
| `leaf[7]` SDPWithdraw | 0x38a43680e28f72fc64887fd118ed240d1e31acba3dd4a97de2881ba7cb5f4e60 |
| `leaf[8]` SDPActive, with the payload of [section 1](#1-active-message-vector) | 0xa6e19c480403346bb61853478867b19f6bb7d481d8a6c5dd60c39a9d52e28e71 |
| `leaf[9]` LeaderClaim | 0x840433dae7248668c9903c300103c65881f2bd2c0406f1634ede6c58d281ec20 |
| `merkle_root(transactions)`, 16 leaves after padding | 0x5b9ec0bcf3a4e30ed76de3113af80b574fac031867a72278c3f4c4ebe31023be |
| `body_root`, no uncles | 0xde89013d3358676d3a09bd69743db1f4417aeb76cb8f302816c67c00ce9627e5 |
| `body_root`, the two uncle entries as written | 0x444a7e933a7712bef7f73cf97ca30349cfbd7d7e09c0fae005e8b91f6b18037e |
| `block_id` of the header carrying the no-uncle `body_root` | 0x604b84cf816eedf450c783f91ef5d1abd6e7f66c1229695ad2e56beeb5a26a05 |

The `block_id` preimage is the one of [Block ID](../cryptarchia-v1-protocol.md#block-id), without a version byte.

# Implementation

- [ ] Write the `UINT32` length prefix before the active message metadata, and update the `ActiveMessage` and `SDP_ACTIVE` fixtures
- [ ] Regenerate the body-root, block ID and transaction-hash vectors once transactions carry the fork digest, and compare them with these
- [ ] Add or extend tests / test vectors that exercise the change
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | §Test Vectors: transaction leaves, `merkle_root`, `body_root`, `block_id` |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | §Test Vectors: `SDP_ACTIVE` payload and `op_id`, the transaction hash that contains it |
