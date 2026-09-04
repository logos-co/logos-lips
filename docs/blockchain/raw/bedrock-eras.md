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

An era is a range of consecutive epochs ([Cryptarchia Protocol](cryptarchia-v1-protocol.md#epoch)) governed by one set of protocol rules. Protocol rules change only at era boundaries.

# Protocol

## Era Schedule

The era schedule is embedded in the node software and is not read from the chain. Each network (mainnet, testnet) has its own schedule.

The schedule is a strictly increasing list of epoch numbers. The first entry is 0. Entry $`n`$ (1-based) is the first epoch of era $`n`$, denoted $`E_n`$. Era $`n`$ comprises the epochs from $`E_n`$ up to, but not including, $`E_{n+1}`$; the last era of the schedule is unbounded.

The era of an epoch $`ep`$ is $`\textbf{era}(ep) = \max\{n : E_n \le ep\}`$. The era of a slot $`sl`$ is the era of its epoch: $`\textbf{era}(sl) = \textbf{era}(\lfloor sl / \text{EPOCH\_LENGTH} \rfloor)`$, with the epoch length defined in [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule). Era $`n`$ begins at slot $`E_n \cdot \text{EPOCH\_LENGTH}`$. An era must not change the epoch length; a change moves the first slot of every scheduled era. The **era in force** is $`\textbf{era}(sl)`$ of the current slot.

The era number is encoded as a `uint8` in every binary wire field that carries it. The schedule must not exceed 255 entries; a later era cannot be expressed in the wire fields.

A schedule entry must never change once a release has published it. Changing it makes nodes running different releases apply different rules to the same slots, which is a fork. A defective era is corrected by a new era at a future epoch.

An era defines rules, not the values set under them. A [Service Parameters](bedrock-service-declaration-protocol.md#service-parameters) entry changes a value within an era.

## Interpreting Chain Data

A block, and everything it carries, is parsed, validated and executed under the rules of $`\textbf{era}(sl)`$ of the block's slot. An era must not move or re-encode the header fields up to and including `slot`: the slot selects the era, so it must parse before the era is known; otherwise a synchronization stream carrying blocks of two eras cannot be parsed.

A procedure that reads a span of the chain — [fork choice](fork-choice.md), [Fork Pruning](cryptarchia-v1-protocol.md#fork-pruning), [synchronization](cryptarchia-v1-bootstr-sync.md) — runs under the era in force.

A node must implement every era from $`\textbf{era}(sl_{B_\text{imm}})`$ to the era in force, where $`B_\text{imm}`$ is the [Latest Immutable Block](cryptarchia-v1-protocol.md#latest-immutable-block). A node that must validate a block whose slot lies in an era it does not implement must halt with an error to the operator. A block whose slot precedes that of $`B_\text{imm}`$ is discarded without a halt.

When an era begins, a node must remove from its mempool every transaction that is not valid under the new era. Mempool admission applies the new era's rules, whichever era's protocol delivered the transaction.

## Era Migration

Every era after the first defines a migration from its predecessor: a function over the recorded chain state — the [ledger](bedrock-v1.1-mantle-specification.md) state, the [Declaration Storage](bedrock-service-declaration-protocol.md#declaration-storage), and snapshots taken but not yet consumed.

The migration must be:

- **Deterministic** — a function of the pre-boundary chain state alone, with no clock and no node-local input. Otherwise nodes diverge on identical chains.
- **Total** — defined for every state reachable under era $`n`$. A migration undefined for a reachable state halts the network at the boundary.
- **Identity by default** — every state component the era does not redefine crosses unchanged.

The migration applies per chain, not per wall clock. Validating or executing a block whose parent lies in an earlier era first applies the intervening migrations, in order, to the state after the parent.

Derived values are not migrated. The [Epoch State](cryptarchia-v1-protocol.md#epoch-state) of an epoch in era $`n+1`$ is computed under era $`n+1`$'s rules; the values it reads from earlier epochs are used as they were derived. The recorded inputs of such derivations — e.g. the [snapshot](bedrock-service-declaration-protocol.md#snapshots) consumed with its two-epoch delay during the new era's first epochs — are part of the recorded chain state and thus of the migration's domain.

Node-local state that is not derived from the chain — caches, key pools, connections — is not migrated. The [Era Transition Period](#era-transition-period) governs it.

## Era Transition Period

The Era Transition Period is the first $`T_\text{era} = 30`$ rounds ([Blend Protocol](blend-protocol.md#time)) of a new era.

$`T_\text{era} \ge T`$, the Blend [Transition Period](blend-protocol.md#transition-period). If violated, payloads in flight at the boundary are dropped, and the connections still carrying them are closed as misbehaving.

During the Era Transition Period a node must:

1. Run the network protocols of both eras.
2. Accept messages and transaction gossip under both eras.
3. Retain every input the predecessor era's checks read until the period ends.

After the Era Transition Period the node must drop the old era's network protocols and must not process its messages.

The Era Transition Period applies to the network layer only.

## Network Protocol Identity

Every libp2p protocol identifier and gossipsub topic carries the era number in place of a version: `/logos-blockchain/<protocol>/<era>` for mainnet and `/logos-blockchain-testnet/<protocol>/<era>` for testnet, with `<era>` the decimal era number.

The era in an identifier is the era in force, not the era of the data carried.

During the [Era Transition Period](#era-transition-period) a node advertises and accepts the identifiers of both eras.

## Horizon

The horizon $`H`$ is an epoch number embedded in the node software beside the schedule. A schedule entry may be added only with a first epoch after the $`H`$ of every earlier release; an earlier release whose $`H`$ extends past that epoch interprets those slots under the predecessor era and forks. $`H`$ must not precede the first epoch of the last entry of the release's own schedule; a smaller $`H`$ halts the release before an era it implements begins.

From the first slot of epoch $`H+1`$, per the local clock, a node must halt with an error to the operator; until it has halted, it must not propose blocks and must not serve synchronization responses.

The halt must not be triggered by information received from peers, such as advertised eras.
