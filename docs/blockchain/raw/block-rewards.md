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
| 1.2.0 | Block reward redefined as $`R_t = R^{\text{block}}_t + A_t c`$. Fee cap, fee split and excess capture removed; the reserve throttle removed and replaced by a solvency clamp. | 2026-09-12 |

> Disclaimer:
> This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.
>
> All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein. 
>
> Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.

# Introduction

This document specifies the block reward mechanism of Logos Blockchain: the amount of tokens paid at each block, the source of those tokens, and the state transitions the mechanism applies to the token stocks it controls.

The objective is a block reward that pays for security while the network is establishing it, and that hands the job to transaction fees as the network grows into them. The mechanism must remain defined when the pre-allocated reserve is close to exhausted while the security target is still unmet.

The design holds the token supply fixed. Block rewards are not minted. The fee component is recycled from the fees the block itself collected, the released component is drawn from a reserve allocated at genesis out of the hard cap, and the three stocks the mechanism controls sum to a constant at every block. Emission into circulation is bounded per block and per year, in every state and at any fee level.

The released component is anchored to one measured indicator, the inferred total stake, compared against a target. A block height tracks time but says nothing about chain state, and a per-transaction count is manipulable by the proposer. The release depends on nothing else. Fee revenue passes through the mechanism to the recipients without altering it, and the reserve balance enters only at the solvency boundary, where it bounds what can be released.

Fee computation and stake inference are out of scope. Refer to [Execution Market](execution-market.md) and [Storage Markets](storage-markets.md) for the fee amount, and to [Total Stake Inference](cryptarchia-total-stake-inference.md) for the stake estimate. Distribution to individual recipients is also out of scope. Refer to [Anonymous Leaders Reward Protocol](bedrock-anonymous-leaders-reward.md) for how the leader share is held and claimed, and to [Blend Protocol](blend-protocol.md) and [Service Reward Distribution Protocol](bedrock-service-reward-distribution.md) for the Blend share. This document only defines the amount transferred at each epoch boundary and its split between the two recipient classes. The Execution priority fee is outside that amount. It is routed in full to the leader class through the leader reward accumulator of the [Anonymous Leaders Reward Protocol](bedrock-anonymous-leaders-reward.md).

The properties this mechanism satisfies, its behaviour across the range of its state variables, the incentives it creates, its failure modes, and the trade-offs taken are derived in [\[Analysis\] Block Rewards](analysis-block-rewards.md). Results proved there are referenced from this document by the labels P for derived properties, S for scenarios, I for incentive results, and F for failure modes.

# Overview

## Terminology

The word "reward" denotes three distinct quantities in this document. Each is named explicitly wherever it appears to avoid misinterpretation.

| Term | Symbol | Definition |
| --- | --- | --- |
| Block reward | $`R_t`$ | The total amount accrued at block $`t`$. The outcome of the mechanism, and the sum of the two quantities below. |
| Block fees | $`R^{\text{block}}_t`$ | The gross Execution base fees and Permanent Storage fees collected in block $`t`$, passed through in full. Execution priority fees are excluded. |
| Released rewards | $`\iota_t`$ | The part drawn from the reserve pool, which is allocated at genesis out of the hard cap. |

$$
R_t = R^{\text{block}}_t + \iota_t.
$$

The distinction is economic, and it is also a difference in provenance. Block fees move from circulation into the rewards pool directly, recycling tokens the block itself collected. Released rewards move from the reserve pool into the rewards pool, drawing down an allocation made at genesis and expanding the circulating supply. The two components arrive at the same destination along different edges, as Figure 1 shows.

