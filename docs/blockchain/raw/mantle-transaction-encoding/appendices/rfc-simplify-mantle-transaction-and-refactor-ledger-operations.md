# [RFC] Simplify Mantle Transaction and Refactor Ledger Operations

**Authors:** Thomas Lavaur

## Motivation

The current Mantle Specification (v1.4) has accumulated several areas of unnecessary complexity and inconsistency that hinder readability, maintainability and implementation correctness:
1. Duplicated Ledger logic: every Operation that consumes or creates notes (actually `TRANSFER`, `CHANNEL_DEPOSIT`, `CHANNEL_WITHDRAW` and `LEADER_CLAIM`) independently re-implement the same validation and execution steps to check that inputs are unspent and unlocked, validating output note format, removing consumed notes from the Ledger and inserting new notes. This duplication increases the possibility of implementation and comprehension error.
2. Unnecessary `ZkHash` in the Mantle Transaction hash: the `mantle_tx_hash` function currently computes a classical Blake2b `Hash` digest and then wraps it in a Poseidon2 `ZkHash`. This second hashing step is unnecessary and increase complexity, attack surface and reduce the efficiency of deriving the hash. The Mantle Transaction hash is not only consumed inside ZK circuits as a public input but it’s also used to build the `block_root` in headers. ZK circuits use the Mantle Transaction hash as a signature scheme and a simple modular reduction of the `Hash` to a field element suffices to achieve the same (exactly as is already done for `op_id` in the `derive_note_id` function). Removing the `ZkHash` step simplifies implementation, increase the efficiency which makes bootstrapping faster and removes an extra Poseidon2 evaluation that may be cryptographically more vulnerable than Blake2b.
3. Embedded gas prices in Mantle Transaction: the current design embeds `permanent_storage_gas_price` and `execution_gas_price` inside each Mantle Transaction. In practice the `permanent_storage_gas_price` is fixed per epoch and is the same for every transaction. The `execution_gas_price` is composed of a protocol-determined base fee (identical for every transaction in a block) plus a priority tip. Encoding these prices inside the transaction is redundant, inflates transaction size which increase its price. This offers better UX where users don’t have to correctly guess the storage price during epoch transitions.
## Proposal

We propose four complementary changes:
1. Refactor the Ledger code into a dedicated Section. We introduce common helper functions for note consumption and creation that are reused by every Operation. This eliminates code duplication and guarantees uniform validation across `TRANSFER`, `CHANNEL_DEPOSIT`, `CHANNEL_WITHDRAW` and `LEADER_CLAIM`.
2. Simplify `mantle_tx_hash` to only a classical Blake2b `Hash` instead of returning a `ZkHash`. ZK circuits that consumes transaction hash as a public input will instead consume the modular reduction modulo $`p`$, identical to the treatment of `op_id` in `derive_note_id`.
3. Remove gas prices from Mantle Transaction. The `permanent_storage_gas_price` becomes a protocol parameter fixed per epoch. The execution gas is split into a base fee (protocol-determined, same for all transactions in a block) and a tip (the leftover balance after mandatory fees). The balance validation of a Mantle Transaction checks that the balance covers at least the mandatory fees. Any excess is treated as the execution tip.
## Discussion

### Ledger Refactoring

The duplicated note validation and ledger manipulation across four Operations is the primary source of specification drift risk. By extracting these into shared functions, reviewers need only audit one code path for correctness. Future Operations that consume or creates notes automatically inherit the same checks.
### Transaction Hash Simplification

The current two-stage hash (Blake2b and then Poseidon2) was introduced to fasten the transaction hash derivation (that was previously slowing down bootstrapping). Before it was only Poseidon2 because the transaction hash is also used as a public input of Operations’ zero-knowledge proofs to achieve binding to the transaction and avoid replay attacks. With the `derive_op_id` and `derive_note_id` refactoring from [[RFC] Enforce NoteId uniqueness](rfc-enforce-noteid-uniqueness.md), we already have a well-understood pattern for reducing classical digests to field elements via a modulo $`p`$ operation. Applying the same pattern to the transaction hash removes Poseidon2 evaluation for transactions and unifies the hash-to-field approach across the Mantle Specification. The modular reduction is slightly non-uniform but since $`p \approx 2^{254}`$, the bias is negligible and does not affect security.
### Fee Model Simplification

