# NOMOS-MESSAGE-ENCAPSULATION

| Field | Value |
| --- | --- |
| Name | Nomos Message Encapsulation Mechanism |
| Slug | 91 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski |
| Contributors | Youngjoon Lee <youngjoon@status.im>, Alexander Mozeika <alexander.mozeika@status.im>, Mehmet Gonen <mehmet@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Daniel Kashepava <danielkashepava@status.im>, Daniel Sanchez Quiros <danielsq@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-message-encapsulation.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-message-encapsulation.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

The message encapsulation mechanism is a core component of the Blend Protocol
that ensures privacy and security during node-to-node message transmission.
By implementing multiple encryption layers and cryptographic operations,
this mechanism keeps messages confidential while concealing their origins.
The encapsulation process includes building a multi-layered structure
with public headers, private headers, and encrypted payloads,
using cryptographic keys and proofs for layer security and authentication,
applying verifiable random node selection for message routing,
and using shared key derivation for secure inter-node communication.

This document outlines the cryptographic notation, data structures,
and algorithms essential to the encapsulation process.

**Keywords:** Blend, message encapsulation, encryption, privacy,
layered encryption, cryptographic proof, routing

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Document Structure

This specification is organized into two distinct parts
to serve different audiences and use cases:

**Protocol Specification** contains the normative requirements necessary
for implementing an interoperable Blend Protocol node.
This section defines the cryptographic primitives, message formats,
network protocols, and behavioral requirements that all implementations
must follow to ensure compatibility and maintain the protocol's
privacy guarantees.
Protocol designers, auditors, and those seeking to understand the core
mechanisms should focus on this part.

**Implementation Considerations** provides non-normative guidance
for implementers.
This section offers practical recommendations, optimization strategies,
and detailed examples that help developers build efficient and robust
implementations.
While these details are not required for interoperability,
they represent best practices learned from reference implementations
and can significantly improve performance and reliability.

## Protocol Specification

### Introduction

The message encapsulation mechanism is part of the [Blend Protocol][blend-protocol]
and it describes the cryptographic operations necessary for building
and processing messages by a Blend node.
See the [Blend Protocol Formatting][blend-formatting] specification
for additional context on message structure and formatting conventions.

### Notation

**Key Collections:**

$\mathbf K^{n}h = \{(K^{n}{0}, k^{n}{0}, \pi{Q}^{K_{0}^{n}}),...,(K^{n}{h-1}, k^{n}{h-1}, \pi_{Q}^{K_{h-1}^{n}}) \}$
is a collection of $h$ key pairs for a node $n$ with proofs of quota,
where $K_{i}^{n}$ is the $i$-th public key
and $k_{i}^{n}$ is its corresponding private key,
and $\pi_{Q}^{K_{i}^{n}}$ is its proof of quota.

```python
Ed25519PublicKey = bytes
Ed25519PrivateKey = bytes
KEY_SIZE = 32
ProofOfQuota = bytes
PROOF_OF_QUOTA_SIZE = 160

KeyCollection = List[KeyPair]

class KeyPair:
    signing_public_key: Ed25519PublicKey
    signing_private_key: Ed25519PrivateKey
    proof_of_quota: ProofOfQuota

class ProofOfQuota:
    key_nullifier: zkhash  # 32 bytes
    proof: bytes  # 128 bytes
```

For more information about key generation mechanism
please refer to the [Key Types and Generation Specification][key-types].

For more information about proof of quota
please refer to the [Proof of Quota Specification][proof-of-quota].

**Service Declaration Protocol:**

$P^n$ is a public key of the node $n$,
which is globally accessible using the Service Declaration Protocol (SDP).
This notation is used to distinguish the origin of the key,
hence the following simplified notation.

For more information about Service Declaration Protocol
please refer to the [Service Declaration Protocol][sdp].

$\mathcal{N} = \text{SDP}(s)$ is the set of nodes globally accessible using the SDP.

```python
Nodes = set[Ed25519PublicKey]  # set of signing public keys
```

$N =|\mathcal{N}|$ is the number of nodes globally accessible using the SDP.

**Shared Keys:**

$\kappa^{n,m}{i} = k^{n}{i} \cdot P^{m} = p^{m} \cdot K^{n}_{i}$,
is a shared key calculated between node $n$ and node $m$
using the $i$-th key of the node $n$,
$P^{m}$ is the public key of the node $m$ retrieved from the SDP protocol
and $p^m$ is its corresponding private key.

```python
SharedKey = bytes  # KEY_SIZE
```

**Proof of Selection:**

$\pi^{K^{n}{l},m}{S}$ is the proof of selection of the public key $K^{n}_l$
to the node index $m$ from a set of all nodes $\mathcal N$.

```python
ProofOfSelection = bytes
PROOF_OF_SELECTION_SIZE = 32
```

For more information about the proof of selection,
please refer to the [Proof of Selection Specification][proof-of-selection].

**Hash Functions:**

$H_{\mathbf N}()$ is a domain-separated hash function dedicated to the
node index selection (the implementation of the hash function is blake2b).

```python
def hashds(domain=b"BlendNode", data: bytes) -> bytes:
    return Blake2B.hash512(domain + data)
```

$H_\mathbf{I}()$ is a domain-separated hash function dedicated to the
initialization of the blend header
(the implementation of the hash function is blake2b).

