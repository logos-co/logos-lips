# [RFC] Block Construction: Validate the header before resolving references

**Motivation and proposal:** PR #TBD

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-21 |

## Reviewer Orientation

Single-document change — read [Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) top to bottom, and focus on steps 2 and 3, which now run before reconstruction.

# Discussion

## Why the header is checked before the mempool

A mempool scan is the expensive step in accepting a proposal, and a proposal is unauthenticated below its header. [Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) therefore checks every rule of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation) that reads no transactions before it resolves a reference.

Until this change it described what `logos-blockchain` does at `60744b8e7`. Before reconstruction the implementation checks only that the slot is later than the latest immutable block's and is not the genesis slot, that its block tree does not already hold the block, and the signature. It finds a missing parent only when it applies the reconstructed block. Two things follow:

- A proposal whose parent is missing and whose references do not resolve is dropped before the missing parent is noticed. It never reaches the orphan path of [Listening for New Blocks](../cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks), so the node does not download the missing blocks.
- A proposal with an invalid proof of leadership costs a mempool scan before it is rejected.

Checking the header first costs a proof-of-leadership verification for every proposal that passes the signature check, including one whose references would not resolve. The current order drops such a proposal without that verification.

## The orphan path is not stated

Block Proposal Validation rejects a proposal that fails any check, and it records which rejections condemn the block. It does not mention a missing parent. Only [Listening for New Blocks](../cryptarchia-v1-bootstr-sync.md#listening-for-new-blocks) says that a block whose parent is missing is an orphan, whose missing blocks the node downloads. Step 2 could state that a proposal whose parent the block tree lacks fails without a verdict and is handled as an orphan. This RFC leaves that open.

# Details

## Header and uncle validation precede reconstruction

[Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) checks rules 1 and 5 through 9 of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation) in step 2, the parent's presence and the proof of leadership included, and the uncle rule, rule 10, in step 3. Reconstruction becomes step 4 and keeps the size rule, rule 2. The step that applied Block Header Validation to the reconstructed block goes, since every rule it applied now runs before reconstruction or in it. This is revision 1.5.0 of [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md).

```diff
-2. **Header Authentication**
-  The `header` must name a slot later than the slot of the [Latest Immutable Block](cryptarchia-v1-protocol.md#latest-immutable-block), and not the genesis slot. It must not name a block that the node's block tree already holds. `signature` must verify under the leader key that the header's proof of leadership commits to, which is the second condition of rule 9 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation).
+2. **Header Validation**
+  The `header` must satisfy the rules of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) that range over the header and the block tree alone: the bedrock version, the slot ordering against the parent, the wallclock check, the presence of the parent in the block tree, the height against the latest immutable block, and the leader's right to propose — that is, rules 1 and 5 through 9.
+3. **Uncle Validation**
+  Every entry of `uncle_headers` must be a valid uncle of the block, which is rule 10 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) (see [Uncle References](cryptarchia-v1-protocol.md#uncle-references)).
 
-3. **Block Proposal Reconstruction**
+4. **Block Proposal Reconstruction**
 
-4. **Block Validation**
-  With `transactions` now available, the reconstructed block must satisfy [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) as written.
-
 5. **Mempool Transactions Validation**
```

The paragraph after the steps counts an invalid uncle entry, step 3, among the failures that discard only the received copy, and cites the other steps by their new numbers. The note on the cost of reconstruction says it follows signature and PoL verification.

# Implementation

- [ ]  Run steps 2 and 3 of Block Proposal Validation, the parent's presence and the proof of leadership included, before reference resolution, so a proposal whose parent is missing reaches the orphan path
- [ ]  Add or extend tests: a proposal with a missing parent and unresolvable references reaches the orphan path, and a proposal with an invalid proof of leadership is rejected before any mempool lookup
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | Header and uncle validation precede reconstruction (1.5.0). |
