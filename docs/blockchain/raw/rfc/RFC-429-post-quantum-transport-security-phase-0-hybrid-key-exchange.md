# [RFC] Post-Quantum Transport Security — phase 0, hybrid key exchange

**Motivation and proposal:** [PR #429](https://github.com/logos-co/logos-lips/pull/429)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial PR description | 2026-08-28 |
| v2 | Split into the PR description and this RFC document per the template; rebased on master, Blend Protocol row 1.2.2 → 1.5.1; Affected Specifications reduced to the two changed documents, the Service Declaration Protocol, Service Reward Distribution and Cryptarchia rows removed (their rationale stays in Discussion) | 2026-09-14 |
| v3 | Hybrid only: the classical `X25519` fallback is dropped after review, so `X25519MLKEM768` is the only key exchange group a node offers or accepts; rebased on master, Blend Protocol row 1.5.1 → 1.6.1; the dependency constraint updated for the libp2p 0.57 release | 2026-10-09 |

## Reviewer Orientation

Read the PR's Motivation first: the PR does two things at once, and only one of them is about post-quantum cryptography. Assumed background: none. Apart from one sentence in the Blend Protocol, the transport handshake had not been specified before, so there is almost no prior text to reconcile against.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [P2P Network § Transport Security](#1-key-exchange-p2p-network--transport-security): Key Exchange | One group: `X25519MLKEM768` is offered, and nothing else is offered or accepted. Check that the requirement names no library, and that dropping the classical fallback is acceptable for every implementation on the network. |
| 2 | Critical | [P2P Network § Transport Security](#2-post-quantum-scope-p2p-network--transport-security): Post-Quantum Scope | The claim that nothing SDP-visible moves. This is what confines the change to one phase; if it is wrong, the phasing is wrong. |
| 3 | High | [P2P Network § Transport Security](#3-handshake-and-peer-authentication-p2p-network--transport-security): Handshake, Peer Authentication | First normative statement of TLS version, cipher suites and the authentication model. Confirm it describes what is deployed rather than what we would like. |
| 4 | Medium | [Blend Protocol § Connection Details](#4-connection-details-blend-protocol) | The one place that already specified connection security. Confirm the update loses nothing normative and that the privacy motivation is stated correctly. |

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

The stacks already support it. rustls offers the group and libp2p 0.57 enables
it; the Nimbos QUIC stack is backed by BoringSSL, whose default group list
starts with `X25519_MLKEM768`, so conforming there is a matter of restricting
the offered groups and testing interoperability.

The cost is that a peer without the group cannot connect at all, rather than
connecting with classical security. In a testnet whose implementations are all
expected to conform, that is the intended outcome.

## Why this does not touch the Service Declaration Protocol

Worth setting out explicitly, because "post-quantum transition" invites the
assumption that identities are in scope.

`provider_id` is an Ed25519 **signature** key. It is the node identity, it is
embedded in every `Locator`, it is hashed into
`declaration_id = blake2b(service ‖ provider_id ‖ zk_id ‖ locators)`, and it
signs SDP messages. This PR changes the **key exchange**, which in TLS 1.3 is
ephemeral per handshake, is never persisted, and appears in no protocol message
outside the handshake. Nothing SDP-visible moves: not `provider_id`, not
`declaration_id`, not the locator format, not declaration sizes.

Service reward distribution is further removed still — rewards are paid to
`zk_id`, which never enters the transport handshake at all.

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

Nodes **MUST** offer `X25519MLKEM768` (IANA named group `0x11EC`), **MUST NOT**
offer or accept any other key exchange group, and a handshake in which the peer
offers no hybrid group **MUST** fail.

A single group rather than a preference order is the whole change from the
previous revision. With more than one group offered, a node obtains the property
only when its peer also prefers the hybrid group; with one, there is nothing to
negotiate down to, and the requirement cannot be weakened by configuration.

Key exchange material is ephemeral per handshake and **MUST NOT** be persisted,
reused across connections, or transmitted outside the handshake. No new wire
structure is introduced; the section gives the group codepoints and share sizes.

## 2. Post-Quantum Scope (P2P Network § Transport Security)

States what the phase does not affect, as a table a reviewer can check rather
than infer: the node identity signature, the certificate signature,
`declaration_id`, locators, declaration size, SDP messages, service rewards,
and the record-layer AEAD. Also states what is deliberately deferred
(authentication, until the next phase), that no classical-only group is offered
and therefore no downgrade exists, and why the larger handshake is not an
amplification concern on QUIC.

## 3. Handshake and peer authentication (P2P Network § Transport Security)

First normative statement of what is already deployed: TLS 1.3 only, the three
TLS 1.3 AEAD cipher suites, and the libp2p TLS authentication model — a
self-signed certificate carrying the identity key in the libp2p Public Key
Extension, with the identity key signing `libp2p-tls-handshake:` ‖
`certificate_public_key`.

The node identity key is Ed25519 and is the same key SDP declares as
`provider_id`.

The certificate's own key algorithm is **deliberately left unspecified**. It is
unrelated to the identity key, carries no protocol meaning, and constraining it
would create an interoperability requirement with no corresponding benefit.

## 4. Connection Details (Blend Protocol)

The Connection Details section currently reads *"TLS 1.3 … the cryptographic
scheme is Ed25519 with ephemeral keys"*. That phrase packs a static identity
key together with two different ephemeral objects, and was the likeliest source
of the scoping question this PR had to answer. It is replaced by text that
follows the Transport Security section, states the hybrid requirement, and
names Blend's privacy as its sharpest motivation. Nothing normative is lost:
TLS 1.3 remains stated, and the identity and ephemeral layers are now
distinguished instead of conflated.

# Implementation

- [ ]  Adopt a transport configuration that offers `X25519MLKEM768` and no
       other group (logos-blockchain#3768 adopts the provider; its classical
       fallback is to be removed).
- [ ]  Assert the negotiated group in a test rather than relying on a library
       default.
- [ ]  Verify that a handshake with a peer offering only `X25519` fails.
- [x]  Measure the QUIC handshake, classical against hybrid: datagrams, first
       flight, flight structure
       ([`tools/benchmarks/pq-transport/quic-handshake`]).
- [ ]  Record the build implications of the crypto provider change: a C
       toolchain is required, so check cross-compilation and container images.
- [ ]  Verify the implementation matches the specification: TLS 1.3 only, the
       hybrid group the only one offered or accepted, no key exchange material
       persisted.

## Dependency

When this RFC was first written, no released rust-libp2p carried a TLS crypto
provider with ML-KEM: upstream had merged the change
([rust-libp2p#6568](https://github.com/libp2p/rust-libp2p/pull/6568)) but
`libp2p` 0.56 still fixed the provider to `ring`. libp2p 0.57 has since been
released with the aws-lc-rs provider, and the node adopts it in
logos-blockchain#3768. The specification still mandates no stack; the
provider is an engineering choice, and a C toolchain is now part of the build.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [P2P Network](../../draft/p2p-network.md#transport-security) | Modified | 1.0.1 → 1.1.0; new Transport Security section: the canonical TLS configuration of the stack, with `X25519MLKEM768` as the only key exchange group |
| [Blend Protocol](../blend-protocol.md#connection-details) | Modified | 1.6.0 → 1.6.1; Connection Details follows the new section and states the hybrid requirement with its privacy motivation |

[P2P Network]: ../../draft/p2p-network.md
[Blend Protocol]: ../blend-protocol.md
[`reports/pqc`]: https://github.com/logos-blockchain/research/tree/master/reports/pqc
[`tools/benchmarks/pq-transport/quic-handshake`]: https://github.com/logos-blockchain/research/pull/11
