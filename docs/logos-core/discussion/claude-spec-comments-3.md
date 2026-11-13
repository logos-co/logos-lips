# Logos Core module specs — open points at `6a4dfa28`

This is the list of points on the Logos Core module specs (`docs/logos-core/raw/spec-*.md`) at revision
`6a4dfa28` that still need discussion with the spec owner. It follows two earlier audits,
`claude-spec-comments.md` and `claude-spec-comments-2.md`, which the owner answered item by item. The
responses are appended to those documents, and the remarks on each response are appended after it, in
the same document. This document refers to those remarks, adds the new findings, and lists in its
appendices everything that is settled.

**How it is organised.**

1. Earlier items that were answered and still need discussion. The remarks are in the earlier documents;
   this section lists them.
2. Earlier items that have no response yet. The items are in the earlier documents; this section lists
   them.
3. New findings, in full.
4. Appendices, for everything that needs no discussion: earlier items resolved by the current text (A),
   earlier items the owner declined (B), the concerns of `human-spec-comments.md` that the current text
   settles (C), and the comparisons behind the new findings (D to F).

**Conventions.**
- Short names: RUNTIME, INTERFACE, TRANSPORT, LOADER, CA (Capability Authority), PM (Package Manager),
  CONFIG, COMMITMENT, HASH, cdCDDLe, SECURITY, BCP. `l.N` is a line of the specification file at
  `6a4dfa28` (`git show 6a4dfa28:docs/logos-core/raw/<file>` gives the text, whatever revision a working
  tree holds).
- Earlier items keep their identifiers: C-, GN-, CM-, IF-, EC-, TR-, RT-, CA-, PM-, SO- from the first
  audit; NX-, NE-, NI-, NL-, NA-, NR-, ND-, NP-, NC-, NS-, NO-, NF- from the second. HC- items are the
  concerns of `human-spec-comments.md`. New findings are TF- (spec text), TL- (the system contracts
  against their own rules), TS- (the integrator documents) and TP- (porting the module catalog).
- Needs that come from existing modules are stated with neutral roles (consumer C, provider P, host
  application H, and so on). The shape of the need is what matters to the specification.
- Every statement about the specs was checked against the lines it cites, and every quotation is exact.

## Summary

| Section | Content | Items |
|---|---|---|
| 1 | Earlier items answered, still needing discussion | 11 remarks covering 15 items |
| 2.1 | Items of the second audit with no response | 10 |
| 2.2 | Concerns of `human-spec-comments.md` that still need an answer | 4 |
| 3.1 | New: contradictions and gaps in the spec text | 35 |
| 3.2 | New: the system contracts against their own rules | 10 |
| 3.3 | New: the integrator documents against the specs | 8 |
| 3.4 | New: porting the existing module catalog | 7 |
| 3.5 | New: editorial | 1 list |
| Appendix A | Earlier items resolved by the current specs | 138 |
| Appendix B | Earlier items the owner declined | 60 |
| Appendix C | Concerns of `human-spec-comments.md` settled by the current specs | 9 |
| Appendices D to F | Comparisons behind sections 3.2 to 3.4 | 35 claims, 20 needs, one list |

**What most needs an answer.**

From the earlier items (sections 1 and 2):
- EC-01 to EC-04, NC-03: Runtime Control reports designed outcomes through the shared error channel, by
  normative tables that contradict INTERFACE §1.4.
- RT-05: nothing tells a Runtime how to distinguish a Module Loader that is briefly unavailable (modules
  keep running) from one that has failed (modules are terminated).
- NA-04: it is not said whether an idempotent `establish_route` replay returns the one-time ticket.
- NL-07: a remote-module facade whose target is stopped, failed or not ready has no defined failure code
  on its module record, and no defined state.
- PM-11: the Package Manager refers to a dynamic-linker integration "defined by LOGOS-MODULE-LOADER" that
  LOADER does not define.
- SO-10: the CDDL mirror files are said to be present and are not in the repository.

From the new findings (section 3):
- TF-01: INTERFACE forbids requiring the Runtime and Transport to know payload schemas; RUNTIME and
  TRANSPORT require them to validate payloads and compute commitments.
- TF-02: the state directory is guaranteed only until `_MODULE_destroy` begins, and that call is the only
  place a module learns it is stopping.
- TF-07: after a package-signing key is rotated, no operation can bring an installed, unchanged package
  under the new key.
- TF-08: where modules are linked statically, nothing says whether an instance survives an update of the
  host binary.
- TF-12: nothing says how an installed package's recorded dependency edges enter a new closure, so two
  Package Managers can resolve the same request differently.
- TF-21: in direct mode an event must be delivered on the publishing thread, and a subscription's handler
  must never run on two threads at once. Two modules that publish into each other's handlers cannot
  satisfy both, and both threads stop.
- TL-01: `logos_types.h` is said to declare every common-schema type, but only one of the eight has a
  specified declaration.
- TL-02: the Credential Store specification and contract are cited and are not in the set.
- TL-03: route states have no rule for `draining`, and expiry has no state.
- TS-01: the embedding application is not a participant and cannot call a module or receive an event,
  while the integrator documents say application code need not be a module.
- TS-05: trust in a publisher is prohibited; every package name needs its own entry in protected trust
  input, which no specified operation edits.

---

## 1. Earlier items that were answered and still need discussion

Each of these items has a response, and the current text settles most of what was asked. What is still
wrong, missing or ambiguous is written up next to the response, in the section "Remarks on the response"
at the end of the document named in the last column. This table only lists them.

| Item | What still needs discussion | Remark in |
|---|---|---|
| C-10 | The Loader `realize_request` has no field for the provider endpoint it must use, and idempotency compares data that is not in the request. | `claude-spec-comments.md` |
| C-11 | Two uppercase MUST NOTs in informative text (SECURITY l.475, BCP l.552) have no normative counterpart, under a BCP 14 statement that has no exemption for informative text. | `claude-spec-comments.md` |
| EC-01 to EC-04, NC-03 | Runtime Control reports designed outcomes through the shared error channel, by normative tables that contradict INTERFACE §1.4 (l.365-366). | `claude-spec-comments.md` |
| RT-05 | No criterion separates a Module Loader that is briefly unavailable (modules keep running) from one that has failed (modules are terminated). | `claude-spec-comments.md` |
| PM-11 | PM l.1192 refers to a dynamic-linker integration "defined by LOGOS-MODULE-LOADER" that LOADER does not define; dependent libraries are mapped without the Loader's hash check; only the Package Manager discloses host paths. | `claude-spec-comments.md` |
| SO-10 | The CDDL mirror files are said to be present and are not in the repository; the Package Manager mirror cannot be extracted in document order. | `claude-spec-comments.md` |
| NL-07 | A remote-module facade whose target is stopped, failed, not ready or contract-incompatible has no defined `failure` code on its module record, and no defined `state`. | `claude-spec-comments-2.md` |
| NA-04 | Whether an idempotent `establish_route` replay returns the one-time ticket is not said. | `claude-spec-comments-2.md` |
| NR-04 | One sentence reads as if continuations were exposed to modules, against the rule beside it; `partial` has two meanings between Runtimes. | `claude-spec-comments-2.md` |
| ND-04 | Four list constraints in the specs' own contracts have no stated failure outcome, which INTERFACE l.3141-3142 requires of every contract. | `claude-spec-comments-2.md` |
| NF-06 (on C-09) | Nothing says what it means for a grant target owned by another Runtime to "resolve" (CA l.77). | `claude-spec-comments-2.md` |

---

## 2. Earlier items that have no response yet

### 2.1 Items of the second audit

Thirteen items of the second audit have no reply. The current text settles three of them without one
(ND-11, ND-13, ND-14; see Appendix A). The other ten are restated against the current text in
`claude-spec-comments-2.md`, under "Items without a response, restated against the current
specifications".

| Item | Subject |
|---|---|
| NE-07 | A consumer learns that an optional provider has appeared only through Runtime Control observation authority keyed by module name |
| NL-12 | Core knows only runtime-ready: no common application-readiness or health surface, and ordering constraints cannot wait for one |
| NA-12 | A provider picked by a person: a requester that does not ask the chooser cannot be steered, and the chosen application cannot be brought forward |
| ND-10 | `.size` on a named target is inside the supported cdCDDLe subset but has no schema-as-data node |
| ND-12 | A cycle of local aliases is accepted and has a schema root, but no value and no C form |
| NP-11 | Files common to all variants have no place in an LGX: each variant carries its own copy |
| NP-12 | Every host downloads every variant, and a catalog entry does not say which platform a source serves |
| NP-13 | Building variants on separate machines is not described, and provenance then attests only the assembly |
| NP-14 | A module cannot declare that it needs one instance per Runtime or a process of its own |
| NP-15 | One manifest defect, two mandated codes: an artifact without its hash, and an artifact of the wrong kind |

### 2.2 The concerns of `human-spec-comments.md`

The thirteen concerns HC-01 to HC-13 have no reply either. The current specs settle nine of them (see
Appendix C). The four below still need an answer. Where each stands against the current text is written
up at the end of `human-spec-comments.md`, under "Status against the current specifications".

| Item | What still needs an answer |
|---|---|
| HC-02 | The reply to NF-24 leaves both open: a placement of several hosted instances in one Module Host, and a pattern for a provider to call a consumer's registered handler. |
| HC-04 | The replies to NF-23 and NO-04 call the broader evolution request separate. Open: whether INTERFACE l.205-208 is the final answer, or a compatibility mechanism across roots is still intended. |
| HC-07 | Whether one provider surface can be normative and the others derived by the Runtime or a required generator. Equivalence of the three surfaces remains a per-module obligation. |
| HC-10 | Whether the ordinary publish callback gets a result or a defined diagnostic. A publisher of an invalid broadcast event learns nothing, and an oversized one closes the affected connection. |

---

## 3. New findings

None of the items in this section is in the earlier audits. Where an item touches an earlier one, the
earlier item is named under **Overlap** or **See**; its outcome is in section 1 or 2 or in the appendices.

### 3.1 Contradictions and gaps in the spec text

These items are places where two passages of the specs cannot both be followed, or where a rule that
other rules depend on is not stated.

