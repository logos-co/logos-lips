# [RFC] Cryptarchia: Shorten the epoch to 60 hours

**Motivation and proposal:** [PR #TBD](https://github.com/logos-co/logos-lips/pull/TBD)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-19 |

## Reviewer Orientation

Read the PR's Motivation first. The finality window `K` stays at 36,000 slots, 10 hours, sized as before. The epoch loses its Buffer phase, its two phases read `K`, and the stake inference learns more slowly from its shorter window.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the Epoch Schedule](#1-the-epoch-schedule-has-two-phases-of-3k-slots) | why the Buffer phase can go, and what each phase still needs ([What 60 hours hold](#what-60-hours-hold)) |
| 2 | Critical | **Start here** — [Total Stake Inference](#affected-specifications): [the window and the learning rate](#2-the-stake-inference-reads-3k-and-learns-at-34) | the noise of a 30-hour window, the learning rate that contains it, and how slowly the estimate then follows a change ([The stake inference](#the-stake-inference)) |
| 3 | High | [Proof of Work](#affected-specifications): [the reward per claim](#3-proof-of-work-keeps-its-reward-per-claim) | the distribution rate that keeps the reward of a claim |
| 4 | Medium | [Blend Protocol](#affected-specifications): [the epoch's length](#4-blend-reads-the-epochs-length) | the values derived from the rounds per epoch |
| 5 | Low | [Block Rewards](#affected-specifications) | skim: two examples ([Chores](#chores)) |

# Discussion

## What 60 hours hold

The epoch has two phases of `3K`: 30 hours for the stake snapshot to become final, then 30 hours for the epoch nonce and the inferred total stake `D` to become final. Today it has three phases of 54, 54 and 72 hours.

A phase keeps its value **final in time** when [Commit](../cryptarchia-v1-protocol.md#commit) makes the value final before its first use, except with chance `1e-9`. This depends on the share of `D` that builds blocks and on the delay of each block. The figures take every block `T_M` late, 15 s. The specification states no such standard, and this RFC does not add one.

| Phase | Today | 60 hours |
| --- | --- | --- |
| Snapshot of the stake: final in time while this share of `D` builds | 13.8 % | 26.1 % |
| Nonce and inferred stake: final in time while this share of `D` builds | 10.2 % | 26.1 % |

- The `K` row's worst state is a coalition of 30 % of the total active stake that does not build, with every honest block 15 s late. The building share is then 70 %, and a phase of 13.03 hours keeps its value final in time in every state of the row. 30 hours is 2.3 times that.
- A phase of exactly `K` makes its value final only if two given slots hold blocks, a chance of at most `f²`, about 0.11 %.
- The argument that the Bootstrap rule keeps a joining node on the honest chain asks the Lottery Constants Finalization phase for at least `2K − 1` slots. A phase of `3K` meets it.
- The bound of Theorem 2 of Ouroboros Genesis on the epoch, `6·s_gen` = 27 hours, is met. The theorem itself does not cover delays above two slots.

The specification does not say what a node does when a value is not final at the end of its phase. This RFC does not change that.

### Why the Buffer phase can go

The Buffer phase was there so that an honest leader contributes to the epoch nonce after the stake snapshot is final. A coalition that could predict the nonce while it still chose its notes could grind them.

- An honest block of the chain between the snapshot slot and the cut-off suffices. The coalition fixed every note of the snapshot before that block existed. The block's contribution to the nonce cannot be predicted without its leader's key, and its parent is signed, so the contribution cannot be carried onto another fork.
- The block need not follow the snapshot's finality. A fork that changes the snapshot diverges before the snapshot slot, so it holds none of the abandoned branch's honest contributions.
- The snapshot's finality excludes only a choice between two snapshots that both survive past the cut-off. A snapshot phase of at least 13.03 hours excludes it.
- The snapshot phase holds an honest block with chance `1 − 1e-9` in every state of the `K` row once it lasts 17,268 slots, by a proved survival law. It lasts 108,000. At least 903 slots are necessary.

The Epoch Schedule states this condition in place of the Buffer row: the snapshot phase must hold a block of an honest leader on the chain, except with chance `ε`.

What the Buffer phase gave instead was length for the stake inference's window. The window ends at the cut-off and lies in one epoch, so without a Buffer phase it is at most the snapshot phase.

## The stake inference

The window is the first `3K` slots of an epoch: 30 hours in place of 108. A shorter window counts fewer slots, so each estimate is noisier. `K` holds 30 % at 15 s only while the true active stake stays within 1.094 times `D`. The chance per epoch that the noise alone breaks that limit:

| Learning rate `beta` | With this specification's rule | With a rule that computes with `f` exactly |
| --- | --- | --- |
| 1, today's | `2.2·10^-9` | `5.4·10^-8` |
| **3/4** | **`8.8·10^-15`** | **`2.1·10^-12`** |

- The specification's rule truncates `f` to thousandths, so it settles with `D` 1.03 % above the stake that builds. A rule that computes with `f` exactly settles with `D` equal to it, which leaves the limit 9.4 % away in place of 10.5 %.
- `beta` = 3/4 is the largest of 1, 3/4 and 2/3 that keeps the chance below `1e-9` under both rules. It is held as a ratio of integers, so the rule computes it exactly.
- With `beta` = 1 the window would need 113,038 slots, 31.4 hours, under this specification's rule, and 137,780 slots, 38.3 hours, under an exact rule.
- An exact computation of the inference's steady state and importance sampling of the rule in integers agree within 2 % for `beta` of 1 and 3/4. Plain Monte Carlo agrees with them on the mean, the spread and the share of epochs above 1.03 to 1.05.

What a learning rate of 3/4 costs, simulated with the rule in integers:

| | Today | 60 hours, `beta` = 3/4 |
| --- | --- | --- |
| A change of the active stake just after a cut-off is first corrected | 252 h later, in one step | 90 h later |
| After the stake that builds halves, `D` is still off by | 1.2 % at 252 h | 26 % at 90 h, 6.7 % at 150 h, 1.9 % at 210 h |
| After the stake that builds falls by a tenth, `D` is still off by | 0.7 % at 252 h | 2.9 % at 90 h, 1.2 % at 150 h |
| After the active stake doubles, `D` is low enough to break the limit of 1.094 until | the correction at 252 h | the second correction, at 150 h |
| A coalition of 30 % that withholds every block brings `D` to where it settles on the honest stake | in one window, 3,934 wins | to within 11 %, 3 % and 1 % after one, two and three windows, 1,093 wins each |
| Noise of `D`, one standard deviation | 0.87 % | 1.28 % |
| Chance that a chain misses the floor of 689 occupied slots in `K` | `1.4·10^-8` | `3.7·10^-8` |

- The floor is sized while the stake that builds equals `D`. The noise and the rule's 1 % offset already put the chance of missing it above `1e-9` today. Missing the floor delays finality past `K`. It never makes a block immutable early. With a rule that computes with `f` exactly the chance is `7.8·10^-9`.

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
- **Blend admission by proof of work.** A solution's ticket hashes the epoch nonce, so a solution serves one epoch, 60 hours in place of 180. It can be searched only once the nonce is read at the cut-off, 30 hours before the epoch in place of 72.
- **Leader rewards.** The vouchers of an epoch enter the voucher tree together in the first block of the next epoch. An epoch holds 7,200 blocks on average in place of 21,600, and that is the smallest set a voucher hides in.
- **Service declarations.** A message takes effect at the start of the second epoch after its block, so it waits one to two epochs: 60 to 120 hours in place of 180 to 360.
- **Storage markets.** The price may still change by up to 12.5 % per epoch, now every 60 hours.
- **Block rewards.** Its chosen time step is one block. Only its examples of a one-epoch time step change ([Chores](#chores)).
- **Analyses.** [\[Analysis\] Total Stake Inference](../analysis-total-stake-inference.md) studies a window of `6k/f` slots with `beta` = 1, and [\[Analysis\] Resilience and Anonymity](../analysis-resilience-and-anonymity.md) an epoch of 648,000 slots. This RFC does not change them.

## Alternatives

| Schedule | Epoch | Better than this RFC | Worse than this RFC |
| --- | --- | --- | --- |
| Today | 180 h | keeps every margin | new stake waits up to 360 h, `D` uncorrected for up to 252 h |
| `3K`, `3K`, `4K`, `beta` = 1 | 100 h | keeps the Buffer phase and the inference as it is, with a 60-hour window; the nonce and the inferred stake are final in time down to 19.0 % | 40 hours longer |
| No Buffer phase, `2K` + `2K`, `beta` = 2/3 | 40 h | 20 hours shorter: new stake waits 40 to 80 h, a change is first corrected after 60 h, and a doubling breaks the limit until 100 h | phases final in time down to 41.3 %; 25 % of targets meet two nonces, a grinding gain of 1.49 %; an epoch holds 4,800 blocks |
| No Buffer phase, `1.5K` + `2K`, `beta` = 1/2 | 35 h | 25 hours shorter | the snapshot phase is final in time down to 58.5 %; the 15-hour window needs `beta` = 1/2: after a halving, `D` is 50 % off at 55 h and 13 % at 125 h |
| No Buffer phase, `1.5K` + `1.5K` | 30 h | 30 hours shorter | the Lottery Constants Finalization phase is below `2K − 1` |
| `K`, `K`, `K` | 30 h | 30 hours shorter, and keeps the Buffer phase | phases of exactly `K` make their values final with chance at most 0.11 % |
| 60 hours with `beta` = 1 | 60 h | keeps the inference's rule | noise breaks the limit with `2.2·10^-9` per epoch, `5.4·10^-8` with an exact rule |

- **Keep `ρ` at 1/200 per epoch.** The reward of a claim then rises 3 times, and the pool pays out 51.9 % of itself a year in place of 21.6 %.
- **Keep 180 hours and take the snapshot later.** New stake would wait less, but nothing else shortens, and the rule on eligible notes changes.
- **Give the lottery its own cycle, apart from the epoch other protocols read.** It adds a second clock that every reader must name.

## Compatibility

This is a consensus change. Nodes with a different epoch compute different epoch states, so a network runs one schedule. Every epoch boundary, the cut-off slot, `PERIOD` and the learning rate change, and so do the per-epoch values of proof of work and Blend. No header or wire format changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from [`slot-finality/epoch`](https://github.com/logos-blockchain/research/tree/a78ca91adf493a2b11d299601867f4655c7c0d5f/tools/simulators/finality/slot-finality/epoch) of the research repository at commit `a78ca91`. The README of `slot-finality` lists the review's scripts with their stored outputs, and section 7 of `schedule/SCHEDULE.md` lists the schedule's.

- `REVIEW.md` proves the shares at which a phase is final in time, the honest block a span needs, and the bounds behind the condition on the Lottery Constants Finalization phase. `proofs/survival/SURVIVAL.md` proves the survival law, and `proofs/genesis/GENESIS.md` the argument for the Bootstrap rule that asks for that condition.
- `schedule/SCHEDULE.md` gives why the Buffer phase can go, the learning rate and its simulations, the costs of each schedule in [Alternatives](#alternatives), the grinding gain and Blend's reward lottery.

The bounds hold in the specification's own model of the floor, and the mapping of each state of the `K` row to a building share and a delay is the review's.

# Details

## 1. The Epoch Schedule has two phases of 3K slots

In the [Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule), the Buffer phase is removed and the two remaining phases read `K`:

```diff
-An epoch is divided into 3 phases, as outlined below.
+An epoch is divided into 2 phases, as outlined below.
-| Stake Distribution Snapshot | 3⌊k/f⌋ slots | ...
-| Buffer phase | 3⌊k/f⌋ slots | ...
-| Lottery Constants Finalization | 4⌊k/f⌋ slots | On the 6⌊k/f⌋th slot into the epoch, ...
+| Stake Distribution Snapshot | 3K slots | ...
+| Lottery Constants Finalization | 3K slots | On the 3Kth slot into the epoch, ...
```

- The epoch length is `3K + 3K = 6K` slots. With `K = 36000`, an epoch lasts 216,000 slots.
- In [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode), the slot at which the epoch nonce is read and the end of the inference's window read `3K`.
- The sentence "Each phase that waits for a value to finalize must last at least the finality window `K` …" is removed from the Epoch Schedule.
- The Epoch Schedule adds: the Stake Distribution Snapshot phase must hold a block of an honest leader on the chain, except with the chance `ε` of [Finality Floor](../cryptarchia-v1-protocol.md#finality-floor), or a coalition that predicts the epoch nonce can grind its notes.
- The `K` row of [Constants](../cryptarchia-v1-protocol.md#constants) says that `K` also sets the Epoch Schedule. It no longer says that `K` must not exceed a phase of the Epoch Schedule that waits for a value to finalize.

## 2. The stake inference reads 3K and learns at 3/4

In [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) of the Total Stake Inference:

- `PERIOD` is `3K` in place of `6⌊k/f⌋`. The document inherits `K` in place of `k`.
- `beta` is 3/4 in place of 1.0. Its numerator and denominator are integers. Its row says that it is derived together with `PERIOD`, and that a change of `PERIOD` requires it to be derived again.

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

- [ ] Set the epoch's two phases to `3K` slots each, without the Buffer phase, the cut-off and `PERIOD` to `3K`, and the epoch to 216,000 slots
- [ ] Hold the learning rate as the ratio 3/4 and apply it as `(beta.num × error) / beta.den`
- [ ] Set `EXPECTED_BLOCKS_PER_EPOCH` to 7,200 and `EPOCH_POW_DISTRIBUTION_RATE_DEN` to 600
- [ ] Derive Blend's core quota and nullifier cache from 216,000 rounds
- [ ] Add tests: the epoch boundaries, the cut-off slot and the inference's window at `K = 36,000`; the inference's correction at `beta` = 3/4; and the reward of a claim before and after the change
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.5.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.3.0 |
| [Proof of Work](../proof-of-work.md) | Modified | 1.2.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.9.0 |
| [Block Rewards](../block-rewards.md) | Modified | 1.2.1 |
