# [RFC] SDP: Keep declarations active while their service does not run

**Motivation and proposal:** [PR #530](https://github.com/logos-co/logos-lips/pull/530)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Service Declaration Protocol](#affected-specifications): [the credit](#1-an-epoch-in-which-a-service-does-not-run-counts-as-reported) | which declarations are credited and with which epoch; that a credit never revives a declaration outside the epoch's active set |
| 2 | Critical | [Mantle](#affected-specifications): [the finalization step](#2-sdp-epoch-finalization-applies-the-credit) | the epochs it covers, an epoch without blocks included; the era whose minimal network size it reads |
| 3 | Medium | [Blend Protocol](#affected-specifications): [active messages only where Blend runs](#3-blend-asks-for-active-messages-only-in-epochs-it-runs) | the scope of the obligation to construct an active message |

# Discussion

## The trap today

A declaration is in the active set of epoch `n` while `active + inactivity_period >= n`, and `active` moves only when an active message is accepted. An active message carries an activity proof built from a blending token, and a node collects blending tokens only from the Blend messages it processes. Below the minimal network size Blend does not run, so no node of the set can report the epoch.

With `inactivity_period` = 2, the active set of epoch `n` keeps a declaration only if its report for epoch `n − 3` was accepted, or if it was declared in epoch `n − 4` or later. The sets of epochs `n`, `n + 3`, `n + 6` and so on therefore form a chain that the other epochs do not feed. An epoch below the minimum empties the next set of its chain, which is then below the minimum too.

The table runs these rules for three histories. Every declaration is online and reports whenever it can, and the minimal network size is 32. `#` marks an epoch in which Blend runs.

| History | Today | With the credit |
| --- | --- | --- |
| 40 declarations; 9 withdraw in epoch 10 (out from epoch 12); 9 join in epoch 11 | `############.##.##.##.##.##.##.##.##.##.` | `############.###########################` |
| 40 declarations; 9 withdraw in epoch 10; 5 join in epoch 25 | off from epoch 12 for good | off from epoch 12, on again from epoch 27 |
| 31 declarations at genesis; 1 joins in epoch 5 | never on | on from epoch 7 |

Without the credit, `inactivity_period` = 3 avoids the loss in the first history and changes nothing in the other two: it delays the expiry, but a dip that outlasts it still empties the set.

## Alternatives

- **Keep Blend running below the minimum, without data messages.** Nodes would then collect blending tokens and report. It changes the [Fallback](../blend-protocol.md#fallback) rule and keeps nodes sending cover traffic while Blend is unsafe to use, only so that they can prove an activity that earns nothing.
- **Exempt such epochs from `inactivity_period`.** The effect is the same, but each declaration would need a count of the exempt epochs since its `active`. The credit reuses `active`.
- **Raise `inactivity_period`.** It delays the expiry by the added epochs and no more ([The trap today](#the-trap-today)).
- **Leave it.** Providers must withdraw and declare again, and Blend starts only when 32 new declarations are counted in the same epoch: with `inactivity_period` = 2, a declaration made in epoch `e` is counted, without a report, in the sets of epochs `e + 2` to `e + 4`.

## Risks

- The declarations of nodes that stopped running stay in the set while Blend does not run. When the set reaches the minimum again, they count towards it, so Blend can start with members that never report. Those leave the set as any member that stops reporting does today. Messages a node routes through them in the meantime are lost.
- A credited epoch earns no reward. Blend's [Reward Calculation](../blend-protocol.md#reward-calculation) calculates no reward for an epoch below the minimal network size, and the credit leaves that rule as it is.

## Missed reports with `inactivity_period` = 2

This change leaves a related effect of the same chains alone. A declaration that misses one report is out of the next set of that chain, so it cannot report that epoch either, and it stays out of every third epoch from then on. An epoch without blocks makes every report for the epoch before it impossible, so the whole chain of that epoch loses Blend for good. The implementation also rejects the reports for the epoch without blocks, so there two chains of three lose it. With `inactivity_period` = 3, the same simulation shows neither effect. Whether to raise the default is an open question.

## Compatibility

The credit changes the SDP state at epoch boundaries, so every node must apply it to agree on the active sets. No encoding changes, and no record field is added. Bedrock has no deployed network, so the change needs no migration. The implementation rejects an active message for an epoch below the minimal network size, which no node can build, and has no credit ([Implementation](#implementation)).

# Details

## 1. An epoch in which a service does not run counts as reported

In [Active](../bedrock-service-declaration-protocol.md#active), after the validity of an active message:

```diff
+An epoch in which a service does not run counts as reported for every declaration in the
+service's active set for that epoch. The first block after that epoch sets the `active` of
+each such declaration to its own epoch (SDP Epoch Finalization). The Blend Network does not
+run in an epoch whose active set holds fewer declarations than the minimal network size of
+that epoch's era (Fallback).
```

In [Declaration Storage](../bedrock-service-declaration-protocol.md#declaration-storage), `active` covers the credit:

```diff
-- `active` is the epoch of the block that contained the latest accepted active message,
-  initialised to `created + 2`;
+- `active` is the epoch of the block that last accepted an active message for the
+  declaration or credited it with an epoch its service did not run, initialised to
+  `created + 2`;
```

A credit never lowers `active`: a declaration in the active set of epoch `m` was declared by epoch `m − 2`, so its `active` is at most the epoch of the block that credits it.

## 2. SDP epoch finalization applies the credit

In [SDP Epoch Finalization](../bedrock-v1.1-mantle-specification.md#sdp-epoch-finalization), after the withdrawn declarations are removed:

```python
for m in range(parent_epoch, current_epoch):
    members = active_sets[m][ServiceType.BN]
    if len(members) < minimum_network_size(m):
        for declaration_id in members:
            if declaration_id in declarations[ServiceType.BN]:
                declarations[ServiceType.BN][declaration_id].active = current_epoch
```

- `parent_epoch`, the epoch of the previous block, and `active_sets`, the Active Set of each epoch, join the inputs.
- `minimum_network_size(m)` is the `minimum_network_size` of the era of epoch `m`.
- The range covers every epoch that ended since the previous block, an epoch without blocks included.

## 3. Blend asks for active messages only in epochs it runs

In [Active Message](../blend-protocol.md#active-message):

```diff
-A node l for every epoch must construct an active message, which must follow ...
+For every epoch in which the minimal network size is reached (Fallback), a node l must
+construct an active message, which must follow ...
```

# Implementation

- [ ] In `ServiceState::try_apply_header` (`ledger/src/mantle/sdp/mod.rs`), after the withdrawn declarations are removed, credit the declarations of every epoch since the previous block whose Blend active set held fewer than the `minimum_network_size` of its era, skipped epochs included: set their `active` to the new epoch.
- [ ] Add tests: a set that falls below the minimum keeps its declarations, and Blend runs again once the set reaches the minimum; a declaration outside the epoch's active set is not credited; a skipped epoch below the minimum is credited.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.10.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 1.21.0 |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.10.0 |
