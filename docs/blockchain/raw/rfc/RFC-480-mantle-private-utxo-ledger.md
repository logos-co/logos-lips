# [RFC] Mantle: Private UTXO ledger

**Motivation and proposal:** [PR #480](https://github.com/logos-co/logos-lips/pull/480)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-07 |
| v2 | Notes live in note sets: a ledger, an SDP and one per channel, each with its commitment MMR and nullifier IMT, committed together in the eligible root of the Proof of Leadership. Channel notes are moved by the steps their holders sign, published by `CHANNEL_INSCRIBE`, and withdrawn by their holders. Removed the transparent channel and service notes, the transparent eligible set and the `is_shielded` selector, `CHANNEL_TRANSFER` and the channel `transfer_threshold`. `SDP_WITHDRAW` consumes the service note with a ZkTransfer | 2026-10-07 |
| v3 | The spending, adding and transfer verification functions are methods of `NoteSet`. The recent commitment roots of a set keep their MMR peaks, to which `verify_transfer` appends the buffer of the Mantle Transaction. Two steps of an inscription cannot consume the same note | 2026-10-08 |
| v4 | Operations append their outputs to the commitment buffer when validated, and a step can consume the outputs of an earlier step of its inscription. A channel withdrawal consumes its inputs at its due slot, only if they are still unspent, so a valid step cancels it. The withdrawal of a service note is proven against the root of an MMR holding only that note. The PoW ticket hashes the public key first | 2026-10-09 |
| v5 | The ZkTransfer public root is `tx_cm_root`, the referenced recent `cm_merkle_root` extended with the buffer of its set | 2026-10-12 |
| v6 | A channel step names the commitments of the transaction buffer its proof covers, so that steps proven against the same recent root hold at any position. Channel withdrawals carry no fee. Each note set records its root at the end of every block. The ZkTransfer of the Genesis declarations is verified, and withdrawn declarations are released in a fixed order. The block reward keeps the 120-block average of the pooled fees, with the reserve, the pool and the pending Blend share as integer consensus state. Merkle paths are read from the leaf level up. The Proof of Leadership is bound to its block by a hash of the header, which removes the `leader_key` header field, the proposal and block signatures and the signatures of the uncle headers, and the block ID hashes the header without its proof. The cross-channel messaging template is deprecated | 2026-10-15 |
| v7 | The null channel has no note set. The operation payloads name a recent root only, the buffer being appended in validation. Channel steps can be grouped in mini-blocks sharing their `buffered`, and the withdrawal is the forced exit and the optimistic settlement of double signing. The block rewards state that the leader is paid in its block and that the maximum supply is fixed at genesis, and the execution market why base fees are pooled | 2026-10-16 |
| v8 | A `TokenValue` counts units of $`10^{-9}`$ LGO, in which the integer block reward is expressed. The Execution Gas of each Operation is summed against the state it is validated against. Ed25519 signatures sign the `mantle_txhash` digest and the proofs take it reduced modulo $`p`$. A `FieldElement` not less than $`p`$ is rejected. A channel with an infinite posting timeframe keeps its sequencer. The commitment MMR and the nullifier IMT have depth 40, a note set then taking about 50 years of transfers at the Execution Gas target to fill instead of 72 days at depth 32, and of any two identical notes only one can be spent. The eligible tree has depth 40, since channel creations, which cost no Execution Gas, would fill a tree of depth 32 in about 79 days of full blocks. The Proof of Leadership error table is computed for $`f = 1/30`$ | 2026-10-19 |
| v9 | No proof of the Genesis transaction is verified. The proof of work share of the fees waits in `pow_rewards_pending` until the epoch boundary. Mantle defines `path_root`, the root of a Merkle path, the ZkTransfer, PoL and PoQ check that every path selector is a bit, and the eligible root uses the commitment MMR functions. The nullifier IMT keeps its leaves, a full note set rejects new commitments and nullifiers, and the indexes of a multi-signature are bounded by the keys. The leader reward reads the release and payout of the block update. The limits of channel re-inclusion after a reorg, of the forced exit fee, of leader reward privacy and of wallet tracking are stated. Storage Markets and the initial base fee keep their master values. The Execution Market and overview figures are redrawn | 2026-10-30 |
| v10 | The specifications no longer reference deprecated documents, and historical documents are left as they are | 2026-11-02 |
| v11 | Follows the SDP rules of master: `declaration_id = Hash(service \|\| zk_id)`, one map of declarations and of providers per service, a `nonce` carrying the `created` epoch of its declaration, one `MinStake`. Each declaration keeps creating its own service note, so the `service_notes` map is not kept. Revisions renumbered past master's | 2026-11-03 |
| v12 | Builds on #503: every amount counts LEPTA, the token is LOGOS, the Block Rewards reference types its constants as 128-bit integers, and the revisions of Block Rewards, the Cryptoeconomics Overview and Total Stake Inference are renumbered past its own. The `zk_id` is a unique one-time random key, which the declaration does not prove | 2026-11-03 |
| v13 | The Proof of Quota leader branch proves the note unspent at the freeze of the stake distribution. Genesis declarations consume no note, and Genesis checks the supply. A block above $`G_\text{max}`$ is invalid, and a proposal confirms its body root before verifying its uncles. A note set records its root only when a block appends to it, and every block records the eligible root. The Blend shares of the closed and of the current epoch are kept apart, what an epoch does not distribute returning to the reserve. `step_msg` hashes the channel, and the claim ticket has a DST | 2026-11-03 |
| v14 | An inscription is a list of mini-blocks of steps, each step proven against its recent root and the buffer before its mini-block, in place of a `buffered` count on each step | 2026-11-04 |

## Reviewer Orientation

Read the PR's Motivation first. The note sets in Mantle are the base every other document builds on.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [note sets](#1-note-sets) | one commitment MMR and nullifier IMT per set; the 1024-block root window and the commitment buffer per set |
| 2 | Critical | [Mantle](#affected-specifications), [channel Operations](#2-channel-notes-moved-by-their-holders) | steps bound to `step_msg` and verified on chain; holder withdrawals with `WITHDRAW_DELAY` |
| 3 | Critical | **Start here**: [Proof of Leadership](#affected-specifications), [eligible root](#3-proof-of-leadership-over-the-eligible-root) | the eligible tree over the sets; the same set position for the aged and latest checks |
| 4 | High | [Mantle](#affected-specifications), [SDP and proof of work](#4-sdp-stake-and-the-proof-of-work-claim) | the SDP note set; the single-note MMR root binding the withdrawal to its service note; the unsigned PoW claim |
| 5 | High | [Block Construction](#affected-specifications), [leader reward and block execution](#5-leader-reward-paid-in-the-block) | `reward_key`, the reward note, the release of due withdrawals |
| 6 | High | [Block Rewards](#affected-specifications), [Cryptoeconomics overview](#affected-specifications), [block reward state](#6-block-reward-state-and-supply-projection) | the integer reference over the 120-block window, the reserve, the pool, the closed and pending Blend shares and the pending proof of work share, the 40% leader share plus tips |
| 7 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#7-encoding) | steps in `ChannelInscribe`, new payloads and proof variants |
| 8 | High | [Cryptarchia](#affected-specifications), [Proof of Quota](#affected-specifications), [Message Encapsulation](#affected-specifications), [consensus inputs](#8-cryptarchia-and-proof-of-quota-inputs) | epoch state and uncle inputs, PoQ leader branch |
| 9 | High | [Genesis Block](#affected-specifications), [genesis](#9-genesis) | the initial sets; the distribution inscription; declarations consuming no note; the supply check |
| 10 | Medium | [Service Declaration Protocol](#affected-specifications), [Service Reward Distribution](#affected-specifications), [Proof of Work](#affected-specifications), [Gas Cost Determination](#affected-specifications) | follow-on changes of items 2 and 4 |
| 11 | Medium | [Wallet Technical Standard](#affected-specifications), [note tracking](#10-wallet-note-tracking) | per-set tracking; MMR and IMT path updates |
| 12 | Medium | [Gas Cost Determination](#affected-specifications), [Execution Market](#affected-specifications), [Cryptoeconomics overview](#affected-specifications), [Execution Gas limit](#chores) | the ZkTransfer priced from the measured batch verification; $`G_\text{max}`$ from 3,193,460 to 3,196,459, $`G_\text{target}`$ to 1,598,229, and the base-fee constants |
| 13 | Low | the remaining documents in [Chores](#chores) | skim |

# Discussion

## One note set per partition

Every note is private and lives in exactly one note set: the ledger, the SDP, or a channel. A set has its own commitment MMR and nullifier IMT, so an Operation only ever touches the sets it names: a Transfer the ledger set, a step its channel's set, a withdrawal its channel's set and then the ledger set. The Proof of Leadership covers every set through one eligible root, and a note's kind no longer changes how it proves itself. This is what removes the transparent channel and service notes, the transparent eligible set and the selector of the Proof of Leadership.

## Channel notes: moved by holders, ordered by sequencers

A channel note is spent only by its holder. Inside the channel, the holder signs a step, a ZkTransfer bound to `step_msg` rather than to the transaction, since it is signed before the transaction exists. The sequencers collect the steps and publish them in their inscriptions, and the ledger verifies every step. A sequencer orders the moves of its channel and can delay or drop a step, but cannot move a note, and cannot create value: every step is a verified, balanced ZkTransfer. An inscription is a list of mini-blocks of steps: every step of a mini-block is verified against its referenced root extended with the buffer as it stands when the mini-block starts, what the earlier Operations of the transaction and the earlier mini-blocks added. The holders prove their steps independently, before the sequencer assembles the transaction, and the steps of a mini-block are ordered freely among themselves, so a sequencer can collect the steps of many users and order them as it chooses. Extending every proof with the whole buffer would tie each proof to one position, and holders would have to prove one after another once the sequencer had fixed everything before them. A per-step count of covered commitments was also considered: it lets a step cover less than the previous mini-blocks, but a mini-block is simpler to reason about, and a step covering all of them points less at the notes it consumes.

Out of the channel, the holder withdraws alone. The withdrawal is the forced exit of a holder whose steps the sequencers do not publish, and it settles double signing optimistically: a holder signing both a step and a withdrawal of the same notes loses the withdrawal, and the fees it paid for it, if the step lands first. The withdrawal takes effect `WITHDRAW_DELAY` slots later, only if its notes are still unspent: until then, an inscription can consume them with a valid step, which cancels it. A holder cannot invalidate an inscription carrying one of its steps by withdrawing the same note, as long as the inscription lands before the withdrawal is due; a sequencer should not accept a step whose inputs a pending withdrawal may release before then, since the due slots and nullifiers are public. The withdrawal carries no fee: another Operation of its transaction pays it, since a fee paid at posting would stay paid if the withdrawal were dropped, and would create tokens. A holder whose funds are all in channels therefore needs a ledger note, of its own or added by a third party, to post its withdrawal.

All the data of a step lands on chain: its nullifiers, its commitments and its proof. Steps are not compressed, so a channel costs the chain as much per move as the ledger does. Steps carry no `excess_value`, so a move inside a channel pays no fee from channel funds, and the fee of the inscription comes from its sequencer. We plan later to add compression in order to bring scalability to layers 2.

## Root window and commitment buffer

A ZkTransfer proves its inputs against a commitment root of their set from one of the last 1024 blocks, except for `SDP_WITHDRAW`, whose root holds only the service note of its declaration. A wallet can therefore build its proof against a root a few blocks old and still be included. A note set records its root only when a block appends to it, so the work of a block follows the sets it changes and not the channels ever created, and each recent root keeps the last block it was current, which keeps the window at 1024 blocks whatever the activity of the set. Inside a Mantle Transaction, the commitments created by earlier Operations go into the buffer of their set, and a proof is verified against its referenced root with that buffer appended, or for a channel step only the part of it the step names. A note created in a block can be spent from the next block on, or later in the same transaction.

## SDP stake

The service note is created by the ledger in the SDP set, so it stakes like any note. Its withdrawal is proven against the root of an MMR holding only the declaration's service note, which ties the consumed nullifier to that note without exposing it in the circuit. The outputs reach the ledger set when the declaration is removed, and the stake leaves Proof of Stake when the withdrawal is included.

The `zk_id` is a unique one-time random key, so `SDP_DECLARE` does not prove it: its proofs cover the inputs and the `provider_id`. A declaration naming a `zk_id` it does not hold locks its stake for good, since consuming the service note takes both the `zk_id` secret and the `provider_id` signature, and cannot serve, since the Proof of Quota takes the secret.

## Leader reward in the block

The reward note of a block carries the block's own value and still does not link the leader to its spending: the spend reveals a nullifier and no commitment. The voucher set, the pooled leader reward and `LEADER_CLAIM` are retired. The block reward keeps averaging the pooled fees over the last 120 blocks, so a leader can barely steer its own reward with the fees it pays in its block. The reward note has nonce `0`, so two rewards of the same value under one `reward_key` are identical notes and, as for any two identical notes, only one can be spent: a leader should use a fresh key per block. Every reward value is public and an `SDP_DECLARE` publishes the amount it stakes, so staking reward notes can link the blocks they were won in to the declaration.

## Proof of Leadership on the proposal path

The Proof of Leadership is bound to the header, so it is proven once the body is fixed, and its proving time adds to the latency of the proposal. On the 2-core, 2 GHz minimum specification it takes roughly 2 s, scaled by clock speed from the benchmarks of the stacked PR #481. With a fork chance per block of $`1 - (29/30)^\Delta`$, this raises $`\Delta`$ from the 6 s of a 1 s proof to 7 s, and the chance from 18.4% to 21.1%.

## Proof of Quota at the freeze

Commitments are never removed from a note set, so membership in the commitment MMR does not show that a note was unspent. The leader branch of the Proof of Quota therefore proves that the nullifier of the note is absent from the nullifier IMT of its set when the stake distribution was frozen. Without it, a holder re-creating its note with self-transfers before the freeze would get the leader quota of every copy. The proof can still be made in advance, since that IMT is fixed for the epoch.

## Execution Gas limit

The sum of the Execution Gas of the transactions of a block is a validity rule. The per-Operation prices bound what a transaction pays, not the work a leader puts in its own block, and the base fee update holds its step only while a block stays within $`G_\text{max}`$.

## Open questions for reviewers

- How a wallet learns the value and nonce of a note it receives through a Transfer or a step is out of scope. Only commitments are on chain. This will be addressed by Mehmet in a different and stacked PR for viewing keys.
- The 10-year supply projection in Block Rewards follows the behavioral assumptions of the earlier baseline simulation, which were not published as code. Its fee and stake model should be checked against that reference.

# Details

## 1. Note sets

A note is `(value, nonce, public_key)`, stored as its commitment `derive_note_cm(note)`. Each note set keeps the commitments of its notes in an MMR and the nullifiers `derive_note_nf(cm, sk)` of its spent notes in an IMT.

```python
LEDGER_SET = 0
SDP_SET = 1

class NoteSet:
    commitments: list[(MerkleRoot, int)]  # the peaks of the commitment MMR, with their heights
    nullifiers: set[NoteNf]               # the set of nullifiers, holding the 0 of the sentinel leaf
    nullifier_leaves: list[NullifierLeaf] # the leaves of the nullifier IMT, in insertion order
    current_cm_root: MerkleRoot           # the commitment MMR root at the end of the previous block
    recent_cm_roots: dict[MerkleRoot, RecentRoot]  # the current root and the roots of the last 1024 blocks
    tx_cm_buffer: list[NoteCm]          # commitments added earlier in the Mantle Transaction

class RecentRoot:
    peaks: list[(MerkleRoot, int)]  # the peaks of the commitment MMR at this root
    last_block: int | None          # the last block at whose end this was the root, None if current

class Ledger:
    sets: list[NoteSet]                              # ledger, SDP, then one per channel by creation,
                                                     # none for the null channel
    pending_withdrawals: list[(Slot, int, list[NoteNf], list[NoteCm])]
```

- A channel gets the next note set when it is created, stored as `ChannelState.note_set`. The null channel, which only receives the Genesis inscriptions, gets none, and no deposit, withdrawal or step can target it.
- The commitment MMR root is the root of the depth-40 Merkle tree whose leaves are the commitments in insertion order, empty leaves holding `0`. The ledger keeps its peaks: `mmr_append` adds a commitment, and `mmr_root` computes the root from the peaks.
- The nullifier IMT has depth 40 and appends leaves in insertion order. At depth 32 a set would fill in about 72 days of transfers of 8 outputs at the Execution Gas target, and in about 50 years at depth 40, for 243 constraints per extra level and no change to the verification gas. A leaf is `NullifierLeaf(nf, next_nf, next_index)`, hashed with the DST `NULLIFIER_IMT_LEAF_V1`. The first leaf is the sentinel `(0, 0, 0)`, and positions past the last leaf hold `0`.
- `assert_spendable(inputs, cm_merkle_root)`, `verify_transfer(...)`, `execute_spending(inputs)` and `execute_adding(outputs)` are methods of `NoteSet`, called as `ledger.sets[LEDGER_SET].execute_adding(...)`.
- An Operation references a recent `cm_merkle_root`, and its ZkTransfer is proven against `tx_cm_root`, that root with the set's buffer appended, or only the commitments before its mini-block for a channel step (§2). `verify_transfer` computes `tx_cm_root` and calls `ZkTransfer_verify(...)`. `SDP_WITHDRAW` references no root and calls `ZkTransfer_verify(...)` directly (§4).
- The ZkTransfer has 4 inputs and 8 outputs, marked used by the public flags `inputs_active` and `outputs_active`. The verifier sets the flags from the lengths of `inputs` and `outputs`, and an Operation with more than 4 inputs or 8 outputs is invalid. The circuit checks each flag is boolean, and an inactive input or output holds value `0`.
- The `excess_value` of `TRANSFER`, `CHANNEL_DEPOSIT` and `SDP_WITHDRAW` adds to the transaction balance. Steps and withdrawals carry none, and the excess of `SDP_DECLARE` is its stake.
- `derive_note_nonce(op_id, output_number, value, public_key)` uses the DST `NOTE_NONCE_V1`.
- A Merkle path lists its nodes and its selectors from the leaf level up, a selector being the bit of the leaf index at its level, `1` when the path node is on the left. The circuits follow this convention, the core branch of the Proof of Quota included.
- Mantle is revision 2.0.0.

## 2. Channel notes moved by their holders

```python
class ChannelStep:
    inputs: list[NoteNf]
    outputs: list[NoteCm]
    cm_merkle_root: MerkleRoot  # a recent root of the channel note set

class Inscribe:
    # ... channel, inscription, parent, signer unchanged
    mini_blocks: list[list[ChannelStep]]  # new
```

- Each step carries a ZkTransfer with `msg = step_msg(channel, step)`, a hash of its channel, nullifiers and commitments under the DST `CHANNEL_STEP_V1`, and `excess_value = 0`. Its public root is `cm_merkle_root` extended with the buffer of the channel set as it stands when the mini-block of the step starts. The `ChannelInscribeOpProof` holds the signer's Ed25519 signature and one ZkTransfer per step.
- The steps are validated against the state the inscription is validated against, then applied in order to the channel note set. A channel being created carries no step.
- `CHANNEL_DEPOSIT` consumes ledger notes and creates channel notes, `outputs` being commitments. Its `excess_value` pays fees.
- `CHANNEL_WITHDRAW` is posted by the holder with a ZkTransfer of `excess_value = 0`: another Operation of the Mantle Transaction pays its fees, since an excess paid at posting would stay paid if the withdrawal is dropped. At the first block whose slot reaches `WITHDRAW_DELAY = 86,400` slots after it, its inputs are consumed and its `outputs` created in the ledger set if the inputs are still unspent; otherwise it is dropped.
- `CHANNEL_TRANSFER`, opcode `0x14`, and the channel `transfer_threshold` are removed.
- Execution Gas: `EXECUTION_CHANNEL_INSCRIBE_GAS + EXECUTION_TRANSFER_GAS * len(steps)`, `EXECUTION_CHANNEL_WITHDRAW_GAS = 619`.

## 3. Proof of Leadership over the eligible root

The eligible root is a Merkle tree of depth 40 whose leaf `i` is `zkhash(ELIGIBLE_SET_LEAF_V1, cm_root_i, nf_root_i)` for note set `i`, positions past the last set holding `0`. Every channel adds a note set, and a `CHANNEL_CONFIG` creating a channel costs no Execution Gas, only its 111 bytes of storage: a 2 MiB block holds about 18,900 of them, so blocks full of channel creations would fill a tree of depth 32 in about 79 days, and one of depth 40 in about 55 years.

```python
class ProofOfLeadershipPublic:
    # ... slot, epoch_nonce, t0, t1 unchanged
    eligible_aged: MerkleRoot       # new
    eligible_latest: MerkleRoot     # new
    msg: zkhash                     # new, replaces leader_pk
    entropy_contribution: zkhash
```

- The aged check proves `cm` in the commitment MMR of its set, and the leaf of that set, with the set's aged nullifier root, under `eligible_aged`.
- The latest check proves `nf` absent from the IMT of the same set: a leaf `low` with `low.nf < nf` and `nf < low.next_nf` or `low.next_nf == 0`, and the leaf of the set, with its latest commitment root, under `eligible_latest`.
- Both leaf paths use the same `set_selectors`, so both checks name the same set.
- The lottery ticket and the entropy contribution use the commitment `cm`. The PoL is revision 1.2.0.
- The PoL is bound to its block by `msg = pol_msg(header)`, a Blake2b hash under the DST `POL_MSG_V1` of every header field except the proof and the entropy contribution, reduced modulo `p`. The leader proves it once `body_root` is fixed. The `leader_key` header field, the proposal and block signatures and the signatures of the uncle headers are removed: an uncle entry is a 265-byte header, and the proposal is at most 17,712 bytes, which `Max_Body_Length` follows. The block ID hashes the header without its proof: a Groth16 proof can be re-randomized, so including it would give one block several IDs. An invalid proof of leadership therefore condemns only the received copy, not the block ID.

## 4. SDP stake and the proof of work claim

- `SDP_DECLARE` consumes ledger notes with a ZkTransfer and appends the service note `Note(amount, derive_note_nonce(op_id, 0, amount, zk_id), zk_id)` to the SDP set. `DeclarationInfo` holds `service_note` and `withdraw_outputs`.
- `SDP_WITHDRAW` carries `service_note_nf`, `outputs` and `excess_value`, with a ZkTransfer proven against `mmr_root([(declare_info.service_note, 0)])` and the `provider_id`'s Ed25519 signature. Its outputs reach the ledger set at removal.
- `SDP_ACTIVE` is signed by the `provider_id`.
- The identifiers and nonces of the Service Declaration Protocol apply as they are, with `declaration_id = Hash(service || zk_id)`, `declarations` and `providers` per service, and a `nonce` carrying the `created` epoch of its declaration. Each declaration creates its own service note, so no `service_notes` map is needed.
- `CLAIM_POW_REWARD` moves to opcode `0x30`, freed by `LEADER_CLAIM`, gains a `nonce`, its ticket is `zkhash(POW_CLAIM_V1, public_key, nonce, block_hash, epoch_nonce)`, its proof is empty, and its reward note goes to the ledger set.
- Execution Gas: `EXECUTION_SDP_WITHDRAW_GAS = 678`, `EXECUTION_SDP_ACTIVE_GAS = 59`, `EXECUTION_CLAIM_POW_REWARD_GAS = 0`.

## 5. Leader reward paid in the block

```diff
 class ProofOfLeadership:
     # ... proof, entropy_contribution unchanged
-    leader_key: Ed25519PublicKey
-    leader_voucher: RewardVoucher
+    reward_key: ZkPublicKey
```

Block Execution runs the service rewards and releases the stake of the withdrawn declarations, releases the due channel withdrawals, runs the transactions, then updates the fee window, the reserve, the pool and the pending Blend and proof of work shares and appends the leader reward note `Note(get_leader_reward(block), 0, reward_key)` to the ledger set, and finally records the commitment MMR root of every note set the block appended to, forgetting the roots that have left the 1024-block window, and the eligible root, which validating an uncle or a fork block reads. A leader should use a fresh `reward_key` for every block. Block Proposal Validation confirms the body root before verifying the uncles, a copy with substituted uncle entries then costing one Groth16 verification, so an invalid uncle entry condemns the block. It also rejects a block whose transactions sum to more than $`G_\text{max}`$ Execution Gas. Block Construction is revision 1.4.0. The [Anonymous Leaders Reward](../../deprecated/bedrock-anonymous-leaders-reward.md) specification is deprecated.

## 6. Block reward state and supply projection

The block reward stays `R_t = A_t * I_max * S_cap * Delta_t + (1 - A_t) * R_bar_t`, where `R_bar_t` is the average of the pooled fees over the last 120 blocks. The integer reference now follows that equation, with `FEE_AVG_NUMERATOR = 10_512` over the sum of the window and 128-bit intermediates, and caps the release at the reserve balance. It counts LEPTA, as `TokenValue` does, so `STAKE_TARGET = 3 * 10**18`, `A_SCALE = 12 * 10**16` and `RELEASE_NUMERATOR = 62_500 * 10**9`. The reserve `rewards_reserve`, the pool `rewards_pool`, the Blend shares `blend_rewards_closed` and `blend_rewards_pending`, the pending proof of work share `pow_rewards_pending` and the fee window are integer consensus state, set at Genesis: the block reward is the floored reserve release plus the floored pool payout, the Blend share waits in `blend_rewards_pending` until its epoch closes and in `blend_rewards_closed` until it is paid, what is not distributed returning to the reserve since the pool pays only what the fee window sets, and the proof of work share of the fees of each block waits in `pow_rewards_pending` until the next epoch boundary credits it to the proof of work reward pool. The leader receives 40% of `R_t`, rounded down, plus the Execution market tips of the block, in one note, the remainder going to the Blend reward ([Cryptoeconomics overview](../overview-cryptoeconomics.md#blend-service-and-consensus-leaders)).

The system design figure is redrawn around the reserve, the pool and the per-block reward, and a new annex projects the supply with a per-block simulation over 10 years: the stake and a pooling rate of 0.5% per year settle within 2 years, the inferred stake carries a noise of 0.1 per epoch, and the fees of each block follow a Poisson number of transactions. The net circulating growth is about 3% of the maximum supply after 10 years, 2.8% to 3.2% over 20 runs. The moving average smooths how the fees vary from block to block; the noise of the inferred stake dominates `A_t`, the growth being 3.25% without it and 2.94% with twice as much.

## 7. Encoding

- `ChannelInscribe = ChannelId Inscription Parent Signer MiniBlocks`, with `MiniBlocks = MiniBlockCount *MiniBlock`, `MiniBlock = StepCount *ChannelStep`, a decoder rejecting an empty mini-block, and `ChannelStep = Inputs Outputs CmMerkleRoot`. `ChannelInscribeOpProof = Ed25519Signature *ZkTransfer`.
- `ChannelDeposit = ChannelId Inputs CmMerkleRoot Outputs Value DepositMetadata`, `ChannelWithdraw = ChannelId Inputs CmMerkleRoot Outputs`, `SDPDeclare = ServiceType Locators ProviderId ZkId Inputs CmMerkleRoot Value`, `SDPWithdraw = DeclarationId Nonce NoteNf Outputs Value`. `ChannelConfig` loses `TransferThreshold`.
- `Transfer = Inputs Outputs CmMerkleRoot Value`, with `Inputs` of `NoteNf` and `Outputs` of `NoteCm`. `ClaimPowReward` gains `PowNonce`.
- `ChannelTransfer`, `LeaderClaim` and their proofs are removed, and so is `ChannelWithdrawOpProof`: a channel withdrawal carries a `ZkTransferProof`. `ZkTransferProof` and `ZkTransferAndEd25519SigProof` replace `ZkSigProof` and `ZkAndEd25519SigsProof`, and `ZkTransfer = Groth16` replaces `ZkSignature = Groth16`. `ChannelInscribeOpProof` is added for inscriptions and their steps, and `EmptyProof` for `ClaimPowReward`.
- Mantle Transaction Encoding is revision 2.0.0.

## 8. Cryptarchia and Proof of Quota inputs

- The epoch state `C_LEAD` is `eligible_root_at_slot` at the start of the previous epoch.
- An uncle's Proof of Leadership is verified against `eligible_LATEST` as of its parent block.
- The `block_id` preimage and the header absorb `reward_key` in place of `leader_voucher`.
- The PoQ leader branch takes `pol_eligible_aged`, and its witness takes `pol_note_nonce`, the aged commitment path, the low leaf of the set's aged nullifier IMT with its path, and the set path. It proves the nullifier of the note absent from that IMT. Message Encapsulation retrieves `pol_eligible_aged`.

## 9. Genesis

- The ledger and SDP sets start empty.
- The Transfer outputs are commitments in the ledger set, the nonce of each note being its output index. The Genesis Transfer, having no proof, is exempt from the 8-output limit of a ZkTransfer.
- No proof of the Genesis transaction is verified. After the Genesis transaction, every note set it appended to records its commitment root, and the block reward reserve, pool, Blend and proof of work shares and fee window are initialized.
- A second inscription to the null channel publishes `value` and `public_key` for each output, and validation checks every output against it.
- The declarations consume no note. Only the holder of a note can compute its nullifier, so without a proof a nullifier given at Genesis could not be tied to a note, and a declaration naming an arbitrary one would stake value on top of a note that stays spendable. Their amounts count in the supply: validation checks that the published values, the amounts of the declarations, the proof of work reward pool and the reserve sum to `S_cap`.

## 10. Wallet note tracking

The wallet keeps, for each note, its set, the commitment path inside its MMR peak and its nullifier, and for the lottery the aged path with the set's leaf path and the IMT low leaf of the same set, at the latest root and, for the Proof of Quota, at the freeze. A peak path grows only when its peak merges, at most 40 times. Each nullifier insertion changes two public leaves, from which the wallet updates its low leaf path with at most 40 hashes per changed leaf. A proof following other Operations of its transaction that add to the same set is against the root extended with the commitment buffer.

## Chores

- Common Cryptographic Components removes the ZkSignature scheme and the voucher mention.
- Key Types derives the Non-ephemeral Quota Key public key as in Mantle.
- Block Construction: the batch verification annex covers ZkTransfer and pairs each `pi_A` with its own `pi_B`, and a note cannot be spent by a later transaction of the block that creates it.
- The cross-channel messaging template is deprecated and moved to `deprecated/`.
- The Execution Market and Blend follow the in-block leader reward, and the Execution Market and Cryptoeconomics overview figures are redrawn from Graphviz sources. The Architecture Overview has Transfer Operations over private notes pay the fees and every channel hold a note set.
- Payload Formatting and Message Formatting follow the smaller block proposal: `Max_Body_Length` is 17,712 bytes and `Max_Payload_Length` 17,715 bytes, and the Blend message 18,838 bytes. Bootstrapping and Total Stake Inference carry the uncle headers without signatures.
- Common Cryptographic Components states the hash mode of the three-element nullifier and the compression mode of the Proof of Quota key nullifier, and the Service Declaration Protocol types the stake threshold as a `TokenValue`.
- The Gas Cost Determination analysis follows the new Operations and drops the Proof of Claim measures and images. The ZkTransfer (27 public inputs) is priced from the measured batch verification of Groth16 proofs, `cycles(n, N) = A(N) + n * P`: each proof costs `P = 618,797` cycles, so `EXECUTION_TRANSFER_GAS`, `EXECUTION_CHANNEL_DEPOSIT_GAS` and `EXECUTION_CHANNEL_WITHDRAW_GAS` are 619 and the SDP declaration and withdrawal 678. The fixed part `A(27) = 3,540,612` cycles is deducted from the block limit: `limit_Ex = G_max = 3,196,459` and `G_target = 1,598,229`.
- The PoL circuit diagram and the Example sections of the Mantle Operations are removed. The Mantle and Cryptarchia test vectors are derived from the specification, for the implementation to reproduce.

# Implementation

- [ ] Implement the note sets in the ledger: one commitment MMR, nullifier IMT, 1024 recent roots and transaction buffer per set, a new set per channel.
- [ ] Implement the ZkTransfer circuit and its verifier, with buffer-extended roots.
- [ ] Switch Transfer, deposits and SDP declarations to nullifiers and commitments in the ledger set.
- [ ] Add mini-blocks of steps to `CHANNEL_INSCRIBE`, verify their ZkTransfers against `step_msg` and the buffer before each mini-block, and apply them to the channel set.
- [ ] Implement holder withdrawals, applied after `WITHDRAW_DELAY` if their inputs are still unspent.
- [ ] Remove `CHANNEL_TRANSFER`, the channel `transfer_threshold`, the transparent channel and service notes, `LEADER_CLAIM`, the voucher set and the Proof of Claim verifier.
- [ ] Create service notes in the SDP set, and consume them in `SDP_WITHDRAW` with a ZkTransfer.
- [ ] Sign `SDP_WITHDRAW` and `SDP_ACTIVE` with Ed25519, and drop the proof of `CLAIM_POW_REWARD`.
- [ ] Add `reward_key` to the header and insert the leader reward note during block execution.
- [ ] Keep the pooled fees of the last 120 blocks, the reserve, the pool, the closed and pending Blend shares and the pending proof of work share, and compute the block reward in integers.
- [ ] Pay the Blend rewards from the closed Blend share, returning what they do not use to the reserve.
- [ ] Update the PoL circuit (`mantle/pol_lib.circom` in `logos-blockchain-circuits`) and the PoQ circuit (`blend/poq.circom`) to the eligible root, the PoQ leader branch proving the non-membership of the note nullifier in the aged IMT.
- [ ] Record the commitment root of the note sets a block appends to, and the eligible root of every block.
- [ ] Reject a block whose transactions sum to more than $`G_\text{max}`$ Execution Gas, and confirm the body root of a proposal before verifying its uncles.
- [ ] Update the encoding of payloads and proofs.
- [ ] Build the genesis note sets and distribution inscription, and their validation.
- [x] Benchmark the ZkTransfer batch verification and update the gas values.
- [ ] Regenerate the Mantle and Cryptarchia test vectors, and add tests for buffer chaining, the root window, IMT non-membership, steps, withdrawals and the eligible root.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.0.0 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | Revision 1.2.0 |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | Revision 1.4.0 |
| [Block Rewards](../block-rewards.md) | Modified | Revision 1.4.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | Revision 1.5.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.0.0 |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.0 |
| [Proof of Quota](../proof-of-quota.md) | Modified | Revision 1.3.0 |
| [Message Encapsulation](../message-encapsulation.md) | Modified | Revision 1.2.1 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.3.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.9.0 |
| [Service Reward Distribution](../bedrock-service-reward-distribution.md) | Modified | Revision 1.4.0 |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.2.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.2.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.3.0 |
| [Key Types and Generation](../key-types-and-generation.md) | Modified | Revision 1.1.1 |
| [Execution Market](../execution-market.md) | Modified | Revision 1.3.0 |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 1.8.0 |
| [Analysis: Execution Market](../analysis-execution-market.md) | Modified | Revision 1.0.1 |
| [Architecture Overview](../bedrock-architecture-overview.md) | Modified | Revision 1.2.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | leader reward reference, encapsulation overhead and rounding of the base reward, Revision 1.8.1 |
| [Payload Formatting](../payload-formatting.md) | Modified | Revision 1.2.1 |
| [Message Formatting](../message-formatting.md) | Modified | Revision 1.0.3 |
| [Bootstrapping and Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | Revision 1.0.3 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | Revision 1.1.2 |
| [Cross-Channel Messaging Template](../../deprecated/template-cross-channel-messaging.md) | Deprecated | moved to `deprecated/` |
| [Anonymous Leaders Reward](../../deprecated/bedrock-anonymous-leaders-reward.md) | Deprecated | moved to `deprecated/` |
