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
| 1.16.0 | [RFC] Holder-authorized channel notes: a channel note moves only with its holder's authorization, checked on challenge. `CHANNEL_INSCRIBE` carries the transfer part, `CHANNEL_TRANSFER`, `CHANNEL_WITHDRAW` and `transfer_threshold` are removed, an ordinary `TRANSFER` takes an unlocked note out of its channel, and pools, sequencer collateral, challenges and forced transfers are added, forfeits going to the pending rewards pool. Collateral is derived in [\[Analysis\] Channel Collateral](analysis-channel-collateral.md). A `ZkSignature` over notes lists each distinct key once | 2026-09-18 |

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

The Mantle Ledger enables asset transfers using a transparent UTXO model. While a Transfer Operation can consume more tokens than it creates, the Mantle Transaction excess balance must exactly pay for the fees. The ledger tracks regular notes, notes held as collateral (service notes for service declarations, staked notes for channel sequencers and bond notes for challenges) and channel notes (channel bridge funds, moved inside their channel only with their holder's authorization).

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

Each proof (op proof and signature) must be cryptographically bound to the `MantleTx` through the `mantle_txhash` to prevent replay attacks. This binding is achieved by including the `MantleTx` hash reduced modulo $`p`$ as a public input in every ZK proof. The one exception is an [authorization](#authorizations) of channel notes, the proof of `CHANNEL_REGISTER_AUTH` and of the user steps of `CHANNEL_ANSWER`: its holder cannot know the transaction it will end up in, so it is bound to the notes it consumes instead, and cannot be replayed since each note is consumed once.

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

The state validation reads is not a fixed snapshot: it advances as the block is processed. A Mantle Transaction is validated against the state left by the Mantle Transactions preceding it in the block, as defined in [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation), and validation and execution then follow one another Operation by Operation, in the order the Operations appear: the Operation at index `i` is validated against the state the Operations at indices `0` to `i-1` left, then executed to produce the state the Operation at index `i+1` is validated against. This is what the `ledger`, `channels`, `pools`, `pending_transfers`, `registrations`, `sequencer_stakes`, `service_notes`, `declarations` and `voucher_nullifier_set` given to each Operation below denote.

Atomicity is what a failed check means, not simultaneity. If any of the checks below fails, the whole Mantle Transaction is invalid: none of its Operations takes effect, whether or not it was reached. An invalid Mantle Transaction is never skipped over either, the block including it being invalid and nothing of that block being executed.

`CHANNEL_ANSWER` is the only Operation whose outcome is decided at execution rather than by validity. Its validation holds cheap checks only, and whether the answer holds is an outcome of its execution: a wrong answer forfeits its bond and leaves the transaction, and the block, valid. Evaluating an answer means verifying signatures and a Risc0 proof. Since the result never makes a block invalid, a leader can include an answer without evaluating it first, and a wrong one cannot be used to waste leaders' time.

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
| *RESERVED* | *0x13 - 0x14* | Formerly `CHANNEL_WITHDRAW` and `CHANNEL_TRANSFER`, not reused |
| CHANNEL_REGISTER_AUTH | 0x15 | Register an authorization, starting the delay before it can be forced |
| CHANNEL_FORCE_TRANSFER | 0x16 | Apply a registered authorization the sequencers did not apply |
| CHANNEL_CHALLENGE | 0x17 | Challenge a pending transfer |
| CHANNEL_ANSWER | 0x18 | Answer a challenge with the accounting of the transfer |
| POOL_CREATE | 0x19 | Create a pool in a channel |
| CHANNEL_STAKE | 0x1A | Stake notes as a sequencer's collateral |
| CHANNEL_UNSTAKE | 0x1B | Release staked notes |
| *RESERVED* | *0x1C - 0x1F* |  |
| SDP_DECLARE | 0x20 | Declare intention to participate as a node in a Bedrock Service, locking funds as collateral. |
| SDP_WITHDRAW | 0x21 | Withdraw participation from a Bedrock Service, unlocking your funds in the process. |
| SDP_ACTIVE | 0x22 | Signal that you are still an active participant of a Bedrock Service. |
| *RESERVED* | *0x23 - 0x2F* |  |
| LEADER_CLAIM | 0x30 | Claim leader reward anonymously. |
| *RESERVED* | *0x31 - 0x3F* |  |
| CLAIM_POW_REWARD | 0x40 | Claim a reward from the pow reward pool. |
| *RESERVED* | *0x41 - 0xFF* |  |

## Channel Operations

Channels allow Zones to post their updates on chain. Channels form virtual chains that overlay on top of the Cryptarchia blockchain. Clients and Followers of a Zone can watch its channel to learn the state of that Zone. Each channel has an associated balance, enabling bridging between Zones and Bedrock.

### Message Ordering

Channels form virtual chains by having each message reference its parent message. The order of messages in these channels is enforced by the sequencer by building a hash chain of messages, i.e. new messages reference the previous messages through a parent hash. Given that Cryptarchia has long finality times, these message parent references allow Zone sequencers to continue to post new updates to channels without having to wait for finality. No matter how Cryptarchia forks and reorgs, the channel messages from honest sequencers will eventually be re-included in a way that satisfies the virtual chain order.

Configurations form a second hash chain within the channel: each configuration names the configuration it supersedes, so a pending reconfiguration stays valid while the sequencer keeps posting inscriptions.

The first time a message is sent to an unclaimed channel, the key that signs the initial message becomes the only accredited key in the list (Note that this key may correspond to a threshold signature key). Accredited keys of a channel forms a committee that can configure the channel and take turns to write messages to that channel following a round-robin algorithm. Configuring a channel includes modifying the list of accredited keys, the round-robin parameters and the required number of signatures to establish a new configuration.

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

The state that bridging adds is given in [Bridging State](#bridging-state).

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

Channels let their bridged funds keep participating in Proof of Stake. When a user deposits funds into a channel, the deposited notes stay on the ledger and are not turned into inert collateral. They are consumed and immediately re-created as channel notes that continue to count toward Proof of Stake and can still be used to create PoLs (see [Channel Notes](#channel-notes)). Two goals motivate this design:

- **More PoS participation, stronger security.** Funds deposited into a channel would otherwise leave the staking set. Keeping them as channel notes means the capital backing the application layer also backs consensus security, so bridging does not shrink the stake that secures the chain.
- **No split between security and application.** A user no longer has to choose between staking funds or using them in a channel. The same funds do both at once. They stay usable inside the channel while still earning Proof of Leadership rewards, so capital is never fragmented between the two.

**Custody and authorization.** A `CHANNEL_DEPOSIT` consumes the deposited notes and re-creates them with the same value and `ZkPublicKey` under a new `NoteId` derived from the deposit's `OpId`, registered in the ledger's `channel_notes` set. From then on the channel has custody: apart from a [forced transfer](#forced-transfers), only its sequencers post the transfers that move the note inside the channel, ordered by the channel's inscriptions. The `ZkPublicKey` keeps the meaning it has on an ordinary note. Its holder creates the note's PoLs, earns their rewards, and must [authorize](#authorizations) any transfer of the note. The ledger does not check authorizations when a transfer is posted. It checks them when someone [challenges](#challenges-and-answers) the transfer, and a transfer they do not back is undone.

**Ageing.** Because the deposit re-creates the notes under a new `NoteId`, a deposited note restarts the ageing process and must age again before it can create a PoL. Bridged funds still count toward Proof of Stake, so the goals above hold, but the participation is not continuous across the deposit. The same holds for every transfer, which consumes its inputs and creates new notes.

**What each party can do.**

| Party | Can | Cannot |
|---|---|---|
| Holder of the note's `ZkPublicKey` | Create a PoL with the note and earn its rewards. Authorize transfers of the note. Take the note out of the channel with a `TRANSFER` once it is not [locked](#transfers) | Use the note as service stake or as sequencer collateral while it is a channel note |
| Channel sequencers | Post, on their turn, transfers applying authorizations, netting many of them into one transfer | Move a note for good without its holder's authorization |

What the ledger guarantees is consent: whatever the channel's configuration, no channel note is moved for good without its holder's authorization. It does not guarantee liveness. Sequencers holding the configuration threshold can refuse to post, and holders then leave with a `TRANSFER` or a [forced transfer](#forced-transfers). Capturing a channel stalls it but does not give access to its funds. The sections below describe the mechanism, and [Bridging State](#bridging-state) and [Bridging Parameters](#bridging-parameters) list what it adds to the ledger. [\[Template\] Bridged Zone](template-bridged-zone.md) shows how a Zone uses it, with a swap pool as an example.

### Authorizations

An authorization is a [`ZkSignature`](#zero-knowledge-signature-scheme-zksignature) by the keys of the channel notes it consumes, listed by `distinct_keys`, over

```python
def auth_msg(channel: ChannelId, inputs: list[NoteId], outputs: list[Note]) -> zkhash:
    fr = lambda x: FiniteField(x, byte_order="little", modulus=p)
    return zkhash(
        fr(b"CHANNEL_NOTE_AUTH_V1"),
        fr(channel),
        fr(len(inputs)), *inputs,
        fr(len(outputs)), *[x for note in outputs for x in (fr(note.value), note.public_key)])
```

It states which notes of the channel may be consumed and which notes must come out of them. It is not bound to a `mantle_txhash`, since the holder cannot know the transaction a sequencer builds out of many authorizations. It cannot be replayed, since each input can be consumed once. The same authorization serves a sequencer's transfer and, if the sequencers ignore it, a [forced transfer](#forced-transfers).

### Transfers

The transfer part of a `CHANNEL_INSCRIBE` consumes channel notes (`inputs`), creates channel notes (`outputs`) and advances pool states (`declared`). Carrying it in the inscription ties the note moves to the zone message they back: both land in one Operation, or neither does. Posting checks only what is cheap: the inputs are notes of the channel, value is conserved, the outputs are sorted by key, the declared pool states match the ledger, and the sequencer's stake covers the transfer's `required` collateral. No authorization or proof is checked.

A posted transfer executes at once, but its outputs are **locked**. A locked note stays on the ledger, ages like any note, and may be consumed by a later transfer of the channel, but no `TRANSFER` or forced transfer may spend it. Executing and locking, rather than delaying, lets a lost challenge be repaired by moving notes again instead of re-inserting consumed `NoteId`s, which must stay unique. For that repair, the pending transfer keeps the value and key of every input it consumed.

A transfer **depends on** the pending transfer that created each locked input it consumes, and on the most recent pending transfer declaring each pool it declares, the one that wrote its `state_before`. Without these edges, a child could become final while the parent it builds on can still be undone, and a pool could be drained in two steps: a false jump to a state where the poster owns the reserves, then a genuine transition out of it. Only these edges count, and not the whole inscription chain, so one lost transfer does not undo every later payment of the channel.

A transfer is **final** once its own window is over and every transfer it depends on is final. Its own window is over when `CHALLENGE_WINDOW` has passed without a challenge, or as soon as a valid answer settles its challenge. Its lock then lifts and nothing else changes.

A transfer is **lost** when its challenge is still unanswered at the end of the response window. It is undone together with every pending transfer that depends on it, directly or not. The notes they consumed from outside that set are re-created under the same keys, the notes they created are removed, and the pools they advanced return to the state before the first of them. The re-created notes have new identifiers, so an authorization naming the old ones, registered or not, no longer applies and has to be signed again.

A transfer undone this way moves nothing any more, but its sequencer still answers for it. It stays challengeable until the end of its own challenge window, and forfeits its collateral only if its own challenge goes unanswered. Otherwise it is dropped once its window is over. An answer reads only what the pending transfer recorded, so it stays possible after the undo.

A sequencer that built on a transfer later lost therefore loses its work, not its collateral, provided it can answer for what it posted. A transfer nobody can answer forfeits whether or not it was undone first, which is why an invalid transfer is worth challenging even when it is about to be undone. To spare its users the undo, a sequencer builds only on a pending transfer it could answer for itself, holding and having checked its authorizations and, for a pool, the transition it declares.

[Channel Transfer Resolution](#channel-transfer-resolution) applies finality and losses at the start of each block, as a function of the chain and the slot alone.

### Challenges and Answers

Anyone may challenge a pending transfer during its `CHALLENGE_WINDOW`, once per transfer, bonding a note worth the transfer's `required`. Anyone may answer until the end of the response window, bonding at least `answer_bond()`. A valid answer settles the challenge and the challenger's bond pays the answerer. A wrong answer forfeits its bond to the rewards pool and leaves the challenge open, so wrong answers cannot make a valid transfer lose. Since a valid answer settles the transfer early, whoever holds its authorizations can finalize it before its window ends by challenging it and answering.

An answer is the full accounting of the transfer, as a list of steps. A challenge cannot target a single note: an authorization names its outputs by content, their `NoteId`s depending on the `op_id` of a transfer it does not know, so two authorizations paying the same key the same value would both claim one output (see the [example](#channel_answer) under `CHANNEL_ANSWER`).

A **user step** applies one authorization. A `ZkSignature` proves every key of its list at once, so two authorizations signed apart cannot be combined in one step. A user step consumes transfer inputs only, the only notes a holder can name when signing. A **pool step** applies one pool transition (see [Pools](#pools)) and may also consume notes created by earlier steps.

Every note a step creates is either consumed by a later step, an **intermediate note** named `(step_index, output_index)`, or a **claim**. Claims to the same key merge: the transfer's outputs are the claims summed per key and sorted by key, which is why outputs are posted sorted by key and why a recipient of several payments receives one note. A zone fee is a claim written in a user's authorization. Since the outputs are fully determined by the steps, a sequencer that groups claims wrongly loses the challenge.

An answer is valid when all of the following hold (see [`answer_holds`](#channel_answer)):

1. every note a step consumes is a transfer input, or an intermediate note created by an earlier step;
2. every transfer input is consumed by exactly one step;
3. every intermediate note is consumed exactly once;
4. every step conserves value and creates notes of positive value;
5. the claims, summed per key and sorted by key, equal the transfer's outputs;
6. every user step carries a valid authorization of its inputs and outputs;
7. every declared pool transition is proven by exactly one pool step, and every pool step proves a declared one.

The first check matters most, since a transfer is challenged once and a settled challenge is final: a step consuming a note the transfer never consumed would count value that is still on the ledger, and nothing would catch it later. Conservation holds per step because the outputs only balance in total. The last check stops a transfer from declaring a pool transition that no answer proves.

### Collateral

A sequencer posts transfers against a standing stake: ordinary notes staked with `CHANNEL_STAKE` and held unspendable, as service notes are. A transfer requires, at the prices of the block that includes it,

```python
def fee_cost(gas: int, size: int) -> TokenValue:
    return checked_uint64(gas * execution_gas_base_price + size * permanent_storage_gas_price)

def required_collateral(inputs: list[NoteId], declared: list[PoolTransition]) -> TokenValue:
    n, d = len(inputs), len(declared)
    # The value of the inputs that could have aged: locked inputs are not eligible
    # for leadership, and the reserves of the declared pools carry a pool key
    reserves = {pool_key(pools[t.instance_id].image_id, t.instance_id, 0) for t in declared}
    staking_value = sum(ledger.get_note(i).value for i in inputs
                        if i not in ledger.locked_notes
                        and ledger.get_note(i).public_key not in reserves)
    return checked_uint64(
        COLLATERAL_MARGIN * fee_cost(FLOOR_GAS + INPUT_GAS * n + STATE_GAS * d,
                                     FLOOR_BYTES + INPUT_BYTES * n + STATE_BYTES * d)
        + STATE_PROVING * d
        + staking_value * VALUE_RATE_PPM // 1_000_000)
```

and may be posted only if the signer's staked value exceeds its `at_risk` by at least that amount. The amount is recorded with the transfer, so later price changes do not alter it. A stake belongs to an accredited key and serves every channel where the key is accredited, and `at_risk` counts across all of them, so a sequencer caught in one channel loses capacity in all.

Each part pays for something, derived in [\[Analysis\] Channel Collateral](analysis-channel-collateral.md):

- The fee-priced part, with its margin, pays for the dispute. Its floor makes a right challenge worth a transaction and makes a wrong one pay for the fixed part of the answer it forced; each input and each declared transition adds what its step adds to that answer.
- `STATE_PROVING` pays for the off-chain proof a pool step needs, which gas does not price.
- The value part pays for the lock itself. A transfer consuming a final note restarts its ageing, even when it is later undone, and keeping value out of the leadership lottery raises every other participant's share of the rewards. The value rate makes that unprofitable.

Staked notes are ordinary notes, never channel notes. Any transfer of a channel may consume that channel's notes, so a stake held there could be named as an input by a rival and tied up for a window. It also means a sequencer needs no funds inside the channels it serves. Staked notes keep taking part in Proof of Stake, so collateral costs a sequencer liquidity rather than yield.

The requirement counts inputs, not outputs. Merging lets a transfer consume a thousand notes into one output, and it is the holders of the inputs who are locked out.

A lost transfer forfeits its `required`: half pays the challenger and the rest goes to the pending rewards pool, as fees do (see [Block Rewards](block-rewards.md)). The challenger gets only half because the challenger may be the sequencer itself, under a second key: paid in full, it would recover its forfeit and lock any number of notes for the price of gas. A transfer undone with it keeps its `required` at risk and is judged on its own challenge, so a large transfer cannot escape its requirement by depending on a small one made to lose, and an honest one loses nothing. Locking `n` notes therefore costs `n` times the per-input requirement, while one challenge covers the whole transfer.

A stake is taken from its notes in the order they were staked. The last note taken is split: the excess is re-created under the same key and stays staked.

An answer bonds the fee-priced floor at the prices of its own block:

```python
def answer_bond() -> TokenValue:
    return checked_uint64(COLLATERAL_MARGIN * fee_cost(FLOOR_GAS, FLOOR_BYTES))
```

### Pools

A pool is value in a zone that no single user owns, such as an AMM reserve. Nobody can sign for it, so a Risc0 program governs it and a proof that the program ran replaces the authorization. `image_id` names the program and `instance_id` the pool among those running it.

```python
class PoolEntry:
    channel: ChannelId
    image_id: ImageId  # the Risc0 program the pool runs
    state: zkhash      # opaque to the ledger

def pool_key(image_id: ImageId, instance_id: InstanceId, intent_hash: zkhash) -> ZkPublicKey:
    fr = lambda x: FiniteField(x, byte_order="little", modulus=p)
    return zkhash(fr(b"RISC0_PROGRAM"), fr(image_id), instance_id, intent_hash)
```

Every note held by or sent to a pool carries a pool key. Reserves use `intent_hash = 0`. A deposit uses `intent_hash = zkhash(intent)`, the intent being what the sender wants done, in a form the program defines, typically a recipient, a minimum output, a refund key and a salt. Sending to a pool is an ordinary authorization with an output under the pool key. No secret key exists behind a pool key, so pool notes move only through pool steps.

The intent in the key ties the program's inputs to the deposit paying for them. A pool step gives the `intent_hash` of each note it consumes, and the ledger recomputes the note's key from it. The same `intent_hash` is in the journal the proof commits to, so the program was handed exactly the intent the note carries, and an answer cannot drop a swap and treat the deposit as a gift to the reserves. Two deposits with byte-identical intents would share a key and merge, which is why an intent carries a salt.

The ledger keeps each pool's state, so an answer cannot start from a state of its choosing, and only transfers of the pool's channel may advance it. A transfer declares, for each pool it moves, `state_before` and `new_state`; posting checks the first against the entry and writes the second, as it does for the channel tip. A pool advances at most once per transfer, everything that happened to it in the meantime folding into one transition. A transfer may declare a transition without moving any note, which a private pool needs to advance its roots, and the per-transition part of the collateral prices it, since it would otherwise cost nothing to post.

A pool step for the declared transition `s`, consuming `notes`, is valid when:

```python
image_id = pools[step.instance_id].image_id
for note, consumed in zip(notes, step.consumed):
    assert note.value == consumed.value
    assert note.public_key == pool_key(image_id, step.instance_id, consumed.intent_hash)
journal = PoolJournal(step.instance_id, s.state_before, s.new_state, step.consumed, step.created)
assert risc0_verify(image_id, sha256(encode(journal)), step.seal)
```

The value check matters as much as the key. Without it, an answer could state a deposit smaller than it is, the program would pay less, and the step would still balance against the real value, the difference going to an output of the answerer's choice. The ledger checks ownership by hashing and the program checks intent and logic by proving. The ledger guarantees that the program ran from the recorded state and was handed every intent, not that it honours them: a program that ignores intents still produces valid proofs.

`POOL_CREATE` creates a pool with derived identifiers:

```python
def derive_instance_id(channel: ChannelId, image_id: ImageId, params_hash: zkhash) -> InstanceId:
    fr = lambda x: FiniteField(x, byte_order="little", modulus=p)
    return zkhash(fr(b"POOL_INSTANCE"), fr(channel), fr(image_id), params_hash)

def derive_pool_genesis(image_id: ImageId, params_hash: zkhash) -> zkhash:
    fr = lambda x: FiniteField(x, byte_order="little", modulus=p)
    return zkhash(fr(b"POOL_GENESIS"), fr(image_id), params_hash)
```

The ledger derives both. A creator choosing them could register the identifier users compute for themselves, so their deposits land, with a starting state in which it already owns the reserves, and no challenge would catch it. With derived identifiers, whoever creates a pool first creates the pool others wanted. A salt in the parameters separates two pools running the same program. Entries are never removed, and since creation is not part of a transfer, a lost transfer does not undo it.

### Forced Transfers

A holder censored by the sequencers leaves with a `TRANSFER` once the note is unlocked. To pay inside the channel or into a pool, the holder forces the authorization instead, in two steps. `CHANNEL_REGISTER_AUTH` verifies it and records its slot, giving the ledger a clock. Between `FORCE_DELAY` and `2 * FORCE_DELAY` slots later, anyone may apply it with `CHANNEL_FORCE_TRANSFER`, whose outputs are final at once. If a transfer applied it in the meantime, its inputs are gone and forcing fails.

The delay keeps forcing from becoming an attack on the zone. Without it, anyone holding an authorization that a sequencer had netted could post it first, invalidating the netted transfer and the inscription carrying it, and stall the zone for one transaction per turn. A forced transfer never advances a pool state, and a registered authorization is public before it applies.

### Following a Channel

The ledger checks note moves, not zone semantics. A zone that bridges funds **follows every move of its channel notes and credits only what the same Mantle Transaction backs**. The unit is the transaction because Mantle executes a transaction atomically, which lets a `TRANSFER` out of one channel sit next to that channel's inscription in a [cross-channel transfer](template-cross-channel-messaging.md#synchronous-messaging).

- A move carrying no message, a `TRANSFER` out of the channel or a forced transfer, debits the keys of the channel notes it consumes and credits the keys of the channel notes it creates.
- A lost transfer is undone on the ledger, with the transfers depending on it, while their inscriptions stay. The zone re-executes its history from the lost inscription by a deterministic rule, so that all its followers agree. [\[Template\] Bridged Zone](template-bridged-zone.md#default-rule-for-lost-transfers) gives a default one: drop the messages posted since the lost inscription, and keep following the note moves that still stand.
- Every zone effect that touches bridged value is provisional until the transfer backing it is final.

### Bridging State

Validators maintain the following state for bridging, next to `channels` and the [Ledger](#ledger):

```python
pools: dict[InstanceId, PoolEntry]               # see Pools
pending_transfers: dict[OpId, PendingTransfer]   # iterated in the order the transfers were posted
registrations: dict[zkhash, Slot]                # slot each authorization was registered at, by auth_msg
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]

InstanceId = zkhash
ImageId = bytes      # 32 bytes: the Risc0 image ID, the digest identifying a program
OpId = hash          # identifier of an Operation, see derive_op_id

class PoolTransition:
    instance_id: InstanceId
    state_before: zkhash
    new_state: zkhash

class ConsumedInput:
    note_id: NoteId
    note: Note                  # kept: the transfer removed the note from the ledger
    locked_by: OpId | None      # the pending transfer that created the note, if it was locked

class Challenge:
    bond: NoteId
    settled: bool               # a valid answer has been posted

class PendingTransfer:
    channel: ChannelId
    sequencer: Ed25519PublicKey
    slot: Slot                  # slot of the block that included the transfer
    inputs: list[ConsumedInput]
    outputs: list[Note]
    declared: list[PoolTransition]
    required: TokenValue        # collateral the transfer puts at risk
    depends_on: set[OpId]
    challenge: Challenge | None
    undone: bool                # undone with a lost transfer it depended on, and still answerable

class SequencerStake:
    notes: list[NoteId]         # staked notes, in the order they were staked
    at_risk: TokenValue         # sum of `required` over the sequencer's pending transfers
```

### Bridging Parameters

| Parameter | Value | Role |
| --- | --- | --- |
| `CHALLENGE_WINDOW` | 64,800 slots | How long a posted transfer may be challenged |
| `RESPONSE_WINDOW` | 64,800 slots | How long after the challenge window an answer may still arrive |
| `FORCE_DELAY` | 64,800 slots | How long a registered authorization waits before it can be forced, and how long it can then be forced |
| `COLLATERAL_MARGIN` | 2 | Margin on the fee prices of the dispute |
| `FLOOR_GAS`, `FLOOR_BYTES` | 8,980 gas, 800 bytes | Fee-priced collateral of any transfer, and the answer bond |
| `INPUT_GAS`, `INPUT_BYTES` | 590 gas, 400 bytes | Fee-priced collateral per input |
| `STATE_GAS`, `STATE_BYTES` | 590 gas, 300 bytes | Fee-priced collateral per declared pool transition |
| `STATE_PROVING` | one GPU-hour, in LGO at the genesis price | Collateral per declared pool transition for its off-chain proof |
| `VALUE_RATE_PPM` | 5,000, that is 0.5% | Collateral per unit of value of the inputs that could have aged |
| `RISC0_CONTROL_ROOT`, `RISC0_BN254_CONTROL_ID`, `RISC0_GROTH16_VK` | those of the pinned Risc0 release | [Risc0 receipt verification](#risc0-receipt-verification) |

The windows are ledger parameters and not part of a channel's configuration, since a captured configuration would set them to zero. Each equals the finality depth $`\lfloor k/f \rfloor`$ of [Cryptarchia](cryptarchia-v1-protocol.md#constants), about 18 hours, so keeping a challenge or an answer out of the chain for a whole window takes every leader of that period refusing it. Together they stay below one epoch, 648,000 slots, the shortest time a note needs to become eligible for leadership. Every transfer is resolved by `slot + CHALLENGE_WINDOW + RESPONSE_WINDOW` (see [Channel Transfer Resolution](#channel-transfer-resolution)), so a locked note is never eligible, and a transfer that is later undone never earns its outputs a Proof of Leadership reward.

The collateral parameters are derived in [\[Analysis\] Channel Collateral](analysis-channel-collateral.md). The fee-priced ones follow the size and gas of a challenge, of an answer's fixed part and of its steps. `STATE_PROVING` sizes the heaviest proof, a private pool's transition, and awaits a measurement on reference hardware. `VALUE_RATE_PPM` makes suppressing stake from the leadership lottery unprofitable while the inferred stake is below its target, and can fall towards 1,500 once it is reached. A challenger bonds what the transfer requires, so the same amounts are what a wrong challenge pays the answerer for the work it forced.

### Bridging Security Considerations

- **Watchtowers.** An unchallenged transfer becomes final. A sequencer can lock a note again every window by naming it in transfers it cannot back, and pays for it only when someone challenges. Leaving the channel is available whenever someone is willing to challenge, not unconditionally.
- **Sequencer availability.** A transfer nobody answers within the response window loses, even if it is valid. Running a sequencer means keeping the authorizations of every pending transfer and being able to answer at any time.
- **Pool liveness.** A holder can get their own notes out without the sequencers, but pool value moves only when a sequencer posts. Under round-robin sequencing, a group holding the configuration threshold can remove every honest sequencer and hold pool value hostage. A single accredited sequencer can also stall a pool for up to both windows by declaring a transition nobody can prove: the others cannot build on it, and cannot declare from another state. It forfeits its collateral each time, which does not grow with the pool's value, so the remedy is to remove its key with a `CHANNEL_CONFIG`.
- **Programs.** A pool's `image_id` is in the key of every note it holds, so a pool cannot be upgraded: only a migration path the program provides can move its value. Anything a program reads that is neither in its state nor in the keys of the notes it consumes, an oracle price for instance, is chosen by whoever answers.
- **Native token only.** A note carries no asset type, so only LGO is protected.
- **Lost keys.** Nobody can move a channel note whose key is lost.
- **Privacy.** A registered authorization publishes its inputs, outputs and values before it is applied.

### CHANNEL_INSCRIBE

Write a message to a channel with the message data being permanently stored on the Logos Blockchain, and optionally move the channel's notes with a [transfer](#transfers).

#### Payload

```python
class Inscribe:
    channel: ChannelId       # 32 bytes Channel being written to
    inscription : bytes      # Message to be written on the blockchain
    parent: hash             # Previous message in the channel
    signer: Ed25519PublicKey # Identity of message sender
    # Transfer part, empty when the inscription moves nothing
    inputs: list[NoteId]            # channel notes consumed, locked or not
    outputs: list[Note]             # channel notes created, sorted by public key
    declared: list[PoolTransition]  # pool states advanced
```

The inscription carries a transfer when any of `inputs`, `outputs` and `declared` is non-empty.

#### Proof

```python
Ed25519Signature
```

#### Execution Gas

  Channel Inscribe Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_INSCRIBE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
txhash: hash
msg: Inscribe
sig: Ed25519Signature

channels: dict[ChannelId, ChannelState]
pools: dict[InstanceId, PoolEntry]
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]
execution_gas_base_price: TokenValue    # Given by Execution Market
permanent_storage_gas_price: TokenValue # Given by Storage Market
ledger: Ledger
block_slot: Slot
```
 
  *Validate*

```python
has_transfer = msg.inputs or msg.outputs or msg.declared

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
    # A channel that does not exist holds no note and no pool
    assert not has_transfer

if has_transfer:
    # Inputs are notes of this channel, locked or not
    if msg.inputs:
        ledger.assert_spendable(msg.inputs, msg.channel)

    # Outputs are valid and sorted by strictly increasing public key, keys
    # compared as integers, the order an answer produces them in, which
    # also rules out two outputs under the same key
    ledger.assert_valid_output(msg.outputs)
    for a, b in zip(msg.outputs, msg.outputs[1:]):
        assert a.public_key < b.public_key

    # Value is conserved
    input_amount = checked_uint64(sum(ledger.get_note(i).value for i in msg.inputs))
    output_amount = checked_uint64(sum(o.value for o in msg.outputs))
    assert input_amount == output_amount

    # Each declared pool belongs to this channel, is declared once,
    # and starts from the state the ledger holds
    instances = [t.instance_id for t in msg.declared]
    assert len(instances) == len(set(instances))
    for t in msg.declared:
        assert t.instance_id in pools
        assert pools[t.instance_id].channel == msg.channel
        assert pools[t.instance_id].state == t.state_before

    # The signer's stake covers the collateral this transfer puts at risk
    assert msg.signer in sequencer_stakes
    stake = sequencer_stakes[msg.signer]
    required = required_collateral(msg.inputs, msg.declared)
    assert staked_value(stake) >= checked_uint64(stake.at_risk + required)

# Ensure the msg signer signature
assert Ed25519_verify(txhash, msg.signer, sig)
```

with

```python
def staked_value(stake: SequencerStake) -> TokenValue:
    return checked_uint64(sum(ledger.get_note(n).value for n in stake.notes))
```

#### Execution

  *Given*

```python
msg: Inscribe
sig: Ed25519Signature

channels: dict[ChannelId, ChannelState]
pools: dict[InstanceId, PoolEntry]
pending_transfers: dict[OpId, PendingTransfer]
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]
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

  4. If the inscription carries a transfer, execute it and record it as pending.
      ```python
      if msg.inputs or msg.outputs or msg.declared:
          op_id = derive_op_id(msg)
          # The requirement reads the inputs, so it is computed before they are spent
          required = required_collateral(msg.inputs, msg.declared)
          inputs = [ConsumedInput(note_id=i,
                                  note=ledger.get_note(i),
                                  locked_by=ledger.locked_notes.get(i))
                    for i in msg.inputs]

          # Depend on the creator of each locked input, and on the last
          # pending writer of each declared pool state
          depends_on = {c.locked_by for c in inputs if c.locked_by is not None}
          for t in msg.declared:
              writers = [w for w, p in pending_transfers.items()
                         if not p.undone
                         and any(d.instance_id == t.instance_id for d in p.declared)]
              if writers:
                  depends_on.add(writers[-1])
              pools[t.instance_id].state = t.new_state

          # Consume the inputs and create the outputs, locked
          ledger.execute_spending(msg.inputs, msg.channel)
          ledger.execute_adding(op_id, msg.outputs, msg.channel)
          for index, note in enumerate(msg.outputs):
              ledger.locked_notes[derive_note_id(op_id, index, note)] = op_id

          sequencer_stakes[msg.signer].at_risk += required
          pending_transfers[op_id] = PendingTransfer(
              channel=msg.channel, sequencer=msg.signer, slot=block_slot,
              inputs=inputs, outputs=msg.outputs, declared=msg.declared,
              required=required, depends_on=depends_on, challenge=None, undone=False)
      ```

#### Example

```python
# Build the inscription
greeting = Inscription(
    channel=CHANNEL_EARTH,
    inscription=b"Live long and prosper",
    parent=ZERO
    signer=spock_pk,
    inputs=[],
    outputs=[],
    declared=[]
)

# Build the transfer operation to pay the fees
transfer = Transfer(inputs=[<spocks_note_id>], outputs=[<change_note>])

# Wrap it in a transaction
tx = MantleTx(
    ops=[Op(opcode=CHANNEL_INSCRIBE, payload=encode(greeting)),
         Op(opcode=TRANSFER, payload=encode(transfer))],
)

# Sign the transaction
signed_tx = SignedMantleTx(
    tx=tx,
    op_proofs=[Ed25519_sign(mantle_txhash(tx), spock_sk),
               transfer.prove(spock_sk)]
)

# Send the transaction to the mempool
mempool.push(signed_tx)
```

A transfer nets authorizations. Alice and Bob each pay Carol 25 out of a note of 50, and Carol's two claims merge into one output:

```python
# Each holder signs an authorization of their own note, and hands it to the sequencer
alice_auth = ZkSignature_sign(auth_msg(ZONE_A, [alice_note_id],
                                       [Note(25, carol_pk), Note(25, alice_pk)]), [alice_sk])
bob_auth = ZkSignature_sign(auth_msg(ZONE_A, [bob_note_id],
                                     [Note(25, carol_pk), Note(25, bob_pk)]), [bob_sk])

# The sequencer posts the netted transfer with the zone's message, outputs sorted by key
payment = Inscribe(
    channel=ZONE_A,
    inscription=b"<zone state transition paying Carol>",
    parent=zone_a_tip,
    signer=sequencer_pk,
    inputs=[alice_note_id, bob_note_id],
    outputs=sorted([Note(50, carol_pk), Note(25, alice_pk), Note(25, bob_pk)],
                   key=lambda note: note.public_key),
    declared=[]
)
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

  2. Ensure all inputs are spendable and not already channel notes.
      ```python
      ledger.assert_spendable(deposit.inputs)
      ```

  3. Validate ownership over deposited notes.
      ```python
      input_notes = [ledger[input_note_id] for input_note_id in deposit.inputs]
      assert ZkSignature_verify(mantle_txhash, deposit_proof, distinct_keys(input_notes))
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
- Make the inscription conditional on the deposit, by consuming the deposited note in the inscription's own transfer part. The inscription is then valid only if the deposited note exists, and a reorganization cannot keep one without the other. This removes the waiting period entirely.

The second option resets the ageing of the value, since a transfer consumes its inputs and creates new notes. A `CHANNEL_DEPOSIT` resets ageing for the same reason, and so does leaving the channel with a `TRANSFER`.

### CHANNEL_REGISTER_AUTH

Register an [authorization](#authorizations), so that it can be [forced](#forced-transfers) once `FORCE_DELAY` has passed.

#### Payload

```python
class RegisterAuth:
    channel: ChannelId
    inputs: list[NoteId]  # channel notes the authorization consumes
    outputs: list[Note]   # notes it creates
```

#### Proof

The authorization itself: a [ZkSignature](#zero-knowledge-signature-scheme-zksignature) over `auth_msg(channel, inputs, outputs)` rather than over the `mantle_txhash`. Anyone holding the authorization may register it.

```python
ZkSignature
```

#### Execution Gas

  Register Authorization Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_REGISTER_AUTH_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
register: RegisterAuth
proof: ZkSignature

channels: dict[ChannelId, ChannelState]
registrations: dict[zkhash, Slot]
ledger: Ledger
```

  *Validate*

```python
assert register.channel in channels

# Inputs are notes of the channel. They may still be locked: the authorization
# may be waiting in a pending transfer, and can only be forced once unlocked.
ledger.assert_spendable(register.inputs, register.channel)
ledger.assert_valid_output(register.outputs)
input_notes = [ledger.get_note(i) for i in register.inputs]
input_amount = checked_uint64(sum(n.value for n in input_notes))
output_amount = checked_uint64(sum(o.value for o in register.outputs))
assert input_amount == output_amount

msg = auth_msg(register.channel, register.inputs, register.outputs)
assert msg not in registrations
assert ZkSignature_verify(msg, proof, distinct_keys(input_notes))
```

#### Execution

  *Given*

```python
register: RegisterAuth
registrations: dict[zkhash, Slot]
block_slot: Slot
```

  *Execute*

```python
registrations[auth_msg(register.channel, register.inputs, register.outputs)] = block_slot
```

### CHANNEL_FORCE_TRANSFER

Apply a registered authorization that no transfer has applied.

#### Payload

```python
class ForceTransfer:
    channel: ChannelId
    inputs: list[NoteId]
    outputs: list[Note]
```

#### Proof

None. The authorization was verified when it was registered, and the payload must reproduce it exactly.

```python
EmptyProof
```

#### Execution Gas

  Force Transfer Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_FORCE_TRANSFER_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
force: ForceTransfer
registrations: dict[zkhash, Slot]
ledger: Ledger
block_slot: Slot
```

  *Validate*

```python
msg = auth_msg(force.channel, force.inputs, force.outputs)
assert msg in registrations
assert FORCE_DELAY <= block_slot - registrations[msg] < 2 * FORCE_DELAY

# Inputs are unlocked notes of the channel. If a transfer applied the
# authorization meanwhile, they are gone and forcing fails.
ledger.assert_spendable(force.inputs, force.channel)
for note_id in force.inputs:
    assert note_id not in ledger.locked_notes
```

Value conservation and output validity were checked at registration, over the same notes.

#### Execution

  *Given*

```python
force: ForceTransfer
registrations: dict[zkhash, Slot]
ledger: Ledger
```

  *Execute*

```python
del registrations[auth_msg(force.channel, force.inputs, force.outputs)]
ledger.execute_spending(force.inputs, force.channel)
ledger.execute_adding(derive_op_id(force), force.outputs, force.channel)
```

The outputs are channel notes, unlocked: a forced transfer is final at once.

### CHANNEL_CHALLENGE

Challenge a [pending transfer](#transfers).

#### Payload

```python
class ChannelChallenge:
    transfer: OpId   # the challenged transfer
    bond: NoteId     # an ordinary note of the challenger
```

#### Proof

A [ZkSignature](#zero-knowledge-signature-scheme-zksignature) over the `mantle_txhash` by the key of the bond note.

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
proof: ZkSignature

pending_transfers: dict[OpId, PendingTransfer]
ledger: Ledger
block_slot: Slot
```

  *Validate*

```python
assert challenge.transfer in pending_transfers
t = pending_transfers[challenge.transfer]

# One challenge per transfer, within its challenge window
assert t.challenge is None
assert block_slot < t.slot + CHALLENGE_WINDOW

# The bond is an ordinary note worth the collateral the transfer put at risk
ledger.assert_spendable([challenge.bond], None)
bond = ledger.get_note(challenge.bond)
assert bond.value >= t.required
assert ZkSignature_verify(mantle_txhash, proof, [bond.public_key])
```

#### Execution

  *Given*

```python
challenge: ChannelChallenge
pending_transfers: dict[OpId, PendingTransfer]
ledger: Ledger
```

  *Execute*

```python
ledger.bond_notes.add(challenge.bond)
pending_transfers[challenge.transfer].challenge = Challenge(bond=challenge.bond, settled=False)
```

### CHANNEL_ANSWER

Answer a challenge with the full accounting of the transfer (see [Challenges and Answers](#challenges-and-answers)).

#### Payload

```python
class UserStep:
    inputs: list[NoteId]   # transfer inputs, at least one
    outputs: list[Note]
    proof: ZkSignature     # the authorization, over auth_msg(channel, inputs, outputs)

class PoolInput:
    ref: NoteId | tuple[u16, u16]  # a transfer input, or the (step_index, output_index)
                                   # of a note created by an earlier step
    value: TokenValue
    intent_hash: zkhash

class PoolStep:
    instance_id: InstanceId
    consumed: list[PoolInput]
    created: list[Note]
    seal: Groth16Proof     # Risc0 receipt of the pool's program, wrapped in Groth16

class ChannelAnswer:
    transfer: OpId
    bond: NoteId           # an ordinary note of the answerer
    steps: list[UserStep | PoolStep]
```

#### Proof

A [ZkSignature](#zero-knowledge-signature-scheme-zksignature) over the `mantle_txhash` by the key of the bond note. The proofs the steps carry are part of the payload.

```python
ZkSignature
```

#### Execution Gas

  Channel Answer Operations have a linear Execution Gas cost equal to `EXECUTION_CHANNEL_ANSWER_GAS + 2 * EXECUTION_ANSWER_BATCH_GAS + EXECUTION_ANSWER_PROOF_GAS * len(steps)`: the bond's `ZkSignature`, the fixed cost of the answer's two batches and one proof per step. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
answer: ChannelAnswer
proof: ZkSignature

pending_transfers: dict[OpId, PendingTransfer]
execution_gas_base_price: TokenValue    # Given by Execution Market
permanent_storage_gas_price: TokenValue # Given by Storage Market
ledger: Ledger
block_slot: Slot
```

  *Validate*

```python
assert answer.transfer in pending_transfers
t = pending_transfers[answer.transfer]

# The transfer has an open challenge and its response window is not over
assert t.challenge is not None
assert not t.challenge.settled
assert block_slot < t.slot + CHALLENGE_WINDOW + RESPONSE_WINDOW

# The bond is an ordinary note worth at least answer_bond()
ledger.assert_spendable([answer.bond], None)
bond = ledger.get_note(answer.bond)
assert bond.value >= answer_bond()
assert ZkSignature_verify(mantle_txhash, proof, [bond.public_key])
```

Validation stops there: whether the answer holds is decided at execution, and a wrong answer leaves the Operation valid (see [Validation](#validation)).

#### Execution

  *Given*

```python
answer: ChannelAnswer
pools: dict[InstanceId, PoolEntry]
pending_transfers: dict[OpId, PendingTransfer]
ledger: Ledger
```

  *Execute*

```python
t = pending_transfers[answer.transfer]
if answer_holds(t, answer):
    # The challenge is settled and the challenger's bond pays the answerer
    challenger_bond = ledger.get_note(t.challenge.bond)
    answerer = ledger.get_note(answer.bond).public_key
    ledger.bond_notes.remove(t.challenge.bond)
    ledger.execute_spending([t.challenge.bond], None)
    ledger.execute_adding(derive_op_id(answer), [Note(challenger_bond.value, answerer)], None)
    t.challenge.settled = True
else:
    # A wrong answer forfeits its bond to the rewards pool and leaves the challenge open
    route_to_rewards_pool(ledger.get_note(answer.bond).value)
    ledger.execute_spending([answer.bond], None)
```

`answer_holds` implements the seven checks of [Challenges and Answers](#challenges-and-answers). Its sums are exact: a sum that does not fit a `TokenValue` makes the answer wrong, not the transaction invalid.

```python
def answer_holds(t: PendingTransfer, answer: ChannelAnswer) -> bool:
    inputs = {c.note_id: c.note for c in t.inputs}
    declared = {s.instance_id: s for s in t.declared}
    spent = set()     # transfer inputs consumed so far
    open_notes = {}   # notes created by a step and not consumed yet, by (step_index, output_index)
    proven = set()    # pool transitions proven so far
    auths, receipts = [], []

    for step_index, step in enumerate(answer.steps):
        if isinstance(step, UserStep):
            refs, created = step.inputs, step.outputs
            if not refs:
                return False
        else:
            refs, created = [c.ref for c in step.consumed], step.created

        # 1, 2, 3: a transfer input consumed once, or a note an earlier step created
        consumed = []
        for ref in refs:
            if ref in inputs and ref not in spent:
                spent.add(ref)
                consumed.append(inputs[ref])
            elif ref in open_notes:
                consumed.append(open_notes.pop(ref))
            else:
                return False

        # 4: value is conserved and every created note has a valid value
        if any(not 0 < o.value <= UINT64_MAX for o in created):
            return False
        if sum(n.value for n in consumed) != sum(o.value for o in created):
            return False
        for output_index, note in enumerate(created):
            open_notes[(step_index, output_index)] = note

        if isinstance(step, UserStep):
            # 6: the authorization, verified in the answer's batch
            auths.append((auth_msg(t.channel, step.inputs, step.outputs),
                          step.proof, distinct_keys(consumed)))
        else:
            # 7: the pool step proves one declared transition, from the right notes
            if step.instance_id not in declared or step.instance_id in proven:
                return False
            proven.add(step.instance_id)
            transition = declared[step.instance_id]
            image_id = pools[step.instance_id].image_id
            for note, c in zip(consumed, step.consumed):
                if note.value != c.value:
                    return False
                if note.public_key != pool_key(image_id, step.instance_id, c.intent_hash):
                    return False
            journal = PoolJournal(step.instance_id, transition.state_before,
                                  transition.new_state, step.consumed, step.created)
            receipts.append((image_id, sha256(encode(journal)), step.seal))

    # 2: every input consumed, 7: every declared transition proven
    if spent != set(inputs) or proven != set(declared):
        return False

    # 5: the notes nobody consumed are the claims; summed per key and
    # sorted by key, they are the transfer's outputs
    claims = {}
    for note in open_notes.values():
        claims[note.public_key] = claims.get(note.public_key, 0) + note.value
    if [Note(value=v, public_key=k) for k, v in sorted(claims.items())] != t.outputs:
        return False

    # 6, 7: the proofs, each kind in its own batch
    return (zksig_batch_verify(auths, answer)
            and risc0_batch_verify(receipts, answer))
```

`PoolJournal` is the journal the pool's program commits to, encoded as specified in [Mantle Transaction Encoding](mantle-transaction-encoding.md#channel-operations). `zksig_batch_verify` and `risc0_batch_verify` verify all the proofs of one kind in a single batch, with coefficients derived from the answer (see [Batch verification of ZK proofs](bedrock-v1.1-block-construction.md#answer-batches)), and return whether the batch holds. A `ZkSignature` item is verified as `ZkSignature_verify(msg, proof, keys)`, a Risc0 item as specified in [Risc0 Receipt Verification](#risc0-receipt-verification).

#### Example

The answer to a challenge of the `payment` transfer of the [`CHANNEL_INSCRIBE` example](#channel_inscribe):

```python
answer = ChannelAnswer(
    transfer=derive_op_id(payment),
    bond=answerer_bond_note_id,
    steps=[UserStep(inputs=[alice_note_id],
                    outputs=[Note(25, carol_pk), Note(25, alice_pk)],
                    proof=alice_auth),
           UserStep(inputs=[bob_note_id],
                    outputs=[Note(25, carol_pk), Note(25, bob_pk)],
                    proof=bob_auth)])
```

Each input is consumed once and each step balances. No step consumes another's notes, so all four are claims, and summed per key they give Carol 50, Alice 25 and Bob 25: the transfer's outputs. Had the sequencer posted `Carol(25), Alice(25), Bob(25), Seq(25)` instead, the claims would not match and the answer could not hold.

### POOL_CREATE

Create a [pool](#pools) in a channel.

#### Payload

```python
class PoolCreate:
    channel: ChannelId
    image_id: ImageId      # the Risc0 program the pool runs
    params_hash: zkhash   # the pool's parameters, salt included
```

#### Proof

None. Both identifiers are derived, so whoever creates the pool creates the same one.

```python
EmptyProof
```

#### Execution Gas

  Pool Create Operations have a fixed Execution Gas cost of `EXECUTION_POOL_CREATE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
create: PoolCreate
channels: dict[ChannelId, ChannelState]
pools: dict[InstanceId, PoolEntry]
```

  *Validate*

```python
assert create.channel in channels
assert derive_instance_id(create.channel, create.image_id, create.params_hash) not in pools
```

#### Execution

  *Given*

```python
create: PoolCreate
pools: dict[InstanceId, PoolEntry]
```

  *Execute*

```python
instance_id = derive_instance_id(create.channel, create.image_id, create.params_hash)
pools[instance_id] = PoolEntry(channel=create.channel,
                               image_id=create.image_id,
                               state=derive_pool_genesis(create.image_id, create.params_hash))
```

### CHANNEL_STAKE

Stake ordinary notes as the [collateral](#collateral) of a sequencer key.

#### Payload

```python
class ChannelStake:
    sequencer: Ed25519PublicKey  # the accredited key the stake backs
    notes: list[NoteId]          # ordinary notes
```

#### Proof

A [ZkSignature](#zero-knowledge-signature-scheme-zksignature) over the `mantle_txhash` by the keys of the staked notes. It is what stops a sequencer from staking notes that are not its own.

```python
ZkSignature
```

#### Execution Gas

  Channel Stake Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_STAKE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
stake: ChannelStake
proof: ZkSignature
ledger: Ledger
```

  *Validate*

```python
# Ordinary notes only: not channel, service, staked or bond notes
ledger.assert_spendable(stake.notes, None)
notes = [ledger.get_note(n) for n in stake.notes]
assert ZkSignature_verify(mantle_txhash, proof, distinct_keys(notes))
```

#### Execution

  *Given*

```python
stake: ChannelStake
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]
ledger: Ledger
```

  *Execute*

```python
s = sequencer_stakes.setdefault(stake.sequencer, SequencerStake(notes=[], at_risk=0))
s.notes.extend(stake.notes)
for note_id in stake.notes:
    ledger.staked_notes[note_id] = stake.sequencer
```

Staked notes stay on the ledger and keep taking part in Proof of Stake, as service notes do.

#### Example

```python
# A sequencer of Zone A stakes a note of its own as collateral for its accredited key
stake = ChannelStake(sequencer=sequencer_pk, notes=[sequencer_stake_note_id])
transfer = Transfer(inputs=[<sequencer_funds>], outputs=[<change_note>])

tx = MantleTx(ops=[Op(opcode=CHANNEL_STAKE, payload=encode(stake)),
                   Op(opcode=TRANSFER, payload=encode(transfer))])
signed_tx = SignedMantleTx(tx=tx, op_proofs=[stake.prove(sequencer_zk_sk),
                                             transfer.prove(sequencer_zk_sk)])
```

### CHANNEL_UNSTAKE

Release staked notes that no pending transfer needs.

#### Payload

```python
class ChannelUnstake:
    sequencer: Ed25519PublicKey
    notes: list[NoteId]
```

#### Proof

A [ZkSignature](#zero-knowledge-signature-scheme-zksignature) over the `mantle_txhash` by the keys of the released notes.

```python
ZkSignature
```

#### Execution Gas

  Channel Unstake Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_UNSTAKE_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash: zkhash
unstake: ChannelUnstake
proof: ZkSignature
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]
ledger: Ledger
```

  *Validate*

```python
assert unstake.sequencer in sequencer_stakes
s = sequencer_stakes[unstake.sequencer]
assert len(unstake.notes) > 0
assert len(unstake.notes) == len(set(unstake.notes))
for note_id in unstake.notes:
    assert ledger.staked_notes.get(note_id) == unstake.sequencer

# What stays staked still covers the collateral of the pending transfers
notes = [ledger.get_note(n) for n in unstake.notes]
released = checked_uint64(sum(n.value for n in notes))
assert staked_value(s) - released >= s.at_risk
assert ZkSignature_verify(mantle_txhash, proof, distinct_keys(notes))
```

#### Execution

  *Given*

```python
unstake: ChannelUnstake
sequencer_stakes: dict[Ed25519PublicKey, SequencerStake]
ledger: Ledger
```

  *Execute*

```python
s = sequencer_stakes[unstake.sequencer]
for note_id in unstake.notes:
    s.notes.remove(note_id)
    del ledger.staked_notes[note_id]
```

A sequencer leaving a channel keeps its collateral at risk until its last transfer is resolved, since `at_risk` only falls then.

### Channel Transfer Resolution

At the start of each block, before its transactions, validators resolve the pending transfers as a function of the block's slot, as [Block Execution](bedrock-v1.1-block-construction.md#block-execution) specifies. It reads the ledger state and the slot, never the block's transactions.

```python
def resolve_channel_transfers(block_slot: Slot):
    # Registrations whose forcing window is over are dropped
    for msg, slot in list(registrations.items()):
        if block_slot - slot >= 2 * FORCE_DELAY:
            del registrations[msg]

    # A challenge still unanswered at the end of the response window loses
    for op_id, t in list(pending_transfers.items()):
        if (t.challenge is not None and not t.challenge.settled
                and block_slot >= t.slot + CHALLENGE_WINDOW + RESPONSE_WINDOW):
            lose(op_id)

    # A transfer whose own window is over is final once its dependencies are,
    # and an undone one is dropped. Pending transfers are visited in posting
    # order, so a transfer comes after the ones it depends on and one pass suffices.
    for op_id, t in list(pending_transfers.items()):
        if t.challenge is None:
            window_over = block_slot >= t.slot + CHALLENGE_WINDOW
        else:
            window_over = t.challenge.settled
        if window_over and (t.undone or not any(d in pending_transfers for d in t.depends_on)):
            finalize(op_id)
```

A final transfer releases its lock and its collateral. An undone transfer holds no lock any more, and releases its collateral only:

```python
def finalize(op_id: OpId):
    t = pending_transfers.pop(op_id)
    for note_id in [n for n, o in ledger.locked_notes.items() if o == op_id]:
        del ledger.locked_notes[note_id]
    sequencer_stakes[t.sequencer].at_risk -= t.required
```

A lost transfer forfeits its collateral and, unless an earlier loss already undid it, is undone with every transfer depending on it:

```python
def derive_redirect_id(lost_op_id: OpId) -> Hash:
    h = Hasher()  # /!\ a classic hash, as in derive_op_id /!\
    h.update(b"REDIRECT_V1")
    h.update(lost_op_id)
    return h.digest()

def lose(op_id: OpId):
    lost = pending_transfers[op_id]
    restored = [] if lost.undone else undo(op_id)
    del pending_transfers[op_id]

    # Half of the forfeit pays the challenger and the rest goes to the rewards
    # pool. The excess of the last staked note taken is re-created, still staked.
    challenger = ledger.get_note(lost.challenge.bond).public_key
    payout = [Note(value=lost.required // 2, public_key=challenger)] if lost.required >= 2 else []
    change = take_stake(lost.sequencer, lost.required)
    ids = ledger.execute_adding(derive_redirect_id(op_id),
                                payout + ([change] if change is not None else []),
                                None, first_index=len(restored))
    if change is not None:
        sequencer_stakes[lost.sequencer].notes.insert(0, ids[-1])
        ledger.staked_notes[ids[-1]] = lost.sequencer
    route_to_rewards_pool(lost.required - sum(n.value for n in payout))

    # The challenger's bond is released
    ledger.bond_notes.remove(lost.challenge.bond)
```

Undoing re-inserts no `NoteId`: the consumed notes are re-created under identifiers derived from the lost transfer. The undone transfers stay pending, marked, so that they can still be challenged and answered.

```python
def undo(op_id: OpId) -> list[ConsumedInput]:
    # The lost transfer and every transfer depending on it that still stands, in posting order
    undone = [op_id]
    for other, t in pending_transfers.items():
        if other != op_id and not t.undone and t.depends_on & set(undone):
            undone.append(other)
    records = [pending_transfers[u] for u in undone]
    for t in records:
        t.undone = True

    # Pools go back to the state before the first undone declaration
    for t in reversed(records):
        for s in t.declared:
            pools[s.instance_id].state = s.state_before

    # The notes the undone transfers created are removed
    removed = [n for n, o in ledger.locked_notes.items() if o in undone]
    if removed:
        ledger.execute_spending(removed, records[0].channel)

    # The notes they consumed from outside the undone set are re-created, under
    # the same keys. A note whose creator still stands, pending, stays locked by it.
    restored = [c for t in records for c in t.inputs if c.locked_by not in undone]
    ids = ledger.execute_adding(derive_redirect_id(op_id), [c.note for c in restored],
                                records[0].channel)
    for note_id, c in zip(ids, restored):
        creator = pending_transfers.get(c.locked_by)
        if creator is not None and not creator.undone:
            ledger.locked_notes[note_id] = c.locked_by
    return restored
```

Collateral is taken from the staked notes in the order they were staked, the last note taken being split:

```python
def take_stake(sequencer: Ed25519PublicKey, amount: TokenValue) -> Note | None:
    s = sequencer_stakes[sequencer]
    s.at_risk -= amount
    taken, last = 0, None
    while taken < amount:
        note_id = s.notes.pop(0)
        last = ledger.get_note(note_id)
        del ledger.staked_notes[note_id]
        ledger.execute_spending([note_id], None)
        taken += last.value
    # the excess of the last note taken stays staked
    return Note(value=taken - amount, public_key=last.public_key) if taken > amount else None
```

The loop always ends, since a sequencer's staked value never falls below its `at_risk`: posting checks it, unstaking checks it, and taking a forfeit lowers both by the same amount.

`route_to_rewards_pool(amount)` adds `amount` to the pending rewards pool and counts it in the block's $`R_\text{block}`$, as the fees of its transactions are (see [Block Rewards](block-rewards.md)). Forfeited value is pooled rather than destroyed, and total supply is unchanged.

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

      # A service note is an ordinary note: not a channel note,
      # and not already a sequencer's stake or a bond
      assert declaration.service_note_id not in ledger.channel_notes
      assert declaration.service_note_id not in ledger.staked_notes
      assert declaration.service_note_id not in ledger.bond_notes
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

  1. Ensure all inputs are spendable. An input may be a channel note that is not [locked](#transfers), which the Transfer takes out of its channel.
      ```python
      ledger.assert_spendable(transfer.inputs, None, leaving_channel=True)
      ```

  2. Validate transfer proof to show ownership over input notes.
      ```python
      input_notes = [ledger[input_note_id] for input_note_id in transfer.inputs]
      assert ZkSignature_verify(mantle_txhash, transfer_proof, distinct_keys(input_notes))
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

Channel notes are on-ledger notes minted to represent channel funds. They are distinct from Service Notes as they can’t be used to declare a service. However, they follow the same ageing rule as ordinary notes since they are part of the ledger and can be used for PoL creation once aged enough.

The system maintains a `channel_notes` set in the Ledger tracking all active channel `NoteId` and their respective `ChannelId`, and a `locked_notes` set tracking the channel notes created by a [transfer](#transfers) that is not final yet, with that transfer's `OpId`.

### Staked and Bond Notes

Staked notes are ordinary notes held as a sequencer's [collateral](#collateral), and bond notes are ordinary notes held by an open challenge. Like service notes, they stay in the Ledger and keep taking part in Proof of Stake, but cannot be spent until released.

## Ledger

```python
class Ledger:
    notes: list[Note]
    service_notes: dict[NoteId, ServiceNote]
    channel_notes: dict[NoteId, ChannelId]
    locked_notes: dict[NoteId, OpId]                # channel notes of a pending transfer
    staked_notes: dict[NoteId, Ed25519PublicKey]    # collateral, by sequencer key
    bond_notes: set[NoteId]                         # bonds of open challenges
```

### Input Notes Spendability Validation

A note is spendable if and only if it exists, it is not spent, and it is not a service, staked or bond note. A channel note is spendable by its channel's transfers, locked or not, and by a `TRANSFER` Operation once it is unlocked. The following function validates that an input of notes can be consumed:

```python
class Ledger:
    def assert_spendable(inputs: list[NoteId], channel_id: ChannelId | None,
                         leaving_channel: bool = False):
        # Assert inputs are not empty
        assert len(inputs) > 0

        # Check there is no duplicate
        assert len(inputs) == len(set(inputs))

        for note_id in inputs:
            assert ledger.is_unspent(note_id)
            assert note_id not in ledger.service_notes
            assert note_id not in ledger.staked_notes
            assert note_id not in ledger.bond_notes
            if channel_id is not None:
                # a note of this channel, locked or not
                assert ledger.channel_notes.get(note_id) == channel_id
            elif note_id in ledger.channel_notes:
                # only a Transfer takes a note out of its channel, once unlocked
                assert leaving_channel
                assert note_id not in ledger.locked_notes
```

### Output Notes Validation

Before an output of notes can be inserted into the Ledger, every note field must satisfy the following constraints:

```python
class Ledger:
    def assert_valid_output(outputs: list[Note]):
        for note in outputs:
            assert note.value > 0
            assert note.value <= 2**64-1
```

### Consuming Input Notes Execution

Consuming a set of notes removes them from the Ledger’s Merkle tree and recycles their leaf indices:

```python
class Ledger:
    def execute_spending(inputs: list[NoteId], channel_id: ChannelId | None):
        for note_id in inputs:
            # updates the merkle tree to zero out the leaf for this entry
            # and adds that leaf index to the list of unused leaves
            ledger.remove(note_id)
            # a channel note leaves its channel, and its lock, when consumed,
            # whether by its channel or by a Transfer
            ledger.channel_notes.pop(note_id, None)
            ledger.locked_notes.pop(note_id, None)
```

### Creating Output Notes Execution

Creating notes derives their `NoteId` from the Operation’s `OpId` and insert them in the Ledger. `first_index` lets an operation add its outputs in several calls:

```python
class Ledger:
    def execute_adding(op_id: Hash, outputs: list[Note], channel_id: ChannelId | None,
                       first_index: int = 0) -> list[NoteId]:
        output_note_ids = []
        for (output_index, output_note) in enumerate(outputs, start=first_index):
            output_note_id = derive_note_id(op_id, output_index, output_note)
            ledger.add(output_note_id)
            if channel_id is not None:
                ledger.channel_notes[output_note_id] = channel_id
            output_note_ids.append(output_note_id)
        return output_note_ids
```

# Appendix

## Gas Determination

From the [[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md), we get the table below:

| Constants | Value |
| --- | --- |
| EXECUTION_TRANSFER_GAS | 590 |
| EXECUTION_CHANNEL_INSCRIBE_GAS | 56 |
| EXECUTION_CHANNEL_CONFIG_GAS | 56 |
| EXECUTION_CHANNEL_DEPOSIT_GAS | 590 |
| EXECUTION_CHANNEL_REGISTER_AUTH_GAS | 590 |
| EXECUTION_CHANNEL_FORCE_TRANSFER_GAS | 0 |
| EXECUTION_CHANNEL_CHALLENGE_GAS | 590 |
| EXECUTION_CHANNEL_ANSWER_GAS | 590 |
| EXECUTION_ANSWER_BATCH_GAS | 3,900 |
| EXECUTION_ANSWER_PROOF_GAS | 590 |
| EXECUTION_POOL_CREATE_GAS | 0 |
| EXECUTION_CHANNEL_STAKE_GAS | 590 |
| EXECUTION_CHANNEL_UNSTAKE_GAS | 590 |
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

- The proof is bound to `msg` (it’s the `mantle_tx_hash` reduced modulo $`p`$ in case of transactions, and the `auth_msg` in case of [authorizations](#authorizations)).

  For implementation, the ZkSignature circuit will take a maximum of 32 public keys as inputs. To prove ownership of fewer keys, the remaining inputs will be padded with the public key corresponding to the secret key `0` and ignored during execution. The outputs have no size limit since they are included in the hashed message.

When the keys are those of notes, the list holds each distinct key once, in the order it first appears, so that spending many notes under one key takes one entry and the 32-key limit counts owners rather than notes:

```python
def distinct_keys(notes: list[Note]) -> list[ZkPublicKey]:
    keys = []
    for note in notes:
        if note.public_key not in keys:
            keys.append(note.public_key)
    return keys
```

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

## Risc0 Receipt Verification

A [pool step](#pools) carries the seal of a Risc0 receipt wrapped in Groth16 over BN254. It is verified against the program and the journal the ledger expects:

```python
def risc0_verify(image_id: ImageId, journal_digest: bytes, seal: Groth16Proof) -> bool:
    # The claim that program `image_id` ran to completion with exit code
    # Halted(0), committing to a journal whose SHA-256 digest is `journal_digest`
    claim = risc0_receipt_claim_digest(image_id, journal_digest, exit_code=Halted(0))
    control_root_0, control_root_1 = split_128(RISC0_CONTROL_ROOT)
    claim_0, claim_1 = split_128(claim)
    return groth16_verify(RISC0_GROTH16_VK, seal,
                          [control_root_0, control_root_1, claim_0, claim_1,
                           RISC0_BN254_CONTROL_ID])
```

`risc0_receipt_claim_digest`, `split_128` and `RISC0_GROTH16_VK` are those of the Risc0 release pinned by `RISC0_CONTROL_ROOT` and `RISC0_BN254_CONTROL_ID`. Adopting another release means changing these parameters. The verification key comes from Risc0's trusted setup, not from the [Logos one](trusted-setup-ceremony.md). In an answer, the receipts are verified in one batch, as `risc0_batch_verify`.

## Test Vectors

To see what the payloads represent, refer to [Mantle Transaction Encoding](mantle-transaction-encoding.md).

The `CHANNEL_CONFIG`, `CHANNEL_INSCRIBE`, `CHANNEL_WITHDRAW` and `CHANNEL_TRANSFER` vectors, and the transaction carrying one Operation of each kind, use the payloads in force before revision 1.16.0 and are to be regenerated from the implementation.

### Operation Id

| Operation | Payload | `op_id` |
| ------------------------- | - | - |
| `TRANSFER`                | 0x0201000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020300000000000000040000000000000000000000000000000000000000000000000000000000000005000000000000000600000000000000000000000000000000000000000000000000000000000000 | 0x5e5e1b318aa0c2aec93fbb327e6af5f705e5684269a34e0c1319539d00d06cdb |
| `CHANNEL_CONFIG`          | 0x0707070707070707070707070707070707070707070707070707070707070707000000000000000000000000000000000000000000000000000000000000000002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f6180a0000000b0000000c000d00 | 0x8bac7efe4c3ef10745c0d509ac88e2abaf1d3cda94987ed2eeb9ad71dd31d056 |
| `CHANNEL_INSCRIBE`        | 0x0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0b00000068656c6c6f206c6f676f730000000000000000000000000000000000000000000000000000000000000000d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c | 0xfb9af7fb1384fff51780ec8c5afbcba76449ab7603484f797df3a472e48826c1 |
| `CHANNEL_DEPOSIT`         | 0x1010101010101010101010101010101010101010101010101010101010101010011100000000000000000000000000000000000000000000000000000000000000100000006465706f7369742d6d65746164617461 | 0xf14ff0aad9bc5e8e30c5d1aa3710aaa1c1cc1f47c2c256e7d9e73104cb17ccaf |
| `CHANNEL_WITHDRAW`        | 0x1212121212121212121212121212121212121212121212121212121212121212011300000000000000000000000000000000000000000000000000000000000000 | 0x503d0d08f9faef971864943103965d13be7159fe6e0361c8ea614c6d0431e59c |
| `CHANNEL_TRANSFER`        | 0x14141414141414141414141414141414141414141414141414141414141414140115000000000000000000000000000000000000000000000000000000000000000116000000000000001700000000000000000000000000000000000000000000000000000000000000 | 0xfb24c17731954e8bbe1b0dedd69e4857c8083d1689aff331ba16f3ed5883f0ce |
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
