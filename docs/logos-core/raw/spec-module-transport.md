# LOGOS-MODULE-TRANSPORT

| Field    | Value                                      |
|----------|--------------------------------------------|
| Name     | Logos Module Transport                     |
| Slug     | LOGOS-MODULE-TRANSPORT                     |
| Status   | raw                                        |
| Category | Standards Track                            |
| Editor   | ksr                                        |

## Abstract

This specification defines the thin protocol layer on top of the CDDL message
definitions for inter-process and remote Logos module communication.

The message types and their CBOR encodings are fully defined by the CDDL
schemas in section 1. This spec adds only the non-CDDL parts that CDDL
cannot express:

1. **Framing** — how messages are delimited on a byte stream (section 2)
2. **Connection state machine** — handshake ordering (section 3)
3. **Transport binding** — Unix domain socket, TCP (section 9)

Everything else — message types, field names, value types, error codes —
is defined in CDDL and lives in the schemas below.

This spec is intentionally thin. Length-prefixed dCBOR messages over a
stream socket with a Hello handshake. Future versions may add streaming,
multiplexed channels, or compression.

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

All messages are CBOR-encoded maps, each wrapped in a CBOR tag that
identifies the message type. Tags are in the range 100-109 (unassigned
first-come-first-served range in the CBOR tag registry).

### 1.1 Primitive Types

```cddl
; -- primitive types used in the envelope --

protocol-version  = uint                   ; currently 1
module-name       = tstr .size (1..64)
method-name       = tstr .size (1..128)
; Exact schema event identifier from the module's CDDL, e.g.
; "storage.started-event".
event-name        = tstr .size (1..128)
call-id           = uint
subscription-id   = uint
capability-token  = bstr .size 16
schema-version    = [uint, uint]           ; [major, minor]
```

### 1.2 Message Types

| Tag | Type        | Direction        | Purpose                            |
|-----|-------------|------------------|------------------------------------|
| 100 | Hello       | Both             | Connection handshake               |
| 101 | Request     | Caller -> Callee | Method invocation                  |
| 102 | Response    | Callee -> Caller | Method result or error             |
| 103 | Subscribe   | Caller -> Callee | Register for event notifications   |
| 104 | Unsubscribe | Caller -> Callee | Cancel event subscription          |
| 105 | Event       | Callee -> Caller | Async event notification           |
| 106 | Error       | Either           | Protocol-level error               |
| 107 | Cancel      | Caller -> Callee | Abort an in-flight request         |

### 1.3 Message Definitions

**Note on `{ * tstr => any }` in this CDDL:** The transport envelope uses
`any` for the `params`, `result`, and `data` fields because the transport
layer is generic — it carries payloads for any module without knowing the
concrete schema. This does NOT contradict LOGOS-MODULE-INTERFACE section
1.6, which bans `any` in **module schemas**. The transport CDDL is an
envelope spec, not a module schema. Validation against the concrete module
schema happens at the module layer after the transport layer delivers the
message.

