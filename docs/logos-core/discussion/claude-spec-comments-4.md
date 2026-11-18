# Logos Core module specs — further findings at `6cac8335`

This document lists defects in the Logos Core module specs (`docs/logos-core/raw/spec-*.md`) at revision `6cac8335`. The open
points of the earlier audits are in `claude-spec-comments-3.md`. Remarks on an earlier document are at the end of that document.

**Conventions.**
- Short names: RUNTIME, INTERFACE, TRANSPORT, LOADER, CA (Capability Authority), PM (Package Manager), CONFIG, COMMITMENT,
  HASH, cdCDDLe, SECURITY, BCP, CREDENTIAL (Credential Store). `l.N` is a line of the specification file at `6cac8335`
  (`git show 6cac8335:docs/logos-core/raw/<file>` gives the text, whatever revision a working tree holds).
- The findings of this document are `UF-01` to `UF-63`. Other identifiers name items of the earlier documents.
- Needs are stated with neutral roles (consumer C, provider P, host H, subscriber S). Concrete modules are discussed only in
  `module-port-gaps.md`.
- Every finding survived a separate attempt to refute it from the specs. Every quotation is exact and was checked by program
  against the line it cites.

## Summary

| Section | Content | Findings |
|---|---|---|
| 1 | Credential Store and Capability Authority | 9 |
| 2 | Contract extensions and release compatibility | 9 |
| 3 | Schema language and module binding | 3 |
| 4 | Runtime Control and Transport | 6 |
| 5 | Editorial | 7 |
| 6 | Findings first raised in `gemini-spec-comments.md` | 29 |

**What most needs an answer.**

- UF-02: no specified path lets the Credential Store provider check the original caller's authority, so a provider that relies
  only on specified surfaces rejects every administrative operation.
- UF-03: CA retains the evaluated scope in its audit record, and INTERFACE forbids marked payloads in audit records.
- UF-10: a `0.0.x` patch release must keep its contracts under one rule and may drop them under another.
- UF-19: `true` and `false` are not stated to be Boolean literals, although normative contracts use them.
- UF-23: no inter-Runtime operation ends a route owned by the other Runtime when its consumer stops.
- UF-44: a consumer may close its own route, and method authorization can refuse that call.
- UF-45: the check on marked methods reads the requested route in one place and the permitted route in another.
- UF-58: the listing of `logos_types.h` does not compile as written and cannot be included twice.

**Index of findings.** The last column names an item of an earlier document that describes the same defect.

| Finding | Subject | Overlap |
|---|---|---|
| UF-01 | The Credential Store provider must return a status that provider code may not return | TF-53, GF-01 |
| UF-02 | The provider's authorization integration is named and not defined | TF-06, GF-02 |
| UF-03 | Audit retention of an evaluated scope conflicts with the marked-payload rule | GF-07.2 |
| UF-04 | Whether a versionless `inspect` policy scope covers version queries is not decided |  |
| UF-05 | A replacement instance cannot be told apart from a forbidden alias of a slot | GF-04 |
| UF-06 | Whether the administrative permission passes through saved permission settings is not stated | GF-03.2 |
| UF-07 | A resolved but hidden `issue_grant` target has no assigned outcome |  |
| UF-08 | `revoke_grant` outcomes are not ordered against the permission to revoke |  |
| UF-09 | A clarifying note: whose authority covers the permissions of a started module |  |
| UF-10 | A `0.0.x` patch release must keep its contracts and may also drop them |  |
| UF-11 | A package "provides" a contract through a module that is not selected on this host | TF-56, GF-13.5 |
| UF-12 | Four descriptor rules are worded too widely or too narrowly for `extends` | GF-10.1 |
| UF-13 | An extended contract view is disclosed with no required `discover` decision | GF-11 |
| UF-14 | Package Manager's extension check does not pair the contracts it compares | GF-13.2 |
| UF-15 | `input_artifacts` has no canonical order or uniqueness rule | GF-13.3 |
| UF-16 | "Validated as a Logos-defined contract" is undefined |  |
| UF-17 | Optional catalog exclusion makes resolution depend on the implementation |  |
| UF-18 | A packaged native library has no artifact kind | TF-06 |
| UF-19 | `true` and `false` are not stated to be Boolean literals |  |
| UF-20 | A queued invocation-scoped delivery at the cutoff has no stated outcome | TF-06, GF-17.1 |
| UF-21 | Release does not cover subscription-end callbacks |  |
| UF-22 | No rule says when a selected facade stays on the invocation path |  |
| UF-23 | No inter-Runtime operation ends a route owned by the other Runtime |  |
| UF-24 | Route identifiers can collide between consumers of one Runtime | GF-19.1 |
| UF-25 | RUNTIME and CONFIG order the revision check differently | GF-14.1 |
| UF-26 | A failed continuation resolution has no assigned code |  |
| UF-27 | During termination, an Unsubscribe after a SubscriptionEnd has two required results | GF-15.1 |
| UF-28 | The consequence of extending an implemented interface is unstated | GF-08 |
| UF-29 | RUNTIME l.504 still speaks of rejecting one provider view |  |
| UF-30 | The selected contract is defined without extended contracts | TF-06, GF-10.4 |
| UF-31 | Five reference definitions share one line |  |
| UF-32 | The state pairs a facade may report are not listed | GF-18.1 |
| UF-33 | Two references do not reach their text | TL-03 |
| UF-34 | Example B.3 shows a ready instance at revision 1 |  |
| UF-35 | A manifest can declare only one administrative scope | GF-03.1 |
| UF-36 | Retained operation records can never be released | GF-06 |
| UF-37 | A zero `validity_seconds` has no assigned error | GF-07.1 |
| UF-38 | `extends` may repeat the module's own contract, which makes the module unrealizable | GF-13.1 |
| UF-39 | A manifest that omits an implemented interface installs and then fails | GF-13.4 |
| UF-40 | An unsupported manifest schema has no outcome at two later points | GF-23.4 |
| UF-41 | Two cross-field rejections belong to no step of the order of checks | GF-14.2 |
| UF-42 | When a blocking `failure` classification clears is not stated | GF-18.3 |
| UF-43 | A route survives at its target after an identifier collision fails the resolution | GF-19.1 |
| UF-44 | A consumer may close its own route, and method authorization can refuse it | GF-19.2 |
| UF-45 | The check on marked methods reads the requested route in one place and the permitted route in another | GF-20.1 |
| UF-46 | A provider rejected for a marked method has no place in a multi-provider result | GF-20.2 |
| UF-47 | No rule escalates from an unresponsive Module Loader to protected supervision | GF-22.1 |
| UF-48 | A duplicate SubscriptionEnd is not classified | GF-15.2 |
| UF-49 | A subscription-end callback is not ordered against the return of `unsubscribe` | GF-15.3 |
| UF-50 | An oversized invocation-scoped Event has no assigned code | GF-16 |
| UF-51 | The thread that drains queued deliveries has no limit on its work | GF-17.2 |
| UF-52 | A surviving session is not rebound to the decision that replaces its own | TF-33, GF-21 |
| UF-53 | Coverage for `issue_grant` does not separate holding a scope from issuing it | GF-23.1 |
| UF-54 | A `query_audit` result larger than one message has no stated outcome | GF-23.2 |
| UF-55 | How a selector applies when a Runtime Control subscription is activated is not stated | GF-23.3 |
| UF-56 | A list output exposes response storage through a mutable pointer | GF-24.2 |
| UF-57 | A named declaration whose body is a reference to an aggregate has no C form | GF-25.1 |
| UF-58 | The listing of `logos_types.h` does not compile as written and cannot be included twice | GF-25.2 |
| UF-59 | COMMITMENT does not state what an absent optional reference field commits to | GF-26.1 |
| UF-60 | No value vector covers three shapes that involve references | GF-26.2 |
| UF-61 | A verifier's handling of `.size` and of U+0000 in a disclosed range is not stated | GF-27.2 |
| UF-62 | A standalone cdCDDLe decoder has no rule for two kinds of reference | GF-27.3 |
| UF-63 | Further editorial points | GF-07.3, GF-09, GF-12.1, GF-14.4, GF-25.2, GF-25.3, GF-27.1, GF-28.1, GF-28.2 |

## 1. Credential Store and Capability Authority

### UF-01 — The Credential Store provider must return a status that provider code may not return
- **Specs:** CREDENTIAL §2 l.55-56, §3 l.308, §4.1 l.342; INTERFACE §5.1 l.3308-3311
- **Issue:** Only the provider holds the slot bindings, so only provider code can make these checks.
  CREDENTIAL requires the result: "The provider MUST reject an undeclared or unauthorized slot with `NOT_AUTHORISED` before accessing its backend or revealing its presence." (CREDENTIAL l.56).
  INTERFACE excludes that status from provider code: "Provider code MAY return or complete with `LOGOS_OK`, `LOGOS_ERR_METHOD_NOT_FOUND`, `LOGOS_ERR_INVALID_PARAMS`, or `LOGOS_ERR_MODULE`." (INTERFACE l.3308).
  Any other status is converted: "A provider result violating these rules MUST be treated as `LOGOS_ERR_MODULE`, without forwarding its diagnostics or contract-response outputs." (INTERFACE l.3311).
  The typed error enums of the contract (CREDENTIAL l.176, l.199-200) hold no denial value.
- **Impact:** A consumer C denied a slot receives `MODULE_ERROR` from a conforming ABI caller, while CREDENTIAL
  requires `NOT_AUTHORISED`. No provider can conform to both specifications.
- **Suggested resolution:** Add a non-revealing denial value to both typed error enums and use it at the four
  cited lines, or let INTERFACE define a provider-originated authorization status for a check a contract defines.

