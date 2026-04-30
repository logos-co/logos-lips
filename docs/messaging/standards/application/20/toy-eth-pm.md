# 20/TOY-ETH-PM

| Field | Value |
| --- | --- |
| Name | Toy Ethereum Private Message |
| Slug | 20 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Franck Royer <franck@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/messaging/standards/application/20/toy-eth-pm.md) — chore: add math support (#287)
- **2026-01-30** — [`d5a9240`](https://github.com/logos-co/logos-lips/blob/d5a9240c6c6c859eddd30742b2251f8a13480cf9/docs/messaging/standards/application/20/toy-eth-pm.md) — chore: removed archived (#283)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/messaging/standards/application/20/toy-eth-pm.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/messaging/standards/application/20/toy-eth-pm.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/waku/standards/application/20/toy-eth-pm.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/waku/standards/application/20/toy-eth-pm.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/waku/standards/application/20/toy-eth-pm.md) — ci: add mdBook configuration (#233)
- **2025-04-09** — [`3b152e4`](https://github.com/logos-co/logos-lips/blob/3b152e44b595456250c0f45288c4e2e6a87774e4/waku/standards/application/20/toy-eth-pm.md) — 20/TOY-ETH-PM: Update (#141)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/waku/standards/application/20/toy-eth-pm.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/waku/standards/application/20/toy-eth-pm.md) — Broken Links + Change Editors (#26)
- **2024-01-31** — [`89a94a5`](https://github.com/logos-co/logos-lips/blob/89a94a5ba9e5d45f2563a9ede5ad4fe976d1cc54/waku/standards/application/20/toy-eth-pm.md) — Update toy-eth-pm.md
- **2024-01-30** — [`c4ff509`](https://github.com/logos-co/logos-lips/blob/c4ff509ce7ba84eaf60d9ddb6e273d0a06fbf32d/waku/standards/application/20/toy-eth-pm.md) — Create toy-eth-pm.md
- **2024-01-30** — [`8841f49`](https://github.com/logos-co/logos-lips/blob/8841f4941ec2efd34126ce297c42722ab437b806/waku/informational/20/toy-eth-pm.md) — Update toy-eth-pm.md
- **2024-01-29** — [`a16a2b4`](https://github.com/logos-co/logos-lips/blob/a16a2b474d8f841f71fed42f6247539daa7c4d53/waku/informational/20/toy-eth-pm.md) — Create toy-eth-pm.md

<!-- timeline:end -->

**Content Topics**:

- Public Key Broadcast: `/eth-pm/1/public-key/proto`
- Private Message: `/eth-pm/1/private-message/proto`

## Abstract

This specification explains the Toy Ethereum Private Message protocol
which enables a peer to send an encrypted message to another peer
over the Waku network using the peer's Ethereum address.

## Goal

Alice wants to send an encrypted message to Bob,
where only Bob can decrypt the message.
Alice only knows Bob's Ethereum Address.

The goal of this specification
is to demonstrate how Waku can be used for encrypted messaging purposes,
using Ethereum accounts for identity.
This protocol caters to Web3 wallet restrictions,
allowing it to be implemented using standard Web3 API.
In the current state,
Toy Ethereum Private Message, ETH-PM, has privacy and features [limitations](#limitations),
has not been audited and hence is not fit for production usage.
We hope this can be an inspiration for developers
wishing to build on top of Waku.

## Design Requirements

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

## Variables

Here are the variables used in the protocol and their definition:

- `B` is Bob's Ethereum address (or account),
- `b` is the private key of `B`, and is only known by Bob.
- `B'` is Bob's Encryption Public Key, for which `b'` is the private key.
- `M` is the private message that Alice sends to Bob.

The proposed protocol MUST adhere to the following design requirements:

1. Alice knows Bob's Ethereum address
2. Bob is willing to participate to Eth-PM, and publishes `B'`
3. Bob's ownership of `B'` MUST be verifiable
4. Alice wants to send message `M` to Bob
5. Bob SHOULD be able to get `M` using [10/WAKU2](../../core/10/waku2.md)
6. Participants only have access to their Ethereum Wallet via the Web3 API
7. Carole MUST NOT be able to read `M`'s content,
even if she is storing it or relaying it
8. [Waku Message Version 1](../26/payload.md) Asymmetric Encryption
is used for encryption purposes.

## Limitations

Alice's details are not included in the message's structure,
meaning that there is no programmatic way for Bob to reply to Alice
or verify her identity.

Private messages are sent on the same content topic for all users.
As the recipient data is encrypted,
all participants must decrypt all messages which can lead to scalability issues.

This protocol does not guarantee Perfect Forward Secrecy nor Future Secrecy:
If Bob's private key is compromised, past and future messages could be decrypted.
A solution combining regular [X3DH](https://www.signal.org/docs/specifications/x3dh/)
bundle broadcast with [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)
encryption would remove these limitations;
See the [Status secure transport specification](https://github.com/status-im/status-specs/tree/master/specs/status/deprecated/secure-transport.md)
for an example of a protocol that achieves this in a peer-to-peer setting.

Bob MUST decide to participate in the protocol before Alice can send him a message.
This is discussed in more detail in
[Consideration for a non-interactive/uncoordinated protocol](#consideration-for-a-non-interactiveuncoordinated-protocol)

## The Protocol

### Generate Encryption KeyPair

First, Bob needs to generate a keypair for Encryption purposes.

Bob SHOULD get 32 bytes from a secure random source as Encryption Private Key, `b'`.
Then Bob can compute the corresponding SECP-256k1 Public Key, `B'`.

### Broadcast Encryption Public Key

For Alice to encrypt messages for Bob,
Bob SHOULD broadcast his Encryption Public Key `B'`.
To prove that the Encryption Public Key `B'`
is indeed owned by the owner of Bob's Ethereum Account `B`,
Bob MUST sign `B'` using `B`.

### Sign Encryption Public Key

To prove ownership of the Encryption Public Key,
Bob must sign it using [EIP-712](https://eips.ethereum.org/EIPS/eip-712) v3,
meaning calling `eth_signTypedData_v3` on his wallet's API.

Note: While v4 also exists, it is not available on all wallets and
the features brought by v4 is not needed for the current use case.

The `TypedData` to be passed to `eth_signTypedData_v3` MUST be as follows, where:

- `encryptionPublicKey` is Bob's Encryption Public Key, `B'`,
in hex format, **without** `0x` prefix.
- `bobAddress` is Bob's Ethereum address, corresponding to `B`,
in hex format, **with** `0x` prefix.

```js
const typedData = {
    domain: {
      chainId: 1,
      name: 'Ethereum Private Message over Waku',
      version: '1',
    },
    message: {
      encryptionPublicKey: encryptionPublicKey,
      ownerAddress: bobAddress,
    },
    primaryType: 'PublishEncryptionPublicKey',
    types: {
      EIP712Domain: [
        { name: 'name', type: 'string' },
        { name: 'version', type: 'string' },
        { name: 'chainId', type: 'uint256' },
      ],
      PublishEncryptionPublicKey: [
        { name: 'encryptionPublicKey', type: 'string' },
        { name: 'ownerAddress', type: 'string' },
      ],
    },
  }
```

### Public Key Message

The resulting signature is then included in a `PublicKeyMessage`, where

- `encryption_public_key` is Bob's Encryption Public Key `B'`, not compressed,
- `eth_address` is Bob's Ethereum Address `B`,
- `signature` is the EIP-712 as described above.

```protobuf
syntax = "proto3";

message PublicKeyMessage {
   bytes encryption_public_key = 1;
   bytes eth_address = 2;
   bytes signature = 3;
}
```

This MUST be wrapped in a [14/WAKU-MESSAGE](/messaging/standards/core/14/message.md) version 0,
with the Public Key Broadcast content topic.
Finally, Bob SHOULD publish the message on Waku.

## Consideration for a non-interactive/uncoordinated protocol

Alice has to get Bob's public Key to send a message to Bob.
Because an Ethereum Address is part of the hash of the public key's account,
it is not enough in itself to deduce Bob's Public Key.

This is why the protocol dictates that Bob MUST send his Public Key first,
and Alice MUST receive it before she can send him a message.

Moreover, nwaku, the reference implementation of [13/WAKU2-STORE](/messaging/standards/core/13/store.md),
stores messages for a maximum period of 30 days.
This means that Bob would need to broadcast his public key
at least every 30 days to be reachable.

Below we are reviewing possible solutions to mitigate this "sign up" step.

### Retrieve the public key from the blockchain

If Bob has signed at least one transaction with his account
then his Public Key can be extracted from the transaction's ECDSA signature.
The challenge with this method is that standard Web3 Wallet API
does not allow Alice to specifically retrieve all/any transaction sent by Bob.

Alice would instead need to use the `eth.getBlock` API
to retrieve Ethereum blocks one by one.
For each block, she would need to check the `from` value of each transaction
until she finds a transaction sent by Bob.

This process is resource intensive and
can be slow when using services such as Infura due to rate limits in place,
which makes it inappropriate for a browser or mobile phone environment.

An alternative would be to either run a backend
that can connect directly to an Ethereum node,
use a centralized blockchain explorer
or use a decentralized indexing service such as [The Graph](https://thegraph.com/).

Note that these would resolve a UX issue
only if a sender wants to proceed with _air drops_.

Indeed, if Bob does not publish his Public Key in the first place
then it MAY be an indication that he does not participate in this protocol
and hence will not receive messages.

However, these solutions would be helpful
if the sender wants to proceed with an _air drop_ of messages:
Send messages over Waku for users to retrieve later,
once they decide to participate in this protocol.
Bob may not want to participate first but may decide to participate at a later stage
and would like to access previous messages.
This could make sense in an NFT offer scenario:
Users send offers to any NFT owner,
NFT owner may decide at some point to participate in the protocol and
retrieve previous offers.

### Publishing the public in long term storage

Another improvement would be for Bob not having to re-publish his public key
every 30 days or less.
Similarly to above,
if Bob stops publishing his public key
then it MAY be an indication that he does not participate in the protocol anymore.

In any case,
the protocol could be modified to store the Public Key in a more permanent storage,
such as a dedicated smart contract on the blockchain.

## Send Private Message

Alice MAY monitor the Waku network to collect Ethereum Address and
Encryption Public Key tuples.
Alice SHOULD verify that the `signature`s of `PublicKeyMessage`s she receives
are valid as per EIP-712.
She SHOULD drop any message without a signature or with an invalid signature.

Using Bob's Encryption Public Key,
retrieved via [10/WAKU2](/messaging/standards/core/10/waku2.md),
Alice MAY now send an encrypted message to Bob.

If she wishes to do so,
Alice MUST encrypt her message `M` using Bob's Encryption Public Key `B'`,
as per [26/WAKU-PAYLOAD Asymmetric Encryption specs](../26/payload.md#asymmetric).

Alice SHOULD now publish this message on the Private Message content topic.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [10/WAKU2](/messaging/standards/core/10/waku2.md)
- [Waku Message Version 1](../26/payload.md)
- [X3DH](https://www.signal.org/docs/specifications/x3dh/)
- [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)
- [Status secure transport specification](https://github.com/status-im/status-specs/tree/master/specs/status/deprecated/secure-transport.md)
- [EIP-712](https://eips.ethereum.org/EIPS/eip-712)
- [13/WAKU2-STORE](/messaging/standards/core/13/store.md)
- [The Graph](https://thegraph.com/)
