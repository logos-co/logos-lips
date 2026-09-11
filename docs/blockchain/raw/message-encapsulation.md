# MESSAGE-ENCAPSULATION-MECHANISM

| Field | Value |
| --- | --- |
| Name | Message Encapsulation Mechanism |
| Slug | 91 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors | Youngjoon Lee <youngjoon@logos.co>, Alexander Mozeika <alexander.mozeika@logos.co>, Mehmet Gonen <mehmet@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Daniel Kashepava <danielkashepava@logos.co>, Daniel Sanchez Quiros <danielsq@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/message-encapsulation.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/message-encapsulation.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/message-encapsulation.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/message-encapsulation.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-09 |
| 1.0.1 | [RFC] Remove Concept of a Session | 2026-06-22 |
| 1.1.0 | [RFC] Replace the BLAKE2b-Based PRNG with ChaCha20 (ChaCha20Rng) | 2026-08-28 |
| 1.2.0 | Removed the `version` field from the public header ([Bedrock Eras](bedrock-eras.md)). | 2026-09-04 |

# Introduction

The message encapsulation mechanism is part of the Blend Protocol and it describes the cryptographic operations necessary for building and processing messages by a Blend node.

This document is part of the [Formatting](blend-protocol.md#formatting) section. Please read through that document to better understand the context of the encapsulation mechanism and constructions used here.

# Overview

The Message Encapsulation Mechanism is a core component of the Blend Protocol that ensures privacy and security during node-to-node message transmission. By implementing multiple encryption layers and cryptographic operations, this mechanism keeps messages confidential while concealing their origins.

The encapsulation process includes:

- Building a multi-layered structure with public headers, private headers, and encrypted payloads
- Using cryptographic keys and proofs for layer security and authentication
- Applying verifiable random node selection for message routing
- Using shared key derivation for secure inter-node communication

This document outlines the cryptographic notation, data structures, and algorithms essential to the encapsulation process, providing a complete specification for implementing this mechanism within the Blend Protocol.

## Notation

- $`\mathbf K^{n}_h = \{(K^{n}_{0}, k^{n}_{0}, \pi_{Q}^{K_{0}^{n}}),...,(K^{n}_{h-1}, k^{n}_{h-1}, \pi_{Q}^{K_{h-1}^{n}}) \}`$ is a collection of $`h`$ key pairs for a node $`n`$ with proofs of quota, where $`K_{i}^{n}`$ is the $`i`$-th public key and $`k_{i}^{n}`$ is its corresponding private key, and $`\pi_{Q}^{K_{i}^{n}}`$ is its proof of quota.
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
      key_nullifier: zkhash # 32 bytes
      proof: bytes # 128 bytes
  ```

  For more information about key generation mechanism please refer to [Key Types and Generation](key-types-and-generation.md).

  For more information about proof of quota please refer to [Proof of Quota](blend-protocol.md#proof-of-quota).

- $`P^n`$ is a public key of the node $`n`$, which is globally accessible using the Service Declaration Protocol (SDP). We are using this notation to distinguish the origin of the key, hence the following simplified notation.
  For more information about Service Declaration Protocol please refer to [Service Declaration Protocol](bedrock-service-declaration-protocol.md).

- $`\mathcal{N} = \text{SDP}(e)`$ is the set of nodes globally accessible using the SDP.
  ```python
  Nodes = set[Ed25519PublicKey]  # set of signing public keys
  ```

- $`N =|\mathcal{N}|`$ is the number of nodes globally accessible using the SDP.
- $`\kappa^{n,m}_{i} = k^{n}_{i} \cdot P^{m} = p^{m} \cdot K^{n}_{i}`$, is a shared key calculated between node $`n`$ and node $`m`$ using the $`i`$-th key of the node $`n`$, $`P^{m}`$ is the public key of the node $`m`$ retrieved from the SDP protocol and $`p^m`$ is its corresponding private key.
  ```python
  SharedKey = bytes  # KEY_SIZE
  ```

- $`\pi^{K^{n}_{l},m}_{S}`$ is the proof of selection of the public key $`K^{n}_l`$ to the node index $`m`$ from a set of all nodes $`\mathcal N`$.
  ```python
  ProofOfSelection = bytes
  PROOF_OF_SELECTION_SIZE = 32
  ```

  For more information about the proof of selection, please refer to [Proof of Selection](blend-protocol.md#proof-of-selection).

- $`H_{\mathbf N}()`$ is a domain-separated hash function dedicated to the node index selection (the implementation of the hash function is `blake2b`).
  ```python
  def hashds(domain=b"BlendNode", data: bytes) -> bytes:
      return Blake2B.hash256(domain + data)
  ```

- $`H_\mathbf{I}()`$ is a domain-separated hash function dedicated to the initialization of the blend header (the implementation of the hash function is `blake2b`).
  ```python
  def hashds(domain=b"BlendInitialization", data: bytes) -> bytes:
      return Blake2b.hash256(domain + data)
  ```

- $`H_\mathbf{b}()`$ is a domain-separated hash function dedicated to the blend header encryption operations (the implementation of the hash function is `blake2b`).
  ```python
  def hashds(domain=b"BlendHeader", data: bytes) -> bytes:
      return Blake2b.hash256(domain + data)
  ```

- $`H_\mathbf{P}()`$ is a domain-separated hash function dedicated to the payload encryption operations (the implementation of the hash function is `blake2b`).
  ```python
  def hashds(domain=b"BlendPayload", data: bytes) -> bytes:
      return Blake2b.hash256(domain + data)
  ```

- $`\beta_{max}`$ is the maximal number of blending headers in the private header.
  ```python
  ENCAPSULATION_COUNT: int
  ```

- $`\text {CSPRBG}()`$ is a generalized cryptographically secure pseudo-random bytes generator, it is implemented as [ChaCha20-Based PRNG Construction](common-cryptographic-components.md#chacha20-based-prng-construction).
- $`\text {CSPRBG}()_{x}`$ is a cryptographically secure pseudo-random bytes generator whose output is restricted to $`x`$ bytes, it is implemented as [ChaCha20-Based PRNG Construction](common-cryptographic-components.md#chacha20-based-prng-construction).
  ```python
  def pseudo_random(domain: bytes, key: bytes, size: int) -> bytes:
      rand = ChaCha20Rng.from_seed(hashds(domain, key)).generate(size)
      assert len(rand) == size
      return rand
  ```

  The $`\text {CSPRBG}`$ seed is exactly 32 bytes: the domain-separated hash functions above return 32-byte digests, which are used directly as the seed.

  Every $`\text {CSPRBG}`$ invocation in this specification generates at most a message-sized output, so the interoperability note of the [ChaCha20-Based PRNG Construction](common-cryptographic-components.md#chacha20-based-prng-construction) applies: an RFC 8439 (IETF) ChaCha20 with a zero nonce is byte-for-byte compatible.

- $`|t|`$ returns the length of the $`t`$ expressed in bytes.
- $`\oplus`$ is a XOR operation.
  ```python
  def xor(a: bytes, b: bytes) -> bytes:
      assert len(a) == len(b)
      return bytes(x ^ y for x, y in zip(a, b))
  ```

- $`E_{k}(x)=\text{CSPRBG}(k) \oplus x`$ is an encryption that uses a cryptographically secure pseudo-random bytes generator with a secret $`k`$ and payload $`x`$.
  ```python
  def encrypt(data: bytes, key: bytes -> bytes:
      return xor(data, pseudo_random(b"BlendEncapsulation", key, len(data))))
  ```

- $`D_{k}(x)=\text{CSPRBG}(k) \oplus x`$ is a decryption that uses using cryptographically secure pseudo-random bytes generator with a secret $`k`$ and payload $`x`$.
  ```python
  def decrypt(data: bytes, key: bytes) -> bytes:
      return xor(data, pseudo_random(b"BlendEncapsulation", key, len(data))))
  ```

# Construction

## Message Structure

We start with a definition of the message structure that must be used to provide the protocol with the envisioned capabilities.

A node $`n`$ constructs a message $`\mathbf M = (\mathbf H, \mathbf h, \mathbf P)`$ according to the format presented below.

![Diagram](message-encapsulation/assets/215261aa-09df-818e-9ffd-ed2d35b9d288.jpg)

```python
class Message:
    public_header: PublicHeader
    private_header: PrivateHeader
    payload: EncryptedPayload
