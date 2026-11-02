# [RFC] Enforce NoteId uniqueness

**Authors:** Thomas Lavaur

## Motivation

In [Mantle](../../../deprecated/v1.2.0-mantle.md), the NoteId is derived from the Transfer Operation that mints it:
The introduction of `LEADER_CLAIM` and `CHANNEL_WITHDRAW` operations creates a collision risk in `NoteId` derivation. Both operations allow a Mantle transaction to be balanced without consuming any note as input, breaking the hash chain that previously guaranteed `NoteId` uniqueness. As a result, two distinct Mantle transactions can produce notes with identical `NoteId`s whenever their `TRANSFER` operations share the same output value and public key and carry no inputs.
## Proposal

We propose three complementary changes:
### **Generalize `NoteId` derivation to use a per-operation identifier `OpId`**

Rather than deriving `NoteId` from a `transfer_hash` specific to `TRANSFER`, we introduce a generic `Op``Id` that each Operation creating new notes computes independently.
The `NoteId` derivation ZK circuit is left entirely unchanged, each Operation that outputs notes simply supplies its own `op_id` as the first input. Uniqueness is guaranteed as long as each `op_id` is itself unique.
So instead of using
```python
# v 1.3
def derive_note_id(transfer_hash: zkhash, output_number: int, note: Note) -> NoteId:
    return zkhash(
        FiniteField(b"NOTE_ID_V1", byte_order="little", modulus= p)
        transfer_hash,
        FiniteField(output_number, byte_order="little", modulus= p)
        FiniteField(note.value, byte_order="little", modulus= p)
        note.public_key
    )
```

we would be using:
```python
# new version
def derive_note_id(op_id: OpId, output_index: int, note: Note) -> NoteId:
    return ZkHash(
        FiniteField(b"NOTE_ID_V1",  byte_order="little", modulus=p),
        op_id,                      # transfer_id, leader_claim_id, etc.
        FiniteField(output_index,   byte_order="little", modulus=p),
        FiniteField(note.value,     byte_order="little", modulus=p),
        note.public_key,
    )
```

### Restrict `TRANSFER` to require at least one input note

`TRANSFER` is amended to require at least one input note. This re-establishes a hash chain: `transfer_id` (previously `transfer_hash`) is derived from at least one existing `NoteId`, making each new `NoteId` depend on a prior unpredictable value and eliminating the collision vector. This is achieved because each `TRANSFER` payload is now unique because they include a unique `NoteId`.
The `transfer_id` is not derived using a specific `transfer_hash`function anymore but using a common `derive_op_id` function that output a unique `OpId` as long as the inputted Operation as a unique payload. So instead of
```python
# v1.3
def transfer_hash(tx: LedgerTx) -> ZkHash:
    tx_bytes = encode(tx)

    h = Hasher() # /!\ This is a classic hash not a ZkHash /!\
    h.update(b"TRANSFER_HASH_V1")
    h.update(tx_bytes)
    classic_digest = h.digest()

    zkh = ZkHasher() # /!\ This is a ZkHash not a classic hash /!\
    zkh.update(FiniteField(classic_digest[0:16], bytes_order="little", modulus = p))
    zkh.update(FiniteField(classic_digest[16:32], bytes_order="little", modulus = p))

    return zkh.digest()
```

We would use:
```python
# new version
def derive_op_id(operation: Op) -> Hash:
    op_bytes = encode(op)
    h = Hasher() # /!\ This is a classic hash not a ZkHash /!\
    h.update(b"OPERATION_ID_V1")
    h.update(op_bytes)
    return h.digest()
```

### **Decouple `CHANNEL_WITHDRAW`, `CHANNEL_DEPOSIT`, and `LEADER_CLAIM` from the Mantle transaction balance**

Rather than adjusting the transaction balance, which would require a compensating `TRANSFER` and force the consumption of an otherwise unneeded note, these operations directly consume or create notes using their own `OpId` as input to the shared `derive_note_id` function.
Now the Operations changed from
```python
# v 1.3
class ChannelDeposit:
    channel: ChannelId
    amount: TokenValue
    metadata: bytes

class ChannelWithdraw:
    channel: ChannelId
    amount: TokenValue

class ClaimRequest:
    rewards_root: zkhash # Merkle root used in the proof for voucher membership
    voucher_nf: zkhash
```

