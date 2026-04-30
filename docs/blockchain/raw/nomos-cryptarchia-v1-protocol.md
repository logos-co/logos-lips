# NOMOS-CRYPTARCHIA-V1-PROTOCOL

| Field | Value |
| --- | --- |
| Name | Nomos Cryptarchia v1 Protocol Specification |
| Slug | 92 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <david@status.im> |
| Contributors | Álvaro Castro-Castilla <alvaro@status.im>, Giacomo Pasini <giacomo@status.im>, Thomas Lavaur <thomas@status.im>, Mehmet <mehmet@status.im>, Marcin Pawlowski <marcin@status.im>, Daniel Sanchez Quiros <daniel@status.im>, Youngjoon Lee <youngjoon@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-cryptarchia-v1-protocol.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-cryptarchia-v1-protocol.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

Cryptarchia is the consensus protocol of Nomos Bedrock.
This document specifies how Bedrock comes to agreement on a single history of blocks.
The values that Cryptarchia optimizes for are resilience and privacy,
which come at the cost of block times and finality.
Cryptarchia is a probabilistic consensus protocol with properties similar to
Bitcoin's Nakamoto Consensus,
dividing time into slots with a leadership lottery run at each slot.

**Keywords:** consensus, proof-of-stake, leadership lottery, fork choice,
block validation, epoch, slot, immutability

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119][rfc-2119].

## Background

### Resilience

In consensus, there is a trade-off between prioritizing either safety or liveness
in the presence of catastrophic failure (this is a re-formalization of the CAP theorem).
Choosing safety means the chain never forks,
instead the chain halts until the network heals.
On the other hand, choosing liveness (a la Bitcoin/Ethereum) means that
block production continues but finality will stall,
leading to confusion around which blocks are on the honest chain.

On the surface both options seem to provide similar guarantees.
If finality is delayed indefinitely, is this not equivalent to a halted chain?
The differences come down to how safety or liveness is implemented.

#### Prioritizing Safety

Chains that provide a safety guarantee do so using quorum-based consensus.
This requires a known set of participants (i.e. a permissioned network)
and extensive communication between them to reach agreement.
This restricts the number of participants in the network.
Furthermore, quorum based consensus can only tolerate up to 1/3rd of
the participants becoming faulty.

A small participant set and low threshold for faults generally pushes these networks
to put large barriers to entry,
either through large staking requirements or politics.

#### Prioritizing Liveness

Chains that prioritize liveness generally do so by relying on fork choice rules
such as the longest chain rule from Nakamoto consensus.
These protocols allow each participant to make a local choice
about which fork to follow,
and therefore do not require quorums and thus can be permissionless.

Additionally, due to a lack of quorums, these protocols can be quite message efficient.
Thus, participation does not need to be artificially reduced
to remain within bandwidth restrictions.

These protocols tolerate up to 1/2 of participants becoming faulty.
The large fault tolerance threshold and the large number of participants
provides for much higher resilience to corruption.

### Privacy

The motivation behind the design of Cryptarchia can be boiled down to this statement:

*A block proposer should not feel the need to self-censor when proposing a block.*

Working to give leaders confidence in this statement has had ripple effects
throughout the protocol, including that:

- **The block proposals should not be linkable to a leader**.
  An adversary should not be able to connect together
  the block proposals of a leader in order to build a profile.
  In particular, one should not be able to infer a proposer's stake
  from their past on-chain activity.
- **Cryptarchia must not reveal the stake of the leader** -
  that is, it must be a Private Proof of Stake (PPoS) protocol.
  If the activity of the leader reveals their stake values
  (e.g. through weighted voting),
  then this value can be used to reduce the anonymity set for the leader
  by bucketing the leader as high/low stake and can open him up to targeting.
- **Leaders should be protected against network triangulation attacks**.
  This is outside of the scope of this document,
  but it suffices to say that in-protocol cryptographic privacy
  is not sufficient to guarantee a leader's privacy.
  This topic is dealt with directly in Blend Network Specification.

### Limitations of Cryptarchia V1

Despite best efforts, it is not possible to provide perfect privacy and censorship resistance
to all parties. In particular:

