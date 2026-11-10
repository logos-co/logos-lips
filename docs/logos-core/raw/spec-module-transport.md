# LOGOS-MODULE-TRANSPORT

| Field        | Value                                                         |
|--------------|---------------------------------------------------------------|
| Name         | Logos Module Transport                                        |
| Slug         | 305                                                           |
| Status       | raw                                                           |
| Category     | Standards Track                                               |
| Editor       | ksr <ksr@status.im>                                           |
| Contributors | Jarrad Hope <jarrad@status.im>, Jacek Sieka <jacek@status.im> |

## Abstract

This specification defines the `logos.transport` message envelope and protocol semantics for inter-process and remote Logos module communication.

The message types and their CBOR encodings are fully defined by the CDDL
schema in Section 1. This specification adds only the non-CDDL parts that CDDL
cannot express:

1. **Directional message semantics** — which party may send each message and
   how replies correlate to requests (section 1.4)
2. **Stream binding** — how directional messages are carried over a
   bidirectional byte stream (sections 2 and 3)
3. **Transport binding** — Unix domain socket and TCP stream bindings
   (section 9)

Everything else — message types, field names, value types, error codes —
is defined in the CDDL below.

The CDDL blocks in Section 1 collectively define the `logos.transport` protocol grammar.
`logos_transport.cddl` is an extracted machine-readable mirror.
If the extracted artifact differs from this specification, this specification governs.
This protocol CDDL is not a concrete module schema, interface contract schema, or supporting schema under LOGOS-MODULE-INTERFACE.
It does not participate in Logos schema construction and does not have a Logos schema root.
The `logos.transport.request`, `logos.transport.response`, and `logos.transport.event` declarations are directional Transport messages and do not declare callable module operations.
The envelope references the pinned Logos common definitions `logos.schema_commitment`, `logos.error_code`, and `logos.error_detail` for fields shared with module contracts.
Those references do not make the envelope a supporting-schema dependency.
The envelope may use RFC 8610 constructs that LOGOS-MODULE-INTERFACE reserves for protocol use or prohibits in Logos schema documents.

This spec is intentionally thin.
The Logos transport protocol is defined as directional Logos deterministic
CBOR messages.
A stream transport is one binding of those messages onto a bidirectional,
long-lived byte stream; it is not the only possible binding.
Future revisions may add streaming, multiplexed channels, compression, or
additional bindings.

This spec is ONLY relevant when modules communicate over sockets (inter-
process or remote). In direct mode (in-process), calls go through C function
pointers and this protocol is not used. See LOGOS-MODULE-INTERFACE for the
interface definition format and LOGOS-MODULE-RUNTIME for module admission, lifecycle, routing, and the process model.

This transport does **not** define a different module contract. It is one
runtime realization of the same interface contract defined in
LOGOS-MODULE-INTERFACE. A conforming implementation MUST preserve the same
method names, event names, schema-defined payload shapes, and success/error
semantics that would apply in direct mode.

## Requirements Language

Uppercase requirement keywords in this specification follow BCP 14 [RFC 2119] [RFC 8174].
Lowercase forms retain their ordinary English meanings.

## 1. Message Envelope

All messages are CBOR-encoded maps.
Each top-level message map carries a required compact message-kind field at
integer key `0`.
This field identifies the transport message type.
All other top-level keys defined by this specification are text-string keys.
Under the mandatory deterministic map-key order,
the one-byte encoding of integer key `0` sorts before every text-string key.
A valid message therefore carries key `0` as the first map entry after the definite-length map header.
A receiver MAY select the message kind after parsing only the map header and first key-value pair,
without generically decoding the complete map or making a second pass.
A receiver MUST reject a message whose first map entry is not key `0`.

### 1.1 Primitive Types

```cddl
; -- primitive types used in the envelope --

logos.transport.module-name       = tstr .size (1..64)
logos.transport.method-name       = tstr .size (1..128)
; Exact schema event identifier from the module's CDDL, e.g.
; "storage.started_event".
logos.transport.event-name        = tstr .size (1..128)
logos.transport.call-id           = uint
logos.transport.subscription-id   = uint
logos.transport.authorization-material = bstr
logos.transport.schema-subtree-root = bstr .size 32
logos.transport.value-root        = bstr .size 32

; This block is the owning registry for transport message-kind values.
; Other Logos specifications may cite these values but do not allocate them.
logos.transport.message-kind      = 0..8

logos.transport.message-kind-hello       = 0
logos.transport.message-kind-request     = 1
logos.transport.message-kind-response    = 2
logos.transport.message-kind-subscribe   = 3
logos.transport.message-kind-unsubscribe = 4
logos.transport.message-kind-event       = 5
logos.transport.message-kind-error       = 6
logos.transport.message-kind-cancel      = 7
logos.transport.message-kind-subscription-result = 8
```

### 1.2 Message Types

| Kind | Type        | Direction        | Purpose                            |
|------|-------------|------------------|------------------------------------|
| 0    | Hello       | Both             | Peer identification, authorization, and contract binding |
| 1    | Request     | Caller -> Callee | Method invocation                  |
| 2    | Response    | Callee -> Caller | Method result or error             |
| 3    | Subscribe   | Caller -> Callee | Register for event notifications   |
| 4    | Unsubscribe | Caller -> Callee | Cancel event subscription          |
| 5    | Event       | Callee -> Caller | Async event notification           |
| 6    | ProtocolError | Either           | Protocol-level error               |
| 7    | Cancel      | Caller -> Callee | Abort an in-flight request         |
| 8    | SubscriptionResult | Callee -> Caller | Complete Subscribe or Unsubscribe |

### 1.3 Message Definitions

`{ * tstr => any }` is used for the `params`, `result`, and `data` fields because the Transport layer carries payloads without knowing their concrete module schemas.
The Transport envelope is protocol CDDL rather than a Logos schema document, so the schema type restrictions in LOGOS-MODULE-INTERFACE Section 1.7 do not apply to it.
Validation against the concrete module schema happens at the module layer after the Transport layer delivers the message.

The message maps below are closed.
A receiver MUST reject an unknown field with ProtocolError `INVALID_PARAMS`.
An incompatible envelope change requires a separately named transport profile and is not negotiated within this protocol.

```cddl
; -- Hello --
; Peer identification, authorization, and contract binding.
; Stream bindings use Hello during connection establishment.

logos.transport.hello = {
    0:              logos.transport.message-kind-hello,
    module:         logos.transport.module-name,
    token:          logos.transport.authorization-material,
    schema:         logos.schema_commitment,
}

logos.transport.payload-commitment = {
    schema_subtree_root: logos.transport.schema-subtree-root,
    value_root:          logos.transport.value-root,
}


; -- Request --
; A method call. Params is a CBOR map whose concrete schema is defined
; by the module's .cddl file (see LOGOS-MODULE-INTERFACE section 1.4).
; The method field carries the bare method name defined by
; LOGOS-MODULE-INTERFACE.
; It does not carry the schema namespace or schema root.
; The established provider session supplies the selected provider,
; selected contract, consumer, route, and allowed method roots.
; The transport layer uses a generic map type here; schema validation
; happens at the module layer against the concrete request type.

logos.transport.request = {
    0:          logos.transport.message-kind-request,
    id:         logos.transport.call-id,
    method:     logos.transport.method-name,
    params:     { * tstr => any },
    commitment: logos.transport.payload-commitment,
}


; -- Response --
; Reply to a Request. Exactly one of "result" or "error" MUST be present.
; The result map's concrete schema is defined by the module's .cddl file.
; Schema validation happens at the module layer.
;
; CDDL cannot express "exactly one of two optional fields" directly.
; We use two variants in a choice:

logos.transport.response = logos.transport.response-ok / logos.transport.response-err

logos.transport.response-ok = {
    0:          logos.transport.message-kind-response,
    id:         logos.transport.call-id,
    result:     { * tstr => any },
    commitment: logos.transport.payload-commitment,
}

logos.transport.response-err = {
    0:     logos.transport.message-kind-response,
    id:    logos.transport.call-id,
    error: logos.transport.error-payload,
}


; -- Subscribe --
; Register interest in a named event.

logos.transport.subscribe = {
    0:     logos.transport.message-kind-subscribe,
    id:    logos.transport.subscription-id,
    event: logos.transport.event-name,
}


; -- Unsubscribe --

logos.transport.unsubscribe = {
    0:  logos.transport.message-kind-unsubscribe,
    id: logos.transport.subscription-id,
}


; -- Subscription Result --
; Complete one Subscribe or Unsubscribe operation.

logos.transport.subscription-operation =
      logos.transport.message-kind-subscribe
    / logos.transport.message-kind-unsubscribe

logos.transport.subscription-result =
      logos.transport.subscription-result-ok
    / logos.transport.subscription-result-err

logos.transport.subscription-result-ok = {
    0:         logos.transport.message-kind-subscription-result,
    id:        logos.transport.subscription-id,
    operation: logos.transport.subscription-operation,
}

logos.transport.subscription-result-err = {
    0:         logos.transport.message-kind-subscription-result,
    id:        logos.transport.subscription-id,
    operation: logos.transport.subscription-operation,
    error:     logos.transport.error-payload,
}


; -- Event --
; Async event notification to a subscriber. Data is a CBOR map whose
; concrete schema is defined by the module's .cddl file (see
; LOGOS-MODULE-INTERFACE section 1.5). Schema validation at module layer.

logos.transport.event = {
    0:          logos.transport.message-kind-event,
    sub:        logos.transport.subscription-id,
    event:      logos.transport.event-name,
    data:       { * tstr => any },
    commitment: logos.transport.payload-commitment,
}


; -- ProtocolError message --
; Protocol-level error not tied to a specific Request.

logos.transport.protocol-error = {
    0:        logos.transport.message-kind-error,
    code:     logos.error_code,
    ? message: tstr .size (0..512),
    ? detail: logos.error_detail,
}


; -- Cancel --
; Abort an in-flight request.

logos.transport.cancel = {
    0:  logos.transport.message-kind-cancel,
    id: logos.transport.call-id,
}


; -- Shared status codes --
; Shared status codes and encoded detail are defined by
; LOGOS-MODULE-INTERFACE Section 5.1.
; Transport defines no additional status-code registry.

logos.transport.error-payload = {
    code:     logos.error_code,
    ? message: tstr .size (0..512),
    ? detail: logos.error_detail,
}

; Defined by LOGOS-MODULE-INTERFACE Section 5.1:
; logos.error_code =
;     0 / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9


; -- Top-level message union --

logos.transport.message = logos.transport.hello
        / logos.transport.request
        / logos.transport.response
        / logos.transport.subscribe
        / logos.transport.unsubscribe
        / logos.transport.subscription-result
        / logos.transport.event
        / logos.transport.protocol-error
        / logos.transport.cancel
```

