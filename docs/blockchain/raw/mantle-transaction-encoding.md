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
| 2.0.0 | Follow the private note ledger of Mantle 2.0.0: nullifier inputs and commitment outputs with their `CmMerkleRoot` and `Value`, channel steps in the `MiniBlocks` of `ChannelInscribe`, holder withdrawals, the SDP payloads over notes, `PowNonce` in `ClaimPowReward`, the `ZkTransfer` proof variants, and the removal of `ChannelTransfer`, `TransferThreshold` and `LeaderClaim`. A `FieldElement` not less than $`p`$ is rejected | 2026-10-06 |
| 2.1.0 | Follow the programs of Mantle 2.1.0: the `ProgramRegister` Operation with its `Groth16VerificationKey`, user and program steps in the `MiniBlocks` of `ChannelInscribe` with their proofs and the openings of the program notes, the payments of program steps, the `Groth16` terminal renamed `Groth16Proof`, and the format of compressed points | 2026-10-12 |

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
            ClaimPowReward /
            ProgramRegister
```

### Channel Operations

```schema
ChannelInscribe = ChannelId Inscription Parent Signer MiniBlocks
Inscription     = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes
MiniBlocks      = MiniBlockCount *MiniBlock
MiniBlockCount  = UINT16
MiniBlock       = StepCount *Step ; StepCount at least 1, a decoder MUST reject 0
StepCount       = UINT16
Step            = (UserStepKind UserStep) / (ProgramStepKind ProgramStep)
UserStepKind    = %x00
ProgramStepKind = %x01
UserStep        = Inputs Outputs CommitmentRoot
ProgramStep     = ProgramId Payments Inputs Outputs ProgramOutputs CommitmentRoot SpendNotesHash
Payments        = PaymentCount *Payment
PaymentCount    = Byte
Payment         = Inputs Outputs CommitmentRoot Value Intent
Intent          = FieldElement
ProgramOutputs  = Byte ; bit i (least significant first) set when output i is a note of the program,
                       ; the bits from OutputCount up being 0
SpendNotesHash  = FieldElement

ChannelConfig     = ChannelId Parent KeyCount *Signer PostingTimeframe PostingTimeout ConfigThreshold
KeyCount                   = UINT16
PostingTimeframe           = UINT32
PostingTimeout             = UINT32
ConfigThreshold            = UINT16

ChannelDeposit    = ChannelId Inputs CommitmentRoot Outputs Value DepositMetadata
DepositMetadata   = UINT32 *BYTE ; Max MAX_OPERATION_DATA_SIZE bytes

ChannelWithdraw   = ChannelId Inputs CommitmentRoot Outputs

ChannelId         = Hash32
Parent            = Hash32
Signer            = Ed25519PublicKey
```

A `UserStep` moves the user notes of its holder, a `ProgramStep` executes a program, paid by its `Payment`s with their `Intent`, the hash of what each user expects, and `SpendNotesHash` is the hash of the notes of its program spend. A `MiniBlock` groups the steps whose user steps and payments cover the same transaction buffer. [CHANNEL_INSCRIBE](bedrock-v1.1-mantle-specification.md#channel_inscribe) defines them.

`MAX_OPERATION_DATA_SIZE` MUST be exactly **1,835,008 bytes**. The payloads of `ChannelInscribe.Inscription` and `ChannelDeposit.Metadata` MUST each be at most `MAX_OPERATION_DATA_SIZE` bytes, excluding the outer `UINT32` length prefix. A decoder MUST reject either field when its declared or decoded payload length exceeds the limit.

A decoder MUST reject a `ProgramStep` whose `OutputCount` exceeds 8, or whose `ProgramOutputs` has a bit set at or above its `OutputCount`, so that a step has a single encoding.

### SDP Operations

```schema
SDPDeclare    = ServiceType Locators ProviderId ZkId Inputs CommitmentRoot Value
ServiceType   = Byte          ; 0 = BN
Locators      = LocatorCount *Locator
LocatorCount  = Byte          ; Max 8
Locator       = 2Byte *BYTE   ; Max 329 bytes, multiaddr binary form
ProviderId    = Ed25519PublicKey
ZkId          = ZkPublicKey

SDPWithdraw   = DeclarationId Nonce NoteNullifier Outputs Value
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
ClaimPowReward = EpochNonce BlockHash ZkPublicKey PowNonce
EpochNonce     = FieldElement ; the epoch nonce the solution was found against
BlockHash      = Hash32       ; recent canonical block the solution is anchored to
PowNonce       = FieldElement ; value searched for a ticket satisfying the reward threshold
```

### Program Operations

```schema
ProgramRegister       = Groth16VerificationKey
Groth16VerificationKey = Alpha Beta Gamma Delta IC
Alpha                 = G1Point
Beta                  = G2Point
Gamma                 = G2Point
Delta                 = G2Point
IC                    = 4G1Point ; one point per public input of a program proof, plus one
ProgramId             = FieldElement
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

Commitments and nullifiers are defined in [Note Commitment and Nullifier](bedrock-v1.1-mantle-specification.md#note-commitment-and-nullifier) of Mantle.

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
ChannelInscribeOpProof       = Ed25519Signature *StepProof ; one StepProof per step of the inscription
StepProof                    = ZkTransfer / ProgramStepProof ; ZkTransfer for a user step,
                                                             ; ProgramStepProof for a program step
ProgramStepProof             = *ZkTransfer ZkProgramSpend Groth16Proof *ProgramNoteOpening
                                                       ; one ZkTransfer per payment, the program spend,
                                                       ; the program proof, then one opening per bit set
                                                       ; in the ProgramOutputs of the step
ProgramNoteOpening           = Value NoteNonce ZkPublicKey ProgramNoteData
NoteNonce                    = FieldElement
ProgramNoteData              = FieldElement
ChannelConfigOpProof         = ChannelMultiSigProof
EmptyProof                   = 0Byte ; no bytes

ChannelMultiSigProof = SignatureCount *IndexedSignature
IndexedSignature     = SignerIndex Ed25519Signature

SignatureCount = UINT16
SignerIndex    = UINT16
```

## Common Structures

```schema
; Zero-knowledge transfer proofs
ZkTransfer     = Groth16Proof
ZkProgramSpend = Groth16Proof

; Cryptographic primitives
Groth16Proof     = 128BYTE      ; pi_a (G1Point) + pi_b (G2Point) + pi_c (G1Point)
G1Point          = 32BYTE       ; compressed BN254 G1 point
G2Point          = 64BYTE       ; compressed BN254 G2 point
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

A `G1Point` holds the coordinate `x` of the point as 32 little-endian bytes. A `G2Point` holds `x = c0 + c1 * u` as `c0` then `c1`, each as 32 little-endian bytes. The two top bits of the last byte are flags, not part of the coordinate:

- Bit 7 is set when `y` is the larger of `y` and `-y`. Elements of the base field compare as integers, and elements of its quadratic extension by `c1`, then by `c0`.
- Bit 6 flags the point at infinity, which has no encoding: a decoder MUST reject a point with bit 6 set.

A decoder MUST also reject a coordinate not less than the modulus $`q`$ of the base field of BN254, so that a point has a single encoding.
