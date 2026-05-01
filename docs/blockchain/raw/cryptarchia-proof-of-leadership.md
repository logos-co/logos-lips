# CRYPTARCHIA-PROOF-OF-LEADERSHIP

| Field | Value |
| --- | --- |
| Name | Cryptarchia Proof of Leadership Specification |
| Slug | 83 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomas@status.im> |
| Contributors | Mehmet <mehmet@status.im>, Giacomo Pasini <giacomo@status.im>, Daniel Sanchez Quiros <daniel@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, David Rusu <david@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-proof-of-leadership.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

The Proof of Leadership (PoL) enables a leader to produce a zero-knowledge proof
attesting to the fact that they have an eligible note (a representation of stake)
that has won the leadership lottery.
This proof is designed to be as lightweight as possible to generate and verify,
to impose minimal restrictions on access to the role of leader
and maximize the decentralization of that role.
This document specifies the PoL mechanism for Cryptarchia,
extending the work presented in the Ouroboros Crypsinous paper
with recent cryptographic developments.

**Keywords:** Cryptarchia, proof-of-leadership, zero-knowledge, consensus,
note, stake, lottery, Merkle tree

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Background

### Protocol Overview

The PoL mechanism ensures that a note has legitimately won the leadership election
while protecting the leader's privacy.
The protocol is comprised of two parts: setup and PoL generation.

**Setup:**

1. Draw uniformly a random seed.
2. Construct a Merkle tree composed of slot secrets derived from the seed.
3. Use the root of the tree and the starting slot to get the leader's secret key.
   The starting slot is when the note can start to be used for PoL.
4. The leader receives their stake in a note that uses this generated secret key.
   The leader either transfers this stake to themselves
   or obtains it from a different user.
5. The note becomes eligible for Proof of Stake (PoS) when it has aged sufficiently,
   and the actual slot number is greater than or equal to
   the starting slot of the note.

**PoL generation:**

1. First, check if the note is winning by simulating the lottery.
2. Prove the membership of the note identifier in an old snapshot of the Mantle Ledger,
   proving its age and its existence.
3. Prove the membership of the note identifier in the most recent Mantle ledger,
   proving it's unspent.
4. Prove that the note won the PoS lottery.
5. Prove the knowledge of the slot secret for the winning slot.
6. The proof is bound to a cryptographic public key used for signing
   the leader's proposed blocks.

### Comparison with Original Crypsinous PoL

This description differs from the original paper proposition,
proving that a note is unspent directly
instead of delegating the verification to validators.
This design choice brings the following tradeoffs:

**Advantages:**

1. The ledger isn't required to be private using shielded notes.
   - Validators don't need to maintain a nullifier list.
   - Leaders keep their privacy unlinking their stake, block and PoL.

2. There is no leader note evolution mechanism anymore (see the paper for details).
   - There are no orphan proofs anymore,
     removing the need to include valid PoL proofs from abandoned forks.
   - Crypsinous required maintaining a parallel note commitment set
     integrating evolving notes over time.
     This requirement is removed now.
   - The derivation of the slot secret and its Merkle proof
     can be done locally without connection to the Nomos chain.

**Disadvantages:**

1. The PoL cannot be computed far in advance
   because the leader MUST know the latest ledger state of Mantle.

## Protocol

### Protection Against Adaptive Adversaries

The Ouroboros Crypsinous paper integrates protection against adaptive adversaries:

> The design has several subtleties since a critical consideration in the PoS setting
> is tolerating adaptive corruptions:
> this ensures that even if the adversary can corrupt parties
> in the course of the protocol execution in an adaptive manner,
> it does not gain any non-negligible advantage by e.g., re-issuing past PoS blocks.
> (p. 2)

To avoid a leaked note being reused to maliciously regenerate past PoLs,
this specification adopts the solution proposed in the paper
using slightly different parameters.

The solution proposed in the paper is as follows:

> We solve the former issue, by adding a cheap key-erasure scheme
> into the NIZK for leadership proofs.
> Specifically, **parties have a Merkle tree of secret keys**,
> the root of which is hashed to create the corresponding public key.
> The **Merkle tree roots acts like a Zerocash coin secret key**,
> and can be used to spend coins.
> For leadership however, parties also must prove knowledge of a path
> in the Merkle tree to a leaf at the index of the slot they are claiming to lead.
> **After a slot passes, honest parties erase their preimages**
> of this part of that path in the tree.
> As the size of this tree is linear with the number of slots,
> we allow parties to keep it small, by restricting its size.
> (p. 5)

The paper proposed a tree of depth 24.

- This implies that the note is usable for PoS for only 194 days approximately
  (because 1 slot is 1 second).
- After this period, the note MUST be refreshed to include new randomness.
  For simplicity, the refresh mechanism is designed
  as a classical transaction modifying the nullifier secret key.
- This solution has good performance:

> For a reasonable value of $R = 2^{24}$, this is of little practical concern.
> Public keys are valid for $2^{24}$ slots
> and employing standard space/time trade-offs,
> key updates take under 10,000 hashes, with less than 500kB storage requirement.
> The most expensive part of the process, key generation,
> still takes less than a minute on a modern CPU.
> (p. 29)

The disadvantages of this solution are that:

1. The public key of the note will change periodically
   (each time all slot secrets are consumed) for the ones participating in PoL.
2. The note will not be reusable directly after refresh
   as only old enough notes are usable for PoS.

This specification proposes a tree with a depth of 25,
extending the note's eligibility to around 388 days,
with a maximum of **two epochs remaining ineligible** not counted in these days.
Note that this requirement applies specifically to proving leadership in PoS
and is not needed for every note.
While any note can be used for PoL,
the knowledge of the secret slots behind the public key
is only necessary to demonstrate that you are a leader.

**Setup:** When refreshing their notes, potential leaders will:

1. Uniformly randomly draw a seed $r_1 \xleftarrow{\$} \mathbb{F}_p$.

2. Construct a Merkle Tree of root $R$ containing $2^{25}$ slot secrets
   (that are random numbers).
   One way to efficiently construct the tree is to:

   - Derive the slot secrets using a zkhash chain:
     $\forall i \in [2, 2^{25}], r_i := \text{hash}(r_{i-1})$.
     - More concretely, each leaf is the zkhash of the previous leaf (slot secret).

   - This reduces storage requirements compared to directly randomly drawn
     independently $2^{25}$ slot secrets.
     - The first generation of the Merkle tree should be fast enough
       as it only requires hashing data.
       A correct implementation that erases data over time
       could maintain an upper bound in memory usage during the generation
       of the tree to only $\log_2(2^{25}) = 25$ zk hashes which is 800 bytes.
     - Leaders are only required to maintain the MMR up to the current slot.
       This means at minimum,
       leaders hold only 25 hashes in memory at any point in time.
     - After the first generation, the wallets optimize their storage
       by holding only the necessary information to maintain a correct Merkle path,
       deriving the next one over time using the fact that
       slot secrets were derived from the previous ones.

   - It guarantees protection against adaptive adversaries.
     - Thanks to the pseudo-random properties of the hash function,
       slot secrets are indistinguishable from true randomness.
     - The one-way property of the hash function guarantees
       that an adaptive adversary cannot retrieve past slot secrets
       using a fresher one.

3. The user chooses a starting slot $sl_{start}$ from which their note
   will be eligible for PoS.

   The note MUST be on-chain by the start of epoch $ep - 1$
   to be eligible for PoL in epoch $ep$ because of the age requirement.
   Based on this, we suggest $sl_{start}$ to not be earlier
   than the start of the epoch following the one after the transaction is emitted.
   This prevents the inclusion of unusable slot secrets in the tree
   (because the note would not be aged enough),
   optimizing the PoL lifetime of the note.

4. Finally, they derive their secret key
   $sk := \text{hash}(\text{NOMOS\_POL\_SK\_V1}||sl_{start}||R)$,
   binding the starting slot and the Merkle tree of slot secret
   to the note secret key.
   This is verified in Circuit Constraints.

These four steps are summarized in the following pseudo-code:

