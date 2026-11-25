# [RFC] Mantle: Split the Operations into their protocols

**Motivation and proposal:** [PR #552](https://github.com/logos-co/logos-lips/pull/552)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-11-25 |

## Reviewer Orientation

Every Operation keeps its rules, payload, opcode, Execution Gas and encoding. The review checks that each moved section matches its source line for line, apart from the changes listed in [Chores](#chores).

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Medium | **Start here**: [Mantle](#affected-specifications), [what Mantle keeps](#what-mantle-keeps) | the Opcodes table links every Operation; the transaction, ledger, Gas Determination and Test Vectors cover all of them |
| 2 | Medium | **Start here**: [Mantle Channels](#affected-specifications), [channel Operations](#mantle-channels) | the 646 moved lines match their source; links into Mantle resolve |
| 3 | Medium | [Service Declaration Protocol](#affected-specifications), [SDP Operations](#service-declaration-protocol) | the moved block sits under `# Construction`; links to its own sections are local |
| 4 | Medium | [Proof of Work](#affected-specifications), [claim Operation](#proof-of-work) | the claim Operation sits under `# Protocol`; the Introduction names it |
| 5 | Low | the remaining documents in [Chores](#chores) | skim: link targets only |

# Discussion

## What Mantle keeps

Mantle keeps what spans every Operation: the Mantle Transaction and its validation and execution, the ledger and its note sets, the Opcodes table, the Gas Determination table and the Test Vectors. Every protocol shares them. TRANSFER, the Operation of the ledger itself, is specified in Mantle under `## Ledger Operations`.

## Each protocol owns its Operations

The channel Operations are specified in Mantle Channels, the SDP Operations in the Service Declaration Protocol, and the claim of proof of work rewards in Proof of Work. A reader of a protocol finds its messages, its state and its Operations in one document, and a change to one protocol touches its own document and its own revision history. Every Operation section has the same shape, `#### Payload`, `#### Proof`, `#### Execution Gas`, `#### Validation` and `#### Execution`, wherever it is specified.

## No rule changes

The split moves text and repoints links. No payload, opcode, validation rule, execution step, Execution Gas cost or encoding differs, so nodes and wallets need no change and no migration. Every changed document takes a patch version, and Mantle Channels starts at 1.0.0.

# Details

## Mantle

Version 2.0.1, published as `bedrock-mantle.md`. Mantle specifies the Mantle Transaction, the ledger, TRANSFER under `## Ledger Operations`, and the tables and vectors shared by all Operations. The Opcodes table links each Operation to the section that specifies it:

| **Operation** | **Opcode** | **Specified in** |
| --- | --- | --- |
| `TRANSFER` | `0x00` | [Mantle](../bedrock-mantle.md#transfer) |
| `CHANNEL_CONFIG`, `CHANNEL_INSCRIBE`, `CHANNEL_DEPOSIT`, `CHANNEL_WITHDRAW` | `0x10`-`0x13` | [Mantle Channels](../bedrock-mantle-channels.md#channel-operations) |
| `SDP_DECLARE`, `SDP_WITHDRAW`, `SDP_ACTIVE` | `0x20`-`0x22` | [Service Declaration Protocol](../bedrock-service-declaration-protocol.md#service-declaration-protocol-sdp-operations) |
| `CLAIM_POW_REWARD` | `0x30` | [Proof of Work](../proof-of-work.md#claim_pow_reward) |

## Mantle Channels

Version 1.0.0, slug 246, published as `bedrock-mantle-channels.md`. Mantle Channels opens with an Introduction and an Overview, and specifies `## Channel Operations`: Message Ordering, Decentralized Sequencing, Bridging, and the Operations `CHANNEL_INSCRIBE`, `CHANNEL_CONFIG`, `CHANNEL_DEPOSIT` and `CHANNEL_WITHDRAW`, under a `# Operations` heading. Its Introduction points to Mantle for the transaction that carries the channel Operations and for the ledger they act on.

## Service Declaration Protocol

Version 1.9.1. The Service Declaration Protocol specifies `## Service Declaration Protocol (SDP) Operations` under `# Construction`: the validator state, Common SDP Structures, `SDP_DECLARE`, `SDP_WITHDRAW`, SDP Epoch Finalization and `SDP_ACTIVE`.

## Proof of Work

Version 1.2.1. Proof of Work specifies `## Proof of Work Operations` under `# Protocol`: the validator state and `CLAIM_POW_REWARD`. The Introduction lists the claim Operation among what the document specifies.

## Chores

- Links into the moved sections point to their new documents in [Gas Cost Determination](../analysis-gas-cost-determination.md), [Bedrock Genesis Block](../bedrock-genesis-block.md), [Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md), [Block Construction, Validation and Execution](../bedrock-block-construction.md) and [Mantle Transaction Encoding](../mantle-transaction-encoding.md).
- Links from the moved text back into Mantle name the Mantle document. Links from the SDP and Proof of Work documents to their own sections are local anchors.
- The Service Declaration Protocol drops its `## Mantle and ZK Proofs` section, a pointer to Mantle that the SDP Operations section replaces.
- TRANSFER takes the section shape of the other Operations, `### TRANSFER` with `####` subsections, and the label `*Execute*`. `CLAIM_POW_REWARD` takes the heading `#### Execution Gas` and the label `*Execute*`.
- Two Mantle sentences refer to the Operations without the word "below", one of them through the Opcodes table.
- The blockchain documents carry no version in their file names, since each document keeps its version in its revision history: `bedrock-v1.1-mantle-specification.md` becomes `bedrock-mantle.md`, `bedrock-v1.1-block-construction.md` becomes `bedrock-block-construction.md`, `cryptarchia-v1-protocol.md` becomes `cryptarchia-protocol.md`, and `cryptarchia-v1-bootstr-sync.md` becomes `cryptarchia-bootstr-sync.md` with its image folder `cryptarchia-bootstr-sync/`. Mantle Channels is published as `bedrock-mantle-channels.md`. Every link to them follows, in the documents listed in [Affected Specifications](#affected-specifications) and in the RFC documents of [PR #480](RFC-480-mantle-private-utxo-ledger.md) and [PR #503](RFC-503-cryptoeconomics-define-the-lepton-as-the-indivisible-token-unit.md). Historical documents, merged RFC documents and the revision rows published on master keep their links, and the PR lists the links left dead.
- `scripts/blockchain_structure.py` maps the files under their names and places Mantle Channels under Mantle in the generated summary, beside Mantle and Proof of Work.

# Implementation

- [ ] No implementation required (specification-only change): every Operation keeps its rules, payload, opcode, Execution Gas and encoding.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Mantle](../bedrock-mantle.md) | Modified | 2.0.1, published as `bedrock-mantle.md` |
| [Mantle Channels](../bedrock-mantle-channels.md) | Created | 1.0.0, published as `bedrock-mantle-channels.md` |
| [Service Declaration Protocol](../bedrock-service-declaration-protocol.md) | Modified | 1.9.1 |
| [Proof of Work](../proof-of-work.md) | Modified | 1.2.1 |
| [Block Construction, Validation and Execution](../bedrock-block-construction.md) | Modified | 1.4.1, published as `bedrock-block-construction.md`; link targets only |
| [Cryptarchia Protocol](../cryptarchia-protocol.md) | Modified | 1.3.1, published as `cryptarchia-protocol.md`; link targets only |
| [Cryptarchia Bootstrapping & Synchronization](../cryptarchia-bootstr-sync.md) | Modified | 1.0.4, published as `cryptarchia-bootstr-sync.md` with its images under `cryptarchia-bootstr-sync/`; link targets only |
| [Gas Cost Determination](../analysis-gas-cost-determination.md) | Modified | 1.8.1, link targets only |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | 1.3.1, link targets only |
| [Service Reward Distribution Protocol](../bedrock-service-reward-distribution.md) | Modified | 1.4.1, link targets only |
| [Mantle Transaction Encoding](../mantle-transaction-encoding.md) | Modified | 2.0.1, link targets only |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | 1.3.1, link target only |
| [Proof of Leadership](../cryptarchia-proof-of-leadership.md) | Modified | 1.2.1, link targets only |
| [Key Types and Generation](../key-types-and-generation.md) | Modified | 1.1.2, link target only |
| [Cryptoeconomics](../overview-cryptoeconomics.md) | Modified | 1.5.1, link targets only |
| [Proof of Quota](../proof-of-quota.md) | Modified | 1.3.1, link targets only |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | 1.2.1, link targets only |
| [Analysis: Resilience and Anonymity](../analysis-resilience-and-anonymity.md) | Modified | 1.0.1, link target only |
| [Analysis: Static Minimum Stake Estimation for Service Declaration Protocol](../analysis-static-minimum-stake-estimation-for-service-declaration-protocol.md) | Modified | 1.0.3, link target only |
| [Analysis: Total Stake Inference](../analysis-total-stake-inference.md) | Modified | 1.0.1, link target only |
| [Overview: Bedrock Architecture](../bedrock-architecture-overview.md) | Modified | 1.2.1, link target only |
| [Blend Protocol](../blend-protocol.md) | Modified | 1.8.2, link targets only |
| [Block Rewards](../block-rewards.md) | Modified | 1.4.1, link targets only |
| [Total Stake Inference](../cryptarchia-total-stake-inference.md) | Modified | 1.1.3, link targets only |
| [Execution Market](../execution-market.md) | Modified | 1.3.1, link targets only |
| [Cryptarchia Fork Choice Rule](../fork-choice.md) | Modified | 1.1.1, link target only |
| [Network Wire Format](../network-wire-format.md) | Modified | 1.0.2, link target only |
| [Payload Formatting](../payload-formatting.md) | Modified | 1.2.2, link targets only |
