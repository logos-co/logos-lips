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
| 1.1.0 | Added the collateral of a declared pool transition, fee-priced and for its off-chain proof, the batch of receipts in the floor, the pool share in the per-input storage gas, and the pool stall that is not priced, following [Mantle](bedrock-v1.1-mantle-specification.md) 1.17.0 | 2026-09-21 |

# Introduction

A `CHANNEL_INSCRIBE` that moves channel notes or advances a pool is not proven when it is posted. Its sequencer bonds unlocked channel notes of the channel instead, and the inscription forfeits its requirement if it is challenged and nobody answers (see [Collateral](channels.md#collateral)). A challenger bonds the same amount, and forfeits the same requirement to a valid answer. This document derives how much such an inscription must put at risk, and why.

# Overview

The collateral an inscription requires pays for three things:

1. **The dispute.** A challenger must profit from stopping an inscription nobody can answer for, and a wrong challenger must pay for the answer it forced. Both are the fees of Mantle Transactions, so this part is priced in Execution Gas and Permanent Storage Gas, at the prices of the two fee markets. For the notes of users, the answer verifies signatures they produced off-chain, and nothing else, so its fees are the whole of its cost.
2. **The pool proofs.** Answering for a pool transition means producing a Risc0 proof off chain. That cost is compute time, not block space, so it is a token amount.
3. **The harm of a lock.** An inscription that consumes a final note restarts its ageing, and one nobody can answer for keeps the holder out of the leadership lottery for up to two epochs. This part is proportional to the value of the notes moved.

One property shapes every choice below: bonded notes stay in the ledger and keep taking part in Proof of Stake. Over-collateralizing therefore costs an honest party liquidity, not yield, and every parameter is set on the conservative side.

# Parameters

| Parameter | Value | What it prices |
| --- | --- | --- |
| `COLLATERAL_MARGIN` | 2 | Fee prices moving between the posting and the dispute ([The Margin](#the-margin)) |
| `FLOOR_EXECUTION_GAS` | 4,490 | Execution Gas of the dispute of any inscription ([The Floor](#the-floor)) |
| `FLOOR_STORAGE_GAS` | 796 | Permanent Storage Gas of the dispute of any inscription ([The Floor](#the-floor)) |
| `INPUT_EXECUTION_GAS` | 590 | Execution Gas one input adds to an answer ([The Per-Input Rate](#the-per-input-rate)) |
| `INPUT_STORAGE_GAS` | 395 | Permanent Storage Gas one input adds to an answer ([The Per-Input Rate](#the-per-input-rate)) |
| `STATE_EXECUTION_GAS` | 590 | Execution Gas one declared pool transition adds to an answer ([The Per-Transition Rate](#the-per-transition-rate)) |
| `STATE_STORAGE_GAS` | 275 | Permanent Storage Gas one declared pool transition adds to an answer ([The Per-Transition Rate](#the-per-transition-rate)) |
| `STATE_PROVING` | one GPU-hour, in LGO at the genesis price | The off-chain proof of one declared pool transition ([The Per-Transition Rate](#the-per-transition-rate)) |
| `VALUE_RATE_PPM` | 5,000, that is 0.5% | The lock, per unit of value of the inputs, the reserves of the declared pools excluded ([The Value Rate](#the-value-rate)) |

For an inscription with $`n`$ inputs declaring $`d`$ pool transitions, [Channels](channels.md#collateral) requires three parts. The fee-priced part is `COLLATERAL_MARGIN` times the fee of `FLOOR_EXECUTION_GAS + INPUT_EXECUTION_GAS * n + STATE_EXECUTION_GAS * d` Execution Gas and `FLOOR_STORAGE_GAS + INPUT_STORAGE_GAS * n + STATE_STORAGE_GAS * d` Permanent Storage Gas, at the prices of the block that includes the inscription. The proving part is `STATE_PROVING` times $`d`$. The value part is `VALUE_RATE_PPM` parts per million of the value of its inputs, locked or not, the reserves of the declared pools excluded. The amount is recorded with the inscription. The sections below derive each parameter.

# Prices and Fees

A Mantle Transaction pays two fees. Its Execution Gas is paid at the base fee of its block, $`b_{\mathrm{exec}}[s]`$ of [Execution Market](execution-market.md). Its Permanent Storage Gas is paid at the price $`P_{\text{storage}}(s)`$ of [Storage Markets](storage-markets.md), and a transaction consumes exactly one unit of Permanent Storage Gas per byte of its encoding. Every count of bytes below is therefore a count of Permanent Storage Gas, and the fee of a transaction of $`g`$ Execution Gas and $`S`$ bytes is $`g \cdot b_{\mathrm{exec}}[s] + S \cdot P_{\text{storage}}(s)`$, which Channels writes `fee_cost(g, S)`.

The Execution Gas of each Operation is taken from [\[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md), and the size of each payload from [Mantle Transaction Encoding](mantle-transaction-encoding.md).

# Costs on Chain

Every transaction below pays its fee with a `TRANSFER` consuming one note and creating one note of change. That Operation is 75 bytes: 1 of opcode, 1 of input count, 32 for the `NoteId`, 1 of output count and 40 for the `Note`. Its proof, the `ZkSignature` of the consumed note, is 128 bytes and 590 Execution Gas.

**A challenge transaction.** The transaction starts with 1 byte counting its two Operations. The `CHANNEL_CHALLENGE` is 66 bytes: its opcode, the `OpId` of the challenged inscription (32) and a bond of one note (1 byte of count and 32 of `NoteId`). The fee `TRANSFER` is 75 bytes. The two proofs are two `ZkSignature`s, 256 bytes. In all, 398 bytes and 1,180 Execution Gas: 590 for the bond's signature and 590 for the fee transfer's.

**The fixed part of an answer.** The same, with a `CHANNEL_ANSWER` of 35 bytes before its steps: its opcode, the `OpId` of the inscription (32) and the step count (2). Its own proof is empty. In all, 239 bytes. Its Execution Gas is 590 for the fee transfer's signature, plus 3,900 when it has a pool step, for the batch of Risc0 receipts the answer verifies on its own: 4,490 at most.

**One user step of an answer.** A user step applying the authorization of one payment consumes one input and creates at least three notes: the payment, the change and the zone's fee. It is 283 bytes: its kind (1), the input (1 byte of count and 32 of `NoteId`), the three outputs (1 byte of count and 120 of `Note`s) and the authorization (128). Its Execution Gas is 590, the verification of one `ZkSignature`. An authorization with more outputs makes a larger step; that shortfall falls on whoever answers a wrong challenge, and changes no outcome.

**One pool step of an answer.** A pool step consumes the pool's reserve note and re-creates it, and consumes the deposits made to the pool. Its fixed part is 275 bytes: its kind (1), the instance (32), the reserve consumed as a `PoolInput` (1 byte of count, then 32 of `NoteId`, 8 of value and 32 of intent hash) and re-created as a `Note` (1 byte of count and 40), and the seal (128). Each deposit it consumes adds a `PoolInput` (72) and, at most, a payout `Note` (40): 112 bytes. Its Execution Gas is 590, the verification of one receipt in the batch, assumed to cost what a `ZkSignature` does until measured.

| Item | Bytes | Execution Gas |
| --- | --- | --- |
| Challenge transaction, one bond note | 398 | 1,180 |
| Answer, fixed part | 239 | 590, or 4,490 with a pool step |
| User step, one input, three outputs | 283 | 590 |
| Pool step, fixed part with the reserve in and out | 275 | 590 |
| Share of a pool step per deposit it consumes and pays | 112 | 0 |

# The Floor

The floor covers the two costs every dispute has, whatever the size of the inscription. Both bounds are at the prices of the posting block, before the margin.

- **A right challenge must pay.** The challenger receives half of what the inscription forfeits, so half the floor must cover a challenge transaction: at least twice 1,180 Execution Gas and twice 398 bytes, that is 2,360 and 796.
- **A wrong challenge must pay for the fixed part of the answer.** The sequencer receives the inscription's requirement, forfeited from the challenger's bond, so the floor must cover the fixed part of an answer: at least 4,490 Execution Gas and 239 bytes.

Taking the larger of each pair gives `FLOOR_EXECUTION_GAS = 4,490` and `FLOOR_STORAGE_GAS = 796`.

# The Per-Input Rate

A wrong challenge must also pay for the steps it forces. The most one input adds to an answer is a user step of its own and, when the payment it authorizes is a deposit to a pool, its share of that pool's step: `INPUT_EXECUTION_GAS = 590` and `INPUT_STORAGE_GAS = 283 + 112 = 395`.

The requirement counts inputs rather than outputs: it is the holders of the inputs whose notes are locked, and an inscription can consume a thousand notes into one output through a step of the sequencer's own.

# The Per-Transition Rate

A declared pool transition needs one pool step on chain, whatever the deposits it consumes, which the per-input rate already covers: `STATE_EXECUTION_GAS = 590` and `STATE_STORAGE_GAS = 275`. It also needs a proof, produced off chain, which gas does not price: an Execution Gas unit prices a validator's CPU time inside a scarce block, not a prover's machine. The proving part is therefore a token amount, `STATE_PROVING`, added once per declared transition.

A public pool's transition, a batch of swaps over a few million Risc0 cycles plus the Groth16 wrap, takes minutes on a data-centre GPU. A private pool's transition aggregates the private receipts of the period and is the heaviest case, about an hour for a thousand receipts. `STATE_PROVING` is set to one GPU-hour, about 2 to 3 USD at current cloud prices, converted into LGO at the price of the token at genesis, as the initial storage price is ([Storage Markets](storage-markets.md)). Since the bond keeps earning, sizing it for the private case costs a public pool almost nothing.

This part needs a measurement: the proving time of a reference pool program and of a private pool transition, on the hardware a sequencer is expected to run.

# The Value Rate

An inscription consuming a final note re-creates it, and the new note must age again before it can win the leadership lottery: up to two epochs, 15 days. A sequencer can do this to notes it has no authorization for. If challenged it loses, but the victims' notes are re-created under new identifiers and their ageing restarts anyway. Neither the floor nor the per-input rate grows with the value of those notes, while the harm does. A note under withdrawal changes nothing here: an inscription may consume it during the delay only, at the same price, and it leaves at the first unlock after its due.

The harm is also a gain for the attacker. Keeping value out of the lottery lowers the inferred total stake, which raises every other participant's share of the rewards. A participant holding a share of the eligible stake gains, per year of suppression, that share of the yearly Proof of Stake reward on the suppressed value. One attack suppresses the value for at most the two windows of the dispute, 3 days, plus the 15 days of ageing, 18 days, which is 0.049 year. The attacker's cheapest loss is half the forfeit, by challenging itself from a second key. With the value part of the forfeit set to a rate of the value moved, the attack is unprofitable when half that rate exceeds the attacker's share of the eligible stake, times the yearly reward rate, times 0.049. An attacker holds less than half of the eligible stake, so the attack is unprofitable for every attacker once the rate exceeds 0.049 times the yearly reward rate:

| Regime | Yearly reward rate ([Block Rewards](block-rewards.md)) | Minimum rate |
| --- | --- | --- |
| Inferred stake at its 30% target | 3.34% | 0.165% |
| Inferred stake at 10% of the maximum supply | 10% | 0.493% |

`VALUE_RATE_PPM` is set to 5,000, that is 0.5%, which covers the bootstrap phase. It can fall towards 1,700 once the inferred stake reaches its target.

Every input is counted, locked or not. Consuming a locked note before its creator is final extends the lock on its value: the new output waits for its own deadline, and a chain of inscriptions each consuming the output of the previous one could keep a holder's value locked indefinitely for the floor cost alone. Charging the value rate at each consumption makes each extension cost what the first lock cost. The reserve notes of a pool the inscription declares carry a pool key, behind which no secret key exists, so they never stake: the ledger recognizes them by recomputing `pool_key(image_id, instance_id, 0)` for each declared pool and leaves them out. Without that exemption, a large pool would pay 0.5% of its reserve on every swap.

The value part deters, it does not compensate: the forfeit pays the challenger and the rewards pool, not the victims.

# The Margin

A dispute is settled at the prices of the blocks that carry the challenge and the answer, up to 3 days after the inscription was posted. $`P_{\text{storage}}(s)`$ moves at most 12.5% per timeframe, so at most once in that span. $`b_{\mathrm{exec}}[s]`$ moves at most 12.5% per block under sustained full blocks. `COLLATERAL_MARGIN = 2` covers a doubling of either price between posting and dispute. A longer congestion leaves the sequencer under-compensated for the fees of its answer; it cannot make a valid inscription lose or an invalid one final.

# Arithmetic

Every amount is a `TokenValue`, a 64-bit unsigned integer, and Channels computes the requirement with `checked_uint64`: an inscription whose requirement does not fit is invalid. The fee part cannot reach that bound at any realistic price. An inscription has at most 255 inputs and 255 declared transitions, since the encoding counts each on one byte. The fee part is therefore at most twice the fee of 305,390 Execution Gas and 171,646 Permanent Storage Gas. It overflows only if a gas price exceeds about $`2^{64} / 610{,}780`$, that is $`3 \cdot 10^{13}`$ units of value per unit of gas. The proving part is at most 255 times `STATE_PROVING`.

The value part multiplies a value by `VALUE_RATE_PPM` before dividing by a million, and the value of the inputs can be a large share of the supply, so the product is computed on 128 bits. The quotient is below the value itself and fits a `TokenValue`.

# What It Costs a Sequencer

A sequencer must have bonded, at any time, the collateral of all its pending inscriptions, most of which are pending for one challenge window. Take a zone that nets 2,000 payments a day into 100 inscriptions of 20 inputs, and moves 1 million LGO of notes a day. About 200 inscriptions are pending at any time:

- the fee-priced part is 200 times twice the fee of 16,290 Execution Gas and 8,696 bytes, twice the fees of answering all of them, of the order of the fees of two full blocks;
- the value part is 0.5% of 2 million LGO, 10,000 LGO;
- a zone whose every inscription advances a swap pool adds 200 times `STATE_PROVING`, of the order of 500 USD in LGO at the genesis price.

The bonds keep earning their Proof of Stake rewards, so the sequencer's cost is the liquidity of about 10,000 LGO plus the fee-priced and proving parts, not a yield. A challenger bonds the requirement of the one inscription it challenges, under the same terms.

# What Is Not Priced

An inscription declaring a pool transition nobody can prove stalls that pool until it loses, up to both windows: no other sequencer can build on the false state or declare from another one. Its collateral does not grow with the value the pool holds, since the reserve is left out of the value part. Only an accredited sequencer can do it, on its turn, and it forfeits its requirement each time, so under round-robin sequencing the remedy is to remove its key. A permissionless sequencer set would need this priced, for instance by a rate on the declared pool's reserve.

# Open Measurements

- The proving time of a reference pool program and of a private pool transition, which sets `STATE_PROVING`.
- The verification cost of a Risc0 Groth16 receipt batch, assumed equal to a `ZkSignature` batch in [\[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md).
- The LGO price at genesis, which converts `STATE_PROVING`.
