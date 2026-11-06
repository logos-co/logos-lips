# [RFC] Mantle: Vest a share of each proof of work reward

**Motivation and proposal:** [PR #515](https://github.com/logos-co/logos-lips/pull/515)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-04 |
| v2 | Follows the stack below: `commitment_root` and the full names of commitments and nullifiers, and the `note_pk` of a declaration, under which a handed-over stake now sits. The `SDP_DECLARE` and whole-transaction test vectors of Mantle hold the new encoding of a declaration | 2026-11-05 |
| v3 | Cryptarchia test vectors and a two-spend declaration vector; the unmeasured gas and the Execution Gas limit are TBD; recomputed declaration limits | 2026-11-05 |
| v4 | Vesting ends at an epoch start, `VESTING_EPOCHS = 49` epochs after the epoch of the referenced block; wallets no longer delay their spends | 2026-11-05 |
| v5 | Follows the nullifier and staking keys of the stack. `amount` goes, the stake being the sum of the spends; `vested_by` becomes `spending_slot`; the vesting check drops the active flag; a declaration that lapses waits for its lock | 2026-11-06 |
| v6 | Follows the stack below: a declaration also names `note_stake_pk`, and the service rewards go to the two keys of its service note. The declaration test vectors of Mantle and Cryptarchia hold the new field | 2026-11-06 |
| v7 | Every figure assumes a fixed claim reward of 334 LOGOS. Proof of Work requires the vested notes of a minimum stake to fit one declaration | 2026-11-06 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Mantle](#affected-specifications), [the vesting bound of a ZkTransfer](#1-vested-notes-and-the-vesting-bound-of-a-zktransfer) | `spending_slot` from the slot that recorded a ledger root, `0` for channel and service notes; no output carries a vesting end |
| 2 | Critical | **Start here** — [Mantle](#affected-specifications), [Service Declaration Protocol](#affected-specifications), [staking and the lock](#3-declarations-stake-through-zkstake-locked-until-an-epoch) | `locked_until` checked by every ZkStake and by `SDP_WITHDRAW`; the spends summing to the stake |
| 3 | Critical | [Mantle](#affected-specifications), [the ZkStake circuit](#4-the-zkstake-circuit) | 16 inputs, no output, the input constraints of the ZkTransfer |
| 4 | High | [Mantle](#affected-specifications), [Proof of Work](#affected-specifications), [the claim split](#2-a-claim-pays-a-liquid-and-a-vested-note) | the vesting end at an epoch start, counted from the epoch of the referenced block; the fee rule on the liquid part |
| 5 | High | [Proof of Leadership](#affected-specifications), [Proof of Quota](#affected-specifications), [vested notes lead](#5-vested-notes-lead) | vested notes lead, the proofs already reading the `data` of a note |
| 6 | High | [Mantle Transaction Encoding](#affected-specifications), [encoding](#6-encoding) | `SDPDeclare`, `StakeSpend`, `SDPDeclareProof` |
| 7 | Medium | [Block Construction](#affected-specifications), [Gas Cost Determination](#affected-specifications), [Execution Market](#affected-specifications), [Cryptoeconomics](#affected-specifications) | the slot of a recorded root; the ZkStake batch; the `SDP_DECLARE` gas; the TBD gas values and limit |
| 8 | Medium | [Genesis Block](#affected-specifications), [Genesis declarations](#7-genesis-declarations) | one spend with no inputs |
| 9 | Medium | [Wallet Technical Standard](#affected-specifications), [wallets](#8-wallets) | the `data` of every note; claims sent through other peers |
| 10 | Low | [Cryptarchia](#affected-specifications) | test vectors only |

# Discussion

## Where the vesting end lives

A vested note keeps its vesting end in `data`, a field every user note had at `0`. The ledger creates the note in the claim, so the end is public from the start, like the value and the key of every claim note. The ZkTransfer bounds the `data` of its inputs with one 64-bit comparison per input, and the Proof of Leadership and the Proof of Quota already read the `data` of a note. No note set, Operation or root history is added: each recent root only keeps the slot that recorded it.

The alternatives keep the circuits unchanged and pay elsewhere:

- **A note set of vested notes, with its commitment root recorded at the end of every epoch.** A proof against the root of epoch `e` shows that its notes were created by `e`. The ledger keeps a root history, a release Operation spends the notes after vesting, and wallets keep paths at old roots.
- **One note set per epoch.** A proof spends notes of one epoch only, and each set a transaction touches pays the 3,461 Execution Gas of a changed note set.
- **A public record of each vested note's end, the spend naming the note.** Every spend links to its claim, and the records take about 24 MB for the 600,000 claims the pool pays.

The vesting ends at the first slot of the epoch `VESTING_EPOCHS` = 49 epochs after the epoch of the block the claim references, so a note vests 360 to 367.5 days after that block. Every claim of an epoch then vests at the same slot. A spend right after it hides among the claims of a whole epoch, and a declaration can lock its stake until exactly the end of its latest note. All the vested notes of an epoch become spendable at once, so transfer demand can peak at the start of that epoch.

The vesting end counts from the block the claim references, not from the block including it. The claim's fee is paid by a Transfer spending the liquid note in the same transaction, and that Transfer is proven against a root extended with the transaction buffer, which holds the vested note. The miner therefore needs the vested commitment before it knows the including block, which can fall in the next epoch. The referenced block is at most `WINDOW` = 300 slots older.

## What a vested note can do before its end

Every ZkTransfer output has `data = 0`, so no Operation passes a vesting end on to a new note. Before its end, a vested note:

- leads in the lottery after the ageing every note has: a note created in epoch `e` leads from epoch `e + 2`;
- counts for the leader branch of the Proof of Quota;
- can be staked by `SDP_DECLARE`.

It cannot pay a fee, move to another key outside a declaration, or enter a channel. A Transfer and a channel deposit take `spending_slot` from the slot that recorded their referenced root. Each block appends its own leader note, so two forks share a ledger root only if one leader builds two blocks of the same content on one parent, and a proof against that root then holds on one fork only. Proofs over channel notes use `spending_slot = 0`: a channel root can be recorded again at another slot after a reorganization, and steps signed against it would fail.

The declarer names `locked_until`, and every note it stakes must have vested by the first slot of that epoch. Vesting ends at the start of an epoch, so the earliest valid epoch is the one at which the latest staked note vests. The stake returns 3 epochs after the withdrawal.

## Staking many notes

A miner holds one vested note per claim, and vested notes cannot be merged, so a declaration consumes them all at once. The reward therefore decides whether mining can fund a stake before its notes vest. This RFC assumes a fixed reward of 334 LOGOS per claim, paid from a pool of 200M LOGOS over two years, and a stake of up to 50,000 LOGOS. 150 claims then earn that stake, half of it on 150 vested notes, and a stake of vested notes alone takes 300. A separate draft stacked on this one sets that reward. At the reward [Reward Pool](../proof-of-work.md#reward-pool) computes on this branch, about 1.157 LOGOS, one declaration holds at most 2,189 LOGOS of vested notes. `SDP_DECLARE` uses a ZkStake circuit with 16 inputs and no output. Transfers keep the 4-input ZkTransfer: a Groth16 circuit costs its full size whatever inputs stay unused, so a 16-input ZkTransfer would make every transfer about 3× slower to prove.

Constraints were measured by compiling the transfer circuit of the circuits repository (branch `tl/private_utxo`) as `zkTransfer(k, 1, 40)`: 12,604 per input and 1,747 per output. That circuit predates the nullifier and staking keys, which add 480 per input: a compression of 240 for the nullifier key and 240 for one more element in the note commitment hash, both measured. The table drops the output, which a ZkStake does not have, and adds 64 per input for the vesting check, also measured. Proving times scale linearly from the ZkProgramSpend, 86,813 constraints in 2.6 s on one thread of the Mantle benchmark machine. Bytes and Execution Gas cover the spends of a declaration, at `EXECUTION_PROOF_GAS` per proof, and the fees use the starting storage price of 8·10⁵ LEPTA per byte. The last column fills `G_max`, at its last value of 3,173,691, with one declaration, its fee Transfer of one input and one output and the SDP note set it changes, 6,811 Execution Gas outside the spends. The one-byte spend count caps a declaration at 255 spends, which binds the 4- and 8-input rows.

| Inputs per proof | Constraints | One proof, 1 thread | Bytes per note | Gas per note | 150 notes: proofs, size, fee | Max notes per declaration |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 52,816 | 1.6 s | 66 | 1,169 | 38, 10.0 KB, 8.0 LOGOS | 1,020 |
| 8 | 105,408 | 3.2 s | 49 | 948 | 19, 7.4 KB, 5.9 LOGOS | 2,040 |
| 16 | 210,592 | 6.3 s | 41 | 837 | 10, 6.2 KB, 4.9 LOGOS | 3,783 |
| 32 | 420,960 | 12.6 s | 36 | 781 | 5, 5.5 KB, 4.4 LOGOS | 4,052 |
| 64 | 841,696 | 25.2 s | 34 | 754 | 3, 5.2 KB, 4.2 LOGOS | 4,201 |

The nullifier sets a floor of 32 bytes and 725 Execution Gas per note, so a block holds at most 4,372 staked notes. 16 inputs reach most of the saving. The proving work per note is about the same at every size.

Three other ways to stake many notes were dropped:

- **A proto-service note** accumulating vested notes before the declaration. With the vesting end in the note, it would be the output of a lock-preserving merge, below. Each top-up would also re-create the note, which then never ages into the lottery while it fills.
- **Lock-preserving merges**, whose outputs keep the vesting end of their inputs. They let locked tokens change hands. Restricting them to one key would force a miner to reuse its claim key, which links all its claims.
- **A top-up of an existing declaration.** Service rewards do not grow with stake above the minimum, and vested notes lead on their own.

## Linkability

Claims stay public. The ledger creates both notes, and their value, key, vesting end and commitment are known to everyone. A spend reveals nullifiers, never commitments, so it does not show which note it consumes.

- **A spend after vesting** adds nothing, since `spending_slot` is the slot of a public root. Its timing points at most at the epoch whose claims just vested, about 6,100 claims if the pool pays out evenly over its two years, and fewer in the first epochs.
- **A declaration** reveals its number of notes, the value of each spend and its lock epoch. The claim reward is fixed, so the value of a spend of vested notes only repeats their count. [Reward Pool](../proof-of-work.md#reward-pool) still recomputes the reward at every epoch boundary. While it does, the value reveals how many of the notes were claimed in each epoch, wherever that sum has one decomposition into the public claim values. If the declarer picks the earliest valid lock epoch, that epoch gives away the epoch its latest claim referenced, which holds about 6,100 such claims. Each other staked note hides among all vested notes claimed by then and not yet spent.
- **The Proof of Leadership and the Proof of Quota** reveal nothing new.
- **The strongest link is off chain:** a provider sending its claims from the node named in its locators. Wallets send them through other peers.

A commitment supplied by the miner, instead of one the ledger creates, would hide only the key of the vested note, a one-time key, since the value and the block are public through the claim.

## A locked stake can change hands

`SDP_DECLARE` creates the service note under the `note_pk` and `note_stake_pk` it names, which no proof covers. A seller can therefore stake its vested notes under a buyer's `note_pk`, `note_stake_pk`, `zk_id` and `provider_id`, in one transaction with a Transfer paying the seller. The buyer then holds the stake: it earns the lottery and service rewards, and withdraws the stake once the lock ends. This is accepted: the stake stays locked, serves only service provision and the lottery, and its value cannot move before its vesting ends.

Binding the stake to its staker is a separate draft stacked on this one. Miners derive their claim keys and the `note_pk` from one stake secret, and the ZkStake proves that every vested input and the `note_pk` come from it. Measured with the two-to-one compression of the circuits, it costs 4,848 constraints at 16 inputs, 2.3% of the ZkStake. Handing a secret over off chain stays possible, and no protocol can prevent it.

## A declaration that lapses

A declaration leaves the active set once its reports stop, and it cannot come back. An active message for an epoch needs a blending token collected as a member of the core list of that epoch, and the ledger rejects it from a provider outside the list. Two offline epochs are enough. The way back is to withdraw and declare again, and `locked_until` blocks the withdrawal. A provider that lapses therefore cannot serve with that stake until the lock ends, up to a year. Its service note can still lead in the lottery, and it can declare with other notes under new identifiers.

This is accepted as a cost of the lock. The activity proof is to change to something less probabilistic and more forgiving, which should make a lapse rarer.

## Era parameters

`POW_VESTED_SHARE` and `VESTING_EPOCHS` are era parameters. On this branch they are constants of Proof of Work, as `POW_SHARE` and `SHARE_DEN` are. The era parameter record is specified in Eras, which this branch does not have. Its two new fields, with the rule that a claim reads the values of the era of its including block, go into whichever of the two specifications lands second. A note keeps the end slot it was created with, so an era changing `VESTING_EPOCHS` moves no existing lock.

An era can also change the length of an epoch. The first slot of epoch `locked_until`, and that of the epoch at which a claim's vesting ends, then come from the epoch schedule of Eras rather than from a product with `EPOCH_LENGTH`, and this change goes in with the two fields.

## Gas still to measure

- The ZkStake proofs of a block form a batch of their own, whose fixed part is not yet measured. The fixed part of each batch is deducted from the Execution Gas limit of a block, so until it is measured the fixed costs of a block, the Execution Gas limit, `G_max` and `G_target` are TBD.
- The 28th public input of the ZkTransfer adds a term to the fixed part of its batch.
- A ZkStake proof is priced at `EXECUTION_PROOF_GAS`, since each proof of a batch adds two scalar multiplications and one pairing whatever its public inputs. A measurement should confirm it.
- `EXECUTION_CLAIM_POW_REWARD_GAS` is TBD. Its former 592 was measured on a claim creating one note, and the second note adds a nonce, a commitment and an append to the ledger note set.

## Compatibility

The chain has not launched, so no migration is needed. The ZkTransfer gets a new verification key, the ZkStake needs a setup of its own, and `SDPDeclare` and its proof get a new encoding.

## Open questions

- A provider whose stake is locked cannot change its locators: the Service Declaration Protocol has no update, and declaring again takes other notes and identifiers.
- The liquid part of a claim covers its fee 572 times at the starting storage price at the assumed reward, and only twice at 1.157 LOGOS.
- Every vested note leads on its own, so a miner evaluates one lottery ticket per note and slot. A miner with 1% of the claims holds about 3,000 vested notes after a year. Before their vesting ends, only a declaration merges them.

# Details

## 1. Vested notes and the vesting bound of a ZkTransfer

- The `data` of a user note is the slot its vesting ends, `0` if it does not vest. A user note with another `data` is a vested note, created only by `CLAIM_POW_REWARD`.
- The ZkTransfer takes each input's `data` as a witness and a new public input `spending_slot`. Every input satisfies `0 <= spending_slot - inputs_data[i] < 2**64`, and the prover sets the `data` of an inactive input to `0`. Outputs keep `data = 0`. The public signals are 28, `spending_slot` coming after `tx_commitment_root`.

```diff
 class ZkTransferPublic:
     # ... inputs, outputs, their flags and excess_value unchanged
     tx_commitment_root: MerkleRoot
+    spending_slot: Slot                 # every input has finished vesting by this slot
     msg: zkhash
```

- `verify_transfer` takes `spending_slot`, `0` by default. A Transfer and a channel deposit pass the slot that recorded their referenced root, `recent_commitment_roots[commitment_root].slot`. `SDP_WITHDRAW` passes `0`.
- `RecentRoot` gains `slot`, the slot of the block that recorded the root, `0` for the root of an empty set. `record_commitment_root` takes the slot, and Block Execution passes `block.header.slot`.

## 2. A claim pays a liquid and a vested note

`CLAIM_POW_REWARD` creates two notes under the claim's key, which is also their staking key, and adds both to the buffer of the ledger note set. A note of value `0` is not created.

```python
vested_value = checked_uint64(epoch_pow_reward * POW_VESTED_SHARE) // SHARE_DEN
liquid_value = checked_uint64(epoch_pow_reward - vested_value)
# liquid note: output number 0, data 0
# vested note: output number 1, data = (block.slot // EPOCH_LENGTH + VESTING_EPOCHS) * EPOCH_LENGTH,
#   the first slot of the epoch VESTING_EPOCHS after that of the referenced block
```

Proof of Work adds `POW_VESTED_SHARE = 50`, over the existing `SHARE_DEN = 100`, and `VESTING_EPOCHS = 49`. The liquid part, not the whole reward, must exceed the fee of a claim transaction, and `POW_VESTED_SHARE` must be at most `SHARE_DEN`.

## 3. Declarations stake through ZkStake, locked until an epoch

```diff
 class DeclarationMessage:
     # ... service_type, locators, provider_id, zk_id, note_pk, note_stake_pk unchanged
-    inputs: list[NoteNullifier]
     commitment_root: MerkleRoot
-    amount: TokenValue
+    locked_until: EpochNumber    # the first epoch at which the declaration can be withdrawn
+    spends: list[StakeSpend]     # 1 to 16 nullifiers each, with their total value
```

- Validation: the inputs of all spends are distinct and spendable against `commitment_root`, 1 to 16 per spend. The sum of the spend values is the stake, which meets the minimum stake. Each spend carries one ZkStake, verified with `spending_slot = locked_until * EPOCH_LENGTH`, the first slot of epoch `locked_until`.
- Execution consumes the inputs, creates the service note with the stake as its value, and stores `locked_until` in `DeclarationInfo`.
- `SDP_WITHDRAW` is invalid before epoch `locked_until`.
- Execution Gas: `EXECUTION_SDP_DECLARE_GAS + EXECUTION_SIGNATURE_GAS + EXECUTION_COMMITMENT_GAS + sum(spend_gas(spend.inputs, []) for spend in spends)`.

## 4. The ZkStake circuit

The ZkStake takes 16 inputs and no output. Its public values are the nullifiers and their flags, `excess_value`, the sum of the input values, `tx_commitment_root`, `spending_slot` and `msg`. Its inputs satisfy the input constraints of the ZkTransfer. `verify_stake` verifies it against the referenced root extended with the buffer, and the ZkStake proofs of a block are batch-verified in a batch of their own.

## 5. Vested notes lead

The Proof of Leadership and the leader branch of the Proof of Quota already read the `data` of a note, so a vested note leads like any other and neither circuit changes.

## 6. Encoding

```schema
SDPDeclare      = ServiceType Locators ProviderId ZkId NotePk CommitmentRoot LockedUntil StakeSpends
LockedUntil     = UINT32        ; EpochNumber
StakeSpends     = StakeSpendCount *StakeSpend
StakeSpendCount = Byte
StakeSpend      = Inputs Value  ; InputCount at most 16
SDPDeclareProof = *ZkStake Ed25519Signature ; one ZkStake per StakeSpend
ZkStake         = Groth16Proof
```

A decoder rejects a `StakeSpend` whose `InputCount` exceeds 16, and validation rejects a spend with no inputs.

## 7. Genesis declarations

A Genesis declaration carries one spend with no inputs, whose value is its stake. Genesis waives the lower bound of the inputs of a spend, and the placeholder proof of the declaration holds one `ZkStake`.

## 8. Wallets

A wallet keeps the `data` of each note it tracks. It should submit the claims of a service provider through peers other than the node named in the provider's locators.

## Chores

- Mantle's Programs section says the ZkTransfer derives commitments with `program` set to `0`, no longer `data` too.
- Mantle's Note Delivery notes that the `data` of a vested note is public.
- Block Construction verifies the ZkProgramSpend proofs in a batch of their own, no longer a "second" batch.
- The `SDP_DECLARE` test vector of Mantle carries two spends, and the test vectors of Cryptarchia, which hash the Mantle test transactions, follow it.

# Implementation

- [ ] Create the liquid and the vested note in `CLAIM_POW_REWARD`, the vested `data` the first slot of the epoch `VESTING_EPOCHS` after that of the referenced block.
- [ ] Record the slot of each recent commitment root, and pass it as `spending_slot` for Transfers and channel deposits, `0` elsewhere.
- [ ] Extend the ZkTransfer circuit (`mantle/transfer.circom` in logos-blockchain-circuits) with the `data` witness of each input, the `spending_slot` public input and its 64-bit comparison, and generate its new key.
- [ ] Implement the ZkStake circuit, its circuit-specific setup and its batch verification.
- [ ] Implement the spends and `locked_until` of `SDP_DECLARE`, `DeclarationInfo.locked_until` and the lock check of `SDP_WITHDRAW`.
- [ ] Update the encoding of `SDPDeclare` and its proof.
- [ ] Build each Genesis declaration with one spend with no inputs.
- [ ] Keep the `data` of every note in the wallet.
- [ ] Measure the ZkStake batch, the ZkTransfer batch with 28 public inputs and a claim creating two notes, and fill in the TBD values: the fixed costs of a block, the Execution Gas limit, `G_max`, `G_target` and `EXECUTION_CLAIM_POW_REWARD_GAS`.
- [ ] Add `POW_VESTED_SHARE` and `VESTING_EPOCHS` to the era parameter record once Eras and this change are on one branch.
- [ ] Add tests and test vectors: the two claim notes, `spending_slot` at, before and after a vesting end, a ZkStake of 1 and 16 inputs, a withdrawal before and at `locked_until`, the new encoding.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | Revision 2.4.0 |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | Revision 1.11.0 |
| [Proof of Work](../proof-of-work.md) | Modified | Revision 1.3.0 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | Revision 1.2.3 |
| [Proof of Quota](../proof-of-quota.md) | Modified | Revision 1.3.2 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | Revision 2.2.0 |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | Revision 1.4.3 |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | Revision 2.1.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | Revision 1.3.2 |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | Revision 1.4.0 |
| [Cryptarchia](../cryptarchia-v1-protocol.md) | Modified | Revision 1.3.2 |
| [Execution Market](../execution-market.md) | Modified | Revision 1.3.3 |
| [Cryptoeconomics](../overview-cryptoeconomics.md) | Modified | Revision 1.5.3 |
