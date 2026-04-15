# ETH-SECPM

| Field | Value |
| --- | --- |
| Name | Secure channel setup using Ethereum accounts |
| Slug | 110 |
| Status | deleted |
| Category | Standards Track |
| Editor | Ramses Fernandez <ramses@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/deleted/eth-secpm.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/deleted/eth-secpm.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/deleted/eth-secpm.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/deleted/eth-secpm.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/deleted/eth-secpm.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/deleted/eth-secpm.md) — ci: add mdBook configuration (#233)
- **2025-06-05** — [`36caaa6`](https://github.com/logos-co/logos-lips/blob/36caaa621a711c7d73b5ecc80e7ba5f938d30691/vac/raw/deleted/eth-secpm.md) — Fix Errors rfc.vac.dev (#165)
- **2025-06-02** — [`db90adc`](https://github.com/logos-co/logos-lips/blob/db90adc94e9f69627dd1254159d33eb062f00867/vac/raw/deleted/eth-secpm.md) — Fix LaTeX errors (#163)
- **2025-04-04** — [`517b639`](https://github.com/logos-co/logos-lips/blob/517b63984c875670e437d50359f2f67331104974/vac/raw/deleted/eth-secpm.md) — Update the RFCs: Vac Raw RFC (#143)
- **2024-08-29** — [`13aaae3`](https://github.com/logos-co/logos-lips/blob/13aaae37d15bdd672c26565bd0e0ebfc2e8b9459/vac/raw/eth-secpm.md) — Update eth-secpm.md (#84)
- **2024-05-21** — [`e234e9d`](https://github.com/logos-co/logos-lips/blob/e234e9d5a30bb4d9d4654285c6118f3d9900a3b9/vac/raw/eth-secpm.md) — Update eth-secpm.md (#35)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/vac/70/eth-secpm.md) — Broken Links + Change Editors (#26)
- **2024-02-28** — [`b842725`](https://github.com/logos-co/logos-lips/blob/b842725d42f1c7d7661808035eff2b0dfa1fca7e/vac/70/eth-secpm.md) — Update eth-secpm.md
- **2024-02-01** — [`f2e1b4c`](https://github.com/logos-co/logos-lips/blob/f2e1b4cd4613f9ab648e42fd00475acf4541649d/vac/70/eth-secpm.md) — Rename ETH-SECPM.md to eth-secpm.md
- **2024-02-01** — [`22bb331`](https://github.com/logos-co/logos-lips/blob/22bb3312fa6ab920281e11c5db190b123c9553b1/vac/70/ETH-SECPM.md) — Update ETH-SECPM.md
- **2024-01-27** — [`5b8ce46`](https://github.com/logos-co/logos-lips/blob/5b8ce46a6b384d6ee4c2d884f9db82b0aee9ce8c/vac/70/ETH-SECPM.md) — Create ETH-SECPM.md

<!-- timeline:end -->

## NOTE

The content of this specification has been split between
[ETH-MLS-OFFCHAIN](/ift-ts/raw/eth-mls-offchain.md) and [NOISE-X3DH-DOUBLE-RATCHET](/ift-ts/raw/noise-x3dh-double-ratchet.md)
LIPs.

## Motivation

The need for secure communications has become paramount.  
Traditional centralized messaging protocols are susceptible to various security threats,
including unauthorized access, data breaches, and single points of failure.
Therefore a decentralized approach to secure communication becomes increasingly relevant,
offering a robust solution to address these challenges.

This specification outlines a private messaging service using the
Ethereum blockchain as authentication service.
Rooted in the existing [model](../../../messaging/standards/application/20/toy-eth-pm.md),
this proposal addresses the deficiencies related
to forward privacy and authentication inherent
in the current framework.
The specification is divided into 3 sections:

- Private 1-to-1 communications protocol, based on [Signal's double
ratchet](https://signal.org/docs/specifications/doubleratchet/).
- Private group messaging protocol, based on the
[MLS protocol](https://datatracker.ietf.org/doc/rfc9420/).
- Description of an Ethereum-based authentication protocol, based on
[SIWE](https://eips.ethereum.org/EIPS/eip-4361).

## Private 1-to-1 communications protocol

### Theory

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

> The inclusion of this first section devoted to secure 1-to-1
communications between users is motivated by the fact certain
interactions between existing group members and prospective new
members require secure communication channels.

### Syntax

#### Cryptographic suite

The following cryptographic functions MUST be used:

- `X488` as Diffie-Hellman function `DH`.
- `SHA256` as KDF.
- `AES256-GCM` as AEAD algorithm.
- `SHA512` as hash function.
- `XEd448` for digital signatures.

#### X3DH initialization

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

#### Use of X3DH

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

#### Initialization of the double datchet

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

#### Encryption

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

#### Decryption

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

This applies to `KeyPackage`,
which in the MLS specification are meant
o be stored in a directory provided by the delivery service.
If such an element does not exist,
`KeyPackage` MUST be stored according
to one of the two options outlined above.

## Private group messaging protocol

### Theoretical content

The [Messaging Layer Security](https://datatracker.ietf.org/doc/rfc9420/)(MLS)
protocol aims at providing a group of users with
end-to-end encryption in an authenticated and asynchronous way.
The main security characteristics of the protocol are:
Message confidentiality and authentication, sender authentication,
membership agreement, post-remove
and post-update security, and forward secrecy and
post-compromise security.
The MLS protocol achieves: low-complexity, group integrity,
synchronization and extensibility.

The extension to group chat described in forthcoming sections is built upon the
[MLS](https://datatracker.ietf.org/doc/rfc9420/) protocol.

### Structure

Each MLS session uses a single cipher suite that specifies the
primitives to be used in group key computations. The cipher suite MUST
use:

- `X488` as Diffie-Hellman function.
- `SHA256` as KDF.
- `AES256-GCM` as AEAD algorithm.
- `SHA512` as hash function.
- `XEd448` for digital signatures.

Formats for public keys, signatures and public-key encryption MUST
follow Section 5.1 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Hash-based identifiers

Some MLS messages refer to other MLS objects by hash.
These identifiers MUST be computed according to Section 5.2 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Credentials

Each member of a group presents a credential that provides one or more
identities for the
member and associates them with the member's signing key.
The identities and signing key are verified by the Authentication
Service in use for a
group.

Credentials MUST follow the specifications of section 5.3 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

Below follows the flow diagram for the generation of credentials.
Users MUST generate key pairs by themselves.
![figure1](/ift-ts/raw/images/eth-secpm_credential.png)

### Message framing

Handshake and application messages use a common framing structure
providing encryption to
ensure confidentiality within the group, and signing to authenticate
the sender.

The structure is:

- `PublicMessage`: represents a message that is only signed, and not
encrypted.
The definition and the encoding/decoding of a `PublicMessage` MUST
follow the specification
in section 6.2 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).
- `PrivateMessage`: represents a signed and encrypted message, with
protections for both the content of the message and related metadata.

The definition, and the encoding/decoding of a `PrivateMessage` MUST
follow the  specification in section 6.3 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

Applications MUST use `PrivateMessage` to encrypt application messages.

Applications SHOULD use `PrivateMessage` to encode handshake messages.

Each encrypted MLS message carries a "generation" number which is a
per-sender incrementing counter.
If a group member observes a gap in the generation sequence for a
sender, then they know that they have missed a message from that
sender.

### Nodes contents

The nodes of a ratchet tree contain several types of data:

- Leaf nodes describe individual members.
- Parent nodes describe subgroups.

Contents of each kind of node, and its structure MUST follow the
indications described in
sections 7.1 and 7.2 of
[RFC9420](https://datatracker.ietf.org/docrfc9420/).

### Leaf node validation

`KeyPackage` objects describe the client's capabilities and provides
keys that can be used  to add the client to a group.

The validity of a leaf node needs to be verified at the following
stages:

- When a leaf node is downloaded in a `KeyPackage`, before it is used
to add the client to the group.
- When a leaf node is received by a group member in an Add, Update, or
Commit message.
- When a client validates a ratchet tree.

A client MUST verify the validity of a leaf node following the
instructions of section 7.3 in
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Ratchet tree evolution

Whenever a member initiates an epoch change, they MAY need to refresh
the key pairs of their leaf and of the nodes on their direct path. This
is done to keep forward secrecy and post-compromise security.
The member initiating the epoch change MUST follow this procedure
procedure.
A member updates the nodes along its direct path as follows:

- Blank all the nodes on the direct path from the leaf to the root.
- Generate a fresh HPKE key pair for the leaf.
- Generate a sequence of path secrets, one for each node on the leaf's
filtered direct path.

It MUST follow the procedure described in section 7.4 of [RFC9420
(https://datatracker.ietf.org/doc/rfc9420/).

- Compute the sequence of HPKE key pairs `(node_priv,node_pub)`, one
for each node on the leaf's direct path.

It MUST follow the procedure described in section 7.4 of [RFC9420
(https://datatracker.ietf.org/doc/rfc9420/).

### Views of the tree synchronization

After generating fresh key material and applying it to update their
local tree state, the generator broadcasts this update to other members
of the group.
This operation MUST be done according to section 7.5 of [RFC9420
(https://datatracker.ietf.org/doc/rfc9420/).

### Leaf synchronization

Changes to group memberships MUST be represented by adding and removing
leaves of the tree.
This corresponds to increasing or decreasing the depth of the tree,
resulting in the number of leaves being doubled or halved.
These operations MUST be done as described in section 7.7 of [RFC9420
(https://datatracker.ietf.org/doc/rfc9420/).

### Tree and parent hashing

Group members can agree on the cryptographic state of the group by
generating a hash value that represents the contents of the group
ratchet tree and the member’s credentials.
The hash of the tree is the hash of its root node, defined recursively
from the leaves.
Tree hashes summarize the state of a tree at point in time.
The hash of a leaf is the hash of the `LeafNodeHashInput` object.
At the same time, the hash of a parent node including the root, is the
hash of a `ParentNodeHashInput` object.
Parent hashes capture information about how keys in the tree were
populated.

Tree and parent hashing MUST follow the directions in Sections 7.8 and
7.9 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Key schedule

Group keys are derived using the `Extract` and `Expand` functions from
the KDF for the group's cipher suite, as well as the functions defined
below:

```text
ExpandWithLabel(Secret, Label, Context, Length) = KDF.Expand(Secret,
KDFLabel, Length)
DeriveSecret(Secret, Label) = ExpandWithLabel(Secret, Label, "",
KDF.Nh)

```

`KDFLabel` MUST be specified as:

```text
struct {
    uint16 length;
    opaque label<V>;
    opaque context<V>;
} KDFLabel;

```

The fields of `KDFLabel` MUST be:

```text
length = Length;
label = "MLS 1.0 " + Label;
context = Context;

```

Each member of the group MUST maintaint a `GroupContext` object
summarizing the state of the group.

The sturcture of such object MUST be:

```text
struct {
ProtocolVersion version = mls10;
CipherSuite cipher_suite;
opaque group_id<V>;
uint64 epoch;
opaque tree_hash<V>;
opaque confirmed_trasncript_hash<V>;
Extension extension<V>;
} GroupContext;

```

The use of key scheduling MUST follow the indications in sections 8.1 -
8.7 in [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Secret trees

For the generation of encryption keys and nonces, the key schedule
begins with the `encryption_secret` at the root and derives a tree of
secrets with the same structure as the group's ratchet tree.
Each leaf in the secret tree is associated with the same group member
as the corresponding leaf in the ratchet tree.

If `N` is a parent node in the secret tree, the secrets of the children
of `N` MUST be defined following section 9 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

#### Encryption keys

MLS encrypts three different types of information:

- Metadata (sender information).
- Handshake messages (Proposal and Commit).
- Application messages.

For handshake and application messages, a sequence of keys is derived
via a sender ratchet.
Each sender has their own sender ratchet, and each step along the
ratchet is called a generation. These procedures MUST follow section
9.1 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

#### Deletion schedule

All security-sensitive values MUST be deleted as soon as they are
consumed.

A sensitive value S is consumed if:

- S was used to encrypt or (successfully) decrypt a message.
- A key, nonce, or secret derived from S has been consumed.

The deletion procedure MUST follow the instruction described in section
9.2 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Key packages

KeyPackage objects are used to ease the addition of clients to a group
asynchronously.
A KeyPackage object specifies:

- Protocol version and cipher suite supported by the client.
- Public keys that can be used to encrypt Welcome messages.
Welcome messages provide new members with the information
to initialize their
state for the epoch in which they were added or in which they want to
add themselves to the group
- The content of the leaf node that should be added to the tree to
represent this client.

KeyPackages are intended to be used only once and SHOULD NOT be reused.

Clients MAY generate and publish multiple KeyPackages to support
multiple cipher suites.

The structure of the object MUST be:

```text
struct {
ProtocolVersion version;
CipherSuite cipher_suite;
HPKEPublicKey init_key;
LeafNode leaf_node;
Extension extensions<V>;
/* SignWithLabel(., "KeyPackageTBS", KeyPackageTBS) */
opaque signature<V>;
}

```

```text
struct {
ProtocolVersion version;
CipheSuite cipher_suite;
HPKEPublicKey init_key;
LeafNode leaf_node;
Extension extensions<V>;
}

```

`KeyPackage` object MUST be verified when:

- A `KeyPackage` is downloaded by a group member, before it is used to
add the client to the group.
- When a `KeyPackage` is received by a group member in an `Add`
message.

Verification MUST be done as follows:

- Verify that the cipher suite and protocol version of the `KeyPackage`
match those in the `GroupContext`.
- Verify that the `leaf_node` of the `KeyPackage` is valid for a
`KeyPackage`.
- Verify that the signature on the `KeyPackage` is valid.
- Verify that the value of `leaf_node.encryption_key` is different from
the value of the `init_key field`.

HPKE public keys are opaque values in a format defined by Section 4 of
[RFC9180](https://datatracker.ietf.org/doc/rfc9180/).

Signature public keys are represented as opaque values in a format
defined by the cipher suite's signature scheme.

### Group creation

A group is always created with a single member.
Other members are then added to the group using the usual Add/Commit
mechanism.
The creator of a group MUST set:

- the group ID.
- cipher suite.
- initial extensions for the group.

If the creator intends to add other members at the time of creation,
then it SHOULD fetch `KeyPackages` for those members, and select a
cipher suite and extensions according to their capabilities.

The creator MUST use the capabilities information in these
`KeyPackages` to verify that the chosen version and cipher suite is the
best option supported by all members.

Group IDs SHOULD be constructed so they are unique with high
probability.

To initialize a group, the creator of the group MUST initialize a one
member group with the following initial values:

- Ratchet tree: A tree with a single node, a leaf node containing an
HPKE public key and credential for the creator.
- Group ID: A value set by the creator.
- Epoch: `0`.
- Tree hash: The root hash of the above ratchet tree.
- Confirmed transcript hash: The zero-length octet string.
- Epoch secret: A fresh random value of size `KDF.Nh`.
- Extensions: Any values of the creator's choosing.

The creator MUST also calculate the interim transcript hash:

- Derive the `confirmation_key` for the epoch according to Section 8 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).
- Compute a `confirmation_tag` over the empty
`confirmed_transcript_hash` using the `confirmation_key` as described
in Section 8.1 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).
- Compute the updated `interim_transcript_hash` from the
`confirmed_transcript_hash` and the `confirmation_tag` as described in
Section 8.2 [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

All members of a group MUST support the cipher suite and protocol
version in use. Additional requirements MAY be imposed by including a
`required_capabilities` extension in the `GroupContext`.

```text
struct {
ExtensionType extension_types<V>;
ProposalType proposal_types<V>;
CredentialType credential_types<V>;
}

```

The flow diagram shows the procedure to fetch key material from other
users:
![figure2](/ift-ts/raw/images/eth-secpm_fetching.png)

Below follows the flow diagram for the creation of a group:
![figure3](/ift-ts/raw/images/eth-secpm_creation.png)

### Group evolution

Group membership can change, and existing members can change their keys
in order to achieve post-compromise security.
In MLS, each such change is accomplished by a two-step process:

- A proposal to make the change is broadcast to the group in a Proposal
message.
- A member of the group or a new member broadcasts a Commit message
that causes one or more proposed changes to enter into effect.

The group evolves from one cryptographic state to another each time a
Commit message is sent and processed.
These states are called epochs and are uniquely identified among states
of the group by eight-octet epoch values.

Proposals are included in a `FramedContent` by way of a `Proposal`
structure that indicates their type:

```text
struct {
ProposalType proposal_type;
select (Proposal.proposal_type) {
case add:                      Add:
case update:                   Update;
case remove:                   Remove;
case psk:                      PreSharedKey;
case reinit:                   ReInit;
case external_init:            ExternalInit;
case group_context_extensions: GroupContextExtensions;
}

```

On receiving a `FramedContent` containing a `Proposal`, a client MUST
verify the signature inside `FramedContentAuthData` and that the epoch
field of the enclosing FramedContent is equal to the epoch field of the
current GroupContext object.
If the verification is successful, then the Proposal SHOULD be cached
in such a way that it can be retrieved by hash in a later Commit
message.

Proposals are organized as follows:

- `Add`: requests that a client with a specified KeyPackage be added to
the group.
- `Update`: similar to Add, it replaces the sender's LeafNode in the
tree instead of adding a new leaf to the tree.
- `Remove`: requests that the member with the leaf index removed be
removed from the group.
- `ReInit`: requests to reinitialize the group with different
parameters.
- `ExternalInit`: used by new members that want to join a group by
using an external commit.
- `GroupContentExtensions`: it is used to update the list of extensions
in the GroupContext for the group.

Proposals structure and semantics MUST follow sections 12.1.1 - 12.1.7
of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

Any list of commited proposals MUST be validated either by a the group
member who created the commit, or any group member processing such
commit.
The validation MUST be done according to one of the procedures
described in Section 12.2 of
[RFC9420](https://datatracker.ietf.orgdoc/rfc9420/).

When creating or processing a Commit, a client applies a list of
proposals to the ratchet tree and `GroupContext`.
The client MUST apply the proposals in the list in the order described
in Section 12.3 of [RFC9420](https://datatracker.ietf.org/docrfc9420/).

Below follows the flow diagram for the addition of a member to a group:
![figure4](/ift-ts/raw/images/eth-secpm_add.png)

The diagram below shows the procedure to remove a group member:

![figure5](/ift-ts/raw/images/eth-secpm_remove.png)

The flow diagram below shows an update procedure:

![figure6](/ift-ts/raw/images/eth-secpm_update.png)

### Commit messages

Commit messages initiate new group epochs.
It informs group members to update their representation of the state of
the group by applying the proposals and advancing the key schedule.

Each proposal covered by the Commit is included by a `ProposalOrRef`
value.
`ProposalOrRef` identify the proposal to be applied by value or by
reference.
Commits that refer to new Proposals from the committer can be included
by value.
Commits for previously sent proposals from anyone can be sent by
reference.
Proposals sent by reference are specified by including the hash of the
`AuthenticatedContent`.

Group members that have observed one or more valid proposals within an
epoch MUST send a Commit message before sending application data.
A sender and a receiver of a Commit MUST verify that the committed list
of proposals is valid.
The sender of a Commit SHOULD include all valid proposals received
during the current epoch.

Functioning of commits MUST follow the instructions of Section 12.4 of
[RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Application messages

Handshake messages provide an authenticated group key exchange to
clients.
To protect application messages sent among the members of a group, the
`encryption_secret` provided by the key schedule is used to derive a
sequence of nonces and keys for message encryption.

Each client MUST maintain their local copy of the key schedule for each
epoch during which they are a group member.
They derive new keys, nonces, and secrets as needed. This data MUST be
deleted as soon as they have been used.

Group members MUST use the AEAD algorithm associated with the
negotiated MLS ciphersuite to encrypt and decrypt Application messages
according to the Message Framing section.
The group identifier and epoch allow a device to know which group
secrets should be used and from which Epoch secret to start computing
other secrets and keys.
Application messages SHOULD be padded to provide resistance against
traffic analysis techniques.
This avoids additional information to be provided to an attacker in
order to guess the length of the encrypted message.
Padding SHOULD be used on messages with zero-valued bytes before AEAD
encryption.

Functioning of application messages MUST follow the instructions of
Section 15 of [RFC9420](https://datatracker.ietf.org/doc/rfc9420/).

### Considerations with respect to decentralization

The MLS protocol assumes the existence on a (central, untrusted)
*delivery service*, whose responsabilites include:

- Acting as a directory service providing the initial
keying material for clients to use.
- Routing MLS messages among clients.

The central delivery service can be avoided in protocols using the
publish/gossip approach, such as
[gossipsub](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub).

Concerning keys, each node can generate and disseminate their
encryption key among the other nodes, so they can create a local
version of the tree that allows for the generation of the group key.

Another important component is the *authentication service*, which is
replaced with SIWE in this specification.

## Ethereum-based authentication protocol

### Introduction

Sign-in with Ethereum describes how Ethereum accounts authenticate with
off-chain services by signing a standard message format
parameterized by scope, session details, and security mechanisms.
Sign-in with Ethereum (SIWE), which is described in the [EIP 4361
(https://eips.ethereum.org/EIPS/eip-4361), MUST be the authentication
method required.

### Pattern

#### Message format (ABNF)

A SIWE Message MUST conform with the following Augmented Backus–Naur
Form ([RFC 5234](https://datatracker.ietf.org/doc/html/rfc5234))
expression.

```text
sign-in-with-ethereum =
    [ scheme "://" ] domain %s" wants you to sign in with your 
    Ethereum account:" LF address LF
    LF
    [ statement LF ]
    LF
    %s"URI: " uri LF
    %s"Version: " version LF
    %s"Chain ID: " chain-id LF
    %s"Nonce: " nonce LF
    %s"Issued At: " issued-at
    [ LF %s"Expiration Time: " expiration-time ]
    [ LF %s"Not Before: " not-before ]
    [ LF %s"Request ID: " request-id ]
    [ LF %s"Resources:"
    resources ]

scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
    ; See RFC 3986 for the fully contextualized
    ; definition of "scheme".

domain = authority
    ; From RFC 3986:
    ;     authority     = [ userinfo "@" ] host [ ":" port ]
    ; See RFC 3986 for the fully contextualized
    ; definition of "authority".

address = "0x" 40*40HEXDIG
    ; Must also conform to captilization
    ; checksum encoding specified in EIP-55
    ; where applicable (EOAs).

statement = *( reserved / unreserved / " " )
    ; See RFC 3986 for the definition
    ; of "reserved" and "unreserved".
    ; The purpose is to exclude LF (line break).

uri = URI
    ; See RFC 3986 for the definition of "URI".

version = "1"

chain-id = 1*DIGIT
    ; See EIP-155 for valid CHAIN_IDs.

nonce = 8*( ALPHA / DIGIT )
    ; See RFC 5234 for the definition
    ; of "ALPHA" and "DIGIT".

issued-at = date-time
expiration-time = date-time
not-before = date-time
    ; See RFC 3339 (ISO 8601) for the
    ; definition of "date-time".

request-id = *pchar
    ; See RFC 3986 for the definition of "pchar".

resources = *( LF resource )

resource = "- " URI

```

This specification defines the following SIWE Message fields that can
be parsed from a SIWE Message by following the rules in ABNF Message
Format:

- `scheme` OPTIONAL. The URI scheme of the origin of the request.
Its value MUST be a
[RFC 3986](https://datatracker.ietf.org/doc/htmlrfc3986)
URI scheme.

- `domain` REQUIRED.
The domain that is requesting the signing.
Its value MUST be a [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986)
authority. The authority includes an OPTIONAL port.
If the port is not specified, the default
port for the provided scheme is assumed.

If scheme is not specified, HTTPS is assumed by default.

- `address` REQUIRED. The Ethereum address performing the signing.
Its value SHOULD be conformant to mixed-case checksum address encoding
specified in ERC-55 where applicable.

- `statement` OPTIONAL. A human-readable ASCII assertion that the user
will sign which MUST NOT include '\n' (the byte 0x0a).
- `uri` REQUIRED. An
[RFC 3986](https://datatracker.ietf.org/doc/htmlrfc3986)
URI referring to the resource that is the subject of the
signing.

- `version` REQUIRED. The current version of the SIWE Message, which
MUST be 1 for this specification.

- `chain-id` REQUIRED. The EIP-155 Chain ID to which the session is
bound, and the network where Contract Accounts MUST be resolved.

- `nonce` REQUIRED. A random string (minimum 8 alphanumeric characters)
chosen by the relying party and used to prevent replay attacks.

- `issued-at` REQUIRED. The time when the message was generated,
typically the current time.

Its value MUST be an ISO 8601 datetime string.

- `expiration-time` OPTIONAL. The time when the signed authentication
message is no longer valid.

Its value MUST be an ISO 8601 datetime string.

- `not-before` OPTIONAL. The time when the signed authentication
message will become valid.

Its value MUST be an ISO 8601 datetime string.

- `request-id` OPTIONAL. An system-specific identifier that MAY be used
to uniquely refer to the sign-in request.

- `resources` OPTIONAL. A list of information or references to
information the user wishes to have resolved as part of authentication
by the relying party.

Every resource MUST be a RFC 3986 URI separated by "\n- " where \n is
the byte 0x0a.

#### Signing and Verifying Messages with Ethereum Accounts

- For Externally Owned Accounts, the verification method specified in
[ERC-191](https://eips.ethereum.org/EIPS/eip-191)
MUST be used.

- For Contract Accounts,

  - The verification method specified in
[ERC-1271](https://eips.ethereum.org/EIPS/eip-1271)
SHOULD be used.
Otherwise, the implementer MUST clearly define the
verification method
to attain security and interoperability for both
wallets and relying parties.

  - When performing [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271)
signature verification, the contract performing the verification MUST
be resolved from the specified `chain-id`.

  - Implementers SHOULD take into consideration that [ERC-1271
(https://eips.ethereum.org/EIPS/eip-1271) implementations are not
required to be pure functions.
They can return different results for the same inputs depending on
blockchain state.
This can affect the security model and session validation rules.

#### Resolving Ethereum Name Service (ENS) Data

- The relying party or wallet MAY additionally perform resolution of
ENS data, as this can improve the user experience by displaying human
friendly information that is related to the `address`.
Resolvable ENS data include:

  - The primary ENS name.
  - The ENS avatar.
  - Any other resolvable resources specified in the ENS documentation.

- If resolution of ENS data is performed, implementers SHOULD take
precautions to preserve user privacy and consent.
Their `address` could be forwarded to third party services as part of
the resolution process.

#### Implementer steps: specifying the request origin

The `domain` and, if present, the `scheme`, in the SIWE Message MUST
correspond to the origin from where the signing request was made.

#### Implementer steps: verifying a signed message

The SIWE Message MUST be checked for conformance to the ABNF Message
Format and its signature MUST be checked as defined in Signing and
Verifying Messages with Ethereum Accounts.

#### Implementer steps: creating sessions

Sessions MUST be bound to the address and not to further resolved
resources that can change.

#### Implementer steps: interpreting and resolving resources

Implementers SHOULD ensure that that URIs in the listed resources are
human-friendly when expressed in plaintext form.

#### Wallet implementer steps: verifying the message format

The full SIWE message MUST be checked for conformance to the ABNF
defined in ABNF Message Format.

Wallet implementers SHOULD warn users if the substring `"wants you to
sign in with your Ethereum account"` appears anywhere in an [ERC-191
(https://eips.ethereum.org/EIPS/eip-191) message signing request unless
the message fully conforms to the format defined ABNF Message Format.

#### Wallet implementer steps: verifying the request origin

Wallet implementers MUST prevent phishing attacks by verifying the
origin of the request against the `scheme` and `domain` fields in the
SIWE Message.

The origin SHOULD be read from a trusted data source such as the
browser window or over WalletConnect
[ERC-1328](https://eips.ethereum.org/EIPS/eip-1328) sessions for
comparison against the
signing message contents.

Wallet implementers MAY warn instead of rejecting the verification if
the origin is pointing to localhost.

The following is a RECOMMENDED algorithm for Wallets to conform with
the requirements on request origin verification defined by this
specification.

The algorithm takes the following input variables:

- fields from the SIWE message.
- `origin` of the signing request: the origin of the page which
requested the signin via the provider.
- `allowedSchemes`: a list of schemes allowed by the Wallet.
- `defaultScheme`: a scheme to assume when none was provided. Wallet
implementers in the browser SHOULD use https.
- developer mode indication: a setting deciding if certain risks should
be a warning instead of rejection. Can be manually configured or
derived from `origin` being localhost.

The algorithm is described as follows:

- If `scheme` was not provided, then assign `defaultScheme` as scheme.
- If `scheme` is not contained in `allowedSchemes`, then the `scheme`
is not expected and the Wallet MUST reject the request.
Wallet implementers in the browser SHOULD limit the list of
allowedSchemes to just 'https' unless a developer mode is activated.
- If `scheme` does not match the scheme of origin, the Wallet SHOULD
reject the request.
Wallet implementers MAY show a warning instead of rejecting the request
if a developer mode is activated.
In that case the Wallet continues processing the request.
- If the `host` part of the `domain` and `origin` do not match, the
Wallet MUST reject the request unless the Wallet is in developer mode.
In developer mode the Wallet MAY show a warning instead and continues
procesing the request.
- If `domain` and `origin` have mismatching subdomains, the Wallet
SHOULD reject the request unless the Wallet is in developer mode.
In developer mode the Wallet MAY show a warning instead and continues
procesing the request.
- Let `port` be the port component of `domain`, and if no port is
contained in domain, assign port the default port specified for the
scheme.
- If `port` is not empty, then the Wallet SHOULD show a warning if the
`port` does not match the port of `origin`.
- If `port` is empty, then the Wallet MAY show a warning if `origin`
contains a specific port.
- Return request origin verification completed.

#### Wallet implementer steps: creating SIWE interfaces

Wallet implementers MUST display to the user the following fields from
the SIWE Message request by default and prior to signing, if they are
present: `scheme`, `domain`, `address`, `statement`, and `resources`.
Other present fields MUST also be made available to the user prior to
signing either by default or through an extended interface.

Wallet implementers displaying a plaintext SIWE Message to the user
SHOULD require the user to scroll to the bottom of the text area prior
to signing.

Wallet implementers MAY construct a custom SIWE user interface by
parsing the ABNF terms into data elements for use in the interface.
The display rules above still apply to custom interfaces.

#### Wallet implementer steps: supporting internationalization (i18n)

After successfully parsing the message into ABNF terms, translation MAY
happen at the UX level per human language.

## Privacy and Security Considerations

- The double ratchet "recommends" using AES in CBC mode. Since
encryption must be with an AEAD encryption scheme, we will use AES in
GCM mode instead (supported by Noise).
- For the information retrieval, the algorithm MUST include a access
control mechanisms to restrict who can call the set and get functions.
- One SHOULD include event logs to track changes in public keys.
- The curve vurve448 MUST be chosen due to its higher security level:
224-bit security instead of the 128-bit security provided by X25519.
- It is important that Bob MUST NOT reuse `SPK`.

## Considerations related to the use of Ethereum addresses

### With respect to the Authentication Service

- If users used their Ethereum addresses as identifiers, they MUST
generate their own credentials.
These credentials MUST use the digital signature key pair associated to
the Ethereum address.
- Other users can verify credentials.
- With this approach, there is no need to have a dedicated
Authentication Service responsible for the issuance and verification of
credentials.
- The interaction diagram showing the generation of credentials becomes
obsolete.

### With respect to the Delivery Service

- Users MUST generate their own KeyPackage.
- Other users can verify KeyPackages when required.
- A Delivery Service storage system MUST verify KeyPackages before
storing them.
- Interaction diagrams involving the DS do not change.

## Consideration related to the onchain component of the protocol

### Assumptions

- Users have set a secure 1-1 communication channel.
- Each group is managed by a separate smart contract.

### Addition of members to a group

#### Alice knows Bob’s Ethereum address

1. Off-chain - Alice and Bob set a secure communication channel.
2. Alice creates the smart contract associated to the group. This smart
contract MUST include an ACL.
3. Alice adds Bob’s Ethereum address to the ACL.
4. Off-chain - Alice sends a request to join the group to Bob. The
request MUST include the contract’s address: `RequestMLSPayload {"You
are joining the group with smart contract: 0xabcd"}`
5. Off-chain - Bob responds the request with a digitally signed
response. This response includes Bob’s credentials and key package:
`ResponseMLSPayload {sig: signature(ethereum_sk, message_to_sign),
address: ethereum_address, credentials, keypackage}`
6. Off-chain - Alice verifies the signature, using Bob’s `ethereum_pk`
and checks that it corresponds to an address contained in the ACL.
7. Off-chain - Alice sends a welcome message to Bob.
8. Off-chain - Alice SHOULD broadcasts a message announcing the
addition of Bob to other users of the group.
![figure7](/ift-ts/raw/images/eth-secpm_onchain-register-1.png)

#### Alice does not know Bob’s Ethereum address

1. Off-chain - Alice and Bob set a secure communication channel.
2. Alice creates the smart contract associated to the group.
This smart contract MUST include an ACL.
3. Off-chain - Alice sends a request to join the group to Bob. The
request MUST include the contract’s address:
`RequestMLSPayload{"You are joining the group
with smart contract: 0xabcd"}`
4. Off-chain - Bob responds the request with a digitally signed
response. This response includes Bob’s credentials, his Ethereum
address and key package: `ResponseMLSPayload {sig:
signature(ethereum_sk, message_to_sign), address: ethereum_address,
credentials, keypackage}`
5. Off-chain - Alice verifies the signature using Bob’s `ethereum_pk`.
6. Upon reception of Bob’s data, Alice registers data with the smart
contract.
7. Off-chain - Alice sends a welcome message to Bob.
8. Off-chain - Alice SHOULD broadcasts a message announcing the
addition of Bob to other users of the group.

![figure8](/ift-ts/raw/images/eth-secpm_onchain-register-2.png)

### Considerations regarding smart contracts

The role of the smart contract includes:

- Register user information and key packages:
As described in the previous section.
- Updates of key material.
  - Users MUST send any update in their key material to the other
users of the group via off-chain messages.
  - Upon reception of the new key material, the creator of the
contract MUST update the state of the smart contract.
- Deletion of users.
  - Any user can submit a proposal for the removal of a user via
off-chain message.
  - This proposal MUST be sent to the creator of the contract.
  - The creator of the contract MUST update the ACL, and send
messages to the group for key update.

![figure9](/ift-ts/raw/images/eth-secpm_onchain-update.png)

> It is important to note that both
user removal and updates of any kind
have a similar interaction flow.

- Queries of existing users.
  - Any user can query the smart contract to know the state of the
group, including existing users and removed ones.
  - This aspect MUST be used when adding new members to verify that
the prospective key package has not been already used.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Augmented BNF for Syntax Specifications](https://datatracker.ietf.org/doc/html/rfc5234)
- [Gossipsub](https://github.com/libp2p/specs/tree/master/pubsub/gossipsub)
- [HMAC-based Extract-and-Expand Key Derivation Function](https://www.ietf.org/rfc/rfc5869.txt)
- [Hybrid Public Key Encryption](https://datatracker.ietf.org/doc/rfc9180/)
- [Security Analysis and Improvements for the IETF MLS Standard for Group Messaging](https://eprint.iacr.org/2019/1189.pdf)
- [Signed Data Standard](https://eips.ethereum.org/EIPS/eip-191)
- [Sign-In with Ethereum](https://eips.ethereum.org/EIPS/eip-4361)
- [Standard Signature Validation Method for Contracts](https://eips.ethereum.org/EIPS/eip-1271)
- [The Double Ratchet Algorithm](https://signal.org/docs/specifications/doubleratchet/)
- [The Messaging Layer Security Protocol](https://datatracker.ietf.org/doc/rfc9420/)
- [The X3DH Key Agreement Protocol](https://signal.org/docs/specifications/x3dh/)
- [Toy Ethereum Private Messaging Protocol](https://rfc.vac.dev/spec/20/)
- [Uniform Resource Identifier](https://datatracker.ietf.org/doc/html/rfc3986)
- [WalletConnect URI Format](https://eips.ethereum.org/EIPS/eip-1328)
