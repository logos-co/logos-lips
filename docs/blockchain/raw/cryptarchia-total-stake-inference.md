# TOTAL-STAKE-INFERENCE

| Field | Value |
| --- | --- |
| Name | Total Stake Inference |
| Slug | 94 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <davidrusu@logos.co> |
| Contributors | Alexander Mozeika <alexander.mozeika@logos.co>, Daniel Kashepava <danielkashepava@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-01-20 |
| 1.1.0 | Changed `density_over_slots` to count **distinct occupied slots** instead of blocks, including the slots of the [uncles](cryptarchia-v1-protocol.md#uncle-references) referenced by the honest chain's in-period blocks, due to updated [Cryptarchia Protocol](cryptarchia-v1-protocol.md). | 2026-08-06 |
| 1.2.0 | `PERIOD` reads the finality window `K`. `density_over_slots` and the inference take the chain they count, so that [Commit](cryptarchia-v1-protocol.md#commit) can read the count. | 2026-11-13 |
| 1.2.1 | `PERIOD` reads `⌊k/f⌋` in place of the finality window `K`, so the observation period keeps its length when `K` changes. | 2026-11-13 |
| 1.3.0 | `PERIOD` reads the finality window `K`, as the [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule) does: 144,000 slots. The learning rate `beta` is 1/2, a ratio of integers. The next estimate keeps at least `gamma` = 3/4 of the current one. | 2026-11-27 |

# Introduction

As with any Proof of Stake (PoS) consensus protocol, the probability that an eligible Cryptarchia participant wins the right to propose a block depends on that participant’s stake relative to the total active stake. Because leader selection in Cryptarchia is private, the total active stake is not directly observable. Instead, nodes must infer it from observable chain growth.

# Overview

The total active stake can be inferred by observing the slot occupancy rate: a higher fraction of occupied slots implies more stake participating in consensus. By observing the rate of occupied slots from the previous epoch and knowing the total stake estimate used during that period, we can infer a correction to the total stake estimate to compensate for any changes in consensus participation. This inference process is done by each node following the chain. Leaders will use this *total stake estimate* to calculate their *relative stake* as part of the leadership lottery *without revealing their stake* to others.

The stake inference algorithm adjusts the previous total stake estimate based on the difference between the empirical slot activation rate (measured as the growth rate of the honest chain) and the expected slot activation rate. A large difference serves as an indicator that the total stake estimate is not accurate and must be adjusted.

To measure the slot activation rate more accurately, the block count also includes the [uncle blocks](cryptarchia-v1-protocol.md#uncle-references) referenced by the honest chain. An uncle is a genuine lottery win, backed by a valid Proof of Leadership, that was lost to a fork instead of becoming part of the honest chain. Each block may reference several uncles, and the same uncle may be referenced by more than one block; the count is taken over distinct occupied slots, so each slot — whether occupied by a canonical block, a referenced uncle, or both — is counted only once. Without uncle references, these occupied slots would not be observed and the inference would underestimate the participation. Every uncle referenced from within the observation period contributes to the count, with no verification-based filtering: the signed headers are carried with the referencing blocks, and their validity is a condition of those blocks' own validity, so an uncle present in the chain has already been verified and every node holding the chain counts exactly the same set. Since forks are predominantly caused by network delays, counting referenced uncles also mitigates the accuracy loss under increased network delays noted below.

This algorithm has been analyzed and shown to have good accuracy, precision and convergence speed. A caveat to note is that accuracy decreases with increased network delays. The analysis can be found in [\[Analysis\] Total Stake Inference](analysis-total-stake-inference.md).

# Construction

## Definitions

### Parameters and variables

| Symbol | Value | Name | Description |
| --- | --- | --- | --- |
| `beta` | 1/2 | learning rate | Scales each correction of the estimate. Its numerator `beta.num` and denominator `beta.den` are integers (see [The stake inference](https://github.com/logos-co/logos-lips/blob/master/docs/blockchain/raw/rfc/RFC-TBD-cryptarchia-shorten-the-epoch-to-60-hours.md#the-stake-inference) for the choice of 1/2). |
| `gamma` | 3/4 | retained share | The least share of the current estimate that the next estimate keeps. Its numerator `gamma.num` and denominator `gamma.den` are integers. `gamma` must be below 1, or the estimate cannot fall. `gamma` must be at least $`1/\sqrt{2.097}`$. [`K`](cryptarchia-v1-protocol.md#constants) meets its targets with every block up to its delay $`\Delta`$ late only while the total active stake is at most 2.097 times the estimate. With a smaller `gamma`, two observation periods in a row without an occupied slot, as during a halt of block production, let the total active stake exceed 2.097 times the estimate. A change of `K` or of its targets requires `gamma` to be derived again (see [The stake inference](https://github.com/logos-co/logos-lips/blob/master/docs/blockchain/raw/rfc/RFC-TBD-cryptarchia-shorten-the-epoch-to-60-hours.md#the-stake-inference) for the derivation). |
| `PERIOD` | $`4K`$ | observation period | The length of the observation period in slots. |
| `f` | *inherited from* [Constants](cryptarchia-v1-protocol.md#constants) | slot activation coefficient | The target rate of occupied slots. Not all slots contain blocks, many are empty. |
| `K` | *inherited from* [Constants](cryptarchia-v1-protocol.md#constants) | finality window | The parameter from which `PERIOD` is derived. |

### Functions

- $`\textbf{density\_over\_slots}(c, s, p)`$
  *Returns the number of distinct occupied slots of the chain ending in block* $`c`$ *among the* $`p`$ *slots starting at slot* $`s`$*: a slot in* $`[s, s+p)`$ *counts if it holds a block of the chain and/or one or more* [uncles](cryptarchia-v1-protocol.md#uncle-references) *referenced by the blocks of the chain that lie in* $`[s, s+p)`$ *themselves, and each slot is counted at most once — a slot that holds both a canonical block and a referenced uncle, or several referenced uncles, still counts once. A block outside the range contributes neither its own slot nor the slots of the uncles it references, so the value for a past range is closed once that range ends.*

## Algorithm

For the tip `tip` of the chain the estimate is derived on, a current epoch’s estimate `total_stake_estimate` and the epoch’s first slot `epoch_slot`, the next epoch’s estimate is calculated as shown below:

```rust
const PRECISION: u64 = 1e3
fn total_stake_inference(tip: Block, total_stake_estimate: u64, epoch_slot: u64) -> u64 {
    // beta.num: u64, beta.den: u64
    // gamma.num: u64, gamma.den: u64
    // f: f64
    // PERIOD: u64
    // density_over_slots(Block, u64, u64) -> u64

    let f_p: u64 = truncate(f * PRECISION)
    let tse_p: u64 = total_stake_estimate * PRECISION

    let measured_density_p: u64 = density_over_slots(tip, epoch_slot, PERIOD) * PRECISION
    let expected_density_p: u64 = PERIOD * f_p
    let density_diff_p: i128 = (expected_density_p as i128) - (measured_density_p as i128)
        let slot_activation_error_p: i128 = (tse_p * density_diff_p) / (expected_density_p as i128)
        let correction_p: i128 = (beta.num as i128 * slot_activation_error_p) / (beta.den as i128);
        let retained_p: i128 = (gamma.num as i128 * tse_p as i128) / (gamma.den as i128);
        let new_total_stake_estimate = max(tse_p - correction_p, retained_p) / PRECISION;

        max(new_total_stake_estimate, 1) as u64
}
```

# Annex

[\[Analysis\] Total Stake Inference](analysis-total-stake-inference.md)
