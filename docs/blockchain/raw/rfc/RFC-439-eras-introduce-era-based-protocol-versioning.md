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
| v13 | Review round of 7–9 October. The specification is restructured into Introduction, Overview, Protocol and Details tiers: diagrams, a Protocol part per building block that opens with its objective, a walk through an era boundary, and reference code in Details for the era arithmetic, the fork digest, the transaction fork digest check, migration and the mempool. | 2026-10-09 |
|  | The parameter record has a canonical encoding: a block version, a layout version, and Blend, Cryptarchia and Time sections that each start with a section version; ratios in lowest terms; the slot length in whole seconds. The slot activation coefficient's numerator is at least 1. | 2026-10-09 |
|  | The rules of an era and a published era are defined, and an era's rules apply to every state its migration produces. A node migrates on demand: a block's parent state, an epoch's input state, and its tip's state, against which it re-validates its mempool whenever the tip or the era in force changes. Active messages and reward claims are verified under the era of the epoch they are for. | 2026-10-09 |
|  | The horizon is removed. A node warns its operator when a peer advertises an unknown fork digest. A percent-encoded chain ID uses uppercase hexadecimal digits. These change normative content, so approvals are collected again on v13. | 2026-10-09 |
| v14 | The fork digest hashes the genesis block ID and the era digests, without the chain ID, which the genesis block already commits to. Kademlia and identify carry the genesis block ID in lowercase hexadecimal instead of the percent-encoded chain ID, and the unknown fork digest warning skips their identifiers. These change normative content, so approvals are collected again on v14. | 2026-10-13 |
| v15 | Identify keeps its libp2p identifier and announces `/logos-blockchain/<genesis_id>/identify` as its protocol version, as the implementation does; only the Kademlia identifier carries the genesis block ID. The unknown fork digest warning covers only a peer that announces the node's own protocol version. This changes normative content, so approvals are collected again on v15. | 2026-10-14 |
| v16 | Merged master, which removes the Activity Proof `version` byte in its tagged encoding of the active message metadata. This RFC no longer removes that byte itself, its note on the stale `SDP_ACTIVE` vector is dropped, and the transaction-hash vector with one of each operation is recomputed with the test fork digest. | 2026-10-14 |
| v17 | The parameter record follows the implementation where that is safe. One `version` names the era's rules, block layout and fields, in place of the block, layout and section versions. `learning_rate` is a double-precision value, and Total Stake Inference computes with `beta` and `f` in double precision. Ratios are encoded as written, `min_stake`'s epoch takes eight bytes, and the slot length is encoded as seconds and nanoseconds. The proof-of-work acceptance window is the parameter `WINDOW`, in slots. These change the era digest, so approvals are collected again on v17. | 2026-10-15 |
|  | Review round of 14 October. A release must not move a published era to an earlier first epoch. `commit` advances `B_imm` only while it lies deeper than the k of its own era, so a smaller k in a new era no longer makes the previous era's blocks immutable early. The Discussion records why an outdated release warns instead of halting. | 2026-10-16 |
|  | A block accepts a transaction carrying its era's fork digest or an earlier one, unless an era refuses earlier transactions, which it states with its migration; the first-epoch window is gone. The Era Transition Period starts two seconds before the boundary, the clock slack Blend now applies at every epoch: a node opens the new identifiers and connections early and processes what arrives on them under the new era and epoch, and its mempool follows the era in force two seconds ahead. This replaces Blend's one-round clock bound and its last-round exemption from blacklisting. | 2026-10-16 |
| v18 | The Era Transition Period takes its length from the previous era's Blend Transition Period instead of the new era's, because the traffic it drains is the previous era's. | 2026-10-20 |
|  | The two-second clock slack is removed again. The Era Transition Period starts at the boundary, the mempool follows the era in force, and Blend's one-round clock bound and its last-round exemption from blacklisting are restored. | 2026-10-20 |
|  | A synchronization request not served by the end of the Era Transition Period is dropped with the previous era's identifiers, and the requesting node continues downloading under the new era; open streams are no longer served to their end. | 2026-10-20 |
| v19 | Consistency check. A transaction's fork digest is checked against an era, so the mempool applies the rule a block applies. Era of Chain Data names the active-message and reward-claim exception. A release must not change which era governs an epoch that has begun, or that era's record. `min_stake`'s eight-byte epoch is an exception to the `EpochNumber` encoding. Fork choice takes k and s from the common ancestor's era. The two uncle signatures of the 2-uncle vector, made over the old header, are `TBD`, and a Blend message is 19,313 bytes. | 2026-10-20 |
|  | A proof-of-work claim's window, for its check and for discarding its nullifier, is the `WINDOW` of the era of its referenced block. The fork-choice constraint uses the smaller k of the two eras. A request dropped at the end of an Era Transition Period is not a download failure, and a node that starts during the period runs only the era in force. | 2026-10-20 |
|  | The pow reward pool seed and the consensus-excluded keys are Cryptarchia parameters of the Genesis block instead of era values. The initial total stake leaves out the excluded keys' genesis notes, and a node does not lead with their notes. Removed from Discussion: the narration of earlier drafts, and the floating-point ⌊k/f⌋ from the pre-existing defects, which an implementation task covers. These change normative content, so approvals are collected again on v19. | 2026-10-20 |
| v20 | Every era after the first keeps its uncle reference window within the finalization window of the era before it, `W_n · f_n⁻¹ ≤ s_{n−1}/5`, since the latest immutable block of an era's first blocks still lies in the era before. This changes normative content, so approvals are collected again on v20. | 2026-10-21 |

