# TRUSTED-SETUP-CEREMONY

| Field | Value |
| --- | --- |
| Name | Trusted Setup Ceremony |
| Slug | 207 |
| Status | raw |
| Category | Standards Track |
| Editor | Mehmet Gonen <mehmet@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/trusted-setup-ceremony.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2025-09-04 |
| 1.0.1 | Renamed Nomos to Logos Blockchain. Removed mentions of DA. | 2026-04-23 |
| 1.1.0 | Described the two phases as snarkjs runs them: $\alpha$ and $\beta$ belong to Phase 1, Phase 2 contributes to $\delta$ alone and $\gamma = 1$. Gave the Phase 1 accumulator its full shape. Fixed the scope to the four mainnet circuits and the RLN circuit, with a Phase 1 of degree $2^{18}$ extended from the Perpetual Powers of Tau. Added the random beacon, the freeze rule, the participant software and transcript requirements, the post-quantum note. Replaced the Annex pseudocode with the command flow. Separated the base field from the scalar field. | 2026-11-12 |

# Introduction

The Logos Blockchain proves its ledger transitions, its leadership and its Blend quota with Groth16 ([Common Cryptographic Components - Groth16](common-cryptographic-components.md#groth16-zk-snark)). Groth16 proves against a Common Reference String (CRS) that encodes secret scalars, and whoever knows those scalars forges proofs. The CRS is therefore produced by a multi-party computation, the trusted setup ceremony, in which each participant applies a secret of its own and destroys it: the CRS is sound as long as one participant destroyed its secret.

This document fixes the ceremony of the Logos Blockchain: the circuits it covers, the source and the size of its first phase, the contribution and verification steps of both phases, the random beacon closing each phase, the software and the transcript, and the rule for changing a circuit once its keys exist. The Logos Blockchain shares the ceremony with the RLN circuit of Zerokit, so that a participant contributes to every Logos circuit in one session.

# Overview

## Two phases

A Groth16 CRS has five secret scalars, $\tau, \alpha, \beta, \gamma, \delta$, and the ceremony produces it in two phases, as [BGM17] describes and snarkjs implements:

- **Phase 1, the Powers of Tau**, is independent of any circuit. It produces encodings of the powers of $\tau$, and of those powers multiplied by $\alpha$ and $\beta$, up to a degree $n$. Any circuit of at most $n$ constraints derives its keys from it, so one Phase 1 serves every circuit of the ceremony.
- **Phase 2** is specific to one circuit. It starts from the output of Phase 1 and the constraint system of the circuit, and its participants contribute to $\delta$ alone. $\gamma$ is fixed to $1$: it only separates the public inputs from the private ones, which $\delta$ already does.

A participant of either phase downloads the current accumulator, multiplies the elements its secret acts on by powers of that secret, publishes the new accumulator with a proof that it knows the secret and applied it consistently, and destroys the secret. A random beacon, a public value nobody controls, closes each phase as a last contribution. Every intermediate file stays public, so that anyone can verify the whole chain afterwards.

## Security

Let $N$ be the number of participants of a phase. The output stays sound against an adversary who corrupts $N - 1$ of them, under the q-SDH and knowledge-of-exponent assumptions of pairing groups, provided one honest participant erased its secret. Three points follow:

- **One honest participant.** The trust assumption is on the ceremony as a whole, not on any participant, so the ceremony takes as many independent participants as it can, and inherits the participants of an earlier ceremony when it extends one.
- **Erasure.** The analysis is in the secure erasure model: a participant deletes its secret after its contribution. Compromising a participant later gives the adversary nothing.
- **Beacon.** The last participant of a phase sees every earlier contribution and could bias the output toward a value of its choice. The beacon, applied after it, removes that influence ([BGM17], [WCB25]).

## Curve and fields

The circuits are over BN254, whose scalar field $`\mathbb{F}_r`$ is the field of `zkhash` and of every circuit signal, $r$ being the modulus `p` of the [Mantle specification](bedrock-v1.1-mantle-specification.md#arithmetic). The curve points lie over the base field $`\mathbb{F}_q`$ and its extensions, and $`\mathbb{G}_1`$, $`\mathbb{G}_2`$ and $`\mathbb{G}_T`$ are their subgroups of order $r$, with the pairing $`e: \mathbb{G}_1 \times \mathbb{G}_2 \to \mathbb{G}_T`$ and the fixed generators $`G_1`$, $`G_2`$. $`[x]_1 = x \cdot G_1`$ and $`[x]_2 = x \cdot G_2`$ denote the encodings of a scalar $x$. BN254 gives about 100 bits of security against the best known discrete logarithm attacks, less than its 128-bit design target. The Logos Blockchain accepts this for the proving time, the proof size and the tooling of the curve (circom, snarkjs, rapidsnark), and leaves Groth16 with its post-quantum migration ([Post-quantum note](#post-quantum-note)).

# Scope

The ceremony covers the four circuits of the Logos Blockchain mainnet and the RLN circuit of Zerokit, all Groth16 over BN254, compiled with circom and proven with snarkjs or rapidsnark:

| Circuit | Specification | Constraints |
| --- | --- | --- |
| ZkTransfer | [Mantle](bedrock-v1.1-mantle-specification.md), Zero Knowledge Transfer Proof | 64,615 |
| ZkProgramSpend | [Mantle](bedrock-v1.1-mantle-specification.md), Zero Knowledge Program Spend Proof | 91,629 |
| Proof of Leadership | [Cryptarchia - Proof of Leadership](cryptarchia-proof-of-leadership.md) | 51,863 |
| Proof of Quota | [Proof of Quota](proof-of-quota.md) | 47,215 |
| RLN | Zerokit | > **TODO (author):** to be filled in by the Zerokit team |

The constraint counts are those of the circuits under review and move until the circuits are frozen ([Freezing the circuits](#freezing-the-circuits)). The RLN row is the Zerokit team's to complete: the circuit and the version it freezes for the ceremony, its constraint count, where it is specified, and who verifies its Phase 2. Phase 1 has degree $`n = 2^{18}`$: the largest circuit takes under half of it, which leaves room for the fixes of the audit without a second Phase 1.

The program circuits that users register with the `PROGRAM_REGISTER` Operation of [Mantle](bedrock-v1.1-mantle-specification.md) are not part of the ceremony. Their authors derive their keys from the same Phase 1 and run their own Phase 2, and the ledger only checks a registered verification key against the proofs that name it.

# Protocol

## Phase 1: Powers of Tau

### The accumulator

Phase 1 produces, for the degree $n$,

```math
\left([\tau^i]_1\right)_{i=0}^{2n-2},\quad \left([\tau^i]_2\right)_{i=0}^{n-1},\quad \left([\alpha\tau^i]_1\right)_{i=0}^{n-1},\quad \left([\beta\tau^i]_1\right)_{i=0}^{n-1},\quad [\beta]_2
```

This is the content of a snarkjs `.ptau` file before it is prepared for Phase 2. The $`\mathbb{G}_1`$ powers go to $2n - 2$ because the quotient polynomial of a circuit of $n$ constraints has degree $2n - 2$. The accumulator starts at $`\tau = \alpha = \beta = 1`$ when a ceremony starts from scratch, and at the output of an earlier ceremony when it extends one.

### Source: the Perpetual Powers of Tau

Phase 1 of the Logos ceremony extends the [Perpetual Powers of Tau](https://github.com/privacy-scaling-explorations/perpetualpowersoftau) (PPoT), the BN254 ceremony of degree $`2^{28}`$ run by Privacy and Scaling Explorations since 2019, whose public transcript holds the response of every contribution. Extending it means that the Logos CRS is sound if one PPoT participant or one Logos participant destroyed its secret. The coordinator:

1. Obtains the response files of the PPoT contributions, from the PPoT repository, its IPFS or torrent mirrors or its archive, and imports them one after the other into a `.ptau` file of degree $`2^{28}`$ started from scratch. Each import verifies the response against the accumulator before it, so the import of the whole chain is its verification. The files are about 100 GB each, so this step takes storage and days of computation, once.
2. Truncates the resulting accumulator to the degree $`n = 2^{18}`$. Truncation keeps the first elements of each sequence above, so anyone recomputes the truncated accumulator from the public responses and checks it.
3. Publishes the truncated accumulator, its hash and the number of the PPoT response it ends at, as the first challenge of the Logos Phase 1.

The CRS the PPoT published with its own beacon, and the prepared `powersOfTau28_hez_final_*.ptau` files that Hermez derived from the first 54 contributions of the PPoT, are already closed by a beacon and cannot be extended. The repository of the circuits uses `powersOfTau28_hez_final_17.ptau` for its test keys, pinned by its SHA-256. If no PPoT response can be obtained and verified, the ceremony falls back to one of those closed files, verified with `snarkjs powersoftau verify` and pinned by hash in this document, and runs Phase 2 alone. Phase 1 is then the PPoT's, with no Logos participant in it.

### Contribution

Participant $i$ receives the current accumulator and:

1. Samples three secrets $`r_\tau, r_\alpha, r_\beta`$ uniformly from $`\mathbb{F}_r^*`$.
2. Multiplies each element by the matching power of its secrets: $`[\tau^j]_1 \mapsto r_\tau^j \cdot [\tau^j]_1`$, likewise in $`\mathbb{G}_2`$, $`[\alpha\tau^j]_1 \mapsto r_\alpha r_\tau^j \cdot [\alpha\tau^j]_1`$, $`[\beta\tau^j]_1 \mapsto r_\beta r_\tau^j \cdot [\beta\tau^j]_1`$ and $`[\beta]_2 \mapsto r_\beta \cdot [\beta]_2`$.
3. Publishes, for each secret $s$, a proof of knowledge $`([s]_1,\ [s]_2^{H})`$, where $`[s]_2^{H} = s \cdot H`$ and $H$ is the hash of the transcript so far and of $`[s]_1`$ mapped to $`\mathbb{G}_2`$. Binding the proof to the transcript stops a participant from replaying or deriving another participant's proof.
4. Publishes the new accumulator and the hash of the file it received, then erases its secrets and the memory that held them.

Each secret is non-zero, so a contribution never erases the earlier ones.

### Verification of a contribution

A verifier holds the previous accumulator, the new one and the proofs, and checks:

1. **Knowledge of each secret.** $`e([s]_1, H) = e(G_1, [s]_2^{H})`$ for each of $`r_\tau, r_\alpha, r_\beta`$, with $H$ recomputed from the transcript.
2. **The secret was applied.** $`e([\tau']_1, H) = e([\tau]_1, [r_\tau]_2^{H})`$ for the first power, and likewise $`[\alpha']_1`$ against $`[\alpha]_1`$ and $`[\beta']_1`$ against $`[\beta]_1`$, where the primed elements are the new accumulator's. The first element of each sequence is non-zero.
3. **The new accumulator is well formed.** For a random $`\rho \in \mathbb{F}_r^*`$ drawn by the verifier, with sums over the new accumulator,
   $`e\left(\sum_{i=0}^{2n-3} \rho^i [\tau^i]_1,\ [\tau]_2\right) = e\left(\sum_{i=0}^{2n-3} \rho^i [\tau^{i+1}]_1,\ G_2\right)`$ ties every $`\mathbb{G}_1`$ power to the next, the same check with the roles of the groups exchanged ties the $`\mathbb{G}_2`$ powers, $`e\left(\sum_i \rho^i [\alpha\tau^i]_1,\ [\tau]_2\right) = e\left(\sum_i \rho^i [\alpha\tau^{i+1}]_1,\ G_2\right)`$ and the same for $\beta$ tie the $\alpha$ and $\beta$ sequences to the powers, and $`e([\beta]_1, G_2) = e(G_1, [\beta]_2)`$ ties the two encodings of $\beta$.

A single random $\rho$ checks a whole sequence with two pairings: a sequence that is not a geometric progression passes with probability about $`2n/r`$. `snarkjs powersoftau verify` runs these checks over the whole chain of a `.ptau` file, from its initialization to its last contribution.

### Beacon and preparation

After the last participant, the coordinator applies the beacon: a public value fixed after that participant's contribution, such as the hash of a block of a public chain at a height announced in advance, hashed a published number of times. The result is a last contribution whose secret is public and that nobody could choose. The coordinator then prepares the accumulator for Phase 2, which adds the Lagrange basis evaluations snarkjs needs, and publishes the final `.ptau` with its hash. The hash is pinned in this document once it exists.

## Phase 2: one setup per circuit

### Initialization

For each circuit, the coordinator compiles the frozen circuit to R1CS, publishes the hash of the R1CS, and derives the initial proving key from the R1CS and the final Phase 1 file (`snarkjs groth16 setup`, or `zkey new`). This key has $`\delta = 1`$ and $`\gamma = 1`$. Its elements are those of the Groth16 proving key:

```math
[\alpha]_1,\ [\beta]_1,\ [\beta]_2,\ [\delta]_1,\ [\delta]_2,\quad \left([\tau^i]_1\right),\ \left([\tau^i]_2\right),\quad \left(\mathrm{IC}_i = \left[\beta u_i(\tau) + \alpha v_i(\tau) + w_i(\tau)\right]_1\right)_{i \text{ public}},\quad \left(L_i = \left[\tfrac{\beta u_i(\tau) + \alpha v_i(\tau) + w_i(\tau)}{\delta}\right]_1\right)_{i \text{ private}},\quad \left(\left[\tfrac{\tau^i\, t(\tau)}{\delta}\right]_1\right)
```

where $`u_i, v_i, w_i`$ are the polynomials of the constraint system, $t$ the vanishing polynomial of the evaluation domain, and $`\gamma = 1`$ leaves the public input elements $`\mathrm{IC}_i`$ as they come from Phase 1.

### Contribution

A participant samples $`r_\delta`$ uniformly from $`\mathbb{F}_r^*`$, multiplies $`[\delta]_1`$ and $`[\delta]_2`$ by $`r_\delta`$ and every $`L_i`$ and every quotient element by $`r_\delta^{-1}`$, publishes the proof of knowledge $`([r_\delta]_1, [r_\delta]_2^{H})`$ as in Phase 1, and erases $`r_\delta`$. The other elements of the key do not change. A participant of the Logos ceremony contributes to the five circuits in one session of the ceremony software, one contribution each.

### Verification

`snarkjs zkey verify` takes the R1CS, the final Phase 1 file and a proving key, and checks that the key's Phase 1 elements and public input elements are those the R1CS and the Phase 1 file give, that each contribution's proof of knowledge holds and was applied to $`[\delta]_1`$ and $`[\delta]_2`$ consistently, and that the private input and quotient elements are the initial ones divided by the product of the contributions, through pairing checks of the form $`e(L_i, [\delta]_2) = e(L_i^{(0)}, G_2)`$ over random combinations. The phase closes with the beacon as Phase 1 does, and the coordinator exports the verification key of each circuit. The node pins the hash of each verification key, and a key that does not match the published transcript is rejected before any proof is checked.

## Participant software and transcript

- The ceremony runs on software the Logos project publishes, with reproducible builds, so that a participant checks the hash of the binary it runs against the hash of the source release. The participant software contributes to Phase 1 and, in one session, to the Phase 2 of every circuit.
- A participant publishes, for each contribution, the hash of the file it received, the hash of the file it produced and its proofs of knowledge, signed with a key it is known by. The coordinator publishes the same, with the order of the participants, and keeps every intermediate file: the transcript is the chain of these files, and a chain with a missing file cannot be verified.
- Anyone verifies a contribution or the whole chain with the published software, and the project runs the full verification itself before pinning any hash. The coordinator orders the participants and relays the files; it holds no secret and no authority over the output.
- A participant samples its secrets from the operating system's random generator, mixed with entropy it provides itself, on a machine it trusts, and erases them before it publishes. The software never writes a secret to disk.

## Freezing the circuits

A circuit is frozen after its security audit and before its Phase 2 begins, and the hash of its R1CS is published with the initial proving key. Any later change to a circuit, a constraint added or removed, a public input reordered, invalidates its proving and verification keys and takes a new Phase 2 for that circuit alone: Phase 1 and the Phase 2 of the other circuits stand. The new Phase 2 is a shorter ceremony, since each participant only contributes to one circuit, but it takes the same transcript rules and the same beacon.

> **TODO (author):** the dates of the freeze, of Phase 1 and of Phase 2, agreed with the Zerokit team. The current plan starts the ceremony at the end of February 2027 and closes it by the end of March 2027, after the audit of the circuits.

## Post-quantum note

A quantum adversary that recovers $`\tau`$ or $`\delta`$ from the CRS forges Groth16 proofs, so the CRS gives Groth16 no post-quantum soundness. This does not change the plan: the ceremony's secrecy protects soundness, not confidentiality, so it is not a harvest now, decrypt later exposure, and Groth16 leaves the Logos Blockchain in the third phase of its post-quantum migration, after mainnet, for a proof system without a trusted setup. The ceremony is sized for the Groth16 circuits alone.

## References

- [Groth16] [On the Size of Pairing-based Non-interactive Arguments](https://eprint.iacr.org/2016/260), Jens Groth, Eurocrypt 2016
- [BGM17] [Scalable Multi-party Computation for zk-SNARK Parameters in the Random Beacon Model](https://eprint.iacr.org/2017/1050), Sean Bowe, Ariel Gabizon, Ian Miers, 2017
- [WCB25] [SoK: Trusted setups for powers-of-tau strings](https://eprint.iacr.org/2025/064), Faxing Wang, Shaanan Cohney, Joseph Bonneau, FC 2025
- [PPoT] [Perpetual Powers of Tau](https://github.com/privacy-scaling-explorations/perpetualpowersoftau), Privacy and Scaling Explorations
- [snarkjs] [snarkjs](https://github.com/iden3/snarkjs), iden3

# Annex

## Command flow

The flow below names the snarkjs commands each step of the ceremony maps to. The ceremony software wraps them; the commands are given so that a verifier reproduces each step by hand.

```bash
# Phase 1: extend the Perpetual Powers of Tau at degree 2^18
snarkjs powersoftau new bn128 28 ppot_0000.ptau
snarkjs powersoftau import response ppot_0000.ptau response_0001 ppot_0001.ptau        # each import verifies the response
# ... one import per PPoT response, up to the last one, response_00NN
snarkjs powersoftau truncate ppot_00NN.ptau                                            # writes one accumulator per degree, keep the 2^18 one as logos_0000.ptau
snarkjs powersoftau contribute logos_0000.ptau logos_0001.ptau --name="<participant 1>"
# ... one contribution per participant, each verified on receipt
snarkjs powersoftau verify logos_00NN.ptau
snarkjs powersoftau beacon logos_00NN.ptau logos_beacon.ptau <beacon hex> <iterations> -n="Phase 1 beacon"
snarkjs powersoftau prepare phase2 logos_beacon.ptau logos_final.ptau
snarkjs powersoftau verify logos_final.ptau
sha256sum logos_final.ptau                                                             # pinned in this document

# Phase 2, for each frozen circuit
circom <circuit>.circom --r1cs                                                         # the frozen release, hash of the R1CS published
snarkjs groth16 setup <circuit>.r1cs logos_final.ptau <circuit>_0000.zkey
snarkjs zkey contribute <circuit>_0000.zkey <circuit>_0001.zkey --name="<participant 1>"
# ... one contribution per participant, each verified on receipt
snarkjs zkey beacon <circuit>_00NN.zkey <circuit>_final.zkey <beacon hex> <iterations> -n="Phase 2 beacon"
snarkjs zkey verify <circuit>.r1cs logos_final.ptau <circuit>_final.zkey
snarkjs zkey export verificationkey <circuit>_final.zkey <circuit>_verification_key.json
sha256sum <circuit>_final.zkey <circuit>_verification_key.json                         # pinned by the node
```
