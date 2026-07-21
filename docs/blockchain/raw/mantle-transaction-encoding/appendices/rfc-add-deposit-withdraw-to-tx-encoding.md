# [RFC] Add Deposit/Withdraw to Tx Encoding

**Authors:** Youngjoon Lee
**Approvals (research):** Marcin Pawlowski, Thomas Lavaur
**Approvals (engineering):** Daniel Sanchez Quiros, Alex Cabeza Romero

---

## Motivation

[Mantle Transaction Encoding](../../../deprecated/v1.1.0-mantle-transaction-encoding.md) does not cover channel deposit and withdraw operations, even though they have been already added to the [Mantle](../../../deprecated/v1.2.0-mantle.md).
This RFC proposes adding the encoding format of channel deposit and withdraw operations and their proofs to the [Mantle Transaction Encoding](../../../deprecated/v1.1.0-mantle-transaction-encoding.md).
## Proposal

We adapt the Mantle Transaction Encoding to include the Channel Deposit and Channel Withdraw operations as defined below:
- CHANNEL_DEPOSIT
- CHANNEL_WITHDRAW
We add  `ChannelDeposit` and `ChannelWithdraw` to [Operations:](../../mantle-transaction-encoding.md)
```text
OpPayload = Transfer /
    ChannelInscribe /
    ChannelBlob /
    ChannelSetKeys /
+   ChannelDeposit /
+   ChannelWithdraw /
    SDPDeclare /
    SDPWithdraw /
    SDPActive /
    LeaderClaim
```

Then define the structures in [Channel Operations](../../mantle-transaction-encoding.md):
```text
    ChannelSetKeys = ChannelId KeyCount *Signer
    KeyCount       = Byte

+   ChannelDeposit = ChannelId Amount Metadata
+   Amount         = UINT64
+   Metadata       = UINT32 *BYTE

+   ChannelWithdraw = ChannelId Amount

    ChannelId = Hash32
    Parent    = Hash32
    Signer    = Ed25519PublicKey
```

Next we add `ChannelWithdrawOpProof` to [Op Proofs:](../../mantle-transaction-encoding.md)
```text
OpsProofs  = *OpProof ; 1. Lenth must equal OpCount
                      ; 2. OpProof variant is derived from the corresponding Op.
                      ;    That is, type(OpProofs[i]) == ProofFor(Op[i])

OpProof  =  Ed25519SigProof /
    ZkSigProof /
    ZkAndEd25519SigsProof /
+   ChannelWithdrawOpProof /
    ProofOfClaimProof

Ed25519SigProof        = Ed25519Signature
ZkSigProof             = ZkSignature
ZkAndEd25519SigsProof  = ZkSignature Ed25519Signature
+ ChannelWithdrawOpProof = SignatureCount *IndexedEd25519Signature
ProofOfClaimProof      = Groth16

+ SignatureCount          = UINT16
+ ChannelKeyIndex         = UINT16
+ IndexedEd25519Signature = Ed25519Signature ChannelKeyIndex
```

Finally we extend the [Common Structures](../../mantle-transaction-encoding.md) with definition of `UINT16`:
```text
; Zero-knowledge signature
ZkSignature = Groth16

; Cryptographic primitives
Groth16          = 128BYTE      ; pi_a (32) + pi_b (64) + pi_c (32)
ZkPublicKey      = FieldElement
Ed25519PublicKey = 32BYTE
Ed25519Signature = 64BYTE
FieldElement     = 32BYTE       ; BN254 field element (little-endian)
Hash32           = 32BYTE

 ; Primitive types
UINT64    = 8BYTE ; 64-bit unsigned integer, little-endian
UINT32    = 4BYTE ; 32-bit unsigned integer, little-endian
+ UINT16    = 2 BYTE ; 16-bit unsigned integer, little-endian

Byte      = OCTET
```

## Justification

[Mantle Transaction Encoding](../../../deprecated/v1.1.0-mantle-transaction-encoding.md) does not cover channel deposit and withdraw operations, even though they have been already added to the [Mantle](../../../deprecated/v1.2.0-mantle.md).
## Specifications Update

- [v1.2] Mantle Transaction Encoding