### UF-02 — The provider's authorization integration is named and not defined
- **Specs:** CREDENTIAL §2.2 l.132-134, l.157; CA §3.5 l.417-418; PM §15 l.1638
- **Issue:** CA requires a provider-enforced permission to define its integration: "A permission enforced by a module provider MUST define how the authenticated enforcing provider obtains the applicable authorization for the checked subject, resource, and operation." (CA l.417).
  CREDENTIAL fixes the subject and the checked operation: "The protected invocation integration MUST evaluate the original authenticated caller's permission for the exact operation and assignment." (CREDENTIAL l.132).
  It also fails closed (l.134) and applies the existing decision rules (l.157). It does not define the
  integration's request and result, who may call it, how long a decision stays valid at the provider, or how the
  provider learns of invalidation, all of which CA l.418 requires. No specification defines the term.
  The specified surfaces do not fill the gap. A routed `evaluate` cannot check another subject: "On an ordinary routed call, Runtime MUST reject a supplied `consumer` that differs from the authenticated caller with `NOT_AUTHORISED` without dispatch and MUST NOT replace it." (CA l.93).
  "This rule does not grant ordinary providers access to the Runtime's protected `evaluate` binding." (CA l.421).
  "Grant inspection, grant identifiers, and possession of a module-instance address MUST NOT substitute for authorization." (CA l.420).
  A provider that relies only on specified surfaces therefore fails closed on every administrative operation: "The provider MUST reject the operation if that caller binding or an enforceable authorization result is unavailable." (CREDENTIAL l.134).
- **Impact:** Deployments can differ on decision caching and revocation timing, and a provider built for one
  integration cannot be moved to another.
- **Suggested resolution:** Define the integration in CREDENTIAL, or require a named deployment profile to define
  each item of CA l.418 and add it to the BCP documentation list.

### UF-03 — Audit retention of an evaluated scope conflicts with the marked-payload rule
- **Specs:** CREDENTIAL §2.2 l.139; INTERFACE §1.4.1 l.375, l.379; CA §9 l.1184, l.1207, §9.1 l.1384-1386
- **Issue:** Copying marked request fields into the evaluated scope is permitted, because the method's contract
  defines that use (INTERFACE l.379, CREDENTIAL l.139). The conflict is the audit record. CA retains that scope: "An `evaluate` allow record contains its exact allowed scopes." (CA l.1184).
  INTERFACE forbids it without exception: "Marked payloads and their value-derived identifiers MUST NOT enter logs, audit records, or diagnostics." (INTERFACE l.375).
  CA lets a deployment authorize retention of sensitive constraint values (l.1385). CREDENTIAL does not classify the
  scope fields, although subjects, names, purposes, validity and version all enter the evaluated scope (l.106-121, l.139): "Sensitive constraint values require protection and explicit audit authorization before retention." (CA l.1384).
- **Impact:** A deployment without that authorization fails these evaluations (CA l.1386), so the administrative
  operations cannot succeed. A deployment with it conflicts with INTERFACE l.375.
- **Suggested resolution:** State which request fields are authorization inputs outside the marked-payload rule,
  with a matching exception in INTERFACE §1.4.1, or define an audit form that carries none of the marked values.

### UF-04 — Whether a versionless `inspect` policy scope covers version queries is not decided
- **Specs:** CREDENTIAL §2.2 l.129-130, l.146, §4.1 l.381
- **Issue:** "An `inspect` operation without a version authorizes operation-status inspection, not disclosure of credential versions." (CREDENTIAL l.130).
  That sentence follows one about the evaluated scope, but its verb concerns authorization. Read as a statement
  about a policy scope, it conflicts with the rule for policy scopes: "An absent version in a policy scope permits any version; a present version requires the same version in the evaluated scope." (CREDENTIAL l.146).
- **Impact:** With the same grant, one provider discloses a version and another refuses. The same reading decides
  whether such a scope satisfies the target `inspect` permission of l.381.
- **Suggested resolution:** Say in l.130 whether it describes the evaluated scope or a policy scope.

### UF-05 — A replacement instance cannot be told apart from a forbidden alias of a slot
- **Specs:** CREDENTIAL §1 l.36, §2 l.49, l.58-59; RUNTIME §9.3.17 l.3419; BCP §5.4 l.371
- **Issue:** A slot belongs to one module-instance address (l.49), and an upgrade produces a new address. Migration
  belongs to a module-specific procedure or deployment profile (RUNTIME l.3419), and slot bindings are protected
  deployment input (l.58). CREDENTIAL does not say whether that input may rebind a slot to the replacement, given "Different caller identities MUST NOT alias the same slot." (CREDENTIAL l.59).
  It defines no removal of the old slot (l.36).
- **Impact:** One deployment rebinds the slot on upgrade and another treats that as an alias, so consumer C keeps
  its credential under the first and loses it under the second.
- **Suggested resolution:** State that a deployment may rebind a slot to the replacement of the same logical owner,
  retiring the earlier binding, and define what happens to an abandoned slot.

### UF-06 — Whether the administrative permission passes through saved permission settings is not stated
- **Specs:** CREDENTIAL §2.2 l.132; CA §3.3 l.369; RUNTIME §9 l.1533, §9.3.4 l.2461-2465
- **Issue:** Saved settings are described as operating-system settings (RUNTIME l.1533), but no rule excludes
  `logos.credential-store.administration` from them, and RUNTIME l.2461-2462 accepts any known definition.
  CA applies to every declared permission: "A declared permission that those settings omit is denied and does not by itself prevent execution." (CA l.369).
  The text does not say whether that denial binds the provider's check at CREDENTIAL l.132. If saved settings do bound
  this permission, the unique-name rule at RUNTIME l.2463 caps an instance at one administrative scope.
- **Impact:** A module that declares the permission and holds a grant, with settings that omit it, is allowed by
  one provider and denied by another.
- **Suggested resolution:** State that provider-enforced permissions are outside saved permission settings and
  outside CA l.369, or state that the denial applies.

### UF-07 — A resolved but hidden `issue_grant` target has no assigned outcome
- **Specs:** CA §2 l.76-77, §7 l.800, l.804, l.810
- **Issue:** An unknown target, or one on a Runtime that is not enrolled, is `invalid-request` (l.76-77, l.800). CA
  also requires a visibility step: "MUST establish visibility of that grant or target before it evaluates policy for it." (CA l.810).
  Only a named grant has a defined result when it is hidden (l.804).
- **Impact:** A provider may answer differently for a hidden target and an unknown one, which reveals that the
  hidden target exists.
- **Suggested resolution:** Assign a hidden target the same outcome as an unknown one.

### UF-08 — `revoke_grant` outcomes are not ordered against the permission to revoke
- **Specs:** CA §6 l.736-737, §7 l.794, l.806, l.810-811
- **Issue:** "Revoking an already revoked grant is idempotent and returns its current record." (CA l.736).
  "Attempting to revoke an expired grant returns `grant-not-active`." (CA l.737).
  A visible grant that the consumer may not revoke is `not-authorised` (l.806). The precedence rule of l.794 covers
  denial codes only, and l.810 does not place the grant-state check against policy evaluation.
- **Impact:** The same request by a consumer without revocation permission succeeds on one provider and fails on
  another.
- **Suggested resolution:** Order the grant-state check against the revocation policy check for `revoke_grant`.

### UF-09 — A clarifying note: whose authority covers the permissions of a started module
- **Specs:** CA §3.3 l.326, l.341, l.368, §5 l.475, §10 l.1437
- **Issue:** This is a consequence of the rules, not a gap. For a start requested by controller O, O's authority
  must cover both the execution scope and the permission scopes mapped from target M's settings (l.326, l.341,
  l.368), and a grant to M cannot support that decision (l.1437). The generic permission scope names no target, so
  a grant to O is specific to M only if the permission's own constraints name M.
- **Impact:** A policy author can expect a grant to M to authorize M's start. Implementations that follow the text
  agree, but the outcome has to be derived from five rules.
- **Suggested resolution:** Add one sentence to CA §3.3 stating this consequence.

## 2. Contract extensions and release compatibility

### UF-10 — A `0.0.x` patch release must keep its contracts and may also drop them
- **Specs:** PM §11 l.1229, l.1235-1237
- **Issue:** "A release that differs from an earlier release only in its patch component MUST provide exactly the contracts that the earlier release provides." (PM l.1235).
  Release `0.0.4` meets that rule. It is also outside the range of a `compatible` requirement on `0.0.3` (l.1229), and "A release outside that range MAY cease to provide a contract." (PM l.1237).
  For `1.2.4` after `1.2.3`, "exactly" at l.1235 meets "MAY provide additional contracts" at l.1236. No precedence is stated.
- **Impact:** A producer cannot tell whether `0.0.4` may drop a contract, or whether `1.2.4` may add one.
- **Suggested resolution:** Say that the patch rule takes precedence over l.1236 and l.1237.

### UF-11 — A package "provides" a contract through a module that is not selected on this host
- **Specs:** PM §5 l.814, §7.1 l.968-970, §11 l.1215-1216, l.1289-1291
- **Issue:** "A package provides a contract when one of its module declarations declares that commitment as its `primary_contract`, in `implements`, or in `extends`." (PM l.1215).
  That counts a declaration with no implementation in the selected variant: "A module declaration whose implementation artifact is absent from the selected variant is not selected." (PM l.968).
- **Impact:** Consumer C requires contract K. Release 2.0 of package P implements K only on another platform, and
  release 1.5 implements it everywhere. The resolver takes 2.0 as eligible, installation succeeds, and no provider
  of K can exist. An installed record holds selected declarations only (l.814), so a resolver reading it and one
  reading the manifest reach different answers.
- **Suggested resolution:** Define "provides" over the selected module declarations of the candidate's selected variant.

### UF-12 — Four descriptor rules are worded too widely or too narrowly for `extends`
- **Specs:** INTERFACE §1.1 l.110, l.113, §1.2 l.204, §2.6 l.1694, l.1696, l.1711-1712, l.1716; COMMITMENT §9.1 l.970, l.972
- **Issue:**
  1. The duplicate-namespace check of l.1712 is not limited to the `interfaces` array, although an earlier interface
     always shares its successor's namespace, as l.1696 and l.1711 require.
  2. "For each `extends` entry it MUST also establish the extension relation against the described contract that has the same schema namespace" (INTERFACE l.1711) does not say which contract is meant when a `primary` and an `interfaces` contract share a namespace. No rule forbids that, and COMMITMENT l.970 lets the relation hold only between contracts of the same role.
  3. "Adding declarations is the only change an extension permits." (INTERFACE l.204) is narrower than COMMITMENT l.972, which also lets the extending contract implement more interfaces.
  4. "An entry for an earlier concrete module contract follows the rules for `primary`, and an entry for an earlier interface contract follows the rules for `interfaces`." (INTERFACE l.1694). Read with "The interface entries provide the exact resolved `_implements` set used when constructing and validating the primary contract." (INTERFACE l.1716), an earlier concrete entry would be built with every `interfaces` entry, including ones it does not select. INTERFACE l.110 and l.113 settle the input, so this is a wording defect.
