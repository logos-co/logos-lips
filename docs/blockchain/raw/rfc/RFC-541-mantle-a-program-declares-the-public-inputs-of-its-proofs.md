# [RFC] Mantle: A program declares the public inputs of its proofs

**Motivation and proposal:** [PR #541](https://github.com/logos-co/logos-lips/pull/541)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-18 |

## Reviewer Orientation

Read [Programs](../bedrock-v1.1-mantle-specification.md#programs) on the base branch first if program steps and program deposits are new to you.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Mantle](#affected-specifications), [the program ABI](#1-a-program-registers-an-abi-with-its-key) | the nodes, sources and types, and that `evaluate_abi` is total once `abi_type_checks` holds |
| 2 | Critical | **Start here**: [Mantle](#affected-specifications), [program step validation](#2-a-program-step-verifies-its-proof-on-the-inputs-its-abi-builds) | the arguments of the new `Groth16_verify` call; the spend stays bound to the `op_id` |
| 3 | Critical | [Mantle Transaction Encoding](#affected-specifications), [encoding](#3-encoding) | the ABI has a single encoding; `IC` is count-prefixed |
| 4 | High | [Mantle](#affected-specifications), [binding](#4-what-a-program-binds) | the definition of "an ABI binds `s`", the `Fr` argument, and the RISC Zero and SP1 examples |
| 5 | Medium | [Mantle](#affected-specifications) and [Gas Cost Determination](#affected-specifications), [gas](#5-gas) | `abi_gas` counts every hashed byte and permutation; four constants are `TBD` |
| 6 | Medium | [Mantle](#affected-specifications) and [Cryptarchia](#affected-specifications), [test vectors](#6-test-vectors) | recomputed values only |
| 7 | Low | [Chores](#chores) | skim |

# Discussion

## Why an expression the ledger evaluates

A proof binds a statement only through its public inputs, so the ledger's one job is to pin them to public data. Any computation over pinned data can run inside the circuit or the guest. The ABI therefore holds no logic of its own: it reproduces the format a wrapper fixes for its inputs, such as RISC Zero's nested SHA-256 claim digest, and nothing more.

Three shapes were considered:

- **An expression per public input** (chosen). It has no loop and no condition, so its type follows from its nodes and its cost from its size and the lengths of the sources it reads. It covers RISC Zero, SP1 and plain Groth16 with one mechanism.
- **Bytecode, or code the node runs over a snapshot of its state.** This puts a deterministic virtual machine, with its metering and memory limits, into consensus, and every node implementation must carry it. Reading ledger state also fails on its own terms: a sequencer proves a step before it knows the block carrying it, or the transactions before it in that block, so it cannot predict that state, and a reorg changes it.
- **Field elements and constants only, with no hashing.** RISC Zero and SP1 both hash their claim, so neither fits.

A fixed list of verifier kinds (one for RISC Zero, one for SP1) was also set aside: it ties the ledger to named products and to their versions.

## What the ledger enforces and what it recommends

No public input is mandatory. The ZkProgramSpend keeps every property the ledger owes other users: it balances exactly, it is bound to the `op_id`, its inputs are notes of the program of the step, and it derives the nonces of its outputs. A program whose ABI binds nothing lets any sequencer move its notes, and loses only those notes and the deposits paid to it, as `PROGRAM_REGISTER` already states of a faulty program. The ledger therefore checks only what protects the ledger itself:

- an encoding with a single reading, so no one registers a hostile ABI under the `ProgramId` of another;
- static types, so evaluation never fails and only the proof can;
- gas computed from the ABI and the lengths of its sources, before any hash runs.

Which constructions bind a value is a definition in [Programs](../bedrock-v1.1-mantle-specification.md#programs), with the reason for each rule, including why `Fr` binds only a hash output or bytes of a fixed length of at most 31. A wallet reads the ABI of a program to see what it binds.

Constants live in the ABI and the `ProgramId` covers them. The inscription is written by the sequencer, so a constant read from it, such as an `image_id`, would let a sequencer swap the guest of a program.

## The sources and nodes

Every source is fixed once the Mantle Transaction is fixed, does not depend on the block carrying it, and excludes every proof and opening. A sequencer can therefore prove a step as soon as its transaction is fixed, and pruning openings affects no input. The spec gives one sentence for each source left out: the whole transaction, the channel record (it holds slots and an index that a reorg changes) and time.

A survey of the on-chain verifiers of widely used zkVMs, read from their contracts and the code that builds their public inputs, gives this coverage:

| Coverage | Stacks |
| --- | --- |
| Verified unmodified by this ABI | RISC Zero Groth16 receipt, SP1 v5, SP1 v6 with its default nonce 0, Ziren |
| A `Slice` node would add | SP1 v6 with a network-chosen nonce |
| A `Blake3` node would add | RISC Zero Blake3Groth16 receipt, SP1 guests hashing their public values with BLAKE3 |
| `Keccak256` and a sorted-pair Merkle path node would add | Boundless set-inclusion receipts, Aligned aggregation |
| Out of reach of any node | Pico (gnark Groth16 with a Pedersen commitment, which changes the verifier itself); OpenVM, Powdr, ZisK, Airbender, Noir and STARK verifiers (not Groth16) |

The node set covers the first row only. Each node carries its own kind in the encoding, so a later change adds a node when a program needs one.

## Gas reads the registered ABI

The Execution Gas of a program step depends on the ABI registered under its program, which is ledger state. Validation reads that entry anyway, the `ProgramId` fixes the ABI, and programs are never removed, so the gas of an Operation stays a deterministic function of the Operation, its proof and the programs registered before it.

> **TODO (author):** measure `EXECUTION_PROGRAM_INPUT_GAS`, `EXECUTION_ABI_BYTE_GAS`, `EXECUTION_ABI_PERMUTATION_GAS` and `EXECUTION_PROGRAM_REGISTER_BYTE_GAS`, written `TBD`. Re-measure `EXECUTION_PROGRAM_STEP_GAS` and `EXECUTION_PROGRAM_DEPOSIT_GAS` without the input derivation and the hash of the program deposits, which their current figures include and the new terms price. Re-measure `EXECUTION_PROGRAM_REGISTER_GAS` on a key of `MAX_PROGRAM_INPUTS` inputs: the current figure covers 5 G1 points and a key of 12 inputs has 14.

## Parameters

`MAX_PROGRAM_INPUTS = 12` bounds verification, which costs one G1 scalar multiplication per input. RISC Zero needs 5 inputs and SP1 v6 needs 5. `MAX_ABI_NODES = 64` bounds the size and the nesting of an ABI while it is decoded; the RISC Zero example uses 41, since its two halves each repeat the claim digest.

## Documents left as they are

Two RFC documents describe the base this change builds on and are not edited:

- [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) states the three fixed public inputs of a program proof.
- [RFC-506](RFC-506-mantle-execution-gas-measured-component-by-component.md), in its v8 change-log entry, states that the Execution Gas of an Operation reads no state.

> **TODO (author):** decide whether either document should note this change.

# Details

## 1. A program registers an ABI with its key

`PROGRAM_REGISTER` carries the expressions that build the public inputs of the proofs of a program, and the `ProgramId` covers them.

```diff
 class ProgramRegister:
     verification_key: Groth16VerificationKey
+    abi: list[Expr]  # one expression per public input of a program proof, in order

-def derive_program_id(key: Groth16VerificationKey) -> ProgramId:
+def derive_program_id(key: Groth16VerificationKey, abi: list[Expr]) -> ProgramId:
     h = Hasher()
     h.update(b"PROGRAM_ID_V1")
     h.update(encode(key))
+    h.update(encode(abi))  # the ProgramAbi of the encoding, its count included
```

Validation checks `len(key.ic) == len(abi) + 1`, `1 <= len(abi) <= MAX_PROGRAM_INPUTS` and `abi_type_checks(abi)`. The ledger stores the ABI in `Groth16StoredKey` beside the key and `e(α, β)`.

The new section [Program ABI](../bedrock-v1.1-mantle-specification.md#program-abi) defines:

- the nodes `Const`, `FConst`, `Src`, `Concat`, `Sha256`, `ZkHash`, `Fr`, `Lo128`, `Hi128`, `Rev` and `Mask253`;
- the sources `OP_ID`, `TXHASH`, `PROGRAM_ID`, `PROGRAM_STEP_ID`, `STEP_INPUTS`, `STEP_PROGRAM_OUTPUTS`, `STEP_OUTPUTS`, `STEP_INSCRIPTION`, `PROGRAM_DEPOSITS`, `CHANNEL` and `SIGNER`;
- the types `field`, `bytes(n)` and `bytes(*)`, the fixed reading of a field element, a value and a list as bytes or as field elements, and the rule of each node;
- `evaluate_abi(abi, msg, step, program_deposits, op_id, txhash) -> list[zkhash]`.

## 2. A program step verifies its proof on the inputs its ABI builds

```diff
-assert Groth16_verify(ledger.programs[step.program_id],
-                      [step.program_step_id, program_deposits_hash(program_deposits), op_id_fr],
+stored = ledger.programs[step.program_id]
+assert Groth16_verify(stored,
+                      evaluate_abi(stored.abi, msg, step, program_deposits, op_id, txhash),
                       step_proof.program_proof)
```

`program_deposits_hash` leaves the ledger. The program spend stays bound to the `op_id`; the program proof is bound to what its ABI binds. `program_step_id` remains a public output of the ZkProgramSpend, the value through which an ABI reaches the notes of the spend.

## 3. Encoding

```diff
-ProgramRegister       = Groth16VerificationKey
+ProgramRegister       = Groth16VerificationKey ProgramAbi
-IC                    = 4G1Point
+IC                    = ICCount *G1Point
+ICCount               = Byte
+ProgramAbi  = ExprCount *Expr ; one Expr per public input of a program proof, in order
```

Each `Expr` starts with the byte of its kind, `%x00` to `%x0a`, followed by its operands: a `UINT16` length and the bytes of a `Const`, a `FieldElement`, a source byte, or a count and children. A decoder rejects an unknown kind or source, and stops past `MAX_ABI_NODES` nodes.

## 4. What a program binds

[Programs](../bedrock-v1.1-mantle-specification.md#programs) gains:

- a table of the bindings a program should declare (its spend, its inscription, its payments, and its sequencer and channel when its rule depends on them), and what each omission exposes;
- the definition of "an ABI binds `s`", and the reason `Fr` binds only a hash output or bytes of a fixed length of at most 31;
- three examples: a plain ABI reproducing `program_step_id`, the hash of the program deposits and the `op_id` exactly, a RISC Zero guest under the stock wrapper, and SP1 v5 and v6.

Its enforcement table, its Holder paragraph and its trust paragraph follow the ABI: a program whose rule depends on its sequencer binds `SIGNER`, and programs under one wrapper share its trusted setup.

## 5. Gas

```python
# CHANNEL_INSCRIBE, per program step, added to EXECUTION_PROGRAM_STEP_GAS:
EXECUTION_PROGRAM_INPUT_GAS * len(abi) + abi_gas(abi, step, program_deposits)
# PROGRAM_REGISTER, added to EXECUTION_PROGRAM_REGISTER_GAS:
EXECUTION_PROGRAM_REGISTER_BYTE_GAS * len(encode(register.abi))
```

`abi_gas` charges `EXECUTION_ABI_BYTE_GAS` per byte entering each `Sha256` or `Fr` and `EXECUTION_ABI_PERMUTATION_GAS` per `zkhash` permutation, at every occurrence in the tree. The four new constants are `TBD`. The Execution Gas of an Operation is derived from the Operation, its proof and, for each program step, the ABI registered under its program; `execution_gas` takes the registered programs.

## 6. Test vectors

- Mantle: the `PROGRAM_REGISTER` payload carries the key of the Program Id vector with `IC` count-prefixed and the plain ABI of the examples. Its `op_id`, the Program Id and the hash of the transaction with one of each Operation change.
- Cryptarchia: `leaf[1]`, the Merkle root of the transactions, both `body_root` values and the `block_id` change, since `leaf[1]` hashes the `PROGRAM_REGISTER` transaction.

## Chores

- Sentences saying the proofs of a program step are bound to the `op_id` (Channels, `CHANNEL_WITHDRAW`, the ZkProgramSpend comment) name the program spend.
- The gas analysis describes its program-step and program-deposit figures as measured: a program proof of 3 public inputs, one of them the hash of the program deposits.
- The unlanded revision rows Mantle 2.1.0 and 2.2.0, Encoding 2.1.0 and Gas Cost Determination 2.0.0 name the ABI.

# Implementation

- [ ]  Decode `ProgramRegister` with its count-prefixed `IC` and its `ProgramAbi`, rejecting an unknown kind or source and stopping past `MAX_ABI_NODES` nodes
- [ ]  Type-check an ABI at registration (`abi_type_checks`) and check `len(ic) == len(abi) + 1` and `1 <= len(abi) <= MAX_PROGRAM_INPUTS`
- [ ]  Derive the `ProgramId` from the key and the ABI, and store the ABI with the key
- [ ]  Evaluate the ABI of a program step (`evaluate_abi`) and verify the program proof on its result; remove `program_deposits_hash`
- [ ]  Compute `abi_gas` and the new gas terms of `CHANNEL_INSCRIBE` and `PROGRAM_REGISTER`, passing the registered programs to `execution_gas`
- [ ]  Measure the four `TBD` gas constants and re-measure the program step, program deposit and program register constants
- [ ]  Prove a RISC Zero guest and an SP1 v6 guest under their stock wrappers and verify both receipts through their ABIs
- [ ]  Add or extend tests / test vectors that exercise the change: the Mantle and Cryptarchia vectors, an ABI rejected for each validation rule, and the plain ABI matching the three inputs
- [ ]  Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | program ABI, `PROGRAM_REGISTER`, `CHANNEL_INSCRIBE` validation, Programs, gas, test vectors |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | `ProgramAbi`, `Expr`, count-prefixed `IC` |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | new gas terms; figures described as measured |
| [Cryptarchia](../cryptarchia-v1-protocol.md) | Modified | block test vectors |
