# ANALYSIS-STORAGE-MARKET

| Field | Value |
| --- | --- |
| Name | [Analysis] Storage Market |
| Slug | 197 |
| Status | raw |
| Category | Informational |
| Editor | Juan Pablo Madrigal-Cianci <jp@logos.co> |
| Contributors | Frederico Teixeira <frederico@logos.co>, Filip Dimitrijevic <filip@logos.co>, Marcin Pawlowski <marcin@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/analysis-storage-market.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision | 2026-04-24 |
| 1.0.1 | [RFC] Remove Concept of a Session | 2026-06-22 |

> **Disclaimer:**
> This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.
>
> All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein. 
>
> Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.

# Introduction

This document provides a formal mathematical analysis of the proposed fee mechanism. We model the price update rule as a discrete-time dynamical system to evaluate its stability, long-term behaviour, and incentive properties rigorously.

# System Dynamics and Equilibrium

Let's define the state of the system at the end of timeframe $s$ by the price $`P_s`$ and the usage EMA, $`T_{\text{RA}, s}`$. The core of the mechanism is the price update rule:

$$
P_{s+1} = P_s \cdot \left(1 + \mathrm{clamped\_adjustment}(s)\right)
$$

Where the adjustment is a function of the timeframe's usage, $`C_s`$. For this analysis, let's assume usage $`C_s`$ is a function of the price, $`C(P_s)`$, where $`C' \lt 0`$ (demand decreases as price increases).

The system is in equilibrium when the price no longer changes between timeframes, i.e., $`P_{s+1} = P_s`$. This occurs if and only if the clamped_adjustment term is zero. This condition implies:

$$
C(P^{\ast}) = T_{\text{effective}}(P^{\ast})
$$

where $`P^{\ast}`$ is the equilibrium price. The effective target itself depends on the usage EMA, which at equilibrium will have stabilized such that $`T_{\text{RA}, s} = T_{\text{RA}, s-1} = C(P^{\ast})`$. Substituting this into the effective target equation:

$$
T_{\text{effective}}(P^{\ast}) = w \cdot T_{\text{base}} + (1-w) \cdot C(P^{\ast})
$$

Therefore, the equilibrium condition simplifies to:

$$
\begin{aligned}
C(P^{\ast}) &= w \cdot T_{\text{base}} + (1-w) \cdot C(P^{\ast})\\
w \cdot C(P^{\ast}) &= w \cdot T_{\text{base}}\\
\implies& {C(P^{\ast}) = T_{\text{base}}}
\end{aligned}
$$

Conclusion: The system is designed to reach equilibrium when the long-term average usage, dictated by the market's demand curve $C(P)$, equals the static, governance-set baseline target $`T_{\text{base}}`$ (note that by governance we refer to clients and protocol design, not on-chain governance). The equilibrium price $`P^{\ast}`$ is therefore the price that induces exactly $`T_{\text{base}}`$ Gas of usage from the market. This proves that the parameter $`T_{\text{base}}`$ acts as the effective long-term controller of network usage.

# Price Stability Analysis

Stability determines whether the system will naturally converge to the equilibrium price $`P^{\ast}`$ after a shock. We can analyze this by examining how a small deviation from equilibrium evolves.

Let's consider the un-clamped adjustment for simplicity, as the clamping factor $\alpha$ only serves to dampen the dynamics and enhance stability. The price update function is:

$$
P_{s+1} = P_s \left(1 + \frac{C(P_s) - T_{\text{effective}, s}}{T_{\text{effective}, s}}\right) = P_s \frac{C(P_s)}{T_{\text{effective}, s}}
$$

To analyze the stability around the equilibrium $`P^{\ast}`$, we can linearize this system. Let's find the derivative of $`P_{s+1}`$ with respect to $`P_s`$ and evaluate it at $`P^{\ast}`$. A system is stable if the absolute value of this derivative is less than 1.

$$
\frac{dP_{s+1}}{dP_s} \bigg|_{P=P^{\ast}} = \frac{C(P^{\ast})}{T_{\text{effective}}(P^{\ast})} + P^{\ast} \frac{C'(P^{\ast})T_{\text{effective}}(P^{\ast}) - C(P^{\ast})T'_{\text{effective}}(P^{\ast})}{T_{\text{effective}}(P^{\ast})^2}
$$

At equilibrium, $`C(P^{\ast}) = T_{\text{effective}}(P^{\ast}) = T_{\text{base}}`$. The expression simplifies to:

$$
= 1 + P^{\ast} \frac{C'(P^{\ast})T_{\text{base}} - T_{\text{base}}T'_{\text{effective}}(P^{\ast})}{T_{\text{base}}^2} = 1 + \frac{P^{\ast}}{T_{\text{base}}}(C'(P^{\ast}) - T'_{\text{effective}}(P^{\ast}))
$$

The derivative of the effective target is $`T'_{\text{effective}}(P^{\ast}) = (1-w) \cdot \beta \cdot C'(P^{\ast})`$. Substituting this in:

$$
\begin{aligned}
&= 1 + \frac{P^{\ast}}{T_{\text{base}}}(C'(P^{\ast}) - (1-w)\beta C'(P^{\ast}))\\
&= 1 + \frac{P^{\ast} C'(P^{\ast})}{T_{\text{base}}}(1 - (1-w)\beta)
\end{aligned}
$$

For stability, we require $`\left| \frac{dP_{s+1}}{dP_s} \right| \lt 1`$, which means:

$$
-2 \lt \frac{P^{\ast} C'(P^{\ast})}{T_{\text{base}}}(1 - (1-w)\beta) \lt 0
$$

Since $`C'(P^{\ast}) \lt 0`$ (demand falls with price) and $`(1 - (1-w)\beta) \gt 0`$ for reasonable parameter choices, the right-hand inequality is always satisfied. The left-hand inequality defines the stability condition:

$$
\left| \frac{P^{\ast} C'(P^{\ast})}{T_{\text{base}}} \right| \lt \frac{2}{1 - (1-w)\beta}
$$

The term on the left is the price elasticity of demand at equilibrium.

**Conclusion:** The system is guaranteed to be stable if the elasticity of demand is not excessively high (see the stability condition above), i.e., if the market is so sensitive that a small price increase to curb overuse causes a demand crash so severe that the system begins to oscillate uncontrollably.  The parameters $`{1-w}`$ and $\beta$ directly contribute to stability; higher values (stronger anchor, faster EMA) relax the stability condition, making the system robust against a wider range of market behaviors. The clamping factor $`{\alpha}`$ provides an additional, powerful guarantee of stability by bounding the adjustment step, ensuring that even under extreme demand shocks, the price cannot diverge uncontrollably.

> If the stability condition wouldn’t hold, this just cause price to become more unpredictable. That said, we have the levers of $w$, $\beta$ and $\alpha$ to adjust should this be the case. Specifically,  $\alpha$ privdes a hard limit in the amount that these storage fees can increase and decrease by, hence reducing this unpredictability.

# Long-Term Price Behavior Under Demand Shifts

Consider a permanent upward shift in demand, where a new demand curve $`\tilde{C}(P)`$ replaces $C(P)$ such that $`\tilde{C}(P) \gt C(P)`$ for all $P$.

Immediately after the shift, usage will be consistently above the effective target. The price update rule will cause $`P_s`$ to increase in each timeframe. At the end of this first high-usage epoch, the protocol observes the overuse. This single event triggers two parallel responses:

1. Usage $`\tilde{C}(P_s)`$ will begin to decrease due to the higher price.
2. The usage EMA, $`T_{\text{RA},s}`$, will rise, pulling the effective target $`T_{\text{effective},s}`$ upwards.

This begins a "chasing" dynamic across subsequent epochs. As long as the new, higher demand persists, usage will likely remain above the (now rising) effective target. Each epoch's high usage continues to send the same two signals to the protocol: "increase the price" and "increase the EMA." The system will seek a new equilibrium price $`\tilde{P}^*`$ where $`\tilde{C}(\tilde{P}^*) = T_{\text{base}}`$. Since $`\tilde{C} \gt C \text{ and } T_{\text{base}}`$ is constant, it must be that $`\tilde{P}^* \gt P^{\ast}.`$

The anchor weight $`{w}`$ is critical here. If $w=0$ (no anchor), the equilibrium condition becomes $`C(P^{\ast}) = T_{\text{RA}}`$, which means the target would simply follow the demand, and the price would not effectively respond to the new normal. The non-zero anchor weight $w$ ensures the system always feels a "pull" back towards the governance-set target $`T_{\text{base}}`$, forcing the price to adjust until usage realigns with this long-term policy goal.

Conclusion: The mechanism is proven to autonomously guide the market to a new, stable equilibrium price that respects the long-term usage target, even in the face of permanent shifts in market demand. It avoids the failure modes of purely static models (which would see chronic overuse) and purely adaptive models (which would normalize the new, higher usage level instead of controlling it).
