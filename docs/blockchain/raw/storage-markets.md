# STORAGE-MARKETS

| Field | Value |
| --- | --- |
| Name | Storage Markets |
| Slug | 205 |
| Status | raw |
| Category | Standards Track |
| Editor | Juan Pablo Madrigal-Cianci <jp@logos.co> |
| Contributors | Frederico Teixeira <frederico@logos.co>, Filip Dimitrijevic <filip@logos.co>, Marcin Pawlowski <marcin@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/storage-markets.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-24 |
| 1.0.1 | [RFC] Remove Concept of a Session | 2026-06-22 |
| 1.0.2 | Fix invalid python indentation due to github migration | 2026-07-27 | 
| 1.1.0 | Round the price update upwards and align the reference code with the zero target guard | 2026-07-28 |
| 1.1.1 | Changing from burning/minting to pooling/distributing/releasing | 2026-08-25 |
| 1.2.0 | The storage fee is routed to the rewards pool less the share diverted to the proof of work reward pool | 2026-08-31 |

> **Disclaimer:**
> This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.
>
> All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein. 
>
> Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.

# Introduction

This document provides the formal specification for the fee collection mechanism of the Permanent Storage market. The primary objective is to define a system that is robust, predictable, and economically sustainable. This mechanism is a critical component of the overall Permanent Storage Market Transaction Fee Mechanism (TFM), a usage-driven market whose price formation is self-contained and independent of the protocol's core consensus and privacy services. The fees it collects are routed into the shared rewards pool that funds leader and Blend rewards, as detailed in [Fee Routing](#fee-routing) below.

In what follows, Logos Blockchain Storage refers to the Permanent Storage markets and Logos Blockchain Storage Gas refers to the Permanent Storage Gas respectively.

## Requirements and Rationale

The mechanism is designed with the following core requirements, derived from the project's goals:

- Predictability: Consumers of the Logos Blockchain Storage require a high degree of cost predictability for their own operational planning.
- Robustness: The mechanism must be able to adapt to significant, medium-term shifts in demand without requiring constant, emergency governance intervention.
- Fairness: The fee paid by a user must be directly and transparently proportional to the resources they consume.
- Simplicity: The on-chain implementation should be as simple as possible to minimize attack surface and ensure auditability.

Justification. As will be discussed later, the tradeoff between adaptability and predictability of the mechanism is determined by its parameters. In scenarios of high volatility, its core design principle is to act as a shock absorber, deliberately filtering out high-frequency, transient volatility by operating over longer timeframes and using a smoothed moving average (EMA). For the primary consumer, reacting to every momentary spike in demand would create untenable price chaos. This model, therefore, intentionally forgoes instantaneous adaptation in favor of providing crucial timeframe-level price certainty, ensuring that fees reflect meaningful, medium-term trends rather than reacting to volatile, short-term market noise.

# Overview

The proposed fee mechanism operates on a simple but powerful principle: the price for Logos Blockchain Storage is fixed and predictable within a given timeframe (epoch for Permanent Storage), but it adjusts smoothly between timeframes based on observed network usage.

When a user submits data, a fee is calculated based on the Logos Blockchain Storage Gas consumption. This fee is determined by a price per Gas, $`P_{storage}`$, which is known in advance for the entire timeframe. The collected fee is routed into the network's shared rewards pool, the same pool that funds block rewards (see [Fee Routing](#fee-routing)).

At the end of each timeframe, the protocol tallies the total amount of Logos Blockchain Storage Gas that was stored. It compares this actual usage to an adaptive target a "healthy" usage level that is itself a dynamic blend of a long-term policy goal and recent historical usage. Based on whether the actual usage was above or below this target, the price $`P_{storage}`$ for the next timeframe is adjusted slightly up or down.

This flow can be visualized as follows:

![Storage market lifecycle flow](storage-markets/assets/storage-market-lifecycle.svg)

This model provides the best of both worlds: users have perfect price clarity for the duration of a timeframe, while the system as a whole can gracefully adapt to evolving market conditions over time.

# Construction

This section defines the precise algorithm, constants, and state variables for the Logos Blockchain Storage TFM.

## Core Fee Equation

The fee for a Logos Blockchain Storage transaction, $`F_{\text{storage}}`$, is a linear function of Logos Blockchain Storage Gas' size, $`S_{\text{gas}}`$, and the price-per-gas for the current timeframe, $`P_{\text{storage}}(s)`$.