`protocol-error.code` and `error-payload.code` MUST be nonzero.
When `message` is present,
it is human-readable diagnostic text with no machine-readable semantics.
Its absence does not change the meaning of `code`.
When either structure contains `detail`,
the receiver MUST validate its length, deterministic encoding, and error-specific root
as required by LOGOS-MODULE-INTERFACE Section 5.1.
A message containing disallowed or invalid detail is invalid.

### 1.4 Directional Message Semantics

The Logos transport protocol is defined as directional Logos deterministic
CBOR messages between
a caller and a callee.
The caller is the party invoking methods or subscribing to events.
The callee is the party exposing the module interface.

Caller-to-callee messages:

- `Hello`
- `Request`
- `Subscribe`
- `Unsubscribe`
- `Cancel`
- `ProtocolError`

Callee-to-caller messages:

- `Hello`
- `Response`
- `SubscriptionResult`
- `Event`
- `ProtocolError`

`Request` and `Response` messages are correlated by `id`.
The caller assigns the request `id`; the callee echoes that `id` in exactly
one `Response`.

`Subscribe`, `Unsubscribe`, `SubscriptionResult`, and `Event` messages
are correlated by subscription `id`.
The caller assigns the subscription `id`; the callee includes that value in
the corresponding `SubscriptionResult` and matching `Event` messages.
`SubscriptionResult.operation` identifies the completed control operation.

These directional semantics are independent of the carrier.
The stream binding defined in this specification carries both directions over
one long-lived bidirectional byte stream.
Other bindings, such as an HTTP-style request-oriented binding, would need a
separate specification to define how these directional messages are mapped to
that carrier.

---

## 2. Stream Binding

### 2.1 Stream Framing

The stream binding carries directional transport messages over a
bidirectional byte stream such as a Unix domain socket or TCP connection.
Messages over a stream binding MUST be length-prefixed.
Each message is preceded by a 4-byte big-endian unsigned integer indicating
the byte length of the following CBOR-encoded message:

```
+--------+--------+--------+--------+------- ... -------+
|       length (uint32, big-endian) |  CBOR message      |
+--------+--------+--------+--------+------- ... -------+
```

The 4-byte length prefix can represent frame lengths up to 4,294,967,295
bytes.
This is the framing ceiling, not a recommended operational message size.

Implementations MUST enforce a configured maximum accepted frame size for
resource safety.
On reading a length prefix greater than that configured maximum, the receiver MUST NOT allocate or read the declared body.
The receiver MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable and MUST then close the connection.
Every in-flight call on that connection fails locally with `TRANSPORT_ERROR` as defined in Section 3.2.

The active configured maximum accepted frame-body size of a conforming stream binding MUST be at least 16 MiB.
Logos module interfaces MUST NOT require single Transport messages larger than 16 MiB unless deployment-specific configuration, a Transport binding, or a future protocol extension specifies a larger supported size.

Before writing any part of a frame, the sender MUST ensure that its complete deterministic-CBOR body fits the peer-supported maximum, including the envelope and commitments but excluding the four-byte prefix.
Absent separately established support for a larger limit, the sender MUST use 16 MiB.
An oversized ordinary Request MUST NOT be sent and MUST fail its local invocation with `MODULE_ERROR`.
An oversized successful Response MUST be replaced by a correlated `response-err` carrying `MODULE_ERROR` without validation detail; that size failure alone MUST NOT close the session when the error Response can be sent.
If the failure Response cannot be sent, Section 3.2 governs connection termination.
An oversized Event MUST NOT be committed or partially sent to the affected connection.
Its publication boundary MUST report failure where that boundary permits it; otherwise the sender MUST send ProtocolError `TRANSPORT_ERROR` when writable and close the affected connection.
An already committed Event MUST NOT be silently discarded.
These checks apply per destination and do not make a multicast publication atomic.
Other control or establishment messages must also fit; inability to send them fails the corresponding establishment or connection without inventing a correlated method result.
These stream limits do not impose a new direct-mode payload limit.

### 2.2 Message Ordering

Messages on a single stream connection are processed in order. However,
multiple requests may be in flight simultaneously (multiplexed by `logos.transport.call-id`).
The callee MAY send responses out of order relative to requests (e.g. a
fast synchronous call may return before a slow one started earlier).

### 2.3 Deterministic CBOR

All messages MUST be encoded using Logos deterministic CBOR as specified in
LOGOS-MODULE-INTERFACE section 4.4.
The transport layer MUST validate the message envelope:
frame length, deterministic CBOR, payload depth, known message-kind, required envelope fields, envelope field types, message direction, and connection state.
Payload-depth validation MUST apply LOGOS-MODULE-INTERFACE Section 4.5.1 to `params`, `result`, and `data`.
Whole-message depth limits MUST allow at least one additional container level beyond the configured payload-depth limit.
If a received message fails an envelope validation check
and this specification does not define more specific failure behavior,
the receiver MUST NOT dispatch, accept, or deliver the message.
The receiver MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable.
It MUST then close the connection.
For a rejection caused solely by exceeding the payload-depth limit, the ProtocolError MUST omit `detail`.

The receiver MUST enforce the message directions in Section 1.4.
Before the receiving endpoint has completed its part of the Hello exchange, it MUST accept only the Hello or ProtocolError messages permitted by Section 3.1.
A wrong-direction message or an ordinary message received before that point MUST produce ProtocolError `INVALID_PARAMS` when the connection remains writable, followed by connection closure without dispatch or delivery.
Post-establishment Hello follows Section 3.3.
A well-formed ProtocolError is permitted in either direction during establishment or after establishment; its recipient MUST close the connection without sending another ProtocolError in response.

The transport layer treats schema payload fields (`params`, `result`, and
`data`) as opaque CBOR maps after envelope validation.
Payload validation against the target method or event declaration under its defining contract occurs at the schema-aware sending and receiving boundaries.

---

## 3. Connection Lifecycle

### 3.1 Stream Connection Establishment

```
Caller                                  Callee
  |                                        |
  |--- open socket ----------------------->|
  |                                        |
  |--- Hello{module, token, schema} ------>|
  |                                        |
  |<-- Hello{module, token, schema} -------|
  |                                        |
  |    (connection established)            |
  |                                        |
```

1. **Caller opens the carrier connection** at the endpoint selected by the transport profile.
   For a Runtime-established route,
   the caller MUST use the exact endpoint from the invocation descriptor.

2. **Caller sends Hello.** Fields:
   - `module`: the callee's selected flat runtime module or endpoint name.
     In this transport specification, "module" includes ordinary modules,
     Logos-defined system modules, runtime-control surfaces, and runtime-host
     endpoints that expose a Logos interface.
   - `token`: authorization or consumer-binding material defined for this connection
   - `schema`: the selected contract for this provider session.
     Both peers MUST provide the same exact structural schema identity.
     For a runtime-control connection, it identifies the Runtime Control contract.
     For an ordinary module invocation connection, it identifies the ordinary module contract exposed on that connection.
     When the connection is opened for a Runtime-established route,
     this is the route's selected contract.
     If the route selects the provider's primary concrete module contract,
     the field identifies that concrete contract.
     If the route selects an implemented interface contract,
     the field identifies that interface contract rather than the provider's
     full concrete module contract.
     It does not identify every module provider, facade, or route known behind a
     runtime.
