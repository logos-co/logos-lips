# LOGOS-MODULE-TRANSPORT

| Field        | Value                   |
|--------------|-------------------------|
| Name         | Logos Module Transport  |
| Slug         | 305                     |
| Status       | raw                     |
| Category     | Standards Track         |
| Editor       | ksr                     |
| Contributors | Jarrad, atd             |

## Abstract

This specification defines the thin protocol layer on top of the CDDL message
definitions for inter-process and remote Logos module communication.

The message types and their CBOR encodings are fully defined by the CDDL
schemas in section 1. This spec adds only the non-CDDL parts that CDDL
cannot express:

1. **Directional message semantics** — which party may send each message and
   how replies correlate to requests (section 1.4)
2. **Stream binding** — how directional messages are carried over a
   bidirectional byte stream (sections 2 and 3)
3. **Transport binding** — Unix domain socket and TCP stream bindings
   (section 9)

Everything else — message types, field names, value types, error codes —
is defined in CDDL and lives in the schemas below.

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
interface definition format and LOGOS-MODULE-RUNTIME for the module loading
and process model.

This transport does **not** define a different module contract. It is one
runtime realization of the same interface contract defined in
LOGOS-MODULE-INTERFACE. A conforming implementation MUST preserve the same
method names, event names, schema-defined payload shapes, and success/error
semantics that would apply in direct mode.

## 1. Message Envelope

All messages are CBOR-encoded maps.
Each top-level message map carries a required compact message-kind field at
integer key `0`.
This field identifies the transport message type.

### 1.1 Primitive Types

```cddl
; -- primitive types used in the envelope --

protocol-version  = uint
module-name       = tstr .size (1..64)
method-name       = tstr .size (1..128)
; Exact schema event identifier from the module's CDDL, e.g.
; "storage.started_event".
event-name        = tstr .size (1..128)
call-id           = uint
subscription-id   = uint
capability-token  = bstr .size 16
schema-version    = [uint, uint]           ; [major, minor]
semantic-commitment-model-revision = tstr
hash-profile-id   = tstr
hash-suite-id     = tstr
schema-root       = bstr

; This block is the owning registry for transport message-kind values in this
; revision.
; Other Logos specifications may cite these values but do not allocate them.
message-kind      = 0..7

message-kind-hello       = 0
message-kind-request     = 1
message-kind-response    = 2
message-kind-subscribe   = 3
message-kind-unsubscribe = 4
message-kind-event       = 5
message-kind-error       = 6
message-kind-cancel      = 7
```

### 1.2 Message Types

| Kind | Type        | Direction        | Purpose                            |
|------|-------------|------------------|------------------------------------|
| 0    | Hello       | Both             | Peer identification and version/auth metadata |
| 1    | Request     | Caller -> Callee | Method invocation                  |
| 2    | Response    | Callee -> Caller | Method result or error             |
| 3    | Subscribe   | Caller -> Callee | Register for event notifications   |
| 4    | Unsubscribe | Caller -> Callee | Cancel event subscription          |
| 5    | Event       | Callee -> Caller | Async event notification           |
| 6    | Error       | Either           | Protocol-level error               |
| 7    | Cancel      | Caller -> Callee | Abort an in-flight request         |

### 1.3 Message Definitions

**Note on `{ * tstr => any }` in this CDDL:** The transport envelope uses
`any` for the `params`, `result`, and `data` fields because the transport
layer is generic — it carries payloads for any module without knowing the
concrete schema. This does NOT contradict LOGOS-MODULE-INTERFACE section
1.6, which bans `any` in **module schemas**. The transport CDDL is an
envelope spec, not a module schema. Validation against the concrete module
schema happens at the module layer after the transport layer delivers the
message.

The message maps below list the fields defined by this draft revision.
Published transport revisions may add fields.
Implementations MUST ignore unknown fields in known message maps, as specified
in section 10.2.