Embedding gas prices in the transaction couples the encoding format to the fee market mechanism. By deriving prices from protocol state instead, transaction become smaller and the fee market can evolve independently of the transaction encoding. The new model is closer to EIP-1559-style designs where the base fee is protocol-determined and users only express willingness to pay through the balance of their Mantle Transaction.
## Details

### Refactored Ledger Functions

#### Introducing New Helpers

We introduce a new **Ledger Helpers** subsection in the already existing Mantle Ledger. This Section defines reusable helper functions for note validation and ledger manipulation. All Operations that consume or create notes must use these helpers.
At the same time we add inputs uniqueness check to prevent double spending. **The double spending bug was introduced in the previous specification therefore we need to fix this vulnerability.**
>

### Ledger

```python
class Ledger:
    notes: list[Note]
    locked_notes: dict[NoteId, LockedNote]
```

#### Input Notes Spendability Validation

  A note is spendable if and only if it exists, it is not spent or locked. The following function validates that an input of notes can be consumed:
```python
class Ledger:
    def assert_spendable(inputs: list[NoteId]):
        ## Check there is no duplicate
        assert len(inputs) == len(set(inputs))

        # Check that each note is individually not locked and unspent
        for note_id in inputs:
            assert ledger.is_unspent(note_id)
            assert note_id not in locked_notes
```

#### Output Notes Validation

  Before an output of notes can be inserted into the Ledger, every note field must satisfy the following constraints:
```python
class Ledger:
    def assert_valid_output(outputs: list[Note]):
        for note in outputs:
            assert note.value > 0
            assert note.value <= 2**64-1
```

#### Consuming Input Notes Execution

  Consuming a set of notes removes them from the Ledger’s Merkle tree and recycles their leaf indices:
```python
class Ledger:
    def execute_spending(inputs: list[NoteId]):
        for note_id in inputs:
            # updates the merkle tree to zero out the leaf for this entry
            # and adds that leaf index to the list of unused leaves
            ledger.remove(note_id)
```

#### Creating Output Notes Execution

  Creating notes derives their `NoteId` from the Operation’s `OpId` and insert them in the Ledger:
```python
class Ledger:
    def execute_adding(op_id: Hash,
                       outputs: list[Note]):
        for (output_index, output_note) in enumerate(outputs):
            output_note_id = derive_note_id(op_id, output_index, output_note)
            ledger.add(output_note_id)
```

#### Updating Operations

#### Channel Deposit Validation

>

  1. Ensure all inputs are ~~unspent~~spendable.
```text
assert all(ledger.is_unspent(note_id) for note_id in deposit.inputs)
ledger.assert_spendable(note_id)
```

  2. ~~Ensure inputs are not locked.~~
```text
# Ensure inputs are not locked
for note_id in deposit.inputs:
    assert note_id not in locked_notes
```

#### Channel Deposit Execution

```text
- for note_id in deposit.inputs:
-    # updates the merkle tree to zero out the leaf for this entry
-    # and adds that leaf index to the list of unused leaves
-    ledger.remove(note_id)
+ ledger.execute_spending(deposit.inputs)
```

#### Channel Withdraw Validation

We took the opportunity to also refactor the presentation of the validation steps to match the other Operations’ style.
*Validate*
1. Check that the outputs are valid
```text
ledger.assert_valid_output(withdrawal.outputs)
```

2. Check that the channel exists
```text
assert withdrawal.channel in channels
```

3. Check that the withdraw nonce is correct
```text
assert channels[withdrawal.channel].withdraw_nonce == withdrawal.withdraw_nonce
```

4. Check that the channel has enough funds
```text
withdrawal_amount = sum(output.value for output in withdrawal.outputs)
assert channels[withdrawal.channel].balance >= withdrawal_amount
```

5. Check that there are enough signatures
```text
assert len(proof.signatures) == len(proof.indexes)
assert len(proof.signatures) == channels[withdrawal.channel]
                    .withdraw_threshold
```

6. Check that every proof index is unique
```text
assert len(proof.indexes) == len(set(proof.indexes))
```

7. Check the signatures
```text
for sig, idx in zip(proof.signatures, proof.indexes):
    assert Ed25519_verify(txhash,
        channels[withdrawal.channel].accredited_keys[idx],
        sig)
```

