# Logos Token: Units and Precision

| Field | Value |
| --- | --- |
| Name | LOGOS Unit and Denominations |
| Slug | 245 |
| Status | raw |
| Category | Standards Track |
| Editor | Frederico Teixeira [frederico@logos.co](mailto:frederico@logos.co) |
| Contributors |  |

## Timeline

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-10-05 |

> *Disclaimer:
This material, including any linked pages or documents, is provided for informational purposes only. It does not constitute investment advice, a solicitation, or an offer to buy or sell any securities, tokens, or other financial instruments, nor should it be construed as legal, financial, or tax advice.*
> 
> 
> *All information regarding project details, token design, distribution mechanisms, technical parameters, and any forward-looking statements is preliminary and subject to change without notice. No representations or warranties are made as to the completeness or accuracy of the information herein.*
> 
> *Nothing in this material should be relied upon for investment or business decisions. Recipients of this information assume all risks associated with its use and are responsible for seeking independent professional advice regarding any actions based on it.*
> 

# Introduction

This document specifies the smallest indivisible unit of the Logos Blockchain native token and the precision that relates it to the display unit. It also fixes the intermediate denominations, the encoding of amounts, and the rounding quantum that other specifications inherit.

The Logos Blockchain ledger holds no fractional quantities. Note values are integers of type `TokenValue`, defined as `uint64` in [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md). Every fee, price, and reward reduces to an integer count of indivisible units.

Precision therefore fixes the representable range of the ledger and the price resolution of both gas markets. This document derives it from those two constraints rather than by analogy with other chains.

The derivation is two-sided. Section Upper Bound on Precision bounds precision from above by representability: the supply must fit in a `uint64` note. Section Lower Bound on Precision bounds it from below by economics: one indivisible unit is the price floor of both gas markets, so a coarse unit prices operations above their market-clearing level.

The results are:

- The indivisible unit is the LEPTON, plural LEPTA, with $1 \text{ LOGOS} = 10^{9} \text{ LEPTA}$.
- The upper bound is $d \le 9$. Precision $10^{10}$ and above is unrepresentable, and $10^{18}$ would require widening `TokenValue` to at least 128 bits.
- The lower bound is $d \ge \log_{10}\left(p \cdot 2^{30} / c^{\ast}\right)$, which depends on the token price $p$ and the target permanent-storage cost $c^{\ast}$ only through their ratio. It is satisfied at $d = 9$ whenever $p / c^{\ast} \le 10^{9} / 2^{30}$ GiB per LOGOS.
- The two bounds meet at $d = 9$. Above $p / c^{\ast} = 10^{9} / 2^{30}$ the requirement becomes $d \ge 10$, which **R1** excludes, so no admissible precision restores it. The boundary scales as $10^{9} / g$, so it is the Permanent Storage Gas unit $g$, and not the precision, that sets the available room.

# Overview

## Key Principles

Three properties of the surrounding specifications constrain the unit system:

- **Integer ledger**. `Note.value` is a `TokenValue`, which is a `uint64`. All arithmetic over token values, balances, gas amounts, and fees is checked, and a Mantle Transaction is invalid if any intermediate result is not representable in its stated type. See [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md).
- **Fixed supply**. The hard cap is $S_{cap} = 10^{10}$ LOGOS. This document takes it as an input, and every precision result below is a function of it. See [Block Rewards](block-rewards.md).
- **Integer-valued prices**. The Execution base fee and the Permanent Storage price are integers with an effective floor of one base unit per gas unit. See [Execution Market](execution-market.md) and [Storage Markets](storage-markets.md).

The first two bound precision from above. The third bounds it from below.

## Requirements

- **R1. Representability**. Any admissible balance must be encodable in `TokenValue`. A single note holding the entire supply is admissible, so $S_{cap}$ must be representable.
- **R2. Integrality**. No protocol quantity is fractional. Every fee, price, reward, and balance is an integer count of indivisible units.
- **R3. Price resolution**. One indivisible unit must be small enough that the gas-market price floor stays below the market-clearing price of the operations those markets serve.
- **R4. Unique naming**. Each named unit denotes exactly one quantity, and each quantity has exactly one canonical name in protocol interfaces.

**R1** and **R3** are opposing. **R1** is satisfied by lowering precision, **R3** by raising it. Sections Upper Bound on Precision and Lower Bound on Precision derive each independently, and section Choice of Precision combines them.

