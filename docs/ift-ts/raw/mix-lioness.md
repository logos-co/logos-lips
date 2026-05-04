# LIONESS-PAYLOAD-ENCRYPTION-FOR-MIX

Field | Value
--- | ---
Name | LIONESS encryption scheme for LIBP2P-MIX payload encryption
Slug | TBD
Status | raw
Category | Standards Track
Editor | Mohammed Alghazwi <mohalghazwi@status.im>
Contributors | Balázs Kőműves <balazs@status.im>

## Abstract

This specification defines the LIONESS wide-block encryption scheme for the Sphinx payload encryption. The purpose of this is to perform layered-encryption and preserve payload integrity in the Sphinx construction used by libp2p mix while keeping the payload fixed-size. The routing header integrity mechanism defined in the Mix Protocol remains unchanged. Only the payload field $\delta$ is affected by this specification.

This specification defines:
- the LIONESS construction to use for payload encryption and decryption,
- the KDF used to derive LIONESS round keys from the per-hop shared secret,
- the required payload format and construction.
- the hop payload processing and integrity verification.

## 1. Introduction

The libp2p Mix Protocol uses a Sphinx packet format with four fields ($\alpha,\ \beta,\ \gamma,\ \delta$). The header fields ($\alpha,\ \beta,\ \gamma$) provide per-hop layered-encrypted routing information which includes header integrity. The payload field $\delta$ carries only the application message in layered-encrypted form.

In the current Mix Protocol, AES-CTR is used to encrypt the routing header $\beta$. This is sufficient for $\beta$ because header integrity is separately protected by the per-hop MAC field $\gamma$. However, the integrity of $\delta$ is not covered by $\gamma$, since the Sphinx design intentionally separates header integrity from payload integrity.

This separation is necessary because a valid Sphinx header may be paired with different payload content, and because SURB replies require the sender of the SURB to construct the return header before the reply payload is known. As a result, payload integrity MUST be provided independently of header integrity.

A malleable encryption scheme such as AES-CTR does not satisfy this requirement. Bit modifications to the ciphertext result in modifications to the decrypted plaintext. This violates the integrity of the Sphinx payload. Therefore, the payload-encryption scheme for libp2p mix MUST satisfy the following:
1. It MUST preserve the fixed payload size $|\delta|$.
2. It MUST support layered encryption and per-hop layer removal.
3. It MUST be compatible with SURBs and therefore MUST NOT require payload-dependent header authentication.
4. It MUST allow the final hop to detect payload tampering.
5. It MUST avoid adding external authentication material/tags that change the packet or payload size.

To achieve this, this specification introduces LIONESS, a wide-block cipher built from a stream cipher and a keyed hash function. LIONESS acts as a pseudo-random permutation (PRP) over the entire payload block, allowing us to add an integrity prefix (e.g. leading zeros) into the plaintext and verify it after decryption.

## 2. Terminology
The following terms are used throughout this specification:

- **Mix Protocol**: The libp2p-mix protocol defined in [the Mix specification](./mix.md).
- **Sphinx packet**: The packet format used by the Mix Protocol, consisting of ($\alpha,\ \beta,\ \gamma,\ \delta$).
- **Payload**: The fixed-size encrypted field $\delta$ in a Sphinx packet.
- **Payload integrity prefix**: A fixed all-zero prefix added to the plaintext payload before layered encryption and checked after final decryption.
- **Wide-block cipher**: A cipher that operates on the whole payload block as one unit rather than as independent small blocks.
- **Payload encryption key ($\mathbf{\delta_{key}}$)**: A key derived from the per-hop shared secret. It is used to derive the four LIONESS internal round keys.
- **Round keys**: The four keys $(K_1, K_2, K_3, K_4)$ used by the LIONESS Feistel network.

## 3. Cryptographic Primitives

This section defines the primitives used by this specification. In this specification, we will assume the following constants:
- The security parameter $\kappa = 16$ bytes ($128$-bits)
- The key size $k = 32$ bytes.

### 3.1 Stream Cipher

The stream cipher $\mathsf{S}$ used in LIONESS. We denote this as:
$$
\mathsf{S}(k, \mathsf{iv}, n) \to \mathsf{ks}
$$

where:
- $k$ is a 32 byte key
- $\mathsf{iv}$ is IV/nonce with size that depends on the chosen stream cipher. 
- $n$ is the required keystream length
- $\mathsf{ks}$ is the output arbitrary-length keystream.

