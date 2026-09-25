# MANTLE

| Field | Value |
| --- | --- |
| Name | Mantle |
| Slug | 98 |
| Status | raw |
| Category | Informational |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors | David Rusu <davidrusu@logos.co>, Filip Dimitrijevic <filip@logos.co>, Marcin Pawlowski <marcin@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/bedrock-v1.1-mantle-specification.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/bedrock-v1.1-mantle-specification.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-v1.1-mantle-specification.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-v1.1-mantle-specification.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revisions History

| **Version** | **Changes** | Date |
| --- | --- | --- |
| 1.1.0 | Initial revision. | 2026-12-01 |
| 1.2.0 | Removed DA references. Removed notions of Sovereignty and Rollups and used Zones for simplicity. Removed Nomos from specifications and DSTs. Added bridging and decentralized sequencing for channels. | 2026-01-01 |
| 1.2.1 | [RFC] Improve Mantle Transaction hash. | 2026-03-25 |
| 1.3.0 | [[RFC] Make Ledger Transaction an Operation](mantle-transaction-encoding/appendices/rfc-make-ledger-transaction-an-operation.md). | 2026-04-02 |
| 1.4.0 | [[RFC] Enforce NoteId uniqueness](mantle-transaction-encoding/appendices/rfc-enforce-noteid-uniqueness.md). | 2026-04-24 |
| 1.5.0 | [[RFC] Simplify Mantle Transaction and Refactor Ledger Operations](mantle-transaction-encoding/appendices/rfc-simplify-mantle-transaction-and-refactor-ledger-operations.md). | 2026-05-06 |
| 1.6.0 | [RFC] Remove Concept of a Session | 2026-06-22 |
| 1.7.0 | Factor out the multi eddsa threshold verification and added a validation step in channel config to check the new config threshold is lower or equal than the number of accredited keys | 2026-06-25 |
| 1.8.0 | [RFC] Update channels to support proof of stake participation and test vectors for OpId and Mantle Transaction Hash | 2026-07-06 |
| 1.9.0 | Update the execution of `CHANNEL_DEPOSIT` to consume the inputs and recreate them in the channel, updating their NoteId avoid replay attacks in case of withdraw after a deposit | 2026-07-27 |
| 1.9.1 | Rename the excess balance left after the mandatory fees into `tx_priority_tip` and convert it back into a `TokenValue` explicitly | 2026-08-05 |
| 1.9.2 | Required checked arithmetic for all token value, balance, gas, and fee computations. | 2026-08-06 |
| 1.10.0| Enforce non empty inputs for every operation not only transfer moving the assertion in the validation of input spendability | 2026-08-11 |
| 1.10.1| [RFC] One canonical encoding for `ServiceType` and `Locator`: `ServiceType` is its one-byte discriminant and `Locator` is the multiaddr binary form. Added a `declaration_id` test vector | 2026-08-14 |
| 1.10.2| Precise the state validation reads: the Operations of a Mantle Transaction are validated and executed one after the other in the order they appear, each against the state the preceding ones left, and a Mantle Transaction against the state the transactions preceding it in the block left. Accumulated the transaction balance along that pass, replacing `get_transaction_balance` | 2026-08-24 |
| 1.11.0 | Track the configuration lineage of a channel: `ChannelState` gains `config_tip_hash` and the `CHANNEL_CONFIG` payload carries the `parent` configuration it extends, ordering configurations and preventing their replay | 2026-08-27 |
| 1.11.1 | Renamed locked notes into service notes: `service_notes`, `ServiceNote` and `service_note_id` replace their locked counterparts, and the note kind is named after the role it plays rather than after the state it is left in | 2026-08-27 |
| 1.12.0 | Specified the `SDP_ACTIVE` execution effects, matching the implementation: `active` is set to the epoch of the including block, and a message the activity logic rejects makes the Operation invalid. Set `withdraw_at` to `current_epoch + 2`, the epoch at which the node stops providing the service, and removed declarations at `withdraw_at` | 2026-09-02 |
| 1.13.0 | Removed the `None` case of `op_proofs`, every Operation carrying exactly one proof. A `CHANNEL_CONFIG` creating a channel is verified against a threshold of `0` and its proof carries no signature and no index. Execution Gas is derived from the Operation and the state it is validated against, the thresholds pricing the channel Operations being the ones held in the channel state | 2026-08-31 |
| 1.14.0 | Moved SDP declaration removal to `withdraw_at + 1`; the last served epoch's reward is paid in the same first block, before removal | 2026-09-11 |
| 1.15.0 | Add the `CLAIM_POW_REWARD` Operation and the proof of work state it is validated against; the reward pool and the difficulty controllers are specified in [Proof of Work](proof-of-work.md) | 2026-09-08 |
| 1.16.0 | Channel notes move only with their holder's authorization, checked on challenge: `CHANNEL_INSCRIBE` moves notes against a bond, `CHANNEL_TRANSFER` and `transfer_threshold` are removed, every channel note leaves its channel through `CHANNEL_WITHDRAW`, after a delay and without the sequencers, and the `CHANNEL_CHALLENGE` and `CHANNEL_ANSWER` Operations are added. The channel protocol is specified in [Channels](channels.md), and pending inscriptions and withdrawals are resolved at the start of each block by the [Channel Resolution](#channel-resolution). A `ZkSignature` over notes lists the distinct keys of the notes, so its 32-key limit bounds owners rather than notes | 2026-09-18 |

# Introduction

Mantle is a foundational element of Bedrock, designed to provide a minimal and efficient execution layer that connects together Bedrock Services in order to provide the necessary functionality for Zones. It can be viewed as the system call interface of Bedrock, exposing a safe and constrained set of Operations to interact with lower-level Bedrock services, similar to syscalls in an operating system.

Mantle Transactions provide Operations for Zones and blockchain Services to interact with Bedrock. For example, a Zone sequencer posting an update to Bedrock, or a node operator declaring its participation in the Blend Network, would be done through the corresponding Operations within a Mantle Transaction.

Mantle manages assets using a note-based ledger that follows an UTXO model. Each Mantle Transaction can include Transfer Operation, and any excess balance serves as the fee payment.

# Overview

## Mantle Transaction

The features of the Logos Blockchain are exposed through Mantle Transactions. Each transaction can contain zero or more **Operations**. Mantle Transactions enable users to execute multiple Operations atomically: the Operations are applied one after the other in the order they appear, and either all of them take effect or none does.

## Mantle Operations

Logos Blockchain features are exposed through Mantle Operations, which can be combined in a single Mantle Transaction and executed atomically. These Operations enable transfers and functions such as on-chain data posting, Cross-Zone interactions, SDP interaction, and leader reward claims.

## Mantle Ledger

