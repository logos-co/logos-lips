# BEDROCK-V1-1-BLOCK-CONSTRUCTION

| Field | Value |
| --- | --- |
| Name | Bedrock v1.1 Block Construction, Validation and Execution Specification |
| Slug | 93 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@status.im> |
| Contributors | Thomas Lavaur <thomaslavaur@status.im>, Daniel Sanchez Quiros <danielsq@status.im>, David Rusu <davidrusu@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Mehmet Gonen <mehmet@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-v1.1-block-construction.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the construction, validation,
and execution of block proposals in the Nomos blockchain.
It describes how block proposals contain references to transactions
rather than complete transactions,
compressing the proposal size from up to 1 MB down to 33 kB
to save bandwidth necessary to broadcast new blocks.

**Keywords:** Bedrock, block construction, validation, execution,
leader, transaction, Proof of Leadership

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Definitions

| Terminology | Description |
| ----------- | ----------- |
| Leader | A node elected through the leader lottery to construct a new block. |
| Block Builder | The leader node that constructs a new block proposal. |
| Block Proposer | The leader node that shares the constructed block with other network members. |
| Block Proposal | A message structure containing a header and references to transactions. |
| Proof of Leadership (PoL) | A proof confirming that a node is indeed the elected leader. |
| Transaction Maturity | The assumption that transactions have had enough time to spread across the network. |
| Validator | A node that validates and executes block proposals. |

## High-level Flow

This section presents a high-level description of the block lifecycle.
The main focus of this section is to build an intuition
on the block construction, validation, and execution.

1. A leader is selected. The leader becomes a block builder.

1. The block builder **constructs** a block proposal.

   1. The block builder selects the latest block (parent)
      as the reference point for the chain state update.

   1. The block builder constructs references to the deterministically generated
      Mantle Transactions that execute the [Service Reward Distribution Protocol][service-reward],
      if such transactions can be constructed.
      For example, there is no need to distribute rewards
      when all rewards have already been distributed.

   1. The block builder selects valid Mantle Transactions
      (as defined in [Mantle Specification][mantle-spec])
      from its mempool and includes references to them in the proposal.

   1. The block builder populates the block header of the block proposal.

1. The block proposer sends the block proposal to the Blend network.

1. The validators receive the block proposal.

1. The validators **validate** the block proposal.

   1. They validate the block header.

   1. They verify distribution of service rewards through Mantle Transactions
      as specified in [Service Reward Distribution Protocol][service-reward].
      This is done by independently deriving the distribution transaction
      and confirming that it matches the first reference,
      if there are rewards to be distributed.

   1. They retrieve complete transactions from their mempool
      that are referred in the block.

   1. They validate each transaction included in the block.

1. The validators **execute** the block proposal.

   1. They derive the new blockchain state from the previous one
      by executing transactions as defined in [Mantle Specification][mantle-spec].

   1. They update the different variables that need to be maintained over time.

## Constructions

### Hash

This specification uses two hashing algorithms
that have the same output length of 256 bits (32 bytes)
that are Poseidon2 and Blake2b.

### Block Proposal

A block proposal,
instead of containing complete Mantle Transactions of an unlimited size,
contains references of fixed size to the transactions.
Therefore, the size of the proposal is constant and it is 33129 bytes.

The following message structure is defined:

```python
class Proposal:  # 33129 bytes
    header: Header              # 297 bytes
    references: References      # 32768 bytes
    signature: Ed25519Signature # 64 bytes
```

Where:

- `header` is the header of the proposal; defined below: [Header](#header).
- `references` is a set of 1024 references to transactions of a `hash` type;
  the size of the `hash` type is 32 bytes
  and is the transaction hash as defined in [Mantle Specification - Mantle Transaction][mantle-tx].
- `signature` is the signature of the complete `header` using the `leader_key`
  from the `ProofOfLeadership`;
  the size of the `Ed25519Signature` type is 64 bytes.

> **Note**: The length of the `references` list must be preserved
> to maintain the message's indistinguishability in the Blend protocol.
> Therefore, the list must be padded with zeros when necessary.

### Header

```python
class Header:  # 297 bytes
    bedrock_version: byte             # 1 bytes
    parent_block: hash                # 32 bytes
    slot: SlotNumber                  # 8 bytes
    block_root: hash                  # 32 bytes
    proof_of_leadership: ProofOfLeadership  # 224 bytes
```

Where:

- `bedrock_version` is the version of the proposal message structure
  that supports other protocols defined in [Bedrock Specification][bedrock-spec];
  the size of it is 1 byte and is fixed to `0x01`.
- `parent_block` is the block ID ([Cryptarchia v1 Protocol Specification][cryptarchia-spec])
  of the parent block, validated and accepted by the block builder.
  It is used for the derivation of the `AgedLedger` and `LatestLedger` values
  necessary for validating the PoL;
  the size of the `hash` is 32 bytes.
- `slot` is the consensus slot number;
  the size of the `SlotNumber` type is 8 bytes.
- `block_root` is the root of the Merkle tree constructed from transaction hashes
  (defined in [Mantle Specification - Mantle Transaction][mantle-tx])
  used for constructing the `references` list in the `transactions`;
  the size of the `hash` is 32 bytes.
- `proof_of_leadership` is the proof confirming that the sender is the leader;
  defined below: [Proof of Leadership](#proof-of-leadership).

### Block References

```python
class References:  # 32768 bytes
    service_reward: list[zkhash]        # 1*32 bytes
    mempool_transactions: list[zkhash]  # 1024-len(service_reward)*32 bytes
```

Where:

- `service_reward` is a set of up to 1 reference
  to a reward transaction of a `zkhash` type;
  the size of the `zkhash` type is 32 bytes
  and is the transaction hash as defined in
  [Mantle Specification - Mantle Transaction][mantle-tx].
- `mempool_transactions` is a set of up to 1024 references
  to transactions of a `zkhash` type;
  the size of the `zkhash` type is 32 bytes
  and is the transaction hash as defined in
  [Mantle Specification - Mantle Transaction][mantle-tx].

The `service_reward` transaction is created deterministically by the leader
and is not obtained from the mempool.
If this transaction were obtained from the mempool,
it could expose the leader's identity as the transaction creator.
To protect the leader's identity,
only the `service_reward` reference is included in the proposal,
and it is derived again by the nodes verifying the block.

The `service_reward` transaction is a Service Rewards Distribution Transaction
that distributes service rewards.
It is a Mantle Transaction with no input
and up to `service_count x 4` outputs,
`service_count` being the number of services (global parameter).
The outputs represent the validators rewarded (up to 4 per service).

If the `service_reward` transaction cannot be created,
then nothing is added to the list.
Therefore, the `service_reward` list is allowed to have a length of 0.

### Proof of Leadership

```python
class ProofOfLeadership:  # 224 bytes
    leader_voucher: RewardVoucher       # 32 bytes
    entropy_contribution: zkhash        # 32 bytes
    proof: ProofOfLeadership            # 128 bytes
    leader_key: Ed25519PublicKey        # 32 bytes
```

Where:

- `leader_voucher` is the voucher value
  used for retrieving the reward by the leader for proposal;
  the size of the `RewardVoucher` is 32 bytes.
- `entropy_contribution` is the output of the PoL contribution
  for Cryptarchia entropy;
  the size of the `zkhash` type is 32 bytes.
- `proof` is the proof confirming that the proposal
  is constructed by the leader;
  the size of the `ProofOfLeadership` type is 128 bytes
  (2 compressed G1 and 1 compressed G2 BN256 elements).
- `leader_key` is the one-time `Ed25519PublicKey`
  used for signing the `Proposal`.
  This binds the content of the proposal with the `ProofOfLeadership`;
  the size of the `Ed25519PublicKey` type is 32 bytes.

## Proposal Construction

This section explains how the block proposal structure presented above
is populated by the consensus leader.

The block proposal is constructed by the leader of the current slot.
The node becomes a leader only after successfully generating a valid PoL
for a given `(Epoch, Slot)`.

### Prerequisites

Before constructing the proposal, the block builder must:

1. Select a valid parent block referenced by `ParentBlock`
   on which they will extend the chain.

1. Derive the required Ledger state snapshots `AgedLedger` and `LatestLedger`
   from the state of the chain including the last block.

1. Select a valid unspent note winning the PoL.

1. Generate a valid PoL proving leadership eligibility for `(Epoch, Slot)`
   based on the selected note.
   Attach the PoL to a one-time Ed25519 public key used to sign the block proposal.

Only after the PoL is generated can the block proposal be constructed
(see [Proof of Leadership Specification][pol-spec]).

### Construction Procedure

1. Initialize proposal metadata with the last known state of the blockchain.
   Set the:

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

1. Construct the `service_reward` object:

   1. If there are service rewards to be distributed,
      construct the transaction that distributes
      the service rewards from previous session
      and add its reference to the `service_reward` list.
      This transaction must be computed locally,
      do not disseminate this transaction.

1. Construct the `mempool_transactions` object:

   1. Select Mantle transactions:

      - Choose up to `1024-len(service_reward)` valid `SignedMantleTx`
        from the local mempool.

      - Ensure each transaction:

        - Is valid according to [Mantle Specification][mantle-spec].

        - Has no conflicts with others
          (e.g., two transactions trying to spend the same note).

1. Derive references values:

   ```python
   references: list[zkhash] = [mantle_txhash(tx) for tx in service_reward + mempool_transactions]
   ```

1. Compute the `header.block_root` as the root of the Merkle tree constructed
   from the `list(service_reward) + mempool_transactions` transactions
   used to build `references`.

1. Sign the block proposal header.

   ```python
   signature = Ed25519.sign(leader_secret_key, header)
   ```

1. Assemble the block proposal.

   ```python
   proposal = Proposal( header, references, signature )
   ```

The PoL must have been generated beforehand
and bound to the same Ledger view as mentioned in the [Prerequisites](#prerequisites).

The constructed proposal can now be broadcast to the network for validation.

## Block Proposal Reconstruction

Given a block proposal, this specification assumes *transaction maturity*.
This means that the block proposal must include transactions from the mempool
that have had enough time to spread across the network to reach all nodes.
This ensures that transactions are widely known and recognized
before block reconstruction.

This transaction maturity assumption holds true
because the block proposal must be sent through the Blend Network
before it reaches validators and can be reconstructed.
The Blend Network introduces significant delay,
ensuring that transactions referenced in the proposal
have reached all network participants.

This approach is crucial for maintaining smooth network operation
and reducing the risk that proposals get rejected
due to transactions being unavailable to some validators.
Moreover, by increasing the number of nodes that have seen the transaction,
anonymity is also enhanced as the set of nodes with the same view is larger.
This may result in increased difficulty—or even practical prevention—of
executing deanonymization attacks such as tagging attacks.

Upon receipt of a block proposal,
validators must confirm the presence of all referenced transactions
within their local mempool.
This verification is an absolute requirement—if even a single referenced transaction
is missing from the validator's mempool, the entire proposal must be rejected.
This stringent validation protocol ensures only widely-distributed transactions
are included in the blockchain,
safeguarding against potential network state fragmentation.

The process works as follows:

1. Transaction is added to the node mempool.

1. Node sends the transaction to all its neighbors.

1. Neighbors add the transaction to their own mempools
   and propagate it to their neighbors—transaction
   is gossiped throughout the network.

1. Block builder selects a transaction from its local mempool,
   which is guaranteed to be propagated through the network
   due to steps 1-3.

1. Block builder constructs a block proposal
   with references to selected transactions.

1. Block proposal is sent through the Blend Network,
   which requires multiple rounds of gossiping.
   This introduces a delay that ensures the transaction
   has reached most of the network participants' mempools.

1. Block proposal is received by validators.

1. Validators check their local mempools
   for all referenced transactions from the proposal.

1. If any transaction is missing, the entire proposal is rejected.

1. If all transactions are present,
   the block proposal is reconstructed and proceeds to further validation steps.

## Block Proposal Validation

This section defines the procedure followed by a Nomos node
to validate a received block proposal.

Given a `Proposal`, a proposed block consisting of a `header` and `references`.
This block proposal is considered valid if the following conditions are met:

### Block Validation

The `Proposal` must satisfy the rules defined in
[Cryptarchia v1 Protocol Specification - Block Header Validation][cryptarchia-block-validation].

### Block Proposal Reconstruction Validation

The `references` must refer to either a `service_reward` transaction
that is locally derivable
or to existing `mempool_transaction` entries
that are retrievable from the node's local mempool.

### Mempool Transactions Validation

`mempool_transactions` must refer to a valid sequence
of Mantle Transactions from the mempool.
Each transaction must be valid according to the rules
defined in the [Mantle Specification][mantle-spec].
In order to verify ZK proofs,
they are batched for verification as explained in
[Batch verification of ZK proofs](#batch-verification-of-zk-proofs)
to get better performances.

### Rewards Validation

1. Check if the first reference matches a deterministically derived
   Service Rewards Distribution Transaction
   that distributes previous session service fees
   as defined in [Service Reward Distribution Protocol][service-reward].
   It should take no input and output up to `service_count * 4` reward notes
   distributed to the correct validators.

1. If the above rewarding transactions cannot be derived,
   then the first reference must refer to a `mempool_transaction`.

If any of the above checks fail, the block proposal must be rejected.

## Block Execution

This section specifies how a Nomos node executes a valid block proposal
to update its local state.

Given a `ValidBlock` that has successfully passed proposal validation,
the node must:

1. Append the `leader_voucher` contained in the block to the set of reward vouchers
   **when the following epoch starts**.

1. Execute the Mantle Transactions included in the block sequentially,
   using the execution rules defined in the [Mantle Specification][mantle-spec].

## Annex

### Batch verification of ZK proofs

#### Blob Samples

1. For each sample the verifier follows the classic cryptographic verification procedure
   as described in [NomosDA Cryptographic Protocol - Verification][nomosda-verification]
   except the last step, once the verifier has a single commitment C^(i),
   an aggregated element v^(i) at position u^(i) and one proof π^(i) for each sample.

1. The verifier draws a random value for each sample r_i ← $F_p$.

1. The verifier computes:

   1. C' := Σ(i=1 to k) r_i · C^(i)

   1. v' := Σ(i=1 to k) r_i · v^(i)

   1. π' := Σ(i=1 to k) r_i · π^(i)

   1. u' := Σ(i=1 to k) r_i · u^(i) · π^(i)

1. They test if e(C' - v' · G1 + u', G2) = e(π', τ · G2).

#### Proofs of Claim

1. For each proof of Claim the verifier collects
   the classic Groth16 elements required for verification.
   It includes the proof π^(i), and the public values x_j^(i)
   for each proof of claim.

1. The verifier draws one random value for each proof r_i ← $F_p$.

1. The verifier computes:

   1. π'_j := Σ(i=1 to k) r_i · π_j^(i) for j ∈ {A, B, C}.

   1. r' := Σ(i=1 to k) r_i

   1. IC := r' · Ψ_0 + Σ(j=1 to l) (Σ(i=1 to k) r_i · x_j^(i)) · Ψ_j

1. They test if Σ(i=1 to k) e(r_1 · π'_A, π'_B) = e(r' · [α]_1, [β]_2) + e(IC, [γ]_2) + e(π'_C, [δ]_2).

> **Note**: This batch verification of Groth16 proofs is the same
> as what is described in the Zcash paper, Appendix B.2.

#### ZkSignatures

The verifier follows the same procedure as in [Proofs of Claim](#proofs-of-claim)
but with the Groth16 proofs of ZkSignatures.

## References

### Normative

- [Mantle Specification][mantle-spec] - Mantle transaction specification
- [Cryptarchia v1 Protocol Specification][cryptarchia-spec]
  \- Cryptarchia consensus protocol
- [Bedrock Specification][bedrock-spec] - Bedrock protocol specification
- [Proof of Leadership Specification][pol-spec]
  \- Proof of Leadership specification
- [Service Reward Distribution Protocol][service-reward]
  \- Service reward distribution protocol
- [NomosDA Cryptographic Protocol][nomosda-verification]
  \- NomosDA cryptographic verification

### Informative

- [v1.1 Block Construction, Validation and Execution Specification][origin-ref]
  \- Original specification document
- Poseidon2 - Hash function
- Blake2b - Hash function
- Zcash paper, Appendix B.2 - Batch verification of Groth16 proofs

[mantle-spec]: https://nomos-tech.notion.site/Mantle-Specification
[mantle-tx]: https://nomos-tech.notion.site/Mantle-Specification
[cryptarchia-spec]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification
[cryptarchia-block-validation]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification
[bedrock-spec]: https://nomos-tech.notion.site/Bedrock-Specification
[pol-spec]: https://nomos-tech.notion.site/Proof-of-Leadership-Specification
[service-reward]: https://nomos-tech.notion.site/Service-Reward-Distribution-Protocol
[nomosda-verification]: https://nomos-tech.notion.site/NomosDA-Cryptographic-Protocol
[origin-ref]: https://nomos-tech.notion.site/v1-1-Block-Construction-Validation-and-Execution-Specification-269261aa09df807185a9e0764acffe22

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
