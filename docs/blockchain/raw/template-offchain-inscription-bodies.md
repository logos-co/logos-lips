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
| 1.0.0 | Initial version. | 2026-10-13 |

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

## Interim Deployment: Writer-Pinned Bodies

Until Logos Storage offers a persistence primitive, the pattern can still be deployed with availability that does not depend on the Storage network at large. The rule is the second observation above, made explicit:

- Every accredited writer of the channel keeps a local copy of every payload it has published and of every payload it has verified from its co-writers, for as long as it is in the committee and for a retention window after leaving it, and advertises these datasets on the Storage DHT.
- Archivers (indexers, explorers, anyone with an interest in the channel's history) may do the same for any part of the history; because identifiers are content-derived, a reader cannot tell a writer's copy from an archiver's and does not need to.

Under this rule the providers a reader finds are, at minimum, the channel's own committee. Availability then has the same trust basis as the channel itself, the committee's liveness, and a payload is lost only if every writer that held it is gone, which is also the condition under which the channel can no longer progress. Logos Storage is used for what it provides today, content addressing, discovery and transport, and nothing is assumed about replication beyond the committee. When Storage persistence arrives it adds holders; it does not change the rule.

One condition on the pinning nodes follows from the first measurements below: they must be **directly reachable** (a public address, or a working port mapping). A Storage node that only has relayed addresses can publish and be discovered, but the circuit relays carry at most one block per circuit, so it cannot serve a body of any realistic size. For a sequencer committee this is an operational requirement, not a protocol change.

The rule is also what makes measurements meaningful before Storage persistence exists: with writer-pinned providers, a measurement exercises nodes the channel operates rather than the current state of a network whose composition it does not control.

## Use Cases

- **Zone blocks (LEZ).** The sequencer inscribes a block commitment (block number, parent commitment, state root, transaction root, payload reference) and publishes the transactions and their receipts as the payload. Followers fetch, verify, re-execute and only then apply. This is the priority profile.
- **Proof bundles.** A channel that wants third-party verifiability commits to a set of proofs on-chain and publishes the proofs themselves off-chain. The chain fixes which proofs were claimed at which slot.
- **Application logs.** Channels used as ordered logs by non-zone applications keep their existing payload format and gain a fixed inscription cost; only the envelope changes.
- **Dataset anchoring.** A single envelope is a timestamped, sequencer-signed commitment to an arbitrary dataset already living in Logos Storage.

## Payload Sizes

The sizes Logos Storage has to serve are set by the priority profile. A LEZ privacy transaction carries a `risc0_zkvm::InnerReceipt` ([LEE v0.3](lez/lee-v0.3-specifications.md)), and the receipt dominates the transaction. Nominal sizes, from the risc0 documentation rather than measured here:

| Receipt kind | Size per transaction | Note |
| --- | --- | --- |
| Composite (prover default) | 1–3 MB | STARK segments, no compression |
| Succinct | about 200 KB | recursive compression, provable on ordinary hardware |
| Groth16-wrapped | about 300 B | SNARK wrap, today needs an x86_64 host |

A zone block body is the transactions and their receipts, so a block of `n` privacy transactions is a few hundred bytes with Groth16-wrapped receipts, `n × 200 KB` with succinct receipts and `n × 1–3 MB` with composite ones. The inline threshold, the availability window and the measurement plan below are all expressed against these three points.

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
- **Transfer that does not depend on the relays.** Nodes behind NAT currently reach each other only through the network's circuit relays, whose default data limit (128 KiB per circuit in the libp2p implementation in use) is below a single succinct receipt. Either providers of bodies are directly reachable, or the relays are sized for the payloads, or hole punching works; the pattern needs one of the three to hold for the pinning nodes.

# Security and Privacy Considerations

- **Data withholding** is the primary risk and is discussed under Trust Model. The stall rule makes it observable and attributable; it does not prevent it.
- **Integrity** rests on the collision resistance of the hash used by Logos Storage for its Merkle trees and on the inscribed root; a reader must reject any block that does not verify.
- **Privacy.** The payload is public on Logos Storage, as it would be on-chain. For LEZ this exposes nothing beyond what an inscribed block already exposes (ciphertexts, nullifiers, public state). Timing of uploads and DHT announcements may correlate a Storage provider with a channel writer whose key is already public.
- **Fee accounting** is unchanged: the inscribing transaction pays the fixed execution gas and the storage gas of the envelope only.

# Measurement Plan

The normative layer needs three numbers that this document does not have: the availability window, the inline threshold and the retention window. Before it is written, the following are to be measured on a controlled testbed, with a committee-sized set of writer-pinned providers (see Interim Deployment) and a reader that holds none of the data:

1. **Discovery latency.** Time from a provider's DHT announcement to the dataset being resolvable by the reader. This bounds the "wait until discoverable" step of the message flow and is the main input to the availability window.
2. **Fetch time by payload size.** Time to obtain and verify a body of about 300 B, about 200 KB and about 3 MB, the three receipt points above, from the pinned providers; then for a block of several such transactions.
3. **Fetch under provider churn.** The same with a fraction of the providers offline, down to a single remaining holder, which is the case the stall rule has to survive.
4. **Verification on the reader.** Time to verify one receipt of each kind and to re-execute a block, since the reader applies a message only after both.

The results are a floor, not a forecast: they measure the protocol with providers the channel controls, and say nothing about how long a payload survives on Storage without them, which depends on the persistence primitive this document asks for. They are enough to set the three parameters for the interim deployment, and they establish the method to be repeated once Storage persistence exists.

## First Measurements

Logos Storage is live on the testnet: the Basecamp application (0.3.2) downloads its packages over it, through the Storage module (3.0.2) and the `logos-storage-nim` node (0.5.3), with an HTTPS fallback. That makes the plan above measurable against a running system rather than a mock. A first round was taken with the prebuilt 0.5.3 node, two nodes on one laptop behind a home NAT, on the `logos.dev` and `logos.test` networks. The numbers are preliminary and will be replaced by the controlled testbed; they are recorded because two of them already shape the design.

| Quantity | Observed | Setting |
| --- | ---: | --- |
| Discovery: upload on one node to manifest resolvable on the other | 14–144 s, typically 30–40 s | live DHT, both networks, 9 trials |
| Download, 64 KiB (one block) | 3–4 s | live network, through a circuit relay |
| Download, 128 KiB to 30 MB | mostly fails | live network, through a circuit relay (limit 128 KiB per circuit) |
| Download, 200 KB | 0.11 s | private two-node network, no relay, loopback |
| Download, 3 MB | 0.37 s | same |
| Download, 30 MB | 2.9 s (about 11 MB/s) | same |
| Manifest resolution | 50 ms | same |

What the two settings say. Over the live network the laptop's nodes never obtained a verified direct address (a UPnP mapping was created, AutoNAT did not confirm it), so every connection between them went through the network's relays, and the relays' per-circuit data limit decided the outcome: one block passes, a succinct receipt does not. The private network measures the protocol with no network in between: block exchange delivers a composite-receipt-sized body in well under a second and a 30 MB block of such bodies in a few seconds, so the protocol's own cost is not the constraint. The live-network transfer time for bodies above one block is therefore still unmeasured, and the next round is set up to measure it: one node with a public address (a Raspberry Pi 5 behind a port forward, the reference platform of the other measurement reports), payloads at the three receipt sizes and a 30 MB block, the laptop as the empty reader; then the same through Mix, using the Mix relay configuration the Storage module ships per network; then receipt verification on the reader.

# Open Questions

1. **Retention.** Who must keep a payload available, and for how long. The interim deployment answers the *who* (accredited writers while in the committee, archivers optionally); the *how long* after a writer leaves the committee, and whether indefinite retention is required of anyone, is left open until the Storage roadmap settles persistence.
2. **Hash alignment.** Whether channel-level roots (transaction root, commitment identifier) should use the hash of the Storage Merkle tree or Mantle's hash.
3. **Receipts in the payload.** Whether a zone should publish receipts at all once its sequencer has verified them, trading third-party verifiability for size.
4. **Envelope registration.** Whether the envelope should carry a recognizable tag so that generic indexers can identify off-chain bodies on channels they do not otherwise understand.

# Future Work

Once the requirements on Logos Storage are met, a Standards Track specification (or a CFR against LEE) will define the envelope's wire format, the availability window, the inline threshold and the reader state machine.
