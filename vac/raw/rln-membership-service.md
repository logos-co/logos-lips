---
title: RLN-MEMBERSHIP-SERVICE
name: RLN Membership Allocation Service
status: raw
category: Standards Track
tags: rln
editor: Arseniy Klempner <arseniyk@status.im>
contributors:
---

## Abstract

This specification defines the RLN Membership Allocation
Service, which registers RLN identity commitments on behalf of clients.
The service enables applications to obtain RLN memberships
without directly interacting with the on-chain membership contract.
It aims to do so while minimizing linkability between the client's
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

The RLN Membership Allocation Service addresses the first concern by acting as an intermediary that registers identity commitments on behalf of clients. Each service provider
can implement their own authentication mechanism to determine client eligibility for membership allocation.

The second concern can be addressed by using a privacy-preserving identity mechanism like [RLN Stealth Commitments](./rln-stealth-commitments.md), which allows the service to register identity commitments on behalf of clients without gaining knowledge of the client's network identity.

## Service Provider Eligibility

A service provider SHOULD deposit sufficient funds in a smart contract to cover the cost of registering at least `min_membership_buffer` RLN memberships.
The service providers smart contract MUST allow depositors to use the deposited funds to register memberships in the RLN membership contract.
The service providers smart contract MUST allow depositors to withdraw their deposited funds.
The service providers smart contract MUST track how many memberships have been registered by a depositor.

## Wire Format Specification

### Discovery

A service provider SHOULD advertise that it offers membership allocation services by participating in the [Logos Capability Discovery protocol](./logos-capability-discovery.md).
A service provider MUST include a list of supported authentication methods in the metadata field of the `Advertisement` message.
A service provider MUST use the protocol ID `/rln/membership/<version>` when generating the `service_id_hash`.
A service provider MAY also advertise support for a specific authentication method by using the protocol ID `/rln/membership/<version>/<authentication_method>`.

A client SHOULD send a `GET_ADS` request for the `/rln/membership/<version>` service to registrars to discover service providers that offer membership allocation services.

### Allocation Request and Response

A client MUST send a message to a service provider to request the allocation of a membership.
A client MUST specify the authentication method to use in the `authentication_type` field.
A client MUST include a payload in the `authentication_payload` field, further defined by the authentication method.
A client MUST include the [identity commitment](../32/rln-v1.md#user-identity) to register in the `identity_commitment` field.

```protobuf
message MembershipAllocationRequest {
    // Indicates which authentication mechanism is used
    bytes authentication_type = 1;

    // Generic payload, further defined by the authentication mechanism
    bytes authentication_payload = 2;
    
    // The identity commitment to register
    bytes identity_commitment = 3;

    // Rate limit for the membership
    uint64 optional rate_limit = 4;
}
```

A service provider MUST respond to the client's request with a `MembershipAllocationResponse` message.
A service provider SHOULD perform basic validation on the identity commitment, such as total bit length.
A service provider SHOULD check if the identity commitment has already been registered in the RLN membership contract.
A service provider SHOULD check if the hash of the request has already been processed in the service provider smart contract.
A service provider MUST deserialize the authentication payload based on the authentication method specified in the `authentication_type` field.
A service provider MUST authenticate the client's request using the authentication payload.
Upon successful authentication, a service provider SHOULD send a transaction to the RLN membership contract with the `identity_commitment` as an argument.
A service provider MUST respond with a `MembershipAllocationResponse` message indicating whether the authentication for the request was accepted.
A service provider MUST respond with a `MembershipAllocationSuccess` message if the transaction to register was successful.
A service provider MUST respond with a `MembershipAllocationFailure` message if the transaction to register was unsuccessful.

```protobuf
message MembershipAllocationResponse {
    // Result of the authentication attempt
    bool auth_success = 1;
    uint64 request_id = 2;
    string optional error = 3;
}

message MembershipAllocationSuccess {
    uint64 request_id = 1;
    // Leaf index in the membership tree
    uint64 leaf_index = 2;
    
    // Current Merkle root after registration
    bytes merkle_root = 3;
    
    // Block number at which registration was confirmed
    uint64 block_number = 4;
    
    // Transaction hash of the registration
    bytes transaction_hash = 5;
}

message MembershipAllocationFailure {
    uint64 request_id = 1;
    string error_message = 2;
}
```

## Registration Flow

The service provider SHOULD construct a hash of the `MembershipAllocationRequest` message and include it when calling the service provider smart contract.
The service provider smart contract MUST include track which request hashes have already been processed by service providers and reject transactions for requests that have already been processed.

### Example Authentication Mechanism

A simple authentication mechanism would require the client to sign a message using a private key for which the associated public address passes some criteria, e.g. held a certain amount of a specific token before a specific block number.

```protobuf
message BasicAuthenticationPayload {
    bytes message = 1;
    bytes signature = 2;
}
```

Depending on the claims being verified, the authentication payload may require additional fields:

```protobuf
message BasicAuthenticationPayload {
    bytes message = 1;
    bytes signature = 2;
    bytes transaction_hash = 3;
    uint64 chain_id = 4;
}
``` 