$$
F_{\text{storage}} = S_{\text{gas}} \cdot P_{\text{storage}}(s)
$$

As a remark, the equation above assumes a linear increase of $`F_\text{storage}`$ with respect to $`S_\text{gas}`$. For completeness, a more general version can be

$$
\begin{align*}
F_\text{storage}=f(S_\text{gas})\cdot P_\text{storage}
\end{align*}
$$

with $`f:\mathbb{N}\to\mathbb{R}_+`$ a monotonically increasing function. Making f sublinear can be understood as accounting for economies of scale, while making $f$ superlinear can be understood as a penalization for using larger data sizes. We decided to go with the linear form of $f$ as it was the least opinionated. Examples of this could be

$$
\begin{align*}
F_\text{storage}^\text{exp}&=\exp(\alpha S_\text{gas})\cdot P_\text{storage}\quad \alpha >0\\
F_\text{poly}^\text{exp}&=S^\beta_\text{gas}\cdot P_\text{storage},\quad \beta>1\\
\end{align*}
$$

### Fee Routing

Each Logos Blockchain Storage fee $`F_{\text{storage}}`$ is routed into the network's shared rewards pool at the moment its transaction is included, less the fixed share diverted to the [Proof of Work Reward Pool](overview-cryptoeconomics.md#proof-of-work-reward-pool), rather than paid to any participant or removed from supply. This is the same pool fed by the [Execution Market](execution-market.md) and drawn down to pay leaders and Blend nodes.

Aggregated over a block, the Storage fees of its transactions form the Storage-market component of the per-block pool inflow $`R_{block}`$ used to compute block rewards:

$$
\hat{R}_{\text{storage}} = \sum_{t \in \mathcal{B}} S_{\text{gas}}(t) \cdot P_{\text{storage}}(s) = P_{\text{storage}}(s) \sum_{t \in \mathcal{B}} S_{\text{gas}}(t),
$$

where $`\mathcal{B}`$ is the set of transactions in the block, $`S_{\text{gas}}(t)`$ is the Logos Blockchain Storage Gas consumed by transaction $t$, and $`P_{\text{storage}}(s)`$ is the fixed price of the enclosing timeframe $s$. The Execution market contributes the remaining component of $`R_{block}`$, the pooled base fees $`\hat{R}_{\text{pooled}}`$ (cf. [Execution Market](execution-market.md)), giving $`R_{block} = \hat{R}_{\text{storage}} + \hat{R}_{\text{pooled}}`$. This pooled inflow is distributed to leaders and Blend nodes through the reward mechanism of [Block Rewards](block-rewards.md). The Storage market governs only the price $`P_{\text{storage}}(s)`$; the routing and subsequent distribution of the resulting fee are defined by the block-reward mechanism.

### Protocol Constants

To ensure on-chain efficiency, the protocol shall use an Exponential Moving Average (EMA) for its adaptive target calculation. The behavior of the TFM is governed by the following on-chain constants, which are set at genesis.

| Symbol | Name | Description | Initial Value | Justification |
| --- | --- | --- | --- | --- |
| $`T_{\text{base}}`$ | Baseline Target | A static, policy-driven usage target in Logos Blockchain Storage Gas per timeframe. Acts as a long-term gravitational anchor for the dynamic target. | 0 Permanent Storage Gas per block. | It should represent a conservative initial timeframe capacity. providing a healthy buffer and a clear policy goal. |
| $w$ | Anchor Weight | A coefficient in $[0, 1]$ determining the influence of $`T_{\text{base}}`$. It's the "gravity knob" for the system. | for Permanent Storage: 0 | Allows the target to be primarily driven by recent demand, ensuring adaptability, while the $w$% pull from $`T_{\text{base}}`$ prevents long-term drift. |
| $\alpha$ | Max Adjustment Factor | The maximum fractional amount the price can change per timeframe. Acts as "safety brakes" to bound price volatility. | 0.125 for Permanent Storage | A $100\alpha$% cap provides strong predictability for users planning across timeframes while allowing the price to respond effectively to sustained demand changes. |
| $\beta$ | EMA Smoothing Factor | A coefficient in $[0, 1]$ controlling the responsiveness of the usage EMA. It governs the speed of adaptation. | 0.5 for Permanent Storage | A value of $\beta$ gives significant weight to the most recent timeframe's usage while incorporating the "memory" of the system with a half-life of 1 timeframe, balancing responsiveness and stability. |
| $`T_{\text{RA}}(-1)`$ | Initial Usage EMA | First value for EMA | 0 (=$`T_{\text{base}}`$) | Given $`T_{\text{base}} = 0`$, this is the least opinionated choice: with no prior usage data at genesis, a neutral prior of zero makes no assumption about initial market activity and anchors the EMA to the long-term policy goal from the outset. |
| $`P_{\text{storage}}(0)`$ | Initial Price | The price on the first epoch | 1 LGO/gas | The initial price is set conservatively low at the beginning and let to discover the true market price |
| $s$ | timeframe | How often things adjust | 1 epoch | Primary users of the Storage market plan operational costs over days or weeks, not block-by-block. |