- It is not possible to protect leaders from leaking information about themselves
  based on the contents of blocks they propose.
  The tagging attack is an example of this,
  where an adversary may distribute a transaction to only a small subset of the network.
  If the block proposal includes this transaction,
  the adversary learns that the leader was one of those nodes in that subset.
- The leader is a single point of failure (SPOF).
  Despite all the efforts to protect the leader,
  the network can be easily censored by the leader.
  The leader may choose to exclude certain types of transactions from blocks,
  leading to a worse UX for targeted parties.

These limitations are not considered insurmountable
and there are sketches towards solutions that will be developed
in following iterations of the protocol.

## Design Overview

Cryptarchia is a probabilistic consensus protocol with properties similar to
Bitcoin's Nakamoto Consensus.

At a high level, Cryptarchia divides time into slots and at each slot,
a leadership lottery is run.
To participate in the lottery, a node must have held stake in the chain
in the form of a note for a minimum time period.
Given a sufficiently aged note, you can check if it has won a slot lottery
by cryptographically flipping a weighted coin.
The weight of the coin is proportional to the value of your note,
thus higher valued notes lead to increased chances of winning.
To ensure privacy and avoid revealing the note value,
this lottery result is proven within a ZK proof system.

The design starts from the solid foundation provided by
Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake
and builds upon it, incorporating the latest research at the intersection of
cryptography, consensus and network engineering.

## Protocol

### Constants

| Symbol | Name | Description | Value |
| ------ | ---- | ----------- | ----- |
| $f$ | slot activation coefficient | The target rate of occupied slots. Not all slots contain blocks, many are empty. (See Block Times & Blend Network Analysis for analysis leading to the choice of value.) | 1/30 |
| $k$ | security parameter | Block depth finality. Blocks deeper than $k$ on any given chain are considered immutable. | 2160 blocks |
| none | slot length | The duration of a single slot. | 1 second |
| MAX_BLOCK_SIZE | max block size | The maximum size of the block body (not including the header) | 1 MB |
| MAX_BLOCK_TXS | max block transactions | The maximum number of transactions in a block | 1024 |

### Notation

| Symbol | Name | Description | Value |
| ------ | ---- | ----------- | ----- |
| $s$ | slot security parameter | Sufficient slots such that $k$ blocks have been produced with high probability. | $3\lfloor \frac{k}{f}\rfloor$ |
| $T$ | the block tree | This is the block tree observed by a node. | |
| $F_T$ | tips of block tree $T$ | The set of concurrent forks of some block tree $T$. | $F_T=\{b\in T:\forall c \in T\space \textbf{parent}(c) \neq b \}$ |
| $c_{loc}$ | tip of local chain | The chain that a node considers to be the honest chain. | $c_{loc} \in F_{T}$ |
| $B_\text{imm}$ | the latest immutable block | The latest block which was committed (finalized) by the chain maintenance. | $B_\text{imm} \in \textbf{ancestors}(c_{loc})$ |
| $sl$ | slot number | Index of slot. $sl=0$ denotes the genesis slot. | $sl=0,1,2,3,\dots$ |
| $ep$ | epoch number | Index of epoch. $ep=0$ denotes the genesis epoch. | $ep=0,1,2,3,\dots$ |

### Latest Immutable Block

The latest immutable block $B_\text{imm}$ is the most recent block
considered permanently finalized.
The blocks deeper than $B_\text{imm}$ in the local chain $c_{loc}$
are never to be reorganized.

This is maintained locally by the Chain Maintenance procedure.
When the Online fork choice rule is in use,
$B_\text{imm}$ corresponds to the $k$-deep block.
However, it may be deeper than the $k$-deep block if the fork choice rule
has been switched from Online to Bootstrap.
Unlike the $k$-deep block, $B_\text{imm}$ does not advance as new blocks are added
unless the Online fork choice rule is used.

The details of fork choice rule transitions are defined in the bootstrap spec:
[Cryptarchia v1 Bootstrapping & Synchronization][bootstrap-sync].

### Slot

