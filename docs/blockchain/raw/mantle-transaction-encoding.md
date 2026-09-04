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
| 1.7.0 | [RFC] SDP Operations address a declaration by `ZkId` instead of `DeclarationId`, and `SDPWithdraw` drops the redundant `ServiceNoteId` | 2026-09-01 |

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
            ChannelTransfer /
            SDPDeclare /
            SDPWithdraw /
            SDPActive /
            LeaderClaim 
```

### Channel Operations

```schema
ChannelInscribe = ChannelId Inscription Parent Signer
Inscription     = UINT32 *BYTE 

ChannelConfig     = ChannelId Parent KeyCount *Signer PostingTimeframe PostingTimeout ConfigThreshold TransferThreshold
KeyCount                   = UINT16
PostingTimeframe           = UINT32
PostingTimeout             = UINT32
ConfigThreshold            = UINT16
TransferThreshold          = UINT16

ChannelDeposit    = ChannelId Inputs Metadata
Inputs            = InputCount *NoteId
InputCount        = Byte
Metadata          = UINT32 *BYTE

ChannelTransfer = ChannelId Inputs Outputs

ChannelWithdraw   = ChannelId Inputs

ChannelId         = Hash32
Parent            = Hash32
Signer            = Ed25519PublicKey
Outputs           = OutputCount *Note
OutputCount       = Byte
Inputs            = InputCount *NoteId
```

### SDP Operations

```schema
SDPDeclare    = ServiceType Locators ProviderId ZkId ServiceNoteId
ServiceType   = Byte          ; 0 = BN
Locators      = LocatorCount *Locator
LocatorCount  = Byte          ; Max 8
Locator       = 2Byte *BYTE   ; Max 329 bytes, multiaddr binary form
ProviderId    = Ed25519PublicKey
ZkId          = ZkPublicKey
ServiceNoteId = NoteId

SDPWithdraw   = ZkId Nonce
Nonce         = UINT64

SDPActive     = ZkId Nonce Metadata
Metadata      = UINT32 *BYTE  ; Service-specific node activeness metadata
```

### Leader operations

```schema
LeaderClaim      = RewardsRoot VoucherNullifier PublicKey
RewardsRoot      = FieldElement ; Merkle root for voucher membership proof
VoucherNullifier = FieldElement
PublicKey        = ZkPublicKey
```

### Transfer Operations

```schema
Transfer    = Inputs Outputs
Inputs      = InputCount *NoteId
InputCount  = Byte
Outputs     = OutputCount *Note
OutputCount = Byte
```

## Ledger

```schema
Note   = Value ZkPublicKey
Value  = UINT64
NoteId = FieldElement
```

## Op Proofs

```schema
OpsProofs = *OpProof ; 1. Lenth must equal OpCount
                     ; 2. OpProof variant is derived from the corresponding Op.
                     ;    That is, type(OpProofs[i]) == ProofFor(Op[i])

OpProof   = Ed25519SigProof /
            ZkSigProof /
            ZkAndEd25519SigsProof /
            ChannelWithdrawOpProof /
            ProofOfClaimProof

Ed25519SigProof         = Ed25519Signature
ZkSigProof              = ZkSignature
ZkAndEd25519SigsProof   = ZkSignature Ed25519Signature
ChannelWithdrawOpProof  = SignatureCount *Ed25519Signature
ProofOfClaimProof       = Groth16

SignatureCount = UINT16
```

## Common Structures

```schema
; Zero-knowledge signature
ZkSignature = Groth16

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