3. **Callee validates the Hello.**
   After validating framing, deterministic CBOR, the message kind, and the absence of unknown fields,
   the callee MUST perform the following checks in the listed order.
   If more than one check would fail,
   the callee MUST report the outcome of the first failing check.
   - The `module` field MUST be present and well-formed.
     If it is missing or malformed, the callee MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable
     and MUST close the connection without consuming authorization material.
     On a remote intrinsic Runtime Control endpoint, a well-formed `module` that differs from the endpoint name is treated the same way.
     On an ordinary protected provider endpoint or a Runtime-owned local system-service endpoint, a well-formed `module` that differs from the provider selected for this connection
     MUST fail the following ticket check with the non-revealing `NOT_AUTHORISED` outcome required by Section 8.1.
   - The `token` field MUST be present and satisfy the selected endpoint and transport profile.
     A remote intrinsic Runtime Control endpoint uses the consumer-binding rules in LOGOS-MODULE-RUNTIME Section 9.
     An ordinary protected provider route uses the route-ticket validation defined in Section 8.1.
     A Runtime-owned local system-service session uses Section 8.1.2.
     If validation fails,
     the callee MUST send ProtocolError `NOT_AUTHORISED` when the connection remains writable
     and MUST close the connection.
     Ticket validation MUST NOT consume a live ticket.
   - The caller's `schema` MUST equal the selected contract exposed by the callee.
     For a Runtime-established ordinary module route,
     this is the selected contract exposed by that invocation path.
     A provider selected through an implemented interface contract validates
     against that interface contract for this connection.
     Its primary concrete module contract remains provider metadata exposed by
     Runtime Control.
     It is not the Transport Hello identity for the interface-selected
     connection.
     The comparison includes `commitment_model`, `schema_root`,
     `hash_profile`, and `hash_suite`.
     If the callee cannot compute structural schema identity for the selected schema,
     if `schema` is missing or malformed, or if any field differs,
     the callee MUST send ProtocolError `VERSION_MISMATCH` when the connection remains writable
     and MUST close the connection without consuming a live ticket.
     A caller's use of the selected contract does not claim that the caller implements that contract
     and does not grant provider or method authority.
   - After all preceding checks succeed,
     the callee MUST atomically redeem authorization material when required by the selected profile.
     A concurrent redemption that has already consumed the ticket produces `NOT_AUTHORISED`.

   If the callee cannot complete a check because evaluation capacity is temporarily unavailable,
   it MUST send ProtocolError `MODULE_ERROR` when the connection remains writable and MUST close the connection;
   ticket consumption follows Section 8.1.

4. **Callee sends Hello response.** Fields:
   - `module`: the callee's selected flat runtime module or endpoint name
   - `token`: response authorization material defined by the selected profile
   - `schema`: the same selected contract accepted from the caller

5. **Caller validates the Hello response.**
   After envelope validation, the caller MUST perform the following module, token, and schema checks in that order and report the first failing check.
   The caller MUST verify that `module` equals the selected name sent in its initial Hello.
   If it differs,
   the caller MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable
   and MUST close the connection.
   It MUST validate `token` according to the selected profile's response rules.
   If the response token fails those rules, the caller MUST send ProtocolError `NOT_AUTHORISED` when the connection remains writable and MUST close the connection.
   This includes a non-empty response token for a profile that requires it to be empty.
   The caller MUST verify that the callee response includes the same selected contract in `schema`.
   For Runtime-established ordinary module routes,
   this verifies the selected contract for the invocation path.
   It does not validate unrelated contracts implemented by the same backing
   provider.
   If `schema` differs,
   the caller MUST send ProtocolError `VERSION_MISMATCH` when the connection remains writable
   and MUST close the connection.

6. **Connection is established.** Both parties may now send directional
   transport messages allowed for their role.

### 3.2 Connection Termination

Either party may close the socket at any time. On close:

- All in-flight requests receive a synthetic `TRANSPORT_ERROR` response.
- All active subscriptions are cancelled.
- The caller-side handle becomes unusable for ordinary invocation and subscription operations.

The caller-side binding MUST process connection loss as invocation-path termination for its route-handle observer under LOGOS-MODULE-INTERFACE Section 2.5.
The unreleased native handle storage remains valid for terminal-observer registration, response-buffer release and handle release.
This is a local notification and requires no final message from the peer.
It does not change the result classification for outstanding requests.

A synthetic `TRANSPORT_ERROR` does not prove
that the callee did not execute an in-flight request.
The callee may have completed the operation
before the response was lost.

Transport and Runtime MUST NOT automatically replay an ordinary module request after connection loss.
A caller may retry only when the module contract or application semantics make that retry safe.
The retry is a new request on a valid provider session and uses a new transport call identifier.

For a protected remote session,
the redeemed route ticket MUST NOT be reused.
The caller obtains a new usable invocation
through route renewal or new route establishment.

Re-establishing a subscription creates a new subscription.
Transport does not replay events missed while the previous session was unavailable
unless the module contract defines an explicit event-recovery mechanism.

### 3.3 Post-Establishment Hello

The Hello exchange is used only during connection establishment.
After the connection is established,
each party MUST NOT send another Hello.
A recipient MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable
and MUST close the connection.

### 3.4 Response and Event Correlation

After envelope validation, a Response MUST identify a Request transmitted on that connection for which no terminal Response has yet been received.
A SubscriptionResult MUST match both the identifier and the operation of an outstanding Subscribe or Unsubscribe on that connection.
An Event MUST identify a subscription active according to the received successful SubscriptionResults and MUST name that subscription's selected event.
An Event before successful Subscribe completion or after successful Unsubscribe completion is invalid.
An Event while Unsubscribe is outstanding remains valid until successful completion.

A message violating these correlation rules, including an unsolicited or duplicate Response or SubscriptionResult, MUST NOT be delivered.
The recipient MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable and MUST close the connection.
A request identifier below the highest transmitted identifier does not by itself establish correlation, because Section 7 permits gaps.

Local timeout, cancellation, or abandonment does not remove the protocol state of a transmitted operation while the connection remains open.
The receiver MUST retain enough information to correlate and validate its eventual result, including the selected response declaration where applicable.
If the local caller no longer awaits a Request's result, the receiver MUST validate and discard its first terminal Response, then retire that outstanding request state.
A later Response for the same identifier is a duplicate.
Sending Cancel does not itself constitute receipt of a terminal Response.

A late matching SubscriptionResult MUST still update protocol subscription state, even if local delivery has been abandoned.
An abandoned local subscription MUST suppress application callbacks, but Events valid under the retained protocol state still require validation before being discarded.
To stop that subscription, the caller MUST complete the Section 5.1 Unsubscribe sequence or close the connection.
Abandonment MUST NOT cause callbacks to access released application state.

Retained correlation state is subject to Section 8.6 limits.
An implementation that cannot retain the state required for an open connection MUST close that connection before discarding the state.
Discarding a late result or Event does not waive any envelope, schema, error-payload, or commitment check.

---

## 4. Request/Response Protocol

### 4.1 Method Calls

```
Caller                                  Callee
  |                                        |
  |--- Request{id:1, method, params, c} --->|
  |                                        |
  |<-- Response{id:1, result, c} -----------|
  |                                        |
```

The caller sends a Request and waits for a Response with the matching `id`.

**Request fields:**
- `id`: caller-assigned according to Section 7
- `method`: the bare method name defined by LOGOS-MODULE-INTERFACE
  (e.g. `"exists"`, `"upload_url"`)
- `params`: a CBOR map matching the method's `_request` schema
- `commitment`: the mandatory payload commitment for `params`

**Response fields:**
- `id`: echoed from the Request
- `result`: a CBOR map matching the method's `_response` schema when the invocation produced a valid contract response
- `commitment`: the mandatory payload commitment for that valid response
- `error`: an `logos.transport.error-payload` when the invocation failed to produce a valid contract response

Exactly one of `result` or `error` MUST be present.
A schema-defined response remains a valid `result`
when it represents an expected domain or application failure.
`response-err.error.code` MUST be nonzero.
An error response MUST NOT contain `commitment`.

The caller MUST generate unique `id` values within a connection. The callee
MUST echo the `id` verbatim.

Every Request, `logos.transport.response-ok`, and Event carries a `logos.transport.payload-commitment`.
The commitment covers only the schema-typed `params`, `result`, or `data` value,
not the Transport envelope.
The target method or event's defining contract supplies the schema root, commitment-model revision, hash profile, and hash suite.
The defining schema root is the session's selected contract root except for the well-known `logos.schema` method, whose defining schema root is the pinned Logos common schema root.
The message's method or event declaration identifies the exact request, response, or event-data type.
`schema_subtree_root` MUST equal the subtree root of that type,
and `value_root` MUST be the root of the transmitted value under those exact inputs.
Both roots MUST have the 32-byte digest length required by
`logos.hash-suite.blake3-256`.