Time is divided up into slots of equal length,
where one instance of the leadership lottery is held in each slot.
A slot is said to be occupied if some validator has won the leadership lottery
and proposed a block for that slot,
otherwise the slot is said to be unoccupied.

### Epoch

Cryptarchia has a few global variables that are adjusted periodically
in order for consensus to function. Namely, the protocol requires:

- Dynamic participation, thus the eligible notes must be refreshed regularly.
- An unpredictable source of randomness for the leadership lottery.
  This source of randomness is derived from in-protocol activity
  and thus must be selected carefully to avoid giving adversaries an advantage.
- Approximately constant block production rate achieved by dynamically adjusting
  the lottery difficulty based on observed participation levels.

The order in which these variables are calculated is important
and is done w.r.t. the epoch schedule.

#### Epoch Schedule

An epoch is divided into 3 phases, as outlined below.

| Epoch Phase | Phase Length | Description |
| ----------- | ------------ | ----------- |
| Stake Distribution Snapshot | $s$ slots | A snapshot of note commitments are taken at the beginning of the epoch. The protocol waits for this value to finalize before entering the next phase. |
| Buffer phase | $s$ slots | After the stake distribution is finalized, the protocol waits another slot finality period before entering the next phase. This is to further ensure that there is at least one honest leader contributing to the epoch nonce randomness. If an adversary can predict the nonce, they can grind their coin secret keys to gain an advantage. |
| Lottery Constants Finalization | $s+\lfloor\frac{k}{f}\rfloor=4\lfloor\frac{k}{f}\rfloor$ slots | On the $2s^{th}$ slot into the epoch, the epoch nonce $\eta$ and the inferred total stake $D$ can be computed. The protocol waits another $4\frac{k}{f}$ slots for these values to finalize. |

The **epoch length** is the sum of the individual phases:
$3\lfloor \frac{k}{f} \rfloor + 3\lfloor \frac{k}{f} \rfloor + 4\lfloor \frac{k}{f} \rfloor = 10 \lfloor \frac{k}{f} \rfloor$ slots.

#### Epoch State

The epoch state holds the variables derived over the course of the epoch schedule.
It is the 3-tuple $(\mathbb{C}_\text{LEAD}, \eta, D)$ described below.

| Symbol | Name | Description | Value |
| ------ | ---- | ----------- | ----- |
| $\mathbb{C}_{\text{LEAD}}$ | Eligible Leader Notes Commitment | A commitment to the set of notes eligible for leadership. | See Eligible Leader Notes |
| $\eta$ | Epoch Nonce | Randomness used in the leadership lottery (selected once per epoch) | See Epoch Nonce |
| $D$ | Inferred Total Stake (Lottery Difficulty) | Total stake inferred from watching the results of the lottery during the course of the epoch. $D$ is used as the stake relativization constant for the following epoch. | See Total Stake Inference |

### Eligible Leader Notes

A note is eligible to participate in the leadership lottery if it has not been spent
and was a member of the note set at the beginning of the previous epoch,
i.e. they are members of $\mathbb{C}_\text{LEAD}$.

#### Note Ageing

If an adversary knows the epoch nonce $\eta$,
they may grind a note that wins the lottery more frequently
than should be statistically expected.
Thus, it's critical that notes participating in the lottery are sufficiently old
to ensure that they have no predictive power over $\eta$.

### Epoch Nonce

The epoch nonce $\eta$ is evolved after each block.

Given block $B = (parent, sl, \rho_\text{LEAD}, \dots)$ where:

- $parent$ is the parent of block $B$
- $sl$ is the slot that $B$ is occupying.
- $\rho_\text{LEAD}$ is the epoch nonce entropy contribution
  from the block's leadership proof

Then, $\eta_B$ is derived as:

$$\eta_{B} = \text{zkHASH}(\text{EPOCH\_NONCE\_V1}||\eta_{\text{parent}}||\rho_\text{LEAD}||\text{Fr}(sl))$$

where $\text{Fr}(sl)$ maps the slot number to the corresponding scalar
in Poseidon's scalar field and $\text{zkHASH}(..)$ is Poseidon2
as specified in Common Cryptographic Components.