```python
def hashds(domain=b"BlendInitialization", data: bytes) -> bytes:
    return Blake2b.hash512(domain + data)
```

$H_\mathbf{b}()$ is a domain-separated hash function dedicated to the
blend header encryption operations
(the implementation of the hash function is blake2b).

```python
def hashds(domain=b"BlendHeader", data: bytes) -> bytes:
    return Blake2b.hash512(domain + data)
```

$H_\mathbf{P}()$ is a domain-separated hash function dedicated to the
payload encryption operations
(the implementation of the hash function is blake2b).

```python
def hashds(domain=b"BlendPayload", data: bytes) -> bytes:
    return Blake2b.hash512(domain + data)
```

**Encapsulation Parameters:**

$\beta_{max}$ is the maximal number of blending headers in the private header.

```python
ENCAPSULATION_COUNT: int
```

**Pseudo-Random Generation:**

$\text {CSPRBG}()$ is a generalized cryptographically secure pseudo-random
bytes generator,
it is implemented as BLAKE2b-Based PRNG Construction.

$\text {CSPRBG}()_{x}$ is a cryptographically secure pseudo-random bytes
generator whose output is restricted to $x$ bytes,
it is implemented as BLAKE2b-Based PRNG Construction.

```python
def pseudo_random(domain: bytes, key: bytes, size: int) -> bytes:
    rand = BlakeRng.from_seed(hashds(domain, key)).generate(size)
    assert len(rand) == size
    return rand
```

**Basic Operations:**

$|t|$ returns the length of the $t$ expressed in bytes.

$\oplus$ is a XOR operation.

```python
def xor(a: bytes, b: bytes) -> bytes:
    assert len(a) == len(b)
    return bytes(x ^ y for x, y in zip(a, b))
```

**Encryption and Decryption:**

$E_k(x)=\text{CSPRBG}(k) \oplus x$ is an encryption that uses a
cryptographically secure pseudo-random bytes generator
with a secret $k$ and payload $x$.

```python
def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, pseudo_random(b"BlendEncapsulation", key, len(data)))
```

$D_k(x)=\text{CSPRBG}(k) \oplus x$ is a decryption that uses
cryptographically secure pseudo-random bytes generator
with a secret $k$ and payload $x$.

```python
def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, pseudo_random(b"BlendEncapsulation", key, len(data)))
```

### Construction

#### Message Structure

The following defines the message structure
that provides the protocol with the envisioned capabilities.

A node $n$ constructs a message $\mathbf M = (\mathbf H, \mathbf h, \mathbf P)$
according to the format presented below.

```python
class Message:
    public_header: PublicHeader
    private_header: PrivateHeader
    payload: EncryptedPayload
```

**Public Header:**

$\mathbf H$ is a public header:

1. $V$, version of the header, it is set to $1$.
2. $K^{n}_i$, a public key from the set $\mathbf K^n_h$.
3. $\pi^{K^{n}i}{Q}$, a corresponding proof of quota for the key $K^{n}_i$
   from the set $\mathbf K^n_h$ and contains its proof nullifier.
4. $\sigma_{K^{n}_{i}}(\mathbf {h|P}i)$, a signature of the concatenation
   of the $i$-th encapsulation of the payload $\mathbf P$
   and the private header $\mathbf h$,
   that can be verified by the public key $K^{n}{i}$.

```python
Signature = bytes
SIGNATURE_SIZE = 64

class PublicHeader:
    version: int = 1  # u8
    signing_public_key: Ed25519PublicKey
    proof_of_quota: ProofOfQuota
    signature: Signature
```

**Private Header:**

$\mathbf h = (\mathbf b_1,...,\mathbf b_{\beta_{max}})$ is an encrypted private header:

$\mathbf b_l$ is a blending header:

1. $K^{n}_{l}$, a public key from the set $\mathbf K^n_h$.
2. $\pi^{K^{n}{l}}{Q}$, a corresponding proof of quota for the key $K^{n}_l$
   from the $\mathbf K^n_h$ and contains its proof nullifier.
3. $\sigma_{K^{n}_{l}}(\mathbf {h|P}l)$, a signature of the concatenation
   of the $l$-th encapsulation of the payload $\mathbf P$
   and the private header $\mathbf h$,
   that can be verified by public key $K^{n}{l}$.
4. $\pi^{K^{n}{l+1},m{l+1}}{S}$, a proof of selection of the node index
   $m{l+1}$ assuming public key $K^{n}_{l+1}$.
5. $\Omega$, a flag that indicates that this is the last blending header.

```python
PrivateHeader = List[EncryptedBlendingHeader]  # length: ENCAPSULATION_COUNT
EncryptedBlendingHeader = bytes

class BlendingHeader:
    signing_public_key: Ed25519PublicKey
    proof_of_quota: ProofOfQuota
    signature: Signature
    proof_of_selection: ProofOfSelection
    is_last: bool  # 1 byte
```

**Payload:**

$\mathbf P$ is a payload.

```python
EncryptedPayload = bytes

PAYLOAD_BODY_SIZE = 34 * 1024

class Payload:
    header: PayloadHeader
    body: bytes  # PAYLOAD_BODY_SIZE

class PayloadHeader:
    payload_type: PayloadType  # 1 byte
    body_len: int  # u16

class PayloadType(Enum):
    COVER = 0x00
    DATA = 0x01
```

#### Keys and Proof Generation

For simplicity of the presentation,
this specification does not distinguish between signing and encryption keys.
However, in practice, such a distinction is necessary, that is:

