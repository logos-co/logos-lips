# [RFC] Mantle: Programs governing channel notes

**Motivation and proposal:** [PR #481](https://github.com/logos-co/logos-lips/pull/481)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-12 |

## Reviewer Orientation

Read [RFC-480](RFC-480-mantle-private-utxo-ledger.md) first: this RFC builds on its note sets, channel steps and commitment buffer.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [program notes](#1-program-notes) | the `program` and `data` fields of the note; the ZkTransfer and the Proof of Leadership fixing both to `0` |
| 2 | Critical | **Start here**: [Mantle](#affected-specifications), [program steps](#2-program-steps) | payments, the `ZkProgramSpend`, the program proof and its three public inputs; nothing creates value |
| 3 | High | [Mantle](#affected-specifications), [what enforces what](#3-what-enforces-what) | the split between what the ledger enforces and what the users of the zone check |
| 4 | High | [Mantle](#affected-specifications), [registration](#4-program-registration) | `PROGRAM_REGISTER`, the program identifier, the key checks |
| 5 | High | [Encoding](#affected-specifications), [encoding](#5-encoding) | step kinds, payments, program step proofs, the verification key |
| 6 | Medium | [Proof of Leadership](#affected-specifications), [gas](#6-gas) | the commitment with `0` fields; the measured gas constants and block limit |
| 7 | Low | [Block Construction](#affected-specifications), [cross-channel template](#affected-specifications) | skim: renames |

# Discussion

## What the ledger guarantees

The ledger guarantees that no LGO is created, that a user note moves only with the key of its holder, and that a program note moves only with the proof of its program. It does not check the assets of a zone. For a swap of LGO against a zone token, the users of the zone verify the inscription against the intents, and the sequencers of the zone slash a faulty sequencer. Mantle states this split in its [What enforces what](../bedrock-v1.1-mantle-specification.md#programs) table.

## Privacy

Users stay hidden: payments consume notes by nullifier, and the notes a program pays are commitments. The amounts are public: every payment carries its `paid_value`, and a public program such as a pool publishes its state. Interactions with a public program are therefore subject to timing attacks. Hiding the amounts needs value commitments in place of public values, which changes the ZkTransfer and the fee payment across Mantle and is left to a later RFC.

## Alternatives considered

- **A signed delta per program spend, summed to zero over the inscription.** Value would move between proofs through signed amounts. Rejected: every proof balances on its own with unsigned values, which is simpler to check and to implement.
- **Order notes created by the users.** A user would create a program note holding the payment and its intent, and the sequencer would consume it later. Rejected: creating a program note needs the program proof, which is bound to an inscription the user does not know when signing. Unfilled orders would also need a refund rule.
- **Payment notes under the key of secret key `0`.** A user would pay the program with a plain note anyone can spend, consumed by the program step of the same inscription. Rejected: if the sequencer published the payment without the program step, anyone could take the note. A payment that lives inside its program step cannot be stranded.
- **Routing the excess of user steps to a program, with a per-program sum.** Rejected: the payment moves into the program step, so the ledger needs no routing field, and user steps keep an `excess_value` of `0`, which saves space in every inscription.
- **A custom inscription hash, or a per-step flag choosing whether a proof is bound to the inscription.** Rejected: the `op_id` of the Inscribe Operation already covers the inscription and the public data of every step without any proof, and every program proof is bound to it. No circuit has to open the inscription: LGO-only programs read `payments_hash` and `spend_notes_hash`, and the users of the zone check the rest.
- **One zkVM verifier for every program.** Rejected for now: a Groth16 key per program reuses the stack of the ZkTransfer, on BN254 with `zkhash`, and a zone can still wrap a zkVM proof in a Groth16 circuit.
- **Folding `program` and `data` into `public_key`.** Rejected: separate fields keep the commitment of a user note readable as such, and let the ZkTransfer and the Proof of Leadership fix them to `0` without a branch.
- **A registry per channel.** Rejected: a program only governs its own notes, so a global, permissionless registry is safe, and the sequencer, who often controls the channel configuration, gains no gatekeeping power.

# Details

## 1. Program notes

`Note` gains two fields, part of its commitment. They default to `0`, the value of a user note.

```diff
 class Note:
     value: TokenValue
     nonce: NoteNonce
     public_key: ZkPublicKey
+    program: ProgramId = 0  # the program governing the note, 0 for a user note
+    data: zkhash = 0        # the state the program commits in the note, 0 for a user note
```

```diff
 def derive_note_cm(note: Note) -> NoteCm:
     return zkhash(FiniteField(b"NOTE_CM_V1", ...), FiniteField(note.value, ...),
-                  note.nonce, note.public_key)
+                  note.nonce, note.public_key, note.program, note.data)
```

- The ZkTransfer derives the commitments of its inputs and outputs with `program` and `data` set to `0`, so it moves user notes only.
- The Proof of Leadership derives the commitment of its note the same way, so program notes do not lead.
- The nullifier is `zkhash(NOTE_NF_V1, cm, sk)` for every note. A program note has a holder chosen by its program. The key of secret key `0` is the convention for a note open to everyone, such as the reserves of a pool.

## 2. Program steps

`CHANNEL_INSCRIBE` carries `steps: list[UserStep | ProgramStep]`.

- A **user step** is a ZkTransfer of its holder bound to `step_msg`, with an `excess_value` of `0`.
- A **program step** carries a `program_id`, its `payments`, and a program spend over the program notes.

```python
class Payment:
    inputs: list[NoteNf]
    outputs: list[NoteCm]       # change
    cm_merkle_root: MerkleRoot
    paid_value: TokenValue      # the excess of the ZkTransfer, paid to the program
    intent: zkhash

class ProgramStep:
    program_id: ProgramId
    payments: list[Payment]
    inputs: list[NoteNf]        # notes of the program, possibly none
    outputs: list[NoteCm]       # notes of the program, and user notes it pays
    cm_merkle_root: MerkleRoot
    spend_notes_hash: zkhash
```

Validation of a program step, in order:

1. The program is registered.
2. Each payment is spendable, and its ZkTransfer verifies with `payment_msg(program_id, payment)` and an excess of `paid_value`. Its change goes to the buffer.
3. The program spend consumes unspent notes of the program, possibly none, and its `ZkProgramSpend` verifies with `paid_value` the sum of the payments, `spend_notes_hash`, and the `op_id` of the inscription.
4. The program proof verifies under the registered key on `(spend_notes_hash, payments_hash(step), op_id)`.

The `ZkProgramSpend` is the ZkTransfer with program checks: its inputs are notes of `program_id`, its outputs are notes of `program_id` or user notes, `spend_notes_hash` commits to the active flag and the note of every input and output, nonce included, so that a program can constrain the nonces its sequencer picks, and `sum(inputs_value) + paid_value == sum(outputs_value)`. Its used inputs and outputs are marked by the public flags `inputs_active` and `outputs_active`, set from the published lists as in the ZkTransfer. It is proven by the sequencer. The circuit (`program_spend` in [logos-blockchain-circuits](https://github.com/logos-blockchain/logos-blockchain-circuits)) has 69,361 constraints and proves in about 2.1 s on one thread and 0.3 s on 32 threads (see the Mantle benchmark).

## 3. What enforces what

Mantle gains a **Programs** section stating, for each guarantee, the check that enforces it, and the design choices behind them: why creating a program note needs its proof, why a payment lives inside its program step, why the proofs are bound to the `op_id`, why program notes neither stake nor withdraw. Publishing the preimage of each intent in the inscription is recommended, depending on the program.

## 4. Program registration

`PROGRAM_REGISTER`, opcode `0x01`, carries a `Groth16VerificationKey` with exactly four `ic` points, one per public input plus one. Its proof is empty.

```python
def derive_program_id(key: Groth16VerificationKey) -> ProgramId:
    h = Hasher()
    h.update(b"PROGRAM_ID_V1")
    h.update(encode(key))
    return FiniteField(h.digest(), byte_order="little", modulus= p)
```

- Validation checks that every point is on its curve, in its prime-order subgroup and not the point at infinity.
- Execution prepares the key once, computing `e(α, β)` and the line coefficients of `-γ` and `-δ`, and stores the prepared key in `ledger.programs` under its identifier. Registering a key already registered has no effect.

## 5. Encoding

```diff
-Steps           = StepCount *ChannelStep
-ChannelStep     = Inputs Outputs CmMerkleRoot
+Steps           = StepCount *Step
+Step            = (UserStepKind UserStep) / (ProgramStepKind ProgramStep)
+UserStep        = Inputs Outputs CmMerkleRoot
+ProgramStep     = ProgramId Payments Inputs Outputs CmMerkleRoot SpendNotesHash
+Payment         = Inputs Outputs CmMerkleRoot Value Intent
+ProgramRegister = Groth16VerificationKey   ; Alpha G1, Beta Gamma Delta G2, 4 IC G1: 352 bytes
-ChannelInscribeOpProof = Ed25519Signature *ZkTransfer
+ChannelInscribeOpProof = Ed25519Signature *StepProof
+ProgramStepProof       = *ZkTransfer ZkProgramSpend Groth16Proof
```

## 6. Gas

A program step costs `EXECUTION_TRANSFER_GAS` per payment, plus `EXECUTION_PROGRAM_SPEND_GAS` and `EXECUTION_PROGRAM_PROOF_GAS`. `PROGRAM_REGISTER` costs `EXECUTION_PROGRAM_REGISTER_GAS`. The values come from measurements of the node's Groth16 verifiers, 1 Execution Gas per 1,000 CPU cycles:

- `EXECUTION_PROGRAM_SPEND_GAS = 619`: the ZkProgramSpend proofs of a block (29 public inputs) are verified in one batch, `3,608,664 + n * 618,796` cycles. Its fixed part is deduced from the block limit with the ZkTransfer one, so `limit_Ex = G_max = 3,192,850` and `G_target = 1,596,425`.
- `EXECUTION_PROGRAM_PROOF_GAS = 2222`: the program proof is verified alone, since it cannot share the batch of another program, by the single proof verifier on the prepared key of the program, 2,221,544 cycles at 3 public inputs.
- `EXECUTION_PROGRAM_REGISTER_GAS = 2278`: the subgroup checks of the 3 G2 points of the key, 573,324 cycles, and the preparation of the key, 1,704,632 cycles. Point decompression is the same for every key and proof and is not counted. Preparing the key at every verification instead would raise each program proof to 4,062,923 cycles.

## Chores

- The `Groth16` terminal of the encoding is renamed `Groth16Proof`, and Block Construction follows.
- The cross-channel messaging template builds its swap from `UserStep`s.

# Implementation

- [ ] Add the `program` and `data` fields to notes and to their commitment, with `0` for user notes.
- [ ] Fix `program` and `data` to `0` in the ZkTransfer and the Proof of Leadership circuits.
- [ ] Implement the `ZkProgramSpend` circuit, its setup and its verifier.
- [ ] Implement `PROGRAM_REGISTER`: the key encoding, the curve and subgroup checks, the program identifier and the `programs` map.
- [ ] Implement user and program steps in `CHANNEL_INSCRIBE`: payments, the program spend, the program proof under its registered key, and their encoding.
- [x] Measure the Execution Gas of `PROGRAM_REGISTER`, the `ZkProgramSpend` and the program proof.
- [ ] Add tests and test vectors for note commitments, program registration, program steps and their encoding.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | 2.1.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | 2.1.0 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.2.1 |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | 1.4.1, terminal rename, ZkProgramSpend batch |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 1.9.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | 1.4.1, Execution Gas limit |
| [Execution Market](../execution-market.md) | Modified | 1.3.1, `G_max` and `G_target` |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | test vectors with `PROGRAM_REGISTER` and program steps |
| [Cross-Channel Messaging Template](../template-cross-channel-messaging.md) | Modified | 1.3.1 |