```cddl
; -- Hello --
; Peer identification and version/auth metadata.
; Stream bindings use Hello during connection establishment.
; The version field carries compatibility version metadata.
; It is not a canonical schema identity or schema root.
; Structural schema identity is carried separately using the commitment model
; and hash profile.

schema-commitment = {
    commitment_model:  semantic-commitment-model-revision,
    schema_root:       schema-root,
    hash_profile:      hash-profile-id,
    hash_suite:        hash-suite-id,
}

hello = {
    0:              message-kind-hello,
    protocol:       protocol-version,
    module:         module-name,
    version:        schema-version,
    token:          capability-token,
    schema:         schema-commitment,
    ? expect_schema: schema-commitment,
}


; -- Request --
; A method call. Params is a CBOR map whose concrete schema is defined
; by the module's .cddl file (see LOGOS-MODULE-INTERFACE section 1.3).
; The transport layer uses a generic map type here; schema validation
; happens at the module layer against the concrete request type.

request = {
    0:      message-kind-request,
    id:     call-id,
    method: method-name,
    params: { * tstr => any },
}


; -- Response --
; Reply to a Request. Exactly one of "result" or "error" MUST be present.
; The result map's concrete schema is defined by the module's .cddl file.
; Schema validation happens at the module layer.
;
; CDDL cannot express "exactly one of two optional fields" directly.
; We use two variants in a choice:

response = response-ok / response-err

response-ok = {
    0:      message-kind-response,
    id:     call-id,
    result: { * tstr => any },
}

response-err = {
    0:     message-kind-response,
    id:    call-id,
    error: error-payload,
}


; -- Subscribe --
; Register interest in a named event.

subscribe = {
    0:     message-kind-subscribe,
    id:    subscription-id,
    event: event-name,
}


; -- Unsubscribe --

unsubscribe = {
    0:  message-kind-unsubscribe,
    id: subscription-id,
}


; -- Event --
; Async event notification to a subscriber. Data is a CBOR map whose
; concrete schema is defined by the module's .cddl file (see
; LOGOS-MODULE-INTERFACE section 1.4). Schema validation at module layer.

event = {
    0:     message-kind-event,
    sub:   subscription-id,
    event: event-name,
    data:  { * tstr => any },
}


; -- Error --
; Protocol-level error (not tied to a specific request).

protocol-error = {
    0:        message-kind-error,
    code:     error-code,
    message:  tstr,
    ? detail: bstr,
}


; -- Cancel --
; Abort an in-flight request.

cancel = {
    0:  message-kind-cancel,
    id: call-id,
}


; -- Error codes --
; Error codes are defined in logos_common.cddl (see LOGOS-MODULE-INTERFACE
; section 5.1) and shared by both the transport and module layers.
; The same numeric codes are used everywhere — no separate transport-only
; error code set.

error-payload = {
    code:     logos_error_code,        ; from logos_common.cddl
    message:  tstr,
    ? detail: bstr,
}

; Imported from logos_common.cddl:
; logos_error_code = &(
;     ok: 0, method_not_found: 1, invalid_params: 2, module_error: 3,
;     not_authorised: 4, transport_error: 5, timeout: 6,
;     version_mismatch: 7, not_ready: 8, cancelled: 9,
; )


; -- Top-level message union --

message = hello
        / request
        / response
        / subscribe
        / unsubscribe
        / event
        / protocol-error
        / cancel
```

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
- `Event`
- `ProtocolError`

`Request` and `Response` messages are correlated by `id`.
The caller assigns the request `id`; the callee echoes that `id` in exactly
one `Response`.

`Subscribe`, `Unsubscribe`, and `Event` messages are correlated by
subscription `id`.
The caller assigns the subscription `id`; the callee includes that value in
matching `Event` messages.

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
Frames larger than that configured maximum MUST be rejected with error code
`INVALID_PARAMS` or `TRANSPORT_ERROR`.

A conforming stream implementation MUST support a configured maximum of at
least 16 MiB.
Portable module interfaces MUST NOT require single transport messages larger
than 16 MiB unless deployment-specific configuration, a transport binding, or a
future protocol extension specifies a larger supported size.