- **Impact:** A validator that reads l.1712 literally rejects every provider that offers an earlier interface view.
- **Suggested resolution:** Scope l.1712 to the `interfaces` array, select the compared contract by namespace and
  role in l.1711, and align l.204 with COMMITMENT.

### UF-13 — An extended contract view is disclosed with no required `discover` decision
- **Specs:** CA §3.1 l.253-254; RUNTIME §2.4 l.415, l.430; INTERFACE §2.6 l.1695
- **Issue:** "Runtime MUST obtain one `discover` allow decision for the selected provider and each exact primary or interface contract in its validated call surface." (CA l.253).
  The validated call surface now also holds `extends` entries, whose documents a module-selected binding discloses, and `describe_provider` returns them in the complete surface (RUNTIME l.430).
  CA l.254 and RUNTIME l.415 fail on any view that may not be disclosed, without requiring a decision for this kind.
- **Impact:** A consumer denied `discover` on an earlier contract can still receive that contract's document on one
  implementation and be refused on another.
- **Suggested resolution:** Extend CA l.253 to every contract view of the validated call surface.

### UF-14 — Package Manager's extension check does not pair the contracts it compares
- **Specs:** PM §4 l.360, §9 l.1141; INTERFACE §2.6 l.1711
- **Issue:** "When a module declaration's contract and a commitment in its `extends` both have entries, Package Manager MUST verify the extension" is at PM l.360, and the sentence does not say which declared contract is compared. Take a declaration with primary P and interface I, where P has no entry, I and E have entries, and E is an earlier revision of P. A literal reading compares I with E and fails, while l.1141 defers the check because P cannot be constructed.
- **Impact:** Two Package Managers return `invalid-package` and success for the same signed package.
- **Suggested resolution:** Pair each `extends` entry with the declared contract of the same schema namespace and role.

### UF-15 — `input_artifacts` has no canonical order or uniqueness rule
- **Specs:** PM §4 l.259, l.345-353, l.356
- **Issue:** The canonical-order list that follows "All other manifest arrays use canonical order:" (PM l.345) omits `input_artifacts`, and no other rule orders it or forbids duplicates. No rule says whether the optional array (l.259) may be present and empty.
- **Impact:** Implementations can disagree on rejecting a manifest, and two producers can sign different commitments
  for the same content.
- **Suggested resolution:** Add `input_artifacts` to the list with a uniqueness rule, and require it to be non-empty when present.

### UF-16 — "Validated as a Logos-defined contract" is undefined
- **Specs:** PM §4 l.359; INTERFACE §1.3 l.249-262; RUNTIME §1.3 l.292-293
- **Issue:** "A document that defines a contract under a name reserved by LOGOS-MODULE-INTERFACE Section 1.3 is validated as a Logos-defined contract," (PM l.359).
  The phrase occurs only here. The cited section reserves names and lists no separate validation.
- **Impact:** For a document under a reserved name that no specification assigns, one Package Manager accepts it and
  another returns `invalid-package`.
- **Suggested resolution:** List the checks that differ, and say whether a reserved name no specification assigns is accepted.

### UF-17 — Optional catalog exclusion makes resolution depend on the implementation
- **Specs:** PM §11 l.1262-1263, l.1279, l.1308, l.1311-1314
- **Issue:** "Package Manager MAY exclude a catalog candidate before obtaining its material when implementation-defined catalog metadata indicates that the candidate has no variant compatible with the target execution environment." (PM l.1311).
  Exclusion is optional and rests on implementation-defined metadata, while "Limit exhaustion and all counter values are determined by the installed state, catalog inputs, and protected policy" (PM l.1279).
  An implementation that does not exclude the candidate charges it (l.1262-1263) and needs its material (l.1308).
- **Impact:** With a tight limit, one implementation finds a closure and another fails. If the candidate's material
  is unavailable, one succeeds with a lower version and another fails with `package-unavailable`.
- **Suggested resolution:** Make exclusion a deterministic rule over a defined input, or exempt it explicitly from
  the determinism and counter rules.

### UF-18 — A packaged native library has no artifact kind
- **Specs:** PM §4 l.317, l.340-341, §7.1 l.964, §10 l.1185-1189
- **Issue:** Every file in a variant needs an artifact record of one of four kinds (l.964, l.317). "A packaged native library is a declared artifact of the selected variant, and the verified-byte binding above applies to its installed path." (PM l.1185).
  `module-binary` is assigned to a module's implementation artifact (l.340-341), and of `resource` and `data` the text says "Neither kind authorizes execution, module realization, application activation, or access to an operating-system resource." (PM l.1189).
- **Impact:** Producers choose different kinds, and a deployment that materializes `resource` artifacts as
  non-executable cannot load a library that another deployment accepts.
- **Suggested resolution:** Name the kind for a dependent native library.

## 3. Schema language and module binding

### UF-19 — `true` and `false` are not stated to be Boolean literals
- **Specs:** cdCDDLe §5.1 l.150, §6 l.232-234, §7.4 l.307-308; INTERFACE §1.1 l.119; LOADER Appendix A l.779; CA Appendix A l.1629; HASH §4 l.135
- **Issue:** RFC 8610 spells a Boolean literal only through the prelude names `true` and `false`. This commit adds: "Of those names, only the primitive types listed in Section 5.1 are predefined; a reference to another prelude name resolves only through an external context." (cdCDDLe l.233).
  Read literally, `true` then needs an external context, which no Logos document can supply (INTERFACE l.119), and the schema is rejected (l.234). The supported subset requires Boolean literals (l.150, l.307-308), and normative contracts use one, such as "? direct_static: true," (LOADER l.779).
  No normative vector or pinned root exercises a Boolean literal.
- **Impact:** Canonicalizers can disagree between emitting a `bool-literal` node and rejecting the schema.
- **Suggested resolution:** State in cdCDDLe §5.1 that `true` and `false` denote Boolean literals, except them from
  l.233, and add a vector.

### UF-20 — A queued invocation-scoped delivery at the cutoff has no stated outcome
- **Specs:** INTERFACE §2.5 l.1406, l.1472, §2.8 l.1921; RUNTIME §7.3.1 l.1196, l.1200
- **Issue:** The commit makes a delivery that reaches a handler active on another thread wait in a queue (l.1406).
  Admission is per callback (l.1921, RUNTIME l.1196), so a queued delivery that has not begun must not run after "No new scoped-event commitment is permitted after terminal Response commitment or processed cancellation." (RUNTIME l.1200).
  The text does not say whether that event was admitted to the subscription: "A binding MUST NOT discard an individual event admitted to an active subscription; it delivers every such event in order or ends the subscription." (INTERFACE l.1472).
- **Impact:** One binding omits the event and keeps the subscription, and another ends the subscription.
- **Suggested resolution:** State which of the two applies to a scoped delivery still queued at the cutoff.

### UF-21 — Release does not cover subscription-end callbacks
- **Specs:** INTERFACE §2.5 l.1483-1484, §2.8 l.1954
- **Issue:** "Release MUST suppress terminal callbacks that have not begun and wait for active terminal callbacks as well as active event handlers." (INTERFACE l.1484).
  The spec treats a subscription-end callback as a separate term, and the matching duty exists only for the initialization binding at l.1954. Callback state need only stay valid until release returns (l.1483).
- **Impact:** A binding that waits only for what l.1484 names can return from release while a subscription-end
  callback is running, and that callback then uses freed state.
- **Suggested resolution:** Extend l.1484 to subscription-end callbacks for every binding and handle release.

## 4. Runtime Control and Transport

### UF-22 — No rule says when a selected facade stays on the invocation path
- **Specs:** RUNTIME §9.3.12 l.2949, §9.3.13 l.2998, l.3027-3028, §9.3.14 l.3121
- **Issue:** For any one route the text gives one answer: "A route established by resolving a continuation depends only on its final target provider and the authorization of that route." (RUNTIME l.3027).
  A route whose selected provider is the facade ends with it. But "A contacted Runtime MAY return a continuation for a selected remote facade as defined below." (RUNTIME l.2998), and l.2949 treats a facade on the path as an implementation property, so nothing chooses between the two.
- **Impact:** The same facade failure leaves a route `ready` under one Runtime and ends it under another.
- **Suggested resolution:** State when a selected facade must be resolved through a continuation and when it stays on the path.

### UF-23 — No inter-Runtime operation ends a route owned by the other Runtime
- **Specs:** RUNTIME §3.4 l.589-591, §9 l.1705-1706, §9.3.11 l.2895, §9.3.13 l.3022
- **Issue:** After resolution, the route record belongs to the target Runtime T (l.3022). The consumer's Runtime S must still act: "During a stop other than an unexpected realization failure, Runtime MUST close every route whose consumer is that module instance." (RUNTIME l.589).
  No defined operation carries that end to T, and l.1705 leaves such coordination to an internal protocol.
- **Impact:** Until `expires_at` (l.2895) or another independent rule ends the route, T can report `ready` for a
  consumer that has stopped or failed, and `failed` with `consumer-unavailable` cannot be recorded at T by any
  defined means.
- **Suggested resolution:** Define how S reports a consumer's end to T, or limit l.589-591 to routes the Runtime owns
  and state S's duty for a route that T owns.

### UF-24 — Route identifiers can collide between consumers of one Runtime
- **Specs:** RUNTIME §9.3.2 l.2403, §9.3.13 l.3022, l.3025, §9.3.15 l.3271
- **Issue:** "If a resolved route's identifier equals that of a different route the consumer already holds, Runtime MUST fail that resolution with `TRANSPORT_ERROR` and MUST NOT return the route." (RUNTIME l.3025).
  The check covers one consumer's routes, so consumers C1 and C2 at S can hold different routes with the same identifier. `route_state_changed_event` does not require the owning Runtime (l.2403), and the text does not say whether `list_routes` at S returns routes that another Runtime owns.
- **Impact:** An observer cannot tell which route an event describes. If `list_routes` returns such routes, the sort
  key of l.3271 has no tie-break.
- **Suggested resolution:** Require S to keep identifiers unique across every route it exposes, or add the owning
  Runtime to the event and the sort key.

