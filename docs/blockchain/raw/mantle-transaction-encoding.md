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
| 2.0.0 | Follow the private note ledger of Mantle 2.0.0: channel steps in `ChannelInscribe`, holder withdrawals, and the removal of `ChannelTransfer`, `TransferThreshold` and `LeaderClaim` | 2026-10-06 |

# Introduction

This document specifies the canonical encoding of Mantle transactions (see [Mantle - Mantle Transaction](bedrock-v1.1-mantle-specification.md)) and its sub-components. Transactions sent through the mempool and included in blocks use this encoding.

# Overview

The transaction encoding is specified in ABNF form to remove any ambiguity and guarantee a canonical encoding. The high level encoding choices which were not immediately derivable from the Mantle specification are listed here:

1. All multi-byte integers use little-endian encoding
1. Any lists are length-prefixed with fixed width uints
1. We derive number of proofs and type of proof from the Ops list parsed earlier

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
ChannelInscribe = ChannelId Inscription Parent Signer Steps
Inscription     = UINT32 *BYTE 
Steps           = StepCount *ChannelStep
StepCount       = UINT16
ChannelStep     = Inputs Outputs CmMerkleRoot

ChannelConfig     = ChannelId Parent KeyCount *Signer PostingTimeframe PostingTimeout ConfigThreshold
KeyCount                   = UINT16
PostingTimeframe           = UINT32
PostingTimeout             = UINT32
ConfigThreshold            = UINT16

ChannelDeposit    = ChannelId Inputs CmMerkleRoot Outputs Value Metadata
Metadata          = UINT32 *BYTE

ChannelWithdraw   = ChannelId Inputs CmMerkleRoot Outputs Value

ChannelId         = Hash32
Parent            = Hash32
Signer            = Ed25519PublicKey
```

### SDP Operations

```schema
SDPDeclare    = ServiceType Locators ProviderId ZkId Inputs CmMerkleRoot Value
ServiceType   = Byte          ; 0 = BN
Locators      = LocatorCount *Locator
LocatorCount  = Byte          ; Max 8
Locator       = 2Byte *BYTE   ; Max 329 bytes, multiaddr binary form
ProviderId    = Ed25519PublicKey
ZkId          = ZkPublicKey

SDPWithdraw   = DeclarationId Nonce NoteNf Outputs Value
DeclarationId = Hash32
Nonce         = UINT64

SDPActive     = DeclarationId Nonce Metadata
Metadata      = UINT32 *BYTE  ; Service-specific node activeness metadata
```

### Proof of work operations

```schema
ClaimPowReward = EpochNonce BlockHash ZkPublicKey PowNonce
EpochNonce     = FieldElement ; the epoch nonce the solution was found against
BlockHash      = Hash32       ; recent canonical block the solution is anchored to
PowNonce       = FieldElement ; value searched for a ticket satisfying the reward threshold
```

### Transfer Operations

```schema
Transfer    = Inputs Outputs CmMerkleRoot Value
Inputs      = InputCount *NoteNf
InputCount  = Byte
Outputs     = OutputCount *NoteCm
OutputCount = Byte
```

## Ledger

```schema
Value        = UINT64
NoteCm       = FieldElement
NoteNf       = FieldElement
CmMerkleRoot = FieldElement ; MMR root of note commitments
```

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
FieldElement     = 32BYTE      ; BN254 field element (little-endian)
Hash32           = 32BYTE

; Primitive types
UINT64 = 8BYTE ; 64-bit unsigned integer, little-endian
UINT32 = 4BYTE ; 32-bit unsigned integer, little-endian
UINT16 = 2BYTE ; 16-bit unsigned integer, little-endian
Byte   = OCTET
```
