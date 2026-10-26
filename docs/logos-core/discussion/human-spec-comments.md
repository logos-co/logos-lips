# Human Concerns — Logos Core module specs

Concerns raised by the project owner while planning logos-core-nim: things that look missing, wrong or
underdefined in the specs. Spec: logos-lips `draft/logos-core-module-specs` at `f4f83471`
(`docs/logos-core/raw/spec-*.md`); short names as in `claude-spec-comments.md` (TRANSPORT, INTERFACE,
RUNTIME, CONFIG, LOADER, PM, CA, SECURITY, BCP, COMMITMENT, HASH, cdCDDLe); `l.N` = line at that commit.

Each concern has a short statement of the concern, what the specs actually say (with references), and
an assessment: **valid**, **partly addressed** (the spec covers some of it) or **partly accurate** (the
premise needs a correction).

## Summary

| ID | Concern | Assessment |
|---|---|---|
| HC-01 | Same module name and contract, different behaviour | valid |
| HC-02 | Several modules in one process; shared libp2p with "filters" | valid |
| HC-03 | Caller identity in method bodies; parameter-level grants | valid |
| HC-04 | No non-breaking contract evolution | valid |
| HC-05 | Calls are synchronous for the caller | partly addressed (async on the wire, sync in the C API) |
| HC-06 | No configurable call timeout or cancellation | valid |
| HC-07 | Mandatory `_dispatch` and typed functions (two APIs that may drift) | valid |
| HC-08 | File paths vs bytes between modules | valid |
| HC-09 | No unified logging | valid |
| HC-10 | `logos_publish_fn` returns void; invalid events dropped silently | valid |
| HC-11 | C ABI ordering is unstable | partly accurate (deterministic, but not append-stable) |
| HC-12 | No alias or stable name for module instances | valid |
| HC-13 | Asking the user at call time | partly addressed (deny-and-retry only) |

---

## HC-01 — Two modules with the same name and contract that behave differently

**Concern:** two modules can share a name and a contract yet not be equivalent (they return different
values), and there seems to be no way to tell them apart or choose between them.

**What the specs say:**
- A contract's identity is its schema root; it describes shape, not behaviour (INTERFACE §1.2: "An exact
  schema root identifies a contract").
- Module names: "Exact flat module names assigned by a Logos specification, package catalog, or
  registry are reserved for that assigned module" (RUNTIME §1.3; INTERFACE §1.3), but no registry or
  enforcement mechanism exists.
- Package signing binds a signer to exact **package** names (PM §4.1 l.404-411), not to module names;
  nothing stops a package signed for `foo` from declaring module `storage_module`.
- Route establishment selects by contract; a consumer may name one provider instance
  (`establish_route_request.provider`, RUNTIME §9.3 l.1912-1918), and CA scopes may restrict
  `providers` (CA §3.1). Execution scopes can pin package/version/artifact (CA §3.3), but a consumer
  cannot ask for "the implementation from publisher X" at route time.
- RUNTIME §9.3 `create_module` selects "one accepted declaration … under active policy" for a module
  name (see `claude-spec-comments.md` RT-04).

**Assessment:** valid. Implementation identity (package, signer) is invisible at the point where a
consumer chooses a provider, and module names are not bound to anyone.

---

## HC-02 — Several modules in one process (e.g. storage and chat sharing one libp2p instance)

**Concern:** there is no way to ask for a module to be loaded into another module's process, e.g. so
storage and chat can share one libp2p instance and each register their own handlers ("filters") on it.

**What the specs say:**
- Hosted realization starts one Module Host per module instance (LOADER l.18, l.87, l.190, l.380; "at
  most one active or failed realization for one module instance", l.362). There is no placement that
  puts two hosted modules into one host process.
- Co-location exists only in the Runtime's own process, via direct mode (RUNTIME §5.2, §5.3 "Hybrid";
  system services MAY be co-located, l.168).
- Module-to-module interaction is only through routes (RUNTIME §7.5).
- There is no consumer-to-provider callback: events flow only from provider to subscribers, and a
  Subscribe carries only an event name, no filter or parameters (TRANSPORT §1.3
  `logos.transport.subscribe = {0, id, event}`; §5).

**Assessment:** valid, two gaps: (1) no co-location group placement for hosted modules (only "everything
in the Runtime process" or "one process each"); (2) no pattern for a consumer to register a handler or
filter with a provider (e.g. a libp2p protocol handler) — it has to be emulated with methods plus
broadcast events, and every subscriber receives every event.

---

## HC-03 — A method cannot see who is calling it

**Concern:** a method body has no access to the caller's identity; without it, per-caller policy is only
possible if grants can constrain parameter values.

**What the specs say:**
- The provider ABI passes no consumer to the module: `logos_<module>_dispatch(module, method,
  params_cbor, params_len, out…)` (INTERFACE §2.6 l.1338-1345) and the typed functions likewise.
- "Authority accepted for an inbound route or call applies only within its allowed scope. It does not
  transfer the consumer's authority to the provider" (CA §2).
- Route access is granular to method and event declarations (`route_access.methods`,
  `subscribe_events`; CA §3.1). No scope constrains parameter values.
- The PM spec itself needs per-caller behaviour ("cursors bound to the authenticated caller", records
  filtered per caller, PM §15) and has no way to get it (`claude-spec-comments.md` PM-03).

**Assessment:** valid. A provider cannot implement per-caller policy (e.g. a keystore that approves
signing only for the module that owns an account), and the CA cannot express "may call `sign` only for
account X". Options a spec could take: pass an authenticated consumer address into dispatch (and typed
calls), or add value-level constraints to `route_access`.

