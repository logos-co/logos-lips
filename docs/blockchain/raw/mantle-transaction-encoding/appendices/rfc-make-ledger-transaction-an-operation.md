# [RFC] Make Ledger Transaction an Operation

This RFC follows an older schema and will be updated when time allows.

**Authors:** Thomas Lavaur
**Approvals (research):** Marcin Pawlowski
**Approvals (engineering):** Daniel Sanchez Quiros, Youngjoon Lee

---

## Motivation

In [Mantle](../../../deprecated/v1.2.0-mantle.md), the Ledger Transaction is modeled as a special, mandatory component of every Mantle Transaction. Each Mantle Transaction must include exactly one Ledger Transaction, which is validated and executed separately from the rest of the transaction:
```python
# v1.2
class MantleTx:
    ledger_tx: LedgerTx
    ops: list[Op]
    permanent_storage_gas_price: TokenValue
    execution_gas_price: TokenValue

class SignedMantleTx:
    tx: MantleTx
    op_proofs: list[OpProof | None]
    ledger_tx_proof: ZkSignature  # separate from op proofs
```

This structure introduces unnecessary complexity by treating the Ledger Transaction asymmetrically: it is validated and executed in a dedicated step, outside the normal Operation pipeline. It also prevents multiple users from issuing independent transfers within a single atomic Mantle Transaction.
This RFC proposes removing that constraint. Instead, the Ledger Transaction becomes a regular transfer Operation, subject to the same validation and execution rules as any other Operation.
## Proposal

We introduce a `TRANSFER` Operation (opcode `0x00`) that is semantically equivalent to the former `LedgerTx`. The Mantle Transaction structure is simplified to a flat list of Operations:
```python
# v1.3 — proposed
class MantleTx:
    ops: list[Op]
    permanent_storage_gas_price: TokenValue
    execution_gas_price: TokenValue

class SignedMantleTx:
    tx: MantleTx
    op_proofs: list[OpProof | None]  # Transfer proof now included here
```

A transfer that previously lived in `ledger_tx` is now represented as a `TRANSFER` Operation inside `ops`. A Mantle Transaction becomes a homogeneous bundle of Operations that are either all valid or all invalid together.
## Justification

### **Simplicity and consistency**

The distinction between `LedgerTx` and `Op` was an artificial split. Treating transfers as first-class Operations removes a special case from every layer of the stack (validation, execution, encoding, gas).
### **Multiple transfers per transaction**

Several actors can issue independent transfers within one atomic Mantle Transaction, with no off-chain compensation required.
### **Atomic cross-zone deposits**

A representative use case requires two transfers in a single transaction (user burn + sequencer fee), which was not possible in v1.2 without out-of-band coordination.
## Details

### Chores

We updated project references to Logos Blockchain and removed all references to DA throughout the documents.
### The Mantle Specification

#### Mantle Transaction

```python
class MantleTx:
     ops: list[Op]
-    ledger_tx: LedgerTx
     permanent_storage_gas_price: TokenValue
     execution_gas_price: TokenValue
```

We removed the `ledger_tx` field because the transfers will be part of the `ops`.
#### Signed Mantle Transaction

#### We removed the Ledger Transaction from the structure

```python
class SignedMantleTx:
     tx: MantleTx
     op_proofs: list[OpProof | None]
-    ledger_tx_proof: ZkSignature
```

The proof for the Transfer Operation is now included in `op_proofs` at the index corresponding to the Transfer Op's position in `ops`.
#### We redefined how the gas fees are calculated

```text
def gas_fees(signed_tx: SignedMantleTx) -> int:
    mantle_tx = signed_tx.tx
  permanent_storage_fees = len(encode(signed_mantle_tx)) * mantle_tx.permanent_storage_gas_price
-  execution_fees = execution_gas(mantle_tx.ledger_tx)
-             * mantle_tx.execution_gas_price
+   execution_fees = 0

  for op in mantle_tx.ops:
    # Compute the execution gas of this operation as defined
    # in the gas cost determination specification.
    execution_fees += execution_gas(op) * mantle_tx.execution_gas_price

  return execution_fees + permanent_storage_fees
```

