# [RFC] Mantle: Programs governing channel notes

**Motivation and proposal:** [PR #481](https://github.com/logos-co/logos-lips/pull/481)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-12 |
| v2 | The users of a zone alone check how a program step serves the intents over its assets. Payments follow the mini-blocks of user steps through their `buffered`, and the Execution Gas of an inscription sums the cost of each of its program steps | 2026-10-16 |
| v3 | The ZkProgramSpend derives the output nonces of a step consuming a note of the program, and `spend_notes_hash` reads inactive fields as `0`. Every node holds an opening until its block is immutable, the sequencers of a channel after that. The freeze by sequencers, the holding of a payment, unauthenticated intents and the trust in the setup of a key are stated. The format of compressed points is defined, the point at infinity having no encoding. A step opens the program notes it creates, and program steps and `PROGRAM_REGISTER` are priced from measurements | 2026-11-03 |
| v4 | User steps and payments are grouped in the mini-blocks of an inscription, each proven against the buffer before its mini-block, and a program spend covers the whole buffer at its position. The test vectors follow the node, the `CHANNEL_CONFIG` vector taking a threshold its two keys can reach | 2026-11-04 |
| v5 | The message of a payment holds the channel ID as two elements, its low and high 16 bytes, so that no two channels share a message. The root a step or a payment references is named `commitment_root`, the commitment and nullifier names are written in full, and each notation is explained where it first appears. The commitment of the leader reward note is derived with `program` and `data` set to `0`, so a reward is a user note | 2026-11-04 |
| v6 | A nullifier key sits between the spending secret key and the public key, and derives the nullifier. A note has a staking key, `stake_public_key`, the public key by default, and program notes lead in Proof of Stake unless their program fixes their staking key to `0`. Payments and program steps carry their own inscription | 2026-11-06 |
| v7 | A declaration names `note_stake_pk`, the staking key of its service note, and the service rewards go to `note_pk` and `note_stake_pk` | 2026-11-06 |
| v8 | A mini-block is a flat list of user steps, program deposits and program steps, the kind of a step carried only by its encoding. A program step consumes the deposits of its program before it in its mini-block, and a deposit left unconsumed makes the inscription invalid. `payment_msg`, `spend_notes_hash` and `payments_hash` are renamed `program_deposit_id`, `program_step_id` and `program_deposits_hash` | 2026-11-06 |
| v9 | A deposit checks that its program is registered, and a program step takes its deposits in their order in the mini-block. `program_step_id` hashes under the DST `PROGRAM_STEP_ID_V1` | 2026-11-06 |
| v10 | The amount of a deposit is its `value`, `paid_value` naming the sum of the values of the deposits of a program step, a public input of its ZkProgramSpend | 2026-11-06 |
| v11 | A program step consumes the program deposits after the previous program step of its mini-block, which must all pay its program, from one pending list. `program_deposit_id` is a BLAKE2b hash of the channel and the encoded program deposit, reduced modulo `p`. A program step lists its `program_outputs`, the notes of its program, apart from its `outputs`, the user notes it pays, which sets the `outputs_of_program` flags. Every program note is held by `PK0`, the public key of the spending secret key `0`, so the ZkProgramSpend takes no spending secret key and an opening no public key. A channel being created carries no step. The nullifier key derives under `NF_KDF_V1`, the encoding names the staking key `NoteStakePk` everywhere, and the nonce of a service reward note derives over its `note_pk` | 2026-11-06 |

## Reviewer Orientation

Read [RFC-480](RFC-480-mantle-private-utxo-ledger.md) first: this RFC builds on its note sets, channel steps and commitment buffer.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [program notes](#1-program-notes) | the `stake_public_key`, `program` and `data` fields of the note; the nullifier key between the spending secret key and the public key; the ZkTransfer fixing `program` and `data` to `0`; the Proof of Leadership proving a user or program note from its nullifier key and staking secret key |
| 2 | Critical | **Start here**: [Mantle](#affected-specifications), [program steps](#2-program-steps) | program deposits and the program step consuming them in the mini-block, the `ZkProgramSpend` with its `program_outputs` held by `PK0` and its `outputs_of_program` flags, its derivation of the output nonces and the flags in `program_step_id`, the program proof and its three public inputs, the openings of the program notes; nothing creates value, and no program note is created without its opening |
| 3 | High | [Mantle](#affected-specifications), [what enforces what](#3-what-enforces-what) | the split between what the ledger enforces and what the users of the zone check |
| 4 | High | [Mantle](#affected-specifications), [registration](#4-program-registration) | `PROGRAM_REGISTER`, the program identifier, the key checks |
| 5 | High | [Encoding](#affected-specifications), [encoding](#5-encoding) | step kinds, program deposits, the inscriptions of the steps, `ProgramOutputs`, program step proofs with their `ProgramNoteOpening`s, the verification key, the format of compressed points |
| 6 | Medium | [Proof of Leadership](#affected-specifications), [Proof of Quota](#affected-specifications), [gas](#6-gas) | the public key and the nullifier proven from the nullifier key; the ticket, the entropy contribution and the key nullifier derived from the staking secret key; the measured gas constants and block limit |
| 7 | Medium | [Block Construction](#affected-specifications) | terminal rename, ZkProgramSpend batch, copies lacking or altering openings |

# Discussion

## What the ledger guarantees

The ledger guarantees that no LOGOS is created, that a user note moves only with the key of its holder, and that a program note moves only with the proof of its program. It also checks the opening of every program note a step creates, so that every node holds it until the block creating the note is immutable. It does not check the assets of a zone. For a swap of LOGOS against a zone token, the users of the zone can detect a step that does not serve an intent, but the LOGOS it moved stays moved, so a payer relies on the sequencer for the zone side. Mantle states this split in its [What enforces what](../bedrock-v1.1-mantle-specification.md#programs) table.

The ledger does not guarantee the liveness of a program:

- The sequencers of a channel can freeze every program note of the channel for good, since program notes are never withdrawn and only the sequencers publish program steps. They cannot take the value of the notes, but they can hold it.
- A sequencer can hold a signed program deposit until `ROOT_WINDOW` blocks, about 8.5 hours, after its root stopped being the current root of the note set, a root that stays current staying valid, and fill it at the worst price its intent accepts.
- Past the immutable block, the sequencers of a channel should keep the openings of its unspent notes. The next sequencer can take over a program from the openings alone as long as its state is in opened fields.
- The circuit fixes the total a step pays, not the value of each payout, so a program should fix that value from public data for its payee to recompute the note.

The users of a program trust its circuit and the setup that produced its key: whoever kept the trapdoor of that setup can prove any statement under the key.

## Program notes in Proof of Stake

The keys of a note form two chains. The spending secret key derives the nullifier key `nf_sk = zkhash(NF_KDF_V1, spending_sk)`, which derives the public key `pk = zkhash(KDF, nf_sk)` and the nullifier `zkhash(NOTE_NF_V1, commitment, nf_sk)`. The staking secret key derives the staking key `stake_pk = zkhash(KDF, staking_sk)`, a field of the note. A wallet uses `nf_sk` as `staking_sk` by default, so `stake_pk = pk`, and a transfer output takes the public key of its recipient as staking key unless the recipient asks for another. A Genesis note, the note of a proof of work claim and the leader reward note take their one public key as both. A declaration names two keys for its service note, `note_pk` and `note_stake_pk`, and the service rewards of the validator go to the same two keys, so both can stay in a cold wallet: the node keeps online only the secret of its `zk_id`, its Proof of Quota identity which holds no funds, its `provider_id` key and, to lead, the `nf_sk` and `staking_sk` of the service note.

The Proof of Leadership proves `pk` from `nf_sk`, which ties the nullifier it shows unspent to the note: with any other nullifier, the non-membership check would pass for a spent note. It never takes `spending_sk`, which is why the nullifier key sits between the spending secret key and the public key: a node handed `nf_sk` alone leads with the note but cannot spend it, cold staking, and sees when the note is spent. The ZkTransfer pays one more hash per input for it. The staking secret key derives the lottery ticket, the entropy contribution and the key nullifier of the Proof of Quota, so the lottery of a note stays private when its `nf_sk` is public.

Program notes take part in Proof of Stake by default. The LOGOS a program keeps in notes its steps do not move stakes, since only a note left unspent across the freeze of the stake distribution leads, and a program can offer liquid staking: every program note is held by `PK0`, the public key of the spending secret key `0`, so its `nf_sk` and `pk` are public and any sequencer can move it under the program proof, while its staking key is the one of its operator. A program should never give a note of the program the staking key `PK0`, since `NF_SK0` is public and anyone could lead with it. A program opts out by constraining the staking key of its notes to `0` in its proof: no secret key is known whose public key is `0`, so such a note never leads.

The reward of a block led by a program note goes, as for any leader, to the key its staker chooses, not to the program: the ledger cannot make the reward a program note, since only the proof of a program creates its notes. A program that does not constrain the staking key of the notes it creates, its own notes and its payouts, lets the sequencer proving the step choose it, so that sequencer can stake the notes of the program and keep their rewards, their value staying governed by the program. A payee needs the staking key of its payout to spend it, and a payout has no published opening, so a program should fix that key, for example to the public key of the payee. Program notes are never withdrawn, since a withdrawal consumes notes with a ZkTransfer.

## Program notes held by `PK0`

Every program note is held by `PK0 = zkhash(KDF, NF_SK0)`, `NF_SK0 = zkhash(NF_KDF_V1, 0)` being the nullifier key of the spending secret key `0`. A program note moves only with the proof of its program, so a holder of its own protects nothing, and a holder left to the sequencer would let it create notes of the program under its own key, which no other sequencer could spend. With a fixed holder, the ZkProgramSpend takes no spending secret key and an opening no public key. Anyone can compute the nullifiers of the program notes, so which program notes a step consumes is public, as the state of a program already is. A program that wants only some sequencers to move its notes enforces it in its circuit, for example with a signature over the `op_id`.

## Program deposits as steps

A mini-block is a flat list of steps of three kinds: user steps, program deposits and program steps. A program step consumes the program deposits after the previous program step of its mini-block, in their order in the mini-block, which the sequencer chooses, and they must all pay its program; a sequencer usually places them right before it. The ledger keeps one list of pending program deposits, which a program step empties, and an inscription leaving a program deposit pending at the end of a mini-block is invalid, so a program deposit exists only together with the program step that consumes it. The encoding tags each step with its kind, so a step is decoded once, by its tag.

A deposit carries its own inscription, the zone message of its holder, bound by `program_deposit_id` as a user step binds its own through `user_step_id`, and a program step carries the zone message of the step, bound by the `op_id` like the rest of its public data. The inscription of the inscribe and those of its steps count together against `MAX_OPERATION_DATA_SIZE`. The `program_step_id` of a program step hashes private fields of the notes of its program spend, so the ledger cannot recompute it: it is the public value linking the ZkProgramSpend and the program proof.

## Privacy

Users stay hidden: program deposits consume notes by nullifier, and the notes a program pays are commitments, as long as each payee uses a one-time public key, since the nonce of such a note is a public function of its value and public key. Which program notes a step consumes is public, every program note being held by `PK0`. The amounts are public: every deposit carries its `value`, and every program note is opened in the step that creates it, so the state of a program is public, and so is the total a program step pays to users. Interactions with a program are therefore subject to timing attacks. Hiding the amounts needs value commitments in place of public values, which changes the ZkTransfer and the fee payment across Mantle and is left to a later RFC.

## Alternatives considered

- **A signed delta per program spend, summed to zero over the inscription.** Value would move between proofs through signed amounts. Rejected: every proof balances on its own with unsigned values, which is simpler to check and to implement.
- **Order notes created by the users.** A user would create a program note holding the deposit and its intent, and the sequencer would consume it later. Rejected: creating a program note needs the program proof, which is bound to an inscription the user does not know when signing. Unfilled orders would also need a refund rule.
- **Deposit notes under the key of spending secret key `0`.** A user would pay the program with a plain note anyone can spend, consumed by the program step of the same inscription. Rejected: if the sequencer published the deposit without the program step, anyone could take the note. A deposit that exists only together with its program step cannot be stranded.
- **Deposits nested inside their program step.** Rejected: a flat list of steps of three kinds keeps one loop, one proof per step and one encoding tag per step, and the rule that a program step consumes the program deposits after the previous program step of its mini-block keeps a program deposit from being stranded just as well.
- **A holder chosen by the program for each program note.** Rejected: a program note moves only with the proof of its program, and a program leaving the holder free would let a sequencer create notes of the program that no other sequencer can spend. Every program note is held by `PK0`.
- **Letting a user step pay a program with its excess.** Rejected: a user step would need a program field and a nonzero `excess_value`. Only deposits carry a `program_id` and an excess, so a user step keeps an `excess_value` of `0` and names no program, which saves space in every inscription.
- **A custom inscription hash, or a per-step flag choosing whether a proof is bound to the inscription.** Rejected: the `op_id` of the Inscribe Operation already covers the inscription and the public data of every step without any proof, and every program proof is bound to it. No circuit has to open the inscription: LOGOS-only programs read `program_deposits_hash` and `program_step_id`, and the users of the zone check the rest.
- **One zkVM verifier for every program.** Rejected for now: a Groth16 key per program reuses the stack of the ZkTransfer, on BN254 with `zkhash`, and a zone can still wrap a zkVM proof in a Groth16 circuit.
- **Folding `program` and `data` into `public_key`.** Rejected: separate fields keep the commitment of a user note readable as such, and let the ZkTransfer fix them to `0` without a branch.
- **Program notes outside Proof of Stake.** Rejected: the LOGOS held by programs would leave the staking set, and no program could offer liquid staking. A program that wants its notes out of Proof of Stake fixes their staking key to `0`.
- **Paying the reward of a block led by a program note to the program.** Rejected: only the proof of a program creates its notes, so the ledger cannot create the reward as a note of the program. The reward goes to the key the staker chooses, as for any leader.
- **Openings of program notes left to the sequencer, in the inscription or off-chain.** Rejected: the ledger cannot see whether they were published, and a sequencer withholding the opening of a program note freezes it, since program notes are never withdrawn and no sequencer can prove a program spend over a note it cannot open. The safety of a program would hold, but not its liveness.
- **The state of a program stored on chain next to its key, as a public balance and state.** Rejected: program notes stay in the note set of their channel, in the same model as user notes, a program can hold many records as many notes, and the ledger needs no storage for program state nor a price for it.
- **A registry per channel.** Rejected: a program only governs its own notes, so a global, permissionless registry is safe, and the sequencer, who often controls the channel configuration, gains no gatekeeping power.
- **A program step anyone can post after a delay, as an exit from a freeze.** Left to a later RFC: it needs a new Operation and pending state, and a live sequencer cancels it by moving the note it consumes, so it only covers sequencers that stop altogether, not sequencers that censor.
- **Nonces left to the sequencer, with a recommended derivation or a rule for programs.** Rejected: a sequencer could burn a note by re-creating it, or withhold a payout, from any program that does not constrain them, and the program proof cannot see the channel or the parent. The nullifier of the first input takes the role the `op_id` has for the notes the ledger creates, without a new public input, so the batch verification of the ZkProgramSpend keeps its price.
- **Binding the proofs of a step to its channel, parent and position instead of the `op_id`.** Rejected: a dropped step would no longer force the earlier program steps of its inscription to be proven again, but the later ones still cover the buffer, and the `parent` of every chained inscription still changes.
- **An expiry on deposits.** Left out: it adds a field to every deposit, and a holder bounds its risk with the worst price its intent accepts.
- **A public payer key on deposits.** Rejected: it would link all the deposits of a user to a program. A program authorizes its users inside its circuit.
- **Rejecting a key with `γ = ±δ`, two of its points, at registration.** Rejected: a key with `δ = s·γ` and a known `s` is as forgeable and cannot be detected, so users have to verify the setup of a key whatever the ledger checks.

# Details

## 1. Program notes

`Note` gains three fields, part of its commitment. `stake_public_key` is the staking key of the note. `program` and `data` default to `0`, the value of a user note. A `ProgramId` is the identifier of a program (§4).

```python
nf_sk = zkhash(FiniteField(b"NF_KDF_V1", ...), spending_sk)  # the nullifier key, compression mode
public_key = zkhash(FiniteField(b"KDF", ...), nf_sk)
stake_public_key = zkhash(FiniteField(b"KDF", ...), staking_sk)
nullifier = zkhash(FiniteField(b"NOTE_NF_V1", ...), commitment, nf_sk)
NF_SK0 = zkhash(FiniteField(b"NF_KDF_V1", ...), 0)  # the keys of the spending secret key 0,
PK0 = zkhash(FiniteField(b"KDF", ...), NF_SK0)      # which hold every program note
```

```diff
 class Note:
     value: TokenValue
     nonce: NoteNonce
     public_key: ZkPublicKey
+    stake_public_key: ZkPublicKey  # the staking key of the note
+    program: ProgramId = 0  # the program governing the note, 0 for a user note
+    data: zkhash = 0        # the state the program commits in the note, 0 for a user note
```

```diff
 def derive_note_commitment(note: Note) -> NoteCommitment:
     return zkhash(FiniteField(b"NOTE_CM_V1", ...), FiniteField(note.value, ...),
-                  note.nonce, note.public_key)
+                  note.nonce, note.public_key, note.stake_public_key, note.program, note.data)
```

- The ZkTransfer proves `spending_sk`, derives `nf_sk`, then the public key and the nullifier of each input, and the ZkProgramSpend uses the constants `PK0` and `NF_SK0` for the notes of the program. Both derive the commitments of their inputs and outputs with their staking keys as private witnesses, the ZkTransfer with `program` and `data` set to `0`, so it moves user notes only. They do not prove the staking key: spending a user note takes its spending secret key alone, and a program note the proof of its program.
- The Proof of Leadership takes `nf_sk`, `staking_sk`, the `program` and the `data` of its note as private witnesses, derives the public key and the nullifier from `nf_sk` and the staking key from `staking_sk`, and derives the lottery ticket and the entropy contribution from `staking_sk`, so program notes lead. It never takes `spending_sk`. A note whose staking key is `0` never leads. The leader reward note is `(reward_value, reward_nonce, reward_public_key, reward_public_key, 0, 0)`, so a reward is a user note under one key. The leader branch of the Proof of Quota does the same, and derives its key nullifier from `staking_sk`.
- `DeclarationMessage` and `DeclarationInfo` gain `note_stake_pk`, `DeclarationInfo` keeps `note_pk` too, and the service note and the service reward notes are created under `note_pk` and `note_stake_pk`, the nonce of a reward note derived over its `note_pk` as for every note the ledger creates. A Genesis note takes its public key as both keys, and the note of a `CLAIM_POW_REWARD` the public key of the claim. A program should fix the staking key of the notes it pays, which their payee needs to spend them. A wallet should use `nf_sk` as the staking secret key of its notes, and give a transfer output the public key of its recipient as staking key unless the recipient asks for another.
- The nullifier is `zkhash(NOTE_NF_V1, commitment, nf_sk)` for every note. Every program note is held by `PK0`, so its nullifier uses `NF_SK0` and is public, and has a staker chosen by its program, or by the sequencer proving the step where the program leaves it free.
- Common Cryptographic Components lists the `NF_KDF_V1` derivation among the uses of the compression mode, and the Wallet Technical Standard derives the nullifier key and the public key from the wallet's `ZkSecretKey`.

## 2. Program steps

`CHANNEL_INSCRIBE` carries `mini_blocks: list[list[UserStep | ProgramDeposit | ProgramStep]]`, a flat list of steps per mini-block, the kind of a step being the tag of its encoding.

- A **user step** is a ZkTransfer of its holder bound to `user_step_id`, which commits to its channel and the whole step, its inscription included, with an `excess_value` of `0`.
- A **program deposit** is a ZkTransfer of its holder bound to `program_deposit_id`, which commits to its channel and the whole program deposit, its inscription, its program and its intent included, with an `excess_value` of its `value`. Like a user step, it is verified against its referenced root extended with the buffer as it stands when its mini-block starts, and holds at any position in its mini-block, so a sequencer can gather the program deposits of many users without the users proving one after another.
- A **program step** carries a `program_id` and a program spend over the program notes, and consumes the program deposits after the previous program step of its mini-block, in their order in the mini-block, which must all pay its program. A program deposit left pending at the end of its mini-block makes the inscription invalid.
- The program spend is proven by the sequencer once the inscription is fixed, and covers the whole buffer at its position. Program steps moving one pool can therefore follow each other in a single mini-block, each consuming the note the previous one created.

```python
class ProgramDeposit:
    program_id: ProgramId          # the program the program deposit pays
    inputs: list[NoteNullifier]    # nullifiers of the consumed user notes
    outputs: list[NoteCommitment]  # change
    commitment_root: MerkleRoot    # a recent root of the channel note set
    value: TokenValue              # the excess of the ZkTransfer, paid to the program
    intent: zkhash                 # the hash of what the user expects from the program
    inscription: bytes             # the zone message of the program deposit, signed by its holder

class ProgramStep:
    program_id: ProgramId                  # the program the step executes
    inputs: list[NoteNullifier]            # notes of the program, possibly none
    program_outputs: list[NoteCommitment]  # notes of the program the step creates
    outputs: list[NoteCommitment]          # user notes the step pays
    commitment_root: MerkleRoot            # a recent root of the channel note set
    program_step_id: zkhash                # the hash of the input and output notes of the program spend
    inscription: bytes                     # the zone message of the step, bound by the op_id

class ProgramStepProof:
    spend_proof: ZkProgramSpend       # the proof of the program spend
    program_proof: Groth16Proof       # under the registered key of the program
    program_notes: list[ProgramNoteOpening]  # (value, nonce, stake_public_key, data)
                                             # of each of the program_outputs
```

Validation, in one loop over the mini-blocks and their steps, each step first checked for unspent inputs, which no earlier step consumes, a program step possibly consuming none:

1. A program deposit names a registered program, and its ZkTransfer verifies with an excess of its `value` and `program_deposit_id(channel, program_deposit)`, the BLAKE2b-256 hash under the domain separation tag (DST) `PROGRAM_DEPOSIT_V1` of the channel ID and of the encoded program deposit, reduced modulo `p`, as `user_step_id` is under `USER_STEP_V1`. Each identifier keeps its own DST, as every hash of Mantle does, although the kind tag of the encoding already tells the steps apart. Its change goes to the buffer, and the program deposit is pending until the next program step.
2. A program step names a registered program, which every pending program deposit pays, and consumes them all.
3. The program spend consumes notes of the program, possibly none, at most 4 notes in and 8 out, and its `ZkProgramSpend` verifies with `paid_value` the sum of the values of those program deposits, `program_outputs` then `outputs` as its outputs, `program_step_id`, and the `op_id` of the inscription.
4. Each of the `program_outputs` has its opening in `program_notes`, in the same order, whose commitment, with the public key `PK0` and `program` set to `program_id`, is that output.
5. The program proof verifies under the registered key on `(program_step_id, program_deposits_hash(program_deposits), op_id)`, `program_deposits_hash` being the hash of the `(value, intent)` pairs of the program deposits the step consumes, in their order in the mini-block, which the sequencer chooses.
6. No program deposit is left pending at the end of a mini-block.

The openings serve only the availability of the state of the program. They sit in the proof of the step, outside the `op_id` and the transaction hash, and the ledger keeps nothing from them. A block is valid only with all its openings, so stripping them cannot skip the check. A node may prune the openings of the blocks behind its latest immutable block, which it never validates again; a node syncing these blocks needs a peer that kept them, or bootstraps from a checkpoint after them. Past that point the sequencers of a channel should keep the openings of its unspent notes.

The `ZkProgramSpend` is the ZkTransfer with program checks: its inputs are notes of `program_id` held by `PK0`, their nullifiers derived with `NF_SK0`, so it takes no spending secret key, its outputs are notes of `program_id` held by `PK0` or user notes, `program_step_id` commits to the active flag and the note of every input and output, nonce and staking key included, so that a program can constrain the staking key of the notes it creates, the fields of an inactive one reading as `0`, and `sum(inputs_value) + paid_value == sum(outputs_value)` over the values of its inputs and outputs, with `paid_value` below $`2^{64}`$ and the sum of the inputs below $`2^{74}`$, the nullifiers of its active inputs pairwise distinct, and its active inputs first. Its used inputs and outputs are marked by the public flags `inputs_active` and `outputs_active`, set from the published lists as in the ZkTransfer, and its outputs of the program by the public flags `outputs_of_program`, set from the length of `program_outputs`, which come first. It is proven by the sequencer. The circuit is `program_spend` in [logos-blockchain-circuits](https://github.com/logos-blockchain/logos-blockchain-circuits); its constraints and proving time are to be measured on the circuit this RFC specifies (see [Implementation](#implementation)).

When a step consumes a note of the program, the circuit derives the nonce of each active output `k` as `zkhash(NOTE_NONCE_V1, inputs[0], k, value, public_key)`, from the nullifier of the first input: the `op_id` cannot serve, since it covers the output commitments and thus their nonces. The circuit requires the active inputs to come first, so `inputs_active[0]` holds exactly when the step consumes a note of the program. Such a step re-creates neither a note it consumes nor the output of another such step, so a sequencer cannot burn a note by re-creating it, and cannot withhold a payout from a holder who knows its value, since the holder recomputes the nonce from the inscription. A commitment created ahead of time with a chosen nonce costs its creator the value. A step consuming no note of the program picks its nonces, and a program admitting such a step should constrain them through `program_step_id`. A derived nonce is a public function of the value and the public key of the note, so a payee should use a one-time public key.

## 3. What enforces what

Mantle gains a **Programs** section stating, for each guarantee, the check that enforces it, and the design choices behind them: why creating a program note needs its proof, why a program deposit exists only together with the program step consuming it, why program notes are held by `PK0`, why the proofs are bound to the `op_id`, why program notes stake unless their staking key is `0` and where the reward of a block they lead goes, why they never withdraw, why every program note a step creates is opened, for data availability only. Publishing the preimage of each intent in the inscription is recommended, depending on the program.

## 4. Program registration

`PROGRAM_REGISTER`, opcode `0x01`, carries a `Groth16VerificationKey`, the Groth16 verification key of the program, with exactly four `ic` points, one per public input plus one. Its proof is empty.

```python
def derive_program_id(key: Groth16VerificationKey) -> ProgramId:
    h = Hasher()
    h.update(b"PROGRAM_ID_V1")
    h.update(encode(key))
    return FiniteField(h.digest(), byte_order="little", modulus= p)
```

- Validation checks that every point is on its curve, in its prime-order subgroup and not the point at infinity.
- Execution computes the pairing `e(α, β)` once, and stores the key with it in `ledger.programs` under its identifier: 384 bytes beyond the key. The line coefficients of `-γ` and `-δ` would take tens of kilobytes per program, so each program proof computes them. Registering a key already registered has no effect.

## 5. Encoding

```diff
-Step               = UserStepKind UserStep
+Step               = (UserStepKind UserStep) / (ProgramDepositKind ProgramDeposit)
+                     / (ProgramStepKind ProgramStep)
 UserStepKind       = %x00
+ProgramDepositKind = %x01
+ProgramStepKind    = %x02
+ProgramDeposit     = ProgramId Inputs Outputs CommitmentRoot Value Intent Inscription
+ProgramStep        = ProgramId Inputs ProgramOutputs Outputs CommitmentRoot ProgramStepId Inscription
+Intent             = FieldElement
+ProgramOutputs     = Outputs                ; the notes of the program the step creates
+ProgramStepId      = FieldElement
+ProgramRegister    = Groth16VerificationKey ; Alpha G1, Beta Gamma Delta G2, 4 IC G1: 352 bytes
-ChannelInscribeOpProof = Ed25519Signature *ZkTransfer
+ChannelInscribeOpProof = Ed25519Signature *StepProof
+StepProof              = ZkTransfer / ProgramStepProof   ; ZkTransfer for a user step or a program deposit
+ProgramStepProof       = ZkProgramSpend Groth16Proof *ProgramNoteOpening   ; one per ProgramOutputs entry
+ProgramNoteOpening     = Value NoteNonce NoteStakePk ProgramNoteData   ; 104 bytes
-SDPDeclare             = ServiceType Locators ProviderId ZkId NotePk Inputs CommitmentRoot Value
+SDPDeclare             = ServiceType Locators ProviderId ZkId NotePk NoteStakePk Inputs CommitmentRoot Value
```

The inscriptions of a `ChannelInscribe` and of its steps total at most `MAX_OPERATION_DATA_SIZE` bytes, a decoder rejecting more. A program step lists the notes of its program in `ProgramOutputs` apart from the user notes in `Outputs`, so the flags of the ZkProgramSpend follow from the two lengths and a step has a single encoding. The staking key is a `NoteStakePk` wherever it is encoded.

The encoding also defines the compressed points `G1Point` and `G2Point`: little-endian coordinates, `c0` then `c1` for `G2Point`, bit 7 of the last byte set when `y` is the larger root, bit 6 the point at infinity, which is rejected, and coordinates below the base field modulus, so that a point, and thus a key and its program identifier, has a single encoding. What makes a proof valid beyond its encoding is defined by Groth16, as for Ed25519 signatures. Mantle checks the points of a key because the key is registered as ledger state.

## 6. Gas

A program deposit costs `EXECUTION_TRANSFER_GAS`, like a user step, and a program step `EXECUTION_PROGRAM_SPEND_GAS` and `EXECUTION_PROGRAM_PROOF_GAS`. `PROGRAM_REGISTER` costs `EXECUTION_PROGRAM_REGISTER_GAS`. The values come from measurements of the node's Groth16 verifiers, 1 Execution Gas per 1,000 CPU cycles:

- `EXECUTION_PROGRAM_SPEND_GAS = 619`: the ZkProgramSpend proofs of a block (37 public inputs) are verified in one batch, `3,975,765 + n * 618,796` cycles. Its fixed part is deducted from the block limit with the ZkTransfer one, so `limit_Ex = G_max = 3,192,483` and `G_target = 1,596,241`.
- `EXECUTION_PROGRAM_PROOF_GAS = 2451`: the program proof is verified alone, since it cannot share the batch of another program, by the single proof verifier, 2,221,544 cycles at 3 public inputs, plus the line coefficients of `-γ` and `-δ` of the key, 228,669 cycles.
- `EXECUTION_PROGRAM_REGISTER_GAS = 1896`: the subgroup checks of the 3 G2 points of the key, 573,324 cycles, and the pairing `e(α, β)`, 1,322,111 cycles. Point decompression is the same for every key and proof and is not counted.

## Chores

- The `Groth16` terminal of the encoding is renamed `Groth16Proof`, and Block Construction follows.
- The proving time benchmarks of the Proof of Leadership, the Proof of Quota, the ZkTransfer and the ZkProgramSpend are to be measured again on the circuits of this RFC.

# Implementation

- [ ] Add the `stake_public_key`, `program` and `data` fields to notes and to their commitment, with `0` as `program` and `data` for user notes, and `stake_public_key` set to the public key for the Genesis notes, the proof of work claim notes and the leader reward notes.
- [ ] Add `note_stake_pk` to `SDP_DECLARE`, its encoding and `DeclarationInfo`, keep `note_pk` in `DeclarationInfo`, and create the service note and the service reward notes under `note_pk` and `note_stake_pk`.
- [ ] Derive the nullifier key `nf_sk` from the spending secret key with `NF_KDF_V1`, the public key from `nf_sk`, and the nullifier from `nf_sk`, in the wallet and the ZkTransfer, the DST of the circuits renamed from `NF_KDF` to `NF_KDF_V1`.
- [ ] In the ZkProgramSpend circuit, drop the witness `inputs_spending_sk` and fix the public key of every input and of every output flagged in `outputs_of_program` to the constant `PK0 = zkhash(KDF, NF_SK0)`, and the nullifier key of every input to the constant `NF_SK0 = zkhash(NF_KDF_V1, 0)`, `program_step_id` hashing `PK0` as the public key of each active input.
- [ ] Take the staking key as a private witness of the ZkTransfer and the ZkProgramSpend, with `program` and `data` fixed to `0` in the ZkTransfer, and add the staking keys to `program_step_id`.
- [ ] In the Proof of Leadership and the leader branch of the Proof of Quota, which shares its lottery constraints, take `nf_sk`, `staking_sk` and the `program` and `data` of the note as private witnesses, derive the public key and the nullifier from `nf_sk` and the staking key from `staking_sk`, derive the ticket, the entropy contribution and the key nullifier from `staking_sk`, and derive the leader reward note with `reward_public_key` as both keys.
- [ ] Regenerate the verification keys of the ZkTransfer, the ZkProgramSpend, the Proof of Leadership and the Proof of Quota, which every node verifying them needs.
- [ ] Measure the constraints and proving times of these four circuits, and update their benchmarks in Mantle, the Proof of Leadership and the Proof of Quota.
- [ ] Have wallets use `nf_sk` as the staking secret key of their notes, and give a transfer output the public key of its recipient as staking key unless the recipient asks for another.
- [ ] Add the `inscription` of program deposits and program steps, compute `program_deposit_id` as the BLAKE2b hash of the channel and the encoded program deposit, and bound the inscriptions of an inscribe together by `MAX_OPERATION_DATA_SIZE`.
- [ ] Implement the `ZkProgramSpend` circuit, its own circuit-specific setup and its verifier.
- [ ] Reject the point at infinity when decoding the points of a proof.
- [ ] Implement `PROGRAM_REGISTER`: the key encoding, the curve and subgroup checks, the program identifier and the `programs` map.
- [ ] Implement user steps, program deposits and program steps in `CHANNEL_INSCRIBE`, as one flat list per mini-block tagged by kind in the encoding: the program deposits pending until the next program step, which must run their program, the program spend over the `program_outputs` then the `outputs` of the step, the program proof under its registered key, the openings of the program notes under `PK0`, and their encoding.
- [ ] Rename, in the ZkProgramSpend circuit, the signal `spend_notes_hash` to `program_step_id` and its DST `PROGRAM_SPEND_NOTES_V1` to `PROGRAM_STEP_ID_V1`.
- [x] Measure the Execution Gas of `PROGRAM_REGISTER`, the `ZkProgramSpend` and the program proof.
- [ ] Add tests and test vectors for note commitments, program registration, program steps and their encoding.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | 2.1.0 |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | 2.1.0 |
| [Genesis Block](../bedrock-genesis-block.md) | Modified | 1.3.1, no registered program, staking keys of the initial notes, the `note_stake_pk` of the declarations |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.2.1 |
| [Proof of Quota](../proof-of-quota.md) | Modified | 1.3.1, staking secret of the leader branch, verification key |
| [Service Reward Distribution](../bedrock-service-reward-distribution.md) | Modified | 1.4.1, reward notes under `note_pk` and `note_stake_pk` |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | 1.4.1, terminal rename, ZkProgramSpend batch, copies lacking or altering openings, staking key of the leader reward note |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | 1.9.1, `note_stake_pk`, rewards under the keys of the service note |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | 1.2.1, nullifier key and staking keys |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | 1.3.1, compression mode of the nullifier key derivation |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 1.9.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | 1.5.1, Execution Gas limit |
| [Execution Market](../execution-market.md) | Modified | 1.3.1, `G_max` and `G_target` |
| [Cryptarchia Protocol](../cryptarchia-v1-protocol.md) | Modified | 1.3.1, test vectors with `PROGRAM_REGISTER` and program steps |