to
```python
# new version
class ChannelDeposit:
    channel: ChannelId
    inputs: list[NoteId]  # the list of consumed note identifiers
    metadata: bytes

class ChannelWithdraw:
    channel: ChannelId
    outputs: list[Note]
    withdrawal_nonce: u32

class ClaimRequest:
    rewards_root: zkhash # Merkle root used in the proof for voucher membership
    voucher_nf: zkhash
    public_key: ZkPublicKey
```

And the balance is now computed using only transfers, while `CHANNEL_DEPOSIT`, `CHANNEL_WITHDRAW` and `LEADER_CLAIM` directly create or consume the note they need.
## Discussion

### **Security**

A `NoteId` collision results in fund loss. The UTXO model marks notes as consumed upon spending; once a `NoteId` is spent, it cannot be spent again. If two distinct notes share the same `NoteId`, only one can ever be consumed, the other becomes permanently unspendable.
Beyond accidental collisions, the vulnerability is actively exploitable. An adversary who learns a target's public key and the value of a pending note can front-run it by submitting an input-free `TRANSFER` with identical parameters, forcing a collision with an already-spent `NoteId`. Requiring an input makes this attack computationally infeasible, as the attacker would also need to control the input `NoteId`.
### ZK Circuit Simplicity

Crucially, the `derive_note_id` template circuit requires no modification. By parameterising it on a generic `op_id`, each operation type, `TRANSFER`, `LEADER_CLAIM`, `CHANNEL_WITHDRAW` feeds its own unique Identifier while reusing the same constraint system. This keeps the proving infrastructure stable and avoids per-operation circuit variants.
### Semantic Correctness

`TRANSFER` is semantically a movement of value: it consumes existing notes and produces new ones, and is the right tool for splitting, merging, or redirecting value already held in the Mantle ledger. `LEADER_CLAIM`, `CHANNEL_WITHDRAW`, and `CHANNEL_DEPOSIT` are boundary operations: they interface with external systems (the PoS reward pool, payment channels) and directly issue or redeem notes without routing through `TRANSFER`'s balance accounting. This proposal enforces that boundary by requiring `TRANSFER` to have at least one input, and by having each boundary operation own its note issuance or consumption directly. The result is clean separation: value movement and value creation/destruction are handled by distinct operations, which simplifies protocol reasoning.
## Details

### Mantle Specification

#### Mantle Transaction Balance

We change the Mantle Transaction Balance computation to calculate the balance of Transfer Operations only:
```text
tx_fee = gas_fees(signed_tx)  # Not an unsigned int
assert tx_fee == get_transaction_balance(signed_tx)

def get_transaction_balance(signed_tx: SignedMantleTx) -> int:
    balance = 0   # It's important to not use unsigned int here to avoid
                  # overflow vulnerabilities
    for op in signed_tx.tx.ops:
-       if op.opcode == LEADER_CLAIM:
-           balance += get_leader_reward()
-       if op.opcode == CHANNEL_DEPOSIT:
-           balance -= get_channel_deposit_amount(op)
-       if op.opcode == CHANNEL_WITHDRAW:
-           balance += get_channel_withdrawal_amount(op)
        if op.opcode == TRANSFER:
            for inp in op.inputs:
                balance += get_value_from_note_id(inp)
            for out in op.outputs:
                balance -= out.value
    return balance
```

#### Channel Operations

#### Channel State

We add a channel identifier nonce in the Channel State. It is initialized at 0, and each time a `CHANNEL_WITHDRAW` creates a note as output, it is used to derive a unique `OpId`:
```python
channels: dict[ChannelId, ChannelState] # ChannelId is 32 bytes

class ChannelState:
    # Channel Configuration
    accredited_keys: list[Ed25519PublicKey]  # limited to 65 535 keys
    configuration_threshold: u16   # indicating how many keys are
                   # required to update the configuration

    # Message Ordering
    tip_hash: hash

    # Decentralized Sequencing
    tip_slot: Slot
    tip_sequencer: u16      # indicating the actual
                            # sequencer position in the list of accredited keys
    tip_sequencer_starting_slot: Slot
    posting_timeframe: u32  # number of slots (0 = infinity)
    posting_timeout: u32    # number of slots (0 = no timeout)

    # Bridging
    balance: TokenValue            # See the Note section for its precision
+   withdrawal_nonce: u32          # Nonce used to derive a withdraw OpId
    withdraw_threshold: u16        # indicating how many keys are
                  # required to withdraw funds from the channel

def default_channel(block_slot: Slot, keys: list[Ed25519PublicKey])
                            -> ChannelState:
    return ChannelState(
        tip_hash = ZERO,
        tip_slot = block_slot,
        accredited_keys = keys,
        tip_sequencer = 0,
        tip_sequencer_starting_slot = block_slot,
        posting_timeframe = 0,
        posting_timeout = 0,
        configuration_threshold = 1,
        balance = 0,
+       withdrawal_nonce = 0,
        withdraw_threshold = 1)
```

