# RLN-STEALTH-COMMITMENTS

| Field | Value |
| --- | --- |
| Name | RLN Stealth Commitment Usage |
| Slug | 102 |
| Status | raw |
| Category | Standards Track |
| Editor | Aaryamann Challani <p1ge0nh8er@proton.me> |
| Contributors | Jimmy Debe <jimmy@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/rln-stealth-commitments.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/rln-stealth-commitments.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/rln-stealth-commitments.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/rln-stealth-commitments.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/rln-stealth-commitments.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/rln-stealth-commitments.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/raw/rln-stealth-commitments.md) — Fix Files for Linting (#94)
- **2024-08-05** — [`eb25cd0`](https://github.com/logos-co/logos-lips/blob/eb25cd06d679e94409072a96841de16a6b3910d5/vac/raw/rln-stealth-commitments.md) — chore: replace email addresses (#86)
- **2024-04-15** — [`0b0e00f`](https://github.com/logos-co/logos-lips/blob/0b0e00f510f5995b612b4ac8c50c51f9d938dfc8/vac/raw/rln-stealth-commitments.md) — feat(rln-stealth-commitments): add initial tech writeup (#23)

<!-- timeline:end -->

## Abstract

This specification describes the usage of stealth commitments
to add prospective users to a network-governed
[32/RLN-V1](32/rln-v1.md) membership set.

## Motivation

When [32/RLN-V1](32/rln-v1.md) is enforced in [10/Waku2](../../messaging/standards/core/10/waku2.md),
all users are required to register to a membership set.
The membership set will store user identities
allowing the secure interaction within an application.
Forcing a user to do an on-chain transaction
to join a membership set is an onboarding friction,
and some projects may be opposed to this method.
To improve the user experience,
stealth commitments can be used by a counterparty
to register identities on the user's behalf,
while maintaining the user's anonymity.

This document specifies a privacy-preserving mechanism,
allowing a counterparty to utilize [32/RLN-V1](32/rln-v1.md)
to register an `identityCommitment` on-chain.
Counterparties will be able to register members
to a RLN membership set without exposing the user's private keys.

## Background

The [32/RLN-V1](32/rln-v1.md) protocol,
consists of a smart contract that stores a `idenitityCommitment`
in a membership set.
In order for a user to join the membership set,
the user is required to make a transaction on the blockchain.
A set of public keys is used to compute a stealth commitment for a user,
as described in [ERC-5564](https://eips.ethereum.org/EIPS/eip-5564).
This specification is an implementation of the
[ERC-5564](https://eips.ethereum.org/EIPS/eip-5564) scheme,
tailored to the curve that is used in the [32/RLN-V1](32/rln-v1.md) protocol.

This can be used in a couple of ways in applications:

1. Applications can add users
to the [32/RLN-V1](32/rln-v1.md) membership set in a batch.
2. Users of the application
can register other users to the [32/RLN-V1](32/rln-v1.md) membership set.

This is useful when the prospective user does not have access to funds
on the network that [32/RLN-V1](32/rln-v1.md) is deployed on.

## Wire Format Specification

The two parties, the requester and the receiver,
MUST exchange the following information:

```protobuf

message Request {
  // The spending public key of the requester
  bytes spending_public_key = 1;

  // The viewing public key of the requester
  bytes viewing_public_key = 2;
}
```

### Generate Stealth Commitment

The application or user SHOULD generate a `stealth_commitment`
after a request to do so is received.
This commitment MAY be inserted into the corresponding application membership set.

Once the membership set is updated,
the receiver SHOULD exchange the following as a response to the request:

```protobuf

message Response {
  
  // The used to check if the stealth_commitment belongs to the requester
  bytes view_tag = 2;

  // The stealth commitment for the requester
  bytes stealth_commitment = 3;

  // The ephemeral public key used to generate the commitment
  bytes ephemeral_public_key = 4;

}

```

The receiver MUST generate an `ephemeral_public_key`,
`view_tag` and `stealth_commitment`.
This will be used to check the stealth commitment
used to register to the membership set,
and the user MUST be able to check ownership with their `viewing_public_key`.

## Implementation Suggestions

An implementation of the Stealth Address scheme is available in the
[erc-5564-bn254](https://github.com/rymnc/erc-5564-bn254) repository,
which also includes a test to generate a stealth commitment for a given user.

## Security/Privacy Considerations

This specification inherits the security and privacy considerations of the
[Stealth Address](https://eips.ethereum.org/EIPS/eip-5564) scheme.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [10/Waku2](../../messaging/standards/core/10/waku2.md)
- [32/RLN-V1](32/rln-v1.md)
- [ERC-5564](https://eips.ethereum.org/EIPS/eip-5564)
