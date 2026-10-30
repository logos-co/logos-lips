# Logos Core module specs — second independent audit: gaps, underspecifications and corrections

An independent re-read of logos-lips `draft/logos-core-module-specs` at `f4f83471` (the branch head on
2026-10-29; `docs/logos-core/raw/spec-*.md`), made after and without reuse of the planning session that
produced `claude-spec-comments.md` and `human-spec-comments.md`. Everything listed here was checked
against those two documents and against the decisions record of that session (`DECISIONS.md`, cited as
`[Gn]` / `[Dn]`): an item appears only when no existing entry covers its specific point. Where an
existing entry touches the same area, it is named under **Overlap** and the new point is stated.

Short names and `l.N` line references as in `claude-spec-comments.md`.

**Roles used in scenarios.** Items describe situations with abstract roles rather than real modules:
P is a provider; C, C1, C2 are consumers of P; A is an approval module through which a person accepts
or rejects requests; H is a host application that embeds a Runtime and presents a user interface; D is a
module that uses an OS-mediated device. Concrete cases from existing modules are collected in
`module-port-gaps.md` (Appendix), keyed by the item IDs used here.

**Method.** Twelve topic readings of the specs (events, identity, lifecycle, authority, transport, data
model, packaging, configuration and state, security, presentation, operations, Runtime Control), eight
readings from the point of view of the module families to be ported (listed in `module-port-gaps.md`),
and four re-readings of the existing findings, each by a separate reader. Every candidate then went
through two independent checks: one reader tried to refute it from the spec text, another compared it
with the existing documents and the decisions record. Candidates the refuter settled, or the comparer
found duplicated, are not listed; the main ones are summarised in Part 4 so the work is not repeated.

**Scope difference.** The earlier session planned a headless node. This audit also covers what the specs
must provide for providers that serve several consumers with confidential results, user-approval flows,
OS-mediated device access, graphical presentation modules, several devices and mobile hosts, which is
where most of the new items come from.

Each item gives **Specs**, **Issue**, **Impact**, **Overlap** with existing IDs, and a **Suggested
resolution**.

## Summary

| Part | Count |
|---|---|
| 1. Contradictions and internal inconsistencies | 6 |
| 2. Gaps and underspecifications (events 6, identity 7, lifecycle 11, authority 11, remote 14, data model 9, packaging 10, configuration and state 6, security 3, Runtime Control observation 7) | 84 |
| 3. Corrections and addenda to existing findings | 25 |
| 4. Dropped candidates | 20 |

The items a module author cannot work around inside a module contract are: NX-01 (the Capability
Authority's own change event cannot be filtered as required), NI-01 (a module cannot learn its own
instance address), NI-04 (no way to delete an instance), NL-01 and NL-02 (stop budget and cooperative
stop), NL-05 (no suspend/resume), NA-06 (a provider cannot enforce per-caller policy even if it knew the
caller), NR-01 (no provider-initiated carrier), NR-11 (one outstanding call per route), ND-01 (no
256-bit integers), ND-08 (no shared vocabulary between interface contracts), NP-01 (no human-facing
metadata), NP-02 (no executable artifact), NC-05 (secrets in payloads leave guessable commitments) and
NO-07 (CA actions never mapped to lifecycle methods). NE-01 (results only the requester may see) is not
on the list: the specs require results to travel as method responses, so notification plus fetch works;
what is missing is a statement of that pattern and caller identity for the fetch (HC-03).

---

## Part 1 — Contradictions and internal inconsistencies

### NX-01 — CA §8 requires per-subscriber filtering of `grant_changed`, but a provider's publish path cannot filter
- **Specs:** CA §8 l.671-673 (`grant_changed_event = { grant: grant }`: the full record), l.696 ("The
  event MUST NOT expose targets the subscriber is not authorized to observe"), l.740-743 ("Emission does
  not by itself authorize delivery to every subscriber ... deliver a change event only while the
  subscriber remains authorized for ... the included grant"), §10 l.1114-1116; RUNTIME §1 l.162-168 (a
  Capability Authority realized as code is "a direct-mode local module instance" with ordinary route and
  authority records), §7.3 l.1161-1166, l.1173-1181 ("delivers a validated event to all authorized
  subscribers"), §9.3 l.2644-2645; CA §3.1 l.259-260 and §5 l.468-472 (the authority check for a
  subscription carries the one event declaration and no payload); INTERFACE §2.5 l.1125-1127 (subscription
  is a caller-side binding operation; the provider never sees it).
- **Issue:** the CA must publish `grant_changed` through `logos_publish_fn`, which has no target; the
  Runtime fans the event out per route and can check only the event name; whether subscriber X may see
  grant G is CA visibility policy the Runtime does not hold, and the CA never learns who subscribed. Either
  hidden grants leak to every subscriber (violating l.743) or the CA cannot emit the event, which breaks
  the Runtime's cache invalidation (l.734-738). The Runtime filters its own intrinsic events per target
  (RUNTIME l.2267, l.3180-3183; CONFIG l.282); a module-realized CA gets no equivalent.
- **Impact:** a conformant CA module cannot be written as the specs describe it. The CA's own contract is
  the one place where the specs put confidential content into an event (see NE-01 for the general rule
  that results travel as method responses).
- **Overlap:** CA-03/G49 (meaning of `publish_events`), HC-02, HC-03, HC-13. New: CA §8's payload-dependent
  per-subscriber rule is unimplementable through the RUNTIME §7.3 publish path.
- **Suggested resolution:** apply the notification-plus-fetch shape to the CA's own contract: make
  `grant_changed` carry no grant (a change counter or revision), and let subscribers call `get_grant` /
  `list_grants`, which already filter per authenticated consumer (l.594-596, l.1114-1116) and whose
  `consumer` the Runtime validates before dispatch (l.78-80); the Runtime, as a privileged subscriber, can
  then fetch what its cache invalidation needs (l.737-738). Alternatively make grant visibility a
  Runtime-evaluable attribute (`grant.target == subscriber`) and have the Runtime filter, or give providers
  a subscription-admission hook plus a targeted publish. State which.

### NX-02 — TRANSPORT §5.1's "atomic initial-snapshot event" model has no module-side carrier
- **Specs:** TRANSPORT §5.1 l.684-707 (a contract promising race-free reconstruction MUST define snapshot
  plus revision or an initial-snapshot event "after successful Subscribe completion"; l.706-707 Transport
  defines no snapshot method, revision field or retained log), §1.4 l.311 (the callee is "the party
  exposing the module interface"); INTERFACE §2.5 l.1121-1127, §2.6 l.1201-1236 (the complete provider
  symbol set: no on-subscribe hook), §5.2 l.2626-2631; RUNTIME §4.4 l.944-949, §7.3 l.1181; LOADER
  l.192-195, l.405-406 (the Module Host serves subscriptions).
- **Issue:** a module never observes Subscribe and `logos_publish_fn` broadcasts, so it cannot "commit one
  event containing the complete initial state" for one subscriber; publishing a snapshot anyway delivers
  it to every other subscriber as a spurious change. The Runtime boundary that does see the Subscribe
  holds no module state to snapshot. No Logos contract uses this model (Runtime Control uses revisions).
- **Impact:** every contract that exposes a current value plus change events (a balance, a progress
  counter, the state of a background service) must use model 1, which needs a revision type the common
  schema does not define (ND-02, NO-02).
- **Overlap:** HC-02 (no consumer-to-provider callback), HC-10. New: a normative model with no
  implementation path for module contracts.
- **Suggested resolution:** restrict model 2 to Runtime-intrinsic contracts, or add an optional
  `logos_<module>_on_subscription(context, event_name, subscription)` plus a per-subscription publish
  target; define `logos.revision` and document the snapshot-plus-revision pattern in INTERFACE.

### NX-03 — Per-call versus per-route authorization: CA defines per-call decisions and call records that RUNTIME never produces
- **Specs:** CA §3 l.147-153 (`call` is a separate action), §3.1 l.259-260 (request shape for "a call,
  publication, or subscription on an existing route"), §5 l.435-437 (each action-bearing scope names only
  the action being evaluated), §8 l.748-751 ("Protected operations include new calls"), §9 l.948-953 (a
  `call` audit record MUST contain the decision's `decision_id` and "exactly one" call scope: the `call`
  action, one route, one provider, the selected contract and one method root), §9.1 l.1056 (the verifier
  reads "the single method declaration root"); RUNTIME §4.3 l.923-925, §9 l.1555-1563 (the list of
  operations that need an allow decision omits calls), §4.1 l.805-813 (per-call enforcement is the
  `route_access.methods` check only); TRANSPORT l.824-826, l.851-856; CA §11 l.1131-1141 (the ticket is
  not consumed per call).
