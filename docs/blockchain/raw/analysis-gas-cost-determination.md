# ANALYSIS-GAS-COST-DETERMINATION

| Field | Value |
| --- | --- |
| Name | [Analysis] Gas Cost Determination |
| Slug | 191 |
| Status | raw |
| Category | Informational |
| Editor | Thomas Lavaur <thomaslavaur@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/analysis-gas-cost-determination.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | N/A |
| 1.2.0 | Removed DA, included Execution Gas determination for channel deposits and withdraws. Updated the Execution Gas of the Channel config. | N/A |
| 1.3.0 | [\[RFC\] Make Ledger Transaction an Operation](mantle-transaction-encoding/appendices/rfc-make-ledger-transaction-an-operation.md). Updated project references to Logos Blockchain | N/A |
| 1.4.0 | [\[RFC\] Enforce NoteId uniqueness](mantle-transaction-encoding/appendices/rfc-enforce-noteid-uniqueness.md)​ | N/A |
| 1.4.1 | [\[RFC\] Simplify Mantle Transaction and Refactor Ledger Operations](mantle-transaction-encoding/appendices/rfc-simplify-mantle-transaction-and-refactor-ledger-operations.md) | N/A |
| 1.5.0 | Introduce the new Operation `CHANNEL_STAKE_ASSIGNATION` and update of the channel operations to reflect changes in Mantle | 2026-06-24 |
| 1.5.1 | Reflect Channel Deposit execution modification. It now consumes inputs to update their NoteId | 2026-07-27 |
| 1.5.2 | Renamed locked notes into service notes and stated that the Input Gas covers the check that a note is neither a service nor a channel note | 2026-08-27 |
| 1.5.3 | Adopted "active message" as the single name for the message | 2026-09-02 |
| 1.5.4 | Renamed the `stake_manipulation_threshold` of the channel gas derivations into `transfer_threshold` and the Channel Stake Assignation section into Channel Transfer, following Mantle | 2026-08-31 |
| 1.6.0 | Add the Execution Gas derivation for the `CLAIM_POW_REWARD` Operation | 2026-09-04 |
| 1.7.0 | Per-signature Ed25519 cost re-measured with strict verification ([Common Cryptographic Components](common-cryptographic-components.md) 1.2.0): 56 → 59 Execution Gas, `SDP_DECLARE_GAS` 646 → 649 | 2026-09-24 |
| 1.8.0 | Follow the private ledger of Mantle: the notes are proven with a ZkTransfer and spent by nullifier, the SDP messages are signed with Ed25519, the proof of work claim carries no proof, and the `LEADER_CLAIM` Operation is removed | 2026-10-07 |

# Introduction

In Mantle, each Mantle Transaction contains one or more Operations. These components consume gas, measured through fixed gas units that reflect their execution or storage impact. Logos Blockchain introduces two independent gas markets:

- Execution Gas: measuring computational workload.
- Permanent Storage Gas: measuring cost of fully replicated storage.

Gas constants are carefully calibrated to reflect the computational and storage requirements of different operations on Logos Blockchain. By standardizing gas measurements, the system can accurately charge fees proportional to resource usage, preventing network abuse and incentivizing efficient transaction design.

# Overview

We conducted a comprehensive analysis of execution requirements for each Operation type in Mantle Transactions. This detailed examination allowed us to determine precise gas amounts for each Operation based on the actual computational resources consumed.

The gas constants we established are strategically divided between permanent storage and execution components, directly proportional to their respective resource utilization within Mantle Transactions. This separation ensures that gas costs accurately reflect the true computational burden of different operations. Moreover, gas can also be adjusted arbitrarily to incentivize or disincentivize the usage of certain Operations compared to others.

Our methodology involved measuring execution complexity and defining how gas is determined for each Gas Market. This is critical for proper network operation as it directly impacts transaction prioritization and network economics.

## Permanent Storage Gas

Permanent Storage is paid directly for the entire signed Mantle Transaction. The Permanent Storage Gas price is derived from [Storage Markets](storage-markets.md) and is used to determine the Permanent Storage fee. 1 Permanent Storage Gas corresponds to 1 byte.

```python
permanent_storage_fee = len(encode(tx_signed)) * permanent_storage_gas_price
```

## Execution Gas

Execution is a second general market that represents how costly an Operation is to execute. This cost can be fixed or variable based on the content of the Operation. The Execution Gas base price is derived from [Execution Market](execution-market.md) and each Operation defines its execution gas amount. 1 Execution Gas corresponds to 1,000 CPU cycles.

```python
execution_base_fee = tx.ops.get_summed_gas() * execution_gas_base_price
```

The gas derivation of each Operation are:

