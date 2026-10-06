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

An era schedule embedded in the node software maps every epoch to an era and gives each era a parameter record. A node applies to a block the rules of the era of the block's slot, and to its network protocols the era of the slot given by its clock. Every era after the first defines a migration of the recorded chain state from its predecessor. When the era changes, a node runs the network protocols of both eras for a transition period. Protocol identifiers and transactions carry a digest of the chain's genesis and of the eras it has activated. A software release warns its operator past its horizon, the last epoch it interprets.

# Protocol

## Constants

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| *none* | era schedule of mainnet | The first epoch and the parameter record of each era of mainnet. | $`[(0, P_0)]`$ |
| *none* | era schedule of testnet | The first epoch and the parameter record of each era of testnet. | $`[(0, P_0)]`$ |

## Notation

| Symbol | Name | Description | Value |
| --- | --- | --- | --- |
| $`E_n`$ | first epoch of era $`n`$ | The first epoch of entry $`n`$ of the era schedule, counting from 0. | $`E_0 = 0`$ |
| $`P_n`$ | parameter record of era $`n`$ | The [parameter record](#era-parameters) of entry $`n`$ of the era schedule. | |
| $`\textbf{era}(ep)`$ | era of an epoch | The era whose first epoch is the largest at or before $`ep`$. | $`\max\{n : E_n \le ep\}`$ |
| $`L_n`$ | epoch length of era $`n`$ | The epoch length of [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule) under the rules of era $`n`$. | |
| $`\Delta_n`$ | slot length of era $`n`$ | The slot length of [Constants](cryptarchia-v1-protocol.md#constants) under the rules of era $`n`$, in nanoseconds. | |
| $`S_n`$ | first slot of era $`n`$ | | $`S_0 = 0`$, $`S_n = S_{n-1} + (E_n - E_{n-1}) \cdot L_{n-1}`$ |
| $`\tau_n`$ | start time of era $`n`$ | In nanoseconds since the Unix epoch, as every time $`t`$ here. `genesis_time` is from [Cryptarchia Parameters](bedrock-genesis-block.md#cryptarchia-parameters). | $`\tau_0 = 10^9 \cdot \text{genesis\_time}`$, $`\tau_n = \tau_{n-1} + (S_n - S_{n-1}) \cdot \Delta_{n-1}`$ |
| $`\textbf{era}(sl)`$ | era of a slot | The era whose first slot is the largest at or before $`sl`$. | $`\max\{n : S_n \le sl\}`$ |
| $`\textbf{epoch}(sl)`$ | epoch of a slot | | $`E_m + \lfloor (sl - S_m) / L_m \rfloor`$ with $`m = \textbf{era}(sl)`$ |
| $`\textbf{first\_slot}(ep)`$ | first slot of an epoch | | $`S_m + (ep - E_m) \cdot L_m`$ with $`m = \textbf{era}(ep)`$ |
| $`\textbf{slot}(t)`$ | slot of a time | The slot that contains time $`t`$. $`\textbf{wallclock\_time}().\textbf{to\_slot}()`$ of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) is $`\textbf{slot}(\textbf{wallclock\_time}())`$. | $`S_m + \lfloor (t - \tau_m) / \Delta_m \rfloor`$ with $`m = \max\{n : \tau_n \le t\}`$ |
| *none* | era in force | The era of the slot given by the local clock. | $`\textbf{era}(\textbf{wallclock\_time}().\textbf{to\_slot}())`$ |
| $`H`$ | horizon | The last epoch a software release interprets, per network. | set per release |
| $`T`$ | Transition Period | The Blend [Transition Period](blend-protocol.md#transition-period) of the era in force. | |
| $`B_\text{imm}`$ | latest immutable block | See [Cryptarchia Protocol](cryptarchia-v1-protocol.md#latest-immutable-block). | |
| $`G`$ | genesis block ID | The [Block ID](cryptarchia-v1-protocol.md#block-id) of the [Genesis Block](bedrock-genesis-block.md). | |
| $`D_n`$ | era digest of era $`n`$ | The `hash` of [Block ID](cryptarchia-v1-protocol.md#block-id) over $`E_n`$ as an [`EpochNumber`](cryptarchia-v1-protocol.md#epoch) and $`P_n`$ in its [encoding](#era-parameters). | $`\textbf{hash}(\texttt{ERA\_DIGEST\_V1} \,\|\, E_n \,\|\, P_n)`$ |
| $`F_n`$ | fork digest of era $`n`$ | The same `hash` over $`G`$, `chain_id` encoded as in [Cryptarchia Parameters](bedrock-genesis-block.md#cryptarchia-parameters), and $`D_0`$ to $`D_n`$. | $`\textbf{hash}(\texttt{FORK\_DIGEST\_V1} \,\|\, G \,\|\, \text{chain\_id} \,\|\, D_0 \,\|\, \dots \,\|\, D_n)`$ |

## Era Schedule

The era schedule is embedded in the node software and is not read from the chain. Each network has its own schedule. The schedule is a list of entries, each a first epoch and a [parameter record](#era-parameters). The first epochs strictly increase, and the first of them is 0.

An era must not change the comparison of chains that diverge by at most $`k`$ blocks ([Online Fork Choice Rule](fork-choice.md#online-fork-choice-rule)). Otherwise fork choice depends on the order in which forks were seen for the first $`k`$ blocks of the era.

The nodes of two software releases apply different rules from the first epoch whose era has a different digest in the two schedules. From that epoch they use different fork digests. A software release must not change the rules of a published era, or the migration into it, while keeping the era's first epoch and parameter record. Otherwise the nodes of the two releases apply different rules under one fork digest. A software release must not publish an entry, or change the record of an entry, whose epoch has begun. Otherwise a node that installs the release holds state executed under the wrong era.

## Era Parameters

The parameter record of an era is a layout version followed by the fields below, in this order. A field holds the value of its source constant under the rules of the era. The layout version is a `UINT16` equal to 1. Integers are unsigned and little-endian. A ratio is its numerator, then its denominator, each a `UINT32`. A duration is its whole seconds as a `UINT64`, then the nanoseconds past them as a `UINT32`.

| Field | Encoding | Source constant |
| --- | --- | --- |
| `num_blend_layers` | `UINT64` | $`\beta_{max}`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `minimum_network_size` | `UINT64` | The minimal network size of [Minimal Network Size](blend-protocol.md#minimal-network-size) |
| `network_absorption_in_rounds` | `UINT64` | $`\eta`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `data_replication_factor` | `UINT64` | $`R_D`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `message_frequency_per_round` | ratio | $`F_C`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `maximum_release_delay_in_rounds` | `UINT64` | $`\Delta_{max}`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `target_peering_degree` | `UINT32` | $`\Phi_{CC}`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `verification_rate_per_second` | `UINT32` | $`V`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `edge_node_send_deadline_in_rounds` | `UINT64` | $`T_E`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `core_handshake_deadline_in_rounds` | `UINT128` | $`T_H`$ of [Global Parameters](blend-protocol.md#global-parameters) |
| `activity_threshold_sensitivity` | `UINT64` | $`\theta`$ of [Activity Threshold](blend-protocol.md#activity-threshold) |
| `epoch_config` | three `UINT8` | The lengths of the three phases of [Epoch Schedule](cryptarchia-v1-protocol.md#epoch-schedule), in multiples of $`\lfloor k/f \rfloor`$ |
| `security_param` | `UINT32` | $`k`$ of [Constants](cryptarchia-v1-protocol.md#constants) |
| `slot_activation_coeff` | ratio | $`f`$ of [Constants](cryptarchia-v1-protocol.md#constants) |
| `learning_rate` | ratio | `beta` of [Parameters and variables](cryptarchia-total-stake-inference.md#parameters-and-variables) |
| `uncle_reference_window_in_block` | `UINT32` | $`W`$ of [Constants](cryptarchia-v1-protocol.md#constants) |
| `service_params` | A `UINT32` count, then for each service in ascending order of its `ServiceType` byte: that byte, `inactivity_period` as a `UINT32` and `epoch` as a `UINT32` | [Service Parameters](bedrock-service-declaration-protocol.md#service-parameters) |
| `min_stake` | `stake_threshold` as a `UINT64`, then `epoch` as a `UINT32` | [Minimum Stake](bedrock-service-declaration-protocol.md#minimum-stake) |
| `base_difficulty` | `UINT32` | $`n`$ in `BLEND_DIFFICULTY_BASE` $`= \lfloor p / 2^n \rfloor`$ of [Parameters](proof-of-work.md#parameters) |
| `target_transactions_per_block` | `UINT64` | `TARGET_TXS_PER_BLOCK` of [Parameters](proof-of-work.md#parameters) |
| `max_step` | `UINT64` | `BLEND_MAX_STEP` of [Parameters](proof-of-work.md#parameters) |
| `damping_num` | `UINT32` | `BLEND_DAMPING_NUM` of [Parameters](proof-of-work.md#parameters) |
| `damping_den_offset` | `UINT32` | `BLEND_DAMPING_DEN` minus `BLEND_DAMPING_NUM` of [Parameters](proof-of-work.md#parameters) |
| `minimum_difficulty` | `UINT32` | $`n`$ in `REWARD_TARGET_CAP` $`= \lfloor p / 2^n \rfloor`$ of [Parameters](proof-of-work.md#parameters) |
| `ema_smoothing_factor` | `UINT64` | `EMA_SMOOTHING_FACTOR` of [Parameters](proof-of-work.md#parameters) |
| `ema_smoothing_precision` | `UINT64` | `EMA_SMOOTHING_PRECISION` of [Parameters](proof-of-work.md#parameters) |
| `target_claims_per_block` | `UINT64` | `TARGET_CLAIMS_PER_BLOCK` of [Parameters](proof-of-work.md#parameters) |
| `rate_num` | `UINT64` | `EPOCH_POW_DISTRIBUTION_RATE_NUM` of [Parameters](proof-of-work.md#parameters) |
| `rate_den` | `UINT64` | `EPOCH_POW_DISTRIBUTION_RATE_DEN` of [Parameters](proof-of-work.md#parameters) |
| `pow_share` | `UINT64` | `POW_SHARE` of [Parameters](proof-of-work.md#parameters) |
| `share_den` | `UINT64` | `SHARE_DEN` of [Parameters](proof-of-work.md#parameters) |
| `expected_blocks_per_window` | `UINT64` | `EXPECTED_BLOCKS_PER_WINDOW` of [Parameters](proof-of-work.md#parameters) |
| `slot_duration` | duration | The slot length of [Constants](cryptarchia-v1-protocol.md#constants) |

The `stake_thresholds` ([Minimum Stake](bedrock-service-declaration-protocol.md#minimum-stake)) and `parameters` ([Service Parameters](bedrock-service-declaration-protocol.md#service-parameters)) stores hold the `min_stake` and `service_params` entries of the records of the schedule.

A software release that adds, removes or re-encodes a field defines a new layout version, used by the eras that adopt it.

## Interpreting Chain Data

A block or proposal, and everything it carries, is parsed, validated and executed under the rules of $`\textbf{era}(sl)`$ of its slot, except that a transaction is parsed under the era whose fork digest it carries. `slot` is the first field of the header ([Block Header](cryptarchia-v1-protocol.md#block-header)) and has the same encoding in every era, and every message that carries a block or proposal begins with the header in its [canonical encoding](bedrock-v1.1-block-construction.md#canonical-encoding). Otherwise a node cannot parse a block before it knows the block's era.

Every transaction begins with the fork digest of the era in force when it was signed ([Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction)), in the same encoding in every era. Otherwise a node cannot parse a transaction before it knows the transaction's era. A block of era $`m`$ accepts a transaction that carries $`F_m`$, or $`F_{m-1}`$ while the block's slot lies in epoch $`E_m`$.

[Fork choice](fork-choice.md) compares two chains under the era of the slot of their $`\textbf{common\_ancestor}`$ ([Fork Pruning](cryptarchia-v1-protocol.md#fork-pruning)). The fork choice rule of an era reads only the block tree and the slot of each block. Otherwise it is undefined on the blocks of a later era that re-encodes a field it reads. [Commit](cryptarchia-v1-protocol.md#commit) uses the $`k`$ of the era of the slot of the local chain tip.

At startup and on checkpoint import, a node whose software does not implement the rules of every era from $`\textbf{era}(sl_{B_\text{imm}})`$ to the era in force must halt. A halted node stops every protocol and exits with an error to the operator.

A node keeps in its mempool only transactions valid under the era in force.


## Era Migration

Every era after the first defines a migration from its predecessor. A migration is a function of the recorded chain state alone. The recorded chain state is the state a Mantle Operation is validated against ([Validation](bedrock-v1.1-mantle-specification.md#validation), [Proof of Work Operations](bedrock-v1.1-mantle-specification.md#proof-of-work-operations)) and the [snapshots](bedrock-service-declaration-protocol.md#snapshots) of the current and later epochs.

The migration must be:

- **Total**: defined for every state reachable under the predecessor era. A migration undefined for a reachable state halts the network at the boundary.
- **Identity by default**: every state component the new era does not redefine is unchanged.

A block reads the state after any block of an earlier era with the intervening migrations applied, in order. When the era in force changes, a node applies the same migrations to the state after its local chain tip; it re-validates its mempool and runs the network protocols of the new era against that state.

A value derived for an epoch is derived under the rules of the epoch's era: its [Epoch State](cryptarchia-v1-protocol.md#epoch-state), its `difficulty_blend` ([Blend Difficulty](proof-of-work.md#blend-difficulty)) and its `epoch_pow_reward` ([Reward Pool](proof-of-work.md#reward-pool)). A quantity measured over an epoch, such as a phase boundary, an observation window or an expected block count, uses the parameters of that epoch's era. Where a derivation reads the chain state as of a slot, it reads the state after the last block at or before that slot, migrated to the epoch's era. A value derived for an earlier epoch is used as it was derived.

The rules of an era verify the Activity Proofs and reward claims of the last epoch of the predecessor era, [CLAIM_POW_REWARD](bedrock-v1.1-mantle-specification.md#claim_pow_reward) included, as the predecessor's rules do. Otherwise the rewards of that epoch are lost.


## Era Transition Period

The Era Transition Period is the first $`T`$ [rounds](blend-protocol.md#time) after the era in force changes. It applies to the network layer only. $`T`$ must exceed the clock difference between any two honest nodes. Otherwise those nodes share no round in which both run one era's protocols.

During the Era Transition Period a node must:

1. Accept and open connections on the identifiers of both eras.
2. Validate a Blend message under the era of the connection it arrived on.
3. Keep every input the predecessor era's message checks read until the period ends.

After the Era Transition Period the node must drop the identifiers of the predecessor era and must not process its Blend messages. A synchronization stream open at the end of the period is served to its end.

## Network Protocol Identity

Every protocol identifier and gossipsub topic a Logos Blockchain specification defines is `/logos-blockchain/<chain_id>/<protocol>` for Kademlia and identify ([P2P Network](../draft/p2p-network.md)), and `/logos-blockchain/<fork_digest>/<protocol>` for every other protocol. `<chain_id>` is `chain_id` ([Cryptarchia Parameters](bedrock-genesis-block.md#cryptarchia-parameters)), percent-encoded as in [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986#section-2.1) except for its unreserved characters. `<fork_digest>` is the fork digest $`F_n`$ of an era $`n`$ in lowercase hexadecimal, and the identifier is an identifier of era $`n`$. `<protocol>` is the identifier the protocol's own specification defines.

A node sends a message it generates over the identifiers of the era in force at generation. A node relays or releases a received or processed Blend message, and broadcasts its payload, over the identifiers of the era of the connection it arrived on. A node publishes a proposal it accepts, and a transaction it admits to its mempool, on the topic of the era in force. A [synchronization](cryptarchia-v1-bootstr-sync.md#downloading-blocks) response carries blocks of any era.


## Horizon

$`H`$ must not be smaller than the last entry of the schedule. Otherwise the node warns its operator before its last era begins.

When $`\textbf{wallclock\_time}().\textbf{to\_slot}()`$ reaches the first slot of epoch $`H+1`$, a node warns its operator that its software no longer interprets the chain. A node also warns its operator when a peer of its chain advertises an identifier whose fork digest the node does not know.