The schema-aware sending boundary MUST compute the commitment from the validated schema-typed value.
A missing, malformed, or incorrectly sized commitment is an envelope failure under Section 2.3.
After the envelope and identifier checks required by Sections 2.3, 3.4, and 7, the schema-aware receiving boundary MUST apply the following declaration-dependent checks in order.
For Requests, selected-contract method resolution and route access checks under Section 8.1 precede these checks.

1. Compare `schema_subtree_root` with the root of the selected request, response, or event-data declaration under the defining contract.
   A mismatch MUST produce ProtocolError `INVALID_PARAMS` when the connection remains writable, followed by session closure, even if the payload also fails that declaration's schema.
2. Validate the complete payload against that declaration.
   A schema-invalid Request MUST produce a correlated `logos.transport.response-err` with `INVALID_PARAMS`, without dispatch; this failure alone MUST NOT terminate the session.
   Any validation detail MUST follow LOGOS-MODULE-INTERFACE Section 5.1.
   A schema-invalid `logos.transport.response-ok` or Event follows the session-closure rule below.
3. For a schema-valid payload, recompute `value_root` under the exact commitment inputs and compare it with the transmitted root.
   A mismatch MUST produce ProtocolError `INVALID_PARAMS` when the connection remains writable, followed by session closure.

The receiver MUST NOT dispatch, accept, or deliver a payload until all applicable checks succeed.
It MUST NOT trust a root merely because the sending module supplied it.
A schema-invalid payload has no valid value commitment under the selected declaration; the receiver MUST NOT substitute a hash of untyped CBOR bytes to classify a value-root mismatch.
Validation and commitment computation MAY be combined, provided the observable failure classification preserves this order.
Resource-limit failures remain subject to Sections 2.3 and 8.6 and MUST NOT be reported as root mismatches without establishing a mismatch.
A caller awaiting a rejected `logos.transport.response-ok` receives `TRANSPORT_ERROR` on session closure.

A `logos.transport.response-ok` or Event whose payload fails its declared response or event schema MUST also be rejected without accepting or delivering that payload.
The schema-aware receiving boundary MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable and MUST close the affected provider session.
This rule applies even when the invalid payload prevents recomputation of its value commitment.
Connection termination follows Section 3.2, including `TRANSPORT_ERROR` for outstanding requests; an invalid Event is never delivered to a subscription handler.

A payload commitment is not a verified-view proof.
Because the complete schema-typed value is already present in the same message,
a Merkle reconstruction path would duplicate information without strengthening verification.
A module contract that intentionally exchanges a partial disclosure
MUST declare the applicable `verified-view` value in its own method or event schema.
Retained call evidence uses the container defined by LOGOS-MODULE-CAPABILITY-AUTHORITY.

### 4.2 Error Responses

```
Caller                                  Callee
  |                                        |
  |--- Request{id:2, method, params, c} --->|
  |                                        |
  |<-- Response{id:2, error:{code, msg}} --|
  |                                        |
```

If the callee cannot produce a valid contract response,
it returns `logos.transport.response-err` with an `error` field
instead of `logos.transport.response-ok` with a `result` field.
An expected domain or application failure defined by the selected response schema
MUST be returned in `response-ok.result`
and MUST NOT be converted to `logos.transport.response-err`.
The error code MUST be nonzero.
When `detail` is present,
it MUST satisfy the code-specific rules in LOGOS-MODULE-INTERFACE Section 5.1.

---

## 5. Event Subscriptions

Message definitions: see Section 1.3
(Subscribe kind 3, Unsubscribe kind 4, Event kind 5, and SubscriptionResult kind 8).

### 5.1 Subscription Lifecycle

The caller assigns a `logos.transport.subscription-id` that is unique for the lifetime of the connection.
A caller MAY subscribe to the same event more than once by using distinct identifiers.
The caller MUST keep at most one subscription-control operation outstanding for one identifier.
After sending Subscribe or Unsubscribe,
the caller MUST wait for its `SubscriptionResult`
before sending another control operation for that identifier.

Unless the connection is terminated, the callee MUST return exactly one `SubscriptionResult` for each syntactically valid Subscribe or Unsubscribe, with the same identifier and matching `operation`.
A successful result contains no `error`.
A failed result contains `error` with a nonzero shared invocation-failure code
and MUST leave the subscription state unchanged.
`SubscriptionResult` carries no payload commitment.

After envelope validation, the callee MUST apply the overlap and identifier checks below before resolving the event name or checking event-subscription access.

For a Subscribe, the callee MUST resolve the event name only under the session's selected contract
and enforce the route's event-subscription access before activation.
An event name outside the selected contract and a selected-contract event outside the route's allowed event-subscription scope
MUST both produce a failed `SubscriptionResult` with error code `NOT_AUTHORISED` and leave the subscription state unchanged.
The callee MUST NOT resolve the event name against the backing provider's other contracts.

For this section, a message is committed when the callee accepts it into the connection's ordered output sequence.

If the callee processes a subscription-control operation for an identifier while the preceding operation's result for that identifier has not been committed, it MUST reject the overlap with ProtocolError `INVALID_PARAMS` when the connection remains writable and close the connection.
It MUST NOT send a SubscriptionResult for the overlapping operation.
This check takes precedence over the identifier-misuse checks below.
It depends on the callee's pending operation state, not on knowledge of whether the caller has received a committed result.

Otherwise, a Subscribe reusing an identifier from any earlier syntactically valid Subscribe on the connection MUST produce a failed SubscriptionResult with `INVALID_PARAMS` and leave the active subscription state unchanged.
The identifier remains used even if the earlier Subscribe failed or the subscription has since ended.
An Unsubscribe naming no active subscription MUST likewise produce a failed SubscriptionResult with `INVALID_PARAMS` and leave the active subscription state unchanged.
The callee MUST retain enough identifier history to enforce non-reuse for the connection's lifetime, subject to Section 8.6; it MUST close the connection before discarding history needed for this check.

Successful Subscribe completion is the subscription activation linearization point.
The callee MUST commit `subscription-result-ok`
before committing the first matching Event for that identifier.
An event committed before activation does not belong to the subscription.
After receiving the successful result,
the caller may treat the subscription as active.

Successful Unsubscribe completion is the subscription deactivation linearization point.
Before committing `subscription-result-ok`,
the callee MUST commit every matching Event already accepted for that subscription.
After committing the successful result,
it MUST NOT commit another Event for that identifier.
After receiving the successful result, the caller has received every Event committed before deactivation.
Receipt does not require application handlers to have run.
Handler execution and successful unsubscription return follow LOGOS-MODULE-INTERFACE Section 2.5.

Closing the connection terminates all of its subscriptions
without requiring individual results.
Ordering is scoped to one connection.
Transport defines no ordering between a subscription operation on one connection
and an event-triggering action on another connection.

**State synchronization.**

The subscription lifecycle defines a delivery boundary
but does not by itself provide a current-state snapshot.
A contract that promises race-free current-state reconstruction
from a snapshot and subsequent events
MUST define one of these synchronization models:

- Snapshot plus revision.
  The snapshot response and every event used for reconstruction
  carry revisions from one ordered revision domain.
  The contract defines which revisions the snapshot includes,
  how a consumer reconciles events buffered around the snapshot request,
  and how it detects and recovers from a revision gap.
- Ordered snapshot and events.
  The contract defines an observation boundary that orders one complete initial snapshot before subsequent change events for that observation.
  It defines the state point represented by the snapshot.
  A watch method using invocation-scoped events can establish this boundary.
  Subscription activation alone does not establish an initial snapshot.

A contract that does not promise current-state reconstruction
need not define either model.
Transport defines no generic snapshot method, revision field,
retained-event log, or recovery protocol.

### 5.2 Event Delivery

Events are one-way and carry no per-event acknowledgement.
A callee MUST NOT silently discard an Event committed to an active subscription.
Transported delivery MAY use bounded buffering.
Accepting an Event into that buffer commits it under Section 5.1.
When output capacity is exhausted, the callee MUST do one of the following:

- delay commitment of additional Events until capacity is available,
  applying backpressure to the publication boundary; or
- send `logos.transport.protocol-error` with `LOGOS_ERR_TRANSPORT`
  when the connection remains writable and close the connection.

If the connection is no longer writable, the callee MUST close it.
Connection closure is the observable failure boundary
and terminates every subscription on that connection.

An implementation MUST document which overflow actions may occur for transported event output and the conditions selecting them.
The documentation MUST state any applicable wait or timeout bounds, including the absence of a finite bound where applicable, and that connection closure terminates all subscriptions on that connection.
These implementation choices do not permit silently discarding an Event already committed to an active subscription.