### 2.2 Message Ordering

Messages on a single stream connection are processed in order. However,
multiple requests may be in flight simultaneously (multiplexed by `call-id`).
The callee MAY send responses out of order relative to requests (e.g. a
fast synchronous call may return before a slow one started earlier).

### 2.3 Deterministic CBOR

All messages MUST be encoded using Logos deterministic CBOR as specified in
LOGOS-MODULE-INTERFACE section 4.5.
The transport layer MUST validate the message envelope:
frame length, deterministic CBOR, known message-kind, required envelope fields,
and envelope field types.

The transport layer treats schema payload fields (`params`, `result`, and
`data`) as opaque CBOR maps after envelope validation.
Payload validation against module CDDL schemas is owned by the module host,
generated adapter, native module method boundary, or generated client helper
that interprets the concrete module schema.

---

## 3. Connection Lifecycle

### 3.1 Stream Connection Establishment

```
Caller                                  Callee
  |                                        |
  |--- open socket ----------------------->|
  |                                        |
  |--- Hello{protocol, module,       ----->|
  |         version, token, schema}        |
  |                                        |
  |<-- Hello{protocol, module,       ------|
  |         version, token, schema}        |
  |                                        |
  |    (connection established)            |
  |                                        |
```

1. **Caller opens a socket** to the callee's well-known path
   (`<runtime-dir>/logos_<name>.sock`) or TCP address.

2. **Caller sends Hello.** Fields:
   - `protocol`: the offered transport protocol revision
   - `module`: the callee's selected flat runtime module or endpoint name.
     In this transport specification, "module" includes ordinary modules,
     Logos-defined system modules, runtime-control surfaces, and runtime-host
     endpoints that expose a Logos interface.
   - `version`: the compatibility version metadata the caller expects for the
     callee
   - `token`: a capability token authorising this connection
   - `schema`: structural schema identity of the caller.
     Every transport endpoint exposes a Logos schema and MUST provide this
     field.
     The field identifies the schema of the endpoint participating in this
     transport connection.
     For a runtime-control connection, it identifies the Runtime Control
     contract.
     For an ordinary module invocation connection, it identifies the ordinary
     module contract exposed on that connection.
     It does not identify every module provider, facade, or route known behind a
     runtime.
   - `expect_schema`: optional structural schema identity the caller expects
     for the callee

