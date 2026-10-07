# [RFC] Mempool: Specify the mempool as implemented

**Motivation and proposal:** [PR #413](https://github.com/logos-co/logos-lips/pull/413)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-09-01 |
| v2 | Removed the retirement grace period and the retirement records, which nothing read. Reference resolution is now specified once, in this document, and linked from block construction. | 2026-09-02 |
| v3 | Review: dropped the admission-order tie-break, keyed retirement on entering the canonical chain rather than on becoming the tip, stopped a fork switch re-admitting transactions the adopted branch already carries, and gave the second reason admission is stateless. | 2026-09-04 |
| v4 | Chores checked against the implementation at `4e0405d51`: added the missing stateless validation, the fork-switch re-admission set and the TTL configurability, and corrected two Chores that overstated what the code does. | 2026-09-04 |
| v5 | Recorded the mempool entry point a Blend Protocol revision adds, and what the admission, decoding and broadcast rules would each need to say for it. | 2026-09-04 |
| v6 | Laid the document out like the other specifications: timeline, overview, and the rules under one Construction heading. Heading text and anchors are unchanged. | 2026-09-09 |
| v7 | Removed text the document already carried: the overview no longer re-lists how a transaction enters and leaves, block building no longer states a retirement rule retirement states, and resolution no longer restates the procedure above it. | 2026-09-10 |
| v8 | Moved the submission to the current template. This document now holds everything except Motivation and Proposal. The implementation departures, formerly Chores, and the open issues moved under Discussion, and Details no longer restate the rationale Discussion gives. | 2026-10-07 |
|  | Review: Open Issue 10 now points at #448, which closes it, and lost its argument against closing it, which held only if the pending set did not already depend on the node's branch. Removed the claim that unique matching makes proposal acceptance independent of node-local history. | 2026-10-07 |
|  | Added the departure in which the implementation resolves references before it checks the parent, checked at `cad13d0d9`, with its implementation task. Linked the implementation PRs of two tasks. | 2026-10-07 |
|  | Merged master, and moved the specification to slug 251 after master gave 245 to Proof of Work. | 2026-10-07 |
| v9 | Review: moved the rule that a fork switch re-admits a transaction at its original admission time to [#448](https://github.com/logos-co/logos-lips/pull/448), which keeps that time past retirement. Retirement discards it here before a fork switch needs it, so this document could not honour the rule. | 2026-10-07 |
|  | `admit` lost its `at` argument and `pending` is an insertion-ordered set again, as implemented. Removed the departure, its implementation task and its test, and added Open Issue 14. | 2026-10-07 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mempool](#affected-specifications): [Reference resolution](#1-reference-resolution) | Resolution succeeds only on a unique prefix match, and reads the proposal, `by_prefix` and `bodies` and nothing else. Check that no other state can enter it. |
| 2 | Critical | [Mempool](#affected-specifications): [Block building](#2-block-building) | Retirement lists three reasons a transaction leaves, and selection is not among them. Check that a transaction which merely did not fit stays resolvable. |
| 3 | High | [Mempool](#affected-specifications): [Admission](#3-admission) | Stateless by design: no ledger reads. Confirm the `preverify` subset matches Mantle's rules, including `None` proof entries. |
| 4 | High | [Mempool](#affected-specifications): [Retirement and persistence](#4-retirement-and-persistence) | Retirement is not rejection, and it clears every per-transaction map. |
| 5 | High | [Block Construction, Validation and Execution](#affected-specifications): [Resolution moves to the mempool](#5-block-construction-links-to-the-mempool) | What block construction keeps is its own, and nothing it removed is lost. |
| 6 | Medium | [Mempool](#affected-specifications): [Dissemination](#6-dissemination) | Payload-digest message identity, and relay preceding admission. |
| 7 | Medium | [Mempool](#affected-specifications): [Mempool State](../mempool.md#mempool-state) and [Constants](../mempool.md#constants) | Only constants this specification owns are defined here. The rest are referenced. |
| 8 | Low | [Mempool](#affected-specifications): [Node API](../mempool.md#node-api) | Skim. |

# Discussion

## Why admission is stateless

Admission could check a transaction against the node's ledger state and reject what cannot be applied. It does not, for two reasons.

The first is view uniformity, not cost. A stateful rule makes mempool contents a function of chain state. Two nodes on different branches would then decide differently about the same transaction. Every such disagreement is a proposal that some validators can reconstruct and others cannot, for reasons unrelated to its validity.

The second is that transactions depend on each other. If `tx2` spends a note `tx1` creates and `tx2` arrives first, a stateful check rejects it although nothing is wrong with it. Arrival order is not dependency order. Judging `tx2` correctly means applying the other pending transactions first, which is the applicability fixpoint of block building run once per arrival instead of once per block. Stateful admission is therefore either wrong about dependent transactions, or block building repeated on every gossip message.

The price is that the mempool holds transactions that can never be applied, at no charge to whoever submitted them. Only `MAX_BLOCK_SIZE` and `TRANSACTION_TTL` bound them.

## Rationale for individual rules

The specification states rules only. The reasoning behind them is recorded here.

- **Unique-match reference resolution.** A non-unique match is reported as unresolved rather than searched, so resolution never branches and never depends on scan order.
- **Resolution follows header authentication.** A mempool scan is the expensive step in accepting a proposal, and a proposal is unauthenticated below its header.
- **Applicability separated from selection.** Only the applicability fixpoint retires transactions. A transaction that merely did not fit in a block is one another leader can validly include. Evicting it would stop this node from resolving that leader's reference to it.
- **Retirement clears every per-transaction map.** A map that retirement did not clear would grow for the node's lifetime and, being persisted, across restarts.
- **Payload-digest message identity.** Gossipsub's default source-and-sequence identity would let every re-publisher mint a fresh identity for the same bytes, which defeats suppression at the router.
- **`by_prefix` is rebuilt rather than persisted.** A change to `REFERENCE_PREFIX_LENGTH` then takes effect on restart, and an index built under the previous value cannot contradict it.

## Where the specification departs from the implementation

This document describes what runs. It departs from the implementation only where the current behaviour is not defensible as a design. Each departure is listed below, with its task under [Implementation](#implementation). Everything else that differs from an ideal mempool stays an [open issue](#open-issues), so the specification and the code can be compared line by line.

The entries were checked against `logos-blockchain` at `4e0405d51`: `services/tx-service`, with the block-building and block-applied halves in `services/chain/chain-leader` and `services/chain/chain-network`. The header-validation and grace-period entries were checked at `cad13d0d9`.

- **Header validation precedes resolution.** [Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) checks the parent's presence and the proof of leadership in step 2, before reconstruction in step 4. The implementation resolves references after checking only the latest-immutable-block bound, the genesis slot and the signature. It finds a missing parent only when it applies the reconstructed block. A proposal whose references do not resolve is therefore dropped before its missing parent is noticed, and it never reaches the orphan path. A proposal with an invalid proof of leadership also costs a mempool scan.
- **Stateless validation.** `preverify` has no counterpart. The whole of admission validation is a size bound. No proof is counted, type-checked or verified anywhere on the ingress path, and verification first happens when the ledger applies a transaction. The pool therefore holds transactions nobody has shown to be well-formed beyond decoding, and a peer can fill it with proofless ones at no cost. This is the one place where the document specifies a check rather than describing one.
- **Size before verification.** The size bound is checked on the raw payload before decoding. The implementation checks it on the decoded transaction, so the bound does not limit the cost of decoding an oversized payload.
- **Retirement follows the canonical chain, not the tip.** Retiring on "becomes the tip" only reaches the new head of an adopted branch. The blocks beneath it were applied while that branch was losing. They become ancestors without ever being the tip, so their transactions stay pending while being canonical.
- **A fork switch re-admits only what the adopted branch does not carry.** Re-admitting every transaction of every displaced block puts back transactions that are canonical again. Competing branches select from similar mempools, so the overlap is routine.
- **Retirement discards the body.** The implementation keeps a retired body for a ten-minute grace period, but retirement removes the hash from the prefix index at once. Since [logos-blockchain#3251](https://github.com/logos-blockchain/logos-blockchain/pull/3251), no resolution reads the retained body, so the timer only delays its deletion. [#448](https://github.com/logos-co/logos-lips/pull/448) brings retention back together with the rule that reads it.
- **`TRANSACTION_TTL` is a constant.** The implementation carries it as a configuration value that can be set to disable expiry altogether, which leaves a node with no eviction at all.

## Open issues

Recorded here rather than in the specification.

1. **No attestation that a transaction reached the network.** [Blend Protocol](../blend-protocol.md#privacy-of-proof-of-stake-systems) states that its network-level protection is not sufficient alone, and defers the other half to the mempool: a node should hold "an attestation that the transaction was seen by the majority of the network". Nothing here supplies it, so a selectively delivered transaction is proposed like any other and identifies its proposer.
2. **A transaction has no defined end of life.** `TRANSACTION_TTL` is a local eviction policy, not a property of the transaction. Nodes drop the same transaction at different moments, and a submitter can never conclude an in-flight transaction is dead.
3. **Expiry has no independent clock.** The implementation evaluates expiry only when a block is applied, so a stalled or partitioned node retains everything.
4. **Relay precedes validation.** A malformed transaction is amplified network-wide before any node rejects it. Deferring relay until after validation would close the amplification, at the cost of one validation per hop.
5. **Content-addressed suppression does not suppress re-proved copies.** `mantle_txhash` covers `MantleTx`, not `op_proofs`, and Groth16 proofs are re-randomizable. An adversary can therefore mint unlimited byte-distinct copies of one transaction, each with a fresh payload digest and so a fresh message identity, each relayed to the mesh before admission decodes it. Keying message identity on the transaction hash, which is computable from the payload, would collapse them, at the cost of decoding before relaying.
6. **No capacity bound.** `pending` grows without limit. `TRANSACTION_TTL` bounds how long a transaction is held, not how many are held.
7. **The applicability fixpoint is superlinear in an unbounded set.** Repeated passes until nothing applies is quadratic in `pending` in the worst case, each apply verifies the state-bound proofs that admission deliberately skips, and the leader has one slot to finish. Bounding the input to the fixpoint, or the number of passes, would bound the cost. Neither is specified.
8. **Inapplicability retirement is only reachable on a leader.** The applicability determination runs when a node builds a block, at the rate the stake lottery grants it. For a node that rarely leads, TTL is the only eviction. A transaction is also retired the first time a fixpoint fails to apply it, even though the transaction creating its input may simply not have arrived yet.
9. **No fee-aware selection.** [Execution Market](../execution-market.md#block-builder-mechanism-block-construction) specifies filtering by base fee and ordering by revenue. The view is ordered by admission time and carries no fee information.
10. **A retired transaction cannot resolve a reference.** A node that has included a transaction on its own branch cannot reconstruct a competing branch's proposal that references it, until a fork switch re-admits it. Competing leaders select from similar mempools, so most forks between non-empty blocks hit this. [#448](https://github.com/logos-co/logos-lips/pull/448), stacked on this PR, closes it: an included transaction stays resolvable until its block becomes immutable.
11. **Re-admission of included transactions.** A transaction already in a canonical block can be gossiped back in, and it occupies space until block building finds it inapplicable or its TTL expires. [#448](https://github.com/logos-co/logos-lips/pull/448) makes its hash a duplicate until its block is immutable.
12. **No periodic re-broadcast.** A transaction lost by the gossip layer is not retried until the submitter resubmits it.
13. **The entry points are a closed list, and a fourth is coming.** [Transaction Admission](../mempool.md#transaction-admission) enumerates three ways a transaction reaches the pool, and the broadcast rule keys on which of them it arrived by. A [Blend Protocol](../blend-protocol.md) revision adds transactions as a second data-message payload, which the core node that unwraps one submits to its own mempool. That is a fourth entry point, and Blend itself broadcasts its transactions. Three things then need saying that the document currently leaves implicit. The broadcast rule reaches the right answer only by omission: Blend delivery is neither local submission nor re-insertion, so nothing is disseminated twice, but that holds by accident rather than by statement. [Decoding](../mempool.md#decoding) describes one transaction in the Network Wire Format envelope, where a Blend payload body carries a sequence of them. And the two paths admit different sizes: `MAX_BLOCK_SIZE` here, against a fixed Blend payload body two orders of magnitude smaller, so a transaction this document would admit may not be sendable over Blend at all.
14. **A fork switch re-admits a transaction at the current time.** Retirement has already discarded its admission time, so the transaction goes to the end of `pending`, behind everything admitted since. Selection carries no fee signal that could buy the position back. [#448](https://github.com/logos-co/logos-lips/pull/448) keeps the time until the block is immutable, and re-admits the transaction at the position that time gives it.

# Details

The [Mempool](../mempool.md) specification is the single source of truth. The entries below name each mechanism in review order and link to it.

## 1. Reference resolution

[Reference Resolution](../mempool.md#reference-resolution). A reference is a `REFERENCE_PREFIX_LENGTH`-byte prefix of the transaction hash. It resolves only when the match is unique. Zero matches means this node does not hold the transaction, and two or more would be a prefix collision. Both are reported as unresolved and are not searched. Resolution reads the proposal and the mempool alone, and runs only after the decode-time bounds checks and header authentication.

## 2. Block building

[Block Building View](../mempool.md#block-building-view). Block building makes two separate determinations. **Applicability** is a fixpoint over all pending transactions against the working ledger state, repeated until a pass applies nothing new, which resolves dependencies within a block. A transaction that never becomes applicable is invalid against this branch, and is retired. **Selection** then fills the block from the applicable set, up to `MAX_BLOCK_TXS` and `MAX_BLOCK_SIZE`, and retires nothing.

## 3. Admission

[Transaction Admission](../mempool.md#transaction-admission). Admission checks the size of the raw payload, then decodes it, requiring full consumption, then applies Mantle's stateless validation, then checks for a duplicate. Stateless validation requires one proof entry per operation, with `None` where the opcode admits it, the proof type each opcode requires, and a valid proof wherever the proof binds only the transaction hash and the operation payload. Admission reads no ledger state. A pending transaction is therefore **well-formed, not valid**, and membership must never be taken as evidence that it can be applied.

## 4. Retirement and persistence

[Retirement](../mempool.md#retirement), [Reorganisation](../mempool.md#reorganisation) and [Persistence and Recovery](../mempool.md#persistence-and-recovery). A transaction is retired when a block that carries it enters the canonical chain, when the applicability fixpoint never applies it, or when its age exceeds `TRANSACTION_TTL`. Retirement clears every per-transaction map, the body included. Retirement is **not** rejection: a re-gossiped copy is admitted again. A fork switch re-admits the displaced transactions the adopted branch does not carry. A node persists the pending hashes, their admission times and the bodies, and rebuilds the prefix index on recovery.

## 5. Block construction links to the mempool

[Reference Resolution](../bedrock-v1.1-block-construction.md#reference-resolution) in block construction defined the same procedure, as a scan of every held transaction. It now links to the mempool's procedure, which reads the prefix index. Block construction keeps what is its own: the collision argument, the body-root check, repeated references, and what a failed resolution establishes about the block. This is its revision 1.3.1.

```diff
 # Block Construction, Validation and Execution, removed
-def resolve(reference, mempool):
-    matches = [tx for tx in mempool
-               if prefix(mantle_txhash(tx), REFERENCE_PREFIX_LENGTH) == reference]
-    return matches[0] if len(matches) == 1 else None
 # Mempool, the procedure block construction now links to
+def resolve(mempool, reference) -> Optional[SignedMantleTx]:
+    matches = mempool.by_prefix.get(reference, empty_set)
+    if len(matches) != 1:
+        return None
+    return mempool.bodies[single(matches)]
```

## 6. Dissemination

[Dissemination](../mempool.md#dissemination). Message identity on the mempool topic is the Blake2b-256 digest of the payload, not gossipsub's source-and-sequence default. A node relays a received message to its mesh before admission. It broadcasts a transaction it admits by local submission or by re-insertion, and not one it received by gossip.

## Chores

- Registered the Mempool document in `scripts/blockchain_structure.py`, under Mantle.

# Implementation

- [ ]  Run step 2 of Block Proposal Validation, the parent's presence and the proof of leadership included, before reference resolution, so a proposal whose parent is missing reaches the orphan path
- [ ]  Apply `preverify` at admission: one proof entry per operation, the type each opcode requires, and the self-contained proofs verified
- [x]  Move the mempool size check ahead of decoding
- [ ]  Retire the transactions of every block that enters the canonical chain, not only those of the new tip ([logos-blockchain#3734](https://github.com/logos-blockchain/logos-blockchain/pull/3734))
- [ ]  Exclude the transactions the adopted branch carries when a fork switch re-admits displaced ones ([logos-blockchain#3746](https://github.com/logos-blockchain/logos-blockchain/pull/3746))
- [ ]  Decide whether expiry may be disabled by configuration, and pin `TRANSACTION_TTL` if not
- [x]  Confirm the gossipsub message-id function on the mempool topic is the payload digest, and register the topic and its message-id in the P2P Network specification
- [ ]  Reconcile the mempool status and metrics endpoints with the Node API section
- [ ]  Add or extend tests that exercise the change: admission ordering, resolution uniqueness, retirement clearing, restart recovery, and a proposal with a missing parent and unresolvable references reaching the orphan path
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mempool](../mempool.md) | Created | New specification. |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | Reference resolution is linked to the Mempool instead of restated (1.3.1). |