Encryption and decryption can then be done by first generating a key stream $\mathsf{ks}$ and then XORing the key stream with the message/ciphertext. Encryption and decryption work in the same way: 

$$
\begin{aligned}
c &= m \oplus \mathsf{ks} \\
m &= c \oplus \mathsf{ks}
\end{aligned}
$$

where $m$ is the plaintext and $c$ is the ciphertext.
- $m$ is the arbitrary-length message
- $c$ is the arbitrary-length ciphertext of the same size as $m$, i.e., $|m| = |c|$
### 3.2 Keyed Hash Function

In this specification, the keyed hash function used in LIONESS will be denoted as $\mathsf{H}_k$, 
That is:
$$
\mathsf{H}_k(m) \to h
$$

where:
- $k$ is a 32-byte key
- $m$ is an arbitrary-length input message.
- $h$ is the 32-byte digest output

### 3.3 Key Derivation Function (KDF)
The key derivation function $\mathsf{KDF}$ is used to derive the internal LIONESS round keys from:
- $\mathsf{dom}$: a domain-separation string
- $\mathsf{seed}$: a 32-byte seed 
- $\mathsf{len}$: a required output length  in bytes

the KDF outputs key material $u$ such that $|u| = \mathsf{len}$:
$$
\mathsf{KDF}(\mathsf{dom}, \mathsf{seed}, \mathsf{len}) \to u
$$

LIONESS requires the output key material from the KDF to be of size $|u| = 4\times k$ bytes. In this specification, we have $k = 32$ bytes, resulting in $|u| = 128$ bytes.

## 4. LIONESS Construction

### 4.1 High-level API
In general the LIONESS wide-block cipher provides the following:

$$
\begin{array}{l}
\mathsf{Lioness.Enc}(k,x) \to y \\
\mathsf{Lioness.Dec}(k,y) \to x 
\end{array}
$$
where:
- $k$ is the seed/master key from which the internal round keys are derived, with size $|k| = 32$ bytes
- $x$ is the plaintext message with size $|x| \ge 2 |k|$ bytes.
- $y$ is the corresponding ciphertext with size $|y| = |x|$

### 4.2 Block Structure
LIONESS is a wide-block cipher, meaning that it can take a large plaintext message and process it as a single large block by applying a small Feistel network over it. Instead of splitting the plaintexts into small blocks and processing these, LIONESS splits the input message block $b$ into two chunks: 
$$
B = L \parallel R 
$$
where:
- $B$ is the plaintext message block of any size $|B| \ge 2 |k|$
- $L$ is the left chunk with size $|L| = |k|$ bytes
- $R$ is the right chunk with size $|R| = |m| - |k|$ bytes. 

LIONESS scheme requires the size of the message to be at least $|k| + \kappa$, i.e., $|B| \ge |k| + \kappa$ where $\kappa$ is the security parameter.  For simplicity, in this specification, we require the payload size to be strictly greater than 64 bytes (i.e., $\ge 2 |k|$). The Mix protocol payload size satisfies this requirement since the expected payload is much larger than 64 bytes.

In summary, we set $|k| = 32$ bytes. Therefore:
- $|B| \ge 64$ bytes
- $|L| = |k| = 32$ bytes,
- $|R|$ is the remaining $|B| - |L|$ bytes.

The choice $|k| = 32$ bytes must match:
- the stream cipher ($\mathsf{S}$) key size, and
- the keyed hash ($H_k$) key size and digest ($h$) size.

As a result, we can observe that for large messages, the right chunk is expected to be much larger than the left chunk.

```
+----------------+----------------------------------+
|       L        |          R                       |
|   |k| bytes    |    (|B| - |k|) bytes             |
+----------------+----------------------------------+
```

### 4.3 Key Derivation
LIONESS requires 4 internal round keys, one for each round: $(K_1, K_2, K_3, K_4)$:

- $K_1$ and $K_3$ are the keys used for the stream cipher.
- $K_2$ and $K_4$ are the keys used for the keyed hash function.

All internal round keys are $|k| = 32$ bytes in size. Therefore, the required output key material from the $\mathsf{KDF}$ is 128 bytes. 

We expect the seed/master key ($\delta_{key}$) to be of size 32 bytes. This $\delta_{key}$ is derived from the shared key $s_i$ as defined in the [mix specification](./mix.md). Therefore, we use this $\delta_{key}$ to derive all the LIONESS round keys to encrypt the payload. For this we use the KDF as defined in section 3.3:

$$
(K_1 \parallel K_2 \parallel K_3 \parallel K_4) = \mathsf{KDF}(\texttt{"lioness-payload-key"}, \delta_{key}, 128)
$$

### 4.4 Encryption

Let:
- plaintext message $B = L_0 \parallel R_0$
- round keys $(K_1, K_2, K_3, K_4)$ 
- $S$ is the stream cipher as defined in section 3.1
- $H$ is the keyed hash function as defined in section 3.2 
- $\mathsf{iv}$ is the initialization vector or nonce for the stream cipher. The choice of $\mathsf{iv}$  and its size depend on the chosen stream cipher and therefore depend on how LIONESS is instantiated.

LIONESS encryption proceeds with applying a small Feistel network of four rounds:

$$
\begin{aligned}
B &= L_0 \parallel R_0 \\
R_1 &= R_0 \oplus S(K_1 \oplus L_0, \mathsf{iv}, |R_0|) \\
L_1 &= L_0 \oplus H_{K_2}(R_1) \\
R_2 &= R_1 \oplus S(K_3 \oplus L_1, \mathsf{iv}, |R_1|) \\
L_2 &= L_1 \oplus H_{K_4}(R_2) \\
C   &= L_2 \parallel R_2
\end{aligned}
$$

```                                                   
round 1:  R1 = R0 ^ S(L0 ^ K1, iv, |R_0|)                        
                                                      
+-----------+                           +-----------+ 
|    L0     |                           |    R0     | 
+-----------+                           +-----------+ 
      |                 K1                    |       
      |                 │                     | xor   
      |                 │                     v       
      |                 v              +-------------+
      +----------------xor------------>|      S      |
                                       +-------------+
                                              |       
                                              v       
+-----------+                           +-----------+ 
|    L0     |                           |    R1     | 
+-----------+                           +-----------+ 
                                                      
                                                      
round 2:  L1 = L0 ^ H_K2(R1)                          
                                                      
+-----------+                           +-----------+ 
|    L0     |                           |    R1     | 
+-----------+                           +-----------+ 
      |                                       |       
      | xor                                   |       
      v                                       |       
+-------------+<------------------------------+       
|      H      |<----- K2                              
+-------------+                                       
      |                                               
      v                                               
+-----------+                           +-----------+ 
|    L1     |                           |    R1     | 
+-----------+                           +-----------+ 
                                                      
                                                      
round 3:  R2 = R1 ^ S(L1 ^ K3, iv, |R_1|)                        
                                                      
+-----------+                           +-----------+ 
|    L1     |                           |    R1     | 
+-----------+                           +-----------+ 
      |                K3                     |       
      |                │                      | xor   
      |                │                      v       
      |                v               +-------------+
      +---------------xor------------->|      S      |
                                       +-------------+
                                              |       
                                              v       
+-----------+                           +-----------+ 
|    L1     |                           |    R2     | 
+-----------+                           +-----------+ 
                                                      
                                                      
round 4:  L2 = L1 ^ H_K4(R2)                          
                                                      
+-----------+                           +-----------+ 
|    L1     |                           |    R2     | 
+-----------+                           +-----------+ 
      |                                       |       
      | xor                                   |       
      v                                       |       
+-------------+<------------------------------+       
|      H      |<----- K4                              
+-------------+                                       
      |                                               
      v                                               
+-----------+                           +-----------+ 
|    L2     |                           |    R2     | 
+-----------+                           +-----------+ 
```                                                   

### 4.5 Decryption

LIONESS decryption is the inverse of the four internal rounds defined in the previous section:

$$
\begin{aligned}
C &= L_2 \parallel R_2 \\
L_1 &= L_2 \oplus H_{K_4}(R_2) \\
R_1 &= R_2 \oplus S(K_3 \oplus L_1, \mathsf{iv}, |R_2|) \\
L_0 &= L_1 \oplus H_{K_2}(R_1) \\
R_0 &= R_1 \oplus S(K_1 \oplus L_0, \mathsf{iv}, |R_1|) \\
B &= L_0 \parallel R_0
\end{aligned}
$$

## 5. Payload Construction
This section specifies how the Sphinx payload is constructed using the LIONESS wide-block encryption. Some parts of this section restates the mix specification for clarity. For full specification of how the Sphinx packet is constructed, refer to the [mix specification](./mix.md).

