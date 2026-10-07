# [RFC] Eras: Introduce era-based protocol versioning

**Motivation and proposal:** [PR #439](https://github.com/logos-co/logos-lips/pull/439)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-09-04 |
| v2 | Applied first-review findings to the branch and re-derived this description: closed the era-in-force rule to chain selection and synchronization, bound migration to validation as well as execution, constrained the header fields up to `slot` to be immovable across eras, split network-layer acceptance from mempool admission, restated the horizon constraint on schedule additions with its breakage, tightened the `T_era` constraint wording, removed restated rules (Blend TP note, step 9's uncle enumeration, ETP scoping), renumbered the stale Block Proposal Validation rule references, aligned revision bumps to minor for wire-visible changes, and linked this table into Details. | 2026-09-04 |
| v3 | Second review pass, applied to the branch and re-derived here. Specification: closed the epoch-length circularity in `era(sl)`; froze schedule entries at publication rather than at activation, so two deployed releases cannot disagree on a pending era; guarded the unimplemented-era halt against peer-supplied blocks below `B_imm`; bounded `H` below by the release's own last schedule entry; added the same-era condition to the `uncle_candidates` pseudocode, which carried only the prose rule; restored the general class of span-reading procedures, fork pruning included; restored the normative keyword on the halt; wrote `era(sl_B_imm)` for the block domain; removed the motivation clause from the `T_era` constraint and the inaccurate breakage clause from the uncle rule; deleted two non-rule sentences. Pseudocode: `era` was an undefined identifier in both encapsulation functions — it is now an input of `encapsulate`, while `decapsulate` carries the received header's version forward. Description: corrected the uncle rationale, the behaviour-preserving exception list, and the in-flight branch names. | 2026-09-04 |
| v4 | Review round (ntn-x2 inline comments; 10-finding review). Specification: both `version` bytes deleted, replaced by two routing rules (a message travels over the identifiers of its own era; Blend releases a message on the connections of the era it arrived on); identifiers `/<network>/<era>/<protocol>` with a network name; fork choice anchored to the era of the latest common ancestor, with the fork-choice rule confined to the tree and the frozen header prefix; the `k`/`f` freeze stated on the inputs with both breakages; the horizon restated as a consequence (an entry at or before a published release's `H` forks off that release's nodes) with the off-by-one fixed; the slot-prefix, rules-versus-values and mempool sentences rewritten plainly; `Header.SIZE` fossil removed from the decapsulation pseudocode. Description: uncle-rule cost argument corrected (zero effect on `D`); Discussion sections added for boundary warm-up, emergency eras and release expiry, migration cost, genesis accretion, and the version-byte removal; pre-existing defects listed. | 2026-09-09 |
| v5 | Concision pass on the specification (two independent cold reads): 17 sentences cut as restatements or justification, 14 rewritten to one statement each; the Blend release rule and the two `<era>` glosses reduced to pointers; the checkpoint sentence split into its two rules; `<protocol>` defined; the era in force tied to the local clock; the Transition Period items restated as validation under the connection's era; the horizon halt stated as one rule. The cut justifications now live in this Discussion. The specifications' revision-history rows reworded to say only what changed. | 2026-09-09 |
| v6 | Folded `T_era` into Blend's Transition Period `T`: the Era Transition Period is the first `T` rounds after the era in force changes, and the `T_era ≥ T` constraint is gone with the second symbol. | 2026-09-09 |
| v7 | Third review round (six lenses). Specification: the state an Epoch State reads as of a slot across a boundary is defined (last block at or before the slot, migrated); a synchronization stream open at the end of the Transition Period is served to its end; the rules of a published era and its migration are frozen with the entry, and an entry cannot be published for an epoch that has begun; a generated message is sent under the era in force at generation, and processed Blend messages follow the connection they arrived on; the migrated tip state is used at the boundary before any new-era block; an era verifies the predecessor's last-epoch rewards as the predecessor does; `T` must exceed the clock difference between honest nodes; the unimplemented-era halt is a startup and checkpoint-import check (so no received block can halt a node); "halt" is defined; the recorded chain state is defined by reference to Mantle §Validation and the SDP stores; every message carrying a block begins with the canonical header; the schedules `[0]` are stated; `EPOCH_LENGTH` named in Cryptarchia; `common_ancestor` replaces "latest common ancestor"; the fork-choice comparison of forks within `k` is frozen across eras. Description: Proposal, Details §1/§4/§5/§7, Implementation and Affected Specifications re-derived; rationale added for every rule above; v6 had omitted that it also rewrote the `T_era` Discussion section, re-derived Details §1 and tasks 8–9, and added the `CHAIN_ID` naming question. | 2026-09-09 |
| v8 | Specification restructured to the standard layout: Overview, Constants and Notation sections added; the definitions of `E_n`, `era(ep)`, `era(sl)`, the era in force, `H`, `T` and `B_imm` moved into Notation and the schedules into Constants; no rule changed. | 2026-09-09 |
| v9 | Review follow-up. `slot` becomes the first header field and the single component an era may not change, replacing the frozen 40-byte prefix, so `parent_block` and everything after it stay changeable; the carried uncle headers re-serialize and the 2-uncle `body_root` vector is regenerated, while `block_id` is unaffected because the preimage keeps its own field order. Discussion states the release-side reading of the implementation floor: a release may drop eras older than the checkpoints it supports. | 2026-09-09 |
| v10 | Review round of 21–23 September. Protocol identifiers carry a fork digest of the genesis block, the chain ID and the eras activated so far, in place of `/<network>/<era>/`; Kademlia and identify carry the chain ID. The era parameter record is specified (layout version 1). Eras count from 0, and chain sync is named `chainsync`. | 2026-10-06 |
|  | Consensus parameters (k, f, the epoch phases, the slot length) may change across eras: era start slots and times are sums over earlier eras, an epoch is measured with its own era's parameters, and `commit` uses the tip era's k and keeps `B_imm` from moving back. | 2026-10-06 |
|  | A change to a published schedule is stated by its consequence, which allows postponement; changing a published era's code rules in place, or an entry whose epoch has begun, stays forbidden. The horizon warns the operator instead of halting the node. | 2026-10-06 |
|  | Transactions carry the fork digest as their first field; a block accepts its era's digest and, during the era's first epoch, the previous era's. SDP values become era parameters. | 2026-10-06 |
|  | Merged master twice: the era rules now cover proof-of-work state and per-epoch values, transactions delivered by Blend and the Proposals topic, and the record carries the PoW reward cap and pool funding. | 2026-10-06 |
|  | Description split into this RFC document and the PR body, per the current template. Removed the `T_era` history, the `/<network>/<era>/` identifiers, the frozen k, f and epoch length, the halting horizon, the resolved `CHAIN_ID` question, a fixed pre-existing defect and the references to other in-flight PRs. The approval of 2026-09-07 predates v4–v10, which change normative content, so approvals are collected again on v10. | 2026-10-06 |
| v11 | Added the constraints the era arithmetic needs: epoch and slot lengths of at least 1, non-zero ratio denominators, and `slot(t)` defined from genesis on. Bounded Blend's Transition Period by the clock difference between honest nodes, `T ≥ T_M + T_C`, which replaces the weaker requirement in Bedrock Eras that `T` exceed that difference. Removed the corresponding open question and added the early-clock gap in its place. Approvals are collected on v11. | 2026-10-06 |
| v12 | Covered the early-clock gap: Blend requires honest clocks to differ by less than one round, and in the last round of its epoch a node does not blacklist a neighbor for a proof of quota valid for the next epoch. The early-acceptance window is recorded as future investigation instead of an open question. Approvals are collected on v12. | 2026-10-06 |

## Reviewer Orientation

Read the PR's Motivation first. Era 0 is the set of rules the specifications describe today, so the mechanism changes nothing until a second schedule entry exists, except four wire changes that land now, before genesis: block IDs (header byte removed, `slot` first), the Blend message and Activity Proof layouts (version bytes removed), every protocol identifier (fork digest), and the transaction encoding (fork digest first).

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Bedrock Eras](../bedrock-eras.md) (Created), [details](#1-the-era-mechanism) | the whole mechanism: schedule and parameter record, `era(sl)` by summation, fork digests, the schedule-change consequence, migration, the transition period, transaction acceptance, the horizon warning |
| 2 | Critical | **Start here**: [Mantle](../bedrock-v1.1-mantle-specification.md) and [Mantle Transaction Encoding](../mantle-transaction-encoding.md), [details](#2-transaction-fork-digest) | `fork_digest` first in every transaction and inside its hash; the acceptance rule; recomputed transaction-hash vectors |
| 3 | Critical | [Cryptarchia Protocol](../cryptarchia-v1-protocol.md), [details](#3-header-bedrock_version-removed-slot-first) | header loses `bedrock_version`, `slot` first; validation steps renumbered 1–9; `first_slot` and a monotone `commit` ([details](#4-consensus-parameters-across-eras)); same-era uncles ([details](#5-same-era-uncle-rule)); test vectors marked `TBD` |
| 4 | Critical | [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md), [details](#3-header-bedrock_version-removed-slot-first) | header layout and encoding grammar; sizes 296, 360, proposal maximum 18,187 |
| 5 | High | [Message Formatting](../message-formatting.md), [Message Encapsulation Mechanism](../message-encapsulation.md), [Blend Protocol](../blend-protocol.md), [details](#6-blend-version-bytes-removed) | `version` bytes removed; relay check removed; Activity Proof metadata 229 bytes; protocol name; pointers to the era rules; Transition Period bound `T ≥ T_M + T_C`; clocks within one round; no blacklisting for a next-epoch proof |
| 6 | High | [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md), [details](#8-synchronization-and-checkpoints) | `chainsync` identifier; blocks parsed under their slot's era; checkpoint state |
| 7 | High | [Bedrock Genesis Block](../bedrock-genesis-block.md), [details](#2-transaction-fork-digest) | the zero `fork_digest` exemption; header field order |
| 8 | Medium | [Payload Formatting](../payload-formatting.md), [details](#9-size-cascade) | `Max_Body_Length` 18,187 |
| 9 | Low | [P2P Network](../../draft/p2p-network.md), [details](#7-protocol-identifiers) | identifiers; skim |
| 10 | Low | [Template Cross-Channel Messaging](../template-cross-channel-messaging.md) | example gains `fork_digest`; skim |

# Discussion

## Two version axes

Chain data is read under the era of its slot. The network runs under the era of the local clock. A node syncing from genesis fetches era-0 blocks over the current era's sync protocol: a block names its era through its slot, and a transaction through its fork digest. Mixing the two axes would force every node to keep speaking every past protocol. This is why `slot` is the first header field, which no era may change, and why the fork digest is the first transaction field.

## Fork digests and the parameter record

- Identifiers carry `F_n`, a hash of the genesis block ID, the chain ID and the era digests of the eras activated so far. Two releases that agree up to now share identifiers until their first differing epoch, and never again after it. Kademlia and identify carry the chain ID instead, so peer discovery works across boundaries.
- Each era digest hashes the era's first epoch and its parameter record, as the implementation already does (logos-blockchain/logos-blockchain#3687). Hashing the parameters separates instances that share a genesis block but differ in a parameter. It also lets a release correct a pending era's parameters without moving its first epoch, and separates rival forks that pick the same epoch. The record also carries a revision. The digest covers an era's parameters but not its code, so a release that changes a pending era's rules or migration increments the revision. The era's digest changes without moving its first epoch.
- The cost is that the record is normative, and every activated era's record must be encoded byte for byte the same forever. The layout version keeps that possible when a later era changes the field list. `chain_id` is implied by the genesis block ID; it stays in the digest input to match the implementation.
- The specified record follows the specifications' constants. It differs from the implementation's `EraParameters` in seven places, each of which changes the digest. A `revision` is added. `faucet_pk` is dropped. `target_claim_per_block` duplicates `TARGET_CLAIMS_PER_BLOCK` and is dropped. `learning_rate` and `message_frequency_per_round` become ratios. `reward_pool_genesis`, a Genesis value, and `epoch_reward_genesis`, a derived value, are dropped. `min_stake` carries an epoch instead of a block-number timestamp. `slot_window` becomes `expected_blocks_per_window`, so the window follows f. These should be aligned before the next testnet release fixes its era-0 digest.

## Consensus parameters across eras

An era may change k, f, the epoch phases and the slot length, as agreed in review. Era boundaries stay epoch boundaries. Each era's first slot and start time are sums over the earlier eras; with equal epoch lengths the sum is the old `⌊sl / EPOCH_LENGTH⌋`, so era 0 is unaffected. A measurement over an epoch uses that epoch's era: the stake-inference window of epoch e−1 uses the k and f of e−1's era. `commit` takes k from the tip's era and never moves `B_imm` back, which a growing k would otherwise do. Fork choice compares two chains under the era of their common ancestor, so its k is that era's. The longest-chain comparison of forks within k stays frozen: an era that changed it would make the result depend on the order in which forks were seen.

## Version fields removed

Once the era follows from `slot`, the `bedrock_version` byte carries nothing, so it is removed. The header shrinks to 296 bytes and every block ID changes, which is possible only before genesis. The Blend message and Activity Proof `version` bytes go too, because the identifier a message arrives on, or the slot of the including block, already names the era. Two routing rules replace them: a message travels over the identifiers of the era in force when it was generated, and Blend forwards a received or processed message on the era of the connection it arrived on.

## Fork choice under the common ancestor's era

Pinning fork choice to the local clock would make a node judge an old fork under a later era's density rules, depending on when it syncs. The era of the common ancestor is a function of the two chains alone. An era's fork-choice rule reads only the block tree and the slot of each block; otherwise it would be undefined on the blocks of a later era that re-encodes a field it reads.

## The transition period

The era overlap reuses Blend's Transition Period T, 30 rounds. It must cover the drain of every protocol whose in-flight work cannot resume under the new era, and Blend messages are the only such traffic: sync streams resume through `KnownBlocks`. Nodes switch by their own clocks, so a node whose clock runs ahead ends its period up to `T_C` rounds early, `T_C` being the largest clock difference between honest nodes. A message generated just before the boundary must still reach it, so Blend now requires `T ≥ T_M + T_C`. The same bound covers Blend's own epoch boundaries, and it implies the overlap Bedrock Eras used to require separately. The opposite direction is a message of the new epoch reaching a node whose clock runs behind. A node releases a message it generates at the start of the next round, so no honest new-epoch message exists until one round after the earliest switch. Blend therefore requires honest clocks to differ by less than one round. An attacker can still send a new-epoch message early. It sends a valid one to a node just after that node's clock switches, and that node relays it at once to a neighbor whose clock has not. Under Blend's existing blacklist rule, that neighbor would blacklist the honest relayer for an invalid proof of quota. Now, in the last round of its epoch, a node discards such a message but keeps the connection and does not blacklist. Accepting these messages early instead is recorded below as future investigation. A sync stream open when the period ends is served to its end, because cutting every initial block download at once would terminate syncing nodes. Before the boundary nobody subscribes to the new era's topics. Transport connections persist, gossipsub grafts at the next heartbeat (about a second, against 30-second blocks), and Blend re-forms its network at every epoch anyway.

## State at the boundary

A block reads earlier-era state with the migrations applied. At the boundary a node migrates the state of its tip for the mempool and the new era's protocols. An epoch derives its values (Epoch State, `difficulty_blend`, `epoch_pow_reward`) under its own era, from state migrated to that era; values an earlier epoch derived are used as derived. The predecessor's last-epoch Activity Proofs, reward claims and `CLAIM_POW_REWARD` solutions are verified as the predecessor does, or that epoch's rewards would be lost.

An era's rules must be defined on the state its migration produces. That rules out one case: a new rule that reads data only another new rule can create. An example is a new Blend that needs a new kind of SDP declaration. No migration can produce declarations that nodes have not yet made, and SDP takes a declaration into a snapshot two epochs after it is made. Such a change is staged over two eras. The first introduces the new SDP logic and leaves Blend unchanged. The second starts at least two epochs later and introduces the new Blend. A per-protocol activation delay inside one era would do the same, but the rules of a slot would then depend on more than its era, and one fork digest would no longer stand for one set of rules.

## Same-era uncle references

A carried uncle is validated as a block of its own era, so a cross-era uncle would pull the predecessor's encoding and proof system into current-era validation. The rule costs nothing: the stake-inference window counts an uncle only when both it and the referencing block lie in the first `6k/f` slots of one epoch, and every era boundary is an epoch boundary. Its only effect is that blocks in an era's first 360 slots reference no uncle from before the boundary.

## Changing a published schedule

The schedule is embedded in the software because it must be known before any block of the new era exists. Two releases apply different rules from the first epoch whose era digest differs between their schedules, and the fork digest separates them from then on. A release may therefore postpone a pending era, or correct its parameters in place; nodes of the earlier release split off at the old epoch unless they upgrade. Changing a published era's code rules while keeping its first epoch and record is forbidden, because both populations would share one identifier and reject each other's blocks. So is publishing an entry, or changing one, whose epoch has begun: a node would hold state executed under the wrong era.

## Horizon as a warning

A node that misses an upgrade keeps running on the old rules. The fork digest isolates it from upgraded nodes, but nothing tells its operator, and its users keep trusting a minority chain. The horizon warns the operator once the clock passes `H`, and whenever a peer of the chain advertises a fork digest the node does not know. It does not halt the node: a halt would also stop the whole network if no release shipped before `H`.

- **Rollout policy:** ship a release well before the `H` of the release it replaces, and start its era after that `H`. A new release can extend `H` without adding an era: same schedule, same fork digest.
- **Emergency eras:** an era can start at the next epoch boundary, up to 648,000 slots (7.5 days) away at the reference parameters. Nodes that do not upgrade split off.

## Transaction replay protection

A transaction carries the fork digest in force when it was signed, inside its hash, so a transaction signed on one fork is invalid on another. A block of era m accepts `F_m`, and also `F_{m−1}` during era m's first epoch, so a transaction in flight at a boundary survives it. The review first proposed accepting any past digest. That would let a chain that did not upgrade, which keeps signing with the old digest, replay its transactions onto the real chain forever, and every era would have to keep every earlier transaction format. The Genesis transaction carries the zero digest, because every fork digest hashes the Genesis block. Each transaction grows by 32 bytes. Operation and note IDs do not change, because `op_id` hashes the operation alone.

## SDP values as era parameters

No Operation sets the minimum stake or the service parameters; the Genesis Block takes them from the node software. They are therefore era parameters, set through the parameter record. Their entries keep an `epoch`, so a value can take effect inside an era. The SDP stores leave the migrated chain state.

## Migration applied per chain

Near the tip the chain is not final, so "the state at the boundary" is not a single thing. The migration is a pure function applied per chain, composing across eras without blocks. Purity makes a reorg across a boundary need no rule: each branch migrates independently. Caches, key pools and connections are not chain state; the transition period governs them. A heavy migration runs once per live fork tip, in the validation of the first new-era block. No concrete migration exists yet, because era 0 has no predecessor.

## Genesis bootstrap and accretion

The schedule is complete from era 0, so a release that dropped era-0 code still computes `era(sl) = 0` after genesis and halts at startup. Bootstrapping from genesis requires the rules of every era. Checkpoint bootstrapping needs only the eras from the checkpoint forward, so a release may drop the eras older than the oldest checkpoint it supports.

## Governance, readiness and emergency recovery

Out of scope, as agreed in review: stake-weighted approval of an era, readiness signalling, a voting mechanism, on-chain era definitions, and coordinating stake onto an emergency era. Each needs its own RFC.

## Compatibility and rollout

This PR precedes any launched network. Era 0 is today's rules. The identifier, header, Blend layout and transaction encoding changes land at a network reset, with no transition of their own. A devnet can exercise the whole mechanism with a schedule such as `[0, 3]` and an identity era.

## Open questions

- Testnet's era-0 record: the Constants give testnet the specifications' values. If testnet runs other values, its record must list them.
- Future investigation: an early-acceptance window. From a set number of rounds before its own boundary, a node would also accept proofs built on the next epoch's inputs, and connections on the next era's identifiers. This mirrors the transition period. A late node could then relay a next-epoch message instead of discarding it, and honest clocks could differ by more than one round.
- No specification defines a canonical encoding of the recorded chain state: the checkpoint API serves it as an opaque blob. Checkpoint interoperability and migration test vectors need one.
- Domain-separation tags stay `_V1`. Whether a construction changed in era n should take `_V<n>` is for the leads.
- Version-carrying file names (`bedrock-v1.1-*`, `cryptarchia-v1-*`) are not renamed.
- Pre-existing defects noticed during review, left for separate PRs: the `SDP_ACTIVE` Mantle vector omits the `UINT32` metadata length prefix and still carries the removed Activity Proof `version` byte; a checkpoint carries no Epoch State, yet `compute_epoch_state` recurses to genesis for D; `H+1` overflows a `u32` epoch number at its maximum.

# Details

## 1. The era mechanism

[Bedrock Eras](../bedrock-eras.md) is the specification and should be read whole. Its sections:

- **Notation:** `E_n`, the parameter record `P_n`, the epoch and slot lengths `L_n` and `Δ_n`, the era start slots `S_n` and times `τ_n`, `era(ep)`, `era(sl)`, `epoch(sl)`, `first_slot(ep)`, `slot(t)`, the era in force, the horizon `H`, the genesis block ID `G`, the era digest `D_n` and the fork digest `F_n`.
- **Era Schedule:** an embedded list per network of (first epoch, parameter record), first epoch 0; the frozen within-k fork comparison; the consequence of two releases' schedules differing; a revision increment for any change to a published era's rules or migration, and no entry for an epoch that has begun.
- **Era Parameters:** the record, a layout version and a revision followed by 33 fields in a fixed order, each holding a named constant of Blend, Cryptarchia, Total Stake Inference, SDP or Proof of Work; their encodings, with non-zero ratio denominators; epoch and slot lengths of at least 1; the SDP stores filled from the records; layout versioning.
- **Era of Chain Data:** a block and everything it carries under `era(sl)`, except that a transaction is parsed under the era its fork digest names; `slot` first and unchanged in every era; the fork digest first in every transaction, and the acceptance rule; fork choice under the common ancestor's era; `commit` with the tip era's k; the startup and checkpoint-import halt; the mempool.
- **Era Migration:** a function of the recorded chain state (Mantle validation state, PoW state, SDP snapshots); total; identity by default; applied per chain and at the boundary tip; epoch derivations under the epoch's era; predecessor last-epoch proofs.
- **Era Transition Period:** the first `T` rounds after the era in force changes; both eras' identifiers; Blend messages validated under the arrival connection's era; afterwards the predecessor's identifiers dropped and open sync streams served to their end.
- **Network Protocol Identity:** `/logos-blockchain/<fork_digest>/<protocol>`, and `/logos-blockchain/<chain_id>/<protocol>` for Kademlia and identify; generation, forwarding and publication rules.
- **Horizon:** `H` no smaller than `E_n` of the last entry; warnings past `H` and on unknown peer fork digests.

## 2. Transaction fork digest

[Mantle](../bedrock-v1.1-mantle-specification.md) and [Mantle Transaction Encoding](../mantle-transaction-encoding.md):

```diff
 class MantleTx:
+    fork_digest: hash
     ops: list[Op]
```

```diff
-MantleTx = OpCount *Op
+MantleTx   = ForkDigest OpCount *Op
+ForkDigest = Hash32
```

- `fork_digest` is the fork digest of the era in force when the transaction was signed. `mantle_txhash` covers it, and with it every signature and proof bound to the transaction.
- Validation gains step 4: the `fork_digest` is accepted as defined in Bedrock Eras.
- The Mantle Transaction Hash vectors are recomputed with a test `fork_digest` of 32 `0x11` bytes. The Cryptarchia vectors that depend on transaction hashes are marked `TBD` ([§3](#3-header-bedrock_version-removed-slot-first)).
- [Bedrock Genesis Block](../bedrock-genesis-block.md): the Genesis Mantle Transaction carries a `fork_digest` of 32 zero bytes, and is exempt from step 4.

## 3. Header: `bedrock_version` removed, `slot` first

[Cryptarchia Protocol](../cryptarchia-v1-protocol.md) and [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md):

```diff
-class Header:                                # 297 bytes
-    bedrock_version: byte                    # 1 byte
-    parent_block: hash                       # 32 bytes
+class Header:                                # 296 bytes
     slot: SlotNumber                         # 8 bytes
+    parent_block: hash                       # 32 bytes
     body_root: hash                          # 32 bytes
     # ... unchanged fields elided
```

- The `BLOCK_ID_V1` preimage loses `bedrock_version` and keeps its own field order. `SignedHeader` is 360 bytes, the canonical-encoding grammar drops `Version`, and the proposal maximum becomes 18,187 bytes.
- Block Header Validation step 1 (`bedrock_version = 1`) is removed and the remaining steps are renumbered 1–9, together with every reference to them.
- The Genesis Block examples drop the field and list `slot` first.
- The test vectors whose inputs contain transaction hashes are marked `TBD`: the leaf hashes, the transaction Merkle root, both `body_root` rows and the header `block_id`. The empty-block Merkle root is unchanged.

## 4. Consensus parameters across eras

[Cryptarchia Protocol](../cryptarchia-v1-protocol.md):

- The Epoch State pseudocode takes the start of the previous epoch from the era schedule: `sl_{ep−1} := first_slot(ep−1)`.
- `commit` takes the current `B_imm` and moves it only to a higher block:

```diff
-define commit(T, c_loc, depth) -> (T', B_imm):
-    B_imm := block_at_depth(c_loc, depth)
+define commit(T, c_loc, B_imm, depth) -> (T', B_imm'):
+    B := block_at_depth(c_loc, depth)
+    B_imm' := B if height(B) > height(B_imm) else B_imm
```

The rules that choose k for `commit`, measure each epoch with its own era's parameters, and sum era start slots and times are in Bedrock Eras ([§1](#1-the-era-mechanism)).

## 5. Same-era uncle rule

A new validity condition in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references), also added to the `uncle_candidates` pseudocode:

> The uncle lies in the same era as the referencing block: `era(sl_U) = era(sl_A)`.

## 6. Blend version bytes removed

[Message Formatting](../message-formatting.md) and [Message Encapsulation Mechanism](../message-encapsulation.md):

```diff
 class PublicHeader:
-    version: byte,
     public_key: PublicKey,
     proof_of_quota: ProofOfQuota,
     signature: Signature
```

[Blend Protocol](../blend-protocol.md): Relaying step 1.1, the version check, is deleted. The Activity Proof `version` row is deleted, so the metadata is 229 bytes; `metadata_type` remains `0x01`. §Releasing and §Transition Period point to the era rules. §Transition Period requires `T ≥ T_M + T_C`, where `T_C` is the largest clock difference between two honest nodes, in rounds, and requires `T_C` to stay below one round. In Connectivity Maintenance, a message received in the last round of an epoch whose proof of quota is valid against the next epoch's public input carries no reaction, and Relaying step 6 defers its reaction to that rule. In Message Encapsulation, `encapsulate` and `decapsulate` no longer set `version`, the `decapsulate` offsets no longer use the undefined `Header.SIZE`, and `PAYLOAD_BODY_SIZE` equals `Max_Body_Length`.

## 7. Protocol identifiers

| Protocol | Identifier |
| --- | --- |
| Blend | `/logos-blockchain/<fork_digest>/blend` |
| Chain sync | `/logos-blockchain/<fork_digest>/chainsync` |
| Mempool topic | `/logos-blockchain/<fork_digest>/mempool` |
| Proposals topic | `/logos-blockchain/<fork_digest>/cryptarchia` |
| Kademlia | `/logos-blockchain/<chain_id>/kad` |
| Identify | `/logos-blockchain/<chain_id>/identify` |

The testnet variants are gone, because the chain ID and the genesis block separate networks. The placeholders are defined in Bedrock Eras ([§1](#1-the-era-mechanism)).

## 8. Synchronization and checkpoints

[Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md): each downloaded block is parsed and validated under the era of its slot. The `checkpoint_ledger_state` carries the recorded chain state of Era Migration, encoded under the era of the checkpoint block's slot.

## 9. Size cascade

The proposal maximum of 18,187 bytes propagates: [Payload Formatting](../payload-formatting.md) `Max_Body_Length = 18187`; [Message Formatting](../message-formatting.md) `Max_Payload_Length = 18190`; the Blend encapsulation-overhead figure follows.

## 10. Versioning section replaced

Cryptarchia's §Versioning and Protocol Upgrades, which activated upgrades by block height, is reduced to a link to Bedrock Eras.

## Chores

- Registered Bedrock Eras in `scripts/blockchain_structure.py` (`FILE_ASSIGNMENTS`).
- Revision-history rows added to every edited specification.
- Dropped the "Current versions are `1.0.0`" sentences from P2P Network, and the "we omit the versioning" sentences from Blend and Message Encapsulation.
- Block Header Validation step 9 reduced to a pointer to Uncle References.
- Genesis Block: "hard / soft fork" wording replaced by "era change", and gas constants are no longer described as hard-coded.
- Template Cross-Channel Messaging: the example sets `fork_digest`.

# Implementation

- [x] Remove the `Version` header field and the Blend version bytes; put `slot` first ([logos-blockchain#3679](https://github.com/logos-blockchain/logos-blockchain/pull/3679))
- [x] Era schedule with parameter records; era and fork digests; identifiers from the fork digest ([#3683](https://github.com/logos-blockchain/logos-blockchain/pull/3683), [#3687](https://github.com/logos-blockchain/logos-blockchain/pull/3687), [#3689](https://github.com/logos-blockchain/logos-blockchain/pull/3689))
- [ ] Align `EraParameters` with layout version 1 of Era Parameters (the six differences in Discussion) and regenerate the era and fork digest vectors
- [ ] Reject a schedule whose record has a zero ratio denominator, or an epoch or slot length below 1
- [ ] Support more than one era: `era`, `epoch`, `first_slot` and `slot(t)` by summation; switch identifiers at the boundary, run both eras for `T` rounds, then drop the predecessor's, serving open sync streams to their end
- [ ] Transaction fork digest: first field of every transaction, the acceptance rule, the zero digest at genesis, parsing by digest; reopen [#3692](https://github.com/logos-blockchain/logos-blockchain/pull/3692)
- [ ] Fork choice under the common ancestor's era; `commit` with the tip era's k and a monotone `B_imm`
- [ ] Same-era uncle validity, in validation and in `uncle_candidates`
- [ ] Migration hook (identity for now), applied per block and to the tip at the boundary; epoch derivations under the epoch's era; predecessor last-epoch Activity Proofs, reward claims and `CLAIM_POW_REWARD`
- [ ] Message routing: generated messages under the era in force at generation; received and processed Blend messages, and their broadcast payloads, on the arrival connection's era; accepted proposals and admitted transactions on the era-in-force topic
- [ ] In the last round of an epoch, check a failing proof of quota against the next epoch's public input; if it passes, discard the message without closing the connection or blacklisting
- [ ] Startup and checkpoint-import halt when an era from `era(sl_B_imm)` to the era in force is not implemented; checkpoint export and import under the checkpoint block's era
- [ ] Horizon warnings: past `H`, and when a peer advertises an unknown fork digest
- [ ] Regenerate the Cryptarchia test vectors marked `TBD`, and the `SDP_ACTIVE` operation and transaction-hash vectors with 229-byte Activity Proof metadata and the `UINT32` length prefix
- [ ] Add or extend tests / test vectors that exercise the change, including a devnet schedule such as `[0, 3]` with an identity era
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Bedrock Eras](../bedrock-eras.md) | Created | the mechanism |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | header field removed, `slot` first, validation renumbered, same-era uncles, `first_slot`, monotone `commit`, §Versioning replaced by a link, vectors `TBD` |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | header layout, encoding grammar, size derivations |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | `fork_digest` field, validation step 4, transaction-hash vectors |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | `ForkDigest` first in `MantleTx` |
| [Blend Protocol](../blend-protocol.md) | Modified | version checks removed, protocol name, era pointers, overhead figure, Transition Period and clock bounds, no blacklisting for a next-epoch proof |
| [Message Formatting](../message-formatting.md) | Modified | `version` byte removed, payload maximum |
| [Message Encapsulation Mechanism](../message-encapsulation.md) | Modified | `version` field removed, decapsulation offsets, `PAYLOAD_BODY_SIZE` |
| [Payload Formatting](../payload-formatting.md) | Modified | `Max_Body_Length` |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | `chainsync` identifier, per-era parsing, checkpoint state |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | header field order, zero `fork_digest` exemption, gas wording |
| [P2P Network](../../draft/p2p-network.md) | Modified | identifiers |
| [Template Cross-Channel Messaging](../template-cross-channel-messaging.md) | Modified | example sets `fork_digest` |
