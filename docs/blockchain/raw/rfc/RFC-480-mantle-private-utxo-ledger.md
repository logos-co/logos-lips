# [RFC] Mantle: Private UTXO ledger

**Motivation and proposal:** [PR #480](https://github.com/logos-co/logos-lips/pull/480)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-07 |

## Reviewer Orientation

Read the PR's Motivation first. The ledger change in Mantle is the base every other document builds on.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [private notes and their ledger](#1-private-notes-commitment-mmr-and-nullifier-imt) | the commitment MMR, the nullifier IMT and its leaf hash, the 1024-block root window |
| 2 | Critical | [Mantle](#affected-specifications), [commitment buffer of a transaction](#2-commitment-buffer-of-a-mantle-transaction) | which root a ZkTransfer is verified against; chaining outputs inside one transaction |
| 3 | Critical | [Mantle](#affected-specifications), [Operations on private notes](#3-operations-on-private-notes) | Transfer, channel and SDP Operations consuming nullifiers; transparent channel and service notes |
| 4 | Critical | **Start here**: [Proof of Leadership](#affected-specifications), [eligible sets](#4-proof-of-leadership-over-two-eligible-sets) | the `is_shielded` selector and the aged and latest checks it gates |
| 5 | High | [Block Construction](#affected-specifications), [leader reward in the block](#5-leader-reward-paid-in-the-block) | `reward_key` in the header, the reward note, reuse of the key |
| 6 | High | [Block Rewards](#affected-specifications), [Cryptoeconomics overview](#affected-specifications), [reward from the block's fees](#6-block-reward-from-the-blocks-own-fees) | `T = 1`, the integer reference, the 40% leader share plus tips |
| 7 | High | [Mantle](#affected-specifications), [SDP and proof of work Operations](#7-sdp-signatures-and-the-proof-of-work-claim) | Ed25519 by `provider_id`; the ticket over a public nonce; empty proof |
| 8 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#8-encoding) | new payload productions and proof variants |
| 9 | High | [Cryptarchia](#affected-specifications), [Proof of Quota](#affected-specifications), [Message Encapsulation](#affected-specifications), [consensus inputs](#9-cryptarchia-and-proof-of-quota-inputs) | epoch state roots, uncle verification inputs, PoQ leader branch |
| 10 | High | [Genesis Block](#affected-specifications), [genesis](#10-genesis) | the distribution inscription; declarations spending the distribution |
| 11 | Medium | [Service Declaration Protocol](#affected-specifications), [Service Reward Distribution](#affected-specifications), [Proof of Work](#affected-specifications), [Gas Cost Determination](#affected-specifications) | follow-on changes of items 3 and 7 |
| 12 | Medium | [Wallet Technical Standard](#affected-specifications), [note tracking](#11-wallet-note-tracking) | the MMR and IMT path updates |
| 13 | Low | the remaining documents in [Chores](#chores) | skim |

# Discussion

## Root window and commitment buffer

A ZkTransfer proves its inputs against a commitment root from one of the last 1024 blocks. A wallet can therefore build its proof against a root a few blocks old and still be included, without rebuilding it for every new block. The 1024 bound keeps the set of roots a validator holds small.

Inside a Mantle Transaction, the commitments created by earlier Operations go into a buffer, and a proof is verified against its referenced root with the buffer appended. An Operation can spend an output of an earlier Operation of the same transaction, for example a channel withdrawal followed by a deposit. Across the transactions of one block this does not hold: a shielded note created in a block can be spent from the next block on.

> **TODO (author):** explain why 1024 blocks, and whether spending across transactions of a block is planned.

## Channel and service notes stay transparent

A channel spends its notes with its sequencers' signatures, without the secret key of the note's public key, so it cannot derive the note's nullifier. Channel notes therefore stay in a transparent mapping, keyed by commitment and removed when spent. Service notes are created by `SDP_DECLARE` under the `zk_id`, one per declaration, and are kept with their declaration until it is removed.

The Proof of Leadership covers both kinds. A shielded note proves it is unspent by nullifier non-membership. A transparent note proves it is still present in the latest transparent set. A private selector picks the check, so a leader does not reveal which kind of note won.

> **TODO (author):** state the plan for giving channel notes nullifiers, which would let the transparent set go.

## Leader reward in the block

With private notes, the reward note of a block can carry the block's own value and still not link the leader to its spending: the spend reveals a nullifier and no commitment. The voucher set, the pooled leader reward and `LEADER_CLAIM` existed to hide that link and are retired. The block reward follows the fees of its own block (`T = 1`), because the dependency on the block content no longer reveals anything once the note is spent.

The reward note has nonce `0`. Two rewards of the same value under the same `reward_key` share a commitment, and only one can be spent. A leader that reuses a key also links its blocks together. This forces a fresh key per block.

## Proof of work claim without a proof

The ticket hashes the public key the reward is paid to, so a solution only pays that key. A copied claim pays the same key, and the claim needs no signature. Its Execution Gas is `0`.

## Open questions for reviewers

- How a wallet learns the value and nonce of a note it receives through a Transfer is out of scope. Only commitments are on chain.
- The ZkTransfer gas values reuse the earlier ZkSignature measures until the circuit is benchmarked.
- The simulation behind the 10-year supply projection in Block Rewards predates `T = 1`.
- PR #407 (SDP declaration identifiers) touches the same SDP sections. Its `service_notes` map and per-service note uniqueness do not apply once each declaration creates its own note.

# Details

## 1. Private notes: commitment MMR and nullifier IMT

A note is `(value, nonce, public_key)`. The Ledger stores its commitment `derive_note_cm(note)` in the commitment MMR, and the nullifier `derive_note_nf(cm, sk)` of each spent note in the nullifier set.

```python
class MantleNotes:
    commitments: list[MerkleRoot] # the peaks of the MMR
    nullifiers: set[NoteNf]       # the set of nullifiers, maintained in an IMT

class Ledger:
    mantle_notes: MantleNotes
    recent_cm_roots: list[MerkleRoot]   # the commitment MMR roots of the last 1024 blocks
    tx_cm_buffer: list[NoteCm]          # the commitments added by the previous Operations
                                        # of the Mantle Transaction, empty at its start
    channel_notes: dict[NoteCm, (Note, ChannelId)]
```

- The nullifier IMT has depth 32 and appends leaves in insertion order. A leaf is `NullifierLeaf(nf, next_nf, next_index)`, hashed with the DST `NULLIFIER_IMT_LEAF_V1`. The first leaf is the sentinel `(0, 0, 0)`, and positions past the last leaf hold `0`.
- `assert_spendable(inputs, cm_merkle_root)` checks non-empty, distinct inputs, a root in `recent_cm_roots`, and nullifiers absent from the set. `execute_spending` inserts the nullifiers; `execute_adding` appends commitments to the MMR and to the buffer.
- Channel notes use `assert_spendable_channel`, `execute_spending_channel` and `execute_adding_channel`, the last deriving each nonce with `derive_note_nonce`.
- `derive_note_nonce(op_id, output_number, value, public_key)` takes the value and key directly, with the DST `NOTE_NONCE_V1`.
- Mantle is revision 2.0.0.

## 2. Commitment buffer of a Mantle Transaction

Every Operation referencing a commitment root references the root of one of the last 1024 blocks. `ZkTransfer_verify` checks the proof against that root with the commitments of `tx_cm_buffer` appended.

```python
class ZkTransferPublic:
    inputs: list[NoteNf]       # (len = 4)
    outputs: list[NoteCm]      # (len = 8)
    excess_value: TokenValue
    cm_merkle_root: MerkleRoot # a recent MMR root, with the tx_cm_buffer appended
    msg: zkhash
```

The ZkTransfer proves key ownership, commitment derivation, nullifier derivation, membership in the root, well-formed outputs, and `excess_value = inputs - outputs`. Unused input and output slots carry value `0`.

## 3. Operations on private notes

```diff
 class Transfer:
-    inputs: list[NoteId]
-    outputs: list[Note]
+    inputs: list[NoteNf]
+    outputs: list[NoteCm]
+    cm_merkle_root: MerkleRoot
+    excess_value: TokenValue
```

- `CHANNEL_DEPOSIT` consumes nullifiers with a ZkTransfer of `amount`, then creates the channel note `(amount, pk)` in the channel.
- `CHANNEL_WITHDRAW` removes channel notes by commitment and appends the same commitments to the MMR.
- `CHANNEL_TRANSFER` consumes channel notes by commitment and creates outputs given as `(value, public_key)`.
- `SDP_DECLARE` carries `inputs`, `cm_merkle_root` and `amount`, proven by a ZkTransfer. It creates one service note `Note(amount, derive_note_nonce(op_id, 0, amount, zk_id), zk_id)`, stored in `DeclarationInfo.service_note: NoteCm`. At [SDP Epoch Finalization](../bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization), the declaration's removal appends the note to the MMR. The `service_notes` map is removed.
- `LEADER_CLAIM`, the Proof of Claim appendix and `EXECUTION_LEADER_CLAIM_GAS` are removed.

## 4. Proof of Leadership over two eligible sets

The shielded eligible set is the commitment MMR. The transparent eligible set is a depth-32 Merkle tree over the service and channel note commitments, where insertion fills the first empty leaf and deletion writes `0`.

```python
class ProofOfLeadershipPublic:
    # ... slot, epoch_nonce, t0, t1 unchanged
    shielded_aged: MerkleRoot       # new
    transparent_aged: MerkleRoot    # new
    nullifiers_latest: MerkleRoot   # new
    transparent_latest: MerkleRoot  # new
    leader_pk: (FrElement, FrElement)
    entropy_contribution: zkhash
```

- The aged root is selected by the private boolean `is_shielded`: `aged_root == is_shielded * shielded_aged + (1 - is_shielded) * transparent_aged`.
- A shielded note proves `nf` absent from the IMT: a leaf `low` with `low.nf < nf` and `nf < low.next_nf` or `low.next_nf == 0`, in `nullifiers_latest`. A transparent note proves `cm` in `transparent_latest`. Each check is multiplied by its selector.
- The lottery ticket and the entropy contribution use the commitment `cm`.
- The PoL statement uses the public values, witness and constraints layout of ZkTransfer. The PoL is revision 1.2.0.

## 5. Leader reward paid in the block

```diff
 class ProofOfLeadership:
     # ... proof, entropy_contribution, leader_key unchanged
-    leader_voucher: RewardVoucher
+    reward_key: ZkPublicKey
```

Block Execution runs the service rewards, then the transactions, then inserts the leader reward:

```python
leader_note = Note(
    value=get_leader_reward(block),
    nonce=0,
    public_key=block.header.proof_of_leadership.reward_key
)
ledger.execute_adding([derive_note_cm(leader_note)])
```

`reward_key` must be fresh for every block. Block Construction is revision 1.4.0. The [Anonymous Leaders Reward](../../deprecated/bedrock-anonymous-leaders-reward.md) specification is deprecated.

## 6. Block reward from the block's own fees

The block reward is `R_t = A_t * I_max * S_cap * Delta_t + (1 - A_t) * R_block`, where `R_block` is the fees pooled in the block, with a time step of one block. The integer reference uses 128-bit intermediates:

```python
FEE_NUMERATOR: int64 = 1_261_440        # was: 10_512 over a window of 120 blocks

def block_reward(total_stake: uint64, pooled_fee: uint64) -> uint64:
    # ... int128 intermediates
```

The leader receives 40% of `R_t` plus the Execution market tips of the block, in one note ([Cryptoeconomics overview](../overview-cryptoeconomics.md#blend-service-and-consensus-leaders)).

## 7. SDP signatures and the proof of work claim

- `SDP_WITHDRAW` and `SDP_ACTIVE` carry an `Ed25519Signature` by the declaration's `provider_id`. `WithdrawMessage` has no `service_note_id`.
- `CLAIM_POW_REWARD` gains a `nonce`. The ticket is `zkhash(nonce, public_key, block_hash, epoch_nonce)`, the proof is empty, and the reward note nonce is `derive_note_nonce(claim_id, 0, epoch_pow_reward, public_key)`.
- Execution Gas: `EXECUTION_SDP_WITHDRAW_GAS = 59`, `EXECUTION_SDP_ACTIVE_GAS = 59`, `EXECUTION_CLAIM_POW_REWARD_GAS = 0`.

## 8. Encoding

- Payloads: `Transfer = Inputs Outputs CmMerkleRoot Value`, with `Inputs` of `NoteNf` and `Outputs` of `NoteCm`. `ChannelDeposit`, `SDPDeclare` and `ClaimPowReward` gain the fields above. `ChannelWithdraw` and `ChannelTransfer` use `ChannelNotes`, and `ChannelOutputs` is a list of `(Value ZkPublicKey)`. `SDPWithdraw = DeclarationId Nonce`. `LeaderClaim` is removed.
- Proofs: `ZkTransferProof`, `ZkTransferAndEd25519SigProof` and `EmptyProof` replace `ZkSigProof`, `ZkAndEd25519SigsProof` and `ProofOfClaimProof`.
- Mantle Transaction Encoding is revision 2.0.0.

## 9. Cryptarchia and Proof of Quota inputs

- The epoch state `C_LEAD` is the pair `(shielded_root_at_slot, transparent_root_at_slot)` at the start of the previous epoch.
- An uncle's Proof of Leadership is verified against `nullifiers_LATEST` and `transparent_LATEST` as of its parent block.
- The `block_id` preimage and the header absorb `reward_key` in place of `leader_voucher`.
- The PoQ leader branch takes `pol_shielded_aged` and `pol_transparent_aged`, and its witness takes `pol_note_nonce`, `pol_is_shielded` and the aged commitment path. Message Encapsulation retrieves both roots.

## 10. Genesis

- The Transfer outputs are commitments, the nonce of each note being its output index.
- A second inscription to the null channel, chained after the Cryptarchia parameters, publishes `value` and `public_key` for each output. Validation checks every output against it.
- The declarations spend the distributed notes by nullifier, proven against the empty MMR root with the commitment buffer appended. Before Genesis the empty MMR root is the only recent root, and the IMT holds only its sentinel.

## 11. Wallet note tracking

The wallet keeps, for each note, the commitment path inside its MMR peak, the nullifier, and for the lottery the aged path and the IMT low leaf. A peak path grows only when its peak merges, at most 32 times. Each nullifier insertion changes two public leaves, from which the wallet updates its low leaf path with at most 32 hashes per changed leaf.

## Chores

- Common Cryptographic Components removes the ZkSignature scheme and the voucher mention.
- Key Types derives the Non-ephemeral Quota Key public key as in Mantle.
- Block Construction: the batch verification annex covers ZkTransfer and pairs each `pi_A` with its own `pi_B`, and the same-block limitation of shielded notes is stated.
- The Execution Market, the Architecture Overview, Blend and the cross-channel messaging template follow the private ledger and the in-block leader reward.
- The Gas Cost Determination analysis follows the new Operations and drops the Proof of Claim measures and images.
- The PoL circuit diagram, the Block Rewards figure and the test vectors carry TODO markers.

# Implementation

- [ ] Implement the commitment MMR with the 1024 recent roots, the nullifier IMT and the transaction commitment buffer in the ledger.
- [ ] Implement the ZkTransfer circuit and its verifier, with buffer-extended roots.
- [ ] Switch Transfer, channel and SDP Operations to nullifiers and commitments, and keep channel notes in the transparent mapping.
- [ ] Sign `SDP_WITHDRAW` and `SDP_ACTIVE` with Ed25519, and drop the proof of `CLAIM_POW_REWARD`.
- [ ] Remove `LEADER_CLAIM`, the voucher set and the Proof of Claim verifier.
- [ ] Add `reward_key` to the header and insert the leader reward note during block execution.
- [ ] Compute the block reward from the block's own fees.
- [ ] Update the PoL circuit (`mantle/pol_lib.circom` in `logos-blockchain-circuits`) and the PoQ circuit (`blend/poq.circom`) to the two eligible sets.
- [ ] Update the encoding of payloads and proofs.
- [ ] Build the genesis distribution inscription and its validation.
- [ ] Benchmark the ZkTransfer batch verification and update the gas values.
- [ ] Regenerate the Mantle and Cryptarchia test vectors, and add tests for buffer chaining, the root window, IMT non-membership and the PoL selector.
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