- The $\mathbf K^n_h$ contains Ephemeral Signing Keys (ESK)
  that are part of the PoQ generation and are used for message signing;
  these are included in the public and private headers.
- Shared secret keys used for encryption of messages are generated from an
  Ephemeral Encryption Key (sender), which is derived from the ESK,
  and from a Non-ephemeral Encryption Key (NEK) (receiver),
  which is derived from a Non-ephemeral Signing Key (NSK)
  retrieved from the SDP protocol.

For more information, look at Key Types and Generation Specification.

The first step is to generate a set of keys alongside all necessary proofs
that will be used in the next steps of the algorithm.

#### Step 1: Generate Key Collection

Generate the collection $\mathbf K^n_h$,
where $h$ defines the number of encapsulation layers
such that $h \le \beta_{max}$.

```python
def generate_key_collection(num_layers: int) -> List[KeyPair]:
    assert num_layers <= ENCAPSULATION_COUNT
    # Generate `num_layers` random KeyPairs non-deterministically.
    return [KeyPair.random() for _ in range(num_layers)]
```

The key collection generation requires generation of Proof of Quota
(Proof of Quota Specification) for each key, as defined in the following steps.

The ProofOfQuotaPublic (Public values) structure must be filled
with public information:

1. session, core_quota, leader_quota, core_root, pol_epoch_nonce, pol_t0,
   pol_t1, pol_ledger_aged are retrieved from the blockchain.
2. K_part_one and K_part_two are first and second part of the signature key
   (KeyPair) generated by the above generate_key_collection.

```python
class ProofOfQuotaPublic:
    session: int  # Session number (uint64)
    core_quota: int  # Allowed messages per session for core nodes
    leader_quota: int  # Allowed messages per session for potential leaders
    core_root: zkhash  # Merkle root of zk_id of the core nodes
    K_part_one: int  # First part of the signature public key (16 bytes)
    K_part_two: int  # Second part of the signature public key (16 bytes)
    pol_epoch_nonce: int  # PoL Epoch nonce
    pol_t0: int  # PoL constant t0
    pol_t1: int  # PoL constant t1
    pol_ledger_aged: zkhash  # Merkle root of the PoL eligible notes
    # Outputs:
    key_nullifier: zkhash  # derived from session, private index and private sk
```

The ProofOfQuotaWitness (Witness) structure must be filled as follows:

1. If the message contains cover traffic then:
   1. The core quota is used and the selector=0 value must be specified.
   2. The index counts the number of cover messages and must be below core_quota.
   3. The core_sk, core_path, core_path_selector are filled by the node to prove that the node is the core node.
   4. The rest of the ProofOfQuotaWitness, is filled with arbitrary data.
2. If the message contains data then:
   1. The leader quota is used and the selector=1 value must be specified.
   2. The index counts the number of data messages and must be below leader_quota.
   3. The core_sk, core_path, core_path_selector are filled with arbitrary data.
   4. The rest is filled with [Proof of Leadership][proof-of-leadership] (PoL) related data.

```python
class ProofOfQuotaWitness:
    index: int  # This is the index of the generated key. Limiting this index
                # limits the maximum number of key generated. (20 bits)
    selector: int  # Indicates if it's a leader (=1) or a core node (=0)
    # This part is filled randomly by potential leaders
    core_sk: zkhash  # sk corresponding to the zk_id of the core node
    core_path: list[zkhash]  # Merkle path proving zk_id membership (len = 20)
    core_path_selectors: list[bool]  # Indicates how to read the core_path (if
                                      # Merkle nodes are left or right in the path)
    # This part is filled randomly by core nodes
    pol_sl: int  # PoL slot
    pol_sk_starting_slot: int  # PoL starting slot of the slot secrets
    pol_note_value: int  # PoL note value
    pol_note_tx_hash: zkhash  # PoL note transaction
    pol_note_output_number: int  # PoL note transaction output number
    pol_noteid_path: list[zkhash]  # PoL Merkle path proving noteID membership
                                    # in ledger aged (len = 32)
    pol_noteid_path_selectors: list[bool]  # Indicates how to read the note_path
                                            # (if Merkle nodes are left or right in the path)
    pol_slot_secret: int  # PoL slot secret corresponding to sl
    pol_slot_secret_path: list[zkhash]  # PoL slot secret Merkle path to
                                         # sk_secrets_root (len = 25)
```

The ProofOfQuotaPublic and ProofOfQuotaWitness are passed to the
zero-knowledge circuits that generate the proof $\pi^{K^{n}{l}}{Q}$
which derives the key_nullifier ($\nu_s$) from session,
private index, private secret key during proof generation.

#### Step 2: Select Nodes

Select $h$ nodes from the set of nodes $\mathcal{N}$
in a random and verifiable manner.
For $i \in \{1,…,h\}$,
select $l_i = \text{CSPRBG}(H_{\mathbf N}(\rho))_{8} \mod N$,
where $\rho$ is a selection randomness (using little-endian encoding),
a shared secret derived during Proof of Quota generation,
the output of the $\text{CSPRBG}()_8$ is returns 8 bytes (little-endian).

