# MANTLE-ROLLUPS

| Field | Value |
| --- | --- |
| Name | Mantle Rollups |
| Slug | 247 |
| Status | raw |
| Category | Informational |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors | David Rusu <davidrusu@logos.co>, Filip Dimitrijevic <filip@logos.co>, Marcin Pawlowski <marcin@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-11-25 |

# Introduction

Rollup channels let a Zone compute its state off chain and settle it on chain with validity proofs of its state transitions. This document specifies the rollup Operations; the Mantle Transaction that carries them and the ledger they act on are specified in [Mantle](bedrock-mantle.md), and the sequencing they share with native channels in [Mantle Channels](bedrock-mantle-channels.md).

# Overview

## Rollup Channels

A [rollup channel](#rollup-operations) is a [channel](bedrock-mantle-channels.md#channel-operations) whose [state](#rollup-state) follows a [state transition function (STF)](#stf-verification-key), a [Groth16](common-cryptographic-components.md#groth16-zk-snark) circuit its [creator](#rollup_create) chooses. Its [sequencers](bedrock-mantle-channels.md#decentralized-sequencing) take turns, following the [round-robin](bedrock-mantle-channels.md#decentralized-sequencing) of every channel, to post the data of its state transitions with [`ROLLUP_INSCRIBE`](#rollup_inscribe). Anyone then proves these inscriptions with [`ROLLUP_PROVE`](#rollup_prove), one at a time and in the order they were inscribed. Each proof is a step of the rollup, the application of one inscription by `ROLLUP_PROVE`: a proof of its STF takes the rollup from its state root to the next one, and the step mints pending [deposits](#rollup_deposit), moves the [notes](bedrock-mantle.md#notes) of the rollup and pays some of them out to the [ledger](bedrock-mantle.md#ledger). The steps of the proven prefix of the inscriptions give the state of the rollup, and the inscriptions after it wait for their steps. A step reads the [slot](cryptarchia-protocol.md#slot) of the block that included its inscription, so a rollup can depend on time while every prover knows the inputs of a step as soon as its inscription is in a block.

## What the Ledger Checks

The [notes](bedrock-mantle.md#notes) of a rollup live in a note set of their own, which only [`ROLLUP_PROVE`](#rollup_prove) spends ([Ledger](bedrock-mantle.md#ledger)). Each transfer of a step is a [ZkTransfer](bedrock-mantle.md#zero-knowledge-transfer-proof-zktransfer) with an `excess_value` of `0`, so whatever the [STF](#stf-verification-key), the ledger checks that a step keeps the value of the notes it moves and spends no note twice. A faulty STF can give the funds of its rollup to the wrong users but never create value, so the notes of a rollup take part in [Proof of Stake](cryptarchia-proof-of-leadership.md#eligible-sets) as safely as ledger notes. A rollup whose funds take part in Proof of Stake should give the notes its transfers create the staking keys of their users, and never `PK0` as their staking key ([Keys](bedrock-mantle.md#keys)), since the deposit note of a step has staking key `0`. The STF proof decides who gets what: which deposits a step mints, and which notes its transfers consume, create and pay out.

## Sequencers Can Only Delay

A [step](#rollup_prove) sets the next [accredited keys](bedrock-mantle-channels.md#message-ordering) and [rotation parameters](bedrock-mantle-channels.md#decentralized-sequencing) of its [rollup channel](#rollup-operations) when it carries them, and its STF proof covers them, so the rules of the STF decide who sequences the rollup. The [round-robin](bedrock-mantle-channels.md#decentralized-sequencing) hands the turn to the next accredited key when the timeframe or the timeout of a [sequencer](bedrock-mantle-channels.md#decentralized-sequencing) elapses, so a sequencer that refuses to [inscribe](#rollup_inscribe) a transition only delays it until a sequencer that accepts it takes its turn, provided the configuration of the rollup sets a timeframe; a timeout alone replaces only a sequencer that inscribes nothing. Anyone posts the steps, so no party can hold back the proof of an inscription, and a step applies exactly the data its sequencer inscribed when the STF circuit recomputes the [`op_id`](bedrock-mantle.md#note-commitment-and-nullifier) of that inscription, as [STF Verification Key](#stf-verification-key) recommends.

## Recommendations

The [ledger](bedrock-mantle.md#ledger) leaves the following choices to the rollup, and they are recommended to a rollup that wants any prover to be able to prove it:

- Hold the [notes](bedrock-mantle.md#notes) of the rollup by `PK0` ([Keys](bedrock-mantle.md#keys)), the public key whose secret key everyone knows, so that no [step](#rollup_prove) depends on a key one party holds.
- Make a step depend only on its [inscription](#rollup_inscribe), which the STF circuit reads through its [`op_id`](bedrock-mantle.md#note-commitment-and-nullifier) ([STF Verification Key](#stf-verification-key)), and on the [state](#rollup-state) before it, so that every prover computes the same step from public data.
- Credit every minted [deposit](#rollup_deposit) in the state of the rollup as its intent asks, since the ledger merges the deposits a step mints into one note and leaves their accounting to the STF.
- Pay the provers inside the rollup, since the ledger pays nothing for a step and its prover pays the [fees](bedrock-mantle.md#mantle-transaction-fee) of its [Mantle Transaction](bedrock-mantle.md#mantle-transaction).
- Publish what lets a prover recompute the notes of the rollup, such as their openings or the data they derive from, since a [ZkTransfer](bedrock-mantle.md#zero-knowledge-transfer-proof-zktransfer) consuming a note takes its opening.

## What the Ledger Does Not Guarantee

Funds leave a rollup only through its [steps](#rollup_prove): a user exits when a step pays it out. If no [sequencer](bedrock-mantle-channels.md#decentralized-sequencing) [inscribes](#rollup_inscribe), no step can be proven and the funds of the rollup stay frozen. Users trust the [STF](#stf-verification-key) circuit of the rollup, the rule by which its steps change its verification key, and the [setup](common-cryptographic-components.md#groth16-zk-snark) of each key: a faulty circuit, or a key whose setup lets someone forge proofs, can pay the funds of the rollup to anyone.

# Rollup Channel State

## Rollup State

Validators keep the state of a rollup channel, of kind `ROLLUP`, in the `rollup` field of its [`ChannelState`](bedrock-mantle-channels.md#channel-operations), next to the sequencing fields and the note set every channel has:

```python
class RollupState:
    key: Groth16Key                       # the verification key of the STF proofs
    state_root: zkhash                    # the state root after the last proven inscription
    deposits: dict[Hash, PendingDeposit]  # the deposits waiting to be minted,
                                          # by the op_id of their ROLLUP_DEPOSIT
    unproven: list[(Hash, Slot)]          # the op_id and the block slot of each unproven
                                          # inscription, oldest first

class PendingDeposit:
    value: TokenValue  # the value deposited
    intent: zkhash     # the hash of what the depositor expects from the rollup
```

A pending deposit waits in `deposits` until a step mints it. A step proves only the oldest entry of `unproven`, so every step starts from the state root the previous step left, and the proven state of the rollup is always a prefix of its inscriptions.

## STF Verification Key

```python
class Groth16Key:
    alpha: G1
    beta: G2
    gamma: G2
    delta: G2
    ic: list[G1]  # (len = 6) one point per public input of an STF proof, plus one
```

`G1` and `G2` are points of the groups of BN254 of these names, and `alpha`, `beta`, `gamma`, `delta` and `ic` are the points of a [Groth16](common-cryptographic-components.md#groth16-zk-snark) verification key.

An STF proof always has five public inputs: the state root of the rollup, its next state root, the `op_id` of the inscription it proves, the slot of the block that included that inscription, and `effects_hash`, the hash of the effects of the step ([`ROLLUP_PROVE`](#rollup_prove)). Since the size of a Groth16 verification key depends only on its number of public inputs, every rollup key has the same size, and the ledger stores and verifies the key of every rollup the same way.

A rollup that applies the data of its inscriptions should have its STF circuit recompute the `op_id` it takes as its third public input from the encoded [`RollupInscribe`](#rollup_inscribe) it applies, so that its proof covers exactly the data, parent and signer its sequencer inscribed. The circuit then hashes the inscription with BLAKE2b, over up to [`MAX_OPERATION_DATA_SIZE`](mantle-transaction-encoding.md#channel-operations) bytes of data.

`Groth16_verify(key, public_inputs, proof)` verifies a proof against a verification key and its public inputs, as [Groth16](common-cryptographic-components.md#groth16-zk-snark) specifies.

# Operations

## Rollup Operations

### ROLLUP_CREATE

Create a rollup channel with its accredited keys, its rotation parameters, the verification key of its STF proofs and its initial state root. Anyone can create a rollup channel, under a `ChannelId` no channel holds.

#### Payload

```python
class RollupCreate:
    channel: ChannelId                        # 32 bytes, the channel to create
    keys: list[Ed25519PublicKey]              # the accredited keys, limited to 65 535 keys
    posting_timeframe: u32                    # number of slots (0 = infinity)
    posting_timeout: u32                      # number of slots (0 = no timeout)
    verification_key: Groth16Key              # the key of the STF proofs
    state_root: zkhash                        # the initial state root of the rollup
```

#### Proof

  The proof is empty.

#### Execution Gas

  Rollup Create Operations have a fixed Execution Gas cost of `EXECUTION_ROLLUP_KEY_GAS`. See [Gas Determination](bedrock-mantle.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
create: RollupCreate

channels: dict[ChannelId, ChannelState]
```

  *Validate*

  1. Ensure the channel does not exist.
      ```python
      assert create.channel not in channels
      ```

  2. Ensure the rollup has accredited keys, each with an index the round-robin can hold in a `u16`.
      ```python
      assert 0 < len(create.keys) < 2**16
      ```

  3. Ensure every point of the key is on its curve, in its prime-order subgroup and not the point at infinity, since an invalid point would make the STF proofs of the rollup unsound. `is_valid_g1(point)` (resp. `is_valid_g2(point)`) holds when the point satisfies these three conditions in the group $`\mathbb{G}_1`$ (resp. $`\mathbb{G}_2`$) of BN254.
      ```python
      key = create.verification_key
      for point in [key.alpha] + key.ic:
          assert is_valid_g1(point)
      for point in [key.beta, key.gamma, key.delta]:
          assert is_valid_g2(point)
      ```

#### Execution

  *Given*

```python
create: RollupCreate

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```

  *Execute*

Create the rollup under the parameters of the payload.

```python
ledger.sets.append(empty_note_set())
chan = default_channel(block_slot,
                       create.keys,
                       ROLLUP,
                       len(ledger.sets) - 1,
                       RollupState(key = create.verification_key,
                                   state_root = create.state_root,
                                   deposits = {},
                                   unproven = []))
chan.posting_timeframe = create.posting_timeframe
chan.posting_timeout = create.posting_timeout
channels[create.channel] = chan
```

### ROLLUP_INSCRIBE

Write the data of a state transition to a rollup channel, extending the tip of the channel, and the inscription joins the unproven inscriptions of the rollup, which its steps prove in that order.

The STF reads the data of the inscription through its `op_id` ([STF Verification Key](#stf-verification-key)). A rollup should let its STF prove, for an inscription it cannot apply, a step that mints no deposit, makes no transfer and keeps its state root, so that the inscription does not block the ones after it.

#### Payload

```python
class RollupInscribe:
    channel: ChannelId        # 32 bytes Channel being written to
    inscription: bytes        # the data of the state transition
    parent: hash              # Previous message in the channel
    signer: Ed25519PublicKey  # Identity of message sender
```

#### Proof

```python
Ed25519Signature  # by the signer, over the mantle_txhash
```

#### Execution Gas

  Rollup Inscribe Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_INSCRIBE_GAS`. See [Gas Determination](bedrock-mantle.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: hash
msg: RollupInscribe
sig: Ed25519Signature

channels: dict[ChannelId, ChannelState]
block_slot: Slot
```

  *Validate*

  1. Ensure the inscription does not exceed [`MAX_OPERATION_DATA_SIZE`](mantle-transaction-encoding.md#channel-operations).
      ```python
      assert len(msg.inscription) <= MAX_OPERATION_DATA_SIZE
      ```

  2. Ensure the channel exists and is a rollup channel.
      ```python
      assert msg.channel in channels
      chan = channels[msg.channel]
      assert chan.kind == ROLLUP
      ```

  3. Ensure the signer is the sequencer the [round-robin](bedrock-mantle-channels.md#decentralized-sequencing) designates.
      ```python
      current_sequencer_index = round_robin(block_slot, chan)[0]
      assert msg.signer == chan.accredited_keys[current_sequencer_index]
      ```

  4. Ensure the inscription continues the channel sequence.
      ```python
      assert msg.parent == chan.tip_hash
      ```

  5. Verify the signature of the signer.
      ```python
      assert Ed25519_verify(txhash, msg.signer, sig)
      ```

#### Execution

  *Given*

```python
msg: RollupInscribe

channels: dict[ChannelId, ChannelState]
block_slot: Slot
```

  *Execute*

  1. Update the channel sequencer.
      ```python
      chan = channels[msg.channel]
      (new_sequencer_index, new_sequencer_starting_slot) = round_robin(block_slot, chan)

      chan.tip_sequencer_starting_slot = new_sequencer_starting_slot
      chan.tip_sequencer = new_sequencer_index
      ```

  2. Update the channel tip.
      ```python
      chan = channels[msg.channel]
      chan.tip_hash = hash(encode(msg))
      chan.tip_slot = block_slot
      ```

  3. Queue the inscription for its step, with the slot of its block.
      ```python
      chan = channels[msg.channel]
      chan.rollup.unproven.append((derive_op_id(msg), block_slot))
      ```

The slot of the block is recorded with the [`op_id`](bedrock-mantle.md#note-commitment-and-nullifier) of the inscription because the STF proof of its step takes it as a public input: it is fixed once the inscription is in a block, and the prover reads it from the ledger.

### ROLLUP_DEPOSIT

Deposit value into a rollup channel. The deposit consumes notes of the ledger note set and creates no note: it records a [pending deposit](#rollup-state) of its value and its intent in the `deposits` of the rollup, under its [`op_id`](bedrock-mantle.md#note-commitment-and-nullifier), until a [`ROLLUP_PROVE`](#rollup_prove) mints it into the note set of the rollup.

A deposit waits until a step chosen by the sequencers of the rollup mints it, and the ledger never refunds it, so the STF decides when the rollup takes it in. The ledger keeps only the value and intent of a deposit: its inscription publishes data for the zone, which its `intent` can commit to.

#### Payload

```python
class RollupDeposit:
    channel: ChannelId
    inputs: list[NoteNullifier]  # nullifiers of the consumed notes of the ledger note set
    commitment_root: MerkleRoot  # the MMR root of the ledger note set at the end of one of the last ROOT_WINDOW blocks
    excess_value: TokenValue     # the excess to pay the fees
    value: TokenValue            # the value deposited
    intent: zkhash               # the hash of what the depositor expects from the rollup
    inscription: bytes           # the zone message of the deposit
```

#### Proof

  A Rollup Deposit proves the inputs, the deposited value and the excess value with a [Zero Knowledge Transfer Proof (ZkTransfer)](bedrock-mantle.md#zero-knowledge-transfer-proof-zktransfer).

```python
ZkTransfer
```

#### Execution Gas

  Rollup Deposit Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_DEPOSIT_GAS`. See [Gas Determination](bedrock-mantle.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash_fr: zkhash # mantle_txhash of the tx containing this Operation, reduced modulo p
deposit: RollupDeposit
deposit_proof: ZkTransfer

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Validate*

  1. Ensure the inscription does not exceed [`MAX_OPERATION_DATA_SIZE`](mantle-transaction-encoding.md#channel-operations).
      ```python
      assert len(deposit.inscription) <= MAX_OPERATION_DATA_SIZE
      ```

  2. Ensure the channel exists and is a rollup channel.
      ```python
      assert deposit.channel in channels
      chan = channels[deposit.channel]
      assert chan.kind == ROLLUP
      ```

  3. Ensure all inputs are spendable in the [ledger note set](bedrock-mantle.md#ledger), `LEDGER_SET`.
      ```python
      ledger.sets[LEDGER_SET].assert_spendable(deposit.inputs)
      ```

  4. Validate ownership over the consumed notes, and that their value covers the deposited value and the excess value.
      ```python
      assert ledger.sets[LEDGER_SET].verify_transfer(deposit.inputs,
                                                     [],
                                                     checked_uint64(deposit.excess_value + deposit.value),
                                                     deposit.commitment_root,
                                                     mantle_txhash_fr,
                                                     deposit_proof)
      ```

#### Execution

  *Given*

```python
deposit: RollupDeposit

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Execute*

  1. Consume the inputs in the ledger note set.
      ```python
      ledger.sets[LEDGER_SET].execute_spending(deposit.inputs)
      ```

  2. Record the deposit as pending under its `op_id`.
      ```python
      chan = channels[deposit.channel]
      chan.rollup.deposits[derive_op_id(deposit)] = PendingDeposit(value=deposit.value,
                                                                   intent=deposit.intent)
      ```

### ROLLUP_PROVE

Apply the oldest unproven inscription of a rollup channel with a step of the rollup. Anyone posts it: the step mints the pending deposits it lists into one note of the rollup note set, applies its transfers to the notes of the rollup and pays their payouts to the ledger note set, and sets the next state root of the rollup and, when the step carries one, its next configuration, all of which its STF proof covers.

A step proves only the oldest entry of `unproven`, so a node never holds a proof it has not applied. Provers compute the steps of consecutive inscriptions in parallel, each from the state the step before it leaves, and the mempool orders the steps by their inscriptions. The transfers of a step are verified against the live commitment MMR root of the rollup note set, which a prover knows in advance since only this Operation appends to that set, so consecutive steps of a rollup can share a block, and even a Mantle Transaction.

#### Payload

```python
class RollupTransfer:
    inputs: list[NoteNullifier]    # nullifiers of the consumed notes of the rollup note set
    outputs: list[NoteCommitment]  # commitments of the created notes of the rollup note set
    payouts: list[NoteCommitment]  # commitments of the notes created in the ledger note set

class RollupConfig:
    keys: list[Ed25519PublicKey]                     # the next accredited keys, limited to 65 535 keys
    posting_timeframe: u32                           # number of slots (0 = infinity)
    posting_timeout: u32                             # number of slots (0 = no timeout)
    verification_key: Groth16Key | None              # the next key of the STF proofs, None to keep the current one

class RollupProve:
    channel: ChannelId                  # 32 bytes, the rollup channel
    deposits: list[Hash]                # the op_id of each pending deposit the step mints
    transfers: list[RollupTransfer]     # the transfers of the step, in the order they apply
    state_root: zkhash                  # the next state root of the rollup
    next_config: RollupConfig | None    # the next configuration of the rollup, None to keep the current one
```

The deposits a step mints become one note of the rollup note set, the deposit note, which holds their total value. It is held by `PK0`, so that any prover can spend it in a transfer of the step or of a later step, and its staking key is `0`, so that no one leads with it ([Keys](bedrock-mantle.md#keys)). Its nonce derives from the `op_id` of the inscription the step proves, and a step proves an inscription once, so no two deposit notes share a commitment.

Each `RollupTransfer` is a [ZkTransfer](bedrock-mantle.md#zero-knowledge-transfer-proof-zktransfer) whose outputs are its `outputs` followed by its `payouts`, and it balances exactly, with an `excess_value` of `0`. A step therefore pays no fee: its prover pays the fees of its Mantle Transaction with another Operation of it, such as a Transfer.

The STF proof covers the effects of the step through `effects_hash`, its fifth public input: the value and intent of every minted deposit, in the order of `deposits`, the inputs, outputs and payouts of every transfer, and the next configuration. `effects_hash` is a BLAKE2b-256 hash, under the DST `ROLLUP_EFFECTS_V1`, of the encoding of these effects, reduced modulo $`p`$ as `op_id` is, since it is a public input of a Groth16 proof. It is a classic hash because most STF circuits are wrapped zkVMs, for which BLAKE2b is the natural hash.

```python
def rollup_effects_hash(minted: list[PendingDeposit],
                        transfers: list[RollupTransfer],
                        next_config: RollupConfig | None) -> zkhash:
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"ROLLUP_EFFECTS_V1")
    h.update(encode(len(minted)))         # UINT16
    for deposit in minted:
        h.update(encode(deposit.value))   # Value
        h.update(encode(deposit.intent))  # Intent
    h.update(encode(transfers))           # RollupTransfers of the encoding
    h.update(encode(next_config))         # OptionalConfig
    return FiniteField(h.digest(), byte_order="little", modulus= p)
```

#### Proof

```python
class RollupProveOpProof:
    transfer_proofs: list[ZkTransfer]  # one per transfer, in the order of the transfers
    stf_proof: Groth16Proof            # the proof of the STF, under the current key of the rollup
```

The ZkTransfers and the STF proof of a step are bound to the `op_id` of the inscription it proves, which is the `msg` of every ZkTransfer and the third public input of the STF proof, and not to the `mantle_txhash`, so anyone can post the step.

#### Execution Gas

  Rollup Prove Operations have an Execution Gas cost of `EXECUTION_TRANSFER_GAS * len(transfers) + EXECUTION_ROLLUP_PROOF_GAS`, plus `EXECUTION_ROLLUP_KEY_GAS` when its next configuration carries a verification key. See [Gas Determination](bedrock-mantle.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
prove: RollupProve
proof: RollupProveOpProof

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Validate*

  1. Ensure the channel exists, is a rollup channel and has an unproven inscription. The step proves the oldest one, `k`, whose `op_id` binds its proofs.
      ```python
      assert prove.channel in channels
      chan = channels[prove.channel]
      assert chan.kind == ROLLUP
      rollup = chan.rollup
      assert len(rollup.unproven) > 0
      (k, slot_k) = rollup.unproven[0]
      msg = FiniteField(k, byte_order="little", modulus= p)
      ```

  2. Ensure the minted deposits are distinct and pending, and sum their values.
      ```python
      assert len(prove.deposits) == len(set(prove.deposits))
      minted = []
      for deposit_id in prove.deposits:
          assert deposit_id in rollup.deposits
          minted.append(rollup.deposits[deposit_id])
      total = checked_uint64(sum(deposit.value for deposit in minted))
      ```

  3. Derive the deposit note, if the minted deposits hold any value.
      ```python
      deposit_outputs = []
      if total > 0:
          deposit_note = Note(value=total,
                              nonce=derive_note_nonce(k, 0, total, PK0),
                              public_key=PK0,
                              stake_public_key=0)
          deposit_outputs = [derive_note_commitment(deposit_note)]
      ```

  4. Start from the commitment MMR of the rollup note set as it stands, extended with the deposit note.
      ```python
      note_set = ledger.sets[chan.note_set]
      peaks = list(note_set.commitments)
      for note_commitment in deposit_outputs:
          mmr_append(peaks, note_commitment)
      ```

  5. Ensure every transfer is spendable in the rollup note set and balances exactly, in the order of the transfers.
      ```python
      assert len(proof.transfer_proofs) == len(prove.transfers)
      step_nullifiers = set()  # the nullifiers of the earlier transfers of the step
      for (transfer, transfer_proof) in zip(prove.transfers, proof.transfer_proofs):
          note_set.assert_spendable(transfer.inputs)
          for note_nullifier in transfer.inputs:
              assert note_nullifier not in step_nullifiers
              step_nullifiers.add(note_nullifier)
          assert ZkTransfer_verify(transfer.inputs,
                                   transfer.outputs + transfer.payouts,
                                   0,  # a transfer of a step balances exactly
                                   mmr_root(peaks),
                                   msg,
                                   transfer_proof)
          # the later transfers of the step cover the outputs of this transfer
          for note_commitment in transfer.outputs:
              mmr_append(peaks, note_commitment)
      ```

  6. Ensure the next configuration is one [`ROLLUP_CREATE`](#rollup_create) accepts.
      ```python
      config = prove.next_config
      if config is not None:
          assert 0 < len(config.keys) < 2**16
          key = config.verification_key
          if key is not None:
              for point in [key.alpha] + key.ic:
                  assert is_valid_g1(point)
              for point in [key.beta, key.gamma, key.delta]:
                  assert is_valid_g2(point)
      ```

  7. Verify the STF proof under the current key of the rollup, from its state root to the next one, for the inscription `k`, the slot of its block and the effects of the step.
      ```python
      assert Groth16_verify(rollup.key,
                            [rollup.state_root,
                             prove.state_root,
                             msg,
                             FiniteField(slot_k, byte_order="little", modulus= p),
                             rollup_effects_hash(minted, prove.transfers, prove.next_config)],
                            proof.stf_proof)
      ```

  8. Add the payouts to the buffer of the ledger note set.
      ```python
      for transfer in prove.transfers:
          ledger.sets[LEDGER_SET].tx_commitment_buffer.extend(transfer.payouts)
      ```

#### Execution

  *Given*

```python
prove: RollupProve

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```

  *Execute*

  1. Mint the deposits: remove them from the pending deposits, and add the deposit note to the rollup note set.
      ```python
      chan = channels[prove.channel]
      rollup = chan.rollup
      note_set = ledger.sets[chan.note_set]
      (k, _) = rollup.unproven[0]
      total = sum(rollup.deposits[deposit_id].value for deposit_id in prove.deposits)
      for deposit_id in prove.deposits:
          del rollup.deposits[deposit_id]
      if total > 0:
          note_set.execute_adding([derive_note_commitment(Note(value=total,
                                                               nonce=derive_note_nonce(k, 0, total, PK0),
                                                               public_key=PK0,
                                                               stake_public_key=0))])
      ```

  2. Apply the transfers, in their order: consume their inputs and create their outputs in the rollup note set, and create their payouts in the ledger note set.
      ```python
      for transfer in prove.transfers:
          note_set.execute_spending(transfer.inputs)
          note_set.execute_adding(transfer.outputs)
          ledger.sets[LEDGER_SET].execute_adding(transfer.payouts)
      ```

  3. Remove the proven inscription, and set the next state root.
      ```python
      rollup.unproven.pop(0)
      rollup.state_root = prove.state_root
      ```

  4. If the step carries a next configuration, set its accredited keys, its rotation parameters and, if it carries one, its verification key, and restart the round-robin.
      ```python
      config = prove.next_config
      if config is not None:
          chan.accredited_keys = config.keys
          chan.tip_slot = block_slot
          chan.tip_sequencer = 0
          chan.tip_sequencer_starting_slot = block_slot
          chan.posting_timeframe = config.posting_timeframe
          chan.posting_timeout = config.posting_timeout
          if config.verification_key is not None:
              rollup.key = config.verification_key
      ```

A step with no next configuration leaves the turn to the rotation of the sequencers, so the steps themselves never pin the turn to one sequencer. A change of configuration applies from the block of its step, not from the block of its inscription: the inscriptions after `k` that come before that step are signed under the current keys, and a sequencer a step removes stays accredited until that step is proven.
