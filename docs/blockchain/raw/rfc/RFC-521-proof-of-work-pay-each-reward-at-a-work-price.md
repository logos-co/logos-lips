# [RFC] Proof of Work: Pay each reward at a work price

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
| v11 | The reward puzzle is HashWX. The two caps follow its measured rate, and a claim transaction falls to 341 bytes and the reference transaction to 608 | 2026-11-10 |
| v12 | Rebuilt from first principles: no bootstrapping period. A reward pays for the gas it carries, vests 90% for a year and takes at least `WORK_PER_LEPTA` hashes per LEPTON. The threshold keeps steering toward `TARGET_CLAIMS_PER_BLOCK`, raised to 12, with no payout limit | 2026-11-27 |
| v13 | `VESTING_EPOCHS` is the number of epochs that first reaches a year, so the vesting follows the epoch length: 49 epochs of 7.5 days, 146 of 60 hours. The change lands after the epoch is shortened to 60 hours | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Proof of Work](#affected-specifications), [the work floor](#2-the-work-floor) | `WORK_PER_LEPTA` and its derivation; the cap scales with the reward, so every token costs the same work |
| 2 | Critical | [Proof of Work](#affected-specifications), [the reward](#1-the-reward) | the liquid part pays the storage fee of a claim and of one reference transaction; `POW_VESTED_SHARE` rises from 50 to 90; `VESTING_EPOCHS` follows the epoch length |
| 3 | High | [Proof of Work](#affected-specifications), [the claim limit](#3-the-claim-limit) | the threshold steers toward `TARGET_CLAIMS_PER_BLOCK`, raised from 10 to 12, under the new cap; a block holds at most `MAX_CLAIMS_FACTOR` times the target |
| 4 | High | [Mantle](#affected-specifications), [the claim limit](#4-the-claim-limit-in-mantle) | `claims_before < MAX_CLAIMS_FACTOR * TARGET_CLAIMS_PER_BLOCK`; the check that the reward is positive goes |
| 5 | Medium | [Genesis Block](#affected-specifications), [the pool seed](#5-the-pool-seed) | 200M LOGOS; `epoch_pow_reward` at the initial storage price |

# Discussion

## The design

Proof of work spreads stake and gives access to participants who hold nothing. This revision sets every value from six principles. When two conflict, principles 2 to 4 come first, then 5, then 6.

1. **Purpose.** Spread stake and give access. Success is how widely the stake spreads. Reaching the minimum stake is not a goal.
2. **Little effect on the price.** Most of each reward vests, and only the part that pays for gas is liquid.
3. **Buying hash rate just to mine does not pay,** at home or in a data centre, at any token price up to $0.05.
4. **Privacy.** Mining and claiming reveal no more than an ordinary transaction.
5. **Equal terms.** A unit of work earns the same for everyone.
6. **Simplicity.** Every parameter serves a stated target.

The design has three rules. A reward pays for the gas it carries. A claim takes at least a fixed amount of work per token. Above a target number of claims per block, the puzzle gets harder.

## The work price

`WORK_PER_LEPTA` sets the least work per token. At 37 hashes per LEPTON, one core of the target machine earns at most 16.99 LOGOS in 30 days. At $0.05 that is $0.85, below the $0.86 a month that the cheapest rented server costs for the same work.

The server comes from an October 2026 survey of plans: a Contabo Cloud VPS 4, 4 shared vCPUs for $6.12 a month. Its terms forbid mining. No server has run HashWX, so a vCPU is counted as one core of the Intel Core Ultra 9 285HX with all 24 cores busy: 430,833 hashes a second, 1.78 Pi 5 cores. At the 285HX's one-worker rate of 558,000 hashes a second, the same derivation gives 48 hashes per LEPTON.

What a core's worth of hash rate costs a month, at 30 cents a kWh:

| Machine | Cost per Pi 5 core a month |
| --- | --- |
| A spare core of a machine that already runs a node, at home or in a data centre | close to nothing |
| An Apple M4 Pro someone owns, all cores mining at 65 W | about $0.60 |
| The cheapest rented server | $0.86 |
| An RTX 5060 Ti someone owns, at 180 W, on its author's figure | about $1.69 |
| A Raspberry Pi 5 mining on one core, paying the whole board's power | about $0.66 |
| The cheapest host that allows mining, a Contabo Cloud VDS S | $4.50 |

The cheapest server sets the line rather than the cheapest host that allows mining. With the higher line, renters who break their host's terms would join at five times their rent, until the claims target binds and their competition brings every core's income back to their cost. The line would then only decide who takes the pool. Neither line favours home or professional nodes: both earn the same per unit of hash rate.

Above $0.05 renting pays, until renters push the puzzle to the claims target. The target bounds how fast they take the pool, and the vesting how soon they can sell on the open market, as the next sections show.

`WORK_PER_LEPTA` is an era parameter. Servers get cheaper and faster, so it is revised from a fresh survey of plans and a HashWX run on the cheapest server. The reference machine may change at the same revision.

The rates are HashWX v1.0.0 in compiled mode:

| Machine | One core, hashes/s | Whole machine, hashes/s |
| --- | --- | --- |
| Raspberry Pi 5, 10 minutes per run | 243,836 | 975,685 |
| Apple M4 Pro | 487,000 | 5.0M to 6.0M, machine busy |
| Intel Core Ultra 9 285HX | 558,000, one worker | 10.34M |

The Pi 5 held 2,400 MHz for 10 minutes at 54 to 69 °C with an active cooler, and never throttled. Interpreted, one core does 51,088 hashes a second, 4.77 times fewer. On its own power rails the Pi draws about 1.8 W idle, 3.0 W with one core mining and 5.3 W with four.

The author of HashWX reports 5.6M hashes a second on an RTX 5060 Ti at 180 W, about 23 Pi 5 cores. Nobody has reproduced it. Such a card earns about $20 a month at the work price at $0.05. Bought to mine, it does not pay: its power costs $13 to $39 a month at 10 to 30 cents a kWh, and a $400 card costs about $17 a month over two years. A card someone owns covers its power only below about 15 cents a kWh.

## The reward and the vested share

The liquid part of a reward pays the storage fee of 949 bytes: a claim transaction of 341 bytes and one reference transaction of 608. At the initial storage price that is 0.7592 LOGOS, and the reward is 7.592 LOGOS. The reward follows the storage price, so a dearer byte means a larger reward and proportionally more work.

`POW_VESTED_SHARE` rises from 50 to 90. A higher share needs a larger reward to carry the same gas, so one core waits longer for each claim:

| Vested share | Reward per claim at the initial price | One core finds a claim |
| --- | --- | --- |
| 90% | 7.6 LOGOS | about every 13 days |
| 95% | 15.2 LOGOS | about every 27 days |
| 98% | 38.0 LOGOS | about every 67 days |
| 99% | 75.9 LOGOS | about every 134 days |

The total paid per core is the same in every row. The liquid part is gas, so a share above 90% does little more for the price, and claims for one core become rare.

A claim leaves one vested note, which cannot merge before it vests, and one liquid change note. The `TRANSFER` that pays its fee spends its first liquid note at once. A claim therefore adds up to three nullifiers in its life. One core makes about 27 vested notes a year. At the claims target, claims add at most 1.2 GB of nullifiers a year: 12 claims a block, 1,051,200 blocks and three nullifiers of 32 bytes each.

The vesting lasts a year: `VESTING_EPOCHS` is the number of epochs that first reaches a year, 49 of 7.5 days today and 146 of 60 hours once the epoch is shortened. A vested note leads and can be staked like a liquid one, so vesting delays sales on the open market rather than every sale. A miner can mine to a buyer's key, or stake its vested notes under a buyer's keys in one transaction with a `TRANSFER` paying the seller.

## The claims target

The threshold steers toward `TARGET_CLAIMS_PER_BLOCK` claims per block, raised from master's 10 to 12. Below the target every core earns the work price. Above it the puzzle gets harder, and every core earns less. It binds once about 460,000 cores' worth of hash rate mines at the work price.

The target is the only brake on how fast the pool pays out. At a reward of 7.592 LOGOS, 12 claims a block pay at most 95.8M LOGOS a year, so without fees the 200M last at least 2.1 years. 12 is the largest target at which they last at least two years: at 13 they would last 1.9. The brake is a number of claims, not a share of what the pool holds, so a long busy stretch can empty the pool. Claiming then resumes only as the fee share refills it.

The two hundredths of the supply set aside at genesis are a ceiling, not a schedule. Each thousand participants mining on one core take about 0.21M LOGOS a year. Fees beyond what claims take stay in the pool.

Claim transactions count in the load that sets `difficulty_blend`. 12 claims a block are 9% of the reference 130 transactions a block, so with other traffic at the reference load a full target makes a Blend solution take about 4.5% more work.

## The claim limit

A block holds at most `MAX_CLAIMS_FACTOR` = 10 times the target: 120 claims, 40,920 bytes of a 2 MiB block.

## What goes

- The reward computed from the pool, and with it the distribution rate $`\rho`$ and `EXPECTED_BLOCKS_PER_EPOCH`.
- The fixed cap `REWARD_TARGET_CAP`.
- The check that `epoch_pow_reward` is positive, since a reward is at least 9,490 LEPTA.
- The constraint that the vested notes of a minimum stake fit one declaration.

## Era parameters

Eras holds every proof of work value as an era parameter. This change adds `WORK_PER_LEPTA`, `MAX_CLAIMS_FACTOR`, `POW_CLAIM_TX_SIZE` and `POW_REFERENCE_TX_SIZE` to the record. `WORK_PER_LEPTA` replaces `minimum_difficulty`, the field of `REWARD_TARGET_CAP`. `rate_num` and `rate_den`, the distribution rate, leave the record. `target_claims_per_block` stays and takes 12. `ema_smoothing_factor` and `ema_smoothing_precision` take 999 and 1000, and `REWARD_TARGET_FLOOR` follows from them. `POW_VESTED_SHARE` takes 90. `VESTING_EPOCHS` follows from `EPOCH_LENGTH`. `POW_REWARD_POOL_GENESIS` is set at genesis only.

## Compatibility

Bedrock has no genesis yet, so the change needs no migration.

## Open questions

- **Execution Gas.** The reward covers storage fees only. A claim's Execution Gas fee must stay below the storage fee of the reference transaction, or the liquid part cannot pay the claim's whole fee.
- **The implementation.** The known implementations of HashWX are LGPL, and the node's licence policy allows no LGPL. A permissive reimplementation is planned. The values assume the compiled mode.
- **The author's caution.** The author of HashWX advises against it for proof-of-work consensus. Here it prices rewards, not consensus.
- **Stolen machines.** Owned machines include stolen ones, so botnets earn the most. Their earnings are 90% vested stake rather than cash.
- **Graphics cards.** The figure for the RTX 5060 Ti is the author's, not reproduced.
- **The reference transaction.** 608 bytes is this RFC's choice of an ordinary transaction, to revise once real sizes are known.

# Details

## 1. The reward

A reward pays for the gas it carries, and `POW_VESTED_SHARE` rises from 50 to 90. `VESTING_EPOCHS` becomes the number of epochs that first reaches a year, so it follows the epoch length. The reward computed from the pool goes, with the distribution rate and `EXPECTED_BLOCKS_PER_EPOCH`.

```diff
+POW_CLAIM_TX_SIZE: uint64 = 341                 # the bytes of a claim transaction
+POW_REFERENCE_TX_SIZE: uint64 = 608             # the bytes of the further transaction a reward's liquid part pays for
-POW_VESTED_SHARE: uint64 = 50
+POW_VESTED_SHARE: uint64 = 90                   # the share of a reward paid as a vested note, out of SHARE_DEN
-VESTING_EPOCHS: uint64 = 49                     # the length of the vesting, in epochs
+EPOCH_LENGTH: uint64                            # the slots of an epoch of Epoch Schedule
+VESTING_EPOCHS: uint64 = (31_536_000 + EPOCH_LENGTH - 1) // EPOCH_LENGTH  # the epochs that first reach a year of one-second slots
-EPOCH_POW_DISTRIBUTION_RATE_NUM: uint64 = 1
-EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 200
-EXPECTED_BLOCKS_PER_EPOCH: uint64 = 21_600

-def compute_epoch_pow_reward(pow_reward_pool: TokenValue) -> TokenValue:
-    denominator = (EPOCH_POW_DISTRIBUTION_RATE_DEN
-                   * TARGET_CLAIMS_PER_BLOCK
-                   * EXPECTED_BLOCKS_PER_EPOCH)
-    return (pow_reward_pool * EPOCH_POW_DISTRIBUTION_RATE_NUM) // denominator
+def compute_epoch_pow_reward(permanent_storage_gas_price: TokenValue) -> TokenValue:
+    # Rounded up, so that the liquid part covers the storage fee of both transactions.
+    fee = (POW_CLAIM_TX_SIZE + POW_REFERENCE_TX_SIZE) * permanent_storage_gas_price
+    liquid_share = SHARE_DEN - POW_VESTED_SHARE
+    return checked_uint64((fee * SHARE_DEN + liquid_share - 1) // liquid_share)
```

At each epoch boundary, once the storage price of the new epoch is set, `epoch_pow_reward` is set for the epoch and held for it. `fee * SHARE_DEN` is computed in 128 bits.

## 2. The work floor

The fixed cap goes. The cap now scales with the reward, so a claim takes at least `WORK_PER_LEPTA` hashes per LEPTON of its reward in expectation.

```diff
-REWARD_TARGET_CAP: uint64 = 2**64 // (HASHWX_MACHINE_RATE * 1_620)
+WORK_PER_LEPTA: uint64 = 37                     # least expected HashWX hashes per LEPTON of a reward
-EMA_SMOOTHING_FACTOR: uint64 = 9
-EMA_SMOOTHING_PRECISION: uint64 = 10
-REWARD_TARGET_FLOOR: uint64 = 9
+EMA_SMOOTHING_FACTOR: uint64 = 999
+EMA_SMOOTHING_PRECISION: uint64 = 1000
+REWARD_TARGET_FLOOR: uint64 = max(1, (EMA_SMOOTHING_PRECISION - 1) // (EMA_SMOOTHING_PRECISION - EMA_SMOOTHING_FACTOR))

+def reward_target_cap(epoch_pow_reward: TokenValue) -> uint64:
+    return 2**64 // (epoch_pow_reward * WORK_PER_LEPTA)
```

`WORK_PER_LEPTA` is the work of one core of the target machine in 30 days, a quarter of `HASHWX_MACHINE_RATE` times 2,592,000 seconds, divided by the LEPTA that the cheapest server's monthly cost for the same work buys at $0.05: 6.29·10¹¹ / 1.722·10¹⁰ = 36.5, rounded up to 37. At genesis `difficulty_reward` is the cap of the reward of epoch 0, and at each epoch boundary it is lowered to the cap of the new reward if it lies above it. `REWARD_TARGET_FLOOR` follows from the smoothing constants, 999 at 999/1000. A reward is at least 9,490 LEPTA, since the storage price is at least one LEPTON per byte, so the cap stays below $`2^{46}`$ and the retarget's product within 128 bits. The cap stays above `REWARD_TARGET_FLOOR` for every reward below about 499,000 LOGOS.

## 3. The claim limit

`TARGET_CLAIMS_PER_BLOCK` rises from 10 to 12. The retarget keeps steering toward it under the cap of the work floor, and a block holds at most `MAX_CLAIMS_FACTOR` times the target.

```diff
-TARGET_CLAIMS_PER_BLOCK: uint64 = 10            # T
+TARGET_CLAIMS_PER_BLOCK: uint64 = 12            # T
+MAX_CLAIMS_FACTOR: uint64 = 10                  # a block's claim limit, in multiples of T

 def compute_new_reward_difficulty(claims_in_block: uint64,
-                                  current_target: uint64) -> uint64:
+                                  current_target: uint64,
+                                  epoch_pow_reward: TokenValue) -> uint64:
     demand = max(1, (P - F) * claims_in_block + F * TARGET_CLAIMS_PER_BLOCK)
     new_target = (TARGET_CLAIMS_PER_BLOCK * current_target * P) // demand
-    return min(max(new_target, REWARD_TARGET_FLOOR), REWARD_TARGET_CAP)
+    return min(max(new_target, REWARD_TARGET_FLOOR), reward_target_cap(epoch_pow_reward))
```

`P` and `F` stand for the two smoothing constants. Claims take at most `MAX_CLAIMS_FACTOR` · `TARGET_CLAIMS_PER_BLOCK` · `POW_CLAIM_TX_SIZE` = 40,920 bytes of a block. `MAX_CLAIMS_FACTOR` must be at least 2, or the retarget never lowers the target.

## 4. The claim limit in Mantle

A claim fails in a block that already holds `MAX_CLAIMS_FACTOR * TARGET_CLAIMS_PER_BLOCK` claims. The check that the reward is positive goes, since a reward is at least 9,490 LEPTA.

```diff
-assert epoch_pow_reward > 0
 assert pow_reward_pool >= epoch_pow_reward
+assert claims_before < MAX_CLAIMS_FACTOR * TARGET_CLAIMS_PER_BLOCK
```

## 5. The pool seed

`POW_REWARD_POOL_GENESIS` becomes two hundredths of $`S_{cap}`$, 200M LOGOS, instead of five thousandths. Genesis sets `epoch_pow_reward` at the initial storage price.

## Chores

- The Introduction and Overview of Proof of Work describe the reward, the work floor and the claims target.
- The Protocol of Proof of Work lists the claim checks in the order Mantle runs them.
- The Notation of Proof of Work drops $`\rho`$, $`N_b`$, $`S_{cap}`$ and $`k`$. Only the Genesis Block states the value of the seed.
- Block Rewards says its projected growth leaves out the claims paid from the pool.

# Implementation

- [ ] Land this after the reward puzzle is replaced by HashWX, and after the epoch is shortened to 60 hours.
- [ ] Set `epoch_pow_reward` from the storage price at each epoch boundary and at genesis, after the storage price of the new epoch, and remove the reward computed from the pool.
- [ ] Cap `difficulty_reward` at `reward_target_cap(epoch_pow_reward)` after every block and at each epoch boundary, keep steering it toward `TARGET_CLAIMS_PER_BLOCK`, and start it at the cap of epoch 0.
- [ ] Set the smoothing constants to 999 and 1000, and derive `REWARD_TARGET_FLOOR` from them.
- [ ] Refuse a claim in a block that already holds `MAX_CLAIMS_FACTOR * TARGET_CLAIMS_PER_BLOCK` claims, and drop the check that the reward is positive.
- [ ] Set `POW_VESTED_SHARE` to 90, and derive `VESTING_EPOCHS` from the epoch length.
- [ ] Set `TARGET_CLAIMS_PER_BLOCK` to 12.
- [ ] Seed the pow reward pool with two hundredths of the supply cap.
- [ ] Measure HashWX on a rented server, and revise `WORK_PER_LEPTA` if a vCPU is not about 1.78 Pi 5 cores.
- [ ] Add the new constants to the era parameter record, and remove `minimum_difficulty`, `rate_num` and `rate_den`, once Eras and this change are on one branch.
- [ ] Add tests: the reward at the initial and at a high storage price, the cap at both and at an epoch boundary, a claim refused by the claim limit, a claim against a pool below the reward, the retarget at the cap and above the target, and a block without claims at the floor.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.5.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.6.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.4.0 |
| [Block Rewards](../block-rewards.md) | Modified | Revision 1.4.1 |
