# RLN-API

| Field | Value |
| --- | --- |
| Name | RLN Module API |
| Status | raw |
| Category | Standards Track |
| Tags | rln, membership, spam-protection, api |
| Editor | Tanya Stubbs <tanya@status.im>, Arseniy Klempner <arseniyk@status.im> |

## Abstract

This document specifies the RLN Module:
a registry-agnostic API that manages
[RLN](https://lip.logos.co/anoncomms/raw/rln-v2.html) memberships —
registration, persistence, and lifecycle state —
and generates and verifies RLN proofs
on behalf of consuming services.
Registries are identified by
[CAIP-10](https://standards.chainagnostic.org/CAIPs/caip-10) account identifiers
and applications by their `rln_identifier`;
together they scope every call,
so one Module serves multiple memberships, registries and applications concurrently.

## Motivation

[RLN](https://lip.logos.co/anoncomms/raw/rln-v2.html) requires a user
to register an identity commitment in a membership set
before participating in rate-limited anonymous signalling.
At the time of writing, existing specifications assume that set
is a smart contract on an EVM-compatible blockchain —
the links below are pinned to the versions this refers to:
[WAKU2-RLN-CONTRACT](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/core/raw/rln-contract.md)
specifies the contract,
[MESSAGING-API](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/application/raw/messaging-api.md) configures validation
through an EVM-specific `RlnConfig`,
and [RLN-KEYSTORE](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/application/raw/rln-keystore.md) identifies a registry
by chain id and contract address.
Registries now exist, and will continue to appear,
in other execution environments.

Supporting memberships that live in different registries,
acquired in different ways,
means generalizing registry identification and
concentrating the registry-specific work in a module
that consuming services do not themselves implement.
This document defines that Module, so that:

- the registry backing a deployment is selected by configuration, not by code;
- a consumer manages memberships and generates and verifies proofs
  through one stable interface,
  independent of how the Module packages its internals;
- payment and account handling remain below the Module,
  invisible to the consumer.

## Semantic

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Terminology

| Term | Meaning |
| --- | --- |
| Module | The component implementing this interface. Exposes a membership-management portion and a rate-limiting portion. |
| Consumer | The component calling this interface — e.g. a relay node implementing [WAKU2-RLN-RELAY](https://lip.logos.co/messaging/core/draft/17/rln-relay.html), a mix node, or a light client. |
| Application | A network or protocol deployment that verifies RLN proofs against a registry, identified by an `rln_identifier`. |
| Registry | A membership set — a Merkle tree of rate commitments — identified by a CAIP-10 `registry_id`; a smart contract, an on-chain program, or any other service maintaining such a tree. Internal registry access is the Module's concern. |
| `registry_id` | `<namespace>:<reference>:<account_address>`, e.g. `eip155:59144:0xb9cd…` or `logos:testnet:<64 lowercase hex>`. MUST be canonicalized before comparison or hashing. |
| `rln_identifier` | A 32-byte per-application identifier ([32/RLN-V1](https://github.com/logos-co/logos-lips/blob/master/docs/anoncomms/draft/32/rln-v1.md)), mixed into the external nullifier so one membership can serve several applications. |
| Scope | The context a call operates on — a registry and an application: `registry_id` + `rln_identifier` (`MembershipScope`). |
| Identity commitment | The public value derived from an identity credential ([RLN](https://lip.logos.co/anoncomms/raw/rln-v2.html)); the only credential-derived value that appears in the registry. |
| Rate commitment | `poseidon(identity_commitment, rate_limit)` — a registry tree leaf. |
| Direct registration | The Module registers a membership itself, from a funded account. |
| Delegated registration | The Module registers on a client's behalf as a participant in the [RLN Membership Allocation Protocol](https://lip.logos.co/anoncomms/raw/rln-membership-service.html). |

## Registry identification

A `registry_id` is a [CAIP-10](https://standards.chainagnostic.org/CAIPs/caip-10)
account identifier, `namespace:reference:account_address`,
that MUST uniquely identify a single registry instance.
A registry deployment typically spans several accounts —
the contract or program, its configuration, the tree accounts —
so each namespace binding MUST define which single account anchors the registry
(the account from which its other objects can be resolved)
and one canonical textual form for `account_address`, including letter case.

The `registry_id` is compared as an opaque string
and is an input to the `membership_hash`,
so implementations MUST canonicalize it before comparing or hashing,
and MUST NOT require the ability to parse the `account_address`
of namespaces they do not support.
The namespace binding for `logos` registries is given in
[Appendix A](#appendix-a-the-logos-namespace-binding).

## API design

### The Module

An instance of the Module serves the registries selected by its configuration;
every call names the registry and application context it operates on
through a `MembershipScope`.
It exposes two portions:

- **Membership management** — registration and membership state:
  the Module generates the identity credential,
  registers its rate commitment,
  persists it,
  and tracks the membership's lifecycle in the registry.
- **Rate limiting** — proof generation and verification
  over state the Module maintains itself:
  the current epoch, message-id allocation,
  the membership's Merkle proof path, the valid-root window,
  and the nullifier log for double-signalling detection.

The consumer supplies only scopes, signals, and proofs.
Registry access and payment — the latter via an accounts module beneath the Module —
are internal to the Module and out of scope here.
Identity credentials never leave the Module:
they are generated at registration, persisted encrypted,
and used only inside proof generation.

## Type definitions

### Common types

```c

typedef struct { const uint8_t* ptr; size_t len; } Bytes;

// The minimum set of conditions an error result MUST distinguish.
typedef enum {
    RLN_ERR_NOT_READY,         // Module cannot serve this yet; retry once ready
    RLN_ERR_TRANSIENT,         // e.g. registry/RPC failure; the caller MAY retry
    RLN_ERR_BUDGET_EXHAUSTED,  // the epoch's rate limit is spent; retry next epoch
    RLN_ERR_PERMANENT          // e.g. invalid input; retrying cannot succeed
} RlnErrorKind;

// An error: the kind the caller dispatches on,
// and a human-readable detail for diagnostics.
typedef struct {
    RlnErrorKind kind;
    const char*  message;
} RlnError;

// Result<T> denotes a fallible return carrying either a T or an RlnError,
// never both. The notation is language-neutral: a binding maps it onto its
// native idiom — a Rust Result, a C value-plus-error struct, an exception —
// preserving the RlnErrorKind distinctions.

// Everything a call operates on: the registry and the application context.
// Every call passes its scope explicitly; the Module holds no default.
typedef struct {
    const char* registry_id;         // CAIP-10 account identifier, canonicalized,
                                     // e.g. "eip155:59144:0xb9cd..."
    uint8_t     rln_identifier[32];  // per-application identifier, mixed into
                                     // the external nullifier
} MembershipScope;

// Open registration options. The common key "rate_limit" carries the
// requested per-epoch rate limit as a decimal string; omitted, the
// registry applies its default. All other recognized keys are
// registry-specific, e.g. selecting delegated registration through
// an allocation service.
typedef struct { const char* key; const char* value; } RegistryOption;
typedef struct { const RegistryOption* ptr; size_t len; } RegistryOptions;

// A consistent snapshot of one scope's rate-limit budget.
typedef struct {
    uint64_t epoch_index;  // current epoch
    uint64_t rate_limit;   // messages the epoch grants the membership;
                           // zero when the scope has no usable membership
    uint64_t remaining;    // messages still unspent in this epoch
} EpochQuota;

```

### Membership

```c

typedef enum {
    MEMBERSHIP_UNKNOWN,                   // no membership known for the scope
    MEMBERSHIP_PENDING,                   // submitted, not yet confirmed by the registry
    MEMBERSHIP_FAILED,                    // observed absent after the confirmation window
    MEMBERSHIP_ACTIVE,                    // confirmed and within its validity period
    MEMBERSHIP_GRACE_PERIOD,              // still usable, but approaching expiry
    MEMBERSHIP_EXPIRED,                   // validity period lapsed
    MEMBERSHIP_ERASED_AWAITS_WITHDRAWAL,  // removed; deposit still recoverable
    MEMBERSHIP_ERASED                     // removed; nothing left to recover
} MembershipStatus;

// Membership metadata. The identity credential backing it is generated,
// persisted, and used only inside the Module; it never crosses this interface.
typedef struct {
    const char* membership_hash;  // stable one-way local handle,
                                  // lowercase_hex(SHA256(registry_id || 0x00 || identity_commitment))
    uint64_t    rate_limit;       // messages per epoch; provisional while PENDING
    uint64_t    leaf_index;       // index of the rate commitment in the tree;
                                  // meaningful once ACTIVE
} Membership;

typedef struct {
    MembershipStatus status;
    Membership       membership;  // meaningful unless status is UNKNOWN
} MembershipState;

```

A membership belongs to exactly one registry
and carries no application association:
it MAY back any application whose scope names its registry,
which is why a `MembershipScope` pairs the `registry_id` with an `rln_identifier`.

`PENDING` and `FAILED` are Module-local states:
accepting a submission confirms the registry received the registration,
not that it applied it.
A membership MUST NOT remain `PENDING` indefinitely —
the Module bounds it with a confirmation window (see [`register`](#registration)),
after which a membership observed absent is reported `FAILED`.
While `PENDING`, `rate_limit` and `leaf_index` are provisional:
the registry assigns the leaf position when the registration is applied,
so the Module MUST re-read both once the membership is `ACTIVE`.

A membership MAY leave the set involuntarily.
Where a registry implements slashing —
which removes the leaf and publicly reveals the identity secret
([32/RLN-V1](https://github.com/logos-co/logos-lips/blob/master/docs/anoncomms/draft/32/rln-v1.md)) —
an `ACTIVE` membership can disappear at any time.
A registry that erases all record of a membership on removal
makes `ERASED` indistinguishable from never-registered in a raw read,
so the Module infers erasure from its own records.
A membership reported `ERASED` or `UNKNOWN` no longer backs proof generation:
[`generate_proof`](#rate-limiting) requires a usable membership.

The `membership_hash` is derived deterministically from
the canonical `registry_id` and the credential's identity commitment,
and from nothing else —
in particular not from provisional values such as `leaf_index` —
so that Modules sharing a storage backend agree on it.
The construction is given in
[Appendix B](#appendix-b-membership-hash-construction).

### Rate-limit proof

```c

typedef struct {
    uint8_t proof[128];              // zero-knowledge proof, compressed encoding
    uint8_t root[32];                // root the proof was generated against
    uint8_t epoch[32];               // epoch the proof was generated for,
                                     // little-endian field element
    uint8_t external_nullifier[32];  // poseidon(hash_to_field_le(epoch),
                                     //          hash_to_field_le(rln_identifier))
    uint8_t share_x[32];             // hash_to_field_le(signal) —
                                     // the share's evaluation point
    uint8_t share_y[32];             // Shamir share of the identity secret,
                                     // evaluated at share_x
    uint8_t nullifier[32];           // deterministic fingerprint of (identity
                                     // secret, external_nullifier, message_id)
} RateLimitProof;

typedef enum {
    PROOF_VALID,                // all verification conditions hold
    PROOF_INVALID,              // a verification condition fails
    PROOF_DUPLICATE,            // a proof for a signal already verified
    PROOF_RATE_LIMIT_VIOLATION  // nullifier reuse with a different signal
} ProofVerdict;

typedef struct {
    ProofVerdict verdict;
    uint8_t      recovered_secret[32];  // the double-signaller's identity secret,
                                        // reconstructed from the colliding shares;
                                        // set only on PROOF_RATE_LIMIT_VIOLATION
} VerificationResult;

```

A `RateLimitProof` is opaque to the consumer,
which passes it from [`generate_proof`](#rate-limiting) to
[`verify_proof`](#rate-limiting) unchanged;
its fields follow [RLN](https://lip.logos.co/anoncomms/raw/rln-v2.html).
Two proofs that share an external nullifier and message id
expose `share_x`/`share_y` pairs that reconstruct the identity secret —
the mechanism the rate limit rests on.
`verify_proof` performs that reconstruction when it detects the collision
and reports the secret in its result.
The `recovered_secret` is the violator's,
revealed by their own double-signalling —
not a credential of the Module's,
which never crosses this interface.

## Required functions

The Module SHALL expose the functions in this section.
Every function returns a `Result`:
its declared value on success, an `RlnError` otherwise.
A function called before the Module can serve it
SHALL fail with `RLN_ERR_NOT_READY`
rather than be served from a cold registry view.

### Lifecycle

#### `start()`

Start the Module with its configuration,
which selects the registries the instance serves.
Starting establishes the registry connections,
loads persisted memberships (see [Persistence](#persistence)),
and starts the tasks that maintain the Module's local registry view:
the valid-root window, each membership's Merkle proof path, and each membership's state.
The Module does not require a membership to start:
a Module started without one serves [`verify_proof`](#rate-limiting)
from its registry view alone.

#### `stop()`

Stop the Module and all its maintenance tasks.
In-flight requests SHALL be cancelled cleanly.

### Registration

#### `Result<MembershipState> register(MembershipScope scope, RegistryOptions options)`

Generate a new identity credential inside the Module,
attempt to register a membership for it,
and persist the credential and membership (see [Persistence](#persistence)).
The membership's rate limit is requested through the common option key
`rate_limit`:
absent, the registry, or the allocation service under delegated registration,
applies its default;
present, it is a request, not a guarantee:
a registry MAY grant a different value,
which the membership reports once `ACTIVE`
(its `rate_limit` is provisional while `PENDING`).
A requested `rate_limit` outside the registry's accepted bounds
SHALL fail as `RLN_ERR_PERMANENT`.
Only the rate commitment derived from the credential is submitted to the registry;
the credential itself never leaves the Module.
The remaining `options` keys carry registry-specific registration choices —
for example, selecting delegated registration through the
[RLN Membership Allocation Protocol](https://lip.logos.co/anoncomms/raw/rln-membership-service.html)
rather than direct registration from a funded account.

`register` is idempotent for a scope:
if the scope already has a membership that is `PENDING`, `ACTIVE`,
or in its `GRACE_PERIOD`,
the function SHALL return that membership
rather than generate a second credential or double-register,
and its `rate_limit` MAY differ from any requested value.
A membership in a terminal state — `FAILED`, `EXPIRED`,
`ERASED_AWAITS_WITHDRAWAL`, or `ERASED` —
does not block registration:
the function SHALL register a fresh membership for the scope,
and a prior recoverable deposit remains claimable through
[withdrawal](#optional-extensions).
Holding more than one live membership for a scope is an
[optional extension](#optional-extensions).

Registration is not instantaneous — on some registries confirmation takes minutes —
so the function SHALL return once the registration is submitted and durably persisted,
with the membership `PENDING`
and its `rate_limit` and `leaf_index` provisional.
Confirmation is observed through [`get_membership_state`](#registration),
which transitions to `ACTIVE` once the registration is confirmed in the registry.
The transition to `FAILED` SHALL be based on a successful registry read
observing the membership absent after the confirmation window;
inability to reach the registry is not such an observation,
and the membership SHALL remain `PENDING` while the registry cannot be read.
A failed submission SHALL be reported as `RLN_ERR_TRANSIENT` or `RLN_ERR_PERMANENT`
according to whether retrying can succeed.

#### `Result<MembershipState> get_membership_state(MembershipScope scope)`

Return the status and metadata of the scope's membership,
whether registered in this run or loaded from persistence at `start()`.
The reported status is the registry's view overlaid on the Module's local records:
a submission the registry does not yet know about
is reported `PENDING` or `FAILED` rather than `UNKNOWN`,
and — symmetrically — a membership the Module has previously observed in the set
that the registry no longer reports is `ERASED` rather than `UNKNOWN`.
`UNKNOWN` is returned only when no membership exists for the scope,
in this run or in persistence.

### Persistence

The Module SHALL persist each membership it registers,
so that a membership registered before a restart is available after it
without registering again.
The store SHALL satisfy:

- identity credentials are encrypted at rest;
- when the encryption key is password-derived,
  the derivation uses a function suitable for password hashing
  (e.g. PBKDF2, [RFC 2898](https://www.ietf.org/rfc/rfc2898.txt));
- tampering with a stored credential is detectable before it is used;
- plaintext identity secrets are never exposed outside the Module.

The storage medium and encoding are the Module's concern.
A keystore format portable across implementations is an
[optional extension](#optional-extensions);
identity secrets held in memory are covered by the
[security considerations](#security-and-privacy-considerations).

### Rate limiting

The rate-limiting portion is the proof functions and a quota read.
All RLN state they need —
the current epoch, message-id allocation within the rate limit,
the membership's Merkle proof path, the valid-root window,
and the nullifier log for double-signalling detection —
is maintained inside the Module;
the consumer supplies only the scope and the signal.
A membership is required only to generate proofs:
verification runs against the registry view alone,
so a consumer that only validates messages never registers.
Detecting double-signalling across messages —
two proofs sharing a nullifier within one epoch —
is the Module's responsibility:
it keeps a log of the nullifiers it has verified, with their shares,
recovers the identity secret two colliding proofs reveal,
and reports it in the verification result.

#### `Result<EpochQuota> get_epoch_quota(MembershipScope scope)`

Return the scope's current epoch index,
the membership's `rate_limit` for it,
and the budget still unspent in it,
for consumer-side send scheduling:
rolling a metering window on the epoch boundary,
parking traffic when the budget is spent,
and releasing it when the epoch advances.
All fields SHALL derive from one observation of the epoch:
a `remaining` computed in one epoch MUST NOT be paired
with the index of another,
so a read taken across an epoch rollover reflects
either the old epoch or the new one, never a mixture.
The read is advisory:
allocation happens in [`generate_proof`](#rate-limiting),
which remains the authority and fails with `RLN_ERR_BUDGET_EXHAUSTED`
when the budget is spent between a read and a proof.
A scope without a usable membership — `ACTIVE` or `GRACE_PERIOD` — has no budget:
the read SHALL return the current `epoch_index`
with `rate_limit` and `remaining` both zero.
A `rate_limit` of zero therefore indicates the absence of a usable membership,
never an exhausted budget,
and the consumer resolves which through
[`get_membership_state`](#registration).

#### `Result<RateLimitProof> generate_proof(MembershipScope scope, Bytes signal)`

Generate an RLN proof that `signal` was produced by the holder of the scope's membership
within its rate limit for the current epoch.
The Module determines the epoch,
allocates the next unused `message_id` within the membership's `rate_limit`,
and binds the proof to the external nullifier
`poseidon(hash_to_field_le(epoch), hash_to_field_le(rln_identifier))`.
The Module SHALL NOT issue two proofs for the same `(epoch, message_id)` pair:
doing so reveals the identity secret.
When the epoch's budget is exhausted,
the function SHALL fail with `RLN_ERR_BUDGET_EXHAUSTED`;
allocation resets at the next epoch.
The membership MUST be usable — `ACTIVE` or `GRACE_PERIOD` —
for proof generation to succeed.

#### `Result<VerificationResult> verify_proof(MembershipScope scope, Bytes signal, RateLimitProof proof)`

Verify an RLN proof for `signal`.
The following MUST hold for the verdict to be `PROOF_VALID`:

- the proof is valid;
- `proof.root` is within the Module's current valid-root window;
- `proof.epoch` is within a configured maximum gap of the Module's current epoch,
  so a newly registered member cannot publish into past epochs;
- `proof.external_nullifier` matches the value recomputed from
  `proof.epoch` and the scope's `rln_identifier`;
- `proof.share_x` matches `hash_to_field_le(signal)`,
  recomputed by the Module from the supplied `signal`,
  so the proof is bound to this signal and cannot be replayed onto another message.

A proof that fails any of these is `PROOF_INVALID` —
a verdict, not an error:
the error channel is reserved for calls the Module cannot judge,
e.g. `RLN_ERR_NOT_READY` before its registry view is warm.
A proof that passes them
but whose `nullifier` is already in the epoch's log
is judged by its `share_x` against the recorded one:
the same value is a retransmission of a message already verified,
reported `PROOF_DUPLICATE`;
a different value is double-signalling,
and the Module SHALL reconstruct the identity secret from the two shares
and report `PROOF_RATE_LIMIT_VIOLATION` with `recovered_secret` set.
The nullifier log is verification state local to the Module,
retained per epoch for at least the maximum epoch gap
within which proofs are accepted.
Verification is on the message hot path —
it runs for every message a validator receives —
so the Module SHALL serve it from its locally maintained registry state
and SHALL NOT perform registry access on the verification path.
The valid-root window is maintained asynchronously as the registry changes,
and SHOULD be maintained timely enough
that a proof generated against a newly published root is not falsely rejected.
The epoch size, the window's length, and the maximum epoch gap
are configuration parameters of the Module —
the registry does not enforce them;
validators of an application MUST use the same values,
or a proof accepted at one node is rejected at another.

## Optional extensions

A Module MAY additionally provide any of the following;
the consumer MUST NOT require them,
and a Module SHALL fail a call to an extension it does not provide
with `RLN_ERR_PERMANENT`.

- **Multiple memberships** —
  holding more than one membership for a scope.
  A Module that does so MUST require the consumer to select one explicitly —
  for example by `membership_hash` —
  and MUST NOT choose silently among candidates.
- **Credential export** —
  exporting a persisted membership (see [Persistence](#persistence))
  per [RLN-KEYSTORE](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/application/raw/rln-keystore.md),
  making credential files portable across implementations.
  Export is the only operation through which one of the Module's own credentials
  crosses this interface;
  a consumer that invokes it takes custody of the identity secrets.
- **Slot reclamation** —
  returning a message-id allocation to the epoch's budget
  when a proof was generated but its message was never published.
- **Proof staleness check** —
  a lightweight check that a held proof would still pass
  [`verify_proof`](#rate-limiting) —
  its root still current, its epoch within tolerance —
  without performing full verification,
  so a consumer retrying a long-parked message can refresh its proof
  before resending rather than after a rejection.
- **Registry parameters read** —
  exposing the registry-declared parameters that bound registration,
  e.g. the accepted rate-limit range or an assumed epoch length;
  a Module offering this read SHOULD reject
  a configured epoch size that contradicts a declared one.
- **Membership state subscriptions** —
  change notifications for the membership lifecycle,
  sparing the consumer polling [`get_membership_state`](#registration).
- **Withdrawal** —
  erasing a membership and recovering its deposit, where the registry supports it —
  the operation that resolves the `ERASED_AWAITS_WITHDRAWAL` state.

## Security and privacy considerations

### Message-id allocation and shared credentials

The rate limit rests on a single secret:
two proofs that reuse an `(epoch, message_id)` pair under one external nullifier
expose Shamir shares that reconstruct the identity secret,
which on registries implementing slashing burns the credential
(see [Rate-limit proof](#rate-limit-proof)).
The Module owns `message_id` allocation for its memberships,
so a single Module never reuses a pair.
This safety holds only within one Module:
a credential shared across Module instances —
by exporting it (see [Credential export](#optional-extensions))
and importing it elsewhere —
splits allocation across uncoordinated allocators.
A consumer that shares a credential this way
MUST coordinate `message_id` allocation across the holders,
the RECOMMENDED mechanism being static partitioning of the
`[0, rate_limit)` range;
otherwise a credential MUST be used by one Module at a time.

### Credential reuse across applications

One membership serving several applications is safe
only because each application's `rln_identifier`
is mixed into the external nullifier.
An application's `rln_identifier` MUST be unique to it
and MUST NOT be copied from another application;
a collision lets proofs from one application
consume another's rate budget and correlate the shared membership.

### Registry trust

The Module trusts its registry access for roots and proofs;
a compromised registry connection can equivocate about membership state.
A consumer with stronger trust requirements
SHOULD arrange for the Module to read the registry directly,
e.g. by running a node for the host network.
Reading a registry through a third-party RPC provider
MAY link the consumer's network identity to its membership.

## Appendix A: The `logos` namespace binding

The namespace binding required by [Registry identification](#registry-identification)
for registries hosted on Logos execution environments:

- **Namespace**: `logos`.
- **Reference**: the network name, pinned to lowercase (e.g. `testnet`, `local`).
  References are compared opaquely,
  so without pinned casing `logos:Testnet:…` and `logos:testnet:…`
  would identify distinct registries with distinct `membership_hash`es,
  silently fragmenting stored memberships.
- **Anchor account**: the registration program's configuration account —
  the account from which every other object of the registry
  (tree account, subtree accounts, membership accounts, treasury) is derived.
- **Canonical `account_address` form**:
  64 lowercase hexadecimal characters, without prefix.
- **`RegistryOptions`**: `funding_holding_account_id` —
  the token holding account paying `rate_limit × price_per_unit` at registration.
- **Time base**: membership lifecycle state is derived from
  the on-chain clock account, which reports Unix-epoch milliseconds;
  lifecycle durations (active duration, grace period) use the same unit.

## Appendix B: Membership hash construction

```text
membership_hash = lowercase_hex(
    SHA256(utf8(registry_id) || 0x00 || identity_commitment))
```

`registry_id` is in canonical form,
`0x00` is a single separator byte
(CAIP-10 identifiers cannot contain it),
and `identity_commitment` is its 32-byte little-endian representation.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [MESSAGING-API](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/application/raw/messaging-api.md)
- [RLN-KEYSTORE](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/application/raw/rln-keystore.md)
- [RLN](https://lip.logos.co/anoncomms/raw/rln-v2.html)
- [32/RLN-V1](https://github.com/logos-co/logos-lips/blob/master/docs/anoncomms/draft/32/rln-v1.md)
- [RLN Membership Allocation Protocol](https://lip.logos.co/anoncomms/raw/rln-membership-service.html)
- [WAKU2-RLN-RELAY](https://lip.logos.co/messaging/core/draft/17/rln-relay.html)
- [WAKU2-RLN-CONTRACT](https://github.com/logos-co/logos-lips/blob/6ebd9c86bba66090b277fa49d6f08182debf1247/docs/messaging/core/raw/rln-contract.md)
- [CAIP-10](https://standards.chainagnostic.org/CAIPs/caip-10)
- [RFC 2898](https://www.ietf.org/rfc/rfc2898.txt)
- [OnchainGroupManager, logos-delivery](https://github.com/logos-messaging/logos-delivery/blob/master/logos_delivery/waku/rln/group_manager/on_chain/group_manager.nim)
