# PROOF-OF-LEADERSHIP

| Field | Value |
| --- | --- |
| Name | Proof of Leadership |
| Slug | 83 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors | Mehmet <mehmet@logos.co>, Giacomo Pasini <giacomo@logos.co>, Daniel Sanchez Quiros <daniel@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, David Rusu <david@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-12-09 |
| 1.1.0 | Remove the protection against adaptive adversary from PoL removing a non-enforced feature, simplifying work for engineers, improving UX and performances of PoL and PoQ. Update the performance according to the new circuit. Remove the notion of NOMOS in DSTs | 2026-01-29 |
| 1.1.1 | Introduced a discussion for when the value of a participating note is way higher than the total estimated stake | 2026-06-24 |
| 1.2.0 | Support the private ledger of Mantle: a note is eligible from the shielded or the transparent eligible set, and proven unspent by nullifier non-membership or by latest membership respectively | 2026-10-06 |

# Introduction

The Proof of Leadership enables a leader to produce a zero-knowledge proof attesting to the fact that they have an eligible note that has won the leadership lottery. This proof must be as lightweight as possible to generate and verify, due to the following reasons:

- Impose minimal restrictions on access to the role of leader and thus maximize the decentralization of that role.
- Similarly, the proof and its context must be efficiently verifiable for validators

