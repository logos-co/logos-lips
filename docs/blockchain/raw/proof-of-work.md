# PROOF-OF-WORK

| Field | Value |
| --- | --- |
| Name | Proof of Work |
| Slug | 245 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors |  |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-09-09 |
| 1.1.0 | Set the reference load of the Blend difficulty to the transaction rate the Blend network carries, `F_T / F_D = 130` transactions per block | 2026-09-11 |

# Introduction

Posting a transaction to the chain or sending a message through the Blend network requires tokens. A participant who arrives with nothing therefore cannot use the protocol.

Proof of work removes this obstacle. A participant who has computed a puzzle solution may use it to post transactions and to send messages through Blend. Neither use has a prerequisite beyond the computation itself. The cost is the hardware and the electricity it burns, and it cannot be faked, since a valid ticket proves the work, and a validator checks it cheaply.

The puzzles are measured against separate thresholds that follow separate objectives:

- the reward threshold keeps the number of paid claims per block near a target whatever the amount of mining,
- and the Blend threshold keeps admission to the network affordable when the network is quiet and dearer when it is busy.

This document specifies the puzzle, the two thresholds, the pow reward pool and the reward it pays per claim, and the window within which a reward may be claimed. The Blend side of the mechanism is specified in [Proof of Quota](proof-of-quota.md) and the claim Operation in [Mantle](bedrock-v1.1-mantle-specification.md#claim_pow_reward); this document holds what both depend on.

# Overview

A miner finds a solution only by trying values until one of them hashes below a threshold, so a solution costs electricity and nothing else: no tokens, no stake, no permission. Checking a solution costs a single `zkhash`.

A solution is spent on one of two things, and this is how a participant that holds nothing starts using the protocol.

```mermaid
graph LR
    p["a participant with<br/>no tokens and no stake"] --> s["mines a puzzle solution"]
    s --> b["sends Blend messages"]
    s --> c["claims tokens from the<br/>pow reward pool"]
    c --> t["pays for transactions"]
```

The tokens come from the pow reward pool, set aside at genesis. Nothing is minted for it, so mining does not inflate the supply. Each epoch pays out a fraction of what the pool still holds, so the reward is the same for every claim of that epoch, for as long as the pool can pay it.

Each use has its own threshold, and a threshold sets how much work a solution costs. Every node computes both from what blocks carry, so no node trusts another for them.

The reward threshold reads the claims in a block, the only sign of mining the chain has.

```mermaid
graph LR
    m["amount of mining"] -- "rises" --> mh["puzzle harder"]
    m -- "falls" --> me["puzzle easier"]
    mh --> mt["about ten paid claims<br/>per block"]
    me --> mt
```

The two branches end in the same place. About ten claims are paid per block once mining is heavy enough to find that many, so more mining changes the work behind a claim and not the number of claims paid.

A claim must name a recent block, so a solution cannot be spent long after it was found.

The Blend threshold reads the transactions in a block.

```mermaid
graph LR
    l["transactions per block"] -- "rises" --> lh["puzzle harder"]
    l -- "falls" --> le["puzzle easier"]
    lh --> lm["admission costs more"]
    le --> ll["admission costs less"]
```

Here the branches end apart. Nothing absorbs the load, so a Blend message costs more work when blocks are full and less when they are quiet.

# Protocol

```mermaid
graph TB
    sv["searched value"] --> tk["ticket<br/>zkhash(searched value,<br/>epoch nonce)"]
    tk -- "does not satisfy<br/>the threshold" --> sv

    tk -- "satisfies<br/>difficulty_blend" --> pq["Proof of Quota"]
    pq --> bm["Blend messages"]

    tk -- "satisfies<br/>difficulty_reward" --> cl["CLAIM_POW_REWARD"]
    cl --> vc["checked in<br/>a block"]
    vc -- "a check fails" --> iv["transaction<br/>invalid"]
    vc -- "accepted" --> ac["epoch_pow_reward<br/>paid to the key<br/>ticket spent<br/>pow_reward_pool falls"]
```

A miner picks a value and hashes it into a **ticket**. The hash is `zkhash` over the value and the [Epoch Nonce](cryptarchia-v1-protocol.md#epoch-nonce). A claim search hashes the referenced block hash as well. Tickets and **thresholds** are numbers in $`\mathbb{F}_p`$, the BN254 scalar field of [Poseidon2](common-cryptographic-components.md#poseidon2-zk-friendly-hash-function). A ticket satisfies a threshold when the ticket is below it, as [Puzzle Target](#puzzle-target) specifies. The miner keeps picking values, each sampled with full entropy, until one ticket satisfies the threshold.

Each use searches its own value against its own threshold, so a solution works for one use only. For Blend admission the miner searches a private nonce against `difficulty_blend`. The nonce stays secret. [Proof of Quota](proof-of-quota.md) proves the miner holds one, and that buys the quota of blending operations given in [Proof of Work Quota](blend-protocol.md#proof-of-work-quota). Nothing about it reaches the chain. For a reward the miner searches public keys whose secret keys it knows, against `difficulty_reward`. The miner then publishes a `CLAIM_POW_REWARD` Operation in a transaction.

A validator checks a claim against the `difficulty_reward` the previous block produced. A block's own claims update `difficulty_reward` after the block is processed, and that new value governs the next block. The validator accepts a claim when all of these hold:

- the ticket is below `difficulty_reward`,
- the ticket has not been claimed before,
- the referenced block is canonical and inside the acceptance window,
- the epoch nonce is the current one or the one before it,
- the transaction is signed by the key the claim names, which proves the signer knows its secret key,
- `epoch_pow_reward` is positive and `pow_reward_pool` still holds it.

[Mantle](bedrock-v1.1-mantle-specification.md#claim_pow_reward) specifies these checks and the order they run in. A claim that fails any of them makes its transaction invalid. On acceptance the node pays `epoch_pow_reward` to the key, marks the ticket spent, and subtracts the same amount from `pow_reward_pool`.

A node computes five values from the chain. `pow_reward_pool` and the set of spent tickets change when a claim is accepted. `difficulty_reward` is recomputed after every block, from the number of claims in that block. `epoch_pow_reward` is recomputed at each epoch boundary, from `pow_reward_pool`. `difficulty_blend` is recomputed once per epoch, from the transactions of the epoch before last, at the snapshot that fixes the epoch nonce. [Reward Difficulty](#reward-difficulty), [Reward Pool](#reward-pool) and [Blend Difficulty](#blend-difficulty) specify the three computations.

A node keeps a spent ticket only while its referenced block is inside the window, so the set stays small. [Acceptance Window](#acceptance-window) gives the window in slots.

# Details

## Notation

| Symbol | Name | Description |
| --- | --- | --- |
| $`p`$ | field modulus | Modulus of the scalar field $`\mathbb{F}_p`$ of [Poseidon2](common-cryptographic-components.md#poseidon2-zk-friendly-hash-function); tickets and thresholds are its elements. |
| $`T`$ | target claims per block | `TARGET_CLAIMS_PER_BLOCK`, the accepted rate the reward threshold steers toward. |
| $`\rho`$ | distribution rate | `EPOCH_POW_DISTRIBUTION_RATE_NUM / EPOCH_POW_DISTRIBUTION_RATE_DEN`, the fraction of the pool an epoch distributes at the target rate. |
| $`N_b`$ | expected blocks per epoch | `EXPECTED_BLOCKS_PER_EPOCH`, the epoch length in slots of [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule) times $`f`$. |
| $`W_b`$ | window depth | `EXPECTED_BLOCKS_PER_WINDOW`, the acceptance window in expected blocks. |
| $`F`$, $`P`$ | smoothing factor and precision | `EMA_SMOOTHING_FACTOR` and `EMA_SMOOTHING_PRECISION`; the reward update weighs the previous estimate $`F`$ out of $`P`$. |
| $`\alpha = a / b`$ | damping exponent | `BLEND_DAMPING_NUM / BLEND_DAMPING_DEN`, the Blend update's response to the load ratio. |
| $`S_{cap}`$ | maximum supply | The hard cap of [Block Rewards](block-rewards.md). |
| $`f`$ | slot activation coefficient | The probability that a slot has a leader, $`1/30`$, from [Constants](cryptarchia-v1-protocol.md#constants). |
| $`k`$ | security parameter | $`2160`$, from [Constants](cryptarchia-v1-protocol.md#constants). |

## Parameters

```python
POW_REWARD_POOL_GENESIS: TokenValue             # 5/1000 of S_cap, set in the Genesis Block
EPOCH_POW_DISTRIBUTION_RATE_NUM: uint64 = 1     # rho, as a fraction NUM / DEN
EPOCH_POW_DISTRIBUTION_RATE_DEN: uint64 = 200
TARGET_CLAIMS_PER_BLOCK: uint64 = 10            # T
EXPECTED_BLOCKS_PER_EPOCH: uint64 = 21_600      # N_b = 10 k
EXPECTED_BLOCKS_PER_WINDOW: uint64 = 10         # W_b
EMA_SMOOTHING_FACTOR: uint64 = 9                # F, the weight given to the previous estimate
EMA_SMOOTHING_PRECISION: uint64 = 10            # P, the scale F is expressed against; F < P
BLEND_DIFFICULTY_BASE: PowTarget = p // 2**19   # difficulty_blend at the reference load
TARGET_TXS_PER_BLOCK: uint64 = 130              # Reference transactions per block, F_T / F_D
BLEND_DAMPING_NUM: uint64 = 1                   # a, where the exponent is alpha = a / b
BLEND_DAMPING_DEN: uint64 = 2                   # b, with 0 < a <= b so that alpha <= 1
BLEND_MAX_STEP: uint64 = 2                      # Max factor difficulty_blend may move per epoch
```

The parameters must give an `epoch_pow_reward` above the fee of a claim transaction, which pays for the claim and the `TRANSFER` that spends its note, or a claim cannot pay its own fee.

`TARGET_TXS_PER_BLOCK` is the transaction rate the Blend network carries, $`F_T / F_D = 130`$ transactions per block ([Global Parameters](blend-protocol.md#global-parameters)).

## Puzzle Target

`PowTarget` is an element of $`\mathbb{F}_p`$, as every ticket is. A ticket satisfies a target when its canonical integer representative in $`[0, p-1]`$ is strictly below the target's; a smaller target is a harder puzzle. A representative is at most 254 bits, so a 256-bit unsigned integer holds any target.

The two updates below multiply and divide targets as integers rather than in the fixed-width types of [Arithmetic](bedrock-v1.1-mantle-specification.md#arithmetic), and cap their result at $`p - 1`$, so that it converts back to a field element without reduction. Every intermediate fits in **512 bits**: the reward retarget's product reaches $`2^{261}`$ and the Blend radicand $`2^{493}`$. Each operation is integer addition, multiplication, floor division or comparison, and `integer_nth_root` returns the exact floor, so two implementations agree exactly.

## Reward Pool

The pool is seeded once, at genesis, with `POW_REWARD_POOL_GENESIS`, five thousandths of $`S_{cap}`$, as specified in [Bedrock Genesis Block](bedrock-genesis-block.md). After that it changes only through claims.

```python
def compute_epoch_pow_reward(pow_reward_pool: TokenValue) -> TokenValue:
    denominator = (EPOCH_POW_DISTRIBUTION_RATE_DEN
                   * TARGET_CLAIMS_PER_BLOCK
                   * EXPECTED_BLOCKS_PER_EPOCH)
    return (pow_reward_pool * EPOCH_POW_DISTRIBUTION_RATE_NUM) // denominator
```

At each epoch boundary, before any block of the new epoch is processed, `epoch_pow_reward` is set to `compute_epoch_pow_reward(pow_reward_pool)` and held for the epoch. The division rounds down, and the remainder stays in the pow reward pool. All arithmetic here is checked, in accordance with [Arithmetic](bedrock-v1.1-mantle-specification.md#arithmetic).

### Exhaustion within an epoch

The reward is fixed for the epoch while the pool shrinks with every claim. The first condition of [CLAIM_POW_REWARD](bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation, that the reward is positive and the pool covers it, is evaluated for every claim against the pool as it stands at that point in the block, and a claim it rejects invalidates its transaction. Claiming resumes at the next epoch boundary at which the recomputed reward is positive and the pow reward pool covers it.

## Acceptance Window

$$
\mathrm{WINDOW} = \left\lfloor \frac{W_b}{f} \right\rfloor
$$

With $`W_b = 10`$ and $`f = 1/30`$, `WINDOW` is $`300`$ slots. A claim's referenced block must be canonical and at most `WINDOW` slots older than the block including the claim; the check is step 2 of [CLAIM_POW_REWARD](bedrock-v1.1-mantle-specification.md#claim_pow_reward) validation. A nullifier may be discarded once the block its claim referenced has left the window.

## Reward Difficulty

```python
def compute_new_reward_difficulty(claims_in_block: uint64,
                                  current_target: PowTarget) -> PowTarget:
    # 512-bit integers over canonical representatives; see Puzzle Target.
    # The demand implied by this block, reconstructed from the target that produced
    # it and smoothed against the target rate; floored at 1 so the division is defined.
    demand = max(1, (EMA_SMOOTHING_PRECISION - EMA_SMOOTHING_FACTOR) * claims_in_block
                    + EMA_SMOOTHING_FACTOR * TARGET_CLAIMS_PER_BLOCK)
    new_target = (TARGET_CLAIMS_PER_BLOCK * current_target
                  * EMA_SMOOTHING_PRECISION) // demand
    return min(new_target, p - 1)
```

`claims_in_block` counts the `CLAIM_POW_REWARD` Operations the block includes. Every claim in a block is validated against the target produced by the previous block's update; the update from a block's own count is applied after the block is processed and governs the next block. At genesis `difficulty_reward` is the quotient of the Euclidean division of the scalar field modulus by $`2^{26}`$.

## Blend Difficulty

`difficulty_blend` for epoch $`N`$ is computed at the lottery-constants snapshot of epoch $`N-1`$ specified in [Epoch](cryptarchia-v1-protocol.md#epoch), the moment epoch $`N`$'s nonce is fixed, from the blocks of epoch $`N-2`$, and is the public input `pow_blend_difficulty` of [Proof of Quota](proof-of-quota.md) for the whole of epoch $`N`$. For epochs 0 and 1 it is `BLEND_DIFFICULTY_BASE`; the schedule begins with epoch 2, computed during epoch 1 from epoch 0's blocks.

```python
def compute_epoch_blend_difficulty(epoch_blocks: list[Block],   # the blocks of epoch N-2
                                   previous: PowTarget) -> PowTarget:  # difficulty_blend of epoch N-1
    # 512-bit integers over canonical representatives; see Puzzle Target.
    # Observed load as an exact ratio: num == den at the reference load.
    num = sum(num_transactions(b) for b in epoch_blocks)
    den = TARGET_TXS_PER_BLOCK * len(epoch_blocks)

    lo = previous // BLEND_MAX_STEP
    hi = min(previous * BLEND_MAX_STEP, p - 1)

    if num == 0:
        return hi   # No load observed: as permissive as this epoch's clamp allows.

    # A smaller target is harder, so load divides the baseline:
    #     target = BASE / load ** alpha
    # Only the final root is floored, so the result is at most one unit from exact.
    a, b = BLEND_DAMPING_NUM, BLEND_DAMPING_DEN
    radicand = (BLEND_DIFFICULTY_BASE ** b * den ** a) // num ** a
    return clamp(integer_nth_root(radicand, b), lo, hi)

def integer_nth_root(x: int, n: int) -> int:
    # The floor of the real n-th root: the largest integer r with r**n <= x.
    # Any exact method serves; this reference is a binary search.
    lo, hi = 0, 1 << (x.bit_length() // n + 1)   # hi**n > x by construction
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if mid ** n <= x:
            lo = mid
        else:
            hi = mid
    return lo
```

`previous` is the value computed one snapshot earlier. `BLEND_DIFFICULTY_BASE` is calibrated against a measurement of the work itself: about 38 seconds per solution in expectation on one core of the target machine, a Raspberry Pi 5, measured on that hardware.
