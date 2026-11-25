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

A rollup channel is a channel whose state follows a state transition function (STF), a Groth16 circuit its creator chooses. Its sequencers take turns, following the [round-robin](bedrock-mantle-channels.md#decentralized-sequencing) of every channel, to post the data of its state transitions with [`ROLLUP_INSCRIBE`](#rollup_inscribe). Anyone then proves these inscriptions with [`ROLLUP_PROVE`](#rollup_prove), one at a time and in the order they were inscribed. Each proof is a step of the rollup: a proof of its STF takes the rollup from its state root to the next one, and the step mints pending [deposits](#rollup_deposit), moves the notes of the rollup and pays some of them out to the ledger. The proven prefix of the inscriptions is the finalized state of the rollup, and the inscriptions after it wait for their steps. A step reads the slot of the block that included its inscription, so a rollup can depend on time while every prover knows the inputs of a step as soon as its inscription is in a block.

**What the ledger checks.** The notes of a rollup live in a note set of their own, which only `ROLLUP_PROVE` spends ([Ledger](bedrock-mantle-specification.md#ledger)). Each transfer of a step is a [ZkTransfer](bedrock-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) with an `excess_value` of `0`, so whatever the STF, the ledger checks that a step keeps the value of the notes it moves and spends no note twice. A faulty STF can give the funds of its rollup to the wrong users but never create value, so the notes of a rollup take part in Proof of Stake as safely as ledger notes. The STF proof decides who gets what: which deposits a step mints, and which notes its transfers consume, create and pay out.

**Sequencers can only delay.** No signature reconfigures a rollup channel: each step carries the next accredited keys and rotation parameters of the rollup, which its STF proof covers, so only the rules of the STF change who sequences the rollup. The round-robin hands the turn to the next accredited key when the timeframe or the timeout of a sequencer elapses, so a sequencer that refuses to inscribe a transition only delays it until a sequencer that accepts it takes its turn, provided the configuration of the rollup sets a timeframe; a timeout alone replaces only a sequencer that inscribes nothing. Anyone posts the steps, so no party can hold back the proof of an inscription.

**Recommendations.** The ledger leaves the following choices to the rollup, and they are recommended to a rollup that wants any prover to be able to prove it:

- Hold the notes of the rollup by `PK0` ([Keys](bedrock-mantle-specification.md#keys)), the public key whose secret key everyone knows, so that no step depends on a key one party holds.
- Make a step depend only on its inscription and on the state before it, so that every prover computes the same step from public data.
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

A pending deposit waits in `deposits` until a step mints it. A step proves only the oldest entry of `unproven`, so every step starts from the state root the previous step left, and the finalized state of the rollup is always a prefix of its inscriptions.

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

The ledger does not read the data of the inscription: the STF does. A rollup should let its STF prove, for an inscription it cannot apply, a step that mints no deposit, makes no transfer and keeps its state root, so that the inscription does not block the ones after it.

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