```python
def pol_sk_gen(sl_start, seed):
    frontier_nodes = MMR()
    path = MerkleProof()

    # Generate 2^25 slot secrets using a hash chain initialized with `seed`.
    r = zkhash(seed)
    for i in range(2**25):
        frontier_nodes.append(r)  # Append the slot secret to the MMR
        path.update(frontier_nodes)  # Update Merkle path of this slot secret
        r = zkhash(r)  # Derive the next slot secret

    # Derive the root of the MMR
    root = frontier_nodes.get_root()

    # Finally, derive the final PoL secret key.
    # Return the secret key and the Merkle proof of seed.
    return (zkhash(b"NOMOS_POL_SK_V1" + sl_start + root), path)

def update_secret_and_path(r, path):
    r = zkhash(r)  # Derive next slot secret
    path.update(r)  # Update the path for the Merkle proof of the new slot secret
    return (r, path)
```

> Note that the generation of the slot secret tree is not constrained
> by proofs or at consensus level and can be adapted by the node
> as long as they are able to derive the merkle proof of their slot secret.

**PoL:** When proving the leadership election,
note owners will prove knowledge of the slot secret corresponding to the slot $sl$.

1. To do that, they will give a Merkle path from the leaf at index $sl - sl_{start}$.
2. The root of the tree hashed with $sl_{start}$ MUST be the secret key $sk$,
   which will be used for public key derivation.

**Protection against adaptive adversaries:**
Since each slot has its own slot secret,
requiring wallets to delete slot secrets used for previous slots
avoids the risk of corruption that leads to the creation of PoL for previous blocks.

- The slot secret is derived from the previous one but the opposite is impossible.
- An adaptive adversary corrupting the node would not have access to
  previous slot secrets if correctly deleted.
  Therefore, an adversary would not be able to generate the PoL for previous slots.

### Ledger Root

In order to prove that the winning note exists in the ledger
and existed at the start of the previous epoch,
every node MUST compute two ledger commitments.
These commitments $ledger_{AGED}$ and $ledger_{LATEST}$
are Merkle roots constructed over the Note IDs.
The trees have a depth of 32 and are populated with note IDs.
The value 0 represents an empty leaf.
When the set is updated, during insertion,
the first empty leaf is replaced with the new note ID,
and during deletion, the leaf containing the deleted note ID is replaced with 0.

The following pseudo-code shows how the tree is managed:

```python
def insert_new_note(note_set: list[NoteId], new_note: NoteId):
    i = 0
    while i < len(note_set) and note_set[i] != 0:
        i += 1
    if i < len(note_set):
        note_set[i] = new_note
    else:
        note_set.append(new_note)
    return note_set

def delete_note(note_set: list[NoteId], note: NoteId):
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
        h = hasher()  # zk hash
        h.update(root)
        h.update(root)
        root = h.digest()
    return root

def get_ledger_root(note_set: list[NoteId]):
    assert(len(note_set) < 2**32)
    ledger_root = get_merkle_root(note_set)
    # return the Merkle root of the set padded with 0 to next power of 2
    ledger_root_height = len(note_set).bit_length()
    for height in range(ledger_root_height, 32):
        h = Hasher()  # zk hash
        h.update(ledger_root)
        h.update(empty_tree_root(height))
        ledger_root = h.digest()
    return ledger_root
```

> The ledger root may not be unique because the note IDs set can cycle.
> Indeed, even if it's not possible to insert the same note ID twice,
> it's possible to cycle on a previous set state by removing notes.
> However, note IDs uniqueness guarantees protection against attacks on note aging.

### Zero-knowledge Proof Statement

![Proof of Leadership Circuit Diagram](assets/pol-short-diagram.webp)

#### Circuit Public Inputs

The prover (the leader) and the verifiers (nodes of the chain)
MUST agree on these values:

1. **The slot number:** $sl$.

2. **The epoch nonce:** $\eta$.
   - For details see Cryptarchia v1 Protocol Specification - Epoch Nonce.

3. **The lottery function constants:**
   $t_0 = -\frac{\text{VRF\_order} \cdot \ln(1-f)}{\text{inferred\_total\_stake}}$
   and
   $t_1 = -\frac{\text{VRF\_order} \cdot \ln^2(1-f)}{2 \cdot \text{inferred\_total\_stake}^2}$.
   - For details see Lottery Approximation.
   - These numbers MUST be computed with high precision outside the proof.

