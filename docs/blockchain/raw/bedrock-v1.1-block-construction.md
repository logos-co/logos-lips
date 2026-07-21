# BLOCK-CONSTRUCTION-VALIDATION-AND-EXECUTION

| Field | Value |
| --- | --- |
| Name | Block Construction, Validation and Execution |
| Slug | 93 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors | Thomas Lavaur <thomaslavaur@logos.co>, Daniel Sanchez Quiros <danielsq@logos.co>, David Rusu <davidrusu@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Mehmet Gonen <mehmet@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revisions History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2025-12-03 |
| 1.1.0 | Removed `service_rewards` due to updated [SERVICE-REWARD-DISTRIBUTION-PROTOCOL](bedrock-service-reward-distribution.md). Extended the [Block Execution](#block-execution) logic with rewards distribution due to updated [SERVICE-REWARD-DISTRIBUTION-PROTOCOL](bedrock-service-reward-distribution.md). Removed **Block Samples** subsection of the [Batch verification of ZK proofs](#batch-verification-of-zk-proofs) from the [Annex](#annex). Reordered the [Block Execution](#block-execution) steps to enable immediate use of reward notes as inputs for transactions included in the proposal. | 2026-03-27 |
| 1.1.1 | [[RFC] Simplify Mantle Transaction and Refactor Ledger Operations](mantle-transaction-encoding/appendices/rfc-simplify-mantle-transaction-and-refactor-ledger-operations.md) | 2026-05-06 |

# Introduction

In this document, we present the specification defining the construction of the block proposal, its validation, and execution. We define the block proposal construction that contains references to transactions (from the mempool) instead of a complete transaction to limit its length. The raw block size increases with the size of transactions it contains up to 1 MB, and the proposal compresses its size down to 33 kB, which saves the bandwidth necessary to broadcast new blocks.

# Overview

For the consensus protocol to make progress, a new **leader** is elected through the leader lottery. The new leader is in possession of a proof of leadership (PoL) that confirms that it is indeed the leader. The main objective of the leader is to construct a new block, hence becoming a **block builder,** and share it with other members of the network as a **block proposer**. The block must be correctly constructed; otherwise, it will be rejected by the consensus nodes who are validating every block. Only validated blocks are executed, which means that the transactions included in the block are interpreted by all nodes, and the state of the chain is modified according to the instructions embedded in the transactions.

## High-level Flow

Below, we present a high-level description of the block lifecycle. The main focus of this section is to build an intuition on the block construction, validation, and execution.

1. A leader is selected. The leader becomes a block builder.
2. The block builder **constructs** a block proposal.
1. The block builder selects the latest block (parent) as the reference point for the chain state update.
2. The block builder selects valid Mantle Transactions (as defined in [Mantle](bedrock-v1.1-mantle-specification.md)) from its mempool and includes references to them in the proposal.
3. The block builder populates the block header of the block proposal.

3. The block proposer sends the block proposal to the Blend network.
4. The validators receive the block proposal.
5. The validators **validate** the block proposal.
1. They validate the block header.
2. They retrieve complete transactions from their mempool that are referred in the block.
3. They validate each transaction included in the block.

6. The validators **execute** the block proposal.
1. They derive the new blockchain state from the previous one by executing transactions as defined in [Mantle](bedrock-v1.1-mantle-specification.md).
2. They update the different variables that need to be maintained over time.
3. They execute the [**Service Reward Distribution Protocol**](bedrock-service-reward-distribution.md) to generate reward notes locally.

# Constructions

## Hash

We are using two hashing algorithms that have the same output length of 256 bits (32 bytes) that are [Poseidon2 and Blake2b](common-cryptographic-components.md).

## Block Proposal

A block proposal, instead of containing complete Mantle Transactions of an unlimited size, contains references of fixed size to the transactions. Therefore, the size of the proposal is constant and it is 33129 bytes.

We define the following message structure:

```python
class Proposal:                              # 33129 bytes
    header: Header                           # 297 bytes
    references: References                   # 32768 bytes
    signature: Ed25519Signature              # 64 bytes
```

Where:

- `header` is the header of the proposal; defined below: [Header](#header).
- `references` is a set of 1024 references to transactions of a `hash` type; the size of the `hash` type is 32 bytes and is the transaction hash as defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction).
- `signature` is the signature of the complete `header` using the `leader_key` from the `ProofOfLeadership`; the size of the `Ed25519Signature` type is 64 bytes.

  The length of the `references` list must be preserved to maintain the message’s indistinguishability in the Blend protocol. Therefore, the list must be padded with zeros when necessary.

### Header

```python
class Header:                                # 297 bytes
    bedrock_version: byte                    # 1 byte
    parent_block: hash                       # 32 bytes
    slot: SlotNumber                         # 8 bytes
    block_root: hash                         # 32 bytes
    proof_of_leadership: ProofOfLeadership   # 224 bytes
```

Where:

- `bedrock_version` is the version of the proposal message structure that supports other protocols defined in linked reference; its size is 1 byte and is fixed to `0x01`.
- `parent_block` is the block ID ([Cryptarchia Protocol](cryptarchia-v1-protocol.md)) of the parent block, validated and accepted by the block builder. It is used for the derivation of the `AgedLedger` and `LatestLedger` values necessary for validating the PoL; the size of the `hash` is 32 bytes.
- `slot` is the consensus slot number; the size of the `SlotNumber` type is 8 bytes.
- `block_root` is the root of the Merkle tree constructed from transaction hashes (defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction)) used for constructing the `references` list in the `mempool_ransactions`; the size of the `hash` is 32 bytes.
- `proof_of_leadership` is the proof confirming that the sender is the leader; defined below: [Proof of Leadership](#proof-of-leadership).

### References

```python
class References:                            # 32768 bytes
    mempool_transactions: list[hash]         # 1024 * 32 bytes
```

Where `mempool_transactions` is a set of up to 1024 references to transactions of a `hash` type; the size of the `hash` type is 32 bytes and is the transaction hash as defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction).