### 5.1 Payload Plaintext Format

Before layered encryption, the sender MUST construct the payload plaintext as the following concatenation:

$$
B = z \parallel m
$$

where:
- $z$ is an all-zero integrity prefix of the same length as the security parameter $\kappa$, which equals to 16 bytes (128 bits).
- $m$ is the application message padded to fill the remaining payload space.

Thus:
- $|z| = \kappa$ bytes
- $|B| = |\delta|$
- $|m| = |B| - |z|$

The size of the payload $|\delta|$ is specified in the Mix protocol, and if the application message $|p|$ is small payload padding is added as specified in the [Mix Protocol](./mix.md).

### 5.2 Sphinx Payload Construction

#### Forward Payload
Once the plaintext is formatted as specified above, it needs to be encrypted in layers such that each hop in the mix path removes exactly one layer using the per-hop session key. This ensures that only the final hop (i.e., the exit node) can fully recover the plaintext message $m$, validate its integrity, and forward it to the destination. To compute the encrypted payload, perform the following steps for each hop $i = L-1$ down to $0$, recursively:

- Derive the payload key $\delta_{\mathrm{key}_i} = \mathsf{KDF}(\texttt{"delta_key"}, s_i, 32)$ where $s_i$ is the per-hop shared secret for hop `i` as defined in the Mix protocol specification.
- Using $\delta_{\mathrm{key}_i}$, compute the encrypted payload $\delta_i$:
     - If $i = L-1$ (_i.e.,_ exit node):
       $$
       \delta_i = \mathsf{Lioness.Enc}\bigl(\delta_{\mathrm{key}_i}, B
       \bigr)
       $$
     - Otherwise (_i.e.,_ intermediary node):
       $$
       \delta_i = \mathsf{Lioness.Enc}\bigl(\delta_{\mathrm{key}_i},
       δ_{i+1} \bigr)
       $$

The resulting $\delta$ is placed into the final Sphinx packet.

#### Reply payload (SURB payload)
For a SURB reply, the reply sender does not know the return-path shared secrets $s_0, \ldots, s_{L-1}$.
Therefore, the reply sender MUST perform the following steps:
- constructs the payload plaintext:
    $$
    B = 0_\kappa \parallel m
    $$
- Then it derives the reply payload encryption key:
    $$
    \delta_{key_{\tilde{k}}}
    = \mathsf{KDF}(\texttt{"delta_key"}, \tilde{k}, 32)
    $$
- and computes:
    $$
    \delta = \mathsf{Lioness.Enc}(\delta_{key_{\tilde{k}}}, B)
    $$

The resulting $\delta$ is placed into the SURB reply packet.
Each hop on return-path subsequently applies the normal payload-processing rule, namely one LIONESS decryption under its per-hop payload encryption key.
The SURB creator reverses these return-path transformations during reply recovery as described in the next section.

## 6. Sphinx Payload Processing

Once the Sphinx packet is deserialized into ($\alpha,\ \beta,\ \gamma,\ \delta$) and the header is preprocessed as specified in the Mix protocol, the mix node performs the following steps depends on its role (as defined in the [mix specification, Section 8.6.2 Node Role Determination](./mix)):

**Intermediary Processing**

If the node is an intermediary, it MUST:
- Derive the payload encryption key:
$$
\delta_{\mathrm{key_i}} = \mathsf{KDF}(\texttt{"delta_key"}, s, 32)
$$
- Decrypt one layer of the payload using the payload encryption key $\delta_{\mathrm{key}}$: 
    $$
    \delta' = \mathsf{Lioness.Dec}\bigl(\delta_{\mathrm{key}}, \delta
       \bigr)
    $$
- use $\delta'$ as the outgoing payload,
- forward the updated packet as defined by the Mix Protocol.

**Exit Processing - Forward packet**

If the node is the exit, and the packet is not a reply (using SURBs), it MUST:
1. Derive the payload encryption key:
$$
\delta_{\mathrm{key_i}} = \mathsf{KDF}(\texttt{"delta_key"}, s, 32)
$$
2 Decrypt one layer of the payload using the payload encryption key $\delta_{\mathrm{key}}$: 
    $$
    \delta' = \mathsf{Lioness.Dec}\bigl(\delta_{\mathrm{key}}, \delta
       \bigr)
    $$