## Reviewer Orientation

Read the PR's Motivation first. Era 0 is the set of rules the specifications describe today, so the mechanism changes nothing until a second schedule entry exists, with two exceptions. Five wire changes land now, before genesis: block IDs (header byte removed, `slot` first), the Blend message layout (version byte removed), every protocol identifier (fork digest), the transaction encoding (fork digest first), and the Genesis inscription (pool seed and consensus-excluded keys). Blend's rules at every epoch boundary also apply from genesis: honest clocks within one round, `T ≥ T_M + T_C`, and no blacklisting for a next-epoch proof in an epoch's last round.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Bedrock Eras](../bedrock-eras.md) (Created), [details](#1-the-era-mechanism) | the whole mechanism: the Overview's diagrams and the Protocol's walk through an era boundary first; then the schedule and the versioned parameter record with its canonical encoding, the era arithmetic and fork digests as reference code, the schedule rules, migration with `migrate` and the rules that apply to its output, mempool re-validation, the transition period, transaction acceptance, and the warning on an unknown fork digest |
| 2 | Critical | **Start here**: [Mantle](../bedrock-v1.1-mantle-specification.md) and [Mantle Transaction Encoding](../mantle-transaction-encoding.md), [details](#2-transaction-fork-digest) | `fork_digest` first in every transaction and inside its hash; the acceptance rule; recomputed transaction-hash vectors |
| 3 | Critical | [Cryptarchia Protocol](../cryptarchia-v1-protocol.md), [details](#3-header-bedrock_version-removed-slot-first) | header loses `bedrock_version`, `slot` first; validation steps renumbered 1–9; `first_slot`, fork choice with the common ancestor's era's k and s, and a `commit` that advances `B_imm` only while it lies deeper than its own era's k ([details](#4-consensus-parameters-across-eras)); same-era uncles ([details](#5-same-era-uncle-rule)); test vectors marked `TBD` |
| 4 | Critical | [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md), [details](#3-header-bedrock_version-removed-slot-first) | header layout and encoding grammar; sizes 296, 360, proposal maximum 18,187 |
| 5 | High | [Message Formatting](../message-formatting.md), [Message Encapsulation Mechanism](../message-encapsulation.md), [Blend Protocol](../blend-protocol.md), [details](#6-blend-version-byte-removed) | `version` byte removed; relay check removed; protocol name; pointers to the era rules; Transition Period bound `T ≥ T_M + T_C`; clocks within one round; no blacklisting for a next-epoch proof |
| 6 | High | [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md), [details](#8-synchronization-and-checkpoints) | `chainsync` identifier; blocks parsed under their slot's era; checkpoint state; a request dropped at the end of an Era Transition Period is not a failure |
| 7 | High | [Bedrock Genesis Block](../bedrock-genesis-block.md), [details](#12-genesis-parameters) | the pool seed and the consensus-excluded keys in the Cryptarchia parameters, and the initial total stake without the excluded keys; the zero `fork_digest` exemption ([details](#2-transaction-fork-digest)); header field order |
| 8 | Medium | [Payload Formatting](../payload-formatting.md), [details](#9-size-cascade) | `Max_Body_Length` 18,187 |
| 9 | Medium | [Proof of Work](../proof-of-work.md), [Total Stake Inference](../cryptarchia-total-stake-inference.md), [details](#11-acceptance-window-and-stake-inference-arithmetic) | `WINDOW` a parameter in slots, of the era of the referenced block; the pool seed from the Genesis block; `beta` and `f` in double precision |
| 10 | Low | [P2P Network](../../draft/p2p-network.md), [details](#7-protocol-identifiers) | identifiers; skim |
| 11 | Low | [Template Cross-Channel Messaging](../template-cross-channel-messaging.md) | example gains `fork_digest`; skim |

# Discussion

## Two version axes

Chain data is read under the era of its slot. The network runs under the era of the local clock. A node syncing from genesis fetches era-0 blocks over the current era's sync protocol: a block names its era through its slot, and a transaction through its fork digest. Mixing the two axes would force every node to keep speaking every past protocol. This is why `slot` is the first header field, which no era may change, and why the fork digest is the first transaction field.

## Fork digests and the parameter record

- Identifiers carry `F_n`, a hash of the genesis block ID and the era digests of the eras activated so far. Two releases that agree up to now share identifiers until their first differing epoch, and never again after it. Kademlia carries the genesis block ID instead, and identify announces it as its protocol version, so peer discovery works across boundaries.
- The chain ID is not hashed again. It is part of the Genesis inscription, so the genesis block ID already commits to it. The Kademlia identifier also separates two networks that reuse a chain ID with different genesis blocks, such as a reset testnet: their nodes no longer share a DHT. The identifiers lose a readable network name, and the percent-encoding of the chain ID is gone.
- Identify keeps the libp2p identifier `/ipfs/id/1.0.0`, as the implementation does, so two nodes of different networks that reach each other directly still exchange identify messages. They then negotiate nothing else, because each advertises identifiers the other does not run. Their `protocolVersion` values differ, so the unknown fork digest warning covers only peers that announce the node's own value, and a node of another network is not reported as running an unknown era. A node does not close the connection over a different `protocolVersion`: the libp2p identify specification revoked that requirement to let networks interoperate.
- Each era digest hashes the era's first epoch number and its parameter record, as the implementation already does (logos-blockchain/logos-blockchain#3687). Hashing the parameters separates instances that share a genesis block but differ in a parameter. It also lets a release correct a pending era's parameters without moving its first epoch, and separates rival forks that pick the same epoch.
- The cost is that the record is normative, and every activated era's record must be encoded byte for byte the same forever. One version, leading the record, keeps that possible. It names the era's rules, its block layout and the record's fields, as the implementation's ruleset number does, and any change to them takes a new version. Two releases that disagree on an era's rules or block layout therefore get different fork digests instead of forking under one. Separate block, layout and section versions would carry nothing more, because no node reads a version from the wire.
- The record follows the implementation's encoding wherever every record keeps a single byte string and every value derived from it stays exactly reproducible. `learning_rate` is a double-precision value, which Total Stake Inference already truncates in double precision. Ratios are encoded as written, `min_stake`'s epoch takes eight bytes, and the slot length is seconds followed by zero nanoseconds. The proof-of-work window is a parameter in slots, so it no longer follows f: an era that changes f sets the window too.
- The record still differs from the implementation's in four places, each of which changes the digest. `target_claim_per_block` duplicates `TARGET_CLAIMS_PER_BLOCK`, which the payout and the retarget both use, and is dropped. `reward_pool_genesis` and `consensus_excluded_keys` are fixed at genesis and never change with an era, so they are Cryptarchia parameters of the Genesis block, which the fork digest commits to through the genesis block ID; a structure next to the Genesis block would need its own fork-digest input. `epoch_reward_genesis` is dropped, because the first epoch's reward is derived from the pool like every later epoch's. `message_frequency_per_round` stays a ratio: the core quota is the ceiling of a product with it, and a double-precision product can come out just above a whole number that the exact product equals, so the ceiling adds one. `min_stake`'s second field is also an epoch, where the implementation names a block number; both are 0. These should be aligned before any network fixes its era-0 digest.

## Consensus parameters across eras

An era may change k, f, the epoch phases and the slot length, as agreed in review. Era boundaries stay epoch boundaries. Each era's first slot and start time are sums over the earlier eras; with equal epoch lengths the sum is the old `⌊sl / EPOCH_LENGTH⌋`, so era 0 is unaffected. A measurement over an epoch uses that epoch's era: the stake-inference window of epoch e−1 uses the k and f of e−1's era. Fork choice compares two chains under the era of their common ancestor, so its k is that era's. `commit` advances `B_imm` only while `B_imm` lies deeper than the k of its own era. A fork that would replace the next block diverges at `B_imm`, so the two measure against the same k. With the tip era's k instead, as the review pointed out, a k that falls from 100 to 50 would make 51 blocks of the previous era immutable at once, pruning forks that its k still admits. A k that grows only delays commitment, and `B_imm` never moves back. While `B_imm` still lies in the previous era, an era's uncle window must also fit inside that era's finalization window, so `W_n · f_n⁻¹ ≤ s_{n−1}/5` adds to the bound within each era; with f unchanged it reads `W_n ≤ ⌊0.6·k_{n−1}⌋`. The longest-chain comparison of forks within k stays frozen, with k the smaller of the two eras' values, so k may still rise or fall: an era that changed the comparison would make the result depend on the order in which forks were seen.

## Version fields removed

Once the era follows from `slot`, the `bedrock_version` byte carries nothing, so it is removed. The version in the era's parameter record names the block layout instead. The header shrinks to 296 bytes and every block ID changes, which is possible only before genesis. The Blend message `version` byte goes too, because the identifier a message arrives on already names the era. Two routing rules replace it: a message travels over the identifiers of the era in force when it was generated, and Blend forwards a received or processed message on the era of the connection it arrived on.

## Fork choice under the common ancestor's era

Pinning fork choice to the local clock would make a node judge an old fork under a later era's density rules, depending on when it syncs. The era of the common ancestor is a function of the two chains alone. An era's fork-choice rule reads only the block tree and the slot of each block; otherwise it would be undefined on the blocks of a later era that re-encodes a field it reads.

## The transition period

The era overlap reuses Blend's Transition Period T, 30 rounds, of the previous era: the messages still crossing the network are that era's, so their traversal time follows its parameters. It must cover the drain of every protocol whose in-flight work cannot resume under the new era, and Blend messages are the only such traffic: sync streams resume through `KnownBlocks`. Nodes switch by their own clocks, so a node whose clock runs ahead ends its period up to `T_C` rounds early, `T_C` being the largest clock difference between honest nodes. A message generated just before the boundary must still reach it, so Blend now requires `T ≥ T_M + T_C`. The same bound covers Blend's own epoch boundaries. The opposite direction is a message of the new epoch reaching a node whose clock runs behind. A node releases a message it generates at the start of the next round, so no honest new-epoch message exists until one round after the earliest switch. Blend therefore requires honest clocks to differ by less than one round. An attacker can still send a new-epoch message early. It sends a valid one to a node just after that node's clock switches, and that node relays it at once to a neighbor whose clock has not. Under Blend's existing blacklist rule, that neighbor would blacklist the honest relayer for an invalid proof of quota. Now, in the last round of its epoch, a node discards such a message but keeps the connection and does not blacklist. Accepting these messages early instead is recorded below as future investigation. A sync request not served when the period ends is dropped with the previous era's identifiers, and the requesting node continues downloading under the new era, where `KnownBlocks` lets it resume after its last downloaded block. Serving open streams to their end would let a peer hold a connection of the previous era open for as long as it keeps a stream alive. A node that starts during the period runs only the era in force: it has nothing in flight from before the boundary, and what peers still send it under the previous era is retried under the new one, like a dropped sync request. Before the boundary nobody subscribes to the new era's topics. Transport connections persist, gossipsub grafts at the next heartbeat (about a second, against 30-second blocks), and Blend re-forms its network at every epoch anyway.

## State at the boundary

A node migrates state on demand, with one function. It validates a block against its parent's state migrated to the block's era. It derives an epoch's values (Epoch State, `difficulty_blend`, `epoch_pow_reward`) under the epoch's era, from state migrated to that era, and uses values an earlier epoch derived as derived. It re-validates its mempool against its tip's state migrated to the era in force, whenever the tip or the era in force changes. The state after a block is never replaced by a migrated copy, so a reorganization or a restart across a boundary migrates from the tip's own era, and nothing is migrated twice. Active messages and reward claims are verified under the era of the epoch they are for, because the rewards of an era's last epoch are claimed in the next era. A claim's acceptance window is the exception: its check and the discarding of its nullifier both use the `WINDOW` of the era of the referenced block. Each nullifier then has one fixed window, so it is never discarded while a claim on it can still pass, whichever way an era changes `WINDOW`.

An era's rules must apply to every state its migration produces. That rules out one case: a new rule that reads data only another new rule can create. An example is a new Blend that needs a new kind of SDP declaration. No migration can produce declarations that nodes have not yet made, and SDP takes a declaration into a snapshot two epochs after it is made. Such a change is staged over two eras. The first introduces the new SDP logic and leaves Blend unchanged. The second starts at least two epochs later and introduces the new Blend. A per-protocol activation delay inside one era would do the same, but the rules of a slot would then depend on more than its era, and one fork digest would no longer stand for one set of rules.

## Same-era uncle references

A carried uncle is validated as a block of its own era, so a cross-era uncle would pull the previous era's encoding and proof system into current-era validation. The rule costs nothing: the stake-inference window counts an uncle only when both it and the referencing block lie in the first `6k/f` slots of one epoch, and every era boundary is an epoch boundary. Its only effect is that blocks in an era's first 360 slots reference no uncle from before the boundary.

## Changing a published schedule

The schedule is embedded in the software because it must be known before any block of the new era exists. Two releases apply different rules from the first epoch whose era digest differs between their schedules, and the fork digest separates them from then on. A release may therefore postpone a pending era, or correct its parameters in place. Nodes of the earlier release split off at the old epoch unless they upgrade. A release may not bring a published era forward, because nodes of the earlier release would then split off before the epoch they were given to upgrade by. An emergency adds a new era instead. A correction to a pending era's rules gives the era a new version, so its record and its fork digest change; otherwise both populations would share one identifier and reject each other's blocks. Changing which era governs an epoch that has begun, or that era's record, is forbidden: a node would hold state executed under the wrong era.

## Outdated releases

A node that misses an upgrade keeps running on the old rules. The fork digest isolates it from upgraded nodes, but nothing else tells its operator, and its users keep trusting a minority chain. Peer discovery does not depend on the fork digest, so the node keeps meeting upgraded peers, and it warns its operator when one advertises a fork digest it does not know. The warning does not halt the node. A halt is not used, because a group of nodes may stay on the old era on purpose, as a hard fork, and the warning leaves that choice to their operators.

A release horizon, a constant past which a node warns, would guess at the next era instead of detecting it. It would raise a false alarm whenever a release outlived it, and repeat the fork-digest warning when a new era came first. The warnings carry no consensus effect, so the specification keeps only the one that detects the actual condition.

An emergency era can start at the next epoch boundary, up to 648,000 slots (7.5 days) away at the reference parameters. Nodes that do not upgrade split off.

## Transaction replay protection

A transaction carries the fork digest in force when it was signed, inside its hash, so a transaction signed for one fork digest is invalid on a chain that does not accept that digest. A transaction is valid under era m when it carries `F_m` or the digest of an earlier era, unless an era up to m refuses the transactions of the eras before it. A block checks it under the era of its slot, and the mempool under the era in force. Most eras change parts of the system that transactions do not touch, and invalidating transactions at their boundary would serve no purpose. An era that changes how transactions are encoded or validated refuses earlier ones, and states it with its migration. An accepted transaction is parsed under the era its digest names, so an era that keeps accepting earlier transactions keeps their format. By default, a group of nodes that stays on the old era as a hard fork keeps signing with the old digest, and its transactions stay valid on the upgraded chain. An era that expects such a split refuses earlier transactions. A transaction signed with a newer digest cannot be replayed onto a chain that did not upgrade, because its nodes do not know that digest. The Genesis transaction carries the zero digest, because every fork digest hashes the Genesis block. Each transaction grows by 32 bytes. Operation and note IDs do not change, because `op_id` hashes the operation alone.

## SDP values as era parameters

No Operation sets the minimum stake or the service parameters; the Genesis Block takes them from the node software. They are therefore era parameters, set through the parameter record. Their entries keep an `epoch`, so a value can take effect inside an era. The SDP stores leave the migrated chain state.

## Migration applied per chain

Near the tip the chain is not final, so "the state at the boundary" is not a single thing. The migration is a pure function applied per chain, composing across eras without blocks. Purity makes a reorg across a boundary need no rule: each branch migrates independently. Caches, key pools and connections are not chain state; the transition period governs them. A heavy migration runs for each live fork tip when the first new-era block on it is validated, and for the local tip when the mempool is re-validated. An implementation can cache the result, because a migration depends on the recorded chain state alone. No concrete migration exists yet, because era 0 has no previous era.

## Genesis bootstrap and accretion

The schedule is complete from era 0, so a release that dropped era-0 code still computes `era(sl) = 0` after genesis and halts at startup. Bootstrapping from genesis requires the rules of every era. Checkpoint bootstrapping needs only the eras from the checkpoint forward, so a release may drop the eras older than the oldest checkpoint it supports.

## Governance, readiness and emergency recovery

Out of scope, as agreed in review: stake-weighted approval of an era, readiness signalling, a voting mechanism, on-chain era definitions, and coordinating stake onto an emergency era. Each needs its own RFC.

## Compatibility and rollout

This PR precedes any launched network. Era 0 is today's rules. The identifier, header, Blend layout and transaction encoding changes land at a network reset, with no transition of their own. A devnet can exercise the whole mechanism with a schedule such as `[0, 3]` and an identity era.

## Open questions

- Future investigation: an early-acceptance window. From a set number of rounds before its own boundary, a node would also accept proofs built on the next epoch's inputs, and connections on the next era's identifiers. This mirrors the transition period. A late node could then relay a next-epoch message instead of discarding it, and honest clocks could differ by more than one round.
- No specification defines a canonical encoding of the recorded chain state: the checkpoint API serves it as an opaque blob. Checkpoint interoperability and migration test vectors need one.
- Domain-separation tags stay `_V1`. Whether a construction changed in era n should take `_V<n>` is for the leads.
- The implementation defers transaction replay protection to a later era (logos-blockchain/logos-blockchain#3692 was closed). Until it lands, a contentious fork at a boundary lets transactions replay across the two chains indefinitely. Whether the transaction fork digest ships at genesis, as specified, is for the leads.
- An era may change k, and forks whose depth lies between the two eras' values are compared by length under one era and rejected under the other. Whether that band needs a rule is open.
- Version-carrying file names (`bedrock-v1.1-*`, `cryptarchia-v1-*`) are not renamed.
- A pre-existing defect noticed during review, left for a separate PR: a checkpoint carries no Epoch State, yet `compute_epoch_state` recurses to genesis for D.

# Details

## 1. The era mechanism

[Bedrock Eras](../bedrock-eras.md) is the specification and should be read whole. Its upper tiers:

- **Introduction and Overview:** the purpose, then the mechanism in plain words with four diagrams on one worked example: slots, epochs and eras with migrations and transition periods; a node syncing blocks of three eras; two releases whose schedules split; an outdated release that warns on an unknown fork digest.
- **Protocol:** one part per building block (schedule and parameter records, fork and era digests, chain data, chain state, network layer, outdated releases), each opening with its objective and linking to the Details section that governs it; a numbered walk through an era boundary; the state a node keeps.

Its Details sections:

- **Notation:** `E_n`, the parameter record `P_n`, the epoch and slot lengths `L_n` and `Δ_n`, `era(sl)`, `epoch(sl)`, `first_slot(ep)`, `slot(t)`, the era in force and the fork digest `F_n`, each pointing to the function that defines it.
- **Parameters:** the era schedule.
- **Era Schedule:** an embedded list per network of (first epoch number, parameter record), the first number 0; the frozen within-k fork comparison, k the smaller of the two eras'; the rules of an era and a published era; the consequence of two releases' schedules differing; no published era moved to an earlier epoch, and no change to which era governs an epoch that has begun, or to that era's record.
- **Era Parameters:** the record: a version naming the era's rules, block layout and fields, then 33 fields in Blend, Cryptarchia and Time sections, each carrying a named constant of Blend, Cryptarchia, Total Stake Inference, SDP or Proof of Work; its canonical encoding as reference code, with ratios as written, the learning rate in double precision, `min_stake`'s epoch in eight bytes and the slot length as whole seconds followed by zero nanoseconds; the slot activation coefficient's numerator, the epoch length and the slot length at least 1; an era's uncle window within the finalization window of the era before it; the SDP stores filled from the records; a new version for any change to what a version names, so that two releases never apply different rules under one fork digest.
- **Era Boundaries:** reference code for the epoch and slot lengths read from the record's sections, each era's first slot and start time, the era and epoch of a slot, the first slot of an epoch, the slot of a time in whole seconds, and the era in force.
- **Fork Digest:** reference code for the era digest and the fork digest.
- **Era of Chain Data:** a block and everything it carries under `era(sl)`, except that a transaction is parsed under the era its fork digest names and an active message or reward claim is verified as Era Migration specifies; `slot` first and unchanged in every era; the fork digest first in every transaction, and the acceptance rule as reference code: a transaction is valid under era n when it carries the digest of n or of an earlier era, unless an era up to n refuses the transactions of the eras before it; fork choice under the common ancestor's era; the startup and checkpoint-import halt.
- **Era Migration:** a function of the recorded chain state (Mantle validation state, PoW state, SDP snapshots), stated with whether the era refuses earlier transactions; total; identity by default; the new era's rules apply to every state it produces; `migrate` as reference code, applied to the parent state of every validated block; the rules for values derived per epoch, with the Epoch State as an example; active messages and reward claims verified under the era of the epoch they are for, except for a claim's acceptance window.
- **Era Change:** the mempool rule as reference code: transactions re-validated against the local chain tip's state migrated to the era in force, whenever the tip or the era in force changes; the Era Transition Period started at an era change.
- **Era Transition Period:** the first `T` rounds after the era in force changes, `T` from the previous era's Blend Transition Period; both eras' identifiers; Blend messages validated under the arrival connection's era; afterwards the previous era's identifiers dropped and sync requests not yet served dropped with them, the requesting node continuing under the new era; a node that starts during the period runs only the era in force.
- **Network Protocol Identity:** `/logos-blockchain/<fork_digest>/<protocol>`, and `/logos-blockchain/<genesis_id>/kad` for Kademlia, with the genesis block ID in lowercase hexadecimal; identify under its libp2p identifier, with the protocol version `/logos-blockchain/<genesis_id>/identify`; generation, forwarding and publication rules; the warning on an identifier `/logos-blockchain/<fork_digest>/<protocol>` with an unknown fork digest, from a peer that announces the node's own protocol version, which skips the Kademlia identifier.

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
- [Bedrock Genesis Block](../bedrock-genesis-block.md): the Genesis Mantle Transaction carries a `fork_digest` of 32 zero bytes, is parsed under era 0, and is exempt from step 4.

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
- The test vectors whose inputs contain transaction hashes are marked `TBD`: the leaf hashes, the transaction Merkle root, both `body_root` rows and the header `block_id`. The empty-block Merkle root is unchanged. The two uncle signatures of the 2-uncle vector were made over the 297-byte headers, so they are `TBD` too.

## 4. Consensus parameters across eras

[Cryptarchia Protocol](../cryptarchia-v1-protocol.md):

- The Epoch State pseudocode takes the start of the previous epoch from the era schedule: `sl_{ep−1} := first_slot(ep−1)`.
- `on_block` compares each fork with `c_loc` under the k and s of the era of the slot of their common ancestor.
- `commit` advances `B_imm` along the local chain, one block at a time, while `B_imm` lies deeper than the k of its own era:

```diff
-define commit(T, c_loc, depth) -> (T', B_imm):
-    B_imm := block_at_depth(c_loc, depth)
+define commit(T, c_loc, B_imm) -> (T', B_imm'):
+    B_imm' := B_imm
+    while height(c_loc) - height(B_imm') > k_era(sl_B_imm'):
+        B_imm' := the child of B_imm' on the chain of c_loc
```

The rules that measure each epoch with its own era's parameters, and sum era start slots and times, are in Bedrock Eras ([§1](#1-the-era-mechanism)).

## 5. Same-era uncle rule

A new validity condition in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references), also added to the `uncle_candidates` pseudocode:

> The uncle lies in the same era as the referencing block: `era(sl_U) = era(sl_A)`.

## 6. Blend version byte removed

[Message Formatting](../message-formatting.md) and [Message Encapsulation Mechanism](../message-encapsulation.md):

```diff
 class PublicHeader:
-    version: byte,
     public_key: PublicKey,
     proof_of_quota: ProofOfQuota,
     signature: Signature
```

[Blend Protocol](../blend-protocol.md): Relaying step 1.1, the version check, is deleted. §Releasing and §Transition Period point to the era rules. §Transition Period requires `T ≥ T_M + T_C`, where `T_C` is the largest clock difference between two honest nodes, in rounds, and requires `T_C` to stay below one round. In Connectivity Maintenance, a message received in the last round of an epoch whose proof of quota is valid against the next epoch's public input carries no reaction, and Relaying step 6 defers its reaction to that rule. In Message Encapsulation, `encapsulate` and `decapsulate` no longer set `version`, the `decapsulate` offsets no longer use the undefined `Header.SIZE`, and `PAYLOAD_BODY_SIZE` equals `Max_Body_Length`.

## 7. Protocol identifiers

| Protocol | Identifier |
| --- | --- |
| Blend | `/logos-blockchain/<fork_digest>/blend` |
| Chain sync | `/logos-blockchain/<fork_digest>/chainsync` |
| Mempool topic | `/logos-blockchain/<fork_digest>/mempool` |
| Proposals topic | `/logos-blockchain/<fork_digest>/cryptarchia` |
| Kademlia | `/logos-blockchain/<genesis_id>/kad` |
| Identify | `/ipfs/id/1.0.0`, with the protocol version `/logos-blockchain/<genesis_id>/identify` |

The per-network variants are gone, because the genesis block separates networks. The placeholders are defined in Bedrock Eras ([§1](#1-the-era-mechanism)).

## 8. Synchronization and checkpoints

[Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md): each downloaded block is parsed and validated under the era of its slot. The `checkpoint_ledger_state` carries the recorded chain state of Era Migration, encoded under the era of the checkpoint block's slot. A request dropped at the end of an Era Transition Period is not a download failure.

## 9. Size cascade

The proposal maximum of 18,187 bytes propagates: [Payload Formatting](../payload-formatting.md) `Max_Body_Length = 18187`; [Message Formatting](../message-formatting.md) `Max_Payload_Length = 18190`; the Blend encapsulation-overhead figure follows, and an encapsulated message is 19,313 bytes.

## 10. Versioning section replaced

Cryptarchia's §Versioning and Protocol Upgrades, which activated upgrades by block height, is reduced to a link to Bedrock Eras.

## 11. Acceptance window and stake-inference arithmetic

- [Proof of Work](../proof-of-work.md): `WINDOW`, the acceptance window in slots, is a parameter, 300, in place of `EXPECTED_BLOCKS_PER_WINDOW` and the derivation ⌊W_b / f⌋. The window check and the discarding of nullifiers both use the `WINDOW` of the era of the referenced block's slot. [Mantle](../bedrock-v1.1-mantle-specification.md) `CLAIM_POW_REWARD` takes it from there.
- [Total Stake Inference](../cryptarchia-total-stake-inference.md): in `total_stake_inference`, `beta` and `f` are double-precision values, and their products with `PRECISION` are double-precision products.

## 12. Genesis parameters

[Bedrock Genesis Block](../bedrock-genesis-block.md): the Cryptarchia Parameters inscription gains two fields after `genesis_epoch_nonce`, and must decode to exactly five parameters.

```diff
 inscription = (chain_id_len + chain_id + genesis_time + genesis_epoch_nonce
+               + pow_reward_pool_genesis        # u64, little-endian
+               + consensus_excluded_keys)       # u32 count, then ZkPublicKeys in increasing order
```

- The initial total stake `D` leaves out the genesis notes of the keys in `consensus_excluded_keys`, and a node must not prove leadership with a note of one of them.
- `pow_reward_pool` starts at `pow_reward_pool_genesis`. [Proof of Work](../proof-of-work.md) drops the constant `POW_REWARD_POOL_GENESIS`, and the first epoch's `epoch_pow_reward` stays derived from the pool.

## Chores

- Registered Bedrock Eras in `scripts/blockchain_structure.py` (`FILE_ASSIGNMENTS`).
- Revision-history rows added to every edited specification.
- Dropped the "Current versions are `1.0.0`" sentences from P2P Network, and the "we omit the versioning" sentences from Blend and Message Encapsulation.
- Block Header Validation step 9 reduced to a pointer to Uncle References.
- Genesis Block: "hard / soft fork" wording replaced by "era change", and gas constants are no longer described as hard-coded.
- Template Cross-Channel Messaging: the example sets `fork_digest`.
- Bedrock Eras: the record's difficulty rows name their exponent `j`, and the Era Change code reads `tip.header.slot`.

# Implementation

- [x] Remove the `Version` header field and the Blend version bytes; put `slot` first ([logos-blockchain#3679](https://github.com/logos-blockchain/logos-blockchain/pull/3679))
- [x] Era schedule with parameter records; era and fork digests; identifiers from the fork digest ([#3683](https://github.com/logos-blockchain/logos-blockchain/pull/3683), [#3687](https://github.com/logos-blockchain/logos-blockchain/pull/3687), [#3689](https://github.com/logos-blockchain/logos-blockchain/pull/3689))
- [ ] Align the era record with Era Parameters (the differences listed in Discussion) and regenerate the era and fork digest vectors
- [ ] Move `reward_pool_genesis` and `consensus_excluded_keys` from the era ruleset to the Genesis block's Cryptarchia parameters, and derive the first epoch's pow reward from the pool in place of `epoch_reward_genesis`
- [ ] Drop the chain ID from the fork digest input; name Kademlia by the genesis block ID in lowercase hexadecimal, and announce `/logos-blockchain/<genesis_id>/identify` as the identify protocol version, both in place of the percent-encoded chain ID
- [ ] Reject a schedule whose record has a ratio with a zero denominator, a slot activation coefficient with numerator 0, a fractional slot length, a learning rate that is negative, negative zero or not finite, or an epoch or slot length below 1, and a schedule whose era has `W_n · f_n⁻¹` above `s_{n−1}/5`; compute ⌊k/f⌋ with integers
- [ ] Support more than one era: `era`, `epoch`, `first_slot` and `slot(t)` by summation; switch identifiers at the boundary and, for the previous era's `T` rounds, accept and open connections on both eras' identifiers; then drop the previous era's identifiers with the sync requests not yet served on them, and let the requester continue under the new era without counting the drop as a download failure; a node that starts during the period runs only the era in force
- [ ] Transaction fork digest: first field of every transaction; the acceptance rule under an era, applied by blocks and by the mempool, with each era's statement of whether it refuses earlier transactions; the zero digest at genesis, parsed under era 0; parsing by digest; reopen [#3692](https://github.com/logos-blockchain/logos-blockchain/pull/3692)
- [ ] Fork choice under the common ancestor's era, with that era's k and s; `commit` advancing `B_imm` only while it lies deeper than its own era's k
- [ ] `CLAIM_POW_REWARD`: check the acceptance window, and discard nullifiers, with the `WINDOW` of the era of the referenced block's slot
- [ ] Same-era uncle validity, in validation and in `uncle_candidates`
- [ ] Migration hook (identity for now), applied to the parent state of every validated block, and to the tip's state for mempool re-validation whenever the tip or the era in force changes; epoch derivations under the epoch's era; active messages and `CLAIM_POW_REWARD` verified under the era of the epoch they are for
- [ ] Message routing: generated messages under the era in force at generation; received and processed Blend messages, and their broadcast payloads, on the arrival connection's era; accepted proposals and admitted transactions on the era-in-force topic
- [ ] In the last round of an epoch, check a failing proof of quota against the next epoch's public input; if it passes, discard the message without closing the connection or blacklisting
- [ ] Startup and checkpoint-import halt when an era from `era(sl_B_imm)` to the era in force is not implemented; checkpoint export and import under the checkpoint block's era
- [ ] Warn the operator when a peer whose identify message announces the node's own protocol version lists an identifier, other than that of Kademlia, with an unknown fork digest
- [ ] Regenerate the Cryptarchia test vectors marked `TBD`, for transactions that carry the fork digest, and sign the two uncle headers of the 2-uncle vector
- [ ] Add or extend tests / test vectors that exercise the change, including a devnet schedule such as `[0, 3]` with an identity era
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Bedrock Eras](../bedrock-eras.md) | Created | the mechanism |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | header field removed, `slot` first, validation renumbered, same-era uncles, `first_slot`, fork choice and `commit` with per-era k, §Versioning replaced by a link, vectors `TBD` |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | header layout, encoding grammar, size derivations |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | `fork_digest` field, validation step 4, transaction-hash vectors, `WINDOW` of the referenced block's era |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | `ForkDigest` first in `MantleTx` |
| [Blend Protocol](../blend-protocol.md) | Modified | version checks removed, protocol name, era pointers, overhead figure and message size, Transition Period and clock bounds, no blacklisting for a next-epoch proof |
| [Message Formatting](../message-formatting.md) | Modified | `version` byte removed, payload maximum |
| [Message Encapsulation Mechanism](../message-encapsulation.md) | Modified | `version` field removed, decapsulation offsets, `PAYLOAD_BODY_SIZE` |
| [Payload Formatting](../payload-formatting.md) | Modified | `Max_Body_Length` |
| [Proof of Work](../proof-of-work.md) | Modified | `WINDOW` a parameter in slots, of the referenced block's era; the pool seed from the Genesis block |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | `beta` and `f` in double precision |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | `chainsync` identifier, per-era parsing, checkpoint state, dropped requests not failures |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | header field order, zero `fork_digest` exemption and era-0 parsing, pool seed and consensus-excluded keys in the Cryptarchia parameters, gas wording |
| [P2P Network](../../draft/p2p-network.md) | Modified | identifiers |
| [Template Cross-Channel Messaging](../template-cross-channel-messaging.md) | Modified | example sets `fork_digest` |
