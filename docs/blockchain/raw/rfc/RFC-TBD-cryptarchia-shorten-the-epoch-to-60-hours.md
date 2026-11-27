# [RFC] Cryptarchia: Shorten the epoch to 60 hours

**Motivation and proposal:** [PR #TBD](https://github.com/logos-co/logos-lips/pull/TBD)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first. The finality window `K` stays at 36,000 slots, 10 hours, sized as before. The epoch loses its Buffer phase and keeps 60 hours in two phases. The first, `4K`, is the stake snapshot's phase and the stake inference's window. The second, `2K`, lets the epoch nonce and the inferred total stake become final. The inference learns at 1/2, so that one window without blocks cannot take the inferred total stake below what `K` holds.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the Epoch Schedule](#1-the-epoch-schedule-has-phases-of-4k-and-2k-slots) | why the Buffer phase can go, what each phase still needs, and why the window gets the longer phase ([What 60 hours hold](#what-60-hours-hold), [The split of 60 hours](#the-split-of-60-hours)) |
| 2 | Critical | **Start here** — [Total Stake Inference](#affected-specifications): [the window and the learning rate](#2-the-stake-inference-reads-4k-and-learns-at-12) | the bound on the learning rate, and how slowly the estimate then follows a change ([The stake inference](#the-stake-inference)) |
| 3 | High | [Proof of Work](#affected-specifications): [the reward per claim](#3-proof-of-work-keeps-its-reward-per-claim) | the distribution rate that keeps the reward of a claim |
| 4 | Medium | [Blend Protocol](#affected-specifications): [the epoch's length](#4-blend-reads-the-epochs-length) | the values derived from the rounds per epoch |
| 5 | Low | [Block Rewards](#affected-specifications) | skim: two examples ([Chores](#chores)) |

# Discussion

## What 60 hours hold

The epoch has two phases. The first lasts `4K`, 40 hours, for the stake snapshot to become final. It ends at the **cut-off**, the slot at which the epoch nonce and the inferred total stake `D` of the next epoch are read. The second phase lasts `2K`, 20 hours, for those values to become final. Today the epoch has three phases of 54, 54 and 72 hours.

A phase keeps its value **final in time** when [Commit](../cryptarchia-v1-protocol.md#commit) makes the value final before its first use, except with chance `1e-9`. This depends on the share of `D` that builds blocks and on the delay of each block. The table takes every block `T_M` late, 15 s. The specification states no such standard. This RFC does not add one.

| Phase | Today | 60 hours |
| --- | --- | --- |
| Snapshot of the stake: final in time while this share of `D` builds | 13.80 % | 19.02 % |
| Nonce and inferred total stake: final in time while this share of `D` builds | 10.20 % | 41.35 % |

- The lowest share of `D` that builds in a state of the `K` row is 63 %, with every block 10 s late. In that state a coalition of 30 % of the total active stake does not build, and a tenth of the honest stake is offline before `D` corrects for it.
- A coalition can also build a private chain before a phase starts and release it during the phase. The honest blocks that the released chain overtakes then do not count. Counting such a lead, a phase of about 47,600 slots, 13.2 hours, keeps its value final in time in every state of the `K` row. 20 hours is 1.5 times that.
- A phase of exactly `K` makes its value final only if two given slots hold blocks, a chance of at most `f²`, about 0.11 %.
- The argument that the Bootstrap rule keeps a joining node on the honest chain asks the Lottery Constants Finalization phase for at least `2K − 1` slots. A phase of `2K` meets it. A closer reading of the argument, not yet reviewed, needs only `K − 1` slots.
- The bound of Theorem 2 of Ouroboros Genesis on the epoch, `6·s_gen` = 27 hours, is met. The theorem itself does not cover delays above two slots.
- At launch `D` starts from its genesis value. If only 30 % of it builds, the first epoch's nonce and inferred total stake become final about 26 hours after the cut-off, at 15 s. That is 6 hours after their first use. A fork from before that cut-off, made by a coalition of 30 % of the stake that builds, is then still alive at the first use with chance `3·10^-15`.

The specification does not say what a node does when a value is not final at the end of its phase. This RFC does not change that.

### Why the Buffer phase can go

The Buffer phase was there so that an honest leader contributes to the epoch nonce after the stake snapshot is final. That order rules out two attacks.

- **Grinding.** A coalition that could predict the nonce while it still chose its notes could grind them. An honest block of the chain between the snapshot slot and the cut-off is enough to stop this. The coalition fixed every note of the snapshot before that block existed. The block's contribution to the nonce cannot be predicted without its leader's key. Its parent is signed, so the contribution cannot be carried onto another fork. The block need not follow the snapshot's finality. A fork that changes the snapshot diverges before the snapshot slot, so it holds none of the abandoned branch's honest contributions.
- **A choice between snapshots.** A coalition can keep two branches alive from before the snapshot slot, each with its own notes. Once the last honest block before the cut-off is public, the coalition knows both nonces. It can then pick one. The choice ends when a block of the epoch becomes immutable at an honest node. So the snapshot must be final at every honest node before the last honest block of the phase. Both conditions hold together, except with `1e-9` in every state of the `K` row, once the phase lasts about 65,000 slots, 18 hours. The phase lasts 144,000.

The snapshot phase holds an honest block with chance `1 − 1e-9` in every state of the `K` row once it lasts 17,709 slots. At least 971 slots are necessary.

The Epoch Schedule states the first condition in place of the Buffer row: the snapshot phase must hold a block of an honest leader on the chain, except with chance `ε`. The specification does not state the second condition. Its phase table asks only that the snapshot be final before the next phase starts.

What the Buffer phase gave instead was length for the stake inference's window. The window ends at the cut-off and lies in one epoch, so without a Buffer phase it is at most the snapshot phase. This RFC gives it the whole phase.

### The split of 60 hours

Two phases that are whole multiples of `K` and at least `2K` each fill 60 hours in three ways. A phase of `K` is too short for either role, which rules out `K` + `5K` and `5K` + `K`. Each of the three splits keeps every rule above. The split moves length between the inference's window and the last phase.

| | `2K` + `4K` | `3K` + `3K` | **`4K` + `2K`** |
| --- | --- | --- | --- |
| A halt of all blocks within one window takes the active stake past 1.094 times `D`, `K`'s limit at 15 s, from (`beta` = 1/2) | 3.4 h | 5.2 h | **6.9 h** |
| Income a coalition of 30 % gives up to keep `D` on the honest stake, by withholding in every window | 5.0 % | 28.7 % | **52.5 %** |
| A change of the active stake just after a cut-off is first corrected | 100 h later | 90 h later | **80 h later** |
| The next epoch's nonce is known before the epoch by | 40 h | 30 h | **20 h** |
| The last phase is final in time while this share of `D` builds | 19.02 % | 26.05 % | **41.35 %** |
| A halt within the last phase that it absorbs in every state of the `K` row | 26.8 h | 16.8 h | **6.8 h** |

- `4K` + `2K` gives the window the most length. Its last phase keeps its values final in time with room: the lowest building share of the `K` row is 63 %, against 41.35 % needed.
- The targets that meet two nonces, the gain from choosing among nonces, the wait of new stake, and the per-epoch values of proof of work and Blend depend only on the epoch's length. They are the same in all three splits.
- A nonce known 20 hours ahead leaves less time for work that a nonce lets a node do in advance, such as searching for Blend admission tickets.

## The stake inference

The window, the observation period of the Total Stake Inference, is the first `4K` slots of an epoch: 40 hours in place of 108.

The rule moves `D` by the share `beta` of the error it measures: `D' = D · ((1 − beta) + beta · N / (PERIOD · f))`, for `N` occupied slots in the window. A window without an occupied slot lowers `D` to `(1 − beta) · D`. A window can lose a share `y` of its blocks to a halt, to stake that goes offline, or to a coalition that withholds its blocks. If `D` was right before, the total active stake is then `1 / (1 − beta · y)` times `D` in the next epoch.

`K` holds a coalition of 30 % only while the total active stake is at most 2.097 times `D` with every block 10 s late. With every block 15 s late, the limit is 1.094 times `D`. With `beta` = 1/2, one window lowers `D` by at most half, so the total active stake reaches at most twice `D`. This keeps the first limit for any loss within one window, if `D` was at most 4.6 % below the total active stake before. The specification's rule leaves `D` that low with chance `2·10^-12` per epoch. A rule that computes with `f` exactly does so with chance `5·10^-9`. A coalition that withholds its blocks before the window keeps `D` on the honest stake. A halt then takes the total active stake to 2.86 times `D`. That combines two disturbances, and the `K` row covers one at a time. The specification bounds `beta` by the first limit, and 1/2 meets it.

What one window of lost blocks does:

| | Today: 108-hour window, `beta` = 1 | `3K` + `3K`, `beta` = 3/4 | `4K` + `2K`, `beta` = 1 | **`4K` + `2K`, `beta` = 1/2** |
| --- | --- | --- | --- | --- |
| Total active stake over `D` after a window without blocks | unbounded | 4 | unbounded | **2** |
| A halt within one window takes it past 2.097, the limit at 10 s, from | 56.5 h | 20.9 h | 20.9 h | **never** |
| A halt within one window takes it past 1.094, the limit at 15 s, from | 9.3 h | 3.4 h | 3.4 h | **6.9 h** |
| Largest total active stake over `D` after a halt of 24 h, at any time of the epoch | 1.29 | 2.50 | 2.50 | **1.43** |
| Total active stake over `D` after a coalition of 30 % withholds one window, under the specification's rule | 1.41 | 1.27 | 1.41 | **1.16** |

- The halt rows take `D` right before the halt.
- Today `beta` is 1, and the long window is what keeps a halt of up to 56 hours within the limit at 10 s. With `beta` = 1, a window without blocks takes `D` to its floor of one unit.
- The halt rows take the coalition to halt too. A coalition that keeps building through a halt of the honest stake gains a private lead, which `K` is not sized for, under any split and any `beta`.
- Two windows in a row without blocks need a halt of at least 100 hours. They take the total active stake to 4 times `D`.

The noise of a 40-hour window does not limit `beta`. With `beta` = 1/2, `D` has a standard deviation of 0.83 %, against 0.87 % today. The chance per epoch that the noise alone takes the total active stake past 1.094 times `D` is about `2·10^-33`. Averaged over the noise, the chance per block that a coalition of 30 % displaces a block after 10 hours at 15 s is `2.21·10^-10` under the specification's rule. It is the same today. Under a rule that computes with `f` exactly it is `2.53·10^-10`, against `2.50·10^-10` with `D` exact.

- The specification's rule truncates `f` to thousandths, so it settles with `D` 1.03 % above the stake that builds. A rule that computes with `f` exactly settles with `D` equal to it.
- `D` counts the wins it sees. Uncles recover only forks of depth one, so some wins go uncounted, and `D` settles low by their share. By simulation the share is 0.13 % at Blend's design delays and 0.26 % at a mean delay of 15 s. Deliveries timed to split the honest leaders raise it to about 7 % at 15 s. `K` then holds at about `7.5·10^-10`. These shares are the same for every split and every `beta`.

What a learning rate of 1/2 costs, under the specification's rule. The figures follow the mean path of `D`, without its noise.

| | Today | 60 hours, `beta` = 1/2 |
| --- | --- | --- |
| A change of the active stake just after a cut-off is first corrected | 252 h later, in one step | 80 h later, by half of the error each epoch |
| After the stake that builds halves, `D` is still off by | 0.8 % at 252 h | 50 % at 80 h, 25 % at 140 h, 13 % at 200 h |
| After the stake that builds falls by a tenth, `D` is still off by | 0.2 % at 252 h | 5.6 % at 80 h, 2.9 % at 140 h, 1.5 % at 200 h |
| After the active stake doubles, `D` is low enough to break the limit of 1.094 until | the correction at 252 h | the third correction, at 200 h |
| A coalition of 30 % that withholds every block brings `D` to where it settles on the honest stake | in one window, withholding 3,894 wins | to within 22 %, 11 %, 6 % and 3 % after one to four windows, withholding 1,442, 1,692, 1,854 and 1,948 wins in turn |
| Daily growth of the active stake that `K` holds at 15 s, with new stake joining at epoch boundaries | 1.32 % | 2.03 % |
| Noise of `D`, one standard deviation | 0.87 % | 0.83 % |
| Chance that a chain misses the floor of 689 occupied slots in `K` | `1.4·10^-8` | `1.3·10^-8` |

- After the stake halves, `D` is too high, so slots are occupied more slowly than `f`. At mean rates with blocks 10 s late, finality then takes about 13.3 hours until the first correction under any `beta`. It takes 10.5 hours for the next 60 hours with `beta` = 1/2. A chain that misses the floor delays finality past `K`. It never makes a block immutable early.
- At launch, if only 30 % of the genesis `D` builds, the stake that builds is 0.46, 0.63, 0.76 and 0.86 times `D` after one to four windows. With `beta` = 1 it is 0.98 after one window.
- The floor is sized while the stake that builds equals `D`. The noise and the rule's 1 % offset already put the chance of missing it above `1e-9` today. With a rule that computes with `f` exactly, the chance is `2.5·10^-9`.

## The epoch nonce

The epoch nonce stays as it is.

| | Today | 60 hours |
| --- | --- | --- |
| Cut-offs a year | 48.7 | 146 |
| Targets whose race of `K` slots meets two nonces | 5.6 % | 16.7 % |
| Blocks a coalition of 30 % gains by choosing among at most `2^16` nonces, at 10 s and 15 s | 0.70 %, 0.82 % | 1.21 %, 1.43 % |
| The same, in blocks a year at 10 s | 2,230 | 3,870 |

- The share of targets that meet two nonces is `K` divided by the epoch's length. Against an attack that meets two ground nonces, a 10-hour `K` proves 24.7 to 27.9 % of the total active stake with today's nonce, by the state of the `K` row. That case now covers 16.7 % of targets.
- The gain takes the number of nonces a coalition holds at a cut-off as independent of the epoch's length. The bound behind the shares that a 10-hour `K` holds with today's nonce is taken as independent of the gap from the cut-off to the next epoch, as long as the cut-off is final in time. Neither is derived for epochs other than 180 hours.

## New stake and the other readers of the epoch

A note may lead once it was in the note set at the beginning of the previous epoch. New stake therefore waits one to two epochs before it can lead: 60 to 120 hours in place of 180 to 360.

Every other specification that reads the epoch keeps its rules per epoch:

- **Proof of work.** `EXPECTED_BLOCKS_PER_EPOCH` is the epoch's length times `f`, 7,200. The distribution rate `ρ` is 1/600 per epoch. The reward of a claim divides the pool by `EPOCH_POW_DISTRIBUTION_RATE_DEN · TARGET_CLAIMS_PER_BLOCK · EXPECTED_BLOCKS_PER_EPOCH`, 43,200,000 as today. So the reward of a claim does not change, and at the target rate the pool pays out 21.6 % of itself a year before refills, as today. `difficulty_blend` may move by a factor of 2 every 60 hours, and reads the transactions of 7,200 expected blocks.
- **Blend.** An epoch lasts 216,000 rounds. The core quota is derived from the rounds per epoch, so a core node gets 1/3 of today's quota per epoch and the same number of cover messages per hour. The nullifier cache needs about 111 MB. A node rebuilds its connections and sends its active message once per epoch, 3 times as often per hour. The activity threshold of the reward lottery reads the cover messages of an epoch. Counting only the tokens of cover traffic, a core node at 10,000 core nodes wins a base reward with chance 0.19 per epoch, or 0.48 over 180 hours, against 0.89 per epoch today. The chance falls below a half from 8,192 core nodes, against 16,384, and the threshold is 0 for every count from 262,144 core nodes, against 972,000. Blend's sensitivity `θ` is not derived again here.
- **Blend admission by proof of work.** A solution's ticket hashes the epoch nonce, so a solution serves one epoch, 60 hours in place of 180. It can be searched only once the nonce is read at the cut-off, 20 hours before the epoch in place of 72.
- **Leader rewards.** The vouchers of an epoch enter the voucher tree together in the first block of the next epoch. An epoch holds 7,200 blocks on average in place of 21,600, and that is the smallest set a voucher hides in.
- **Service declarations.** A message takes effect at the start of the second epoch after its block, so it waits one to two epochs: 60 to 120 hours in place of 180 to 360.
- **Storage markets.** The price may still change by up to 12.5 % per epoch, now every 60 hours.
- **Block rewards.** Its chosen time step is one block. Only its examples of a one-epoch time step change ([Chores](#chores)).
- **Analyses.** [\[Analysis\] Total Stake Inference](../analysis-total-stake-inference.md) studies a window of `6k/f` slots with `beta` = 1, and [\[Analysis\] Resilience and Anonymity](../analysis-resilience-and-anonymity.md) an epoch of 648,000 slots. This RFC does not change them.

## Alternatives

| Schedule | Epoch | Better than this RFC | Worse than this RFC |
| --- | --- | --- | --- |
| Today | 180 h | keeps every margin; a halt of up to 56 h within one window keeps `D` within what `K` holds at 10 s | new stake waits up to 360 h, and `D` stays uncorrected for up to 252 h |
| `3K`, `3K`, `4K`, `beta` = 1 | 100 h | keeps the Buffer phase and the inference's rule, with a 60-hour window; the last phase is final in time down to 19.02 % | 40 hours longer; a halt of 31.4 h within one window takes the total active stake past 2.097 times `D` |
| No Buffer phase, `3K` + `3K`, `beta` = 3/4 | 60 h | the last phase is final in time down to 26.05 %; the nonce is known 30 hours before the epoch, 10 hours earlier, for work done in advance | a halt of 20.9 h within one window takes the total active stake past 2.097 times `D`; keeping `D` on the honest stake costs a coalition 28.7 % of its income, against 52.5 % |
| No Buffer phase, `4K` + `2K`, `beta` = 1 | 60 h | keeps the inference's rule; corrects a change in one step, 80 h after it; holds a daily growth of 4.01 % at 15 s | a window without blocks takes `D` to one unit; a halt of 20.9 h within one window takes the total active stake past 2.097 times `D` |
| `4K` + `2K`, `beta` = 1, and `D` falls by at most a quarter per window | 60 h | the total active stake reaches at most 4/3 of `D` after a window without blocks; a rise is corrected in one step; after a halving `D` is 12 % off at 140 h | a new rule in the inference, which bounds each correction from below |
| No Buffer phase, `2K` + `2K` | 40 h | 20 hours shorter: new stake waits 40 to 80 h | the snapshot phase is final in time only down to 41.35 %, and has only about 7,000 slots more than dropping the Buffer phase needs; 25 % of targets meet two nonces, a grinding gain of 1.48 %; an epoch holds 4,800 blocks |
| No Buffer phase, `1.5K` + `2K` | 35 h | 25 hours shorter | the snapshot phase, 54,000 slots, is shorter than dropping the Buffer phase needs, about 65,000 |
| No Buffer phase, `1.5K` + `1.5K` | 30 h | 30 hours shorter | the snapshot phase is too short, as for `1.5K` + `2K` |
| `K`, `K`, `K` | 30 h | 30 hours shorter, and keeps the Buffer phase | phases of exactly `K` make their values final with chance at most 0.11 % |

- **Keep `ρ` at 1/200 per epoch.** The reward of a claim then rises 3 times, and the pool pays out 51.9 % of itself a year in place of 21.6 %.
- **Keep 180 hours and take the snapshot later.** New stake would wait less, but nothing else shortens, and the rule on eligible notes changes.
- **Give the lottery its own cycle, apart from the epoch other protocols read.** It adds a second clock that every reader must name.

## Compatibility

This is a consensus change. Nodes with a different epoch compute different epoch states, so a network runs one schedule. Every epoch boundary, the cut-off slot, `PERIOD` and the learning rate change, and so do the per-epoch values of proof of work and Blend. No header or wire format changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from [`slot-finality/epoch`](https://github.com/logos-blockchain/research/tree/3bbdc271d13d8f67655b72969cf747bbdec39ff0/tools/simulators/finality/slot-finality/epoch) of the research repository at commit `3bbdc27`. The README of `slot-finality` lists the scripts with their stored outputs.

- `split/SPLIT.md` gives the split of 60 hours, the bound on the learning rate, what a window of lost blocks does, the noise of `D`, the costs of `beta` = 1/2, the lengths that count a coalition's private lead, and the condition for dropping the Buffer phase. It lists where each figure of this RFC comes from, and corrects sections 3 and 4 of `schedule/SCHEDULE.md`.
- `REVIEW.md` proves the shares at which a phase is final in time, the honest block a span needs, and the bounds behind the condition on the Lottery Constants Finalization phase. `proofs/survival/SURVIVAL.md` proves the survival law, and `proofs/genesis/GENESIS.md` the argument for the Bootstrap rule that asks for that condition. `proofs/genesis-step2/` gives the closer reading, not yet reviewed, that needs only `K − 1` slots.
- The limits of 2.097 and 1.094 come from the study's bound on how long a block waits, as for `K` itself.

The bounds hold in the specification's own model of the floor. The mapping of each state of the `K` row to a building share and a delay is the review's. Where its two readings of the offline state differ, this RFC takes the one that needs more: `D` before it corrects for the offline stake.

# Details

## 1. The Epoch Schedule has phases of 4K and 2K slots

In the [Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule), the Buffer phase is removed and the two remaining phases read `K`:

```diff
-An epoch is divided into 3 phases, as outlined below.
+An epoch is divided into 2 phases, as outlined below.
-| Stake Distribution Snapshot | 3⌊k/f⌋ slots | ...
-| Buffer phase | 3⌊k/f⌋ slots | ...
-| Lottery Constants Finalization | 4⌊k/f⌋ slots | On the 6⌊k/f⌋th slot into the epoch, ... We wait another 4⌊k/f⌋ slots ...
+| Stake Distribution Snapshot | 4K slots | ...
+| Lottery Constants Finalization | 2K slots | On the 4Kth slot into the epoch, ... We wait another 2K slots ...
```

- The epoch length is `4K + 2K = 6K` slots. With `K = 36000`, an epoch lasts 216,000 slots.
- In [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode), the slot at which the epoch nonce is read and the end of the inference's window read `4K`.
- The sentence "Each phase that waits for a value to finalize must last at least the finality window `K` …" is removed from the Epoch Schedule.
- The Epoch Schedule adds: the Stake Distribution Snapshot phase must hold a block of an honest leader on the chain, except with the chance `ε` of [Finality Floor](../cryptarchia-v1-protocol.md#finality-floor), or a coalition that predicts the epoch nonce can grind its notes.
- The `K` row of [Constants](../cryptarchia-v1-protocol.md#constants) says that `K` also sets the Epoch Schedule. It no longer says that `K` must not exceed a phase of the Epoch Schedule that waits for a value to finalize.

## 2. The stake inference reads 4K and learns at 1/2

In [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) of the Total Stake Inference:

- `PERIOD` is `4K` in place of `6⌊k/f⌋`. The document inherits `K` in place of `k`.
- `beta` is 1/2 in place of 1.0. Its numerator and denominator are integers. Its row states three things:
  - `beta` must not exceed `1 − 1/2.097`;
  - `K` meets its targets at its delay `Δ` only while the total active stake is at most 2.097 times the estimate, and with a larger `beta` one observation period without an occupied slot lets the total active stake exceed that;
  - a change of `K` or of its targets requires `beta` to be derived again.

In the [Algorithm](../cryptarchia-total-stake-inference.md#algorithm):

```diff
+    // beta.num: u64, beta.den: u64
     // f: f64
     # ...
-    let beta_p: u64 = truncate(beta * PRECISION)
     let f_p: u64 = truncate(f * PRECISION)
     # ...
-        let correction_p: i128 = (beta_p * slot_activation_error_p) / PRECISION;
+        let correction_p: i128 = (beta.num as i128 * slot_activation_error_p) / (beta.den as i128);
```

## 3. Proof of work keeps its reward per claim

In [Parameters](../proof-of-work.md#parameters):

```diff
-EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 200
+EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 600
 TARGET_CLAIMS_PER_BLOCK: uint64 = 10            # T
-EXPECTED_BLOCKS_PER_EPOCH: uint64 = 21_600      # N_b = 10 k
+EXPECTED_BLOCKS_PER_EPOCH: uint64 = 7_200       # N_b = 6 K f
```

- [Notation](../proof-of-work.md#notation) defines `K`, 36,000 slots, in place of `k`.
- The Parameters add: `EPOCH_POW_DISTRIBUTION_RATE_DEN` · `EXPECTED_BLOCKS_PER_EPOCH` is 4,320,000, so that at the target rate the pool pays out 1/4,320,000 of itself per expected block. A change of the epoch length changes `EXPECTED_BLOCKS_PER_EPOCH`, and `EPOCH_POW_DISTRIBUTION_RATE_DEN` must keep the product, or the reward of a claim changes.

## 4. Blend reads the epoch's length

- [Time](../blend-protocol.md#time): an epoch lasts the epoch length of the Epoch Schedule, 216,000 slots, or 7,200 blocks on average.
- [Global Parameters](../blend-protocol.md#global-parameters): `E` is 216,000 rounds, the epoch length of the Epoch Schedule.
- [Leadership Quota](../blend-protocol.md#leadership-quota): `L_Avg = E · F_D = 216000/30 = 7200`.
- [Relaying](../blend-protocol.md#relaying-2): the nullifier cache needs at least `(216000 + 30) · (1 + 130/30) · 3 · 32 = 110607360` bytes, about 111 MB.

## Chores

- [Block Rewards](../block-rewards.md): the two examples of a one-epoch time step read an epoch of 60 hours: `Δ_t = 1/146` and `f = 7200`.
- [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode): the comment on the inferred total stake names the Stake Distribution Snapshot phase in place of "the stake freezing phase".

# Implementation

- [ ] Set the epoch's phases to `4K` and `2K` slots, without the Buffer phase, the cut-off and `PERIOD` to `4K`, and the epoch to 216,000 slots
- [ ] Hold the learning rate as the ratio 1/2 and apply it as `(beta.num × error) / beta.den`
- [ ] Set `EXPECTED_BLOCKS_PER_EPOCH` to 7,200 and `EPOCH_POW_DISTRIBUTION_RATE_DEN` to 600
- [ ] Derive Blend's core quota and nullifier cache from 216,000 rounds
- [ ] Add tests: the epoch boundaries, the cut-off slot and the inference's window at `K = 36,000`; the inference's correction at `beta` = 1/2, including a window with no occupied slot; and the reward of a claim before and after the change
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.5.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.3.0 |
| [Proof of Work](../proof-of-work.md) | Modified | 1.2.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.9.0 |
| [Block Rewards](../block-rewards.md) | Modified | 1.2.1 |
