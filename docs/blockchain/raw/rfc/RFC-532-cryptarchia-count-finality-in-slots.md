# [RFC] Cryptarchia: Count finality in slots

**Motivation and proposal:** [PR #532](https://github.com/logos-co/logos-lips/pull/532)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |
| v2 | Merged master, and applied the wording again to its rewritten oracle zone document | 2026-11-17 |
| | The last round before the switch takes each tip from the peer that returned it, repeats its steps for each peer, names in its requests blocks that an honest peer is likely to hold, and waits at most `T_offline` for a peer that is not an IBD peer. Qualified the claim that one honest answer closes the case | |
| | A node restarts with the Bootstrap rule if it stopped under it, or if it cannot tell how long it was offline. It stores `c_loc`, `B_imm` and its fork choice rule together, where v1 recorded the switch with the result of its `commit` | |
| | `2·s_gen ≤ K` replaces `s_gen < K`. The `K` row states what `K` must hold. The Online rule visits forks by block ID | |
| | [The epoch nonce](#the-epoch-nonce) states what each nonce design gives, that 18 hours takes a nonce with a delay, what the nonce's RFC is to propose, and when it should be adopted | |
| | Corrected the floor's count by one honest uncle, "does not worsen", the restart path against the 15 s case, and two figures: 6.5 hours for 30 % after a deflated inference, and the limit of 2.628 on joining stake. Added honest stake offline, a split in halves, and the participation the epoch's waits need | |
| | Removed the statement that the node does not wait `s_gen` slots after Initial Block Download | |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the rule](#1-the-latest-immutable-block-is-counted-in-slots) | the `commit` loop, its first slot and its last slot; `K`, what it must hold, and `φ` ([What the finality window holds](#what-the-finality-window-holds), [The finality floor](#the-finality-floor)) |
| 2 | Critical | [Fork Choice Rule](#affected-specifications), [Cryptarchia Protocol](#affected-specifications): [both rules](#2-the-fork-choice-rules-read-the-age-of-a-fork-in-slots) | the Bootstrap test runs on every block; both rules visit forks by block ID; the Online rule's only bound is descent from `B_imm` ([Comparing forks](#comparing-forks)) |
| 3 | Critical | **Start here** — [Bootstrapping & Synchronization](#affected-specifications): [the switch](#3-the-switch-to-online-runs-a-last-round-and-commit) | the last round takes each tip from the peer that returned it, and waits at most `T_offline` for a peer that is not an IBD peer; a fork whose divergence block `commit` passes must not win after the switch, even across a restart; the rule a restart takes, and what it loads ([The switch to Online](#the-switch-to-online)) |
| 4 | High | [Cryptarchia Protocol](#affected-specifications): [the epoch schedule](#4-the-finality-window-sets-the-epoch-schedule) | every epoch value stays as it is |
| 5 | Medium | [Cryptarchia Protocol, Fork Choice Rule, Bootstrapping & Synchronization](#affected-specifications): [three periods](#5-three-periods-stay-within-the-finality-window) | the bound on the uncle window, and two density windows within `K` |
| 6 | Medium | [Total Stake Inference](#affected-specifications): [the count](#6-the-count-of-occupied-slots-takes-a-chain) | the inference's own count does not change |
| 7 | Medium | [Cryptarchia Protocol](#affected-specifications): [fork pruning](#7-fork-pruning-removes-every-fork) | one call removes every fork |
| 8 | Low | [Chores](#chores) | skim |

# Discussion

## What the finality window holds

`K` is 64,800 slots, 18 hours. This section gives the share of stake it holds at a chance of `1e-9` per block that a block made immutable is displaced.

The figures come from the finality study ([Reproducing the figures](#reproducing-the-figures)), under two delay models.

- **Worst case.** An adversary delivers every honest block as late as a bound `Δ` allows, taken at `Δ = 10` s, about the 99th percentile of delivery on the specification's Blend. The study reads the model of Gaži, Ren and Russell ("Practical Settlement Bounds for Longest-Chain Consensus", ePrint 2022/1571) for a wait on the 1 s slot lottery. `K` binds every node, so it must hold under this model.
- **Random delay.** Blocks take Blend's mixing delays, measured in a simulation of 1,000 nodes. Only the private attack is played, with honest relays.

The figures name two cases of the epoch nonce. A nonce that **cannot be ground** gives an adversary no choice among nonces. A nonce that **resists grinding** lets an attack raise its chance by a factor of at most 1.21 when it lasts across an epoch boundary and so meets two nonces. That is the bound the study derives for its candidate ([The epoch nonce](#the-epoch-nonce)).

The wait that holds that chance, in hours:

| Case | 30 % | a third |
| --- | --- | --- |
| Worst case at 10 s, a nonce that cannot be ground | 5.9 | 10.1 |
| Worst case at 10 s, a nonce that resists grinding | 6.0 | 10.2 |
| Worst case at 10 s, today's nonce, one ground nonce | 13.6–14.1 | 25.9–26.7 |
| Worst case at 10 s, today's nonce, two ground nonces | 16.1–18.7 | 38.3–42.0 |
| Worst case at 10 s, a nonce that cannot be ground, after a deflated inference | 6.4 | 12.4 |
| Worst case at 10 s, a nonce that resists grinding, after a deflated inference | 6.5 | 12.5 |
| Worst case at 10 s, a nonce that cannot be ground, 90 % of the honest stake online | 8.4 | 16.2 |
| Worst case at 10 s, a nonce that resists grinding, 90 % of the honest stake online | 8.5 | 16.4 |
| Worst case at 15 s, a nonce that cannot be ground | 9.4 | 17.4 |
| Worst case at 15 s, a nonce that resists grinding | 9.5 | 17.5 |
| Worst case at 15 s, a nonce that cannot be ground, after a deflated inference | 14.2 | 35.6 |
| Worst case at 20 s, a nonce that cannot be ground | 16.1 | 33.5 |
| Random delay, a nonce that cannot be ground | 3.1 | 5.1 |

- The ranges span two bounds on the grinding factor. Neither end is an attack.
- The `K` row of the specification names two of these cases, with the epoch nonce taken as unbiased, which is a nonce that cannot be ground: a delay of `T_M`, 15 s, where a third needs 17.4 hours, and 10 s with a tenth of the honest stake offline, where it needs 16.2. With a nonce that resists grinding they are 17.5 and 16.4.
- The rows on honest stake offline read the lottery once the inference has corrected to the stake that is online. At 10 s, with a nonce that resists grinding, 18 hours holds a third down to 89 % of the honest stake online, and not at 88 %, where the wait is 18.4 hours.
- A deflated inference is what an adversary gets by withholding every block for one observation period, 4.5 days. The inferred stake falls by its share, and every lottery threshold rises by `1/(1 − α)` for the next epoch. With the honest stake alone filling slots at `f`, the fixed delay weighs more.
- Stake that joins faster than the inference corrects has the same effect: blocks come faster than `f` until the next correction, and under the worst case faster blocks need a longer wait. Against a third at 10 s, without grinding, 18 hours holds while the true active stake stays within 1.925 times the inferred, and against 30 % within 2.628 times. A deflation, or a third's coalition entering, makes 1.5. A rise of the active stake from 15 % to 30 % of the supply before the inference corrects breaks the limit against a third, and needs 19.6 hours.
- The 12.5 hours takes the nonce's factor at the old rates, where its bound is derived.
- After 18 hours against a third at 10 s, the chance of displacement is `1.2·10^-16` without grinding and `8.4·10^-14` after a deflated inference.
- The delay leaves little margin after a deflation. Against a third, with a nonce that cannot be ground, 18 hours holds up to 15 s without a deflation. After one it holds up to 11 s, where the wait is 14.9 hours, and not at 12 s, where it is 18.2. The study prints deflated waits only at 1, 10 and 20 s, so the figures from 11 s to 15 s come from running its bound for this RFC.
- The bound is the chain of Gaži, Ren and Russell frozen at the phase in which the wait passes, with each phase's span charged at its longest. The paper's attack, played against a wait on the slot lottery at 1 s and 10 s and at waits up to 2 hours, succeeds 0.26 to 0.82 times as often as the bound allows against a third.
- Delivery later than `Δ` lies outside the bound. Under honest mixing on the specification's Blend, that is about one block in a hundred.

### The epoch nonce

This RFC does not change the epoch nonce. Today's nonce is a hash chain over the leaders' contributions, and a coalition grinds it by withholding or forking its blocks near the cut-off, the slot at which the next epoch's nonce is read. At 15 s of delay, 18 hours holds a third only with a nonce that resists grinding. The `K` row takes the epoch nonce as unbiased, and says that a nonce an adversary can bias lowers the share `K` holds. A nonce that resists grinding is required before genesis, in its own RFC.

The largest share each rule holds with today's nonce, with two ground nonces at the upper end of the factor:

| Delay model | `k` = 2,160 blocks | `K` = 18 h |
| --- | --- | --- |
| Worst case at 10 s | 0.288 | 0.298 |
| Worst case at 15 s | not computed | 0.274 |
| Random delay on the specification's Blend | 0.358 | 0.322 |

- With a nonce that resists grinding, 18 hours holds at least a third in all three rows.
- Under random delay the depth rule holds more with today's nonce, because 2,160 blocks take 30 to 32 hours on that model's clock while 30 % to a third withholds, and `K` stays at 18. With no one withholding they take 21 hours.
- Under the worst case at 10 s the two figures come from different bounds: 0.288 from a depth bound and 0.298 from the wait bound. So 0.298 against 0.288 does not show a gain.
- Two ground nonces reach only targets past the cut-off and within `K` slots of the epoch's end: 10 % of targets at 18 hours. On a chain that meets the floor, a race lasts about `K`, far below the `4K` slots from a cut-off to the next epoch, so the grinding bounds cover every target.
- Bedrock has no deployed network, so these shares describe the specification only until the nonce's RFC lands.

The wait depends on how the nonce is made. The least wait that holds a third at `1e-9` under the worst case at 15 s, for an attack that meets two nonces:

| Epoch nonce | Wait (hours) | In whole hours |
| --- | --- | --- |
| The study's candidate: the smallest contributions of 25 sub-windows, each bound to its parent's, under a sequential delay | 17.5 | 18 |
| The same contributions without the delay | 21.4–22.3 | 23 |
| Today's hash chain, with at most `2^8` candidates evaluated in an epoch | 24.0–26.1 | 27 |
| Today's hash chain, with at most `2^16` | 31.3–33.4 | 34 |
| Today's hash chain, with at most `2^24` | 38.6–40.7 | 41 |
| Today's hash chain | 75.4–77.6 | 78 |

- A sequential delay is a function whose steps cannot be run in parallel. A cap on candidates is what a delay function gives when a coalition can run it in parallel, as Ouroboros Phalanx (CIP-0161) proposes: the coalition evaluates as many candidates as its machines and its time allow. The study places Phalanx's cap between `2^8` and `2^16`.
- The candidate's factor, 1.21, and the factor without the delay are derived at 10 s. The other rows take the factor at 15 s.
- So at 15 s, 18 hours takes a nonce with a sequential delay. At 10 s the candidate without its delay would do: a third then needs 12.4 to 13.0 hours.

**What the nonce's RFC is to propose.** The study's candidate changes how the nonce is made, in three steps. The proof of leadership and the epoch schedule stay as they are.

1. A block's contribution is bound to its parent's: `c(b) = hash(c(parent) ‖ ρ_LEAD(b))`, under its own domain separator. A contribution of a fork then exists only once the blocks before it do, so a coalition cannot compute it ahead.
2. The 108 hours before the cut-off are split into 25 sub-windows of 4.32 hours. The pre-nonce is a hash of the previous nonce and the smallest contribution of each sub-window. A withheld or displaced block changes the pre-nonce only if its contribution was the smallest of its sub-window.
3. The nonce is a hash of the output of a sequential delay function on the pre-nonce, Wesolowski's over a class group. The delay takes 4.49 hours on the fastest hardware: one sub-window and a margin of 10 minutes. A coalition then sees the nonce a choice gives only after it had to make the choice.

A block of the last phase carries the output with its proof, and every node verifies the proof in place of the computation. An honest node computes for `R` times 4.49 hours, where `R` is how much faster the fastest hardware is than the node's: 13.5 hours at `R = 3`, 22.4 at 5 and 44.9 at 10. The 72 hours from the cut-off to the next epoch hold `R` up to 16. Published chips and designs give `R` between 3 and 5.

The design is not settled. Three things are open:

- The delay function has no measured prototype at this length, so `R` rests on other projects' figures.
- The candidate has not been compared with a single delay on today's cut-off value, which changes fewer rules.
- What a node does when no block carries the output by the first slot of the epoch is not specified.

**When it should be adopted.**

- Before genesis. Until it lands, 18 hours holds the shares of the first table of this section, below the third its row names.
- In either order with this RFC. This RFC changes how finality is counted, and it sets `K` to `⌊k/f⌋`, the unit the epoch already has. Neither change reads the design of the nonce.
- Before any change that shortens `K`. The table above gives each design its own least wait, so a shorter window can be sized only once the design is chosen.
- The `K` row requires its cases to be checked again when the epoch nonce changes, so the nonce's RFC reads `K` again. If it adopts a design of a lower row, `K` moves to that row's wait.

### Alternatives

- **`K = 3⌊k/f⌋`, 54 hours.** Under the worst case it holds a third with today's nonce, and it fits the epoch without changing it. Every block then waits three times as long.
- **The least `K` that holds.** It is 12.5 hours against a third at 10 s, after a deflated inference. It is not `⌊k/f⌋`, so it adds a parameter beside `k`. It also leaves the delay no margin, where 18 hours reaches 11 s after a deflation.

### A change of parameters

`K = ⌊k/f⌋` shrinks as `f` rises, while a faster block rate needs a longer wait, because a fixed delay costs more block intervals. Against a third under the worst case at 10 s, without grinding:

| Mean block interval | `⌊k/f⌋` (hours) | Wait that holds (hours) |
| --- | --- | --- |
| 30 s | 18 | 10.1 |
| 20 s | 12 | 12.5 |
| 15 s | 9 | 20.4 |

This is why the `K` row asks for its two cases to be checked again, and for `φ` to be derived again, when `k`, `f`, the slot length, `T_M`, the epoch nonce or a target of the floor changes. The first case reads `T_M` itself, 15 rounds of one slot each. `T_M` and the floor's `Δ` are counted in slots, but the analysis sizes them in seconds at 1-second slots. `T_M` is 15 rounds and leaves out the gossip after the last hop, so a strict delay bound lies past the 15 s that 18 hours holds without a deflation, and past the 11 s it holds after one.

## The finality floor

Without a floor, a node fixes its chain once a block the rest of the network lacks is `K` slots behind its tip, whatever stake made it. An eclipsed node fixes the chain it is shown, or the chain it makes itself, 18 hours after that chain's first block, for every share from a tenth up. `φ` delays this: `B_imm` passes a block only once `φ` occupied slots follow it.

`φ` is the lower tail of the blocks the honest chain makes in `K` slots while `α_max` withholds, with every honest block delivered `Δ` late. The tail's chance is `1e-9`. The gap between blocks is `Δ` plus a geometric wait at `p_h = 1 − (1 − f)^(1 − α_max)`, so the chance is a negative binomial tail:

| `α_max` | `Δ` | Mean blocks in `K` | `φ` | `P(N < φ)` |
| --- | --- | --- | --- | --- |
| 1/3 | 10 | 1,183.6 | **1,019** | 9.3e-10 |
| 0.3 | 10 | 1,231.0 | 1,064 | 8.2e-10 |
| 1/4 | 10 | 1,300.4 | 1,131 | 8.3e-10 |

These targets size the floor. They claim nothing about Blend. Missing the floor costs time, not safety, because finality waits for the next blocks. While a third withholds:

| Worst-case delay | Mean blocks in `K` | `P(N < 1,019)` |
| --- | --- | --- |
| 10 s | 1,183.6 | 9.3e-10 |
| 15 s | 1,084.6 | 3.4e-3 |
| 20 s | 1,000.8 | 0.80, about 22 minutes' wait on average |

For the floor, the specification therefore states the chance only at `Δ = 10`, and makes no statement at `T_M`. The `K` row states its own cases: one at `T_M`, 15 slots, and one at `Δ` with honest stake offline. The two delays differ on purpose: missing the floor costs time, and a `K` that is too short costs safety.

The count covers the slots after the block, up to and including the slot of the tip, as `density_over_slots` counts them. Every canonical block occupies its own slot, so the count of occupied slots is at least the count of blocks, and a floor sized on blocks keeps its liveness. Under random delay a floor on occupied slots could stand at 1,225. Under the worst case no larger lower bound is derived, because an adversary that orphans a run of honest blocks leaves one countable uncle. An uncle counts only a genuine lottery win, and a slot counts once. So a side cut off from the rest counts the slots it won, and the slots of the honest blocks that hang from its chain, which its blocks can reference as uncles for 360 slots. In practice that is the first honest block after the divergence block.

The floor holds back a side cut off from the rest until it has made `φ + 1` blocks, or `φ` with that uncle. The table takes `φ + 1`. With `φ`, each figure is lower by 0.1 %:

| The side's share of the stake | Days to fix its fork, mean | Earliest at `1e-9` |
| --- | --- | --- |
| 0.1 | 3.49 | 2.87 |
| 0.2 | 1.75 | 1.44 |
| 0.25 | 1.40 | 1.15 |
| 0.3 | 1.17 | 0.96 |
| a third | 1.05 | 0.87 |

- This is about half of the 2.2 and 7.4 days that 2,160 blocks give a third and a tenth.
- The floor holds back past `K`, with chance `1 − 1e-9`, a side of at most 0.385 of the stake. A side of 0.4 makes its `φ + 1` blocks after 0.88 days on average.
- The protection ends when a sparse chain's inferred stake corrects. A side keeps its thresholds for at least 3 days, and has corrected in full 7.5 to 15 days after the split.

### What the floor leaves open

- **Partitions.** The adversary signs on both sides of a partition, so no floor separates one at a third. At 18 hours a side the floor holds back has at most 0.052 of honest stake when a third signs on it. A split the adversary signs on waits for operators. A network split in halves fixes the chain of each half after 18 hours, where 2,160 blocks take a half 35.7 hours. After that the split does not heal by itself.
- **An eclipse.** A fork started at the eclipse takes a third 1.05 days. A fork prepared in advance needs the eclipse only for the last part of that. At mean rates with no delivery delay, against a node that received the honest chain until the eclipse began, a third's fork needs an eclipse of about 12.5 hours, where 2,160 blocks need about 27. With the delay of the specification's Blend, they need about 10 and 22. How long an adversary can hold an eclipse is open.

### Alternatives

- **A floor on the density of the `K` slots after the block.** It holds a sparse side back for 8.25 days at the earliest. But it stalls finality whenever the active stake falls below 0.562 under random delay, for up to 11.25 days. The floor used here never stalls: a block made as the active stake halves is fixed after 0.75 days on average under random delay.
- **A cap on the inference's correction.** The inference reads a side cut off as stake that left, so a cap lengthens the protection and the stall after a genuine fall alike. The floor used here gains little from a cap at 18 hours. A side of a tenth or more makes its `φ + 1` blocks within 3.5 days on average, and a correction that comes sooner reads at most a ninth of its observation period after the split. The inference's correction stays uncapped.

## Counting from the tip's slot

`K` counts back from the slot of the tip of `c_loc`, not from the clock. `commit` therefore reads no clock and needs no tick per slot. A block is final `K` slots after its slot, plus the gap to the next block.

| | From the clock | From the tip's slot |
| --- | --- | --- |
| New machinery | A tick per slot, since `B_imm` moves with no block | None. `commit` stays in `on_block` |
| `commit` reads the wall clock | Yes, for the first time | No. Only step 6 of Block Header Validation does, as today |
| Forged clock step of +18 h, alone (simulated) | `B_imm` goes from 18 h old to about 8.5 h old at once, about 1,019 occupied slots deep | No move until the chain gains a block in the shifted range: still 18 h old, about 2,160 occupied slots deep |
| The same step plus one block in the last 30,540 slots of the shifted range (simulated) | As above | The same outcome: about 8.5 h old, about 1,018 occupied slots deep |
| Node keeps running and receives nothing for `K` slots (simulated) | `B_imm` climbs to 1,019 occupied slots below its stale tip, which limits how far it can still heal | No move until the next block, about 2,160 occupied slots below the tip. That block moves `B_imm` to the floor, as the clock rule does |
| Lag behind the clock rule (simulated, delivery aside) | None | About 29 slots on average, about 44 while a third withholds |
| The bounds of [What the finality window holds](#what-the-finality-window-holds) | Hold as computed | Hold on an honest clock: step 6 gives tip slot ≤ clock, so this rule fixes a subset of what the clock rule fixes |
| Bootstrap test | Reads the clock, so nodes can differ at the boundary | Reads the later of the two tips: a function of the two chains alone |

**Residual risk: clock faults.** Neither rule makes a shifted clock safe, and the study has no analysis of clock faults. A time service that applies any forward step at once lets one forged reply move a node's clock.

- The floor bounds the damage under both rules: `B_imm` stays about 1,019 occupied slots deep, about 860 blocks on the specification's Blend. That is below the 1,510 blocks the study's depth bound proves against a third at 10 s, at the count of its code, so a shifted node loses that guarantee.
- Under the tip rule the attacker needs a forged reply plus one block in the shifted range. That block may be the node's own: a staking node on a shifted clock proposes at the shifted slot. With 1 % of stake its first win takes 49 minutes on average, and that win reaches the floor. An attacker with 1 % of stake has about 10 wins in the part of the range that reaches the floor.
- This revision adds no clock rule. The [Clocks](../cryptarchia-v1-protocol.md#clocks) annex already assumes in-sync clocks.

## The switch to Online

A node under the Bootstrap rule keeps `B_imm` frozen, and the forks it rejected stay in its block tree. The Online rule has no depth bound to refuse them. So the node runs `commit` on `c_loc` before it processes any further block. Without this step, the first block processed after the switch that does not extend `c_loc`, which an attacker can send, makes a longer rejected fork win by length, and `B_imm` then passes the divergence block. A model of the rules shows this: a fork sparse in the density window but longer overall loses under Bootstrap, and wins at the next such block when `commit` is left out.

### Alternative: hold `B_imm` until the node has been online for `K`

This revision has no hold. `B_imm` stays frozen under Bootstrap, moves at the switch, and moves at once after a restart within `T_offline`.

- **At the switch, a hold is unsafe or pointless.** Without `commit`, nothing is pruned, and a rejected fork wins by length for the whole hold. `B_imm` then lands on it when the hold ends. With `commit`, `B_imm` has already moved, so the hold no longer delays the step it was meant to delay.
- **After a restart, a hold is safe and costs 18 hours per restart.** A node that restarts more often than every 18 hours never finalizes. A network-wide upgrade stalls `B_imm` on every node for 18 hours, and everything that waits for finality on those nodes waits with it.

### The restart path

After a restart within `T_offline`, the fork runs over `K` slots and the node's chain stopped up to 20 minutes earlier. The margin `K/T_offline` is 54, as it is today. In a private race at 10 s, the head start makes 18 hours behave like 16.8 at 0.298 and 16.5 at a third. This is an estimate from a private race, not the study's bound.

- With a nonce that resists grinding, this path covers a third at 10 s, where the wait is 10.2 hours, and after a deflated inference, where it is 12.5.
- It does not cover 15 s of delay, where the wait is 17.5 hours, above 16.5. So on this path 18 hours keeps the deflated case and not the case of the `K` row at `T_M`.
- With today's nonce, the share on this path falls from 0.298 to about 0.295, from the study's bound at that wait.

**Open question.** Deferring `commit` to the end of Initial Block Download would close the head start for a node with an honest IBD peer, a peer configured for Initial Block Download, with no stall. It would not cover a node with no IBD peers, and a malicious IBD peer could prolong IBD. Today's rule has the same exposure, so this RFC leaves it out.

### What a restart loads

A start decides the rule from what the node stored. Today's text lets a restart reach the Online rule on a chain that the Bootstrap rule has not finished with, in two ways.

- **A node that stopped under the Bootstrap rule.** Today's cases read `B_imm`, the operator's flag and the time offline. None reads the rule the node used when it stopped. A node that is started with the flag, and restarted without it within `T_offline` of its last use of the Online rule, starts with the Online rule. It has run no Prolonged Bootstrap Period, no last round and no `commit`, while Initial Block Download may have moved its chain by days. Such a node now restarts with the Bootstrap rule.
- **A node that cannot tell how long it was offline.** Today the Bootstrap rule is selected only if it is certain that the node was offline for longer than `T_offline`. A lost record of that time therefore selects the Online rule after any outage. Now the Online rule needs the certainty.

The first case reads the rule the node stored. So the node stores `c_loc`, `B_imm` and the rule it uses together: after it sets the rule at startup, after each block it processes, and after it switches to the Online rule. A restart loads the three as last stored. Stored apart, a restart can find the Online rule with the `B_imm` from before the switch, or a tip that does not descend from `B_imm`. Stored only after a block, the Online rule would still be the stored one after a start with the flag. The node software already keeps the three in one record, and restarts with the recorded rule within the grace period.

**Alternative: run `commit` at every start with the Online rule.** It repairs a `B_imm` that was stored before the `commit` of the switch. It runs on the tip as stored, so it does not help a node whose stored tip is older than its stored rule. With the three stored together it never moves `B_imm`.

**What is left.** The rule does not cover the block tree. A node that stored a block, and not the three values after it, restarts on the earlier tip. Under the Bootstrap rule it compares the stored block when the next block arrives. If none arrives before the switch, `commit` runs on the earlier tip.

### The last round

After Initial Block Download a node receives new blocks only from its connected peers. An adversary that fills those can withhold the honest chain even when the IBD peers are honest, and a fork the Bootstrap rule rejected then wins after the switch ([Comparing forks](#comparing-forks)). So the node fetches the tip of every IBD peer and of every other connected peer once more before the switch.

- **Each tip comes from the peer that returned it.** Initial Block Download asks a tip's blocks from up to 16 connected and 16 discovered peers and uses the first usable answer, which spares the IBD peers. In this round that would defeat the purpose. The adversary that fills the connections answers first, one invalid block ends the download, and the node switches without the honest chain. v1 of this RFC had this flaw.
- **Each peer is handled on its own, in parallel.** A peer that holds back its tip, returns a tip on a long fork, or streams slowly then delays only its own download.
- **The steps repeat for each peer, as the rounds of Initial Block Download do.** The node asks the peer's tip, downloads up to it, waits `T_round` and asks again, until the tip it gets is in its block tree. So one failed tip request or one broken download does not cost the node the honest chain. The node also gets the blocks the peer added while it was downloading. As in Initial Block Download, the handling of an IBD peer does not end while each tip it returns is new to the node and each pass brings a block that counts. A node whose clock lags behind the newest block is such a case.
- **Requests name blocks the peer is likely to hold.** A peer starts its stream at the latest block it shares with the blocks a request names: the local tip, `B_imm` and the last block downloaded. One private block on the node's tip makes that tip unknown to an honest peer, whose stream then starts at `B_imm`, which the Bootstrap rule never moves. So the round's requests also name the latest blocks of `c_loc` that lie at least `T_offline`, `s_gen` and `K` behind its tip. An adversary whose fork has been the node's chain for more than `K` slots made all three. So the requests also name a block the node recorded when its Prolonged Bootstrap Period started: the block that lay `K` behind its tip then. If the node was on the honest chain at that time, every honest peer holds that block, and a stream starts there at the latest. When the round starts, that is 42 hours of blocks, `K` and `T_boot`. That also keeps the load on the IBD peers small.
- **A peer that has delivered a block is asked to go on from it.** A download that follows an earlier one names the last valid block the peer delivered, beside the recorded block and in place of the three blocks behind the tip. A peer that still holds that block goes on from it. Without it, a download that is started again brings blocks the peer has delivered before, which make no progress below, and an honest IBD peer is given up while it sends them. The recorded block stays for a peer that no longer holds the block it delivered. With the three blocks as well, the list would pass the limit of 5 on `additional_blocks` once `download_blocks` adds its own latest block.
- **The round waits at most `T_offline` for a peer that is not an IBD peer.** Without a limit, one such peer that streams slowly, or that returns a tip on a long valid fork, holds the node on the Bootstrap rule, where it must not propose.
- **An IBD peer is given up only when it stops delivering.** Its handling ends when `T_offline` passes without a block that counts. A block counts if it is valid and this peer has not delivered it earlier in the round, even when the node holds it. So a stream that starts below what the node holds counts as progress. A peer that sends the same blocks again, or a new invalid block on every request, makes none. With one limit for every peer, a node that is far behind would switch, and make its chain immutable, while a peer its operator chose is still delivering another. The cost is that an IBD peer holds the node on the Bootstrap rule for as long as it delivers, in each `T_offline`, one valid block it has not delivered before. It needs no fork for that, because blocks the node holds count. Today an IBD peer holds Initial Block Download with less: a tip that cannot be downloaded.
- **What is left.** A node whose every peer is the adversary's stays exposed, and this is accepted. So does a node whose honest peers return no tip within `T_offline`. A restart during the Prolonged Bootstrap Period records the block again. With IBD peers, Initial Block Download runs first. A node with no IBD peers records from the chain it holds at the restart, which an adversary may have made.

In the reference code of the rules, one IBD peer that returns the honest tip and serves its blocks closes the case, whatever the other peers return: an invalid block, a tip on a long fork, or nothing. A peer that is not an IBD peer closes it if it serves the blocks within `T_offline`. The reference code has a case in which a fork has been the local chain for more than `K` slots: the download from an honest peer fits the limit when the requests name the recorded block, and starts at `B_imm` and does not fit without it. The round asks for no tip of a given age, and does not terminate the node when no peer answers. So a network in which every node bootstraps at once, as at genesis, still switches.

**Alternative: one limit for every peer.** The round would end `T_offline` after it started at the latest, whatever its peers do. A node still downloading the honest chain from an IBD peer at that time would switch without the rest. This RFC waits for the IBD peer.

### `T_boot` has no relation to `K`

`T_boot` stays at 24 hours. That it exceeds 18 hours is incidental. With an honest peer, the density test does not read `T_boot`. Under an eclipse, the node sees the honest chain only if `T_boot` outlasts the eclipse. So `T_boot` buys time to find an honest peer.

## Comparing forks

**On every block.** The Bootstrap rule now runs on every block. `on_block` used to skip it when a block extends `c_loc`, so a chain chosen by length while a fork is young could keep `c_loc` past `K` with no density comparison, and `commit` then fixes it at the switch. Two nodes with the same blocks could end on different chains by delivery order alone. Trees with no strict winner can still split, as the order of comparison below states. A later block of the other fork re-runs the comparison, so the node must also stop receiving that fork. A block that extends `c_loc` can also move the node to a shorter fork, when it makes that fork old enough for the density test and the fork is denser in the window. The Online rule keeps the skip.

**Forks below `B_imm`.** Both rules check descent from `B_imm` explicitly, because step 8 of Block Header Validation allows incomplete pruning. Without the check, a node that restarts under the Bootstrap rule can select a denser fork below `B_imm`, and `commit` then has no path from `B_imm` to `c_loc`.

**Where the two rules differ.** The Online and Bootstrap rules compare a fork differently in one case: its divergence block `D` is at least `K` slots before the later tip, but `B_imm` has not passed it. That happens for three reasons:

- `D`'s child is younger than `K`, for about one block interval.
- The floor holds `B_imm` back on a sparse chain.
- The local tip lags the later tip, as after a restart, or while the rest of the chain has not arrived.

Online then compares by length and Bootstrap by density, so a fork the Bootstrap rule rejected can survive the switch. If it is longer it wins, `B_imm` passes `D` at that block, and the honest chain is pruned. In the model, at mean rates, a third's fork of 1,020 blocks, `φ + 1`, that reaches the node before the rest of the honest chain does this with a lag of 12.5 hours with no delivery delay, and about 10 on the specification's Blend.

The lag needs every peer that relays to the node to withhold the honest chain until the switch, which is the eclipse of [What the floor leaves open](#what-the-floor-leaves-open). With the honest chain up to the switch, the local tip is recent, and a fork must outgrow the honest chain over `K` slots to win. [The last round](#the-last-round) brings the honest chain up to the switch when one peer returns the honest tip and serves it.

Two other changes were run in the model and rejected. Pruning the fork at the switch does not hold, because `D` lies above `B_imm` and the fork can be delivered again. Using the Bootstrap test under the Online rule as well does close the case, but a fork that is denser in the window and then dies holds the node for good: with 3,333 live blocks the node stayed on the dead fork, and `B_imm` never passed `D`.

**The order of comparison.** The Bootstrap test compares two chains at a time, and it is not transitive. With three forks, the result can depend on the order in which a node visits them. At the switch, `commit` then fixes whichever chain the order produced, so two nodes with the same blocks that visit them in different orders can hold conflicting `B_imm`. A model shows this with three forks, one of them denser in the window than the longest chain, which the Genesis assumption excludes. In random trees at a small scale (`K` = 40, `s_gen` = 10, and `k` = 6 for the depth test), 953 of 3,497 cases depend on the order when the forks are visited as listed, against 781 with the depth test. These counts show that the class exists today, not a rate on a real chain. Between two chains, at the same scale, the test gave no disagreement beyond exact ties in 236,941 pairs, where the depth test gave 6,848. The rule therefore visits the forks in increasing order of block ID, and none of the 3,497 cases then depends on how they are listed. Its result is a function of the block tree and the local tip, and the order in which an implementation stores its tips cannot change it. An adversary that grinds block IDs can choose where its fork falls in that order, but every node with the same tree and local tip then picks the same chain.

The Online rule visits the forks in the same order. There the order decides only between forks of equal length that are both longer than the local chain, which can stand in the block tree at the first block after the switch.

**Open question.** Two nodes that hold the same blocks on different local tips can still differ. And while three forks compare in a cycle, a node's own tip can change from one block to the next.

## What else reads `K`

- **The epoch.** Every epoch value stays as it is: phases of 194,400, 194,400 and 259,200 slots, an epoch of 648,000 and a `PERIOD` of 388,800. Changing `K` now changes the epoch.
- **The epoch's waits.** A value is final when its phase ends only if `φ` occupied slots follow it by then, where it needed 2,160 blocks. At mean rates, the 54-hour phase that waits for the stake snapshot needs 15.5 % of the inferred stake to produce blocks, against 33.0 %. The 72-hour phase that waits for the nonce and the inferred stake needs 11.6 %, against 24.7 %. What a node does when a value is not final at the end of its phase is specified under neither rule.
- **The density window.** `s_gen` stays at `⌊k/4f⌋`, 4.5 hours, against the 4.8 to 4.9 hours a third needs at `1e-9`. The chance of winning the window does not change. What a win buys does: a fork that wins the window is fixed at the switch after 1,020 blocks, where it needed 2,161.
- **Two windows within `K`.** `s_gen` comes from Theorem 2 of Ouroboros Genesis. Its proof reads two windows of `s_gen` slots after the divergence block: one for the growth of the honest chain, and one for an honest block that follows it. Both must lie within the age of the fork when densities are compared. Under the depth rule that follows from `k` blocks. Here the comparison starts at `K` slots, so the bound becomes `2·s_gen ≤ K`, 9 hours against 18.
- **The uncle window.** It is 360 slots against 64,800. A candidate's parent is above the proposer's `B_imm` exactly, not with high probability, because a `B_imm` that has moved lies at least `K` behind the slot being built. No candidate was pruned in a model of 9,000 random trees.
- **Blocks above `B_imm`.** Their number is no longer bounded by `k`, which changes how a node sizes the ledger states it keeps. On the specification's Blend, `K` slots hold about 1,825 blocks.
- **The last round.** Its requests name the block that lies `K` behind the local tip, and the block that lay `K` behind it when the Prolonged Bootstrap Period started.

## Compatibility

This is a consensus change. Nodes on the old rule and on this one can fix different blocks in a deep reorganization, so a network runs one rule or the other. No header, wire format or epoch value changes. Bedrock has no deployed network, so the change needs no migration.

Two properties of the depth rule do not carry over. `B_imm` is no longer the `k`-th block below the tip of `c_loc`: it depends on the order in which blocks arrived, so two nodes on the same chain can hold different `B_imm`, though never conflicting ones. And it no longer moves one block per block: after a silence longer than `K`, the next block moves it to the floor at once.

## Reproducing the figures

The figures come from the finality study, `tools/simulators/finality` of the research repository. Its notes carry each result with its check: `SLOTS.md` phase K, `SETTLEMENT.md` B6 and B7, `DESIGNS.md` H.2, `FURTHER.md` G7, `RATE.md` and `SIGNERS.md` M.7. `make k7`, `k2`, `k3`, `k5`, `k9`, `k8` and `m7` give the waits, the shares, the splits and eclipses, the targets within reach of grinding, the floor, the cap and the limit on joining stake. The study reads `B_imm` against the clock. Its figures carry over as [Counting from the tip's slot](#counting-from-the-tips-slot) states.

Beyond the study's notes, the figures come from four sources:

- The study's bound, run for this RFC: the waits with a nonce that resists grinding, the deflated waits from 11 s to 15 s, the waits with honest stake offline, the waits and the share at 15 s of [The epoch nonce](#the-epoch-nonce), the limit of 2.628 on joining stake, which the study prints as 2.627, and the share of 0.295 on the restart path.
- A model that runs the rules as the specifications print them: the counts of [Comparing forks](#comparing-forks), the two changes rejected there, and the uncle-window check of [What else reads `K`](#what-else-reads-k). The `φ` code is run as printed too.
- Reference code of the rules with its tests: the switch, the last round, the order of visits, and the first and last slot of the floor's count. It has 49 tests, and each of 33 deliberately broken versions fails at least one of them. In it a peer starts its stream at the highest block it shares with the blocks a request names, a step delivers one block, and `T_offline` is a number of steps.
- Small models at mean rates: the rows marked simulated, the eclipse and lag figures of [What the floor leaves open](#what-the-floor-leaves-open) and [Comparing forks](#comparing-forks), the private race of [The restart path](#the-restart-path), the days a side needs, the split in halves, the participation the epoch's waits need, and the blocks above `B_imm`.

> **TODO (author):** the study is not on GitHub yet, so none of this can be reproduced by a reviewer. Publish its branch with the models, the reference code and the runs listed here, link that commit in the first sentence, and remove this note.

# Details

Snippets leave out the specifications' comments and markup, and a `...` line stands for unchanged logic.

## 1. The latest immutable block is counted in slots

In [Constants](../cryptarchia-v1-protocol.md#constants), `k` stops being a depth, and `K` and `φ` are added. The Notation row of `s` is deleted.

```diff
-| k | security parameter | Block depth finality. Blocks deeper than k on any given chain are considered immutable. | 2160 blocks |
+| k | security parameter | A number of blocks from which other constants are derived, each at its definition. | 2160 blocks |
+| K | finality window | The number of slots a block must lie behind the tip of the local chain before Commit can make it immutable. ... | ⌊k/f⌋ = 64,800 slots (18 hours) |
+| φ | finality floor | The number of occupied slots that must follow a block before Commit can make it immutable, derived in Finality Floor. ... | 1,019 occupied slots |
```

The `K` row also states:

- the three periods of [§5](#5-three-periods-stay-within-the-finality-window), each with a link to its definition;
- what `K` must hold: the chance that a share `α_max` of the stake displaces an immutable block stays at most `ε` per block, with every honest block up to `T_M` late, or up to `Δ` late while a tenth of the honest stake is offline;
- that `α_max`, `Δ` and `ε` are the targets of Finality Floor;
- that both cases take the epoch nonce as unbiased, and that a nonce an adversary can bias lowers the share `K` holds;
- that a change of `k`, `f`, the slot length, `T_M`, the epoch nonce or one of those targets requires both cases to be checked again and `φ` to be derived again.

`commit` moves `B_imm` along `c_loc` instead of reading the block at a depth. It runs in `on_block` under the Online rule, and at the switch.

```python
def commit(T, c_loc, B_imm):                    # was: commit(T, c_loc, depth)
    assert fork_choice_rule == ONLINE
    B = B_imm
    while B != c_loc:
        C = child_on_chain(B, c_loc)
        if sl(C) + K > sl(c_loc) or density_over_slots(c_loc, sl(C) + 1, sl(c_loc) - sl(C)) < phi:
            break
        B = C
    return prune_forks(T, B), B
```

[Finality Floor](../cryptarchia-v1-protocol.md#finality-floor) derives `φ` from `K`, `f` and the targets `α_max = 1/3`, `Δ = 10` and `ε = 10⁻⁹`.

An uncle's slot now also counts for the floor, in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references).

## 2. The fork choice rules read the age of a fork in slots

Both rules also visit the forks in increasing order of block ID, the lexicographic order of its bytes.

```diff
-def bootstrap_fork_choice(c_local, forks, k, s_gen):
+def bootstrap_fork_choice(c_local, forks, K, s_gen, B_imm):
     c_max = c_local
-    for c_fork in forks:
+    for c_fork in sorted(forks, key=block_id):
-        depth_max, depth_fork = common_prefix_depth(c_max, c_fork):
-        if depth_max <= k:
+        if not is_ancestor(B_imm, c_fork):
+            continue
+        depth_max, depth_fork = common_prefix_depth(c_max, c_fork)
+        sl_div = grandparent(c_max, depth_max).slot
+        sl_top = max(c_max.slot, c_fork.slot)
+        if sl_div + K > sl_top:
             ...  # longest chain
         else:
             ...  # density over s_gen
+    return c_max
```

```diff
-def online_fork_choice(c_local, forks, k):
+def online_fork_choice(c_local, forks, B_imm):
     c_max = c_local
-    for c_fork in forks:
+    for c_fork in sorted(forks, key=block_id):
-        depth_max, depth_fork = common_prefix_depth(c_max, c_fork):
-        if depth_max <= k:
-            if depth_max < depth_fork
-                c_max = c_fork
-        else:
-            continue
+        if not is_ancestor(B_imm, c_fork):
+            continue
+        depth_max, depth_fork = common_prefix_depth(c_max, c_fork)
+        if depth_max < depth_fork:
+            c_max = c_fork
+    return c_max
```

[Chain Maintenance](../cryptarchia-v1-protocol.md#chain-maintenance) calls each rule with its own arguments, and runs the Bootstrap rule on every block:

```diff
-c_loc' = B if parent(B) == c_loc else fork_choice(c_loc, F_T', k, s)
+c = B if parent(B) == c_loc else c_loc
+if fork_choice_rule == BOOTSTRAP:
+    c_loc' = bootstrap_fork_choice(c, F_T', K, s_gen, B_imm)
+elif parent(B) == c_loc:
+    c_loc' = c
+else:
+    c_loc' = online_fork_choice(c_loc, F_T', B_imm)
```

## 3. The switch to Online runs a last round and `commit`

[Switching to the Online Rule](../cryptarchia-v1-bootstr-sync.md#switching-to-the-online-rule) is a new section. When the timer of the Prolonged Bootstrap Period completes, the node runs a last round under the Bootstrap rule, and keeps listening for new blocks during it:

```python
def last_round(ibd_peers, local_tree, recorded):
    def catch_up(peer):
        while True:
            tip = get_tip(peer)
            if tip is not None:
                if local_tree.has(tip):
                    return
                last = last_delivered(peer)
                known = [recorded] + ([last] if last is not None else
                                      local_tree.blocks_behind_tip([T_offline, s_gen, K]))
                download_blocks(local_tree, target_block=tip, peers=[peer], known=known)
            sleep(T_round)

    parallel(catch_up(peer) for peer in set(ibd_peers) | connected_peers())
```

- For each peer the node asks the tip, downloads up to it from that peer, and waits `T_round`, until the tip it gets is in the local block tree. A tip request that fails is followed by the same wait, and the node is not terminated if no tip arrives.
- When the Prolonged Bootstrap Period starts, the node records the latest block of `c_loc` whose slot lies at least `K` behind the slot of its tip, or `B_imm` if there is none. Each request names that block in `KnownBlocks.additional_blocks`.
- The requests of a download also name the last valid block that the peer delivered in an earlier download of the round. If it has delivered none, they name the latest blocks of `c_loc` whose slots lie at least `T_offline`, `s_gen` and `K` behind the slot of its tip, where each exists.
- In [Downloading Blocks](../cryptarchia-v1-bootstr-sync.md#downloading-blocks), a responder ignores a known block that it does not hold. The round relies on this.
- The handling of an IBD peer ends when `T_offline` has passed since the round started, or since the peer last delivered a block that counts, whichever is later. A block counts if it is valid and no download from the peer delivered it earlier in the round. The handling of any other peer ends `T_offline` after the round started. What is running then is cancelled, and the blocks it delivered stay.
- `download_blocks` gains the arguments `peers` and `known`. Without them it behaves as before.
- The rows of `T_offline` and `T_round` state these second uses.

The node then switches to the Online rule and runs `commit` on `c_loc` before it processes any further block.

The sentence that the node does not wait `s_gen` slots after Initial Block Download is removed.

[Setting the Fork Choice Rule](../cryptarchia-v1-bootstr-sync.md#setting-the-fork-choice-rule) changes in three places ([What a restart loads](#what-a-restart-loads)):

- A new case selects the Bootstrap rule: the node is restarting after it stopped under the Bootstrap rule.
- The offline case also covers a node that cannot tell how long it was offline. It selects the Bootstrap rule unless it is certain that the node has been offline for at most `T_offline` since it last used the Online rule. It selected that rule only if it was certain that the node had been offline for longer.
- The node stores `c_loc`, `B_imm` and the fork choice rule it uses together: after it sets the rule at startup, after each block it processes, and after it switches to the Online rule. A restart loads the three as last stored.

## 4. The finality window sets the epoch schedule

Phases of `3K`, `3K` and `4K` slots, an epoch of `10K`, and a `PERIOD` of `6K` replace `s` and `⌊k/f⌋`. Each phase that waits for a value to finalize must last at least `K` slots, or `commit` cannot make the value final within the phase.

## 5. Three periods stay within the finality window

- `W·f⁻¹ < K` replaces `W ≤ ⌊0.6k⌋`. It sits in the `W` row, with what breaks if it fails, and the note in [Uncle Selection](../cryptarchia-v1-protocol.md#uncle-selection) says why it suffices.
- `2·s_gen ≤ K`, in [Definitions](../fork-choice.md#definitions) of the Fork Choice Rule.
- `T_offline < K`, in [Constants](../cryptarchia-v1-bootstr-sync.md#constants) of Bootstrapping & Synchronization.

## 6. The count of occupied slots takes a chain

`density_over_slots` read "the honest chain". `commit` reads it over `c_loc`, so it gains an argument:

```diff
-density_over_slots(s, p)
+density_over_slots(c, s, p)
```

The range stays `[s, s + p)`. `commit` passes `s = sl_C + 1` and `p = sl_tip − sl_C`, so `C` itself does not count and the tip does. The inference's function takes the tip of the chain the estimate is derived on as its first argument, `total_stake_inference(tip, total_stake_estimate, epoch_slot)`, and passes it on.

## 7. Fork pruning removes every fork

`prune_forks` restarted from `T` on every iteration, so one call removed only one fork. Step 8 of Block Header Validation leans on this step, so it now accumulates. `commit` also passed it a third argument it does not take.

```diff
-T' := prune_blocks(B_tip, B_div, T)
+T' := prune_blocks(B_tip, B_div, T')
```

## Chores

- Removed `s`, the name "slot security parameter", `block_at_depth`, "slot finality period" and the second name for `k`, "safety parameter".
- Fixed `s` where `s_gen` was meant in `density`, made both fork choice functions valid Python, defined `grandparent`, and corrected their tie-break comments.
- In the [Cryptarchia Fork Choice Rule](../fork-choice.md), named both headings of the long range attack after the rules, Bootstrap and Online, reworded its Introduction, its Overview and the Online section around `B_imm`, and defined the divergence block.
- In the [Cryptarchia Protocol](../cryptarchia-v1-protocol.md), named `commit` as what moves `B_imm`, wrote "divergence block" throughout [Uncle References](../cryptarchia-v1-protocol.md#uncle-references), dropped "a proposer has no incentive to deviate from it" from [Uncle Selection](../cryptarchia-v1-protocol.md#uncle-selection), and corrected step 8 of Block Header Validation to name step 7. Its Introduction said that longest-chain protocols tolerate half of the participants, and called that a large threshold. It now says that this holds when blocks are delivered at once, and points to the share the document sizes immutability against.
- In [Setting the Fork Choice Rule](../cryptarchia-v1-bootstr-sync.md#setting-the-fork-choice-rule) and [Offline Grace Period](../cryptarchia-v1-bootstr-sync.md#offline-grace-period), reworded the lines that read `k`, restated the example's attack in slots, and replaced two images with one diagram. In [Downloading Blocks](../cryptarchia-v1-bootstr-sync.md#downloading-blocks), named the floor of `commit` among the readers of the uncle headers.
- In [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md), named `commit` among the readers of the uncle headers.
- In [\[Overview\] Bedrock Architecture](../bedrock-architecture-overview.md) and the [Bedrock Genesis Block](../bedrock-genesis-block.md), reworded the lines that read finality as a depth. In [\[Analysis\] Total Stake Inference](../analysis-total-stake-inference.md), stated the effect of participation on finality through the floor.
- In the [Logos Oracle Network (LON) Oracle Zone](../../../anoncomms/raw/logos-oracle-zone.md), stated the finality of the Logos Blockchain as the finality window `K`, with a link to `commit`, in its parameter list, its two parameter rows and its paragraph on the cooldown.
- In the [Blend Protocol](../blend-protocol.md), added a pointer from `T_M` to `K` and `φ`.

# Implementation

- [ ] Replace the update of `B_imm` with the `commit` loop, reading `K` and `φ`, with no slot tick. The loop's test is monotone along the chain, so one walk down from the tip with a running count finds the new `B_imm`
- [ ] Compute the floor with `density_over_slots` over the local chain, uncles included
- [ ] Remove the depth bound from the Online fork choice, and check descent from `B_imm` in both rules. With complete pruning the check can be skipped, which spares a walk per tip on every Bootstrap block
- [ ] Replace the depth test of the Bootstrap fork choice with the test on the divergence block's slot, and run it on every block, including one that extends the local chain
- [ ] Visit the tips in increasing order of block ID in both fork choice rules
- [ ] Before the switch to Online, run the last round: for every IBD peer and every other connected peer in parallel, ask its tip, download the blocks up to it from that peer, wait `T_round` and repeat until the tip is in the local block tree, without terminating if no peer answers
- [ ] Record, when the Prolonged Bootstrap Period starts, the block `K` behind the local tip, and name it in every request of the last round. Name with it the last valid block the peer delivered in an earlier download, or the three blocks behind the local tip if it delivered none
- [ ] As a responder, ignore a known block that is not held
- [ ] In the last round, end the handling of an IBD peer when `T_offline` passes without a valid block it has not delivered before, and the handling of any other peer `T_offline` after the round started
- [ ] At the switch, run `commit` before any further block
- [ ] Store the tip, `B_imm` and the fork choice rule as one record: after the rule is set at startup, after each block, and after the switch. Restart with the Bootstrap rule when the record holds it
- [ ] Restart with the Bootstrap rule when the time offline cannot be read, or when no record of it exists
- [ ] Prune all forks below `B_imm` in one call, at every move of `B_imm` and at the switch to Online
- [ ] Expire the wallet's leader-claim reservations after `K` slots instead of `k` immutable blocks
- [ ] Size the kept ledger states for blocks above `B_imm`, which `k` no longer bounds
- [ ] Update the fork monitor of the test framework
- [ ] Review the forward step of the time service against [the clock faults](#counting-from-the-tips-slot)
- [ ] Prove the rule in the formal model, floor included: the current theorems read a depth of `k`, or a confirmation rule beside it
- [ ] Add tests: a fork rejected by the Bootstrap rule against the switch, a restart within `T_offline` after a stop under the Bootstrap rule, a restart with no record of the time offline, a last round in which the other peers return an invalid block, a tip on a long fork, or nothing, a last round that reaches its limit with a download running from an IBD peer and from another peer, an IBD peer that sends only blocks it sent before, an IBD peer that sends a new invalid block on every request, an IBD peer whose stream starts below what the node holds, a tip request that fails once, a tip that moves during the download, a download that breaks once while the local chain is a fork, a peer that no longer holds the block it delivered, a fork that has been the local chain for more than `K` slots, one private block on the local tip, the limit of 5 on `additional_blocks`, pruning of several forks at once, the floor's first and last slot, the Bootstrap test from either branch, in any delivery order, and for tips listed in any order, and two equally long forks under the Online rule listed in either order
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.3.0 |
| [Cryptarchia Fork Choice Rule](../fork-choice.md) | Modified | 1.2.0 |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-v1-bootstr-sync.md) | Modified | 1.1.0 |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.2.0 |
| [Block Construction, Validation and Execution](../bedrock-v1.1-block-construction.md) | Modified | 1.3.1, wording only |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.8.2, pointer only |
| [\[Overview\] Bedrock Architecture](../bedrock-architecture-overview.md) | Modified | 1.1.1, wording only |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | 1.2.2, wording only |
| [\[Analysis\] Total Stake Inference](../analysis-total-stake-inference.md) | Modified | 1.0.1, wording only |
| [Logos Oracle Network (LON) Oracle Zone](../../../anoncomms/raw/logos-oracle-zone.md) | Modified | wording only |
