# [RFC] Cryptarchia: Reference any fork block as an uncle

**Motivation and proposal:** [PR #558](https://github.com/logos-co/logos-lips/pull/558)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first. The [Cryptarchia Fork Choice Rule](../fork-choice.md) is unchanged and assumed.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [entries and adoptable chains](#1-entries-and-adoptable-chains) | a missing or wrong uncle delays adoption and never invalidates a block; the exemption of blocks with a descendant `k` blocks higher; the fork choice over adoptable tips |
| 2 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [admission, pruning and retention](#2-admission-pruning-and-retention) | forks kept up to `W/f` slots below `B_imm`; what a node keeps across a restart |
| 3 | Critical | [Block Construction, Validation and Execution](#affected-specifications): [entries in proposals and blocks](#3-entries-in-proposals-and-blocks) | the 40-byte `UncleReference`, `body_root`, Uncle Validation removed, the parent is `c_loc` |
| 4 | High | [Cryptarchia Bootstrapping & Synchronization](#affected-specifications): [downloading uncles](#4-downloading-uncles) | which entries a node downloads, the stop at the window, the retry wait; serving forks; the checkpoint bound |
| 5 | High | [Cryptarchia Protocol](#affected-specifications): [uncle selection](#5-uncle-selection) | the binding `T_M` and `broadcast` conditions |
| 6 | Medium | [Cryptarchia Protocol](#affected-specifications), [Total Stake Inference](#affected-specifications): [the count](#6-the-count) | the count reads entry slots, whether or not the node holds the uncle |
| 7 | Medium | [Cryptarchia Protocol](#affected-specifications): [the window](#7-the-window) | `W = 240`; `W/f ≤ 4⌊k/f⌋` and `W/f > T_M` |
| 8 | Low | [Payload Formatting, Message Formatting, Blend Protocol, Bedrock Genesis Block](#affected-specifications): [sizes and test vectors](#8-sizes-and-test-vectors) | skim — values derived from the proposal size |

# Discussion

## What changes in the guarantees

| | Before (Cryptarchia 1.2.5) | After (1.3.0) |
| --- | --- | --- |
| What an entry check reads | the chain and the carried signed header | the chain and the block tree |
| When a node can decide | at once | once it holds the uncle |
| Two nodes that hold the same blocks | agree | agree, unless an uncle is lost everywhere |
| A node that syncs from genesis | checks every entry | checks the entries of its last `k` blocks |
| Which wins count | the first block of each fork, its parent within 360 slots | every fork block whose fork point lies within 7,200 slots |

An uncle lost everywhere stops only the block that names it. No honest node adopts that block, so none builds on it.

## A missing uncle delays adoption and never invalidates a block

The signed-header design made every entry a validity condition. That was safe because the entry carried all a node needed to check it. With an entry of ID and slot, validity would depend on what each node holds. So block validity stays as it was, and the entries gate adoption instead:

- A block enters the block tree without an uncle check. A node reads entries only from blocks whose `body_root` it has confirmed, so a tampered copy cannot send nodes looking for uncles that do not exist.
- A chain is adoptable when every entry is valid in each block it would add to the node's chain, except blocks with a descendant `k` or more blocks higher in the tree. A missing uncle delays one chain. After `k` blocks it no longer matters.

Earlier wordings of this rule failed independent review, and each failure shaped one part of it:

- If an invalid uncle made its block invalid, one bad copy served by a peer could condemn an honest block for good. The block ID covers neither the signature nor the operation proofs.
- If nodes skipped the check under the Bootstrap rule, a node cut off for more than `k` blocks (18 hours or more) could never rejoin, because its peers have pruned the uncles. Depth decides instead, whatever the fork choice rule.
- If the `k` descendants were counted on the chain itself, a fork without entries could capture a node still fetching uncles, and one uncle lost everywhere would stop the network. Descendants count in the block tree, and a node checks only blocks after the common ancestor with its own chain.

Two alternatives were rejected:

- An invalid block with an "undecided" verdict that waits outside the tree. It needs the uncles' own entries checked: in a model, eight wins made 21,844 downloads out of one block, against 4 here. It also needs forks kept for `k/f` slots.
- A provably wrong entry that condemns its block for good. Nodes that lack the uncle still build on the block, and the others refuse them. In a model, the two groups ended more than `k` blocks apart in up to 9 of 12 runs, and in none under this rule.

## The window

`W = 240` (7,200 slots, 2 hours), measured to the fork point. Inferred over true stake (`D̂/D`) with a selfish coalition, `k = 256`, 1,000 nodes, the selection rule of this change, 20 paired replicates, standard errors up to 0.004. Coalition shares are of the total active stake, and ρ is the load without the coalition.

| Window | Time | 0.2, ρ 0.36 | 0.2, ρ 0.56 | 0.3, ρ 0.36 | 0.3, ρ 0.56 | Extra forks and ledger states kept, share of `k` |
| --- | --- | --- | --- | --- | --- | --- |
| today: `W = 12`, first fork block only | 6 min | 0.919 | 0.904 | 0.816 | 0.779 | none |
| `W = 12`, any depth | 6 min | 0.973 | 0.961 | 0.881 | 0.851 | 0.6 % |
| `W = 48` | 24 min | 0.999 | 0.998 | 0.983 | 0.970 | 2.2 % |
| `W = 96` | 48 min | 0.998 | 0.998 | 0.995 | 0.991 | 4.4 % |
| `W = 144` | 72 min | 0.998 | 0.998 | 0.994 | 0.995 | 6.7 % |
| `W = 240` | 2 h | 0.998 | 0.998 | 0.994 | 0.995 | 11.1 % |

Without a coalition, no window moves the estimate above the noise at these loads. At ρ 1.76 (`k = 2160`, no coalition), `W = 240` gives 1.0011 against 0.9860 at `W = 12`.

In this simulator 240 gives nothing over 144. Its gain shows on a replay of 14 days of testnet block trees (`k = 1000`), where about half of the blocks are off the chain and 37 % of the orphans lie three or more blocks deep. There the chain counts 0.613 of the occupied slots today. Under this change it counts 0.915 to 0.934 at `W = 240` over the last 7 days, depending on how often a node got a branch block by broadcast (0.5 to 0.9), against 0.861 to 0.882 at `W = 144`.

The bound `W·f⁻¹ ≤ 4⌊k/f⌋` replaces `W ≤ ⌊0.6k⌋`. The old bound kept uncles inside the pruning horizon, which step 8 and Fork Pruning now handle directly. The new one keeps every valid uncle under the epoch state of the chain that references it. The states agree up to `4⌊k/f⌋ + 2` slots, so the bound is sufficient.

One block's entries can make a node fetch up to 400 blocks (four branches as long as a coalition of 0.3 wins in the window, 99.9th percentile).

## Uncle selection and leader privacy

A proposer names what it holds, so an entry can reveal who proposed a block. The selection rule limits this:

- A proposer names a fork block only if it reconstructed the block from a proposal it received by broadcast, and every lower block of the branch came the same way or is already referenced on the chain. A block handed to one node alone by download is never named.
- A proposer names a fork block only from `T_M` (15) slots after the block's own slot. In a 400-node honest model (79,984 proposals), the uncle lists of nodes on the same parent differed in 0.24 to 1.51 % of the proposals without the wait, and in none with it.
- Both conditions bind the proposer. Validators cannot check either.

On the testnet replay at `W = 240`, the drafted branch condition counts 0.915 to 0.934. Requiring the whole branch by broadcast counts 0.828 to 0.925. Naming any block the node holds counts 0.936, but a peer can then mark a node with one win, at any time in two hours, by handing it a block no one else holds.

These leaks remain:

- A block broadcast while only one node can accept it still marks that node through a later entry. The attacker can release the block's parent later (two wins), reference the parent from its own chain block (three wins), or hold back one of the block's transactions (one win, with timing within one gossip hop). In a model, retrying a failed orphan download three times, one second apart, removes the first form.
- A fork block released late at a chosen point of the network, or broadcast directly by its proposer after Blend loses it, is named at once by the proposers it reached first. The next block's uncle list then shows which side of the flood its leader stood on. This costs one win per probe and needs a leader within a slot or two.
- The wider window raises the chance that a marked node proposes while the mark is usable: 0.91 at 1 % of the total active stake within 7,200 slots, against 0.11 within 360.

## Downloads

A node downloads the missing uncles of every chain it would prefer to its own. Without limits, one lottery win buys work for every node. A leader can send many versions of one block, since no rule limits them, each naming uncles that do not exist. A node that walks every missing entry after each block it receives then makes `2M(M+1)` downloads for `M` versions: 5,100 at `M = 50`, each sent to up to 32 peers. The limits:

- A node skips entries whose slot cannot be valid.
- A download stops before it adds a block outside the window of its entry. Without the stop, one entry could make a node validate about `α(k + W)` blocks, 720 at `α` = 0.3 of the total active stake, against `αW` = 72.
- A node handles one block of a lottery win at a time.
- The wait before repeating a failed download starts at `T_round` and doubles, up to `f⁻¹` slots. A leader that gives up one win to publish a child of the tip with four fake entries then costs a synced node about 690 peer requests instead of 5,543. The first repetition still comes after `T_round`. In a model where nodes repeated a failed request every second, 99 % of them held an honest uncle within 3 s, even if only its proposer had it.
- The chain of `best_tip()` goes first. A node catching up fetched 600 honest uncles in 5.6 minutes behind 2,592 fake entries, against 171 minutes without that order (sequential model).

Downloading for the chain of `best_tip()` alone was rejected. A node that lacks an honest block's uncle, and saw an attacker's block of equal length first, would then wait for the next honest block. On the testnet a given fork block is held by about 9 % of the proposers, so that would be most nodes.

## The count

The count reads the chain's entries only, whether or not the node holds the uncle. By the first use of an estimate, every counted block is at least `4⌊k/f⌋` slots old. So all chains a running node holds share the count, unless fewer than `k` blocks were made in the last `4⌊k/f⌋ − W/f` slots, which takes growth below a quarter of the target (10⁻²⁹² at half the target growth).

Trusting old entries is safe because a forged entry cannot help the chain that carries it. Entries add no weight and earn nothing, and a higher count gives a higher estimate: fewer wins and a lower block reward on that chain.

The Total Stake Inference algorithm truncates `f` to thousandths. With that arithmetic, counting any depth overshoots to 1.0098–1.0107 of the true stake. The figures above assume exact arithmetic.

## Costs

- The verdict on a chain waits for its uncles. About 20 to 50 % of the chain's blocks hold an entry at the simulated loads.
- Without the broadcast condition, nodes waited for an uncle in about half to all of the simulated epochs, depending on the Blend delay. With it, in none of 1,823.
- On a testnet-like network (60 nodes, half of the producers reaching 9 % of the nodes), orphans rise from 50.5 to 51.3 % at `W = 240` when a node asks three peers every second, and from 54.5 to 63.4 % when it asks one peer every ten seconds.
- A node that syncs downloads the fork blocks of its last `k` blocks once, about 490 to 700 at design load.
- A Blend message carries a transaction of at most 16,908 bytes, down from 18,192.
- An entry is no longer free to its proposer: it can delay the block's adoption at nodes that lack the uncle.
- In return, the largest proposal falls from 18,192 to 16,908 bytes, a Blend message from 19,318 to 18,034 bytes, and an entry needs no proof or signature check.

## Compatibility

Bedrock has no deployed network, so no migration is needed. The change alters the proposal and block encodings, the `body_root` preimage, the largest Blend payload, the inputs of the fork choice, and what a node keeps. Nodes on the old and the new rules cannot share a chain.

## Not changed here

- [Cryptarchia Fork Choice Rule](../fork-choice.md): the tie-break comment in both rules says "first-seen chain". The functions receive adoptable tips only, so it reads as the first seen among them.
- [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md): three older gaps in block downloads also affect uncle downloads. A download takes the first response whose first item is not an error, so a fast malicious peer wins every race. `download_blocks` does not check that a stream is one chain, so a malicious provider can push any number of valid blocks into a download; the stop at the window limits which blocks an uncle download adds, not how many. And `download_blocks` compares a block with a block ID (`block == req.target_block`).

# Details

## 1. Entries and adoptable chains

[Uncle References](../cryptarchia-v1-protocol.md#uncle-references) and [Adoptable Chains](../cryptarchia-v1-protocol.md#adoptable-chains) in the Cryptarchia Protocol. An entry of the `uncles` field of a block `A` names an uncle by its block ID and slot. With `X` the block it names and `G = common_ancestor(X, A)`, the entry is valid if and only if:

```diff
+- X ∈ T
+- X ≠ G                            # X is off the chain of A
+- u.slot = sl_X < sl_A
+- sl_A − sl_G ≤ W·f⁻¹              # the fork point lies within the window
-- parent(U) lies on the chain of A, and U does not
-- sl_parent(U) < sl_U < sl_A and sl_A − sl_parent(U) ≤ W·f⁻¹
-- the Proof of Leadership of U verifies against inputs from the chain of A
-- the carried signature verifies over the header of U
```

- Any block off the chain of `A` can be an uncle, not only the first block of a fork. Entries need not be unique. A referenced uncle earns no reward and adds no fork-choice weight.
- Step 10 of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation), which made every carried uncle a validity condition, is removed.

The chain of a block `b` is **adoptable** if and only if it contains `B_imm` and every entry is valid in each block of the chain after `common_ancestor(b, c_loc)`, except a block that has a descendant in `T` `k` or more blocks higher. The fork choice takes the adoptable tips `C_T` (new in Notation: the blocks whose chain is adoptable and that have no child whose chain is), and `c_loc ∈ C_T`:

```diff
-c_loc' := B                              if parent(B) = c_loc
-          fork_choice(c_loc, F_T', k, s)  otherwise
+c_loc' := fork_choice(c_loc, C_T', k, s)
```

## 2. Admission, pruning and retention

Step 8 of [Block Header Validation](../cryptarchia-v1-protocol.md#block-header-validation) admits the blocks of forks that can still hold an uncle of a block after `B_imm`, and [Fork Pruning](../cryptarchia-v1-protocol.md#fork-pruning) keeps them:

```diff
-8. height(B) > height(B_imm)
+8. is_ancestor(B_imm, B) ∨ sl_common_ancestor(B, B_imm) + W·f⁻¹ > sl_B_imm
```

```diff
 B_div := common_ancestor(B_tip, B)
-if B_div ≠ B:
+if B_div ≠ B ∧ sl_B_div + W·f⁻¹ ≤ sl_B:
     T' := prune_blocks(B_tip, B_div, T)
```

- Commit prunes the forks that step 8 admits no further block on.
- A node keeps `T` across a restart, and for each of its blocks whether `broadcast` holds ([5](#5-uncle-selection)). It keeps the ledger state after each block that a block admitted by step 8 can extend.

## 3. Entries in proposals and blocks

[Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md):

```diff
-class Proposal:                              # 364..18192 bytes
+class Proposal:                              # 364..16908 bytes
     header: Header                           # 297 bytes
-    uncle_headers: list[SignedHeader]        # 1 + u * 361 bytes, u <= MAX_UNCLES
+    uncles: list[UncleReference]             # 1 + u * 40 bytes, u <= MAX_UNCLES
     references: References                   # 2..16386 bytes (2-byte count + entries)
     signature: Ed25519Signature              # 64 bytes

-class SignedHeader:                          # 361 bytes
-    header: Header                           # 297 bytes
-    signature: Ed25519Signature              # 64 bytes
+class UncleReference:                        # 40 bytes
+    block_id: hash                           # 32 bytes
+    slot: SlotNumber                         # 8 bytes
```

```diff
-UncleHeaders      = UncleCount *SignedHeader
+Uncles            = UncleCount *UncleReference
 UncleCount        = Byte            ; MUST NOT exceed MAX_UNCLES
-SignedHeader      = Header Ed25519Signature
+UncleReference    = BlockId Slot
+BlockId           = Hash32
```

- `Block` carries the same `uncles` list, verbatim from the proposal.
- `body_root` hashes `serialize(uncles)`, a count byte followed by the 40-byte entries, with the transaction Merkle root under the same `BODY_ROOT_V1` tag.
- [Block Proposal Validation](../bedrock-v1.1-block-construction.md#block-proposal-validation) loses its Uncle Validation step. The later steps move up by one.
- A block builder takes the tip of its local chain, `c_loc`, as the parent block.

## 4. Downloading uncles

New section [Downloading Uncles](../cryptarchia-v1-bootstr-sync.md#downloading-uncles) in Cryptarchia Bootstrapping & Synchronization. A node downloads the missing uncles of every chain that contains `B_imm`, is not adoptable, and that the fork choice rule would prefer to `c_loc` if it were adoptable. It does so after each block it receives and in each round of Initial Block Download. For an entry `u` of a block `A`:

- It skips `u` if the slot of `u` is not before the slot of `A`, or lies `W·f⁻¹` or more slots before it.
- It stops the download before it adds a block outside the window of `u`, as `outside_window` defines.
- It downloads the entries of the chain of `best_tip()` before any other.
- Of the blocks of one lottery win, which share their slot and `entropy_contribution`, it handles one at a time, and moves to the next after a failure.
- It repeats a failed download with newly selected peers. It waits `T_round` before the first repetition and twice the previous wait before each further one, never more than `f⁻¹` slots.

```python
def download_missing_uncles(local_tree: Tree):
    for block, uncle in local_tree.missing_uncles():
        def outside_window(b: Block) -> bool:
            # b is not in the tree yet, so its parent leads to its fork point with the block.
            fork_point = local_tree.common_ancestor(b.parent_block, block.id)
            return block.slot - fork_point.slot > W / f or (b.slot >= uncle.slot and b.id != uncle.block_id)

        # With the parent as a known block, the response starts after the fork point of the uncle.
        download_blocks(local_tree, target_block=uncle.block_id, known=[block.parent_block], stop=outside_window)
```

- [Downloading Blocks](../cryptarchia-v1-bootstr-sync.md#downloading-blocks): `download_blocks` takes `known` (more blocks for `KnownBlocks.additional_blocks`) and `stop` (checked before it adds a block not yet in the tree), and sends `best_tip()` as `local_tip`. `best_tip()` is the block the fork choice rule would select if every chain that contains `B_imm` were adoptable. A peer answers a download request from its whole block tree, forks included.
- `T_round` is also the first wait before a failed uncle download is repeated.
- [Bootstrapping from Checkpoint](../cryptarchia-v1-bootstr-sync.md#bootstrapping-from-checkpoint): the checkpoint block must lie at least `W·f⁻¹` slots before the provider's latest immutable block.

## 5. Uncle selection

[Uncle Selection](../cryptarchia-v1-protocol.md#uncle-selection) in the Cryptarchia Protocol:

```python
def uncle_candidates(B) -> Set[Block]:
    # Slots occupied on the chain B extends: its blocks and the uncles they reference.
    occupied = {A.slot for A in ancestors(B)} | {u.slot for A in ancestors(B) for u in A.uncles}
    referenced = {u.block_id for A in ancestors(B) for u in A.uncles}

    return {X for X in T if
              valid_uncle(UncleReference(block_id(X), X.slot), B)
              and X.slot not in occupied
              and X.slot + T_M <= B.slot                                                  # new
              and all(broadcast(Y) or block_id(Y) in referenced for Y in branch(X, B))}   # new
```

- `branch(X, B)` is the blocks after the fork point of `X` up to `X`. `T_M` is the Blend message traversal time, 15 slots. `broadcast(Y)` holds if the node reconstructed `Y` from a proposal it received on the broadcasting channel, or sent that proposal there.
- The proposer takes at most `MAX_UNCLES` candidates, oldest fork point first (was: oldest parent first), one per slot.
- A proposer must not reference a block that fails the `T_M` or the `broadcast` condition. The rest of the procedure stays a recommendation.

## 6. The count

[Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode) in the Cryptarchia Protocol, and `density_over_slots` in the [Total Stake Inference](../cryptarchia-total-stake-inference.md): an uncle counts at the slot its entry holds, whether or not the node holds the uncle.

```diff
-referenced_uncles := { U : A ∈ chain, in_window(sl_A), (U, σ_U) ∈ A.uncle_headers }
-N_BLOCKS := |{sl_B : B ∈ chain, in_window(sl_B)} ∪ {sl_U : U ∈ referenced_uncles, in_window(sl_U)}|
+uncle_slots := { u.slot : A ∈ chain, in_window(sl_A), u ∈ A.uncles }
+N_BLOCKS := |{sl_B : B ∈ chain, in_window(sl_B)} ∪ {sl ∈ uncle_slots : in_window(sl)}|
```

## 7. The window

[Constants](../cryptarchia-v1-protocol.md#constants) in the Cryptarchia Protocol:

- `W` is 240, was 12. The window is measured to the fork point, was to the parent of the uncle.
- `W·f⁻¹` must be at most `4⌊k/f⌋`, the length of the Lottery Constants Finalization phase, and must exceed `T_M`. The virtual bound `W ≤ ⌊0.6k⌋` is removed.

## 8. Sizes and test vectors

| Value | Before | After | Specification |
| --- | --- | --- | --- |
| Largest proposal | 18,192 bytes | 16,908 bytes | Block Construction, Validation and Execution |
| `Max_Body_Length` | 18,192 | 16,908 | Payload Formatting |
| `Max_Payload_Length` | 18,195 | 16,911 | Message Formatting |
| Blend message | 19,318 bytes | 18,034 bytes | Blend Protocol |
| Blend read rate at 124 messages a round | 2.4 MB/s | 2.2 MB/s | Blend Protocol |
| One edge message over 1 Mbit/s | 0.15 s | 0.14 s | Blend Protocol |
| Encapsulation overhead | 6.2 % | 6.6 % | Blend Protocol |
| Full-hash layout in the prefix-length annex | 34,574 bytes | 33,290 bytes | Block Construction, Validation and Execution |

[Test Vectors](../cryptarchia-v1-protocol.md#test-vectors): the two-entry `body_root` is recomputed over two 40-byte entries, the block IDs and slots of the two uncle headers of the previous vector, and is now `0xf1e1f71b031f5d0e499f54480bd2572148af16a6375161600def977601c1197c`. The empty-list `body_root` and the header `block_id` are unchanged.

## Chores

- Removed the text that explained the signed-header design: the notes on the virtual bound of `W` and on structural availability, the rationale of Uncle References and Uncle Selection, and the Block Construction passages on carried signatures.
- Block ID no longer claims that two blocks with the same ID are identical byte for byte.
- Header Validation in Block Proposal Validation names "the position relative to the latest immutable block" in place of "the height against the latest immutable block".
- Bedrock Genesis Block: the `body_root` description names the `uncles` list.

# Implementation

- [ ] Core: replace `uncle_headers` of signed headers with `uncles` of 40-byte `UncleReference` entries in the proposal and the block, with their encoding, `body_root` and the proposal size limit (`core/src/header/mod.rs`).
- [ ] Engine: keep forks whose fork point lies less than `W/f` slots before the latest immutable block; record per block whether its entries were found valid and the height of its highest descendant; run the fork choice over adoptable tips (`consensus/cryptarchia-engine/src/lib.rs`).
- [ ] Chain service: drop `verify_uncles` from header verification (`services/chain/chain-service/src/uncle.rs`); recover the block tree with its forks, and the record of broadcast blocks, after a restart.
- [ ] Chain network: download the missing uncles of preferred chains with the limits of Downloading Uncles, naming the parent of the referencing block as a known block; let the filter of blocks older than the latest immutable block admit uncles (`services/chain/chain-network/src/lib.rs`).
- [ ] Block provider: serve fork blocks, also after a restart.
- [ ] Leader: select uncles by fork point, from `T_M` slots after the uncle's slot, only among blocks reconstructed from broadcast proposals or referenced on the chain; record which blocks were reconstructed from broadcast proposals.
- [ ] Configuration: set the uncle reference window to 240; replace the `⌊0.6k⌋` maximum, and the check against a fifth of `s`, with `W/f ≤ 4⌊k/f⌋`.
- [ ] Checkpoint provider: serve a block at least `W/f` slots before its latest immutable block.
- [ ] Add tests: the `body_root` vectors with no entry and with two, adoption with missing and with invalid entries, the exemption at `k` descendants, pruning at the window, and each download limit.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.3.0 |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | 1.4.0 |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | 1.1.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.1.1 |
| [Payload Formatting](../payload-formatting.md) | Modified | 1.2.1 |
| [Message Formatting](../message-formatting.md) | Modified | 1.0.3 |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.8.2 |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | 1.2.2 |