For ordinary publication, the callee sends Event messages to every authorized active connection that has matching subscription IDs.
Invocation-scoped publication restricts eligible subscriptions under LOGOS-MODULE-RUNTIME Section 7.3.1.
Eligibility is checked at each individual commitment; a destination that ends during publication may prevent delivery to some initially eligible subscriptions.
Previously committed Events retain the buffering and failure rules above.
The `sub` field is scoped to the connection that created the subscription.
Neither publication mode adds a Request identifier to an Event or changes its payload commitment.

The `data` field is a CBOR map matching the event's `_event` schema
(see LOGOS-MODULE-INTERFACE section 1.5).
The `commitment` field is mandatory
and binds `data` according to the payload-commitment rules in Section 4.1.

Events are an asynchronous one-way notification mechanism with schema-defined
payloads, not a second RPC channel.
They are intended for progress, completion, state-change, and other one-way
notifications.
Methods remain request/response.
A callee MUST NOT require an Event message as a reply path for a method
invocation.

### 5.3 Long-Running Operations

A method that produces one delayed result uses one Request and its eventual final Response.
The provider may complete native processing synchronously or use deferred completion under LOGOS-MODULE-INTERFACE.
Neither case requires an acknowledgement method, a job identifier or an event subscription merely to return that result.

When intermediate notifications are needed, the caller activates their subscriptions before starting the invocation.
The provider may publish ordinary events or invocation-scoped events according to the contract's disclosure requirements and LOGOS-MODULE-RUNTIME Section 7.3.
An event may arrive before the caller's native submission operation returns.
The contract MUST NOT require a provider-generated identifier available only in the final Response to be the sole means of recognizing an earlier event.
Event correlation does not grant authority.

A contract may instead define a resource whose lifetime spans method invocations, with methods to start, inspect, read or cancel it.
An acknowledgement is then the final Response of the method that creates or starts the resource.
Any later invocation-scoped events require another active invocation, such as a method that watches the resource.
Cancelling that watch ends observation; it does not cancel the resource unless the contract explicitly assigns that effect.
Ordinary event subscriptions remain independent of these invocations.

These are uses of methods and events, not additional contract declaration kinds.
A contract need not implement a generic job protocol, and an event is not a substitute for a method's final Response.

---

## 6. Cancellation

Message definition: see section 1.3 (Cancel kind 7).

A caller may cancel an in-flight request by sending Cancel with the request's `id`.
The terminal-response linearization point is the commitment of a Response to the connection's ordered output sequence.

If the callee processes Cancel before committing a terminal Response,
it MUST commit exactly one Response with error code `CANCELLED`
and MUST NOT subsequently commit another Response for that request.
The callee SHOULD attempt to stop the operation.
A `CANCELLED` Response does not prove that the operation had no effects.

If the callee commits a terminal Response before processing Cancel,
the Cancel MUST NOT change that Response or cause another Response.

If a Cancel identifier does not identify an in-flight request,
the callee MUST ignore it without emitting a Response or ProtocolError
and MUST leave the connection and request state unchanged.

Transport Event messages identify subscriptions, not requests.
For invocation-scoped publication under LOGOS-MODULE-RUNTIME Section 7.3.1, the provider-side boundary MUST prevent further event commitments through the invocation's destination once it processes Cancel or commits the terminal Response.
This restriction does not retract previously committed Events or cancel the subscription.
It does not affect ordinary publication, another invocation's publication authority or a contract-owned job unless the module contract defines that effect.

The boundary MUST be able to process Cancel without acquiring an ordinary provider-execution slot held by the request being cancelled.
It MUST retain bounded control and output capacity for cancellation or terminate the connection under its existing failure rules.
Committing CANCELLED MUST NOT require provider execution to have stopped.
The implementation chooses its scheduling and numerical capacity limits.

---

## 7. Multiplexing

Multiple requests MAY be in flight on a single socket simultaneously.
Correlation is by `logos.transport.call-id`:

```
Caller                                  Callee
  |                                        |
  |--- Request{id:1, method:"space", c} --->|
  |--- Request{id:2, method:"exists", c} -->|
  |                                        |
  |<-- Response{id:2, result:{...}, c} -----|  (id:2 returns first)
  |<-- Response{id:1, result:{...}, c} -----|
  |                                        |
```

Rules:

- The caller MUST transmit Requests with strictly increasing `id` values on each connection.
  Gaps between consecutive Request `id` values are permitted.
- If no larger `id` is available for a new Request, the caller MUST close the connection without transmitting that Request.
- If a Request's `id` is not greater than the highest Request `id` previously received on the connection,
  the callee MUST NOT dispatch it, MUST send ProtocolError `INVALID_PARAMS` when the connection remains writable, and MUST close the connection.
- The callee need not execute Requests in transmission order.
- The callee MAY respond out of order.
- Cancel identifiers refer to their target Requests and are not part of the Request `id` sequence.
- Event messages for different subscriptions may be interleaved with
  responses.

---

## 8. Security

### 8.1 Route Authorization Material

Route renewal does not by itself replace the authorization decision or expiry of an existing provider session.
The session MUST end when its bound decision expires or is revoked.
A replacement session requires newly issued authorization material and all establishment checks.

The Hello `token` field carries the authorization material required by the selected transport profile.
The base envelope permits an empty value only for a profile
that explicitly does not claim protected route authorization.
An empty value MUST NOT establish a protected local-transport or remote-transport session.

The protected ordinary-provider route profile uses a non-empty, opaque, one-time route ticket
issued or bound by the Runtime that owns the target provider.
The ticket is consumed once to establish one transport session;
it is not consumed separately for each call on that session.
The caller MUST place the ticket in the first Hello and MUST NOT reuse it in a later Hello or another connection.

The Runtime that owns the target provider MUST validate the ticket without consuming it.
After all Hello checks succeed and before returning a Hello response or dispatching an ordinary module message,
that Runtime MUST atomically redeem the ticket at the provider endpoint as part of establishing the session.
Validation MUST bind the session to:

- the consumer and, for a remote session, the authenticated source Runtime that owns that consumer;
- the selected provider;
- the selected contract and route access;
- the target endpoint and Runtime route;
- the authority decision;
- expiry and revocation state.

Only one concurrent redemption of the same ticket may succeed.
A missing, empty, malformed, invalid, expired, revoked, replayed, or incorrectly bound ticket
MUST produce ProtocolError `NOT_AUTHORISED`, close the connection, create no usable session,
and dispatch no ordinary module message.
A Hello failure before successful ticket redemption MUST NOT consume a live ticket.
Failure after successful redemption MUST NOT restore the ticket.
A caller establishing another connection MUST obtain a new ticket.
An expired or revoked ticket record MUST be deleted,
and a replayed ticket remains consumed.
A ticket whose stored selected-contract constraint does not match the selected provider session is incorrectly bound and produces `NOT_AUTHORISED`.
When that constraint matches but the Hello `schema` differs,
the failure is the `VERSION_MISMATCH` defined in Section 3.1.

After successful redemption,
the Runtime that owns the target provider MUST enforce the route's method-call,
event-publication, and event-subscription access
at the provider endpoint for the life of the session.
For every Request, that boundary MUST resolve the bare `method` name
under the session's selected contract
and enforce the corresponding method declaration root before calling any provider method code.
It MUST NOT resolve against the backing provider's other contracts.
A name outside the selected contract produces `METHOD_NOT_FOUND` without calling provider method code.
A selected-contract method outside the route's allowed method scope produces `NOT_AUTHORISED`
without calling provider method code.

The provider-side boundary handles an authorized `logos.schema` Request
as selected-contract introspection under LOGOS-MODULE-INTERFACE.
It MUST NOT forward that request to `logos_<module-C>_MODULE_dispatch()`
or a schema-derived per-method C function.
It MUST NOT return the provider's complete call-surface descriptor or disclose a contract document outside the selected contract's required construction input.
Returning a required interface document does not select that interface contract for the session or widen route access.
When the route expires or is revoked, that Runtime MUST stop admitting new operations and terminate affected subscriptions and the protected session.
In-flight work remains subject to the applicable policy in LOGOS-MODULE-RUNTIME Section 9.3.
A new Request processed during termination MUST receive a correlated `logos.transport.response-err` with `NOT_AUTHORISED`, without dispatch.
Termination MUST NOT wait for another Request or require processing every unread Request.
After any permitted bounded completion of in-flight work, the Runtime MUST send ProtocolError `NOT_AUTHORISED` when the connection remains writable and close the session.
The diagnostic MUST NOT disclose the underlying authorization condition beyond the permitted observation scope.
Sending the error MUST be bounded by the implementation's Transport output and timeout limits; failure to send it MUST NOT delay termination indefinitely.
No peer acknowledgement is required.
The recipient MUST follow Section 3.2, so requests without a terminal Response still fail with `TRANSPORT_ERROR`; the session error does not prove that those operations had no effects.
A known authorization failure governs subsequent new local operations under LOGOS-MODULE-RUNTIME Section 7.5.

