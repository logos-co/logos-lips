# BLOCK-REWARDS

| Field | Value |
| --- | --- |
| Name | Block Rewards |
| Slug | 199 |
| Status | raw |
| Category | Standards Track |
| Editor | Frederico Teixeira <frederico@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/block-rewards.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-24 |
| 1.1.0 | Changing from burning/minting to pooling/distributing/releasing, removing $`S_{tge}`$ | 2026-08-25 |
| 1.2.0 | Count the proof of work reward pool as a fourth controlled stock, bound net circulating growth by the two stocks that drain, and state that the pooled fee is net of the share diverted to that pool | 2026-08-31 |
| 1.3.0 | Compute the reward of a block from the fees pooled in that block, with a time step of one block | 2026-10-07 |

> Disclaimer:
> This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.
>
> All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein. 
>
> Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.

# Introduction

This document specifies how many tokens each block of the Logos Blockchain distributes as rewards. The reward of a block combines two sources: a release from the LGO rewards reserve allocated at genesis, and the transaction fees pooled in the block, paid back out. An emission rate factor, driven by network Key Performance Indicators (KPIs), sets the balance between the two.

The two KPIs are the inferred total stake, as a security indicator, and the fee pooling rate of the block, to keep the supply in equilibrium. The resulting model has the following properties:

- The release from the reserve is higher while the stake is below its target, to bootstrap network participation, and is capped at $`1\%`$ of the maximum supply per year.
- The release from the reserve decreases as the pooled fees grow, so that block rewards are funded primarily by the fees in the long run.
- No token is ever minted: the reward moves tokens between the reserve, the rewards pool and the circulating supply.

