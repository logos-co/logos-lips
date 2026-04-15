# 25/LIBP2P-DNS-DISCOVERY

| Field | Value |
| --- | --- |
| Name | Libp2p Peer Discovery via DNS |
| Slug | 25 |
| Status | deleted |
| Category | Standards Track |
| Editor | Hanno Cornelius <hanno@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-02-09** — [`afd94c8`](https://github.com/logos-co/logos-lips/blob/afd94c8bc1420376ae9af7e14a4feb246f2ed621/docs/ift-ts/raw/25/libp2p-dns-discovery.md) — chore: add math support (#287)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/25/libp2p-dns-discovery.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/25/libp2p-dns-discovery.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/25/libp2p-dns-discovery.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/25/libp2p-dns-discovery.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/25/libp2p-dns-discovery.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/25/libp2p-dns-discovery.md) — Fix Files for Linting (#94)
- **2024-03-21** — [`2eaa794`](https://github.com/logos-co/logos-lips/blob/2eaa7949c4abe7d14e2b9560e8c045bf2e937c9a/vac/25/libp2p-dns-discovery.md) — Broken Links + Change Editors (#26)
- **2024-02-08** — [`a3ad14e`](https://github.com/logos-co/logos-lips/blob/a3ad14e6400392ccbc83ab401a605d80a92a6542/vac/25/libp2p-dns-discovery.md) — Create libp2p-dns-discovery.md

<!-- timeline:end -->

`25/LIBP2P-DNS-DISCOVERY` specifies a scheme to implement [`libp2p`](https://libp2p.io/)
peer discovery via DNS for Waku v2.
The generalised purpose is to retrieve an arbitrarily long, authenticated,
updateable list of [`libp2p` peers](https://docs.libp2p.io/concepts/peer-id/)
to bootstrap connection to a `libp2p` network.
Since [`10/WAKU2`](../../../messaging/standards/core/10/waku2.md)
currently specifies use of [`libp2p` peer identities](https://docs.libp2p.io/concepts/peer-id/),
this method is suitable for a new Waku v2 node
to discover other Waku v2 nodes to connect to.

This specification is largely based on [EIP-1459](https://eips.ethereum.org/EIPS/eip-1459),
with the only deviation being the type of address being encoded (`multiaddr` vs `enr`).
Also see [this earlier explainer](https://vac.dev/dns-based-discovery)
for more background on the suitability of DNS based discovery for Waku v2.

## List encoding

The peer list MUST be encoded as a [Merkle tree](https://www.wikiwand.com/en/Merkle_tree).
EIP-1459 specifies [the URL scheme](https://eips.ethereum.org/EIPS/eip-1459#specification)
to refer to such a DNS node list.
This specification uses the same approach, but with a `matree` scheme:

```yaml
matree://<key>@<fqdn>
```

where

- `matree` is the selected `multiaddr` Merkle tree scheme
- `<fqdn>` is the fully qualified domain name on which the list can be found
- `<key>` is the base32 encoding of the compressed 32-byte binary public key
that signed the list.

The example URL from EIP-1459, adapted to the above scheme becomes:

```yaml
matree://AM5FCQLWIZX2QFPNJAP7VUERCCRNGRHWZG3YYHIUV7BVDQ5FDPRT2@peers.example.org
```

Each entry within the Merkle tree MUST be contained within a [DNS TXT record](https://www.rfc-editor.org/rfc/rfc1035.txt)
and stored in a subdomain (except for the base URL `matree` entry).
The content of any TXT record
MUST be small enough to fit into the 512-byte limit imposed on UDP DNS packets,
which limits the number of hashes that can be contained within a branch entry.
The subdomain name for each entry
is the base32 encoding of the abbreviated keccak256 hash of its text content.
See [this example](https://eips.ethereum.org/EIPS/eip-1459#dns-record-structure)
of a fully populated tree for more information.

## Entry types

The following entry types are derived from [EIP-1459](https://eips.ethereum.org/EIPS/eip-1459)
and adapted for use with `multiaddrs`:

## Root entry

The tree root entry MUST use the following format:

```yaml
matree-root:v1 m=<ma-root> l=<link-root> seq=<sequence number> sig=<signature>
```

where

- `ma-root` and `link-root` refer to the root hashes of subtrees
containing `multiaddrs` and links to other subtrees, respectively
- `sequence-number` is the tree's update sequence number.
This number SHOULD increase with each update to the tree.
- `signature` is a 65-byte secp256k1 EC signature
over the keccak256 hash of the root record content,
excluding the `sig=` part,
encoded as URL-safe base64

## Branch entry

Branch entries MUST take the format:

```yaml
matree-branch:<h₁>,<h₂>,...,<hₙ>
```

where

- `<h₁>,<h₂>,...,<hₙ>` are the hashes of other subtree entries

## Leaf entries

There are two types of leaf entries:

### Link entries

For the subtree pointed to by `link-root`,
leaf entries MUST take the format:

```yaml
matree://<key>@<fqdn>
```

which links to a different list located in another domain.

### `multiaddr` entries

For the subtree pointed to by `ma-root`,
leaf entries MUST take the format:

```yaml
ma:<multiaddr>
```

which contains the `multiaddr` of a `libp2p` peer.

## Client protocol

A client MUST adhere to the [client protocol](https://eips.ethereum.org/EIPS/eip-1459#client-protocol)
as specified in EIP-1459,
and adapted for usage with `multiaddr` entry types below:

To find nodes at a given DNS name a client MUST perform the following steps:

1. Resolve the TXT record of the DNS name and
check whether it contains a valid `matree-root:v1` entry.
2. Verify the signature on the root against the known public key
and check whether the sequence number is larger than or
equal to any previous number seen for that name.
3. Resolve the TXT record of a hash subdomain indicated in the record
and verify that the content matches the hash.
4. If the resolved entry is of type:

- `matree-branch`: parse the list of hashes and continue resolving them (step 3).
- `ma`: import the `multiaddr` and add it to a local list of discovered nodes.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [`10/WAKU2`](../../../messaging/standards/core/10/waku2.md)
1. [EIP-1459: Client Protocol](https://eips.ethereum.org/EIPS/eip-1459#client-protocol)
1. [EIP-1459: Node Discovery via DNS](https://eips.ethereum.org/EIPS/eip-1459)
1. [`libp2p`](https://libp2p.io/)
1. [`libp2p` peer identity](https://docs.libp2p.io/concepts/peer-id/)
1. [Merkle trees](https://www.wikiwand.com/en/Merkle_tree)