4. **The root of the note Merkle tree when the stake distribution was frozen:**
   $ledger_{AGED}$.
   - For details see Cryptarchia v1 Protocol Specification - Epoch State Pseudocode.

5. **The latest root of the note Merkle tree:** $ledger_{LATEST}$.
   - Used to ensure the leadership note has not been spent.

6. **The leader's one-time public key** $P_{LEAD}$
   represented by 2 public inputs, each of 16 bytes in little endian.
   This key is needed to sign the proposed block.
   - For details see Linking the Proof of Leadership to a Block.

7. **The entropy contribution** $\rho_{LEAD}$ verified to be correctly derived.
   - This is the epoch nonce entropy contribution.
     See Cryptarchia v1 Protocol Specification - Epoch Nonce.

#### Circuit Private Inputs

The prover has to provide these values, but they remain secret:

1. **The slot secret and the related information** used for the slot $sl$
   as described in Protection Against Adaptive Adversaries:
   - The slot secret $r_{sl}$.
   - The Merkle path $slot\_secret\_path$ of $r_{sl}$ leading to the root $R$.
   - The starting secret slot $sl_{start}$.

2. **The eligible note and its related information** used to derive the $noteID$
   (the secret key is derived for the previous step):
   - The note value: $v$.
   - The note transaction zk hash: $note\_tx\_hash$.
   - The note outputs number: $note\_output\_number$.

3. **The proof of membership** of the note identifier in the zone ledgers
   $ledger_{AGED}$ and $ledger_{LATEST}$.
   This is done by providing the complementary Merkle nodes
   and indicating whether they are left (0) or right (1) through boolean selectors:
   - The aged ledger complementary nodes: $noteid\_aged\_path$.
   - The aged ledger complementary node selectors: $note\_id\_aged\_selectors$.
   - The latest ledger complementary nodes: $noteid\_latest\_path$.
   - The latest ledger complementary node selectors: $note\_id\_latest\_selectors$.

#### Circuit Constraints

The proof confirms the following relations:

1. The derivation of the Merkle tree root $R$
   using the slot secret $r_{sl}$ as the $sl - sl_{start}$'s leaf
   of the Merkle tree using the Merkle path.

   This is a proof of knowledge of the secret slot $r_{sl}$
   guaranteeing protection against adaptive adversaries.

2. The derivation of $sk = \text{hash}(\text{NOMOS\_POL\_SK\_V1}||sl_{start}||R)$,
   as documented in Protection Against Adaptive Adversaries.

3. The computation of the note identifier.

4. The note identifier is in $ledger_{AGED}$ and $ledger_{LATEST}$.

5. The computation of the lottery ticket:
   $ticket := \text{hash}(\text{LEAD\_V1}||\eta||sl||noteID||sk)$ using Poseidon2.

6. The computation of the threshold: $t := v(t_0 + t_1 \cdot v)$.
   The ticket MUST be lower than this threshold to win the lottery.

7. The check that indeed $ticket < t$.

8. Compute and output the entropy contribution
   $\rho_{LEAD} := \text{hash}(\text{NOMOS\_NONCE\_CONTRIB\_V1}||sl||noteID||sk)$.

### Linking the Proof of Leadership to a Block

The PoL is bound to a public key from an asymmetric signature scheme.
This public key $P_{LEAD}$ is given as two public inputs during the PoL proof generation,
binding the proof to the key.

- The public key is represented by two public inputs of 16 bytes
  to guarantee the support of every possible EdDSA25519 public key.
- This public key is later used to verify the signature $\sigma$ of a block
  when it is dispersed.
  This ensures that the PoL is tied to a specific block,
  and only the entity creating the proof can perform this binding.
- The key is single-use, as reusing the same one could allow multiple PoLs
  to be linked to the same identity.
  An observer could then infer the stake of that identity
  by observing the frequency at which it emits a PoL.

## Appendix

### Lottery Approximation