### UF-25 — RUNTIME and CONFIG order the revision check differently
- **Specs:** RUNTIME §9.3.1 l.1824-1831, §9.3.5 l.2539; CONFIG §1 l.51, §5 l.194, l.203, §8 l.305
- **Issue:** RUNTIME places every precondition row after the comparison: "5. comparison of an expected revision, which produces `stale-revision`;" (RUNTIME l.1830).
  CONFIG excepts the first row: "Runtime evaluates the first row before the revision comparison and the remaining rows after it." (CONFIG l.203).
  RUNTIME l.2539 imports the CONFIG mappings, but neither text says which order prevails.
- **Impact:** For a target with no configuration binding and a non-matching expected revision, one Runtime returns
  `stale-revision` and another `INVALID_PARAMS`.
- **Suggested resolution:** Add to RUNTIME step 5 an exception for the first row of the CONFIG §5 table.

### UF-26 — A failed continuation resolution has no assigned code
- **Specs:** RUNTIME §9.3.13 l.3025, l.3058, l.3062-3063
- **Issue:** "Resolution of a selected provider MUST fail on a cycle or exhaustion of implementation-defined bounds." (RUNTIME l.3058).
  A cycle, exhausted bounds, failed authentication at a next hop, and an unreachable next hop not already reflected as an unavailable facade have no assigned shared code. An identifier collision (l.3025), a denial (l.3062) and an unavailable provider (l.3063) do.
- **Impact:** For the same cycle, Runtimes return different codes, and consumer C cannot tell whether a retry can succeed.
- **Suggested resolution:** Assign one shared code to each of these causes, subject to the non-disclosure rule at l.3060-3061.

### UF-27 — During termination, an Unsubscribe after a SubscriptionEnd has two required results
- **Specs:** TRANSPORT §5.1 l.755, §8.1 l.972, l.977
- **Issue:** "An Unsubscribe for a subscription that the callee has ended with a SubscriptionEnd MUST produce a successful SubscriptionResult." (TRANSPORT l.755).
  "A Subscribe or Unsubscribe processed during termination MUST receive a failed SubscriptionResult with `NOT_AUTHORISED` and MUST NOT change subscription state." (TRANSPORT l.972).
  No sentence orders the two.
- **Impact:** During session termination, one callee reports success and another failure for the same Unsubscribe.
- **Suggested resolution:** State which rule takes precedence during termination.

## 5. Editorial

### UF-28 — The consequence of extending an implemented interface is unstated
- **Specs:** COMMITMENT §9.1 l.963, l.972; INTERFACE §1.2 l.199, l.206; PM §11 l.1236-1237
- **Issue:** One primary contract cannot implement a new revision of an interface and also extend a primary that
  implements the earlier revision (COMMITMENT l.963, l.972). The rules determine this, and INTERFACE l.199 and l.206
  give the alternatives, but no sentence states it.
- **Suggested resolution:** State the consequence in INTERFACE §1.2 and PM §11.

### UF-29 — RUNTIME l.504 still speaks of rejecting one provider view
- **Specs:** RUNTIME §3.3 l.504, §3.6 l.681-682, §9.3.19 l.3612; PM §12 l.1441
- **Issue:** Any difference between handoff and descriptor keeps the instance from becoming ready (l.682, PM l.1441),
  while l.504 speaks only of rejecting that view. No specific failure classification names the cause, so `failure` is `other` (l.3612).
- **Suggested resolution:** Align l.504 with l.682 and name a classification.

### UF-30 — The selected contract is defined without extended contracts
- **Specs:** RUNTIME l.91-92, §2.4 l.398, §3.2 l.466-467, §3.3 l.484-485, §3.5 l.639-640, §4.2 l.863, l.869-870, §8 l.1455-1456, §9.3.10 l.2846-2848, l.2852, l.2856-2857, §9.3.13 l.2995; TRANSPORT §3.1 l.453-456, l.479-481
- **Issue:** "The selected contract is the exact concrete module contract or implemented interface contract used for provider selection and route validation." (RUNTIME l.863).
  RUNTIME l.91-92, l.2852 and l.2995 add the extended contract. RUNTIME l.398, l.466-467, l.484-485, l.639-640, l.869-870, l.1455-1456, l.2846-2848 and l.2856-2857, and TRANSPORT l.453-456 and l.479-481, enumerate the same two forms as l.863.
- **Suggested resolution:** Add the extended contract to those enumerations, starting with the definition at l.863.

### UF-31 — Five reference definitions share one line
- **Specs:** PM References l.2101
- **Issue:** Five link reference definitions were joined onto l.2101, so references such as `[DSSE v1]` at l.616 no longer
  resolve when the text is rendered. This was read against the CommonMark rule, not run through a parser.
- **Suggested resolution:** Restore one definition per line.

### UF-32 — The state pairs a facade may report are not listed
- **Specs:** RUNTIME §3.4 l.528, l.561-563, §9.3.19 l.3616-3617
- **Issue:** The transition table binds module instances, and a facade is not one (l.561). Facade states are defined by
  condition (l.3616-3617), and no list gives the `old_state` and `new_state` pairs that `module_state_changed_event` may report for a facade.
- **Suggested resolution:** List the pairs, or say that any pair the conditions produce is valid.

### UF-33 — Two references do not reach their text
- **Specs:** RUNTIME §7.5 l.1293, §9.3.13 l.3060-3061, §9.3.14 l.3204
- **Issue:** "drain, or close dependent routes according to runtime authority policy." (RUNTIME l.3204) names an outcome with no state or operation, because `route_state` no longer has `draining`.
  "Unknown, hidden, or denied targets use the non-revealing authorization behavior defined in Section 4." (RUNTIME l.1293) cites a rule that is at l.3060-3061.
- **Suggested resolution:** Delete "drain," and point l.1293 to Section 9.3.13.

### UF-34 — Example B.3 shows a ready instance at revision 1
- **Specs:** RUNTIME §9.3.17 l.3368, Appendix B.3 l.4057-4061
- **Issue:** The record has "revision: 1," (RUNTIME l.4057) and "intent_revision: 1" (RUNTIME l.4059) with `state: "ready"` at l.4061.
  The revision advances at each lifecycle change (l.3368), so a ready instance cannot still be at the revision of its intent.
- **Suggested resolution:** Give `revision` a larger value in the example.

## 6. Findings first raised in `gemini-spec-comments.md`

Each finding below was first raised in `gemini-spec-comments.md`, in the item named under **Origin**. The statement here is the
one the specs support.

### UF-35 — A manifest can declare only one administrative scope
- **Specs:** PM §4 l.339; CREDENTIAL §2.2 l.98, §4.1 l.376, l.381; CA §3.3 l.365-366
- **Origin:** GF-03.1.
- **Issue:** "Within one module declaration, implemented contract commitments, extended contract commitments, required contract commitments, and requested permission names MUST each be unique." (PM l.339).
  The constraints of `logos.credential-store.administration` are one scope (CREDENTIAL l.98). The `issue` operation needs "`issue` permission on the exact issuer version and `inspect` permission on the exact target version." (CREDENTIAL l.381), and l.376 needs a `generate` and `issue` pair.
- **Impact:** A manifest cannot declare what such a consumer needs. The authority itself can still be granted, because
  CA l.365-366 keeps declarations separate from grants, so policy review works from an incomplete declaration.
- **Suggested resolution:** Let the permission's constraints carry a canonically ordered list of scopes.

### UF-36 — Retained operation records can never be released
- **Specs:** CREDENTIAL §3 l.312, §4.1 l.422-426
- **Origin:** GF-06.
- **Issue:** "The provider MUST bound retained operation data and reject new admission with `capacity` before exhausting that bound." (CREDENTIAL l.422).
  A retired operation keeps its identifier, comparison data and outcome (l.423), and "Retiring a record MUST NOT make its identifier available for a new operation or turn an uncertain outcome into `absent`." (CREDENTIAL l.426).
  No rule ever lets the remainder go.
- **Impact:** An assignment with continuing operations reaches `capacity` unless the deployment raises its configured
  limit (l.312).
- **Suggested resolution:** Define a bounded retirement mechanism, such as a per-assignment floor below which a retried
  operation returns `unavailable`.

### UF-37 — A zero `validity_seconds` has no assigned error
- **Specs:** CREDENTIAL §2.2 l.147, §3 l.212, l.307-308
- **Origin:** GF-07.1, first point.
- **Issue:** The schema admits zero (l.212). "For issuance, each evaluated set MUST be a subset of its policy set, and evaluated validity MUST be positive and no greater than the policy limit." (CREDENTIAL l.147).
  That makes zero a containment failure, which is `NOT_AUTHORISED` (l.308), while "Invalid request shapes, names, identifiers, and certificate constraint sets MUST fail with `INVALID_PARAMS`." (CREDENTIAL l.307) can be read to cover it.
- **Impact:** The same request receives `INVALID_PARAMS` from one provider and `NOT_AUTHORISED` from another.
- **Suggested resolution:** State which of the two applies.

### UF-38 — `extends` may repeat the module's own contract, which makes the module unrealizable
- **Specs:** PM §4 l.339, l.360, §9 l.1141, §12 l.1441; RUNTIME §8 l.1358; INTERFACE §2.6 l.1712
- **Origin:** GF-13.1.
- **Issue:** Uniqueness applies within each array (PM l.339), so a manifest with `primary_contract` R and `extends` [R]
  passes PM l.360 and l.1141. A descriptor of that shape fails, because the validator "MUST reject an unknown profile identifier, a root mismatch, duplicate contract identity, duplicate interface namespace, missing or unused supporting schema," (INTERFACE l.1712).
  No other descriptor can match, since Runtime "MUST require the descriptor's optional primary contract, implemented-interface set, and extended-contract set to match the handoff exactly." (PM l.1441).
- **Impact:** The package installs and can never be realized. The failure is safe but arrives late.
- **Suggested resolution:** Require `extends` to be disjoint from `primary_contract` and `implements`.

### UF-39 — A manifest that omits an implemented interface installs and then fails
- **Specs:** PM §9 l.1123, l.1139-1140, §12 l.1441; INTERFACE §2.6 l.1717
- **Origin:** GF-13.4.
- **Issue:** "Package Manager MUST reject any `implements` entry that is not committed by that concrete contract." (PM l.1140).
  That catches an extra entry and not a missing one. The exact match of PM l.1441 and INTERFACE l.1717 then fails at
  realization.
