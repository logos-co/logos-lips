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
| 1.1.0 | Changed `density_over_slots` to count **distinct occupied slots** instead of blocks, counting the slots of the [uncles](cryptarchia-v1-protocol.md#uncle-references) the honest chain references alongside those of its own blocks, due to updated [Cryptarchia Protocol](cryptarchia-v1-protocol.md). | 2026-08-06 |

# Introduction

As with any Proof of Stake (PoS) consensus protocol, the probability that an eligible Cryptarchia participant wins the right to propose a block depends on that participant’s stake relative to the total active stake. Because leader selection in Cryptarchia is private, the total active stake is not directly observable. Instead, nodes must infer it from observable chain growth.

# Overview

The total active stake can be inferred by observing the slot occupancy rate: a higher fraction of occupied slots implies more stake participating in consensus. By observing the rate of occupied slots from the previous epoch and knowing the total stake estimate used during that period, we can infer a correction to the total stake estimate to compensate for any changes in consensus participation. This inference process is done by each node following the chain. Leaders will use this *total stake estimate* to calculate their *relative stake* as part of the leadership lottery *without revealing their stake* to others.

The stake inference algorithm adjusts the previous total stake estimate based on the difference between the empirical slot activation rate (measured as the growth rate of the honest chain) and the expected slot activation rate. A large difference serves as an indicator that the total stake estimate is not accurate and must be adjusted.

To measure the slot activation rate more accurately, the block count also includes the [uncle blocks](cryptarchia-v1-protocol.md#uncle-references) referenced by the honest chain. An uncle is a genuine lottery win, backed by a valid Proof of Leadership, that was lost to a fork instead of becoming part of the honest chain. Each block may reference several uncles, and the same uncle may be referenced by more than one block; the count is taken over distinct occupied slots, so each slot — whether occupied by a canonical block, a referenced uncle, or both — is counted only once. Without uncle references, these occupied slots would not be observed and the inference would underestimate the participation. Every referenced uncle contributes to the count: the signed headers are carried with the referencing blocks, and their validity is a condition of those blocks' own validity, so an uncle present in the chain has already been verified and every node holding the chain counts exactly the same set. Since forks are predominantly caused by network delays, counting referenced uncles also mitigates the accuracy loss under increased network delays noted below.

This algorithm has been analyzed and shown to have good accuracy, precision and convergence speed. A caveat to note is that accuracy decreases with increased network delays. The analysis can be found in [\[Analysis\] Total Stake Inference](analysis-total-stake-inference.md).

# Construction

## Definitions

### Parameters and variables

| Symbol | Value | Name | Description |
| --- | --- | --- | --- |
| `beta` | 1.0 | learning rate | Controls how quickly we adjust to new participation levels.  Lower values for `beta` give a more stable / gradual adjustment, while higher values give faster convergence but at the cost of less stability. |
| `PERIOD` | $`6\lfloor \frac{k}{f} \rfloor`$ | observation period | The length of the observation period in slots. |
| `f` | *inherited from* [Constants](cryptarchia-v1-protocol.md#constants) | slot activation coefficient | The target rate of occupied slots. Not all slots contain blocks, many are empty. |
| `k` | *inherited from* [Constants](cryptarchia-v1-protocol.md#constants) | security parameter | Block depth finality. Blocks deeper than `k` on any given chain are considered immutable. |

### Functions

- $`\textbf{density\_over\_slots}(s, p)`$
  *Returns the number of distinct occupied slots among the* $`p`$ *slots following slot* $`s`$*: a slot in* $`[s, s+p)`$ *counts if it holds a block of the honest chain and/or one or more* [uncles](cryptarchia-v1-protocol.md#uncle-references) *referenced by the honest chain, and each slot is counted at most once — a slot that holds both a canonical block and a referenced uncle, or several referenced uncles, still counts once.*

## Algorithm

For a current epoch’s estimate `total_stake_estimate` and the epoch’s first slot `epoch_slot`, the next epoch’s estimate is calculated as shown below:

```rust
const PRECISION: u64 = 1e3
fn total_stake_inference(total_stake_estimate: u64, epoch_slot: u64) -> u64 {
    // f: f64
    // PERIOD: u64
    // density_over_slots(u64, u64) -> u64

    let beta_p: u64 = truncate(beta * PRECISION)
    let f_p: u64 = truncate(f * PRECISION)
    let tse_p: u64 = total_stake_estimate * PRECISION

    let measured_density_p: u64 = density_over_slots(epoch_slot, PERIOD) * PRECISION
    let expected_density_p: u64 = PERIOD * f_p
    let density_diff_p: i128 = (expected_density_p as i128) - (measured_density_p as i128)
        let slot_activation_error_p: i128 = (tse_p * density_diff_p) / (expected_density_p as i128)
        let correction_p: i128 = (beta_p * slot_activation_error_p) / PRECISION;
        let new_total_stake_estimate = (tse_p - correction_p) / PRECISION;

        max(new_total_stake_estimate, 1) as u64
}
```

# Annex

[\[Analysis\] Total Stake Inference](analysis-total-stake-inference.md)
