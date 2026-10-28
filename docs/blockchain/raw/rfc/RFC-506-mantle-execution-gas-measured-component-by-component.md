# [RFC] Mantle: Execution Gas measured component by component

**Motivation and proposal:** [PR #506](https://github.com/logos-co/logos-lips/pull/506)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-27 |

## Reviewer Orientation

Read [RFC-480](RFC-480-mantle-private-utxo-ledger.md), [RFC-481](RFC-481-mantle-programs-governing-channel-notes.md) and [RFC-486](RFC-486-mantle-post-quantum-note-encryption.md) first: this RFC prices the ledger they define.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | High | **Start here**: [Gas Cost Determination](#affected-specifications), [measures and fit](#1-measures) | the method, the cross-check of a full block, what each constant measures |
| 2 | High | **Start here**: [Mantle](#affected-specifications), [Execution Gas of a transaction](#2-execution-gas-of-a-mantle-transaction) | the bytes and note set terms of the transaction; `spend_gas`; the per-Operation formulas |
| 3 | High | [Cryptoeconomics Overview](#affected-specifications), [Execution Market](#affected-specifications), [block limit](#3-execution-gas-limit) | the fixed costs of a block deducted from the limit; `G_max`, `G_target` and the base fee constants |
| 4 | Medium | [node optimizations](#4-node-optimizations) | consensus neutrality of the deferred nullifier hashing and of the root reuse |

# Discussion

## Unit: core cycles of the reference machine

One Execution Gas is 1,000 core cycles, counted by the hardware performance counters of a pinned performance core. `rdtsc` ticks run at a fixed 2.419 GHz on the reference machine while its cores run up to 5.6 GHz, so a tick count understates the work of the core by about 2.2 times and depends on the frequency the core happens to run at. The 3.2 billion cycle budget of a block is unchanged. Calibrating it to the 2 GHz minimum-specification CPU of the hardware requirements is left open: it needs a measurement on such a CPU.

## Measured end to end, explained by components

Each constant is fitted on the node's own functions, run on a whole Mantle Transaction from its encoded bytes to the updated state, varying one dimension of its shape at a time. Micro-benchmarks of the trees, hashes and verifiers explain each constant. Summing micro-benchmarks alone would have priced at zero everything not benchmarked, which is how the earlier constants missed the trees. A block of 64 mixed transactions measured whole costs 14.8% less than the constants predict with the end of block work of its one channel set counted once. Its 24 transactions changing that set each pay the work, so its Execution Gas is 49.3% above its cost; [Nullifiers and note sets](#nullifiers-and-note-sets) explains why.

## Nullifiers and note sets

The nullifiers of a block are hashed into their tree once, at the end of the block. The first nullifier of a set costs two paths of the tree, 1,470,411 cycles. Every further one costs at most 773,145: its leaf lands next to the leaves appended before it, but its low leaf is anywhere in the tree, and the path of the low leaf shares only its upper levels with the other paths of the block. The measures draw the spent nullifiers like the nullifiers of real notes for that reason. `EXECUTION_NULLIFIER_GAS` prices the largest cost of a further nullifier, so the price of an Operation never depends on the other transactions of its block. The first nullifier of a set is paid with the end of block work of that set.

`EXECUTION_NOTE_SET_GAS` is paid once per transaction for each channel or SDP note set it changes. Alternatives:

- **Once per Operation.** Rejected: the Operations of one transaction changing the same set share one end of block work, and a transaction of several deposits or inscriptions to one channel would pay it several times.
- **Once per block, by the first transaction changing the set.** Rejected: the price of a transaction would depend on its position in the block and on the other transactions, which a block builder controls, and a user could not predict it.

A transaction changing a set pays its full end of block work, the largest measure of what a block spends on that set. The cost of this predictability falls on blocks where many transactions change one set: on the measured block, whose 24 inscriptions and deposit change one channel set, the Execution Gas is 49.3% above the work.

## Bytes

A transaction costs 26.0 cycles per byte for its decoding, its hash and the identifiers of its Operations. The term is integer: `len * 26 // 1000`. Note ciphertexts are paid through it.

## Rejected alternatives

- **Worst-case constant per Operation.** Each Operation would keep one constant at its maximum shape, 4 inputs and 8 outputs. Rejected: a Transfer of one input would pay for four nullifiers.
- **Pricing the growth of the ledger state.** Nullifier leaves, commitments, programs and declarations stay in the ledger state for good, and Permanent Storage Gas prices only the transaction bytes. Left out of this RFC.

## Limits of the measures

- SDP declarations are measured among up to 1,024 declarations of a service. Through the keys of the declarations of each service, their cost grows from 812,189 cycles among none to 890,885 among 1,024.
- `CLAIM_POW_REWARD` is measured on a state with an eased reward difficulty, the fixture difficulty requiring about 2^26 grinds to build a claim.
- Creating a channel creates its note set, priced as a change of that set; the creation itself, an insertion in the eligible tree, was not measured alone.

# Details

## 1. Measures

The Gas Cost Determination is rewritten around the measurements. It gives, for every Operation, the cycles of each of its steps, and, for every constant, the measure it comes from. Its Annex states the method, the machine, the batch verification fits and the cross-check, and links the benchmark of the node at the commit measured.

## 2. Execution Gas of a Mantle Transaction

```python
tx_execution_gas = (sum(execution_gas(op) for op in ops)
                    + len(encode(signed_tx)) * EXECUTION_KB_GAS // 1000
                    + EXECUTION_NOTE_SET_GAS * len(tx_note_sets))  # channel and SDP sets created or changed

def spend_gas(inputs, outputs, buffered) -> int:
    root_gas = 0 if buffered == 0 else EXECUTION_ROOT_GAS + EXECUTION_BUFFERED_GAS * buffered
    return (EXECUTION_PROOF_GAS + root_gas
            + EXECUTION_NULLIFIER_GAS * len(inputs)
            + EXECUTION_COMMITMENT_GAS * len(outputs))
```

- Transfer, Channel Deposit and Channel Withdraw: their constant plus `spend_gas`. A withdrawal pays in advance its release at its slot.
- Channel Inscribe: its constant and a signature, `EXECUTION_USER_STEP_GAS + spend_gas` per user step, and per program step `EXECUTION_PROGRAM_STEP_GAS + EXECUTION_PROGRAM_PROOF_GAS + spend_gas + EXECUTION_OPENING_GAS` per opening, plus `EXECUTION_PAYMENT_GAS + spend_gas` per payment.
- Channel Config: its constant plus a signature per unit of `configuration_threshold`.
- SDP Declare and SDP Withdraw: their constant, a signature and `spend_gas`. SDP Active: its constant, which includes the Proof of Quota, and a signature.

| Constant | Value | | Constant | Value |
| --- | --- | --- | --- | --- |
| `EXECUTION_TRANSFER_GAS` | 30 | | `EXECUTION_KB_GAS` | 26 |
| `EXECUTION_CHANNEL_INSCRIBE_GAS` | 13 | | `EXECUTION_NOTE_SET_GAS` | 4285 |
| `EXECUTION_CHANNEL_CONFIG_GAS` | 18 | | `EXECUTION_PROOF_GAS` | 1946 |
| `EXECUTION_CHANNEL_DEPOSIT_GAS` | 16 | | `EXECUTION_ROOT_GAS` | 887 |
| `EXECUTION_CHANNEL_WITHDRAW_GAS` | 13 | | `EXECUTION_BUFFERED_GAS` | 23 |
| `EXECUTION_SDP_DECLARE_GAS` | 669 | | `EXECUTION_NULLIFIER_GAS` | 838 |
| `EXECUTION_SDP_WITHDRAW_GAS` | 889 | | `EXECUTION_COMMITMENT_GAS` | 25 |
| `EXECUTION_SDP_ACTIVE_GAS` | 6975 | | `EXECUTION_SIGNATURE_GAS` | 167 |
| `EXECUTION_CLAIM_POW_REWARD_GAS` | 569 | | `EXECUTION_USER_STEP_GAS` | 137 |
| `EXECUTION_PROGRAM_REGISTER_GAS` | 6843 | | `EXECUTION_PAYMENT_GAS` | 211 |
| | | | `EXECUTION_PROGRAM_STEP_GAS` | 60 |
| | | | `EXECUTION_OPENING_GAS` | 157 |
| | | | `EXECUTION_PROGRAM_PROOF_GAS` | 6305 |

`EXECUTION_PROGRAM_SPEND_GAS` is replaced by `EXECUTION_PROOF_GAS`, which prices both ZkTransfer and ZkProgramSpend proofs.

## 3. Execution Gas limit

The fixed costs of a block are deducted from the 3,200,000 Execution Gas of a block: the header (105,594 cycles), its Proof of Leadership (7,123,958), the leader note and the end of block of the ledger set (2,882,057), its first nullifier (1,470,411), and the fixed parts of the ZkTransfer and ZkProgramSpend batches (7,602,306 and 8,574,612). Total 27,758,938 cycles, so `limit_Ex = G_max = 3,172,241`, `G_target = 1,586,120`, `BASE_FEE_NUMERATOR = 11_102_840` and `BASE_FEE_DENOMINATOR = 12_688_960`.

A note set takes about 250 years to fill with transfers of 8 outputs at the Execution Gas target (Mantle), and the eligible tree about 1,400 years with blocks full of channel creations, each paying `EXECUTION_NOTE_SET_GAS` (Proof of Leadership).

The Cryptoeconomics Overview states that every Mantle Transaction consumes Execution Gas for its bytes, and that a full 2 MiB block of large inscriptions costs 54,525 Execution Gas for its bytes, so the maximum block size bounds such blocks.

## 4. Node optimizations

The constants assume four optimizations of the node, which change no validity rule and no root:

- the nullifiers of a block are hashed into their tree once, at its end, each dirty node once;
- a proof whose root no buffered commitment extends is verified against the referenced root itself;
- the recent roots of a set expire in the order of their blocks rather than by a scan;
- the `provider_id` and `zk_id` of a declaration are looked up in keys of each service rather than by a scan.

# Implementation

- [ ] Merge the ledger optimizations of [Details 4](#4-node-optimizations) ([logos-blockchain#3921](https://github.com/logos-blockchain/logos-blockchain/pull/3921))
- [ ] Merge the gas benchmark of the node ([logos-blockchain#3922](https://github.com/logos-blockchain/logos-blockchain/pull/3922))
- [ ] Implement the Execution Gas of each Operation from the per-component constants and `spend_gas`, and the bytes and note set terms of the transaction
- [ ] Set the Execution Gas limit to 3,172,241 and the base fee constants of the Execution Market
- [ ] Update the tests and test vectors whose fees or gas depend on these constants
- [ ] Re-run the gas benchmark and check every constant against the Gas Cost Determination
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 2.0.0 |
| [Mantle](../bedrock-v1.1-mantle-specification.md) | Modified | 2.3.0 |
| [Cryptoeconomics Overview](../overview-cryptoeconomics.md) | Modified | 1.4.2 |
| [Execution Market](../execution-market.md) | Modified | 1.3.2 |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.2.2, time to fill the eligible tree |