This document extends the work presented in the [Ouroboros Crypsinous paper](https://eprint.iacr.org/2018/1132.pdf) with recent cryptographic developments.

## References

- [Cryptarchia Protocol](cryptarchia-v1-protocol.md).

# Overview

## Overview of the Protocol

The PoL mechanism ensures that a note has legitimately won the leadership election while protecting the leader’s privacy. The protocol is:

- Setup: The note becomes eligible for PoS when it has aged sufficiently.
- PoL generation:
  1. First, check if the note is winning by simulating the lottery
  2. Prove the membership of the note commitment in an old snapshot of the shielded or the transparent eligible set, proving its age and its existence.
  3. Prove that the note is unspent: by the non-membership of its nullifier in the most recent nullifier set for a shielded note, or by the membership of its commitment in the most recent transparent eligible set for a transparent note.
  4. Prove that the note won the PoS lottery.
  5. The proof is bound to a cryptographic public key used for signing the leader’s proposed blocks.

## Comparison with Original Crypsinous PoL

Our description differs from the original paper proposition, proving that a note is unspent directly instead of delegating the verification to validators. Moreover, we don't include the protection against adaptive adversaries that cannot be enforced by the chain or incentivized. This design choice brings the following tradeoffs:

### Advantages

1. The nullifier of the winning note is never revealed.
	- Leaders keep their privacy unlinking their stake, block and PoL.

2. There is no leader note evolution mechanism anymore ([see the paper](https://eprint.iacr.org/2018/1132.pdf) for details)
	- There are no orphan proofs anymore, removing the need to include valid PoL proofs from abandoned forks.
	- Crypsinous forced us to maintain a parallel note commitment set integrating evolving notes over time. This requirement is removed now

### Disadvantages

1. We cannot compute the PoL far in advance because the leader must know the latest ledger state of Mantle.

# Protocol

## Eligible Sets

In order to prove that the winning note exists and existed at the start of the previous epoch, and that it is unspent, every node must compute the roots of two eligible sets and of the nullifier set.

The **shielded eligible set** is the commitment MMR of the [Mantle Ledger](bedrock-v1.1-mantle-specification.md#ledger). Its root at the snapshot is $`shielded_{AGED}`$. A shielded note is proven unspent by the non-membership of its nullifier in the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree), whose latest root is $`nullifiers_{LATEST}`$.

The **transparent eligible set** holds the commitments of the service notes and of the channel notes. Its roots $`transparent_{AGED}`$ at the snapshot and $`transparent_{LATEST}`$ at the latest state are Merkle roots constructed over these commitments. The trees have a depth of $`32`$ (32 layers without counting the root), that is, the tree has a maximal capacity of $`2^{32}`$ commitments. The value $`0`$ represents an empty leaf. When the set is updated, during insertion, the first empty leaf is replaced with the new commitment, and during deletion, the leaf containing the deleted commitment is replaced with $`0`$. A transparent note is proven unspent by the membership of its commitment in $`transparent_{LATEST}`$, since it is deleted from the set when it is spent or released to the ledger. The following pseudo-code shows how the tree is managed:

```python
def insert_new_note(note_set: list[NoteCm], new_note: NoteCm):
    i = 0
    while i < len(note_set) and note_set[i] != 0:
        i += 1
    if i < len(note_set):
        note_set[i] = new_note
    else:
        note_set.append(new_note)
    return note_set

def delete_note(note_set: list[NoteCm], note: NoteCm):
    i = 0
    while i < len(note_set) and note_set[i] != note:
        i += 1

    if i == len(note_set):
        # note not in the set
        return note_set

    note_set[i] = 0
    return note_set

def empty_tree_root(depth: int):
    root = 0
    for i in range(depth):
        h = hasher()   # zk hash
        h.update(root)
        h.update(root)
        root = h.digest()
    return root

def get_transparent_root(note_set: list[NoteCm]):
    assert(len(note_set) < 2**32)
    transparent_root = get_merkle_root(note_set)  # return the Merkle root of the set
                                                  # padded with 0 to next power of 2
    transparent_root_height = len(note_set).bit_length()
    for height in range(transparent_root_height, 32):
        h= Hasher()    # zk hash
        h.update(transparent_root)
        h.update(empty_tree_root(height))
        transparent_root = h.digest()
    return transparent_root
```

  The transparent root may not be unique because the commitment set can cycle. Indeed, even if it’s not possible to insert the same commitment twice, it’s possible to cycle on a previous set state by removing notes. However, commitment uniqueness guarantees protection against attacks on note aging.

## Zero-knowledge Proof Statement

<!-- TODO: update -->
![Diagram](cryptarchia-proof-of-leadership/assets/2e9261aa-09df-80d6-b61f-d8881f0b0425.png)

A proof attesting that for the following public values:

```python
class ProofOfLeadershipPublic:
    slot: int                       # sl
    epoch_nonce: zkhash             # eta
    t0: FrElement                   # lottery constants
    t1: FrElement
    shielded_aged: MerkleRoot       # shielded eligible set root when the stake distribution was frozen
    transparent_aged: MerkleRoot    # transparent eligible set root when the stake distribution was frozen
    nullifiers_latest: MerkleRoot   # latest nullifier IMT root
    transparent_latest: MerkleRoot  # latest transparent eligible set root
    leader_pk: (FrElement, FrElement)  # P_LEAD as 2 values of 16 bytes in little endian
    entropy_contribution: zkhash    # rho_LEAD
```

The epoch nonce is defined in [Epoch Nonce](cryptarchia-v1-protocol.md#epoch-nonce) and the aged roots in [Epoch State Pseudocode](cryptarchia-v1-protocol.md#epoch-state-pseudocode). The lottery constants are computed with high precision outside the proof (see [Lottery Approximation](#lottery-approximation)), and `leader_pk` is the key signing the proposed block (see [Linking the Proof of Leadership to a Block](#linking-the-proof-of-leadership-to-a-block)).

The prover knows a witness:

```python
class ProofOfLeadershipWitness:
    sk: ZkSecretKey
    value: TokenValue
    nonce: NoteNonce
    is_shielded: boolean
    cm_aged_path: list[FrElement]
    cm_aged_selectors: list[boolean]
    low_leaf: NullifierLeaf           # used by a shielded note only
    low_leaf_path: list[FrElement]
    low_leaf_selectors: list[boolean]
    cm_latest_path: list[FrElement]   # used by a transparent note only
    cm_latest_selectors: list[boolean]
```

The circuit computes the constraints of both kinds of note, and `is_shielded` cancels those of the kind the note is not. The witness values used only by the other kind can be arbitrary.

Such that the following constraints hold:

- The selector is a boolean.
  ```python
  assert is_shielded * (1 - is_shielded) == 0
  ```

- The public key is derived from the secret key.
  ```python
  pk = zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), sk)
  ```

- The note commitment is derived from the value, the nonce and the public key.
  ```python
  cm = zkhash(FiniteField(b"NOTE_CM_V1", byte_order="little", modulus= p), value, nonce, pk)
  ```

- The note commitment was in the shielded or the transparent eligible set when the stake distribution was frozen.
  ```python
  aged_root = path_root(leaf=cm,
      path=cm_aged_path,
      selectors=cm_aged_selectors)
  assert aged_root == is_shielded * shielded_aged + (1 - is_shielded) * transparent_aged
  ```

- The note is unspent: a shielded note nullifier is not in the [Nullifier Indexed Merkle Tree](bedrock-v1.1-mantle-specification.md#nullifier-indexed-merkle-tree) of root `nullifiers_latest`, and a transparent note commitment is still in the latest transparent eligible set.
  ```python
  nf = zkhash(FiniteField(b"NOTE_NF_V1", byte_order="little", modulus= p), cm, sk)
  low_root = path_root(leaf=nullifier_leaf_hash(low_leaf),
      path=low_leaf_path,
      selectors=low_leaf_selectors)
  nf_above_low = low_leaf.nf < nf                                    # boolean
  nf_below_next = nf < low_leaf.next_nf or low_leaf.next_nf == 0     # boolean
  assert is_shielded * (nullifiers_latest - low_root) == 0
  assert is_shielded * (1 - nf_above_low) == 0
  assert is_shielded * (1 - nf_below_next) == 0

  latest_root = path_root(leaf=cm,
      path=cm_latest_path,
      selectors=cm_latest_selectors)
  assert (1 - is_shielded) * (transparent_latest - latest_root) == 0
  ```

- The note wins the lottery.
  ```python
  ticket = zkhash(FiniteField(b"LEAD_V1", byte_order="little", modulus= p), epoch_nonce, slot, cm, sk)
  threshold = value * (t0 + t1 * value)
  assert ticket < threshold
  ```

- The entropy contribution is derived from the slot and the note.
  ```python
  assert entropy_contribution == zkhash(FiniteField(b"NONCE_CONTRIB_V1", byte_order="little", modulus= p), slot, cm, sk)
  ```

- The proof is bound to `leader_pk`.

# Linking the Proof of Leadership to a Block

The PoL is bound to a public key from an asymmetric signature scheme. This public key $`P_\text{LEAD}`$ is given as two public inputs during the PoL proof generation, binding the proof to the key.

- The public key is represented by two public inputs of 16 bytes to guarantee the support of every possible Eddsa25519 public key.
- This public key is later used to verify the signature $`\sigma`$ of a block when it is dispersed. This ensures that the PoL is tied to a specific block, and only the entity creating the proof can perform this binding.
- The key is single-use, as reusing the same one could allow multiple PoLs to be linked to the same identity. An observer could then infer the stake of that identity by observing the frequency at which it emits a PoL.

# Appendix

## Lottery Approximation

- The $`\phi_f(\alpha)=1 - (1-f)^\alpha`$ function of [Ouroboros Crypsinous](https://eprint.iacr.org/2018/1132.pdf) cannot be computed in a hand-written circuit as it can only operates on elements of $`\mathbb{F}_p`$ for a certain prime number $`p`$.
- Managing floating point numbers and mathematical functions involving floating points like exponentiations or logarithms in circuits is very inefficient.
- We compared the Taylor expansion of order 1 and 2 and used the Taylor expansion of order 2 method to approximate the Ouroboros Genesis (and Crypsinous) function by the following linear function
  - $`\underset{0}{\sim}`$ means nearly equal in the neighborhood of 0
  - $`f`$ is the probability that at least one leader wins the lottery on each slot
  - $`x`$ is the stake of the proven note

$$
\begin{align*}1-(1-f)^x &= 1-e^{x\ln(1-f)} \\ 1-e^{x\ln(1-f)} &\underset{0}{\sim}x(-\ln(1-f)-0.5\ln²(1-f)x)\end{align*}
$$

Then the threshold is $`stake(t_0+t_1\cdot stake)`$ with $`t_0 := -\frac{\text{VRF}\_order \ln(1-f)}{\text{inferred\_total\_stake}}`$ and

$`t_1:=- \frac{\text{VRF}\_order\ln^2(1-f)}{2\cdot \text{inferred\_total\_stake}^2}`$. Since everything is known by every node except the value of the staked note, we pre-compute $`t_0`$ and $`t_1`$ outside of the circuit.

- The Hash functions used to derive the lottery ticket is Poseidon2 so the $`\text{VRF}\_order`$ is $`p`$ the order of the scalar field of the BN254 elliptic curve.
- To compute $`t_0`$ and $`t_1`$, we precomputed the constant parts using sagemath and real number of 512 bits precision. In the implementation, $`t_0`$ and $`t_1`$ should then be derived using 256-bit precision integers following:

| Variable | Formula |
| --- | --- |
| $`p`$ | 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001 |
| $`t_0\_constant`$ | 0x1a3fb997fd5838f2a1585ee090a95c88129ab25cc4d2e2d28f1a95f81d85465 |
| $`t_1\_constant`$ | 0x71e790b4199113a9a00298d823c5716ddac764a110a45fe3b770bbb3e8a57 |
| $`t_0`$ | $`\frac{t_0\_constant}{inferred\_total\_stake}`$ |
| $`t_1`$ | $`p-\left\lfloor\frac{t_1\_constant}{inferred\_total\_stake^2}\right\rfloor`$ |

<details><summary>**Python code to derive constants**</summary>

```python
from sage.all import RealField


FIELD_ORDER = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001
R = RealField(512)
F = R(1) / R(30)

t_0_constant = int(-R(FIELD_ORDER) * (R(1) - F).log())
t_1_constant = int(R(FIELD_ORDER) * (R(1) - F).log() ** 2 / R(2))


def lottery_constants(inferred_total_stake: int) -> tuple[int, int]:
    t_0 = t_0_constant // inferred_total_stake
    t_1 = FIELD_ORDER - (t_1_constant // inferred_total_stake**2)
    return t_0, t_1


print(f"p = {FIELD_ORDER:#x}")
print(f"t_0_constant = {t_0_constant:#x}")
print(f"t_1_constant = {t_1_constant:#x}")
```

</details>

### Error Analysis

- For $`f = \frac{1}{30}`$. The error percentage is computed with $`100 \cdot \frac{estimation - real\_value}{real\_value}`$
- We will consider that $`inferred\_total\_stake`$ is 23.5B as in Cardano
- Original function: $`1-(1-f)^\frac{stake}{inferred\_total\_stake}`$
- Taylor expansion of order 1: $`- \frac{stake}{inferred\_total\_stake}\ln(1-f) := stake \cdot t_0`$
- Taylor expansion of order 2: $`\frac{stake}{inferred\_total\_stake}(-\ln(1-f)-0.5\ln^2(1-f)(\frac{stake}{inferred\_total\_stake})) := stake(t_0+stake \cdot t_1)`$

| stake (%) | order 1 error | order 2 error |
| --- | --- | --- |
| 5% | 0.13% | -0.0001% |
| 10% | 0.26% | -0.0004% |
| 15% | 0.39% | -0.0010% |
| 20% | 0.51% | -0.0018% |
| 25% | 0.64% | -0.0027% |
| 30% | 0.77% | -0.0040% |
| 35% | 0.90% | -0.0054% |
| 40% | 1.03% | -0.0071% |
| 45% | 1.16% | -0.0089% |
| 50% | 1.29% | -0.0110% |
| 55% | 1.42% | -0.0134% |
| 60% | 1.55% | -0.0159% |
| 65% | 1.68% | -0.0187% |
| 70% | 1.81% | -0.0217% |
| 75% | 1.94% | -0.0249% |
| 80% | 2.07% | -0.0284% |
| 85% | 2.20% | -0.0320% |
| 90% | 2.33% | -0.0359% |
| 95% | 2.46% | -0.0406% |
| 100% | 2.59% | -0.0444% |

### Corner Case: Note Value Exceeding Inferred Total Stake
The lottery threshold approximation relies on a second-order Taylor expansion of $`\phi_f(α)=1−(1−f)^\alpha`$, 
which is only accurate when $`\alpha=v/\text{inferred\_total\_stake}≪1`$.
Under normal operation this holds trivially, since no single note can hold a significant fraction of the total stake.
However, a pathological regime exists where this assumption breaks down.

#### Scenario

Suppose the chain halts and only a small fraction of the original stakers come back online to restart it. 
The `inferred_total_stake` parameter, which is derived from recent epoch snapshots, may lag far behind the actual participating stake. 
A note with value $v$ could then satisfy $`v≫\text{inferred\_total\_stake}`$, placing it well outside the valid domain of the approximation.

#### What happens
The threshold $`t:=v(t0+t1⋅v)t := v(t_0 + t_1 \cdot v)`$ is a downward-opening parabola in the reals.
It peaks near $`v \approx 29 \cdot \text{inferred\_total\_stake}`$ and crosses zero again near 
$`v \approx 58 \cdot \text{inferred\_total\_stake}`$.
Past the peak, the real-valued threshold becomes negative.
In $`\mathbb{F}_p`$ this wraps to a large value close to $`p`$, meaning the lottery ticket is almost certain to be below the threshold.
The note wins nearly every slot.
Past the second zero crossing, the threshold wraps back toward zero and the behavior becomes an oscillation between near-certain win and near-certain loss depending on the exact ratio $`v/\text{inferred\_total\_stake}`$

#### Severity

This cannot be triggered by a rational adversary under normal conditions, since it requires `inferred_total_stake` to be severely underestimated relative to individual note values. 
Several scenarios can produce this regime:
- Chain halt and partial restart: only a fraction of original stakers come back online, so `inferred_total_stake` lags the actual participating stake by a large factor.
- Mass unstaking: a large coordinated withdrawal in a short period (confidence crisis, protocol migration) deflates `inferred_total_stake` while large notes remain in circulation.
- Early bootstrap: at genesis or in the first epochs, total stake has not built up yet but individual notes may already carry significant value.
- Estimation failure: a bug or manipulation in the `inferred_total_stake` derivation mechanism produces a value far below reality.

In all these cases the effect on liveness is arguably beneficial: large-stake notes winning aggressively helps the chain find leaders and recover from the depressed-stake regime.
Once epochs progress and `inferred_total_stake` converges back toward reality, the lottery returns to its normal operating range.
No circuit-level mitigation is strictly necessary given the above.

## Benchmarks

The material used for the benchmarks is the following:

- CPU       : 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM       : 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS        : Ubuntu 22.04.5 LTS
- Kernel    : 6.8.0-59-generic

![Diagram](cryptarchia-proof-of-leadership/assets/2e9261aa-09df-80b0-b368-d153e4199f56.png)
