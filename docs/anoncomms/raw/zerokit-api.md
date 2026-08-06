# Zerokit API

| Field | Value |
| --- | --- |
| Name | Zerokit API |
| Slug | 142 |
| Status | raw |
| Category | Standards Track |
| Editor | Vinh Trinh <vinh@status.im> |
| Contributors | Ekaterina Broslavskaya [ekaterina@status.im](mailto:ekaterina@status.im), Sylvain Delhomme [sylvain@status.im](mailto:sylvain@status.im) |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`1ac7689`](https://github.com/logos-co/logos-lips/blob/1ac7689ee3fe1665d5d5d1bf9c180ed951cc660d/docs/anoncomms/raw/zerokit-api.md) — chore: split ift ts specs (#334)
- **2026-01-21** — [`70f3cfb`](https://github.com/logos-co/logos-lips/blob/70f3cfb4df4e9a94e56b1284e98ee1dc9df50ac7/docs/ift-ts/raw/zerokit-api.md) — chore: mdbook font fix (#266)

<!-- timeline:end -->

## Abstract

This document specifies the Zerokit API (version 3.0.0),
an implementation of the RLN-V2 protocol.
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

All terms and parameters used remain the same as in [RLN-V2](rln-v2.md) and [RLN-V1](../draft/32/rln-v1.md#technical-overview).

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
All three interfaces share identical serialization formats for
inputs and outputs.
Native Rust and FFI expose the full API surface,
while WASM exposes the stateless subset
(see [WASM-Specific Notes](#wasm-specific-notes)).

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

The workspace consists of four crates:
`rln` (protocol core, FFI bindings),
`zerokit_utils` (Merkle trees and Poseidon primitives),
`rln-wasm` (WASM bindings),
and `rln-cli` (example CLI, not published).
All published crates share the unified version 3.0.0.

### Type-Level Configuration

The Merkle tree backend and the stateful/stateless operating mode
are chosen **at the type level** in Rust
(and through dedicated constructors in FFI/WASM):

- `RLN<Stateful<T>, ZkProof>` embeds a Merkle tree of type `T`
  and exposes the full tree management API.
- `RLN<Stateless, ZkProof>` carries no tree;
  applications MUST provide Merkle proofs and roots externally.

The core is also generic over the zkSNARK backend
(the `RLNZkProof` / `RLNPartialZkProof` traits) and,
through it, over the protocol hash (the `ZerokitHasher` trait);
custom backends and hashes are **native-Rust-only** extension points.
The shipped, proof-verifying implementation is
`ArkGroth16Backend<PoseidonHash>` (Groth16 over BN254 with Poseidon),
and the FFI and WASM bindings expose only this concrete combination.
A hash implementation without matching circuit resources (zkey and graph)
compiles but cannot produce valid proofs.

The available feature flags are:

- `parallel` (`rln`, `zerokit_utils`, `rln-wasm`) enables rayon-based
  parallel computation for proof generation and tree operations.
- `headers` (`rln`) enables C header generation for the FFI surface.
- `panic_hook` (`rln-wasm`) enables the `initPanicHook()` console panic hook.
- `utils` (`rln-wasm`) builds a utility-only WASM module
  (field elements, identity keys, hashing) without the proof surface.

#### Merkle Tree Backends

All backends are always compiled and implement the common
`ZerokitMerkleTree` trait; applications pick one by constructing it and
passing it to the builder.

`FullMerkleTree` allocates the complete tree structure in memory.
This backend provides the fastest performance but consumes the most memory.

`OptimalMerkleTree` uses sparse HashMap storage that only allocates nodes as needed.
This backend balances performance and memory efficiency.

`PmTree<D, H>` persists the tree to disk and
enables state durability across process restarts.
It is generic over the storage backend `D`;
`SledDB` (a [sled](https://sled.rs) database) is the provided backend,
configured through `PmTreeSledConfig`
(path, temporary flag, cache capacity, flush interval,
sled mode, compression, tree depth).

The backend set is open on the native Rust side.
Applications MAY plug in a fully custom tree
(any layout or storage strategy) by implementing the
`ZerokitMerkleTree` trait,
or keep `PmTree` and swap only its persistence layer
(PostgreSQL, RocksDB, or any other store)
by implementing the `pmtree::Database` trait for `D`.
The FFI constructors expose only the three built-in backends,
and WASM, being stateless, embeds no tree backend at all.

#### Proof Modes

Every RLN instance operates in one of two circuit modes,
selected by the circuit resources (zkey and graph) loaded at construction:

- **Single message-id mode**: one `message_id` per proof.
  This is the default circuit on native targets.
- **Multi message-id mode**: a batch of message ids per proof.
  The circuit has a fixed slot count `max_out`
  (the embedded default circuit uses `DEFAULT_MAX_OUT = 4`);
  `message_ids` and `selector_used` MUST match it in length,
  with the boolean `selector_used` vector marking the active slots.
  Proof values carry vectors `ys` and `nullifiers`
  instead of scalar `y` and `nullifier`.
  The Multi circuit is larger than the Single one,
  so proof generation is slower;
  choose it only when batching message ids per proof is needed.

Embedded circuit resources are exposed as
`default_zkey_single()` / `default_graph_single()` and
`default_zkey_multi()` / `default_graph_multi()`.
The default tree depth is `DEFAULT_TREE_DEPTH = 20`.

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

The API exposes strongly-typed interfaces.
All three platform bindings share the same operations,
differing only in language-specific conventions.
Function signatures documented below are from the Rust perspective.

- Rust: <https://github.com/vacp2p/zerokit/blob/master/rln/src/public.rs>
- FFI: <https://github.com/vacp2p/zerokit/tree/master/rln/src/ffi>
- WASM: <https://github.com/vacp2p/zerokit/tree/master/rln-wasm>

Rust consumers SHOULD import from `rln::prelude`,
which re-exports the full public surface
(RLN types, protocol types, hashers, errors, and serialization traits).

### Error Handling

Error handling differs across platform bindings.

For **native Rust**,
each operation returns a `Result` with a **narrow, operation-specific error enum**
whose variants are all reachable from that code path.
There is no top-level union error type.
The error enums map to operations as follows:

- `WitnessInputSingleError` / `WitnessInputMultiError` / `PartialWitnessInputError`:
  structural validation in the witness builders.
- `ProofValuesMultiError`: structural validation of Multi-mode proof values.
- `GenerateProofError`: proof generation
  (witness/circuit mismatch or backend fault).
- `VerifyProofError`: verification input mismatch
  (`InvalidSignal`, `InvalidRoot`) or backend fault.
- `RecoverSecretError`: slashing recovery when the two proofs do not
  yield a matching nullifier.
- `SerializationError`: deserialization failures,
  including the construction-time validation errors surfaced through
  typed wrap variants.

For **WASM** and **FFI** bindings,
errors are returned as human-readable string messages.
This simplifies cross-language error propagation at
the cost of type safety.
Applications consuming these bindings SHOULD parse error strings or
use error message prefixes to distinguish error types when needed.

### Initialization

Native Rust construction goes exclusively through `RLNBuilder`,
a type-state builder that fixes the proof backend to
Groth16 over BN254 with the Poseidon hash
(`ArkGroth16Backend<PoseidonHash>`).

`RLNBuilder::stateless().build()` - *Rust | Stateless mode*

- Builds a stateless RLN instance.
- Optional setters `.zkey()` and `.graph()` accept pre-loaded circuit
  resources; on native targets both default to the Single message-id circuit.
- On `wasm32` targets the resources MUST be supplied.

```rust
// A stateless instance; the embedded Single message-id circuit is used by default.
let rln = RLNBuilder::stateless().build();

// A stateless instance using the embedded Multi message-id circuit instead.
let rln = RLNBuilder::stateless()
    .graph(default_graph_multi().clone())
    .zkey(default_zkey_multi().clone())
    .build();
```

`RLNBuilder::stateful().tree(tree).build()` - *Rust | Stateful mode*

- Builds a stateful RLN instance around a caller-constructed Merkle tree
  (`FullMerkleTree`, `OptimalMerkleTree`, or `PmTree`).
- The tree hasher MUST match the proof backend hash;
  a mismatch is a compile error.
- Optional `.zkey()` / `.graph()` setters behave as in `stateless`.

```rust
// A stateful instance owning a persistent PmTree;
// the embedded Single message-id circuit is used by default.
let config = PmTreeSledConfig::new()
    .path("./database")
    .temporary(false)
    .cache_capacity(1_073_741_824)
    .flush_every_ms(500)
    .build()?;
let tree = PmTree::<SledDB, PoseidonHash>::new(DEFAULT_TREE_DEPTH, Fr::default(), config)?;
let mut rln = RLNBuilder::stateful().tree(tree).build();
```

FFI exposes one constructor per backend and mode,
each with a `_default` variant that uses the embedded Single message-id
circuit and `DEFAULT_TREE_DEPTH`:

- `ffi_rln_new_stateless(zkey_data, graph_data)` / `ffi_rln_new_stateless_default()`
- `ffi_rln_new_with_full_merkle_tree(tree_depth, zkey_data, graph_data)` /
  `ffi_rln_new_with_full_merkle_tree_default()`
- `ffi_rln_new_with_optimal_merkle_tree(tree_depth, zkey_data, graph_data)` /
  `ffi_rln_new_with_optimal_merkle_tree_default()`
- `ffi_rln_new_with_pm_tree(tree_depth, zkey_data, graph_data, config_path)` /
  `ffi_rln_new_with_pm_tree_default()`
  (an empty `config_path` selects the default sled configuration)

WASM is **stateless only**:

`WasmRLN.newWithParams(zkey_data, graph_data)` - *WASM | Stateless mode*

- Creates a stateless RLN instance from pre-loaded zkey and graph bytes.
- Unlike native targets, WASM ships no default circuit resources;
  both byte buffers are REQUIRED.
- Witness calculation is performed internally by the witness graph
  supplied at construction.

### Key Generation

Identity material is represented by dedicated structs.
Secret components are wrapped in `SecretFr`,
a zeroize-on-drop field element with a redacted `Debug` representation
(see [Security/Privacy Considerations](#securityprivacy-considerations)).

`IdentityKeys::generate::<PoseidonHash, R>(rng)`

- Generates a random identity keypair using the caller-supplied
  cryptographically secure RNG `R`.
- Accessors: `identity_secret() -> SecretFr`, `id_commitment() -> Fr`.

`IdentityKeys::generate_seeded::<PoseidonHash, R>(seed)`

- Generates a deterministic identity keypair from a byte seed.
- The seed is expanded with Keccak-256 (an out-of-circuit hash;
  see [Hash Utilities](#hash-utilities)) into the seed of the
  type-level chosen seedable RNG `R`.

`ExtendedIdentityKeys::generate::<PoseidonHash, R>(rng)`

- Generates a random extended identity keypair.
- Accessors: `identity_trapdoor()`, `identity_nullifier()`,
  `identity_secret()` (all `SecretFr`), and `id_commitment() -> Fr`.

`ExtendedIdentityKeys::generate_seeded::<PoseidonHash, R>(seed)`

- Deterministic variant of the extended keypair generation.

Both the hash and the RNG are spelled at the call site;
the Merkle leaf is the rate commitment derived from the identity commitment:

```rust
let identity_keys = IdentityKeys::generate::<PoseidonHash, ThreadRng>(&mut thread_rng());
let seeded_keys = IdentityKeys::generate_seeded::<PoseidonHash, ChaCha20Rng>(b"seed bytes");

let rate_commitment =
    Hasher::<PoseidonHash>::hash_pair(identity_keys.id_commitment(), user_message_limit);
```

FFI and WASM wrappers pin concrete RNG defaults
(`ThreadRng` for random, `ChaCha20Rng` for seeded generation)
so seeded outputs are bit-identical across platforms:
`ffi_identity_keys_generate()` / `ffi_identity_keys_generate_seeded()`,
`ffi_extended_identity_keys_generate()` /
`ffi_extended_identity_keys_generate_seeded()`,
`WasmIdentityKeys.generate()` / `generateSeeded()`,
and `WasmExtendedIdentityKeys.generate()` / `generateSeeded()`.

### Merkle Tree Management

Tree management methods exist **only** on stateful instances
(`RLN<Stateful<T>, _>`); stateless instances do not expose them
(in FFI, calling a tree operation on a stateless handle returns an error).

`tree_depth()`

- Returns the depth of the internal Merkle tree.

`leaves_set()`

- Returns the number of leaves that have been set in the tree.

`get_root()`

- Returns the current Merkle tree root.

`get_subtree_root(level, index)`

- Returns the root of the subtree at the given `level` on the path to leaf `index`.
- `level` 0 is the tree root; `level` equal to the tree depth is the leaf itself.

`set_leaf(index, leaf)`

- Sets a leaf value at the specified index.

`set_leaves_from(index, leaves)`

- Sets multiple leaves starting from the specified index.
- Updates `next_index` to `max(next_index, index + n)`.
- If `n` leaves are passed, they will be set at positions `index`, `index + 1`, ...,
  `index + n - 1`.

`init_tree_with_leaves(leaves)`

- Resets the tree state to default (keeping the current depth) and
  initializes it with the provided leaves starting from index 0.
- Resets the internal `next_index` to 0 before setting the leaves.

`get_leaf(index)`

- Returns the leaf value at the specified index.

`get_empty_leaves_indices()`

- Returns the indices of the leaves set to the default value, up to the last set leaf.

`atomic_operation(index, leaves, indices)`

- Atomically sets `leaves` starting from `index` and resets each entry of `indices`
  to the default value, in a single commit.
- When a written position also appears in `indices`, the write wins.
- Updates `next_index` to `max(next_index, index + n)` where `n` is the number of leaves inserted.

`set_next_leaf(leaf)`

- Sets a leaf at the next never-set index and increments `next_index` by one.

`delete_leaf(index)`

- Resets the leaf at the specified index to the default value.
- Does not change the internal `next_index` value.

`get_merkle_proof(index)`

- Returns the Merkle proof for the leaf at the specified index.
- Any backend proof converts into the canonical `RLNMerkleProof`
  data type (`path_elements`, `identity_path_index`) used by witness construction.

`set_metadata(metadata)` / `get_metadata()`

- Stores and retrieves arbitrary application metadata in the RLN object.
- This metadata is not used by the RLN module.

`close()`

- Closes the tree, flushing pending writes for persistent backends
  (a no-op for in-memory backends).
- Dropping the instance does not flush, so persistent-backend users
  MUST call `close()` before exit to guarantee durability.

### Merkle Proof

`RLNMerkleProof` is the canonical Merkle proof data type
(`path_elements`, `identity_path_index`) consumed by witness construction.

`RLNMerkleProof::new(path_elements, identity_path_index)`

- Wraps externally supplied path data (stateless workflows).
- Tree proofs returned by `get_merkle_proof()` convert into it automatically:
  a blanket `From` impl covers every type implementing the
  `ZerokitMerkleProof` trait, current and future backends alike.
- The type carries its own LE and BE serde impls,
  so a Merkle proof can be stored or transmitted on its own
  (exposed over FFI as `ffi_rln_merkle_proof_to_bytes_le()` /
  `ffi_rln_merkle_proof_to_bytes_be()` and the matching `from_bytes`
  functions, and over WASM as `WasmRLNMerkleProof.toBytesLE()` /
  `toBytesBE()` / `fromBytesLE()` / `fromBytesBE()`).

### Witness Construction

Witness inputs are built through validating builders and
are represented by the `RLNWitnessInput` enum
(`Single` / `Multi` variants).
Every builder takes its Merkle path through the `merkle_proof` setter,
which accepts the [`RLNMerkleProof`](#merkle-proof) data type
described above (or any tree proof convertible into it).

Single message-id witness:

```rust
let witness = RLNWitnessInput::new_single()
    .identity_secret(identity_secret)
    .user_message_limit(user_message_limit)
    .merkle_proof(&merkle_proof)
    .x(x)
    .external_nullifier(external_nullifier)
    .message_id(message_id)
    .build()?;
```

- `build()` checks the structural invariants
  (non-zero `user_message_limit`,
  matching `path_elements` / `identity_path_index` lengths,
  `message_id < user_message_limit`)
  and returns `WitnessInputSingleError` on violation.

Multi message-id witness:

```rust
let witness = RLNWitnessInput::new_multi()
    .identity_secret(identity_secret)
    .user_message_limit(user_message_limit)
    .merkle_proof(&merkle_proof)
    .x(x)
    .external_nullifier(external_nullifier)
    .message_ids(message_ids)
    .selector_used(selector_used)
    .build()?;
```

- `build()` checks the Multi-mode invariants
  (non-zero `user_message_limit`, matching path lengths,
  non-empty `message_ids`, `selector_used` matching `message_ids` in length,
  at least one active selector,
  and unique in-range active `message_id`s)
  and returns `WitnessInputMultiError` on violation.

Partial witness (the subset known ahead of time,
used for two-step proof generation):

```rust
let partial_witness = RLNPartialWitnessInput::new()
    .identity_secret(identity_secret)
    .user_message_limit(user_message_limit)
    .merkle_proof(&merkle_proof)
    .build()?;
```

- `build()` checks the structural invariants and returns
  `PartialWitnessInputError` on violation.
- A partial witness can also be converted from a full witness
  (`From<&RLNWitnessInput>`).

Witness calculation is handled internally on **all** platforms,
including WASM, by the witness graph loaded at construction
(the embedded default on native targets, caller-supplied bytes on WASM).

### Proof Generation

`generate_proof(witness)`

- Generates a Groth16 zkSNARK proof and its public proof values from a witness.
- Returns `(proof, proof_values)`;
  `proof_values` is an `RLNProofValues` enum (`Single` / `Multi`).
- Fails with `GenerateProofError` on witness/graph inconsistency or backend fault.

`generate_partial_proof(partial_witness)`

- First step of **two-step proof generation**:
  precomputes a partial proof from the inputs known ahead of time
  (identity, message limit, Merkle path),
  before the signal and external nullifier are known.

`finish_proof(partial_proof, witness)`

- Second step: completes the partial proof with the full witness and
  returns `(proof, proof_values)`.
- This split lets latency-sensitive applications move the bulk of the
  proving work off the critical path.

### Proof Verification

All verification methods return `Result<bool>`.
The `Ok(bool)` value is the zkSNARK verification **verdict**:
an invalid proof is reported as `Ok(false)`, not as an error.
`Err` is reserved for caller-input mismatch
(`InvalidSignal`, `InvalidRoot`) and backend faults.

`verify(proof, proof_values)`

- Verifies only the zkSNARK proof without root or signal validation.

`verify_with_signal(proof, proof_values, x)`

- Checks that the signal `x` matches the value bound in the proof
  (`Err(InvalidSignal)` on mismatch), then returns the zkSNARK verdict.

`verify_with_roots(proof, proof_values, x, roots)`

- Additionally checks that the proof root is among `roots`
  (`Err(InvalidRoot)` on mismatch).
- If the `roots` slice is empty, root verification is skipped.
- This is the RECOMMENDED verification entry point:
  pass the accepted root window when membership changes over time,
  or the externally obtained roots in stateless deployments.

End-to-end, proof generation and verification compose as:

```rust
let (proof, proof_values) = rln.generate_proof(&witness)?;

let root = rln.get_root();
let verified = rln.verify_with_roots(&proof, &proof_values, &x, &[root])?;
assert!(verified, "proof rejected");
```

The FFI and WASM boundaries preserve this shape:
an FFI `FFI_BoolResult { ok: false, err: null }` and
a WASM `false` return are real "proof invalid" verdicts,
not errors.

### Slashing

`RLNProofValues::recover_secret(other)` (trait `RecoverSecret`)

- Recovers the identity secret from two proof values that share the same
  nullifier.
- Two proofs collide on a nullifier when they were generated with the same
  `external_nullifier` **and** the same `message_id`
  (the nullifier is derived from both),
  i.e. a `message_id` was reused within an epoch.
- Returns `RecoverSecretError` when the two proofs do not yield a matching
  nullifier (no slashing possible).
- Recovery works across modes: Single with Single, Multi with Multi,
  and Single combined with Multi.

`compute_id_secret(share1, share2)`

- Lower-level Shamir reconstruction from two `(x, y)` shares.

FFI: `ffi_rln_recover_id_secret()`, `ffi_rln_compute_id_secret()`
(the recovered secret is returned as a plain field element deliberately,
since slashing is a reveal).
WASM: `WasmRLNProofValues.recoverIdSecret()` / `computeIdSecret()`.

### Hash Utilities

`Hasher::<PoseidonHash>::hash_single(input)` / `hash_pair(left, right)` / `hash_list(inputs)`

- Computes the Poseidon hash for one, two, or a list of inputs.
- All protocol hashes route through this facade.

`hash_to_field_le(input)` / `hash_to_field_be(input)`

- Hashes arbitrary bytes to a field element using Keccak-256,
  interpreting the digest with little-endian or big-endian byte order.
- Keccak-256 is used only for this out-of-circuit byte-to-field mapping
  (and for seed expansion in seeded key generation);
  Poseidon is the only hash evaluated inside the circuit.

Boundary equivalents: `ffi_poseidon_hash_pair()`,
`ffi_hash_to_field_le()` / `ffi_hash_to_field_be()`, and
`ffi_uint_to_fr()` (FFI);
`poseidonHashPair()` and `hashToFieldLE()` / `hashToFieldBE()` (WASM).

### Serialization

Serialization is trait-based; there are no free serialization functions.
Three trait pairs cover all protocol types
(all re-exported by the prelude):

- `CanonicalSerialize` / `CanonicalDeserialize` (arkworks):
  **little-endian**, the arkworks/circom native encoding.
- `CanonicalSerializeBE` / `CanonicalDeserializeBE`:
  **big-endian**, matching EVM smart contracts and other on-chain
  consumers. The zkSNARK `Proof` and `PartialProof` are little-endian
  only and have no BE impls.
- `CanonicalSerializeMixed` / `CanonicalDeserializeMixed`:
  for types whose fields have conflicting encoding requirements.
  `RLNProof` is the one such type: it bundles the Groth16 proof,
  which only exists in arkworks compressed LE form,
  with the proof values, which are transmitted BE for on-chain
  consumers. Mixed writes both into a single buffer
  (proof in LE, then values in BE),
  so a complete proof can be sent as one payload.

Usage is uniform across types; endianness is chosen by the trait used:

```rust
// Little-endian (arkworks traits).
let mut le_bytes = Vec::new();
witness.serialize_compressed(&mut le_bytes)?;
let witness = RLNWitnessInput::deserialize_compressed(&le_bytes[..])?;

// Big-endian (Zerokit BE traits).
let mut be_bytes = Vec::new();
CanonicalSerializeBE::serialize(&witness, &mut be_bytes)?;
let witness = <RLNWitnessInput as CanonicalDeserializeBE>::deserialize(&be_bytes[..])?;

// Mixed: a complete RLN proof (Groth16 proof LE + proof values BE) in one buffer.
let rln_proof = RLNProof::new(proof, proof_values);
let mut mixed_bytes = Vec::new();
CanonicalSerializeMixed::serialize(&rln_proof, &mut mixed_bytes)?;
let rln_proof = <RLNProof as CanonicalDeserializeMixed>::deserialize(&mixed_bytes[..])?;
```

Deserialization enforces the same structural invariants as construction
and returns typed validation errors through `SerializationError`.

### WASM-Specific Notes

WASM bindings wrap the Rust API with JavaScript-compatible types. Key differences:

- Field elements are wrapped as `WasmFr`
  (`zero()`, `one()`, `fromUint()`, `fromBytesLE()` / `fromBytesBE()`,
  `toBytesLE()` / `toBytesBE()`, `debug()`).
- Vectors of field elements use `VecWasmFr` with
  `push()`, `get()`, and `length()`.
- Secrets are wrapped as `WasmSecretFr`, which exposes ONLY a redacted
  `debug()` and an `equals()` comparison; raw byte export of a bare secret
  is intentionally not available. Secret persistence goes through
  `WasmIdentityKeys.toBytesLE()` / `toBytesBE()` (whole-struct).
- Identity generation uses `WasmIdentityKeys.generate()` /
  `generateSeeded()` and `WasmExtendedIdentityKeys` equivalents.
- The Merkle path crosses the boundary as `WasmRLNMerkleProof`
  (built with `WasmRLNMerkleProof.new(pathElements, identityPathIndex)`,
  with its own getters and LE/BE serialization),
  mirroring the FFI `FFI_RLNMerkleProof` handle.
- Witness input uses `WasmRLNWitnessInput.newSingle()` / `newMulti()`
  taking a `WasmRLNMerkleProof`;
  proof generation is `WasmRLN.generateProof()` with witness
  calculation handled internally.
- Two-step proving: `generatePartialProof()` / `finishProof()` with
  `WasmRLNPartialWitnessInput` and `WasmRLNPartialProof`;
  a partial witness reuses `witness.getMerkleProof()`.
- The WASM surface is stateless only and exposes **no tree methods**;
  JavaScript supplies the Merkle path data itself.
- When the `parallel` feature is enabled, call `initThreadPool()`
  to initialize the rayon thread pool.
- `initPanicHook()` (with the `panic_hook` feature) installs a console
  panic hook for debugging.
- Errors are returned as JavaScript strings that can be caught via try-catch blocks.

### FFI-Specific Notes

FFI bindings use C-compatible types with the `ffi_` function prefix
(pattern `ffi_<type>_<action>_<variant>`). Key differences:

- Field elements are wrapped as `FFI_Fr`; secrets as the opaque `FFI_SecretFr`
  (redacted debug via `ffi_secret_fr_debug()`, comparison via
  `ffi_secret_fr_eq()`).
- Fallible functions return `FFI_Result<T>` (heap pointer + error string),
  or `FFI_BoolResult` / `FFI_UsizeResult` for bare values;
  errors are C strings in the `err` field.
- All protocol types cross the boundary as opaque handles:
  `FFI_RLN`, `FFI_IdentityKeys`, `FFI_ExtendedIdentityKeys`,
  `FFI_RLNMerkleProof`, `FFI_RLNWitnessInput`, `FFI_RLNPartialWitnessInput`,
  `FFI_RLNProof`, `FFI_RLNPartialProof`, `FFI_RLNProofValues`.
- Memory MUST be explicitly freed with the matching `ffi_*_free` function;
  every owned vector type has one (`ffi_vec_fr_free()`, `ffi_vec_u8_free()`,
  `ffi_vec_bool_free()`, `ffi_vec_usize_free()`);
  strings use `ffi_c_string_free()`.
- Returned strings and byte buffers are **not** NUL-terminated;
  C callers MUST print them with an explicit length (`%.*s`), never `%s`.
- The C header `rln.h` is generated with
  `cargo run --bin generate_headers --features=headers`.

## Usage Patterns

This section describes common deployment scenarios and
the recommended API combinations for each.

### Stateful with Changing Root

Applies when membership changes over time with members joining and slashing continuously.

Applications MUST maintain a sliding window of recent roots externally.
When members are added or removed via `set_leaf()`, `delete_leaf()`, or `atomic_operation()`,
capture the new root using `get_root()` and append it to the history buffer.
Verify incoming proofs using `verify_with_roots()` with the root history buffer,
accepting proofs valid against any recent root.

The window size depends on network propagation delays and epoch duration.

### Stateful with Fixed Root

Applies when membership is established once and remains static during an operation period.

Initialize the tree using `init_tree_with_leaves()` with the complete membership set.
No root history is required.
Verify proofs using `verify_with_signal()`,
optionally combined with `verify_with_roots()` against the single internal root.

### Stateless

Applies when membership state is managed externally,
such as by a smart contract or relay network.

Construct the instance with `RLNBuilder::stateless()`
(or `ffi_rln_new_stateless()` / `WasmRLN.newWithParams()`).
Obtain Merkle proofs and valid roots from the external source.
Wrap externally provided `path_elements` and `identity_path_index` in
`RLNMerkleProof::new()` and pass it to the witness builder.
Verify using `verify_with_roots()` with externally provided roots.

### Two-Step Proving

Applies when proof latency at message time matters.

Build an `RLNPartialWitnessInput` as soon as the identity and Merkle path
are known and call `generate_partial_proof()`.
When the signal arrives, build the full witness and call `finish_proof()`
to obtain `(proof, proof_values)` with reduced critical-path latency.

### Epoch and Rate Limit Configuration

The external nullifier is computed as `poseidon_hash([epoch, rln_identifier])`.
The `rln_identifier` is a field element that uniquely identifies your application (e.g., a hash of your app name).

All values that will be hashed MUST be represented as field elements.
For converting arbitrary data to field elements,
use the `hash_to_field_le()` or `hash_to_field_be()` functions,
which internally use Keccak-256.

Each application SHOULD use a unique `rln_identifier` to
prevent cross-application nullifier collisions.

The `user_message_limit` in the rate commitment determines messages allowed per epoch.
Each `message_id` MUST be less than `user_message_limit` and
SHOULD increment with each message.
In Multi message-id mode a single proof covers a batch of message ids,
with `selector_used` marking the active slots.

Applications MUST persist the `message_id` counter to avoid violations after restarts.

## Security/Privacy Considerations

The security of Zerokit depends on the correct implementation of the RLN-V2 protocol
and the underlying zero-knowledge proof system.
Applications MUST ensure that:

- Identity secrets are kept confidential and never transmitted or logged
- The `message_id` counter is properly persisted to prevent accidental rate limit violations
- External nullifiers are constructed correctly to prevent cross-application attacks
- Merkle tree roots are validated when using stateless mode
- Circuit parameters (zkey and graph data) are obtained from trusted sources;
  production deployments SHOULD run or verify their own trusted setup
  ceremony (Powers of Tau plus circuit-specific phase 2) for the circuit,
  rather than relying solely on the ceremony behind the embedded zkey

Zerokit handles secrets defensively in-process:
all secret field elements are carried as `SecretFr`,
which zeroizes its memory on drop,
cannot be implicitly copied,
and prints a redacted `Debug` representation so secrets never leak into logs.
The FFI boundary keeps secrets behind the opaque `FFI_SecretFr` handle,
and the WASM boundary exposes no raw byte export for a bare secret.
Note that WASM linear memory remains readable by the host page;
this hygiene is best-effort, not isolation.

When using the `parallel` feature in WASM,
applications MUST serve content with the
`Cross-Origin-Opener-Policy: same-origin` and
`Cross-Origin-Embedder-Policy: require-corp` HTTP response headers,
which browsers require before enabling `SharedArrayBuffer`.

The slashing mechanism exposes identity secrets when rate limits are violated.
Applications SHOULD educate users about this risk and
implement safeguards to prevent accidental violations.

## References

### Normative

- [RLN-V1 Specification](../draft/32/rln-v1.md) - Rate Limit Nullifier V1 protocol

### Informative

- [Zerokit GitHub Repository](https://github.com/vacp2p/zerokit) - Reference implementation
- [RLN-V2 Specification](rln-v2.md) - Rate Limit Nullifier V2 protocol
- [Sled Database](https://sled.rs) - Embedded database for persistent Merkle tree storage

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
