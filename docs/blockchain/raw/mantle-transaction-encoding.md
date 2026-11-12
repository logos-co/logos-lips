# MANTLE-TRANSACTION-ENCODING

| Field | Value |
| --- | --- |
| Name | Mantle Transaction Encoding |
| Slug | 202 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <davidrusu@logos.co> |
| Contributors | Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/mantle-transaction-encoding.md) — chore: move blockchain specs from notion to github

<!-- timeline:end -->

# Revisions History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-12-01 |
| 1.1.0 | [\[RFC\] Make Ledger Transaction an Operation](mantle-transaction-encoding/appendices/rfc-make-ledger-transaction-an-operation.md) | 2026-03-25 |
| 1.2.0 | [\[RFC\] Add Deposit/Withdraw to Tx Encoding](mantle-transaction-encoding/appendices/rfc-add-deposit-withdraw-to-tx-encoding.md) | 2026-04-02 |
| 1.3.0 | [\[RFC\] Enforce NoteId uniqueness](mantle-transaction-encoding/appendices/rfc-enforce-noteid-uniqueness.md) | 2026-04-24 |
| 1.4.0 | [\[RFC\] Simplify Mantle Transaction and Refactor Ledger Operations](mantle-transaction-encoding/appendices/rfc-simplify-mantle-transaction-and-refactor-ledger-operations.md) | 2026-05-06 |
| 1.4.1 | Removed mention of DA. Updated KeyCount from Byte to UINT16 to follow Mantle. | 2026-05-21 |
| 1.5.0 | Introduce the new Operation `CHANNEL_STAKE_ASSIGNATION` and update of the channel operations to reflect changes in Mantle | 2026-06-24 |
| 1.5.1 | [RFC] One canonical encoding for `ServiceType` and `Locator`: pin `Locator` bytes to the multiaddr binary form | 2026-08-14 |
| 1.6.0 | Added the `Parent` of the `ChannelConfig` to follow Mantle | 2026-08-27 |
| 1.6.1 | Renamed the `LockedNoteId` production of the SDP Operations into `ServiceNoteId` | 2026-08-27 |
| 1.7.0 | Added the `ChannelConfigOpProof` and `ChannelTransferOpProof` variants and factored the three channel threshold proofs into `ChannelMultiSigProof`, carrying the index of the signing key alongside each signature | 2026-08-31 |
| 1.8.0 | Added the `ClaimPowReward` Operation payload; its proof is a `ZkSigProof` | 2026-09-08 |
| 1.9.0 | Swap Ed25519Signature and SignerIndex order in IndexedSignature | 2026-10-01 |
| 1.10.0 | Introduced a shared maximum operation data payload size for channel inscriptions and channel deposit metadata, retaining their `UINT32` length prefixes; corrected SDP activity metadata to use its tagged variant encoding without a generic length prefix | 2026-10-06 |
| 1.11.0 | [RFC] `SDPWithdraw` drops the redundant `ServiceNoteId` | 2026-10-27 |
| 2.0.0 | Follow the private note ledger of Mantle 2.0.0: nullifier inputs and commitment outputs with their `CommitmentRoot` and `Value`, user steps, tagged by their kind and with their own `Inscription`, in the `MiniBlocks` of `ChannelInscribe`, holder withdrawals, the `Inscription` of `ChannelDeposit`, the SDP payloads over notes with `NotePk` in `SDPDeclare` and no `Nonce` in `SDPWithdraw`, `PowNonce` and no `EpochNonce` in `ClaimPowReward`, the `ZkTransfer` proof variants, and the removal of `ChannelTransfer`, `TransferThreshold` and `LeaderClaim`. A `FieldElement` not less than $`p`$ is rejected | 2026-11-06 |

# Introduction

This document specifies the canonical encoding of Mantle transactions (see [Mantle - Mantle Transaction](bedrock-v1.1-mantle-specification.md)) and its sub-components. Transactions sent through the mempool and included in blocks use this encoding.

# Overview

The transaction encoding is specified in ABNF form to remove any ambiguity and guarantee a canonical encoding. The high level encoding choices which were not immediately derivable from the Mantle specification are listed here:

1. All multi-byte integers use little-endian encoding
2. Any lists are length-prefixed with fixed width uints
3. We derive number of proofs and type of proof from the Ops list parsed earlier
4. A `FieldElement` whose value is not less than the BN254 scalar field order $`p`$ is rejected, so every field element has a single encoding

# Specification

## Signed Mantle Tx

```schema
SignedMantleTx = MantleTx OpsProofs
```

## Mantle Tx

```schema
MantleTx = OpCount *Op
OpCount  = Byte
```

## Operations

```schema
Op        = Opcode OpPayload
Opcode    = Byte

OpPayload = Transfer /
            ChannelInscribe /
            ChannelConfig /
            ChannelDeposit /
            ChannelWithdraw /
            SDPDeclare /
            SDPWithdraw /
            SDPActive /
            ClaimPowReward
```

### Channel Operations

```schema
ChannelInscribe = ChannelId Inscription Parent Signer MiniBlocks
Inscription     = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes, the inscriptions
                               ; of a ChannelInscribe counting together
MiniBlocks      = MiniBlockCount *MiniBlock
MiniBlockCount  = UINT16
MiniBlock       = StepCount *Step ; StepCount at least 1, a decoder MUST reject 0
StepCount       = UINT16
Step            = UserStepKind UserStep
UserStepKind    = %x00
UserStep        = Inputs Outputs CommitmentRoot Inscription

ChannelConfig     = ChannelId Parent KeyCount *Signer PostingTimeframe PostingTimeout ConfigThreshold
KeyCount                   = UINT16
PostingTimeframe           = UINT32
PostingTimeout             = UINT32
ConfigThreshold            = UINT16

ChannelDeposit    = ChannelId Inputs Outputs CommitmentRoot Value Inscription

ChannelWithdraw   = ChannelId Inputs Outputs CommitmentRoot

ChannelId         = Hash32
Parent            = Hash32
Signer            = Ed25519PublicKey
```