The withdraw nonce is incremented by one during `CHANNEL_WITHDRAW` execution: Increase the channel withdrawal_nonce.
#### Channel Deposit

#### Payload

The `CHANNEL_DEPOSIT` Operation now takes a list of inputs to consume. The consume notes replace the amount because it’s directly derived from the consume notes.
```text
class ChannelDeposit:
    channel: ChannelId
-   amount: TokenValue
+   inputs: list[NoteId]  # the list of consumed note identifiers
    metadata: bytes
```

#### Proof

The Channel Deposit now consumes notes as input. For this reason the Operation needs to prove the ownership of the note. This is done through a ZkSignature.
>

  A Channel Deposit proves the ownership of the consumed notes using a Zero Knowledge Signature Scheme (ZkSignature).
```text
None # Indirectly signed through the Transfer signature
ZkSignature
```

#### Validation

We now need to check the proof and the validity of the consumed `NoteId`. This is done in the exact same way as transfer is validated and executed.
>

  *Given*
```text
mantle_txhash: ZkHash # ZkHash of mantle tx containing this ledger tx
deposit: ChannelDeposit
deposit_proof: ZkSignature

channels: dict[ChannelId, ChannelState]

ledger: Ledger
locked_notes: dict[NoteId, LockedNote]
```

  *Validate*
  1. Verify that the channel exist
```text
assert deposit.channel in channels
```

  2. Ensure all inputs are unspent.
```text
assert all(ledger.is_unspent(note_id) for note_id in deposit.inputs)
```

  3. Validate ownership over deposited notes.
```text
input_notes = [ledger[input_note_id] for input_note_id in deposit.inputs]
input_pks = [note.public_key for note in input_notes]
assert ZkSignature_verify(mantle_txhash, deposit_proof, input_pks)
```

  4. Ensure inputs are not locked.
```text
# Ensure inputs are not locked
for note_id in deposit.inputs:
    assert note_id not in locked_notes
```

#### Execution

We now need to remove the note from the Ledger:
>

  *Given*
```text
deposit: ChannelDeposit

channels: dict[ChannelId, ChannelState]

ledger: Ledger
```

  *Execute*
  1. Remove inputs from the ledger.
```text
for note_id in deposit.inputs:
    # updates the merkle tree to zero out the leaf for this entry
    # and adds that leaf index to the list of unused leaves
    ledger.remove(note_id)
```

  2. Increase the balance of the channel
```text
for inp in deposit.inputs:
    channels[deposit.channel].balance += inp.value
channels[deposit.channel].balance += deposit.amount
```

#### Example

We need to update the example because the payload was modified:
```text
deposit = ChannelDeposit(
    channel=ZONE_A,
-   amount=50,
+   inputs=[alice_deposit_note_id]    # This is a note of 50 tokens
    metadata=b"deposit to address: 0x..."
)
```

#### Channel Withdraw

#### Payload

We redefine the Payload to take notes as output instead of an amount:
```text
class ChannelWithdraw:
    channel: ChannelId
-   amount: TokenValue
+   outputs: list[Note]
+   withdrawal_nonce: u32
```

#### Validation

We update the validation to check the format of outputted Notes and to fit the new payload
```text
+ # Check that the outputs are valid
+ for output in withdrawal.outputs:
+     assert output.value > 0
+     assert output.value < 2**64

# Check that the channel exists
assert withdrawal.channel in channels
chan = channels[withdrawal.channel]

+ # Check that the withdraw nonce is correct
+ assert channels[withdrawal.channel].withdrawal_nonce == withdrawal.withdrawal_nonce

# Check that the channel has enough funds
+ withdrawal_amount = sum(output.value for output in withdrawal.outputs)
+ assert chan.balance >= withdrawal_amount
- assert chan.balance >= withdrawal.amount

# Check that there are enough signatures
assert len(proof.signatures) == len(proof.indexes)
assert len(proof.signatures) == chan.withdraw_threshold

# Check that every index is unique
assert len(proof.indexes) == len(set(proof.indexes))

# Check the signatures
for sig, idx in zip(proof.signatures, proof.indexes):
    assert Ed25519_verify(txhash, chan.accredited_keys[idx], sig)
```