### Proof of Leadership

```python
class ProofOfLeadership:                     # 224 bytes
    leader_voucher: RewardVoucher            # 32 bytes
    entropy_contribution: zkhash             # 32 bytes
    proof: ProofOfLeadership                 # 128 bytes
    leader_key: Ed25519PublicKey             # 32 bytes
```

Where:

- `leader_voucher` is the voucher value used for retrieving the reward by the leader for proposal; the size of the `RewardVoucher` is 32 bytes.
- `entropy_contribution` is the output of the PoL contribution for Cryptarchia entropy; the size of the `zkhash` type is 32 bytes.
- `proof` is the proof confirming that the proposal is constructed by the leader; the size of the `ProofOfLeadership` type is 128 bytes (2 compressed $`\mathbb{G}_1`$and 1 compressed $`\mathbb{G}_2`$ BN256 elements).
- `leader_key` is the one-time `Ed25519PublicKey` used for signing the `Proposal`. This binds the content of the proposal with the `ProofOfLeadership`; the size of the `Ed25519PublicKey` type is 32 bytes.

## Proposal Construction

In this section, we explain how the block proposal structure presented above is populated by the consensus leader.

The block proposal is constructed by the leader of the current slot. The node becomes a leader only after successfully generating a valid PoL for a given `(Epoch, Slot)`.

### Prerequisites

Before constructing the proposal, the block builder must:

1. Select a valid parent block referenced by `ParentBlock` on which they will extend the chain.
2. Derive the required Ledger state snapshots `AgedLedger` and `LatestLedger` from the state of the chain including the last block.
3. Select a valid unspent note winning the PoL.
4. Generate a valid PoL proving leadership eligibility for `(Epoch, Slot)` based on the selected note. Attach the PoL to a one-time Ed25519 public key used to sign the block proposal.

Only after the PoL is generated can the block proposal be constructed (see [Proof of Leadership](cryptarchia-proof-of-leadership.md)).

### Construction Procedure

1. Initialize proposal metadata with the last known state of the blockchain. Set the:
  - `header`:
    - `bedrock_version`
    - `parent_block`
    - `slot`
    - `block_root`
    - `proof_of_leadership`:
      - `leader_voucher`
      - `entropy_contribution`
      - `proof`
      - `leader_key`

2. Construct the `mempool_transactions` object:
1. Select Mantle transactions:
    - Choose up to `1024` valid `SignedMantleTx` from the local mempool.
    - Ensure each transaction:
      - Is valid according to [Mantle](bedrock-v1.1-mantle-specification.md).
      - Has no conflicts with others (e.g., two transactions trying to spend the same note).

3. Derive references values:
```python
references: list[hash] = [mantle_txhash(tx) for tx in mempool_transactions]
```

4. Compute the `header.block_root` as the root of the Merkle tree constructed from the `mempool_transactions` transactions used to build `references`.
5. Sign the block proposal header.
```text
signature = Ed25519.sign(leader_secret_key, header)
```