3. parse the decrypted payload $\delta'$ as $B = z \parallel m$, where $|z| = \kappa$ bytes.
4. verify that the first $\kappa$ bytes of $B$ are all zeros.
5. discard the packet if this integrity check fails.
6. otherwise remove the $\kappa$ bytes prefix and pass $m$ to the Mix Exit Layer.

**Exit Processing - Reply packet**
If the node is the exit, and the packet is a reply, it MUST:
1. reverse the return-path transformations, i.e., since the hops apply LIONESS decryption, the exit must apply LIONESS encryption:
    For each hop `$i = L-1$` down to `$0$`:
    - Derive the payload encryption key:
    $$
    \delta_{\mathrm{key}_i}
    =\mathsf{KDF}(\texttt{"delta_key"}, s_i, 32)
    $$
    - and compute:
    $$
    \delta' \leftarrow \mathsf{Lioness.Enc}(\delta_{\mathrm{key}_i}, \delta)
    $$
2. After all return-path transformations are reversed, derive the reply payload encryption key from the reply key $\tilde{k}$:
    $$
    \delta_{Key_{\tilde{k}}} = \mathsf{KDF}(\texttt{"delta_key"}, \tilde{k}, 32)
    $$
    and decrypt the final layer (reversing the effect of the initial encryption):
    $$
    B = \mathsf{Lioness.Dec}(\delta_{Key_{\tilde{k}}}, δ)
    $$
3. parse the decrypted payload $B = z \parallel m$, where $|z| = \kappa$ bytes.
4. verify that the first $\kappa$ bytes of $B$ are all zeros.
5. discard the packet if this integrity check fails.
6. otherwise remove the $\kappa$ bytes prefix and pass $m$ to the Mix Exit Layer.

*Note: We assume here that the exit is the SURB creator, if not then the exit will forward to an exit-layer which will process the reply payload as specified above.*

## 7. Security Considerations

### 7.1 LIONESS Blocks/Messages
This specification requires the LIONESS input block to be at least 64 bytes. 

LIONESS splits the input block into two parts 
$$
B = L \parallel R
$$

where:
- $|L| = 32$ bytes,
- $|R| = |B| - 32$ bytes.

Therefore, the 64 byte minimum ensures that both $L$ and $R$ contain at least 32 bytes. The Mix Protocol payload size is expected to be much larger than this minimum, so this requirement is satisfied by normal Mix payload.

### 7.2 LIONESS Integrity

This specification does not use an explicit payload authentication tag. Instead, integrity is obtained by:
- embedding a fixed all-zero prefix into the plaintext,
- encrypting the whole payload with a pseudo-random permutation (PRP).

Because LIONESS acts as a wide-block permutation over the entire message, a modification to the ciphertext will, except with negligible probability, produce a decrypted plaintext whose first $\kappa = 16$ bytes are not all zero. Replacing LIONESS with a malleable stream construction invalidates this property.

### 7.3 Primitive Choices
The security of LIONESS depends on the security of the primitives used to instantiate it:
- the stream cipher $\mathsf{S}$,
- the keyed hash function $\mathsf{H}_k$,
- the key derivation function $\mathsf{KDF}$.

Implementations may use any compatible choices. For detailed analysis on the security of LIONESS, refer to the [paper](https://www.cl.cam.ac.uk/~rja14/Papers/bear-lion.pdf). 

## 8. Reference Implementations

- [Rust reference implementation of LIONESS](https://github.com/mghazwi/lioness_blockcipher)
- [Haskell reference implementation](https://github.com/logos-storage/transport-over-mix).

These reference implementations are generic and can support any compatible $\mathsf{S}$, $\mathsf{H}_k$, and $\mathsf{KDF}$. 

The current Mix protocol already uses primitives that can be used for LIONESS. A recommended instantiation is:
- AES-CTR as the stream cipher $\mathsf{S}$,
- HMAC-SHA-256 as the keyed hash $\mathsf{H}_k$,
- HKDF-SHA256 as the key derivation function $\mathsf{KDF}$.

## 9. Future Work

The following are under research/consideration:
- support for faster alternative wide-block ciphers such as AEZ. Research into AEZ is still in progress.

## References

- [Sphinx: A Compact and Provably Secure Mix Format](https://eprint.iacr.org/2008/475.pdf)
- [The Bear and Lion Block Cipher Design](https://www.cl.cam.ac.uk/~rja14/Papers/bear-lion.pdf)
- [libp2p Mix Protocol](./mix.md)