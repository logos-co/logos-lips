# [RFC] Trusted Setup: Extend the Perpetual Powers of Tau for the mainnet circuits

**Motivation and proposal:** [PR #535](https://github.com/logos-co/logos-lips/pull/535)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-12 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then the [Trusted Setup Ceremony](#affected-specifications) top to bottom. Focus on the [split of the secrets between the phases](#1-the-phases-as-bgm17-defines-them), the [source of Phase 1](#4-phase-1-extends-the-perpetual-powers-of-tau) and its fallback, and the [freeze rule](#8-a-circuit-is-frozen-before-its-phase-2). The constraint counts come from the circuits under review in logos-blockchain-circuits PR #73, not from master.

# Discussion

## A description no tool implements

Revision 1.0.1 presented $\alpha$, $\beta$, $\gamma$ and $\delta$ as four secrets sampled in Phase 2 for each circuit, and Phase 1 as the powers of $\tau$ alone, in $`\mathbb{G}_1`$ up to degree $n$ and in $`\mathbb{G}_2`$ up to degree $1$. No ceremony software works this way, and the circuits repository already derives its keys with snarkjs. In the protocol of [BGM17] that snarkjs implements, $\alpha$ and $\beta$ are part of the Powers of Tau, the $`\mathbb{G}_2`$ powers go up to $n - 1$ and the $`\mathbb{G}_1`$ powers to $2n - 2$, Phase 2 contributes to $\delta$ alone and $\gamma$ is $1$. A ceremony run from the old description would have produced parameters no prover reads. The revision describes the phases the tools run, so that the ceremony software, the verifiers and this document agree.

## Why extend the Perpetual Powers of Tau

Three sources of Phase 1 were weighed.

- **A closed file.** The prepared `powersOfTau28_hez_final_*.ptau` files inherit the 54 contributions of the Perpetual Powers of Tau (PPoT) and the beacon Hermez applied, and the circuits repository uses one for its test keys. A beacon closes a chain, so no Logos participant can join it: the soundness of the mainnet keys would rest on a ceremony Logos took no part in.
- **A ceremony from scratch.** At degree $`2^{18}`$ a contribution takes seconds, and the whole transcript would be Logos's own. It would also rest on the Logos participants alone, fewer and less independent than the PPoT's.
- **Extending the PPoT.** The Logos contributions follow the PPoT's in one chain, so the output is sound if one participant of either set erased its secret. The cost is the import and verification of the PPoT responses at degree $`2^{28}`$, about 100 GB each, once, and the dependence on obtaining them from the PPoT archive now that its public buckets are gone.

The revision takes the third, with the first as the fallback if the responses cannot be obtained and verified, and documents the fallback so that the choice is visible in the transcript.

## Degree

The largest circuit, the ZkProgramSpend, has 91,629 constraints, under $`2^{17} = 131,072`$. The audit of the circuits is not finished, and a constraint added past that bound would force a second Phase 1. $`2^{18}`$ leaves the room, at twice the file size, 300 MB instead of 150 MB, and twice the contribution time, both negligible. A universal setup, which would let the circuits change without a new Phase 2, was not pursued: Groth16 leaves the Logos Blockchain with its post-quantum migration, and the PPoT at degree $`2^{28}`$ stays available for any proof system that needs it.

## Dependencies

The four circuits and their constraint counts are those of the private ledger of Mantle, logos-lips PRs #480 and #481 and logos-blockchain-circuits PR #73, under review. The specification links the Mantle document without anchors to their sections until those PRs land, and the counts will move with the audit. The RLN row of the Scope table is a `TODO (author)` for the Zerokit team: the frozen circuit and version, its constraint count, its specification and the verifier of its Phase 2.

## Compatibility

Bedrock has no deployed network and no production keys exist, so nothing migrates. The test keys the circuits CI derives from `powersOfTau28_hez_final_17.ptau` with one unverified contribution stay test keys, and the node pins the hashes of the ceremony's verification keys when they exist.

# Details

## 1. The phases as [BGM17] defines them

Phase 1 produces the powers of $\tau$ and their products with $\alpha$ and $\beta$. Phase 2 contributes to $\delta$ alone, and $\gamma = 1$:

```diff
-Phase 2 ... introduces four additional toxic waste scalars α, β, γ, δ ...
-For the τ secret in Groth16 ... m = 1. In contrast, the parameters α, β, γ, δ each require only n = m = 0.
+Phase 1, the Powers of Tau ... produces encodings of the powers of τ, and of those powers multiplied by α and β, up to a degree n.
+Phase 2 ... its participants contribute to δ alone. γ is fixed to 1.
```

The Phase 2 key is written out with its public input elements $`\mathrm{IC}_i`$, which Phase 1 fixes, and its private input and quotient elements, which each contribution divides by $`r_\delta`$.

## 2. The shape of the Phase 1 accumulator

```math
\left([\tau^i]_1\right)_{i=0}^{2n-2},\quad \left([\tau^i]_2\right)_{i=0}^{n-1},\quad \left([\alpha\tau^i]_1\right)_{i=0}^{n-1},\quad \left([\beta\tau^i]_1\right)_{i=0}^{n-1},\quad [\beta]_2
```

replacing the $n + 1$ elements in $`\mathbb{G}_1`$ and $m + 1 = 2$ in $`\mathbb{G}_2`$ of 1.0.1. The well-formedness check is restated over these sequences, with the $\alpha$ and $\beta$ sequences tied to the powers and the two encodings of $\beta$ tied to each other.

## 3. Scope and degree

A new Scope section lists the five circuits of the ceremony, the four of the Logos Blockchain with their constraint counts and the RLN circuit of Zerokit, fixes the degree $`n = 2^{18}`$, and excludes the program circuits registered with `PROGRAM_REGISTER`, whose authors run their own Phase 2 on the same Phase 1.

## 4. Phase 1 extends the Perpetual Powers of Tau

The coordinator imports and verifies the PPoT responses into an accumulator of degree $`2^{28}`$, truncates it to $`2^{18}`$ and publishes the truncated accumulator, its hash and the response it ends at as the first challenge. If the responses cannot be obtained, the ceremony falls back to a closed `powersOfTau28_hez_final_*.ptau`, verified and pinned by hash, and runs Phase 2 alone. The 1.0.1 section on extending an existing ceremony named no ceremony and no procedure.

## 5. The beacon

Each phase closes with a random beacon applied after the last participant, a public value fixed after that contribution, hashed a published number of times, and Phase 1 is then prepared for Phase 2. 1.0.1 had no beacon.

## 6. Proof of knowledge bound to the transcript

A contribution proves each secret $s$ with $`([s]_1, s \cdot H)`$, $H$ being the hash of the transcript and of $`[s]_1`$ mapped to $`\mathbb{G}_2`$, checked by $`e([s]_1, H) = e(G_1, s \cdot H)`$ and $`e([\tau']_1, H) = e([\tau]_1, r_\tau \cdot H)`$. This is the form of proof snarkjs uses. It replaces the Schnorr proof of 1.0.1, which bound the secret to nothing but the two $`\mathbb{G}_1`$ elements.

## 7. Participant software and transcript

Reproducible builds of the ceremony software, a signed publication of the hashes and proofs of each contribution by the participant and by the coordinator, every intermediate file kept, full verification by the project before any hash is pinned, secrets from the system generator mixed with the participant's own entropy and never written to disk, and a coordinator with no secret and no authority over the output.

## 8. A circuit is frozen before its Phase 2

A circuit is frozen after its audit, the hash of its R1CS is published with its initial key, and any later change to the circuit takes a new Phase 2 for that circuit alone, Phase 1 and the other circuits standing. The dates are a `TODO (author)`, to be agreed with the Zerokit team.

## 9. Post-quantum note

The CRS gives Groth16 no post-quantum soundness, the secrecy of the ceremony protects soundness and not confidentiality, so it is not a harvest now, decrypt later exposure, and Groth16 leaves the Logos Blockchain in the third phase of its post-quantum migration.

## Chores

- The base field $`\mathbb{F}_q`$ and the scalar field $`\mathbb{F}_r`$ are distinguished, where 1.0.1 wrote $p$ for both, and the ~100-bit security of BN254 is stated.
- The Annex pseudocode, which did not parse and used the $m = 1$ shape, is replaced by the snarkjs command flow of each step.
- References add [BGM17], the PPoT repository and snarkjs, and the glued titles of the existing ones are fixed.
- Revision History row 1.1.0.

# Implementation

- [ ] Have the Zerokit team fill in the RLN row of the Scope table (frozen circuit and version, constraint count, specification, Phase 2 verifier) and agree the dates
- [ ] Obtain the PPoT responses, import and verify the chain at degree $`2^{28}`$, truncate to $`2^{18}`$, publish the first challenge with its hash
- [ ] Ship the ceremony software as a Logos module with reproducible builds, contributing to Phase 1 and to the Phase 2 of the five circuits in one session
- [ ] Run Phase 1, apply the beacon, prepare for Phase 2, publish the final `.ptau` and pin its hash in the specification
- [ ] Freeze the four circuits after the audit and publish the hash of each R1CS
- [ ] Run Phase 2 for each circuit, apply the beacon, export the verification keys and pin their hashes in the node
- [ ] Publish the whole transcript and verify it with the published software from the first challenge to the last key
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Trusted Setup Ceremony](../trusted-setup-ceremony.md) | Modified | 1.1.0 |