Neither component creates tokens, which is why [Derived Property P1](analysis-block-rewards.md#p1-conservation) holds.

Two neighbouring terms are not rewards:

* The **reserve pool** $`B_t`$ is the account that funds released rewards. It is allocated at genesis, has no inflow and exactly one outflow, so its balance moves by $`\Delta B_t = -\iota_t`$ and is non-increasing for the life of the chain.
* The **rewards pool** $`P_t`$ is the account in which block rewards accrue within an epoch before settlement. It receives both components of $`R_t`$ and pays out only at an epoch boundary.

## Key Principles

Four architectural constraints of Logos Blockchain determine the shape of the mechanism.

- **Unlinkability.** Block proposal and reward collection are decoupled, so a block reward cannot be assigned to an identified proposer.
- **Fee pooling.** Transaction fees are routed to a protocol reward pool rather than paid directly to a proposer.
- **Global metrics.** The block reward is a function of network-wide state observable at block production time, not of proposer-local or single-transaction data.
- **Epoch settlement.** Block rewards are computed per block but paid per epoch. The amount owed accrues over the blocks of an epoch and is transferred at the epoch boundary to the distribution protocols, which pay individual recipients.

The block reward is therefore an obligation accrued at block time and discharged at epoch time. The two schedules are distinct and the specification treats them separately.

## Requirements

The mechanism is specified to satisfy the following requirements. Each is discharged by a numbered result in [\[Analysis\] Block Rewards](analysis-block-rewards.md). The requirement is normative here; the proof that the mechanism meets it is in that document.

| | Requirement | Discharged by |
| --- | --- | --- |
| R1 | The token supply is fixed. The mechanism never mints. The stocks it controls are conserved under every state transition. | [Derived Property P1](analysis-block-rewards.md#p1-conservation) |
| R2 | The released component responds to measured network state instead of elapsed time. A larger deviation of the key performance indicator from its target produces a larger draw on the pre-allocated reserve. | [Key Performance Indicator](#key-performance-indicator), [Security Controller](#security-controller) |
| R3 | Released rewards are strictly positive whenever the security shortfall is positive **and the reserve is non-empty**. | [Derived Property P3](analysis-block-rewards.md#p3-block-reward-bounds-and-monotonicity), scoped by [Derived Property P7](analysis-block-rewards.md#p7-the-reserve-reaches-zero-in-finite-time) |
| R4 | The block reward is a continuous function of the state. No threshold produces a jump in the amount paid. | [Derived Property P6](analysis-block-rewards.md#p6-the-reserve-pool-covers-every-released-reward) |
| R5 | Gross emission into circulation is bounded per block and per year, in every state, independently of fee revenue. | [Derived Property P3](analysis-block-rewards.md#p3-block-reward-bounds-and-monotonicity) |
| R6 | No stock accumulates without a release rule. Any token withheld from a block reward is held in an account the mechanism can later draw on. | [Derived Property P2](analysis-block-rewards.md#p2-the-rewards-pool-accrues-within-an-epoch-and-discharges-at-the-boundary) |
| R7 | No participant profits from inflating the fees in a block. | [Incentive Analysis I1](analysis-block-rewards.md#i1-inflating-fees-is-not-profitable-but-its-effect-is-unbounded) |
| R8 | The consensus rule is integer-valued and deterministic across nodes. | [Float Precision for Implementation](#float-precision-for-implementation) |
| R9 | The obligation accrued over an epoch is discharged in full at the epoch boundary. The rewards pool retains no balance across epochs. | [Derived Property P2](analysis-block-rewards.md#p2-the-rewards-pool-accrues-within-an-epoch-and-discharges-at-the-boundary) |

R3 holds only over a bounded horizon. The reserve has no inflow, so a shortfall that persists long enough exhausts it and the released component goes to zero permanently. R3 is therefore a statement about the reserve's lifetime, not about all future states.

R9 separates accrual from payment. Without it the rewards pool balance would be a free variable and the conservation argument would not close at any single point in time.

## High-level System Design

The mechanism controls three token stocks:

* the circulating supply $`S_t`$,
* a reserve pool $`B_t`$ allocated at genesis, and
* a rewards pool $`P_t`$ that accrues the obligation within an epoch.

Every block, the block's Execution base fees and Permanent Storage fees move in full from circulation into the rewards pool, and the reserve pool releases $`\iota_t`$ into the rewards pool. At each epoch boundary the rewards pool is emptied into the distribution protocols. These are the only flows this mechanism applies, so $`S_t + P_t + B_t`$ is invariant under them. The Execution priority fee moves along a separate edge, from the payer to the leader reward accumulator.

![Block reward token flows](block-rewards/assets/token-flows.png)

> <sub>Figure 1. Token flows. Every edge is a transfer between existing stocks. Flows 1 and 2 occur at every block; flow 3 occurs only at an epoch boundary, when the rewards pool is emptied. The reserve pool has no inflow.</sub>

The amount accrued at block $`t`$ is

$$
R_t = R^{\text{block}}_t + A_t \cdot c ,
$$

the block's fees in full, plus a release from the reserve sized only by the security state:

- $`c = I_{max} S_{cap} \Delta_t / f`$ is the per-block release cap. It is the maximum draw on the reserve in one block, and it annualizes to $`I_{max} S_{cap}`$.
- $`A_t \in [0,1]`$ is the security controller. It responds to the shortfall of inferred total stake against target and to nothing else.

The two components are independent. Fees do not displace the release, and the release does not depend on fees. The mechanism is a fee pass-through plus a stake-driven subsidy.

## Lifecycle Phases

Let $`\theta_t`$ denote the security level. The regimes are keyed on $`\theta_t`$ and on the reserve balance. Fee revenue no longer selects a regime; it scales the reward within one. Each is evaluated in full in [Scenario Analysis](analysis-block-rewards.md#scenario-analysis).

- **Bootstrap.** $`\theta_t \le 25\%`$, so $`A_t = 1`$. The release is at $`c`$ every block, the reserve drains at its maximum rate, and the staking yield against a small base is high. [Scenario S1](analysis-block-rewards.md#s1-bootstrap)
- **Stabilization.** $`\theta_t \in (25\%, 30\%)`$. $`A_t`$ falls linearly with the shortfall, the release shrinks, and a growing share of the block reward is fees. [Scenario S3](analysis-block-rewards.md#s3-proportional-band)
- **Self-sustaining.** $`\theta_t \ge 30\%`$, so $`A_t = 0`$. Nothing is released, the reward is fees alone, and the reserve is frozen at its current balance rather than drained. The mechanism spends the reserve only in the states that call for it. [Scenario S2](analysis-block-rewards.md#s2-target-reached-no-usage), [Scenario S4](analysis-block-rewards.md#s4-high-adoption)
- **Terminal.** $`B_{t-1} = 0`$. The reserve is spent and the reward is fees alone from that block onward, whatever the security state. This state is absorbing: there is no inflow that can restore the reserve. [Scenario S5](analysis-block-rewards.md#s5-depleted-reserve-security-below-target), [Failure Mode F1](analysis-block-rewards.md#f1-terminal-reserve-exhaustion-and-the-yield-cliff)

The self-sustaining regime is reversible and the terminal regime is not. The difference between them is the subject of [Reserve Horizon and Terminal State](#reserve-horizon-and-terminal-state).

## Properties

Each claim below is a result proved in the analysis document.

- **Conservation.** $`S_t + P_t + B_t`$ is invariant at every block. The mechanism never mints. [Derived Property P1](analysis-block-rewards.md#p1-conservation)
- **Epoch discharge.** The rewards pool accrues within an epoch and returns to zero at the boundary. [Derived Property P2](analysis-block-rewards.md#p2-the-rewards-pool-accrues-within-an-epoch-and-discharges-at-the-boundary)
- **Bounded emission.** Released rewards are at most $`c`$ per block, that is $`I_{max} S_{cap}`$ per year, in every state and at any fee level. The bound is unconditional on fees rather than mediated by the fee gap. [Derived Property P3](analysis-block-rewards.md#p3-block-reward-bounds-and-monotonicity)
- **Unbounded block reward.** $`R_t`$ has no upper bound, since it contains the block's fees uncapped. No ceiling on $`R_t`$ may be assumed by downstream protocols. [Derived Property P3](analysis-block-rewards.md#p3-block-reward-bounds-and-monotonicity), [Failure Mode F5](analysis-block-rewards.md#f5-the-settled-reward-is-not-a-bounded-signal)
- **Separability.** The fee component and the released component are additively separable, with zero cross-partial. Fee revenue neither displaces nor triggers a release. [Derived Property P4](analysis-block-rewards.md#p4-the-two-components-are-additively-separable)
- **Monotone supply.** Circulating supply is non-decreasing epoch over epoch, and strictly increasing whenever $`A_t > 0`$ over the epoch. No fee level contracts it. [Derived Property P5](analysis-block-rewards.md#p5-closed-form-for-the-stock-dynamics)
- **Reserve solvency.** Released rewards never exceed the reserve pool balance, by the clamp in equation (2). [Derived Property P6](analysis-block-rewards.md#p6-the-reserve-pool-covers-every-released-reward)
- **Finite reserve horizon.** The reserve reaches zero in finite time under a persistent shortfall, and the terminal state is absorbing. [Derived Property P7](analysis-block-rewards.md#p7-the-reserve-reaches-zero-in-finite-time), [Derived Property P8](analysis-block-rewards.md#p8-reserve-horizon)
- **Manipulation resistance.** Inflating the fees in a block is never profitable for a participant whose combined share of the epoch settlement is below one. The recovered fraction is constant in the fee paid. [Incentive Analysis I1](analysis-block-rewards.md#i1-inflating-fees-is-not-profitable-but-its-effect-is-unbounded)
- **Minimal consensus state.** The rule reads the reserve pool balance, the stake estimate, the block's fees, the rewards pool balance and the epoch position. No fee window or history is maintained.

# Construction

## Core Variables

### Protocol constants

- $`S_{cap}`$ is the maximum allowable token supply (hard cap).
- $`\Delta_t`$ is the fraction of a year in one time step.
- $`f`$ is the average number of block proposals within $`\Delta_t`$.
- $`L`$ is the number of blocks in an epoch.
- $`I_{max}`$ is the maximum annual release rate, expressed as a fraction of $`S_{cap}`$.
- $`Y`$ is the lifetime, in years, of the reserve at release rate $`I_{max}`$.
- $`D_{target}`$ is the target inferred total stake.
- $`\Lambda`$ is the stake shortfall at which the security controller saturates, in tokens. Equivalently $`\delta^\ast = \Lambda / D_{target}`$, the same threshold as a normalized deviation.
- $`B_0 = I_{max} \cdot S_{cap} \cdot Y`$ is the initial reserve, allocated at genesis from $`S_{cap}`$.
- $`c`$ is the per-block release cap, in tokens.

The per-block release cap $`c`$ is derived as:

$$
c = \frac{I_{max} \cdot S_{cap} \cdot \Delta_t}{f} .
$$

$`c`$ has a single role: it is the maximum draw on the reserve in one block. It is not applied to fees.

Its calibration is a yield statement, but the reference base is the saturation boundary and not the target. The release is at $`c`$ only while $`A_t = 1`$, that is while $`D_t \le D_{target} - \Lambda`$. At $`D_t = D_{target}`$ the controller is zero, nothing is released, and the block reward is pure fee recycling, so no release-funded yield can be quoted there at all. The largest staked base still receiving the full release is therefore $`D_{target} - \Lambda`$, and over the saturated region the release-funded annual yield is

$$
r^{\iota}(D_t) = \frac{I_{max} S_{cap}}{D_t} \;\ge\; \frac{I_{max} S_{cap}}{D_{target} - \Lambda} ,
$$

which at the adopted parameters is at least $`4.0\%`$, on a base of $`2.5 \cdot 10^9`$ LGO, and rises without bound as the staked base falls. Across the proportional band the release-funded yield is $`A_t I_{max} S_{cap} / D_t`$, which falls monotonically from $`4.0\%`$ at $`\theta = 25\%`$ to zero at $`\theta = 30\%`$. [Failure Mode F1](analysis-block-rewards.md#f1-terminal-reserve-exhaustion-and-the-yield-cliff) tabulates $`r^{\iota}`$ across the range.

Epochs are indexed by $`e`$, and epoch $`e`$ spans the blocks $`t \in (T_{e-1}, T_e]`$ with $`T_e = e L`$.

Under a leader lottery the realized block count in an epoch is a random variable and $`L`$ is its expected value. The block reward accrues per block, so the amount settled at a boundary scales with the realized count. The annualized figures in this document assume the expected rate.

### State

- $`S_t`$ is the circulating supply.
- $`B_t`$ is the reserve pool balance. It funds every released reward and receives nothing.
- $`P_t`$ is the rewards pool balance. It accrues the block reward obligation within an epoch and is emptied at the boundary.
- $`D_t`$ is the inferred total stake at time $`t`$, the key performance indicator.
- $`R^{\text{block}}_t`$ is the gross amount of Execution base fees and Permanent Storage fees collected in block $`t`$. Execution priority fees are not included.

Consensus state read by this mechanism is $`(B_{t-1}, D_t, R^{\text{block}}_t)`$ to compute the block reward, and $`(P_{t-1}, t \bmod L)`$ to accrue and settle it. No window or fee history is required.

### Derived quantities

- $`\delta_t`$ is the normalized deviation of the key performance indicator from its target.
- $`A_t \in [0,1]`$ is the security controller.
- $`\iota_t = \min \lbrace A_t c, \; B_{t-1} \rbrace`$ is the released rewards, the part of the block reward drawn from the reserve.
- $`R_t = R^{\text{block}}_t + \iota_t`$ is the block reward, accrued at block $`t`$ into $`P_t`$.
- $`\Pi_e`$ is the epoch settlement amount, the total transferred to the distribution protocols at the boundary $`T_e`$.

## Parametrization

| Symbol | Definition | Value | Basis |
| --- | --- | --- | --- |
| $`S_{cap}`$ | Maximum token supply | $`10^{10}`$ LGO | Hard cap. |
| $`I_{max}`$ | Maximum annual release rate | $`1\%`$ | Sets the release-funded yield floor over the saturated region at $`I_{max} S_{cap} / (D_{target} - \Lambda) = 4.0\%`$, and the reserve at $`B_0 = I_{max} S_{cap} Y`$. Comparable to the annual supply growth of gold. |
| $`Y`$ | Reserve lifetime at $`I_{max}`$ | $`10`$ years | Sets $`B_0 = 10^9`$ LGO, $`10\%`$ of $`S_{cap}`$. Exact, not nominal: the reserve has no inflow, so $`Y`$ is the calendar lifetime under a saturated controller regardless of fee revenue. |
| $`\Delta_t`$ | Time step | $`1/(365 \cdot 2880)`$ | One block every 30 seconds. |
| $`f`$ | Block proposals per time step | $`1`$ | $`\Delta_t`$ chosen so $`f = 1`$. |
| $`c`$ | Per-block release cap | $`62500/657 \approx 95.129`$ LGO | Derived from the four rows above. |
| $`D_{target}`$ | Target inferred total stake | $`3 \cdot 10^9`$ LGO | $`\theta_{target} = 30\%`$. Chains with utility exhibit a negative relation between usage and staking ratio, so a target above $`50\%`$ is not appropriate; the lower end of the observed $`30\%`$ to $`50\%`$ band stops the release sooner. |
| $`\Lambda`$ | Stake shortfall at controller saturation | $`5 \cdot 10^8`$ LGO | Equivalently $`\delta^\ast = \Lambda / D_{target} = 1/6`$, so $`A_t = 1`$ below $`\theta = 25\%`$ and the proportional band runs from there to $`30\%`$. Jointly with $`I_{max}`$ it fixes the release-funded yield floor, since the base at saturation is $`D_{target} - \Lambda`$. |
| $`L`$ | Blocks per epoch | $`21600`$ | $`7.5`$ days at one block every 30 seconds. Sets the reserve-funded settlement float at $`L c = 2.055 \cdot 10^6`$ LGO, $`0.02\%`$ of $`S_{cap}`$. The fee-funded part of the float is unbounded by the protocol. |

## Key Performance Indicator

The mechanism uses the inferred total stake as a key performance indicator. It is measured at block production time, compared against a target, and the deviation drives the reserve release.

### Definition

$`D_t`$ denotes the inferred total stake, and $`D_{target}`$ the level considered secure. Refer to [Total Stake Inference](cryptarchia-total-stake-inference.md) for how $`D_t`$ is estimated from the observed rate of occupied slots.

Given the privacy properties of Logos Blockchain, individual stake is not observable, and given a known maximum supply, the inferred total stake is the available indicator of the system's security. The security level is

$$
\theta_t = \frac{D_t}{S_{cap}}, \qquad \theta_{target} = \frac{D_{target}}{S_{cap}} .
$$

### Deviation from Target

The mechanism responds to the deviation of the indicator from its target, normalized by the target:

$$
\delta_t = \frac{D_{target} - D_t}{D_{target}} = 1 - \frac{\theta_t}{\theta_{target}} \;\in\; (-\infty, \, 1] .
$$

- $`\delta_t > 0`$: stake below target. Released rewards are positive, in proportion to $`\delta_t`$.
- $`\delta_t = 0`$: stake at target. Nothing is released.
- $`\delta_t < 0`$: stake above target. Nothing is released, and the response is clamped rather than reversed, since the mechanism has no instrument for reducing stake.

At genesis $`D_t`$ is small against the target, so $`\delta_t \rightarrow 1`$ and the response is maximal. As participation grows, $`\delta_t`$ falls toward zero and the block reward converges on the block's fees.

The loop is closed: a larger deviation raises the block reward, a higher block reward raises the staking yield, and a higher yield attracts stake, which reduces the deviation. Fee revenue reinforces the same loop from the other side, since it adds to the yield without displacing the release.

## Security Controller

The controller is the normalized deviation of the key performance indicator, saturated at a threshold $`\delta^\ast`$ and clamped below at zero:

$$
A_t = \min \left\lbrace 1, \; \max \left\lbrace 0, \; \frac{\delta_t}{\delta^\ast} \right\rbrace \right\rbrace , \qquad \delta^\ast = \frac{\Lambda}{D_{target}} .
$$

$`\delta^\ast`$ is the deviation at which the response saturates and $`\Lambda`$ is the same threshold expressed in tokens. The two are one parameter in two units. Substituting $`\delta_t`$ gives the form used by the consensus rule, in which no division by $`D_{target}`$ appears:

$$
A_t = \frac{\min \lbrace \Lambda, \; \max \lbrace 0, \; D_{target} - D_t \rbrace \rbrace}{\Lambda} .
$$

Both forms are equivalent. The second is normative for implementation because $`\Lambda`$ is measured in tokens and can be compared directly against the stake shortfall.

The controller is piecewise linear in the indicator:

- $`\delta_t \le 0`$, that is $`D_t \ge D_{target}`$, implies $`A_t = 0`$. Stake is at or above target and no release is warranted.
- $`\delta_t \ge \delta^\ast`$, that is $`D_t \le D_{target} - \Lambda`$, implies $`A_t = 1`$. The deviation is at or beyond saturation and the release is maximal.
- Between the two, $`A_t`$ interpolates linearly, so the response is proportional to the measured deviation over the interval $`(0, \delta^\ast)`$.

$`\delta^\ast`$ therefore fixes the width of the proportional band. At $`\delta^\ast = 1/6`$ the band runs from $`\theta = 25\%`$ to $`\theta = 30\%`$, and $`A_t`$ is saturated below it.

## Block Rewards

The block reward is the block's fees plus a release from the reserve:

$$
\begin{equation}
R_t = R^{\text{block}}_t + A_t \cdot c .
\end{equation}
$$

The two terms are independent. The first is a pass-through of value the block already collected; the second is a subsidy sized only by how far the inferred total stake sits below target. Neither scales the other.

Equation (1) is the design statement. It is well defined only while the reserve can fund it, so the normative rule applies a solvency clamp:

$$
\begin{equation}
\iota_t = \min \lbrace A_t \cdot c, \; B_{t-1} \rbrace , \qquad R_t = R^{\text{block}}_t + \iota_t .
\end{equation}
$$

The clamp is not a design parameter. Without it the mechanism would debit more than the reserve holds and R1 would fail. It binds only in the final blocks of the reserve's life; at every earlier block $`A_t c \lll B_{t-1}`$ and equation (2) reduces to equation (1).

The clamp preserves R4. $`\min`$ of two continuous functions is continuous, so $`R_t`$ is continuous in $`D_t`$, in $`R^{\text{block}}_t`$ and in $`B_{t-1}`$, and no threshold produces a jump in the amount paid. What the clamp does not preserve is the asymptotic exhaustion of the reserve, that can reach zero exactly, in finite time, and the release stops there.

Bounds follow directly:

$$
R^{\text{block}}_t \;\le\; R_t \;\le\; R^{\text{block}}_t + c .
$$

The reward is bounded below by the fees and above by the fees plus the per-block release cap. It is not bounded above in absolute terms. The released component alone satisfies $`0 \le \iota_t \le c`$ in every state and at any fee level, which is what discharges R5.

### Reserve Horizon and Terminal State

The reserve is spent at $`\iota_t`$ per block and never replenished, so its horizon is determined at genesis by the path of the controller:

$$
B_t = B_0 - \sum_{s \le t} \iota_s , \qquad \sum_{s} \iota_s \;\le\; B_0 = I_{max} S_{cap} Y .
$$

Under a saturated controller, $`A_t = 1`$ at every block, the horizon is exactly $`B_0 / c = 1.0512 \cdot 10^7`$ blocks, that is $`Y = 10`$ years. Under a mean controller value $`\bar{A}`$ over the interval, the horizon is $`Y / \bar{A}`$ years, tabulated in [Derived Property P8](analysis-block-rewards.md#p8-reserve-horizon). The reserve is spent only in the states that call for it, so a chain that reaches its stake target early conserves the balance indefinitely; a chain that never reaches it spends the reserve in ten years.

Once $`B_t = 0`$ the state is absorbing, per [Derived Property P7](analysis-block-rewards.md#p7-the-reserve-reaches-zero-in-finite-time). Released rewards are zero from that block onward, the block reward is fees alone, and the mechanism has no instrument left if the stake subsequently falls below target. The release also stops abruptly rather than tapering: it falls from $`A_t c`$ to zero across two consecutive blocks, removing up to $`I_{max} S_{cap} / D_t`$ of annual staking yield at that instant. [Failure Mode F1](analysis-block-rewards.md#f1-terminal-reserve-exhaustion-and-the-yield-cliff) quantifies the cliff and evaluates the available mitigations.

## Accounting and Supply Dynamics

### Stock accounting

Two flows occur at every block. They are independent, and the order in which a node applies them does not matter.

$$
\text{1. Block fees:} \quad R^{\text{block}}_t: \; S_t \rightarrow P_t , \qquad
\text{2. Released rewards:} \quad \iota_t: \; B_t \rightarrow P_t .
$$

$$
S_t = S_{t-1} - R^{\text{block}}_t + \Pi_e \cdot \mathbb{1} \lbrace t = T_e \rbrace ,
$$

$$
B_t = B_{t-1} - \iota_t ,
$$

$$
P_t = P_{t-1} + R^{\text{block}}_t + \iota_t - \Pi_e \cdot \mathbb{1} \lbrace t = T_e \rbrace = P_{t-1} + R_t - \Pi_e \cdot \mathbb{1} \lbrace t = T_e \rbrace .
$$

Each account has one role. The reserve pool funds released rewards and nothing else; it never touches the fees. The rewards pool receives both components of the block reward and pays out only at a boundary. Circulating supply loses the block's fees during the epoch and regains the settlement amount at the boundary.

The only debit from the reserve pool is $`\iota_t`$, and the clamp in equation (2) bounds it by $`B_{t-1}`$ unconditionally, so $`B_t \ge 0`$ holds at every block. No flow ordering constraint is required.

R6 is satisfied trivially. The reserve pool never accumulates, since it has no inflow, and the rewards pool is emptied at every boundary by R9. There is no stock in which value can build up without a release rule, because there is no stock that builds up.

### Supply dynamics

Over epoch $`e`$ the circulating supply loses the epoch's fees and regains the settlement, which is the epoch's fees plus the epoch's releases. Netting the two,

$$
S_{T_e} - S_{T_{e-1}} = \sum_{t = T_{e-1}+1}^{T_e} \iota_t \;\ge\; 0 .
$$

Circulating supply is non-decreasing epoch over epoch and strictly increasing whenever any block in the epoch carries a positive release. Total net emission over the life of the chain is bounded by $`B_0 = 10^9`$ LGO, that is $`10\%`$ of $`S_{cap}`$, and is reached only if the shortfall persists for the full horizon.

### Epoch settlement

At the last block of epoch $`e`$ the rewards pool is emptied. The settlement amount is the sum of the block rewards accrued over the epoch,

$$
\Pi_e = \sum_{t = T_{e-1}+1}^{T_e} R_t ,
$$

and it is transferred out of $`P`$ and split between the two recipient classes, with the residual assigned so that the parts sum to the whole:

$$
\Pi^{blend}_e = \left\lfloor \frac{3 \, \Pi_e}{5} \right\rfloor, \qquad \Pi^{leader}_e = \Pi_e - \Pi^{blend}_e .
$$

$`\Pi^{blend}_e`$ passes to the Blend distribution and $`\Pi^{leader}_e`$ to the leader reward pool. Both are outside this specification; refer to the protocols listed in the [Introduction](#introduction). The two components are settled on different downstream schedules, which does not affect the accounting here: from the perspective of this mechanism both leave $`P`$ at $`T_e`$.

Splitting at the epoch aggregate rather than per block reduces the truncation residual from one base unit per block to one per epoch, a factor of $`L`$.

Immediately after settlement $`P_{T_e} = 0`$. This is the only instant at which the rewards pool balance is known without reference to the epoch's history, and it is the point at which the three-stock identity reduces to two, per [Derived Property P2](analysis-block-rewards.md#p2-the-rewards-pool-accrues-within-an-epoch-and-discharges-at-the-boundary).

# Float Precision for Implementation

Block rewards affect consensus state, so the normative rule is defined in integer arithmetic. All quantities are in base units, $`1`$ LGO $`= 10^{d}`$ base units with $`d = 18`$. No floating point, no machine-epsilon comparison, and no rounding-mode dependence appears in the rule. This discharges R8.

## Constants

$$
c^{\ast} = \left\lfloor \frac{62500 \cdot 10^{d}}{657} \right\rfloor, \quad
\Lambda^{\ast} = 5 \cdot 10^{8} \cdot 10^{d}, \quad
M = 2^{32} .
$$

$`M`$ is the fixed-point scale of the controller. $`c^{\ast}`$ replaces the exact rational $`c`$; the truncation is below one base unit, that is $`10^{-18}`$ LGO.

## Rule

$$
a_t = \left\lfloor \frac{\min \lbrace \Lambda^{\ast}, \; \max \lbrace 0, \; D_{target} - D_t \rbrace \rbrace \cdot M}{\Lambda^{\ast}} \right\rfloor ,
$$

$$
\iota_t = \min \left\lbrace \left\lfloor \frac{a_t \cdot c^{\ast}}{M} \right\rfloor, \; B_{t-1} \right\rbrace , \qquad
R_t = R^{\text{block}}_t + \iota_t .
$$

The fee term enters exactly, with no scaling and no floor, so all approximation error in $`R_t`$ is confined to the released component. The state update is then

$$
B_t = B_{t-1} - \iota_t, \qquad P_t = P_{t-1} + R_t, \qquad S_t = S_{t-1} - R^{\text{block}}_t ,
$$

in any order, and at $`t = T_e`$ additionally

$$
\Pi_e = P_t, \qquad \Pi^{blend}_e = \left\lfloor \frac{3 \Pi_e}{5} \right\rfloor, \qquad \Pi^{leader}_e = \Pi_e - \Pi^{blend}_e, \qquad P_t \leftarrow 0 .
$$

The clamp against $`B_{t-1}`$ is applied after the multiplication and floor, on a quantity already bounded by $`c^{\ast}`$, so it cannot overflow.

## Bit width

The largest intermediate is $`\max \lbrace \Lambda^{\ast} M, \; M c^{\ast} \rbrace = \Lambda^{\ast} M = 2.15 \cdot 10^{36}`$, which fits in `u128` with a factor of $`158`$ of headroom. `u64` is insufficient by seventeen orders of magnitude. Any change to $`\Lambda`$ or $`M`$ must preserve

$$
\max \lbrace \Lambda^{\ast} M, \; M c^{\ast} \rbrace < 2^{128} .
$$

The rewards pool accumulator is no longer bounded by a protocol constant, because the fee component of $`R_t`$ is uncapped. Its reserve-funded part is at most $`L c^{\ast} \approx 2.06 \cdot 10^{24}`$ base units, and the only bound on the total is the conservation bound $`P_t \le S_{cap}^{\ast} = 10^{28}`$ base units. `uint128` accommodates the latter with eleven orders of magnitude to spare; `uint64` does not accommodate either.

## Reference

```python
DECIMALS = 18
ONE = 10 ** DECIMALS

CAP      = 62_500 * ONE // 657        # c*
LAMBDA   = 500_000_000 * ONE          # Lambda*
D_TARGET = 3_000_000_000 * ONE
M        = 1 << 32
L        = 21_600                     # blocks per epoch


def released(total_stake: int, reserve: int) -> int:
    """Released rewards for this block: A_t * c, clamped by the reserve balance."""
    # security controller, scaled by M
    shortfall = D_TARGET - total_stake
    if shortfall < 0:
        shortfall = 0
    elif shortfall > LAMBDA:
        shortfall = LAMBDA
    a = shortfall * M // LAMBDA

    iota = a * CAP // M
    return iota if iota < reserve else reserve


def block_reward(total_stake: int, gross_fees: int, reserve: int) -> int:
    """The block reward accrued at this block: fees in full, plus the release."""
    return gross_fees + released(total_stake, reserve)


def apply_block(state, height, total_stake, gross_fees):
    """State transition. The two block flows are independent, so a node may
    apply them in any order."""
    iota = released(total_stake, state["B"])
    R = gross_fees + iota

    state["S"] -= gross_fees                   # 1. R^block: S -> P
    state["P"] += gross_fees
    state["B"] -= iota                         # 2. iota   : B -> P
    state["P"] += iota

    if height % L == 0:                        # 3. settlement at the boundary
        Pi = state["P"]
        blend = Pi * 3 // 5
        leader = Pi - blend
        state["P"] = 0
        state["S"] += Pi
        return R, (Pi, blend, leader)
    return R, None
```

`blend` passes to the Blend distribution and `leader` to the leader reward pool; both are outside this specification.
