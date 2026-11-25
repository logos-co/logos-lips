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
| 1.16.0 | Gas Determination table updated for strict Ed25519 verification: channel Operations 56 → 59 Execution Gas per signature, `EXECUTION_SDP_DECLARE_GAS` 646 → 649, from [Gas Cost Determination](analysis-gas-cost-determination.md) 1.7.0 | 2026-09-24 |
| 1.17.0 | Bound channel inscription data and channel deposit metadata by `MAX_OPERATION_DATA_SIZE` as defined in Mantle Transaction Encoding; aligned SDP activity metadata and its test vectors with the tagged variant encoding. | 2026-10-06 |
| 1.18.0 | [RFC] The `declaration_id` is the hash of the service and the `zk_id`; a note backs one declaration per service, `SDP_WITHDRAW` no longer names the note, and a `nonce` carries the `created` epoch of its declaration | 2026-10-27 |
| 1.19.0 | `MinStake` holds `threshold` and the block number `timestamp`, following the Service Declaration Protocol | 2026-10-27 |
| 2.0.0 | Changed the UTXO ledger to private notes with transaction unlinkability, kept in a ledger, an SDP and one note set per channel but the null channel. Channel notes are moved by the steps their holders sign, each with its own inscription, grouped in the mini-blocks of an inscription, each proven against a recent root and the transaction buffer before its mini-block, and are withdrawn by their holders. Removed `LEADER_CLAIM`, `CHANNEL_TRANSFER` and the Example sections of the Operations, signed `SDP_ACTIVE` with the `provider_id`, made the `CLAIM_POW_REWARD` ticket publicly verifiable and independent of the epoch nonce, and moved `CLAIM_POW_REWARD` to the opcode `0x30`. A declaration names in `note_pk` the key of its service note, and `SDP_WITHDRAW` carries no nonce, consumes the service note, and releases its outputs with the channel withdrawals when its declaration is removed. A channel deposit carries an `inscription`. The commitment MMR and the nullifier IMT of a note set have depth `NOTE_SET_DEPTH` = 40, and a commitment root stays recent for `ROOT_WINDOW` = 1024 blocks | 2026-11-06 |
| 2.0.1 | The channel Operations are specified in Mantle Channels, the SDP Operations in the Service Declaration Protocol and the claim of proof of work rewards in Proof of Work; the Opcodes table links every Operation; the document is published as `bedrock-mantle.md`, links to Block Construction point to `bedrock-block-construction.md` and links to Mantle Transaction Encoding to `bedrock-mantle-encoding.md` | 2026-11-25 |
| 2.1.0 | A note carries a staking key, `stake_public_key`, hashed in its commitment, and a note whose staking key is `0` cannot lead. The Keys section derives the nullifier key `nf_sk` from the spending secret key and the public key from `nf_sk`, the nullifier hashes `nf_sk`, and the ZkTransfer proves the spending secret key; `PK0` and `NF_SK0` are the keys of the spending secret key `0`. The Opcodes table lists `ROLLUP_CREATE`, `ROLLUP_INSCRIBE`, `ROLLUP_DEPOSIT` and `ROLLUP_PROVE` at `0x40` to `0x43`: the excess value of `ROLLUP_DEPOSIT` pays fees, the proofs of `ROLLUP_PROVE` are bound to the `op_id` of the inscription they prove and verified against the live MMR of the rollup note set, and rollup channels share the note set indices of channels. The test vectors cover the rollup Operations and follow the encoding of `ChannelInscribe` and `SDPDeclare` | 2026-11-25 |

# Introduction

Mantle is a foundational element of Bedrock, designed to provide a minimal and efficient execution layer that connects together Bedrock Services in order to provide the necessary functionality for Zones. It can be viewed as the system call interface of Bedrock, exposing a safe and constrained set of Operations to interact with lower-level Bedrock services, similar to syscalls in an operating system.

Mantle Transactions provide Operations for Zones and blockchain Services to interact with Bedrock. For example, a Zone sequencer posting an update to Bedrock, or a node operator declaring its participation in the Blend Network, would be done through the corresponding Operations within a Mantle Transaction.

Mantle manages assets using a private note-based ledger that follows an UTXO model. Each Mantle Transaction can include Transfer Operation, and any excess balance serves as the fee payment.

# Overview

## Transactions

