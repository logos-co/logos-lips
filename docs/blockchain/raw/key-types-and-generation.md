# KEY-TYPES-AND-GENERATION

| Field | Value |
| --- | --- |
| Name | Key Types and Generation |
| Slug | 84 |
| Status | raw |
| Category | Standards Track |
| Editor | Mehmet Gonen <mehmet@logos.co> |
| Contributors | Marcin Pawlowski <marcin@logos.co>, Youngjoon Lee <youngjoon@logos.co>, Alexander Mozeika <alexander@logos.co>, Thomas Lavaur <thomas@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/key-types-and-generation.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/key-types-and-generation.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/key-types-and-generation.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/key-types-and-generation.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-04-09 |
| 1.0.1 | [RFC] Remove Concept of a Session | 2026-06-22 |

# Introduction

This document defines the key types used in the Blend protocol and describes the process of generating them.

# Overview

This document ensures that the keys are used and generated in a common manner, which is necessary for making the Blend protocol work. The keys include:

- **Non-ephemeral Quota Key (NQK)** — used for proving that a node is a core node.
- **Non-ephemeral Signing Key (NSK)** — used to authenticate the node on the network level and derive the Non-ephemeral Encryption Key.
- **Ephemeral Signing Key (ESK)** — used for signing Blend messages, one per encapsulation.
- **Non-ephemeral Encryption Key (NEK)** — used for deriving shared secrets for message encryption.
- **Ephemeral Encryption Key (EEK)** — used for encrypting Blend messages, one per encapsulation.

# Construction

## Non-ephemeral Quota Key

A node generates a Non-ephemeral Quota Key (NQK) that is a ZkSignature ([Zero Knowledge Signature Scheme (ZkSignature)](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature)). The NQK is stored on the ledger as the `zk_id` field in the `DeclarationInfo` of the node’s outcome of the participation in the Service Declaration Protocol (SDP — [Service Declaration Protocol](bedrock-service-declaration-protocol.md)).

The NQK is used to prove that the node is part of the set of core nodes as indicated through the SDP.

## Non-ephemeral Signing Key

A node generates a Non-ephemeral Signing Key (NSK) that is a Ed25519 key. The NSK is stored on the ledger as the `provider_id` field in the `DeclarationInfo` of the node’s outcome of the participation in the Service Declaration Protocol (SDP — [Service Declaration Protocol](bedrock-service-declaration-protocol.md)).

The NSK is used to authenticate the node on the network level and to derive Non-ephemeral Encryption Key.

## Ephemeral Signing Key

A node generates Ephemeral Signing Keys (ESK) that are proved to be limited in number by the Proof of Quota (PoQ — [Proof of Quota](proof-of-quota.md)). The PoQ for core nodes requires a valid NQK for the epoch for which the PoQ is generated.

A unique signing key must be generated for every encapsulation as required by the [Message Encapsulation Mechanism](message-encapsulation.md).

The key must not be reused. Otherwise, the messages that reuse the same key can be linked together. The node is responsible for not reusing the key.

## Non-ephemeral Encryption Key

A node generates a Non-ephemeral Encryption Key (NEK). It is an X25519 curve key derived from the NSK (Ed25519) public key retrieved from the `provider_id`, which is stored on the ledger when the node executes the SDP protocol.

The NEK key is used for deriving a shared secret (alongside EEK defined below) for the Blend message encapsulation purposes.

## Ephemeral Encryption Key

A node derives an Ephemeral Encryption Key (EEK) pair using the X25519 curve from the ESK.

A unique encryption key must be generated for every encapsulation as required by the [Message Encapsulation Mechanism](message-encapsulation.md).

The derivation of a shared secret for the encryption of an encapsulated message requires using the EEK of the sender and the derived X25519 key from the NEK of the recipient.

The key must not be reused. Otherwise, the messages that reuse the same key can be linked together. The node is responsible for not reusing the key.
