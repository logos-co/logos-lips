# NOISE-X3DH-DOUBLE-RATCHET

| Field | Value |
| --- | --- |
| Name | Secure 1-to-1 channel setup using X3DH and the double ratchet |
| Slug | 108 |
| Status | raw |
| Category | Standards Track |
| Editor | Ramses Fernandez <ramses@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/anoncomms/raw/noise-x3dh-double-ratchet.md) — chore: split ift ts specs
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/noise-x3dh-double-ratchet.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/noise-x3dh-double-ratchet.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/noise-x3dh-double-ratchet.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/noise-x3dh-double-ratchet.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/noise-x3dh-double-ratchet.md) — ci: add mdBook configuration (#233)
- **2025-04-04** — [`517b639`](https://github.com/logos-co/logos-lips/blob/517b63984c875670e437d50359f2f67331104974/vac/raw/noise-x3dh-double-ratchet.md) — Update the RFCs: Vac Raw RFC (#143)
- **2024-10-03** — [`c655980`](https://github.com/logos-co/logos-lips/blob/c655980494a5943634c372009bbea71c13196a8f/vac/raw/eth-secure-channel.md) — Eth secpm splitted (#91)

<!-- timeline:end -->

## Motivation

The need for secure communications has become paramount.
This specification outlines a protocol describing a
secure 1-to-1 comunication channel between 2 users. The
main components are the X3DH key establishment mechanism,
combined with the double ratchet. The aim of this
combination of schemes is providing a protocol with both
forward secrecy and post-compromise security.

## Theory

The specification is based on the noise protocol framework.
It corresponds to the double ratchet scheme combined with
the X3DH algorithm, which will be used to initialize the former.
We chose to express the protocol in noise to be be able to use
the noise streamlined implementation and proving features.
The X3DH algorithm provides both authentication and forward
secrecy, as stated in the
[X3DH specification](https://signal.org/docs/specifications/x3dh/).

This protocol will consist of several stages:

1. Key setting for X3DH: this step will produce
prekey bundles for Bob which will be fed into X3DH.
It will also allow Alice to generate the keys required
to run the X3DH algorithm correctly.
2. Execution of X3DH: This step will output
a common secret key `SK` together with an additional
data vector `AD`. Both will be used in the double
ratchet algorithm initialization.
3. Execution of the double ratchet algorithm
for forward secure, authenticated communications,
using the common secret key `SK`, obtained from X3DH, as a root key.

The protocol assumes the following requirements:

- Alice knows Bob’s Ethereum address.
- Bob is willing to participate in the protocol,
and publishes his public key.
- Bob’s ownership of his public key is verifiable,
- Alice wants to send message M to Bob.
- An eavesdropper cannot read M’s content
even if she is storing it or relaying it.

## Syntax

### Cryptographic suite

The following cryptographic functions MUST be used:

- `X488` as Diffie-Hellman function `DH`.
- `SHA256` as KDF.
- `AES256-GCM` as AEAD algorithm.
- `SHA512` as hash function.
- `XEd448` for digital signatures.

### X3DH initialization

This scheme MUST work on the curve curve448.
The X3DH algorithm corresponds to the IX pattern in Noise.

Bob and Alice MUST define personal key pairs
`(ik_B, IK_B)` and `(ik_A, IK_A)` respectively where:

- The key `ik` must be kept secret,
- and the key `IK` is public.

Bob MUST generate new keys using
`(ik_B, IK_B) = GENERATE_KEYPAIR(curve = curve448)`.

Bob MUST also generate a public key pair
`(spk_B, SPK_B) = GENERATE_KEYPAIR(curve = curve448)`.

`SPK` is a public key generated and stored at medium-term.
Both signed prekey and the certificate MUST
undergo periodic replacement.
After replacing the key,
Bob keeps the old private key of `SPK`
for some interval, dependant on the implementation.
This allows Bob to decrypt delayed messages.

Bob MUST sign `SPK` for authentication:
`SigSPK = XEd448(ik, Encode(SPK))`

A final step requires the definition of
`prekey_bundle = (IK, SPK, SigSPK, OPK_i)`

One-time keys `OPK` MUST be generated as
`(opk_B, OPK_B) = GENERATE_KEYPAIR(curve = curve448)`.

Before sending an initial message to Bob,
Alice MUST generate an AD: `AD = Encode(IK_A) || Encode(IK_B)`.

Alice MUST generate ephemeral key pairs
`(ek, EK) = GENERATE_KEYPAIR(curve = curve448)`.

The function `Encode()` transforms a
curve448 public key into a byte sequence.
This is specified in the [RFC 7748](http://www.ietf.org/rfc/rfc7748.txt)
on elliptic curves for security.

One MUST consider `q = 2^446 - 13818066809895115352007386748515426880336692474882178609894547503885`
for digital signatures with `(XEd448_sign, XEd448_verify)`:

```text
XEd448_sign((ik, IK), message):
    Z = randbytes(64)  
    r = SHA512(2^456 - 2 || ik || message || Z )
    R = (r * convert_mont(5)) % q
    h = SHA512(R || IK || M)
    s = (r + h * ik) % q
    return (R || s)
```

```text
XEd448_verify(u, message, (R || s)):
    if (R.y >= 2^448) or (s >= 2^446): return FALSE
    h = (SHA512(R || 156326 || message)) % q
    R_check = s * convert_mont(5) - h * 156326
    if R == R_check: return TRUE
    return FALSE 
```

```text
convert_mont(u):
    u_masked = u % mod 2^448
    inv = ((1 - u_masked)^(2^448 - 2^224 - 3)) % (2^448 - 2^224 - 1)
    P.y = ((1 + u_masked) * inv)) % (2^448 - 2^224 - 1)
    P.s = 0
    return P
```

### Use of X3DH

This specification combines the double ratchet
with X3DH using the following data as initialization for the former:

- The `SK` output from X3DH becomes the `SK`
input of the double ratchet. See section 3.3 of
[Signal Specification](https://signal.org/docs/specifications/doubleratchet/)
for a detailed description.
- The `AD` output from X3DH becomes the `AD`
input of the double ratchet. See sections 3.4 and 3.5 of
[Signal Specification](https://signal.org/docs/specifications/doubleratchet/)
for a detailed description.
- Bob’s signed prekey `SigSPKB` from X3DH is used as Bob’s
initial ratchet public key of the double ratchet.

X3DH has three phases:

1. Bob publishes his identity key and prekeys to a server,
a network, or dedicated smart contract.
2. Alice fetches a prekey bundle from the server,
and uses it to send an initial message to Bob.
3. Bob receives and processes Alice's initial message.

Alice MUST perform the following computations:

```text
dh1 = DH(IK_A, SPK_B, curve = curve448)
dh2 = DH(EK_A, IK_B, curve = curve448)
dh3 = DH(EK_A, SPK_B)
SK = KDF(dh1 || dh2 || dh3)
```

Alice MUST send to Bob a message containing:

- `IK_A, EK_A`.
- An identifier to Bob's prekeys used.
- A message encrypted with AES256-GCM using `AD` and `SK`.

Upon reception of the initial message, Bob MUST:

1. Perform the same computations above with the `DH()` function.
2. Derive `SK` and construct `AD`.
3. Decrypt the initial message encrypted with `AES256-GCM`.
4. If decryption fails, abort the protocol.

### Initialization of the double datchet

In this stage Bob and Alice have generated key pairs
and agreed a shared secret `SK` using X3DH.

Alice calls `RatchetInitAlice()` defined below:

```text
RatchetInitAlice(SK, IK_B):
    state.DHs = GENERATE_KEYPAIR(curve = curve448)
    state.DHr = IK_B
    state.RK, state.CKs = HKDF(SK, DH(state.DHs, state.DHr)) 
    state.CKr = None
    state.Ns, state.Nr, state.PN = 0
    state.MKSKIPPED = {}
```

The HKDF function MUST be the proposal by
[Krawczyk and Eronen](http://www.ietf.org/rfc/rfc5869.txt).
In this proposal `chaining_key` and `input_key_material`
MUST be replaced with `SK` and the output of `DH` respectively.

Similarly, Bob calls the function `RatchetInitBob()` defined below:

```text
RatchetInitBob(SK, (ik_B,IK_B)):
    state.DHs = (ik_B, IK_B)
    state.Dhr = None
    state.RK = SK
    state.CKs, state.CKr = None
    state.Ns, state.Nr, state.PN = 0
    state.MKSKIPPED = {}
```

### Encryption

This function performs the symmetric key ratchet.

```text
RatchetEncrypt(state, plaintext, AD):
   state.CKs, mk = HMAC-SHA256(state.CKs)
   header = HEADER(state.DHs, state.PN, state.Ns)
   state.Ns = state.Ns + 1
   return header, AES256-GCM_Enc(mk, plaintext, AD || header)
```

The `HEADER` function creates a new message header
containing the public key from the key pair output of the `DH`function.
It outputs the previous chain length `pn`,
and the message number `n`.
The returned header object contains ratchet public key
`dh` and integers `pn` and `n`.

### Decryption

The function `RatchetDecrypt()` decrypts incoming messages:

```text
RatchetDecrypt(state, header, ciphertext, AD):
    plaintext = TrySkippedMessageKeys(state, header, ciphertext, AD)
    if plaintext != None:
        return plaintext
    if header.dh != state.DHr:
        SkipMessageKeys(state, header.pn)
        DHRatchet(state, header)
    SkipMessageKeys(state, header.n)
    state.CKr, mk = HMAC-SHA256(state.CKr)
    state.Nr = state.Nr + 1
    return AES256-GCM_Dec(mk, ciphertext, AD || header)
```

Auxiliary functions follow:

```text
DHRatchet(state, header):
    state.PN = state.Ns
    state.Ns = state.Nr = 0
    state.DHr = header.dh
    state.RK, state.CKr = HKDF(state.RK, DH(state.DHs, state.DHr))
    state.DHs = GENERATE_KEYPAIR(curve = curve448)
    state.RK, state.CKs = HKDF(state.RK, DH(state.DHs, state.DHr))
```

```text
SkipMessageKeys(state, until):
    if state.NR + MAX_SKIP < until:
        raise Error
    if state.CKr != none:
        while state.Nr < until:
            state.CKr, mk = HMAC-SHA256(state.CKr)
            state.MKSKIPPED[state.DHr, state.Nr] = mk
            state.Nr = state.Nr + 1
```

```text
TrySkippedMessageKey(state, header, ciphertext, AD):
    if (header.dh, header.n) in state.MKSKIPPED:
        mk = state.MKSKIPPED[header.dh, header.n]
        delete state.MKSKIPPED[header.dh, header.n]
        return AES256-GCM_Dec(mk, ciphertext, AD || header)
    else: return None
```

## Information retrieval

### Static data

Some data, such as the key pairs `(ik, IK)` for Alice and Bob,
MAY NOT be regenerated after a period of time.
Therefore the prekey bundle MAY be stored in long-term
storage solutions, such as a dedicated smart contract
which outputs such a key pair when receiving an Ethereum wallet
address.

Storing static data is done using a dedicated
smart contract `PublicKeyStorage` which associates
the Ethereum wallet address of a user with his public key.
This mapping is done by `PublicKeyStorage`
using a `publicKeys` function, or a `setPublicKey` function.
This mapping is done if the user passed an authorization process.
A user who wants to retrieve a public key associated
with a specific wallet address calls a function `getPublicKey`.
The user provides the wallet address as the only
input parameter for `getPublicKey`.
The function outputs the associated public key
from the smart contract.

### Ephemeral data

Storing ephemeral data on Ethereum MAY be done using
a combination of on-chain and off-chain solutions.
This approach provides an efficient solution to
the problem of storing updatable data in Ethereum.

1. Ethereum stores a reference or a hash
that points to the off-chain data.
2. Off-chain solutions can include systems like IPFS,
traditional cloud storage solutions, or
decentralized storage networks such as a
[Swarm](https://www.ethswarm.org).

In any case, the user stores the associated
IPFS hash, URL or reference in Ethereum.

The fact of a user not updating the ephemeral information
can be understood as Bob not willing to participate in any
communication.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [The Double Ratchet Algorithm](https://signal.org/docs/specifications/doubleratchet/)
- [The X3DH Key Agreement Protocol](https://signal.org/docs/specifications/x3dh/)
