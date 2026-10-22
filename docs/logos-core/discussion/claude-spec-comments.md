# Logos Core module specs — contradictions, gaps and missing definitions

Found while planning an independent implementation (logos-core-nim) of logos-lips
`draft/logos-core-module-specs` at commit `f4f83471` (2026-10-03; still the branch head on
2026-10-22), files `docs/logos-core/raw/spec-*.md`. Short names: TRANSPORT, INTERFACE, RUNTIME, CONFIG,
LOADER, PM (package manager), CA (capability authority), SECURITY, BCP (system BCP), COMMITMENT, HASH,
cdCDDLe. Line numbers (`l.N`) refer to the files at that commit.

This document is only about the specs. Implementation choices that the specs rightly leave to
implementers (language, libraries, build, CI, repository layout, how existing modules are ported) are
not here; they are in `DECISIONS.md`, which this document cross-references as `[Gn]` / `[Dn]`.

Every item was checked against all twelve documents before being listed: an item appears here only if
no spec text settles it. Items that looked like gaps but turned out to be answered are in the appendix,
because the answers were hard to find.

Each item gives:
- **Specs** — the sections and lines involved.
- **Issue** — what the text says and what is missing or inconsistent.
- **Impact** — why an implementation cannot proceed without a choice, or why two implementations would
  diverge.
- **Our interim choice** — what logos-core-nim does until the spec settles it.
- **Suggested resolution** — a proposal for the spec text.

## Summary

| Part | Count |
|---|---|
| 1. Contradictions | 12 |
| 2. Gaps (spec silent or ambiguous) | 74 |
| 3. Choices an implementation had to make that the specs should probably own | 10 |
| Appendix: answered, but hard to find | 9 |

Still open on our side, pending the spec author: **G5** (LGX `storage`/`object`), **G49**
(`publish_events`), **G93** (module access to its own artifacts).

---

## Part 1 — Contradictions

