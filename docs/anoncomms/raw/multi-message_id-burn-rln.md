# Multi-message_id Burn RLN

| Field | Value |
| --- | --- |
| Name | Multi-message_id burn feature RLN |
| Slug | 141 |
| Status | raw |
| Category | Standards Track |
| Editor | Ugur Sen <ugur@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/anoncomms/raw/multi-message_id-burn-rln.md) — chore: split ift ts specs
- **2026-01-21** — [`70f3cfb`](https://github.com/logos-co/logos-lips/blob/70f3cfb4df4e9a94e56b1284e98ee1dc9df50ac7/docs/ift-ts/raw/multi-message_id-burn-rln.md) — chore: mdbook font fix (#266)

<!-- timeline:end -->

## Abstract

This document specifies multi-message_id burn RLN which the users
can use their multiple message rights at once unlike previous versions of RLN
that require a separate execution per `message_id`.

## Motivation

RLN is a decentralized rate-limiting mechanism designed for anonymous networks.
In [RLNv2](rln-v2.md), the latest version of the protocol, users can apply arbitrary rate limits
by defining a specific limit over the `message_id`.
However, this version does not support the simultaneous exercise
of multiple messaging rights under a single `message_id`.
In other words, if a user needs to consume multiple `message_id` units,
they must compute separate proofs for each one.

This lack of flexibility creates an imbalance: users sending signals
of significantly different sizes still consume only one `message_id` per proof.
While computing multiple proofs is a trivial workaround,
it is neither computationally efficient nor manageable for high-throughput applications.

Multiple burning refers to the mechanism where a fixed number of `message_id` units are processed
within the circuit to generate multiple corresponding nullifiers inside a single cryptographic proof.
This multiple burning feature may unlock the usage of RLN for big signals
such as large messages or complex transactions, by validating their resource consumption in a single proof.

Alternatively, multiple burning could be realized by defining a separate circuit
for each possible number of `message_id` units to be consumed.
While such an approach would allow precise specialization, it would significantly increase
operational complexity by requiring the management, deployment, and verification
of multiple circuit variants.

To avoid this complexity, this document adopts a single, fixed-size but flexible
circuit design, where a bounded number of `message_id` units can be selectively
burned using selector bits.
This approach preserves the simplicity of a single
circuit while enabling efficient multi-burn proofs within a single execution.

This document specifies the mechanism that allows users to burn multiple `message_id` units
at once by slightly modifying the existing [RLNv2](rln-v2.md) circuit.

## Format Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

## Recap of RLNv2

Since the multi-message_id RLN is achieved by modifying the existing RLNv2 protocol,
it is helpful to first recap RLNv2.
Note that this modification only affects the signaling section;
the remaining sections—registration, verification, and slashing—remain identical to RLNv2.

### RLNv2 Registration

RLN-Diff introduces per-user rate limits. Therefore, **id_commitment** must depend on
`user_message_limit`, where
0 ≤ `user_message_limit` ≤ `message_limit`.

The user submits the same `identity_secret_hash` as in
[32/RLN-V1](32/rln-v1.md), i.e.
`poseidonHash(identity_secret)`, together with `user_message_limit` to a server or
smart contract.

The verifier computes
`rate_commitment = poseidonHash(identity_secret_hash, user_message_limit)`,
which is inserted as a leaf in the membership Merkle tree.

### RLNv2 Signalling

For proof generation, the user need to submit the following fields to the circuit:

```js
{
    identity_secret: identity_secret_hash,
    path_elements: Merkle_proof.path_elements,
    identity_path_index: Merkle_proof.indices,
    x: signal_hash,
    message_id: message_id,
    external_nullifier: external_nullifier,
    user_message_limit: message_limit
}
```

Calculating output

The output `[y, internal_nullifier]` is calculated in the following way:

```js

a_0 = identity_secret_hash;
a_1 = poseidonHash([a0, external_nullifier, message_id]);

y = a_0 + x * a_1;

internal_nullifier = poseidonHash([a_1]);

```

### RLNv2 Verification/slashing

Verification and slashing in both subprotocols remain the same as in [32/RLN-V1](32/rln-v1.md).
The only difference that may arise is the `message_limit` check in RLN-Same,
since it is now a public input of the Circuit.

## Multi-message_id Burn RLN (Multi-burn RLN)

The multi-burn protocol follows previous versions by comprising
registration, signaling, and verification/slashing sections.

Since the registration and verification/slashing mechanisms remain unchanged,
this section focuses exclusively on the modifications to the signaling process.

### Multi-burn RLN Signalling

The multi-burn RLN signalling section consists of the proving of the circuit as follows:

Circuit parameters

Public Inputs

* `x`
* `external_nullifier`
* `selector_used []`

Private Inputs

* `identity_secret_hash`
* `path_elements`
* `identity_path_index`
* `message_id []`
* `user_message_limit`

Outputs

* `y []`
* `root`
* `internal_nullifiers []`

The output `(root, y [], internal_nullifiers [])` is calculated in the following way:

```js

a_0 = identity_secret_hash;
a_1i = poseidonHash([a0, external_nullifier, message_id [i]]);

y_i = a_0 + x * a_1i;

internal_nullifiers_i = poseidonHash([a_1i]);

```

where 0 < `i` ≤ `max_out`,  `max_out` is a new parameter that is fixed for a application.
`max_out` is arranged the requirements of the application.
To define this fixed number makes the circuit is flexiable with a single circuit that is maintable.
Since the user is free to burn arbitrary number of `message_id` at once up to `max_out`.

Note that within a given epoch, the `external_nullifier` MUST be identical for all messages
as shown in NULL (unused) output [section](#null-unused-outputs),
as it is computed deterministically from the epoch value and the `rln_identifier` as follows:

```js
external_nullifier = poseidonHash([epoch, rln_identifier]);

```

#### NULL (unused) outputs

Since the number of used `message_id` values MAY be less than `max_out`, the difference
`j = max_out - i`, where `0 ≤ j ≤ max_out − 1`, denotes the number of unused output slots.

These `j` outputs are referred to as **NULL outputs**. NULL outputs carry no semantic meaning and
**MUST** be identical to one another in order to unambiguously indicate that they correspond to
unused `message_id` slots and do not represent valid proofs.

To compute NULL outputs, the circuit makes use of a selector bit array `selector_used []`,
where `selector_used[i] = 1` denotes a used `message_id` slot and `selector_used[i] = 0` denotes
an unused slot.

The `message_id` values MUST NOT be checked in the circuit incrementally (e.g., `1, 2, 3, ...`),
independently of whether a slot is used or unused.
For the best practice the application MAY pass the `message_id` values incrementally and
tracks unused `message_id` values across executions to ensure that subsequent executions
continue from the last assigned `message_id` without reuse or skipping.
The circuit computes the corresponding intermediate values for all slots according to the RLNv2 equations.

For each slot `k`, the final outputs are masked using the selector bits as
follows:

```js

a_0 = identity_secret_hash;
a_1i = poseidonHash([a0, external_nullifier, message_id [i]]);

y_i = selector_used[i] * (a_0 + x * a_1i);

internal_nullifiers_i = selector_used[i] * poseidonHash([a_1i]);

```

Since multiplication by zero yields the additive identity in the field,
all unused slots (`selector_used[k] = 0`) result in
`y[k] = 0` and `internal_nullifiers[k] = 0`, which are interpreted as
NULL outputs and carry no semantic meaning.

As a consequence, the presence of valid-looking `message_id` values in unused
slots does not result in additional burns, as their corresponding outputs are
fully masked and ignored during verification.
Moreover, `message_id` values that are provided to the circuit but correspond to unused slots (`selector_used[k] = 0`)
are not considered consumed and MAY be reused in subsequent proofs in which the corresponding selector bit is set to `1`.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/)

### References

* [RLNv1](32/rln-v1.md)
* [RLNv2](rln-v2.md)