```

1. $`\mathbf H`$ is a public header:
    1. $`K^{n}_i`$, a public key from the set $`\mathbf K^n_h`$.
    2. $`\pi^{K^{n}_i}_{Q}`$, a corresponding proof of quota for the key $`K^{n}_i`$ from the set $`\mathbf K^n_h`$ and contains its proof nullifier.
    3. $`\sigma_{K^{n}_{i}}(\mathbf {h|P}_i)`$, a signature of the concatenation of the $`i`$-th encapsulation of the payload $`\mathbf P`$ and the private header $`\mathbf h`$, that can be verified by the public key $`K^{n}_{i}`$.

    ```python
    Signature = bytes
    SIGNATURE_SIZE = 64

    class PublicHeader:
        signing_public_key: Ed25519PublicKey
        proof_of_quota: ProofOfQuota
        signature: Signature
    ```

2. $`\mathbf h = (\mathbf b_1,...,\mathbf b_{\beta_{max}})`$ is an encrypted private blending header $`\mathbf b_l`$:
    1. $`K^{n}_{l}`$, a public key from the set $`\mathbf K^n_h`$.
    2. $`\pi^{K^{n}_{l}}_{Q}`$, a corresponding proof of quota for the key $`K^{n}_l`$ from the $`\mathbf K^n_h`$ and contains its proof nullifier.
    3. $`\sigma_{K^{n}_{l}}(\mathbf {h|P}_l)`$, a signature of the concatenation of the $`l`$-th encapsulation of the payload $`\mathbf P`$ and the private header $`\mathbf h`$, that can be verified by public key $`K^{n}_{l}`$.
    4. $`\pi^{K^{n}_{l+1},m_{l+1}}_{S}`$, a proof of selection of the node index $`m_{l+1}`$ assuming public key $`K^{n}_{l+1}`$.
    5. $`\Omega`$, a flag that indicates that this is the last blending header.

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

3. $`\mathbf P`$ is a payload.
    ```python
    EncryptedPayload = bytes

    PAYLOAD_BODY_SIZE = 18187  # Max_Body_Length, Payload Formatting

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

## **Keys and Proof Generation**

For simplicity of the presentation, we do not distinguish between signing and encryption keys. However, in practice, such a distinction is necessary, that is:

- The $`\mathbf K^n_h`$ contains Ephemeral Signing Keys (ESK) that are part of the PoQ generation and are used for message signing; these are included in the public and private headers.
- Shared secret keys used for encryption of messages are generated from an Ephemeral Encryption Key (sender), which is derived from the ESK, and from a Non-ephemeral Encryption Key (NEK) (receiver), which is derived from a Non-ephemeral Signing Key (NSK) retrieved from the SDP protocol.

For more information, look at [Key Types and Generation](key-types-and-generation.md).

The first step is to generate a set of keys alongside all necessary proofs that will be used in the next steps of the algorithm.

