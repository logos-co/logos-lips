# [RFC] Cryptarchia: Shorten the finality window to 10 hours

**Motivation and proposal:** [PR #533](https://github.com/logos-co/logos-lips/pull/533)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |
| v2 | The `K` row states the rule that gives 10 hours. [The epoch nonce](#the-epoch-nonce) gives the share 10 hours holds with today's nonce and the wait each nonce design needs, and says what the nonce's RFC is to propose and that this RFC waits for it | 2026-11-14 |
| | Added: two density windows within `K`, honest stake offline, a split in halves, the participation the epoch's waits need, and the block-times analysis | |
| | Corrected: the cost of the restart path (1.2 hours, not 1.5), the path against the 15 s case, the edges 2.097 and 1.50 and the cases they belong to, the blocks above `B_imm`, the factor `6.9·10^6`, the delay of a shorter Blend, and 6.5 and 7.1 hours in the table | |
| v3 | [The finality floor](#the-finality-floor) is sized with all of the stake building and every block `T_M` late. It is 689 occupied slots, where v2 had 560 from 30 % withholding at 10 s. Stake that does not build can now delay finality. Every figure that reads the floor follows | 2026-11-17 |
| | The figures on the specification's Blend take a delay per block in place of a scaled block rate ([Reproducing the figures](#reproducing-the-figures)) | |
| | The `K` row names a third case, a delay of `Δ` while the inferred stake is the honest stake alone, and states that its first two cases take the inferred stake as equal to the active stake. [What the finality window holds](#what-the-finality-window-holds) gives what 10 hours holds when two of the three cases come together | |

## Reviewer Orientation

Read the PR's Motivation first. The rules that count finality in slots stay as they are. Only the finality window, the floor and the unit of the epoch change.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the window and the floor](#1-the-finality-window-is-10-hours) | the rule that gives 10 hours, what 10 hours holds against 30 %, what a third of the stake keeps, and what the window takes of the epoch nonce ([What the finality window holds](#what-the-finality-window-holds), [What a third keeps](#what-a-third-keeps), [The epoch nonce](#the-epoch-nonce)) |
| 2 | High | [Cryptarchia Protocol, Total Stake Inference](#affected-specifications): [the epoch](#2-the-epoch-keeps-its-length) | every epoch value stays as it is |

# Discussion

## What the finality window holds

`K` is 36,000 slots, 10 hours. This section gives the share of stake it holds at a chance of `1e-9` per block that a block made immutable is displaced.

The figures come from the finality study ([Reproducing the figures](#reproducing-the-figures)), under its two delay models.

- **Worst case.** An adversary delivers every honest block as late as a bound `Δ` allows, taken at `Δ = 10` s, about the 99th percentile of delivery on the specification's Blend. The bound is the chain of Gaži, Ren and Russell ("Practical Settlement Bounds for Longest-Chain Consensus", ePrint 2022/1571) for a wait on the 1 s slot lottery. `K` binds every node, so it must hold under this model.
- **Random delay.** Blocks take Blend's mixing delays, measured in a simulation of 1,000 nodes. Only the private attack is played, with honest relays.

The figures name two cases of the epoch nonce. A nonce that **cannot be ground** gives an adversary no choice among nonces. A nonce that **resists grinding** lets an attack raise its chance by a factor of at most 1.21 when it lasts across an epoch boundary and so meets two nonces. That is the bound the study derives for its candidate ([The epoch nonce](#the-epoch-nonce)).

The wait that holds that chance, in hours:

| Case | 30 % | a third |
| --- | --- | --- |
| Worst case at 10 s, a nonce that cannot be ground | 5.9 | 10.1 |
| Worst case at 10 s, a nonce that resists grinding | 6.0 | 10.2 |
| Worst case at 10 s, today's nonce, one ground nonce | 13.6–14.1 | 25.9–26.7 |
| Worst case at 10 s, today's nonce, two ground nonces | 16.1–18.7 | 38.3–42.0 |
| Worst case at 10 s, a nonce that cannot be ground, after a deflated inference | 6.4 | 12.4 |
| Worst case at 10 s, a nonce that resists grinding, after a deflated inference | 6.5 | 12.5 |
| Worst case at 10 s, a nonce that cannot be ground, 90 % of the honest stake online | 8.4 | 16.2 |
| Worst case at 10 s, a nonce that resists grinding, 90 % of the honest stake online | 8.5 | 16.4 |
| Worst case at 10 s, a nonce that cannot be ground, 90 % of the honest stake online, after a deflated inference | 9.8 | 23.5 |
| Worst case at 12 s, a nonce that cannot be ground | 7.1 | 12.4 |
| Worst case at 15 s, a nonce that cannot be ground | 9.4 | 17.4 |
| Worst case at 15 s, a nonce that resists grinding | 9.5 | 17.5 |
| Worst case at 15 s, a nonce that cannot be ground, after a deflated inference | 14.2 | 35.6 |
| Worst case at 15 s, a nonce that cannot be ground, 90 % of the honest stake online | 14.0 | 30.8 |
| Worst case at 15 s, a nonce that cannot be ground, 90 % of the honest stake online, after a deflated inference | 25.3 | 95.7 |
| Random delay, a nonce that cannot be ground | 3.1 | 5.1 |

- A deflated inference is what an adversary gets by withholding every block for one observation period, 4.5 days. The inferred stake falls by its share, and every lottery threshold rises by `1/(1 − α)` for the next epoch. With the honest stake alone filling slots at `f`, the fixed delay weighs more.
- 10 hours holds 30 % through each disturbance that 18 hours holds a third through: a deflated inference, 15 s of worst-case delay, and 90 % of the honest stake online. Without a deflation it holds up to 15 s, and not at 16 s, where the wait is 10.4 hours. After one it holds up to 12 s, where the wait is 8.6 hours, and not at 13 s, where it is 10.1.
- These three disturbances are the cases of the `K` row. 10 hours holds 30 % through each of them alone, and through one pair: a tenth of the honest stake offline after a deflated inference needs 9.8 hours at 10 s. A delay of 15 s needs 14.0 hours with a tenth of the honest stake offline, and 14.2 after a deflated inference. All three together need 25.3. After 10 hours the chance of displacement is then `3.4·10^-7`, `4.6·10^-7` and `2.8·10^-4` per block. Through any two of the three, 10 hours holds 28 % of the stake, and through all three 26 %.
- The rows on honest stake offline read the lottery once the inference has corrected to the stake that is online. At 10 s, with a nonce that resists grinding, 10 hours holds 30 % down to 87 % of the honest stake online, and not at 86 %, where the wait is 10.1 hours.
- Stake that joins faster than the inference corrects also makes blocks come faster than `f`. At 10 s, without grinding, 10 hours holds 30 % while the true active stake stays within 2.097 times the inferred, against 2.628 times at 18 hours. At 15 s the limit is 1.094, against 1.593 at 18 hours. With the active stake at most 30 % of the supply, it holds whenever the inferred active stake is at least 14.4 % of the supply. A deflation, or a coalition of 30 % entering, makes 1.43.
- After 10 hours against 30 %, with a nonce that resists grinding, the chance of displacement is `1.0·10^-15` at 10 s, `1.2·10^-14` after a deflated inference, `2.3·10^-13` at 12 s and `3.0·10^-10` at 15 s.
- The paper's attack, played against a wait on the slot lottery at waits up to 2 hours, succeeds 0.26 to 0.82 times as often as the bound allows against a third. Delivery later than `Δ` lies outside the bound.

### How 10 hours is chosen

`K` is the least whole number of hours that meets every bound and the three cases of its row. The case that binds is the delay of `T_M`, 15 s. Against 30 % its wait is 9.37 hours with the epoch nonce taken as unbiased, as the row takes it, which is a nonce that cannot be ground. It is 9.46 hours with a nonce that resists grinding. Both give 10 hours. The other cases need less: 8.4 hours with a tenth of the honest stake offline at 10 s, and 6.4 after a deflated inference at 10 s. Two density windows need 9.

The same rule gives 18 hours against a third, where the binding wait is 17.37 hours, or 17.53 with a nonce that resists grinding. So 10 hours keeps against 30 % the delay margin that 18 hours keeps against a third. The nonce's factor is taken at 10 s, where its bound is derived.

`K` no longer follows from `k` and `f`, because the bound behind the three cases is a numerical computation, not a formula. The row links here, and asks for `K` to be sized again and `φ` to be derived again when `k`, `f`, the slot length, `T_M`, the epoch nonce or one of its targets changes. `α_max` is one of those targets.

The floor is sized at `T_M` too ([The finality floor](#the-finality-floor)).

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

At 15 s of delay, the case that sizes `K`, 10 hours holds 30 % only with a nonce that resists grinding. The `K` row takes the epoch nonce as unbiased, and says that a nonce an adversary can bias lowers the share `K` holds. Today's nonce is a hash chain that a coalition grinds near the cut-off, the slot at which the next epoch's nonce is read. With it, 30 % needs 13.6 to 18.7 hours at 10 s, and 10 hours holds a share of 0.272 at 10 s and 0.247 at 15 s, with two ground nonces at the upper end of the factor.

The least wait that holds 30 % at `1e-9` under the worst case at 15 s, for an attack that meets two nonces:

| Epoch nonce | Wait (hours) | In whole hours |
| --- | --- | --- |
| The study's candidate: the smallest contributions of 25 sub-windows, each bound to its parent's, under a sequential delay | 9.5 | 10 |
| The same contributions without the delay | 11.1–11.4 | 12 |
| Today's hash chain, with at most `2^8` candidates evaluated in an epoch | 12.2–13.4 | 14 |
| Today's hash chain, with at most `2^16` | 15.6–16.7 | 17 |
| Today's hash chain, with at most `2^24` | 19.0–20.1 | 21 |
| Today's hash chain | 29.4–34.4 | 35 |

- A sequential delay is a function whose steps cannot be run in parallel. A cap on candidates is what a delay function gives when a coalition can run it in parallel.
- The candidate's factor, 1.21, and the factor without the delay are derived at 10 s. The other rows take the factor at 15 s.
- So at 15 s, 10 hours takes a nonce with a sequential delay.

**What the nonce's RFC is to propose.** The study's candidate binds each block's contribution to its parent's, takes the smallest contribution of each of 25 sub-windows before the cut-off, and passes a hash of them through a sequential delay of 4.49 hours on the fastest hardware. An honest node then computes for 13.5 to 22.4 hours once an epoch, at the speed ratios of 3 to 5 that published chips and designs give. The design is not settled. Its delay function has no measured prototype, and it has not been compared with a single delay on today's cut-off value.

**When it should be adopted.** Before this RFC, which waits for it. 36,000 slots is what the rule gives for a nonce that is unbiased or resists grinding. If the nonce's RFC adopts a design of a lower row, the cases of the `K` row take that nonce's bias, the rule gives that row's `K`, and this RFC changes with it. Merged first, the specification would state a window that holds 0.247 to 0.272 of the stake where it names 30 %.

Two ground nonces reach only targets past the cut-off and within `K` slots of the epoch's end: 5.6 % of targets at 10 hours, against 10 % at 18.

### Alternatives

- **18 hours against a third.** With a nonce that resists grinding it holds a third at 10 s with a factor of `6.9·10^6` to spare in the chance, and every block waits 8 hours longer.
- **15 hours against 30 %.** It holds 30 % through any two of the `K` row's three cases together: a delay of 15 s after a deflated inference needs 14.2 hours. Every block then waits 5 hours longer, and the floor is 1,064 occupied slots.
- **12.5 hours, the least `K` that holds a third.** With a nonce that resists grinding it holds a third at 10 s after a deflated inference, where the wait is 12.48 hours, and no other disturbance. It misses 95 % of the honest stake online, which needs 12.67 hours, and a rise of the true active stake above 1.50 times the inferred.
- **A settled level beside `B_imm`.** A client rule that reads its own chain gives 10.2 hours against a third at 10 s with a nonce that resists grinding, and waits longer when it sees a deflation. It changes nothing in consensus. But only a client that runs it gains, and `B_imm` and every rule that waits for it keep 18 hours.
- **A block every 40 seconds.** With `f = 1/40` the wait against a third moves little when blocks speed up: 10.3 hours after a deflation, 11.9 at 12 s and 12.3 at twice the inferred stake, where a block every 30 s needs 12.4, 12.4 and 19.6. About 12.5 hours would hold a third through these. Offline stake gains nothing: 12.7 hours at 95 % online. It costs a quarter of the blocks an hour, and everything sized in blocks must be derived again.
- **A shorter delay.** Blend at 3 hops of 2 rounds has a 99th percentile of delivery of 7.3 s. Rounded up to 8 s, a third needs 8.4 hours without grinding. Rounded up the same way, the 10.2 s of the specification's Blend is 11 s, where a third needs 11.2 hours. So like for like the gain is from 11.2 to 8.4 hours. It costs Blend's anonymity and needs its own RFC. The deflated wait at 8 s is not computed.

## The finality floor

`φ` is the lower tail of the blocks the chain makes in `K` slots while all of the stake builds, with every block delivered `T_M` late, 15 s. The tail's chance is `1e-9`. The floor reads `K` and not `α_max`.

| Stake that does not build | Delay | Mean blocks in `K` | Floor | `P(N < floor)` |
| --- | --- | --- | --- | --- |
| none | 15 s | 800.0 | **689** | 9.8e-10 |
| none | 10 s | 900.0 | 768 | 8.3e-10 |
| 30 % | 10 s | 683.9 | 560 | 8.0e-10 |

The first row is the specification's. The second shows that its floor holds at 10 s too. The third is the floor of v2.

Missing the floor costs time, not safety, because finality waits for the next blocks. The floor is what the whole stake makes, so stake that does not build makes a chain miss it, whether that stake withholds or is offline. The chance that a chain misses the floor at `K`, and the median time to finality, counting only blocks of the chain:

| Stake that does not build | 10 s | 15 s | 20 s |
| --- | --- | --- | --- |
| none | 1.7e-22, 10.0 h | 9.8e-10, 10.0 h | 0.025, 10.0 h |
| a tenth | 1.7e-11, 10.0 h | 1.1e-3, 10.0 h | 0.79, 10.2 h |
| a fifth | 4.2e-4, 10.0 h | 0.53, 10.0 h | 1, 11.0 h |
| 30 % | 0.59, 10.1 h | 1, 11.0 h | 1, 12.0 h |

- The floor counts occupied slots, and a block lost to delay can return as an uncle, so these rows are the worst case. With every lottery win counted, finality is late with chance `1e-9` only when more than 29.0 % of the stake does not build, and the withholding of 30 % gives a median of 10.0 hours and 10.1 at the latest.
- A coalition can therefore delay finality by withholding. While 30 % withholds, the latest finality is 12.1 hours at 10 s and 13.0 at 15 s, where 2,160 blocks take 31.6 and 34.6 hours at the median. On the specification's Blend it is 10.0 hours at the median and 11.2 at the latest. The delay costs the coalition its rewards.
- The delay lasts until the inference corrects to the stake that builds. A coalition that starts to withhold at the end of an observation period keeps finality late for 10.5 days.
- At 15 s there is no margin. With 9.9 % of the stake absent, finality is late with chance `1e-3`, and with 19.8 % half of the time. At 10 s the margin is 12.0 % of the stake at `1e-9`. A delay above `T_M` raises the chance quickly: with all of the stake building, the floor is missed with chance `8.7e-8` at 16 s and `4.6e-6` at 17 s.
- The derivation takes slots as occupied at `f` while all of the stake builds. The stake inference stores `f` at three decimals, so it settles where slots are occupied at 0.033 a slot, 1 % below `f`. At that rate the whole stake misses the floor at 15 s with chance `5.6e-9`, and the same derivation gives 683. An estimate that is 2 % high for an epoch gives `2.6e-8`. At 10 s the chance stays below `1e-18` in each of these cases. An inference that computes with `f` exactly removes the first effect, and not the noise of its estimate, about 0.9 % an epoch.

The floor holds back a side cut off from the rest until it has made `φ + 1` blocks, or `φ` when its blocks reference the first honest block after the divergence block as an uncle. The table takes `φ + 1`. With `φ`, each figure is lower by 0.1 %:

| The side's share of the stake | Days to fix its fork, mean | Earliest at `1e-9` |
| --- | --- | --- |
| 0.1 | 2.36 | 1.86 |
| 0.2 | 1.18 | 0.93 |
| 0.25 | 0.95 | 0.75 |
| 0.3 | 0.79 | 0.62 |
| a third | 0.71 | 0.56 |

- This is 53 % of what the floor gives at 18 hours: 4.42 days for a tenth and 1.33 for a third.
- The floor holds back past `K`, with chance `1 − 1e-9`, a side of at most 0.449 of the stake. With 30 % of the stake signing on both sides of a partition, that side's honest part is at most 0.149.
- **A split in halves.** Each half fixes its own chain once `φ + 1` of its own blocks follow the split, on average after 11.4 hours with no delay and 12.5 on the specification's Blend, against 21.4 and 23.3 hours at 64,800 slots and 35.7 hours with 2,160 blocks. After that the split does not heal by itself.
- **An eclipse.** At mean rates, against a node that received the honest chain until the eclipse began, a fork of 30 % prepared in advance needs an eclipse of about 10.8 hours with no delivery delay, and 9.7 with the delay of the specification's Blend. A third's fork needs 8.5 and 7.4 hours, against 15.9 and 13.9 at 18 hours. These are means for one attempt. A coalition can prepare many forks and start with a lucky one: in one attempt of 1,000 the eclipse is about 2 hours shorter.

### Alternatives

- **A floor that 30 % cannot miss on purpose.** v2 sized the floor while 30 % withholds at 10 s, which gives 560. A coalition of 30 % then cannot delay finality by withholding at 10 s. That floor holds back a side of at most 0.355, a split in halves fixes each half after 10 hours, and a prepared fork of 30 % needs an eclipse of about 8.8 hours. The floor used here gives up that timeliness for the larger side, the longer split and the longer eclipse.
- **A floor sized at 10 s only.** With all of the stake building and every block 10 s late, the floor is 768. At 15 s, the delay that sizes `K`, the whole stake then misses it with chance 0.041.

## The restart path

`T_offline` stays at 20 minutes, so `K/T_offline` falls from 54 to 30. In a private race at 10 s the head start costs about 1.2 hours against 30 %, so 10 hours behaves like about 8.8. This is an estimate from a private race, not the study's bound.

- With a nonce that resists grinding, this path covers 30 % at 10 s, where the wait is 6.0 hours, and after a deflated inference, where it is 6.5.
- It does not cover 15 s of delay, where the wait is 9.5 hours, above 8.8. So on this path 10 hours keeps the deflated case and not the case that sizes `K`.

## Comparing forks and the switch

- `s_gen` stays at 16,200 slots. `2·s_gen` is 32,400 slots, 9 hours, within `K`. The proof behind `s_gen` reads two windows after the divergence block, and 10 hours holds 2.2 of them, where 18 hours holds four.
- The density test now decides forks from 10 to 18 hours old, which the length test decided before. Over one window of `s_gen` at 10 s, a fork of 30 % is at least as dense as the honest chain with chance `6.0·10^-14`. Against a third the same estimate is `3.9·10^-9`, the shortfall of a 4.5-hour window that counting in slots already accepts. These are single-window estimates, not the study's bound. A fork that wins the window is fixed at the switch after 690 blocks, against 1,292 at 18 hours.
- A fork the Bootstrap rule rejected by density needs a lag to survive the switch. Against 30 % at mean rates the lag is about 10.8 hours with no delivery delay, and 8.9 at 10 s. The last round before the switch closes this when an IBD peer returns the honest tip and serves its blocks, or a peer that is not an IBD peer does so within `T_offline`.
- The reference code of the rules passes its 49 tests at `K = 36,000` and `φ = 689`, and each of 33 deliberately broken versions fails at least one of them.

## What else reads `K`

- **The epoch.** Every epoch value stays as it is: phases of 194,400, 194,400 and 259,200 slots, an epoch of 648,000 and a `PERIOD` of 388,800. Each phase that waits for a value to finalize lasts at least 5.4 times `K`.
- **The epoch's waits.** A value is final when its phase ends only if `φ` occupied slots follow it by then. At mean rates the 54-hour phase that waits for the stake snapshot needs 10.5 % of the inferred stake to produce blocks, and the 72-hour phase that waits for the nonce and the inferred stake needs 7.9 %, against 19.7 % and 14.7 % at 18 hours.
- **The uncle window.** It is 360 slots against 36,000.
- **Blocks above `B_imm`.** About 1,014 on the specification's Blend, against about 1,825 at 18 hours. A node keeps the ledger states of these blocks.
- **Who waits for `B_imm`.** A Zone that credits a deposit only once the deposit is final ([CHANNEL_DEPOSIT](../bedrock-v1.1-mantle-specification.md#channel_deposit)), and a client that waits for a Zone's inscription to be final ([Sovereign Zones](../bedrock-architecture-overview.md#sovereign-zones)). On a chain that meets the floor each waits `K`, 10 hours in place of 18.
- **The last round.** Its requests name the block that lies `K` behind the local tip, and the block that lay `K` behind it when the Prolonged Bootstrap Period started. Each lies 10 hours behind in place of 18, so a stream starts at most 34 hours of blocks back when the round starts, against 42.
- **The block time.** [\[Analysis\] Block Times & Blend Network](../analysis-block-times-blend-network.md) says that Cryptarchia wants shorter block times for faster finality. With `K` sized by the rule above, a shorter block time does not shorten the wait. Against 30 % at 10 s it is 5.9 hours with a block every 30 s, 6.6 with a block every 20 s and 9.5 with a block every 15 s. This RFC does not change that document.

## Compatibility

This is a consensus change. Nodes with a different `K` or `φ` can fix different blocks, so a network runs one value of each. No header, wire format or epoch value changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from the finality study's bound, run at 10 hours: `tools/simulators/finality` of the research repository. Its notes carry each result with its check: `SLOTS.md` phase K, `SETTLEMENT.md` B6 and B7, `DESIGNS.md` H.2, `SIGNERS.md` M.7 and `UNITS.md` N.2.

Beyond the study's notes, the figures come from four sources:

- The study's bound, run for this RFC: every wait and chance at 10 hours, the waits at 12, 13, 15 and 16 s, the waits with honest stake offline, the waits, chances and shares with two or three of the `K` row's cases together, the limit on joining stake at 15 s, the waits and shares of [The epoch nonce](#the-epoch-nonce), and the waits with a block every 40, 20 and 15 s.
- The specifications as printed: the `φ` code and both fork choice rules were run as written, against the reference code's tests.
- Small models at mean rates: the eclipse, the restart race, the switch lag, the single-window estimates, the days a side needs, the split in halves, the participation the epoch's waits need, and the blocks above `B_imm`.
- The formula of Finality Floor, a delay per block and a geometric wait: the two tables of [The finality floor](#the-finality-floor) and the times to finality while stake does not build. For the specification's Blend, this formula and the small models take a delay of 5.5 slots per block, fitted so that 64,800 slots hold 1,825 blocks with all of the stake building. v2 scaled the block rate by 0.845 instead.

> **TODO (author):** the study is not on GitHub yet, so none of this can be reproduced by a reviewer. Publish its branch with the models, the reference code and the runs listed here, link that commit in the first sentence, and remove this note.

# Details

## 1. The finality window is 10 hours

In [Constants](../cryptarchia-v1-protocol.md#constants):

- `K` is 36,000 slots, 10 hours, in place of `⌊k/f⌋` = 64,800 slots. Its row no longer sets the Epoch Schedule.
- The row states the rule that gives `K`: the least whole number of hours that meets its bounds and its three cases. At 64,800 slots the row required `K` to meet them.
- The row adds that `K` must not exceed a phase of the Epoch Schedule that waits for a value to finalize. A change that required its cases to be checked again now requires `K` to be sized again.
- The row's target `α_max` is 3/10, in place of 1/3.
- `φ` is 689 occupied slots, in place of 1,291.

[Finality Floor](../cryptarchia-v1-protocol.md#finality-floor) reads `K` and not `α_max`, so its code does not change. With `K = 36000`, `f = 1/30` and `T_M = 15`, `finality_floor()` returns 689.

## 2. The epoch keeps its length

The phases of the [Epoch Schedule](../cryptarchia-v1-protocol.md#epoch-schedule) read `⌊k/f⌋` in place of `K`: `3⌊k/f⌋`, `3⌊k/f⌋` and `4⌊k/f⌋` slots, and an epoch of `10⌊k/f⌋`. The epoch nonce's slot and the inference's window in [Epoch State Pseudocode](../cryptarchia-v1-protocol.md#epoch-state-pseudocode) read `6⌊k/f⌋`, and so does `PERIOD` in [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) of the Total Stake Inference, which inherits `k` in place of `K`.

Each phase that waits for a value to finalize must still last at least `K` slots. With `K` apart from the epoch's unit, this is now a bound: `3⌊k/f⌋` is 194,400 slots against 36,000.

# Implementation

- [ ] Set the finality window to 36,000 slots, apart from the epoch's unit `⌊k/f⌋`, so that the epoch stays at 648,000 slots and `PERIOD` at 388,800
- [ ] Set the floor to 689 occupied slots
- [ ] Add tests: the floor's first and last slot at `K = 36,000` and `φ = 689`, and the epoch's phases at their lengths with `K = 36,000`
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.4.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.2.1 |
