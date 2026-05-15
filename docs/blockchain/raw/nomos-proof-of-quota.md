# NOMOS-PROOF-OF-QUOTA

| Field | Value |
| --- | --- |
| Name | Nomos Proof of Quota Specification |
| Slug | 88 |
| Status | raw |
| Category | Standards Track |
| Editor | Mehmet Gonen <mehmet@logos.co> |
| Contributors | Marcin Pawlowski <marcin@logos.co>, Thomas Lavaur <thomaslavaur@logos.co>, Youngjoon Lee <youngjoon@logos.co>, David Rusu <davidrusu@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/nomos-proof-of-quota.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/nomos-proof-of-quota.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document defines an implementation-friendly specification
of the Proof of Quota (PoQ),
which ensures that there is a limited number of message encapsulations
that a node can perform,
thereby constraining the number of messages a node can introduce
to the Blend network used in Nomos
(see [NOMOS-BLEND-PROTOCOL](#references)).
The mechanism regulating these messages is similar to rate-limiting nullifiers.

**Keywords:** cryptography, zero-knowledge, Blend, quota, rate-limiting,
PoQ, nullifier

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

This section defines the normative cryptographic protocol requirements
for the Proof of Quota.

### Construction

The Proof of Quota (PoQ) can be satisfied by one of two proof types,
depending on the node's role in the network:

1. **Proof of Core Quota (PoQ_C)**: Ensures that the core node is declared
   and hasn't already produced more keys than the core quota Q_C.

2. **Proof of Leadership Quota (PoQ_L)**: Ensures that the leader node
   would win the proof of stake for current Cryptarchia epoch
   (see [Cryptarchia Consensus](#references))
   and hasn't already produced more keys than the leadership quota Q_L.
   This doesn't guarantee that the node is indeed winning
   because the PoQ doesn't check if the Proof of Leadership note
   (representing staked value) is unspent,
   enabling generation of the proof ahead of time preventing extreme delays.

**Validity**: The final proof PoQ is valid if either PoQ_C or PoQ_L holds.

### Zero-Knowledge Proof Statement

#### Public Values

A proof attesting that for the following public values
derived from blockchain parameters:

**Type Definition:**
`zkhash` represents a 256-bit hash value used in zero-knowledge circuits,
typically a Poseidon hash output compatible with the BN256 scalar field.

```python
class ProofOfQuotaPublic:
    session: int              # Session number (uint64)
    core_quota: int           # Allowed messages per session for core nodes (20 bits)
    leader_quota: int         # Allowed messages per session for potential leaders (20 bits)
    core_root: zkhash         # Merkle root of zk_id of the core nodes
    K_part_one: int           # First part of the signature public key (16 bytes)
    K_part_two: int           # Second part of the signature public key (16 bytes)
    pol_epoch_nonce: int      # PoL Epoch nonce
    pol_t0: int               # PoL constant t0
    pol_t1: int               # PoL constant t1
    pol_ledger_aged: zkhash   # Merkle root of the PoL eligible notes

    # Outputs:
    key_nullifier: zkhash     # Derived from session, private index and private sk
```

**Field Descriptions:**

- `session`: Unique session identifier for temporal partitioning
- `core_quota`: Maximum number of message encapsulations allowed per session
  for core nodes (20-bit value)
- `leader_quota`: Maximum number of message encapsulations allowed per session
  for potential leaders (20-bit value)
- `core_root`: Root of Merkle tree containing zk_id values
  of all declared core nodes
- `K_part_one`, `K_part_two`: Split representation of one-time signature
  public key (32 bytes total)
- `pol_epoch_nonce`: Proof of Leadership epoch nonce for lottery
- `pol_t0`, `pol_t1`: Proof of Leadership threshold constants
- `pol_ledger_aged`: Root of Merkle tree containing eligible
  Proof of Leadership notes
- `key_nullifier`: Output nullifier preventing key reuse within a session

#### Witness

The prover knows a witness:

```python
class ProofOfQuotaWitness:
    index: int                              # Index of the generated key (20 bits)
    selector: bool                          # Indicates if it's a leader (=1) or core node (=0)

    # This part is filled randomly by potential leaders
    core_sk: zkhash                         # sk corresponding to the zk_id of the core node
    core_path: list[zkhash]                 # Merkle path proving zk_id membership (len = 20)
    core_path_selectors: list[bool]         # Indicates how to read the core_path

    # This part is filled randomly by core nodes
    pol_sl: int                             # PoL slot
    pol_sk_starting_slot: int               # PoL starting slot of the slot secrets
    pol_note_value: int                     # PoL note value
    pol_note_tx_hash: zkhash                # PoL note transaction
    pol_note_output_number: int             # PoL note transaction output number
    pol_noteid_path: list[zkhash]           # PoL Merkle path proving noteID membership (len = 32)
    pol_noteid_path_selectors: list[bool]   # Indicates how to read the note_path
    pol_slot_secret: int                    # PoL slot secret corresponding to sl
    pol_slot_secret_path: list[zkhash]      # PoL slot secret Merkle path (len = 25)
```

**Witness Field Descriptions:**

- `index`: The index of the generated key.
  Limiting this index limits the maximum number of keys generated
  (20 bits enables up to 2^20 = 1,048,576 messages per node per session)
- `selector`: Boolean flag indicating node type (1 for leader, 0 for core node)
- `core_sk`: Secret key corresponding to the core node's zk_id
- `core_path`: Merkle authentication path for core node membership
- `core_path_selectors`: Navigation bits for Merkle path (left/right)
- `pol_*`: Proof of Leadership witness fields (filled randomly by core nodes)

**Note**: All inputs and outputs of zero-knowledge proofs are scalar field elements.

### Constraints

The following constraints MUST hold for a valid proof:

#### Step 1: Index Selection and Quota Limitation

The prover selects an index for the chosen key.
This index MUST be lower than the allowed quota and not already used.
This index is used to derive the key nullifier in
[Step 4: Key Nullifier Derivation](#step-4-key-nullifier-derivation).

**Purpose**: Limiting the possible values of this index limits the possible
nullifiers created,
which produces the desired effect of limiting the generation of keys
to a certain quota.

**Specification**: `index` is 20 bits,
enabling up to 2^20 messages per node per session.

#### Step 2: Core Node Verification

If the prover indicated that the node is a core node for the proof
(`selector` is 0), the proof checks that:

1. **Core Node Registration**: The core node is registered
   in the set N = SDP(session),
   where SDP is the Service Declaration Protocol
   (see [Service Declaration Protocol](#references)).
   This is proven by demonstrating knowledge of a `core_sk`
   that corresponds to a declared `zk_id`,
   which is a valid SDP registry for the current session.

   - The `zk_id` values are stored in a Merkle tree with a fixed depth of 20
   - The root is provided as a public input
   - To build the Merkle tree, `zk_id` values are ordered from smallest
     to biggest (when seen as natural numbers between 0 and p)
   - Remaining empty leaves are represented by 0 after the sorting
     (appended at the end of the vector)
   - This structure supports up to 1M validators

2. **Index Validity**: The index MUST satisfy: `index < core_quota`

#### Step 3: Leader Node Verification

If the prover indicated that the node is a potential leader node for the proof
(`selector` is 1), the proof checks that:

1. **Leadership Lottery**: The leader node possesses a note
   that would win a slot in the consensus lottery.
   Unlike leadership conditions,
   the proof of quota doesn't verify that the note is unspent.
   This enables potential provers to generate the PoQ well in advance.
   All other lottery constraints are the same as in Circuit Constraints.

2. **Index Validity**: The index MUST satisfy: `index < leader_quota`

#### Step 4: Key Nullifier Derivation

The prover derives a `key_nullifier` maintained by blend nodes
during the session for message deduplication purposes:

```python
selection_randomness = zkhash(b"SELECTION_RANDOMNESS_V1", sk, index, session)
key_nullifier = zkhash(b"KEY_NULLIFIER_V1", selection_randomness)
```

Where `sk` is:

- The `core_sk` as defined in the Mantle specification if the node is a core node
- The secret key of the PoL note if it's a leader node derived from inputs

**Rationale**: Two hashes are used because the selection randomness is used
in the Proof of Selection to prove the ownership of a valid PoQ.

#### Step 5: One-Time Signature Key Attachment

The prover attaches a one-time signature key used in the blend protocol.
This public key is split into two 16-byte parts:
`K_part_one` and `K_part_two`.

**Encoding**: When written in little-endian byte order,
the complete public key equals the concatenation `K_part_one || K_part_two`.

### Circuit Implementation

```python
# Verify selector is a boolean
# selector = 1 if it's a potential leader and 0 if it's a core node
selector * (1 - selector) == 0  # Check that selector is indeed a bit

# Verify index is lower than quota
# Equivalent to: index < leader_quota if selector == 1
#                or index < core_quota if selector == 0
index < selector * (leader_quota - core_quota) + core_quota

# Check if it's a registered core node
zk_id = zkhash(b"NOMOS_KDF", core_sk)
is_registered = merkle_verify(core_root, core_path, core_path_selectors, zk_id)

# Check if it's a potential leader
is_leader = would_win_leadership(
    pol_epoch_nonce,
    pol_t0,
    pol_t1,
    pol_ledger_aged,
    pol_sl,
    pol_sk_starting_slot,
    pol_sk_secrets_root,
    pol_note_value,
    pol_note_tx_hash,
    pol_note_output_number,
    pol_noteid_path,
    pol_noteid_path_selectors,
    pol_slot_secret,
    pol_slot_secret_path
)

# Verify that it's a core node or a leader
assert(selector * (is_leader - is_registered) + is_registered == 1)

# Get leader note secret key
pol_sk_secrets_root = get_merkle_root(pol_sk_starting_slot, sl, pol_slot_secret_path)
pol_note_sk = zkhash(b"NOMOS_POL_SK_V1", pol_sk_starting_slot, pol_sk_secrets_root)

# Derive nullifier
selection_randomness = zkhash(
    b"SELECTION_RANDOMNESS_V1",
    selector * (pol_note_sk - core_sk) + core_sk,
    index,
    session
)
key_nullifier = zkhash(b"KEY_NULLIFIER_V1", selection_randomness)
```

### Proof Compression

The proof confirming that the PoQ is correct MUST be compressed
to a size of 128 bytes.

**Uncompressed Format**: The UncompressedProof comprises 2 G1 and 1 G2
BN256 elements:

```python
class UncompressedProof:
    pi_a: G1  # BN256 element
    pi_b: G2  # BN256 element
    pi_c: G1  # BN256 element
```

**Compression Requirements**:

- Compressed size: 128 bytes
- Curve: BN256 (also known as BN254 or alt_bn128)
- Compression MUST preserve proof validity

### Proof Serialization

The ProofOfQuota structure contains `key_nullifier` and the compressed proof
transformed into bytes.

```python
class ProofOfQuota:
    key_nullifier: zkhash  # 32 bytes
    proof: bytes           # 128 bytes
```

**Serialization Format**:

1. Transform `key_nullifier` into 32 bytes
2. Compress proof to 128 bytes
3. Concatenate: `key_nullifier || proof`
4. Total size: 160 bytes

**Deserialization**:

Interpret the 160-byte sequence as:

- Bytes 0-31: `key_nullifier`
- Bytes 32-159: `proof`

### Security Considerations

#### Quota Enforcement

- Implementations MUST track `key_nullifier` values during each session
- Duplicate `key_nullifier` values MUST be rejected
- Session transitions MUST clear the nullifier set

#### Proof Verification

- All Merkle path verifications MUST be performed
- The `selector` bit MUST be verified as boolean (0 or 1)
- Index bounds MUST be strictly enforced
- Implementations MUST reject proofs where neither core nor leader conditions hold

#### Cryptographic Assumptions

- Relies on soundness of the underlying zk-SNARK system
- Assumes collision resistance of `zkhash` function
- Assumes computational Diffie-Hellman assumption on BN256 curve

#### Note Unspent Condition

- **Critical**: The PoQ does NOT verify that Proof of Leadership notes are unspent
- This allows pre-generation of proofs to avoid delays
- Implementations SHOULD implement additional checks for actual leadership

## Implementation Considerations

This section provides guidance for implementing the Proof of Quota protocol.

### Proof Generation

**Performance Characteristics**:

Implementations SHOULD consider:

- Proof generation is computationally intensive
- Pre-generation is recommended for leader nodes
- Witness preparation involves Merkle path computation

### Proof Verification Implementation

**Verification Steps**:

1. Deserialize proof into `key_nullifier` and `proof` components
2. Verify proof size (160 bytes total)
3. Check `key_nullifier` against session nullifier set
4. Verify zk-SNARK proof with public inputs
5. Add `key_nullifier` to session set if valid

### Merkle Tree Construction

#### Core Nodes Merkle Tree

**Specification**:

- Depth: 20 levels
- Leaf values: `zk_id` of declared core nodes
- Ordering: Ascending numerical order (as natural numbers 0 to p)
- Empty leaves: Represented by 0, appended after sorted values
- Capacity: 2^20 = 1,048,576 validators

**Construction Algorithm**:

```python
def build_core_tree(zk_ids: list[int]) -> MerkleTree:
    # Sort zk_ids in ascending order
    sorted_ids = sorted(zk_ids)

    # Pad to 2^20 with zeros
    padded = sorted_ids + [0] * (2**20 - len(sorted_ids))

    # Build Merkle tree
    return MerkleTree(padded, depth=20)
```

#### PoL Ledger Merkle Tree

**Specification**:

- Depth: 32 levels
- Leaf values: Note IDs of eligible PoL notes
- Purpose: Prove note membership in aged ledger

### Session Management

**Session Lifecycle**:

1. **Session Start**:
   - Initialize empty nullifier set
   - Load current session parameters (quotas, roots)
   - Prepare session number for proofs

2. **During Session**:
   - Verify incoming proofs
   - Track nullifiers in set
   - Reject duplicate nullifiers

3. **Session End**:
   - Clear nullifier set
   - Archive session data
   - Transition to next session

### Best Practices

#### Nullifier Set Management

- Use efficient data structure (hash set or Bloom filter with fallback)
- Implement atomic operations for nullifier insertion
- Consider memory constraints for long sessions

#### Pre-Generation Strategy

For leader nodes:

- Generate proofs before slot assignment
- Cache proofs for multiple indices
- Monitor note status separately from PoQ

#### Error Handling

Implementations SHOULD handle:

- Invalid proof format
- Duplicate nullifiers
- Index out of bounds
- Merkle path verification failures
- Invalid selector values

## References

### Normative

- NOMOS-BLEND-PROTOCOL - Blend Protocol specification for Nomos
- Service Declaration Protocol (SDP) - Protocol for declaring core nodes
- Mantle Specification
- Circuit Constraints (Cryptarchia)
- Proof of Selection
- [Rate-Limiting Nullifiers](https://rate-limiting-nullifier.github.io/rln-docs/)
  \- RLN documentation for rate-limiting mechanisms

### Informative

- [Proof of Quota Specification](https://nomos-tech.notion.site/Proof-of-Quota-Specification-215261aa09df81d88118ee22205cbafe)
  \- Original Proof of Quota documentation
- BN256 Curve Specification
- zk-SNARKs (Zero-Knowledge Succinct Non-Interactive Arguments of Knowledge)
- [Cryptarchia Consensus](https://arxiv.org/abs/2402.06408)
- Merkle Trees and Authentication Paths

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
