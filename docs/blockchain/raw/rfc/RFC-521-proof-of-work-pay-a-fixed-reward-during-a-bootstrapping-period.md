# [RFC] Proof of Work: Pay a fixed reward during a bootstrapping period

**Motivation and proposal:** [PR #521](https://github.com/logos-co/logos-lips/pull/521)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-06 |
| v2 | Outside mining takes a patience of 1 as its base case, so the rent check counts a board's whole income | 2026-11-06 |
| v3 | Owned hash rate is the lower bound on the cost of a board, and the reward of 334 LOGOS depends on replacing the reward puzzle | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the rewards](#1-fixed-rewards-and-vested-shares) | every node switches the reward and the share at the same epoch; the rule that computed the reward from the pool is gone |
| 2 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the difficulty controller](#2-the-difficulty-controller) | the fractional target of the period, the caps by epoch, the new smoothing and floor, against [The difficulty controller](#the-difficulty-controller) |
| 3 | High | [Mantle](#affected-specifications), [the vested share](#3-the-vested-share-in-mantle) | a claim reads `epoch_pow_vested_share`; the positive reward check goes |
| 4 | Medium | [Genesis Block](#affected-specifications), [the pool seed](#4-the-pool-seed) | 200M LOGOS drawn from the initial distribution |

# Discussion

## The design

A **board** is one Raspberry Pi 5 with four cores, the target machine of [Proof of Work](../proof-of-work.md). All the figures below follow from these values.

|  | First 98 epochs (two years) | After epoch 98 |
| --- | --- | --- |
| Reward per claim | 334 LOGOS | 1.2 LOGOS |
| Vested-liquid split | 90-10 | 30-70 |
| A claim on a board, at the minimum work | about every 3 days | about every 2.7 hours |
| Income per board per month, at most | about 3,340 LOGOS, 334 of it liquid | about 320 LOGOS, 224 of it liquid |
| Target | 0.283 claims per block, which pays out 200M LOGOS over the period | 10 claims per block |
| Payout per month at the target | about 8.2M LOGOS | about 1.04M LOGOS |

No rule limits the claims of an epoch. Only the difficulty controls them, through the minimum work and the retarget. A month here is 4 epochs, 30 days, and the period is 24.5 months.

At this income a stake of 20,000 LOGOS takes 60 claims, 6 months of mining. A stake of 10,000 takes 30 claims, 3 months. No specification sets the minimum stake, and both stakes use the same minimum work.

These times hold while no outsiders mine. At a token price of $0.01 and a rent of $4.08 a month, outsiders bring a board's income down to 408 LOGOS a month, and the times become 49 and 24.5 months. [Outside mining](#outside-mining) gives this base case.

These values assume the reward puzzle is replaced first, as [Dependence on the puzzle](#dependence-on-the-puzzle) says.

## The model

The figures come from a simulation of the 98 epochs:

- The pool holds 200M LOGOS. Only its fee share of claim fees refills it. Fees from other traffic would add to it.
- Each newcomer runs one board, and newcomers arrive at a steady rate `a` per month for the whole period.
- A board's claims per epoch follow a Poisson distribution. Total claims per epoch are the lesser of what boards find and the target rate.
- Every claim pays a fee for its 365-byte transaction, at a storage price that follows [Storage Markets](../storage-markets.md) with claims as the only storage use.
- A newcomer is **onboarded** when its rewards, minus the fees of its claims and of its declaration, reach the stake by epoch 98.
- A node either **stops** mining at the claim that completes its stake or **keeps mining** until the end.
- Only proof of work rewards count. Leadership rewards on vested notes would shorten onboarding.
- A table without outsiders is the best case for newcomers. It holds only while a board's income times the token price stays below the cost of a board.

Each figure is the mean of three to five runs, rounded to 10. Sweeps for the best arrival rate use one run per rate. Run on the inputs of an earlier analysis, the same model gives that analysis's figures to within 4%: 2,093 nodes against 2,094, and 1,374, 1,012 and 468 nodes against 1,375, 985 and 451 with outside hash rate.

## Income per node against a VPS

A board's income per month should stay below what a VPS costs, so that mining does not pay for a machine rented only to mine. This check counts the vested part in full, since a miner need not wait a year to get its value:

- A vested note leads and can be staked like a liquid one, so it serves anyone who wants a stake as well as a liquid LOGOS does. The rewards it earns are liquid.
- A miner picks the key a claim pays, so it can mine to a buyer's key. The note then belongs to the buyer from the start.
- A seller can stake its vested notes under a buyer's keys, in one transaction with a Transfer paying the seller. Binding a stake to its miner would close this route and leave the other two.

The rented costs come from an October 2026 survey of plans. No server hash rate has been measured, and a vCPU is counted as 1.5 Raspberry Pi 5 cores. The owned machine's boards are measured and its power is assumed. A plain C Poseidon2 permutation, with the round counts of [Common Cryptographic Components](../common-cryptographic-components.md), ran 2.38M times a second on its 14 threads over 59 seconds. A board is the 165,565 a second that `BLEND_DIFFICULTY_BASE` implies at 3 permutations per ticket.

| Machine | Price per month | Boards it mines | Cost per board per month | Mining in its terms |
| --- | --- | --- | --- | --- |
| Apple M4 Pro someone already owns | about $14 of electricity, at an assumed 65 W | 14.4 | about $1 | not applicable |
| Raspberry Pi 5 at home | about $2.15 of electricity | 1 | $2.15 | not applicable |
| Contabo Cloud VPS 4, 4 shared vCPUs | $6.12 | 1.5 | $4.08 | prohibited |
| Contabo Cloud VDS S, 6 dedicated threads | $48 on a 24-month term | 2.25 | $21.30 | allowed |

A board's income depends on how many boards mine. Up to 2,449 boards each earns the income of the minimum work. Above that the target holds the payout at 8.18M LOGOS a month, and they share it.

| Boards mining | Income per board per month, LOGOS | Liquid part at 90-10 | Total at $0.01 per LOGOS | Liquid part at $0.01 |
| --- | --- | --- | --- | --- |
| up to 2,449 | 3,340 | 334 | $33.40 | $3.34 |
| 5,000 | 1,636 | 164 | $16.36 | $1.64 |
| 10,000 | 818 | 82 | $8.18 | $0.82 |
| 20,000 | 409 | 41 | $4.09 | $0.41 |
| 50,000 | 164 | 16 | $1.64 | $0.16 |

$0.01 is the price the minimum stake analysis's $100M gives over the supply cap. The token prices up to which a board's income at the minimum work stays below each cost:

| Cost per board per month | Token price, whole income | Token price, liquid part at 90-10 |
| --- | --- | --- |
| $1 | $0.0003 | $0.003 |
| $2.15 | $0.00064 | $0.0064 |
| $4.08 | $0.0012 | $0.012 |
| $6.12 | $0.0018 | $0.018 |
| $21.30 | $0.0064 | $0.064 |

So at $0.01 a board's income at the minimum work, $33.40, is 8 times the rent of $4.08. Outsiders join above $0.0012, and the target brings the income back to the rent, as [Outside mining](#outside-mining) shows. The liquid part alone, $3.34, stays below the rent, so a miner that counts only its liquid income stays out up to $0.012. Holding the whole income below the rent at $0.01 by the minimum work alone would need a claim about every 24.6 days. That puts a stake of 20,000 at 49 months, longer than the period, and a stake of 10,000 at 24.5 months, the whole period.

Average income over the period, per newcomer's board, with miners that keep mining:

| Case | Average, LOGOS per month | At epoch 98, LOGOS per month | Average at $0.01 | Liquid part of the average at $0.01 |
| --- | --- | --- | --- | --- |
| 100 newcomers a month, no outsiders | 3,340 | 3,340 | $33.40 | $3.34 |
| 200 newcomers a month, no outsiders | 2,500 | 1,670 | $25.00 | $2.50 |
| 500 newcomers a month, no outsiders | 1,200 | 670 | $12.00 | $1.20 |
| 1,000 newcomers a month, no outsiders | 630 | 330 | $6.30 | $0.63 |
| 100 newcomers a month, outsiders renting at $4.08 | 510 | 410 | $5.10 | $0.51 |

Claim fees take 0.3% to 1.8% of this. A node that has declared also earns service rewards, about 5.0M / `N` LOGOS a month among `N` providers while total stake is below 28.8% of the cap. That covers a $6.12 machine at $0.01 up to about 8,000 providers. Providing a service therefore pays for the machine. Once outsiders have joined, mining pays a board no more than its cost.

## Outside mining

Mining pays anyone, not only newcomers. An outsider adds boards while a board-month is worth more than it costs. A board-month is worth `income * p * (1 - v + v * d)`, where `p` is the token price, `v` the vested share, and `d` the miner's **patience**: what a LOGOS that vests in a year is worth to it today. With a target that holds the payout at `R = 8.18M` LOGOS a month, boards join until the value equals the cost `c`:

```python
boards = R * p * (1 - v + v * d) / c
income = c / (p * (1 - v + v * d))    # at most 3,340 LOGOS a month
```

The base case is a patience of 1, for the reasons in [Income per node against a VPS](#income-per-node-against-a-vps). It is also the upper bound, since a liquid LOGOS can do all that a vested one can. The split then drops out: `boards = R * p / c` and `income = c / p`. The base cost is the cheapest rent, $4.08. Hash rate someone already owns, at about $1 a board, is the lower bound.

The target therefore holds a board's income at the cost of the cheapest hash rate, at any token price, without knowing the price. A rise in price brings more boards and lowers the income in LOGOS. A LOGOS then costs a miner what it costs to buy: at $0.01 a stake of 20,000 takes $200 of rent, on one board or on many.

The table simulates outside boards that start at 100 and grow by 25% an epoch while mining pays, at patience 1, the 90-10 split and 100 newcomers a month, with miners that keep mining. Counts with miners that stop differ by at most 20 nodes.

| Token price | Cost | Boards at the end | Income, LOGOS per month | Months to 20,000 / 10,000 on one board | Nodes at stake 20,000 / 10,000 | Outsiders' share of payouts |
| --- | --- | --- | --- | --- | --- | --- |
| $0.001 | $4.08 | no outsiders join | 3,340 | 6 / 3 | 1,850 / 2,150 | 0% |
| $0.002 | $4.08 | 4,010 | 2,040 | 9.8 / 4.9 | 1,460 / 1,950 | 66% |
| $0.005 | $4.08 | 10,024 | 816 | 24.5 / 12.3 | 320 / 1,180 | 85% |
| $0.01 | $4.08 | 20,048 | 408 | 49 / 24.5 | 85 / 410 | 91% |
| $0.05 | $4.08 | 100,240 | 82 | 245.1 / 122.5 | 4 / 210 | 97% |
| $0.005 | $21.30 | no outsiders join | 3,340 | 6 / 3 | 1,850 / 2,150 | 0% |
| $0.01 | $21.30 | 3,840 | 2,130 | 9.4 / 4.7 | 1,500 / 1,970 | 64% |
| $0.05 | $21.30 | 19,201 | 426 | 46.9 / 23.5 | 97 / 440 | 91% |
| $0.001 | $2.15 | 3,804 | 2,150 | 9.3 / 4.7 | 1,510 / 1,980 | 64% |
| $0.002 | $2.15 | 7,609 | 1,075 | 18.6 / 9.3 | 600 / 1,500 | 81% |
| $0.01 | $2.15 | 38,045 | 215 | 93 / 46.5 | 21 / 280 | 95% |
| $0.001 | $1 | 8,180 | 1,000 | 20 / 10 | 500 / 1,440 | 82% |
| $0.002 | $1 | 16,359 | 500 | 40 / 20 | 130 / 560 | 90% |
| $0.01 | $1 | 81,796 | 100 | 200 / 100 | 5 / 220 | 96% |

What this shows:

- A stake of 10,000 holds up far better than one of 20,000: 410 nodes against 85 at $0.01 and $4.08.
- Where a board would need longer than the period, the nodes counted are early arrivals, which mine at the minimum work before outsiders come. The counts therefore depend on when outsiders arrive. At $0.01 and $4.08 they are 320 / 610 from 10 starting boards, 1 / 240 from 1,000, and 0 / 170 with outsiders there at launch.
- Outsiders do not get a free pool, since they pay for each LOGOS in rent. They hold what they mine, 90% of it locked for a year, and could stake it. At $0.01 they mine enough for about 8,300 stakes of 20,000, so stakes still form, for whoever mines most.
- Rented plans that may mine cost $21.30 a board. At that cost outsiders join at $0.01 only if a vested LOGOS is worth at least 60% of a liquid one.
- Hash rate someone already owns costs only electricity, so it joins at lower prices than any rented plan. At $0.01 and $1 a board it leaves 100 LOGOS a month, so a board needs 100 months to reach 10,000. About 5,700 machines like the M4 Pro reach that income. Nodes fall to 5 / 220, and to none if 20,000 of those boards are there at launch.

The split matters only against miners that value a vested LOGOS below a liquid one. At $0.01 and $4.08, as boards at the end and nodes at stake 20,000 / 10,000:

| Vested-liquid | Patience 1 | Patience 0.5 | Patience 0 |
| --- | --- | --- | --- |
| 30-70 | 20,048: 85 / 410 | 17,041: 130 / 510 | 14,034: 180 / 730 |
| 50-50 | 20,048: 85 / 410 | 15,036: 160 / 630 | 10,024: 320 / 1,180 |
| 70-30 | 20,048: 85 / 410 | 13,031: 200 / 820 | 6,014: 950 / 1,710 |
| 90-10 | 20,048: 85 / 410 | 11,026: 270 / 1,060 | no outsiders: 1,850 / 2,150 |

So 90-10 does not keep a patient miner out. The period uses it for what it still does. It is the only split that keeps out, at $0.01, a miner that counts only its liquid income. It puts the least on the market, 20M LOGOS of the 200M. A stake also forms from vested notes alone in about the same time, as [The vested-liquid split](#the-vested-liquid-split) shows.

## Dependence on the puzzle

The reward of 334 LOGOS depends on replacing the reward puzzle first. `zkhash` is a small arithmetic kernel over one field, which dedicated hardware accelerates well, and no GPU has been measured on it. At this reward a board earns up to $33.40 a month at $0.01, so acceleration would pay. `POW_BOOTSTRAP_REWARD` should therefore not take this value while claims use `zkhash`. Blend admission keeps `zkhash`, since its solution is proven in a circuit.

A replacement addresses GPUs and dedicated hardware. It does not address desktops, which stay ahead of a board on both puzzles. In boards, where a board is 165,565 permutations a second on `zkhash` and 187 solves a second on [Equi-X](https://github.com/logos-blockchain/research/blob/blend-header-verification-benchmark/reports/EmPoWering/Equi-X/benchmark-findings/findings.md):

| Machine | `zkhash` | Equi-X |
| --- | --- | --- |
| Apple M4 Pro, 14 threads | 14.4 | 15.3 |
| Intel Core Ultra 9 285HX, 24 cores | not measured | 23.8 |

Owned hash rate at about $1 a board therefore stays the lower bound after the replacement.

The two caps and the retarget are stated in terms of `zkhash`. A new puzzle needs them restated, with the caps taken from measurements on a board. The size and fee of a claim may change too. The income and node figures of this RFC are per board, so they carry over once the caps are restated.

## The difficulty controller

The review of the retarget found three problems, all of which grow as the claim rate falls.

**A target of 10 claims per block does nothing at 334 LOGOS.** That rate empties the pool in under 3 epochs. Income per board stays at the minimum work's level however many boards mine, so it never falls toward the cost of a VPS, and outside hash rate races to empty the pool. With outsiders at $0.01 and a rent of $4.08, and 100 newcomers a month:

| Outside boards grow per epoch | Target 10: pool empty at epoch | Target 10: nodes at 20,000 / 10,000 | Paced target: nodes at 20,000 / 10,000 | Paced target: pool left at epoch 98 |
| --- | --- | --- | --- | --- |
| 5% | 87 | 1,580 / 1,880 | 1,240 / 1,620 | 58M |
| 10% | 55 | 780 / 1,090 | 560 / 880 | 38M |
| 25% | 28 | 110 / 410 | 85 / 410 | 19M |
| 50% | 17 | 0 / 130 | 3 / 270 | 11M |

The paced target's gain here is the pool, not the node count. A target of 10 onboards at least as many nodes up to 25% growth, since a newcomer keeps the income of the minimum work until the pool is empty. It onboards fewer only at 50%. A newcomer that arrives after the pool is empty earns nothing.

**Smoothing of 9/10 is too fast.** The target moves about 11% on an empty block, and at 0.283 claims per block it falls 20% on a single claim. Simulated block by block at that target, saturated:

| Smoothing | Rate above target | Swing of the target (standard deviation of its log) | Claims rejected after a delay of 10 blocks | Gain from holding a near miss for the window | Best hopper's income per hash, against a steady miner | Payout under that hopper | Time to follow a flood of 50 times | Time back to the cap after a flood of 5 times |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9/10 | +23% | 46% | 26% | +43% | 1.60 times | 1.48 times the target | 6 minutes | 7 minutes |
| 99/100 | +2.2% | 15% | 4.8% | +4.2% | 1.11 times | 1.04 times the target | 110 minutes | 128 minutes |
| 999/1000 | +0.2% | 4.6% | 0.5% | +0.4% | 1.01 times | 1.01 times the target | 16 hours | 18.5 hours |

A claim travels through Blend, so a miner holds a ticket found against one target and it is checked against a later one. A hopper mines only while the target is easy, so a faster controller pays it more. The same smoothing also helps after the period, at 10 claims per block, where 9/10 swings the target by 23% and rejects about 12% of claims after that delay, and 999/1000 swings it by 2.4% and rejects 0.2%.

The cost of 999/1000 is its slow response, and it is small. Before the target catches up with a sudden flood of 50 times, the flood takes about 1,200 extra claims, about 400k LOGOS, 0.2% of the pool.

**The rule cannot express a target below 1.** `TARGET_CLAIMS_PER_BLOCK` is an integer. A fraction put straight into the rule would also hit the floor of `demand` below about 0.1 claims per block, and tighten the target on every block, even an empty one.

The revision has three parts:

- During the period, the target is the rate that pays out `POW_REWARD_POOL_GENESIS` over `POW_BOOTSTRAP_EPOCHS` at `POW_BOOTSTRAP_REWARD`. It is derived from those three values and needs no new constant. The retarget works with it as a fraction, so the floor of `demand` no longer binds.
- `EMA_SMOOTHING_FACTOR / EMA_SMOOTHING_PRECISION` becomes 999/1000, and `REWARD_TARGET_FLOOR` follows at 999.
- Each period has its own cap. After the period the cap is `p // 2**29` instead of `p // 2**26`, so a board earns about 320 LOGOS a month, $3.20 at $0.01, below the rent of $4.08. The liquid part is 224 LOGOS.

The paced target has a cost when many real newcomers arrive at once, because it shares the payout among them. Nodes by epoch 98 with no outsiders, as stop / keep mining:

| Newcomers a month | Stake 20,000, target 10 | Stake 20,000, paced | Stake 10,000, target 10 | Stake 10,000, paced |
| --- | --- | --- | --- | --- |
| 100 | 1,850 / 1,850 | 1,850 / 1,850 | 2,150 / 2,150 | 2,150 / 2,150 |
| 200 | 3,710 / 3,660 | 3,710 / 2,990 | 4,300 / 4,270 | 4,300 / 3,820 |
| 500 | 8,300 / 4,690 | 5,960 / 3,610 | 10,760 / 6,190 | 10,760 / 6,560 |
| 1,000 | 6,820 / 4,860 | 2,210 / 2,030 | 17,800 / 7,850 | 13,270 / 7,150 |
| 2,000 | 3,690 / 3,300 | 35 / 33 | 16,200 / 9,280 | 4,950 / 4,290 |

A faster pace reduces this cost and empties the pool sooner. Outsiders here are at $0.01 and a rent of $4.08, growing 25% an epoch, with 100 newcomers a month:

| Pace, times the rate of the period | Pool empty at epoch, with outsiders | Nodes with outsiders, 20,000 / 10,000 | Nodes at 1,000 newcomers a month with no outsiders, stake 20,000, stop / keep mining |
| --- | --- | --- | --- |
| 1 | never | 85 / 410 | 2,210 / 2,030 |
| 1.5 | 76 | 68 / 360 | 4,210 / 3,470 |
| 2 | 61 | 62 / 340 | 5,690 / 4,170 |
| 3 | 47 | 57 / 350 | 6,820 / 4,730 |
| target 10, 35 | 28 | 110 / 410 | 6,820 / 4,860 |

This RFC uses a pace of 1. It is the one case where the pool lasts the period, which is what a two-year period means. A late newcomer therefore still earns, 408 LOGOS a month at $0.01, and the target holds a board's income at the cost of hash rate for all of that time. A pace of 1 does not onboard the most nodes. With outsiders the paces give 57 to 110 nodes at a stake of 20,000 and 340 to 410 at 10,000, since those nodes are the early arrivals. Without outsiders a faster pace gives more at high arrival rates. At or below about 100 newcomers a month, with one claim every 3 days and no outsiders, the paced target and a target of 10 agree.

## Stakes, onboarding times and nodes

These tables compare other minimum works, for the record, and have no outsiders. Each cell of the first gives the income per board per month that a stake and onboarding time need, and the days per claim at 334 LOGOS. The minimum work scales with the days per claim. A stake of 50,000 in 1 month needs about $`2^{29.8}`$ hashes per claim, and a stake of 10,000 in 6 months about $`2^{34.7}`$.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 50,000, 0.2 days | 30,000, 0.3 days | 20,000, 0.5 days | 10,000, 1 day |
| 2 | 25,000, 0.4 days | 15,000, 0.7 days | 10,000, 1 day | 5,000, 2 days |
| 3 | 16,667, 0.6 days | 10,000, 1 day | 6,667, 1.5 days | 3,333, 3 days |
| 4 | 12,500, 0.8 days | 7,500, 1.3 days | 5,000, 2 days | 2,500, 4 days |
| 5 | 10,000, 1 day | 6,000, 1.7 days | 4,000, 2.5 days | 2,000, 5 days |
| 6 | 8,333, 1.2 days | 5,000, 2 days | 3,333, 3 days | 1,667, 6 days |

At 334 LOGOS per claim:

| Stake | Stakes the pool can pay | Claims per stake | Spread of onboarding time | Declaration of all its claim notes |
| --- | --- | --- | --- | --- |
| 50,000 | 4,000 | 150 | ±8.2% | 300 notes, 12.7 KB, 8.1% of `G_max`, 10.2 LOGOS |
| 30,000 | 6,667 | 90 | ±10.5% | 180 notes, 7.9 KB, 5.0% of `G_max`, 6.3 LOGOS |
| 20,000 | 10,000 | 60 | ±12.9% | 120 notes, 5.4 KB, 3.4% of `G_max`, 4.3 LOGOS |
| 10,000 | 20,000 | 30 | ±18.3% | 60 notes, 3.0 KB, 1.8% of `G_max`, 2.4 LOGOS |

The spread is the Poisson spread of a node's claim count. The declaration uses the last value of `G_max`, 3,173,691, and the starting storage price.

With no outsiders the counts follow closed forms, where `B = 24.5` months and `O` is the months of mining. Of the 86 cells below with at least 500 nodes at 100 to 1,000 newcomers a month, the keep mining form is within 3% of the runs in 78 and within 13% in all.

```python
R = 8.18e6    # LOGOS per month at the target

# Miners stop. The target does not bind while newcomers finish as fast as they arrive.
stop = a * (B - O)    # while a <= R / S

# Miners keep mining. Boards reach the target once a * t = R * O / S.
keep = a * (B - O) if a * B <= R * O / S else a * B * exp(-a * S / R)
```

Nodes onboarded by epoch 98, as stop / keep mining. At 100 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 2,360 / 1,330 | 2,360 / 1,700 | 2,360 / 1,920 | 2,360 / 2,170 |
| 2 | 2,260 / 1,330 | 2,260 / 1,700 | 2,260 / 1,920 | 2,260 / 2,170 |
| 3 | 2,160 / 1,330 | 2,160 / 1,700 | 2,160 / 1,920 | 2,150 / 2,160 |
| 4 | 2,060 / 1,330 | 2,060 / 1,700 | 2,060 / 1,910 | 2,050 / 2,040 |
| 5 | 1,960 / 1,330 | 1,950 / 1,700 | 1,950 / 1,910 | 1,940 / 1,950 |
| 6 | 1,850 / 1,330 | 1,850 / 1,690 | 1,860 / 1,840 | 1,840 / 1,840 |

At 500 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 660 / 600 | 3,010 / 1,990 | 7,290 / 3,600 | 11,800 / 6,590 |
| 2 | 640 / 600 | 2,830 / 1,950 | 7,050 / 3,610 | 11,280 / 6,580 |
| 3 | 610 / 580 | 2,720 / 1,960 | 6,790 / 3,600 | 10,760 / 6,570 |
| 4 | 590 / 560 | 2,590 / 1,960 | 6,510 / 3,600 | 10,240 / 6,590 |
| 5 | 530 / 510 | 2,480 / 1,960 | 6,230 / 3,590 | 9,730 / 6,610 |
| 6 | 470 / 440 | 2,370 / 1,960 | 5,970 / 3,600 | 9,220 / 6,570 |

At the steady rate that gives the most nodes, swept for each cell:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 3,480 / 1,480 | 5,780 / 2,460 | 8,580 / 3,690 | 16,770 / 7,350 |
| 2 | 3,400 / 1,470 | 5,650 / 2,470 | 8,430 / 3,660 | 16,400 / 7,270 |
| 3 | 3,240 / 1,470 | 5,390 / 2,430 | 8,170 / 3,660 | 15,880 / 7,320 |
| 4 | 3,090 / 1,460 | 5,150 / 2,460 | 7,860 / 3,660 | 15,330 / 7,300 |
| 5 | 2,950 / 1,480 | 4,890 / 2,450 | 7,580 / 3,680 | 14,660 / 7,240 |
| 6 | 2,780 / 1,470 | 4,640 / 2,430 | 7,190 / 3,670 | 13,990 / 7,280 |

Miners that stop can onboard 70% to 87% of the stakes the pool can pay. Miners that keep mining can onboard about 37% of them, `capacity / e`, whatever the onboarding time, at `a = R / S`.

## Ranges that work

These checks decide whether a combination works. The limits of ±20% and 5% are choices this RFC makes.

| Check | Rule | Result at 334 LOGOS |
| --- | --- | --- |
| A stake fits one declaration | at most 3,783 notes | every stake and split: at most 500 notes |
| A claim pays its fee | the liquid part exceeds the fee at the highest storage price | every split, see [The vested-liquid split](#the-vested-liquid-split) |
| Fees stay small | the fee is at most 5% of the reward | every run: the price peaks at 32 times its start, a fee of 9.4 LOGOS, 2.8% of the reward |
| Onboarding is predictable | a spread of at most ±20%, so at least 25 claims per stake | every stake: at most ±18.3% |
| The activity proof holds | at most 8,191 providers | miners that keep mining stay below it in every run without outsiders; miners that stop pass it at stakes of 20,000 and 10,000 at high arrival rates |
| The onboarding time holds | it holds for every newcomer until epoch 98, with nobody stopping and no outsiders | depends on the income per board, below |
| Income does not pay rent | a board's whole income at the minimum work stays below the rent at $0.01 | no stake and onboarding time passes, below |
| Liquid income does not pay rent | the liquid part stays below the rent at $0.01, which keeps out a miner that counts only its liquid income | depends on the income per board and the split |

The onboarding time holds while a board's income per month is at most `R / (a * B)`: 6,678 LOGOS at 50 newcomers a month, 3,339 at 100 and 1,670 at 200. Each cell gives the most newcomers a month for which it holds. If miners stop, it holds up to `R / S`: 164, 273, 409 and 818 a month at the four stakes.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 7 | 11 | 17 | 33 |
| 2 | 13 | 22 | 33 | 67 |
| 3 | 20 | 33 | 50 | 100 |
| 4 | 27 | 45 | 67 | 134 |
| 5 | 33 | 56 | 83 | 167 |
| 6 | 40 | 67 | 100 | 200 |

With 100 newcomers a month as the reference, an assumption of this RFC:

| Stake | Months of mining at which the onboarding time holds | Nodes by epoch 98, miners keep mining | Most nodes, miners stop / keep mining | Nodes with outsiders at $0.01 and $4.08, one claim every 3 days |
| --- | --- | --- | --- | --- |
| 50,000 | from 15, none up to 6 | 1,330 | 2,780 to 3,480 / about 1,470 | 0 |
| 30,000 | from 9, none up to 6 | 1,690 to 1,700 | 4,640 to 5,780 / about 2,450 | 0 |
| 20,000 | 6 | 1,840 | 7,190 to 8,580 / about 3,670 | 85 |
| 10,000 | 3 to 6 | 1,840 to 2,160 | 13,990 to 16,770 / about 7,300 | 410 |

No stake and onboarding time in these tables passes the check on the whole income. At $0.01 and $4.08 that check needs at most 408 LOGOS a month, which puts a stake of 20,000 at 49 months and a stake of 10,000 at 24.5. The minimum work therefore cannot keep a patient miner out at $0.01. The target does that, at the cost in nodes in the last column.

The income of one claim every 3 days is the highest that passes the onboarding check and the check on liquid income at 90-10: a stake of 20,000 at 6 months, or a stake of 10,000 at 3 months. In those cells stop and keep mining agree within about 1%, so no rule is needed to make miners stop.

The reward has a range of its own. The fee check needs a reward of at least 187 LOGOS at a 32-fold price, or 275 LOGOS at the 47-fold price a slower three-year arrival gives. The spread check needs at most `S / 25`: 2,000, 1,200, 800 and 400 LOGOS at the four stakes. A reward from 275 to 400 LOGOS therefore serves all four, and 334 sits inside it.

## The vested-liquid split

A node that stakes both parts of its claims needs the same claims at every split, so the node counts above hold for all four splits when no outsiders mine, and at patience 1 when they do. The split changes what a node can do with its liquid part, and how much of the pool can reach the market at once.

| Vested-liquid | Per claim, vested / liquid, LOGOS | Liquid part ÷ claim fee, at the start / at 32 times | Time to a stake of vested notes alone | Notes for that stake, at 20,000 / 10,000 | Liquid share of the 200M |
| --- | --- | --- | --- | --- | --- |
| 30-70 | 100.2 / 233.8 | 801 / 25 | 3.3 × `O` | 200 / 100 | 140M |
| 50-50 | 167 / 167 | 572 / 18 | 2 × `O` | 120 / 60 | 100M |
| 70-30 | 233.8 / 100.2 | 343 / 11 | 1.4 × `O` | 86 / 43 | 60M |
| 90-10 | 300.6 / 33.4 | 114 / 3.6 | 1.1 × `O` | 67 / 34 | 20M |

A node that sells its liquid part and stakes vested notes alone needs longer. At one claim every 3 days, as stop / keep mining:

| Vested-liquid | Stake 20,000: time | At 100 a month | At 500 a month | Stake 10,000: time | At 100 a month | At 500 a month |
| --- | --- | --- | --- | --- | --- | --- |
| 30-70 | 20 months | 440 / 450 | 0 / 0 | 10 months | 1,460 / 1,450 | 1,470 / 1,360 |
| 50-50 | 12 months | 1,250 / 1,250 | 490 / 490 | 6 months | 1,860 / 1,860 | 6,190 / 3,670 |
| 70-30 | 8.6 months | 1,610 / 1,600 | 2,490 / 2,100 | 4.3 months | 2,030 / 2,020 | 10,160 / 5,180 |
| 90-10 | 6.7 months | 1,800 / 1,790 | 4,770 / 3,190 | 3.3 months | 2,120 / 2,120 | 10,620 / 6,180 |

At 90-10 a stake forms from vested notes alone in about the same time, and the node keeps its liquid part for fees. The liquid part still pays a claim's fee up to 114 times the starting storage price. A newcomer on a rented machine pays rent from other funds, since the liquid part stays below the rent. On a Raspberry Pi 5 at home at $0.01, the liquid part of 334 LOGOS a month, $3.34, covers the electricity of $2.15. Once outsiders bring the income to 408 LOGOS a month, the liquid part falls to $0.41 and no longer does.

## Stopping

No rule can make a node stop, because every claim pays a fresh key. Service rewards of 5.0M / `N` LOGOS a month exceed a board's 3,340 LOGOS below 1,500 providers, and its 408 LOGOS at $0.01 and $4.08 below about 12,000. But Blend uses at most one of a board's four cores, so a provider can also keep mining on the others. Stop is therefore an upper bound on the count, and keep mining the expected case.

More providers are not always better. An earlier estimate puts one limit at about 8,000 providers, where service rewards still cover a $6.12 machine at $0.01. The activity proof sets another. On cover traffic alone it fails by chance under 0.05% of the time up to 8,191 providers, 6.6% at 8,192 and 11% at 10,000, and data traffic lowers these. With `inactivity_period` at 2, a failed proof costs a locked provider epochs until its lock ends. At 6.6% about 27% of locked providers are out for good within a year, and at 11% about 57%. At a stake of 10,000 the pool can pay for 20,000 providers, more than either limit.

## After epoch 98

After the period the reward only has to pay for a transaction, and every reward vests at 30-70. An average transaction here holds a claim, the Transfer that spends its liquid note and an inscription of 100 bytes:

| Part | Bytes |
| --- | --- |
| Operation count | 1 |
| Claim, with an empty proof | 129 |
| Transfer of one input and one output, with its proof | 235 |
| Inscription of 100 bytes, with its signature | 267 |
| Total | 632 |

Its fee is 0.51 LOGOS at the starting storage price, or 0.82 LOGOS at 1.62 times that price, the rise a steady load causes. Execution gas adds under 0.001 LOGOS at the starting base fee. Dividing by the liquid share of 70% gives 1.17 LOGOS, and the reward rounds up to 1.2 LOGOS. Its liquid part of 0.84 LOGOS pays for this transaction up to 1.66 times the starting price. This value is a placeholder to revise once real fees are known.

At `REWARD_TARGET_CAP` a board finds a claim about every 2.7 hours, and a participant with nothing can pay for its first transaction after that. At the target the payout is 259,200 LOGOS an epoch. So 99M LOGOS left at epoch 98 lasts about 380 epochs, and 19M lasts about 73. After that, only the fee share of each block pays claims.

The change at epoch 98 is abrupt:

- A newcomer short of its stake at epoch 98 then earns at most about 320 LOGOS a month, so it finishes by other means or not at all. At a stake of 20,000, that is any newcomer arriving in the last 6 months of the period.
- If claims had been the only storage use, the storage price would stand at about 6.6 times its start at $0.01 and $4.08, a fee of about 1.9 LOGOS, above the reward. With no outsiders it would stand at about 31 times, a fee of about 9 LOGOS. Claims would stop for about 7 and 18 epochs while the price falls.
- The cap takes about 27 hours to reach its new value.

## Era parameters

`POW_BOOTSTRAP_EPOCHS`, `POW_BOOTSTRAP_REWARD`, `POW_BOOTSTRAP_VESTED_SHARE`, `POW_BOOTSTRAP_TARGET_CAP`, `POW_REWARD`, `REWARD_TARGET_CAP` and `POW_VESTED_SHARE` are era parameters. Eras specifies the era parameter record, and this branch does not have it, so their fields go into whichever of the two specifications lands second.

## Compatibility

The chain has not launched, so no migration is needed. Claims, their encoding and the circuits do not change.

## Open questions

- **The token price.** All the rent checks depend on it, and it is not known. Above $0.0012 a board's income at the minimum work exceeds the cheapest rent, and the target then does the work. Above $0.012 its liquid part does too.
- **The minimum stake.** No specification sets it. The analysis of the minimum stake gives 0.001% of the supply at launch, which is 100,000 LOGOS if that supply is the cap. Stakes of 20,000 and 10,000 are 0.0002% and 0.0001% of the cap. That analysis should change with any value chosen here, and this branch does not change it. A lower stake lets the same pool fund more provider identities, but it also holds up better against outside mining.
- **Hash rates and power still to measure.** The rents in this RFC count 1.5 Raspberry Pi 5 cores per vCPU, within a range of 1 to 2, and no rented machine has been measured. The owned machine's power is assumed. No GPU has been measured on any puzzle.
- **The end of the period.** A softer change at epoch 98 could help newcomers partway to a stake. It would add a rule.
- **The pool.** 200M LOGOS is 2% of the supply cap, four times the current seed, and it comes out of the initial distribution.
- **Privacy.** With 334 LOGOS per claim a spend hides among far fewer claims. At 100 newcomers a month, an epoch holds about 60 claims at launch and about 6,000 at the end if nobody stops. If everybody stops at a stake of 20,000, it holds about 1,500 from month 6 on.
- **Storage price.** The price model counts claims as the only storage use. Other traffic changes its path, and the size of the fall in fees at epoch 98.
- **The puzzle.** Which puzzle replaces `zkhash` for rewards is not settled. Equi-X has a benchmark, and its author has since deprecated it in favour of HashWX, which has none here.

# Details

## 1. Fixed rewards and vested shares

A claim pays one fixed reward and vested share during the first `POW_BOOTSTRAP_EPOCHS` epochs, the bootstrapping period, and another after it. The rule that computed the reward from the pool goes, with `EPOCH_POW_DISTRIBUTION_RATE_NUM` and `EPOCH_POW_DISTRIBUTION_RATE_DEN`.

```diff
+POW_BOOTSTRAP_EPOCHS: uint64 = 98               # the length of the bootstrapping period, in epochs
+POW_BOOTSTRAP_REWARD: TokenValue = 334 * 10**9  # the reward per claim during it, 334 LOGOS, in LEPTA
+POW_BOOTSTRAP_VESTED_SHARE: uint64 = 90         # the share of that reward paid as a vested note
+POW_REWARD: TokenValue = 12 * 10**8             # the reward per claim after it, 1.2 LOGOS, in LEPTA
-POW_VESTED_SHARE: uint64 = 50
+POW_VESTED_SHARE: uint64 = 30                   # the share of that reward paid as a vested note

-def compute_epoch_pow_reward(pow_reward_pool: TokenValue) -> TokenValue:
-    # ... a share of the pool, over the target claims of an epoch
+def compute_epoch_pow_reward(epoch: EpochNumber) -> tuple[TokenValue, uint64]:
+    # The reward per claim, and the share of it paid as a vested note.
+    if epoch < POW_BOOTSTRAP_EPOCHS:
+        return POW_BOOTSTRAP_REWARD, POW_BOOTSTRAP_VESTED_SHARE
+    return POW_REWARD, POW_VESTED_SHARE
```

At each epoch boundary `epoch_pow_reward` and `epoch_pow_vested_share` are set for the new epoch and held for it. A claim still needs the pool to cover the reward, as [CLAIM_POW_REWARD](../bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation requires. Claiming resumes when the fee shares of the blocks bring the pool back to the reward, or at the end of the period if the pool covers `POW_REWARD`.

`POW_BOOTSTRAP_EPOCHS` is the number of epochs that first reaches two years, $`\lceil 730 / 7.5 \rceil = 98`$. The constraint that the vested notes of a minimum stake fit one declaration now reads `POW_BOOTSTRAP_REWARD`.

## 2. The difficulty controller

```diff
+POW_BOOTSTRAP_TARGET_CAP: PowTarget = p // 14_300_000_000
-EMA_SMOOTHING_FACTOR: uint64 = 9
-EMA_SMOOTHING_PRECISION: uint64 = 10
-REWARD_TARGET_FLOOR: uint64 = 9
-REWARD_TARGET_CAP: PowTarget = p // 2**26
+EMA_SMOOTHING_FACTOR: uint64 = 999
+EMA_SMOOTHING_PRECISION: uint64 = 1000
+REWARD_TARGET_FLOOR: uint64 = 999
+REWARD_TARGET_CAP: PowTarget = p // 2**29

+def target_claims_per_block(epoch: EpochNumber) -> tuple[uint64, uint64]:
+    if epoch < POW_BOOTSTRAP_EPOCHS:
+        return (POW_REWARD_POOL_GENESIS,
+                POW_BOOTSTRAP_REWARD * POW_BOOTSTRAP_EPOCHS * EXPECTED_BLOCKS_PER_EPOCH)
+    return TARGET_CLAIMS_PER_BLOCK, 1
+
 def compute_new_reward_difficulty(claims_in_block: uint64,
-                                  current_target: PowTarget) -> PowTarget:
+                                  current_target: PowTarget,
+                                  epoch: EpochNumber) -> PowTarget:
-    demand = max(1, (P - F) * claims_in_block + F * TARGET_CLAIMS_PER_BLOCK)
-    new_target = (TARGET_CLAIMS_PER_BLOCK * current_target * P) // demand
-    return min(max(new_target, REWARD_TARGET_FLOOR), REWARD_TARGET_CAP)
+    num, den = target_claims_per_block(epoch)
+    demand = max(1, (P - F) * claims_in_block * den + F * num)
+    new_target = (num * current_target * P) // demand
+    cap = POW_BOOTSTRAP_TARGET_CAP if epoch < POW_BOOTSTRAP_EPOCHS else REWARD_TARGET_CAP
+    return min(max(new_target, REWARD_TARGET_FLOOR), cap)
```

`epoch` is the epoch of the processed block. At genesis `difficulty_reward` is `POW_BOOTSTRAP_TARGET_CAP`. `P` and `F` stand for the two smoothing constants. The product of the retarget stays below $`2^{322}`$, inside the 512 bits [Puzzle Target](../proof-of-work.md#puzzle-target) allows.

Both caps are calibrated against the measurement of `BLEND_DIFFICULTY_BASE`, $`2^{19}`$ hashes in about 38 seconds on one core. The four cores of the target machine find a claim about every 3 days at `POW_BOOTSTRAP_TARGET_CAP` and about every 2.7 hours at `REWARD_TARGET_CAP`.

## 3. The vested share in Mantle

Validators keep `epoch_pow_vested_share` beside `epoch_pow_reward`, and a claim reads it.

```diff
-vested_value = checked_uint64(epoch_pow_reward * POW_VESTED_SHARE) // SHARE_DEN
+vested_value = checked_uint64(epoch_pow_reward * epoch_pow_vested_share) // SHARE_DEN
```

The check `assert epoch_pow_reward > 0` goes, since both rewards are positive constants.

## 4. The pool seed

`POW_REWARD_POOL_GENESIS` becomes two hundredths of $`S_{cap}`$, 200M LOGOS, instead of five thousandths. Genesis sets `epoch_pow_reward` and `epoch_pow_vested_share` by the same computation.

## Chores

- The Overview of Proof of Work says what a claim pays in each period, and the target rate of the first.
- The Notation of Proof of Work drops the distribution rate.

# Implementation

- [ ] Land this after the reward puzzle is replaced, and restate the two caps and the retarget for the new puzzle, as [Dependence on the puzzle](#dependence-on-the-puzzle) says.
- [ ] Add the constants of the period and change the shares, the smoothing, the floor and the cap, with the values chosen from [Ranges that work](#ranges-that-work).
- [ ] Set `epoch_pow_reward` and `epoch_pow_vested_share` by epoch at each epoch boundary and at genesis, and remove the reward computed from the pool.
- [ ] Apply the target and the cap by the epoch of the processed block, and start `difficulty_reward` at `POW_BOOTSTRAP_TARGET_CAP`.
- [ ] Read `epoch_pow_vested_share` in `CLAIM_POW_REWARD`.
- [ ] Seed the pow reward pool with two hundredths of the supply cap.
- [ ] Measure the claims per epoch of a Raspberry Pi 5 at both caps, the hash rate of a rented vCPU and of a GPU, and the power of an owned desktop.
- [ ] Add the seven constants to the era parameter record once Eras and this change are on one branch.
- [ ] Revise `POW_REWARD` once real fees are known.
- [ ] Add tests: the reward and share at epochs 97 and 98, a claim against a pool below the reward, the retarget at the cap in both periods, a block with claims at the fractional target, the genesis values.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.4.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.4.0 |
