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

Rollup channels let a Zone compute its state off chain and settle it on chain with proofs of its state transitions. This document specifies the rollup Operations; the Mantle Transaction that carries them and the ledger they act on are specified in [Mantle](bedrock-mantle-specification.md), and the sequencing they share with native channels in [Mantle Channels](bedrock-mantle-channels.md).

# Operations

## Rollup Operations

A rollup channel is a channel whose state follows a state transition function (STF), a Groth16 circuit its creator chooses. Its sequencers take turns, following the [round-robin](bedrock-mantle-channels.md#decentralized-sequencing) of every channel, to post the data of its state transitions with [`ROLLUP_INSCRIBE`](#rollup_inscribe). Anyone then proves these inscriptions with [`ROLLUP_PROVE`](#rollup_prove), one at a time and in the order they were inscribed. Each proof is a step of the rollup, the application of one inscription by `ROLLUP_PROVE`: a proof of its STF takes the rollup from its state root to the next one, and the step mints pending [deposits](#rollup_deposit), moves the notes of the rollup and pays some of them out to the ledger. The proven prefix of the inscriptions is the proven state of the rollup, and the inscriptions after it wait for their steps. A step reads the slot of the block that included its inscription, so a rollup can depend on time while every prover knows the inputs of a step as soon as its inscription is in a block.

**What the ledger checks.** The notes of a rollup live in a note set of their own, which only `ROLLUP_PROVE` spends ([Ledger](bedrock-mantle-specification.md#ledger)). Each transfer of a step is a [ZkTransfer](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) with an `excess_value` of `0`, so whatever the STF, the ledger checks that a step keeps the value of the notes it moves and spends no note twice. A faulty STF can give the funds of its rollup to the wrong users but never create value, so the notes of a rollup take part in Proof of Stake as safely as ledger notes. A rollup whose funds take part in Proof of Stake should give the notes its transfers create the staking keys of their users, and never `PK0` ([Keys](bedrock-mantle-specification.md#keys)), since the deposit note of a step has staking key `0`. The STF proof decides who gets what: which deposits a step mints, and which notes its transfers consume, create and pay out.

**Sequencers can only delay.** No signature reconfigures a rollup channel: each step carries the next accredited keys and rotation parameters of the rollup, which its STF proof covers, so only the rules of the STF change who sequences the rollup. The round-robin hands the turn to the next accredited key when the timeframe or the timeout of a sequencer elapses, so a sequencer that refuses to inscribe a transition only delays it until a sequencer that accepts it takes its turn, provided the configuration of the rollup sets a timeframe; a timeout alone replaces only a sequencer that inscribes nothing. Anyone posts the steps, so no party can hold back the proof of an inscription, and a step applies exactly the data its sequencer inscribed when the STF circuit recomputes the `op_id` of that inscription, as [STF Verification Key](#stf-verification-key) recommends.

**Recommendations.** The ledger leaves the following choices to the rollup, and they are recommended to a rollup that wants any prover to be able to prove it:

- Hold the notes of the rollup by `PK0` ([Keys](bedrock-mantle-specification.md#keys)), the public key whose secret key everyone knows, so that no step depends on a key one party holds.
- Make a step depend only on its inscription, which the STF circuit reads through the `op_id` of the inscription ([STF Verification Key](#stf-verification-key)), and on the state before it, so that every prover computes the same step from public data.
- Credit every minted deposit in the state of the rollup as its intent asks, since the ledger merges the deposits a step mints into one note and leaves their accounting to the STF.
- Pay the provers inside the rollup, since the ledger pays nothing for a step and its prover pays the fees of its Mantle Transaction.
- Publish what lets a prover recompute the notes of the rollup, such as their openings or the data they derive from, since a ZkTransfer consuming a note takes its opening.

**What the ledger does not guarantee.** Funds leave a rollup only through its steps: a user exits when a step pays it out, and no withdrawal bypasses the STF. If no sequencer inscribes, no step can be proven and the funds of the rollup stay frozen. Users trust the STF circuit of the rollup, the rule by which its steps change its verification key, and the setup of each key: a faulty circuit, or a key whose setup lets someone forge proofs, can pay the funds of the rollup to anyone.

### Rollup State

Validators keep the state of a rollup channel in the `kind` of its [`ChannelState`](bedrock-mantle-channels.md#channel-operations), next to the sequencing fields every channel has:

```python
class RollupChannel:
    note_set: int                         # index of the note set of the rollup in ledger.sets
    key: Groth16StoredKey                 # the verification key of the STF proofs, with e(alpha, beta)
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

### STF Verification Key

```python
class Groth16VerificationKey:
    alpha: G1
    beta: G2
    gamma: G2
    delta: G2
    ic: list[G1]  # (len = 6) one point per public input of an STF proof, plus one

class Groth16StoredKey:
    key: Groth16VerificationKey
    alpha_beta: GT  # the pairing e(alpha, beta), computed when the key is stored
```

`G1` and `G2` are points of the groups of BN254 of these names, and `alpha`, `beta`, `gamma`, `delta` and `ic` are the points of a [Groth16](common-cryptographic-components.md#groth16-zk-snark) verification key.

An STF proof always has five public inputs: the state root of the rollup, its next state root, the `op_id` of the inscription it proves, the slot of the block that included that inscription, and `effects_hash`, the hash of the effects of the step ([`ROLLUP_PROVE`](#rollup_prove)). Since the size of a Groth16 verification key depends only on its number of public inputs, every rollup key has the same size, and the ledger stores and verifies the key of every rollup the same way.

A rollup that applies the data of its inscriptions should have its STF circuit recompute the `op_id` it takes as its third public input from the encoded [`RollupInscribe`](#rollup_inscribe) it applies, so that its proof covers exactly the data, parent and signer its sequencer inscribed. The circuit then hashes the inscription with BLAKE2b, over up to [`MAX_OPERATION_DATA_SIZE`](mantle-transaction-encoding.md#channel-operations) bytes of data.

`Groth16_verify(key, public_inputs, proof)` verifies a [Groth16](common-cryptographic-components.md#groth16-zk-snark) proof against a verification key, given with the pairing $`e(\alpha, \beta)`$ stored with it, and its public inputs. `pairing(P, Q)` is the optimal ate pairing of BN254, from $`\mathbb{G}_1 \times \mathbb{G}_2`$ to $`\mathbb{G}_T`$, the subgroup of order $`p`$ of $`\mathbb{F}_{q^{12}}^*`$, $`q`$ being the modulus of the base field of BN254, whose elements take 384 bytes.

### ROLLUP_CREATE

Create a rollup channel with its accredited keys, its rotation parameters, the verification key of its STF proofs and its initial state root. Anyone can create a rollup channel, under a `ChannelId` no channel holds. No Operation reconfigures the channel with signatures afterwards: only the steps of the rollup change its accredited keys, its rotation parameters, its verification key and its state root.

#### Payload

```python
class RollupCreate:
    channel: ChannelId                        # 32 bytes, the channel to create
    keys: list[Ed25519PublicKey]              # the accredited keys, limited to 65 535 keys
    posting_timeframe: u32                    # number of slots (0 = infinity)
    posting_timeout: u32                      # number of slots (0 = no timeout)
    verification_key: Groth16VerificationKey  # the key of the STF proofs
    state_root: zkhash                        # the initial state root of the rollup
```

#### Proof

  The proof is empty.

#### Execution Gas

  Rollup Create Operations have a fixed Execution Gas cost of `EXECUTION_ROLLUP_KEY_GAS`, the cost of the checks of the key and of the pairing $`e(\alpha, \beta)`$. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

#### Validation

  *Given*

```python
create: RollupCreate

channels: dict[ChannelId, ChannelState]
```

  *Validate*

  1. Ensure the channel does not exist, since the kind of a channel is fixed when it is created.
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

Append a note set for the rollup, as every new channel does ([Ledger](bedrock-mantle-specification.md#ledger)), and store the channel with the sequencing fields of [`default_channel`](bedrock-mantle-channels.md#channel-operations), the rotation parameters of the payload, and the key with the pairing $`e(\alpha, \beta)`$ of its points.

```python
ledger.sets.append(empty_note_set())
key = create.verification_key
chan = default_channel(block_slot,
                       create.keys,
                       RollupChannel(note_set = len(ledger.sets) - 1,
                                     key = Groth16StoredKey(key=key, alpha_beta=pairing(key.alpha, key.beta)),
                                     state_root = create.state_root,
                                     deposits = {},
                                     unproven = []))
chan.posting_timeframe = create.posting_timeframe
chan.posting_timeout = create.posting_timeout
channels[create.channel] = chan
```

The pairing $`e(\alpha, \beta)`$, an element of $`\mathbb{G}_T`$ of 384 bytes, is the costliest part of what a verification derives from the key alone; it is computed once and paid by the Operation that stores the key. The line coefficients of the pairings with $`-\gamma`$ and $`-\delta`$ are not stored, since they would take tens of kilobytes of ledger state per rollup: each STF proof computes them, and pays for it.

### ROLLUP_INSCRIBE

Write the data of a state transition to a rollup channel, the data being permanently stored on the Logos Blockchain. The current sequencer of the rollup posts it, extending the tip of the channel as an inscription of a native channel does, and the inscription joins the unproven inscriptions of the rollup, which its steps prove in that order.

The ledger does not read the data of the inscription: the STF does, through its `op_id` ([STF Verification Key](#stf-verification-key)). A rollup should let its STF prove, for an inscription it cannot apply, a step that mints no deposit, makes no transfer and keeps its state root, so that the inscription does not block the ones after it.

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

  Rollup Inscribe Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_INSCRIBE_GAS`, the cost of an inscription. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

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
      assert isinstance(chan.kind, RollupChannel)
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
      chan.kind.unproven.append((derive_op_id(msg), block_slot))
      ```

The slot of the block is recorded with the [`op_id`](bedrock-mantle-specification.md#note-commitment-and-nullifier) of the inscription because the STF proof of its step takes it as a public input: it is fixed once the inscription is in a block, and the prover reads it from the ledger.

### ROLLUP_DEPOSIT

Deposit value into a rollup channel. The deposit consumes notes of the ledger note set and creates no note: it records a [pending deposit](#rollup-state) of its value and its intent in the `deposits` of the rollup, under its [`op_id`](bedrock-mantle-specification.md#note-commitment-and-nullifier), until a [`ROLLUP_PROVE`](#rollup_prove) mints it into the note set of the rollup.

A deposit waits until a step chosen by the sequencers of the rollup mints it, and the ledger never refunds it, so the STF decides when the rollup takes it in. Its ZkTransfer has no outputs, so the change of the depositor comes from a [Transfer](bedrock-mantle-specification.md#transfer) earlier in the same Mantle Transaction, which splits off the value to deposit into notes the deposit then consumes. The ledger keeps only the value and intent of a deposit: its inscription publishes data for the zone, which its `intent` can commit to.

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

  A Rollup Deposit proves the ownership of the notes being consumed, and that their value is the deposited value plus the excess value, using a [Zero Knowledge Transfer Proof (ZkTransfer)](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) with no outputs.

```python
ZkTransfer
```

#### Execution Gas

  Rollup Deposit Operations have a fixed Execution Gas cost of `EXECUTION_CHANNEL_DEPOSIT_GAS`, the cost of a deposit. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

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
      assert isinstance(chan.kind, RollupChannel)
      ```

  3. Ensure all inputs are spendable in the [ledger note set](bedrock-mantle-specification.md#ledger), `LEDGER_SET`.
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
      chan.kind.deposits[derive_op_id(deposit)] = PendingDeposit(value=deposit.value,
                                                                 intent=deposit.intent)
      ```

### ROLLUP_PROVE

Apply the oldest unproven inscription of a rollup channel with a step of the rollup. Anyone posts it: the step mints the pending deposits it lists into one note of the rollup note set, applies its transfers to the notes of the rollup and pays their payouts to the ledger note set, and sets the next state root, accredited keys and rotation parameters of the rollup, and optionally its next verification key, all of which its STF proof covers.

A step proves only the oldest entry of `unproven`, so a node never holds a proof it has not applied. Provers compute the steps of consecutive inscriptions in parallel, each from the state the step before it leaves, and the mempool orders the steps by their inscriptions. The transfers of a step are verified against the live commitment MMR root of the rollup note set, which a prover knows in advance since only this Operation appends to that set, so consecutive steps of a rollup can share a block, and even a Mantle Transaction.

#### Payload

```python
class RollupTransfer:
    inputs: list[NoteNullifier]    # nullifiers of the consumed notes of the rollup note set
    outputs: list[NoteCommitment]  # commitments of the created notes of the rollup note set
    payouts: list[NoteCommitment]  # commitments of the notes created in the ledger note set

class RollupProve:
    channel: ChannelId                               # 32 bytes, the rollup channel
    deposits: list[Hash]                             # the op_id of each pending deposit the step mints
    transfers: list[RollupTransfer]                  # the transfers of the step, in the order they apply
    state_root: zkhash                               # the next state root of the rollup
    keys: list[Ed25519PublicKey]                     # the next accredited keys, limited to 65 535 keys
    posting_timeframe: u32                           # number of slots (0 = infinity)
    posting_timeout: u32                             # number of slots (0 = no timeout)
    verification_key: Groth16VerificationKey | None  # the next key of the STF proofs, None to keep the current one
```

The deposits a step mints become one note of the rollup note set, the deposit note, which holds their total value. It is held by `PK0`, so that any prover can spend it in a transfer of the step or of a later step, and its staking key is `0`, so that no one leads with it ([Keys](bedrock-mantle-specification.md#keys)). Its nonce derives from the `op_id` of the inscription the step proves, and a step proves an inscription once, so no two deposit notes share a commitment.

Each `RollupTransfer` is a [ZkTransfer](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) whose outputs are its `outputs` followed by its `payouts`, and it balances exactly, with an `excess_value` of `0`. A step therefore pays no fee: its prover pays the fees of its Mantle Transaction with another Operation of it, such as a Transfer.

The step that [`ROLLUP_INSCRIBE`](#rollup_inscribe) recommends for an inscription the STF cannot apply, with no deposit, no transfer and the same state root, is valid: every transfer consumes at least one note, as `assert_spendable` requires, but a step can have no transfer.

The STF proof covers the effects of the step through `effects_hash`, its fifth public input: the value and intent of every minted deposit, in the order of `deposits`, the inputs, outputs and payouts of every transfer, and the digest of the next configuration. The configuration digest is a BLAKE2b-256 hash, under the DST `ROLLUP_CONFIG_V1`, of the encoded next accredited keys, rotation parameters and optional verification key, as the [`RollupProve`](mantle-transaction-encoding.md#rollup-operations) of the encoding encodes them, reduced modulo $`p`$ as `op_id` is. A rollup should keep the digest of its configuration in its state, so that its STF circuit compares the digest the ledger computes with the one its next state holds and never recomputes the configuration digest, its transactions approving any change of the digest.

```python
def rollup_config_digest(keys: list[Ed25519PublicKey],
                         posting_timeframe: u32,
                         posting_timeout: u32,
                         verification_key: Groth16VerificationKey | None) -> zkhash:
    h = Hasher() # /!\ This is a classic hash not a zkhash /!\
    h.update(b"ROLLUP_CONFIG_V1")
    h.update(encode(keys))               # KeyCount *Signer of the encoding
    h.update(encode(posting_timeframe))  # PostingTimeframe
    h.update(encode(posting_timeout))    # PostingTimeout
    h.update(encode(verification_key))   # OptionalKey
    return FiniteField(h.digest(), byte_order="little", modulus= p)

def rollup_effects_hash(minted: list[PendingDeposit],
                        transfers: list[RollupTransfer],
                        config_digest: zkhash) -> zkhash:
    effects = [FiniteField(len(minted), byte_order="little", modulus= p)]
    for deposit in minted:
        effects.append(FiniteField(deposit.value, byte_order="little", modulus= p))
        effects.append(deposit.intent)
    effects.append(FiniteField(len(transfers), byte_order="little", modulus= p))
    for transfer in transfers:
        for notes in (transfer.inputs, transfer.outputs, transfer.payouts):
            effects.append(FiniteField(len(notes), byte_order="little", modulus= p))
            effects.extend(notes)
    return zkhash(
        FiniteField(b"ROLLUP_EFFECTS_V1", byte_order="little", modulus= p),
        *effects,
        config_digest)
```

#### Proof

```python
class RollupProveOpProof:
    transfer_proofs: list[ZkTransfer]  # one per transfer, in the order of the transfers
    stf_proof: Groth16Proof            # the proof of the STF, under the current key of the rollup
```

The ZkTransfers and the STF proof of a step are bound to the `op_id` of the inscription it proves, which is the `msg` of every ZkTransfer and the third public input of the STF proof, and not to the `mantle_txhash`, so anyone can post the step. A copy of the step in another Mantle Transaction applies the same step, and only once, since the step removes its inscription from `unproven`.

#### Execution Gas

  Rollup Prove Operations have an Execution Gas cost of `EXECUTION_TRANSFER_GAS * len(transfers) + EXECUTION_ROLLUP_PROOF_GAS`, the cost of the transfers and of the STF proof, plus `EXECUTION_ROLLUP_KEY_GAS` when the payload carries a next verification key. See [Gas Determination](bedrock-mantle-specification.md#gas-determination) for the Execution Gas values.

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
      assert isinstance(chan.kind, RollupChannel)
      rollup = chan.kind
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
      note_set = ledger.sets[rollup.note_set]
      peaks = list(note_set.commitments)
      for note_commitment in deposit_outputs:
          mmr_append(peaks, note_commitment)
      ```

  5. Ensure every transfer is spendable in the rollup note set and balances exactly, in the order of the transfers. A transfer can consume the deposit note and the outputs of the earlier transfers of the step, never a note an earlier transfer of the step consumes.
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

  6. Ensure the next configuration is one [`ROLLUP_CREATE`](#rollup_create) accepts: accredited keys with indexes the round-robin can hold in a `u16`, and, if the step carries a next verification key, every point of it on its curve, in its prime-order subgroup and not the point at infinity.
      ```python
      assert 0 < len(prove.keys) < 2**16
      key = prove.verification_key
      if key is not None:
          for point in [key.alpha] + key.ic:
              assert is_valid_g1(point)
          for point in [key.beta, key.gamma, key.delta]:
              assert is_valid_g2(point)
      ```

  7. Verify the STF proof under the current key of the rollup, from its state root to the next one, for the inscription `k`, the slot of its block and the effects of the step.
      ```python
      config_digest = rollup_config_digest(prove.keys,
                                           prove.posting_timeframe,
                                           prove.posting_timeout,
                                           prove.verification_key)
      assert Groth16_verify(rollup.key,
                            [rollup.state_root,
                             prove.state_root,
                             msg,
                             FiniteField(slot_k, byte_order="little", modulus= p),
                             rollup_effects_hash(minted, prove.transfers, config_digest)],
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
      rollup = chan.kind
      note_set = ledger.sets[rollup.note_set]
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

  3. Remove the proven inscription, and set the next state root and, if the step carries one, the next verification key with the pairing $`e(\alpha, \beta)`$ of its points.
      ```python
      rollup.unproven.pop(0)
      rollup.state_root = prove.state_root
      if prove.verification_key is not None:
          key = prove.verification_key
          rollup.key = Groth16StoredKey(key=key, alpha_beta=pairing(key.alpha, key.beta))
      ```

  4. If the next accredited keys or rotation parameters differ from the current ones, set them and restart the round-robin, as a [`CHANNEL_CONFIG`](bedrock-mantle-channels.md#channel_config) does, and otherwise leave the round-robin as it stands.
      ```python
      if (prove.keys, prove.posting_timeframe, prove.posting_timeout) != \
         (chan.accredited_keys, chan.posting_timeframe, chan.posting_timeout):
          chan.accredited_keys = prove.keys
          chan.tip_slot = block_slot
          chan.tip_sequencer = 0
          chan.tip_sequencer_starting_slot = block_slot
          chan.posting_timeframe = prove.posting_timeframe
          chan.posting_timeout = prove.posting_timeout
      ```

A step that keeps the configuration leaves the turn to the rotation of the sequencers, so the steps themselves never pin the turn to one sequencer. A change of configuration applies from the block of its step, not from the block of its inscription: the inscriptions after `k` that come before that step are signed under the current keys, and a sequencer a step removes stays accredited until that step is proven.
