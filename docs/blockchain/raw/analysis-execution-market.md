# ANALYSIS-EXECUTION-MARKET

| Field | Value |
| --- | --- |
| Name | [Analysis] Execution Market |
| Slug | 190 |
| Status | raw |
| Category | Informational |
| Editor | Juan Pablo Madrigal-Cianci <jp@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/analysis-execution-market.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision | 2026-04-24 |

> Disclaimer:
> This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.
>
> All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein. 
>
> Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.

# Introduction

We provide here a formal mathematical analysis of the execution market's fee mechanism. We model the system's dynamics to evaluate its equilibrium state, stability, and the economic impact of its unique features, particularly the block builder subsidy. We also refer the interested reader to [Base Fee Manipulation In Ethereums EIP-1559 Transaction Fee Mechanism](https://arxiv.org/pdf/2304.11478).

# System Dynamics and Equilibrium

The state of the system evolves block-by-block, defined by two key variables: the base fee, $`b_\text{exec}[s]`$, and the EMA of execution gas usage, $`G_{\text{avg}}[s]`$. Their evolution is described by the following system of equations:

$$
\begin{align}
G_{\text{avg}}[s] &= (1 - q) \cdot G(b_\text{exec}[s]) + q \cdot G_{\text{avg}}[s-1]\\
b_\text{exec}[s+1] &= b_\text{exec}[s] \cdot \left(1 + \phi \cdot \frac{G_{\text{avg}}[s] - G_{\text{target}}}{G_{\text{target}}}\right)
\end{align}
$$

Here, we model the total Execution Gas used in a block, $G[s]$, as a function of the base fee, $`G[b_\text{exec}[s] ]`$, where we assume a standard demand curve with $`G' \lt 0`$ (demand for Execution Gas decreases as the price increases).

The system is in equilibrium when its state variables no longer change. Let the equilibrium state be $`(b^{\ast}, G_{\text{avg}}^{\ast})`$. From the base fee update rule (2), for $`b_\text{exec}[s+1] = b_\text{exec}[s] = b^{\ast}`$, the adjustment factor must be zero. This implies:

$$
G_{\text{avg}}^{\ast} - G_{\text{target}} = 0 \implies \boldsymbol{G_{\text{avg}}^{\ast} = G_{\text{target}}}
$$

From the EMA update rule (1), for $`G_{\text{avg}}[s] = G_{\text{avg}}[s-1] = G_{\text{avg}}^{\ast}`$, we must have:

$$
\begin{aligned}
G_{\text{avg}}^{\ast} &= (1 - q) \cdot G[b^{\ast}] + q \cdot G_{\text{avg}}^{\ast} \\
(1 - q) \cdot G_{\text{avg}}^{\ast} &= (1 - q) \cdot G[b^{\ast}] \\
\implies G_{\text{avg}}^{\ast} &= G[b^{\ast}]
\end{aligned}
$$

Conclusion: Combining these results, the system reaches equilibrium when the execution gas demanded by the market at price $`b^{\ast}`$ is exactly equal to the protocol's target: $`{G[b^{\ast}] = G_{\text{target}}}`$. The equilibrium base fee, $`b^{\ast}`$, is the market-clearing price that induces a level of network activity precisely equal to the desired target.

# Base Fee Stability Analysis

Stability analysis determines if the system will naturally converge to the equilibrium state $`(b^{\ast}, G_{\text{target}})`$ after a market shock. Due to the two-variable, cross-dependent nature of the system, we analyze the Jacobian matrix of the linearized system around the equilibrium point.

The system can be written as a function $`F(b_\text{exec}[s], G_{\text{avg}}[s-1]) = (b_\text{exec}[s+1], G_{\text{avg}}[s])`$. The Jacobian matrix $J$ is:

$$
\begin{aligned}J = \begin{pmatrix}
\displaystyle \frac{\partial b_\text{exec}[s+1]}{\partial b_\text{exec}[s]} & \displaystyle \frac{\partial b_\text{exec}[s+1]}{\partial G_{\text{avg}}[s]} \\
\displaystyle \frac{\partial G_{\text{avg}}[s]}{\partial b_\text{exec}[s]} & \displaystyle\frac{\partial G_{\text{avg}}[s]}{\partial G_{\text{avg}}[s-1]} \end{pmatrix}\end{aligned}
$$

Evaluating the partial derivatives at the equilibrium point yields:

- $`\displaystyle \frac{\partial b_\text{exec}[s+1]}{\partial b_\text{exec}[s]} = 1 + \phi (1-q)\frac{b^{\ast} G'[b^{\ast}]}{G_{\text{target}}}`$
- $`\displaystyle \frac{\partial b_\text{exec}[s+1]}{\partial G_{\text{avg}}[s]} = \phi \frac{q \cdot b^{\ast}}{G_{\text{target}}}`$
- $`\displaystyle \frac{\partial G_{\text{avg}}[s]}{\partial b_\text{exec}[s]} = (1-q)G'[b^{\ast}]`$
- $`\displaystyle \frac{\partial G_{\text{avg}}[s]}{\partial G_{\text{avg}}[s-1]} = q`$

The system is stable if and only if the eigenvalues of this matrix have a magnitude less than 1. While the full characteristic equation is complex, the analysis shows that stability is primarily dependent on the parameters $\phi$, $q$, and the price elasticity of demand, $`\mathcal{E} = \frac{b^{\ast} G'[b^{\ast}]}{G_{\text{target}}}`$.

The introduction of the EMA smoothing factor $q$ significantly enhances stability compared to the classic EIP-1559 model (which is equivalent to setting $q=0$). The term $q$ acts as a damper, reducing the magnitude of the eigenvalues and making the system resilient to oscillations and divergence, even with highly elastic demand. This mathematical property is the foundation of the mechanism's resistance to base fee manipulation attacks.

# User and block builder Incentive Analysis

User Strategy: A rational user has a private valuation for their transaction's inclusion, $`V_t.`$ Their utility is $`U_t = V_t - g_t \cdot c_t`$. For the transaction to be valid, they must set their Execution Gas price $`c_t \ge b_\text{exec}[s]`$. The user's problem is to choose $`c_t`$ to maximize their expected utility.

- Setting $`c_t`$ much higher than $`b_\text{exec}[s]`$ does not guarantee faster inclusion than setting it slightly higher; inclusion speed is determined by the priority fee $`p_t = c_t - b_\text{exec}[s]`$ relative to other users.
- The optimal strategy is to set $`c_t`$ such that it reflects their true marginal valuation per unit of execution gas, $`c_t^{\ast} = V_t / g_t`$. They then pay $`b_\text{exec}[s]`$ (base fee) plus a competitive tip $`p_t`$ that they believe is sufficient for inclusion.

block builder Strategy: A rational block builder seeks to maximize their total block reward, $`R_{\text{proposer}}`$ (cf [Block Rewards](block-rewards.md)). Maximizing this sum is achieved by a greedy algorithm: sort all valid transactions by their revenue and include them in descending order until the block is full.

Conclusion: The subsidy mechanism, while critical for block builder revenue, does not distort the transaction selection incentive. The dominant strategy remains to prioritize transactions with the highest total tips, which aligns the block builder's interest with that of users who value inclusion the most.

# References

- [Blend Protocol - Rewarding](blend-protocol.md)
- StableFee [https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2023.4735](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2023.4735)
- [Base Fee Manipulation In Ethereums EIP-1559 Transaction Fee Mechanism](https://arxiv.org/pdf/2304.11478)
- [Transaction fees on a honeymoon](https://arxiv.org/pdf/2110.04753)
- [Anonymous Leaders Reward Protocol](bedrock-anonymous-leaders-reward.md)
- [\[Overview\] Cryptoeconomics](overview-cryptoeconomics.md)
- [EIP 1559: A transaction fee market proposal](https://ethereum.github.io/abm1559/notebooks/eip1559.html)
