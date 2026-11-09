# [RFC] Cryptarchia: Shorten the finality window to 10 hours

**Motivation and proposal:** [PR #TBD](https://github.com/logos-co/logos-lips/pull/TBD)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-09 |

## Reviewer Orientation

Read the PR's Motivation first. The rules that count finality in slots stay as they are. Only the finality window, the floor and the unit of the epoch change.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the window and the floor](#1-the-finality-window-is-10-hours) | what 10 hours holds against 30 %, and what a third of the stake keeps ([What the finality window holds](#what-the-finality-window-holds), [What a third keeps](#what-a-third-keeps)) |
| 2 | High | [Cryptarchia Protocol, Total Stake Inference](#affected-specifications): [the epoch](#2-the-epoch-keeps-its-length) | every epoch value stays as it is |

# Discussion

## What the finality window holds

`K` is 36,000 slots, 10 hours. This section gives the share of stake it holds at a chance of `1e-9` per block that a block made immutable is displaced.

The figures come from the two delay models of the finality study.

- **Worst case.** An adversary delivers every honest block as late as a bound `Δ` allows, taken at `Δ = 10` s, about the 99th percentile of delivery on the specification's Blend. The bound is the chain of Gaži, Ren and Russell ("Practical Settlement Bounds for Longest-Chain Consensus", ePrint 2022/1571) for a wait on the 1 s slot lottery. `K` binds every node, so it must hold under this model.
- **Random delay.** Blocks take Blend's mixing delays, measured in a simulation of 1,000 nodes. Only the private attack is played, with honest relays.

The wait that holds that chance, in hours:

| Case | 30 % | a third |
| --- | --- | --- |
| Worst case at 10 s, a nonce that cannot be ground | 5.9 | 10.1 |
| Worst case at 10 s, a nonce that resists grinding | 6.0 | 10.2 |
| Worst case at 10 s, a nonce that resists grinding, after a deflated inference | 6.4 | 12.5 |
| Worst case at 12 s, a nonce that cannot be ground | 7.05 | 12.4 |
| Worst case at 15 s, a nonce that cannot be ground | 9.4 | 17.4 |
| Worst case at 15 s, a nonce that cannot be ground, after a deflated inference | 14.2 | 35.6 |
| Worst case at 10 s, a nonce that cannot be ground, 90 % of the honest stake online | 8.4 | 16.2 |
| Worst case at 10 s, today's nonce, one ground nonce | 13.6–14.1 | 25.9–26.7 |
| Worst case at 10 s, today's nonce, two ground nonces | 16.1–18.7 | 38.3–42.0 |
| Random delay, a nonce that cannot be ground | 3.1 | 5.1 |

- A deflated inference is what an adversary gets by withholding every block for one observation period, 4.5 days. The inferred stake falls by its share, and every lottery threshold rises by `1/(1 − α)` for the next epoch. With the honest stake alone filling slots at `f`, the fixed delay weighs more.
- 10 hours holds 30 % through each disturbance that 18 hours holds a third through: a deflated inference, 15 s of worst-case delay, and 90 % of the honest stake online. Without a deflation it holds up to 15 s, and not at 16 s, where the wait is 10.4 hours. After one it holds up to 12 s, where the wait is 8.6 hours, and not at 13 s, where it is 10.1.
- Stake that joins faster than the inference corrects also makes blocks come faster than `f`. 10 hours holds 30 % while the true active stake stays within 2.098 times the inferred, against 2.627 times at 18 hours. With the active stake at most 30 % of the supply, it holds whenever the inferred active stake is at least 14.3 % of the supply. A deflation, or a coalition of 30 % entering, makes 1.43.
- After 10 hours against 30 %, with a nonce that resists grinding, the chance of displacement is `1.0·10^-15` at 10 s, `1.2·10^-14` after a deflated inference, `2.3·10^-13` at 12 s and `3.0·10^-10` at 15 s.
- The uptime row reads the lottery once the inference has corrected to the online stake.
- The paper's attack, played against a wait on the slot lottery at waits up to 2 hours, succeeds 0.26 to 0.82 times as often as the bound allows against a third. Delivery later than `Δ` lies outside the bound.

### How 10 hours is chosen

`K` is the least whole number of hours that holds `α_max` at `1e-9` under the worst case at 15 s, with a nonce that resists grinding. Against 30 % that wait is 9.46 hours, so `K` is 10 hours. The same rule gives 18 hours against a third, where the wait is 17.53 hours. So 10 hours keeps against 30 % the delay margin that 18 hours keeps against a third. The nonce's factor is taken at 10 s, where its bound is derived.

`K` is now a constant of the specification. It no longer follows from `k` and `f`, because the bound behind it is a numerical computation, not a formula. Its row links here, and asks for `K` and `φ` to be checked again when `k`, `f`, `α_max`, the slot length or `T_M` changes.

### What a third keeps

At 10 hours a third of the stake is outside the `1e-9` guarantee. The chance that it displaces a block made immutable, with a nonce that resists grinding:

| Case | 10 hours | 18 hours |
| --- | --- | --- |
| Worst case at 10 s | 1.5e-9 | 1.4e-16 |
| Worst case at 10 s, after a deflated inference | 6.2e-8 | 1.0e-13 |
| Worst case at 12 s | 6.3e-8 | 1.2e-13 |
| Worst case at 15 s | 7.4e-6 | 5.7e-10 |

- With the active stake at 30 % of the supply, a coalition between 30 % and a third of it holds 9.0 to 10.0 % of the supply.
- A tighter proof would not restore a third. If the attack's ratio to the bound held at 10 hours, a proof that matched the attack would lower a third's wait at 10 s from 10.1 hours to between 9.4 and 10.0, and its wait after a deflation from 12.4 to between 11.6 and 12.2.

### The epoch nonce

Every figure in this RFC below 13.6 hours rests on a nonce that resists grinding. With today's nonce, 30 % needs 13.6 to 18.7 hours, so 10 hours holds 30 % only once that nonce lands. The nonce is required before genesis, in its own RFC, as it is for 18 hours against a third.

Two ground nonces reach only targets past the cut-off and within `K` slots of the epoch's end: 5.6 % of targets at 10 hours, against 10 % at 18.

### Alternatives

- **18 hours against a third.** It holds a third at 10 s with a factor of `8.4·10^6` to spare, and every block waits 8 hours longer.
- **12.5 hours, the least `K` that holds a third.** It holds a third at 10 s after a deflated inference, at the edge, and nothing beyond. It misses 95 % of the honest stake online, which needs 12.55 hours, and a rise of the true active stake above 1.52 times the inferred.
- **A settled level beside `B_imm`.** A client rule that reads its own chain gives 10.2 hours against a third at 10 s with a nonce that resists grinding, and waits longer when it sees a deflation. It changes nothing in consensus. But only a client that runs it gains, and `B_imm` and every rule that waits for it keep 18 hours.
- **A block every 40 seconds.** With `f = 1/40` the wait against a third moves little when blocks speed up: 10.3 hours after a deflation, 11.9 at 12 s and 12.3 at twice the inferred stake, where a block every 30 s needs 12.4, 12.4 and 19.6. About 12.5 hours would hold a third through these. Offline stake gains nothing: 12.7 hours at 95 % online. It costs a quarter of the blocks an hour, and everything sized in blocks must be derived again.
- **A shorter delay.** Blend at 3 hops of 2 rounds bounds the delay at 8 s, where a third needs 8.4 hours without grinding. It costs Blend's anonymity and needs its own RFC. The deflated wait at 8 s is not computed.

## The finality floor

`φ` is sized against the same share as `K`: `α_max = 3/10`. It is the lower tail of the blocks the honest chain makes in `K` slots while 30 % withholds, with every honest block delivered `Δ = 10` slots late. The tail's chance is `1e-9`.

| `α_max` | Mean blocks in `K` | `φ` | `P(N < φ)` while 30 % withholds | `P(N < φ)` while a third withholds |
| --- | --- | --- | --- | --- |
| 3/10 | 683.9 | **560** | 8.0e-10 | 8.4e-7 |
| 1/3 | 657.6 | 535 | 1.7e-13 | 7.8e-10 |

Missing the floor costs time, not safety, because finality waits for the next block that reaches it. While 30 % withholds, the chance is 1.8e-4 at 15 s of delay and 0.18 at 20 s.

The floor holds back a side cut off from the rest until it has made `φ + 1` blocks:

| The side's share of the stake | Days to fix its fork, mean | Earliest at `1e-9` |
| --- | --- | --- |
| 0.1 | 1.92 | 1.47 |
| 0.2 | 0.96 | 0.74 |
| 0.25 | 0.77 | 0.59 |
| 0.3 | 0.64 | 0.49 |
| a third | 0.58 | 0.44 |

- This is 55 % of what the floor gives at 18 hours: 3.49 days for a tenth and 1.05 for a third.
- The floor holds back past `K`, with chance `1 − 1e-9`, a side of at most 0.355 of the stake. With 30 % of the stake signing on both sides of a partition, that side's honest part is at most 0.055.
- **An eclipse.** At mean rates, against a node that received the honest chain until the eclipse began, a third's fork prepared in advance needs an eclipse of about 6.9 hours with no delivery delay, and 5.6 with the delay of the specification's Blend. 18 hours needs 12.5 and 10. A fork of 30 % needs 8.8 and 7.5 hours.

## The restart path

`T_offline` stays at 20 minutes, so `K/T_offline` falls from 54 to 30. In a private race at 10 s the head start costs about 1.5 hours, so 10 hours behaves like about 8.8 against 30 %. 30 % needs 6.4 hours after a deflated inference, so it still holds on this path. This is an estimate from a private race, not the study's bound.

## Comparing forks and the switch

- `s_gen` stays at 16,200 slots, below `K`. A fork decided by density diverged at least `K` slots before the later tip, so the chain with the later tip still holds the whole window.
- The density test now decides forks from 10 to 18 hours old, which the length test decided before. Over one window of `s_gen` at 10 s, a fork of 30 % is at least as dense as the honest chain with chance `6.0·10^-14`. Against a third the same estimate is `3.9·10^-9`, the shortfall of a 4.5-hour window that counting in slots already accepts. These are single-window estimates, not the study's bound.
- A fork the Bootstrap rule rejected by density needs a lag to survive the switch. Against 30 % at mean rates the lag is about 8.8 hours with no delivery delay, and 7.2 at 10 s. The last round of Initial Block Download before the switch closes this whenever one peer returns the honest tip.
- The reference code of the rules passes its 32 tests at `K = 36,000` and `φ = 560`, and each of 17 deliberately broken versions fails at least one of them.

## What else reads `K`

- **The epoch.** Every epoch value stays as it is: phases of 194,400, 194,400 and 259,200 slots, an epoch of 648,000 and a `PERIOD` of 388,800. Each phase that waits for a value to finalize lasts at least 5.4 times `K`.
- **The uncle window.** It is 360 slots against 36,000.
- **Blocks above `B_imm`.** About 1,030 at Blend's block rate, against about 1,850 at 18 hours.

## Compatibility

This is a consensus change. Nodes with a different `K` or `φ` can fix different blocks, so a network runs one value of each. No header, wire format or epoch value changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from the finality study's bound, run at 10 hours: [`tools/simulators/finality`](https://github.com/logos-blockchain/research/tree/b2ff0767d350cf92346bf996bc1c1b88d2b1065a/tools/simulators/finality). Its notes carry each result with its check: `SLOTS.md` phase K, `SIGNERS.md` M.7 and `UNITS.md` N.2.

Beyond the study's notes, the figures come from three sources:

- The study's bound, run for this RFC: every wait and chance at 10 hours, the waits at 12, 13, 15 and 16 s, and the waits with a block every 40 s.
- The specifications as printed: the `φ` code and both fork choice rules were run as written.
- Small models of the rules: the eclipse, the restart race, the switch lag, the single-window estimates and the reference code's tests.

> **TODO (author):** publish the finality study's branch with these runs and models, and pin that commit in the link above. The pinned commit must contain `SIGNERS.md` M.7 and `UNITS.md` N.2, which the commit linked now does not.

# Details

## 1. The finality window is 10 hours

In [Constants](../cryptarchia-v1-protocol.md#constants):

- `K` is 36,000 slots, 10 hours, in place of `⌊k/f⌋` = 64,800 slots. Its row no longer sets the Epoch Schedule. It adds that `K` must not exceed a phase of the Epoch Schedule that waits for a value to finalize, and names `α_max` among the parameters whose change requires `K` and `φ` to be checked again.
- `k` is the parameter from which `s_gen` and the Epoch Schedule are derived.
- `φ` is 560 occupied slots, in place of 1,019.

In [Finality Floor](../cryptarchia-v1-protocol.md#finality-floor) the floor is sized against the share `K` is sized against:

```diff
-ALPHA_MAX = 1 / 3   # α_max, the share of the stake the floor is sized against
+ALPHA_MAX = 3 / 10  # α_max, the share of the stake K and the floor are sized against
```

With `K = 36000` and `f = 1/30`, `finality_floor()` returns 560.

## 2. The epoch keeps its length

The phases of the [Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule) read `⌊k/f⌋` in place of `K`: `3⌊k/f⌋`, `3⌊k/f⌋` and `4⌊k/f⌋` slots, and an epoch of `10⌊k/f⌋`. The epoch nonce's slot and the inference's window in [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode) read `6⌊k/f⌋`, and so does `PERIOD` in [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) of the Total Stake Inference, which inherits `k` in place of `K`.

Each phase that waits for a value to finalize must still last at least `K` slots. With `K` apart from the epoch's unit, this is now a bound: `3⌊k/f⌋` is 194,400 slots against 36,000.

# Implementation

- [ ] Set the finality window to 36,000 slots, apart from the epoch's unit `⌊k/f⌋`, so that the epoch stays at 648,000 slots and `PERIOD` at 388,800
- [ ] Set the floor to 560 occupied slots, with `α_max` at 3/10
- [ ] Add tests: the floor's first and last slot at `K = 36,000` and `φ = 560`, and the epoch's phases at their lengths with `K = 36,000`
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.4.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.2.1 |