## High-level Design

The unit system has two layers. The protocol layer counts LEPTA as unsigned integers and never sees a decimal point. The presentation layer renders a LEPTA count as a decimal LOGOS string with at most nine fractional digits, and parses such a string back into a LEPTA count.

Between them sit two named intermediate denominations, kilolepton and megalepton. They make gas prices and small fees readable without introducing a second numeric type. They are simply display aliases.

# Construction

## Core Variables

- $S_{cap}$ denotes the maximum allowable token supply (hard cap).
- $d \in \mathbb{N}$ denotes the precision exponent: one LOGOS equals $10^d$ LEPTA.
- $V_{max}$ denotes the largest value representable by `TokenValue`.
- $N(d) = S_{cap} \cdot 10^{d}$ denotes the hard cap expressed in indivisible units.
- $H(d) = V_{max} / N(d)$ denotes the representable headroom, in multiples of $S_{cap}$.
- $S^{\ast}_{cap}$ denotes the largest admissible hard cap.
- $g$ denotes the gas units consumed by a reference operation.
- $p$ denotes the token price, in currency units per LOGOS.
- $c^{\ast}$ denotes the target cost of the reference operation, in the same currency units.
- $p^{\ast}(g, d)$ denotes the saturation price: the value of $p$ above which the one-unit price floor makes the operation cost more than $c^{\ast}$.

## Parametrization

| Symbol | Definition | Value | Source |
| --- | --- | --- | --- |
| $d$ | Precision exponent | $9$ | Derived in Choice of Precision. |
| $V_{max}$ | Largest representable `TokenValue` | $2^{64}-1 = 18{,}446{,}744{,}073{,}709{,}551{,}615$ | `Note.value: uint64` in [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md). |
| $S_{cap}$ | Maximum allowable token supply | $10^{10}$ LOGOS $= 10^{19}$ LEPTA | [Block Rewards](block-rewards.md). |
| $N(9)$ | Hard cap in LEPTA | $10^{19}$ | $S_{cap} \cdot 10^9$. |
| $H(9)$ | Representable headroom | $1.8446744073709551$ | $V_{max}/N(9)$. |
| $S_{cap}^{\ast}$ | Largest admissible hard cap | $18{,}446{,}744{,}073$ LOGOS | $\lfloor V_{max}/10^9 \rfloor$. Derived in Headroom. |
| `EXECUTION_TRANSFER_GAS` | Execution gas of a Transfer Operation | $590$ | Appendix of [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md). |
| Storage gas per byte | Permanent Storage gas per stored byte | $1$ | [Storage Markets](storage-markets.md). |

## Upper Bound on Precision

Requirement **R1** states that a single note must hold the entire supply. Assume the supply is bounded by $S_{cap}$. Then **R1** is the condition

$$
N(d) = S_{cap} \cdot 10^{d} \le V_{max}.
$$

Substituting $S_{cap} = 10^{10}$ and $V_{max} = 2^{64}-1$ gives

$$
10^{10+d} \le 2^{64}-1
\quad \Longleftrightarrow \quad
10 + d \le \log_{10}\left(2^{64}-1\right) = 19.26591972\ldots
$$

Since $d$ is an integer, this implies

$$
d \le 9 .
$$

The bound is tight, and the margin at $d = 10$ is not marginal. The table evaluates $N(d)$ and $H(d)$ around the bound.

| $d$ | $N(d)$ (LEPTA) | Representable in `uint64` | $H(d)$ |
| --- | --- | --- | --- |
| $7$ | $1.0000 \times 10^{17}$ | yes | $184.47$ |
| $8$ | $1.0000 \times 10^{18}$ | yes | $18.447$ |
| $9$ | $1.0000 \times 10^{19}$ | yes | $1.8447$ |
| $10$ | $1.0000 \times 10^{20}$ | no | $0.1845$ |
| $18$ | $1.0000 \times 10^{28}$ | no | $1.8447 \times 10^{-9}$ |

A wei-like precision of $10^{18}$ is not available under the current ledger types. It exceeds $V_{max}$ by a factor of $5.4 \times 10^8$. Adopting it would require widening `TokenValue` from 64 to at least 128 bits, which changes note encoding, transaction encoding, and every checked-arithmetic bound in [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md) and [Mantle Transaction Encoding](mantle-transaction-encoding.md).

