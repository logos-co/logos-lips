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
| 1.1.0 | State that amending a circuit requires a fresh Phase 2, and that the Proof of Quota proof of work branch is such an amendment | 2026-08-10 |

# Introduction

The Logos Blockchain utilizes zero-knowledge proof systems not only to ensure strong privacy and security guarantees across its decentralized architecture, but also to reduce the computational burden on validators by compressing execution into succinct proofs. Some of the Logos Blockchain's cryptographic applications specifically use Groth16 (see [Common Cryptographic Components - Groth16 (zk-SNARK)](common-cryptographic-components.md#groth16-zk-snark)), a proof system renowned for its succinctness and efficient verification.

A critical requirement of Groth16 is the secure generation of a Common Reference String (CRS) through a one-time cryptographic ceremony, commonly known as a Trusted Setup Ceremony. This ceremony ensures that cryptographic parameters are generated in a decentralized manner, such that no individual participant can later compromise the security or privacy guarantees of the system.

The Logos Blockchain adopts a secure, publicly verifiable, and auditable Multi-Party Computation (MPC) protocol known as [Powers-of-Tau](https://eprint.iacr.org/2022/1592.pdf), performed over the BN254 elliptic curve as a first step for Groth16-based zero-knowledge proofs, to generate and extend these trusted setup parameters.

This document defines the cryptographic foundations and provides detailed instructions for securely performing or extending a trusted setup ceremony, including:

- Essential cryptographic definitions and parameters.
- Step-by-step guidance for participant contributions.
- Procedures for extending an existing Powers-of-Tau ceremony.

# Overview

At a high level, the Powers-of-Tau ceremony generates a structured set of elliptic curve points corresponding to powers of a secret scalar $\tau$. These elements form the Phase 1 CRS that underpins the Groth16 protocol in the Logos Blockchain. For Groth16, the CRS can be extended in a short Phase 2 MPC to derive circuit-specific proving and verification keys, ensuring the underlying secret remains hidden as long as at least one participant discards their randomness. The Logos Blockchain adopts an MPC setup ceremony: the Powers-of-Tau protocol.

## Powers-of-Tau Ceremony Overview

- Each participant securely contributes randomness sequentially.
- Each participant iterates over the existing CRS parameters to update it.
- At least one participant must be honest and destroy their secret input to guarantee the security of ZK schemes using the CRS.
- All transformations are accompanied by publicly verifiable proofs, ensuring full auditability of the ceremony.

![Diagram](trusted-setup-ceremony/assets/229261aa-09df-8031-9983-cc4bea1d36ff.png)

In the ceremony, a coordinator manages the sequential flow of contributions. Each contributor downloads the current CRS, applies their secret randomness, and sends the updated CRS back through the coordinator, who relays it to the next participant. At each step, an independent verifier can check that the update was performed correctly. Once all contributions are complete, the final CRS is published.

### Security of Powers-of-Tau

Let N denote the total number of contributors participating in the ceremony. The Powers-of-Tau ceremony achieves computational soundness against adversaries that corrupt up to (N-1) participants, under certain number-theoretic assumptions (e.g., the q-Strong Diffie-Hellman (q-SDH) assumption in the underlying elliptic curve groups), provided that at least one honest participant successfully erases their secret randomness.

- Honest Participation: The core trust assumption is that at least one participant in the multi-party computation securely deletes their secret contribution (i.e., the toxic waste). If this holds, then the final CRS remains sound and cannot be used to forge proofs.
- Computational Assumptions: The protocol relies on several number-theoretic assumptions, most notably the q-SDH assumption over the elliptic curve. These assumptions are fundamental to pairing-based cryptography and are not specific to the ceremony.
- Erasure Assumption: Powers-of-Tau is typically analyzed in the secure erasure model, where each participant is assumed to be capable of permanently deleting their internal secret randomness after applying it. This ensures that even if an adversary later compromises a participant, they cannot recover the toxic waste. While not a computational assumption, secure erasure is essential for the soundness of the protocol in this model.

The security of Groth16-based zero-knowledge proofs in the Logos Blockchain critically depends on a sound and verifiable trusted setup. Each participant contributes to the CRS without revealing their secret randomness, and public proofs guarantee the correctness of every transformation. The procedure applies to all required secret scalars, $\tau, \alpha, \beta, \gamma, \delta$, ensuring that all toxic waste is handled consistently and securely. Furthermore, the Logos Blockchain builds its Powers-of-Tau ceremony on top of an existing, already-audited CRS instead of starting from scratch, providing greater confidence in its security. This trusted setup process forms a foundational cryptographic pillar for ensuring privacy, integrity, and long-term resilience in the Logos architecture.

We have two phases for the ceremony. Phase 1 is circuit-independent and involves generating elliptic curve encodings of powers of a toxic waste scalar $\tau$. This enables polynomial commitments up to a certain degree and can be reused across any circuit of bounded size. Phase 2 is circuit-specific and requires knowledge of the exact constraint system. It introduces four additional toxic waste scalars $\alpha, \beta, \gamma, \delta$, which are used to encode the circuit's polynomials and, crucially, compute the $`K_i`$ elements in the verification key. These $`K_i`$ terms represent compressed combinations of public input polynomials and must be computed for each unique circuit. As a result, while Phase 1 can be performed once and reused broadly, Phase 2 must be securely executed for every new circuit.

This requirement applies to any change in a circuit's constraint system, not only to the introduction of an entirely new circuit. Amending an existing circuit produces a different constraint system, so the proving and verification keys derived for its previous form no longer apply and a fresh Phase 2 must be run before the amended circuit can be used. A change that alters the number of public inputs additionally changes how many $`K_i`$ elements the verification key contains, so the previous key is not merely stale but structurally incompatible.

Adding the proof of work branch to the [Proof of Quota](proof-of-quota.md) is such a change: it alters the constraint system and raises the number of public inputs. A Phase 2 ceremony for the amended circuit is therefore a prerequisite for deploying it, and because a ceremony requires co-ordinating independent participants it should be planned well in advance of the point at which the branch is needed.

## Curve Selection and Parameter Structure

The Logos Blockchain uses the BN254 elliptic curve for Groth16-based zero-knowledge proofs because proving time and proof size are critical in these applications. BN254 offers smaller proofs and faster proving times compared to alternatives like BLS12-381, and is backed by mature, highly optimized libraries such as Circom, SnarkJS, and libsnark.

### Groth16 Parameters

Groth16 proving systems derive two key components from a structured CRS:

- Proving Key ($pk$): This is a set of cryptographic parameters enabling the prover to generate proofs. Includes group elements from the prime-order cyclic subgroups $`\mathbb G_1`$ and $`\mathbb G_2`$ on elliptic curve, where $`\mathbb G_2`$ is defined over a degree-2 extension field.
- Verification Key ($vk$): This is a smaller set of parameters allowing efficient verification of proofs. The verification key contains a much smaller set of elliptic curve elements from groups $`\mathbb G_1`$ and $`\mathbb G_2`$.

# Protocol

## Technical and Cryptographic Steps

This section describes the trusted setup procedure in detail, outlining both the cryptographic computations and the interactive flow of the multi-party Powers-of-Tau protocol. The process begins with a coordinator initializing elliptic curve parameters and generating the initial set of structured CRS elements. Each participant builds on the previous one’s output by applying a secret random transformation and publishing a proof of correctness — so the process is sequential. As long as at least one participant discards their secret input, the entire setup remains secure. These contributions are chained together, and the ceremony concludes with a publicly verifiable aggregation of the final CRS.

The Groth16 protocol requires a CRS with a suite of powers of one random scalar $`\tau \in \mathbb{F}^*_p`$. To ensure soundness and zero-knowledge for a given arithmetic circuit, four additional toxic-waste elements must also be sampled independently and uniformly at random. While their values are circuit-independent, the way they are applied in constructing the proving and verification keys depends on the specific circuit.

In addition to $\tau$, the Groth16 proving system requires, for each circuit, four additional secret scalars, $\alpha,$ $\beta,\gamma$ and $\delta$ all sampled independently and uniformly at random from the field $`\mathbb{F}_p^*`$. These values are essential for securely encoding different components of the constraint system and for ensuring zero-knowledge in the final proof. Specifically, $\alpha$ and $\beta$ are used to randomize the circuit polynomials $A(x)$ and $B(x)$, $\gamma$ is used to compress linear combinations of public inputs, and $\delta$ provides blinding for the quotient polynomial that ensures witness-hiding. Like $\tau$, each of these values must be treated as toxic waste and securely discarded after use. All five values: $\tau, \alpha, \beta, \gamma, \delta$ must be generated using the same secure procedure and structure. In Groth16 Phase 2, these scalars are used immediately to derive circuit-specific CRS elements, in particular the $`K_i`$ terms in the verification key, before all toxic waste is securely destroyed.

### Step 1: Initialization (Coordinator)

The coordinator publicly specifies the foundational cryptographic parameters:

- Elliptic Curve:
    BN254: $`(x,y) \in \mathbb{F}_{p}^{\text{BN254}}`$ such that $`y^2 = x^3 + 3`$​
    Here $`\mathbb{F}_{p}^{\text{BN254}}`$ denotes distinct prime fields of size $`p^{\text{BN254}}`$.
- Cryptographic Groups:
    - $`\mathbb{G}_1, \mathbb{G}_2, \mathbb{G_T}`$: prime-order subgroups of elliptic curve points over $`\mathbb{F}_p`$ and its extensions.
    - $`e: \mathbb{G}_1 \times \mathbb{G}_2 \to \mathbb{G}_T`$: a bilinear, non-degenerate pairing function.
- Generators:
    - $`G_i \in \mathbb{G}_i : i \in \{1,2,T\}`$ are fixed public generators.
- Element Notation:
    - Elements of the group $`\mathbb{G}_i : i \in \{1,2,T\}`$ are written additively by using the following notation: $`[\alpha]_i := \alpha \cdot G_i`$.

These values are fixed and published to all ceremony participants.

- An initialized CRS:
    - The initialized CRS contains $n + 1$ elements in $`G_1`$ and $m+1$ elements in $`G_2`$. For the $\tau$ secret in Groth16, the value of $n$ defines the maximum degree of polynomials that will be committed and the maximum size of circuits (the number of R1CS constraints must be ≤ $n$) and $m=1$. In contrast, the parameters $\alpha, \beta, \gamma, \delta$ of the Groth16 protocol each require only $n=m=0$. But, Phase 2 also includes the computation of the $`K_i`$ elements in $`\mathbb G_1`$, whose number depends on the circuit’s public inputs. These must be generated at the same time, while the toxic waste scalars are still in memory.
    - The CRS is of the form $`\left([1]_1\right)_{j=0}^n \; \left([1]_2\right)_{k=0}^m`$ when initializing from scratch.
    > For performance reasons, especially to leverage Number Theoretic Transforms (NTT) for fast polynomial arithmetic, it is common to choose $n$ as a power of two. For example, setting $`n = 2^{k}`$ allows working with polynomials of degree up to $`2^{k} - 1`$, and proving circuits with up to $`2^{k}`$ constraints.

### Step 2: Participant Contribution

Each participant $i$ in the sequence performs the following:

1. Downloads the current CRS:
   $`([\tau^j]_1)_{j=0}^{n}, \; ([\tau^k]_2)_{k=0}^{m}`$ ($\tau = 1$ at the initialization phase).
1. Generates a random secret scalar $`r_i \stackrel{\mathrm{R}}{\leftarrow} \mathbb{F}_p^*`$.
1. Updates the CRS by contributing its secret $`r_i`$ into the CRS.
    - $`\forall j\in [0,n]: \; [(\tau')^j]_1 := [{(r_i \tau)^j}]_1 ={r_i^j}\cdot [\tau^j]_1`$.
    - $`\forall k \in [0,m] : [(\tau')^k]_2 = [{(r_i \tau)^k}]_2 = {r_i^k}\cdot [\tau^k]_2`$.
1. Creates a proof showing they know $`r_i`$, and that the CRS is a correct transformation of the old one.
    - This proof consists of three checks (detailed in Step 4):
        - Knowledge of exponent $`r_i`$ for the first element.
        - Non-zero: $`r_i \neq 0`$ ensuring previous contributions are not erased.
        - Well-formedness of the updated CRS via random linear combination pairing check.
1. Submits:
    - Updated parameters $`([(\tau')^j]_1)_{j=0}^{n}, \; ([(\tau')^k]_2)_{k=0}^{m}`$.
    - Proof of correct transformation.

In Phase 2 for Groth16, participants also update all circuit-specific elements derived from the toxic waste scalars (including the $`K_i`$ terms), ensuring they are transformed consistently with the rest of the CRS.

### Step 3: Public Verification

1. Knowledge of Exponent $`r_i`$​
    This is proven using a Fiat–Shamir transform of a Schnorr-like protocol:
    - Let: $`\quad [\tau']_1 = {r_i \cdot [\tau]_1}`$.
    - Prover samples random values uniformly $`z \stackrel{\mathrm{R}}{\leftarrow} \mathbb{F}_p`$.
    - Computes: $`[z']_1 = z\cdot[\tau]_1`$.
    - Computes challenge: $`h = \text{Hash}([\tau]_1, [\tau']_1, [z']_1)`$.
    - Computes response: $`s = z + h \cdot r_i \mod p`$.
    - Publishes proof $`\pi = ([z']_1, s)`$.
    - Verifier checks: $`s\cdot[\tau]_1 \stackrel{?}{=} [z']_1 + h\cdot [\tau']_1`$.
    This protocol confirms that the first element of the CRS was exponentiated with a known secret $`r_i`$.
1. Well-Formedness of CRS
    - Verifier samples $`\rho_1, \rho_2 \stackrel{\mathrm{R}}{\leftarrow} \mathbb{F}_p^*`$.
    - The verifier computes the following pairing equation on the new CRS:

$$
e\!\left(
\sum_{j=1}^n \rho_1^{j-1} \cdot [\tau^j]_1,\,
[1]_2 + \sum_{k=1}^{m-1}\rho_2^k \cdot [\tau^k]_2
\right)
\stackrel{?}{=}
e\!\left(
[1]_1 + \sum_{j=1}^{n-1} \rho_1^j \cdot [\tau^j]_1,\,
\sum_{k=1}^m \rho_2^{k-1} \cdot [\tau^k]_2
\right)
$$

This pairing check confirms that the CRS has been updated via exponentiation by the same secret scalar $`r_i`$, preserving the structure of the powers of $\tau$.

1. Non-Erasing Contribution
    - Checks that $`r_i \neq 0`$:  $`r_i \cdot [\tau]_1\ne \mathcal{O} \quad (\text{identity element})`$.
1. $`K_i`$’s verification (Phase2 only)
    For each public $i$, check the pairing equation:
   $`e(K_i,\; [\gamma]_2) \;\stackrel{?}{=}\; e\!\left([A_i(\tau)]_1,\; [\beta]_2\right)\;\cdot\; e\!\left([B_i(\tau)]_1,\; [\alpha]_2\right)\;\cdot\; e\!\left([C_i(\tau)]_1,\; G_2\right)`$​
    - Left side encodes the division by $\gamma$ (respectively $\delta$ for private inputs).
    - Right side encodes the linear combination $`\beta A_i(\tau) + \alpha B_i(\tau) + C_i(\tau)`$.
    - If it holds for all $i$, the $`K_i`$ are correct and consistent with the same $\alpha,\beta,\gamma,\tau$ for public inputs (respectively $\delta$ for private inputs).

### Step 4: Toxic Waste Destruction

While each participant is expected to delete their secret scalar $`r_i`$ immediately after contribution, security is guaranteed as long as at least one participant successfully deletes their randomness.

### Finalized CRS

Once all participants have contributed:

- The final CRS $`([\tau^j]_1)_{j=0}^{n} = ([\prod_i r_i^j]_1)_{j=0}^n, \; ([\tau^k]_2)_{k=0}^m = ([\prod_i r_i^k]_2)_{k=0}^m`$ is published ($i$ being the number of participants).
- This CRS is used to derive:
    - Circuit-specific proving keys $pk$.
    - Circuit-specific verification keys $vk$.

## Extending an Existing Trusted Setup Ceremony

Logos may choose to leverage an existing, publicly verified Powers-of-Tau ceremony to inherit trust and security. To do this, Logos simply adds additional participants following the above participant contribution steps (Step 2):

- Logos participants securely download existing Powers-of-Tau parameters.
- Each Logos participant sequentially adds their randomness and generates proofs-of-knowledge, updating the parameters.
- After all Logos contributions, a new final set of parameters is derived.
- A Logos coordinator aggregates the auditable contributions to compute the new CRS parameters and publish them for Logos.

By following this protocol, Logos ensures robust security guarantees without repeating the entire ceremony from scratch. Most importantly, this process allows Logos to onboard previous contributions from external parties, inheriting their randomness and strengthening the trust assumption. It also preserves the transparency, integrity, and auditability of the original ceremony while enhancing its security by contributing additional entropy from Logos’ own participants, effectively extending a trusted foundation with new safeguards.

## References

- [Groth16] [IACR Cryptology ePrint ArchiveOn the Size of Pairing-based Non-interactive Arguments](https://eprint.iacr.org/2016/260), Jens Groth, Eurocrypt 2016
- [WCB25] [IACR Cryptology ePrint ArchiveSoK: Trusted setups for powers-of-tau strings](https://eprint.iacr.org/2025/064), Faxing Wang, Shaanan Cohney, Joseph Bonneau, FC 2025

# Annex

```python
# Pseudocode for Multi-Party Powers-of-Tau Ceremony
# Input:
#   - n: Max degree of polynomials to support (e.g., #constraints in Groth16)
#   - m: Usually 1
#   - G1, G2: Elliptic curve generators for groups G1 and G2
#   - p: Prime order of the field F_p
# Output:
#   - crs: Common Reference String with structured powers of tau
#   - transcript: List of contributions and public proofs
# Assume Point is a placeholder for an elliptic curve point class
Point = object
Scalar = int
@dataclass
class ContributionProof:
    z_point: Point
    s: Scalar

def initialize_crs(n: int, m: int, G1: Point, G2: Point):
    crs_G1 = [(1 ** j) * G1 for j in range(n)] # [1]_1, [1]_1, ..., [1]_1
    crs_G2 = [(1 ** k) * G2 for k in range(m)] # [1]_2, [1]_2
return crs_G1, crs_G2

def contribute(
    crs_G1: list[Point],
    crs_G2: list[Point],
    G1: Point,
    G2: Point,
    p: int):
    r: Scalar = random_non_zero_scalar(p) # secret toxic waste scalar. 254-bit for BN254 and 255-bit for BLS12-381

# Apply exponentiation to CRS
    crs_G1_prime = [(r ** j) * crs_G1[j] for j in range(len(crs_G1))]
    crs_G2_prime = [(r ** k) * crs_G2[k] for k in range(len(crs_G2))]
# Generate proof of correct exponentiation
    proof = generate_proof_of_knowledge(crs_G1[1], crs_G1_prime[1], r, G1, p)
# Destroy r securely
del r

    return crs_G1_prime, crs_G2_prime, proof

def generate_proof_of_knowledge(
    old_point: Point,
    new_point: Point,
    r: Scalar,
    G: Point,
    p: int):
    
    z: Scalar = random_non_zero_scalar(p)
    z_point = z * G
    # Schnorr-style proof with Fiat–Shamir challenge
    h: Scalar = hash_to_scalar(old_point, new_point, z_point)
    s: Scalar = (z + h * r) % p
    return ContributionProof(z_point, s)
def verify_contribution(
    old_crs_G1: list[Point],
    old_crs_G2: list[Point],
    new_crs_G1: list[Point],
    new_crs_G2: list[Point],
    proof: ContributionProof,
    G1: Point,
    G2: Point,
    p: int):
    
    z_point, s = proof.z_point, proof.s
    h = hash_to_scalar(old_crs_G1[1], new_crs_G1[1], z_point)
    lhs = s * G1
    rhs = z_point + h * new_crs_G1[1]
if lhs != rhs:
return False

    rho_one = random_non_zero_scalar(p)
    rho_two = random_non_zero_scalar(p)

    lhs = pairing(
sum([(rho_one ** j) * new_crs_G1[j] for j in range(len(new_crs_G1))]),
(1 * old_crs_G2[0]) + sum([(rho_two ** k) * old_crs_G2[k] for k in range(len(old_crs_G2))])
)
    rhs = pairing(
(1 * old_crs_G1[0]) + sum([(rho_one ** j) * old_crs_G1[j] for j in range(len(old_crs_G1))]),
sum([(rho_two ** k) * new_crs_G2[k] for k in range(len(new_crs_G2))])
)
return lhs == rhs

def powers_of_tau_ceremony(
    participants: list[object], # Should ideally be a class/interface with contribute()
    n: int,
    m: int,
    G1: Point,
    G2: Point,
    p: int):
    
    crs_G1, crs_G2 = initialize_crs(n, m, G1, G2)
    transcript: list[ContributionProof] = []
for participant in participants:
        crs_G1_new, crs_G2_new, proof = participant.contribute(crs_G1, crs_G2, G1, G2, p)
if not verify_contribution(crs_G1, crs_G2, crs_G1_new, crs_G2_new, proof, G1, G2, p):
raise ValueError("Invalid contribution by participant")
        transcript.append(proof)
        crs_G1, crs_G2 = crs_G1_new, crs_G2_new

    return crs_G1, crs_G2, transcript
```
