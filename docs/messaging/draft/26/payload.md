# 26/WAKU2-PAYLOAD

| Field | Value |
| --- | --- |
| Name | Waku Message Payload Encryption |
| Slug | 26 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Oskar Thoren <oskarth@titanproxy.com> |
| Contributors | Oskar Thoren <oskarth@titanproxy.com> |

<!-- timeline:start -->

## Timeline

- **2026-04-20** — [`c3d15a9`](https://github.com/logos-co/logos-lips/blob/c3d15a9c7c24b4d6b0eb4fb578f9670ede6f69b0/docs/messaging/standards/application/26/payload.md) — COSS overhaul: new statuses, CFR type, raw-spec leniency (#308)
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/application/26/payload.md) — chore: add math support (#287)
- **2026-01-30** — [`d5a9240`](https://github.com/logos-co/logos-lips/blob/d5a9240c6c6c859eddd30742b2251f8a13480cf9/docs/messaging/standards/application/26/payload.md) — chore: removed archived (#283)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/application/26/payload.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/application/26/payload.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/application/26/payload.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/application/26/payload.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/application/26/payload.md) — ci: add mdBook configuration (#233)
- **2025-03-31** — [`f08de10`](https://github.com/logos-co/logos-lips/blob/f08de108457eed828dadbd36339433c586701267/waku/standards/application/26/payload.md) — 26/WAKU2-PAYLOADS: Update (#136)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/application/26/payload.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/application/26/payload.md) — Broken Links + Change Editors (#26)
- **2024-01-31** — [`33cf551`](https://github.com/logos-co/logos-lips/blob/33cf551676123ef90340f5fa909084675d51e8cd/waku/standards/application/26/payload.md) — Update payload.md
- **2024-01-31** — [`29acb80`](https://github.com/logos-co/logos-lips/blob/29acb80f5333aaa5f5e829520fa49d2820bd550e/waku/standards/application/26/payload.md) — Rename README.md to payload.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/application/26/README.md) — remove rfs folder
- **2024-01-25** — [`7bd0712`](https://github.com/logos-co/logos-lips/blob/7bd071220d54b345d477bf4041c593c4da4d4a53/waku/rfcs/standards/application/26/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

This specification describes how Waku provides confidentiality, authenticity, and
integrity, as well as some form of unlinkability.
Specifically, it describes how encryption, decryption and
signing works in [6/WAKU1](../../stable/6/waku1.md) and
in [10/WAKU2](../10/waku2.md) with [14/WAKU-MESSAGE](../../stable/14/message.md#version1).

This specification effectively replaces [7/WAKU-DATA](../../stable/7/data.md)
as well as [6/WAKU1 Payload encryption](../../stable/6/waku1.md#payload-encryption)
but written in a way that is agnostic and self-contained for [6/WAKU1](../../stable/6/waku1.md) and [10/WAKU2](../10/waku2.md).

Large sections of the specification originate from
[EIP-627: Whisper spec](https://eips.ethereum.org/EIPS/eip-627) as well from
[RLPx Transport Protocol spec (ECIES encryption)](https://github.com/ethereum/devp2p/blob/master/rlpx.md#ecies-encryption)
with some modifications.

## Specification

The keywords “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

For [6/WAKU1](../../stable/6/waku1.md),
the `data` field is used in the [waku envelope](../../stable/6/waku1.md#abnf-specification)
and the field MAY contain the encrypted payload.

For [10/WAKU2](../10/waku2.md),
the `payload` field is used in `WakuMessage`
and MAY contain the encrypted payload.

The fields that are concatenated and
encrypted as part of the `data` (Waku legacy) or
`payload` (Waku) field are:

- `flags`
- `payload-length`
- `payload`
- `padding`
- `signature`

## Design requirements

- *Confidentiality*:
The adversary SHOULD NOT be able to learn what data is being sent from one Waku node
to one or several other Waku nodes.
- *Authenticity*:
The adversary SHOULD NOT be able to cause Waku endpoint
to accept data from any third party as though it came from the other endpoint.
- *Integrity*:
The adversary SHOULD NOT be able to cause a Waku endpoint to
accept data that has been tampered with.

Notable, *forward secrecy* is not provided for at this layer.
If this property is desired,
a more fully featured secure communication protocol can be used on top.

It also provides some form of *unlinkability* since:

- only participants who are able to decrypt a message can see its signature
- payload are padded to a fixed length

## Cryptographic primitives

- AES-256-GCM (for symmetric encryption)
- ECIES
- ECDSA
- KECCAK-256

ECIES is using the following cryptosystem:

- Curve: secp256k1
- KDF: NIST SP 800-56 Concatenation Key Derivation Function, with SHA-256 option
- MAC: HMAC with SHA-256
- AES: AES-128-CTR

### ABNF

Using [Augmented Backus-Naur form (ABNF)](https://tools.ietf.org/html/rfc5234)
we have the following format:

```abnf
; 1 byte; first two bits contain the size of payload-length field,
; third bit indicates whether the signature is present.
flags           = 1OCTET

; contains the size of payload.
payload-length  = 4*OCTET

; byte array of arbitrary size (may be zero).
payload         = *OCTET

; byte array of arbitrary size (may be zero).
padding         = *OCTET

; 65 bytes, if present.
signature       = 65OCTET

data            = flags payload-length payload padding [signature]

; This field is called payload in Waku
payload         = data
```

### Signature

Those unable to decrypt the payload/data are also unable to access the signature.
The signature, if provided,
SHOULD be the ECDSA signature of the Keccak-256 hash of the unencrypted data
using the secret key of the originator identity.
The signature is serialized as the concatenation of the `r`, `s` and `v` parameters
of the SECP-256k1 ECDSA signature, in that order.
`r` and `s` MUST be big-endian encoded, fixed-width 256-bit unsigned.
`v` MUST be an 8-bit big-endian encoded,
non-normalized and should be either 27 or 28.

See [Ethereum "Yellow paper": Appendix F Signing transactions](https://ethereum.github.io/yellowpaper/paper.pdf)
for more information on signature generation, parameters and public key recovery.

### Encryption

#### Symmetric

Symmetric encryption uses AES-256-GCM for
[authenticated encryption](https://en.wikipedia.org/wiki/Authenticated_encryption).
The output of encryption is of the form (`ciphertext`, `tag`, `iv`)
where `ciphertext` is the encrypted message,
`tag` is a 16 byte message authentication tag and
`iv` is a 12 byte initialization vector (nonce).
The message authentication `tag` and
initialization vector `iv` field MUST be appended to the resulting `ciphertext`,
in that order.
Note that previous specifications and
some implementations might refer to `iv` as `nonce` or `salt`.

#### Asymmetric

Asymmetric encryption uses the standard Elliptic Curve Integrated Encryption Scheme
(ECIES) with SECP-256k1 public key.

#### ECIES

This section originates from the [RLPx Transport Protocol spec](https://github.com/ethereum/devp2p/blob/master/rlpx.md#ecies-encryption)
specification with minor modifications.

The cryptosystem used is:

- The elliptic curve secp256k1 with generator `G`.
- `KDF(k, len)`: the NIST SP 800-56 Concatenation Key Derivation Function.
- `MAC(k, m)`: HMAC using the SHA-256 hash function.
- `AES(k, iv, m)`: the AES-128 encryption function in CTR mode.

Special notation used: `X || Y` denotes concatenation of `X` and `Y`.

Alice wants to send an encrypted message that can be decrypted by
Bob's static private key `kB`.
Alice knows about Bobs static public key `KB`.

To encrypt the message `m`, Alice generates a random number `r` and
corresponding elliptic curve public key `R = r * G` and
computes the shared secret `S = Px` where `(Px, Py) = r * KB`.
She derives key material for encryption and
authentication as `kE || kM = KDF(S, 32)`
as well as a random initialization vector `iv`.
Alice sends the encrypted message `R || iv || c || d` where `c = AES(kE, iv , m)`
and `d = MAC(sha256(kM), iv || c)` to Bob.

For Bob to decrypt the message `R || iv || c || d`,
he derives the shared secret `S = Px` where `(Px, Py) = kB * R`
as well as the encryption and authentication keys `kE || kM = KDF(S, 32)`.
Bob verifies the authenticity of the message
by checking whether `d == MAC(sha256(kM), iv || c)`
then obtains the plaintext as `m = AES(kE, iv || c)`.

### Padding

The `padding` field is used to align data size,
since data size alone might reveal important metainformation.
Padding can be arbitrary size.
However, it is recommended that the size of `data` field
(excluding the `iv` and `tag`) before encryption (i.e. plain text)
SHOULD be a multiple of 256 bytes.

### Decoding a message

In order to decode a message, a node SHOULD try to apply both symmetric and
asymmetric decryption operations.
This is because the type of encryption is not included in the message.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [6/WAKU1](../../stable/6/waku1.md)
2. [10/WAKU2 spec](../10/waku2.md)
3. [14/WAKU-MESSAGE version 1](../../stable/14/message.md#version1)
4. [7/WAKU-DATA](../../stable/7/data.md)
5. [EIP-627: Whisper spec](https://eips.ethereum.org/EIPS/eip-627)
6. [RLPx Transport Protocol spec (ECIES encryption)](https://github.com/ethereum/devp2p/blob/master/rlpx.md#ecies-encryption)
7. [Status 5/SECURE-TRANSPORT](https://github.com/status-im/status-specs/tree/master/specs/status/deprecated/secure-transport.md)
8. [Augmented Backus-Naur form (ABNF)](https://tools.ietf.org/html/rfc5234)
9. [Ethereum "Yellow paper": Appendix F Signing transactions](https://ethereum.github.io/yellowpaper/paper.pdf)
10. [authenticated encryption](https://en.wikipedia.org/wiki/Authenticated_encryption)