The bound depends on $S_{cap}$. Any change to the hard cap changes the admissible set, as recorded in Headroom.

## Lower Bound on Precision

Both gas markets price in integers with a floor of one unit. The minimum cost of an operation consuming $g$ gas units is therefore $g$ base units, independent of demand. In currency terms,

$$
c_{min}(g, d, p) = g \cdot 10^{-d} \cdot p .
$$

Requirement **R3** is $c_{min} \le c^{\ast}$. Substituting $c_{min}$ and solving for $d$:

$$
g \cdot 10^{-d} \cdot p \le c^{\ast}
\quad \Longleftrightarrow \quad
10^{d} \ge \frac{g \cdot p}{c^{\ast}}
\quad \Longleftrightarrow \quad
d \ge \log_{10}\left(\frac{g \cdot p}{c^{\ast}}\right).
$$

With $g = 2^{30}$, the gas charged for one GiB of permanent storage, the requirement is

$$
d \ge \log_{10}\left(\frac{p \cdot 2^{30}}{c^{\ast}}\right).
$$

The requirement depends only on the ratio $p / c^{\ast}$, not on either value separately. Scaling the token price and the target cost by the same factor leaves the right-hand side unchanged. A $1 token against a $\$5$ per GiB target imposes exactly the precision requirement of a $\$6$ token against a $\$30$ per GiB target, because both fix $p / c^{\ast} = 0.2$.

The ratio carries units of GiB per LOGOS, so it is how much permanent storage one LOGOS buys at the target cost.

Combining the requirement with the **R1** cap $d_{req} \le 9$ gives the admissibility condition in closed form:

$$
d_{req} \le 9
\quad \Longleftrightarrow \quad
\frac{p}{c^{\ast}} \le \frac{10^{9}}{2^{30}} = 0.9313225746 .
$$

The boundary is therefore a straight line, $p = 0.9313 \cdot c^{\ast}$, and the admissible region is everything below it. In words, $d = 9$ remains admissible for as long as one LOGOS buys at most $0.93$ GiB of permanent storage.

The argument generalizes to any operation as 

$$
\dfrac{p}{c^{\ast}} \le \dfrac{ 10^{9} }{ g }.
$$

The bound scales with the gas charged, so it is the definition of the gas unit, and not the precision, that sets how much room the mechanism has. Charging Permanent Storage Gas per KiB rather than per byte replaces $g = 2^{30}$ with $g = 2^{20}$ and moves the boundary from $0.93$ to $953.7$ GiB per LOGOS.

![**Figure 1.** Required precision $d$ over a grid of token prices and storage-cost targets, with each cell holding $d_{req} = \lceil \log_{10}(p \cdot 2^{30} / c^{\ast}) \rceil$. Green marks $d_{req} \le 9$, admissible under **R1**. Red marks $d_{req} \ge 10$, which **R1** excludes.](overview-cryptoeconomics/assets/precision-admissibility-heatmap.png)

**Figure 1.** Required precision $d$ over a grid of token prices and storage-cost targets, with each cell holding $d_{req} = \lceil \log_{10}(p \cdot 2^{30} / c^{\ast}) \rceil$. Green marks $d_{req} \le 9$, admissible under **R1**. Red marks $d_{req} \ge 10$, which **R1** excludes.

Read as a price rather than a ratio, the same condition gives the saturation price

$$
p^{\ast}(g, d) = \frac{c^{\ast} \cdot 10^{d}}{g} .
$$

Above $p^{\ast}$ the floor binds: the market cannot clear below $c_{min}$, regardless of demand. Below $p^{\ast}$ the floor is slack, and the price update rules in [Execution Market](execution-market.md) and [Storage Markets](storage-markets.md) discover the price.

Two reference operations bracket the range of $g$ in the protocol:

- A Transfer Operation, with $g = 590$.
- One GiB of permanent storage, with $g = 2^{30} = 1{,}073{,}741{,}824$, since Permanent Storage Gas is charged per byte.

The gap in $g$ is a factor of $1.82 \times 10^{6}$, so the two markets saturate at prices six orders of magnitude apart. The table gives $p^{\ast}$ in USD per LOGOS across candidate precisions and target costs.