```text
# Check that the outputs are valid
for output in withdrawal.outputs:
    assert output.value > 0
    assert output.value < 2**64

# Check that the withdraw nonce is correct
assert channels[withdrawal.channel].withdraw_nonce == withdrawal.withdraw_nonce

# Check that the channel exists
assert withdrawal.channel in channels
chan = channels[withdrawal.channel]

# Check that the channel has enough funds
withdrawal_amount = sum(output.value for output in withdrawal.outputs)
assert chan.balance >= withdrawal_amount

# Check that there are enough signatures
assert len(proof.signatures) == len(proof.indexes)
assert len(proof.signatures) == chan.withdraw_threshold

# Check that every index is unique
assert len(proof.indexes) == len(set(proof.indexes))

# Check the signatures
for sig, idx in zip(proof.signatures, proof.indexes):
    assert Ed25519_verify(txhash, chan.accredited_keys[idx], sig)
```

#### Channel Withdraw Execution

```text
 withdrawal_id = derive_op_id(withdrawal)
+ ledger.execute_adding(withdrawal_id, withdrawal.outputs)
- for (output_number, output_note) in enumerate(withdrawal.outputs):
-    output_note_id = derive_note_id(withdrawal_id, output_number, output_note)
-    ledger.add(output_note_id)
```

#### Leader Claim Execution

```text
output_note=Note(
    value = leader_reward
    public_key = claim.public_key,
)
claim_id = derive_op_id(claim)
+ ledger.execute_adding(claim_id, [output_note])
- output_note_id = derive_note_id(claim_id, 0, output_note)
- ledger.add(output_note_id)
```

#### Transfer Validation

>

  1. Ensure all inputs are ~~unspent~~spendable
```text
ledger.assert_spendable(transfer.inputs)
assert all(ledger.is_unspent(note_id) for note_id in transfer.inputs)
```

  2. ~~Ensure inputs are not locked.~~
```text
# Ensure inputs are not locked
for note_id in transfer.inputs:
    assert note_id not in locked_notes
```

  3. Ensure outputs are valid.
```text
ledger.assert_valid_output(transfer.output)
for output in transfer.outputs:
    assert output.value > 0
    assert output.value < 2**64
```

#### Transfer Execution

```text
+ ledger.execute_spending(transfer.inputs)
- for note_id in transfer.inputs:
-    # updates the merkle tree to zero out the leaf for this entry
-    # and adds that leaf index to the list of unused leaves
-    ledger.remove(note_id)
```

```text
transfer_id = derive_operation_id(transfer)
+ ledger.execute_adding(transfer_id, transfer.outputs)
- for (output_number, output_note) in enumerate(transfer.outputs):
-    output_note_id = derive_note_id(transfer_id, output_number, output_note)
-    ledger.add(output_note_id)
```

### Simplify `mantle_tx_hash`

#### Updating Mantle Transaction Hash Computation

```text
- def mantle_txhash(tx: MantleTx) -> ZkHash:
+ def mantle_txhash(tx: MantleTx) -> Hash:
    tx_bytes = encode(tx)

-   h = Hasher() # /!\ This is a classic hash not a ZkHash /!\
+   h = Hasher()
    h.update(b"MANTLE_TXHASH_V1")
    h.update(tx_bytes)
+   return h.digest()
-   classic_digest = h.digest()

-   zkh = ZkHasher() # /!\ This is a ZkHash not a classic hash /!\
-   zkh.update(FiniteField(classic_digest[0:16], bytes_order="little", modulus = p))
-   zkh.update(FiniteField(classic_digest[16:32], bytes_order="little", modulus = p))

-   return zkh.digest()
```

In the Mantle Transaction section explaining that ZK proofs are linked to Mantle Transaction Hash:
>

  Each proof (op proof and signature) must be cryptographically bound to the `MantleTx` through the `mantle_txhash` to prevent replay attacks. This binding is achieved by including the `MantleTx` hash reduced modulo $`p`$ as a public input in every ZK proof.
```text
mantle_txhash_fr = FiniteField(mantle_txhash, byte_order="little", modulus = p)
```

`mantle_txhash` is a classical 256-bit hash digest and must be reduced to a field element before being passed to any ZkHasher or used as a ZK public input. We apply a direct modular reduction mod $`p`$ (via `FiniteField(..., modulus=p)`). Since $`p \approx 2^{254}`$, the reduction is slightly non-uniform. This is inconsequential in practice as the collision probability remains around $`2^{-254}`$, and proof binding is derived from the collision-resistance of the classic hash, not from uniformity over $`F_p`$.