#### Execution

We update the execution to remove notes from the ledger and updated the way the balance is decreased:
>

  1. Decrease the balance of the Channel
```text
for output in withdrawal.outputs:
    channels[withdrawal.channel].balance -= output.value
    channels[withdrawal.channel].balance -= withdrawal.amount
```

  2. Add outputs to the ledger.
```text
withdrawal_id = derive_op_id(withdrawal)
for (output_number, output_note) in enumerate(withdrawal.outputs):
    output_note_id = derive_note_id(withdrawal_id, output_number, output_note)
    ledger.add(output_note_id)
```

  3. Increase the channel `withdrawal_nonce`
```text
channels[withdrawal.channel].withdrawal_nonce += 1
```

#### Example

The example needs an update to match the new payload
```text
# Sequencer encodes his withdrawal
withdrawal = ChannelWithdraw(
    channel=ZONE_A,
+   outputs=[Note(pk=alice, value=50)]
-   amount=50
)
```

#### Leader Claim

#### Payload

Because the note is created directly through this Operation, the leader need to indicate its Public key to receive the funds. This needs an update in the Payload:
```python
class ClaimRequest:
    rewards_root: zkhash # Merkle root used in the proof for voucher membership
    voucher_nf: zkhash
+   public_key: ZkPublicKey
```

#### Execution

The execution now derives the note id and directly introduces it in the ledger:
>

  **Execution**
  *Given*
```text
claim: ClaimRequest

ledger: Ledger
voucher_nullifier_set: set[zkhash]
leaders_rewards: TokenValue   # The pool of tokens to be claim by leaders
leader_reward: TokenValue     # The amount one leader can claim
```

  *Execution*
  1. Add `claim.voucher_nf` to the `voucher_nullifier_set`.
  2. ~~Increase the balance of the Mantle Transaction by the leader reward amount according to Leaders Reward. ~~
  3. Denoting by `leader_reward` the amount defined for leader rewards in Leaders Reward, construct a single output note with value leader_reward under the public key defined in the payload, and insert it into the Ledger:
```text
output_note = Note(
    value = leader_reward
    public_key = claim.public_key,
)
claim_id = derive_op_id(claim)
output_note_id = derive_note_id(claim_id, 0, output_note)
ledger.add(output_note_id)
```

  4. Reduce the leader’s reward `leaders_rewards` value by the same amount (without ZK proof).

#### Example

The example needed an update to match the new payload
```text
claim=ClaimRequest(
    rewards_root=REWARDS_MERKLE_TREE.root(),
    voucher_nf=voucher_nullifier,
+   public_key=leader_one_time_key
)
```

#### Transfer

#### Payload

We added an enforcement in the comment to say that the list of inputs must be at least 1
```python
class Transfer:
    inputs: list[NoteId]  # the non-empty list of consumed note identifiers
    outputs: list[Note]
```

#### Transfer Hash

**We removed this section to match the new `derive_operation_id` function.**
#### Validation

We need to verify that the transfer is non-empty. So we added this as a first step of the verification:
>

  1. Ensure the Transfer in non-empty
```text
assert len(transfer.inputs) > 0
```

#### Execution

In the execution we update how the `N``oteId` is computed to match the new functions names
```text
- transfer_hash = transfer_hash(transfer)
+ transfer_id = derive_operation_id(transfer)
for (output_number, output_note) in enumerate(transfer.outputs):
-    output_note_id = derive_note_id(transfer_hash, output_number, output_note)
+    output_note_id = derive_note_id(transfer_id, output_number, output_note)
    ledger.add(output_note_id)
```

#### Note Id

The NoteId Section also needs an update to include the new `OpId` derivation. We need to define a common way to derive the `OpId` and to update the function that derives the `NoteId`:
>

  ~~Any note can be uniquely identified by the Transfer Operation that created it and its output number: `(transfer_hash, output_number)`. However, it is often useful to have a commitment to the note fields for use in ZK proofs (e.g., for PoL), so we include the note in the note identifier derivation.~~
  A note can be uniquely identified by the Operation that created it and its output number: `(op_id, output_number)` if each Operation is uniquely identifiable. For this reason, every Operation that output notes have a unique payload that is used to derive the Operation identifier. It is useful to have a commitment to the note fields for use in ZK proofs (e.g., for PoL), we include the note in the note identifier derivation.