3. **Callee validates the Hello:**
   - `protocol` MUST be compatible with the callee's supported transport
     revisions, using the negotiation rule in section 10.1.
     If not: Error `VERSION_MISMATCH`.
   - In this draft revision, the `token` field MUST be present and MAY be
     empty.
     If the active runtime security policy enforces capability tokens, the
     token MUST be valid for this caller/callee pair.
     If token validation is enforced and fails: Error `NOT_AUTHORISED`.
   - Schema version MUST be compatible (same major version, caller's minor
     <= callee's minor). If not: Error `VERSION_MISMATCH`.
   - If `expect_schema` is present, the callee MUST compare it with the
     callee's structural schema identity.
     The comparison includes `commitment_model`, `schema_root`,
     `hash_profile`, and `hash_suite`.
     If the callee cannot compute structural schema identity for the selected
     schema, or if any field differs, it MUST send Error `VERSION_MISMATCH`
     and close.
   - The caller's `schema` field MUST be present.
     The callee MUST reject the Hello with Error `VERSION_MISMATCH` and close if
     the field is missing, malformed, or not acceptable under the active runtime
     policy.
   - The callee MAY record the caller's declared `schema` identity for
     diagnostics, policy, authorization, audit, or later routing decisions.
     Transport validation does not require the callee to trust the caller's
     declared `schema` without policy support.
   - On validation failure: callee sends protocol-error and closes.

4. **Callee sends Hello response.** Fields:
   - `protocol`: the negotiated protocol revision
   - `module`: the callee's selected flat runtime module or endpoint name
   - `version`: the callee's current compatibility version metadata
   - `token`: echoed or a session token for the connection
   - `schema`: structural schema identity of the callee.
     The callee MUST provide this field.
   - `expect_schema`: optional structural schema identity the callee expects
     for the caller, when callee-side policy requires the caller to expose a
     particular schema identity

5. **Caller validates the Hello response.**
   The caller MUST validate `protocol`, `module`, `version`, and `token`
   according to the same negotiated-revision and policy rules used for the
   initial Hello.
   The caller MUST verify that the callee response includes a valid `schema`.
   If the caller sent `expect_schema`, it MUST verify that the callee response
   includes a matching `schema`.
   If the callee response includes `expect_schema`, the caller MUST compare it
   with the caller's own structural schema identity and close the connection if
   it cannot satisfy that expectation.

6. **Connection is established.** Both parties may now send directional
   transport messages allowed for their role.

### 3.2 Connection Termination

Either party may close the socket at any time. On close:

- All in-flight requests receive a synthetic `TRANSPORT_ERROR` response.
- All active subscriptions are cancelled.
- The handle on the caller side becomes invalid.

### 3.3 Keep-Alive

For long-lived connections, either party MAY send a Hello message with the
same token as a keep-alive / heartbeat.
The recipient MUST validate it using the same negotiated transport revision and
token policy as the initial Hello, then respond with a Hello.
If validation fails, the recipient sends protocol-error and closes.
This can be used to detect dead connections.

---

## 4. Request/Response Protocol

### 4.1 Method Calls

```
Caller                                  Callee
  |                                        |
  |--- Request{id:1, method, params} ----->|
  |                                        |
  |<-- Response{id:1, result} -------------|
  |                                        |
```

The caller sends a Request and waits for a Response with the matching `id`.

**Request fields:**
- `id`: unique within this connection (caller-assigned)
- `method`: the method name (e.g. `"exists"`, `"upload_url"`)
- `params`: a CBOR map matching the method's `_request` schema

**Response fields:**
- `id`: echoed from the Request
- `result`: a CBOR map matching the method's `_response` schema (on success)
- `error`: an error-payload (on failure)

Exactly one of `result` or `error` MUST be present.

The caller MUST generate unique `id` values within a connection. The callee
MUST echo the `id` verbatim.

### 4.2 Error Responses

```
Caller                                  Callee
  |                                        |
  |--- Request{id:2, method, params} ----->|
  |                                        |
  |<-- Response{id:2, error:{code, msg}} --|
  |                                        |
```

If the callee cannot process a request, it returns a Response with an
`error` field instead of a `result` field.

---

## 5. Event Subscriptions

Message definitions: see section 1.3 (Subscribe kind 3, Unsubscribe kind 4,
Event kind 5).

### 5.1 Subscription Lifecycle

The caller assigns a `subscription-id` (unique within the connection) and
sends Subscribe. The callee records it. Subsequent Event messages include
that `subscription-id` in the `sub` field.

A caller MAY subscribe to the same event multiple times (with different
IDs). Unsubscribe removes one subscription by ID.

Subscribe and Unsubscribe messages have no separate acknowledgement in
this draft revision.
On a single connection, normal connection ordering applies:
a callee processes a Subscribe before any later Request read on that same
connection.
Across different connections, the transport provides no global ordering.
If one connection subscribes while another connection triggers an event, the
caller cannot infer that the subscription was active for that event unless the
application establishes its own ordering.

### 5.2 Event Delivery

Events are fire-and-forget. No acknowledgement. If the caller's socket
buffer is full, the callee MAY drop events (SHOULD log this).

For a given published event, the callee sends Event messages to every active
connection that has matching subscription IDs.
The `sub` field is scoped to the connection that created the subscription.

The `data` field is a CBOR map matching the event's `_event` schema
(see LOGOS-MODULE-INTERFACE section 1.5).

Events are an asynchronous one-way notification mechanism with schema-defined
payloads, not a second RPC channel.
They are intended for progress, completion, state-change, and other one-way
notifications.
Methods remain request/response.
A callee MUST NOT require an Event message as a reply path for a method
invocation.

### 5.3 Async Operations Pattern

1. Caller subscribes to progress/completion events.
2. Caller sends Request.
3. Callee responds with ack.
4. Callee publishes Event messages as the operation progresses.
5. Caller unsubscribes when done.

There is no "async method" concept. All methods are request/response.
Events are orthogonal.

---

## 6. Cancellation

Message definition: see section 1.3 (Cancel kind 7).

A caller may cancel an in-flight request by sending Cancel with the
request's `id`. The callee SHOULD attempt to stop the operation, send a
Response with error code `CANCELLED`, and stop publishing related events.
The callee MAY ignore the cancel if the operation already completed.

---

## 7. Multiplexing

Multiple requests MAY be in flight on a single socket simultaneously.
Correlation is by `call-id`:

```
Caller                                  Callee
  |                                        |
  |--- Request{id:1, method:"space"} ----->|
  |--- Request{id:2, method:"exists"} ---->|
  |                                        |
  |<-- Response{id:2, result:{...}} -------|  (id:2 returns first)
  |<-- Response{id:1, result:{...}} -------|
  |                                        |
```

Rules:

- The caller MUST NOT reuse an `id` that is still in flight.
- The callee MUST NOT assume requests arrive in order.
- The callee MAY respond out of order.
- Event messages for different subscriptions may be interleaved with
  responses.

---

## 8. Security

### 8.1 Capability Tokens

The Hello `token` field (16-byte `bstr`) is reserved for capability-based
authentication. The field MUST be present for wire compatibility but MAY be
empty (`h''`). Token validation is **not enforced** in this draft revision.

Future revisions or security profiles will specify token issuance (via
Capability Module),
validation, and revocation. See LOGOS-MODULE-RUNTIME section 4.3.

### 8.2 Socket Path Security

Unix domain socket paths (`<runtime-dir>/logos_<name>.sock`) are predictable.
To prevent socket squatting:

- Place sockets in a per-instance runtime directory with mode `0700`
  (e.g. `/run/user/<uid>/logos/<instance-id>/`)
- The runtime SHOULD verify socket ownership (via `SO_PEERCRED` or
  `getpeereid()`) after connecting
- The runtime SHOULD delete stale socket files on startup

The runtime host SHOULD derive a fresh instance identity for each local runtime
session and set `LOGOS_RUNTIME_DIR` to the per-instance runtime directory.
Socket filenames inside that directory should remain stable, such as
`logos_<module>.sock`.
The instance identity MAY also be exposed to hosted processes as
`LOGOS_INSTANCE_ID` for diagnostics and host/session correlation, but modules
MUST NOT need it to construct local module socket paths when
`LOGOS_RUNTIME_DIR` is available.

### 8.3 CBOR Validation

All incoming CBOR MUST be validated before processing:

- Reject malformed CBOR with `INVALID_PARAMS`
- Reject messages exceeding the size limit with `INVALID_PARAMS`
- Reject non-deterministic envelope CBOR (unsorted keys, non-shortest integers)
  with `INVALID_PARAMS`
- Reject unknown or unallocated message-kind values with `INVALID_PARAMS`
- Validate required envelope fields and envelope field types

LOGOS-MODULE-TRANSPORT does not require validation of `params`, `result`, or
`data` against the module's CDDL schema as part of local or remote transport
message handling.
Those payload maps are validated by the module host, generated adapter, native
module method boundary, or generated client helper that interprets the concrete
module schema.

### 8.4 TLS (Remote Mode)

For TCP connections (remote module access), TLS 1.3 MUST be used.

This specification requires authenticated and validated TLS connections, but
does not define a single certificate policy.
The exact trust model belongs to the runtime security and authorization
architecture.

Examples include:

- a runtime-managed private CA,
- pinned certificates or public keys,
- or another downstream authentication profile.

Whatever policy is used, a conforming implementation MUST reject unauthenticated
or untrusted peers before any module traffic is accepted.

---

## 9. Transport Selection

This specification defines stream bindings for local transport mode and remote
transport mode:

### 9.1 Unix Domain Sockets (Local Transport Mode)

Default on Linux and macOS. Socket path:

```
<runtime-dir>/logos_<module-name>.sock
```

where `<runtime-dir>` is:
- Linux: `/run/user/<uid>/logos/` or `$XDG_RUNTIME_DIR/logos/`
- macOS: `~/Library/Caches/logos/`

### 9.2 TCP (Remote Transport Mode)

For accessing modules on a remote machine. The runtime connects to
`<host>:<port>` where the module host is listening.

The stream binding is identical to the Unix domain socket binding, except:
- TLS 1.3 is required (section 8.4)

This draft defines commitment-aware Hello fields for structural schema
identity.
Before publication, those fields should be covered by transport conformance
vectors and checked against LOGOS-MODULE-COMMITMENT-MODEL and
LOGOS-MODULE-HASH-PROFILE review feedback.

### 9.3 Future Request-Oriented Bindings

HTTP-style or other request-oriented bindings are not defined by this
specification.
Such bindings would need a separate interoperability specification that maps
the directional message semantics from section 1.4 onto the carrier,
including version/auth metadata, request/response correlation, cancellation,
subscriptions, event delivery, and error handling without assuming a
long-lived bidirectional stream session.

---

## 10. Protocol Revisioning

The transport protocol has a revision number, carried in the `protocol` field
of the Hello message.
This document is still a raw draft and does not assign a final published
transport revision number.
Local prototypes MAY use a temporary numeric value while testing, but that
value is not a published transport revision identifier.

### 10.1 Revision Negotiation

Both parties send their highest supported protocol revision in the Hello.
The connection operates at the **minimum** of the caller's offered revision and
the callee's highest supported revision.
If that negotiated revision is below the callee's minimum supported revision,
the callee MUST send Error `VERSION_MISMATCH` and close.

Published revisions must define their own accepted revision numbers and
minimum-supported revision behavior.

### 10.2 Commitment Hash-Suite Interoperability

Commitment-aware Hello validation compares `commitment_model`, `schema_root`,
`hash_profile`, and `hash_suite`.
This document does not select a production hash suite.

A commitment-aware deployment MUST define the accepted hash profile and hash
suite set by local policy or deployment-specific configuration.
Implementations MUST reject a Hello schema commitment whose `hash_profile` or
`hash_suite` is not in that accepted set.

A published interoperable transport profile that requires commitment-aware Hello
validation MUST select at least one mandatory-to-implement hash suite or define
a deterministic suite-negotiation rule.
Until such a profile is selected, commitment-aware Hello interoperability is
defined only within deployments or conformance vector sets that explicitly
select the same accepted hash profile and hash suite.

### 10.3 Future Revisions

New protocol revisions MAY add:
- New message kinds
- New fields in existing message types (existing fields MUST remain)
- New error codes

Implementations MUST ignore unknown fields in known message maps.
This is the forward-compatibility mechanism for future envelope extensions.

Message-kind values 0 through 7 are allocated in this draft revision.
Receiving an unknown or unallocated message-kind value in this draft revision
MUST yield a protocol error with code `INVALID_PARAMS`.

New protocol revisions MUST NOT:
- Remove existing message types
- Change the meaning of existing fields
- Change the framing format

---

## References

### Normative

- [RFC 8949] -- CBOR: Concise Binary Object Representation.
  https://www.rfc-editor.org/rfc/rfc8949
- [RFC 8610] -- CDDL: Concise Data Definition Language.
  https://www.rfc-editor.org/rfc/rfc8610
- LOGOS-MODULE-INTERFACE -- Module interface definition specification.
- LOGOS-MODULE-RUNTIME -- Module loading and lifecycle specification.

### Informative

- [COSS] -- Consensus-Oriented Specification System.
  https://rfc.vac.dev/spec/1/

---

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).
