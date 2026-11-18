# [RFC] SDP: Raise the default inactivity period to three epochs

**Motivation and proposal:** [PR #531](https://github.com/logos-co/logos-lips/pull/531)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-10 |

## Reviewer Orientation

Single-document change. Read the PR's Motivation first, then [the new default](#1-the-default-inactivity-period-of-the-blend-network-is-3) and [what a value of 2 does](#2-the-definition-states-what-a-value-of-2-does) in the [Service Declaration Protocol](#affected-specifications). [What the change moves](#what-the-change-moves) shows the effect.

# Discussion

## The chains

A snapshot for epoch `n` holds the registry at the end of epoch `n − 2`, so the latest report it can contain attests to epoch `n − 3` ([Message Timing](../bedrock-service-declaration-protocol.md#message-timing)). With `inactivity_period` = `2 + k`, the active set of epoch `n` keeps a declaration whose report for an epoch from `n − 3 − k` to `n − 3` was accepted, or that was declared in epoch `n − 4 − k` or later.

At `k` = 0 that is the report for `n − 3` alone. A node reports an epoch only if its declaration is in that epoch's set, since it collects blending tokens only as a member. So a declaration out of the set of epoch `n` cannot report `n`, and is out of the set of `n + 3`. The sets of `n`, `n + 3`, `n + 6` and so on form a chain that the other epochs do not feed. At `k` ≥ 1 the windows of consecutive sets overlap, so a declaration that reports in one chain returns to the others.

## What the change moves

These histories run the rules of the Service Declaration Protocol and of the Blend Protocol, with 40 declarations, a minimal network size of 32, and every node online and reporting whenever it can unless the history says otherwise.

| History | `inactivity_period` = 2 | `inactivity_period` = 3 |
| --- | --- | --- |
| One declaration misses its report for epoch 10 | out of epochs 13, 16, 19, … for good | in every set |
| One declaration misses its reports for epochs 10 and 11 | in one epoch of three for good | out of epoch 14 only |
| No block in epoch 10 | Blend off in epochs 12, 15, 18, … for good | Blend always on |
| No block in epoch 10, under the implementation's rejection of the reports for that epoch | Blend off in two epochs of three for good | Blend off in epoch 13 only |
| One epoch, 12, below the minimal network size | Blend off in epochs 12, 15, 18, … for good | Blend off in epoch 12 only |
| A dip below the minimal network size that outlasts the period | Blend off for good | Blend off for good |

The last row is out of scope: no report can be made while the set is below the minimum, whatever the period.

## Cost

A declaration whose node stops reporting stays in the active set one epoch longer. After its last report, included in epoch `a`, it is in the sets up to epoch `a + 3` instead of `a + 2`. Messages that nodes route through it in that epoch are lost, as in the epochs it already stays.

## Why 3

3 is the smallest value at which the windows of consecutive sets overlap. 4 also tolerates two consecutive missed reports, at the cost of a second extra epoch for a node that stopped.

## Compatibility

The default is the value of era 0's `service_params` entry for the Blend Network ([Era Parameters](../bedrock-eras.md#era-parameters)). Era 0's record, era digest and fork digest therefore change. No encoding changes. Bedrock has no deployed network, so the change needs no migration. The implementation's era schedules and genesis templates hold 2 ([Implementation](#implementation)).

# Details

## 1. The default inactivity period of the Blend Network is 3

In [Default Service Parameters](../bedrock-service-declaration-protocol.md#default-service-parameters):

```diff
 class BlendNetworkServiceParameters:
-    inactivity_period: 2
+    inactivity_period: 3
```

## 2. The definition states what a value of 2 does

In [Service Parameters](../bedrock-service-declaration-protocol.md#service-parameters):

```diff
 A value of `2 + k` tolerates `k` consecutive missed reports (Message Timing).
+At 2, a declaration that misses one report is out of the active set of every third epoch
+from then on, as it cannot report an epoch whose set it is not in.
 Any value below 2 excludes every declaration.
```

# Implementation

- [ ] Set the Blend Network's `inactivity_period` to 3 in the era schedules (`nodes/node/era/schedule/0.yaml`, `nodes/node/binary/src/config/deployment/era/schedule/0.yaml`) and the genesis deployment templates (`deployment/ceremony/genesis/*/deployment-template.yaml`).
- [ ] Add tests: at 3, a declaration that misses one report stays in every active set, and an epoch without blocks leaves the active sets of later epochs full.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.10.0 |
