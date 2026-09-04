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
| 1.1.2 | Precise that the maximum block size applies to the block body only. | 2026-07-27 |
| 1.1.3 | Corrected `MAX_BLOCK_SIZE` to 2 MiB, to match the implementation. | 2026-08-05 |
| 1.2.0 | Added the `uncle_headers` field — the signed headers of the referenced uncles — to the [Proposal](#block-proposal) and to the newly defined [Block](#block), and replaced `block_root` with `body_root` in the [Header](#header), which commits to them, signatures included, as well as to the transactions. Due to updated [Cryptarchia Protocol](cryptarchia-v1-protocol.md) (uncle references). | 2026-08-06 |
| 1.2.1 | Precise the state each transaction of a block is validated against: the transactions are validated and executed one after the other in the order they appear, each against the state the preceding ones left, which makes block validity order-dependent. Precise that a block whose validation fails at any point is not executed at all. | 2026-08-24 |
| 1.3.0 | Compressed Block Proposal: 16-byte transaction reference prefixes and a variable-length `references` list, reducing the proposal from 34,574 bytes to at most 18,192. Added the [Canonical Encoding](#canonical-encoding) section. | 2026-08-18 |
| 1.4.0 | Removed the `bedrock_version` header field ([Bedrock Eras](bedrock-eras.md)): the header is 296 bytes, a signed header 360, and the maximum proposal 18,187 bytes. | 2026-09-04 |

# Introduction

In this document, we present the specification defining the construction of the block proposal, its validation, and execution. We define the block proposal construction that contains references to transactions (from the mempool) instead of a complete transaction to limit its length. The raw block body increases with the size of transactions it contains up to `MAX_BLOCK_SIZE`, which is 2 MiB and covers the transactions only, and the proposal compresses its size down to at most ≈18.2 kB (18,187 bytes), which saves the bandwidth necessary to broadcast new blocks.

# Overview

For the consensus protocol to make progress, a new **leader** is elected through the leader lottery. The new leader is in possession of a proof of leadership (PoL) that confirms that it is indeed the leader. The main objective of the leader is to construct a new block, hence becoming a **block builder,** and share it with other members of the network as a **block proposer**. The block must be correctly constructed; otherwise, it will be rejected by the consensus nodes who are validating every block. Only a block that validates in full modifies the state of the chain: the transactions it includes are interpreted by all nodes, one after the other in the order they appear, and the state of the chain is modified according to the instructions embedded in them.

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
   3. They validate each transaction included in the block, in the order the transactions appear, each against the state the preceding ones left.

6. The validators **execute** the block proposal.
   1. They append the `leader_voucher` of the block to the set of reward vouchers, which the following epoch starts with.
   2. They execute the [**Service Reward Distribution Protocol**](bedrock-service-reward-distribution.md) to generate reward notes locally and include them in the ledger.
   3. They derive the new blockchain state from the previous one by executing transactions as defined in [Mantle](bedrock-v1.1-mantle-specification.md), in that same pass, adopting the result only once the whole block has validated.

# Constructions

## Hash

We are using two hashing algorithms that have the same output length of 256 bits (32 bytes) that are [Poseidon2 and Blake2b](common-cryptographic-components.md).

## Block Proposal

A block proposal, instead of containing complete Mantle Transactions of an unlimited size, contains short fixed-size references to the transactions. It also carries the full signed headers of the uncles it references, so that every node holding the block holds those headers as well. Its size therefore varies with both the number of referenced transactions and the number of referenced uncles: from 363 bytes, up to the maximum of 18,187 bytes at `MAX_BLOCK_TXS` references and `MAX_UNCLES` uncles. The indistinguishability of proposals required by the [Blend Protocol](blend-protocol.md) is provided at the message layer: every dispersed proposal is padded up to the maximum payload size `Max_Body_Length = 18187` bytes — set from the maximum proposal size — by [Payload Formatting](payload-formatting.md).

We define the following message structure:

```python
class Proposal:                              # 363..18187 bytes
    header: Header                           # 296 bytes
    uncle_headers: list[SignedHeader]        # 1 + u * 360 bytes, u <= MAX_UNCLES
    references: References                   # 2..16386 bytes (2-byte count + entries)
    signature: Ed25519Signature              # 64 bytes

class SignedHeader:                          # 360 bytes
    header: Header                           # 296 bytes
    signature: Ed25519Signature              # 64 bytes
```

Where:

- `header` is the header of the proposal; defined below: [Header](#header).
- `uncle_headers` is a variable-size list carrying the full signed headers of the referenced uncles, with at most `MAX_UNCLES` entries. Each entry holds an uncle block header together with the signature of that header under its `leader_key` — the header and signature as originally received with the uncle's own proposal. This list *is* the reference: the block ID ([Cryptarchia Protocol](cryptarchia-v1-protocol.md#block-id)) of an uncle is derived from its carried header and is not recorded separately. Like every list, it is serialized as a 1-byte little-endian element count followed by that many entries, and a decoder must reject a count exceeding `MAX_UNCLES`. The `uncles` field having been removed from the [Header](#header), each entry is a fixed 360 bytes — a 296-byte header plus a 64-byte signature — so the list of carried headers parses unambiguously from its element count alone. The whole list, signatures included, is committed by `header.body_root` and therefore by the block ID, so no two blocks sharing an ID can differ in a carried signature. The proposal length reveals how many uncles are referenced — proposal indistinguishability is provided by the message-layer padding of [Payload Formatting](payload-formatting.md), not by the encoding. The proposer chooses which uncles to reference according to [Uncle Selection](cryptarchia-v1-protocol.md#uncle-selection), and every entry must satisfy the validity rules of [Uncle References](cryptarchia-v1-protocol.md#uncle-references) or the block is rejected. The same list is carried over into the reconstructed [Block](#block), which is what makes every referenced uncle structurally available: those rules can be evaluated by any node holding the chain, including nodes bootstrapping from genesis that never receive the proposal.
- `references` is a variable-length list of up to `MAX_BLOCK_TXS` [references](#references) to transactions, each being a 16-byte (`REFERENCE_PREFIX_LENGTH`) prefix of the transaction hash defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction).
- `signature` is the signature of the complete `header` using the `leader_key` from the `ProofOfLeadership`; the size of the `Ed25519Signature` type is 64 bytes.

The proposal carries no padding of its own. Proposal indistinguishability is provided at the message layer: [Payload Formatting](payload-formatting.md#body) already mandates a fixed body length (`Max_Body_Length`) for every dispersed payload, with shorter messages padded with **random** data and the true length carried in `body_length`. An in-proposal zero-padded layout would duplicate that guarantee while charging every proposal the full `MAX_BLOCK_TXS` cost even when it references few transactions. The padding lies outside the signed proposal and is discarded via `body_length` on decapsulation, so no consensus meaning ever attaches to it.

Note that this makes the random-padding requirement of [Payload Formatting](payload-formatting.md#body) load-bearing for the first time. While the proposal was a constant size it always filled the body exactly and the padding path never fired for a real proposal. Implementations must pad with random data, not zeros, or the padding region will itself distinguish proposals by their reference count.

### Header

```python
class Header:                                # 296 bytes
    parent_block: hash                       # 32 bytes
    slot: SlotNumber                         # 8 bytes
    body_root: hash                          # 32 bytes
    proof_of_leadership: ProofOfLeadership   # 224 bytes
```

Where:

- `parent_block` is the block ID ([Cryptarchia Protocol](cryptarchia-v1-protocol.md)) of the parent block, validated and accepted by the block builder. It is used for the derivation of the `AgedLedger` and `LatestLedger` values necessary for validating the PoL; the size of the `hash` is 32 bytes.
- `slot` is the consensus slot number; the size of the `SlotNumber` type is 8 bytes.
- `body_root` is the commitment to the block body — both the carried `uncle_headers` and the transactions. It is computed as defined in step 3 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation), which combines the serialized `uncle_headers` list with the root of the Merkle tree constructed from the **full** transaction hashes (defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction)) — the same hashes used for constructing the `mempool_transactions` references list; the size of the `hash` is 32 bytes. Because that Merkle root is taken over the full hashes, `body_root` uniquely binds the proposal to a specific ordered transaction selection even when two transactions share the same `references` prefix, and it also binds the *number* of references; see [Binding of the reference list](#binding-of-the-reference-list). Since the block ID is taken over the header, committing the uncle headers here is what makes two blocks with the same ID identical byte for byte.
- `proof_of_leadership` is the proof confirming that the sender is the leader; defined below: [Proof of Leadership](#proof-of-leadership).

### References

Each reference is a fixed-length prefix of the transaction hash rather than the full hash. The prefix length is the protocol parameter `REFERENCE_PREFIX_LENGTH = 16` bytes, and the prefix is taken by:

```python
REFERENCE_PREFIX_LENGTH = 16   # bytes

def prefix(hash_input: bytes, length: int) -> bytes:
    return hash_input[:length]
```

```python
class References:                            # 2..16386 bytes
    mempool_transactions: list[bytes]        # UINT16 count + len * REFERENCE_PREFIX_LENGTH
```

Where `mempool_transactions` is a variable-length list of up to `MAX_BLOCK_TXS` references to transactions, each being `prefix(mantle_txhash(tx), REFERENCE_PREFIX_LENGTH)` of the transaction hash defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction).

The list is not padded. As specified in [Canonical Encoding](#canonical-encoding), it is serialized as a 2-byte little-endian element count followed by that many `REFERENCE_PREFIX_LENGTH`-byte entries, so its encoded size is `2 + len(mempool_transactions) * REFERENCE_PREFIX_LENGTH` bytes — 2 bytes when the proposal references no transaction, and `2 + 1024 * 16 = 16386` bytes at `MAX_BLOCK_TXS`.

A decoder must reject a count greater than `MAX_BLOCK_TXS` **before** allocating for it or performing any mempool lookup, on every ingress path.

### Proof of Leadership

```python
class ProofOfLeadership:                     # 224 bytes
    proof: Groth16Proof                      # 128 bytes
    entropy_contribution: zkhash             # 32 bytes
    leader_key: Ed25519PublicKey             # 32 bytes
    leader_voucher: RewardVoucher            # 32 bytes
```

Where:

- `proof` is the proof confirming that the proposal is constructed by the leader; the size of the `Groth16Proof` type is 128 bytes (2 compressed $`\mathbb{G}_1`$and 1 compressed $`\mathbb{G}_2`$ BN256 elements).
- `entropy_contribution` is the output of the PoL contribution for Cryptarchia entropy; the size of the `zkhash` type is 32 bytes.
- `leader_key` is the one-time `Ed25519PublicKey` used for signing the `Proposal`. This binds the content of the proposal with the `ProofOfLeadership`; the size of the `Ed25519PublicKey` type is 32 bytes.
- `leader_voucher` is the voucher value used for retrieving the reward by the leader for proposal; the size of the `RewardVoucher` is 32 bytes.

> **Field order.** The order above is the **wire** order, i.e. the order in which these fields are concatenated by [Canonical Encoding](#canonical-encoding). The `block_id` preimage in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#block-id) absorbs the same four fields in a *different* order (`leader_voucher`, `entropy_contribution`, `proof`, `leader_key`). This is deliberate, not an inconsistency: `block_id` is a domain-separated enumeration of header fields rather than a re-serialization of the header, so the two orders are independent and both are normative. Changing either one changes a different thing — the wire format in the first case, block identity in the second.

## Canonical Encoding

This section defines the byte-level wire format of the block proposal. It follows the same conventions as the [Mantle Transaction Encoding](mantle-transaction-encoding.md), in particular *"All multi-byte integers use little-endian encoding"* and *"Any lists are length-prefixed with fixed width uints"*, and reuses its primitive terminals rather than redefining them.

The encoding is canonical: every valid proposal has exactly one byte representation, and every byte string decodes to at most one proposal. The following rules are normative.

1. All multi-byte integers are little-endian.
2. The fields of a structure are concatenated in the order in which they are declared, with no separators, no alignment padding, and no per-field framing.
3. A list is encoded as a fixed-width little-endian element count followed by that many elements, each encoded individually. The width is given per list below — a `UINT16` for `References`, a single byte for `UncleHeaders`, whose `MAX_UNCLES` bound one byte covers — following the [Mantle Transaction Encoding](mantle-transaction-encoding.md) convention that lists are *"length-prefixed with fixed width uints"*. The count must not exceed the list's declared bound.
4. Decoding must consume the input exactly. A decoder must reject input that ends before the structure is complete, and must equally reject input with bytes remaining after it. Accepting trailing bytes would allow two distinct wire messages to decode to the same proposal, which is a parser differential and therefore a consensus-split risk.

```schema
Proposal          = Header UncleHeaders References Ed25519Signature

Header            = ParentBlock Slot BodyRoot ProofOfLeadership
ParentBlock       = Hash32
Slot              = UINT64
BodyRoot          = Hash32

UncleHeaders      = UncleCount *SignedHeader
UncleCount        = Byte            ; MUST NOT exceed MAX_UNCLES
SignedHeader      = Header Ed25519Signature

ProofOfLeadership = Groth16 EntropyContribution LeaderKey LeaderVoucher
EntropyContribution = FieldElement
LeaderKey         = Ed25519PublicKey
LeaderVoucher     = FieldElement

References        = ReferenceCount *Reference
ReferenceCount    = UINT16          ; MUST NOT exceed MAX_BLOCK_TXS
Reference         = 16BYTE          ; REFERENCE_PREFIX_LENGTH bytes
```

The terminals `Byte`, `UINT16`, `UINT64`, `Hash32`, `FieldElement`, `Groth16`, `Ed25519PublicKey` and `Ed25519Signature` are those defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md#common-structures). Note in particular that `FieldElement` is a little-endian BN254 field element, which fixes the byte order of `entropy_contribution` and `leader_voucher`.

This yields the following sizes, where `n` is the number of references:

| Structure | Encoded size | Minimum | Maximum |
| --- | --- | --- | --- |
| `Header` | `32 + 8 + 32 + 224` | 296 | 296 |
| `ProofOfLeadership` | `128 + 32 + 32 + 32` | 224 | 224 |
| `SignedHeader` | `296 + 64` | 360 | 360 |
| `UncleHeaders` | `1 + 360u` | 1 | 1,441 |
| `References` | `2 + 16n` | 2 | 16,386 |
| `Proposal` | `296 + (1 + 360u) + (2 + 16n) + 64` | 363 | 18,187 |

The maximum of 18,187 bytes, at `n = MAX_BLOCK_TXS` references and `u = MAX_UNCLES` uncles, is what [Payload Formatting](payload-formatting.md#body) uses as `Max_Body_Length`.

## Block

A **block** is what a proposal becomes once its references have been resolved against the mempool, and it is the unit that nodes store, execute and serve to their peers — in particular over [Downloading Blocks](cryptarchia-v1-bootstr-sync.md#downloading-blocks) during synchronization, where proposals are never transferred.

```python
class Block:
    header: Header                           # 296 bytes
    signature: Ed25519Signature              # 64 bytes
    uncle_headers: list[SignedHeader]        # 1 + n × 360 bytes, n <= MAX_UNCLES
    transactions: list[SignedMantleTx]       # up to MAX_BLOCK_SIZE
```

Where:

- `header` is the header of the proposal the block was reconstructed from, unchanged; defined above: [Header](#header).
- `signature` is the proposal signature over that `header`, carried over unchanged. It is retained because `block_id` commits to the header alone and therefore does not cover the signature, so a node that receives the block without ever seeing the proposal — as happens during synchronization — would otherwise have nothing to check against step 8 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation); the size of the `Ed25519Signature` type is 64 bytes.
- `uncle_headers` is the list carried over verbatim from the proposal, defined above: [Block Proposal](#block-proposal). It is committed by `header.body_root`, so it cannot be altered, reordered or truncated without changing the block ID, and every entry must satisfy the validity rules of [Uncle References](cryptarchia-v1-protocol.md#uncle-references) for the block to be valid.
- `transactions` is the sequence of Mantle Transactions resolved from `references` during [Block Proposal Reconstruction](#block-proposal-reconstruction).

The `uncle_headers` list is part of the block rather than only of the proposal because both [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) and the [Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference) need it. A node that obtained the chain by synchronizing from its peers — which transfers blocks, not proposals — would otherwise hold no record of the referenced uncles at all: it could not apply the validity rules of [Uncle References](cryptarchia-v1-protocol.md#uncle-references) to the blocks it downloads, could not compute $`N_\text{BLOCKS}`$, and therefore could not derive the difficulty $`D`$ that gates Proof-of-Leadership validity in the following epoch. Carrying the list in the block makes both the validation and the inference reproducible from chain data alone, for a bootstrapping node exactly as for a node that followed the chain live.

As with the header, `uncle_headers` does not count towards `MAX_BLOCK_SIZE`, which bounds the block body — the serialized `transactions` — only. The uncle payload is bounded independently by `MAX_UNCLES` entries per block.

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
    - `parent_block`
    - `slot`
    - `body_root` — left unset here; it is computed in step 4, once both parts of the body are known
    - `proof_of_leadership`:
      - `leader_voucher`
      - `entropy_contribution`
      - `proof`
      - `leader_key`
  - `uncle_headers`: the full signed headers — header and signature as received with the uncle's own proposal — of the uncles chosen by [Uncle Selection](cryptarchia-v1-protocol.md#uncle-selection), in selection order. Every entry must satisfy the validity rules of [Uncle References](cryptarchia-v1-protocol.md#uncle-references) against the chain the proposal extends, or the resulting block will be rejected; because those rules read only that chain and the entry itself, the proposer can verify this before publishing.

2. Construct the `mempool_transactions` object:
1. Select Mantle transactions:
    - Choose up to `MAX_BLOCK_TXS` valid `SignedMantleTx` from the local mempool.
    - Ensure the selected transactions, in the order they are placed in, form a sequence that is valid under [Block Proposal Validation](#block-proposal-validation).

  No prefix-collision avoidance is needed at selection time. At `REFERENCE_PREFIX_LENGTH = 16` a collision between two distinct transaction hashes is infeasible to encounter or to manufacture (see [Prefix length and collision resistance](#prefix-length-and-collision-resistance)), so a 16-byte prefix identifies a transaction as unambiguously as the full hash does for reconstruction purposes.

3. Derive references values:
```python
references: list[bytes] = [prefix(mantle_txhash(tx), REFERENCE_PREFIX_LENGTH)
                           for tx in mempool_transactions]
```

4. Compute the `header.body_root` over both parts of the body, as defined in step 3 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation): the serialized `uncle_headers` list from step 1, combined with the root of the Merkle tree constructed over the full transaction hashes of the selected transactions used to build `references`. The `references` list is left exactly as long as the selection; it is not padded. This step therefore comes after both uncle selection and transaction selection.
5. Sign the block proposal header, where `header` is its canonical encoding as defined in [Canonical Encoding](#canonical-encoding) — the 296 bytes of the header alone, without `uncle_headers`, without `references` and without the signature itself.
```text
signature = Ed25519.sign(leader_secret_key, header)
```

6. Assemble the block proposal.
```python
proposal = Proposal(
    header,
    uncle_headers,
    references,
    signature
)
```

  The PoL must have been generated beforehand and bound to the same Ledger view as mentioned in the [Prerequisites](#prerequisites).

The constructed proposal can now be broadcast to the network for validation.

## Block Proposal Reconstruction

Given a block proposal, we assume *transaction maturity*. This means that the block proposal must include transactions from the mempool that have had enough time to spread across the network to reach all nodes. This ensures that transactions are widely known and recognized before block reconstruction.

This transaction maturity assumption holds true because the block proposal must be sent through the Blend Network before it reaches validators and can be reconstructed. The Blend Network introduces significant delay, ensuring that transactions referenced in the proposal have reached all network participants. This approach is crucial for maintaining smooth network operation and reducing the risk that proposals get rejected due to transactions being unavailable to some validators. Moreover, by increasing the number of nodes that have seen the transaction, anonymity is also enhanced as the set of nodes with the same view is larger. This may result in increased difficulty—or even practical prevention—of executing deanonymization attacks such as tagging attacks.

Upon receipt of a block proposal, validators must confirm the presence of all referenced transactions within their local mempool. This verification is an absolute requirement—if even a single referenced transaction is missing from the validator's mempool, that validator must reject the proposal. This stringent validation protocol ensures only widely-distributed transactions are included in the blockchain, safeguarding against potential network state fragmentation. The check is against a local mempool, so see [Reference Resolution](#reference-resolution) for what such a rejection does and does not establish about the block.

The process works as follows:

1. Transaction is added to the node mempool.
2. Node sends the transaction to all its neighbors.
3. Neighbors add the transaction to their own mempools and propagate it to their neighbors—transaction is gossiped throughout the network.
4. Block builder selects a transaction from its local mempool, which is guaranteed to be propagated through the network due to steps 1-3.
5. Block builder constructs a block proposal with references to selected transactions.
6. Block proposal is sent through the Blend Network, which requires multiple rounds of gossiping. This introduces a delay that ensures the transaction has reached most of the network participants' mempools.
7. Block proposal is received by validators.
8. Validators match each reference prefix in `references` against the transactions in their local mempool.
9. If every reference resolves to a mempool transaction and the resolved set reproduces `header.body_root`, the block proposal is reconstructed and proceeds to further validation steps; otherwise the validator rejects it, without that being a finding of invalidity — see [Reference Resolution](#reference-resolution).

### Reference Resolution

A reference is a 16-byte (`REFERENCE_PREFIX_LENGTH`) prefix of the transaction hash. Because two distinct transaction hashes cannot be made or found to share a 16-byte prefix at any feasible cost (see [Prefix length and collision resistance](#prefix-length-and-collision-resistance)), a validator resolves each reference to exactly one local mempool transaction:

```python
def resolve(reference, mempool):
    matches = [tx for tx in mempool
               if prefix(mantle_txhash(tx), REFERENCE_PREFIX_LENGTH) == reference]
    return matches[0] if len(matches) == 1 else None
```

A reference resolves only when the match is unique. Zero matches means the transaction is absent locally; two or more would mean a prefix collision, which is infeasible to manufacture and vanishingly unlikely to occur by chance, and is treated as unresolved rather than searched, so that resolution never branches. Because the match is unique when it exists, the result does not depend on the order in which the mempool is scanned.

Reconstruction considers every entry of `references`; the list has no padding. Nothing in the encoding forbids the same reference appearing more than once: each occurrence resolves independently to the same transaction, the reconstructed sequence contains that transaction more than once, and `header.body_root` decides — as for any sequence — whether that is what the proposer committed to. Whether such a sequence is *valid* is not a reconstruction question; it is decided by [Mantle](bedrock-v1.1-mantle-specification.md) transaction validation and execution, where a repeated transaction conflicts with itself, spending the same notes twice. A proposal whose reference count exceeds `MAX_BLOCK_TXS` is rejected at decode time, as specified in [References](#references). The proposal is reconstructed when every reference resolves to a transaction and the body root over the carried `uncle_headers` and the resolved transactions' full hashes reproduces `header.body_root`; otherwise it is rejected. Resolution is a function of the proposal and the validator's mempool alone, so two validators holding the same mempool always reach the same decision.

A reference resolving to no local transaction means the referenced transaction has not reached this validator's mempool, which the transaction maturity assumption above is designed to prevent. The validator rejects the proposal and does not build on it. It **must not** record that outcome as a verdict on `block_id`: the block may be received again, in full, through chain synchronisation, and is then validated on its merits. This is unlike a failure implied by the header bytes alone — an invalid proof of leadership — which condemns the block the header names, identically at every node, and is final. Note that not every mempool-independent failure is of that kind: a frame that does not decode or a bad `signature` condemns only the received copy, because the bytes at fault lie outside the header that `block_id` is computed from. [Block Proposal Validation](#block-proposal-validation) states the full classification.

The `header.body_root` check is what makes resolution safe against the residual, cryptographically-negligible case of a prefix matching the wrong transaction: a mismatched set never reproduces the root.

### Binding of the reference list

Neither the reference entries nor their count are covered by `signature` or by `block_id`, both of which range over `header` only. `header.body_root` is therefore the **sole** mechanism binding a proposal to its reference list and to the number of references: any altered reference set, and any altered count, fails to reproduce `header.body_root` and the proposal is rejected. The argument is given in [Why `body_root` alone binds the reference list](#why-body_root-alone-binds-the-reference-list).

Two operational consequences follow:

- Tampered copies of a genuine proposal are cheap to produce, since `references` is unauthenticated. `block_id` is computable from the 296-byte header alone and is shared by every variant of one proposal, which cuts both ways: once a copy has been **accepted**, every later copy carrying that `block_id` can be dropped at a glance, collapsing all tampered variants into a single unit of reconstruction work — but a *rejected* copy must not suppress later ones, or the first tampered variant to arrive would censor the genuine proposal behind it. Duplicate suppression on `block_id` is therefore keyed on acceptance, never on receipt.
- Reconstruction must not be the first expensive step. It is a mempool scan, so it should follow signature and PoL verification, and an unauthenticated proposal must be discarded before any mempool scanning takes place.

Reconstruction assembles the [Block](#block) from the proposal's `header` and `signature`, its `uncle_headers` copied over verbatim, and the transactions resolved from `references` in the order the references appear. The `uncle_headers` list is retained rather than discarded: it is not recoverable from the mempool, it is committed by `header.body_root` and so cannot be dropped without invalidating the block, and once the proposal has been consumed the block is the only carrier of the signed uncle headers that [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) and the [Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference) need.

## Block Proposal Validation

This section defines the procedure followed by a Logos Blockchain node to validate a received block proposal.

Given a `proposal`, a proposed block consisting of a `header`, `uncle_headers`, `references` and a `signature`. This block proposal is considered valid if the following conditions are met, checked **in the order given** so that the cheapest checks discard a malformed or unauthenticated proposal first.

The order is constrained as well as economical. [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) is defined over a block $`B = (header, transactions)`$, but a proposal carries `references` rather than transactions, so the rules that range over `transactions` cannot be evaluated until reconstruction has produced them. They are therefore applied in the step where their operand exists, and each is named below.

1. **Decoding**
  The received bytes must decode to a `proposal` under [Canonical Encoding](#canonical-encoding): the frame must be consumed exactly, with no trailing bytes, the `references` element count must not exceed `MAX_BLOCK_TXS`, and the `uncle_headers` element count must not exceed `MAX_UNCLES`. These checks precede any allocation proportional to a count and any mempool lookup. Because reconstruction produces exactly one transaction per reference, the first of them also discharges rule 2 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation), `length(transactions) <= MAX_BLOCK_TXS`.

2. **Header Validation**
  The `header` must satisfy the rules of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) that range over the header and the block tree alone: the slot ordering against the parent, the wallclock check, the presence of the parent in the block tree, the height against the latest immutable block, and the leader's right to propose — that is, rules 4 through 8. These need no mempool access, and rule 8 covers `signature` and the proof of leadership, so an unauthenticated proposal is discarded here, before any mempool scanning.

3. **Uncle Validation**
  Every entry of `uncle_headers` must be a valid uncle of the block, which is rule 9 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) (see [Uncle References](cryptarchia-v1-protocol.md#uncle-references)). Like the previous step this reads only the chain being extended and the carried entry, so it needs no mempool access and precedes reconstruction. At this point the carried entries are not yet authenticated: `signature` does not cover them, and they are bound to the header only by `header.body_root`, which is not checked until the next step. A failure here therefore condemns the received copy, not the block — it is handled exactly like a reconstruction failure, with no verdict recorded against `block_id`. A finding that the *block* carries an invalid uncle requires entries whose binding has been confirmed: a full block obtained through chain synchronisation, whose `body_root` is checkable immediately, is judged by rule 9 on its merits.

4. **Block Proposal Reconstruction**
  Every `references` prefix must resolve to a local mempool transaction, as defined in [Reference Resolution](#reference-resolution), and the body root computed over the carried `uncle_headers` and the resolved transactions must equal `header.body_root`. This step produces `transactions` and discharges rule 3 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation). A mismatch here means the message was corrupted in transit or malformed by its proposer, not that the block it names is invalid. Corruption of the header itself cannot reach this step — it would have failed the signature check in step 2 — so a mismatching copy has a genuine header over a tampered or damaged body, and carries the **same** `block_id` as the block it names. When that block is genuine, its well-formed bytes are held by the proposer and by every node that accepted it, and the proposal may be re-requested from any of them. That shared identity is exactly why no verdict about the block may be recorded from the mismatch: condemning the `block_id` of a corrupted copy would condemn the genuine block with it.

5. **Block Body Validation**
  With `transactions` now available, the remaining rule of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) applies: rule 1, `bytes(transactions) <= MAX_BLOCK_SIZE`.

6. **Mempool Transactions Validation**
  `mempool_transactions` must refer to a valid sequence of Mantle Transactions from the mempool. The transactions are validated in the order the `references` resolve them, against a state that advances with them: each transaction is validated against the state the transactions preceding it left, the first one against the state the block inherits once the steps of [Block Execution](#block-execution) that precede it have been applied. Each transaction must be valid in that state according to the rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md#validation), which validates and executes its Operations along that same progression. Validation and execution are therefore one pass over one state, not two.

  Block validity is consequently order-dependent, and the order the transactions appear in is normative. Two transactions consuming the same note make the block invalid whatever their order, since the second consumption finds the note gone; a transaction consuming a note an earlier transaction created is valid in that order and invalid in the reverse one.

  In order to verify ZK proofs, they are batched for verification as explained in [Batch verification of ZK proofs](#batch-verification-of-zk-proofs) to get better performance. Batching covers the proof checks alone and does not change the state a transaction is validated in: the public inputs of every proof are taken from the state its transaction is reached in, and the state-dependent assertions still run in sequence.

If any of the above checks fail, the block proposal must be rejected. What the rejection establishes depends on which bytes the failed check read. `block_id` is computed from the 296-byte header alone, so every byte outside the header — `uncle_headers`, `references`, `signature`, trailing bytes — can be altered in a copy without changing the `block_id` it names, and none of those bytes are authenticated until `header.body_root` is confirmed in step 4. A failure detected in them is a property of the received copy, not of the block: a frame that does not decode (step 1), a bad `signature` (step 2), an invalid uncle entry (step 3) and a failure to reconstruct (step 4) each discard the copy **without** recording a verdict against `block_id`. Only a failure implied by the header bytes themselves — an invalid proof of leadership — condemns the block the header names, identically at every node. Treating any of the former as final would let an attacker censor a genuine block by circulating tampered copies of it: one flipped bit in the trailing `signature`, or one substituted uncle entry, leaves `block_id` unchanged. The mempool-dependence of step 4 adds one further distinction — a reference that fails to resolve locally may resolve at another node — described in [Reference Resolution](#reference-resolution). Independently of what a rejection establishes about the block, **nothing of the proposal is executed**. The state progression the pass builds is a working one, adopted as the new chain state only once the last transaction of the block has validated: a single failed check anywhere in the block, in any transaction, in any Operation of any transaction, invalidates the whole block, so a node rejecting it holds exactly the state it held before it started processing it.

This ordering is specific to the proposal path. A block received in full through chain synchronisation carries its transactions from the start, so [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) applies to it as written, with no ordering constraint.

## Block Execution

This section specifies how a Logos Blockchain node executes a valid block proposal to update its local state.

Given a `ValidBlock` that has successfully passed proposal validation, the node must, in this order:

1. Append the `leader_voucher` contained in the block to the set of reward vouchers **when the following epoch starts**.
2. Execute the reward distribution protocol defined in [**Service Reward Distribution Protocol**](bedrock-service-reward-distribution.md) to generate reward notes locally and include them in the ledger.
3. Execute the Mantle Transactions included in the block in the order they appear, using the execution rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md).

Steps 1 and 2 read the epoch and the state of the [Service Declaration Protocol](bedrock-service-declaration-protocol.md), never the transactions of the block, which is what lets them run before those transactions are validated and makes the reward notes of step 2 available to them.

The three steps stand or fall together, on a block that has validated in full: a block that fails validation at any point is not executed at all. The voucher of step 1 is appended to the set the following epoch starts with, so it lands at the epoch boundary rather than with the other two.

The carried `uncle_headers` are not executed. A referenced uncle is not part of the chain; therefore, its transactions have no effect on the ledger state. The uncles are used only as evidence of consensus participation for the [Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference).

# Annex

## Prefix length and collision resistance

`REFERENCE_PREFIX_LENGTH = 16` is chosen so that a collision between two 16-byte prefixes cannot be manufactured. Two distinct attacks have to be priced separately, because they cost very differently.

Write $`b = 8 \cdot`$ `REFERENCE_PREFIX_LENGTH` for the prefix length in bits, so $`b = 128`$ at the chosen parameter.

**Targeted collision.** To make a reference resolve to the wrong transaction — for example to censor one specific transaction `T` — an attacker must produce a transaction whose prefix equals `T`'s. That is a fixed target, matched with probability $`2^{-b}`$ per attempt, so it costs ≈ $`2^{b} = 2^{128}`$ work: infeasible by an enormous margin.

**Self-collision.** To merely create *ambiguity* — two transactions sharing a prefix, so a reference matches more than one — the attacker does not need a specific target. They generate their own candidate transactions and wait for any two to collide. This is a birthday search, which finds a colliding pair after only ≈ $`2^{b/2}`$ candidates rather than $`2^{b}`$: the number of candidate *pairs* grows as the square of the number of candidates, so a collision appears once $`N^2/2 \approx 2^{b}`$, i.e. $`N \approx 2^{b/2}`$. Grinding a candidate is cheap — `mantle_txhash` covers the `MantleTx` alone and not the `op_proofs` of the enclosing `SignedMantleTx`, so each candidate costs one encoding and one hash, and nothing is signed until a pair is found.

The self-collision cost is the one that governs the parameter, because it is the cheaper of the two and it is what an attacker needs to force reconstruction failures. At the 8-byte prefix of an earlier revision ($`b = 64`$) it was only ≈ $`2^{32}`$ — under a second of GPU hashing — which is why that revision needed a construction-side ambiguity bound and a validator-side reconstruction cap to survive grindable collisions. At 16 bytes the birthday cost is ≈ $`2^{64}`$: about 58 years on one GPU at $`10^{10}`$ hashes per second, and still ~214 days against a 100× adversary. Manufacturing even a single ambiguous pair is therefore infeasible, and the whole class of grinding attacks disappears along with the machinery that managed it. Every reference resolves to exactly one transaction, reconstruction is a deterministic lookup, and `header.body_root` remains the backstop for the residual, cryptographically-negligible random collision.

The cost is that references are twice as long as at 8 bytes, so the maximum proposal grows by 8,192 bytes. That still leaves it at 18,187 bytes against the 34,569 of a full-hash layout carrying the same uncles — a ≈1.9× reduction — and it buys reconstruction that no adversary can perturb — for a consensus structure, the stronger property is worth the bytes.

## Why `body_root` alone binds the reference list

This annex substantiates [Binding of the reference list](#binding-of-the-reference-list).

It is not the case that tampering with `references` is caught by the signature. An attacker who truncates or extends the list and adjusts the 2-byte count to match produces a frame that is still well-formed and whose header bytes are untouched, so `signature` still verifies. Framing gives unambiguity, not tamper-detection.

What rules the tampering out is `body_root`. It is a domain-separated hash over the serialized `uncle_headers` and the Merkle root of the transaction hashes ([Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation)), so by collision-resistance of that outer hash it binds the Merkle root exactly, and the Merkle root binds the transaction set in two steps:

1. The Merkle root is taken over the **full** 32-byte transaction hashes, with the leaf set padded to the next power of two using all-zero leaves. Changing the number of leaves across a power-of-two boundary changes the depth of the tree and therefore the root.
2. Within a boundary, an added leaf would have to hash to the all-zero value to leave the root unchanged. Reconstruction rejects any reference that resolves to no mempool transaction, so every leaf must be the hash of a real Mantle Transaction, and producing one whose hash is all-zero is infeasible.

Relative to a design that carries the count in the signed header, this removes one of two independent mechanisms rather than adding one: the count would be bound both by the signature and by `body_root`, and is now bound by `body_root` alone. That is an acceptable trade because the count is not a security binding. Its only role is to remove the parsing ambiguity between a genuine all-zero reference and zero padding, and an explicit length prefix removes that ambiguity directly, at the same cost in bytes and without a fixed-size layout.

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