The Hello response MUST NOT echo the one-time route ticket.
The response `token` is empty unless the selected profile defines distinct session-bound response material.

Capability Authority decisions and grant references are not route tickets.
Capability Authority does not issue the final provider-session credential or participate in ordinary module data flow.
The baseline ticket encoding, proof of possession, issuer validation, and lifetime
are defined by the profile below.
Another selected security profile MUST define equivalent behavior and a maximum authorization-material size.
Operating-system peer credentials and TLS authentication may strengthen the ordinary provider profile,
but they do not replace route-ticket validation for an ordinary provider session.
Remote Runtime Control connections use the consumer-bound rule defined by LOGOS-MODULE-RUNTIME instead.

LOGOS-MODULE-TRANSPORT defines no provider-enumeration request on an ordinary module endpoint.
Without a valid route ticket bound to one selected provider and contract,
a missing provider, hidden provider, disabled export, invalid route,
and denied provider session MUST produce the same `NOT_AUTHORISED` result and no usable session.
The diagnostic MUST NOT reveal which condition occurred.

Section 8.1.2 defines the separate authorization bindings for Runtime-owned local system-service sessions.
Ordinary consumer-route requirements in this section do not create a consumer or route for those sessions.

#### 8.1.1 Random 256-Bit Route-Ticket Profile

`logos.route-ticket.random-256` is the mandatory route-ticket profile
for ordinary provider sessions over `logos.local.unix-stream`,
`logos.remote.tls-tcp`, and `logos.remote.quic`.
The ticket is an opaque 32-byte string carried directly in the first Hello `token` field.
It is not CBOR, COSE, a Capability Authority decision, or a self-contained authorization claim.

The Runtime that owns the target provider is the ticket issuer.
After it has fixed the route constraints and accepted the required allow decision,
it generates 32 uniformly random bytes with a cryptographically secure random generator
meeting the requirements of RFC 4086.
If the resulting ticket collides with an unexpired ticket issued by that Runtime,
the Runtime MUST discard it and generate another.

The issuer stores the `logos.hash-suite.blake3-256` digest of the ticket
with the complete route constraints listed in Section 8.1.
It MUST protect that record as Runtime authority state
and MUST NOT persist the raw ticket as the lookup key.
The raw ticket may exist transiently only where needed to return the invocation descriptor,
establish the connection, and redeem the ticket.
It MUST NOT appear in logs, audit records, route observations, or error messages.

The ticket MUST expire no later than the route
and no later than 60 seconds after issuance.
The issuer evaluates this short lifetime with its own monotonic clock,
so cross-host clock skew does not apply.
Expiry or loss before redemption requires route renewal or new route establishment;
the same ticket is never reissued.

To validate a ticket, the provider-side Runtime requires an exact 32-byte token,
computes its `logos.hash-suite.blake3-256` digest, and looks up the matching live record without consuming it.
It MUST verify every stored route constraint against the authenticated connection and selected provider session.
For a remote profile, the authenticated source Runtime MUST match the route consumer's `runtime_instance_id` stored in the record.
Possession of the ticket without that remote Runtime authentication is insufficient.
For `logos.local.unix-stream`, the target Runtime associates the redeemed session with the consumer stored in the ticket record
and MUST NOT accept a caller-supplied replacement consumer identity.

After every Hello check succeeds,
the Runtime MUST atomically consume the record as part of committing session establishment.
The record becomes consumed before the Runtime returns a Hello response or dispatches module code.
If the record is no longer live at that atomic step,
the Runtime MUST produce `NOT_AUTHORISED` and MUST NOT establish the session.
The Runtime MUST delete consumed, expired, and revoked ticket records.
After successful redemption,
the authenticated channel binding and consumed ticket record establish the provider session;
the raw ticket has no further protocol role.

This profile uses no signing key, MAC key, separate cryptographic nonce, COSE object, or algorithm negotiation.
The BLAKE3-256 value is used only as a one-way lookup digest for the uniformly random ticket.
The issuer and verifier are the same Runtime,
which already retains state for atomic one-time redemption and revocation.
A self-contained signed ticket would not remove that state requirement.

#### 8.1.2 Runtime-Owned Local System-Service Sessions

A Runtime-owned system-service binding under LOGOS-MODULE-RUNTIME Section 9 MAY use `logos.local.unix-stream` with the ticket algorithm in Section 8.1.1 and the substitutions defined here.
This case is limited to the Runtime engine invoking a bound local service; it MUST NOT authorize an ordinary module route or a remote session.
The session uses the same framing, message directions, module and contract selection, Hello validation order, payload validation, correlation, and resource limits as other provider sessions.

The provider-side admission context MUST obtain the expected credential kind from protected setup bound to the actual listener or accepted session, independently of the received token.
An ordinary route acceptor MUST NOT redeem a system-service ticket, and a system-service acceptor MUST NOT redeem an ordinary route ticket, even for the same provider and contract.
Selecting the kind by searching alternative ticket stores MUST NOT be permitted.
A dedicated endpoint or a protected realization handoff MAY establish this context; an ordinary caller MUST NOT be able to select or replace it.

The target Runtime issues the ticket only after bootstrap or active policy has authorized the system-service binding.
Instead of a module consumer, ordinary route, and provider-access decision, the ticket record MUST bind the issuing Runtime, system-service binding, exact local provider realization, endpoint, selected contract, permitted methods and events, and binding validity and revocation state.
The record MUST identify its system-service purpose explicitly.
The random generation, collision rejection, 32-byte token, BLAKE3-256 lookup digest, secret handling, monotonic lifetime, validation before consumption, single redemption, and record deletion rules of Section 8.1.1 apply unchanged.
The ticket MUST expire no later than the binding and no later than 60 seconds after issuance.
After expiry or loss, Runtime may issue a new ticket only while that exact binding remains authorized; it MUST NOT renew an ordinary module route or reissue the same ticket.

Runtime MUST deliver the ticket only to its protected engine invocation context through authenticated setup.
Sharing an operating-system identity does not by itself authorize another process or module to obtain it.
The caller MUST complete Section 8.2 peer verification before disclosing the ticket.
The target MUST validate every stored binding against the actual session, selected module, exact contract, and current provider realization before atomically redeeming the ticket.
Redemption and admission MUST be ordered with binding invalidation and replacement so a superseded or unauthorized binding cannot establish or use a session.
Invalid, stale, expired, replayed, or wrong-purpose material MUST produce ProtocolError `NOT_AUTHORISED` and no usable session.
The remaining Hello checks and error precedence follow Section 3.1; the response token MUST be empty.

The provider-side boundary MUST enforce the binding's allowed method and event scope throughout the session.
An event or method outside that scope MUST NOT be delivered or dispatched.
Method and subscription access failures use the ordinary `NOT_AUTHORISED` outcomes without widening the binding.
Binding expiry or revocation follows Section 8.1's admission-stop, bounded notification, and session-termination rules, with the system-service binding replacing the ordinary route.
No module consumer, ordinary route, or general engine authority is created by redemption.

### 8.2 Protected Unix-Stream Profile

A shared operating-system user identity is not an isolation boundary between processes of that identity.
Private directory mode bits and matching user or group credentials alone do not prevent a same-identity process from replacing a socket pathname or impersonating its endpoint.
A deployment claiming protection from such processes MUST establish endpoint and credential protection that prevents that substitution and unauthorized credential access, or fail the placement.
A bare process identifier alone MUST NOT establish that protection.
The protected binding must identify the actual trusted endpoint with the required lifetime and race protections, including when listener creation and serving occur in different processes.

Except for Windows applicability under Section 8.2.1, `logos.local.unix-stream` is the mandatory protected local-transport profile for systems that support Unix-domain stream sockets.
It uses the stream framing in Section 2 and the route-ticket profile in Section 8.1.1.

For an ordinary module route, the invocation descriptor carries the exact socket path and one 32-byte route ticket.
For a Runtime-owned system-service session, protected setup supplies the exact path and ticket under Section 8.1.2.
Runtime MUST create a per-instance directory accessible only to Runtime and explicitly launched or authorized consumers.
The directory mode MUST be `0700` on POSIX filesystems.
Runtime MUST reject a pre-existing endpoint path and MUST NOT follow, remove, or replace a symbolic link or another filesystem object at that path.
Under the expected Runtime operating-system identity,
Runtime MUST create and bind the Unix socket and place it in the listening state before transferring its open descriptor through the selected realization mechanism.
The Module Host MUST serve only that transferred listener and MUST NOT bind or substitute another endpoint.
Before accepting the endpoint or marking the provider ready,
Runtime MUST validate the exact transferred listener and its directory, path type, symbolic-link absence, ownership, and listening state.
Failure to transfer the listener securely through a selected placement MUST fail that placement and MUST NOT cause an isolation downgrade.