TODO: update the gas values from the ZkTransfer measures
```python
TRANSFER_GAS                  = 590
CHANNEL_INSCRIBE_GAS          = 59
CHANNEL_CONFIG_GAS            = 59 * configuration_threshold
CHANNEL_DEPOSIT_GAS           = 590
CHANNEL_TRANSFER_GAS          = 59 * transfer_threshold
CHANNEL_WITHDRAW_GAS          = 59 * transfer_threshold
SDP_DECLARE_GAS               = 649
SDP_WITHDRAW_GAS              = 59
SDP_ACTIVE_GAS                = 59
CLAIM_POW_REWARD_GAS          = 0
```

and come from our implementation observations as described in [Gas determination from measures](#gas-determination-from-measures).  To get these numbers, we based our calculations on the following measures:

| Operation | Number of CPU cycles |
| --- | --- |
| ZkTransfer batch verification | 3,900,000 + number_of_proof x 590,000 |
| Eddsa25519 signature verification | 59,200 |

Comparison, list searching, hashes and operation in small fields are neglected. We also supposed that the initialization cost for batch verification is paid by everyone and deduced from the block directly. The user then pay only for the part that is proportional to the number of proofs.

# Transfer

The Execution Gas of the Transfer Operation compensates for the verification of the [ZkTransfer](bedrock-v1.1-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) proof.

Execution: ~590k CPU cycles.

- Verification of the ZkTransfer: 590,000 cycles.
## Input Gas

Input gas covers the computational cost of verifying that one nullifier is not in the nullifier set and that the referenced commitment root is recent. Additionally, it compensates for the insertion of the nullifier in the nullifier set.

Execution: negligible.

- Verification that the nullifier is not in the set: negligible.
- Verification that the commitment root is one of the last 1024 blocks: negligible.
- Insertion of the nullifier in the nullifier set: negligible.
## Output Gas

Output gas accounts for the computational resources required for the inclusion of one output commitment in the Ledger.

Execution: negligible.

- Appending of the commitment to the commitment MMR: negligible.
## Channel Inscription

The validation process includes verifying an Eddsa25519 signature, confirming that the signer is authorized for the specified channel, and checking the chaining sequence of the channel. The execution encompasses creating channel records (if not previously used) and updating the tip of the channel.

Execution: ~59k CPU cycles.

- Verification of the Ed25519 signature: 59,200 cycles.
- Verification of the signer authorization: negligible.
- Verification of channel sequencing: negligible
- Update the channel state: negligible
## Channel Deposit

The Execution Gas of the Channel Deposit Operation compensates for the verification of the [ZkTransfer](bedrock-v1.1-mantle-specification.md#zero-knowledge-transfer-proof-zktransfer) proof and for the check of the inputs.

Execution: ~590k CPU cycles.

- Verification of the ZkTransfer: 590,000 cycles.
- Verification that the nullifiers are not in the set: negligible.
- Insertion of the nullifiers in the nullifier set: negligible.
- Derivation of the channel note nonce and commitment: negligible.
- Insertion of the channel note in the channel notes: negligible.

## Channel Withdraw

The validation process requires verifying multiple Eddsa25519 signatures.
The execution require removing the channel notes and appending their commitments to the commitment MMR.

Execution: ~59k CPU cycles * transfer_threshold.

- Verification of `transfer_threshold` Ed25519Signatures: 59,200 cycles per signature.
- Verification that the notes are in the channel: negligible.
- Removing the notes from channel notes: negligible.
- Appending of the commitments to the commitment MMR: negligible.

## Channel Transfer

The validation process requires verifying multiple Eddsa25519 signatures, and managing the channel notes.
The execution require deriving the nonce and commitment of the outputs and adding them to the channel notes.

Execution: ~59k CPU cycles * transfer_threshold.

- Verification of `transfer_threshold` Ed25519Signatures: 59,200 cycles per signature.
- Verification that the notes are in the channel: negligible.
- Removing of the notes from the channel notes: negligible.
- Verification of the output validity: negligible.
- Derivation of the output nonces and commitments: negligible.
- Insertion of the outputs in the channel notes: negligible.

## Channel Config

This gas amount covers the verification of multiple Eddsa25519 signatures and ensures the operation is well-formed. This represents the computational cost associated with processing channel configuration operations.

- Execution: ~59k CPU cycles * configuration_threshold.
    - Verification of the configuration_threshold Ed25519 signatures: 59,200 cycles per signature.
    - Modification of the state of the channel: negligible.

## SDP Declaration

This gas covers multiple verification processes: confirming ownership of the consumed notes through a ZkTransfer verification and establishing ownership of the provider_id through an Eddsa25519 signature. It also includes verification of the declaration format, of the spendability of the inputs and of the amount. Additionally, it accounts for the creation of the service note and declaration management.

Execution: ~ 649k CPU cycles.

- Verification of the Ed25519 signature: 59,200 cycles.
- Verification of the ZkTransfer: 590,000 cycles.
- Verification that the declaration doesn’t already exist: negligible.
- Verification of locator length: negligible.
- Verification that the nullifiers are not in the set: negligible.
- Verification of the amount: negligible.
- Insertion of the nullifiers in the nullifier set: negligible.
- Derivation of the service note commitment: negligible.
## SDP Withdraw

This gas covers a verification process that includes: confirming ownership of the provider_id through an Eddsa25519 signature, and confirming that the declaration exists and has not been previously withdrawn. The validation process also ensures that the withdrawal message's nonce is greater than any previous nonce, preventing replay attacks. During execution, the system updates the declaration's status to withdrawn.

Execution: ~ 59k CPU cycles.

- Verification that the declaration exist: negligible.
- Verification of the Ed25519 signature: 59,200 cycles.
- Verification that the declaration wasn’t already withdrawn: negligible.
- Verification of nonce incrementation: negligible.
- Update declaration: negligible.
## SDP Activation

This gas funds the verification of the provider_id signature through an Eddsa25519 signature verification, validates the existence of the declaration in the system, and ensures that the active message's nonce is greater than any previous nonce to prevent replay attacks. The validation includes confirming that the declaration ID is present in the declarations dictionary and that the signature corresponds to the declaration's registered provider_id public key.

- Execution: ~59k CPU cycles.
    - Verification that the declaration exist: negligible.
    - Verification of nonce incrementation: negligible.
    - Verification of the Ed25519 signature: 59,200 cycles.
    - Evaluation of the activity depends on the service and is neglected here

## Claim PoW Reward

This gas covers the re-derivation of the puzzle ticket from the Operation payload, the comparison of that ticket against the reward difficulty, the lookup confirming the referenced block is canonical and within the acceptance window, the check that the ticket is not already in the nullifier set, and the check that the pool can cover a reward. The Operation carries no proof. Execution then inserts the nullifier, creates a single output note and decrements the pool.

Execution: negligible.

- Re-derivation of the puzzle ticket: one `zkhash` over four field elements, negligible.
- Comparison of the ticket against the reward difficulty: negligible.
- Lookup of the referenced block and the slot window comparison: negligible.
- Verification that the ticket isn't already in the nullifier set: negligible.
- Verification that the pool covers the per-claim reward: negligible.
- Insertion of the nullifier in the set: negligible.
- Derivation of the note nonce and commitment: negligible.
- Appending of the commitment to the commitment MMR: negligible.

A claim is intended to pay its own fee out of the reward it creates. The claim adds no Execution Gas to that fee, so the floor the per-claim reward must clear is set by the Permanent Storage fee of the transaction and the Execution Gas of the Transfer spending the reward note.

# Annex

## Gas determination from measures

The material used for the benchmarks is the following:

- CPU       : 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM       : 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS        : Ubuntu 22.04.5 LTS
- Kernel    : 6.8.0-59-generic

### Eddsa Signature Verification

To get the numbers, we executed the [test included in the official Rust implementation of the node](https://github.com/logos-blockchain/logos-blockchain/blob/3c249f67d11bcad6ce7cbd92cf8c6b977d35a443/tests/src/benchmarks/eddsa.rs#L17).

Over 100 iterations, verifying an Eddsa25519 signature with strict verification (small-order checks on the public key and on `R`, see [Common Cryptographic Components](common-cryptographic-components.md#eddsa)) requires an average of 59,200 CPU cycles.

### ZkTransfer

<!-- TODO: update the measures for the ZkTransfer circuit -->
To get the numbers, we executed the [test included in the official Rust implementation of the node](https://github.com/logos-blockchain/logos-blockchain/blob/3c249f67d11bcad6ce7cbd92cf8c6b977d35a443/zk/groth16/tests/zk_signature_cpu_cycles.rs#L349).

We found the best linear curve approximating these measures (over 1000 iterations):

| Number of Batches | Number of CPU cycles |
| --- | --- |
| 1 | 4,126,177 |
| 2 | 4,904,084 |
| 3 | 5,538,085 |
| 4 | 6,061,800 |
| 5 | 6,957,754 |
| 6 | 7,421,851 |
| 7 | 8,237,485 |
| 8 | 8,621,986 |
| 9 | 9,115,091 |
| 10 | 10,186,171 |
| 20 | 15,777,800 |
| 30 | 21,456,771 |
| 40 | 27,441,722 |
| 50 | 33,430,729 |
| 60 | 38,986,389 |

| Number of Batches | Number of CPU cycles |
| --- | --- |
| 70 | 44,708,450 |
| 80 | 50,894,373 |
| 90 | 56,534,430 |
| 100 | 63,606,624 |
| 110 | 70,036,347 |
| 120 | 75,612,096 |
| 130 | 82,048,010 |
| 140 | 87,080,407 |
| 150 | 91,473,391 |
| 160 | 97,862,623 |
| 170 | 104,019,852 |
| 180 | 111,498,103 |
| 190 | 114,814,226 |
| 200 | 119,739,702 |
