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

A `CHANNEL_INSCRIBE` that moves channel notes is not proven when it is posted. Its sequencer bonds unlocked channel notes of the channel instead, and the inscription forfeits its requirement if it is challenged and nobody answers (see [Collateral](channels.md#collateral)). A challenger bonds the same amount, and forfeits the same requirement to a valid answer. This document derives how much such an inscription must put at risk, and why.

# Overview

The collateral an inscription requires pays for two things:

1. **The dispute.** A challenger must profit from stopping an inscription nobody can answer for, and a wrong challenger must pay for the answer it forced. Both are the fees of Mantle Transactions, so this part is priced in Execution Gas and Permanent Storage Gas, at the prices of the two fee markets. The answer verifies signatures the users produced off-chain, and nothing else, so its fees are the whole of its cost.
2. **The harm of a lock.** An inscription that consumes a final note restarts its ageing, and one nobody can answer for keeps the holder out of the leadership lottery for up to two epochs. This part is proportional to the value of the notes moved.

One property shapes every choice below: bonded notes stay in the ledger and keep taking part in Proof of Stake. Over-collateralizing therefore costs an honest party liquidity, not yield, and every parameter is set on the conservative side.

# Parameters

| Parameter | Value | What it prices |
| --- | --- | --- |
| `COLLATERAL_MARGIN` | 2 | Fee prices moving between the posting and the dispute ([The Margin](#the-margin)) |
| `FLOOR_EXECUTION_GAS` | 2,360 | Execution Gas of the dispute of any inscription ([The Floor](#the-floor)) |
| `FLOOR_STORAGE_GAS` | 796 | Permanent Storage Gas of the dispute of any inscription ([The Floor](#the-floor)) |
| `INPUT_EXECUTION_GAS` | 590 | Execution Gas one input adds to an answer ([The Per-Input Rate](#the-per-input-rate)) |
| `INPUT_STORAGE_GAS` | 282 | Permanent Storage Gas one input adds to an answer ([The Per-Input Rate](#the-per-input-rate)) |
| `VALUE_RATE_PPM` | 5,000, that is 0.5% | The lock, per unit of value of the inputs ([The Value Rate](#the-value-rate)) |

For an inscription with $`n`$ inputs, [Channels](channels.md#collateral) requires two parts. The fee-priced part is `COLLATERAL_MARGIN` times the fee of `FLOOR_EXECUTION_GAS + INPUT_EXECUTION_GAS * n` Execution Gas and `FLOOR_STORAGE_GAS + INPUT_STORAGE_GAS * n` Permanent Storage Gas, at the prices of the block that includes the inscription. The value part is `VALUE_RATE_PPM` parts per million of the value of its inputs, locked or not. The amount is recorded with the inscription. The sections below derive each parameter.

# Prices and Fees

A Mantle Transaction pays two fees. Its Execution Gas is paid at the base fee of its block, $`b_{\mathrm{exec}}[s]`$ of [Execution Market](execution-market.md). Its Permanent Storage Gas is paid at the price $`P_{\text{storage}}(s)`$ of [Storage Markets](storage-markets.md), and a transaction consumes exactly one unit of Permanent Storage Gas per byte of its encoding. Every count of bytes below is therefore a count of Permanent Storage Gas, and the fee of a transaction of $`g`$ Execution Gas and $`S`$ bytes is $`g \cdot b_{\mathrm{exec}}[s] + S \cdot P_{\text{storage}}(s)`$, which Channels writes `fee_cost(g, S)`.

The Execution Gas of each Operation is taken from [\[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md), and the size of each payload from [Mantle Transaction Encoding](mantle-transaction-encoding.md).

# Costs on Chain

Every transaction below pays its fee with a `TRANSFER` consuming one note and creating one note of change. That Operation is 75 bytes: 1 of opcode, 1 of input count, 32 for the `NoteId`, 1 of output count and 40 for the `Note`. Its proof, the `ZkSignature` of the consumed note, is 128 bytes and 590 Execution Gas.

**A challenge transaction.** The transaction starts with 1 byte counting its two Operations. The `CHANNEL_CHALLENGE` is 66 bytes: its opcode, the `OpId` of the challenged inscription (32) and a bond of one note (1 byte of count and 32 of `NoteId`). The fee `TRANSFER` is 75 bytes. The two proofs are two `ZkSignature`s, 256 bytes. In all, 398 bytes and 1,180 Execution Gas: 590 for the bond's signature and 590 for the fee transfer's.

**The fixed part of an answer.** The same, with a `CHANNEL_ANSWER` of 35 bytes before its steps: its opcode, the `OpId` of the inscription (32) and the step count (2). Its own proof is empty. In all, 239 bytes and 590 Execution Gas, the fee transfer's signature.

**One step of an answer.** A step applying the authorization of one payment consumes one input and creates at least three notes: the payment, the change and the zone's fee. It is 282 bytes: the input (1 byte of count and 32 of `NoteId`), the three outputs (1 byte of count and 120 of `Note`s) and the authorization (128). Its Execution Gas is 590, the verification of one `ZkSignature`. An authorization with more outputs makes a larger step; that shortfall falls on whoever answers a wrong challenge, and changes no outcome.

| Item | Bytes | Execution Gas |
| --- | --- | --- |
| Challenge transaction, one bond note | 398 | 1,180 |
| Answer, fixed part | 239 | 590 |
| Step, one input, three outputs | 282 | 590 |

# The Floor

The floor covers the two costs every dispute has, whatever the size of the inscription. Both bounds are at the prices of the posting block, before the margin.

- **A right challenge must pay.** The challenger receives half of what the inscription forfeits, so half the floor must cover a challenge transaction: at least twice 1,180 Execution Gas and twice 398 bytes, that is 2,360 and 796.
- **A wrong challenge must pay for the fixed part of the answer.** The sequencer receives the inscription's requirement, forfeited from the challenger's bond, so the floor must cover the fixed part of an answer: at least 590 Execution Gas and 239 bytes.

Taking the larger of each pair gives `FLOOR_EXECUTION_GAS = 2,360` and `FLOOR_STORAGE_GAS = 796`.

# The Per-Input Rate

A wrong challenge must also pay for the steps it forces. The most one input adds to an answer is a step of its own, so each input adds the cost of one step: `INPUT_EXECUTION_GAS = 590` and `INPUT_STORAGE_GAS = 282`.

The requirement counts inputs rather than outputs: it is the holders of the inputs whose notes are locked, and an inscription can consume a thousand notes into one output through a step of the sequencer's own.

# The Value Rate

An inscription consuming a final note re-creates it, and the new note must age again before it can win the leadership lottery: up to two epochs, 15 days. A sequencer can do this to notes it has no authorization for. If challenged it loses, but the victims' notes are re-created under new identifiers and their ageing restarts anyway. Neither the floor nor the per-input rate grows with the value of those notes, while the harm does. A note under withdrawal changes nothing here: an inscription may consume it during the delay only, at the same price, and it leaves at the first unlock after its due.

The harm is also a gain for the attacker. Keeping value out of the lottery lowers the inferred total stake, which raises every other participant's share of the rewards. A participant holding a share of the eligible stake gains, per year of suppression, that share of the yearly Proof of Stake reward on the suppressed value. One attack suppresses the value for at most the two windows of the dispute, 3 days, plus the 15 days of ageing, 18 days, which is 0.049 year. The attacker's cheapest loss is half the forfeit, by challenging itself from a second key. With the value part of the forfeit set to a rate of the value moved, the attack is unprofitable when half that rate exceeds the attacker's share of the eligible stake, times the yearly reward rate, times 0.049. An attacker holds less than half of the eligible stake, so the attack is unprofitable for every attacker once the rate exceeds 0.049 times the yearly reward rate:

| Regime | Yearly reward rate ([Block Rewards](block-rewards.md)) | Minimum rate |
| --- | --- | --- |
| Inferred stake at its 30% target | 3.34% | 0.165% |
| Inferred stake at 10% of the maximum supply | 10% | 0.493% |

`VALUE_RATE_PPM` is set to 5,000, that is 0.5%, which covers the bootstrap phase. It can fall towards 1,700 once the inferred stake reaches its target.

Every input is counted, locked or not. Consuming a locked note before its creator is final extends the lock on its value: the new output waits for its own deadline, and a chain of inscriptions each consuming the output of the previous one could keep a holder's value locked indefinitely for the floor cost alone. Charging the value rate at each consumption makes each extension cost what the first lock cost.

The value part deters, it does not compensate: the forfeit pays the challenger and the rewards pool, not the victims.

# The Margin

A dispute is settled at the prices of the blocks that carry the challenge and the answer, up to 3 days after the inscription was posted. $`P_{\text{storage}}(s)`$ moves at most 12.5% per timeframe, so at most once in that span. $`b_{\mathrm{exec}}[s]`$ moves at most 12.5% per block under sustained full blocks. `COLLATERAL_MARGIN = 2` covers a doubling of either price between posting and dispute. A longer congestion leaves the sequencer under-compensated for the fees of its answer; it cannot make a valid inscription lose or an invalid one final.

# Arithmetic

Every amount is a `TokenValue`, a 64-bit unsigned integer, and Channels computes the requirement with `checked_uint64`: an inscription whose requirement does not fit is invalid. The fee part cannot reach that bound at any realistic price. An inscription has at most 255 inputs, since the encoding counts them on one byte. The fee part is therefore at most twice the fee of 152,810 Execution Gas and 72,706 Permanent Storage Gas. It overflows only if a gas price exceeds about $`2^{64} / 305{,}620`$, that is $`6 \cdot 10^{13}`$ units of value per unit of gas.

The value part multiplies a value by `VALUE_RATE_PPM` before dividing by a million, and the value of the inputs can be a large share of the supply, so the product is computed on 128 bits. The quotient is below the value itself and fits a `TokenValue`.

# What It Costs a Sequencer

A sequencer must have bonded, at any time, the collateral of all its pending inscriptions, most of which are pending for one challenge window. Take a zone that nets 2,000 payments a day into 100 inscriptions of 20 inputs, and moves 1 million LGO of notes a day. About 200 inscriptions are pending at any time:

- the fee-priced part is 200 times twice the fee of 14,160 Execution Gas and 6,436 bytes, twice the fees of answering all of them, of the order of the fees of two full blocks;
- the value part is 0.5% of 2 million LGO, 10,000 LGO.

The bonds keep earning their Proof of Stake rewards, so the sequencer's cost is the liquidity of about 10,000 LGO plus the fee-priced part, not a yield. A challenger bonds the requirement of the one inscription it challenges, under the same terms.
