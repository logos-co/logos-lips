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

---

# Response to the specification comments

Item identifiers and specification abbreviations follow [the comments](claude-spec-comments.md), which reviewed snapshot `f4f83471`.
The responses below refer to the [updated specifications in commit `6a4dfa28`](https://github.com/logos-co/logos-lips/commit/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad).

## Contradictions

| Item | Response |
|---|---|
| C-01 | Fixed in [Logos Module Commitment Model, section 5: Imported Definitions And Prelude](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#5-imported-definitions-and-prelude). |
| C-02 | Restricted declarations to one identifier segment after the schema namespace in [COMMITMENT §3.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md); dotted namespaces remain valid. This prevents dot boundaries from being lost during CDDL–C round trips without adding escaping or per-declaration metadata. It limits naming hierarchy within a document, not the data structures it can describe. |
| C-03 | Clarified the conformance boundary in the [Interface specification's abstract](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#abstract): an implementation of the bidirectional mapping must support both directions; a module must supply conforming artifacts and value encoding but need not implement authoring tools. This preserves the canonical round-trip guarantee while allowing handwritten modules. |
| C-04 | Required the canonical C representation to retain literal tag fields in tagged-map choice arms in [Interface §2.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#23-composite-type-mapping). This follows the ordinary literal-field mapping and removes generator-dependent layout variation, at the cost of retaining a fixed tag alongside the choice discriminant. CBOR encoding is unchanged. |
| C-05 | Aligned the helper example in [Runtime §4.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#41-route-handles) with Interface Appendix A.5. |
| C-06 | Clarified [Runtime §1.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#13-module-naming): local socket naming uses the protected per-instance directory required by Transport §8.2, with an illustrative layout subject to host pathname limits. Each instance can have a distinct endpoint; the concrete pathname remains implementation-defined. |
| C-07 | Corrected [Package Manager §8](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md#8-validation-rules): sharing an implementation artifact remains invalid, while sharing schema/default artifacts is permitted as stated in §4. Manifest array ordering or uniqueness violations explicitly return `invalid-package` under [§4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md#4-manifest-schema-identity). For packages with multiple defects, implementations may return the first detected validation error while preserving required verification order. This avoids imposing a single validation pipeline; different errors may be reported for multiply invalid packages. |
| C-08 | No specification change is needed. `unsupported-strategy` permits selecting another advertised strategy or placement under [Loader §10](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#10-results-and-errors); it does not waive [§6](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#6-realize-operation)'s prohibition on weaker substitution or [§12](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#12-security-requirements)'s required security controls. Any alternative must satisfy the active constraints. |
| C-09 | No specification change is needed. [Capability Authority §2](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-capability-authority.md#2-module-instance-addresses-and-authenticated-call-context) requires a Runtime-known instance, without restricting it to local ownership. [Runtime §9](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#9-runtime-control-interface) defines how the target verifies an enrolled source Runtime's consumer assertion, binds the connection to that consumer and authorizes its operations. These checks supply the authenticated context for a remote consumer. |
| C-10 | Clarified the [Runtime abstract](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#abstract) to distinguish the ordinary Loader contract from required private realization handoffs. Separate-process compositions must provide implementation-defined mechanisms satisfying [Loader §§5.3–5.4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#53-hosted-provider-endpoint) and [§14](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#14-shared-type-ownership). This preserves placement flexibility without requiring a standardized descriptor-transfer protocol. |
| C-11 | No specification change is needed. The cited [Interface Appendix A.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#a3-generated-dispatch-implementation) obligations are already stated in normative §§1.2, 2.6, 5.1 and 5.2. [Security Considerations §1.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-security-considerations.md#11-normative-ownership) explicitly defers to the owning specifications: its fail-closed statement reflects Loader §§4, 6 and 12, while the iOS passage describes platform availability. These passages do not create additional Core conformance requirements. |
| C-12 | Listed the current upward dependencies in [BCP §1.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-system-bcp.md#11-dependency-exceptions), including Runtime/Transport use of Capability Authority call-audit and evidence formats. Keeping the existing formats preserves their schema identities and avoids a schema migration; this dependency requires no Authority provider or module calls. A caution states that future revisions will review the exceptions for removal or relocation while current requirements remain in force. |

## Gaps

| Item | Response |
|---|---|
| PM-01 | Clarified [Package Manager §§6 and 13](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md): `storage` selects a deployment-configured Storage binding; object locators are opaque bytes interpreted through its documented retrieval API and encoding. Acquisition remains an implementation choice, so Storage providers need no new common fetch interface and a separate downloader is not required. Cross-deployment locator reuse requires compatible bindings. Package validation remains Package Manager’s responsibility. |
| CA-03 | Clarified [Capability Authority §3.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-capability-authority.md#31-provider-access): `publish-event` evaluates the publishing module’s authority to send an event along a subscriber route, while `subscribe-event` evaluates the subscriber’s authority. Delivery must satisfy both permissions and route event lists. Runtime now states explicitly that authorization is per subscriber route and that invoking the publication callback grants no delivery permission. This retains separate publication and subscription controls without adding a consumer-to-provider event path or changing the schemas. |
| PM-11 | Clarified [Package Manager §10](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md#10-artifact-records): installed paths are not guaranteed to be module-visible. Deployment and realization establish resource access under active permissions, using a documented convention such as schema-typed configuration; native libraries use Loader’s deployment-selected dynamic-linker integration. This keeps the ABI and handoff unchanged. Packages needing external resources require compatible deployment integration rather than a standardized artifact directory or lookup table. |
| GN-01 | Added explicit BCP 14 requirement-language declarations and RFC 2119/8174 references across the specification set, including clarification of cdCDDLe’s existing declaration. Uppercase keywords use those RFC meanings; lowercase forms retain ordinary English meanings. Clarified direct conformance requirements in [Capability Authority §§3/6](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-capability-authority.md), [Commitment Model §§2.1/6/7](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md), [Configuration §§7/9](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-configuration.md), [Loader §6](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md), [Package Manager §§4.4/12](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md), [Runtime Terminology and §§3.4/9.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md), and [System BCP §2](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-system-bcp.md). Reviewed the remaining lowercase forms in context and retained explanatory, informative, advisory and future-profile wording. Normative requirements can also be expressed without these keywords (RFC 8174 §2). |
| CM-01 | Clarified recursive local-reference normalization in [Commitment Model §8](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#8-semantic-value-tree). A chain creates no intermediate value nodes: the outer value root or containing structural node retains the referring location’s identity, while the child uses the terminal declaration’s identity. Added a normative chain vector in [Appendix B.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#b1-local-reference-chain). Alias names remain in the canonical schema model, so this does not flatten schema identity. |
| CM-02 | Clarified imported-reference schema context and added explicit verifier checks and exact positive and negative vectors. Imported descendants use the referenced document’s root, preserving subtree identity across importers. The current draft profile identifier is retained; affected imported-value commitments require recomputation. |
| CM-03 | Clarified [Commitment Model §5](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#5-imported-definitions-and-prelude): imported references must target named type declarations. This excludes `logos.schema_request` and `logos.schema_response` as reusable type references, consistently with local and supporting-schema references; their well-known callable use is unchanged. |
| CM-04 | Clarified [Hash Profile §8](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-hash-profile.md#8-verified-views): a path ending at a present field, list element, or tuple position discloses the contained normalized value. Field and tuple-element payloads are carried in the proof material. Empty paths still disclose the whole value, and absent optional fields use the absence marker. |
| CM-05 | Clarified [Commitment Model §9.4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#94-semantic-path-objects): continuing through a choice requires a `choice-arm` segment matching the selected canonical arm index. The segment selects the arm’s contained value. A path may instead end at the choice and select the complete normalized choice value. |
| CM-06 | Clarified [Commitment Model §3.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#31-logos-schema-model-construction): literal tests collect constraints on the observed value, following references and choice alternatives without descending into containers. A map-field-literal test observes the selected field’s value. Added examples showing that disjoint literal choices in a field can distinguish arms, while literals inside equal-length tuples cannot. |
| CM-07 | Clarified [Hash Profile §4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-hash-profile.md#4-canonical-packing-and-chunking-rules): Boolean and integer literal element schemas are packable. Lists such as `[* true]`, `[* 5]`, and `[* -5]` follow the existing 256-element threshold; their literal schema identities and constraints remain binding. |
| CM-08 | Clarified [Hash Profile §8](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-hash-profile.md#8-verified-views): verification requires the schema construction input and its required dependencies separately from the view. The verifier validates that input, computes the schema and selected subtree roots, and checks them against the view. Previously validated results may be reused under matching commitment-model, hash-profile, and hash-suite identifiers. |
| CM-09 | Clarified [Hash Profile §7.2](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-hash-profile.md#72-schema-payloads): `logos.schema.reference` hashes a standalone `schema-import` pair. No schema or value commitment construction or verified view in this revision uses that digest. Imports retain their two-root representation; the standalone digest cannot replace either root or the pair. |
| CM-10 | Clarified [cdCDDLe §5.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-cdcddle.md#51-supported-cddl-construct-subset): source occurrence indicators with explicit numeric bounds are rejected, including `0*` in arrays and `*1` in maps, even when equivalent to a supported form. Use `*` for homogeneous variable-length arrays and `?` for optional map members. |
| CM-11 | Pinned text-string and byte-string literal parsing in [cdCDDLe §5](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-cdcddle.md#5-processing-model) to RFC 9682 §2, retaining RFC 8610 for the rest of the supported subset. This adopts the corrected string grammar and braced Unicode escapes. Escape spelling remains outside the canonical model. |
| CM-12 | Clarified [cdCDDLe §5.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-cdcddle.md#51-supported-cddl-construct-subset): range bounds must be integer literals written directly in the source, including bounds in `.size` controllers. Named bounds are rejected, preserving the existing literal-bound range model without introducing reference expansion. |
| CM-13 | Clarified [cdCDDLe §10](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-cdcddle.md#10-decoding-and-checking): decoders must reject a choice node with another choice node as a direct alternative. Source canonicalization flattens these choices under §7.4; encoded canonical models must already have that form. |
| CM-14 | Clarified [Commitment Model §5](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-commitment-model.md#5-imported-definitions-and-prelude): each `cdCDDLe` document contains only its own declared rules. Prelude aliases and external named types remain type-reference nodes resolved within the permitted scope; their definitions are not merged into its rule array. Logos schema-model construction then normalizes prelude aliases to primitives and represents external named types by imported references. |
| IF-01 | Specified in [Interface §4.4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#44-logos-deterministic-cbor-requirement) that floating-point data items are forbidden at every nesting depth. [Section 4.5](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#45-validation) makes their presence in `params`, `result`, or `data` a Transport validation failure: [Transport §2.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-transport.md#23-deterministic-cbor) requires ProtocolError `INVALID_PARAMS` when writable, followed by connection closure. This applies even to a shortest-form float; rejection is not deferred to payload-schema validation. |
| IF-02 | Added [Interface §4.5.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#451-value-nesting): finite configurable payload-depth limits of at least 128 array/map containers, with bounded processing and cleanup. [Transport §2.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-transport.md#23-deterministic-cbor) enforces that limit during envelope validation and requires room for the enclosing message map. Module dispatch reports a depth-only rejection as `INVALID_PARAMS` without structured detail; Transport sends ProtocolError `INVALID_PARAMS` without `detail` when writable and closes the connection. No new error reason is allocated. |

| IF-03 | Defined inline tuple, list, and byte-string aggregates in Interface §§2.1–2.3 for tuple positions, list elements, and choice arms. They use existing named-aggregate layouts and owner/path-derived C names; empty tuples and exact-zero byte strings retain their shared forms. Lists store complete aggregate elements contiguously, and positive exact-size byte strings use embedded arrays rather than pointer-valued constraint typedefs. Required forward typedefs also cover list-mediated recursion. Section 3.5 recovers inline schema nodes without introducing named declarations. Schema identity and wire values are unchanged; implementations using pointer-valued exact-byte elements require coordinated native ABI alignment. |

| IF-04 | The event mapping specifies both map and choice-of-maps payloads. Choice-valued events use the ordinary tagged-union representation and preserve the event declaration name; they add no wire wrapper. |
| IF-07 | Typed responses use one response owner for backing storage, including recursive values. Clearing it releases the complete result; callers do not free individual payload pointers. |
| IF-08 | Interface §2.7.2 requires generated C call helpers to return an owner for decoded response storage and provide matching typed cleanup that resets the outputs. Cleanup uses the decoder’s allocator; Appendix A.5 illustrates the call and cleanup pair. Helper names remain implementation-defined. Aligned the typed call-helper example in Runtime §4.1 with these ownership rules. |

| IF-05 | Defined deterministic generated literal spellings and a bounded set of equivalent handwritten Boolean, integer, and UTF-8 string forms. Reverse mapping preserves their scalar values and schema identity. Signed extrema and byte escapes are explicit; general C expression evaluation is not required. |
| IF-06 | An optional inline tuple has one presence flag before its first expanded component. The flag governs the entire tuple; empty and nested tuple representations follow the existing aggregate rules. |
| IF-09 | Distinct module-operation and provider-method symbol families separate the reported collision without additional namespace reservations. |
| IF-10 | Route construction input may be embedded or supplied contract data, a correctly projected authorized provider descriptor, or a previously obtained selected-contract introspection response. Runtime validates the same exact contract root for every source; materialization does not require an introspection call. |
| IF-11 | The mapping fixes declaration content, dependency correctness, and ABI-visible value layout. Independent declaration placement and source file layout do not affect schema identity or interoperability. |
| EC-01 | Reusing a retained request key within its specified scope for different request fields or a different operation returns INVALID_PARAMS without validation detail, subject to authorization and non-disclosure rules. |
| EC-02 | For an authorized request whose target may be disclosed, a mismatched expected execution, permission-settings, or configuration-state revision returns INVALID_PARAMS without validation detail and does not permit mutation. |
| EC-03 | Prohibited Runtime lifecycle operations and renewal of closed or failed routes return NOT_READY, subject to authorization and non-disclosure rules. Existing idempotent success rules are unchanged. |
| EC-07 | An unavailable non-authority system service returns NOT_READY when it is required to complete the operation. Capability Authority unavailability retains its existing authorization-failure rules. |
| EC-11 | Static registration rejects detectable symbol-table defects with INVALID_PARAMS. Contract-dependent symbol checks remain part of implementation binding; registration does not execute module code or certify a raw function pointer’s C signature. |

| EC-04 | Defined apply_configuration precondition errors: INVALID_PARAMS for stale revision, missing staged data or absent live support; NOT_READY for readiness or an existing application attempt; VERSION_MISMATCH for configuration-schema commitment mismatch. Valid hook rejection returns MODULE_ERROR. Indeterminate completion returns TRANSPORT_ERROR for transport failure and MODULE_ERROR otherwise, while preserving the required error-state transition and retained configuration records. |
| EC-05 | New route operations distinguish authority withdrawal or expiry (NOT_AUTHORISED) from explicit closure or Runtime readiness loss (NOT_READY), using the enforcement cause. Known authorization failure takes precedence over readiness. Revoked-route renewal follows the same classification without reviving the route; in-flight transport failures retain their transport semantics. |
| EC-06 | A stopping provider or logically invalidated Runtime Control binding returns NOT_READY for a new invocation while the binding remains valid to access. Cleanup during stopping remains permitted. Released bindings, destroyed contexts and unloaded code are outside the valid-use contract. |
| EC-08 | Specified separate errors for incompatible vtable layout, malformed producer bindings, invalid construction input, contract-root mismatch and route authorization/readiness. Non-remote or same-Runtime connect_remote targets return INVALID_PARAMS. Invalid vtables are rejected locally without invoking them; failed acquisition preserves null outputs. |
| EC-09 | Invalid listener/export input uses INVALID_PARAMS, subject to non-disclosure rules. Transport activation failure uses TRANSPORT_ERROR; other operational failures retain their applicable shared codes. Enrollment is provisioning input rather than a Runtime Control method; provisioning interfaces using shared errors distinguish invalid records from authentication or authorization failure. |

| EC-10 | Defined retained failure labels for route causes and permission enforcement. Consumers accept unknown labels as unclassified failures. These state classifications do not replace invocation-error codes or the separate audit distinctions for authentication, enrollment and ticket validation; execution resumption failures remain execution state. |
| TR-01 | Wrong-direction messages and ordinary messages received before Hello completion produce ProtocolError INVALID_PARAMS and close the connection without dispatch or delivery. A valid ProtocolError is allowed during setup and terminates the connection without an error reply. |
| TR-04 | After envelope validation, the caller checks the Hello response module, token and schema in that order. A response token violating the selected profile, including a non-empty token where an empty one is required, produces ProtocolError NOT_AUTHORISED and closes the connection. |
| TR-07 | A schema-invalid response-ok or Event produces ProtocolError INVALID_PARAMS and closes the provider session, even if its value commitment cannot be recomputed. Invalid data is not delivered, and outstanding calls receive TRANSPORT_ERROR. |

| TR-02 | Defined Response, SubscriptionResult and Event correlation. Local abandonment retains bounded protocol state: the first valid late response is validated and discarded; late subscription results still update protocol state. Unsolicited, duplicate or mismatched messages produce ProtocolError INVALID_PARAMS and close. Required state cannot be forgotten while keeping the connection open. |
| TR-03 | Reused Subscribe IDs, including failed earlier attempts, and Unsubscribe IDs without an active subscription produce failed SubscriptionResult INVALID_PARAMS without changing active state. A control operation processed while the preceding same-ID result is uncommitted instead produces ProtocolError INVALID_PARAMS and closes; this avoids ambiguous overlapping results without adding wire fields. |
| TR-05 | Transported route materialization completes profile peer validation and provider Hello before returning a handle, or reuses a live session satisfying the same route bindings and authorization. Validated Hello rejection codes are preserved; transport loss or timeout without such a rejection returns TRANSPORT_ERROR. Failures leave null outputs and do not implicitly renew, retarget or replay a redeemed ticket. |
| TR-06 | Route expiry or revocation stops admission and ends subscriptions and the session under the applicable in-flight policy. A new Request processed during termination receives NOT_AUTHORISED. The endpoint sends ProtocolError NOT_AUTHORISED when writable and closes within bounded shutdown limits, without waiting for another request or acknowledgement. Calls lacking a terminal response retain TRANSPORT_ERROR and uncertain execution semantics. |
| TR-08 | Specified validation precedence: envelope and correlation/access checks, schema-subtree-root comparison, payload-schema validation, then typed value-root comparison. Root mismatch closes with ProtocolError INVALID_PARAMS. A Request with matching schema root but invalid payload receives response-err INVALID_PARAMS without dispatch or closure for that failure alone. Invalid responses/Events close; untyped CBOR hashing is not a fallback. |

| TR-09 | Defined conditional Windows applicability for protected Unix-stream transport: effective filesystem protection, secure listener transfer and an independently authenticated process reference established before connection. PID-based verification must prevent identifier reuse and use qualified listener attribution. Unsupported checks fail before Hello or ticket disclosure. The descriptor is unchanged; implementation support requires native platform qualification. |
| RT-01 | Clarified protected deployment activation followed by ordinary module admission and Loader realization. The admitted application receives consumer-bound Runtime Control access; an external launcher cannot claim module identity or bypass lifecycle and authority checks. Activation encoding and terminal integration remain documented deployment choices, without a mandatory embedded Runtime or loopback transport. |
| RT-02 | Defined Runtime-owned system-service bindings separately from consumer routes, with direct and protected local-transport forms. Protected policy binds the exact local provider realization, contract, endpoint, operations and validity. The local ticket case has disjoint credential purposes, ordered redemption/invalidation and engine-only delivery. It creates no module consumer or general engine authority and does not replace execution or permission authorization. |
| RT-03 | Orchestration is a deployment-bound role with no canonical module name or required provider contract. Deployment identifies the selected instance explicitly. Existing module-name and reserved-prefix rules apply; names confer neither the role nor authority. |
| RT-04 | Package selection remains protected deployment policy, with exact package/version selection required for package-backed declarations. Unavailable exact selections and unresolved declaration choices fail without substitution. Versions do not select between different packages, and authorization constraints are not selectors. Existing instances retain their selection; no per-request create_module package selector is added. |
| RT-05 | Loader loss does not establish release. Runtime retains unresolved custody and arranges protected termination when realization control is lost; replacement is blocked until old execution and assigned-state access are confirmed ended. A replacement Loader's empty registry or unknown-ID release success is insufficient. Rebinding does not adopt old realizations, and temporary service unavailability alone does not terminate independently enforced healthy work. |
| RT-06 | Package update does not reselect a retained instance. Upgrade uses an explicitly selected replacement instance, confirmed old-realization cleanup and separately authorized, format-aware state migration, with fresh state assignment by default. The replacement passes ordinary acceptance and readiness checks; callers acquire new routes. Recovery preserves the old selection. No general Runtime Control upgrade or state-transfer method is introduced. |
| CA-01 | Ended execution authorization requires withdrawal and termination without waiting for re-evaluation. A retryable proactive renewal failure may preserve only an independently valid existing authorization, without extending it or overriding denial, invalidation or expiry. Execution intent is retained; later recovery requires fresh authority and completed cleanup. |
| CA-02 | Optional policy attributes use a protected deployment-defined integration with authoritative source, consumer/operation binding, visibility and freshness rules. Required missing or unverifiable facts cause evaluation failure. Attribute snapshots and invalidating changes must follow the policy-revision/event ordering; dependent allows require bounded validity that cannot outlive required facts, and evaluation fails if the guarantees are unavailable. No generic attribute bag, automatic Runtime Control visibility or recursive prerequisite authorization is introduced. |

| CA-04 | Each request or response proof array is ordered by the bytewise lexicographic deterministic-CBOR encoding of its verified-view semantic path, with duplicate paths rejected per side. Empty side arrays and empty `proofs` are omitted. The same path may appear once on each side. This canonicalizes the selected proof collection, not the choice of disclosure. |

| CA-05 | Grant lists use ascending grant-id bytes and live continuation strictly after the last returned ID, with current state and visibility checked on every page. Cursors bind the consumer and effective query, confer no authority, and may expire under documented policy. Audit records use descending timestamps and reverse recording order for ties; `since` is inclusive and `until` exclusive. Audit queries remain bounded to 1000 visible matching records without pagination or a complete-export guarantee. |

| CA-06 | Call audit records retain the actual call-authorizing decision, enforced scope, and retention requirements captured consistently at admission. A valid cached call decision may be used; establishment or renewal authority alone is insufficient. Later renewal or revocation does not rewrite that record’s decision, and required revocation enforcement remains effective. |

| CA-07 | The signed evidence profile remains independent of retrieval. Export requires a documented protected deployment integration that authorizes the complete record and each included proof; commitment visibility alone does not authorize proof disclosure. An authorized subset of optional proofs requires a newly signed valid container. `query_audit` continues to return audit records, not evidence containers; no new retrieval method is introduced. |

| PM-03 | Package Manager requires compatible protected invocation integration and observation policy. Ordinary queries and cursors use the authenticated module consumer; engine queries and cursors use their exact Runtime-owned system-service binding. The integration enforces visibility before limits and snapshots and rechecks it on continuation. Method permission alone does not imply record visibility. The generic provider ABI is unchanged and does not supply this context. |

| PM-07 | Equivalent acceptable sources for the same exact package identity and full manifest commitment are selected by ascending bytewise lexicographic deterministic-CBOR source-record encoding, consistent with catalog listing order. Explicit root sources and installed dependency edges remain pinned. Advertised name/version equality does not prove equivalent content; conflicting commitments retain the protected-selection-or-failure rule. |

| PM-08 | When material needed to assess a candidate or resolve its closure is unavailable, the root operation fails with `package-unavailable` without changing installed state. Unavailability is not proof of invalidity or an unsatisfiable closure and cannot silently trigger a downgrade. Proven invalid candidates and unsatisfiable closures retain their existing rules; irrelevant lower candidates need not be fetched after a complete solution is selected. |

| PM-02 | Explain first Storage/PM provisioning through accepted protected local inputs and normal Runtime/Loader rules. | Existing bootstrap boundary; no file/URL source or fake installed record. |
| PM-04 | Require full LGX paths to fit USTAR name/prefix fields at a slash split, measured in bytes. | Keep narrow USTAR and general manifest schema; long LGX paths require repackaging. |
| PM-05 | One gzip member; optional inferred directories, explicit empty variants, normalized directory spelling and sorting. | Small bounded archive reader; general gzip/tar extensions are not all accepted. |
| PM-09 | `manifest.json` is removed from the LGX format. The canonical `manifest.cbor` is the sole manifest representation. Human-readable inspection can be derived from verified structured manifest data by consumer tools; it is not another package file or signing input. Native DSSE/in-toto JSON provenance remains unchanged. |
| PM-13 | Map missing/malformed evidence, retrieval failure and failed trust/binding to existing errors. | No new enum or total validation order; an invalid extra signature does not defeat an accepted signer-builder pair. |
| PM-14 | Reject direct Nix under LGX-only SLSA policy; allow Nix-built LGX and eligible dependency alternatives. | Preserve required provenance without evaluating unsupported sources. |
| PM-15 | Dependencies remain unconditional across variants; different sets use separate packages. | Preserve variant-specific module presence and Runtime ordering boundaries; conditional dependency language remains separate. |

| PM-06 | Replaced the Ed25519 baseline with pure FIPS 205 SLH-DSA-SHA2-192s for package signatures and call evidence. Both profiles fix the algorithm through protected context using RFC 9052 Appendix A, reject every explicit alg header, and authenticate the expected profile identifier as external AAD. Public keys are exactly 48 bytes and signatures exactly 16,224 bytes; verification uses the FIPS 205 procedure with an empty context, without prehashing or input repair. Signing keys and trust remain purpose-specific. |
| PM-12 | Defined logos.provenance-signing.dsse-slh-dsa-sha2-192s as required support for implementations supporting optional SLSA provenance. Protected policy selects accepted profiles and binds each exact public-key signer identity to authorized builders. The profile signs native DSSE PAE with pure SLH-DSA-SHA2-192s and an empty context; keyid is only a bounded lookup hint. Revocation and cache invalidation follow active trust, unsupported configurations fail, and failed verification cannot activate an unselected profile or baseline-only acceptance. Common cryptographic support does not establish shared signer trust. |

| SO-03 | Protected deployment-input encodings remain deployment-defined. Deployment documentation identifies their accepted representations, provisioning, validation and replacement or revocation behavior; those representations cannot alter Core contract semantics. Configuration migration between implementations requires compatible deployment tooling. |
| SO-04 | Core standardizes authorization scopes, decisions and enforcement, not the policy language. Default deny and explicit bootstrap and system-service permissions remain required. Deployment-specific module roles and enabled services prevent one universal baseline allow policy. |
| SO-06 | Ordinary administrative contract invocations use admitted module identities and applicable route and operation authority. Protected host provisioning remains a distinct deployment input. The administrative path must document principal authentication and authority to change protected inputs; administrator status does not substitute for Runtime’s protected Capability Authority evaluate binding. No human Core participant or automatic administrator privilege is introduced. |
| SO-07 | Independent implementations may use the same nonreserved schema namespace. Existing exact-document identity and composition-conflict rules apply when documents are combined. No implementation-prefix reservation or registry is introduced; a prefix grants neither authority nor automatic support. |
| SO-08 | The non-production mechanisms identified in Security §13 require explicit protected configuration and a non-production designation in deployment documentation and operator-facing diagnostics. Build mode alone enables no development trust or exemption, and that designation waives no Core or selected-profile requirement. Development trust anchors retain normal verification and transport test hooks retain their existing restrictions. |

| PM-10 | Platform constraints use values and matching rules documented by the deployment profile for the target execution environment, including the native ABI and version constraints they represent. Values without defined matching rules do not match; omitted fields remain unconstrained, and declared variant order selects the first compatible variant. No global platform registry or separate runtime-profile selector is introduced. Cross-deployment package use requires compatible definitions. Path collision checks follow the actual installation filesystem and namespace. |
| SO-01 | Catalog acquisition, document formats, refresh and policy configuration remain implementation-defined and documented. The common catalog records and package verification rules remain unchanged. Catalog metadata cannot establish package trust, and selected freshness requirements still apply. |
| SO-05 | Capability Authority §3.5 already requires each permission definition to specify its constraints, containment semantics, enforcement and failure behavior. Deployments document supported definitions and reject unknown or unenforceable permissions. Cross-implementation use requires agreement on those definitions; this revision adds neither a universal permission registry nor an ambient-access permission. |
| SO-09 | Large transfers and continuing work use module-defined schemas under existing payload bounds and method/event rules. Transport already describes acknowledgement and progress workflows; cancellation and recovery guarantees belong to the module contract. No generic streaming or operation-handle protocol is added. Filesystem paths require suitable visibility and permissions; co-location grants neither. |
| SO-10 | The named extracted CDDL mirrors and the existing Core conformance corpus are present. The owning specifications remain authoritative; cdCDDLe §12 defines vector records and coverage without requiring a shared outer container or diagnostic vocabulary. Their presence is not independent verification or a claim of complete coverage. |

## Implementation choices

| Item | Response |
|---|---|
| SO-02 | Clarified [Package Manager §§6 and 13](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-package-manager.md): `storage` selects a deployment-configured Storage binding; object locators are opaque bytes interpreted through its documented retrieval API and encoding. Acquisition remains an implementation choice, so Storage providers need no new common fetch interface and a separate downloader is not required. Cross-deployment locator reuse requires compatible bindings. Package validation remains Package Manager’s responsibility. |

## Appendix references

The following references address the nine unnumbered appendix entries.

| Item | Response |
|---|---|
| System services and Runtime Control in `list_modules` `[G54]` | System-service module instances have ordinary provider and lifecycle records. [Runtime §9.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#93-runtime-control-module-contract) returns the runtime-known records visible to the authorized caller. [Runtime §9](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#9-runtime-control-interface) defines Runtime Control as an intrinsic contract surface; the specification does not require that surface itself to appear as a separate ordinary module record. |
| Bootstrap-realized Loader reporting `[G57]` | [Runtime §9.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#93-runtime-control-module-contract) requires the implementation record to report the selected Loader-defined realization strategy when applicable. Other realization mechanisms use `implementation-specific`; transport mode alone does not establish placement. |
| Unknown or hidden listener/export targets `[G26]` | [Runtime §9.3](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#93-runtime-control-module-contract) preserves non-revealing `NOT_AUTHORISED` for unknown, hidden, or denied targets. Invalid listener/export inputs use `INVALID_PARAMS` when the relevant facts may be disclosed. |
| Host Embedding API errors `[G60]` | [Runtime §13](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#13-host-embedding-api) defines specific ABI, input and lifecycle errors, including `VERSION_MISMATCH`, `INVALID_PARAMS`, `NOT_READY` and `CANCELLED` for their stated cases. Other failures use the applicable shared error, or `LOGOS_ERR_MODULE` when none is more specific. |
| Empty call-evidence proofs `[G50]` | [Capability Authority §9.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-capability-authority.md#91-call-evidence-profile) requires at least one proof when `proofs` is present. Empty side arrays are omitted, and `proofs` is omitted when neither side has a proof. |
| Implementation-local presentation hop `[G83]` | [Runtime §11](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#11-presentation-boundary) leaves concrete presentation handoffs and compositing to the selected presentation profile while preserving module identity, lifecycle, authority and audit rules. No additional Core intermediary contract is required. |
| Loader-to-Module-Host channel `[G108]` | [Module Loader §5.4](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-loader.md#54-trusted-transport-adapter-handoff) leaves setup and descriptor transfer of the private adapter channel to the implementation, subject to its isolation and credential requirements. |
| Storage process placement | [Runtime §4.2](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#42-routing-selection) presents separate-process Storage as a routing example. Runtime owns routing selection, with policy supplied by Runtime, host, deployment or configured policy; the example does not require Storage to run out of process. |
| Storage examples as an API | [Interface §1.1](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#11-schema-file) and [§1.8](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-interface.md#18-complete-example) identify the Storage schemas as illustrative. [Runtime Appendix B](https://github.com/logos-co/logos-lips/blob/6a4dfa2846ab9f1f679ad285f8caa848ee8544ad/docs/logos-core/raw/spec-module-runtime.md#appendix-b-runtime-control-record-examples) contains informative record examples. These examples do not define the Storage API. |