| $d$ | Transfer, $c^{\ast} = \$0.01$ | 1 GiB, $c^{\ast} = \$1$ | 1 GiB, $c^{\ast} = \$5$ | 1 GiB, $c^{\ast} = \$10$ | 1 GiB, $c^{\ast} = \$30$ |
| --- | --- | --- | --- | --- | --- |
| $7$ | $\$169.49$ | $\$0.0093$ | $\$0.0466$ | $\$0.0931$ | $\$0.2794$ |
| $8$ | $\$1{,}694.92$ | $\$0.0931$ | $\$0.4657$ | $\$0.9313$ | $\$2.7940$ |
| $9$ | $\$16{,}949.15$ | $\$0.9313$ | $\$4.6566$ | $\$9.3132$ | $\$27.9397$ |

Three readings follow:

- Execution is not the binding market. At $d = 8$ a transfer stays under one cent up to $\$1{,}695$ per LOGOS, which is a fully diluted valuation of $17$ trillion USD at $S_{cap} = 10^{10}$. The execution floor does not discriminate between candidate precisions at any plausible price.
- Permanent storage is the binding market. Its boundary $p / c^{\ast} \le 10^{9} / 2^{30}$ is tighter than the execution boundary $p / c^{\ast} \le 10^{9} / 590$ by the gas ratio alone, so the ordering holds whatever target costs are assigned to the two operations.
- At $d = 8$ and $c=\$5$/GiB, the storage floor exceeds $\$5$ per GiB once LOGOS passes $\$0.47$. That is inside the plausible price range, so $d = 8$ fails **R3**.

Evaluating the requirement derived above at four prices and three targets gives the integer precision each combination demands.

| $p$ (USD per LOGOS) | Required $d$ at $c^{\ast} = \$5$ per GiB | Required $d$ at $c^{\ast} = \$10$ per GiB | Required $d$ at $c^{\ast} = \$30$ per GiB | Admissible under R1 |
| --- | --- | --- | --- | --- |
| $\$1$ | $8.33 \rightarrow 9$ | $8.03 \rightarrow 9$ | $7.55 \rightarrow 8$ | yes / yes / yes |
| $\$2$ | $8.63 \rightarrow 9$ | $8.33 \rightarrow 9$ | $7.85 \rightarrow 8$ | yes / yes / yes |
| $\$5$ | $9.03 \rightarrow 10$ | $8.73 \rightarrow 9$ | $8.25 \rightarrow 9$ | no / yes / yes |
| $\$10$ | $9.33 \rightarrow 10$ | $9.03 \rightarrow 10$ | $8.55 \rightarrow 9$ | no / no / yes |

**R3** is satisfiable under **R1** exactly when $p / c^{\ast} \le 0.9313$. At $c^{\ast} = \$5$ per GiB that is $p \le \$4.66$, at $\$10$ it is $p \le \$9.31$, and at $\$30$ it is $p \le \$27.94$. Outside that region the requirement is $d \ge 10$, which **R1** excludes.

## Choice of Precision

**R1** caps precision at $d \le 9$. **R3** requires $d \ge d_{req}$, the smallest integer meeting the bound derived above:

$$
d_{req} = \left\lceil \log_{10}\left(\frac{p \cdot 2^{30}}{c^{\ast}}\right) \right\rceil .
$$

The admissible set is therefore the integer interval

$$
\mathcal{D} = \lbrace d \in \mathbb{N} : d_{req} \le d \le 9 \rbrace .
$$

Its contents depend only on the ratio $p / c^{\ast}$, through the equivalence $d_{req} \le k \Leftrightarrow p / c^{\ast} \le 10^{k} / 2^{30}$.

| $p / c^{\ast}$ (GiB per LOGOS) | $d_{req}$ | Admissible set $\mathcal{D}$ |
| --- | --- | --- |
| $\le 10^{7} / 2^{30}$ | $\le 7$ | $\lbrace 7, 8, 9 \rbrace$ |
| $\left( 10^{7} / 2^{30}, \; 10^{8} / 2^{30} \right]$ | $8$ | $\lbrace 8, 9 \rbrace$ |
| $\left( 10^{8} / 2^{30}, \; 10^{9} / 2^{30} \right]$ | $9$ | $\lbrace 9 \rbrace$ |
| $> 10^{9} / 2^{30}$ | $\ge 10$ | empty |

$\mathcal{D}$ is an interval capped at $9$ by **R1**, so its upper endpoint is $9$ whenever it is non-empty. This gives a dominance argument: $d = 9$ **is admissible whenever any precision is admissible.**