```python
def select_nodes(key_collection: List[KeyPair], nodes: List[Node]) -> List[Node]:
    selected_nodes = []
    for keypair in key_collection:
        rand = pseudo_random(
            b"BlendNode",
            selection_randomness,
            8
        )
        index = modular_bytes(rand, NUM_NODES)
        selected_nodes.append(nodes[index])
    return selected_nodes

def modular_bytes(data: bytes, modulus: int) -> int:
    # Convert data into an unsigned big integer using little-endian.
    return int.from_bytes(data, byteorder='little') % modulus
```

#### Step 3: Generate Proofs of Selection

Generate proofs of selection $\pi^{K^{n}i,l_i}{S}$ for $i \in \{1,…,h\}$,
which proves that the public key $K^{n}_i$ correctly maps to the index $l_i$
from the set of nodes $\mathcal{N}$.

#### Step 4: Retrieve Public Keys

For $i \in \{1,…,h\}$,
retrieve public keys $\mathcal P = \{ {P^{l_1},..., P^{l_h}} \}$
for all $h$ selected nodes using the SDP protocol
(defined as provider_id in Identifiers).

```python
def blend_node_signing_public_keys(selected_nodes: List[Node]) -> List[Ed25519PublicKey]:
    return [node.signing_public_key for node in selected_nodes]
```

#### Step 5: Calculate Shared Keys

For $i \in \{1,…,h\}$,
calculate shared keys from a set of public keys of selected nodes
$\kappa^{n,i}{i} = k^{n}{i} \cdot P^{l_i}$.

```python
def derive_shared_keys(key_collection: List[KeyPair],
                       blend_node_signing_public_keys: List[Ed25519PublicKey]) -> List[SharedKey]:
    assert len(key_collection) == len(blend_node_signing_public_keys)
    assert len(key_collection) <= ENCAPSULATION_COUNT

    shared_keys = []
    for (keypair, blend_node_signing_public_key) in zip(key_collection,
                                                          blend_node_signing_public_keys):
        encryption_private_key = signing_private_key.derive_x25519()
        blend_node_encryption_public_key = blend_node_signing_public_key
        shared_key = diffie_hellman(encryption_private_key,
                                     blend_node_encryption_public_key)
        shared_keys.append(shared_key)
    return shared_keys
```

**Node Selection Mechanism:**

In step 2 of the algorithm above,
the sender constructs a blending path from nodes sampled at random
but in a verifiable manner.
The nodes are selected deterministically (and randomly) by the key value.
The key to node mapping is proven in step 3.

The node selection proof $\pi^{K^n_i,l_i}_{S}$ is constructed in such a way
that it proves only the fact that the key $K^n_i$ used for the encryption
maps correctly to the node index $l_i$ from the stable set of nodes
$\mathcal{N}$.
This proof should be considered a private proof intended only
for the recipient blend node.

This mechanism intends to limit the possibility of "double spending"
the emission token.
This restricts the sender's ability to use the same emission token twice,
first for constructing and emitting a message
and then for claiming a reward for it.

For more information about proof of selection
please refer to the [Proof of Selection Specification][proof-of-selection].

#### Message Initialization

The second step is to create an empty message $\mathbf M$
and fill the private header with random values.

#### Step 1: Create Empty Message

Create an empty message $\mathbf M$ (filled with zeros).

#### Step 2: Randomize Private Header

Randomize the private header:
For $\mathbf b_i \in \mathbf h = (\mathbf b_{1},...,\mathbf b_{\beta_{max}})$,
set $\mathbf b_{i} = \text {CSPRBG}( \rho_{i})_{|\mathbf b|}$,
where $\rho_i$ is some random value.

```python
def randomize_private_header() -> PrivateHeader:
    blending_headers = []
    for _ in range(ENCAPSULATION_COUNT):
        blending_header = pseudo_random(b"BlendRandom", entropy(),
                                         BlendingHeader.SIZE)
        blending_headers.append(blending_header)
    return blending_headers
```

#### Step 3: Fill Last Blend Headers

Fill the last $h$ blend headers with reconstructable payloads:
For $i = \{ 1+\beta_{max}-h,...,\beta_{max})$, do the following:

1. $t=\beta_{max} - i + 1$
2. $r_{t,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}t|1)){|K|}$
3. $r_{t,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}t|2)){|\pi^{K}_{Q}|}$
4. $r_{t,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}t|3)){|\sigma_{K}(\mathbf P)|}$
5. $r_{t,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}t|4)){|\pi^{K,k}_{S}|}$
6. $\mathbf{b}i = \{ r{t,1}, r_{t,2}, r_{t,3}, r_{t,4} \}$.

```python
def fill_last_blending_headers(private_header: PrivateHeader,
                                shared_keys: List[SharedKeys]) -> PrivateHeader:
    assert len(private_header) == ENCAPSULATION_COUNT
    assert len(shared_keys) <= ENCAPSULATION_COUNT

    pseudo_random_blending_headers = []
    for shared_key in shared_keys:
        r1 = pseudo_random(b"BlendInitialization", shared_key + b"\\x01", KEY_SIZE)
        r2 = pseudo_random(b"BlendInitialization", shared_key + b"\\x02",
                           PROOF_OF_QUOTA_SIZE)
        r3 = pseudo_random(b"BlendInitialization", shared_key + b"\\x03",
                           SIGNATURE_SIZE)
        r4 = pseudo_random(b"BlendInitialization", shared_key + b"\\x04",
                           PROOF_OF_SELECTION_SIZE)
        pseudo_random_blending_headers.append(r1 + r2 + r3 + r4)

    # Replace the last `len(shared_keys)` blending headers.
    private_header[-num_layers:] = pseudo_random_blending_headers
    return private_header
```