```text
+ def derive_op_id(operation: Op) -> Hash:
+     op_bytes = encode(op)
+     h = Hasher() # /!\ This is a classic hash not a ZkHash /!\
+     h.update(b"OPERATION_ID_V1")
+     h.update(op_bytes)
+     return h.digest()

- def derive_note_id(transfer_hash: zkhash, output_number: int, note: Note) -> NoteId:
+ def derive_note_id(op_id: Hash, output_number: int, note: Note) -> NoteId:
    return zkhash(
        FiniteField(b"NOTE_ID_V1", byte_order="little", modulus= p),
-       transfer_hash,
+       FiniteField(op_id, byte_order="little", modulus= p),
        FiniteField(output_number, byte_order="little", modulus= p),
        FiniteField(note.value, byte_order="little", modulus= p),
        note.public_key
    )
```

> `op_id` is a classical 256-bit hash digest and must be reduced to a field element before being passed to the ZkHasher. We apply a direct modular reduction mod `p` (via `FiniteField(..., modulus=p)`). Since $`p \approx2^{-254}`$, the reduction is slightly non-uniform, values in $`[0, 2^{256} \mod p)`$ appear one extra time, but this is inconsequential in practice: the collision probability remains around $`2^{-254}`$, and `NoteId` uniqueness is not derived from uniformity of `op_id` over $`𝔽_p`$ but from the collision-resistance of the underlying hash and per-operation payload uniqueness.

#### Gas Determination

The Gas Cost table was also updated to reflect the new `CHANNEL_DEPOSIT` cost:

| Constants | Value |
| --- | --- |
| EXECUTION_TRANSFER_GAS | 590 |
| EXECUTION_CHANNEL_INSCRIBE_GAS | 56 |
| EXECUTION_CHANNEL_CONFIG_GAS | 56 |
| EXECUTION_CHANNEL_DEPOSIT_GAS | 590 |
| EXECUTION_CHANNEL_WITHDRAW_GAS | 56 |
| EXECUTION_SDP_DECLARE_GAS | 646 |
| EXECUTION_SDP_WITHDRAW_GAS | 590 |
| EXECUTION_SDP_ACTIVE_GAS | 590 |
| EXECUTION_LEADER_CLAIM_GAS | 580 |

### Gas Cost Determination

#### Overview

The table containing the summary of Gas Costs needs an update because the `CHANNEL_DEPOSIT` gas cost increases (see Channel Deposit):
```text
TRANSFER_GAS = 590
CHANNEL_INSCRIBE_GAS   = 56
CHANNEL_CONFIG_GAS     = 56 * configuration_threshold
- CHANNEL_DEPOSIT_GAS    = 0
+ CHANNEL_DEPOSIT_GAS    = 590
CHANNEL_WITHDRAW_GAS   = 56 * withdraw_threshold
SDP_DECLARE_GAS        = 646
SDP_WITHDRAW_GAS       = 590
SDP_ACTIVE_GAS         = 590
LEADER_CLAIM_GAS       = 580
```

#### Transfer

We add the derivation of the outputs `NoteId` in the cost of a `TRANSFER`
```text
Execution: negligible.
    - Verification of the output validity: negligible.
    - Insertion of the note in the ledger: negligible.
+   - Derivation of the note identifiers: negligible
```

#### Channel Deposit