The protected Runtime context supplying the route descriptor or system-service setup MUST establish the expected Runtime operating-system identity for the caller.
The caller MUST connect to that exact path and verify the connected peer as that identity through `SO_PEERCRED`, `getpeereid()`, or an equivalent operating-system mechanism.
This verification MUST succeed before the caller sends its first Hello or otherwise discloses the route ticket.
On mismatch, the caller MUST close the connection without disclosing or consuming the ticket and report `TRANSPORT_ERROR`.
Runtime MUST fail the affected route or system-service session establishment, and the ticket MUST NOT be accepted after that failure.
An implementation that cannot perform an equivalent peer-identity check does not conform to this profile.

After successful peer verification, the caller MUST place the ticket in its first Hello.
The selected contract in that Hello MUST equal the route's expected contract or the contract of the system-service binding, as applicable.
The target Runtime MUST redeem the ticket before returning a Hello response or dispatching module code.
The response token is empty.
One connection carries one provider session, and connection loss ends that session.

For an ordinary module route, the ticket is the local proof that the caller received the invocation descriptor through an authorized Runtime path.
Runtime MUST disclose an ordinary route ticket only for delivery to that route's consumer through an authenticated invocation context.
System-service ticket delivery follows Section 8.1.2.
Possession by another process is credential compromise;
the short lifetime, single redemption, protected directory, non-logging rule, and revocation behavior limit that residual risk.
This profile defines no fallback to an empty token or an unprotected local session.

#### 8.2.1 Windows Applicability

On Windows, support for AF_UNIX alone does not establish support for `logos.local.unix-stream`.
A Windows implementation MAY support this profile only when it can satisfy the filesystem protection, listener transfer, and peer-verification requirements for the selected placement.
An unsupported placement MUST fail without an unprotected fallback or isolation downgrade.

Runtime MUST protect the endpoint directory, pathname ancestors, and socket with effective access controls that prevent unauthorized endpoint substitution.
Discretionary access-control lists MUST be non-null and MUST NOT acquire permissive entries through inheritance.
Endpoint-use permission alone MUST NOT grant consumers permission to delete, rename, replace, or change security on the endpoint or its containing directory.
Validation MUST recognize the expected `IO_REPARSE_TAG_AF_UNIX` socket object while rejecting symbolic links, junctions, and other redirection or substitution of the selected path.

Runtime MUST transfer only the already-bound listening socket through restricted inheritance or a target-specific Winsock socket-sharing mechanism supported for that socket and placement.
The protected handoff MUST authenticate the target process and expose no unrelated inheritable handles or reusable sharing material.
The Module Host MUST NOT replace a failed handoff by binding another listener.

Before connection, the caller's protected invocation context MUST establish an independently authenticated reference to the process object that the selected operating-system mechanism identifies for the intended listener.
When using `SIO_AF_UNIX_GETPEERPID`, it MUST retain a handle to that expected process object continuously from before connection through peer verification, preventing identifier reuse.
The observed peer identifier MUST match that process object, whose operating-system identity MUST satisfy the expected Runtime identity.
Opening a process solely from an identifier learned from the connection MUST NOT establish the expected reference.
The handle MUST remain within protected context or carry only the rights required for identity and liveness verification.
If that context cannot supply the reference, the process has ended, or verification fails, the caller MUST close before Hello or ticket disclosure and report the Section 8.2 peer-verification failure.

A Windows implementation MUST establish the peer-query attribution and listener-sharing behavior of its supported operating-system versions and placements before claiming support.
It MUST NOT accept either the listener creator or accepting process opportunistically when the required attribution is unknown.
The local descriptor schema is unchanged; the authenticated process reference belongs to protected implementation-local setup, not caller-supplied descriptor data.

### 8.3 CBOR Validation

All incoming CBOR MUST be validated before processing:

- Reject malformed CBOR with `INVALID_PARAMS`
- Reject a length prefix exceeding the size limit before body allocation, send `INVALID_PARAMS` when the connection remains writable, and close the connection as defined in Section 2.1
- Reject non-deterministic envelope CBOR (unsorted keys, non-shortest integers)
  with `INVALID_PARAMS`
- Reject unknown or unallocated message-kind values with `INVALID_PARAMS`
- Validate required envelope fields and envelope field types

For a Hello, required-field and field-type failures are evaluated in the field order defined in Section 3.1.
The framing, deterministic-CBOR, message-kind, and unknown-field checks above take precedence over those field checks.

LOGOS-MODULE-TRANSPORT does not require validation of `params`, `result`, or
`data` against the module's CDDL schema as part of local or remote transport
message handling.
Those payload maps MUST be validated against the target method or event declaration under its defining contract at the schema-aware receiving boundary.
Schema validation at any of those boundaries describes payload shape only.
It MUST occur after the target method and its allowed declaration root are established,
and it MUST NOT authorize a Request or widen the session's route access.
Schema text received through `logos.schema` is subject to the dynamic-schema limits
and resolver restrictions in LOGOS-MODULE-INTERFACE Section 5.3.

### 8.4 Remote Runtime Transport Profiles

These profiles require the caller to establish the carrier to the provider-side listener.
Reachability through NAT, rendezvous, or a relay is deployment-specific unless a separately specified profile defines it.
An intermediary MUST NOT replace required target Runtime authentication or provider-session channel binding.

The `profile` field of a remote Runtime address selects
the complete remote transport and security profile.
An implementation MUST NOT silently substitute another profile or use an unauthenticated carrier.

Production remote profiles MUST bind every accepted provider session
to the authenticated TLS or QUIC connection on which it is established.
Before ordinary module dispatch, Runtime MUST verify all of the following:

- the authenticated target Runtime identity matches the Runtime named by the invocation;
- the authenticated source Runtime identity matches the route consumer's `runtime_instance_id`;
- the selected remote profile matches the invocation endpoint;
- the accepted schema commitment, including its hash profile and hash suite,
  matches the selected contract; and
- the redeemed ticket matches the route, provider, endpoint, and authenticated connection.

Either peer MUST reject the connection if any required binding cannot be verified.
It MUST NOT recover from such a failure by selecting another remote profile,
an earlier TLS version, an unaccepted hash suite, or an unauthenticated carrier.

A peer MUST NOT create or accept a trust anchor or Runtime enrollment
solely because an unknown credential is presented during connection establishment.
The applicable trust anchor and enrollment MUST be established through explicit policy
or authorized provisioning before the connection is accepted.

#### 8.4.1 TLS Over TCP

`logos.remote.tls-tcp` is mandatory to implement
for production remote transport.
It uses a `tls-tcp` Runtime address
and the stream framing defined in Section 2.

Both peers MUST use TLS 1.3 as specified by [RFC 8446]
and MUST reject negotiation of an earlier TLS version.
The connection MUST use mutual TLS authentication.
Protected enrollment MUST select credential and certificate-signature algorithms supported by the intended peers.
A P-256 ECDSA credential using `ecdsa_secp256r1_sha256` is a common enrollment option under the algorithm support required by [RFC 8446] Section 9.1.
Each peer MUST validate the other peer's credential, trust anchor,
and Runtime enrollment before sending or accepting a Transport Hello.
The caller MUST authenticate the target Runtime identity
named by the remote invocation.

For each peer, the verifier MUST select the current active enrollment
for the expected Runtime identity
and `logos.remote.tls-tcp`.
It MUST validate the peer's certificate chain to the trust anchor identified by that enrollment
and require the leaf certificate's DER `SubjectPublicKeyInfo`
to equal one of the enrollment's `subject_public_keys` values.
For an inbound caller whose Runtime identity is not known before TLS authentication,
the accepted public key MUST match exactly one active enrollment under this profile.
No match, multiple Runtime identity matches, a stale or conflicting enrollment,
or a revoked enrollment MUST fail authentication and close the connection.

TLS certificate validation authenticates the enrolled Runtime.

Certificate path validation MUST follow RFC 5280 Section 6.1 under the active enrollment's trust anchor and protected certificate policy.
The verifier MUST check the presented end-entity certificate's validity period using accepted current time, including when that certificate is itself the directly provisioned anchor.
The direct-anchor case requires equality with the provisioned certificate's complete DER encoding; an SPKI match alone does not establish that case.
If end-entity Key Usage is present, it MUST permit digital signatures.
If Extended Key Usage is present, it MUST include `serverAuth` for a TLS server or `clientAuth` for a TLS client, as applicable.
An absent Extended Key Usage imposes no additional purpose restriction; `anyExtendedKeyUsage` alone does not satisfy this profile's explicit-role rule.
TLS proof of private-key possession and the enrollment SPKI match remain mandatory.
Protected policy MUST define accepted current revocation evidence for every non-anchor certificate and reject revoked or unknown required status; active protected enrollment status suffices for the exact directly trusted leaf.
No online revocation protocol is mandated.
Authentication MUST fail if the required time or status cannot be established.

