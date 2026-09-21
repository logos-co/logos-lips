# ANALYSIS-CHANNEL-COLLATERAL

| Field | Value |
| --- | --- |
| Name | [Analysis] Channel Collateral |
| Slug | 247 |
| Status | raw |
| Category | Informational |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors |  |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision | 2026-09-18 |

# Introduction

A channel sequencer posts transfers without proving them, against a stake that a lost challenge takes (see [Mantle Collateral](bedrock-v1.1-mantle-specification.md#collateral)). A challenger bonds the same amount, and an answerer bonds a smaller one. This document derives how much a transfer must put at risk, and why.

# Overview

The collateral a transfer requires pays for three things:

1. **The dispute.** A challenger must profit from stopping an invalid transfer, and a wrong challenger must pay for the answer it forced. Both are fees and proving costs, so this part is priced in gas and bytes at the fee markets' current prices.
2. **The pool proofs.** Answering a pool transition means producing a Risc0 proof off chain. That cost is compute time, not block space, so it is a token amount.
3. **The harm of a lock.** A transfer that consumes a final note restarts its ageing, and an invalid one keeps the holder out of the leadership lottery for up to two epochs. This part is proportional to the value of the notes moved.

One property shapes every choice below: staked notes and bond notes stay in the ledger and keep taking part in Proof of Stake. Over-collateralizing therefore costs an honest party liquidity, not yield, and every parameter is set on the conservative side.

# Notation

| Symbol | Meaning | Value |
| --- | --- | --- |
| $`p_e`$ | Execution Gas base price (`execution_gas_base_price`) | [Execution Market](execution-market.md) |
| $`p_s`$ | Permanent Storage Gas price, per byte (`permanent_storage_gas_price`) | [Storage Markets](storage-markets.md) |
| $`c(g, b)`$ | Fee cost of $`g`$ Execution Gas and $`b`$ bytes: $`g \cdot p_e + b \cdot p_s`$ | |
| $`W`$ | Challenge window plus response window | 129,600 slots, 1.5 days |
| $`T_{age}`$ | Longest time a re-created note waits to become eligible for leadership | 2 epochs, 15 days |
| $`y`$ | Yearly Proof of Stake reward rate | 3.34% at the target stake, higher below it ([Block Rewards](block-rewards.md)) |
| $`s_a`$ | Adversarial share of the eligible stake | below $`1/2`$ |
| $`M`$ | Margin on fee prices | 2 |

# Costs on Chain

The sizes follow [Mantle Transaction Encoding](mantle-transaction-encoding.md): a `NoteId` is 32 bytes, a `Note` 40, a `ZkSignature` 128, and every transaction below pays its fee with a `TRANSFER` of one input and one output, 75 bytes and a `ZkSignature`. The gas follows [Gas Cost Determination](analysis-gas-cost-determination.md).

| Item | Bytes | Execution Gas |
| --- | --- | --- |
| Challenge transaction | 397 | 1,180 |
| Answer, fixed part (bond, both batches, fee) | 399 | 8,980 |
| User step, one input, three outputs | 283 | 590 |
| Pool step, fixed part with the reserve note in and out | 276 | 590 |
| Share of a pool step per deposit it consumes and pays | 85 | 0 |

A challenge transaction is one byte of count, the challenge (65 bytes with its opcode), the fee transfer (75) and two signatures (256). The answer's fixed part is the count, the answer header (67), the fee transfer and two signatures; its gas is the bond's signature, the two batch initializations of 3,900 each, and the fee transfer's signature. A user step is its tag, one input (33), three outputs (121) and a signature. A pool step is its tag, instance (32), both counts, the seal (128), and the reserve note consumed by reference (73) and re-created (40). Each deposit it consumes adds a reference to an intermediate note (45) and, at most, a payout (40).

# Parameters

The fee-priced part of the collateral is

```math
M \cdot c\big(G_f + G_i \cdot n + G_s \cdot d,\; B_f + B_i \cdot n + B_s \cdot d\big)
```

for a transfer with $`n`$ inputs declaring $`d`$ pool transitions, evaluated at the prices of the block that includes the transfer and recorded with it.

## The Floor

The floor covers the two costs every dispute has, whatever its size. The bounds below are at the prices of the posting block, before the margin.

- **A right challenge must pay.** The challenger receives half of what the transfer forfeits, so half the floor must exceed a challenge transaction: $`G_f \geq 2 \cdot 1{,}180`$ and $`B_f \geq 2 \cdot 397`$.
- **A wrong challenge must pay the answer's fixed part.** The answerer receives the whole challenger bond, which equals the transfer's requirement: $`G_f \geq 8{,}980`$ and $`B_f \geq 399`$.

Taking the larger bound of each gives $`G_f = 8{,}980`$ and $`B_f = 800`$.

## The Per-Input Rate

A wrong challenge must also pay for the steps it forces. The most one input adds to an answer is its own user step and its share of a pool step: $`G_i = 590`$ and $`B_i = 283 + 85 = 368`$, rounded to 400.

Counting inputs rather than outputs matters. Claims to one key merge, so a transfer can consume a thousand notes into one output, and it is the holders of the inputs whose notes are locked.

## The Per-Transition Rate

A declared pool transition needs one pool step on chain, $`G_s = 590`$ and $`B_s = 276`$, rounded to 300. It also needs a proof, produced off chain, which gas does not price: an Execution Gas unit prices a validator's CPU time inside a scarce block, not a prover's machine. The proving part is therefore a token amount, `STATE_PROVING`, added once per declared transition.

A public pool's transition, a batch of swaps over a few million Risc0 cycles plus the Groth16 wrap, takes minutes on a data-centre GPU. A private pool's transition aggregates the private receipts of the period and is the heaviest case, about an hour for a thousand receipts. `STATE_PROVING` is set to one GPU-hour, about 2 to 3 USD at current cloud prices, converted into LGO at the price of the token at genesis, as the initial storage price is ([Storage Markets](storage-markets.md)). Since the stake keeps earning, sizing it for the private case costs a public pool almost nothing.

This part needs a measurement: the proving time of a reference pool program and of a private pool transition, on the hardware a sequencer is expected to run.

## The Value Rate

A transfer consuming a final note re-creates it, and the new note must age again before it can win the lottery, up to $`T_{age}`$. A sequencer can do this to notes it has no authorization for. If challenged it loses, but the victims' notes are redirected under new identifiers and their ageing restarts anyway. Neither the fee-priced part nor the floor grows with the value of those notes, while the harm does.

The harm is also a gain for the attacker. Keeping value $`V`$ out of the lottery lowers the inferred total stake, which raises every other participant's share of the rewards. An attacker holding a share $`s_a`$ of the eligible stake gains about $`s_a \cdot y \cdot V`$ per year of suppression, and one attack suppresses $`V`$ for at most $`W + T_{age}`$. The attacker's cheapest loss is half the forfeit, challenging itself from a second key. The attack is unprofitable when

```math
\tfrac{1}{2}\,\rho\, V \;\geq\; s_a \cdot y \cdot V \cdot (W + T_{age})
\quad\Longleftarrow\quad
\rho \;\geq\; y \cdot \frac{W + T_{age}}{1\ \text{year}} \quad\text{for } s_a < \tfrac12 .
```

With $`W + T_{age} = 16.5`$ days, $`\rho \geq 0.045 \cdot y`$:

| Regime | $`y`$ | Minimum $`\rho`$ |
| --- | --- | --- |
| Inferred stake at its 30% target | 3.34% | 0.15% |
| Inferred stake at 10% of the maximum supply | 10% | 0.45% |

`VALUE_RATE_PPM` is set to 5,000, that is 0.5%, which covers the bootstrap phase. It can fall towards 1,500 once the inferred stake reaches its target.

Only inputs that could have aged are counted. A locked input is not eligible for leadership, and its creator's collateral already covers it. The reserve notes of a pool the transfer declares carry a pool key, behind which no secret key exists, so they never stake: the ledger recognizes them by recomputing `pool_key(image_id, instance_id, 0)` for each declared pool and leaves them out. Without that exemption, a large pool whose reserve rests final between swaps would pay 0.5% of its reserve on the next one.

The value part deters, it does not compensate: the forfeit pays the challenger and the rewards pool, not the victims.

## The Margin

A dispute is settled at the prices of the blocks that carry the challenge and the answer, up to 1.5 days after the transfer was posted. The storage price moves at most 12.5% per epoch, so at most once in that span. The execution base fee moves at most 12.5% per block under sustained full blocks. $`M = 2`$ covers a doubling of either price between posting and dispute. A longer congestion leaves an answerer under-compensated for its fees; it cannot make a valid transfer lose or an invalid one final.

## The Answer Bond

A wrong answer forfeits its bond to the rewards pool and leaves the challenge open, so it cannot make a valid transfer lose, and its verification is paid by its own gas. The one thing wrong answers could try is to crowd the valid answer out of the response window. The execution market prevents that on its own: under full blocks the base fee is multiplied by up to 1.125 per block once its average has caught up, and a response window spans about 2,160 blocks.

The answer bond is therefore not load-bearing. It is set to the fee-priced floor at the answer's block, $`M \cdot c(G_f, B_f)`$, which at least doubles the cost of a wrong answer.

# Result

```python
COLLATERAL_MARGIN = 2
FLOOR_GAS,  FLOOR_BYTES = 8_980, 800
INPUT_GAS,  INPUT_BYTES =   590, 400
STATE_GAS,  STATE_BYTES =   590, 300
STATE_PROVING  = GPU_HOUR_IN_LGO  # one GPU-hour, converted at the genesis price of LGO
VALUE_RATE_PPM = 5_000

def fee_cost(gas: int, size: int) -> TokenValue:
    return gas * execution_gas_base_price + size * permanent_storage_gas_price

required = (COLLATERAL_MARGIN * fee_cost(FLOOR_GAS + INPUT_GAS * n + STATE_GAS * d,
                                         FLOOR_BYTES + INPUT_BYTES * n + STATE_BYTES * d)
            + STATE_PROVING * d
            + staking_value * VALUE_RATE_PPM // 1_000_000)

answer_bond = COLLATERAL_MARGIN * fee_cost(FLOOR_GAS, FLOOR_BYTES)
```

where `staking_value` is the value of the unlocked inputs, reserves of declared pools excluded. [Mantle](bedrock-v1.1-mantle-specification.md#collateral) specifies the rule.

# What It Costs a Sequencer

A sequencer must hold, staked, the collateral of all its pending transfers, most of which are pending for one challenge window. Take a zone that nets 2,000 payments a day into 100 transfers of 20 inputs, and moves 1 million LGO of final notes a day. About 75 transfers are pending at any time:

- the fee-priced part is $`75 \cdot 2 \cdot c(20{,}780,\ 8{,}800)`$, twice the fees of answering all of them, of the order of the fees of one full block;
- the value part is $`0.5\% \cdot 1{,}000{,}000 \cdot 0.75 = 3{,}750`$ LGO.

The stake keeps earning its Proof of Stake rewards, so the sequencer's cost is the liquidity of about 3,750 LGO plus the fee-priced part, not a yield. A challenger bonds the requirement of the one transfer it challenges, under the same terms.

# What Is Not Priced

A transfer declaring a pool transition nobody can prove stalls that pool until it loses, up to both windows: no other sequencer can build on the false state or declare from another one. Its collateral does not grow with the value the pool holds, since the reserve is left out of the value part. Only an accredited sequencer can do it, on its turn, and it forfeits each time, so under round-robin sequencing the remedy is to remove its key. A permissionless sequencer set would need this priced, for instance by a rate on the declared pool's reserve.

# Open Measurements

- The proving time of a reference pool program and of a private pool transition, which sets `STATE_PROVING`.
- The verification cost of a Risc0 Groth16 receipt batch, assumed equal to a `ZkSignature` batch in [Gas Cost Determination](analysis-gas-cost-determination.md).
- The LGO price at genesis, which converts `STATE_PROVING`.

# References

- [Mantle](bedrock-v1.1-mantle-specification.md): Bridging, Collateral, Challenges and Answers
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
- [\[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md)
- [Execution Market](execution-market.md) and [Storage Markets](storage-markets.md)
- [Block Rewards](block-rewards.md)
- [Cryptarchia](cryptarchia-v1-protocol.md): epochs and eligibility for leadership
