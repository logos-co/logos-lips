# [RFC] Mantle: Off-chain inscription bodies on Logos Storage

**Motivation and proposal:** [PR #454](https://github.com/logos-co/logos-lips/pull/454)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-16 |

## Reviewer Orientation

Single-document change — read [`[Template] Off-Chain Inscription Bodies`](../template-offchain-inscription-bodies.md) top to bottom. Focus on **Trust Model** (availability is social, not guaranteed by the chain) and **Requirements on Logos Storage** (the list that gates a normative specification). Read the PR's Motivation first.

# Discussion

## Why Informational, and why no wire format

Logos Storage's current scope is file sharing: datasets are content-addressed and replicated organically, and there is no persistence guarantee. The marketplace, erasure-coding and proving specifications were deprecated in January 2026, and persistence incentives are listed on the Storage roadmap as post-mainnet research. A wire format specified against today's Storage would bind to details that are expected to change, and an implementation on today's Storage would lose payloads as replicas disappear. The document therefore fixes what does not depend on those details, the split between on-chain commitment and off-chain body, the trust model and the requirements on Storage, and leaves the normative layer (envelope encoding, availability window, inline threshold, reader state machine) for a later Standards Track specification or a CFR against LEE.

## Trust model

The pattern changes what a reader trusts, and the document says so in one place. Integrity and order stay cryptographic: the inscribed root binds the payload and the channel's hash chain binds the order. Availability becomes social: a writer can inscribe a reference and withhold the payload, and a single holder can lose it. This is acceptable for sovereign channels because the writer already holds equivalent power to halt or censor its channel, the writer committee is on-chain and a missing payload is attributable, and re-publication needs no trust because the dataset identifier is content-derived. Persistence incentives on the Storage side, when they exist, strengthen availability without changing the pattern.

## Alternatives

- **Inscribe full payloads and shrink them** (for LEZ: Groth16-wrap every receipt). Keeps chain-only reconstructibility. Rejected as the default because the wrap is heavy and today needs an x86_64 host, which excludes small sequencers; the document keeps inline inscription as an option.
- **Zone-level gossip without Storage.** Cheapest, but gives late-joining readers no discovery. The document keeps gossip as a fast path and Storage as the rendezvous.
- **A LEZ-only block format.** Every later channel with large payloads would re-invent the reference, the deterministic manifest and the stall rule. The generic envelope costs one tag byte.

## Compatibility

None affected. The ledger treats inscription payloads as opaque bytes, and the pattern is opt-in per channel.

## Review finding

LEE v0.3 does not define what a sequencer inscribes; the earlier LEZ testnet code inscribed the whole serialized block. The document points at this gap but does not modify LEE. When the normative layer lands, LEE should gain a settlement-payload section or a CFR.

# Details

The change is one new Informational document, `docs/blockchain/raw/template-offchain-inscription-bodies.md` (Status raw, Category Informational, modeled on `[Template] Cross-Channel Messaging`). It carries no normative rule for Bedrock. Its sections, in order:

1. **Introduction** and references (Mantle, LEE v0.3, Logos Storage Datasets).
2. **Objectives** and **Requirements**: fixed inscription cost independent of payload size; order and commitment kept on-chain; one pattern for zone blocks, proof bundles, logs and anchors; no Bedrock change.
3. **Overview**: the on-chain envelope (dataset identifier, Merkle root, size, channel commitment) versus the off-chain payload, with a pros and cons table against inline inscription.
4. **Trust Model**: integrity and order cryptographic, availability social, and the three reasons this holds for sovereign channels.
5. **Use Cases**: LEZ zone blocks (priority profile), proof bundles, application logs, dataset anchoring.
6. **Message Flow**: serialize, publish with a deterministic manifest, wait for DHT discoverability, inscribe the envelope, fetch and verify, stall on a missing payload. The one invariant is *upload before inscribe*.
7. **Requirements on Logos Storage**: deterministic dataset identifiers, retrieval with proofs, bounded discovery latency, a persistence primitive, privacy-preserving publication.
8. **Security and Privacy Considerations**, **Open Questions** (retention, hash alignment, receipts in the payload, envelope registration) and **Future Work**.

## Chores

- Register the document in `scripts/blockchain_structure.py` under Mantle so the generated structure validates in CI:

    ```diff
         "blockchain/deprecated/v1.0.0-template-cross-channel-messaging.md": ("Mantle", "[1.0.0] [Template] Cross-Channel Messaging"),
    +    "blockchain/raw/template-offchain-inscription-bodies.md": ("Mantle", "[Template] Off-Chain Inscription Bodies"),
    ```

# Implementation

- [ ]  No implementation required (Informational template); implementation is gated on the document's *Requirements on Logos Storage* being met.
- [ ]  Track the Storage-side prerequisites (deterministic dataset identifiers, retrieval with proofs, discovery latency, a persistence primitive) with the Storage team, and open the normative specification or a CFR against LEE once they are met.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [`[Template] Off-Chain Inscription Bodies`](../template-offchain-inscription-bodies.md) | Created | raw, Informational |