This needs a full update that changes its price from 0 to 590 Execution Gas.
>

  ~~The validation process is free as it doesn't require any verification and its execution only requires modifying the balance of the channel.~~
  The Execution Gas of the Channel Deposit Operation compensates for the verification of the [ZkSignature](../../common-cryptographic-components.md#zksignature-zero-knowledge-signature) proof and for the check of the inputs.
  **Execution: **~~**negligible**~~**. ~590k CPU cycles.**
  - Verification of the ZK signature: 590,000 cycles.
  - Verification that the notes are in the ledger: negligible.
  - Verification that the notes are unlocked: negligible.
  - Increase of the channel balance: negligible

#### Channel Withdraw

We update what covers a channel withdraw. This doesn’t affect its Execution Gas cost:
>

  The validation process requires verifying multiple Eddsa25519 signatures, and updating the balance of the channel. The execution require deriving note Id and adding notes to the ledger.
  **Execution: ~56k CPU cycles * withdraw_threshold.**
  - Verification of `withdraw_threshold` Ed25519Signatures: 56,000 cycles per signature.
  - Decrease of the channel balance: negligible.
  - Verification of the output validity: negligible.
  - Insertion of the note in the ledger: negligible.
  - Derivation of the note identifiers: negligible

#### Leader Claim

We updated what covers a leader claim to include the new output note.
>

  **Execution: ~580k CPU cycles.**
    - Verification that the voucher nullifier isn’t already in the set: negligible.
    - Verification that the rewards root is one of the root of the reward tree of the last blocks: negligible.
    - Verification of the proof of claim: 580,000 cycles.
    - Insertion of the nullifier in the voucher nullifier set: negligible.
    - Insertion of the note in the ledger: negligible.
    - Derivation of the note identifiers: negligible

### Mantle Transaction Encoding

We update the encoding to match the new payloads
#### Ledger

We move the definition of notes and noteIds that was previously in the Transfer Section into a dedicated Ledger section:
>

### Ledger

```text
Note   = Value ZkPublicKey
Value  = UINT64
NoteId = FieldElement
```

#### Channel Deposit

```text
- ChannelDeposit = ChannelId Amount Metadata
- Amount         = UINT64
+ ChannelDeposit = ChannelId Inputs Metadata
+ Inputs         = InputCount *NoteId
+ InputCount     = Byte
  Metadata       = UINT32 *BYTE
```

#### Channel Withdraw

```text
- ChannelWithdraw = ChannelId Amount
+ ChannelWithdraw = ChannelId Outputs WithdrawalNonce
+ Outputs         = OutputCount *Note
+ OutputCount     = Byte
+ WithdrawalNonce   = UINT32
```

#### Leader Claim

```text
- LeaderClaim      = RewardsRoot VoucherNullifier
+ LeaderClaim      = RewardsRoot VoucherNullifier PublicKey
  RewardsRoot      = FieldElement  ; Merkle root for voucher membership proof
  VoucherNullifier = FieldElement
+ PublicKey        = ZkPublicKey
```

### Cross-Channel Messaging

This document needs only a small fix in the Atomic transfer between two zones example:
```text
# Sequencer of Zone A encodes the withdrawal from Zone A
withdrawal = ChannelWithdraw(
    channel=CHANNEL_ZONE_A,
+   outputs=[temporary_transfer_note]
-   amount=5
)

# Sequencer of zone B encodes the deposit to Zone B
deposit = ChannelDeposit(
    channel=CHANNEL_ZONE_B,
+   inputs=[temporary_transfer_note],
-   amount=5
)
```

### Service Reward Distribution Protocol

The SRDP protocol also needs an update: the rewards are directly inserted in the ledger without coming from an Operation. For this reason, the way the `NoteId` of these rewards are derived need to be updated:
from
> The note Id is computed using the result of `zkhash(FiniteField(`[`ServiceType`](../../bedrock-v1.1-mantle-specification.md)`, byte_order="little", modulus= p) || session_number)` as the transaction hash. The output number corresponds to the position of the `zk_id` when sorted in ascending order.

to
> The `NoteId` is computed using the result of `hash(`[`ServiceType`](../../bedrock-v1.1-mantle-specification.md)`|| session_number)` as the `op_id`. The output number corresponds to the position of the `zk_id` when sorted in ascending order.

## Affected Specifications

### Created

### Updated

- [v1.4] Mantle Specification

- \[v1.4\]\[Analysis\] Gas Cost Determination

- [v1.3] Mantle Transaction Encoding

- \[v1.1\]\[Template\] Cross-Channel Messaging

- **[v1.2.1] Service Reward Distribution Protocol**

### Deprecated

[Mantle](../../../deprecated/v1.2.0-mantle.md)
[[Analysis] Gas Cost Determination](../../../deprecated/v1.4.0-analysis-gas-cost-determination.md)
[Mantle Transaction Encoding](../../../deprecated/v1.1.0-mantle-transaction-encoding.md)
[[Template] Cross-Channel Messaging](../../../deprecated/v1.1.0-template-cross-channel-messaging.md)
[Service Reward Distribution Protocol](../../../deprecated/v1.0.0-bedrock-service-reward-distribution.md)
### Retired
