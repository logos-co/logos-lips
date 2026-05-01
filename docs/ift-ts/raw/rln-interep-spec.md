# RLN-INTEREP-SPEC

| Field | Value |
| --- | --- |
| Name | Interep as group management for RLN |
| Slug | 100 |
| Status | raw |
| Category | Standards Track |
| Editor | Aaryamann Challani <p1ge0nh8er@proton.me> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/rln-interep-spec.md) — chore: add math support (#287)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/rln-interep-spec.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/rln-interep-spec.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/rln-interep-spec.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/rln-interep-spec.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/rln-interep-spec.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/rln-interep-spec.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/raw/rln-interep-spec.md) — Fix Files for Linting (#94)
- **2024-08-05** — [`eb25cd0`](https://github.com/logos-co/logos-lips/blob/eb25cd06d679e94409072a96841de16a6b3910d5/vac/raw/rln-interep-spec.md) — chore: replace email addresses (#86)
- **2024-05-27** — [`99be3b9`](https://github.com/logos-co/logos-lips/blob/99be3b974509ea03561c7ef4b1b02a56f24e9297/vac/raw/rln-interep-spec.md) — Move Raw Specs (#37)
- **2024-02-01** — [`860bae2`](https://github.com/logos-co/logos-lips/blob/860bae20d9eb9f17ac6c3839f939d545bf796835/vac/48/rln-interep-spec.md) — Update rln-interep-spec.md
- **2024-02-01** — [`3f722d9`](https://github.com/logos-co/logos-lips/blob/3f722d945c53b8356be6282f9c20646e099a2122/vac/48/rln-interep-spec.md) — Update and rename README.md to rln-interep-spec.md
- **2024-01-30** — [`ea62398`](https://github.com/logos-co/logos-lips/blob/ea623980770922d0dfe2f861db885ca1ae9dd84e/vac/48/README.md) — Create README.md

<!-- timeline:end -->

## Abstract

This spec integrates [Interep](https://interep.link)
into the [RLN](32/rln-v1.md) spec.
Interep is a group management protocol
that allows for the creation of groups of users and
the management of their membership.
It is used to manage the membership of the RLN group.

Interep ties in web2 identities with reputation, and
sorts the users into groups based on their reputation score.
For example, a GitHub user with over 100 followers is considered to have "gold" reputation.

Interep uses [Semaphore](https://semaphore.appliedzkp.org/)
under the hood to allow anonymous signaling of membership in a group.
Therefore, a user with a "gold" reputation can prove the existence
of their membership without revealing their identity.

RLN is used for spam prevention, and Interep is used for group management.

By using Interep with RLN,
we allow users to join RLN membership groups
without the need for on-chain financial stake.

## Motivation

To have Sybil-Resistant group management,
there are [implementations](https://github.com/vacp2p/rln-contract)
of RLN which make use of financial stake on-chain.
However, this is not ideal because it reduces the barrier of entry for honest participants.

In this case,
honest participants will most likely have a web2 identity accessible to them,
which can be used for joining an Interep reputation group.
By modifying the RLN spec to use Interep,
we can have Sybil-Resistant group management
without the need for on-chain financial stake.

Since RLN and Interep both use Semaphore-style credentials,
it is possible to use the same set of credentials for both.

## Functional Operation

Using Interep with RLN involves the following steps -

1. Generate Semaphore credentials
2. Verify reputation and join Interep group
3. Join RLN membership group via interaction with Smart Contract,
by passing a proof of membership to the Interep group

### 1. Generate Semaphore credentials

Semaphore credentials are generated in a standard way,
depicted in the [Semaphore documentation](https://semaphore.appliedzkp.org/docs/guides/identities#create-deterministic-identities).

### 2. Verify reputation and join Interep group

Using the Interep app deployed on [Goerli](https://goerli.interep.link/),
the user can check their reputation tier and join the corresponding group.
This results in a transaction to the Interep contract, which adds them to the group.

### 3. Join RLN membership group

Instead of sending funds to the RLN contract to join the membership group,
the user can send a proof of membership to the Interep group.
This proof is generated by the user, and
is verified by the contract.
The contract ensures that the user is a member of the Interep group, and
then adds them to the RLN membership group.

Following is the modified signature of the register function
in the RLN contract -

```solidity
    /// @param groupId: Id of the group.
    /// @param signal: Semaphore signal.
    /// @param nullifierHash: Nullifier hash.
    /// @param externalNullifier: External nullifier.
    /// @param proof: Zero-knowledge proof.
    /// @param idCommitment: ID Commitment of the member.
    function register(
        uint256 groupId,
        bytes32 signal,
        uint256 nullifierHash,
        uint256 externalNullifier,
        uint256[8] calldata proof,
        uint256 idCommitment
    )
```

## Verification of messages

Messages are verified the same way as in the [RLN spec](32/rln-v1.md#verification).

## Slashing

The slashing mechanism is the same as in the [RLN spec](32/rln-v1.md#slashing).
It is important to note that the slashing
may not have the intended effect on the user,
since the only consequence is that they cannot send messages.
This is due to the fact that the user
can send a identity commitment in the registration to the RLN contract,
which is different than the one used in the Interep group.

## Proof of Concept

A proof of concept is available at
[vacp2p/rln-interp-contract](https://github.com/vacp2p/rln-interep-contract)
which integrates Interep with RLN.

## Security Considerations

1. As mentioned in [Slashing](#slashing),
the slashing mechanism may not have the intended effect on the user.
2. This spec inherits the security considerations of the [RLN spec](32/rln-v1.md#security-considerations).
3. This spec inherits the security considerations of [Interep](https://docs.interep.link/).
4. A user may make multiple registrations using the same Interep proofs but
different identity commitments.
The way to mitigate this is to check if the nullifier hash has been detected
previously in proof verification.

## References

1. [RLN spec](32/rln-v1.md)
2. [Interep](https://interep.link)
3. [Semaphore](https://semaphore.appliedzkp.org/)
4. [Decentralized cloudflare using Interep](https://ethresear.ch/t/decentralised-cloudflare-using-rln-and-rich-user-identities/10774)
5. [Interep contracts](https://github.com/interep-project/contracts)
6. [RLN contract](https://github.com/vacp2p/rln-contract)
7. [RLNP2P](https://rlnp2p.vac.dev/)