```cddl
; -- Hello --
; Sent by caller after opening socket. Callee responds with its own Hello.

hello = #6.100({
    protocol: protocol-version,
    module:   module-name,
    version:  schema-version,
    token:    capability-token,
})


; -- Request --
; A method call. Params is a CBOR map whose concrete schema is defined
; by the module's .cddl file (see LOGOS-MODULE-INTERFACE section 1.3).
; The transport layer uses a generic map type here; schema validation
; happens at the module layer against the concrete request type.

request = #6.101({
    id:     call-id,
    method: method-name,
    params: { * tstr => any },
})


; -- Response --
; Reply to a Request. Exactly one of "result" or "error" MUST be present.
; The result map's concrete schema is defined by the module's .cddl file.
; Schema validation happens at the module layer.
;
; CDDL cannot express "exactly one of two optional fields" directly.
; We use two variants in a choice:

response = #6.102(response-ok / response-err)

response-ok = {
    id:     call-id,
    result: { * tstr => any },
}

response-err = {
    id:    call-id,
    error: error-payload,
}


; -- Subscribe --
; Register interest in a named event.

subscribe = #6.103({
    id:    subscription-id,
    event: event-name,
})


; -- Unsubscribe --

unsubscribe = #6.104({
    id: subscription-id,
})


; -- Event --
; Async event notification to a subscriber. Data is a CBOR map whose
; concrete schema is defined by the module's .cddl file (see
; LOGOS-MODULE-INTERFACE section 1.4). Schema validation at module layer.

event = #6.105({
    sub:   subscription-id,
    event: event-name,
    data:  { * tstr => any },
})


; -- Error --
; Protocol-level error (not tied to a specific request).

protocol-error = #6.106({
    code:     error-code,
    message:  tstr,
    ? detail: bstr,
})


; -- Cancel --
; Abort an in-flight request.

cancel = #6.107({
    id: call-id,
})


; -- Error codes --
; Error codes are defined in logos_common.cddl (see LOGOS-MODULE-INTERFACE
; section 5.1) and shared by both the transport and module layers.
; The same numeric codes are used everywhere — no separate transport-only
; error code set.

error-payload = {
    code:     logos-error-code,        ; from logos_common.cddl
    message:  tstr,
    ? detail: bstr,
}

; Imported from logos_common.cddl:
; logos-error-code = &(
;     ok: 0, method-not-found: 1, invalid-params: 2, module-error: 3,
;     not-authorised: 4, transport-error: 5, timeout: 6,
;     version-mismatch: 7, not-ready: 8, cancelled: 9,
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

---

## 2. Framing

### 2.1 Stream Framing

Messages over a stream socket (Unix domain or TCP) MUST be length-prefixed.
Each message is preceded by a 4-byte big-endian unsigned integer indicating
the byte length of the following CBOR-encoded message:

```
+--------+--------+--------+--------+------- ... -------+
|       length (uint32, big-endian) |  CBOR message      |
+--------+--------+--------+--------+------- ... -------+
```

The maximum message size is 4,294,967,295 bytes (4 GB). Implementations
SHOULD impose a lower configurable limit (default: 16 MB) and reject
messages exceeding it with error code `INVALID_PARAMS`.

### 2.2 Message Ordering

Messages on a single socket connection are processed in order. However,
multiple requests may be in flight simultaneously (multiplexed by `call-id`).
The callee MAY send responses out of order relative to requests (e.g. a
fast synchronous call may return before a slow one started earlier).

### 2.3 Deterministic CBOR

All messages MUST be encoded using deterministic CBOR (dCBOR) as specified
in LOGOS-MODULE-INTERFACE section 4.5. This applies to both the envelope
and the payload (`params`, `result`, `data` fields).

---

## 3. Connection Lifecycle

### 3.1 Connection Establishment

```
Caller                                  Callee
  |                                        |
  |--- open socket ----------------------->|
  |                                        |
  |--- Hello{protocol, module,       ----->|
  |         version, token}                |
  |                                        |
  |<-- Hello{protocol, module,       ------|
  |         version, token}                |
  |                                        |
  |    (connection established)            |
  |                                        |
