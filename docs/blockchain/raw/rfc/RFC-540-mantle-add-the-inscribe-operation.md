# [RFC] Mantle: Add the Inscribe Operation

**Motivation and proposal:** [PR #540](https://github.com/logos-co/logos-lips/pull/540)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-17 |
| v2 | An inscription holds at least one byte | 2026-11-18 |

## Reviewer Orientation

Read the PR's Motivation first. The private ledger of [RFC-480](RFC-480-mantle-private-utxo-ledger.md) and the note delivery of [RFC-486](RFC-486-mantle-post-quantum-note-encryption.md) are assumed. No existing Operation changes, in its fields, its encoding or its validation, and no circuit changes.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [the Inscribe Operation](#1-the-inscribe-operation) | an Operation with an empty proof: what binds it to its transaction and what does not, the opcode, the size bounds |
| 2 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#2-encoding) | the `Inscribe` production: an `Inscription` of at least one byte, under the bound of a channel inscription |
| 3 | High | [Mantle](#affected-specifications), [the delivery inscription](#3-the-delivery-inscription) | what the hash covers and in which order, what a node checks, the steps signed before their transaction |
| 4 | Medium | [Mantle](#affected-specifications), [Execution Gas](#4-execution-gas) | the Execution Gas is not determined yet |
| 5 | Low | [Mantle](#affected-specifications) and [Cryptarchia](#affected-specifications), [test vectors](#5-test-vectors) | reproduce them |

# Discussion

## Why an Operation of its own

Three places could carry the hash of the delivery messages.

A field in each Operation that creates user notes changes six Operations, their encoding and every test vector that holds one, and serves one use.

An inscription in a channel needs a channel. A channel of its own for each wallet links the payments of that wallet through the channel and its signer. A channel for each payment leaves a `ChannelState` on every validator for each payment. One channel shared by everyone, under a key everyone holds, is a single hash chain: `CHANNEL_INSCRIBE` asserts `msg.parent == chan.tip_hash`, so two transactions built on the same tip cannot both be included, the loser has to be rebuilt and proven again, and anyone holding the key can reconfigure the channel or keep moving its tip.

An Operation of its own has none of these: no channel, no key, no order, no state. It changes no existing Operation, and it is not tied to note delivery.

## What an empty proof means

No key signs an inscription. It is bound to its Mantle Transaction by the proofs and signatures of the other Operations of that transaction, which cover the `mantle_txhash`. Two consequences follow:

- Anyone can copy an inscription into another transaction. A reader learns from an inscription what the builder of its transaction wrote, and nothing about any other party.
- A transaction whose other Operations have empty proofs too, such as a lone `CLAIM_POW_REWARD`, does not bind its inscriptions: they can be removed or added. An application that needs the binding puts its inscription beside an Operation whose proof covers the transaction hash.

An Inscribe Operation carries no value, so it cannot be the only Operation of a transaction: another one pays the fees.

## The size bounds

An inscription holds at least one byte. An empty channel inscription still moves the tip of its channel and can carry steps, where an empty inscription of this Operation would do nothing at all.

An inscription is bounded as a channel inscription is, by `MAX_OPERATION_DATA_SIZE`, 1,835,008 bytes, and is encoded the same way. One bound and one encoding for the data Operations carry is simpler for implementations than a second constant, and the bytes of an inscription pay the Permanent Storage fee as those of a channel do.

## Execution Gas

The Execution Gas of the Operation is not determined yet. The ledger compares one length and changes no state, so it is expected to be low, and it has to come from the benchmark of Gas Cost Determination like the others.

> **TODO (author):** determine `EXECUTION_INSCRIBE_GAS` with the benchmark, and add the Operation to Gas Cost Determination.

## A tag, not a field

An inscription is bytes, as the inscription of a channel is. An application starts its bytes with a tag of its own, and the specification lists the tags it defines. A separate kind field would make the Operation one field larger for every user, to save a reader a prefix comparison.

## Privacy

An inscription is public. A transaction that holds a delivery inscription shows that some of its outputs are delivered by delivery messages. It shows nothing of their contents or of their recipients: the hash is over ciphertexts. Free bytes on a private ledger are also a place where a user can write what identifies it, which no rule of the ledger prevents.

## What this RFC leaves open

- The transport of delivery messages: how they travel between nodes, how long nodes keep them, how a wallet reads them. The delivery inscription is what lets that transport check a message, and is specified here so that the transport can rely on it.
- A user step and a program deposit are signed by their holder before their Mantle Transaction exists, so an Inscribe Operation of the transaction does not speak for them. Their holder uses the `inscription` of the step, in the format of its zone, which this RFC does not define.
- The Wallet Technical Standard does not say yet that a sender adds the delivery inscription. The sentence belongs with the wallet changes that follow RFC-486.

## Compatibility

The opcode `0x02` was reserved, so no encoded transaction changes meaning. The payload class of `CHANNEL_INSCRIBE` is renamed from `Inscribe` to `ChannelInscribe` in Mantle, the name Mantle Transaction Encoding already uses: the name `Inscribe` now belongs to the new Operation. The reference implementation names the channel payload `InscriptionOp`.

# Details

## 1. The Inscribe Operation

[INSCRIBE](../bedrock-v1.1-mantle-specification.md#inscribe) is new, with opcode `0x02`, and the reserved range becomes `0x03 - 0x0F`.

```python
class Inscribe:
    inscription: bytes  # from 1 to MAX_OPERATION_DATA_SIZE bytes
```

- The proof is empty.
- Validation is one check: `1 <= len(inscribe.inscription) <= MAX_OPERATION_DATA_SIZE`.
- Execution leaves the ledger state unchanged.
- A Mantle Transaction can hold any number of them. The ledger reads none.
- An application should start its inscription with a tag of its own.

The list of the proofs not bound to the `mantle_txhash` gains one entry for it.

## 2. Encoding

[Inscribe Operation](../mantle-transaction-encoding.md#inscribe-operation) is new, and `Inscribe` joins the alternatives of `OpPayload`:

```schema
Inscribe = Inscription ; from 1 to MAX_OPERATION_DATA_SIZE bytes
```

`Inscription` is the production channels use, a `UINT32` length and its bytes. A decoder MUST reject an `Inscribe` whose declared or decoded payload length is zero or exceeds `MAX_OPERATION_DATA_SIZE`. The proof is the `EmptyProof`.

## 3. The delivery inscription

[Note Delivery](../bedrock-v1.1-mantle-specification.md#note-delivery) gains the first use of the Operation. A sender may commit to the delivery messages of a Mantle Transaction in an Inscribe Operation of that transaction:

```python
def derive_delivery_hash(delivery_messages: list[bytes]) -> Hash:
    h = Hasher()
    h.update(b"NOTE_DELIVERY_V1")
    for delivery_message in delivery_messages:
        h.update(delivery_message)
    return h.digest()

def delivery_inscription(delivery_messages: list[bytes]) -> bytes:  # 48 bytes
    return b"NOTE_DELIVERY_V1" + derive_delivery_hash(delivery_messages)
```

- The messages are those of the outputs of the transaction, in the order of its Operations and of their outputs. An output delivered by other means has none.
- A transaction holds at most one delivery inscription.
- A node handed delivery messages for a transaction checks that each starts with the commitment of an output of the transaction, in the order of the outputs, and that their `delivery_inscription` is an inscription of the transaction, before it keeps or serves them.

## 4. Execution Gas

The Operation has a fixed Execution Gas, `EXECUTION_INSCRIBE_GAS`, whose row in the Gas Determination table of Mantle reads "to be determined". The bytes of an inscription pay the Permanent Storage fee, as any byte of a transaction.

## 5. Test vectors

- Mantle, [Operation Id](../bedrock-v1.1-mantle-specification.md#operation-id): a row for `INSCRIBE`, whose payload is a delivery inscription after its length.
- Mantle, [Mantle Transaction Hash](../bedrock-v1.1-mantle-specification.md#mantle-transaction-hash-1): the transaction with one of each Operation holds 11 Operations, 2331 bytes.
- Mantle, [Delivery Hash](../bedrock-v1.1-mantle-specification.md#delivery-hash): the hash of the delivery message of vector 1 of the Note Encryption Test Values.
- Cryptarchia, [Test Vectors](../cryptarchia-v1-protocol.md#test-vectors): the transaction Merkle root has one more leaf, and the two body roots and the block ID follow.

No other vector changes. The ten Operation Ids, the transaction hash, the ten leaves, the Merkle root, the body roots and the block ID of the base were recomputed and matched before any was replaced.

## Chores

- Mantle: the payload class of `CHANNEL_INSCRIBE` is named `ChannelInscribe`.

# Implementation

- [ ] `core`: the `Inscribe` Operation with opcode `0x02`, its codec with the rejection of an empty inscription and of one above `MAX_OPERATION_DATA_SIZE`, its empty proof and its Operation Id.
- [ ] Ledger: the size checks, no state change.
- [ ] The Operation in the API types, the C bindings and the transaction builder.
- [ ] Wallet: a transfer whose outputs are delivered by delivery messages adds the delivery inscription.
- [ ] Measure the Execution Gas of the Operation with the gas benchmark, and set `EXECUTION_INSCRIBE_GAS`.
- [ ] Add the test vectors of Mantle and Cryptarchia as tests.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.2.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.2.0 |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.2, test vectors only |
