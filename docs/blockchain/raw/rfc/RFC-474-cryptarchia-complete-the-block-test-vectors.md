# [RFC] Cryptarchia: Complete the block test vectors

**Motivation and proposal:** [PR #474](https://github.com/logos-co/logos-lips/pull/474)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |
| v2 | Retitled from "Complete the block test vectors and correct the active message vector" and renamed the file to match. Removed the Mantle part: the active message vector, its implementation divergence, its implementation task, and the Mantle rows of Reviewer Orientation and Affected Specifications. Mantle now encodes the active message metadata as a tagged variant without a length prefix, and carries its own vectors. | 2026-10-14 |
|  | Recomputed `leaf[8]` from Mantle's current `SDP_ACTIVE` payload, and with it `merkle_root`, both `body_root` values and `block_id`. | 2026-10-14 |
| v3 | The base now marks the two uncle signatures `TBD`, because master's were made over the 297-byte headers. The re-signed values fill those cells, and the table keeps master's values only as the check of the seeds. | 2026-10-20 |

## Reviewer Orientation

Single-document change: read §Test Vectors of [Cryptarchia Protocol](../cryptarchia-v1-protocol.md). Focus on how each leaf is built, a single-operation transaction with the test fork digest, and on the two re-signed uncle headers. Every value can be recomputed from the inputs in [Details](#details).

# Discussion

## How the values were checked

A script implements the encodings and hashes as the specifications define them. Before computing any new value, it reproduced every value it depends on:

- the ten `op_id` vectors and both transaction-hash vectors of Mantle;
- all 15 values of the Cryptarchia table on master, which the implementation generated: the ten leaves, both `merkle_root` values, both `body_root` values and `block_id`. Master's `leaf[8]` reproduces from the earlier `SDP_ACTIVE` payload it was generated from, which carried a `version` byte;
- the Ed25519 signatures of the two carried uncle headers on master. Ed25519 signing is deterministic, and signing master's 297-byte headers with the seeds `0x66` and `0x77`, each repeated 32 times, reproduces both signatures byte for byte.

The 296-byte header encoding also matches the implementation's `Header` fixture byte for byte.

## Open questions

- **The Merkle node hash is not stated.** Step 3 of Block Header Validation says the transaction Merkle tree pads its leaves with zeros to a power of two, but not how two children combine. The implementation, and all vectors here, use `Hash(left || right)` with no tag; a tree of one leaf is that leaf. Step 3 could state it in one clause.
- **`derive_op_id` hashes the payload alone.** It is written as `Hash(b"OPERATION_ID_V1" || encode(op))`, and `Op` is the opcode followed by the payload. All ten `op_id` vectors hash the payload without the opcode, so `encode(op)` there means the payload only. The definition could say so.

# Details

## Block test vectors

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
| `leaf[8]` SDPActive | 0x6c92ea8b434c2be4c6d4de85f1d846207600c2ee067c4e07a769902e61e37e88 |
| `leaf[9]` LeaderClaim | 0x840433dae7248668c9903c300103c65881f2bd2c0406f1634ede6c58d281ec20 |
| `merkle_root(transactions)`, 16 leaves after padding | 0x06e94c5a0876f4c190703ae2de8127721a731b9fddf2cef5807bcf1537f9bcdb |
| `body_root`, no uncles | 0x052e55428b0df36aaa6d15d45af3d5c4b6d6fcea52df654ad0f339edf0cae0ad |
| `body_root`, the two re-signed uncle entries below | 0x8d29dcb941df1a7356789acf71f0671a6638b0e3da251896560ac18b51c5d3cf |
| `block_id` of the header carrying the no-uncle `body_root` | 0x7b6d789888d076dfdd2dfbc4f8373e40e493bd261cd9e0d6efa256db045beabe |

The `block_id` preimage is the one of [Block ID](../cryptarchia-v1-protocol.md#block-id), without a version byte.

Each carried uncle entry is a 296-byte header followed by its 64-byte signature. The base marks both signatures `TBD`, because master's were made over the earlier 297-byte headers and do not verify over the 296-byte ones. Each header is signed with its own key. The key's Ed25519 seed is the entry's fill byte repeated 32 times, and the header's `leader_key` field is the public key of that seed:

| Entry | Seed | Master's signature, over the 297-byte header | Signature |
| --- | --- | --- | --- |
| `uncle_headers[0]` | `0x66` | 0x563913f1ba7ad4129a077acd56278e743fd45120226dd315fa49f3a9c5d07af6a174ab84d4555a279afe053e79c8bb794be3f7d2e71e92b8da1b490687cb8306 | 0x810216baf4c2149463b457f0f776ab1f71a9f996915345e4f8709ffe181a2373341baa0b1080b8d07345f3cb67e446c7fa0dd4348f521523eaa37c1387520b0d |
| `uncle_headers[1]` | `0x77` | 0xad17e45d503a16fb41c25c4b3025956c63b31015871e957f3562b47cebce784e5b392ce3dd05214afe09102e0d2ed8211a83b81f18231963a226198fd528df0c | 0x96ca0d9f04bb9d19129c8c348dd5fbb03ddf08025cc82096079b38916fa5cc8b8368ac9aa26c618b691a402e1c06812b6c7e010651ed1b9656a26afea88ba705 |

# Implementation

- [ ] Regenerate the body-root and block ID test vectors once transactions carry the fork digest, and compare every value with these, leaves and uncle signatures included
- [ ] Add or extend tests / test vectors that exercise the change
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | §Test Vectors: transaction leaves, `merkle_root`, `body_root`, `block_id`, uncle signatures |
