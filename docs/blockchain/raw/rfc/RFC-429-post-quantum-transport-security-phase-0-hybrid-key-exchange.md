# [RFC] Post-Quantum Transport Security — phase 0, hybrid key exchange

**Motivation and proposal:** [PR #429](https://github.com/logos-co/logos-lips/pull/429)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-08-28 |
| v2 | Split into the PR description and this RFC document per the template; rebased on master, Blend Protocol row 1.2.2 → 1.5.1; Affected Specifications reduced to the two changed documents, the Service Declaration Protocol, Service Reward Distribution and Cryptarchia rows removed (their rationale stays in Discussion) | 2026-09-14 |
| v3 | Hybrid only: the classical `X25519` fallback is dropped after review, so `X25519MLKEM768` is the only key exchange group a node offers or accepts; rebased on master, Blend Protocol row 1.5.1 → 1.6.2; the dependency constraint updated for the libp2p 0.57 release | 2026-10-09 |
| v4 | After review: the Transport Security section reduced to its rules, the motivation and the restatements of RFC 9001 and the libp2p TLS specification moved here; the Post-Quantum Scope subsection and the `provider_id` identity sentence removed; Blend's Connection Details reduced to a pointer; the dependency corrected to rust-libp2p#6435 or a patched libp2p-tls, since libp2p 0.57 cannot restrict the groups; the implementation list rewritten per implementation, with key logging, Nimbos and the rollout order; `declaration_id` updated to #407 | 2026-11-02 |

## Reviewer Orientation

Read the PR's Motivation first: the PR does two things at once, and only one of them is about post-quantum cryptography. Assumed background: none. Apart from one sentence in the Blend Protocol, the transport handshake had not been specified before, so there is almost no prior text to reconcile against. The specification text is short by design: it states the rules, and this document carries the reasoning.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [P2P Network § Transport Security](#1-key-exchange-p2p-network--transport-security): Key Exchange | One group: `X25519MLKEM768` is offered and accepted, and nothing else. Check that the requirement names no library, and that dropping the classical fallback is acceptable for every implementation on the network. |
| 2 | High | [P2P Network § Transport Security](#2-handshake-and-peer-authentication-p2p-network--transport-security): Handshake, Peer Authentication | First normative statement of the cipher suites and the identity key type. Confirm it describes what is deployed: TLS 1.3, the three suites and the libp2p TLS authentication match libp2p-tls and nim-lsquic today. |
| 3 | Medium | [Blend Protocol § Connection Details](#3-connection-details-blend-protocol) | The one place that already specified connection security. It now points at Transport Security and nothing else; confirm nothing normative is lost. |

# Discussion

## Why hybrid rather than pure ML-KEM

The hybrid derives its secret from both components, so it is secure unless both
are broken. If ML-KEM-768 is found to be weak, X25519 still provides classical
security; if X25519 falls to a quantum adversary, ML-KEM-768 holds. A pure
post-quantum group would trade one single point of failure for another, against
a primitive with far less deployment history. The cost of carrying both is one
X25519 operation.

## Why `X25519MLKEM768` specifically

The parameter set and the classical half were both chosen against measurements
we took ourselves ([`reports/pqc`]), which is what allows the alternatives to be
priced on one basis rather than compared across sources.

**Parameter set.** All three ML-KEM parameter sets were measured on the
reference Raspberry Pi 5 (liboqs, medians):

| | encapsulate | decapsulate | public key | ciphertext |
| --- | ---: | ---: | ---: | ---: |
| ML-KEM-512 | 21 µs | 24 µs | 800 B | 768 B |
| **ML-KEM-768** | **32 µs** | **37 µs** | **1184 B** | **1088 B** |
| ML-KEM-1024 | 48 µs | 55 µs | 1568 B | 1568 B |

The compute differences do not matter at this scale — all three are tens of
microseconds against a handshake measured in milliseconds. The decision is
security level against wire size. ML-KEM-768 is NIST Level 3: 512 is thin for a
protocol constant that will outlive several hardware generations, and 1024 buys
a level nobody is asking for at 480 bytes more per handshake.

**Classical half.** `SecP256r1MLKEM768` exists and is supported by the same
stacks. `X25519` is what the network deploys today, and the classical half of a
hybrid should be the curve already trusted in the deployment rather than a
second one introduced beside it.

**Ecosystem.** `X25519MLKEM768` is the group go-libp2p already advertises and
the one rustls prefers by default, so this is the interoperable choice as well
as the measured one.

**Excluded by measurement.** Classic McEliece is disqualified on receiver cost,
and on the reference Pi 5 the data is unusually blunt about it: decapsulation
costs 25.7 ms to 136.5 ms against ML-KEM-768's 37 µs, a decoder-to-encoder ratio
of 306–526 against 1.17. Flooding its decapsulator buys roughly four orders of
magnitude more receiver CPU per byte sent than anything else measured. (The gap
is architecture-dependent — a vectorised x86 decoder narrows it substantially —
but the reference platform is the Pi, and the exclusion below stands on any
platform.) BIKE, HQC and NTRU have no TLS codepoint and no stack support, so
they are not deployable here whatever their merits.

## Cost

Measured on the reference Raspberry Pi 5, classical against hybrid on the same
stack in the same pass ([`reports/pqc`]):

| | classical | hybrid | ratio |
| --- | ---: | ---: | ---: |
| handshake latency | 1.291 ms | 1.633 ms | ×1.26 |
| handshake bytes | 1518 B | 3782 B | ×2.49 |

Those are **TCP-TLS** figures, and QUIC — which is what we actually run — turns
out to be cheaper. Measured on the real quinn + rustls stack, varying the key
exchange group and nothing else
([`tools/benchmarks/pq-transport/quic-handshake`], logos-blockchain/research#11):

| | `X25519` | `X25519MLKEM768` |
| --- | ---: | ---: |
| client first flight | 1 datagram, 1200 B | **2 datagrams, 2400 B** |
| handshake total | 5202 B | 7653 B — **×1.47** |
| round trips | — | **unchanged** |

Three results, two of which were not guessable in advance.

**No additional round trip.** A packet trace shows the flight structure is
identical in both arms — client flight, server flight, client flight — and only
the number of datagrams per flight changes. On a real link, where handshake
latency is set by round-trip time rather than by CPU, the hybrid group therefore
costs approximately nothing in latency.

**QUIC absorbs part of the size cost: ×1.47 against TCP-TLS's ×2.49.** A QUIC
Initial is padded to at least 1200 bytes whatever it carries, so the classical
handshake is already paying for padding that the hybrid simply fills.

**Anti-amplification is not a constraint, and moves in the defender's favour.**
A QUIC server may not send more than three times what it has received before
validating the peer's address. The larger client flight raises that allowance
from 3600 to 7200 bytes, against 1338 and 2538 actually sent. Neither arm
approaches the limit, and the hybrid has more headroom than the classical one.

*(The wall-clock figure from the QUIC harness is deliberately not quoted here.
On loopback it is dominated by scheduler wakeups, spanning 0.6–2.0 ms across
runs of the same arm on the same machine. The key exchange's CPU cost is small
and is measured properly in the table above.)*

## Bigger is not only a cost

An attacker floods bandwidth, so what bounds a flood is receiver CPU purchased
per byte sent. On the reference Pi 5, X25519 yields 5.2 µs/byte; ML-KEM-768
yields 34 ns/byte — **150× less**. The larger wire objects, normally counted as
the migration's price, are a defensive asset against flooding.

## Why no classical fallback

Earlier revisions kept `X25519` as a second group so that a conforming node
and a peer on the current stack could still connect. Review (PR #429) argued
against it, and this revision drops it, for three reasons.

The property is the point. A node that also offers `X25519` obtains
post-quantum confidentiality only on the connections where the peer supports
the hybrid group, and a peer can always steer a handshake to the classical
group by not offering the hybrid one. The motivation is harvest-now-decrypt-later
protection, for Blend in particular, and "in proportion to adoption" is not a
guarantee Blend can build on.

There is nothing to migrate from. The network is in testnet, so rolling-upgrade
compatibility with older Logos implementations is not a requirement, and other
implementations are expected to follow the transport specification rather than
the specification to follow what they currently ship.

The stacks support the group, but neither restricts to it today. libp2p 0.57
ships the aws-lc-rs provider, whose default group list is `X25519MLKEM768`,
`X25519`, `secp256r1` and `secp384r1`, and libp2p-tls builds that default
provider inside `make_client_config` and `make_server_config` while libp2p-quic
keeps the TLS configuration private. Restricting the groups in the Rust node
therefore needs either the injection seam of
[rust-libp2p#6435](https://github.com/libp2p/rust-libp2p/pull/6435)
(`Config::new_with_provider`) or a patched libp2p-tls. The Nimbos QUIC stack is
backed by BoringSSL, whose defaults are the same four groups; nim-lsquic has to
call `SSL_CTX_set1_group_ids` from an option of its `TLSConfig`, and nim-libp2p
has to pass that option through `QuicTransport.makeConfig`. See Implementation.

The cost is that a peer without the group cannot connect at all, rather than
connecting with classical security. In a testnet whose implementations are all
expected to conform, that is the intended outcome.

## Why this does not touch the Service Declaration Protocol

Worth setting out explicitly, because "post-quantum transition" invites the
assumption that identities are in scope.

`provider_id` is an Ed25519 **signature** key. For a declared provider, SDP
already requires it as the node identity
([SDP § Locators](../bedrock-service-declaration-protocol.md#locators)), it is
embedded in every `Locator`, it signs SDP messages, and Blend's Neighbor
Distinction Process relies on it. The transport section states only that the
identity key is Ed25519: not every connection is a declared provider's. In the
Rust node the main-network swarm uses its own `NETWORK_SWARM` key and only the
Blend swarms use the declared key, and a node without a declaration has no
`provider_id` at all. Since #407, `declaration_id = Hash(service || zk_id)` and
does not involve the identity key.

This PR changes the **key exchange**, which in TLS 1.3 is ephemeral per
handshake and appears in no protocol message outside the handshake. Nothing
SDP-visible moves:

| | changed by this PR |
| --- | --- |
| node identity signature (Ed25519) | no |
| certificate signature | no |
| `declaration_id`, locators, declaration size | no |
| Service Declaration Protocol messages | no |
| service reward distribution | no |
| record-layer AEAD | no |

Service reward distribution is further removed still — rewards are paid to
`zk_id`, which never enters the transport handshake at all.

Authentication is deferred, not overlooked: a signature cannot be forged
retroactively, so an adversary who breaks Ed25519 in the future cannot
impersonate a peer in a handshake that has already completed.

## What the specification does not say

The section states the rules and nothing else. The motivation
(harvest-now-decrypt-later, Blend), the description of the libp2p TLS
certificate and its `libp2p-tls-handshake:` signature, the TLS 1.3 minimum (RFC
9001 §4.2 and the libp2p TLS specification already require it), the codepoint
and share sizes of the group (RFC 8446 and the draft), the anti-amplification
analysis and the phasing all live in this document, so that the specification
describes the current state and not a strategy. The certificate's own key
algorithm is left to the libp2p TLS specification, which already says it should
not be related to the host key.

## The next phase, named but not proposed here

Migrating `provider_id` to a post-quantum signature (ML-DSA) is the natural
next step, and it is a substantially larger change precisely because SDP *is* in
scope: declaration sizes, `declaration_id`, the locator format, and an on-chain
migration for every declared provider. Upstream tracking exists
(rust-libp2p#6462).

Keeping the phases apart is deliberate. "PQ transition" should not read as one
change, and the confidentiality/authentication asymmetry in Motivation is what
justifies doing them in this order rather than together.

# Details

## 1. Key exchange (P2P Network § Transport Security)

Nodes must offer and accept only the key exchange group `X25519MLKEM768`
(IANA named group `0x11EC`). A single group rather than a preference order is
the whole change from the previous revision: with more than one group offered,
a node obtains the property only when its peer also prefers the hybrid group;
with one, there is nothing to negotiate down to, and when the peers share no
group the handshake fails by RFC 8446 §4.1.1.

A node must generate a new key share for every handshake, and must not write
the private keys of the key exchange, or any secret derived from them, to
storage. The derived secrets are named because libp2p-tls 0.7.0 sets
`key_log = KeyLogFile::new()`, so a node started with `SSLKEYLOGFILE` set
writes its traffic secrets to that file.

## 2. Handshake and peer authentication (P2P Network § Transport Security)

First normative statement of what is already deployed: the QUIC handshake is
TLS 1.3 (RFC 9001), nodes support the three TLS 1.3 AEAD cipher suites, peers
authenticate as the libp2p TLS specification describes, and the node identity
key is Ed25519. The section opens with its objective in two sentences and
applies to every libp2p connection a node establishes.

## 3. Connection Details (Blend Protocol)

The Connection Details section read *"TLS 1.3 … the cryptographic scheme is
Ed25519 with ephemeral keys"*, which packs a static identity key together with
two different ephemeral objects. It now points at Transport Security, and keeps
the protocol-name sentence. Nothing normative is lost, and since the paragraph
states no rule of its own, the change is the patch version 1.6.3.

# Implementation

Checked against logos-blockchain master (`4a31f31f4`) and Nimbos `unstable`
(`a7b3cfb`) on 2026-10-29. Already compliant in both: TLS 1.3 only, the three
cipher suites, libp2p TLS authentication, Ed25519 identity. Nimbos sets no
key-log callback.

## Rust node (logos-blockchain)

- [ ]  Upgrade to libp2p 0.57: rebase logos-blockchain#3768 onto master and fix
       its Linux unit tests. The upgrade can land on its own first.
- [ ]  Get a way to set the groups: either patch libp2p-tls with
       `[patch.crates-io]`, setting
       `provider.kx_groups = vec![aws_lc_rs::kx_group::X25519MLKEM768]` in
       `make_client_config` and `make_server_config` (one patch covers the
       three swarms, which all build QUIC through them), or revive
       rust-libp2p#6435 and build QUIC with `Config::new_with_provider` in the
       main-network, Blend core and Blend edge swarms.
- [ ]  Offer and accept only `X25519MLKEM768`, on the dialing and the
       accepting side.
- [ ]  Turn off TLS key logging: drop `KeyLogFile::new()` in the same patch,
       or clear `SSLKEYLOGFILE` before the swarms are built.
- [ ]  Tests: turn `classical_only_peer_still_connects_over_x25519` into a
       rejection test in both directions, and check the negotiated group over
       the real QUIC transport with two nodes, not only the in-memory TLS
       handshake.
- [ ]  Build: aws-lc-sys needs a C toolchain; check the cross-compilation
       targets, the container images and the Nix build. The binary grows by
       about 3.3 MB.

## Nimbos

- [ ]  nim-lsquic: call `SSL_CTX_set1_group_ids(sslCtx,
       [SSL_GROUP_X25519_MLKEM768], 1)` in `setupSSLContext`, as an option of
       `TLSConfig` rather than a default, since other users may still need
       classical peers.
- [ ]  nim-libp2p: pass the groups through `QuicTransport.makeConfig`; Nimbos
       sets them at `withQuicTransport()`.
- [ ]  Bump `vendor/nim-lsquic` and `vendor/nim-libp2p` once both are merged.
- [ ]  Tests: the negotiated group is `X25519MLKEM768`, and a classical-only
       peer is rejected in both directions.

## Both

- [ ]  Rollout order: every Rust node offers only classical groups today, so
       ship the 0.57 upgrade to all Rust nodes first (Nimbos already offers
       the hybrid group), then turn on hybrid-only in each implementation, in
       either order.
- [ ]  Interop test: with hybrid-only on both sides, a Rust node and a Nimbos
       node connect over `X25519MLKEM768`, and each rejects a classical-only
       peer.
- [x]  Measure the QUIC handshake, classical against hybrid: datagrams, first
       flight, flight structure
       ([`tools/benchmarks/pq-transport/quic-handshake`]).
- [ ]  Merge logos-blockchain/research#11, which holds that tool.
- [ ]  Verify both implementations against the final text once the review
       settles.

## Dependency

libp2p 0.57 ships the aws-lc-rs provider with ML-KEM, which the node adopts in
logos-blockchain#3768, but libp2p-tls 0.7.0 fixes the provider's default group
list and libp2p-quic 0.14.0 keeps its TLS configuration private, so the
release alone does not let the Rust node restrict the groups. The dependency
is [rust-libp2p#6435](https://github.com/libp2p/rust-libp2p/pull/6435), open
since May with merge conflicts, or a patched libp2p-tls. Nimbos depends on
the nim-lsquic and nim-libp2p changes above. The specification mandates no
stack.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [P2P Network](../../draft/p2p-network.md#transport-security) | Modified | 1.0.1 → 1.1.0; new Transport Security section, with `X25519MLKEM768` as the only key exchange group |
| [Blend Protocol](../blend-protocol.md#connection-details) | Modified | 1.6.2 → 1.6.3; Connection Details points at Transport Security |

[P2P Network]: ../../draft/p2p-network.md
[Blend Protocol]: ../blend-protocol.md
[`reports/pqc`]: https://github.com/logos-blockchain/research/tree/master/reports/pqc
[`tools/benchmarks/pq-transport/quic-handshake`]: https://github.com/logos-blockchain/research/pull/11