#### Step 4: Encrypt Last Blend Headers

Encrypt the last $h$ blend headers in a reconstructable manner:
For $i=\{ 1,...,h \}$, for $j=\{1, ..., i \}$, encrypt blend header:

$$ \mathbf{b}{\beta{max}-i+1}=E_{H_{\mathbf b}(\kappa^{n,l_j}{j})}(\mathbf b{\beta_{max}-i+1}) $$

```python
def encrypt_last_blending_headers(private_header: PrivateHeader,
                                   shared_keys: List[SharedKeys]) -> PrivateHeader:
    assert len(private_header) == ENCAPSULATION_COUNT
    assert len(shared_keys) <= ENCAPSULATION_COUNT

    for i, _ in enumerate(shared_keys):
        index = len(private_header) - i - 1
        for shared_key in shared_keys[:i + 1]:
            private_header[index] = encrypt(private_header[index], shared_key)

    return private_header
```

This prevents leakage of the encryption sequence when a message is encapsulated
less than $\beta_{max}$ times,
and enables us to encode the header in a way
that it can be reconstructed during the decapsulation.

#### Message Encapsulation

The final part of the algorithm is the true encapsulation of the payload.
That is, given the payload $\mathbf P_0$ and number of encapsulations
$h \le \beta_{max}$ we do the following.

For $i \in \{ 1,…,h \}$ do the following:

1. If $i=1$ then generate a new ephemeral key pair: $(K^n_0, k^n_0) \notin \mathbf K^n_h$.
2. Calculate the signature of the concatenation of the current header and payload: $\sigma_{K^{n}{i-1}}(\mathbf h{i-1}| \mathbf P_{i-1})$.
3. Using the shared key $\kappa^{n,l_i}i$, encrypt the payload: $\mathbf{P}i = E{H\mathbf{P}( \kappa^{n,l_i}i)}(\mathbf P{i-1})=\mathbf{P}{i-1} \oplus \text {CSPRBG}(H\mathbf{P}(\kappa^{n,l_i}_i))$.
4. Shift blending headers by one downward: $\mathbf b_z \rightarrow \mathbf b_{z+1}$ for $z \in \{ 1,…,\beta_{max} \}$. The first blending header is now empty, and the last blending header is truncated.
5. Fill the blending header $\mathbf b_1$, where $1$ refers to the top position:
   1. If $i=1$ then:
      1. Fill the proof of quota with random data: $\pi^{K^{n}0}{Q}= \text {CSPRBG}(H_\mathbf{I}(k^{n}0)){|\pi^{K}_{Q}|}$
      2. Set the last flag to 1: $\Omega=1$
   2. Else set the last flag to 0: $\Omega = 0$
   3. $\mathbf{b}1 = \{ K^n{i-1}, \pi^{K^{n}{i-1}}{Q}, \sigma_{K^{n}{i-1}}(\mathbf h{i-1}|\mathbf P_{i-1}), \pi^{K^{n}i,l_i}{S}, \Omega \}$.
6. Using shared key $\kappa^{n,l_i}i$, encrypt the private header $\mathbf{h}{E_{i}} = E_{H_{\mathbf b}(\kappa^{n,l_i}_i)}(\mathbf{h}_i)$:

For each $\mathbf b_j \in \mathbf h_i = (\mathbf b_1,...,\mathbf b_{m_{max}})$ using a shared key $\kappa^{n,l_i}i$, encrypt the blending header: $\mathbf{b}j = E{H\mathbf{b}(\kappa^{n,l_i}_i)}(\mathbf{b}_j)=\mathbf{b}j \oplus \text {CSPRBG}(H\mathbf{b}(\kappa^{n,l_i}_i))$.

Fill in the public header: $\mathbf H=\{ K^{n}h, \pi^{K^{n}h}{Q}, \sigma{K^{n}_h}(\mathbf P_h) \}$.

The message is encapsulated.

```python
def encapsulate(
    private_header: PrivateHeader,
    payload: Payload,
    shared_keys: List[SharedKeys],
    key_collection: List[KeyPair],
    list_of_pos: List[ProofOfSelection]
) -> bytes:
    # Step 1 ~ 6: Encapsulate private header and payload
    prev_keypair = KeyPair.random()
    is_first_selected = True
    for shared_key, keypair, proof_of_selection) in zip(shared_keys, key_collection,
                                                          list_of_pos):
        private_header, payload = encapsulate_private_part(
            private_header,
            payload.bytes(),
            shared_key,
            prev_keypair.signing_private_key,
            prev_keypair.proof_of_quota,
            proof_of_selection,
            # The first encapsulation is for the last decapsulation.
            is_last=is_first_selected,
        )
        prev_keypair = keypair
        is_first = False

    # Fill in the public header
    public_header = PublicHeader(
        prev_keypair.signing_public_key,
        prev_keypair.proof_of_quota,
        signature=sign(private_part, prev_keypair.signing_private_key),
        version=1,
    )

    return public_header.bytes() + b"".join(private_headers) + payload

def encapsulate_private_part(
    private_header: PrivateHeader,
    payload: EncryptedPayload,
    shared_key: SharedKey,
    signing_private_key: Ed25519PrivateKey,
    proof_of_quota: ProofOfQuota,
    proof_of_selection: ProofOfSelection,
    is_last: bool
) -> bytes:
    # Step 2: Calculate a signature on `private_header + payload`.
    signature = sign(
        signing_body(private_header, payload),
        signing_private_key
    )

    # Step 3: Encrypt the payload
    payload = encrypt(payload, shared_key)

    # Step 4: Shift blending headers by one rightward.
    private_header.pop()  # Remove the last blending header

    # Step 5: Add the new blending header to the front.
    blending_header = BlendingHeader(
        signing_private_key.public(),
        proof_of_quota,
        signature,
        proof_of_selection,
        is_last
    )
    private_header.insert(0, blending_header.bytes())

    # Step 6: Encrypt the private header
    for i, _ in enumerate(private_header):
        private_header[i] = encrypt(private_header[i], shared_key)

    return private_header, payload

def signing_body(private_header: PrivateHeader, payload: EncryptedPayload) -> bytes:
    return b"".join(private_headers) + payload
```