The epoch nonce used in the next epoch is $\eta_{B'}$
where $B'$ is the last block before the start of the
"Lottery Constants Finalization" phase in the epoch schedule.

### Total Stake Inference

Given that stake is private in Cryptarchia,
and that the goal is to maintain an approximately constant block rate,
the difficulty of the slot lottery must be adjusted
based on the level of participation.
The details can be found in the Total Stake Inference specification.

### Epoch State Pseudocode

At the start of each epoch, each validator must derive the new epoch state variables.
This is done through the following protocol:

```text
define compute_epoch_state(ep, tip ∈ T) → (C_LEAD^ep, η^ep, D^ep):

case ep = 0:
    The genesis epoch state is hardcoded upon chain initialization.
    return (C_GENESIS, η_GENESIS, D_GENESIS)

otherwise:
    The epoch state is derived w.r.t. observations in the previous epoch.
    First, compute the slot at the start of the previous epoch.
    Observations will be queried relative to this slot.

    sl_{ep-1} := (ep-1) · EPOCH_LENGTH

    Notes eligible for leadership lottery are those present in the
    commitment root at the start of the previous epoch.

    C_LEAD^ep := commitment_root_at_slot(sl_{ep-1}, tip)

    The epoch nonce for epoch ep is the value of η at the beginning
    of the lottery constants finalization phase in the epoch schedule

    η^ep := epoch_nonce_at_slot(sl_{ep-1} + ⌊6k/f⌋, tip)

    Total active stake is inferred from the number of blocks produced
    in the previous epoch during the stake freezing phase.
    It is also derived from the previous estimate of total stake,
    thus recursion is used here to retrieve the previous epochs estimate D^{ep-1}

    (_, _, D^{ep-1}) := compute_epoch_state(ep-1, tip)

    The number of blocks produced during the first 6k/f slots
    of the previous epoch

    N_BLOCKS^{ep-1} := |{B ∈ T | sl_{ep-1} ≤ sl_B < sl_{ep-1} + ⌊6k/f⌋}|

    D^ep := infer_total_active_stake(D^{ep-1}, N_BLOCKS^{ep-1})

    return (C_LEAD^ep, η^ep, D^ep)
```

## Leadership Lottery

A lottery is run for every slot to decide who is eligible to propose a block.
For each slot, there can be 0 or more winners.
In fact, it's desirable to have short slots and many empty slots
to allow for the network to propagate blocks
and to reduce the chances of two leaders winning the same slot
which are guaranteed forks.

### Proof of Leadership

The specifications of how a leader can prove that they have won the lottery
are specified in the Proof of Leadership Specification.

### Leader Rewards

As an incentive for producing blocks,
leaders are rewarded with every block proposal.
The rewarding protocol is specified in Anonymous Leaders Reward Protocol.

## Block Chain

### Fork Choice Rule

Two fork choice rules are used,
one during bootstrapping and a second once a node completes bootstrapping.

During bootstrapping, the protocol must be resilient to malicious peers feeding false chains,
this calls for a more expensive fork choice rule that can differentiate
between malicious long-range attacks and honest chains.

After bootstrapping, the node commits to the most honest looking chain found
and switches to a fork choice rule that rejects chains that diverge
by more than $k$ blocks.

The details are specified in Cryptarchia Fork Choice Rule.

### Block ID

Block ID is defined by the hash of the block header,
where hash is Blake2b as specified in Common Cryptographic Components.

```python
def block_id(header: Header) -> hash:
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
class Header:                                    # 297 bytes
    bedrock_version: byte                        # 1 byte
    parent_block: hash                           # 32 bytes
    slot: int                                    # 8 bytes
    block_root: hash                             # 32 bytes
    proof_of_leadership: ProofOfLeadership       # 224 bytes

class ProofOfLeadership:                         # 224 bytes
    leader_voucher: zkhash                       # 32 bytes
    entropy_contribution: zkhash                 # 32 bytes
    proof: Groth16Proof                          # 128 bytes
    leader_key: Ed25519PublicKey                 # 32 bytes
```

### Block

Block construction, validation and execution are specified in
Block Construction, Validation and Execution Specification.

### Block Header Validation

Given block $B=(header, transactions)$ and the block tree $T$ where:

- $header$ is the header defined in Header
- $transactions$ is the sequence of transactions in the block

The function $\textbf{valid\_header}(B)$ returns True
if all of the following constraints hold,
otherwise it returns False.

1. `header.version.bedrock_version = 1`
   Ensure bedrock version number.

2. `bytes(transactions) < MAX_BLOCK_SIZE`
   Ensure block size is smaller than the maximum allowed block size.

3. `length(transactions) < MAX_BLOCK_TXS`
   Ensure the number of transactions in the block is below the limit.

4. `merkle_root(transactions) = header.block_root`
   Ensure block root is over the transaction list.

5. `header.slot > fetch_header(header.parent_block).slot`
   Ensure the block's slot comes after the parent block's slot.

6. `wallclock_time() > slot_time(header.slot)`
   Ensure this block's slot time has elapsed.
   Local time is used in this validation.
   See Clocks for discussion around clock synchronization.

7. `header.parent ∈ T`
   Ensure the block's parent has already been accepted into the block tree.

8. `height(B) > height(B_imm)`
   Ensure the block comes after the latest immutable block.
   Assuming that $T$ prunes all forks diverged deeper than $B_\text{imm}$,
   this step, along with step 5, ensures that $B$ is descendant from $B_\text{imm}$.
   If all forks cannot be pruned completely in the implementation,
   this step must be replaced with `is_ancestor(B_imm, B)`,
   which checks whether $B_\text{imm}$ is an ancestor of $B$.

9. Verify the leader's right to propose
   and ensure it is the one proposing this block:
   Given leadership proof $\pi_\text{LEAD} = (\pi_\text{PoL}, P_\text{LEAD}, \sigma)$,
   where:
   - $\pi_\text{PoL}$ is the slot lottery win proof
     as defined in Proof of Leadership Specification
   - $P_\text{LEAD}$ is the public key committed to in $\pi_\text{PoL}$
   - $\sigma$ is a signature

10. A leader's proposal is valid if:
    - `verify_PoL(T, parent, sl, P_LEAD, π_PoL) = True`
    - `verify_signature(block_id(H), σ, P_LEAD) = True`
    Ensure that the leader who won the lottery is actually proposing this block
    since PoL's are not bound to blocks directly.

### Chain Maintenance

The chain maintenance procedure `on_block(state, B)`
governs how the block tree $T$ is updated.

**Note:** It's assumed that block contents have already been validated
by the execution layer w.r.t. the parent block's execution state.

```text
define on_block(state, B) → state':

(c_loc, B_imm, T) := state

if B ∈ T ∨ ¬valid_header(B):
    Either B has already been seen or it's invalid, in both cases the block is ignored
    return state

T' := T ∪ {B}

c_loc' := B                              if parent(B) = c_loc
          fork_choice(c_loc, F_T', k, s)  if parent(B) ≠ c_loc

if fork_choice_rule = ONLINE:
    Explicitly commit to the k-deep block
    if the Online Fork Choice Rule is being used.
    (T', B_imm) := commit(T', c_loc', k)

return (c_loc', B_imm, T')
```

### Commit

The following procedure commits to the block
which is $depth$ deep from $c_{loc}$.
This procedure computes the new latest immutable block $B_\text{imm}$.

```text
define commit(T, c_loc, depth) → (T', B_imm):

assert fork_choice_rule = ONLINE

Compute the latest immutable block, which is depth deep from c_loc.
B_imm := block_at_depth(c_loc, depth)

Prune all forks diverged deeper than B_imm,
so that future blocks on those forks can be rejected by Block Header Validation.
T' := prune_forks(T, B_imm, c_loc)

return (T', B_imm)
```

### Fork Pruning

The fork pruning procedure removes all blocks
which are part of forks diverged deeper than a certain block.

```text
define prune_forks(T, B) → T':

T' := T

for each B_tip ∈ F_T:
    If B_tip is a fork diverged deeper than B, prune the fork.
    B_div := common_ancestor(B_tip, B)
    if B_div ≠ B:
        T' := prune_blocks(B_tip, B_div, T)

return T'

define prune_blocks(B_new, B_old, T) → T':

Remove all blocks in the chain within range (B_old, B_new] from T.
(B, T') := (B_new, T)

while B ≠ B_old:
    T' := T' \ {B}
    B := parent(B)

return T'
```

### Versioning and Protocol Upgrades

Protocol versions are signalled through the `bedrock_version` field
of the block header.
Protocol upgrades need to be co-ordinated well in advance
to ensure that node operators have enough time to update their node.
Block height is used to schedule the activation of protocol updates.
E.g. bedrock version 35 will be active after block height 32000.

## Implementation Considerations

### Proof of Stake vs. Proof of Work

From a privacy and resiliency point of view, Proof of Work is highly attractive.
The amount of hashing power of a node is private,
they can provide a new public key for each block they mine
ensuring that their blocks cannot be connected by this identity,
and PoW is not susceptible to long range attacks as is PoS.
Unfortunately, it is wasteful and demands that leaders have powerful machines.
The goal is to ensure strong decentralization by having a low barrier to entry
and a good enough level of security can be achieved
by having participants have an economic stake in the protocol.

### Clocks

Cryptarchia depends on honest nodes having relatively in-sync clocks.
The protocol currently relies on NTP to synchronize clocks,
this may be improved upon in the future,
borrowing ideas from Ouroboros Chronos: Permissionless Clock Synchronization
via Proof-of-Stake.

## References

### Normative

- [Proof of Leadership Specification][proof-of-leadership]
  \- ZK proof specification for leadership lottery
- [Anonymous Leaders Reward Protocol][leaders-reward]
  \- Leader reward mechanism
- [Cryptarchia Fork Choice Rule][fork-choice]
  \- Fork choice rule specification
- [Block Construction, Validation and Execution Specification][block-construction]
  \- Block structure details
- [Common Cryptographic Components][crypto-components]
  \- Cryptographic primitives (Blake2b, Poseidon2)
- [Cryptarchia v1 Bootstrapping & Synchronization][bootstrap-sync]
  \- Bootstrap and synchronization procedures
- [Total Stake Inference][stake-inference]
  \- Stake inference mechanism
- [Block Times & Blend Network Analysis][block-times]
  \- Analysis for slot activation coefficient

### Informative

- [Cryptarchia v1 Protocol Specification][cryptarchia-origin]
  \- Original Cryptarchia v1 Protocol documentation
- [Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake][ouroboros-crypsinous]
  \- Foundation for Cryptarchia design
- [Ouroboros Chronos: Permissionless Clock Synchronization via Proof-of-Stake][ouroboros-chronos]
  \- Clock synchronization research
- [Blend Network Specification][blend-network]
  \- Network privacy layer

[proof-of-leadership]: https://nomos-tech.notion.site/Proof-of-Leadership-215261aa09df8145a0f2c0d059aed59c
[leaders-reward]: https://nomos-tech.notion.site/Anonymous-Leaders-Reward-Protocol
[fork-choice]: https://nomos-tech.notion.site/Cryptarchia-Fork-Choice-Rule
[block-construction]: https://nomos-tech.notion.site/Block-Construction-Validation-and-Execution-Specification
[crypto-components]: https://nomos-tech.notion.site/Common-Cryptographic-Components
[bootstrap-sync]: https://nomos-tech.notion.site/Cryptarchia-v1-Bootstrapping-Synchronization
[stake-inference]: https://nomos-tech.notion.site/Total-Stake-Inference
[block-times]: https://nomos-tech.notion.site/Block-Times-Blend-Network-Analysis
[cryptarchia-origin]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification-21c261aa09df810cb85eff1c76e5798c
[ouroboros-crypsinous]: https://eprint.iacr.org/2018/1132.pdf
[ouroboros-chronos]: https://eprint.iacr.org/2019/838.pdf
[blend-network]: https://nomos-tech.notion.site/Blend-Protocol-215261aa09df81ae8857d71066a80084
[rfc-2119]: https://www.ietf.org/rfc/rfc2119.txt

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
