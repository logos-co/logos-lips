# [RFC] Cryptarchia: Infer the total stake without floating point

**Motivation and proposal:** [PR #529](https://github.com/logos-co/logos-lips/pull/529)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Total Stake Inference](#affected-specifications): [the exact inference](#1-the-inference-computes-the-next-estimate-exactly) | the single division against the analysis's update rule; why truncating division agrees; the cap and the 256-bit width |
| 2 | Critical | [Bedrock Eras](#affected-specifications): [the learning rate as a ratio](#2-the-era-record-carries-the-learning-rate-as-a-ratio) | one field's new encoding, which changes every era and fork digest |
| 3 | Medium | [Bedrock Eras](#affected-specifications): [the record's bounds](#3-the-record-bounds-the-learning-rate-and-no-longer-bounds-f-from-below) | the learning-rate bound against the stability condition; the bound on `f` that goes away |

# Discussion

## What the change moves

The estimate settles where the measured density equals the expected density. The implementation expects `PERIOD · ⌊1000 · f⌋ / 1000` occupied slots per observation period. With this change the inference expects `PERIOD · f`.

| Settings | Implementation | This change |
| --- | --- | --- |
| Reference: `k` = 2160, `f` = 1/30, `β` = 1 | 1.0103 × the true stake; 0.0330 occupied slots per slot | the true stake; 1/30 |
| `k` = 120, `f` = 1/30, `β` = 1, as in the implementation's genesis deployment templates | 1.0098 × the true stake; 0.0330 | the true stake; 1/30 |
| `k` = 30, `f` = 1/20, `β` = 1/2, as in the implementation's era schedule | the same estimates | the same estimates |

Each row iterates the inference on the expected density, with every occupied slot counted, from an estimate equal to the true stake. At the reference values the implementation aims for 12,830 occupied slots per observation period instead of 12,960, and a period with exactly 12,960 raises the estimate by 1.01%. An `f` such as 1/91 would move the estimate by 10%.

Where `f · 1000` and `β · 1000` are integers, the two agree. At `f` = 1/20 and `β` = 1/2 they gave the same estimate in 200,000 random cases, apart from estimates above `2^64 − 1` ([The cap](#the-cap)).

## Why the estimate must be exact

The estimate sets the lottery constants `t_0` and `t_1`, which are public inputs of [Proof of Leadership](../cryptarchia-proof-of-leadership.md#circuit-public-inputs). At an estimate of `3 · 10^18`, a difference of one changes `t_0` by about `8 · 10^37`. A leader proof made under one estimate then fails verification under the other. Every node must derive the same estimate exactly.

The old pseudo-code is Rust-like and does not say how its three integer divisions round. The implementation truncates toward zero. The same code with floor division, which a Python port would use, gave a different estimate in 193 of 200,000 random cases with more occupied slots than expected, at the reference values. The new form has one division. Its numerator is negative only when the result is clamped to 1, so floor and truncating division give the same estimate.

## Why a ratio

The implementation truncates the double-precision learning rate to thousandths. A learning rate of 0.0005 becomes 0 and freezes the estimate. Binary64 rounding also makes 48 of the 5,001 three-decimal values in `[0, 5]` one thousandth short: 1.001 becomes 1.000. A ratio holds the value the record gives, and `f` is already one.

## Why the learning rate is at most 2

The [Stability Condition](../analysis-total-stake-inference.md#stability-condition) of the analysis bounds `β` by `2f / ((q − f) · ln(1 / (1 − f/q)))`. The bound is lowest at `q` = 1, and there it exceeds 2 for every `f`: 2.109 at `f` = 1/10, 2.034 at 1/30 and 2.001 at 1/1000. It approaches 2 as `f` approaches 0. A learning rate up to 2 is therefore stable for every `f` and `q`, and no larger bound is. The implementation accepts any non-negative finite learning rate, 0 included.

## The cap

The estimate is clamped to at most `2^64 − 1`. The implementation panics when the estimate exceeds that value, and the old pseudo-code's cast to `u64` wraps it. Neither happens unless the estimate approaches `2^64 − 1`. The cap makes the result defined for every record.

## Width

With the estimate and `PERIOD` below `2^64` and the parts of `β` and `f` below `2^32`, the numerator needs up to 193 bits, so the specification states a signed 256-bit integer. At the reference values, with an estimate up to `10^19`, it needs 87 bits. A record bound such as `β.den · f.den · PERIOD < 2^61` would keep every value within a signed 128-bit integer, since `β` is at most 2 and `f` is below 1. That bound would tie three fields together, so this RFC states the width instead.

## Compatibility

The estimate changes wherever `f · 1000` or `β · 1000` is not an integer, the reference `f` of 1/30 included. The record's encoding of `learning_rate` changes from an 8-byte binary64 to two 4-byte integers, so every era digest and fork digest changes. Bedrock has no deployed network, so the change needs no migration. The implementation still computes the inference with floats ([Implementation](#implementation)).

# Details

## 1. The inference computes the next estimate exactly

In [Algorithm](../cryptarchia-total-stake-inference.md#algorithm), the old pseudo-code scaled `beta` and `f` by `PRECISION` = 1,000 as truncated double-precision products, then divided three times. The new code computes the estimate from the ratios with one floor division:

```python
def total_stake_inference(total_stake_estimate: int, epoch_slot: int) -> int:
    measured_density = density_over_slots(epoch_slot, PERIOD)
    # total_stake_estimate * (1 - beta + beta * measured_density / (f * PERIOD)),
    # over a single denominator so that only the last division rounds.
    numerator = total_stake_estimate * (
        (beta.den - beta.num) * f.num * PERIOD + beta.num * f.den * measured_density
    )
    denominator = beta.den * f.num * PERIOD
    return min(max(numerator // denominator, 1), 2**64 - 1)
```

The rules after the code replace the sentence on double-precision values:

- A negative numerator makes the result 1 under either rounding, so truncating division gives the same result.
- Every intermediate value lies strictly between `−2^193` and `2^193`, so a signed 256-bit integer holds each one.

## 2. The era record carries the learning rate as a ratio

In [Era Parameters](../bedrock-eras.md#era-parameters):

```diff
-| `cryptarchia` | `learning_rate` | `binary64` | `beta` of Parameters and variables |
+| `cryptarchia` | `learning_rate` | `ratio` | `beta` of Parameters and variables |
```

The record encodes a ratio's parts as given, so the source constant names both. In [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables):

```diff
-| `beta` | 1.0 | learning rate | Controls how quickly we adjust to new participation levels. ... |
+| `beta` | 1/1 | learning rate | Scales each correction of the estimate. |
```

## 3. The record bounds the learning rate, and no longer bounds f from below

In [Era Parameters](../bedrock-eras.md#era-parameters):

```diff
 In every record, `slot_activation_coeff` is below 1. Otherwise the lottery constants t_0
-and t_1 of Proof of Leadership take the logarithm of 0. It is also at least 1/PRECISION,
-with PRECISION of Total Stake Inference. Otherwise Total Stake Inference truncates
-f · PRECISION to 0.
+and t_1 of Proof of Leadership take the logarithm of 0.
+
+In every record, `learning_rate` is above 0 and at most 2. Otherwise Total Stake
+Inference never changes the estimate, or can fail the Stability Condition of its
+analysis, which holds for every learning rate up to 2.
```

A record with an `f` below 1/1000 becomes valid. A record with a learning rate of 0 or above 2 becomes invalid.

## Chores

- [Era Parameters](../bedrock-eras.md#era-parameters) loses the `binary64` encoder and the sentence that defines it, which no field uses any more.
- The description of `beta` in [Parameters and variables](../cryptarchia-total-stake-inference.md#parameters-and-variables) says what it does. The trade-off it described is in the analysis.

# Implementation

- [ ] Compute the estimate as in [Details 1](#1-the-inference-computes-the-next-estimate-exactly) in `StakeInference::total_stake_inference` (`ledger/src/cryptarchia/stake.rs`), from `slot_activation_coeff` and the learning rate as ratios, and clamp it to `u64::MAX` in place of the `expect`. Remove `PRECISION` and its re-export `STAKE_INFERENCE_PRECISION`.
- [ ] Make the learning rate a ratio: `learning_rate` in `Settings` (`nodes/node/binary/src/config/deployment/era/ruleset/v1/cryptarchia/mod.rs`), `stake_inference_learning_rate` in `consensus/cryptarchia-engine/src/config.rs`, the era schedules and the genesis deployment templates (`learning_rate: 0.5` becomes `{numerator: 1, denominator: 2}`), and the `SETTINGS_HEX` fixture in `ruleset/v1/cryptarchia/codec.rs`.
- [ ] Refuse a record whose learning rate is 0 or above 2, and remove the check of `f` against `STAKE_INFERENCE_PRECISION` from `SlotActivationCoeff::try_from`.
- [ ] Compute `PERIOD` in integers. `average_slots_for_blocks` (`consensus/cryptarchia-engine/src/config.rs`) divides `k` by `f` in binary64, and for some values, such as `k` = 2160 with `f` = 1/91, it returns one slot less than `⌊k/f⌋`.
- [ ] Add tests at `k` = 2160 and `f` = 1/30: at `β` = 1/1, an estimate of `3 · 10^18` stays unchanged at 12,960 occupied slots and falls to 1 with none; at `β` = 1/2 it halves with none; at `β` = 2/1 with none the result is 1; an estimate that would exceed `u64::MAX` is clamped.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | Revision 1.3.0 |
| [Bedrock Eras](../bedrock-eras.md) | Modified | Revision 1.1.0 |
