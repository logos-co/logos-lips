# [RFC] Eras: Carry the fee window, and keep dependent values consistent

**Motivation and proposal:** [PR #517](https://github.com/logos-co/logos-lips/pull/517)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-09 |

## Reviewer Orientation

Read the PR's Motivation first. [Era Parameters](../bedrock-eras.md#era-parameters) defines the record that this change extends.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Bedrock Eras](#affected-specifications): [`fee_window_size`](#1-the-era-record-carries-fee_window_size) | the field's position and width, which every fork digest hashes |
| 2 | Critical | **Start here** — [Block Rewards](#affected-specifications): [the window update](#2-the-window-updates-in-every-block) | the update runs before the reward, under the era of the block's slot; [why it is not a migration](#a-rule-per-block-not-a-migration) |
| 3 | Critical | [Execution Market](#affected-specifications): [the cap](#3-the-base-fee-update-caps-the-previous-average) | [the cap acts once per cut](#the-cap-acts-once-per-cut), and every other block computes what it computed before |
| 4 | High | [Bedrock Eras](#affected-specifications): [the gas bound](#4-a-records-gas-values-leave-room-for-the-fee-payment) | [the largest threshold it covers](#the-gas-bound), and that the reference table passes |
| 5 | Medium | [Block Rewards](#affected-specifications), [Bedrock Eras](#affected-specifications): [the derived constants](#5-the-reward-constants-are-derived) | the derivations give `10_512` and `62500/657` at the reference values; [one open question](#should-the-record-keep-fee_average_numerator) |
| 6 | Medium | [Blend Protocol](#affected-specifications): [the transaction target](#6-the-transaction-target-follows-blends-sizing) | [one open question](#should-the-transaction-target-be-an-upper-bound) |

# Discussion

## A rule per block, not a migration

`update_pooled_fees_window` runs in every block and does not look at the previous era. A migration at each era boundary gives another result when an era passes with no block. Take `T` of 120, 60 and 120 in three eras, with no block in the second. A migration leaves 60 zeros in the window. The rule leaves none.

The implementation's `resize_fee_window` compares the window with the size of the block's era, so it gives the same window as the rule. A Python copy of it equals the reference code on 100,778 blocks, with `T` drawn from 1 to 12 and changed at random.

A longer window starts with zeros, so `A_t` reads fewer fees until the window fills. With `T` going from 120 to 240 and steady fees, `FEE_AVG_NUMERATOR` halves while the window still holds the old sum. The fee term of `A_t` then halves at the boundary and returns to its old value after 120 blocks. A shorter window leaves the term unchanged at steady fees.

## The cap acts once per cut

Block usage is at most `G_max`, so the average stays within `G_max` unless an era lowers it. The cap therefore acts in at most one block per cut: the first block whose era has a `G_max` below the average.

The table shows the highest base fee after a cut, as a multiple of the base fee before it. It uses `q = 9/10` and `φ = 1/8`, starts with the average at the old limit of 3,193,460, and takes every later block as empty.

| `G_max` cut to | With the cap | Without the cap |
| --- | --- | --- |
| 1/2 | ×1.34, after 6 blocks | ×4.83, after 13 blocks |
| 1/10 | ×1.34, after 6 blocks | ×173,730, after 28 blocks |

## The gas bound

A channel sets its thresholds when it is configured, and a later era can raise a per-key price or lower the limit. The bound uses the most signatures a block body can hold, so it covers every threshold that fits a block by size. At the reference values, the largest sum is 590 + 59 · 32,768 = 1,933,902, within the limit of 3,193,460.

The implementation checks each field alone, and a per-key field for one key only.

## Should the transaction target be an upper bound?

[The sizing rule](#6-the-transaction-target-follows-blends-sizing) fixes `target_transactions_per_block` at `⌊F_T / F_D⌋`, which is 130 at the reference values. The reason it gives, the backlog, needs only an upper bound.

The implementation's schedule holds 2, and its comment says the reference load must be the load the network carries, not a theoretical capacity. The sizing gives 246 at that schedule's Blend values. A rule of "at most `⌊F_T / F_D⌋`" would still prevent the backlog, and it would accept that schedule. This question is open.

## Should the record keep `fee_average_numerator`?

[The derivation](#5-the-reward-constants-are-derived) makes this field a value that other fields fix. The implementation's encoding carries it, so the record keeps it, and a record where it differs is invalid. Dropping the field would leave one source for one quantity, and it would change the implementation's encoding. This question is open.

## Compatibility

`fee_window_size` changes the encoding of every record, and so every era digest and fork digest. Bedrock has no deployed network, so the change needs no migration. The other rules change no encoding. While `T` and `G_max` keep their values, the window update and the base fee update compute what they computed before. The new constraints refuse records that the earlier ones accepted, and [Implementation](#implementation) lists the schedule values this affects.

# Details

## 1. The era record carries `fee_window_size`

In [Era Parameters](../bedrock-eras.md#era-parameters), `block_rewards` gains a field. [Section 5](#5-the-reward-constants-are-derived) requires it to be at least 1.

```diff
 | `block_rewards` | `emission_factor_scale` | `UINT64` | `A_SCALE` of Float Precision for Implementation |
+| `block_rewards` | `fee_window_size` | `UINT16` | T of Parametrization |
 | `block_rewards` | `fee_average_numerator` | `UINT64` | `FEE_AVG_NUMERATOR` of Float Precision for Implementation |
```

## 2. The window updates in every block

In [Float Precision for Implementation](../block-rewards.md#float-precision-for-implementation), `T` joins the constants and the update joins the reference code:

```diff
+T = 120                          # the blocks of the look-back window
 # ...
+def update_pooled_fees_window(pooled_fees_window: list[int], pooled_fees: int) -> list[int]:
+    # After an era that changes T, the window holds a different number of fees.
+    # A shorter T drops the oldest, and a longer T starts the entries it adds at 0.
+    return ([0] * T + pooled_fees_window + [pooled_fees])[-T:]
```

The text after the code defines the window and names the era for both functions:

```diff
-`block_reward` uses the constants of the era of the block's slot.
+`pooled_fees_window` holds D_1,τ of the latest blocks, oldest first and ending with the
+current block. It holds T zeros at genesis. A block updates it with its own D_1,t before
+it computes its reward. `update_pooled_fees_window` and `block_reward` use the constants
+of the era of the block's slot.
```

## 3. The base fee update caps the previous average

In the [Base Fee Update Rule](../execution-market.md#base-fee-update-rule), the smoothed average reads the previous average capped at `G_max` of the era of block `s`. The step, the two derivation formulas and the reference code all change this way:

```diff
-2. Smoothed Average Update: G_avg[s] = (1 - q) · G[s] + q · G_avg[s-1]
+2. Smoothed Average Update: G_avg[s] = (1 - q) · G[s] + q · min(G_avg[s-1], G_max)
```

```diff
 def update_g_avg(prev_g_avg: int, block_gas_used: int) -> int:
-    numerator = (EMA_DENOMINATOR - EMA_PREV_WEIGHT) * block_gas_used + EMA_PREV_WEIGHT * prev_g_avg
+    # An era may set a G_max below the previous average. Without the cap, the base
+    # fee could then rise by more than phi in a block.
+    numerator = (EMA_DENOMINATOR - EMA_PREV_WEIGHT) * block_gas_used + EMA_PREV_WEIGHT * min(prev_g_avg, G_MAX)
     return numerator // EMA_DENOMINATOR
```

## 4. A record's gas values leave room for the fee payment

In the constraints of [Era Parameters](../bedrock-eras.md#era-parameters):

```diff
-Each field of `gas_profile` is at most `max_gas_per_block`. Otherwise no block can include
-an Operation that costs that field or more.
+In every record, `transfer` plus each other field of `gas_profile` is at most
+`max_gas_per_block`, with `channel_config`, `channel_withdraw` and `channel_transfer` first
+multiplied by ⌊max_transactions_size / 64⌋, the most signatures a block body can hold.
+Otherwise an Operation that fits a block by size cannot be included with the `TRANSFER`
+that pays its fee, and a channel's funds can be stranded.
```

## 5. The reward constants are derived

In [Float Precision for Implementation](../block-rewards.md#float-precision-for-implementation), `FEE_AVG_NUMERATOR` is computed, and the text after the code gives the emission per block:

```diff
-FEE_AVG_NUMERATOR = 10_512       # A_SCALE * alpha_a / (I_max * D1_target * Delta_t * T)
+# A_SCALE * alpha_a / (I_max * D1_target * Delta_t * T), which is 10_512, with
+# alpha_a = 1, D1_target = S_CAP and f = 1.
+FEE_AVG_NUMERATOR = A_SCALE * INFLATION_DENOMINATOR // (INFLATION_NUMERATOR * T)
```

```diff
+`INFLATION_NUMERATOR / INFLATION_DENOMINATOR` is I_max · S_cap · d / (f_s · 365 · 86400),
+with d the slot length in seconds and f_s the slot activation coefficient of Constants,
+which gives 62500/657 at their reference values. With another value, the reserve releases
+more or less than I_max of S_cap per year.
```

In the constraints of [Era Parameters](../bedrock-eras.md#era-parameters):

```diff
-In every record, `emission_factor_scale` is at least 1. Otherwise `block_reward` of Float
-Precision for Implementation divides by zero.
+In every record, `fee_window_size`, `emission_factor_scale` and the numerator of
+`max_emission_per_block` are at least 1. Otherwise Float Precision for Implementation
+divides by zero. `fee_average_numerator` is the `FEE_AVG_NUMERATOR` that section derives
+from these fields. Otherwise the emission rate factor weighs the pooled fees by more or
+less than their annualized rate.
```

## 6. The transaction target follows Blend's sizing

In [Expected Traffic](../blend-protocol.md#expected-traffic), after the sizing of `F_T`:

```diff
+An era that changes a value this sizing reads must set `target_transactions_per_block`
+(Era Parameters) to the resulting ⌊F_T / F_D⌋. Otherwise a backlog outlasts the time a
+message may spend at one hop.
```

## Chores

- In [Float Precision for Implementation](../block-rewards.md#float-precision-for-implementation), the sentence that states the section's goal also names the window.

# Implementation

- [ ] Carry `fee_window_size` in `BlockRewardsConfig` and the record's encoding, and apply `resize_fee_window` in every block ([logos-blockchain#4016](https://github.com/logos-blockchain/logos-blockchain/pull/4016), draft).
- [ ] In `update_execution_market` (`ledger/src/cryptarchia/mod.rs`), use `min(average_execution_gas, max_gas_per_block)` as the previous average.
- [ ] In the validation of `nodes/node/binary/src/config/deployment/era/ruleset/v1/cryptarchia/mod.rs`, replace the check that bounds each `gas_profile` field alone with [the gas bound](#4-a-records-gas-values-leave-room-for-the-fee-payment).
- [ ] In `BlockRewardsConfig::new` (`ledger/src/config.rs`), refuse a zero numerator of `max_emission_per_block`, and a `fee_average_numerator` other than the derived one.
- [ ] Set `max_emission_per_block` and `fee_average_numerator` in the era schedule from [the derivations](#5-the-reward-constants-are-derived). At its `slot_activation_coeff` of 1/20 and 1-second slots they are 125000/1971 and 15,768. It holds 62500/657 and 10,512, which release 1.5% of `S_cap` a year in place of 1%.
- [ ] Set `target_transactions_per_block` in the era schedule once [the open question](#should-the-transaction-target-be-an-upper-bound) is settled.
- [ ] Add tests: a cut to `G_max` at the reference market values, a record at each edge of the gas bound, and a record with a wrong `fee_average_numerator`.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Revision 1.1.0 |
| [Block Rewards](../block-rewards.md) | Modified | Revision 1.4.0 |
| [Execution Market](../execution-market.md) | Modified | Revision 1.4.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.10.0 |