- **Impact:** Package P passes every installation check and no instance of it can become ready.
- **Suggested resolution:** Require `implements` to equal the primary contract's `_implements` whenever Package Manager
  can compute that contract's identity.

### UF-40 — An unsupported manifest schema has no outcome at two later points
- **Specs:** PM §4 l.371, §4.3 l.565-568, §11 l.1218, §15 l.1662-1665, l.1686-1689, Appendix A l.1896
- **Origin:** GF-23.4.
- **Issue:** Three points remain.
  1. The claim's commitment model is a literal (l.1896), so a package naming a later model fails claim decoding and is
     reported under "Any other failure produces `signature-verification-failed`" (PM l.568), not as `unsupported-manifest`.
  2. "An installed record whose retained manifest commitment names such a schema is ineligible in the same way and is not an artifact-integrity failure." (PM l.1218). `get_runtime_handoff` (l.1662-1665) has no outcome for that record.
  3. The retained signer can be replaced (l.1686), and the text does not say whether `source` changes with it.
- **Impact:** A consumer cannot tell a package that is too new from a forged one, and implementations differ on the
  handoff of a retained record.
- **Suggested resolution:** Classify an unknown commitment model as `unsupported-manifest`, assign that error to the
  handoff, and state whether signer replacement updates `source`.

### UF-41 — Two cross-field rejections belong to no step of the order of checks
- **Specs:** RUNTIME §9.3.1 l.1824-1833, §9.3.18 l.3524-3525
- **Origin:** GF-14.2.
- **Issue:** "A request supplying both selectors MUST produce `INVALID_PARAMS` without structured detail." (RUNTIME l.3524).
  "A request supplying `provider` and `expected_execution_revision` MUST produce `INVALID_PARAMS` without structured detail because a facade has no local execution-intent revision." (RUNTIME l.3525).
  The schema admits both combinations, so they are not step 3 failures, and no other step names them.
- **Impact:** A caller without target authority that sends either combination receives `INVALID_PARAMS` from one Runtime
  and `NOT_AUTHORISED` from another.
- **Suggested resolution:** Place both rejections in a named step, before target authorization.

### UF-42 — When a blocking `failure` classification clears is not stated
- **Specs:** RUNTIME §9.3.19 l.3611, l.3613, l.3618
- **Origin:** GF-18.3.
- **Issue:** Runtime is told to "clear it when a new execution attempt is accepted or an explicit stop completes successfully" (RUNTIME l.3611).
  Those events are not said to be the only ones. For an `unloaded` instance classified `configuration-missing`, the text
  does not say whether the classification ends when valid configuration is staged or at the next accepted attempt.
- **Impact:** Two Runtimes report different `failure` values for the same instance in that interval.
- **Suggested resolution:** State whether a classification under l.3613 clears when its condition ends.

### UF-43 — A route survives at its target after an identifier collision fails the resolution
- **Specs:** RUNTIME §9.3.13 l.3025, l.3066-3069
- **Origin:** GF-19.1. UF-24 covers the collision itself.
- **Issue:** "Runtime MUST fail that resolution with `TRANSPORT_ERROR` and MUST NOT return the route." (RUNTIME l.3025).
  The target Runtime has already established the route, and no rule makes the consumer's Runtime close it. A validity end
  is mandatory only for a Capability Authority allow decision (l.3066-3069).
- **Impact:** The target keeps a `ready` route that no consumer holds, until expiry or other enforcement.
- **Suggested resolution:** Require the consumer's Runtime to attempt closure of the target route when it fails a
  resolution under l.3025.

### UF-44 — A consumer may close its own route, and method authorization can refuse it
- **Specs:** RUNTIME §9 l.1540, §9.3.1 l.1827-1828, §9.3.16 l.3347-3348
- **Origin:** GF-19.2.
- **Issue:** "The route's consumer may close its own route." (RUNTIME l.3347).
  Authorization of the method comes first, with three named exceptions: "except that `get_self`, `get_execution_permissions`, and `report_failure` use their caller-bound authorization rules." (RUNTIME l.1540).
  Step 2 authorizes the method before the request is decoded (l.1827), so the route is not yet known.
- **Impact:** A consumer without a `close_route` grant is admitted under one rule and refused under the other.
- **Suggested resolution:** Add `close_route` on the caller's own route to the exceptions of l.1540, and define that check
  after decoding.

### UF-45 — The check on marked methods reads the requested route in one place and the permitted route in another
- **Specs:** RUNTIME §9.3.1 l.1808, §9.3.12 l.2935, l.2939, §9.3.13 l.3070
- **Origin:** GF-20.1.
- **Issue:** The error table lists "A requested remote route permits a marked method that the selected remote profile cannot carry." (RUNTIME l.1808).
  RUNTIME l.2939 tests "the permitted method scope" instead. With an absent method list, which "permits every method in the selected contract" (l.2935), and an allow decision narrowed to unmarked methods (l.3070), l.1808 requires `INVALID_PARAMS` and l.2939 does not reject the route.
- **Impact:** The same request succeeds on one Runtime and fails on another.
- **Suggested resolution:** State whether l.1808 applies to the requested access or to the access left after narrowing.

### UF-46 — A provider rejected for a marked method has no place in a multi-provider result
- **Specs:** RUNTIME §9.3.1 l.1808, §9.3.12 l.2939, §9.3.13 l.3005-3010, l.3047
- **Origin:** GF-20.2.
- **Issue:** The omission rule lists failures of listeners, exports, contracts and authority: "For `all-runtime-visible`, Runtime may omit that provider," (RUNTIME l.3009).
  A rejection under l.2939 is not among them, and l.1808 is a failure of the whole request.
- **Impact:** One marked method on one provider either fails the whole request or yields a `partial` result (l.3047).
- **Suggested resolution:** Add the l.2939 rejection to the per-provider failures at l.3005.

### UF-47 — No rule escalates from an unresponsive Module Loader to protected supervision
- **Specs:** RUNTIME §10.1 l.3685-3687; CA §8 l.880
- **Origin:** GF-22.1.
- **Issue:** "When an execution authorization ends, Runtime MUST withdraw the dependent execution access and initiate required termination without waiting for re-evaluation or a renewal response." (CA l.880).
  For a Loader that stays live and stops answering, "Failed Loader operations or loss of its binding while that provider instance remains `ready` are temporary service unavailability." (RUNTIME l.3687), so the supervision path of l.3685 is not reached.
- **Impact:** Termination that authority requires can wait without limit on a Loader that does not answer.
- **Suggested resolution:** Require protected host or deployment supervision when termination through the owning Loader
  does not complete within a finite deadline.

### UF-48 — A duplicate SubscriptionEnd is not classified
- **Specs:** TRANSPORT §3.4 l.569, l.572
- **Origin:** GF-15.2.
- **Issue:** "A SubscriptionEnd MUST identify a subscription active according to the received successful SubscriptionResults." (TRANSPORT l.569).
  A second SubscriptionEnd for one identifier passes that test, and the duplicates named at l.572 are a Response and a
  SubscriptionResult only.
- **Impact:** One receiver accepts the message and another closes the session.
- **Suggested resolution:** Make l.569 require a subscription for which no SubscriptionEnd has already been received.

### UF-49 — A subscription-end callback is not ordered against the return of `unsubscribe`
- **Specs:** INTERFACE §2.5 l.1465-1466, l.1478, l.1482-1483
- **Origin:** GF-15.3.
- **Issue:** "`unsubscribe` for a binding-ended subscription returns `LOGOS_OK`." (INTERFACE l.1482).
  The text does not say whether the callback of l.1478 may begin or still be running after that return. Callback state stays valid until release (l.1483), so this is no lifetime hazard.
- **Impact:** Consumer C cannot use the return of `unsubscribe` as a barrier for per-subscription bookkeeping.
- **Suggested resolution:** State that the two are unordered, or require `unsubscribe` to wait for the callback.

### UF-50 — An oversized invocation-scoped Event has no assigned code
- **Specs:** TRANSPORT §2.1 l.379-380, l.383; INTERFACE §2.9.3 l.2154-2158; RUNTIME §7.3 l.1150
- **Origin:** GF-16.
- **Issue:** "Its publication boundary MUST report failure where that boundary permits it; otherwise the sender MUST send ProtocolError `TRANSPORT_ERROR` when writable and close the affected connection." (TRANSPORT l.383).
  Invocation-scoped `publish` can report failure, yet INTERFACE l.2154-2158 names no code for this case. The oversized Request and Response use `MODULE_ERROR` (TRANSPORT l.379-380).
- **Impact:** Bindings return different codes for the same oversized Event.
- **Suggested resolution:** Add to INTERFACE §2.9.3 that such an Event produces `MODULE_ERROR`.

### UF-51 — The thread that drains queued deliveries has no limit on its work
- **Specs:** INTERFACE §2.5 l.1406-1407, l.1473
- **Origin:** GF-17.2. UF-20 covers the outcome of a queued delivery at the cutoff.
- **Issue:** "The thread running the active invocation MUST run the queued deliveries for that subscription in publication order before another thread may begin a handler invocation for it." (INTERFACE l.1407).
  While another thread publishes at least as fast as the handler completes, the draining publish call does not return. The bound is optional: "A binding MAY end a subscription when its pending deliveries reach an implementation-documented bound." (INTERFACE l.1473).
- **Impact:** A publisher that reached a busy subscription can be held for an unbounded time by other publishers.
- **Suggested resolution:** Require a finite queue bound for each subscription, and limit the deliveries one active
  invocation must drain.

### UF-52 — A surviving session is not rebound to the decision that replaces its own
- **Specs:** CA §8 l.897-898, l.939; TRANSPORT §8.1 l.914, l.936; RUNTIME §9.3.16 l.3337-3338
- **Origin:** GF-21. Point 6 of TF-33 asks the same question.
- **Issue:** "An allow decision covering the bound scope keeps the route, replaces its `decision_id`, and sets `expires_at` to the earlier of its current value and the new validity end." (CA l.939).
  A session is bound to an authority decision (TRANSPORT l.936), and "The session MUST end when its bound decision expires or is revoked." (TRANSPORT l.914). Neither text says whether the session follows the replacement.