No other value has this property. $d = 8$ is admissible only on $p / c^{\ast} \le 10^{8} / 2^{30}$, one tenth of the range, and $d = 7$ on one hundredth. 

Selecting $d = 9$ therefore does not require committing to a value of $p / c^{\ast}$, which is not known when the encoding is fixed and can move by an order of magnitude over its life.

$$
\boxed{\;d = 9 \qquad \Longrightarrow \qquad 1 \text{ LOGOS} = 10^{9} \text{ LEPTA}.\;}
$$

What is forced and what is not:

- On the band $10^{8} / 2^{30} < p / c^{\ast} \le 10^{9} / 2^{30}$, $d = 9$ is the only admissible value.
- Below that band $d = 9$ remains admissible but is no longer unique, and $d = 8$ satisfies both requirements as well. Here $d = 9$ is selected by dominance, not by necessity.
- Above the band $\mathcal{D}$ is empty and no precision satisfies both requirements.

Taking the top of the interval costs representable headroom, $H(9) = 1.8447$ against $H(8) = 18.447$. Under a fixed hard cap no process consumes that headroom, as shown in Headroom, so the cost is not realised.

Two consequences are recorded rather than resolved.

- The result is a function of $S_{cap} = 10^{10}$ LOGOS and of `TokenValue` being 64 bits wide. Changing either reopens the derivation.
- Where $p / c^{\ast} > 10^{9} / 2^{30}$ the two requirements are jointly infeasible: **R1** caps $d$ before **R3** is met. The remedy lies in the Permanent Storage Gas unit $g$, which sets the boundary at $10^{9} / g$, and not in the precision.

## Headroom

At $d = 9$ the representable headroom is $H(9) = 1.8447$ times the hard cap. This section states where it is consumed and when it fails.

**Hard cap ceiling.** **R1** requires $S_{cap} \cdot 10^9 \le V_{max}$, hence

$$
S_{cap} \le \left\lfloor \frac{2^{64}-1}{10^9} \right\rfloor = 18{,}446{,}744{,}073 \text{ LOGOS}.
$$

The specified cap of $10^{10}$ LOGOS sits at $54.2\%$ of this ceiling. A cap above $1.8446744073 \times 10^{10}$ LOGOS is incompatible with $d = 9$ and forces $d \le 8$. By Lower Bound on Precision that narrows the region where **R3** can be met by a factor of ten, from $p / c^{\ast} \le 10^{9} / 2^{30}$ to $p / c^{\ast} \le 10^{8} / 2^{30}$, so the failure appears at high prices rather than low ones. Raising the cap is therefore constrained from two directions at once.

**Supply growth.** [Block Rewards](block-rewards.md) allocates the full supply at genesis and moves tokens between circulating supply, a fee pool, and a rewards reserve. No path in that mechanism raises the total above $S_{cap}$. The bound $N(9) \le V_{max}$ therefore holds at every step, with no growth argument required. If a later revision introduces issuance above $S_{cap}$, this section must be reopened.

**Aggregation.** Two notes each holding more than $H(9)/2 = 92.23\%$ of the hard cap would overflow `uint64` when summed. The state is unreachable while the sum of all note values is bounded by $S_{cap}$. The failure mode is confined to malformed or adversarial inputs, which [Bedrock v1.1 Mantle Specification](bedrock-v1.1-mantle-specification.md) excludes by requiring checked arithmetic on every addition, and by accumulating the transaction balance in a signed 128-bit integer.

## Denominations

The ladder below is normative. The remaining columns give the exact conversions.

| Unit (singular / plural) | Symbol | In LEPTA | In LOGOS |
| --- | --- | --- | --- |
| lepton / lepta | `LEPTON` | $1$ | $10^{-9}$ |
| kilolepton / kilolepta | `kLEPTON` | $10^{3}$ | $10^{-6}$ |
| megalepton / megalepta | `MLEPTON` | $10^{6}$ | $10^{-3}$ |
| logos | `LOGOS` | $10^{9}$ | $1$ |

Rules, following R4:

- The LEPTON is the indivisible unit. No representable balance is smaller than one LEPTON at any layer of the protocol.
- Symbols are never pluralized. The plural applies to the spelled-out name only, so “$500$ `LEPTON`” and “five hundred lepta” are both correct, and “$500$ `LEPTA`” is not.
- The SI-prefixed forms $\mu\text{LOGOS}$ and mLOGOS denote the same quantities as `kLEPTON` and `MLEPTON`. They are permitted as display aliases in user-facing surfaces, and are not permitted in protocol interfaces, RPC payloads, or specification text.
- `GLEPTON` is not a valid unit. It would denote $10^9$ LEPTA, which is the LOGOS, and R4 admits one canonical name per quantity.

