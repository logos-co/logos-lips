# [RFC] Proof of Work: Pay a fixed reward during a bootstrapping period

**Motivation and proposal:** [PR #521](https://github.com/logos-co/logos-lips/pull/521)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-06 |
| v2 | Outside mining takes a patience of 1 as its base case, so the rent check counts a board's whole income | 2026-11-06 |
| v3 | Owned hash rate is the lower bound on the cost of a board, and the reward of 334 LOGOS depends on replacing the reward puzzle | 2026-11-06 |
| v4 | After the period the reward is derived from the storage price, and the target pays out a ninety-eighth of the pool per epoch | 2026-11-06 |
| v5 | The caps are calibrated on a claim ticket of 4 permutations, so a board does find a claim about every 3 days | 2026-11-06 |
| v6 | The base case moves to a token price of $0.05, and the analysis compares stakes of 50,000, 30,000, 20,000 and 10,000 | 2026-11-06 |
| v7 | The seed is paced over one epoch more than the period, and the target after it pays out a ninety-ninth of the pool per epoch | 2026-11-06 |
| v8 | Corrections from the review: the constraints on rewards and shares, service rewards of 4.93M LOGOS a month, the assumptions of the model, the smoothing table, and two more open questions. Block Rewards says its projection leaves out claims | 2026-11-06 |
| v9 | The reward per claim during the period becomes 100 LOGOS, and its cap moves so that a board's income stays about the same. A new section compares other values | 2026-11-06 |
| v10 | Corrections from a review against the calculator: claim fees take 1% to 6% of a board's income, the storage price peaks at up to 32 times, the reward-10 row follows the paced renter rule, and smaller figures and wording | 2026-11-09 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the rewards](#1-fixed-rewards-and-vested-shares) | every node switches the reward and the share at the same epoch; after it the reward follows the storage price; the rule that computed the reward from the pool is gone |
| 2 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the difficulty controller](#2-the-difficulty-controller) | the target as a fraction of the pool, the caps by epoch, the new smoothing and floor, against [The difficulty controller](#the-difficulty-controller) |
| 3 | High | [Mantle](#affected-specifications), [the vested share](#3-the-vested-share-in-mantle) | a claim reads `epoch_pow_vested_share`; the positive reward check goes |
| 4 | Medium | [Genesis Block](#affected-specifications), [the pool seed](#4-the-pool-seed) | 200M LOGOS drawn from the initial distribution |

# Discussion

## The design

A **board** is one Raspberry Pi 5 with four cores, the target machine of [Proof of Work](../proof-of-work.md). All the figures below follow from these values.

|  | First 98 epochs (two years) | After epoch 98 |
| --- | --- | --- |
| Reward per claim | 100 LOGOS | enough for its liquid part to pay for a 632-byte transaction at the storage price of the epoch, 0.72 LOGOS at the starting price |
| Vested-liquid split | 90-10 | 30-70 |
| A claim on a board, at the minimum work | about every 21.6 hours | about every 2.7 hours |
| Income per board per month, at the minimum work | about 3,330 LOGOS, 333 of it liquid | about 270 rewards, 70% of each liquid |
| Target | 0.935 claims per block, which pays out 198M of the 200M LOGOS over the period | the rate that pays out a ninety-ninth of the pool per epoch |
| Payout per month at the target | about 8.1M LOGOS | about 4% of the pool |

No rule limits the claims of an epoch. Only the difficulty controls them, through the minimum work and the retarget. A month here is 4 epochs, 30 days, and the period is 24.5 months.

At this income a stake of 50,000 LOGOS takes 500 claims, 15 months of mining. A stake of 30,000 takes 300 claims, 9 months. A stake of 20,000 takes 200 claims, 6 months. A stake of 10,000 takes 100 claims, 3 months. No specification sets the minimum stake. This RFC compares these four, at the same minimum work, and does not consider 100,000.

These times hold while no outsiders mine. This RFC takes a token price of $0.05, which values the supply cap at $500M. At that price and a rent of $4.08 a month, outsiders bring a board's income down to 82 LOGOS a month, and the times become 613, 368, 245 and 123 months. [Outside mining](#outside-mining) gives this base case.

These values assume the reward puzzle is replaced first, as [Dependence on the puzzle](#dependence-on-the-puzzle) says.

## The model

The figures come from a simulation of the 98 epochs:

- The pool holds 200M LOGOS. Only its fee share of claim fees refills it. Fees from other traffic would add to it.
- Each newcomer runs one board, and newcomers arrive at a steady rate `a` per month for the whole period.
- A board's claims per epoch follow a Poisson distribution. No rule limits claims. The retarget makes the puzzle harder while claims outpace the target rate, and the model applies its average over an epoch: the lesser of what boards find at the minimum work and the target rate.
- The retarget overshoots its target by about 0.1% at 0.935 claims per block, so the payout at the target is `R = 200M / 99 * 1.0011 * 4`, 8.09M LOGOS a month.
- Every claim pays a fee for its 365-byte transaction, at a storage price that follows [Storage Markets](../storage-markets.md) with claims as the only storage use.
- A newcomer is **onboarded** when its rewards, minus the fees of its claims and of its declaration, reach the stake by epoch 98.
- A node either **stops** mining at the claim that completes its stake or **keeps mining** until the end.
- Only proof of work rewards count. Leadership rewards on vested notes would shorten onboarding.
- A table without outsiders is the best case for newcomers. It holds only while a board's income times the token price stays below the cost of a board.

Each figure is the mean of three to five runs, rounded to 10 from 100 up. Sweeps for the best arrival rate use one run per rate. Run on the inputs of an earlier analysis, the same model gives that analysis's figures to within 4%: 2,093 nodes against 2,094, and 1,374, 1,012 and 468 nodes against 1,375, 985 and 451 with outside hash rate.

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
| Contabo Cloud VDS S, 6 dedicated threads | $48 on a 24-month term | 2.25 | $21.33 | allowed |

A board's income depends on how many boards mine. Up to 2,429 boards each earns the income of the minimum work. Above that the target holds the payout at 8.09M LOGOS a month, and they share it.

| Boards mining | Income per board per month, LOGOS | Liquid part at 90-10 | Total at $0.05 per LOGOS | Liquid part at $0.05 |
| --- | --- | --- | --- | --- |
| up to 2,429 | 3,331 | 333 | $166.53 | $16.65 |
| 5,000 | 1,618 | 162 | $80.90 | $8.09 |
| 10,000 | 809 | 81 | $40.45 | $4.04 |
| 20,000 | 404 | 40 | $20.22 | $2.02 |
| 50,000 | 162 | 16 | $8.09 | $0.81 |
| 100,000 | 81 | 8 | $4.04 | $0.40 |

The token prices up to which a board's income at the minimum work stays below each cost:

| Cost per board per month | Token price, whole income | Token price, liquid part at 90-10 |
| --- | --- | --- |
| $1 | $0.0003 | $0.003 |
| $2.15 | $0.00065 | $0.0065 |
| $4.08 | $0.0012 | $0.012 |
| $6.12 | $0.0018 | $0.018 |
| $21.33 | $0.0064 | $0.064 |

So at $0.05 a board's income at the minimum work, $167, is 41 times the rent of $4.08. Outsiders join above $0.0012, and the target brings the income back to the rent, as [Outside mining](#outside-mining) shows. The liquid part alone, $16.65, is also above the rent, so a miner that counts only its liquid income joins too, above $0.012. Holding the whole income below the rent at $0.05 by the minimum work alone would need a claim about every 37 days. That puts even a stake of 10,000 at 122.5 months, five times the period.

Average income over the period, per newcomer's board, with miners that keep mining:

| Case | Average, LOGOS per month | At epoch 98, LOGOS per month | Average at $0.05 | Liquid part of the average at $0.05 |
| --- | --- | --- | --- | --- |
| 100 newcomers a month, no outsiders | 3,330 | 3,300 | $166.50 | $16.65 |
| 200 newcomers a month, no outsiders | 2,470 | 1,650 | $123.50 | $12.35 |
| 500 newcomers a month, no outsiders | 1,180 | 660 | $59.00 | $5.90 |
| 1,000 newcomers a month, no outsiders | 620 | 330 | $31.00 | $3.10 |
| 100 newcomers a month, outsiders renting at $4.08 | 210 | 82 | $10.50 | $1.05 |

Claim fees take 1% to 6% of this. A node that has declared also earns service rewards, about 4.93M / `N` LOGOS a month among `N` providers while total stake is below 28.8% of the cap. That covers a $6.12 machine at $0.05 up to about 40,000 providers. Providing a service therefore pays for the machine. Once outsiders have joined, mining pays a board no more than its cost.

## Outside mining

Mining pays anyone, not only newcomers. An outsider adds boards while a board-month is worth more than it costs. A board-month is worth `income * p * (1 - v + v * d)`, where `p` is the token price, `v` the vested share, and `d` the miner's **patience**: what a LOGOS that vests in a year is worth to it today. With a target that holds the payout at `R = 8.09M` LOGOS a month, boards join until the value equals the cost `c`:

```python
boards = R * p * (1 - v + v * d) / c
income = c / (p * (1 - v + v * d))    # at most 3,331 LOGOS a month
```

The base case is a patience of 1, for the reasons in [Income per node against a VPS](#income-per-node-against-a-vps). It is also the upper bound, since a liquid LOGOS can do all that a vested one can. The split then drops out: `boards = R * p / c` and `income = c / p`. The base cost is the cheapest rent, $4.08. Hash rate someone already owns, at about $1 a board, is the lower bound.

The target therefore holds a board's income at the cost of the cheapest hash rate, at any token price, without knowing the price. A rise in price brings more boards and lowers the income in LOGOS. A LOGOS then costs a miner what it costs to buy: at $0.05 a stake of 20,000 takes $1,000 of rent, on one board or on many.

The table simulates outside boards that start from 100 and grow by 25% an epoch while mining pays, at patience 1, the 90-10 split and 100 newcomers a month, with miners that keep mining. Outsiders first mine in the second epoch, with 125 boards. Counts with miners that stop differ by at most 50 nodes.

| Token price | Cost | Boards at the end | Income, LOGOS per month | Months to 50,000 / 30,000 / 20,000 / 10,000 on one board | Nodes at stake 50,000 / 30,000 / 20,000 / 10,000 | Outsiders' share of payouts |
| --- | --- | --- | --- | --- | --- | --- |
| $0.001 | $4.08 | no outsiders join | 3,331 | 15 / 9 / 6 / 3 | 830 / 1,470 / 1,790 / 2,130 | 0% |
| $0.002 | $4.08 | 3,966 | 2,040 | 24.5 / 14.7 / 9.8 / 4.9 | 110 / 940 / 1,460 / 1,960 | 65% |
| $0.005 | $4.08 | 9,914 | 816 | 61.3 / 36.8 / 24.5 / 12.3 | 0 / 25 / 310 / 1,200 | 85% |
| $0.01 | $4.08 | 19,828 | 408 | 122.5 / 73.5 / 49 / 24.5 | 0 / 0 / 80 / 400 | 91% |
| $0.05 | $4.08 | 99,138 | 82 | 612.7 / 367.6 / 245.1 / 122.5 | 0 / 0 / 1 / 210 | 97% |
| $0.10 | $4.08 | 198,277 | 41 | 1,225.5 / 735.3 / 490.2 / 245.1 | 0 / 0 / 0 / 190 | 97% |
| $0.005 | $21.33 | no outsiders join | 3,331 | 15 / 9 / 6 / 3 | 830 / 1,470 / 1,790 / 2,130 | 0% |
| $0.01 | $21.33 | 3,793 | 2,133 | 23.4 / 14.1 / 9.4 / 4.7 | 170 / 1,020 / 1,490 / 1,980 | 64% |
| $0.05 | $21.33 | 18,963 | 427 | 117.2 / 70.3 / 46.9 / 23.4 | 0 / 0 / 90 / 410 | 91% |
| $0.10 | $21.33 | 37,926 | 213 | 234.4 / 140.6 / 93.8 / 46.9 | 0 / 0 / 9 / 280 | 94% |
| $0.001 | $2.15 | 3,763 | 2,150 | 23.3 / 14 / 9.3 / 4.7 | 190 / 1,020 / 1,500 / 1,980 | 63% |
| $0.002 | $2.15 | 7,525 | 1,075 | 46.5 / 27.9 / 18.6 / 9.3 | 0 / 160 / 560 / 1,500 | 81% |
| $0.01 | $2.15 | 37,626 | 215 | 232.6 / 139.5 / 93 / 46.5 | 0 / 0 / 9 / 280 | 94% |
| $0.05 | $2.15 | 188,132 | 43 | 1,162.8 / 697.7 / 465.1 / 232.6 | 0 / 0 / 0 / 200 | 97% |
| $0.001 | $1 | 8,090 | 1,000 | 50 / 30 / 20 / 10 | 0 / 110 / 460 / 1,430 | 82% |
| $0.002 | $1 | 16,179 | 500 | 100 / 60 / 40 / 20 | 0 / 0 / 130 / 510 | 90% |
| $0.01 | $1 | 80,897 | 100 | 500 / 300 / 200 / 100 | 0 / 0 / 1 / 220 | 96% |
| $0.05 | $1 | 404,485 | 20 | 2,500 / 1,500 / 1,000 / 500 | 0 / 0 / 0 / 190 | 97% |

What this shows:

- At $0.05 and $4.08 only a stake of 10,000 onboards anyone in numbers: 210 nodes, against an average below 1 at 20,000 and none at 30,000 or 50,000.
- Where a board would need longer than the period, the nodes counted are early arrivals, which mine at the minimum work before outsiders come. The counts therefore depend on when outsiders arrive. At $0.05 and $4.08 they are 0 / 0 / 140 / 450 from 10 starting boards and 0 / 0 / 0 / 2 from 1,000. They are 0 at every stake from 10,000 starting boards, or with outsiders at their full count from the second epoch.
- Outsiders do not get a free pool, since they pay for each LOGOS in rent. They hold what they mine, 90% of it locked for a year, and could stake it. At $0.05 they mine about 173M LOGOS for about $8.7M of rent, enough for about 3,500, 5,800, 8,700 or 17,300 stakes, so stakes still form, for whoever mines most.
- Rented plans that may mine cost $21.33 a board. At $0.05 outsiders join there as well, if a vested LOGOS is worth at least 3% of a liquid one. A board then earns 427 LOGOS a month, and the nodes are 0 / 0 / 90 / 410.
- Hash rate someone already owns costs only electricity, so it joins at lower prices than any rented plan. At $0.05 and $1 a board it leaves 20 LOGOS a month, so a board needs 500 months to reach 10,000. About 28,000 machines like the M4 Pro reach that income. Nodes fall to 0 / 0 / 0 / 190, and to none if 20,000 of those boards mine from the second epoch.

The split matters only against miners that value a vested LOGOS below a liquid one. At $0.05 and $4.08, as boards at the end and nodes at stake 50,000 / 30,000 / 20,000 / 10,000:

| Vested-liquid | Patience 1 | Patience 0.5 | Patience 0 |
| --- | --- | --- | --- |
| 30-70 | 99,138: 0 / 0 / 1 / 210 | 84,268: 0 / 0 / 1 / 220 | 69,397: 0 / 0 / 1 / 230 |
| 50-50 | 99,138: 0 / 0 / 1 / 210 | 74,354: 0 / 0 / 0 / 230 | 49,569: 0 / 0 / 2 / 260 |
| 70-30 | 99,138: 0 / 0 / 1 / 210 | 64,440: 0 / 0 / 1 / 240 | 29,742: 0 / 0 / 21 / 320 |
| 90-10 | 99,138: 0 / 0 / 1 / 210 | 54,526: 0 / 0 / 2 / 250 | 9,914: 0 / 25 / 310 / 1,200 |

So 90-10 keeps out neither a patient miner nor, at $0.05, a miner that counts only its liquid income. The period uses it for what it still does. It draws the fewest boards from miners that value a vested LOGOS less, 9,914 at patience 0 against 69,397 at 30-70. It puts the least on the market, 20M LOGOS of the 200M. A stake also forms from vested notes alone in about the same time, as [The vested-liquid split](#the-vested-liquid-split) shows.

## Dependence on the puzzle

The reward of 100 LOGOS depends on replacing the reward puzzle first. `zkhash` is a small arithmetic kernel over one field, which dedicated hardware accelerates well, and no GPU has been measured on it. At this reward a board earns up to $167 a month at $0.05, so acceleration would pay. `POW_BOOTSTRAP_REWARD` should therefore not take this value while claims use `zkhash`. Blend admission keeps `zkhash`, since its solution is proven in a circuit.

A replacement addresses GPUs and dedicated hardware. It does not address desktops, which stay ahead of a board on both puzzles. In boards, where a board is 165,565 permutations a second on `zkhash` and 187 solves a second on [Equi-X](https://github.com/logos-blockchain/research/blob/blend-header-verification-benchmark/reports/EmPoWering/Equi-X/benchmark-findings/findings.md):

| Machine | `zkhash` | Equi-X |
| --- | --- | --- |
| Apple M4 Pro, 14 threads | 14.4 | 15.3 |
| Intel Core Ultra 9 285HX, 24 cores | not measured | 23.8 |

Owned hash rate at about $1 a board therefore stays the lower bound after the replacement.

The two caps and the retarget are stated in terms of `zkhash`. A new puzzle needs them restated, with the caps taken from measurements on a board. The size and fee of a claim may change too. The income and node figures of this RFC are per board, so they carry over once the caps are restated.

## The cost of a claim ticket

The caps assume a claim ticket of 4 permutations, since a board's rate comes from a Blend ticket of 3. A claim ticket hashes 5 inputs, which costs 6 permutations. A miner reuses the hash of the tag and the public key, so each nonce costs 4. It can go lower by sharing more of the hash, trying both epoch nonces a claim may name and the 10 recent blocks it may name:

| Ticket | Permutations | Days per claim on a board | Income per board per month, LOGOS | Months to 50,000 / 30,000 / 20,000 / 10,000 on one board | Nodes with no outsiders at those stakes | Nodes at $0.05 and $4.08 at those stakes |
| --- | --- | --- | --- | --- | --- | --- |
| Plain | 6 | 1.35 | 2,220 | 22.5 / 13.5 / 9 / 4.5 | 68 / 990 / 1,470 / 1,960 | 0 / 0 / 0 / 130 |
| Reusing the hash of the tag and key, which the caps assume | 4 | 0.9 | 3,331 | 15 / 9 / 6 / 3 | 830 / 1,470 / 1,790 / 2,130 | 0 / 0 / 1 / 210 |
| Trying both epoch nonces as well | 3 | 0.68 | 4,441 | 11.3 / 6.8 / 4.5 / 2.3 | 1,160 / 1,630 / 1,880 / 2,150 | 0 / 0 / 26 / 250 |
| A tree over 10 recent blocks as well | 2.55 | 0.57 | 5,224 | 9.6 / 5.7 / 3.8 / 1.9 | 1,240 / 1,650 / 1,890 / 2,150 | 0 / 0 / 68 / 260 |

All the other figures of this RFC take 4 permutations.

## The claim value

The reward per claim hardly changes how many nodes reach a stake. A board's income decides that, and with outsiders the cost of a board does. So the runs below move the cap with the reward, and hold a board's income at the minimum work at about 3,330 LOGOS a month. That keeps the onboarding times. All of this is at 100 newcomers a month.

| Reward, LOGOS | Claims per block | Days per claim on a board, at the minimum work | Days per claim on a board, at $0.05 and $4.08 | Chance of a claim in a month, at $0.05 and $4.08 | Liquid part at 90-10 pays a claim's fee up to | Fee at 6.7 times / 31 times the starting price, as a share of the reward |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 9.35 | 0.09 | 3.7 | 100% | 3 times | 20% / 91% |
| 20 | 4.68 | 0.18 | 7.4 | 98% | 7 times | 10% / 45% |
| 50 | 1.87 | 0.45 | 18 | 80% | 17 times | 3.9% / 18% |
| 75 | 1.25 | 0.68 | 28 | 66% | 26 times | 2.6% / 12% |
| 100 | 0.935 | 0.9 | 37 | 56% | 34 times | 2.0% / 9.1% |
| 150 | 0.62 | 1.35 | 55 | 42% | 51 times | 1.3% / 6.0% |
| 200 | 0.47 | 1.8 | 74 | 34% | 68 times | 1.0% / 4.5% |
| 334 | 0.28 | 3 | 123 | 22% | 114 times | 0.6% / 2.7% |
| 500 | 0.19 | 4.5 | 184 | 15% | 171 times | 0.4% / 1.8% |

| Reward, LOGOS | Claims for a stake of 50,000 / 30,000 / 20,000 / 10,000 | Spread at 50,000 / 10,000 | Notes with both parts at 50,000 / 10,000, as a share of the 3,783 a declaration holds | Declaration fee at 6.7 times, as a share of a stake of 10,000 | Claims over the period, GB / million notes | Swing of the target |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 5,000 / 3,000 / 2,000 / 1,000 | ±1.4% / ±3.2% | 264% / 53% | 4.4% | 7.2 / 39.6 | 2.4% |
| 20 | 2,500 / 1,500 / 1,000 / 500 | ±2.0% / ±4.5% | 132% / 26% | 2.2% | 3.6 / 19.8 | 2.3% |
| 50 | 1,000 / 600 / 400 / 200 | ±3.2% / ±7.1% | 53% / 11% | 0.9% | 1.4 / 7.9 | 2.9% |
| 75 | 667 / 400 / 267 / 134 | ±3.9% / ±8.6% | 35% / 7% | 0.6% | 1.0 / 5.3 | 3.0% |
| 100 | 500 / 300 / 200 / 100 | ±4.5% / ±10% | 26% / 5% | 0.5% | 0.7 / 4.0 | 3.2% |
| 150 | 334 / 200 / 134 / 67 | ±5.5% / ±12% | 18% / 4% | 0.3% | 0.5 / 2.6 | 3.4% |
| 200 | 250 / 150 / 100 / 50 | ±6.3% / ±14% | 13% / 3% | 0.2% | 0.4 / 2.0 | 3.8% |
| 334 | 150 / 90 / 60 / 30 | ±8.2% / ±18% | 8% / 2% | 0.2% | 0.2 / 1.2 | 4.4% |
| 500 | 100 / 60 / 40 / 20 | ±10% / ±22% | 5% / 1% | 0.1% | 0.1 / 0.8 | 5.5% |

| Reward, LOGOS | Nodes at 50,000 / 30,000 / 20,000 / 10,000, no outsiders | The same, with claims only while the liquid part pays the fee | Epochs without such claims | Nodes at $0.05 and $4.08 | Nodes at $0.05 and $21.33 |
| --- | --- | --- | --- | --- | --- |
| 10 | 0 / 270 / 720 / 1,280 | 0 / 540 / 1,190 / 1,820 | 41 | 0 / 0 / 0 / 160 | 0 / 0 / 0 / 320 |
| 20 | 250 / 1,000 / 1,430 / 1,910 | 0 / 550 / 1,170 / 1,820 | 36 | 0 / 0 / 0 / 190 | 0 / 0 / 48 / 370 |
| 50 | 700 / 1,370 / 1,720 / 2,080 | 290 / 930 / 1,260 / 1,820 | 21 | 0 / 0 / 0 / 210 | 0 / 0 / 83 / 400 |
| 75 | 780 / 1,440 / 1,770 / 2,110 | 620 / 1,260 / 1,590 / 1,920 | 8 | 0 / 0 / 0 / 220 | 0 / 0 / 87 / 410 |
| 100 | 830 / 1,470 / 1,790 / 2,130 | 830 / 1,470 / 1,790 / 2,130 | 0 | 0 / 0 / 1 / 210 | 0 / 0 / 90 / 410 |
| 150 | 880 / 1,500 / 1,820 / 2,140 | 880 / 1,500 / 1,820 / 2,140 | 0 | 0 / 0 / 1 / 220 | 0 / 0 / 94 / 430 |
| 200 | 900 / 1,520 / 1,830 / 2,150 | 900 / 1,520 / 1,830 / 2,150 | 0 | 0 / 0 / 1 / 220 | 0 / 0 / 100 / 430 |
| 334 | 920 / 1,530 / 1,840 / 2,160 | 920 / 1,530 / 1,840 / 2,160 | 0 | 0 / 0 / 3 / 210 | 0 / 0 / 96 / 440 |
| 500 | 930 / 1,540 / 1,840 / 2,150 | 930 / 1,540 / 1,840 / 2,150 | 0 | 0 / 0 / 8 / 200 | 0 / 1 / 100 / 450 |

The checks bound the reward from both sides:

- A claim pays its fee. A load of claims alone takes the storage price to about 31 times its start, and to 32 in some runs, a fee of up to 9.3 LOGOS, so the liquid part at 90-10 needs a reward of at least 93 LOGOS. Below that, newcomers with nothing cannot claim for part of the period.
- A stake fits one declaration. With both parts staked, a stake of 50,000 needs a reward of at least 27 LOGOS.
- Onboarding is predictable. A spread of at most ±20% needs at most `S / 25`, which is 400 LOGOS at a stake of 10,000.

So the reward can be from 93 to 400 LOGOS. Inside that range a lower reward is better on four counts, and this RFC takes the lowest round value, 100 LOGOS:

- A board finds a claim sooner. At $0.05 and $4.08 that is every 37 days against 123 at 334 LOGOS, so a newcomer has a 56% chance of its first tokens within a month, against 22%. This matters most for what proof of work is for, a participant that holds nothing.
- The time to a stake is more predictable, ±10% against ±18% at a stake of 10,000.
- A spend hides among more claims, about 20,000 an epoch against about 6,000.
- The target is steadier, with a swing of 3.2% against 4.4%.

It costs little. A declaration of a stake of 50,000 takes 26% of what one can hold, against 8%, and its fee is 0.4% of the stake, against 0.1%. Claims take 0.7 GB over the period, against 0.2 GB, and 0.7% of the 130 transactions a block. With no outsiders, fees take up to 9.3% of the reward, so the nodes at a stake of 50,000 fall from 920 to 830. With outsiders the counts do not change beyond noise. The liquid part pays a claim's fee up to 34 times the starting price, against 114.

## The difficulty controller

The review of the retarget found three problems, all of which grow as the claim rate falls.

**A target of 10 claims per block does nothing at 100 LOGOS.** That rate empties the pool in about 9 epochs. Income per board stays at the minimum work's level up to about 26,000 boards, so it does not fall toward the cost of a VPS, and outside hash rate races to empty the pool. With outsiders at $0.05 and a rent of $4.08, and 100 newcomers a month:

| Outside boards grow per epoch | Target 10: pool empty at epoch | Target 10: nodes at 50,000 / 30,000 / 20,000 / 10,000 | Paced target: nodes at those stakes | Paced target: pool left at epoch 98 |
| --- | --- | --- | --- | --- |
| 5% | 88 | 580 / 1,200 / 1,530 / 1,860 | 280 / 900 / 1,210 / 1,590 | 60M |
| 10% | 55 | 0 / 420 / 730 / 1,040 | 0 / 140 / 450 / 770 | 40M |
| 25% | 29 | 0 / 0 / 100 / 400 | 0 / 0 / 1 / 210 | 21M |
| 50% | 20 | 0 / 0 / 0 / 120 | 0 / 0 / 0 / 23 | 13M |

The paced target's gain here is the pool, not the node count. A target of 10 onboards more nodes at every growth rate, since a newcomer keeps the income of the minimum work until the pool is empty. A newcomer that arrives after the pool is empty earns nothing.

**Smoothing of 9/10 is too fast.** The target rises about 11% on an empty block, and about half of all blocks are empty at 0.935 claims per block. Simulated block by block at that target, saturated, with geometric gaps between blocks:

| Smoothing | Rate above target | Swing of the target (standard deviation of its log) | Tickets rejected after a delay of 10 blocks | Gain from holding a near miss for the window | Income per hash of a hopper at 18 times the target, against a steady miner | Payout under that hopper | Time to follow a flood of 50 times | Time back to the cap after a flood of 5 times |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9/10 | +11% | 32% | 16% | +28% | 1.46 times | 1.33 times the target | 8 minutes | 13 minutes |
| 99/100 | +1.0% | 10% | 2.2% | +2.8% | 1.10 times | 1.03 times the target | 104 minutes | 2.6 hours |
| 999/1000 | +0.1% | 3.2% | 0.23% | +0.3% | 1.00 times | 1.01 times the target | 20 hours | 29 hours |

The time to follow runs until the target is within 10% of its new level, and the time back until it is within 10% of the cap. Rejected tickets are weighted by the rate at which they are found. A claim travels through Blend, so a miner holds a ticket found against one target and it is checked against a later one. A hopper mines only while the target is easy, so a faster controller pays it more. The hopper in the table is not the best one: at 1,800 times the target and a low duty, a hopper gets up to about 3.0, 1.8 and 1.4 times per hash. The same smoothing also helps after the period. At 2.06 claims per block, 9/10 swings the target by 27% and rejects about 12% of claims after that delay, and 999/1000 swings it by 2.9% and rejects 0.15%.

The cost of 999/1000 is its slow response, and it is small. Before the target catches up with a sudden flood of 50 times, the flood takes about 3,600 extra claims, about 360k LOGOS, 0.2% of the pool.

**The rule cannot express a target below 1.** `TARGET_CLAIMS_PER_BLOCK` is an integer. A fraction put straight into the rule would also hit the floor of `demand` below about 0.1 claims per block, and tighten the target on every block, even an empty one.

The revision has four parts:

- During the period, the target is the rate that pays out `POW_REWARD_POOL_GENESIS` over `POW_BOOTSTRAP_EPOCHS + 1` epochs at `POW_BOOTSTRAP_REWARD`. It is derived from those three values and needs no new constant. The retarget works with it as a fraction, so the floor of `demand` no longer binds.
- After the period, the same rule reads what the pool holds in place of its seed, and the reward of the epoch, as [After epoch 98](#after-epoch-98) explains.
- `EMA_SMOOTHING_FACTOR / EMA_SMOOTHING_PRECISION` becomes 999/1000, and `REWARD_TARGET_FLOOR` follows at 999.
- Each period has its own cap. After the period the cap is `p // (3 * 2**27)` instead of `p // 2**26`, so a board finds a claim about every 2.7 hours, about 270 rewards a month. Above 0.42 times the starting storage price that is above the rent of $4.08 at $0.05, so the target holds outsiders at nearly every price, as during the period.

The paced target has a cost when many real newcomers arrive at once, because it shares the payout among them. Nodes by epoch 98 with no outsiders, as stop / keep mining:

| Newcomers a month | Stake 20,000, target 10 | Stake 20,000, paced | Stake 10,000, target 10 | Stake 10,000, paced |
| --- | --- | --- | --- | --- |
| 100 | 1,840 / 1,800 | 1,840 / 1,790 | 2,160 / 2,130 | 2,160 / 2,130 |
| 200 | 3,680 / 3,580 | 3,680 / 2,910 | 4,310 / 4,250 | 4,310 / 3,780 |
| 500 | 8,140 / 4,600 | 5,680 / 3,490 | 10,780 / 6,170 | 10,780 / 6,520 |
| 1,000 | 6,690 / 4,780 | 2,090 / 1,960 | 18,080 / 7,840 | 13,170 / 7,060 |
| 2,000 | 3,600 / 3,250 | 0 / 0 | 16,560 / 9,330 | 4,710 / 4,170 |

The same at stakes of 50,000 and 30,000:

| Newcomers a month | Stake 50,000, target 10 | Stake 50,000, paced | Stake 30,000, target 10 | Stake 30,000, paced |
| --- | --- | --- | --- | --- |
| 100 | 860 / 830 | 860 / 830 | 1,520 / 1,470 | 1,520 / 1,470 |
| 200 | 1,700 / 1,640 | 1,140 / 980 | 3,040 / 2,940 | 3,040 / 2,240 |
| 500 | 140 / 140 | 0 / 0 | 4,090 / 3,070 | 1,960 / 1,760 |
| 1,000 | 0 / 0 | 0 / 0 | 1,900 / 1,740 | 4 / 4 |
| 2,000 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 |

A faster pace reduces this cost and empties the pool sooner. Outsiders here are at $0.05 and a rent of $4.08, growing 25% an epoch, with 100 newcomers a month:

| Pace, times the rate that pays out the seed over 99 epochs | Pool empty at epoch, with outsiders | Nodes with outsiders, 50,000 / 30,000 / 20,000 / 10,000 | Nodes at 1,000 newcomers a month with no outsiders, stake 20,000, stop / keep mining |
| --- | --- | --- | --- |
| 1 | never | 0 / 0 / 1 / 210 | 2,090 / 1,960 |
| 1.5 | 77 | 0 / 0 / 1 / 250 | 4,090 / 3,440 |
| 2 | 62 | 0 / 0 / 7 / 270 | 5,490 / 4,150 |
| 3 | 47 | 0 / 0 / 17 / 310 | 6,690 / 4,700 |
| target 10, 11 | 29 | 0 / 0 / 100 / 400 | 6,690 / 4,780 |

This RFC uses a pace of 1. It is the one case where the pool lasts the period, which is what a two-year period means. A late newcomer therefore still earns, 82 LOGOS a month at $0.05, and the target holds a board's income at the cost of hash rate for all of that time. A pace of 1 onboards the fewest nodes. With outsiders a target of 10 gives 0 / 0 / 100 / 400 against 0 / 0 / 1 / 210, since those nodes are the early arrivals. Without outsiders a faster pace gives more at high arrival rates. At or below about 100 newcomers a month, with one claim every 21.6 hours and no outsiders, the paced target and a target of 10 agree.

The pace is one epoch slower than the period, so that the pool keeps about 1% of its seed as a margin. The retarget overshoots its target by about 0.1%, a flood at launch takes about 3,600 extra claims before the target catches up, and a miner that hops in and out adds a little more. At a pace over 98 epochs, a chain at the target from the first block would empty the pool at about epoch 97.9, and claims would then fail until epoch 98. What the period leaves at $0.05 and $4.08:

| How outsiders arrive | Pool left at epoch 98 |
| --- | --- |
| No outsiders | 99.6M |
| 5% growth an epoch from 100 boards | 59.7M |
| 25% growth an epoch from 100 boards | 21.0M |
| 25% growth an epoch from 1,000 boards | 5.8M |
| At the target boards within the first epoch | 3.9M |
| 100,000 boards from the first block, block by block | 1.56M |
| 1,000,000 boards from the first block, block by block | 1.32M |
| A hopper at 18 times the target and steady miners at 2 times, block by block | 1.48M |

The last three rows run the reference code over all 98 epochs, and in none of them does a claim find the pool short.

## Stakes, onboarding times and nodes

These tables compare other minimum works, for the record, and have no outsiders. Each cell of the first gives the income per board per month that a stake and onboarding time need, and the days per claim at 100 LOGOS. The minimum work scales with the days per claim. A stake of 50,000 in 1 month needs about $`2^{27.7}`$ claim tickets per claim, and a stake of 10,000 in 6 months about $`2^{32.6}`$.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 50,000, 0.06 days | 30,000, 0.1 days | 20,000, 0.15 days | 10,000, 0.3 days |
| 2 | 25,000, 0.12 days | 15,000, 0.2 days | 10,000, 0.3 days | 5,000, 0.6 days |
| 3 | 16,667, 0.18 days | 10,000, 0.3 days | 6,667, 0.45 days | 3,333, 0.9 days |
| 4 | 12,500, 0.24 days | 7,500, 0.4 days | 5,000, 0.6 days | 2,500, 1.2 days |
| 5 | 10,000, 0.3 days | 6,000, 0.5 days | 4,000, 0.75 days | 2,000, 1.5 days |
| 6 | 8,333, 0.36 days | 5,000, 0.6 days | 3,333, 0.9 days | 1,667, 1.8 days |

At 100 LOGOS per claim:

| Stake | Stakes the pool can pay | Claims per stake | Spread of onboarding time | Declaration of all its claim notes |
| --- | --- | --- | --- | --- |
| 50,000 | 4,000 | 500 | ±4.5% | 1,000 notes, 41.1 KB, 26.6% of `G_max`, 32.9 LOGOS |
| 30,000 | 6,667 | 300 | ±5.8% | 600 notes, 24.9 KB, 16.1% of `G_max`, 19.9 LOGOS |
| 20,000 | 10,000 | 200 | ±7.1% | 400 notes, 16.7 KB, 10.8% of `G_max`, 13.4 LOGOS |
| 10,000 | 20,000 | 100 | ±10% | 200 notes, 8.7 KB, 5.5% of `G_max`, 6.9 LOGOS |

The spread is the Poisson spread of a node's claim count. The declaration uses the last value of `G_max`, 3,173,691, and the starting storage price.

With no outsiders the counts follow closed forms, where `B = 24.5` months and `O` is the months of mining. Of the 85 cells with at least 500 nodes at 100 to 1,000 newcomers a month, the keep mining form is within 3% of the runs in 80 and within 8% in all.

```python
R = 8.09e6    # LOGOS per month at the target

# Miners stop. The target does not bind while newcomers finish as fast as they arrive.
stop = a * (B - O)    # while a <= R / S

# Miners keep mining. Boards reach the target once a * t = R * O / S.
keep = a * (B - O) if a * B <= R * O / S else a * B * exp(-a * S / R)
```

Nodes onboarded by epoch 98, as stop / keep mining. At 100 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 2,360 / 1,320 | 2,360 / 1,690 | 2,360 / 1,920 | 2,360 / 2,160 |
| 2 | 2,260 / 1,310 | 2,260 / 1,680 | 2,260 / 1,910 | 2,260 / 2,150 |
| 3 | 2,160 / 1,310 | 2,160 / 1,680 | 2,160 / 1,890 | 2,150 / 2,130 |
| 4 | 2,060 / 1,300 | 2,060 / 1,670 | 2,050 / 1,890 | 2,050 / 2,020 |
| 5 | 1,950 / 1,300 | 1,950 / 1,660 | 1,950 / 1,870 | 1,950 / 1,910 |
| 6 | 1,850 / 1,290 | 1,840 / 1,650 | 1,840 / 1,800 | 1,840 / 1,800 |

At 500 newcomers a month:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 610 / 550 | 2,860 / 1,920 | 7,180 / 3,560 | 11,810 / 6,600 |
| 2 | 580 / 550 | 2,740 / 1,910 | 6,960 / 3,560 | 11,300 / 6,570 |
| 3 | 570 / 540 | 2,620 / 1,900 | 6,630 / 3,530 | 10,790 / 6,530 |
| 4 | 560 / 530 | 2,470 / 1,900 | 6,300 / 3,510 | 10,260 / 6,490 |
| 5 | 500 / 480 | 2,330 / 1,880 | 6,000 / 3,490 | 9,740 / 6,490 |
| 6 | 420 / 410 | 2,230 / 1,890 | 5,690 / 3,490 | 9,190 / 6,450 |

At the steady rate that gives the most nodes, swept for each cell:

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 3,480 / 1,460 | 5,740 / 2,420 | 8,530 / 3,620 | 17,090 / 7,290 |
| 2 | 3,390 / 1,460 | 5,650 / 2,420 | 8,300 / 3,620 | 16,520 / 7,220 |
| 3 | 3,240 / 1,440 | 5,390 / 2,400 | 8,060 / 3,590 | 15,990 / 7,220 |
| 4 | 3,080 / 1,440 | 5,130 / 2,390 | 7,720 / 3,580 | 15,420 / 7,120 |
| 5 | 2,930 / 1,430 | 4,860 / 2,380 | 7,340 / 3,580 | 14,520 / 7,160 |
| 6 | 2,770 / 1,430 | 4,600 / 2,360 | 6,930 / 3,550 | 13,830 / 7,120 |

Miners that stop can onboard 69% to 87% of the stakes the pool can pay. Miners that keep mining can onboard about 36% of them, close to `capacity / e`, whatever the onboarding time, at `a = R / S`.

## Ranges that work

These checks decide whether a combination works. The limits of ±20% and 10% are choices this RFC makes.

| Check | Rule | Result at 100 LOGOS |
| --- | --- | --- |
| A stake fits one declaration | at most 3,783 notes | every stake and split, counting a stake of vested notes alone: at most 1,667 notes |
| A claim pays its fee | the liquid part exceeds the fee at the highest storage price | every split, see [The vested-liquid split](#the-vested-liquid-split) |
| Fees stay small | the fee is at most 10% of the reward | every run: the price peaks at up to 32 times its start, a fee of up to 9.3 LOGOS, 9.3% of the reward |
| Onboarding is predictable | a spread of at most ±20%, so at least 25 claims per stake | every stake: at most ±10% |
| The activity proof holds | at most 8,191 providers | miners that keep mining stay below it in every run without outsiders; miners that stop pass it at stakes of 20,000 and 10,000 at high arrival rates; at $0.05 service rewards support more than this at every stake, below |
| The onboarding time holds | it holds for every newcomer until epoch 98, with nobody stopping and no outsiders | depends on the income per board, below |
| Income does not pay rent | a board's whole income at the minimum work stays below the rent at $0.05 | no stake and onboarding time passes, below |
| Liquid income does not pay rent | the liquid part stays below the rent at $0.05, which keeps out a miner that counts only its liquid income | no stake and onboarding time passes at any split, below |
| One operator's share | what one operator pays to fill the 8,191 providers | $4.0M at a stake of 10,000 to $20.5M at 50,000, below; this RFC sets no limit |

The onboarding time holds while a board's income per month is at most `R / (a * B)`: 6,604 LOGOS at 50 newcomers a month, 3,302 at 100 and 1,651 at 200. Each cell gives the most newcomers a month for which it holds. If miners stop, it holds up to `R / S`: 162, 270, 404 and 809 a month at the four stakes.

| Months of mining | Stake 50,000 | Stake 30,000 | Stake 20,000 | Stake 10,000 |
| --- | --- | --- | --- | --- |
| 1 | 6 | 11 | 16 | 33 |
| 2 | 13 | 22 | 33 | 66 |
| 3 | 19 | 33 | 49 | 99 |
| 4 | 26 | 44 | 66 | 132 |
| 5 | 33 | 55 | 82 | 165 |
| 6 | 39 | 66 | 99 | 198 |

With about 100 newcomers a month as the reference, an assumption of this RFC:

| Stake | Months of mining at which the onboarding time holds | Nodes by epoch 98, miners keep mining | Most nodes, miners stop / keep mining |
| --- | --- | --- | --- |
| 50,000 | from 15, none up to 6 | 1,290 | 2,770 to 3,480 / about 1,440 |
| 30,000 | from 9, none up to 6 | 1,650 | 4,600 to 5,740 / about 2,400 |
| 20,000 | 6 | 1,800 | 6,930 to 8,530 / about 3,590 |
| 10,000 | 3 to 6 | 1,800 to 2,130 | 13,830 to 17,090 / about 7,190 |

The income of one claim every 21.6 hours is the highest that passes the onboarding check at about 100 newcomers a month: a stake of 20,000 at 6 months, or a stake of 10,000 at 3 months. It holds up to 99 a month, so at 100 it misses by 1% in the last month. In those cells stop and keep mining agree within about 2.5%, so no rule is needed to make miners stop.

No stake and onboarding time in these tables passes the two rent checks at $0.05. The check on the whole income needs at most 82 LOGOS a month, which puts a stake of 10,000 at 122.5 months. The check on the liquid part at 90-10 needs at most 816 LOGOS a month, which puts it at 12.3 months. The minimum work therefore cannot keep outsiders out at $0.05. The target does that, at the cost in nodes below.

Each stake at $0.05, with one claim every 21.6 hours and 100 newcomers a month. Outsiders start from 100 boards unless the column says otherwise.

| Stake | Cost at $0.05 | Months on one board, no outsiders / outsiders at $4.08 | Nodes, no outsiders | Nodes, outsiders at $4.08 | Nodes, from 10 boards | Nodes, from 1,000 boards | Nodes, outsiders at $21.33 | Nodes, owned hash at $1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50,000 | $2,500 | 15 / 612.7 | 830 | 0 | 0 | 0 | 0 | 0 |
| 30,000 | $1,500 | 9 / 367.6 | 1,470 | 0 | 0 | 0 | 0 | 0 |
| 20,000 | $1,000 | 6 / 245.1 | 1,790 | 1 | 140 | 0 | 90 | 0 |
| 10,000 | $500 | 3 / 122.5 | 2,130 | 210 | 450 | 2 | 410 | 190 |

With outsiders at $4.08 at their full count from the second epoch, no stake onboards anyone. A stake can still be bought at the same price it costs to mine, so these counts measure the route through one board, and not how many providers can exist.

Service rewards decide that, and one operator can take them. `Providers supported` is the count at which service rewards pay for a $6.12 machine and 10% a year on the stake, `4.93M * p / (6.12 + 0.1 * S * p / 12)`. The return is what a provider earns on its stake at $0.05 with 8,191 providers: 602 LOGOS a month, $30.09, less the $6.12 machine.

| Stake | Providers supported at $0.01 / $0.05 / $0.10 | Return a year on the stake | Stakes outsiders mine | Identities one operator needs to reach 8,191 providers | What they cost at $0.05 |
| --- | --- | --- | --- | --- | --- |
| 50,000 | 4,793 / 9,145 / 10,317 | 12% | 3,462 | 8,191 | $20.5M |
| 30,000 | 5,719 / 13,238 / 15,842 | 19% | 5,770 | 8,191 | $12.3M |
| 20,000 | 6,331 / 17,055 / 21,635 | 29% | 8,656 | 8,190 | $8.2M |
| 10,000 | 7,090 / 23,963 / 34,110 | 58% | 17,311 | 7,977 | $4.0M |

- At $0.05 every stake supports more providers than the 8,191 at which the activity proof starts failing by chance. So that proof has to change first, whichever stake is chosen.
- A lower stake makes identities cheaper. Outsiders mine enough to fill the 8,191 at 20,000 and 10,000. At 30,000 and 50,000 an operator would buy the rest.
- The lottery does not depend on the stake. What outsiders mine is about 37% of it at any stake, against an assumed 300M LOGOS of other active stake.

## The vested-liquid split

A node that stakes both parts of its claims needs the same claims at every split, so the node counts above hold for all four splits when no outsiders mine, and at patience 1 when they do. The split changes what a node can do with its liquid part, and how much of the pool can reach the market at once.

| Vested-liquid | Per claim, vested / liquid, LOGOS | Liquid part ÷ claim fee, at the start / at 31 times | Time to a stake of vested notes alone | Notes for that stake, at 50,000 / 30,000 / 20,000 / 10,000 | Liquid share of the 200M |
| --- | --- | --- | --- | --- | --- |
| 30-70 | 30 / 70 | 240 / 7.7 | 3.3 × `O` | 1,667 / 1,000 / 667 / 334 | 140M |
| 50-50 | 50 / 50 | 171 / 5.5 | 2 × `O` | 1,000 / 600 / 400 / 200 | 100M |
| 70-30 | 70 / 30 | 103 / 3.3 | 1.4 × `O` | 715 / 429 / 286 / 143 | 60M |
| 90-10 | 90 / 10 | 34 / 1.1 | 1.1 × `O` | 556 / 334 / 223 / 112 | 20M |

A node that sells its liquid part and stakes vested notes alone needs longer. At one claim every 21.6 hours, as stop / keep mining:

| Vested-liquid | Stake 20,000: time | At 100 a month | At 500 a month | Stake 10,000: time | At 100 a month | At 500 a month |
| --- | --- | --- | --- | --- | --- | --- |
| 30-70 | 20 months | 400 / 390 | 0 / 0 | 10 months | 1,440 / 1,430 | 1,440 / 1,340 |
| 50-50 | 12 months | 1,250 / 1,230 | 370 / 350 | 6 months | 1,860 / 1,850 | 5,970 / 3,580 |
| 70-30 | 8.6 months | 1,600 / 1,590 | 2,370 / 2,070 | 4.3 months | 2,020 / 2,030 | 10,160 / 5,070 |
| 90-10 | 6.7 months | 1,790 / 1,790 | 4,620 / 3,130 | 3.3 months | 2,130 / 2,120 | 10,630 / 6,180 |

The same at stakes of 50,000 and 30,000:

| Vested-liquid | Stake 50,000: time | At 100 a month | At 500 a month | Stake 30,000: time | At 100 a month | At 500 a month |
| --- | --- | --- | --- | --- | --- | --- |
| 30-70 | 50 months | 0 / 0 | 0 / 0 | 30 months | 0 / 0 | 0 / 0 |
| 50-50 | 30 months | 0 / 0 | 0 / 0 | 18 months | 630 / 630 | 0 / 0 |
| 70-30 | 21.4 months | 290 / 290 | 0 / 0 | 12.9 months | 1,160 / 1,150 | 81 / 85 |
| 90-10 | 16.7 months | 780 / 770 | 0 / 0 | 10 months | 1,450 / 1,450 | 1,460 / 1,350 |

At 90-10 a stake forms from vested notes alone in about the same time, and the node keeps its liquid part for fees. The liquid part still pays a claim's fee up to 34 times the starting storage price. While no outsiders mine, the liquid part of 333 LOGOS a month, $16.65 at $0.05, pays for a rented machine or for the electricity of a Raspberry Pi 5 at home. Once outsiders bring the income to 82 LOGOS a month, the liquid part falls to $0.41, and a node pays for its machine from other funds.

## Stopping

No rule can make a node stop, because every claim pays a fresh key. Service rewards of 4.93M / `N` LOGOS a month exceed a board's 3,331 LOGOS below about 1,500 providers, and its 82 LOGOS at $0.05 and $4.08 below about 60,000. But Blend uses at most one of a board's four cores, so a provider can also keep mining on the others. Stop is therefore an upper bound on the count, and keep mining the expected case.

More providers are not always better. Service rewards still cover a $6.12 machine at $0.05 up to about 40,000 providers, so at this price the activity proof sets the limit. On cover traffic alone it fails by chance under 0.05% of the time up to 8,191 providers, 6.6% at 8,192 and 11% at 10,000, and data traffic lowers these. With `inactivity_period` at 2, a failed proof costs a locked provider epochs until its lock ends. At 6.6% about 27% of locked providers are out for good within a year, and at 11% about 57%. The pool can pay for 10,000 stakes of 20,000 and 20,000 stakes of 10,000, more than that limit, and for 6,667 of 30,000 and 4,000 of 50,000, fewer.

## After epoch 98

After the period the reward only has to pay for a transaction, and every reward vests at 30-70. An average transaction here holds a claim, the Transfer that spends its liquid note and an inscription of 100 bytes:

| Part | Bytes |
| --- | --- |
| Operation count | 1 |
| Claim, with an empty proof | 129 |
| Transfer of one input and one output, with its proof | 235 |
| Inscription of 100 bytes, with its signature | 267 |
| Total | 632 |

A fixed reward cannot keep paying for it. [Storage Markets](../storage-markets.md) moves the storage price with growth in usage and not with its level, so the price at epoch 98 depends on how traffic got there. A fixed 1.2 LOGOS would have a liquid part of 0.84 LOGOS, which covers a claim's fee up to 2.88 times the starting price. On the claims of the base case, with other traffic of 300-byte transactions:

| Other traffic | Storage price at epoch 98 | Fee of a claim, LOGOS | A fixed 1.2 LOGOS |
| --- | --- | --- | --- |
| None | 6.60 times | 1.93 | Claims stop for 7 epochs, then flow in about half of all epochs |
| Starts at epoch 98, 1 per block | 6.60 times | 1.93 | The price sticks at 5.77 times, and the liquid part never covers the fee |
| Steady from genesis, 1 per block | 3.05 times | 0.89 | The liquid part falls just short |
| Steady from genesis, 13 per block or more | 1.75 times or less | 0.51 or less | Works |
| Grows from 1 to 13 per block | 18 times | 5.27 | The fee is above the whole reward |
| Grows from 1 to 130 per block | 136 times | 40 | The fee is above the whole reward |
| Grows from 1 per hour to 130 per block | 483 times | 141 | The fee is above the whole reward |

So the reward is set at each epoch boundary, so that its liquid part pays the storage fee of the 632-byte transaction at the price of that epoch:

```python
reward = ceil(632 * permanent_storage_gas_price / 0.7)
```

That is 0.72 LOGOS at the starting price, 4.77 at 6.60 times and 98 at 136 times. A claim transaction alone is 365 bytes, so it always pays its own fee. The Execution Gas of the 632-byte transaction is not counted. It adds about 0.000004 LOGOS at the starting base fee, the storage fee of less than a hundredth of a byte.

A target of 10 claims per block would then drain the pool, at 21M LOGOS an epoch at 136 times. The target is therefore derived too. It is the rule of the period, with what the pool holds in place of its seed, and it needs no new constant:

```python
target = pool / (reward * 99 * 21_600)    # claims per block
```

This pays out a ninety-ninth of the pool per epoch, about 4% a month, at any storage price:

- A higher price means a higher reward and fewer claims, so pushing the price up does not draw the pool faster.
- A smaller pool pays out less, so the pool does not run out.
- Fee shares refill the pool, so in the long run the payout equals the fee share. That is one claim for about every 29 transactions of 300 bytes, at any storage price.

A fixed 10 claims per block empties the pool by epoch 113 with no other traffic, and a fixed payout of 259,200 LOGOS an epoch empties it by epoch 183. With traffic growing from 1 to 130 per block, that fixed payout stays at 0.12 claims per block while the pool grows past 3.8B LOGOS.

The table gives the reward in LOGOS, the claims per block and the pool, on the claims of the base case. The 2,450 boards of the newcomers keep mining, and renters at $0.05 and $4.08 join when it pays.

| Other traffic | At epoch 98 | At epoch 250, about 3 years later | At epoch 497, about 8 years later |
| --- | --- | --- | --- |
| None | 4.77, 2.06, 21.0M | 2.83, 0.79, 4.8M | 0.85, 0.24, 0.4M |
| Steady, 1 per block | 2.20, 4.46, 21.0M | 1.55, 1.47, 4.9M | 0.76, 0.31, 0.5M |
| Steady, 13 per block | 1.26, 8.13, 21.9M | 1.21, 2.32, 6.0M | 1.05, 0.66, 1.5M |
| Steady, 130 per block | 1.18, 12.48, 31.4M | 1.23, 6.23, 16.4M | 1.22, 4.68, 12.1M |
| Grows from 1 to 13 per block | 13.02, 0.85, 23.6M | 12.89, 0.54, 15.0M | 12.79, 0.46, 12.6M |
| Grows from 1 to 130 per block | 98.33, 0.56, 117M | 105.53, 3.57, 805M | 106.35, 4.41, 1,003M |
| Steady, 13 per block, stops at epoch 98 | 1.26, 8.13, 21.9M | 0.51, 4.56, 5.0M | 0.15, 1.37, 0.5M |

Across these runs and the ones with no outsiders, the target stays between 0.2 and 59 claims per block. At 0.2 the smoothing of 999/1000 overshoots it by about 0.3%, and at 0.01 it would overshoot by 5%.

At `REWARD_TARGET_CAP` a board finds a claim about every 2.7 hours, and a participant with nothing can pay for its first transaction after its first claim. At the target it waits longer. At $0.05 and $4.08 renters join until a board earns 82 LOGOS a month, about 10,400 boards at 2.06 claims per block, and a board then finds a claim about every 42 hours.

The change at epoch 98 is abrupt:

- A newcomer short of its stake at epoch 98 then shares about 4% of the pool a month instead of 8.09M LOGOS, about 850k LOGOS at 21.0M. So it finishes by other means or not at all. At a stake of 20,000, that is any newcomer arriving in the last 6 months of the period, and in the base case nearly every newcomer.
- Claims do not stop. At 6.60 times the liquid part of 3.34 LOGOS pays the fee of 1.93 LOGOS. Claims rise from 0.94 to about 1.6 per block, which takes the price to about 8.1 times within 2 epochs, and the reward with it.
- The cap takes about 17 hours to reach its new value.

## Era parameters

`POW_BOOTSTRAP_EPOCHS`, `POW_BOOTSTRAP_REWARD`, `POW_BOOTSTRAP_VESTED_SHARE`, `POW_BOOTSTRAP_TARGET_CAP`, `POW_REFERENCE_TX_SIZE`, `REWARD_TARGET_CAP` and `POW_VESTED_SHARE` are era parameters. Eras specifies the era parameter record, and this branch does not have it, so their fields go into whichever of the two specifications lands second.

## Compatibility

The chain has not launched, so no migration is needed. Claims, their encoding and the circuits do not change.

## Open questions

- **The token price.** All the rent checks depend on it, and this RFC assumes $0.05. Above $0.0012 a board's income at the minimum work exceeds the cheapest rent, and the target then does the work. Above $0.012 its liquid part does too.
- **The minimum stake.** No specification sets it, and this RFC compares 50,000, 30,000, 20,000 and 10,000 without choosing. They are 0.0005% to 0.0001% of the cap. The analysis of the minimum stake gives 0.001% of the supply at launch, which is 100,000 LOGOS if that supply is the cap, and this RFC does not consider that value. That analysis still lists a supply of 100M LOGOS against a cap of 10B. It should change with any value chosen here, and this branch does not change it. A lower stake lets the same pool fund more provider identities, makes an identity cheaper, and holds up better against outside mining.
- **Hash rates and power still to measure.** The rents in this RFC count 1.5 Raspberry Pi 5 cores per vCPU, within a range of 1 to 2, and no rented machine has been measured. The owned machine's power is assumed. No GPU has been measured on any puzzle.
- **The end of the period.** A softer change at epoch 98 could help newcomers partway to a stake. It would add a rule.
- **The pool.** 200M LOGOS is 2% of the supply cap, four times the current seed, and it comes out of the initial distribution.
- **Privacy.** With 100 LOGOS per claim a spend hides among far fewer claims than under the current target of 10 claims per block. At 100 newcomers a month, an epoch holds about 200 claims at launch and about 20,000 at the end if nobody stops. If everybody stops at a stake of 20,000, it holds about 5,000 from month 6 on. After the period the reward differs by epoch, so the value of a spend of vested notes can reveal how many were claimed in each epoch.
- **Storage price.** The price still follows growth in usage and not its level. The derived reward copes with that, and the price itself would need an anchor in its own RFC. During the period the model counts claims as the only storage use, and other traffic changes its path.
- **Fees during the period.** The reward stays fixed during the period, so the liquid part of 10 LOGOS falls short above about 34 times the starting price. With traffic growing from 1 to 130 per block that is from epoch 69, and from 1 per hour to 130 per block it is from epoch 68. A miner then pays the fee from other funds.
- **The reference transaction.** 632 bytes is this RFC's choice of an average transaction, to revise once real sizes are known.
- **Bursts of claims.** A miner can land the tickets of a whole window in one block, since a block's claims lower the target by less than the same claims spread over blocks. Against about 100,000 boards, a burst of 1,000,000 boards earns 1.24 times per hash and lifts the payout by 2%, more than the margin of 1%. Against 2,429 boards, the same burst lifts it by 46%, and the pool lasts 68 epochs. A limit on the claims of a block, or a step of the retarget per claim, would stop this. This RFC adds neither.
- **Vested notes after the period.** A vested note is worth the storage fee of 271 bytes at the price of its epoch, and the Transfer that spends it a year later costs 235 bytes. Above a 15% rise in the price over that year, it is not worth spending alone.
- **The puzzle.** Which puzzle replaces `zkhash` for rewards is not settled. Equi-X has a benchmark, and its author has since deprecated it in favour of HashWX, which has none here.

# Details

## 1. Fixed rewards and vested shares

A claim pays one fixed reward and vested share during the first `POW_BOOTSTRAP_EPOCHS` epochs, the bootstrapping period. After it the liquid part of the reward pays the storage fee of `POW_REFERENCE_TX_SIZE` bytes at the storage price of the epoch. The rule that computed the reward from the pool goes, with `EPOCH_POW_DISTRIBUTION_RATE_NUM` and `EPOCH_POW_DISTRIBUTION_RATE_DEN`.

```diff
+POW_BOOTSTRAP_EPOCHS: uint64 = 98               # the length of the bootstrapping period, in epochs
+POW_BOOTSTRAP_REWARD: TokenValue = 100 * 10**9  # the reward per claim during it, 100 LOGOS, in LEPTA
+POW_BOOTSTRAP_VESTED_SHARE: uint64 = 90         # the share of that reward paid as a vested note
+POW_REFERENCE_TX_SIZE: uint64 = 632             # the bytes whose storage fee the liquid part of a reward pays after it
-POW_VESTED_SHARE: uint64 = 50
+POW_VESTED_SHARE: uint64 = 30                   # the share of a reward paid as a vested note after it
-TARGET_CLAIMS_PER_BLOCK: uint64 = 10

-def compute_epoch_pow_reward(pow_reward_pool: TokenValue) -> TokenValue:
-    # ... a share of the pool, over the target claims of an epoch
+def compute_epoch_pow_reward(epoch: EpochNumber,
+                             permanent_storage_gas_price: TokenValue) -> tuple[TokenValue, uint64]:
+    # The reward per claim, and the share of it paid as a vested note.
+    if epoch < POW_BOOTSTRAP_EPOCHS:
+        return POW_BOOTSTRAP_REWARD, POW_BOOTSTRAP_VESTED_SHARE
+    # Rounded up, so that the liquid part covers the storage fee of POW_REFERENCE_TX_SIZE bytes.
+    fee = POW_REFERENCE_TX_SIZE * permanent_storage_gas_price
+    liquid_share = SHARE_DEN - POW_VESTED_SHARE
+    reward = (fee * SHARE_DEN + liquid_share - 1) // liquid_share
+    return checked_uint64(reward), POW_VESTED_SHARE
```

At each epoch boundary, once the storage price of the new epoch is set, `epoch_pow_reward` and `epoch_pow_vested_share` are set for the new epoch and held for it. A claim still needs the pool to cover the reward, as [CLAIM_POW_REWARD](../bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation requires. Claiming resumes when the fee shares of the blocks bring the pool back to the reward, or at the first epoch boundary that sets a reward the pool covers.

`POW_BOOTSTRAP_EPOCHS` is the number of epochs that first reaches two years, $`\lceil 730 / 7.5 \rceil = 98`$. The constraint that the vested notes of a minimum stake fit one declaration now reads `POW_BOOTSTRAP_REWARD`.

## 2. The difficulty controller

```diff
+POW_BOOTSTRAP_TARGET_CAP: PowTarget = p // (3 * 2**30)
-EMA_SMOOTHING_FACTOR: uint64 = 9
-EMA_SMOOTHING_PRECISION: uint64 = 10
-REWARD_TARGET_FLOOR: uint64 = 9
-REWARD_TARGET_CAP: PowTarget = p // 2**26
+EMA_SMOOTHING_FACTOR: uint64 = 999
+EMA_SMOOTHING_PRECISION: uint64 = 1000
+REWARD_TARGET_FLOOR: uint64 = 999
+REWARD_TARGET_CAP: PowTarget = p // (3 * 2**27)

+def target_claims_per_block(epoch: EpochNumber,
+                            epoch_pow_reward: TokenValue,
+                            pow_reward_pool: TokenValue) -> tuple[int, int]:
+    pool = POW_REWARD_POOL_GENESIS if epoch < POW_BOOTSTRAP_EPOCHS else pow_reward_pool
+    return pool, epoch_pow_reward * (POW_BOOTSTRAP_EPOCHS + 1) * EXPECTED_BLOCKS_PER_EPOCH
+
 def compute_new_reward_difficulty(claims_in_block: uint64,
-                                  current_target: PowTarget) -> PowTarget:
+                                  current_target: PowTarget,
+                                  epoch: EpochNumber,
+                                  epoch_pow_reward: TokenValue,
+                                  pow_reward_pool: TokenValue) -> PowTarget:
-    demand = max(1, (P - F) * claims_in_block + F * TARGET_CLAIMS_PER_BLOCK)
-    new_target = (TARGET_CLAIMS_PER_BLOCK * current_target * P) // demand
-    return min(max(new_target, REWARD_TARGET_FLOOR), REWARD_TARGET_CAP)
+    num, den = target_claims_per_block(epoch, epoch_pow_reward, pow_reward_pool)
+    demand = max(1, (P - F) * claims_in_block * den + F * num)
+    new_target = (num * current_target * P) // demand
+    cap = POW_BOOTSTRAP_TARGET_CAP if epoch < POW_BOOTSTRAP_EPOCHS else REWARD_TARGET_CAP
+    return min(max(new_target, REWARD_TARGET_FLOOR), cap)
```

`epoch` is the epoch of the processed block, and `pow_reward_pool` is the pool once that block's claims and fee share are applied. At genesis `difficulty_reward` is `POW_BOOTSTRAP_TARGET_CAP`. `P` and `F` stand for the two smoothing constants. The product of the retarget stays below $`2^{328}`$, inside the 512 bits [Puzzle Target](../proof-of-work.md#puzzle-target) allows.

Both caps are calibrated against the measurement of `BLEND_DIFFICULTY_BASE`, $`2^{19}`$ hashes in about 38 seconds on one core, each a Blend ticket of 3 permutations, for a claim ticket of 4 permutations. The four cores of the target machine find a claim about every 21.6 hours at `POW_BOOTSTRAP_TARGET_CAP` and about every 2.7 hours at `REWARD_TARGET_CAP`, which is 8 times the target.

## 3. The vested share in Mantle

Validators keep `epoch_pow_vested_share` beside `epoch_pow_reward`, and a claim reads it.

```diff
-vested_value = checked_uint64(epoch_pow_reward * POW_VESTED_SHARE) // SHARE_DEN
+vested_value = checked_uint64(epoch_pow_reward * epoch_pow_vested_share) // SHARE_DEN
```

The check `assert epoch_pow_reward > 0` goes, since `POW_BOOTSTRAP_REWARD` is a positive constant and the storage price never reaches 0.

## 4. The pool seed

`POW_REWARD_POOL_GENESIS` becomes two hundredths of $`S_{cap}`$, 200M LOGOS, instead of five thousandths. Genesis sets `epoch_pow_reward` and `epoch_pow_vested_share` by the same computation.

## Chores

- The Overview of Proof of Work says what a claim pays in each period, and the target rate of each.
- The Notation of Proof of Work drops the distribution rate and `T`.
- Block Rewards says its projected growth leaves out the claims paid from the pool.

# Implementation

- [ ] Land this after the reward puzzle is replaced, and restate the two caps and the retarget for the new puzzle, as [Dependence on the puzzle](#dependence-on-the-puzzle) says.
- [ ] Add the constants of the period and change the shares, the smoothing, the floor and the cap, with the values chosen from [Ranges that work](#ranges-that-work).
- [ ] Set `epoch_pow_reward` and `epoch_pow_vested_share` by epoch at each epoch boundary and at genesis, after the storage price of the new epoch, and remove the reward computed from the pool.
- [ ] Apply the target and the cap by the epoch of the processed block, reading the reward of the epoch and the pool after that block, and start `difficulty_reward` at `POW_BOOTSTRAP_TARGET_CAP`.
- [ ] Read `epoch_pow_vested_share` in `CLAIM_POW_REWARD`.
- [ ] Seed the pow reward pool with two hundredths of the supply cap.
- [ ] Measure the claims per epoch of a Raspberry Pi 5 at both caps with real claim tickets, the hash rate of a rented vCPU and of a GPU, and the power of an owned desktop.
- [ ] Add the seven constants to the era parameter record once Eras and this change are on one branch.
- [ ] Revise `POW_REFERENCE_TX_SIZE` once real transaction sizes are known.
- [ ] Add tests: the reward and share at epochs 97 and 98, the reward at the lowest and at a high storage price with its liquid part covering `POW_REFERENCE_TX_SIZE` bytes, a claim against a pool below the reward, the retarget at the cap in both periods, a block with claims at the fractional target, the target at a small pool, the genesis values.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.4.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.5.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.4.0 |
| [Block Rewards](../block-rewards.md) | Modified | Revision 1.4.1 |
