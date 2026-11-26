# [RFC] Mantle: Native and rollup channels

**Motivation and proposal:** [PR #553](https://github.com/logos-co/logos-lips/pull/553)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-25 |
| v2 | A channel state holds its kind, its note set and, for a rollup channel, its rollup state, and the null channel has a note set and is rejected by every channel Operation outside Genesis. The next configuration of a step is optional, the effects of a step are hashed with BLAKE2b, the rollup state and its `Groth16VerificationKey`, which stores the pairing `alpha_beta`, have a section of their own in Mantle Rollups, and each element is described by what it is | 2026-11-26 |
| v3 | The Discussion gives the reason for the note set index `2` of the null channel and defines `PK0` and `NF_SK0` before their first use, and leaves the names of the two kinds out | 2026-11-26 |

## Reviewer Orientation

Read [Mantle Rollups](../bedrock-mantle-rollups.md) first, from `# Overview` to the end: it is new, and every other change serves it or follows the note of four fields. The PR sits on [PR #552](https://github.com/logos-co/logos-lips/pull/552), which places the channel Operations in Mantle Channels, and on [PR #480](https://github.com/logos-co/logos-lips/pull/480), the private note ledger.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle Rollups](#mantle-rollups), `ROLLUP_PROVE` | value conserved by every step; no note spent twice within a step or across steps; the live root; the five public inputs of the STF proof and what `effects_hash` covers |
| 2 | Critical | **Start here**: [Mantle](#mantle), Notes and Keys | the commitment over four fields; `nf_sk` between the spending secret key and the public key; `PK0` and `NF_SK0`; a staking key `0` never leads |
| 3 | Critical | [Proof of Leadership](#proof-of-leadership) and [Proof of Quota](#proof-of-quota) | the witness takes `nf_sk` and `staking_sk`, never `spending_sk`; ticket and entropy from `staking_sk` |
| 4 | High | [Mantle Rollups](#mantle-rollups), `ROLLUP_CREATE`, `ROLLUP_INSCRIBE`, `ROLLUP_DEPOSIT` | the kind checks; the FIFO of unproven inscriptions with their slots; pending deposits under their `op_id` |
| 5 | High | [Mantle Channels](#mantle-channels) | the channel kind; creation by `CHANNEL_CONFIG` only; the null channel before Genesis; `Step` and `STEP_V1` |
| 6 | High | [Mantle Transaction Encoding](#mantle-transaction-encoding) | the rollup payloads; compressed points with a single encoding; `Step` without a kind byte; `NoteStakePk` |
| 7 | High | [Bedrock Genesis Block](#bedrock-genesis-block) and [Block Construction](#block-construction-validation-and-execution) | initial notes and declarations with a staking key; the null channel; the batch of ZkTransfers and the STF proofs |
| 8 | Medium | [SDP](#service-declaration-protocol), [Service Reward Distribution](#service-reward-distribution-protocol), [Proof of Work](#proof-of-work), [Common Cryptographic Components](#common-cryptographic-components), [Wallet](#wallet-technical-standard) | `note_stake_pk`; the keys of reward notes; the compression mode of `NF_KDF_V1`; the Staking Keys recommendations |
| 9 | Low | [Cryptarchia Protocol](#cryptarchia-protocol), [Message Encapsulation](#message-encapsulation), [Chores](#chores) | skim: vectors and wording |

# Discussion

## Two kinds of channel in one map

A channel is a native channel or a rollup channel. Both live in one `channels` map and one id space, and `ChannelState` holds the sequencing fields every channel shares next to its `kind`, `NATIVE` or `ROLLUP`, fixed at creation, the index of its `note_set`, and `rollup`, a `RollupState` for a rollup channel and `None` for a native channel. The round-robin and the parent and signer checks of an inscription are the same for both kinds, and every channel has a note set, so the Operations of both kinds read it the same way.

Three alternatives lost:

- **A separate rollup structure, with its own map and Operations.** It gives fully independent documents, but duplicates the sequencing rules and opens two id spaces to keep apart.
- **The rollup fields directly on every channel.** It needs no new type, but every native channel carries fields it never uses.
- **One type per kind, each holding the fields of its kind.** Each kind holds only its own fields, but the note set, which every channel has, sits in both types, and every check tests a type where an enum comparison reads plainly.

Each kind has its own Operations: `CHANNEL_CONFIG`, `CHANNEL_INSCRIBE`, `CHANNEL_DEPOSIT` and `CHANNEL_WITHDRAW` for native channels, and `ROLLUP_CREATE`, `ROLLUP_INSCRIBE`, `ROLLUP_DEPOSIT` and `ROLLUP_PROVE`, at opcodes `0x40` to `0x43`, for rollup channels. Each Operation asserts the kind it expects. Shared Operations that branch on the kind would give one payload two meanings, and some of them would be invalid for one kind, such as a withdrawal from a rollup. One Operation per kind keeps each payload and each validation for one kind. The range `0x44` to `0x4F` is reserved for later rollup Operations.

## Creation by configuration, and the null channel before Genesis

A native channel is created only by its first `CHANNEL_CONFIG`, whose `parent` is `ZERO`, and a rollup channel only by `ROLLUP_CREATE`. No inscription creates a channel. An inscription that created its channel could not say which kind it creates, and the channel would start with its first signer as its only accredited key. With creation by configuration, every channel starts with the kind, committee and parameters its creator chose, and every inscription lands on a channel whose kind is known.

The null channel is a native channel that exists before Genesis, with the null key as its only accredited key, `ZERO` as its `tip_hash` and the note set of index `2`, empty before Genesis. Index `2` is the first one after the ledger note set `LEDGER_SET = 0` and the SDP note set `SDP_SET = 1` ([Note sets](../bedrock-mantle.md#ledger)), and the null channel is the first channel. The Cryptarchia inscription of the Genesis block extends it as any inscription extends its channel. So `CHANNEL_INSCRIBE` needs no branch that creates a channel, and the Genesis block needs no configuration to create the null channel. The null channel has a note set like every channel. Every channel Operation, native or rollup, rejects it, since its inscriptions are those of the Genesis block, and the Genesis block exempts its two inscriptions from that check.

## Notes with a staking key and a nullifier key, without program or data

A note has four fields: `value`, `nonce`, `public_key` and `stake_public_key`. The holder keeps three secrets: `spending_sk` derives `nf_sk` under `NF_KDF_V1`, `nf_sk` derives `public_key`, and `staking_sk` derives `stake_public_key`. The nullifier hashes `nf_sk`. A note has no program and no data field ([Programs governing notes](#programs-governing-notes)). `PK0` and `NF_SK0` are the public key and the nullifier key of the spending secret key `0`, which everyone knows.

- The staking key separates who leads with a note from who spends it. A wallet stakes with a hot key and keeps its spending key cold, and a rollup can hold its notes by `PK0` while giving them the staking keys of their users.
- The nullifier key lets the Proof of Leadership prove the nullifier of the note unspent without the spending secret key. A node given `nf_sk` and `staking_sk` leads with a note it cannot spend.

No secret key is known whose public key is `0`, so a note whose staking key is `0` never leads. Since anyone can derive the keys of `PK0`, `PK0` is never a staking key.

## FIFO proving, open to anyone

Sequencers post the data of their state transitions with `ROLLUP_INSCRIBE`. Anyone posts the step of an inscription with `ROLLUP_PROVE`, and only for the oldest unproven one. Every input of a step is known once its inscription is in a block, so provers compute the steps of consecutive inscriptions in parallel off chain, and post them in order. The mempool orders the steps by their inscriptions, and consecutive steps can share a block.

The alternatives weighed:

- **The sequencer proves its own inscription.** This ties the proposer to the prover: a sequencer must finish a proof before it posts, and a rollup whose proofs take longer than a turn cannot run.
- **Steps accepted out of order and held until the earlier ones are proven.** Nodes would keep proofs waiting to be applied, which anyone can fill with proofs that never apply.
- **An accredited set of provers.** The liveness of the rollup would depend on that set.

With FIFO proving, a node never holds a proof it has not applied, and posting a step applies it.

## The live root

The transfers of a step are verified against the live commitment MMR root of the rollup note set, extended by the deposit note and by the outputs of the earlier transfers of the step. Ledger Operations name a root of one of the last `ROOT_WINDOW` blocks. With such a root, the step of inscription `k + 1` could only spend what the step of `k` creates once a block holds the step of `k`. Only `ROLLUP_PROVE` appends to a rollup note set, and in the order of the inscriptions, so a prover knows the live root in advance. Consecutive steps then share a block, and even a Mantle Transaction, and a step can name no stale or forged root. A step never reads or writes the buffer of the rollup note set.

## Transfers of a step are ZkTransfers

Each transfer of a step is a ZkTransfer, the circuit every other spend uses, with an `excess_value` of `0`. Whatever the STF, the ledger checks that a step keeps the value of the notes it moves and spends no note twice. A faulty STF can give the funds of its rollup to the wrong users, but never creates value, so the notes of a rollup take part in Proof of Stake as safely as ledger notes. The ZkTransfers of a step join the batch of the ZkTransfers of the block.

A rollup holds its notes by `PK0`, the public key of the spending secret key `0`, so that any prover can spend them. The ledger recommends this and does not enforce it, apart from the deposit note, which it creates under `PK0`.

The alternative is a dedicated spend circuit for rollup notes, which would check the balance and the fields of the rollup notes. It needs a circuit, a trusted setup and a verification path of its own, and gives no guarantee a ZkTransfer does not. A ZkTransfer spends at most 4 notes and creates at most 8, so a step lists as many transfers as it needs, and pays the Execution Gas of each.

## One STF proof with five public inputs

Each step carries one Groth16 proof of the STF of the rollup, under its current key, with five public inputs:

```python
[state_root,       # the state root of the rollup
 next_state_root,  # its next state root
 op_id_k,          # the op_id of the inscription k the step proves
 slot_k,           # the slot of the block that included inscription k
 effects_hash]     # the hash of the effects of the step
```

A fixed number of public inputs fixes the size of every verification key at 6 `IC` points, so the ledger stores and verifies the key of every rollup the same way. The pairing $`e(\alpha, \beta)`$ depends on the key alone and is the costliest part of a verification, so the ledger computes it once, when it stores the key, as its `alpha_beta`. `effects_hash` packs the effects of a step, of any size, into one field element: the value and intent of each minted deposit, the inputs, outputs and payouts of each transfer, and the next configuration.

`slot_k` lets a rollup depend on time. It is the slot of the block that included the inscription, recorded with its `op_id` in the FIFO, and so known to every prover as soon as the inscription lands. The slot of the block that includes the step is known to no prover in advance, which would rule out parallel proving.

The proofs of a step are bound to `op_id_k`, the third public input of the STF proof and the `msg` of every ZkTransfer, not to the `mantle_txhash`. So anyone posts the step.

## Deposits wait until the sequencers mint them

`ROLLUP_DEPOSIT` consumes ledger notes and records a pending deposit, its value and intent, under its `op_id`. A deposit waits until a step mints it, and the sequencers of the rollup choose which deposits a step mints through the data they inscribe. The ledger never refunds a deposit.

A rule over deposits can give at most two of three properties: no stall of the rollup, no censorship of a deposit, and no harm from spam. The rules weighed:

| Rule | What fails |
| --- | --- |
| Forced inclusion: an inscription is invalid while it leaves deposits pending | the circuit handles a fixed number of deposits per step, so a flood of deposits blocks the rollup for good |
| A queue that refuses deposits once full | spam crowds out real deposits |
| An inscription takes the oldest deposits first | spam delays real deposits |
| The sequencer takes `min(max_deposits, queued)`, each deposit at least `min_deposit` | two ledger parameters per rollup, a count the ledger checks, and a sequencer willing to pay can delay a deposit |

With no rule, a deposit never stalls the rollup. A sequencer that ignores a deposit delays it until a sequencer of the rotation mints it, and the STF decides what a deposit means and when the rollup takes it in. If every sequencer ignores a deposit, its value stays pending: users trust the sequencers of a rollup with their deposits as they trust its STF with their notes.

A refund by the ledger after a delay would race the step that mints the deposit. That step lists the deposit, and its STF proof covers its value, so a refund that lands first invalidates a proven step, and every later inscription waits for a new proof of it. A refund made by the STF is a payout, and every payout costs the prover of the step a ZkTransfer output, so crediting each minted deposit in the state of the rollup is the recommended practice.

## Sequencers can only delay

A step carries the next accredited keys and rotation parameters of the rollup when its STF changes them, and its STF proof covers them through `effects_hash`, so the rules of the STF decide who sequences the rollup. A native channel reconfigures with a threshold of signatures of its accredited keys. For a rollup, that threshold could replace the other sequencers and censor without limit, so the configuration of a rollup changes only through its steps.

The round-robin hands the turn to the next accredited key when the timeframe or the timeout of a sequencer elapses. A sequencer that refuses an inscription therefore only delays it until a sequencer that accepts it takes its turn, provided the configuration sets a `posting_timeframe`. A `posting_timeout` alone replaces only a sequencer that inscribes nothing, so a sequencer that inscribes other data holds its turn. A rollup that wants censorship to cost only a delay sets a timeframe.

A change of configuration applies from the block of its step, not of its inscription. The inscriptions after `k` that land before that step are signed under the current keys, and a sequencer the step removes stays accredited until the step is proven.

## An optional configuration in each step

A step carries `next_config`, a `RollupConfig` holding the next accredited keys, rotation parameters and optional verification key, or `None`, which keeps the configuration. Most steps keep it, so their payload carries one byte for it. A step that carries a configuration applies it and restarts the round-robin, as `CHANNEL_CONFIG` does, which sets the turn to `keys[0]`. A step with no configuration leaves the rotation as it stands: restarting on every step would hand the turn back to `keys[0]` at each step, and with steps landing within a timeframe, `keys[0]` would hold the turn for good.

## A BLAKE2b effects hash

`effects_hash` is a BLAKE2b-256 hash, under `ROLLUP_EFFECTS_V1`, of the encoding of the minted deposits, the transfers and `next_config`, reduced modulo $`p`$ as `op_id` is, since it is a public input of the STF proof. Most STF circuits are wrapped zkVMs, for which BLAKE2b is the natural hash.

The alternative is a `zkhash` of the effects, which a hand-written circuit recomputes cheaply. The configuration holds Ed25519 keys and BN254 points of 32 and 64 bytes, which a `zkhash` would have to split into field elements in a packing of its own.

## The STF reads its inscription through its op_id

The ledger does not read the data of a rollup inscription. A rollup that applies that data should have its STF circuit recompute `op_id_k` from the encoded `RollupInscribe` it applies, so that its proof covers exactly the data, parent and signer its sequencer inscribed. Without it, a prover could apply data no sequencer inscribed, and the sequencers would lose their role.

The cost is BLAKE2b inside the circuit, over up to `MAX_OPERATION_DATA_SIZE`, 1,835,008 bytes, of data. BLAKE2b takes about 100 times the constraints of Poseidon2 ([Common Cryptographic Components](../common-cryptographic-components.md)), and the cost grows with the size of the inscription, which the rollup chooses.

The alternative weighed is a `zkhash` commitment to the inscription, as a sixth public input. A circuit opens it cheaply, but every node would compute Poseidon2 over up to 1,835,008 bytes for each inscription, and the key of every rollup would grow by one point. `op_id` exists for every Operation and costs nodes nothing more, so the cost of binding the data falls on the provers of the rollups that need it.

## Deposits of zero value

A `ROLLUP_DEPOSIT` with a `value` of `0` is valid. It leaves a pending deposit that the STF may never mint, and that entry stays in the state of the rollup. The depositor pays its gas, and its ZkTransfer consumes at least one ledger note, so a spammer pays for every entry it adds. A minimum deposit value would add a ledger parameter per rollup and leave spam at that minimum. The spam is accepted.

## Programs governing notes

[PR #481](https://github.com/logos-co/logos-lips/pull/481) adds programs that govern notes inside native channels: notes with `program` and `data` fields, `PROGRAM_REGISTER`, program deposits and program steps proven with a ZkProgramSpend, and the openings of the program notes. In those steps, the sequencer that inscribes a step also proves it.

This PR takes the staking key and the nullifier key from PR #481, and none of its programs. A rollup channel gives a zone the same power with the proposer separated from the prover:

- The STF of a rollup governs every note of the rollup, so a field naming a program and a field of program data in every note would repeat what the state of the rollup holds.
- A ZkTransfer with an `excess_value` of `0` gives the balance and Proof of Stake guarantees the ZkProgramSpend gives, with no circuit of its own.
- The note commitment hashes four fields, and the ZkTransfer, the Proof of Leadership and the leader branch of the Proof of Quota open no program fields.
- Native channels hold user notes, which their holders move with steps, and a mini-block holds one kind of step.

## Compatibility

A node that follows this PR and one that follows its base disagree on every note commitment and nullifier, on the encoding of a `ChannelInscribe` with steps and of an `SDPDeclare`, and on the opcodes `0x40` to `0x43`. The ZkTransfer, Proof of Leadership and Proof of Quota circuits change, so each takes a new trusted setup and new proving and verification keys.

# Details

## Mantle Rollups

Version 1.0.0, a new document, published as `bedrock-mantle-rollups.md`. It specifies the rollup channels and their four Operations, each with the sections Payload, Proof, Execution Gas, Validation and Execution. Its Overview, between the Introduction and the Operations as in Mantle and Mantle Channels, describes rollup channels and states what the ledger checks, why the sequencers can only delay, what it recommends to a rollup that wants any prover to prove it, and what it does not guarantee. The state of a rollup and the verification key of its STF have a section of their own, before the Operations.

The state of a rollup is the `rollup` field of its `ChannelState`, whose `kind` is `ROLLUP`, and its key a `Groth16VerificationKey`, the points of a Groth16 verification key with `alpha_beta`, their pairing $`e(\alpha, \beta)`$, computed when the key is stored:

```python
class RollupState:
    key: Groth16VerificationKey           # the verification key of the STF proofs
    state_root: zkhash                    # the state root after the last proven inscription
    deposits: dict[Hash, PendingDeposit]  # the deposits waiting to be minted, by their op_id
    unproven: list[(Hash, Slot)]          # the op_id and block slot of each unproven inscription
```

- **`ROLLUP_CREATE`** (`0x40`) creates a rollup channel under a `ChannelId` no channel holds, with its accredited keys, rotation parameters, Groth16 verification key and initial state root. Every point of the key is checked on its curve, in its prime-order subgroup and not at infinity. Its proof is empty.
- **`ROLLUP_INSCRIBE`** (`0x41`) writes the data of a state transition. The sequencer the round-robin designates signs it, it extends the tip of the channel, and its `op_id` and block slot join `unproven`.
- **`ROLLUP_DEPOSIT`** (`0x42`) consumes ledger notes with a ZkTransfer with no outputs, whose excess is `value + excess_value`, and records a `PendingDeposit(value, intent)` under its `op_id`. Its `excess_value` pays fees. Its `inscription` publishes data for the zone, which the ledger does not keep.
- **`ROLLUP_PROVE`** (`0x43`) applies the oldest unproven inscription `k`. It mints the deposits it lists into one deposit note, `Note(total, derive_note_nonce(op_id_k, 0, total, PK0), PK0, 0)`, applies its transfers to the rollup note set and creates their payouts in the ledger note set, and sets the next state root and, when the step carries a `next_config`, the next accredited keys, rotation parameters and, optionally, verification key. Its proof is a `RollupProveOpProof`: one ZkTransfer per transfer, then the STF proof. The round-robin restarts only when the step carries a configuration.

`ROLLUP_CREATE` asserts that the channel does not exist, the other three that it is not the null channel and that its kind is `ROLLUP`, and only `ROLLUP_PROVE` spends from or adds to a rollup note set. The Execution Gas of `ROLLUP_CREATE` is `EXECUTION_ROLLUP_KEY_GAS`; that of `ROLLUP_PROVE` is `EXECUTION_TRANSFER_GAS * len(transfers) + EXECUTION_ROLLUP_PROOF_GAS`, plus `EXECUTION_ROLLUP_KEY_GAS` with a next key. `ROLLUP_INSCRIBE` and `ROLLUP_DEPOSIT` cost what `CHANNEL_INSCRIBE` and `CHANNEL_DEPOSIT` cost.

## Mantle

Version 2.1.0.

- **Notes.** A note carries `stake_public_key`, and the commitment hashes it:

  ```diff
   class Note:
       value: TokenValue
       nonce: NoteNonce
       public_key: ZkPublicKey        # the holder, whose nullifier key derives the nullifier
  +    stake_public_key: ZkPublicKey  # the staking key, whose secret the Proof of Leadership takes
  ```

- **Keys.** A new `### Keys` section derives `nf_sk = zkhash(NF_KDF_V1, spending_sk)` and `public_key = zkhash(KDF, nf_sk)`, defines `PK0` and `NF_SK0`, and states that spending takes `spending_sk` alone and leading takes `nf_sk` and `staking_sk`. `derive_note_nullifier` hashes `nf_sk`.
- **ZkTransfer.** The witness holds the spending secret key and the staking key of each input and output. The circuit derives `nf_sk` and the public key from the spending secret key, and every commitment over four fields. It does not prove the staking key of an input.
- **Opcodes.** `ROLLUP_CREATE` to `ROLLUP_PROVE` at `0x40` to `0x43`, linked to Mantle Rollups, with `0x44` to `0x4F` reserved.
- **Transaction and ledger.** The `excess_value` of `ROLLUP_DEPOSIT` pays fees. The proofs of `ROLLUP_PROVE` are bound to the `op_id` of the inscription they prove and verified against the live MMR of the rollup note set. The Ledger table gives every channel, native or rollup, the null channel first, a note set from index `2` on, in creation order. The deposit note of a step derives its nonce from the `op_id` of the inscription the step proves.
- **Test vectors.** They cover the rollup Operations and follow the encoding of `ChannelInscribe` and `SDPDeclare`. The verification key of `ROLLUP_CREATE` holds real points.

## Mantle Channels

Version 1.1.0.

- `ChannelState` gains `kind: ChannelKind`, `NATIVE` or `ROLLUP`, and `rollup: RollupState | None` next to its `note_set`. `default_channel` takes the kind, the note set and the rollup state.
- A native channel is created only by its first `CHANNEL_CONFIG`, whose `parent` is `ZERO`. `CHANNEL_INSCRIBE` creates no channel. `CHANNEL_CONFIG`, `CHANNEL_INSCRIBE`, `CHANNEL_DEPOSIT` and `CHANNEL_WITHDRAW` assert `chan.kind == NATIVE`.
- The null channel is a native channel that exists before Genesis, with the null key, the note set of index `2` and the fields `default_channel` gives at slot `0`. Its `ChannelId` is `NULL_CHANNEL`, which every channel Operation, native or rollup, rejects.
- `UserStep` becomes `Step`, bound to `step_id`, a BLAKE2b-256 hash under the DST `STEP_V1`.
- The party table splits the roles: the spending secret key moves and withdraws a note, and the nullifier key with the staking secret key leads with it.

## Mantle Transaction Encoding

Version 2.1.0.

- `RollupCreate`, `RollupInscribe`, `RollupDeposit` and `RollupProve` under `### Rollup Operations`, and `RollupProveOpProof` among the proofs. A `RollupProve` ends with its `OptionalConfig`, `%x00` to keep the current configuration, or `%x01` and a `RollupConfig`, whose `OptionalKey` is `%x00` to keep the current key, or `%x01` and a key.
- `Groth16VerificationKey = Alpha Beta Gamma Delta IC`, with `IC` exactly 6 points. Its `alpha_beta` is derived, not encoded.
- `Groth16Proof` replaces the `Groth16` terminal and is made of compressed `G1Point` (32 bytes) and `G2Point` (64 bytes). A decoder rejects the infinity flag and any coordinate not less than $`q`$, so each point has a single encoding. A proof is decompressed only when verified.
- `Step = Inputs Outputs CommitmentRoot Inscription`, with no kind byte.
- `SDPDeclare` carries `NoteStakePk` after `NotePk`.

## Proof of Leadership

Version 1.3.0. The witness holds `nf_sk` and `staking_sk`. The circuit derives the public key from `nf_sk` and the staking key from `staking_sk`, hashes four fields into the commitment, and derives the nullifier from `nf_sk`, and the ticket and entropy contribution from `staking_sk`. The leader reward note has `reward_public_key` as both its public key and its staking key.

```diff
-  ticket = zkhash(LEAD_V1, epoch_nonce, slot, commitment, sk)
+  ticket = zkhash(LEAD_V1, epoch_nonce, slot, commitment, staking_sk)
```

## Proof of Quota

Two versions: 1.4.0 from [#526](#chores), and 1.5.0. In 1.5.0, the leader branch takes `pol_nullifier_key` and `pol_staking_secret_key`, follows the Proof of Leadership over the staking key of the note, and derives the selection randomness of a leader from the staking secret key. The proof is encoded as a `Groth16Proof`.

## Common Cryptographic Components

Version 1.4.0. The nullifier key derivation `zkhash(NF_KDF_V1, spending_sk)` uses the compression mode of Poseidon2, and the note nullifier hashes `nf_sk`.

## Block Construction, Validation and Execution

Version 1.5.0. The leader reward note has `reward_public_key` as both its keys. The ZkTransfers of a `ROLLUP_PROVE` join the batch of the block, and each STF proof is verified alone under the current key of its rollup, since keys differ between rollups and can change with each step. The proof of leadership is a `Groth16Proof`.

## Bedrock Genesis Block

Version 1.4.0. The public key of each initial note is also its staking key, and each initial declaration names `note_stake_pk`. The null channel exists before Genesis with the note set of index `2`, a third empty note set, and the Cryptarchia inscription extends it from its `tip_hash`, `ZERO`. A fourth Genesis Validation Exemption lifts the rejection of the null channel for the two Genesis inscriptions. The null proof of leadership is 128 zero bytes, which encode no point.

## Service Declaration Protocol

Version 1.10.0. `DeclarationMessage` and `DeclarationInfo` carry `note_stake_pk` next to `note_pk`, the keys of the service note and of the rewards of the validator. The `zk_id` is the key the validator proves in the Proof of Quota and holds no funds.

## Service Reward Distribution Protocol

Version 1.5.0. The reward note of a `zk_id` is created under the `note_pk` and `note_stake_pk` of its declaration, its nonce derived over `note_pk`.

## Proof of Work

Version 1.3.0. The note a reward claim creates has the public key of the claim as both its public key and its staking key.

## Wallet Technical Standard

Version 1.3.0. $`k_{\text{logos}}`$ is the spending secret key, which derives `nf_sk` and then the public key. A tracked note carries its staking key, and its nullifier hashes `nf_sk`. A new Staking Keys section recommends `staking_sk = nf_sk` by default, which gives cold staking, and cold keys for a service declaration. Every channel has a note set.

## Cryptarchia Protocol

Version 1.3.2. The transaction Merkle root, body root and block ID test vectors cover the rollup Operations and follow the encoding of `ChannelInscribe` and `SDPDeclare`.

## Message Encapsulation

Version 1.3.0, from [#526](#chores). The Proof of Quota public values hold the first and last slots of the epoch, and `pol_sl` is a slot of the epoch in the core and proof of work cases.

## Chores

- [PR #526](https://github.com/logos-co/logos-lips/pull/526), which binds the slot of the Proof of Quota to its epoch, is carried in with its own revision rows and its RFC document, [RFC-526](RFC-526-blend-bind-the-proof-of-quota-slot-to-its-epoch.md). So Proof of Quota has two rows from this PR, 1.4.0 from #526 and 1.5.0, and Message Encapsulation has the 1.3.0 row of #526.
- RFC-526 names the public inputs `pol_window_first_slot` and `pol_window_last_slot`, as Proof of Quota and Message Encapsulation do, and states once that the window they bound is the epoch.
- `scripts/blockchain_structure.py` maps Mantle Rollups under Mantle in the generated summary, next to Mantle Channels.
- [Gas Cost Determination](../analysis-gas-cost-determination.md), version 1.8.2: the execution of a channel inscription applies its steps to the note set of an existing channel and creates no channel record.
- The 2.0.0 row of Mantle Transaction Encoding, from PR #480, which is not on master, names steps by the name this PR gives them.

# Implementation

- [ ] ZkTransfer circuit: derive `nf_sk` from the spending secret key and the public key from `nf_sk`, and hash the four note fields in every input and output commitment.
- [ ] Proof of Leadership circuit: take `nf_sk` and `staking_sk`, hash the four note fields, derive the ticket and entropy contribution from `staking_sk`, and commit the reward note under `reward_public_key` twice.
- [ ] Proof of Quota circuit, leader branch: take `pol_nullifier_key` and `pol_staking_secret_key`, hash the four note fields, and derive the selection randomness from the staking secret key.
- [ ] Run the trusted setups of the three circuits and publish their keys.
- [ ] Re-run the ZkTransfer, Proof of Leadership and Proof of Quota proving benchmarks on the new circuits, and update their results.
- [ ] Measure `EXECUTION_ROLLUP_KEY_GAS` and `EXECUTION_ROLLUP_PROOF_GAS`, the key checks with the pairing $`e(\alpha, \beta)`$, and the verification of an STF proof with five public inputs, and add their values to the Gas Determination table of Mantle in a later PR.
- [ ] Node, notes and keys: `stake_public_key` in notes, `nf_sk` and `NF_KDF_V1`, nullifiers over `nf_sk`, `PK0` and `NF_SK0`, `note_stake_pk` in SDP declarations and reward notes, and wallet key derivation.
- [ ] Node, native channels: the channel kind, creation by `CHANNEL_CONFIG` only, the null channel before Genesis with the note set of index `2`, rejected by every channel Operation outside Genesis, the kind checks, and `Step` under `STEP_V1` with no kind byte.
- [ ] Node, rollup channels: `ROLLUP_CREATE`, `ROLLUP_INSCRIBE`, `ROLLUP_DEPOSIT` and `ROLLUP_PROVE`, the rollup state, the live root, and the STF verification.
- [ ] Node, encoding and blocks: compressed `G1Point` and `G2Point` with a single encoding, the rollup payloads, the ZkTransfers of `ROLLUP_PROVE` in the batch of the block, and each STF proof verified alone.
- [ ] Reproduce the test vectors of Mantle and of the Cryptarchia Protocol, and add a focused test for each rollup Operation.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle Rollups](../bedrock-mantle-rollups.md) | Created | 1.0.0 |
| [Mantle](../bedrock-mantle.md) | Modified | 2.1.0 |
| [Mantle Channels](../bedrock-mantle-channels.md) | Modified | 1.1.0 |
| [Mantle Transaction Encoding](../bedrock-mantle-encoding.md) | Modified | 2.1.0 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.3.0 |
| [Proof of Quota](../proof-of-quota.md) | Modified | 1.4.0 (#526) and 1.5.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | 1.4.0 |
| [Block Construction, Validation and Execution](../bedrock-block-construction.md) | Modified | 1.5.0 |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | 1.4.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | 1.10.0 |
| [Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md) | Modified | 1.5.0 |
| [Proof of Work](../proof-of-work.md) | Modified | 1.3.0 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | 1.3.0 |
| [Cryptarchia Protocol](../cryptarchia-protocol.md) | Modified | 1.3.2, test vectors only |
| [Message Encapsulation](../message-encapsulation.md) | Modified | 1.3.0 (#526) |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 1.8.2, wording only |