How the reward of a block is divided between the block leader and the Blend service is specified in [Blend Service and Consensus Leaders](overview-cryptoeconomics.md#blend-service-and-consensus-leaders).

# Overview

## Key Principles

- Fee pooling: All transaction fees (execution base fees and permanent storage fees) are collected into a rewards pool, rather than directly given to block proposers.
- Reserve release: The rewards are topped up by releasing tokens from a reserve pre-allocated from the fixed supply cap, not by minting.
- KPI driven: The balance between the reserve release and the pooled fees is computed at each block from the inferred total stake and the fees pooled in that block.

## High-level System Design

The system adjusts the reserve release based on two KPIs:

- Inferred Total Stake: Measures network security by tracking the total amount staked against a target threshold ($`30\%`$ of the maximum supply).
- Pooling Rate: Tracks the transaction fees (both Execution base fees and Permanent Storage fees) routed to the rewards pool by the block.

A control function combines these KPIs into the emission rate factor, bounded between a minimum and a maximum annual reserve release. This ensures that:

- When security participation is below target, a higher reserve release attracts more validators.
- As usage increases and fees are pooled, the reserve release adjusts downward and the distribution of pooled fees rises to stabilize the circulating supply.

TODO: update
![Block rewards high-level system design](block-rewards/assets/high-level-system-design.png)

The reward of the block $`t`$ is given by:

$$
R_t = A_t \cdot I_{max} \cdot S_{cap} \cdot \Delta_t + (1-A_t) \cdot R_\text{block}
$$

where $`A_t`$ is the emission rate factor, $`I_{max} \cdot S_{cap} \cdot \Delta_t`$ the maximum reserve release of a block and $`R_\text{block}`$ the fees pooled in the block.

## Lifecycle Phases

The system is designed to evolve through different phases:

- Bootstrap Phase: Initially higher emission rates (up to $`1\%`$ annually) to incentivize network participation when stake is below target. This is viable even when Logos Blockchain experiences low activity because the level of activity only plays a role when the network participation gets close to the predefined target.
- Stabilization Phase: As Proof-of-Stake (PoS) participation approaches target levels, emission becomes primarily driven by the fee pooling rate.
- Equilibrium Phase: Circulating supply stabilizes as distribution from the pool matches pooled fees and the reserve release approaches zero.
- High-Adoption Phase: If the fee pooling rate exceeds the maximum reserve release rate, circulating supply contracts as the pool accumulates faster than tokens are released. Total supply is unchanged.

## Benefits

This KPI-based approach delivers several advantages:

- Self-regulating mechanism that automatically adjusts to network conditions.
- Bounded supply growth: the reserve release never exceeds $`I_{max}`$ of the maximum supply per year, and net circulating growth is bounded by the reserve and the proof of work reward pool allocated at genesis.
TODO: update the simulation for the per block pooling rate
- Long-term sustainability with projected net circulating-supply growth of just $`1.33\%`$ after $`10`$ years (assuming constant pooling rate of $`0.5\%`$ per year).
- Predictable economic model that balances security incentives with controlled supply.

# Construction

## Parameters

| Symbol | Definition | Value | Explanation |
| --- | --- | --- | --- |
| $`S_{cap}`$ | Maximum token supply (hard cap) | 10 billion LGO | N.A. |
| $`\Delta_t`$ | Fraction of a year in one block | $`1/(365 \times 2880)`$ | One block every $`30`$ seconds; there are 2880 blocks of 30 seconds in a day. |
| $`I_{max}`$ | The maximum emission rate per year | $`1\%`$ | This value guarantees that, when the total inferred stake reaches $`D_{0,target}`$, then the APY for validation is ~3.33%. |
| $`I_{min}`$ | The minimum emission rate per year | $`0\%`$ | This avoids inflationary token emissions. |
| $`Y`$ | Lifetime of the rewards reserve at the maximum release rate ($`I_{max}`$ of $`S_{cap}`$ per year) | $`10`$ years | Sets the reserve size $`B_0 = I_{max} \cdot S_{cap} \cdot Y = 10^9`$ LGO ($10\%$ of $`S_{cap}`$). |
| $`D_{0,target}`$ | Target value of the inferred total stake | 3 billion LGO | $`30\%`$ of the maximum supply. |
| $`D_{1,target}`$ | Normalizer of the pooling rate | 10 billion LGO | The maximum supply. |
| $`\alpha_d`$ | Control responsiveness to the stake deviation | $`1/4`$ | See [\[Analysis\] Block Reward Parameter Calibration](analysis-block-reward-parameter-calibration.md), for details. |
| $`\alpha_a`$ | Control responsiveness to the pooling rate | $`1`$ | This parameter scales the reserve-release response to the pooling rate. It must be one-to-one. |

The calibration of these parameters can be found in [\[Analysis\] Block Reward Parameter Calibration](analysis-block-reward-parameter-calibration.md).

The following values are read at block $`t`$:

- $`D_{0,t}`$ is the inferred total stake of the epoch of the block ([Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference)).
- $`D_{1,t} = R_\text{block}`$ is the amount of Execution base fees and Permanent Storage fees collected in the block and routed to the rewards pool, net of the share diverted to the [Proof of Work Reward Pool](overview-cryptoeconomics.md#proof-of-work-reward-pool). Refer to [Execution Market](execution-market.md) and [Storage Markets](storage-markets.md) for how the fees are computed.

## Emission Rate Factor Function

The emission rate factor $`A_t \in [0,1]`$ determines the portion of $`I_{max}`$ released from the reserve at block $`t`$:

$$
A_t = \min \lbrace 1, \max \lbrace 0, \dfrac{ \alpha_d \cdot \delta_t + \alpha_a \cdot \gamma_t + I_{min}}{I_{max}} \rbrace \rbrace
$$

where $`\delta_t`$ is the deviation of the inferred total stake from its target and $`\gamma_t`$ is the annualized pooling rate of the block:

$$
\delta_t = \dfrac{D_{0,target} - D_{0,t}}{D_{0,target}}, \qquad
\gamma_t = \dfrac{1}{\Delta_t} \cdot \dfrac{D_{1,t}}{D_{1,target}}.
$$

All terms are expressed in annualized form to ease comparison. It implies that:

- $`\delta_t \gt 0`$ → stake below target → the release increases by $`\alpha_d \cdot \delta_t`$.
- $`\delta_t \lt 0`$ → stake above target → the release decreases by $`\alpha_d \cdot \delta_t`$.
- $`\gamma_t \gt 0`$ → fees are pooled → the release increases by $`\alpha_a \cdot \gamma_t`$, complementing the share of the pooled fees not paid back.

## Block Rewards

The reward of the block $`t`$ is:

$$
R_t = A_t \cdot I_{max} \cdot S_{cap} \cdot \Delta_t + (1-A_t) \cdot R_\text{block}
$$

The following behavior is expected:

- When the KPIs are far from their targets, $`A_t \rightarrow 1`$, the reward is the maximum reserve release of a block $`I_{max} \cdot S_{cap} \cdot \Delta_t`$, and the pool keeps the fees of the block.
- When the KPIs are close to their targets, $`A_t \rightarrow 0`$, the reserve release vanishes and the reward is the fees pooled in the block, paid back.

Rearranging the equation isolates the role of the reserve release:

$$
R_t = R_\text{block} + A_t \cdot \left( I_{max} \cdot S_{cap} \cdot \Delta_t - R_\text{block} \right).
$$

In the bootstrap regime, where activity is low and $`R_\text{block} \lt I_{max} \cdot S_{cap} \cdot \Delta_t`$, the reserve release raises the reward above the pooled fees. If the pooled fees exceed the release cap, the second term is non-positive and the pool keeps part of the fees.

## Pool Accounting and Supply Dynamics

The reserve holds tokens pre-allocated from the fixed cap $`S_{cap}`$ at genesis. It is sized so that releasing at the maximum rate $`I_{max}`$ of $`S_{cap}`$ per year lasts $`Y`$ years, giving an initial balance $`B_0 = I_{max} \cdot S_{cap} \cdot Y`$.

The flows of block $`t`$ are:

- Fee inflow to the pool: $`R_\text{block}`$.
- Reserve release: $`\iota_t = \min \lbrace A_t \cdot I_{max} \cdot S_{cap} \cdot \Delta_t, \; B_{t-1} \rbrace`$.
- Distribution, equal to the block reward: $`R_t = (1 - A_t) \cdot R_\text{block} + \iota_t`$.

The reserve balance $`B_t`$ and the pool balance $`P_t`$ evolve as

$$
B_t = B_{t-1} - \iota_t, \qquad P_t = P_{t-1} + A_t \cdot R_\text{block}.
$$

The reserve is non-increasing and bounded below by zero. Once it is depleted, $`\iota_t = 0`$ and the reward reduces to $`(1 - A_t) \cdot R_\text{block}`$, funded entirely by pooled fees. The pool keeps the share $`A_t`$ of the fees of every block.

The mechanism conserves tokens. With $`S_t`$ the circulating supply, the controlled total $`S_t + P_t + B_t`$ is constant:

$$
\Delta S_t = R_t - R_\text{block}, \qquad \Delta P_t = A_t \cdot R_\text{block}, \qquad \Delta B_t = -\iota_t.
$$

A reserve release moves tokens from $`B_t`$ into circulation, routing a fee moves tokens from circulation into $`P_t`$, and the reward pays part of them back. Circulating supply $`S_t`$ rises as the reserve drains, and contracts whenever the fees of a block exceed its reward. This removes tokens from circulation, not from existence.

The [Proof of Work Reward Pool](overview-cryptoeconomics.md#proof-of-work-reward-pool) is a stock of the same kind, holding tokens allocated at genesis and topped up by the share of the fees diverted before they reach $`P_t`$, and paying them into circulation as claims are made. It joins the controlled total, which is $`S_t + P_t + B_t + W_t`$, writing $`W_t`$ for this pool, and is constant for the same reason: every movement is between stocks. Net circulating growth over the reserve's life is bounded by $`B_0 + W_0`$, the two stocks that begin full and drain into circulation.

## Key Performance Indicators

### KPI 1 - The Inferred Total Stake

Given the privacy features of Logos Blockchain and the fact that the token's maximum supply is known, the inferred total stake is the most appropriate indicator of the system's security. $`D_{0,target}`$ is the total stake considered secure, $`30\%`$ of the maximum supply.

The inferred total stake affects the emission rate through $`\delta_t`$, characterized by the plot below.

![Diagram](block-rewards/assets/cc1261aa-09df-82f0-ace9-81b7dd81a13a.png)

> <sub>Figure 1</sub>

When the blockchain starts, $`D_{0,t}`$ is very likely small compared to the target, so $`\delta_t`$ is close to $`1`$ (or $`100\%`$). As more stake participates in the PoS, $`\delta_t`$ diminishes, and oscillates around $`0`$ when $`D_{0,t}`$ oscillates around $`D_{0,target}`$.

The security level of the Logos Blockchain is defined by:

$$
\text{Security Level} = \dfrac{D_{0,target}}{S_{cap}}.
$$

### KPI 2 - The Pooling Rate

In the long run, Logos Blockchain should release only enough tokens to complement the pooled transaction fees, so that block rewards are funded primarily by distribution from the pool.

$`D_{1,target} = S_{cap}`$ is a normalizer: $`\gamma_t`$ is the pooling rate of the block, annualized and relative to the maximum supply, which makes it comparable with $`I_{max}`$.

# Deterministic Implementation

Block rewards affect consensus state, so their computation must be deterministic across all nodes. It must not rely on floating-point arithmetic, and is defined below with integers only.

With the parameters above, the two terms of the emission rate factor are:

$$
\frac{\alpha_d}{I_{max}}\delta_t = \frac{1/4}{10^{-2}} \cdot \frac{3\cdot 10^9 - D_{0,t}}{3\cdot 10^9} = \frac{3\cdot 10^9 - D_{0,t}}{12\cdot 10^7},
$$

$$
\frac{\alpha_a}{I_{max}}\gamma_t = \frac{1}{10^{-2}} \cdot (365 \cdot 2880) \cdot \frac{D_{1,t}}{10^{10}} = \frac{1261440 \cdot D_{1,t}}{12\cdot 10^7}.
$$

So $`A_t = A_t' / (12\cdot 10^7)`$ with

$$
A_t' = \min\!\lbrace12\cdot 10^7,\max\!\lbrace0,\; 3\cdot 10^9 - D_{0,t} + 1261440 \cdot D_{1,t}\rbrace\rbrace.
$$

The maximum reserve release of a block is

$$
I_{max} \cdot S_{cap} \cdot \Delta_t = \frac{10^{-2}\cdot 10^{10}}{365\cdot 2880} = \frac{62500}{657},
$$

so the reward of the block is

$$
R_t = \frac{62500\cdot A_t' + 657\cdot(12\cdot 10^7-A_t')\cdot D_{1,t}}{657\cdot 12\cdot 10^7},
$$

rounded down. The reference implementation is:

```python
A_SCALE: int64 = 120_000_000            # denominator of A_t
STAKE_TARGET: int64 = 3_000_000_000     # D_0_target
FEE_NUMERATOR: int64 = 1_261_440        # alpha_a / (I_max * D_1_target * Delta_t), over A_SCALE
RELEASE_NUMERATOR: int64 = 62_500       # numerator of I_max * S_cap * Delta_t
RELEASE_DENOMINATOR: int64 = 657        # denominator of I_max * S_cap * Delta_t


def block_reward(total_stake: uint64, pooled_fee: uint64) -> uint64:
    # Intermediates are int128: every product stays below 2**101,
    # and the reward, a weighted average of the release cap and
    # pooled_fee, fits back in a uint64.
    stake: int128 = total_stake
    fee: int128 = pooled_fee

    a_numerator: int128 = min(max(STAKE_TARGET - stake + FEE_NUMERATOR * fee, 0), A_SCALE)

    reward_numerator: int128 = (
        RELEASE_NUMERATOR * a_numerator
        + RELEASE_DENOMINATOR * (A_SCALE - a_numerator) * fee
    )
    return uint64(reward_numerator // (RELEASE_DENOMINATOR * A_SCALE))
```