```

1. **Caller opens a socket** to the callee's well-known path
   (`<runtime-dir>/logos_<name>.sock`) or TCP address.

2. **Caller sends Hello.** Fields:
   - `protocol`: the transport protocol version (currently `1`)
   - `module`: the caller's module name
   - `version`: the schema version the caller expects for the callee
   - `token`: a capability token authorising this connection

3. **Callee validates the Hello:**
   - `protocol` MUST be supported. If not: Error `VERSION_MISMATCH`.
   - Token MUST be valid (issued by the Capability Module for this
     caller/callee pair). If not: Error `NOT_AUTHORISED`.
   - Schema version MUST be compatible (same major version, caller's minor
     <= callee's minor). If not: Error `VERSION_MISMATCH`.
   - On validation failure: callee sends protocol-error and closes.

4. **Callee sends Hello response.** Fields:
   - `protocol`: the callee's protocol version
   - `module`: the callee's module name
   - `version`: the callee's current schema version
   - `token`: echoed or a session token for the connection

5. **Connection is established.** Both parties may now send messages.

### 3.2 Connection Termination

Either party may close the socket at any time. On close:

- All in-flight requests receive a synthetic `TRANSPORT_ERROR` response.
- All active subscriptions are cancelled.
- The handle on the caller side becomes invalid.

### 3.3 Keep-Alive

For long-lived connections, either party MAY send a Hello message with the
same token as a keep-alive / heartbeat. The recipient MUST respond with a
Hello. This can be used to detect dead connections.

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
- `method`: the method name (e.g. `"exists"`, `"upload-url"`)
- `params`: a CBOR map matching the method's `-request` schema

**Response fields:**
- `id`: echoed from the Request
- `result`: a CBOR map matching the method's `-response` schema (on success)
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

Message definitions: see section 1.3 (Subscribe tag 103, Unsubscribe tag
104, Event tag 105).

### 5.1 Subscription Lifecycle

The caller assigns a `subscription-id` (unique within the connection) and
sends Subscribe. The callee records it. Subsequent Event messages include
that `subscription-id` in the `sub` field.

A caller MAY subscribe to the same event multiple times (with different
IDs). Unsubscribe removes one subscription by ID.

### 5.2 Event Delivery

Events are fire-and-forget. No acknowledgement. If the caller's socket
buffer is full, the callee MAY drop events (SHOULD log this).

The `data` field is a CBOR map matching the event's `-event` schema
(see LOGOS-MODULE-INTERFACE section 1.4).

Events are a **narrow asynchronous notification mechanism**, not a second
RPC channel. They are intended for progress, completion, state-change, and
other one-way notifications. Methods remain request/response. A callee MUST
NOT require an Event message as a reply path for a method invocation.

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

Message definition: see section 1.3 (Cancel tag 107).

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
empty (`h''`). Token validation is **not enforced** in the current version.

Future versions will specify token issuance (via Capability Module),
validation, and revocation. See LOGOS-MODULE-RUNTIME section 4.3.

### 8.2 Socket Path Security

Unix domain socket paths (`<runtime-dir>/logos_<name>.sock`) are predictable.
To prevent socket squatting:

- Place sockets in a per-user runtime directory with mode `0700`
  (e.g. `/run/user/<uid>/logos/`)
- The runtime SHOULD verify socket ownership (via `SO_PEERCRED` or
  `getpeereid()`) after connecting
- The runtime SHOULD delete stale socket files on startup

### 8.3 CBOR Validation

All incoming CBOR MUST be validated before processing:

- Reject malformed CBOR with `INVALID_PARAMS`
- Reject messages exceeding the size limit with `INVALID_PARAMS`
- Reject non-deterministic CBOR (unsorted keys, non-shortest integers)
  with `INVALID_PARAMS`
- Reject unknown CBOR tags with `INVALID_PARAMS`
- Validate `params`, `result`, and `data` maps against the module's CDDL
  schema

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

This protocol is used in two modes:

### 9.1 Unix Domain Sockets (Inter-Process)

Default on Linux and macOS. Socket path:

```
<runtime-dir>/logos_<module-name>.sock
```

where `<runtime-dir>` is:
- Linux: `/run/user/<uid>/logos/` or `$XDG_RUNTIME_DIR/logos/`
- macOS: `~/Library/Caches/logos/`

### 9.2 TCP (Remote)

For accessing modules on a remote machine. The runtime connects to
`<host>:<port>` where the module host is listening.

The protocol is identical to Unix domain socket mode, except:
- TLS 1.3 is required (section 8.4)

No additional Hello fields are defined in transport version 1.
Future transport versions MAY extend the Hello message using the normal
versioning rules in section 10.

---

## 10. Protocol Versioning

The transport protocol has a version number, carried in the `protocol` field
of the Hello message. The current protocol version is **1**.

### 10.1 Version Negotiation

Both parties send their protocol version in the Hello. The connection operates
at the **minimum** of the two versions. If the minimum version is below the
recipient's minimum supported version, it MUST send Error `VERSION_MISMATCH`
and close.

### 10.2 Future Versions

New protocol versions MAY add:
- New message types (new tags)
- New fields in existing message types (existing fields MUST remain)
- New error codes

New protocol versions MUST NOT:
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
