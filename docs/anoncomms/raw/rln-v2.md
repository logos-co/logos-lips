# RLN-V2

| Field | Value |
| --- | --- |
| Name | Rate Limit Nullifier V2 |
| Slug | 106 |
| Status | raw |
| Category | Standards Track |
| Editor | Rasul Ibragimov <curryrasul@gmail.com> |
| Contributors | Lev Soukhanov <0xdeadfae@gmail.com> |

<!-- timeline:start -->

## Timeline

- **2026-05-11** — [`ae4c4a1`](https://github.com/logos-co/logos-lips/blob/ae4c4a11e4f7b0d09cbfd2333e22295d3df56582/docs/anoncomms/raw/rln-v2.md) — chore: split ift ts specs
- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/rln-v2.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/rln-v2.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/rln-v2.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/rln-v2.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/rln-v2.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/rln-v2.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/rln-v2.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/raw/rln-v2.md) — Fix Files for Linting (#94)
- **2024-05-27** — [`99be3b9`](https://github.com/logos-co/logos-lips/blob/99be3b974509ea03561c7ef4b1b02a56f24e9297/vac/raw/rln-v2.md) — Move Raw Specs (#37)
- **2024-02-01** — [`8342636`](https://github.com/logos-co/logos-lips/blob/83426365f7b85619052172be4e55a5f2b9b052a0/vac/58/rln-v2.md) — Update and rename RLN-V2.md to rln-v2.md
- **2024-01-27** — [`d7e84b4`](https://github.com/logos-co/logos-lips/blob/d7e84b4762946426e7317ec43e27dfd0738ec39b/vac/58/RLN-V2.md) — Create RLN-V2.md

<!-- timeline:end -->

## Abstract

The protocol specified in this document is an improvement of [32/RLN-V1](32/rln-v1.md),
being more general construct, that allows to set various limits for an epoch
(it's 1 message per epoch in [32/RLN-V1](32/rln-v1.md))
while remaining almost as simple as it predecessor.
Moreover, it allows to set different rate-limits
for different RLN app users based on some public data,
e.g. stake or reputation.

## Motivation

The main goal of this RFC is to generalize [32/RLN-V1](32/rln-v1.md) and
expand its applications.
There are two different subprotocols based on this protocol:

* RLN-Same - RLN with the same rate-limit for all users;
* RLN-Diff - RLN that allows to set different rate-limits for different users.

It is important to note that by using a large epoch limit value,
users will be able to remain anonymous,
because their `internal_nullifiers` will not be repeated until they exceed the limit.

## Flow

As in [32/RLN-V1](32/rln-v1.md), the general flow can be described by three steps:

1. Registration
2. Signaling
3. Verification and slashing

The two sub-protocols have different flows, and
hence are defined separately.

### Important note

All terms and parameters used remain the same as in [32/RLN-V1](32/rln-v1.md),
more details [here](32/rln-v1.md#technical-overview)

## RLN-Same flow

### Registration

The registration process in the RLN-Same subprotocol does not differ from [32/RLN-V1](32/rln-v1.md).

Signalling

For proof generation, the user needs to submit the following fields to the circuit:

```js
{
    identity_secret: identity_secret_hash,
    path_elements: Merkle_proof.path_elements,
    identity_path_index: Merkle_proof.indices,
    x: signal_hash,
    message_id: message_id,
    external_nullifier: external_nullifier,
    message_limit: message_limit
}
```

Calculating output

The following fields are needed for proof output calculation:

```js
{
    identity_secret_hash: bigint, 
    external_nullifier: bigint,
    message_id: bigint,
    x: bigint, 
}
```

The output `[y, internal_nullifier]` is calculated in the following way:

```js
a_0 = identity_secret_hash
a_1 = poseidonHash([a0, external_nullifier, message_id])

y = a_0 + x * a_1

internal_nullifier = poseidonHash([a_1])
```

## RLN-Diff flow

Registration

**id_commitment** in [32/RLN-V1](32/rln-v1.md) is equal to `poseidonHash(identity_secret)`.
The goal of RLN-Diff is to set different rate-limits for different users.
It follows that **id_commitment** must somehow depend
on the `user_message_limit` parameter,
where 0 <= `user_message_limit` <= `message_limit`.
There are few ways to do that:

1. Sending `identity_secret_hash` = `poseidonHash(identity_secret, userMessageLimit)`
and zk proof that `user_message_limit` is valid (is in the right range).
This approach requires zkSNARK verification,
which is an expensive operation on the blockchain.
2. Sending the same `identity_secret_hash` as in [32/RLN-V1](32/rln-v1.md)
(`poseidonHash(identity_secret)`) and a user_message_limit publicly to a server
 or smart-contract where
`rate_commitment` = `poseidonHash(identity_secret_hash, userMessageLimit)` is calculated.
The leaves in the membership Merkle tree would be the rate_commitments of the users.
This approach requires additional hashing in the Circuit, but
it eliminates the need for zk proof verification for the registration.

Both methods are correct, and the choice of the method is left to the implementer.
It is recommended to use second method for the reasons already described.
The following flow description will also be based on the second method.

Signalling

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

The Output is calculated in the same way as the RLN-Same sub-protocol.

### Verification and slashing

Verification and slashing in both subprotocols remain the same as in [32/RLN-V1](32/rln-v1.md).
The only difference that may arise is the `message_limit` check in RLN-Same,
since it is now a public input of the Circuit.

### ZK Circuits specification

The design of the [32/RLN-V1](32/rln-v1.md) circuits
is different from the circuits of this protocol.
RLN-v2 requires additional algebraic constraints.
The membership proof and Shamir's Secret Sharing constraints remain unchanged.

The ZK Circuit is implemented using a [Groth-16 ZK-SNARK](https://eprint.iacr.org/2016/260.pdf),
using the [circomlib](https://docs.circom.io/) library.
Both schemes contain compile-time constants/system parameters:

* DEPTH - depth of membership Merkle tree
* LIMIT_BIT_SIZE - bit size of `limit` numbers,
e.g. for the 16 - maximum `limit` number is 65535.

The main difference of the protocol is that instead of a new polynomial
(a new value `a_1`) for a new epoch, a new polynomial is generated for each message.
The user assigns an identifier to each message;
the main requirement is that this identifier be in the range from 1 to `limit`.
This is proven using range constraints.

### RLN-Same circuit

#### Circuit parameters

Public Inputs

* `x`
* `external_nullifier`
* `message_limit` - limit per epoch

Private Inputs

* `identity_secret_hash`
* `path_elements`
* `identity_path_index`
* `message_id`

Outputs

* `y`
* `root`
* `internal_nullifier`

### RLN-Diff circuit

In the RLN-Diff scheme, instead of the public parameter `message_limit`,
a parameter is used that is set for each user during registration (`user_message_limit`);
the `message_id` value is compared to it in the same way
as it is compared to `message_limit` in the case of RLN-Same.

Circuit parameters

Public Inputs

* `x`
* `external_nullifier`

Private Inputs

* `identity_secret_hash`
* `path_elements`
* `identity_path_index`
* `message_id`
* `user_message_limit`

Outputs

* `y`
* `root`
* `internal_nullifier`

## Appendix A: Security considerations

Although there are changes in the circuits,
this spec inherits all the security considerations of [32/RLN-V1](32/rln-v1.md).

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

* [1](https://zkresear.ch/t/rate-limit-nullifier-v2-circuits/102)
* [2](https://github.com/Rate-Limiting-Nullifier/rln-circuits-v2)
* [3](32/rln-v1.md#technical-overview)