#### Updating ZK Proofs Inputs

#### Zk Signature

In the public values definition:
```text
class ZkSignaturePublic:
    public_keys: list[ZkPublicKey] # public keys signing the message (len = 32)
-   msg: zkhash # zkhash of the message
+   msg: zkhash # a finite field element uniquely representing the message
```

and in the last bullet point of the proof constraints:
```text
- The proof is bound to msg (it’s the mantle_tx_hash in case of transactions).
+ The proof is bound to msg (it’s the mantle_tx_hash reduced modulo p in case of transactions).
```

#### Proof of Claim

In the public values:
```text
class ProofOfClaimPublic:
    voucher_root: zkhash # Merkle root of the reward_voucher maintained by everyone
    voucher_nullifier: zkhash
-   mantle_tx_hash: zkhash # attached hash
+   mantle_tx_hash_fr: zkhash # attached hash reduced modulo p
```

and in the last bullet point of the proof constraint:
```text
- The proof is bound to the mantle_tx_hash.
+ The proof is bound to the mantle_tx_hash reduced modulo p.
```

#### [Mantle Transaction Encoding](../../mantle-transaction-encoding.md)

We removed the callout:
>

    ~~In future iterations, we will use this encoding to derive the `mantle_txhash`~~

### Remove Gas Price From `MantleTx`

#### Overview

> Users can build unbalanced ~~specify their gas prices in their~~ Mantle Transactions to tip the leaders and incentivize the network to include their transaction.

#### Mantle Transaction

#### Definition

```text
class MantleTx:
    ops: list[Op]
-   permanent_storage_gas_price: TokenValue      # See the note section
-   execution_gas_price: TokenValue
```

#### Fee

>

### Mantle Transaction Fee

  The transaction mandatory fee is a sum of two components: the multiplication of the total Execution Gas by the `execution_``base_fee`~~`gas_price`~~, and the total size of the encoded signed Mantle Transaction multiplied by the `permanent_storage_gas_price`. The execution base fee and the permanent storage gas price are protocol-determined values that are the same for every Mantle Transaction in a block. They are derived following [Execution Market](../../analysis-execution-market.md) and [Storage Markets](../../storage-markets.md).

We replaced this **old code:**
```python
def gas_fees(signed_tx: SignedMantleTx) -> int:
    mantle_tx = signed_tx.tx
    permanent_storage_fees = len(encode(signed_mantle_tx)) * mantle_tx.permanent_storage_gas_price
    execution_fees = 0

    for op in mantle_tx.ops:
        # Compute the execution gas of this operation as defined
        # in the gas cost determination specification.
        execution_fees += execution_gas(op) * mantle_tx.execution_gas_price

    return execution_fees + permanent_storage_fees
```

by this **new code**:
```python
def mandatory_fees(signed_tx: SignedMantleTx,
                   permanent_storage_gas_price: TokenValue, # Given by Storage Market
                   execution_gas_base_price: TokenValue) -> int:  # Given by Execution Market
    mantle_tx = signed_tx.tx
    permanent_storage_fees = len(encode(signed_mantle_tx)) * permanent_storage_gas_price
    tx_execution_gas = 0

    for op in mantle_tx.ops:
        # Compute how much execution gas of this operation as defined
        # in the gas determination Appendix
        tx_execution_gas += execution_gas(op)
    execution_base_fees = tx_execution_gas * execution_gas_base_price

    return execution_base_fees + permanent_storage_fees
```

>

  If the Mantle Transaction is unbalanced (meaning that the Transaction consume more value than it creates) and that the leftover balance cover more than the mandatory fees, the remaining is treated as execution tip fees.

#### Validation

>

```text
signed_tx = SignedMantleTx(
    tx=MantleTx(ops, permanent_storage_gas_price, execution_gas_price),
    op_proofs
)
```

We also changed the third validation point:
> The Mantle Transaction excess balance pays ~~for the~~at least the mandatory ~~transaction ~~fees.

```text
- tx_fee = gas_fees(signed_tx)  # Not an unsigned int
+ tx_mandatory_fee = mandatory_gas_fees(signed_tx)  # Not an unsigned int
+ tx_balance = get_transaction_balance(signed_tx)
- assert tx_fee == get_transaction_balance(signed_tx)
+ assert tx_mandatory_fee <= tx_balance
+ tx_execution_tip = tx_balance - tx_mandatory_fee
```