A `UserStep` moves channel notes with the inscription of its holder, and a `MiniBlock` groups the steps proven against the same state of the transaction buffer, as [CHANNEL_INSCRIBE](bedrock-v1.1-mantle-specification.md#channel_inscribe) defines them. A `Step` starts with the byte of its kind; a decoder MUST reject an unknown kind.

`MAX_OPERATION_DATA_SIZE` MUST be exactly **1,835,008 bytes**. The payloads of the `Inscription` of a `ChannelInscribe` and of the `Inscription` of each of its steps MUST together be at most `MAX_OPERATION_DATA_SIZE` bytes, and the payload of the `Inscription` of a `ChannelDeposit` MUST be at most `MAX_OPERATION_DATA_SIZE` bytes, each excluding its `UINT32` length prefix. A decoder MUST reject a `ChannelInscribe` when the declared or decoded payload lengths of its inscriptions sum to more than the limit, and a `ChannelDeposit` when the declared or decoded payload length of its inscription exceeds it.

### SDP Operations

```schema
SDPDeclare    = ServiceType Locators ProviderId ZkId NotePk Inputs CommitmentRoot Value
ServiceType   = Byte          ; 0 = BN
Locators      = LocatorCount *Locator
LocatorCount  = Byte          ; Max 8
Locator       = 2Byte *BYTE   ; Max 329 bytes, multiaddr binary form
ProviderId    = Ed25519PublicKey
ZkId          = ZkPublicKey
NotePk        = ZkPublicKey

SDPWithdraw   = DeclarationId NoteNullifier Outputs Value
DeclarationId = Hash32
Nonce         = UINT64

SDPActive               = DeclarationId Nonce ActivityMetadata
ActivityMetadata        = ActivityMetadataType ActivityMetadataPayload
ActivityMetadataType    = Byte ; 0x01 = Blend
ActivityMetadataPayload = BlendActivityProof ; Selected by ActivityMetadataType
```

`ActivityMetadataType` is a one-byte discriminant. The only currently valid value is `0x01`, which selects `BlendActivityProof`; a decoder MUST reject any other value. `BlendActivityProof` is the 228-byte concatenation of `epoch_number`, `signing_key`, `proof_of_quota`, and `proof_of_selection` defined in [Blend Protocol — Active Message](blend-protocol.md#active-message), excluding that section's `metadata_type` byte, which is encoded here as `ActivityMetadataType`.

The current Blend variant occupies 229 bytes including its discriminant. Its encoding and validation follow the selected variant's rules; `MAX_OPERATION_DATA_SIZE` does not apply to `SDPActive.Metadata`.

### Proof of work operations

```schema
ClaimPowReward = BlockHash ZkPublicKey PowNonce
BlockHash      = Hash32       ; recent canonical block the solution is anchored to
PowNonce       = FieldElement ; value searched for a ticket satisfying the reward threshold
```

### Transfer Operations

```schema
Transfer    = Inputs Outputs CommitmentRoot Value
Inputs      = InputCount *NoteNullifier
InputCount  = Byte
Outputs     = OutputCount *NoteCommitment
OutputCount = Byte
```

## Ledger

```schema
Value          = UINT64
NoteCommitment = FieldElement ; commitment of a note
NoteNullifier  = FieldElement ; nullifier of a note
CommitmentRoot = FieldElement ; MMR root of note commitments
```

Commitments and nullifiers are defined in [Note Commitment and Nullifier](bedrock-v1.1-mantle-specification.md#note-commitment-and-nullifier) of Mantle, and the root of the commitments of a note set in its [Commitment Merkle Mountain Range](bedrock-v1.1-mantle-specification.md#commitment-merkle-mountain-range) (MMR).

## Op Proofs

```schema
OpsProofs = *OpProof ; 1. Lenth must equal OpCount
                     ; 2. OpProof variant is derived from the corresponding Op.
                     ;    That is, type(OpProofs[i]) == ProofFor(Op[i])

OpProof   = Ed25519SigProof /
            ZkTransferProof /
            ZkTransferAndEd25519SigProof /
            ChannelInscribeOpProof /
            ChannelConfigOpProof /
            EmptyProof

Ed25519SigProof              = Ed25519Signature
ZkTransferProof              = ZkTransfer
ZkTransferAndEd25519SigProof = ZkTransfer Ed25519Signature
ChannelInscribeOpProof       = Ed25519Signature *ZkTransfer ; one ZkTransfer per step of the inscription
ChannelConfigOpProof         = ChannelMultiSigProof
EmptyProof                   = 0Byte ; no bytes

ChannelMultiSigProof = SignatureCount *IndexedSignature
IndexedSignature     = SignerIndex Ed25519Signature

SignatureCount = UINT16
SignerIndex    = UINT16
```

## Common Structures

```schema
; Zero-knowledge transfer proof
ZkTransfer = Groth16

; Cryptographic primitives
Groth16          = 128BYTE      ; pi_a (32) + pi_b (64) + pi_c (32)
ZkPublicKey      = FieldElement
Ed25519PublicKey = 32BYTE
Ed25519Signature = 64BYTE
FieldElement     = 32BYTE      ; BN254 field element (little-endian), less than p
Hash32           = 32BYTE

; Primitive types
UINT64 = 8BYTE ; 64-bit unsigned integer, little-endian
UINT32 = 4BYTE ; 32-bit unsigned integer, little-endian
UINT16 = 2BYTE ; 16-bit unsigned integer, little-endian
Byte   = OCTET
```