6. Assemble the block proposal.
```python
proposal = Proposal(
    header,
    references,
    signature
)
```

  The PoL must have been generated beforehand and bound to the same Ledger view as mentioned in the [Prerequisites](#prerequisites).

The constructed proposal can now be broadcast to the network for validation.

## Block Proposal Reconstruction

Given a block proposal, we assume *transaction maturity*. This means that the block proposal must include transactions from the mempool that have had enough time to spread across the network to reach all nodes. This ensures that transactions are widely known and recognized before block reconstruction.

This transaction maturity assumption holds true because the block proposal must be sent through the Blend Network before it reaches validators and can be reconstructed. The Blend Network introduces significant delay, ensuring that transactions referenced in the proposal have reached all network participants. This approach is crucial for maintaining smooth network operation and reducing the risk that proposals get rejected due to transactions being unavailable to some validators. Moreover, by increasing the number of nodes that have seen the transaction, anonymity is also enhanced as the set of nodes with the same view is larger. This may result in increased difficulty—or even practical prevention—of executing deanonymization attacks such as tagging attacks.

Upon receipt of a block proposal, validators must confirm the presence of all referenced transactions within their local mempool. This verification is an absolute requirement—if even a single referenced transaction is missing from the validator's mempool, the entire proposal must be rejected. This stringent validation protocol ensures only widely-distributed transactions are included in the blockchain, safeguarding against potential network state fragmentation.

The process works as follows:

1. Transaction is added to the node mempool.
2. Node sends the transaction to all its neighbors.
3. Neighbors add the transaction to their own mempools and propagate it to their neighbors—transaction is gossiped throughout the network.
4. Block builder selects a transaction from its local mempool, which is guaranteed to be propagated through the network due to steps 1-3.
5. Block builder constructs a block proposal with references to selected transactions.
6. Block proposal is sent through the Blend Network, which requires multiple rounds of gossiping. This introduces a delay that ensures the transaction has reached most of the network participants' mempools.
7. Block proposal is received by validators.
8. Validators check their local mempools for all referenced transactions from the proposal.
9. If any transaction is missing, the entire proposal is rejected.
10. If all transactions are present, the block proposal is reconstructed and proceeds to further validation steps.

## Block Proposal Validation

This section defines the procedure followed by a Logos Blockchain node to validate a received block proposal.

Given a `proposal`, a proposed block consisting of a `header` and `references`. This block proposal is considered valid if the following conditions are met:

1. **Block Validation**
  The `proposal` must satisfy the rules defined in [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation).

2. **Block Proposal Reconstruction**
  The `references` must refer to existing `mempool_transaction` entries that are retrievable from the node's local mempool.

3. **Mempool Transactions Validation**
  `mempool_transactions` must refer to a valid sequence of Mantle Transactions from the mempool. Each transaction must be valid according to the rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md). In order to verify ZK proofs, they are batched for verification as explained in [Batch verification of ZK proofs](#batch-verification-of-zk-proofs) to get better performance.

If any of the above checks fail, the block proposal must be rejected.

## Block Execution

This section specifies how a Logos Blockchain node executes a valid block proposal to update its local state.

Given a `ValidBlock` that has successfully passed proposal validation, the node must:

1. Append the `leader_voucher` contained in the block to the set of reward vouchers **when the following epoch starts**.
2. Execute the reward distribution protocol defined in [**Service Reward Distribution Protocol**](bedrock-service-reward-distribution.md) to generate reward notes locally and include them in the ledger.
3. Execute the Mantle Transactions included in the block sequentially, using the execution rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md).

# Annex

## Batch verification of ZK proofs

### Proofs of Claim

1. For each proof of Claim, the verifier collects the classic Groth16 elements required for verification. It includes the proof $`\pi^{(i)}`$, and the public values $`x_j^{(i)}`$ for each proof of claim.
2. The verifier draws one random value for each proof $`r_i \overset{\$}{\leftarrow} \mathbb{F}_p`$.
3. The verifier computes:
1. $`\pi'_{j} := \sum_{i=1}^k r_i \cdot \pi_j^{(i)}`$ for $`j \in \{A,B,C\}`$.
2. $`r' := \sum_{i=1}^k r_i`$
3. $`IC := r' \cdot \Psi_0 + \sum_{j=1}^l\left( \sum_{i=1}^k r_i \cdot x_j^{(i)} \right) \cdot \Psi_j`$

4. They test if $`\sum_{i=1}^k e(r_1\pi'_A,\pi'_B) = e(r'[\alpha]_1,[\beta]_2)+ e(IC,[\gamma]_2) + e(\pi'_C,[\delta]_2)`$.

  Note that this batch verification of Groth16 proofs is the same as what is described in the Zcash paper, Appendix B.2.

### ZkSignatures

The verifier follows the same procedure as in [Proofs of Claim](#proofs-of-claim) but with the Groth16 proofs of ZkSignatures.