Runtime identity comes from enrollment, not a DNS name or endpoint address.
The baseline does not require DNS-name matching; a deployment may select additional documented name checks without replacing enrollment or key matching.
When `server_name` is supplied, the TLS client MUST send it as RFC 6066 `host_name` SNI and require a DNS name valid for that extension, not an IP literal.
SNI guides credential selection and does not replace peer authentication.
It does not validate the provider, contract, method, request, or response claims made by that Runtime.
Those claims remain bound and checked through the route ticket,
selected provider, schema and method roots, and any required commitment evidence.
If an accepted enrollment becomes revoked or conflicting,
Runtime MUST close the affected authenticated connections and provider sessions.

After the authenticated TLS handshake,
both peers MUST obtain the `tls-exporter` channel-binding value defined by RFC 9266.
That construction uses the registered `EXPORTER-Channel-Binding` label,
a zero-length context, and a 32-byte output.
The output is channel-binding data, not a secret application key.
It MUST NOT be persisted as enrollment state or reused on another connection.

The provider-side Runtime MUST atomically bind successful ticket redemption
and the resulting provider session to that channel-binding value.
The caller MUST bind its local route session to the same value.
One authenticated connection carries one such provider session and channel-binding use.
The connection MUST close when that provider session ends.
Loss of the TLS connection destroys the channel binding,
and the consumed route ticket cannot establish another binding.
The channel-binding value does not authenticate the long-lived Runtime identity
and does not replace certificate and enrollment validation.

This profile does not use TLS session resumption or TLS early data.
The full mutual-authentication handshake MUST complete
before either peer sends Logos Transport application data.

#### 8.4.2 QUIC

`logos.remote.quic` is an optional production profile.
It uses QUIC version 1 as specified by [RFC 9000],
with the TLS integration specified by [RFC 9001].
It applies the same mutual Runtime authentication, enrollment, route-ticket,
and authorization requirements as `logos.remote.tls-tcp`.
For QUIC, each peer selects the active `logos.remote.quic` enrollment
and applies the certificate-chain and public-key matching rules from Section 8.4.1.
It also uses the same RFC 9266 `tls-exporter` value
and provider-session binding defined in Section 8.4.1.

The endpoint address MUST use transport `quic`
and ALPN [RFC 7301] value `logos.remote.quic`.
One QUIC connection carries one Logos provider session
on its first client-initiated bidirectional stream.
The profile does not use additional Logos application streams or QUIC datagrams.

This profile does not use TLS session resumption
or carry Logos application data in QUIC 0-RTT packets.
The TLS handshake MUST complete
before Runtime processes the Transport Hello or any ordinary module message.

QUIC migration is permitted only after successful QUIC path validation.
Migration MUST preserve the authenticated Runtime identity, the selected provider,
and the existing route and session binding.
Runtime MUST close the session if those bindings cannot be preserved.

For every remote profile,
loss of the underlying TLS or QUIC connection ends the provider session.
A redeemed ticket MUST NOT be reused to reconnect.

### 8.5 Implementation-Local Test Hooks

An implementation MAY provide test hooks that inject or observe framed Logos Transport messages without opening a Core remote endpoint.
Such hooks are implementation-local diagnostics,
not transport profiles, Runtime addresses, listener addresses, discovery records, or negotiation choices.
They MUST NOT be advertised to peers or selected as a fallback.
They MUST NOT be used with production credentials, production authority material, live route tickets, or production application data.
A conformance claim MUST NOT depend on another implementation recognizing or supporting an implementation-local test hook.

### 8.6 Resource Limits

Implementations MUST enforce and document finite limits on connections (including incomplete Hello exchanges), outstanding calls, subscriptions, retained correlation and identifier-history state, and bytes retained for Transport input and output.
These limits MUST bound aggregate use across admitted connections.
The documentation MUST identify each limit's scope and behavior on exhaustion.
Numerical limits and scheduling policies are implementation or deployment choices, subject to Sections 2.1 and 2.3.

Resource admission MUST occur before acquiring the bounded resources.
Resource reservations MUST remain held while the corresponding work or storage remains live, including after cancellation or connection closure.
If capacity is unavailable, the implementation MUST either delay admission while retaining bounded state, reject the affected operation using the failure form and error-code semantics for that protocol phase, or refuse or close the affected connection.
Delayed admission MUST observe applicable deadlines and cancellation and connection-closure requirements.
Event backpressure remains subject to Section 5.2.
Resource exhaustion MUST NOT silently discard an accepted Request or a committed Event.
More specific validation and failure rules in this specification take precedence.
Connection closure MUST follow Section 3.2.

Resource bounds do not imply a common retryable overload response or a maximum control-message latency.
An implementation MUST NOT promise that Cancel can overtake a frame already committed to the same ordered stream.

---

## 9. Transport Selection

This specification defines stream bindings for local transport mode and remote
transport mode:

### 9.1 Unix Domain Sockets (Local Transport Mode)

`logos.local.unix-stream` is the mandatory protected local-transport profile for systems that support Unix-domain stream sockets, subject to the Windows applicability requirements in Section 8.2.1.
It is defined in Section 8.2.
The endpoint path is the exact value supplied through the protected context required by Section 8.2.
Its filesystem spelling is not an interoperability identifier.
The caller MUST NOT derive or substitute another path from the module name.

### 9.2 Remote Transport Mode

Production remote transport uses one of the profiles in Section 8.4.
Every conforming remote-transport implementation supports `logos.remote.tls-tcp`.
An implementation may additionally support `logos.remote.quic`.

Both profiles carry the same Logos Transport messages
and enforce the same route and provider-session semantics.
The carrier does not change module contracts, authority decisions, or route access.

### 9.3 Future Request-Oriented Bindings

HTTP-style or other request-oriented bindings are not defined by this
specification.
Such bindings would need a separate interoperability specification that maps
the directional message semantics from section 1.4 onto the carrier,
including authorization and contract-binding metadata, request/response correlation, cancellation,
subscriptions, event delivery, and error handling without assuming a
long-lived bidirectional stream session.

---

## 10. Protocol Evolution

This protocol has no revision field, revision negotiation, or compatible-version range.
The message maps and framing defined by this specification are the protocol.
Peers MUST reject unknown fields and unknown or unallocated message-kind values with ProtocolError `INVALID_PARAMS` when possible and then close.
An incompatible change requires a separately named transport profile whose specification defines its complete framing and message maps.
The two protocols MUST NOT share a connection unless that new profile defines an unambiguous out-of-band selection mechanism.

### 10.1 Commitment Hash-Suite Interoperability

Commitment-aware Hello validation compares `commitment_model`, `schema_root`,
`hash_profile`, and `hash_suite`.
This protocol uses `logos.hash-profile.2026-08.choice-index` with `logos.hash-suite.blake3-256`.
A peer MUST reject another hash profile or hash suite with ProtocolError `VERSION_MISMATCH` and close.
There is no hash-suite negotiation.

---

## References

### Normative

- [RFC 2119] -- Key words for use in RFCs to Indicate Requirement Levels.
  https://www.rfc-editor.org/rfc/rfc2119
- [RFC 8174] -- Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
  https://www.rfc-editor.org/rfc/rfc8174
- [RFC 7301] -- Transport Layer Security Application-Layer Protocol Negotiation Extension.
  https://www.rfc-editor.org/rfc/rfc7301
- [RFC 8446] -- The Transport Layer Security (TLS) Protocol Version 1.3.
  https://www.rfc-editor.org/rfc/rfc8446
- [RFC 9266] -- Channel Bindings for TLS 1.3.
  https://www.rfc-editor.org/rfc/rfc9266
- [RFC 4086] -- Randomness Requirements for Security.
  https://www.rfc-editor.org/rfc/rfc4086
- [RFC 5280] -- Internet X.509 Public Key Infrastructure Certificate and CRL Profile.
  https://www.rfc-editor.org/rfc/rfc5280
- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- [RFC 9000] -- QUIC: A UDP-Based Multiplexed and Secure Transport.
  https://www.rfc-editor.org/rfc/rfc9000
- [RFC 9001] -- Using TLS to Secure QUIC.
  https://www.rfc-editor.org/rfc/rfc9001
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-RUNTIME -- Module admission, lifecycle, and routing specification.
- LOGOS-MODULE-CAPABILITY-AUTHORITY -- Call-evidence container and disclosure requirements.
- LOGOS-MODULE-HASH-PROFILE -- Payload commitments, the required hash profile and suite, and ticket lookup digests.

- [RFC 5280] -- Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile.
  https://www.rfc-editor.org/rfc/rfc5280
- [RFC 6066] -- Transport Layer Security (TLS) Extensions: Extension Definitions.
  https://www.rfc-editor.org/rfc/rfc6066

### Informative

- [COSS] -- Consensus-Oriented Specification System.
  https://rfc.vac.dev/spec/1/

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