- **Impact:** After a policy change that allows the route, one Runtime keeps the session and another ends it.
- **Suggested resolution:** State that a session kept under CA l.939 is governed by the route's current decision and
  `expires_at`.

### UF-53 — Coverage for `issue_grant` does not separate holding a scope from issuing it
- **Specs:** CA §6 l.684, §7 l.791-792
- **Origin:** GF-23.1.
- **Issue:** "Authority to invoke `issue_grant` does not itself permit the requested grant; active policy MUST allow the consumer to issue the requested scopes to that target." (CA l.684).
  The coverage test asks only whether a rule "applies to the consumer and contains a scope of the same kind and action as a requested scope," (CA l.792), and "`evaluate` and `issue_grant` use these codes." (CA l.791).
- **Impact:** An issuer that holds scope S for itself, with no right to issue S, receives `scope-denied` or a grant-state
  code and not `not-granted`.
- **Suggested resolution:** Define coverage for `issue_grant` over rules that authorize issuing the requested scopes to the
  target.

### UF-54 — A `query_audit` result larger than one message has no stated outcome
- **Specs:** CA §6 l.702, §9 l.1159-1163, l.1199; TRANSPORT §2.1 l.380
- **Origin:** GF-23.2.
- **Issue:** "`query_audit` returns at most the 1000 most recent retained records that match the request and are visible to the authenticated consumer." (CA l.1159).
  `list_grants` has an explicit rule: "Each response returns at most the applicable limit and MAY return fewer records to remain within the Core Transport message-size ceiling." (CA l.702). `query_audit` has none, and records can be large enough to reach the limit (l.1199).
- **Impact:** One provider returns the most recent records that fit, and another fails with `MODULE_ERROR`.
- **Suggested resolution:** Give `query_audit` the rule of CA l.702, keeping most-recent-first order.

### UF-55 — How a selector applies when a Runtime Control subscription is activated is not stated
- **Specs:** CA §3.2 l.301-305, §5 l.556; RUNTIME §9.3.17 l.3362, §9.3.19 l.3589; INTERFACE §5.2 l.3705-3711
- **Origin:** GF-23.3.
- **Issue:** "Every present constraint MUST match the attempted operation or returned observation." (CA l.301).
  A subscription activation names only an event and has no record subject. RUNTIME expects a check per record: "Event observation authority MUST be checked for that exact instance or provider before delivery commitment." (RUNTIME l.3362). Whether a scope narrowed by a selector admits the activation is not said.
- **Impact:** A subscriber with a narrowed scope is admitted and filtered by one Runtime and refused by another.
- **Suggested resolution:** State that selectors are evaluated per delivered record and do not by themselves prevent
  activation for an allowed event.

### UF-56 — A list output exposes response storage through a mutable pointer
- **Specs:** INTERFACE §2.3 l.974-976, §2.4 l.1254, §2.7.1 l.1834-1835
- **Origin:** GF-24.2. Tested with Apple clang 21.0.0.
- **Issue:** "Its output uses adjacent `<type>** out_<name>` and `size_t* out_<name>_count` parameters." (INTERFACE l.1254).
  List elements are const elsewhere (l.974-976), and "Every referenced region MUST remain readable and unchanged until the owner is cleared." (INTERFACE l.1834).
- **Impact:** A C++ provider that returns const static storage, which l.1835 allows, needs a `const_cast`. Without the
  cast, the assignment is an error in C++17 and a warning in C11.
- **Suggested resolution:** Change the output to a pointer to the const-qualified list pointer of l.974-976.

### UF-57 — A named declaration whose body is a reference to an aggregate has no C form
- **Specs:** INTERFACE §2.3 l.993-1001, l.1036-1041, §3.4
- **Origin:** GF-25.1.
- **Issue:** "**Named aliases and aggregates.** Every named CDDL type retains its declaration identity in C:" (INTERFACE l.993).
  The forms listed after that sentence and §3.4 give no C declaration and no reverse mapping for a declaration whose body
  is a local or imported reference to an aggregate. COMMITMENT l.1723 and HASH l.1294-1305 use such declarations.
- **Impact:** Two generators emit different C for the same contract, so their headers do not agree.
- **Suggested resolution:** Require `typedef logos_<target>_t logos_<ns>_<Alias>_t;` with its reverse mapping, and state
  which name a recursive pointer uses.

### UF-58 — The listing of `logos_types.h` does not compile as written and cannot be included twice
- **Specs:** INTERFACE §2 l.612, l.624, §3.2 l.2242, l.2289, §5.2 l.3325, l.3373-3822
- **Origin:** GF-25.2, first and second points. Both tested with Apple clang 21.0.0 in C11 and C++17.
- **Issue:** "The listing below states those declarations completely; a tool copies them and does not derive them." (INTERFACE l.3325).
  1. l.3814 and l.3818 are per-module templates containing `<module-C>`, which belong in a provider header under l.2242.
     With those two lines removed, the listing compiles.
  2. The listing has no include guard, while "Generated contract headers MUST include `logos_types.h` and check the generation they target before any declaration-suppressing guard." (INTERFACE l.624). Two generated headers in one translation unit therefore fail with enumerator redefinitions.
- **Impact:** A tool that copies the listing exactly produces a header that does not compile.
- **Suggested resolution:** Move the two templates out of the listing, add an include guard, and require that the header be
  safe to include repeatedly.

### UF-59 — COMMITMENT does not state what an absent optional reference field commits to
- **Specs:** HASH §7.3 l.592, §7.4 l.604, l.656; COMMITMENT §9.3 l.1228-1231
- **Origin:** GF-26.1.
- **Issue:** HASH fixes the absent payload's identity: "and the record carries the identity of the field's value schema." (HASH l.656).
  COMMITMENT's `absent-value` (l.1228-1231) does not say what its field `1` holds for an optional field of reference
  type. The two specifications do not state opposite rules, but a reader of COMMITMENT alone can apply its child-value
  rule instead.
- **Impact:** An implementation built from COMMITMENT can compute a different commitment from one built from HASH.
- **Suggested resolution:** State in COMMITMENT §8 that field `1` is the identity of the referring field's value schema,
  for local and imported references alike.

### UF-60 — No value vector covers three shapes that involve references
- **Specs:** COMMITMENT Appendix A l.1412, Appendix B; HASH Appendix B
- **Origin:** GF-26.2, third point.
- **Issue:** Neither appendix has a value-commitment vector for an absent optional reference, a list of local aliases, or
  a choice with reference arms. "storage.lookup_key = storage.cid / storage.blob_hash" (COMMITMENT l.1412) covers a choice of references at schema level only.
- **Impact:** Implementations can agree on every published vector and still disagree on these values.
- **Suggested resolution:** Add a value vector for each of the three shapes.

### UF-61 — A verifier's handling of `.size` and of U+0000 in a disclosed range is not stated
- **Specs:** HASH §7.6 l.972, §8 l.1096, l.1098; COMMITMENT §7 l.756
- **Origin:** GF-27.2.
- **Issue:** "4. Normalize the disclosed value, disclosed range, or absent marker under the schema selected by the typed path." (HASH l.1098).
  The step does not say that a `.size` constraint applies to the total length and not to the disclosed slice. COMMITMENT
  l.756 forbids U+0000 in text values, but no verifier rule rejects a `0x00` byte in a disclosed text chunk or range.
- **Impact:** Two verifiers reach different verdicts on the same partial view.
- **Suggested resolution:** State in step 4 that `.size` is checked against the total length and that a `0x00` byte in a
  disclosed text chunk or range invalidates the view.

### UF-62 — A standalone cdCDDLe decoder has no rule for two kinds of reference
- **Specs:** cdCDDLe §6 l.232-235, §10, §12 l.631
- **Origin:** GF-27.3.
- **Issue:** "Resolution MAY use an external context supplied by an owning profile, such as LOGOS-MODULE-COMMITMENT-MODEL." (cdCDDLe l.235).
  A decoder or vector has no input for that context (l.631), so a reference that resolves only through it has no defined
  result. Nothing in §10 rejects a `type-reference` whose name is `uint`, `bool`, `tstr` or `bstr`.
- **Impact:** Conforming decoders can accept and reject the same canonical model.
- **Suggested resolution:** Define the treatment of unresolved references, give vectors an external-context input, and
  reject §5.1 primitive names in `type-reference`.

### UF-63 — Further editorial points
- **Origin:** GF-07.3, GF-09, GF-12.1, GF-14.4, GF-25.2 (third point), GF-25.3 (second point), GF-27.1, GF-28.1, GF-28.2.
- **Points:**
  - BCP l.201-202 describes only the caller-owned Credential Store methods, although CREDENTIAL l.37-40 adds administrative
    methods. BCP l.140-148 omits `_sensitive` and `extends`. BCP l.374 does not name the protected invocation and
    assignment integrations that CREDENTIAL l.132 and l.382 require.
  - COMMITMENT l.496-499 and l.805-809 and HASH l.998-1000 do not state the defining schema root for a method reached
    through an extended contract view, although TRANSPORT l.634 and INTERFACE l.1722 determine it.
  - BCP l.453-458 omits extended contract documents and their supporting schemas from the generator inputs, while BCP
    l.476 lists call-surface descriptors as output and INTERFACE l.1657 places those documents in the descriptor.
  - RUNTIME l.1829 lists the foreign-target rejection at step 4, and l.1806 and l.1831 list it as a table row evaluated at
    step 6. Step 4 always fires first, and the row supplies only the code.
  - INTERFACE l.3326 does not say whether the support typedef at l.3432 may be re-emitted by a generated header.
  - INTERFACE l.912 lacks the "except for zero itself" wording used for indices elsewhere, although a zero minimum is a
    valid component.
  - HASH l.1376 describes the rejection cause accurately only for the partial views of N2 to N8. Complete views fail by
    root mismatch at step 7, and the N1 partial view fails by child-record mismatch at step 6.
  - SECURITY l.49-59, l.89, l.385 and l.556-566 omit Credential Store, although CREDENTIAL l.456 places its
    backend-privileged process inside a credential trust boundary.

## 7. What was checked

- An independent implementation reproduced all 52 digests of the normative vectors.
- UF-31 was judged against the CommonMark rule and was not run through a parser.
- Claims about C and C++ compilation were tested with Apple clang 21.0.0 only. GCC was not available.

---

# Response from Claude Fable: the discussion settled