---

## HC-04 — No way to evolve a contract without breaking callers

**Concern:** callers are bound to the exact contract root, so even an additive change (a new method — a
semver-minor bump) breaks every existing caller; there is no way to evolve a contract compatibly.

**What the specs say:**
- "Concrete module, interface contract, and supporting schemas do not carry release or compatibility
  versions. An exact schema root identifies a contract. Two different schema roots are not
  interchangeable unless another specification explicitly defines and selects a cross-root
  transformation" (INTERFACE §1.2).
- The Transport Hello requires exact equality of the schema commitment, else VERSION_MISMATCH
  (TRANSPORT §3.1, §8.3); there is no version negotiation (§10).
- CA scopes and package `requires` pin exact roots (CA §3.1 `contract`; PM §4 `requires`).
- The one escape hatch is `_implements`: a provider can expose several exact interface contracts, and a
  route selects one. But "the bare method names exposed by the primary module contract and all implemented
  interface contracts MUST be unique" (INTERFACE §1.4), so a provider cannot implement `foo_v1` and
  `foo_v2` interfaces that share a method name side by side.

**Assessment:** valid. Any addition yields a new root; every consumer, grant and dependency pin must move
in lockstep, and the `_implements` route to side-by-side versions is blocked by the bare-name rule. The
spec anticipates a future "cross-root transformation" but defines none.

---

## HC-05 — Are calls synchronous for the caller?

**Concern:** calls appear to be synchronous for the caller, leaving asynchrony to the caller's own
threading.

**What the specs say:**
- On the wire, calls are asynchronous: request ids are multiplexed and responses may arrive out of order
  (TRANSPORT §4.1, §7).
- In the C ABI, they are synchronous: the route vtable's `call(route, method, params, out_response…)`
  returns the result (INTERFACE §5.2), as do typed per-method functions; direct calls run synchronously
  on the caller's thread (RUNTIME §6.4). There is no async call or completion callback in the ABI.
- Concurrency is the caller's job: calls may be issued concurrently from any thread (INTERFACE §2.8).
- For long operations, TRANSPORT §5.3 describes a pattern: subscribe to progress events, the request
  returns an acknowledgement, events report progress ("There is no 'async method' concept").

**Assessment:** partly addressed. Async exists on the wire and as an event-based convention, but a
consumer using the C ABI must dedicate a thread per outstanding call.

---

## HC-06 — No configurable timeout or cancellation for calls

**Concern:** there is no configurable call timeout, and it is unclear whether timeouts are meant to be the
caller's job (together with HC-05).

**What the specs say:**
- The route `call` has no timeout parameter (INTERFACE §5.2).
- TRANSPORT defines no call timeout; RUNTIME leaves it to implementations: "In-flight call behavior,
  timeout policy, idle expiry, and retry policy are …" implementation/profile matters (RUNTIME l.2835).
- `LOGOS_ERR_TIMEOUT` exists in the registry (INTERFACE §5.1) with no defined producer.
- TRANSPORT §6 defines Cancel on the wire, but the native route vtable has no cancel operation
  (INTERFACE §5.2: `call`, `release_response`, `subscribe`, `unsubscribe`, `release` only), so a module
  cannot cancel a call through the ABI.
- The only mandatory timeout is the hosted startup timeout (RUNTIME §6.2 l.1089).

**Assessment:** valid. Combined with HC-05, a caller blocked in `call` can neither time it out nor cancel
it, and each implementation will pick different defaults.

---

## HC-07 — Mandatory `_dispatch` and typed functions: two APIs that can drift

**Concern:** providers must export both `_dispatch` and the typed per-method functions — two APIs that
must behave identically and may drift; one should be derived from the other.

**What the specs say:**
- "Provider modules MUST expose both surfaces" with identical semantics (INTERFACE §2.6 l.1222-1244);
  ABI callers may use either (l.1422); both may be called concurrently (l.1536).
- `_dispatch` "is commonly generated from the module's exposed contract set" (INTERFACE App A.3 l.2932,
  informative); code generation is "the expected path" but not a conformance requirement (BCP §6.1);
  a hand-written module must be behaviourally equivalent.
- A Runtime-side derivation of one from the other through a foreign-function interface is explicitly
  not "the interoperable native-host path" (RUNTIME App A l.3480-3482).

**Assessment:** valid. Equivalence is only guaranteed if both come from one generator; otherwise it has to
be tested per module. A spec could make one surface normative and define the other as derivable (e.g.
the Runtime marshals CBOR into the typed call using the layout rules it already specifies).

