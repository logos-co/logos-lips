# CRYPTARCHIA-TOTAL-STAKE-INFERENCE

| Field | Value |
| --- | --- |
| Name | Cryptarchia Total Stake Inference |
| Slug | 94 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <davidrusu@status.im> |
| Contributors | Alexander Mozeika <alexander.mozeika@status.im>, Daniel Kashepava <danielkashepava@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-total-stake-inference.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document defines the total stake inference algorithm for Cryptarchia.
In proof-of-stake consensus protocols,
the probability that an eligible participant wins the right to propose a block
depends on that participant's stake relative to the total active stake.
Because leader selection in Cryptarchia is private,
the total active stake is not directly observable.
Instead, nodes must infer it from observable chain growth.

**Keywords:** Cryptarchia, stake inference, proof-of-stake, epoch,
slot occupancy, leadership lottery

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Background

The total active stake can be inferred by observing the slot occupancy rate:
a higher fraction of occupied slots implies more stake participating in consensus.
By observing the rate of occupied slots from the previous epoch
and knowing the total stake estimate used during that period,
nodes can infer a correction to the total stake estimate
to compensate for any changes in consensus participation.

This inference process is done by each node following the chain.
Leaders will use this *total stake estimate* to calculate their *relative stake*
as part of the leadership lottery *without revealing their stake* to others.

The stake inference algorithm adjusts the previous total stake estimate
based on the difference between the empirical slot activation rate
(measured as the growth rate of the honest chain)
and the expected slot activation rate.
A large difference serves as an indicator
that the total stake estimate is not accurate and must be adjusted.

This algorithm has been analyzed and shown to have good accuracy,
precision, and convergence speed.
A caveat to note is that accuracy decreases with increased network delays.
The analysis can be found in [Total Stake Inference Analysis][stake-analysis].

## Construction

### Parameters and Variables

#### beta (learning rate)

- **Value:** 1.0
- **Description:** Controls how quickly the algorithm adjusts to new participation levels.
  Lower values for `beta` give a more stable/gradual adjustment,
  while higher values give faster convergence but at the cost of less stability.

#### PERIOD (observation period)

- **Value:** ⌊6k/f⌋
- **Description:** The length of the observation period in slots.

#### f (slot activation coefficient)

- **Value:** inherited from [Cryptarchia v1 Protocol][cryptarchia-v1]
- **Description:** The target rate of occupied slots.
  Not all slots contain blocks, many are empty.

#### k (security parameter)

- **Value:** inherited from [Cryptarchia v1 Protocol][cryptarchia-v1]
- **Description:** Block depth finality.
  Blocks deeper than `k` on any given chain are considered immutable.

### Functions

#### density_over_slots

```python
def density_over_slots(s, p):
    """
    Returns the number of blocks produced in the p slots
    following slot s in the honest chain.
    """
```

### Algorithm

For a current epoch's estimate `total_stake_estimate`
and the epoch's first slot `epoch_slot`,
the next epoch's estimate is calculated as shown below:

```python
def total_stake_inference(total_stake_estimate, epoch_slot):
    period_block_density = density_over_slots(epoch_slot, PERIOD)
    slot_activation_error = 1 - period_block_density / (PERIOD * f)
    coefficient = total_stake_estimate * beta
    return total_stake_estimate - coefficient * slot_activation_error
```

## Security Considerations

### Stake Estimation Accuracy

The accuracy of the total stake inference depends on the observed slot occupancy rate.
Implementations SHOULD be aware of the following security considerations:

- **Network delays**: Accuracy decreases with increased network delays,
  as delayed blocks may not be included in density calculations.
- **Adversarial manipulation**: An adversary with significant stake
  could potentially influence the slot occupancy rate by withholding blocks.
- **Convergence period**: During periods of rapid stake changes,
  the estimate may lag behind the actual total stake.

### Privacy Considerations

The stake inference algorithm is designed to maintain leader privacy:

- Leaders calculate their relative stake locally
  using the shared total stake estimate.
- Individual stake amounts are never revealed to the network.
- The algorithm relies only on publicly observable chain growth,
  not on private stake information.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [Cryptarchia v1 Protocol][cryptarchia-v1]
  \- Protocol specification defining `f` and `k` constants

[cryptarchia-v1]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification-22d261aa09df80c4a0a1f8af0ddf65ca

### Informative

- [Total Stake Inference](https://nomos-tech.notion.site/Total-Stake-Inference-22d261aa09df8051a454caa46ec54b34)
  \- Original Total Stake Inference documentation
- [Total Stake Inference Analysis][stake-analysis]
  \- Analysis of algorithm accuracy, precision, and convergence speed

[stake-analysis]: https://nomos-tech.notion.site/Total-Stake-Inference-Analysis-237261aa09df800285cccbb00b3aeb0a
