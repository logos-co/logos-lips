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
| MAX_BLOCK_SIZE | max block size | The maximum size of the block body (not including the header) | 1 MB |
| MAX_BLOCK_TXS | max block transactions | The maximum number of transactions in a block | 1024 |

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

Given that stake is private in Cryptarchia, and that we want to maintain an approximately constant block rate, we must therefore adjust the difficulty of the slot lottery somehow based on the level of participation. The details can be found in the following document:

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

> The number of blocks produced during the first $`6\frac{k}{f}`$ slots of the previous epoch

&nbsp;&nbsp;&nbsp;&nbsp;$`N_\text{BLOCKS}^{ep-1} \coloneqq |\{B \in T | sl_{ep - 1} \le sl_B \lt sl_{ep-1}+\lfloor 6\frac{k}{f} \rfloor\}|`$

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

Block ID is defined by the hash of the block header [Block Header](#block-header), where `hash` is Blake2b as specified in [Common Cryptographic Components](common-cryptographic-components.md)

```python
def block_id(header: Header) -> hash
    return hash(
        b"BLOCK_ID_V1",
        header.bedrock_version,
        header.parent_block,
        header.slot.to_bytes(8, byteorder='little'),
        header.block_root,
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
    block_root: hash                         # 32 bytes
    proof_of_leadership: ProofOfLeadership   # 224 bytes

class ProofOfLeadership:                     # 224 bytes
    leader_voucher: zkhash                   # 32 bytes
    entropy_contribution: zkhash             # 32 bytes
    proof: Groth16Proof                      # 128 bytes
    leader_key: Ed25519PublicKey             # 32 bytes
```

### Block

[Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)

### Block Header Validation

Given block $`B=(header, transactions)`$ and the block tree $`T`$ where:

- $`header`$ is the header defined in [Header](bedrock-v1.1-block-construction.md#header)
- $`transactions`$ is the sequence of transactions in the block

We say $`\textbf{valid\_header}(B)`$ returns True if all of the following constraints hold, otherwise it returns False.

1. $`header.\text{version}.\text{bedrock\_version} = 1`$
  Ensure bedrock version number.

2. $`\textbf{bytes}(transactions) \le \text{MAX\_BLOCK\_SIZE}`$
  Ensure the block body, i.e. the serialized sequence of transactions, does not exceed the maximum allowed size. The header is not part of the body and does not count towards this limit.

3. $`\textbf{length}(transactions) \le \text{MAX\_BLOCK\_TXS}`$
  Ensure the number of transactions in the block does not exceed the limit.

4. $`\textbf{merkle\_root}(transactions) = header.\text{block\_root}`$
  Ensure block root is over the transaction list. Compute the block root by using transaction hashes (see Mantle - Mantle Transaction Hash) as leaves, and `0` to represent the hash of an empty transaction, padding leaves to the closest power of two.

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
  - $`\textbf{verify\_signature}(\textbf{block\_id}(H), \sigma, P_\text{LEAD})=True`$
    Ensure that the leader who won the lottery is actually proposing this block since PoL’s are not bound to blocks directly.

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

The operations used to derive the `block_root` are the same as those defined in Test Vectors.

| Input | Output |
|-|-|
| empty block (no transaction) | `block_root`: 0x0000000000000000000000000000000000000000000000000000000000000000 |
| one transaction per operation kind: <br />- `leaf[0]`: 0x6ab0046084f3ce8dad90eb28afe5692ad92d5d0588a4e868ad38d0d841d7a60e (Transfer)<br />- `leaf[1]`: 0xd3a1aa9d2df8383e389dba072b1397f5e7fc290f884e04147c787619f60493cf (ChannelConfig) <br />- `leaf[2]`: 0x50e5674eea7fa17f531a51159ea7c3cab843fb1c8e8bf9bd5518a8aad08865d3 (ChannelInscribe)<br />- `leaf[3]`: 0xd52da59d9db42391363d6c4f96447536e5dfff747b91b88320310b07581a8dee (ChannelDeposit)<br />- `leaf[4]`: 0x6f57c77dc872cc3f01380fbd57a97e9f7998a1cd8b24e84594ceba796cfa0822 (ChannelWithdraw)<br />- `leaf[5]`: 0x2c04be946507e2b8c239b85b03cf476a8be5af8e4de853660d0447a46ea460fc (ChannelTransfer)<br />- `leaf[6]`: 0x9ce9fa694b4c801eca6c9a1d3dca6401952404bda8c144fb16e03e3872fd475e (SDPDeclare)<br />- `leaf[7]`: 0x3555b3d8f5d05ea5d69efb17aab7639474738bcb4bfee8d354107433d781ef9c (SDPWithdraw)<br />- `leaf[8]`: 0x0a91ab8271016f212061e6b45ea35c95cfa0f9a70c5225508f284b2657f4d931 (SDPActive)<br />- `leaf[9]`: 0xc992f1a63a7ea665a3766fae6b032df3db12ef386caf0ef1f3654afedbc51c6c (LeaderClaim) | `block_root`: 0xcfbf83500e534669d039d09ec9ada459970610bb03b2ce06f944df72833c7de3 |
| `Header`:<br />- `bedrock_version`: 0x01<br />- `parent_block`: 0x1111111111111111111111111111111111111111111111111111111111111111<br />- `slot`: 0x42<br />- `block_root`: 0xcfbf83500e534669d039d09ec9ada459970610bb03b2ce06f944df72833c7de3 <br />- `leader_voucher`: 0x4444000000000000000000000000000000000000000000000000000000000000<br />- `entropy_contribution`: 0x5555000000000000000000000000000000000000000000000000000000000000<br />- `proof`: 0x2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222<br />- `leader_key`: 0x17cb79fb2b4120f2b1ec65e4198d6e08b28e813feb01e4a400839b85e18080ce | `block_id`: 0x ec351be5585023f3e96140b8903baba40028f222037b1dd12e1dbc1884788071 |