The features of the Logos Blockchain are exposed through [Mantle Transactions](#mantle-transaction). Each transaction can contain one or more **[Operations](#operations)**. Mantle Transactions enable users to execute multiple Operations atomically: the Operations are applied one after the other in the order they appear, and either all of them take effect or none does.

## Mantle Operations

Logos Blockchain features are exposed through [Mantle Operations](#opcodes), which can be combined in a single [Mantle Transaction](#mantle-transaction) and validated atomically. These Operations enable [transfers](#transfer) and functions such as [on-chain data posting](bedrock-mantle-channels.md#channel_inscribe), [Cross-Zone interactions](bedrock-architecture-overview.md#mantle-channels) and [SDP interaction](bedrock-service-declaration-protocol.md#service-declaration-protocol-sdp-operations).

## Private Ledger

The [Mantle Ledger](#mantle-ledger) enables [asset transfers](#transfer) using a private note-based ledger. The ledger tracks three kinds of [notes](#notes), each in [note sets](#ledger) of its own: regular notes, [service notes](#service-notes) (collateral for [service declarations](bedrock-service-declaration-protocol.md#declare)) and [channel notes](bedrock-mantle-channels.md#bridging) (the funds of [native](bedrock-mantle-channels.md) and [rollup channels](bedrock-mantle-rollups.md)). Every note participates in [Proof of Stake](cryptarchia-proof-of-leadership.md#eligible-sets) through its [staking key](#keys), unless that key is `0`. Each note set has a [commitment Merkle Mountain Range (MMR)](#commitment-merkle-mountain-range) and a [nullifier Indexed Merkle Tree (IMT)](#nullifier-indexed-merkle-tree).

## Transaction Fees

[Mantle Transaction fees](#mantle-transaction-fee) are derived from a gas model. The Logos Blockchain has two different gas markets, accounting for [permanent data storage](storage-markets.md), and [execution costs](execution-market.md). Each [Operation](#operations) has an associated [Execution Gas](#gas-determination) cost. Users can build unbalanced Mantle Transactions to [tip](execution-market.md#fee-distribution) the leaders and incentivize the network to include their transaction.

| Gas Market | Charged On | Pricing Basis |
| --- | --- | --- |
| Execution Gas | Operations | Operation dependent |
| [Permanent Storage Gas](storage-markets.md#core-fee-equation) | [Signed Mantle Transaction](#mantle-transaction-hash) | Proportional to encoded size |

# Mantle Transaction

Mantle Transactions form the core of Mantle, enabling users to combine multiple Operations to access different functions. Each transaction contains a list of Operations. The system validates the Operations atomically and executes them in the order they appear.

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

The [hash function used](common-cryptographic-components.md), as well as other cryptographic primitives like ZK proof generation protocol and signature schemes, are described in [Common Cryptographic Components](common-cryptographic-components.md).

## Mantle Transaction Hash

A Mantle Transaction must include all relevant proofs for each Operation.

```python
class SignedMantleTx:
    tx: MantleTx
    op_proofs: list[OpProof] # each Op has exactly 1 associated proof
```

Every Operation proof (zk proofs or signatures) must be cryptographically bound to the `MantleTx` through the `mantle_txhash` to prevent replay attacks. This binding is achieved by signing the 32-byte `mantle_txhash` digest with every Ed25519 signature, and by including it reduced modulo $`p`$ as a public input in every ZK proof. The exceptions are the [ZkTransfer](#zero-knowledge-transfer-proof-zktransfer) of a channel step, signed before the Mantle Transaction exists, which is bound to the step itself ([CHANNEL_INSCRIBE](bedrock-mantle-channels.md#channel_inscribe)), the ZkTransfers and the STF proof of a [ROLLUP_PROVE](bedrock-mantle-rollups.md#rollup_prove), which are bound to the `op_id` of the inscription they prove so that anyone can post them, and the empty proof of [CLAIM_POW_REWARD](proof-of-work.md#claim_pow_reward), whose ticket is bound to the public key it pays: a claim copied into another Mantle Transaction pays the same key, but invalidates the transaction it was copied from.

```python
mantle_txhash_fr = FiniteField(mantle_txhash, byte_order="little", modulus = p)
```

  `mantle_txhash` is a classical 256-bit hash digest and must be reduced to a field element before being passed to any ZkHasher or used as a ZK public input. We apply a direct modular reduction mod $`p`$ (via `FiniteField(..., modulus=p)`). Since $`p \approx 2^{254}`$, the reduction is slightly non-uniform. This is inconsequential in practice as the collision probability remains around $`2^{-254}`$, and proof binding is derived from the collision-resistance of the classic hash, not from uniformity over $`F_p`$.

## Arithmetic

All arithmetic in this specification is checked. Every addition, subtraction, and multiplication over transaction balance, gas amounts, and fees is performed on the stated integer type, and a Mantle Transaction is invalid if any intermediate or final result cannot be represented in that type; results must never silently wrap around or saturate. A `TokenValue` counts [LEPTA](overview-cryptoeconomics.md#token-units-and-precision). No token is minted after [Genesis](bedrock-genesis-block.md), so no token value exceeds the maximum supply of $`10^{19}`$ LEPTA ([Block Rewards](block-rewards.md)), which a `TokenValue` holds.

The pseudocode expresses these checks with the following helpers; a failed check makes the Mantle Transaction invalid:

```python
UINT64_MAX = 2**64 - 1

def checked_uint64(value: int) -> TokenValue:
        assert 0 <= value <= UINT64_MAX
        return value
```

The proof of work difficulty updates are the exception to these bounds; they are specified in [Puzzle Target](proof-of-work.md#puzzle-target).

## Mantle Transaction Fee

The transaction mandatory fee is a sum of two components: the multiplication of the total Execution Gas by the `execution_base_fee`, and the total size of the encoded signed Mantle Transaction multiplied by the `permanent_storage_gas_price`. The execution base fee and the permanent storage gas price are protocol-determined values that are the same for every Mantle Transaction in a block. They are derived following [[Execution Market](execution-market.md) and [Storage Markets](storage-markets.md).

```python
def mandatory_fees(signed_tx: SignedMantleTx,
                   tx_execution_gas: uint64,  # total Execution Gas of the Operations
                   permanent_storage_gas_price: TokenValue, # Given by Storage Market
                   execution_gas_base_price: TokenValue) -> uint64:  # Given by Execution Market
    permanent_storage_fees = checked_uint64(len(encode(signed_tx)) * permanent_storage_gas_price)
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

ledger: Ledger
channels: dict[ChannelId, ChannelState]
```

The state validation reads is not a fixed snapshot: it advances as the block is processed. A Mantle Transaction is validated against the state left by the Mantle Transactions preceding it in the block, as defined in [Block Proposal Validation](bedrock-block-construction.md#block-proposal-validation), and validation and execution then follow one another Operation by Operation, in the order the Operations appear: the Operation at index `i` is validated against the state the Operations at indices `0` to `i-1` left, then executed to produce the state the Operation at index `i+1` is validated against. This is what the `ledger`, `channels` and `declarations` given to each Operation denote.

The commitment MMRs of the [note sets](#ledger) that some Operations are proven against follow the same Operation by Operation progression, but locally to the Mantle Transaction. Every Operation adding notes to the ledger note set or to a channel note set appends their commitments to the buffer of that set for the Mantle Transaction, its `tx_commitment_buffer`, when validated, and every Operation referencing a commitment MMR root of a set references the root of that set at one of the last [`ROOT_WINDOW`](#ledger) blocks, against which it is verified once the buffer of the set is appended to it. A channel step, proven before the Mantle Transaction exists, is verified against its root extended with the buffer as it stands when its mini-block starts, so that its proof depends on what precedes its mini-block and not on its position inside it ([CHANNEL_INSCRIBE](bedrock-mantle-channels.md#channel_inscribe)). `SDP_WITHDRAW` references no root: its proof is verified against the root of an MMR holding only the service note of its declaration ([SDP_WITHDRAW](bedrock-service-declaration-protocol.md#sdp_withdraw)). `ROLLUP_PROVE` references no root either: its transfers are verified against the commitment MMR of the note set of its rollup as it stands, which only that Operation appends to, and it adds nothing to the buffer of that set ([ROLLUP_PROVE](bedrock-mantle-rollups.md#rollup_prove)). An Operation can therefore consume the outputs of a previous Operation of the same Mantle Transaction without waiting for a block to include them.

Atomicity is what a failed check means, not simultaneity. If any of the checks below fails, the whole Mantle Transaction is invalid: none of its Operations takes effect, whether or not it was reached. An invalid Mantle Transaction is never skipped over either, the block including it being invalid and nothing of that block being executed.

Mantle validators will ensure the following:

1. We have exactly one proof for each Operation, of the variant that Operation requires.
    ```python
    assert len(op_proofs) == len(ops)
    ```

2. Each Operation is valid, and takes effect before the next one is validated.
    ```python
    tx_balance = 0
    tx_execution_gas = 0
    for op, op_proof in zip(ops, op_proofs):
        assert op.opcode in MANTLE_OPCODES
        validate_mantle_op(mantle_txhash(tx), op.opcode, op.payload, op_proof)
        tx_execution_gas = checked_uint64(tx_execution_gas + execution_gas(op, ledger, channels))
        # the excess_value of these Operations pays the fees
        if op.opcode in (TRANSFER, CHANNEL_DEPOSIT, ROLLUP_DEPOSIT, SDP_WITHDRAW):
            tx_balance = checked_uint64(tx_balance + op.payload.excess_value)
        execute_mantle_op(op.opcode, op.payload)
    for note_set in note_sets_appended_to(tx):  # the note sets the transaction appended a commitment to
        note_set.tx_commitment_buffer = []  # the buffers start empty with every Mantle Transaction

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
                                      tx_execution_gas,
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

Mantle Validators execute each Operation in `ops` according to its opcode, in the order the Operations appear and along the state progression [Validation](#validation) defines. The [Opcodes](#opcodes) table links each opcode to the section that defines what validating and executing it amount to.

# Operations

## Opcodes

Each Operation is specified in the document of its protocol, and this table, the [Gas Determination](#gas-determination) table and the [Test Vectors](#test-vectors) cover them all.

| **Operation** | **Opcode** | **Description** |
| --- | --- | --- |
| [TRANSFER](#transfer) | 0x00 | Consume and create notes. |
| *RESERVED* | *0x01 - 0x0F* |  |
| [CHANNEL_CONFIG](bedrock-mantle-channels.md#channel_config) | 0x10 | Configure a channel |
| [CHANNEL_INSCRIBE](bedrock-mantle-channels.md#channel_inscribe) | 0x11 | Write a message permanently onto Mantle. |
| [CHANNEL_DEPOSIT](bedrock-mantle-channels.md#channel_deposit) | 0x12 | Deposit notes into a channel |
| [CHANNEL_WITHDRAW](bedrock-mantle-channels.md#channel_withdraw) | 0x13 | Withdraw notes from a channel |
| *RESERVED* | *0x14 - 0x1F* |  |
| [SDP_DECLARE](bedrock-service-declaration-protocol.md#sdp_declare) | 0x20 | Declare intention to participate as a node in a Bedrock Service, locking funds as collateral. |
| [SDP_WITHDRAW](bedrock-service-declaration-protocol.md#sdp_withdraw) | 0x21 | Withdraw participation from a Bedrock Service, consuming its service note in the process. |
| [SDP_ACTIVE](bedrock-service-declaration-protocol.md#sdp_active) | 0x22 | Signal that you are still an active participant of a Bedrock Service. |
| *RESERVED* | *0x23 - 0x2F* |  |
| [CLAIM_POW_REWARD](proof-of-work.md#claim_pow_reward) | 0x30 | Claim a reward from the pow reward pool. |
| *RESERVED* | *0x31 - 0x3F* |  |
| [ROLLUP_CREATE](bedrock-mantle-rollups.md#rollup_create) | 0x40 | Create a rollup channel with the verification key of its state transition function. |
| [ROLLUP_INSCRIBE](bedrock-mantle-rollups.md#rollup_inscribe) | 0x41 | Write the data of a state transition onto a rollup channel. |
| [ROLLUP_DEPOSIT](bedrock-mantle-rollups.md#rollup_deposit) | 0x42 | Deposit notes into a rollup channel, pending until a step mints them. |
| [ROLLUP_PROVE](bedrock-mantle-rollups.md#rollup_prove) | 0x43 | Apply the oldest unproven inscription of a rollup channel with a proven step. |
| *RESERVED* | *0x44 - 0x4F* |  |
| *RESERVED* | *0x50 - 0xFF* |  |

## Ledger Operations

### TRANSFER

Transfer prove the correct consumption and creation of notes. Because notes aren't transparent, this is done by a ZK proof (see [Zero Knowledge Transfer Proof (ZkTransfer)](#zero-knowledge-transfer-proof-zktransfer)), proving the correctness of the transfer and outputting the excess value of the transfer balance to pay for the fees.

A Transfer hides the commitments related to the nullifiers it's spending. It also hides the values, public keys and staking keys of its notes behind the created commitments. It reveals the nullifiers of the notes spent, the commitments of the created notes, their amount, the commitment root it names and its `excess_value` that is the difference between the value consumed and the value created.

#### Payload

```python
class Transfer:
    inputs: list[NoteNullifier]    # the list of consumed note nullifiers
                                   # must be non-empty
    outputs: list[NoteCommitment]  # the list of created note commitments
    commitment_root: MerkleRoot    # the MMR root of the ledger note set at the end of one of the last ROOT_WINDOW blocks
    excess_value: TokenValue       # the excess to pay the fees
```

#### Proof

  A Transfer proves the inputs, outputs and excess balance with a [Zero Knowledge Transfer Proof (ZkTransfer)](#zero-knowledge-transfer-proof-zktransfer).

```python
ZkTransfer
```

#### Execution Gas

  Transfer have a fixed Execution Gas cost of `EXECUTION_TRANSFER_GAS`. See [Gas Determination](#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
mantle_txhash_fr: zkhash # mantle_txhash of the tx containing this Operation, reduced modulo p
transfer: Transfer
transfer_proof: ZkTransfer

ledger: Ledger
```

  *Validate*

  1. Ensure all inputs are spendable.
      ```python
      ledger.sets[LEDGER_SET].assert_spendable(transfer.inputs)
      ```

  2. Validate transfer proof.
      ```python
      assert ledger.sets[LEDGER_SET].verify_transfer(transfer.inputs,
                                                     transfer.outputs,
                                                     transfer.excess_value,
                                                     transfer.commitment_root,
                                                     mantle_txhash_fr,
                                                     transfer_proof)
      ```

  3. Add the outputs to the buffer of the ledger note set.
      ```python
      ledger.sets[LEDGER_SET].tx_commitment_buffer.extend(transfer.outputs)
      ```

#### Execution

  *Given*

```python
transfer: Transfer

ledger: Ledger
```

  *Execute*

  1. Remove inputs from the ledger.
      ```python
      ledger.sets[LEDGER_SET].execute_spending(transfer.inputs)
      ```

  2. Add outputs to the ledger.
      ```python
      ledger.sets[LEDGER_SET].execute_adding(transfer.outputs)
      ```

# Mantle Ledger

## Notes

Notes are composed of four fields representing their value, their holder and their staker:

```python
class Note:
    value: TokenValue   # uint64
    nonce: NoteNonce	# to avoid two notes having the same commitment
    public_key: ZkPublicKey # 32 bytes, the holder, whose nullifier key derives the nullifier
    stake_public_key: ZkPublicKey  # 32 bytes, the staking key, whose secret the Proof of Leadership takes
```

`MerkleRoot`, `NoteCommitment`, `NoteNullifier` and `NoteNonce` are `zkhash` values, elements of $`\mathbb{F}_p`$. A `NoteCommitment` hashes the fields of a note and identifies it without revealing them, and a `NoteNullifier` hashes the commitment and the nullifier key of the holder and is published when the note is spent.

### Keys

The holder of a note keeps three secrets. Its spending secret key `spending_sk` derives its nullifier key `nf_sk`, which derives the `public_key` of the note, and its staking secret key `staking_sk` derives the staking key `stake_public_key` of the note:

```python
nf_sk = zkhash(FiniteField(b"NF_KDF_V1", byte_order="little", modulus= p), spending_sk)
public_key = zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), nf_sk)
stake_public_key = zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), staking_sk)
```

These derivations use the compression mode of Poseidon2 ([Common Cryptographic Components](common-cryptographic-components.md)), each over a single field element.

`PK0` and `NF_SK0` are the keys of the spending secret key `0`, which everyone knows:

```python
NF_SK0 = zkhash(FiniteField(b"NF_KDF_V1", byte_order="little", modulus= p), 0)
PK0 = zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), NF_SK0)
```

Anyone can spend a note `PK0` holds, such as the notes of a [rollup](bedrock-mantle-rollups.md) that chooses a key every prover knows. `NF_SK0` is public, so `PK0` should never be the staking key of such a note: anyone could lead with it, taking `NF_SK0` as nullifier key and as staking secret key.

- **Spending.** A [ZkTransfer](#zero-knowledge-transfer-proof-zktransfer) proves `spending_sk`, from which it derives `nf_sk`, then the `public_key` and the nullifier of the note. Spending a note takes `spending_sk`, and no other secret.
- **Leading.** A [Proof of Leadership](cryptarchia-proof-of-leadership.md#zero-knowledge-proof-statement) proves the `public_key` from `nf_sk`, which ties the nullifier it shows unspent to the note, and the `stake_public_key` from `staking_sk`, which derives the lottery ticket. The nullifier key sits between the spending secret key and the public key so that this proof never takes `spending_sk`.

No secret key is known whose public key is `0`, so a note whose staking key is `0` cannot lead. How a wallet chooses these keys, for cold staking and for a cold service declaration, is recommended in the [Wallet Technical Standard](wallet-technical-standard.md#staking-keys).

### Note Commitment and Nullifier

A note can be uniquely identified by its fields. Any two notes with the same fields share a commitment and a nullifier, so only one of them can be spent: value can be lost this way, never created. For notes the ledger creates itself, such as rewards and service notes, the nonce can be derived from the Operation that created it and its output number: `(op_id, output_number)` if each Operation are uniquely identifiable. For this reason, every Operation that output notes have a unique payload that is used to derive the Operation identifier. The deposit note of a [rollup step](bedrock-mantle-rollups.md#rollup_prove) derives its nonce from the `op_id` of the inscription the step proves.

```python
def derive_op_id(payload) -> Hash:
    op_bytes = encode(payload)
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"OPERATION_ID_V1")
    h.update(op_bytes)
    return h.digest()

def derive_note_nonce(op_id: Hash, output_number: int, value: TokenValue, public_key: ZkPublicKey) -> NoteNonce:
    return zkhash(
        FiniteField(b"NOTE_NONCE_V1", byte_order="little", modulus= p),
        FiniteField(op_id, byte_order="little", modulus= p),
        FiniteField(output_number, byte_order="little", modulus= p),
        FiniteField(value, byte_order="little", modulus= p),
        public_key
    )
    
def derive_note_commitment(note: Note) -> NoteCommitment:
    return zkhash(
        FiniteField(b"NOTE_CM_V1", byte_order="little", modulus= p),
        FiniteField(note.value, byte_order="little", modulus= p),
        note.nonce,
        note.public_key,
        note.stake_public_key
    )
	
def derive_note_nullifier(note_commitment: NoteCommitment, nf_sk: ZkSecretKey) -> NoteNullifier:
    return zkhash(
        FiniteField(b"NOTE_NF_V1", byte_order="little", modulus= p),
        note_commitment,
        nf_sk
    )
```

`op_id` is a classical 256-bit hash digest and must be reduced to a field element before being passed to the ZkHasher. We apply a direct modular reduction mod `p` (via `FiniteField(..., modulus=p)`). Since $`p \approx 2^{254}`$, the reduction is slightly non-uniform, values in $`[0, 2^{256} \mod p)`$ appear one extra time, but this is inconsequential in practice: the collision probability remains around $`2^{-254}`$, and `NoteNonce` uniqueness is not derived from uniformity of `op_id` over $`𝔽_p`$ but from the collision-resistance of the underlying hash and per-operation payload uniqueness.

These note commitments and nullifiers uniquely define notes in the system. Nodes maintain each [note set](#ledger) through an MMR for note commitments and an indexed merkle tree for note nullifiers.

### Service notes

Service notes are special notes in Mantle that serve as collateral for Service Declarations. Executing a Declare Operation consumes notes of the ledger note set and creates one service note under the declaration's `note_pk` and `note_stake_pk` in the SDP note set, its commitment kept with the declaration. A note of the SDP note set is spent only by the Withdraw Operation of its declaration, and the notes that withdrawal creates enter the ledger note set when the declaration is removed. Service notes participate in Proof of Stake.

## Ledger

The notes live in note sets, each with its own commitment MMR and nullifier IMT. A note belongs to one set from its creation until it is consumed, and is spent only by the Operations of that set:

| Note set | Index | Notes | Spent by |
| --- | --- | --- | --- |
| Ledger | `LEDGER_SET = 0` | the notes of transfers, rewards and withdrawals | Transfers, deposits and declarations |
| SDP | `SDP_SET = 1` | service notes | the Withdraw Operation of their declaration |
| Native channel | `2` onward, shared with rollup channels in the order the channels were created, the null channel having none | channel notes | the steps of the channel's inscriptions, and withdrawals |
| Rollup channel | `2` onward, shared with native channels in the order the channels were created | the notes of the rollup | the [`ROLLUP_PROVE`](bedrock-mantle-rollups.md#rollup_prove) Operations of the rollup only |

Two parameters fix the trees of a note set and how long their roots can be proven against:

```python
NOTE_SET_DEPTH = 40  # depth of the commitment MMR and of the nullifier IMT of every note set
ROOT_WINDOW = 1024   # number of blocks a commitment MMR root stays recent for the Operations
```

```python
class NoteSet:
    commitments: list[(MerkleRoot, int)]        # the peaks of the commitment MMR
    nullifiers: set[NoteNullifier]              # the set of nullifiers
    nullifier_leaves: list[NullifierLeaf]       # the leaves of the nullifier IMT, in insertion order
    current_commitment_root: MerkleRoot         # the commitment MMR root at the end of the previous block
    recent_commitment_roots: dict[MerkleRoot, RecentRoot]  # the current root and the roots of the last ROOT_WINDOW blocks
    tx_commitment_buffer: list[NoteCommitment]  # the commitments added by the previous Operations
                                                # of the Mantle Transaction, empty at its start

class RecentRoot:
    peaks: list[(MerkleRoot, int)]  # the peaks of the commitment MMR at this root
    last_block: BlockHeight | None  # the height of the last block at whose end this was the root
                                    # of the set, None for the current root

class Ledger:
    sets: list[NoteSet]  # indexed as in the table above
    # the channel and SDP withdrawals waiting for their due slot: (due slot, note set, inputs, outputs)
    pending_withdrawals: list[(Slot, int, list[NoteNullifier], list[NoteCommitment])]

def empty_note_set() -> NoteSet:
    return NoteSet(
        commitments=[],                       # an empty MMR has no peak
        nullifiers={0},                       # the nullifier of the sentinel leaf
        nullifier_leaves=[NullifierLeaf(0, 0)],  # an IMT holding only its sentinel leaf
        current_commitment_root=mmr_root([]),  # the root of the empty MMR
        recent_commitment_roots={mmr_root([]): RecentRoot([], None)},
        tx_commitment_buffer=[]
    )
```

At the end of a block at height `block_height`, after its transactions and its leader reward, every note set a commitment was appended to in the block records its commitment MMR root and forgets the roots that have left the window of the last `ROOT_WINDOW` blocks ([Block Execution](bedrock-block-construction.md#block-execution)), `note_sets_appended_to` giving the note sets a block or a Mantle Transaction appended a commitment to. The work of a block thus follows the note sets it changes, and a note set no block changes costs the later blocks nothing:

```python
class NoteSet:
    def record_commitment_root(self, block_height: BlockHeight):
        self.recent_commitment_roots[self.current_commitment_root].last_block = block_height - 1
        self.current_commitment_root = mmr_root(self.commitments)
        self.recent_commitment_roots[self.current_commitment_root] = RecentRoot(list(self.commitments), None)
        for root, recent in list(self.recent_commitment_roots.items()):
            if recent.last_block is not None and recent.last_block < block_height - ROOT_WINDOW + 1:
                del self.recent_commitment_roots[root]
```

A root is recent for a block at height `block_height` if it is the current root of the set, or if its `last_block` is at least `block_height - ROOT_WINDOW`: a root is the root of the set at the end of each block from the one that recorded it until the block before the one that replaces it.

The note sets are what the [Proof of Leadership](cryptarchia-proof-of-leadership.md#eligible-sets) proves a note against.

### Commitment Merkle Mountain Range

The commitments of each note set are appended, in insertion order, to the leaves of a Merkle tree of depth `NOTE_SET_DEPTH` whose every leaf past the last appended one holds $`0`$. The root of that tree is the commitment MMR root of the set, and a commitment is proven in it by a Merkle path of length `NOTE_SET_DEPTH`. A note set therefore holds at most `2**NOTE_SET_DEPTH` commitments and, its [IMT](#nullifier-indexed-merkle-tree) giving a leaf to the sentinel, `2**NOTE_SET_DEPTH - 1` nullifiers, a capacity that transfers of 8 outputs at the Execution Gas target take about 50 years to fill. An Operation adding a commitment or a nullifier to a full set is invalid.

A Merkle path, in this tree and in every Merkle tree the circuits prove membership in, lists its nodes from the leaf level up to the root, and its selectors in the same order: the selector of a level is the bit of the leaf index at that level, starting from the least significant, `1` when the node computed at that level from the leaf is the right child, so that the path node is on the left. The root of a path is computed as follows:

```python
def path_root(leaf: zkhash, path: list[zkhash], selectors: list[boolean]) -> MerkleRoot:
    node = leaf
    for (sibling, selector) in zip(path, selectors):
        node = zkhash(sibling, node) if selector == 1 else zkhash(node, sibling)
    return node
```

The ledger keeps only the peaks of the tree: the roots of its largest perfect subtrees holding appended commitments, with their heights, from left to right. Appending a commitment adds a peak of height $`0`$ and merges the last two peaks while they have the same height, and the root is computed from the peaks and the roots of the empty subtrees:

```python
def mmr_append(peaks: list[(MerkleRoot, int)], note_commitment: NoteCommitment):
    assert sum(2**height for (_, height) in peaks) < 2**NOTE_SET_DEPTH  # the number of leaves of the tree
    peaks.append((note_commitment, 0))
    while len(peaks) > 1 and peaks[-1][1] == peaks[-2][1]:
        (left, height), (right, _) = peaks[-2], peaks[-1]
        peaks[-2:] = [(zkhash(left, right), height + 1)]

def empty_root(height: int) -> MerkleRoot:
    # the root of a perfect subtree of the given height whose leaves all hold 0
    root = 0
    for _ in range(height):
        root = zkhash(root, root)
    return root

def mmr_root(peaks: list[(MerkleRoot, int)]) -> MerkleRoot:
    if len(peaks) == 1 and peaks[0][1] == NOTE_SET_DEPTH:
        return peaks[0][0]  # a full tree is its single peak
    # fold the peaks from the right, each peak being the left sibling of what lies after it
    root = 0
    height = 0
    for (peak, peak_height) in reversed(peaks):
        while height < peak_height:
            root = zkhash(root, empty_root(height))
            height += 1
        root = zkhash(peak, root)
        height += 1
    while height < NOTE_SET_DEPTH:
        root = zkhash(root, empty_root(height))
        height += 1
    return root
```

### Nullifier Indexed Merkle Tree

The nullifiers of each note set are maintained in an indexed Merkle tree (IMT) of depth `NOTE_SET_DEPTH`, whose leaves are appended in insertion order. Each leaf holds the next greater nullifier of the set, so the leaves form a sorted linked list. The first leaf is the sentinel `(0, 0)`, and a `next_nullifier` of `0` means there is no greater nullifier.

```python
class NullifierLeaf:
    nullifier: NoteNullifier       # the nullifier this leaf holds
    next_nullifier: NoteNullifier  # the next greater nullifier of the set, 0 if none

def nullifier_leaf_hash(leaf: NullifierLeaf) -> zkhash:
    return zkhash(
        FiniteField(b"NULLIFIER_IMT_LEAF_V1", byte_order="little", modulus= p),
        leaf.nullifier,
        leaf.next_nullifier
    )

def insert_nullifier(leaves: list[NullifierLeaf], nullifier: NoteNullifier):
    assert len(leaves) < 2**NOTE_SET_DEPTH  # the number of leaves of the IMT, the sentinel included
    # the leaf of the greatest nullifier lower than nullifier
    low = max((leaf for leaf in leaves if leaf.nullifier < nullifier), key=lambda leaf: leaf.nullifier)

    leaves.append(NullifierLeaf(nullifier=nullifier, next_nullifier=low.next_nullifier))
    low.next_nullifier = nullifier
```

A `nullifier` is not in the set if and only if there is a leaf `low` with `low.nullifier < nullifier` and either `nullifier < low.next_nullifier` or `low.next_nullifier == 0`. The root of the IMT is the Merkle root of depth `NOTE_SET_DEPTH` over the hashes of its leaves, where every position past the last appended leaf holds the value $`0`$. An empty position is therefore distinct from the sentinel, whose position holds `nullifier_leaf_hash(NullifierLeaf(0, 0))`.

For a note set, the method `commitment_root()` is `mmr_root(self.commitments)`, the root of its commitment MMR as it stands, and `nullifier_root()` is the root of its nullifier IMT, over the hashes of `self.nullifier_leaves`. The `commitment_root` field of an Operation is one of the roots the set recorded.

### Input Notes Spendability Validation

The following method validates that an input of notes of a note set can be consumed:

```python
class NoteSet:
    def assert_spendable(self, inputs: list[NoteNullifier]):
        # Assert inputs are not empty
        assert len(inputs) > 0

        ## Check there is no duplicate
        assert len(inputs) == len(set(inputs))

        # Check that each note is unspent
        for note_nullifier in inputs:
            assert note_nullifier not in self.nullifiers
```

The [ZkTransfer](#zero-knowledge-transfer-proof-zktransfer) spending notes of a note set is verified against the root referenced by the Operation, which must be recent, once the commitments of the `tx_commitment_buffer` of the set are appended to it, all of them, or only those before its mini-block for a [channel step](bedrock-mantle-channels.md#channel_inscribe). The inputs can therefore be notes created by the previous Operations of the Mantle Transaction:

```python
class NoteSet:
    def tx_commitment_root(self, commitment_root: MerkleRoot, covered: int | None = None) -> MerkleRoot:
        # Check the root is the commitment MMR root of the set at the end of one of the last
        # ROOT_WINDOW blocks, block_height being the height of the block validated
        assert commitment_root in self.recent_commitment_roots
        last_block = self.recent_commitment_roots[commitment_root].last_block
        assert last_block is None or last_block >= block_height - ROOT_WINDOW
        # append the first covered commitments of tx_commitment_buffer, all of them by default,
        # to a copy of the peaks of the MMR of root commitment_root
        peaks = list(self.recent_commitment_roots[commitment_root].peaks)
        for note_commitment in self.tx_commitment_buffer[:covered]:
            mmr_append(peaks, note_commitment)
        return mmr_root(peaks)

    def verify_transfer(self, inputs: list[NoteNullifier], outputs: list[NoteCommitment], excess_value: TokenValue,
                        commitment_root: MerkleRoot, msg: zkhash, proof: ZkTransfer,
                        covered: int | None = None) -> bool:
        return ZkTransfer_verify(inputs, outputs, excess_value,
                                 self.tx_commitment_root(commitment_root, covered), msg, proof)
```

### Consuming Input Notes Execution

Consuming notes of a note set inserts their nullifiers in the nullifier IMT of the set:

```python
class NoteSet:
    def execute_spending(self, inputs: list[NoteNullifier]):
        for note_nullifier in inputs:
            self.nullifiers.add(note_nullifier)
            insert_nullifier(self.nullifier_leaves, note_nullifier)
```

### Creating Output Notes Execution

Creating notes of a note set appends their commitments to the commitment MMR of the set:

```python
class NoteSet:
    def execute_adding(self, outputs: list[NoteCommitment]):
        for note_commitment in outputs:
            mmr_append(self.commitments, note_commitment)
```

# Appendix

## Gas Determination

From the [[Analysis\] Gas Cost Determination](analysis-gas-cost-determination.md), we get the table below:

| Constants | Value |
| --- | --- |
| EXECUTION_TRANSFER_GAS | 619 |
| EXECUTION_CHANNEL_INSCRIBE_GAS | 59 |
| EXECUTION_CHANNEL_CONFIG_GAS | 59 |
| EXECUTION_CHANNEL_DEPOSIT_GAS | 619 |
| EXECUTION_CHANNEL_WITHDRAW_GAS | 619 |
| EXECUTION_SDP_DECLARE_GAS | 678 |
| EXECUTION_SDP_WITHDRAW_GAS | 678 |
| EXECUTION_SDP_ACTIVE_GAS | 59 |
| EXECUTION_CLAIM_POW_REWARD_GAS | 0 |

## Zero Knowledge Transfer Proof (ZkTransfer)

A proof attesting that for the following public values:

```python
class ZkTransferPublic:
    inputs: list[NoteNullifier]     # (len = 4) the nullifiers of the consumed notes
    inputs_active: list[boolean]    # (len = 4) whether each input consumes a note
    outputs: list[NoteCommitment]   # (len = 8) the commitments of the created notes
    outputs_active: list[boolean]   # (len = 8) whether each output creates a note
    excess_value: TokenValue        # the value of the inputs left over by the outputs
    tx_commitment_root: MerkleRoot  # the referenced commitment_root extended with the tx_commitment_buffer of the set,
                                    # or the commitments before its mini-block for a channel step,
                                    # the live MMR of the rollup note set for ROLLUP_PROVE, or the single-note MMR for SDP_WITHDRAW
    msg: zkhash                     # the message the proof is bound to
```

`ZkTransfer_verify(inputs, outputs, excess_value, tx_commitment_root, msg, proof)` verifies the proof for these public values. The nullifiers of `inputs` fill the first inputs of the circuit and the commitments of `outputs` its first outputs. These are active, and every other input and output is inactive and holds `0`, so the verifier sets the flags from the lengths of the two lists. A ZkTransfer therefore spends at most 4 notes and creates at most 8: an Operation whose `inputs` or `outputs` list is longer is invalid. An Operation spending notes of a note set, other than `SDP_WITHDRAW` and [`ROLLUP_PROVE`](bedrock-mantle-rollups.md#rollup_prove), verifies the proof through the [`verify_transfer`](#input-notes-spendability-validation) method of the set, which appends the commitments created earlier in the Mantle Transaction to the referenced root, all of them, or only those before its mini-block for a channel step.

The circuit fixes the order of the public signals of the proof: the outputs `inputs`, `outputs` and `excess_value` first, then `inputs_active`, `outputs_active`, `tx_commitment_root` and `msg`.

The prover knows a witness:

```python
class ZkTransferWitness:
    inputs_spending_sk: list[ZkSecretKey]  # (len = 4) the spending secret key of each input
    inputs_stake_pk: list[ZkPublicKey]     # the staking key of each input note
    inputs_nonce: list[zkhash]             # the nonce of each input note
    inputs_value: list[TokenValue]         # the value of each input note
    inputs_selectors: list[list[boolean]]  # (len = 4 x NOTE_SET_DEPTH) the Merkle path direction of each input
    inputs_path: list[list[zkhash]]        # (len = 4 x NOTE_SET_DEPTH) the Merkle path of each input
    outputs_pk: list[ZkPublicKey]          # (len = 8) the public key of each output note
    outputs_stake_pk: list[ZkPublicKey]    # the staking key of each output note
    outputs_nonce: list[zkhash]            # the nonce of each output note
    outputs_value: list[TokenValue]        # the value of each output note
```

Such that the following constraints hold, where `inputs_nf_sk`, `inputs_pk` and `inputs_commitment` are the nullifier keys, public keys and commitments the circuit derives for the inputs:

- Each nullifier key is derived from the corresponding spending secret key, and each public key from the nullifier key ([Keys](#keys)).
  ```python
  assert all(
      inputs_nf_sk[i] == zkhash(FiniteField(b"NF_KDF_V1", byte_order="little", modulus= p), inputs_spending_sk[i])
      and inputs_pk[i] == zkhash(FiniteField(b"KDF", byte_order="little", modulus= p), inputs_nf_sk[i])
      for i in range(len(inputs_spending_sk))
  )
  ```
  
- Each input flag is boolean, and each input commitment is derived from the value, the nonce, the public key and the staking key. The staking key is not proven: spending a note takes its spending secret key alone.
  ```python
  assert all(
      inputs_active[i] * (1 - inputs_active[i]) == 0
      and inputs_commitment[i] == zkhash(FiniteField(b"NOTE_CM_V1", byte_order="little", modulus= p), inputs_value[i], inputs_nonce[i], inputs_pk[i], inputs_stake_pk[i])
      for i in range(len(inputs_spending_sk))
  )
  ```
  
- Each active input nullifier is derived from the nullifier key and the input commitment, and each inactive input has value 0.
  ```python
  assert all(
      inputs[i] == zkhash(FiniteField(b"NOTE_NF_V1", byte_order="little", modulus= p), inputs_commitment[i], inputs_nf_sk[i])
      if inputs_active[i] else inputs_value[i] == 0
      for i in range(len(inputs_spending_sk))
  )
  ```
  
- The nullifiers of the active inputs are pairwise distinct, so a note is consumed at most once and counted once in the balance.
  ```python
  assert all(
      inputs[i] != inputs[j]
      for i in range(len(inputs_spending_sk))
      for j in range(i + 1, len(inputs_spending_sk))
      if inputs_active[i] and inputs_active[j]
  )
  ```
  
- Each selector is a bit, and each active input commitment is in `tx_commitment_root`, its path computed by [`path_root`](#commitment-merkle-mountain-range).
  ```python
  assert all(
      inputs_selectors[i][j] * (1 - inputs_selectors[i][j]) == 0
      for i in range(len(inputs_spending_sk))
      for j in range(len(inputs_selectors[i]))
  )
  assert all(
      path_root(inputs_commitment[i], inputs_path[i], inputs_selectors[i]) == tx_commitment_root
      or not inputs_active[i]
      for i in range(len(inputs_spending_sk))
  )
  ```

- Each output flag is boolean, each active output commitment is derived from the value, the nonce, the public key and the staking key, and each inactive output has value 0.
  ```python
  assert all(
      outputs_active[i] * (1 - outputs_active[i]) == 0
      and (outputs[i] == zkhash(FiniteField(b"NOTE_CM_V1", byte_order="little", modulus= p), outputs_value[i], outputs_nonce[i], outputs_pk[i], outputs_stake_pk[i])
           if outputs_active[i] else outputs_value[i] == 0)
      for i in range(len(outputs_pk))
  )
  ```
  
- Each output is well-formed and the excess value, zero or more, is outputted. Input values need no range check: every commitment of a set opens to a value below $`2^{64}`$, since ZkTransfer outputs are range-checked and every other note the ledger creates holds a `TokenValue`. Every Operation and note kind must keep this.
  ```python
  assert all(
      outputs_value[i] < 2**64
      for i in range(len(outputs_value))
  )
  value_inputs = sum(inputs_value)
  value_outputs = sum(outputs_value)
  assert value_inputs >= value_outputs
  assert excess_value == value_inputs - value_outputs
  ```

- The proof is bound to `msg` (it’s the `mantle_tx_hash` reduced modulo $`p`$ in case of transactions).

The circuit takes at most 4 inputs and 8 outputs. The unused ones are inactive: their entry of `inputs` (or `outputs`) and of `inputs_value` (or `outputs_value` respectively) is `0`, and their other witnesses are arbitrary.

## Multiple Ed25519 Signatures Verification

The [Channel Configuration](bedrock-mantle-channels.md#channel_config) authorizes an action with a threshold of Ed25519 signatures produced by a list of accredited keys. Each signature comes with the index, in the accredited keys list, of the key that produced it. The verification is factored out in the following routine:

*Given*

```python
msg: hash                          # the 32-byte mantle_txhash digest being signed
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

    # Indexes must be ordered from smallest to biggest without duplication,
    # and the last one, hence every one, must index a key of `keys`.
    for i in range(len(indexes) - 1):
        assert indexes[i] < indexes[i + 1]
    assert len(indexes) == 0 or indexes[-1] < len(keys)

    # Each signature must be valid for the accredited key at its index
    for sig, idx in zip(signatures, indexes):
        assert Ed25519_verify(msg, keys[idx], sig)
```

## Test Vectors

To see what the payloads represent, refer to [Mantle Transaction Encoding](bedrock-mantle-encoding.md). The vectors are derived from this specification: `op_id` is the BLAKE2b-256 hash of `OPERATION_ID_V1` and the payload, without its opcode, and the transaction hash the BLAKE2b-256 hash of `MANTLE_TXHASH_V1` and the encoded `MantleTx`. Each field holds a small distinct value, so that every field can be told apart in the payload. The verification key of `ROLLUP_CREATE` holds real points, since [ROLLUP_CREATE](bedrock-mantle-rollups.md#rollup_create) checks every point of the key: `alpha` is $`[1]G_1`$, `beta`, `gamma` and `delta` are $`[2]G_2`$, $`[3]G_2`$ and $`[4]G_2`$, and the six points of `ic` are $`[5]G_1`$ to $`[10]G_1`$, $`[k]G_1`$ and $`[k]G_2`$ being `k` times the generators of $`\mathbb{G}_1`$ and $`\mathbb{G}_2`$.

### Operation Id

| Operation | Payload | `op_id` |
| ------------------------- | - | - |
| `TRANSFER`                | 0x0201000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000600000000000000 | 0xb39493d223a2fefae67c6aac3c8f9338e3272137d4ae4ce714607bcbc9d011a4 |
| `CHANNEL_CONFIG`          | 0x0707070707070707070707070707070707070707070707070707070707070707000000000000000000000000000000000000000000000000000000000000000002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f6180a0000000b0000000c00 | 0xce2011caae1d309c81b201ba7dc3c7516e93fbd43359e1fe8aff423d61fd7cc1 |
| `CHANNEL_INSCRIBE`        | 0x0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0b00000068656c6c6f206c6f676f730000000000000000000000000000000000000000000000000000000000000000d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c01000100012300000000000000000000000000000000000000000000000000000000000000012400000000000000000000000000000000000000000000000000000000000000250000000000000000000000000000000000000000000000000000000000000010000000737465702d696e736372697074696f6e | 0xbe94d0343391e97bdf3a2842b832b9214e3d0827503a055b1c06bd66743ac2b0 |
| `CHANNEL_DEPOSIT`         | 0x1010101010101010101010101010101010101010101010101010101010101010011100000000000000000000000000000000000000000000000000000000000000012700000000000000000000000000000000000000000000000000000000000000260000000000000000000000000000000000000000000000000000000000000028000000000000001b0000006368616e6e656c2d6465706f7369742d696e736372697074696f6e | 0x27586493a0af5c413ec02bbb1cf310f70c74370df5b81c1d729f5e355a1e2937 |
| `CHANNEL_WITHDRAW`        | 0x1212121212121212121212121212121212121212121212121212121212121212011300000000000000000000000000000000000000000000000000000000000000012a000000000000000000000000000000000000000000000000000000000000002900000000000000000000000000000000000000000000000000000000000000 | 0x18e88fc3142c430bce8210829302c77689735fd470668a303d26568d17939d09 |
| `SDP_DECLARE`             | 0x00010b00047f00000191020bb8cd0353470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f3190000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000003e00000000000000000000000000000000000000000000000000000000000000011a000000000000000000000000000000000000000000000000000000000000002c000000000000000000000000000000000000000000000000000000000000002d00000000000000 | 0x3bde3b9b04ed242ca887f6f8139e317acf9fe0d8a6237f92e048bc0447bc9b64 |
| `SDP_WITHDRAW`            | 0x1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1c00000000000000000000000000000000000000000000000000000000000000012e000000000000000000000000000000000000000000000000000000000000002f00000000000000 | 0x22cfc077d947c544eada3e018542be63f726bda60c96f64477518eee62d88009 |
| `SDP_ACTIVE`              | 0x1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1f00000000000000010a0000008a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020303030303030303030303030303030303030303030303030303030303030303 | 0xc4a2a639034016f52728f34041cf95fc2c7adb8f54cf94b4361b2d0cb72ebb70 |
| `CLAIM_POW_REWARD`        | 0x313131313131313131313131313131313131313131313131313131313131313132000000000000000000000000000000000000000000000000000000000000003300000000000000000000000000000000000000000000000000000000000000 | 0x271876ff684b7087005dba3153c44e8dcefd09257aa7e0d491399e2a483c975a |
| `ROLLUP_CREATE`           | 0x404040404040404040404040404040404040404040404040404040404040404002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f61841000000420000000100000000000000000000000000000000000000000000000000000000000000b9b3b4620913f849ee2aa6a9cfd35c9d146f3e7c27596cc3e8d311fd3472dc2779ad28398ced57998435d8c63164b86d7033733ab82101b6379bf1b45d203ea0f5c7fb9406fade12005e9ab08c477e8d5e7192e12628e551900eb14d784e0606856eb6ff324f82c9a7a078686b1504bcebe4cf5dcd9151734297bb572f7714102ce236b4ddb40977fd454c08e570151342c4cc50a86380c3472f6a6ff8dbdd296f237195c2856d5a3f8ca190f6666f2084d776f9935a48a2d57a569e476806a9a93f16faa7a849e89ca35389d8dee46243772b760402bc66f7e0fe0edf39c117f94a688c5b3dfe2a762ab3d315927156987792e7d92f79e0f4523f1a41caf40978e0ffab866b3a9876bd01b8ecc66fcb86936277f425539a758dbbd32e2b0717636a302c88373904f75a15fe21c13882a8fe9c3be9f572f4100c48231dd5b18869b8433bc4184f193f6816e6b710c7a9297d77eac0e9fec05412ff8dea309703b445404b921d95c60479caf418a57fda721ca74e35e2a904d81a9fb957a2d3094300000000000000000000000000000000000000000000000000000000000000 | 0xf5482184be0c3cddce2eb4202001015290f48a060e87d7ed1c3c98db5d8e3939 |
| `ROLLUP_INSCRIBE`         | 0x444444444444444444444444444444444444444444444444444444444444444412000000726f6c6c75702d696e736372697074696f6e4545454545454545454545454545454545454545454545454545454545454545d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c | 0xe1f54d3d24b48566c8e5fd397918892cb8328c9ed1c0590839a8aee30275204e |
| `ROLLUP_DEPOSIT`          | 0x4646464646464646464646464646464646464646464646464646464646464646014700000000000000000000000000000000000000000000000000000000000000480000000000000000000000000000000000000000000000000000000000000049000000000000004a000000000000004b000000000000000000000000000000000000000000000000000000000000001a000000726f6c6c75702d6465706f7369742d696e736372697074696f6e | 0x1f4bec88032b609db67c519a00b39daf80befd7e27c1317cfb77673ce3a745eb |
| `ROLLUP_PROVE`            | 0x4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c01004d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d0100014e00000000000000000000000000000000000000000000000000000000000000014f0000000000000000000000000000000000000000000000000000000000000001500000000000000000000000000000000000000000000000000000000000000051000000000000000000000000000000000000000000000000000000000000000100fd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f618520000005300000000 | 0xe0406385367de6a766730b10a33fc11ed59cf5ae785c724bc877233fe7b8fc61 |

### Transaction Hash

| Transaction | Payload | Transaction Hash                                                   |
| - | - | - |
| Empty transaction | 0x00 | 0x2eba3f667b80a508f3d44d149a1c27a90ea365a51e4fc8209289088142b364e5 |
| Transaction with one of each operation | 0x0d000201000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000600000000000000100707070707070707070707070707070707070707070707070707070707070707000000000000000000000000000000000000000000000000000000000000000002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f6180a0000000b0000000c00110e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0b00000068656c6c6f206c6f676f730000000000000000000000000000000000000000000000000000000000000000d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c01000100012300000000000000000000000000000000000000000000000000000000000000012400000000000000000000000000000000000000000000000000000000000000250000000000000000000000000000000000000000000000000000000000000010000000737465702d696e736372697074696f6e121010101010101010101010101010101010101010101010101010101010101010011100000000000000000000000000000000000000000000000000000000000000012700000000000000000000000000000000000000000000000000000000000000260000000000000000000000000000000000000000000000000000000000000028000000000000001b0000006368616e6e656c2d6465706f7369742d696e736372697074696f6e131212121212121212121212121212121212121212121212121212121212121212011300000000000000000000000000000000000000000000000000000000000000012a0000000000000000000000000000000000000000000000000000000000000029000000000000000000000000000000000000000000000000000000000000002000010b00047f00000191020bb8cd0353470962558a6e0839022ae65c6b2723b32772e5c0c5f4776cb8e6a3e10ba2f3190000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000003e00000000000000000000000000000000000000000000000000000000000000011a000000000000000000000000000000000000000000000000000000000000002c000000000000000000000000000000000000000000000000000000000000002d00000000000000211b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1c00000000000000000000000000000000000000000000000000000000000000012e000000000000000000000000000000000000000000000000000000000000002f00000000000000221e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1f00000000000000010a0000008a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c0202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020203030303030303030303030303030303030303030303030303030303030303033031313131313131313131313131313131313131313131313131313131313131313200000000000000000000000000000000000000000000000000000000000000330000000000000000000000000000000000000000000000000000000000000040404040404040404040404040404040404040404040404040404040404040404002001398f62c6d1a457c51ba6a4b5f3dbd2f69fca93216218dc8997e416bd17d93cafd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f61841000000420000000100000000000000000000000000000000000000000000000000000000000000b9b3b4620913f849ee2aa6a9cfd35c9d146f3e7c27596cc3e8d311fd3472dc2779ad28398ced57998435d8c63164b86d7033733ab82101b6379bf1b45d203ea0f5c7fb9406fade12005e9ab08c477e8d5e7192e12628e551900eb14d784e0606856eb6ff324f82c9a7a078686b1504bcebe4cf5dcd9151734297bb572f7714102ce236b4ddb40977fd454c08e570151342c4cc50a86380c3472f6a6ff8dbdd296f237195c2856d5a3f8ca190f6666f2084d776f9935a48a2d57a569e476806a9a93f16faa7a849e89ca35389d8dee46243772b760402bc66f7e0fe0edf39c117f94a688c5b3dfe2a762ab3d315927156987792e7d92f79e0f4523f1a41caf40978e0ffab866b3a9876bd01b8ecc66fcb86936277f425539a758dbbd32e2b0717636a302c88373904f75a15fe21c13882a8fe9c3be9f572f4100c48231dd5b18869b8433bc4184f193f6816e6b710c7a9297d77eac0e9fec05412ff8dea309703b445404b921d95c60479caf418a57fda721ca74e35e2a904d81a9fb957a2d309430000000000000000000000000000000000000000000000000000000000000041444444444444444444444444444444444444444444444444444444444444444412000000726f6c6c75702d696e736372697074696f6e4545454545454545454545454545454545454545454545454545454545454545d9bf2148748a85c89da5aad8ee0b0fc2d105fd39d41a4c796536354f0ae2900c424646464646464646464646464646464646464646464646464646464646464646014700000000000000000000000000000000000000000000000000000000000000480000000000000000000000000000000000000000000000000000000000000049000000000000004a000000000000004b000000000000000000000000000000000000000000000000000000000000001a000000726f6c6c75702d6465706f7369742d696e736372697074696f6e434c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c01004d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d0100014e00000000000000000000000000000000000000000000000000000000000000014f0000000000000000000000000000000000000000000000000000000000000001500000000000000000000000000000000000000000000000000000000000000051000000000000000000000000000000000000000000000000000000000000000100fd1724385aa0c75b64fb78cd602fa1d991fdebf76b13c58ed702eac835e9f618520000005300000000 | 0xd7b31902e3a954d68dc6efe14ec140817942767a236db078c600d8b711962a51 |

### Declaration Id

The `declaration_id` ([Declaration Storage](bedrock-service-declaration-protocol.md#declaration-storage)) is `Hash(service||zk_id)`. This vector reuses the fields of the `SDP_DECLARE` payload from [Operation Id](#operation-id).

| Field | Value |
| - | - |
| `service` | 0x00 |
| `zk_id` | 0x1900000000000000000000000000000000000000000000000000000000000000 |
| Preimage | 0x001900000000000000000000000000000000000000000000000000000000000000 |
| `declaration_id` | 0x67fa7d1fe7f1391195fdd479bba30dd97c9e6d2e1525436ac2427f2bf8567a0d |