1. Generate the collection $`\mathbf K^n_h`$, where $`h`$ defines the number of encapsulation layers such that $`h \le \beta_{max}`$.
    ```python
    def generate_key_collection(num_layers: int) -> List[KeyPair]:
        assert num_layers <= ENCAPSULATION_COUNT
        # Generate `num_layers` random KeyPairs non-deterministically.
        return [KeyPair.random() for _ in range(num_layers)]
    ```

    The key collection generation requires generation of Proof of Quota ([Proof of Quota](proof-of-quota.md)) for each key, as defined in the following steps.

    1. The `ProofOfQuotaPublic` ([Public values](proof-of-quota.md#public-values)) structure must be filled with public information:
        1. `core_quota`, `leader_quota`, `core_root`, `pol_epoch_nonce`, `pol_t0`, `pol_t1`, `pol_ledger_aged` are retrieved from the blockchain.
        2. `K_part_one` and `K_part_two` are first and second part of the signature key (`KeyPair`) generated by the above `generate_key_collection`.
    2. The `ProofOfQuotaWitness` ([Witness](proof-of-quota.md#witness)) structure must be filled as follows:
        1. If the message contains cover traffic then:
            1. We assume that the core quota is used and the `selector=0` value must be specified.
            2. The `index` counts the number of cover messages and must be below `core_quota`.
            3. The `core_sk`, `core_path`, `core_path_selector` are filled by the node to prove that the node is the core node.
            4. The rest of the `ProofOfQuotaWitness`, is filled with arbitrary data.
        2. If the message contains data then:
            1. We assume that the leader quota is used and the `selector=1` value must be specified.
            2. The `index` counts the number of data messages and must be below `leader_quota`.
            3. The `core_sk`, `core_path`, `core_path_selector` are filled with arbitrary data.
            4. The rest is filled with Proof of Leadership (PoL — [Proof of Leadership](cryptarchia-proof-of-leadership.md)) related data.
        3. The `ProofOfQuotaPublic` and `ProofOfQuotaWitness` are passed to the zero-knowledge circuits that generate the proof $`\pi^{K^{n}_{l}}_{Q}`$ which derives the `key_nullifier` ($`\nu_e`$) from `pol_epoch_nonce`, private `index`, private secret key during proof generation.

2. Select $`h`$ nodes from the set of nodes $`\mathcal{N}`$ in a random and verifiable manner. For $`i \in \{1,…,h\}`$, select $`l_i = \text{CSPRBG}(H_{\mathbf N}(\rho))_{8} \mod N`$, where $`\rho`$ is a [selection randomness](proof-of-quota.md) (using little-endian encoding), a shared secret derived during Proof of Quota generation, the output of the $`\text{CSPRBG}()_8`$ is returns 8 bytes (little-endian).
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

3. Generate proofs of selection $`\pi^{K^{n}_i,l_i}_{S}`$ for $`i \in \{1,…,h\}`$, which proves that the public key $`K^{n}_i`$ correctly maps to the index $`l_i`$ from the set of nodes $`\mathcal{N}`$.
4. For $`i \in \{1,…,h\}`$, retrieve public keys $`\mathcal P = \{ {P^{l_1},..., P^{l_h}} \}`$ for all $`h`$ selected nodes using the SDP protocol (defined as `provider_id` in [Identifiers](bedrock-service-declaration-protocol.md#identifiers)).
    ```python
    def blend_node_signing_public_keys(selected_nodes: List[Node]) -> List[Ed25519PublicKey]:
        return [node.signing_public_key for node in selected_nodes]
    ```

5. For $`i \in \{1,…,h\}`$, calculate shared keys from a set of public keys of selected nodes $`\kappa^{n,i}_{i} = k^{n}_{i} \cdot P^{l_i}`$.
    ```python
    def derive_shared_keys(key_collection: List[KeyPair], blend_node_signing_public_keys: List[Ed25519PublicKey]) -> List[SharedKey]:
        assert len(key_collection) == len(blend_node_signing_public_keys)
        assert len(key_collection) <= ENCAPSULATION_COUNT

        shared_keys = []
        for (keypair, blend_node_signing_public_key) in zip(key_collection, blend_node_signing_public_keys):
            encryption_private_key = signing_private_key.derive_x25519()
            blend_node_encryption_public_key = blend_node_signing_public_key
            shared_key = diffie_hellman(encryption_private_key, blend_node_encryption_public_key)
            shared_keys.append(shared_key)
        return shared_keys
    ```

In step 2 of the algorithm above, the sender constructs a blending path from nodes sampled at random but in a verifiable manner. The nodes are selected deterministically (and randomly) by the key value. The *key to node* mapping is proven in step 3.

The node selection proof $`\pi^{K^n_i,l_i}_{S}`$ is constructed in such a way that it proves only the fact that the key $`K^n_i`$ used for the encryption maps correctly to the node index $`l_i`$ from the stable set of nodes $`\mathcal{N}`$. This proof should be considered a private proof intended only for the recipient blend node.

This mechanism intends to limit the possibility of “double spending” the emission token. This restricts the sender's ability to use the same emission token twice, first for constructing and emitting a message and then for claiming a reward for it.

For more information about proof of selection please refer to [Proof of Selection](blend-protocol.md#proof-of-selection).

## **Message** **Initialization**

The second step is to create an empty message $`\mathbf M`$ and fill the private header with random values.

1. Create an empty message $`\mathbf M`$ (filled with zeros).
2. Randomize the private header: For $`\mathbf b_i \in \mathbf h = (\mathbf b_{1},...,\mathbf b_{\beta_{max}})`$, set $`\mathbf b_{i} = \text {CSPRBG}( \rho_{i})_{|\mathbf b|}`$, where $`\rho_i`$ is some random value.
    ```python
    def randomize_private_header() -> PrivateHeader:
        blending_headers = []
        for _ in range(ENCAPSULATION_COUNT):
            blending_header = pseudo_random(b"BlendRandom", entropy(), BlendingHeader.SIZE)
            blending_headers.append(blending_header)
        return blending_headers
    ```
3. Fill the last $`h`$ blend headers with reconstructable payloads: For $`i = \{ 1+\beta_{max}-h,...,\beta_{max})`$, do the following:
    1. $`t=\beta_{max} - i + 1`$
    2. $`r_{t,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}_t|1))_{|K|}`$
    3. $`r_{t,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}_t|2))_{|\pi^{K}_{Q}|}`$
    4. $`r_{t,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}_t|3))_{|\sigma_{K}(\mathbf P)|}`$
    5. $`r_{t,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,t}_t|4))_{|\pi^{K,k}_{S}|}`$
    6. $`\Omega=0`$
    7. $`\mathbf{b}_i = \{ r_{t,1}, r_{t,2}, r_{t,3}, r_{t,4}, \Omega\}`$.

    ```python
    def fill_last_blending_headers(private_header: PrivateHeader, shared_keys: List[SharedKeys]) -> PrivateHeader:
        assert len(private_header) == ENCAPSULATION_COUNT
        assert len(shared_keys) <= ENCAPSULATION_COUNT

        pseudo_random_blending_headers = []
        for shared_key in shared_keys:
            r1 = pseudo_random(b"BlendInitialization", shared_key + b"\x01", KEY_SIZE)
            r2 = pseudo_random(b"BlendInitialization", shared_key + b"\x02", PROOF_OF_QUOTA_SIZE)
            r3 = pseudo_random(b"BlendInitialization", shared_key + b"\x03", SIGNATURE_SIZE)
            r4 = pseudo_random(b"BlendInitialization", shared_key + b"\x04", PROOF_OF_SELECTION_SIZE)
            is_last = False
            pseudo_random_blending_headers.append(r1 + r2 + r3 + r4 + is_last)

        # Replace the last `len(shared_keys)` blending headers.
        private_header[-num_layers:] = pseudo_random_blending_headers
        return private_header
    ```

4. Encrypt the last $`h`$ blend headers in a reconstructable manner:

    For $`i=\{ 1,...,h \}`$, for $`j=\{1, ..., i \}`$, encrypt blend header $`\mathbf{b}_{\beta_{max}-i+1}=E_{H_{\mathbf{b}}(\kappa^{n,l_j}_{j})}(\mathbf{b}_{\beta_{max}-i+1})`$.

    ```python
    def encrypt_last_blending_headers(private_header: PrivateHeader, shared_keys: List[SharedKeys]) -> PrivateHeader:
        assert len(private_header) == ENCAPSULATION_COUNT
        assert len(shared_keys) <= ENCAPSULATION_COUNT

        for i, _ in enumerate(shared_keys):
            index = len(private_header) - i - 1
            for shared_key in shared_keys[:i + 1]:
                private_header[index] = encrypt(private_header[index], shared_key)

        return private_header
    ```

    This prevents leakage of the encryption sequence when a message is encapsulated less than $`\beta_{max}`$ times, and enables us to encode the header in a way that it can be reconstructed during the decapsulation.

## **Message Encapsulation**

The final part of the algorithm is the true encapsulation of the payload. That is, given the payload $`\mathbf P_0`$ and number of encapsulations $`h \le \beta_{max}`$ we do the following.

For $`i \in \{ 1,…,h \}`$ do the following:

1. If $`i=1`$ then generate a new ephemeral key pair:

    $`(K^n_0, k^n_0) \notin \mathbf K^n_h`$.

2. Calculate the signature of the concatenation of the *current* header and payload:

    $`\sigma_{K^{n}_{i-1}}(\mathbf h_{i-1}| \mathbf P_{i-1})`$.

3. Using the shared key $`\kappa^{n,l_i}_i`$, encrypt the payload:

    $`\mathbf{P}_i = E_{H_\mathbf{P}( \kappa^{n,l_i}_i)}(\mathbf P_{i-1})=\mathbf{P}_{i-1} \oplus \text {CSPRBG}(H_\mathbf{P}(\kappa^{n,l_i}_i))`$
    
    Note that the uniqueness of the key stream is preserved as the encryption is done on a domain separated checksum of the shared key, which renders a different key stream than the encryption of the header.

4. Shift blending headers by one downward:

    $`\mathbf b_z \rightarrow \mathbf b_{z+1}`$ for $`z \in \{ 1,…,\beta_{max} \}`$.
    
    The first blending header is now empty, and the last blending header is truncated.

5. Fill the blending header $`\mathbf b_1`$, where $`1`$ refers to the top position:
    1. If $`i=1`$ then:
        1. Fill the proof of quota with random data:
        
            $`\pi^{K^{n}_0}_{Q}= \text {CSPRBG}(H_\mathbf{I}(k^{n}_0))_{|\pi^{K}_{Q}|}`$
        
        2. Set the last flag to 1:
        
            $`\Omega=1`$

    2. Else set the last flag to 0:
    
        $`\Omega = 0`$
    
    3. $`\mathbf{b}_1 = \{ K^n_{i-1}, \pi^{K^{n}_{i-1}}_{Q}, \sigma_{K^{n}_{i-1}}(\mathbf h_{i-1}|\mathbf P_{i-1}), \pi^{K^{n}_i,l_i}_{S}, \Omega \}`$.

6. Using shared key $`\kappa^{n,l_i}_i`$, encrypt the private header $`\mathbf{h}_{E_{i}} = E_{H_{\mathbf b}(\kappa^{n,l_i}_i)}(\mathbf{h}_i)`$:

    For each $`\mathbf b_j \in \mathbf h_i = (\mathbf b_1,...,\mathbf b_{m_{max}})`$ using a shared key $`\kappa^{n,l_i}_i`$, encrypt the blending header:
    
    $`\mathbf{b}_j = E_{H_\mathbf{b}(\kappa^{n,l_i}_i)}(\mathbf{b}_j)=\mathbf{b}_j \oplus \text {CSPRBG}(H_\mathbf{b}(\kappa^{n,l_i}_i))`$.

Fill in the public header: $`\mathbf H=\{ K^{n}_h, \pi^{K^{n}_h}_{Q}, \sigma_{K^{n}_h}(\mathbf P_h) \}`$.

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
    for shared_key, keypair, proof_of_selection) in zip(shared_keys, key_collection, list_of_pos):
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

## Message Decapsulation

If a message $`\mathbf M`$ is received by the node and its public header is correct - that is, it was verified according to the relay logic defined here: [Relaying](blend-protocol.md#relaying) - then the node $`l`$ executes the following logic:

1. Calculate the shared secret. Using the key $`K^{n}_l \in \mathbf H`$ from the public header of the message $`\mathbf M`$ and the private key $`p^l`$ of the node $`l`$ calculate:

    $`\kappa^{n,l}_l = K^{n}_l \cdot p^l`$.

2. Decrypt the private header using the shared key $`\kappa^{n,l}_l`$.


    For each $`\mathbf b_j \in \mathbf h = (\mathbf b_1,...,\mathbf b_{\beta_{max}})`$ using a shared key $`\kappa^{n,l}_l`$ decrypt the blending header:
    
    $`\mathbf{b}_j = D_{H_\mathbf{b}(\kappa^{n,l}_l)}(\mathbf{b}_j)=\mathbf{b}_j \oplus \text {CSPRBG}(H_\mathbf{b}(\kappa^{n,l}_l))`$.

3. Verify the header:
    1. If the proof $`\pi^{K^{n}_l,l}_{S}\in \mathbf b_1`$ is not correct, discard the message. That is, if the node index $`l`$ does not correspond to the $`K^{n}_l\in \mathbf H`$, then the message must be rejected.
    2. If the key $`K^{n}_l \in \mathbf b_1`$ was already seen, discard the message.
    3. If the proof $`\pi^{K^{n}_l,l}_{Q} \in \mathbf b_1`$ is incorrect, discard the message.
    4. If $`\Omega \in \mathbf b_1`$ equals $`1`$, then stop processing the message and process the payload.

4. Using the blending header $`\mathbf b_1`$, set the public header:

    $`\mathbf H_l = \{K^{n}_l \in \mathbf b_1,\pi^{K^{n}_l,l}_{Q} \in \mathbf b_1 ,\sigma_{K^{n}_l}(\mathbf {h|P}) \in \mathbf b_1\}`$.

5. Decrypt the payload, using the shared key $`\kappa^{n,l}_l`$:

    $`\mathbf{P}_l =D_{H_\mathbf{P}(\kappa^{n,l}_l)}=\mathbf{P} \oplus \text {CSPRBG}(H_{\mathbf P}(\kappa^{n,l}_l))`$.

6. Reconstruct the blend header:
    1. $`r_{l,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|1))_{|K|}`$
    2. $`r_{l,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|2))_{|\pi^{K}_{Q}|}`$
    3. $`r_{l,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|3))_{|\sigma_{K}(\mathbf P)|}`$
    4. $`r_{l,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|4))_{|\pi^{K,k}_{S}|}`$
    5. $`\Omega=0`$
    6. $`b = \{ r_{l,1}, r_{l,2}, r_{l,3}, r_{l,4}, \Omega \}`$.

7. Encrypt the blending header:

    $`\hat b = E_{H_\mathbf{b}(\kappa^{n,{l}}_{l})}(b)`$

8. Shift blending headers by one upward:

    $`\mathbf b_z \rightarrow \mathbf b_{z-1}`$ for $`z \in \{ 1,…,\beta_{max} \}`$. The first blending header is truncated, and the last blending header is empty.

9. Reconstruct the private header:

    $`\mathbf h_{E_{l}} = \{`$ $`…`$ $`\mathbf{b}_{\beta_{max}} = \hat b`$, $`\}`$.

10. If the signature from the public header does not match the signature of the reconstructed header and the decrypted payload, discard the message:

    $`\text{verify\_sig}(\sigma_{K^n_l}(\mathbf{h}_{E_l}| \mathbf{P}_l), \mathbf{h}| \mathbf{P},{K^n_l})`$.

11. The message is decapsulated.

12. Follow the message processing logic: [Processing](blend-protocol.md#processing).

```python
def decapsulate(
    message: bytes,
    signing_private_key: Ed25519PrivateKey
) -> bytes:
    # Step 1: Derive the shared key.
    encryption_private_key = signing_private_key.derive_x25519()
    public_header = PublicHeader.from_bytes(
        message[0 : PublicHeader.SIZE]
    )
    shared_key = diffie_hellman(
        encryption_private_key,
        public_header.signing_public_key.derive_x25519()
    )

    # Step 2: Decrypt the private header
    private_header = message[
        PublicHeader.SIZE:
        PublicHeader.SIZE + (BlendingHeader.SIZE * ENCAPSULATION_COUNT)
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
    )

    # Step 5: Decrypt the payload
    payload_offset = (
        PublicHeader.SIZE + (BlendingHeader.SIZE * ENCAPSULATION_COUNT)
    )
    payload = message[payload_offset:]
    payload = decrypt(payload, shared_key)

    # Step 6: Reconstruct the new blending header
    r1 = pseudo_random(b"BlendInitialization", shared_key + b"\x01", KEY_SIZE)
    r2 = pseudo_random(b"BlendInitialization", shared_key + b"\x02", PROOF_OF_QUOTA_SIZE)
    r3 = pseudo_random(b"BlendInitialization", shared_key + b"\x03", SIGNATURE_SIZE)
    r4 = pseudo_random(b"BlendInitialization", shared_key + b"\x04", PROOF_OF_SELECTION_SIZE)
    is_last = False

    # Step 7: Encrypt the new blending header
    encrypted_new_blending_header = encrypt(r1 + r2 + r3 + r4 + is_last, shared_key)

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

    return public_header.bytes() + b"".join(private_header) + payload
```

# Appendix

## **Example**

Let us look at an example of the above mechanism. Let us assume that $`\beta_{max}=4,h=3`$.

### **Initialization**

1. Create an empty message:

    $`\mathbf{M} = (\mathbf{H}=0,\mathbf{h}=0,\mathbf{P}=0)`$

2. Randomize the private header: 

    $`\mathbf h_0 = \{`$
    
    $`\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

    $`\mathbf b_2 = \text {CSPRBG}( \rho_{2})_{|\mathbf b|}`$,

    $`\mathbf b_3 = \text {CSPRBG}( \rho_{3})_{|\mathbf b|}`$,

    $`\mathbf b_4 = \text {CSPRBG}( \rho_{4})_{|\mathbf b|}`$,

    $`\}`$.

3. Fill the last $`h`$ blend headers with reconstructable payloads:

      $`\mathbf h_0 = \{`$
      
      $`\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

      $`\mathbf b_2 = \{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \}`$,

      $`\mathbf b_3 = \{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \}`$,

      $`\mathbf b_4 = \{ r_{l_1,1}, r_{l_1,2} ,r_{l_1,3}, r_{l_1,4}, \Omega \}`$,

      $`\}`$.

4. Encrypt the last $`h`$ blend headers in a reconstructable manner:

    $`\mathbf h_{E_0} = \{`$

    $`\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

    $`\mathbf b_2 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

    $`\mathbf b_3 = E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

    $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_1,1}, r_{l_1,2} ,r_{l_1,3}, r_{l_1,4}, \Omega \})`$,

    $`\}`$.

### **Encapsulation**

$`i=1`$:

  1. Generate a new ephemeral key pair:
      
      $`(K^n_0, k^n_0) \notin \mathbf K^n`$.
  
  2. Calculate the signature of the header and the payload:
  
      $`\sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0)`$.
  
  3. Using shared key $`\kappa^{n,l_1}_{1}`$ encrypt the payload:
      $`\mathbf P_1 = E_{H_\mathbf{P}(\kappa^{n,l_1}_{1})}(\mathbf P_0)`$.
  
  4. Shift blending headers by one down:
  
      $`\mathbf h_1 = \{`$

      $`\mathbf b_1 = \emptyset`$,

      $`\mathbf b_2 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

      $`\mathbf b_3 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \}`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{1})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

      $`\}`$.

  5. Fill the first blending header (the $`\Omega=1`$ in this case):
  
      $`\mathbf h_1 = \{`$

      $`\mathbf b_1 = \{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega=1 \}`$,

      $`\mathbf b_2 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

      $`\mathbf b_3 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

      $`\}`$.

  6. Using shared key $`\kappa^{n,l_1}_{1}`$ encrypt the private header:
  
      $`\mathbf{h}_{E_{1}} = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\mathbf{h}_1) = \{`$

      $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_3 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

      $`\}`$.

$`i=2`$:

  1. $`i \ne 1`$.
  
  2. Calculate the signature of the header and the payload:
  
      $`\sigma_{K^{n}_1}(\mathbf{h}_{E_1}| \mathbf{P}_1)`$.
  
  3. Using shared key $`\kappa^{n,l_2}_{2}`$ encrypt the payload:
  
      $`\mathbf P_2 = E_{H_\mathbf{P}(\kappa^{n,l_2}_{2})}(\mathbf P_1)`$.
  
  4. Shift blending headers by one down:
  
      $`\mathbf h_2 = \{`$

      $`\mathbf b_1 = \emptyset`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S} , \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\}`$.

  5. Fill the first blending header:
  
      $`\mathbf h_2 = \{`$
      
      $`\mathbf b_1 = \{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S}, \Omega \}`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\}`$.

  6. Using shared key $`\kappa^{n,l_2}_2`$ encrypt the private header:
  
      $`\mathbf{h}_{E_2} = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\mathbf{h}_2) = \{`$
      
      $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S} , \Omega \})`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_4 = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\}`$.

$`i=3`$:

  1. $`i \ne 1`$.

  2. Calculate the signature of the header and the payload:

      $`\sigma_{K^{n}_2}(\mathbf{h}_{E_2}| \mathbf{P}_2)`$.
  
  3. Using shared key $`\kappa^{n,l_3}_{3}`$ encrypt the payload:
  
      $`\mathbf P_3 = E_{H_\mathbf{P}(\kappa^{n,l_3}_{3})}(\mathbf P_2)`$.
  
  4. Shift blending headers by one down:
  
      $`\mathbf h_3 = \{`$

      $`\mathbf b_1 = \emptyset`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S} , \Omega \})`$,

      $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\}`$.

  5. Fill the first blending header:
      
      $`\mathbf h_3 = \{`$
      
      $`\mathbf b_1 = \{K^{n}_2,\pi_Q^{K^{n}_2},\sigma_{K^n_2}(\mathbf{h}_{E_2}| \mathbf{P}_2),\pi^{K^{n}_3,l_3}_{S}, \Omega \}`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S} , \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S} , \Omega \})`$,

      $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\}`$.

  6. Using shared key $`\kappa^{n,l_3}_3`$ encrypt the private header: 
  
      $`\mathbf{h}_{E_3} = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}(\mathbf{h}_3) = \{`$
      
      $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}(\{K^{n}_2,\pi_Q^{K^{n}_2},\sigma_{K^n_2}(\mathbf{h}_{E_2}| \mathbf{P}_2),\pi^{K^{n}_3,l_3}_{S}, \Omega \})`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\}`$.

The above calculations give us the final message $`\mathbf {M = (H,h,P)}`$ where:

$`\mathbf H = (K^{n}_3,~ \pi^{K^{n}_3}_Q,~ \sigma_{K^{n}_3}(\mathbf{h}_{E_3}|\mathbf{P}_3))`$,

$`\mathbf{h} = \mathbf{h}_{E_3} = \{`$

  $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}(\{K^{n}_2,\pi_Q^{K^{n}_2},\sigma_{K^n_2}(\mathbf{h}_{E_2}| \mathbf{P}_2),\pi^{K^{n}_3,l_3}_{S}, \Omega \})`$,

  $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S} , \Omega \})`$,

  $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathcal{P}), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

  $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_3}_3)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

$`\}`$,

$`\mathbf{P} = \mathbf P_3= E_{H_{\mathbf P_0}(\kappa^{n,l_3}_3)}E_{H_{\mathbf P}(\kappa^{n,l_2}_2)}E_{H_{\mathbf P}(\kappa^{n,l_1}_1)}(\mathbf{P}_0)`$.

### Decapsulation

Now let us take the above message and decapsulate it. We verify that the node doing the processing is the rightful recipient of the message and that the public header is correct.

$`l=l_3`$:

  1. Calculate shared secret:
  
      $`\kappa^{n,l_3}_{3}=K^n_{3} \cdot p^{l_3}`$, where $`K^{n}_{3} \in \mathbf H`$ and $`p^{l_3}`$ is the private part of the public key of the node $`l_3`$.
  2. Decrypt the header: 
  
      $`\mathbf h_{l_3} = D_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\mathbf{h}) = \{`$
      
      $`\mathbf b_1 = \{K^{n}_2,\pi_Q^{K^{n}_2},\sigma_{K^n_2}(\mathbf{h}_{E_2}| \mathbf{P}_2),\pi^{K^{n}_3,l_3}_{S}, \Omega \}`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_{E_1}| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\}.`$

  3. Verify the header:
      1. If the proof of selection $`\pi^{K^{n}_3,l_3}_{S} \in \mathbf{b}_1`$ fails then stop.
      2. If the key $`K^{n}_2 \in \mathbf b_1`$ was already seen, discard the message.
      3. If the proof $`\pi^{K^{n}_2,l_2}_{Q} \in \mathbf b_1`$ is incorrect, discard the message.

  4. Reconstruct the public header:

      $`\mathbf H = (K^{n}_2,~ \pi^{K^{n}_2}_Q,~ \sigma_{K^{n}_2}(\mathbf{h}_{E_2}|\mathbf{P}_2))`$

  5. Decrypt the payload:
  
      $`\mathbf{P}_{l_3} = D_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\mathbf P)`$.
  
  6. Reconstruct the blend header:
  
      $`b = \{`$

      $`r_{l_3,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|1))_{|K|}`$,

      $`r_{l_3,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|2))_{|\pi^{K}_{Q}|}`$,

      $`r_{l_3,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|3))_{|\sigma_{K}(\mathbf P)|}`$,

      $`r_{l_3,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|4))_{|\pi^{K,k}_{S}|}`$,

      $`\Omega = 0`$,

      $`\}.`$

  7. Encrypt the blend header:
  
      $`\hat b = E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(b)`$.
  
  8. Shift blending headers by one upward, the first blending header is discarded:
  
      $`\mathbf b_i \rightarrow \mathbf b_{i-1}`$.
  
  9. Reconstruct the private header:
  
      $`\mathbf h_{E_{l_3}} = \{`$

      $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}(\{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_1| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S} , \Omega \})`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_4 = \hat b=E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\}.`$

  10. If the signature from the public header does not match the signature of the reconstructed header and the decrypted payload then discard the message:
  
      $`\sigma_{K^n_2}(\mathbf{h}_{E_2}| \mathbf{P}_2) == \sigma_{K^n_2}(\mathbf{h}_{E_{l_3}}| \mathbf{P}_{l_3})`$ $`\text{verify\_sig}(\sigma_{K^{n}_2}(\mathbf{h}_{E_2}|\mathbf{P}_2), \mathbf{h}_{E_{l_3}}| \mathbf{P}_{l_3},{K^n_2})`$
  
  11. The message is decapsulated.
  
  12. Follow the processing logic: [Processing](blend-protocol.md#processing).

$`l=l_2`$:

  1. Calculate shared secret:
  
      $`\kappa^{n,l_2}_{2}=K^n_{2} \cdot p^{l_2}`$, where $`K^{n}_{2} \in \mathbf H`$ and $`p^{l_2}`$ is the private part of the public key of the node $`l_2`$.

  2. Decrypt the header:

      $`\mathbf h_{l_2} = D_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\mathbf{h}_{E_{l_3}}) = \{`$

      $`\mathbf b_1 = \{K^{n}_1,\pi_Q^{K^{n}_1},\sigma_{K^n_1}(\mathbf{h}_1| \mathbf{P}_1),\pi^{K^{n}_2,l_2}_{S}, \Omega \}`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_3 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_4 = E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\}.`$

  3. Verify the header:
      1. If the proof of selection $`\pi^{K^{n}_2,l_2}_{S} \in \mathbf{b}_1`$ fails then stop.
      2. If the key $`K^{n}_1 \in \mathbf b_1`$ was already seen, discard the message.
      3. If the proof $`\pi^{K^{n}_1,l_1}_{Q} \in \mathbf b_1`$ is incorrect, discard the message.

  4. Reconstruct the public header:

      $`\mathbf H = (K^{n}_1,~ \pi^{K^{n}_1}_Q,~ \sigma_{K^{n}_1}(\mathbf{h}_{E_1}|\mathbf{P}_1))`$

  5. Decrypt the payload:
  
      $`\mathbf{P}_x = D_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\mathbf P)`$.
  
  6. Reconstruct the blend header:
  
      $`b = \{`$

      $`r_{l_2,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|1))_{|K|}`$,

      $`r_{l_2,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|2))_{|\pi^{K}_{Q}|}`$,

      $`r_{l_2,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|3))_{|\sigma_{K}(\mathbf P)|}`$,

      $`r_{l_2,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|4))_{|\pi^{K,k}_{S}|}`$,

      $`\Omega=0`$,

      $`\}.`$

  7. Encrypt the reconstructed blend header:

      $`\hat b = E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(b)`$.
  
  8. Shift blending headers by one upward, the first blending header is discarded:
  
      $`\mathbf b_i \rightarrow \mathbf b_{i-1}`$.
  
  9. Reconstruct the private header:
  
      $`\mathbf h_{E_{l_2}} = \{`$

      $`\mathbf b_1 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ K^n_0, \pi^{K^{n}_{0}}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \})`$,

      $`\mathbf b_2 = E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\text {CSPRBG}( \rho_{1})_{|\mathbf b|})`$,

      $`\mathbf b_3=E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega\})`$,

      $`\mathbf b_4 = \hat b=E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

      $`\}.`$

  10. Check the signature:
  
      $`\sigma_{K^n_2}(\mathbf{h}_{E_1}| \mathbf{P}_1) == \sigma_{K^n_2}(\mathbf{h}_{E_{l_2}}| \mathbf{P}_{l_2})`$ $`\text{verify\_sig}(\sigma_{K^{n}_1}(\mathbf{h}_{E_1}|\mathbf{P}_1), \mathbf{h}_{E_{l_2}}| \mathbf{P}_{{l_2}},{K^n_1})`$
  11. The message is decapsulated.
  12. Follow the message processing logic: [Processing](blend-protocol.md#processing).

$`l=l_1`$:

  1. Calculate shared secret:
  
      $`\kappa^{n,l_1}_{1}=K^n_{1} \cdot k^{l_1}`$, where $`K^{n}_{l_1} \in \mathbf H`$ and $`p^{l_1}`$ is the private part of the public key of the node $`l_1`$.

  2. Decrypt the private header:

      $`\mathbf h_{l_1} = D_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(\mathbf{h}_{E_{l_2}}) = \{`$

      $`\mathbf b_1 = \{ K^n_0, \pi^{K^{n}_{0},l_0}_{Q}, \sigma_{K^{n}_0}(\mathbf{h}_{E_0}| \mathbf{P}_0), \pi^{K^{n}_1,l_1}_{S}, \Omega \}`$,

      $`\mathbf b_2 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

      $`\mathbf b_3=E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4}, \Omega \})`$,

      $`\mathbf b_4 =E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4}, \Omega \})`$,

      $`\}.`$

  3. Verify the header:
      1. If the proof of selection $`\pi^{K^{n}_1,l_1}_{S} \in \mathbf{b}_1`$ fails then stop.
      2. If the key $`K^{n}_0 \in \mathbf b_1`$ was already seen, discard the message.
      3. If the proof $`\pi^{K^{n}_0,l_0}_{Q} \in \mathbf b_1`$ is incorrect, discard the message.

  4. Reconstruct the public header:

      $`\mathbf H = (K^{n}_0,~ \pi^{K^{n}_0}_Q,~ \sigma_{K^{n}_0}(\mathbf{h}_{E_0}|\mathbf{P}_0))`$

  5. Decrypt the payload:
  
      $`\mathbf{P}_{l_1} = D_{H_\mathbf{P}(\kappa^{n,{l_1}}_{1})}(\mathbf P)`$.
  
  6. Reconstruct the blend header:
  
      $`b = \{`$
      $`r_{l_1,1} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|1))_{|K|}`$,

      $`r_{l_1,2} = \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|2))_{|\pi^{K}_{Q}|}`$,

      $`r_{l_1,3}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|3))_{|\sigma_{K}(\mathbf P)|}`$,

      $`r_{l_1,4}= \text {CSPRBG}(H_\mathbf{I}(\kappa^{n,l}_l|4))_{|\pi^{K,k}_{S}|}`$,

      $`\Omega = 0`$,

      $`\}.`$

  7. Encrypt the reconstructed blend header:
  
      $`\hat b = E_{H_\mathbf{b}(\kappa^{n,{l_1}}_{1})}(b)`$.
  
  8. Shift blending headers by one upward, the first blending header is discarded: 
  
      $`\mathbf b_i \rightarrow \mathbf b_{i-1}`$.

  9. Reconstruct the private header:
  
      $`\mathbf h_{E_{l_1}} = \{`$

      $`\mathbf b_1 = \text {CSPRBG}( \rho_{1})_{|\mathbf b|}`$,

      $`\mathbf b_2=E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}E_{H_{\mathbf b}(\kappa^{n,l_2}_2)}E_{H_\mathbf{b}(\kappa^{n,{l_3}}_{l_3})}(\{ r_{l_3,1}, r_{l_3,2} ,r_{l_3,3}, r_{l_3,4},\Omega \})`$,

      $`\mathbf b_3 =E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}E_{H_\mathbf{b}(\kappa^{n,{l_2}}_{2})}(\{ r_{l_2,1}, r_{l_2,2} ,r_{l_2,3}, r_{l_2,4},\Omega \})`$,

      $`\mathbf b_4 = \hat b=E_{H_{\mathbf b}(\kappa^{n,l_1}_1)}(\{ r_{l_1,1}, r_{l_1,2} ,r_{l_1,3}, r_{l_1,4},\Omega \})`$,

      $`\}.`$

  10. If the signature from the public header does not match the signature of the reconstructed header and the decrypted payload then discard the message: $`\text{verify\_sig}(\sigma_{K^{n}_0}(\mathbf{h}_{E_0}|\mathbf{P}_0), \mathbf{h}_{E_{l_1}}| \mathbf{P}_{{l_1}},{K^n_0})`$.
  11. The message is decapsulated.
  12. Follow the message processing logic: [Processing](blend-protocol.md#processing).