### C-01 — Unqualified common names `[G3]`
- **Specs:** COMMITMENT §5 l.697-698 vs INTERFACE §1.1, §5.3; BCP §6.1 l.388-390.
- **Issue:** COMMITMENT §5 says unqualified common names are "interpreted as names in that namespace",
  so `error_code` would mean `logos.error_code`. INTERFACE and BCP §6.1 require complete documents with
  explicit qualified names ("interoperability … only when the tool emits the complete ordinary CDDL
  documents with explicit qualified names").
- **Impact:** one implementation accepts a schema another rejects; schema roots differ if names resolve
  differently.
- **Our interim choice:** reject unqualified common names.
- **Suggested resolution:** state in COMMITMENT §5 that common definitions are referenced only by their
  qualified `logos.` names.

### C-02 — Namespace depth: COMMITMENT allows what INTERFACE cannot represent `[G4]`
- **Specs:** COMMITMENT §3.1 step 2 (the namespace must be a proper prefix of every name; nothing
  forbids extra segments) vs INTERFACE §2 l.537 (every accepted schema set MUST be representable in both
  C forms), §3.8 (CDDL -> C -> CDDL MUST reproduce the same model).
- **Issue:** `storage.sub.thing` beside `storage.x` projects to `logos_storage_sub_thing_t`, which maps
  back to `storage.sub_thing`; a bare method name `sub.read` would contain a dot.
- **Our interim choice:** reject declarations nested deeper than the namespace.
- **Suggested resolution:** COMMITMENT §3.1 step 2: every declaration name is `<namespace>.<identifier>`
  with exactly one segment after the namespace.

### C-03 — Is the C->CDDL reverse mapping a conformance requirement? `[G139]`
- **Specs:** INTERFACE Abstract l.22-30 (the mapping is total; a conforming implementation MUST recover
  the same model from either representation), §3, §3.8 l.1876-1891, §3.9 (normative cases) vs BCP §6.1
  l.372 ("Code generation is an implementation technique rather than a conformance requirement"),
  l.412.
- **Impact:** decides whether an implementation without a C parser can claim INTERFACE conformance.
- **Our interim choice:** implement and claim the reverse mapper.
- **Suggested resolution:** either define an INTERFACE conformance class that excludes C-first
  authoring, or reword BCP §6.1 so it does not read as contradicting INTERFACE §3.

### C-04 — Optional tag member vs identical headers `[G64]`
- **Specs:** INTERFACE §2.3 (a generator MAY omit a tagged choice's tag member) vs §2 intro (any two
  implementations MUST produce identical header sets modulo whitespace, comments, include layout and
  guards).
- **Our interim choice:** always emit the tag member.
- **Suggested resolution:** remove the MAY, or exclude the tag member from header identity.

### C-05 — Generated helper names `[G71]`
- **Specs:** INTERFACE App A.4/A.5 (`logos_<module>_publish_<ns>_<event>`,
  `logos_<ns>_invoke_<method>(route, …)`) vs RUNTIME §4.1 (`logos_storage_exists(h, …)`), both informative.
- **Impact:** low (informative), but generated bindings from different generators will not link against
  each other's examples.
- **Our interim choice:** INTERFACE A.4/A.5 names, never exported from module artifacts.
- **Suggested resolution:** align the RUNTIME §4.1 example with INTERFACE App A.

### C-06 — Socket path layout `[G58]`
- **Specs:** RUNTIME §1.3 (the module name drives `<runtime-dir>/logos_<name>.sock`, one per name) vs
  TRANSPORT §8.2 (Runtime creates a 0700 directory per instance, binds the listener and hands it to the
  Module Host; several instances of one module may exist).
- **Impact:** RUNTIME §1.3 read literally allows only one hosted instance per module name; sun_path limits
  (104 bytes on macOS, 108 on Linux) are not considered.
- **Our interim choice:** `<short base>/<instance dir 0700>/logos_<name>.sock`; placement fails if the path
  does not fit.
- **Suggested resolution:** make RUNTIME §1.3's path informative or per-instance, and mention the sun_path
  limit.

### C-07 — Shared artifacts across module declarations `[G29]`
- **Specs:** PM §4 l.341 (declarations "MAY reference the same schema or default artifact") vs §8 (an
  artifact assigned to more than one declaration is `invalid-package`); §4 l.363 (ordering rules with no
  error value named); no check precedence anywhere.
- **Our interim choice:** shared schema/default artifacts allowed, shared implementation artifacts
  rejected; ordering violations `invalid-package`; precedence limits > structure > signature > commitment
  > provenance > schema > platform > artifact hashes.
- **Suggested resolution:** carve the §4 exception into §8, name the ordering error, define precedence.

### C-08 — `unsupported-strategy` permits the downgrade it is meant to prevent `[G28]`
- **Specs:** LOADER §6 l.395-396, l.423 (fail rather than substitute a weaker strategy, placement or
  isolation), §10 l.612 (`unsupported-strategy` lets Runtime choose another strategy or placement),
  l.615-616 (initialization failures are `realization-failed`); TRANSPORT l.960 (no isolation downgrade).
- **Issue:** the only error value for "refused a weaker substitute" is defined as permission to try
  another strategy.
- **Our interim choice:** use `unsupported-strategy`, but Runtime never reselects a weaker strategy or
  placement after it; a disallowed init result is `realization-failed`.
- **Suggested resolution:** state in §10 that `unsupported-strategy` never licenses a weaker choice, or
  add a distinct value.

### C-09 — "Runtime-known" instances vs remote forwarding `[G81]`
- **Specs:** CA §2 ("Every module-instance address named by this contract MUST resolve to one
  Runtime-known module instance"; every decision identifies its consumer) vs RUNTIME §9 l.1603-1636 (a
  target Runtime authorizes operations "for the consumer" asserted by an enrolled source Runtime, i.e. an
  instance the target does not own).
- **Impact:** read strictly, the target's CA can neither record a decision nor issue a grant for a remote
  consumer, which makes the specified remote forwarding unusable.
- **Our interim choice:** a consumer accepted through an enrolled remote Hello is recorded and counts as
  Runtime-known.
- **Suggested resolution:** CA §2 to say "known to the Runtime, either as a local instance or as a
  consumer authenticated through an enrolled source Runtime".

### C-10 — The Loader may be out of process, but its private handoffs cannot leave the process `[D14]`
- **Specs:** RUNTIME Abstract note (Runtime and Loader "need not share a process, binary, or
  implementation-private API"); LOADER §5 (handoffs: listener descriptors, process-local bindings), §5.4
  l.330 (channel setup and descriptor transfer are implementation-defined); the Loader contract is CBOR.
- **Issue:** file descriptors and process-local bindings cannot travel over the CBOR Loader contract, so
  an out-of-process Loader needs an undefined side channel.
- **Our interim choice:** the Loader is linked into the Runtime host; handoffs use an in-process table.
- **Suggested resolution:** either state that hosted handoffs require Runtime/Loader co-location, or
  define the descriptor-transfer channel.

### C-11 — Normative keywords inside informative sections `[G118]`
- **Specs:** INTERFACE App A.3 l.2934-2981 (uppercase MUSTs under a section titled "Informative");
  SECURITY (category Informational) l.230, l.441.
- **Our interim choice:** claim and test them as normative.
- **Suggested resolution:** move the requirements into normative sections, or lower-case them.

### C-12 — Layer direction: Runtime conformance depends on a higher layer's formats
- **Specs:** BCP §1 l.50-52 ("a higher layer may consume identities and records from a lower layer,
  while conformance to a lower-layer specification does not require a higher-layer module contract") vs
  BCP §5.3 l.297 (call evidence is "Mandatory for every conforming Runtime"; "The format is fixed by
  LOGOS-MODULE-CAPABILITY-AUTHORITY"); RUNTIME §9 l.1585-1603 (Runtime must produce the CA `call` audit
  record, which requires a CA `decision_id` and scope, even with internal policy).
- **Issue:** a layer-2 conformance claim needs record types defined in a layer-3 spec. It is a record
  format, not the CA module contract, so the letter of BCP §1 holds, but the stated dependency direction
  does not.
- **Our interim choice:** none needed; the Runtime implements the CA record types.
- **Suggested resolution:** move the audit-record and call-evidence types into a lower-layer document
  (e.g. RUNTIME or a shared types spec), or say explicitly that RUNTIME depends on them.

---

## Part 2 — Gaps

### 2.1 Normative text in general

#### GN-01 — Only cdCDDLe cites BCP 14 `[G117]`
- **Specs:** cdCDDLe §4 l.87-88 is the only BCP 14 (RFC 2119/8174) boilerplate; the other eleven specs
  use uppercase MUST/SHOULD/MAY without it, and 55 lines use lowercase must/should.
- **Impact:** without the boilerplate, whether uppercase keywords are normative is formally undefined,
  and lowercase modals are ambiguous.
- **Our interim choice:** uppercase = BCP 14 everywhere; each lowercase modal is tracked and either tested
  or triaged with a written reason.
- **Suggested resolution:** add the RFC 8174 boilerplate to every spec; uppercase or rephrase the
  lowercase modals that are meant normatively.

### 2.2 Commitment model, hash profile, cdCDDLe

Context: these decide every schema and value root on the wire (TRANSPORT §4.1). No vector exercises
identity assignment through references, aliases or leaf-bodied declarations: HASH App B uses synthetic
identities and COMMITMENT App A/B use placeholders. Each gap below is invisible to a single
implementation and breaks interoperability between two.

#### CM-01 — Value identity under alias chains `[G1]`
- **Specs:** COMMITMENT §8 (one-hop rule: a local reference adds no node; the containing node keeps the
  referring location, the child carries the referenced declaration's identity), §9.2; HASH §7.3.
- **Issue:** chains such as `a.x = a.y`, `a.y = tstr` are not addressed.
- **Our interim choice:** the innermost declaration (`a.y`), applying the one-hop rule at each step.
- **Suggested resolution:** state the chain rule and add a vector.

#### CM-02 — Schema root of payloads below an imported reference `[G2]`
- **Specs:** COMMITMENT §8, §9.3; HASH §5 ("needed to interpret the node"), §7.4 (reference-value payload;
  every payload's field 1 is a schema root).
- **Issue:** whether field 1 under a reference-value node is the outer value's root or the referenced
  schema's root. Affects every value containing `logos.schema_commitment`, `logos.error_detail` or any
  Runtime Control record.
- **Our interim choice:** the referenced schema root.
- **Suggested resolution:** state it in HASH §7.4 and add a vector with an imported reference.

#### CM-03 — Referencing common callable declarations `[G6]`
- **Specs:** INTERFACE §1.1, §1.7 (imply named types only); COMMITMENT §5 (silent).
- **Issue:** may a schema node reference `logos.schema_request` / `logos.schema_response`?
- **Our interim choice:** no; common named types only.
- **Suggested resolution:** one sentence in COMMITMENT §5.

#### CM-04 — What a field or tuple-position path discloses `[G7]`
- **Specs:** COMMITMENT §9.4; HASH §8, App B.1 (list elements disclose the inner value; the empty path the
  whole value).
- **Our interim choice:** the inner value node, as for list elements.
- **Suggested resolution:** state the disclosure target per segment kind in HASH §8.

#### CM-05 — Is a choice-arm segment required to cross a choice? `[G8]`
- **Specs:** COMMITMENT §9.4 (defines the segment; does not say it is mandatory).
- **Our interim choice:** required.
- **Suggested resolution:** state it.

#### CM-06 — Literals counted by the choice selection plan `[G9]`
- **Specs:** COMMITMENT §3.1 (selection plan; table l.490-503).
- **Issue:** when checking arms are distinguishable, do only literal constraints on the arm's top-level
  observed value count, or every literal reachable inside the arm?
- **Our interim choice:** the top-level observed value only (following references and nested choices).
- **Suggested resolution:** state it with an example.

#### CM-07 — Literal-element lists and packing `[G119]`
- **Specs:** HASH §4 l.162-165 (packable kinds bool, uint8…int64; tstr, bstr, reference, choice and
  composite lists excluded; literals not mentioned).
- **Our interim choice:** `[* true]` / `[* 5]` are packable (a literal's scalar kind is bool/uint64).
- **Suggested resolution:** list literals explicitly.

#### CM-08 — Where the verified-view verifier gets its schema `[G120]`
- **Specs:** HASH §8, §9; INTERFACE §5.3 (schema text is untrusted).
- **Our interim choice:** caller-supplied; root recomputed and compared with the view's root.
- **Suggested resolution:** state the verifier's inputs in HASH §8.

#### CM-09 — `logos.schema.reference` is never produced `[G122]`
- **Specs:** COMMITMENT §6, HASH §7.2 define the domain; no spec object uses it.
- **Our interim choice:** implemented and unit-tested only.
- **Suggested resolution:** say what produces it, or remove it.

#### CM-10 — `0*` and `*1` occurrence spellings `[G10]`
- **Specs:** cdCDDLe §5.1 l.172 (only `?` on map members and `*` on array members are supported).
- **Issue:** equivalent spellings of supported occurrences are not mentioned.
- **Our interim choice:** reject.
- **Suggested resolution:** say "reject" or "normalize" explicitly.

#### CM-11 — String-escape grammar `[G11]`
- **Specs:** cdCDDLe §5 l.125 (RFC 8610 parse semantics), l.455; RFC 9682 updated CDDL's escapes.
- **Our interim choice:** RFC 8610.
- **Suggested resolution:** pin the grammar version explicitly.

#### CM-12 — Named range bounds `[G12]`
- **Specs:** cdCDDLe §5.1 l.163 (inclusive integer ranges with `..`; RFC 8610 allows names as bounds).
- **Our interim choice:** reject; literal bounds only.
- **Suggested resolution:** state it.

#### CM-13 — Non-flattened nested choices in schema-as-data `[G13]`
- **Specs:** cdCDDLe §7.2 / l.332 (canonicalization flattens), §10 (decoder rejection list does not
  include this case).
- **Our interim choice:** the decoder rejects it.
- **Suggested resolution:** add it to the §10 rejection list.

#### CM-14 — Scope of the cdCDDLe document for a Logos schema `[G14]`
- **Specs:** cdCDDLe §8; COMMITMENT §5.
- **Issue:** whether prelude, common and supporting definitions are merged into the document or stay as
  references.
- **Our interim choice:** authored rules only; the others stay type references resolved against an
  explicit scope.
- **Suggested resolution:** state it in COMMITMENT §5 or cdCDDLe §8.

### 2.3 Interface: encoding and the C mapping

Context: INTERFACE §2 requires identical header sets across implementations and makes the exported
signatures mandatory (§2.4), so each gap here is an interoperability gap. Runtime Control (RUNTIME
l.1814, a tuple-arm choice) and the CA (l.1001, `[* bstr]` in a list position) use shapes the C mapping
does not define.

#### IF-01 — Floats inside opaque payloads `[G38]`
- **Specs:** INTERFACE §4.4 (deterministic CBOR incl. float rules), §1.7 (schemas cannot declare floats),
  §4.5 (reasons); TRANSPORT §2.3 (schema-free envelope checks).
- **Issue:** a float inside params/result/data: profile violation (ProtocolError + close) or schema
  mismatch (correlated INVALID_PARAMS)?
- **Our interim choice:** schema mismatch; a non-shortest float is `non-deterministic-cbor`.
- **Suggested resolution:** state which layer rejects floats.

#### IF-02 — Value nesting depth `[G59]`
- **Specs:** INTERFACE §2.3, §3.9.3, COMMITMENT l.427-428 (recursion is legal); no depth bound anywhere;
  INTERFACE §4.5 (closed reason list); SECURITY §10 l.367 (residual risk).
- **Issue:** a 16 MiB frame can nest ~16 million levels; a depth limit has no INVALID_PARAMS reason.
- **Our interim choice:** iterative processing and a configurable cap (default 1024); over-cap =
  INVALID_PARAMS without detail.
- **Suggested resolution:** a minimum supported depth, plus a reason value for exceeding the deployment's
  limit.

#### IF-03 — C form of inline tuples, lists and unbounded bstr as choice arms or list elements `[G62]`
- **Specs:** INTERFACE §2.3; COMMITMENT l.496 (`[uint64] / [uint64, uint64]` is valid); used by
  RUNTIME l.1814 and CA l.1001.
- **Our interim choice:** path-named synthetic types (`…_arm_<i>`, `…_list_item`); a tuple arm is a struct
  of `item_<i>` fields; list/bstr become an adjacent ptr+len pair.
- **Suggested resolution:** define these forms in §2.3.

#### IF-04 — Choice-of-maps event bodies in C `[G63]`
- **Specs:** INTERFACE §1.5 (allowed) vs §2.5 (maps only map-bodied events).
- **Our interim choice:** a wrapper struct with a kind tag and a union, as §2.4 rules 4-5 do for requests.
- **Suggested resolution:** add the event form to §2.5.

#### IF-05 — Literal macro spelling `[G65]`
- **Specs:** INTERFACE §2.3 ("the exact C scalar literal"), §3.5.
- **Our interim choice:** `UINT64_C(…)`, `INT64_C(…)`, INT64_MIN as `(-INT64_C(9223372036854775807) - 1)`,
  `true`/`false`, C strings with `\xNN` escapes.
- **Suggested resolution:** specify the spelling (header identity depends on it).

#### IF-06 — `has_` adjacency for optional inline tuples `[G66]`
- **Specs:** INTERFACE §3.4.
- **Our interim choice:** `has_<f>` immediately before the first expanded member.
- **Suggested resolution:** state it.

#### IF-07 — Ownership of recursive typed outputs `[G67]`
- **Specs:** INTERFACE §2.7 (each dynamic output freed with `_free`; recursive `const B*` edges not
  addressed).
- **Our interim choice:** one allocation per node, freed children first.
- **Suggested resolution:** state the allocation unit and free order.

#### IF-08 — Freeing typed route-helper outputs `[G68]`
- **Specs:** INTERFACE §2.7 ("the side that decodes … owns and frees its own decoded allocations"),
  App A.5; no API named.
- **Our interim choice:** generated consumer-side free helpers.
- **Suggested resolution:** name the consumer-side free function in App A.5.

#### IF-09 — Symbol collisions across modules `[G69]`
- **Specs:** INTERFACE §1.3, §2.1; RUNTIME §1.3 (`_call_` / `_publish_` reserved in module names).
- **Issue:** module `foo` + namespace `call` + method `surface` and module `foo_call` both derive
  `logos_foo_call_call_surface`; names ending in `_call`/`_publish` are not covered.
- **Our interim choice:** reject module names ending `_call`/`_publish` and namespaces `call`/`publish`.
- **Suggested resolution:** extend the reservation in RUNTIME §1.3 / INTERFACE §1.3.

#### IF-10 — Where consumers get `schema_cbor` for `materialize_route` `[G70]`
- **Specs:** INTERFACE §5.2; RUNTIME §4.2 (helpers "can carry this expectation by construction");
  `route_record` carries only the commitment.
- **Our interim choice:** generated bindings embed it; generic clients use `describe_provider`.
- **Suggested resolution:** name the expected sources.

#### IF-11 — Header declaration order `[G72]`
- **Specs:** INTERFACE §2.1 (orders types, fields and arms, not macros, lifecycle symbols and typedefs
  relative to provider declarations).
- **Our interim choice:** forward declarations, types, literal macros by name, provider functions by
  qualified name, lifecycle symbols.
- **Suggested resolution:** complete the §2.1 ordering.

### 2.4 Error codes the specs require but do not assign

Context: INTERFACE §5.1 fixes a closed registry; only INVALID_PARAMS may carry detail (reasons
malformed-cbor, non-deterministic-cbor, schema-mismatch); RUNTIME §3.4 l.633 reserves NOT_READY for
"Runtime-owned lifecycle, provider, or route readiness"; execution-boundary invariance requires the same
code in every mode. Many MUST-reject rules name no code, so implementations will diverge and conformance
tests cannot assert values.

| ID | Condition | Specs | Our interim code |
|---|---|---|---|
| EC-01 `[G18]` | `request_key` reused with different fields | RUNTIME §9.3 | INVALID_PARAMS, no detail |
| EC-02 `[G19]` | stale expected execution / permission / configuration revision | RUNTIME §9.1, §9.3; CONFIG; l.633 | INVALID_PARAMS, no detail (l.633 rules out NOT_READY) |
| EC-03 `[G20]` | lifecycle preconditions: start while stopping, recover outside its states, renew a closed/failed route | RUNTIME §9.3 | NOT_READY |
| EC-04 `[G21]` | `apply_configuration` cannot succeed (the response has no failure arm) | CONFIG §8; RUNTIME §9.3; l.633 | readiness NOT_READY; no staged record / non-live binding INVALID_PARAMS; module rejects or indeterminate MODULE_ERROR |
| EC-05 `[G22]` | call through a closed/failed vs revoked/expired route handle | RUNTIME §4.1; INTERFACE §5.2 | NOT_READY vs NOT_AUTHORISED, at the Runtime boundary in every mode |
| EC-06 `[G23]` | call into a stopping provider; call on an invalidated RC binding | RUNTIME §3.4 | NOT_READY (in-flight transport calls keep TRANSPORT_ERROR) |
| EC-07 `[G24]` | required Loader / Package Manager unavailable | RUNTIME "System Service Availability" (CA case = deny, l.1516) | NOT_READY |
| EC-08 `[G25]` | RC vtable fails its checks; `materialize_route` fails; `connect_remote` with a non-remote endpoint | INTERFACE §5.2 | VERSION_MISMATCH; the route-establishment code; INVALID_PARAMS |
| EC-09 `[G26]` | listener / export / enrollment validation failures | RUNTIME §9.3 l.2991-3017 (unknown or hidden targets are already NOT_AUTHORISED, l.433, l.2774-2776) | INVALID_PARAMS |
| EC-10 `[G27]` | values of `route_failure.code` and `permission_settings_state.failure` (free `tstr` 1..64, yet l.2864-2871 and l.2937-2943 require distinguishing a dozen classes) | RUNTIME §9.3 | a fixed kebab-case list, one value per class |
| EC-11 `[G60]` | binding symbol defects beyond the l.3436 list | RUNTIME §13.3, §13.4 l.3470 | INVALID_PARAMS at `register_binding` |

- **Suggested resolution:** an error-mapping table in RUNTIME §9.3 (and §13.4) covering every MUST-reject
  rule, plus normative value lists for the two failure strings.

### 2.5 Transport

Context: TRANSPORT fixes directions, envelope checks (§2.3), Hello order and codes (§3.1, §8.3) and one
receiver leniency (§6, unknown Cancel ids are ignored). It ships no byte vectors. Receiver behaviour for
the following cases is unspecified, so two implementations can disagree on whether a session survives.

#### TR-01 — Wrong-direction or pre-Hello messages `[G30]`
- **Specs:** §1.2, §1.4 (directions); §2.3 (direction and state are not envelope checks); §3.3 (only a
  second Hello is covered); RUNTIME §6.2.
- **Our interim choice:** ProtocolError INVALID_PARAMS, then close.
- **Suggested resolution:** add direction and connection state to §2.3.

#### TR-02 — Uncorrelated Response, SubscriptionResult or Event `[G31]`
- **Specs:** §1.4, §5.1, §6; RUNTIME §9.3 (timeouts are implementation policy, so late replies to abandoned
  calls are legitimate).
- **Our interim choice:** late replies to ids the caller abandoned are dropped; never-sent or duplicate ids
  get ProtocolError INVALID_PARAMS and close.
- **Suggested resolution:** define receiver rules, distinguishing abandoned from never-issued ids.

#### TR-03 — Subscription id misuse `[G32]`
- **Specs:** §5.1 (exactly one SubscriptionResult per syntactically valid control op; no code for reused or
  unknown ids; no rule for overlapping operations).
- **Our interim choice:** a failed SubscriptionResult with INVALID_PARAMS, state unchanged, in all three cases.
- **Suggested resolution:** name the code and the overlap behaviour.

#### TR-04 — Non-empty Hello response token `[G33]`
- **Specs:** §3.1 (validated "under the profile's response rules", no code); §8.1, §8.2, RUNTIME §9 (all
  profiles require it empty).
- **Our interim choice:** ProtocolError NOT_AUTHORISED, then close.
- **Suggested resolution:** name the code in §3.1.

#### TR-05 — When the provider Hello happens, and what the consumer sees when it fails `[G34]`
- **Specs:** §3.1, §3.2, §8.1.1 (tickets live ≤ 60 s); INTERFACE §4.6; RUNTIME §4.1, §9.
- **Our interim choice:** inside `materialize_route`, which returns the peer's code (NOT_AUTHORISED,
  VERSION_MISMATCH).
- **Suggested resolution:** state it in RUNTIME §4.1.

#### TR-06 — Expiry or revocation on a live session `[G35]`
- **Specs:** §8.1 (reject new operations, then end subscriptions and the session); CA §8; RUNTIME §9.3
  (audit distinguishes the cause). The on-wire signal is unspecified.
- **Our interim choice:** new Requests get NOT_AUTHORISED; then ProtocolError NOT_AUTHORISED and close.
- **Suggested resolution:** define the signal.

#### TR-07 — Schema-invalid response-ok or Event `[G36]`
- **Specs:** §4.1; SECURITY §8 (fail closed).
- **Our interim choice:** ProtocolError INVALID_PARAMS, close, the waiting caller gets TRANSPORT_ERROR.
- **Suggested resolution:** state it in §4.1.

#### TR-08 — Precedence of the schema check and the commitment check `[G37]`
- **Specs:** §4.1 (validate, recompute, compare — no explicit precedence, unlike §8.3 for Hello); RUNTIME
  §4.1 (validation and hashing may be combined).
- **Issue:** a Request that is schema-invalid and has a wrong subtree root could get response-err
  INVALID_PARAMS (session kept) or ProtocolError and close.
- **Our interim choice:** commitment first: any root mismatch closes the session.
- **Suggested resolution:** define the precedence.

#### TR-09 — No named equivalent mechanism for Windows `[G107]`
- **Specs:** §8.2 l.947, §9.1 l.1135 (unix-stream mandatory where AF_UNIX exists, including Windows 10
  1803+), l.956 (listener transfer), l.967 ("equivalent" peer-identity mechanism); "0700 on POSIX
  filesystems" does not cover NTFS.
- **Issue:** Windows AF_UNIX has no socketpair or SCM_RIGHTS, and PID-based peer checks race with PID
  reuse; the spec names no equivalents.
- **Our interim choice:** `SIO_AF_UNIX_GETPEERPID` plus a token-SID comparison while holding the peer's
  process handle; an owner-only DACL directory; listener transfer by handle inheritance.
- **Suggested resolution:** a Windows subsection in §8.2.

### 2.6 Runtime

#### RT-01 — No defined way for a command-line tool to reach a running Runtime `[D13, G83]`
- **Specs:** RUNTIME Terminology (every consumer is a module instance; humans are outside the model), §9
  l.1465, §9.3 l.1825 (remote listeners are tls-tcp/quic only); BCP §2 (a CLI participates as a module
  instance), §5.1, §7 (informative "protected deployment activation"); TRANSPORT §3.1, §8.4.
- **Issue:** the only specified way for another process to call Runtime Control is remote Runtime Control
  with mTLS and enrollment. A shell command cannot be "realized by the Loader", and the activation/
  presentation hop of BCP §7 is informative and undefined.
- **Our interim choice:** logosctl embeds a small source Runtime and uses remote Runtime Control over
  loopback mTLS; argv/stdio reach its module through an implementation-local presentation handoff.
- **Suggested resolution:** a normative local activation profile (e.g. an owner-only local endpoint that
  binds a shell invocation to a Loader-realized module instance), and a minimal presentation/terminal
  profile.

#### RT-02 — Engine-originated calls have no consumer `[G48]`
- **Specs:** RUNTIME Terminology; §9 l.1499 (startup realizes orchestration), l.1640 (internal
  coordination "MUST NOT be represented using a fabricated consumer reference"), §10.2; BCP §5.1;
  TRANSPORT §3.1 (a Hello needs a consumer-bound ticket).
- **Issue:** realizing the orchestrator at bootstrap, releasing realizations at shutdown and calling the
  CA's `evaluate` are done by the engine for no module, which works only if those services are in-process.
- **Our interim choice:** the Loader and CA are always direct and in-process; the engine calls them through
  its enforcement boundary under bootstrap policy.
- **Suggested resolution:** state that system services the engine itself calls must be direct, or define
  the authority basis for engine-originated calls.

#### RT-03 — No name for the orchestration module `[G53]`
- **Specs:** RUNTIME §1.3, INTERFACE §1.3 (`logos_` reserved for Logos-defined runtime and system
  modules); BCP §5 names only PM, Loader, CA and Runtime Control.
- **Our interim choice:** `logos_orchestrator` (takes the reserved prefix).
- **Suggested resolution:** assign a name or say the role's name is deployment-chosen and unreserved.

#### RT-04 — Choosing an installed package for a module name `[G55]`
- **Specs:** RUNTIME §9.3 (`create_module_request` is closed `{request_key, module}`; "Runtime MUST select
  one accepted declaration … under active policy or fail"); PM §5, §11 (several versions installable; two
  packages may declare one module); CA §3.3 (module_execution_scope may carry package/version).
- **Our interim choice:** the highest installed normal release; two different packages declaring the
  module fail without disclosure; explicit pins via a CA module_execution_scope grant.
- **Suggested resolution:** a default selection rule, and a way to request a specific package@version.

#### RT-05 — Hosts orphaned by a failed Loader `[G56]`
- **Specs:** LOADER §7 (realization ids scoped to the issuing provider; no adoption rule); RUNTIME §10.1,
  §10.2 step 5.
- **Our interim choice:** the host terminates them, their instances go to `error`, orchestration recovers
  them through the new Loader.
- **Suggested resolution:** an adoption-or-termination rule for realizations of a replaced Loader.

#### RT-06 — No operation to move an instance to a newer package `[G92]`
- **Specs:** RUNTIME §9.3 l.3056-3059 (the retained selection is never inferred from inventory or a newer
  package), l.3072 (recovery preserves it), l.1317 (reusing state across identities is a policy decision).
- **Issue:** after a package update, nothing lets an existing instance (and its state) move to the new
  version; the only path is a new instance.
- **Our interim choice:** an explicit upgrade: stop, create a new instance selected per RT-04, bind it to
  the old instance's state assignment, start.
- **Suggested resolution:** an RC upgrade/reselect operation, or a documented upgrade procedure with
  state handover.

### 2.7 Capability Authority

#### CA-01 — Losing execution authorization while running `[G46]`
- **Specs:** CA §3.3, §8 (terminate dependent sessions when continued use would exceed authority; may keep
  them open while a fresh decision is fetched); RUNTIME §10.1 (stops caused by permission withdrawal keep
  intent).
- **Issue:** whether to stop at once or re-evaluate first, and what to do if evaluation fails.
- **Our interim choice:** stop immediately, intent preserved.
- **Suggested resolution:** state the rule in CA §8.

#### CA-02 — Consumer attributes for an external CA `[G47]`
- **Specs:** CA §2; RUNTIME l.1528 (policy may use attributes derived from authenticated context); no
  field carries them.
- **Our interim choice:** the CA reads them through its own Runtime Control binding under bootstrap grants.
- **Suggested resolution:** define how attributes reach the CA.

#### CA-03 — Meaning of `publish_events` / `publish-event` `[G49]`, OPEN
- **Specs:** CA §3.1 (`route_access.publish_events`; action `publish-event`); TRANSPORT §1.4 (only the
  callee sends Events).
- **Issue:** there is no consumer-to-provider event path for these to authorize.
- **Our interim choice:** stored and committed, never enforced.
- **Suggested resolution:** define or remove.

#### CA-04 — Call-evidence proof arrays `[G50]`
- **Specs:** CA §9.1 (per-side order and duplicates unspecified; l.1049 requires at least one proof when
  `proofs` is present); l.110-115 (CA's set-valued arrays are strictly ascending).
- **Our interim choice:** ascending deterministic-CBOR order of semantic path, no duplicates; `proofs`
  omitted when empty.
- **Suggested resolution:** state the ordering.

#### CA-05 — Ordering and cursors of `list_grants` and `query_audit` `[G51]`
- **Specs:** CA §6, §9 (limits only).
- **Our interim choice:** grants by grant-id bytes; audit newest first; snapshot cursors expiring after 10
  minutes; since inclusive, until exclusive.
- **Suggested resolution:** define order, cursor lifetime and bounds.

#### CA-06 — Call audit under a route-level decision `[G52]`
- **Specs:** CA §9 (a call record needs `decision_id` and a scope); RUNTIME §9 (calls are authorized by the
  route's decision).
- **Our interim choice:** the decision that established or last renewed the route.
- **Suggested resolution:** state it.

#### CA-07 — Exporting call evidence `[G115]`
- **Specs:** CA §9.1 l.988-990 (no query method or batch format), l.1072 (disclosure follows
  `query_audit`), l.1078.
- **Our interim choice:** containers stay in the Runtime's audit store; an owner-only host export.
- **Suggested resolution:** an export or query method for evidence containers.

### 2.8 Package Manager

#### PM-01 — Meaning of the LGX `storage` and `object` fields `[G5]`, OPEN
- **Specs:** PM §5 (`storage: tstr .size(1..128)`, `object: bstr .size(1..4096)`), §6 l.786, §4.5 l.583
  ("the Logos Storage provider named by `storage`"), §13; INTERFACE §1.1 l.115-119 (the storage examples
  are not the real Storage interface).
- **Issue:** nothing defines what `storage` names (a provider id, a module name, a deployment label), how
  `object` is encoded (binary or text CID), or which Storage method the PM calls.
- **Our interim choice:** none; tests run against a fake Storage provider.
- **Suggested resolution:** define the locator and the Storage fetch contract (see SO-02).

#### PM-02 — Only Storage and Nix sources; no way to obtain the first Storage provider `[D17]`
- **Specs:** PM §5 (closed `package_source`), §7 l.808 (`unsupported-source`), §13; RUNTIME §3.6 step 2
  and SECURITY §3.1 l.142 (protected bootstrap input may supply digests); BCP §5.5.
- **Issue:** an LGX package can only come from Logos Storage, so the Storage module itself must arrive
  some other way; the spec allows protected bootstrap input but does not describe the expected
  bootstrap. There is no local-file or URL source for development or air-gapped installs.
- **Our interim choice:** storage and the system services ship as protected bootstrap input; everything
  else comes from Storage.
- **Suggested resolution:** describe the bootstrap explicitly; consider a local-file source kind.

#### PM-03 — Per-caller cursors without a caller identity `[G39]`
- **Specs:** PM §15 (cursors bound to "the authenticated caller", records filtered per caller); the
  INTERFACE dispatch ABI passes no caller; no CA scope defines package-record visibility.
- **Our interim choice:** cursors bound to the route/session by the host layer; anyone allowed the method
  sees every record.
- **Suggested resolution:** pass the consumer to providers, or drop the per-caller wording.

#### PM-04 — Paths longer than USTAR allows `[G40]`
- **Specs:** PM §7.1 (gzip USTAR; pax not mentioned); PM §4 (artifact paths up to 4096 bytes).
- **Our interim choice:** reject; no pax headers.
- **Suggested resolution:** align the path limit with USTAR, or allow pax `path` records.

#### PM-05 — Multi-member gzip and directory entries `[G41]`
- **Specs:** PM §7.1.
- **Our interim choice:** reject multi-member streams; directory entries optional on read.
- **Suggested resolution:** state both.

#### PM-06 — Ed25519 verification strictness `[G42]`
- **Specs:** PM §4.3; CA §9.1 (RFC 8032 only).
- **Issue:** cofactored vs cofactorless verification and small-order or non-canonical points are not
  pinned, so libraries disagree on edge cases.
- **Our interim choice:** libsodium semantics (cofactorless; reject non-canonical and small-order); small-
  order keys rejected when trust is loaded.
- **Suggested resolution:** pin the verification rules (e.g. by reference to a vector suite).

#### PM-07 — Same identity and commitment from different sources `[G43]`
- **Specs:** PM §11, §15.
- **Our interim choice:** the first in `list_packages` order.
- **Suggested resolution:** state it.

#### PM-08 — A candidate cannot be fetched during resolution `[G44]`
- **Specs:** PM §11 (deterministic; independent of local resource thresholds).
- **Our interim choice:** abort with `package-unavailable`.
- **Suggested resolution:** state it.

#### PM-09 — `manifest.json` handling `[G45]`
- **Specs:** PM §3 (diagnostic only), §7.1 (allowed).
- **Our interim choice:** path-checked, never read.
- **Suggested resolution:** state whether it must be checked against `manifest.cbor`.

#### PM-10 — No platform registry `[G73]`
- **Specs:** PM §7.1 l.1082 ("Platform profiles define the registered os, architecture, and abi values" —
  none exist), l.1083; PM §3 (closed `platform_constraint`); BCP §5.2.
- **Impact:** a package producer and a Package Manager from different implementations will not agree on
  strings, so every install fails with `incompatible-platform`.
- **Our interim choice:** os {linux, darwin, windows, android, ios}; architecture {x86_64, aarch64}; abi
  optional {gnu, musl, mingw, msvc}; exact match; case-insensitive path collisions on darwin/windows.
- **Suggested resolution:** a platform registry, and a definition of "selected runtime profile".

#### PM-11 — How a module reaches its own artifacts and native libraries `[G93]`, OPEN
- **Specs:** PM §10, §12 (the handoff carries only the implementation artifact); LOADER §3, §5;
  INTERFACE §2.6 (init input: state_dir and configuration only).
- **Issue:** resource and data artifacts are declared and verified, but the module is never told where they
  are; dependent native libraries are not addressed.
- **Our interim choice:** modules are self-contained binaries.
- **Suggested resolution:** pass an artifact directory or table in the init input / handoff.

#### PM-12 — No provenance-signing profile `[G94]`
- **Specs:** PM §4.5 l.611-615 (each provenance-signing profile must define its algorithms; none is
  defined).
- **Our interim choice:** our own Ed25519/DSSE profile in deployment configuration.
- **Suggested resolution:** define a baseline provenance-signing profile.

#### PM-13 — Error codes for provenance failures `[G113]`
- **Specs:** PM §4.5 vs the closed §14 list.
- **Our interim choice:** retrieval failures `package-unavailable`; malformed envelopes or statements
  `invalid-package`; signer, subject, buildType or source failures `signature-verification-failed`.
- **Suggested resolution:** add the mapping to §14 and the provenance step to the check precedence.

#### PM-14 — Nix sources while provenance is selected `[G114]`
- **Specs:** PM §4.5 l.582 (LGX only), l.680-689 (no weakening).
- **Our interim choice:** reject (`package-unavailable`).
- **Suggested resolution:** state it.

#### PM-15 — No optional or platform-conditional dependencies `[G142]`
- **Specs:** PM Scope l.112 (optional, alternative, feature-selected dependencies out of scope), §11
  (dependencies apply to every variant); RUNTIME §3.7.
- **Issue:** a module whose dependencies exist only on some platforms either fails to install elsewhere
  (`dependency-unavailable`) or cannot declare them at all.
- **Our interim choice:** such dependencies are not declared; they are installed explicitly and ordered by
  deployment constraints.
- **Suggested resolution:** platform-scoped dependencies (per variant).

---

## Part 3 — Choices an implementation had to make that the specs should probably own

These are not contradictions, and the specs do deliberately leave them open. But each one either blocks
two implementations from interoperating (sharing packages, catalogs, contracts or deployments) or forces
every implementation to invent the same thing. For each: what the specs leave open, what we chose, and
what a spec could define.

#### SO-01 — Catalog document, origin, refresh and catalog policy `[G90, G150, G74, D17]`
- **Specs:** PM §6 (catalog entry `{identity, source}`, location data only), §4.2/§4.4 (catalogs are
  untrusted; no signature required), §11 l.1182-1184 (protected catalog policy selects among conflicting
  commitments; no format), §13 (PM MAY retrieve catalogs from Storage), §15 (only `list_packages`; no way
  to configure or refresh a catalog); RUNTIME l.1397-1399 (catalogs belong elsewhere).
- **Why it matters:** packages published by one party cannot be discovered by another implementation's
  Package Manager unless both agree on the catalog document and where it lives. A new catalog in Storage
  is a new object, and nothing tells nodes about it.
- **Our choice:** the catalog is a Storage object; its locator lives in deployment configuration; the
  document is deterministic CBOR `{format, sequence: uint64, entries}`, unsigned, rejecting a lower
  sequence than the last seen; "refresh" restarts the PM, which re-fetches; no catalog policy (conflicts
  fail).
- **Spec could define:** the catalog document schema, a mutable pointer or announcement mechanism for the
  latest catalog, a refresh/configure operation, and the catalog-policy format.

#### SO-02 — The Storage fetch contract the Package Manager uses `[G91, G5]`
- **Specs:** PM §4.5 l.583, §6 l.786, §13; INTERFACE §1.1 l.115-119.
- **Why it matters:** the PM spec relies on retrieving objects from "the Logos Storage provider named by
  `storage`", but no contract says how; every PM and every Storage module must agree on it.
- **Our choice:** an interface contract we own (`lcn.storage_fetch`) implemented by the storage module:
  chunked `read_object{object, offset, length ≤ 1 MiB}` plus size.
- **Spec could define:** a `logos.storage_fetch`-style interface (reserved namespace), together with
  PM-01.

#### SO-03 — Formats of protected deployment inputs `[G137, G141, G149, G86, G87, G75, G142]`
- **Specs:** RUNTIME §3.6 step 2 (protected bootstrap input), §3.7 ("This specification does not define
  their serialized representation" — lifecycle-ordering constraints), l.187 (startup defaults), §8,
  §9.3 l.2333-2371 (trust anchors and enrollments), §10.1 (restart policy), §13.3 (implementation-defined
  `configuration_format`); PM §4.1 (trust input binds kids to keys and signers to exact package names;
  "does not define … a trust-store representation"), §11 l.1117-1125 (four resolver limits from protected
  policy), §7.1 (LGX limits); CONFIG §4 (`protected-provisioning` source; no producer); CA §9.1
  l.1029-1033 (call-evidence keys); BCP §5.4.
- **Why it matters:** each item must exist for a deployment to work, and each implementation invents its
  own file; a deployment cannot move between implementations, and the BCP §5.4 deployment profile has
  nothing common to refer to.
- **Our choice:** one deterministic-CBOR daemon configuration with a published CDDL, carrying bootstrap
  pins, startup defaults, ordering constraints, restart policy, provisioned module configuration, trust
  anchors and enrollments, package-signing trust input with exact name sets, call-evidence key mappings,
  resolver limits and resource bounds.
- **Spec could define:** standard CDDL for these protected inputs (even if the transport of the input
  stays deployment-specific).

#### SO-04 — An authority policy language and a baseline policy `[G140, G82]`
- **Specs:** RUNTIME l.1536-1537 ("does not define a generic capability token, policy language, or
  security trust-store format"), l.1490-1521 (default deny; bootstrap policy); CA §1 l.51-52, §6 l.632.
- **Why it matters:** every deployment needs the same baseline rules (orchestrator lifecycle rights,
  PM -> Storage access, module-to-module routes, permission scopes, remote forwarding); without a common
  format they are re-invented per implementation and cannot be audited across them.
- **Our choice:** our own deterministic-CBOR rule set with explicit allows and everything else denied.
- **Spec could define:** a policy rule format, or at least a baseline policy that a conforming deployment
  starts from.

#### SO-05 — A permission vocabulary `[D25, G110]`
- **Specs:** CA §3.5 ("a profile that permits operating-system or platform access MUST define permission
  names and constraints for every facility it exposes"; l.345 identifiers must name their profile);
  RUNTIME l.2240 (omitted permissions are denied); PM §4 (`requested_permission` carries constraints).
- **Why it matters:** a package cannot request a permission another deployment understands; every
  module that touches the network or disk needs one.
- **Our choice:** one coarse `logos-core-nim.host-ambient` permission with empty constraints, enforced by
  Runtime and Loader (no OS sandboxing).
- **Spec could define:** a small common vocabulary (network listen/connect, filesystem, devices) with
  constraint schemas and fail-closed rules.

#### SO-06 — Human operators and administrative access `[G82, RT-01]`
- **Specs:** BCP §2 (humans are outside the participant model; "If a later specification needs a human …
  identity, it must define that identity and its delegation relationship explicitly"); SECURITY §13
  ("trusted administrative path"), §14 ("Core defines no fixed user, operator, or administrator
  classes"); CA l.1108-1110 (`evaluate` is Runtime-facing).
- **Why it matters:** every node has an operator who must start modules, install packages and grant
  access; today each implementation builds its own operator module and rule.
- **Our choice:** the operator acts through the CLI's module instance; a CA policy rule grants it every
  Runtime Control method, provider access, module execution, the ambient permission and `evaluate`,
  narrowable in configuration.
- **Spec could define:** the operator principal and its delegation, and the administrative path
  SECURITY §13 refers to.

#### SO-07 — A namespace for implementation-owned schemas `[G109]`
- **Specs:** INTERFACE §1.3 (`logos.`, `logos-`, `logos_` reserved; nothing reserved for implementations).
- **Why it matters:** implementations need their own contracts (configuration, interfaces such as
  SO-02) and will collide.
- **Our choice:** `lcn.` for CDDL rule names; `logos-core-nim.` for identifier strings.
- **Spec could define:** a convention (e.g. reverse-DNS or registered prefixes).

#### SO-08 — Marking development deployments `[D27]`
- **Specs:** SECURITY §13 (development features must be explicitly non-production); PM §4.1 l.440-441
  (development trust anchors through the same path); TRANSPORT §8.5, BCP §5.5 (test hooks never on Core
  surfaces); INTERFACE l.2300 (debug and release builds encode identically). No mechanism is defined.
- **Our choice:** separate development and release builds; release builds refuse the published
  development key.
- **Spec could define:** how a deployment declares itself non-production and what that permits.

#### SO-09 — Large payloads and long-running operations `[G100]`
- **Specs:** RUNTIME Abstract ("Streaming and large data (acknowledged gap)"), §12 (no generic streaming;
  interfaces should model large data with paths, external references or chunked requests; "Future
  specifications may define generic streaming or large-object transfer profiles"); TRANSPORT §2.1 (16 MiB
  minimum frame); no long-running-operation convention.
- **Why it matters:** storage uploads/downloads and other multi-minute operations exceed any sensible
  call timeout and payload size; every module invents its own session-and-event pattern.
- **Our choice:** long operations return `{session_id}` and finish with a `*_done_event`; data moves in
  chunked methods; absolute host paths allowed for co-located modules.
- **Spec could define:** the streaming / large-object profile §12 anticipates, and a standard
  long-running-operation pattern in INTERFACE.

#### SO-10 — Conformance artifacts: CDDL mirror files and vectors `[G16, D7]`
- **Specs:** every spec names an extracted CDDL mirror file (`logos_transport.cddl`, `logos_common.cddl`,
  `logos_runtime_types.cddl`, `logos_runtime_control.cddl`, `logos_capability_authority.cddl`,
  `logos_module_loader.cddl`, `logos_module_configuration_types.cddl`, `logos_package_manager.cddl`,
  `logos_package_manifest.cddl`), but none exists at `f4f83471`; cdCDDLe §12 fixes each vector record but
  not the error-class vocabulary or the container format.
- **What vectors exist:** cdCDDLe App A (522 bytes), HASH App A (one schema root) and App B.1-B.3 (layout
  digests over synthetic identities; the verified views are given as paths only, without bytes),
  COMMITMENT App A/B (structural, placeholder identities), the COMMITMENT §5 registry, INTERFACE §3.9
  cases, and the two PM manifest roots.
- **What has none:** Transport frames and Hello; Runtime Control, CA, Loader and configuration-types
  schema roots (which are authorization identities); COSE package signatures; call evidence; LGX archives;
  the resolver; value roots through references, aliases or leaf-bodied declarations.
- **Why it matters:** independent implementations can only check each other through shared vectors.
- **Our choice:** extract the mirrors from the spec text; write our own vectors, cross-checked by an
  independent reference implementation, marked non-normative, and offered upstream.
- **Spec could define:** publish the mirror files and normative vectors for the areas above, plus the
  vector container and error classes.

---

## Appendix — Answered by the specs, but hard to find

These looked like gaps and were asked about; each turned out to be settled by text elsewhere. Moving or
cross-referencing that text would save the next implementer the search.

| Item | Where the answer is |
|---|---|
| Whether `list_modules` shows system services and Runtime Control `[G54]` | RUNTIME l.164 (system services are ordinary records), l.2963-2964 |
| How the bootstrap-realized Loader reports its realization `[G57]` | RUNTIME l.3060-3061 ("Other realization mechanisms MUST use implementation-specific") |
| Code for unknown or hidden listener/export targets `[G26]` | RUNTIME l.433, l.2774-2776 (non-revealing NOT_AUTHORISED) |
| Codes for listed Host API binding defects `[G60]` | RUNTIME §13.3 l.3436 (INVALID_PARAMS), §13.4 l.3470 (else MODULE_ERROR) |
| Whether call-evidence `proofs` may be empty `[G50]` | CA §9.1 l.1049 (if present, at least one proof) |
| Whether an implementation-local terminal/presentation hop is allowed `[G83]` | RUNTIME Abstract l.35-38 (implementation-local presentation mechanisms MAY be used); §11 |
| Who defines the Loader-to-Module-Host channel `[G108]` | LOADER §5.4 l.330 ("determined by the implementation") |
| Whether storage must run out of process | RUNTIME §4.2 routing table (around l.833) reads like a requirement ("Default: separate process") but has no keyword; l.842 makes routing policy local |
| Whether the storage examples are the real Storage API | INTERFACE §1.1 l.115-119 and §1.8 (illustrative only); RUNTIME App B examples are informative too |