#### Execution

>

```text
SignedMantleTx(
    tx=MantleTx(ops, permanent_storage_gas_price, execution_gas_price),
    op_proofs
)
```

#### [Gas Determination Storage Definition](../../analysis-gas-cost-determination.md)

> Permanent Storage is paid directly for the entire signed Mantle Transaction. The Permanent Storage Gas price is derived from [Storage Markets](../../storage-markets.md) ~~included in the Mantle Transaction structure~~ and is used to determine the Permanent Storage fee. 1 Permanent Storage Gas corresponds to 1 byte.

#### [Gas Determination Execution Definition](../../analysis-gas-cost-determination.md)

> Execution is a second general market that represents how costly an Operation is to execute. This cost can be fixed or variable based on the content of the Operation. The Execution Gas base price is derived from [Execution Market](../../analysis-execution-market.md) ~~contained in the Mantle Transaction structure ~~and each Operation defines its execution gas amount. 1 Execution Gas corresponds to 1,000 CPU cycles.

```text
execution_base_fee = tx.ops.get_summed_gas() * execution_gas_base_price
```

#### Mantle Transaction Encoding

#### [Mantle Transaction](../../mantle-transaction-encoding.md)

```text
- MantleTx = Ops ExecutionGasPrice StorageGasPrice
+ MantleTx = OpCount *Op
+ OpCount  = Byte

- ExecutionGasPrice = UINT64
- StorageGasPrice   = UINT64
```

#### [Operation](../../mantle-transaction-encoding.md)

```text
- Ops     = OpCount *Op
- OpCount = Byte
```

## Chores

### Simplify Transaction Hash

#### Mantle Transaction Type

We changed the `zkhash` type of the Mantle Transaction hash to a simple `hash` like in
>

```text
 mempool_transactions: list[zkhash]         # 1024 * 32 bytes
```

#### Exemples

Every examples including a Mantle Transaction need an update to remove the prices. Here is an example:
```text
tx = MantleTx(
    ops=[Op(opcode=CHANNEL_INSCRIBE, payload=encode(greeting)),
         Op(opcode=TRANSFER, payload=encode(transfer)],
-   permanent_storage_gas_price=150,
-   execution_gas_price=70,
)
```

#### Spendable Note Validation

In the validation of notes we were verifying the zero-knowledge proof before verifying that the note isn’t locked. Even if the Specification doesn’t enforce an order, we swapped this order to provide the most efficient order for implementation pushing ZK verification for the end in `TRANSFER` and `CHANNEL_DEPOSIT` (the only two Operations consuming notes).
#### [Clean Mantle Transaction Encoding](../../mantle-transaction-encoding.md)

Mantle Transaction Encoding document still refers to deprecated blobs from DA and ChannelSetKey Operation that was deprecated. We remove the blobs reference and update the ChannelSetKey to ChannelConfig as in Mantle:
```text
ChannelConfig     = ChannelId KeyCount *Signer PostingTimeframe PostingTimeout ConfigThreshold WithdrawThreshold
KeyCount          = Byte
PostingTimeframe  = UINT32
PostingTimeout    = UINT32
ConfigThreshold   = UINT16
WithdrawThreshold = UINT16
```

## Specification updates

### New

### Update

- Mantle

- \[Analysis\] Gas Cost Determination

- Mantle Transaction Encoding

- \[Template\] Cross-Channel Messaging

- Block Construction, Validation and Execution

- Bedrock Genesis Block

### Deprecate

[Mantle](../../../deprecated/v1.2.0-mantle.md)
[\[Analysis\] Gas Cost Determination](../../../deprecated/v1.4.0-analysis-gas-cost-determination.md)
[Mantle Transaction Encoding](../../../deprecated/v1.1.0-mantle-transaction-encoding.md)
[\[Template\] Cross-Channel Messaging](../../../deprecated/v1.1.0-template-cross-channel-messaging.md)
[Block Construction, Validation and Execution](../../../deprecated/v1.0.0-bedrock-block-construction.md)
[Bedrock Genesis Block](../../../deprecated/v1.0.0-bedrock-genesis-block.md)
### Retire
