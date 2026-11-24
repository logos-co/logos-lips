# [RFC] Mantle: Off-chain inscription bodies on Logos Storage

**Motivation and proposal:** [PR #454](https://github.com/logos-co/logos-lips/pull/454)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-16 |
| v2 | Added the interim deployment with writer-pinned bodies, the LEZ payload sizes and a measurement plan; the retention question narrowed accordingly. Storage status updated (live on the testnet, used by Basecamp); first measurements from a laptop and a Raspberry Pi 5 recorded, with the problems met (unreachable home connections, relay limit, swarm admission, arm64 build) and the reachability condition and relay requirement they imply | 2026-10-17 |

## Reviewer Orientation

Single-document change — read [`[Template] Off-Chain Inscription Bodies`](../template-offchain-inscription-bodies.md) top to bottom. Focus on **Trust Model** (availability is social, not guaranteed by the chain), **Interim Deployment** (writer-pinned bodies, which is what makes the pattern deployable and measurable before Storage persistence exists) and **Requirements on Logos Storage** (the list that gates a normative specification). Read the PR's Motivation first.

# Discussion

## Why Informational, and why no wire format

Logos Storage's current scope is file sharing: datasets are content-addressed and replicated organically, and there is no persistence guarantee. It is live on the testnet, where Basecamp downloads its packages over it, so the pattern can be measured against a running system. The marketplace, erasure-coding and proving specifications were deprecated in January 2026, and persistence incentives are listed on the Storage roadmap as post-mainnet research. A wire format specified against today's Storage would bind to details that are expected to change, and an implementation on today's Storage would lose payloads as replicas disappear. The document therefore fixes what does not depend on those details, the split between on-chain commitment and off-chain body, the trust model and the requirements on Storage, and leaves the normative layer (envelope encoding, availability window, inline threshold, reader state machine) for a later Standards Track specification or a CFR against LEE.

## Trust model

The pattern changes what a reader trusts, and the document says so in one place. Integrity and order stay cryptographic: the inscribed root binds the payload and the channel's hash chain binds the order. Availability becomes social: a writer can inscribe a reference and withhold the payload, and a single holder can lose it. This is acceptable for sovereign channels because the writer already holds equivalent power to halt or censor its channel, the writer committee is on-chain and a missing payload is attributable, and re-publication needs no trust because the dataset identifier is content-derived. Persistence incentives on the Storage side, when they exist, strengthen availability without changing the pattern.

## Why the measurements come later, and what they will be

The numbers the normative layer needs, the availability window, the inline threshold and the retention window, depend on how fast a payload can be discovered and fetched. Measuring that against the Storage network as it runs today would measure its current composition and stability rather than the pattern, and the result would not transfer. The document therefore does two things instead. It fixes an interim deployment in which the channel's own writers pin and advertise every body, so that the providers a reader relies on are nodes the channel operates; and it states a measurement plan against that deployment, on a controlled testbed, whose results are to be read as a floor. The plan is in the document so that it can be reviewed before it is run, and so that the Storage team can see which of their properties it exercises (discovery latency, retrieval with proofs) and which it deliberately does not (persistence).

Two rounds have been taken on the live networks with node 0.5.3, from a laptop and from a Raspberry Pi 5, and are recorded in the document under *First Measurements*, problems first. Three of the problems are inputs to this document and to the Storage side: home connections end up relay-only (one of them is behind carrier-grade NAT, where no port forward can help), relayed transfers are capped at one block by the relay's per-circuit limit, and the 0.5.3 download engine stalls when the provider is not among the first sixteen peers it happens to admit, which a `--max-peers=16` cap works around. A fourth, the arm64 release binaries not running on a Pi 5, is a build-flag issue. The document therefore requires the pinning nodes to be directly reachable and asks the Storage side for a transfer path that does not depend on the relays. The numbers are consistent across both machines: the protocol floor is a third of a second for a composite receipt, discovery through the live DHT takes seconds to a minute, and the pessimistic live path measured on the Pi fetches a succinct receipt in under four seconds. The representative case, a reachable provider and a reader elsewhere, needs a node with a public address and is the next round.

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
5. **Interim Deployment: Writer-Pinned Bodies**: accredited writers pin and advertise every body while in the committee and for a retention window after; archivers may; availability then rests on the committee's liveness, and Storage is used for addressing, discovery and transport only.
6. **Use Cases**: LEZ zone blocks (priority profile), proof bundles, application logs, dataset anchoring.
7. **Payload Sizes**: the three risc0 receipt points a LEZ body is built from (composite 1–3 MB, succinct about 200 KB, Groth16-wrapped about 300 B; nominal, from the risc0 documentation), against which the inline threshold, the availability window and the measurements are expressed.
8. **Message Flow**: serialize, publish with a deterministic manifest, wait for DHT discoverability, inscribe the envelope, fetch and verify, stall on a missing payload. The one invariant is *upload before inscribe*.
9. **Requirements on Logos Storage**: deterministic dataset identifiers, retrieval with proofs, bounded discovery latency, a persistence primitive, privacy-preserving publication.
10. **Security and Privacy Considerations**, **Measurement Plan** (discovery latency, fetch time at the three sizes, fetch under provider churn, verification on the reader; on a controlled testbed with writer-pinned providers; results read as a floor), **First Measurements** (live-network discovery and relay-limited transfer, private-network protocol floor, and the next round), **Open Questions** (retention narrowed to the window after leaving the committee, hash alignment, receipts in the payload, envelope registration) and **Future Work**.

## Chores

- Register the document in `scripts/blockchain_structure.py` under Mantle so the generated structure validates in CI:

    ```diff
         "blockchain/deprecated/v1.0.0-template-cross-channel-messaging.md": ("Mantle", "[1.0.0] [Template] Cross-Channel Messaging"),
    +    "blockchain/raw/template-offchain-inscription-bodies.md": ("Mantle", "[Template] Off-Chain Inscription Bodies"),
    ```

# Implementation

- [ ]  No implementation required (Informational template); the normative layer is gated on the document's *Requirements on Logos Storage* and on the measurement plan.
- [ ]  Agree the interim pinning rule with the LEZ side (who pins, the retention window after leaving the committee).
- [x]  First rounds on the live networks and on private two-node networks, laptop and Raspberry Pi 5, node 0.5.3 (discovery latency, relay limit, swarm admission, protocol floor, live numbers with the `--max-peers=16` workaround); recorded under *First Measurements*.
- [ ]  Report upstream: the arm64 release build flag, and the swarm admission behaviour with the trace evidence.
- [ ]  Live transfer from a directly reachable provider: a node with a public address as writer (the home connections used so far cannot provide one), the three receipt sizes and a 30 MB block, an empty reader elsewhere, with and without the swarm workaround; then the same through Mix with the per-network Mix configuration of the Storage module.
- [ ]  Build the full harness of the *Measurement Plan*: a committee-sized set of pinned providers and one empty reader on a controlled testbed; record discovery latency, fetch time, fetch under churn and reader verification time.
- [ ]  Ask the Storage team whether the relay data limit is intended on the fleet relays, and whether hole punching is expected to work between NATed nodes.
- [ ]  Track the Storage-side prerequisites (deterministic dataset identifiers, retrieval with proofs, discovery latency, a persistence primitive) with the Storage team, and open the normative specification or a CFR against LEE once they are met.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [`[Template] Off-Chain Inscription Bodies`](../template-offchain-inscription-bodies.md) | Created | raw, Informational |
