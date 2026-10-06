# [RFC] Cryptarchia: Specify what a checkpoint carries

**Motivation and proposal:** [PR #475](https://github.com/logos-co/logos-lips/pull/475)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |

## Reviewer Orientation

Read the PR's Motivation first. The recorded chain state a checkpoint carries is defined in [Bedrock Chain State](../bedrock-chain-state.md), and this change leaves it as it is.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md), [details](#1-checkpoint-contents) | each consensus value against its reader; any value a block after the checkpoint reads before it that the list misses; the reach of `recent_blocks`; when the next epoch's nonce is present |
| 2 | Critical | [Cryptarchia Protocol](../cryptarchia-v1-protocol.md), [details](#2-epoch-states-after-a-checkpoint) | the epoch-state recursion ends at the carried states; reads at or before the checkpoint block take carried values |
| 3 | High | [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md), [details](#3-checkpoint-provider-http-api) | the third part of the `GET /checkpoint` response |

# Discussion

## Decisions

Each point is open for review.

1. **A third part.** The consensus state travels beside the recorded chain state, not inside it. A migration transforms the recorded chain state, while epoch values are derived under the rules of each epoch's era ([Era Migration](../bedrock-eras.md#era-migration)). Both parts use the same encoding rules.
2. **Epochs $`e-1`$ and $`e`$ are carried; epoch $`e+1`$ is derived where it can be.** Of the four values of epoch $`e+1`$, $`\mathbb{C}_\text{LEAD}`$ is the ledger root of the carried aged notes, $`D`$ follows from the $`D`$ of epoch $`e`$ and the carried occupied slots, and `difficulty_blend` follows from that of epoch $`e`$ and the closed epoch counts the recorded chain state holds. Only the epoch nonce cannot be rebuilt once fixed, because the running nonce moves on, so it is carried from then on.
3. **Epoch $`e-1`$.** An uncle referenced after the checkpoint can have its parent in epoch $`e-1`$ when the checkpoint block lies within $`W \cdot f^{-1}`$ slots of the start of epoch $`e`$, and a proof-of-work claim accepts the previous epoch's nonce. The implementation keeps only that nonce, and validates uncles from the state it holds for each block; a node started from a checkpoint has no such states. The checkpoint carries the whole epoch state of epoch $`e-1`$, but not its `difficulty_blend`, which `blend_target` already holds.
4. **Aged note sets.** The implementation keeps the aged note sets of the current and the next epoch (`EpochState.utxos`), and proving leadership needs Merkle paths in them. Carrying them lets a node started from a checkpoint lead at once. The alternative carries only their roots, and the node leads from epoch $`e+2`$, the first whose aged notes it observes itself. Each set is a full note map, the size of `notes`.
5. **Lottery constants.** They are derived from $`D`$, as [Proof of Leadership](../cryptarchia-proof-of-leadership.md) defines them. The implementation stores them as well.
6. **The reach of `recent_blocks`.** A block $`A`$ after the checkpoint block $`B`$ has $`sl_A \gt sl_B`$, and an uncle's parent precedes $`A`$ by at most $`W \cdot f^{-1}`$ slots. So every parent an uncle check after $`B`$ can reach has a slot greater than $`sl_B - W \cdot f^{-1}`$, and no older block is carried.
7. **Types.** $`D`$ is a `UINT64`, as `total_stake_inference` computes it. `difficulty_blend` and the nonces are field elements.

## Open questions

- No canonical byte encoding of a `Block` is specified, so `checkpoint_block` has none.
- Nothing in a checkpoint lets the node check the consensus state. It trusts the provider, as it trusts the recorded chain state.
- A checkpoint carries the note set three times: the current notes and two aged sets. The aged sets differ from the current notes only by the notes created and spent since, so encoding the differences would shrink them.

## Compatibility

No implementation serves or imports checkpoints yet, and Bedrock has not launched.

# Details

## 1. Checkpoint contents

[Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) §Checkpoint Contents is new. A checkpoint for a block $`B`$ of epoch $`e`$ has three parts: the block, the recorded chain state after it, and the consensus state:

- `epoch_nonce`: the epoch nonce after $`B`$;
- `previous_epoch`: the epoch state $`(\mathbb{C}_\text{LEAD}, \eta, D)`$ of epoch $`e-1`$, absent in epoch 0;
- `current_epoch`: the aged notes, $`\eta`$, $`D`$ and `difficulty_blend` of epoch $`e`$;
- `next_epoch`: the aged notes of epoch $`e+1`$, and its nonce once fixed;
- `occupied_slots`: the slots counted so far for $`N_\text{BLOCKS}`$ of epoch $`e`$;
- `recent_blocks`: block id, slot and ledger root of the blocks of the chain whose slot is greater than $`sl_B - W \cdot f^{-1}`$.

```schema
ConsensusState   = EpochNonce PreviousEpoch CurrentEpoch NextEpoch OccupiedSlots RecentBlocks
PreviousEpoch    = %x00 / %x01 PastEpoch          ; absent when e is 0
PastEpoch        = LeadRoot Nonce TotalStake
CurrentEpoch     = AgedNotes Nonce TotalStake BlendDifficulty
NextEpoch        = AgedNotes NextNonce
NextNonce        = %x00 / %x01 Nonce              ; present once fixed
RecentBlock      = BlockId BlockSlot LedgerRoot
```

The aged notes of epoch $`n \ge 1`$ are the `notes` as of the first slot of epoch $`n-1`$, and their ledger root is the epoch's $`\mathbb{C}_\text{LEAD}`$. §Bootstrapping from Checkpoint: the node imports the three parts.

## 2. Epoch states after a checkpoint

[Cryptarchia Protocol](../cryptarchia-v1-protocol.md) §Epoch State Pseudocode gains one paragraph. A node that bootstrapped from a checkpoint for a block $`B`$ holds no block before $`B`$. It takes every value that the pseudocode or [Uncle References](../cryptarchia-v1-protocol.md#uncle-references) reads at or before $`B`$ from the checkpoint, and `compute_epoch_state` returns the carried epoch state for the epoch of $`B`$ and the epoch before it.

## 3. Checkpoint Provider HTTP API

```diff
                                     checkpoint_ledger_state:
                                         type: string
                                         format: binary
+                                    checkpoint_consensus_state:
+                                        type: string
+                                        format: binary
```

# Implementation

- [ ] Build the consensus state at the checkpoint block: the running epoch nonce, the epoch states of the previous and current epoch, the aged note sets, the next epoch's nonce once fixed, the occupied slots and the recent blocks with their ledger roots
- [ ] Serve `checkpoint_consensus_state` from `GET /checkpoint`, and import all three parts
- [ ] Start the epoch-state derivation, the epoch nonce, the stake inference and uncle validation from the carried values
- [ ] Add tests that bootstrap from checkpoints before and after the next epoch's nonce snapshot, and within $`W \cdot f^{-1}`$ slots of an epoch start, and check that the node accepts and rejects the same blocks as a node synchronized from genesis
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | checkpoint contents, consensus state, `GET /checkpoint` response |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | epoch states and uncle checks after a checkpoint |
