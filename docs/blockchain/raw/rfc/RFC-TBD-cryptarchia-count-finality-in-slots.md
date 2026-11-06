# [RFC] Cryptarchia: Count finality in slots

**Motivation and proposal:** [PR #TBD](https://github.com/logos-co/logos-lips/pull/TBD)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Cryptarchia Protocol](#affected-specifications): [the rule](#1-the-latest-immutable-block-is-counted-in-slots) | the `commit` loop, its first slot and its last slot; `K` and `φ` ([What the finality window holds](#what-the-finality-window-holds), [The finality floor](#the-finality-floor)) |
| 2 | Critical | [Fork Choice Rule](#affected-specifications), [Cryptarchia Protocol](#affected-specifications): [both rules](#2-the-fork-choice-rules-read-the-age-of-a-fork-in-slots) | the Bootstrap test reads only the two chains and runs on every block; both rules ignore a fork below `B_imm`; the Online rule has no depth bound ([Comparing forks](#comparing-forks)) |
| 3 | Critical | **Start here** — [Bootstrapping & Synchronization](#affected-specifications): [the switch](#3-the-switch-to-online-runs-commit) | a fork whose divergence block `commit` passes must not win after the switch ([The switch to Online](#the-switch-to-online)) |
| 4 | High | [Cryptarchia Protocol](#affected-specifications): [the epoch schedule](#4-the-finality-window-sets-the-epoch-schedule) | every epoch value stays as it is |
| 5 | Medium | [Cryptarchia Protocol, Bootstrapping & Synchronization](#affected-specifications): [two periods](#5-two-periods-stay-below-the-finality-window) | the bound on the uncle window |
| 6 | Medium | [Total Stake Inference](#affected-specifications): [the count](#6-the-count-of-occupied-slots-takes-a-chain) | the inference's own count does not change |
| 7 | Medium | [Cryptarchia Protocol](#affected-specifications): [fork pruning](#7-fork-pruning-removes-every-fork) | one call removes every fork |
| 8 | Low | [Chores](#chores) | skim |

# Discussion

## What the finality window holds

`K` is 64,800 slots, 18 hours. This section gives the share of stake it holds at `ε = 1e-9`, the chance allowed per block that a block made immutable is displaced.

The figures come from two delay models.

- **Worst case.** An adversary delivers every honest block as late as a bound `Δ` allows, taken at `Δ = 10` s, about the 99th percentile of delivery on the specification's Blend. The study reads the model of Gaži, Ren and Russell ("Practical Settlement Bounds for Longest-Chain Consensus", ePrint 2022/1571) for a wait on the 1 s slot lottery. `K` binds every node, so it must hold under this model.
- **Random delay.** Blocks take Blend's mixing delays, measured in a simulation of 1,000 nodes. Only the private attack is played, with honest relays.

The wait that holds `ε`, in hours:

| Case | 30 % | a third |
| --- | --- | --- |
| Worst case at 10 s, a nonce that cannot be ground | 5.9 | 10.1 |
| Worst case at 10 s, today's nonce, one ground nonce | 13.6–14.1 | 25.9–26.7 |
| Worst case at 10 s, today's nonce, two ground nonces | 16.1–18.7 | 38.3–42.0 |
| Worst case at 10 s, a nonce that resists grinding, after a deflated inference | 6.4 | 12.5 |
| Worst case at 15 s, a nonce that cannot be ground | 9.4 | 17.4 |
| Worst case at 15 s, a nonce that cannot be ground, after a deflated inference | 14.2 | 35.6 |
| Worst case at 20 s, a nonce that cannot be ground | 16.1 | 33.5 |
| Random delay, a nonce that cannot be ground | 3.1 | 5.1 |

- The ranges span two bounds on the grinding factor. Neither end is an attack.
- A deflated inference is what an adversary gets by withholding every block for one observation period, 4.5 days. The inferred stake falls by its share, and every lottery threshold rises by `1/(1 − α)` for the next epoch. With the honest stake alone filling slots at `f`, the fixed delay weighs more.
- The 12.5 hours takes the nonce's factor at the old rates, where its bound is derived.
- After 18 hours against a third at 10 s, the chance of displacement is `1.2·10^-16` without grinding and `8.4·10^-14` after a deflated inference.
- The delay leaves little margin after a deflation. Against a third, 18 hours holds up to 15 s without a deflation. After one it holds up to 11 s, where the wait is 14.9 hours, and not at 12 s, where it is 18.2. The study prints deflated waits only at 1, 10 and 20 s, so the figures from 11 s to 15 s come from running its bound for this RFC.
- The bound is the chain of Gaži, Ren and Russell frozen at the phase in which the wait passes, with each phase's span charged at its longest. The paper's attack, played against a wait on the slot lottery at 1 s and 10 s and at waits up to 2 hours, succeeds 0.26 to 0.82 times as often as the bound allows against a third.
- Delivery later than `Δ` lies outside the bound. Under honest mixing on the specification's Blend, that is one block in a hundred.

### The epoch nonce

This RFC does not change the epoch nonce. A nonce that resists grinding is required before genesis, in its own RFC, and the two land separately. Until it lands, a third of the stake is not held.

The largest share each rule holds, with two ground nonces at the upper end of the factor:

| Delay model | `k` = 2,160 blocks, today's nonce | `K` = 18 h, today's nonce | `K` = 18 h, a nonce that resists grinding |
| --- | --- | --- | --- |
| Worst case at 10 s | 0.288 | 0.298 | at least a third |
| Random delay on the specification's Blend | 0.358 | 0.322 | at least a third |

- Under random delay the rule alone loses, because 2,160 blocks take 30 to 33 hours while 30 % to a third withholds, and `K` stays at 18.
- Under the worst case the two figures come from different bounds: 0.288 from a depth bound and 0.298 from the wait bound. So 0.298 against 0.288 does not show a gain.
- Two ground nonces reach only targets past the cut-off and within `K` slots of the epoch's end: 10 % of targets at 18 hours. On a chain that meets the floor, a race lasts about `K`, far below the `4K` slots from a cut-off to the next epoch, so the grinding bounds cover every target.
- The last column rests on a candidate from the finality study: the smallest contributions of 25 sub-windows, each bound to its parent's, under a sequential delay. That design is not settled. It must also be compared with a single delay on today's cut-off value, and its delay prototype is unmeasured. The nonce's RFC reads these figures again.
- Bedrock has no deployed network, so the middle column exists only until the nonce lands.

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

This is why the `K` row asks for `K` and `φ` to be checked again when `k`, `f` or `T_M` changes. `T_M` is 15 rounds and leaves out the gossip after the last hop, so a strict delay bound lies past the 15 s that 18 hours holds without a deflation, and past the 11 s it holds after one.

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
| 20 s | 1,000.8 | 0.80, about 20 minutes' wait on average |

The specification therefore states the chance only at `Δ = 10`, and makes no statement at `T_M`.

The count covers the slots after the block, up to and including the slot of the tip, as `density_over_slots` counts them. Every canonical block occupies its own slot, so the count of occupied slots is at least the count of blocks, and a floor sized on blocks keeps its liveness. Under random delay a floor on occupied slots could stand at 1,225. Under the worst case no larger lower bound is derived, because an adversary that orphans a run of honest blocks leaves one countable uncle. An uncle counts only a genuine lottery win, so a side cut off from the rest counts no more occupied slots than the slots it won.

The floor holds back a side cut off from the rest until it has made `φ + 1` blocks:

| The side's share of the stake | Days to fix its fork, mean | Earliest at `ε` |
| --- | --- | --- |
| 0.1 | 3.49 | 2.87 |
| 0.2 | 1.75 | 1.44 |
| 0.25 | 1.40 | 1.15 |
| 0.3 | 1.17 | 0.96 |
| a third | 1.05 | 0.87 |

- This is about half of the 2.2 and 7.4 days that 2,160 blocks give a third and a tenth.
- The floor holds back past `K`, with chance `1 − ε`, a side of at most 0.385 of the stake. A side of 0.4 makes its `φ + 1` blocks after 0.88 days on average.
- The protection ends when a sparse chain's inferred stake corrects. A side keeps its thresholds for at least 3 days, and has corrected in full 7.5 to 15 days after the split.

### What the floor leaves open

- **Partitions.** The adversary signs on both sides of a partition, so no floor separates one at a third. At 18 hours a side the floor holds back has at most 0.052 of honest stake when a third signs on it. A split the adversary signs on waits for operators.
- **An eclipse.** A fork started at the eclipse takes a third 1.05 days. A fork prepared in advance needs the eclipse only for the last part of that. At mean rates, against a node that received the honest chain until the eclipse began, a third's fork needs an eclipse of about 12.5 hours, where 2,160 blocks need about 26. How long an adversary can hold an eclipse is open.

### Alternatives

- **A floor on the density of the `K` slots after the block.** It holds a sparse side back for 8.25 days at the earliest. But it stalls finality whenever the active stake falls below 0.562 under random delay, for up to 11.25 days. The floor used here never stalls: a block made as the active stake halves is fixed after 0.75 days on average under random delay.
- **A cap on the inference's correction.** The inference reads a side cut off as stake that left, so a cap lengthens the protection and the stall after a genuine fall alike. The floor used here gains nothing from a cap at 18 hours, because a side of a tenth or more makes its `φ + 1` blocks before the first correction. The inference's correction stays uncapped.

## Counting from the tip's slot

`K` counts back from the slot of the tip of `c_loc`, not from the clock. `commit` therefore reads no clock and needs no tick per slot. A block is final `K` slots after its slot, plus the gap to the next block.

| | From the clock | From the tip's slot |
| --- | --- | --- |
| New machinery | A tick per slot, since `B_imm` moves with no block | None. `commit` stays in `on_block` |
| `commit` reads the wall clock | Yes, for the first time | No. Only step 6 of Block Header Validation does, as today |
| Forged clock step of +18 h, alone (simulated) | `B_imm` goes from 18 h old to about 8.5 h old at once, about 1,019 deep | No move until the chain gains a block in the shifted range: still 18 h old, about 2,160 deep |
| The same step plus one block in the last 30,540 slots of the shifted range (simulated) | As above | The same outcome: about 8.5 h old, about 1,018 deep |
| Node keeps running and receives nothing for `K` slots (simulated) | `B_imm` climbs to 1,019 below its stale tip, which limits how far it can still heal | No move: about 2,160 below it |
| Lag behind the clock rule (simulated, delivery aside) | None | About 29 slots on average, about 44 while a third withholds |
| The bounds of [What the finality window holds](#what-the-finality-window-holds) | Hold as computed | Hold on an honest clock: step 6 gives tip slot ≤ clock, so this rule fixes a subset of what the clock rule fixes |
| Bootstrap test | Reads the clock, so nodes can differ at the boundary | Reads the later of the two tips: a function of the two chains alone |

**Residual risk: clock faults.** Neither rule makes a shifted clock safe, and the study has no analysis of clock faults. A time service that applies any forward step at once lets one forged reply move a node's clock.

- The floor bounds the damage under both rules: `B_imm` stays about 1,019 occupied slots deep, about 860 blocks on the specification's Blend. That is below the 1,510 blocks the study's depth bound proves against a third at 10 s, at the count of its code, so a shifted node loses that guarantee.
- Under the tip rule the attacker needs a forged reply plus one block in the shifted range. That block may be the node's own: a staking node on a shifted clock proposes at the shifted slot. With 1 % of stake that takes 49 minutes on average, and about 10 of its wins fall in the part of the range that reaches the floor.
- This revision adds no clock rule. The [Clocks](../cryptarchia-v1-protocol.md#clocks) annex already assumes in-sync clocks.

## The switch to Online

A node under the Bootstrap rule keeps `B_imm` frozen, and the forks it rejected stay in its block tree. The Online rule has no depth bound to refuse them. So the node runs `commit` on `c_loc` before it processes any further block. Without this step, the first block processed after the switch that does not extend `c_loc`, which an attacker can send, makes a longer rejected fork win by length, and `B_imm` then passes the divergence block. A model of the rules shows this: a fork sparse in the density window but longer overall loses under Bootstrap, and wins at the next such block when `commit` is left out.

### Alternative: hold `B_imm` until the node has been online for `K`

This revision has no hold. `B_imm` stays frozen under Bootstrap, moves at the switch, and moves at once after a restart within `T_offline`.

- **At the switch, a hold is unsafe or pointless.** Without `commit`, nothing is pruned, and a rejected fork wins by length for the whole hold. `B_imm` then lands on it when the hold ends. With `commit`, `B_imm` has already moved, so the hold no longer delays the step it was meant to delay.
- **After a restart, a hold is safe and costs 18 hours per restart.** A node that restarts more often than every 18 hours never finalizes. A network-wide upgrade stalls `B_imm` on every node for 18 hours, and everything that waits for finality on those nodes waits with it.

### The restart path

After a restart within `T_offline`, the fork runs over `K` slots and the node's chain stopped up to 20 minutes earlier. The margin `K/T_offline` is 54, as it is today. In a private race at 10 s, the head start makes 18 hours behave like 16.8 at 0.298 and 16.5 at a third. This is an estimate from a private race, not the study's bound.

- A nonce that resists grinding needs 12.5 hours against a third, so a third still holds on this path.
- With today's nonce, the share on this path falls from 0.298 to about 0.295, from the study's bound at that wait.

**Open question.** Deferring `commit` to the end of Initial Block Download would close the head start for a node with an honest IBD peer, with no stall. It would not cover a node with no IBD peers, and a malicious IBD peer could prolong IBD. Today's rule has the same exposure, so this RFC leaves it out.

### `T_boot` has no relation to `K`

`T_boot` stays at 24 hours. That it exceeds 18 hours is incidental. With an honest peer, the density test does not read `T_boot`. Under an eclipse, the node sees the honest chain only if `T_boot` outlasts the eclipse. So `T_boot` buys time to find an honest peer.

## Comparing forks

**On every block.** The Bootstrap rule now runs on every block. `on_block` used to skip it when a block extends `c_loc`, so a chain chosen by length while a fork is young could keep `c_loc` past `K` with no density comparison, and `commit` then fixes it at the switch. Two nodes with the same blocks could end on different chains by delivery order alone. A later block of the other fork re-runs the comparison, so the node must also stop receiving that fork. The Online rule keeps the skip.

**Forks below `B_imm`.** Both rules check descent from `B_imm` explicitly, because step 8 of Block Header Validation allows incomplete pruning. Without the check, a node that restarts under the Bootstrap rule can select a denser fork below `B_imm`, and `commit` then has no path from `B_imm` to `c_loc`.

**Where the two rules differ.** The Online and Bootstrap rules compare a fork differently in one case: its divergence block `D` is at least `K` slots before the later tip, but `B_imm` has not passed it. That happens for three reasons:

- `D`'s child is younger than `K`, for about one block interval.
- The floor holds `B_imm` back on a sparse chain.
- The local tip lags the later tip, as after a restart, or while the rest of the chain has not arrived.

Online then compares by length and Bootstrap by density, so a fork the Bootstrap rule rejected can survive the switch, and wins if it is longer. In the model, at mean rates, a third's fork of 1,019 blocks that reaches the node before the rest of the honest chain does this with a lag of 12.5 hours. This is accepted, because a test that reads only the slot of `D` and the two tips gives the same result from either branch. No small rule change closes it. Pruning the fork at the switch does not hold, because `D` lies above `B_imm` and the fork can be delivered again.

**Open question: the order of comparison.** The Bootstrap test compares two chains at a time, and it is not transitive. With three forks, the result can depend on the order in which a node visits them. In random trees, 953 of 3,497 cases depend on the order, against 781 with the depth test, so this class exists today. Between two chains, the test gave no disagreement beyond exact ties in 236,941 pairs, where the depth test gave 6,848. A fixed order would give one result per local tip, but nodes on different local tips can still differ, so this RFC does not fix one.

## What else reads `K`

- **The epoch.** Every epoch value stays as it is: phases of 194,400, 194,400 and 259,200 slots, an epoch of 648,000 and a `PERIOD` of 388,800. Changing `K` now changes the epoch. The window `s_gen` stays at `⌊k/4f⌋`, 4.5 hours, against the 4.8 to 4.9 hours a third needs at `1e-9`. The change does not worsen this.
- **The uncle window.** It is 360 slots against 64,800. A candidate's parent is above the proposer's `B_imm` exactly, not with high probability, because a `B_imm` that has moved lies at least `K` behind the slot being built. No candidate was pruned in a model of 9,000 random trees.
- **Blocks above `B_imm`.** Their number is no longer bounded by `k`, which changes how a node sizes the ledger states it keeps.

## Compatibility

This is a consensus change. Nodes on the old rule and on this one can fix different blocks in a deep reorganization, so a network runs one rule or the other. No header, wire format or epoch value changes. Bedrock has no deployed network, so the change needs no migration.

## Reproducing the figures

The figures come from the finality study: [`tools/simulators/finality`](https://github.com/logos-blockchain/research/tree/b2ff0767d350cf92346bf996bc1c1b88d2b1065a/tools/simulators/finality). Its notes carry each result with its check: `SLOTS.md` phase K, `SETTLEMENT.md` B6, `FURTHER.md` G7 and `RATE.md`. `make k1`, `k2`, `k3`, `k7`, `k8` and `k9` give the waits, the shares, the floor and the cap. The study reads `B_imm` against the clock. Its figures carry over as [Counting from the tip's slot](#counting-from-the-tips-slot) states.

The rows marked simulated, and the figures in [The restart path](#the-restart-path) and [Comparing forks](#comparing-forks), come from small models of this RFC's rules. The `φ` code and both fork choice rules were run as the specifications print them.

> **TODO (author):** publish the small models with the study before this RFC cites them.

# Details

## 1. The latest immutable block is counted in slots

In [Constants](../cryptarchia-v1-protocol.md#constants), `k` stops being a depth, and `K` and `φ` are added. The Notation row of `s` is deleted.

```diff
-| k | security parameter | Block depth finality. Blocks deeper than k on any given chain are considered immutable. | 2160 blocks |
+| k | security parameter | The number of blocks expected in K slots at the rate f. | 2160 blocks |
+| K | finality window | The number of slots a block must lie behind the tip of the local chain before Commit can make it immutable. ... | ⌊k/f⌋ = 64,800 slots (18 hours) |
+| φ | finality floor | The number of occupied slots that must follow a block before Commit can make it immutable, derived in Finality Floor. ... | 1,019 occupied slots |
```

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

An uncle's slot now also counts for the floor, in [Uncle References](../cryptarchia-v1-protocol.md#uncle-references) and in [Block Construction](../bedrock-v1.1-block-construction.md).

## 2. The fork choice rules read the age of a fork in slots

```diff
-def bootstrap_fork_choice(c_local, forks, k, s_gen):
+def bootstrap_fork_choice(c_local, forks, K, s_gen, B_imm):
     c_max = c_local
     for c_fork in forks:
+        if not is_ancestor(B_imm, c_fork):
+            continue
         depth_max, depth_fork = common_prefix_depth(c_max, c_fork)
-        if depth_max <= k:
+        sl_div = grandparent(c_max, depth_max).slot
+        sl_top = max(c_max.slot, c_fork.slot)
+        if sl_div + K > sl_top:
             # ... longest chain
         else:
             # ... density over s_gen
```

```diff
-def online_fork_choice(c_local, forks, k):
+def online_fork_choice(c_local, forks, B_imm):
     c_max = c_local
     for c_fork in forks:
+        if not is_ancestor(B_imm, c_fork):
+            continue
         depth_max, depth_fork = common_prefix_depth(c_max, c_fork)
-        if depth_max <= k:
-            if depth_max < depth_fork:
-                c_max = c_fork
-        else:
-            continue
+        if depth_max < depth_fork:
+            c_max = c_fork
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

## 3. The switch to Online runs `commit`

In [Prolonged Bootstrap Period](../cryptarchia-v1-bootstr-sync.md#prolonged-bootstrap-period), the node runs `commit` on `c_loc` when the fork choice rule switches to Online, before it processes any further block. The same section's reasoning on `s_gen` now reads the finality window. A fork decided by density diverged at least `K` slots before the later tip, and `s_gen < K`, so the chain with the later tip holds the whole window.

## 4. The finality window sets the epoch schedule

Phases of `3K`, `3K` and `4K` slots, an epoch of `10K`, and a `PERIOD` of `6K` replace `s` and `⌊k/f⌋`. Each phase that waits for a value to finalize must last at least `K` slots, or the value is not final when the phase ends.

## 5. Two periods stay below the finality window

- `W·f⁻¹ < K` replaces `W ≤ ⌊0.6k⌋`. It sits in the `W` row, and in the note in [Uncle Selection](../cryptarchia-v1-protocol.md#uncle-selection).
- `T_offline < K`, in [Constants](../cryptarchia-v1-bootstr-sync.md#constants) of Bootstrapping & Synchronization.

## 6. The count of occupied slots takes a chain

`density_over_slots` read "the honest chain". `commit` reads it over `c_loc`, so it gains an argument:

```diff
-density_over_slots(s, p)
+density_over_slots(c, s, p)
```

The range stays `[s, s + p)`. `commit` passes `s = sl_C + 1` and `p = sl_tip − sl_C`, so `C` itself does not count and the tip does.

## 7. Fork pruning removes every fork

`prune_forks` restarted from `T` on every iteration, so one call removed only one fork. Step 8 of Block Header Validation leans on this step, so it now accumulates. `commit` also passed it a third argument it does not take.

```diff
-T' := prune_blocks(B_tip, B_div, T)
+T' := prune_blocks(B_tip, B_div, T')
```

## Chores

- Removed `s`, the name "slot security parameter", `block_at_depth`, "slot finality period" and the second name for `k`, "safety parameter".
- Fixed `s` where `s_gen` was meant in `density`, and made both fork choice functions valid Python.
- Renamed the Praos heading of the long range attack in [Fork Choice Rule](../fork-choice.md) to Online, and reworded its Overview.
- In [Setting the Fork Choice Rule](../cryptarchia-v1-bootstr-sync.md#setting-the-fork-choice-rule) and [Offline Grace Period](../cryptarchia-v1-bootstr-sync.md#offline-grace-period), reworded the lines that read `k`, restated the example's attack in slots, and replaced two images with one diagram.
- In [\[Overview\] Bedrock Architecture](../bedrock-architecture-overview.md), the [Bedrock Genesis Block](../bedrock-genesis-block.md) and two analyses, reworded the lines that read finality as a depth.
- In the [Blend Protocol](../blend-protocol.md), added a pointer from `T_M` to `K` and `φ`.

# Implementation

- [ ] Replace the LIB update with the `commit` loop, reading `K` and `φ`, with no slot tick
- [ ] Compute the floor with `density_over_slots` over the local chain, uncles included
- [ ] Remove the depth bound from the Online fork choice, and check descent from the LIB in both rules
- [ ] Replace the depth test of the Bootstrap fork choice with the test on the divergence block's slot
- [ ] Run `commit` when the fork choice rule switches to Online, before any further block, and persist the two together
- [ ] Prune all forks below the LIB in one call, at every LIB move and at the switch to Online
- [ ] Expire the wallet's leader-claim reservations after `K` slots instead of `k` immutable blocks
- [ ] Size the kept ledger states for blocks above the LIB, which `k` no longer bounds
- [ ] Update the fork monitor of the test framework
- [ ] Review the forward step of the time service against [the clock faults](#counting-from-the-tips-slot)
- [ ] Prove the rule in the formal model, floor included: the current theorems read a depth of `k`, or a confirmation rule beside it
- [ ] Add tests: a fork rejected by the Bootstrap rule against the switch, pruning of several forks at once, the floor's first and last slot, and the Bootstrap test from either branch and in any delivery order
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
| [\[Analysis\] Block Times & Blend Network](../analysis-block-times-blend-network.md) | Modified | 1.0.1, wording only |
| [\[Analysis\] Total Stake Inference](../analysis-total-stake-inference.md) | Modified | 1.0.1, wording only |