---

## HC-08 — File paths vs bytes between modules

**Concern:** modules pass host file paths to each other (e.g. a storage download target); since modules
may run on different machines, payload bytes should perhaps go through the contract instead.

**What the specs say:**
- The contract must mean the same in direct, local and remote mode: placement "MUST NOT change … the
  meaning of success and error results" (INTERFACE, Execution-Boundary Invariance; RUNTIME
  "Execution-Boundary Preservation").
- Yet RUNTIME §12 l.3304 suggests "filesystem paths for co-located modules" for large data, and CONFIG
  §6 l.197 only forbids configuration-file paths at the configuration boundary (configured paths are
  otherwise allowed, CONFIG §1 l.53).
- Nothing in a schema marks a method as co-location-only, and a path's meaning changes when the
  provider moves to another host, sandbox or container.

**Assessment:** valid: path-taking methods silently break execution-boundary invariance when the provider
is remote. Related: `claude-spec-comments.md` SO-09 (large payloads).

---

## HC-09 — No unified logging

**Concern:** there is no unified logging mechanism, e.g. one log level set once and applied to every
module.

**What the specs say:** the specs define audit records (CA §9) and Runtime observation, and say what must
never be logged (route tickets, keys: TRANSPORT l.912, SECURITY l.493), but define no logging facility,
log levels, log routing or log retrieval. A module could carry a log level in its own configuration
(CONFIG), but there is no common field, and Runtime Control has no logging operations.

**Assessment:** valid. Each module and implementation invents its own; an operator cannot change verbosity
uniformly or collect module logs through Logos contracts.

---

## HC-10 — `logos_publish_fn` returns void; invalid events vanish

**Concern:** publishing an event has no result: an event that fails validation is dropped and recorded only
as an implementation diagnostic.

**What the specs say:** `typedef void (*logos_publish_fn)(user_data, event_name, cbor_data, cbor_data_len)`
(INTERFACE §5.2 l.2626-2631). RUNTIME §7.3 l.1172-1179: the boundary must validate each event and "MUST
NOT deliver an event whose name, payload, or commitment cannot be validated. Because `logos_publish_fn`
has no result channel, Runtime records that failure as an implementation diagnostic and drops the
event." By contrast, Transport forbids silently dropping accepted events (backpressure or close,
TRANSPORT §5.2).

**Assessment:** valid. A module publishing a malformed event gets no signal; tests and operators see it
only through implementation-specific diagnostics. A result code from publish (or a defined diagnostic
event) would fix it.

---

## HC-11 — C ABI ordering is unstable

**Concern:** the ordering of the C ABI (parameters, choice arms) is unstable.

**What the specs say:** struct fields and method parameters are ordered by field-name bytes, not
declaration order ("Source declaration order is not ABI-visible", INTERFACE §2.1 l.677-682). Choice arms
use the COMMITMENT §9.1 canonical order — sorted by the deterministic-CBOR encoding of each arm's schema
node (COMMITMENT l.1289) — and the C enumerators are `…_ARM_<index>` by that position (INTERFACE l.648-650,
l.882, l.939).

**Assessment:** partly accurate. The order is deterministic, so a given contract always has the same ABI.
It is not append-stable: adding a field can move existing parameters, and adding a choice arm can change
the enum values of existing arms. But any such change also produces a new schema root, so the spec treats
it as a new contract anyway; the ABI instability is a consequence of HC-04, not a separate defect.

---

## HC-12 — No alias or stable name for module instances

**Concern:** instances are created and addressed by module name; `create_module` should accept an alias or
identity for the instance.

**What the specs say:** `create_module_request = {request_key, module}` (RUNTIME §9.3 l.2009-2012); Runtime
mints a fresh `module_instance_id` (`tstr .size(1..128)`, l.1680); several instances of one module name
may exist, and lifecycle operations take an optional `instance` to disambiguate. `request_key` gives
idempotency per consumer, not a shared name.

**Assessment:** valid. There is no operator- or consumer-meaningful instance name (e.g. "storage-archive"
vs "storage-cache"); everything outside the creating consumer must discover opaque instance ids.

---

## HC-13 — Asking the user at call time

**Concern:** there is no specified way to ask the user, at call time, whether a call should be allowed.

**What the specs say:**
- The CA has an `approval-required` denial reason (CA l.459).
- SECURITY §13 l.501-502: approval can create or modify policy or grants, but "the prompt itself is not
  an authority result"; it needs an authenticated approving principal and a trusted administrative path.
  SECURITY §14 l.516: prompt presentation is an application or deployment concern.
- Authorization is decided when a route is established or renewed, not per call (RUNTIME §4.3; §9
  l.1555-1563), and a denied operation fails immediately (RUNTIME §9 l.1565-1568). Consumers can learn
  about new grants through `grant_changed` (CA §8), and retry.

**Assessment:** partly addressed: the spec supports deny-with-`approval-required`, then grant, then retry.
It has no pending/held decision, no way to block a call while the user decides, and no defined human
principal or administrative path for the approval (see `claude-spec-comments.md` SO-06).