This section closes the discussion that the remarks of Claude Opus and of Gemini opened. It covers the
remarks appended to `claude-spec-comments.md`, `claude-spec-comments-2.md`, `claude-spec-comments-3.md`
and `gemini-spec-comments.md`, and the two responses of Gemini. Every point on which two readings still
differed was decided again from the spec text at `6cac8335`, without starting from either conclusion.
Each `l.N` is a line of the specification file at that revision. Where a verdict accepts a point, the
statement given here is the one the text supports, and it replaces the wording of the claim.

The verdicts mean:

- **Holds:** two conforming implementations can differ, or a producer cannot do what a rule requires.
- **Wording:** one outcome can be derived, and the text should still change.
- **Optional:** one outcome can be derived, and a sentence would only restate it.
- **No defect:** the text states the outcome that the claim says is missing.

## 1. Summary

| Group | Points | Holds | Wording | Optional | No defect |
|---|---|---|---|---|---|
| Points that Gemini reports as left out of this document (section 2) | 8 | 4 | 0 | 0 | 4 |
| Refutations that Gemini answered (section 3) | 7 | 1 | 4 | 1 | 1 |
| Items listed as settled in `claude-spec-comments-3.md` where Claude Opus finds a point (section 4) | 17 | 5 | 8 | 3 | 1 |
| Total | 32 | 10 | 12 | 4 | 6 |

Neither reviewer is right throughout. Of the fifteen points that Gemini kept open, five hold, four
hold as wording, one is optional and five are no defect. Of the seventeen points that Claude Opus raised
against the items that `claude-spec-comments-3.md` lists as settled, sixteen are fair, three of those
need no change to the text, and the text answers the seventeenth.

## 2. Points that Gemini reports as left out of this document

These are the sub-points of section 2 of Gemini's response in `gemini-spec-comments.md`.

| Point | Verdict | What the text supports | Where it goes |
|---|---|---|---|
| GF-23.1, first point: the contract is not part of the action of a `provider-access` scope | No defect | Coverage is decided by kind and action: a rule covers the request when it "contains a scope of the same kind and action as a requested scope, whatever constraints, methods, or events that scope carries" (CA l.792), and l.793 widens the action only for permission and runtime-control scopes. A grant to call contract X therefore covers the action `call`, and a refused call on contract Y is `scope-denied` on every implementation. The outcome is determinate. The owner may want to confirm that it is intended, because `not-granted` then means only that the consumer holds no scope with that action. | A question of intent beside UF-53. No finding. |
| GF-23.1, third point: one requested scope decides coverage, while the lapsed-grant codes test every scope | No defect | `scope-denied` is defined for a request that policy covers in part: "Active policy covers the requested action for the consumer, but a requested scope, method or event list, or constraint exceeds what it allows." (CA l.788). A request with one allowed scope and one scope that no rule names is that case. The codes of l.785-786 test every requested scope because they say what lapsed grants would have allowed. The two tests answer different questions. | None. |
| GF-14.2: a facade selected by module name, with `expected_execution_revision` | Holds | "After an authorized selection of a facade by module name, a request carrying `expected_execution_revision` MUST produce `INVALID_PARAMS` without structured detail." (RUNTIME l.3540). This does not conflict with step 5 of the order of checks (l.1830): a facade record has no execution revision to compare (l.3359), so `stale-revision` cannot arise. It is a third cross-field rejection that no step names. Its own words place it after target authorization. Its order against the precondition rows of step 6 and against step 7 is not given. | Add to UF-41. |
| GF-14.4: forwarding of `renew_route` and `close_route` | Holds | "When a source Runtime forwards a consumer's `renew_route` or `close_route` request for a route established through a target Runtime, the target Runtime applies this order and the source Runtime does not authorize the method itself." (RUNTIME l.1836). Which Runtime a route was established through is known only from the decoded request, and step 2 authorizes the method before decoding (l.1827-1828). For a caller with no local grant for the method, whose request does not decode, one source Runtime returns `NOT_AUTHORISED` and another `INVALID_PARAMS`. This is the dependency that UF-44 describes for a consumer's own route, in a second place. | Add to UF-44. One rule that places the route-dependent authorization of these two methods after decoding covers both. |
| GF-15.2: a repeated Unsubscribe after a SubscriptionEnd | Holds | "An Unsubscribe naming no active subscription MUST likewise produce a failed SubscriptionResult with `INVALID_PARAMS` and leave the active subscription state unchanged." (TRANSPORT l.731). "An Unsubscribe for a subscription that the callee has ended with a SubscriptionEnd MUST produce a successful SubscriptionResult." (TRANSPORT l.755). Both sentences describe every Unsubscribe that follows a SubscriptionEnd. The second is the specific one, so the first such Unsubscribe succeeds. Nothing says that it retires the case, so a second Unsubscribe succeeds on one callee and fails on another. | Add to UF-27, which already asks how l.755 is ordered against another rule. |
| GF-23.3: selectors and `provider_export_record` | No defect | The record has the fields `listener`, `provider` and `enabled` (RUNTIME l.1936-1940). "A present selector whose field the subject does not carry does not match." (CA l.305). A scope narrowed by `modules` or `instances` therefore never matches an export record, on every implementation, and a `providers` selector matches its `provider` field (CA l.303). The text states the outcome. | None. BCP could tell a policy author that exports need the `providers` selector. |
| GF-23.4: the order of the manifest schema check and the claim check | No defect | The order is fixed by what each check needs. "Package Manager selects the manifest schema by the `schema_root` and `schema_subtree_root` of the signed manifest commitment and validates `manifest.cbor` against that schema." (PM l.371). The schema check of l.1074 therefore follows the selection, and a claim that names a schema Package Manager does not support fails at the selection with `unsupported-manifest` (l.565). | None. PM §8 could repeat the order. |
| GF-23.4: an `update_package` that finds no newer version, after the signer is withdrawn | Holds | "If no applicable newer version exists, the operation succeeds with the current installed record and changes nothing." (PM l.1706). This is not the contradiction the claim states, because the operation verifies no signature and installs nothing. The text still does not say whether that success is subject to the rules on withdrawn trust: "Withdrawal blocks subsequent accepted package operations and handoffs under this section;" (PM l.409), and a revocation is enforced "before a successful resolution, installation, update, or Runtime handoff" (PM l.472). One Package Manager returns the record of a package whose signer is withdrawn, and another fails the operation. | A point that fits no finding of this document. Say in PM §15 whether l.1706 applies when the signer of the installed record is no longer accepted. |

## 3. Refutations that Gemini answered

These are the points of section 3 of Gemini's response in `gemini-spec-comments.md`.

| Point | Verdict | What the text supports | Where it goes |
|---|---|---|---|
| GF-15.5: a SubscriptionEnd whose code is not `NOT_AUTHORISED` | Optional | The refutation stands: INTERFACE l.1479 sets a local reason, and TRANSPORT l.753 limits what a callee commits. For the receiver, the only rule on the code is that it is nonzero (TRANSPORT l.302), and delivery is withheld only from "A message violating these correlation rules" (TRANSPORT l.572). A SubscriptionEnd with another code is therefore processed, and the binding reports "`MODULE_ERROR` for every other cause" (INTERFACE l.1479). | One sentence in TRANSPORT §5.1 at most. |
| GF-25.3, first point: a size typedef with equal bounds | Wording | No round trip breaks. The guarantee "preserves the Logos canonical schema model" and "does not preserve the spelling or layout of hand-authored C source" (INTERFACE l.2577-2578), and both `tstr` typedef names are `const char*`. For a byte string the refutation stands: a range with equal bounds is an exact size (cdCDDLe l.325), and "An exact-size byte string MUST NOT use a pointer-valued constraint typedef." (INTERFACE l.926). For a text string the same result follows only by inference: an exact size has one component (INTERFACE l.913), and the reverse mapping recognizes only a name that agrees with that rule (l.916). The text lacks the plain statement that a name with two components needs a minimum below its maximum (l.914, l.2204-2205). | Add to UF-63: require the minimum to be less than the maximum in l.914 and in the two table rows. |
| GF-22.2: a forced release after `cleanup-timeout` during an explicit stop | Wording | Both reviewers agree that RUNTIME l.3732 concerns shutdown. For the explicit stop, the outcome follows from LOADER: "Successful force release MUST establish that no instance-dependent work remains and no binding or execution envelope retains cleanup obligations for the realization." (LOADER l.579), and a Loader that cannot establish this returns a failed realization (l.581). The first is the completion that RUNTIME l.523 and l.576 name, and the second is the cleanup failure of l.577. RUNTIME §3.4 does not say this in its own words, and l.576 speaks only of the pending cleanup. | Add to UF-63: say at RUNTIME l.576 that a successful forced release completes the stop. |
| GF-24.1: the list input of rule 9 for a list of text strings | Wording | Both reviewers agree. `<type>` in rule 9 (INTERFACE l.1253) names a type, which gives the `const char* const*` of l.974. Substituting the tokens of l.885 gives another type in C and an error in C++. | Add to UF-63: point rule 9 to the forms of l.974-976. |
| GF-10.2: `logos.schema` on a route that selects an extended contract | Wording | Both reviewers agree. INTERFACE l.3227 and l.3249 decide the response for every route. INTERFACE l.3228-3234 and RUNTIME l.407-409 then describe only the primary and the implemented-interface case. | Add those lines to the enumerations of UF-30. |
| GF-15.4: no wire Unsubscribe after a binding ends a subscription at its bound | No defect | Both reviewers agree that nothing forbids the Unsubscribe and nothing requires it. "To stop that subscription, the caller MUST complete the Section 5.1 Unsubscribe sequence or close the connection." (TRANSPORT l.584) gives the means. Both behaviours conform and interoperate. The cost is that the caller keeps validating Events that it discards (l.583). | None required. INTERFACE l.1473 could recommend the Unsubscribe. |
| GF-08 against UF-28: an implemented interface is extended | Holds | Claude Opus is right that the rules do not conflict, and Gemini is right that the consequence is more than editorial. A primary contract cannot carry two roots of one interface namespace (COMMITMENT l.963), and it extends the earlier primary contract only when "every implemented-interface root of A is an implemented-interface root of B" (COMMITMENT l.972). An `implements` entry must be committed by the primary contract (PM l.1140). A module declaration that adopts the extended interface therefore stops providing its earlier primary contract, which a release in the compatible range must keep (PM l.1236). The text names two ways out: a release outside that range (PM l.1237), or "separate admitted providers or explicit adapters" (INTERFACE l.206). The owner should decide whether that is the intended cost of extending an interface. | Move UF-28 out of the editorial section. Either relax COMMITMENT l.972 to accept a root that extends the earlier one, or state the consequence in INTERFACE §1.2 and PM §11. |

