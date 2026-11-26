# [RFC] Mantle: Add the Inscribe Operation

**Motivation and proposal:** [PR #540](https://github.com/logos-co/logos-lips/pull/540)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-17 |
| v2 | An inscription holds at least one byte | 2026-11-18 |
| v3 | The Operation has no validation, no Execution Gas and no execution: its bounds are in its encoding alone. The delivery inscription and its test value leave Mantle and this RFC | 2026-11-18 |
| v4 | The bounds of an inscription are stated by its production alone | 2026-11-18 |
| v5 | Rebased on the channels and rollups of [RFC-553](RFC-553-mantle-channels-and-rollups.md) and the split of Mantle of [RFC-552](RFC-552-mantle-split-the-operations-into-their-protocols.md): the opcode stays `0x02` and `0x01` is reserved, the payload class of `CHANNEL_INSCRIBE` is renamed in Mantle Channels, the test vectors are recomputed over the 14 Operations, and Cryptarchia is revision 1.3.3 | 2026-11-26 |

## Reviewer Orientation

Read the PR's Motivation first. No existing Operation changes, in its fields, its encoding or its validation, and no circuit changes.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [the Inscribe Operation](#1-the-inscribe-operation) | an Operation with an empty proof, no validation, no gas and no execution; the opcode |
| 2 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#2-encoding) | the `Inscribe` production and its two bounds |
| 3 | Low | [Mantle](#affected-specifications) and [Cryptarchia](#affected-specifications), [test vectors](#3-test-vectors) | reproduce them |

# Discussion

## Why an Operation of its own

The need comes from note delivery ([RFC-486](RFC-486-mantle-post-quantum-note-encryption.md)): a sender wants to commit to the delivery messages of its transaction. Three places could carry that hash.

A field in each Operation that creates user notes changes each of them, their encoding and every test vector that holds one, and serves one use.

An inscription in a channel needs a channel. A channel of its own for each wallet links the payments of that wallet through the channel and its signer. A channel for each payment leaves a `ChannelState` on every validator for each payment. One channel shared by everyone, under a key everyone holds, is a single hash chain: `CHANNEL_INSCRIBE` asserts `msg.parent == chan.tip_hash`, so two transactions built on the same tip cannot both be included, the loser has to be rebuilt and proven again, and anyone holding the key can reconfigure the channel or keep moving its tip.

An Operation of its own has none of these: no channel, no key, no order, no state. It changes no existing Operation, and it is not tied to note delivery.

## What an empty proof means

No key signs an inscription. It is bound to its Mantle Transaction by the proofs and signatures of the other Operations of that transaction, which cover the `mantle_txhash`. Two consequences follow:

- Anyone can copy an inscription into another transaction. A reader learns from an inscription what the builder of its transaction wrote, and nothing about any other party.
- A transaction whose other Operations have empty proofs too, such as a lone `CLAIM_POW_REWARD`, does not bind its inscriptions: they can be removed or added. An application that needs the binding puts its inscription beside an Operation whose proof covers the transaction hash.

An Inscribe Operation carries no value, so it cannot be the only Operation of a transaction: another one pays the fees.

## Bounds, validation and gas

An inscription holds from 1 byte to `MAX_OPERATION_DATA_SIZE` bytes, the bound of a channel inscription. Both bounds are in the production of the encoding, so a transaction that decodes holds a valid inscription and the ledger has nothing left to check: the Operation has no validation rule, and so no Execution Gas, the gas pricing validation. Its bytes pay the Permanent Storage fee as any byte of a transaction.

## A tag, not a field

An inscription is bytes, as the inscription of a channel is. An application could start its bytes with a tag of its own. A separate kind field would make the Operation one field larger for every user, to save a reader a prefix comparison.

## Privacy

An inscription is public. Free bytes on a private ledger are a place where a user can write what identifies it, which no rule of the ledger prevents.

## What this RFC leaves open

- The inscription a sender commits to its delivery messages with, a tag followed by their hash, is not specified in Mantle. It belongs with the wallet, and is proposed in the Wallet Technical Standard by [PR #538](https://github.com/logos-co/logos-lips/pull/538).

## Compatibility

The opcode `0x02` was reserved, so no encoded transaction changes meaning. The payload class of `CHANNEL_INSCRIBE` is renamed from `Inscribe` to `ChannelInscribe` in Mantle Channels, the name Mantle Transaction Encoding already uses: the name `Inscribe` now belongs to the new Operation. The reference implementation names the channel payload `InscriptionOp`.

# Details

## 1. The Inscribe Operation

[INSCRIBE](../bedrock-mantle.md#inscribe) is new, with opcode `0x02`, and `0x01` and `0x03 - 0x0F` are reserved.

```python
class Inscribe:
    inscription: bytes  # from 1 to MAX_OPERATION_DATA_SIZE bytes
```

- The proof is empty.
- Execution Gas, validation and execution: none.
- An application could start its inscription with a tag of its own.

The entry of the proofs not bound to the `mantle_txhash` that describes `CLAIM_POW_REWARD` now describes both empty proofs.

## 2. Encoding

[Inscribe Operation](../bedrock-mantle-encoding.md#inscribe-operation) is new, and `Inscribe` joins the alternatives of `OpPayload`:

```schema
Inscribe = UINT32 1*BYTE ; Min 1 byte, max MAX_OPERATION_DATA_SIZE bytes
```

## 3. Test vectors

- Mantle, [Operation Id](../bedrock-mantle.md#operation-id): a row for `INSCRIBE`, with a payload of 48 bytes after its length.
- Mantle, [Transaction Hash](../bedrock-mantle.md#transaction-hash): the transaction with one of each Operation holds 14 Operations, 2685 bytes.
- Cryptarchia, [Test Vectors](../cryptarchia-protocol.md#test-vectors): the transaction Merkle root has one more leaf, and the two body roots and the block ID follow.

No other vector changes. The thirteen Operation Ids, the transaction hash, the thirteen leaves, the Merkle root, the body roots and the block ID of the base were recomputed and matched before any was replaced.

## Chores

- Mantle Channels: the payload class of `CHANNEL_INSCRIBE` is named `ChannelInscribe`.

# Implementation

- [ ] `core`: the `Inscribe` Operation with opcode `0x02`, its codec with the rejection of an empty inscription and of one above `MAX_OPERATION_DATA_SIZE`, its empty proof and its Operation Id.
- [ ] Ledger: no validation, no Execution Gas, no state change.
- [ ] The Operation in the API types, the C bindings and the transaction builder.
- [ ] Add the test vectors of Mantle and Cryptarchia as tests.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-mantle.md) | Modified | Revision 2.2.0 |
| [Mantle Channels](../bedrock-mantle-channels.md) | Modified | Revision 1.1.1, payload class name only |
| [Mantle Transaction Encoding](../bedrock-mantle-encoding.md) | Modified | Revision 2.2.0 |
| [Cryptarchia Protocol](../cryptarchia-protocol.md) | Modified | Revision 1.3.3, test vectors only |