The gas fees are computed over every operation and doesn’t need to be initialized with the ledger transaction price first.
#### We redefined the validation

The validation of the signed Mantle Transaction now doesn’t need a specific first step validating the ledger transaction so the first block of this part is removed:
>

  Mantle validators will ensure the following:
  1. ~~The ledger transaction is valid according to .~~
```text
validate_ledger_tx(ledger_tx, ledger_tx_proof, mantle_txhash(tx))
```

  2. We have a proof or a `None` value for each operation.
```text
assert len(op_proofs) == len(ops)
```

#### We redefined the execution

The same thing happens for the execution: we removed the special execution of the ledger transaction since everything will be embedded in the operations.
>

  Mantle Validators execute sequentially each Operation in `ops` according to its opcode. ~~ the following:~~
  1. ~~Execute the Ledger Transaction as described in .~~
  2. ~~Execute sequentially each Operation in `ops` according to its opcode.~~

#### We updated the balance computation

The computation of the balance of the Mantle Transaction also needs an update because the entire Mantle transaction must be balanced not the transfers individually.
```python
def get_transaction_balance(signed_tx: SignedMantleTx) -> int:
  balance = 0   # It's important to not use unsigned int here to avoid
         # overflow vulnerabilities
  for op in signed_tx.tx.ops:
    if op.opcode == LEADER_CLAIM:
      balance += get_leader_reward()
    if op.opcode == CHANNEL_DEPOSIT:
      balance -= get_channel_deposit_amount(op)
    if op.opcode == CHANNEL_WITHDRAW:
      balance += get_channel_withdrawal_amount(op)
+    if op.opcode == TRANSFER:
      for inp in op.inputs:
        balance += get_value_from_note_id(inp)
      for out in op.outputs:
        balance -= out.value
  return balance
```

#### Opcode table

Add `TRANSFER` as opcode `0x00` and rearrange the different opcodes:

| Operation | Opcode | Description |
| --- | --- | --- |
| TRANSFER | 0x00 | Consume and create notes. |
| RESERVED | 0x01 - 0x0F |  |
| CHANNEL_CONFIG | 0x10 | Configure a channel |
| CHANNEL_INSCRIBE | 0x11 | Write a message permanently onto Mantle. |
| CHANNEL_DEPOSIT | 0x12 | Deposit assets into a channel |
| CHANNEL_WITHDRAW | 0x13 | Withdraw assets from a channel |
| RESERVED | 0x14 - 0x1F |  |
| SDP_DECLARE | 0x20 | Declare intention to participate as a node in a Bedrock Service, locking funds as collateral. |
| SDP_WITHDRAW | 0x21 | Withdraw participation from a Bedrock Service, unlocking your funds in the process. |
| SDP_ACTIVE | 0x22 | Signal that you are still an active participant of a Bedrock Service. |
| RESERVED | 0x23 - 0xFF |  |
| LEADER_CLAIM | 0x30 | Claim leader reward anonymously. |
| RESERVED | 0x31 - 0xFF |  |

#### Operation Examples

All operation examples that are embedded in a Mantle Transaction during the example needed an update like `SDP_ACTIVE` for example:
```text
active=Active(
  declaration=alice_declaration_id,
    nonce=1579532,
    metadata=b"Look, I am still doing my job"
)

+ # Build the transfer operation to pay the fees
+ transfer = Transfer(inputs=[fee_note_id], outputs=[])

tx = MantleTx(
    ops=[Op(opcode=SDP_ACTIVE, payload=encode(active))],
    permanent_storage_gas_price=150,
    execution_gas_price=70,
-   ledger_tx=LedgerTx(inputs=[fee_note_id], outputs=[]),
)
txhash = mantle_txhash(tx)

SignedMantleTx(
    tx=tx,
-   ledger_tx_proof=tx.ledger_tx.prove(fee_note_sk),
    op_proofs=[Ed25519_sign(txhash, validator_sk),
+          transfer.prove(fee_note_sk)]
)
```

