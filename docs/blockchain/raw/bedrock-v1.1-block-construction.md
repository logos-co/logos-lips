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
| 1.3.0 | Compressed Block Proposal: 16-byte transaction reference prefixes and a variable-length `references` list, reducing the proposal from 34,574 bytes to at most 18,192. Added the [Canonical Encoding](#canonical-encoding) section. | 2026-08-18 |
| 1.4.0 | Revised compression: replaced the 16-byte unkeyed hash prefixes with 8-byte keyed short transaction IDs — SipHash-2-4 under a per-proposal key derived from signed header fields — with a builder-side collision pre-check and a bounded-ambiguity reconstruction (`MAX_RECONSTRUCTION_COMBINATIONS`). The maximum proposal falls from 18,192 to 10,000 bytes. | 2026-08-20 |

# Introduction

In this document, we present the specification defining the construction of the block proposal, its validation, and execution. We define the block proposal construction that contains references to transactions (from the mempool) instead of a complete transaction to limit its length. The raw block body increases with the size of transactions it contains up to `MAX_BLOCK_SIZE`, which is 2 MiB and covers the transactions only, and the proposal compresses its size down to at most 10 kB (10,000 bytes), which saves the bandwidth necessary to broadcast new blocks.

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

In addition to these cryptographic hashes, the short transaction IDs of the [References](#references) use SipHash-2-4 ([Aumasson–Bernstein, 2012](https://eprint.iacr.org/2012/351)) — a keyed 64-bit pseudorandom function for short inputs, not a general-purpose cryptographic hash. Its 128-bit key is derived per proposal from header fields using Blake2b, so Blake2b remains the only cryptographic hash in the construction; why a PRF suffices for the references is established in [Short ID keying and collision resistance](#short-id-keying-and-collision-resistance).

## Block Proposal

A block proposal, instead of containing complete Mantle Transactions of an unlimited size, contains short fixed-size references to the transactions. It also carries the full signed headers of the uncles it references, so that every node holding the block holds those headers as well. Its size therefore varies with both the number of referenced transactions and the number of referenced uncles: from 364 bytes, up to the maximum of 10,000 bytes at `MAX_BLOCK_TXS` references and `MAX_UNCLES` uncles. The indistinguishability of proposals required by the [Blend Protocol](blend-protocol.md) is provided at the message layer: every dispersed proposal is padded up to the maximum payload size `Max_Body_Length = 10000` bytes — set from the maximum proposal size — by [Payload Formatting](payload-formatting.md).

We define the following message structure:

```python
class Proposal:                              # 364..10000 bytes
    header: Header                           # 297 bytes
    uncle_headers: list[SignedHeader]        # 1 + u * 361 bytes, u <= MAX_UNCLES
    references: References                   # 2..8194 bytes (2-byte count + entries)
    signature: Ed25519Signature              # 64 bytes

class SignedHeader:                          # 361 bytes
    header: Header                           # 297 bytes
    signature: Ed25519Signature              # 64 bytes
```

Where:

- `header` is the header of the proposal; defined below: [Header](#header).
- `uncle_headers` is a variable-size list carrying the full signed headers of the referenced uncles, with at most `MAX_UNCLES` entries. Each entry holds an uncle block header together with the signature of that header under its `leader_key` — the header and signature as originally received with the uncle's own proposal. This list *is* the reference: the block ID ([Cryptarchia Protocol](cryptarchia-v1-protocol.md#block-id)) of an uncle is derived from its carried header and is not recorded separately. Like every list, it is serialized as a 1-byte little-endian element count followed by that many entries, and a decoder must reject a count exceeding `MAX_UNCLES`. The `uncles` field having been removed from the [Header](#header), each entry is a fixed 361 bytes — a 297-byte header plus a 64-byte signature — so the list of carried headers parses unambiguously from its element count alone. The whole list, signatures included, is committed by `header.body_root` and therefore by the block ID, so no two blocks sharing an ID can differ in a carried signature. The proposal length reveals how many uncles are referenced — proposal indistinguishability is provided by the message-layer padding of [Payload Formatting](payload-formatting.md), not by the encoding. The proposer chooses which uncles to reference according to [Uncle Selection](cryptarchia-v1-protocol.md#uncle-selection), and every entry must satisfy the validity rules of [Uncle References](cryptarchia-v1-protocol.md#uncle-references) or the block is rejected. The same list is carried over into the reconstructed [Block](#block), which is what makes every referenced uncle structurally available: those rules can be evaluated by any node holding the chain, including nodes bootstrapping from genesis that never receive the proposal.
- `references` is a variable-length list of up to `MAX_BLOCK_TXS` [references](#references) to transactions, each being an 8-byte (`SHORT_ID_LENGTH`) keyed short transaction ID, derived under a key specific to this proposal from the transaction hash defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction).
- `signature` is the signature of the complete `header` using the `leader_key` from the `ProofOfLeadership`; the size of the `Ed25519Signature` type is 64 bytes.

The proposal carries no padding of its own. Proposal indistinguishability is provided at the message layer: [Payload Formatting](payload-formatting.md#body) already mandates a fixed body length (`Max_Body_Length`) for every dispersed payload, with shorter messages padded with **random** data and the true length carried in `body_length`. An in-proposal zero-padded layout would duplicate that guarantee while charging every proposal the full `MAX_BLOCK_TXS` cost even when it references few transactions. The padding lies outside the signed proposal and is discarded via `body_length` on decapsulation, so no consensus meaning ever attaches to it.

Note that this makes the random-padding requirement of [Payload Formatting](payload-formatting.md#body) load-bearing for the first time. While the proposal was a constant size it always filled the body exactly and the padding path never fired for a real proposal. Implementations must pad with random data, not zeros, or the padding region will itself distinguish proposals by their reference count.

### Header

```python
class Header:                                # 297 bytes
    bedrock_version: byte                    # 1 byte
    parent_block: hash                       # 32 bytes
    slot: SlotNumber                         # 8 bytes
    body_root: hash                          # 32 bytes
    proof_of_leadership: ProofOfLeadership   # 224 bytes
```

Where:

- `bedrock_version` is the version of the proposal message structure that supports other protocols defined in linked reference; its size is 1 byte and is fixed to `0x01`.
- `parent_block` is the block ID ([Cryptarchia Protocol](cryptarchia-v1-protocol.md)) of the parent block, validated and accepted by the block builder. It is used for the derivation of the `AgedLedger` and `LatestLedger` values necessary for validating the PoL; the size of the `hash` is 32 bytes.
- `slot` is the consensus slot number; the size of the `SlotNumber` type is 8 bytes.
- `body_root` is the commitment to the block body — both the carried `uncle_headers` and the transactions. It is computed as defined in step 4 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation), which combines the serialized `uncle_headers` list with the root of the Merkle tree constructed from the **full** transaction hashes (defined in [Mantle Transaction](bedrock-v1.1-mantle-specification.md#mantle-transaction)) — the same hashes from which the `mempool_transactions` short IDs are derived; the size of the `hash` is 32 bytes. Because that Merkle root is taken over the full hashes, `body_root` uniquely binds the proposal to a specific ordered transaction selection even when two transactions share the same `references` prefix, and it also binds the *number* of references; see [Binding of the reference list](#binding-of-the-reference-list). Since the block ID is taken over the header, committing the uncle headers here is what makes two blocks with the same ID identical byte for byte.
- `proof_of_leadership` is the proof confirming that the sender is the leader; defined below: [Proof of Leadership](#proof-of-leadership).

### References

Each reference is a keyed **short transaction ID** rather than the transaction hash or a prefix of it. A short ID is the full 64-bit output of SipHash-2-4 over the transaction hash, under a 128-bit key specific to this proposal:

```python
SHORT_ID_LENGTH = 8                   # bytes: the full SipHash-2-4 output
MAX_RECONSTRUCTION_COMBINATIONS = 64  # see Reference Resolution

def reference_key(header) -> (uint64, uint64):
    material = hash(b"REFKEY_V1",
                    header.parent_block,
                    encode(header.slot),                  # UINT64, little-endian
                    encode(header.proof_of_leadership))   # 224 bytes, wire order
    return uint64_le(material[0:8]), uint64_le(material[8:16])

def short_id(k0: uint64, k1: uint64, tx) -> bytes:
    return encode(SipHash24(k0, k1, mantle_txhash(tx)))   # UINT64, little-endian
```

Where `hash` is Blake2b as specified in [Common Cryptographic Components](common-cryptographic-components.md), `encode` is the canonical encoding of [Canonical Encoding](#canonical-encoding), `uint64_le` reads 8 bytes as a little-endian integer, and `SipHash24` is SipHash-2-4 ([Aumasson–Bernstein, 2012](https://eprint.iacr.org/2012/351)) keyed with `(k0, k1)`.

The key is **derived, not carried**. Every field of its preimage is part of the signed header, so the key is authenticated by `signature` and by `block_id` exactly as the header is, adds no bytes to the wire, and cannot be tampered with separately from the header. The preimage deliberately excludes `body_root`, so the key is fixed before transaction selection begins and the builder can compute short IDs while selecting. And because the preimage contains the `ProofOfLeadership`, the key of a future proposal is unknowable to anyone but its — still secret — leader until the proposal is broadcast; [Short ID keying and collision resistance](#short-id-keying-and-collision-resistance) establishes why that is what makes 8-byte references safe.

```python
class References:                            # 2..8194 bytes
    mempool_transactions: list[bytes]        # UINT16 count + len * SHORT_ID_LENGTH
```

Where `mempool_transactions` is a variable-length list of up to `MAX_BLOCK_TXS` references to transactions, each being `short_id(k0, k1, tx)` for a selected transaction `tx`.

The list is not padded. As specified in [Canonical Encoding](#canonical-encoding), it is serialized as a 2-byte little-endian element count followed by that many `SHORT_ID_LENGTH`-byte entries, so its encoded size is `2 + len(mempool_transactions) * SHORT_ID_LENGTH` bytes — 2 bytes when the proposal references no transaction, and `2 + 1024 * 8 = 8194` bytes at `MAX_BLOCK_TXS`.

A decoder must reject a count greater than `MAX_BLOCK_TXS` **before** allocating for it or performing any mempool lookup, on every ingress path. A decoder must equally reject a list containing the same reference value twice: [Proposal Construction](#proposal-construction) guarantees that an honest proposal never carries duplicate short IDs, so a duplicate marks the copy as tampered or dishonestly built, and rejecting it at decode time closes the cheapest way of inflating reconstruction work. As with every check on bytes outside the header, this rejection condemns the received copy, not the block ([Block Proposal Validation](#block-proposal-validation)).

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

Header            = Version ParentBlock Slot BodyRoot ProofOfLeadership
Version           = Byte            ; fixed to 0x01
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
Reference         = UINT64          ; short transaction ID: full SipHash-2-4 output
```

The terminals `Byte`, `UINT16`, `UINT64`, `Hash32`, `FieldElement`, `Groth16`, `Ed25519PublicKey` and `Ed25519Signature` are those defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md#common-structures). Note in particular that `FieldElement` is a little-endian BN254 field element, which fixes the byte order of `entropy_contribution` and `leader_voucher`.

This yields the following sizes, where `n` is the number of references:

| Structure | Encoded size | Minimum | Maximum |
| --- | --- | --- | --- |
| `Header` | `1 + 32 + 8 + 32 + 224` | 297 | 297 |
| `ProofOfLeadership` | `128 + 32 + 32 + 32` | 224 | 224 |
| `SignedHeader` | `297 + 64` | 361 | 361 |
| `UncleHeaders` | `1 + 361u` | 1 | 1,445 |
| `References` | `2 + 8n` | 2 | 8,194 |
| `Proposal` | `297 + (1 + 361u) + (2 + 8n) + 64` | 364 | 10,000 |

The maximum of 10,000 bytes, at `n = MAX_BLOCK_TXS` references and `u = MAX_UNCLES` uncles, is what [Payload Formatting](payload-formatting.md#body) uses as `Max_Body_Length`.

## Block

A **block** is what a proposal becomes once its references have been resolved against the mempool, and it is the unit that nodes store, execute and serve to their peers — in particular over [Downloading Blocks](cryptarchia-v1-bootstr-sync.md#downloading-blocks) during synchronization, where proposals are never transferred.

```python
class Block:
    header: Header                           # 297 bytes
    signature: Ed25519Signature              # 64 bytes
    uncle_headers: list[SignedHeader]        # 1 + n × 361 bytes, n <= MAX_UNCLES
    transactions: list[SignedMantleTx]       # up to MAX_BLOCK_SIZE
```

Where:

- `header` is the header of the proposal the block was reconstructed from, unchanged; defined above: [Header](#header).
- `signature` is the proposal signature over that `header`, carried over unchanged. It is retained because `block_id` commits to the header alone and therefore does not cover the signature, so a node that receives the block without ever seeing the proposal — as happens during synchronization — would otherwise have nothing to check against step 9 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation); the size of the `Ed25519Signature` type is 64 bytes.
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
    - `bedrock_version`
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
    - Ensure each transaction:
      - Is valid according to [Mantle](bedrock-v1.1-mantle-specification.md).
      - Has no conflicts with others (e.g., two transactions trying to spend the same note).

3. Derive the reference key and the short IDs, and clear the selection of collisions:
```python
k0, k1 = reference_key(header)   # parent_block, slot and the PoL are already set
references: list[bytes] = [short_id(k0, k1, tx) for tx in mempool_transactions]
```

  The selection **must not** contain two transactions with the same short ID: on a duplicate, drop or replace one of the pair and recompute. Under an honestly derived key a duplicate occurs with probability ≈ $`N^2/2^{65}`$ per proposal — below $`2^{-45}`$ at `MAX_BLOCK_TXS` — so this rule fires essentially never, and its purpose is to let decoders treat a duplicate reference as proof of tampering or dishonest construction ([References](#references)). The builder **should** also avoid selecting a transaction whose short ID collides with any *other* transaction in its mempool: such a collision is visible to the builder, and would resolve ambiguously at every validator holding both transactions. This is best effort — the builder cannot see other mempools — and [Reference Resolution](#reference-resolution) handles what it cannot prevent.

4. Compute the `header.body_root` over both parts of the body, as defined in step 4 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation): the serialized `uncle_headers` list from step 1, combined with the root of the Merkle tree constructed over the full transaction hashes of the selected transactions used to build `references`. The `references` list is left exactly as long as the selection; it is not padded. This step therefore comes after both uncle selection and transaction selection.
5. Sign the block proposal header, where `header` is its canonical encoding as defined in [Canonical Encoding](#canonical-encoding) — the 297 bytes of the header alone, without `uncle_headers`, without `references` and without the signature itself.
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
8. Validators derive the proposal's reference key from its header, recompute the short IDs of the transactions in their local mempool under it, and match each reference in `references` against them.
9. If every reference resolves to a mempool transaction — uniquely, or through the bounded combination search — and the resolved sequence reproduces `header.body_root`, the block proposal is reconstructed and proceeds to further validation steps; otherwise the validator rejects it, without that being a finding of invalidity — see [Reference Resolution](#reference-resolution).

### Reference Resolution

A reference is the 8-byte keyed short ID of a transaction, as defined in [References](#references). The key is derived from the proposal's header, so resolution begins by recomputing the short IDs of the local mempool under that key:

```python
def resolve_candidates(proposal, mempool):
    k0, k1 = reference_key(proposal.header)
    index = {}                                   # short ID -> local transactions
    for tx in mempool:
        index.setdefault(short_id(k0, k1, tx), []).append(tx)
    return [index.get(r, []) for r in proposal.references]
```

The rehash is per proposal — the key changes with every proposal, which is the point — and costs one SipHash evaluation per mempool transaction over its cached 32-byte hash. Nothing of it can be reused across proposals, and nothing needs to be: the index for one proposal is discarded with it.

Each reference then has a set of local candidates:

- **Exactly one candidate** — the case by an overwhelming margin: the reference resolves to that transaction.
- **No candidate** — the referenced transaction is absent locally, and the proposal cannot be reconstructed here.
- **Two or more candidates** — a short-ID collision between a referenced transaction and another local transaction. Under a fresh key this is a chance event with expected rate $`N \cdot M / 2^{64}`$ per proposal, for $`N`$ references against $`M`$ mempool transactions — about $`2^{-34}`$ at $`N = 1024`$, $`M = 10^6`$ — and [Short ID keying and collision resistance](#short-id-keying-and-collision-resistance) establishes that an adversary cannot do meaningfully better. It is resolved, not rejected.

Distinct references are distinct short IDs — decoders reject duplicates — and a transaction has exactly one short ID under the key, so the candidate sets of different references are disjoint and ambiguity is resolved by trying the combinations independently per reference:

```python
def reconstruct(proposal, candidates):
    if any(len(c) == 0 for c in candidates):
        return None            # missing transaction: not reconstructible here
    if product(len(c) for c in candidates) > MAX_RECONSTRUCTION_COMBINATIONS:
        return None            # ambiguity beyond the bound: not reconstructible here
    for assignment in cartesian_product(candidates):
        if body_root(proposal.uncle_headers, assignment) == proposal.header.body_root:
            return assignment  # the committed selection; unique, see below
    return None                # no assignment matches: corrupted or malformed
```

`MAX_RECONSTRUCTION_COMBINATIONS = 64` bounds the work of the search at 64 body-root evaluations, each over the carried `uncle_headers` and one candidate assignment; an implementation can keep the unchanged Merkle leaves between assignments, so that successive combinations cost one leaf path recomputation each rather than a full tree. The bound exists for the adversarial case — honest ambiguity is almost always a single reference with two candidates, two combinations. At most one assignment can reproduce `header.body_root`, because two assignments differ in at least one full 32-byte transaction hash and the body root binds them all ([Why `body_root` alone binds the reference list](#why-body_root-alone-binds-the-reference-list)); the order in which combinations are tried therefore does not matter.

Resolution is a function of the proposal and the validator's mempool alone, so two validators holding the same mempool always reach the same decision. A proposal whose reference count exceeds `MAX_BLOCK_TXS`, or that contains the same reference twice, is rejected at decode time, as specified in [References](#references).

A reference resolving to no local transaction means the referenced transaction has not reached this validator's mempool, which the transaction maturity assumption above is designed to prevent; a combination count above the bound means the local mempool holds a pile-up of collisions that [Short ID keying and collision resistance](#short-id-keying-and-collision-resistance) prices out of reach of both chance and adversaries. In either case the validator rejects the proposal and does not build on it. It **must not** record that outcome as a verdict on `block_id`: both conditions are properties of the local mempool, not of the block, and the block may be received again — another copy of the proposal, or the full block through chain synchronisation — and is then validated on its merits. This is unlike a failure implied by the header bytes alone — a wrong version, an invalid proof of leadership — which condemns the block the header names, identically at every node, and is final. Note that not every mempool-independent failure is of that kind: a frame that does not decode or a bad `signature` condemns only the received copy, because the bytes at fault lie outside the header that `block_id` is computed from. [Block Proposal Validation](#block-proposal-validation) states the full classification.

The `header.body_root` check is what makes resolution safe under collisions of any origin: an assignment containing the wrong transaction never reproduces the root.

### Binding of the reference list

Neither the reference entries nor their count are covered by `signature` or by `block_id`, both of which range over `header` only. `header.body_root` is therefore the **sole** mechanism binding a proposal to its reference list and to the number of references: any altered reference set, and any altered count, fails to reproduce `header.body_root` and the proposal is rejected. The argument is given in [Why `body_root` alone binds the reference list](#why-body_root-alone-binds-the-reference-list).

Two operational consequences follow:

- Tampered copies of a genuine proposal are cheap to produce, since `references` is unauthenticated. `block_id` is computable from the 297-byte header alone and is shared by every variant of one proposal, which cuts both ways: once a copy has been **accepted**, every later copy carrying that `block_id` can be dropped at a glance, collapsing all tampered variants into a single unit of reconstruction work — but a *rejected* copy must not suppress later ones, or the first tampered variant to arrive would censor the genuine proposal behind it. Duplicate suppression on `block_id` is therefore keyed on acceptance, never on receipt.
- Reconstruction must not be the first expensive step. It begins with a full mempool rehash under the proposal's key, so it should follow signature and PoL verification, and an unauthenticated proposal must be discarded before any rehashing takes place. Each *distinct* `block_id` admitted past those checks triggers at most one rehash; an equivocating leader can still mint several distinct proposals for one slot, so implementations should additionally bound reconstruction attempts per slot.

Reconstruction assembles the [Block](#block) from the proposal's `header` and `signature`, its `uncle_headers` copied over verbatim, and the transactions resolved from `references` in the order the references appear. The `uncle_headers` list is retained rather than discarded: it is not recoverable from the mempool, it is committed by `header.body_root` and so cannot be dropped without invalidating the block, and once the proposal has been consumed the block is the only carrier of the signed uncle headers that [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) and the [Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference) need.

## Block Proposal Validation

This section defines the procedure followed by a Logos Blockchain node to validate a received block proposal.

Given a `proposal`, a proposed block consisting of a `header`, `uncle_headers`, `references` and a `signature`. This block proposal is considered valid if the following conditions are met, checked **in the order given** so that the cheapest checks discard a malformed or unauthenticated proposal first.

The order is constrained as well as economical. [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) is defined over a block $`B = (header, transactions)`$, but a proposal carries `references` rather than transactions, so the rules that range over `transactions` cannot be evaluated until reconstruction has produced them. They are therefore applied in the step where their operand exists, and each is named below.

1. **Decoding**
  The received bytes must decode to a `proposal` under [Canonical Encoding](#canonical-encoding): the frame must be consumed exactly, with no trailing bytes, the `references` element count must not exceed `MAX_BLOCK_TXS` and its entries must be pairwise distinct ([References](#references)), and the `uncle_headers` element count must not exceed `MAX_UNCLES`. These checks precede any allocation proportional to a count and any mempool lookup. Because reconstruction produces exactly one transaction per reference, the first of them also discharges rule 3 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation), `length(transactions) <= MAX_BLOCK_TXS`.

2. **Header Validation**
  The `header` must satisfy the rules of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) that range over the header and the block tree alone: the bedrock version, the slot ordering against the parent, the wallclock check, the presence of the parent in the block tree, the height against the latest immutable block, and the leader's right to propose — that is, rules 1 and 5 through 9. These need no mempool access, and rule 9 covers `signature` and the proof of leadership, so an unauthenticated proposal is discarded here, before any mempool scanning.

3. **Uncle Validation**
  Every entry of `uncle_headers` must be a valid uncle of the block, which is rule 10 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) (see [Uncle References](cryptarchia-v1-protocol.md#uncle-references)). Like the previous step this reads only the chain being extended and the carried entry, so it needs no mempool access and precedes reconstruction. At this point the carried entries are not yet authenticated: `signature` does not cover them, and they are bound to the header only by `header.body_root`, which is not checked until the next step. A failure here therefore condemns the received copy, not the block — it is handled exactly like a reconstruction failure, with no verdict recorded against `block_id`. A finding that the *block* carries an invalid uncle requires entries whose binding has been confirmed: a full block obtained through chain synchronisation, whose `body_root` is checkable immediately, is judged by rule 10 on its merits.

4. **Block Proposal Reconstruction**
  Every reference must resolve to a local mempool transaction under the proposal's reference key — uniquely, or through the bounded combination search of [Reference Resolution](#reference-resolution) — and the body root computed over the carried `uncle_headers` and the resolved transactions must equal `header.body_root`. This step produces `transactions` and discharges rule 4 of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation). A mismatch here means the message was corrupted in transit or malformed by its proposer, not that the block it names is invalid. Corruption of the header itself cannot reach this step — it would have failed the signature check in step 2 — so a mismatching copy has a genuine header over a tampered or damaged body, and carries the **same** `block_id` as the block it names. When that block is genuine, its well-formed bytes are held by the proposer and by every node that accepted it, and the proposal may be re-requested from any of them. That shared identity is exactly why no verdict about the block may be recorded from the mismatch: condemning the `block_id` of a corrupted copy would condemn the genuine block with it.

5. **Block Body Validation**
  With `transactions` now available, the remaining rule of [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) applies: rule 2, `bytes(transactions) <= MAX_BLOCK_SIZE`.

6. **Mempool Transactions Validation**
  `mempool_transactions` must refer to a valid sequence of Mantle Transactions from the mempool. Each transaction must be valid according to the rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md). In order to verify ZK proofs, they are batched for verification as explained in [Batch verification of ZK proofs](#batch-verification-of-zk-proofs) to get better performance.

If any of the above checks fail, the block proposal must be rejected. What the rejection establishes depends on which bytes the failed check read. `block_id` is computed from the 297-byte header alone, so every byte outside the header — `uncle_headers`, `references`, `signature`, trailing bytes — can be altered in a copy without changing the `block_id` it names, and none of those bytes are authenticated until `header.body_root` is confirmed in step 4. A failure detected in them is a property of the received copy, not of the block: a frame that does not decode (step 1), a bad `signature` (step 2), an invalid uncle entry (step 3) and a failure to reconstruct (step 4) each discard the copy **without** recording a verdict against `block_id`. Only a failure implied by the header bytes themselves — a wrong version, an invalid proof of leadership — condemns the block the header names, identically at every node. Treating any of the former as final would let an attacker censor a genuine block by circulating tampered copies of it: one flipped bit in the trailing `signature`, or one substituted uncle entry, leaves `block_id` unchanged. The mempool-dependence of step 4 adds one further distinction — a reference that fails to resolve locally may resolve at another node — described in [Reference Resolution](#reference-resolution).

This ordering is specific to the proposal path. A block received in full through chain synchronisation carries its transactions from the start, so [Block Header Validation](cryptarchia-v1-protocol.md#block-header-validation) applies to it as written, with no ordering constraint.

## Block Execution

This section specifies how a Logos Blockchain node executes a valid block proposal to update its local state.

Given a `ValidBlock` that has successfully passed proposal validation, the node must:

1. Append the `leader_voucher` contained in the block to the set of reward vouchers **when the following epoch starts**.
2. Execute the reward distribution protocol defined in [**Service Reward Distribution Protocol**](bedrock-service-reward-distribution.md) to generate reward notes locally and include them in the ledger.
3. Execute the Mantle Transactions included in the block sequentially, using the execution rules defined in the [Mantle](bedrock-v1.1-mantle-specification.md).

The carried `uncle_headers` are not executed. A referenced uncle is not part of the chain; therefore, its transactions have no effect on the ledger state. The uncles are used only as evidence of consensus participation for the [Total Stake Inference](cryptarchia-v1-protocol.md#total-stake-inference).

# Annex

## Short ID keying and collision resistance

References are 8-byte short IDs, yet the design tolerates no grinding of collisions. What reconciles the two is that a short ID is a *keyed* function of the transaction, under a key that does not exist until the proposal does. This adapts the compact-block relay of Bitcoin's [BIP-152](https://github.com/bitcoin/bips/blob/master/bip-0152.mediawiki), which has run SipHash short IDs at 48 bits in an adversarial network for years. The differences here: a longer ID (64 bits), a key derived from consensus data rather than a relayer-chosen nonce, and — because [Blend](blend-protocol.md) anonymity permits no counterpart to BIP-152's `getblocktxn` follow-up — a bounded local combination search in place of a fetch-the-missing-parts fallback.

**Before the proposal exists, no useful work can be done.** The key preimage contains the `ProofOfLeadership`. Until the proposal is broadcast, the winning leader is unknown — leadership is anonymous by design — so no other party can evaluate `short_id` for the coming block at all. Collisions can be neither pre-ground nor pre-planted: transactions inserted into mempools in advance meet the eventual key as uniformly random 64-bit values, and a planted set of $`M`$ transactions collides with a selection of $`N`$ with expected count $`N \cdot M / 2^{64}`$ — at $`N = 2^{10}`$, one expected hit requires $`M = 2^{54}`$ resident transactions. An unkeyed prefix, by contrast, can be ground for as long as the attacker likes before the block exists: at 8 unkeyed bytes a birthday search finds colliding pairs within $`2^{32}`$ hashes — under a second on a GPU — which is why the previous revision of this specification had to spend 16 bytes per reference.

**After the proposal is broadcast, the window is seconds and the birthday advantage is gone.** Once the key is public, only collisions against the $`N`$ *referenced* short IDs matter: a pair of attacker transactions colliding with each other but with no reference is never consulted by resolution. Hitting a fixed set of $`N`$ targets is a targeted search costing $`2^{64}/N`$ attempts — the birthday square-root shortcut does not apply — and every attempt must be a distinct valid transaction, so each costs at least one `mantle_txhash` evaluation of a fresh candidate. At $`N = 1024`$ that is $`2^{54}`$ transaction hashes, years of GPU time, against a window that closes when the proposal finishes propagating: seconds. The keying also charges attacker and defender asymmetrically — the attacker pays the cryptographic hash per candidate, while validators pay one SipHash per mempool transaction over a hash they already cache.

**The leader's advance knowledge of its own key is harmless.** A leader can know its winning slots — and therefore its own future keys — well in advance, and could grind colliding pairs under them at birthday cost. But a key is used only by its own proposal, so all such a leader can sabotage is its own block: referencing ground collisions past `MAX_RECONSTRUCTION_COMBINATIONS` makes every validator reject the proposal, which achieves exactly what not proposing achieves. The bound is what turns this from a validator-CPU attack into a self-DoS: the search a malicious leader can impose on each validator is capped at 64 body-root evaluations per proposal.

**What remains is chance, and it is priced in.** Under a fresh key, a validator holding $`M`$ transactions sees an ambiguous reference with probability ≈ $`N \cdot M / 2^{64}`$ per proposal — about $`2^{-34}`$ at $`M = 10^6`$: of the order of one occurrence per year across a network of ten thousand validators, and that occurrence is one reference with two candidates, settled by trying both against `header.body_root`. Exceeding `MAX_RECONSTRUCTION_COMBINATIONS = 64` by chance requires simultaneous independent collisions on at least seven references — or improbably many candidates on fewer — and has no practical probability of occurring; a validator that nonetheless hits either failure rejects locally and provisionally, exactly as for a missing transaction ([Reference Resolution](#reference-resolution)).

**Why SipHash-2-4, and why the full 64 bits.** The short ID needs pseudorandomness under an unpredictable key — PRF security — not collision resistance in the cryptographic sense. SipHash-2-4 is a keyed PRF designed for short inputs and for precisely this threat shape (it was built to stop hash-flood denial-of-service), and it evaluates a 32-byte input several times faster than a single Blake2b compression, which is what keeps the per-proposal mempool rehash cheap: about 13 ms per $`10^6`$ transactions on a desktop core, against 80–160 ms for Blake2b variants (benchmarked in the research repository, `simulations/block-proposal/bench-shortid`). BIP-152's 48-bit IDs would not carry over safely: at $`b = 48`$ the post-broadcast targeted search is $`2^{48}/N = 2^{38}`$ — GPU-seconds, inside the propagation window — while at $`b = 64`$ it is $`2^{54}`$, out of reach by many orders of magnitude. The full SipHash output is used directly, so a reference is a native little-endian 64-bit integer on the wire and no truncation step exists to specify.

The price of the revision is the collision machinery itself — the builder-side pre-check, the bounded search — in exchange for halving the references against the 16-byte unkeyed design: the maximum proposal falls from 18,192 to 10,000 bytes, 3.5× below the full-hash layout's 34,574. `header.body_root` remains the safety backstop in every case: no assignment of wrong transactions can reproduce it.

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