#### TF-01 — INTERFACE says Runtime and Transport must not be required to know payload schemas; RUNTIME and TRANSPORT require exactly that
- **Specs:** INTERFACE §4.5 l.3130-3134 ("For module method payloads, schema validation is owned by the
  module dispatch layer ... The runtime and transport layers validate envelopes and routing fields. They
  MUST NOT be required to introspect module payload schemas while forwarding local or remote transport
  calls"). Against: RUNTIME §7.3 l.1222-1224 ("the Runtime-controlled boundary MUST resolve `event_name`
  ..., validate `cbor_data` against the exact event-data type, and compute its payload commitment before
  delivery"), §4.1 l.847-853 (a generic path "validates and decodes" the payload; a commitment failure
  "MUST occur before provider method code executes"), l.1762-1764 ("Runtime MUST compute every request
  and successful-response payload commitment at the Runtime-controlled invocation boundary"),
  l.1000-1001 (a route is not ready unless "its caller-side and provider-side boundaries can compute and
  verify payload commitments"); TRANSPORT §4.1 l.657-669 ("the schema-aware receiving boundary MUST apply
  the following declaration-dependent checks in order": compare the declaration root, validate the
  payload, recompute the value root; "The receiver MUST NOT dispatch, accept, or deliver a payload until
  all applicable checks succeed"), l.677, §8.3 l.1188-1191.
- **Issue:** a value root can be computed only from a schema-typed value, so every boundary that
  computes or checks a commitment must hold the contract's schema. RUNTIME names the Runtime as that
  boundary for events and for every request and response in every mode; INTERFACE forbids requiring
  it. The owner's answers to IF-01 and IF-02 are schema-free checks in the envelope layer (INTERFACE
  l.3136-3139, directly under the sentence quoted above). The owner's answers to TR-07 and TR-08 are an
  ordered, schema-dependent procedure at a "schema-aware receiving boundary". That boundary must act
  before dispatch, send ProtocolError and close sessions. Module dispatch can do none of this:
  `_MODULE_dispatch()` receives the method and the payload (INTERFACE l.1758), never the commitment. So
  the boundary before dispatch holds the schema, and it is the Runtime or its Module Host.
- **Impact:** an implementer cannot tell whether a forwarding Runtime (the provider-side endpoint of a
  remote route, a hop through a facade, the adapter of LOADER §5.4) must load the contract's schema;
  read literally, a hosted provider validates twice (boundary, then dispatch glue), and an
  implementation that follows INTERFACE l.3133 validates nowhere before dispatch.
- **Overlap:** TR-07, TR-08 (the outcome of a schema-invalid response; precedence of the two checks),
  IF-01.
- **Suggested resolution:** delete INTERFACE l.3130-3134, or restrict it to a relay that neither
  terminates a provider session nor computes a commitment, and list the boundaries that must be
  schema-aware: the caller-side route binding, the provider-side invocation boundary including the
  Module Host, and the Runtime for events and direct calls.

#### TF-02 — The state directory is guaranteed only until `_MODULE_destroy` begins, and `_MODULE_destroy` is the only stop hook
- **Specs:** INTERFACE §2.6 l.1619 ("The Runtime Control binding, publish callback, and opaque publish
  state remain valid and unchanged from `_MODULE_init()` entry until `_MODULE_destroy()` returns"),
  l.1623 ("The corresponding module-visible directory mapping remains established until destruction
  begins"), l.2163 (the `invocation_access` state and its `current` operation "remain valid through
  `_MODULE_destroy()` return, like the other initialization bindings"); RUNTIME l.623, l.3854-3856;
  LOADER l.570-572. The owner's position on NL-02 and NL-03: RUNTIME l.3870-3871 ("Return from native
  destruction completes that lifetime operation; it does not supply a schema-defined result for
  application flushing or persistence. Applications needing an observable preparation or persistence
  outcome use their declared methods before administrative stop").
- **Issue:** a module learns that it is stopping only when `_MODULE_destroy` is entered, and from that moment
  the specs do not guarantee its state directory. A conforming Loader may unmap or revoke the
  directory before making the call. The owner's answer to NL-02 and NL-03 is that persistence belongs in
  a declared "prepare" method called before stop. That covers an orderly stop by an orchestrator that
  knows the method. For a host-initiated shutdown, a stop caused by a permission change or by loss of
  execution authorization (CA l.854), or a recovery, nothing requires such a method to be called first;
  a deployment may arrange it (RUNTIME l.3872). The state directory is the only facility of the
  initialization input with the shorter lifetime.
- **Impact:** every module that persists on shutdown (a key store, a node database, a message history)
  depends on unspecified behaviour.
- **Overlap:** NL-01, NL-02, NL-03, NC-04.
- **Suggested resolution:** "until `_MODULE_destroy()` returns", as for the other initialization-input
  facilities. This does not add a preparation phase or a result; it only lets a destructor close its
  files.

#### TF-03 — What happens to a directly loaded library after `_MODULE_destroy`, and to work the module leaves behind, is not stated; three lifetime rules are keyed on OS-thread identity
- **Specs:** INTERFACE §2.8 l.2001-2002 ("the module MUST stop or join internal work that could later
  use the context, Runtime Control binding, publish callback, or publish state"), l.2141 ("to stop or
  join residual internal work"), l.1602 ("retain the implementation binding until the call returns"),
  §2.7 l.1826 and l.1833-1834 (diagnostic storage valid "until the next ABI call into the implementation
  that returned the result begins on the calling thread", or until the binding "is released"); RUNTIME
  l.387 ("MUST retain the implementation binding until destruction has returned"), l.631, l.727 (the
  only mention of `dlclose`, in another context), l.3799 ("Accepted recovery uses a new realization,
  including a new native context"), l.4086 ("unloading of that implementation"); LOADER l.572 ("before
  discarding the binding"), l.590 ("establishes absence"), l.473; CA l.337 ("`stop` includes teardown,
  unloading, and realization release"). For forced paths only: RUNTIME l.3838 ("A shared-process native
  realization MUST NOT be force-released by destroying referenced state or unloading code that can still
  execute"), l.667; LOADER l.582; INTERFACE l.2138. For asynchronous completion: INTERFACE l.2091,
  l.2131 (diagnostics are owned, not thread-keyed). The caller-context lookup, which is thread-keyed:
  INTERFACE l.2166-2171.
- **Issue:** (1) "Discarding", "releasing" or "unloading" the binding is anticipated in five places and
  defined in none: after a normal `_MODULE_destroy` return a Loader may unmap a direct-dynamic library, or
  never. The module's duty at `_MODULE_destroy` covers only work that touches the context or the Runtime
  bindings. A library that keeps other threads or process-wide registrations (a Go runtime, which
  cannot be unloaded; a Rust async executor or thread-local destructors; Nim or C++ worker threads,
  `atexit` handlers, signal handlers) crashes the Runtime's process if it is unmapped, and leaves that
  state behind if it is not, where the next realization of the same module (stop/start, recovery,
  upgrade) meets it. The sentences on forced paths cover only forced release and start-up expiry, and
  "code that can still execute" is not something a Loader can know about a module's private threads.
  Hosted placements are not affected, because the process exits. (2) The diagnostic lifetime of every
  synchronous result is defined by "the calling thread". A caller written in Go, async Rust, Kotlin
  coroutines or Swift concurrency does not stay on one OS thread between the call returning and its
  next statement. The rule is satisfiable only by copying inside the C glue before control returns to
  the language runtime, which nothing says. The asynchronous completion path does not have the problem:
  its diagnostics are transferred with an owner. (3) The caller-context lookup has the same shape on the
  provider side. `current` "returns the borrowed context of the active authenticated provider entry ...
  or null when no such entry exists", and "Unrelated threads ... MUST NOT inherit a provider's active
  invocation context" (INTERFACE l.2166-2170). A provider whose language runtime continues a
  synchronous entry on another OS thread gets null there. The C glue has to capture the context on the
  entry thread and pass it along, which nothing says; l.2171 only forbids keeping it beyond the entry.
- **Impact:** in-process modules written in the documented SDK languages behave differently per Loader
  on stop, recovery and upgrade; language bindings can read freed or overwritten diagnostics; a caller
  check written in a language with migrating tasks can see no caller.
- **Overlap:** NL-01, NL-03 (stop budget, `_MODULE_destroy` cannot report failure), IF-09 (symbol collisions
  across modules).
- **Suggested resolution:** in LOADER §9, state that a direct-dynamic image stays mapped until the
  hosting process exits unless the accepted module declares that it may be unmapped, and that a later
  realization of the same accepted artifact may reuse the image with a fresh context (this generalises
  RUNTIME l.3838 from forced release to release). Extend the `_MODULE_destroy` duty to every thread and
  process-wide registration the module created, or name the exceptions. In INTERFACE §2.7 and §2.9.3,
  add that a binding for a language runtime that migrates work between OS threads MUST copy `message`
  and `detail`, and capture the invocation context, before returning to that runtime.

#### TF-04 — `requires` has no normative effect, and a route for an undeclared contract is neither allowed nor forbidden
- **Specs:** RUNTIME §3.7 l.753-754 ("A provider requirement does not create a package dependency or a
  lifecycle-ordering constraint"), l.915 (requirements "may constrain candidate resolution"), l.1329 (the
  declaration "supplies the exact contract and cardinality used to construct the route request, but
  ... does not select a provider or authorize a route"), l.1381, l.1432-1434; PM l.1357-1358
  (requirements may be used for "dependency graph presentation, install-time diagnostics, or
  runtime-handoff construction"), l.1409; BCP l.121 ("It can declare provider requirements or acquire
  authorized routes as a consumer").
- **Issue:** the declaration is signed, handed off and preserved "without addition or widening", and
  then nothing consumes it. An unsatisfied entry fails neither install nor start. No rule says whether
  `establish_route` for a contract absent from the consumer's `requires` is permitted; the "or" in BCP
  l.121 leans towards permitted. The policy that the integrator SDK documents give as their example, a
  module may reach only what it declares, is neither implied nor excluded.
- **Impact:** two Runtimes differ on whether an undeclared route can be established; a reviewer cannot
  read `requires` as the upper bound of a module's reach.
- **Overlap:** PM-15 (optional dependencies), NE-07, SO-04.
- **Suggested resolution:** either say that `requires` is advisory, or make it the declared upper bound:
  Runtime MUST refuse `establish_route` for a contract the consumer's accepted declaration does not
  list, and policy narrows from there.

#### TF-05 — Route establishment names inputs that the contract model removed
- **Specs:** RUNTIME §9.3 l.3097 (step 5: "the runtime validates the selected contract using the module
  name, schema namespace, schema commitment, and compatibility metadata"), l.3244 (retained route
  material includes the "expected module name"), l.3223 ("incompatible schema change"), l.3301
  ("compatible with readiness for the selected contract"), l.3315, l.3325 ("becomes
  contract-incompatible"). Against: l.2118-2124 (`establish_route_request` carries a `contract`
  commitment and no module name), l.2922 (the root "commits to the complete schema, including its
  namespace, so Runtime Control does not carry a separate namespace wrapper"), l.520 (name and
  namespace "MUST NOT be treated as interchangeable"); INTERFACE l.193 (schemas "do not carry release
  or compatibility versions"). The correct rule stands nearby: RUNTIME l.2948 ("MUST validate the
  expected module contract using the relevant schema commitment and the Transport Hello schema
  commitment"), and the failure-code table has the right wording: `contract-mismatch`, "The selected
  provider or session no longer satisfies the route's exact contract" (l.2510).
- **Issue:** step 5 validates with a module name the request does not contain, a namespace that is not a
  separate input, and "compatibility metadata" that no specification defines; a provider's schema cannot
  change without a new realization, so "incompatible schema change" names no event. These read as text
  from before exact-root selection.
- **Impact:** an implementer cannot tell whether a module-name check is required at step 5 (which would
  defeat TS-07) or what a compatibility check would compare.
- **Overlap:** none (HC-04 is the absence of compatibility by design).
- **Suggested resolution:** reduce step 5 to a reference to l.2948, with wording such as "validates that
  the selected provider exposes the requested contract commitment as its primary contract or an
  implemented interface", and replace the compatibility wording at l.3223, l.3301 and l.3325 by the
  wording of l.2510.

#### TF-07 — Rotating a package-signing key leaves installed packages that no operation can bring under the new key
- **Specs:** PM l.429-431 (rotation "MAY accept old and new identities for that exact package name during
  a configured overlap period"; "After an anchor is removed or revoked, Package Manager MUST NOT use it
  for a new successful resolution, installation, update, or Runtime handoff"), l.405 ("Retained
  verification provenance MUST NOT substitute for current trust"), l.539-541 (the `package_signer` record
  is derived "from the verification that accepted the adjacent manifest commitment" and retained with
  installed state; "A Runtime handoff MUST report the signer retained with its selected installed
  record"), l.378 (the signed claim binds the manifest commitment), l.1667 ("Installing an
  already-installed package identity with the same manifest commitment succeeds with the current installed
  record and creates no duplicate"), l.1680 (`update_package` "selects a version strictly greater than
  `current`"), l.1672 (`remove_package` fails with `package-in-use` while another installed package
  depends on the package), l.1504-1513 (the method list).
- **Issue:** when the overlap ends, an installed package whose retained signer is the removed key can no
  longer be handed off to Runtime. The publisher can sign the unchanged manifest with the new key, because
  the signature covers the manifest commitment and not the reverse. No operation accepts that signature
  for the installed record: installing the package again returns the current record unchanged, an update
  needs a greater version, and there is no re-verification method. What remains is removing and
  reinstalling the package, which is refused while another installed package depends on it, or a new
  release of every package that was signed with the old key.
- **Impact:** a routine key rotation becomes a re-release of the publisher's whole catalog or an uninstall
  on every device, and a revoked key cannot be replaced for a package whose content has not changed.
- **Overlap:** NP-10 (continuity of trust input), TS-05.
- **Suggested resolution:** let `install_package` accept an installed package identity with an unchanged
  manifest commitment under a signature by a currently accepted signer and replace the retained signer
  record; or add a re-verification method; or state that rotation requires a new release of each package.

#### TF-08 — A statically linked module across an update of the host binary: whether the instance survives is not said
- **Specs:** RUNTIME l.1394-1396 ("Core supports static realization through protected registration but
  defines no package-to-static-registration handoff"; a deployment "MUST verify those declarations and
  bind the accepted facts to the selected linked implementation through protected registration"; "A signed
  dynamic artifact hash does not establish the identity or provenance of different statically linked
  code"), l.4041 (the registered `binding` is a deployment-local identifier), l.3637 ("Starting an existing
  local module instance, including after an explicit stop, MUST use its retained accepted declaration and
  MUST NOT select a replacement declaration"), l.3546-3547 ("Installing or updating a package MUST NOT
  replace an existing instance's retained implementation selection. A deployment upgrade uses a new module
  instance selected under current policy"), l.2629-2632 (an address is preserved only with "continuity of
  the same logical instance"; otherwise "Runtime MUST allocate a fresh address", and it "MUST NOT assign
  an address previously used for one logical instance to an unrelated instance"); CONFIG l.93-95 (the
  configuration revision follows the module-instance identity); SECURITY l.473 (the iOS baseline is
  "statically linked or bundled trusted module code using direct mode inside one application").
- **Issue:** relinking the host application replaces the implementation of every statically linked
  module. For a package-backed module the rule is explicit: a changed implementation means a new instance,
  and state moves only through a separately authorized migration. For a static module nothing identifies
  the linked implementation across two builds of the host: there is no artifact hash, and the binding
  identifier is deployment-local. The specs therefore do not say when the retained declaration still
  describes the linked code, or whether the instance, its address, its state assignment and its
  configuration records continue.
- **Impact:** on a platform where every module is linked statically, every application update raises the
  question for every module. One Runtime keeps the instances and their state. Another allocates fresh
  instances, and the user's state is left behind until a migration that no specified operation performs.
- **Reading an implementation needs today:** keep the instance when the declaration facts supplied at
  registration are identical to the retained ones and do not continue it otherwise; or always keep it; or
  never keep it. The first is the conservative reading that still preserves state across an unchanged
  declaration. Not continuing it means a fresh address (l.2631). Where protected deployment input names
  the instance, the Runtime cannot choose another identifier: it refuses the changed record under the
  retained one (l.2632) until the deployment names a new instance.
- **Overlap:** NP-04 (no package-to-static-registration handoff, declined), RT-06 (upgrade by a replacement
  instance), TS-08.
- **Suggested resolution:** state the continuity rule for static registration: which registered facts
  (module name, contract commitments, configuration-schema binding, requested permissions) must be
  unchanged for the instance to continue, and that a change in any of them requires a replacement
  instance.

#### TF-09 — "Observation authority" is a precondition in several rules and is never tied to a scope
- **Specs:** RUNTIME l.3665-3667 ("Before resolving a request that omits both selectors, Runtime MUST
  establish observation authority covering the complete selection scope for that module name"; "Authority
  limited to particular instances or providers does not establish visibility of the complete selection
  scope"), l.3157 ("matching provider-discovery or Runtime Control observation authority"), l.3498 ("Event
  observation authority MUST be checked for that exact instance or provider"), l.3594 ("sufficient
  inventory observation authority"), l.1725 ("observing Runtime Control state that is not visible to
  ordinary modules" requires an allow decision); CA l.180-190 (`runtime_control_scope` has `methods`,
  `events`, `modules`, `instances`, `providers` and `routes`), l.301-308 (it "covers calls, observations,
  and subscriptions"; the optional fields constrain the records "that may be observed or targeted").
- **Issue:** an observation is not an action and has no method of its own, and a `runtime_control_scope`
  names methods and events. For a lifecycle request that names only a module, no text says which allowed
  scope counts as observation authority over "the complete selection scope": the scope for the requested
  method with `modules` naming the module and neither `instances` nor `providers`, a scope for
  `list_modules` over that name, or something else. The same question applies to the other uses of the
  term.
- **Impact:** a policy written for one Runtime does not grant the same thing on another. The same grant
  lets a name-only `start_module` proceed on one and returns `NOT_AUTHORISED` on the other.
- **Reading an implementation needs today:** take the allowed scope of the requested method itself,
  constrained by `modules` and by neither `instances` nor `providers`, as the observation authority; or
  require a scope for `list_modules` over that module name. The second is the conservative reading.
- **Overlap:** NI-05 (name-only lifecycle selection), NO-01.
- **Suggested resolution:** define observation authority in RUNTIME §9 in terms of
  `runtime_control_scope`: which method or event entries and which record constraints establish it for
  each use; or add an explicit observation action to the Capability Authority.

#### TF-10 — The lifecycle state after an accepted start is stopped before any realization exists is not stated, for missing configuration and for a denied execution authorization
- **Specs:** CONFIG l.123-126 ("Runtime MUST NOT start a module whose declaration contains a
  configuration-schema binding"; "Missing eligible configuration MUST prevent initialization and produce
  `NOT_READY` for an otherwise authorized startup attempt. This startup failure does not cancel execution
  intent accepted under Runtime's lifecycle rules"), l.213 (`update_configuration` does not "invoke a
  lifecycle operation"); RUNTIME l.3643-3646 (acceptance establishes `requested` intent "before execution
  authorization or startup", and "A subsequent startup denial or failure MUST NOT cancel that intent or
  change its origin"), l.1737-1741 ("When authority policy denies an operation, the runtime MUST NOT
  perform the operation and MUST report an authorization failure through the method, transport, or
  runtime API error channel used for the attempted operation"), l.1747-1748 ("retained observation or
  audit material MUST distinguish denial from evaluation failure"); CA l.343-345 ("Runtime MUST obtain an
  allow decision before asking Module Loader to realize a direct native implementation"); RUNTIME
  l.553-570 (the state diagram has no edge from `unloaded` to `error`, and `error` means "Realization,
  initialization, readiness, execution, or cleanup failed"), l.3750 (`failure` is optional and "describes
  the current local failure"), l.3753 (the failure classifications: `authority-denied` and
  `authority-evaluation-failed` are among them, and none names missing configuration), l.3757 (Runtime
  clears the classification "when a new execution attempt is accepted or an explicit stop completes
  successfully"), l.3758 ("A local instance in `error` MUST include `failure`, using `other` when no more
  specific cause is established"), l.3537-3538 (`recover_module` requests one attempt for retained
  intent, with the instance `unloaded` or `error`), l.3803 ("orchestration MUST request resumption of
  that intent through `recover_module`, including deployment intent initially blocked by missing
  permissions"), l.3761 ("An observation with no current failure or failure-caused unavailability,
  including a ready local instance, MUST omit `failure`"), l.3801 ("A stop caused by permission-settings
  reconciliation, permission withdrawal, or loss of execution authorization MUST preserve execution intent
  and its authenticated origin"); CA l.854 ("When an execution authorization ends, Runtime MUST withdraw
  the dependent execution access and initiate required termination").
- **Issue:** two causes can stop an accepted start before a realization exists, and for neither is the
  resulting state given.
  1. Missing configuration. The attempt returns `NOT_READY` and leaves intent `requested`. Whether the
     instance stays `unloaded` with no `failure`, or enters `error` with a classification (CONFIG calls
     the outcome a "startup failure"), is not said. Nor is it said who acts on the retained intent once
     a value is supplied: updating configuration starts nothing, and l.3803 gives the `recover_module`
     request to orchestration only for permissions.
  2. Denied execution authorization. Intent is established before the decision, the decision has to
     come before realization, and the denial is reported on the call and must stay distinguishable from
     an evaluation failure. The two classifications suggest that the record carries one. But `failure`
     is required only in `error` (l.3758), `error` is defined as a failure of something that was
     attempted (l.570), and the diagram has no edge from `unloaded` to `error`. An instance whose start
     was denied is therefore either `unloaded` and carrying a `failure`, which no rule allows or
     forbids, or in `error` although nothing was realized.

  The second question returns for an instance that was running. When its execution authorization ends,
  Runtime stops it (CA l.854) and keeps its intent (l.3801). That is a stop, so the instance passes
  through `stopping` to `unloaded`. It is not an explicit stop, so l.3757 clears nothing, and
  `authority-expired`, `authority-revoked` and `permission-enforcement-failed` are classifications for
  exactly these causes. Whether the `unloaded` record then carries that `failure`, or the instance is put
  in `error` although its stop and cleanup succeeded, is not said: l.3761 requires `failure` to be omitted
  only where there is "no current failure or failure-caused unavailability".

  Each outcome is observable through the module record, the readiness result and the state events.
- **Impact:** an orchestrator or a presentation module cannot tell "waiting for configuration" or
  "waiting for permission" from "not started" or from a failure, two Runtimes report different states for
  the same event, and whether the module starts by itself when the value arrives differs as well.
- **Reading an implementation needs today:** keep the instance `unloaded` with intent `requested` in both
  cases, with no failure for missing configuration and with `failure` set to `authority-denied` or
  `authority-evaluation-failed` after a refused authorization, and leave the retry to orchestration; or
  enter `error`, with `other` for missing configuration. The first is the conservative reading, because
  it reports no failure of something that never ran. For a running instance that enforcement stops, report
  `unloaded` with the intent kept and a `failure` that names the cause.
- **Overlap:** NC-02 (missing configuration gives `NOT_READY` and preserves intent), NL-07, TL-07.
- **Suggested resolution:** state the lifecycle state for both causes and whether an `unloaded` instance
  may carry a `failure`, including after a stop that enforcement caused; add a classification such as
  `configuration-missing` if one is intended for the first cause; and say that acting on the retained
  intent after a configuration mutation is orchestration's task, as l.3803 says for permissions.

#### TF-11 — A line break inside an unprefixed byte-string literal: which bytes it contributes is not defined
- **Specs:** cdCDDLe l.127 ("For text-string and byte-string literals, the grammar and escape rules MUST
  follow [RFC 9682] Section 2"), l.159 (byte-string literals are in the supported subset), l.330-331 (a
  byte-string value "maps to the corresponding literal node"); RFC 9682 Appendix A (`bytes = [bsqual] %x27
  *BCHAR %x27`, where `BCHAR` includes `CRLF` and `CRLF = %x0A / %x0D.0A`); RFC 8610 §3.1 (an unprefixed
  byte string "is interpreted as with a text string", and whitespace is ignored only in the prefixed
  forms); COMMITMENT l.396-397 and INTERFACE l.166 (in a Logos schema document a byte-string literal is
  valid only in `_implements`).
- **Issue:** the grammar admits a raw line break, written as LF or as CR LF, between the quotes of an
  unprefixed byte-string literal. Neither RFC nor cdCDDLe says which bytes it contributes to the value:
  the bytes as written, one LF, or nothing. A text-string literal cannot contain a raw line break, so the
  question exists only for byte strings.
- **Impact:** two cdCDDLe implementations can give the same source text different literal bytes and so
  different canonical bytes, and a file that passes through a tool that rewrites line endings changes its
  identity. Within Logos schema documents the exposure is limited to `_implements`, whose elements are
  roots normally written with the `h` prefix, where whitespace is ignored. Minor.
- **Reading an implementation needs today:** reject a raw line break inside an unprefixed byte-string
  literal, which is the conservative reading; or take it as one LF.
- **Overlap:** CM-11 (which string-escape grammar applies), ND-10.
- **Suggested resolution:** state in cdCDDLe §5 that a raw line break inside an unprefixed byte-string
  literal is rejected, or that it contributes exactly one LF.

#### TF-12 — How an installed package's recorded dependency edges enter a new closure is not stated
- **Specs:** PM l.1280-1281 ("A candidate is an installed package record or catalog package whose version
  satisfies every accumulated requirement for its package name"), l.1292-1293 ("An installed candidate
  with matching exact identity and manifest commitment MAY satisfy a dependency without being materialized
  again"), l.1307-1309 (candidates in descending SemVer precedence; "It MUST select the first candidate
  for which the complete transitive closure can be resolved, backtracking to lower candidates when a
  candidate's dependencies make the closure unsatisfiable"), l.1288-1289 (the one conflict that may not be
  resolved by backtracking is a manifest-commitment mismatch for an installed identity), l.1315 ("Source
  selection MUST preserve the recorded dependency edges of installed packages"), l.1319-1326
  (`resolved_dependencies` binds each selected dependency to an exact version and commitment; "Catalog
  changes MUST NOT alter the recorded dependency edges of an installed package"; "Different installed
  closures MAY contain different versions of one package name, but one closure MUST NOT select more than
  one"), l.1660-1661 ("An already-installed package satisfies a selected dependency only when its package
  name, version, and manifest commitment match the recorded resolution"), l.1672 (removal consults the
  "recorded dependency closure"), l.1689-1690 (for the root of `update_package` only: when the target is
  already installed, its recorded direct edges must equal the newly selected ones, or the update fails
  with `dependency-unavailable`), l.1254-1265 and l.1270-1271 (candidate considerations and assignment
  attempts are counted, and the counts may not depend on the implementation), l.1294 (material that
  cannot be obtained fails the operation with `package-unavailable`).
- **Issue:** package B at version 1.0.0 has a `compatible` requirement on package C at 1.0.0 and was
  installed when C 1.0.0 was the newest version, so B's record holds the edge to C 1.0.0. The catalog then
  gains C 1.1.0. A new root R requires B, and in a second case also requires C at 1.1.0 or later. When the
  resolver reaches the installed B, no rule says what B contributes. Four readings are possible.
  1. B's recorded edges are exact requirements. The first case selects C 1.0.0. In the second case B is
     unsatisfiable and the resolver backtracks to other versions of B.
  2. B's manifest requirements are resolved afresh, and a selection that differs from B's record fails
     the root operation, as l.1689-1690 does for an update root. The first case then fails although a
     complete closure exists, against l.1308-1309, and it stays failed, because no operation re-resolves
     an installed package whose content has not changed.
  3. B's requirements are resolved afresh and the record is ignored. In the second case R's installed
     closure reaches C 1.0.0 through B's record and C 1.1.0 directly, against l.1326.
  4. B's requirements are resolved afresh, and a selection that differs from B's record is treated as
     unsatisfiable, so the resolver backtracks over C's versions. The closures equal those of the first
     reading, but C 1.1.0 is considered and attempted, so the counters differ, and when its material
     cannot be fetched the operation fails with `package-unavailable` where the first reading succeeds.
- **Impact:** two Package Managers given the same installed state and catalog select different closures,
  or the same closure with different limit exhaustion, although "Resolution MUST be deterministic for the
  same installed state, catalog inputs, and protected policy" (l.1298-1299).
- **Reading an implementation needs today:** the first reading is the conservative one. It never alters
  or contradicts a recorded edge, keeps one version per name in every installed closure, and needs no
  material for a version that a recorded edge excludes.
- **Overlap:** PM-07 and PM-08 (source selection and unavailable material), TP-07.
- **Suggested resolution:** state in PM §11 that an installed candidate contributes its recorded direct
  dependency edges as exact requirements, transitively; that a candidate excluded by such an edge is
  neither considered nor charged; and that a conflict with another accumulated requirement makes the
  installed candidate unsatisfiable, so that resolution backtracks.

#### TF-13 — The verified views of HASH Appendix B.1 and B.2 must be accepted, and the verification procedure cannot be applied to them
- **Specs:** HASH l.1214-1216 ("Verification requires the schema construction input defined by
  LOGOS-MODULE-COMMITMENT-MODEL Section 3.1, including its required dependency documents, separately from
  the verified view. The verifier MUST validate that input and compute the schema root and selected schema
  subtree root for comparison with the view in step 2"; "Previously validated construction results and
  computed roots MAY be reused"), l.1223-1232 (steps 2 to 4: check that the schema root and schema subtree
  root "identify the schema under which the value root is interpreted", "Validate the typed path against
  the schema", and normalize the disclosed value "under the schema selected by the typed path"),
  l.1385-1392 ("The vectors in Sections B.1 through B.3 use these synthetic 32-byte schema identities": a
  schema root that is the byte `10` repeated, and three subtree roots of the same kind), l.1406-1408 and
  l.1423-1425 (B.1 and B.2 each describe a verified view and say "The verified view MUST validate against
  the value root above"), l.1266 ("A verified-view implementation MUST accept the valid Appendix B views
  and reject mutations that change a disclosed value, path, range, label, count, schema identity, payload
  schema root, node kind, child digest, payload discriminator, domain tag, step order, or expected value
  root"), l.1476 (B.4, by contrast: "All schema identities are computed from the documents above and the
  pinned common schema").
- **Issue:** the identities of B.1 to B.3 are arbitrary byte patterns. No schema construction input has
  that schema root or those subtree roots, since producing one would mean inverting the hash. A verifier
  that follows §8 therefore has no input to validate, nothing to compare in step 2, no schema to validate
  the path against in step 3 and none to normalize the disclosed `uint16` or byte range under in step 4.
  It never reaches steps 5 to 7, which are what these two vectors exercise. The reuse sentence of l.1216
  does not help, because it covers the results of a construction that was validated. B.3 has no view, and
  B.4 does not have the problem.
- **Impact:** the conformance requirement of l.1266 and the two "MUST validate" sentences cannot be met by
  the normative procedure. Each implementation needs a test-only path that supplies the identities in
  place of steps 2 to 4, and each decides for itself what that path checks, so the mutations of l.1266
  that concern "schema identity" and "payload schema root" are not tested alike.
- **Reading an implementation needs today:** check the B.1 and B.2 views with the table of l.1387-1392
  standing in for the results of steps 2 to 4, and keep that path out of the verifier that callers use.
- **Overlap:** CM-08 (the verifier receives the schema input separately from the view), SO-10.
- **Suggested resolution:** rebuild B.1 and B.2 over concrete schema documents, as B.4 is; or state that
  for B.1 to B.3 the listed identities stand for the results of schema construction, and which steps of
  §8 then apply.

#### TF-14 — Two resolver counters are not fully defined: dependency depth for a package reached by more than one path, and what the root is charged
- **Specs:** PM l.1236-1241 (four resolver limits: package names in one partial closure, dependency
  depth, candidate records considered for one name, and candidate-assignment attempts), l.1249-1252 ("The
  root package counts toward the partial-closure limit and has dependency depth zero. Dependency depth is
  the number of manifest dependency edges from the root"; the limit is verified "Before adding a package
  name to a partial closure or inspecting a manifest at a greater depth"), l.1254-1255 ("A candidate
  consideration occurs when Package Manager examines one satisfying candidate in the required order for
  possible assignment and dependency exploration"), l.1263 (an attempt "occurs whenever Package Manager
  tentatively binds a package name to a candidate"), l.1267-1271 (exceeding a limit ends the operation
  with `dependency-unavailable`; "Limit exhaustion and all counter values are determined by the installed
  state, catalog inputs, and protected policy and MUST NOT depend on implementation-local resource
  thresholds"), l.1298-1299 (resolution is deterministic), l.1302-1303 (a root without a version takes
  "the highest available normal release under SemVer precedence"), l.1306 (the next name resolved is "the
  unresolved package name that is first in UTF-8 byte order", whatever its depth).
- **Issue:**
  1. A package name can be required along paths of different lengths. If root R requires M directly and
     also requires A, which requires M, then "the number of manifest dependency edges from the root"
     (l.1250) is 1 or 2 for M. The fewest edges, the most edges, and the edges of the path through which
     M was first required are all readings; with a depth limit of 1 the first accepts and the second
     fails. The fewest edges are not even known when M is inspected, because names are taken in byte
     order (l.1306). With R requiring A and Z, A requiring B, and both B and Z requiring M, the names are
     resolved in the order A, B, M, Z, so M is inspected at three edges before the two-edge path through Z
     exists.
  2. l.1249 says that the root counts toward the name limit and has depth zero. It does not say whether
     selecting the root is a candidate consideration and a candidate-assignment attempt. With an attempt
     limit of N and a closure that needs N assignments below the root, the operation succeeds under one
     reading and fails under the other.
- **Impact:** for the same installed state, catalog and policy, two Package Managers reach limit
  exhaustion at different points and so disagree on whether an operation succeeds, which l.1270-1271 and
  l.1298-1299 exclude. The difference shows only near a limit.
- **Reading an implementation needs today:** none is safer than the others. Whichever is chosen has to be
  documented with the limits, since it decides when they are reached.
- **Overlap:** TF-12 (its fourth reading differs from the first only in these counters), PM-08.
- **Suggested resolution:** define depth for a name with several requiring paths, for example as the
  fewest edges through the packages already bound when the name is selected, and state whether the root is
  charged against the consideration and attempt limits.

#### TF-15 — A new operation through a route handle whose connection was lost for no known cause has no assigned code
- **Specs:** RUNTIME l.1341-1347 ("A route handle remains usable only while its route is `ready` and its
  consumer module context is live"; for a new operation, `NOT_AUTHORISED` "when route authority has been
  withdrawn, has expired, or cannot be established"; "If no such authorization failure is known, explicit
  route closure or loss of Runtime-owned provider or route readiness MUST produce `NOT_READY`"), l.1350
  ("A transport failure that prevents receiving a result remains `TRANSPORT_ERROR`", which concerns a call
  already made), l.1354-1356 (the terminal observer reports the end of the handle's invocation path,
  "including session failure while the logical route remains ready"), l.3474-3475 ("Loss of a
  provider-session connection ends that session and its invocation path. Connection loss alone need not
  make the logical route terminal"); TRANSPORT l.541-545 (on close, "The caller-side handle becomes
  unusable for ordinary invocation and subscription operations"); INTERFACE l.1486-1491 (the binding
  retains a termination code, and "Connection failure without a known authorization or readiness cause
  uses `TRANSPORT_ERROR`"; a later `observe_end` registration returns that code), l.1496 ("A replacement
  connection or provider MUST NOT revive the handle or its registration"), l.2045-2046 (a prepared call
  fails "without provider dispatch" and does not reconnect).
- **Issue:** after a connection fails with no authorization or readiness cause, the route can still be
  `ready` while the handle is unusable. A `call`, a `subscribe` or a `prepare_call` then made through that
  handle must fail, and no rule gives the code. RUNTIME l.1343-1344 covers withdrawn authority and
  "explicit route closure or loss of Runtime-owned provider or route readiness", and this case is neither.
  `TRANSPORT_ERROR` is assigned to the call that was in flight (l.1350) and to the retained termination
  code, which only `observe_end` returns. The retained code cannot simply serve for new operations: it
  "MUST NOT be replaced when a later cause becomes known" (INTERFACE l.1490), while RUNTIME l.1343 requires
  `NOT_AUTHORISED` for a new operation once a withdrawal of authority is known.
- **Impact:** a consumer that calls through such a handle gets `NOT_READY` from one implementation and
  `TRANSPORT_ERROR` from another. The two call for different handling: wait for the provider, or renew
  the route and materialize a new handle.
- **Reading an implementation needs today:** `TRANSPORT_ERROR`, the code the handle's observer receives;
  or `NOT_READY`.
- **Overlap:** EC-05 (codes for a closed, failed, revoked or expired route), TL-03 (a `ready` route need
  not have a usable path), TS-04.
- **Suggested resolution:** add the case to RUNTIME l.1343-1347: when the handle's invocation path has
  ended and no authorization or readiness cause is known, a new operation returns `TRANSPORT_ERROR`.

#### TF-16 — `establish_route` that can return nothing has no assigned code when the provider is allowed but not ready, or when an allowed discovery matches no provider
- **Specs:** RUNTIME l.3145-3146 ("every returned route MUST be independently authorized and ready"; "If
  neither a route nor a continuation can be returned, establishment fails"), l.1501-1502 ("If no
  runtime-visible provider matches a `single` requirement, route establishment for that requirement
  fails"), l.3109-3112 ("If listener validation, export validation, contract validation, or authority
  checking fails, Runtime creates no usable route for that provider. For `single`, the request fails"),
  l.3157-3159 ("A caller without matching provider-discovery or Runtime Control observation authority MUST
  NOT be able to distinguish an unknown target from an existing but hidden or denied target. Runtime MUST
  report `NOT_AUTHORISED` with a non-revealing diagnostic for those cases"), l.1908-1916 (the table of
  precondition failures, with rows for lifecycle operations and for renewal and none for establishment),
  l.660 ("Runtime MUST use `LOGOS_ERR_NOT_READY` only when Runtime-owned lifecycle, provider, or route
  readiness prevents a valid contract response"), l.1485-1486 (a `discover` allow precedes disclosure of
  the provider set), l.1500 ("The provider identity in a successful route record is disclosure necessary
  to that authorized route").
- **Issue:** a denied or unknown target has a code. Two other ways of returning nothing do not.
  1. The selected provider exists, the consumer is authorized to route to it, and it is not ready
     (stopped, starting or failed). `NOT_READY` fits l.660, but reporting readiness discloses that the
     provider exists, and l.1500 covers only "a successful route record". Whether a route allow, without
     discovery or observation authority, makes the provider's existence and state disclosable is not
     said. If it does not, the answer has to be `NOT_AUTHORISED`.
  2. An `all-runtime-visible` request whose `discover` decision allows, when no provider offers the
     contract or none can be made ready. The caller may learn the provider set, the set is empty, and
     "establishment fails" with no code. `NOT_AUTHORISED` would misreport an allowed request.
- **Impact:** a consumer cannot tell "wait and retry" from "ask for authority", and two Runtimes answer
  the same request with different codes.
- **Reading an implementation needs today:** `NOT_READY` when the caller holds a route allow for that
  provider or a `discover` allow for the contract, and `NOT_AUTHORISED` otherwise.
- **Overlap:** NE-07 (an absent provider cannot be told from a denied one), EC-01 to EC-04, TL-03.
- **Suggested resolution:** add rows for establishment to the table at l.1910-1916, and say which
  authority makes a provider's readiness disclosable to the requesting consumer.

#### TF-17 — Three route outcomes are stated two ways or not at all: the routes of a consumer that stops, closing a route that has failed, and a renewal that is denied
- **Specs:** RUNTIME l.624-626 ("During an authorized stop, Runtime MUST close every route whose consumer
  is that module instance. For an unexpected realization failure, Runtime MUST fail every such route"),
  l.2508 (`consumer-unavailable`: "The route consumer has stopped or its realization has failed"), l.2520
  ("a route record in `failed` or `revoked` state MUST include `failure`"), l.2524 ("Normal explicit
  closure does not require a failure record"), l.3486-3491 ("If successful, Runtime MUST set the route
  state to `closed` and prevent new ordinary calls through it"; "The response reports the resulting route
  state"), l.1845-1846 ("Once `close_route`, failure, or revocation places a route in a terminal state, a
  later renewal MUST fail and MUST NOT revive it"), l.3183-3184 (`renew_route` "performs a new authority
  check and may extend `expires_at` and replace `decision_id`"), l.3188-3189 ("Renewal MUST fail if the
  route is unknown, closed, failed, or revoked, or no longer satisfies provider and contract
  validation"), l.2502 (`authority-denied`: "A policy decision denies the route access"), l.3801 (a stop
  "caused by permission-settings reconciliation, permission withdrawal, or loss of execution
  authorization"); CA l.906-911 (after a policy-change notification Runtime "MUST make a dependent route
  unusable when the new decision denies the route").
- **Issue:**
  1. A consumer that stops. l.624 closes its routes on an authorized stop, so their records are `closed`
     and carry no failure. Yet `consumer-unavailable` is described as covering a consumer that "has
     stopped", and a failure code is recorded only on `failed` or `revoked` records (l.2520). Either the
     routes of a stopped consumer are `failed` with that code, against l.624, or the words "has stopped"
     have no case. A stop that enforcement causes (l.3801) is not plainly an authorized stop and is not a
     realization failure, so which of the two rules of l.624-626 the routes of that consumer follow is
     open as well.
  2. Closing a route that has failed. A successful `close_route` sets the state to `closed` (l.3489).
     For a route already `failed` or `revoked`, the text does not say whether the close succeeds and
     moves it to `closed`, which drops the recorded failure, succeeds and reports the state unchanged,
     or fails. l.1845-1846 only keeps renewal from reviving a terminal route.
  3. A renewal that is denied. Renewal makes a new authority check (l.3184). When that check denies,
     the request fails, and nothing says what becomes of the route: it stays `ready` under its earlier
     decision, or it becomes unusable, as CA l.910 requires when a re-evaluation after a policy change
     denies. `authority-denied` is a recorded cause, and no rule says when an established route gets it.
- **Impact:** route records and `route_state_changed_event` differ between Runtimes for the same history,
  and after a denied renewal one Runtime keeps serving calls that another refuses.
- **Reading an implementation needs today:** close the routes of a stopped consumer with no failure; let
  `close_route` on a terminal route succeed and report the state unchanged; make a route unusable when
  its renewal is denied. The last is the conservative reading, because it never serves a call under a
  decision that a later check withdrew.
- **Overlap:** TL-03 (`draining` and expiry), EC-10 (the failure codes), NA-03, TF-33 (a re-authorization
  that Runtime starts after a policy change).
- **Suggested resolution:** drop "has stopped" from l.2508 or say which stop it means; state the result of
  `close_route` on a terminal route; state whether a denied renewal revokes the route with
  `authority-denied` or leaves it unchanged.

#### TF-18 — Where the order of checks is not fixed, the same request gets different codes
- **Specs:** INTERFACE l.3116-3124 (unknown method names give `METHOD_NOT_FOUND`, wrong parameter types
  `INVALID_PARAMS`); RUNTIME l.1626 ("Runtime MUST authorize the consumer and requested method, target,
  and observation scope according to active policy before executing an operation"), l.1823 ("before
  applying a state mutation"), l.1907-1908 ("Runtime MUST preserve the method and target authorization
  requirements and non-disclosure rules when classifying a failed request"; the listed failures apply
  "For an authorized request whose target may be disclosed"), l.630-632 ("A new invocation rejected
  solely because its provider is stopping or its Runtime Control binding has been logically invalidated
  MUST return `NOT_READY`"; "Known authorization failures retain the precedence defined in Section 7.5"),
  l.1347 ("When both authorization and readiness failures are known for the same operation,
  `NOT_AUTHORISED` takes precedence"), l.1732 ("Before dispatching an ordinary provider method, Runtime
  MUST authorize the authenticated consumer's call on the selected route, provider, contract and
  method"), l.852-853 ("Failure to validate or compute a request commitment produces `INVALID_PARAMS` and
  MUST occur before provider method code executes"); TRANSPORT l.657-658 ("For Requests,
  selected-contract method resolution and route access checks under Section 8.1 precede these checks");
  INTERFACE l.3888-3890 (for `materialize_route`: "After the ownership and non-disclosure checks, a
  successfully reconstructed schema root that differs from `expected_contract_root`, or a recorded route
  contract root that differs from it, MUST produce `VERSION_MISMATCH`"; "Route readiness and
  authorization failures MUST follow LOGOS-MODULE-RUNTIME Section 7.5"); CONFIG l.190 ("After ordinary
  target authorization and non-disclosure checks, configuration operations use these pre-acceptance
  classifications"), l.192-198 and l.292-296 (the two tables of failed preconditions).
- **Issue:** some orders are fixed: method resolution and the route's access scope come before payload
  checks, and ownership comes before the root comparison. Five are not.
  1. A malformed Runtime Control request from a caller without authority for the method. Validating
     first gives `INVALID_PARAMS`, with detail; authorizing the method first gives `NOT_AUTHORISED`.
     "before executing an operation" (l.1626) and "before applying a state mutation" (l.1823) bind
     neither order. The target cannot be authorized before decoding, since it is in the payload.
  2. An invalidated binding or a stopping provider, and a caller that policy would deny. `NOT_READY` is
     for a rejection "solely" for that reason, and `NOT_AUTHORISED` takes precedence when both failures
     are "known" (l.1347). Whether Runtime has to evaluate the authorization in order to know is not
     said.
  3. A route call that the per-call authorization would deny and whose payload is invalid:
     `NOT_AUTHORISED` or `INVALID_PARAMS`. Both checks must come before provider code (l.1732, l.852-853),
     and nothing orders them.
  4. `materialize_route` for an owned route that is no longer ready, with a root that does not match: the
     readiness code or `VERSION_MISMATCH`.
  5. A configuration request that meets two rows of a CONFIG table. `update_configuration` with a stale
     revision and a schema commitment that does not match gives `INVALID_PARAMS` or `VERSION_MISMATCH`
     (CONFIG l.195-196). `apply_configuration` for an instance that is not `ready`, with a stale revision
     or a differing commitment, gives `NOT_READY`, `INVALID_PARAMS` or `VERSION_MISMATCH` (CONFIG
     l.294-296). Authorization comes first (CONFIG l.190), and nothing says that the order of the rows is
     an order of precedence.
- **Impact:** none of the five discloses anything about a hidden target. But two Runtimes answer the same
  request with different codes, a consumer handles `NOT_AUTHORISED`, `INVALID_PARAMS` and `NOT_READY`
  differently, and a conformance test cannot assert either answer.
- **Reading an implementation needs today:** authorize what can be authorized without the payload, then
  validate the payload, then authorize the target, then check readiness, then compare roots. For a
  configuration request, take the rows of each CONFIG table in the order written.
- **Overlap:** EC-05 and EC-06 (the codes themselves), EC-01 to EC-04.
- **Suggested resolution:** state one order of checks for a Runtime Control invocation, for a route call
  and for `materialize_route`, and say whether the rows of the two CONFIG tables are in order of
  precedence.

#### TF-19 — Whether provider code may return the status codes that carry Runtime meanings, and what the caller does with them, is not stated
- **Specs:** INTERFACE l.3315-3319 ("A nonzero value means that the invocation did not produce a valid
  contract response. The registry is not a vocabulary for schema-defined domain or application
  outcomes"), l.1802-1803 ("It MUST NOT use `LOGOS_ERR_NOT_READY` for application state.
  `LOGOS_ERR_NOT_READY` is reserved for an invocation failure caused by Runtime-owned readiness"),
  l.3178-3180 ("In direct mode, the per-method function returns `logos_result_t` directly. No encoding or
  Transport message is involved. The invocation status passes through unchanged"), l.3329-3331 (a code
  outside the allocated range is a module failure), l.3366-3367 ("An ABI caller MUST validate a native
  provider result's status code, message and detail before forwarding them. A provider result violating
  these rules MUST be treated as `LOGOS_ERR_MODULE`"); RUNTIME l.660 (`NOT_READY` only for Runtime-owned
  readiness), l.1343-1347 (on a call through a handle, `NOT_AUTHORISED` and `NOT_READY` report the state
  of the route's authority and readiness).
- **Issue:** the validation an ABI caller must apply covers the range of the code and the form of the
  message and detail. It does not say which allocated codes provider code may return. A method that
  returns `NOT_READY`, `NOT_AUTHORISED`, `TRANSPORT_ERROR`, `VERSION_MISMATCH`, `TIMEOUT` or `CANCELLED`
  is within the range, and the status "passes through unchanged". The consumer then reads a Runtime
  meaning into a code the provider chose, because RUNTIME l.1343-1347 makes `NOT_AUTHORISED` and
  `NOT_READY` on a route call statements about the route. l.1802-1803 forbids one such use to the
  module, and nothing says whether the caller enforces it or what the other codes mean when they come
  from provider code.
- **Impact:** a consumer abandons or re-establishes a healthy route because a provider used one of these
  codes for an application condition. One Runtime forwards such a code and another turns it into
  `MODULE_ERROR`.
- **Reading an implementation needs today:** forward the code unchanged, as l.3180 says; or treat every
  code from provider code other than `METHOD_NOT_FOUND`, `INVALID_PARAMS` and `MODULE_ERROR` as a result
  that violates the rules.
- **Overlap:** EC-01 to EC-04 (Runtime Control's own outcomes), EC-05.
- **Suggested resolution:** list the codes that provider code may return, including whether `CANCELLED`
  is one after a cancellation the provider observed, and say that the ABI caller treats any other as
  `LOGOS_ERR_MODULE`.

#### TF-20 — When `start_module` and `stop_module` answer is not stated, and a module that stops itself cannot be answered after its own destruction
- **Specs:** RUNTIME l.3649 ("success means Runtime has performed the lifecycle work needed to move the
  selected module instance toward `ready`, including native artifact loading and lifecycle initialization
  where applicable"), l.3687 ("success means Runtime has performed the lifecycle work needed to move the
  selected module instance toward `stopping` or `unloaded`, including lifecycle destruction where
  applicable"), l.3654 and l.3693 ("The response reports the resulting local runtime lifecycle state"),
  l.620-621 (on stop the instance becomes `stopping`, and Runtime "prevents new outbound method calls and
  new Runtime Control contract calls by that module instance"), l.3609 (for `report_failure`: "Failure
  handling MUST allow the reporting invocation to return without waiting for cleanup"), l.3697 (for
  `shutdown_runtime`: "A successful response acknowledges acceptance, not completed shutdown");
  INTERFACE l.1994-2002 (before destruction begins the ABI caller must "wait for every in-flight call to
  return"; "`_MODULE_destroy()` MUST NOT execute concurrently with another call using that context";
  before it returns "the module MUST stop or join internal work").
- **Issue:** "toward" leaves the point of the answer open. `start_module` may answer at `loaded` or at
  `ready`, and `stop_module` at `stopping` or at `unloaded`. The reported state and the time the caller
  is blocked both differ. For a module that stops itself, waiting for `unloaded` cannot complete:
  destruction waits for the module's in-flight calls and joins its threads, and one of them is waiting
  for this answer. `report_failure` and `shutdown_runtime` each say that the answer does not wait;
  `stop_module` does not, and nothing says whether a module may name itself as the target. Nothing says
  either what a `stop_module` that waits for `unloaded` answers when its drain deadline expires before
  destruction returns (TF-28 has the state at that point).
- **Impact:** orchestration written against a Runtime that answers `start_module` at `ready` misbehaves
  on one that answers at `loaded`. On a Runtime that answers `stop_module` at `unloaded`, a module that
  stops itself hangs until a drain deadline expires.
- **Reading an implementation needs today:** answer `stop_module` at `stopping` at least when the caller
  is the target or has a call in progress in it; for `start_module`, either point, documented. A
  `stop_module` that waits for `unloaded` answers no later than the expiry of its drain deadline, with
  the state the instance has then.
- **Overlap:** NL-06 (leaving `error`), TL-07 (the state diagram), TF-10.
- **Suggested resolution:** state for each method the state at which the response is sent, or that both
  are permitted and the returned state tells which; and state that a `stop_module` whose target is the
  caller is answered without waiting for destruction, as `report_failure` is.

#### TF-21 — Delivery on the publishing thread and one thread at a time per subscription cannot both be met when two publishers deliver into each other's handlers
- **Specs:** INTERFACE l.1961-1965 ("In direct mode, a publish call MUST invoke every applicable direct
  subscriber callback synchronously on the publishing thread before the publish call returns"; "An
  implementation MUST NOT move a direct subscriber callback to another thread or return from publication
  before that callback completes"), l.1435-1438 ("The binding MUST NOT begin a handler invocation on one
  thread while an invocation for the same subscription remains active on another thread"; "Same-thread
  handler re-entry is permitted only when an action during a callback synchronously causes nested direct
  publication for the same subscription"), l.1958 ("The module MAY invoke its publish callback
  concurrently from multiple threads while its context remains live"), l.1969-1973 ("Direct publication
  is a re-entrancy boundary"; the publishing module "MUST synchronize its state without deadlocking such
  conforming re-entry"), l.1463-1464 (when a route becomes terminal the binding "MUST deactivate every
  subscription on that route and MUST NOT begin another handler invocation"); RUNTIME l.1181-1182
  ("Runtime MUST preserve those semantics and MUST NOT substitute a Runtime event-delivery thread for
  direct callback execution").
- **Issue:** take two modules in direct mode, P and Q, each subscribed to an event of the other. On
  thread 1, Q publishes; P's handler runs on thread 1 and publishes an event of P, which has to reach Q's
  handler. On thread 2, P publishes; Q's handler runs on thread 2 and publishes an event of Q, which has
  to reach P's handler. P's subscription is active on thread 1, so thread 2 may not begin its handler
  (l.1435-1436), and may neither hand the callback to another thread nor return without it
  (l.1964-1965). The same holds for thread 1 and Q's subscription. Each thread waits for the other, and
  no step that would end the wait is permitted. Neither module has broken a rule: publishing from
  several threads is allowed (l.1958), publication from inside a handler is contemplated (l.1437-1438),
  and the re-entrancy rule of l.1969-1973 is about the module's own state. The wait is in the binding's
  exclusion for each subscription, which a module cannot see.
- **Impact:** two modules that keep each other informed, each republishing when it is told of a change,
  can stop both of their publishing threads for good. The hang depends on timing, so it appears under
  load and not in a test.
- **Reading an implementation needs today:** wait, which is the only choice that breaks neither rule, and
  end the wait when the awaited subscription is deactivated (l.1463-1464), so that closing either route
  or stopping either module releases both threads.
- **Overlap:** NE-02 (a handler that runs inside the consumer's own blocked call), NE-05 (a publisher
  blocked behind a slow transported subscriber).
- **Suggested resolution:** say which rule yields when the subscription is active on another thread.
  Queuing the event behind the active invocation, to be run by the thread that holds the subscription,
  keeps the order and the exclusion; `publish` then returns without that one callback. If neither rule
  is to yield, state the hazard and say what a module must not do from a handler.

#### TF-22 — On which thread, and when, the handler of a Runtime Control subscription runs is not defined
- **Specs:** INTERFACE l.3837 ("The Runtime Control `subscribe` and `unsubscribe` operations apply the
  subscription semantics in Section 2.5 to events selected from the Runtime Control contract"), l.1470
  ("Direct delivery follows Section 2.8"), l.1961-1962 ("a publish call MUST invoke every applicable
  direct subscriber callback synchronously on the publishing thread"), l.1434 ("handler invocations MUST
  begin in direct publication order or in Event commitment order for Transport delivery"), l.1954-1955
  ("Operations through one Runtime Control binding, except its release, MAY be initiated concurrently
  from multiple module threads"); RUNTIME l.1181-1185 ("MUST NOT substitute a Runtime event-delivery
  thread for direct callback execution"; "For transported subscribers, delivery scheduling is
  Runtime-internal"), l.2603 and l.3509 (`permission_settings_changed_event` and
  `execution_state_changed_event` report changes "in committed order"), l.3732-3733 ("Runtime MUST
  deliver Runtime Control state events only while the authenticated subscriber remains authorized to
  observe the referenced module, provider, or route").
- **Issue:** a Runtime Control event is produced by the Runtime when it commits a change. No module makes
  "a publish call", so there is no "publishing thread" for l.1961-1962 to name. The binding a module
  receives at initialization is not a route and has no execution mode, so its subscriber is not plainly
  a direct one, and l.1183-1185 leaves scheduling to the Runtime only "For transported subscribers". Two
  placements remain open, and they behave differently:
  1. Inline in the operation that commits the change, on its caller's thread. A handler then runs inside
     another module's `start_module` or `close_route` call, or inside the subscriber's own call, and a
     slow handler of any observer delays that operation. A handler may call Runtime Control (l.1954-1955
     allows it from any module thread), and it would do so while the operation that is delivering to it
     has not returned. Changes that no call causes (a detected failure, a deadline, an expiry) have no
     such thread.
  2. On a thread the Runtime keeps for delivery, after the change is committed. That is what l.1181-1182
     forbids, if this delivery counts as "direct callback execution".
- **Impact:** a module author cannot know whether a handler can run inside the module's own Runtime
  Control call, and so which locks may be held across that call. An observing module can stall the
  lifecycle operations of other modules on one Runtime and not on another.
- **Reading an implementation needs today:** deliver each subscription's events in committed order on a
  thread the Runtime owns, never inline in the operation that committed the change.
- **Overlap:** NE-02, NE-05, TF-09 (the authority these events are checked against), TL-08, TF-21.
- **Suggested resolution:** state in INTERFACE §2.8 or RUNTIME §6.3 that Runtime Control events reaching a
  local binding are scheduled by the Runtime, in committed order for each subscription, and are not
  delivered synchronously within the operation that caused the change. If synchronous delivery is
  intended, name the thread and the re-entrancy that follows.

#### TF-23 — A call that was admitted and is then ended by the end of its route has no assigned code
- **Specs:** RUNTIME l.3226-3227 ("In-flight call behavior, timeout policy, idle expiry, and retry policy
  are profile or implementation policy"), l.3459 ("In-flight call behavior follows the existing
  route-revocation policy"), l.3490 ("In-flight call behavior is governed by runtime authority policy"),
  l.1292-1293 ("Final Response commitment remains subject to the existing policy for work already in
  flight"; "a prior authorization check MUST NOT permit a later commitment contrary to that policy"),
  l.1349 (the codes of §7.5 "apply at the boundary deciding whether to admit a new operation; they do
  not change in-flight call, timeout, or cancellation policy"), l.1737-1738 ("When authority policy
  denies an operation, the runtime MUST NOT perform the operation and MUST report an authorization
  failure"); CA l.823 ("Response commitment for work already admitted remains subject to the existing
  in-flight policy"), l.917 ("An implementation SHOULD cancel in-flight work when safe and supported");
  TRANSPORT l.988 ("In-flight work remains subject to the applicable policy in LOGOS-MODULE-RUNTIME
  Section 9.3"), l.543 ("All in-flight requests receive a synthetic `TRANSPORT_ERROR` response"),
  l.552-553 ("A synthetic `TRANSPORT_ERROR` does not prove that the callee did not execute an in-flight
  request"); INTERFACE l.2065-2067 ("Runtime MUST serialize acceptance of a valid final result with
  local cancellation, timeout and binding-failure outcomes for the call"; "Local cancellation produces
  `CANCELLED`; expiration of the caller-selected duration produces `TIMEOUT`"), l.2076 ("A local timeout
  does not prove that the provider observed cancellation"), l.1486-1487 (the handle retains a
  termination code: "Known authority withdrawal or expiry uses `NOT_AUTHORISED`; otherwise explicit
  route closure or known provider/readiness loss uses `NOT_READY`").
- **Issue:** whether a call admitted before its route was closed, failed or revoked may still complete is
  left to policy, deliberately. Six passages refer to that policy, under three names (a profile or
  implementation policy, the runtime authority policy, the route-revocation policy), and none defines
  it. What is missing is the result when the policy does not let the call complete.
  1. The code. INTERFACE l.2065 counts "binding-failure outcomes" among the terminal decisions of an
     asynchronous call, and l.2067 gives codes only for cancellation and timeout. The codes of RUNTIME
     §7.5 are for new operations (l.1349). TRANSPORT l.543 covers the close of a connection. A
     synchronous call on a direct route has no rule.
  2. What the code says about execution. If the call ends with `NOT_AUTHORISED` after a revocation, the
     provider may have run it to the end, while elsewhere that code reports an operation that was not
     performed (l.1737-1738). The specs say "does not prove" only of `TRANSPORT_ERROR` (TRANSPORT
     l.552-553) and of a local timeout (INTERFACE l.2076).
- **Impact:** for a route that is revoked or closed during a call, one Runtime returns the result,
  another `NOT_AUTHORISED` or `NOT_READY`, and a third `CANCELLED`. A consumer that takes
  `NOT_AUTHORISED` to mean that nothing happened skips a compensation it owes, or repeats an operation
  that was carried out.
- **Reading an implementation needs today:** the code that the handle's terminal observer receives
  (INTERFACE l.1486-1487): `NOT_AUTHORISED` after a withdrawal or expiry of authority, `NOT_READY` after
  a closure or a loss of readiness. Treat either as `TRANSPORT_ERROR` is treated, as no proof that the
  provider did not execute.
- **Overlap:** TF-15 (a new operation after a lost connection), the `TIMEOUT` note in TF-06, EC-05, TL-03
  (`draining`), TF-17 (a denied renewal).
- **Suggested resolution:** add to INTERFACE §2.9.1 and RUNTIME §7.5 the code of a call that the end of
  its route terminates before a result is accepted, for synchronous and asynchronous calls, with one
  sentence saying that this code does not prove that the provider did not execute.

#### TF-24 — Whether activating an event subscription needs an authority decision is not stated
- **Specs:** RUNTIME l.1720-1730 (the list of operations that "require an allow decision from runtime
  authority policy" has "invoking an ordinary provider method" and names no event operation),
  l.1732-1733 ("Before dispatching an ordinary provider method, Runtime MUST authorize the authenticated
  consumer's call on the selected route, provider, contract and method. Authority to establish or renew
  the route does not itself authorize the call"), l.1018-1020 ("Before activating a subscription,
  Runtime MUST resolve `event_name` under the route's selected contract and enforce its event
  declaration root against `route_access.subscribe_events`"), l.1229 ("Runtime MUST authorize delivery
  separately for each subscriber route using the publisher's authority and the subscriber's authority"),
  l.1263 ("Invocation authority does not itself grant event-publication or event-subscription
  authority"); CA l.239-240 ("The `actions` field distinguishes provider discovery, route establishment
  or renewal, calls, event publication, and event subscription"), l.245 ("Event delivery also requires
  the subscriber's `subscribe-event` authority and MUST satisfy both route event lists"), l.906-911 (after
  a policy change the re-evaluated operations include "new event-delivery commitments", and a denied or
  narrowed route becomes unusable), l.914 ("It MUST terminate dependent provider sessions and
  subscriptions when their continued use would exceed current authority"); INTERFACE l.1427 ("The route
  `subscribe` operation returns `LOGOS_OK` only after the subscription is active"), l.1474-1475
  (`observe_end` reports "loss of the handle's invocation path"); TRANSPORT l.733-736 (a Subscribe is
  checked against "the route's event-subscription access before activation", with `NOT_AUTHORISED` for an
  event outside it).
- **Issue:** for a method call the text names the authorization point and says that authority for the
  route is not enough (l.1732-1733). For events it names the delivery (l.1229, CA l.245) and, at
  activation, only the comparison with the route's scope list (l.1018-1020). `subscribe-event` is an
  action of its own, and nothing says whether a decision for it is required when a subscription is
  activated or only when an event is delivered. The list at l.1720-1730 names neither point. Take a
  consumer whose route scope admits the event and which has no `subscribe-event` authority. One Runtime
  refuses `subscribe` with `NOT_AUTHORISED`. Another returns `LOGOS_OK` for a subscription that is
  active (INTERFACE l.1427) and never delivers, and the consumer is not told.

  The end of a subscription is open in the same way. After a grant is revoked or expires, Runtime
  terminates the subscriptions whose continued use "would exceed current authority" (CA l.914). After a
  policy change the text names "new event-delivery commitments" and routes (CA l.906-911), and not
  subscriptions. When the `subscribe-event` decision for an active subscription turns into a deny and the
  route stays usable, the subscription is either terminated or left active and silent. In neither case is
  the subscriber told: the route is still `ready`, so `observe_end` does not fire (INTERFACE l.1474-1475),
  and no operation reports the end of one subscription.
- **Impact:** on the second Runtime a consumer cannot tell "no event has occurred" from "not permitted",
  and a conformance test cannot assert either answer to `subscribe`.
- **Reading an implementation needs today:** evaluate `subscribe-event` when the subscription is
  activated and again for each delivery.
- **Overlap:** NA-07 (subscriptions after a policy change), NE-03, CA-03 (the meaning of
  `publish-event`), TF-18, TF-35.
- **Suggested resolution:** add event subscription and event delivery to the list at l.1720-1730, and
  state in RUNTIME §4.4 whether activation requires the subscriber's `subscribe-event` decision, with
  `NOT_AUTHORISED` when it is denied. Say also whether a subscription whose `subscribe-event` authority is
  withdrawn is terminated, and how the subscriber learns of it.

#### TF-25 — Where bootstrap ends is not defined, so what `logos_runtime_start` waits for and the code of an expired startup deadline are open
- **Specs:** RUNTIME §13.2 l.3967 (Start: "Complete bootstrap, then return while the Runtime continues
  execution in the background"), l.3973-3974 ("Successful startup MUST establish the initial
  system-service bindings required by Section 9"; "It does not require every ordinary module in the
  deployment to be ready"), §13.4 l.4072 ("Invalid registration or startup ordering MUST return
  `LOGOS_ERR_NOT_READY`"), l.4073 ("If shutdown is requested through Runtime Control during bootstrap,
  startup MUST return `LOGOS_ERR_CANCELLED` unless it has already completed"), l.4088 ("Other failures
  MUST use the applicable shared error code, or `LOGOS_ERR_MODULE` when no more specific shared code
  applies"); §9 l.1640 ("Runtime startup MUST establish the initial orchestration realization under
  bootstrap policy"), l.1643 ("Orchestration MUST establish that binding before starting the remaining
  deployment under active authority policy"), l.1648 (a provider is used as a system service only when
  "the module instance is ready under its selected execution mode"), l.1675 ("If an external Capability
  Authority is unavailable, Runtime MUST deny operations that depend on it"), l.1685 ("Protected
  construction and deployment inputs may establish bootstrap policy and initial system-service bindings");
  §3.4 l.566 (`loaded`: "Runtime has acquired or attached the selected realization and is performing the
  applicable initialization and readiness checks"), l.664 ("The Runtime host or deployment supplies a
  finite logical startup deadline"); §10.2 l.3876-3877 (a module that "fails during startup before it
  reaches `ready`" is a "partially realized implementation", which Runtime releases); §9.3 l.3753
  (`startup-timeout` is a failure classification of the instance); INTERFACE l.2067 ("expiration of the
  caller-selected duration produces `TIMEOUT`"); CONFIG l.123-125 ("Runtime MUST NOT start a module whose
  declaration contains a configuration-schema binding"; "Missing eligible configuration MUST prevent
  initialization and produce `NOT_READY` for an otherwise authorized startup attempt").
- **Issue:** §13 ends `start` at "bootstrap" and never says what bootstrap contains. §9 gives startup two
  obligations, the orchestration realization (l.1640) and the initial system-service bindings (l.3973).
  Four things about the end point are not stated.
  1. The state the orchestration instance must reach. A realization exists from `loaded` on (l.566), so
     on one reading the obligation of l.1640 is met there. On the other it is met at `ready`: a
     realization that fails before `ready` is only partial and is released (l.3876-3877), and `ready` is
     what the text requires of a system-service provider (l.1648). The readings differ when the
     module's initialization fails: `LOGOS_OK` on the first, a failed startup on the second.
  2. The first authority binding. With an externalized authority that binding is established by
     orchestration (l.1643), a module that can act only once it is ready, while successful startup must
     establish the initial system-service bindings (l.3973). Whether `start` returns before or after
     that binding exists is not said. No Runtime Control method binds a system service, so what
     orchestration does to establish it, beyond starting the selected instance, is not said either.
  3. The code when the startup deadline expires first. l.4088 asks for the applicable shared code.
     `TIMEOUT` has one assigned producer, a prepared call's own duration (INTERFACE l.2067). The startup
     deadline is also a duration the host supplies (l.664), and the instance's record then says
     `startup-timeout` (l.3753). `TIMEOUT` and `LOGOS_ERR_MODULE` can both be argued.
  4. The code when the orchestration instance has no configuration value. Its declaration may bind a
     configuration schema, and without a value the startup attempt is refused with `NOT_READY` (CONFIG
     l.125). For `logos_runtime_start`, `LOGOS_ERR_NOT_READY` is the code of an ordering mistake by the
     host (l.4072), and other failures take the applicable shared code or `LOGOS_ERR_MODULE` (l.4088).
     Whether the host receives `NOT_READY`, which it cannot tell from a call made out of order, or
     `LOGOS_ERR_MODULE`, is not said.

  That a startup which cannot establish orchestration has failed, and that the Runtime then stays up
  until the host shuts it down, follows from l.1640, l.3989 and l.4075 and is not in question.
- **Impact:** the host has no other view of the Runtime, because the Host Embedding API has no
  observation operation and the host is not a consumer. The result of `start` is all it learns about
  whether the module that drives the deployment is running and, under an externalized authority,
  whether anything can be authorized yet. One Runtime returns `LOGOS_OK` where another reports a failed
  startup, and a host that handles `TIMEOUT` and `LOGOS_ERR_MODULE` differently behaves differently on
  the two.
- **Reading an implementation needs today:** return from `start` when the orchestration instance is
  `ready`, and treat a failure to reach it as a failed startup. Count towards bootstrap only the
  system-service bindings that protected input establishes itself (l.1685); the first authority binding
  is orchestration's task after `start` has returned, and until it exists the operations that depend on
  it are denied (l.1675). Report an expired startup deadline as `LOGOS_ERR_MODULE`, with the
  classification in the diagnostic message. Report an orchestration instance that has no configuration
  value as `LOGOS_ERR_MODULE` too.
- **Overlap:** TF-20 (when `start_module` answers), the `TIMEOUT` note in TF-06, TS-01 (what the host
  cannot observe), NA-11 (bootstrap policy once an authority is bound).
- **Suggested resolution:** define in §13.2 when bootstrap is complete, for example when every
  system-service binding established from protected input has passed the checks of §9 and the
  orchestration instance is `ready`; say whether the first authority binding of l.1643 belongs to it;
  and assign the codes that `start` returns when the startup deadline expires and when the orchestration
  instance cannot start for want of a configuration value.

#### TF-26 — The execution intent of an instance that startup realizes is not stated
- **Specs:** RUNTIME §9 l.1640-1641 ("Runtime startup MUST establish the initial orchestration
  realization under bootstrap policy"; "When Module Loader is used, its initial provider MUST be
  established first and used to realize orchestration"), l.1667 ("Bootstrap realization and engine
  enforcement cleanup MUST use their protected policy basis without fabricating a module consumer when
  no module operation supplies one"); §9.3 l.3644 ("acceptance MUST establish `requested` intent with
  the authenticated requesting module as its origin before execution authorization or startup"), l.3647
  ("For an instance in `loaded` or `ready`, the request MUST preserve existing intent and origin"),
  l.3500-3501 ("`execution.intent` is `uninitialized` before an execution choice is established,
  `requested` while execution intent is retained, and `stopped` after an explicit stop";
  "`intent_revision` MUST be present exactly when intent is `requested`"), l.3538-3540 ("Runtime MUST
  reject the request unless intent is `requested`, the instance is `unloaded` or `error`, and cleanup of
  any previous realization is complete"; "Authority to request recovery does not substitute for the
  retained origin's execution authority"), l.2598 ("Resumption of retained requested intent MUST use
  ordinary recovery and current authorization under that origin"), l.2052-2056 (`execution_state`
  carries `revision`, `intent` and an optional `intent_revision`, and no origin); §10.1 l.3807-3808
  ("MUST NOT autonomously restart orchestration"; "Another authorized module MAY restore orchestration,
  or protected construction may establish it when the Runtime host restarts"); §9.1 l.1838 ("An explicit
  stop MUST cancel retained execution intent"); §10.2 l.3842 ("Shutdown MUST preserve retained execution
  intent and its origin").
- **Issue:** execution intent is established by `start_module`, with the requesting module as its origin
  (l.3644). Startup realizes orchestration, and before it the initial Module Loader provider, with no
  requesting module, and must not invent one (l.1667). What `execution` then reports for such an
  instance is not said, and either answer is visible to every observer.
  1. `requested`, with an `intent_revision`. The intent then has an origin that is not a module, a kind
     the text does not name. A later recovery is checked against the execution authority of that origin
     (l.2598, l.3540), which would be the bootstrap policy, and that is not said.
  2. `uninitialized`, although the instance is running. `recover_module` is then always rejected
     (l.3538), so a failed orchestration can be restored only by `start_module`, which makes the calling
     module the origin. While the instance runs, a `start_module` leaves the intent as it is (l.3647),
     so it stays `uninitialized`.

  A Runtime that keeps execution state across restarts meets a second question. After an explicit stop
  of orchestration its intent is `stopped` (l.1838, l.3500), and shutdown preserves it (l.3842). At the
  next startup l.1640 requires the realization to be established, and l.3808 expects protected
  construction to do it. Whether startup overrides the retained `stopped`, and what the intent is
  afterwards, is not stated.
- **Impact:** two Runtimes report different `intent` values for the same deployment. Which method
  restores a failed orchestration, and under whose execution authority, differs. With retained state,
  whether an explicit stop of orchestration survives a restart differs as well.
- **Reading an implementation needs today:** report `requested` with an `intent_revision`, record
  protected bootstrap input as the origin, and check a later recovery against bootstrap policy. With
  retained state the nearest reading is that startup establishes orchestration every time (l.1640,
  l.3808) and so replaces a retained `stopped`.
- **Overlap:** RT-02 (the basis of calls the engine makes for no module), NL-10 (who resumes retained
  intent after a restart), TF-10, TF-25.
- **Suggested resolution:** state in §9 the intent that startup establishes for the instances it
  realizes, name protected input as a possible origin, and say which policy its execution authority is
  checked against; and state whether startup establishes orchestration when its retained intent is
  `stopped`.

#### TF-27 — The host must accept a Runtime-generated instance id, and the Host Embedding API never shows it one
- **Specs:** RUNTIME §9.3 l.2659-2660 ("A runtime instance id is an opaque string chosen or accepted by
  the runtime host for a concrete runtime instance"), l.2665-2667 ("A runtime instance id MAY be
  host-assigned or runtime-generated"; "If the runtime generates the id, the runtime host MUST accept it
  before the id is used in runtime-control, addressing, or route records owned by that host"),
  l.2671-2672 (for the remote profiles, "The runtime host or authorized provisioning system generates it
  once and preserves it for the lifetime of that logical Runtime identity"), l.2553 (`get_self` "returns
  the complete authenticated module-instance address associated with the invoked Runtime Control
  binding"); §13 l.3935 ("It is not a module contract and does not give the host a module-instance or
  consumer identity"), §13.2 l.3963-3970 (six operations), §13.3 l.4019-4030 (each returns
  `logos_result_t`, and the only output is the handle), l.4034 ("an implementation-defined
  configuration format").
- **Issue:** a host-assigned id reaches the Runtime inside the implementation-defined configuration, and
  that is enough. For a Runtime-generated id the host "MUST accept it" before its first use, and the six
  host operations neither return the id nor take an acceptance. The id is in use as soon as startup
  creates module-instance addresses. The duty therefore cannot be discharged through the standard
  interface. The host cannot read the id afterwards either: `get_self` returns it to a module, and the
  host is not one.
- **Impact:** an implementation that generates the id either leaves the MUST unmet or defines an
  implicit acceptance of its own. A host that needs the id, to provision an enrollment for a remote
  profile or to relate its own records to the Runtime's, has to obtain it through a private channel.
- **Reading an implementation needs today:** document that choosing a configuration which lets the
  Runtime generate the id is the host's acceptance of it; a host that needs to know the id assigns it.
- **Overlap:** TS-01 (what the host cannot do through the Host Embedding API), SO-03 (declined), TF-25.
- **Suggested resolution:** add a host operation that returns the Runtime instance id once the handle
  exists and before startup, or state that a configuration permitting generation is the acceptance that
  l.2666-2667 requires.

#### TF-28 — A stop that outlives its drain deadline: the state at expiry, and the state when its cleanup later ends, are not stated
- **Specs:** RUNTIME §3.4 l.569-570 (`stopping`: "Runtime has begun logical shutdown and is waiting for
  applicable draining, lifecycle destruction, realization stop, detachment, and cleanup"; `error`:
  "Realization, initialization, readiness, execution, or cleanup failed"), l.611-613 ("Completion of
  cleanup after a failure MUST NOT by itself change `error` to `unloaded`"; "A new accepted execution
  attempt may leave `error`; a completed explicit stop transitions the instance to `unloaded`"; "Runtime
  MUST reject `start_module` with `NOT_READY` for an instance in `error` while cleanup of a previous
  realization remains unresolved"), l.627 ("Runtime transitions to `unloaded` only after the required
  cleanup or detachment is complete"); §9.1 l.1835-1837 ("Concurrent lifecycle requests MUST NOT create
  duplicate realizations, native contexts, destruction calls, or release operations"; "A `stop_module`
  request for an instance in `stopping` or `unloaded` MUST return its current module state and MUST NOT
  initiate another destruction or release"); §9.3 l.3753 (`cleanup-timeout` is one of the initial
  failure classifications), l.3757 ("Runtime MUST preserve the classification through failure cleanup,
  replace it when a later failure supplies the current cause, and clear it when a new execution attempt
  is accepted or an explicit stop completes successfully"), l.3758 ("A local instance in `error` MUST
  include `failure`"); §10.2 l.3835-3838 (the deployment supplies "finite logical drain deadlines, the
  phase covered by each deadline, and the permitted escalation after expiry"; "Expiry does not establish
  quiescence, successful destruction, or absence of a realization"; "Runtime MUST retain unresolved
  realization ownership and native resources until their actual uses end"; a shared-process native
  realization "MUST NOT be force-released by destroying referenced state or unloading code that can
  still execute"), l.3860-3861 (shutdown continues once each realization is released "or its cleanup
  failure has been recorded according to shutdown policy"); CONFIG l.272 ("MUST NOT destroy the native
  context while the hook can still use it"), l.312 ("If the application outcome is indeterminate, Runtime
  MUST place the module instance in `error`").
- **Issue:** for a native realization in the Runtime's own process nothing can be forced (l.3838). When
  the drain deadline of an explicit stop expires and destruction has not returned, the Runtime can only
  keep waiting. Three points are then open.
  1. The state at expiry. The instance may stay `stopping`, which still describes it (l.569, l.627), or
     become `error` with `cleanup-timeout` (l.570, l.3753). Shutdown records a cleanup failure
     (l.3861). No rule says the same for `stop_module`, and no rule says when `cleanup-timeout` is set
     or whether a record in `stopping` may carry it.
  2. The state when the cleanup ends later, for an instance that was moved to `error`. By l.611 and the
     first clause of l.3757 the instance stays `error` and keeps `cleanup-timeout`, because the cleanup
     completed after a failure. By l.612 and the last clause of l.3757 the explicit stop has now
     completed, so the instance becomes `unloaded` and the failure is cleared. The text does not say
     whether a stop that overran its deadline "completes successfully" when its destruction returns.
  3. A `stop_module` that arrives while the instance is in `error` and that cleanup is unresolved.
     l.1837 covers `stopping` and `unloaded` only, and l.1835 excludes a second destruction. Whether
     the request is answered with the current state, or is itself the explicit stop that completes
     when the pending cleanup ends, is not said.

  The doubt of point 2 also arises with no overrun. A live reconfiguration is pending when an explicit
  stop arrives, and the stop must not destroy the context while the hook can still use it (CONFIG l.272).
  If the application deadline expires first, the outcome is indeterminate and the instance is placed in
  `error` (CONFIG l.312). The hook then returns, and the destruction of the stop completes within the
  stop's own deadline. l.612 and the last clause of l.3757 give `unloaded` with the failure cleared; l.611
  keeps `error` with `configuration-indeterminate`.
- **Impact:** for one history, one Runtime reports `stopping` and then `unloaded`, another reports
  `stopping`, `error` and `unloaded`, and a third stays in `error` until a second stop. The sequence of
  `module_state_changed_event`, the presence of `failure` and what an operator must do after a slow
  stop all differ. Orchestration that treats `error` as a failed instance acts on a stop that only took
  long.
- **Reading an implementation needs today:** at expiry move the instance to `error` with
  `cleanup-timeout`, keep the realization, and refuse `start_module` with `NOT_READY` (l.613). When the
  cleanup ends, keep `error` and the classification (l.611). A later `stop_module` then completes at
  once and gives `unloaded` with the failure cleared; a new accepted start also leaves `error`. A
  `stop_module` received while the cleanup is unresolved starts no second destruction. It is an explicit
  stop of an instance in `error` (l.612): the instance is `stopping` again under a new deadline, and the
  end of the pending cleanup completes that stop and gives `unloaded` with the failure cleared. Where the
  stop itself completed in time, after a live reconfiguration became indeterminate, report `unloaded`
  with the failure cleared.
- **Overlap:** TL-07 (the diagram has no edge from stopping to error), TL-08 (cleanup completion
  produces no event), TF-20 (when `stop_module` answers), NL-06 (answered: cleanup alone never leaves
  `error`).
- **Suggested resolution:** state what the expiry of a stop's drain deadline does to the lifecycle state
  and where `cleanup-timeout` is reported; state whether the later return of that destruction is a
  completed explicit stop or cleanup after a failure; say what `stop_module` does for an instance in
  `error` whose cleanup is unresolved; and say which rule applies to an explicit stop that completes after
  a live reconfiguration became indeterminate.

#### TF-29 — What a preserved instance reports after the Runtime ended without completing shutdown is not stated
- **Specs:** RUNTIME §3.4 l.562 (apart from a stop, the diagram leaves `ready` only by an "unexpected
  realization failure", to `error`), l.565 (`unloaded`: "The module instance is known to Runtime but has
  no active local realization or attached facade binding"), l.627 ("Runtime transitions to `unloaded` only
  after the required cleanup or detachment is complete"); l.2634 ("These rules do not require every
  deployment to preserve logical instances across Runtime restart"); §9.3 l.3505-3506 ("Runtime MUST
  persist the revision with the corresponding state before exposing the change or performing a newly
  accepted execution attempt"; "Before accepting lifecycle requests after restart or state reconstruction,
  Runtime MUST advance each preserved instance's execution revision beyond every value previously exposed
  for that identity"), l.3534 ("Retained selection MUST NOT be reported as a current realization merely
  because it survived a stop, failure, or Runtime restart"), l.3753 (the classifications include
  `host-terminated` and `other`), l.3757 (Runtime clears the classification "when a new execution attempt
  is accepted or an explicit stop completes successfully"), l.3758 ("A local instance in `error` MUST
  include `failure`, using `other` when no more specific cause is established"); §10.1 l.3774-3776 ("it
  MUST reconcile retained requested execution intents, including after Runtime restart"; "Deployment
  documentation MUST distinguish resumption after Runtime restart from retries after execution failure";
  "Reconciliation MUST preserve retained origin, retry accounting, lifecycle ordering, current authority,
  and unresolved cleanup obligations"), l.3783 ("containment of faults that corrupt or terminate that
  process is not guaranteed"); §10.2 l.3842 ("Shutdown MUST preserve retained execution intent and its
  origin"); LOADER l.497-499 ("Unexpected Module Host termination, loss of a required direct binding, or
  an indeterminate live-configuration outcome changes an active realization to failed").
- **Issue:** a Runtime that keeps its instances across a restart writes each lifecycle state before it
  shows it (l.3505). Its store can therefore hold an instance as `loaded`, `ready` or `stopping` when the
  Runtime's process ends with no shutdown: a crash, a kill by the operating system, a power loss. After a
  completed shutdown the answer is given: every instance was stopped and released, so it is `unloaded`
  with its intent kept (l.627, l.3842). For the other case no rule says what the next Runtime reports. Two
  readings are open.
  1. `unloaded`, with no `failure`. The definition fits, since the realization ended with the process
     (l.565). But the transition is allowed "only after the required cleanup or detachment is complete"
     (l.627), and no stop ran: `_MODULE_destroy` was never called. An observer then cannot tell this
     instance from one that was stopped in order.
  2. `error`. The realization was lost unexpectedly, which is the diagram's edge out of `ready` (l.562)
     and LOADER's "loss of a required direct binding" (l.498). A `failure` is then required (l.3758), and
     its classification is open. `host-terminated` is in the list (l.3753) and is defined nowhere; the
     nearest cause in the text is the unexpected end of a Module Host (LOADER l.497), which is not the end
     of the Runtime's own process. Otherwise the classification is `other`.

  The choice also decides how the restart is counted. Deployment documentation has to "distinguish
  resumption after Runtime restart from retries after execution failure" (l.3775), and an instance in
  `error` reads as an execution failure. On a platform that ends the host process routinely, each such end
  would then be charged to the module's retry limit.
- **Impact:** for the same crash one Runtime reports `unloaded` and another `error`, with `other` or with
  `host-terminated`. The first state event after the restart, the readiness result and the execution
  summary differ, and an orchestration module's restart policy treats the same module as resumed on one
  Runtime and as failed on the other.
- **Reading an implementation needs today:** report `error` with `other` for an instance stored as
  `loaded`, `ready` or `stopping`, keep its intent, and document that orchestration counts this state
  after a restart as a resumption and charges no retry; or report `unloaded` with no failure. The first is
  the conservative reading, because it does not report an orderly stop that never took place.
- **Overlap:** NL-10 (who resumes retained intent after a restart; answered), TF-08 (a statically linked
  module across an update of the host binary), TF-26, TF-28, TL-07.
- **Suggested resolution:** state in §9.3 or §10.1 the lifecycle state of a preserved instance when the
  Runtime starts after ending without a completed shutdown; define `host-terminated` and say whether it
  covers the end of the Runtime's own process; and say whether orchestration counts such an instance as a
  resumption under l.3775.

#### TF-30 — Four required refusals have no assigned code: a target owned by another Runtime, `create_module` with no selected declaration, a configuration state too large for a frame, and a revision that cannot advance
- **Specs:** RUNTIME l.3558 ("The target's `runtime_instance_id` MUST identify the Runtime exposing this
  contract"), l.3515 ("Runtime MUST reject a target owned by another Runtime without forwarding the query
  or substituting a facade"), l.2611-2612 ("Runtime MUST reject a target owned by another Runtime rather
  than forwarding the operation or substituting a local facade instance"), l.2579
  ("`get_permission_settings` and `update_permission_settings` MUST target a local module instance owned
  by the Runtime exposing the contract"); against l.449 ("An explicit `runtime_instance_id` MUST identify
  the addressed Runtime; otherwise Runtime MUST return `INVALID_PARAMS`"), l.3659 ("otherwise Runtime MUST
  return `INVALID_PARAMS` without structured detail") and l.3662 ("An unknown or undisclosable selected
  record MUST produce non-revealing `NOT_AUTHORISED`"); l.3614-3619 ("Runtime MUST select one accepted
  declaration for `module` under active policy or fail the request"; "An unavailable or unacceptable exact
  selection MUST fail without substituting another package or version"; "If active policy does not select
  one accepted declaration, the request MUST fail without creating an instance"); l.3507 ("Revision
  exhaustion or persistence failure MUST prevent new execution attempts"), l.3442-3443 (in the rules for
  listeners and exports: "Other resource, persistence, or internal failures MUST use the applicable more
  specific shared error code, or `MODULE_ERROR` when none applies"; "Resource exhaustion alone MUST NOT be
  classified as Runtime readiness failure"), l.3383 ("If a disclosable record cannot fit in a permitted
  response, Runtime MUST fail with `MODULE_ERROR`"), l.1910-1916 (the table of precondition failures);
  CONFIG l.100-101 ("Runtime MUST reject a state mutation that would advance it beyond the maximum
  `uint64` value"; "MUST reject the attempt without invoking that behavior when it cannot"), l.111
  ("Runtime MUST reject without mutation any source or state transition whose resulting complete state
  would violate this limit"), l.192-198 and l.292-296 (the two tables of configuration failures);
  TRANSPORT l.385 ("An oversized ordinary Request MUST NOT be sent and MUST fail its local invocation with
  `MODULE_ERROR`").
- **Issue:** each of these rules tells Runtime to refuse a request and names no code for the refusal.
  1. A target owned by another Runtime. `retire_module`, `get_execution_summary`, the five configuration
     methods and the two permission-settings methods take a complete module-instance address, and each
     must refuse one that names another Runtime (l.3558, l.3515, l.2612, l.2579). Where the same check is
     made on a provider address the code is `INVALID_PARAMS` (l.449, l.3659). Here none is given.
     `INVALID_PARAMS` follows by analogy. But the address also names no record this Runtime knows, and an
     unknown record is answered with a non-revealing `NOT_AUTHORISED` (l.3662).
  2. `create_module` when active policy selects no accepted declaration, or when the exact selection is
     unavailable (l.3614-3619). The request must fail. `NOT_AUTHORISED`, `INVALID_PARAMS` and `NOT_READY`
     can each be argued, and they differ in what the caller learns about the modules this deployment can
     create.
  3. A configuration value or transition whose resulting state would not fit a frame (CONFIG l.111).
     Neither CONFIG table has a row for it. The rows about the value give `INVALID_PARAMS` (CONFIG
     l.197-198); the size rules elsewhere give `MODULE_ERROR` (TRANSPORT l.385, RUNTIME l.3383).
  4. A revision that cannot advance, or state that cannot be written. CONFIG l.100-101 refuses the
     mutation or the attempt, and RUNTIME l.3507 prevents new execution attempts. The refused
     `update_configuration`, `apply_configuration`, `start_module` or `recover_module` has no code.
     `MODULE_ERROR` follows from l.3442, which is written for listener and export requests; `NOT_READY`
     follows from the lifecycle row at l.1914, against l.3443.
- **Impact:** a caller reads `INVALID_PARAMS` as its own mistake, `NOT_AUTHORISED` as missing authority,
  `NOT_READY` as a reason to retry and `MODULE_ERROR` as a fault. Two Runtimes answer the same request
  with different codes, and a conformance test can assert none of the four.
- **Reading an implementation needs today:** `INVALID_PARAMS` without detail for a target on another
  Runtime; a non-revealing `NOT_AUTHORISED` when no declaration is selected; `MODULE_ERROR` for a state
  that would not fit, and for a revision or a store that cannot take the change.
- **Overlap:** EC-01 to EC-04 (the codes of Runtime Control's own outcomes), TF-16 (route establishment
  that can return nothing), TF-18 (the order of checks), TL-09.
- **Suggested resolution:** add the four cases to the table at RUNTIME l.1910-1916 and to the CONFIG
  tables at l.192-198 and l.292-296.

#### TF-31 — An authority request from an ordinary caller that names another consumer, or carries `execution_renewal`, must be refused, and neither the code nor the record of the refusal is stated
- **Specs:** CA l.87-91 ("Runtime MUST supply Capability Authority with authenticated context for the
  consumer"; "Runtime MUST populate or validate the request's `consumer` against that context before
  dispatching a Capability Authority method"; "For other methods, the consumer is the module instance
  authenticated at the Capability Authority invocation boundary"), §5.1 l.578-580 ("Runtime MUST set it
  only while that authorization remains valid under Section 8"; "Runtime MUST reject this field on
  evaluation requests supplied by ordinary callers, including routed calls"; "Capability Authority MUST
  receive the indication through the Runtime-enforced invocation boundary required by Section 2");
  l.1167-1170 (an audit record is required "for each evaluation result or failure", and a rejection before
  evaluation begins "is an admission failure and does not require an audit record"), l.1373-1376
  ("`evaluate` is the Runtime-facing policy-decision method"; "Ordinary consumers MUST NOT gain direct
  authority to call `evaluate` merely because they can request a provider route or invoke another
  Capability Authority method"); RUNTIME l.1665-1668 ("For Capability Authority `evaluate`, the request's
  `consumer` remains the authenticated module whose attempted operation is evaluated"; "An ordinary module
  invoking a system service still requires its own consumer-bound route and provider-access authority"),
  l.1745-1748 ("An authorization denial is an explicit deny result from runtime authority policy"; "An
  authority-evaluation failure occurs when Runtime cannot obtain or validate a required authority
  decision"; "retained observation or audit material MUST distinguish denial from evaluation failure"),
  l.2559 (for `get_self`: "Runtime MUST reject a call without an authenticated module-consumer association
  with `NOT_AUTHORISED`").
- **Issue:** the Capability Authority is a module provider, so a module that policy allows holds a route
  to it and calls its methods (RUNTIME l.1668). Two checks on such a call belong to Runtime, at the
  invocation boundary and before the provider sees the request: the request's `consumer` has to be the
  authenticated caller (CA l.88), and `execution_renewal` has to be absent (CA l.579). The result of a
  failed check is not given.
  1. The code. The call itself was authorized: the route exists and the method is within its scope.
     `NOT_AUTHORISED` reports a refusal that policy did not make, and `INVALID_PARAMS` reports a value
     that the schema allows. For `consumer`, CA l.88 also lets Runtime populate the field, so on one
     reading a wrong value is overwritten and the call proceeds for the caller itself.
  2. The record. The refusal is neither a policy denial nor an evaluation failure (RUNTIME l.1745-1746),
     the two kinds that retained material has to tell apart (l.1748). It also comes before the authority's
     own audit begins (CA l.1170). Whether anything is recorded, and as what, is not said.

  CA l.579 presupposes that an ordinary caller can reach `evaluate` on a route. CA l.1375-1376 says only
  that a route or another method does not give that authority by itself. Whether a grant can give it, and
  for which consumers the caller may then ask, is not stated either.
- **Impact:** a management module that asks whether an operation would be allowed for another module gets
  `NOT_AUTHORISED` on one Runtime, `INVALID_PARAMS` on another, and on a third a decision about itself,
  with nothing to show that the question was changed. An audit trail shows the attempt on one deployment
  and not on another.
- **Reading an implementation needs today:** refuse both with `NOT_AUTHORISED` and without dispatch, never
  replace a supplied `consumer` that differs from the caller, and keep the refusal in retained material as
  a kind of its own, neither a denial nor an evaluation failure.
- **Overlap:** TL-04 (the authority's own codes), RT-02 (the calls the engine makes for no module), TF-18.
- **Suggested resolution:** assign the code for both refusals, in CA §5.1 and beside l.88; say that a
  `consumer` supplied on a routed call is validated and never replaced; say whether the refusal is
  audited; and state whether an ordinary caller can be authorized to call `evaluate` at all.

#### TF-32 — Which permission scopes an execution decision must cover is not stated
- **Specs:** CA §3.3 l.344-345 ("Runtime MUST obtain an allow decision before asking Module Loader to
  realize a direct native implementation"; "The decision MUST cover the module execution operation and
  every required permission scope"), l.351-353 (for a hosted realization, "the module execution operation,
  selected hosted placement, and required permission scopes"), l.369-372 ("A package or module manifest's
  requested permissions are policy inputs"; "Capability Authority maps each declared permission into one
  or more authority scopes according to the permission's defining specification or profile"); l.392
  ("Capability Authority MUST reject an unknown permission or invalid constraints"), l.484-485 ("A request
  may carry more than one scope when the operation requires multiple simultaneous constraints, such as
  module execution plus network and persistent-state permissions"), l.563 ("For every requested scope, an
  allow decision MUST contain at least one equal or narrower allowed scope"); LOADER l.426 ("Runtime MUST
  obtain authorization for module execution and every required permission before invoking `realize`");
  RUNTIME l.1439-1442 ("`requested_permissions` contains module-declared policy inputs"; "The declarations
  do not grant authority, approve execution, or prove that the selected execution path can enforce the
  requested constraints"), l.2538-2539 ("Omitted permissions are denied, including when the array is
  empty; declarations and grants MUST NOT bypass these limits"; "Settings do not modify accepted module
  declarations or independently authorize execution"), l.2541 (a new instance starts with "an empty
  permission array, status `applied`, and no failure"), l.2543 ("module declarations and
  `requested_permissions` alone MUST NOT supply those settings"), l.2596 ("Before widening effective
  access, Runtime MUST establish current execution and permission authority covering that access"), l.3803
  ("including deployment intent initially blocked by missing permissions").
- **Issue:** the execution decision has to cover "every required permission scope" (CA l.345), and nothing
  defines which permissions are required. Runtime builds the evaluation request, so it has to choose
  between two sets.
  1. The permissions the module declares in `requested_permissions`. The request then carries a scope for
     each of them, and an allow has to cover each (CA l.563). A new instance has empty settings (RUNTIME
     l.2541), under which every permission is denied (l.2538), and a declaration cannot supply settings
     (l.2543). So either the authority is asked to allow what the settings deny, or a module that declares
     any permission cannot start until an administrator has saved settings that name all of them. The
     words "initially blocked by missing permissions" (l.3803) fit this reading.
  2. The permissions in the instance's saved settings. A module with empty settings then needs the
     execution scope only, and starts with every declared permission denied. The declaration is input for
     whoever writes the settings and the policy (CA l.369), and whether the module can work without a
     permission is its own affair.

  Under the first reading a further case follows. The authority "MUST reject an unknown permission" (CA
  l.392), so a module that declares a permission of a profile the deployment has not selected cannot be
  started there at all.
- **Impact:** a module with a declared permission and no saved settings starts on one Runtime and is
  refused on another. A policy author cannot tell whether a grant for execution has to name the declared
  permissions. A package that declares a permission it can do without is portable only under the second
  reading.
- **Reading an implementation needs today:** request the execution scope together with one scope for each
  permission of the saved settings, so that an instance with empty settings needs the execution scope
  alone.
- **Overlap:** TF-10 (the state after a start that authorization refuses), TL-04 (the rejection of an
  unknown permission has no assigned code).
- **Suggested resolution:** define in CA §3.3 which permission scopes an execution decision requires,
  those of the instance's saved settings or those of its declaration, and say whether a declared
  permission that the settings omit prevents the start.

#### TF-33 — How an established route is re-authorized after a policy change is not stated: the request, its timing, the new expiry, a failed evaluation and the recorded cause
- **Specs:** CA l.290-292 ("An allow decision permits Runtime to create or renew a route within the
  allowed scope; it does not create the route"; "An allow decision used to keep a route or provider
  session usable MUST contain `valid_until`"), l.869-872 (after loss of the notification path, "Runtime
  MAY retain allocated routes or sessions while obtaining a fresh decision, but they MUST remain unusable
  for protected operations until reauthorized"), l.894 ("On `policy_changed`, Runtime MUST invalidate
  every cached decision from that Capability Authority"), l.906-911 ("After processing a policy-change
  notification, Runtime MUST re-evaluate dependent operations before admitting another protected
  operation"; "It MUST make a dependent route unusable when the new decision denies the route or narrows
  its scope below the route's bound scope"); RUNTIME l.1732-1733 ("Authority to establish or renew the
  route does not itself authorize the call"), l.2502-2505 (among the failure codes, `authority-denied` is
  "A policy decision denies the route access" and `authority-revoked` is "The route authority has been
  explicitly withdrawn"), l.2520 ("a route record in `failed` or `revoked` state MUST include `failure`"),
  l.3164-3165 ("An allow decision used for an established route MUST have a validity end, and `expires_at`
  MUST NOT be later than that end"), l.3183-3184 ("`renew_route` preserves the route identity, consumer,
  selected provider, contract, and access scope"; "It performs a new authority check and may extend
  `expires_at` and replace `decision_id`").
- **Issue:** after a policy change an established route depends on a new decision (CA l.910). The text
  gives the result of a deny and of a narrowing allow, and leaves open how and when that decision is
  obtained and what else it changes.
  1. The request. Two kinds of decision stand behind a route: the one that established or last renewed it,
     and one for each call (RUNTIME l.1732-1733). The new decision for the route is presumably a renewal
     that Runtime evaluates by itself, with no `renew_route` from the consumer. Whether that is meant, or
     whether the next call's decision is enough, is not said.
  2. The timing. "before admitting another protected operation" (CA l.906) allows the evaluation when the
     notification is processed, for every dependent route, or at each route's next use. Under the second,
     the route of an idle consumer stays `ready` in every record and list although policy now denies it,
     and `route_state_changed_event` is produced only when the consumer next calls.
  3. The expiry and the decision id. A consumer's renewal "may extend `expires_at` and replace
     `decision_id`" (RUNTIME l.3184). For a re-authorization that Runtime starts, nothing says whether the
     record takes the new decision's id, or whether `expires_at` may move later. That it must move earlier
     when the new validity end is earlier follows from l.3165.
  4. An evaluation that fails. If the authority cannot be reached, the route is neither denied nor
     allowed. After loss of the notification path a route stays allocated and "unusable for protected
     operations until reauthorized" (CA l.872). For a policy change the text names only the deny and the
     narrowing. Whether the route stays `ready` and refuses operations, or becomes `failed` with
     `authority-evaluation-failed`, and whether a later allow restores it, is not said.
  5. The recorded cause. For a deny, `authority-denied` and `authority-revoked` both fit their definitions
     (RUNTIME l.2502, l.2505). For an allow narrower than the bound scope neither fits plainly. The state,
     `revoked` or `failed`, is given for neither case.
- **Impact:** after the same policy change, routes stop working at different times on two Runtimes, and
  their records show different states, failure codes, decision ids and expiry times. An observer of route
  state sees a denied route as `ready` on one of them for as long as its consumer is idle.
- **Reading an implementation needs today:** when the notification is processed, evaluate each dependent
  route as a renewal. On an allow that covers the bound scope keep the route, record the new decision id,
  and set `expires_at` to the earlier of its old value and the new validity end. On a deny or a narrowing
  allow, revoke the route with `authority-denied`. On a failed evaluation treat the route as CA l.872
  treats loss of the notification path: keep it, refuse protected operations, and evaluate again at its
  next use.
- **Overlap:** TF-17 (a renewal that the consumer requests and policy denies), NA-07 (event deliveries
  after a policy change; answered), NA-03, TL-03, TF-24.
- **Suggested resolution:** say beside CA l.906-911 that re-evaluating a dependent route is a renewal
  evaluated by Runtime, when it has to happen, and what it does to `expires_at` and `decision_id`; and
  give the route state and failure code for a deny, for a narrowing allow and for a failed evaluation.

#### TF-34 — Which fields of a record the selectors of a Runtime Control scope are compared with is not stated
- **Specs:** CA l.180-190 (`runtime_control_scope` has the optional selectors `modules`, `instances`,
  `providers` and `routes`), §3.2 l.306-309 ("The remaining optional fields constrain the module, module
  instance, provider, or route records that may be observed or targeted"; "Every present constraint MUST
  match the attempted operation or returned observation"); l.565-567 ("For Runtime Control scopes that
  differ only in their subject selectors, those selectors are alternatives"; "Runtime MUST NOT combine
  selector fields from different alternatives to admit a subject that no individual alternative permits");
  RUNTIME l.2103-2108 (`route_record` has the required fields `route`, `consumer`, `target_provider` and
  `module`, and an optional `instance`), l.2952 ("The `consumer` field on a `route_record` identifies the
  consumer whose authority the route represents"), l.3373-3375 ("Runtime MUST apply method authorization,
  scope constraints, record visibility, and optional-field redaction before creating that snapshot"; "A
  record whose required fields or identity key cannot be disclosed MUST be omitted"), l.3496-3498 (a
  module event about a local instance "MUST include its exact `instance` and omit `provider`"; "Event
  observation authority MUST be checked for that exact instance or provider before delivery commitment"),
  l.3663 (in a lifecycle request, "a provider selector naming a local module implementation MUST produce
  `INVALID_PARAMS`"), l.3732-3735 ("Runtime MUST deliver Runtime Control state events only while the
  authenticated subscriber remains authorized to observe the referenced module, provider, or route"; "A
  Runtime Control subscription MUST NOT reveal unrelated provider inventory, route state, event
  publishers, or subscribers").
- **Issue:** every present selector "MUST match the attempted operation or returned observation" (CA
  l.308), and a record can hold more than one value of the kind a selector names, or none. Which value is
  compared is not said.
  1. A route record names two parties: the consumer, which is a module instance, and the provider, with
     the provider's module name and its optional instance. An `instances` selector can be compared with
     the consumer's instance, with the provider's, with either, or with both. A scope written to let a
     module watch the routes into its provider, and one written to let it watch the routes it consumes,
     look the same.
  2. A selector for a fact the record does not carry. A module event about a local instance carries no
     provider (RUNTIME l.3496), and a listener record carries no instance. The selector is present, and
     whether it then fails to match, which hides the record, or does not apply, is not said. A `providers`
     selector that names the provider of a local instance is the common case.
  3. The consumer of a route. `consumer` is a required field of the record, so a record whose consumer may
     not be disclosed is omitted whole (RUNTIME l.3374). No selector says that an observer may learn who
     consumes a provider. If a scope that selects the provider is enough to show the record, every
     observer of a provider learns its consumers, which sits badly with l.3734-3735.
- **Impact:** the same grant shows different route records and delivers different state events on two
  Runtimes. A policy author cannot write a scope for the routes into one provider, or for the routes of
  one consumer, and know what it admits. Under one reading, authority to observe a provider discloses the
  address of each of its consumers.
- **Reading an implementation needs today:** compare each selector with the subject's own facts and never
  with the consumer of a route: for a route record, `routes` with the route id, `providers` with
  `target_provider`, and `modules` and `instances` with the provider's. A selector that names a fact the
  subject does not carry does not match.
- **Overlap:** TF-09 (which scope counts as observation authority), NO-01.
- **Suggested resolution:** state in CA §3.2 or RUNTIME §9, for each kind of record and event, the field
  each selector is compared with, what a selector means for a record without that field, and which
  authority discloses the consumer of a route.

#### TF-35 — A Runtime Control subscription that the Runtime stops serving gives its subscriber no signal
- **Specs:** INTERFACE l.1461-1464 ("A subscription exists only while its route is ready"; "the binding
  MUST deactivate every subscription on that route and MUST NOT begin another handler invocation"),
  l.1474-1476 ("The route handle also provides `observe_end` for local termination notification"; "It
  requires no additional observation authority and MUST be supported in every invocation mode"), l.3837
  (the Runtime Control `subscribe` and `unsubscribe` operations "apply the subscription semantics in
  Section 2.5"); TRANSPORT l.801 ("A callee MUST NOT silently discard an Event committed to an active
  subscription"), l.812-813 ("Connection closure is the observable failure boundary and terminates every
  subscription on that connection"), l.815 ("An implementation MUST document which overflow actions may
  occur for transported event output and the conditions selecting them"); RUNTIME l.3426-3428 ("Connection
  or subscription loss requires resubscription and a fresh query"; "Observers requiring a refreshed
  inventory MUST query it, including periodic resynchronization when uninterrupted hint delivery or
  continued visibility cannot be established"), l.3511 ("Queries can resynchronize observation after
  missed events or uncertain request outcomes"), l.3732-3733 ("Runtime MUST deliver Runtime Control state
  events only while the authenticated subscriber remains authorized to observe the referenced module,
  provider, or route").
- **Issue:** a module subscribes to Runtime Control events through the binding it receives at
  initialization. That binding is not a route: it has no route state and no `observe_end`. Runtime can
  nevertheless stop serving such a subscription. The subscriber's authority to observe can end (RUNTIME
  l.3732-3733), and events can be committed faster than the handler returns, until the bound that Runtime
  keeps for them is reached. For a transported subscriber the second case ends in backpressure or in a
  closed connection, which the subscriber sees (TRANSPORT l.812-813). For the local binding two things are
  not said.
  1. What Runtime may do at its bound: end the subscription, drop events from it, or hold up the operation
     that commits the change (see TF-22).
  2. How the subscriber learns of it. RUNTIME l.3426 tells an observer what to do after subscription loss,
     and no operation, result or event reports that loss on a Runtime Control binding. A subscriber that
     was cut off holds a subscription that looks active and receives nothing.

  The inventory hint has a fallback, periodic resynchronization (RUNTIME l.3428). The state events have
  l.3511 only, and it helps an observer that knows events were missed.
- **Impact:** an orchestration module that drives recovery from state events cannot tell a quiet
  deployment from a lost subscription, and has to poll at an interval of its own choosing to be correct.
  Under load one Runtime delays lifecycle operations, another drops events and a third ends the
  subscription, and the subscriber cannot tell which.
- **Reading an implementation needs today:** bound the pending events of each subscription; when the bound
  is reached end the subscription, never drop single events from it, and record a diagnostic. Subscribers
  that act on state events resynchronize periodically.
- **Overlap:** TF-22 (the thread and the time of delivery), NE-05 (a slow transported subscriber), TF-09,
  TF-24.
- **Suggested resolution:** give the Runtime Control binding a way to report the end of a subscription, as
  a route handle has `observe_end`; or state that Runtime never ends or thins a local Runtime Control
  subscription and holds up the committing operation instead.

#### TF-36 — Whether a realization mechanism that is not the Module Loader may report LOADER's strategy names and error codes is not stated
- **Specs:** RUNTIME l.27 ("An implementation may conform to this specification without implementing
  Module Loader"), l.38 ("An implementation conforming only to this specification MAY use
  implementation-local mechanisms for those concerns"), l.212 ("An implementation-local realization
  mechanism or a bound Module Loader provider may realize accepted implementations"), l.2309-2316 (the
  `implementation` record is `direct_static`, `direct_dynamic`, `hosted_dynamic` with a placement, or
  `implementation-specific`), l.3527-3528 ("The implementation record reports the selected realization
  strategy and, for `hosted_dynamic`, its concrete placement as defined by LOGOS-MODULE-LOADER"; "Other
  realization mechanisms MUST use `implementation-specific`; transport mode alone does not establish a
  concrete placement"), l.3754 ("When the cause is a typed Module Loader error and no more specific
  Runtime classification applies, the classification MUST be `loader-` followed by that error's defined
  code"); LOADER l.23-26 ("Every Module Loader provider MUST be a local module provider backed by a local
  module instance"; "An implementation MAY co-locate or statically link Module Loader code, but Runtime
  MUST represent that code as a direct local module instance"), l.120-122 (a realization strategy is "one
  of the three ways Module Loader applies the canonical module ABI").
- **Issue:** a Runtime with no Module Loader instance realizes modules through a mechanism of its own
  (RUNTIME l.212). That is a Runtime which claims RUNTIME alone, since a complete system realizes every
  local module through the bound Module Loader (BCP l.289). Such a mechanism commonly does what LOADER's
  direct strategies describe: it binds a statically linked module, or loads a library and applies the
  native ABI. "Other realization mechanisms MUST use `implementation-specific`" (RUNTIME l.3528), and
  other than what is not said. On one reading it means other than the three strategies, so a local
  mechanism that performs a static binding reports `direct_static`. On the other it means other than the
  Module Loader, so a Runtime without a Loader instance reports `implementation-specific` for every
  module, and an observer cannot tell a static binding from a loaded library. LOADER defines a strategy as
  a way the Module Loader applies the ABI (l.121), which supports the second reading. Failures raise the
  same question: RUNTIME l.3754 ties the `loader-` classifications to "a typed Module Loader error", so a
  local mechanism that fails for a cause LOADER's codes name reports either that `loader-` code or
  `other`.
- **Impact:** small. The execution summary and the failure classification of the same module differ
  between a Runtime that has a Loader instance and one that does not, and a tool that shows the strategy
  or keys on `loader-` codes loses both on the second.
- **Reading an implementation needs today:** report `implementation-specific`, and no `loader-`
  classification, unless a Module Loader instance performed the realization.
- **Overlap:** TF-08 (statically linked modules), TF-29.
- **Suggested resolution:** one sentence at RUNTIME l.3528 and one at l.3754 saying whether an
  implementation-local mechanism that follows a LOADER strategy may report that strategy's name and
  LOADER's error codes.

### 3.2 The system contracts, checked against their own rules

The CDDL of Runtime Control (RUNTIME §9.2-§9.3), Configuration (CONFIG §9), Capability Authority, Module
Loader and Package Manager was extracted from the specs, parsed, and checked against INTERFACE §1 and
§2.1, cdCDDLe §5.1 and the structural selection rules. The prose of each spec was compared with its CDDL.

What came back clean is listed in Appendix F. The items below are what did not.

#### TL-01 — `logos_types.h` is said to declare every common-schema type by a projection that §2 does not define
- **Specs:** INTERFACE §5.2 l.3382-3384 ("`logos_types.h` also supplies the canonical C declarations for
  every named type in the pinned common schema surface from Section 5.1 ... Those declarations are
  derived by Sections 2.1 through 2.3, including the dedicated common-name projection and the
  `logos.error_code` exception. Generated contract headers include `logos_types.h` and MUST NOT
  redeclare its fixed common types"); §2.1 l.834-844 (common types "use their exact predefined names
  from `logos_types.h`", with a table of three: `logos_error_code_t`, `logos_error_detail_t`,
  `logos_schema_commitment_t`); §5.1 l.3222-3254 (the common schema has eight named types).
- **Issue:** §2.1 contains no "dedicated common-name projection"; it has the three-row table and no rule
  that derives a name. Each section points at the other. The §5.2 listing declares only
  `logos_error_code_t` (l.3459). `logos_error_detail_t` and `logos_schema_commitment_t` occur nowhere
  else in the twelve files, so their layout is unspecified, and `logos.invalid_params_reason`,
  `logos.invalid_params_path_segment`, `logos.invalid_params_detail`, `logos.schema_request` and
  `logos.schema_response` have no C name at all.
- **Impact:** Runtime Control, the Package Manager contract and the manifest schema reference
  `logos.schema_commitment` (for example RUNTIME l.2068), and a generated header may not redeclare it.
  Two independent tools therefore have to invent the same struct for the headers of the system contracts
  to agree, which is the property §2 exists to guarantee (INTERFACE l.641).
- **Overlap:** NX-04 (module-derived C type names against the fixed `logos_types.h` names).
- **Suggested resolution:** print the eight declarations in the §5.2 listing, or state a projection
  rule in §2.1 and extend the table to all eight types.

#### TL-02 — A specification and a system contract are named that are not in the set
- **Specs:** BCP l.52 (LOGOS-MODULE-CREDENTIAL-STORE in the document map), l.199-200 ("defines
  authenticated creation and presence queries for encrypted credentials in protected
  deployment-assigned slots"), l.276 (module name `logos_credential_store`), l.282-284 ("Its contract
  requirements apply when conformance to LOGOS-MODULE-CREDENTIAL-STORE is claimed"); SECURITY l.528-529
  (credential values "may be submitted through its authorized `create` or administrative requests,
  subject to the ... requirements of LOGOS-MODULE-CREDENTIAL-STORE").
- **Issue:** no such file exists at `6a4dfa28`, and the name is in neither document's reference list.
  The owner's answer to NS-03 refers to "The existing Credential Store", and CONFIG l.57 excludes
  credentials from configuration, which leaves this service as the place they go.
- **Impact:** the answer to "where do a module's keys live" (a node's network private key, a key store)
  cannot be evaluated, and a fifth system contract has not been through any of the checks of this
  section.
- **Overlap:** NS-03 (secret storage in the deployment-profile checklist).
- **Suggested resolution:** publish the specification with the set, or mark the references as
  forthcoming and say what a deployment does until then.

#### TL-03 — Route states: `draining` has no entry or exit rule, expiry has a failure code and no state, and a subscription on a draining route is both ended and alive
- **Specs:** RUNTIME l.1964-1970 (`route_state`), l.3053-3059 (the only meaning given to `draining`),
  l.3340-3341, l.3489 (`close_route` goes straight to `closed`), l.1845-1846 (the terminal set is defined
  by cause: `close_route`, failure, revocation), l.3188-3189 (renewal fails for "unknown, closed, failed,
  or revoked") against l.3476 ("Only a nonterminal route can renew"), l.1342 ("When the route becomes
  closed, failed, revoked, or expired"), l.3032, l.2504 and l.2517 (failure codes `authority-expired`
  and `route-timeout`), l.2520 (a record in `failed` or `revoked` state includes `failure`), l.3474-3475
  (session loss is separate from route state); INTERFACE §2.5 l.1461-1464 ("A subscription exists only
  while its route is ready. When the route enters a terminal state, the binding MUST deactivate every
  subscription"); RUNTIME l.1027-1030.
- **Issue:** nothing puts a route into `draining` or takes it out, and whether a draining route can be
  renewed depends on whether one reads l.3188 (a list that omits it) or l.3476 (nonterminal). Expiry has
  a `failure.code` and no named state: `failed` or `revoked` is not chosen, and the terminal set of
  l.1845 does not list expiry. A draining route is neither ready (so its subscriptions do not exist)
  nor terminal (so they have not been deactivated). `ready` does not imply a usable path, because a
  route can stay `ready` after its session is lost (l.3474-3475), and nothing in the record says so.
- **Impact:** implementations disagree on whether a draining or just-expired route can be renewed, what
  `new_state` an expiry produces, and when events stop.
- **Overlap:** NE-06, EC-03, EC-05, TR-06, NA-03 (answered with codes and `expires_at`).
- **Suggested resolution:** state which operations enter and leave `draining`; map expiry to one named
  state and add it to l.1845; rewrite INTERFACE l.1461 as "until its route leaves `ready`" or keep
  subscriptions through `draining` explicitly.

#### TL-04 — The Capability Authority enumerates sixteen denial and error codes and assigns four
- **Specs:** CA §5 l.505-512 (`denial_code`, seven values), §7 l.767-776 (`error_code`, nine values),
  l.784-785 (`denial` is a policy result, `error` an inability to process). Assigned in prose:
  `invalid-request` (l.714, l.1132), `grant-not-active` (l.745), `grant-not-found` (l.1390),
  `authority-unavailable` (l.1345). MUST-reject rules with no code: l.138 (unordered or duplicate
  set-valued array), l.392 (unknown permission or invalid constraints). By contrast LOADER l.620-631 and
  PM l.1474-1485 define every value. Related rules: l.484-486 (a request may carry several scopes "when
  the operation requires multiple simultaneous constraints"; "An evaluation request MUST NOT combine
  independent operations"), l.744 ("Revoking an already revoked grant is idempotent and returns its
  current record"), l.1167-1168 ("Capability Authority MUST produce an audit record for each evaluation
  result or failure, grant issuance, grant revocation, grant expiry, and policy change"), l.1389-1390
  ("After method authorization, an unknown grant and a grant hidden from the consumer both produce
  `grant-not-found`").
- **Issue:** no sentence says when a CA returns `scope-denied` rather than `not-granted`, which denial
  codes apply to `evaluate` and which to `issue_grant`, or what `not-authorised` is for: a policy refusal
  is by definition not an `error`, yet `revoke_grant_response` has no `denial` arm (l.662-664) and its
  audit outcomes are only `success` and `failure` (l.1150). Three further points have no rule. The order
  among the outcomes: the one fixed step is that hiding a grant comes after method authorization
  (l.1389-1390), and an authority that resolves a named grant or target before it has found a rule that
  lets the caller act on it shows, through the code, whether that grant or target exists. A repeated
  revocation is idempotent (l.744), and whether it writes a second audit record under l.1167-1168 is not
  said. Which scope kinds one request may combine as a single operation, beyond execution with permissions
  (l.484-486), and the code for a request that combines two operations, are not given.
- **Impact:** two CA providers pick different codes for one condition; Runtime's mapping to its own
  channels and the audit trail differ; no conformance test can assert a value.
- **Overlap:** the EC group lists codes the specs need and do not assign; this is the converse.
- **Suggested resolution:** a one-line definition per value in CA §5 and §7, as LOADER §10 has, a `denial`
  arm (or a stated code) for a refused revocation, the order of the checks, whether a repeated revocation
  is audited, and the scope combinations that one evaluation request may carry.

#### TL-05 — "Consume by schema reference" is promised for types that the schema rules make unreferenceable
- **Specs:** LOADER §3 l.142-144 ("`logos.module_loader.realization_descriptor` is the canonical
  realization handoff type. Other specifications may consume it by schema reference"); PM §16
  l.1776-1777 ("Other Core specs consume them by schema reference when they need package facts");
  INTERFACE §1.1 l.118 ("An external named-type reference in a concrete module or interface contract
  schema MUST resolve to exactly one declaration in an explicitly supplied supporting schema or the
  pinned Logos common schema"), l.103 (a supporting schema references no other schema).
- **Issue:** both types live in concrete module schemas (`_module = "logos_module_loader"`,
  `"logos_package_manager"`), which no other schema may import. No CDDL outside the owner references
  either namespace; the borrowers re-declare by hand. CA l.157-160 and l.318-321 call its copies "wire
  projections" whose "subtree roots are distinct". RUNTIME l.2300-2304 is a third copy: it spells out
  the Package Manager's signer record and its profile literal inside `execution_selection.signer`.
- **Impact:** the ownership sentences describe a mechanism that does not exist; agreement between copies
  rests on review (they agree today).
- **Overlap:** ND-08, C-12 and NX-05 (layer direction; the owner's answer to NX-05 repairs the
  reference lists and relocates no type).
- **Suggested resolution:** replace "by schema reference" with "by projection" and list the
  projections; or move the records other specs need into supporting schemas, as RUNTIME §9.2 and CONFIG
  §9 already do for their shared types. Only `static_binding` (LOADER l.177-179) is leaf-only today; the
  others would also need INTERFACE l.103 relaxed.

#### TL-06 — Records that no method or event reaches sit inside the callable contracts, so changing them changes the contract identity every peer must match
- **Specs:** RUNTIME l.2005-2028 (`remote_identity_profile`, `trust_anchor_id`,
  `subject_public_key_info`, `remote_runtime_enrollment`) with l.2678-2679 ("a provisioning and Runtime
  input record, not a new Runtime Control method or a record disclosed to ordinary modules") and l.2689;
  CA §9.1 l.1228-1243 (`call_evidence_profile`, `evidence_key_id`, the proof and claim records); PM §4.3
  l.497 and l.504-507 (`package_signing_key_id`, `package_signature_claim`);
  COMMITMENT l.341-342 (every local named type is a schema declaration and so part of the root);
  RUNTIME l.2803-2805 (both peers of a remote Runtime Control connection "MUST use that same selected
  contract"); PM l.246-247 (the manifest has its own schema "so a Package Manager API change does not
  change the schema identity of signed manifests").
- **Issue:** ten declarations are reachable from no request, response or event of the contract they are
  declared in. They are off-contract formats (a deployment input record and two signed payloads), but an
  edit to any of them changes the Runtime Control, CA or Package Manager schema root. The call-evidence
  profile is an example: replacing the signature algorithm of call evidence changes the literal at CA
  l.1229, and with it the Capability Authority contract root, although no method or event of that
  contract changes. For Runtime Control the root is the Hello identity between two Runtimes, so a phone
  and a home node whose releases differ only in the enrollment record format cannot open a control
  connection (`VERSION_MISMATCH`). The manifest has exactly this separation; the signature claim that
  signs it does not.
- **Impact:** needless coupling between provisioning or signing formats and the contract identities
  that routes, grants and remote peers pin; offline signers and verifiers must extract a type from a
  callable module's document.
- **Overlap:** HC-04, NR-02 and NF-12 (enrollment stays deployment-defined), C-12.
- **Suggested resolution:** move the enrollment record into `logos.runtime` or a provisioning supporting
  schema, and the two signed-claim types into supporting schemas of their own.

#### TL-07 — The module state diagram omits two transitions that the prose requires
- **Specs:** RUNTIME §3.4 l.553-563 (edges: unloaded to loaded, loaded to ready, loaded to error, ready
  to stopping, ready to error, stopping to unloaded, error to unloaded by "explicit stop and cleanup",
  error to loaded). Against: l.1839-1840 ("If `stop_module` is ordered after an incomplete start or
  recovery, Runtime MUST prevent that attempt from later making the instance `ready`") and l.620, l.3847
  (stop and shutdown move instances to `stopping`): loaded to stopping is missing. l.569-570 and
  l.3873-3874 (cleanup happens in `stopping`; `error` includes a failed cleanup): stopping to error is
  missing. The edge from error to unloaded has its rule at l.611-612 ("Completion of cleanup after a
  failure MUST NOT by itself change `error` to `unloaded` ... a completed explicit stop transitions the
  instance to `unloaded`").
- **Issue:** the diagram lacks the two transitions, and whether an explicit stop from `error` passes
  through `stopping` is not said.
- **Impact:** `module_state_changed_event` carries `old_state` and `new_state`; observers and conformance
  tests cannot tell which pairs are legal for stop-during-start and for failed cleanup.
- **Overlap:** NL-06, NL-03.
- **Suggested resolution:** replace the diagram by a transition table with the triggering operation for
  each pair.

#### TL-08 — `execution_state_changed_event` is said to report execution-summary changes but cannot report two of the summary's parts
- **Specs:** RUNTIME l.3509 ("reports execution-summary changes in committed order"), l.2459-2463 (the
  event carries `module`, `instance`, `execution`), l.2323-2330 (the summary also has `? failure`,
  `? selection` and `realization: "current" / "absent" / "unknown"`), l.3504 (the revision advances on
  intent, attempt and lifecycle-state changes only), l.611 (cleanup completion is not a lifecycle
  transition), l.613 (`start_module` is refused while cleanup is unresolved), l.3538 (`recover_module`
  requires that "cleanup of any previous realization is complete"), l.3563 (`retire_module` requires
  the same), l.2052-2056 (`execution_state` has `revision`, `intent` and an optional `intent_revision`),
  l.3511 ("Queries can resynchronize observation after missed events or uncertain request outcomes"),
  l.3789 ("retry accounting MUST survive orchestration restart and lost responses").
- **Issue:** a change of `realization` (cleanup completing while the state stays `error`) or of
  `selection` produces no event and no revision. The `inventory_changed` hints do not cover it:
  `module_record` has neither field. The state also carries no mark of an accepted attempt (l.2052-2056).
  After a lost `recover_module` response, orchestration has only the revision to compare (l.3511), and the
  revision advances for intent and state changes as well as for attempts (l.3504). A changed revision
  therefore does not show that the attempt was accepted, and the retry accounting that l.3789 requires
  across lost responses has nothing certain to count.
- **Impact:** cleanup completion is a precondition of three operations, so orchestration has to poll
  `get_execution_summary` to learn when it may start, recover or retire.
- **Overlap:** NO-02 (answered by inventory hints), NL-06.
- **Suggested resolution:** advance the execution revision and emit the event on `realization` and
  `selection` changes, and carry both in the event. Add to `execution_state` the revision at which the
  last execution attempt was accepted, so that a lost response can be settled.

#### TL-09 — Configuration summary for an instance without a binding: `state_revision` is required and undefined
- **Specs:** CONFIG §1 l.50 (`get_configuration_summary` is the only operation allowed without a
  binding), §9 l.405-406 (`state_revision: uint64` required), §3 l.89-90 (the revision exists "for each
  configurable module instance" and starts at zero "when it creates configuration state"), l.329 with
  l.176-177 (without a binding the summary omits `schema_commitment`, `current` and `staged`),
  l.251-253 (an existing instance cannot lose its binding, so the case is an instance whose declaration
  has none).
- **Issue:** for an instance whose declaration has no binding, the one permitted operation returns a
  required field that is defined only for configurable instances.
- **Impact:** the value a caller reads for such an instance differs between implementations.
- **Overlap:** none.
- **Suggested resolution:** define the revision as zero for an instance without a binding.

#### TL-10 — Fields and types that no prose gives meaning to
- **Specs:** RUNTIME l.2448-2452 (`apply_configuration_response.applied_value_revision`), l.2223-2226
  (`close_route_request.reason`), l.3486-3492 (the `close_route` prose), l.1901-1905 (the disclosure
  rule for `reason` values), l.3178-3180 (the uniqueness rule of `logos.runtime.route_id`), l.1922-1932
  (the object table of the supporting schema); PM l.1522-1523
  (`logos.package_manager.progress_phase`); CONFIG §8.
- **Issue:**
  - `apply_configuration_response.applied_value_revision` occurs nowhere else in the twelve files;
    CONFIG §8 gives the preconditions and the error mapping of the method, not what it returns.
  - `close_route_request.reason` is not mentioned in the `close_route` prose: whether it reaches the
    provider, the route record or audit is unstated. The disclosure rule for `reason` values applies to
    it and does not say where it goes.
  - `logos.package_manager.progress_phase` has five literals (`resolving`, `fetching`, `verifying`,
    `installing`, `removing`) that no prose defines or orders.
  - `logos.runtime.route_id` has a uniqueness rule and is the only identifier of the supporting schema
    absent from the object table.
- **Impact:** two implementations give these fields and literals different meanings, so a caller cannot
  rely on them.
- **Overlap:** none.
- **Suggested resolution:** one sentence of meaning for each field and literal, and a row for
  `route_id` in the object table.

### 3.3 The integrator documents against the specs

Two public documents tell integrators what the stack gives them. One is the documentation page
"Integrate Logos into your application" of logos-co/logos-docs, cited as `DOCS l.N`. The other is the
appendix "Integrating the Logos Technology Stack" of logos-co/rfp (PR 206), cited as `RFP l.N`. Together
they describe the product the specs are meant to enable. Every claim they make about the runtime, 35 in
all, was compared with the specs: 14 are supported, 16 are supported with a limit, 3 are not provided and
2 are contradicted. The comparison is in Appendix D. The eight items below state where the documents and
the specs disagree, and where a documented design rests on something the specs do not define.

#### TS-01 — The embedding application cannot call a module, and the specs describe an application-facing call surface in three places without defining it
- **Specs:** RUNTIME §13 l.3933-3936 (the Host Embedding API "is not a module contract and does not give
  the host a module-instance or consumer identity"), §13.2 l.3963-3970 (six operations: construct,
  register bindings, start, request shutdown, wait, destroy), l.3973-3974 (start "does not require every
  ordinary module in the deployment to be ready"), §13.3 l.4034-4036 (`configuration_format` is
  implementation-defined), l.4049 ("Registration alone MUST NOT create a module instance"), l.4069
  (registration only before start); Terminology l.138-140 ("Every consumer is a module instance"), §9
  l.1604, l.1609 ("One program may both host a Runtime instance and contain admitted module
  implementations"), §8 l.1391-1392; BCP §2 l.100-104. Against these: RUNTIME App A.1 l.4112-4131 (an
  "application driver" that "links one generated library and includes one generated facade header" and
  gets "outbound module calls" through "one app-facing API"), §5.2.1 l.1101-1102 (no-handle helpers
  that "route calls through the runtime's default binding for that module name"), and an undefined
  "runtime API" in normative sentences: l.923-924 ("Runtime APIs and runtime-host bindings may carry the
  selected contract explicitly or derive it from deployment metadata"), l.1738-1739 and l.1750
  ("runtime API error channel"), l.3081-3082 ("runtime API surface"), l.3006 and l.3469 ("the Runtime
  handle API").
- **What the specs provide:** protected activation of an application module, as a deployment
  requirement (BCP §5.4 l.384-390: "An activation request is protected deployment input, not a Runtime
  Control invocation or an authenticated module consumer"; "A complete-system deployment MUST realize
  the activated application through its bound Module Loader before application code invokes Logos
  contracts"; RUNTIME l.1606-1607, l.1815), and `get_self` (RUNTIME l.2553-2559), which needs a binding.
  Both confirm that an application takes part only as an admitted module. Neither mentions the Host
  Embedding API or a host that is itself the application, and the six host operations include none for
  activation or for obtaining a binding.
- **Issue:** DOCS l.132-141 and RFP l.435-448 describe an application that is not a module, starts the
  runtime and then calls modules and receives their events. Under the specs every call needs a consumer,
  the host is explicitly not one, and the Host Embedding API has no invoke, subscribe or binding-acquire
  operation. The only conforming shape is that the application registers a consumer-only module of its
  own and has it admitted; the specs allow that (RUNTIME l.1609) and say nothing else about it. What each
  implementation must then invent: (a) how the host declares that module instance, its `requires` and
  its permissions (inside the opaque `configuration_format`); (b) how host code obtains the instance's
  Runtime Control binding, which exists only as the `_MODULE_init` input (INTERFACE l.3628, l.3923) and
  so has to be passed back to the application through process globals; (c) how the host learns that its
  instance is `ready`, since start returns earlier and the host has no observation channel that is not
  itself a module call; (d) what the application does when an authorised module stops or retires that
  instance (INTERFACE l.2006; RUNTIME l.630 gives `NOT_READY` on a logically invalidated binding).
  App A.1 and §5.2.1 describe calls made by an application driver without saying which module instance
  is the consumer for them; that driver is also not a Loader-realized module, which BCP l.388 and l.289
  require. Today's stack has a non-module host caller as a first-class kind, so the specs take away a
  capability that applications have today.
- **Impact:** the Kotlin, Swift, Go, Dart and Rust host libraries of RFP deliverable 5 each bind one
  implementation's private convention; an application written against one Runtime's host library does
  not move to another. "Your own application code does not need to be implemented as a Logos module" is
  false as written.
- **Overlap:** RT-01 (declined: protected activation, "without a mandatory embedded Runtime or loopback
  transport"), SO-06 and SO-03 (declined), NP-04 (declined).
- **Suggested resolution:** in §13, define the host's participation in the vocabulary of BCP §5.4: the
  host supplies one statically registered consumer-only (or provider) module, admitted by protected
  activation, and may bind it to the orchestration role (RUNTIME l.187-190: "The orchestration role
  assigns no canonical module name and does not require a provider contract", which is exactly an
  application that drives lifecycle); add a host operation that returns that instance's Runtime Control
  binding once it is ready, or blocks until then, and state its lifetime against `stop_module`,
  `retire_module` and shutdown; give a minimal portable record for a statically registered module (name,
  binding, `requires`, requested permissions) even if its carrier stays implementation-defined. Reword
  App A.1 and §5.2.1 to name that instance as the consumer, and replace "runtime API" and "Runtime
  handle API" by the binding operations they mean (`materialize_route`).

#### TS-02 — A provider's contract set is fixed when it is built, so one generic client module cannot proxy "other module APIs after them"
- **Specs:** INTERFACE §2.6 l.1637-1638 ("The initialization input and returned context are instance
  state. They MUST NOT change the implementation name, provider call-surface descriptor, or exact
  contract set"), l.1710 (the call surface "MUST return the same bytes on every call for one native
  provider implementation binding"), l.1557-1563 (typed per-method functions and dispatch are both
  mandatory), §2.9.2 l.2115-2116 (the asynchronous provider surface "does not replace mandatory typed
  functions or `_MODULE_dispatch()`"); RUNTIME Terminology l.120-123 (a remote-module facade is routing
  state between Runtimes), l.1812; TRANSPORT §9.3 l.1385-1393 (other bindings are not defined).
- **Issue:** RFP l.871-873 intends one proxy module to cover a blockchain's API alongside an execution
  zone's, "and other module APIs after them", rather than one proxy per protocol. The server half is
  possible: it is a consumer making dynamic calls (subject to TS-03). The client half is a provider, and
  a provider cannot take its contract from configuration: the descriptor and the per-method symbols are
  fixed in the artifact. Each proxied contract set therefore needs its own generated and signed client
  artifact. The one provider whose contract does come from deployment input, the remote-module facade,
  is reserved to the Runtime and its own transport profiles. In today's stack the dispatch and the
  method list are computed at run time, which is what the RFP's design relies on.
- **Impact:** RFP deliverables 4 and 6 are one build per transport and per API, not one module per
  transport.
- **Overlap:** HC-07 (no response yet), TS-08.
- **Suggested resolution:** accept this and say so in the RFP; or define a provider form whose
  call-surface descriptor is supplied as accepted deployment input and which exports dispatch only (the
  relaxation TS-08 asks for, which has to cover all three provider surfaces).

#### TS-03 — No JSON (or text) projection of contract values for generic clients
- **Specs:** RUNTIME §4.1 l.821-833 (a binding MAY expose a generic `logos_route_call` "for callers that
  discover schemas at runtime"), §2.4 l.426-428, l.448-458; INTERFACE §4.4 l.3099 (deterministic CBOR
  only), §5.3 l.3937 (dynamic schema text may be used for "user presentation"), App A.6 l.4140-4148 (UI
  bindings are "derived views", details out of scope), §1.7 l.483 (choice arms are selected
  structurally), l.497-499 (a contract may carry an external encoding in `bstr` or `tstr`). In the
  twelve files the word JSON occurs only for the SLSA envelope (PM l.615-622) and in two sentences
  about what CDDL is.
- **Issue:** every client that is not generated code turns typed values into text and back: the
  JSON-RPC server and client module pair of RFP l.804-819, which is meant to carry "other module APIs
  after them" and whose two paths "must express the same semantics" (RFP l.875-879); a command-line
  tool; the JavaScript SDK (DOCS l.167); QML and web views. The projection has real choices: `bstr` as
  hex or base64; 64-bit integers above 2^53; an absent optional field versus `null`; tuples; and
  choices, where the JSON-to-CBOR direction needs the schema and a rule. Two independently written
  bridges for the same contract will not interoperate. The manifest has no defined text rendering
  either: only `manifest.cbor`, `manifest.cose` and `variants/` may appear at the archive root (PM
  l.906), and the owner's answer to PM-09 leaves human-readable inspection to "consumer tools".
- **Impact:** a JSON-RPC client module from one vendor cannot talk to a server module from another; a
  call recorded by one tool cannot be replayed by another.
- **Overlap:** ND-06, ND-01, ND-07 (all declined: no JSON type, no wide-integer type, no common error
  record).
- **Suggested resolution:** an informative annex in INTERFACE (or a small named profile) defining one
  JSON rendering of schema-typed values and its inverse under a given schema, stated to carry no
  commitment meaning: objects for maps, arrays for lists and tuples, base16 for `bstr`, numbers up to
  2^53-1 and decimal strings above, absent for absent, arm selection by the existing structural rules.

#### TS-04 — The remote profiles fix one authenticated connection per route and one per consumer for control; a session can be reused only by the same route
- **Specs:** TRANSPORT §8.4.1 l.1289-1290 ("One authenticated connection carries one such provider
  session ... The connection MUST close when that provider session ends"), l.1296-1298 (no session
  resumption, no early data), §8.4.2 l.1314-1316 (one QUIC connection, one session, no further
  application streams); RUNTIME l.2843-2848 ("A caller that requires another provider or route MUST
  establish another session"), §9 l.1801-1802 (a remote Runtime Control connection is used "only for
  that consumer"), l.925 (a route exposes one exact contract), l.784 (materialization "MAY reuse a live
  session bound to the same consumer, route, provider, and exact selected contract"), l.3477-3478
  (renewal leaves the live session on its old decision; a replacement session needs "its fresh
  ticket").
- **Issue:** between the same two enrolled Runtimes, every route of every consumer module is a separate
  TCP or QUIC connection with a full mutual TLS 1.3 handshake, and each consumer module needs its own
  control connection to establish or renew. Renewal and any session loss mean a control round trip plus
  another full handshake. DOCS l.222 says connection scale is left "to each deployment"; the profile
  leaves nothing to choose. The cost is per route and not per call: several asynchronous calls can be
  outstanding through one route handle (RUNTIME l.1363).
- **Impact:** a phone using three contract views of a home node holds three provider connections plus
  one control connection per consuming module; an operator serving many applications carries at least
  one connection per user per contract. QUIC's stream multiplexing is unused by rule.
- **Overlap:** NR-11 (resolved by the asynchronous call API), NR-06 (resolved: no live rebind), NR-08 and
  NR-07 (declined).
- **Suggested resolution:** either state the cost as an accepted property, or define a separately
  specified profile (RUNTIME l.3480 anticipates one for updating live sessions) with one authenticated
  Runtime-pair connection that carries several provider sessions (each redeeming its own ticket and
  bound to the same exporter value; one QUIC stream per session) and several consumers' control traffic.

#### TS-05 — Publisher-level trust is prohibited: every package name needs its own entry in protected trust input
- **Specs:** PM §4.1 l.407-413 (the trust input "MUST also bind each accepted signer to a non-empty set
  of exact package names"; it "MUST NOT use case folding, Unicode normalization, prefixes, wildcard
  patterns, or an authorization covering every package name"), l.437-438 ("Package material, catalog
  metadata, Storage content, and Nix metadata MUST NOT add, replace, or reactivate a package-signing
  trust anchor"), l.395 (the trust configuration, including "exact-name authorization", is under a
  monotonically ordered revision), §4.3 l.538 (the signer record "does not identify a publisher or
  assert current trust"), §15 l.1506-1513 (no method changes trust input).
- **Issue:** DOCS l.104 promises "Logos's own keys are trusted by default, users can add the publishers
  they trust", and DOCS l.105 an ecosystem where "other developers' modules can depend on yours". Under
  §4.1 a signer is never trusted as a publisher: it is trusted for an enumerated list of package names
  that lives in protected input. A user who trusts a publisher must re-approve each new package name
  that publisher ships, and each approval is a new protected trust revision; the default Logos anchor
  must list every Logos package by name and be re-issued when one is added; a third-party package
  cannot be installed on any device until that device's protected input names it, and neither the
  catalog nor the package may supply the name binding.
- **Impact:** the open catalogue the documents describe needs a per-device, per-package provisioning
  step that no specified operation performs; "add a publisher" cannot be offered as one action.
- **Overlap:** NI-06 and NP-10 (resolved: the verified signer is retained, and trust input has
  continuity rules), SO-03 (declined), HC-01.
- **Suggested resolution:** keep exact-name binding as the baseline, and define how the binding is
  extended without editing deployment files: a Package Manager (or Runtime Control) method, gated by a
  Capability Authority scope, that adds an exact package name to an accepted signer's set as a later
  trust revision (PM l.395-398), with the change audited; optionally a signer-signed name list that a
  deployment may accept for a signer it already trusts, with collision rules when two accepted signers
  claim one name.

#### TS-06 — A package does not carry its provider contracts in any declared way, so a contract can be read only from running code
- **Specs:** PM §4 l.265-273 (`module_declaration` carries `primary_contract`, `implements` and
  `requires` as commitments only), l.275-281 and l.329 (the one declared link from a module to a `schema`
  artifact is `configuration.schema_artifact`), l.318 (artifact kind `schema`), §9 l.1142-1147 ("If ...
  Package Manager can compute or obtain that contract's schema identity"), l.1149-1154 (commitments "do
  not contain the CDDL schema documents"; a package "may carry declared schema artifacts as ordinary
  hashed package material"), l.1116 (a manifest may declare zero modules), §15 l.1506-1513 (no method
  returns contract documents); INTERFACE §2.6 l.1679-1699 (the documents are inside the call-surface
  descriptor returned by the artifact's own code), §5.2 l.3873 ("The caller may construct this value
  from contract documents embedded in generated bindings or supplied with the application"); RUNTIME
  §2.4 l.418, l.448-458, §3.6 l.725-726 and SECURITY l.172-174 (loading a library to inspect it is not
  allowed).
- **Issue:** DOCS l.137 and l.229 have clients "generated from each module's contract" and say every
  module "publishes its contract as a CDDL schema". In the specs the documents that reproduce a contract
  root reach a consumer in two ways only, which INTERFACE l.3873 states: from a provider that has been
  realized, or out of band. A package may include `schema` artifacts, but no field says which artifact
  is the primary contract, which are implemented interfaces and which are supporting schemas, and
  nothing ties a manifest commitment to them. A developer who wants to generate a typed client for a
  module, a store page that wants to show a package's API, and the Package Manager's own
  `implements`-versus-primary check (PM l.1142-1144) all have no defined input before the code runs. An
  interface contract defined by one party and implemented by others has no distribution path at all (a
  package with zero modules and only `schema` artifacts is permitted, but nothing recognises it).
- **Impact:** typed-client generation depends on side channels per module; `requires` entries cannot be
  matched to candidate packages without installing and starting them; interface contracts spread by
  copy.
- **Overlap:** IF-10 (resolved: the sources of route construction input are listed), SO-10 (section 1),
  ND-09, NP-01 and SO-01 (declined).
- **Suggested resolution:** an optional `contracts` field on `module_declaration` (or a manifest-level
  table) mapping each declared commitment to the artifact ids of its document and of its interface and
  supporting documents, verified by recomputing the root at inspection; a Package Manager method that
  returns those documents for an installed or inspected package, as the handoff already does for the
  configuration schema (PM l.1399: "The handoff MUST contain the schema document and default value
  rather than their package artifact identifiers"); a statement that a module-less package of `schema`
  artifacts is the way to publish an interface contract.

#### TS-07 — Interchangeable providers: the module name and the document role are not part of a contract's identity (clarification, and what remains undefined)
- **Specs:** COMMITMENT §9.1 l.1188-1194 (the schema root object holds the commitment-model revision,
  the schema namespace, the declarations and the implemented-interface roots, and no module name or
  document role), §4 l.635-641 ("Schema identity uses schema namespaces and qualified schema definition
  names, not runtime module names"), §3.1 l.306-311 (role metadata "is not emitted as a schema
  declaration"); INTERFACE l.1718-1719 (the `primary` document's `_module` must equal the module's own
  name), l.322-325; RUNTIME l.917-919, l.2118-2124 (`establish_route` selects by `contract`, never by
  module name), l.1477-1482 ("This specification does not define an ordering among equivalent matching
  providers"), l.1472 ("deployment pinning"), l.1436-1437 ("Equal module names or contract commitments
  do not establish equal behavior, trusted publisher identity, or equivalent authority. Accepted
  provider selection and execution policy remain responsible for choosing an allowed implementation");
  CA l.164-178.
- **Issue:** RFP l.811-819 requires a client module that "implements the same IPC interface as the
  module it proxies" so that the two are interchangeable to callers. This works, and more simply than an
  interface contract: two modules with different `_module` names whose primary documents have the same
  namespace and declarations have the same schema root, so a route request for that contract matches
  either. A concrete document and an interface document with the same namespace and declarations also
  share a root. The specs say that equal commitments do not mean the same implementation (RUNTIME
  l.1436-1437) but do not state the property, and three things the RFP design needs remain undefined:
  which provider a `single` request gets when both are present (RUNTIME l.1482); how a deployment pins
  one ("Accepted provider selection" has no record, and a consumer can only name a provider by a
  Runtime-minted address); and how a policy tells the node from the proxy, since a
  `provider_access_scope` for the contract covers both unless `providers` is listed.
- **Impact:** the RFP's design is sound against the specs but rests on an unstated property; the same
  property means a module needs no name collision to stand in for another module's contract.
- **Overlap:** HC-01, NF-22 (declined: no universal role names or resolver), RT-04 (resolved for the
  choice of package per module name only).
- **Suggested resolution:** state the property in INTERFACE §1.2 and RUNTIME §3.3; define the
  provider-preference input for `single` selection as a protected record keyed by contract commitment
  and module name (or package identity), and say that without one a request matching several providers
  fails rather than picking arbitrarily, as `create_module` already does for declarations (RUNTIME
  l.3619: "If active policy does not select one accepted declaration, the request MUST fail").

#### TS-08 — Static registration from a managed language must still supply every per-method C symbol (addendum to HC-07)
- **Specs:** INTERFACE §2.6 l.1557-1563 ("Provider modules MUST expose both surfaces"), l.1754 (a direct
  ABI caller MAY call the per-method functions), §2.9.2 l.2115-2116; RUNTIME §13.3 l.4042-4045 ("The
  table MUST include every symbol required for the implementation, including schema-derived per-method
  symbols when applicable"), l.4051-4054 (a missing per-method symbol is detected at implementation
  binding, not at registration), §1.2 l.282-284.
- **Issue:** an application that serves calls from Kotlin, Swift, Go or JavaScript (RFP l.484-486:
  "Provider hosting ... This is the barrier") registers a binding whose table must contain, for every
  method, a C function with the canonical struct layouts of INTERFACE §2, although the natural bridge
  for those languages is the single dispatch entry point carrying CBOR. The typed functions must work,
  because a direct caller is allowed to use them. The optional asynchronous provider descriptor is a
  third surface and replaces neither.
- **Impact:** each language SDK must generate and compile per-method C trampolines for every contract;
  the "universal string and JSON interface" the RFP relies on today (RFP l.489-490) has no counterpart.
- **Overlap:** HC-07 (no response yet).
- **Suggested resolution:** let a binding or call-surface descriptor declare "dispatch only", in which
  case the per-method symbols are absent and every caller uses dispatch; say how that combines with
  `_MODULE_async_api()`.

### 3.4 Porting the existing module catalog

The modules of the current release catalog were read for what they need from the platform. The needs are
stated here with neutral roles (consumer C, provider P, a lower provider Q, a presentation module), because
what matters to the specification is the shape of a need and not which module has it. Twenty needs that
recur across the catalog are compared with the specs in Appendix E. The verdict words are `core gap` (Core
must define something), `profile` (the need is assigned to a platform, deployment or presentation profile
that does not exist yet), `contract` (the module can carry it in its own contract, at the stated cost) and
`policy` (a deployment policy or configuration matter).

The seven items below take more than a table row to state. Where the same module recurs, it keeps its
letter: C is a consumer, P a provider that C uses, Q a lower provider that P runs on, and R a provider that
holds keys. A and B stand for other modules and are local to one item.

#### TP-01 — A shared provider that its consumers create, configure and start
- **Need:** Consumer C creates a node inside provider P with C's own configuration. If P refuses because
  the node exists, C reads the node's state, starts it and records that it adopted a node which another
  module created. C's source notes that P's lifecycle should belong to the host application and not to a
  consumer. P in turn creates and configures a lower provider Q, laying its own settings over the
  operator's configuration, because Q replaces its options wholesale on each create call. Three further
  consumers operate on the one session that a presentation module opened in provider R. Another
  presentation module stops and destroys a node it finds running.
- **In the specs:** application-level setup through ordinary schema methods is sanctioned (RUNTIME
  l.647-648), so a create method that takes a configuration and a start method can stay contract methods.
  Core configuration is the other route and has the opposite shape: one complete value per instance with
  "no field patch, implicit merge, or partially applied configuration value" (CONFIG l.52-53; "No source
  implicitly merges with another source", l.132), never starting or stopping anything (l.56), and without
  credentials (l.57; the node configurations of two providers in the catalog contain a private key). A
  provider can identify its caller (INTERFACE l.2181-2182), so a rule that the first caller owns the node
  can be enforced by the provider's own contract instead of being a race. Core does not arbitrate between
  consumers, and nothing tells a consumer which configuration the provider runs with. Key parameters can
  be marked `_sensitive` (INTERFACE l.213-214).
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
  (RUNTIME l.1249-1250) and "A callee MUST NOT require an Event message as a reply path for a method
  invocation" (TRANSPORT l.836-837). P's pattern is the one the second forbids, in the reverse direction:
  the request is the event and the reply is the method. Three shapes conform:
  1. An inversion of roles. The provider declares `requires` on an interface contract that the handler
     implements, and calls it. P already does this where the handler runs in P's own process.
  2. A long-poll issued as a prepared asynchronous call with a timeout and cancellation (INTERFACE l.2059,
     l.2067). The prepared call does not occupy its route handle (RUNTIME l.1363-1364). This fits Q's
     accept method with its timeout as it is. Issued through the synchronous `call`, the long-poll
     occupies its handle until it returns, because a caller must serialise operations on one route handle
     (INTERFACE l.1980).
  3. A work-item resource owned by the contract and observed through a watch method. The handler keeps a
     watch invocation open, the provider publishes invocation-scoped notifications that only that
     handler's path receives (RUNTIME l.1258-1260), and the handler completes each item through a method
     (TRANSPORT l.851-853). This removes the rule that the first listener to answer wins. Whether this
     shape is itself a request/reply flow through events in the sense of RUNTIME l.1250 is open. Every
     watch that the specs themselves define is notification-only (CA l.946-954; PM l.1712). A notification
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
  persistent state requires an explicit deployment or policy rule" (RUNTIME l.1451-1452). A `state_dir`
  "does not imply authority to access any host path or another module instance's state" (l.1465). Sharing
  is named only as a facility that a permission profile would define (CA l.400), and no such profile
  exists. The specs state the consequence directly: "A filesystem path does not grant access or guarantee
  visibility in another module's realization" (RUNTIME l.3910) and "Co-location alone does not establish a
  shared filesystem namespace" (l.3917), which is the assumption the fixed home-directory path rests on.
  Methods that take paths are allowed, with a duty: the contract "MUST define whose namespace it addresses
  and the applicable failure when that namespace or access is unavailable" (l.3918). The Credential Store
  (BCP l.199) is for credentials in deployment-assigned slots and gives nothing for a shared file.
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
  metrics-provider interface", l.227). The collector declares `requires` on a metrics interface with
  cardinality `all-runtime-visible` and gets one route per visible provider (RUNTIME l.1484-1487). Each
  `route_record` carries the provider's `module` name (l.2107), so the label needs no extra observation
  grant. Three things do not carry over. Floats are reserved (INTERFACE l.492), and a float anywhere in a
  transported payload "is a Transport validation failure" (INTERFACE l.3139) that closes the connection
  (TRANSPORT l.413-414), not a schema rejection, so samples travel as exposition text or decimal strings
  and must never reach the wire as floats. Conformance is declared, not structural ("This revision does not
  define ... structural duck typing", INTERFACE l.190-191), so every source module must implement the
  interface by exact reference: in `_implements` of its primary document, or in its module binding when it
  has none (INTERFACE l.604, l.722). And "either method" becomes two interfaces.
- **Verdict:** `contract`. The operator's module list becomes the provider constraint of the `discover`
  decision (`policy`).
- **See:** ND-01, IF-01, NL-12.

#### TP-05 — A dependency between two modules that runs over loopback HTTP
- **Need:** Module A reads finalised state from the node that module B runs, through a loopback HTTP
  address in A's configuration, while A's package declares no dependencies. Another module talks plain
  HTTP to a separately run service.
- **In the specs:** such a dependency is invisible to the Runtime: no `requires`, no ordering constraint
  (ordering exists only as a deployment-supplied constraint, RUNTIME l.746), no route authority, no
  commitment or audit. It works only while both modules share a network namespace, which `sandbox`,
  `container` and remote placement do not guarantee. The integrator SDK documents describe the intended
  shape: a node depends on another node as a module dependency, and a client reaches its node only through
  the node's interface. The only spec hook for the loopback shape is a profile-defined network permission
  (CA l.398), and the owner's response to SO-05 is that no registry of such permissions is added.
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
  not anything retains it (RUNTIME l.1762-1764, l.843; INTERFACE l.3832; SECURITY l.504-505). The only
  latitude is the optimisation rule, which may not bypass validation (RUNTIME l.3194), and no profile that
  would skip the computation is assigned (BCP l.342). A stream binding accepts at least 16 MiB, and a
  sender uses 16 MiB unless a larger limit is separately established (TRANSPORT l.380-384). The failure is
  defined: an oversized Request "MUST fail its local invocation with `MODULE_ERROR`", an oversized Response
  becomes a `response-err`, and an oversized Event closes the subscriber's connection when its publication
  boundary cannot report the failure (l.385-389), which is the case for the ordinary publish callback
  (INTERFACE l.3618). "These stream limits do not impose a new direct-mode payload limit" (TRANSPORT
  l.393). So a 64 MiB message crosses a direct route, and a transported one only where the deployment
  configures a larger limit. One point is open. The same call with a 20 MiB value succeeds on a direct
  route and fails with `MODULE_ERROR` on a transported one. INTERFACE l.60-65 says the execution boundary
  "MUST NOT change ... the meaning of success and error results", and TRANSPORT l.381 limits what a
  contract may require, not what a value may be. A contract with an unbounded `bstr` therefore behaves
  differently by placement. Bounding such fields in the schema (`bstr .size`) is the port's way out; the
  specs could say that a contract whose values can exceed the limit must bound them.
- **Verdict:** not a defect, but a cost the port must measure for the per-message and large-message data
  paths; `contract` for the chunking (SO-09). The specs could assign a profile that skips commitment
  computation on a direct route when no policy requires retention; none is assigned.
- **See:** ND-03, SO-09, NE-05.

#### TP-07 — Package dependency ranges and exact pins
- **Need:** Consumer C requires provider P at an open lower bound (a given version or any later one). A
  presentation module requires provider R at an open lower bound that only the newer of two shipped
  versions of R satisfies. Three consumers pin R exactly at the older version, while the same release set
  ships the newer one.
- **In the specs:** a requirement is `exact` or `compatible`, the latter a caret range (PM l.300,
  l.1225-1228); an open lower bound has no form. Two closures may install two versions of one package
  (l.1325-1326), which here means two declarations of R's module name. Which one `create_module` picks is
  a matter of protected deployment policy (RT-04): policy must select one declaration and pin the exact
  package and version, the request carries no selector, and creation fails when policy does not select
  (RUNTIME l.3614-3622; BCP l.367). The shared session of TP-01 does not survive this: routes select exact
  contracts (RUNTIME l.3140), so consumers built against the older and the newer contract of R need two
  instances of R unless the two contract roots are identical.
- **Verdict:** `policy` for the ranges (use `compatible`) and for the pin of R's declaration. The exact
  pins have to be relaxed before the port, or the set carries two packages of R and two sessions.
- **See:** PM-15, RT-04, NF-17.

### 3.5 Editorial

#### TF-06 — Editorial
- RUNTIME §2.2 l.366: "the applicable ABI caller MUST invoke `logos_<module-C>_MODULE_name()` and return
  the expected module name" has lost its subject; LOADER l.392 has the intended rule ("require
  `logos_<module-C>_MODULE_name()` to return `descriptor.module`").
- RUNTIME l.3006, l.3469: "the Runtime handle API" is the `materialize_route` operation, which the same
  specification names at l.763 and l.2965 (see TS-01 for the wider "runtime API" wording).
- INTERFACE §1.8, the complete example (l.571-577, l.583-591): `upload_url` answers `{ accepted: bool }`
  and the outcome arrives as `upload_done_event = { cid }`, with a `session` in the progress event that
  the response never returned. That is an acknowledgement-plus-broadcast shape, which the specs make
  unnecessary elsewhere: a delayed result needs no "acknowledgement method, a job identifier or an event
  subscription" (TRANSPORT l.842-844), and "When concurrent invocations require correlation, the module
  contract MUST define enough information to distinguish their events before publication can begin"
  (RUNTIME l.1271). Two concurrent uploads cannot be told apart under the example contract. It is the
  first contract a reader copies.
- RUNTIME l.3128-3129: see NR-04 in section 1.
- "A module binding identifies one runtime module name, its optional primary document, and its
  implemented interface set" (INTERFACE l.604), so a provider can implement interfaces without having a
  primary contract. Three passages do not fit that:
  - INTERFACE l.85 says each CDDL-authored concrete module "MUST have a single `.cddl` file that
    contains the canonical CDDL representation of its primary module contract", and RUNTIME l.84 reads
    as if interfaces hang off a primary ("one primary concrete contract with zero or more exact
    implemented interface contracts").
  - The binding has no authored form on the CDDL side ("no additional schema document, serialized
    format, or authored sidecar file is required", INTERFACE l.2625). A CDDL-first interface-only
    provider therefore states its implemented set only to its tool, the descriptor and the manifest.
  - A types-only primary is carried in a `provider-contract-schema` entry although INTERFACE l.1545
    says it is not a provider contract.
- Four conditions in CONFIG presuppose that an instance's accepted binding can differ from the one its
  records or realization were created under, which CONFIG l.251-252 excludes ("An upgrade that changes
  or removes the configuration-schema binding or changes the live-reconfiguration declaration MUST
  establish a new module instance under the replacement declaration"): l.38 ("behavior when an accepted
  configuration schema changes"), l.145 ("A retained record under a different configuration-schema
  commitment"), l.215 ("both its accepted binding and the binding used to initialize the current
  realization"), l.296 (the `VERSION_MISMATCH` row for a binding, staged record and realization that
  disagree). They are unreachable rather than contradictory; a sentence saying when they can arise
  (restoration of protected state, for example) would settle it.
- RUNTIME l.301 reserves `_call_` and `_publish_` in module names as "separators in schema-derived
  method symbols and generated event-publication helper symbols", and l.318 says the name is used to
  derive C symbol prefixes of the form `logos_<name>_*`. INTERFACE has neither separator. A method symbol
  is `logos_<module-C>_CALL_<namespace>_<Method>` (l.737), with an upper-case separator, and `<module-C>`
  is the projection of l.696-699, which differs from the name when the name has a doubled or trailing
  underscore. The names of event-publication helpers are "implementation-defined" (l.886); the one name
  with `_publish_` that INTERFACE prints is in an informative appendix (l.4084), where "The helper name
  is illustrative" (l.4091). RUNTIME l.301 and l.318 should refer to INTERFACE §2.1 or be brought into
  line with it.
- COMMITMENT l.1409-1410 says "The empty path `[]` is valid when the named declaration body is itself a
  leaf schema node", while l.569 says "An empty path always uses the named declaration's schema subtree
  root, including when its body is a primitive, literal or reference node". Under l.569 no value node
  uses a leaf payload with an empty path; one sentence should say what l.1409-1410 is for.
- INTERFACE §3.9.3 (l.2877-2930) recurses only through optional by-value fields, so no conformance case
  shows the forward typedef that l.1077 requires for an aggregate named through a variable-length list.
- RUNTIME uses "startup timeout" (l.1162) for what l.664 calls the "startup deadline", and "active grace
  period" (l.3857) beside the drain deadlines of l.3835. One term for each would help.
- TRANSPORT l.1180 lists "Reject non-deterministic envelope CBOR", while INTERFACE l.3138 says that
  Transport deterministic-CBOR validation "includes the embedded payload maps".
- RUNTIME l.1225-1227 says an event that cannot be validated is not delivered, and "Because
  `logos_publish_fn` has no result channel, Runtime records that failure as an implementation diagnostic
  and drops the event". TRANSPORT l.389 gives an oversized Event a different outcome when its boundary
  cannot report failure: the sender closes the affected connection. The two rules can be read as
  conflicting for the ordinary publish callback. One sentence in RUNTIME saying that the drop covers
  validation failures, and that TRANSPORT l.388-389 governs size, would remove the doubt (see also
  TP-06 and HC-10).
- RUNTIME l.888 says that for an engine system-service binding the caller context identifies the invoking
  Runtime "and the protected system-service kind". The caller view has only a two-valued `kind`
  (`LOGOS_CALLER_MODULE` or `LOGOS_CALLER_SYSTEM_SERVICE`, INTERFACE l.3505-3506, l.3519-3523). If
  l.888 means which system service is calling, the view has no field for it; if it means the caller
  kind, saying so would remove the doubt.
- INTERFACE §2.4 rule 8 (l.1280-1283) says "Unbounded and ranged `bstr` fields expand to adjacent
  pointer-and-length parameters" and spells out an output form only for the exact-size case ("its
  caller-allocated output uses `uint8_t (*out_<name>)[N]`"). Rule 6 gives the text output ("An
  unconstrained `tstr` response field uses `const char** out_<name>`", l.1275) and rule 9 the list output
  ("Its output uses adjacent `<type>** out_<name>` and `size_t* out_<name>_count` parameters", l.1285).
  The byte-string output is left to analogy, including whether the pointee is `const` and what the
  length parameter is called, although l.641 requires any two implementations to produce the same
  parameter types. One sentence giving `const uint8_t** out_<name>` with `size_t* out_<name>_len`, and
  the constrained typedef for a ranged field, would close it.
- `TIMEOUT` has one assigned producer: "expiration of the caller-selected duration produces `TIMEOUT`"
  (INTERFACE l.2067), for a prepared call. "Applicable policy, route lifetime and execution-envelope
  failure may still end delivery earlier" (l.2062), and RUNTIME l.3226-3227 leaves "In-flight call
  behavior, timeout policy, idle expiry, and retry policy" to the profile or implementation. No sentence
  says which code a call returns when such a policy deadline ends it; that includes a synchronous `call`,
  which takes no timeout.
- TRANSPORT l.989 gives the outcome of "A new Request processed during termination". A Subscribe or an
  Unsubscribe processed in the same window still needs its one SubscriptionResult (l.725), and what it
  carries is left to the general rules: `NOT_AUTHORISED` for the Subscribe (l.735-736), and for an
  Unsubscribe of a subscription that the termination has already ended, `INVALID_PARAMS` under l.748 ("An
  Unsubscribe naming no active subscription"), which the caller cannot tell from a mistake of its own. A
  sentence beside l.989 would settle both.
- PM l.910 ("A manifest variant with no descendant entry MUST have an explicit variant-directory entry")
  describes a variant directory without files. l.766 requires every variant to declare at least one
  artifact, and l.965 says "Every declared artifact path MUST identify one regular file", so the case
  cannot occur unless l.964-965 bind only the selected variant, as l.963 ("Artifact paths are relative to
  the selected variant directory") and l.1100 ("a required artifact is missing from the selected variant
  or realized output") suggest. If an archive may omit the files of variants it does not serve, saying so
  would also answer part of NP-12; if not, l.910 has no case.
- BCP §5.4 l.398-399 places two requirements on "the non-production mechanisms identified in
  LOGOS-MODULE-SECURITY-CONSIDERATIONS Section 13". That identification is one bullet (SECURITY l.532) in
  a document that says of itself "This document is informational" (l.18). Of the four mechanisms the
  bullet names, only the transport test hooks are defined (TRANSPORT §8.5); "relaxed debugging
  entitlements" and "unknown-artifact analysis" appear nowhere else, and a development trust anchor
  enters "through the same protected trust-input path" as any other (PM l.443-444). When a deployment
  owes the non-production designation of BCP l.399 is therefore left to its own judgement. Naming the
  mechanisms in BCP §5.4 would fix both points.
- RUNTIME l.1824: "Concurrent invocations from the same or different consumers MUST NOT share consumer
  identity, authority decisions, or request-key scope." Two invocations by one consumer have the same
  consumer identity, and a `create_module` request key is scoped "to this method, the authenticated
  consumer, and the Runtime instance" (l.3627; l.3168 likewise for route operations), which l.3631
  relies on ("Concurrent requests with the same key MUST NOT create multiple instances"). The sentence
  presumably means that each invocation is authenticated and authorized on its own, which l.1823 says.
- INTERFACE l.108 and COMMITMENT l.678 call the construction input "ordinary RFC 8610 CDDL documents",
  and INTERFACE l.505-506 names RFC 8610 among what decides "whether source text is a valid Logos schema
  document". The answer to CM-11 put the string-literal grammar of RFC 9682 Section 2 into cdCDDLe
  l.127 only. INTERFACE and COMMITMENT do not cite RFC 9682, so which grammar decides the validity of a
  string literal in a schema document depends on which specification is read.
- INTERFACE l.3719-3726: `prepare_call` takes `const logos_async_options_t* options`. l.3906 and l.3911
  cover a wrong version or extent and "Malformed callback or option input"; whether a null `options`
  pointer is malformed or selects the defaults (no timeout) is not said.
- INTERFACE l.1454-1457 defines self-unsubscription by the caller ("If a handler invokes the route
  `unsubscribe` operation for its own subscription through the same route handle") and states its effect
  by the stack ("MUST NOT wait for handler frames already active on the calling thread"). l.1504
  likewise forbids release "from an event or terminal callback for that handle". Direct publication is a
  re-entrancy boundary (l.1969), so a module can reach `unsubscribe` or `release` from code that is not
  the handler, such as a provider method entered while the handler's frame is still on that thread's
  stack. Read narrowly, that unsubscription is an external one and waits until "every active handler
  invocation has returned" (l.1448), including the frame beneath it. Defining both rules by a handler
  frame of that subscription, or of that handle, being active on the calling thread would remove the
  doubt.
- INTERFACE l.1428 has `subscribe` "write an identifier scoped to that route into
  `*out_subscription_id`", while a subscription ends with the handle that made it ("Releasing those
  handles deactivates their remaining route subscriptions", l.2005; "Release deactivates every remaining
  subscription", l.3897). Whether an identifier obtained through one handle may be given to `unsubscribe`
  through another handle of the same route is not said. If it may, a handler that follows l.1984-1985
  ("Every other operation initiated by a handler MUST use a distinct route handle or wait until the
  handler returns") and unsubscribes itself through a second handle makes an external unsubscription
  that waits for its own frame. Saying that a subscription is operated only through the handle that
  created it would settle it.
- INTERFACE l.2193-2195, on the invocation context's `publish`: "A valid event outside the selected
  contract or permitted event scope produces `NOT_AUTHORISED`" and "A known authority failure produces
  `NOT_AUTHORISED`; otherwise a closed invocation destination produces `NOT_READY`". "permitted event
  scope" is not a defined term, and a route has two event lists (RUNTIME l.3014-3015). Whose authority
  failure is meant is not said either. Presumably the scope is the route's `publish_events` and the
  failure is one of the publisher's own authority: a delivery refused because the subscriber lacks
  authority, if reported, would tell the provider a fact about the consumer. The order between
  `INVALID_PARAMS` for a malformed payload (l.2194) and `NOT_READY` for a closed destination is also
  left open (see TF-18).
- RUNTIME l.372 says what the absence of the provider's asynchronous descriptor selects ("Absence or a
  null descriptor selects the synchronous provider ABI without removing consumer asynchronous-call
  support"). No sentence says that a valid descriptor is used. A Runtime may "adapt that ABI using
  implementation-owned scheduling" (INTERFACE l.2016), and whether it may do so for a provider that
  exports `submit` is left to inference. Such a provider exports it to avoid holding a thread for each
  call, or to receive `request_cancel` (INTERFACE l.2144), and gets neither from a Runtime that ignores
  the descriptor.
- RUNTIME l.2541 gives a new instance "an empty permission array, status `applied`, and no failure", and
  l.2549 says "`applied` means the saved settings are enforced". With empty settings every permission is
  denied (l.2538). For a direct native realization nothing can enforce that denial: "Runtime MUST NOT
  claim containment against code that can access Runtime memory or unrestricted process resources" (CA
  l.366). l.2545 says that the initial `applied` state "does not grant execution or operating-system
  access", which is less than saying it is enforced. A sentence saying what `applied` asserts for a
  realization with no containment mechanism would remove the doubt.
- TRANSPORT l.418-419: an endpoint that has not completed its part of the Hello exchange accepts only
  Hello or ProtocolError, and "A wrong-direction message or an ordinary message received before that point
  MUST produce ProtocolError `INVALID_PARAMS`". A peer may write its Hello and its first Request back to
  back. The Request is then received before the receiver has finished the Hello and is processed after it,
  since "Messages on a single stream connection are processed in order" (l.397). Whether "received before
  that point" is judged by arrival or by processing order is left to inference. Saying that it is
  processing order would settle it.
- INTERFACE l.397: "If active policy requires retaining a marked payload's value commitment, Runtime MUST
  reject the invocation before dispatch rather than retain it or omit the policy requirement". The
  rejection has no code.
- CA l.1192-1194: a `call` audit record uses the `failure` outcome when "a required value was not produced
  or could not be committed", and "A successful call record MUST contain non-empty `commitments`". When
  every required value was committed and the provider then returns an error, for example when only the
  request commitment is required, whether the outcome is `success` or `failure` is not said.
- A Runtime instance is "composed of a Runtime engine and an orchestration module" (RUNTIME l.72), and the
  orchestration module is an ordinary module that the deployment binds ("Deployment MUST bind the
  orchestration role to a local module instance owned by that Runtime", l.187). RUNTIME places
  requirements on each, for example l.3786 ("The orchestration module MUST evaluate the active restart
  policy and schedule permitted recovery through `recover_module`") and l.3795 ("The Runtime engine MUST
  detect realization failure, mark the instance as `error`, fail its routes, and arrange cleanup through
  the mechanism that established the realization"). BCP §5.1 knows two claims: conformance "to an
  individual Core specification" (l.280) and conformance to the BCP as a complete system (l.287). An
  implementation that supplies the engine and leaves the orchestration module to the deployment fits
  neither, and the specs name no claim for the engine alone. Saying which requirements of RUNTIME bind the
  engine and which bind the orchestration module, and that the first set can be claimed by itself, would
  settle it.

---

## Appendix A — Earlier items resolved by the current specs

Every item of the two earlier audits that the current text settles, with the rule that settles it. Items
NF-01 to NF-25 were corrections or additions to other items; the item they refer to is named in
parentheses. NF-25 made no point about the spec text and is left out. ND-11, ND-13 and ND-14 are settled
by the text although they have no response; their rows say so.

| Item | Subject | Outcome |
|---|---|---|
| C-01 | Whether an unqualified common-schema name such as `error_code` is read as `logos.error_code` or rejected. | COMMITMENT l.706: "Common schema references in the normative construction input MUST use qualified names in the `logos` namespace." A local-namespace shorthand stays non-normative tool input (BCP l.458-459). |
| C-02 | Whether a declaration may have more than one name segment after the schema namespace, which the C mapping cannot round-trip. | COMMITMENT l.319: every local declaration name is the primary schema namespace, a dot and exactly one identifier segment. Dotted namespaces remain valid and project with `_NS_` (INTERFACE l.686). |
| C-03 | Whether the C-to-CDDL reverse mapping is required for INTERFACE conformance, given that BCP calls code generation optional. | INTERFACE l.23-24: an implementation of the bidirectional mapping supports both directions; a module implementation need not implement the authoring mappings, only conforming artifacts and encoding. BCP l.482-483 agrees. No separate conformance section was added. |
| C-04 | A generator could omit a tagged choice's tag member, while generated headers have to be identical across implementations. | INTERFACE l.1215: "The canonical C representation MUST retain a required literal tag field as a writable member of its map struct." Encoders still emit the tag field in the CBOR map (l.1216). |
| C-05 | The typed call helper in the RUNTIME example was named differently from the one in the INTERFACE appendix. | Both examples now use `logos_storage_invoke_exists` (RUNTIME l.809; INTERFACE l.4110), and INTERFACE l.4105 says such helper names are implementation-defined. |
| C-06 | RUNTIME derived one socket path per module name, while TRANSPORT requires a directory per instance; path length limits were ignored. | RUNTIME l.316-317: socket names are derived inside the per-instance directory of TRANSPORT §8.2 (l.1118-1119); the concrete pathname is implementation-defined and subject to the host's Unix-domain socket pathname limit. |
| C-07 | Whether module declarations may share artifacts, which error an ordering violation returns, and which error wins when several apply. | PM l.335 and l.1088: schema and default artifacts may be shared, an implementation artifact may not. Ordering or uniqueness violations are `invalid-package` (l.358). No precedence is fixed: the first detected failure may be returned (l.1070). |
| C-08 | The only Loader error for refusing a weaker substitute, `unsupported-strategy`, was defined as permission to try another strategy. | LOADER l.628: an advertised strategy whose required security or deployment controls cannot be established fails with `realization-failed`. `unsupported-strategy` is only for an unadvertised strategy or hosted placement (l.377). |
| C-12 | Runtime conformance needs call-audit and call-evidence record types defined by the higher-layer Capability Authority specification, against the stated layer direction. | BCP §1.1 lists the dependency as an explicit exception (l.86) that needs no Capability Authority provider or module calls (l.89). RUNTIME now cites the Capability Authority specification normatively (l.4307). |
| GN-01 | Only one of the twelve specifications cited BCP 14, so the force of uppercase and lowercase keywords was undefined. | Every specification now states that uppercase keywords follow BCP 14 and that lowercase forms keep their ordinary English meaning (for example TRANSPORT l.61-62 and SECURITY l.24-25). |
| CM-01 | Which declaration's identity a value carries when its type is reached through a chain of local aliases. | COMMITMENT l.1114-1116: the one-hop rule repeats to the terminal declaration; the referring location keeps its identity, the child carries the terminal declaration's, and intermediate aliases add no nodes. Vector in Appendix B.1 (l.1990). |
| CM-02 | Whether hash payloads below an imported reference carry the importing schema's root or the referenced schema's root. | HASH l.709-712: the reference payload keeps the importing document's root; its child and descendants use the referenced document's root; local references do not change context. Verifier checks at l.1239-1242, vectors in Appendix B.4 (l.1442). |
| CM-03 | Whether a schema node may reference the common callable declarations `logos.schema_request` and `logos.schema_response`. | COMMITMENT l.667: "An imported reference MUST target a named type declaration." The callable declarations of the common schema therefore cannot be used as type references. |
| CM-04 | What a verified-view path that ends at a map field or a tuple position discloses. | HASH l.1150-1152: a path ending at a present field, list index or tuple position discloses the contained normalized value; the field or tuple-element payload appears in the proof material. |
| CM-05 | Whether a semantic path must contain a choice-arm segment to pass through a choice value. | COMMITMENT l.1592-1594: continuing through a choice requires a `choice-arm` segment equal to the selected canonical arm index; a path that ends at the choice selects the complete choice value. |
| CM-06 | Whether choice-arm selection counts only literals on the tested value or every literal nested inside an arm. | COMMITMENT l.462-465: literals are collected only at the tested value or the selected field, following references and choice arms, never descending into map fields, list elements or tuple positions. Examples at l.503-504. |
| CM-07 | Whether a list whose element schema is a Boolean or integer literal is a packable scalar list. | HASH l.168-169: a packable list has "a primitive or literal element schema with a packable scalar kind"; `[* true]`, `[* 5]` and `[* -5]` are given as examples. |
| CM-08 | Where the verifier of a verified view obtains the schema it checks the view against. | HASH l.1214-1216: the verifier receives the schema construction input and its dependency documents separately from the view, validates them and computes the roots it compares; validated results may be reused. |
| CM-09 | The `logos.schema.reference` hash domain is defined but no object in the specifications uses it. | HASH l.610-612: the domain hashes a standalone `schema-import` pair, takes no part in schema or value commitments or verified views in this revision, and cannot stand in for a root or for the pair. |
| CM-10 | Whether `0*` and `*1`, spellings equivalent to the supported `*` and `?` occurrences, are rejected or normalized. | cdCDDLe l.178-179: occurrence indicators with explicit numeric bounds are rejected even when equivalent to a supported form, including `0*` in arrays and `*1` in maps. |
| CM-11 | Which CDDL string-escape grammar applies, RFC 8610 or its RFC 9682 update. | cdCDDLe l.127: text-string and byte-string literals follow RFC 9682 Section 2; the rest of the supported subset follows RFC 8610 (l.126). |
| CM-12 | Whether a range bound may be a named reference instead of an integer literal. | cdCDDLe l.181-182: range bounds, including those in `.size` controllers, are integer literals written directly in the source; named references as bounds are rejected. |
| CM-13 | The decoder's rejection list did not include a choice nested directly inside another choice. | cdCDDLe l.608: "A `cdCDDLe` decoder MUST reject a choice node that has another choice node as a direct alternative." |
| CM-14 | Whether prelude, common and supporting definitions are merged into a schema's cdCDDLe document or stay references. | COMMITMENT l.679-681: the document node contains exactly the document's own rules; the prelude and other documents are not merged; references to prelude aliases and external named types stay type-reference nodes. |
| IF-01 | Whether a float inside `params`, `result` or `data` is a Transport profile violation or a schema mismatch. | A float at any depth violates the deterministic profile (INTERFACE l.3109). It is a Transport validation failure, not deferred to schema validation (INTERFACE l.3139): ProtocolError `INVALID_PARAMS`, then close (TRANSPORT l.410-414). |
| IF-02 | No bound on value nesting depth, and no error for a payload that exceeds an implementation's limit. | Implementations enforce a configurable payload depth limit of at least 128 (INTERFACE l.3150). Dispatch rejects with `INVALID_PARAMS` without detail (INTERFACE l.3157). Transport sends ProtocolError `INVALID_PARAMS` without `detail` and closes (TRANSPORT l.408-415). |
| IF-03 | C representation of inline tuples, lists and byte strings used as choice arms or list elements. | In tuple positions, list elements and choice arms, each is one aggregate value with the named-aggregate layout (INTERFACE l.1033-1038). Its name comes from the path steps and tag families at INTERFACE l.778-784 and l.803-805. |
| IF-04 | C representation of an event whose body is a choice of maps. | Such an event uses the ordinary choice representation with its `_CHOICE` tag and no outer wrapper (INTERFACE l.1395-1397). The reverse mapping reconstructs it at INTERFACE l.2575. |
| IF-05 | Exact spelling of generated literal macros, on which generated header content depends. | Generated spellings are fixed: `true` or `false`, `UINT64_C(n)`, `(-INT64_C(n))`, one minimum-`int64` expression and one string form with octal escapes (INTERFACE l.1087-1093). Accepted handwritten forms are listed at INTERFACE l.2537-2569. |
| IF-06 | Position of the `has_` presence flag for an optional inline tuple field. | One `bool has_x` immediately precedes the first expanded member `x_0` and governs the whole tuple group (INTERFACE l.1014-1016). The reverse mapping enforces this at INTERFACE l.2510-2512. |
| IF-07 | Allocation unit and free order for recursive typed response outputs. | One response owner governs all backing storage of a typed response, including nested and recursive values. The caller clears the owner and frees no individual pointer (INTERFACE l.1835-1837). |
| IF-08 | Which function a consumer calls to free outputs decoded by a typed route call helper. | A generated call helper returns a response owner for its decoded storage and comes with a matching typed cleanup helper (INTERFACE l.1908-1922). Helper names are implementation-defined (INTERFACE l.886). INTERFACE l.4123-4138 shows the pair. |
| IF-09 | One module's method symbol could have the same C name as another module's lifecycle symbol. | Lifecycle symbols use `logos_<module-C>_MODULE_<operation>` and method symbols `logos_<module-C>_CALL_<namespace>_<Method>` (INTERFACE l.703, l.736-737). Module names and schema atoms are lowercase (RUNTIME l.299, INTERFACE l.791), so the families cannot coincide. |
| IF-10 | Where a consumer obtains the `schema_cbor` input that `materialize_route` requires. | The sources are named: documents embedded in generated bindings or supplied with the application, a projected `describe_provider` response, or an earlier `logos.schema` response (INTERFACE l.3873-3875). No `logos.schema` call is needed first (INTERFACE l.3876). |
| IF-11 | Relative order of macros, typedefs, lifecycle symbols and provider declarations in generated headers. | The placement of independent declarations is not part of the canonical mapping (INTERFACE l.893) and may differ between implementations (INTERFACE l.642). Only declaration before use is required (INTERFACE l.891). |
| EC-05 | Error code for a call through a route handle whose route is closed, failed, revoked or expired. | Withdrawn or expired authority gives `NOT_AUTHORISED`; explicit closure or readiness loss gives `NOT_READY`; authorization takes precedence (RUNTIME l.1343-1347). A transport failure that hides the result stays `TRANSPORT_ERROR` (RUNTIME l.1350). |
| EC-06 | Error code for a new call into a stopping provider or through an invalidated Runtime Control binding. | Both return `NOT_READY` while the binding storage remains valid (RUNTIME l.630). Known authorization failures keep their precedence (RUNTIME l.632). |
| EC-07 | Error code when an operation needs a Module Loader or Package Manager that is unavailable. | An unavailable non-authority system service that prevents completion gives `NOT_READY` (RUNTIME l.1916). An unavailable Capability Authority keeps its authorization-failure rules (RUNTIME l.1919). |
| EC-08 | Error codes for an invalid Runtime Control or route vtable, a failed `materialize_route`, and `connect_remote` with a non-remote endpoint. | Vtable version or size failures give `VERSION_MISMATCH` and null members `MODULE_ERROR` (INTERFACE l.3819-3820). `materialize_route` failures are classified at INTERFACE l.3886-3892. A non-remote endpoint gives `INVALID_PARAMS` without detail (INTERFACE l.3845). |
| EC-09 | Error code for invalid remote-listener, provider-export or enrollment input. | Invalid listener or export input gives `INVALID_PARAMS` without detail, and activation failure `TRANSPORT_ERROR` (RUNTIME l.3437-3441). Enrollment is provisioning input, not a Runtime Control method; a provisioning interface using shared codes follows RUNTIME l.2689-2691. |
| EC-10 | `route_failure.code` and `permission_settings_state.failure` were free strings with no defined values. | `route_failure.code` has seventeen defined values (RUNTIME l.2498-2518) and the permission failure value is `enforcement-failed` (RUNTIME l.2526). Consumers treat any other string as an unclassified failure (RUNTIME l.2495). |
| EC-11 | Error code at static binding registration for symbol-table defects other than duplicates, empty tables and null addresses. | Registration also rejects a malformed symbol name, an ambiguous symbol family or a missing unconditional ABI symbol with `INVALID_PARAMS` (RUNTIME l.4050-4051). Contract-dependent checks run at implementation binding (RUNTIME l.4053), where the Loader reports `abi-invalid` (LOADER l.400). |
| TR-01 | Receiver behaviour for a wrong-direction message or an ordinary message received before Hello completes. | Direction and connection state are envelope checks (TRANSPORT l.407). Such a message gets ProtocolError `INVALID_PARAMS` and the connection closes without dispatch or delivery (TRANSPORT l.417-419). |
| TR-02 | Receiver behaviour for a Response, SubscriptionResult or Event that matches no outstanding operation. | Unsolicited, duplicate or mismatched messages get ProtocolError `INVALID_PARAMS` and close (TRANSPORT l.586-587). A late Response to an abandoned call is validated and discarded, because correlation state is kept while the connection is open (TRANSPORT l.590-593). |
| TR-03 | Callee behaviour for a reused subscription identifier, an unknown one, or overlapping control operations. | An overlapping operation gets ProtocolError `INVALID_PARAMS` and close (TRANSPORT l.741-743). A reused Subscribe identifier or an Unsubscribe naming no active subscription gets a failed SubscriptionResult with `INVALID_PARAMS` (TRANSPORT l.746-748). |
| TR-04 | Error code when the Hello response carries a non-empty token under a profile that requires an empty one. | The caller sends ProtocolError `NOT_AUTHORISED` and closes (TRANSPORT l.525-526). The response checks run in the order module, token, schema (TRANSPORT l.519). |
| TR-05 | When the provider Hello takes place, and which error the consumer sees when it fails. | `materialize_route` completes peer validation and Hello before it returns a handle (RUNTIME l.783-785). A Hello rejection returns its own code, and loss or timeout returns `TRANSPORT_ERROR` (RUNTIME l.788-791). |
| TR-06 | On-wire signal when a route expires or is revoked while its session is live. | A new Request during termination gets `response-err` with `NOT_AUTHORISED` (TRANSPORT l.989). The Runtime then sends ProtocolError `NOT_AUTHORISED` when writable and closes, without waiting for an acknowledgement (TRANSPORT l.991-994). |
| TR-07 | Receiver behaviour for a `response-ok` or Event whose payload fails its declared schema. | The schema-aware receiving boundary sends ProtocolError `INVALID_PARAMS` and closes the provider session; outstanding calls get `TRANSPORT_ERROR` (TRANSPORT l.676-679). Which component is that boundary is the subject of TF-01. |
| TR-08 | Precedence between payload schema validation and the commitment check on a received message. | The order is fixed: schema subtree root, payload schema, value root (TRANSPORT l.657-667). A root mismatch closes the session; a schema-invalid Request alone gets `response-err` with `INVALID_PARAMS`. The boundary that applies it is the subject of TF-01. |
| TR-09 | No named Windows equivalents for listener transfer, peer-identity verification and directory protection in the Unix-stream profile. | The profile is conditional on Windows (TRANSPORT l.1150-1152). TRANSPORT l.1154-1168 states the access-control, listener-transfer and `SIO_AF_UNIX_GETPEERPID` peer-verification requirements. An unsupported placement fails without fallback. |
| RT-02 | Calls the Runtime engine makes for no module (bootstrap realization, cleanup, authority evaluation) had no consumer or authority basis. | A Runtime-owned system-service binding, direct or protected local transport, authorizes the engine without making it a consumer (RUNTIME l.1652-1656, l.1667; TRANSPORT l.1075). `evaluate` keeps the evaluated module as `consumer` (RUNTIME l.1665). |
| RT-03 | The orchestration module had no assigned name, and its use of the reserved `logos_` prefix was unsettled. | The role has no canonical module name and needs no provider contract; deployment identifies the instance explicitly, and neither a name nor a reserved prefix confers the role (RUNTIME l.190-192). |
| RT-04 | How `create_module` chooses among installed packages or versions that declare the requested module name. | Active policy must select one accepted declaration or the request fails; the integration must support exact package and version selection, with no substitution and no selector in the request (RUNTIME l.3614-3622). |
| RT-06 | No operation or documented procedure moves an existing instance and its state to a newer package. | Upgrade uses a new instance selected under current policy, with fresh state unless separately authorized migration applies; no Runtime Control upgrade method (RUNTIME l.3546-3554). `start_module` reuses the retained declaration, also after a stop (l.3637). |
| CA-01 | Whether a running module that loses execution authorization stops at once or waits for re-evaluation. | Runtime withdraws execution access and starts termination without waiting for re-evaluation; a retryable renewal failure keeps only an authorization that is still independently valid; intent is retained (CA l.854-859). |
| CA-03 | `publish_events` and the `publish-event` action had no defined meaning, since only providers send events. | `publish-event` is the publisher's authority to deliver an event on a subscriber route; delivery also needs the subscriber's `subscribe-event` authority and both route event lists (CA l.242-245; RUNTIME l.1229, l.3014-3016). |
| CA-04 | Order and duplicate handling of the request and response proof arrays in call evidence. | Each side is ordered by ascending deterministic-CBOR bytes of the proof's semantic path, with no duplicate path per side; empty arrays and an empty `proofs` are omitted; verifiers reject, never sort (CA l.1292-1298). |
| CA-05 | Result order, cursor lifetime and time bounds of `list_grants` and `query_audit`. | `list_grants` orders by ascending grant-id bytes, continues live after the last ID, and binds cursors to consumer and query, with documented expiry (CA l.705-714). `query_audit` has no cursor: newest first, `since` inclusive, `until` exclusive (CA l.1129-1133). |
| CA-06 | Which decision and scope a call audit record carries when the route was authorized by a route-level decision. | The record carries the allow decision actually applied to the call and the exact enforced call scope, captured at admission; a cached call decision may serve, a route-establishment decision may not (CA l.1176-1180; RUNTIME l.1732-1734). |
| PM-03 | Package Manager cursors and record filtering are bound to an authenticated caller that the provider ABI did not pass. | The invocation context identifies the caller (INTERFACE l.2181-2183). Cursors bind to the authenticated consumer, and record visibility is a deployment observation policy (PM l.1620-1628). |
| PM-04 | Manifest artifact paths may be up to 4096 bytes, longer than a USTAR header can hold. | Every archive path must fit the USTAR `name` and `prefix` fields, 100 bytes or a 155 plus 100 byte split at a slash; PAX and GNU long-name headers are forbidden (PM l.920-924). |
| PM-05 | Whether an LGX archive may be a multi-member gzip stream, and whether directory entries are required. | Exactly one gzip member; extra members or trailing bytes are rejected (PM l.943-944). Directory entries may be omitted when descendants imply them; a variant with no entries needs an explicit directory entry (PM l.909-911). |
| PM-06 | Ed25519 verification strictness (cofactor, small-order and non-canonical points) was not pinned. | Package signatures and call evidence use pure SLH-DSA-SHA2-192s, not Ed25519; lengths are fixed, and verifiers apply FIPS 205 `slh_verify` without repairing a key or signature (PM l.549-556; CA l.1274-1281). |
| PM-07 | Which source is used when several offer the same package identity and manifest commitment. | Unless the operation fixes the source, equivalent acceptable sources are taken in ascending bytewise order of their deterministic-CBOR source-record encoding (PM l.1313). |
| PM-08 | What dependency resolution does when a candidate's material cannot be fetched. | The root operation fails with `package-unavailable` and leaves installed state unchanged; unavailability is not proof of invalidity, and lower candidates need not be fetched once a solution is selected (PM l.1294-1296). |
| PM-09 | Whether `manifest.json` in an LGX archive must be checked against `manifest.cbor`. | `manifest.json` is not part of the LGX format. Only `manifest.cbor`, `manifest.cose` and `variants/` may appear at the archive root (PM l.906), so there is nothing to compare. |
| PM-12 | Provenance verification required a provenance-signing profile, and none was defined. | `logos.provenance-signing.dsse-slh-dsa-sha2-192s` is defined and required of every implementation that supports the SLSA provenance profile; protected policy selects it and binds each signer key to its builders (PM l.651-661). |
| PM-13 | Provenance failures had no assigned codes in the closed Package Manager error list. | Absent locator or malformed evidence gives `invalid-package`; retrieval failure gives `package-unavailable`; a failed signer, subject, build-type or source binding gives `signature-verification-failed` (PM l.1487-1489). The first-detected-failure rule applies (PM l.1491). |
| PM-14 | What happens to a Nix source while the LGX-only provenance profile is selected. | A request selecting a direct Nix source fails with `unsupported-source` before any Nix evaluation; resolution may use another eligible source, and a Nix-built package supplied as LGX stays eligible (PM l.603-606). |
| SO-08 | No mechanism for a deployment to declare itself non-production, or statement of what that permits. | Non-production mechanisms need explicit protected configuration, and the deployment identifies itself as non-production in documentation and operator-facing diagnostics; build mode alone enables nothing and the designation waives no requirement (BCP l.398-401). |
| NX-01 | The Capability Authority's grant-change event had to be filtered per subscriber, which a provider's broadcast publish could not do. | `grant_changed` and `policy_changed` are restricted to Runtime-owned system-service bindings (CA l.897-898). Ordinary consumers call `watch_changes` and receive `observed_change` through that invocation's protected destination, with visibility checked per publication (CA l.951, l.969). |
| NX-02 | The ordered snapshot-then-events synchronization model had no way for a provider to send a snapshot to one subscriber. | A watch method publishing invocation-scoped events orders the snapshot before the changes (TRANSPORT l.788-790), and the invocation context gives the provider that publish operation (INTERFACE l.2189). No generic revision type is added (TRANSPORT l.795-796). |
| NX-03 | One specification defined per-call authority decisions and call audit records that the Runtime specification never produced. | Every provider call needs call authority beyond the route checks, which a valid cached call decision may satisfy (RUNTIME l.1732-1735). The call record carries that decision and the enforced scope; a route-only decision does not authorize a call (CA l.1176-1179). |
| NX-04 | A module's schema namespace and type names could generate C type names equal to fixed common-header names, undetected. | Generated type names capitalize the local declaration name (INTERFACE l.775-776) and schema atoms have no uppercase letters (l.791), so `error.code` becomes `logos_error_Code_t`, never the fixed lowercase `logos_error_code_t` (l.838). |
| NX-05 | The Runtime specification depended normatively on three other specifications that its reference list omitted. | Its normative references now list the Capability Authority, Package Manager, Loader, commitment and hash specifications (RUNTIME l.4307-4311), package identity points at Package Manager Section 4 (l.3525), and the upward dependencies are tabulated (BCP l.83-86). |
| NX-06 | Diagnostic text supplied by a module had no content rule and could carry host paths to every observer. | `reason` values, including `route_failure.message`, must not expose credentials, sensitive host paths or anything the recipient may not observe, in records, responses, events and reflected remote state; Runtime may omit or replace module text (RUNTIME l.1901-1905). |
| NE-01 | How a provider returns a result only the requester may see, and progress, without broadcasting them as events. | A delayed result returns through the method's own final Response, with no job identifier or event (TRANSPORT l.841-843). Progress goes to the caller alone as invocation-scoped events (RUNTIME l.1254-1260), and the provider sees the authenticated caller (INTERFACE l.2181-2182). |
| NE-03 | A consumer was never told that its route, and the subscriptions on it, had ended. | Every route handle provides `observe_end`, which reports loss of the handle's invocation path in every mode without an observation grant (INTERFACE l.1474-1476; RUNTIME l.1355-1358). No deadline is set for detecting a silent connection failure (INTERFACE l.1495). |
| NI-01 | A module could not learn its own instance address, which every self-targeting control method requires. | `get_self` returns the complete authenticated module-instance address of the calling binding, is callable during initialization and needs no policy grant or Capability Authority (RUNTIME l.2553-2556). |
| NI-02 | The provider identifier was called stable but had no defined lifetime across stop, start, recovery and restart. | Stop, start and recovery do not replace provider records or identifiers; records restored after a Runtime restart keep their identifiers and instance, and an identifier is never reassigned to an unrelated record (RUNTIME l.2869-2872). |
| NI-03 | Whether instance identity must persist was ambiguous, and records naming a lost identity had no defined fate. | An address is kept only with continuity of the same logical instance; otherwise a fresh address is allocated and old ones are never reused (RUNTIME l.2629-2634). Retained records stay attributed to the old address and transfer nothing (l.2637-2640). |
| NI-04 | No operation ever removed a module instance, and package removal ignored instances that still used the package. | `retire_module` removes a stopped instance and its provider records from inventory, without cascade, keeping assigned storage and grants (RUNTIME l.3556-3563, l.3579, l.3585-3588). Package removal and state disposal stay separate authorized operations (PM l.1677-1678). |
| NI-05 | A request naming only a module had no rule when several instances matched, and events could omit the instance. | Lifecycle responses and state events carry the exact `instance`, or the facade's `provider` (RUNTIME l.3496-3497). A name-only request needs observation authority over the whole selection, else `NOT_AUTHORISED`; zero or several matches give `INVALID_PARAMS` (l.3665-3670). |
| NI-06 | The verified package signer was dropped from every package record, the Runtime handoff and execution observation. | The verified signer key is retained with installed state and reported by inspection results and the Runtime handoff (PM l.538-541), and observable as `selection.signer`, as provenance and not publisher identity (RUNTIME l.3519-3522). |
| NL-04 | The startup timeout had no source, and behaviour when native initialization outlives it was undefined. | The deployment supplies and documents a finite startup deadline (RUNTIME l.664). Expiry blocks readiness, never destroys or unloads while initialization runs, and the attempt stays owned until cleanup resolves (l.665-668); the failure is classified `startup-timeout` (l.3753). |
| NL-06 | Whether cleanup turns a failed instance from `error` to `unloaded` was undefined, and start and recover had different preconditions. | Cleanup alone never changes `error` to `unloaded`; only a new accepted attempt or a completed explicit stop leaves `error` (RUNTIME l.611-612). `start_module` is refused with `NOT_READY` while earlier cleanup is unresolved (l.613). TL-07 and TL-08 cover related gaps. |
| NL-10 | After a Runtime restart nothing said who resumes retained start intent, and no restart operation exists. | Orchestration must reconcile retained requested intents when it becomes operational, including after Runtime restart, and schedule the recovery that policy permits (RUNTIME l.3774-3776). No restart method is added; a restart is a stop followed by a start. |
| NL-11 | Applying configuration live had no deadline, no outcome for a timed-out attempt, and no rule for a stop meanwhile. | The deployment supplies a finite application-attempt deadline; expiry without a valid result is indeterminate, not rejection, and puts the instance in `error` (CONFIG l.269-270, l.312). A stop may close admission but not destroy the context while the hook runs (l.272). |
| NA-03 | A local route's record could omit the expiry time although its authorization always has a validity end. | Every ready route returned to its consumer "whose authorization has a validity end MUST contain `expires_at`" (RUNTIME l.2982), local routes included. Which state an expired route takes is TL-03. |
| NA-05 | Grants recorded neither who issued them nor which decision they answer, so administration depended on audit retention. | Each grant carries an immutable `issuer`, a module address or a protected-policy source, derived by the Authority (CA l.620-632, l.694-697). There is no decision link and no issuer filter on `list_grants` (l.675-681); a caller filters the listed grants. |
| NA-07 | After a policy change, existing subscriptions kept delivering events until the consumer's next protected operation. | The protected operations re-evaluated after a policy-change notification now include "new event-delivery commitments" (CA l.906-908). Events already committed follow the existing commitment rules (l.909). |
| NA-08 | Decision identifiers could repeat after an Authority restart, and the term "Authority binding" was undefined. | Decision identifiers must be collision-resistant across issuers, restarts, replacements and restored or cloned state (CA l.548-551). An Authority binding is Runtime's protected association with the selected provider realization and its invocation and notification paths (l.825). |
| NA-11 | Bootstrap policy after the Authority is bound had no precedence rule, and recovering a failed Authority rested on inference. | Protected recovery policy may authorize restoring the selected unavailable Authority and the operations this needs, and cannot override an active-policy denial (RUNTIME l.1675-1679). The specs add no lapse of bootstrap grants and no synthetic decision identity. |
| NR-05 | Whether loss of a provider session ends the route or leaves it renewable hung on an undefined phrase. | Session loss ends the session and its invocation path; alone it "need not make the logical route terminal", and a nonterminal route can renew (RUNTIME l.3474-3476). A `ready` route without a usable path is TL-03. |
| NR-06 | Whether a successful route renewal extends a live provider session was implied but never stated. | It does not. A live session keeps its previous decision and ends at that expiry; the renewed descriptor's fresh ticket establishes a replacement session (RUNTIME l.3477-3478; TRANSPORT l.929-931). The connection cost is TS-04. |
| NR-09 | Whose clock governs a remote route's expiry, and whether certificate validity times are checked. | The target Runtime enforces expiry on its accepted clock, and each Runtime enforcing an exposed deadline uses its own; disagreement cannot extend authority (RUNTIME l.3034-3037). Certificate validity periods are checked (TRANSPORT l.1259, l.1267). |
| NR-10 | The remote certificate profile left open self-signed leaves, host-name checks, the role of `server_name`, and key usage. | A directly provisioned leaf is valid as its own anchor by complete DER equality, and key-usage rules are stated (TRANSPORT l.1259-1262). Identity comes from enrollment, DNS-name matching is not required, and `server_name` is SNI (l.1269-1271). |
| NR-11 | One route handle allowed only one outstanding call, so concurrent calls needed one route each. | A prepared asynchronous call "does not monopolize that handle", and another call can be prepared while it is outstanding (RUNTIME l.1363-1364). Separately materialized handles do not by themselves share a path (l.1269). One connection per route remains: TS-04. |
| NR-12 | A caller's cancellation of a long call stopped at the provider's host and never reached provider code. | Cancellation is a sticky state on the provider's invocation context, with an optional `request_cancel` hook (INTERFACE l.2143-2144); Runtime arranges Cancel processing on a live session (l.2073). It does not prove that the work stopped (l.2179). |
| ND-03 | A schema-valid value larger than the frame limit closed the whole connection; a sender-side rule and per-call failure were missing. | Before writing, the sender checks each frame against the peer maximum, 16 MiB by default (TRANSPORT l.383-384). An oversized Request fails locally, an oversized Response becomes a correlated `MODULE_ERROR` (l.385-386), and an oversized Event is not committed (l.388). |
| ND-08 | Named types could not be shared between interface contracts, or between an interface and a module implementing it. | Interface and concrete contracts may both import named types from an explicitly supplied supporting schema (INTERFACE l.102, l.110), so shared records live there. Types declared inside a contract are not referenceable from other documents (l.118-119; TL-05). |
| ND-11 | Whether a value typed by a declaration whose body is a primitive, literal or reference carries the declaration's subtree root or a leaf hash. | No response, but the text settles it: "An empty path always uses the named declaration's schema subtree root, including when its body is a primitive, literal or reference node" (COMMITMENT l.569); the vectors agree (HASH l.1495). |
| ND-13 | An aggregate named only through a variable-length list had no forward typedef, although its definition names its own type. | No response, but the text settles it: "The generator MUST also emit a forward typedef whenever an aggregate type name is used before its complete definition, including uses through variable-length lists" (INTERFACE l.1077). |
| ND-14 | The tie rule for ordering type definitions did not give the order of the normative example header. | No response, but the text settles it: there is no tie rule, and the placement of independent declarations "is not part of the canonical mapping" (INTERFACE l.893; l.642, l.2639). |
| NP-05 | Where licence and attribution material goes, and how a user-replaceable (LGPL) library coexists with verified-byte binding. | Licence and attribution material ships as verified `resource` artifacts under documented application conventions (PM l.1202). Replacing executable bytes requires acceptance of the replacement through the artifact, trust and authorization rules, never an in-place swap (l.1203). No notice-discovery contract (l.1204). |
| NP-07 | What the installation root is, and whether installed sets are per user or per host when several Package Managers coexist. | The installation root is the protected destination for materialized artifacts (PM l.929). Layout and per-user, per-host or per-service scope are documented deployment choices (l.930, l.934); distinct Package Manager instances share no inventory implicitly (l.931). |
| NP-08 | Events for installed-set changes and install progress, and a Runtime Control event when a module record is created. | `watch_installed_packages` delivers change hints to its caller, who re-queries (PM l.1712, l.1734-1735). A `progress_key` enables caller-correlated `operation_progress` events (l.1752-1754). Record creation raises an `inventory_changed` hint (RUNTIME l.3417). |
| NP-10 | Anti-rollback for package-signing trust input, and who decides the fate of running modules when a signer is withdrawn. | Trust configuration uses a monotonic revision or equivalent, surviving restart; older state is rejected (PM l.395-397). Withdrawal blocks later package operations; the deployment documents whether execution depends on current trust, and then authorization is invalidated (l.402-404). Exact-name binding: TS-05. |
| NC-05 | Secrets passed as method parameters were committed deterministically and could be retained, and no schema marker identified them. | `_sensitive` marks whole requests and responses (INTERFACE l.213, l.223): buffers are erased (l.381), nothing is logged or audited (l.395), a retention policy rejects the call (l.397). Events cannot be marked (l.449); exposed commitments stay guessable (SECURITY l.402). Credential storage: TL-02. |
| NS-01 | The specs did not say that operating-system device consent goes to the application, leaving per-module device permissions without an enforcer. | Platform consent applies to platform-defined principals, not to module instances (SECURITY l.410). A profile claiming per-module device restrictions must name the consent principal and the controls against bypass (CA l.408-409). No such profile is defined. |
| NS-02 | What a module's host process does when the Runtime that owns it dies was unspecified. | Terminal loss of the control carrier stops new work and starts termination. Earlier authority cannot keep admission open, destruction is not guaranteed to run, and a new Runtime binding adopts no survivor (RUNTIME l.974-977). |
| NS-03 | Deployment profiles were not required to state secret storage, backup exposure or deletion of module state. | Deployment documentation must state protection at rest, secret-storage facilities, backup and synchronization exposure and deletion limits (BCP l.394). No blanket backup exclusion or erasure guarantee is required (l.396). The Credential Store the specs name is absent: TL-02. |
| NO-01 | Runtime Control list methods returned an arbitrary subset with no continuation, no defined order and no filter for modules. | All four list methods page through one snapshot with `cursor`, `limit` and `next_cursor` (RUNTIME l.3372, l.3379-3382), in a fixed key order (l.3406-3413). `list_modules` takes `module` and `instance` filters (l.3376). |
| NO-02 | Observers could not synchronize snapshots with events: no revisions or timestamps, and no event for created or removed records. | Membership and record changes in the four collections raise `inventory_changed` hints (RUNTIME l.3416-3417); observers subscribe, list and rescan (l.3425-3428). There is no timestamp, route sequence or replay. Changes of `realization` and `selection` raise no event or hint (TL-08). |
| NO-05 | The initial permission-settings state and first revision of a newly created instance were undefined. | A new instance without protected settings starts at revision 1, with an empty permission array, status `applied` and no failure (RUNTIME l.2541). Declarations and `requested_permissions` alone never supply settings (l.2543); the initial state grants nothing (l.2545). |
| NO-06 | What happens to a running instance when its permission settings are replaced with wider access. | Runtime reconciles widening and narrowing, live or by stop and re-realize (RUNTIME l.2594-2595). Widening needs current execution and permission authority (l.2596). A reconciliation stop keeps execution intent and its origin, and resumption uses ordinary recovery (l.2597-2598). |
| NO-07 | The four module-execution actions of an authorization scope were never mapped to the lifecycle methods. | Actions are `start` and `stop` only (CA l.197, l.314). `start` covers loading, initialization, readiness and continued execution (l.329); `stop_module` needs `stop` (l.335), which includes unloading (l.337). Creation, retirement and settings need separate management authorization (l.340). |
| NF-01 | (on C-01) the sentence on unqualified common names was ambiguous rather than contradictory; common definitions should be referenced only by qualified names | COMMITMENT l.706: "Common schema references in the normative construction input MUST use qualified names in the `logos` namespace." |
| NF-02 | (on C-03) the interface specification defined no conformance classes, so a tool without the C-to-CDDL direction could not tell whether it conforms | INTERFACE l.23-24 separates two subjects: "a conforming implementation of the bidirectional mapping" supports both directions; "A module implementation is not required to implement the authoring mappings". No one-direction mapping class exists. |
| NF-03 | (on C-06) the per-name socket path was only an example; the real gap was the 4096-byte address bound against host socket-path limits | RUNTIME l.316-317 places the socket in the per-instance directory and makes the pathname "implementation-defined and subject to the host's Unix-domain socket pathname limit". TRANSPORT l.1371-1373: callers use the supplied path and derive none. |
| NF-04 | (on C-07) a manifest ordering violation already had a code; the shared-artifact contradiction and the missing check precedence remained | PM l.358 assigns `invalid-package` to ordering or uniqueness violations. Schema and default artifacts may be shared (l.335); only "one implementation artifact" on several declarations is invalid (l.1088). Validation "MAY stop at the first detected validation failure" (l.1070). |
| NF-05 | (on C-08) `unsupported-strategy` covers only strategies that were not advertised; a refusal to weaken isolation had no error code | LOADER l.628: an otherwise valid request using an advertised strategy and placement "MUST fail with `realization-failed` if required security or deployment controls cannot be established". `unsupported-strategy` keeps its meaning (l.377, l.621). |
| NF-07 | (on CM-02) the schema root below a common-schema reference was already fixed; the hash payload label and supporting-schema imports were not | HASH l.709-710: the reference payload keeps the importing document's root, and "Its child and that child's descendants MUST use the referenced document's root in field `1`", for common and supporting imports alike. Vectors: Appendix B.4 (l.1442). |
| NF-08 | (on CM-03) the commitment model was not silent on importing callable declarations; the undefined term was "permitted kind" | COMMITMENT l.667: "An imported reference MUST target a named type declaration." That fixes the "permitted kind" of l.1310 and excludes the method request and response declarations of the common schema (l.727-728). |
| NF-09 | (on CM-06) the closed ordered list of selection tests already rules out literals nested in containers; only table rows were missing | COMMITMENT l.464-465: literal collection follows references and choice arms and "MUST NOT descend into map fields, list elements, or tuple positions within that value". The table marks `["a"] / ["b"]` Invalid (l.503). |
| NF-10 | (on CM-10) whether `0*` and `*1` are rejected or normalized turned on an undefined notion of construct identity | cdCDDLe l.178-179: "Source occurrence indicators with explicit numeric bounds MUST be rejected, even when their cardinality equals that of a supported form." The next sentence names `0*` in arrays and `*1` in maps. |
| NF-11 | (on CM-12) rejecting a named range bound already followed from the text; only an explicit statement was missing | cdCDDLe l.181-182: "Range bounds, including those in `.size` controllers, MUST be integer literals written directly in the source." Named references as range bounds are rejected. |
| NF-12 | (on EC-09) enrollment is not a Runtime Control method, so it has no method failure that needs an error code | RUNTIME l.2689: "Enrollment validation is a provisioning requirement, not a Runtime Control method." A provisioning interface that uses the shared error registry reports malformed, stale or conflicting records as `INVALID_PARAMS` and authentication or authorization failure as `NOT_AUTHORISED` (l.2690-2691). |
| NF-13 | (on EC-11) symbol defects that static registration cannot detect are binding-time failures reported by the Loader, not a missing registration code | RUNTIME l.4050-4053 lists the table defects rejected at registration with `LOGOS_ERR_INVALID_PARAMS` and defers checks that depend on the call surface to implementation binding, where the Loader reports `abi-invalid` (LOADER l.400). |
| NF-14 | (on CA-05) the audit query has no cursor and a fixed order; only the grant list's order and cursors were open | CA l.705-714: grants are ordered by ascending grant-id bytes, continuation is live and strictly after the last returned ID, cursors are consumer-bound and may expire. Audit: newest first, `since` inclusive, `until` exclusive, no pagination (l.1129-1133). |
| NF-15 | (on CA-06) a route-establishment decision cannot be recorded on a call audit record, which needs one call scope with one method | CA l.1176-1179: the record carries the decision "actually applied to authorize the call and the exact enforced call scope"; "a decision authorizing only route establishment or renewal does not authorize a call". A cached call decision may be used. |
| NF-16 | (on HC-13) the authority contract can express a per-call decision; the Runtime text never said when a call is evaluated | RUNTIME l.1732-1735: before dispatching a provider method "Runtime MUST authorize the authenticated consumer's call on the selected route, provider, contract and method"; route authority is not enough, and a valid cached call decision may satisfy the check. |
| NF-17 | (on RT-06) the text did not say when a package declaration is selected or whether stop then start selects again | RUNTIME l.3614: creation selects the declaration. l.3637: starting an existing instance "MUST use its retained accepted declaration and MUST NOT select a replacement declaration". A package update never reselects; an upgrade is a new instance (l.3546-3547). |
| NF-18 | (on RT-05) a replacement Loader reports unknown identifiers as absent or released, hiding realizations left by the Loader it replaced | RUNTIME l.3822: "A replacement Loader's empty registry or successful release of an unknown identifier does not establish that confirmation." Runtime keeps cleanup ownership, reports `unknown` (l.3533) and realizes no replacement until termination is confirmed (l.3821, l.3824). |
| NF-20 | (on SO-09) a long-running-operation pattern already existed in the transport text; the defect was that it was underspecified, not absent | TRANSPORT l.841-858 states three shapes: one delayed result through the method's own final Response, intermediate events to subscriptions activated before the call, and a contract-defined resource with start, inspect, read and cancel methods. No generic job protocol. |
| NF-21 | (on C-12) the upward dependency also covers package-manager handoff records and Loader binding identifiers, and the Runtime references omitted all three specifications | BCP §1.1 lists the Runtime dependencies on Package Manager and Module Loader definitions as exceptions to the layer direction (l.84-85), next to the Capability Authority ones. RUNTIME's normative references name all three (l.4307-4309). |
| NF-24 | (on HC-02) broadcast events expose each consumer's operation identifiers, timing and progress to every other authorized subscriber | RUNTIME l.1254-1260: an invocation-scoped publication uses a protected destination bound to the admitted invocation and "selects only active subscriptions for the named event within that invocation path". The result returns in the method's own Response (TRANSPORT l.841). |

## Appendix B — Earlier items the owner declined

Items where the response keeps the boundary where it was: the matter stays outside Core, or is left to an
implementation, a deployment or a profile. The specs are consistent on each point, so nothing further is
asked. The outcome column says what the specs state and what an implementer or a deployment does
instead.

| Item | Subject | Outcome |
|---|---|---|
| C-09 | Whether a consumer owned by an enrolled remote Runtime counts as a "Runtime-known" instance for the target's Capability Authority. | No definition of "resolve" for an address owned by another Runtime was added. An address names its owning Runtime (CA l.84), and the target authorizes a forwarded consumer after the ownership and forwarding checks (RUNTIME l.1788-1791). |
| RT-01 | No defined way for a command-line tool, which is not a module instance, to reach a running Runtime. | Activation is protected deployment input that must resolve to an accepted declaration realized by the Loader (BCP l.384-388). BCP l.390 assigns no activation encoding or terminal protocol; each deployment documents its own (RUNTIME l.1815). |
| CA-02 | How consumer attributes that policy depends on reach an external Capability Authority. | No attribute field or query protocol is defined (CA l.115). A deployment whose policy needs attributes defines a protected attribute-source integration with authoritative sources, freshness and failure rules; missing facts fail evaluation (CA l.101-106). |
| CA-07 | No method or format for exporting signed call-evidence containers. | `query_audit` returns audit records, not evidence containers, and no retrieval method is added. Export goes through a documented, protected deployment integration that authorizes the complete record and each included proof (CA l.1320-1325). |
| PM-01 | What the LGX source fields `storage` and `object` name, and how `object` is encoded. | `storage` names a deployment-configured Storage binding and `object` is an opaque locator; the retrieval API and locator encoding are implementation-defined and documented, so locators carry over only between compatible deployments (PM l.856-860). |
| PM-02 | Packages come only from Storage or Nix; no local-file source, and no described way to obtain the first Storage provider. | `package_source` stays `lgx` or `nix` (PM l.790-802). The first Package Manager and Storage providers arrive as protected deployment input, without a source record or an installed record (PM l.1440-1442). |
| PM-10 | No registry of platform `os`, `architecture` and `abi` values for producers and Package Managers to share. | No global registry (PM l.960). The deployment profile defines the supported values and matching rules; a value with no rule does not match; cross-deployment packages need compatible definitions (PM l.954-960). |
| PM-15 | No optional or platform-conditional package dependencies. | Dependencies are unconditional and apply to every variant, and platform selection never omits one. A producer whose platforms need different dependency sets publishes separate packages (PM l.1221-1223). |
| SO-01 | No common catalog document, catalog location, refresh operation or catalog-policy format. | Catalog formats, acquisition, refresh and catalog-policy configuration are implementation-defined and must be documented; only the catalog entry record is common (PM l.836-837, l.843-846). Two implementations share catalogs only by agreement. |
| SO-02 | No common Storage fetch contract for the Package Manager to retrieve package objects. | No common fetch interface is required of Storage providers (PM l.1438). The retrieval API and locator encoding of each Storage binding are implementation-defined and documented (PM l.859), so a Package Manager works with the Storage bindings its deployment configures. |
| SO-03 | No standard formats for protected deployment inputs such as bootstrap pins, trust anchors, enrollments, policies and limits. | Encodings stay deployment-defined. Deployment documentation must identify the accepted representations, their provisioning, validation and replacement or revocation (BCP l.359); a representation cannot change Core value semantics (BCP l.392). Moving a deployment between implementations needs compatible tooling. |
| SO-04 | No common authority policy language and no baseline policy for deployments to start from. | RUNTIME defines no policy language (l.1701-1702); default deny stays mandatory (l.1682-1683). Each deployment documents its policy input format and the explicit permissions its bootstrap and system-service integrations need (BCP l.360). |
| SO-05 | No common permission vocabulary (network, filesystem, devices) that a package can request across deployments. | Permission names and constraints come from the profile that exposes a facility (CA l.394-395); each permission identifies its defining profile (CA l.388-389); unknown permissions are rejected (CA l.392). Packages work across deployments only where the definitions agree. |
| SO-06 | No operator principal: how a human administrator is identified, delegated authority and given an administrative path. | Humans stay outside the participant model (BCP l.103-105). Administrative software acts as an admitted module under ordinary authority (SECURITY l.540); the deployment documents how its administrative path authenticates the approving principal (BCP l.380). |
| SO-07 | No reserved namespace or prefix convention for schemas owned by an implementation. | Only the `logos.`, `logos-` and `logos_` prefixes are reserved (INTERFACE l.256-258). Implementations pick any other namespace; a clash surfaces through the existing collision and conflicting-identity rules when documents are combined (INTERFACE l.898, l.2302-2303). |
| SO-09 | No generic streaming or large-object profile, and no standard pattern for long-running operations. | No generic streaming or chunked transfer (RUNTIME l.3894-3895). Contracts model chunking, references and jobs themselves (RUNTIME l.3920-3921); TRANSPORT l.841-858 describes delayed results, intermediate events and contract-owned resources as uses of ordinary methods and events. |
| NE-02 | No rule orders a call's Response before the events that call causes, so a consumer cannot correlate early events. | No ordering is required (RUNTIME l.1301); an event may arrive before submission returns (TRANSPORT l.847). The consumer subscribes first and the contract correlates by a value known before the call, such as a caller-chosen one (TRANSPORT l.848; RUNTIME l.1271-1272). |
| NE-04 | A provider is never told that a consumer's route or session ended, so per-consumer state has no release trigger. | No session-end notification. The provider learns of caller loss only for an outstanding invocation, as cancellation (INTERFACE l.2101); state tied to an open watch call is released then, and other state is a contract-defined resource with its own lease (l.446). |
| NE-05 | A slow transported subscriber either blocks the publisher or has its whole connection closed, with no bound or per-subscription policy. | Backpressure or connection closure stays (TRANSPORT l.804-809). Each implementation must document which action occurs, under what conditions and with what wait bounds (l.815-816). A provider that must not block publishes from its own thread with a bounded latest-value queue. |
| NE-06 | Whether a provider's final events, published while it is stopping or being destroyed, are delivered was undefined. | Delivery of an event published while stopping is not guaranteed; route, subscription and authority state decide (RUNTIME l.1239-1241). A provider publishes its final state before stop is requested, from a declared preparation method. See TL-03 for route states. |
| NI-07 | Grants outlive their target instance: no orphaned status, and a grant cannot name a replacement instance. | Grant status describes the policy record, not target liveness, and a grant never moves to another instance (CA l.731-733). A replacement consumer instance needs new grants; stale ones are revoked explicitly, since retirement does not revoke (RUNTIME l.3588). |
| NL-01 | The stop grace period was undefined, and a module could not learn, declare or extend its stop time. | Drain and cleanup deadlines are deployment-supplied and documented (RUNTIME l.3835; BCP l.372); a module neither declares nor sees one. A long flush goes into a declared method called before stop (RUNTIME l.3871). TF-02 bears on work left in the destructor. |
| NL-02 | No cooperative pre-stop phase: a stopping module loses its outbound routes before its only stop hook runs. | No preparation phase; a stop still prevents the module's new outbound calls first (RUNTIME l.620-621). An orchestrator calls each module's declared preparation method before stopping it (l.3871-3872); nothing requires this on a host-initiated shutdown. See TF-02. |
| NL-03 | The destructor returns nothing, so a module cannot report that its final flush or close failed. | Destruction reports lifetime completion only (RUNTIME l.3870). A flush outcome is the Response of a declared method called before stop (l.3871); Runtime-observed cleanup problems appear as `cleanup-failed` or `cleanup-timeout` (l.3753). See TF-02. |
| NL-05 | No suspend and resume, or background and foreground, notion exists for hosts that the operating system suspends. | There are five module states and six host operations, none for suspension (RUNTIME l.565-570, l.3963-3970); background work is left to platform profiles (SECURITY l.407-408). A module checkpoints to its state directory and tolerates termination without destruction (INTERFACE l.1603). |
| NL-08 | Core has no liveness source, so a module whose dispatch hangs stays `ready`. | Readiness does not guarantee continued progress (RUNTIME l.578) and a failed call is not a realization failure (l.3793). A caller bounds each call with `timeout_ms` (INTERFACE l.2059); hang detection is left to deployment supervision or a contract's own status method. |
| NL-09 | Long-running operations lack a common idempotency key, durable operation handle and resynchronization shape. | A delayed result uses the method's own deferred Response (TRANSPORT l.841-843). Anything spanning invocations is a contract-defined resource (l.851; INTERFACE l.446); each contract defines its durability, idempotency and resynchronization, with no generic job protocol (TRANSPORT l.858). |
| NA-01 | A consumer denied while a person's approval is pending cannot tell that from a permanent refusal. | The denial stays opaque: an application "MUST NOT infer an approval request or pending approval from `NOT_AUTHORISED`" (RUNTIME l.742). The consumer learns a pending state from the approval module's own contract (l.741) and makes a new attempt later (l.743-744). |
| NA-02 | An approval module gets no notification of a pending denial and no presentable description of the requested scope. | No approval queue, event or record. The approval module keeps its own state under an ordinary contract (RUNTIME l.741); its display separates authenticated scope from supplied descriptions (BCP l.381), and presentation authority gives no discovery or audit access (SECURITY l.545). |
| NA-06 | A provider that enforces a permission per caller has no way to learn the caller's allowed scope. | No Core check method. A provider-enforced permission must define its own authorization integration, which an ordinary contract may supply (CA l.419-421). The provider sees the caller's address (INTERFACE l.2181-2182), which is not authorization (CA l.422). |
| NA-09 | A module acting for another module's request, or for a person's choice, cannot carry that requester's authority. | No delegation. A forwarding module acts under its own identity and authority (INTERFACE l.209; RUNTIME l.1333). A contract may record the requester as provenance, kept distinct from the authorizing consumer (BCP l.382); provider selection delegates nothing (SECURITY l.548). |
| NA-10 | Audit records cannot hide sensitive constraint values without dropping the whole record. | No redacted form. A returned record keeps its exact recorded scopes, or the whole record is omitted (CA l.1336-1338). Sensitive constraint values need explicit audit authorization before they are retained (l.1340). |
| NR-01 | A provider on a device that cannot accept inbound connections cannot serve consumers on another device. | The caller must reach the provider-side listener (TRANSPORT l.1200). NAT traversal, rendezvous or relay needs a deployment mechanism or a separately specified profile, and no intermediary may replace target authentication or channel binding (l.1201-1202). |
| NR-02 | Two independently owned devices have no defined exchange for enrolling each other's Runtime. | "This specification defines no pairing exchange or general provisioning method" (RUNTIME l.1818). Enrollment provisioning is supplied by the implementation or deployment (l.1817), with trust established independently of an unauthenticated connection (l.1819). |
| NR-03 | Nothing creates the local facade for a provider on another Runtime, sets its target or refreshes its address. | Facades are created and targeted by "protected deployment input or an authorized implementation-defined management operation" (RUNTIME l.1812). A changed locator is authenticated against the configured target and never retargets an established route (l.1813). |
| NR-07 | No keepalive or idle rule, so a call to a sleeping remote peer can hang; fresh remote state is undefined. | No keepalive. Facade readiness needs fresh evidence under a Runtime policy that says when the evidence lapses; an open carrier is not enough (RUNTIME l.3764-3765). Callers bound each call with a timeout (INTERFACE l.2059) and observe path loss (l.1474). |
| NR-08 | No bound on in-flight requests, no common overload result, and control messages queue behind large frames. | Implementations enforce and document finite limits and their exhaustion behaviour (TRANSPORT l.1343-1345), choosing delay, rejection or close (l.1350). There is no common retryable overload response or control-latency bound, and Cancel cannot overtake a committed frame (l.1357-1358). |
| NR-13 | A local Unix-socket address for Runtime Control was typed and shown in an example without any consumer-binding rule. | The Unix address form "does not define a general local Runtime Control access profile" (RUNTIME l.1814), and the example now shows a remote endpoint (l.4162-4174). An external local process enters through deployment-defined activation (l.1815; BCP l.384-385). |
| NR-14 | The local socket profile checks the peer by user identity, so a same-user module can impersonate a provider. | Stated as a limit: a shared user identity "is not an isolation boundary", and mode bits do not stop endpoint replacement (TRANSPORT l.1107-1108). A deployment claiming that protection must prevent substitution or fail the placement (l.1109). No mechanism is defined. |
| ND-01 | A common type for integers wider than 64 bits and for decimal amounts, so generic clients can render them. | Integer types end at 64 bits (INTERFACE l.477) and no numeric profile exists (COMMITMENT l.951-953). A contract carries a wider value in a `bstr` or `tstr` and defines its meaning (INTERFACE l.497); generic clients cannot interpret it. |
| ND-02 | A common timestamp and duration type for all contracts. | No common alias. Capability Authority and Runtime Control each state whole milliseconds since 1970 for their own fields (CA l.545; RUNTIME l.3031). Every other contract defines the epoch, unit and clock of its time values itself. |
| ND-05 | Maps with dynamic keys, or a standard list-of-pairs convention with declared key uniqueness and set semantics. | Dynamic-key maps are not allowed (INTERFACE l.493). A contract uses a list of records and defines key equality, duplicates and order itself (l.3141); list order is part of the value (COMMITMENT l.1077). See ND-04 for the specs' own lists. |
| ND-06 | A declarable opaque-payload type for contracts that forward externally defined formats such as JSON. | No opaque or JSON type. A contract may carry an external encoding in a `bstr` or `tstr` and define it (INTERFACE l.497); generic validation does not check it and the commitment covers the bytes or text only (l.498-499). |
| ND-07 | A common record and response convention for domain failures, so generic clients can tell failure from success. | No common error record. Each contract represents an expected domain failure in its own response schema (INTERFACE l.365), returned as a valid response (l.3169-3170). A generic client shows the response and needs the contract to interpret it. |
| ND-09 | A surface for human-readable descriptions of contracts and methods. | No description surface. Comments are not schema identity inputs and may differ after reconstruction (INTERFACE l.2634). Descriptions travel outside the contract, as application-defined material; a package has no declared carrier for contract documents either (TS-06). |
| NP-01 | Signed display metadata (name, description, icon, publisher) in packages and catalog entries, so a store can browse without downloading. | Core catalog entries carry location data only (PM l.869-870). Display metadata and search belong to an application catalog contract, which must separate unverified claims from verified facts (l.875-876); display names establish no trust (l.878). See also TS-06 (contract documents). |
| NP-02 | An executable or bundle artifact kind, so a module can ship and launch its own separately signed helper program. | No executable artifact kind. `resource` and `data` artifacts authorize no execution (PM l.1196) and no executable-bundle realization form exists (l.1200). A deployment that needs a helper program provisions it outside the package, under its own controls. |
| NP-03 | A package form for presentation modules: view-only modules, entry view, icon, and defined `resource` and `data` kinds. | `resource` and `data` are defined (PM l.1195). No view-only form (l.1200): a presentation module is an ordinary module (RUNTIME l.3885) with an adapter exporting the native ABI (LOADER l.202-203). Entry views and icons belong to a presentation profile. |
| NP-04 | A way for a signed package to describe a statically linked module, as on mobile hosts. | Core defines no package-to-static-registration handoff (RUNTIME l.1394). A deployment that keeps signed declarations for a statically linked module verifies them and binds the accepted facts to the linked code through protected registration (l.1395). |
| NP-06 | A package field stating a minimum Runtime ABI or OS version, checked when the platform variant is selected. | No version-range field. The deployment profile defines the `os`, `architecture` and `abi` values and their matching rules, including ABI or version constraints (PM l.954); a value without a rule never matches (l.957). No global registry (l.960). |
| NP-09 | A declarative home for platform-integration material such as device rules, usage descriptions and entitlements, with an install-time check. | No such artifact kind. The deployment documents the protected administration of operating-system integration material (BCP l.376); installation grants no device consent and authorizes no package-supplied system rules (l.377). A missing facility fails the dependent realization, not the installation (l.378). |
| NC-01 | A change to a module's configuration schema leaves installed instances unable to start, with no migration hook or fallback. | No hook, automatic migration or default fallback. An unchanged declaration keeps its records (CONFIG l.248); a changed schema needs a replacement instance (l.251), and the deployment names the workflow that transforms and supplies the old value (l.258, l.261). |
| NC-02 | Accepting a package default is optional, a start without a value has no error code, and no reset exists. | Default acceptance stays a documented deployment choice (CONFIG l.134, l.141). A start without an eligible value fails with `NOT_READY` (l.125). Reset is an explicit complete replacement, with no default-retrieval method (l.135-136). |
| NC-04 | A module cannot declare that it needs persistent state, and state has no class, size or backup semantics. | No declaration field, classes or sizes. A state requirement travels in deployment input or a profile-defined permission's constraints (RUNTIME l.1424); a deployment accepting one defines its carrier, and start fails when it cannot be supplied (l.1457-1458). |
| NC-06 | A user-selected file's operating-system capability cannot be handed from the module that obtained it to another module. | No capability carrier. A broker contract keeps the platform capability at its provider (RUNTIME l.3912); a profile that transfers it must define binding, operations, lifetime and revocation (l.3913). A path or descriptor value in a payload grants nothing (l.3914). |
| NO-03 | Per-instance resource usage observation, a declared expected footprint, and a typed signal when a resource limit is hit. | No usage method, footprint declaration or limit event. Usage reporting is left to an ordinary module contract that defines its own measurement; the informative observer section defines no contract (BCP l.536, l.546). Resource accounting appears only as enforcement (CA l.413-414). |
| NO-04 | A Runtime self-description method, and the package identity on each module record, for diagnostics and version reporting. | No self-description method, and the module record has no package field (RUNTIME l.2058-2071). A client calls `get_execution_summary` per instance and reads `selection.package` (l.3513, l.3525). Implementation version reporting stays in host diagnostics. |
| NF-19 | (on PM-10) citation correction only; the request for a registry of platform values and a defined runtime profile is unchanged | PM l.954-960: the deployment profile defines the `os`, `architecture` and `abi` values and their matching rules; "A value with no defined matching rule MUST NOT match". No global registry. Producers and installers share one deployment's definitions. |
| NF-22 | (on HC-12) every way to tell apart two instances of one module uses identifiers minted at creation; no alias exists beforehand | Core defines no instance alias or role name. With several matching providers Runtime selects by routing-selection state or deployment configuration (RUNTIME l.1479-1482). A management module creates the instances, keeps their identifiers and gives each consumer the provider to pin (l.3141). |
| NF-23 | (on HC-04) lifting the unique-method-name rule would not allow two revisions in one provider, because native dispatch carries no contract identity | Exact contracts and the uniqueness rule stay (INTERFACE l.339-340). l.208: "Overlapping contract revisions may be supplied by separate admitted providers or explicit adapters." A provider keeps an old interface contract and adds interfaces with distinct method names (l.205). |

## Appendix C — Concerns of `human-spec-comments.md` that the current specs settle

These nine concerns have no reply, but the current text either meets the need or places it outside Core,
as the last column states.

| Item | Concern | In the current specs |
|---|---|---|
| HC-01 | Two modules can share a name and a contract yet behave differently, and a consumer can neither tell them apart nor choose between them. | The verified signer and package of an instance's selection are observable as provenance, not publisher identity (RUNTIME l.3519-3525). Equal names or commitments establish no equal behaviour; provider selection and execution policy choose (l.1436-1437). A route request can pin one provider (l.3141). |
| HC-03 | A method body cannot see which consumer is calling it, so a provider cannot apply per-caller policy unless grants can constrain parameter values. | A method reads its caller's authenticated Runtime and module-instance identifiers through the invocation context (INTERFACE l.2162-2186; RUNTIME l.886-890). The view carries no module name (INTERFACE l.3519-3523). Caller identity is a fact, not authorization (CA l.419-422). No scope constrains parameter values (CA l.147-151). |
| HC-05 | Calls block the caller, which must dedicate a thread to each outstanding call to get asynchrony. | Runtime Control and route bindings must provide `prepare_call`, for synchronous providers too (INTERFACE l.2013-2016). Several prepared calls may be outstanding on one route handle (RUNTIME l.1363-1364), completing by callback (INTERFACE l.2053). A synchronous `call` stays serialized per handle (INTERFACE l.1980-1981). |
| HC-06 | A call has no configurable timeout and cannot be cancelled through the native interface, and it is unclear whether timeouts are the caller's job. | A prepared call takes a caller-selected timeout from submission (INTERFACE l.2059) and ends with `TIMEOUT` or, after `cancel`, `CANCELLED` (l.2067). Runtime arranges Transport Cancel on a live session (l.2073); the provider sees sticky cancellation and an optional hook (l.2143-2144). A synchronous `call` has neither (l.3734-3741). |
| HC-08 | Modules pass host file paths to each other; a path loses its meaning when the provider runs on another machine or in a sandbox. | A path grants no access or visibility in another realization (RUNTIME l.3910); co-location gives no shared namespace (l.3917). A contract accepting a path must define whose namespace it addresses (l.3918), and a provider must not silently reinterpret a caller-local path (l.3919). Values, chunks or references can carry content (l.3920). |
| HC-09 | There is no unified logging: no common log level set once for every module, and no way to collect module logs through contracts. | Core defines no logging facility, level or retrieval contract. Optional diagnostic logging is left to ordinary module contracts and deployment integration, which must define attribution, authorized access, sensitive-data handling, retention and delivery bounds (BCP l.550-551). Its failure must not waive audit or enforcement (l.552). |
| HC-11 | The order of C parameters, struct fields and choice arms is unstable: adding a field or an arm can move existing ones. | Fields and parameters are ordered by field-name bytes (INTERFACE l.895), choice discriminants by label order or canonical index (l.1157-1159). Source order is not ABI-visible (l.897); placement of independent declarations is outside the canonical mapping (l.893). The order is deterministic, not append-stable; a reordering change is also a new root (HC-04). |
| HC-12 | A module instance has no alias or stable name: the creator gets an opaque identifier, and everyone else must discover it. | `create_module_request` carries only `request_key` and `module` (RUNTIME l.2233-2236), and the key is idempotency only (l.3627). Lifecycle requests select an exact instance or facade (l.3656, l.3665-3670); a route request can pin a provider (l.3141). The reply to NF-22 declines role names and a resolver. |
| HC-13 | There is no specified way to ask a person, at call time, whether a call should be allowed, and to hold the call meanwhile. | Each call is an authorization point (RUNTIME l.1732-1735). A denial is opaque and final: no pending approval may be inferred, and a later approval does not resume the attempt (l.742-743). Approval workflows are ordinary module contracts (l.741); a method may hold its own Response while a person decides (TRANSPORT l.841-843). |

## Appendix D — The integrator documents, claim by claim

Status words: `ok` means the specs support the claim as written, `partly` that they support it with a
stated limit, `no` that they do not provide it, and `contra` that they forbid it. Next to the identifier of
an earlier item, "declined" and "resolved" give its outcome as in Appendices A and B, and "no response
yet" means the owner has not answered it.

| # | Claim (source) | Status | Spec basis |
|---|---|---|---|
| 1 | Application code need not be a module; it calls modules through typed clients and subscribes to their events (DOCS l.137, l.139; RFP l.435-448) | contra | RUNTIME §13 l.3935, Terminology l.138; BCP §2 l.100-102. TS-01 |
| 2 | The host starts the runtime through a small C interface and needs no particular event loop (DOCS l.135) | ok | RUNTIME §13.2 l.3975. The interface is small because everything else is an opaque `configuration_format` blob (l.4034-4036): TS-01. Those encodings stay deployment-defined (SO-03, declined) |
| 3 | The application ships the runtime and the module packages in its own bundle (DOCS l.134) | partly | A bundled `.lgx` cannot be installed: `package_source` has no file kind (PM l.790-802; PM-02, declined). Bundled code enters as protected bootstrap input or static registration, both implementation-defined (RUNTIME l.1391-1392), and "Core ... defines no package-to-static-registration handoff" (l.1394; NP-04, declined) |
| 4 | Logos Core "resolves their dependencies, and manages their lifecycle" (DOCS l.136) | partly | Dependency resolution is the Package Manager's and never starts anything (RUNTIME §3.7 l.736-739, l.753-754); start order comes from orchestration and from ordering constraints with no defined representation (l.746-748; SO-03 and PM-15, declined) |
| 5 | Placement per module: own process, one runtime process, in-application; `sandbox` and `container`; start refused when the platform cannot provide the sandbox (DOCS l.102, l.145) | ok | LOADER §3 l.165-168, §4 l.255, §6 l.428; SECURITY §4 l.214. How a deployment states the per-module choice is not portable (NP-14, no response yet; SO-03, declined) |
| 6 | A module can be linked statically where dynamic loading is unavailable (DOCS l.124) | ok | RUNTIME §2.3 l.392-393; LOADER l.186-188. A signed package does not describe such a module (RUNTIME l.1394-1396) |
| 7 | Signature checks: Logos keys trusted by default, users add publishers they trust (DOCS l.104) | contra | PM §4.1 l.411-413. TS-05 |
| 8 | Each package is checked when downloaded and again before it runs (DOCS l.104) | ok | PM l.360, l.382-383; LOADER l.212-215; RUNTIME §3.6 l.712-718 |
| 9 | Modules are discovered in a catalogue and downloaded over the project's storage network (DOCS l.104) | partly | Catalog formats, acquisition and the Storage retrieval API are implementation-defined and must be documented (PM l.836, l.858-861, l.1438; SO-01, SO-02, PM-01 and NP-01, declined) |
| 10 | Typed clients are generated from each module's contract; "every module publishes its contract as a CDDL schema" (DOCS l.137, l.229) | partly | Only a realized provider discloses its documents (RUNTIME l.418, l.448); otherwise they are "embedded in generated bindings or supplied with the application" (INTERFACE l.3873). TS-06 |
| 11 | A module can describe its own contract at run time (DOCS l.229) | ok | RUNTIME §2.4 l.426-428, l.448-458 |
| 12 | The same call works in-process, across processes and across machines (DOCS l.34, l.228) | partly | INTERFACE l.47-50. Paths do not travel: "Co-location alone does not establish a shared filesystem namespace" (RUNTIME §12 l.3910, l.3917-3918). No order is required between events and method responses (l.1301; NE-02, declined). No suspend and resume (NL-05, declined). Cancellation reaches the provider in every mode (INTERFACE l.2143-2144) |
| 13 | An access policy set before the runtime starts decides which modules may call which, "for example only the modules that declare a dependency" (DOCS l.189) | partly | Default-deny policy is mandatory (RUNTIME l.1631-1632, l.1682-1683). No policy language (SO-04, declined). A dependency or `requires` entry is never authority by itself (l.739, l.915, l.1434), and `requires` names a contract, not a module, so the rule has to be written as policy; whether an undeclared route is even possible is unstated (TF-04) |
| 14 | Grants per method and per event, enforced before module code runs (DOCS l.215) | ok | RUNTIME l.860-867, l.1732; TRANSPORT l.973-979 |
| 15 | Each grant can expire and be revoked individually while the node runs (DOCS l.216) | ok | CA §6. New event deliveries are among the operations re-evaluated after a policy change (CA l.906-908) |
| 16 | Every access decision leaves an audit record (DOCS l.217) | partly | Retention is selected by policy (RUNTIME l.1756-1758, l.1769-1774; CA §9); "every" holds only under a policy that says so |
| 17 | Enrolling a user's runtime is an operation a service can be authorised to perform (DOCS l.218) | no | A scope exists (CA §3.4 l.376-377); "This specification defines no pairing exchange or general provisioning method" (RUNTIME l.1817-1818, l.2689; NR-02, declined) |
| 18 | No anonymous access; each runtime is enrolled with its own keys (DOCS l.220) | ok | TRANSPORT §8.4.1 l.1237-1254 |
| 19 | Pairing by six-digit code or single-use invite; certificates issued to each side (DOCS l.199, l.235) | no | RUNTIME l.1818-1819 (NR-02, declined) |
| 20 | One runtime exports a module, the other imports it under a local name (DOCS l.199-201) | partly | Export: `set_provider_export` (RUNTIME l.2215-2221, l.2816-2832). Import: a facade created by "protected deployment input or an authorized implementation-defined management operation" (l.1812; NR-03, declined). No alias (HC-12; NF-22, declined: the response says Core does not define universal role names or a resolver) |
| 21 | Mutual TLS 1.3 with pinned keys; no downgrade (DOCS l.199, l.236) | ok | TRANSPORT l.1235-1237, l.1249-1250, l.1219-1221 |
| 22 | Each connection opens with a single-use ticket that expires within seconds and is bound to that connection (DOCS l.235) | ok | TRANSPORT l.938-942, l.1042-1043 (at most 60 s), l.1286-1292 |
| 23 | A refused caller cannot tell whether the module exists (DOCS l.237) | ok | RUNTIME l.3157-3159; TRANSPORT l.1010-1014 |
| 24 | Both sides send the contract hash; a mismatch refuses the connection before any call (DOCS l.238) | ok | TRANSPORT §3.1 l.488, l.499-502, l.527-534 |
| 25 | When the remote runtime restarts "the import becomes ready again"; in-flight calls fail; missed events are not redelivered (DOCS l.201) | partly | Failure and no replay: TRANSPORT l.543-545, l.557, l.566-568. After a provider restart the old routes stay dead (RUNTIME l.3810-3811, l.1351); after a mere session loss the route may stay ready and be renewed with a fresh ticket (l.3474-3478). The consumer is told that its path ended (the terminal observer, l.1355-1356), but not when the provider is back, and nothing re-subscribes (NE-07, no response yet) |
| 26 | Subscriptions work across the network without polling (DOCS l.230) | partly | While a session lives (TRANSPORT l.544). No keepalive (NR-07, declined), no suspend and resume (NL-05, declined), one connection per route (TS-04) |
| 27 | Rate limits and connection scale are left to each deployment (DOCS l.222) | partly | Limits: finite, documented, chosen by the implementation (TRANSPORT §8.6 l.1343-1346, l.1357; NR-08, declined). Connection count is fixed by the transport profile, not by deployment: TS-04 |
| 28 | A local node module and a client module that proxies a remote node are interchangeable to callers, selected by which module is loaded (DOCS l.91; RFP l.615-621, l.811-819) | ok | COMMITMENT §4 l.635-637, §9.1 l.1188-1194. TS-07 explains how, and what is not defined |
| 29 | One instance of the node module per execution zone (RFP l.940-947) | partly | Several instances per name are allowed (RUNTIME l.2650-2651); `create_module_request` carries no alias and no configuration (l.2233-2236; HC-12) |
| 30 | Modules written in JavaScript or React Native (DOCS l.167; RFP l.98) | partly | Adapter inside the artifact (LOADER l.202-205). Script files are reachable only through an implementation-defined, documented convention (PM l.1189-1193), and there is "no executable-bundle or view-only realization form" (PM l.1200). TF-03 for the embedded engine's threads |
| 31 | A JSON-RPC server and client module pair for any module API (RFP l.804-819, l.843-854, l.871-873) | partly | Dynamic invocation exists (RUNTIME l.821-833). One client module cannot serve an API chosen by configuration: TS-02. No JSON projection of values: TS-03. The server acts under its own authority ("forwarding does not implicitly transfer the original consumer's authority", INTERFACE l.209; NA-09, declined), though it can read who called it (INTERFACE l.2181-2182) |
| 32 | The project's messaging network as the carrier for reaching a node (RFP l.856-863) | no | "Reachability through NAT, rendezvous, or a relay is deployment-specific unless a separately specified profile defines it" (TRANSPORT l.1200-1201; §9.3 l.1387-1388; NR-01, declined) |
| 33 | Android: one AAR per module, registered in-process (RFP l.611-613, l.831-841) | ok | `logos_runtime_register_binding` per module (RUNTIME l.4023-4026, l.4041-4050). TS-08 |
| 34 | The application itself serves calls (provider hosting) without being a packaged module (RFP l.484-486) | partly | Only as a statically registered module, before start (RUNTIME l.4069), with the complete native ABI (TS-08) |
| 35 | Host libraries for Kotlin, Swift, Go, Dart, Rust (DOCS l.160-169; RFP l.821-829) | partly | Only the C ABI is specified; for other languages "A separately specified language mapping can provide idiomatic bindings or a language-native authoring form" (BCP §6.1 l.477-480). TF-03 for runtimes that move work between OS threads |

## Appendix E — Catalog needs and where the specs stand

The twenty needs that recur across the module catalog, the earlier items that recorded them, and what
the current specs provide for each.

| Need | Earlier items | In the current specs |
|---|---|---|
| Results delivered as broadcast events correlated by an identifier, at per-message, per-block and per-chunk rates | NE-01, NE-02, NE-05, ND-03 | Provided for correlation. Invocation-scoped events reach only subscriptions on the caller's invocation path (RUNTIME l.1254-1271). A contract may not make an identifier that is available only in the final Response the sole means of recognising an earlier event (TRANSPORT l.848). For rates there is only a duty to document overflow behaviour (TRANSPORT l.815). |
| Late subscribers: subscribe before start, snapshot method plus transition events, history replay | NX-02, NE-02 | Partly provided. A watch method with invocation-scoped events can order one snapshot before the changes (TRANSPORT l.788-791). There is no retained-event log or replay (l.795-796). A subscription exists only while its route is ready (INTERFACE l.1461). |
| Long calls, long-polls, per-call deadlines from 2 s to unbounded, concurrent dispatch | HC-05, HC-06, NR-11, NR-12 | Provided. Prepared asynchronous calls with a per-call timeout, cancellation that reaches the provider, and deferred provider completion (INTERFACE l.2013-2014, l.2059, l.2144). An outstanding call does not occupy its route handle (RUNTIME l.1363-1364). |
| Streaming: chunk sessions, chunks as events, opaque stream handles, megabyte byte parameters | SO-09, ND-03, NR-08, NE-04 | No generic streaming or chunked-transfer facility (RUNTIME l.3894). Chunks can be addressed to one consumer as in the first row. A stream session is a resource of the contract (INTERFACE l.446). An oversized frame fails before it is sent (TRANSPORT l.383-389). See TP-06. |
| Host file paths as arguments and results | HC-08, NC-06 | No mechanism; the duty is on the contract. A contract that accepts a path "MUST define whose namespace it addresses and the applicable failure" (RUNTIME l.3918). See TP-03. |
| Bundled native libraries and resources | PM-11, NP-11 | Declined. There is no package-root directory or artifact lookup table; access to packaged resources follows an implementation-defined, documented convention, and native library dependencies go through the deployment's dynamic-linker integration (PM l.1189-1193). See PM-11 in section 1. |
| Process-global library state, one node per process, embedded language runtimes | NP-14, HC-02 | One implementation binding may be initialised more than once, each time as a distinct instance (INTERFACE l.1597-1599). Placement is selected by Runtime or deployment policy (RUNTIME l.1038). A module declaration has no field that asks for one instance per Runtime or for a process of its own (PM l.265-273). Process-global environment may not carry per-instance state (RUNTIME l.1466-1467). For a library's residual work after `_MODULE_destroy` see TF-03. |
| Module-owned sockets: peer-to-peer listeners, NAT mapping, HTTP servers, outbound HTTPS | SO-05 | A profile that permits platform access must define permission names and constraints for network connection, listening, destination and port access (CA l.394-398). No such profile exists, and the owner's response to SO-05 adds no permission registry. |
| A child process of a system binary; the OS keychain | NS-03, SO-05, NP-02 | Child process: there is no packaged executable form (PM l.1200), and spawning a binary that the deployment provides needs a profile-defined process permission (CA l.401), which does not exist. Keychain: a Credential Store specification is named (BCP l.199-200) and is not in the specification set (TL-02). |
| Configuration by method call, schema migration, environment variables, secrets in configuration | NC-01, NC-02, NC-05 | Partly provided. A schema change needs a replacement instance, with values transformed outside Core (CONFIG l.251-258). Reset is an explicit complete replacement (l.135). Credentials may not be in module configuration (l.57). Environment entries do not carry per-instance values (LOADER l.224-225, l.287; RUNTIME l.1466-1467). For configuration by method call see TP-01. |
| A node lifecycle inside the loaded module, readiness states, bounded shutdown | NL-01, NL-02, NL-12 | No Core hook. Application setup uses ordinary schema methods, and application readiness belongs to the module's own contract (RUNTIME l.647-648, l.661-662). Start-up and drain deadlines are supplied by the host or deployment (l.664, l.3835). Preparation is a declared method called before the administrative stop (l.3871). |
| Liveness probing of a provider by its consumers | NL-08, NE-03 | Provided for path loss. Every route handle has `observe_end`, which needs no additional grant (INTERFACE l.1474-1476). There is no deadline for detecting a silent connection failure (l.1495). Readiness "does not guarantee continuous progress of every application operation" (RUNTIME l.578), so application health is outside Core. |
| Logging: stderr discarded, module-owned log files, run-time level | HC-09 | No logging facility. "Optional diagnostic logging can be supplied through ordinary module contracts and deployment integration" (BCP l.550). |
| Process statistics of another module | NO-03 | Declined. The owner's response to NO-03 leaves resource usage to ordinary metrics or domain contracts and adds no Runtime usage method. |
| Data shapes: JSON in strings, dynamic maps, 128-bit integers as strings, `any`, in-band error envelopes | ND-01, ND-02, ND-05, ND-06, ND-07 | An external encoding such as JSON may be carried in a `bstr` or `tstr` under the contract's own interpretation (INTERFACE l.497). `any`, floats and unkeyed maps are not available to module schemas (l.491-493). Integer aliases stop at 64 bits (l.241, l.246). The owner's responses to ND-01, ND-05 and ND-07 add no wide-integer type, map type or common error record. |
| Secrets as parameters, results and environment values | NC-05 | Provided for requests and responses through `_sensitive` (INTERFACE l.213-214, l.395). Not provided for events (l.449). A commitment over a marked value can be tested against guessed values (SECURITY l.402). |
| No caller checks: any module can drive a provider that holds unlocked keys or runs a node | HC-03 | Provided. A provider reads the authenticated caller from the invocation context (INTERFACE l.2181-2182; RUNTIME l.886), and a module reads its own address through `get_self` (RUNTIME l.2553). |
| Presentation coupling: replicated objects, list models, calls from the view layer through a bridge, a view entry file named by a path in package metadata | NP-03, NX-02 | No presentation mechanism: presentation data planes and toolkit integration are outside the specification (RUNTIME l.3884), and there is no view-only realization form (PM l.1200). List models can be built from paginated snapshots with `inventory_changed` hints (RUNTIME l.3372, l.3416) and from `watch_installed_packages` and `operation_progress` (PM l.1712, l.1754). |
| Several instances per network or zone | HC-12 | Partly provided. `retire_module` removes an instance, and `list_modules` filters by `module` and `instance` (RUNTIME l.3556, l.3376). A consumer chooses among instances only by exact provider (l.3141); there is no role or alias. |
| Optional dependencies | PM-15, NE-07 | Declined: "Manifest dependencies are unconditional and apply to every variant" (PM l.1221-1223). A `requires` entry has no hard effect (TF-04). |

## Appendix F — What the check of the system contracts found clean

The results of the check described in section 3.2 that need no action.

- Size: Runtime Control 109 rules, Capability Authority 49, Module Loader 24, Package Manager 37
  contract rules and 14 manifest rules, Configuration 11. There are 48 methods (Runtime Control 28,
  Capability Authority 7, Loader 5, Package Manager 8) and 11 events.
- All blocks parse inside the supported subset (no `=>`, integer keys, group rules, generics, tags, bare
  `uint`/`int`/`any`, floats, controls other than `.size`).
- Every reference resolves. No rule is defined twice within or across specs.
- The hand-copied projections agree: the signer profile and its 48-byte key (RUNTIME l.2301-2304
  against PM l.494-502), the cursor type in three contracts, and the `observed_change` arms against the
  two engine events in CA.
- All 48 methods are proper request/response pairs with map-valued bodies. Every name obeys the lexical
  rules (one identifier segment after the namespace, COMMITMENT l.319).
- All 64 choices admit a structural selection plan under the COMMITMENT rules.
- Under the C mapping of INTERFACE §2.1-§2.5, 1,171 derived identifiers have no collision with one
  another, none when case is ignored, and none with the fixed names of INTERFACE §5.2.
- Every error-code string used in prose is a member of its enumeration; all Loader and Package Manager
  codes are both defined and used.
- The pinned manifest roots at PM l.364-365 reproduce, as do the common-schema root and its nine
  subtree roots (COMMITMENT l.719-728).
- All 98 section cross-references in RUNTIME resolve, and all 530 across the twelve files.