## Encoding and Parsing

All protocol quantities are encoded as unsigned integers counting LEPTA. `Value` is `UINT64` in [Mantle Transaction Encoding](mantle-transaction-encoding.md), and this specification adds no new numeric type.

Let a decimal LOGOS string be $s = I . F$, where $I$ is a non-empty digit sequence and $F$ is a possibly empty digit sequence of length $\ell = |F|$. The corresponding LEPTA count is

$$
v = I \cdot 10^{9} + F \cdot 10^{\,9 - \ell}.
$$

A parser implementing this conversion:

1. MUST reject $s$ if $\ell > 9$. Excess fractional digits express an amount the ledger cannot represent. Truncating or rounding them substitutes a different amount for the one the user specified.
2. MUST reject $s$ if $v > 2^{64}-1$. The largest representable amount is $18{,}446{,}744{,}073.709551615$ LOGOS.
3. MUST NOT use binary or decimal floating-point arithmetic at any step. Both directions are exact integer operations.

Rendering is the inverse. The value $v$ is rendered as $\lfloor v / 10^9 \rfloor$, a decimal point, and $v \bmod 10^9$ zero-padded to nine digits. Trailing zeros MAY be trimmed for display, and MUST NOT be trimmed in any string that is subsequently parsed as a canonical amount.

## Rounding

Fee, price, and reward mechanisms produce rational quantities. Each must be reduced to an integer count of LEPTA before it moves a balance, which makes the direction a consensus rule. This document fixes the quantum and the direction. It does not specify where the reductions occur, which belongs to the specification defining each mechanism.

**Quantum.** Every reduction is to a whole LEPTON, so each rounded quantity carries an error below $10^{-9}$ LOGOS.

**Direction.** The convention already applied across the blockchain specifications:

| Class of quantity | Direction | Reason |
| --- | --- | --- |
| Amounts charged to a user | away from zero | Keeps one LEPTON as the effective price floor. Rounding down makes $0$ an absorbing state for the base fee, after which execution is permanently free. |
| Amounts credited to a participant | toward zero | The sum of credited shares never exceeds the exact entitlement. |
| Measurements, such as usage averages | toward zero | The usage EMA in [Storage Markets](storage-markets.md) is additive and recovers from $0$ once demand resumes. Rounding up reports residual demand on an idle network. |

**Residues.** A mechanism that splits an amount by two or more independent roundings leaves a residue below one LEPTON per rounding. The specification defining that mechanism MUST state where the residue goes to avoid silently reducing the total supply.

# Units of Account

Every protocol quantity denominated in the native token is measured in LEPTA, or in LEPTA per gas unit. The table records the unit for quantities defined elsewhere in the blockchain set.

| Quantity | Symbol | Specification | Unit |
| --- | --- | --- | --- |
| Note value | `Note.value` | [Mantle](bedrock-v1.1-mantle-specification.md) | LEPTA |
| Transaction balance | `tx_balance` | [Mantle](bedrock-v1.1-mantle-specification.md) | LEPTA |
| Mandatory fee | `tx_mandatory_fee` | [Mantle](bedrock-v1.1-mantle-specification.md) | LEPTA |
| Priority tip | `tx_priority_tip` | [Mantle](bedrock-v1.1-mantle-specification.md) | LEPTA |
| Execution base fee | $b_{\mathrm{exec}}[s]$ | [Execution Market](execution-market.md) | LEPTA per Execution Gas unit |
| Execution gas price cap | $c_t$ | [Execution Market](execution-market.md) | LEPTA per Execution Gas unit |
| Permanent storage price | $P_{\mathrm{STR}}(s)$ | [Storage Markets](storage-markets.md) | LEPTA per Storage Gas unit |
| Block reward | $R_t$ | [Block Rewards](block-rewards.md) | LEPTA |
| Inferred total stake | $D_{0,t}$ | [Block Rewards](block-rewards.md) | LEPTA |
| Hard cap | $S_{cap}$ | [Block Rewards](block-rewards.md) | $10^{19}$ LEPTA |

