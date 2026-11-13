# [RFC] Block Construction: Recover from a bad copy of a transaction

**Motivation and proposal:** [PR #523](https://github.com/logos-co/logos-lips/pull/523)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Block Construction, Validation and Execution](#affected-specifications): [A failed copy records no verdict](#1-a-failed-copy-records-no-verdict) | Both failures must come from bytes that `block_id` does not cover. A forged header must not trigger a download. |
| 2 | Critical | [Block Construction, Validation and Execution](#affected-specifications): [A block received in full](#2-a-block-received-in-full) | A peer serving a tampered copy must not get a block condemned, and a block that is really invalid must still not be adopted. |
| 3 | Medium | [Mempool](#affected-specifications): [A block's copy replaces the node's](#3-a-blocks-copy-replaces-the-nodes) | Only a block the node has validated replaces a copy. |

# Discussion

## What a copy can change

The hash covers `MantleTx` and not `op_proofs`, so two copies of one hash differ only in their proofs. Three things read those bytes: the proof checks, rule 2 of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation), and the permanent storage fee in [`mandatory_fees`](../bedrock-v1.1-mantle-specification.md#mantle-transaction-fee), which reads `len(encode(signed_tx))`.

The fee cannot split nodes. Copies that pass the proof checks have one length: a `ZkSignature` is 128 bytes, an `Ed25519Signature` is 64, and [`MultiEd25519_verify`](../bedrock-v1.1-mantle-specification.md#multiple-ed25519-signatures-verification) takes exactly `threshold` signatures. Rule 2 of Mantle's [Validation](../bedrock-v1.1-mantle-specification.md#validation) checks the proofs before rule 3 checks the fee, so a padded copy fails on its proof and not on its fee. A re-randomized proof gives another valid copy of the same length, and no state reads its bytes.

## Why the node downloads the block, and when

Without a download, the block reaches the node only when a later block names it as parent. With $`f = 1/30`$ and one second per slot, that takes about 30 seconds on average. A download takes one round trip to a peer that already holds the block.

The download comes after rule 9, since a proposal is unauthenticated below its header and a forged header must not cost a request. A failed proof comes in step 5, after step 4 has checked rule 9. The size failure comes in step 3, before step 4, so the node checks rule 9 at that point.

A peer holds the block once it has adopted it, so a node that asks too early may have to ask again. The orphan path already allows this through its retry policy.

## Compatibility

Block validity does not change, and no format changes. What a node records and when it downloads are local to it, so nodes can adopt this change one at a time.

## Alternatives

- **Check the state-bound proofs at admission.** Admission reads no ledger state, because a stateful rule makes the contents of a mempool depend on the node's branch, and because transactions can depend on each other. A copy of a transaction that spends an output of another pending transaction could not be checked anyway, so a recovery path is still needed.
- **Commit to the proofs in `references` or `body_root`.** A block would then name one exact copy, as compact block relay in Bitcoin does with witness hashes (BIP 152). This changes the header commitment and the proposal. Groth16 proofs can be re-randomized, so an honest node holding another valid copy would miss the reference, and would need the same download.
- **Keep several copies of a hash and try each.** A peer can send any number of copies, so a fixed number of slots fills up first, and each try costs a proof verification. One slot per peer would hold, at a memory cost of the mesh size, and a node holding no good copy still needs the download.
- **Discard the copy when its proof fails.** A later proposal would then fail to resolve its reference, and that path has no download. A proof can also fail on one branch and hold on another, since channel keys are state. The node therefore keeps its copy until a validated block replaces it.

## What remains

- **A leader holding a bad copy does not include that transaction.** Its block building finds the copy inapplicable and retires it. Gossip does not bring the honest copy back, since each node remembers a message identity for `SEEN_TTL`. Other leaders can still include the transaction, and a sender can change the transaction to give it a new hash.
- **A bad copy still costs a download.** A peer that pays one fee per block can make the nodes holding its bad copy download that block, up to `MAX_BLOCK_SIZE` each. Those blocks lose the saving of compressed proposals, and nothing more.
- **An invalid block gets no verdict.** A block whose proof fails in every copy is never adopted and never condemned, so a node validates it again each time a peer sends it. Each such block needs a winning proof of leadership. An implementation can remember failures by a digest of the whole block, and not by `block_id`.
- **A leader that wins during the download extends the parent,** like any node that has not received the block yet.

## How this was checked

A model runs `admit`, `resolve`, `retire` and `reorganise` as [Mempool](../mempool.md) writes them, with Block Proposal Validation written from this text. 28 directed checks pass. They cover a bad copy, a copy padded to 2,097,120 bytes, a forged header, a peer serving tampered blocks, a block whose proof fails in every copy, a state failure, a sibling proposal and a fork switch.

A randomized run used 8 nodes, 30 blocks and 200 seeds, with half of the transactions attacked and each node taking the bad copy first with probability 1/2. That is a heavy attack, and the model has no network timing, so only the comparison means anything.

| Behaviour | Nodes more than 1 block behind at the end, of 1,600 | Genuine blocks recorded as rejected | Download requests |
| --- | --- | --- | --- |
| Specification before this change | 52 | 0 | 16,510 |
| `logos-blockchain` at `ce15ec15e1`, modelled from its code | 486 | 14,927 | 10,432 |
| This change | 0 | 0 | 26,565 |

No part of this ran on a node.

# Details

## 1. A failed copy records no verdict

[Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) gains a paragraph after the one on what a rejection establishes. This is revision 1.5.0 of [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md).

```diff
+`block_id` and `header.body_root` cover the hash of each transaction, and that hash covers no `op_proofs` ([Mantle Transaction Hash](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash)). A node's copy of a transaction can therefore fail where the proposer's copy holds. Two failures can come from those bytes alone: a failed proof in step 5, and resolved transactions that reproduce `header.body_root` but exceed `MAX_BLOCK_SIZE` in step 3. On either failure the node records no verdict against `block_id`. If the header satisfies rule 9 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation), the node downloads the block in full, as it does for an orphan block ([Listening for New Blocks](cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks)).
```

## 2. A block received in full

The same section's last paragraph gains one sentence.

```diff
 This ordering is specific to the proposal path. [...] with no ordering constraint.
+Those transactions are the copies of the serving peer, so a failure of rule 2 or a failed proof records no verdict against `block_id` either.
```

## 3. A block's copy replaces the node's

[Inclusion in a Canonical Block](../mempool.md#inclusion-in-a-canonical-block) gains the replacement. [Node State](../mempool.md#node-state) adds it to what changes `bodies`, and [Proposal References](../mempool.md#proposal-references) says that a reference resolves to the node's own copy. This is revision 1.1.0 of [Mempool](../mempool.md).

```diff
-When a block enters the node's canonical chain, each pending transaction it carries is retired.
+When a block enters the node's canonical chain, each pending transaction it carries is retired. The block's copy of each transaction it carries replaces the copy in `bodies`, if the mempool holds one.
```

# Implementation

- [ ]  Keep a failed proof apart from other failures when a block is applied: `verify_batch_proofs` in `services/chain/chain-service/src/lib.rs` and the checks that run during the transactions end in `ApiError::Unexpected(String)`
- [ ]  Do not add a block ID to `rejected_blocks` for a failed proof or a size failure, in `handle_proposal_processing_error` and in the orphan download branch of `services/chain/chain-network/src/lib.rs`
- [ ]  After a failed proof of a proposal, enqueue the block for download through `OrphanBlocksDownloader`
- [ ]  Do the same after `ContentTooBig` in `Block::reconstruct` when the body root matches and rule 9 holds; `Block::reconstruct` checks the size first, so it has to compute the root as well
- [ ]  Store a block's copies in the mempool when the block enters the canonical chain, in `services/tx-service`
- [ ]  Add or extend tests: a node holding a bad or padded copy adopts the genuine block and rejects nothing, a peer serving a tampered block does not get it rejected, a forged header triggers no download, and a sibling proposal resolves to the block's copy
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | A failed proof of a resolved transaction records no verdict, and the node downloads the block in full (1.5.0). |
| [Mempool](../mempool.md) | Modified | A block's copy replaces the node's when the block enters the canonical chain (1.1.0). |