- **Issue:** the baseline is route-level and consistent on the RUNTIME/TRANSPORT side, but CA defines a
  per-call vocabulary that nothing triggers and a call-record rule that a route decision cannot satisfy: an
  establish-route decision's scope carries the `establish-route` action and usually several method roots,
  so stamping it onto a call record (CA-06's interim choice) yields a non-conforming record. Nothing says
  when, if ever, a `call`-action evaluation happens, so "a person approves every call to method m" is not
  portably expressible and CA §8's re-evaluation of "new calls" is satisfiable only by re-deciding the
  route.
- **Impact:** a provider P whose method m must be approved per call by a person through A cannot say so in
  policy; CA-06/G52's records would be rejected by a CA-conformant auditor; two Runtimes differ on whether
  each call to m triggers an evaluate round trip.
- **Overlap:** HC-13 (states RUNTIME's side only), CA-06/G52 (notices the audit symptom). New: the two
  specs disagree on when a decision is made; CA-06's interim choice violates CA §9.
- **Suggested resolution:** RUNTIME §9 to state when a call-action decision is requested (for example when
  the route decision carries a `per-operation` marker or lacks `valid_until`) and how a call record is
  formed under a route decision (derive the single-method call scope from the route decision), or CA to
  drop the `call` action and define call records as route-decision derived.

### NX-04 — Module-derived C type names collide with fixed `logos_types.h` names, and the collision rule does not look at the common document
- **Specs:** INTERFACE §2 l.547 (a simple namespace is one lowercase segment; `error`, `schema`, `module`,
  `route`, `runtime`, `tstr`, `bstr`, `tuple` are all valid), §2.1 l.623 (`logos_<namespace>_<type>_t`),
  l.660-670 (common types use one `logos_` prefix: `logos.error_code` -> `logos_error_code_t`), l.655-658
  and l.683 (collision rules scoped to "an accepted schema set"), §1.1 l.104 (the set is module, interface
  and supporting documents), §5.1 l.2353, l.2535-2536 (the common surface is not a supporting schema; its
  declarations are "mapping inputs in the same sense as uint64_t"), §3.1 l.1640, §3.2 l.1666 (the reverse
  mapper reads `logos_error_code_t` as the common type), §3.8 l.1888-1891, §3.9.5 l.2185-2195 (the only
  listed collision case is `a.b` vs `a_b`), §1.3 l.223-238 (reservations cover only CDDL names starting
  `logos.`/`logos-`/`logos_`).
- **Issue:** a module whose namespace is `error` with a type `code` projects to `logos_error_code_t`;
  `module.context` to `logos_module_context_t` (l.968); `route.handle` to `logos_route_handle_t` (l.1185);
  `tstr.size_32` to the fixed `tstr .size 32` projection (l.1633). The accepted-set collision rule never
  compares against the common document, the acceptance list (l.2890-2896) has no C-identifier criterion,
  and the reverse mapper then reads the module's type as the common one, so §3.8's round trip cannot hold
  and nothing rejects the schema. The spec guards C keywords for field names (l.272-274) but not
  namespace/type projections.
- **Impact:** a schema with an ordinary-looking namespace produces a header that redeclares fixed types.
- **Overlap:** IF-09/G69 (function symbols across modules), C-02/G4 (namespace depth). New: collisions
  through the single-prefix exception and the fixed header, and the scope of l.683.
- **Suggested resolution:** an acceptance rule rejecting any derived C identifier equal to a
  `logos_types.h` declaration or a pinned common-type projection (or reserve the namespaces `error`,
  `schema`, `module`, `route`, `runtime`, `result`, `invalid`, `tstr`, `bstr`, `tuple`), plus a §3.9.5
  rejection case.

### NX-05 — RUNTIME's normative dependencies on CA, PM and LOADER are not in its References (extends C-12)
- **Specs:** RUNTIME §8 l.1254 (consumes PM `runtime_handoff`), §2.4 l.419 ("Runtime MUST obtain the
  per-contract discover allow decisions required by LOGOS-MODULE-CAPABILITY-AUTHORITY"), §9 l.1527, l.1599
  (CA call audit record), §13.3 l.3427 (the host binding is typed by `logos.module_loader.static_binding`,
  unconditional for any embedding host), l.3058 (cites LOGOS-PACKAGE-MANIFEST); References l.3675-3688
  (Normative: RFC 5280, RFC 9562, CONFIGURATION, INTERFACE, TRANSPORT; LOADER informative; CA, PM and
  PACKAGE-MANIFEST absent); CA l.1199-1208 and PM l.1563-1571 list no Logos specification at all; LOADER
  l.732 lists RUNTIME as normative.
- **Issue:** C-12 records the CA record-format dependency. The same inversion covers PM and LOADER, and
  RUNTIME's own normative reading list omits all three; the PM and LOADER uses are conditional ("When
  Package Manager supplies a module", l.1253; "When hosted local Transport applies", l.984) but the §13.3
  one is not.
- **Impact:** an implementer reading RUNTIME's normative references misses three documents it depends on.
- **Overlap:** C-12. New: the three-document pattern and the concrete References defect.
- **Suggested resolution:** list CA, PM, PACKAGE-MANIFEST and LOADER as normative references (or move the
  shared record types, `call` audit record, `runtime_handoff`, `static_binding`, into RUNTIME §9.2 or a
  shared-types document) and amend BCP §1 l.50-52 to say layer 2 depends on layer-3 record formats.

### NX-06 — Module-supplied `reason` text has no content rule, unlike every other diagnostic string in the specs
- **Specs:** RUNTIME §9.3 l.1737 (`reason = tstr .size (0..512)`), l.1864, l.2218, l.2227 (carried in
  `module_record`, `module_state_changed_event`, `route_state_changed_event`), l.3088 (`report_failure`:
  "a module-supplied diagnostic", subject only to observation authorization), l.2942-2943 (reason strings
  reach remote observers through facade state), l.1882-1885 (`route_failure.message`); LOADER §10
  l.626-628, PM §14 l.1348-1349, CA §7 l.662-665 (MUST NOT carry credentials, protected policy input, host
  paths, backend configuration).
- **Issue:** a module that calls `report_failure("cannot open /home/u/.../data.db: permission denied")`
  has that host path copied into records, events and remote reflected state with no rule. Three sibling
  specs carry an explicit content rule for the same kind of text; RUNTIME has none and never says whether
  the Runtime may withhold or truncate module text for observers other than the lifecycle controller.
- **Impact:** host paths and other local detail reach every authorized observer, including remote ones.
- **Overlap:** HC-09 (logging), HC-08 (host paths as arguments), EC-10 (`route_failure.code` vocabulary).
  New: the content rule for `reason` and `route_failure.message`.
- **Suggested resolution:** apply the LOADER §10 / CA §7 rule to both fields and state that Runtime MAY
  withhold module-supplied text from observers other than the instance's lifecycle controller.

---

## Part 2 — Gaps and underspecifications

### 2.1 Events and subscriptions

#### NE-01 — Results only the requester may see: the notification-plus-fetch shape is implied but never stated, and its fetch cannot be access-checked without caller identity
- **Specs:** TRANSPORT §5.2 l.736-741 ("Events are an asynchronous one-way notification mechanism ... not a
  second RPC channel ... A callee MUST NOT require an Event message as a reply path for a method
  invocation"), §5.3 l.743-752 (subscribe, request, ack, "Event messages as the operation progresses";
  "There is no 'async method' concept"), §5.2 l.726-727 and §1.3 l.193-197 (Subscribe is `{id, event}`;
  every connection with a matching subscription receives the event); RUNTIME §7.3 l.1181, l.1186-1187,
  l.1189-1195 ("modules MUST NOT model request/reply flows through events"), §9.3 l.2644-2645 (the finest
  route scope is the event declaration root); INTERFACE §1.5 l.366-380 ("Any caller that subscribes to an
  event receives it whenever the module publishes it"; events "do not carry per-call correlation semantics
  beyond subscription"), §5.2 l.2626-2631 (`logos_publish_fn` has no target), §2.6 l.1338-1345 (dispatch
  carries no caller); CA §3.1 l.259-260 and §5 l.468-472 (a subscription decision sees one event
  declaration and no payload). Contrast RUNTIME l.2267 and l.3180-3183 (the Runtime filters its own
  intrinsic events per subscriber) and CA l.78-80 (the Runtime validates the `consumer` of CA requests).
- **Issue:** the specs are consistent on this point: an operation's result travels as a method response,
  which goes only on the requester's route; events are notifications. So "P publishes `op_done{op_id}`,
  C calls `get_result(op_id)`" is the sanctioned shape and keeps the result private. Three things are
  missing or left to each contract:
  1. §5.3 never states the split. It lists "progress/completion events" without saying that they carry
     only correlation data and non-confidential state, that the ack returns the correlation id, or that the
     result is fetched by method. The natural reading of §5.3 puts the result in the completion event,
     which every co-authorized subscriber then receives.
  2. The fetch cannot be access-checked: P does not see who calls `get_result` (HC-03), so it must return
     an unguessable receipt in the ack (the response is private to C's connection) and require it in the
     fetch. The specs never mention this bearer pattern, although the CA gets Runtime-validated caller
     identity for its own methods (CA l.78-80).
  3. Every consumer authorized for the event name receives every other consumer's notifications. Operation
     ids, timing, counts and progress values are visible to co-authorized subscribers, and each consumer
     wakes for all of them; policy can restrict who subscribes per event root but cannot partition by
     operation. Per-consumer progress *content* cannot be private at all.
- **Impact:** two implementations of one contract will differ in whether results ride on events; contracts
  that follow the natural reading of §5.3 leak results; contracts that follow the sanctioned shape need a
  receipt convention the specs do not define and still expose operation metadata.
- **Overlap:** HC-02 (notes in passing that every subscriber receives every event), HC-03, HC-05,
  SO-09/G100 (G100's `{session_id}` plus `*_done_event` is this shape; it is safe when the done event
  carries only the id). New: the unstated split, the fetch's dependence on HC-03, the metadata exposure.
  Where the missing targeted delivery does make the specs inconsistent is NX-01 and NX-02.
- **Suggested resolution:** state in TRANSPORT §5.3 (or an INTERFACE long-operation profile) that progress
  and completion events carry only correlation data and non-confidential state, that the ack returns the
  correlation id, and that results are fetched by method; until HC-03 is fixed, describe the receipt;
  optionally a targeted publish (a route or subscription token the Runtime hands the module with the
  inbound call) for per-consumer progress.

#### NE-02 — No rule orders a call's Response before the Events that call causes; in direct mode the handler runs inside the caller's blocked call
- **Specs:** TRANSPORT §5.3 l.743-752, §6 l.776-778 ("Transport does not associate Event messages with
  individual requests"), §7 l.808-809 (interleaving allowed), §2.2 l.381-384, l.661; RUNTIME §7.2
  l.1150-1153 (the pseudo-code enqueues the Response after dispatch returns, so an event published inside
  dispatch is committed first), §6.4 l.1115 (direct dispatch runs on the caller's thread); INTERFACE §2.8
  l.1554-1558 (direct publish runs every subscriber callback synchronously on the publishing thread),
  l.1560-1564 (re-entrancy is addressed for the publishing module only), l.1570-1576 (a caller must not
  touch its handle concurrently).
- **Issue:** a fast operation (a call on a resource that is already open, an approval granted by an
  unattended rule, a cached response) can commit `op_done{op_id}` before the ack carrying `op_id` reaches
  C, which cannot correlate because it does not know the id yet. In direct mode C's handler executes while
  C is still blocked inside `call` on the same handle.
- **Impact:** every consumer of the §5.3 pattern must buffer notifications for unknown ids; a direct-mode
  consumer that takes a lock around `call` deadlocks in its own handler.
- **Overlap:** SO-09/G100, HC-05. DECISIONS l.1542-1543 (a publisher thread) is a mitigation, not a spec
  finding. New: the ack-versus-caused-event ordering hazard and consumer-side nested delivery.
- **Suggested resolution:** state that events caused by a call MUST be committed or delivered after that
  call's Response (equivalently, a provider MUST NOT publish for a call before returning from dispatch), or
  add a request-correlation field to Event.

#### NE-03 — A consumer is never told that its subscriptions died with the route; observing one's own routes is not a default right
- **Specs:** INTERFACE §5.2 l.2651-2656 (`logos_event_handler_t` has no status variant), l.2722-2755 (the
  route vtable: call, release_response, subscribe, unsubscribe, release), §2.5 l.1161-1165 (silent
  deactivation); RUNTIME §4.4 l.953-956, §7.5 l.1235-1237 ("later calls through the handle MUST fail"),
  §9.3 l.2807-2814 (asynchronous route notifications are a MAY; "Runtime Control is the contract for
  privileged observation of route records"), §9 l.1557-1559, l.3029 (the only default own-route right is
  `close_route`), l.3180-3183, l.2968 (`list_routes` visible to the authorized caller), l.1956-1959
  (`list_routes` filters by target module and provider only); CA §3 l.157-167 (`runtime_control_scope`
  selects by module, instance, provider or route id), §3.2 l.277-279 (policy MAY constrain observation to
  own routes, but no default); TRANSPORT §3.2 l.509-513, l.529-531 (no replay).
- **Issue:** a pure subscriber C with no outstanding call learns that P failed or was recovered only on its
  next failed call, so it must poll.
- **Impact:** every subscriber that matters builds a liveness poll or a periodic re-read.
- **Overlap:** EC-05/G22 (codes for calls through a dead handle), TR-06/G35 (on-wire expiry signal),
  CA-01/G46. New: no consumer-side termination callback, and the only defined signal is optional and
  policy-gated.
- **Suggested resolution:** a terminal notification on the subscription surface (an ended-callback passed
  to subscribe, or a reserved route-ended delivery carrying the failure class) required in every mode; or
  mandate that a route's consumer may observe `route_state_changed_event` for its own routes without a
  separate grant. The second option also needs a `consumers` selector in `runtime_control_scope` and a
  `? consumer` filter on `list_routes`: as written, a scope can select routes only by id (unknown before
  establishment), target module, instance or provider, so a least-privilege "own routes only" grant is
  inexpressible and a `modules: [target]` grant over-discloses every consumer's routes to that module,
  against l.3182-3183.

#### NE-04 — A provider is never told that a consumer's route or session ended
- **Specs:** TRANSPORT §8.2 l.973 (connection loss ends the session), §5.1 l.678; INTERFACE §2.6
  l.1338-1345 (dispatch carries no caller or route identity); RUNTIME §9.3 l.2221-2228
  (`route_state_changed_event` has no `consumer` field), l.1897-1899 (`route_record.consumer` exists
  only in `list_routes`), l.2810-2814 (route observation is privileged), l.3180-3183; CA §3.1 l.157-167 (a
  `runtime_control_scope` can be narrowed to the provider's own address).
- **Issue:** per-consumer state held by P (a lock taken on C's request, a resource unlocked only for C, a
  session held open for C) has no release trigger when C dies. A deployment can grant P observation of its
  inbound routes, but that is a deployment decision, the event carries no consumer, and without HC-03 P
  cannot bind the closed route to the state it holds for C.
- **Impact:** providers fall back to leases with periodic re-assertion by the consumer.
- **Overlap:** HC-03 (the identity half), PM-03/G39 (the Nim interim binds cursors at the host layer,
  which knows about session ends while the module does not), HC-02. New: the lifecycle half.
- **Suggested resolution:** a provider-side session-end notification (route id and consumer address)
  available without a Runtime Control observation grant; at least add `consumer` to
  `route_state_changed_event`.

#### NE-05 — Slow transported subscriber: blocking the publisher versus closing the connection is an unassigned, unbounded choice
- **Specs:** TRANSPORT §5.2 l.709-725 (the callee MUST either delay commitment, "applying backpressure to
  the publication boundary", or send a protocol error and close; closure "terminates every subscription on
  that connection"), §1.3 l.193-197, l.239-245 (no coalesce hint, no lag marker); INTERFACE §2.8
  l.1551-1568 (l.1523-1524 call this "the complete concurrency contract" yet it states blocking only for
  direct mode), §5.2 l.2626-2631 (void publish, no timeout); RUNTIME §6.3 l.1103-1111, §7.3 l.1172-1179;
  SECURITY §10 l.367; CA l.1165 (limits are profile policy); BCP §5.4 l.325-333 (the deployment need not
  document which branch it takes).
- **Issue:** on one Runtime P's publishing thread (often an internal worker of a long-running service)
  blocks inside `logos_publish_fn` behind one stalled subscriber; on another the subscriber's whole
  connection is closed, ending every subscription it held, with no lagged or dropped signal and no
  per-subscription policy. Neither bound nor choice is visible to the contract.
- **Impact:** a slow or suspended UI can stall a provider's internal work on one Runtime and silently lose
  all its subscriptions on another.
- **Overlap:** HC-10 (void publish, drop of invalid events), SO-09, HC-05; G77 and DECISIONS §13 (a
  publisher thread with a bounded queue) mitigate in one implementation. New: the overflow remedy as a
  divergent choice, head-of-line blocking across subscribers, no lag signal or coalesce hint.
- **Suggested resolution:** per-subscription bounded buffering, then either drop with a
  `subscription-lagged` marker or close only that subscription; a coalesce/latest-only hint on Subscribe;
  a stated bound on how long `logos_publish_fn` may block in transported mode.

#### NE-06 — Delivery of a provider's final events during `stopping` is undefined
- **Specs:** INTERFACE §2.6 l.1288 and RUNTIME §6.4 l.1423 (the publish callback stays valid until
  `_destroy` returns), §2.8 l.1589-1591; RUNTIME §3.4 l.592-603 (provider views unavailable "for new routes
  and invocations"; draining is defined for calls), §9.3 l.2680-2681, l.2832 (provider routes fail on
  module stop, with no point within `stopping`), §10.2 l.3255-3257.
- **Issue:** P's final `state_changed{closed}` or `op_done` published while draining or inside `_destroy`
  is ABI-valid but may or may not be delivered, depending on when the Runtime fails P's routes.
  (Pre-`ready` publications are unobservable by construction and need no rule.)
- **Impact:** subscribers cannot rely on a final state event.
- **Overlap:** HC-10, EC-06/G23 (the call side). New: the event-side lifecycle window.
- **Suggested resolution:** state when provider routes and subscriptions are failed during `stopping` (for
  example only once `_destroy` begins, so final events are delivered).

### 2.2 Identity

#### NI-01 — A module cannot learn its own `module_instance_id` or `runtime_instance_id`, yet every self-targeting method needs them
- **Specs:** INTERFACE §5.2 l.2633-2642 (`logos_module_init_input_t`: abi_version, struct_size,
  runtime_control, publish_user_data, publish, state_dir, configuration_cbor/len), l.2668-2720 (the Runtime
  Control vtable has no self-identity operation), §2.6 l.1203 (`_name()` gives the module name only),
  l.2787-2788 (a request is one complete map, so the binding cannot fill a `consumer` field); RUNTIME §9.3
  l.1685-1688 (`module_instance_address` needs both ids), l.2080-2081, l.2117-2130, l.2142-2147,
  l.2161-2163 (configuration, execution-summary and permission-settings requests take a required
  `target`), l.3079-3080 (`report_failure` is the one target-less self method), l.1897 (the only echo is
  `route_record.consumer`, which a module without routes never sees), l.2092-2094 with l.3036 (a
  single-instance module can read `instance` from `get_readiness{module}`, which fails when several
  instances exist and gives no `runtime_instance_id`); CONFIG l.239; CA §5 l.468-470, §6 l.573-575
  (`consumer` required), §10 l.1114.
- **Issue:** a module cannot read its own configuration summary, its own execution summary, or
  `list_grants{consumer: self}` without first discovering an opaque id it was never given; with two
  instances of one module the only workaround breaks. (`state_dir` is already per instance, so per-instance
  storage does not need the id.)
- **Impact:** every self-administering module needs an out-of-band way to learn its address.
- **Overlap:** HC-12 (an operator alias), PM-11/G93 (lists the init fields for artifact paths), HC-03 (the
  mirror image). New: self-knowledge of the instance address.
- **Suggested resolution:** append `module_instance_id` and `runtime_instance_id` (or one
  `module_instance_address` CBOR value) to `logos_module_init_input_t` (the versioned struct allows
  appended fields), or add a `describe_self` Runtime Control method; say whether `route_record.consumer`
  is an acceptable source.

#### NI-02 — `module_provider_id` is called a stable address but has no defined lifetime
- **Specs:** RUNTIME §9.3 l.2505-2515 ("opaque and scoped to the runtime instance that owns the provider
  record"; "the stable address form"), l.2287-2289 (the instance id is lifecycle identity, not provider
  identity), l.2532-2535 (a facade SHOULD carry the remote `provider` id), l.1835-1839 and l.3013-3014
  (exports, possibly from deployment input, name a provider), §2.4 l.399-402 and l.1293 (a provider record
  is created at registration, not with the instance), §10.1 l.3224 (recovery is "a new realization"),
  l.3235 ("Callers require new route acquisition"), l.96 (one record MAY expose several views); CA §3.1
  l.152, l.164-165 (`providers` constraints in durable grants).
- **Issue:** nothing says whether a recovered, re-started or restarted instance keeps its provider id. If
  it does not, a grant pinned to the old id silently stops matching, an export from deployment input dangles
  and a facade points at a dead provider; if it does, the text should say so.
- **Impact:** durable grants, exports and facades naming a provider cannot be written portably.
- **Overlap:** none; G84 (an export supplied from deployment input) and G5 option (a) assume a stable id.
- **Suggested resolution:** bind the provider id to its instance for the instance's lifetime (across
  stop/start, recovery and Runtime restart); say whether one instance has exactly one provider record;
  define how grants, exports and facades naming a non-preserved id are handled.

#### NI-03 — Identity preservation is ambiguous and durable records naming a non-preserved identity have no defined fate
- **Specs:** RUNTIME Terminology l.90 and §9.3 l.2285 (a module instance identity "MAY remain stable across
  stop/start cycles when the Runtime host or deployment preserves" it) vs l.109 ("Runtime MUST preserve
  the addressed module-instance identity while it is needed to keep active routes and retained authority
  or audit material unambiguous"); l.2317-2320 (`runtime_instance_id` persistence is mandated only for the
  tls-tcp/quic profiles); CONFIG l.84-90 (a Runtime that cannot restore a configuration revision MUST mint
  a new identity); CA §6 l.526, l.614 (grant status is only active/expired/revoked); RUNTIME l.2118-2127
  (permission settings keyed by target), l.3075 (retained intent and origin), l.3045.
- **Issue:** grants, permission settings, configuration state and retained intent all name
  `{runtime_instance_id, module_instance_id}`; whether l.109 is a stability guarantee or only an anti-reuse
  rule is unclear; local-profile Runtimes have no `runtime_instance_id` persistence rule; and when the
  CONFIG l.90 new-identity path (or any host non-preservation) is taken, nothing says what the Runtime and
  the CA do with the records naming the old identity: they stay `active` forever (see also NI-07).
- **Impact:** approvals and settings silently stop applying after a Runtime or host loses an identity.
- **Overlap:** CA-01/G46, RT-06/G92, G143 (the Nim layout keeps identities), HC-12.
- **Suggested resolution:** require both address components to persist for the life of the logical
  instance and Runtime in every profile while any durable record names them; define the record fate
  otherwise (for example grants become `revoked` with a reason; a state-migration rule).

#### NI-04 — No operation ever forgets a module instance, and package removal is blind to instances
- **Specs:** RUNTIME §9.3 l.1912-2191 (the complete request set: create/start/stop/recover_module,
  report_failure, shutdown_runtime, get/update/apply configuration and permission methods, route, listener
  and export methods; no remove/destroy/forget), l.3095-3103 ("retain a successful key-to-instance
  association while the created instance remains known": an end that is never defined), Terminology l.109,
  §3.4 l.541 (`unloaded` instances remain known), §8 l.1318-1319 (state deletion is policy), l.3056-3059,
  l.3072 (recovery rechecks realization acceptance and fails forever for a removed package), l.3131-3134
  ("An authorized module may coordinate those workflows before invoking stop_module"), §10.1 l.3214
  (bounded retries); PM §15 l.1492-1498 (`remove_package` checks only package dependency edges), §14
  l.1340, §4.1 l.429 ("Whether an already-running module is stopped is a separate Runtime and
  active-authority decision"), §5 l.765, Scope l.123-125 (no lifecycle event stream, no module lifecycle
  semantics); LOADER §5.1 l.283-284; CA §3 l.174 (an `unload` action) and §3.5 l.357 (a deletion
  facility) with no Runtime Control counterpart.
- **Issue:** deleting an instance (its record, request_key association, configuration revision history,
  permission settings and the state behind its assignment, which may hold encrypted user data or hundreds
  of GB) has no spec path; uninstalling a package leaves an instance with retained intent known forever,
  with recovery failing at every start under the restart policy; `list_modules` accumulates every instance
  ever created.
- **Impact:** a host's uninstall flow cannot complete through Logos contracts; the implementation plan
  went out of band (G143: a purge tool run with the daemon stopped).
- **Overlap:** RT-06/G92 (moving to a newer package), G143 (filed as a FREE retention choice), HC-12.
  New: no deletion operation at all; `remove_package`/`update_package` cannot see instances retaining the
  package; a retained selection whose package is gone has no defined observable state.
- **Suggested resolution:** `destroy_module {instance, ? delete_state}` valid for `unloaded`/`error`
  with intent not `requested`, forgetting the record, key association, configuration and permission state,
  reporting the state assignment's fate as a policy-governed field and emitting a terminal event; in PM §15
  either fail `remove_package`/`update_package` with `package-in-use` while a Runtime-known instance
  retains the package (with a force flag) or define that removal moves affected instances to `error` with a
  typed `package-removed` reason not subject to retry.

#### NI-05 — Omitting `instance` under ambiguity has no rule and no error code; events and the stop response may omit `instance` for local instances
- **Specs:** RUNTIME §9.3 l.3127-3129 ("If no ambiguity exists, the caller MAY omit instance"),
  l.2297-2301 ("live" instances vs "runtime-known" instances: two populations, no test), l.3114 ("target
  selection" named once as a rejection class, no code), l.2213-2219 (`module_state_changed_event` has
  `? instance`), l.2031-2041 (`stop_module_request/response` `? instance`) vs l.2025-2029 and l.2049-2053
  (start and recover responses require it), l.3036 (the `instance` MUST covers only `module_record` and
  `get_readiness_response`), l.2774-2776 (unknown vs hidden targets must be indistinguishable), §3.2
  l.463-476 (the registry sketch is keyed by module name).
- **Issue:** with two instances of one module name, a subscriber cannot tell which one failed, and a
  `stop_module{module}` fails with an unspecified code that discloses that more than one instance exists to
  a caller who may observe only one.
- **Impact:** multi-instance deployments cannot be observed or controlled portably.
- **Overlap:** HC-12, C-06/G58, EC-03/G20. New: the ambiguity rule, its code and its non-disclosure
  interaction; `instance` optional on the event and the stop response.
- **Suggested resolution:** an omitted `instance` is valid only when exactly one instance record (any state)
  exists for the name, otherwise INVALID_PARAMS with a named reason (or non-revealing NOT_AUTHORISED when
  the caller lacks observation authority); `instance` MUST be present on every record and event describing a
  local instance.

#### NI-06 — The verified signer is not retained in any Package Manager record, handoff or CA scope
- **Specs:** PM §4.3 l.528 (the authenticated `kid` is known at verification), §5 l.722-730
  (`installed_package_record`), §6 l.774-783 (catalog entry, inspect record), §12 l.1241-1250
  (`runtime_handoff`), §4.1 l.427-429 (anchor revocation defers the running-instance decision to Runtime
  and the CA), l.420-422 (the verification cache must be invalidated per signer); CA §3.3 l.169-181
  (`module_execution_scope` pins package/version/artifact, never signer); RUNTIME l.2065-2075.
- **Issue:** the PM verifies the signer and then omits it from all its outputs, so an installer UI cannot
  show who signed, group by publisher or detect a signer change across an upgrade (pin-on-first-use), a
  provider chooser cannot say "same publisher as the requesting module", and the Runtime/CA decision that
  l.429 defers to has no input.
- **Impact:** publisher identity is invisible after installation.
- **Overlap:** HC-01 (publisher invisible at route time). New: the PM's own records drop it.
- **Suggested resolution:** record `signer` (the profile's `kid`) and the accepting trust-anchor id in
  `installed_package_record` and `package_inspect_record`, carry them in `runtime_handoff` and
  `get_execution_summary.selection`, and allow `module_execution_scope` to constrain by signer.

#### NI-07 — Grants outlive their target: no orphaned or retired grant state, and a grant target can only be an instance address
- **Specs:** CA §6 l.529-539 (`target: module_instance_address`), l.613-616 (the only transitions are
  active -> expired / revoked); RUNTIME l.109, l.3098 (`create_module` always mints a fresh identity);
  §9.3 l.2960-3150 (no retire operation).
- **Issue:** after an upgrade by new instance (RT-06/G92) or any identity loss (NI-03), a remembered
  approval "C may call method m on P" targets an address that no longer resolves; the grant stays `active`
  with no status, event or filter distinguishing it, and the person's approval is lost.
- **Impact:** every upgrade silently drops remembered approvals while stale grants accumulate.
- **Overlap:** HC-12, RT-06/G92. New: grant lifecycle versus target lifecycle. (G143's "identity and state
  survive package update" conflicts with G92's new-instance decision; see NF-17.)
- **Suggested resolution:** an `orphaned` status or auto-revoke with `revocation_reason` plus a
  `grant_changed` event when the target is forgotten; allow a grant target expressed by a stable selector
  (the HC-12 alias) that Runtime resolves to the current instance.

### 2.3 Lifecycle

#### NL-01 — The stop grace period is named but never defined, and a module can neither learn, declare, extend nor report progress against it
- **Specs:** RUNTIME §10.2 l.3262-3269 (l.3265 "within the active grace period" is the only occurrence of
  "grace period" in the twelve files; forced cleanup is a MAY; l.3269 "shutdown policy" undefined), §3.4
  l.592-601 (the per-instance stop names no grace at all: "drains or fails in-flight work according to
  active policy"), l.3271, §6.2 l.1089 (the equally undefined "startup timeout"), §9.3 l.3085
  (`report_failure` is rejected outside `loaded`/`ready`), l.592-594 (no Runtime Control calls once
  `stopping`), l.2832 (provider routes failed on stop, so progress events reach nobody); INTERFACE §2.6
  l.1331 (`void _destroy(context)`), §2.8 l.1584-1592 (the module must join all work before returning);
  LOADER §9 l.541-545 (`release_request` carries only `? force`), l.558-576 (force proves nothing about
  cooperative cleanup); PM §4 l.271-279 (no declaration field); BCP §5.4 l.327-328 (arguably obliges a
  deployment to document a value, not a mechanism); RUNTIME §10.1 l.3209 (direct realizations share the
  Runtime's process: a slow `_destroy` cannot be forced without killing the Runtime).
- **Issue:** `_destroy` is the single stop phase; the module receives no deadline, cannot ask for more
  time and cannot report progress; the deployment's uniform value is right for no module in particular.
- **Impact:** a module wrapping a native service whose orderly stop flushes caches or databases for
  seconds to minutes either has its state corrupted by a short grace or stalls host shutdown under a long
  one, and a module that cannot interrupt a running native call has no way to say so.
- **Overlap:** G61 (fixes "stop drain 10 s, shutdown grace 10 s per realization then force-release" as a
  FREE deployment default without asking whether the module can see or influence it), HC-06 (call
  timeouts). New: no module-visible deadline, no declared budget, no extension or progress channel, no
  spec source for the value.
- **Suggested resolution:** a declared stop budget in the module declaration or handoff that Runtime MUST
  honour up to a deployment cap; pass the effective deadline to the module (a `prepare_stop(deadline)` hook
  or a `_destroy` parameter); let stopping progress be observable through Runtime Control; put the grace
  policy into BCP §5.4's required documentation; state the forced-cleanup default and that direct
  realizations cannot be force-released.

#### NL-02 — No cooperative pre-stop phase: a stopping module loses its outbound routes before `_destroy`, and shutdown closes all admission before the reverse-order release
- **Specs:** RUNTIME §3.4 l.592-600 (the order: `stopping`, provider views unavailable, "prevents new
  outbound method calls and new Runtime Control contract calls", drain, destruction; l.600 "Runtime MUST
  close every route whose consumer is that module instance"), §9.3 l.3146, §10.2 l.3253-3261 (step 1
  quiesces every instance's invocation paths; step 3 releases in reverse dependency order), §3.7 l.707-712
  (constraints apply in reverse "during graceful shutdown", but step-1 quiescence is not ordered), l.3131-3134
  (an authorized module "may coordinate those workflows before invoking stop_module", which does not exist
  for host-initiated shutdown, l.3250); INTERFACE §2.8 l.1584-1595.
- **Issue:** by the time C's only stop hook runs, its routes to P are closed, so C can neither finish an
  in-flight multi-step flow through P, nor cancel a request pending at P, nor checkpoint through P; the
  reverse-order release protects nothing, because a dependent can no longer call its prerequisite from
  `_destroy`. (In-flight outbound calls MAY complete under l.596; new ones cannot be issued.)
- **Impact:** resources a stopping module holds at other modules (sessions, pending requests, open
  handles) leak until the provider restarts or a lease expires.
- **Overlap:** EC-06/G23 (calls into a stopping provider), CA-01/G46, G142 (deployment ordering). New: the
  stopping module's own outbound work is cut before it learns of the stop; reverse-order release is vacuous
  for cooperative draining.
- **Suggested resolution:** a `prepare_stop` phase (per instance and at shutdown) during which the
  instance keeps its consumer routes until the grace deadline and may answer busy/needs-time; make §10.2
  step 1's admission closure per instance in reverse dependency order rather than runtime-wide.

#### NL-03 — `_destroy` returns void: a cleanup failure cannot be reported although `error` is defined to include one
- **Specs:** INTERFACE §2.6 l.1331, l.2986-2987; RUNTIME §3.4 l.549-550 ("error: Realization,
  initialization, readiness, execution, or cleanup failed"), §10.2 l.3269, l.3272-3273 (Runtime maps
  realization and cleanup failures, which originate in the realization mechanism), l.3085 and l.594 (the
  module's report paths are closed during destruction); LOADER l.584-585, l.609, l.619-620 (incomplete
  release is Loader-observed non-absence, not a module-reported outcome); RUNTIME §13.3 l.3416
  (`logos_runtime_destroy` returns `logos_result_t`: the asymmetry).
- **Issue:** a failed final flush or database close that returns is indistinguishable from a clean stop;
  the only cleanup failure the Runtime can map into `error` is non-return within the grace period.
- **Impact:** a UI cannot warn that persistent state may be damaged; an orchestrator cannot tell a clean
  stop from a failed one.
- **Overlap:** HC-10 (void publish), G60 (`wait_for_shutdown` returns MODULE_ERROR "when cleanup failures
  were recorded", which presupposes a recorder that exists only for realization-observed failures).
- **Suggested resolution:** return `logos_result_t` from `_destroy` (or admit a `report_cleanup` Runtime
  Control call during `stopping`) and surface it as a typed reason on `module_state_changed_event`.

#### NL-04 — The startup timeout has no source, cannot interrupt `_init`, and the mandated release is serialized behind the pending `realize`
- **Specs:** RUNTIME §6.2 l.1082-1093 (the sole mention of a startup timeout: not a manifest field, not a
  named option, not a profile input; at expiry "Runtime MUST initiate release through the same mechanism
  that established the realization"), §8.1 l.1431-1436, §10.1 l.3211-3215 (bounded retry policy); LOADER
  §6 l.404-411 (`realize` returns no intermediate state), §9 l.541-542 (`release_request` needs a
  `realization_id` that does not yet exist), §11 l.633-634 (per-instance total order queues the release
  behind the in-flight realize), l.413-414; INTERFACE §2.6 l.1266-1277, l.1454-1467 (heavy work belongs in
  a schema `init`, not lifecycle `_init`: the spec's intended answer).
- **Issue:** in hosted mode the only exit from an `_init` that outlives the timeout is envelope termination
  by a non-Loader mechanism; in direct mode nothing can interrupt it at all; no declarable startup budget
  exists; restart policy has no carve-out for startup-timeout failures.
- **Impact:** a module whose `_init` opens a large database or runs migrations on a slow disk is killed
  and restarted repeatedly while making progress.
- **Overlap:** G61 (120 s FREE), G136 (a payload module split its start into phases, the intended
  workaround), HC-06.
- **Suggested resolution:** define the timeout's source; define the ABI caller's behaviour when `_init`
  outlives it (never call `_destroy`; hosted: terminate the envelope; direct: wait and report with a typed
  reason); exclude startup-timeout failures from automatic recovery unless policy opts in.

#### NL-05 — No suspend/resume or background/foreground notion anywhere
- **Specs:** RUNTIME §3.4 l.530-549, l.587 (exactly five states; "There is no separate active module
  state"), §13.2 l.3347-3356 and §13.3 l.3405-3416 (six host operations: Construct, Register bindings,
  Start, Request shutdown, Wait for shutdown, Destroy), l.3453 (startup once per handle), l.3321 (the host
  has no consumer identity, so it cannot call `stop_module`), l.3361 (no host-driven hook), §5.2
  l.1007-1017 (single-process mobile mode); INTERFACE §2.6 l.1201-1210 (symbol set), l.1263 (post-init
  callback setters forbidden), l.1272-1273 (OS kill without `_destroy` is anticipated); SECURITY §11
  l.377-378 ("background work" is a platform-profile matter), §11.4 l.425, §11.5 l.438-441 (the "iOS-specific
  transport and lifecycle profile" is only for separate application or extension providers; the in-app
  direct-mode baseline has no profile reference), §11.6 l.455; BCP l.282-287 (a profile cannot create an
  independent Core layer, so it has no extension point to add a state, hook, event or host operation).
- **Issue:** when a mobile OS suspends the application, the host's only tools are `stop_module` (which
  destroys the context: unsealed keys and per-session unlocks held in memory are gone, an in-progress chunk
  of work and a pending approval are lost) or leaving modules running until the OS kills the process with
  `_destroy` never called. A module holding long-lived network sessions needs to go dormant and resume; a
  module doing incremental work needs to pause at a boundary.
- **Impact:** every backgrounding is a full teardown or an unclean kill.
- **Overlap:** none; D19, G105, G106, G125 cover mobile composition and transport, never lifecycle.
- **Suggested resolution:** Suspend/Resume host operations (context kept; Runtime quiesces routes and
  timers; instance identity and intent preserved; no `_destroy`) propagated as an optional module hook to
  flush and relock; write the mobile lifecycle profile SECURITY §11.5 refers to, for the in-app baseline
  too.

#### NL-06 — `error` state: whether cleanup moves the instance to `unloaded` is undefined, and `start_module` and `recover_module` have different preconditions from the same state
- **Specs:** RUNTIME §3.4 l.532-541 (the diagram draws both `[error] -- cleanup --> [unloaded]` and
  `[error] -- establish new realization --> [loaded]`), l.603, l.606-607; §9.3 l.3063-3066 (`realization`
  current/absent/unknown gives an axis either reading fits), l.3071 (`recover_module` requires `unloaded`
  or `error` "and cleanup of any previous realization is complete"), l.3115 (`start_module` on `error`
  establishes intent with no cleanup-complete precondition), l.3114; LOADER §7 l.362-370.
- **Issue:** one Runtime silently turns a crashed instance's `error` into `unloaded` once cleanup completes
  (a UI's failure indicator disappears), another keeps `error` as a resting state; a `start_module` on
  `error` is rejected up front by one Runtime and accepted with retained intent by another.
- **Impact:** observers and orchestrators cannot rely on `error` persisting.
- **Overlap:** EC-03/G20, D24, RT-05.
- **Suggested resolution:** state that `error` persists until an explicit start, recover or stop
  (cleanup completion changes only `realization` to `absent`), and give `start_module` on `error` the same
  cleanup-complete precondition as `recover_module`, or forbid it.

#### NL-07 — Lifecycle failures are free text: no typed failure class on module records, the Loader's typed code is dropped, and facade uncertainty has no `state` value
- **Specs:** RUNTIME §9.3 l.1737 (`reason = tstr .size (0..512)`), l.1740 (`failure_code` is used only by
  `route_failure.code` and `permission_settings_state.failure`), l.1747-1752 (`state` is exactly
  unloaded/loaded/ready/stopping/error), l.1853-1865, l.2097-2103, l.2213-2219 (module records and events
  carry `state` plus optional `reason` only), l.2936-2943 (seven mandatory distinctions for facades reported
  "through readiness state, route state, reason strings, and runtime-control events"), l.2956-2958 and
  l.3158-3159 (uncertainty "through state and reason" with no value for it), l.3272-3273, l.616 (the Loader's
  typed `error_code`, LOADER §10 l.595-604, becomes free text at the Runtime boundary), §3.4 l.549-550,
  §6.2 l.1089 (startup timeout), §10.1 l.3211-3215; CONFIG §8 l.269 (indeterminate apply -> `error`).
- **Issue:** an instance in `error` because its host crashed, the startup timeout fired, a permission was
  withdrawn, `apply_configuration` was indeterminate, the artifact was rejected or it called
  `report_failure` looks identical to an orchestrator and a UI; process exit status or signal appears
  nowhere; for a remote provider that becomes unreachable one Runtime reports `error` and another `loaded`,
  with the seven mandated classes worded differently in `reason`.
- **Impact:** no portable restart policy and no meaningful "why did this stop" display.
- **Overlap:** EC-10/G27 (value lists for the two existing `failure_code` uses), CA-01/G46, G20/G21. New:
  module-level records have no code field at all, so EC-10's fix cannot reach them; the Loader code and
  termination evidence are never surfaced; no `unknown`/`stale` state for facades.
- **Suggested resolution:** `? failure: {code, ? message, ? exit: {status / signal}}` on `module_record`,
  `get_readiness_response` and `module_state_changed_event` with a closed kebab-case list
  (startup-timeout, loader-<error_code>, reported-by-module, host-terminated, authority-withdrawn,
  config-indeterminate, artifact-rejected, cleanup-failed, remote-unreachable, remote-not-ready,
  remote-stopped, remote-failed, contract-mismatch), the Loader `error_code` carried unchanged, and a
  reflected `fresh/stale/unknown` field (or an `unknown` state) for facades.

#### NL-08 — No Core liveness source: a hung module stays `ready`
- **Specs:** LOADER §7 l.489-491 (exactly three failure triggers: host termination, lost direct binding,
  indeterminate live configuration); RUNTIME §10.1 l.3217-3218 (the module itself must notice; "An
  ordinary invocation failure MUST NOT by itself be treated as a report of realization failure"), §9.3
  l.2835-2837 (timeouts are implementation policy), §8.1 l.1441 (graceful release waits for in-flight
  calls), l.3245-3247 (supervision is a deployment detail), l.3209 (direct mode unsupervisable); no
  keepalive, heartbeat, watchdog or idle text in any file.
- **Issue:** a provider whose dispatch deadlocks (a blocking nested call on its own main thread, a
  dependency that vanished mid-call) stays `ready` forever while a consumer UI waiting on it stays busy,
  and a stuck dispatch thread makes graceful release impossible until forced cleanup. A deployment
  watchdog can feed "host termination", but Core defines no liveness source and no module-declared
  tolerance.
- **Impact:** hangs are invisible to restart policy.
- **Overlap:** HC-06, G61, D24. Minor.
- **Suggested resolution:** an optional periodic liveness probe (a trivial Runtime Control round trip or
  watchdog) with a module-declared tolerance, added to LOADER §7's failure triggers.

#### NL-09 — Long-running operations: no idempotency key for module methods, no durability statement for operation handles, no common resync shape (SO-09 addendum)
- **Specs:** RUNTIME §9.3 l.2785-2787, l.3102-3103 (`request_key` exists only for Runtime Control route
  and create operations), §10.1 l.3224, l.3234-3235; TRANSPORT §3.2 l.511-531 (retry only when the contract
  makes it safe; no replay "unless the module contract defines an explicit event-recovery mechanism"), §5.1
  l.688-707 (the two synchronization models, but no shape); RUNTIME §8 l.1315-1320 (state durability is
  policy).
- **Issue:** C holds an operation handle from P while a person decides at A, or a pending-submission id:
  whether the handle survives P's recovery, whether a retried request prompts or submits twice, and how C
  resyncs after a dropped session are reinvented per contract.
- **Impact:** duplicate prompts or submissions after a provider restart.
- **Overlap:** SO-09/G100 (records the absence of a standard pattern), HC-05/HC-06, TR-02/G31.
- **Suggested resolution:** a long-running-operation profile in INTERFACE: caller idempotency key,
  operation record with stated durability (state_dir-backed), a `list_operations`/`since` resync, a cancel
  binding (see NR-12), and the notification-plus-fetch rule of NE-01.

#### NL-10 — Retained `requested` intent after a Runtime restart: no MUST names who resumes it, and there is no restart primitive
- **Specs:** RUNTIME Terminology l.70 (orchestration "owns automatic recovery policy and scheduling"),
  §10.1 l.3212-3214 ("Disabling automatic restart is a valid policy"), l.3226-3228 (the only sentence
  requiring resumption concerns permission withdrawal), §10.2 l.3251 (shutdown preserves intent), §9.1
  l.1657 (an explicit stop cancels intent), §9.3 l.3115 (a new start records the requester as origin),
  l.3070-3075 (recovery rechecks the retained origin's authority), method list l.1912-2191 (no
  `restart_module`).
- **Issue:** an instance started by a UI module and preserved across a host quit is started again by one
  implementation and left `unloaded` by another, both conformant; a UI "restart" action must stop (intent
  cancelled) then start, making the module that pressed it the new origin whose authority later recovery
  checks.
- **Impact:** startup after a restart is implementation-dependent.
- **Overlap:** D24 (chose persist-and-resume as FREE), CA-01/G46, D22. Minor.
- **Suggested resolution:** state that orchestration MUST request recovery of every `requested` intent
  after Runtime start, honouring ordering constraints, unless the restart policy disables it; add a
  `restart_module` that preserves intent and origin.

#### NL-11 — `apply_configuration` has no bound, no outcome class for a timed-out attempt, and an explicit stop cannot pre-empt a wedged attempt by rule
- **Specs:** CONFIG §8 l.250-256 (ordering with other mutations), l.262-270 ("Failure to obtain a valid
  result" is indeterminate -> `error`, with no defined trigger); RUNTIME §6.2 l.1089 (the startup precedent),
  §9.1 l.1646-1648, §8.1 l.1441-1443, §9.3 l.2835; LOADER §8 l.531-535; INTERFACE l.1537-1538.
- **Issue:** a module applying a live change that closes and reopens its storage and restarts background
  work outlives whatever deadline the implementation chose: one Runtime waits forever, another declares
  the outcome indeterminate after a few seconds and puts the instance into `error`; both conform.
- **Impact:** live reconfiguration is unpredictable across implementations; G61's timeout list has no
  apply bound.
- **Overlap:** HC-06, EC-04/G21, G61.
- **Suggested resolution:** a mandatory bounded deadline like the startup timeout; a timed-out attempt is
  `configuration-rejected` (behaviour stays under the previous value) unless the module reported partial
  application; let an explicit stop pre-empt an in-flight attempt.

### 2.4 Authority

#### NA-01 — The `approval-required` denial cannot reach the denied consumer interoperably
- **Specs:** CA §5 l.454-466 (`denial = {code, ? message}` returned to the Runtime), §7 l.662-666;
  INTERFACE §5.1 l.2503-2506 (structured `detail` only for INVALID_PARAMS), l.2491-2492 (`message` has no
  machine-readable semantics), l.2520-2521; RUNTIME §9 l.1566-1570 (denial reported only through the error
  channel), §9.3 l.2762 (`establish_route` never returns a failed `route_record`), l.2774-2777 (callers
  without observation authority must not distinguish unknown from hidden or denied targets), l.2810-2814;
  CA l.1114, l.733-738 (retry trigger via `grant_changed` or own-grant inspection, both policy-gated);
  SECURITY §14 l.516.
- **Issue:** C's `establish_route` to P's method m is denied while a person decides at A; C receives bare
  NOT_AUTHORISED and cannot tell "waiting for the person" from "never allowed", so it cannot show the right
  state or decide whether to retry. The spec deliberately hides reasons from unprivileged callers, so a
  fix must respect l.2774-2777.
- **Impact:** every approval flow invents its own out-of-band "pending" signal.
- **Overlap:** HC-13 (assumes deny -> grant -> retry works and asks for a pending state), EC-10/G27
  (observer vocabulary). New: the denial reason is structurally unable to reach the denied consumer.
- **Suggested resolution:** a bounded, non-disclosing detail under NOT_AUTHORISED
  (`{reason: "approval-required" / "denied"}`) delivered only when the target exists and is visible to the
  caller, or a consumer-scoped pending-approval event; either way, without weakening l.2774-2777 for hidden
  targets.

#### NA-02 — The approver's data path: no event for an `approval-required` denial, no presentable content in any CA record, and roots the approver may not be allowed to resolve
- **Specs:** CA §8 l.1103-1106 (the CA publishes only `grant_changed` and `policy_changed`), §9 l.793-800
  (the deny record carries consumer, decision_id, scopes, denial: pull-only, within the 1000 most recent
  records l.904, l.1088), §3 l.141-155, l.189-193 (scopes are roots and typed constraints), §3.1 l.241-244,
  l.397-401 (roots are deliberate), l.631-632; RUNTIME §9.3 l.1887-1891 (`route_access` methods are
  `bstr .size 32`), §2.4 l.416-421, l.427, l.433 (`describe_provider`/`logos.schema` need `discover`
  authority), l.2105-2108; PM §4 l.294-298 (`requested_permission.reason`, reachable only through
  `list_installed_packages` l.1366, not carried into `permission_scope` or any decision or grant);
  INTERFACE §5.1 l.2401-2406 (a `schema_commitment` carries no namespace text); SECURITY §13 l.501-502
  ("accurate presentation of the requested scope"), §14 l.516.
- **Issue:** A, which must ask "may C call m on P?", gets no notification of the pending denial, must poll
  `query_audit` with its own authorization, must hold `discover` visibility on every provider to turn roots
  into method names, and finds no record binding a rendering to the decision or grant.
- **Impact:** an approval UI cannot be built from Core data without broad, polled authority.
- **Overlap:** HC-13, SO-06, SO-05. New: the approver's data path and the missing presentation record.
- **Suggested resolution:** a `pending_approval` record published as an event to modules granted an
  approver role (consumer, target, requested scopes, method and event names resolved by Runtime under the
  exact contract, the manifest `reason`), marked non-authoritative; an approver role with implied
  `discover` visibility; a resulting grant referencing the record.

#### NA-03 — Local routes: `expires_at` is optional although the decision has a mandatory validity end
- **Specs:** RUNTIME §9.3 l.2614-2615 (`expires_at` required only "For a ready remote route"), l.1907-1908
  (optional in `route_record`), l.2781-2782 (a route decision MUST have a validity end; `expires_at` bounded
  only when present), l.2659-2660, l.1235-1237; CA §3.1 l.262-263, §5 l.512-514. (Who renews is settled:
  l.2745, l.2790-2791; Runtime-initiated re-acquisition is policy and observable: l.2839-2847.)
- **Issue:** C holding a local route to P for an operation of several hours under short-lived decisions may
  never be told the deadline it must renew by.
- **Impact:** long operations fail at an unannounced expiry.
- **Overlap:** TR-06/G35, CA-01, CA-06, EC-03/G20.
- **Suggested resolution:** require `expires_at` on every ready route whose decision has a validity end.

#### NA-04 — `request_key` for route operations: whether a denied result is retained is unstated
- **Specs:** RUNTIME §9.3 l.2785-2788 (the entire rule: "while the result remains retained MUST return the
  same result") vs l.3103 (`create_module` retains only successful associations); INTERFACE §4.6
  l.2321-2328 and RUNTIME l.1240-1241 (a route-establishment failure is an invocation failure, so whether it
  is a "result" is open); CA §8 l.748-752 (re-evaluation applies to protected operations, not to a retained
  idempotent response).
- **Issue:** a consumer that follows HC-13's deny -> grant -> retry with the same request may be answered
  with the retained denial indefinitely on one Runtime and succeed on another.
- **Impact:** the approval it waited for does not take effect.
- **Overlap:** EC-01/G18, HC-13, HC-12.
- **Suggested resolution:** retain only successful route results under `request_key`, or discard a
  retained failure on any `policy_changed`/`grant_changed` affecting the consumer.

#### NA-05 — Grants carry no issuer and no link to the decision they answer
- **Specs:** CA §6 l.529-539 (grant CDDL), l.541-547 (`issue_grant_request`), l.573-580 (`list_grants` and
  `revoke_grant` have no issuer filter), §5 l.483; §9 l.830-838 (the issue-grant audit record does carry
  `? consumer`), l.887-897, l.940-941 (retention is policy and bounded); SECURITY §13 l.501-502.
- **Issue:** when several modules on one host (an approval UI, a CLI) and deployment configuration can all
  issue grants, "revoke everything module X approved" and "which approval does this grant answer" are
  answerable only through the audit window while it lasts.
- **Impact:** grant administration depends on audit retention.
- **Overlap:** SO-06 (operator principal and administrative path). Minor.
- **Suggested resolution:** `issuer` (a module-instance address or a `protected-policy` marker) and
  `? decision_id` on the grant record and the issue-grant audit record; an issuer filter on `list_grants`.

#### NA-06 — A provider named as a permission's enforcement component is handed nothing to enforce with
- **Specs:** CA §3.5 l.363-364 ("The permission definition MUST identify the enforcement component"), §12
  l.1164 ("another enforcement point named by the permission definition": a provider is not excluded), §2
  l.79-83 and §10 l.1108-1111 (`evaluate` is Runtime-facing; Runtime supplies the consumer), §6 l.520
  (not every allow decision creates a grant), §10 l.1114 (inspecting other targets' grants is not implied);
  INTERFACE §2.6 l.1338-1345 (dispatch: context, method, params); RUNTIME §9.3 l.2105-2140, l.2249-2253
  (permission settings are OS-policy inputs, not per-call decisions).
- **Issue:** even after HC-03 is fixed (P learns its caller), a provider with per-caller roles, an
  allow-list of callers for some methods, or per-caller resources needs "does this caller hold permission
  Q with constraints K", and no core path delivers the allowed scope or lets P ask.
- **Impact:** each such provider keeps its own roles file outside the authority model.
- **Overlap:** HC-03 (caller identity and value-level constraints), PM-03/G39. New: no authorized path for a
  provider to consult the CA or receive the applicable scope.
- **Suggested resolution:** allow a permission definition to name a module provider as enforcement
  component and give that provider a scoped `check`-style method (or `list_grants` with `target` = the
  inbound consumer) for permissions it enforces; alternatively deliver the applicable allowed scope with
  each dispatch.

#### NA-07 — After `policy_changed`, live subscriptions keep delivering until the consumer's next protected operation
- **Specs:** CA §3.1 l.264-265 (event deliveries outside the allowed scope MUST be rejected), §8 l.737,
  l.748-753 (re-evaluate "before performing another protected operation"; a route becomes unusable "when
  the new decision denies" it), l.755-756 (grant revocation terminates the subscription); RUNTIME l.956-958,
  l.2832 (subscriptions end on terminal route state, expiry or revocation; policy change is not listed).
- **Issue:** C subscribed to P's progress events keeps receiving them after a policy change that would deny
  the route, until C happens to make a call; eager and lazy readings both have textual support.
- **Impact:** a policy narrowing takes effect at an unpredictable time.
- **Overlap:** CA-01/G46, TR-06/G35. Minor.
- **Suggested resolution:** on `policy_changed` Runtime MUST re-evaluate every live route whose cached
  decision was invalidated within a bounded time and terminate what the new decisions deny, or list event
  delivery explicitly as a protected operation.

#### NA-08 — `decision_id` uniqueness across Authority restarts is unspecified; "Authority binding" is undefined
- **Specs:** CA §3 l.122 (`decision_id = tstr .size (1..128)`), §5 l.494-495 ("an opaque correlation
  value"), §9 l.891 (`query_audit` filters by it), l.948 (call records cite it), §8 l.686, l.698 ("scoped to
  the selected Authority binding", a term used twice and never defined; policy revisions themselves are
  settled by l.686, l.700, l.703, l.715-723).
- **Issue:** a CA that restarts daily and reissues ids makes weeks of audit records and signed evidence
  containers ambiguous.
- **Impact:** audit correlation by decision is unreliable.
- **Overlap:** CA-05/G51, CA-06/G52, G80. Minor.
- **Suggested resolution:** require `decision_id` to be unique per Authority binding across restarts
  (binding epoch or 128-bit random ids) and define "Authority binding".

#### NA-09 — No delegated or attenuated authority: acting for another module or for a person's per-request choice is unrepresentable
- **Specs:** RUNTIME Terminology l.135-137 and BCP §2 l.77-79 (a human, user-session, device or agent
  identity and its delegation "must be defined explicitly" by a later specification: a deliberate deferral);
  CA §2 l.89-91, RUNTIME §7.5 l.1225-1228, SECURITY §7 l.292-300 (no implicit transfer); CA §5 l.467-471
  (`evaluate_request`: consumer, scopes, commitment), §6 l.529-539, l.590 (issuance is policy-gated, with
  no rule that issued scopes lie within the issuer's own authority); RUNTIME l.2816-2821 (delegation exists
  only Runtime-to-Runtime).
- **Issue:** requester R asks host H to perform a capability; the person picks provider W in a chooser in
  H; W must act for R's request. Under the specs W acts solely under its own authority, H's call carries no
  "for R" relation, and the person's choice has no authority representation; a broker module in the data
  path is attributed as consumer in every call record.
- **Impact:** brokered capability dispatch loses the requester in authority and audit.
- **Overlap:** HC-03, HC-13, SO-06, RT-01.
- **Suggested resolution:** a minimal delegation record (an optional `on_behalf_of` consumer in evaluate
  requests, grants and call records with a containment rule: delegated scope within the delegator's and
  the delegate's own scopes), and either a user-session principal or an explicit statement that user choice
  is outside authority.

#### NA-10 — Audit records have no redacted form
- **Specs:** CA §9.1 l.1083 ("filter or redact information the authenticated consumer is not allowed to
  observe": "redact" occurs only here), §9 l.786-803 (evaluate records require `scopes`), l.911-912 (no
  fields outside the variant), §3 l.189-193 and §1 l.107-109 (non-empty `constraints` and arrays), §9.1
  l.1085-1086.
- **Issue:** a filesystem or network scope whose constraints hold a user's data path or private network
  endpoints can only be hidden by omitting the whole record from a query response.
- **Impact:** audit consumers see all of a record or none of it.
- **Overlap:** CA-04..CA-07, G143 (retention bounds). Minor.
- **Suggested resolution:** a redacted scope form (`constraints` replaced by its subtree root plus
  `redacted: true`) admitted in audit records and list responses.

#### NA-11 — Bootstrap policy after the CA is bound: no precedence, lapse or change notification; the CA's own recovery rests on inference
- **Specs:** RUNTIME §9 l.1494-1497 (bootstrap grants "only the operations needed to validate and reach"
  system services), l.1501-1502 ("establish the selected initial Capability Authority"), l.1513,
  l.1515-1519 (bootstrap grants beyond binding admitted; "narrower recovery path" occurs once and is
  undefined), l.1566-1568, l.1574 (an explicit CA deny is binding); §10.1 l.3230-3242; CA §1 l.59-63, §8
  l.715-723.
- **Issue:** no sentence says which source is consulted first, that bootstrap allows lapse once a CA is
  bound, or what the recovery path may contain; a host whose CA module crashes depends on l.1501's
  "initial" being read as "or re-establish".
- **Impact:** CA recovery without a Runtime restart is not portable.
- **Overlap:** RT-02/G48, SO-04/G140, D15, C-12, EC-07/G24, RT-05/G56. Minor.
- **Suggested resolution:** state that once a CA is bound, bootstrap policy authorizes only reaching and
  recovering system services (orchestration's `recover_module` and rebinding for the bound CA), that CA
  decisions take precedence, and give bootstrap allows a synthetic decision identity for audit.

### 2.5 Remote transport and multi-device use

#### NR-01 — Provider endpoints are inbound-only: no provider-initiated or relayed carrier
- **Specs:** TRANSPORT §3.1 l.422 ("Caller opens the carrier connection at the endpoint selected by the
  transport profile"), §8.2 l.973, §8.4 l.1007-1010, §8.4.1 l.1052, §9.3 l.1151-1160 and §10 l.1168 (other
  carriers need "a separate specification" or "a separately named transport profile"); RUNTIME §9.3
  l.1790-1793 (closed `runtime_address` kinds: unix_stream / tls_tcp / quic), l.2378-2389 (locators),
  l.2416-2418 (several addresses because "reachability can differ"), l.2459-2463 (remote access requires an
  active listener on the provider's Runtime), l.2484, §9 l.1630, l.169 (no remote facade as a system
  service); SECURITY §11.5 l.438-440, §11.6 l.455. No relay, NAT, rendezvous or provider-initiated text in
  any file.
- **Issue:** P on a device that cannot accept inbound connections (behind carrier NAT, on a cellular
  network, or suspended by a mobile OS) cannot serve consumers on another device: they must dial a
  tls-tcp/quic listener on P's Runtime.
- **Impact:** a provider on a phone cannot serve a desktop consumer.
- **Overlap:** none (RT-01/D13 is a CLI on loopback; G125 decides to claim remote transport on mobile).
- **Suggested resolution:** a provider-initiated carrier in TRANSPORT §8.4 (P's Runtime dials C's Runtime
  with the same mutual authentication; caller and callee roles follow the route, not the TCP direction)
  and/or a relayed `runtime_address` kind, with the ticket, channel-binding, listener and export rules
  adapted.

#### NR-02 — No pairing or enrollment exchange between two Runtimes; the "authorized provisioning operation" is never defined
- **Specs:** RUNTIME §9.3 l.2317-2335 (enrollment "is a provisioning and Runtime input record, not a new
  Runtime Control method"; changes only "through protected deployment input or an authorized provisioning
  operation", a phrase at l.2319, l.2335, l.2341 and TRANSPORT l.1029 with no definition), l.2344-2349 (key
  rotation), l.2358-2359 ("Protected local provisioning ... is sufficient"); §9 l.1564; CA §3 l.182-187 and
  §3.4 l.331-340 (`remote_enrollment_scope` with actions enroll/refresh/remove, but no method); INTERFACE
  §5.2 l.2802-2810 (`connect_remote` needs the peer's id and address up front); SECURITY §6.1 l.254-255,
  l.56, l.80, l.82; BCP §5.4 l.324.
- **Issue:** pairing two independently owned devices needs each side's UUID, profile, trust anchor and
  exact SPKI in both directions before the first handshake, and again after rotation or revocation; the
  only sanctioned paths are deployment files and an undefined operation. The deferral to deployment is
  deliberate, but two personal devices have no deployment operator.
- **Impact:** no portable way to connect two devices' Runtimes.
- **Overlap:** SO-03 (formats of protected inputs), SO-06 (operator principal). New: the two-party exchange,
  bootstrap when neither side holds an enrollment, an out-of-band bundle, the dangling provisioning
  operation.
- **Suggested resolution:** a pairing profile: a deterministic-CBOR enrollment bundle (runtime id, profile,
  SPKI(s), trust anchor, addresses, revision) fit for QR, NFC or a link; an authority-gated Runtime Control
  provisioning method that imports it; a short-lived pairing code for the first mutual exchange.

#### NR-03 — Remote-module facades: no operation or deployment record creates one, sets its target or refreshes its address
- **Specs:** RUNTIME Terminology l.99, l.118-119 (a facade "is not another local module instance"), §9
  l.1605-1607, §9.3 l.2009-2012 (`create_module` creates a local record), l.3095, l.3121-3124 (`start_module`
  on a facade "may only start or refresh"), l.2417-2418 ("MAY publish multiple runtime addresses", with no
  publication mechanism), l.2523-2538, l.2766-2771 (continuations presuppose an existing facade),
  l.2905-2924 (the local Runtime "may query" the remote Runtime and map results into facade state,
  preserving the endpoint used for refresh), l.3013 (deployment inputs name listener and export records
  only); INTERFACE §5.2 l.2802-2817 (`connect_remote` reaches a remote provider without a facade, from a
  module-supplied address each time); BCP §5.1 l.257.
- **Issue:** for a `single` route to select P on another device, a facade with `remote.runtime.address` and
  `remote.provider` must exist in C's Runtime; nothing creates or removes it, and when P's device changes
  address nothing updates it.
- **Impact:** contract-selected routing to remote providers depends on implementation-local setup.
- **Overlap:** none (RT-04 is local package selection; HC-12 instance aliases).
- **Suggested resolution:** `set_remote_facade`/`remove_remote_facade` Runtime Control methods taking a
  `remote_provider_target`, or a named deployment-input record; a rule that a facade follows the peer's
  latest authenticated address; or state that a forwarded `establish_route` continuation creates the
  facade.

#### NR-04 — Route continuations: a module-facing `establish_route_response` may contain them, and a module cannot consume one
- **Specs:** RUNTIME §9.3 l.1920-1929 (`route_continuation`; one shared `establish_route_response` for
  module-facing and Runtime-facing calls), l.2760 (a `single` response is "exactly one route or one
  continuation"), l.3019 (`establish_route` "returns routes or continuations"), vs l.2722-2724 and
  l.2770-2771 ("The consumer's Runtime follows it with a new single request"); INTERFACE §5.2 l.2700-2707,
  l.2829 (`materialize_route` accepts only a ready route).
- **Issue:** the actor is the consumer's Runtime, but no sentence says a module-facing response MUST have
  empty `continuations`; a module written for a Runtime that resolves them internally gets no route on a
  Runtime that returns them.
- **Impact:** remote route establishment is not portable for modules.
- **Overlap:** C-09/G81 (Runtime-known consumers in forwarding). New: the module-visible response shape.
- **Suggested resolution:** state that continuations are resolved inside `establish_route` and never
  returned to modules (and drop the field from the module-facing shape), or define the follow-up a module
  must issue.

#### NR-05 — Route state after loss of a provider session; "remote runtime disconnect" is undefined
- **Specs:** TRANSPORT §3.2 l.520-531 (renewal or new establishment after connection loss), §8.2 l.973,
  §8.4.2 l.1113-1114, §8.1.1 l.918; RUNTIME §9.3 l.2635 (renewal returns a fresh ticket), l.2790-2795,
  l.2832 (routes fail on "remote runtime disconnect", undefined), l.2871-2872 (connection loss is session
  termination distinct from revocation), l.2835-2837 (whether policy also fails the route is policy).
- **Issue:** when P's device changes network and the provider session dies, whether C's route stays
  renewable (new ticket, same decision) or is failed (new `establish_route`, fresh CA evaluation, possibly
  another approval round, HC-13) depends on reading one undefined phrase.
- **Impact:** a network change may or may not cost a new approval.
- **Overlap:** TR-06/G35, EC-05/G22, G20, G31, HC-13. Minor.
- **Suggested resolution:** define "remote runtime disconnect" (loss of the Runtime-to-Runtime path or
  enrollment) and state that loss of a provider session alone leaves the route ready and renewable.

#### NR-06 — Whether a successful `renew_route` rebinds a live session is implied but never stated
- **Specs:** TRANSPORT §8.1 l.831-838 (a session is bound to "the authority decision" and "expiry and
  revocation state"), l.869-871, §8.1.1 l.914-919 (the fresh ticket lives 60 s and is never reissued), §3.2
  l.524-527; RUNTIME §9.3 l.2635 (a fresh ticket is mandatory on every renewal, even for a live session),
  l.2660, l.2790-2791, l.3023-3026; CA §3.1 l.262-263, §8 l.717, l.756.
- **Issue:** the texts compose to "the live session continues under the renewed decision", but no sentence
  says the session's bound decision and expiry are updated, and the mandatory fresh ticket dies unused.
- **Impact:** implementations may end live sessions at the old expiry.
- **Overlap:** TR-06/G35, CA-06/G52. Minor.
- **Suggested resolution:** state that renewal rebinds existing provider sessions to the new decision and
  expiry, the returned descriptor serving only replacement sessions.

#### NR-07 — No liveness, keepalive or idle-session rule; "fresh" has no evidence definition
- **Specs:** TRANSPORT §1.1 l.91 (message kinds closed at 0..8), §10 l.1163-1169, §3.2 l.509-513, §8.4.1
  l.1032-1060, §8.4.2 l.1108-1115; RUNTIME §9.3 l.2835-2837 (idle expiry is policy), l.2929-2934 (advisory
  "unless it is fresh"), l.2956-2958 (fail-safe: uncertainty must not be reported as ready), §4.2 l.870-871.
- **Issue:** a peer device that sleeps leaves a half-open TCP connection; nothing defines the evidence
  behind "fresh"/"unreachable" or requires keepalive on tls-tcp, so the facade stays ready and a call blocks
  until the OS timeout (and the ABI has no timeout, HC-06).
- **Impact:** remote calls hang for minutes on a sleeping peer.
- **Overlap:** G61 (values), HC-06, TR-06/G35. Minor.
- **Suggested resolution:** a keepalive requirement (TCP keepalive or QUIC PING with a bounded interval)
  per remote profile; define "fresh" in terms of the last liveness evidence.

#### NR-08 — Request-side flow control and overload: no in-flight bound, no rejection code, no subscription limit code; control messages queue behind large frames
- **Specs:** TRANSPORT §2.2 l.381-385 and §7 l.784-809 (unbounded multiplexed requests), §5.2 l.711-724
  (backpressure defined for Events only), §5.1 l.640-652 (duplicate subscriptions allowed, no count limit),
  §2.1 l.369-377 and §3.2 l.509-512 (the only defined overload reaction is connection close), §8.4.2
  l.1099-1101 (one QUIC stream: Cancel and Events wait behind a 16 MiB response); INTERFACE §5.1
  l.2476-2483 (codes 0..9 closed; "MUST NOT emit any other value"), l.2389-2391 (INVALID_PARAMS reasons:
  malformed-cbor, non-deterministic-cbor, schema-mismatch), §2.6 l.1470 (NOT_READY reserved), l.2594
  (TIMEOUT has no producer anywhere); CA §9 l.942 (admission failures exempt from audit), l.646
  (`authority-unavailable` unexplained), §3.5 l.368-370, l.1165 (limits are profile policy); SECURITY §10
  l.367; BCP l.329-330.
- **Issue:** a consumer flooding P with calls, or a compromised module flooding an approval provider or the
  CA: P may refuse per request (no code fits), stop reading (head-of-line blocks Cancel too) or close
  (fails every in-flight call and subscription).
- **Impact:** callers cannot implement portable retry-with-backoff and conformance tests cannot assert the
  outcome.
- **Overlap:** IF-02/G59 (nesting depth, same "a limit without a reason value" shape), G75 (bound values),
  G61, SO-09, HC-06, the EC table. New: per-connection in-flight and subscription bounds as profile
  parameters, a correlated per-request rejection signal, explicit read-side backpressure, Cancel/Event
  latency behind large frames.
- **Suggested resolution:** profile parameters for maximum in-flight requests, queued-response bytes and
  subscriptions per connection; a shared retryable code (`LOGOS_ERR_RESOURCE_EXHAUSTED`, or a detail under
  an existing code) that is correlated and MUST NOT close the connection; a second QUIC stream for Cancel
  and Events or a documented latency limit.

#### NR-09 — Cross-host wall-clock dependence: whose clock governs a remote route's `expires_at`, and whether certificate validity times are checked
- **Specs:** RUNTIME §9.3 l.2659-2660 (the consumer's Runtime enforces expiry on its own clock),
  l.2684-2691 and l.2722-2733 (the provider's Runtime sets it), l.2781-2782, l.2790-2796 (no renewal lead
  time), l.2346-2347 ("certificate and trust-anchor validation" presupposed, undefined); TRANSPORT §8.1.1
  l.914-917 (tickets use the issuer's monotonic clock: the spec solved skew for tickets), §8.4.1 l.1049-1052
  (chain validation to the anchor; RFC 5280 is cited only for the SPKI structure); CA §6 l.597-601 ("no
  distributed clock-synchronization or clock-skew protocol"; exact expiry), §9.1 l.1043; PM l.548.
- **Issue:** a device whose clock is minutes off, or an offline device with no trusted time, either drops a
  route the peer still honours or keeps calling an expired one; whether notBefore/notAfter is evaluated
  under SPKI pinning is never said.
- **Impact:** remote routes fail spuriously across devices with skewed clocks.
- **Overlap:** TR-06/G35, G61, G86. Minor.
- **Suggested resolution:** declare `expires_at` authoritative on the provider-side Runtime's clock and
  advisory for consumers, with a renewal lead time at least equal to a defined skew tolerance (or an
  `expires_in_ms` relative to the response); state the certificate time-validity rule and any trusted-clock
  prerequisite.

#### NR-10 — The tls-tcp/quic certificate profile: self-signed leaf as its own anchor, host-name verification, `server_name`, key usage
- **Specs:** TRANSPORT §8.4.1 l.1026-1028, l.1046-1058 (chain to the enrollment's anchor; leaf SPKI
  equality; "TLS certificate validation authenticates the enrolled Runtime"), §8.4.2 l.1091-1093; RUNTIME
  §9.3 l.1744, l.1773-1786, l.1804-1806 (`trust_anchor_id` opaque), l.2321-2322, l.2328-2331, l.2373-2376
  (the address is a locator, not identity), l.2385-2389, App B l.3611-3616 (`server_name` equal to host, no
  prose).
- **Issue:** two devices with self-signed certificates: may the enrollment's anchor be the peer's own leaf
  (chain length one)? A TLS stack with default host-name verification left on rejects peers another
  accepts; `server_name` has no stated role (SNI only?); key usage is never mentioned. Host names are not
  identity by construction, but no sentence forbids checking them.
- **Impact:** two conforming implementations reject each other's peers.
- **Overlap:** SO-03 (G137, G86, G87). New: the validation semantics of the mandatory profile itself.
- **Suggested resolution:** state in §8.4.1 that identity is SPKI-pinned, that host-name/SAN matching is
  not performed, that a self-signed leaf MAY be its own trust anchor, that `server_name` is SNI only, and
  any key-usage expectations.

#### NR-11 — Route-handle multiplicity is unspecified, so outstanding calls per route are capped at one
- **Specs:** INTERFACE §2.8 l.1571-1572 ("A caller MUST externally serialize operations on one route
  handle"), §5.2 l.2564 (one route per handle; silent on handles per route), l.2829-2845, l.2730-2737
  (synchronous `call`, no completion operation), l.1547 (the Runtime Control binding is thread-safe; route
  handles are not); RUNTIME §4.1 l.724, l.736-737 (a handle "wraps a local transport connection"), §9.3
  l.2747, l.1099-1101, l.2491; TRANSPORT §8.1 l.824-826 (one ticket, one session), §8.2 l.973, §7 l.784
  (multiplexing exists on the wire).
- **Issue:** C issuing many concurrent calls to P either serializes per route, pays an `establish_route`
  (CA decision, ticket, audit record) per in-flight call, or relies on a binding that materializes several
  handles sharing the single ticketed session, which no text allows or forbids. HC-05's "a thread per
  outstanding call" is achievable only in the last case.
- **Impact:** consumers that fan out reads or proxy calls cannot get concurrency portably.
- **Overlap:** HC-05, HC-06, G22, G77. New: the per-route concurrency cap derived from three rules.
- **Suggested resolution:** state whether `materialize_route` may yield several handles for one ready
  route sharing its session, or add an asynchronous call/completion operation to the route vtable.

#### NR-12 — A Transport Cancel never reaches the native provider
- **Specs:** TRANSPORT §6 l.760-778 (Cancel; "SHOULD attempt to stop"; linearization against a committed
  Response; later-Event semantics are the contract's); INTERFACE §2.6 l.1201-1224, l.1338-1345 (no cancel
  symbol, no per-dispatch token), l.1436 ("Dispatch itself is synchronous"), §2.8 l.1583-1586 (every
  in-flight call must return before `_destroy`); LOADER §3 l.190-195; CA §8 l.759-760 ("If cancellation is
  impossible ..."); RUNTIME §10.2 l.3266-3267.
- **Issue:** C's Cancel on a long call to P (a slow stop, a long chunk of background work, a deliberately
  slow key derivation) ends at the Module Host: P's worker stays busy, the late result is discarded, and an
  uncancellable call blocks graceful release until forced termination (unavailable in direct mode). Not a
  contradiction (the specs legislate the impossible case) but nothing says the ABI intentionally has no
  cancellation path, so P learns that C gave up only through its own contract method.
- **Impact:** every cancellable operation needs a contract-level cancel method that races the wire Cancel.
- **Overlap:** HC-06 (consumer side), G61, G23. New: the provider side.
- **Suggested resolution:** an optional `logos_<module>_cancel(context, call_token)` with a per-dispatch
  token, or a normative statement that Cancel is honoured only at the Module Host boundary and that
  cancellable contracts expose their own cancel method and event semantics.

#### NR-13 — A local unix-stream Runtime Control endpoint is typed and illustrated but has no consumer-binding rule
- **Specs:** RUNTIME §9.3 l.1767-1771 (`unix_stream_runtime_address`), l.2373 ("A Runtime-controlled
  endpoint can expose Runtime Control, ordinary provider traffic, or both"), App B.1 l.3544-3557
  (`/run/logos/runtime-control.sock` with profile `logos.local.unix-stream`); every Runtime-Control-over-
  Transport rule is remote-only (TRANSPORT §3.1 l.456-458, §8.1 l.883; RUNTIME l.1624-1633);
  `remote_listener_address` (l.1825-1827) and `remote_identity_profile` (l.1800-1802) exclude unix-stream;
  `connect_remote` accepts tls-tcp/quic only (INTERFACE l.2805); the ticketed §8.2 profile presupposes a
  Runtime-established route and Runtime Control has no provider record to route to; LOADER §5.4 l.330.
- **Issue:** a dangling type and example: nothing says what the Hello `token` carries on such an endpoint
  or how the consumer is bound; a hosted module's own binding is the implementation-defined Loader channel
  (G108), and any other process (a UI host, a shell) is outside the model (RT-01).
- **Impact:** implementations will expose incompatible local control sockets.
- **Overlap:** RT-01/D13/G83 (only remote Runtime Control is specified for another process), G108. New: the
  internal inconsistency and the fix site.
- **Suggested resolution:** define a local Runtime Control profile in TRANSPORT §3.1/§8.2 (a Loader-conveyed
  consumer-bound ticket after peer-credential verification), or delete the variant and App B.1; fold into
  RT-01's "local activation profile".

#### NR-14 — Unix-stream profile: the "Runtime operating-system identity" is undefined and uid-granular, so a same-user module can impersonate the provider
- **Specs:** TRANSPORT §8.2 l.951-953 (the per-instance directory "accessible only to Runtime and
  explicitly launched or authorized consumers", mode 0700), l.955 ("Under the expected Runtime
  operating-system identity", used at l.955, l.962, l.963, never defined), l.962-967 (the caller verifies
  the peer with `SO_PEERCRED`, `getpeereid()` "or an equivalent": uid/gid granularity accepted),
  l.975-978 (ticket possession by another process is credential compromise), §8.1 l.881-882 (OS credentials
  "may strengthen" ticket validation); RUNTIME §9.3 l.1867-1873 (the invocation descriptor carries path and
  ticket only), §1.3 l.303-304; SECURITY §4 l.197-200, §11.1 l.383, l.388-389, §11.6 l.448 (process
  placement is not containment).
- **Issue:** under desktop `process` placement every Module Host and application module runs as one uid; a
  malicious module M unlinks the Runtime-created socket path of P (the 0700 directory is owned by the same
  uid) and rebinds; C's uid-level peer check passes, C sends the ticket and then a call carrying a password
  in cleartext to M. The l.952-953 MUST cannot be met by 0700 alone when every consumer shares the uid.
  SECURITY says bare process placement gives no containment but never that one user's modules get no
  confidentiality from each other.
- **Impact:** any module of the same user can intercept another module's provider traffic.
- **Overlap:** C-06/G58 (socket layout; records "peer check by euid" without noticing it is vacuous between
  modules), TR-09/G107 (Windows check is stronger), G129. New: identity granularity, unlink-and-rebind
  impersonation, the unrealizable access statement.
- **Suggested resolution:** define the expected identity (at least uid plus pid, or a per-route socketpair
  or nonce instead of a path), require the Runtime side to verify inbound peer credentials where the OS
  provides them, and state in SECURITY §11.1-11.3 that `process` placement without a sandbox gives no
  confidentiality between modules of one user.

### 2.6 Data model and schema language

#### ND-01 — No integer wider than 64 bits and no numeric-string convention
- **Specs:** INTERFACE §1.7 l.400-427 (allowed: `uint64`/`int64` at most; floats, CBOR tags (so RFC 8949
  bignums) and `.regexp` reserved), §2.2 l.685-699, §2 l.1654, §5.1 l.2365-2426 (no numeric text type in
  the common surface); HASH l.555-556; COMMITMENT §7 l.936-943 (differently spelled numeric strings commit
  to different roots); BCP §5.3 l.306 ("Future numeric ... No profile assigned").
- **Issue:** values held as 256-bit unsigned integers (common in blockchain contracts) and decimal-scaled
  amounts cannot be typed; each contract will pick `tstr` with its own grammar, and generic clients (a CLI,
  an approval UI rendering a request from any provider) cannot interpret or compare them.
- **Impact:** every contract that carries such values defines its own string format.
- **Overlap:** none (IF-01/G38 is floats inside opaque payloads; G89/D26 is CLI rendering above 2^53).
- **Suggested resolution:** `logos.decimal_uint = tstr` with a normative grammar (ASCII digits, no leading
  zero except "0", no sign) and a stated scale convention, or `logos.uint256 = bstr .size 32`, in §5.1;
  publish the numeric profile before contracts that need it are frozen.

#### ND-02 — No common timestamp or duration type
- **Specs:** INTERFACE §5.1 l.2365-2426 (none); RUNTIME §9.3 l.1908 (`? expires_at: uint64`, unnamed) and
  l.2659 (unit in prose); CA §5 l.448 (`logos.capability_authority.timestamp = uint64`), l.493, §6
  l.600-601 ("Capability Authority and Runtime use the local Unix-time domain defined for timestamp",
  which RUNTIME never references).
- **Issue:** the millisecond-epoch semantics are stated twice and reach no module contract; history
  records, request deadlines, progress estimates and lock times each choose their own representation.
- **Impact:** generic clients cannot render or compare times across contracts.
- **Overlap:** HC-06, CA-05, G61, C-12. Minor.
- **Suggested resolution:** `logos.timestamp_ms = uint64` and `logos.duration_ms = uint64` in §5.1,
  referenced from RUNTIME and CA, with a SHOULD for module contracts.

#### ND-03 — A schema-valid value can exceed the frame ceiling: no sender-side rule, no per-call code, and the failure is session-wide
- **Specs:** TRANSPORT §2.1 l.369-377 (the receiver closes the connection; "MUST support a configured
  maximum of at least 16 MiB"; interfaces "MUST NOT require" larger messages), §3.1 l.133-138 (Hello
  carries no size), §3.2 l.509-513, §10 l.1165; INTERFACE §1.7 l.404-414 (unbounded `tstr`, `bstr`, `[* T]`),
  §4.6 l.2319-2347 (adapter duties assign no status to an oversize response), §5.1 l.2453-2455 and CONFIG
  l.103 (the spec bounds its own surfaces); RUNTIME §4.1 l.800-802, §7.3 l.1173-1179 (validation checks
  name, payload and commitment, not size), §12 l.3291-3310, §9.3 l.2986-2988.
- **Issue:** P's response that encodes above the ceiling (a passthrough of a large external result, a
  history export, a large catalogue) is sent, and the receiver kills the session: every other call
  multiplexed on C's connection fails with an uncorrelated TRANSPORT_ERROR; in direct mode the same value is
  delivered. An oversized Event has the same blast radius.
- **Impact:** one large reply takes down unrelated calls, and only in transported mode.
- **Overlap:** SO-09 (streaming profile), IF-02/G59 (depth), G75, G100. New: the sender-side behaviour,
  the mode asymmetry, the uncorrelated session-wide failure.
- **Suggested resolution:** a sender rule (size check before send; fail the call locally with a named
  reason) and either carry the receiver's maximum in Hello or fix 16 MiB as the universal ceiling for any
  encoded contract value in every mode; decide whether an oversized Event fails only its subscription
  (which would change l.723-724).

#### ND-04 — Array length cannot be bounded
- **Specs:** cdCDDLe §5.1 l.172, §7.4 l.324-326, §9 l.503-509 (only `*` occurrence on one array member);
  COMMITMENT §9.1 l.1295-1296 (`size-constraint` only on `tstr`/`bstr`); INTERFACE §1.7 l.410, §2.6
  l.1373-1374, CA §1 l.107-108, RUNTIME l.2239 (the specs bound their own lists in prose, with no code for
  a prose-bound violation: the value still conforms to `[* T]`).
- **Issue:** every list in a contract (rosters, histories, catalogues, endpoint lists, batch inputs, paging
  limits) is unbounded by schema.
- **Impact:** bounds live in prose and are enforced inconsistently.
- **Overlap:** CM-10 (alternative spellings), IF-03/G62. Minor.
- **Suggested resolution:** admit bounded occurrences `[n*m T]` (at least `[1* T]` and `[0*m T]`) as a
  `size-constraint` on `list-schema`, enforced by the validator with no C-layout change.

#### ND-05 — Dynamic-key maps are forbidden with no sanctioned replacement; key uniqueness and set semantics cannot be declared
- **Specs:** INTERFACE §1.7 l.423, §2.6 l.1398, §5.1 l.2449; cdCDDLe §5.1 l.171, §9 l.503-505; CA §1
  l.107-116 (a receiver MUST-reject rule the schema cannot carry); COMMITMENT l.265-268; the specs' own
  dictionaries use list plus prose (RUNTIME l.2105-2113 with l.2239; l.2652-2653) and the ordering primitive
  exists (INTERFACE §4.4 l.2281).
- **Issue:** catalogues keyed by a composite key, values per asset, endpoints per network, rosters keyed by
  account id and per-network settings maps all become lists with uniqueness stated in prose.
- **Impact:** every contract invents its own association-list convention.
- **Overlap:** CA-04/G50 (proof arrays). New.
- **Suggested resolution:** admit typed `{ * K => V }` for scalar `K` (deterministic-CBOR key order exists),
  or define in INTERFACE §1.6 a normative association-list convention (`[* {key: K, value: V}]`, unique
  keys sorted by the deterministic encoding of `key`) with a validator rule.

#### ND-06 — No declarable opaque-payload form
- **Specs:** INTERFACE §1.7 l.421 (`any` forbidden), l.425 (`.cbor` reserved), §5.1 l.2386 and
  l.2497-2500 (`logos.error_detail` is a `bstr` typed by an external root in prose), l.2462-2464 (no
  introspection inside); RUNTIME l.2107 with l.2237 (constraints: the same pattern); CONFIG §5 l.314-315;
  HASH §4 l.222-239 (a byte-chunked leaf with no path inside); RUNTIME §12 l.3291-3310.
- **Issue:** a module that forwards an external JSON-RPC API (a method name plus arbitrary params and
  results), or relays externally defined request formats that no single schema can enumerate, can use the
  pattern by example (declare `bstr`/`tstr` and define the content in prose), but it has no normative
  sanction, no common type, no presentation rule for generic clients, and two spellings of the same JSON
  commit to different roots.
- **Impact:** passthrough contracts are each non-standard.
- **Overlap:** D20 (the Nim plan's own contract choice). New.
- **Suggested resolution:** admit `bstr .cbor T` for externally-rooted CBOR and/or define
  `logos.json_text = tstr` declared uninterpreted, byte-committed and non-introspectable, with a stated
  presentation rule.

#### ND-07 — Domain failures must be typed response arms, but no common shape exists; the specs declare the same `{code, ? message}` record four times
- **Specs:** INTERFACE §1.4 l.337-338, §4.6 l.2319-2337, §5.1 l.2476-2477, l.2523-2524 (domain failures
  MUST NOT use the detail channel), §5.1 l.2365-2425 (no domain-error record); PM §15 l.1312-1319 (a PM-local
  convention never generalized), l.1403-1413; LOADER l.342-354, l.590-593; CA l.463-466 (`denial`),
  l.488-490, l.549-552, l.649-652; RUNTIME §9.3 l.2113; COMMITMENT l.493-500 (both `{} / { error }` and
  double `status` arms are valid examples).
- **Issue:** a CLI, a generic call view in a host UI and a broker that relays any provider's outcome to a
  requester cannot tell structurally which arm means failure.
- **Impact:** generic tooling must be taught each contract's failure shape.
- **Overlap:** EC-04, EC-10, G89 (the implementation's CLI invented an "any domain-error arm" detection for
  exit code 3: evidence the plan hit this). New: no normative shape and the specs' internal inconsistency.
- **Suggested resolution:** `logos.domain_error = { code: tstr .size (1..64), ? message: tstr .size
  (0..512) }` in §5.1, a SHOULD-level response convention (`{ ...ok } / { error: logos.domain_error }`)
  detectable by `logos.schema` consumers, and PM, CA and LOADER referencing it.

#### ND-08 — Named types cannot be shared between interface contracts, or between an interface and the primary contract of a module implementing it
- **Specs:** INTERFACE §1.1 l.97 ("An interface contract schema MUST NOT reference a supporting schema"),
  l.98, l.100-101, l.111-112 ("An _implements entry is a whole-interface dependency and not a named-type
  import"), §1.2 l.182-184 (inheritance and composition are non-goals), §1.3 l.224-226 (`logos.` names
  reserved, so third parties cannot extend the common schema), §5.1 l.2444; COMMITMENT §3.1 l.352-354, §5
  l.654-655, l.676-686, §8 l.1104-1107.
- **Issue:** two interface contracts I1 and I2 for one domain share record types (an account, a key path,
  a network id); a broker module B implements I1, consumes I2 and relays both through its primary contract;
  a provider implements I1 beside its own types. Every shared type must be re-declared under a distinct
  identity, so the same record has as many identities as contracts.
- **Impact:** brokers and implementers convert between structurally identical types.
- **Overlap:** none (CM-03/G6 is referencing common callables; CM-14/G14 document scope; SO-07 namespaces).
- **Suggested resolution:** allow interface contracts to reference explicitly supplied supporting schemas
  (the construction input and `logos.schema_response` already model them) and allow a concrete module to
  reference the named types of the interfaces it implements as imported references.

#### ND-09 — No surface carries human-readable descriptions of contracts or methods
- **Specs:** INTERFACE §1.2 l.121-197 (metadata is `_module`/`_interface`/`_implements`; l.150 the namespace
  is "human-readable metadata"), §5.1 l.2412-2423, l.2438-2446 (`document` must reconstruct the identity;
  comment survival unspecified), §5.3 l.2863-2900, l.2869 (dynamic schema text contemplated "for user
  presentation"); COMMITMENT §3 l.248-253; cdCDDLe §7 l.235-237 (comments removed before canonicalization,
  no retention defined); CONFIG l.318, l.373 (the configuration `document` is the source text, so comments
  do reach a settings UI there); PM §4 l.271-279.
- **Issue:** a host listing a module's purpose and methods, an approval UI explaining a request kind, and a
  developer guide generated from contracts have no description to show.
- **Impact:** descriptions travel outside the contract.
- **Overlap:** HC-09, SO-01, NP-01 (package metadata). Minor.
- **Suggested resolution:** state whether `document` is the authored source with comments preserved;
  define a doc-comment convention (`;;` lines before a declaration) that `logos.schema` consumers may
  present; see NP-01 for package-level fields.

### 2.7 Packaging

#### NP-01 — No human-facing metadata at any identity level; browsing a catalog costs one verified fetch per entry
- **Specs:** PM §4 l.263-279 (manifest and `module_declaration`: package, version, modules, variants,
  dependencies; artifact, contracts, requires, requested_permissions, configuration), l.297 (`reason` is
  the only human text), §6 l.774-777 (`package_catalog_entry = {identity, source}`), l.795-796 ("Catalog
  entries contain location data only; they do not carry another manifest or trusted package metadata
  projection"), l.798, §4.4 l.562-568 (catalog records are "discovery and presentation inputs" with nothing
  presentable defined), §15 l.1374-1378, l.1460 (`list_packages` filters by exact name), l.1471-1477
  (`inspect_package` resolves the full closure); RUNTIME §9.3 l.1853-1865 (`module_record`), l.2540-2543;
  COMMITMENT l.903 (unknown manifest fields are rejected, so a deployment cannot extend it); BCP §5.3
  l.305.
- **Issue:** a store UI shows name, description, category, icon and author per catalog entry; a provider
  chooser shows a display name and package per candidate; an approval UI must name the requesting module
  from signed data. Under the specs a store must download and verify every package to show a name, and
  even then the manifest has none; the only unsigned place (the catalog) is barred from carrying a trusted
  projection; a signed `resource`/`data` artifact under a conventional id is the only carrier, and it is
  implementation-private and unavailable before install.
- **Impact:** no portable store or chooser can be built over the specified surface.
- **Overlap:** SO-01/G90/G150/D17 (catalog document format, origin and refresh), HC-12 (instance alias),
  HC-01 (publisher invisible at route time). New: no display name, description, publisher, icon, category,
  license or homepage anywhere in signed or Runtime data; the browse cost; no search or category filter.
- **Suggested resolution:** an optional signed `metadata` map in the manifest or `module_declaration`
  (display name, description, publisher display name, icon artifact id, category, license, homepage,
  localizable), a manifest-commitment-bound projection of it plus `implements` in catalog entries so UIs
  render before download, and an operator-assigned label on `create_module` surfaced in `module_record`
  and `route_record`.

#### NP-02 — No executable artifact kind: LGX fixes 0644 modes, forbids symlinks and scripts, and every realization strategy ends in a dynamic library
- **Specs:** PM §4 l.324 and §10 l.1066 (`kind` is module-binary / resource / schema / data), §7.1 l.814
  (no installation scripts), l.837 (no symbolic or hard links), l.846 (LGX writers: "regular-file modes
  MUST be 0644"; nothing addresses modes at extraction), l.871-873; §7.3 l.1073 (the Nix profile has no
  mode rule but each artifact is one file, so a bundle has no internal symlinks); LOADER §3 l.142-158,
  l.181-202 ("The Module Host loads the same form of dynamic library used by direct_dynamic"), l.219-222
  (descriptors carry no arguments or environment), l.401, l.660 (a Module Host serves only the
  Runtime-created listener); RUNTIME Abstract l.36 (process creation belongs to profiles); CA §3.5 l.350-358;
  SECURITY §11.2 l.404, §11.4 l.426, §11.5 l.440 (separately installed processes, XPC services, extensions
  are named as provider forms with no normative counterpart).
- **Issue:** D ships a separately signed helper executable (or application bundle) beside its library and
  spawns it, so that the OS attributes device consent to the helper's own identity; another module ships a
  tool or emulator. None of these is a `module-binary`, and a `resource` arrives 0644 with no bundle layout;
  no rule says a module may execute its own artifacts; a separately signed executable cannot be a provider
  through any Core strategy.
- **Impact:** modules that need their own OS code identity cannot be packaged.
- **Overlap:** PM-11/G93 (a module cannot locate its artifacts), SO-05/D25/G110 (no process-creation
  permission), G41, G112, D19. New: the missing executable/bundle kind, the mode and symlink rules, the
  absent execution rule, the absent realization strategy for signed executables.
- **Suggested resolution:** an `executable` (or bundle) artifact kind extracted 0755 with preserved trees
  (symlinks allowed inside the variant directory); a realization strategy whose artifact is a signed
  executable implementing the Module Host role itself (verified and launched by the Loader, speaking the
  protected local transport); a process-creation permission whose constraints name the artifact id; paired
  with PM-11's artifact table so the module can find the path.

#### NP-03 — Presentation modules have no package representation: `module-binary` is mandatory, `resource`/`data` are never defined, and no entry-view, icon or app-kind declaration exists
- **Specs:** PM §4 l.272-274 (`artifact` required), l.351-352 and §9 l.1022 (it MUST be `module-binary`),
  l.324 and l.1066 (the words `resource` and `data` occur only in the enumerations), l.1078 (artifact ids
  are logical roles); RUNTIME Terminology l.84 (an implementation is "Code, resources, or built-in
  behavior"), Abstract l.35-38, §11 l.3283-3287; LOADER §3 l.142-174 (every strategy is a native binding or
  library); BCP §2.1 l.94-103, §5.3 l.305 ("Presentation interoperability | No profile assigned"), §5.4
  l.331, §7 l.415-452 (informative); SECURITY §12 l.461, §3.1 l.127-135 (the acceptance chain is stated for
  native code); CA §3.3 l.285-288.
- **Issue:** a presentation module declares a view entry file, an icon and a display name; some have no
  native code at all (only interpreted view files); H loads another module's interpreted view files into
  its own process and sandboxes them. Under the specs a module without native code cannot be declared,
  nothing marks a module as a launchable application or names its view artifact, and interpreted content
  executed by H has no artifact flag, no acceptance step, and its calls are attributed to H (RUNTIME §7.5
  l.1225-1226) unless a profile says otherwise.
- **Impact:** graphical applications have no portable package form.
- **Overlap:** RT-01/G83 (terminal hop), PM-11/G93. New: the graphical facet.
- **Suggested resolution:** an optional `presentation` declaration in `module_declaration` (profile id,
  entry artifact id, icon artifact id); allow a presentation entry (or a profile-provided stub) in place of
  `module-binary`; define the `resource`/`data` kinds and an "interpreted executable" flag; a minimal
  graphical presentation profile stating how a host obtains the entry artifact, binds the module's routes
  and attributes the view's calls.

#### NP-04 — Statically bound (mobile) modules cannot be described by a signed package
- **Specs:** PM §4 l.272-274, l.351-352 (a declaration needs a `module-binary`), §7.1 l.865-869
  (declarations without one are "not selected" and produce no handoff), §12 l.1241-1244 (`runtime_handoff
  .artifact` mandatory), l.1292-1294; RUNTIME §8 l.1266-1268 ("implementation-local inputs ... formats
  remain implementation-defined"), §13.3 l.3397-3422; LOADER §3 l.142-147, l.172-174; CONFIG §4 l.122, l.129;
  SECURITY §11.5 l.439-441.
- **Issue:** with modules bundled as `direct_static` on mobile hosts (D19, G105, G106), a module's signed
  configuration schema and default, `requested_permissions` and `requires` reach the Runtime only through
  implementation-defined bootstrap input, and one package cannot declare the same module for a dynamic
  desktop variant and a static mobile variant.
- **Impact:** signed package facts are lost on static platforms.
- **Overlap:** SO-03/G137/G141 (formats of protected inputs), PM-15/G142, D19/G105/G106. Minor.
- **Suggested resolution:** a per-variant static implementation form in `module_declaration`
  (`static_binding: tstr` in place of `artifact` for that variant) with `runtime_handoff.artifact`
  optional in that case.

#### NP-05 — No license or attribution metadata, and LGPL replaceability versus byte binding has no stated path
- **Specs:** PM §4 l.263-279, l.323-329 (no license field), §6 l.795-796, §10 l.1085-1088 ("MUST keep each
  installed path bound to the verified bytes"), §7.1 l.863, l.871 (non-binary artifacts' binding after
  extraction unstated), §4.1 l.404-411, l.440-441 (a deployment may add its own package-signing anchor);
  LOADER §3 l.202-210; SECURITY §10 l.365.
- **Issue:** a module that links an LGPL library dynamically as a separate file the user may replace, or
  ships licence and notice files beside its binary, cannot name them, and in-place replacement collides
  with the byte binding, which is deliberate TOCTOU hardening. The only path left is "rebuild and install
  under your own anchor", which the specs never state.
- **Impact:** licence compliance mechanisms must change and are undocumented.
- **Overlap:** PM-11/G93. Minor.
- **Suggested resolution:** per-artifact `license`/attribution metadata (or a licence/notice artifact role)
  and a normative statement of the intended replacement path (a user-local package-signing anchor through
  l.440-441), or a declared `replaceable` flag excluded from the byte binding and audited.

#### NP-06 — Variant selection cannot express a minimum Runtime init-ABI or OS version
- **Specs:** PM §4 l.316-320 (`platform_constraint`), §7.1 l.855-859 (exact match on os/architecture/abi),
  §8 l.991-992 (`incompatible-platform`), §10 l.1082-1083 (registry delegated to profiles); INTERFACE §5.2
  l.2624, l.2766-2776 (ABI 1 with append-only revisions; VERSION_MISMATCH at `_init`); RUNTIME §8.1
  l.1428-1432, §13.1 l.3329-3343.
- **Issue:** a package built against a future incompatible init ABI, or one that needs a minimum OS version
  or API level for a device API, installs successfully and fails at start.
- **Impact:** incompatibility appears as a start failure instead of `incompatible-platform`.
- **Overlap:** PM-10/G73 (value registry). Minor.
- **Suggested resolution:** `? requires_runtime: { init_abi: uint, ? min_os_version: tstr }` on
  `platform_constraint` or `module_declaration`, checked at variant selection with `incompatible-platform`.

#### NP-07 — The "selected installation root" is undefined, and whether installed sets are per user or per host is undocumented
- **Specs:** PM §7.1 l.840-841 (the term occurs once, in a MUST), l.868-869, l.871 ("a Package Manager or
  deployment-controlled location"), §15 l.1492-1493, l.766; RUNTIME §8 l.1397-1400, §9 l.1473-1476; BCP
  §5.4 l.325-331 (names Runtime directories, not the PM location); SECURITY §11.2 l.402-403.
- **Issue:** a headless daemon and a desktop application on one machine, or two user accounts, each run a
  PM whose installed set is its own; nothing says how several PM instances on one host relate.
- **Impact:** installations collide or duplicate across processes and users.
- **Overlap:** SO-03, G143, G88. Minor.
- **Suggested resolution:** define "installation root" (one per PM instance, selected by protected
  deployment input) and add the per-user/per-host scope and the multi-instance rule to BCP §5.4.

#### NP-08 — The Package Manager defines no events, `install_package` is one blocking call, and Runtime Control has no record-created event
- **Specs:** PM Abstract l.22 ("progress reporting, and lifecycle automation may be defined separately"),
  Scope l.123-124 (a package lifecycle event stream is out of scope), §15 l.1357-1370, l.1395-1405,
  l.1416-1421, l.1452-1463 (`list_installed_packages` is one snapshot, no revision); TRANSPORT §5.3 l.751
  (no async methods; the §5.3 pattern cannot be attached to the fixed PM contract root); RUNTIME §9.3
  l.2213-2219 (`module_state_changed_event` needs `old_state`, so creation into `unloaded` cannot be
  expressed), l.3043-3048 (creation is not among the causes that advance `execution.revision`), l.3095-3099;
  G61 (30 s default call timeout).
- **Issue:** hosts, store UIs, download managers and capability registries coordinate through
  install/uninstall and progress events; a package of several hundred MB fetched inside one
  `install_package` collides with any sensible call timeout; an orchestrator learns of a `create_module`
  by another consumer only by polling `list_modules`.
- **Impact:** every installer UI polls snapshots and shows no progress.
- **Overlap:** SO-09/G100 (long operations, for the implementation's own contracts), SO-01/G150 (catalog
  refresh), RT-02/G48. New: installed-set change notification, an installed-state revision, PM-specific
  progress, a record-created event.
- **Suggested resolution:** `installed_set_changed_event {identity, change, installed-state revision}` and
  an optional progress event keyed by the request under ordinary subscription authorization (or at least an
  installed-state revision on `list_installed_packages`); a record-created event in Runtime Control.

#### NP-09 — Platform-integration material (udev rules, usage descriptions, entitlements) has no declarative home
- **Specs:** PM Scope l.116, l.120 (permission approval rules out of scope), §1 l.148-153, §7.1 l.814
  (no scripts), §4 l.294-298 (`requested_permission` is a declarative hook once a profile defines the
  permission); CA §3.5 l.351-366, l.372 (an unenforceable scope fails at start); SECURITY §5 l.219, l.224-225,
  §11.1 l.388-389, §11.2 l.404, §11.6 l.450; BCP §5.4 l.326-327, l.331.
- **Issue:** a module driving a USB HID device needs a udev rule on Linux; a smart-card module needs the
  host's PC/SC service; a helper that opens a consent-gated device needs usage descriptions and
  entitlements inside a signed bundle. The no-scripts rule is right, but nothing says that an enforcement
  component may install enablement material when applying a permission setting, and no install-time check
  tells the user that the host cannot satisfy a requested permission.
- **Impact:** device modules install cleanly and fail at start.
- **Overlap:** SO-05/D25/G110. Minor.
- **Suggested resolution:** a `platform-integration` artifact kind or declaration (udev rules, usage
  descriptions, entitlement lists) installed by the profile's enforcement component under PM or deployment
  control, and an install-time "cannot satisfy permission" report.

#### NP-10 — Package-signing trust input has no anti-rollback rule, and the running-module response to signer withdrawal has no owner
- **Specs:** PM §4.1 l.402-429 (no revision rule; l.429 "Whether an already-running module is stopped is a
  separate Runtime and active-authority decision"), §4.2 l.464-476 (retention of signer state only "under
  such a profile"), §4.3 l.547-551; RUNTIME §9.3 l.2361-2370 (the remote trust-anchor set has a monotonic
  revision), §3.6 l.695-698, §10.1 l.3241-3242; CA §8 l.701-703 (the mechanism to end execution
  authorization exists, with no trigger from package-signing state).
- **Issue:** a rolled-back trust file re-admits a revoked signer; one deployment stops instances of a
  withdrawn signer mid-work, another never does; the asymmetry with l.2361-2365 is unexplained.
- **Impact:** signer revocation is neither durable nor predictable.
- **Overlap:** G137, G87, SO-03, CA-01/G46. Minor.
- **Suggested resolution:** mirror l.2361-2365 for package-signing trust input and state the default for
  installed instances of a withdrawn signer (or name the CA policy transition that drives it).

### 2.8 Configuration and state

#### NC-01 — A configuration-schema change strands every installed instance: no party, hook or fallback re-supplies a value
- **Specs:** CONFIG §7 l.224 ("MUST NOT reinterpret or migrate an existing record automatically"), l.226,
  l.235, l.240 ("defines no general configuration-migration language"), §4 l.133-134 (the package default
  is explicitly excluded as fallback), §3 l.118, l.222 (retention under an unchanged commitment is only a
  MAY), l.239 ("An authorized module instance MAY obtain an old value, transform it outside Core");
  RUNTIME §9.3 l.3056-3059, l.3072, §10.1 l.3226-3228; SECURITY §14 l.512.
- **Issue:** a package update that adds one optional field to a module's configuration schema leaves the
  instance unable to start or recover until some module with configuration authority and
  module-specific knowledge rewrites the value; on the G92 upgrade path (new instance) the old instance's
  configuration is dropped.
- **Impact:** routine package updates stop configured modules.
- **Overlap:** RT-06/G92, G141 (first provisioning), HC-04. New: the post-change stranding, the undefined
  responsible party, the excluded default, the MAY at l.222.
- **Suggested resolution:** a module-side hook `logos_<module>_migrate_configuration(old_commitment,
  old_value) -> new_value` invoked before the first start under a new commitment (the module alone knows the
  semantics), or let the declaration mark its package default as an accepted fallback on schema change;
  make l.222 a MUST retain.

#### NC-02 — Package-default acceptance is a MAY, a start with no eligible value has no code, and there is no reset-to-default
- **Specs:** CONFIG §4 l.129 ("Runtime MAY accept a package default as the staged value"), §3 l.118, §5
  l.162, l.171-183; RUNTIME §9.3 l.3108-3118 (prose; `start_module_response` carries only `state`), §3.4
  l.633, l.2170-2183 (`update_configuration` actions: stage, discard); PM §12 l.1264-1266, §14 l.1349,
  l.1234-1239 and l.1466 (`get_runtime_handoff` exposes `local_path` host paths to whoever may read the
  default).
- **Issue:** H installs a package from a catalog and starts it: one Runtime starts with the signed default,
  another refuses with an implementation-chosen code; a "Reset to defaults" action has no Core operation.
- **Impact:** install-then-start differs across conforming Runtimes.
- **Overlap:** G141, EC-03/EC-04 (same unassigned-code family, no "no configuration value" row).
- **Suggested resolution:** make package-default acceptance a MUST (or a declared package choice), add a
  `reset-to-package-default` action to `update_configuration`, and assign the start-refusal code.

#### NC-03 — Error-code table additions for configuration and permission operations
- **Specs:** CONFIG §5 l.178 (validate the complete value against the configuration schema: no code),
  §1 l.45 (operations on a binding-less instance MUST be rejected: no code); INTERFACE §5.1 l.2511
  (`schema-mismatch` is defined against "the selected request schema", which the inner value is not),
  l.2476-2477; RUNTIME §9.3 l.2185-2189 (`update_configuration_response` has no failure arm), l.2254,
  l.2259 (stale permission `expected_revision`). (An oversized value is covered: CONFIG l.314-315 types
  `value` at 8 MiB, so request validation fails with `schema-mismatch`.)
- **Issue:** a settings UI staging a value that violates the module's configuration schema (below a
  module-defined minimum, for example) gets no defined code and no path into the value.
- **Impact:** settings UIs cannot point at the offending field.
- **Overlap:** EC-02/G19, EC-04/G21. Minor.
- **Suggested resolution:** new `invalid_params_reason` values (`configuration-schema-mismatch` with a
  path into the value) or typed failure arms on the configuration and permission responses; a row for a
  configuration operation on a module without a binding.

#### NC-04 — Persistent state: the declaration RUNTIME refers to has no carrier, `state_dir` may be null for a module that needs it, and no state class, size, quota or backup semantics exist
- **Specs:** RUNTIME §8 l.1294 ("persistent-state needs" a module "may declare": defined nowhere),
  l.1310-1326 (assignment is policy; l.1320 "no persistent-state guarantee"; l.1322-1323 fail-closed only
  "If ... has a state assignment"), §9.2 l.2291-2296, §9.3 l.1853-1865 (`state_assignment` opaque, no
  size); INTERFACE §5.2 l.2558-2561 (`state_dir` null means none assigned); PM §4 l.271-279 (no field),
  l.294-298 (`requested_permissions` is the designated carrier once a profile defines the permission);
  CA §3.5 l.357 (persistent-state facility), l.360 (`storage-growth` limits) with no defining profile;
  LOADER Scope l.68, §5.1 l.283-284; BCP §5.4 l.328; SECURITY §11.5 l.436-438, §13 l.489.
- **Issue:** a module that needs persistent state, initialized on a deployment that assigned none, must
  fail `_init` with no way to have asked; multi-GB reconstructible data and a sealed secret share the same
  opaque assignment; a mobile host cannot exclude bulk data from backup or report usage per module; the
  footprint cannot be shown before install.
- **Impact:** state needs are discovered at start, and storage policy cannot distinguish kinds of data.
- **Overlap:** SO-05 (permission vocabulary), PM-11, G143/D21/G144 (the Nim layout always assigns state),
  RT-06/G92. New: the dangling declaration, nullable `state_dir` for a requiring module, state classes and
  size, backup class.
- **Suggested resolution:** a persistent-state declaration in `module_declaration` (required or optional;
  classes secret / durable / reconstructible cache with an expected size each; growth); Runtime MUST fail
  realization rather than pass a null `state_dir` to a module that requires state; size and class per
  assignment in `module_record` or a `get_state_summary`; define the `storage-growth` constraint shape.

#### NC-05 — Secrets travel as method parameters, every request is committed deterministically, and nothing can mark a field secret
- **Specs:** HASH §5 l.378-379 (a scalar leaf commits to schema identity, kind and canonical value, nothing
  else), l.393-399, §6.1 l.506-509 ("MUST NOT use keyed hashing, key derivation mode, a context string"),
  §8 l.1077 (no encrypted selective disclosure); TRANSPORT §4.1 l.580-587 (the whole params value is
  committed in every Request); RUNTIME §9 l.1591-1602 (roots computed on every call); CA §4 l.382-395,
  l.426-427 (an allow decision may add `retain-root`; the provider cannot remove it), §9 l.945-948, l.977-982
  ("callers authorized to see only roots"), §9.1 l.1071-1074, l.1084-1085 (the duty "Audit records MUST
  NOT contain ... secrets" rests on the auditor), §13 l.1181-1185; SECURITY §9 l.342-343, §10 l.365-370
  (the guessable-root hazard is unnamed); cdCDDLe §5.1 l.173 (only `.size`), INTERFACE §1.2 (metadata is
  `_module`/`_interface`/`_implements`; "sensitive" appears nowhere as a marker), §2.7 l.1486-1519
  (ownership only; no zeroization text in any file); RUNTIME §7.3 l.1178-1179 (the dropped-event diagnostic
  has no content rule).
- **Issue:** a policy that retains request roots on a method taking a password (`unlock(password)`), a
  short PIN (`sign{..., pin}`) or a recovery secret, or on a method whose response is a recovery secret,
  stores an unsalted BLAKE3 commitment that a 10^4 to 10^8 dictionary inverts offline once the other fields
  are known; identical requests give identical roots (repeated amounts and addresses are linkable); the
  module cannot refuse retention and the schema cannot say which parameter is a secret, so the auditor
  cannot discharge l.1084 from the contract; decoded copies at the Runtime boundary, in generated dispatch
  and in caller helpers have no erasure rule. Retention is opt-in (G115 keeps it off in one deployment),
  which mitigates and settles nothing.
- **Impact:** audit stores become an offline oracle for low-entropy secrets.
- **Overlap:** CA-07/G115 (evidence export; retain-root off by default), HC-09 (logging), CA-04/G50,
  HC-03. New: the guessable-root hazard, the missing sensitivity marker, the provider's lack of veto, memory
  hygiene, diagnostic echo.
- **Suggested resolution:** a schema-level `sensitive` marker (a control or wrapper type) with normative
  consequences: excluded from or blinded in payload commitments (a per-value random salt committed inside
  the value tree), no `retain-root` or verified-view proof over the path (an enforcement failure if policy
  asks), no diagnostic echo, zeroization at every decoding boundary; or a per-method no-retain declaration;
  name the hazard in CA §13 and SECURITY §10.

#### NC-06 — User-selected files: no carrier for a per-operation OS file capability
- **Specs:** TRANSPORT §8.2 l.956 (the only descriptor transfer is the Runtime-created listener); PM §4
  l.294-298, l.353 (constraints are fixed bytes in the signed manifest; a user-approved per-operation grant
  is representable in the authority model but has no carrier for the capability object); RUNTIME §8 l.1326,
  §12 l.3301-3307 (bytes and chunking as the fallback); INTERFACE §5.2 l.2561; CA §3.5 l.344-349, l.356;
  SECURITY §11.2 l.402, §11.4 l.413.
- **Issue:** an export or import through a file picker on a sandboxed OS: the UI module holds a
  user-selected file, the module that must read or write it runs in another process with no permission for
  that path, and the OS-issued capability (descriptor, security-scoped bookmark, content URI) has no way
  across. Bytes in chunked methods work for small files, not for a user-chosen data directory.
- **Impact:** user-chosen locations cannot be handed to a backend module on sandboxed platforms.
- **Overlap:** HC-08 (paths vs bytes), SO-09/G99, SO-05, HC-13, C-10. Minor.
- **Suggested resolution:** a `file-handle` permission constraint and a Transport/Loader handoff for an
  OS-issued file capability scoped to one operation and consumer, or a normative statement that
  user-selected files are always carried as bytes.

### 2.9 Security and deployment profiles

#### NS-01 — OS device consent is attributed to the application, which SECURITY §11 never says, so a per-module device permission has no enforcement component in a generic Module Host
- **Specs:** CA §3.5 l.351-353, l.359, l.363-366, l.372 (an unenforceable scope fails the dependent
  operation); SECURITY §11 l.377-378 (a platform profile maps enforcement to platform facilities), §11.2
  l.404 ("whether a provider is an embedded library, XPC service, or separately installed process"), §11.4
  l.426-427, §11.5 l.440, §11.6 l.450, §13 l.489; LOADER §1 l.102-105 (platform-specific process settings are
  deployment configuration; a per-module host identity is possible), §3 l.190-193 (one generic Module Host
  form; its executable identity and signing are never discussed).
- **Issue:** the major desktop and mobile OSes attribute camera, Bluetooth and similar consent to the
  responsible process's code identity; a grant to module D and a denial to module E have no component that
  can enforce them once the host application holds the consent, and under l.372 every device scope then
  fails. The working recipe (a separately signed helper with its own identity) matches no Core strategy
  (NP-02). Screen capture is absent from the l.353 facility list (non-exhaustive).
- **Impact:** per-module device permissions are unenforceable as specified.
- **Overlap:** SO-05/D25/G110 (permission vocabulary; the Nim choice of one ambient permission leaves OS
  consent outside the model). New: the attribution fact and its consequence for profile authors.
- **Suggested resolution:** state in SECURITY §11.2, §11.4 and §11.5 that OS device consent is per
  application and that per-module device permissions require a separately identified executable (helper
  application, XPC service, isolated-process service) as the enforcement component; add the hosted
  placement or profile for such executables.

#### NS-02 — A Module Host whose owning Runtime dies: no semantics for loss of the realization-internal carrier
- **Specs:** RUNTIME §4.2.1 l.883-893 (the carrier between a Module Host and its Runtime is
  "realization-internal machinery"), §10.1 l.3209, l.3243-3246, l.3254-3256, §10.2 l.3262-3270, §9.3
  l.3067 (a restarted Runtime re-realizes rather than adopting survivors), l.2615 (`expires_at` bounds
  exposure only for remote routes); LOADER §1 l.87-90, §7 l.489-491 (the opposite direction only), §12
  l.661-663; TRANSPORT §8.1 l.851-854, §8.2 l.973; CA §8 l.703, l.715-718 (written for the Runtime).
- **Issue:** when the Runtime host crashes while a module that flushes on stop, or one that holds keys,
  runs in a Module Host, whether the host keeps dispatching on established sessions (expiry and revocation
  now unreachable), runs `_destroy` or exits is unspecified.
- **Impact:** orphaned hosts keep serving with stale authority, or lose data.
- **Overlap:** RT-05/G56 (hosts orphaned by a failed Loader; in the Nim layout Loader and Runtime die
  together), C-10/D14, CA-01/G46, D24, G61. Minor.
- **Suggested resolution:** loss of the realization-internal carrier is terminal: the Module Host MUST stop
  accepting and dispatching, run `_destroy` within the grace period and exit; a recovering Runtime treats
  such hosts as failed realizations.

#### NS-03 — Secret storage, backup exposure and secure deletion of module state are missing from the deployment-profile checklist
- **Specs:** CONFIG §1 l.52 (credentials MUST NOT be configuration, so every secret lands in `state_dir`);
  SECURITY §3.3 l.187-189 (storage protection is deployment-owned), §11.1 l.383 (desktop processes are not
  sandboxed), §11 "Logos consequence" lines l.396, l.404, l.416, l.427, l.438 (no secret store, backup or
  deletion item), §10 l.369; CA §3.5 l.357, l.359 (facilities named, undefined); LOADER §5.1 l.284; PM §15
  l.1491-1497 (`remove_package` carries no state-deletion rule); BCP §5.4 l.328; no file mentions keychain,
  backup, iCloud, DPAPI or secure deletion.
- **Issue:** per-module data keys, sealed secrets, password-encrypted vaults and device pairing secrets
  each get their own at-rest protection in a directory any process of the same user can read on an
  unsandboxed desktop; on platforms with credential stores there is no Logos permission, handoff or state
  class for them, and backup and sync exposure of `state_dir` is named nowhere.
- **Impact:** every key-holding module invents its own at-rest scheme and backup behaviour.
- **Overlap:** SO-05 (vocabulary), D21/G144 (the Nim choice), G143. New: the checklist omissions.
- **Suggested resolution:** require each platform profile to name the secret store and the
  backup-exclusion mechanism applied to `state_dir`, and add to RUNTIME or LOADER that state assigned to a
  module is excluded from platform backups and securely deleted on authorized removal.

### 2.10 Runtime Control observation and operations

#### NO-01 — Runtime Control list methods return `partial` with no continuation, no ordering and no `list_modules` filter
- **Specs:** RUNTIME §9.3 l.1949-1990 (`list_modules_request = {}`; responses are an array plus
  `partial`), l.2981-2990 ("the applicable response resource limit", a term used at l.1353 and l.2986 and
  defined nowhere), l.3195; contrast PM §15 l.1425-1437 and l.1449-1464 (cursor, limit, next_cursor,
  orderings) and CA §6 l.573-596 (`list_grants` cursor and limit); BCP §5.4 l.329-330.
- **Issue:** a deployment with dozens of instances and hundreds of routes can never enumerate the full set
  once `partial` is true, in no defined order; `list_routes` and `list_provider_exports` can at least be
  narrowed, `list_modules` and `list_remote_listeners` cannot.
- **Impact:** module managers and observers see an arbitrary subset.
- **Overlap:** CA-05/G51 (the sibling defect in the CA), G54, G75.
- **Suggested resolution:** `? cursor`, `? limit`, `? next_cursor` on the four list methods with PM §15's
  rules; define the record order (module-name bytes then instance-id bytes; route-id bytes); name the limit
  and its home.

#### NO-02 — Observation synchronization: lifecycle events carry no revision or timestamp, routes and facades have none at all, and membership changes fire no event
- **Specs:** RUNTIME §9.3 l.2213-2219 (`module_state_changed_event`: no revision, `? instance`),
  l.2207-2211 (`execution_state_changed_event`: revision, no lifecycle state), l.1897-1911 and l.2221-2228
  (route records and events: no sequence), l.3036-3037 (facades "MUST omit execution", so no revision),
  l.3043-3050 (the per-instance snapshot-plus-revision path that does exist: "advance", not increment;
  "Queries can resynchronize"), l.1669-1671, l.3095-3099 (`create_module` fires nothing), l.3008
  (listener/export changes have no event), the five events l.2137-2228; "timestamp" does not occur in
  RUNTIME; TRANSPORT §5.1 l.683-707 (gap detection is owed only by contracts promising reconstruction; RC
  promises none).
- **Issue:** an observer that lists modules and then follows events cannot order lifecycle events against
  the snapshot except through the co-emitted execution event, cannot see instances created by others,
  cannot show "in error since" or uptime, and gets no revision for routes or facades; deltas and snapshots
  overtake each other across a transported connection.
- **Impact:** every module manager builds its own reconciliation with timers.
- **Overlap:** EC-02/G19 (stale compare-and-set revisions), CA-05/G51, TR-02/G31, G54. New: observation
  synchronization and the missing events and timestamps.
- **Suggested resolution:** carry `execution.revision` (or a per-target sequence) and a `timestamp` in
  `module_state_changed_event`, `route_record` and `route_state_changed_event`; make `instance` mandatory
  for local instances; add record-created/removed and listener/export-changed events; state which TRANSPORT
  §5.1 model Runtime Control uses and which snapshot anchors it.

#### NO-03 — No per-instance resource usage observation, footprint declaration or typed limit-exceeded signal
- **Specs:** RUNTIME §9.3 l.1853-1865, l.2080-2090, l.2097-2103 (no usage fields), l.1912-2191 (no usage
  method), l.474-475 (the pid exists only in the internal registry sketch), Terminology l.199 and CA §3.5
  l.360, l.368-369, §12 l.1165 ("Runtime-owned resource accounting" as enforcement only; never defined);
  LOADER §7 l.431-446, §12 l.669-671 (PIDs deliberately excluded), Scope l.68; PM §3 l.270-330 (no footprint
  field), §14 (no insufficient-storage value); SECURITY §5 l.220, §10 l.367; BCP §8 l.464-478 (informative;
  "defines no observer contract").
- **Issue:** H wants to show CPU and memory per module so a user can stop a runaway one; a module needing
  tens to hundreds of GB of disk must be announced before install and its usage shown; when a CA
  storage-growth or memory limit is hit the outcome is a stopped module with a free-text reason.
- **Impact:** no portable resource view or limit diagnosis.
- **Overlap:** SO-05 (limit constraints), G75 (bound values), G143, EC-10, HC-09. New: usage observation,
  footprint declaration, limit-exceeded signal, the undefined accounting term.
- **Suggested resolution:** an optional `get_resource_usage(target)` (state bytes, resident memory, CPU
  time, network counters, applicable limits) and a `resource_limit_event` under module-observation
  authorization; an informational expected-footprint field in module declarations that PM and UIs may show
  before install; define the accounting CA §3.5 refers to.

#### NO-04 — No Runtime self-description, and `module_record` carries no package identity
- **Specs:** RUNTIME §9.2 l.1673-1706, §9.3 l.1679, l.2305-2312 (an opaque UUID; "MUST NOT infer ...
  package identity, schema compatibility" from it), l.1795-1798, l.1912-2191 (no describe or version
  method), l.1853-1865 (no package field), l.2065-2070 and l.3056-3058 (package identity per instance only
  through `get_execution_summary.selection`, one authorized call each); TRANSPORT §3.1 l.425-432 (Hello),
  l.476, l.501 (VERSION_MISMATCH carries no side information), §10 l.1165; INTERFACE §1.2 l.186, l.190.
- **Issue:** a diagnostics view or bug report needs "Runtime implementation and version, Runtime Control
  root, module m from package p version v"; a UI built against a newer Runtime Control root gets
  VERSION_MISMATCH at Hello and cannot say which side to update; `list_modules` cannot be joined to
  `list_installed_packages` when two packages declare one module name.
- **Impact:** version problems are undiagnosable from Core data.
- **Overlap:** HC-04 (no negotiation), HC-01, RT-04/G55, RT-06/G92, G54. Minor.
- **Suggested resolution:** a `describe_runtime` method (implementation name and version, supported Runtime
  Control and supporting-schema roots, configured limits such as frame size and list limits) and
  `? package: {package, version}` on `module_record`.

#### NO-05 — The initial `permission_settings_state` of a fresh instance is undefined
- **Specs:** RUNTIME §9.3 l.3096-3098 (`create_module` fixes lifecycle `unloaded` and intent
  `uninitialized`, nothing about permission settings), l.2110-2116, l.2126-2130 (`update_permission_settings`
  requires `expected_revision`), l.2240 ("Omitted permissions are denied, including when the array is
  empty; declarations and grants MUST NOT bypass these limits"), l.2243 ("revision MUST be positive"), l.2249;
  §9 l.1478-1482 (persistence owned by the Runtime host, formats outside the spec); §10.1 l.3227
  ("deployment intent initially blocked by missing permissions"); CONFIG §3 l.85 (the twin problem is solved:
  "initialize that revision to zero").
- **Issue:** after `create_module` for a module needing a device or network permission,
  `get_permission_settings` must return a positive `revision` although nothing was accepted; the first
  `update_permission_settings` needs an `expected_revision` nobody can know; until someone replaces the
  settings every permission is denied, so the module cannot start; whether the handoff's
  `requested_permissions` seed anything (as pending) is unstated (l.2240 rules out automatic seeding).
- **Impact:** the first permission grant on a new instance is implementation-specific.
- **Overlap:** SO-05/D25/G110, G82, HC-13, SO-06, EC-10. New: the initial state, first revision and seeding
  rule.
- **Suggested resolution:** define the initial state (revision 0 or 1, empty permissions, `applied`)
  created with the instance, and whether `requested_permissions` are staged as `pending` until an
  authorized replacement.

#### NO-06 — Effect of a permission-settings replacement that widens access for a running instance
- **Specs:** RUNTIME §9.3 l.2244-2247 (pending / applied / failed), l.2255 (repeating settings returns the
  existing state "without another update or restart", implying restart otherwise), l.2261-2264 (an
  enforcement failure leaves the module stopped; settings never create intent), §10.1 l.3226-3228 (the
  withdrawal case: intent preserved, orchestration resumes through `recover_module`); CA §3.5 l.363-364 and
  §8 l.757-758 (only the unenforceable or revoked case is delegated to the permission definition).
- **Issue:** a person grants a device permission to a running module D: stop and re-realize under the
  engine, live application, or next start only; and whether such a stop is the "permission withdrawal" that
  preserves intent.
- **Impact:** granting a permission may or may not restart the module.
- **Overlap:** CA-01/G46, G110, EC-10/G27, HC-13. Minor.
- **Suggested resolution:** state that a replacement for a running local instance stops it with intent
  preserved and re-realizes it, or define a per-definition live-application hook with fallback to stop.

#### NO-07 — CA module-execution actions {load, start, stop, unload} are never mapped to Runtime Control lifecycle methods
- **Specs:** CA §3 l.174 (`actions: [* ("load" / "start" / "stop" / "unload")]`), §3.3 l.285 ("covers
  Runtime-owned module load, start, stop, and unload operations"), l.300-301 (the only action given meaning:
  `start` includes realization for a hosted instance), l.302-310, §5 l.435-436 (each evaluation scope names
  exactly one action); RUNTIME §3.6 l.663 (dynamic loading is "an execution operation", bound to no action),
  l.681, §9 l.1560, §9.3 l.3072, l.3115 (the need named without an action); `unload` never appears as an
  operation in RUNTIME (`stop_module` reaches `unloaded`, l.3134).
- **Issue:** writing the grant that lets orchestration run module m: does `start_module` need `load` plus
  `start` or just `start`? Does `stop_module` need `stop` plus `unload`? Which action, if any, do
  `create_module` and `recover_module` consume?
- **Impact:** grants do not port between Runtimes, a conformance test cannot assert a denial, and audit
  records (which carry scopes, not method names) inherit the mismatch.
- **Overlap:** none (RT-04/G55 uses `module_execution_scope` for package pinning; CA-01/G46 for losing
  authority).
- **Suggested resolution:** a normative table (RUNTIME §9.3 or CA §3.3) giving, for each lifecycle method
  and target state, the action(s) an allow decision must cover; define or remove `load` and `unload`.

---

## Part 3 — Corrections and addenda to existing findings

Each entry names the existing item, what the re-reading found, and what to change. Items marked
"reclassify" keep their substance under a different heading.

### NF-01 — C-01: the quote is truncated, the BCP side is informative, and the contradiction is an ambiguity
- COMMITMENT l.697-698 in full: "Unqualified common names in source CDDL are interpreted as names in that
  namespace **when they are represented as qualified schema definition names**." The dropped clause makes
  the sentence readable either as a source-shorthand allowance or as a statement about the canonical
  representation. BCP §6 is titled "Module Kit (Informative)" (l.356), so l.388-391 cannot be the normative
  side; it remains useful evidence of intent (shorthand expanded "before cdCDDLe canonicalization").
  INTERFACE l.108 and l.302 are stated for local names only; the only normative pressure is INTERFACE
  l.111, l.2362 and l.2892 (reject unresolved or conflicting definitions). Reclassify as underspecified; the
  interim choice (reject) and the fix locus (COMMITMENT §5) stand.

### NF-02 — C-03: the real defect is that INTERFACE defines no conformance classes
- BCP §6.1 is informative (l.356, l.370 "conformance depends on the artifacts and behavior required by the
  owning specifications") and about code generation, so it is not a contradiction partner. INTERFACE's
  MUSTs bind tools (l.535, l.538, l.1607, l.2166) and the document has no conformance section (HASH has one at
  l.1225); l.437-438 names the conformance boundaries without the C mapping. Reclassify as a gap; the first
  resolution branch (a conformance class excluding C-first authoring, plus which §3.9 cases each class must
  pass) stands; drop the BCP rewording.

### NF-03 — C-06: TRANSPORT §9.1 settles the path question; the real residue is the address bound versus `sun_path`
- TRANSPORT l.1137-1139: "Its filesystem spelling is not an interoperability identifier. The caller MUST NOT
  derive or substitute another path from the module name." RUNTIME l.304's `<runtime-dir>` is the only
  occurrence in the twelve files and is undefined (it may be the per-instance 0700 directory of TRANSPORT
  l.952-953), and RUNTIME l.2298-2299 admits several instances per name, so the one-per-name reading is not
  the spec's intent. Downgrade to editorial (make RUNTIME §1.3's derivation informative or per-instance).
  New to the item: LOADER §5.3 l.309 bounds `provider_endpoint.address` at 4096 bytes while `sun_path` is
  104 (macOS) or 108 (Linux); no spec mentions the limit. See also NR-14 for the same profile.

### NF-04 — C-07: the ordering error value is `invalid-package`, and the citation is l.364
- PM l.363 is blank; l.364 reads "Package Manager MUST reject a manifest whose arrays violate these ordering
  or uniqueness rules." PM §14 l.1341 defines `invalid-package` as covering "an absent or invalid manifest",
  so the value is assigned (matching the interim choice); the §8 list l.971-986 has uniqueness bullets but
  no ordering bullet (editorial). The artifact-sharing contradiction (l.341 vs §8 l.984) and the missing
  check precedence stand.

### NF-05 — C-08: `unsupported-strategy` is assigned only to un-advertised strategies, so the premise does not hold; re-file as an error-code row
- LOADER l.372 is the only assignment: "MUST reject a strategy or hosted placement that it did not
  advertise with `unsupported-strategy`"; l.612 licenses Runtime to pick another *advertised* strategy, and
  l.318 forbids advertising a placement that would weaken isolation. The l.423 refusal ("MUST fail rather
  than substitute a weaker strategy ...") names no code; `realization-failed` (l.616-618) covers "unexpected
  realization failure" and, through l.617's "endpoint handoff or activation", the TRANSPORT l.960 case.
  Re-selection after `unsupported-strategy` is gated by CA §3.3 l.311-313 and l.321. The cited LOADER
  l.395-396 is the `abi-invalid` text, not a no-substitution rule. Replace the contradiction with an EC
  row: a code for an l.423 / §12 l.657 refusal.

### NF-06 — C-09: "Runtime-known" already admits instances owned by an enrolled source Runtime; only "resolve" is undefined
- RUNTIME l.87 ("owned by exactly one Runtime"), l.99 (a facade represents an instance "owned by another
  Runtime"), l.2281-2283, the l.1729 table, CA l.75-76 (the address's `runtime_instance_id` identifies the
  owner), l.206-209, l.280-281 ("Local and remote Runtime Control use the same scope shape") and RUNTIME
  l.1617-1623 (the target accepts consumers authenticated by the enrolled source) together give the item's
  interim reading; where CA means locally owned it says so (l.23). Reclassify as an underspecified term;
  the resolution gains one sentence defining "resolve" for a remote address as the ownership and
  forwarding check of RUNTIME l.1605-1611.

### NF-07 — CM-02: COMMITMENT §8 already settles the common-schema case
- COMMITMENT l.1036-1041: "For nodes whose meaning is defined by a common-schema definition, the node
  carries the common schema root and referenced schema subtree root." Every example the item names
  (`logos.schema_commitment`, `logos.error_detail`, Runtime Control records) is a common-schema reference,
  so field 1 beneath the reference node is the common schema root, the interim choice; drop the "outer
  root" alternative. HASH §7.4 still never labels field 1 beneath a reference, the §9.3 data shapes carry no
  `schema-root` on inner nodes (l.1427-1494), and supporting-schema imports are covered only by analogy
  (l.1104-1107 gives the reference node both roots and says nothing about descendants). Keep the vector
  request; cite l.1040-1041.

### NF-08 — CM-03: COMMITMENT §5 is not silent, and the undefined term is "permitted kind"
- COMMITMENT l.653-654 says a schema may reference "named definitions in the pinned Logos common schema"
  but l.664 narrows only the supporting case to "a named type"; l.1287 "exactly one declaration of the
  permitted kind" is the sole occurrence of the term and nothing defines it; INTERFACE l.101 ("the common
  Logos schema definitions") is broad while l.111 and the §1.7 table l.413 are narrow; the registry
  l.709-720 assigns subtree roots to `logos.schema_request/response` and l.364-370 contemplates module-side
  references to them. Fix the "(silent)" citation and name the defect; the interim choice stands on
  INTERFACE l.111 plus the l.664 analogy. Note that `foo.probe_request = logos.schema_request` is
  independently invalid under §3.1 step 5 (l.344-345: request bodies MUST be map or choice schemas); only
  the field-type case exercises the undefined kind.

### NF-09 — CM-06: answered by the closed, ordered selection-test list
- COMMITMENT l.447-453 is a closed ordered list (CBOR major type; exact scalar literal; fixed-tuple element
  count; presence and exact scalar value of a closed-map field; presence or absence of a closed-map field),
  each partition defined over the decoded value itself (l.455-459), and l.466-469 makes a choice invalid
  when no test makes progress. No test observes a tuple position or a nested map's field, so a literal two
  levels deep cannot distinguish arms: `{ a: { kind: "x" } } / { a: { kind: "y" } }` and `["ok", T] /
  ["err", E]` are invalid. The interim choice is consistent with the text; two implementations cannot
  diverge. Close CM-06; propose "nested literal" and "tuple-position literal" rows marked Invalid in the
  l.491-503 table.

### NF-10 — CM-10: cite cdCDDLe §7 l.239-240; the ambiguity is about construct identity
- cdCDDLe l.239-240 ("MUST normalize syntactic forms that are unambiguously equivalent in CDDL") bears on
  `0*`/`*1`/`0*1`, so "not mentioned" should cite it. Whether `0*` is an unsupported construct (rejected at
  the l.132-135 gate, whose supported forms are defined by spelling at l.147 and l.172) or a syntactic form
  of `*` (normalized inside the gate) turns on an undefined notion of construct identity in the resolved
  rule graph; every concrete normalization in §7 concerns literal presentation (l.241-243, l.454-456,
  l.668-669). The interim "reject" is not clearly non-conformant; both resolutions remain; add "state the
  scope of §7's rule" to the ask.

### NF-11 — CM-12: already determined by the text; editorial only
- The range node holds integer literals (cdCDDLe l.519-522); a named reference maps to a type-reference
  node (l.317-318) and MUST NOT be expanded (l.209-212); the only range canonicalizations are ordering and
  equal bounds (l.334-337); l.224 and l.134-135 then require rejection of `1..max_port`. "Reject" is
  determined; an implementation that inlined the bound would violate l.209-212 and l.245. Downgrade to
  editorial: add "with integer-literal bounds" to §5.1 l.163.

### NF-12 — EC-09: enrollment has no Runtime Control method that could fail
- Enrollment is "a provisioning and Runtime input record, not a new Runtime Control method" (RUNTIME
  l.2326-2327) accepted only through protected deployment input or the undefined provisioning operation
  (l.2334-2335); the cited l.2991-3017 cover `set_remote_listener` and `set_provider_export` only, and the
  method list l.1912-2191 has no enrollment method. Strike "enrollment" from EC-09; the listener and export
  validation failures stand. (The missing provisioning operation is NR-02.)

### NF-13 — EC-11: symbol defects beyond the l.3436 list are realization-time `abi-invalid`, not an unassigned `register_binding` code
- `logos_runtime_register_binding` validates only duplicates, empty tables and null addresses
  (RUNTIME l.3436); LOADER §6 l.386 step 1 ("resolve the mandatory ABI symbols for the expected module
  name") runs at `realize` for direct static realization too (l.375-376: the Loader is the ABI caller), and
  l.395 assigns "Missing, contradictory, or invalid ABI symbols and metadata" to `abi-invalid`; the instance
  goes to `error`. Reword EC-11 as a cross-reference request from RUNTIME §13.3 to LOADER §6/§10.

### NF-14 — CA-05: `query_audit` has no cursor and its order and bound are fixed; only `list_grants` is open
- `query_audit_request` (CA l.887-896) has no `cursor` and the response (l.897-902) no `next_cursor`;
  l.904-905 fix the result ("at most the 1000 most recent retained records", "ordered newest first").
  Cursors exist only on `list_grants` (l.577, l.584, l.592-596). Narrow CA-05 to `list_grants` order, cursor
  lifetime and since/until bounds, and drop the query_audit snapshot cursor from the implementation.

### NF-15 — CA-06: the interim choice produces call records the CA rejects (see NX-03)
- A call record MUST carry "exactly one" call scope with the `call` action and one method declaration root
  (CA l.948-953); each action-bearing scope in a decision names only the action evaluated (l.436-437), so
  an establish-route decision's scope (establish-route action, several roots) cannot be stamped onto a call
  record, and the evidence verifier reads "the single method declaration root" (l.1056). Until the specs
  settle NX-03, derive a single-method `call` scope from the route decision for each record rather than
  copying the route scope.

### NF-16 — HC-13: "not per call" describes RUNTIME only (see NX-03)
- CA has a `call` action (l.147-153), a per-call request shape (l.259-260) and re-evaluation of "new calls"
  after a policy change (l.748-751), so per-call denial is representable in CA; what is missing is any
  RUNTIME sentence saying when a call evaluation occurs. Correct HC-13's premise and point the ask at
  RUNTIME §9 (are method calls decision points, under what caching) or at CA §3.1 (drop the `call` action).

### NF-17 — RT-06: the premise over-reads l.3056-3059; the gap is when the selection is made or replaced
- l.3056-3059 govern what `get_execution_summary` reports (no inferred package identity); only recovery
  (l.3072) is required to preserve the selection; the `start_module` prose (l.3108-3121) says nothing about
  selection, so a Runtime that re-selects under active policy on every `start_module` after an explicit
  stop also conforms, and G92's stop/create/rebind/start procedure rests on the over-read. Re-file as
  underspecified: §9.3 should state when the selection is made (`create_module`) and whether an explicit
  stop followed by `start_module` reuses or re-makes it; then decide whether an upgrade operation is still
  needed. Also reconcile G143 ("identity and state survive package update and module upgrade") with G92
  (upgrade = new instance), which contradict each other.

### NF-18 — RT-05 addendum: a replacement Loader's idempotent `release` and `realization-not-found` hide the orphan
- A replacement Loader answers `get_status` with `realization-not-found` (LOADER l.496) and `release` with
  success (l.581-583 "establishes absence") for ids it never issued, so Runtime may report `absent`
  (RUNTIME l.3065) and accept `recover_module` while the old host still serves the Runtime-created listener
  and holds chain state open; `realize` for the same `module_instance` then succeeds (l.362-368) against the
  same state assignment. RT-05's rule must also define `release`/`get_status` for pre-replacement ids: they
  are `unknown`, not `absent`, until Runtime has closed the listener and the deployment mechanism confirms
  termination; releasing such an id is not a successful no-op.

### NF-19 — PM-10: citation fix
- The platform-registry sentence is PM §10 l.1082-1083 (Artifact Records), not §7.1; "selected runtime
  profile" is at §7.1 l.858 and §8 l.992. Substance unchanged.

### NF-20 — SO-09: TRANSPORT §5.3 defines a long-running-operation pattern; the ask is underspecification, not absence
- TRANSPORT §5.3 l.743-752 prescribes subscribe, request, ack, progress and completion events ("There is
  no 'async method' concept"), and l.736-741 with RUNTIME l.1189-1195 make events notifications only, so
  results are fetched by method. SO-09 should cite both and argue what the pattern lacks: a stated rule
  that events carry only correlation data and the ack returns the id (NE-01), access control for the fetch
  without caller identity (HC-03), ordering of the ack against the first event (NE-02), a cancel binding
  (NR-12), durability and idempotency (NL-09). G100's `{session_id}` plus `*_done_event` is that pattern;
  it is safe when the done event carries only the session id.

### NF-21 — C-12 addendum
- See NX-05: the layer inversion also covers PM (`runtime_handoff`) and LOADER (`static_binding`), and
  RUNTIME's References section omits all three.

### NF-22 — HC-12 addendum: every disambiguation input the spec names keys on runtime-minted ids
- `create_module_request = {request_key, module}` (RUNTIME l.2009-2012) gives the creator no alias;
  `establish_route_request` narrows only by `provider: module_provider_address` (l.1916), which
  intentionally excludes the instance id (l.2538-2540); the §4.2 routing-selection example is keyed by
  caller and callee module name (l.829-835); the ordering among equivalent providers is undefined (l.1343).
  Deployment inputs MAY fix instance and provider identities for deployment-defined instances (PM
  l.1292-1294; RUNTIME l.2284) and CA scopes can name instances and providers (CA l.152, l.164-165, l.173),
  but none of these can be written before an instance created through Runtime Control exists. Fold into
  HC-12 as a consequence paragraph; the concrete case is a consumer that declares `requires` with
  cardinality `single` on a contract that two instances of one module (serving different networks)
  satisfy.

### NF-23 — HC-04 addendum: relaxing the bare-method-name rule would not enable side-by-side revisions
- The wire resolves a bare `method` under the session's selected contract (TRANSPORT l.855-859; the
  Hello `schema` is the route's contract, l.432-442), but the in-process `logos_<module>_dispatch(context,
  method, params)` (INTERFACE l.1423) carries no namespace or contract root, so any HC-04 remedy needs a
  `_dispatch` ABI change (a namespace-qualified `method` or a contract-root argument). The same-namespace
  rule (COMMITMENT l.360, l.1185) is a naming constraint (revisions are distinct namespaces), and the
  absence of a revision-naming convention is explicit design (INTERFACE l.186-190), not a gap.

### NF-24 — HC-02 addendum
- See NE-01: besides the handler-registration problem HC-02 describes, the fan-out exposes every
  consumer's operation ids, timing and progress values to co-authorized subscribers; content stays private
  only if results are fetched by method, which the specs require but do not spell out.

### NF-25 — DECISIONS notes (G61, RT-03)
- G61's values ("stop drain 10 s; shutdown grace 10 s per realization then force-release; route call 30 s
  then Cancel") have no spec source and the module cannot see them (NL-01); the Cancel never reaches the
  provider (NR-12); "Ctrl-C during start queued until start returns" assumes a blocking `start_module`,
  while l.3120-3125 ("toward ready", "reports the resulting state") admits a `loaded` return. RT-03's
  `logos_orchestrator` is already noted as taking the reserved prefix; RUNTIME l.300-301 additionally
  reserves exact names assigned by a Logos specification, so a later assignment would collide; a
  non-reserved name until the spec assigns one avoids the risk.

---

## Part 4 — Dropped candidates (and why)

Candidates that the refutation pass settled from the text, or that add nothing beyond an existing item.
Listed so the work is not repeated.

- **Cross-subscription event ordering differs by mode.** INTERFACE l.1143 ("Handlers for distinct
  subscriptions MAY run concurrently") denies ordering in every mode; direct-mode ordering is incidental.
  Contracts must use revisions or carry state in the completion event.
- **Subscription count limits and refusal code.** Limits are profile policy (CA l.1165, l.368-369) with a
  defined NOT_AUTHORISED path (CA l.259-260; TRANSPORT l.650-658); the residual (a Runtime-internal refusal
  code) is folded into NR-08.
- **Publish may block in transported mode.** TRANSPORT l.713-720 names both permitted behaviours; the
  unbounded delay and the unassigned choice are NE-05.
- **Facade freshness refresh path.** RUNTIME l.1638-1639 and l.2913-2914 permit consumerless internal
  coordination; a live provider session is itself a freshness source (l.2929-2930). Residue (no role holds
  the remote Runtime Control binding) is minor and not filed.
- **Hung `_destroy` versus the Loader total order (claimed contradiction).** "Incomplete release" is an
  enumerated `realization-failed` outcome (LOADER l.584-585, l.619-620), so graceful release returns and
  `release{force}` is reachable; the wait-budget ownership question is NL-01.
- **Startup ordering as a manifest field.** Deliberate design (RUNTIME l.705, l.708, l.715); a GUI host is
  the deployment and may derive constraints from `requires`.
- **Who resumes retained intent after restart.** Orchestration is named (l.70, l.3230) and divergence is
  documented policy (l.3212-3214); the residue is NL-10.
- **Transferred outputs across provider stop.** Runtime releases them itself (l.1442-1444, l.991-992);
  the consumer never holds the provider's buffer under the ABI rules.
- **Mid-call revocation audit record shape.** Enforcement outcomes have a home in route records and
  route-state events (RUNTIME l.2849-2871); the free-text `failure_code` is EC-10.
- **Permission settings versus the evaluated `permission_scope`.** The CA evaluates the declaration
  (l.1308, l.468-472) and settings compose by containment per definition (l.2240-2241; CA l.106).
- **Platform code-signing attestation in the manifest.** Assigned to platform profiles by design
  (SECURITY l.377-378, l.412, l.514); the signature is in the artifact bytes the manifest hash binds.
- **Install-time downgrade floor.** Package identity is name plus version (PM l.714), `update_package` is
  monotonic (l.1500-1503) and version policy is explicitly profile territory (l.464-471); SECURITY's
  "downgrade" means protocol or isolation downgrade.
- **Approval-surface spoofing.** Explicitly outside the specs (SECURITY l.516; RUNTIME l.3283; BCP l.305);
  binding an approval to a request root is a resolution for HC-03/HC-13.
- **Diagnostic hygiene for ABI and transport messages.** INTERFACE l.2520-2521 has the same shape as the PM
  and Loader rules; structured detail carries a path, not the value. The residue (payload echo in
  implementation diagnostics, no sensitivity marker) is in NC-05.
- **Runtime Control reports expected compare-and-set outcomes on the shared error channel (claimed
  contradiction with INTERFACE §1.4).** INTERFACE's taxonomy treats Runtime-owned conditions as
  invocation failures (l.1470; RUNTIME l.633, l.2258, l.3105, l.3109) and RC uses typed state for retained
  outcomes; the residue is EC-02.
- **`start_module` response boundary.** l.3120 is past tense ("has performed the lifecycle work ... toward
  ready") and l.1655 makes a `loaded` response legitimate; callers must handle it.
- **`describe_provider` on a facade.** Deployment-supplied contract documents (l.492-493, l.512-513) and
  `logos.schema` on the ready route give a surface; low confidence residue.
- **Schema node and depth counting.** "Node" is the COMMITMENT `schema-node` (l.1213-1222); only "parsed
  or canonical" depth wording (INTERFACE l.2874) is loose.
- **Side-by-side interface revisions as an independent blocker.** Folded into NF-23 (HC-04).
- **CM-10 as a contradiction with the opposite default.** Folded into NF-10.
