# [RFC] Cryptarchia: Shorten the epoch to 100 hours

**Motivation and proposal:** [PR #TBD](https://github.com/logos-co/logos-lips/pull/TBD)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-18 |

## Reviewer Orientation

Read the PR's Motivation first. The finality window `K` stays at 36,000 slots, 10 hours, sized as before. The phases of the epoch now read `K`, and every value that reads the epoch's length follows.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol, Total Stake Inference](#affected-specifications): [the Epoch Schedule](#1-the-epoch-schedule-reads-the-finality-window) | the share of the inferred stake each phase still needs, the inference's noise and the choice among nonces ([What 100 hours hold](#what-100-hours-hold), [The stake inference](#the-stake-inference), [The epoch nonce](#the-epoch-nonce)) |
| 2 | High | [Proof of Work](#affected-specifications): [the reward per claim](#2-proof-of-work-keeps-its-reward-per-claim) | the distribution rate that keeps the reward of a claim, and the relation the Parameters now state |
| 3 | Medium | [Blend Protocol](#affected-specifications): [the epoch's length](#3-blend-reads-the-epochs-length) | the values derived from the number of rounds per epoch |
| 4 | Low | [Block Rewards](#affected-specifications) | skim: two examples ([Chores](#chores)) |

# Discussion

## What 100 hours hold

The epoch has three phases: the snapshot of the stake, a buffer, and the wait for the epoch nonce and the inferred total stake `D` to become final. Today they last 54, 54 and 72 hours. With phases of `3K`, `3K` and `4K` they last 30, 30 and 40 hours.

A phase keeps its value **final in time** when [Commit](../cryptarchia-v1-protocol.md#commit) makes the value final before its first use, except with chance `1e-9`. This depends on the share of `D` that builds blocks and on the delay of each block. The figures below take every block `T_M` late, 15 s. The specification states no such standard, and this RFC does not add one.

| Phase | Today | 100 hours |
| --- | --- | --- |
| Snapshot of the stake: final in time while this share of `D` builds | 13.8 % | 26.1 % |
| Nonce and inferred stake: final in time while this share of `D` builds | 10.2 % | 19.0 % |

- The `K` row's worst state is a coalition of 30 % of the total active stake that does not build, with every honest block 15 s late. The building share is then 70 %, and a waiting phase of 13.03 hours keeps its value final in time in every state of the row. 30 and 40 hours are 2.3 and 3.1 times that.
- No phase shorter than 10.48 hours keeps its value final in time in every state of the row when every lottery win is counted. No phase shorter than 13.03 hours does when only blocks of the chain are counted.
- A phase of exactly `K` makes its value final only if two given slots hold blocks, a chance of at most `f²`, about 0.11 %. The specification's two statements that a waiting phase lasts at least `K` state a bound that is needed but not enough. The phases now imply them, so this RFC removes them ([Details](#1-the-epoch-schedule-reads-the-finality-window)).
- The buffer needs at least one slot won by honest stake. To hold in every state of the row, that needs at least 903 slots. The buffer has 108,000.
- Theorem 2 of Ouroboros Genesis, which the Bootstrap rule follows, asks for an epoch of at least `6·s_gen` = 27 hours. On one reading of its proof, that bound serves to fit two density windows, `2·s_gen` = 9 hours, between the cut-off and the next epoch. 100 and 40 hours meet both. The theorem itself does not cover delays above two slots.

The specification does not say what a node does when a value is not final at the end of its phase. This RFC does not change that.

## The stake inference

The observation window is the first `6K` slots of an epoch: 60 hours in place of 108. A shorter window counts fewer slots, so its estimate is noisier.

| | Today | 100 hours |
| --- | --- | --- |
| Noise of `D`, one standard deviation | 0.87 % | 1.16 % |
| Chance that a chain misses the floor of 689 occupied slots in `K`, one epoch after the inference settles | `1.4·10^-8` | `2.7·10^-8` |
| The floor that chance would give at `1e-9` | 680 | 678 |
| Chance per epoch that the noise alone puts the true active stake above 1.094 times `D` | `3.8·10^-29` | `5.2·10^-17` |
| Wins a coalition of 30 % gives up to deflate the inference | 3,934 | 2,186 |
| Longest time a change of the active stake leaves `D` untouched | 252 h | 140 h |

- The floor is sized while the stake that builds equals `D`. The inference settles where slots are occupied at 0.033 a slot, 1 % below `f`, so the chance of missing the floor is above `1e-9` already today. A shorter window raises it from `1.4·10^-8` to `2.7·10^-8`. Missing the floor delays finality past `K`. It does not make a block immutable early.
- At 15 s, `K` holds 30 % while the true active stake stays within 1.094 times `D`. The shorter window keeps the chance that noise alone breaks that limit at `5.2·10^-17` per epoch.
- A coalition deflates the inference by withholding every block for one observation window. The window is 60 hours, so a deflation costs it 2,186 wins in place of 3,934.

## The epoch nonce

The epoch nonce stays as it is. A coalition that can choose among nonces gains more blocks the more cut-offs there are, and a race of `K` slots that starts near the end of an epoch meets two nonces.

| | Today | 100 hours |
| --- | --- | --- |
| Cut-offs a year | 48.7 | 87.6 |
| Targets whose race of `K` slots meets two nonces | 5.6 % | 10.0 % |
| Blocks a coalition of 30 % gains by choosing among at most `2^16` nonces, at 10 s and 15 s | 0.70 %, 0.82 % | 0.94 %, 1.10 % |
| The same, in blocks a year at 10 s | 2,230 | 2,995 |

- The share of targets that meet two nonces is `K` divided by the epoch's length: 36,000 of 360,000 slots.
- The gain grows about as the square root of the number of cut-offs. It takes the number of nonces a coalition holds at a cut-off as independent of the epoch's length. The bound from which a 10-hour `K` holds its shares with today's nonce is taken as independent of the gap from the cut-off to the next epoch, as long as the cut-off is final in time. Neither is derived for epochs other than 180 hours.

## New stake and the other readers of the epoch

A note may lead once it was in the note set at the beginning of the previous epoch. New stake therefore waits one to two epochs before it can lead: 100 to 200 hours in place of 180 to 360.

Every other specification that reads the epoch keeps its rules per epoch:

- **Proof of work.** `EXPECTED_BLOCKS_PER_EPOCH` is the epoch's length times `f`, so it falls from 21,600 to 12,000. The distribution rate `ρ` falls from 1/200 to 1/360 per epoch. The reward of a claim divides the pool by `EPOCH_POW_DISTRIBUTION_RATE_DEN · TARGET_CLAIMS_PER_BLOCK · EXPECTED_BLOCKS_PER_EPOCH`, which is 43,200,000 both before and after. So the reward of a claim does not change, and at the target rate the pool pays out 21.6 % of itself a year before refills, as it does today. `difficulty_blend` may still move by a factor of 2 per epoch, now every 100 hours, and reads the transactions of 12,000 expected blocks.
- **Blend.** An epoch lasts 360,000 rounds. The core quota is derived from the rounds per epoch, so a core node gets about 5/9 of today's core quota per epoch and the same number of cover messages per hour. The nullifier cache needs about 184 MB in place of 332. A node rebuilds its connections and sends its active message once per epoch, so 1.8 times as often per hour. The activity threshold of the reward lottery reads the cover messages of an epoch. It is 0, where Blend says rewards are nearly unreachable, for every network of 524,288 core nodes or more, up to the 2^20 that a Proof of Quota tree holds. Today it is 0 from 972,000 core nodes, and at some sizes from 648,000. A core node that uses its whole quota wins the base reward of an epoch with chance 0.71 in place of 0.89 at 10,000 core nodes, and 0.0015 in place of 0.0028 at 100,000.
- **Leader rewards.** The vouchers of an epoch enter the voucher tree together in the first block of the next epoch. An epoch holds 12,000 blocks on average in place of 21,600, and that is the smallest set a voucher hides in.
- **Service declarations.** A message takes effect at the start of the second epoch after its block, so it waits one to two epochs: 100 to 200 hours in place of 180 to 360.
- **Storage markets.** The price may still change by up to 12.5 % per epoch, now every 100 hours.
- **Block rewards.** Its chosen time step is one block. Only its examples of a one-epoch time step change ([Chores](#chores)).

## Alternatives

- **Keep 180 hours.** Every margin above stays as it is, and new stake waits 180 to 360 hours.
- **Shorten only the last phase, to 13.03 hours: an epoch of 121 hours.** The window and its noise do not change. The nonce and the inferred stake are then final in time only while 70 % of `D` builds, the `K` row's worst state, so the phase has no margin. 8.3 % of targets meet two nonces.
- **Halve every phase: 27, 27 and 36 hours, an epoch of 90 hours.** The phases stay final in time down to 29.3 % and 21.3 % of `D` building, and the noise of `D` is 1.23 %. The phases would read a new unit, `⌊k/(2f)⌋`, and no longer follow `K`, so the statement that a waiting phase lasts at least `K` would have to stay.
- **A third of every phase: 18, 18 and 24 hours, an epoch of 60 hours.** The phases stay final in time down to 46.9 % and 33.5 %. The noise of `D` is 1.50 %, noise alone breaks the 1.094 limit with chance `6.3·10^-11` per epoch, 16.7 % of targets meet two nonces, and a deflation costs 30 % only 1,311 wins.
- **Every phase at the value that suffices for its rule: 13.03, 4.78 and 13.03 hours, an epoch of 30.84 hours.** No phase has a margin. The noise of `D` is 2.14 %, noise alone breaks the 1.094 limit with chance `3.0·10^-6` per epoch, 32.4 % of targets meet two nonces, and an epoch holds 3,701 blocks. The buffer of 4.78 hours rests on a survival law for branches that is not proved.
- **Keep 180 hours and take the snapshot later.** New stake would wait from about 90 to 270 hours. It changes the rule on eligible notes, and nothing else shortens.
- **Give the lottery its own cycle, apart from the epoch other protocols read.** It adds a second clock that every reader must name.
- **Keep `ρ` at 1/200 per epoch.** The reward of a claim then rises 1.8 times, and the pool pays out 35.5 % of itself a year in place of 21.6 %.
- **Rescale every per-epoch rate to keep its pace per hour.** Only `ρ` rescales to a whole number. The step of `difficulty_blend` would be `2^(5/9)`, about 1.47, and the storage price bound about 6.76 %.

## Compatibility

This is a consensus change. Nodes with a different epoch compute different epoch states, so a network runs one schedule. Every epoch boundary, the cut-off slot and `PERIOD` change, and so do the per-epoch values of proof of work and Blend. No header or wire format changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from a review, with proofs, of the epoch's length under a finality window of 10 hours: [`slot-finality/epoch`](https://github.com/logos-blockchain/research/tree/5e9f172ece0d3f64b32382643e80f268a4dd607d/tools/simulators/finality/slot-finality/epoch) of the research repository at commit `5e9f172`. `REVIEW.md` there states each result with its proof and names the script and the output lines behind it. The folder's README lists each script with its command and its stored output.

- `s03_gap_bound.py` and `s09_epoch.py`: the shares at which each phase is final in time, and the least phase in each state of the `K` row.
- `s14_bracket.py`: the phases and the buffer below which a rule fails.
- `s06_inference.py`: the noise of `D`, the floor and the 1.094 limit under that noise, and the cost of a deflation.
- `s05_targets.py` and `s11_gain.py`: the targets that meet two nonces, and the gain of choosing among nonces.
- `s07_genesis.py`: the bounds of Ouroboros Genesis.
- `s09_epoch.py`: the cost of each schedule in [Alternatives](#alternatives).

The bounds hold in the specification's own model of the floor. The mapping of each state of the `K` row to a building share and a delay is the review's. Only the alternative of 30.84 hours rests on the finality study's survival law for branches, which is not proved.

# Details

## 1. The Epoch Schedule reads the finality window

In the [Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule), the phases read `K` in place of `⌊k/f⌋`:

```diff
-| Stake Distribution Snapshot | 3⌊k/f⌋ slots | ...
-| Buffer phase | 3⌊k/f⌋ slots | ...
-| Lottery Constants Finalization | 4⌊k/f⌋ slots | On the 6⌊k/f⌋th slot into the epoch, ...
+| Stake Distribution Snapshot | 3K slots | ...
+| Buffer phase | 3K slots | ...
+| Lottery Constants Finalization | 4K slots | On the 6Kth slot into the epoch, ...
```

- The epoch length is `3K + 3K + 4K = 10K` slots. With `K = 36000`, an epoch lasts 360,000 slots.
- In [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode), the slot at which the epoch nonce is read and the end of the inference's window read `6K`, 216,000 slots into the epoch.
- In [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) of the Total Stake Inference, `PERIOD` is `6K`. The document inherits `K` in place of `k`.
- The sentence "Each phase that waits for a value to finalize must last at least the finality window `K` …" is removed from the Epoch Schedule.
- The `K` row of [Constants](../cryptarchia-v1-protocol.md#constants) says that `K` also sets the Epoch Schedule. It no longer says that `K` must not exceed a phase of the Epoch Schedule that waits for a value to finalize.

## 2. Proof of work keeps its reward per claim

In [Parameters](../proof-of-work.md#parameters):

```diff
-EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 200
+EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 360
 TARGET_CLAIMS_PER_BLOCK: uint64 = 10            # T
-EXPECTED_BLOCKS_PER_EPOCH: uint64 = 21_600      # N_b = 10 k
+EXPECTED_BLOCKS_PER_EPOCH: uint64 = 12_000      # N_b = 10 K f
```

- [Notation](../proof-of-work.md#notation) defines `K`, 36,000 slots, in place of `k`.
- The Parameters add: `ρ` is a share per epoch. A change of the epoch length changes `EXPECTED_BLOCKS_PER_EPOCH`, and `ρ` must change in proportion to it, or the reward of a claim and the share of the pool paid out per hour change.

## 3. Blend reads the epoch's length

- [Time](../blend-protocol.md#time): an epoch lasts the epoch length of the Epoch Schedule, 360,000 slots, or 12,000 blocks on average.
- [Global Parameters](../blend-protocol.md#global-parameters): `E` is 360,000 rounds, the epoch length of the Epoch Schedule.
- [Leadership Quota](../blend-protocol.md#leadership-quota): `L_Avg = E · F_D = 360000/30 = 12000`.
- [Relaying](../blend-protocol.md#relaying-2): the nullifier cache needs at least `(360000 + 30) · (1 + 130/30) · 3 · 32 = 184335360` bytes, about 184 MB.

## Chores

- [Block Rewards](../block-rewards.md): the two examples of a one-epoch time step read an epoch of 100 hours: `Δ_t = 1/87.6` and `f = 12000`.

# Implementation

- [ ] Set the epoch's phases to `3K`, `3K` and `4K` slots, the cut-off and `PERIOD` to `6K`, and the epoch to 360,000 slots
- [ ] Set `EXPECTED_BLOCKS_PER_EPOCH` to 12,000 and `EPOCH_POW_DISTRIBUTION_RATE_DEN` to 360
- [ ] Derive Blend's core quota and nullifier cache from 360,000 rounds
- [ ] Add tests: the epoch boundaries, the cut-off slot and the inference's window at `K = 36,000`, and the reward of a claim before and after the change
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.5.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.3.0 |
| [Proof of Work](../proof-of-work.md) | Modified | 1.2.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.9.0 |
| [Block Rewards](../block-rewards.md) | Modified | 1.2.1 |
