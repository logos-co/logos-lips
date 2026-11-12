# [RFC] Mantle: Execution Gas measured component by component

**Motivation and proposal:** [PR #506](https://github.com/logos-co/logos-lips/pull/506)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-27 |
| v2 | Note ciphertexts are delivered off chain and pay no Execution Gas of their own. An `SDP_WITHDRAW` extends no root by the buffer. The batch verification draws its coefficients on 128 bits in Block Construction. Every constant is measured again on the node following the SDP rules of master, as the minimum over 5 runs of the benchmark | 2026-11-03 |
| v3 | A Mantle Transaction pays each root extension once for each distinct note set, referenced root and `buffered` of its proofs. `EXECUTION_USER_STEP_GAS` is 178, `EXECUTION_PAYMENT_GAS` 250 and `EXECUTION_CLAIM_POW_REWARD_GAS` 592, for the channel in the messages of steps and payments and the tag of the claim ticket | 2026-11-03 |
| v4 | User steps and payments cover the buffer before their mini-block, so the number of commitments an extension covers follows from the mini-block | 2026-11-04 |
| v5 | `EXECUTION_USER_STEP_GAS` is 195 and `EXECUTION_PAYMENT_GAS` 267, for the two elements of the channel ID in the messages of steps and payments. Each notation is explained where it first appears | 2026-11-04 |
| v6 | The inscriptions of user steps and payments pay as transaction bytes | 2026-11-06 |
| v7 | A program deposit is a step of its own, priced by `EXECUTION_PROGRAM_DEPOSIT_GAS`, and the identifiers of user steps and deposits are `user_step_id` and `program_deposit_id` | 2026-11-06 |
| v8 | `EXECUTION_PROGRAM_STEP_GAS` includes the program proof, 13528 being the sum of the two measured constants. An Operation pays `EXECUTION_SIGNATURE_GAS` for each signature its proof carries, so its Execution Gas reads no state. The note sets record the root extensions and the changes of a transaction, which pays them from that record. The one-note root of `SDP_WITHDRAW` is paid as `root_gas(1)`, its constant keeping the rest, `0`. The identifiers of user steps and program deposits hash the encoded step with BLAKE2b | 2026-11-06 |

## Reviewer Orientation

Read [RFC-480](RFC-480-mantle-private-utxo-ledger.md) and [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) first: this RFC prices the ledger they define.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | High | **Start here**: [Gas Cost Determination](#affected-specifications), [measures and fit](#1-measures) | the method, the cross-check of a full block, what each constant measures |
| 2 | High | **Start here**: [Mantle](#affected-specifications), [Execution Gas of a transaction](#2-execution-gas-of-a-mantle-transaction) | the bytes and note set terms of the transaction; `spend_gas`; the per-Operation formulas |
| 3 | High | [Cryptoeconomics Overview](#affected-specifications), [Execution Market](#affected-specifications), [block limit](#3-execution-gas-limit) | the fixed costs of a block deducted from the limit; `G_max`, `G_target` and the base fee constants |
| 4 | Medium | [node optimizations](#4-node-optimizations) | consensus neutrality of the deferred nullifier hashing and of the root reuse |

# Discussion

## Unit: core cycles of the reference machine

One Execution Gas is 1,000 core cycles of a Cortex-A76 at 2.4 GHz, counted by its hardware cycle counter (`CPU_CYCLES`, read through `perf_event`) with the benchmark pinned to one core. The reference machine is a Raspberry Pi 5, whose 4 cores at 2.4 GHz are close to the CPU of 2 cores at 2 GHz that the Cryptoeconomics Overview takes as the minimum of a basic Bedrock validator node. The 3.2 billion cycle budget of a block is unchanged.

## Measured end to end, explained by components

Each constant is fitted on the node's own functions, run on a whole Mantle Transaction from its encoded bytes to the updated state, varying one dimension of its shape at a time. Micro-benchmarks of the trees, hashes and verifiers explain each constant. Summing micro-benchmarks alone would have priced at zero everything not benchmarked, which is how the earlier constants missed the trees. With the end of block work of its one channel set counted once, the constants predict 9.1% more than a block of 64 mixed transactions costs, measured whole. Its 24 transactions changing that set each pay the work, so its Execution Gas is 41.2% above its cost; [Nullifiers and note sets](#nullifiers-and-note-sets) explains why.

## Nullifiers and note sets

The nullifiers of a block are hashed into their tree once, at the end of the block. The first nullifier of a set costs two paths of the tree, 4,061,452 cycles. Every further one costs at most 1,696,105: its leaf lands next to the leaves appended before it, but its low leaf is anywhere in the tree, and the path of the low leaf shares only its upper levels with the other paths of the block. The measures draw the spent nullifiers like the nullifiers of real notes for that reason. `EXECUTION_NULLIFIER_GAS` prices the largest cost of a further nullifier in a set of about a million nullifiers, each doubling of a set adding about one compression, so the price of an Operation never depends on the other transactions of its block. The first nullifier of a set is paid with the end of block work of that set.

`EXECUTION_NOTE_SET_GAS` is paid once per transaction for each channel or SDP note set it changes. Alternatives:

- **Once per Operation.** Rejected: the Operations of one transaction changing the same set share one end of block work, and a transaction of several channel deposits or inscriptions to one channel would pay it several times.
- **Once per block, by the first transaction changing the set.** Rejected: the price of a transaction would depend on its position in the block and on the other transactions, which a block builder controls, and a user could not predict it.

A transaction changing a set pays its full end of block work, the largest measure of what a block spends on that set. The cost of this predictability falls on blocks where many transactions change one set: on the measured block, whose 24 inscriptions and channel deposit change one channel set, the Execution Gas is 41.2% above the work.

## Bytes

A transaction costs 29.1 cycles per byte for its decoding, its hash and the identifiers of its Operations. The term is integer: `len * 30 // 1000`. The inscriptions of user steps and program deposits pay through this term and the Permanent Storage Gas like any other byte. The whole encoded step is read by one more Blake2b pass, into its `user_step_id` or `program_deposit_id`, 3.8 cycles per byte that the per-byte measure does not include ([Limits of the measures](#limits-of-the-measures)).

## Rejected alternatives

- **Worst-case constant per Operation.** Each Operation would keep one constant at its maximum shape, 4 inputs and 8 outputs. Rejected: a Transfer of one input would pay for four nullifiers.
- **Pricing the growth of the ledger state.** Nullifier leaves, commitments, programs and declarations stay in the ledger state for good, and Permanent Storage Gas prices only the transaction bytes. Left out of this RFC.

## Limits of the measures

- SDP declarations are measured among up to 1,024 declarations of a service. Through the keys of the declarations of each service, their cost grows from 2,302,348 cycles among none to 2,366,053 among 1,024.
- The measures that look up or insert nullifiers vary much more between runs than the others: each nullifier lands anywhere in the tree of a million leaves, and cache misses dominate. The base of a Transfer goes from 1 to 16 Execution Gas over 5 runs, so the constants take the per-case minimum over 5 runs. The constants of a few thousand cycles are therefore known only roughly.
- The cost of a user step grows with their number in an inscription: about 147,000 cycles per step from 2 to 4 steps, 156,000 from 4 to 8, each of these steps merging one peak of the MMR on average. `EXECUTION_USER_STEP_GAS` prices the slope over the measured range, and the cause of the growth is not identified.
- The Blake2b pass over the whole encoded step, 3.8 cycles per byte, is not in the per-byte measure, whose payload is the inscription of the Operation: a byte of the inscription of a step costs about 33 cycles against the 30 priced. A 2 MiB block made of inscriptions of steps spends at most about 8,000 Execution Gas in that pass, about 6,100 beyond what its bytes pay.
- `CLAIM_POW_REWARD` is measured on a state with an eased reward difficulty, the fixture difficulty requiring about 2^26 grinds to build a claim.
- Creating a channel creates its note set, priced as a change of that set; the creation itself, an insertion in the eligible tree, was not measured alone.
- The credit of the proof of work share of the fees to its pool, one integer addition per block, is not counted in the fixed costs of a block.

# Details

## 1. Measures

The Gas Cost Determination is rewritten around the measurements. It gives, for every Operation, the cycles of each of its steps, and, for every constant, the measure it comes from. Its Annex states the method, the machine, the batch verification fits and the cross-check, and links the benchmark of the node at the commit measured.

## 2. Execution Gas of a Mantle Transaction

```python
tx_execution_gas = (sum(execution_gas(op, op_proof)  # each Operation, from itself and its proof, below
                        for op, op_proof in zip(ops, op_proofs))
                    + len(encode(signed_tx)) * EXECUTION_KB_GAS // 1000
                    # the channel and SDP sets the transaction created or changed, each recording it
                    + EXECUTION_NOTE_SET_GAS * sum(note_set.tx_changed for note_set in ledger.sets[SDP_SET:])
                    # the (referenced root, covered) each set recorded when tx_commitment_root extended
                    # a root, covered being the number of buffered commitments a proof covers
                    + sum(root_gas(covered) for note_set in ledger.sets
                          for (_, covered) in note_set.tx_extended_roots))

# the extension of a referenced root by the commitments buffered before a proof
def root_gas(covered) -> int:
    return EXECUTION_ROOT_GAS + EXECUTION_BUFFERED_GAS * covered

# a ZkTransfer or a ZkProgramSpend, with the notes it spends and creates
def spend_gas(inputs, outputs) -> int:
    return (EXECUTION_PROOF_GAS
            + EXECUTION_NULLIFIER_GAS * len(inputs)
            + EXECUTION_COMMITMENT_GAS * len(outputs))
```

Proofs sharing their note set, referenced root and number of commitments covered, such as the user steps and program deposits of a mini-block naming one root, are verified against one extended root, computed and paid once: `tx_commitment_root` records the extension in `tx_extended_roots` of the set the first time it computes it, and returns the recorded root after. Charging each proof would price a step covering 800 commitments at about eight times a step of the first mini-block, so a block would hold few mini-blocks. A set records `tx_changed` when an Operation creates it, spends from it or adds to it, and a channel withdrawal pays the change of its release in its own Execution Gas, since that change comes in a later block.

The Execution Gas of each Operation reads only the Operation and its proof, an Ed25519 signature paying `EXECUTION_SIGNATURE_GAS` wherever the proof carries it:

- Transfer, Channel Deposit and Channel Withdraw: their constant plus `spend_gas`. A withdrawal also pays in advance its release at its slot, `EXECUTION_NOTE_SET_GAS` for the change it makes to the channel note set.
- Channel Inscribe: its constant and a signature, `EXECUTION_USER_STEP_GAS + spend_gas` per user step, `EXECUTION_PROGRAM_DEPOSIT_GAS + spend_gas` per program deposit, and per program step `EXECUTION_PROGRAM_STEP_GAS`, its program proof included, `spend_gas` over its program outputs and outputs, and `EXECUTION_OPENING_GAS` per opening.
- Channel Config: its constant plus a signature per signature of its proof, which validation holds to the threshold of the channel, none for a channel it creates.
- SDP Declare: its constant, a signature and `spend_gas`. SDP Withdraw: the same plus `root_gas(1)`, its root being the empty MMR extended by its service note, its constant keeping the rest. SDP Active: its constant, which includes the Proof of Quota, and a signature.

| Constant | Value | | Constant | Value |
| --- | --- | --- | --- | --- |
| `EXECUTION_TRANSFER_GAS` | 10 | | `EXECUTION_KB_GAS` | 30 |
| `EXECUTION_CHANNEL_INSCRIBE_GAS` | 26 | | `EXECUTION_NOTE_SET_GAS` | 8961 |
| `EXECUTION_CHANNEL_CONFIG_GAS` | 24 | | `EXECUTION_PROOF_GAS` | 4177 |
| `EXECUTION_CHANNEL_DEPOSIT_GAS` | 26 | | `EXECUTION_ROOT_GAS` | 2332 |
| `EXECUTION_CHANNEL_WITHDRAW_GAS` | 33 | | `EXECUTION_BUFFERED_GAS` | 60 |
| `EXECUTION_SDP_DECLARE_GAS` | 1693 | | `EXECUTION_NULLIFIER_GAS` | 1758 |
| `EXECUTION_SDP_WITHDRAW_GAS` | 0 | | `EXECUTION_COMMITMENT_GAS` | 58 |
| `EXECUTION_SDP_ACTIVE_GAS` | 15117 | | `EXECUTION_SIGNATURE_GAS` | 557 |
| `EXECUTION_CLAIM_POW_REWARD_GAS` | 1506 | | `EXECUTION_USER_STEP_GAS` | 28 |
| `EXECUTION_PROGRAM_REGISTER_GAS` | 15114 | | `EXECUTION_PROGRAM_DEPOSIT_GAS` | 144 |
| | | | `EXECUTION_PROGRAM_STEP_GAS` | 13528 |
| | | | `EXECUTION_OPENING_GAS` | 470 |

The [Gas Cost Determination](../analysis-gas-cost-determination.md#execution-gas) states what each constant measures. `EXECUTION_PROGRAM_SPEND_GAS` is replaced by `EXECUTION_PROOF_GAS`, which prices both ZkTransfer and ZkProgramSpend proofs. `EXECUTION_PROGRAM_STEP_GAS` is the sum of the measured program step beyond its spend, 213, and of its program proof, 13315. `EXECUTION_SDP_WITHDRAW_GAS` is what remains of the measured 2294 once `root_gas(1) = 2392` pays the one-note root, floored at `0`.

## 3. Execution Gas limit

The fixed costs of a block are deducted from the 3,200,000 Execution Gas of a block: the header (297,346 cycles), its Proof of Leadership (17,282,257), the leader note and the end of block of the ledger set (4,936,784), its first nullifier (4,061,452), and the fixed parts of the ZkTransfer and ZkProgramSpend batches (16,171,648 and 19,452,227). Total 62,201,714 cycles, so the block limit `limit_Ex = G_max = 3,137,798`, its target `G_target = 1,568,899`, and the factor of the base fee update `BASE_FEE_NUMERATOR = 10_982_293` over `BASE_FEE_DENOMINATOR = 12_551_192`.

A note set takes about 535 years to fill with transfers of 8 outputs at the Execution Gas target (Mantle), and the eligible tree about 2,990 years with blocks full of channel creations, each paying `EXECUTION_NOTE_SET_GAS` (Proof of Leadership).

The Cryptoeconomics Overview states that every Mantle Transaction consumes Execution Gas for its bytes, and that a full 2 MiB block of large inscriptions costs 62,914 Execution Gas for its bytes, so the maximum block size bounds such blocks.

## 4. Node optimizations

The constants assume six optimizations of the node, which change no validity rule and no root:

- the nullifiers of a block are hashed into their tree once, at its end, each dirty node once;
- a proof whose root no buffered commitment extends is verified against the referenced root itself;
- the recent roots of a set expire in the order of their blocks rather than by a scan;
- the `declaration_id` and the `provider_id` of a declaration are looked up in keys of each service rather than by a scan;
- the commitment root of a changed set is computed once at the end of the block, for both its recent roots and its eligible leaf;
- the batch verification of Groth16 proofs draws its random coefficients on 128 bits, which keeps the probability that an invalid proof passes at `2^-128`.

# Implementation

- [ ] Merge the ledger optimizations of [Details 4](#4-node-optimizations) ([logos-blockchain#3921](https://github.com/logos-blockchain/logos-blockchain/pull/3921))
- [ ] Merge the gas benchmark of the node ([logos-blockchain#3922](https://github.com/logos-blockchain/logos-blockchain/pull/3922))
- [ ] Implement the Execution Gas of each Operation from the Operation and its proof, with the per-component constants and `spend_gas`, a signature paid per signature carried, and the bytes, note set and root terms of the transaction from what its note sets record
- [ ] Set the Execution Gas limit to 3,137,798 and the base fee constants of the Execution Market
- [ ] Update the tests and test vectors whose fees or gas depend on these constants
- [ ] Re-run the gas benchmark and check every constant against the Gas Cost Determination
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 2.0.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | 2.2.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | 1.5.2 |
| [Execution Market](../execution-market.md) | Modified | 1.3.2 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.2.2, time to fill the eligible tree |
| [Block Construction](../bedrock-v1.1-block-construction.md) | Modified | 1.4.2, 128-bit batch coefficients |
