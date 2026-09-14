# TEMPLATE-OFFCHAIN-INSCRIPTION-BODIES

| Field | Value |
| --- | --- |
| Name | [Template] Off-Chain Inscription Bodies |
| Slug | 249 |
| Status | raw |
| Category | Informational |
| Tags | mantle, channels, inscription, logos-storage, lez, data-availability |
| Editor | Mehmet Gonen <mehmet@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial version. | 2026-09-16 |

# Introduction

This document outlines a pattern for channels whose inscriptions carry large payloads. Instead of writing the payload itself on-chain, the channel writer inscribes a small, fixed-size commitment and publishes the payload as a content-addressed dataset on Logos Storage. The chain keeps what only the chain can provide, a canonical order and a signed commitment, while Logos Storage holds the bytes. In this role Logos Storage acts as a pseudo data-availability layer: it provides integrity and discovery, not a durability guarantee.

The pattern is generic. Its first intended user is the Logos Execution Zone (LEZ), whose zone blocks carry transaction bodies and zero-knowledge receipts that are large relative to what the base layer needs to see.

## Reference: [Mantle](bedrock-v1.1-mantle-specification.md), [LEE v0.3](lez/lee-v0.3-specifications.md), [Logos Storage Datasets](../../storage/raw/datasets.md).

## Objectives

- Make the on-chain cost of an inscription independent of the size of the payload it commits to.
- Preserve the two properties the base layer actually provides for an inscription: a canonical order among a channel's messages, and a sequencer-signed commitment to each message's content.
- Define the pattern once, so that zone blocks, proof bundles, application logs and dataset anchors share one envelope, one publication order and one reader behaviour.
- Keep the base layer untouched. The ledger already treats inscription payloads as opaque bytes; nothing in this pattern requires a Mantle change.

## Requirements

- A reader holding only the chain and access to Logos Storage must be able to obtain the payload and verify that it is exactly the payload the writer committed to.
- Anyone holding the payload must be able to re-publish it so that readers accept it, without any additional trust in the re-publisher.
- A reader must never apply a later message while an earlier one's payload is missing; ordering on-chain must not be silently reinterpreted off-chain.
- Small payloads must remain inscribable inline, so that channels do not depend on Logos Storage for messages that do not need it.

# Overview

Bedrock validates a `CHANNEL_INSCRIBE` operation by checking the writer's signature, the round-robin sequencer slot and the parent message; it never inspects the payload. The fee, however, is proportional to the encoded size of the transaction through the permanent storage gas market. A channel that inscribes megabytes therefore pays per byte for data the ledger never reads, and receives in return exactly two properties: order and a signed commitment.

The pattern separates the two halves of an inscription:

- The **on-chain part** is a fixed-size envelope carrying a reference to the payload: a Logos Storage dataset identifier, the payload's Merkle root and its size, plus whatever commitment the channel's own semantics require (for a zone: the post-state root and a root over the block's transactions).
- The **off-chain part** is the payload itself, published as a Logos Storage dataset whose manifest is built deterministically from the bytes, so that the dataset identifier is a pure function of the payload.

|  | Pros | Cons |
| --- | --- | --- |
| Inline inscription (status quo) | - Anyone can rebuild the channel's state from the chain alone. - No dependency on another network. | - Fee grows linearly with payload size. - Bounded by the maximum inscription size. |
| Off-chain body (this pattern) | - Fixed inscription cost regardless of payload size. - Payload integrity verifiable from the on-chain root. - Content addressing makes re-publication trustless. | - Availability of the payload is not guaranteed by the chain. - Readers depend on Logos Storage (or another holder) to obtain the bytes. |

## Trust Model

The pattern changes what a reader must trust, and it is important to state it plainly.

- **Integrity is cryptographic.** The dataset identifier and Merkle root inscribed on-chain bind the payload byte for byte. A reader that obtains the payload from any source can verify it.
- **Order is cryptographic.** Channel messages remain a hash chain enforced by the ledger; the pattern does not touch it.
- **Availability is social.** Logos Storage, in its current file-sharing scope, replicates data organically and offers no persistence guarantee. A writer can inscribe a commitment and withhold the payload; a payload held by a single node can be lost. This is the well-known failure mode of validium-style designs.

Three observations make this acceptable for sovereign channels today, and set the bar for what would make it robust:

1. Bedrock already trusts a channel's accredited keys for whatever the payload means. For LEZ, the base layer does not verify zone receipts. Withholding a payload is the same power a sequencer already has to halt or censor its channel, exercised through a different route.
2. The writer committee is on-chain. With decentralized sequencing every accredited key is a natural holder of the channel's payloads, and a missing payload is attributable to the key that signed the commitment.
3. Re-publication is trustless because the dataset identifier is content-derived. Persistence incentives on the Storage side, when they exist, strengthen availability without changing anything in this pattern.

## Use Cases

- **Zone blocks (LEZ).** The sequencer inscribes a block commitment (block number, parent commitment, state root, transaction root, payload reference) and publishes the transactions and their receipts as the payload. Followers fetch, verify, re-execute and only then apply. This is the priority profile.
- **Proof bundles.** A channel that wants third-party verifiability commits to a set of proofs on-chain and publishes the proofs themselves off-chain. The chain fixes which proofs were claimed at which slot.
- **Application logs.** Channels used as ordered logs by non-zone applications keep their existing payload format and gain a fixed inscription cost; only the envelope changes.
- **Dataset anchoring.** A single envelope is a timestamped, sequencer-signed commitment to an arbitrary dataset already living in Logos Storage.

## Message Flow

1. The writer serializes the payload. If it is small enough to inscribe directly, it uses the inline form and skips to step 4.
2. The writer builds a deterministic Logos Storage manifest for the payload (fixed block size, no optional attributes), publishes the dataset and waits until it is discoverable on the Storage DHT.
3. The writer builds the envelope: the dataset identifier, Merkle root and size, plus the channel-specific commitment.
4. The writer inscribes the envelope through `CHANNEL_INSCRIBE` in the usual way; for a zone this may be bundled atomically with deposits or withdrawals as today.
5. A reader observing the inscription obtains the payload, inline or by dataset identifier, verifies every block against the inscribed root, applies the channel's own validation, and only then applies the message.
6. If the payload cannot be obtained within an availability window, the reader stalls at that message. It keeps ingesting later inscriptions for ordering but applies none of them until the payload appears. Skipping is never allowed, because later commitments depend on the skipped state.

The publication order is the one invariant that matters: **upload before inscribe.** It turns a missing payload into a re-publication problem rather than a data-loss problem.

## Requirements on Logos Storage

This pattern can be specified normatively and implemented only once Logos Storage provides the following. They are listed here as a demand signal towards the Storage roadmap.

- **Deterministic dataset identifiers.** Given fixed block size and no optional manifest attributes, the same bytes must always yield the same dataset identifier, so that any holder can re-publish under the identifier already on-chain.
- **Retrieval with proofs.** A reader must be able to fetch individual blocks together with Merkle proofs against the tree root, so that partial and untrusted sources can be verified.
- **Discovery.** Announcing a dataset on the DHT and looking it up must have a bounded, measurable latency, which sets the availability window.
- **A persistence primitive.** At minimum, a way for a node to pin a dataset locally and advertise that it holds it. Incentivized persistence is the eventual goal; without at least pinning, availability rests on unstated operator behaviour.
- **Privacy-preserving publication.** Uploads and provider announcements should not leak more about the writer than the accredited key already reveals on-chain.

# Security and Privacy Considerations

- **Data withholding** is the primary risk and is discussed under Trust Model. The stall rule makes it observable and attributable; it does not prevent it.
- **Integrity** rests on the collision resistance of the hash used by Logos Storage for its Merkle trees and on the inscribed root; a reader must reject any block that does not verify.
- **Privacy.** The payload is public on Logos Storage, as it would be on-chain. For LEZ this exposes nothing beyond what an inscribed block already exposes (ciphertexts, nullifiers, public state). Timing of uploads and DHT announcements may correlate a Storage provider with a channel writer whose key is already public.
- **Fee accounting** is unchanged: the inscribing transaction pays the fixed execution gas and the storage gas of the envelope only.

# Open Questions

1. **Retention.** Who must keep a payload available, and for how long: accredited writers while in the committee, archivers, a fixed window, or indefinitely. This is left open until the Storage roadmap settles persistence.
2. **Hash alignment.** Whether channel-level roots (transaction root, commitment identifier) should use the hash of the Storage Merkle tree or Mantle's hash.
3. **Receipts in the payload.** Whether a zone should publish receipts at all once its sequencer has verified them, trading third-party verifiability for size.
4. **Envelope registration.** Whether the envelope should carry a recognizable tag so that generic indexers can identify off-chain bodies on channels they do not otherwise understand.

# Future Work

Once the requirements on Logos Storage are met, a Standards Track specification (or a CFR against LEE) will define the envelope's wire format, the availability window, the inline threshold and the reader state machine.
