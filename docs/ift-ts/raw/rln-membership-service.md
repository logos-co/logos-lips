# RLN-MEMBERSHIP-SERVICE

| Field | Value |
| --- | --- |
| Name | RLN Membership Allocation |
| Slug | |
| Status | raw |
| Category | Standards Track |
| Tags | rln |
| Editor | Arseniy Klempner <arseniyk@status.im> |
| Contributors |  |

**Protocol identifier**: `/logos/rln/membership/1.0.0`

## Abstract

This specification defines the RLN Membership Allocation
Protocol, which registers RLN identity commitments on behalf of clients.
The protocol enables membership providers to allocate RLN memberships
to eligible clients without requiring those clients to interact
directly with the on-chain membership contract.
It aims to do so while minimising linkability between the client's
network identity and their RLN identity.
The specification includes a pluggable authentication mechanism
to determine client eligibility for membership allocation.

## Motivation

The Rate Limiting Nullifier (RLN) protocol, as specified in
[32/RLN-V1](./32/rln-v1.md), requires users to register their
identity commitments in a membership Merkle tree before
participating in rate-limited anonymous signaling.
In the standard registration flow, clients submit a transaction
to a smart contract on a blockchain to register their identity commitments.

There are two main concerns with the standard registration flow:

1. This typically requires clients to have a wallet with sufficient funds to
pay for gas fees, and access to a node for the blockchain network.
2. Access to a node is typically done using an RPC provider, which risks
creating a correlation between the client's IP address and their RLN identity.

The RLN Membership Allocation Protocol addresses the first concern by
defining an interaction in which a membership provider registers identity
commitments on behalf of clients. Each membership provider can implement
their own authentication mechanism to determine client eligibility for
membership allocation.

The second concern is out of scope for this specification and is considered
future work. It can be addressed by using a privacy-preserving identity
mechanism like [RLN Stealth Commitments](./rln-stealth-commitments.md),
which would allow the provider to register identity commitments on behalf
of clients without gaining knowledge of the client's network identity.

## Membership Provider Eligibility

A membership provider SHOULD have sufficient funds to register
memberships on behalf of clients at the expected rate for the desired
application.
A membership provider MAY track registered memberships and processed
requests through local accounting, depending on deployment requirements.

## Wire Format Specification

### Membership Allocation Request

```protobuf
message MembershipAllocationRequest {
    // Unique identifier used to correlate requests and responses
    string request_id = 1;

    // Indicates which authentication mechanism is used
    bytes authentication_type = 2;

    // Generic payload, further defined by the authentication mechanism
    bytes authentication_payload = 3;

    // The identity commitment to register
    bytes identity_commitment = 4;

    // Rate limit for the membership
    optional uint64 rate_limit = 5;
}
```

A client who wants to obtain an RLN membership using this protocol
MUST send a `MembershipAllocationRequest` to a relevant membership provider.
A client MUST include a unique `request_id` to correlate the request with
the response.
A client MUST specify the authentication method to use in the
`authentication_type` field.
A client MUST include a payload in the `authentication_payload` field,
further defined by the authentication method.
A client MUST include the
[identity commitment](../32/rln-v1.md#user-identity) to register in the
`identity_commitment` field.
A client MAY include a `rate_limit` value specifying the requested
per-epoch message rate limit for the membership; if omitted, the
membership provider applies its default rate limit. Supported values
are determined by the membership provider and the underlying RLN
membership contract.

Authentication is pluggable: membership providers MAY support any
authentication mechanism, including token-based authentication,
cryptographic signatures over eligibility claims, or demo/testnet
memberships with minimal authentication.

A client MAY retry a `MembershipAllocationRequest` after a suitable
timeout if no response is received. When retrying, the client SHOULD
reuse the same `request_id` so the membership provider can detect
duplicates.

### Membership Allocation Response

```protobuf
message MembershipAllocationResponse {
    string request_id = 1;

    // Result of the authentication attempt
    bool auth_success = 2;

    optional string error = 3;

    oneof result {
        MembershipAllocationSuccess success = 4;
        MembershipAllocationFailure failure = 5;
    }
}

message MembershipAllocationSuccess {
    // Leaf index in the membership tree
    uint64 leaf_index = 1;

    // Current Merkle root after registration
    bytes merkle_root = 2;

    // Block number at which registration was confirmed
    uint64 block_number = 3;

    // Transaction hash of the registration
    bytes transaction_hash = 4;
}

message MembershipAllocationFailure {
    string error_message = 1;
}
```

A membership provider SHOULD respond to the client's request with a
`MembershipAllocationResponse` message.
A membership provider SHOULD perform basic validation on the identity
commitment, such as total bit length.
A membership provider SHOULD check if the identity commitment has already
been registered in the RLN membership contract.
A membership provider SHOULD check if the hash of the request has already
been processed.
A membership provider MUST deserialize the authentication payload based
on the authentication method specified in the `authentication_type` field.
A membership provider MUST authenticate the client's request using the
authentication payload.
Upon successful authentication, a membership provider SHOULD send a
transaction to the RLN membership contract with the `identity_commitment`
as an argument.
A membership provider's response MUST include the `auth_success` field
indicating whether the authentication for the request was accepted.
If the transaction to register was successful, the response MUST include
a `MembershipAllocationSuccess` message in the `result` field.
If the transaction to register was unsuccessful, the response MUST include
a `MembershipAllocationFailure` message in the `result` field.
A membership provider SHOULD include a descriptive error message in the
`error_message` field of `MembershipAllocationFailure` to help clients
diagnose the cause of failure.

## Registration Flow

A membership provider MAY construct a hash of the
`MembershipAllocationRequest` message and use it for local accounting
of processed requests, or include it when calling a provider-specific
smart contract that tracks processed request hashes.

### Example Authentication Mechanism

A simple authentication mechanism would require the client to sign a
message using a private key for which the associated public address passes
some criteria, e.g. held a certain amount of a specific token before a
specific block number.

```protobuf
message BasicAuthenticationPayload {
    bytes message = 1;
    bytes signature = 2;
}
```

Depending on the claims being verified, the authentication payload may
require additional fields:

```protobuf
message OnchainAuthenticationPayload {
    bytes message = 1;
    bytes signature = 2;
    bytes transaction_hash = 3;
    uint64 chain_id = 4;
}
```

## Appendix A: Discovery

A membership provider MAY advertise that it offers membership allocation
services by participating in the
[Logos Capability Discovery protocol](./logos-capability-discovery.md).
A membership provider SHOULD include a list of supported authentication
methods in the metadata field of the `Advertisement` message.
A membership provider MUST use the protocol ID `/rln/membership/<version>`
when generating the `service_id_hash`.
A membership provider MAY also advertise support for a specific
authentication method by using the protocol ID
`/rln/membership/<version>/<authentication_method>`.

A client MAY send a `GET_ADS` request for the `/rln/membership/<version>`
service to registrars to discover membership providers that offer
membership allocation.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [32/RLN-V1](./32/rln-v1.md)
- [RLN Stealth Commitments](./rln-stealth-commitments.md)
- [Logos Capability Discovery protocol](./logos-capability-discovery.md)
