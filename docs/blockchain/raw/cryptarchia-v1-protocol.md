# CRYPTARCHIA-PROTOCOL

| Field | Value |
| --- | --- |
| Name | Cryptarchia Protocol |
| Slug | 92 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <david@logos.co> |
| Contributors | Álvaro Castro-Castilla <alvaro@logos.co>, Giacomo Pasini <giacomo@logos.co>, Thomas Lavaur <thomas@logos.co>, Mehmet <mehmet@logos.co>, Marcin Pawlowski <marcin@logos.co>, Daniel Sanchez Quiros <daniel@logos.co>, Youngjoon Lee <youngjoon@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/cryptarchia-v1-protocol.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/cryptarchia-v1-protocol.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-v1-protocol.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-v1-protocol.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-01-20 |
| 1.0.1 | Replaced Logos Blockchain name with Logos Blockchain | 2026-04-17 |
| 1.0.2 | Added details for block root computation | 2026-05-26 |
| 1.1.0 | Precise and make clearer that the max block size is the max body size, and fix the verification of the number of transaction per block to be <= 1024 | 2026-07-27 |
| 1.1.1 | Corrected `MAX_BLOCK_SIZE` to 2 MiB, to match the implementation. | 2026-08-05 |
| 1.2.0 | Added [uncle references](#uncle-references): a block carries the signed headers of the fork blocks it references, every carried entry must be valid for the block itself to be valid, and the [Total Stake Inference](#total-stake-inference) counts their slots. Replaced `block_root` with `body_root`, which commits to those headers as well as to the transactions. | 2026-08-06 |
| 1.2.1 | Reordered the `ProofOfLeadership` fields to the wire order defined by the [Canonical Encoding](bedrock-v1.1-block-construction.md#canonical-encoding), and noted that the [Block ID](#block-id) preimage absorbs the same fields in a different order by design. The `Header` layout and the `block_id` preimage are otherwise unchanged. | 2026-08-19 |

# Introduction

Cryptarchia is the consensus protocol of the Logos Blockchain’s Bedrock layer. This document specifies how Bedrock comes to agreement to a single history of blocks.

The values that Cryptarchia optimizes for are **resilience and privacy**. These come at the cost of block times and finality. These values have significant implications on user experience and we should understand them well.

## Resilience

In consensus, we are presented with a choice of prioritizing either safety or liveness in the presence of catastrophic failure (this is a re-formalization of the CAP theorem). Choosing safety means the chain never forks, instead the chain halts until the network heals. On the other hand, choosing liveness (a la Bitcoin/Ethereum) means that block production continues but finality will stall, leading to confusion around which blocks are on the honest chain.

On the surface both options seem to provide similar guarantees. If finality is delayed indefinitely, is this not equivalent to a halted chain? The differences come down to how safety or liveness is implemented.

### Prioritizing Safety

Chains that provide a safety guarantee do so using quorum-based consensus. This requires a known set of participants (i.e. a permissioned network) and extensive communication between them to reach agreement. This restricts the number of participants in the network. Furthermore, quorum based consensus can only tolerate up to 1/3rd of the participants becoming faulty.

A small participant set and low threshold for faults generally pushes these networks to put large barriers to entry, either through large staking requirements or politics.

### Prioritizing Liveness

Chains that prioritize liveness generally do so by relying on fork choice rules such as the longest chain rule from Nakamoto consensus. These protocols allow each participant to make a local choice about which fork to follow, and therefore do not require quorums and thus can be permissionless.

Additionally, due to a lack of quorums, these protocols can be quite message efficient. Thus, participation does not need to be artificially reduced to remain within bandwidth restrictions.

These protocols tolerate up to 1/2 of participants becoming faulty. The large fault tolerance threshold and the large number of participants provides for much higher resilience to corruption.

## Privacy

The motivation behind the design of Cryptarchia can be boiled down to this statement:

  *A block proposer should not feel the need to self-censor when proposing a block.*

Working to give leaders confidence in this statement has had ripple effects throughout the protocol, including that:

- **The block proposals should not be linkable to a leader**. An adversary should not be able to connect together the block proposals of a leader in order to build a profile. In particular, one should not be able to infer a proposer's stake from their past on-chain activity.
- **Cryptarchia must not reveal the stake of the leader** - that is, it must be a Private Proof of Stake (PPoS) protocol. If the activity of the leader reveals their stake values (e.g. through weighted voting), then this value can be used to reduce the anonymity set for the leader by bucketing the leader as high/low stake and can open him up to targeting.
- **Leaders should be protected against network triangulation attacks**. This is outside of the scope of this document, but it suffices to say that in-protocol cryptographic privacy is not sufficient to guarantee a leader's privacy. This topic is dealt with directly in [Blend Protocol](blend-protocol.md).

## Limitations of Cryptarchia V1

Despite our best efforts, we cannot provide perfect privacy and censorship resistance to all parties. In particular:

- We are unable to protect leaders from leaking information about themselves based on the contents of blocks they propose. The tagging attack is an example of this, where an adversary may distribute a transaction to only a small subset of the network. If the block proposal includes this transaction, the adversary learns that the leader was one of those nodes in that subset.
- The leader is a single point of failure (SPOF). Despite all the efforts we go through to protect the leader, the network can be easily censored by the leader. The leader may choose to exclude certain types of transactions from blocks, leading to a worse UX for targeted parties.

As far as we can tell, these limitations are not insurmountable and we have sketches towards solutions that we will develop in following iterations of the protocol.

# Overview

Cryptarchia is a probabilistic consensus protocol with properties similar to Bitcoin’s Nakamoto Consensus.

At a high level, Cryptarchia divides time into slots and at each slot, a leadership lottery is run. To participate in the lottery, a node must have held stake in the chain in the form of a note for a minimum time period. Given a sufficiently aged note, you can check if it has won a slot lottery by cryptographically flipping a weighted coin. The weight of the coin is proportional to the value of your note, thus higher valued notes lead to increased chances of winning. To ensure privacy and avoid revealing the note value, this lottery result is proven within a ZK proof system.

Our design starts from the solid foundation provided by Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake [eprint.iacr.org](https://eprint.iacr.org/2018/1132.pdf)  and builds upon it, incorporating the latest research at the intersection of cryptography, consensus and network engineering.

# Protocol

## Constants

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| $`f`$ | slot activation coefficient | The target rate of occupied slots. Not all slots contain blocks, many are empty.   (see [ANALYSIS-BLOCK-TIMES-BLEND-NETWORK](analysis-block-times-blend-network.md) for analysis leading to the choice of value) | 1/30 |
| $`k`$ | security parameter | Block depth finality. Blocks deeper than $`k`$ on any given chain are considered immutable. | 2160 blocks |
| *none* | slot length | The duration of a single slot. | 1 second |
| MAX_BLOCK_SIZE | max block size | The maximum size of the block body (not including the header) | 2 MiB (2,097,152 bytes) |
| MAX_BLOCK_TXS | max block transactions | The maximum number of transactions in a block | 1024 |
| $`W`$ | uncle reference window | The window width in expected block-intervals (each of $`f^{-1}`$ slots): the slot of the **parent** of a referenced [uncle](#uncle-references) must precede the slot of the referencing block by at most $`W\cdot f^{-1}`$ slots (360 at $`W=12`$). Anchoring the window to the parent bounds how far back the referencing chain must be retained to verify the uncle; a virtual upper bound on $`W`$ applies (see the note in [Uncle Selection](#uncle-selection)). | 12 |
| MAX_UNCLES | max uncle references | The maximum number of [uncles](#uncle-references) a block may reference. | 4 |

## Notation

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| $`s`$ | slot security parameter | Sufficient slots such that $`k`$ blocks have been produced with high probability. | $`3\lfloor \frac{k}{f}\rfloor`$ |
| $`T`$ | the block tree | This is the block tree observed by a node. |  |
| $`F_T`$ | tips of block tree $`T`$ | The set of concurrent forks of some block tree $`T`$. | $`F_T=\{b\in T:\forall c \in T\space \textbf{parent}(c) \neq b \}`$ |
| $`c_{loc}`$ | tip of local chain | The chain that a node considers to be the honest chain. | $`c_{loc} \in F_{T}`$ |
| $`B_\text{imm}`$ | the latest immutable block | The latest block which was committed (finalized) by the chain maintenance. | $`B_\text{imm} \in \textbf{ancestors}(c_{loc})`$ |
| $`sl`$ | slot number | Index of slot. $`sl=0`$ denotes the genesis slot. | $`sl=0,1,2,3,\dots`$ |
| $`ep`$ | epoch number | Index of epoch. $`ep=0`$ denotes the genesis epoch. | $`ep=0,1,2,3,\dots`$ |

## Latest Immutable Block

The latest immutable block $`B_\text{imm}`$ is the most recent block considered permanently finalized. The blocks deeper than $`B_\text{imm}`$ in the local chain $`c_{loc}`$ are never to be reorganized.

This is maintained locally by the [Chain Maintenance](#chain-maintenance) procedure. When the [Online fork choice rule](fork-choice.md) is in use, $`B_\text{imm}`$ corresponds to the $`k`$-deep block. However, it may be deeper than the $`k`$-deep block if the fork choice rule has been switched from Online to [Bootstrap](fork-choice.md). Unlike the $`k`$-deep block, $`B_\text{imm}`$ does not advance as new blocks are added unless the Online fork choice rule is used.

The details of fork choice rule transitions are defined in the bootstrap spec: [Cryptarchia Bootstrapping & Synchronization](cryptarchia-v1-bootstr-sync.md)

## Slot

Time is divided up into slots of equal length, where one instance of the leadership lottery is held in each slot. A slot is said to be occupied if some validator has won the leadership lottery and proposed a block for that slot, otherwise the slot is said to be unoccupied.

## Epoch

Cryptarchia has a few global variables that are adjusted periodically in order for consensus to function. Namely, we need:

- Dynamic participation, thus the eligible notes must be refreshed regularly.
- An unpredictable source of randomness for the leadership lottery. This source of randomness is derived from in-protocol activity and thus must be selected carefully to avoid giving adversaries an advantage.
- Approximately constant block production rate achieved by dynamically adjusting the lottery difficulty based on observed participation levels.

The order in which these variables are calculated is important and is done w.r.t. the epoch schedule.

### Epoch Schedule

An epoch is divided into 3 phases, as outlined below.

| Epoch Phase | Phase Length | Description |
| --- | --- | --- |
| Stake Distribution Snapshot | $`s`$ slots | A snapshot of note commitments are taken at the beginning of the epoch. We wait for this value to finalize before entering the next phase. |
| Buffer phase | $`s`$ slots | After the stake distribution is finalized, we wait another slot finality period before entering the next phase. This is to further ensure that there is at least one honest leader contributing to the epoch nonce randomness. If an adversary can predict the nonce, they can grind their coin secret keys to gain an advantage. |
| Lottery Constants Finalization | $`s+\lfloor\frac{k}{f}\rfloor=4\lfloor\frac{k}{f}\rfloor`$ slots | On the $`2s^{th}`$ slot into the epoch, the epoch nonce $`\eta`$ and the inferred total stake $`D`$ can be computed. We wait another $`4\frac{k}{f}`$ slots for these values to finalize. |

The **epoch length** is the sum of the individual phases: $`3\lfloor \frac{k}{f} \rfloor + 3\lfloor \frac{k}{f} \rfloor + 4\lfloor \frac{k}{f} \rfloor =10 \lfloor \frac{k}{f} \rfloor`$ slots.

### Epoch State

The epoch state holds the variables derived over the course of the epoch schedule. It is the 3-tuple $`(\mathbb{C}_\text{LEAD}, \eta, D)`$ described below.

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| $`\mathbb{C}_{\text{LEAD}}`$ | Eligible Leader Notes Commitment | A commitment to the set of notes eligible for leadership. | See [Eligible Leader Notes](#eligible-leader-notes) |
| $`\eta`$ | Epoch Nonce | Randomness used in the leadership lottery (selected once per epoch) | See [Epoch Nonce](#epoch-nonce) |
| $`D`$ | Inferred Total Stake (Lottery Difficulty) | Total stake inferred from watching the results of the lottery during the course of the epoch. $`D`$ is used as the stake relativization constant for the following epoch. | See [Total Stake Inference](#total-stake-inference) |

### Eligible Leader Notes

A note is eligible to participate in the leadership lottery if it has not been spent and was a member of the note set at the beginning of the previous epoch, i.e. they are members of $`\mathbb{C}_\text{LEAD}`$.

**Note Ageing**

If an adversary knows the epoch nonce $`\eta`$, they may grind a note that wins the lottery more frequently than should be statistically expected. Thus, it’s critical that notes participating in the lottery are sufficiently old to ensure that they have no predictive power over $`\eta`$.

### Epoch Nonce

The epoch nonce $`\eta`$ is evolved after each block.

Given block $`B = (parent,sl, \rho_\text{LEAD},\dots)`$ where

- $`parent`$ is the parent of block $`B`$
- $`sl`$ is the slot that $`B`$ is occupying.
- $`\rho_\text{LEAD}`$ is the epoch nonce entropy contribution from the block’s leadership proof

Then, $`\eta_B`$ is derived as

$$
\eta_{B} = \mathrm{zkHASH}(D_{\mathrm{epoch}}\mathbin{\|}\eta_{\mathrm{parent}}\mathbin{\|}\rho_{\mathrm{LEAD}}\mathbin{\|}\mathrm{Fr}(sl))
$$

where $`D_{\mathrm{epoch}}`$ is the domain separator `EPOCH_NONCE_V1`, $`\mathrm{Fr}(sl)`$ maps the slot number to the corresponding scalser in Poseidon’s scalar field and $`\mathrm{zkHASH}(..)`$ is Poseidon2 as specified in [Common Cryptographic Components](common-cryptographic-components.md) .

The epoch nonce used in the next epoch is $`\eta_{B'}`$ where $`B'`$ is the last block before the start of the “Lottery Constants Finalization” phase in the epoch schedule.

### Total Stake Inference

Given that stake is private in Cryptarchia, and that we want to maintain an approximately constant block rate, we must therefore adjust the difficulty of the slot lottery somehow based on the level of participation. The inference counts the number of **occupied slots** of the honest chain — the slots holding a canonical block or one of the [uncle](#uncle-references) blocks it references. Therefore, lottery wins lost to forks still contribute to the estimate, and each slot is counted once however many blocks fall in it. The details can be found in the following document:

[Total Stake Inference](cryptarchia-total-stake-inference.md)

### Epoch State Pseudocode

At the start of each epoch, each validator must derive the new epoch state variables. This is done through the following protocol:

$`\text{define } \textbf{compute\_epoch\_state}(ep, tip \in T)\to(\mathbb{C}_\text{LEAD}^{ep},\eta^{ep},D^{ep})`$ :

  $`\textbf{case}\space ep = 0:`$

> The genesis epoch state is hardcoded upon chain initialization.

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{return}\space (\mathbb{C}_\text{GENESIS}, \eta_\text{GENESIS}, D_\text{GENESIS})`$

  $`\textbf{otherwise}:`$

> The epoch state is derived w.r.t. observations in the previous epoch. Here we compute the slot at the start of the previous epoch. We will query observations relative to this slot.

&nbsp;&nbsp;&nbsp;&nbsp;$`sl_{ep-1} \coloneqq (ep-1) \cdot \text{EPOCH\_LENGTH}`$

> Notes eligible for leadership lottery are those present in the commitment root at the start of the previous epoch.

&nbsp;&nbsp;&nbsp;&nbsp;$`\mathbb{C}_\text{LEAD}^{ep} \coloneqq \textbf{commitment\_root\_at\_slot}(sl_{ep-1}, tip)`$

> The epoch nonce for epoch $`ep`$ is the value of $`\eta`$ at the beginning of the lottery constants finalization phase in the epoch schedule

&nbsp;&nbsp;&nbsp;&nbsp;$`\eta^{ep} \coloneqq \textbf{epoch\_nonce\_at\_slot}(sl_{ep-1} + \lfloor6\frac{k}{f}\rfloor, tip)`$

> Total active stake is inferred from the number of blocks produced in the previous epoch during the stake freezing phase. It is also derived from the previous estimate of total stake, thus we recurse here to retrieve the previous epochs estimate $`D^{ep-1}`$

&nbsp;&nbsp;&nbsp;&nbsp;$`(\_,\_,D^{ep-1}) \coloneqq \textbf{compute\_epoch\_state}(ep-1,tip)`$

> The number of distinct occupied slots during the first $`6\frac{k}{f}`$ slots of the previous epoch: a slot counts if it holds a block of the chain of $`tip`$ and/or one or more [uncles](#uncle-references) referenced by the blocks of that chain **that themselves lie in the window**, and each slot is counted at most once. Referenced uncles are genuine lottery wins that were lost to forks; counting them gives a more accurate estimate of consensus participation. No filtering is needed here: an uncle carried by a block of the chain was validated as a condition of that block's acceptance (see [Uncle References](#uncle-references)), so every node holding the chain counts exactly the same uncles.

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{in\_window}(sl) \coloneqq sl_{ep - 1} \le sl \lt sl_{ep-1}+\lfloor 6\frac{k}{f} \rfloor`$

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{chain} \coloneqq \textbf{ancestors}(tip)`$

> The referenced uncles are the headers carried in the `uncle_headers` field of the blocks of the chain that fall inside the window. A block outside the window contributes nothing — neither its own slot nor the slots of the uncles it carries — so the count of a window is closed the moment that window ends: no block proposed afterwards can alter the estimate of a past epoch, however far back an uncle it carries may reach. Each entry was checked against the rules of [Uncle References](#uncle-references) when its referencing block was validated — the parent of the uncle lies on the chain while the uncle itself does not, the uncle precedes its referencer and its parent does so by at most $`W\cdot f^{-1}`$ slots, its Proof of Leadership verifies against inputs derived from the chain, and its signature verifies over its header — so no entry needs to be re-examined or skipped here.

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{referenced\_uncles} \coloneqq \{\, U : A \in \textbf{chain},\ \textbf{in\_window}(sl_A),\ (U, \sigma_U) \in A.\text{uncle\_headers} \,\}`$

&nbsp;&nbsp;&nbsp;&nbsp;$`N_\text{BLOCKS}^{ep-1} \coloneqq \left|\ \{sl_B : B \in \textbf{chain},\ \textbf{in\_window}(sl_B)\}\ \cup\ \{sl_U : U \in \textbf{referenced\_uncles},\ \textbf{in\_window}(sl_U)\}\ \right|`$

&nbsp;&nbsp;&nbsp;&nbsp;$`D^{ep} \coloneqq \textbf{infer\_total\_active\_stake}(D^{ep-1}, N_\text{BLOCKS}^{ep-1})`$

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{return}\space (\mathbb{C}_\text{LEAD}^{ep}, \eta^{ep}, D^{ep})`$

## Leadership Lottery

A lottery is run for every slot to decide who is eligible to propose a block. For each slot, we can have 0 or more winners. In fact, it’s desirable to have short slots and many empty slots to allow for the network to propagate blocks and to reduce the chances of two leaders winning the same slot which are guaranteed forks.

### Proof of Leadership

The specifications of how a leader can prove that they have won the lottery are specified in the following document:

### Leader Rewards

As an incentive for producing blocks, leaders are rewarded with every block proposal. The rewarding protocol is specified in [**Anonymous Leaders Reward Protocol**](bedrock-anonymous-leaders-reward.md).

## Block Chain

### Fork Choice Rule

We use two fork choice rules, one during bootstrapping and a second once a node completes bootstrapping.

During bootstrapping, we must be resilient to malicious peers feeding us false chains, this calls for a more expensive fork choice rule that can differentiate between malicious long-range attacks and honest chains.

After bootstrapping we commit to the most honest looking chain we found and switch to a fork choice rule that rejects chains that diverge by more than $`k`$ blocks

[Cryptarchia Fork Choice Rule](fork-choice.md)

### Block ID

Block ID is defined by the hash of the block header [Block Header](#block-header), where `hash` is Blake2b as specified in [Common Cryptographic Components](common-cryptographic-components.md). The header commits to the whole block body through $`body\_root`$ (see [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#header)), so the block ID transitively commits to the signed uncle headers the block carries as well as to its transactions: two blocks with the same ID are identical byte for byte.

```python
def block_id(header: Header) -> hash
    return hash(
        b"BLOCK_ID_V1",
        header.bedrock_version,
        header.parent_block,
        header.slot.to_bytes(8, byteorder='little'),
        header.body_root,
        # PoL fields
        header.proof_of_leadership.leader_voucher,
        header.proof_of_leadership.entropy_contribution,
        header.proof_of_leadership.proof.serialize(),
        header.proof_of_leadership.leader_key.compressed(),
    )
```

### Block Header

```python
class Header:                                # 297 bytes
    bedrock_version: byte                    # 1 bytes
    parent_block: hash                       # 32 bytes
    slot: int                                # 8 bytes
    body_root: hash                          # 32 bytes
    proof_of_leadership: ProofOfLeadership   # 224 bytes

class ProofOfLeadership:                     # 224 bytes
    proof: Groth16Proof                      # 128 bytes
    entropy_contribution: zkhash             # 32 bytes
    leader_key: Ed25519PublicKey             # 32 bytes
    leader_voucher: zkhash                   # 32 bytes
```

The field order above is the wire order defined in [Canonical Encoding](bedrock-v1.1-block-construction.md#canonical-encoding). The [Block ID](#block-id) preimage above absorbs the same `ProofOfLeadership` fields in a different order; that is deliberate, since the preimage is a domain-separated enumeration of header fields rather than a re-serialization of the header.

### Block

[Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)

### Uncle References

A block may reference up to `MAX_UNCLES` **uncles** (see [Constants](#constants)). An uncle is a valid fork block that is not part of the chain of the referencing block but shares a common ancestor with it. A block references an uncle by carrying its full signed header in the `uncle_headers` field of both the block proposal and the reconstructed block ([Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#block)); the block ID of an uncle is derived from the carried header as $`\textbf{block\_id}(U)`$ and is not recorded separately. Following the list convention of the [Mantle Transaction Encoding](mantle-transaction-encoding.md) — *"Any lists are length-prefixed with fixed width uints"* — the list is serialized as a 1-byte little-endian element count followed by that many fixed-size entries (one byte suffices for the `MAX_UNCLES` bound), so it carries its own length. The header holds no uncle data of its own and is fixed-size; it commits to the carried entries — signatures included — through $`body\_root`$, and hence so does the [Block ID](#block-id). Any node holding a block therefore also holds the signed headers of the uncles it references, however it obtained that block, and cannot hold a variant of them. The size of a proposal varies with the number of referenced uncles; the indistinguishability of proposals required by the [Blend Protocol](blend-protocol.md) is preserved at the message layer instead: [Payload Formatting](payload-formatting.md) fixes every dispersed payload body to the maximum payload size `Max_Body_Length` — set from the maximum proposal size — padding shorter proposals with random data.

The only purpose of an uncle reference is to feed the [Total Stake Inference](#total-stake-inference), which infers the total active stake from the number of **occupied slots** — the slots in which at least one leader won the lottery. A referenced uncle is a genuine lottery win, backed by a valid Proof of Leadership, that was lost to a fork (predominantly caused by network delays); its slot was occupied, but without the reference the canonical chain would not observe it. Counting the slots of the referenced uncles alongside those of the canonical blocks recovers those occupied slots and gives a more accurate estimate of the total active stake.

At the moment a block is produced it is not yet known which branch of a fork will become canonical: some nodes build on one branch and some on the other. By referencing the blocks of the competing branches as uncles, whichever branch ultimately becomes canonical still counts the lottery wins of the branches that lost. This is the intent of uncle references — to let each branch count its counterpart branches — and it is what improves the total stake estimate.

**A block is valid only if every uncle it carries is valid.** The rules below are validity conditions, checked as step 10 of [Block Header Validation](#block-header-validation): a block carrying an entry that fails any of them is rejected, exactly as one carrying an invalid Proof of Leadership is. Gating validity this way is safe because every rule is a function of the chain being extended and of the carried entry alone — never of the block tree $`T`$, the node's pruning state, or the node's network history. All nodes therefore reach the same verdict on the same block; no node can be starved of the inputs needed to decide, since the entry travels inside the very block whose validity depends on it; and an adversary manipulating which fork blocks are visible can neither make a block valid for some nodes and invalid for others nor thereby influence block inclusion. Requiring validity also keeps fabricated uncles out of the chain permanently, instead of leaving every node that ever synchronizes to detect and discard the same entries again.

An entry $`(U, \sigma_U)`$ of the `uncle_headers` list of a block $`A`$ is **valid** — we say $`\textbf{valid\_uncle}(U, \sigma_U, A)`$ holds — only if all of the following hold:

- The parent of the uncle is part of the chain of the referencing block: $`U.\text{parent\_block} \in \textbf{ancestors}(A)`$. Hence the uncle is the **first block of its fork**, and its chain is a prefix of the chain of $`A`$. Blocks deeper in a fork branch cannot be referenced: verifying their Proof of Leadership requires the ledger state of the fork branch, which cannot be reconstructed from the chain of $`A`$ (see the verification rule below).
- The uncle itself is not part of the chain of the referencing block: $`\lnot\,\textbf{is\_ancestor}(U, A)`$ — equivalently, $`U`$ is not the block of the chain of $`A`$ at slot $`sl_U`$.
- The uncle precedes the referencing block, and the **parent** of the uncle lies within the uncle reference window (see [Constants](#constants)): $`sl_A \gt sl_U`$ and $`sl_A - sl_{\textbf{parent}(U)} \le W\cdot f^{-1}`$. The window is anchored to the parent rather than to the uncle itself because the parent is the block whose historical state the remaining checks need: $`ledger_\text{LATEST}`$ as of $`U.\text{parent\_block}`$ is required to verify the Proof of Leadership below, and anchoring here bounds how far back the chain of $`A`$ must be retained to supply it. Anchoring to $`sl_U`$ would not bound it: a leader may build on a stale tip, so $`sl_U - sl_{\textbf{parent}(U)}`$ is unbounded and a block could demand a ledger root arbitrarily deep in the chain. The anchor also matches [Fork Pruning](#fork-pruning), which prunes by divergence depth — and the parent of a first-fork block is exactly that divergence point. Since $`sl_U \gt sl_{\textbf{parent}(U)}`$ by step 5 of [Block Header Validation](#block-header-validation), this rule implies $`0 \lt sl_A - sl_U \lt W\cdot f^{-1}`$: the uncle's own slot falls inside the window as a consequence, not as a separate condition.
- The [Proof of Leadership](cryptarchia-proof-of-leadership.md) of $`U`$ verifies against public inputs derived from the chain of $`A`$: the slot, $`P_\text{LEAD}`$ and $`\rho_\text{LEAD}`$ taken from the header of $`U`$; the epoch state $`(\mathbb{C}_\text{LEAD}, \eta, D)`$ of the epoch of $`sl_U`$ as derived on the chain of $`A`$; and $`ledger_\text{LATEST}`$ as of $`U.\text{parent\_block}`$, which is a historical ledger root of the chain of $`A`$ because the parent lies on that chain. Since the chain of the uncle is a prefix of the chain of $`A`$, a genuine fork win was proven against exactly these values and verifies; a fabricated header does not. These are the same inputs a node derives to validate the Proofs of Leadership of the canonical blocks themselves; in particular $`ledger_\text{LATEST}`$ is a function of the **executed** chain, so this check requires a full node's possession of the chain — headers alone do not suffice, exactly as they do not suffice to validate canonical blocks.
- The carried signature verifies over the header of $`U`$: $`\textbf{verify\_signature}(U, \sigma_U, P_\text{LEAD})=True`$, with $`P_\text{LEAD}`$ taken from that header — the same binding required of a canonical proposal by step 9 of [Block Header Validation](#block-header-validation). This ensures the uncle is a block authorized by the leader who won the lottery, not a fabricated header wrapped around a replayed proof.

A proposer can always determine in advance whether an entry will be accepted: the chain of $`A`$ is fixed the moment it selects the parent of $`A`$, and every rule reads only that chain and the entry itself, so proposer and validators evaluate identically and a well-implemented proposer never builds a block that others reject. For the same reason all nodes — including a node bootstrapping from genesis — accept exactly the same blocks and, having accepted them, count exactly the same uncles and derive exactly the same estimate. A carried uncle is checked exactly as a received proposal is — the Proof of Leadership and the signature binding it to the header — minus the chain-context steps that do not apply to a fork block. One caveat is recorded for honesty: the signature proves that the winning leader authorized this header, not that the block was published in its slot — the owner of a winning note can fabricate and self-sign such a header later. This is benign: the Proof of Leadership still attests a genuine lottery win at that slot, which is precisely the signal the [Total Stake Inference](#total-stake-inference) measures, and the count is taken per distinct slot, so neither replay nor self-wrapping can add occupied slots beyond genuine wins.

Uncle references are **not** required to be unique, and duplicates are permitted — the same uncle may be referenced by more than one block on the canonical chain, and a single block may carry the same entry twice. Each occurrence is validated on its own and a duplicate passes the rules above exactly as the first occurrence does; it merely wastes one of the `MAX_UNCLES` entries. Duplication is harmless because the [Total Stake Inference](#total-stake-inference) counts **occupied slots**, not references: it forms the set of slots occupied by the canonical chain together with the slots of the uncles that chain references, and counts each slot once. A slot therefore contributes at most once to the estimate no matter how many blocks fall in it — the same uncle referenced several times, two distinct uncles that share a slot, and an uncle that shares its slot with a canonical block each add a single occupied slot, or none if that slot is already counted. This matches the slot lottery, which activates a slot with probability $`f`$ regardless of how many leaders win it.

#### Uncle Selection

When constructing a block $`B`$ at slot $`sl_B`$, the proposer fills the `uncle_headers` field by selecting from the accepted fork blocks in its block tree $`T`$ that are valid uncles for $`B`$ — the first blocks of the competing branches that $`B`$'s own chain does not contain. Only a block whose parent is on $`B`$'s chain qualifies (see the validity rules above), so only such blocks are candidates; carrying anything else would make $`B`$ itself invalid. Because the [Total Stake Inference](#total-stake-inference) counts occupied slots, the proposer further narrows the candidate set to only the uncles that would add a **new** occupied slot: it excludes any uncle whose slot is already occupied on the **chain that $`B`$ extends** (the ancestors of $`B`$) — whether that slot holds a canonical block or an uncle the chain already references — since referencing it would waste one of the $`\texttt{MAX\_UNCLES}`$ entries without changing the count. This last narrowing is a best-effort optimization and is **not** a validity rule: a proposer that references an already-occupied slot produces a block that is still valid, merely one entry poorer. The preceding conditions are not optional — validation enforces every one of them.

An uncle is **not** excluded because some *other* branch referenced it, nor because its slot is occupied on some other branch. The Total Stake Inference counts only the slots occupied by the canonical chain and its uncles, and at production time it is unknown which branch will become canonical. If a competing branch referenced an uncle but that branch is later discarded, its reference does not count; $`B`$ must therefore remain free to reference the same uncle, so that its lottery win is still counted should $`B`$'s branch win.

```python
def uncle_candidates(B) -> Set[Block]:
    # Slots already occupied on the chain B extends: the slots of B's ancestors (canonical
    # blocks) and the slots of the uncles those ancestors already reference. The Total Stake
    # Inference counts occupied slots, so an uncle whose slot is already occupied adds nothing —
    # referencing it would waste an entry. Slots occupied on *other* branches are deliberately
    # not excluded: they do not count unless that branch becomes canonical.
    referenced_uncles = { U for A in ancestors(B) for (U, _) in A.uncle_headers }
    occupied = { sl_A for A in ancestors(B) } | { sl_U for U in referenced_uncles }

    # Accepted fork blocks that are valid uncles for B and would add a new occupied slot
    # (see the validity rules in Uncle References).
    return { U for U in T if
               parent(U) in ancestors(B)          # first block of its fork: the only referenceable kind
               and not is_ancestor(U, B)          # a fork, not on B's chain
               and sl_B > sl_U                    # the uncle precedes B
               and sl_B - sl_parent(U) <= W / f   # its parent is within the uncle window
               and sl_U not in occupied           # its slot is not already occupied on B's chain
           }
```

The proposer then selects at most $`\texttt{MAX\_UNCLES}`$ of these candidates by deterministically taking those with the oldest parent first. A candidate leaves the window when its **parent** ages out of it, so ordering by parent slot is ordering by time to expiry:

```python
def select_uncles_oldest(B) -> array[SignedHeader]:   # at most MAX_UNCLES entries, in selection order
    ordered = sorted(uncle_candidates(B), key=lambda U: (sl_parent(U), sl_U, block_id(U)))
    selected, slots = [], set()
    for U in ordered:
        if len(selected) == MAX_UNCLES:
            break
        if sl_U in slots:              # at most one uncle per slot: a second adds no occupied slot
            continue
        slots.add(sl_U)
        selected.append(signed_header(U))   # header of U with the signature it arrived under
    return selected                    # the list carries its own length; no padding entries
```

This deterministic rule is simple and, without communication between proposers, robust. Two non-communicating proposers with the same candidate set produce the same selection, but they also tend to produce **competing blocks** that extend the same tip, of which only one becomes part of the canonical chain — the [Fork Choice Rule](fork-choice.md) discards the rest. The identical uncle references on the discarded competitors therefore cost nothing, and along a single canonical chain, excluding the slots already occupied on a block's own chain keeps successive blocks from re-counting a slot.

*Which* candidates a proposer selects is proposer-local: it may reference fewer uncles than it could, or pass over a candidate for another, and its block remains valid. *What* it may reference is not — every carried entry must satisfy the validity rules above, and a block carrying one that does not is rejected (see [Block Header Validation](#block-header-validation)). The procedure given here is therefore a recommendation for filling the entries well, not a consensus rule. Because uncle references carry no fork-choice weight and grant no reward, a proposer has no incentive to deviate from it, and deviating within the rules only affects the accuracy of the [Total Stake Inference](#total-stake-inference).

A referenced uncle never becomes part of the chain:

- The transactions of the uncle are not executed and have no effect on the ledger state (see [Block Execution](bedrock-v1.1-block-construction.md#block-execution)).
- The uncle carries no weight in the [Fork Choice Rule](fork-choice.md).
- The uncle grants no block reward.

The only effect of a referenced uncle is its contribution to the [Total Stake Inference](#total-stake-inference). Nothing further gates it: an uncle carried by a block of the chain has already been verified as a condition of that block's validity, so the inference counts its slot — whenever that slot and its referencing block both fall in the observation window — without re-examining the entry.

> **Note:** The uncle reference window spans $`W`$ expected block-intervals — $`W\cdot f^{-1}`$ slots, 360 at the default $`W=12`$ and $`f=1/30`$ — and `MAX_UNCLES` is 4. Forks are predominantly caused by network delays and resolve within a few slots, so this window comfortably captures the forks worth referencing. $`W`$ carries a **virtual upper bound** of $`\lfloor 0.6\,k \rfloor`$ — equivalently $`W\cdot f^{-1} \le 0.6\frac{k}{f} = \frac{s}{5}`$ — virtual in that no validation rule evaluates it: it constrains the choice of the constant itself, limiting the expense of lineage checking — how far back the chain of a referencing block must be reachable to verify an uncle — and any retuning of $`W`$ must stay within it. The bound keeps the window strictly inside the finalization window, which is what the proposer needs: a candidate whose parent is within the window is still present in its block tree, since only forks that diverged deeper than the latest immutable block — at most $`s`$ slots back — are pruned (see [Fork Pruning](#fork-pruning)); because the window is anchored to the parent, which is the divergence point, the two conditions are stated over the same quantity. The [Total Stake Inference](#total-stake-inference) needs no such bound: it counts only the blocks of its observation window and the uncles those blocks carry, so the count of a past window is closed once the window ends whatever the value of $`W`$, and recomputing $`N_\text{BLOCKS}`$ for a past epoch always yields the same value.
>
> **Note:** The validity rules are functions only of the referencing chain and the carried entry, and the signed headers are carried inside the blocks themselves (the `uncle_headers` field of [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#block)) — availability is structural, and referencing an uncle is inseparable from publishing its signed header. Every node therefore accepts exactly the same blocks and, from them, computes the same $`N_\text{BLOCKS}`$ and the same $`D`$, at any time; a bootstrapping node reproduces the estimate of every past epoch from the chain data alone. An adversary manipulating the visibility of fork blocks can thus affect neither block inclusion nor the agreement of the estimate — only whether its own lottery wins are referenced at all. Because a block carrying an unverifiable entry is rejected outright, no such entry ever becomes chain data, and the cost of checking one is paid once by the receiving node rather than by every node that later synchronizes. The carried signed headers are retained as part of the chain data, bounded by `MAX_UNCLES` entries per block.

### Block Header Validation

Given block $`B=(header, uncle\_headers, transactions)`$ and the block tree $`T`$ where:

- $`header`$ is the header defined in [Header](bedrock-v1.1-block-construction.md#header)
- $`uncle\_headers`$ is the list of signed headers of the uncles the block references, defined in [Block](bedrock-v1.1-block-construction.md#block)
- $`transactions`$ is the sequence of transactions in the block

We say $`\textbf{valid\_header}(B)`$ returns True if all of the following constraints hold, otherwise it returns False.

1. $`header.\text{version}.\text{bedrock\_version} = 1`$
  Ensure bedrock version number.

2. $`\textbf{bytes}(transactions) \le \text{MAX\_BLOCK\_SIZE}`$
  Ensure the block body, i.e. the serialized sequence of transactions, does not exceed the maximum allowed size. The header is not part of the body and does not count towards this limit.

3. $`\textbf{length}(transactions) \le \text{MAX\_BLOCK\_TXS}`$
  Ensure the number of transactions in the block does not exceed the limit.

4. $`\textbf{body\_root}(uncle\_headers, transactions) = header.\text{body\_root}`$
  Ensure the body root commits to both parts of the block body. It is computed as

  ```python
  def body_root(uncle_headers: list[SignedHeader], transactions: list[SignedMantleTx]) -> hash:
      return hash(
          b"BODY_ROOT_V1",
          serialize(uncle_headers),  # 1-byte count, then the fixed 361-byte entries
          merkle_root(transactions),
      )
  ```

  where $`\textbf{merkle\_root}`$ is the root of the Merkle tree built from transaction hashes (see Mantle - Mantle Transaction Hash) as leaves, using `0` to represent the hash of an empty transaction and padding the leaves to the closest power of two, and $`\textbf{serialize}`$ is the list encoding of [Block Proposal](bedrock-v1.1-block-construction.md#block-proposal) — a 1-byte little-endian element count followed by that many entries, so an empty list encodes as a single zero byte. The serialized list is committed directly, with no inner hash: the element count and the fixed 361-byte entries keep the flat preimage unambiguous, and the single `BODY_ROOT_V1` tag versions the whole construction. Because the signatures of the carried uncle headers are inside $`\textbf{serialize}(uncle\_headers)`$, they are committed here and hence in the [Block ID](#block-id); a copy of a block that differs in any of those bytes has a different ID and is a different block.

5. $`header.\text{slot} \gt \textbf{fetch\_header}(header.\text{parent\_block}).\text{slot}`$
  Ensure the block’s slot comes after the parent block’s slot.

6. $`\textbf{wallclock\_time}().\textbf{to\_slot}() \ge header\text{.slot}`$
  Ensure this block’s slot time has elapsed. Local time is used in this validation. See [Clocks](#clocks) for discussion around clock synchronization.

7. $`header.\text{parent} \in T`$
  Ensure we have already accepted the block’s parent into the block tree.

8. $`\textbf{height}(B) \gt \textbf{height}(B_{imm})`$
  Ensure the block comes after the latest immutable block. Assuming that $`T`$ prunes all forks diverged deeper than $`B_\text{imm}`$, this step, along with step 5, ensures that $`B`$ is descendant from $`B_\text{imm}`$. If all forks cannot be pruned completely in the implementation, this step must be replaced with $`\textbf{is\_ancestor}(B_\text{imm}, B)`$, which checks whether $`B_\text{imm}`$ is an ancestor of $`B`$.

9. Verify the leader’s right to propose and ensure it is the one proposing this block:
  Given leadership proof $`\pi_\text{LEAD} = (\pi_\text{PoL},P_\text{LEAD},\sigma)`$, where

  - $`\pi_\text{PoL}`$ is the slot lottery win proof as defined in [Proof of Leadership](cryptarchia-proof-of-leadership.md)
  - $`P_\text{LEAD}`$ is the public key committed to in $`\pi_\text{PoL}`$.
  - $`\sigma`$ is a signature.

  A leaders proposal is valid if

  - $`\textbf{verify\_PoL}(T, parent,sl,P_\text{LEAD}, \pi_\text{PoL})=True`$
  - $`\textbf{verify\_signature}(H, \sigma, P_\text{LEAD})=True`$
    Ensure that the leader who won the lottery is actually proposing this block since PoL’s are not bound to blocks directly.

10. $`\forall\,(U, \sigma_U) \in uncle\_headers:\ \textbf{valid\_uncle}(U, \sigma_U, B) = True`$
  Ensure every carried uncle is valid, as defined by the rules of [Uncle References](#uncle-references): the parent of $`U`$ lies on the chain of $`B`$, $`U`$ itself does not, $`U`$ precedes $`B`$ and the slot of its parent precedes $`sl_B`$ by at most $`W\cdot f^{-1}`$, its Proof of Leadership verifies against inputs derived from the chain of $`B`$, and $`\sigma_U`$ verifies over $`U`$ under the $`P_\text{LEAD}`$ of that header. A block carrying an entry that fails any of these is rejected.

  The list bound `len(uncle_headers) <= MAX_UNCLES` is a constraint of the serialization schema, rejected at decode time (a block that does not parse is no block), and so is not restated here. Duplicate entries are permitted: each is validated independently and a repeat passes exactly as the first occurrence does.

  Every input to these checks comes from the chain of $`B`$ or from the carried entry itself, both of which any node validating $`B`$ necessarily has — the entries travel inside $`B`$ and are committed by its $`body\_root`$. Validity is therefore a function of the block and the chain it extends alone, so all nodes agree on it and an adversary influencing what nodes know of forks cannot influence block inclusion.

### Chain Maintenance

We define the chain maintenance procedure $`\textbf{on\_block}(state,B)`$ that governs how the block tree $`T`$ is updated.

**Note:** It’s assumed that block contents have already been validated by the execution layer w.r.t. the parent block’s execution state.

$`\text{define } \textbf{on\_block}(state, B)\to state'`$:

  $`(c_{loc}, B_\text{imm}, T) \coloneqq state`$

  **if** $`B \in T \lor \lnot \textbf{valid\_header}(B)`$:

> Either we’ve already seen $`B`$ or it’s invalid, in both cases we ignore this block

&nbsp;&nbsp;&nbsp;&nbsp;$`\textbf{return} \space state`$

  $`T' \coloneqq T \cup \{B\}`$

  $`c_{loc}' \coloneqq \begin{cases} B &\text{if } \textbf{parent}(B) = c_{loc}\\ \textbf{fork\_choice}(c_{loc}, F_{T'}, k, s) &\text{if } \textbf{parent}(B) \neq c_{loc} \end{cases}`$

  $`\text{if } \text{fork\_choice\_rule} = \text{ONLINE}:`$

> Explicitly commit to the $`k`$-deep block if the [Online Fork Choice Rule](fork-choice.md) is being used.

&nbsp;&nbsp;&nbsp;&nbsp;$`(T', B_\text{imm}) \coloneqq \textbf{commit}(T', c_{loc}', k)`$

  $`\textbf{return} \space (c_{loc}', B_\text{imm}, T')`$

### Commit

We define the procedure that commits to the block, which is $`depth`$ deep from $`c_{loc}`$. This procedure computes the new latest immutable block $`B_\text{imm}`$.

$`\text{define } \textbf{commit}(T,c_{loc},depth)\to (T', B_\text{imm}):`$

  $`\textbf{assert } \text{fork\_choice\_rule} = \text{ONLINE}`$

> Compute the latest immutable block, which is $`depth`$ deep from $`c_{loc}`$.

  $`B_\text{imm} \coloneqq \textbf{block\_at\_depth}(c_{loc}, depth)`$

> Prune all forks diverged deeper than $`B_\text{imm}`$, so that future blocks on those forks can be rejected by [Block Header Validation](#block-header-validation).

  $`T' \coloneqq \textbf{prune\_forks}(T, B_\text{imm}, c_{loc})`$

  $`\textbf{return} \space (T', B_\text{imm})`$

### Fork Pruning

We define the fork pruning procedure that removes all blocks which are part of forks diverged deeper than a certain block.

$`\text{define } \textbf{prune\_forks}(T, B)\to T':`$

  $`T' \coloneqq T`$

  $`\text{for each } B_\text{tip} \in F_T:`$

> If $`B_\text{tip}`$ is a fork diverged deeper than $`B`$, prune the fork.

&nbsp;&nbsp;&nbsp;&nbsp;$`B_{\text{div}} \coloneqq \textbf{common\_ancestor}(B_\text{tip}, B)`$

&nbsp;&nbsp;&nbsp;&nbsp;$`\text{if } B_\text{div} \neq B:`$

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$`T' \coloneqq \textbf{prune\_blocks}(B_\text{tip}, B_\text{div}, T)`$

  $`\textbf{return } T'`$

$`\text{define } \textbf{prune\_blocks}(B_\text{new}, B_\text{old}, T)\to T':`$

> Remove all blocks in the chain within range $`(B_\text{old}, B_\text{new}]`$ from $`T`$.

  $`(B, T') \coloneqq (B_\text{new}, T)`$

  $`\text{while } B \ne B_\text{old}:`$

&nbsp;&nbsp;&nbsp;&nbsp;$`T' \coloneqq T' \setminus \{B\}`$

&nbsp;&nbsp;&nbsp;&nbsp;$`B \coloneqq \textbf{parent}(B)`$

  $`\textbf{return } T'`$

### Versioning and Protocol Upgrades

Protocol versions are signalled through the `bedrock_version` field of the block header. Protocol upgrades need to be co-ordinated well in advance to ensure that node operators have enough time to update their node. We will use block height to schedule the activation of protocol updates. E.g. bedrock version 35 will be active after block height 32000.

# Annexes

## Proof of Stake vs. Proof of Work

From a privacy and resiliency point of view, Proof of Work is highly attractive. The amount of hashing power of a node is private, they can provide a new public key for each block he mines ensuring that his blocks cannot be connected by this identity, and PoW is not susceptible to long range attacks as is PoS. Unfortunately, it is wasteful and demands that leaders have powerful machines. We want to ensure strong decentralization by having a low barrier to entry and we believe we can achieve a good enough level of security given by having participants have an economic stake in the protocol.

## Clocks

Cryptarchia depends on honest nodes having relatively in-sync clocks. We are currently rely on NTP to synchronize clocks, this may be improved upon in the future, borrowing ideas from Ouroboros Chronos: Permissionless Clock Synchronization via Proof-of-Stake  [eprint.iacr.org](https://eprint.iacr.org/2019/838.pdf)

## References

1. Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake [eprint.iacr.org](https://eprint.iacr.org/2018/1132.pdf)
2. Ouroboros Chronos: Permissionless Clock Synchronization via Proof-of-Stake  [eprint.iacr.org](https://eprint.iacr.org/2019/838.pdf)

## Test Vectors

The operations used to derive the transaction Merkle root are the same as those defined in Test Vectors. That root is no longer a header field on its own: it is one of the two inputs to the `body_root` defined in step 4 of [Block Header Validation](#block-header-validation), alongside the serialized carried `uncle_headers`. The vectors below are generated by the implementation's `generate_body_root_test_vectors` (`core/src/header/mod.rs`) at commit `fca0fc6e`.

| Input | Output |
|-|-|
| empty block (no transaction) | `merkle_root(transactions)`: 0x0000000000000000000000000000000000000000000000000000000000000000 |
| one transaction per operation kind: <br />- `leaf[0]`: 0x6ab0046084f3ce8dad90eb28afe5692ad92d5d0588a4e868ad38d0d841d7a60e (Transfer)<br />- `leaf[1]`: 0xd3a1aa9d2df8383e389dba072b1397f5e7fc290f884e04147c787619f60493cf (ChannelConfig) <br />- `leaf[2]`: 0x50e5674eea7fa17f531a51159ea7c3cab843fb1c8e8bf9bd5518a8aad08865d3 (ChannelInscribe)<br />- `leaf[3]`: 0xd52da59d9db42391363d6c4f96447536e5dfff747b91b88320310b07581a8dee (ChannelDeposit)<br />- `leaf[4]`: 0x6f57c77dc872cc3f01380fbd57a97e9f7998a1cd8b24e84594ceba796cfa0822 (ChannelWithdraw)<br />- `leaf[5]`: 0x2c04be946507e2b8c239b85b03cf476a8be5af8e4de853660d0447a46ea460fc (ChannelTransfer)<br />- `leaf[6]`: 0x9ce9fa694b4c801eca6c9a1d3dca6401952404bda8c144fb16e03e3872fd475e (SDPDeclare)<br />- `leaf[7]`: 0x3555b3d8f5d05ea5d69efb17aab7639474738bcb4bfee8d354107433d781ef9c (SDPWithdraw)<br />- `leaf[8]`: 0x0a91ab8271016f212061e6b45ea35c95cfa0f9a70c5225508f284b2657f4d931 (SDPActive)<br />- `leaf[9]`: 0xc992f1a63a7ea665a3766fae6b032df3db12ef386caf0ef1f3654afedbc51c6c (LeaderClaim) | `merkle_root(transactions)`: 0xcfbf83500e534669d039d09ec9ada459970610bb03b2ce06f944df72833c7de3 |
| `uncle_headers`: empty list (encoded as the single byte 0x00)<br />- `merkle_root(transactions)`: 0xcfbf83500e534669d039d09ec9ada459970610bb03b2ce06f944df72833c7de3 | `body_root`: 0x12fecd1a7be7764cf1ac15cd034736f9b78832ea4f3fd5006ceb61c60569775a |
| `uncle_headers`: 2 entries (encoded as the count byte 0x02 followed by the two 361-byte entries below, each a 297-byte header and its 64-byte signature)<br />- `uncle_headers[0]`: 0x016666666666666666666666666666666666666666666666666666666666666666660000000000000066666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666660000000000000000000000000000000000000000000000000000000000000034b4d9043156cb6dcf0beb0a2949b7559c940d2bcb6dbe8c53a9b30278e3a7466600000000000000000000000000000000000000000000000000000000000000563913f1ba7ad4129a077acd56278e743fd45120226dd315fa49f3a9c5d07af6a174ab84d4555a279afe053e79c8bb794be3f7d2e71e92b8da1b490687cb8306<br />- `uncle_headers[1]`: 0x0177777777777777777777777777777777777777777777777777777777777777777700000000000000777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777700000000000000000000000000000000000000000000000000000000000000c853ad0f0cd2b619aea92ceec4fd56a24d6499d584ce79257e45cfd8139b60a77700000000000000000000000000000000000000000000000000000000000000ad17e45d503a16fb41c25c4b3025956c63b31015871e957f3562b47cebce784e5b392ce3dd05214afe09102e0d2ed8211a83b81f18231963a226198fd528df0c<br />- `merkle_root(transactions)`: 0xcfbf83500e534669d039d09ec9ada459970610bb03b2ce06f944df72833c7de3 | `body_root`: 0x40aacc6d9d7fced681980e3ed51d3046330e8fe4698095e0d88ba3999b6589d5 |
| `Header`:<br />- `bedrock_version`: 0x01<br />- `parent_block`: 0x1111111111111111111111111111111111111111111111111111111111111111<br />- `slot`: 42 (0x2a; encoded little-endian)<br />- `body_root`: 0x12fecd1a7be7764cf1ac15cd034736f9b78832ea4f3fd5006ceb61c60569775a (the empty-`uncle_headers` value above)<br />- `leader_voucher`: 0x4444000000000000000000000000000000000000000000000000000000000000<br />- `entropy_contribution`: 0x5555000000000000000000000000000000000000000000000000000000000000<br />- `proof`: 0x2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222<br />- `leader_key`: 0x17cb79fb2b4120f2b1ec65e4198d6e08b28e813feb01e4a400839b85e18080ce | `block_id`: 0xd97592227b832c6f1b8fb3556e22fc22149d5a5d51bdc2d1fd82a71e68518dd8 |