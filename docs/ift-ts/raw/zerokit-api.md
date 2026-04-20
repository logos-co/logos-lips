# Zerokit API

| Field | Value |
| --- | --- |
| Name | Zerokit API |
| Slug | 142 |
| Status | raw |
| Category | Standards Track |
| Editor | Vinh Trinh <vinh@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-21** — [`70f3cfb`](https://github.com/logos-co/logos-lips/blob/70f3cfb4df4e9a94e56b1284e98ee1dc9df50ac7/docs/ift-ts/raw/zerokit-api.md) — chore: mdbook font fix (#266)

<!-- timeline:end -->

## Abstract

This document specifies the Zerokit API, an implementation of the RLN-V2 protocol.
The specification covers the unified interface exposed through **native Rust**,
C-compatible Foreign Function Interface (FFI) bindings,
and WebAssembly (WASM) bindings.

## Motivation

The main goal of this RFC is to define the API contract,
serialization formats,
and architectural guidance for integrating the Zerokit library
across all supported platforms.
Zerokit is the reference implementation of the RLN-V2 protocol.

## Format Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Important Note

All terms and parameters used remain the same as in [RLN-V2](rln-v2.md) and [RLN-V1](32/rln-v1.md#technical-overview).

### Architecture Overview

Zerokit follows a layered architecture where
the core RLN logic is implemented once in **Rust** and
exposed through platform-specific bindings.
The protocol layer handles zero-knowledge proof generation and verification,
Merkle tree operations, and cryptographic primitives.
This core is wrapped by three interface layers:
**native Rust** for direct library integration,
**FFI** for C-compatible bindings consumed by languages (such as C and Nim),
and **WASM** for browser and Node.js environments.
All three interfaces maintain functional parity and
share identical serialization formats for inputs and outputs.

```text
      ┌─────────────────────────────────────────────────────┐
      │                  Application Layer                  │
      └──────────┬───────────────┬───────────────┬──────────┘
                 │               │               │
          ┌──────▼───────┐ ┌─────▼─────┐ ┌───────▼─────┐
          │    FFI API   │ │ WASM API  │ │   Rust API  │
          │   (C/Nim/..) │ │ (Browser) │ │   (Native)  │
          └──────┬───────┘ └─────┬─────┘ └───────┬─────┘
                 └───────────────┼───────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │   RLN Protocol    │
                       │   (Rust Core)     │
                       └───────────────────┘
```

### Supported Features

Zerokit provides [compile-time feature flags](https://github.com/vacp2p/zerokit/blob/c35e62a63517b0d32e91677422de4603760e41fa/rln/Cargo.toml#L65) that
select the Merkle tree storage backend,
configure the RLN operational mode (e.g., stateful vs. stateless),
and enable or disable parallel execution.

#### Merkle Tree Backends

`fullmerkletree` allocates the complete tree structure in memory.
This backend provides the fastest performance but consumes the most memory.

`optimalmerkletree` uses sparse HashMap storage that only allocates nodes as needed.
This backend balances performance and memory efficiency.

`pmtree` persists the tree to disk using a sled database.
This backend enables state durability across process restarts.

#### Operational Modes

`stateless` disables the internal Merkle tree.
Applications MUST provide the Merkle root and
membership proof externally when generating proofs.

When `stateless` is not enabled,
the library operates in **Stateful** mode and
requires one of the Merkle tree backends.

#### Parallelization

`parallel` enables rayon-based parallel computation for
proof generation and tree operations.

This flag SHOULD be enabled for end-user clients where
fastest individual proof generation time is required.
For server-side proof services handling multiple concurrent requests,
this flag SHOULD be disabled and
applications SHOULD use dedicated worker threads per proof instead.
The worker thread approach provides significantly higher throughput for
concurrent proof generation.

## The API

### Overview

The API exposes functional interfaces with strongly-typed parameters.
All three platform bindings share the same function signatures,
differing only in language-specific conventions.
Function signatures documented below are from the Rust perspective.

- Rust: <https://github.com/vacp2p/zerokit/blob/master/rln/src/public.rs>
- FFI: <https://github.com/vacp2p/zerokit/tree/master/rln/src/ffi>
- WASM: <https://github.com/vacp2p/zerokit/tree/master/rln-wasm>

### Error Handling

Error handling differs across platform bindings.

For **native Rust**,
functions return `Result<T, RLNError>` where `RLNError` is an enum
representing specific error conditions.
The enum variants provide type-safe error handling and
pattern matching capabilities.

For **WASM** and **FFI** bindings,
errors are returned as human-readable string messages.
This simplifies cross-language error propagation at
the cost of type safety.
Applications consuming these bindings SHOULD parse error strings or
use error message prefixes to distinguish error types when needed.

### Initialization

Functions with the same name but different signatures are **conditional compilation variants**.
This means that multiple definitions exist in the source code,
but only one variant is compiled and available at runtime based on the enabled feature flags.

`RLN::new(tree_depth, tree_config)` - *Available in Rust, FFI | Stateful mode*

- Creates a new RLN instance by loading circuit resources from the default folder.
- The `tree_config` parameter accepts multiple types via the `TreeConfigInput` trait: a JSON string, a direct config object (with `pmtree` feature), or an empty string for defaults.

`RLN::new()` - *Available in Rust, FFI | Stateless mode*

- Creates a new stateless RLN instance by loading circuit resources from the default folder.

`RLN::new_with_params(tree_depth, zkey_data, graph_data, tree_config)` - *Available in Rust, FFI | Stateful mode*

- Creates a new RLN instance with pre-loaded circuit parameters passed as byte vectors.
- The `tree_config` parameter accepts multiple types via the `TreeConfigInput` trait.

`RLN::new_with_params(zkey_data, graph_data)` - *Available in Rust, FFI | Stateless mode*

- Creates a new stateless RLN instance with pre-loaded circuit parameters.

`RLN::new_with_params(zkey_data)` - *Available in WASM | Stateless mode*

- Creates a new stateless RLN instance for WASM with pre-loaded zkey data.
- Graph data is not required as witness calculation is handled externally in WASM environments (e.g., using [witness_calculator.js](https://github.com/vacp2p/zerokit/blob/master/rln-wasm/resources/witness_calculator.js)).

### Key Generation

`keygen()`

- Generates a random identity keypair returning `(identity_secret, id_commitment)`.

`seeded_keygen(seed)`

- Generates a deterministic identity keypair from a seed returning `(identity_secret, id_commitment)`.

`extended_keygen()`

- Generates a random extended identity keypair returning `(identity_trapdoor, identity_nullifier, identity_secret, id_commitment)`.

`extended_seeded_keygen(seed)`

- Generates a deterministic extended identity keypair from a seed returning `(identity_trapdoor, identity_nullifier, identity_secret, id_commitment)`.

### Merkle Tree Management

All tree management functions are only available when `stateless` feature is **NOT** enabled.

`set_tree(tree_depth)`

- Initializes the internal Merkle tree with the specified depth.
- Leaves are set to the default zero value.

`set_leaf(index, leaf)`

- Sets a leaf value at the specified index.

`get_leaf(index)`

- Returns the leaf value at the specified index.

`set_leaves_from(index, leaves)`

- Sets multiple leaves starting from the specified index.
- Updates `next_index` to `max(next_index, index + n)`.
- If `n` leaves are passed, they will be set at positions `index`, `index+1`, ..., `index+n-1`.

`init_tree_with_leaves(leaves)`

- Resets the tree state to default and initializes it with the provided leaves starting from index 0.
- Resets the internal `next_index` to 0 before setting the leaves.

`atomic_operation(index, leaves, indices)`

- Atomically inserts leaves starting from index and removes leaves at the specified indices.
- Updates `next_index` to `max(next_index, index + n)` where `n` is the number of leaves inserted.

`set_next_leaf(leaf)`

- Sets a leaf at the next available index and increments `next_index`.
- The leaf is set at the current `next_index` value, then `next_index` is incremented.

`delete_leaf(index)`

- Sets the leaf at the specified index to the default zero value.
- Does not change the internal `next_index` value.

`leaves_set()`

- Returns the number of leaves that have been set in the tree.

`get_root()`

- Returns the current Merkle tree root.

`get_subtree_root(level, index)`

- Returns the root of a subtree at the specified level and index.

`get_merkle_proof(index)`

- Returns the Merkle proof for the leaf at the specified index as `(path_elements, identity_path_index)`.

`get_empty_leaves_indices()`

- Returns indices of leaves set to zero up to the final leaf that was set.

`set_metadata(metadata)`

- Stores arbitrary metadata in the RLN object for application use.
- This metadata is not used by the RLN module.

`get_metadata()`

- Returns the metadata stored in the RLN object.

`flush()`

- Closes the connection to the Merkle tree database.
- Should be called before dropping the RLN object when using persistent storage.

### Witness Construction

`RLNWitnessInput::new(identity_secret, user_message_limit, message_id, path_elements, identity_path_index, x, external_nullifier)`

- Constructs a witness input for proof generation.
- Validates that `message_id <= user_message_limit` and `path_elements` and `identity_path_index` have the same length.

### Witness Calculation

For **native Rust**** environments, witness calculation is handled internally by the proof generation functions.
The circuit witness is computed from the `RLNWitnessInput` and passed to the zero-knowledge proof system.

For **WASM** environments, witness calculation must be performed externally using a JavaScript witness calculator.
The workflow is:

1. Create a `WasmRLNWitnessInput` with the required parameters
2. Export to JSON format using `toBigIntJson()` method
3. Pass the JSON to an external JavaScript witness calculator
4. Use the calculated witness with `generate_rln_proof_with_witness`

The witness calculator computes all intermediate values required by the RLN circuit.

### Proof Generation

`generate_zk_proof(witness)` - *Available in Rust, FFI*

- Generates a Groth16 zkSNARK proof from a witness.
- Extract proof values separately using `proof_values_from_witness`.

`generate_rln_proof(witness)` - *Available in Rust, FFI*

- Generates a complete RLN proof returning both the zkSNARK proof and proof values as `(proof, proof_values)`.
- Combines proof generation and proof values extraction.

`generate_rln_proof_with_witness(calculated_witness, witness)`

- Generates an RLN proof using a pre-calculated witness from an external witness calculator.
- The `calculated_witness` should be a `Vec<BigInt>` obtained from the external witness calculator.
- Returns `(proof, proof_values)`.
- This is the primary proof generation method for **WASM** where witness calculation is handled by **JavaScript**.

### Proof Verification

`verify_zk_proof(proof, proof_values)`

- Verifies only the zkSNARK proof without root or signal validation.
- Returns `true` if the proof is valid.

`verify_rln_proof(proof, proof_values, x)` - *Stateful mode*

- Verifies the proof against the internal Merkle tree root and validates that `x` matches the proof signal.
- Returns an error if verification fails (invalid proof, invalid root, or invalid signal).

`verify_with_roots(proof, proof_values, x, roots)`

- Verifies the proof against a set of acceptable roots and validates the signal.
- If the roots slice is empty, root verification is skipped.
- Returns an error if verification fails.

### Slashing

`recover_id_secret(proof_values_1, proof_values_2)`

- Recovers the identity secret from two proof values that share the same external nullifier.
- Used to detect and penalize rate limit violations.

### Hash Utilities

`poseidon_hash(inputs)`

- Computes the Poseidon hash of the input field elements.

`hash_to_field_le(input)`

- Hashes arbitrary bytes to a field element using little-endian byte order.

`hash_to_field_be(input)`

- Hashes arbitrary bytes to a field element using big-endian byte order.

### Serialization Utilities

`rln_witness_to_bytes_le` / `rln_witness_to_bytes_be`

- Serializes an RLN witness to bytes.

`bytes_le_to_rln_witness` / `bytes_be_to_rln_witness`

- Deserializes bytes to an RLN witness.

`rln_proof_to_bytes_le` / `rln_proof_to_bytes_be`

- Serializes an RLN proof to bytes.

`bytes_le_to_rln_proof` / `bytes_be_to_rln_proof`

- Deserializes bytes to an RLN proof.

`rln_proof_values_to_bytes_le` / `rln_proof_values_to_bytes_be`

- Serializes proof values to bytes.

`bytes_le_to_rln_proof_values` / `bytes_be_to_rln_proof_values`

- Deserializes bytes to proof values.

`fr_to_bytes_le` / `fr_to_bytes_be`

- Serializes a field element to 32 bytes.

`bytes_le_to_fr` / `bytes_be_to_fr`

- Deserializes 32 bytes to a field element.

`vec_fr_to_bytes_le` / `vec_fr_to_bytes_be`

- Serializes a vector of field elements to bytes.

`bytes_le_to_vec_fr` / `bytes_be_to_vec_fr`

- Deserializes bytes to a vector of field elements.

### WASM-Specific Notes

WASM bindings wrap the Rust API with JavaScript-compatible types. Key differences:

- Field elements are wrapped as `WasmFr` with `fromBytesLE`, `fromBytesBE`, `toBytesLE`, `toBytesBE` methods.
- Vectors of field elements use `VecWasmFr` with `push`, `get`, `length` methods.
- Identity generation uses `Identity.generate()` and `Identity.generateSeeded(seed)` static methods.
- Extended identity uses `ExtendedIdentity.generate()` and `ExtendedIdentity.generateSeeded(seed)`.
- Witness input uses `WasmRLNWitnessInput` constructor and `toBigIntJson()` for witness calculator integration.
- Proof generation requires external witness calculation via `generateRLNProofWithWitness(calculatedWitness, witness)`.
- When `parallel` feature is enabled, call `initThreadPool()` to initialize the thread pool.
- Errors are returned as JavaScript strings that can be caught via try-catch blocks.

### FFI-Specific Notes

FFI bindings use C-compatible types with the `ffi_` prefix. Key differences:

- Field elements are wrapped as `CFr` with corresponding conversion functions.
- Results use `CResult` or `CBoolResult` structs with `ok` and `err` fields.
- Errors are returned as C-compatible strings in the `err` field of result structs.
- Memory must be explicitly freed using `ffi_*_free` functions.
- Vectors use `repr_c::Vec` with `ffi_vec_*` helper functions.
- Configuration is passed via file path to a JSON configuration file.

## Usage Patterns

This section describes common deployment scenarios and
the recommended API combinations for each.

### Stateful with Changing Root

Applies when membership changes over time with members joining and slashing continuously.

Applications MUST maintain a sliding window of recent roots externally.
When members are added or removed via `set_leaf`, `delete_leaf`, or `atomic_operation`,
capture the new root using `get_root` and append it to the history buffer.
Verify incoming proofs using `verify_with_roots` with the root history buffer,
accepting proofs valid against any recent root.

The window size depends on network propagation delays and epoch duration.

### Stateful with Fixed Root

Applies when membership is established once and remains static during an operation period.

Initialize the tree using `init_tree_with_leaves` with the complete membership set.
No root history is required.
Verify proofs using `verify_rln_proof` which checks against the internal tree root directly.

### Stateless

Applies when membership state is managed externally,
such as by a smart contract or relay network.

Enable the `stateless` feature flag.
Obtain Merkle proofs and valid roots from the external source.
Pass externally provided `path_elements` and `identity_path_index` to `RLNWitnessInput::new`.
Verify using `verify_with_roots` with externally provided roots.

### WASM Browser Integration

WASM environments require external witness calculation.
Use `WasmRLNWitnessInput::toBigIntJson()` to export the witness for
JavaScript witness calculators,
then pass the result to `generateRLNProofWithWitness`.

When `parallel` feature is enabled,
call `initThreadPool()` before proof operations.
This requires COOP/COEP headers for SharedArrayBuffer support.

#### Epoch and Rate Limit Configuration

The external nullifier is computed as `poseidon_hash([epoch, rln_identifier])`.
The `rln_identifier` is a field element that uniquely identifies your application (e.g., a hash of your app name).

All values that will be hashed MUST be represented as field elements.
For converting arbitrary data to field elements,
use `hash_to_field_le` or `hash_to_field_be` functions which internally use Poseidon hash.

Each application SHOULD use a unique `rln_identifier` to
prevent cross-application nullifier collisions.

The `user_message_limit` in the rate commitment determines messages allowed per epoch. The `message_id` must be less than `user_message_limit` and
should increment with each message.

Applications MUST persist the `message_id` counter to avoid violations after restarts.

## Security/Privacy Considerations

The security of Zerokit depends on the correct implementation of the RLN-V2 protocol
and the underlying zero-knowledge proof system.
Applications MUST ensure that:

- Identity secrets are kept confidential and never transmitted or logged
- The `message_id` counter is properly persisted to prevent accidental rate limit violations
- External nullifiers are constructed correctly to prevent cross-application attacks
- Merkle tree roots are validated when using stateless mode
- Circuit parameters (zkey and graph data) are obtained from trusted sources

When using the `parallel` feature in WASM,
applications MUST serve content with appropriate COOP/COEP headers to
enable SharedArrayBuffer support securely.

The slashing mechanism exposes identity secrets when rate limits are violated.
Applications SHOULD educate users about this risk and
implement safeguards to prevent accidental violations.

## References

### Normative

- [RLN-V1 Specification](32/rln-v1.md) - Rate Limit Nullifier V1 protocol

### Informative

- [Zerokit GitHub Repository](https://github.com/vacp2p/zerokit) - Reference implementation
- [RLN-V2 Specification](rln-v2.md) - Rate Limit Nullifier V2 protocol
- [Sled Database](https://sled.rs) - Embedded database for persistent Merkle tree storage
- [Witness Calculator](https://github.com/vacp2p/zerokit/blob/master/rln-wasm/resources/witness_calculator.js) - JavaScript witness calculator for WASM environments

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
