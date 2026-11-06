# [RFC] Proof of Work: Pay a fixed reward during a bootstrapping period

**Motivation and proposal:** PR not opened yet.

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the fixed reward](#1-a-fixed-reward-during-the-bootstrapping-period) | every node switches the reward at the same epoch; the pool check still applies to a fixed reward |
| 2 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the minimum work](#2-a-higher-minimum-work) | the cap the retarget applies by epoch; the genesis value of `difficulty_reward`; the values against [Ranges that work](#ranges-that-work) |
| 3 | Medium | [Genesis Block](#affected-specifications), [the pool seed](#3-the-pool-seed) | 200M LOGOS drawn from the initial distribution |

# Discussion

## What the reward and the minimum work set

A **board** is one Raspberry Pi 5 with four cores, the target machine of [Proof of Work](../proof-of-work.md). The fixed reward and the minimum work together set one number: what a board earns per month. A minimum stake `S` then takes `O = S / income` months of mining. A month here is 4 epochs, 30 days, and the bootstrapping period is 98 epochs, 24.5 months.

Each cell gives the LOGOS a board must earn per month for a stake and an onboarding time, and the days per claim that takes at 334 LOGOS per claim.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 50,000, 0.2 days | 30,000, 0.3 days | 20,000, 0.5 days | 10,000, 1 day |
| 2 | 25,000, 0.4 days | 15,000, 0.7 days | 10,000, 1 day | 5,000, 2 days |
| 3 | 16,667, 0.6 days | 10,000, 1 day | 6,667, 1.5 days | 3,333, 3 days |
| 4 | 12,500, 0.8 days | 7,500, 1.3 days | 5,000, 2 days | 2,500, 4 days |
| 5 | 10,000, 1 day | 6,000, 1.7 days | 4,000, 2.5 days | 2,000, 5 days |
| 6 | 8,333, 1.2 days | 5,000, 2 days | 3,333, 3 days | 1,667, 6 days |

`POW_BOOTSTRAP_TARGET_CAP` is the minimum work that gives one claim every 3 days, about $`2^{33.7}`$ hashes. That is the cell for a stake of 20,000 in 6 months, and for a stake of 10,000 in 3 months. Any other cell scales the work in proportion to its days per claim: a stake of 50,000 in 1 month needs about $`2^{29.8}`$ hashes per claim, and a stake of 10,000 in 6 months about $`2^{34.7}`$.

The reward sets the number of claims per stake.

| Stake | Stakes the pool can pay | Claims per stake at 334 LOGOS | Spread of onboarding time | Declaration of all its claim notes |
| --- | --- | --- | --- | --- |
| 50,000 | 4,000 | 150 | ±8.2% | 300 notes, 12.7 KB, 8.1% of `G_max`, 10.2 LOGOS |
| 30,000 | 6,667 | 90 | ±10.5% | 180 notes, 7.9 KB, 5.0% of `G_max`, 6.3 LOGOS |
| 20,000 | 10,000 | 60 | ±12.9% | 120 notes, 5.4 KB, 3.4% of `G_max`, 4.3 LOGOS |
| 10,000 | 20,000 | 30 | ±18.3% | 60 notes, 3.0 KB, 1.8% of `G_max`, 2.4 LOGOS |

The spread is the Poisson spread of a node's claim count, $`1/\sqrt{k}`$ for `k` claims. The declaration uses the last value of `G_max`, 3,173,691, and the starting storage price.

## The model

The figures below come from a simulation of the 98 epochs:

- The pool holds 200M LOGOS, and every claim pays 334 LOGOS. Only the pool's own fee share refills it, from claim fees. Fees from other traffic would add to it.
- Each newcomer runs one board. Newcomers arrive at a steady rate for the whole period, `a` per month. Hash rates are equal unless a section says otherwise, and no one else mines.
- A board's claims per epoch follow a Poisson distribution, and every claim pays a fee for its 365-byte transaction.
- The storage price follows [Storage Markets](../storage-markets.md), with claims as the only storage use.
- A newcomer is **onboarded** when its rewards, minus the fees of its claims and of its declaration, reach the stake.
- In the **stop** case a node stops mining at the claim that completes its stake. In the **keep mining** case it mines until the pool runs out or the period ends.
- Only proof of work rewards count. Leadership rewards on vested notes would shorten onboarding.
- A count covers the 98 epochs. A node still short of the stake at epoch 98 is not counted.

Each figure is the mean of five runs, rounded to 10, except the sweep for the best rate, which uses one run per rate. Run on the inputs of an earlier analysis, the same model gives that analysis's figures to within 4%: 2,093 nodes against 2,094, and 1,374, 1,012 and 468 nodes against 1,375, 985 and 451 with outside hash rate.

The counts follow closed forms, within 2.7% of the simulation across the stakes and onboarding times below, at 100 and 500 newcomers a month:

```python
capacity = P / S    # P = 200M LOGOS. S is the stake, O the months of mining
B = 24.5            # months in the bootstrapping period; a is newcomers a month

# Miners stop. While the pool lasts, the count is the newcomers that finish by the end.
# Once it runs out, the newcomers still mining hold half a stake on average.
stop = a * (B - O) if a <= capacity / (B - O / 2) else max(0, capacity - a * O / 2)

# Miners keep mining. The pool then runs out after sqrt(2 * capacity * O / a) months.
keep = a * (B - O) if a <= 2 * capacity * O / B**2 else max(0, sqrt(2 * capacity * O * a) - a * O)
```

## How many nodes the pool onboards

Each cell gives the nodes onboarded by epoch 98, as stop / keep mining.

At 100 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 2,360 / 790 | 2,360 / 1,050 | 2,360 / 1,310 | 2,360 / 1,900 |
| 2 | 2,260 / 1,060 | 2,260 / 1,430 | 2,260 / 1,790 | 2,260 / 2,250 |
| 3 | 2,160 / 1,250 | 2,160 / 1,690 | 2,160 / 2,140 | 2,150 / 2,160 |
| 4 | 2,060 / 1,380 | 2,060 / 1,900 | 2,060 / 2,050 | 2,050 / 2,040 |
| 5 | 1,960 / 1,490 | 1,950 / 1,940 | 1,950 / 1,950 | 1,940 / 1,950 |
| 6 | 1,850 / 1,570 | 1,850 / 1,840 | 1,860 / 1,840 | 1,840 / 1,840 |

At 500 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 3,690 / 1,500 | 6,320 / 2,080 | 9,560 / 2,660 | 11,800 / 3,960 |
| 2 | 3,430 / 1,820 | 6,060 / 2,640 | 9,300 / 3,460 | 11,280 / 5,280 |
| 3 | 3,180 / 1,950 | 5,810 / 2,950 | 9,040 / 3,960 | 10,760 / 6,190 |
| 4 | 2,930 / 1,990 | 5,550 / 3,140 | 8,790 / 4,290 | 10,240 / 6,870 |
| 5 | 2,690 / 1,950 | 5,300 / 3,240 | 8,550 / 4,540 | 9,730 / 7,410 |
| 6 | 2,430 / 1,870 | 5,050 / 3,290 | 8,300 / 4,690 | 9,220 / 7,850 |

At the steady rate that gives the most nodes, swept for each cell:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 3,880 / 2,010 | 6,420 / 3,350 | 9,600 / 5,020 | 18,890 / 9,990 |
| 2 | 3,780 / 1,990 | 6,270 / 3,300 | 9,360 / 4,910 | 18,350 / 9,670 |
| 3 | 3,690 / 2,000 | 6,120 / 3,290 | 9,140 / 4,900 | 17,960 / 9,700 |
| 4 | 3,590 / 1,980 | 5,970 / 3,290 | 8,900 / 4,930 | 17,520 / 9,650 |
| 5 | 3,460 / 1,980 | 5,810 / 3,300 | 8,700 / 4,900 | 17,080 / 9,690 |
| 6 | 3,340 / 1,970 | 5,570 / 3,290 | 8,330 / 4,920 | 16,560 / 9,670 |

What these show:

- Miners that stop can onboard 83% to 97% of the stakes the pool can pay. Miners that keep mining can onboard about half, whatever the onboarding time, at `a = capacity / (2 * O)`. The pool then runs out after `2 * O` months, so that best case is not a two-year bootstrap.
- Where the pool lasts, the count is `a * (B - O)` in both cases, and it depends only on how many newcomers arrive.
- With keep mining, a longer onboarding time onboards more nodes at low arrival rates. At a stake of 50,000 and 100 newcomers a month, 6 months gives 1,570 nodes and 1 month gives 790, because nodes that finish early keep drawing on the pool.
- If all newcomers mine from launch, miners that stop reach 98% of the stakes the pool can pay. Miners that keep mining reach 84%, 80%, 78% and 73% at the four stakes, or 3,350, 5,360, 7,760 and 14,500 nodes. Above that, the pool runs out before the slower half finishes.

## Ranges that work

These checks decide whether a combination works. The limits of ±20% and 5% are choices this RFC makes.

| Check | Rule | Result at 334 LOGOS |
| --- | --- | --- |
| A stake fits one declaration | at most 3,783 notes | every cell: at most 500 notes, even from vested notes alone at a 30-70 split |
| A claim pays its fee | the liquid part exceeds the fee at the highest storage price | every split, see [The vested-liquid split](#the-vested-liquid-split) |
| Fees stay small | the fee is at most 5% of the reward | every run: the price peaks at 32 times its start, a fee of 9.4 LOGOS, 2.8% of the reward |
| Onboarding is predictable | a spread of at most ±20%, so at least 25 claims per stake | every stake: at most ±18.3% |
| The pool lasts | it lasts the 98 epochs, with nobody stopping | depends on the income per board, below |

The last check separates the cells. The pool lasts when a board's income per month is at most `2 * P / (a * B**2)`: 13,328 LOGOS at 50 newcomers a month, 6,664 at 100, 3,332 at 200 and 1,333 at 500. Each cell gives the most newcomers a month for which it holds.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 13 | 22 | 33 | 67 |
| 2 | 27 | 44 | 67 | 133 |
| 3 | 40 | 67 | 100 | 200 |
| 4 | 53 | 89 | 133 | 267 |
| 5 | 67 | 111 | 167 | 333 |
| 6 | 80 | 133 | 200 | 400 |

With 100 newcomers a month as the reference, an assumption of this RFC:

| Stake | Months of mining that work | Nodes by epoch 98 | Stakes the pool can pay |
| --- | --- | --- | --- |
| 50,000 | none up to 6; from 7.5 | at most 1,570, the pool running out | 4,000 |
| 30,000 | 5 and 6 | 1,940 and 1,840 | 6,667 |
| 20,000 | 3 to 6 | 2,140 to 1,840 | 10,000 |
| 10,000 | 2 to 6 | 2,250 to 1,840 | 20,000 |

In these cells stop and keep mining give the same count within 1%, so no rule is needed to make miners stop. A stake of 50,000 works in this sense only with at most 80 newcomers a month at 6 months.

The reward has a range of its own. The fee check needs a reward of at least 187 LOGOS at a 32-fold price, or 275 LOGOS at the 47-fold price a slower three-year arrival gives. The spread check needs at most `S / 25`: 2,000, 1,200, 800 and 400 LOGOS at the four stakes. A reward from 275 to 400 LOGOS therefore serves all four, and 334 sits inside it.

## The vested-liquid split

A node that stakes both parts of its claims needs the same claims at every split, so the counts above hold for all four. The split changes what a node can do with its liquid part, and how much of the pool can reach the market at once.

| Vested-liquid | Per claim, vested / liquid, LOGOS | Liquid part ÷ claim fee, at the start / at 32 times | Time to a stake of vested notes alone | Notes for that stake, at 50,000 / 20,000 | Liquid share of the 200M |
| --- | --- | --- | --- | --- | --- |
| 30-70 | 100.2 / 233.8 | 801 / 25 | 3.3 × `O` | 500 / 200 | 140M |
| 50-50 | 167 / 167 | 572 / 18 | 2 × `O` | 300 / 120 | 100M |
| 70-30 | 233.8 / 100.2 | 343 / 11 | 1.4 × `O` | 214 / 86 | 60M |
| 90-10 | 300.6 / 33.4 | 114 / 3.6 | 1.1 × `O` | 167 / 67 | 20M |

A node that sells its liquid part and stakes vested notes alone needs longer. For a stake of 20,000 at 6 months, as stop / keep mining:

| Vested-liquid | Time to the stake | Nodes at 100 a month | Nodes at 500 a month |
| --- | --- | --- | --- |
| 30-70 | 20 months | 440 / 440 | 0 / 0 |
| 50-50 | 12 months | 1,260 / 1,250 | 1,990 / 1,730 |
| 70-30 | 8.6 months | 1,600 / 1,600 | 4,820 / 3,450 |
| 90-10 | 6.7 months | 1,800 / 1,790 | 7,260 / 4,400 |

So 50-50, 70-30 and 90-10 work across [Ranges that work](#ranges-that-work), and a stake of vested notes alone forms within the year its first notes take to vest. 30-70 does that only up to 3 months of mining. With more, a node must stake its liquid part as well. A 90-10 split still pays a claim's fee up to 114 times the starting storage price.

`POW_VESTED_SHARE` stays at 50 on this branch. Changing it changes no rule.

## Outside hash rate

Mining pays anyone at the prices in question, not only newcomers. A board earns about 3,340 LOGOS a month at a claim every 3 days, $33 at $0.01 per LOGOS, the price the minimum stake analysis's $100M gives over the supply cap. An earlier survey found the cheapest rented hash rate at $4.08 per board per month, on a plan whose terms prohibit mining, and about $21 on the cheapest plan that allows it (October 2026 prices, with no server hash rate measured). A Raspberry Pi 5 at home costs about $2.15 a month in electricity.

Vesting holds back part of what a renter can sell at once. These are the months of mining that keep a rented board's liquid income under 90% of its rent at $4.08 and $0.01, `(1 - v) * S * p / (0.9 * c)`:

| Vested-liquid | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 30-70 | 95 | 57 | 38 | 19 |
| 50-50 | 68 | 41 | 27 | 14 |
| 70-30 | 41 | 25 | 16 | 8.2 |
| 90-10 | 14 | 8.2 | 5.4 | 2.7 |

Only two combinations fall within 1 to 6 months: 90-10 with a stake of 20,000 at 6 months, and 90-10 with a stake of 10,000 at 3 to 6 months. Each bound falls in proportion to the price, so at $0.001 all but two of them are under 6 months. This test counts liquid income only. The vested part still pays a patient renter a year later. It is also the income of a newcomer on a rented machine, who then pays rent from other funds. On a Raspberry Pi 5 at home, liquid income at 90-10 covers the electricity at a stake of 20,000 at 6 months, and at a stake of 10,000 at 3 and 4 months.

Hash rate that mines from launch takes what newcomers would earn. Nodes onboarded by epoch 98, with miners that keep mining and 100 newcomers a month:

| Stake, months of mining | No outside boards | 500 | 1,000 | 2,000 | 5,000 | 10,000 | Outside boards that alone empty the pool in the period |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 50,000, 1 | 790 | 430 | 250 | 100 | 0 | 0 | 163 |
| 50,000, 6 | 1,570 | 1,140 | 810 | 380 | 0 | 0 | 980 |
| 30,000, 6 | 1,840 | 1,770 | 1,400 | 860 | 150 | 0 | 1,633 |
| 20,000, 3 | 2,140 | 1,700 | 1,340 | 860 | 280 | 21 | 1,224 |
| 20,000, 6 | 1,840 | 1,850 | 1,850 | 1,400 | 490 | 29 | 2,449 |
| 10,000, 3 | 2,160 | 2,160 | 2,160 | 1,700 | 790 | 290 | 2,449 |
| 10,000, 6 | 1,840 | 1,840 | 1,840 | 1,840 | 1,400 | 550 | 4,898 |

A lower income per board resists this better. Outside miners that mine a stake can declare too, so stakes may still form, for whoever mines most. The node counts in this RFC hold only while few outsiders mine.

Uneven hash rates also cost nodes. With hash rates spread as a Pareto distribution of α = 1.5 and a mean of one board, a stake of 20,000 at 6 months gives 1,410 nodes at 100 newcomers a month instead of 1,840, because the slower boards do not finish by epoch 98.

## Why the target stays at 10 claims per block

No rule limits the claims of an epoch. Only the minimum work and the existing retarget act on them, and `TARGET_CLAIMS_PER_BLOCK` stays 10. At 334 LOGOS, 216,000 claims an epoch would empty the pool in under 3 epochs, so the target limits nothing that matters. Simulated block by block, claims match what miners find to within 1.1%, up to 5 claims per block.

The alternative is a target paced to spend the pool over the period, 0.283 claims per block at 334 LOGOS. It needs a fractional `TARGET_CLAIMS_PER_BLOCK`, and the retarget overshoots such a target by 23%. It also shares a fixed payout among everyone mining, so too many miners leave nobody with a full stake. This table leaves the overshoot out:

| Stake, months of mining | Newcomers a month | Target 10, stop / keep mining | Paced target, stop / keep mining |
| --- | --- | --- | --- |
| 20,000, 6 | 100 | 1,860 / 1,840 | 1,860 / 1,840 |
| 20,000, 6 | 500 | 8,300 / 4,690 | 5,950 / 3,580 |
| 20,000, 6 | 1,000 | 6,810 / 4,850 | 2,190 / 2,030 |
| 20,000, 6 | 2,000 | 3,720 / 3,280 | 27 / 28 |
| 50,000, 6 | 500 | 2,430 / 1,870 | 460 / 440 |
| 50,000, 6 | 1,000 | 890 / 900 | 0 / 0 |

With a target of 10, each board keeps its income until the pool runs out, so early arrivals finish on time and late arrivals get nothing. A paced target keeps the pool for late arrivals and slows everyone. It does better in two cases. With 1 month of mining, few arrivals and miners that keep mining, it stops early finishers from draining the pool: at a stake of 50,000 and 100 newcomers a month it onboards 1,330 nodes against 790. Against heavy outside hash rate it also holds out longer: with 5,000 outside boards, at a stake of 20,000 at 6 months and 100 newcomers a month, it onboards 840 nodes against 490. In the cells of [Ranges that work](#ranges-that-work) a target of 10 onboards at least as many.

## Stopping

No rule can make a node stop, because every claim pays a fresh key. While total stake is below 28.8% of the cap, a provider earns about 5.0M / `N` LOGOS a month in service rewards among `N` providers, 60% of the 95.13 LOGOS of a block over 87,660 blocks. That exceeds a board's 3,340 LOGOS below 1,500 providers. But Blend uses at most one of a board's four cores, so a provider can also keep mining on the others. Stop is therefore an upper bound on the count, and keep mining the expected case.

More providers are not always better. An earlier estimate puts the limit at about 8,000 providers, where service rewards still cover a $6.12 machine at $0.01 per LOGOS. At 10,000 providers, an honest provider misses the base reward in 11% of epochs on cover traffic alone. At a stake of 10,000 the pool can pay for 20,000 providers, more than either.

## The end of the period

At epoch 98 the reward falls to what [Reward Pool](../proof-of-work.md#reward-pool) computes from the pool, and the cap returns to `REWARD_TARGET_CAP`. With 100M LOGOS left the reward is 2.31 LOGOS, and with 2,450 boards sharing the target of 10 claims per block each earns about 816 LOGOS a month, against 3,340 before. A newcomer partway to its stake at epoch 98 then needs about 4 times longer for what is left. If claims were the only storage use, the storage price would stand at about 31 times its start, a fee of about 9 LOGOS, above that reward. Claims would then stop for about 15 epochs while the price falls. The cap reaches its new value within about 51 blocks.

## The values in Details

Details uses 334 LOGOS and one claim every 3 days, an income of about 3,340 LOGOS per board per month. That is the highest income among the cells that pass the rent test at a 90-10 split, and it passes the pool check up to about 200 newcomers a month. The same minimum work serves both of these cells, as stop / keep mining:

| Stake, months of mining | 100 a month | 200 a month | 500 a month | 1,000 a month |
| --- | --- | --- | --- | --- |
| 20,000, 6 | 1,860 / 1,840 | 3,710 / 3,650 | 8,300 / 4,690 | 6,810 / 4,850 |
| 10,000, 3 | 2,150 / 2,160 | 4,300 / 4,280 | 10,760 / 6,190 | 17,800 / 7,850 |

## Era parameters

The three constants added here, `POW_BOOTSTRAP_EPOCHS`, `POW_BOOTSTRAP_REWARD` and `POW_BOOTSTRAP_TARGET_CAP`, are era parameters. Eras specifies the era parameter record, and this branch does not have it, so their fields go into whichever of the two specifications lands second.

## Compatibility

The chain has not launched, so no migration is needed. Claims, their encoding and the circuits do not change.

## Open questions

- **The values.** Which cell to run is a team decision, and it needs the token price the rent test depends on.
- **The minimum stake.** No specification sets it. The analysis of the minimum stake gives 0.001% of the supply at launch, which is 100,000 LOGOS if that supply is the cap. A stake of 20,000 is 0.0002% of the cap. That analysis should change with any value chosen here, and this branch does not change it. A lower stake also lets the same pool fund more provider identities: 10,000 at 20,000 LOGOS against 4,000 at 50,000.
- **The end of the period.** Paying the fixed reward until the pool is empty would remove the fall at epoch 98, and it would let a slow start use the whole pool. It would also drop the switch this RFC adds by epoch number.
- **The pool.** 200M LOGOS is 2% of the supply cap, four times the current seed, and it comes out of the initial distribution.
- **Privacy.** With 334 LOGOS per claim a spend hides among far fewer claims. At one claim every 3 days and 100 newcomers a month, an epoch holds about 60 claims at launch and about 6,000 at the end if nobody stops. If everybody stops at a stake of 20,000, it holds about 1,500 from month 6 on.
- **Storage price.** The price model counts claims as the only storage use. Other traffic changes its path.
- **The puzzle.** The minimum work assumes the `zkhash` puzzle of this branch. A change of puzzle changes the value of `POW_BOOTSTRAP_TARGET_CAP`, and not the income of a board.

# Details

## 1. A fixed reward during the bootstrapping period

The first `POW_BOOTSTRAP_EPOCHS` epochs are the bootstrapping period. During it, `epoch_pow_reward` is `POW_BOOTSTRAP_REWARD`. A claim still needs the pool to cover it, as [CLAIM_POW_REWARD](../bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation requires.

```diff
+POW_BOOTSTRAP_EPOCHS: uint64 = 98               # the length of the bootstrapping period, in epochs
+POW_BOOTSTRAP_REWARD: TokenValue = 334 * 10**9  # the reward per claim during it, 334 LOGOS, in LEPTA

-def compute_epoch_pow_reward(pow_reward_pool: TokenValue) -> TokenValue:
+def compute_epoch_pow_reward(epoch: EpochNumber, pow_reward_pool: TokenValue) -> TokenValue:
+    if epoch < POW_BOOTSTRAP_EPOCHS:
+        return POW_BOOTSTRAP_REWARD
     denominator = (EPOCH_POW_DISTRIBUTION_RATE_DEN
     # ... unchanged
```

`POW_BOOTSTRAP_EPOCHS` is the number of epochs that first reaches two years, $`\lceil 730 / 7.5 \rceil = 98`$. The constraint that the vested notes of a minimum stake fit one declaration now reads `POW_BOOTSTRAP_REWARD`.

## 2. A higher minimum work

During the bootstrapping period `difficulty_reward` stays at or below `POW_BOOTSTRAP_TARGET_CAP`, which is also its genesis value. After the period it may rise to `REWARD_TARGET_CAP`. `TARGET_CLAIMS_PER_BLOCK` does not change.

```diff
+POW_BOOTSTRAP_TARGET_CAP: PowTarget = p // 14_300_000_000

 def compute_new_reward_difficulty(claims_in_block: uint64,
-                                  current_target: PowTarget) -> PowTarget:
+                                  current_target: PowTarget,
+                                  epoch: EpochNumber) -> PowTarget:
     # ... unchanged
-    return min(max(new_target, REWARD_TARGET_FLOOR), REWARD_TARGET_CAP)
+    cap = POW_BOOTSTRAP_TARGET_CAP if epoch < POW_BOOTSTRAP_EPOCHS else REWARD_TARGET_CAP
+    return min(max(new_target, REWARD_TARGET_FLOOR), cap)
```

`epoch` is the epoch of the processed block. `POW_BOOTSTRAP_TARGET_CAP` is calibrated against the measurement of `BLEND_DIFFICULTY_BASE`, $`2^{19}`$ hashes in about 38 seconds on one core: the four cores of the target machine find a claim about every 3 days, 2.5 claims per epoch.

## 3. The pool seed

`POW_REWARD_POOL_GENESIS` becomes two hundredths of $`S_{cap}`$, 200M LOGOS, instead of five thousandths.

## Chores

- The Overview of Proof of Work says what a claim pays during the period, and that mining stays below the target rate.
- The Notation row of the distribution rate says it applies after the period.
- Genesis says `epoch_pow_reward` is set by the computation, no longer derived from the pool.

# Implementation

- [ ] Add `POW_BOOTSTRAP_EPOCHS`, `POW_BOOTSTRAP_REWARD` and `POW_BOOTSTRAP_TARGET_CAP`, with the values chosen from [Ranges that work](#ranges-that-work).
- [ ] Set `epoch_pow_reward` by epoch at each epoch boundary and at genesis.
- [ ] Apply the cap by the epoch of the processed block, and start `difficulty_reward` at `POW_BOOTSTRAP_TARGET_CAP`.
- [ ] Seed the pow reward pool with two hundredths of the supply cap.
- [ ] Measure the claims per epoch of a Raspberry Pi 5 at the new cap.
- [ ] Add `POW_BOOTSTRAP_EPOCHS`, `POW_BOOTSTRAP_REWARD` and `POW_BOOTSTRAP_TARGET_CAP` to the era parameter record once Eras and this change are on one branch.
- [ ] Add tests: the reward at epochs 97 and 98, a claim against a pool below the fixed reward, the retarget at the cap in both periods, the genesis values.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.4.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.4.0 |
