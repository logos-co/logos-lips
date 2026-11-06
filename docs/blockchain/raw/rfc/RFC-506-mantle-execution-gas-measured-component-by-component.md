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

One Execution Gas is 1,000 core cycles, counted by the hardware performance counters of a pinned performance core. `rdtsc` ticks, of the time stamp counter of the CPU, run at a fixed 2.419 GHz on the reference machine while its cores run up to 5.6 GHz, so a tick count understates the work of the core by about 2.2 times and depends on the frequency the core happens to run at. The 3.2 billion cycle budget of a block is unchanged. Calibrating it to the 2 GHz minimum-specification CPU of the hardware requirements is left open: it needs a measurement on such a CPU.

## Measured end to end, explained by components

Each constant is fitted on the node's own functions, run on a whole Mantle Transaction from its encoded bytes to the updated state, varying one dimension of its shape at a time. Micro-benchmarks of the trees, hashes and verifiers explain each constant. Summing micro-benchmarks alone would have priced at zero everything not benchmarked, which is how the earlier constants missed the trees. A block of 64 mixed transactions measured whole costs 9.1% less than the constants predict with the end of block work of its one channel set counted once. Its 24 transactions changing that set each pay the work, so its Execution Gas is 37.9% above its cost; [Nullifiers and note sets](#nullifiers-and-note-sets) explains why.

## Nullifiers and note sets

The nullifiers of a block are hashed into their tree once, at the end of the block. The first nullifier of a set costs two paths of the tree, 1,560,551 cycles. Every further one costs at most 673,573: its leaf lands next to the leaves appended before it, but its low leaf is anywhere in the tree, and the path of the low leaf shares only its upper levels with the other paths of the block. The measures draw the spent nullifiers like the nullifiers of real notes for that reason. `EXECUTION_NULLIFIER_GAS` prices the largest cost of a further nullifier, so the price of an Operation never depends on the other transactions of its block. The first nullifier of a set is paid with the end of block work of that set.

`EXECUTION_NOTE_SET_GAS` is paid once per transaction for each channel or SDP note set it changes. Alternatives:

- **Once per Operation.** Rejected: the Operations of one transaction changing the same set share one end of block work, and a transaction of several deposits or inscriptions to one channel would pay it several times.
- **Once per block, by the first transaction changing the set.** Rejected: the price of a transaction would depend on its position in the block and on the other transactions, which a block builder controls, and a user could not predict it.

A transaction changing a set pays its full end of block work, the largest measure of what a block spends on that set. The cost of this predictability falls on blocks where many transactions change one set: on the measured block, whose 24 inscriptions and deposit change one channel set, the Execution Gas is 37.9% above the work.

## Bytes

A transaction costs 26.8 cycles per byte for its decoding, its hash and the identifiers of its Operations. The term is integer: `len * 27 // 1000`. The inscriptions of user steps and payments pay through this term and the Permanent Storage Gas like any other byte, and are read by one more Blake2b pass, into the message of their step or payment. That pass is not priced yet: the measure on inscriptions without steps does not include it, and its per-byte cost joins the byte term at the next measurement.

## Rejected alternatives

- **Worst-case constant per Operation.** Each Operation would keep one constant at its maximum shape, 4 inputs and 8 outputs. Rejected: a Transfer of one input would pay for four nullifiers.
- **Pricing the growth of the ledger state.** Nullifier leaves, commitments, programs and declarations stay in the ledger state for good, and Permanent Storage Gas prices only the transaction bytes. Left out of this RFC.

## Limits of the measures

- SDP declarations are measured among up to 1,024 declarations of a service. Through the keys of the declarations of each service, their cost grows from 796,866 cycles among none to 847,129 among 1,024.
- A single run of the benchmark moves the small measures by up to about 10% (the base of a Transfer goes from 5 to 24 Execution Gas between runs), so the constants take the minimum over 5 runs. The constants of a few thousand cycles are therefore known only roughly.
- The cost of a user step grows with their number in an inscription: about 232,000 cycles per step from 1 to 2 steps, 275,000 from 4 to 8. `EXECUTION_USER_STEP_GAS` prices the slope over the measured range, and the cause of the growth is not identified.
- `CLAIM_POW_REWARD` is measured on a state with an eased reward difficulty, the fixture difficulty requiring about 2^26 grinds to build a claim.
- Creating a channel creates its note set, priced as a change of that set; the creation itself, an insertion in the eligible tree, was not measured alone.
- The credit of the proof of work share of the fees to its pool, one integer addition per block, is not counted in the fixed costs of a block.

# Details

## 1. Measures

The Gas Cost Determination is rewritten around the measurements. It gives, for every Operation, the cycles of each of its steps, and, for every constant, the measure it comes from. Its Annex states the method, the machine, the batch verification fits and the cross-check, and links the benchmark of the node at the commit measured.

## 2. Execution Gas of a Mantle Transaction