### Parameter Justification

- For simplicity, we set $`T_\text{base}=0`$ as an anchor and $w=0$ as blocks are already constrained by execution. This is to avoid imposing an opinionated choice of parameters, specially at the beginning of the protocol.
- The EMA factor ($\beta=0.5$) makes the adaptive target highly sensitive to recent network activity by giving 50% weight to the latest epoch's usage, creating an effective "memory" of approximately 3 epochs.
- The maximum adjustment factor ($\alpha=0.125$) provides a crucial layer of predictability, guaranteeing users that the price cannot change by more than 12.5% between any two epochs, thus fulfilling a core design requirement for stable operational planning.
- The seed value for the EMA is set to $`T_{\text{RA}}(-1) = T_{\text{base}} = 0`$.  Given $`T_{\text{base}} = 0`$, this is the least opinionated choice: with no prior usage data at genesis, a neutral prior of zero makes no assumption about initial market activity and anchors the EMA to the long-term policy goal from the outset.
    > **Why is the index $-1$, not $0$?** The price update algorithm runs at the end of timeframe $s$ and requires $`T_{\text{RA}}(s-1)`$ as its prior EMA value. When $s = 0$, the algorithm therefore requires $`T_{\text{RA}}(-1)`$ as its seed. The value $`T_{\text{RA}}(0)`$ is already a well-defined computed quantity  the EMA produced after the first epoch's observed usage: $`T_{\text{RA}}(0) = \beta \cdot C_{\text{usage}}(0) + (1-\beta) \cdot T_{\text{RA}}(-1)`$. Using index $-1$ for the seed avoids a naming collision with this computed value. Implementation note. With $w = 0$ and $`T_{\text{RA}}(-1) = 0`$, the effective target $`T_{\text{effective}}`$ will be zero during the first epoch unless $`C_{\text{usage}}(0) \gt 0`$. The reference implementation handles this correctly via the `if usage == 0: return prev_price` guard, which holds the price at $`P_{\text{storage}}(0)`$ until the first non-zero usage epoch provides a meaningful signal. This is the intended behavior at genesis.
