# Logos Core module specs — open points at `6cac8335`

This is the list of points on the Logos Core module specs (`docs/logos-core/raw/spec-*.md`) at revision
`6cac8335` that still need discussion with the spec owner. It follows two earlier audits,
`claude-spec-comments.md` and `claude-spec-comments-2.md`, which the owner answered item by item. The
responses are appended to those documents, and the remarks on each response are appended after it, in the
same document. This document refers to those remarks, lists the findings that are not in the earlier
audits, and lists in its appendices everything that is settled.

**How it is organised.**

1. Earlier items that were answered and still need discussion. The remarks are in the earlier documents;
   this section lists them.
2. Earlier items that have no response yet. The items are in the earlier documents; this section lists
   them.
3. Findings that are not in the earlier audits, in full.
4. Appendices, for everything that needs no discussion: items resolved by the current text (A), earlier
   items the owner declined (B), the concerns of `human-spec-comments.md` that the current text settles
   (C), and the comparisons behind the findings (D to F).

**Conventions.**
- Short names: RUNTIME, INTERFACE, TRANSPORT, LOADER, CA (Capability Authority), PM (Package Manager),
  CONFIG, COMMITMENT, HASH, cdCDDLe, SECURITY, BCP, CREDENTIAL STORE. `l.N` is a line of the specification
  file at `6cac8335` (`git show 6cac8335:docs/logos-core/raw/<file>` gives the text, whatever revision a
  working tree holds).
- Earlier items keep their identifiers: C-, GN-, CM-, IF-, EC-, TR-, RT-, CA-, PM-, SO- from the first
  audit; NX-, NE-, NI-, NL-, NA-, NR-, ND-, NP-, NC-, NS-, NO-, NF- from the second. HC- items are the
  concerns of `human-spec-comments.md`. The findings of this document are TF- (spec text), TL- (the system
  contracts against their own rules), TS- (the integrator documents) and TP- (porting the module catalog).
  Their numbers are not consecutive: a TF-, TL-, TS- or TP- identifier that section 3 does not list is
  settled by the current text and has its row in Appendix A.
- Needs that come from existing modules are stated with neutral roles (consumer C, provider P, host
  application H, and so on). The shape of the need is what matters to the specification.
- Every statement about the specs was checked against the lines it cites, and every quotation is exact.
- CREDENTIAL STORE was read once for consistency with the other specifications. It has not had the
  line-by-line check that the others had.

## Summary

| Section | Content | Items |
|---|---|---|
| 1 | Earlier items answered, still needing discussion | 1 |
| 2.1 | Items of the second audit with no response | 4 |
| 2.2 | Concerns of `human-spec-comments.md` that still need an answer | 2 |
| 3.1 | Contradictions and gaps in the spec text | 38 |
| 3.2 | The system contracts against their own rules | 4 |
| 3.3 | The integrator documents against the specs | 8 |
| 3.4 | Porting the existing module catalog | 7 |
| 3.5 | Editorial | 1 list |
| Appendix A | Items resolved by the current specs | 154 earlier items, 29 findings of this document |
| Appendix B | Earlier items the owner declined | 60 |
| Appendix C | Concerns of `human-spec-comments.md` settled by the current specs | 11 |
| Appendices D to F | Comparisons behind sections 3.2 to 3.4 | 35 claims, 20 needs, one list |

**What most needs an answer.**

From the earlier items (sections 1 and 2):
- NE-07: a consumer learns that an optional provider has appeared only through observation authority keyed
  by module name, or by polling.
- NL-12: Core knows only runtime-ready; there is no common surface for application readiness or health.
- HC-07: a provider must export three surfaces that have to agree, and no rule derives one from another.

From the findings (section 3):
- TF-53: CREDENTIAL STORE requires its provider to answer `NOT_AUTHORISED`, and INTERFACE turns that code
  into `MODULE_ERROR` when provider code returns it.
- TF-54: the module state table forbids every transition it does not list, and no trigger in it names a
  stop that enforcement causes.
- TF-55: whether one contract extends another depends on `_module`, which the schema root does not commit,
  so the provider that claims the extension can always satisfy the condition.
- TF-56: a package provides a contract by its manifest, while the variant installed on a host may lack the
  module that provides it.
- TF-09: an allow to invoke `establish_route` counts as observation authority, so the non-disclosure rule
  for routes does not bind an ordinary consumer.
- TF-37: who may invoke the Module Loader's `realize`, `release` and `apply_configuration` is not stated.
- TF-43: what a complete Logos module system must contain, and which deployments BCP §5.1 and §5.4 bind,
  is not stated.
- TF-44: *package-backed* is not defined, and when the Package Manager handoff is obtained again is not
  stated.
- TF-48: the erasure of a marked payload cannot be met when an execution envelope is ended by force.
- TF-52: for a remote route, whether the Runtime-controlled boundary stays on the path of every payload of
  a hosted consumer or provider is not stated.
- TS-05: trust in a publisher is prohibited; every package name needs its own entry in protected trust
  input, which no specified operation edits.

---

## 1. Earlier items that were answered and still need discussion

One item of the first audit has a response and still has an open point. It is written up next to the
response, in the section "Remarks on the response" at the end of `claude-spec-comments.md`. Every other
remark made there, and every remark made in `claude-spec-comments-2.md`, is settled by the current text;
Appendices A and B have their rows.

| Item | What still needs discussion | Remark in |
|---|---|---|
| PM-11 | Only the Package Manager returns host paths (`installed_artifact.local_path`, PM l.1155-1160), and no text says that this is intended. | `claude-spec-comments.md` |

---

## 2. Earlier items that have no response yet

### 2.1 Items of the second audit

Thirteen items of the second audit have no reply. The current text settles nine of them without one (ND-10
to ND-14, NP-11 to NP-13 and NP-15; see Appendix A). The other four are restated against the current text
in `claude-spec-comments-2.md`, under "Items without a response, restated against the current
specifications".

| Item | Subject |
|---|---|
| NE-07 | A consumer learns that an optional provider has appeared only through Runtime Control observation authority keyed by module name |
| NL-12 | Core knows only runtime-ready: no common application-readiness or health surface, and ordering constraints cannot wait for one |
| NA-12 | A provider picked by a person: a requester that does not ask the chooser cannot be steered, and the chosen application cannot be brought forward |
| NP-14 | A module cannot declare that it needs one instance per Runtime |

### 2.2 The concerns of `human-spec-comments.md`

The thirteen concerns HC-01 to HC-13 have no reply either. The current specs settle eleven of them (see
Appendix C). The two below still need an answer. Where each stands against the current text is written up
at the end of `human-spec-comments.md`, under "Status against the current specifications".

| Item | What still needs an answer |
|---|---|
| HC-02 | A pattern for a provider to call a handler that a consumer registered with it. The reply to NF-24 leaves it open. |
| HC-07 | Whether one provider surface can be normative and the others derived by the Runtime or a required generator. Equivalence of the three surfaces remains a per-module obligation. |

---

## 3. New findings

None of the items in this section is an item of the earlier audits. TF-20 takes up a point that the second
audit considered and set aside. Where an item touches an earlier one, the earlier item is named under
**Overlap** or **See**; its outcome is in section 1 or 2 or in the appendices.

### 3.1 Contradictions and gaps in the spec text

These items are places where two passages of the specs cannot both be followed, or where a rule that
other rules depend on is not stated.

#### TF-03 — Work that a module leaves behind in a directly loaded library after `_MODULE_destroy` is not covered; the lifetime of a diagnostic is keyed on the calling thread
- **Specs:** INTERFACE §2.8 l.1957-1958 ("the module MUST stop or join internal work that could later use
  the context, Runtime Control binding, publish callback, or publish state"), l.2100 ("to stop or join
  residual internal work"), §2.7 l.1786 and l.1793-1794 (diagnostic storage valid "until the next ABI call
  into the implementation that returned the result begins on the calling thread", or "until the applicable
  implementation binding is released"); RUNTIME l.370-371 ("MUST NOT unmap the code of a direct dynamic
  binding while its hosting process continues to run"; "A later realization of the same accepted artifact
  in that process MAY reuse the loaded code with a new module context"), l.3661 ("Accepted recovery uses a
  new realization, including a new native context"); LOADER l.473. For asynchronous completion: INTERFACE
  l.2050, l.2090 (diagnostics are owned, not thread-keyed).
- **Issue:** (1) A direct-dynamic library stays mapped while its hosting process runs, and a later
  realization of the same accepted artifact may reuse the loaded code (RUNTIME l.370-371). The module's
  duty at `_MODULE_destroy` covers only work that touches the context or the Runtime bindings (INTERFACE
  l.1957-1958). A library that keeps other threads or process-wide registrations (a Go runtime; a Rust
  async executor or thread-local destructors; Nim or C++ worker threads, `atexit` handlers, signal
  handlers) leaves that state behind, where the next realization of the same module (stop/start, recovery,
  upgrade) meets it. Hosted placements are not affected, because the process exits. (2) The diagnostic
  lifetime of every synchronous result is defined by "the calling thread" (INTERFACE l.1786): the storage
  is valid until the next ABI call into that implementation begins on that thread. A caller therefore has
  to copy the diagnostic before its thread can run anything else. A language runtime that can move its
  caller to another OS thread without a suspension point in the source, as a Go runtime can unless the
  goroutine is locked to its thread, lets the next statement run elsewhere while another task makes the
  next call on the first thread. With async Rust, Kotlin coroutines and Swift concurrency the caller stays
  on its thread until it suspends, so the copy has to come before the first suspension. Nothing tells the
  author of a binding so. The asynchronous completion path does not have the problem: its diagnostics are
  transferred with an owner.
- **Impact:** a later realization of an in-process module written in the documented SDK languages meets
  the threads and registrations that the preceding one left behind, on stop/start, recovery and upgrade; a
  language binding that reads a diagnostic after its caller has left the calling thread can read
  overwritten storage.
- **Overlap:** NL-01, NL-03 (stop budget, `_MODULE_destroy` cannot report failure), IF-09 (symbol
  collisions across modules).
- **Suggested resolution:** extend the `_MODULE_destroy` duty to every thread and process-wide
  registration the module created, or name the exceptions. In INTERFACE §2.7, add that a binding MUST copy
  `message` and `detail` before its caller can leave the calling thread.

#### TF-07 — Whether an install or update that changes nothing succeeds while the retained signer is not accepted is not said
- **Specs:** PM l.1685-1686 ("Installing an already-installed package identity with the same manifest
  commitment succeeds with the current installed record and creates no duplicate"; the retained signer is
  replaced "When that request's package signature validates under a currently accepted signer whose
  `package_signer` differs from the retained one"), l.1706 ("If no applicable newer version exists, the
  operation succeeds with the current installed record and changes nothing"), l.436-437 ("After an anchor
  is removed or revoked, Package Manager MUST NOT use it for a new successful resolution, installation,
  update, or Runtime handoff"), l.411 ("Retained verification provenance MUST NOT substitute for current
  trust"), l.540-542 (the `package_signer` record is derived "from the verification that accepted the
  adjacent manifest commitment" and retained with installed state; "A Runtime handoff MUST report the
  signer retained with its selected installed record"), l.424-428 (a package whose signature no accepted
  anchor validates is rejected with `signature-verification-failed`).
- **Issue:** `install_package` for an installed identity with the same manifest commitment "succeeds with
  the current installed record" (PM l.1685), and `update_package` with no newer version "succeeds with the
  current installed record and changes nothing" (PM l.1706). An install whose signature validates under a
  currently accepted signer replaces the retained signer (PM l.1686). The open case is a call made while
  the signer retained with the record is not accepted and the request brings no signature by an accepted
  signer: an install whose source carries only a signature by that signer, or an update that finds no
  newer version. PM l.437 forbids the use of a withdrawn anchor "for a new successful resolution,
  installation, update, or Runtime handoff", and PM l.411 says that retained provenance does not stand in
  for current trust. Whether such a call succeeds, because it installs nothing, or fails, because its
  success rests on a signer that is not accepted, is not said. The caller sees the difference.
- **Impact:** the same call succeeds on one Package Manager and fails on another.
- **Overlap:** NP-10 (continuity of trust input), TS-05.
- **Suggested resolution:** say which outcome an `install_package` or `update_package` call that changes
  nothing has while the signer retained with the installed record is not accepted.

#### TF-09 — Whether authority to invoke `establish_route` is observation authority is not stated
- **Specs:** RUNTIME l.1542-1543 ("Runtime Control observation authority over a record is authority under
  active policy to observe that record through the requested method or event"; "When policy is
  externalized through LOGOS-MODULE-CAPABILITY-AUTHORITY, it is an allow decision for that method or event
  with a `runtime_control_scope` whose present constraints match the record"), l.3060-3063 ("A caller
  without matching provider-discovery or Runtime Control observation authority MUST NOT be able to
  distinguish an unknown target from an existing but hidden or denied target"; "For a caller with that
  authority, a failed establishment caused by denial of route authority for a selected provider MUST
  report `NOT_AUTHORISED`"; "If establishment instead fails because no matching provider is available or
  ready, Runtime MUST report `NOT_READY`"); CA l.182-192 (the selectors of `runtime_control_scope` are
  optional), l.301 ("Every present constraint MUST match the attempted operation or returned
  observation").
- **Issue:** observation authority is defined by the requested method. For route establishment that method
  is `establish_route`, which a consumer must be allowed to invoke before it can establish any route.
  Under an externalized policy the definition asks only that the present constraints of the scope match
  the record, and a scope with no selector has none. Such a consumer holds observation authority over
  every provider record, so the rule of l.3060 never applies to it. It receives `NOT_AUTHORISED` for a
  provider it is denied and `NOT_READY` for one that does not exist or is not ready, and so learns which
  providers exist.
- **Impact:** the non-disclosure rule protects nothing against a consumer whose scope for
  `establish_route` carries no selector, which is the ordinary case. One Runtime applies l.3060 to such a
  consumer and another applies l.3062-3063.
- **Overlap:** TF-16 (the code when the caller holds only a route allow).
- **Suggested resolution:** state at l.3060 that authority to invoke `establish_route` or `renew_route` is
  not observation authority over the providers the request may select, or name the `discover` decision as
  the only authority that lifts the rule.

#### TF-10 — What `start_module` answers when a prerequisite is not ready, and the record of an instance whose start an unavailable system service prevents, are not stated
- **Specs:** RUNTIME l.709 ("every prerequisite module instance MUST be ready before Runtime initializes
  the dependent module instance"), l.3642 ("An unavailable prerequisite MUST prevent dependent startup or
  operations that require it"), l.3512-3514 (acceptance establishes `requested` intent "before execution
  authorization or startup", and "A subsequent startup denial or failure MUST NOT cancel that intent or
  change its origin"), l.3613 (an `unloaded` instance with retained `requested` intent "MUST include
  `failure`" when one of the listed causes prevents that intent from executing, among them "a prerequisite
  instance that is not ready and has no execution attempt in progress"), l.3605 (the classifications,
  among them `prerequisite-unavailable`), l.3618 ("An observation with no current failure or
  failure-caused unavailability, including a ready local instance, MUST omit `failure`"), l.3678-3679
  ("While a required system service is unavailable, Runtime MUST fail every operation that requires it"),
  l.1809-1811 (the precondition table gives `NOT_READY` when "A required non-authority system service is
  unavailable and prevents the operation from completing"), l.1832 (the order of checks places
  "Runtime-owned readiness not covered by such a table" after that table and names no code); CONFIG l.125
  ("Missing eligible configuration MUST prevent initialization and produce `NOT_READY` for an otherwise
  authorized startup attempt").
- **Issue:** two points about a start that cannot proceed are open.
  1. An unready prerequisite. The dependent stays `unloaded` with intent `requested`, and its record
     carries `prerequisite-unavailable` while the prerequisite "is not ready and has no execution attempt
     in progress" (l.3613). What `start_module` answers for the dependent is not said. A start without
     configuration has its code (CONFIG l.125). An unready prerequisite is not a row of the precondition
     table (l.1809-1811), and the order of checks names no code for it (l.1832).
  2. An unavailable system service. A start that needs a system service which is unavailable fails
     (l.3678-3679), with `NOT_READY` when the service is not the authority (l.1811). The causes for which
     an `unloaded` instance with retained intent carries a `failure` are listed in l.3613, and an
     unavailable system service is not among them; no classification names it (l.3605). Whether such a
     service counts as a prerequisite, and whether the record carries a `failure`, is not said.

  Each outcome is observable through the answer to the request, the module record, the readiness result
  and the state events.
- **Impact:** two Runtimes answer the same `start_module` differently, and an orchestrator or a
  presentation module cannot tell an instance that waits for a system service from one that is not
  started.
- **Reading an implementation needs today:** answer `NOT_READY` for a start whose prerequisite is not
  ready, and keep the intent. For a start that an unavailable system service prevents, keep the instance
  `unloaded` with the intent kept, and report `prerequisite-unavailable`; or omit `failure`.
- **Overlap:** NL-07, TL-07.
- **Suggested resolution:** give the code of `start_module` for a start whose prerequisite is not ready,
  and say whether an unavailable system service is one of the causes of l.3613 and which classification it
  uses.

#### TF-16 — `establish_route` has no assigned code when the provider is allowed but not ready and the caller holds only a route allow
- **Specs:** RUNTIME l.3048-3049 ("every returned route MUST be independently authorized and ready"; "If
  neither a route nor a continuation can be returned, establishment fails"), l.3060-3063 ("A caller
  without matching provider-discovery or Runtime Control observation authority MUST NOT be able to
  distinguish an unknown target from an existing but hidden or denied target. Runtime MUST report
  `NOT_AUTHORISED` with a non-revealing diagnostic for those cases"; "For a caller with that authority, a
  failed establishment caused by denial of route authority for a selected provider MUST report
  `NOT_AUTHORISED`. If establishment instead fails because no matching provider is available or ready,
  Runtime MUST report `NOT_READY`"), l.1423 ("A `single` request does not enumerate candidates and does
  not require a separate `discover` decision"), l.624 ("Runtime MUST use `NOT_READY` only when
  Runtime-owned lifecycle, provider, or route readiness prevents a valid contract response"), l.1426 ("The
  provider identity in a successful route record is disclosure necessary to that authorized route").
- **Issue:** a denied or unknown target has a code, and so has a failed establishment for a caller with
  discovery or observation authority. One way of returning nothing has none. The selected provider exists,
  the consumer is authorized to route to it and holds neither discovery nor observation authority, and the
  provider is not ready (stopped, starting or failed). A `single` request is made this way, since it needs
  no `discover` decision (l.1423). `NOT_READY` is given "For a caller with that authority" (l.3062-3063),
  and the `NOT_AUTHORISED` of l.3061 is for a target that is unknown, hidden or denied, which this
  provider is not. `NOT_READY` fits l.624, but reporting readiness discloses that the provider exists, and
  l.1426 covers only "a successful route record". Whether a route allow, without discovery or observation
  authority, makes the provider's existence and state disclosable is not said. If it does not, the answer
  has to be `NOT_AUTHORISED`.
- **Impact:** a consumer cannot tell "wait and retry" from "ask for authority", and two Runtimes answer
  the same request with different codes.
- **Reading an implementation needs today:** `NOT_READY` when the caller holds a route allow for that
  provider, and `NOT_AUTHORISED` otherwise.
- **Overlap:** NE-07 (an absent provider cannot be told from a denied one), EC-01 to EC-04, TL-03.
- **Suggested resolution:** say at RUNTIME l.3060-3063 whether a route allow for the selected provider
  makes its readiness disclosable to the requesting consumer, and so which code that consumer gets.

#### TF-18 — The order of checks is not stated for `materialize_route`, and a materialization that meets the end of its route has two codes
- **Specs:** RUNTIME l.1824-1833 ("When more than one failure or error applies to a Runtime Control
  invocation or an ordinary provider call, Runtime MUST report the first that applies in this order"; the
  last two of its eight steps are "Runtime-owned readiness not covered by such a table" and "comparison of
  an expected contract or schema root not covered by such a table"), l.723 ("Route materialization is a
  process-local binding operation rather than a Runtime Control contract method"); INTERFACE l.3920-3921
  (for `materialize_route`: "After the ownership and non-disclosure checks, a successfully reconstructed
  schema root that differs from `expected_contract_root`, or a recorded route contract root that differs
  from it, MUST produce `VERSION_MISMATCH`"; "Route readiness and authorization failures MUST follow
  LOGOS-MODULE-RUNTIME Section 7.5"); RUNTIME l.746 and l.1262 (quoted in point 2).
- **Issue:** the order of checks is fixed for a Runtime Control invocation and for an ordinary provider
  call (RUNTIME l.1824-1833), and for the rows of the two CONFIG tables (CONFIG l.202-203, l.305). For
  `materialize_route`, ownership comes before the root comparison. Two orders are not fixed.
  1. `materialize_route` for an owned route that is not ready, with a root that does not match: the
     readiness code or `VERSION_MISMATCH`. The order of RUNTIME l.1824-1833 puts readiness before the
     comparison of a root, and it is stated for "a Runtime Control invocation or an ordinary provider
     call". Materialization is not a Runtime Control contract method (l.723), and INTERFACE l.3920-3921
     does not refer to that order.
  2. A materialization that meets the end of its route. The Hello is refused because the ticket was
     revoked, and "a well-formed ProtocolError received during Hello MUST cause materialization to fail
     with that shared error code" (l.746), here `NOT_AUTHORISED`. If the route ended by a closure, a new
     operation gets `NOT_READY`: "explicit route closure or loss of Runtime-owned provider or route
     readiness MUST produce `NOT_READY`" (l.1262). Two rules give two codes for one event.
- **Impact:** neither discloses anything about a hidden target. But two Runtimes answer the same request
  with different codes, a consumer handles `NOT_AUTHORISED`, `VERSION_MISMATCH` and `NOT_READY`
  differently, and a conformance test cannot assert either answer.
- **Reading an implementation needs today:** apply the order of RUNTIME l.1824-1833 to
  `materialize_route`, so that readiness is checked before roots are compared. For a materialization that
  meets the end of its route, return the cause of that end when the binding already holds one, and
  otherwise the code the peer sent.
- **Overlap:** EC-05 and EC-06 (the codes themselves), EC-01 to EC-04.
- **Suggested resolution:** say that the order of RUNTIME §9.3.1 applies to `materialize_route`, and give
  the code of a materialization that meets the end of its route.

#### TF-20 — When `start_module` answers is not stated
- **Specs:** RUNTIME l.3517 ("success means Runtime has performed the lifecycle work needed to move the
  selected module instance toward `ready`, including native artifact loading and lifecycle initialization
  where applicable"), l.3521 ("The response reports the resulting local runtime lifecycle state"),
  l.3554-3555 (for `stop_module`, by contrast: "success means Runtime has accepted the stop and the
  selected module instance is `stopping` or `unloaded`"; "The response MUST NOT wait for draining,
  lifecycle destruction, or realization cleanup").
- **Issue:** "toward" leaves the point of the answer open. `start_module` may answer at `loaded` or at
  `ready`. The reported state and the time the caller is blocked both differ. `stop_module` says when it
  answers (l.3554-3555); `start_module` does not.
- **Impact:** orchestration written against a Runtime that answers `start_module` at `ready` misbehaves on
  one that answers at `loaded`.
- **Reading an implementation needs today:** either point, documented.
- **Overlap:** NL-06 (leaving `error`), TL-07 (the module states), TF-10.
- **Suggested resolution:** state the state at which the `start_module` response is sent, or that both are
  permitted and the returned state tells which.

#### TF-22 — Whether the handler of a Runtime Control subscription may run on a subscriber's thread that is inside another operation of the binding is not stated
- **Specs:** RUNTIME l.1107-1109 ("Runtime Control events delivered through a local Runtime Control
  binding have no publishing thread, and Runtime schedules their handler invocations in committed order
  for each subscription"; "Runtime MUST NOT invoke such a handler on a thread executing the Runtime
  Control operation that committed the change"); INTERFACE l.1467 ("The callback MAY run on the thread
  that detects termination, including during another binding operation").
- **Issue:** the text excludes one thread, the one that runs the operation which committed the change. It
  says nothing of a thread of subscriber S that is inside another operation of the same binding, such as a
  listing call. For the terminal callback the permission is stated (INTERFACE l.1467). For an event
  handler it is neither granted nor excluded.
- **Impact:** S cannot tell whether a lock it holds across a Runtime Control call can be taken again by
  its own handler on the same thread. A handler written for one Runtime deadlocks on another.
- **Suggested resolution:** state in RUNTIME §6.3 whether Runtime may invoke the handler on a thread that
  is executing another operation of that binding.

#### TF-25 — What orchestration does to establish the first authority binding, and how it learns that the binding exists, is not stated
- **Specs:** RUNTIME §9 l.1555-1556 ("When authority policy is externalized, bootstrap policy MUST
  identify the orchestration instance and the operations and targets it may use to establish the selected
  initial Capability Authority"; "Orchestration MUST establish that binding before starting the remaining
  deployment under active authority policy"), l.1561-1566 (the checks Runtime makes before it uses a
  provider as a system service, among them that "the module instance is ready under its selected execution
  mode"), l.1591 ("If an external Capability Authority is unavailable, Runtime MUST deny operations that
  depend on it"), l.2483 (for `get_self`, Runtime "MUST NOT require a separate policy grant or
  availability of Capability Authority for this method"); §13.2 l.3838-3839 ("Startup completes when every
  system-service binding established from protected input has passed the checks of Section 9 and the
  initial orchestration instance is `ready`"; "A system-service binding that orchestration establishes
  under Section 9 after it becomes `ready` is not part of startup").
- **Issue:** with an externalized authority the first authority binding is established by orchestration
  (l.1556), after `logos_runtime_start` has returned (l.3839). Two things about that step are not stated.
  1. What orchestration does. Bootstrap policy names "the operations and targets it may use" (l.1555), and
     no Runtime Control method binds a system service. What orchestration does to establish the binding,
     beyond starting the selected instance, is not said.
  2. How orchestration learns that the binding exists. Runtime makes it after its own checks
     (l.1561-1566), and no record, event or method reports it. `get_self` proves nothing, because Runtime
     "MUST NOT require a separate policy grant or availability of Capability Authority for this method"
     (l.2483). Orchestration must wait for the binding "before starting the remaining deployment"
     (l.1556), and has only the outcome of a policy-decided call to go by.
- **Impact:** orchestration is the module that drives the deployment, and under an externalized authority
  it cannot tell from any record whether anything can be authorized yet. One orchestration module starts
  the remaining deployment while the operations that depend on the authority are denied (l.1591); another
  waits by repeating a policy-decided call.
- **Reading an implementation needs today:** orchestration starts the selected authority instance, and
  Runtime binds it when the checks of l.1561-1566 pass. Until the binding exists the operations that
  depend on it are denied (l.1591). Orchestration takes the first policy-decided call that succeeds as the
  sign that the authority is bound.
- **Overlap:** TF-20 (when `start_module` answers), NA-11 (bootstrap policy once an authority is bound).
- **Suggested resolution:** state in RUNTIME §9 what orchestration does to establish the first authority
  binding of l.1556, and say how orchestration learns that the binding exists.

#### TF-27 — Whether a Runtime that signs call evidence must keep its identity is not stated
- **Specs:** RUNTIME §9.3 l.2586-2587 ("A runtime instance id MAY be host-assigned or runtime-generated";
  "Runtime generates the id only when the host's protected configuration permits generation"), l.2594 (for
  the remote profiles, "The runtime host or authorized provisioning system generates it once and preserves
  it for the lifetime of that logical Runtime identity"), l.2597 ("Assigning a new Runtime identity
  requires a new enrollment"); CA §9.1 l.1309 ("Protected trust input MUST map each accepted `kid` to
  exactly one producer Runtime identity and one exact 48-byte `SLH-DSA-SHA2-192s` public key"), l.1326
  ("Rotation installs a new key under a new `kid` before the producer begins using it"), l.1328-1329
  ("Evidence under an unknown or revoked `kid` MUST be rejected"; "In this baseline, revocation
  invalidates all evidence under that key"), l.1334 ("The `producer` MUST equal the Runtime identity
  authorized for the selected `kid`"); SECURITY l.366 ("The signing key has a distinct evidence-signing
  purpose and is bound through protected trust input to the producer Runtime identity").
- **Issue:** for the remote profiles the id is generated once and preserved (RUNTIME l.2594), and a new
  identity needs a new enrollment (RUNTIME l.2597). For a Runtime that uses local transport only, no rule
  says that the id survives a restart. Call evidence presumes that it does. The trust input of a verifier
  maps each accepted `kid` to "exactly one producer Runtime identity" (CA l.1309), and the `producer` of
  each record must equal it (CA l.1334). A Runtime that takes a fresh id at each start and signs under one
  key produces, after its first restart, records whose producer no trust input names. Rotation is defined
  for the key (CA l.1326) and not for the identity: whether a Runtime whose identity changes must take a
  new key and `kid`, and what becomes of evidence signed under the old pairing, is not said. CA
  l.1328-1329 provide only for an unknown or a revoked `kid`.
- **Impact:** an implementation that keeps its id only while it runs cannot have its call evidence
  verified after a restart. One that keeps the `kid` across a change of identity leaves a verifier with
  two producers under one `kid`, which CA l.1309 excludes.
- **Reading an implementation needs today:** a Runtime that signs call evidence keeps one identity for as
  long as its key is in use: the host assigns the id and keeps it with the key, and a new identity takes a
  new key and `kid`.
- **Overlap:** SO-03 (declined).
- **Suggested resolution:** say in RUNTIME §9.3 that a Runtime which produces call evidence preserves its
  identity, as l.2594 requires for the remote profiles, and in CA §9.1 that a change of the producer's
  identity requires a new `kid`.

#### TF-29 — How a Runtime behind a Loader learns the cause of a failed realization is not stated
- **Specs:** RUNTIME §9.3 l.3604-3607 ("A known cause MUST use its defined classification"; the
  classifications include `initialization-failed` and `host-terminated`; "`host-terminated` means that the
  realization's execution envelope, or the Runtime process containing it, ended without cleanup ordered by
  Runtime"; "When the cause is a typed error returned by a bound Module Loader provider and no more
  specific Runtime classification applies, the classification MUST be `loader-` followed by that error's
  defined code"), §8.1 l.1488 ("Runtime MUST treat the reported rejection or a module's ABI-version or
  structure-size rejection as an initialization failure"); LOADER l.496-498 ("Unexpected Module Host
  termination, loss of a required direct binding, or an indeterminate live-configuration outcome changes
  an active realization to failed"), l.102 ("Module Loader reports operational realization status to
  Runtime"), l.622-624 ("`realization-failed` covers initialization, Module Host creation, state delivery,
  endpoint handoff or activation, indeterminate configuration, unexpected realization failure, and
  incomplete release").
- **Issue:** a realization can be lost while the Runtime keeps running, when its Module Host ends
  unexpectedly (LOADER l.496-498). The Loader reports that as status (LOADER l.102), under one code that
  covers several causes (LOADER l.622-624). For Runtime that end is `host-terminated` (RUNTIME l.3606),
  and a known cause must use its defined classification (RUNTIME l.3604). A cause that reaches Runtime
  only as the Loader's typed error is classified `loader-realization-failed` (RUNTIME l.3607). Which of
  the two the instance reports depends on whether the Runtime's own supervision saw the end or only the
  Loader's record shows it, and how the Runtime learns the cause is not said. The same folding hides a
  second cause that the list names. A failed `_MODULE_init` is an initialization failure for Runtime
  (RUNTIME l.1488). Behind a Loader it arrives as `realization-failed`, so `initialization-failed` cannot
  be reported unless the cause travels beside the contract.
- **Impact:** for the same end of a Module Host one Runtime reports `host-terminated` and another
  `loader-realization-failed`, and for the same failed initialization one reports `initialization-failed`
  and another `loader-realization-failed`. The `failure` in the state event, the readiness result and the
  execution summary differ.
- **Reading an implementation needs today:** for a Module Host that ends while the Runtime runs, report
  `host-terminated` when the Runtime's own supervision saw the end, and the `loader-` classification when
  only the Loader's failed record is known. Report a failed initialization as `initialization-failed`
  wherever the implementation can know that cause.
- **Overlap:** TF-36 (which realization mechanism may report a `loader-` classification).
- **Suggested resolution:** say how a Runtime behind a Loader learns the cause of a failed realization,
  since `realization-failed` covers initialization and an unexpected end of the Module Host as well.

#### TF-33 — Whether a live session of a route ends when the route is re-authorized after a policy change is not stated
- **Specs:** CA l.920 ("On `policy_changed`, Runtime MUST invalidate every cached decision from that
  Capability Authority"), l.937-939 ("Runtime re-evaluates a dependent route by requesting a decision for
  the route's bound scope as for renewal, without a consumer request"; "An allow decision covering the
  bound scope keeps the route, replaces its `decision_id`, and sets `expires_at` to the earlier of its
  current value and the new validity end"), l.944 ("It MUST terminate dependent provider sessions and
  subscriptions when their continued use would exceed current authority"); TRANSPORT l.913-914 ("Route
  renewal does not by itself replace the authorization decision or expiry of an existing provider
  session"; "The session MUST end when its bound decision expires or is revoked"); RUNTIME l.3337-3338
  ("Renewal does not by itself change the decision or deadline bound to an existing provider session";
  "That session remains subject to its previous decision and expiry").
- **Issue:** after a policy change Runtime re-evaluates an established route as for renewal (CA l.937),
  and an allow that covers the bound scope keeps the route and replaces its `decision_id` (CA l.939). What
  that does to a live session of the route is not stated. On a transported route "The session MUST end
  when its bound decision expires or is revoked" (TRANSPORT l.914), and "Renewal does not by itself change
  the decision or deadline bound to an existing provider session" (RUNTIME l.3337). After a
  re-authorization that allows, the notification has invalidated the session's own decision (CA l.920),
  and no deny has revoked it. Whether the session ends, as for a revoked decision, or goes on because its
  use does not "exceed current authority" (CA l.944), is not said.
- **Impact:** after the same policy change a live session ends on one Runtime and continues on another,
  although both keep the route. On the first the consumer needs a replacement session before its next
  call.
- **Reading an implementation needs today:** after an allow, keep a live session of the route; each call
  on it is decided on its own.
- **Overlap:** NA-07 (event deliveries after a policy change; answered).
- **Suggested resolution:** say beside CA l.937-941 whether a session bound to the earlier decision ends
  when the re-authorization allows.

#### TF-37 — Who may invoke the Module Loader's `realize`, `release` and `apply_configuration` is not stated
- **Specs:** RUNTIME l.157-159 ("Every system service provider MUST be a local module provider backed by a
  local module instance"; "Ordinary module consumers access them through consumer-bound routes; the
  Runtime engine uses the protected system-service bindings defined in Section 9"); LOADER l.80 ("The
  engine admits lifecycle requests and invokes the bound Module Loader provider for realization, status
  and release"), l.103-104 (the Loader "MUST NOT directly create or mutate Runtime-owned module
  identity,"), l.425-427 ("Runtime MUST obtain authorization for module execution and every required
  permission before invoking `realize`"; "Module Loader MUST accept security and deployment constraints
  only from a boundary trusted by the selected profile"); CA l.339-341 (outside bootstrap, an allow
  decision comes "before asking Module Loader to realize a direct native implementation"), l.350-354
  ("Authorization to call the Module Loader provider does not authorize an arbitrary module execution
  operation"; "An ordinary module caller requires its own provider-access decision"; "Neither invocation
  authority substitutes for the required execution and permission decision").
- **Issue:** the Loader is a module provider, so policy can grant an ordinary module a route to it
  (RUNTIME l.159; CA l.353). Its contract is written for one caller, the engine (LOADER l.80, l.426). For
  an ordinary caller three things are not stated.
  1. Which methods it may invoke. Nothing separates `list_capabilities` and `get_status` from `realize`,
     `release` and `apply_configuration`.
  2. Who obtains the execution decision. The decision is required of Runtime before it invokes `realize`
     (CA l.340; LOADER l.426). An ordinary caller is not Runtime, and its provider-access decision is
     expressly not that decision (CA l.354).
  3. What such a realization belongs to. Runtime owns module identity, lifecycle and readiness (LOADER
     l.103-104). A realization that the engine did not request has no lifecycle record behind it, and the
     Loader may take constraints only from a trusted boundary (LOADER l.427).
- **Impact:** one Runtime lets policy grant the route and then holds realizations outside its lifecycle
  records. Another refuses every such route, which no text says it may. The same policy gives a module
  different powers on the two.
- **Reading an implementation needs today:** refuse to establish a route from an ordinary module to the
  Loader's contract, whatever policy allows, and have the Loader accept the three mutating methods only
  from the engine's system-service binding.
- **Overlap:** C-10 (the request has no field for the endpoint or for private handoffs), RT-05, TF-36.
- **Suggested resolution:** state in LOADER §13 which methods an ordinary consumer may invoke. If a
  mutating method is among them, say who obtains the execution decision and how Runtime learns of the
  realization.

#### TF-38 — A consumer in a Module Host and a provider realized directly: whether the route exists, and how its endpoint is served, is not stated
- **Specs:** RUNTIME l.159, l.163 ("A system service provider MAY use direct mode or local transport mode
  according to active policy and the applicable profile"), §9.3 l.1963 (a module record has one `mode`),
  l.2915-2916 ("Runtime Control MUST NOT return an invocation descriptor for a direct-mode route"; "and an
  out-of-process caller requires a local or remote transport route"), l.3063 ("If establishment instead
  fails because no matching provider is available or ready, Runtime MUST report `NOT_READY`"); LOADER
  l.191-192 ("Module Loader MUST NOT create or return a Transport endpoint for a direct realization";
  "Runtime MAY expose the directly realized provider through a separate Transport invocation boundary");
  TRANSPORT §8.2 l.1103-1106 (Runtime binds the socket "before transferring its open descriptor through
  the selected realization mechanism"; "The Module Host MUST serve only that transferred listener and MUST
  NOT bind or substitute another endpoint"; "Runtime MUST validate the exact transferred listener and its
  directory, path type, symbolic-link absence, ownership, and listening state").
- **Issue:** when the consumer runs in a Module Host and the provider is realized directly in the
  Runtime's process, the route must be transported (RUNTIME l.2916). The only endpoint a direct provider
  can have is one that Runtime chooses to expose (LOADER l.192, a MAY). Three things are not stated.
  1. Whether Runtime must offer that endpoint. If it may refuse the route, the nearest rule is RUNTIME
     l.3063, which gives `NOT_READY` when no matching provider is available or ready, and whether a ready
     provider that Runtime does not expose counts as not available is not said. System services are
     commonly direct (RUNTIME l.163), and a hosted module reaches them only by such a route (RUNTIME
     l.159), so a refusal cuts every hosted module off from every system-service contract.
  2. How TRANSPORT §8.2 applies. Its rules are written for a listener that Runtime creates and transfers
     to a Module Host (TRANSPORT l.1103-1106). When Runtime serves the listener itself, nothing is
     transferred, and which of those rules still bind is not said.
  3. What the provider's record shows. It has one `mode` (RUNTIME l.1963), and the provider is then direct
     for callers in its process and transported for the others.
- **Impact:** a module that works when it is realized directly loses its routes to direct providers when
  the deployment moves it into a Module Host on one Runtime, and keeps them on another. Nothing in the
  route record tells the consumer which it has.
- **Reading an implementation needs today:** Runtime serves a listener of its own for the direct provider,
  under every rule of §8.2 that does not concern the transfer, and the provider's record stays `direct`.
- **Overlap:** TF-16 (a route that cannot be returned has no code), TS-04.
- **Suggested resolution:** say in RUNTIME §4.2.1 whether Runtime must expose a direct provider to
  out-of-process consumers. If it may refuse, say whether l.3063 gives the code. State how §8.2 applies to
  a listener that Runtime serves itself.

#### TF-39 — What the execution envelope of a hosted placement contains, when its end is confirmed after a Runtime restart, is not stated
- **Specs:** RUNTIME l.578 ("Runtime MUST reject `start_module` with `NOT_READY` for an instance in
  `error` while cleanup of a previous realization remains unresolved"), §9.3 l.2568 ("Creating a fresh
  identity MUST NOT discharge unresolved realization cleanup or permit access to persistent state that the
  previous realization may still hold"), l.3413 ("confirm quiescence and cleanup of every realization that
  could still access that state"), §10.1 l.3635 ("until the responsible realization or deployment
  mechanism confirms that the previous execution envelope has ended"), l.3637 ("confirmation that
  execution envelopes outside the previous Runtime process have ended MUST come from the protected host or
  deployment mechanism"); LOADER l.124-125 (a hosted placement is "the execution envelope for hosted
  dynamic loading:", "a process, sandbox, or container"); SECURITY l.209 ("The hosted `process` placement
  is not equivalent to a sandbox,").
- **Issue:** a Module Host is another process and can outlive the Runtime that started it. After a
  restart, Runtime keeps the cleanup ownership of a preserved instance until the protected host or
  deployment mechanism confirms that the previous execution envelope has ended (l.3635, l.3637). That
  confirmation releases a start (l.578), access to the state under a fresh identity (l.2568) and a
  transfer of the state (l.3413). What belongs to the envelope of a `process` placement is not stated: the
  host process, its process group, or every process the module started. LOADER says only that the envelope
  is a process, sandbox or container (LOADER l.124-125). What the confirmation has to cover is therefore
  not stated either.
- **Impact:** one deployment confirms the end when the host process has exited, another when every process
  the module started has exited. On the first, a second host starts on a state directory that a process of
  the earlier one holds.
- **Reading an implementation needs today:** for a `process` placement take the host's process group as
  the envelope, and state that a process which left the group is not covered.
- **Overlap:** TF-29 (what a preserved instance reports; this item is the case of an isolated
  realization), RT-05, NL-10 (answered).
- **Suggested resolution:** say in §10.1 what the envelope of each hosted placement contains.

#### TF-40 — The code of `apply_configuration` when the hook's result is lost between the Module Loader and a Module Host is not stated
- **Specs:** CONFIG §8 l.320, l.325-326 ("If Runtime cannot obtain a valid application-hook result, it
  MUST report `TRANSPORT_ERROR` when the cause is failure to exchange the required transport messages, and
  `MODULE_ERROR` otherwise"; "That distinction MUST NOT change the required transition to `error` for an
  indeterminate application outcome"); LOADER l.335 ("Channel setup and descriptor transfer are determined
  by the implementation"), l.535 ("For hosted realization, the Module Host invokes the same ABI hook under
  Loader control"), l.539-540 ("If Module Loader cannot establish whether the module accepted the value,";
  "the operation returns `realization-failed` with the failed realization"); RUNTIME l.890 ("Any carrier
  between a Module Host and the owning Runtime is realization-internal machinery rather than an ordinary
  provider route").
- **Issue:** for a hosted realization the hook runs in the Module Host (LOADER l.535). If the host ends or
  its channel breaks during the hook, the Loader cannot tell whether the module accepted the value, and it
  answers `realization-failed` (LOADER l.539-540). Runtime then has no valid hook result (CONFIG l.325).
  Which code applies turns on whether the exchange between the Loader and its host counts as "the required
  transport messages". Two readings are open.
  1. `MODULE_ERROR`. Runtime received a valid answer from the Loader and exchanged no Transport message. A
     channel inside a realization is machinery, not a route (RUNTIME l.890; LOADER l.335).
  2. `TRANSPORT_ERROR`. The messages that carried the hook and its result were lost, whatever carried
     them.
- **Impact:** the instance is `error` under both (CONFIG l.326). The caller of `apply_configuration` gets
  one code or the other for the same event, and a caller that retries after `TRANSPORT_ERROR` and not
  after `MODULE_ERROR` behaves differently.
- **Reading an implementation needs today:** `MODULE_ERROR`. Keep `TRANSPORT_ERROR` for a Loader that
  Runtime reaches through Transport and cannot reach.
- **Overlap:** TF-28 (an explicit stop after an indeterminate reconfiguration), TF-29.
- **Suggested resolution:** say in CONFIG §8 whether a channel inside a realization counts as transport
  for this rule.

#### TF-41 — Whether a disabled restart policy also stops resumption, and how orchestration tells a resumption from a retry, is not stated
- **Specs:** RUNTIME §9.3 l.3606 ("`host-terminated` means that the realization's execution envelope, or
  the Runtime process containing it, ended without cleanup ordered by Runtime"), §10.1 l.3631-3632 ("When
  orchestration becomes operational, it MUST reconcile retained requested execution intents, including
  after Runtime restart, and schedule the recovery attempts permitted by active policy"; "Deployment
  documentation MUST distinguish resumption after Runtime restart from retries after execution failure"),
  l.3634 ("it MUST report each preserved instance last recorded as `loaded`, `ready` or `stopping` as
  `error` with `host-terminated` before accepting lifecycle requests"), l.3638 ("Recovery of such an
  instance is resumption after Runtime restart"), l.3648-3651 ("The orchestration module MUST evaluate the
  active restart policy and schedule permitted recovery through `recover_module`"; "Disabling automatic
  restart is a valid policy"; "Enabled policy MUST bound retry frequency and MAY limit attempts; retry
  accounting MUST survive orchestration restart and lost responses"), l.3665-3666 ("When required
  permissions or eligible configuration become available, orchestration MUST request resumption of that
  intent through `recover_module`"; "A failed resumption is subject to the active restart policy"),
  l.3668-3670 ("Another authorized module MAY restore orchestration, or protected construction may
  establish it when the Runtime host restarts").
- **Issue:** the texts name two things, a resumption and a retry (l.3632), and one policy, the restart
  policy. Three things are not stated.
  1. Whether resumption is under that policy. With automatic restart disabled (l.3650), orchestration may
     still be bound to resume retained intents after a Runtime restart (l.3631 says "permitted by active
     policy" and does not say which policy) and after permissions or configuration become available
     (l.3665 has no condition). Only a failed resumption is put under the restart policy (l.3666).
  2. What shows that a recovery is a resumption. Recovery of an instance that Runtime, at its own start,
     reports as `error` with `host-terminated` is a resumption (l.3634, l.3638). The same classification
     is reported when an execution envelope ends during a run (l.3606), and recovery from that is a retry.
     Orchestration can also be restored alone (l.3668-3670), and nothing shows it whether the Runtime
     restarted or only it did.
  3. Whether a resumption counts against the attempt limit of l.3651.
- **Impact:** with automatic restart disabled, one deployment comes back after a power loss and another
  stays down. With an attempt limit, a platform that ends the host process routinely uses up a module's
  attempts on one Runtime and not on another.
- **Reading an implementation needs today:** treat resumption as outside the restart policy. After a
  Runtime restart and after permissions or configuration become available, request one recovery for every
  instance whose intent is `requested`, under every policy, and do not charge it. Charge what follows a
  failed resumption.
- **Overlap:** TF-29, TL-08 (the state carries no mark of an accepted attempt), NL-10 (answered).
- **Suggested resolution:** say in §10.1 whether resumption after a Runtime restart and after permissions
  or configuration become available is subject to the restart policy, and whether it is charged. Give
  orchestration a way to tell that the Runtime restarted, for example a start counter in the readiness
  result.

#### TF-42 — Whether a state assignment may pass to another instance, and what authorizes a migration of state, is not stated
- **Specs:** RUNTIME §8 l.1383-1386 ("Distinct module instances MUST NOT share a state assignment by
  default"; "Allocation, reuse across identities, sharing, inspection, retention, deletion, migration, and
  restoration of concrete state are authority-bearing policy decisions"; "This specification does not
  define their policy language, configuration files, or concrete storage layout"), §9.3 l.2552 ("When a
  module has persistent state, the state assignment is bound to this module instance identity"),
  l.2564-2566 ("Retained grants, permission settings, configuration, state assignments, execution intent,
  and audit records MUST remain attributed to their original module-instance addresses"; "Any authorized
  migration or provisioning MUST satisfy the requirements of the owning contract and active policy"),
  l.2570 ("`module_state_assignment_id` identifies an abstract persistent-state assignment visible through
  Runtime Control"), l.3412-3415 ("The replacement receives a fresh state assignment unless an explicit
  authorized state-reassignment or sharing policy applies"; "Populating its state from the old instance
  requires a separately authorized migration or restoration procedure compatible with the selected
  implementation"), l.3419 ("this revision defines no general upgrade or state-transfer Runtime Control
  method"), l.3452 ("Retirement MUST preserve concrete assigned storage and the metadata needed for its
  separately authorized retention, disposal, or migration").
- **Issue:** an upgrade replaces an instance by a new one (l.3412), and two things about its state are not
  stated.
  1. Whether the assignment itself may pass to the replacement. l.3414 allows a "state-reassignment"
     policy. l.2564 keeps state assignments with their original instance, and l.2552 binds the assignment
     to that identity. Either the reassignment clause is an exception, so that the identifier passes to
     the replacement and the old record stops showing it, or the identifier never moves and only the
     concrete state is copied or moved into a fresh assignment (l.3415). The identifier is visible through
     Runtime Control (l.2570), so the two differ for an observer.
  2. What authorizes the procedure. It is an "authority-bearing" decision (l.1385) that is "separately
     authorized" (l.3415) and must meet "the requirements of the owning contract" (l.2566). Grants,
     configuration and permission settings each have an owning contract. Persistent state has none, no
     scope names a migration, and no method performs one (l.3419).
- **Impact:** after the same upgrade one deployment shows the old assignment on the new instance and
  another shows a new one. A tool that follows state by its assignment identifier finds it on one and not
  on the other. What must be recorded, and by whom, is left to each deployment.
- **Reading an implementation needs today:** the identifier does not move. The replacement gets a fresh
  assignment, and a procedure that protected deployment input authorizes copies or moves the concrete
  state, after the old instance is stopped and its cleanup is confirmed (l.3413). No authority decision is
  taken for it.
- **Overlap:** RT-06 (upgrade by a replacement instance; resolved), TF-08, TF-02.
- **Suggested resolution:** say whether the reassignment of l.3414 moves the assignment identifier, as an
  exception to l.2564, or only concrete state. Name the owning contract of l.2566 for persistent state, or
  say that protected deployment input is the authorization.

#### TF-43 — What a complete Logos module system must contain, and which deployments BCP §5.1 and §5.4 bind, is not stated
- **Specs:** BCP l.125 ("Its local realization follows the complete-system composition rule in Section 5.1
  when that conformance is claimed"), §5.1 l.287-288 ("Credential Store is optional to implement and
  deploy"; "Neither lower-layer conformance nor complete-system conformance to this BCP requires it"),
  l.292-295 ("A deployment claiming conformance to this BCP as a complete Logos module system MUST
  establish its initial Module Loader provider through protected, non-recursive bootstrap"; "Every
  subsequent local module implementation MUST also be realized through the bound Module Loader provider"),
  §5.3 l.345 ("The deployment owner chooses and documents the applicable behavior listed in Section 5.4"),
  §5.4 l.360-363 ("A complete deployment MUST document every applicable choice that the Core
  specifications assign to deployment"; "At minimum, that documentation MUST identify:"; "supported
  Package Manager source kinds and optional package-provenance profiles"); RUNTIME l.244 ("Package Manager
  is not required for Runtime to consume already resolved module facts from protected sources"), l.1300,
  l.1554 ("When Module Loader is used, its initial provider MUST be established first and used to realize
  orchestration").
- **Issue:** four things about the complete-system claim are not stated.
  1. Its members. §5.1 gives the composition rule for the Module Loader and orchestration only. The
     Credential Store alone is declared optional for a complete system (BCP l.288), which suggests that
     the other system services are required. RUNTIME makes the Package Manager conditional (RUNTIME l.244,
     l.1300). Whether a deployment with no Package Manager can make the claim is not said.
  2. The reach of BCP l.293-295. The sentences after l.292 name no subject. They may bind only a
     deployment that makes the claim, or every Runtime with a bound Loader, for which RUNTIME has only the
     order rule of l.1554.
  3. The reach of §5.4. BCP l.360 binds "A complete deployment". The matrix gives the same duty to "The
     deployment owner" with no such word (BCP l.345). Whether a deployment that claims the lower
     specifications alone owes the document is not said.
  4. An item with no subject. For a deployment with no Package Manager, "every applicable choice" (BCP
     l.360) lets the item of l.363 be left out, and "At minimum" (BCP l.361) asks for it. Whether a true
     *none* meets the duty is not said.
- **Impact:** two deployments with the same components make different conformance statements, and a reader
  cannot tell from the claim whether a Package Manager is present. A conformance suite cannot decide
  whether a missing item of the document is a failure.
- **Reading an implementation needs today:** take every system service except the Credential Store as a
  member, and make no complete-system claim without a Package Manager. Follow BCP l.293-295 whenever a
  Loader is bound. Publish the §5.4 document for any deployment, and answer an item that has no subject
  with *none*.
- **Overlap:** TF-36.
- **Suggested resolution:** list in §5.1 what a complete system contains. Say whether l.293-295 and §5.4
  bind every deployment or only one that makes the claim, and whether an item with no subject is answered
  or omitted.

#### TF-44 — "Package-backed" is not defined, and when the Package Manager handoff is obtained again is not stated
- **Specs:** RUNTIME §8 l.1301 ("Runtime consumes `logos.package_manager.runtime_handoff` directly"),
  l.1310-1313 ("accepted integrity evidence only because the record came from the authenticated Package
  Manager system service"; "Copying those fields into another record does not preserve that provenance";
  "Protected bootstrap, static registration, deployment mechanisms, and test harnesses MAY supply
  equivalent accepted facts through implementation-local inputs"), §9.3 l.3384 ("`selection.signer` MUST
  report the exact verified signer retained with a package-backed selection when that authenticated
  evidence exists, and MUST otherwise be omitted"), l.3404 ("MUST recheck current execution authority,
  trust, prerequisites and realization acceptance"), l.3481-3483 ("For package-backed declarations, that
  integration MUST support protected selection of an exact package identity and version"), l.3506 ("MUST
  use its retained accepted declaration and MUST NOT select a replacement declaration"); PM l.409
  ("Withdrawal blocks subsequent accepted package operations and handoffs under this section; existing
  execution remains subject to its independent execution authority"), l.1413 ("MUST NOT emit the handoff
  if the package is no longer accepted by active signing trust"), l.1741 ("an engine system-service
  invocation MUST NOT be admitted to this method").
- **Issue:** two things are not stated.
  1. The term. Rules attach to a "package-backed" selection or declaration (RUNTIME l.3384, l.3483), and
     the term has no definition. It may mean only a declaration taken from an authenticated handoff
     (RUNTIME l.1310-1311), or any declaration whose protected input names a verified package and signer
     (RUNTIME l.1313, "equivalent accepted facts"). Under the second, `selection.signer` could be reported
     with no Package Manager.
  2. When the handoff is obtained. Creation selects a declaration (RUNTIME l.3481), a start uses the
     retained one (RUNTIME l.3506), and recovery rechecks "trust" (RUNTIME l.3404). Whether Runtime asks
     for a new handoff before each realization is not said. If it does, what a start does when the Package
     Manager now refuses (PM l.1413) or returns other facts is not said. If it does not, withdrawn signing
     trust reaches a retained instance only through execution authority (PM l.409), and no event tells the
     engine of it (PM l.1741).
- **Impact:** after a signer is withdrawn, one Runtime refuses the next start of an instance and another
  keeps starting it. Policy that names a signer applies to host-configured modules on one Runtime and not
  on another.
- **Reading an implementation needs today:** package-backed means taken from an authenticated handoff. Ask
  for a new handoff before each realization, and fail the start if it is refused or if its commitment,
  signer or artifact hash differ from the retained ones.
- **Overlap:** TF-07 (key rotation and installed packages), TF-08, TS-05, TP-07.
- **Suggested resolution:** define the term in RUNTIME §8. Say when Runtime obtains the handoff again and
  what a refusal or a changed handoff does to an existing instance.

#### TF-45 — A bound system service with dependents: a stop, a permission-settings update and its replacement are not stated
- **Specs:** RUNTIME l.157-161, §9.3 l.2519 ("An enforcement failure MUST retain the saved settings, leave
  the affected module stopped, and report `failed`"), l.2523 ("It MAY enforce the replacement on a running
  realization through the selected permission mechanism or stop the realization when necessary to enforce
  it"), l.3431 ("Runtime MUST NOT accept retirement while a conflicting mutation remains incomplete or a
  live dependency requires the target to remain Runtime-known"), l.3551 ("The `stop_module` method stops
  the selected module instance"), §10.1 l.3676 ("The failed provider MUST NOT be invoked to restart
  itself"), l.3685 ("When the owning Loader has failed and continued realization control cannot be
  maintained, Runtime MUST mark affected instances as `error`, fail their routes, preserve execution
  intent, and arrange termination through protected host or deployment supervision"), l.3693-3695, §10.2
  l.3729 ("Runtime MUST release Loader-owned realizations before quiescing and releasing or detaching
  their owning Loader provider through its bootstrap mechanism"), l.3731 ("Runtime MUST keep the system
  service that supplies execution authorization usable for execution renewal until every dependent
  realization has been released or its cleanup failure has been recorded"); BCP l.292 ("through protected,
  non-recursive bootstrap").
- **Issue:** a system service is an ordinary module instance (l.157-161), so the lifecycle and settings
  methods can name it. Three things are not stated for one that has dependents: the Module Loader while it
  owns realizations, or the Capability Authority while decisions it gave are in force.
  1. A stop. `stop_module` has no rule for it (l.3551). The rules that Loader-owned realizations are
     released first, and that the service which supplies execution authorization stays usable until its
     dependents are released, stand in the shutdown procedure only (l.3729, l.3731), and the
     live-dependency rule covers retirement only (l.3431). The Runtime may refuse, stop the dependents
     first, or stop the service and treat it as lost.
  2. A permission-settings replacement. Reconciliation may have to stop the realization (l.2523), and a
     failure leaves it stopped (l.2519). The question is the same.
  3. Its replacement. A failed provider is not invoked to restart itself (l.3676). Whether a replacement
     Loader is established by bootstrap again, and what "non-recursive" (BCP l.292) allows, is not said.
     The supervision that must end the affected realizations (l.3685) is left to the deployment
     (l.3693-3695), and the Host Embedding API gives the host no sign that it is needed.
- **Impact:** an operator's stop of the Loader ends every hosted module on one Runtime and is refused on
  another.
- **Reading an implementation needs today:** refuse `stop_module` and a settings replacement with
  `NOT_READY` while the service has dependents. Restore a failed Loader only by a restart of the Runtime
  host.
- **Overlap:** TF-26, TF-36, TF-37.
- **Suggested resolution:** give `stop_module` and the settings methods a rule for a bound system service
  that has dependents. Say in §10.1 how a failed Loader is replaced, and how the host learns that
  termination through its supervision is required.

#### TF-46 — Permission settings at three edges: an instance established by protected bootstrap, an instance with no realization, and the snapshot a module reads
- **Specs:** RUNTIME §9 l.1575 ("The binding does not authorize remote system-service invocation or waive
  package, realization, execution-authority, or permission checks"), §9.3 l.2465 ("Omitted permissions are
  denied, including when the array is empty; declarations and grants MUST NOT bypass these limits"),
  l.2468-2471 ("When a new instance has no accepted protected permission settings, Runtime MUST atomically
  initialize its permission settings with revision 1, an empty permission array, status `applied`, and no
  failure"; "Protected provisioning MAY supply independently authorized initial settings before the
  instance is exposed"; "Restoration of an existing instance MUST preserve its accepted settings,
  revision, and application state"), l.2476-2477 ("`applied` means the saved settings are enforced"; "For
  code that the selected execution path cannot restrict, `applied` asserts only that Runtime grants no
  access beyond the saved settings"), l.2500-2502 ("Runtime MUST derive it from retained enforcement
  state, not from module declarations, saved permission settings, or a fresh authority evaluation"; "When
  Runtime cannot provide an enforced snapshot, it MUST return `unavailable` rather than an empty
  permission array"), l.2518, l.2521 ("Settings administration MUST NOT create execution intent or
  substitute the administrator's execution authority"), l.2523, l.2527-2528 ("An `applied` settings state
  describes enforcement, not successful resumption"; "Runtime MUST NOT report the replacement as `applied`
  until the selected mechanism enforces the saved constraints"); CA l.124 ("An allow decision MUST NOT
  broaden a requested scope and MAY narrow it"), l.339, l.360 ("Runtime MUST reject the operation if the
  selected execution path cannot enforce a required constraint"); LOADER l.425 ("Outside protected initial
  system-service bootstrap,").
- **Issue:** three things are not stated.
  1. An instance that protected bootstrap establishes. Its bootstrap needs no allow decision (CA l.339;
     LOADER l.425). Whether its saved settings still limit it is not said. RUNTIME l.2465 has no
     exception, and the system-service binding waives no permission check (RUNTIME l.1575). With the
     default of l.2468 every permission of such an instance is denied, and it runs. Either bootstrap
     provisions its settings (l.2470), or the settings do not apply to it. In the second case `applied`
     (l.2476) is untrue for it, unless its execution path cannot restrict it (l.2477).
  2. An instance with no realization. A replacement saved while the instance is `unloaded` has no running
     realization to be enforced on (RUNTIME l.2523). l.2528 withholds `applied` until the mechanism
     enforces the constraints, while l.2468 reports `applied` for a new instance that never ran. Such a
     replacement may be `applied` at once, `pending` until a start that the administration may not cause
     (l.2521), or `failed` when it names a permission that nothing can enforce (CA l.360). The revision
     and status of settings that protected provisioning supplies (l.2470), and whether a restored
     `pending` (l.2471, l.2518) may change before the instance is exposed, are not given either.
  3. The snapshot. `get_execution_permissions` answers from "retained enforcement state" (RUNTIME l.2500),
     a term with no definition. It may be what Runtime handed to enforcement at admission, that is the
     saved settings cut to the scopes the decision allowed (CA l.124), or what the enforcing mechanism
     reports.
- **Impact:** a system service that bootstrap establishes on a path that can restrict it is held to empty
  settings on one Runtime and runs with what its bootstrap gave it on another, and both show status
  `applied`. A replacement saved for a stopped instance shows three different statuses on three Runtimes.
  A module reads different snapshots of the same enforcement.
- **Reading an implementation needs today:** provision the settings of every bootstrap-established
  instance during its protected construction, so that the settings limit every instance alike. Report a
  replacement saved for an instance with no realization as `applied` when every permission it names has an
  enforcement point, and as `failed` otherwise. Answer the snapshot from what was handed to enforcement at
  admission, kept per realization.
- **Overlap:** TF-32 (which scopes an execution decision covers), TF-10, TL-04.
- **Suggested resolution:** say in §9.3 whether saved settings limit an instance that protected bootstrap
  establishes. Give the status of a replacement saved while no realization exists. Define retained
  enforcement state.

#### TF-47 — Transport does not say whether a route that is explicitly closed gets the `NOT_READY` signal on the wire
- **Specs:** TRANSPORT §3.2 l.524-527 ("Either party may close the socket at any time"; "All in-flight
  requests receive a synthetic `TRANSPORT_ERROR` response"), §8.1 l.969-977 ("When route authority expires
  or is revoked, that Runtime MUST stop admitting new operations and terminate affected subscriptions and
  the protected session"; "the Runtime MUST send ProtocolError `NOT_AUTHORISED` when the connection
  remains writable and close the session"; "When the route ends through a loss of route readiness,
  including `route-timeout`, the same termination rules apply with `NOT_READY` in place of
  `NOT_AUTHORISED`"); INTERFACE l.1454-1458 ("Known authority withdrawal or expiry uses `NOT_AUTHORISED`;
  otherwise explicit route closure or known provider/readiness loss uses `NOT_READY`"; "Connection failure
  without a known authorization or readiness cause uses `TRANSPORT_ERROR`"; "The code records the first
  terminal transition and MUST NOT be replaced when a later cause becomes known"); RUNTIME l.1262
  ("explicit route closure or loss of Runtime-owned provider or route readiness MUST produce
  `NOT_READY`"), l.3348-3349.
- **Issue:** at an expiry or revocation of route authority the provider side sends a ProtocolError that
  carries the cause (TRANSPORT l.974), and a route that ends through a loss of route readiness has the
  same message with `NOT_READY` (TRANSPORT l.977). RUNTIME l.1262 and INTERFACE l.1455 name explicit route
  closure beside the loss of readiness, as a separate cause with the same code. TRANSPORT l.977 names only
  the loss of readiness. Whether a route closed through `close_route` (RUNTIME l.3349) ends "through a
  loss of route readiness" is not said. If it does not, there is no message for it, and the socket closes
  (TRANSPORT l.524). The handle must then record `NOT_READY` (INTERFACE l.1455). The caller side sees only
  a lost connection, may not infer a cause (INTERFACE l.1457), and records `TRANSPORT_ERROR` (INTERFACE
  l.1456), for good (INTERFACE l.1458). Where the consumer closes its own route, or consumer and provider
  have one Runtime, the consumer's Runtime knows the cause. Where a different consumer closes a route
  between two Runtimes (RUNTIME l.3348), nothing carries the cause.
- **Impact:** a consumer of a remote route sees `TRANSPORT_ERROR` for an orderly closure and retries where
  `NOT_READY` would have told it to stop.
- **Reading an implementation needs today:** treat an explicit closure as a loss of route readiness under
  TRANSPORT l.977, and send ProtocolError `NOT_READY` before the session closes.
- **Overlap:** TF-15 (a new operation after a lost connection), TF-23, TL-03.
- **Suggested resolution:** name explicit route closure in TRANSPORT l.977 beside the loss of route
  readiness, or say that a closed route ends without a message.

#### TF-48 — The erasure of a marked payload cannot be met when an execution envelope is ended by force
- **Specs:** INTERFACE §1.4.1 l.360-362 ("They MUST erase their owned temporary buffers containing payload
  data after their last use, before releasing or reusing their storage"; "This requirement includes
  encoding, decoding, commitment processing, transport buffering, and partial processing on failure or
  cancellation"), l.368 ("An invocation path MUST NOT be established for a marked payload unless its
  participating implementations support these requirements"), l.380 ("Each implementation remains
  responsible for the temporary copies it owns"); RUNTIME l.633 ("Protected supervision may terminate an
  isolated execution envelope without waiting for a public release invocation"), l.909-911 ("native
  destruction is not guaranteed to begin or return"); LOADER l.571 ("Forced termination of the execution
  envelope MAY prevent destruction from beginning or returning").
- **Issue:** the erasure duty has no exception (INTERFACE l.361-362), and it reaches a Module Host as an
  invocation intermediary (INTERFACE l.360). The texts also allow an envelope to be ended by force, at a
  deadline or after its control channel is lost (RUNTIME l.633, l.909-911; LOADER l.571), and a process
  can end by a fault. A process that is ended erases nothing. Whether such an end breaks l.361, and
  whether the participants of a path through a placement that may be ended by force "support these
  requirements" (INTERFACE l.368), is not said.
- **Impact:** a deployment cannot both allow forced termination and claim the erasure rule for hosted
  modules. One implementation refuses marked payloads on every hosted path, and another accepts them and
  claims an erasure it cannot guarantee.
- **Reading an implementation needs today:** erase on every orderly path, the orderly end of a host
  included, and make no erasure claim for an envelope that was ended by force. State that limit where the
  deployment documents its placements.
- **Overlap:** TF-28, TF-39.
- **Suggested resolution:** say in §1.4.1 that forced termination of an execution envelope is outside the
  erasure duty, or say what a deployment must do before it may end such an envelope.

#### TF-49 — A context returned together with a failure code: whether anything is left to clean is not stated
- **Specs:** INTERFACE l.1603-1608 ("Failure requires a nonzero result code and a null context;"; "the
  module MUST release any partially initialized instance state before returning"; "The ABI caller MUST
  reject any other result/context combination"), l.1633 ("Destroy one successfully initialized module
  instance"); RUNTIME l.1486-1493 ("Runtime MUST treat the reported rejection or a module's ABI-version or
  structure-size"; "A failed initialization does not create a live module instance context and"; "the
  applicable ABI caller MUST NOT invoke `_MODULE_destroy(context)` for that failed initialization");
  LOADER l.418-423 ("Module Loader MUST clean every partial context, binding, transferred listener
  reference, and execution envelope that it can safely clean"; "When cleanup completes, it returns the
  error without a realization record"; "it retains and returns a failed realization so Runtime can invoke
  `release`").
- **Issue:** a module that returns a nonzero code and also writes a context breaks INTERFACE l.1606. The
  caller must reject that result (INTERFACE l.1608), and Runtime treats it as an initialization failure
  (RUNTIME l.1488). What becomes of the context is not said. `_MODULE_destroy` is declared for a
  successfully initialized instance (INTERFACE l.1633) and is forbidden after a failure with a null
  context (RUNTIME l.1491). For a failure with a context neither line speaks. Two readings are open.
  1. Nothing is left. The module was bound to release its partial state before returning (INTERFACE
     l.1607), and the pointer is ignored. Behind a Loader the cleanup is then complete, and the Loader
     returns the error with no record (LOADER l.421).
  2. Something may be left that only the module can free. Cleanup then "remains necessary" (LOADER l.422),
     the Loader retains a failed realization (LOADER l.423), and no `release` of it can ever succeed,
     because release would need the destroy call that is not defined for this case.
- **Impact:** under the second reading the instance cannot start again in that process, and its record
  shows a failed realization for good. Under the first a faulty module leaks what it allocated, and the
  instance can be started again.
- **Reading an implementation needs today:** the first: an error and no realization record. Do not call
  `_MODULE_destroy`. What the stray pointer refers to stays the module's fault.
- **Overlap:** TF-03, TF-29.
- **Suggested resolution:** say in INTERFACE beside l.1608 that a context written with a failure is
  ignored and never destroyed, and in LOADER §6 that such a failure leaves nothing to clean.

#### TF-50 — At a hosted provider's endpoint, which event commits a Response and when a policy change takes effect there are not stated
- **Specs:** TRANSPORT l.852 ("The terminal-response linearization point is the commitment of a Response
  to the connection's ordered output sequence"), l.969-971 ("When route authority expires or is revoked,
  that Runtime MUST stop admitting new operations and terminate affected subscriptions and the protected
  session"; "A new Request processed during termination MUST receive a correlated
  `logos.transport.response-err` with `NOT_AUTHORISED`, without dispatch"), l.1104 ("The Module Host MUST
  serve only that transferred listener and MUST NOT bind or substitute another endpoint"); RUNTIME l.124
  ("For a hosted provider, it may also expose the provider endpoint and perform provider-side
  invocation"), l.890 ("Any carrier between a Module Host and the owning Runtime is realization-internal
  machinery rather than an ordinary provider route"), l.1212-1215 ("Runtime MUST order the applicable
  policy transition with the decision to commit a Response; a prior authorization check MUST NOT permit a
  later commitment contrary to that policy"; "A committed result can still be lost when the connection
  terminates; commitment is not proof of receipt or rollback").
- **Issue:** the connections of a hosted provider are held by its Module Host, which serves the listener
  (TRANSPORT l.1104; RUNTIME l.124). A Response is committed when it enters the ordered output sequence of
  its connection (TRANSPORT l.852), and that sequence is in the Module Host. The policy transitions that a
  commitment must be ordered with are changes of Runtime state (RUNTIME l.893): a revocation, an expiry, a
  stop. RUNTIME l.1212 gives the ordering to "Runtime", and TRANSPORT l.969 gives the end of the session
  to "that Runtime". How the two processes meet is left to the carrier, which is not specified (RUNTIME
  l.890). Two points stay open, and both can be seen from outside.
  1. Which event is "the decision to commit a Response" (RUNTIME l.1212). It may be the acceptance of the
     Response into the output sequence by the Module Host, or a decision that the Runtime takes for each
     Response before the Module Host may write it. Under the second, every Response of a hosted provider
     waits for an exchange with the Runtime.
  2. When a policy transition takes effect at that endpoint: when the Runtime decides it, or when the
     Module Host processes what the Runtime tells it. A Response that the Module Host accepts between the
     two is "a later commitment contrary to that policy" (RUNTIME l.1212) under the first and a permitted
     one under the second. The same question holds for "A new Request processed during termination"
     (TRANSPORT l.971): when termination has begun for a Request that the Module Host reads is not said.
- **Impact:** a consumer may or may not receive a successful Response after the Runtime has recorded the
  route as revoked, and the outcome the Runtime records for the call may differ from what the consumer
  received. One implementation sends every Response through the Runtime to order it, and another lets the
  Module Host commit.
- **Reading an implementation needs today:** the Module Host commits. A policy transition takes effect at
  a hosted endpoint when the Module Host processes what the Runtime tells it, and a Response accepted
  before that is committed under the earlier policy. The Module Host reports what it committed, and the
  Runtime records that.
- **Overlap:** TF-23, TF-33, TF-51.
- **Suggested resolution:** say in RUNTIME §7.3.1 that for a hosted provider the boundary in the Module
  Host makes the commit decision and that a policy transition takes effect there when that boundary
  processes it, or say that the Runtime decides each Response.

#### TF-51 — Whose computation of the payload roots enters a call record when the payload never enters the Runtime's own process is not stated
- **Specs:** RUNTIME l.122 ("The Runtime enforcement point that resolves the consumer, route, selected
  provider, selected contract, method, authority, commitments, and audit requirements for a call"),
  l.734-735 ("The handle wraps a local transport connection to the selected provider"), l.886 ("its
  process-local invocation boundary remains part of the same logical Runtime routing domain"), l.897 ("An
  invocation boundary that shares an address space with module code"), l.1665-1667 ("Runtime MUST compute
  every request and successful-response payload commitment at the Runtime-controlled invocation boundary,
  independently of whether authority policy requires audit retention"), l.1673-1674 ("It MUST derive each
  retained request or response commitment from the schema-typed value at the enforcement boundary, not
  from an unverified root or contract identifier supplied by the provider or consumer"); CA l.1217 ("the
  Runtime-controlled invocation boundary MUST produce a `call` audit record"), l.1250 ("`value_root` is
  the corresponding root computed or verified under those exact inputs"); TRANSPORT l.1104 ("The Module
  Host MUST serve only that transferred listener and MUST NOT bind or substitute another endpoint");
  SECURITY l.507 ("call evidence authenticates one retained call record and optional verified views
  without granting authority or proving computation correctness"), l.523 ("place third-party native code
  behind a selected process or application isolation profile whose required controls are available").
- **Issue:** on the path that RUNTIME describes for local transport, the handle of a hosted consumer holds
  a connection to the provider's endpoint (RUNTIME l.734-735), and the endpoint of a hosted provider is in
  its Module Host (TRANSPORT l.1104). A call between two hosted modules then goes from one Module Host to
  the other, and its payload never enters the Runtime's own process. The Runtime must still compute both
  roots at the Runtime-controlled invocation boundary (RUNTIME l.1665-1666), and a retained root must come
  from the value at the enforcement boundary and not from a root "supplied by the provider or consumer"
  (RUNTIME l.1673-1674). The only boundaries that see the value are those inside the two Module Hosts, and
  each shares an address space with module code (RUNTIME l.897). Whether such a boundary is the
  Runtime-controlled invocation boundary for these rules is not said. Two readings are open.
  1. It is, as "part of the same logical Runtime routing domain" (RUNTIME l.886). The record then holds a
     root that was computed in a process the module's code can alter, and nothing in the record or in the
     call evidence (SECURITY l.507) shows that. Which side's root the record holds when both ends are
     hosted is not said either: the sending boundary computes it (TRANSPORT l.640), the receiving boundary
     recomputes it (SECURITY l.338-340), and CA l.1250 allows "computed or verified".
  2. It is not, and a root reported by a Module Host is one "supplied by the provider or consumer"
     (RUNTIME l.1674). The value must then pass through a process of the Runtime itself. Since RUNTIME
     l.1665-1666 ask for the roots of every call, with or without retention, every payload passes through
     the Runtime, and the direct path of RUNTIME l.734-735 is not available.
- **Impact:** the `call` record of one implementation rests on the Runtime's own computation and that of
  another on a Module Host, and the two records look the same. A module is placed in a host because it is
  not trusted to share the Runtime's address space (SECURITY l.523), and under the first reading the
  record of its calls rests on that module's process.
- **Reading an implementation needs today:** the first. The boundary in the provider's Module Host
  verifies the request root and computes the response root, and reports them to the Runtime, which writes
  the record. The deployment documents that the roots of a hosted call rest on the integrity of the
  provider's Module Host.
- **Overlap:** TF-50, the TF-06 note on the sentences that describe local transport mode.
- **Suggested resolution:** say in RUNTIME §9, beside l.1665, whether a boundary inside a Module Host is
  the Runtime-controlled invocation boundary for commitments and call records. If it is, say that the
  record's roots carry the trust of that Module Host, and which side's root is recorded. If it is not, say
  that the payload of such a call passes through the Runtime.

#### TF-52 — For a remote route, which component carries the session of a hosted consumer or provider is not stated
- **Specs:** RUNTIME l.124 ("For a hosted provider, it may also expose the provider endpoint and perform
  provider-side invocation"), l.737-738 ("The handle wraps a remote transport connection to the selected
  remote provider"), l.897-898 ("An invocation boundary that shares an address space with module code MUST
  NOT place unrelated secrets or authority material in that address space"), l.1256 ("the route handle
  uses the authenticated Runtime-to-Runtime path and provider session established for that route"),
  l.2661-2662 ("The baseline uses one Runtime credential for the Runtime identity; ordinary modules and
  providers do not receive separate long-lived certificates"), l.2775 ("The provider endpoint is
  controlled by Runtime"), l.2780 ("The provider-side endpoint MUST authenticate as the Runtime that owns
  the selected provider"), l.2788-2789 ("Runtime dispatches authorized messages to the selected provider
  through its protected local invocation path"), l.2792 ("The mandatory remote profile MUST NOT expose an
  individual module process or container in a way that bypasses this enforcement boundary"), l.3024 ("the
  Runtime-controlled invocation boundary performs the profile-required Runtime authentication and Hello
  exchange under Section 4.1"), l.3033 ("A language binding MAY materialize a ready route returned by
  those methods as a process-local handle or establish its Transport session"); TRANSPORT l.1104 ("The
  Module Host MUST serve only that transferred listener and MUST NOT bind or substitute another
  endpoint"), l.1196 ("the authenticated source Runtime identity matches the route consumer's
  `runtime_instance_id`"), l.1274 ("One authenticated connection carries one such provider session and
  channel-binding use"); LOADER l.331 ("Module Loader MAY convey a private invocation channel between a
  Module Host and a Runtime-controlled Transport adapter outside the module's execution envelope"), l.333
  ("It MUST NOT expose Runtime credentials to the Module Host or module").
- **Issue:** for local transport the specifications say where the sessions of a hosted module live: its
  Module Host serves the listener that the Runtime transferred (TRANSPORT l.1104), and the boundary in
  that process may expose the provider endpoint (RUNTIME l.124). For remote transport they name the
  Runtime and, as an option, one component beside it: a Transport adapter under the Runtime's control and
  outside the module's execution envelope, to which the Loader may convey a private channel from a Module
  Host (LOADER l.331). A remote connection is authenticated on both sides as a Runtime (TRANSPORT l.1196;
  RUNTIME l.2780). The Runtime has one credential (RUNTIME l.2661-2662), which may not be placed in a
  process that also holds module code (RUNTIME l.897-898) and which the adapter may not expose to a Module
  Host (LOADER l.333). So the component that authenticates a remote connection is not a Module Host. What
  carries the session after that is described in more than one way. At the provider's end, RUNTIME
  l.2788-2789 has the Runtime dispatch each message to the provider over its local path, in a sentence
  without a requirement keyword, and RUNTIME l.2792 forbids only the exposure that bypasses enforcement.
  At the consumer's end, RUNTIME l.3024 has the Runtime-controlled invocation boundary authenticate and
  exchange Hello when the route is materialized, RUNTIME l.737-738 and l.3033 put the connection with the
  handle and its language binding, and RUNTIME l.1256 puts it on a path between two Runtimes. The adapter
  is permitted and not required. Two points stay open.
  1. Whether the component that authenticated the connection, the adapter where there is one, must stay on
     the path of every payload of the session, relaying between the remote connection and the private
     channel or local path of a hosted module, or whether the session may then be carried by the Module
     Host of the hosted consumer or provider. A connection carries one provider session (TRANSPORT
     l.1274), so it never serves two module instances.
  2. If it may, whether the traffic keys of that one session are "Runtime credentials" in the sense of
     LOADER l.333, and whether a session served in the provider's own process is exposed "in a way that
     bypasses this enforcement boundary" (RUNTIME l.2792) when the boundary in that process enforces the
     route's method and event access, as it does for a local session (TF-50).
- **Impact:** the layouts interoperate, because the peer sees the same connection. They differ in whether
  the second conforms, in which process holds the payloads of every remote call, and in where the payload
  commitments of a remote call are computed (TF-51). An implementation that keeps payloads out of the
  Runtime's own process for local routes can do so for remote routes only through an adapter, with one
  more process on the path at each end.
- **Reading an implementation needs today:** a component of the Runtime that holds no module code, such as
  the adapter of LOADER l.331, authenticates each remote connection, redeems the ticket and stays the peer
  of the session. It exchanges the session's messages with a hosted module over a private channel or that
  module's local path.
- **Overlap:** TF-50, TF-51, TS-04 (one connection for each route), the TF-06 note on the sentences that
  describe local transport mode.
- **Suggested resolution:** say in RUNTIME §9.3 whether l.2788-2789 describes a required hop or one
  permitted layout, and whether an authenticated provider session, or the caller's end of one, may be
  carried by the process-local invocation boundary of a hosted module once the Runtime has authenticated
  the connection and bound the session to its route. Say in LOADER §5.4 whether the adapter is the only
  component that may stand between a remote connection and a Module Host.

#### TF-53 — CREDENTIAL STORE requires its provider to answer `NOT_AUTHORISED`, a code that provider code may not return
- **Specs:** CREDENTIAL STORE l.29 ("Credential Store is an ordinary local module provider using the
  existing identity, lifecycle, authority, routing, and invocation model"), l.55-56 ("The provider MUST
  reject a call without authenticated context or from a module instance owned by another Runtime with
  `NOT_AUTHORISED`"; "The provider MUST reject an undeclared or unauthorized slot with `NOT_AUTHORISED`
  before accessing its backend or revealing its presence"), l.342 ("The provider MUST reject requests
  without authenticated local caller context with `NOT_AUTHORISED`"), l.176 (the response error is
  `unavailable` or `capacity`); INTERFACE l.3308-3311 ("Provider code MAY return or complete with
  `LOGOS_OK`, `LOGOS_ERR_METHOD_NOT_FOUND`, `LOGOS_ERR_INVALID_PARAMS`, or `LOGOS_ERR_MODULE`"; "any other
  status code violates these rules"; "A provider result violating these rules MUST be treated as
  `LOGOS_ERR_MODULE`, without forwarding its diagnostics or contract-response outputs").
- **Issue:** the slot check and the caller-context check are the provider's own (CREDENTIAL STORE l.55-56,
  l.342), and their outcome is the shared code `NOT_AUTHORISED`. Provider code cannot return that code:
  the ABI caller turns every code outside the list of INTERFACE l.3308-3309 into `MODULE_ERROR` and drops
  the diagnostics. The response schemas have no arm for a refusal (l.176). So the consumer of a conforming
  Credential Store behind a conforming Runtime receives `MODULE_ERROR` where the contract promises
  `NOT_AUTHORISED`.
- **Impact:** a caller cannot tell a refused slot from a provider failure, or a Runtime has to treat this
  one provider differently from every other.
- **Suggested resolution:** give the refusals an arm in the Credential Store response schemas, as the
  Capability Authority and the Package Manager have in theirs; or move the two checks to the Runtime,
  before dispatch; or allow `NOT_AUTHORISED` to a provider that enforces a rule of its own contract.

#### TF-54 — The triggers of the module state table name no stop that enforcement causes
- **Specs:** RUNTIME l.520-521 and l.526 (the three rows that lead to `stopping`; their triggers are "An
  explicit stop or Runtime shutdown is ordered before readiness" and "An explicit stop or Runtime
  shutdown"), l.524 (the row from `stopping` to `error`; its trigger is "Cleanup fails"), l.528 ("Runtime
  MUST NOT perform any other module-state transition"), l.3663 ("A stop caused by permission-settings
  reconciliation, permission withdrawal, or loss of execution authorization MUST preserve execution intent
  and its authenticated origin"), l.1735 ("An explicit stop MUST cancel retained execution intent,
  including when the instance is already `stopping` or `unloaded`"), l.3634 ("When Runtime starts after
  its previous process ended without completed shutdown, it MUST report each preserved instance last
  recorded as `loaded`, `ready` or `stopping` as `error` with `host-terminated` before accepting lifecycle
  requests").
- **Issue:** Runtime stops an instance when its execution authorization ends or when its permission
  settings can no longer be enforced. That stop keeps the intent (l.3663). It is therefore not an explicit
  stop, which cancels the intent (l.1735), and it is not a Runtime shutdown. The pairs of states it needs
  are in the table, but every row that leads to `stopping` names one of those two triggers. Whether l.528
  forbids the stop depends on whether a row is the pair of states alone or the pair with its trigger, and
  the text does not say which.

  The report after an unclean restart (l.3634) raises the same question for an instance last recorded as
  `stopping`. The row to `error` has the trigger "Cleanup fails" (l.524), and that cleanup never finished.
- **Impact:** if the trigger is part of the row, an implementation either makes a transition that l.528
  forbids, or reports an enforcement stop as an explicit one and loses the intent that l.3663 requires it
  to keep.
- **Overlap:** TL-07 (Appendix A) asked which transitions are legal; the table answers that for the pairs
  of states.
- **Suggested resolution:** add the enforcement stop to the triggers of the rows from `loaded`, `ready`
  and `error` to `stopping`, and the report after an unclean restart to the row from `stopping` to
  `error`; or say that the trigger column is not exhaustive.

#### TF-55 — Whether one contract extends another depends on `_module`, which the schema root does not commit
- **Specs:** COMMITMENT l.966-972 (B extends A when, among other conditions, "both are concrete module
  contracts with the same `_module` value, or both are interface contracts"), l.974 ("A verifier MUST
  establish the relation by constructing both schema roots from their explicitly supplied documents; a
  declared claim does not establish it"), l.250 ("Ignore the metadata declarations `_module`,
  `_interface`, `_implements`, and `_sensitive` for schema-declaration construction"), l.951-957 (the
  schema root holds the revision, the namespace, the declarations and the implemented interface roots);
  INTERFACE l.1693 ("Each `extends` entry carries an earlier contract that the `primary` contract or one
  `interfaces` contract of this descriptor extends under LOGOS-MODULE-COMMITMENT-MODEL").
- **Issue:** the relation is stated between two contracts and is verified from two documents. One of its
  conditions, the equality of `_module`, is in neither schema root (l.250, l.951-957). Two documents with
  the same schema root can carry different `_module` values, so the same pair of commitments extends or
  does not extend according to the documents supplied. The earlier document is supplied by the provider
  that claims the extension (INTERFACE l.1693), which can always supply it under its own `_module`. The
  condition then excludes nothing. If it is there to keep one module from offering an earlier contract of
  another, it does not.
- **Impact:** a descriptor or a manifest passes or fails the extension check by an uncommitted metadata
  line, and two verifiers that hold different copies of the earlier document disagree.
- **Suggested resolution:** drop the `_module` condition and rely on the namespace and the declarations;
  or say what the condition is to prevent, and tie `_module` to something a verifier can check, such as
  the module name of the declaring package or instance.

#### TF-56 — A package provides a contract by its manifest, while the variant that is installed may lack the module
- **Specs:** PM l.1215-1216 ("A package provides a contract when one of its module declarations declares
  that commitment as its `primary_contract`, in `implements`, or in `extends`"; "A candidate for a package
  name MUST provide every contract listed by any accumulated requirement for that name; a candidate that
  does not is ineligible"), l.1171 ("Module scope is variant-specific and is determined by the presence of
  the module's implementation artifact"), l.816 ("It MUST NOT contain a module declaration whose
  implementation artifact is absent from the selected variant").
- **Issue:** whether a candidate satisfies a dependency's `contracts` is judged on the module declarations
  of its manifest (l.1215). Which modules a host receives is judged on the selected variant (l.1171,
  l.816). A package whose variant for the target environment lacks the module that declares the contract
  is eligible, is installed, and provides no such contract on that host. Whether the declarations of
  l.1215 are those of the selected variant is not said.
- **Impact:** a closure resolves and installs, and the dependent then finds no provider. The `contracts`
  list of a dependency exists to prevent that.
- **Suggested resolution:** say that a candidate provides a contract when a module declaration whose
  implementation artifact is in the variant selected for the target environment declares it.

#### TF-57 — When the instances of a failed Module Loader are marked `error` depends on a condition that is not defined
- **Specs:** RUNTIME l.3685-3687 ("When the owning Loader has failed and continued realization control
  cannot be maintained, Runtime MUST mark affected instances as `error`, fail their routes, preserve
  execution intent, and arrange termination through protected host or deployment supervision"; "The owning
  Loader has failed when its provider module instance leaves `ready` because its realization ended or
  failed"; "Failed Loader operations or loss of its binding while that provider instance remains `ready`
  are temporary service unavailability"), l.909 ("Observed terminal loss of the protected carrier required
  to control a hosted realization MUST prevent new instance-dependent work and initiate termination
  through the protected realization or deployment mechanism").
- **Issue:** l.3685 has two conditions. The first is defined (l.3686). The second, that continued
  realization control cannot be maintained, is defined nowhere, and it is not tied to the loss of the
  protected carrier (l.909). When a Loader has failed and Runtime still holds the carrier of a hosted
  realization, whether that instance stays `ready` or is marked `error` depends on what control means.
- **Impact:** after the same Loader failure one Runtime keeps its hosted instances `ready`, and another
  marks them `error` and fails their routes.
- **Overlap:** RT-05 (Appendix A) asked what separates a Loader that is briefly unavailable from one that
  has failed, which l.3686-3687 answer. TF-45, point 3.
- **Suggested resolution:** define the second condition, for instance as the loss of every protected
  carrier or mechanism through which Runtime can end the realization.

#### TF-58 — What Runtime reports at its next start for an instance that a completed shutdown left `stopping` is not stated
- **Specs:** RUNTIME l.3702 ("A module instance that is still `stopping` at expiry remains `stopping` and
  reports `cleanup-timeout` under Section 3.4"), l.3727 (shutdown continues once a realization's "cleanup
  failure has been recorded according to shutdown policy"), l.3732 ("a `cleanup-timeout` reported at that
  expiry is a recorded cleanup failure for this purpose"), l.3634 ("When Runtime starts after its previous
  process ended without completed shutdown, it MUST report each preserved instance last recorded as
  `loaded`, `ready` or `stopping` as `error` with `host-terminated` before accepting lifecycle requests"),
  l.3635 ("the end of the previous Runtime process is that confirmation for a realization within that
  process"), l.3637 (the end of an envelope outside the previous process "MUST NOT be inferred from
  retained records of Runtime or of the realization mechanism, including a record of completed shutdown"),
  l.575-577 ("Runtime MUST report `cleanup-timeout` as the instance's failure until the stop completes or
  its cleanup fails"; "When the pending cleanup then completes, the explicit stop completes successfully";
  "A cleanup failure during an explicit stop transitions the instance to `error`"), l.3606
  ("`host-terminated` means that the realization's execution envelope, or the Runtime process containing
  it, ended without cleanup ordered by Runtime").
- **Issue:** a shutdown can now complete while an instance is still `stopping` with `cleanup-timeout`
  (l.3702, l.3727, l.3732), so a completed shutdown can leave that record. The rule for the next start
  covers only a process that "ended without completed shutdown" (l.3634). For a completed shutdown nothing
  says what the preserved instance is at the next start: `unloaded`, because the stop completed when its
  envelope ended (l.576, l.3635); `error`, and then with which classification, since its cleanup was
  ordered by Runtime (l.3606); or still `stopping` until the end of an envelope outside the process is
  confirmed (l.3637). The text also presumes that Runtime can tell the two kinds of end apart, and names
  "a record of completed shutdown" only to say what must not be inferred from it.
- **Impact:** after the same shutdown one Runtime reports the instance `unloaded` and resumes its retained
  intent, another reports `error`, and for a hosted realization a third keeps it `stopping`. A lifecycle
  request for that instance is answered differently in each, and so is the recovery policy that reads the
  classification.
- **Reading an implementation needs today:** the stop completes when the end of the envelope is confirmed
  (l.576). That is at the next start for a realization within the previous process (l.3635). For one
  outside it the instance stays `stopping` with `cleanup-timeout` until the protected mechanism confirms
  the end (l.3637). The implementation records that the shutdown completed, so that the same record after
  an unclean end still follows l.3634.
- **Overlap:** TF-54 names the same table rows for a stop that enforcement causes.
- **Suggested resolution:** say what a preserved `stopping` record means after a completed shutdown, for a
  realization within the previous process and for one outside it, and whether Runtime must record that a
  shutdown completed.

#### TF-59 — What one candidate record is, for the consideration limit and for the material a resolution needs, is not defined
- **Specs:** PM l.1245 (a limit on "candidate records considered for one package name"), l.1262 ("A
  candidate consideration occurs when Package Manager examines one record whose version satisfies the
  accumulated requirements"), l.1265 ("Each candidate record is charged at most once for that package name
  in one root operation"), l.1289 ("A candidate is an installed package record or catalog package whose
  version satisfies every accumulated requirement for its package name"), l.961 (separately signed
  packages of one identity "have different manifest commitments and are distinct candidates under Section
  11"), l.1306 ("a record whose commitment is not yet known is examined and charged like any other"),
  l.1330 ("equivalent acceptable sources for the same exact package identity and full manifest
  commitment"), l.1327-1328 ("If multiple acceptable manifests claim the same package name and version
  with different manifest commitments, protected catalog policy MUST select one exact commitment"), l.1295
  ("A candidate that is not reached is not examined, and its material MUST NOT be required or cause the
  root operation to fail"), l.1308 (material that "cannot be located or materialized" fails the root
  operation with `package-unavailable`), l.1279 ("Limit exhaustion and all counter values are determined
  by the installed state, catalog inputs, and protected policy").
- **Issue:** three things can be the record that is examined and charged. One is a package identity, a
  name with a version. One is a package, an identity with its manifest commitment: l.961 makes two
  separately signed packages of one identity distinct candidates. One is a catalog source record: l.1306
  speaks of a record whose commitment is not yet known, which fits a catalog entry before its material is
  read, and l.1330 has several source records for one identity and commitment. l.1289 also names an
  installed record and a catalog package side by side, and does not say whether the two are one candidate
  when their identity and commitment are equal. The count charged to a package name follows from the
  choice. Take a version that is installed and that the catalog lists as two packages for two platforms,
  each from two sources: it is one consideration by identity, two or three by package, and four or five by
  source record. Which material a resolution needs follows from the choice as well. l.1327-1328 can be
  applied only when every acceptable manifest of the version is known, and l.1330 only when its equivalent
  sources are known, while l.1295 forbids requiring the material of a candidate that is not reached. If
  each source record is a candidate, nothing says whether reaching one of them reaches the others.
- **Impact:** with the same installed state, catalog and limits, one Package Manager completes a
  resolution and another fails it with `dependency-unavailable`, against l.1279. When a second source of a
  reached version is unavailable, one fails with `package-unavailable` (l.1308) and another does not.
- **Reading an implementation needs today:** one record per package identity, charged once, and reaching
  an identity examines every catalog source record of it.
- **Overlap:** TF-14 (how depth is counted and whether the root is charged, settled by the text).
- **Suggested resolution:** define the candidate record as one of the three, say whether an installed
  record and a catalog package of equal identity and commitment are one record, and say which source
  records of a version are reached when one of them is.

#### TF-60 — What a root request reports when versions satisfy it and none is eligible is stated only for an unsupported manifest schema
- **Specs:** PM l.1219 ("When a root request other than an `update_package` request without a fixed target
  version has satisfying root candidates and each of them is ineligible only for this reason, the root
  operation MUST fail with `unsupported-manifest`"), l.1320 ("That release is the highest eligible one
  reached in descending order"), l.1335 ("If no complete solution exists, the root operation MUST fail
  with `dependency-unavailable`"), l.1705 ("When neither fixes a target version, Package Manager selects
  the highest available newer normal release"), l.1706 ("If no applicable newer version exists, the
  operation succeeds with the current installed record and changes nothing"), l.1707 ("A newer version
  that is ineligible because its manifest schema is unsupported is not applicable"), l.1500
  ("`incompatible-platform` permits selection of another package version or source with a compatible
  variant"), l.960 (a producer may publish "separately signed packages with the same package identity for
  different platforms").
- **Issue:** a root request without a version takes the highest eligible release (l.1320), so releases
  that are not eligible are passed over. When none is eligible, l.1219 gives the code for one case: each
  candidate is ineligible only because its manifest schema is unsupported. For the other cases nothing
  gives the code: every candidate fails its signature, or has no compatible variant, or the reasons
  differ. The operation may fail with the error of one candidate, and which one is not said, or with
  `dependency-unavailable` (l.1335). For an `update_package` request without a target the same case
  decides between success and failure. The word "applicable" occurs only in l.1706-1707, which make a
  newer version with an unsupported schema not applicable. Whether a newer version that is ineligible for
  another reason is applicable is not said. If it is not, the update succeeds and changes nothing. If it
  is, the update fails. A package whose newer releases no longer carry the host's platform (l.960) is the
  plain case: each newer version is `incompatible-platform`, and an update without a target either reports
  the current record or fails on every call.
- **Impact:** with the same catalog, one Package Manager answers `update_package` with the current
  installed record and another fails it with the error of a newer version. For `install_package` the
  caller receives different codes.
- **Reading an implementation needs today:** an install without a version fails with the error of the
  highest version examined. An update without a target fails with the first such error when no newer
  version is eligible and one of them is ineligible for a reason other than its schema.
- **Overlap:** TF-07 (a call that changes nothing while the retained signer is not accepted).
- **Suggested resolution:** say which code a root request returns when no satisfying root candidate is
  eligible, and define "applicable" for every reason of ineligibility.

#### TF-61 — What an ordinary consumer's own `evaluate` may reveal about the instances and providers its scopes name is not stated
- **Specs:** CA l.1421 ("A provider-access grant for `evaluate` permits an ordinary consumer to request
  evaluation only with itself as `consumer`"), l.76 ("An address used to authenticate a consumer, issue a
  grant to a target, or apply authority MUST resolve to the exact Runtime-known module instance
  concerned"), l.800 (`invalid-request`: "The request violates a rule of this specification that no more
  specific code covers"), l.810 (Capability Authority "MUST establish visibility of that grant or target
  before it evaluates policy for it"), l.74 ("In a grant, `target` names the module instance to which that
  grant applies"), l.1435 ("an unknown grant and a grant hidden from the consumer both produce
  `grant-not-found`"), l.1498 ("Implementations MUST minimize disclosure"); RUNTIME l.428 ("An unknown
  provider or a provider whose complete surface may not be disclosed MUST produce `NOT_AUTHORISED` with a
  non-revealing diagnostic").
- **Issue:** an ordinary consumer may now be granted `evaluate` for itself (l.1421). The limit is on the
  `consumer` field. The scopes of its request may still name providers and module instances other than
  itself, and for an execution scope the module, package and version of an instance. A scope that names
  an address which does not resolve breaks l.76 and is answered `invalid-request` (l.800); one that
  resolves is answered with a decision. The two answers tell the consumer whether the instance or
  provider exists. The visibility rule of l.810 covers "a named grant or target", and a target is the
  target of a grant (l.74), so it does not reach what a scope names. For a grant the text makes unknown
  and hidden equal (l.1435), and Runtime does the same for a provider (RUNTIME l.428). For the subjects of
  an ordinary consumer's evaluation nothing does.
- **Impact:** a module that holds only a grant for `evaluate` learns which instances and providers exist,
  and which module, package and version an instance runs, on one Capability Authority and not on another.
- **Reading an implementation needs today:** for an ordinary caller, a scope that names an instance or a
  provider which that caller may not observe is answered as one that names an unknown one.
- **Overlap:** TF-31 (the refusal of a request that names another consumer, settled by the text).
- **Suggested resolution:** say what an ordinary consumer's evaluation may name, or require one answer
  for an unknown subject and a subject the consumer may not observe.

#### TF-62 — What the exact match of supplied contract references requires for a reference that the source omits is not stated
- **Specs:** INTERFACE l.1717 ("When a package, Runtime input, static registration, or protected built-in
  declaration supplies contract references, its optional primary contract, implemented-interface set, and
  extended-contract set MUST exactly match the validated descriptor"), l.181-183 ("Runtime, package, and
  deployment records MAY mirror resolved implemented-interface identities. They are not required for a
  concrete module to implement an interface"); PM l.1441 (Runtime "MUST require the descriptor's optional
  primary contract, implemented-interface set, and extended-contract set to match the handoff exactly"),
  l.1132 ("The `implements`, `extends`, `requires`, and `requested_permissions` arrays MUST be non-empty
  when present"); RUNTIME l.1349-1350 ("An accepted input may omit `primary_contract`, `implements`, or
  both. When both are absent, the record declares no contract"), l.1455-1456 ("If a record includes
  `primary_contract` or `implements` expectations, Runtime MUST apply the exact call-surface checks
  defined in Section 3.3 before marking the corresponding provider views ready"), l.503-504 ("If an
  expected contract is absent from the validated provider surface or has a different commitment, Runtime
  MUST reject that provider view"), l.2848 ("If `implements` is absent, the runtime is not reporting
  implemented-interface metadata; absence does not assert that the module implements no interfaces"),
  l.399 ("The validated descriptor supplies the exact contract views retained on the Runtime provider
  record"), l.1303 (Runtime "MUST preserve its module name, `primary_contract`, `implements`, `extends`,
  `requires`, and `requested_permissions` without addition or widening").
- **Issue:** a source states `primary_contract` and omits `implements`, and the validated descriptor of
  the provider has interface entries. The same case arises for an omitted `extends` against `extends`
  entries, and for an omitted `primary_contract` against a primary entry. An empty array cannot be written
  (PM l.1132), so one omission must serve both for a source that states an empty set and for a source
  that states nothing. The text supports two readings.
  1. An omitted field states none. The sets differ, the match of l.1717 and PM l.1441 is not exact, and
     the provider does not become ready. RUNTIME l.1350 reads two absent fields this way.
  2. An omitted field states nothing, and only what is stated is compared. INTERFACE l.181-183 make the
     mirroring optional. RUNTIME l.1455-1456 and l.503-504 speak only of the expectations that a record
     includes, and l.2848 says that absence asserts nothing.

  Under the second reading a further point is open: whether the provider then exposes the views that no
  accepted fact names. RUNTIME l.399 takes the views from the descriptor. For a handoff, that exposes a
  contract which the signed declaration does not carry, against l.1303.
- **Impact:** the same host record or installed package starts on one Runtime and fails on another. Where
  it starts, a consumer reaches an interface or an earlier contract of the provider on one Runtime and not
  on another. A tool that writes records or manifests cannot tell whether it must list every implemented
  interface.
- **Reading an implementation needs today:** once a source supplies any contract reference, an omitted
  field states none, so the provider is not exposed unless its descriptor has no entry of that kind.
- **Suggested resolution:** say in INTERFACE l.1717 and PM l.1441 what an absent field states. If it
  states nothing, say which views of the descriptor Runtime exposes for a source that omitted them.

### 3.2 The system contracts, checked against their own rules

The CDDL of Runtime Control (RUNTIME §9.2-§9.3), Configuration (CONFIG §9), Capability Authority, Module
Loader and Package Manager was extracted from the specs, parsed, and checked against INTERFACE §1 and
§2.1, cdCDDLe §5.1 and the structural selection rules. The prose of each spec was compared with its CDDL.

The contract of the Credential Store (CREDENTIAL STORE §3) and its supporting schema (CREDENTIAL STORE
§2.2) were read against INTERFACE §1, cdCDDLe §5.1 and the structural selection rules, and against their
prose. Their C names under INTERFACE §2.1 were not derived.

What came back clean is listed in Appendix F. The items below are what did not.

#### TL-03 — Route states: dependent routes may be drained though no state or rule describes it, and a `ready` route may have lost its invocation path
- **Specs:** RUNTIME l.1886-1891 (`route_state`: `establishing`, `ready`, `revoked`, `failed`, `closed`),
  l.2959-2967 (the meaning of each state; "`revoked`, `failed`, and `closed` are terminal states"),
  l.3203-3204 ("revoke, fail, drain, or close dependent routes according to runtime authority policy"),
  l.3334-3335 ("Connection loss alone need not make the logical route terminal"), l.1264, l.1278
  ("including session failure while the logical route remains ready").
- **Issue:** l.3203-3204 lets Runtime drain a dependent route. `route_state` has no value for a drained
  route (l.1886-1891), and no rule says whether such a route admits new calls, whether it can be renewed,
  or how it ends. `ready` means "usable through its selected invocation path" (l.2962), yet a route can
  stay `ready` after its session is lost (l.3334-3335), and nothing in the record says so. Only the handle
  reports the loss, to its consumer (l.1264, l.1278).
- **Impact:** implementations disagree on what a drained route reports and on when its events stop. An
  observer of route records takes a `ready` route for usable when its session is gone.
- **Overlap:** TF-15 (a `ready` route whose connection was lost), TF-47.
- **Suggested resolution:** remove "drain" from l.3204, or say which state a drained route has and which
  operations it admits. Say at l.2962 that `ready` describes the logical route and not its session, or
  show the loss of the session in the record.

#### TL-04 — The Capability Authority does not say which scopes one evaluation request may combine, or whether a permission scope in a grant stands by itself
- **Specs:** CA §5 l.476-478 (a request may carry several scopes "when the operation requires multiple
  simultaneous constraints, such as module execution plus network and persistent-state permissions"; "An
  evaluation request MUST NOT combine independent operations"), l.548 ("An allow decision MUST list every
  grant on which it depends"), l.214-218 (`permission_scope`), §7 l.785-786 (the meanings of
  `grant-revoked` and `grant-expired`), l.800 (`invalid-request` covers "an evaluation request that
  combines independent operations").
- **Issue:** a request that combines independent operations fails with `invalid-request` (l.478, l.800).
  Which scope kinds one request may combine as a single operation, beyond execution with permissions
  (l.476-477), is not given, so the line between one operation and two is not fixed. A permission scope
  also names no module and no instance (l.214-218), so it is tied to an execution only by standing beside
  an execution scope in one request (l.476-477). Whether a grant that holds a permission scope alone
  applies to every execution its consumer may request, and whether two grants that together cover a
  request allow it (l.548), is not stated as a rule. The meanings of `grant-revoked` and `grant-expired`
  speak of grants that together "would allow every requested scope" (l.785-786), which suggests that
  scopes are covered one by one.
- **Impact:** one CA provider returns `invalid-request` for a combination of scopes that another
  evaluates. One provider applies a permission that was granted by itself to every execution its consumer
  requests, and another only where one grant also names the execution.
- **Overlap:** none.
- **Suggested resolution:** list the scope combinations that one evaluation request may carry. Say also
  whether a permission scope in a grant stands by itself or only beside an execution scope.

#### TL-06 — Records that no method or event reaches sit inside two callable contracts, so changing them changes the contract identity every peer must match
- **Specs:** CA §9.1 l.1273-1288 (`call_evidence_profile`, `evidence_key_id`, the proof and claim
  records), repeated in CA Appendix A l.1896-1911; PM §4.3 l.498 and l.505-508 (`package_signing_key_id`,
  `package_signature_claim`), repeated in PM Appendix A l.1853 and l.1860-1863; COMMITMENT l.271 (every
  local named type is a schema declaration and so part of the root); PM l.236-237 (the manifest has its
  own schema "so a Package Manager API change does not change the schema identity of signed manifests");
  RUNTIME l.2630 ("The Runtime Control contract does not import this schema, so a change to enrollment
  records does not change the Runtime Control contract identity"); BCP l.91.
- **Issue:** six declarations are reachable from no request, response or event of the contract they are
  declared in. They are off-contract formats (two signed payloads with their key identifiers, and the
  profile literal and proof record of one of them), but an edit to any of them changes the Capability
  Authority or Package Manager schema root. The call-evidence profile is an example: replacing the
  signature algorithm of call evidence changes the literal at CA l.1274, and with it the Capability
  Authority contract root, although no method or event of that contract changes. The manifest has exactly
  this separation, and so has the enrollment record (RUNTIME l.2630); the signature claim that signs the
  manifest does not. BCP l.91 keeps the call-evidence definitions out of the shared Runtime types schema
  so that Runtime Control keeps its identity, and they sit in the Capability Authority contract instead.
- **Impact:** needless coupling between signing formats and the contract identities that routes and grants
  pin; offline signers and verifiers must extract a type from a callable module's document.
- **Overlap:** HC-04, C-12.
- **Suggested resolution:** move the two signed-claim types, with the declarations only they use, into
  supporting schemas of their own, as RUNTIME §9.3.7 does for the enrollment record.

#### TL-08 — `execution_state` carries no mark of an accepted execution attempt, so a lost `recover_module` response cannot be settled
- **Specs:** RUNTIME l.1948-1952 (`execution_state` has `revision`, `intent` and an optional
  `intent_revision`), l.3368 (the revision advances "when intent is established, replaced or cancelled, an
  execution attempt is accepted, the local lifecycle state changes, or the failure, retained selection, or
  realization ownership reported by `get_execution_summary` changes"), l.3376 ("Queries can resynchronize
  observation after missed events or uncertain request outcomes"), l.3651 ("retry accounting MUST survive
  orchestration restart and lost responses").
- **Issue:** the state carries no mark of an accepted attempt (l.1948-1952). After a lost `recover_module`
  response, orchestration has only the revision to compare (l.3376), and the revision advances for intent,
  lifecycle-state, failure, selection and realization changes as well as for attempts (l.3368). A changed
  revision therefore does not show that the attempt was accepted, and the retry accounting that l.3651
  requires across lost responses has nothing certain to count.
- **Impact:** after a lost response orchestration cannot tell whether to count an attempt, so a limit on
  attempts is applied differently between implementations.
- **Overlap:** NL-06.
- **Suggested resolution:** add to `execution_state` the revision at which the last execution attempt was
  accepted, so that a lost response can be settled.

### 3.3 The integrator documents against the specs

Two public documents tell integrators what the stack gives them. One is the documentation page "Integrate
Logos into your application" of logos-co/logos-docs, cited as `DOCS l.N`. The other is the appendix
"Integrating the Logos Technology Stack" of logos-co/rfp (PR 206), cited as `RFP l.N`. Of that pull
request, only this appendix was compared. Together they describe the product the specs are meant to
enable. Every claim they make about the runtime, 35 in all, was compared with the specs: 14 are supported,
17 are supported with a limit, 2 are not provided and 2 are contradicted. The comparison is in Appendix D.
The eight items below state where the documents and the specs disagree, and where a documented design
rests on something the specs do not define.

#### TS-01 — The embedding application takes part only as an admitted module instance, and how the host declares that instance and learns that it is ready is left to each implementation
- **Specs:** RUNTIME §13 l.3796-3799 (the Host Embedding API "is not a module contract and does not give
  the host a module-instance or consumer identity"), §13.2 l.3826-3833 (six operations: construct,
  register bindings, start, request shutdown, wait, destroy), l.3837-3838 (start "does not require every
  ordinary module in the deployment to be ready" and completes when "the initial orchestration instance is
  `ready`"), §13.3 l.3899-3901 (`configuration_format` is implementation-defined), l.3914 ("Registration
  alone MUST NOT create a module instance"), l.3934 (registration only before start); Terminology
  l.132-134 ("Every consumer is a module instance"), §9 l.1520, l.1525 ("One program may both host a
  Runtime instance and contain admitted module implementations"), §8 l.1313-1314; App A.1 l.3971-3972
  ("application code that calls modules or receives their events runs as an admitted module instance", and
  "the Host Embedding API does not provide a call surface"); BCP §2 l.102-106.
- **What the specs provide:** protected activation of an application module, as a deployment requirement
  (BCP §5.4 l.389-395: "An activation request is protected deployment input, not a Runtime Control
  invocation or an authenticated module consumer"; "A complete-system deployment MUST realize the
  activated application through its bound Module Loader before application code invokes Logos contracts";
  RUNTIME l.1522-1523, l.1711), and `get_self` (RUNTIME l.2481-2487), which needs a binding. Both confirm
  that an application takes part only as an admitted module, and App A.1 says so for a host that is itself
  the application: its calls "use the Runtime Control binding supplied to that instance at initialization"
  (RUNTIME l.3972). The six host operations include none for activation or for obtaining a binding.
- **Issue:** DOCS l.132-141 and RFP l.435-448 describe an application that is not a module, starts the
  runtime and then calls modules and receives their events. Under the specs every call needs a consumer,
  the host is explicitly not one, and the Host Embedding API has no invoke, subscribe or binding-acquire
  operation. The only conforming shape is that the application registers a consumer-only module of its
  own, has it admitted, and makes its calls as that instance through the binding it received in
  `_MODULE_init` (RUNTIME l.1525, l.3971-3972; INTERFACE l.3642, l.3954). What each implementation must
  then invent: (a) how the host declares that module instance, its `requires` and its permissions (inside
  the opaque `configuration_format`); (b) how the host learns that its instance is `ready`, since start
  waits for the system-service bindings and the initial orchestration instance and for no other module
  (RUNTIME l.3837-3838), and the host has no observation channel that is not itself a module call; (c)
  what the application does when an authorised module stops or retires that instance (INTERFACE l.1962;
  RUNTIME l.595 gives `NOT_READY` on a logically invalidated binding). Today's stack has a non-module host
  caller as a first-class kind, so the specs take away a capability that applications have today.
- **Impact:** the Kotlin, Swift, Go, Dart and Rust host libraries of RFP deliverable 5 each bind one
  implementation's private convention; an application written against one Runtime's host library does not
  move to another. "Your own application code does not need to be implemented as a Logos module" is false
  as written.
- **Overlap:** RT-01 (declined: protected activation, "without a mandatory embedded Runtime or loopback
  transport"), SO-06 and SO-03 (declined), NP-04 (declined).
- **Suggested resolution:** in §13, say that the host may bind its statically registered module to the
  orchestration role (RUNTIME l.178-181: "The orchestration role assigns no canonical module name and does
  not require a provider contract", which is exactly an application that drives lifecycle), in which case
  start returns once that instance is `ready` (l.3838); for any other instance, add a host operation that
  blocks until it is `ready`, and state the instance's lifetime against `stop_module`, `retire_module` and
  shutdown; give a minimal portable record for a statically registered module (name, binding, `requires`,
  requested permissions) even if its carrier stays implementation-defined.

#### TS-02 — A provider's contract set is fixed when it is built, so one generic client module cannot proxy "other module APIs after them"
- **Specs:** INTERFACE §2.6 l.1610-1611 ("The initialization input and returned context are instance
  state. They MUST NOT change the implementation name, provider call-surface descriptor, or exact contract
  set"), l.1682 (the call surface "MUST return the same bytes on every call for one native provider
  implementation binding"), l.1534-1540 (typed per-method functions and dispatch are both mandatory),
  §2.9.2 l.2074-2075 (the asynchronous provider surface "does not replace mandatory typed functions or
  `_MODULE_dispatch()`"); RUNTIME Terminology l.114-117 (a remote-module facade is routing state between
  Runtimes), l.1708; TRANSPORT §9.3 l.1370-1375 (other bindings are not defined).
- **Issue:** RFP l.871-873 intends one proxy module to cover a blockchain's API alongside an execution
  zone's, "and other module APIs after them", rather than one proxy per protocol. The server half is
  possible: it is a consumer making dynamic calls (subject to TS-03). The client half is a provider, and a
  provider cannot take its contract from configuration: the descriptor and the per-method symbols are
  fixed in the artifact. Each proxied contract set therefore needs its own generated and signed client
  artifact. The one provider whose contract does come from deployment input, the remote-module facade, is
  reserved to the Runtime and its own transport profiles. In today's stack the dispatch and the method
  list are computed at run time, which is what the RFP's design relies on.
- **Impact:** RFP deliverables 4 and 6 are one build per transport and per API, not one module per
  transport.
- **Overlap:** HC-07 (no response yet), TS-08.
- **Suggested resolution:** accept this and say so in the RFP; or define a provider form whose
  call-surface descriptor is supplied as accepted deployment input and which exports dispatch only (the
  relaxation TS-08 asks for, which has to cover all three provider surfaces).

#### TS-03 — No JSON (or text) projection of contract values for generic clients
- **Specs:** RUNTIME §4.1 l.774-786 (a binding MAY expose a generic `logos_route_call` "for callers that
  discover schemas at runtime"), §2.4 l.402-404, l.422-432; INTERFACE §4.4 l.3056 (deterministic CBOR
  only), §5.3 l.3967 (dynamic schema text may be used for "user presentation"), App A.6 l.4156-4164 (UI
  bindings are "derived views", details out of scope), §1.7 l.457 (choice arms are selected structurally),
  l.471-473 (a contract may carry an external encoding in `bstr` or `tstr`). In the thirteen files the
  word JSON occurs only for the SLSA envelope (PM l.616-623) and in two sentences about what CDDL is.
- **Issue:** every client that is not generated code turns typed values into text and back: the JSON-RPC
  server and client module pair of RFP l.804-819, which is meant to carry "other module APIs after them"
  and whose two paths "must express the same semantics" (RFP l.875-879); a command-line tool; the
  JavaScript SDK (DOCS l.167); QML and web views. The projection has real choices: `bstr` as hex or
  base64; 64-bit integers above 2^53; an absent optional field versus `null`; tuples; and choices, where
  the JSON-to-CBOR direction needs the schema and a rule. Two independently written bridges for the same
  contract will not interoperate. The manifest has no defined text rendering either: only `manifest.cbor`,
  `manifest.cose` and `variants/` may appear at the archive root (PM l.904), and the owner's answer to
  PM-09 leaves human-readable inspection to "consumer tools".
- **Impact:** a JSON-RPC client module from one vendor cannot talk to a server module from another; a call
  recorded by one tool cannot be replayed by another.
- **Overlap:** ND-06, ND-01, ND-07 (all declined: no JSON type, no wide-integer type, no common error
  record).
- **Suggested resolution:** an informative annex in INTERFACE (or a small named profile) defining one JSON
  rendering of schema-typed values and its inverse under a given schema, stated to carry no commitment
  meaning: objects for maps, arrays for lists and tuples, base16 for `bstr`, numbers up to 2^53-1 and
  decimal strings above, absent for absent, arm selection by the existing structural rules.

#### TS-04 — The remote profiles fix one authenticated connection per route and one per consumer for control; a session can be reused only by the same route
- **Specs:** TRANSPORT §8.4.1 l.1274-1275 ("One authenticated connection carries one such provider
  session"; "The connection MUST close when that provider session ends"), l.1281-1283 (no session
  resumption, no early data), §8.4.2 l.1300-1302 (one QUIC connection, one session, no further application
  streams); RUNTIME l.2782-2786 ("A caller that requires another provider or route MUST establish another
  session"), §9 l.1698-1699 (a remote Runtime Control connection is used "only for that consumer"), l.868
  (a route exposes one exact contract), l.742 (materialization "MAY reuse a live session bound to the same
  consumer, route, provider, and exact selected contract"), l.3337-3338 (renewal leaves the live session
  on its old decision; a replacement session needs "its fresh ticket").
- **Issue:** between the same two enrolled Runtimes, every route of every consumer module is a separate
  TCP or QUIC connection with a full mutual TLS 1.3 handshake, and each consumer module needs its own
  control connection to establish or renew. Renewal and any session loss mean a control round trip plus
  another full handshake. DOCS l.222 says connection scale is left "to each deployment"; the profile
  leaves nothing to choose. The cost is per route and not per call: several asynchronous calls can be
  outstanding through one route handle (RUNTIME l.1285).
- **Impact:** a phone using three contract views of a home node holds three provider connections plus one
  control connection per consuming module; an operator serving many applications carries at least one
  connection per user per contract. QUIC's stream multiplexing is unused by rule.
- **Overlap:** NR-11 (resolved by the asynchronous call API), NR-06 (resolved: no live rebind), NR-08 and
  NR-07 (declined).
- **Suggested resolution:** either state the cost as an accepted property, or define a separately
  specified profile (RUNTIME l.3340 anticipates one for updating live sessions) with one authenticated
  Runtime-pair connection that carries several provider sessions (each redeeming its own ticket and bound
  to the same exporter value; one QUIC stream per session) and several consumers' control traffic.

#### TS-05 — Publisher-level trust is prohibited: every package name needs its own entry in protected trust input
- **Specs:** PM §4.1 l.413-419 (the trust input "MUST also bind each accepted signer to a non-empty set of
  exact package names"; it "MUST NOT use case folding, Unicode normalization, prefixes, wildcard patterns,
  or an authorization covering every package name"), l.420 ("Adding an exact package name to an accepted
  signer's set is a change of protected trust input and requires a later trust revision"), l.443-444
  ("Package material, catalog metadata, Storage content, and Nix metadata MUST NOT add, replace, or
  reactivate a package-signing trust anchor"), l.401 (the trust configuration, including "exact-name
  authorization", is under a monotonically ordered revision), §4.3 l.539 (the signer record "does not
  identify a publisher or assert current trust"), §15 l.1526-1533 (no method changes trust input).
- **Issue:** DOCS l.104 promises "Logos's own keys are trusted by default, users can add the publishers
  they trust", and DOCS l.105 an ecosystem where "other developers' modules can depend on yours". Under
  §4.1 a signer is never trusted as a publisher: it is trusted for an enumerated list of package names
  that lives in protected input. A user who trusts a publisher must re-approve each new package name that
  publisher ships, and each approval is a new protected trust revision (l.420); the default Logos anchor
  must list every Logos package by name and be re-issued when one is added; a third-party package cannot
  be installed on any device until that device's protected input names it, and neither the catalog nor the
  package may supply the name binding.
- **Impact:** the open catalogue the documents describe needs a per-device, per-package provisioning step
  that no specified operation performs; adding a publisher cannot be offered as one action.
- **Overlap:** NI-06 and NP-10 (resolved: the verified signer is retained, and trust input has continuity
  rules), SO-03 (declined), HC-01.
- **Suggested resolution:** keep exact-name binding as the baseline, and define how the binding is
  extended without editing deployment files: a Package Manager (or Runtime Control) method, gated by a
  Capability Authority scope, that adds an exact package name to an accepted signer's set as a later trust
  revision (PM l.401-404), with the change audited; optionally a signer-signed name list that a deployment
  may accept for a signer it already trusts, with collision rules when two accepted signers claim one
  name.

#### TS-06 — No Package Manager method returns the contract documents that a package carries
- **Specs:** PM §4 l.253-260 (`contract_documents` maps a commitment to the `schema` artifact of its
  document and to the artifacts of its interface and supporting documents), l.355-358 ("Package Manager
  MUST construct the schema root from those documents of the selected variant and MUST fail with
  `invalid-package` when it differs from the commitment"), §6 l.846-851 (an inspection record carries the
  signer, the source, the manifest and its commitment), §10 l.1155-1160, l.1181 (an installed artifact has
  a `local_path`, which "is an installation location, not a guaranteed module-visible path"), l.1186 ("The
  Runtime handoff and Interface initialization input do not provide a package-root directory or artifact
  lookup table"), §12 l.1420, §15 l.1526-1533 (no method returns contract documents); INTERFACE §5.2
  l.3904-3906 (the sources of the documents that materialize a route); RUNTIME §2.4 l.396, l.422-432, §3.6
  l.684-685 and SECURITY l.172-174 (loading a library to inspect it is not allowed).
- **Issue:** DOCS l.137 and l.229 have clients "generated from each module's contract" and say every
  module "publishes its contract as a CDDL schema". A package can carry the documents: a
  `contract_documents` entry ties a commitment to the `schema` artifacts that reproduce it, and the
  Package Manager recomputes the root (PM l.356-358). A developer who holds the package can read them from
  it. A module cannot. An inspection returns the manifest, which names the artifacts and their hashes and
  not their content (PM l.846-851). For an installed package the record gives a `local_path` that is "an
  installation location, not a guaranteed module-visible path" (l.1181). A store page that wants to show a
  package's API therefore gets the text only from a realized provider, through `describe_provider`, or out
  of band (RUNTIME l.422-432; INTERFACE l.3904-3905).
- **Impact:** a module can list the contracts of a package by commitment and cannot show or use their
  definitions; each implementation adds its own way to read package artifacts.
- **Overlap:** IF-10 (resolved: the sources of route construction input are listed), SO-10 (section 1),
  ND-09, NP-01 and SO-01 (declined).
- **Suggested resolution:** a Package Manager method that returns the documents of a `contract_documents`
  entry for an installed or inspected package, as the handoff already does for the configuration schema
  (PM l.1420: "The handoff MUST contain the schema document and default value rather than their package
  artifact identifiers").

#### TS-07 — Interchangeable providers: which of two providers of the same contract a caller gets is undefined
- **Specs:** COMMITMENT §9.1 l.951-957 (the schema root object holds the commitment-model revision, the
  schema namespace, the declarations and the implemented-interface roots, and no module name or document
  role), §4 l.520-521 ("Schema identity uses schema namespaces and qualified schema definition names, not
  runtime module names"); INTERFACE l.1689 (the `primary` document's `_module` must equal the module's own
  name), l.304-307; RUNTIME l.862-863, l.2025-2031 (`establish_route` selects by `contract`, never by
  module name), l.1367-1369 ("A provider requirement matches every provider that exposes a validated
  contract view with the required schema root, independently of module name"; "Accepted provider selection
  and execution policy remain responsible for choosing an allowed implementation"), l.1402 ("deployment
  pinning"), l.1406-1409 ("This specification does not define an ordering among equivalent matching
  providers"), l.1424 (a `single` request never selects a provider hidden from the consumer); CA
  l.166-180.
- **Issue:** RFP l.811-819 requires a client module that "implements the same IPC interface as the module
  it proxies" so that the two are interchangeable to callers. This works: two modules with different
  `_module` names whose primary documents have the same namespace, the same declarations and the same
  implemented interfaces have the same schema root, and a requirement for that contract matches both
  (RUNTIME l.1368). Three things the RFP design needs remain undefined: which provider a `single` request
  gets when both are present (RUNTIME l.1408-1409); how a deployment pins one ("Accepted provider
  selection" has no record, l.1369, and a consumer can only name a provider by a Runtime-minted address);
  and how a policy tells the node from the proxy, since a `provider_access_scope` for the contract covers
  both unless `providers` is listed (CA l.177).
- **Impact:** the RFP's design is sound against the specs, but which of the two providers a caller reaches
  is each implementation's choice; and a module needs no name collision to stand in for another module's
  contract.
- **Overlap:** HC-01, NF-22 (declined: no universal role names or resolver), RT-04 (resolved for the
  choice of package per module name only).
- **Suggested resolution:** define the provider-preference input for `single` selection as a protected
  record keyed by contract commitment and module name (or package identity), and say that without one a
  request matching several providers fails rather than picking arbitrarily, as `create_module` already
  does for declarations (RUNTIME l.3486: "If active policy does not select one accepted declaration, the
  request MUST fail").

#### TS-08 — Static registration from a managed language must still supply every per-method C symbol (addendum to HC-07)
- **Specs:** INTERFACE §2.6 l.1534-1540 ("Provider modules MUST expose both surfaces"), l.1724 (a direct
  ABI caller MAY call the per-method functions), §2.9.2 l.2074-2075; RUNTIME §13.3 l.3907-3910 ("The table
  MUST include every symbol required for the implementation, including schema-derived per-method symbols
  when applicable"), l.3916-3919 (a missing per-method symbol is detected at implementation binding, not
  at registration), §1.2 l.271-272.
- **Issue:** an application that serves calls from Kotlin, Swift, Go or JavaScript (RFP l.484-486:
  "Provider hosting ... This is the barrier") registers a binding whose table must contain, for every
  method, a C function with the canonical struct layouts of INTERFACE §2, although the natural bridge for
  those languages is the single dispatch entry point carrying CBOR. The typed functions must work, because
  a direct caller is allowed to use them. The optional asynchronous provider descriptor is a third surface
  and replaces neither.
- **Impact:** each language SDK must generate and compile per-method C trampolines for every contract; the
  "universal string and JSON interface" the RFP relies on today (RFP l.489-490) has no counterpart.
- **Overlap:** HC-07 (no response yet).
- **Suggested resolution:** let a binding or call-surface descriptor declare that it is dispatch-only, in
  which case the per-method symbols are absent and every caller uses dispatch; say how that combines with
  `_MODULE_async_api()`.

### 3.4 Porting the existing module catalog

The modules of the current release catalog were read for what they need from the platform. The needs are
stated here with neutral roles (consumer C, provider P, a lower provider Q, a presentation module),
because what matters to the specification is the shape of a need and not which module has it. Twenty needs
that recur across the catalog are compared with the specs in Appendix E. The verdict words are `core gap`
(Core must define something), `profile` (the need is assigned to a platform, deployment or presentation
profile that does not exist yet), `contract` (the module can carry it in its own contract, at the stated
cost) and `policy` (a deployment policy or configuration matter).

The seven items below take more than a table row to state. Where the same module recurs, it keeps its
letter: C is a consumer, P a provider that C uses, Q a lower provider that P runs on, and R a provider
that holds keys. A and B stand for other modules and are local to one item.

#### TP-01 — A shared provider that its consumers create, configure and start
- **Need:** Consumer C creates a node inside provider P with C's own configuration. If P refuses because
  the node exists, C reads the node's state, starts it and records that it adopted a node which another
  module created. C's source notes that P's lifecycle should belong to the host application and not to a
  consumer. P in turn creates and configures a lower provider Q, laying its own settings over the
  operator's configuration, because Q replaces its options wholesale on each create call. Three further
  consumers operate on the one session that a presentation module opened in provider R. Another
  presentation module stops and destroys a node it finds running.
- **In the specs:** application-level setup through ordinary schema methods is sanctioned (RUNTIME
  l.611-612), so a create method that takes a configuration and a start method can stay contract methods.
  Core configuration is the other route and has the opposite shape: one complete value per instance with
  "no field patch, implicit merge, or partially applied configuration value" (CONFIG l.53-54; "No source
  implicitly merges with another source", l.132), never starting or stopping anything (l.57), and without
  credentials (l.58; the node configurations of two providers in the catalog contain a private key). A
  provider can identify its caller (INTERFACE l.2140-2141), so a rule that the first caller owns the node
  can be enforced by the provider's own contract instead of being a race. Core does not arbitrate between
  consumers, and nothing tells a consumer which configuration the provider runs with. Key parameters can
  be marked `_sensitive` (INTERFACE l.211-212).
- **Verdict:** `contract` if the create and start methods are kept (the first caller wins, with an owner
  check, and the overlay logic stays in the module); `policy` if node configuration moves to Core
  configuration (then a consumer cannot parametrise a shared provider, and P's overlay onto Q has no
  equivalent). The port has to pick one per provider. The integrator SDK documents' description of
  composing modules assumes the second.
- **See:** HC-03, NC-05, NP-14.

#### TP-02 — Requests from a provider to its consumers, carried as events plus a respond method
- **Need:** Provider P emits a request event that carries a request identifier. Whichever consumer listens
  answers through a respond method that takes the identifier and the answer, and the first answer wins.
  The lower provider Q lets another module mount a protocol on the shared node. Inbound streams for that
  protocol wait in a queue until the module long-polls them through an accept method that takes the
  protocol and a timeout, or they arrive as an event.
- **In the specs:** two prohibitions apply: "modules MUST NOT model request/reply flows through events"
  (RUNTIME l.1168-1169) and "A callee MUST NOT require an Event message as a reply path for a method
  invocation" (TRANSPORT l.822-823). P's pattern is the one the second forbids, in the reverse direction:
  the request is the event and the reply is the method. Three shapes conform:
  1. An inversion of roles. The provider declares `requires` on an interface contract that the handler
     implements, and calls it. P already does this where the handler runs in P's own process.
  2. A long-poll issued as a prepared asynchronous call with a timeout and cancellation (INTERFACE l.2016,
     l.2024). The prepared call does not occupy its route handle (RUNTIME l.1285-1286). This fits Q's
     accept method with its timeout as it is. Issued through the synchronous `call`, the long-poll
     occupies its handle until it returns, because a caller must serialise operations on one route handle
     (INTERFACE l.1935).
  3. A work-item resource owned by the contract and observed through a watch method. The handler keeps a
     watch invocation open, the provider publishes invocation-scoped notifications that only that
     handler's path receives (RUNTIME l.1177-1179), and the handler completes each item through a method
     (TRANSPORT l.836-838). This removes the rule that the first listener to answer wins. Whether this
     shape is itself a request/reply flow through events in the sense of RUNTIME l.1169 is open. Every
     watch that the specs themselves define is notification-only (CA l.976-984; PM l.1738). A notification
     that work is available, answered by a completing method, is not, and no text places the boundary.
- **Verdict:** `contract`. Q's accept long-poll ports nearly as it is (shape 2). P's request-event case
  needs redesign: role inversion makes every handler a provider that needs its own grants, and shape 3
  avoids that if the owner accepts it.
- **See:** HC-02 (no pattern for a consumer to register a handler), NE-04.

#### TP-03 — Files and directories shared between modules
- **Need:** Module A writes a configuration file under its own state directory for provider R, and A's
  presentation module passes that path and a storage path to R's open method. A presentation module writes
  its log files into its backend's directory, which it finds through a method that returns the path. A
  storage provider keeps its repository under one fixed directory in the user's home directory, so that
  every consumer uses the same repository. A presentation module reads a node's log, key store and
  configuration by path. Another presentation module writes a provider's configuration under its own data
  directory and passes the absolute path.
- **In the specs:** "Distinct module instances MUST NOT share a state assignment by default. Shared
  persistent state requires an explicit deployment or policy rule" (RUNTIME l.1383-1384). A `state_dir`
  "does not imply authority to access any host path or another module instance's state" (l.1396). Sharing
  is named only as a facility that a permission profile would define (CA l.398), and no such profile
  exists. The specs state the consequence directly: "A filesystem path does not grant access or guarantee
  visibility in another module's realization" (RUNTIME l.3776) and "Co-location alone does not establish a
  shared filesystem namespace" (l.3783), which is the assumption the fixed home-directory path rests on.
  Methods that take paths are allowed, with a duty: the contract "MUST define whose namespace it addresses
  and the applicable failure when that namespace or access is unavailable" (l.3784; INTERFACE l.2146-2147
  likewise leaves the meaning of such a value to the contract that carries it). The Credential Store (BCP
  l.201) is for credentials in deployment-assigned slots and gives nothing for a shared file.
- **Verdict:** `profile` (a shared-state permission, SO-05) where a file really must be shared; otherwise
  `contract`: pass content, not paths (HC-08), and give each module its own state.
- **See:** HC-08, SO-05, NC-04, NC-06.

#### TP-04 — Metrics: the BCP's own example ports, without floats and without structural matching
- **Need:** A metrics collector pulls on every scrape from a set of modules that the operator lists. For
  each module it calls one of two collection methods, one returning structured samples and one returning
  rendered exposition text, and it labels the samples with the module's name. Any module that happens to
  have a method of the matching shape qualifies; no module declares that it is a source. A module
  implements either method. Sample values are floats, including `NaN` and `+Inf`.
- **In the specs:** this is the case BCP §4 walks through ("a concrete storage module may implement a
  metrics-provider interface", l.228). The collector declares `requires` on a metrics interface with
  cardinality `all-runtime-visible` and gets one route per visible provider (RUNTIME l.1411-1414). Each
  `route_record` carries the provider's `module` name (l.2014), so the label needs no extra observation
  grant. Three things do not carry over. Floats are reserved (INTERFACE l.466), and a float anywhere in a
  transported payload "is a Transport validation failure" (INTERFACE l.3093) that closes the connection
  (TRANSPORT l.406-407), not a schema rejection, so samples travel as exposition text or decimal strings
  and must never reach the wire as floats. Conformance is declared, not structural ("This revision does
  not define interface inheritance, interface composition, default methods, method remapping, or
  structural duck typing", INTERFACE l.186-187), so every source module must implement the interface by
  exact reference: in `_implements` of its primary document, or in its module binding when it has none
  (INTERFACE l.572, l.692). And a module that implements either method becomes a module that implements
  one of two interfaces.
- **Verdict:** `contract`. The operator's module list becomes the provider constraint of the `discover`
  decision (`policy`).
- **See:** ND-01, IF-01, NL-12.

#### TP-05 — A dependency between two modules that runs over loopback HTTP
- **Need:** Module A reads finalised state from the node that module B runs, through a loopback HTTP
  address in A's configuration, while A's package declares no dependencies. Another module talks plain
  HTTP to a separately run service.
- **In the specs:** such a dependency is invisible to the Runtime: no `requires`, no ordering constraint
  (ordering exists only as a deployment-supplied constraint, RUNTIME l.705), no route authority, no
  commitment or audit. It works only while both modules share a network namespace, which `sandbox`,
  `container` and remote placement do not guarantee. The integrator SDK documents describe the intended
  shape: a node depends on another node as a module dependency, and a client reaches its node only through
  the node's interface. The only spec hook for the loopback shape is a profile-defined network permission
  (CA l.396), and the owner's response to SO-05 is that no registry of such permissions is added.
- **Verdict:** `contract` (declare `requires` on a node contract and take the stream of finalised blocks
  as events, within the frame limit of TP-06); if the HTTP path is kept, `profile` (SO-05) plus a
  deployment ordering constraint.
- **See:** SO-05, ND-03.

#### TP-06 — Per-message calls and large messages against mandatory encoding, commitment and the frame limit
- **Need:** Provider P validates or generates a proof for every message through another module. Consumer C
  receives every message of P's node as an event. A storage provider can deliver download chunks as
  events. The lower provider Q declares a 64 MiB message ceiling.
- **In the specs:** every request, successful response and event is encoded as deterministic CBOR and has
  a payload commitment computed from the typed value at the Runtime boundary, in every mode and whether or
  not anything retains it (RUNTIME l.1665-1666, l.794; INTERFACE l.3863; SECURITY l.505-506). The only
  latitude is the optimisation rule, which may not bypass validation (RUNTIME l.3099), and no profile that
  would skip the computation is assigned (BCP l.347). A stream binding accepts at least 16 MiB, and a
  sender uses 16 MiB unless a larger limit is separately established (TRANSPORT l.371, l.378). The failure
  is defined: an oversized Request "MUST fail its local invocation with `MODULE_ERROR`", an oversized
  Response becomes a `response-err`, and an oversized Event closes the subscriber's connection when its
  publication boundary cannot report the failure (l.379-383), which is the case for the ordinary publish
  callback, whose result "does not report delivery to any subscriber" (INTERFACE l.3351-3352; RUNTIME
  l.1149-1150). "These stream limits do not impose a new direct-mode payload limit" (TRANSPORT l.387). So
  a 64 MiB message crosses a direct route, and a transported one only where the deployment configures a
  larger limit. The specs accept that difference: a schema-valid value whose message exceeds the limit
  fails "even when the same call succeeds in direct mode", and that failure "reports a resource limit and
  does not change the meaning of the contract's results" (TRANSPORT l.374). A contract whose values can
  exceed the limit "should bound them with `.size` or transfer them in parts" (l.375), which is the port's
  way out for an unbounded `bstr`.
- **Verdict:** not a defect, but a cost the port must measure for the per-message and large-message data
  paths; `contract` for the chunking (SO-09). The specs could assign a profile that skips commitment
  computation on a direct route when no policy requires retention; none is assigned.
- **See:** ND-03, SO-09, NE-05.

#### TP-07 — Package dependency ranges and exact pins
- **Need:** Consumer C requires provider P at an open lower bound (a given version or any later one). A
  presentation module requires provider R at an open lower bound that only the newer of two shipped
  versions of R satisfies. Three consumers pin R exactly at the older version, while the same release set
  ships the newer one.
- **In the specs:** a requirement is `exact` or `compatible`, the latter a caret range (PM l.299,
  l.1224-1226); an open lower bound has no form. A dependency may also list the contracts it needs from
  the package, and a candidate that does not provide them is ineligible (l.1214-1216). Two closures may
  install two versions of one package (l.1343-1344), which here means two declarations of R's module name.
  Which one `create_module` picks is a matter of protected deployment policy (RT-04): policy must select
  one declaration and pin the exact package and version, the request carries no selector, and creation
  fails when policy does not select (RUNTIME l.3481-3491; BCP l.372). Routes select exact contracts
  (RUNTIME l.3043). The shared session of TP-01 survives in one instance of the newer R in two cases: the
  two contract roots are identical, or the newer contract extends the older one, which may only add
  declarations, and R offers the older contract as an exact contract view (INTERFACE l.201-204; RUNTIME
  l.1344-1347). A release inside the `compatible` range of an earlier release "MUST provide every contract
  that the earlier release provides" (PM l.1236), but "Package Manager does not verify these producer
  obligations across releases" (l.1239). In every other case consumers built against the older and the
  newer contract of R need two instances of R.
- **Verdict:** `policy` for the ranges (use `compatible`) and for the pin of R's declaration. The exact
  pins have to be relaxed before the port, and the newer release of R has to provide the older contract;
  otherwise the set carries two packages of R and two sessions.
- **See:** PM-15, RT-04, NF-17.

### 3.5 Editorial

#### TF-06 — Editorial
- "A module binding identifies one runtime module name, its optional primary document, and its implemented
  interface set" (INTERFACE l.572), so a provider can implement interfaces without having a primary
  contract. Three passages do not fit that:
  - INTERFACE l.77 says each CDDL-authored concrete module "MUST have a single `.cddl` file that contains
    the canonical CDDL representation of its primary module contract".
  - The binding has no authored form on the CDDL side ("no additional schema document, serialized format,
    or authored sidecar file is required", INTERFACE l.2590). A CDDL-first interface-only provider
    therefore states its implemented set only to its tool, the descriptor and the manifest.
  - A types-only primary is carried in a `provider-contract-schema` entry although INTERFACE l.1524 says
    it is not a provider contract.
- `TIMEOUT` is assigned for a prepared call: "expiration of the caller-selected duration produces
  `TIMEOUT`" (INTERFACE l.2024), and "Expiration of any other deadline imposed on that invocation also
  produces `TIMEOUT`" (l.2025). Both sentences stand among the rules for calls made through
  `prepare_call`. "Applicable policy, route lifetime and execution-envelope failure may still end delivery
  earlier" (l.2019), and RUNTIME l.3123 leaves "In-flight call behavior, timeout policy, idle expiry, and
  retry policy" to the profile or implementation. Whether l.2025 also gives the code of a synchronous
  `call`, which takes no timeout, when such a policy deadline ends it is left to inference.
- BCP §5.4 l.403-404 places two requirements on the use of four mechanisms: "development trust anchors,
  relaxed debugging entitlements, implementation-local Transport test hooks under LOGOS-MODULE-TRANSPORT
  Section 8.5, or unknown-artifact analysis". Only the Transport test hooks are defined (TRANSPORT §8.5).
  "relaxed debugging entitlements" and "unknown-artifact analysis" appear elsewhere only in one bullet of
  SECURITY (l.533), and a development trust anchor enters "through the same protected trust-input path" as
  any other (PM l.449). When a deployment owes the non-production designation of BCP l.404 is therefore
  left to its own judgement. Saying what each of the three is would settle it.
- INTERFACE l.1485 forbids release "from an event or terminal callback for that handle". Direct
  publication is a re-entrancy boundary (l.1924), so a module can reach `release` from code that is not
  the handler, such as a provider method entered while the handler's frame is still on that thread's
  stack. Read narrowly, that release is not made from the callback, and it waits for "active event
  handlers" (l.1484), including the frame beneath it. The unsubscription rule is stated by the stack: it
  applies "while a handler invocation of that subscription is active on the calling thread" (l.1424).
  Stating the release rule the same way, by a handler frame of that handle being active on the calling
  thread, would remove the doubt.
- INTERFACE l.2155-2157, on the invocation context's `publish`: "Malformed identifiers or payloads produce
  `INVALID_PARAMS`" (l.2155), and "otherwise a closed invocation destination produces `NOT_READY`"
  (l.2157). The order between the two is left open. The order of checks in RUNTIME l.1824 covers "a
  Runtime Control invocation or an ordinary provider call", and this operation is neither.
- RUNTIME l.185 has the orchestration module apply startup defaults "using conditional start or stop
  requests as defined in Section 9.3". Section 9.3 defines the field (`expected_execution_revision`,
  l.2156); the comparison rule is in §9.1 (l.1727-1728). What a startup default is, is defined nowhere.
- BCP l.267 labels `logos.remote.tls-tcp` "Mandatory remote transport" in the identifier table. The
  requirement is l.341: "Mandatory for an implementation supporting production remote Runtime transport".
  The label lacks that condition.
- RUNTIME l.3299-3300: a Runtime that implements no remote transport profile has no stated answer to a
  valid `set_remote_listener` that enables a listener. It may be `TRANSPORT_ERROR` "when the failure is in
  transport setup", or `MODULE_ERROR` under l.3300. A request that disables a listener asks nothing of the
  transport: "Remote listeners and provider exports MUST be disabled by default" (l.2769), and the method
  "idempotently assigns the requested listener state" (l.3289). Whether a listener in that default state
  has a record, which `list_remote_listeners` returns and an export can name (l.3309), is not said.
- LOADER l.258: "graceful release, and the fixed hosted-provider Transport profile are required behavior".
  Read alone, the sentence binds a Loader that advertises no hosted strategy, which l.252-255 allow.
- TRANSPORT l.1100: "The directory mode MUST be `0700` on POSIX filesystems". If a deployment gives each
  Module Host an operating-system identity of its own, to meet l.1088-1090, a consumer under another
  identity cannot reach the socket by its path (l.1110).
- BCP l.389 binds "A deployment supporting external application activation", and the term is not defined:
  whether a command sent to a module instance that is already running is an activation is open. BCP l.404
  asks for a non-production notice in "operator-facing diagnostics", which is not defined either.
- Whether LOADER strategies and hosted placements are profiles for BCP l.316, l.352 and l.428 is not said.
  BCP l.301 defines a named Core profile as "a complete, interoperable behavior selected by a stable
  identifier", which could cover them; the matrix of §5.3 omits them; LOADER has its own rule (l.377).
- PM l.402-403 are passive ("The accepted high-water state MUST survive ordinary restart"; "Older state or
  different contents at the same revision MUST be rejected") and name no component that keeps the mark.
  Whether the Package Manager keeps it itself or may rely on its host is open.
- TRANSPORT l.1101: Runtime "MUST NOT follow, remove, or replace a symbolic link or another filesystem
  object at that path". Who clears an endpoint path left by a Runtime that ended without cleanup is not
  said.
- RUNTIME describes local transport mode in three sentences, none with a requirement keyword. Two put the
  consumer's end of the provider session in the process that holds the route handle: "The handle wraps a
  local transport connection to the selected provider" (l.734-735), and "the process-local invocation
  boundary uses only the invocation material bound to that route and translates typed calls into
  LOGOS-MODULE-TRANSPORT messages" (l.1255). The third names the Runtime as the Transport peer of a hosted
  provider: "Runtime communicates with the process-local invocation boundary over LOGOS-MODULE-TRANSPORT"
  (l.1007). The same specification leaves the layout open: "Any carrier between a Module Host and the
  owning Runtime is realization-internal machinery rather than an ordinary provider route" (l.890), and
  "If Runtime, a process-local invocation boundary, or a facade provider remains on the invocation path,
  that is an implementation property of the selected provider or descriptor" (l.2949-2950). A Runtime that
  holds a hosted consumer's provider session itself, and exchanges each call with the Module Host over
  that carrier, fits l.890, l.1007 and l.2949-2950 and not l.734-735 or l.1255. Whether those two
  sentences describe one permitted layout or the required one is left to inference. Saying that they
  describe one permitted layout would settle it.
- CA l.1370: "Sensitive evidence requires confidentiality-protected transport and storage." The sentence
  has no requirement keyword and names no component, and sensitive evidence is not defined. SECURITY l.368
  says of all call evidence "Its disclosure and storage still require confidentiality protection and audit
  authority", also without a keyword. Evidence of a marked payload cannot exist, because its commitment is
  never retained: "Runtime MUST reject the invocation with `NOT_AUTHORISED` before dispatch rather than
  retain it or omit the policy requirement" (INTERFACE l.377). What a store of evidence can hold is the
  retained roots of unmarked payloads and the optional proofs (CA l.1287). Of such a root SECURITY l.403
  says "An observer who knows the schema can test guessed values against an exposed commitment". Whether a
  file that only its owner can read is confidentiality-protected storage, or encryption at rest is meant,
  is not said: "This specification does not define a second encrypted evidence format" (CA l.1371). Saying
  which evidence is sensitive, which component protects it and with which keyword would settle it.
- BCP l.372 asks the deployment document for "accepted-declaration selection and exact package/version
  pinning for package-backed module creation". Whether "for package-backed module creation" qualifies both
  parts or only the pinning is not said. A deployment that creates no package-backed instance owes the
  first part under one reading and nothing under the other.
- BCP l.380: "The documentation MUST also identify Package Manager installation and inventory scope,
  shared-state coordination, and the protected administration of required operating-system integration
  material". Whether "Package Manager" governs the first element alone or all three is not said. A
  deployment without a Package Manager owes the last two under one reading and nothing under the other.
- CA l.393 requires a profile that permits operating-system or platform access to define permission names
  and constraints "for every facility it exposes". CA l.394 then says "Relevant facilities include:" and
  lists seven classes (l.396-402). Whether a profile must tell those classes apart, or the list is an
  illustration, is not said. A profile with one permission that stands for every class meets l.393 under
  one reading and fails it under the other.
- RUNTIME l.1672: "Runtime MUST produce the `call` audit record defined by
  LOGOS-MODULE-CAPABILITY-AUTHORITY", when the applied decision requires retention. The record is produced
  "after the corresponding enforcement outcome" (CA l.1218), so a Runtime that then cannot build or store
  it cannot fail the call. No rule says what it does. CA names an outcome for the record of an evaluation:
  "If required retention cannot be acknowledged, Capability Authority MUST fail closed without an allow or
  deny decision" (CA l.1210). For a grant issuance it names one for one cause only, a record that would
  retain unauthorized sensitive constraint values: the request fails "with `authority-unavailable` without
  issuing a grant or grant denial" (CA l.1389). BCP l.560 says "When mandatory audit cannot be satisfied,
  the owning audit failure rules continue to apply", and for a record that cannot be stored there is none
  for the call record, nor for the records of grant issuance, revocation, expiry and policy change (CA
  l.1197-1198). "Retention duration and storage realization are deployment or audit-profile policy" (CA
  l.1202) covers where records go, not what follows when one is lost. Whether the Runtime then refuses
  later calls that need retention, or only notes the loss, is left to each implementation. One sentence in
  CA §9 would settle it.
- PM l.1638: "A deployment MUST establish compatible protected invocation integration and observation
  policy before exposing Package Manager queries." The authority that this policy grants is not defined.
  PM l.1645 speaks of "the corresponding observation authority", and PM l.1646 says "method invocation
  permission alone MUST NOT imply record visibility", which rules out the permission to call the method.
  CA gives observation a scope for Runtime Control, "`runtime_control_scope` covers calls, observations,
  and subscriptions under the Runtime Control contract exposed by one Runtime instance" (CA l.294-295),
  and none for package records. Whether the visibility of a package record is meant to be a Capability
  Authority scope or a rule kept outside it is not said; PM l.1642 calls it "an additional deployment
  requirement". Naming the scope, or saying that none is intended, would settle it.
- PM l.1462 says of the module facts and artifacts that protected deployment input supplies for the
  initial Package Manager and Storage providers: "Provisioning these inputs does not itself create
  installed package records or establish Package Manager verification." A module supplied that way
  therefore has no installed record, and a package that declares a dependency on it is served from a
  catalog source or fails: "an LGX operation can resolve a dependency only from a satisfying installed
  package" (PM l.1355). PM l.829 speaks of "restoring state". Whether an installed record can exist that
  no `install_package` or `update_package` call created, and which verification makes it one, is not said.
- RUNTIME l.2657: "Public-key rotation uses a higher active revision containing both old and new keys
  during overlap." An enrollment names one trust anchor (RUNTIME l.2617), and when the peer's certificate
  is itself that anchor, "The direct-anchor case requires equality with the provisioned certificate's
  complete DER encoding" (TRANSPORT l.1244). A certificate for the new key is a different certificate, so
  a Runtime whose certificate is directly anchored cannot present both keys under one enrollment. It can
  rotate without an overlap, or leave direct anchoring for a certificate chain, whose non-anchor
  certificates need revocation evidence (TRANSPORT l.1250). Which is intended for the direct-anchor case
  is not said.
- TRANSPORT l.1137: "Endpoint-use permission alone MUST NOT grant consumers permission to delete, rename,
  replace, or change security on the endpoint or its containing directory." Whether this binds when the
  consumers run under the Runtime's own operating-system identity is not said. For every platform
  TRANSPORT l.1088 says "A shared operating-system user identity is not an isolation boundary between
  processes of that identity", and l.1090 lays the protection from such processes only on "A deployment
  claiming protection from such processes". On POSIX the rule is a directory of mode `0700` (l.1100), in
  which a consumer of the same identity can delete or replace the socket. Read with those lines, l.1137
  separates the right to use an endpoint from the other rights where a consumer is a different principal.
  Read alone, it asks on Windows for a separation inside one identity that the POSIX rule does not ask
  for. Saying which is meant would settle it.
- TRANSPORT l.1151: "A Windows implementation MUST establish the peer-query attribution and
  listener-sharing behavior of its supported operating-system versions and placements before claiming
  support." What counts as one version is not said: a release, a build number, or each servicing update,
  which can replace the component that answers the peer query. TRANSPORT l.1146 requires that the
  process's "operating-system identity MUST satisfy the expected Runtime identity", and what that identity
  is on Windows is not said either: the user alone, or also the elevation and the integrity level of the
  process's token, in which two processes of one user can differ. The same holds for the ownership that
  TRANSPORT l.1106 has the Runtime validate: an object created under an administrator's elevated token is
  owned by a group by default, and which owner the validation expects is not said.
- INTERFACE l.3904-3907 names three sources for the contract documents that a first route handle needs:
  documents that the caller carries, a `describe_provider` response, and an earlier `logos.schema`
  response, of which l.3907 says "The caller does not need a call to `logos.schema` to materialize its
  first handle." A `logos.schema` request needs a handle already. `describe_provider` answers for the
  whole provider or not at all: "An unknown provider or a provider whose complete surface may not be
  disclosed MUST produce `NOT_AUTHORISED` with a non-revealing diagnostic." (RUNTIME l.428). So a consumer
  that may discover and call one contract of a provider, for example one implemented interface, and that
  carries no documents, has no way to obtain the documents of that contract. A general-purpose consumer,
  such as a command-line tool, is in that position whenever its grant is narrower than the provider's
  whole surface. A Runtime Control method that returns the documents of one selected contract would settle
  it.
- INTERFACE l.2262 has "The fixed common-header and allowed standard-header includes remain governed by
  Section 3.1", and Section 3.1 names no standard header; the three that `logos_types.h` itself includes
  (l.3373-3375) are the natural set. INTERFACE l.612 lets file-level include guards differ, and l.2289
  says "Contract-header dependency includes and the mapping, context, and document identity checks MUST
  remain outside any enclosing guard that could suppress their evaluation." A guard around a whole file
  encloses every include and check in it. The two sentences are met together only by a guard that begins
  after the includes and the checks, which neither sentence says. INTERFACE l.2299 says "A C contract MUST
  include `logos_types.h` rather than redeclare a fixed common type", while l.2180 calls its declarations
  "available to every C contract". Whether a header that uses those names and has no include is a
  conforming input is not said.
- INTERFACE l.2296 defines a namespace group as "the complete set of schema-derived declarations assigned
  to one exact schema namespace". Whether that set may be divided among several header bodies of one
  input, or each body's share is an incomplete group (l.2339), is not said.
- INTERFACE l.2570 recovers the module name "from a consistent lifecycle symbol family conforming to
  Sections 2.1 and 2.6". Section 2.6 says which symbols an implementation makes available (l.1514,
  l.1526). Which declarations a hand-written header must contain for the family to be consistent is not
  said: the three identity and lifecycle symbols, or also the three provider symbols when the module is a
  provider; nor whether a provider symbol in the header of a module that is not a provider is an error.
  INTERFACE l.31: "Both paths MUST produce identical artifacts for the same logical contract and module
  binding, if any." What an artifact is, is not said, and l.2599 lets the CDDL text of the two paths
  differ in comments, whitespace, order and file layout.
- TRANSPORT l.1282-1283: "The full mutual-authentication handshake MUST complete before either peer sends
  Logos Transport application data." In TLS 1.3 the client's handshake is complete when it has verified
  the server and sent its own Finished, and the server verifies the client's certificate only after that.
  The caller speaks first, and TLS 1.3 gives the client no message that says its certificate was accepted.
  TRANSPORT l.1224-1225 has each peer validate the other "before sending or accepting a Transport Hello",
  which the caller meets when it sends its Hello right after its Finished. Whether l.1282-1283 allows
  that, or the caller must wait for a sign from the server that the profile does not define, is not said.
  TRANSPORT l.1222 says "Protected enrollment MUST select credential and certificate-signature algorithms
  supported by the intended peers", and l.1223 calls a P-256 credential "a common enrollment option".
  Which signature schemes every implementation of the profile verifies is not said, and the enrollment
  record has no field for a scheme (RUNTIME l.2611-2627).
- TRANSPORT l.1236 has the key of an inbound caller checked against all enrollments: "the accepted public
  key MUST match exactly one active enrollment under this profile." TRANSPORT l.1237 then fails "multiple
  Runtime identity matches". A caller selects the target's enrollment by the expected Runtime identity
  (l.1229-1231), so it matches by identity and not by key. Whether a caller also fails when the target's
  key is held by the active enrollment of another Runtime is not said.
- RUNTIME l.3613 and l.3665: a dependent's `failure` is required only while its prerequisite "is not ready
  and has no execution attempt in progress", and orchestration's `recover_module` duty covers only
  "required permissions or eligible configuration"; who resumes the dependent's retained intent once the
  prerequisite becomes ready, and what the dependent's start does while the prerequisite's attempt is in
  progress, is not said.
- RUNTIME l.3665 against CA l.369: l.3665 speaks of "deployment intent initially blocked by missing
  permissions or configuration", while "A declared permission that those settings omit is denied and does
  not by itself prevent execution"; which condition a block by missing permissions names (an authority
  decision that does not cover the scopes mapped from the saved settings, or something else) is not said.
- RUNTIME l.370: the ABI caller "MUST NOT unmap the code of a direct dynamic binding while its hosting
  process continues to run, including after destruction has returned for every context and when the
  implementation was rejected before a context was created", so every replaced or rejected direct-dynamic
  artifact stays mapped for the life of the process, and no bound or documentation duty covers that
  growth.
- INTERFACE l.3308-3309 ("Provider code MAY return or complete with `LOGOS_OK`,
  `LOGOS_ERR_METHOD_NOT_FOUND`, `LOGOS_ERR_INVALID_PARAMS`, or `LOGOS_ERR_MODULE`"; "any other status code
  violates these rules") does not say whether the list covers only method invocations: INTERFACE
  l.3837-3838 requires `_MODULE_init` to "return `LOGOS_ERR_VERSION_MISMATCH` and a null context", and
  CONFIG l.288 and l.323 give "A valid nonzero application-hook result" the meaning of a rejection without
  saying which codes are valid, so a hook that returns `LOGOS_ERR_NOT_READY` is either a rejection or an
  indeterminate outcome that puts the instance in `error`.
- RUNTIME l.3096 ("When the renewal authority check denies the route, Runtime MUST place the route in
  `revoked` state with failure code `authority-denied`") covers a denial only; for a renewal whose
  authority evaluation fails (RUNTIME l.1651: "An authority-evaluation failure occurs when Runtime cannot
  obtain or validate a required authority decision") nothing says whether the route stays `ready` under
  its earlier decision or is failed with `authority-evaluation-failed` (RUNTIME l.2427), and no rule
  places a route in a terminal state with that code.
- INTERFACE l.1406 ("the binding MUST queue that delivery with a copy of its event data instead of
  waiting") does not say whether a queued delivery is admitted when it is queued or when its handler
  begins; RUNTIME l.1196-1200 makes admission the commitment point of a direct delivery ("For direct
  delivery, it means admission of an individual subscriber callback"; "No new scoped-event commitment is
  permitted after terminal Response commitment or processed cancellation"), so whether an
  invocation-scoped event queued before the terminal Response and run after it is delivered, and at which
  of the two moments its delivery is authorized, is open.
- RUNTIME l.3836 against l.3839 and l.1555: successful startup "MUST establish the initial system-service
  bindings required by Section 9", yet the binding of "the selected initial Capability Authority", which
  orchestration establishes, "is not part of startup", so l.3836 holds only for the bindings that
  protected input establishes.
- RUNTIME l.3634 against l.3606 and l.3635: a Runtime that starts after an unclean end reports every
  preserved instance last recorded as `loaded`, `ready` or `stopping` as `error` with `host-terminated`, a
  classification that "means that the realization's execution envelope, or the Runtime process containing
  it, ended without cleanup ordered by Runtime"; for a hosted realization whose envelope lies outside the
  Runtime process and is not yet confirmed ended (l.3635), neither has happened.
- RUNTIME l.3635 and l.3683: after a Runtime restart the confirmation required is that "the previous
  execution envelope has ended" (l.3635), while after the loss of a Loader it is that "the old execution
  envelope and its access to assigned state have ended" (l.3683); whether the confirmation after a restart
  also has to cover access to assigned state is not said.
- PM l.1686 and RUNTIME l.3384-3386: Package Manager "MUST atomically replace the retained
  `package_signer` with the newly verified signer" (PM l.1686), while Runtime reports "the exact verified
  signer retained with a package-backed selection" (RUNTIME l.3384) and keeps it bound to the selection
  across restarts (RUNTIME l.3386); whether the retained selection of an existing instance follows the
  replacement, and whether a later handoff that carries the replaced signer matches that selection, is not
  said.
- RUNTIME l.1423-1424 and CA l.249: a `single` request "does not require a separate `discover` decision"
  (RUNTIME l.1423), yet "Runtime MUST NOT select for a `single` request a provider that active visibility
  policy hides from the consumer" (RUNTIME l.1424); under an externalized policy the one decision that
  expresses visibility is `discover` ("A `discover` allow decision permits Runtime to disclose providers
  matching the exact `contract`", CA l.249), so which decision tells Runtime that a provider is hidden,
  when none is required, is not said.
- RUNTIME l.3317 and l.3351: where a listener or a provider export is disabled, and where a route is
  closed, "In-flight call behavior follows the in-flight call policy of this section"; neither Section
  9.3.15 nor Section 9.3.16 states such a policy, and the one sentence on the subject, in Section 9.3.14,
  leaves it to "profile or implementation policy" (RUNTIME l.3123).
- INTERFACE l.853-854 and l.2592-2598: "Tooling implementing this mapping MUST document its
  identifier-length and resource limits" (l.853) stands in Section 2.1, where the mapping is the one from
  CDDL to C. Section 3 has no sentence on the limits of a reverse mapper, and its guarantee holds "For any
  conformant CDDL schema `S`" (l.2592). Whether a reverse mapper may refuse, at a documented limit, the
  header that the forward mapping generates for a schema set within the limits of Section 5.3 is not said,
  and no limit of a tool has a floor.
- TRANSPORT l.417 against RUNTIME l.122-126: Transport assigns payload validation to "the schema-aware
  sending and receiving boundaries" (TRANSPORT l.417) and uses the term again at l.640, l.642, l.662 and
  l.1170, and no text ties it to the three boundaries that RUNTIME defines (l.122-126). That a facade
  provider which stays on the invocation path (RUNTIME l.2949) must hold the contract's schema follows
  only from its ending a session.
- HASH l.1236 and l.1251: "In steps 3 and 4, the schema selected by the typed path is a list of `uint16`
  values in B.1 and a byte string in B.2" (l.1236), while the path of B.1 selects one element, since the
  view "discloses the `uint16` value `256`" (l.1251); the list is the schema against which step 3
  validates the path, and the element is the schema that the path selects for step 4.
- INTERFACE l.4010 and l.4046-4089: the appendix is headed "Appendix A. Generated Artifacts (Informative)"
  (l.4010) and uses requirement keywords at l.4046-4047, l.4082-4083 and l.4087-4089, for instance "A
  handwritten implementation MUST behave as if derived from the same exposed contract set." (l.4047); each
  restates a rule of a normative section, so the keywords add nothing and read as requirements under an
  informative heading.
- RUNTIME l.2515 against l.1819: for `update_permission_settings`, "Failures before acceptance use the
  shared invocation-error channel." (l.2515), and a stale `expected_revision` is such a failure (l.2511),
  which l.1819 sends to the typed `stale-revision` error; l.2515 needs that exception.
- RUNTIME l.1816 against l.1809: the sentence lists "a prohibited lifecycle operation" among the caller
  errors and then calls "the `NOT_READY` conditions" Runtime-owned readiness failures; the prohibited
  lifecycle operation is a `NOT_READY` row of the table (l.1809), so it is classified twice.
- RUNTIME l.3614 against l.3615 and l.2436: "A facade unavailable because current remote state cannot be
  established MUST use `remote-state-unknown` rather than infer a remote crash." (l.3614) also describes a
  facade whose target Runtime cannot be reached, for which `remote-unreachable` is defined (l.3615,
  l.2436) and which l.3199 and l.3604 require to be kept distinct; l.3614 should yield to a more specific
  classification.
- PM l.1311-1312 against l.1279 and l.1314-1315: "Package Manager MAY exclude a catalog candidate before
  obtaining its material when implementation-defined catalog metadata indicates that the candidate has no
  variant compatible with the target execution environment." (l.1311). The exclusion is optional and its
  input is implementation-defined, while counters and resolution are to be determined by "the installed
  state, catalog inputs, and protected policy" (l.1279). A Package Manager that does not exclude the
  candidate charges it and needs its material (l.1262-1263, l.1308), so two Package Managers can resolve
  the same catalog differently, and a catalog entry has no field that tells a resolver which package
  serves its platform (l.841-844).
- INTERFACE l.1479 and RUNTIME l.3589: Runtime delivers Runtime Control state events "only while the
  authenticated subscriber remains authorized to observe the referenced module, provider, or route"
  (RUNTIME l.3589), and a binding ends a subscription with `NOT_AUTHORISED` "when authority to receive the
  event has ended or can no longer be established" (INTERFACE l.1479); whether a subscriber that loses
  authority over every record it could observe keeps a silent subscription or has it ended is not said.
  RUNTIME requires the end only for a route subscription (l.951). Under an externalized policy Runtime
  "MUST terminate dependent provider sessions and subscriptions when their continued use would exceed
  current authority" (CA l.944) after a grant is revoked or expires, and no text says that this reaches a
  Runtime Control subscription.
- INTERFACE l.1481-1482: "An end that occurs while no registration is installed is not reported later"
  (l.1481) and "`unsubscribe` for a binding-ended subscription returns `LOGOS_OK`" (l.1482), so a
  subscriber that registers `observe_subscription_end` after subscribing has no operation that tells an
  ended subscription from an active one; no text requires or advises registering first, whereas
  `observe_end` on an already-terminal handle returns the retained code (INTERFACE l.1459).
- CREDENTIAL STORE l.132-134 against CA l.417-421 and l.1421: "The protected invocation integration MUST
  evaluate the original authenticated caller's permission for the exact operation and assignment" names an
  integration that no specification defines, although a permission enforced by a module provider "MUST
  define how the authenticated enforcing provider obtains the applicable authorization for the checked
  subject, resource, and operation", and an ordinary consumer may request `evaluate` "only with itself as
  `consumer`".
- TRANSPORT l.374 against l.379-380 and INTERFACE l.3308: the size failure is said to report "a resource
  limit", but the assigned code is `MODULE_ERROR` "without validation detail", which provider code may
  also return, so a caller cannot tell a frame-limit failure from a provider failure.
- PM l.357 against l.365 and l.1079-1082: contract-document artifacts "MUST exist in every package
  variant", but the `invalid-package` list of §8 names only artifacts referenced by a module declaration,
  so it is not stated whether a `contract_documents` entry whose artifact a variant does not declare fails
  with `invalid-package` or with `artifact-integrity-failed`.
- RUNTIME l.863 and l.398 against l.2852 and l.2995: the selected contract is defined as "the exact
  concrete module contract or implemented interface contract" and provider validation as covering "the
  complete primary/implemented-interface set", both of which omit the extended contract that a route may
  select.
- INTERFACE l.3351: the publish callback returns `INVALID_PARAMS` when the event data does not conform "to
  that event's data type and size limits"; the term occurs only there, and which size limits of an event
  it means is not said. A destination's limit is not among them, because "A failure for an individual
  subscriber route does not change that result" (RUNTIME l.1149) and an event over the limit of a
  Transport destination follows TRANSPORT §2.1 for that destination (RUNTIME l.1150).
- INTERFACE l.2926-2936: the header set printed for the dotted and underscored namespaces holds an
  interface document and a supporting document that do not reference each other, and l.2936 requires the
  mapper to "reconstruct each document when it is selected as the subject and supplied with exactly its
  required dependency set"; the printed set is that input for neither subject, and whether the mapper
  rejects the printed set as a whole is not said (l.2349 names only "a supporting-schema group supplied as
  a dependency but not referenced").
- RUNTIME l.285: "Module names MUST NOT contain `_call_` or `_publish_`; those substrings are reserved."
  What they are reserved for is not said: a method symbol is `logos_<module-C>_CALL_<namespace>_<Method>`
  (INTERFACE l.706) and the names of helpers are "implementation-defined" (INTERFACE l.858).
- TRANSPORT l.731 and l.755: l.731 gives a failed SubscriptionResult with `INVALID_PARAMS` to an
  Unsubscribe naming no active subscription, and l.755 gives a successful SubscriptionResult to an
  Unsubscribe for a subscription that the callee ended with a SubscriptionEnd, which is no longer active;
  which sentence governs is not said.
- PM l.905-907 and l.306: a variant may declare no artifacts (`artifacts: [* ...]`), `variants/` must
  contain one directory per manifest variant, and an entry may be omitted only when descendants imply it;
  whether such a variant needs an explicit directory entry is left to inference.
- PM l.1185 against l.340-341 and l.1188-1189: a packaged native library is a declared artifact, but no
  artifact kind is assigned to it. `module-binary` is the kind required of an implementation artifact that
  a module declaration references, and `resource` and `data` authorize no execution.
- INTERFACE l.3075 and l.3079 against l.1542 and RUNTIME l.813: an implementation must "Reject incoming
  CBOR that violates the determinism rules in Section 4.4 with error code `INVALID_PARAMS`" (l.3075) and
  "Reject unknown method names -> error code `METHOD_NOT_FOUND`" (l.3079), and the list states no order.
  On a Transport connection the order follows from TRANSPORT l.403-405, because a message that fails
  envelope validation is not dispatched. For a request that reaches a direct provider no text orders the
  two: "A method outside the selected contract produces `METHOD_NOT_FOUND`" (RUNTIME l.813), and a
  provider that declares no methods "MUST return `LOGOS_ERR_METHOD_NOT_FOUND` for every method argument"
  (INTERFACE l.1542), which reads as the name being checked first. A request that names an unknown method
  and carries bytes that are not Logos deterministic CBOR can therefore receive either code.
- INTERFACE l.1477 against l.1448, l.1452 and l.1459: `observe_subscription_end` "follows the registration
  rules of `observe_end`: one registration, no synchronous invocation on the registering thread,
  `INVALID_PARAMS` for a null handler or a second registration, and `MODULE_ERROR` for unavailable
  registration capacity" (l.1477). The list names four of the rules that `observe_end` has, and whether
  the others apply is not said: that the binding orders installation with the reported transition
  (l.1448), that "A failed registration MUST NOT invoke or retain the supplied callback state or alter an
  existing registration" (l.1452), and that "Registration on an already-terminal handle returns that code
  without installing a registration or invoking its callback" (l.1459). A binding therefore has to choose
  what `observe_subscription_end` returns on a route handle that is already terminal.
- INTERFACE l.2974 against l.583 and l.3402-3408: "Generated headers MUST preserve the specified
  discriminant width in the supported C and C++ modes, including when compiler options alter enum storage"
  (l.2974), while "Compiler options that change enumeration storage are outside the supported native ABI"
  (l.583), and the common header, which every generated header includes, now asserts at compile time that
  "logos_error_code_t must have the size of int" (l.3404). Under such an option no generated header
  compiles, so the last clause of l.2974 names a condition in which the headers cannot be used. Whether
  that clause is to be dropped, or read as requiring only that a discriminant is never an enumeration, is
  not said.
- TRANSPORT l.753 and RUNTIME l.951 against INTERFACE l.1479 and CA l.941: the callee ends a subscription
  "when the caller's authority to receive that event ends while the route remains usable; this revision
  defines no other cause" (TRANSPORT l.753), and Runtime ends it "When the consumer's authority to receive
  an event of an active subscription ends" (RUNTIME l.951). The binding's reason is `NOT_AUTHORISED` "when
  authority to receive the event has ended or can no longer be established" (INTERFACE l.1479). Whether a
  decision that cannot be obtained for one event counts as authority that ends, so that the callee commits
  a SubscriptionEnd, or the event is withheld and the subscription continues with a gap, is not said. The
  corresponding rule for a route keeps the route: "If the evaluation fails, the route MUST remain unusable
  for protected operations until a later evaluation reauthorizes it" (CA l.941).
- INTERFACE l.1474 against l.1454 and RUNTIME l.1264: a binding-ended subscription is one that ends "for a
  reason other than unsubscription, the terminal state of its route, or release of its binding or handle"
  (l.1474). A handle's invocation path can end "while its route remains `ready`" (RUNTIME l.1264), and
  then "the binding MUST stop admission of new event handlers" (INTERFACE l.1454). Its subscriptions end
  for none of the three excluded reasons, so by the letter each is a binding-ended subscription that the
  binding reports, although the terminal observer already reports the end of the handle. Whether the
  exclusion means the terminal state of the handle's invocation path is not said.
- INTERFACE l.2155-2156 against TRANSPORT l.75 and l.719: for invocation-scoped publication "Malformed
  identifiers or payloads produce `INVALID_PARAMS`" (l.2155), and "An event identifier that does not
  satisfy Section 1.5, including its namespace and `_event` suffix, is malformed" (l.2156). No sentence
  says the same of the `event_name` given to `subscribe`. On the wire such a name is valid for the
  envelope, which asks only for a text of 1 to 128 bytes (TRANSPORT l.75), and it falls under "An event
  name outside the selected contract", which produces `NOT_AUTHORISED` (TRANSPORT l.719). A binding that
  checks the name itself answers `INVALID_PARAMS` and one that forwards it answers `NOT_AUTHORISED`, so
  the code a consumer sees for the same name can differ by execution mode unless every binding checks
  first.
- TRANSPORT l.755 against l.972, and INTERFACE l.1482 against RUNTIME l.1261-1262: "An Unsubscribe for a
  subscription that the callee has ended with a SubscriptionEnd MUST produce a successful
  SubscriptionResult" (TRANSPORT l.755), while "A Subscribe or Unsubscribe processed during termination
  MUST receive a failed SubscriptionResult with `NOT_AUTHORISED` and MUST NOT change subscription state"
  (l.972). Which sentence governs an Unsubscribe for an ended subscription that is processed during
  termination is not said. The binding has the same pair: "`unsubscribe` for a binding-ended subscription
  returns `LOGOS_OK`" (INTERFACE l.1482), and once the route has ended a new operation through its handle
  reports the route's cause (RUNTIME l.1261-1262).
- INTERFACE l.1405 against l.1402, l.1406 and l.1920: no rule covers a nested direct publication made by
  the thread that runs the active invocation while deliveries from other threads wait in that
  subscription's queue. Re-entry at once (l.1405: "Same-thread handler re-entry is permitted only when an
  action during a callback synchronously causes nested direct publication for the same subscription")
  begins its handler before the queued deliveries that were published earlier, against l.1402 ("handler
  invocations MUST begin in direct publication order"). Queuing it lets its publish call return before
  its callback completes, which l.1920 allows only for "a delivery queued under Section 2.5", and l.1406
  queues only a delivery that reaches "a subscription whose handler invocation is active on another
  thread". Whether the nested publication runs the waiting deliveries first, inside its own call, and
  then its own, is not said.
- INTERFACE l.1478 against l.1465-1466: of the route-end callback the text says that it "does not imply
  that already admitted event handlers or asynchronous call completions have returned" (l.1465) and that
  it "imposes no ordering between their execution and the terminal callback" (l.1466). Of the
  subscription-end callback it says only that the binding "MUST stop admitting handler invocations for
  that subscription and invoke the registered callback exactly once" (l.1478). Whether that callback may
  run while an already admitted handler invocation of the same subscription is still active is not said;
  it must, if a reached pending-delivery bound is to be reported before the handler that caused it
  returns.
- INTERFACE l.1954 against l.1592 and l.3955: before `_MODULE_destroy()` the ABI caller "MUST also
  suppress every subscription-end callback of the initialization Runtime Control binding that has not
  begun and wait for an active one to return" (l.1954), and that binding stays valid "from
  `_MODULE_init()` entry until `_MODULE_destroy()` returns" (l.1592). A module may subscribe and register
  for subscription ends while it initializes ("The module MAY invoke authorized Runtime Control methods
  through that binding during `_MODULE_init()`", l.3955), and a failed initialization has no destroy. No
  sentence says when the binding of a failed initialization stops being valid, or that its
  subscription-end callbacks that have not begun are suppressed then and an active one is waited for.
- RUNTIME l.2704 against l.2703 and l.1896: "If `profile` is present, it MUST match the profile selected
  by `transport`" (l.2704), and the schema allows the field on a `unix-stream` address ("? profile:
  logos.runtime_control.address_profile", l.1896). Selection is stated for two transports only:
  "`tls-tcp` selects `logos.remote.tls-tcp` and `quic` selects `logos.remote.quic`" (l.2703). No sentence
  says which profile `unix-stream` selects, so a `profile` on such an address can be judged neither a
  match nor a mismatch.
- RUNTIME l.2704 against INTERFACE l.3876 and RUNTIME l.225: the rejection is stated for "a Runtime
  Control request that carries a mismatching address" (l.2704). `connect_remote` takes a
  `runtime_endpoint` too, and it is "the `connect_remote` operation defined by LOGOS-MODULE-INTERFACE"
  (RUNTIME l.225), not a request of the contract. Its own list of rejections without detail names an
  endpoint that "omits the required Runtime identity, selects a non-remote address, or names the
  consumer's owning Runtime" (INTERFACE l.3876) and not an address whose `profile` contradicts its
  transport, so the code and the detail for that endpoint are not said.
- RUNTIME l.2704 against l.1824-1833: the order of checks has no place for the mismatching address. It is
  not "request payload decoding and schema validation" (l.1828), whose failures carry detail, and it is
  not among "the conditions of an applicable precondition table" (l.1831). Whether it is reported before
  or after the target authorization of the fourth step and the revision comparison of the fifth is not
  said.
- RUNTIME l.2933 and l.2464 against l.1824-1833: an unordered or duplicate list is rejected "with
  `INVALID_PARAMS` without validation detail" (l.2933 for a `route_access` list, l.2464 for a permission
  array). Like the mismatching address of l.2704, the rejection depends on the request alone, is not a
  schema-validation failure and is not a row of the precondition table, so the order of checks does not
  place it.
- RUNTIME l.1822 against l.1824-1833: "`declaration-unavailable` is produced only by `create_module`,
  after the conditions of the precondition table" (l.1822) places the error after the sixth step of the
  order. `stale-revision` has an item of its own in the list ("comparison of an expected revision, which
  produces `stale-revision`", l.1830) and `declaration-unavailable` has none, so whether it is reported
  before or after "Runtime-owned readiness not covered by such a table" (l.1832) is not said. The two
  differ for a Runtime that is shutting down.
- RUNTIME l.1829 against l.3041, l.3074 and l.3090: the fourth step is "target authorization and
  non-disclosure checks that depend on the decoded request" (l.1829). For `establish_route` the
  provider-access decision is separate from the authority to invoke the method ("Authority to invoke
  `establish_route` does not itself grant provider access", l.3041), and `renew_route` "performs a new
  authority check" (l.3090). Whether those decisions are the target authorization of the fourth step or
  part of the operation is not said. If they are the fourth step, a reused `request_key`, which is the
  second row of the table and so the sixth step, is judged only after a decision has been evaluated, and
  a repeated request, which "MUST return that result" (l.3074), is preceded by a decision that may now
  deny.
- RUNTIME l.2929-2930 against l.1824-1833: "Runtime MUST reject a route request containing a declaration
  root" (l.2929) "that is neither valid under the selected contract nor an allowed well-known method
  root" (l.2930) names no code, and the check needs the selected provider's contract, so it cannot be
  made with the payload's own validation. Whether it is the eighth step ("comparison of an expected
  contract or schema root not covered by such a table", l.1833), and so follows Runtime-owned readiness,
  is not said.
- RUNTIME l.1824-1828 against l.1641, l.1257 and TRANSPORT l.640: the order of checks puts
  "authorization of the consumer, method, and route access that does not depend on the decoded request
  payload" (l.1827) before "request payload decoding and schema validation" (l.1828), for "a Runtime
  Control invocation or an ordinary provider call" (l.1824). For a transported call "The schema-aware
  sending boundary MUST compute the commitment from the validated schema-typed value" (TRANSPORT l.640),
  so the caller's side validates before the request is sent, while the call is authorized by the
  provider's Runtime "Before dispatching an ordinary provider method" (RUNTIME l.1641). A malformed
  request to a method that the call decision denies is then rejected for its payload when transported and
  for its authority when direct, although "The typed call helper exposes the same method inputs, outputs,
  and errors in every mode" (RUNTIME l.1257). At which boundary each step of the order is taken is not
  said.
- RUNTIME l.3056 against l.3031 and l.3019: "The consumer's Runtime follows it with a new `single`
  request selecting that target provider" (l.3056) is stated of every continuation. For a response that
  reaches a module through its `connect_remote` binding, "the module may follow a continuation with a new
  `single` request through a binding to the continuation target" (l.3031), and Runtime resolves
  internally only "When handling acquisition for a local module consumer" (l.3019). Read alone, l.3056
  says that the module's Runtime follows that continuation as well.
- RUNTIME l.3732 against l.3729 and l.3705: "At expiry of the shutdown deadline, Runtime MUST initiate
  release of every realization whose release it has not yet initiated" (l.3732). A Module Loader that
  still owns a realization whose cleanup is unresolved is such a realization, yet "Runtime MUST release
  Loader-owned realizations before quiescing and releasing or detaching their owning Loader provider"
  (l.3729), and "A shared-process native realization MUST NOT be force-released by destroying referenced
  state or unloading code that can still execute" (l.3705). Whether the Loader's own release is initiated
  at expiry while a realization it owns is still `stopping` is not said.
- RUNTIME l.1733-1734 against l.577: "A `stop_module` request for an instance in `error` transitions it
  to `stopping`" (l.1733), and "When cleanup of a previous realization is still unresolved, Runtime MUST
  NOT initiate another destruction or release, and the stop completes when that cleanup completes"
  (l.1734). When the instance is in `error` because that cleanup has already failed, nothing completes it
  while its execution envelope lives, and "A cleanup failure during an explicit stop transitions the
  instance to `error`" (l.577) speaks of a failure during the stop. Whether such an instance stays
  `stopping` until its envelope ends or returns to `error` is not said.
- RUNTIME l.3611 against l.526 and l.523: Runtime clears the classification "when a new execution attempt
  is accepted or an explicit stop completes successfully" (l.3611). Runtime shutdown also takes an
  instance from `error` to `stopping` (l.526) and on to `unloaded` when its cleanup completes (l.523).
  Whether the classification is kept on an instance that a shutdown, and not an explicit stop, took from
  `error` to `unloaded` is not said.
- RUNTIME l.3939 against l.3955 and l.3613: "If an instance that startup realizes fails before it becomes
  `ready`, startup MUST return `LOGOS_ERR_MODULE`, or `LOGOS_ERR_TIMEOUT` when the cause is expiry of its
  startup deadline" (l.3939), and "Other failures MUST use the applicable shared error code" (l.3955). An
  initial orchestration instance whose start is refused, because its execution is denied, its
  configuration is missing or its static binding does not match, is never realized and stays `unloaded`
  with a `failure` (l.3613). Whether that is an instance that "fails before it becomes `ready`", so that
  startup returns `LOGOS_ERR_MODULE` for a denial as well, or another failure with its own code, is not
  said.
- PM l.1296-1298 against l.1305 and l.1323: Package Manager "MUST check each dependency candidate reached
  under the required candidate order and resolver limits against the installed record for its exact
  package identity" (l.1296); a differing commitment fails the root operation (l.1297) and "MUST NOT be
  skipped or resolved by backtracking to another version" (l.1298). A commitment that a recorded edge
  excludes "is not a satisfying candidate" (l.1305), so a catalog package of an installed version with
  another commitment is never checked once the package that carries the edge has been assigned. Names are
  taken "first in UTF-8 byte order" (l.1323). The same installed state and catalog therefore resolve when
  the name of the package that carries the edge sorts first, and fail under l.1297 when the pinned name
  does. Whether the conflict is meant to depend on that order is not said.
- PM l.1503 against l.933 and l.1100: `artifact-integrity-failed` means that required artifact bytes "were
  absent, escaped their realization root, or did not match the signed digest" (l.1503). The term
  "realization root" occurs only there. l.933 has Package Manager verify that the resolved destination of
  an extracted entry "remains within the selected installation root" and assigns no code to a failure, and
  l.1100 assigns the code when the resolved location of a manifest artifact path "lies outside its variant
  directory or realized output". Whether a destination outside the installation root is the case of
  l.1100, and which of the three containers the realization root is, is not said.
- PM l.1688 against l.1292, l.1301, l.437 and l.542: the retained signer is replaced only for "the package
  identity named by the request and not to installed dependencies in its closure" (l.1688). A candidate's
  signature "MUST validate under an accepted trust anchor" (l.1292), an installed candidate "MAY satisfy a
  dependency without being materialized again" (l.1301), and after an anchor is removed Package Manager
  "MUST NOT use it for a new successful resolution, installation, update, or Runtime handoff" (l.437). For
  an installed dependency whose retained signer is no longer accepted, while the catalog offers the same
  identity and commitment under an accepted signer, it is not said whether the dependency is satisfied,
  nor whether the operation reports success while the handoff of that dependency still reports the
  withdrawn signer (l.542).
- PM l.1260 against l.1257: "When an added dependency edge increases the depth of a package name already
  in the partial closure, Package Manager MUST verify the depth limit for that name and for the names it
  requires" (l.1260). Depth is "the greatest number of manifest dependency edges on any path from the root
  to that name in the partial closure" (l.1257), so the edge also raises the depth of every name reached
  through those names. Whether "the names it requires" covers them, and whether it covers a required name
  that has no assigned candidate yet, is not said; the readings end a resolution at different points.
- PM l.1302 against l.1301, l.1303 and l.821: "If Package Manager finds that retained artifact bytes of an
  installed candidate are absent or do not match the signed digest, the root operation MUST fail with
  `artifact-integrity-failed`" (l.1302). Package Manager "MUST retain the selected artifact bytes while
  their installed record remains present" (l.821), and an installed candidate may satisfy a dependency
  "without being materialized again" (l.1301). Whether reaching an installed candidate requires Package
  Manager to read its retained bytes is not said, so the same damaged store fails a resolution on one
  Package Manager and not on another. The order of that check against the ineligibility of the same
  record, which "MUST NOT be treated as an ineligible candidate" (l.1303), is not given either.
- CONFIG l.299 against l.300, l.218 and l.291: "No staged record exists, or either applicable binding is
  absent or does not declare live reconfiguration" gives `INVALID_PARAMS` (l.299), ahead of "The module
  instance is not `ready`, or another live-reconfiguration attempt is in progress" with `NOT_READY`
  (l.300). The two bindings are "its accepted binding and the binding used to initialize the current
  realization" (l.218). An instance that was never started, or was stopped, has no current realization
  and so no second binding. Whether that binding is then absent, so that the first row answers, or not
  applicable, so that the second answers, is not said. l.291 names "the module instance is not `ready`"
  and "either applicable binding does not declare live reconfiguration" as separate causes and does not
  name an absent binding. Under the first reading an unloaded instance is never answered `NOT_READY`, and
  one request repeated during a single start is answered `INVALID_PARAMS` and then `NOT_READY`.
- CA l.785 against l.786 and l.794: `grant-revoked` applies when "revoked grants, alone or together with
  expired grants, would allow every requested scope that active policy does not allow" (l.785), and
  `grant-expired` when "expired grants alone would allow every requested scope that active policy does not
  allow" (l.786). When expired grants alone would allow every such scope and a revoked grant would allow
  one of them, the second meaning holds, and the first holds as well unless "together with" requires that
  the revoked grant be needed. "When several denial codes apply, Capability Authority MUST return the
  first applicable code in the order of this table" (l.794) then gives `grant-revoked`; under the other
  reading the answer is `grant-expired`. Which is meant is not said.
- RUNTIME l.2267 and l.2281 against CA l.1199 and l.368: saved permission settings are an array without a
  bound, `permissions: [* logos.runtime_control.permission_setting]` (RUNTIME l.2281), and each setting
  may carry `constraints: bstr .size (1..1048576)` (RUNTIME l.2267). "The required permission scopes of an
  execution decision are those mapped from the target instance's saved permission settings" (CA l.368),
  and "The deterministic-CBOR encoding of the `scopes` array of an evaluation request or a grant request
  MUST NOT exceed 4194304 bytes" (CA l.1199). Settings whose scopes pass that limit can be saved, and
  every evaluation of a start of that instance is then `invalid-request`. Whether
  `update_permission_settings` refuses such settings, and with which code, is not said.
- RUNTIME l.1349-1351 against l.1344 and PM l.1142: "An accepted input may omit `primary_contract`,
  `implements`, or both. When both are absent, the record declares no contract, and Runtime MUST NOT
  create a provider record merely because it creates the module instance" (l.1349-1351). `extends` "lists
  earlier contracts that a contract provided by the module extends" (l.1344), so an input that carries
  `extends` and neither of the two other fields names contracts that nothing it provides can extend.
  Package Manager "MUST reject a module declaration that has `extends` and has neither `primary_contract`
  nor `implements`" (PM l.1142). Whether Runtime rejects the same input from another source, or accepts
  it and ignores `extends`, is not said.
- PM l.533 against l.531, l.448 and l.727: "The same key material MUST NOT be used for provenance signing,
  call-evidence signing, TLS authentication, or another signature algorithm" (l.533) has no subject. It
  stands between two rules on protected trust input (l.531, l.534), so it may bind Package Manager, which
  sees the package-signing input only, or the deployment, which alone knows every use of a key. Elsewhere
  a key in two roles is described and not forbidden: "Configuring the same key material for more than one
  purpose does not merge those decisions" (l.448), and the package signer and the build-provenance signer
  stay distinct "even when protected policy authorizes the same credential for more than one role"
  (l.727). Whether Package Manager must refuse a trust input in which it can see such a reuse, and with
  which result, is not said. CA l.1312 has the same sentence for an evidence key.
- BCP l.383 against SECURITY l.394 and TRANSPORT l.1334: "For each finite admission pool shared by more
  than one consumer or provider, the documentation MUST state whether a per-consumer or per-provider limit
  applies" (l.383). An admission pool is not defined. SECURITY gives seven examples, "prepared calls,
  native borrows, sessions, routes, route tickets, grants, or audit storage" (l.394), of which a native
  borrow is no bounded resource of any specification, and TRANSPORT uses the word for its own limits:
  "Resource admission MUST occur before acquiring the bounded resources" (TRANSPORT l.1334). Whether a
  pool counts when its exhaustion delays a request and does not refuse it, when no request releases its
  entries, as with a bound on known module instances, or when it is shared by the callers of one system
  service, is left to each deployment. Two documents that both meet the sentence can list different pools.

---

## Appendix A — Items resolved by the current specs

Every item of the two earlier audits that the current text settles, with the rule that settles it. Items
NF-01 to NF-25 were corrections or additions to other items; the item they refer to is named in
parentheses. NF-25 made no point about the spec text and is left out. A row that ends with *No reply;
settled by the text* belongs to an item that has no response.

| Item | Subject | Outcome |
|---|---|---|
| C-01 | Whether an unqualified common-schema name such as `error_code` is read as `logos.error_code` or rejected. | COMMITMENT l.585: "Common schema references in the normative construction input MUST use qualified names in the `logos` namespace." A local-namespace shorthand stays non-normative tool input (BCP l.465-466). |
| C-02 | Whether a declaration may have more than one name segment after the schema namespace, which the C mapping cannot round-trip. | COMMITMENT l.255: every local declaration name is the primary schema namespace, a dot and exactly one identifier segment. Dotted namespaces remain valid and project with `_NS_` (INTERFACE l.656). |
| C-03 | Whether the C-to-CDDL reverse mapping is required for INTERFACE conformance, given that BCP calls code generation optional. | INTERFACE l.23-24: an implementation of the bidirectional mapping supports both directions; a module implementation need not implement the authoring mappings, only conforming artifacts and encoding. BCP l.489-490 agrees. No separate conformance section was added. |
| C-04 | A generator could omit a tagged choice's tag member, while generated headers have to be identical across implementations. | INTERFACE l.1182: "The canonical C representation MUST retain a required literal tag field as a writable member of its map struct." Encoders still emit the tag field in the CBOR map (l.1183). |
| C-05 | The typed call helper in the RUNTIME example was named differently from the one in the INTERFACE appendix. | Both examples now use `logos_storage_invoke_exists` (RUNTIME l.763; INTERFACE l.4127), and INTERFACE l.4122 says such helper names are implementation-defined. |
| C-06 | RUNTIME derived one socket path per module name, while TRANSPORT requires a directory per instance; path length limits were ignored. | RUNTIME l.296-297: socket names are derived inside the per-instance directory of TRANSPORT §8.2 (l.1099-1100); the concrete pathname is implementation-defined and subject to the host's Unix-domain socket pathname limit. |
| C-07 | Whether module declarations may share artifacts, which error an ordering violation returns, and which error wins when several apply. | PM l.330 and l.1085: schema and default artifacts may be shared, an implementation artifact may not. Ordering or uniqueness violations are `invalid-package` (l.353). No precedence is fixed: the first detected failure may be returned (l.1067). |
| C-08 | The only Loader error for refusing a weaker substitute, `unsupported-strategy`, was defined as permission to try another strategy. | LOADER l.625: an advertised strategy whose required security or deployment controls cannot be established fails with `realization-failed`. `unsupported-strategy` is only for an unadvertised strategy or hosted placement (l.377). |
| C-12 | Runtime conformance needs call-audit and call-evidence record types defined by the higher-layer Capability Authority specification, against the stated layer direction. | BCP §1.1 lists the dependency as an explicit exception (l.87) that needs no Capability Authority provider or module calls (l.90). RUNTIME now cites the Capability Authority specification normatively (l.4180). |
| C-11 | Uppercase requirement keywords in informative text that restate no normative rule. | The two sentences that had no normative counterpart use no keyword: a deployment "cannot rely on arbitrary post-install native module loading" (SECURITY l.476), and "Failure of optional logging does not waive required audit or enforcement." (BCP l.559). The uppercase keywords left in informative text restate rules of normative sections. |
| C-09 | Whether a consumer owned by an enrolled remote Runtime counts as a "Runtime-known" instance for the target's Capability Authority. | A grant target whose `runtime_instance_id` names another Runtime "resolves when that Runtime is enrolled with the issuing Runtime" (CA l.77), and such a grant supports authority only when that target is a consumer accepted under the forwarding rules of RUNTIME Section 9 (CA l.78). An address names its owning Runtime (CA l.85), and the target authorizes a forwarded consumer after the ownership and forwarding checks (RUNTIME l.1687-1689). |
| GN-01 | Only one of the twelve specifications cited BCP 14, so the force of uppercase and lowercase keywords was undefined. | Every specification now states that uppercase keywords follow BCP 14 and that lowercase forms keep their ordinary English meaning (for example TRANSPORT l.50-51 and SECURITY l.24-25). |
| CM-01 | Which declaration's identity a value carries when its type is reached through a chain of local aliases. | COMMITMENT l.891-893: the one-hop rule repeats to the terminal declaration; the referring location keeps its identity, the child carries the terminal declaration's, and intermediate aliases add no nodes. Vector in Appendix B.1 (l.1718). |
| CM-02 | Whether hash payloads below an imported reference carry the importing schema's root or the referenced schema's root. | HASH l.608-611: the reference payload keeps the importing document's root; its child and descendants use the referenced document's root; local references do not change context. Verifier checks at l.1105-1108, vectors in Appendix B.4 (l.1287). |
| CM-03 | Whether a schema node may reference the common callable declarations `logos.schema_request` and `logos.schema_response`. | COMMITMENT l.548: "An imported reference MUST target a named type declaration." The callable declarations of the common schema therefore cannot be used as type references. |
| CM-04 | What a verified-view path that ends at a map field or a tuple position discloses. | HASH l.1028-1030: a path ending at a present field, list index or tuple position discloses the contained normalized value; the field or tuple-element payload appears in the proof material. |
| CM-05 | Whether a semantic path must contain a choice-arm segment to pass through a choice value. | COMMITMENT l.1348-1350: continuing through a choice requires a `choice-arm` segment equal to the selected canonical arm index; a path that ends at the choice selects the complete choice value. |
| CM-06 | Whether choice-arm selection counts only literals on the tested value or every literal nested inside an arm. | COMMITMENT l.366-369: literals are collected only at the tested value or the selected field, following references and choice arms, never descending into map fields, list elements or tuple positions. Examples at l.412-413. |
| CM-07 | Whether a list whose element schema is a Boolean or integer literal is a packable scalar list. | HASH l.134-135: a packable list has "a primitive or literal element schema with a packable scalar kind"; `[* true]`, `[* 5]` and `[* -5]` are given as examples. |
| CM-08 | Where the verifier of a verified view obtains the schema it checks the view against. | HASH l.1084-1086: the verifier receives the schema construction input and its dependency documents separately from the view, validates them and computes the roots it compares; validated results may be reused. |
| CM-09 | The `logos.schema.reference` hash domain is defined but no object in the specifications uses it. | HASH l.516-518: the domain hashes a standalone `schema-import` pair, takes no part in schema or value commitments or verified views in this revision, and cannot stand in for a root or for the pair. |
| CM-10 | Whether `0*` and `*1`, spellings equivalent to the supported `*` and `?` occurrences, are rejected or normalized. | cdCDDLe l.169-170: occurrence indicators with explicit numeric bounds are rejected even when equivalent to a supported form, including `0*` in arrays and `*1` in maps. |
| CM-11 | Which CDDL string-escape grammar applies, RFC 8610 or its RFC 9682 update. | cdCDDLe l.120: text-string and byte-string literals follow RFC 9682 Section 2; the rest of the supported subset follows RFC 8610 (l.119). |
| CM-12 | Whether a range bound may be a named reference instead of an integer literal. | cdCDDLe l.172-173: range bounds, including those in `.size` controllers, are integer literals written directly in the source; named references as bounds are rejected. |
| CM-13 | The decoder's rejection list did not include a choice nested directly inside another choice. | cdCDDLe l.578: "A `cdCDDLe` decoder MUST reject a choice node that has another choice node as a direct alternative." |
| CM-14 | Whether prelude, common and supporting definitions are merged into a schema's cdCDDLe document or stay references. | COMMITMENT l.560-562: the document node contains exactly the document's own rules; the prelude and other documents are not merged; references to prelude aliases and external named types stay type-reference nodes. |
| IF-01 | Whether a float inside `params`, `result` or `data` is a Transport profile violation or a schema mismatch. | A float at any depth violates the deterministic profile (INTERFACE l.3066-3067). It is a Transport validation failure, not deferred to schema validation (INTERFACE l.3093): ProtocolError `INVALID_PARAMS`, then close (TRANSPORT l.403-407). |
| IF-02 | No bound on value nesting depth, and no error for a payload that exceeds an implementation's limit. | Implementations enforce a configurable payload depth limit of at least 128 (INTERFACE l.3104). Dispatch rejects with `INVALID_PARAMS` without detail (INTERFACE l.3111). Transport sends ProtocolError `INVALID_PARAMS` without `detail` and closes (TRANSPORT l.401-408). |
| IF-03 | C representation of inline tuples, lists and byte strings used as choice arms or list elements. | In tuple positions, list elements and choice arms, each is one aggregate value with the named-aggregate layout (INTERFACE l.1002-1007). Its name comes from the path steps and tag families at INTERFACE l.745-751 and l.770-772. |
| IF-04 | C representation of an event whose body is a choice of maps. | Such an event uses the ordinary choice representation with its `_CHOICE` tag and no outer wrapper (INTERFACE l.1362-1364). The reverse mapping reconstructs it at INTERFACE l.2540. |
| IF-05 | Exact spelling of generated literal macros, on which generated header content depends. | Generated spellings are fixed: `true` or `false`, `UINT64_C(n)`, `(-INT64_C(n))`, one minimum-`int64` expression and one string form with octal escapes (INTERFACE l.1056-1062). Accepted handwritten forms are listed at INTERFACE l.2502-2534. |
| IF-06 | Position of the `has_` presence flag for an optional inline tuple field. | One `bool has_x` immediately precedes the first expanded member `x_0` and governs the whole tuple group (INTERFACE l.983-985). The reverse mapping enforces this at INTERFACE l.2475-2477. |
| IF-07 | Allocation unit and free order for recursive typed response outputs. | One response owner governs all backing storage of a typed response, including nested and recursive values. The caller clears the owner and frees no individual pointer (INTERFACE l.1795-1797). |
| IF-08 | Which function a consumer calls to free outputs decoded by a typed route call helper. | A generated call helper returns a response owner for its decoded storage and comes with a matching typed cleanup helper (INTERFACE l.1866-1880). Helper names are implementation-defined (INTERFACE l.858). INTERFACE l.4140-4155 shows the pair. |
| IF-09 | One module's method symbol could have the same C name as another module's lifecycle symbol. | Lifecycle symbols use `logos_<module-C>_MODULE_<operation>` and method symbols `logos_<module-C>_CALL_<namespace>_<Method>` (INTERFACE l.673, l.706). Module names and schema atoms are lowercase (RUNTIME l.284, INTERFACE l.758), so the families cannot coincide. |
| IF-10 | Where a consumer obtains the `schema_cbor` input that `materialize_route` requires. | The sources are named: documents embedded in generated bindings or supplied with the application, a projected `describe_provider` response, or an earlier `logos.schema` response (INTERFACE l.3904-3906). No `logos.schema` call is needed first (INTERFACE l.3907). |
| IF-11 | Relative order of macros, typedefs, lifecycle symbols and provider declarations in generated headers. | The placement of independent declarations is not part of the canonical mapping (INTERFACE l.865) and may differ between implementations (INTERFACE l.612). Only declaration before use is required (INTERFACE l.863). |
| EC-05 | Error code for a call through a route handle whose route is closed, failed, revoked or expired. | Withdrawn or expired authority gives `NOT_AUTHORISED`; explicit closure or readiness loss gives `NOT_READY`; authorization takes precedence (RUNTIME l.1261-1267). A transport failure that hides the result stays `TRANSPORT_ERROR` (RUNTIME l.1270). |
| EC-06 | Error code for a new call into a stopping provider or through an invalidated Runtime Control binding. | Both return `NOT_READY` while the binding storage remains valid (RUNTIME l.595). Known authorization failures keep their precedence (RUNTIME l.597). |
| EC-07 | Error code when an operation needs a Module Loader or Package Manager that is unavailable. | An unavailable non-authority system service that prevents completion gives `NOT_READY` (RUNTIME l.1811). An unavailable Capability Authority keeps its authorization-failure rules (RUNTIME l.1815). |
| EC-08 | Error codes for an invalid Runtime Control or route vtable, a failed `materialize_route`, and `connect_remote` with a non-remote endpoint. | Vtable version or size failures give `VERSION_MISMATCH` and null members `MODULE_ERROR` (INTERFACE l.3850-3851). `materialize_route` failures are classified at INTERFACE l.3917-3923. A non-remote endpoint gives `INVALID_PARAMS` without detail (INTERFACE l.3876). |
| EC-09 | Error code for invalid remote-listener, provider-export or enrollment input. | Invalid listener or export input gives `INVALID_PARAMS` without detail, and activation failure `TRANSPORT_ERROR` (RUNTIME l.3295-3299). Enrollment is provisioning input, not a Runtime Control method; a provisioning interface using shared codes follows RUNTIME l.2645-2647. |
| EC-10 | `route_failure.code` and `permission_settings_state.failure` were free strings with no defined values. | `route_failure.code` has seventeen defined values (RUNTIME l.2422-2442) and the permission failure value is `enforcement-failed` (RUNTIME l.2450). Consumers treat any other string as an unclassified failure (RUNTIME l.2419). |
| EC-11 | Error code at static binding registration for symbol-table defects other than duplicates, empty tables and null addresses. | Registration also rejects a malformed symbol name, an ambiguous symbol family or a missing unconditional ABI symbol with `INVALID_PARAMS` (RUNTIME l.3915-3916). Contract-dependent checks run at implementation binding (RUNTIME l.3918), where the Loader reports `abi-invalid` (LOADER l.400). |
| EC-01 to EC-04, NC-03 | Which channel carries the outcomes that a Runtime Control caller must expect, such as a stale revision or a rejected configuration. | RUNTIME l.1818: "An outcome that a correct caller must expect is reported in the response `error` arm, not through the shared invocation-error channel." A stale expected revision gives `stale-revision` with the current revision (l.1819-1820), and a module's rejection of a configuration gives `configuration-rejected` (CONFIG l.323). The conditions that stay on the shared channel are named as failures of the invocation itself (RUNTIME l.1816). |
| TR-01 | Receiver behaviour for a wrong-direction message or an ordinary message received before Hello completes. | Direction and connection state are envelope checks (TRANSPORT l.400). Such a message gets ProtocolError `INVALID_PARAMS` and the connection closes without dispatch or delivery (TRANSPORT l.410-412). |
| TR-02 | Receiver behaviour for a Response, SubscriptionResult or Event that matches no outstanding operation. | Unsolicited, duplicate or mismatched messages get ProtocolError `INVALID_PARAMS` and close (TRANSPORT l.572-573). A late Response to an abandoned call is validated and discarded, because correlation state is kept while the connection is open (TRANSPORT l.576-579). |
| TR-03 | Callee behaviour for a reused subscription identifier, an unknown one, or overlapping control operations. | An overlapping operation gets ProtocolError `INVALID_PARAMS` and close (TRANSPORT l.724-726). A reused Subscribe identifier or an Unsubscribe naming no active subscription gets a failed SubscriptionResult with `INVALID_PARAMS` (TRANSPORT l.729-731). An Unsubscribe for a subscription that the callee ended with a SubscriptionEnd gets a successful SubscriptionResult instead (TRANSPORT l.755). |
| TR-04 | Error code when the Hello response carries a non-empty token under a profile that requires an empty one. | The caller sends ProtocolError `NOT_AUTHORISED` and closes (TRANSPORT l.510-511). The response checks run in the order module, token, schema (TRANSPORT l.504). |
| TR-05 | When the provider Hello takes place, and which error the consumer sees when it fails. | `materialize_route` completes peer validation and Hello before it returns a handle (RUNTIME l.741-743). A Hello rejection returns its own code, and loss or timeout returns `TRANSPORT_ERROR` (RUNTIME l.746-749). |
| TR-06 | On-wire signal when a route expires or is revoked while its session is live. | When route authority expires or is revoked, a new Request during termination gets `response-err` with `NOT_AUTHORISED` (TRANSPORT l.969-971). The Runtime then sends ProtocolError `NOT_AUTHORISED` when writable and closes, without waiting for an acknowledgement (TRANSPORT l.974-978). A route that ends through loss of route readiness, including `route-timeout`, follows the same rules with `NOT_READY` (TRANSPORT l.977). |
| TR-07 | Receiver behaviour for a `response-ok` or Event whose payload fails its declared schema. | The schema-aware receiving boundary sends ProtocolError `INVALID_PARAMS` and closes the provider session; outstanding calls get `TRANSPORT_ERROR` (TRANSPORT l.661-664). The specification that defines an invocation or delivery boundary assigns the payload validation (INTERFACE l.3087-3088). |
| TR-08 | Precedence between payload schema validation and the commitment check on a received message. | The order is fixed: schema subtree root, payload schema, value root (TRANSPORT l.642-652). A root mismatch closes the session; a schema-invalid Request alone gets `response-err` with `INVALID_PARAMS`. The specification that defines the boundary assigns that validation (INTERFACE l.3087-3088). |
| TR-09 | No named Windows equivalents for listener transfer, peer-identity verification and directory protection in the Unix-stream profile. | The profile is conditional on Windows (TRANSPORT l.1131-1133). TRANSPORT l.1135-1149 states the access-control, listener-transfer and `SIO_AF_UNIX_GETPEERPID` peer-verification requirements. An unsupported placement fails without fallback. |
| RT-02 | Calls the Runtime engine makes for no module (bootstrap realization, cleanup, authority evaluation) had no consumer or authority basis. | A Runtime-owned system-service binding, direct or protected local transport, authorizes the engine without making it a consumer (RUNTIME l.1568-1572, l.1583; TRANSPORT l.1056). `evaluate` keeps the evaluated module as `consumer` (RUNTIME l.1581). |
| RT-03 | The orchestration module had no assigned name, and its use of the reserved `logos_` prefix was unsettled. | The role has no canonical module name and needs no provider contract; deployment identifies the instance explicitly, and neither a name nor a reserved prefix confers the role (RUNTIME l.181-183). |
| RT-04 | How `create_module` chooses among installed packages or versions that declare the requested module name. | Active policy must select one accepted declaration or the request fails; the integration must support exact package and version selection, with no substitution and no selector in the request (RUNTIME l.3481-3491). |
| RT-06 | No operation or documented procedure moves an existing instance and its state to a newer package. | Upgrade uses a new instance selected under current policy, with fresh state unless separately authorized migration applies; no Runtime Control upgrade method (RUNTIME l.3411-3419). `start_module` reuses the retained declaration, also after a stop (l.3506). |
| RT-05 | What separates a Module Loader that is briefly unavailable from one that has failed. | RUNTIME l.3686: "The owning Loader has failed when its provider module instance leaves `ready` because its realization ended or failed." Failed operations, or loss of its binding, while that instance stays `ready` are temporary unavailability (l.3687). |
| CA-01 | Whether a running module that loses execution authorization stops at once or waits for re-evaluation. | Runtime withdraws execution access and starts termination without waiting for re-evaluation; a retryable renewal failure keeps only an authorization that is still independently valid; intent is retained (CA l.880-885). |
| CA-03 | `publish_events` and the `publish-event` action had no defined meaning, since only providers send events. | `publish-event` is the publisher's authority to deliver an event on a subscriber route; delivery also needs the subscriber's `subscribe-event` authority and both route event lists (CA l.244-247; RUNTIME l.1152, l.2923-2925). |
| CA-04 | Order and duplicate handling of the request and response proof arrays in call evidence. | Each side is ordered by ascending deterministic-CBOR bytes of the proof's semantic path, with no duplicate path per side; empty arrays and an empty `proofs` are omitted; verifiers reject, never sort (CA l.1336-1342). |
| CA-05 | Result order, cursor lifetime and time bounds of `list_grants` and `query_audit`. | `list_grants` orders by ascending grant-id bytes, continues live after the last ID, and binds cursors to consumer and query, with documented expiry (CA l.697-706). `query_audit` has no cursor: newest first, `since` inclusive, `until` exclusive (CA l.1159-1163). |
| CA-06 | Which decision and scope a call audit record carries when the route was authorized by a route-level decision. | The record carries the allow decision actually applied to the call and the exact enforced call scope, captured at admission; a cached call decision may serve, a route-establishment decision may not (CA l.1219-1224; RUNTIME l.1641-1643). |
| PM-03 | Package Manager cursors and record filtering are bound to an authenticated caller that the provider ABI did not pass. | The invocation context identifies the caller (INTERFACE l.2140-2142). Cursors bind to the authenticated consumer, and record visibility is a deployment observation policy (PM l.1638-1646). |
| PM-04 | Manifest artifact paths may be up to 4096 bytes, longer than a USTAR header can hold. | Every archive path must fit the USTAR `name` and `prefix` fields, 100 bytes or a 155 plus 100 byte split at a slash; PAX and GNU long-name headers are forbidden (PM l.917-921). |
| PM-05 | Whether an LGX archive may be a multi-member gzip stream, and whether directory entries are required. | Exactly one gzip member; extra members or trailing bytes are rejected (PM l.940-941). The `variants/` directory holds exactly one directory per manifest variant (PM l.905), and directory entries may be omitted when descendants imply them (PM l.907). |
| PM-06 | Ed25519 verification strictness (cofactor, small-order and non-canonical points) was not pinned. | Package signatures and call evidence use pure SLH-DSA-SHA2-192s, not Ed25519; lengths are fixed, and verifiers apply FIPS 205 `slh_verify` without repairing a key or signature (PM l.550-557; CA l.1318-1325). |
| PM-07 | Which source is used when several offer the same package identity and manifest commitment. | Unless the operation fixes the source, equivalent acceptable sources are taken in ascending bytewise order of their deterministic-CBOR source-record encoding (PM l.1330). |
| PM-08 | What dependency resolution does when a candidate's material cannot be fetched. | The root operation fails with `package-unavailable` and leaves installed state unchanged; unavailability is not proof of invalidity, and lower candidates need not be fetched once a solution is selected (PM l.1308-1310). |
| PM-09 | Whether `manifest.json` in an LGX archive must be checked against `manifest.cbor`. | `manifest.json` is not part of the LGX format. Only `manifest.cbor`, `manifest.cose` and `variants/` may appear at the archive root (PM l.904), so there is nothing to compare. |
| PM-12 | Provenance verification required a provenance-signing profile, and none was defined. | `logos.provenance-signing.dsse-slh-dsa-sha2-192s` is defined and required of every implementation that supports the SLSA provenance profile; protected policy selects it and binds each signer key to its builders (PM l.652-662). |
| PM-13 | Provenance failures had no assigned codes in the closed Package Manager error list. | Absent locator or malformed evidence gives `invalid-package`; retrieval failure gives `package-unavailable`; a failed signer, subject, build-type or source binding gives `signature-verification-failed` (PM l.1507-1509). The first-detected-failure rule applies (PM l.1511). |
| PM-14 | What happens to a Nix source while the LGX-only provenance profile is selected. | A request selecting a direct Nix source fails with `unsupported-source` before any Nix evaluation; resolution may use another eligible source, and a Nix-built package supplied as LGX stays eligible (PM l.605-608). |
| SO-08 | No mechanism for a deployment to declare itself non-production, or statement of what that permits. | Non-production mechanisms need explicit protected configuration, and the deployment identifies itself as non-production in documentation and operator-facing diagnostics; build mode alone enables nothing and the designation waives no requirement (BCP l.403-406). |
| SO-10 | Where the machine-readable CDDL of each contract is, and whether it can be taken from the text in document order. | No mirror file is named. Each contract has its complete schema in one normative block: "Appendix A lists the complete contract schema in one block." (PM l.43; the same sentence at CA l.32 and LOADER l.39), and RUNTIME l.1774 and CONFIG l.359 say it of their own blocks. The record examples of RUNTIME Appendix B are fenced as text, and B.3 shows `execution` (l.4056-4059). |
| NX-01 | The Capability Authority's grant-change event had to be filtered per subscriber, which a provider's broadcast publish could not do. | `grant_changed` and `policy_changed` are restricted to Runtime-owned system-service bindings (CA l.923-924). Ordinary consumers call `watch_changes` and receive `observed_change` through that invocation's protected destination, with visibility checked per publication (CA l.981, l.999). |
| NX-02 | The ordered snapshot-then-events synchronization model had no way for a provider to send a snapshot to one subscriber. | A watch method publishing invocation-scoped events orders the snapshot before the changes (TRANSPORT l.776-778), and the invocation context gives the provider that publish operation (INTERFACE l.2150). No generic revision type is added (TRANSPORT l.783-784). |
| NX-03 | One specification defined per-call authority decisions and call audit records that the Runtime specification never produced. | Every provider call needs call authority beyond the route checks, which a valid cached call decision may satisfy (RUNTIME l.1641-1644). The call record carries that decision and the enforced scope; a route-only decision does not authorize a call (CA l.1219-1223). |
| NX-04 | A module's schema namespace and type names could generate C type names equal to fixed common-header names, undetected. | Generated type names capitalize the local declaration name (INTERFACE l.742-743) and schema atoms have no uppercase letters (l.758), so `error.code` becomes `logos_error_Code_t`, never the fixed lowercase `logos_error_code_t` (l.805). |
| NX-05 | The Runtime specification depended normatively on three other specifications that its reference list omitted. | Its normative references now list the Capability Authority, Package Manager, Loader, commitment and hash specifications (RUNTIME l.4180-4184), package identity points at Package Manager Section 4 (l.3390), and the upward dependencies are tabulated (BCP l.84-87). |
| NX-06 | Diagnostic text supplied by a module had no content rule and could carry host paths to every observer. | `reason` values, including `route_failure.message`, must not expose credentials, sensitive host paths or anything the recipient may not observe, in records, responses, events and reflected remote state; Runtime may omit or replace module text (RUNTIME l.1793-1797). |
| NE-01 | How a provider returns a result only the requester may see, and progress, without broadcasting them as events. | A delayed result returns through the method's own final Response, with no job identifier or event (TRANSPORT l.826-828). Progress goes to the caller alone as invocation-scoped events (RUNTIME l.1173-1179), and the provider sees the authenticated caller (INTERFACE l.2140-2141). |
| NE-03 | A consumer was never told that its route, and the subscriptions on it, had ended. | Every route handle provides `observe_end`, which reports loss of the handle's invocation path in every mode without an observation grant (INTERFACE l.1442-1444; RUNTIME l.1277-1280). No deadline is set for detecting a silent connection failure (INTERFACE l.1463). |
| NI-01 | A module could not learn its own instance address, which every self-targeting control method requires. | `get_self` returns the complete authenticated module-instance address of the calling binding, is callable during initialization and needs no policy grant or Capability Authority (RUNTIME l.2481-2484). |
| NI-02 | The provider identifier was called stable but had no defined lifetime across stop, start, recovery and restart. | Stop, start and recovery do not replace provider records or identifiers; records restored after a Runtime restart keep their identifiers and instance, and an identifier is never reassigned to an unrelated record (RUNTIME l.2804-2807). |
| NI-03 | Whether instance identity must persist was ambiguous, and records naming a lost identity had no defined fate. | An address is kept only with continuity of the same logical instance; otherwise a fresh address is allocated and old ones are never reused (RUNTIME l.2556-2561). Retained records stay attributed to the old address and transfer nothing (l.2564-2567). |
| NI-04 | No operation ever removed a module instance, and package removal ignored instances that still used the package. | `retire_module` removes a stopped instance and its provider records from inventory, without cascade, keeping assigned storage and grants (RUNTIME l.3421-3428, l.3444, l.3450-3453). Package removal and state disposal stay separate authorized operations (PM l.1698-1699). |
| NI-05 | A request naming only a module had no rule when several instances matched, and events could omit the instance. | Lifecycle responses and state events carry the exact `instance`, or the facade's `provider` (RUNTIME l.3360-3361). A name-only request needs observation authority over the whole selection, else `NOT_AUTHORISED`; zero or several matches give `INVALID_PARAMS` (l.3532-3538). |
| NI-06 | The verified package signer was dropped from every package record, the Runtime handoff and execution observation. | The verified signer key is retained with installed state and reported by inspection results and the Runtime handoff (PM l.539-542), and observable as `selection.signer`, as provenance and not publisher identity (RUNTIME l.3384-3387). |
| NL-04 | The startup timeout had no source, and behaviour when native initialization outlives it was undefined. | The deployment supplies and documents a finite startup deadline (RUNTIME l.628). Expiry blocks readiness, never destroys or unloads while initialization runs, and the attempt stays owned until cleanup resolves (l.629-632); the failure is classified `startup-timeout` (l.3605). |
| NL-06 | Whether cleanup turns a failed instance from `error` to `unloaded` was undefined, and start and recover had different preconditions. | Cleanup alone never changes `error` to `unloaded`; only a new accepted attempt or a completed explicit stop leaves `error` (RUNTIME l.573-574). `start_module` is refused with `NOT_READY` while earlier cleanup is unresolved (l.578). The state table lists the two transitions out of `error`: to `loaded` when a new execution attempt is accepted and to `stopping` on an explicit stop or Runtime shutdown (l.525-526). |
| NL-10 | After a Runtime restart nothing said who resumes retained start intent, and no restart operation exists. | Orchestration must reconcile retained requested intents when it becomes operational, including after Runtime restart, and schedule the recovery that policy permits (RUNTIME l.3631-3633). No restart method is added; a restart is a stop followed by a start. |
| NL-11 | Applying configuration live had no deadline, no outcome for a timed-out attempt, and no rule for a stop meanwhile. | The deployment supplies a finite application-attempt deadline; expiry without a valid result is indeterminate, not rejection, and puts the instance in `error` (CONFIG l.274-275, l.320). A stop may close admission but not destroy the context while the hook runs (l.277), and an instance that is `stopping` when the outcome becomes indeterminate stays `stopping` (l.328). |
| NL-07 | The `failure` code and the `state` of a remote-module facade whose target is stopped, failed, not ready or contract-incompatible. | RUNTIME l.3615: "For a facade, `facade-failed`, `remote-unreachable`, `remote-not-ready`, `remote-stopped`, `remote-failed`, and `contract-mismatch` are also defined classifications, with the causes defined for `route_failure.code`." A started facade that is unavailable reports `loaded` when its target is known to be not ready, stopped or unloaded, and `error` for every other classified cause (l.3616). |
| NA-03 | A local route's record could omit the expiry time although its authorization always has a validity end. | Every ready route returned to its consumer "whose authorization has a validity end MUST contain `expires_at`" (RUNTIME l.2893), local routes included. A route whose authority reaches its validity end becomes `revoked` with failure code `authority-expired` (l.2966). |
| NA-05 | Grants recorded neither who issued them nor which decision they answer, so administration depended on audit retention. | Each grant carries an immutable `issuer`, a module address or a protected-policy source, derived by the Authority (CA l.612-624, l.686-689). There is no decision link and no issuer filter on `list_grants` (l.667-673); a caller filters the listed grants. |
| NA-07 | After a policy change, existing subscriptions kept delivering events until the consumer's next protected operation. | The protected operations re-evaluated after a policy-change notification now include "new event-delivery commitments" (CA l.931-933). Events already committed follow the existing commitment rules (l.934). |
| NA-08 | Decision identifiers could repeat after an Authority restart, and the term "Authority binding" was undefined. | Decision identifiers must be collision-resistant across issuers, restarts, replacements and restored or cloned state (CA l.540-543). An Authority binding is Runtime's protected association with the selected provider realization and its invocation and notification paths (l.851). |
| NA-11 | Bootstrap policy after the Authority is bound had no precedence rule, and recovering a failed Authority rested on inference. | Protected recovery policy may authorize restoring the selected unavailable Authority and the operations this needs, and cannot override an active-policy denial (RUNTIME l.1591-1595). The specs add no lapse of bootstrap grants and no synthetic decision identity. |
| NA-04 | Whether an idempotent `establish_route` replay returns the one-time ticket. | RUNTIME l.3080: "The retained result MUST NOT include a raw route ticket, and a replayed route record omits `invocation`." The consumer obtains an invocation descriptor through `renew_route` (l.3081). |
| NR-05 | Whether loss of a provider session ends the route or leaves it renewable hung on an undefined phrase. | Session loss ends the session and its invocation path; alone it "need not make the logical route terminal", and a nonterminal route can renew (RUNTIME l.3334-3336). A new operation through a handle whose path has ended while the route stays `ready`, with no other known cause, gives `TRANSPORT_ERROR` (l.1264); see TL-03. |
| NR-06 | Whether a successful route renewal extends a live provider session was implied but never stated. | It does not. A live session keeps its previous decision and ends at that expiry; the renewed descriptor's fresh ticket establishes a replacement session (RUNTIME l.3337-3338; TRANSPORT l.913-915). The connection cost is TS-04. |
| NR-09 | Whose clock governs a remote route's expiry, and whether certificate validity times are checked. | The target Runtime enforces expiry on its accepted clock, and each Runtime enforcing an exposed deadline uses its own; disagreement cannot extend authority (RUNTIME l.2943-2946). Certificate validity periods are checked (TRANSPORT l.1243, l.1252). |
| NR-10 | The remote certificate profile left open self-signed leaves, host-name checks, the role of `server_name`, and key usage. | A directly provisioned leaf is valid as its own anchor by complete DER equality where the implementation supports that optional case, and key-usage rules are stated (TRANSPORT l.1243-1247). Identity comes from enrollment, DNS-name matching is not required, and `server_name` is SNI (l.1254-1256). |
| NR-11 | One route handle allowed only one outstanding call, so concurrent calls needed one route each. | A prepared asynchronous call "does not monopolize that handle", and another call can be prepared while it is outstanding (RUNTIME l.1285-1286). Separately materialized handles do not by themselves share a path (l.1188). One connection per route remains: TS-04. |
| NR-12 | A caller's cancellation of a long call stopped at the provider's host and never reached provider code. | Cancellation is a sticky state on the provider's invocation context, with an optional `request_cancel` hook (INTERFACE l.2102-2103); Runtime arranges Cancel processing on a live session (l.2032). It does not prove that the work stopped (l.2138). |
| NR-04 | Who follows a continuation, what `partial` means between Runtimes, and which rule a `connect_remote` binding follows. | For a local module consumer, Runtime resolves continuations itself. RUNTIME l.3032 names its subject: "Runtime exposes route establishment and renewal to modules only through the typed Runtime Control `establish_route` and `renew_route` methods." `partial` is `false` only when every visible provider "has a returned ready route or continuation" (l.1416). A response through a `connect_remote` binding is an inter-Runtime response, and the module may follow a continuation with a new request (l.3031). |
| ND-03 | A schema-valid value larger than the frame limit closed the whole connection; a sender-side rule and per-call failure were missing. | Before writing, the sender checks each frame against the peer maximum, 16 MiB by default (TRANSPORT l.377-378). An oversized Request fails locally, an oversized Response becomes a correlated `MODULE_ERROR` (l.379-380), and an oversized Event is not committed (l.382). |
| ND-08 | Named types could not be shared between interface contracts, or between an interface and a module implementing it. | Interface and concrete contracts may both import named types from an explicitly supplied supporting schema (INTERFACE l.94, l.111), so shared records live there. Types declared inside a contract are not referenceable from other documents (l.119-120). |
| ND-11 | Whether a value typed by a declaration whose body is a primitive, literal or reference carries the declaration's subtree root or a leaf hash. | No response, but the text settles it: "An empty path always uses the named declaration's schema subtree root, including when its body is a primitive, literal or reference node" (COMMITMENT l.472); the vectors agree (HASH l.1340). |
| ND-13 | An aggregate named only through a variable-length list had no forward typedef, although its definition names its own type. | No response, but the text settles it: "The generator MUST also emit a forward typedef whenever an aggregate type name is used before its complete definition, including uses through variable-length lists" (INTERFACE l.1046). |
| ND-14 | The tie rule for ordering type definitions did not give the order of the normative example header. | No response, but the text settles it: there is no tie rule, and the placement of independent declarations "is not part of the canonical mapping" (INTERFACE l.865; l.612, l.2604). |
| ND-04 | The failure outcome of the list constraints that the system contracts state in prose. | RUNTIME l.2464 and l.2933 assign `INVALID_PARAMS` without validation detail to a duplicate or unordered permission array and route-access list, and forbid silent sorting. CA l.800 assigns `invalid-request` to a request that "violates a rule of this specification that no more specific code covers, including an unordered or duplicate set-valued array". |
| ND-10 | Whether `.size` may be applied to a named target. | cdCDDLe l.157 admits only "the `.size` control applied directly to `uint`, `tstr`, or `bstr`". No reply; settled by the text. |
| ND-12 | Whether a cycle of local aliases is a valid schema. | COMMITMENT l.191: "Following local references from a named declaration body MUST reach a non-reference schema node or an imported reference without revisiting a declaration." No reply; settled by the text. |
| NP-05 | Where licence and attribution material goes, and how a user-replaceable (LGPL) library coexists with verified-byte binding. | Licence and attribution material ships as verified `resource` artifacts under documented application conventions (PM l.1195). Replacing executable bytes requires acceptance of the replacement through the artifact, trust and authorization rules, never an in-place swap (l.1196). No notice-discovery contract (l.1197). |
| NP-07 | What the installation root is, and whether installed sets are per user or per host when several Package Managers coexist. | The installation root is the protected destination for materialized artifacts (PM l.926). Layout and per-user, per-host or per-service scope are documented deployment choices (l.927, l.931); distinct Package Manager instances share no inventory implicitly (l.928). |
| NP-08 | Events for installed-set changes and install progress, and a Runtime Control event when a module record is created. | `watch_installed_packages` delivers change hints to its caller, who re-queries (PM l.1738, l.1760-1761). A `progress_key` enables caller-correlated `operation_progress` events (l.1778-1780). Record creation raises an `inventory_changed` hint (RUNTIME l.3275). |
| NP-10 | Anti-rollback for package-signing trust input, and who decides the fate of running modules when a signer is withdrawn. | Trust configuration uses a monotonic revision or equivalent, surviving restart; older state is rejected (PM l.401-403). Withdrawal blocks later package operations; the deployment documents whether execution depends on current trust, and then authorization is invalidated (l.408-410). Exact-name binding: TS-05. |
| NP-11 | Where files common to several variants go in an LGX. | A package need not hold more than one platform: "A producer MAY publish separately signed packages with the same package identity for different platforms, each declaring only the variants for those platforms." (PM l.960). No form shared between variants is defined. No reply; settled by the text. |
| NP-12 | Whether a host must download every variant, and how a resolver learns which source serves its platform. | Packages may be published per platform (PM l.960-961), and an unreached candidate's material "MUST NOT be required or cause the root operation to fail" (l.1295). How a resolver learns which package serves its platform is left to implementation-defined catalog metadata, and that exclusion is optional (l.1311-1312); section 3.5 has a remark on it. No reply; settled by the text. |
| NP-13 | How variants built on separate machines are signed and attested. | Each platform's package is signed separately (PM l.960), so its signature and provenance are its own builder's. No reply; settled by the text. |
| NP-15 | The code for an artifact of the wrong kind and for an artifact without its hash. | A reference to "an artifact whose kind differs from the kind that the reference requires" is in the `invalid-package` list (PM l.1081). PM l.365: "A missing artifact or hash mismatch MUST fail with `artifact-integrity-failed`." No rule names an artifact that omits its hash, which the manifest schema requires. No reply; settled by the text. |
| NC-05 | Secrets passed as method parameters were committed deterministically and could be retained, and no schema marker identified them. | `_sensitive` marks whole requests and responses (INTERFACE l.211, l.221): buffers are erased (l.361), nothing is logged or audited (l.375), a retention policy rejects the call (l.377). Events cannot be marked (l.423); exposed commitments stay guessable (SECURITY l.403). A route under `logos.remote.tls-tcp` or `logos.remote.quic` cannot permit a marked method (TRANSPORT l.1188). Credential storage is the Credential Store contract, optional to implement and deploy (CREDENTIAL STORE l.34-36, l.44). |
| NS-01 | The specs did not say that operating-system device consent goes to the application, leaving per-module device permissions without an enforcer. | Platform consent applies to platform-defined principals, not to module instances (SECURITY l.411). A profile claiming per-module device restrictions must name the consent principal and the controls against bypass (CA l.406-407). No such profile is defined. |
| NS-02 | What a module's host process does when the Runtime that owns it dies was unspecified. | Terminal loss of the control carrier stops new work and starts termination. Earlier authority cannot keep admission open, destruction is not guaranteed to run, and a new Runtime binding adopts no survivor (RUNTIME l.909-912). |
| NS-03 | Deployment profiles were not required to state secret storage, backup exposure or deletion of module state. | Deployment documentation must state protection at rest, secret-storage facilities, backup and synchronization exposure and deletion limits (BCP l.399). No blanket backup exclusion or erasure guarantee is required (l.401). Where the Credential Store is deployed, the documentation also states its credential, format and sealing profiles, backend durability and recovery, and protected delivery (l.374); that contract keeps each credential encrypted in a deployment-assigned slot (CREDENTIAL STORE l.58, l.441). |
| NO-01 | Runtime Control list methods returned an arbitrary subset with no continuation, no defined order and no filter for modules. | All four list methods page through one snapshot with `cursor`, `limit` and `next_cursor` (RUNTIME l.3230, l.3237-3240), in a fixed key order (l.3264-3271). `list_modules` takes `module` and `instance` filters (l.3234). |
| NO-02 | Observers could not synchronize snapshots with events: no revisions or timestamps, and no event for created or removed records. | Membership and record changes in the four collections raise `inventory_changed` hints (RUNTIME l.3274-3275); observers subscribe, list and rescan (l.3283-3286). There is no timestamp, route sequence or replay. Changes of failure, selection and realization are reported by `execution_state_changed_event` as execution-revision changes and read through `get_execution_summary` (l.3373-3374). |
| NO-05 | The initial permission-settings state and first revision of a newly created instance were undefined. | A new instance without protected settings starts at revision 1, with an empty permission array, status `applied` and no failure (RUNTIME l.2468). Declarations and `requested_permissions` alone never supply settings (l.2470); the initial state grants nothing (l.2472). |
| NO-06 | What happens to a running instance when its permission settings are replaced with wider access. | Runtime reconciles widening and narrowing, live or by stopping the realization (RUNTIME l.2522-2523). Widening needs current execution and permission authority (l.2524). A reconciliation stop keeps execution intent and its origin, and resumption uses ordinary recovery (l.2525-2526). |
| NO-07 | The four module-execution actions of an authorization scope were never mapped to the lifecycle methods. | Actions are `start` and `stop` only (CA l.199, l.311). `start` covers loading, initialization, readiness and continued execution (l.325); `stop_module` needs `stop` (l.331), which includes unloading (l.333). Creation, retirement and settings need separate management authorization (l.336). |
| NF-01 | (on C-01) the sentence on unqualified common names was ambiguous rather than contradictory; common definitions should be referenced only by qualified names | COMMITMENT l.585: "Common schema references in the normative construction input MUST use qualified names in the `logos` namespace." |
| NF-02 | (on C-03) the interface specification defined no conformance classes, so a tool without the C-to-CDDL direction could not tell whether it conforms | INTERFACE l.23-24 separates two subjects: "a conforming implementation of the bidirectional mapping" supports both directions; "A module implementation is not required to implement the authoring mappings". No one-direction mapping class exists. |
| NF-03 | (on C-06) the per-name socket path was only an example; the real gap was the 4096-byte address bound against host socket-path limits | RUNTIME l.296-297 places the socket in the per-instance directory and makes the pathname "implementation-defined and subject to the host's Unix-domain socket pathname limit". TRANSPORT l.1356-1358: callers use the supplied path and derive none. |
| NF-04 | (on C-07) a manifest ordering violation already had a code; the shared-artifact contradiction and the missing check precedence remained | PM l.353 assigns `invalid-package` to ordering or uniqueness violations. Schema and default artifacts may be shared (l.330); only "one implementation artifact" on several declarations is invalid (l.1085). Validation "MAY stop at the first detected validation failure" (l.1067). |
| NF-05 | (on C-08) `unsupported-strategy` covers only strategies that were not advertised; a refusal to weaken isolation had no error code | LOADER l.625: an otherwise valid request using an advertised strategy and placement "MUST fail with `realization-failed` if required security or deployment controls cannot be established". `unsupported-strategy` keeps its meaning (l.377, l.618). |
| NF-07 | (on CM-02) the schema root below a common-schema reference was already fixed; the hash payload label and supporting-schema imports were not | HASH l.608-609: the reference payload keeps the importing document's root, and "Its child and that child's descendants MUST use the referenced document's root in field `1`", for common and supporting imports alike. Vectors: Appendix B.4 (l.1287). |
| NF-08 | (on CM-03) the commitment model was not silent on importing callable declarations; the undefined term was "permitted kind" | COMMITMENT l.548: "An imported reference MUST target a named type declaration." That fixes the "permitted kind" of l.1085 and excludes the method request and response declarations of the common schema (l.602-603). |
| NF-09 | (on CM-06) the closed ordered list of selection tests already rules out literals nested in containers; only table rows were missing | COMMITMENT l.368-369: literal collection follows references and choice arms and "MUST NOT descend into map fields, list elements, or tuple positions within that value". The table marks `["a"] / ["b"]` Invalid (l.412). |
| NF-10 | (on CM-10) whether `0*` and `*1` are rejected or normalized turned on an undefined notion of construct identity | cdCDDLe l.169-170: "Source occurrence indicators with explicit numeric bounds MUST be rejected, even when their cardinality equals that of a supported form." The next sentence names `0*` in arrays and `*1` in maps. |
| NF-11 | (on CM-12) rejecting a named range bound already followed from the text; only an explicit statement was missing | cdCDDLe l.172-173: "Range bounds, including those in `.size` controllers, MUST be integer literals written directly in the source." Named references as range bounds are rejected. |
| NF-12 | (on EC-09) enrollment is not a Runtime Control method, so it has no method failure that needs an error code | RUNTIME l.2645: "Enrollment validation is a provisioning requirement, not a Runtime Control method." A provisioning interface that uses the shared error registry reports malformed, stale or conflicting records as `INVALID_PARAMS` and authentication or authorization failure as `NOT_AUTHORISED` (l.2646-2647). |
| NF-13 | (on EC-11) symbol defects that static registration cannot detect are binding-time failures reported by the Loader, not a missing registration code | RUNTIME l.3915-3918 lists the table defects rejected at registration with `LOGOS_ERR_INVALID_PARAMS` and defers checks that depend on the call surface to implementation binding, where the Loader reports `abi-invalid` (LOADER l.400). |
| NF-14 | (on CA-05) the audit query has no cursor and a fixed order; only the grant list's order and cursors were open | CA l.697-706: grants are ordered by ascending grant-id bytes, continuation is live and strictly after the last returned ID, cursors are consumer-bound and may expire. Audit: newest first, `since` inclusive, `until` exclusive, no pagination (l.1159-1163). |
| NF-15 | (on CA-06) a route-establishment decision cannot be recorded on a call audit record, which needs one call scope with one method | CA l.1219-1223: the record carries the decision "actually applied to authorize the call and the exact enforced call scope"; "a decision authorizing only route establishment or renewal does not authorize a call". A cached call decision may be used. |
| NF-16 | (on HC-13) the authority contract can express a per-call decision; the Runtime text never said when a call is evaluated | RUNTIME l.1641-1644: before dispatching a provider method "Runtime MUST authorize the authenticated consumer's call on the selected route, provider, contract and method"; route authority is not enough, and a valid cached call decision may satisfy the check. |
| NF-17 | (on RT-06) the text did not say when a package declaration is selected or whether stop then start selects again | RUNTIME l.3481: creation selects the declaration. l.3506: starting an existing instance "MUST use its retained accepted declaration and MUST NOT select a replacement declaration". A package update never reselects; an upgrade is a new instance (l.3411-3412). |
| NF-18 | (on RT-05) a replacement Loader reports unknown identifiers as absent or released, hiding realizations left by the Loader it replaced | RUNTIME l.3684: "A replacement Loader's empty registry or successful release of an unknown identifier does not establish that confirmation." Runtime keeps cleanup ownership, reports `unknown` (l.3398) and realizes no replacement until termination is confirmed (l.3683, l.3688). |
| NF-20 | (on SO-09) a long-running-operation pattern already existed in the transport text; the defect was that it was underspecified, not absent | TRANSPORT l.826-843 states three shapes: one delayed result through the method's own final Response, intermediate events to subscriptions activated before the call, and a contract-defined resource with start, inspect, read and cancel methods. No generic job protocol. |
| NF-21 | (on C-12) the upward dependency also covers package-manager handoff records and Loader binding identifiers, and the Runtime references omitted all three specifications | BCP §1.1 lists the Runtime dependencies on Package Manager and Module Loader definitions as exceptions to the layer direction (l.85-86), next to the Capability Authority ones. RUNTIME's normative references name all three (l.4180-4182). |
| NF-24 | (on HC-02) broadcast events expose each consumer's operation identifiers, timing and progress to every other authorized subscriber | RUNTIME l.1173-1179: an invocation-scoped publication uses a protected destination bound to the admitted invocation and "selects only active subscriptions for the named event within that invocation path". The result returns in the method's own Response (TRANSPORT l.826). |
| NF-06 (on C-09) | What it means for a grant target owned by another Runtime to resolve. | CA l.77: "A grant target whose `runtime_instance_id` names another Runtime resolves when that Runtime is enrolled with the issuing Runtime; issuance does not verify that the target instance exists." Such a grant supports authority only for a consumer accepted under the forwarding rules of RUNTIME §9 (CA l.78). |

### Findings of this document

The TF- and TL- identifiers that section 3 does not list. Each is settled by the rule named in the last
column.

| Item | Subject | Outcome |
|---|---|---|
| TF-01 | Whether the Runtime and Transport may be required to know payload schemas, given that schema validation and commitment checks happen at their boundaries. | Payloads "MUST be validated against their declarations before provider method code executes or an event is delivered"; the specification that defines the boundary assigns the validation, and "the module dispatch layer MAY repeat it" (INTERFACE l.3087-3088). Envelope validation excludes the payload maps, which are validated at the schema-aware receiving boundary (TRANSPORT l.1169-1170). |
| TF-02 | How long the state directory stays available while a module is destroyed. | "The corresponding module-visible directory mapping remains established until `_MODULE_destroy()` returns" (INTERFACE l.1596), the same lifetime as the other initialization bindings (l.1592). |
| TF-04 | Whether a route may be established for a contract that the consumer's declaration does not list, and what normative effect the declared requirements have. | "Absence of a contract from `requires` does not by itself cause Runtime to reject `establish_route`", and "Authority policy MAY use declared provider requirements as decision input" (RUNTIME l.1364-1365). A requirement selects no provider, grants no authority, and creates no package dependency or lifecycle ordering (l.713, l.1363). |
| TF-05 | Which inputs route establishment and the facade rules use to validate the selected contract. | Step 5 validates "that the provider exposes the selected contract commitment as its primary contract, an implemented interface contract, or an extended contract established under Section 8" (RUNTIME l.2995). Revocation and facade readiness use exact-contract wording (l.3121, l.3178, l.3195), and a mapped facade record keeps "the selected contract commitment" (l.3189). |
| TF-08 | Whether an instance of a statically linked module continues across a relink of the host, given that nothing identified the linked implementation across two builds. | The instance "remains realizable only while protected registration supplies that binding identifier with declaration facts equal to the instance's retained accepted declaration" (RUNTIME l.1319). The same identifier asserts continuity; an incompatible implementation takes a different identifier and a replacement instance (l.1320). Otherwise Runtime does not realize the instance, which stays `unloaded` with `static-binding-mismatch` (l.1321-1322). |
| TF-11 | Which bytes a raw line break inside an unprefixed byte-string literal contributes to the literal's value. | None: "An implementation MUST reject an unprefixed byte-string literal that contains a raw line break" (cdCDDLe l.121). |
| TF-12 | What an installed package's recorded dependency edges contribute when a later resolution reaches that package. | The record's `resolved_dependencies` entries "replace its manifest dependency requirements and become accumulated requirements for exactly the recorded version and manifest commitment" (PM l.1304). An excluded version or commitment "is neither considered nor charged" (l.1305), and a conflict with another accumulated requirement makes resolution backtrack (l.1307). |
| TF-13 | Whether the verified views of two vectors, whose schema identities are arbitrary bytes, can be checked by a verification procedure that needs a schema construction input. | HASH l.1234-1237: the identities "are not computed from schema construction input"; for the views of B.1 and B.2 "the verifier MUST use them as the computed roots compared in step 2 of the procedure in Section 8"; in steps 3 and 4 the selected schema "is a list of `uint16` values in B.1 and a byte string in B.2"; and "All other checks of Section 8 apply unchanged." |
| TF-14 | How dependency depth is counted for a package name reached by paths of different lengths, and whether selecting the root is charged against the consideration and attempt limits. | PM l.1257: "The dependency depth of a package name is the greatest number of manifest dependency edges on any path from the root to that name in the partial closure." PM l.1260 has the depth limit verified again "When an added dependency edge increases the depth of a package name already in the partial closure". PM l.1264: "examining a root candidate is a candidate consideration, and binding the root is a candidate-assignment attempt". |
| TF-15 | Which code a new operation gets through a route handle whose connection failed for no known authorization or readiness cause while the route stays `ready`. | RUNTIME l.1264: "If the handle's invocation path has ended while its route remains `ready` and neither cause is known, a new operation through that handle MUST produce `TRANSPORT_ERROR`." |
| TF-17 | What state and failure the routes of a stopped consumer have, what `close_route` does to a route that has already failed or been revoked, and what becomes of a route whose renewal is denied. | RUNTIME l.589-591: "During a stop other than an unexpected realization failure, Runtime MUST close every route whose consumer is that module instance", and it fails them for such a failure; RUNTIME l.2432 defines `consumer-unavailable` as "The route consumer's realization has failed." RUNTIME l.3350: "Closing a route that is already `closed`, `failed`, or `revoked` succeeds without changing its state or failure record." RUNTIME l.3096: "When the renewal authority check denies the route, Runtime MUST place the route in `revoked` state with failure code `authority-denied`." |
| TF-19 | Which allocated status codes provider code may return, and what the ABI caller does with a code that carries a Runtime meaning. | INTERFACE l.3308-3309: "Provider code MAY return or complete with `LOGOS_OK`, `LOGOS_ERR_METHOD_NOT_FOUND`, `LOGOS_ERR_INVALID_PARAMS`, or `LOGOS_ERR_MODULE`", and `LOGOS_ERR_CANCELLED` "only for an invocation whose cancellation is known at the provider boundary, and any other status code violates these rules". INTERFACE l.3310-3311: the ABI caller validates the status code, and "A provider result violating these rules MUST be treated as `LOGOS_ERR_MODULE`". INTERFACE l.3134: the direct-mode status passes through "after the provider-result validation required by Section 5.1". |
| TF-21 | Which rule yields when a direct publication reaches a subscription whose handler is active on another thread, since delivery on the publishing thread and one thread at a time for each subscription cannot both hold. | INTERFACE l.1406-1408: "the binding MUST queue that delivery with a copy of its event data instead of waiting"; the thread running the active invocation runs the queued deliveries "in publication order before another thread may begin a handler invocation for it"; and "Deactivation of the subscription discards its queued deliveries." INTERFACE l.1920 excepts "a delivery queued under Section 2.5" from the rule that publication does not return before the callback completes. |
| TF-23 | Which code a call gets when it was admitted and the end of its route then ends it, and what that code says about execution by the provider. | RUNTIME l.1271-1272: "An admitted call that route closure, failure, revocation, or expiry ends before a valid final result is accepted MUST complete with `TRANSPORT_ERROR`", and "That code does not prove that the provider did not execute the call." INTERFACE l.2026: "A binding failure that ends an admitted call produces `TRANSPORT_ERROR`, which does not prove that the provider did not execute the call." TRANSPORT l.979 gives the same code on a terminated session: "requests without a terminal Response still fail with `TRANSPORT_ERROR`". |
| TF-24 | Whether activating an event subscription needs the subscriber's own authority decision, and what happens to an active subscription, and how the subscriber learns of it, when that authority ends while the route stays usable. | RUNTIME l.950 requires "an allow decision for the consumer to subscribe to that event on that route; a denial MUST produce `NOT_AUTHORISED` without creating a subscription", and RUNTIME l.1633 lists "activating an event subscription and delivering an event" among the operations that need an allow decision. RUNTIME l.951: when that authority ends "while the route remains usable, Runtime MUST end that subscription, and the binding reports the end with `NOT_AUTHORISED`". INTERFACE l.1476-1479 defines `observe_subscription_end`, whose reason "is `NOT_AUTHORISED` when authority to receive the event has ended or can no longer be established", and TRANSPORT l.752-753 defines the SubscriptionEnd message for a transported route. |
| TF-26 | The execution intent of an instance that startup realizes, its origin, the authority a later recovery is checked against, and whether startup overrides a retained `stopped` intent of orchestration. | Startup establishes `requested` intent for each instance it realizes, "with protected construction and deployment input as the intent's origin" (RUNTIME l.1557). Recovery or resumption of that intent uses the bootstrap policy current at that time as the origin's execution authority (RUNTIME l.1558). Startup establishes orchestration even when its retained intent is `stopped`, and replaces that intent with `requested` (RUNTIME l.1559). |
| TF-28 | The lifecycle state when an explicit stop outlives its drain deadline, the state when its cleanup ends later, and what `stop_module` does for an instance in `error` whose cleanup is unresolved. | Expiry "does not change `stopping`", and the instance reports `cleanup-timeout` until the stop completes or its cleanup fails; "When the pending cleanup then completes, the explicit stop completes successfully", and a cleanup failure gives `error` (RUNTIME l.575-577). A `stop_module` for an instance in `error` moves it to `stopping`, starts no second destruction, and completes when the unresolved cleanup completes (RUNTIME l.1733-1734). An instance that is `stopping` when a live reconfiguration becomes indeterminate remains `stopping` (CONFIG l.328-329). A successful forced release establishes that no cleanup obligation remains and does not prove that destruction returned (LOADER l.579-580), so a stop whose envelope the permitted escalation ended completes in the same way. |
| TF-30 | The code of four required refusals: a target owned by another Runtime, `create_module` with no selected declaration, a configuration state too large for a frame, and a revision or state that cannot advance or be persisted. | A target module-instance address that names another Runtime gives `INVALID_PARAMS` (RUNTIME l.1806). `create_module` with no selected declaration, or with an unavailable exact selection, gives the `declaration-unavailable` error to a caller authorized to create an instance of the module, and the non-revealing `NOT_AUTHORISED` to every other caller (RUNTIME l.3487-3488, l.1822). A resulting configuration state over the response-size limit gives `INVALID_PARAMS` without validation detail (CONFIG l.198). A revision that cannot advance, or a resulting state that cannot be persisted, gives `MODULE_ERROR` (RUNTIME l.1812). |
| TF-31 | The code and the record of the refusal of an ordinary caller's authority request that names another consumer or carries `execution_renewal`, and whether an ordinary caller can be authorized to call `evaluate`. | On an ordinary routed call Runtime rejects a supplied `consumer` that differs from the authenticated caller "with `NOT_AUTHORISED` without dispatch and MUST NOT replace it"; the rejection is an invocation-authorization failure at the Runtime boundary, neither a policy denial nor an evaluation failure, and requires no Capability Authority audit record (CA l.93-94). `execution_renewal` on a request from an ordinary caller is rejected with `NOT_AUTHORISED` without dispatch (CA l.571). A provider-access grant for `evaluate` permits an ordinary consumer to request evaluation "only with itself as `consumer`" (CA l.1421). |
| TF-32 | Which permission scopes an execution decision must cover: those of the module's declaration or those of the instance's saved settings. | "The required permission scopes of an execution decision are those mapped from the target instance's saved permission settings", and a declared permission that those settings omit "is denied and does not by itself prevent execution" (CA l.368-369). |
| TF-34 | Which field of a record each selector of a Runtime Control scope is compared with, what a selector means for a record without that field, and which authority discloses the consumer of a route. | A selector is compared with the subject's own field: `routes` with its route identifier, `providers` with its provider address, `modules` with its module name and `instances` with its module instance identifier; for a route record the last three are compared with `target_provider`, `module` and `instance`, "never with its `consumer`" (CA l.303-304). "A present selector whose field the subject does not carry does not match" (CA l.305). "Authority to observe a route record discloses that route's consumer" (CA l.306). |
| TF-35 | What Runtime may do with a local Runtime Control subscription that it cannot keep serving, and how the subscriber learns that the subscription has ended. | A binding "MUST NOT discard an individual event admitted to an active subscription; it delivers every such event in order or ends the subscription" (INTERFACE l.1472), and it may end one "when its pending deliveries reach an implementation-documented bound" (INTERFACE l.1473). The committing operation is not held up: "Completion of that operation MUST NOT wait for the handler" (RUNTIME l.1109). "The Runtime Control binding and the route handle each provide `observe_subscription_end` to report binding-ended subscriptions" (INTERFACE l.1476); the callback receives the subscription identifier and a reason, `NOT_AUTHORISED` when authority to receive the event has ended and `MODULE_ERROR` for every other cause (INTERFACE l.1478-1479). |
| TF-36 | Whether a realization mechanism that is not the Module Loader may report LOADER's strategy names and its `loader-` failure classifications. | It may not. "A realization not performed by a bound Module Loader provider MUST use `implementation-specific`" (RUNTIME l.3393). The `loader-` classifications apply "When the cause is a typed error returned by a bound Module Loader provider" (RUNTIME l.3607), and "An implementation-local realization mechanism MUST NOT report a `loader-` classification" (RUNTIME l.3608). |
| TL-01 | Whether `logos_types.h` declares every common-schema type, and by which rule the declarations are derived. | Six common types have fixed C names (INTERFACE l.803-810), and "The fixed common declarations, including their aggregate tags, discriminant types, arm constants, and literal constants, are those listed in Section 5.2" (INTERFACE l.813). The listing "states those declarations completely; a tool copies them and does not derive them" (INTERFACE l.3325) and prints them at l.3412-3473. `logos.schema_request` and `logos.schema_response` "have no C declaration" (INTERFACE l.815). |
| TL-02 | Whether the Credential Store specification and contract that other specifications name are part of the set. | CREDENTIAL STORE is one of the specifications. It names the module `logos_credential_store` and the namespace `logos.credential_store`, and "The CDDL block in Section 3 is the complete module contract schema" (CREDENTIAL STORE l.26-27; the block is at l.161-304). SECURITY l.588 lists it among the Core specifications. |
| TL-05 | Whether another specification can use the Loader's realization descriptor and the Package Manager's records by referencing them from its own schema. | The ownership sentences name the mechanism that exists. Other specifications "use it only through the Module Loader contract or define their own wire projections of it" (LOADER l.142), and they "obtain package facts through the Package Manager contract or define their own wire projections of these records" (PM l.1805). "A projection has its own schema subtree root and keeps the meaning defined here" (PM l.1806; LOADER l.143 says the same). |
| TL-07 | Which module-state transitions are legal, including a stop during a start, a failed cleanup and a stop from `error`. | RUNTIME §3.4 l.515-526 is a table of the transitions with the trigger of each. It has `loaded` to `stopping`, `stopping` to `error` and `error` to `stopping`, and "Runtime MUST NOT perform any other module-state transition" (RUNTIME l.528). "A `stop_module` request for an instance in `error` transitions it to `stopping`" (RUNTIME l.1733). |
| TL-09 | Which `state_revision` the configuration summary reports for an instance whose declaration has no configuration binding. | "For such a module instance, `get_configuration_summary` reports `state_revision` zero and omits the other summary fields" (CONFIG l.51). |
| TL-10 | What two fields and one set of literals mean, and whether `route_id` has a row in the object table. | Each has its sentence. `applied_value_revision` is "the value revision of the record made current" (CONFIG l.315). The `reason` of `close_route` "is diagnostic text for Runtime observation and audit; it is not delivered to the provider and does not change the closure outcome" (RUNTIME l.3353). PM l.1787-1788 says what each of the five progress phases covers, and that "the phases have no required order". `route_id` has its row in the object table (RUNTIME l.1853). |

## Appendix B — Earlier items the owner declined

Items where the response keeps the boundary where it was: the matter stays outside Core, or is left to an
implementation, a deployment or a profile. The specs are consistent on each point, so nothing further is
asked. The outcome column says what the specs state and what an implementer or a deployment does
instead.

| Item | Subject | Outcome |
|---|---|---|
| C-10 | Whether the Loader `realize_request` carries the provider endpoint it must use, and what its idempotency rule compares. | Declined: the handoffs stay private. LOADER l.16: "It does not make a Module Loader provider substitutable across Runtime implementations, because the private realization handoffs are implementation-defined." A Runtime and its Loader settle the endpoint, and what counts as the same handoff, outside the contract. |
| RT-01 | No defined way for a command-line tool, which is not a module instance, to reach a running Runtime. | Activation is protected deployment input that must resolve to an accepted declaration realized by the Loader (BCP l.389-393). BCP l.395 assigns no activation encoding or terminal protocol; each deployment documents its own (RUNTIME l.1711). |
| CA-02 | How consumer attributes that policy depends on reach an external Capability Authority. | No attribute field or query protocol is defined (CA l.118). A deployment whose policy needs attributes defines a protected attribute-source integration with authoritative sources, freshness and failure rules; missing facts fail evaluation (CA l.104-109). |
| CA-07 | No method or format for exporting signed call-evidence containers. | `query_audit` returns audit records, not evidence containers, and no retrieval method is added. Export goes through a documented, protected deployment integration that authorizes the complete record and each included proof (CA l.1364-1369). |
| PM-01 | What the LGX source fields `storage` and `object` name, and how `object` is encoded. | `storage` names a deployment-configured Storage binding and `object` is an opaque locator; the retrieval API and locator encoding are implementation-defined and documented, so locators carry over only between compatible deployments (PM l.854-858). |
| PM-02 | Packages come only from Storage or Nix; no local-file source, and no described way to obtain the first Storage provider. | `package_source` stays `lgx` or `nix` (PM l.789-801). The first Package Manager and Storage providers arrive as protected deployment input, without a source record or an installed record (PM l.1460-1462). |
| PM-10 | No registry of platform `os`, `architecture` and `abi` values for producers and Package Managers to share. | No global registry (PM l.957). The deployment profile defines the supported values and matching rules; a value with no rule does not match; cross-deployment packages need compatible definitions (PM l.951-957). |
| PM-15 | No optional or platform-conditional package dependencies. | Dependencies are unconditional and apply to every variant, and platform selection never omits one. A producer whose platforms need different dependency sets publishes separate packages (PM l.1220-1222), which may be separately signed packages with the same package identity for different platforms (PM l.960). |
| SO-01 | No common catalog document, catalog location, refresh operation or catalog-policy format. | Catalog formats, acquisition, refresh and catalog-policy configuration are implementation-defined and must be documented; only the catalog entry record is common (PM l.834-835, l.841-844). Two implementations share catalogs only by agreement. |
| SO-02 | No common Storage fetch contract for the Package Manager to retrieve package objects. | No common fetch interface is required of Storage providers (PM l.1458). The retrieval API and locator encoding of each Storage binding are implementation-defined and documented (PM l.857), so a Package Manager works with the Storage bindings its deployment configures. |
| SO-03 | No standard formats for protected deployment inputs such as bootstrap pins, trust anchors, enrollments, policies and limits. | Encodings stay deployment-defined. Deployment documentation must identify the accepted representations, their provisioning, validation and replacement or revocation (BCP l.364); a representation cannot change Core value semantics (BCP l.397). Moving a deployment between implementations needs compatible tooling. |
| SO-04 | No common authority policy language and no baseline policy for deployments to start from. | RUNTIME defines no policy language (l.1614-1615); default deny stays mandatory (l.1598). Each deployment documents its policy input format and the explicit permissions its bootstrap and system-service integrations need (BCP l.365). |
| SO-05 | No common permission vocabulary (network, filesystem, devices) that a package can request across deployments. | Permission names and constraints come from the profile that exposes a facility (CA l.393); each permission identifies its defining profile (CA l.384-385); unknown permissions are rejected (CA l.388). Packages work across deployments only where the definitions agree. |
| SO-06 | No operator principal: how a human administrator is identified, delegated authority and given an administrative path. | Humans stay outside the participant model (BCP l.105-107). Administrative software acts as an admitted module under ordinary authority (SECURITY l.541); the deployment documents how its administrative path authenticates the approving principal (BCP l.385). |
| SO-07 | No reserved namespace or prefix convention for schemas owned by an implementation. | Only the `logos.`, `logos-` and `logos_` prefixes are reserved (INTERFACE l.251). Implementations pick any other namespace; a clash surfaces through the existing collision and conflicting-identity rules when documents are combined (INTERFACE l.870, l.2266-2267). |
| SO-09 | No generic streaming or large-object profile, and no standard pattern for long-running operations. | No generic streaming or chunked transfer (RUNTIME l.3762). Contracts model chunking, references and jobs themselves (RUNTIME l.3786-3787); TRANSPORT l.826-843 describes delayed results, intermediate events and contract-owned resources as uses of ordinary methods and events. |
| NE-02 | No rule orders a call's Response before the events that call causes, so a consumer cannot correlate early events. | No ordering is required (RUNTIME l.1220); an event may arrive before submission returns (TRANSPORT l.832). The consumer subscribes first and the contract correlates by a value known before the call, such as a caller-chosen one (TRANSPORT l.833; RUNTIME l.1190-1191). |
| NE-04 | A provider is never told that a consumer's route or session ended, so per-consumer state has no release trigger. | No session-end notification. The provider learns of caller loss only for an outstanding invocation, as cancellation (INTERFACE l.2060); state tied to an open watch call is released then, and other state is a contract-defined resource with its own lease (l.420). |
| NE-05 | A slow transported subscriber either blocks the publisher or has its whole connection closed, with no bound or per-subscription policy. | Backpressure or connection closure stays at the callee's output (TRANSPORT l.792-797), and Transport ends a single subscription only when the caller's authority to receive the event ends (l.753). Each implementation must document which action occurs, under what conditions and with what wait bounds (l.803-804). A subscriber's binding never drops one admitted event; it may end that subscription at a documented pending-delivery bound and report the end with `MODULE_ERROR` (INTERFACE l.1472-1473, l.1479). A provider that must not block publishes from its own thread with a bounded latest-value queue. |
| NE-06 | Whether a provider's final events, published while it is stopping or being destroyed, are delivered was undefined. | Delivery of an event published while stopping is not guaranteed; route, subscription and authority state decide (RUNTIME l.1161-1163). A provider publishes its final state before stop is requested, from a declared preparation method. See TL-03 for route states. |
| NI-07 | Grants outlive their target instance: no orphaned status, and a grant cannot name a replacement instance. | Grant status describes the policy record, not target liveness, and a grant never moves to another instance (CA l.723-725). A replacement consumer instance needs new grants; stale ones are revoked explicitly, since retirement does not revoke (RUNTIME l.3453). |
| NL-01 | The stop grace period was undefined, and a module could not learn, declare or extend its stop time. | Drain and cleanup deadlines are deployment-supplied and documented (RUNTIME l.3699; BCP l.376); a module neither declares nor sees one. A long flush goes into a declared method called before stop (RUNTIME l.3739). A destructor may use the state directory, which stays mapped until `_MODULE_destroy()` returns (INTERFACE l.1596). |
| NL-02 | No cooperative pre-stop phase: a stopping module loses its outbound routes before its only stop hook runs. | No preparation phase; a stop still prevents the module's new outbound calls first (RUNTIME l.585-586). An orchestrator calls each module's declared preparation method before stopping it (l.3739-3740); nothing requires this on a host-initiated shutdown. The state directory stays mapped until `_MODULE_destroy()` returns (INTERFACE l.1596). |
| NL-03 | The destructor returns nothing, so a module cannot report that its final flush or close failed. | Destruction reports lifetime completion only (RUNTIME l.3738). A flush outcome is the Response of a declared method called before stop (l.3739); Runtime-observed cleanup problems appear as `cleanup-failed` or `cleanup-timeout` (l.3605). The state directory stays mapped until `_MODULE_destroy()` returns (INTERFACE l.1596). |
| NL-05 | No suspend and resume, or background and foreground, notion exists for hosts that the operating system suspends. | There are five module states and six host operations, none for suspension (RUNTIME l.530-535, l.3826-3833); background work is left to platform profiles (SECURITY l.408-409). A module checkpoints to its state directory and tolerates termination without destruction (INTERFACE l.1577). |
| NL-08 | Core has no liveness source, so a module whose dispatch hangs stays `ready`. | Readiness does not guarantee continued progress (RUNTIME l.543) and a failed call is not a realization failure (l.3655). A caller bounds each call with `timeout_ms` (INTERFACE l.2016); hang detection is left to deployment supervision or a contract's own status method. |
| NL-09 | Long-running operations lack a common idempotency key, durable operation handle and resynchronization shape. | A delayed result uses the method's own deferred Response (TRANSPORT l.826-828). Anything spanning invocations is a contract-defined resource (l.836; INTERFACE l.420); each contract defines its durability, idempotency and resynchronization, with no generic job protocol (TRANSPORT l.843). |
| NA-01 | A consumer denied while a person's approval is pending cannot tell that from a permanent refusal. | The denial stays opaque: an application "MUST NOT infer an approval request or pending approval from `NOT_AUTHORISED`" (RUNTIME l.701). The consumer learns a pending state from the approval module's own contract (l.700) and makes a new attempt later (l.702-703). |
| NA-02 | An approval module gets no notification of a pending denial and no presentable description of the requested scope. | No approval queue, event or record. The approval module keeps its own state under an ordinary contract (RUNTIME l.700); its display separates authenticated scope from supplied descriptions (BCP l.386), and presentation authority gives no discovery or audit access (SECURITY l.546). |
| NA-06 | A provider that enforces a permission per caller has no way to learn the caller's allowed scope. | No Core check method. A provider-enforced permission must define its own authorization integration, which an ordinary contract may supply (CA l.417-419). The provider sees the caller's address (INTERFACE l.2140-2141), which is not authorization (CA l.420). |
| NA-09 | A module acting for another module's request, or for a person's choice, cannot carry that requester's authority. | No delegation. A forwarding module acts under its own identity and authority (INTERFACE l.207; RUNTIME l.1251). A contract may record the requester as provenance, kept distinct from the authorizing consumer (BCP l.387); provider selection delegates nothing (SECURITY l.549). |
| NA-10 | Audit records cannot hide sensitive constraint values without dropping the whole record. | No redacted form. A returned record keeps its exact recorded scopes, or the whole record is omitted (CA l.1380-1382). Sensitive constraint values need explicit audit authorization before they are retained (l.1384). |
| NR-01 | A provider on a device that cannot accept inbound connections cannot serve consumers on another device. | The caller must reach the provider-side listener (TRANSPORT l.1179). NAT traversal, rendezvous or relay needs a deployment mechanism or a separately specified profile, and no intermediary may replace target authentication or channel binding (l.1180-1181). |
| NR-02 | Two independently owned devices have no defined exchange for enrolling each other's Runtime. | "This specification defines no pairing exchange or general provisioning method" (RUNTIME l.1714). Enrollment provisioning is supplied by the implementation or deployment (l.1713), with trust established independently of an unauthenticated connection (l.1715). |
| NR-03 | Nothing creates the local facade for a provider on another Runtime, sets its target or refreshes its address. | Facades are created and targeted by "protected deployment input or an authorized implementation-defined management operation" (RUNTIME l.1708). A changed locator is authenticated against the configured target and never retargets an established route (l.1709). |
| NR-07 | No keepalive or idle rule, so a call to a sleeping remote peer can hang; fresh remote state is undefined. | No keepalive. Facade readiness needs fresh evidence under a Runtime policy that says when the evidence lapses; an open carrier is not enough (RUNTIME l.3621-3622). Callers bound each call with a timeout (INTERFACE l.2016) and observe path loss (l.1442). |
| NR-08 | No bound on in-flight requests, no common overload result, and control messages queue behind large frames. | Implementations enforce and document finite limits and their exhaustion behaviour (TRANSPORT l.1329-1331), choosing delay, rejection or close (l.1336). There is no common retryable overload response or control-latency bound, and Cancel cannot overtake a committed frame (l.1343-1344). |
| NR-13 | A local Unix-socket address for Runtime Control was typed and shown in an example without any consumer-binding rule. | The Unix address form "does not define a general local Runtime Control access profile" (RUNTIME l.1710), and the example now shows a remote endpoint (l.4017-4029). An external local process enters through deployment-defined activation (l.1711; BCP l.389-390). |
| NR-14 | The local socket profile checks the peer by user identity, so a same-user module can impersonate a provider. | Stated as a limit: a shared user identity "is not an isolation boundary", and mode bits do not stop endpoint replacement (TRANSPORT l.1088-1089). A deployment claiming that protection must prevent substitution or fail the placement (l.1090). No mechanism is defined. |
| ND-01 | A common type for integers wider than 64 bits and for decimal amounts, so generic clients can render them. | Integer types end at 64 bits (INTERFACE l.451) and no numeric profile exists (COMMITMENT l.760). A contract carries a wider value in a `bstr` or `tstr` and defines its meaning (INTERFACE l.471); generic clients cannot interpret it. |
| ND-02 | A common timestamp and duration type for all contracts. | No common alias. Capability Authority and Runtime Control each state whole milliseconds since 1970 for their own fields (CA l.537; RUNTIME l.2940). Every other contract defines the epoch, unit and clock of its time values itself. |
| ND-05 | Maps with dynamic keys, or a standard list-of-pairs convention with declared key uniqueness and set semantics. | Dynamic-key maps are not allowed (INTERFACE l.467). A contract uses a list of records and defines key equality, duplicates and order itself (l.3095); list order is part of the value (COMMITMENT l.862). See ND-04 for the specs' own lists. |
| ND-06 | A declarable opaque-payload type for contracts that forward externally defined formats such as JSON. | No opaque or JSON type. A contract may carry an external encoding in a `bstr` or `tstr` and define it (INTERFACE l.471); generic validation does not check it and the commitment covers the bytes or text only (l.472-473). |
| ND-07 | A common record and response convention for domain failures, so generic clients can tell failure from success. | No common error record. Each contract represents an expected domain failure in its own response schema (INTERFACE l.345), returned as a valid response (l.3123-3124). A generic client shows the response and needs the contract to interpret it. |
| ND-09 | A surface for human-readable descriptions of contracts and methods. | No description surface. Comments are not schema identity inputs and may differ after reconstruction (INTERFACE l.2599). Descriptions travel outside the contract, as application-defined material; a package can carry the contract documents themselves in `contract_documents`, whose entries have no description field (PM l.256-260, l.355-356). |
| NP-01 | Signed display metadata (name, description, icon, publisher) in packages and catalog entries, so a store can browse without downloading. | Core catalog entries carry location data only (PM l.867-868). Display metadata and search belong to an application catalog contract, which must separate unverified claims from verified facts (l.873-874); display names establish no trust (l.876). See also TS-06 (contract documents). |
| NP-02 | An executable or bundle artifact kind, so a module can ship and launch its own separately signed helper program. | No executable artifact kind. `resource` and `data` artifacts authorize no execution (PM l.1189) and no executable-bundle realization form exists (l.1193). A deployment that needs a helper program provisions it outside the package, under its own controls. |
| NP-03 | A package form for presentation modules: view-only modules, entry view, icon, and defined `resource` and `data` kinds. | `resource` and `data` are defined (PM l.1188). No view-only form (l.1193): a presentation module is an ordinary module (RUNTIME l.3753) with an adapter exporting the native ABI (LOADER l.203). Entry views and icons belong to a presentation profile. |
| NP-04 | A way for a signed package to describe a statically linked module, as on mobile hosts. | Core defines no package-to-static-registration handoff (RUNTIME l.1316). A deployment that keeps signed declarations for a statically linked module verifies them and binds the accepted facts to the linked code through protected registration (l.1317). |
| NP-06 | A package field stating a minimum Runtime ABI or OS version, checked when the platform variant is selected. | No version-range field. The deployment profile defines the `os`, `architecture` and `abi` values and their matching rules, including ABI or version constraints (PM l.951); a value without a rule never matches (l.954). No global registry (l.957). |
| NP-09 | A declarative home for platform-integration material such as device rules, usage descriptions and entitlements, with an install-time check. | No such artifact kind. The deployment documents the protected administration of operating-system integration material (BCP l.380); installation grants no device consent and authorizes no package-supplied system rules (l.381). A missing facility fails the dependent realization, not the installation (l.382). |
| NC-01 | A change to a module's configuration schema leaves installed instances unable to start, with no migration hook or fallback. | No hook, automatic migration or default fallback. An unchanged declaration keeps its records (CONFIG l.252); a changed schema needs a replacement instance (l.255), and the deployment names the workflow that transforms and supplies the old value (l.263, l.266). |
| NC-02 | Accepting a package default is optional, a start without a value has no error code, and no reset exists. | Default acceptance stays a documented deployment choice (CONFIG l.134, l.141). A start without an eligible value fails with `NOT_READY` (l.125). Reset is an explicit complete replacement, with no default-retrieval method (l.135-136). |
| NC-04 | A module cannot declare that it needs persistent state, and state has no class, size or backup semantics. | No declaration field, classes or sizes. A state requirement travels in deployment input or a profile-defined permission's constraints (RUNTIME l.1353); a deployment accepting one defines its carrier, and start fails when it cannot be supplied (l.1389-1390). |
| NC-06 | A user-selected file's operating-system capability cannot be handed from the module that obtained it to another module. | No capability carrier. A broker contract keeps the platform capability at its provider (RUNTIME l.3778); a profile that transfers it must define binding, operations, lifetime and revocation (l.3779). A path or descriptor value in a payload grants nothing (l.3780). |
| NO-03 | Per-instance resource usage observation, a declared expected footprint, and a typed signal when a resource limit is hit. | No usage method, footprint declaration or limit event. Usage reporting is left to an ordinary module contract that defines its own measurement; the informative observer section defines no contract (BCP l.543, l.553). Resource accounting appears only as enforcement (CA l.411-412). |
| NO-04 | A Runtime self-description method, and the package identity on each module record, for diagnostics and version reporting. | No self-description method, and the module record has no package field (RUNTIME l.1954-1968). A client calls `get_execution_summary` per instance and reads `selection.package` (l.3378, l.3390). Implementation version reporting stays in host diagnostics. |
| NF-19 | (on PM-10) citation correction only; the request for a registry of platform values and a defined runtime profile is unchanged | PM l.951-957: the deployment profile defines the `os`, `architecture` and `abi` values and their matching rules; "A value with no defined matching rule MUST NOT match". No global registry. Producers and installers share one deployment's definitions. |
| NF-22 | (on HC-12) every way to tell apart two instances of one module uses identifiers minted at creation; no alias exists beforehand | Core defines no instance alias or role name. With several matching providers Runtime selects by routing-selection state or deployment configuration (RUNTIME l.1408-1409). A management module creates the instances, keeps their identifiers and gives each consumer the provider to pin (l.3044). |
| NF-23 | (on HC-04) lifting the unique-method-name rule would not allow two revisions in one provider, because native dispatch carries no contract identity | Exact contracts and the uniqueness rule stay (INTERFACE l.319-320). A provider whose contract extends an earlier one, a relation that permits only further declarations, may also offer the earlier contract as an exact contract view (l.201-204). l.206: "Overlapping contract revisions may be supplied by separate admitted providers or explicit adapters." A provider keeps an old interface contract and adds interfaces with distinct method names (l.199). |

## Appendix C — Concerns of `human-spec-comments.md` that the current specs settle

These eleven concerns have no reply, but the current text either meets the need or places it outside Core,
as the last column states.

| Item | Concern | In the current specs |
|---|---|---|
| HC-01 | Two modules can share a name and a contract yet behave differently, and a consumer can neither tell them apart nor choose between them. | The verified signer and package of an instance's selection are observable as provenance, not publisher identity (RUNTIME l.3384-3390). Equal names or commitments establish no equal behaviour; provider selection and execution policy choose (l.1367-1369). A route request can pin one provider (l.3044). |
| HC-03 | A method body cannot see which consumer is calling it, so a provider cannot apply per-caller policy unless grants can constrain parameter values. | A method reads its caller's authenticated Runtime and module-instance identifiers through the invocation context (INTERFACE l.2121-2145; RUNTIME l.833-837). The view carries no module name (INTERFACE l.3533-3537). Caller identity is a fact, not authorization (CA l.417-420). No scope constrains parameter values (CA l.149-153). |
| HC-04 | A caller is bound to an exact contract root, so even adding a method breaks every existing caller. | A contract that only adds declarations extends the earlier one (COMMITMENT l.966-972), and its provider may keep serving the earlier root: "A provider whose contract extends an earlier contract under LOGOS-MODULE-COMMITMENT-MODEL MAY additionally offer that earlier contract as an exact contract view." (INTERFACE l.201). Existing callers keep their root. "Adding declarations is the only change an extension permits." (l.204). |
| HC-05 | Calls block the caller, which must dedicate a thread to each outstanding call to get asynchrony. | Runtime Control and route bindings must provide `prepare_call`, for synchronous providers too (INTERFACE l.1969-1972). Several prepared calls may be outstanding on one route handle (RUNTIME l.1285-1286), completing by callback (INTERFACE l.2010). A synchronous `call` stays serialized per handle (INTERFACE l.1935-1936). |
| HC-06 | A call has no configurable timeout and cannot be cancelled through the native interface, and it is unclear whether timeouts are the caller's job. | A prepared call takes a caller-selected timeout from submission (INTERFACE l.2016) and ends with `TIMEOUT` or, after `cancel`, `CANCELLED` (l.2024). Runtime arranges Transport Cancel on a live session (l.2032); the provider sees sticky cancellation and an optional hook (l.2102-2103). A synchronous `call` has neither (l.3760-3767). |
| HC-08 | Modules pass host file paths to each other; a path loses its meaning when the provider runs on another machine or in a sandbox. | A path grants no access or visibility in another realization (RUNTIME l.3776); co-location gives no shared namespace (l.3783). A contract accepting a path must define whose namespace it addresses (l.3784), and a provider must not silently reinterpret a caller-local path (l.3785). Values, chunks or references can carry content (l.3786). |
| HC-09 | There is no unified logging: no common log level set once for every module, and no way to collect module logs through contracts. | Core defines no logging facility, level or retrieval contract. Optional diagnostic logging is left to ordinary module contracts and deployment integration, which must define attribution, authorized access, sensitive-data handling, retention and delivery bounds (BCP l.557-558). Its failure does not waive audit or enforcement (l.559). |
| HC-10 | Publishing an event returns nothing, so a module that publishes an invalid event gets no signal. | INTERFACE l.3351: "The publish callback returns `LOGOS_OK` when the event name is declared by the publishing module's contracts and the event data conforms to that event's data type and size limits, and `INVALID_PARAMS` otherwise." The result does not report delivery (l.3352); a failure for one subscriber route is a diagnostic (RUNTIME l.1149). |
| HC-11 | The order of C parameters, struct fields and choice arms is unstable: adding a field or an arm can move existing ones. | Fields and parameters are ordered by field-name bytes (INTERFACE l.867), choice discriminants by label order or canonical index (l.1126-1128). Source order is not ABI-visible (l.869); placement of independent declarations is outside the canonical mapping (l.865). The order is deterministic, not append-stable; a reordering change is also a new root (HC-04). |
| HC-12 | A module instance has no alias or stable name: the creator gets an opaque identifier, and everyone else must discover it. | `create_module_request` carries only `request_key` and `module` (RUNTIME l.2140-2143), and the key is idempotency only (l.3496). Lifecycle requests select an exact instance or facade (l.3523, l.3532-3538); a route request can pin a provider (l.3044). The reply to NF-22 declines role names and a resolver. |
| HC-13 | There is no specified way to ask a person, at call time, whether a call should be allowed, and to hold the call meanwhile. | Each call is an authorization point (RUNTIME l.1641-1644). A denial is opaque and final: no pending approval may be inferred, and a later approval does not resume the attempt (l.701-702). Approval workflows are ordinary module contracts (l.700); a method may hold its own Response while a person decides (TRANSPORT l.826-828). |

## Appendix D — The integrator documents, claim by claim

Status words: `ok` means the specs support the claim as written, `partly` that they support it with a
stated limit, `no` that they do not provide it, and `contra` that they forbid it. Next to the identifier
of an earlier item, "declined" and "resolved" give its outcome as in Appendices A and B, and "no response
yet" means the owner has not answered it.

| # | Claim (source) | Status | Spec basis |
|---|---|---|---|
| 1 | Application code need not be a module; it calls modules through typed clients and subscribes to their events (DOCS l.137, l.139; RFP l.435-448) | contra | RUNTIME §13 l.3798, Terminology l.132; BCP §2 l.102-104. TS-01 |
| 2 | The host starts the runtime through a small C interface and needs no particular event loop (DOCS l.135) | ok | RUNTIME §13.2 l.3840. The interface is small because everything else is an opaque `configuration_format` blob (l.3899-3901): TS-01. Those encodings stay deployment-defined (SO-03, declined) |
| 3 | The application ships the runtime and the module packages in its own bundle (DOCS l.134) | partly | A bundled `.lgx` is installable only as a Storage object that a deployment-configured storage provider serves: `package_source` has no file kind (PM l.789-801; PM-02, declined). Bundled code enters as protected bootstrap input or static registration, both implementation-defined (RUNTIME l.1313-1314), and Core "defines no package-to-static-registration handoff" (l.1316; NP-04, declined) |
| 4 | Logos Core "resolves their dependencies, and manages their lifecycle" (DOCS l.136) | partly | Dependency resolution is the Package Manager's and never starts anything (RUNTIME §3.7 l.695-698, l.712-713); start order comes from orchestration and from ordering constraints with no defined representation (l.705-707; SO-03 and PM-15, declined) |
| 5 | Placement per module: own process, one runtime process, in-application; `sandbox` and `container`; start refused when the platform cannot provide the sandbox (DOCS l.102, l.145) | ok | LOADER §3 l.164-167, §4 l.255, §6 l.428; SECURITY §4 l.214. How a deployment states the per-module choice is not portable: a manifest "does not select a realization strategy or placement" (PM l.361; NP-14), and the encoding of deployment input stays deployment-defined (SO-03, declined) |
| 6 | A module can be linked statically where dynamic loading is unavailable (DOCS l.124) | ok | RUNTIME §2.3 l.375-376; LOADER l.185-187. A signed package does not describe such a module (RUNTIME l.1316-1318) |
| 7 | Signature checks: Logos keys trusted by default, users add publishers they trust (DOCS l.104) | contra | PM §4.1 l.417-419. TS-05 |
| 8 | Each package is checked when downloaded and again before it runs (DOCS l.104) | ok | PM l.364, l.388-389; LOADER l.212-215; RUNTIME §3.6 l.672-677 |
| 9 | Modules are discovered in a catalogue and downloaded over the project's storage network (DOCS l.104) | partly | Catalog formats, acquisition and the Storage retrieval API are implementation-defined and must be documented (PM l.834, l.856-859, l.1458; SO-01, SO-02, PM-01 and NP-01, declined) |
| 10 | Typed clients are generated from each module's contract; "every module publishes its contract as a CDDL schema" (DOCS l.137, l.229) | partly | A package may carry its contract documents in `contract_documents`, checked against the commitment (PM l.253, l.355-358), but the field is optional. Otherwise a realized provider discloses them (RUNTIME l.396, l.422), or they are "embedded in generated bindings or supplied with the application" (INTERFACE l.3904). TS-06 |
| 11 | A module can describe its own contract at run time (DOCS l.229) | ok | RUNTIME §2.4 l.402-404, l.422-432 |
| 12 | The same call works in-process, across processes and across machines (DOCS l.34, l.228) | partly | INTERFACE l.43-47. Paths do not travel: "Co-location alone does not establish a shared filesystem namespace" (RUNTIME §12 l.3776, l.3783-3784). No order is required between events and method responses (l.1220; NE-02, declined). No suspend and resume (NL-05, declined). Cancellation reaches the provider in every mode (INTERFACE l.2102-2103). A method marked `_sensitive` cannot be carried under the two defined remote profiles (TRANSPORT l.1188) |
| 13 | An access policy set before the runtime starts decides which modules may call which, "for example only the modules that declare a dependency" (DOCS l.189) | partly | Default-deny policy is mandatory (RUNTIME l.1546, l.1598). No policy language (SO-04, declined). A dependency or `requires` entry is never authority by itself (l.698, l.860, l.1363), and `requires` names a contract, not a module, so the rule has to be written as policy; absence of a contract from `requires` does not by itself reject `establish_route`, and policy may use declared requirements as decision input (l.1364-1365) |
| 14 | Grants per method and per event, enforced before module code runs (DOCS l.215) | ok | RUNTIME l.810-816, l.1641; TRANSPORT l.955-961 |
| 15 | Each grant can expire and be revoked individually while the node runs (DOCS l.216) | ok | CA §6. New event deliveries are among the operations re-evaluated after a policy change (CA l.931-933) |
| 16 | Every access decision leaves an audit record (DOCS l.217) | partly | An external Capability Authority returns no allow or deny decision until retention of its audit record is acknowledged (CA l.1207). How long records are kept, and whether a call leaves a `call` record, is selected by policy (CA l.1202; RUNTIME l.1661-1663, l.1671-1676; CA §9); "every" holds for calls only under a policy that says so |
| 17 | Enrolling a user's runtime is an operation a service can be authorised to perform (DOCS l.218) | partly | A scope exists (CA §3.4 l.373), and an enrollment may change through "an authorized provisioning operation" (RUNTIME l.2642-2643). No specification defines that operation: "This specification defines no pairing exchange or general provisioning method" (RUNTIME l.1714; NR-02, declined) |
| 18 | No anonymous access; each runtime is enrolled with its own keys (DOCS l.220) | ok | TRANSPORT §8.4.1 l.1221-1238 |
| 19 | Pairing by six-digit code or single-use invite; certificates issued to each side (DOCS l.199, l.235) | no | RUNTIME l.1714-1715 (NR-02, declined) |
| 20 | One runtime exports a module, the other imports it under a local name (DOCS l.199-201) | partly | Export: `set_provider_export` (RUNTIME l.2122-2128, l.2755-2771). Import: a facade created by "protected deployment input or an authorized implementation-defined management operation" (l.1708; NR-03, declined). No alias (HC-12; NF-22, declined: the response says Core does not define universal role names or a resolver) |
| 21 | Mutual TLS 1.3 with pinned keys; no downgrade (DOCS l.199, l.236) | ok | TRANSPORT l.1219-1221, l.1233-1234, l.1202-1204 |
| 22 | Each connection opens with a single-use ticket that expires within seconds and is bound to that connection (DOCS l.235) | ok | TRANSPORT l.922-925, l.1023-1024 (at most 60 s), l.1271-1277 |
| 23 | A refused caller cannot tell whether the module exists (DOCS l.237) | ok | RUNTIME l.3060-3061; TRANSPORT l.993-997 |
| 24 | Both sides send the contract hash; a mismatch refuses the connection before any call (DOCS l.238) | ok | TRANSPORT §3.1 l.476, l.484-487, l.512-518 |
| 25 | When the remote runtime restarts "the import becomes ready again"; in-flight calls fail; missed events are not redelivered (DOCS l.201) | partly | Failure and no replay: TRANSPORT l.527-529, l.541, l.550-552. After a provider restart the old routes stay dead (RUNTIME l.3672-3673, l.1273); after a mere session loss the route may stay ready and be renewed with a fresh ticket (l.3334-3338). The consumer is told that its path ended (the terminal observer, l.1277-1278), but not when the provider is back, and nothing re-subscribes (NE-07, no response yet) |
| 26 | Subscriptions work across the network without polling (DOCS l.230) | partly | While a session lives (TRANSPORT l.528). No keepalive (NR-07, declined), no suspend and resume (NL-05, declined), one connection per route (TS-04) |
| 27 | Rate limits and connection scale are left to each deployment (DOCS l.222) | partly | Limits: finite, documented, chosen by the implementation (TRANSPORT §8.6 l.1329-1332, l.1343; NR-08, declined). Connection count is fixed by the transport profile, not by deployment: TS-04 |
| 28 | A local node module and a client module that proxies a remote node are interchangeable to callers, selected by which module is loaded (DOCS l.91; RFP l.615-621, l.811-819) | ok | COMMITMENT §4 l.520-521, §9.1 l.951-957. TS-07 explains how, and what is not defined |
| 29 | One instance of the node module per execution zone (RFP l.940-947) | partly | Several instances per name are allowed (RUNTIME l.2577); `create_module_request` carries no alias and no configuration (l.2140-2143; HC-12) |
| 30 | Modules written in JavaScript or React Native (DOCS l.167; RFP l.98) | partly | Adapter inside the artifact (LOADER l.203-205). Script files are reachable only through an implementation-defined, documented convention (PM l.1181-1186), and there is "no executable-bundle or view-only realization form" (PM l.1193). TF-03 for the embedded engine's threads |
| 31 | A JSON-RPC server and client module pair for any module API (RFP l.804-819, l.843-854, l.871-873) | partly | Dynamic invocation exists (RUNTIME l.774-786). One client module cannot serve an API chosen by configuration: TS-02. No JSON projection of values: TS-03. The server acts under its own authority ("forwarding does not implicitly transfer the original consumer's authority", INTERFACE l.207; NA-09, declined), though it can read who called it (INTERFACE l.2140-2141) |
| 32 | The project's messaging network as the carrier for reaching a node (RFP l.856-863) | no | "Reachability through NAT, rendezvous, or a relay is deployment-specific unless a separately specified profile defines it" (TRANSPORT l.1179-1180; §9.3 l.1372; NR-01, declined) |
| 33 | Android: one AAR per module, registered in-process (RFP l.611-613, l.831-841) | ok | `logos_runtime_register_binding` per module (RUNTIME l.3888-3891, l.3906-3915). TS-08 |
| 34 | The application itself serves calls (provider hosting) without being a packaged module (RFP l.484-486) | partly | Only as a statically registered module, before start (RUNTIME l.3934), with the complete native ABI (TS-08) |
| 35 | Host libraries for Kotlin, Swift, Go, Dart, Rust (DOCS l.160-169; RFP l.821-829) | partly | Only the C ABI is specified; for other languages "A separately specified language mapping can provide idiomatic bindings or a language-native authoring form" (BCP §6.1 l.484-487). TF-03 for runtimes that move work between OS threads |

## Appendix E — Catalog needs and where the specs stand

The twenty needs that recur across the module catalog, the earlier items that recorded them, and what
the current specs provide for each.

| Need | Earlier items | In the current specs |
|---|---|---|
| Results delivered as broadcast events correlated by an identifier, at per-message, per-block and per-chunk rates | NE-01, NE-02, NE-05, ND-03 | Provided for correlation. Invocation-scoped events reach only subscriptions on the caller's invocation path (RUNTIME l.1173-1190). A contract may not make an identifier that is available only in the final Response the sole means of recognising an earlier event (TRANSPORT l.833). For rates there is a duty to document overflow behaviour (TRANSPORT l.803), and a subscriber's binding delivers every admitted event in order or ends the subscription, which it may do at a documented pending-delivery bound (INTERFACE l.1472-1473). |
| Late subscribers: subscribe before start, snapshot method plus transition events, history replay | NX-02, NE-02 | Partly provided. A watch method with invocation-scoped events can order one snapshot before the changes (TRANSPORT l.776-779). There is no retained-event log or replay (l.783-784). A subscription exists only while its route is ready (INTERFACE l.1430). |
| Long calls, long-polls, per-call deadlines from 2 s to unbounded, concurrent dispatch | HC-05, HC-06, NR-11, NR-12 | Provided. Prepared asynchronous calls with a per-call timeout, cancellation that reaches the provider, and deferred provider completion (INTERFACE l.1969-1970, l.2016, l.2103). An outstanding call does not occupy its route handle (RUNTIME l.1285-1286). |
| Streaming: chunk sessions, chunks as events, opaque stream handles, megabyte byte parameters | SO-09, ND-03, NR-08, NE-04 | No generic streaming or chunked-transfer facility (RUNTIME l.3762). Chunks can be addressed to one consumer as in the first row. A stream session is a resource of the contract (INTERFACE l.420). An oversized frame fails before it is sent (TRANSPORT l.377-383). See TP-06. |
| Host file paths as arguments and results | HC-08, NC-06 | No mechanism; the duty is on the contract. A contract that accepts a path "MUST define whose namespace it addresses and the applicable failure" (RUNTIME l.3784). See TP-03. |
| Bundled native libraries and resources | PM-11, NP-11 | Declined. There is no package-root directory or artifact lookup table, and access to packaged resources follows an implementation-defined, documented convention (PM l.1183, l.1186). Native library dependencies go through the deployment's dynamic-linker integration, which LOADER does not define (PM l.1184). A packaged native library is a declared artifact whose installed path stays bound to its verified bytes (PM l.1185); the Loader verifies the selected artifact only, not the libraries the dynamic linker loads for it (LOADER l.658-659). See PM-11. |
| Process-global library state, one node per process, embedded language runtimes | NP-14, HC-02 | One implementation binding may be initialised more than once, each time as a distinct instance (INTERFACE l.1572-1573). Placement is selected by Runtime or deployment policy (RUNTIME l.969). A module declaration has no field that asks for one instance per Runtime or for a process of its own (PM l.262-271), and a manifest "does not select a realization strategy or placement" (PM l.361). A module that cannot operate in a shared process must fail initialization there (RUNTIME l.1053), and a Module Host serves exactly one module instance (LOADER l.200). Process-global environment may not carry per-instance state (RUNTIME l.1397-1398). For a library's residual work after `_MODULE_destroy` see TF-03. |
| Module-owned sockets: peer-to-peer listeners, NAT mapping, HTTP servers, outbound HTTPS | SO-05 | A profile that permits platform access must define permission names and constraints for network connection, listening, destination and port access (CA l.393-396). No such profile exists, and the owner's response to SO-05 adds no permission registry. |
| A child process of a system binary; the OS keychain | NS-03, SO-05, NP-02 | Child process: there is no packaged executable form (PM l.1193), and spawning a binary that the deployment provides needs a profile-defined process permission (CA l.399); no platform permission names are defined (CA l.389). Keychain: the optional Credential Store contract lets a module create an opaque credential in a deployment-assigned slot and query its presence (CREDENTIAL STORE l.34-35, l.44, l.58). It has no retrieval method (l.36); the host integration delivers the credential to the selected component (l.459), and a provider can adapt an operating-system secret store (l.481). |
| Configuration by method call, schema migration, environment variables, secrets in configuration | NC-01, NC-02, NC-05 | Partly provided. A schema change needs a replacement instance, with values transformed outside Core (CONFIG l.255-263). Reset is an explicit complete replacement (l.135). Credentials may not be in module configuration (l.58). Environment entries do not carry per-instance values (LOADER l.224-225, l.287; RUNTIME l.1397-1398). For configuration by method call see TP-01. |
| A node lifecycle inside the loaded module, readiness states, bounded shutdown | NL-01, NL-02, NL-12 | No Core hook. Application setup uses ordinary schema methods, and application readiness belongs to the module's own contract (RUNTIME l.611-612, l.625-626). Start-up and drain deadlines are supplied by the host or deployment (l.628, l.3699). Preparation is a declared method called before the administrative stop (l.3739). |
| Liveness probing of a provider by its consumers | NL-08, NE-03 | Provided for path loss. Every route handle has `observe_end`, which needs no additional grant (INTERFACE l.1442-1444). There is no deadline for detecting a silent connection failure (l.1463). Readiness "does not guarantee continuous progress of every application operation" (RUNTIME l.543), so application health is outside Core. |
| Logging: stderr discarded, module-owned log files, run-time level | HC-09 | No logging facility. "Optional diagnostic logging can be supplied through ordinary module contracts and deployment integration" (BCP l.557). |
| Process statistics of another module | NO-03 | Declined. The owner's response to NO-03 leaves resource usage to ordinary metrics or domain contracts and adds no Runtime usage method. |
| Data shapes: JSON in strings, dynamic maps, 128-bit integers as strings, `any`, in-band error envelopes | ND-01, ND-02, ND-05, ND-06, ND-07 | An external encoding such as JSON may be carried in a `bstr` or `tstr` under the contract's own interpretation (INTERFACE l.471). `any`, floats and unkeyed maps are not available to module schemas (l.465-467). Integer aliases stop at 64 bits (l.238, l.243). The owner's responses to ND-01, ND-05 and ND-07 add no wide-integer type, map type or common error record. |
| Secrets as parameters, results and environment values | NC-05 | Provided for requests and responses through `_sensitive` (INTERFACE l.211-212, l.375), except on a route under `logos.remote.tls-tcp` or `logos.remote.quic`, which cannot permit a marked method (TRANSPORT l.1188). Not provided for events (l.423). A commitment over a marked value can be tested against guessed values (SECURITY l.403). |
| No caller checks: any module can drive a provider that holds unlocked keys or runs a node | HC-03 | Provided. A provider reads the authenticated caller from the invocation context (INTERFACE l.2140-2141; RUNTIME l.833), and a module reads its own address through `get_self` (RUNTIME l.2481). |
| Presentation coupling: replicated objects, list models, calls from the view layer through a bridge, a view entry file named by a path in package metadata | NP-03, NX-02 | No presentation mechanism: presentation data planes and toolkit integration are outside the specification (RUNTIME l.3752), and there is no view-only realization form (PM l.1193). List models can be built from paginated snapshots with `inventory_changed` hints (RUNTIME l.3230, l.3274) and from `watch_installed_packages` and `operation_progress` (PM l.1738, l.1780). |
| Several instances per network or zone | HC-12 | Partly provided. `retire_module` removes an instance, and `list_modules` filters by `module` and `instance` (RUNTIME l.3421, l.3234). A consumer chooses among instances only by exact provider (l.3044); there is no role or alias. |
| Optional dependencies | PM-15, NE-07 | Declined: "Manifest dependencies are unconditional and apply to every variant" (PM l.1220-1222). A `requires` entry selects no provider and grants no authority, and its absence does not by itself reject `establish_route` (RUNTIME l.1363-1364). |

## Appendix F — What the check of the system contracts found clean

The results of the check described in section 3.2 that need no action.

- Size: Runtime Control 98 rules, with 8 more in `logos.runtime` and 5 in `logos.runtime_enrollment`;
  Capability Authority 49; Module Loader 24; Package Manager 37 contract rules and 15 manifest rules;
  Configuration 11. There are 48 methods (Runtime Control 28, Capability Authority 7, Loader 5, Package
  Manager 8) and 11 events. The Credential Store contract, which was read and not put through this check,
  has 26 rules and 3 supporting rules.
- All blocks parse inside the supported subset (no `=>`, integer keys, group rules, generics, tags, bare
  `uint`/`int`/`any`, floats, controls other than `.size`).
- Every reference resolves. No rule has two different definitions: CA, LOADER and PM list every rule of
  their contract a second time in an Appendix A (CA l.1512-1514, LOADER l.737-739, PM l.1842-1845), and
  each listing is identical to the section excerpts.
- The hand-copied projections agree: the signer profile and its 48-byte key (RUNTIME l.2218-2221
  against PM l.495-503), the cursor type in three contracts, and the `observed_change` arms against the
  two engine events in CA.
- All 48 methods are proper request/response pairs with map-valued bodies. Every name obeys the lexical
  rules (one identifier segment after the namespace, COMMITMENT l.255).
- All 73 choices admit a structural selection plan under the COMMITMENT rules.
- Every error-code string used in prose is a member of its enumeration; all Loader and Package Manager
  codes are both defined and used.
- Every section cross-reference in RUNTIME resolves, as does every one across the thirteen files.

Not recomputed for the current text: the collisions among the C identifiers derived under INTERFACE
§2.1-§2.5, the pinned manifest roots (PM l.368-369) and the common-schema roots (COMMITMENT l.594-603).


---

# Remarks from Gemini independent review

Unless tagged `6cac8335`, line citations below (`l.N`) refer to the specification snapshot audited by this document (`6a4dfa28`).

## 1. Corrections to claims and suggested resolutions in this document

### `TF-03` (l.242–252) & Appendix D Row 35 (l.3674) — OS-thread behavior across synchronous C FFI calls in async Rust, Kotlin coroutines, Swift concurrency, and Go
- **Claim (l.242–246, l.250–252, l.3674):** *"A caller written in Go, async Rust, Kotlin coroutines or Swift concurrency does not stay on one OS thread between the call returning and its next statement. The rule is satisfiable only by copying inside the C glue before control returns to the language runtime, which nothing says."*
- **Correction:**
  1. **Async Rust (`Future::poll`)**, **Kotlin coroutines (`suspend` CPS)**, and **Swift concurrency (`async`/`await`)** are **stackless** continuation models: tasks/coroutines can suspend and migrate between worker OS threads **only at explicit suspension points** (`.await`, `suspend` call sites, `await`). Between a synchronous C FFI call returning (`extern "C"`, `@CName`, `@convention(c)`) and the immediately following non-suspending statements that copy `result.message` and `result.detail`, execution is guaranteed to stay on the **exact same OS thread** with zero C wrapper glue. Likewise, a synchronous C callback entry (`_MODULE_dispatch` or a per-method C function) cannot be `async`/`suspend`, so `invocation_access->vtable->current(...)` executes on the entry OS thread before any async task is spawned (as `INTERFACE` §2.9.3 l.2170–2172 already states).
  2. Even in **Go** (the only stackful M:N runtime listed, where `cgo` exit can reschedule a goroutine onto another `M`), pure Go code can bracket the `cgo` call and `C.GoString` / `C.GoBytes` copy with `runtime.LockOSThread()` / `defer runtime.UnlockOSThread()` — so *"satisfiable only by copying inside the C glue before control returns to the language runtime"* does not hold for Go either.

### `TF-11` (l.504–507) — RFC 8610 §3.1 on unprefixed byte-string line breaks
- **Claim (l.504–507):** *"Neither RFC nor cdCDDLe says which bytes it contributes to the value: the bytes as written, one LF, or nothing."*
- **Correction:** RFC 8610 §3.1 states explicitly: *"Whitespace is ignored in the prefixed forms"* and *"If unprefixed, the string is interpreted as with a text string, except that single quotes must be escaped and that the resulting UTF-8 bytes are marked as a byte string (major type 2)."* Thus `"nothing"` (whitespace elision) applies exclusively to *prefixed* byte strings (`h'...'`, `b64'...'`), and RFC 8610 defines no `CRLF -> LF` normalization. The genuine hazard is narrower: RFC 8610's `BCHAR` ABNF (`%x20-26 / %x28-5B / %x5D-10FFFD / SESC / CRLF`) admits `CRLF` while text-string `SCHAR` does not, so Git/OS `LF`↔`CRLF` line-ending conversion silently alters the literal's UTF-8 bytes (`6cac8335` `cdCDDLe` §5 l.121 rejects raw line breaks in unprefixed byte-string literals).

### `TF-23` Suggested Resolution (l.987–992, l.997–999) — Returning `NOT_AUTHORISED` for already-dispatched calls violates `TRANSPORT` §8.1 and `RUNTIME` §9
- **Proposal (l.987–992):** *"return `NOT_AUTHORISED` when the route ended for an authority cause ... On a transported route, answer each in-flight Request with `NOT_AUTHORISED` before the ProtocolError where the connection is still writable."*
- **Correction:** `TRANSPORT` §8.1 l.989 restricts `response-err(NOT_AUTHORISED)` strictly to *"A new Request processed during termination ... without dispatch"*, while l.995 fails already-admitted in-flight requests with `TRANSPORT_ERROR`. Across `RUNTIME` §3.4 l.660, §7.5 l.1349, and §9 l.1737–1738 (*"When authority policy denies an operation, the runtime MUST NOT perform the operation"*), `NOT_AUTHORISED` guarantees to callers that the operation was **rejected before execution**. Answering an already-dispatched call (whose provider may have committed side effects) with `NOT_AUTHORISED` misleads callers into assuming no mutation occurred. (`6cac8335` unified on `TRANSPORT_ERROR` in `RUNTIME` §7.5 l.1271 and `INTERFACE` §2.8 l.2025.)

### `TF-24` (l.1001, l.1023–1025) — `CA` §3.1 already required an authority decision for subscription activation
- **Claim (l.1001, l.1023–1025):** *"`subscribe-event` is an action of its own, and nothing says whether a decision for it is required when a subscription is activated or only when an event is delivered."*
- **Correction:** `TF-24` cites `CA` l.239–240, l.245, and l.906–914, skipping `CA` §3.1 l.288–289 and l.293–294 directly below l.245:
  - `CA` l.288–289: *"For a call, publication, or subscription on an existing route, Runtime MUST include that route and an access value containing the one method or event declaration being checked."*
  - `CA` l.293–294: *"Runtime and the provider-side invocation boundary MUST reject calls, publications, subscriptions, and event deliveries outside the allowed scope."*

  `CA` §3.1 already specified requesting and enforcing an authority decision for activating a subscription on an existing route; only the mirroring prose in `RUNTIME` §4.4 / §9 was missing at `6a4dfa28` (added in `6cac8335` `RUNTIME` l.950 and l.1633 without needing to modify `CA` §3.1).

### `TL-05` (l.2485–2486) — Additional duplicated system types are already leaf-only under `INTERFACE` §1.1
- **Claim (l.2485–2486):** *"Only `static_binding` (LOADER l.177-179) is leaf-only today; the others would also need INTERFACE l.103 relaxed."*
- **Correction:** `INTERFACE` §1.1 l.103–106 permits supporting schemas to use composite maps/arrays, local references within the same supporting schema, prelude integer aliases, and `logos.*` common types; it forbids only referencing *"a concrete module schema, interface contract schema, or another supporting schema"*. Among the duplicated types `TL-05` lists (`l.2468–2478`), `logos.module_loader.hosted_placement` (`LOADER` l.165–168), `logos.module_loader.artifact` (`LOADER` l.170–175), and `logos.package_manager.package_signing_profile` + `package_signer` (`PM` l.494–502) all reference **zero** external concrete, interface, or supporting schemas and satisfy `INTERFACE` l.103 as written.

### `TL-06` Suggested Resolution (l.2511–2512) — Violates `INTERFACE` §1.1 l.103
- **Proposal (l.2511–2512):** *"move the enrollment record into `logos.runtime` or a provisioning supporting schema, and the two signed-claim types into supporting schemas of their own."*
- **Correction:** Under `INTERFACE` §1.1 l.103 (*"A supporting schema MUST NOT reference a concrete module schema, interface contract schema, or another supporting schema"*):
  1. Moving `remote_runtime_enrollment` (`RUNTIME` l.2014, l.2024, which references `logos.runtime.runtime_instance_id`) as-is into a separate provisioning supporting schema references another supporting schema (`logos.runtime`), violating `l.103` (when `6cac8335` extracted `logos.runtime_enrollment` at `RUNTIME` l.2602, it had to inline `tstr .size (1..128)` instead of referencing `logos.runtime`).
  2. Moving `call_evidence_claim` (`CA` l.1240–1241) into a supporting schema references both `logos.runtime.runtime_instance_id` (another supporting schema) **and** `logos.capability_authority.audit_record` (a concrete module contract type), violating `l.103` twice.
  3. Moving `package_signature_claim` (`PM` l.506) into a supporting schema references `logos.package_manager.manifest_commitment` (a concrete module contract type), violating `l.103` again.

### `TS-07` (l.2809–2812) — `_implements` (`normalized-schema-root` field `4`) breaks the unconditional schema-root equality claim
- **Claim (l.2809–2812):** *"two modules with different `_module` names whose primary documents have the same namespace and declarations have the same schema root, so a route request for that contract matches either. A concrete document and an interface document with the same namespace and declarations also share a root."*
- **Correction:** `normalized-schema-root` field `4` (`[* schema-root]`, `COMMITMENT` §9.1 l.1188–1201) commits to the concrete document's `_implements` interface roots (`l.1194`), while *"Field 4 MUST be empty for an interface contract"* (`l.1201`). Therefore, a concrete document and an interface document share a root **only if the concrete document declares no `_implements`**, and if a local node declares `_implements` (e.g., `metrics_provider` per `TP-04`) while a lightweight remote proxy client does not, their primary concrete contract roots differ and a route request for one does not match the other.

### Section 3 intro (l.151), Section 3.3 (l.2593–2599), Section 3.5 `TF-06` (l.3351–3354), Appendix D Rows 3 & 17 (l.3642, l.3656), and Appendix F (l.3722)
1. **Section 3 intro (l.151):** *"None of the items in this section is in the earlier audits"* overlooks that `TF-20` (l.835–857) and `TF-32` (l.1484–1533) revisit and reverse candidates dismissed in `claude-spec-comments-2.md` Part 4 (`l.2284–2285, 2300–2301`).
2. **Section 3.3 scope (l.2593–2599):** Treated `logos-co/rfp` PR #206 as solely *"the appendix 'Integrating the Logos Technology Stack'"* (959 lines), omitting `RFPs/RFP-027-lez-node-api.md` (1,168 lines) and the other five appendices (`logos-api-surfaces.md`, `l1-sdk-strategies.md`, `blockchain-api-sdk-ecosystem.md`, `wallet-libraries-ecosystem.md`, `wallet-tech-stacks.md`), whose additional Core capability requirements are analyzed in `gemini-spec-comments.md` Section 2.
3. **Section 3.5 `TF-06` include-guard bullet (l.3351–3354):** `INTERFACE` l.642 (*"file-level include guards MAY differ"*) defines equivalence of two headers and does not require wrapping line 1 to EOF in `#ifndef`; placing a file-specific declaration guard *after* top-of-file `#include`s and `#if` context/identity checks (`l.654, 679, 2313–2326`) satisfies both rules.
4. **Appendix D Row 3 (l.3642) & Row 17 (l.3656):** Row 3 overlooks that `package_source` `{ kind: "lgx", storage, object }` (`PM` §6 l.856–859, §13 l.1437–1440) resolves against a deployment-configured storage provider whose backing may be local/bundled; Row 17 marks authorized enrollment **`no`** despite `CA` §3.4 l.376–381 (`remote_enrollment_scope`) and `RUNTIME` §9 l.1730 / §9.3 l.2687 (`"or an authorized provisioning operation"`), whereas Row 20 (`l.3659`) marks the identical pattern for facade import **`partly`**.
5. **Appendix F (l.3722):** *"Every error-code string used in prose is a member of its enumeration"* missed `LOGOS_ERR_TRANSPORT` at `TRANSPORT` §5.2 l.808 (the C enum constant rather than `TRANSPORT_ERROR`; fixed in `6cac8335` `TRANSPORT` l.796).

---

## 2. Status of this document's open items at `6cac8335`

For readers moving from `6a4dfa28` to `6cac8335` (`2026-11-17`), the open items in Sections 1–3 stand as follows (cross-references `GF-*` and `GC-*` point to `gemini-spec-comments.md`, where new `6cac8335` defects are analyzed):

- **Resolved cleanly in `6cac8335`:** `C-11`, `RT-05`, `PM-11`, `SO-10`, `NL-07`, `NA-04`, `NR-04`, `ND-04` (except `CREDENTIAL-STORE` l.307, see `GF-07`), `NF-06 (C-09)`, `ND-10`, `ND-12`, `NP-12`, `NP-15`, `TF-01`, `TF-02`, `TF-04`, `TF-05`, `TF-08`, `TF-09`, `TF-10`, `TF-11`, `TF-13`, `TF-14`, `TF-15`, `TF-16`, `TF-17`, `TF-19` (collides with `CREDENTIAL-STORE`, see `GF-01`), `TF-20`, `TF-22`, `TF-23`, `TF-24`, `TF-25`, `TF-26`, `TF-28`, `TF-29`, `TF-31` (collides with `CREDENTIAL-STORE`, see `GF-02`), `TF-32`, `TF-34`, `TF-36`, `TF-40`, `TF-43`, `TL-01` (see `GF-25` on `logos_types.h`), `TL-03`, `TL-04` (see `GF-23` on `CA` §7 precedence), `TL-05`, `TL-07` (see `GF-18` on `RUNTIME` §3.4 table), `TL-09`, `TL-10`, `TS-07`, `TP-07` (see `GF-13`, `GC-08`), and §3.5 `TF-06` editorial items.
- **Addressed in `6cac8335`, but introducing new contradictions/gaps (detailed in `gemini-spec-comments.md`):**
  - `EC-01..04, NC-03`, `TF-18`, `TF-30` → `GF-14` (`RUNTIME` §9.3.1 check-order & typed-error contradictions);
  - `HC-04` → `GF-08`–`GF-13`, `GC-03` (`extends` & release-compatibility defects);
  - `HC-10` → `GF-16` (`logos_publish_fn` return code vs `TRANSPORT` §2.1 frame limits);
  - `TF-21` → `GF-17` (`INTERFACE` §2.5 cross-thread direct event queueing vs `§2.9.3` & starvation);
  - `TF-33` → `GF-21` (`CA` §8 `policy_changed` route `decision_id` replacement vs live Transport sessions);
  - `TF-35`, `TF-47` → `GF-15` (`SubscriptionEnd` & `observe_subscription_end` contradictions and races);
  - `TF-48` → `GF-20`, `GC-01` (`_sensitive` remote-route ban vs `CA` narrowing & default `access: {}` routes);
  - `TL-02` → `GF-01`–`GF-07`, `GC-02` (`LOGOS-MODULE-CREDENTIAL-STORE` contradictions and secret-storage capability gaps);
  - `TS-06` → `GF-13`, `GF-23`, `GC-08` (`contract_documents` & `unsupported-manifest` gaps).
- **Partially addressed in `6cac8335`:** `C-10`, `NP-13`, `NP-14`, `TF-03` (part 1 resolved), `TF-07` (see `GF-23`), `TF-12`, `TF-27`, `TF-39`, `TF-45` (see `GF-22`), `TF-46`, `TL-06`, `TL-08`, `TS-01`, `TP-03`, `TP-06`.
- **Untouched / retained by design in `6cac8335`:** `NE-07`, `NL-12`, `NA-12`, `NP-11`, `HC-02`, `HC-07`, `TF-37`, `TF-38`, `TF-41`, `TF-42`, `TF-44`, `TF-49`, `TF-50`, `TF-51`, `TF-52`, `TS-02`–`TS-05`, `TS-08`, `TP-01`, `TP-02`, `TP-04`, `TP-05`.

---

# Remarks from Claude Opus independent review

Checked against the specs at `6cac8335`. Each `l.N` below is a line of the specification file at that revision.

## 1. How a second reading compares with this document

A second reading classified the same 106 earlier items, excluding the editorial list.

| Outcome | Items |
|---|---|
| Both find the item settled | 31 |
| Both find a point still open | 53 |
| The readings differ | 22 |

Each difference was decided from the spec text by a separate check that started from neither conclusion. This document is
right on five: C-10, HC-04, HC-10, TF-28 and TF-31. On the other seventeen a point remains. Seven are in the table below.
The rest are remarked in the documents that define them: C-11, RT-05, EC-02, EC-03 and EC-04 in
`claude-spec-comments.md`, and NC-03, NL-07, NP-11, NP-12 and NP-13 in `claude-spec-comments-2.md`.

## 2. Items settled in Appendix A where a point remains

| Item | Kind | What remains | Suggested resolution |
|---|---|---|---|
| TF-09 | Changes behaviour | RUNTIME l.3060 lifts non-disclosure for a caller with matching observation authority, and l.1542-1543 define that authority as an allow for the requested method under a matching `runtime_control_scope`. For route establishment the method is `establish_route`, so an unconstrained allow appears to qualify. Such a consumer can tell an absent provider (`NOT_READY`, l.3063) from a denied one (`NOT_AUTHORISED`, l.3062). | State at l.3060 that authority to invoke `establish_route` is not observation authority. |
| TF-22 | Changes behaviour | RUNTIME l.1108 excludes only the thread running the operation that committed the change. No text says whether a Runtime Control event handler may run on a subscriber thread that is inside another operation of the same binding, so subscriber S cannot tell whether a lock held across such a call can deadlock with its handler. INTERFACE l.1467 states the equivalent for a terminal callback. | State the rule in RUNTIME §6.3. |
| TF-35 | Changes behaviour | RUNTIME l.951 ends a route subscription when authority to receive its event ends. For a Runtime Control subscription, l.3362 and l.3589 only restrict delivery, so subscriber S can hold an active subscription that delivers nothing and is never reported as ended. A bullet of TF-06 asks the same question. | Extend l.951 to a Runtime Control subscription whose authority has ended for every record. |
| TL-07 | Wording | The triggers at RUNTIME l.520-521 and l.524 omit an enforcement stop and the report after an unclean Runtime restart. TF-54 carries the first. | Add both causes to the trigger column. |
| TF-01 | Wording | The term schema-aware boundary (TRANSPORT l.640-642) is not mapped to the boundaries RUNTIME defines (l.122-126), and the text does not say whether a forwarding facade (l.2949) must hold the contract's schema. | Define the term and state the facade case. |
| TF-13 | Wording | HASH l.1236 names the list as the schema selected by the typed path, while the path at l.1251 selects a `uint16` element. | Reword l.1236. |
| TF-23 | Wording | TRANSPORT §8.1 does not say expressly that a dispatched in-flight Request receives no correlated `NOT_AUTHORISED` during termination. l.971 grants that answer only to a new Request. | Add that sentence. |

## 3. Remarks on open items

- **TF-54.** The statement that RUNTIME l.528 forbids the transition holds only if l.528 binds the trigger column as well as
  the pair of states. Every pair of states involved is in the table, so the defect may be only an incomplete trigger column.
- **TF-55.** Checked, and it stands. COMMITMENT l.970 makes equal `_module` values a condition of extension, and `_module` is
  outside the schema root (l.250, l.951-957).
- **TF-06, the bullet on INTERFACE l.3351.** The text answers it. RUNTIME l.1149-1150 send a destination's size failure to
  TRANSPORT §2.1 without changing the publish result, and TRANSPORT l.385 and l.387 apply those limits per destination. A
  destination's message limit is therefore not among the limits of INTERFACE l.3351. UF-50 of `claude-spec-comments-4.md`
  covers the separate case of invocation-scoped publication.

## 4. Remarks on the Gemini section above

- **The status list.** Its "Resolved cleanly" line does not match this document. It names twelve items that sections 1 and 3
  here keep open: PM-11, TF-10, TF-16, TF-20, TF-25, TF-29, TF-40, TF-43, TL-03, TL-04, TS-07 and TP-07.
- **Corrections.** The sections of this document now carry the corrections to TF-03, TF-11, TF-23, TF-24, TL-05, TL-06, TS-07,
  the scope of sections 3 and 3.3, the include-guard bullet of TF-06, and rows 3 and 17 of Appendix D.
- **Appendix F.** The remark on `LOGOS_ERR_TRANSPORT` does not hold. That name is a member of the enumeration, and "a bare error name denotes the corresponding `logos_error_code_t` enumerator without its `LOGOS_ERR_` prefix" (INTERFACE l.3825).

## 5. What this check did not cover

- The 22 editorial remarks added to TF-06 at this revision were read for overlap and not verified one by one.
- The 58 entries of the earlier editorial list were not compared with the rewritten TF-06.
- The 53 items that both readings keep open were not checked a third time.

---

# Response from Gemini independent review

1. **The status list (Section 4, first and second bullets):** Agreed — the status list in the earlier Gemini section (`003942ed`) was written against the `6a4dfa28` edition of this document, before commit `9320da5b` re-pinned this document to `6cac8335` (incorporating the eleven accepted corrections and narrowing those twelve items to the residual `6cac8335` sub-points kept open in Sections 1 and 3 above).
2. **Appendix F (`LOGOS_ERR_TRANSPORT`, Section 4, third bullet):** At `6a4dfa28`, `TRANSPORT` §5.2 l.808 read: *"send `logos.transport.protocol-error` with `LOGOS_ERR_TRANSPORT` when the connection remains writable"*. `logos.transport.protocol-error` is a language-neutral CBOR wire message whose `error.code` field uses bare error names in prose (`TRANSPORT_ERROR`, `INVALID_PARAMS`, `NOT_AUTHORISED`), while `INTERFACE` §5.2 (`6a4dfa28` l.3793; `6cac8335` l.3825) maps bare names to C `logos_error_code_t` enumerators (`TRANSPORT_ERROR` → `LOGOS_ERR_TRANSPORT`), not C enumerator identifiers into wire-protocol prose. Commit `6cac8335` fixed `TRANSPORT` l.796 from `LOGOS_ERR_TRANSPORT` to `TRANSPORT_ERROR`, so Appendix F's statement holds at `6cac8335` (while `LOGOS_ERR_TRANSPORT` was a genuine C-identifier leak at `6a4dfa28`, separate from CDDL string-literal error enums).
