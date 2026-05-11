# PAYMENT-STREAMS

| Field | Value |
| --- | --- |
| Name | Payment Streams Protocol for Logos Services |
| Slug | 155 |
| Status | raw |
| Category | Standards Track |
| Editor | Sergei Tikhomirov <sergei@status.im> |
| Contributors | Akhil Peddireddy <akhil@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-03-18** — [`e07c655`](https://github.com/logos-co/logos-lips/blob/e07c655a1fb86b46c99c3dd164a29438ab093b49/docs/anoncomms/raw/payment-streams.md) — Chore: move and fix header for payment streams spec (#295)
- **2026-02-24** — [`14fd5c0`](https://github.com/logos-co/logos-lips/blob/14fd5c09ccb76cb36ebb6a4b6c8082850172d330/vac/raw/payment-streams.md) — docs: add payment streams raw spec (#224)

<!-- timeline:end -->

## Abstract

This document provides a functional specification
for a payment streams protocol for Logos services.

A payment stream is an off-chain protocol
where a payer's deposit releases gradually to a payee.
The blockchain determines fund accrual based on elapsed time.

This specification defines stream-backed eligibility proof types
for the incentivization framework
defined in the incentivization specification
(see [References](#references)).
The incentivization specification is defined
in the context of Logos Messaging request-response protocols.
This specification can be extended to non-Messaging services.

The protocol targets Logos blockchain,
which includes the Logos Execution Zone (LEZ).
This document clarifies MVP requirements
and facilitates discussion with Logos blockchain and LEZ developers
on implementation feasibility and challenges.

## Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in
[RFC 2119](http://tools.ietf.org/html/rfc2119).

## Change Process

This document is governed by the [1/COSS](../../process/draft/1/coss.md) (COSS).

## Motivation

Logos is a privacy-focused tech stack that includes
Logos Messaging, Logos Blockchain, and Logos Storage.

Logos Messaging comprises a suite of communication protocols
with both P2P and request-response structures.
The backbone P2P protocols use tit-for-tat mechanisms.
Incentivization is introduced
for auxiliary request-response protocols
with well-defined user and provider roles.
One such protocol is Store,
which allows users to query historical messages
from Logos Messaging relay nodes.

This specification introduces a payment streams protocol
for Store and other request-response protocols.
The protocol targets the following requirements:

- Performance: Efficient payments with low latency and fees.
- Security: Limited loss exposure through spending controls.
- Privacy: On-chain deposit identity unlinkable to off-chain service requests.
- Extendability: Simple initial design with room for enhancements.

After reviewing prior work on payment channels, streams,
e-cash, and tickets,
payment streams were selected as the most suitable mechanism.

Payment streams enable unidirectional time-based fund flows
from payer to payee.
Streams are simpler than alternatives
and map well to use cases with distinct roles.
Parties need not store old states or initiate disputes
as required in payment channel protocols.
Streams avoid relying on a centralized mint entity,
typical for e-cash and ticket protocols,
improving resilience and privacy.

Different service patterns suit different payment mechanisms.
Ongoing services align well with streams
that provide time-based automatic fund accrual.
One-time or on-demand services suit
payment channels with one-off payments.

This specification targets streams
for services with steady usage patterns.
Addressing burst services with one-off payments
remains future work.

Logos blockchain uses the Logos Execution Zone (LEZ),
which enables both transparent and shielded execution.
LEZ is a natural fit
for the on-chain component of the payment protocol.

This document facilitates discussion with Logos developers on
whether the required functionality can be implemented,
which parts are most challenging and how to simplify them,
and other implementation considerations.

## Theory and Semantics

### Architecture Overview

The protocol has two roles:

- User: the party paying for services (payer).
- Provider: the party delivering services and receiving payment (payee).

The protocol uses a two-level architecture
of vaults and streams.

A vault holds a user's deposit and backs multiple streams.
A user MAY have multiple vaults.
One vault MAY back streams to different providers.
To start using the protocol,
the user MUST deposit funds into a vault.
The user MAY withdraw unallocated funds from the vault at any time.
Vault withdrawals send funds to addresses,
which MAY be external addresses or other vaults.
Allocating funds from a vault to a stream
is not considered a withdrawal,
as the funds remain within the protocol.

A stream is an individual payment flow from a vault to one provider.
When creating a stream,
the user MUST allocate a portion of vault funds to that stream.
Each stream MUST belong to exactly one vault.
Each stream MUST specify an accrual rate (tokens per time unit).
An allocation is the portion of vault funds committed to a stream.
The sum of all stream allocations MUST NOT exceed the vault balance.

A claim is the operation
where the provider retrieves accrued funds from a stream.
The provider MAY claim accrued funds from a stream in any state.
A claim MUST transfer the full accrued balance to the provider.

### Stream Lifecycle

Stream states:

- ACTIVE: Funds accrue to the provider at the agreed rate.
- PAUSED: Accrual is stopped.
  The stream transitions to PAUSED by user action
  or automatically when allocated funds are fully accrued.
  The user MAY resume the stream.
- CLOSED: Stream is permanently terminated.
  The stream MUST NOT transition to any other state.

Stream state transitions:

- Create: User creates a stream in ACTIVE state
  by allocating funds from the vault.
- Pause: User pauses an ACTIVE stream, stopping accrual.
  The stream also transitions automatically from ACTIVE to PAUSED
  when allocated funds are fully accrued.
- Resume: User resumes a PAUSED stream, restarting accrual.
  Resume MUST fail if remaining allocation is zero.
- Top-Up: User MAY add funds to stream allocation.
  Top-up MUST transition the stream to ACTIVE state.
  If the user wants to add funds without resuming,
  the user MUST pause the stream after top-up.
- Close: Either user or provider MAY close the stream
  from any non-CLOSED state.
  When a stream is closed,
  unaccrued funds MUST automatically return to the user's vault.
  Accrued funds remain available for the provider to claim.
- Claim: Provider MAY claim accrued funds from a stream in any state.
  A claim MUST transfer the full accrued balance;
  partial claims are not supported.
  A claim operation does not change stream state.

### Stream State Transition Diagram

```mermaid
graph LR;
    ACTIVE -->|pause / deplete| PAUSED;
    PAUSED -->|resume / top-up| ACTIVE;
    ACTIVE -->|close| CLOSED;
    PAUSED -->|close| CLOSED;
```

### Assumptions

Parties MUST agree on stream parameters before creation.
A separate discovery protocol SHOULD enable
providers to advertise services and accepted payment terms.

The provider SHOULD announce
accepted eligibility proof types and service parameters
via the discovery protocol.

The following is an informal list of discoverable parameters
(to be formally defined in the context of the discovery specification):

- accepted eligibility proof types
- accepted tokens
- required rate (tokens per time unit)
- minimum allocation
- required vault buffer percentage (RECOMMENDED default: 5%)
- load cap (cumulative resource limit per stream per time window)
- `VaultProof` response cap
  (maximum response size for `VaultProof`-backed requests)
- `max_open_stream_window` (RECOMMENDED default: 300 seconds)
  (maximum acceptable duration
  between receiving a `StreamProposal` and stream establishment)

Users SHOULD monitor service delivery
and take action when providers stop delivering service.
Since users are typically online to receive service,
monitoring quality and pausing or closing streams
is a reasonable expectation.

Providers SHOULD monitor the stream on-chain
and SHOULD stop providing service when a stream is not `ACTIVE`.

## Off-Chain Protocol

This section describes off-chain communication
for stream establishment, service delivery, and termination.

### Design Rationale

On-chain state is the source of truth for fund allocation and accrual.
Off-chain communication coordinates lifecycle events
and enables service delivery.

This specification does not redefine the service provision protocol.
The incentivization specification (see [References](#references))
defines the generic request-response framework
with `EligibilityProof` and `EligibilityStatus`.
This specification extends `EligibilityProof`
with two new types for stream-backed service provision,
defined in the following subsection.

### Eligibility Proof Types

The incentivization specification's `EligibilityProof`
is extended with two new optional fields:
`stream_proposal` and `stream_proof`.
These fields are mutually exclusive.
The first `ServiceRequest` MUST use `stream_proposal`;
its semantics: "I want to open a stream to you
with these parameters;
here is proof I have a vault to back it;
here is my first request."
All subsequent requests MUST use `stream_proof`.

```protobuf
message EligibilityProof {
  // existing, from incentivization specification
  optional bytes proof_of_payment = 1;
  // new, for stream-backed service provision
  optional bytes stream_proposal = 2;
  optional bytes stream_proof = 3;
}
```

#### StreamProposal

```protobuf
message StreamProposal {
  VaultProof vault_proof = 1;
  StreamParams stream_params = 2;
  bytes public_key = 3;  // key for signing subsequent service requests
}
```

#### VaultProof

A `VaultProof` proves that the user controls a vault
with sufficient unallocated funds
to back the proposed stream.

```protobuf
message VaultProof {
  bytes vault_id = 1;           // on-chain identifier of the vault
  bytes provider_id = 2;        // target provider (prevents replay)
  uint64 balance_commitment = 3; // asserted unallocated balance
  bytes owner_signature = 4;    // signature covering all fields above
}
```

The provider SHOULD verify on-chain
that the vault's unallocated balance is at least
`stream_allocation * (1 + buffer)`,
where `stream_allocation` is from the accompanying `StreamParams`
and `buffer` is the provider's required vault buffer percentage
(RECOMMENDED default: 5%).

The user MAY issue `VaultProof`s to multiple providers.
The user MUST ensure that issuing a new `VaultProof`
does not cause the total of all promised `VaultProof` allocations
from this vault
to exceed the vault's unallocated balance.

#### StreamParams

`StreamParams` contains proposed stream parameters.

```protobuf
message StreamParams {
  bytes service_id = 1;              // identifier of the requested service
  uint64 stream_rate = 2;           // proposed accrual rate (tokens per time unit)
  uint64 stream_allocation = 3;     // proposed initial allocation
  uint64 open_stream_by = 4;   // stream establishment deadline (absolute timestamp)
}
```

The `open_stream_by` field is an absolute timestamp
by which the user commits to establishing the stream on-chain.
The user MUST set `open_stream_by` to a future timestamp
no later than the current time plus `max_open_stream_window`.

#### StreamProof

A `StreamProof` links a request to an active on-chain stream.

```protobuf
message StreamProof {
  bytes stream_id = 1;    // on-chain identifier of the stream
  bytes signature = 2;    // signature over request_data using committed public_key
}
```

The provider SHOULD verify on-chain
that the stream is `ACTIVE`,
that the signature matches the committed `public_key`,
and that the stream parameters match
those originally proposed.

### Message Types

The off-chain protocol uses three message types:
`ServiceRequest`, `ServiceResponse`, and `ServiceTermination`.

#### ServiceRequest

A `ServiceRequest` has two top-level fields,
consistent with the incentivization specification pattern:

- `request_data`: service-specific payload
- `eligibility_proof`: an `EligibilityProof`
  containing either a `stream_proposal` or a `stream_proof`
  (see [Eligibility Proof Types](#eligibility-proof-types))

#### ServiceResponse

A `ServiceResponse` MUST include:

- `eligibility_status`: an `EligibilityStatus`
  (from the incentivization specification) with:
  - `status_code`: indicating acceptance,
    parameter rejection, proof invalidity, etc.
  - `status_desc`: human-readable description
    (RECOMMENDED to include actionable guidance
    on parameter rejection)
- `response_data`: service-specific payload
  (included if and only if the request is served)

Status codes specific to this specification:

- `OK`: request served
- `PARAMS_REJECTED`: stream parameters unacceptable;
  `VaultProof` NOT marked as spent;
  user MAY retry with adjusted parameters
- `PROOF_INVALID`: `VaultProof` or `StreamProof` verification failed
- `STREAM_NOT_ACTIVE`: referenced stream
  is no longer active on-chain

The provider SHOULD limit parameter-rejection retries
to a RECOMMENDED maximum of 5 per vault
within a RECOMMENDED time window of 600 seconds.

#### ServiceTermination

The provider SHOULD send a `ServiceTermination` message
before stopping service.
A `ServiceTermination` message MAY be sent regardless of whether
a stream has been established on-chain.

This message MUST include:

- `termination_type`: `TEMPORARY` or `PERMANENT`
- `resume_after`: timestamp after which service MAY resume
  (REQUIRED for `TEMPORARY`, empty for `PERMANENT`)

For temporary termination,
the user MAY pause the stream until the `resume_after` time.
For permanent termination,
the user SHOULD close the stream to recover unaccrued funds.

### Protocol Flow

1. The user discovers a provider via the discovery protocol.
   The provider's advertisement includes
   accepted eligibility types and service parameters.

2. The user sends the first `ServiceRequest`
   with `eligibility_proof` containing a `StreamProposal`
   (`VaultProof` + `StreamParams` + `public_key`)
   and `request_data`.

3. The provider verifies `VaultProof` on-chain
   and evaluates `StreamParams`:

   - If parameters are unacceptable:
     the provider responds with `PARAMS_REJECTED`.
     The `VaultProof` is not marked as spent.
     The user MAY retry with adjusted `StreamParams`.
   - If the proof is invalid:
     the provider responds with `PROOF_INVALID`.
   - If accepted:
     the provider serves the request immediately,
     responding with `OK` and `response_data`.
     The provider notes the pending session.
     The provider SHOULD limit this response
     to the advertised `VaultProof` response cap.

4. The user creates the stream on-chain
   before `open_stream_by`.

5. The user sends subsequent `ServiceRequest`s
   with `eligibility_proof` containing a `StreamProof`.

6. The provider monitors the chain for a matching stream.
   If no matching stream appears by `open_stream_by`,
   the provider SHOULD discard the session
   and release planned capacity.
   If the stream is established before `open_stream_by`,
   the first `StreamProof`-backed request
   MAY arrive after `open_stream_by`.

A user MUST NOT have more than one pending
`StreamProposal`-backed session per vault-provider pair at a time.
To open multiple streams to the same provider,
the user MUST complete each stream establishment
before initiating the next.
If the vault is drained between `VaultProof` verification
and stream creation, this constitutes a protocol violation;
the provider SHOULD send a `ServiceTermination`
with `termination_type` `PERMANENT`.

## Protocol Extensions

This section describes optional modifications
that MAY be applied to the base protocol.
Each extension is independent.

### Auto-Pause

The user MAY specify an auto-pause duration when creating a stream.
When the specified duration elapses since stream creation or last resume,
the stream MUST automatically transition to PAUSED state.
The user MAY resume the stream, resetting the auto-pause timer.

Auto-pause limits loss if service stops and the user is offline.
Per-stream allocation already bounds total risk;
auto-pause adds periodic check-ins for long-running streams.

### Delivery Receipts

The claim operation MAY require delivery receipts as proof of service.
A delivery receipt is a user-signed message that MUST include
stream identifier, service delivery details, and signature.
If a stream has delivery receipts enabled,
the protocol MUST only allow claims with valid receipts.

Receipt granularity presents a trade-off.
Per-message receipts allow the user to approve each message individually
but require signing each receipt, increasing interaction overhead.
Batched receipts reduce signing overhead
but require the user to approve multiple messages at once.

### Automatic Claim on Closure

This extension adds an optional auto-claim flag.
When auto-claim is enabled,
closing the stream MUST automatically claim accrued funds for the provider.

Auto-claim simplifies the protocol
by ensuring closed streams hold no funds,
eliminating the need to track balances in closed streams.

However, auto-claim has potential issues:

- Prevents provider from batching claims.
- May create timing correlations that leak privacy.
- Requires user to pay for provider's claim operation.
- May cause the entire close operation to fail if claim fails.

Assessing these trade-offs requires clarity on LEZ,
particularly gas model, batching techniques, and timing privacy.

### Activation Fee

A user can exploit the pause/resume mechanism
by keeping a stream paused
and resuming briefly only when querying a service.
This results in minimal payment for actual service usage.

The activation fee addresses this attack.
When the activation fee is enabled,
a fixed amount MUST accrue to the provider
immediately upon the stream becoming `ACTIVE`.
The activation fee SHOULD reflect
the minimum acceptable payment for a service session.
The activation fee applies to stream creation, resume, and top-up operations,
as only user actions transition a stream to `ACTIVE` state.
If stream allocation is lower than activation fee,
stream activation MUST fail.

Providers MAY alternatively address this attack via off-chain policy
by refusing service to users who pause and resume excessively.

### Load Cap

A load cap represents
cumulative resource consumption per stream per time window
(e.g. total bytes or requests per minute).
It applies to the entire stream session,
not to individual responses.
The provider SHOULD advertise the load cap
via the discovery protocol.

For `VaultProof`-backed requests (the first `ServiceRequest`),
the provider SHOULD advertise a separate `VaultProof` response cap:
the maximum response size for a single `VaultProof`-backed response.
This limits provider exposure
to requests not yet backed by an on-chain stream.

The user MUST NOT exceed the applicable cap.
If the user exceeds it,
the provider SHOULD terminate service.

A user who requires a higher load cap
SHOULD open multiple streams to the same provider.

### Multi-round Stream Parameter Negotiation

A future extension MAY allow the provider
to include counter-proposed parameters
in a `PARAMS_REJECTED` response,
enabling iterative negotiation
before the first request is served.

## Implementation Considerations

This section outlines how the protocol maps onto LEZ.

The stream protocol MAY be deployed as an LEZ program
with three account types:

- StreamDefinition: stream parameters and status.
- VaultDefinition: list of streams backed by a vault, controlled by payer.
- VaultHolding: token account funded by payer, used to pay providers.

Stream lifecycle rules and balance constraints
are encoded and enforced through program logic.

Stream state is evaluated lazily.
On-chain storage holds stream parameters,
but the effective state depends on the block timestamp at execution time.
State transitions (such as auto-pause) are reflected on-chain
only when an on-chain operation is executed.

Whether shielded execution can access block timestamps
for time-based accrual calculation is an open question.
Given a mechanism for elapsed time in shielded execution,
all protocol operations MAY be performed within shielded execution.

## Security and Privacy Considerations

An initial privacy goal is unlinkability
between off-chain requests and on-chain funding.
Vault deposits MUST NOT reveal the depositor's identity.
Stream creation SHOULD NOT reveal which vault funded the stream.

Each account MAY be public or private, configured per-account.
The payer decides whether stream operations use
transparent or shielded execution.
The protocol design SHOULD NOT fix this decision.
A provider MAY reject stream requests
that do not match their privacy preferences.

On-chain state of a stream MUST be verifiable by both parties.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [Incentivization for Waku Light Protocols](https://github.com/logos-messaging/specs/blob/master/standards/core/incentivization.md)

### Informative

#### Related Work

- [Off-Chain Payment Protocols: Classification and Architectural Choice](https://forum.vac.dev/t/off-chain-payment-protocols-classification-and-architectural-choice/596)
- [Logos Execution Zone](https://github.com/logos-blockchain/logos-execution-zone)

#### Payment Streaming Protocols

Existing payment streaming protocols
(Sablier Flow, Sablier Lockup, LlamaPay V2, Superfluid)
target EVM-like state architectures.
They use time-based accrual with ERC-20 tokens.
Protocols differ in stream duration.
Some support fixed-duration streams (Sablier Lockup),
while others allow open-ended streams (Sablier Flow).
Deposit architecture also varies.
Singleton managers (Sablier Flow, Sablier Lockup)
require separate deposits per stream.
Per-payer vaults (LlamaPay V2)
allow one deposit to back multiple streams.

- [Sablier Flow](https://github.com/sablier-labs/flow)
- [Sablier Lockup](https://github.com/sablier-labs/lockup)
- [LlamaPay V2](https://github.com/LlamaPay/llamapay-v2)
- [Superfluid Protocol](https://github.com/superfluid-org/protocol-monorepo)

## Appendix A: Illustrative EVM Implementation

This appendix provides an illustrative EVM-based implementation outline.
The actual implementation will target LEZ.

### A.1 Contract Structure

```solidity
contract PaymentVault {
    enum StreamState { ACTIVE, PAUSED, CLOSED }

    struct Stream {
        address token;
        address provider;
        uint128 ratePerSecond;
        uint128 allocation;
        uint64  lastUpdatedAt;
        uint128 accruedBalance;
        StreamState state;
    }

    address public user;
    mapping(address token => uint256) public vaultBalance;
    uint256 public nextStreamId;
    mapping(uint256 => Stream) public streams;
}
```

### A.2 Vault Operations

```solidity
event Deposited(address indexed token, uint256 amount);
event Withdrawn(address indexed token, uint256 amount, address indexed to);

function deposit(address token, uint256 amount) external;
function withdraw(address token, uint256 amount, address to) external;
```

### A.3 Stream Lifecycle

```solidity
event StreamCreated(
    uint256 indexed streamId,
    address indexed provider,
    address indexed token,
    uint128 ratePerSecond,
    uint128 allocation
);
event StreamPaused(uint256 indexed streamId);
event StreamResumed(uint256 indexed streamId);
event StreamToppedUp(uint256 indexed streamId, uint128 additionalAllocation);
event StreamClosed(uint256 indexed streamId, uint128 refundedToVault);
event Claimed(uint256 indexed streamId, address indexed provider, uint128 amount);

/// @notice Create a new stream in ACTIVE state (user only)
/// @dev MUST revert if allocation exceeds available vault balance
function createStream(
    address provider,
    address token,
    uint128 ratePerSecond,
    uint128 allocation
) external returns (uint256 streamId);

/// @notice Pause an ACTIVE stream (user only)
function pauseStream(uint256 streamId) external;

/// @notice Resume a PAUSED stream (user only)
/// @dev MUST revert if remaining allocation (allocation - accruedBalance) is zero
function resumeStream(uint256 streamId) external;

/// @notice Add funds to stream allocation; transitions to ACTIVE (user only)
/// @dev MUST revert if additionalAllocation exceeds available vault balance
function topUpStream(uint256 streamId, uint128 additionalAllocation) external;

/// @notice Close stream permanently
/// @dev Callable by user or provider. Unaccrued funds (allocation - accruedBalance)
///      MUST be returned to vaultBalance. Accrued funds remain claimable by provider.
function closeStream(uint256 streamId) external;

/// @notice Provider claims accrued funds from a stream
/// @dev Callable in any state (ACTIVE, PAUSED, or CLOSED).
///      Transfers full accruedBalance to provider and resets it to zero.
function claim(uint256 streamId) external;
```

### A.4 Internal Accrual

```solidity
/// @notice Update accruedBalance based on elapsed time since lastUpdatedAt
/// @dev Called by pauseStream, resumeStream, topUpStream, closeStream, and claim
///      before modifying stream state. Caps accrual at allocation and
///      transitions to PAUSED when fully accrued (lazy evaluation:
///      state updates on next interaction, not at exact depletion time).
function _accrue(uint256 streamId) internal;
```