```python
tx_execution_gas = (sum(execution_gas(op) for op in ops)  # the Execution Gas of each Operation, below
                    + len(encode(signed_tx)) * EXECUTION_KB_GAS // 1000
                    + EXECUTION_NOTE_SET_GAS * len(tx_note_sets)  # channel and SDP sets created or changed
                    # distinct (note set, referenced root, covered) of the proofs extending a root,
                    # covered being the number of buffered commitments a proof covers
                    + sum(root_gas(covered) for (_, _, covered) in tx_extended_roots))

# the extension of a referenced root by the commitments buffered before a proof
def root_gas(covered) -> int:
    return EXECUTION_ROOT_GAS + EXECUTION_BUFFERED_GAS * covered

# a ZkTransfer or a ZkProgramSpend, with the notes it spends and creates
def spend_gas(inputs, outputs) -> int:
    return (EXECUTION_PROOF_GAS
            + EXECUTION_NULLIFIER_GAS * len(inputs)
            + EXECUTION_COMMITMENT_GAS * len(outputs))
```

Proofs sharing their note set, referenced root and number of commitments covered, such as the user steps and payments of a mini-block naming one root, are verified against one extended root, computed and paid once. Charging each proof would price a step covering 800 commitments at about eight times a step of the first mini-block, so a block would hold few mini-blocks.

- Transfer, Channel Deposit and Channel Withdraw: their constant plus `spend_gas`. A withdrawal pays in advance its release at its slot.
- Channel Inscribe: its constant and a signature, `EXECUTION_USER_STEP_GAS + spend_gas` per user step, and per program step `EXECUTION_PROGRAM_STEP_GAS + EXECUTION_PROGRAM_PROOF_GAS + spend_gas + EXECUTION_OPENING_GAS` per opening, plus `EXECUTION_PAYMENT_GAS + spend_gas` per payment.
- Channel Config: its constant plus a signature per unit of `configuration_threshold`.
- SDP Declare and SDP Withdraw: their constant, a signature and `spend_gas`. An SDP Withdraw extends no root: its root holds only its service note, and its constant covers that root. SDP Active: its constant, which includes the Proof of Quota, and a signature.

| Constant | Value | | Constant | Value |
| --- | --- | --- | --- | --- |
| `EXECUTION_TRANSFER_GAS` | 12 | | `EXECUTION_KB_GAS` | 27 |
| `EXECUTION_CHANNEL_INSCRIBE_GAS` | 21 | | `EXECUTION_NOTE_SET_GAS` | 3461 |
| `EXECUTION_CHANNEL_CONFIG_GAS` | 20 | | `EXECUTION_PROOF_GAS` | 1770 |
| `EXECUTION_CHANNEL_DEPOSIT_GAS` | 6 | | `EXECUTION_ROOT_GAS` | 879 |
| `EXECUTION_CHANNEL_WITHDRAW_GAS` | 31 | | `EXECUTION_BUFFERED_GAS` | 23 |
| `EXECUTION_SDP_DECLARE_GAS` | 622 | | `EXECUTION_NULLIFIER_GAS` | 725 |
| `EXECUTION_SDP_WITHDRAW_GAS` | 892 | | `EXECUTION_COMMITMENT_GAS` | 24 |
| `EXECUTION_SDP_ACTIVE_GAS` | 6927 | | `EXECUTION_SIGNATURE_GAS` | 161 |
| `EXECUTION_CLAIM_POW_REWARD_GAS` | 592 | | `EXECUTION_USER_STEP_GAS` | 195 |
| `EXECUTION_PROGRAM_REGISTER_GAS` | 6839 | | `EXECUTION_PAYMENT_GAS` | 267 |
| | | | `EXECUTION_PROGRAM_STEP_GAS` | 54 |
| | | | `EXECUTION_OPENING_GAS` | 151 |
| | | | `EXECUTION_PROGRAM_PROOF_GAS` | 6320 |

The [Gas Cost Determination](../analysis-gas-cost-determination.md#execution-gas) states what each constant measures. `EXECUTION_PROGRAM_SPEND_GAS` is replaced by `EXECUTION_PROOF_GAS`, which prices both ZkTransfer and ZkProgramSpend proofs.

## 3. Execution Gas limit

The fixed costs of a block are deducted from the 3,200,000 Execution Gas of a block: the header (103,945 cycles), its Proof of Leadership (7,101,514), the leader note and the end of block of the ledger set (2,040,800), its first nullifier (1,560,551), and the fixed parts of the ZkTransfer and ZkProgramSpend batches (7,260,262 and 8,241,358). Total 26,308,430 cycles, so the block limit `limit_Ex = G_max = 3,173,691`, its target `G_target = 1,586,845`, and the factor of the base fee update `BASE_FEE_NUMERATOR = 11_107_915` over `BASE_FEE_DENOMINATOR = 12_694_760`.

A note set takes about 220 years to fill with transfers of 8 outputs at the Execution Gas target (Mantle), and the eligible tree about 1,140 years with blocks full of channel creations, each paying `EXECUTION_NOTE_SET_GAS` (Proof of Leadership).

The Cryptoeconomics Overview states that every Mantle Transaction consumes Execution Gas for its bytes, and that a full 2 MiB block of large inscriptions costs 56,623 Execution Gas for its bytes, so the maximum block size bounds such blocks.

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
- [ ] Implement the Execution Gas of each Operation from the per-component constants and `spend_gas`, and the bytes and note set terms of the transaction
- [ ] Set the Execution Gas limit to 3,173,691 and the base fee constants of the Execution Market
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
