# [RFC] Mantle: Private UTXO ledger

**Motivation and proposal:** [PR #480](https://github.com/logos-co/logos-lips/pull/480)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-07 |
| v2 | Notes live in note sets: a ledger, an SDP and one per channel, each with its commitment MMR and nullifier IMT, committed together in the eligible root of the Proof of Leadership. Channel notes are moved by the steps their holders sign, published by `CHANNEL_INSCRIBE`, and withdrawn by their holders. Removed the transparent channel and service notes, the transparent eligible set and the `is_shielded` selector, `CHANNEL_TRANSFER` and the channel `transfer_threshold`. `SDP_WITHDRAW` consumes the service note with a ZkTransfer | 2026-10-07 |
| v3 | The spending, adding and transfer verification functions are methods of `NoteSet`. The recent commitment roots of a set keep their MMR peaks, to which `verify_transfer` appends the buffer of the Mantle Transaction. Two steps of an inscription cannot consume the same note | 2026-10-08 |
| v4 | Operations append their outputs to the commitment buffer when validated, and a step can consume the outputs of an earlier step of its inscription. A channel withdrawal consumes its inputs at its due slot, only if they are still unspent, so a valid step cancels it. The withdrawal of a service note is proven against the root of an MMR holding only that note. The PoW ticket hashes the public key first | 2026-10-09 |

## Reviewer Orientation

Read the PR's Motivation first. The note sets in Mantle are the base every other document builds on.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [note sets](#1-note-sets) | one commitment MMR and nullifier IMT per set; the 1024-block root window and the commitment buffer per set |
| 2 | Critical | [Mantle](#affected-specifications), [channel Operations](#2-channel-notes-moved-by-their-holders) | steps bound to `step_msg` and verified on chain; holder withdrawals with `WITHDRAW_DELAY` |
| 3 | Critical | **Start here**: [Proof of Leadership](#affected-specifications), [eligible root](#3-proof-of-leadership-over-the-eligible-root) | the eligible tree over the sets; the same set position for the aged and latest checks |
| 4 | High | [Mantle](#affected-specifications), [SDP and proof of work](#4-sdp-stake-and-the-proof-of-work-claim) | the SDP note set; the single-note MMR root binding the withdrawal to its service note; the unsigned PoW claim |
| 5 | High | [Block Construction](#affected-specifications), [leader reward and block execution](#5-leader-reward-paid-in-the-block) | `reward_key`, the reward note, the release of due withdrawals |
| 6 | High | [Block Rewards](#affected-specifications), [Cryptoeconomics overview](#affected-specifications), [reward from the block's fees](#6-block-reward-from-the-blocks-own-fees) | `T = 1`, the integer reference, the 40% leader share plus tips |
| 7 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#7-encoding) | steps in `ChannelInscribe`, new payloads and proof variants |
| 8 | High | [Cryptarchia](#affected-specifications), [Proof of Quota](#affected-specifications), [Message Encapsulation](#affected-specifications), [consensus inputs](#8-cryptarchia-and-proof-of-quota-inputs) | epoch state and uncle inputs, PoQ leader branch |
| 9 | High | [Genesis Block](#affected-specifications), [genesis](#9-genesis) | the initial sets; the distribution inscription; declarations spending the distribution |
| 10 | Medium | [Service Declaration Protocol](#affected-specifications), [Service Reward Distribution](#affected-specifications), [Proof of Work](#affected-specifications), [Gas Cost Determination](#affected-specifications) | follow-on changes of items 2 and 4 |
| 11 | Medium | [Wallet Technical Standard](#affected-specifications), [note tracking](#10-wallet-note-tracking) | per-set tracking; MMR and IMT path updates |
| 12 | Low | the remaining documents in [Chores](#chores) | skim |

# Discussion

## One note set per partition

Every note is private and lives in exactly one note set: the ledger, the SDP, or a channel. A set has its own commitment MMR and nullifier IMT, so an Operation only ever touches the sets it names: a Transfer the ledger set, a step its channel's set, a withdrawal its channel's set and then the ledger set. The Proof of Leadership covers every set through one eligible root, and a note's kind no longer changes how it proves itself. This is what removes the transparent channel and service notes, the transparent eligible set and the selector of the Proof of Leadership.

## Channel notes: moved by holders, ordered by sequencers

A channel note is spent only by its holder. Inside the channel, the holder signs a step, a ZkTransfer bound to `step_msg` rather than to the transaction, since it is signed before the transaction exists. The sequencers collect the steps and publish them in their inscriptions, and the ledger verifies every step. A sequencer orders the moves of its channel and can delay or drop a step, but cannot move a note, and cannot create value: every step is a verified, balanced ZkTransfer.

Out of the channel, the holder withdraws alone. The withdrawal takes effect `WITHDRAW_DELAY` slots later, only if its notes are still unspent: until then, an inscription can consume them with a valid step, which cancels it. A holder cannot invalidate an inscription carrying one of its steps by withdrawing the same note first.

All the data of a step lands on chain: its nullifiers, its commitments and its proof. Steps are not compressed, so a channel costs the chain as much per move as the ledger does. Steps carry no `excess_value`, so a move inside a channel pays no fee from channel funds, and the fee of the inscription comes from its sequencer.

> **TODO (author):** state the compression planned for steps (proof aggregation, and later a transition proof over the hash of the nullifiers and commitments with data availability), and the step volume at which it pays off.

## Root window and commitment buffer

A ZkTransfer proves its inputs against a commitment root of their set from one of the last 1024 blocks. A wallet can therefore build its proof against a root a few blocks old and still be included. Inside a Mantle Transaction, the commitments created by earlier Operations go into the buffer of their set, and a proof is verified against its referenced root with that buffer appended. A note created in a block can be spent from the next block on, or later in the same transaction.

> **TODO (author):** explain why 1024 blocks.

## SDP stake

The service note is created by the ledger in the SDP set, so it stakes like any note. Its withdrawal is proven against the root of an MMR holding only the declaration's service note, which ties the consumed nullifier to that note without exposing it in the circuit. The outputs reach the ledger set when the declaration is removed, as the stake is released today.

## Leader reward in the block

The reward note of a block carries the block's own value and still does not link the leader to its spending: the spend reveals a nullifier and no commitment. The voucher set, the pooled leader reward and `LEADER_CLAIM` are retired, and the block reward follows the fees of its own block (`T = 1`). The reward note has nonce `0`, so two rewards of the same value under one `reward_key` share a commitment and only one can be spent, which forces a fresh key per block.

## Atomic swaps across zones

Value moves between two channels only through a withdrawal and its delay. A cross-zone swap therefore exchanges notes inside each channel: each zone publishes the step of one party, and both inscriptions share one Mantle Transaction.

## Open questions for reviewers

- How a wallet learns the value and nonce of a note it receives through a Transfer or a step is out of scope. Only commitments are on chain.
- The ZkTransfer gas values reuse the earlier ZkSignature measures until the circuit is benchmarked.
- The simulation behind the 10-year supply projection in Block Rewards predates `T = 1`.
- PR #407 (SDP declaration identifiers) touches the same SDP sections. Its `service_notes` map and per-service note uniqueness do not apply once each declaration creates its own note.

# Details

## 1. Note sets

A note is `(value, nonce, public_key)`, stored as its commitment `derive_note_cm(note)`. Each note set keeps the commitments of its notes in an MMR and the nullifiers `derive_note_nf(cm, sk)` of its spent notes in an IMT.

```python
LEDGER_SET = 0
SDP_SET = 1

class NoteSet:
    commitments: list[MerkleRoot]       # the peaks of the commitment MMR
    nullifiers: set[NoteNf]             # the set of nullifiers, maintained in an IMT
    recent_cm_roots: dict[MerkleRoot, list[MerkleRoot]]  # roots of the last 1024 blocks, with their peaks
    tx_cm_buffer: list[NoteCm]          # commitments added earlier in the Mantle Transaction

class Ledger:
    sets: list[NoteSet]                              # ledger, SDP, then one per channel by creation
    pending_withdrawals: list[(Slot, int, list[NoteNf], list[NoteCm])]
```

- A channel gets the next note set when it is created, stored as `ChannelState.note_set`.
- The nullifier IMT has depth 32 and appends leaves in insertion order. A leaf is `NullifierLeaf(nf, next_nf, next_index)`, hashed with the DST `NULLIFIER_IMT_LEAF_V1`. The first leaf is the sentinel `(0, 0, 0)`, and positions past the last leaf hold `0`.
- `assert_spendable(inputs, cm_merkle_root)`, `verify_transfer(...)`, `execute_spending(inputs)` and `execute_adding(outputs)` are methods of `NoteSet`, called as `ledger.sets[LEDGER_SET].execute_adding(...)`.
- `verify_transfer` checks the ZkTransfer against the referenced root with the set's buffer appended. `ZkTransfer_verify(...)` checks it against a given root.
- Every `excess_value` adds to the transaction balance, except that steps carry none.
- `derive_note_nonce(op_id, output_number, value, public_key)` uses the DST `NOTE_NONCE_V1`.
- Mantle is revision 2.0.0.

## 2. Channel notes moved by their holders

```python
class ChannelStep:
    inputs: list[NoteNf]
    outputs: list[NoteCm]
    cm_merkle_root: MerkleRoot  # a recent root of the channel note set

class Inscribe:
    # ... channel, inscription, parent, signer unchanged
    steps: list[ChannelStep]    # new
```

- Each step carries a ZkTransfer with `msg = step_msg(step)`, a hash of its nullifiers and commitments under the DST `CHANNEL_STEP_V1`, and `excess_value = 0`. The `InscribeProof` holds the signer's Ed25519 signature and one ZkTransfer per step.
- The steps are validated against the state the inscription is validated against, then applied in order to the channel note set. A channel being created carries no step.
- `CHANNEL_DEPOSIT` consumes ledger notes and creates channel notes, `outputs` being commitments. Its `excess_value` pays fees.
- `CHANNEL_WITHDRAW` is posted by the holder with a ZkTransfer. At the first block whose slot reaches `WITHDRAW_DELAY = 86,400` slots after it, its inputs are consumed and its `outputs` created in the ledger set if the inputs are still unspent; otherwise it is dropped.
- `CHANNEL_TRANSFER`, opcode `0x14`, and the channel `transfer_threshold` are removed.
- Execution Gas: `EXECUTION_CHANNEL_INSCRIBE_GAS + EXECUTION_TRANSFER_GAS * len(steps)`, `EXECUTION_CHANNEL_WITHDRAW_GAS = 590`.

## 3. Proof of Leadership over the eligible root

The eligible root is a Merkle tree of depth 32 whose leaf `i` is `zkhash(ELIGIBLE_SET_LEAF_V1, cm_root_i, nf_root_i)` for note set `i`, positions past the last set holding `0`.

```python
class ProofOfLeadershipPublic:
    # ... slot, epoch_nonce, t0, t1 unchanged
    eligible_aged: MerkleRoot       # new
    eligible_latest: MerkleRoot     # new
    leader_pk: (FrElement, FrElement)
    entropy_contribution: zkhash
```

- The aged check proves `cm` in the commitment MMR of its set, and the leaf of that set, with the set's aged nullifier root, under `eligible_aged`.
- The latest check proves `nf` absent from the IMT of the same set: a leaf `low` with `low.nf < nf` and `nf < low.next_nf` or `low.next_nf == 0`, and the leaf of the set, with its latest commitment root, under `eligible_latest`.
- Both leaf paths use the same `set_selectors`, so both checks name the same set.
- The lottery ticket and the entropy contribution use the commitment `cm`. The PoL is revision 1.2.0.

## 4. SDP stake and the proof of work claim

- `SDP_DECLARE` consumes ledger notes with a ZkTransfer and appends the service note `Note(amount, derive_note_nonce(op_id, 0, amount, zk_id), zk_id)` to the SDP set. `DeclarationInfo` holds `service_note` and `withdraw_outputs`.
- `SDP_WITHDRAW` carries `service_note_nf`, `outputs` and `excess_value`, with a ZkTransfer proven against `mmr_root([declare_info.service_note])` and the `provider_id`'s Ed25519 signature. Its outputs reach the ledger set at removal.
- `SDP_ACTIVE` is signed by the `provider_id`.
- `CLAIM_POW_REWARD` gains a `nonce`, its ticket is `zkhash(public_key, nonce, block_hash, epoch_nonce)`, its proof is empty, and its reward note goes to the ledger set.
- Execution Gas: `EXECUTION_SDP_WITHDRAW_GAS = 649`, `EXECUTION_SDP_ACTIVE_GAS = 59`, `EXECUTION_CLAIM_POW_REWARD_GAS = 0`.

## 5. Leader reward paid in the block

```diff
 class ProofOfLeadership:
     # ... proof, entropy_contribution, leader_key unchanged
-    leader_voucher: RewardVoucher
+    reward_key: ZkPublicKey
```

Block Execution runs the service rewards, releases the due channel withdrawals, runs the transactions, then appends the leader reward note `Note(get_leader_reward(block), 0, reward_key)` to the ledger set. `reward_key` must be fresh for every block. Block Construction is revision 1.4.0. The [Anonymous Leaders Reward](../../deprecated/bedrock-anonymous-leaders-reward.md) specification is deprecated.

## 6. Block reward from the block's own fees

The block reward is `R_t = A_t * I_max * S_cap * Delta_t + (1 - A_t) * R_block`, where `R_block` is the fees pooled in the block, with a time step of one block. The integer reference uses 128-bit intermediates and `FEE_NUMERATOR = 1_261_440`. The leader receives 40% of `R_t` plus the Execution market tips of the block, in one note ([Cryptoeconomics overview](../overview-cryptoeconomics.md#blend-service-and-consensus-leaders)).

## 7. Encoding

- `ChannelInscribe = ChannelId Inscription Parent Signer Steps`, with `ChannelStep = Inputs Outputs CmMerkleRoot`. `ChannelInscribeOpProof = Ed25519Signature *ZkTransfer`.
- `ChannelDeposit = ChannelId Inputs CmMerkleRoot Outputs Value Metadata`, `ChannelWithdraw = ChannelId Inputs CmMerkleRoot Outputs Value`, `SDPWithdraw = DeclarationId Nonce NoteNf Outputs Value`. `ChannelConfig` loses `TransferThreshold`.
- `Transfer = Inputs Outputs CmMerkleRoot Value`, with `Inputs` of `NoteNf` and `Outputs` of `NoteCm`. `ClaimPowReward` gains `PowNonce`.
- `ChannelTransfer`, `LeaderClaim` and their proofs are removed. `ZkTransferProof`, `ZkTransferAndEd25519SigProof` and `EmptyProof` replace the ZkSignature and Proof of Claim variants.
- Mantle Transaction Encoding is revision 2.0.0.

## 8. Cryptarchia and Proof of Quota inputs

- The epoch state `C_LEAD` is `eligible_root_at_slot` at the start of the previous epoch.
- An uncle's Proof of Leadership is verified against `eligible_LATEST` as of its parent block.
- The `block_id` preimage and the header absorb `reward_key` in place of `leader_voucher`.
- The PoQ leader branch takes `pol_eligible_aged`, and its witness takes `pol_note_nonce`, the aged commitment path, the set's aged nullifier root and the set path. Message Encapsulation retrieves `pol_eligible_aged`.

## 9. Genesis

- The ledger and SDP sets start empty. The null channel, created by the Cryptarchia inscription, gets the third set.
- The Transfer outputs are commitments in the ledger set, the nonce of each note being its output index.
- A second inscription to the null channel publishes `value` and `public_key` for each output, and validation checks every output against it.
- The declarations spend the distributed notes, proven against the empty MMR root of the ledger set with its buffer appended.

## 10. Wallet note tracking

The wallet keeps, for each note, its set, the commitment path inside its MMR peak and its nullifier, and for the lottery the aged path with the set's leaf path and the IMT low leaf of the same set. A peak path grows only when its peak merges, at most 32 times. Each nullifier insertion changes two public leaves, from which the wallet updates its low leaf path with at most 32 hashes per changed leaf.

## Chores

- Common Cryptographic Components removes the ZkSignature scheme and the voucher mention.
- Key Types derives the Non-ephemeral Quota Key public key as in Mantle.
- Block Construction: the batch verification annex covers ZkTransfer and pairs each `pi_A` with its own `pi_B`, and notes cannot be spent in the block that creates them.
- The cross-channel messaging template shows an atomic swap of steps across two zones.
- The Execution Market, the Architecture Overview and Blend follow the in-block leader reward.
- The Gas Cost Determination analysis follows the new Operations and drops the Proof of Claim measures and images.
- The PoL circuit diagram, the Block Rewards figure and the test vectors carry TODO markers.

# Implementation

- [ ] Implement the note sets in the ledger: one commitment MMR, nullifier IMT, 1024 recent roots and transaction buffer per set, a new set per channel.
- [ ] Implement the ZkTransfer circuit and its verifier, with buffer-extended roots.
- [ ] Switch Transfer, deposits and SDP declarations to nullifiers and commitments in the ledger set.
- [ ] Add steps to `CHANNEL_INSCRIBE`, verify their ZkTransfers against `step_msg`, and apply them to the channel set.
- [ ] Implement holder withdrawals, applied after `WITHDRAW_DELAY` if their inputs are still unspent.
- [ ] Remove `CHANNEL_TRANSFER`, the channel `transfer_threshold`, the transparent channel and service notes, `LEADER_CLAIM`, the voucher set and the Proof of Claim verifier.
- [ ] Create service notes in the SDP set, and consume them in `SDP_WITHDRAW` with a ZkTransfer.
- [ ] Sign `SDP_WITHDRAW` and `SDP_ACTIVE` with Ed25519, and drop the proof of `CLAIM_POW_REWARD`.
- [ ] Add `reward_key` to the header and insert the leader reward note during block execution.
- [ ] Compute the block reward from the block's own fees.
- [ ] Update the PoL circuit (`mantle/pol_lib.circom` in `logos-blockchain-circuits`) and the PoQ circuit (`blend/poq.circom`) to the eligible root.
- [ ] Update the encoding of payloads and proofs.
- [ ] Build the genesis note sets and distribution inscription, and their validation.
- [ ] Benchmark the ZkTransfer batch verification and update the gas values.
- [ ] Regenerate the Mantle and Cryptarchia test vectors, and add tests for buffer chaining, the root window, IMT non-membership, steps, withdrawals and the eligible root.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.0.0 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | Revision 1.2.0 |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | Revision 1.4.0 |
| [Block Rewards](../block-rewards.md) | Modified | Revision 1.3.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | Revision 1.4.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.0.0 |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.0 |
| [Proof of Quota](../proof-of-quota.md) | Modified | Revision 1.3.0 |
| [Message Encapsulation](../message-encapsulation.md) | Modified | Revision 1.2.1 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.3.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.7.0 |
| [Service Reward Distribution](../bedrock-service-reward-distribution.md) | Modified | Revision 1.4.0 |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.2.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.2.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.3.0 |
| [Key Types and Generation](../key-types-and-generation.md) | Modified | Revision 1.1.1 |
| [Execution Market](../execution-market.md) | Modified | Revision 1.3.0 |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 1.8.0 |
| [Analysis: Execution Market](../analysis-execution-market.md) | Modified | reference to the deprecated leader reward |
| [Architecture Overview](../bedrock-architecture-overview.md) | Modified | Revision 1.2.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | leader reward reference |
| [Cross-Channel Messaging Template](../template-cross-channel-messaging.md) | Modified | Revision 1.3.0 |
| [Anonymous Leaders Reward](../../deprecated/bedrock-anonymous-leaders-reward.md) | Deprecated | moved to `deprecated/` |