- The $\phi_f(\alpha) = 1 - (1-f)^\alpha$ function of Ouroboros Crypsinous
  cannot be computed in a hand-written circuit
  as it can only operate on elements of $\mathbb{F}_p$
  for a certain prime number $p$.
- Managing floating point numbers and mathematical functions
  involving floating points like exponentiations or logarithms in circuits
  is very inefficient.
- Comparing the Taylor expansion of order 1 and 2,
  the Taylor expansion of order 2 method is used
  to approximate the Ouroboros Genesis (and Crypsinous) function
  by the following linear function:
  - $\stackrel{0}{\sim}$ means nearly equal in the neighborhood of 0
  - $f$ is the probability that at least one leader wins the lottery on each slot
  - $x$ is the stake of the proven note

$$1 - (1-f)^x = 1 - e^{x \ln(1-f)}$$

$$1 - e^{x \ln(1-f)} \stackrel{0}{\sim} x(-\ln(1-f) - 0.5 \ln^2(1-f)x)$$

Then the threshold is $stake(t_0 + t_1 \cdot stake)$ with
$t_0 := -\frac{\text{VRF\_order} \cdot \ln(1-f)}{\text{inferred\_total\_stake}}$
and
$t_1 := -\frac{\text{VRF\_order} \cdot \ln^2(1-f)}{2 \cdot \text{inferred\_total\_stake}^2}$.

Since everything is known by every node except the value of the staked note,
we pre-compute $t_0$ and $t_1$ outside of the circuit.

- The Hash functions used to derive the lottery ticket is Poseidon2
  so the VRF_order is $p$ the order of the scalar field of the BN254 elliptic curve.
- To compute $t_0$ and $t_1$, we precomputed the constant parts using sagemath
  and real number of 512 bits precision.
  In the implementation, $t_0$ and $t_1$ should then be derived
  using 256-bit precision integers following:

| Variable | Formula |
| -------- | ------- |
| $p$ | `0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001` |
| $t_0\_constant$ | `0x1a3fb997fd58374772808c13d1c2ddacb5ab3ea77413f86fd6e0d3d978e5438` |
| $t_1\_constant$ | `0x71e790b41991052e30c93934b5612412e7958837bac8b1c524c24d84cc7d0` |
| $t_0$ | $\frac{t_0\_constant}{\text{inferred\_total\_stake}}$ |
| $t_1$ | $p - \lfloor\frac{t_1\_constant}{\text{inferred\_total\_stake}^2}\rfloor$ |

### Error Analysis

- For $f = 0.05$.
  The error percentage is computed with $100 \cdot \frac{estimation - real\_value}{real\_value}$.
- This analysis considers inferred_total_stake to be 23.5B as in Cardano.
- Original function: $1 - (1-f)^{\frac{stake}{\text{inferred\_total\_stake}}}$
- Taylor expansion of order 1:
  $-\frac{stake}{\text{inferred\_total\_stake}} \ln(1-f) := stake \cdot t_0$
- Taylor expansion of order 2:
  $\frac{stake}{\text{inferred\_total\_stake}}(-\ln(1-f) - 0.5 \ln^2(1-f)(\frac{stake}{\text{inferred\_total\_stake}})) := stake(t_0 + stake \cdot t_1)$

| stake (%) | order 1 error | order 2 error |
| --------- | ------------- | ------------- |
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

### Benchmarks

The material used for the benchmarks is the following:

- CPU: 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM: 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS: Ubuntu 22.04.5 LTS
- Kernel: 6.8.0-59-generic

![Average proving time vs number of threads (100 Runs)](assets/pol-benchmark-proving-time.webp)

## References

### Normative

- [Cryptarchia v1 Protocol Specification](https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification-21c261aa09df810cb85eff1c76e5798c)
  \- Parent protocol specification

### Informative

- [Proof of Leadership Specification](https://nomos-tech.notion.site/Proof-of-Leadership-Specification-21c261aa09df819ba5b6d95d0fe3066d)
  \- Original Proof of Leadership documentation
- [Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake](https://eprint.iacr.org/2018/1132.pdf)
  \- Foundation for the PoL design

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