Specifications that state a constant in whole LOGOS must scale it by $10^9$ before evaluating it against ledger quantities. Ratios of two same-unit quantities are scale-invariant and are unaffected.

Two floor costs follow from the table and the gas constants:

- A Transfer Operation costs at least $590$ LEPTA in execution fees, which is $5.9 \times 10^{-7}$ LOGOS.
- Storing one GiB permanently costs at least $2^{30} = 1{,}073{,}741{,}824$ LEPTA, which is $1.0737$ LOGOS.

Both are floors, not expected prices. Both markets discover their price upward from the floor.

# Naming

The declarations below are normative. Each carries one line of justification.

| Item | Value | Rationale |
| --- | --- | --- |
| Token name | LOGOS | Matches the project name. |
| Primary ticker | LOGOS | Used wherever no external code system applies. |
| ISO 4217 form | XLG | ISO 4217 reserves codes beginning with X for units that are not specific to a country ([ISO 4217](https://en.wikipedia.org/wiki/ISO_4217), accessed 2026-08-11). XLG is a proposed convention, not an assigned code. |
| Indivisible unit | LEPTON, plural LEPTA | The lepton was the smallest denomination of Ancient Greek coinage, matching the position this unit occupies ([Lesson of the widow’s mite](https://en.wikipedia.org/wiki/Lesson_of_the_widow%27s_mite), accessed 2026-08-11). |

# Appendix: Reference Implementation

```python
LEPTA_PER_LOGOS = 10**9          # d = 9
TOKEN_VALUE_MAX = 2**64 - 1      # TokenValue is uint64
MAX_FRACTIONAL_DIGITS = 9

class AmountError(ValueError):
    pass

def parse_logos(s: str) -> int:
    """
    Parse a decimal LOGOS string into an integer count of LEPTA.
    Exact integer arithmetic only. Rejects rather than rounds.
    """
    if "." in s:
        integer_part, fractional_part = s.split(".", 1)
    else:
        integer_part, fractional_part = s, ""

    if not integer_part.isdigit():
        raise AmountError("integer part must be a non-empty digit sequence")
    if fractional_part and not fractional_part.isdigit():
        raise AmountError("fractional part must be a digit sequence")
    if len(fractional_part) > MAX_FRACTIONAL_DIGITS:
        raise AmountError(
            f"at most{MAX_FRACTIONAL_DIGITS} fractional digits are representable"
        )

    padded = fractional_part.ljust(MAX_FRACTIONAL_DIGITS, "0")
    value = int(integer_part) * LEPTA_PER_LOGOS + int(padded)

    if value > TOKEN_VALUE_MAX:
        raise AmountError("amount exceeds TokenValue range")
    return value

def format_logos(value: int, trim: bool = False) -> str:
    """
    Render an integer count of LEPTA as a decimal LOGOS string.
    Inverse of parse_logos when trim is False.
    """
    if not 0 <= value <= TOKEN_VALUE_MAX:
        raise AmountError("value outside TokenValue range")

    whole, fraction = divmod(value, LEPTA_PER_LOGOS)
    digits = str(fraction).rjust(MAX_FRACTIONAL_DIGITS, "0")
    if trim:
        digits = digits.rstrip("0")
        return f"{whole}.{digits}" if digits else str(whole)
    return f"{whole}.{digits}"

def max_precision_exponent(supply_in_tokens: int, value_max: int) -> int:
    """
    Upper bound on d (R1): largest d such that supply_in_tokens * 10**d
    is representable. Returns 9 for 10**10 tokens and a uint64 value.
    """
    d = 0
    while supply_in_tokens * 10 ** (d + 1) <= value_max:
        d += 1
    return d

def min_precision_exponent(gas: int, price: float, target_cost: float) -> int:
    """
    Lower bound on d (R3): smallest d such that the one-unit price floor
    keeps an operation consuming `gas` units at or below `target_cost`,
    when the token trades at `price`. Returns 9 for one GiB of permanent
    storage at 2 USD per LOGOS and a 5 USD per GiB target.
    """
    d = 0
    while gas * 10 ** (-d) * price > target_cost:
        d += 1
    return d

def saturation_price(gas: int, d: int, target_cost: float) -> float:
    """
    Token price above which the one-unit floor makes an operation consuming
    `gas` units cost more than `target_cost`.
    """
    return target_cost * 10**d / gas
```