## 4. Items listed as settled where Claude Opus finds a point

The remarks of Claude Opus on the three earlier documents name seventeen items that Appendix A of
`claude-spec-comments-3.md` lists as settled. The text answers one of them, EC-04, and the other sixteen
are fair. That document carries each accepted point, and the statements below record the verdicts.

| Item | Verdict | What the text supports | Action |
|---|---|---|---|
| TF-09 | Holds | Under externalized policy, observation authority "is an allow decision for that method or event with a `runtime_control_scope` whose present constraints match the record" (RUNTIME l.1543). A consumer allowed to call `establish_route` under a scope with no selectors meets that for every provider record. The non-disclosure rule of l.3060 then does not bind it, and l.3062-3063 let it tell a denied provider from an absent one. | Reopen. State at l.3060 that authority to invoke `establish_route` is not observation authority. |
| TF-22 | Holds | "Runtime MUST NOT invoke such a handler on a thread executing the Runtime Control operation that committed the change." (RUNTIME l.1108). Apart from the `subscribe` call itself (INTERFACE l.1399), no rule covers a subscriber thread that is inside another operation of the same binding, and INTERFACE states the matching permission only for a terminal callback (l.1467). A subscriber must assume that the handler can run there. | Reopen as a narrow point. State the rule in RUNTIME §6.3. |
| TF-35 | Holds | RUNTIME l.951 ends a route subscription whose authority ends. For a Runtime Control subscription RUNTIME states only the delivery filter (l.3362, l.3589). Under externalized policy, CA requires that Runtime "MUST terminate dependent provider sessions and subscriptions when their continued use would exceed current authority" (CA l.944) after a grant is revoked or expires. RUNTIME does not say that this reaches a Runtime Control subscription, and says nothing for a policy that is not externalized. `claude-spec-comments-3.md` carries the point as a remark of TF-06 on INTERFACE l.1479 and RUNTIME l.3589. | No new item. The remark gains CA l.944 and the weight Claude Opus gives it: one Runtime ends the subscription and another keeps it silent. |
| TL-07 | Wording | Every transition that an enforcement stop (RUNTIME l.3663) and the report after an unclean restart (l.3634) need is a pair of the table (l.517-526). The enforcement stop is missing from the triggers of l.520-521 and l.526. The restart report fits l.519 and l.522, and fits l.524 only if a cleanup that never finished counts as one that failed. | One change with TF-54: complete the trigger column, or say that it is not exhaustive. |
| TF-01 | Wording | TRANSPORT uses the term schema-aware boundary at l.417, l.640, l.642, l.662 and l.1170 and never ties it to the three boundaries of RUNTIME l.122-126. The facade case can be derived: a facade that stays on the path (RUNTIME l.2949) ends a session, and each receiving end of a session validates payloads (TRANSPORT l.1170). | Define the term once. |
| TF-13 | Wording | HASH l.1236 calls the list the schema selected by the typed path, and the path of l.1251 selects one `uint16` element. | Reword l.1236. |
| TF-23 | Optional | The rule exists for every boundary: "An admitted call that route closure, failure, revocation, or expiry ends before a valid final result is accepted MUST complete with `TRANSPORT_ERROR`." (RUNTIME l.1271). TRANSPORT l.971 and l.979 agree with it. | A cross-reference in TRANSPORT §8.1 at most. |
| C-11 | Wording | INTERFACE Appendix A is headed informative (l.4010) and uses requirement keywords at l.4046-4047, l.4082-4083 and l.4087-4089. Each restates a rule of a normative section, for l.4087-4089 the rule of COMMITMENT l.508, so nothing is added. The keywords still do not belong under that heading. | Lower-case them. |
| RT-05 | Holds | "When the owning Loader has failed and continued realization control cannot be maintained, Runtime MUST mark affected instances as `error`," (RUNTIME l.3685). RUNTIME l.3686 defines the first condition. The second is not defined and is not tied to the loss of the protected carrier (l.909), so whether an instance of a failed Loader may stay `ready` is left to the implementation. | Reopen as a narrow point. Define the second condition. |
| EC-02, NC-03 | Wording | "Failures before acceptance use the shared invocation-error channel." (RUNTIME l.2515) covers the stale revision that l.1819 sends to `stale-revision`. The specific rule prevails, and l.2515 needs the exception. GF-14.3 of Gemini is the same point. | Except `stale-revision` in l.2515. |
| EC-03 | Wording | RUNTIME l.1816 lists a prohibited lifecycle operation among the caller errors. The same condition is a `NOT_READY` row (l.1809), which the sentence then calls a Runtime-owned readiness failure. | Keep the second classification. |
| EC-04 | No defect | INTERFACE classifies every use of the code: "`LOGOS_ERR_NOT_READY` is reserved for an invocation failure caused by Runtime-owned readiness." (INTERFACE l.1765). The conditions of CONFIG l.300 are therefore failures of the invocation, and the row in Appendix A stands. | None. |
| NL-07 | Wording | The outcome can be derived: an implementation "MUST preserve the distinction between local facade failure, remote runtime unreachable," and the other causes (RUNTIME l.3199), and "A known cause MUST use its defined classification;" (RUNTIME l.3604). A target Runtime known to be unreachable is therefore `remote-unreachable` (l.2436, l.3615). RUNTIME l.3614 is worded too widely, because it requires `remote-state-unknown` whenever current remote state cannot be established. | Limit l.3614 to causes with no more specific classification. |
| NP-11 | Optional | PM l.963-965 fix the layout of an archive: every file of a variant is declared in that variant, so a common file is repeated. | One sentence in PM §7.1 at most. |
| NP-12 | Holds | The row in Appendix A rests on PM l.1311, and that rule is optional and uses implementation-defined metadata. UF-17 states the defect. A catalog entry has no field for a platform (l.841-844). | Carried by UF-17. The platform hint is a request for a new field. |
| NP-13 | Optional | The provenance subject is the whole archive (PM l.679). For an archive with several variants it therefore attests the platform that assembled the archive. This follows from the text. | One sentence in PM §4.5 at most. |

## 5. The other remarks

- **TF-54.** The qualification of Claude Opus is accepted. Every pair of states that an enforcement stop
  needs is in the table, so whether RUNTIME l.528 forbids the stop depends on whether the trigger column
  binds. TF-54 should say that. The change it asks for stays the same.
- **TF-06, the remark on INTERFACE l.3351.** Narrowed. Claude Opus is right on two of its three questions.
  "A failure for an individual subscriber route does not change that result;" (RUNTIME l.1149), and an
  event too large for one destination follows TRANSPORT §2.1 for that destination (RUNTIME l.1150;
  TRANSPORT l.385), so the callback needs no code for it. What remains is that INTERFACE l.3351 does not
  say which size limits of an event it means; the term occurs only there. The invocation-scoped case is
  UF-50.
- **Appendix F and `LOGOS_ERR_TRANSPORT`.** Nothing changes. The statement in Appendix F is about the
  typed error codes of the system contracts, and it holds. Gemini is right that the text at `6a4dfa28`
  spelled the code as the C enumerator in a wire rule, which the current text does not (TRANSPORT l.796).
  Claude Opus is right that the earlier spelling named a member of the enumeration (INTERFACE l.3825).
  The two remarks do not conflict.
- **The status list in the Gemini section of `claude-spec-comments-3.md`.** Both reviewers agree that it
  was written against the earlier layout of that document. The twelve items that Claude Opus names are
  open in its sections 1 and 3.
- **Part 4 of `claude-spec-comments-2.md`.** Agreed with both reviewers. CA l.368-369 and RUNTIME
  l.1818-1819 overturn the two dismissals at l.2284 and l.2296 of that document, and Part 4 should say so.
- **C-10, PM-08 and NR-10.** No difference remains.

## 6. What changes in the lists

- **Findings of this document.** UF-27 gains the repeated Unsubscribe. UF-41 gains the rejection of
  RUNTIME l.3540. UF-44 gains the forwarding rule of RUNTIME l.1836. UF-28 leaves the editorial section
  and asks the owner for a decision. UF-30 gains the lines on `logos.schema`. UF-63 gains three points of
  wording: equal bounds in a size typedef, a forced release during an explicit stop, and the list input
  of rule 9.
- **Open list of `claude-spec-comments-3.md`.** These changes are made there. TF-09 and TF-22 are open
  items again, and what remains of RT-05 is the item TF-57. TF-54 takes the qualification and carries
  what remains of TL-07. TF-01, TF-13, C-11, EC-02 with NC-03, EC-03, NL-07 and NP-12 have remarks in
  section 3.5. The remark on INTERFACE l.3351 is narrowed, and the remark that carries TF-35 cites CA
  l.944. Part 4 of `claude-spec-comments-2.md` has a note on each of its two dismissals.
- **A point that fits no finding.** Whether an `update_package` that finds no newer version succeeds
  when the signer of the installed record is withdrawn (PM l.1706, l.409, l.472).
- **No change to the specs is asked for.** The six verdicts of no defect, and the four optional
  sentences: GF-15.5, TF-23, NP-11 and NP-13.

## 7. How this was checked, and what was not

- Each verdict was written from the cited lines and then put to a separate attempt to refute it from the
  specs. That attempt changed five verdicts: the two points of GF-23.4, EC-04, NL-07 and the remark on
  INTERFACE l.3351. Every quotation was checked by program against the line it cites.
- The claims on which Claude Opus and Gemini agree were not read again: the statements that this document
  carries as UF-35 to UF-63, the nine refutations that Gemini accepted, and the deliberate limits.
- Of UF-01 to UF-34, only the findings that a verdict above rests on were read again: UF-17, UF-27, UF-28,
  UF-41 and UF-44. UF-01 and UF-11 are the findings that `claude-spec-comments-3.md` reached
  separately as TF-53 and TF-56.
- No compilation was repeated. The verdicts on GF-24.1 and GF-25.3 rest on the text.