#### The Transfer Operation specification

This section replace previous Ledger Transaction section. Mostly by renaming the Ledger Transaction by Transfer Operation.
The `EXECUTION_LEDGER_TX_GAS` was renamed for`EXECUTION_TRANSFER_GAS`.
`transfer_op_hash` replaces the former `ledger_tx_hash`. The domain separator changes:
```text
- h.update(b"LEDGER_TX_HASH_V1")
+ h.update(b"TRANSFER_HASH_V1")
```

Note that the noteId derivation still uses the transfer hash of the transfer that outputs the note.
### The Gas Cost Determination Analysis

**Execution Gas Formula Calculation**
We updated the execution gas computation formula:
```text
- execution_fee = (tx.ops.get_summed_gas() + tx.ledger_tx.get_gas())
-        * execution_gas_price
+ execution_fee = tx.ops.get_summed_gas() * execution_gas_price
```

**Gas computation of Ledger Transaction**
We updated names and the paragraph on the Ledger Transaction Gas determination. We removed the inclusion of the Mantle Transaction cost (balance and computation of the hash that was negligeable):
>

  The Execution Gas of the~~ Ledger Transaction~~Transfer Operation compensates for the verification of the [ZkSignature](../../common-cryptographic-components.md#zksignature-zero-knowledge-signature) proof ~~and the validation of the overall Mantle Transaction balance~~. ~~This fundamental gas cost ensures proper cryptographic verification and data integrity of both the Ledger Transaction and the Mantle Transaction. It covers the cost of computing the Mantle Transaction hash.~~
  **Execution: ~590k CPU cycles.**
    - Verification of the ZK signature: 590,000 cycles.
    - ~~Verification of the balance: negligible.~~
    - ~~Computation of the Mantle Transaction hash: negligible.~~

### Bedrock Genesis Block

The previous version of genesis block was formed with a ledger transaction, an inscription as the very first operation and a list of SDP declaration. With the new Transfer Operation, the genesis block must now be constructed with exactly one Transfer Operation, exactly one Inscription and a potential list of SDP Declare Operations:
```text
# build the genesis Mantle Transaction
GENESIS_MANTLE_TX = MantleTx(
-  ops=[CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
-  ledger_tx=STAKE_DISTRIBUTION,
+  ops=[STAKE_DISTRIBUTION, CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
  permanent_storage_gas_price=0,
  execution_gas_price=0
)
```

### Mantle Transaction Encoding

#### Signed Mantle Transaction

The encoding of the Signed Mantle Transaction doesn’t require the Ledger Transaction Proof field anymore as it is part of the Operation proofs.
```text
- SignedMantleTx = MantleTx OpsProofs LedgerTxProof
+ SignedMantleTx = MantleTx OpsProofs
```

#### Mantle Transaction

```text
- MantleTx = Ops LedgerTx ExecutionGasPrice StorageGasPrice
+ MantleTx = Ops ExecutionGasPrice StorageGasPrice
```

We once again updated the name from Ledger Transaction for Transfer Operation and removed the redundant part of the Ledger Transaction proof:
```text
- LedgerTx  = Inputs Outputs
+ Transfer  = Inputs Outputs
Inputs      = InputCount *NoteId
InputCount  = Byte
Outputs     = OutputCount *Note
OutputCount = Byte

Note   = Value ZkPublicKey
Value  = UINT64
NoteId = FieldElement
```

## Specification Updates

- [v1.3] Mantle Specification

- [v1.3] Gas Cost Determination

- [v1.1] Bedrock Genesis Block

- [v1.1] Mantle Transaction Encoding