#### Message Decapsulation

If a message $\mathbf M$ is received by the node and its public header is correct - that is, it was verified according to the relay logic defined here: Relaying - then the node $l$ executes the following logic:

1. Calculate the shared secret. Using the key $K^{n}_l \in \mathbf H$ from the public header of the message $\mathbf M$ and the private key $p^l$ of the node $l$ calculate: $\kappa^{n,l}_l = K^{n}_l \cdot p^l$.
2. Decrypt the private header using the shared key $\kappa^{n,l}_l$. For each $\mathbf b_j \in \mathbf h = (\mathbf b_1,...,\mathbf b_{\beta_{max}})$ using a shared key $\kappa^{n,l}l$ decrypt the blending header: $\mathbf{b}j = D{H\mathbf{b}(\kappa^{n,l}_l)}(\mathbf{b}_j)=\mathbf{b}j \oplus \text {CSPRBG}(H\mathbf{b}(\kappa^{n,l}_l))$.
3. Verify the header:
   1. If the proof $\pi^{K^{n}l,l}{S}\in \mathbf b_1$ is not correct, discard the message. That is, if the node index $l$ does not correspond to the $K^{n}_l\in \mathbf H$, then the message must be rejected.
   2. If the key $K^{n}_l \in \mathbf b_1$ was already seen, discard the message.
   3. If the proof $\pi^{K^{n}l,l}{Q} \in \mathbf b_1$ is incorrect, discard the message.
4. Using the blending header $\mathbf b_1$, set the public header: $\mathbf H_l = \{K^{n}l \in \mathbf b_1,\pi^{K^{n}l,l}{Q} \in \mathbf b_1 ,\sigma{K^{n}_l}(\mathbf {h|P}) \in \mathbf b_1\}$.
5. Decrypt the payload, using the shared key $\kappa^{n,l}l$: $\mathbf{P}l =D{H\mathbf{P}(\kappa^{n,l}l)}=\mathbf{P} \oplus \text {CSPRBG}(H{\mathbf P}(\kappa^{n,l}_l))$.
6. Reconstruct the blend header:
   1. $r_{l,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}l|1)){|K|}$
   2. $r_{l,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}l|2)){|\pi^{K}_{Q}|}$
   3. $r_{l,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}l|3)){|\sigma_{K}(\mathbf P)|}$
   4. $r_{l,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}l|4)){|\pi^{K,k}_{S}|}$
   5. $b = \{ r_{l,1}, r_{l,2}, r_{l,3}, r_{l,4} \}$.
7. Encrypt the blending header: $\hat b = E_{H_\mathbf{b}(\kappa^{n,{l}}_{l})}(b)$.
8. Shift blending headers by one upward: $\mathbf b_z \rightarrow \mathbf b_{z-1}$ for $z \in \{ 1,…,\beta_{max} \}$. The first blending header is truncated, and the last blending header is empty.
9. Reconstruct the private header: $\mathbf h_{E_{l}} = \{$ $…$ $\mathbf{b}{\beta{max}} = \hat b$, $\}$.
10. If the signature from the public header does not match the signature of the reconstructed header and the decrypted payload, discard the message: $\text{verify\sig}(\sigma{K^n_l}(\mathbf{h}_{E_l}| \mathbf{P}_l), \mathbf{h}| \mathbf{P},{K^n_l})$.
11. The message is decapsulated.
12. Follow the message processing logic: Processing.

