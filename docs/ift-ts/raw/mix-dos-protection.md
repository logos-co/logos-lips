# Mix DoS Protection

| Field | Value |
| --- | --- |
| Name | Mix DoS Protection |
| Slug | TBD |
| Status | raw |
| Category | Standards Track |
| Editor | Prem Prathi <prem@status.im> |
| Contributors | Akshaya Mani <akshaya@status.im> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

This document defines the DoS protection architecture for the [libp2p Mix Protocol](./mix.md).
It specifies the requirements, integration architectures, node responsibilities, and standardized interfaces that any DoS protection mechanism must satisfy to integrate with the Mix Protocol.
Two primary architectural approaches are defined: sender-generated proofs and per-hop generated proofs.
Concrete instantiation of this architecture, using Rate Limiting Nullifier (RLN), is defined in a separate specification (see [Mix RLN DoS Protection](./mix-spam-protection-rln.md)).

## 1. Introduction

The Mix Protocol is a stateless, sender-anonymous message routing protocol.
Without DoS protection, malicious actors can flood mix nodes with valid Sphinx packets, exhausting computational resources or bandwidth, eventually making the mixnet unusable.

This specification expands on the pluggable [DoS protection framework](./mix.md#66-dos-protection) introduced in the Mix Protocol.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Other terms used in this document are as defined in the [libp2p Mix Protocol](./mix.md).

## 3. Requirements

Any DoS protection mechanism integrated with the Mix Protocol MUST satisfy the following requirements:

- Each mix node in the path MUST verify proofs before applying delay and forwarding, or, in the case of exit nodes, taking further action.

- DoS protection data and verification MUST NOT enable linking or correlating packets across hops.
  Therefore, DoS protection proofs MUST be unique per hop.

- DoS protection proofs MUST NOT be reusable across different packets or hops.
  Each hop SHOULD be able to detect replayed or forged proofs (_e.g.,_ via cryptographic binding to packet-specific or hop-specific data).

- Proofs SHOULD be bound to unique signals per message that cannot be known in advance, preventing adversaries from pre-computing large batches of proofs offline for DoS attacks.

- Verification overhead MUST be low to minimise per-hop delays.
  Otherwise, under load, substantial delay at each hop can cause congestion at mix nodes, making the DoS protection mechanism itself a resource exhaustion vector.

- Proof generation and verification methods MUST preserve unlinkability of the sender and MUST NOT leak any additional metadata about the sender or node.

- The mechanism SHOULD provide a way to punish offenders or detect misuse.

## 4. Integration Architecture

Two primary architectural approaches exist for integrating DoS protection with the Mix Protocol, each with distinct trade-offs.
This section describes each approach in detail, including trade-offs and deployment considerations.

### 4.1 Sender-Generated Proofs

In this approach, the initiating node (on behalf of the sender) generates DoS protection proofs for all hops in the mix path during Sphinx packet construction.
These proofs are then independently verified at each hop during Sphinx packet processing.

#### 4.1.1 Details

The proof generation and verification proceed as follows:

1. **Sender Proof Generation and Embedding:**
   During [Sphinx packet construction](./mix.md#85-packet-construction) of the Mix Protocol, the initiating node first computes the ephemeral secrets (step 3.a) and encrypted payload (step 3.d). Note that this deviates from the standard Sphinx construction order.
   Next, it computes the filler strings (step 3.b), where the zero-padding length depends on the size of the DoS protection proof embedded in each hop's routing block (see [Section 4.1.4](#414-impact-on-header-size)).
   Then, during step 3.c, for each hop $i$ in the path, the initiating node:

   a. Computes the DoS protection proof cryptographically bound to the decrypted payload $δ_{i+1}$ that hop $i$ obtains after decrypting one layer.
      This binding ensures proofs are path-specific and tied to specific encrypted message content, preventing proof extraction and reuse.

   b. Embeds the DoS protection proof and related metadata required for verification in hop $i$'s routing block, $β_i$.

2. **Per-Hop Proof Verification:**
   During [Sphinx processing](./mix.md#861-shared-preprocessing), each hop $i$ decrypts $β$ and $δ$ to obtain the routing block $B$ (Step 4) and $δ'$ (Step 5) respectively, then:

   a. Extracts the DoS protection proof and metadata from $B$.
   b. Verifies the proof is bound to $δ'$.

#### 4.1.2 Advantages

- Only the initiating node performs the expensive proof generation.
  All nodes in the path only verify proofs, which is less expensive and also reduces latency per hop.
- Each hop's proof is encrypted in a separate layer of $β$, making proofs unique per hop and cryptographically isolated.
- Aligns with Sphinx design philosophy, where the initiating node bears the computational complexity while all nodes in the path only perform lightweight operations.

#### 4.1.3 Disadvantages

- The initiating node must generate $L$ proofs, which can be expensive.
- Each hop's routing block must include DoS protection data, increasing overall header and packet size (see impact analysis below).
- When packets are sent along [multiple paths for reliability](./mix.md#942-no-built-in-retry-or-acknowledgment), the initiating node must generate $L$ fresh proofs for each path.
- Proofs can only be verified after expensive Sphinx processing operations (session key derivation, replay checking, header integrity verification, and decryption), since they are encrypted within the $β$ field and bound to the decrypted payload state $δ'$.
  Deployments using this approach SHOULD augment with additional network-level protections (connection rate limiting, localized peer reputation) to defend against attacks that can lead to draining nodes' resources.
- This approach does not inherently provide Sybil resistance since nodes in the path do not generate any proof using their credentials.

#### 4.1.4 Impact on Header Size

Each hop's routing block includes $\mathrm{dos\_proof}$, consisting of the DoS protection proof and all verification metadata.
$\mathrm{dos\_proof}$ MUST be exactly $dκ$ bytes for some positive integer $d$, where $κ = 128$ bits is the security parameter defined in [cryptographic primitives](./mix.md#82-cryptographic-primitives) of the Mix Protocol.
This format is required for the Sphinx $β$ construction to hold.

Including $\mathrm{dos\_proof}$ increases the per-hop routing block size from $(t+1)κ$ to $(t+d+1)κ$ bytes.
Consequently, the zero-padding in the filler string computation (see [Section 4.1.1](#411-details)) increases from $(t+1)κ$ to $(t+d+1)κ$, giving a filler string length of $|\Phi_i| = (t+d+1)iκ$, $0 \leq i \leq L-1$.

As a result, the total $β$ size becomes $((t+d+1)r+1)κ$ bytes (see [header field sizes](./mix.md#831-header-field-sizes)) — an increase of $rdκ$ bytes over the baseline.
To offset this increase and maintain the same payload size, the total packet size MUST be increased to $4608 + rdκ$ bytes (see [payload size](./mix.md#832-payload-size)).

### 4.2 Per-Hop Generated Proofs

In this approach, the initiating node generates a DoS protection proof for the first hop, and each mix node in the path generates a fresh proof for the subsequent hop after verifying the proof attached to the incoming packet.

#### 4.2.1 Details

The proof generation, verification, and forwarding proceed as follows:

1. During [Sphinx packet construction](./mix.md#85-packet-construction) of the Mix Protocol, after step 3.e, the initiating node generates an initial DoS protection proof $σ$ for the first hop and appends it after the Sphinx packet, forming the wire format: `SphinxPacket || σ`.
   The proof SHOULD be cryptographically bound to the complete outgoing Sphinx packet $(α_0 | β_0 | γ_0 | δ_0)$ and include any verification metadata required by the DoS protection proof.
2. The first hop extracts and verifies $σ$ before [processing the Sphinx packet](./mix.md#861-shared-preprocessing).
3. After successful verification and Sphinx processing, the hop generates a new proof $σ'$ for the next hop bound to the transformed packet.
4. The updated packet is forwarded to the next hop.
5. This process repeats at each intermediate hop until the packet reaches the final hop.
   The exit just verifies the proof in the incoming packet without generating a new one.

#### 4.2.2 Advantages

- The initiating node only generates one initial proof instead of $L$ proofs.
- DoS protection data has less overhead on packet header size.
- Proofs can be verified before Sphinx processing operations (session key derivation, header integrity verification, and decryption).
  Given that verification is cheaper (see [Section 3](#3-requirements)), this allows nodes to reject invalid packets without performing expensive Sphinx processing.
- If a membership-based DoS protection mechanism is used (_e.g.,_ Rate Limiting Nullifiers), the same mechanism can provide Sybil resistance as a side effect (see [Section 9.4.3 of the Mix Protocol](./mix.md#943-no-sybil-resistance)).
  Nodes must prove membership at each hop, making it infeasible to operate large numbers of Sybil nodes; provided membership carries a cost and offenders can be penalized (see [Section 7](#7-recommended-methods)).

#### 4.2.3 Disadvantages

- Each intermediary node must generate fresh proofs, adding additional latency and processing cost at each hop.
  Pre-computing proofs offline is not an option, as proofs SHOULD be bound to message contents or an alternative unique signal that cannot be known in advance (see [Section 3](#3-requirements)).
- When using rate-limiting mechanisms (such as RLN), a node may exhaust its rate limit solely by being selected on multiple independent senders' paths.
  This causes legitimate packets to be dropped, resulting in unpredictable message delivery, even when no individual sender misbehaves.
  The Mix Protocol's [unlinkability guarantees](./mix.md#91-security-guarantees-of-the-core-mix-protocol) make it impossible to distinguish a node forwarding messages from one originating them. This makes mitigations such as assigning differential or reputation-based rate limits infeasible.

#### 4.2.4 Impact on Packet Size

As mentioned in [Section 4.2.1](#421-details), $σ$ consists of the DoS protection proof and all verification metadata.
Unlike sender-generated proofs, appending $σ$ after the Sphinx packet does not affect the internal Sphinx packet structure.

Consequently, only the total packet size MUST be configured to $4608 + |σ|$ bytes (see [payload size](./mix.md#832-payload-size)).

$|σ|$ MUST be fixed for a chosen DoS protection mechanism.
If the mechanism produces variable-length proofs, they MUST be padded to a fixed size, ensuring all packets remain indistinguishable on the wire.

### 4.3 Comparison

The following table provides a brief comparison between both integration approaches.

| Aspect                             | Sender-Generated Proofs                 | Per-Hop Generated Proofs                   |
| ---------------------------------- | --------------------------------------- | ------------------------------------------ |
| **DoS protection**                 | Weaker (verify after Sphinx decryption) | Stronger (verify before Sphinx decryption) |
| **Sender burden**                  | High (generates $L$ proofs)             | Low (generates 1 proof)                    |
| **Per-hop computational overhead** | Low (verify only)                       | High (verify + generate)                   |
| **Per-hop latency**                | Minimal (fast verification)             | Higher                                     |
| **Total end-to-end latency**       | Lower                                   | Higher                                     |
| **Sybil resistance**               | Requires separate mechanism             | Can be integrated                          |
| **Packet size increase**           | $r \times \|\mathrm{dos\_proof}\|$      | $\|σ\|$                               |

Separate specifications defining concrete DoS protection mechanisms SHOULD specify recommended approaches and provide detailed integration instructions.

## 5. Node Responsibilities

In addition to the core Mix Protocol responsibilities defined in [Section 7](./mix.md#7-core-mix-protocol-responsibilities), all mix nodes MUST implement the following DoS protection responsibilities for the chosen architectural approach.

### 5.1 For Sender-Generated Proofs

**[During Sphinx packet construction](./mix.md#85-packet-construction):** 
Generate and embed DoS protection proofs for all hops as described in [Section 4.1.1](#411-details).
The proofs MUST NOT contain any identifying information.

**[During Sphinx packet preprocessing](./mix.md#861-shared-preprocessing):**
Verify the DoS protection proof in its routing block as described in [Section 4.1.1](#411-details).
If verification fails, discard the packet and apply any penalties or rate-limiting measures.

### 5.2 For Per-Hop Generated Proofs

**[During Sphinx packet construction](./mix.md#85-packet-construction):**
Generate the initial proof $σ$ and append it after the Sphinx packet as described in [Section 4.2.1](#421-details).
The proof MUST NOT contain any identifying information.

**[During Sphinx packet preprocessing](./mix.md#861-shared-preprocessing):**
Extract and verify the incoming proof $σ$ before any Sphinx processing as described in [Section 4.2.1](#421-details).
If verification fails, discard the packet and apply any penalties or rate-limiting measures.

**[After node role determination](./mix.md#862-node-role-determination):**
- If intermediary, during [intermediary processing](./mix.md#863-intermediary-processing), generate a fresh unlinkable proof $σ'$ and append it to the assembled packet before Step 5.
- If exit, perform [exit processing](./mix.md#864-exit-processing) without generating a new proof.

## 6. Anonymity and Security Considerations

DoS protection mechanisms MUST be carefully designed to avoid introducing correlation risks:

- **Timing side channels**: Proof verification and generation SHOULD use constant-time implementations to avoid timing-based side channel attacks that could enable packet fingerprinting.

- **Proof unlinkability**: Linking incoming and outgoing proofs at intermediary hops MUST be cryptographically hard, to preserve the [bitwise unlinkability](./mix.md#91-security-guarantees-of-the-core-mix-protocol) guaranteed by the Mix Protocol.

- **Verification failure handling**: Nodes MUST silently discard packets that fail proof verification, without revealing the reason for failure, to prevent probing attacks.

- **Global state and coordination**: Mechanisms that maintain global state (_e.g.,_ nullifier sets, membership trees) MUST ensure that state reads and writes do not reveal packet processing patterns or enable correlation across hops, in accordance with the [DoS vulnerability considerations](./mix.md#944-vulnerability-to-denial-of-service-attacks) of the Mix Protocol.

- **Sybil attacks**: The Mix Protocol provides no built-in [Sybil resistance](./mix.md#943-no-sybil-resistance).
  Sender-generated proofs do not address this limitation.
  Per-hop generated proofs with membership-based mechanisms MAY provide Sybil resistance as a side effect (see [Section 4.2.2](#422-advantages)).

## 7. Recommended Methods

Specific DoS protection methods fall outside this specification's scope.
Common strategies that MAY be adapted include:

- **PoW-style approaches**: Approaches like [EquiHash](https://github.com/khovratovich/equihash) or [VDF Client puzzles](https://www.researchgate.net/publication/356450648_Non-Interactive_VDF_Client_Puzzle_for_DoS_Mitigation) that satisfy DoS protection requirements can be used.
  These, however, do not provide Sybil resistance, which requires a separate mechanism.

- **Privacy-preserving rate-limiting**: Rate-limiting approaches with zero-knowledge cryptography, such as [RLN](https://rate-limiting-nullifier.github.io/rln-docs/rln_in_details.html), that preserve users' privacy can be used (see [Mix RLN DoS Protection](./mix-spam-protection-rln.md)).
  This approach requires careful design of state access patterns.
  Deployments requiring Sybil resistance SHOULD augment this mechanism with staking and slashing.

Deployments MUST evaluate each method's computational overhead, latency impact, anonymity implications, infrastructure requirements, attack resistance, Sybil resistance, pre-computation resistance, economic cost, and architectural fit.

## 8. DoS Protection Interface

This section defines the standardized interface that DoS protection mechanisms MUST implement to integrate with the Mix Protocol.
The interface is designed to be architecture-agnostic, supporting both sender-generated proofs and per-hop generated proofs approaches described in [Section 4](#4-integration-architecture).

Initialization and configuration of DoS protection mechanisms are out of scope for this interface specification.
Implementations MUST handle their own initialization, configuration management, and runtime state independently before being integrated with the Mix Protocol.

Any DoS protection mechanism integrated with the Mix Protocol MUST implement the procedures defined in this section.
The specific cryptographic constructions, proof systems, and verification logic are left to the mechanism's specification, but implementations MUST adhere to the interface signatures and behavior defined here for interoperability.

### 8.1 Deployment Configuration

The following parameters MUST be agreed upon and configured consistently across all nodes in a deployment:

- **Proof Size**: The fixed size in bytes of `encoded_proof_data` produced by `GenerateProof`.
  This value is used by Mix Protocol implementations to calculate header sizes and payload capacity.

- **Integration Architecture**: The DoS protection integration architecture used by the deployment.
  MUST be one of:
  - `SENDER_GENERATED`: Initiating node generates proofs for each hop (see [Section 8.3.1](#831-for-sender-generated-proofs))
  - `PER_HOP_GENERATED`: Each node generates a fresh proof for the next hop (see [Section 8.3.2](#832-for-per-hop-generated-proofs))

All nodes in a deployment MUST use the same integration architecture.
Nodes MUST refuse to process packets that do not conform to the deployment's configured architecture.

### 8.2 Interface Procedures

All DoS protection mechanisms MUST implement the following procedures.

#### 8.2.1 Proof Generation

`GenerateProof(binding_data) -> encoded_proof_data`

Generate a DoS protection proof bound to specific packet data.

**Parameters**:

- `binding_data`: The packet-specific data to which the proof MAY be cryptographically bound.
  For sender-generated proofs, this is $δ_{i+1}$ (the decrypted payload that hop $i$ will see).
  For per-hop generated proofs, this is the complete outgoing Sphinx packet state $(α', β', γ', δ')$.

**Returns**:

- `encoded_proof_data`: Serialized bytes containing the DoS protection proof and any required verification metadata.
  This is treated as opaque data by the Mix Protocol layer.

**Requirements**:

- The DoS protection mechanism is responsible for managing its own runtime state (_e.g.,_ current epochs, difficulty levels, merkle tree states).
  The Mix Protocol layer does not provide or track mechanism-specific runtime context.
- The encoding MUST produce a fixed-length output.

#### 8.2.2 Proof Verification

`VerifyProof(encoded_proof_data, binding_data) -> valid`

Verify that a DoS protection proof is valid and correctly bound to the provided packet data.

**Parameters**:

- `encoded_proof_data`: Serialized bytes containing the DoS protection proof and verification metadata, extracted from the routing block $β$ (for sender-generated proofs) or from the appended field $σ$ (for per-hop generated proofs).
- `binding_data`: The packet-specific data against which the proof MUST be verified.
  For nodes verifying sender-generated proofs, this is $δ'$ (the decrypted payload).
  For per-hop verification, this is the received Sphinx packet state $(α', β', γ', δ')$.

**Returns**:

- `valid`: Boolean indicating whether the proof is valid.

**Requirements**:

- Implementations MUST handle malformed or truncated `encoded_proof_data` gracefully and return `false`.
- For mechanisms that maintain global state (_e.g.,_ nullifier sets, rate-limit counters, membership trees), this procedure MUST update the internal state atomically when verification succeeds.
  State updates (_e.g.,_ recording nullifiers, updating rate-limit counters) and state cleanup (_e.g.,_ removing expired epochs, old nullifiers) are managed internally by the DoS protection mechanism.

### 8.3 Integration Points in Sphinx Processing

The Mix Protocol invokes [DoS protection procedures](#82-interface-procedures) at specific points in Sphinx packet construction and processing:

#### 8.3.1 For Sender-Generated Proofs

**[During Sphinx packet construction](./mix.md#85-packet-construction):**

After computing encrypted payloads $δ_i$ for each hop (step 3.d), the initiating node MUST:

1. For each hop $i$ in the path (from $i = 0$ to $L-1$):
   - Call `GenerateProof(binding_data = δ_{i+1})` to generate `encoded_proof_data` for hop $i$
   - Embed the `encoded_proof_data` in hop $i$'s routing block within $β_i$ during header construction (step 3.c)

**[During Sphinx packet preprocessing](./mix.md#861-shared-preprocessing):**

After decrypting the routing block $β$ and payload $δ'$ (Steps 4-5), the node MUST:

1. Extract `encoded_proof_data` from the routing block $β$ at the appropriate offset
2. Call `VerifyProof(encoded_proof_data, binding_data = δ')`
3. If `valid = false`, discard the packet and terminate processing
4. If `valid = true`, continue with [node role determination](./mix.md#862-node-role-determination) and role-specific processing

#### 8.3.2 For Per-Hop Generated Proofs

**[During Sphinx packet construction](./mix.md#85-packet-construction):**

After assembling the final Sphinx packet (step 3.e), the initiating node MUST:

1. Call `GenerateProof(binding_data)` where `binding_data` is the complete Sphinx packet bytes
2. Append `encoded_proof_data` after the Sphinx packet and send to the first hop

**[During Sphinx packet preprocessing](./mix.md#861-shared-preprocessing):**

Before any Sphinx decryption operations, nodes MUST:

1. Extract `encoded_proof_data` from the last `proofSize` bytes of the received packet
2. Call `VerifyProof(encoded_proof_data, binding_data)` where `binding_data` is the Sphinx packet bytes
3. If `valid = false`, discard the packet and terminate processing
4. If `valid = true`, continue with [node role determination](./mix.md#862-node-role-determination) and role-specific processing

**Role-specific processing:**
- [Intermediary processing](./mix.md#863-intermediary-processing)
  1. Perform standard Sphinx processing, then call `GenerateProof(binding_data)` with the transformed packet as `binding_data`
  2. Append the new `encoded_proof_data` to the transformed Sphinx packet and forward
- [Exit processing](./mix.md#864-exit-processing)
  Perform standard Sphinx processing without generating a new proof.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [libp2p Mix Protocol](./mix.md)
- [Mix RLN DoS Protection](./mix-spam-protection-rln.md)
- [EquiHash](https://github.com/khovratovich/equihash)
- [VDF Client Puzzles](https://www.researchgate.net/publication/356450648_Non-Interactive_VDF_Client_Puzzle_for_DoS_Mitigation)
- [Rate Limiting Nullifiers (RLN)](https://rate-limiting-nullifier.github.io/rln-docs/rln_in_details.html)
