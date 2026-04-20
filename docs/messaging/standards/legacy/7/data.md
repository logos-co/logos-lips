# 7/WAKU-DATA

| Field | Value |
| --- | --- |
| Name | Waku Envelope data field |
| Slug | 7 |
| Status | stable |
| Type | RFC |
| Category | Standards Track |
| Editor | Oskar Thorén <oskarth@titanproxy.com> |
| Contributors | Dean Eigenmann <dean@status.im>, Kim De Mey <kimdemey@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/legacy/7/data.md) — chore: add math support (#287)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/legacy/7/data.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/legacy/7/data.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/legacy/7/data.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/legacy/7/data.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/legacy/7/data.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/legacy/7/data.md) — Broken Links + Change Editors (#26)
- **2024-02-12** — [`a57d7b4`](https://github.com/logos-co/logos-lips/blob/a57d7b4732eb600c2f9281a26d106d526308ed49/waku/standards/legacy/7/data.md) — Rename data.md to data.md
- **2024-01-31** — [`900a3e9`](https://github.com/logos-co/logos-lips/blob/900a3e92b4d8fd1ecbc4b8cd59429faf6aff4e71/waku/standards/application/7/data.md) — Update and rename DATA.md to data.md
- **2024-01-27** — [`662eb12`](https://github.com/logos-co/logos-lips/blob/662eb12909d9ba09a345fea0864f08f5a780b913/waku/standards/application/7/DATA.md) — Rename README.md to DATA.md
- **2024-01-27** — [`eef961b`](https://github.com/logos-co/logos-lips/blob/eef961bfe3b1cf6aab66df5450555afd1d3543cb/waku/standards/application/07/README.md) — remove rfs folder
- **2024-01-25** — [`93c3896`](https://github.com/logos-co/logos-lips/blob/93c389620d94c46689856a85f3393b8fa50cca2e/waku/rfcs/standards/application/07/README.md) — Create README.md

<!-- timeline:end -->

This specification describes the encryption,
decryption and signing of the content in the [data field used in Waku](../6/waku1.md/#abnf-specification).

## Specification

The `data` field is used within the `waku envelope`,
the field MUST contain the encrypted payload of the envelope.

The fields that are concatenated and encrypted as part of the `data` field are:

- flags
- auxiliary field
- payload
- padding
- signature

In case of symmetric encryption, a `salt`
(a.k.a. AES Nonce, 12 bytes) field MUST be appended.

### ABNF

Using [Augmented Backus-Naur form (ABNF)](https://tools.ietf.org/html/rfc5234)
we have the following format:

```abnf
; 1 byte; first two bits contain the size of auxiliary field, 
; third bit indicates whether the signature is present.
flags           = 1OCTET

; contains the size of payload.
auxiliary-field = 4*OCTET

; byte array of arbitrary size (may be zero)
payload         = *OCTET

; byte array of arbitrary size (may be zero).
padding         = *OCTET

; 65 bytes, if present.
signature       = 65OCTET

; 2 bytes, if present (in case of symmetric encryption).
salt            = 2OCTET

data        = flags auxiliary-field payload padding [signature] [salt]
```

### Signature

Those unable to decrypt the envelope data are also unable to access the signature.
The signature, if provided,
is the ECDSA signature of the Keccak-256 hash of the unencrypted data
using the secret key of the originator identity.
The signature is serialized as the concatenation of the `R`, `S` and
`V` parameters of the SECP-256k1 ECDSA signature, in that order.
`R` and `S` MUST be big-endian encoded, fixed-width 256-bit unsigned.
`V` MUST be an 8-bit big-endian encoded,
non-normalized and should be either 27 or 28.

### Padding

The padding field is used to align data size,
since data size alone might reveal important metainformation.
Padding can be arbitrary size.
However, it is recommended that the size of Data Field (excluding the Salt)
before encryption (i.e. plain text) SHOULD be factor of 256 bytes.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