```python
def decapsulate(
    message: bytes,
    signing_private_key: Ed25519PrivateKey
) -> bytes:
    # Step 1: Derive the shared key.
    encryption_private_key = signing_private_key.derive_x25519()
    public_header = PublicHeader.from_bytes(
        message[Header.SIZE : Header.SIZE + PublicHeader.SIZE]
    )
    shared_key = diffie_hellman(
        encryption_private_key,
        public_header.signing_public_key.derive_x25519()
    )

    # Step 2: Decrypt the private header
    private_header = message[
        Header.SIZE + PublicHeader.SIZE:
        Header.SIZE + PublicHeader.SIZE + (BlendingHeader.SIZE * ENCAPSULATION_COUNT)
    ]
    for i, _ in enumerate(private_header):
        private_header[i] = decrypt(private_header[i], shared_key)

    # Step 3: Verify the first blending header
    first_blending_header = BlendingHeader.from_bytes(private_header[0])
    first_blending_header.validate()

    # Step 4: Construct the new public header
    public_header = PublicHeader(
        first_blending_header.signing_public_key,
        first_blending_header.proof_of_quota,
        first_blending_header.signature,
        version= 1,
    )

    # Step 5: Decrypt the payload
    payload_offset = (
        Header.SIZE + PublicHeader.SIZE + (BlendingHeader.SIZE * ENCAPSULATION_COUNT)
    )
    payload = message[payload_offset:]
    payload = decrypt(payload, shared_key)

    # Step 6: Reconstruct the new blending header
    r1 = pseudo_random(b"BlendInitialization", shared_key + b"\\x01", KEY_SIZE)
    r2 = pseudo_random(b"BlendInitialization", shared_key + b"\\x02",
                       PROOF_OF_QUOTA_SIZE)
    r3 = pseudo_random(b"BlendInitialization", shared_key + b"\\x03", SIGNATURE_SIZE)
    r4 = pseudo_random(b"BlendInitialization", shared_key + b"\\x04",
                       PROOF_OF_SELECTION_SIZE)

    # Step 7: Encrypt the new blending header
    encrypted_new_blending_header = encrypt(r1 + r2 + r3 + r4, shared_key)

    # Step 8: Shift blending headers by one leftward.
    private_header.pop(0)  # Remove the first blending header.

    # Step 9: Add the new blending header to the end.
    private_header.append(encrypted_new_blending_header)

    # Step 10: Verify the signature
    verify_signature(
        first_blending_header.signature,
        signing_body(private_header, payload)
        first_blending_header.signing_public_key,
    )

    header = message[0:Header.SIZE]
    return header + public_header.bytes() + b"".join(private_header) + payload
```

## Implementation Considerations

### Security Considerations

**Message Privacy:**

- The multi-layered encryption ensures that intermediate nodes cannot determine the message origin or final destination
- Each encapsulation layer uses unique ephemeral keys to prevent correlation attacks
- The reconstructable header mechanism prevents leakage of the encryption sequence

**Proof Verification:**

- All Proof of Quota (PoQ) proofs must be verified to ensure message authenticity
- Proof of Selection (PoS) proofs prevent double-spending of emission tokens
- Key nullifiers must be checked to prevent key reuse attacks

**Key Management:**

- Ephemeral keys should be generated using cryptographically secure random sources
- Private keys must never be logged or persisted beyond their required lifetime
- Shared keys derived via Diffie-Hellman must use secure elliptic curve operations

### Performance Optimization

**Cryptographic Operations:**

- BLAKE2b hash operations are efficient but should still be batched when possible
- XOR-based encryption/decryption is computationally inexpensive
- Signature generation and verification are the most expensive operations and should be minimized

**Memory Management:**

- Private headers with $\beta_{max}$ blending headers can consume significant memory
- Implementations should reuse buffers for encryption/decryption operations
- Payload sizes (34 KiB) should be considered when allocating message buffers

### Implementation Notes

**Byte Order:**

- All multi-byte integers use little-endian encoding unless otherwise specified
- The modular_bytes function converts bytes to integers using little-endian format
- Implementations must maintain consistent endianness throughout

**Error Handling:**

- Invalid proofs should result in immediate message rejection
- Signature verification failures must discard the message
- Implementations should not leak timing information about verification failures

**Integration Points:**

- Service Declaration Protocol (SDP) integration is required for node public key retrieval
- Proof of Leadership (PoL) integration is needed for leader quota verification
- The Formatting specification provides additional context for message structure

## Appendix

### Example: Complete Encapsulation and Decapsulation

The following example demonstrates the above mechanism with $\beta_{max}=4,h=3$.
The protocol version in the header is omitted for simplicity.

#### Initialization

##### Create Empty Message (Example)

Create an empty message: $\mathbf{M} = (\mathbf{H}=0,\mathbf{h}=0,\mathbf{P}=0)$

##### Randomize Private Header (Example)

Randomize the private header: $\mathbf h_0 = \{$

$\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}$,

$\mathbf b_2 = \text {CSPRBG}( \rho_{2})_{|\mathbf b|}$,

$\mathbf b_3 = \text {CSPRBG}( \rho_{3})_{|\mathbf b|}$,

$\mathbf b_4 = \text {CSPRBG}( \rho_{4})_{|\mathbf b|}$,

$\}$.

##### Fill Last h Blend Headers (Example)

Fill the last $h$ blend headers with reconstructable payloads: $\mathbf h_0 = \{$

$\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}$,

$\mathbf b_2 = \{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4} \}$,

$\mathbf b_3 = \{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4} \}$,

$\mathbf b_4 = \{ r_{l_1,1}, r_{l_1,2} ,r_{l_1,3}, r_{l_1,4} \}$,

$\}$.

##### Encrypt Last h Blend Headers (Example)

Encrypt the last $h$ blend headers in a reconstructable manner: $\mathbf h_{E_0} = \{$

$\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}$,

$\mathbf b_2 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}{3})}E{H_\mathbf{b}(\kappa^{n,{l_2}}{2})}E{H_\mathbf{b}(\kappa^{n,{l_1}}{1})}(\{ r{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4} \})$,

$\mathbf b_3 = E_{H_\mathbf{b}(\kappa^{n,{l_2}}{2})}E{H_\mathbf{b}(\kappa^{n,{l_1}}{1})}(\{ r{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4} \})$,

$\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_1}}{1})}(\{ r{l_1,1}, r_{l_1,2} ,r_{l_1,3}, r_{l_1,4} \})$,