The Mantle Ledger enables asset transfers using a transparent UTXO model. While a Transfer Operation can consume more tokens than it creates, the Mantle Transaction excess balance must exactly pay for the fees. The ledger tracks regular notes, service notes (collateral for service declarations) and channel notes (channel bridge funds, moved inside their channel only with their holder's authorization and taken out of it only by a withdrawal, after a delay). A pending inscription locks the notes it created and the notes bonded for it, until it is final.

## Transaction Fees

Mantle Transaction fees are derived from a gas model. The Logos Blockchain has two different gas markets, accounting for permanent data storage, and execution costs. Each Operation has an associated Execution Gas cost. Users can build unbalanced Mantle Transactions to tip the leaders and incentivize the network to include their transaction.

| Gas Market | Charged On | Pricing Basis |
| --- | --- | --- |
| Execution Gas | Operations | Fixed per Operation |
| Permanent Storage Gas | Signed Mantle Transaction | Proportional to encoded size |

# Mantle Transaction

Mantle Transactions form the core of Mantle, enabling users to combine multiple Operations to access different functions. Each transaction contains zero or more Operations. The system executes the Operations atomically, while using the Mantle Transaction's excess balance, calculated as the difference between the consumed and created value, as the fee payment.

```python
class MantleTx:
    ops: list[Op]

class Op:
    opcode: byte
    payload: bytes

def mantle_txhash(tx: MantleTx) -> Hash:
    tx_bytes = encode(tx)

    h = Hasher()
    h.update(b"MANTLE_TXHASH_V1")
    h.update(tx_bytes)

    return h.digest()
```

The [hash function used](common-cryptographic-components.md), as well as other cryptographic primitives like ZK proofs and signature schemes, are described in [Common Cryptographic Components](common-cryptographic-components.md).

## Mantle Transaction Hash

A Mantle Transaction must include all relevant signatures and proofs for each Operation.

```python
class SignedMantleTx:
    tx: MantleTx
    op_proofs: list[OpProof] # each Op has exactly 1 associated proof
```

Each proof (op proof and signature) must be cryptographically bound to the `MantleTx` through the `mantle_txhash` to prevent replay attacks. This binding is achieved by including the `MantleTx` hash reduced modulo $`p`$ as a public input in every ZK proof.
```python
mantle_txhash_fr = FiniteField(mantle_txhash, byte_order="little", modulus = p)
```

  `mantle_txhash` is a classical 256-bit hash digest and must be reduced to a field element before being passed to any ZkHasher or used as a ZK public input. We apply a direct modular reduction mod $`p`$ (via `FiniteField(..., modulus=p)`). Since $`p \approx 2^{254}`$, the reduction is slightly non-uniform. This is inconsequential in practice as the collision probability remains around $`2^{-254}`$, and proof binding is derived from the collision-resistance of the classic hash, not from uniformity over $`F_p`$.

## Arithmetic

All arithmetic in this specification is checked. Every addition, subtraction, and multiplication over token values, balances, gas amounts, and fees is performed on the stated integer type, and a Mantle Transaction is invalid if any intermediate or final result cannot be represented in that type; results must never silently wrap around or saturate. Token value computations use the precision of `TokenValue` (see the [Notes](#notes) section). The transaction balance uses a signed 128-bit integer: it can be legitimately negative before the fee check.

The pseudocode expresses these checks with the following helpers; a failed check makes the Mantle Transaction invalid:

```python
UINT64_MAX = 2**64 - 1
INT128_MIN = -2**127
INT128_MAX = 2**127 - 1

def checked_uint64(value: int) -> TokenValue:
        assert 0 <= value <= UINT64_MAX
        return value

def checked_int128(value: int) -> int:
        assert INT128_MIN <= value <= INT128_MAX
        return value
```

The proof of work difficulty updates are the exception to these bounds; they are specified in [Puzzle Target](proof-of-work.md#puzzle-target).

## Mantle Transaction Fee

The transaction mandatory fee is a sum of two components: the multiplication of the total Execution Gas by the `execution_base_fee`, and the total size of the encoded signed Mantle Transaction multiplied by the `permanent_storage_gas_price`. The execution base fee and the permanent storage gas price are protocol-determined values that are the same for every Mantle Transaction in a block. They are derived following [[Execution Market](execution-market.md) and [Storage Markets](storage-markets.md).

```python
def mandatory_fees(signed_tx: SignedMantleTx,
                   ledger: Ledger,
                   channels: dict[ChannelId, ChannelState],
                   permanent_storage_gas_price: TokenValue, # Given by Storage Market
                   execution_gas_base_price: TokenValue) -> uint64:  # Given by Execution Market
    mantle_tx = signed_tx.tx
    permanent_storage_fees = checked_uint64(len(encode(signed_tx)) * permanent_storage_gas_price)
    tx_execution_gas = 0

    for op in mantle_tx.ops:
        # Compute how much execution gas of this operation as defined
        # in the gas determination Appendix, against the state this
        # Operation is validated against
        tx_execution_gas += execution_gas(op, ledger, channels)
    execution_base_fees = checked_uint64(tx_execution_gas * execution_gas_base_price)

    return checked_uint64(execution_base_fees + permanent_storage_fees)
```

The Execution Gas of an Operation is deterministically derived from that Operation and the state it is validated against.

If the Mantle Transaction is unbalanced (meaning that the Transaction consume more value than it creates) and that the leftover balance cover more than the mandatory fees, the remaining is treated as execution tip fees.

## **Validation**

*Given*

```python
signed_tx = SignedMantleTx(
    tx=MantleTx(ops),
    op_proofs
)

permanent_storage_gas_price: TokenValue # Given by Storage Market
execution_gas_base_price: TokenValue    # Given by Execution Market
```

The state validation reads is not a fixed snapshot: it advances as the block is processed. A Mantle Transaction is validated against the state left by the Mantle Transactions preceding it in the block, as defined in [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation), and validation and execution then follow one another Operation by Operation, in the order the Operations appear: the Operation at index `i` is validated against the state the Operations at indices `0` to `i-1` left, then executed to produce the state the Operation at index `i+1` is validated against. This is what the `ledger`, `channels`, `pending`, `withdrawals`, `service_notes`, `declarations` and `voucher_nullifier_set` given to each Operation below denote.

Atomicity is what a failed check means, not simultaneity. If any of the checks below fails, the whole Mantle Transaction is invalid: none of its Operations takes effect, whether or not it was reached. An invalid Mantle Transaction is never skipped over either, the block including it being invalid and nothing of that block being executed.

Mantle validators will ensure the following:

1. We have exactly one proof for each Operation, of the variant that Operation requires.
    ```python
    assert len(op_proofs) == len(ops)
    ```

2. Each Operation is valid, and takes effect before the next one is validated. The transaction balance is accumulated over the same pass, so a `TRANSFER` consuming a note an earlier Operation created contributes that note's value like any other.
    ```python
    tx_balance = 0   # Signed 128-bit accumulator: the balance can be legitimately negative
    for op, op_proof in zip(ops, op_proofs):
        assert op.opcode in MANTLE_OPCODES
        validate_mantle_op(mantle_txhash(tx), op.opcode, op.payload, op_proof)
        if op.opcode == TRANSFER:
            for inp in op.inputs:
                tx_balance = checked_int128(tx_balance + get_value_from_note_id(inp))
            for out in op.outputs:
                tx_balance = checked_int128(tx_balance - out.value)
        execute_mantle_op(op.opcode, op.payload)

    def validate_mantle_op(txhash, opcode, payload, op_proof):
        if opcode == CHANNEL_INSCRIBE:
            validate_channel_inscribe(txhash, payload, op_proof)
        # elif opcode == ...
        #    ...

    def execute_mantle_op(opcode, payload):
        if opcode == CHANNEL_INSCRIBE:
            execute_channel_inscribe(payload)
        # elif opcode == ...
        #    ...
    ```

3. The Mantle Transaction excess balance pays at least the mandatory fees.
    ```python
    tx_mandatory_fee = mandatory_fees(signed_tx,                        # uint64
                                      permanent_storage_gas_price,
                                      execution_gas_base_price)
    assert tx_mandatory_fee <= tx_balance
    tx_priority_tip = checked_uint64(tx_balance - tx_mandatory_fee)
    ```

## Execution

*Given*

```python
SignedMantleTx(
    tx=MantleTx(ops),
    op_proofs
)
```

Mantle Validators execute each Operation in `ops` according to its opcode, in the order the Operations appear and along the state progression [Validation](#validation) defines. The subsections below define, for each opcode, what validating and executing an Operation amount to.

# Operations

## Opcodes

| **Operation** | **Opcode** | **Description** |
| --- | --- | --- |
| TRANSFER | 0x00 | Consume and create notes. |
| *RESERVED* | *0x01 - 0x0F* |  |
| CHANNEL_CONFIG | 0x10 | Configure a channel |
| CHANNEL_INSCRIBE | 0x11 | Write a message permanently onto Mantle. |
| CHANNEL_DEPOSIT | 0x12 | Deposit assets into a channel |
| CHANNEL_WITHDRAW | 0x13 | Take notes out of a channel after a delay, without its sequencers |
| CHANNEL_CHALLENGE | 0x14 | Challenge a pending inscription |
| CHANNEL_ANSWER | 0x15 | Answer a challenge with the accounting of the inscription |
| *RESERVED* | *0x16 - 0x1F* |  |
| SDP_DECLARE | 0x20 | Declare intention to participate as a node in a Bedrock Service, locking funds as collateral. |
| SDP_WITHDRAW | 0x21 | Withdraw participation from a Bedrock Service, unlocking your funds in the process. |
| SDP_ACTIVE | 0x22 | Signal that you are still an active participant of a Bedrock Service. |
| *RESERVED* | *0x23 - 0x2F* |  |
| LEADER_CLAIM | 0x30 | Claim leader reward anonymously. |
| *RESERVED* | *0x31 - 0x3F* |  |
| CLAIM_POW_REWARD | 0x40 | Claim a reward from the pow reward pool. |
| *RESERVED* | *0x41 - 0xFF* |  |

## Channel Operations

These Operations implement [Channels](channels.md), which specifies how a channel orders its messages, how its sequencers take turns, and how the notes bridged into it move. Validation uses its `round_robin`, `auth_msg` and `required_collateral` functions and its [parameters](channels.md#parameters). An inscription that moves notes stays pending until it is final or lost, and a withdrawal waits for its delay; the [Channel Resolution](#channel-resolution) decides both at the start of each block.

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

def default_channel(block_slot: Slot, keys: list[Ed25519PublicKey]) -> ChannelState:
    return ChannelState(
        tip_hash = ZERO,
        config_tip_hash = ZERO,
        tip_slot = block_slot,
        accredited_keys = keys,
        tip_sequencer = 0,
        tip_sequencer_starting_slot = block_slot,
        posting_timeframe = 0,
        posting_timeout = 0,
        configuration_threshold = 1)
```

Note that the user chooses the ChannelId mapping to the ChannelState (but it’s restricted to 32 bytes). We don't currently impose restrictions on it, but we may do so in the future to prevent undesirable behaviors.

Bridging adds the following state:

```python
pending: dict[OpId, PendingInscription]   # inscriptions that moved notes and are not final, in posting order
withdrawals: dict[OpId, Withdrawal]       # withdrawals waiting for their delay, by the OpId of their CHANNEL_WITHDRAW
due: SortedMap[Slot, list[OpId]]          # pending inscriptions and withdrawals to resolve, by slot;
                                          # a block pops the entries due from the front

class ConsumedInput:
    note_id: NoteId                 # the steps of an answer name it, once it has left the ledger
    note: Note                      # re-created if the inscription is undone
    locked_by: OpId | None          # the pending inscription that created the note, if it was locked
    withdrawal: OpId | None         # the withdrawal that named the note, if any: the re-created note inherits it
    withdrawal_due: Slot | None     # its due, kept for the case where the withdrawal was dropped as empty

class PendingInscription:
    channel: ChannelId
    deadline: Slot                   # end of the challenge window; a challenge extends it
                                     # by RESPONSE_WINDOW, and a valid answer brings it to the next block
    inputs: list[ConsumedInput]
    outputs: list[Note]              # the notes it created
    created: list[NoteId]            # those of them still on the ledger, locked until it is final:
                                     # a note a later inscription consumes leaves the list
    bond: list[NoteId]               # locked until it is final, forfeited if it is lost
    required: TokenValue             # collateral the inscription puts at risk
    depends_on: set[OpId]            # the pending inscriptions that created its locked inputs
    dependents: list[OpId]           # the pending inscriptions that consumed a note it created, in posting order
    status: NOT_CHALLENGED | CHALLENGED | PROVEN   # challenged at most once; proven, it is final at the next block
    challenge: list[NoteId]          # the challenger's bond, while CHALLENGED
    undone: bool                     # undone with a lost inscription it depended on, and still answerable

class Withdrawal:
    inputs: list[NoteId]             # the notes leaving the channel; one an inscription consumes before due leaves the list
    due: Slot                        # end of its delay
```

### CHANNEL_INSCRIBE

Write a message to a channel with the message data being permanently stored on the Logos Blockchain, and optionally move the channel's notes.

#### Payload

```python
class Inscribe:
    channel: ChannelId       # 32 bytes Channel being written to
    inscription : bytes      # Message to be written on the blockchain
    parent: hash             # Previous message in the channel
    signer: Ed25519PublicKey # Identity of message sender
    inputs: list[NoteId]     # notes of the channel to consume, locked or not; empty when the inscription moves nothing
    outputs: list[Note]      # notes to create in the channel
    bond: list[NoteId]       # notes bonded for the moved notes; empty when the inscription moves nothing
```

An inscription moves notes when `inputs` is non-empty: it consumes them and creates the `outputs` in the channel, locked until the inscription is final (see [Moving Notes](channels.md#moving-notes)). An input may itself be locked, which makes the inscription depend on the pending inscription that created it. The `bond` is locked until the inscription is final, and forfeited if it is lost.

#### Proof

  An inscription is signed by its sequencer with an Ed25519 signature. When it moves notes, it also proves the ownership of its bond notes using a [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

```python
class InscribeProof:
    bond_sig: ZkSignature | None    # present when the inscription moves notes
    signer_sig: Ed25519Signature
```

#### Execution Gas

  Channel Inscribe Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_INSCRIBE_GAS`, plus `EXECUTION_CHANNEL_BOND_GAS` when they move notes. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: hash
mantle_txhash: zkhash
msg: Inscribe
proof: InscribeProof

channels: dict[ChannelId, ChannelState]
withdrawals: dict[OpId, Withdrawal]
execution_gas_base_price: TokenValue    # Given by Execution Market
permanent_storage_gas_price: TokenValue # Given by Storage Market
ledger: Ledger
block_slot: Slot
```
 
  *Validate*

  1. Ensure the signer is the one authorized to write to the channel and that the message continues the channel sequence. A channel that does not exist is created upon execution: its first message carries a `parent` of `ZERO`, and it holds no note.
      ```python
      if msg.channel in channels:
          chan = channels[msg.channel]
          current_sequencer_index = round_robin(block_slot, chan)[0]

          # Ensure the signer is the one authorized to write to the channel
          assert msg.signer == chan.accredited_keys[current_sequencer_index]

          # Ensure message is continuing the channel sequence
          assert msg.parent == chan.tip_hash
      else:
          # Channel will be created automatically upon execution
          # Ensure that this message is the genesis message (parent == ZERO)
          assert msg.parent == ZERO
          # A channel that does not exist holds no note
          assert not msg.inputs
      ```

  2. Ensure the msg signer signature.
      ```python
      assert Ed25519_verify(txhash, msg.signer, proof.signer_sig)
      ```

  3. An inscription that moves nothing creates no note and bonds none, and its validation ends here.
      ```python
      if not msg.inputs:
          assert not msg.outputs and not msg.bond
          return
      ```

  4. Ensure the inputs are notes of the channel, locked or not, and that no withdrawal past its delay names them.
      ```python
      ledger.assert_spendable(msg.inputs, msg.channel)
      ```

  5. Ensure the outputs are valid.
      ```python
      ledger.assert_valid_output(msg.outputs)
      ```

  6. Ensure value is conserved.
      ```python
      input_amount = checked_uint64(sum(ledger.get_note(note_id).value for note_id in msg.inputs))
      output_amount = checked_uint64(sum(output.value for output in msg.outputs))
      assert input_amount == output_amount
      ```

  7. Ensure the bond covers the collateral the inscription puts at risk, and validate ownership over the bond notes. A bond is made of unlocked channel notes of the channel, none of which the inscription consumes.
      ```python
      ledger.assert_bond(msg.bond, msg.channel)
      assert not set(msg.bond) & set(msg.inputs)
      bond_notes = [ledger.get_note(note_id) for note_id in msg.bond]
      assert checked_uint64(sum(note.value for note in bond_notes)) >= required_collateral(msg.inputs)
      assert ZkSignature_verify(mantle_txhash, proof.bond_sig, keys_of(bond_notes))
      ```

#### Execution

  *Given*

```python
msg: Inscribe

channels: dict[ChannelId, ChannelState]
pending: dict[OpId, PendingInscription]
withdrawals: dict[OpId, Withdrawal]
due: SortedMap[Slot, list[OpId]]
execution_gas_base_price: TokenValue    # Given by Execution Market
permanent_storage_gas_price: TokenValue # Given by Storage Market
ledger: Ledger
block_slot: Slot
```

  *Execute*

  1. If the channel does not exist, create it just-in-time.
      ```python
      if msg.channel not in channels:
          channels[msg.channel] = default_channel(block_slot, [msg.signer])
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

  4. If the inscription moves notes, move them and record the inscription as pending.
      ```python
      if msg.inputs:
          op_id = derive_op_id(msg)
          # The requirement reads the inputs, so it is computed before they are consumed
          required = required_collateral(msg.inputs)
          inputs = []
          for note_id in msg.inputs:
              note = ledger.channel_notes[note_id]
              inputs.append(ConsumedInput(
                  note_id=note_id, note=ledger.get_note(note_id), locked_by=note.locked_by,
                  withdrawal=note.withdrawal,
                  withdrawal_due=None if note.withdrawal is None else withdrawals[note.withdrawal].due))

          # Depend on the creator of each locked input, which drops the note from its created list
          depends_on = {consumed.locked_by for consumed in inputs if consumed.locked_by is not None}
          for consumed in inputs:
              if consumed.locked_by is not None:
                  pending[consumed.locked_by].created.remove(consumed.note_id)
          for dep in depends_on:
              pending[dep].dependents.append(op_id)

          # Consume the inputs, create the outputs, and lock them with the bond
          ledger.execute_spending(msg.inputs)
          created = ledger.execute_adding(op_id, msg.outputs, msg.channel)
          ledger.lock(created, op_id, created=True)
          ledger.lock(msg.bond, op_id, created=False)

          pending[op_id] = PendingInscription(
              channel=msg.channel, deadline=block_slot + CHALLENGE_WINDOW,
              inputs=inputs, outputs=msg.outputs, created=created, bond=msg.bond,
              required=required, depends_on=depends_on, dependents=[],
              status=NOT_CHALLENGED, challenge=[], undone=False)
          due.setdefault(block_slot + CHALLENGE_WINDOW, []).append(op_id)
      ```

#### Example

  Alice and Bob each pay Carol 25 out of a channel note of 50. Each signs an [authorization](channels.md#authorizations) of their own note and hands it to the sequencer of Zone A, which applies both in one inscription, bonding a channel note of its own:

```python
alice_auth = ZkSignature_sign(auth_msg([alice_note_id],
                                       [Note(25, carol_pk), Note(25, alice_pk)]), [alice_sk])
bob_auth = ZkSignature_sign(auth_msg([bob_note_id],
                                     [Note(25, carol_pk), Note(25, bob_pk)]), [bob_sk])

# Build the inscription
payment = Inscribe(
    channel=ZONE_A,
    inscription=b"<zone state transition paying Carol>",
    parent=zone_a_tip,
    signer=sequencer_pk,
    inputs=[alice_note_id, bob_note_id],
    outputs=[Note(25, carol_pk), Note(25, alice_pk),    # Alice's authorization
             Note(25, carol_pk), Note(25, bob_pk)],     # Bob's authorization
    bond=[sequencer_bond_note_id]    # worth at least required_collateral(inputs)
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[sequencer_funds], outputs=[<change_note>])

# Wrap it in a transaction
tx = MantleTx(
    ops=[Op(opcode=CHANNEL_INSCRIBE, payload=encode(payment)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)
txhash = mantle_txhash(tx)

# Sign the transaction
signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[InscribeProof(bond_sig=ZkSignature_sign(txhash, [sequencer_zk_sk]),
                             signer_sig=Ed25519_sign(txhash, sequencer_sk)),
               transfer.prove(sequencer_zk_sk)]
)

# Send the transaction to the mempool
mempool.push(signed_tx)
```

### CHANNEL_CONFIG

Overwrite the configuration of a channel.

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

A Channel Config is authorized by a threshold of the channel's accredited keys using [Multiple Ed25519 Signatures Verification](#multiple-ed25519-signatures-verification).

```python
class ChannelConfigOpProof:
    signatures: list[Ed25519Signature] # signatures from configuration_threshold
    indexes: list[u16]  # signatures of accredited keys with their index.
                        # indexes must be ordered from smallest to
                        # biggest without duplication
```

#### Execution Gas

  Channel Config Operations have a linear Execution Gas cost equal to `EXECUTION_CHANNEL_CONFIG_GAS * configuration_threshold`, where `configuration_threshold` is the one held in the channel state, and `0` for a channel that does not exist yet. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: zkhash
config: ChannelConfig
proof: ChannelConfigOpProof
channels: dict[ChannelId, ChannelState]
```

  *Validate*

```python
assert config.configuration_threshold > 0
assert len(config.keys) > 0
assert len(config.keys) < 2^16
# The configuration threshold must be reachable with the accredited keys,
# otherwise the channel would be locked out of any future reconfiguration
assert config.configuration_threshold <= len(config.keys)

if config.channel in channels:
    chan = channels[config.channel]

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
    # Channel will be created automatically upon execution
    # Ensure that this configuration is the genesis configuration
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
block_slot: Slot
```

  *Execute*

  1. If the channel does not exist, create it just-in-time.

      ```python
      if config.channel not in channels:
          channels[config.channel] = default_channel(block_slot, config.keys)
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

#### Example

  Suppose the unique sequencer of Zone A wants to add a key to the list of accredited keys:

```python
# Given a key to add and the current configuration tip of the channel
new_sequencer_pk: Ed25519PublicKey
zone_a_config_tip: hash

# The unique sequencer encodes the update and builds the payload
config = ChannelConfig(
    channel=ZONE_A,
    parent=zone_a_config_tip,
    keys=[old_sequencer_pk, new_sequencer_pk],
    posting_timeframe = 5000,
    posting_timeout = 500,
    configuration_threshold = 2
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[old_sequencer_funds], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=CHANNEL_CONFIG, payload=encode(config)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[[[Ed25519_sign(mantle_txhash(tx), old_sequencer_sk)], [0]],
               transfer.prove(old_sequencer_sk)]
)
```

### CHANNEL_DEPOSIT

Deposit notes to a channel. The inputs are consumed and re-created as channel notes under a new `NoteId`, which resets their ageing and prevents the deposit from being replayed once the note has left the channel.

#### Payload

```python
class ChannelDeposit:
    channel: ChannelId
    inputs: list[NoteId]  # the notes to be consumed and re-created as channel notes
    metadata: bytes
```

#### Proof

  A Channel Deposit proves the ownership of the notes being consumed using a [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

```python
ZkSignature
```

#### Execution Gas

  Channel Deposit Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_DEPOSIT_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash # zkhash of mantle tx containing this ledger tx
deposit: ChannelDeposit
deposit_proof: ZkSignature

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Validate*

  1. Verify that the channel exist
      ```python
      assert deposit.channel in channels
      ```

  2. Ensure all inputs are spendable, which excludes channel notes.
      ```python
      ledger.assert_spendable(deposit.inputs)
      ```

  3. Validate ownership over deposited notes.
      ```python
      input_notes = [ledger[input_note_id] for input_note_id in deposit.inputs]
      assert ZkSignature_verify(mantle_txhash, deposit_proof, keys_of(input_notes))
      ```

#### Execution

  *Given*

```python
deposit: ChannelDeposit

channels: dict[ChannelId, ChannelState]
ledger: Ledger
```

  *Execute*

Consume the inputs and create the same Note with new NoteId as channel notes owned by the channel.

```python
# read the notes that are being moved into the channel
notes_to_add = [ledger[input_note_id] for input_note_id in deposit.inputs]

# consume the inputs, which are regular notes and not registered in channel_notes
ledger.execute_spending(deposit.inputs)

# re-create them as channel notes under a new NoteId
deposit_id = derive_op_id(deposit)
ledger.execute_adding(deposit_id, notes_to_add, deposit.channel)
```

#### Example

  Suppose Alice wants to make a deposit of 50 tokens on Zone A.

```python
# Alice encodes her deposit
deposit = ChannelDeposit(
    channel=ZONE_A,
    inputs=[alice_deposit_note_id]    # This is a note of 50 tokens
    metadata=b"deposit to address: 0x..."
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[Alice_funds], outputs=[<change_note>])


tx = MantleTx(
    ops=[Op(opcode=CHANNEL_DEPOSIT, payload=encode(deposit)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[deposit.prove(Alice_sk), transfer.prove(Alice_sk)],
)
```

A Zone that credits a deposit in its own state must be sure the deposit really lands on-chain. If the Zone reflects the deposit through a `CHANNEL_INSCRIBE` posted in a separate Mantle Transaction, a reorganization can reorder the two so that the inscription is included while the deposit is not, leaving the Zone crediting funds it never received. Two options avoid this:

- Wait for the deposit to be finalized before interpreting it, at the cost of the finalization delay.
- Make the inscription conditional on the deposit, by consuming the deposited note in the inscription's own `inputs`. The inscription is then valid only if the deposited note exists, and a reorganization cannot keep one without the other. This removes the waiting period entirely.

The second option resets the ageing of the value, since an inscription that moves notes consumes its inputs and creates new notes. A `CHANNEL_DEPOSIT` resets ageing for the same reason, and so does a withdrawal, which re-creates the notes it takes out.

### CHANNEL_WITHDRAW

Take notes out of a channel without its sequencers, the only way out of a channel: the ledger re-creates each as an ordinary note, under the same key, at the first moment it is unlocked once `WITHDRAW_DELAY` has passed (see [Withdrawals](channels.md#withdrawals)). Until then an inscription of the channel may still consume them, as if they were not withdrawn.

#### Payload

```python
class ChannelWithdraw:
    channel: ChannelId
    inputs: list[NoteId]  # notes of the channel to take out
```

#### Proof

  A Channel Withdraw proves the ownership of the input notes using a [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

```python
ZkSignature
```

#### Execution Gas

  Channel Withdraw Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_WITHDRAW_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
withdraw: ChannelWithdraw
withdraw_proof: ZkSignature

channels: dict[ChannelId, ChannelState]
ledger: Ledger
```

  *Validate*

  1. Verify that the channel exists.
      ```python
      assert withdraw.channel in channels
      ```

  2. Ensure the inputs are distinct channel notes of the channel that no withdrawal names yet, unlocked or locked as the outputs of a pending inscription. A bonded note cannot be named until its inscription releases it.
      ```python
      assert len(withdraw.inputs) > 0
      assert len(withdraw.inputs) == len(set(withdraw.inputs))
      for note_id in withdraw.inputs:
          assert ledger.is_unspent(note_id)
          assert note_id in ledger.channel_notes
          note = ledger.channel_notes[note_id]
          assert note.channel == withdraw.channel
          assert note.withdrawal is None
          assert note.locked_by is None or note.created
      ```

  3. Validate ownership over the input notes.
      ```python
      input_notes = [ledger.get_note(note_id) for note_id in withdraw.inputs]
      assert ZkSignature_verify(mantle_txhash, withdraw_proof, keys_of(input_notes))
      ```

#### Execution

  *Given*

```python
withdraw: ChannelWithdraw

withdrawals: dict[OpId, Withdrawal]
due: SortedMap[Slot, list[OpId]]
ledger: Ledger
block_slot: Slot
```

  *Execute*

  Record the withdrawal and mark its notes. From now on no inscription may bond them. For `WITHDRAW_DELAY` slots an inscription of the channel may still consume them, and a note it consumes leaves the withdrawal, coming back to it only if that inscription is undone. Once the delay has passed no inscription may consume them, and the [Channel Resolution](#channel-resolution) takes each out at the first moment it is unlocked, before the transactions of the block.

```python
op_id = derive_op_id(withdraw)
withdrawals[op_id] = Withdrawal(inputs=withdraw.inputs, due=block_slot + WITHDRAW_DELAY)
for note_id in withdraw.inputs:
    ledger.channel_notes[note_id].withdrawal = op_id
due.setdefault(block_slot + WITHDRAW_DELAY, []).append(op_id)
```

#### Example

  The sequencers of Zone A ignore Alice. She takes her note out:

```python
withdraw = ChannelWithdraw(
    channel=ZONE_A,
    inputs=[alice_channel_note_id]
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[alice_funds], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=CHANNEL_WITHDRAW, payload=encode(withdraw)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[withdraw.prove(alice_sk), transfer.prove(alice_sk)],
)
```

### CHANNEL_CHALLENGE

Challenge a [pending inscription](channels.md#moving-notes).

#### Payload

```python
class ChannelChallenge:
    inscription: OpId    # the challenged inscription
    bond: list[NoteId]   # the challenger's bond
```

#### Proof

  A Channel Challenge proves the ownership of the bond notes using a [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

```python
ZkSignature
```

#### Execution Gas

  Channel Challenge Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_CHALLENGE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
challenge: ChannelChallenge
challenge_proof: ZkSignature

pending: dict[OpId, PendingInscription]
withdrawals: dict[OpId, Withdrawal]
ledger: Ledger
block_slot: Slot
```

  *Validate*

  1. Find the pending inscription and ensure it is in its challenge window and not challenged yet. An inscription is challenged at most once: a proven one cannot be challenged again, and is final at the next block whatever happens.
      ```python
      assert challenge.inscription in pending
      challenged_inscription = pending[challenge.inscription]
      assert challenged_inscription.status == NOT_CHALLENGED
      assert block_slot < challenged_inscription.deadline
      ```

  2. Ensure the bond is made of unlocked channel notes of the channel, worth the collateral the inscription put at risk.
      ```python
      ledger.assert_bond(challenge.bond, challenged_inscription.channel)
      bond_notes = [ledger.get_note(note_id) for note_id in challenge.bond]
      assert checked_uint64(sum(note.value for note in bond_notes)) >= challenged_inscription.required
      ```

  3. Validate ownership over the bond notes.
      ```python
      assert ZkSignature_verify(mantle_txhash, challenge_proof, keys_of(bond_notes))
      ```

#### Execution

  *Given*

```python
challenge: ChannelChallenge

pending: dict[OpId, PendingInscription]
due: SortedMap[Slot, list[OpId]]
ledger: Ledger
```

  *Execute*

  Lock the bond and open the challenge, which extends the deadline of the inscription by the response window.

```python
challenged_inscription = pending[challenge.inscription]
ledger.lock(challenge.bond, challenge.inscription, created=False)
challenged_inscription.status = CHALLENGED
challenged_inscription.challenge = challenge.bond
challenged_inscription.deadline += RESPONSE_WINDOW
due.setdefault(challenged_inscription.deadline, []).append(challenge.inscription)
```

#### Example

  Dave watches Zone A, cannot find the authorizations backing the `payment` inscription of the [`CHANNEL_INSCRIBE` example](#channel_inscribe), and challenges it. He holds no channel note of Zone A, so he deposits one and bonds it in the same Mantle Transaction. The Operations of a transaction execute in order, each against the state the preceding ones left, so the challenge finds the channel note the deposit created, and no inscription can consume it in between:

```python
deposit = ChannelDeposit(
    channel=ZONE_A,
    inputs=[dave_note_id],    # a note worth at least required_collateral(payment.inputs)
    metadata=b""
)

challenge = ChannelChallenge(
    inscription=derive_op_id(payment),
    # the channel note the deposit creates, under Dave's key
    bond=[derive_note_id(derive_op_id(deposit), 0, dave_note)]
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[dave_funds], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=CHANNEL_DEPOSIT, payload=encode(deposit)),
         Op(opcode=CHANNEL_CHALLENGE, payload=encode(challenge)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[deposit.prove(dave_sk), challenge.prove(dave_sk), transfer.prove(dave_sk)],
)
```

### CHANNEL_ANSWER

Answer a challenge with the full accounting of the inscription (see [Challenges and Answers](channels.md#challenges-and-answers)).

#### Payload

```python
class Step:
    inputs: list[NoteId]   # inputs of the inscription, or notes created by earlier steps; at least one
    outputs: list[Note]
    auth: ZkSignature      # the authorization, over auth_msg(inputs, outputs)

class ChannelAnswer:
    inscription: OpId
    steps: list[Step]
```

#### Proof

  An empty proof. The answer carries the authorizations of its steps in its payload, and anyone may post them.

```python
EmptyProof
```

#### Execution Gas

  Channel Answer Operations have a linear Execution Gas cost equal to `EXECUTION_ANSWER_STEP_GAS * len(steps)`: one authorization per step. The step count is encoded on two bytes (see [Mantle Transaction Encoding](mantle-transaction-encoding.md#channel-operations)), so an answer carries at most 65,535 steps and costs at most 65,535 times `EXECUTION_ANSWER_STEP_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
answer: ChannelAnswer

pending: dict[OpId, PendingInscription]
ledger: Ledger
block_slot: Slot
```

  *Validate*

  1. Find the pending inscription and ensure it is under challenge.
      ```python
      assert answer.inscription in pending
      answered_inscription = pending[answer.inscription]
      assert answered_inscription.status == CHALLENGED
      assert block_slot < answered_inscription.deadline
      ```

  2. Ensure the answer holds.
      ```python
      assert answer_holds(answered_inscription, answer)
      ```

`answer_holds` implements the five checks of [Challenges and Answers](channels.md#challenges-and-answers). Its sums are exact: a sum that does not fit a `TokenValue` makes the answer wrong.

```python
def answer_holds(inscription: PendingInscription, answer: ChannelAnswer) -> bool:
    # The notes a step may consume, by identifier: the inputs of the inscription to
    # begin with, then the notes earlier steps created
    available = {consumed_input.note_id: consumed_input.note for consumed_input in inscription.inputs}
    # The identifiers the steps have consumed so far
    consumed = set()
    # The authorizations to verify, with their message and key list
    auths = []

    for step in answer.steps:
        # 1, 2: the step consumes available notes, each consumed once over the answer
        if not step.inputs:
            return False
        notes = []
        for note_id in step.inputs:
            if note_id not in available or note_id in consumed:
                return False
            consumed.add(note_id)
            notes.append(available[note_id])

        # 3: value is conserved and every created note has a valid value
        if not ledger.valid_output(step.outputs):
            return False
        if sum(note.value for note in notes) != sum(output.value for output in step.outputs):
            return False

        # 5: the authorization, over the keys of the consumed notes
        msg = auth_msg(step.inputs, step.outputs)
        auths.append((msg, step.auth, keys_of(notes)))

        # The created notes become available to later steps, under the identifiers of Channels
        for index, note in enumerate(step.outputs):
            available[derive_note_id(msg, index, note)] = note

    # 2: every input of the inscription is consumed by some step
    if any(consumed_input.note_id not in consumed for consumed_input in inscription.inputs):
        return False

    # 4: the created notes left unconsumed, in the order the steps created them, are the outputs
    claims = [note for note_id, note in available.items() if note_id not in consumed]
    if claims != inscription.outputs:
        return False

    # 5: every authorization holds
    return all(ZkSignature_verify(msg, auth, keys) for msg, auth, keys in auths)
```

The authorizations are `ZkSignature`s like the Operation proofs of the block, and a failing one makes the block invalid as a failing proof does, so a validator may verify them in the block's `ZkSignature` batch (see [Batch verification of ZK proofs](bedrock-v1.1-block-construction.md#batch-verification-of-zk-proofs)).

#### Execution

  *Given*

```python
answer: ChannelAnswer

pending: dict[OpId, PendingInscription]
withdrawals: dict[OpId, Withdrawal]
due: SortedMap[Slot, list[OpId]]
ledger: Ledger
block_slot: Slot
```

  *Execute*

  The answer proves the inscription. The challenger's bond forfeits the inscription's `required`, paid to the sequencer as a channel note at the key of the first note of the inscription's bond, under the forfeit identifier of the inscription (see [`forfeit`](#channel-resolution)). The inscription resolves at the start of the next block whatever happens: a proven inscription cannot be challenged again, so nobody can hold it pending. It is final as soon as the inscriptions it depends on are.

```python
answered_inscription = pending[answer.inscription]
sequencer = ledger.get_note(answered_inscription.bond[0]).public_key
forfeit(answered_inscription.challenge, answered_inscription.required, answered_inscription.channel,
        derive_forfeit_id(answer.inscription),
        [Note(value=answered_inscription.required, public_key=sequencer)], block_slot)
answered_inscription.status = PROVEN
answered_inscription.challenge = []
answered_inscription.deadline = block_slot + 1
due.setdefault(block_slot + 1, []).append(answer.inscription)
```

#### Example

  The sequencer answers Dave's challenge of the `payment` inscription of the [`CHANNEL_INSCRIBE` example](#channel_inscribe) with the authorizations Alice and Bob gave it:

```python
answer = ChannelAnswer(
    inscription=derive_op_id(payment),
    steps=[Step(inputs=[alice_note_id],
                outputs=[Note(25, carol_pk), Note(25, alice_pk)],
                auth=alice_auth),
           Step(inputs=[bob_note_id],
                outputs=[Note(25, carol_pk), Note(25, bob_pk)],
                auth=bob_auth)])

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[sequencer_funds], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=CHANNEL_ANSWER, payload=encode(answer)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[EmptyProof(), transfer.prove(sequencer_zk_sk)],
)
```

  Each input is consumed once and each step balances. No step consumes what another created, so the four notes created are all claims, and in the order of the steps they are exactly the inscription's outputs. The answer holds, and Dave's bond pays the inscription's `required` to the key of `sequencer_bond_note_id`.

### Channel Resolution

A `CHANNEL_INSCRIBE` that moves notes is pending until its `deadline` has passed: the end of its challenge window, extended by the response window when it is challenged, and the start of the next block once it is proven. A `CHANNEL_WITHDRAW` waits `WITHDRAW_DELAY` slots. Both are entered in `due` at the slot they become resolvable.

[Block Execution](bedrock-v1.1-block-construction.md#block-execution) resolves, at the start of each block and before its transactions, every entry due at the block's slot or before, in slot order. An entry in `due` is visited once. The cost of a block's resolution is the number of entries due, whatever the gap since the previous block.

An inscription whose deadline has passed while an inscription it depends on is still pending is resolved by that inscription, when it leaves `pending`. A withdrawal whose delay has passed while an input is still locked takes its other inputs out at `due` regardless, and each locked input is resolved by the inscription locking it, when it releases the input or when an undo removes it. A withdrawn note therefore leaves its channel at the first moment it is unlocked once the delay has passed, inside the resolution and before the transactions of the block, so that no inscription can consume or relock it: at its `due` if it is unlocked then, or in the resolution that releases it. A withdrawn note that an inscription consumed during the delay comes back under its withdrawal if that inscription is undone. The note the undo re-creates for it inherits the withdrawal, and leaves in that same resolution when the delay has passed and no standing creator relocks it, or at its first release otherwise.

The functions below read and write the following state, at the slot of the block:

```python
pending: dict[OpId, PendingInscription]
withdrawals: dict[OpId, Withdrawal]
due: SortedMap[Slot, list[OpId]]
ledger: Ledger
block_slot: Slot
```

`route_to_rewards_pool` also writes the pending rewards pool. The resolution of a block is:

```python
def resolve_channels(block_slot: Slot):
    while due and due.first_key() <= block_slot:
        for op_id in due.pop(due.first_key()):
            resolve(op_id, block_slot)

def resolve(op_id: OpId, block_slot: Slot):
    if op_id in pending:
        inscription = pending[op_id]
        # The deadline moved since the entry was made: a later entry covers it
        if block_slot < inscription.deadline:
            return
        if inscription.status == CHALLENGED:
            lose(op_id, block_slot)
        elif inscription.undone or not any(dep in pending for dep in inscription.depends_on):
            # NOT_CHALLENGED or PROVEN, and nothing it depends on is pending
            finalize(op_id, block_slot)
        # Otherwise an inscription it depends on is pending, and resolves it when it leaves pending
    elif op_id in withdrawals:
        withdrawal = withdrawals[op_id]
        # Reached through a note it names before its delay: its own entry covers it
        if block_slot < withdrawal.due:
            return
        if any(ledger.channel_notes[note_id].locked_by is None for note_id in withdrawal.inputs):
            withdraw(op_id)
        # The locked inputs stay in the withdrawal, and the inscription locking each
        # resolves it when it releases or removes the note
```

Unlocking notes, or removing them, resolves the withdrawals that were waiting for them:

```python
def release(notes: list[NoteId], block_slot: Slot):
    ledger.unlock(notes)
    for withdrawal_id in withdrawals_naming(notes):
        resolve(withdrawal_id, block_slot)

def withdrawals_naming(notes: list[NoteId]) -> list[OpId]:
    # each once, in the order of the notes
    found = []
    for note_id in notes:
        withdrawal_id = ledger.channel_notes[note_id].withdrawal
        if withdrawal_id is not None and withdrawal_id not in found:
            found.append(withdrawal_id)
    return found
```

A final inscription unlocks the notes it created and its bond, and resolves the inscriptions that consumed a note it created. An undone inscription created nothing any more, and unlocks its bond only:

```python
def finalize(op_id: OpId, block_slot: Slot):
    inscription = pending.pop(op_id)
    release(inscription.created + inscription.bond, block_slot)
    for dep in inscription.dependents:
        resolve(dep, block_slot)
```

A forfeit takes from a bond exactly `required`: the notes in order until they cover it, the excess of the last note taken re-created for its holder as a channel note of the channel, and the rest of the bond released. What the forfeited amount pays is its `payout`, created in the channel under the forfeit identifier of the inscription, derived from its `OpId`: an inscription is challenged at most once, so it forfeits at most once, whether its challenger's bond forfeits to it or its own bond forfeits:

```python
def derive_forfeit_id(op_id: OpId) -> Hash:
    h = Hasher()  # /!\ a classic hash, as in derive_op_id /!\
    h.update(b"CHANNEL_FORFEIT_V1")
    h.update(op_id)
    return h.digest()

def forfeit(bond: list[NoteId], required: TokenValue, channel: ChannelId,
            forfeit_id: Hash, payout: list[Note], block_slot: Slot):
    taken, spent, rest = 0, [], []
    for note_id in bond:
        if taken >= required:
            rest.append(note_id)
        else:
            taken += ledger.get_note(note_id).value
            spent.append(note_id)
    last = ledger.get_note(spent[-1])
    ledger.execute_spending(spent)
    if taken > required:
        payout = payout + [Note(value=taken - required, public_key=last.public_key)]
    ledger.execute_adding(forfeit_id, payout, channel)
    release(rest, block_slot)
```

A lost inscription forfeits its `required`, half of it paying the challenger at the key of the first note of its bond and the rest going to the rewards pool. Unless an earlier loss already undid it, it is undone with every inscription depending on it:

```python
def lose(op_id: OpId, block_slot: Slot):
    lost = pending[op_id]
    if not lost.undone:
        undo(op_id, block_slot)
    del pending[op_id]

    challenger = ledger.get_note(lost.challenge[0]).public_key
    share = lost.required // 2
    payout = [Note(value=share, public_key=challenger)] if share > 0 else []
    forfeit(lost.bond, lost.required, lost.channel, derive_forfeit_id(op_id), payout, block_slot)
    route_to_rewards_pool(lost.required - share)

    # The challenger's bond is released, and the undone dependents are resolved
    release(lost.challenge, block_slot)
    for dep in lost.dependents:
        resolve(dep, block_slot)
```

Undoing re-inserts no `NoteId`: the consumed notes are re-created under the redirect identifier of the lost inscription, derived from its `OpId`. The undone inscriptions stay pending, marked, so that they can still be challenged and answered until their own deadline. No inscription consumes a note under withdrawal, so an undo never restores one; a withdrawn note that an undone inscription created is removed with it, leaves the withdrawal, and the withdrawal is resolved:

```python
def derive_redirect_id(op_id: OpId) -> Hash:
    h = Hasher()  # /!\ a classic hash, as in derive_op_id /!\
    h.update(b"LOST_CHANNEL_INSCRIPTION_REDIRECT_V1")
    h.update(op_id)
    return h.digest()

def undo(op_id: OpId, block_slot: Slot):
    # The lost inscription and every standing inscription depending on it, reached through
    # the dependents of each, which are in posting order: the cost is the size of the undone set
    undone, undone_ids, queue = [], set(), deque([op_id])
    while queue:
        inscription_id = queue.popleft()
        if inscription_id in undone_ids or inscription_id not in pending or (inscription_id != op_id and pending[inscription_id].undone):
            continue
        undone.append(inscription_id)
        undone_ids.add(inscription_id)
        queue.extend(pending[inscription_id].dependents)
    records = [pending[inscription_id] for inscription_id in undone]
    for inscription in records:
        inscription.undone = True

    # The notes the undone inscriptions created are removed
    removed = [note_id for inscription in records for note_id in inscription.created]
    waiting = withdrawals_naming(removed)
    if removed:
        ledger.execute_spending(removed)
    for inscription in records:
        inscription.created = []
    for withdrawal_id in waiting:
        if withdrawal_id in withdrawals:
            resolve(withdrawal_id, block_slot)

    # The notes they consumed from outside the undone set are re-created, under the
    # same keys. A note whose creator still stands, pending, is locked by it again.
    restored = [consumed for inscription in records for consumed in inscription.inputs
                if consumed.locked_by not in undone_ids]
    ids = ledger.execute_adding(derive_redirect_id(op_id), [consumed.note for consumed in restored],
                                records[0].channel)
    inherited = []
    for note_id, consumed in zip(ids, restored):
        creator = pending.get(consumed.locked_by)
        relocked = creator is not None and not creator.undone
        if relocked:
            creator.created.append(note_id)
            ledger.lock([note_id], consumed.locked_by, created=True)
        # A note that was under withdrawal when it was consumed comes back under it.
        # The withdrawal is re-created if it was dropped as empty; its due entry, if
        # still to come, covers it, and past its due it is resolved once every
        # restored note is back
        if consumed.withdrawal is not None:
            if consumed.withdrawal not in withdrawals:
                withdrawals[consumed.withdrawal] = Withdrawal(inputs=[], due=consumed.withdrawal_due)
            withdrawals[consumed.withdrawal].inputs.append(note_id)
            ledger.channel_notes[note_id].withdrawal = consumed.withdrawal
            if not relocked and consumed.withdrawal not in inherited:
                inherited.append(consumed.withdrawal)
    for withdrawal_id in inherited:
        resolve(withdrawal_id, block_slot)
```

A withdrawal takes its notes out of the channel, re-creating them as ordinary notes under the same keys. Each leaves under an identifier derived from the note it replaces, since a withdrawal takes notes out more than once: its inputs leave as each is unlocked, and an undo can return a note to it after others have left:

```python
def derive_withdrawal_id(note_id: NoteId) -> Hash:
    h = Hasher()  # /!\ a classic hash, as in derive_op_id /!\
    h.update(b"CHANNEL_WITHDRAWAL_V1")
    h.update(note_id)
    return h.digest()

def withdraw(op_id: OpId):
    # The unlocked inputs leave now; the locked ones stay in the withdrawal until released
    inputs = [note_id for note_id in withdrawals[op_id].inputs
              if ledger.channel_notes[note_id].locked_by is None]
    notes = [ledger.get_note(note_id) for note_id in inputs]
    ledger.execute_spending(inputs)   # drops the withdrawal with its last note
    for note_id, note in zip(inputs, notes):
        ledger.execute_adding(derive_withdrawal_id(note_id), [note])
```

`route_to_rewards_pool(amount)` adds `amount` to the pending rewards pool and counts it in the block's $`R_\text{block}`$, as the fees of its transactions are (see [Block Rewards](block-rewards.md)).

## Service Declaration Protocol (SDP) Operations

These Operations implement the [Service Declaration Protocol](bedrock-service-declaration-protocol.md).

Validators must keep the following state when implementing SDP Operations:

```python
service_notes: dict[NoteID, ServiceNote]
declarations: dict[DeclarationID, DeclarationInfo]

class ServiceNote:
    declarations: set[DeclarationID]
```

### Common SDP Structures

```python
class ServiceType(Enum):
    BN=0 # Blend Network; the one-byte discriminant is the canonical encoding

class Locator(bytes):
    # multiaddr binary form; the canonical encoding
    # (see SDP: Locators)
    def validate(self):
        assert len(self) <= 329
        assert validate_multiaddr(self)

class MinStake:
    stake_threshold: int # stake value
    epoch: EpochNumber # epoch number

class ServiceParameters:
    inactivity_period: NumberOfEpochs # number of epochs
    epoch: EpochNumber                # epoch number at which the Service Parameters were set

class DeclarationInfo:
    service: ServiceType
    locators: list[Locator]
    provider_id: Ed25519PublicKey
    zk_id: ZkPublicKey
    service_note_id: NoteId
    created: EpochNumber
    active: EpochNumber
    withdraw_at: EpochNumber | None
    # SDP ops updating a declaration must use monotonically increasing nonces
    nonce: int
```

### SDP_DECLARE

The service registration follows the definition given in [**Declaration Message**](bedrock-service-declaration-protocol.md#declaration-message):

#### Payload

```python
class DeclarationMessage:
    service_type: ServiceType
    locators: list[Locator]
    provider_id: Ed25519PublicKey
    zk_id: ZkPublicKey
    service_note_id: NoteId
```

Service notes are introduced in [Service notes](#service-notes) and serve as Service collaterals. They cannot be spent before the owner withdraw its participation from the declared service(s).

#### Proof

```python
class DeclarationProof:
    zk_sig: ZkSignature             # signature proving ownership over
                                    # service note and zk_id
    provider_sig: Ed25519Signature  # signature proving ownership of provider key
```

  see: [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

#### Execution Gas

  SDP Declare Operations have a fixed Execution Gas cost of `EXECUTION_SDP_DECLARE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: zkhash                  # the txhash of the transaction we are validating
declaration: DeclarationMessage # the declaration we are validating
proof: DeclarationProof

min_stake: MinStake      # the (global) minimum stake setting
ledger: Ledger           # the set of unspent notes
service_notes: dict[NoteId, ServiceNote]
declarations: dict[NoteId, DeclarationInfo]
```

  *Validate*

  The declaration is verified according to [Declare](bedrock-service-declaration-protocol.md#declare).

  1. Ensure ownership over the service note, `zk_id` and `provider_id`.
      ```python
      assert ZkSignature_verify(
          txhash, proof.zk_sig, [note.public_key, declaration.zk_id]
      )
      assert Ed25519_verify(txhash, proof.provider_sig, provider_id)
      ```

  2. Ensure declaration does not already exist.
      ```python
      assert declaration_id(declaration) not in declarations
      ```

  3. Ensure the locators list is non-empty and has no more than 8 entries.
      ```python
      assert len(declaration.locators) >= 1
      assert len(declaration.locators) <= 8
      ```

  4. Ensure the service note exists and its value is sufficient for joining the service.
      ```python
      assert ledger.is_unspent(declaration.service_note_id)
      note = ledger.get_note(declaration.service_note_id)
      assert note.value >= min_stake.stake_threshold

      # A service note is an ordinary note, not a channel note
      assert declaration.service_note_id not in ledger.channel_notes
      ```

  5. Ensure the note has not already been used for this service.
      ```python
      if declaration.service_note in service_notes:
          service_note = service_notes[declaration.service_note]
          services = [declarations[declare_id] for declare_id in service_note.declarations]
          assert declaration.service_type not in services
      ```

#### Execution

  *Given*

```python
declaration: DeclarationMessage # the declaration we are executing
current_epoch: EpochNumber
service_notes : dict[NoteId, ServiceNote]
```

  *Execute*

  1. Create the service note state if it doesn't already exist.
      ```python
      if declaration.service_note not in service_notes:
          service_notes[declaration.service_note_id] = ServiceNote(declarations=set())

      service_note = service_notes[declaration.service_note_id]
      ```

  2. Add this declaration to the service note.
      ```python
      declare_id = declaration_id(declaration)
      service_note.declarations.add(declare_id)
      ```

  3. Store the declaration as explained in [**Declaration Storage**](bedrock-service-declaration-protocol.md#declaration-storage).
      ```python
      declarations[declare_id] = DeclarationInfo(
          service: declaration.service
          locators: declaration.locators
          provider_id: declaration.provider_id
          zk_id: declaration.zk_id
          service_note_id: declaration.service_note_id
          declaration,
          created=current_epoch,
          active=current_epoch + 2,
          withdraw_at=None
          nonce=0
      )
      ```

#### Example

```python
# Assume `alice_note` is in the ledger:
alice_note = Utxo(
    txhash=0x2948904F2F0F479B8F8197694B30184B0D2ED1C1CD2A1EC0FB85D299A192A447,
    output_number=3,
    note=Note(value=500, public_key=alice_pk_1),
)

# Alice wishes to lock it to join the Blend network
declaration=DeclarationMessage(
    service_type=ServiceType.BN,
    locators=["/ip4/203.0.113.10/tcp/4001/p2p"],
    provider_id=alice_provider_pk,
    zk_id=alice_pk_2,
    service_note_id=alice_note.id()
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[fee_note_id], outputs=[])


tx = MantleTx(
    ops=[Op(opcode=SDP_DECLARE, payload=encode(declaration)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)
txhash = mantle_txhash(tx)

declaration_proof = DeclarationProof(
    # proof of ownership of the staked note and zk_id
    zk_sig=ZkSignature([alice_sk_1, alice_sk_2], txhash),
    # proof of ownership of the provider id
    provider_sig=Ed25519Signature(alice_provider_sk, txhash),
)

SignedMantleTx(
    tx=tx,
    op_proofs=[declaration_proof, transfer.prove(alice_sk_1)],
)
```

### SDP_WITHDRAW

The service withdrawal follows the definition given in [Withdraw Message](bedrock-service-declaration-protocol.md#withdraw-message).

#### Payload

```python
class WithdrawMessage:
    declaration: DeclarationID
    service_note_id: NoteId
    nonce: int
```

#### Proof

  A signature from the `zk_id` and the service note `pk` attached to the declaration is required for withdrawing from a service, (see [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature)).

```python
ZkSignature
```

#### Execution Gas

  SDP Withdraw Operations have a fixed Execution Gas cost of `EXECUTION_SDP_WITHDRAW_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: zkhash # Mantle transaction hash of the tx containing this operation
withdraw: WithdrawMessage
signature: ZkSignature

ledger: Ledger
service_notes: dict[NoteId, ServiceNote]
declarations: dict[DeclarationID, DeclarationInfo]
```

  *Validate*

  1. Ensure that the service note exists and is bound to this declaration.
      ```python
      assert ledger.is_unspent(withdraw.service_note_id)
      assert withdraw.service_note_id in service_notes

      service_note = service_notes[withdraw.service_note_id]

      assert withdraw.declaration in service_note.declarations
      ```

  2. Validate SDP withdrawal according to [**Withdraw**](bedrock-service-declaration-protocol.md#withdraw).
      1. Ensure declaration exists.
          ```python
          assert withdraw.declaration in declarations
          declare_info = declarations[withdraw.declaration]
          ```
      2. Ensure the declaration is not already scheduled for withdrawal.
          ```python
          assert declare_info.withdraw_at is None
          ```
      3. Ensure service note `pk` and `zk_id` attached to this declaration authorized this Operation.
          ```python
          service_note = ledger[withdraw.service_note_id]
          assert ZkSignature_verify(txhash, signature, [service_note.pk, declare_info.zk_id])
          ```
      4. Ensure that the nonce is greater than the previous one.
          ```python
          assert withdraw.nonce > declare_info.nonce
          ```

#### Execution

  *Given*

```python
withdraw: WithdrawMessage
signature: ZkSignature

current_epoch: EpochNumber # current epoch
ledger: Ledger
service_notes: dict[NoteId, ServiceNote]
declarations: dict[DeclarationID, DeclarationInfo]
```

  *Execute*

  Executes the withdrawal protocol [**Withdraw**](bedrock-service-declaration-protocol.md#withdraw).

  1. Update the declaration info with the nonce and the withdrawal epoch.
      ```python
      declare_info = declarations[withdraw.declaration]
      declare_info.nonce = withdraw.nonce
      declare_info.withdraw_at = current_epoch + 2
      ```

#### Example

```python
withdraw=Withdraw(
    declaration=alice_declaration_id,
    service_note_id=alices_service_note_id
    nonce=1579532
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[alices_service_note_id],
                    outputs=[Note(100, alice_note_pk)])

tx = MantleTx(
    ops=[Op(opcode=SDP_WITHDRAW, payload=encode(withdraw)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

SignedMantleTx(
    tx=tx,
    # proof ownership of the withdrawn note and zk id
    op_proofs=[ZkSignature_sign([alice_note_sk, alice_sk], mantle_txhash(tx)),
               transfer.prove(alice_sk)]
)
```

### SDP Epoch Finalization

Withdrawn declarations are removed by Mantle as part of the epoch transition,
not when the `WithdrawMessage` is processed. The rewards of epoch
`withdraw_at - 1` ([Withdraw](bedrock-service-declaration-protocol.md#withdraw))
are distributed in the first block of epoch `withdraw_at + 1` (see
[Service Reward Distribution Protocol](bedrock-service-reward-distribution.md)).
In that same block, after the rewards have been distributed, every declaration
with `withdraw_at + 1 <= current_epoch` is removed and its stake unlocked.
Declarations that withdrew without earning a final reward are removed by the
same step.

  *Given*

```python
current_epoch: EpochNumber
service_notes: dict[NoteId, ServiceNote]
declarations: dict[DeclarationID, DeclarationInfo]
```

  *Execute*

  For every `declare_id`, `declare_info` in `declarations` where
  `declare_info.withdraw_at is not None and declare_info.withdraw_at + 1 <= current_epoch`:

  1. Remove the declaration from its service note.
      ```python
      service_note = service_notes[declare_info.service_note_id]
      service_note.declarations.remove(declare_id)
      ```

  2. Remove the declaration.
      ```python
      del declarations[declare_id]
      ```

  3. Unlock the note once it is no longer bound to any declaration.
      ```python
      if len(service_note.declarations) == 0:
          del service_notes[declare_info.service_note_id]
      ```

### SDP_ACTIVE

The service active action follows the definition given in [Active Message](bedrock-service-declaration-protocol.md#active-message).

#### Payload

```python
class Active:
    declaration: DeclarationID
    nonce: int
    metadata: bytes # a service-specific node activeness metadata
```

#### Proof

```python
ZkSignature
```

#### Execution Gas

  SDP Active Operations have a fixed Execution Gas cost of `EXECUTION_SDP_ACTIVE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: zkhash # Mantle transaction hash of the tx containing this operation
active: Active
signature: ZkSignature

declarations: dict[DeclarationID, DeclarationInfo]
```

  *Validate*

```python
assert active.declaration in declarations
declaration_info = declarations[active.declaration]

assert active.nonce > declaration_info.nonce

assert ZkSignature_verify(txhash, signature, declaration_info.zk_id)
```

#### Execution

  *Given*

```python
active: Active

current_epoch: EpochNumber # epoch of the block containing this operation
declarations: dict[DeclarationID, DeclarationInfo]
```

  *Execute*

  Executes the active protocol [Active](bedrock-service-declaration-protocol.md#active). If the service-specific activity logic rejects the message, the Operation is invalid.

  1. Update the declaration info with the nonce and the epoch.
      ```python
      declaration_info = declarations[active.declaration]
      declaration_info.nonce = active.nonce
      declaration_info.active = current_epoch
      ```

#### Example

```python
active=Active(
    declaration=alice_declaration_id,
    nonce=1579532,
    metadata=b"Look, I am still doing my job"
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[fee_note_id], outputs=[])

tx = MantleTx(
    ops=[Op(opcode=SDP_ACTIVE, payload=encode(active))],
)
txhash = mantle_txhash(tx)

SignedMantleTx(
    tx=tx,
    op_proofs=[Ed25519_sign(txhash, validator_sk), transfer.prove(fee_note_sk)]
)
```

## Leader Operations

### LEADER_CLAIM

This Operation claims the leader's block reward anonymously.

#### Payload

```python
class ClaimRequest:
    rewards_root: zkhash # Merkle root used in the proof for voucher membership
    voucher_nf: zkhash
    public_key: ZkPublicKey
```

#### Proof

  The provider proves that they have won a proof of Leadership before the start of the current epoch, i.e., their reward voucher is indeed in the voucher set: [Proof of Claim](#proof-of-claim).

#### Execution gas

  Leader Claim Operations have a fixed Execution Gas cost of `EXECUTION_LEADER_CLAIM_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
claim : ClaimRequest
last_voucher_root: zkhash # The last root of the voucher Merkle tree
                          # at the start of the epoch
voucher_nullifier_set: set[zkhash]
proof: ProofOfClaim
```

  *Validate*

```python
assert claim.voucher_nf not in voucher_nullifier_set
assert claim.rewards_root == last_voucher_root
validate_proof(claim, proof, mantle_txhash)
```

#### Execution

  *Given*

```python
claim: ClaimRequest

ledger: Ledger
voucher_nullifier_set: set[zkhash]
leaders_rewards: TokenValue   # The pool of tokens to be claim by leaders
leader_reward: TokenValue     # The amount one leader can claim
```

  *Execution*

  1. Add `claim.voucher_nf` to the `voucher_nullifier_set`.
  2. Denoting by `leader_reward` the amount defined for leader rewards in [Leaders Reward](bedrock-anonymous-leaders-reward.md#leaders-reward), construct a single output note with value leader_reward under the public key defined in the payload, and insert it into the Ledger:
      ```python
      output_note=Note(
          value = leader_reward
          public_key = claim.public_key,
      )
      claim_id = derive_op_id(claim)
      ledger.execute_adding(claim_id, [output_note])
      ```

  3. Reduce the leader’s reward `leaders_rewards` value by the same amount (without ZK proof).

#### Example

```python
secret_voucher = 0xDEADBEAF;
reward_voucher = leader_claim_voucher(secret_voucher)
voucher_nullifier = leader_claim_nullifier(secret_voucher)

claim=ClaimRequest(
    rewards_root=REWARDS_MERKLE_TREE.root(),
    voucher_nf=voucher_nullifier,
    public_key=leader_one_time_key
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[<fee_note>], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=LEADER_CLAIM, payload=encode(claim)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

claim_proof = claim.prove(
    secret_voucher,
    REWARDS_MERKLE_TREE.path(leaf=reward_voucher),
    mantle_txhash(tx)
)

SignedMantleTx(
    tx=tx,
    op_proofs=[claim_proof, transfer.prove(fee_note_sk)]
)
```

## Proof of Work Operations

Validators must maintain the following state to process proof of work Operations:

```python
pow_reward_pool: TokenValue      # Reserve the rewards are paid from
epoch_pow_reward: TokenValue     # Reward per claim, fixed for the epoch
difficulty_reward: PowTarget     # the reward threshold, retargeted every block
pow_nullifiers: set[zkhash]      # Spent solutions, retained for the acceptance window
block_slots: dict[hash, SlotNumber]  # Slots of recently seen blocks, for the window check
```

`PowTarget`, the acceptance window, and the maintenance of `pow_reward_pool`, `epoch_pow_reward` and `difficulty_reward` between blocks are specified in [Proof of Work](proof-of-work.md).

### CLAIM_POW_REWARD

This Operation claims a reward from the proof of work [reward pool](proof-of-work.md#reward-pool) by presenting a puzzle solution.

#### Payload

```python
class ClaimPowRewardOp:
    epoch_nonce: zkhash        # Epoch nonce the solution was found against
    block_hash: hash           # Recent canonical block the solution is anchored to
    public_key: ZkPublicKey    # Key the reward note is paid to
```

#### Proof

  A [ZkSignature](#zero-knowledge-signature-scheme-zksignature) by the secret key corresponding to `public_key`, over the transaction's `mantle_txhash`. The signature proves knowledge of that secret key, so a solution cannot be found by searching over public keys directly.

#### Execution gas

  Claim Operations have a fixed Execution Gas cost of `EXECUTION_CLAIM_POW_REWARD_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
claim: ClaimPowRewardOp            # the CLAIM_POW_REWARD payload
claim_proof: ZkSignature           # the op_proofs entry for this Operation

current_slot: SlotNumber           # slot of the block including this claim
epoch_nonce_current: zkhash        # Cryptarchia epoch nonce of the current epoch
epoch_nonce_previous: zkhash       # and of the epoch before it
WINDOW: SlotNumber                 # the acceptance window, in slots
difficulty_reward: PowTarget       # retargeted every block
pow_nullifiers: set[zkhash]        # spent solutions, retained for WINDOW
pow_reward_pool: TokenValue
epoch_pow_reward: TokenValue
```

  The epoch nonces are the Cryptarchia epoch nonce $`\eta`$ of [Epoch Nonce](cryptarchia-v1-protocol.md#epoch-nonce), and `WINDOW` is derived in [Acceptance Window](proof-of-work.md#acceptance-window).

  *Validate*

```python
# 1. Claiming must be enabled for this block: the pool must be able to cover a reward.
assert epoch_pow_reward > 0
assert pow_reward_pool >= epoch_pow_reward

# 2. The referenced block must be canonical and within the acceptance window.
block = get_block_from_hash(claim.block_hash)   # None if unknown or not canonical
assert block is not None
assert 0 <= current_slot - block.slot <= WINDOW

# 3. The solution must have been found against the current or the previous epoch.
assert claim.epoch_nonce in (epoch_nonce_current, epoch_nonce_previous)

# 4. The ticket must satisfy the reward threshold.
puzzle_ticket = zkhash(claim.public_key,
                       FiniteField(claim.block_hash, byte_order="little", modulus=p),
                       claim.epoch_nonce)
assert puzzle_ticket < difficulty_reward

# 5. The solution must not have been claimed before. The nullifier is the ticket.
assert puzzle_ticket not in pow_nullifiers

# 6. The claim must be signed by the key the reward is paid to.
assert ZkSignature_verify(mantle_txhash, claim_proof, [claim.public_key])
```

#### Execution

  *Given*

```python
claim: ClaimPowRewardOp
puzzle_ticket: zkhash              # computed in validation step 4

ledger: Ledger
pow_reward_pool: TokenValue
epoch_pow_reward: TokenValue       # fixed for the epoch
pow_nullifiers: set[zkhash]
```

  *Execution*

  1. Add `puzzle_ticket` to the `pow_nullifiers` set. The entry is retained until the claim's referenced block leaves the [acceptance window](proof-of-work.md#acceptance-window).
  2. Construct a single output note of value `epoch_pow_reward` under the public key given in the payload, and insert it into the Ledger:
      ```python
      output_note = Note(
          value = epoch_pow_reward,
          public_key = claim.public_key,
      )
      claim_id = derive_op_id(claim)
      ledger.execute_adding(claim_id, [output_note])
      ```

  3. Reduce the `pow_reward_pool` by the same amount:
      ```python
      pow_reward_pool = checked_uint64(pow_reward_pool - epoch_pow_reward)
      ```

#### Example

```python
claim = ClaimPowRewardOp(
    epoch_nonce=get_current_epoch_nonce(),
    block_hash=recent_canonical_block_hash(),
    public_key=reward_pk,          # a key whose ticket satisfies difficulty_reward
)

# The reward note is spendable by the following Operation, so it pays the fee
reward_note_id = derive_note_id(derive_op_id(claim), 0,
                                Note(value=epoch_pow_reward, public_key=reward_pk))
transfer = Transfer(inputs=[reward_note_id], outputs=[<change_note>])

tx = MantleTx(
    ops=[Op(opcode=CLAIM_POW_REWARD, payload=encode(claim)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

SignedMantleTx(
    tx=tx,
    op_proofs=[ZkSignature(reward_sk, mantle_txhash(tx)), transfer.prove(reward_sk)]
)
```

## TRANSFER

Transactions must prove the ownership of spent notes. In classical blockchains, this is done through a signature. To stay compatible with our architecture, the signature is done by a ZK proof (see [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature)), proving the knowledge of the secret key associated with the public key.

Transactions allow complete transaction linkability and the public key spending the note is not hidden.

### Payload

```python
class Transfer:
    inputs: list[NoteId]  # the list of consumed note identifiers
                          # must be non-empty
    outputs: list[Note]
```

### Proof

  A Transfer proves the ownership of the consumed notes using a [Zero Knowledge Signature Scheme (ZkSignature)](#zero-knowledge-signature-scheme-zksignature).

```python
ZkSignature
```

### Execution Gas

  Transfer have a fixed Execution Gas cost of `EXECUTION_TRANSFER_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

### Validation

  *Given*

```python
mantle_txhash: zkhash # zkhash of mantle tx containing this ledger tx
transfer: Transfer
transfer_proof: ZkSignature

ledger: Ledger
```

  *Validate*

  1. Ensure all inputs are spendable and not in a channel.
      ```python
      ledger.assert_spendable(transfer.inputs)
      ```

  2. Validate transfer proof to show ownership over input notes.
      ```python
      input_notes = [ledger[input_note_id] for input_note_id in transfer.inputs]
      assert ZkSignature_verify(mantle_txhash, transfer_proof, keys_of(input_notes))
      ```

  3. Ensure outputs are valid.
      ```python
      ledger.assert_valid_output(transfer.output)
      ```

### Execution

  *Given*

```python
transfer: Transfer
transfer_proof: ZkSignature

ledger: Ledger
```

  *Execution*

  1. Remove inputs from the ledger.
      ```python
      ledger.execute_spending(transfer.inputs)
      ```

  2. Add outputs to the ledger.
      ```python
      transfer_id = derive_operation_id(transfer)
      ledger.execute_adding(transfer_id, transfer.outputs)
      ```

### Example

```python
alice_note_id = ... # assume Alice holds a note worth 501 tokens
bob_note=Note(
    value=500
    public_key=bob_pk,
)

transfer = Transfer(
    inputs=[alice_note_id],
    outputs=[bob_note],
)
```

# Mantle Ledger

## Notes

Notes are composed of two fields representing their value and their owner:

```python
class Note:
    value: TokenValue   # uint64
    public_key: ZkPublicKey # 32 bytes
```

### Note Id

A note can be uniquely identified by the Operation that created it and its output number: `(op_id, output_number)` if each Operation are uniquely identifiable. For this reason, every Operation that output notes have a unique payload that is used to derive the Operation identifier. Because it is often useful to have a commitment to the note fields for use in ZK proofs (e.g., for PoL), we included the note in the note identifier derivation.

```python
def derive_op_id(operation: Op) -> Hash:
    op_bytes = encode(op)
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"OPERATION_ID_V1")
    h.update(op_bytes)
    return h.digest()

def derive_note_id(op_id: Hash, output_number: int, note: Note) -> NoteId:
    return zkhash(
        FiniteField(b"NOTE_ID_V1", byte_order="little", modulus= p),
        FiniteField(op_id, byte_order="little", modulus= p),
        FiniteField(output_number, byte_order="little", modulus= p),
        FiniteField(note.value, byte_order="little", modulus= p),
        note.public_key
    )
```

`op_id` is a classical 256-bit hash digest and must be reduced to a field element before being passed to the ZkHasher. We apply a direct modular reduction mod `p` (via `FiniteField(..., modulus=p)`). Since $`p \approx2^{-254}`$, the reduction is slightly non-uniform, values in $`[0, 2^{256} \mod p)`$ appear one extra time, but this is inconsequential in practice: the collision probability remains around $`2^{-254}`$, and `NoteId` uniqueness is not derived from uniformity of `op_id` over $`𝔽_p`$ but from the collision-resistance of the underlying hash and per-operation payload uniqueness.

These note identifiers uniquely define notes in the system and cannot be chosen by the user. Nodes maintain the set of notes through a dictionary mapping the NoteId to the note.

### Service notes

Service notes are special notes in Mantle that serve as collateral for Service Declarations. A note can become a service note after being locked by executing a Declare Operation, preventing it from being spent until explicitly released through a Withdraw Operation. The system maintains a mapping of service note IDs to their supporting declarations. Though locked, these notes remain in the Ledger and can still participate in Proof of Stake. When service providers withdraw all their declarations, the associated note(s) become unlocked and available for spending again.

### Channel Notes

Channel notes are on-ledger notes representing the funds bridged into a channel. They are distinct from Service Notes as they can’t be used to declare a service, and they move inside their channel only with their holder's authorization (see [Channels](channels.md#bridging)). They follow the same ageing rule as ordinary notes since they are part of the ledger and can be used for PoL creation once aged enough.

The Ledger tracks every channel note in `channel_notes`, with its `ChannelId`, its lock, whether that lock is the one of a note the inscription created or of a bond, and the withdrawal that names it. A pending inscription locks the notes it created, its bond, and the bond of its challenge, under its `OpId`. A locked note stays in the Ledger and keeps taking part in Proof of Stake, like a service note. A note the inscription created may be consumed by a later inscription of its channel and by nothing else; a bond may be consumed by nothing, and cannot be withdrawn. A note under withdrawal may be consumed by an inscription until the withdrawal's delay has passed, and by nothing after. The [Channel Resolution](#channel-resolution) unlocks them when the inscription is final, takes its `required` from the bond when it is lost, and takes the withdrawn notes out of the channel, the only way out of it.

## Ledger

```python
class ChannelNote:
    channel: ChannelId
    locked_by: OpId | None    # the pending inscription that locks the note, if any
    created: bool             # locked as a note that inscription created, not as a bond
    withdrawal: OpId | None   # the withdrawal that names the note, if any

class Ledger:
    notes: list[Note]
    service_notes: dict[NoteId, ServiceNote]
    channel_notes: dict[NoteId, ChannelNote]
```

### Input Notes Spendability Validation

A note is spendable if and only if it exists, it is not spent, and it is not a service note. A channel note is spendable by an inscription of its channel only, so no other Operation takes a note out of a channel. A locked channel note is spendable only when it is a note the pending inscription that locked it created: a bonded note is spendable by nothing until it is released. A channel note under withdrawal is spendable until the withdrawal's `due`, and by nothing from then on. The function reads `withdrawals` and the `block_slot` of the block for that rule, and validates that an input of notes can be consumed:

```python
class Ledger:
    def assert_spendable(inputs: list[NoteId], channel_id: ChannelId | None = None):
        # Assert inputs are not empty
        assert len(inputs) > 0

        # Check there is no duplicate
        assert len(inputs) == len(set(inputs))

        for note_id in inputs:
            assert ledger.is_unspent(note_id)
            assert note_id not in ledger.service_notes
            if channel_id is not None:
                # a note of this channel, under no withdrawal past its delay, and if
                # it is locked, one its inscription created: a bond is locked too,
                # and may be consumed by nothing
                assert note_id in ledger.channel_notes
                note = ledger.channel_notes[note_id]
                assert note.channel == channel_id
                if note.withdrawal is not None:
                    assert block_slot < withdrawals[note.withdrawal].due
                if note.locked_by is not None:
                    assert note.created
            else:
                # a channel note leaves its channel only by a withdrawal
                assert note_id not in ledger.channel_notes
```

A bond is made of unlocked channel notes of the channel the bond is posted in, under no withdrawal:

```python
class Ledger:
    def assert_bond(notes: list[NoteId], channel_id: ChannelId):
        for note_id in notes:
            assert note_id in ledger.channel_notes
            assert ledger.channel_notes[note_id].withdrawal is None
            assert ledger.channel_notes[note_id].locked_by is None
        ledger.assert_spendable(notes, channel_id)
```

### Output Notes Validation

Before an output of notes can be inserted into the Ledger, every note field must satisfy the following constraints:

```python
class Ledger:
    def valid_output(outputs: list[Note]) -> bool:
        return all(0 < note.value <= UINT64_MAX for note in outputs)

    def assert_valid_output(outputs: list[Note]):
        assert ledger.valid_output(outputs)
```

### Consuming Input Notes Execution

Consuming a set of notes removes them from the Ledger’s Merkle tree and recycles their leaf indices. A consumed channel note leaves its channel, and its lock with it. A note under withdrawal that is consumed, by an inscription during the delay or because an undo removes it, leaves its withdrawal, and a withdrawal that names nothing any more is dropped:

```python
class Ledger:
    def execute_spending(inputs: list[NoteId]):
        for note_id in inputs:
            # updates the merkle tree to zero out the leaf for this entry
            # and adds that leaf index to the list of unused leaves
            ledger.remove(note_id)
            note = ledger.channel_notes.pop(note_id, None)
            if note is not None and note.withdrawal is not None:
                w = withdrawals[note.withdrawal]
                w.inputs.remove(note_id)
                if not w.inputs:
                    del withdrawals[note.withdrawal]
```

### Creating Output Notes Execution

Creating notes derives their `NoteId` from the Operation’s `OpId` and insert them in the Ledger:

```python
class Ledger:
    def execute_adding(op_id: Hash, outputs: list[Note], channel_id: ChannelId | None = None) -> list[NoteId]:
        output_note_ids = []
        for (output_index, output_note) in enumerate(outputs):
            output_note_id = derive_note_id(op_id, output_index, output_note)
            ledger.add(output_note_id)
            if channel_id is not None:
                ledger.channel_notes[output_note_id] = ChannelNote(channel=channel_id, locked_by=None, created=False, withdrawal=None)
            output_note_ids.append(output_note_id)
        return output_note_ids
```

### Locking Notes

An inscription that moves notes locks the notes it creates and its bond, and a challenge locks its bond, under the `OpId` of the pending inscription. The note records which of the two it is, since only a note the inscription created may be consumed while it is locked. The [Channel Resolution](#channel-resolution) unlocks them:

```python
class Ledger:
    def lock(notes: list[NoteId], op_id: OpId, created: bool):
        for note_id in notes:
            ledger.channel_notes[note_id].locked_by = op_id
            ledger.channel_notes[note_id].created = created

    def unlock(notes: list[NoteId]):
        for note_id in notes:
            ledger.channel_notes[note_id].locked_by = None
            ledger.channel_notes[note_id].created = False
```

# Appendix

## Gas Determination

From the [[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md), we get the table below:

| Constants | Value |
| --- | --- |
| EXECUTION_TRANSFER_GAS | 590 |
| EXECUTION_CHANNEL_INSCRIBE_GAS | 56 |
| EXECUTION_CHANNEL_BOND_GAS | 590 |
| EXECUTION_CHANNEL_CONFIG_GAS | 56 |
| EXECUTION_CHANNEL_DEPOSIT_GAS | 590 |
| EXECUTION_CHANNEL_WITHDRAW_GAS | 590 |
| EXECUTION_CHANNEL_CHALLENGE_GAS | 590 |
| EXECUTION_ANSWER_STEP_GAS | 590 |
| EXECUTION_SDP_DECLARE_GAS | 646 |
| EXECUTION_SDP_WITHDRAW_GAS | 590 |
| EXECUTION_SDP_ACTIVE_GAS | 590 |
| EXECUTION_LEADER_CLAIM_GAS | 580 |
| EXECUTION_CLAIM_POW_REWARD_GAS | 590 |

## Zero Knowledge Signature Scheme (ZkSignature)

A proof attesting that for the following public values:

```python
class ZkSignaturePublic:
    public_keys: list[ZkPublicKey] # public keys signing the message (len = 32)
    msg: zkhash # a finite field element uniquely representing the message
```

The prover knows a witness:

```python
class ZkSignatureWitness:
    # The list of secret keys used to signed the message
    secret_keys: list[ZkSecretKey] # (len = 32)
```

Such that the following constraints hold:

- The number of secret keys is equal to the number of public keys.
  ```python
  assert len(secret_keys) == len(public_keys)
  ```

- Each public key is derived from the corresponding secret key.
  ```python
  assert all(
      notes[i].public_key == zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), secret_keys[i])
      for i in range(len(public_keys))
  )
  ```

- The ZkSignature is bound to `msg`. For an Operation proof, `msg` is the `mantle_tx_hash` reduced modulo $`p`$. For an [authorization](channels.md#authorizations), the ZkSignature a channel note holder gives a Zone off chain to let its note move, `msg` is the `auth_msg` of the notes consumed and created; the ledger sees it in the payload of a `CHANNEL_ANSWER`, not as an Operation proof.

  For implementation, the ZkSignature circuit will take a maximum of 32 public keys as inputs. To prove ownership of fewer keys, the remaining inputs will be padded with the public key corresponding to the secret key `0` and ignored during execution. The outputs have no size limit since they are included in the hashed message.

### Keys of Notes

When a ZkSignature proves the ownership of notes, `public_keys` is the list of the distinct keys of those notes, each once, in the order it first appears among them. The 32-key limit of the circuit therefore bounds the number of distinct owners, not the number of notes: one signature can spend any number of notes held under one key, and up to 32 keys together.

```python
def keys_of(notes: list[Note]) -> list[ZkPublicKey]:
    keys = []
    for note in notes:
        if note.public_key not in keys:
            keys.append(note.public_key)
    return keys
```

Every verification of a ZkSignature over notes builds its key list with `keys_of`: `TRANSFER`, `CHANNEL_DEPOSIT` and `CHANNEL_WITHDRAW` from the notes they consume or withdraw, `CHANNEL_INSCRIBE` and `CHANNEL_CHALLENGE` from the notes they bond, and the [authorizations](channels.md#authorizations) of a `CHANNEL_ANSWER` from the notes each step consumes.

### Benchmark

The material used for the benchmarks is the following:

- CPU       : 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM       : 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS        : Ubuntu 22.04.5 LTS
- Kernel    : 6.8.0-59-generic

![Diagram](bedrock-v1.1-mantle-specification/assets/477261aa-09df-8268-8845-8145f3f8d670.png)

## Multiple Ed25519 Signatures Verification

[Channel Configuration](#channel_config) authorizes a new configuration with a
threshold of Ed25519 signatures produced by a list of accredited keys. Each signature comes
with the index, in the accredited keys list, of the key that produced it. The
verification is factored out in the following routine:

*Given*

```python
msg: zkhash                        # the message being signed (the mantle txhash)
signatures: list[Ed25519Signature]
indexes: list[u16]                 # for each signature, the index in `keys` of
                                   # the signing key
keys: list[Ed25519PublicKey]       # the accredited keys
threshold: u16                     # the number of required signatures
```

*Verify*

```python
def MultiEd25519_verify(msg, signatures, indexes, keys, threshold):
    # There must be exactly one index per signature
    assert len(signatures) == len(indexes)

    # There must be exactly `threshold` signatures
    assert len(signatures) == threshold

    # Indexes must be ordered from smallest to biggest without duplication.
    # Being strictly increasing rejects duplicates and, since `idx` is used to
    # index `keys`, guarantees every index stays within bounds.
    for i in range(len(indexes) - 1):
        assert indexes[i] < indexes[i + 1]

    # Each signature must be valid for the accredited key at its index
    for sig, idx in zip(signatures, indexes):
        assert Ed25519_verify(msg, keys[idx], sig)
```

## Proof of Claim

A proof attesting that given these public values:

```python
class ProofOfClaimPublic:
    voucher_root: zkhash # Merkle root of the reward_voucher maintained by everyone
    voucher_nullifier: zkhash
    mantle_tx_hash_fr: zkhash # attached hash reduced modulo p
```

The prover knows the following witness:

```python
class ProofOfClaimWitness:
    secret_voucher: zkhash
    voucher_merkle_path: list[zkhash]
    voucher_merkle_path_selectors: list[bool]
```

such that the following constraints hold:

- The reward voucher is derived from the secret voucher.
```python
assert reward_voucher == zkhash(
    FiniteField(b"REWARD_VOUCHER", byte_order="little", modulus= p),
    secret_voucher)
```

- There exists a valid Merkle path from the reward voucher as a leaf to the Merkle root.
```python
assert voucher_root == path_root(leaf=reward_voucher,
    path=voucher_merkle_path,
    selectors=voucher_merkle_path_selectors)
```

- The voucher nullifier is derived from the secret voucher correctly.
```python
assert voucher_nullifier == zkhash(
    FiniteField(b"VOUCHER_NF", byte_order="little", modulus= p),
    secret_voucher)
```

- The proof is bound to the `mantle_tx_hash` reduced modulo $`p`$.

### Benchmark

The material used for the benchmarks is the following:

- CPU       : 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM       : 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS        : Ubuntu 22.04.5 LTS
- Kernel    : 6.8.0-59-generic

![Diagram](bedrock-v1.1-mantle-specification/assets/b23261aa-09df-827c-8565-014a68d98d4c.png)

## Test Vectors

To see what the payloads represent, refer to [Mantle Transaction Encoding](mantle-transaction-encoding.md).

> **TODO before merge (PR 457).** The vectors below predate the channel changes of Mantle 1.16.0 and are regenerated from the implementation, the repository having no vector tooling: the `CHANNEL_CONFIG` payload without `TransferThreshold`, the `CHANNEL_INSCRIBE` payload with `MovesNotes` clear, the `CHANNEL_WITHDRAW` payload with its channel and inputs, and the transaction carrying one Operation of each kind. Vectors are added for a `CHANNEL_INSCRIBE` that moves notes with its `ZkAndEd25519SigsProof`, for `CHANNEL_CHALLENGE`, and for a `CHANNEL_ANSWER` with one step and its `EmptyProof`.

### Operation Id

| Operation | Payload | `op_id` |
| ------------------------- | - | - |
| `TRANSFER`                | 0x0201000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020300000000000000040000000000000000000000000000000000000000000000000000000000000005000000000000000600000000000000000000000000000000000000000000000000000000000000 | 0x5e5e1b318aa0c2aec93fbb327e6af5f705e5684269a34e0c1319539d00d06cdb |
| `CHANNEL_CONFIG`          | 0x0707070707070707070707070707070707070707070707070707070707070707000000000000000000000000000000000000000000000000000000000000000002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f6180a0000000b0000000c000d00 | 0x8bac7efe4c3ef10745c0d509ac88e2abaf1d3cda94987ed2eeb9ad71dd31d056 |
| `CHANNEL_INSCRIBE`        | 0x0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0b00000068656c6c6f206c6f676f730000000000000000000000000000000000000000000000000000000000000000d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c | 0xfb9af7fb1384fff51780ec8c5afbcba76449ab7603484f797df3a472e48826c1 |
| `CHANNEL_DEPOSIT`         | 0x1010101010101010101010101010101010101010101010101010101010101010011100000000000000000000000000000000000000000000000000000000000000100000006465706f7369742d6d65746164617461 | 0xf14ff0aad9bc5e8e30c5d1aa3710aaa1c1cc1f47c2c256e7d9e73104cb17ccaf |
| `CHANNEL_WITHDRAW`        | 0x1212121212121212121212121212121212121212121212121212121212121212011300000000000000000000000000000000000000000000000000000000000000 | 0x503d0d08f9faef971864943103965d13be7159fe6e0361c8ea614c6d0431e59c |
| `SDP_DECLARE`             | 0x00010b00047f00000191020bb8cd0353470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f319000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000 | 0x42e93fdce121a5ab4da3201a6fd2da1d42ca8b7d8c1a8c9e2a657a6cdc7aa468 |
| `SDP_WITHDRAW`            | 0x1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1d000000000000001c00000000000000000000000000000000000000000000000000000000000000 | 0xc95aea0e46f60c12a8b29b259ca1b39947093c0d88a1ea8400c49e392ca491a0 |
| `SDP_ACTIVE`              | 0x1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1f0000000000000001010a0000008a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020303030303030303030303030303030303030303030303030303030303030303 | 0x76afa55f5733db75a982dc5ccabb5c6a7dab992eda78cdfd5f657f314e388354 |
| `LEADER_CLAIM`            | 0x200000000000000000000000000000000000000000000000000000000000000021000000000000000000000000000000000000000000000000000000000000002200000000000000000000000000000000000000000000000000000000000000 | 0x0dc1a007fdd184b4553a83d166b749a621f5be2de4b3b0429ebf0520d1dd9a51 |

### Mantle Transaction Hash

| Transaction | Payload | Transaction Hash                                                   |
| - | - | - |
| Empty transaction | 0x00 | 0x2eba3f667b80a508f3d44d149a1c27a90ea365a51e4fc8209289088142b364e5 |
| Transaction with one of each operation | 0x0a000201000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020300000000000000040000000000000000000000000000000000000000000000000000000000000005000000000000000600000000000000000000000000000000000000000000000000000000000000100707070707070707070707070707070707070707070707070707070707070707000000000000000000000000000000000000000000000000000000000000000002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f6180a0000000b0000000c000d00110e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0b00000068656c6c6f206c6f676f730000000000000000000000000000000000000000000000000000000000000000d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c121010101010101010101010101010101010101010101010101010101010101010011100000000000000000000000000000000000000000000000000000000000000100000006465706f7369742d6d6574616461746113121212121212121212121212121212121212121212121212121212121212121201130000000000000000000000000000000000000000000000000000000000000014141414141414141414141414141414141414141414141414141414141414141401150000000000000000000000000000000000000000000000000000000000000001160000000000000017000000000000000000000000000000000000000000000000000000000000002000010b00047f00000191020bb8cd0353470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f319000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000211b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1d000000000000001c00000000000000000000000000000000000000000000000000000000000000221e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1f0000000000000001010a0000008a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c02020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202030303030303030303030303030303030303030303030303030303030303030330200000000000000000000000000000000000000000000000000000000000000021000000000000000000000000000000000000000000000000000000000000002200000000000000000000000000000000000000000000000000000000000000 | 0x11e6013847824badf33aa383cfbdb4b5b74a621acefc8296c21f48c4072e0e92 |

### Declaration Id

The `declaration_id` ([Declaration Storage](bedrock-service-declaration-protocol.md#declaration-storage)) is `Hash(service||provider_id||zk_id||locators)` (BLAKE2b, 256-bit output, no DST), where `service` is the one-byte `ServiceType` discriminant and `locators` is the `Locators` production ([Mantle Transaction Encoding](mantle-transaction-encoding.md#sdp-operations)): the element count followed by each `Locator`'s binary form prefixed with its 2-byte little-endian byte length. Note that the preimage field order differs from the `SDP_DECLARE` wire order and excludes `service_note_id`. This vector reuses the fields of the `SDP_DECLARE` payload from [Operation Id](#operation-id).

| Field | Value |
| - | - |
| `service` | 0x00 |
| `provider_id` | 0x53470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f3 |
| `zk_id` | 0x1900000000000000000000000000000000000000000000000000000000000000 |
| `locators` | 0x010b00047f00000191020bb8cd03 |
| Preimage | 0x0053470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f31900000000000000000000000000000000000000000000000000000000000000010b00047f00000191020bb8cd03 |
| `declaration_id` | 0x7fb647c069bade94e06685b0825299d220e7cc14752cfc474773b6c4040e37b5 |
