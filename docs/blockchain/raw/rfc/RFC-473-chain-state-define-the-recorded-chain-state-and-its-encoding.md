# [RFC] Chain-State: Define the recorded chain state and its encoding

**Motivation and proposal:** [PR #473](https://github.com/logos-co/logos-lips/pull/473)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |

## Reviewer Orientation

Read the PR's Motivation first. Every resolution below follows the reference implementation, `logos-blockchain` at `5a7d8f0b`, where the specifications disagreed with each other or said nothing; [Decisions](#decisions) lists each one.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Bedrock Chain State](../bedrock-chain-state.md), [details](#1-the-component-list-and-its-encoding) | the 28 components and the value each holds after a block; what is left out; the rules for order, counts and optional values; the layout version and the digest |
| 2 | Critical | **Start here**: [Mantle](../bedrock-v1.1-mantle-specification.md), [details](#2-the-ledger) | the ledger as a map with leaf positions, filled at the first empty leaf; `pow_nullifiers` with slots; claims checked against `block_slots` ([details](#4-proof-of-work-state)) |
| 3 | Critical | [Anonymous Leaders Reward Protocol](../bedrock-anonymous-leaders-reward.md), [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md), [details](#3-the-voucher-tree) | vouchers appended with their block; root and count recorded at each epoch start; the tree's definition; the share computed at each claim |
| 4 | High | [Proof of Work](../proof-of-work.md), [Bedrock Genesis Block](../bedrock-genesis-block.md), [details](#4-proof-of-work-state) | insertion into and pruning of `block_slots` and `pow_nullifiers`; the Genesis block in `block_slots` and out of the Blend difficulty's count |
| 5 | High | [Service Declaration Protocol](../bedrock-service-declaration-protocol.md), [details](#5-declarations-and-snapshots) | what a snapshot holds; `declarations` keyed by `declaration_id`; the field order |
| 6 | High | [Blend Protocol](../blend-protocol.md), [Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md), [details](#6-blend-reward-records) | the ledger records distances, not messages; when an epoch's rewards are not calculated; `Rewards^n` not stored |
| 7 | Medium | [Execution Market](../execution-market.md), [Storage Markets](../storage-markets.md), [Block Rewards](../block-rewards.md), [details](#7-fee-markets-and-the-pooled-fee-window) | starting values; the usage tally; one price update per ended epoch; the window's order |
| 8 | Low | [Bedrock Eras](../bedrock-eras.md), [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md), [details](#8-pointers) | skim: the definition and the checkpoint encoding now point to Bedrock Chain State |

# Discussion

## Decisions

The specifications did not define the recorded chain state precisely enough to encode it. Each point below records what the specifications said, what the implementation does, and what this change specifies. Each is open for review.

1. **The ledger.** Mantle declared `notes: list[Note]` and also "a dictionary mapping the NoteId to the note"; no declared state held a note's leaf position, which the ledger root depends on. Mantle reused leaves from "the list of unused leaves" without an order, and Proof of Leadership took "the first empty leaf". The implementation keeps `NoteId → (op_id, output_number, note, position)` and takes the smallest empty position. `notes` is that map, and the empty leaves follow from the occupied ones. `op_id` and `output_number` are kept, although no validation rule reads them: a wallet that restores from a checkpoint needs them for the leadership witnesses of its own notes. The `NoteId` key is carried and must equal its derivation.
2. **Order of maps and sets.** Ascending key, integers and field elements by value, other keys byte by byte. The implementation keeps most maps in hash tries with no order. Its own serialized note tree is ordered by leaf position; ordering `notes` by position instead is the alternative.
3. **Counts.** A `UINT64` count for every collection of the state, so `notes` can hold all 2<sup>32</sup> leaves. A structure that Mantle Transaction Encoding already defines, such as the `SDPDeclare` part of a declaration, keeps that encoding's widths.
4. **Derived and unread state is left out.** `service_notes` is derived from `declarations`. The SDP `events` index is read by no rule and not stored by the implementation.
5. **SDP snapshots.** The SDP specification snapshots "the SDP registry" and leaves exclusions to each service; Bedrock Eras recorded "the snapshots of the current and later epochs". The implementation holds exactly two, for the epoch of B and the next, each filtered to the declarations active for its epoch as of the last slot of the epoch two before. This change follows the implementation.
6. **Declaration field order.** Mantle, the SDP specification and the implementation used three different orders. Mantle's order is kept: its first five fields are the `SDPDeclare` payload, so the record reuses that encoding.
7. **The voucher tree.** The leader-reward specification and Block Construction appended a block's voucher "when the following epoch starts", and called the set both a depth-32 Merkle tree and an MMR frontier. The implementation appends every voucher with its block and records the root and the voucher count at each epoch start, which claims then use. Both select the same claimable vouchers. This change follows the implementation, and states the tree's leaves, empty value and node hash, which no specification gave. In epoch 0 the recorded root and count are 0, as in the implementation, not the root of an empty tree.
8. **The leader share.** The specifications did not say what `|voucher_cm|` counts or when the share is computed. The implementation computes it at each claim, from the voucher count recorded at the epoch start and the size of the nullifier set.
9. **Proof of work state.** Mantle declared `pow_nullifiers` a set, but each entry expires with the block its claim referenced, which needs that block's slot; `block_slots` was declared but read by no rule; and the acceptance window said a nullifier "may be discarded". The implementation maps each nullifier to the referenced block's slot, prunes both maps at every block, and checks claims against `block_slots`, which holds B and its ancestors within `WINDOW`, the Genesis block included. This change follows the implementation; pruning becomes a rule.
10. **Running values.** The specifications defined the epoch's leader rewards, Blend income, proof-of-work refill, block and transaction counts, and storage usage as sums over the blocks of an epoch. A checkpoint taken during an epoch cannot recompute them, so each is a component holding the sum up to B, as in the implementation.
11. **Blend reward records.** Blend said the active message "is stored on the ledger"; Service Reward Distribution said `Rewards^n` "is stored as an array". The implementation stores neither. It keeps a record of the previous epoch: the participants, the Hamming distance of each accepted activity proof, that epoch's income, and copies of that epoch's verification inputs, which a node cannot derive from the state at B. This change follows the implementation.
12. **Block Rewards' pending pool and reserve.** Block Rewards defines the pool balance $`P_t`$ and the reserve $`B_t`$, and caps the reserve release at $`B_{t-1}`$. Its own integer reference does not read either, and neither does the implementation. They are not components. If the cap is enforced, $`B_t`$ must become one, recorded from genesis.
13. **Market starting values.** The storage price starts at 1, as the implementation does, where Storage Markets also allowed "genesis governance" to set it; $`G_{avg}`$ starts at 0, which no specification stated; the storage price is updated once for each epoch that ended, an epoch without blocks using no storage.
14. **The pooled-fee window.** Oldest first, ending with B. The implementation keeps a ring indexed by block height, which would make the height a component.
15. **Layout version and digest.** A `UINT16` layout version leads the encoding, as the era parameter record does. The digest is Blake2b over the encoding, with the tag `CHAIN_STATE_V1`.

## Found but not changed

These defects surfaced while resolving the state. They concern rules rather than the shape of the state, so this change leaves them for separate review.

- [Proof of Leadership](../cryptarchia-proof-of-leadership.md) §Ledger Root computes the root height as `len(note_set).bit_length()`, which adds a level when the leaf count is a power of two, and bounds the leaf count below $`2^{32}`$ while stating a capacity of $`2^{32}`$.
- [Mantle](../bedrock-v1.1-mantle-specification.md) `SDP_DECLARE` step 5 compares a `ServiceType` with a list of declaration records, and reads `declaration.service_note` for the payload field `service_note_id`. The implementation rejects repeated locators; Mantle allows them. The SDP specification orders `DeclarationMessage` differently from Mantle and the wire grammar.
- [Execution Market](../execution-market.md) and [Storage Markets](../storage-markets.md) describe the fees routed to the reward pool before the proof-of-work share is diverted; [Block Rewards](../block-rewards.md) and the implementation route the net amount.
- Block Rewards' integer reference uses `int64`, which overflows once a block's fee exceeds about $`1.17 \cdot 10^{8}`$; the implementation uses 128-bit intermediates. Its formula pays the window average $`\bar{R}_t`$, while its code and the implementation pay the current block's fee.
- [Blend Protocol](../blend-protocol.md) names no source for the epoch randomness (the implementation uses the epoch nonce), divides the income without stating the rounding, and pays rewards "when epoch $`e+2`$ begins", where the implementation pays in the first block after epoch $`e+1`$, skipped epochs included.
- [Proof of Work](../proof-of-work.md) §Blend Difficulty does not say what happens when an epoch has no block before the snapshot; the implementation keeps the previous value.
- [Block Construction](../bedrock-v1.1-block-construction.md) §Block Execution lists three steps; the implementation also runs the block reward, both market updates and the running sums after the transactions.
- In the implementation: the leader and Blend running sums add without overflow checks; a full voucher tree and more than $`2^{20}`$ Blend participants cause a panic; and after a jump of two epochs `previous_epoch_nonce` may take the running nonce rather than the frozen one.

## Compatibility

Bedrock has not launched. Layout version 1 is the layout of era 0, and no existing state needs converting.

# Details

## 1. The component list and its encoding

[Bedrock Chain State](../bedrock-chain-state.md) is new. It lists the 28 components of layout version 1, each with a type and its value after a block B, and encodes them in that order after a `UINT16` layout version:

- ledger and services: `notes`, `channel_notes`, `channels`, `declarations`, `sdp_snapshot`, `next_sdp_snapshot`;
- leader rewards: `voucher_tree`, `last_voucher_root`, `last_voucher_count`, `voucher_nullifier_set`, `leaders_rewards`, `pending_leaders_rewards`;
- Blend rewards: `blend_target`, `blend_income`;
- proof of work: `pow_reward_pool`, `epoch_pow_reward`, `difficulty_reward`, `pow_pool_refill`, `pow_nullifiers`, `block_slots`, `epoch_tx_counts`, `closed_epoch_tx_counts`;
- fees: `execution_base_fee`, `average_execution_gas`, `permanent_storage_gas_price`, `storage_gas_average`, `storage_gas_used`, `pooled_fees_window`.

Encoding rules beyond Mantle Transaction Encoding: a collection is a `UINT64` count followed by its entries; sets and maps are in ascending order, integers and field elements by value and other keys byte by byte; an optional value is `0x00`, or `0x01` and the value; a decoder rejects unordered or repeated keys. `service_notes` is derived from `declarations`. The `NoteId` key of a `notes` entry must equal its derivation.

```python
def state_digest(encoded_state: bytes) -> Hash32:
    return hash(b"CHAIN_STATE_V1" + encoded_state)
```

## 2. The ledger

[Mantle](../bedrock-v1.1-mantle-specification.md) §Ledger:

```diff
 class Ledger:
-    notes: list[Note]
+    notes: dict[NoteId, LedgerNote]
     service_notes: dict[NoteId, ServiceNote]
     channel_notes: dict[NoteId, ChannelId]
```

Consuming a note empties its leaf. Creating a note records its `op_id`, output index and note, and fills the first empty leaf of the note tree, as [Ledger Root](../cryptarchia-proof-of-leadership.md#ledger-root) states. The sentence describing the notes as a dictionary is deleted, and `channel_notes` is described as the map it is declared as.

## 3. The voucher tree

[Anonymous Leaders Reward Protocol](../bedrock-anonymous-leaders-reward.md): validators append each voucher when they execute its block. In the first block of each epoch, before appending that block's voucher, they record the tree's root as `last_voucher_root` and its voucher count, and that epoch's claims use them. The tree is defined: depth 32, the vouchers in append order followed by zero leaves, each node the Poseidon2 compression of its children. `|voucher_cm|` is the recorded count, `|voucher_nf|` the size of the nullifier set, and the share is computed at each claim. The pool is named `leaders_rewards` throughout.

[Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) §Block Execution step 1 appends the block's voucher when the block is executed, not when the following epoch starts.

## 4. Proof of work state

[Mantle](../bedrock-v1.1-mantle-specification.md) §Proof of Work Operations and `CLAIM_POW_REWARD`:

```diff
-pow_nullifiers: set[zkhash]      # Spent solutions, retained for the acceptance window
+pow_nullifiers: dict[zkhash, SlotNumber]  # Spent ticket -> slot of the block its claim referenced
```

```diff
-block = get_block_from_hash(claim.block_hash)   # None if unknown or not canonical
-assert block is not None
-assert 0 <= current_slot - block.slot <= WINDOW
+assert claim.block_hash in block_slots
```

Execution step 1 inserts `puzzle_ticket` with the value `block_slots[claim.block_hash]`. The price the transaction fee reads is named `execution_base_fee` throughout Mantle, as the execution market and the implementation name it.

[Proof of Work](../proof-of-work.md) §Acceptance Window: before the transactions of a block at slot `s` run, its `block_id` is inserted into `block_slots` with the value `s`, and every entry of `block_slots` and `pow_nullifiers` whose slot is below `s - WINDOW` is removed. §Blend Difficulty counts the blocks of epoch N-2 without the Genesis block.

[Bedrock Genesis Block](../bedrock-genesis-block.md) §Mantle Ledger Initialization: `block_slots` holds the Genesis block at slot 0.

## 5. Declarations and snapshots

[Service Declaration Protocol](../bedrock-service-declaration-protocol.md):

- §Snapshots: the snapshot for epoch $`n`$ holds the declarations stored as of the last slot of epoch $`n-2`$, except those a service excludes from its participant set for epoch $`n`$;
- §Declaration Storage: `declarations: dict[DeclarationId, DeclarationInfo]`, keyed by `declaration_id`, and `DeclarationInfo` in Mantle's field order.

[Mantle](../bedrock-v1.1-mantle-specification.md) `SDP_DECLARE`: its `declarations` are keyed by the declaration identifier, not by `NoteId`.

## 6. Blend reward records

[Blend Protocol](../blend-protocol.md): for each accepted active message, the ledger records the Hamming distance of its activity proof under the sender's `provider_id`, and not the message. Reward Calculation step 1: an epoch's rewards are not calculated if the chain has no block in that epoch or the next, or if too few nodes are declared; an active message for such an epoch is rejected.

[Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md): the Blend Network's epoch rewards are its income $`I`$, and `Rewards^n` is paid in the block that computes it and is not stored.

## 7. Fee markets and the pooled-fee window

- [Execution Market](../execution-market.md): $`G_{avg}`$ is 0 before the first block.
- [Storage Markets](../storage-markets.md): the state variables include the usage tally $`C_{usage}`$, which each block adds to; the price update runs at the epoch boundary, once for each timeframe that ended, a timeframe without blocks using no storage; the initial price is the one in Protocol Constants.
- [Block Rewards](../block-rewards.md): `pooled_fees_window` holds the last $`T`$ values, oldest first and ending with the current block, and an entry for a height below 1 is 0.

## 8. Pointers

- [Bedrock Eras](../bedrock-eras.md) §Era Migration: the recorded chain state is the one Bedrock Chain State defines.
- [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) §Bootstrapping from Checkpoint: `checkpoint_ledger_state` carries the state after the checkpoint block, in that encoding.

## Chores

- Registered Bedrock Chain State in `scripts/blockchain_structure.py`.
- Mantle §Bridging calls `channel_notes` a map.
- The Anonymous Leaders Reward Protocol Overview diagram puts the Merkle tree before the wait for the next epoch, and calls the vouchers a share applies to "claimable".
- Anonymous Leaders Reward Protocol: `r &lt; n` renders as `r \lt n`.

# Implementation

- [ ] Encode the recorded chain state as layout version 1, and decode it, rejecting unordered keys and trailing bytes
- [ ] Give every map and set of the state the canonical order, in place of hash-trie and `HashMap` iteration
- [ ] Encode `pooled_fees_window` oldest first, and drop `block_number` from the encoded state
- [ ] Compute the state digest
- [ ] Add test vectors: a small state, its encoding and its digest
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Bedrock Chain State](../bedrock-chain-state.md) | Created | component list, encoding rules, layout version, state digest |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | ledger map with leaf positions, proof of work state and claim checks, `execution_base_fee`, `SDP_DECLARE` key |
| [Anonymous Leaders Reward Protocol](../bedrock-anonymous-leaders-reward.md) | Modified | voucher append and epoch-start record, tree definition, share |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | voucher appended with its block |
| [Proof of Work](../proof-of-work.md) | Modified | `block_slots` and `pow_nullifiers` maintenance, Genesis block not counted for the Blend difficulty |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | `block_slots` at Genesis |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | snapshot contents, `declarations` type, field order |
| [Blend Protocol](../blend-protocol.md) | Modified | recorded distances, when rewards are not calculated |
| [Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md) | Modified | Blend epoch rewards, `Rewards^n` not stored |
| [Execution Market](../execution-market.md) | Modified | starting $`G_{avg}`$ |
| [Storage Markets](../storage-markets.md) | Modified | usage tally, update timing, initial price |
| [Block Rewards](../block-rewards.md) | Modified | `pooled_fees_window` contents and order |
| [Bedrock Eras](../bedrock-eras.md) | Modified | recorded chain state defined by Bedrock Chain State |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | checkpoint state encoding |
