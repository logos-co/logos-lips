# BEDROCK-ERAS

| Field | Value |
| --- | --- |
| Name | Bedrock Eras |
| Slug | 247 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-09-04 |

# Introduction

An era is a range of consecutive epochs ([Cryptarchia Protocol](cryptarchia-v1-protocol.md#epoch)) governed by one set of protocol rules.

# Overview

An era schedule embedded in the node software maps every epoch to an era. A node applies to a block the rules of the era of the block's slot, and to its network protocols the era of the slot given by its clock. Every era after the first defines a migration of the recorded chain state from its predecessor. When the era changes, a node runs the network protocols of both eras for a transition period, and every protocol identifier carries the era. A software release halts at its horizon, the last epoch it interprets.

# Protocol

## Constants

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| *none* | era schedule of mainnet | The first epochs of the eras of mainnet. | `[0]` |
| *none* | era schedule of testnet | The first epochs of the eras of testnet. | `[0]` |

## Notation

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| $`E_n`$ | first epoch of era $`n`$ | Entry $`n`$ (1-based) of the era schedule. | $`E_1 = 0`$ |
| $`\textbf{era}(ep)`$ | era of an epoch | The era whose first epoch is the largest at or before $`ep`$. | $`\max\{n : E_n \le ep\}`$ |
| $`\textbf{era}(sl)`$ | era of a slot | The era of the slot's epoch, with the epoch length of [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule). | $`\textbf{era}(\lfloor sl / \text{EPOCH\_LENGTH} \rfloor)`$ |
| *none* | era in force | The era of the slot given by the local clock ([Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation)). | $`\textbf{era}(\textbf{wallclock\_time}().\textbf{to\_slot}())`$ |
| $`H`$ | horizon | The last epoch a software release interprets, per network. | set per release |
| $`T`$ | Transition Period | The Blend [Transition Period](blend-protocol.md#transition-period) of the era in force. | |
| $`B_\text{imm}`$ | latest immutable block | See [Cryptarchia Protocol](cryptarchia-v1-protocol.md#latest-immutable-block). | |

## Era Schedule

The era schedule is embedded in the node software and is not read from the chain. Each network has its own schedule. The schedule is a strictly increasing list of epoch numbers whose first entry is 0.

An era must not change $`k`$, $`f`$ ([Constants](cryptarchia-v1-protocol.md#constants)) or the epoch length. Otherwise every later era boundary moves. An era must not change the comparison of chains that diverge by at most $`k`$ blocks ([Online Fork Choice Rule](fork-choice.md#online-fork-choice-rule)). Otherwise fork choice depends on the order in which forks were seen for the first $`k`$ blocks of the era.

A schedule entry, the rules of its era and the migration into it must never change once a software release has published the entry. Otherwise nodes running different releases fork. A software release must not publish an entry whose epoch has begun. Otherwise a node that installs the release holds state executed under the wrong era.

An era does not fix the values of [Service Parameters](bedrock-service-declaration-protocol.md#service-parameters). A new `ServiceParameters` value changes a parameter without an era change.

## Interpreting Chain Data

A block or proposal, and everything it carries, is parsed, validated and executed under the rules of $`\textbf{era}(sl)`$ of its slot. `slot` is the first field of the header ([Block Header](cryptarchia-v1-protocol.md#block-header)) and has the same encoding in every era, and every message that carries a block or proposal begins with the header in its [canonical encoding](bedrock-v1.1-block-construction.md#canonical-encoding). Otherwise a node cannot parse a block before it knows the block's era.

[Fork choice](fork-choice.md) compares two chains under the era of the slot of their $`\textbf{common\_ancestor}`$ ([Fork Pruning](cryptarchia-v1-protocol.md#fork-pruning)). The fork choice rule of an era reads only the block tree and the slot of each block. Otherwise it is undefined on the blocks of a later era that re-encodes a field it reads.

At startup and on checkpoint import, a node whose software does not implement the rules of every era from $`\textbf{era}(sl_{B_\text{imm}})`$ to the era in force must halt. A halted node stops every protocol and exits with an error to the operator.

A node keeps in its mempool only transactions valid under the era in force. A transaction is parsed under the era of the topic that delivered it and admitted under the rules of the era in force.


## Era Migration

Every era after the first defines a migration from its predecessor. A migration is a function of the recorded chain state alone. The recorded chain state is the state a Mantle Operation is validated against ([Validation](bedrock-v1.1-mantle-specification.md#validation)), the `stake_thresholds` ([Minimum Stake](bedrock-service-declaration-protocol.md#minimum-stake)) and `parameters` ([Service Parameters](bedrock-service-declaration-protocol.md#service-parameters)), and the [snapshots](bedrock-service-declaration-protocol.md#snapshots) of the current and later epochs.

The migration must be:

- **Total**: defined for every state reachable under the predecessor era. A migration undefined for a reachable state halts the network at the boundary.
- **Identity by default**: every state component the new era does not redefine is unchanged.

A block reads the state after any block of an earlier era with the intervening migrations applied, in order. When the era in force changes, a node applies the same migrations to the state after its local chain tip; it re-validates its mempool and runs the network protocols of the new era against that state.

The [Epoch State](cryptarchia-v1-protocol.md#epoch-state) of an epoch is computed under the rules of the epoch's era. Where it reads the chain state as of a slot, it reads the state after the last block at or before that slot, migrated to the epoch's era. The Epoch State of an earlier epoch is used as it was derived.

The rules of an era verify the Activity Proofs and reward claims of the last epoch of the predecessor era as the predecessor's rules do. Otherwise the rewards of that epoch are lost.


## Era Transition Period

The Era Transition Period is the first $`T`$ [rounds](blend-protocol.md#time) after the era in force changes. It applies to the network layer only. $`T`$ must exceed the clock difference between any two honest nodes. Otherwise those nodes share no round in which both run one era's protocols.

During the Era Transition Period a node must:

1. Accept and open connections on the identifiers of both eras.
2. Validate a Blend message under the era of the connection it arrived on.
3. Keep every input the predecessor era's message checks read until the period ends.

After the Era Transition Period the node must drop the predecessor era's protocols and must not process its Blend messages. A synchronization stream open at the end of the period is served to its end.

## Network Protocol Identity

Every protocol identifier and gossipsub topic a Logos Blockchain specification defines is `/<network>/<era>/<protocol>`. `<network>` is `logos-blockchain` for mainnet and `logos-blockchain-testnet` for testnet. Any other network takes its own name. `<era>` is the decimal era number. `<protocol>` is the identifier the protocol's own specification defines.

A node sends a message it generates over the identifiers of the era in force at generation. A node relays or releases a received or processed Blend message over the era of the connection it arrived on. A node publishes every block it accepts on the block topic of the era in force. A [synchronization](cryptarchia-v1-bootstr-sync.md#downloading-blocks) response carries blocks of any era.


## Horizon

$`H`$ must not be smaller than the last entry of the schedule. Otherwise the node halts at or before the first slot of its last era.

When $`\textbf{wallclock\_time}().\textbf{to\_slot}()`$ reaches the first slot of epoch $`H+1`$, a node halts. The horizon halt must not be triggered by information received from peers.

If an entry is at or before the $`H`$ of a published software release, the nodes of that release do not halt at the new boundary and fork.
