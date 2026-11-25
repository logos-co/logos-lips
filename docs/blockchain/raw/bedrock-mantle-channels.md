# MANTLE-CHANNELS

| Field | Value |
| --- | --- |
| Name | Mantle Channels |
| Slug | 246 |
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
| 1.0.0 | Initial revision: the channel Operations moved from [Mantle](bedrock-mantle-specification.md). | 2026-11-25 |
| 1.1.0 | A channel has a kind, fixed at its creation: a native channel is created by its first configuration, a `CHANNEL_CONFIG` whose `parent` is `ZERO`, and the channel Operations of this document act on existing native channels, rollup channels being specified in [Mantle Rollups](bedrock-mantle-rollups.md). The null channel is a native channel that exists before Genesis. A `Step` is bound to its `step_id`, hashed under the DST `STEP_V1`. Leading with a channel note takes its nullifier key and its staking secret key, and moving or withdrawing it takes its spending secret key | 2026-11-25 |

# Introduction

Channels let Zones post their updates on chain and bridge notes between Zones and Bedrock. This document specifies the channel Operations; the Mantle Transaction that carries them and the ledger they act on are specified in [Mantle](bedrock-mantle-specification.md).

# Operations

## Channel Operations

Channels allow Zones to post their updates on chain. Channels form virtual chains that overlay on top of the Cryptarchia blockchain. Clients and Followers of a Zone can watch its channel to learn the state of that Zone. Each channel has its own [note set](bedrock-mantle-specification.md#ledger), enabling bridging between Zones and Bedrock.

### Message Ordering

Channels form virtual chains by having each message reference its parent message. The order of messages in these channels is enforced by the sequencer by building a hash chain of messages, i.e. new messages reference the previous messages through a parent hash. Given that Cryptarchia has long finality times, these message parent references allow Zone sequencers to continue to post new updates to channels without having to wait for finality. No matter how Cryptarchia forks and reorgs, the channel messages from honest sequencers will eventually be re-included in a way that satisfies the virtual chain order, with one limit: a step is valid only against a commitment root recorded in the last [`ROOT_WINDOW`](bedrock-mantle-specification.md#ledger) blocks of the fork it lands on. A reorg that moves the channel deposits or the steps a step builds on into other blocks can leave its root absent from the winning fork, which invalidates the inscription carrying the step and the inscriptions chained after it, and the sequencer, who cannot prove the step again for its holder, re-publishes the chain without it.

Configurations form a second hash chain within the channel: each configuration names the configuration it supersedes, so a pending reconfiguration stays valid while the sequencer keeps posting inscriptions.

A native channel is created by its first configuration, a [`CHANNEL_CONFIG`](#channel_config) whose `parent` is `ZERO`: the keys it lists become the accredited keys of the channel (Note that a key may correspond to a threshold signature key), and the channel stays a native channel for good. No inscription creates a channel, so every channel starts with the committee and the sequencing parameters its creator chose, and an inscription always lands on a channel whose kind is known. Accredited keys of a channel forms a committee that can configure the channel and take turns to write messages to that channel following a round-robin algorithm. Configuring a channel includes modifying the list of accredited keys, the round-robin parameters and the required number of signatures to establish a new configuration.

Validators must maintain the following state to process channel Operations:

```python
channels: dict[ChannelId, ChannelState] # ChannelId is 32 bytes

class ChannelState:
    # Channel Configuration
    accredited_keys: list[Ed25519PublicKey]  # limited to 65 535 keys
    configuration_threshold: u16  # indicating how many keys are
                                  # required to update the configuration

    # Message Ordering
    tip_hash: hash         # Last message of the channel
    config_tip_hash: hash  # Last configuration of the channel

    # Decentralized Sequencing
    tip_slot: Slot
    tip_sequencer: u16      # indicating the actual
                            # sequencer position in the list of accredited keys
    tip_sequencer_starting_slot: Slot
    posting_timeframe: u32  # number of slots (0 = infinity)
    posting_timeout: u32    # number of slots (0 = no timeout)

    # Kind, fixed when the channel is created
    kind: NativeChannel | RollupChannel  # RollupChannel is specified in Mantle Rollups,
                                         # bedrock-mantle-rollups.md

class NativeChannel:
    # Bridging
    note_set: int | None    # index of the note set of the channel in ledger.sets,
                            # None for the null channel

def default_channel(block_slot: Slot, keys: list[Ed25519PublicKey], kind: NativeChannel | RollupChannel) -> ChannelState:
    return ChannelState(
        tip_hash = ZERO,
        config_tip_hash = ZERO,
        tip_slot = block_slot,
        accredited_keys = keys,
        tip_sequencer = 0,
        tip_sequencer_starting_slot = block_slot,
        posting_timeframe = 0,
        posting_timeout = 0,
        configuration_threshold = 1,
        kind = kind)

def create_channel(channel_id: ChannelId, block_slot: Slot, keys: list[Ed25519PublicKey]):
    # a new channel appends a new note set, so note sets of channels are ordered by creation
    ledger.sets.append(empty_note_set())
    channels[channel_id] = default_channel(block_slot, keys, NativeChannel(len(ledger.sets) - 1))
```

Each channel Operation checks the kind of channel it acts on, and the Operations of this document act on native channels only; rollup channels and their Operations are specified in [Mantle Rollups](bedrock-mantle-rollups.md). Since the kind is fixed at creation, a channel follows the rules of its kind for its whole life, and the round-robin and the parent and signer checks of an inscription are the same for every kind.

The null channel, whose `ChannelId` is 32 zero bytes, is a native channel that exists before Genesis. Its only accredited key is the null key, the Ed25519 public key made of 32 zero bytes, and its other fields are those `default_channel` gives at the Genesis slot `0`, its `tip_hash` and `config_tip_hash` being `ZERO`. It exists from the start so that the Cryptarchia inscription of the [Genesis block](bedrock-genesis-block.md) extends it as any inscription extends its channel, with a `parent` of `ZERO`. It carries the inscriptions of the Genesis block and nothing after them, since it is signed by a key no one holds. It has no note set: no Operation can deposit to it, withdraw from it or publish a step in it.

Note that the user chooses the ChannelId mapping to the ChannelState (but it’s restricted to 32 bytes). We don't currently impose restrictions on it, but we may do so in the future to prevent undesirable behaviors.

### Decentralized Sequencing

To determine which sequencer is currently authorized to send messages, we use a round-robin algorithm. When a message is posted to a channel, the following algorithm is used to determine who the sequencer is:

```python
# Round Robin algorithm determining the new sequencer index and the
# new sequencer starting slot
def round_robin(block_slot: Slot, channel: ChannelState) -> (u16, u64):
    elapsed_slots = block_slot - channel.tip_slot
    if elapsed_slots >= channel.posting_timeout and channel.posting_timeout != 0:
        # Get the number of sequencers that get timed out
        sequencers_timed_out = elapsed_slots // channel.posting_timeout
        index = (
            (channel.tip_sequencer + sequencers_timed_out)
            % len(channel.accredited_keys)
        )
        starting_slot = (
            channel.tip_slot
            + sequencers_timed_out * channel.posting_timeout
        )
    elif channel.posting_timeframe == 0:
        # An infinite timeframe never rotates: the tip sequencer keeps its turn
        index = channel.tip_sequencer
        starting_slot = channel.tip_sequencer_starting_slot
    else:
        # Get the number of timeframes elapsed to get who is the sequencer
        tip_sequencer_duration = block_slot - channel.tip_sequencer_starting_slot
        index = (
            (channel.tip_sequencer + (tip_sequencer_duration // channel.posting_timeframe))
            % len(channel.accredited_keys)
        )
        starting_slot = (
            channel.tip_sequencer_starting_slot
            + (tip_sequencer_duration // channel.posting_timeframe) * channel.posting_timeframe
        )
    return (index, starting_slot)
```

### Bridging

Channels let their bridged notes keep participating in Proof of Stake. When a user deposits notes into a channel, they are not turned into inert collateral. They are consumed and re-created as notes of the channel's note set, which continue to count toward Proof of Stake and can still be used to create PoLs (see [Ledger](bedrock-mantle-specification.md#ledger)). Two goals motivate this design:

- **More PoS participation, stronger security.** Funds deposited into a channel would otherwise leave the staking set. Keeping them as channel notes means the capital backing the application layer also backs consensus security, so bridging does not shrink the stake that secures the chain.
- **No split between security and application.** A user no longer has to choose between staking funds or using them in a channel. The same funds do both at once. They stay usable inside the channel while still earning Proof of Leadership rewards, so capital is never fragmented between the two.

**Holders keep their notes.** A channel note is a note of the channel's note set, owned by the holder of its `ZkPublicKey`. Only that holder can spend it, in one of two ways:

- *Inside the channel*, the holder signs a step off-chain: a ZkTransfer that consumes its channel notes and creates channel notes of the same total value, together with the inscription of the step, its zone message. The sequencers of the channel collect the steps of their users and publish them in a [`CHANNEL_INSCRIBE`](#channel_inscribe), grouping them in mini-blocks and ordering each mini-block as they choose, since a step holds at any position in its mini-block. The ledger verifies every step, so a sequencer orders the moves of a channel but never makes one.
- *Out of the channel*, the holder posts a [`CHANNEL_WITHDRAW`](#channel_withdraw) alone, its fee paid by a ledger note in the same Mantle Transaction. It takes effect `WITHDRAW_DELAY` slots later, unless an inscription of the channel consumes its notes with a valid step in the meantime. The withdrawal is the forced exit of a holder whose steps the sequencers do not publish. It also settles a holder who signs both a step and a withdrawal of the same notes optimistically: the step wins if an inscription publishes it before the withdrawal is due, and the holder has then paid the fees of the withdrawal for nothing.

**Ageing.** Because a channel deposit and a step consume notes and create new ones, a channel note restarts the ageing process and must age again before it can create a PoL. Bridged funds still count toward Proof of Stake, so the goals above hold, but the participation is not continuous across these moves.

**What each party can do.**

| Party | Can | Cannot |
|---|---|---|
| Holder of the note's spending secret key | Sign a step moving the note inside the channel. Withdraw the note alone, paying the fee with a ledger note | Spend the note in any other Operation. Create a PoL with the note without the staking secret key |
| Holder of the note's nullifier key and staking secret key, the same key by default | Create a PoL with the note and earn its rewards under a key of its choice. See when the note is spent | Spend the note. Create a PoL with a note whose staking key is `0` |
| Channel sequencers | Collect the steps of their users and publish them in the inscriptions of the channel, grouped in mini-blocks in the order they choose, a step consuming an output of the inscription coming in a later mini-block | Move a note without its holder's step |

### CHANNEL_INSCRIBE

Write a message to a native channel with the message data being permanently stored on the Logos Blockchain, and apply the steps the sequencer collected from the users of the channel. The list of mini-blocks can be empty, in which case the inscription only writes its message.

#### Payload

```python
class Step:
    inputs: list[NoteNullifier]    # nullifiers of the consumed channel notes
    outputs: list[NoteCommitment]  # commitments of the created channel notes
    commitment_root: MerkleRoot    # the MMR root of the channel note set at the end of one of the last ROOT_WINDOW blocks
    inscription: bytes             # the zone message of this step, signed by its holder

class Inscribe:
    channel: ChannelId       # 32 bytes Channel being written to
    inscription : bytes      # Message to be written on the blockchain
    parent: hash             # Previous message in the channel
    signer: Ed25519PublicKey # Identity of message sender
    mini_blocks: list[list[Step]]  # Moves of channel notes, in the order they apply, possibly
                                   # empty. A mini-block holds at least one step
```

A `NoteNullifier` is the nullifier of a note and a `NoteCommitment` its commitment, as [Note Commitment and Nullifier](bedrock-mantle-specification.md#note-commitment-and-nullifier) defines them, and a `MerkleRoot` the root of a Merkle tree.

A step is signed by the holder of the notes it consumes, off-chain and before the Mantle Transaction carrying it exists. Its ZkTransfer is therefore bound to the step itself rather than to the `mantle_txhash`, and it balances exactly, with an `excess_value` of `0`.

The `inscription` of the `Inscribe` is the message of the sequencer, and the `inscription` of a step the zone message of the holder of the step. The ZkTransfer of the step binds its inscription together with its inputs and outputs, so a sequencer publishes the message a holder signed with the move it signed, or drops the step whole. The inscription of the `Inscribe` and the inscriptions of its steps count together against `MAX_OPERATION_DATA_SIZE`.

The steps of an inscription are grouped in mini-blocks. The proof of a step is verified, by the [`verify_transfer`](bedrock-mantle-specification.md#input-notes-spendability-validation) method of the note set, against its referenced root extended with the buffer of the channel note set as it stands when the mini-block of the step starts: the commitments the earlier Operations of the Mantle Transaction and the earlier mini-blocks of the inscription added. A step can therefore consume the notes of earlier blocks and the outputs of the earlier mini-blocks, but not the outputs of its own mini-block. Its proof depends on what precedes its mini-block and not on its position inside it, and the holders prove their steps independently of one another:

- The steps of the first mini-block, when no earlier Operation of the Mantle Transaction added to the channel note set, are proven against their recent root alone, so a sequencer collects the steps of many users and publishes them in the order it chooses. A sequencer should place an Operation adding to that note set after the inscription: if it comes first, every step of the first mini-block covers what it adds.
- If the first mini-block adds 400 commitments to the buffer, every step of the second mini-block covers these 400: it can consume the outputs of the first mini-block, and the steps of the second mini-block are again ordered freely among themselves. The same holds for the next mini-blocks.

Extending every proof with the whole buffer would instead tie each proof to its position: each holder would have to wait for the sequencer to fix every step before its own, and the steps would be proven one after another.

The mini-block of a step is public, so a step of a later mini-block reveals that its inputs are among the notes under its root and the commitments it covers. Covering the whole of the previous mini-blocks keeps a step from pointing at the notes it consumes.

The ZkTransfer of a step is bound to `step_id`, a BLAKE2b-256 hash, under the DST `STEP_V1`, of the channel and of the encoded step, its inputs, outputs, root and inscription included, reduced modulo $`p`$ as `op_id` is. It is a classic hash because it is only the public `msg` of the ZkTransfer of the holder, which no circuit recomputes.

```python
def step_id(channel: ChannelId, step: Step) -> zkhash:
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"STEP_V1")
    h.update(channel)
    h.update(encode(step))  # the Step of the encoding
    return FiniteField(h.digest(), byte_order="little", modulus= p)
```

#### Proof

```python
class ChannelInscribeOpProof:
    signature: Ed25519Signature    # by the signer, over the mantle_txhash
    step_proofs: list[ZkTransfer]  # one per step, in the order of the steps
```

#### Execution Gas

  Channel Inscribe Operations have an Execution Gas cost of `EXECUTION_CHANNEL_INSCRIBE_GAS + EXECUTION_TRANSFER_GAS * len(steps)`. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: hash
msg: Inscribe
proof: ChannelInscribeOpProof

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```
 
  *Validate*

```python
# The inscription and the inscriptions of the steps count together
steps = [step for mini_block in msg.mini_blocks for step in mini_block]
assert len(msg.inscription) + sum(len(step.inscription) for step in steps) <= MAX_OPERATION_DATA_SIZE

# Ensure the channel exists and is a native channel
assert msg.channel in channels
chan = channels[msg.channel]
assert isinstance(chan.kind, NativeChannel)

current_sequencer_index = round_robin(block_slot, chan)[0]

# Ensure the signer is the one authorized to write to the channel
assert msg.signer == chan.accredited_keys[current_sequencer_index]

# Ensure message is continuing the channel sequence
assert msg.parent == chan.tip_hash

# Ensure the msg signer signature
assert Ed25519_verify(txhash, msg.signer, proof.signature)

# Ensure the null channel, which has no note set, receives no step
assert chan.kind.note_set is not None or len(msg.mini_blocks) == 0
note_set = ledger.sets[chan.kind.note_set] if chan.kind.note_set is not None else None

# Ensure every step is spendable in the channel note set and signed by its holder.
# A step can consume a note created by an earlier Operation or mini-block, never one consumed by
# an earlier step.
assert all(len(mini_block) > 0 for mini_block in msg.mini_blocks)
assert len(proof.step_proofs) == sum(len(mini_block) for mini_block in msg.mini_blocks)
step_proofs = iter(proof.step_proofs)
step_nullifiers = set()    # the nullifiers of the previous steps
for mini_block in msg.mini_blocks:
    # the steps of the mini-block cover the buffer as it stands now
    covered = len(note_set.tx_commitment_buffer)
    for step in mini_block:
        note_set.assert_spendable(step.inputs)
        for note_nullifier in step.inputs:
            assert note_nullifier not in step_nullifiers
            step_nullifiers.add(note_nullifier)
        assert note_set.verify_transfer(step.inputs,
                                        step.outputs,
                                        0,  # a step balances exactly
                                        step.commitment_root,
                                        step_id(msg.channel, step),
                                        next(step_proofs),
                                        covered)
        # the next mini-blocks cover the outputs of this step
        note_set.tx_commitment_buffer.extend(step.outputs)
```

#### Execution

  *Given*

```python
msg: Inscribe

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```

  *Execute*

  1. Apply the steps, in their order.
      ```python
      for step in [step for mini_block in msg.mini_blocks for step in mini_block]:
          note_set = ledger.sets[channels[msg.channel].kind.note_set]
          note_set.execute_spending(step.inputs)
          note_set.execute_adding(step.outputs)
      ```

  2. Update the channel sequencer.
      ```python
      chan = channels[msg.channel]
      (new_sequencer_index, new_sequencer_starting_slot) = round_robin(block_slot, chan)

      chan.tip_sequencer_starting_slot = new_sequencer_starting_slot
      chan.tip_sequencer = new_sequencer_index
      ```

  3. Update the channel tip.
      ```python
      chan = channels[msg.channel]
      chan.tip_hash = hash(encode(msg))
      chan.tip_slot = block_slot
      ```

### CHANNEL_CONFIG

Create a native channel, or overwrite the configuration of a native channel.

#### Payload

```python
class ChannelConfig:
    channel: ChannelId
    parent: hash             # Previous configuration of the channel
    keys: list[Ed25519PublicKey]
    posting_timeframe: u32
    posting_timeout: u32
    configuration_threshold: u16
```

#### Proof

A Channel Config is authorized by a threshold of the channel's accredited keys using [Multiple Ed25519 Signatures Verification](bedrock-mantle-specification.md#multiple-ed25519-signatures-verification).

```python
class ChannelConfigOpProof:
    signatures: list[Ed25519Signature] # signatures from configuration_threshold
    indexes: list[u16]  # signatures of accredited keys with their index.
                        # indexes must be ordered from smallest to
                        # biggest without duplication
```

#### Execution Gas

  Channel Config Operations have a linear Execution Gas cost equal to `EXECUTION_CHANNEL_CONFIG_GAS * configuration_threshold`, where `configuration_threshold` is the one held in the channel state, and `0` for a channel that does not exist yet. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: hash
config: ChannelConfig
proof: ChannelConfigOpProof
channels: dict[ChannelId, ChannelState]
```

  *Validate*

```python
assert config.configuration_threshold > 0
assert len(config.keys) > 0
assert len(config.keys) < 2**16
# The configuration threshold must be reachable with the accredited keys,
# otherwise the channel would be locked out of any future reconfiguration
assert config.configuration_threshold <= len(config.keys)

if config.channel in channels:
    chan = channels[config.channel]

    # Ensure the channel is a native channel, the only kind a configuration reconfigures
    assert isinstance(chan.kind, NativeChannel)

    # Ensure the configuration is extending the last configuration
    # of the channel
    assert config.parent == chan.config_tip_hash

    # Verify the configuration_threshold signatures (see Appendix)
    MultiEd25519_verify(txhash,
                        proof.signatures,
                        proof.indexes,
                        chan.accredited_keys,
                        chan.configuration_threshold)
else:
    # The configuration creates the channel, a native channel, upon execution
    # Ensure that this configuration is the first configuration of the channel
    assert config.parent == ZERO

    # No key is accredited yet, so the threshold to verify against is 0
    # and the proof must carry no signature and no index (see Appendix)
    MultiEd25519_verify(txhash,
                        proof.signatures,
                        proof.indexes,
                        [],
                        0)
```

#### Execution

  *Given*

```python
config: ChannelConfig

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```

  *Execute*

  1. If the channel does not exist, create it as a native channel.

      ```python
      if config.channel not in channels:
          create_channel(config.channel, block_slot, config.keys)
      ```

  2. Update the configuration.

      ```python
      chan = channels[config.channel]

      # Update Channel Configuration Parameters
      chan.accredited_keys = config.keys
      chan.configuration_threshold = config.configuration_threshold

      # Update Decentralized Sequencing Parameters
      chan.tip_slot = block_slot
      chan.tip_sequencer = 0
      chan.tip_sequencer_starting_slot = block_slot
      chan.posting_timeframe = config.posting_timeframe
      chan.posting_timeout = config.posting_timeout
      ```

  3. Update the configuration tip.

      ```python
      chan = channels[config.channel]
      chan.config_tip_hash = hash(encode(config))
      ```

### CHANNEL_DEPOSIT

Deposit notes to a native channel. The deposit consumes notes of the ledger note set and creates notes of the channel note set, which resets their ageing.

A deposit creates its outputs under the keys its depositor chooses, and the holder of each output withdraws it alone. A Zone should therefore credit in its own state only deposit outputs under a key it holds: a withdrawal shows a nullifier, which the Zone cannot link to a commitment without the key of the holder.

A Zone that credits a deposit in its own state must be sure the deposit really lands on-chain. If the Zone reflects the deposit through a `CHANNEL_INSCRIBE` posted in a separate Mantle Transaction, a reorganization can reorder the two so that the inscription is included while the deposit is not, leaving the Zone crediting funds it never received. Two options avoid this:

- Wait for the deposit to be finalized before interpreting it, at the cost of the finalization delay.
- Include the deposit in the same Mantle Transaction as the inscription. Mantle Transactions validate atomically, so the inscription is included only if the deposit is. This removes the waiting period entirely.

#### Payload

```python
class ChannelDeposit:
    channel: ChannelId
    inputs: list[NoteNullifier]    # nullifiers of the consumed notes of the ledger note set
    outputs: list[NoteCommitment]  # commitments of the created notes of the channel note set
    commitment_root: MerkleRoot    # the MMR root of the ledger note set at the end of one of the last ROOT_WINDOW blocks
    excess_value: TokenValue       # the excess to pay the fees
    inscription: bytes             # the zone message of the deposit
```

#### Proof

  A Channel Deposit proves the ownership of the notes being consumed, the created notes and the excess value using a [Zero Knowledge Transfer Proof (ZkTransfer)](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer).

```python
ZkTransfer
```

#### Execution Gas

  Channel Deposit Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_DEPOSIT_GAS`. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash_fr: zkhash # mantle_txhash of the tx containing this Operation, reduced modulo p
deposit: ChannelDeposit
deposit_proof: ZkTransfer

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Validate*

  1. Ensure the inscription does not exceed `MAX_OPERATION_DATA_SIZE`.
      ```python
      assert len(deposit.inscription) <= MAX_OPERATION_DATA_SIZE
      ```

  2. Verify that the channel exists and is a native channel with a note set, which the null channel has not.
      ```python
      assert deposit.channel in channels
      chan = channels[deposit.channel]
      assert isinstance(chan.kind, NativeChannel)
      assert chan.kind.note_set is not None
      ```

  3. Ensure all inputs are spendable in the [ledger note set](bedrock-mantle-specification.md#ledger), `LEDGER_SET`.
      ```python
      ledger.sets[LEDGER_SET].assert_spendable(deposit.inputs)
      ```

  4. Validate ownership over deposited notes and balance.
      ```python
      assert ledger.sets[LEDGER_SET].verify_transfer(deposit.inputs,
                                                     deposit.outputs,
                                                     deposit.excess_value,
                                                     deposit.commitment_root,
                                                     mantle_txhash_fr,
                                                     deposit_proof)
      ```

  5. Add the outputs to the buffer of the channel note set.
      ```python
      ledger.sets[chan.kind.note_set].tx_commitment_buffer.extend(deposit.outputs)
      ```

#### Execution

  *Given*

```python
deposit: ChannelDeposit

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Execute*

Consume the inputs in the ledger note set and create the outputs in the channel note set.

```python
ledger.sets[LEDGER_SET].execute_spending(deposit.inputs)
ledger.sets[channels[deposit.channel].kind.note_set].execute_adding(deposit.outputs)
```

### CHANNEL_WITHDRAW

Withdraw notes from a native channel. The holder of the notes posts the withdrawal alone, and it takes effect `WITHDRAW_DELAY` slots later: its inputs are then consumed in the channel note set and its outputs created in the ledger note set, if none of its inputs was consumed in the meantime. Until then, an inscription of the channel can consume these notes with a valid step, which cancels the withdrawal. A holder therefore cannot invalidate an inscription carrying one of its steps by withdrawing the same note, as long as the inscription lands before the withdrawal is due. A due withdrawal is executed at the start of its block, before the transactions ([Block Execution](bedrock-block-construction.md#block-execution)), and a later step consuming its notes is invalid, and so is the transaction carrying it. The nullifiers and due slots of pending withdrawals are public in the ledger state: a sequencer should not accept a step whose inputs a pending withdrawal may release before its inscription lands, nor a step whose inputs another accredited key of the channel may consume first, since removing the step afterwards also invalidates the steps of the later mini-blocks, whose proofs cover its outputs. The sequencers of a channel should share the nullifiers of the steps they hold before a later mini-block covers them.

```python
WITHDRAW_DELAY: Slot = 86_400  # 1 day
```

`WITHDRAW_DELAY` leaves the sequencers of the channel time to include the steps they accepted before a forced exit takes their notes, so that a withdrawal does not bypass a step its holder authorized. A sequencer checks the `pending_withdrawals` of the channel when it publishes a step, not only when it accepts it, since a step stays valid as long as its root is recent, which on a quiet channel can outlast the delay.

#### Payload

```python
class ChannelWithdraw:
    channel: ChannelId
    inputs: list[NoteNullifier]    # nullifiers of the consumed notes of the channel note set
    outputs: list[NoteCommitment]  # commitments of the notes created in the ledger note set
    commitment_root: MerkleRoot    # the MMR root of the channel note set at the end of one of the last ROOT_WINDOW blocks
```

A withdrawal balances exactly and carries no fee: another Operation of its Mantle Transaction, such as a Transfer, pays the fees. A holder whose funds are all in channels therefore needs a ledger note, of its own or added by a third party, to post its withdrawal. An excess paid when the withdrawal is posted would stay paid even if the withdrawal is dropped later, which would create tokens.

#### Proof

  A Channel Withdraw proves the ownership of the notes being consumed and the created notes, with an excess value of `0`, using a [Zero Knowledge Transfer Proof (ZkTransfer)](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer).

```python
ZkTransfer
```

#### Execution Gas

  Channel Withdraw Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_WITHDRAW_GAS`. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash_fr: zkhash # mantle_txhash of the tx containing this Operation, reduced modulo p
withdrawal: ChannelWithdraw
proof: ZkTransfer

channels: dict[ChannelId, ChannelState]
ledger: Ledger
```

  *Validate*

  1. Check that the channel exists and is a native channel with a note set, which the null channel has not.
      ```python
      assert withdrawal.channel in channels
      chan = channels[withdrawal.channel]
      assert isinstance(chan.kind, NativeChannel)
      assert chan.kind.note_set is not None
      ```

  2. Ensure all inputs are spendable in the channel note set.
      ```python
      ledger.sets[chan.kind.note_set].assert_spendable(withdrawal.inputs)
      ```

  3. Validate ownership over the withdrawn notes and balance.
      ```python
      assert ledger.sets[chan.kind.note_set].verify_transfer(withdrawal.inputs,
                                                             withdrawal.outputs,
                                                             0,  # a withdrawal balances exactly
                                                             withdrawal.commitment_root,
                                                             mantle_txhash_fr,
                                                             proof)
      ```

#### Execution

  *Given*

```python
withdrawal: ChannelWithdraw

channels: dict[ChannelId, ChannelState]
ledger: Ledger
block_slot: Slot
```

  *Execute*

Keep the withdrawal in the [`pending_withdrawals`](bedrock-mantle-specification.md#ledger) of the ledger until its due slot.

```python
ledger.pending_withdrawals.append((block_slot + WITHDRAW_DELAY,
                                   channels[withdrawal.channel].kind.note_set,
                                   withdrawal.inputs,
                                   withdrawal.outputs))
```

At the start of every block, before its transactions, every pending withdrawal whose due slot is reached is applied if its inputs are still unspent, and dropped otherwise, in the order the withdrawals were posted (see [Block Execution](bedrock-block-construction.md#block-execution)). That order is not the order of the due slots, since an SDP withdrawal can fall due after a channel withdrawal posted later, and it sets the order in which the outputs are appended to the ledger note set:

```python
def release_withdrawals(block_slot: Slot):
    pending = []
    for (due, note_set, inputs, outputs) in ledger.pending_withdrawals:
        if due > block_slot:
            pending.append((due, note_set, inputs, outputs))
            continue
        unspent = True
        for note_nullifier in inputs:
            if note_nullifier in ledger.sets[note_set].nullifiers:
                unspent = False
        if unspent:
            ledger.sets[note_set].execute_spending(inputs)
            ledger.sets[LEDGER_SET].execute_adding(outputs)
    ledger.pending_withdrawals = pending
```