- The precise value of $`P_{\text{storage}}(0)`$ is not critical to the long-term behavior of the mechanism. As established in the equilibrium analysis, the price update rule converges autonomously to the market-clearing price $`P^*`$ regardless of the starting point, provided the stability condition $(*)$ holds (see [\[Analysis\] Storage Market - Price Stability Analysis](analysis-storage-market.md#price-stability-analysis)). The only hard requirement is for $`P_{\text{storage}}(0)`$ to be sufficiently low so as not to suppress early adoption before the mechanism has observed enough demand to self-correct.

    More precisely, since the price can increase by at most $\alpha = 12.5\%$ per epoch, the number
    of epochs required to reach a target price $`P^*`$ from an initial price $`P_{\text{storage}}(0) \lt P^*`$ is bounded above by $`N \leq \left\lceil \log_{1+\alpha}\!\left(\frac{P^*}{P_{\text{storage}}(0)}\right) \right\rceil = \left\lceil \frac{\ln(P^*/P_{\text{storage}}(0))}{\ln(1.125)} \right\rceil`$.
    
    For example, if $`P_{\text{storage}}(0)`$ is set to one tenth of the true equilibrium price, the mechanism reaches $`P^*`$ within at most $\lceil \ln(10)/\ln(1.125) \rceil = 20$ epochs. Starting
    one hundredth below requires at most $40$ epochs. Both are negligible relative to the expected lifetime of the network.
    We therefore set $`P_{\text{storage}}(0) = 1\ \text{LGO per Permanent Storage Gas}`$.

    This corresponds to a cost of 1 LGO per permanently stored byte. Genesis governance may adjust this value based on the LGO price at TGE, but the adjustment has no long-term consequence: the mechanism will converge to the true market price $`P^*`$ within $`O(\log P^*/P_{\text{storage}}(0))`$ epochs regardless.

- The timeframe $s$ corresponds to one epoch. The core reason is that the primary users of the Storage market plan operational costs over days or weeks, not block-by-block. An epoch-length timeframe provides price certainty over hundreds of blocks, directly fulfilling the predictability requirement. It also ensures the EMA aggregates a meaningful volume of usage data before influencing the price, rather than reacting to per-block noise.

### State Variables

The protocol must maintain the following state variables, updated at the end of each timeframe:

| Symbol | Name | Description |
| --- | --- | --- |
| $`P_{\text{storage}}(s)`$ | Price Per Logos Blockchain Storage Gas | The price per Gas of storage for the current timeframe $s$. |
| $`T_{\text{RA}}(s)`$ | Usage EMA | The Exponential Moving Average of storage usage, updated with the usage from timeframe $s$. |

### Price Update Algorithm

At the conclusion of each timeframe $s$, the protocol shall execute the following algorithm to determine the price for the next timeframe, $`P_{\text{storage}}(s+1)`$. This is done as follows.

 1. Tally Usage: Aggregate the total Logos Blockchain Storage Gas consumed during timeframe $s$ into a final value, $`C_{\text{usage}}(s)=\sum_{t\in\mathcal{B}_s}\mathsf{StorageGasUsed}[t]`$, where $`\mathcal{B}_s`$ corresponds to one block in timeframe $s$ and $`\mathsf{StorageGasUsed}[t]`$ corresponds to the Logos Blockchain Storage Gas used by transaction $t$.

 2. Update Usage EMA: Update the Exponential Moving Average of usage: $`T_{\text{RA}}(s) = \beta \cdot C_{\text{usage}}(s) + (1-\beta) \cdot T_{\text{RA}}(s-1)`$

 3. Calculate Effective Target: Calculate the blended, effective target, $`T_{\text{effective}}(s) = w \cdot T_{\text{base}} + (1-w) \cdot T_{\text{RA}}(s)`$

 4. Calculate Adjustment Factor: Determine the fractional deviation of usage from the target and clamp the result to the range $[-\alpha, \alpha]$:
 - $`\text{adjustment}(s) = \frac{C_{\text{usage}}(s) - T_{\text{effective}}(s)}{T_{\text{effective}}(s)}`$

- $`\mathrm{clampedAdjustment}(s)= \max\bigl(-\alpha,\,\min\bigl(\alpha,\, \mathrm{adjustment}(s)\bigr)\bigr)`$

 5. Update Price: Calculate the price for the next timeframe, $s+1$: $`P_{\mathrm{storage}}(s+1) = P_{\mathrm{storage}}(s) \cdot [1 + \mathrm{clampedAdjustment}(s)]`$

### Implementation

Because computation affect consensus state, the implementation must be fully deterministic across all nodes. For that reason, the normative implementation of the reward function should not rely on floating-point arithmetic, machine-dependent rounding behavior, or comparisons against machine epsilon. Earlier sections use real-valued formulas to explain the mechanism and its economic meaning, but the consensus rule itself should be defined only in terms of integer arithmetic.

The goal of this section is not to change the execution mechanism. It is only to restate the already-specified mechanism in a canonical deterministic form with explicit named constants. To we provide here a reference implementation that uses unsigned integers to have a common reference.

First because we have $w = 0$, $`T_\text{RA}(s) = T_\text{effective}(s)`$. Then because $\beta=0.5$

$$
T_{\mathrm{RA}}(s)=\frac{C_{\mathrm{usage}}(s)+T_{\mathrm{RA}}(s-1)}{2}
$$

Secondly, we can rewrite $`P_\text{storage}`$ equation:

$$
\begin{align*}
P_{\mathrm{storage}}(s+1)
&= P_{\mathrm{storage}}(s) \cdot
\left[1 + \max\bigl(-\alpha,\,
\min\bigl(\alpha,\, \mathrm{adjustment}(s)\bigr)
\bigr)\right]\\
&= P_{\mathrm{storage}}(s) \cdot
\max\bigl(1-\alpha,\,
\min\bigl(1+\alpha,\, 1+\mathrm{adjustment}(s)\bigr)
\bigr)\\
&= P_{\mathrm{storage}}(s)\cdot
\max\biggl(\frac78,\,
\min\biggl(\frac98,\,
\frac{C_{\mathrm{usage}}(s)}{T_{\mathrm{RA}}(s)}
\biggr)
\biggr)
\end{align*}
$$

and so:

$`P_{\mathrm{storage}}(s+1)=\begin{cases}P_{\mathrm{storage}}(s),& \text{if } T_{\mathrm{RA}}(s)=0,\\[6pt]\left\lceil P_{\mathrm{storage}}(s)\cdot \frac78 \right\rceil,& \text{if } 8\,C_{\mathrm{usage}}(s)\le 7\,T_{\mathrm{RA}}(s),\\[6pt]\left\lceil P_{\mathrm{storage}}(s)\cdot \frac98 \right\rceil,& \text{if } 8\,C_{\mathrm{usage}}(s)\ge 9\,T_{\mathrm{RA}}(s),\\[6pt]\left\lceil P_{\mathrm{storage}}(s)\cdot\frac{C_{\mathrm{usage}}(s)}{T_{\mathrm{RA}}(s)} \right\rceil,& \text{otherwise.}\end{cases}`$

The first case is the genesis guard discussed in the parameter justification: an effective target of zero carries no demand signal, so the price is held until the first epoch with a non-zero usage EMA. In the three adjustment cases the price is rounded upwards, while the usage EMA $`T_{\mathrm{RA}}(s)`$ is rounded downwards, and so we can derive the following reference code:

```python
EMA_DENOMINATOR = 2         # 1/beta
CLAMP_DENOMINATOR = 8       # denominator of 1+ alpha and 1-alpha
CLAMP_DOWN_NUMERATOR = 7    # numerator of 1-alpha
CLAMP_UP_NUMERATOR = 9      # numerator of 1+alpha

def ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator

def update_usage(total_gas_consumed: int, previous_usage: int) -> int:
    return (total_gas_consumed + previous_usage) // EMA_DENOMINATOR

def update_storage_price(prev_price: int, total_gas_consumed: int, usage: int) -> int:
    if usage == 0:
        return prev_price
    elif CLAMP_DENOMINATOR * total_gas_consumed <= CLAMP_DOWN_NUMERATOR * usage:
        return ceil_div(prev_price * CLAMP_DOWN_NUMERATOR, CLAMP_DENOMINATOR)
    elif CLAMP_DENOMINATOR * total_gas_consumed >= CLAMP_UP_NUMERATOR * usage:
        return ceil_div(prev_price * CLAMP_UP_NUMERATOR, CLAMP_DENOMINATOR)
    else:
        return ceil_div(prev_price * total_gas_consumed, usage)

def update_storage_fee(total_gas_consumed: int, prev_price: int, prev_usage: int) -> tuple[int, int]:
    usage = update_usage(total_gas_consumed, prev_usage)
    price = update_storage_price(prev_price, total_gas_consumed, usage)
    return price, usage
```

The two rounding directions are not interchangeable. The price is multiplied by a factor smaller than one whenever usage falls below the target, so rounding it downwards would make 0 an absorbing state: the initial price $`P_{\mathrm{storage}}(0)=1`$ would be mapped to 0 by the first downward adjustment, and every subsequent update would keep it at 0, making Permanent Storage permanently free. Rounding upwards makes 1 LGO per Permanent Storage Gas the effective floor of the price and leaves the mechanism unchanged at every other price level, as the rounding error is at most one unit against an adjustment of up to $\pm 12.5\%$. The usage EMA is a measurement rather than a price and is not subject to this failure mode, as it is additive and recovers from 0 as soon as usage resumes. Rounding it upwards would instead pin it at 1 once it has been positive, reporting residual demand on an idle market.

### Genesis State

The initial state of the TFM at network launch shall be configured as follows:

- Initial Price P_STR(0): Set to a pre-determined value established by genesis governance.
- Initial Usage EMA T_RA(-1): Set to the value of the baseline target, $`T_{\text{base}}`$. This anchors the mechanism to its long-term policy goal from the outset.