$\}$.

#### Encapsulation

**Iteration i=1:**

1. Generate a new ephemeral key pair: $(K^n_0, k^n_0) \notin \mathbf K^n$.
2. Calculate the signature of the header and the payload: $\sigma_{K^{n}0}(\mathbf{h}{E_0}| \mathbf{P}_0)$.
3. Using shared key $\kappa^{n,l_1}{1}$ encrypt the payload: $\mathbf P_1 = E{H_\mathbf{P}(\kappa^{n,l_1}_{1})}(\mathbf P_0)$.
4. Shift blending headers by one down: $\mathbf h_1 = \{$ $\mathbf b_1 = \empty$, ... $\}$.
5. Fill the first blending header with signature, proof, and flag.
6. Using shared key $\kappa^{n,l_1}{1}$ encrypt the private header: $\mathbf{h}{E_{1}} = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\mathbf{h}_1)$.

**Iteration i=2:**

Continue with similar steps using $\kappa^{n,l_2}_{2}$.

**Iteration i=3:**

Continue with similar steps using $\kappa^{n,l_3}_{3}$.

The above calculations give us the final message $\mathbf {M = (H,h,P)}$ where:

$\mathbf H = (K^{n}_3,~ \pi^{K^{n}_3}Q,~ \sigma{K^{n}3}(\mathbf{h}{E_3}|\mathbf{P}_3))$,

$\mathbf{h} = \mathbf{h}_{E_3}$ with fully encrypted blending headers,

$\mathbf{P} = \mathbf P_3= E_{H_{\mathbf P_0}(\kappa^{n,l_3}3)}E{H_{\mathbf P}(\kappa^{n,l_2}2)}E{H_{\mathbf P}(\kappa^{n,l_1}_1)}(\mathbf{P}_0)$.

#### Decapsulation

This section demonstrates decapsulation of the above message.
The node doing the processing is the rightful recipient of the message
and the public header is verified to be correct.

**Node l=l_3:**

1. Calculate shared secret: $\kappa^{n,l_3}{3}=K^n{3} \cdot p^{l_3}$
2. Decrypt the header: $\mathbf h_{l_3} = D_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\mathbf{h})$
3. Verify the header (proof of selection, key novelty, proof of quota)
4. Reconstruct the public header
5. Decrypt the payload: $\mathbf{P}{l_3} = D{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\mathbf P)$
6. Reconstruct the blend header with pseudo-random values
7. Encrypt the reconstructed blend header
8. Shift blending headers by one upward
9. Reconstruct the private header
10. Verify the signature
11. Message is decapsulated
12. Follow the processing logic

**Node l=l_2 and l=l_1:**

Similar decapsulation steps are performed by subsequent nodes in the blending path.

## References

### Normative

- [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) - Key words for use in LIPs to Indicate Requirement Levels
- [Key Types and Generation Specification](https://nomos-tech.notion.site/Key-Types-and-Generation-Specification-215261aa09df81088b8fd7c3089162e8)
  \- Defines the cryptographic key types used in the Blend protocol
- [Proof of Quota Specification](https://nomos-tech.notion.site/Proof-of-Quota-Specification-215261aa09df81d88118ee22205cbafe)
  \- ZK-SNARK proof limiting message encapsulations
- [Proof of Selection Specification](https://nomos-tech.notion.site/Proof-of-Selection-215261aa09df81f2bbadc13ce0a2c3e2)
  \- Verifiable proof of node selection for message routing
- [Service Declaration Protocol](https://www.notion.so/Service-Declaration-Protocol)
  \- Protocol for global node registration and discovery
- [Proof of Leadership Specification](https://nomos-tech.notion.site/Proof-of-Leadership-215261aa09df8145a0f2c0d059aed59c)
  \- Cryptarchia consensus mechanism for leader selection
- [BLAKE2b](https://www.blake2.net/) - Cryptographic hash function
- [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) - Edwards-Curve Digital Signature Algorithm (EdDSA)
- [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748) - Elliptic Curves for Security (X25519)

### Informative

- [Message Encapsulation Mechanism](https://nomos-tech.notion.site/Message-Encapsulation-Mechanism-215261aa09df81309d7fd7f1c2da086b)
  \- Original Message Encapsulation documentation
- [Blend Protocol](https://nomos-tech.notion.site/Blend-Protocol-215261aa09df81ae8857d71066a80084)
  \- Context for message structure and formatting conventions
- [Blend Protocol Formatting][blend-formatting]
  \- Message formatting conventions

[blend-protocol]: https://nomos-tech.notion.site/Blend-Protocol-215261aa09df81ae8857d71066a80084
[blend-formatting]: https://nomos-tech.notion.site/Formatting-215261aa09df81a3b3ebc1f438209467
[key-types]: https://nomos-tech.notion.site/Key-Types-and-Generation-Specification-215261aa09df81088b8fd7c3089162e8
[proof-of-quota]: https://nomos-tech.notion.site/Proof-of-Quota-Specification-215261aa09df81d88118ee22205cbafe
[proof-of-selection]: https://nomos-tech.notion.site/Proof-of-Selection-215261aa09df81f2bbadc13ce0a2c3e2
[sdp]: https://www.notion.so/Service-Declaration-Protocol
[proof-of-leadership]: https://nomos-tech.notion.site/Proof-of-Leadership-215261aa09df8145a0f2c0d059aed59c

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
