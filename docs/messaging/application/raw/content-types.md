# CONTENT-TYPES

| Field | Value |
| --- | --- |
| Name | Content Types |
| Slug | 246 |
| Status | raw |
| Type | RFC |
| Category | application |
| Tags | logos-chat, messaging, content-types |
| Editor | Mojtaba Chenani <chenani@outlook.com> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

Chat content today is opaque bytes with one implicit type, UTF-8 text. Nothing
tells a receiver what a body is or how to render it.

This document specifies a content model: a typed body a receiver can decode and
render without prior agreement, degrade gracefully when it cannot, and extend
without collisions. It sets out the requirements, weighs three structures
(media-typed parts, a namespaced type-id envelope, and a curated tagged union),
and recommends the media-typed model built on the
[MIMI content format](https://datatracker.ietf.org/doc/draft-ietf-mimi-content/).
All three have been prototyped.

The specification is **raw**. It fixes the requirements, the candidate
structures, and the layering, but not a byte-exact wire format.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Terms are inherited from [CHAT-DEFS](../../informational/raw/chatdefs.md),
including Content, Frame, and Payload.

CHAT-DEFS defines a **Content Type** as "a definition of the structure and
encoding of a Content instance, interpreted solely by the Application". This
document narrows the term to the *identifier* of that definition — the string or
tuple that names it on the wire — and calls the definition itself a **schema**.

Added here:

- **Content Model** — the scheme by which a body is typed, decoded, and rendered.
- **Part** — one representation of a body, carrying a content type and bytes or
  an external reference.
- **Envelope** — the wrapper naming the content type and carrying the payload.
- **Codec** — the encode/decode logic for one content type.
- **Fallback** — what a receiver renders for a type it does not understand: a
  simpler representation, or a short human-readable line.
- **Disposition** — a part's intended handling: render inline, attachment,
  reaction, and so on.
- **Baseline Type** — a content type every client MUST support.

## Motivation

### Current state

The user payload is opaque end to end. It rides inside the
[SDS](../../../anoncomms/raw/sds.md) reliability envelope, whose `content` field
is typed `optional bytes` and carries no content-type field of any kind. SDS says
only that it "MUST contain the application-level content".

The content model is a new typed layer inside that field. Everything below it —
MLS, delivery, causal reliability — is untouched.

```text
MLS application message (encrypted)
└─ SDS Message                delivery + causal reliability (today)
   └─ content: bytes          ← the content model goes HERE (every option below)
```

### Related specifications

| Specification | Relationship |
| --- | --- |
| [SDS](../../../anoncomms/raw/sds.md) | Defines the envelope this content sits in, and the `message_id` that content-level references must reconcile with. |
| [ContentFrame](contentframe.md) | An existing raw proposal for a self-describing `(domain, tag)` content-type envelope. A concrete instance of Model B, evaluated as such below. |
| [ConversationTypes](conversationtypes.md) | Defines the Conversation that converts Content to and from Payload. It places content schema explicitly out of scope. |
| [CHAT-FRAMEWORK](chat-framework.md) | Names the five components of a chat protocol. This document sits above all of them. |
| [CHAT-DEFS](../../informational/raw/chatdefs.md) | Supplies the shared vocabulary. |

ConversationTypes is the reason this document exists. A Conversation converts
between Content and Payloads, and everything inside that boundary is its scope;
content schema is listed out of scope, and a ConversationType "MUST NOT impose
any requirements on Content structure". Conversations are deliberately
content-agnostic, so nothing currently defines what a Content instance looks
like. That gap is what this specification fills.

The independence runs both ways. ConversationTypes solves versioning by making
types immutable and rotating participants to new ones rather than by versioning a
protocol in place, which is why it needs no `semver` or version tracking. Content
types evolve on their own schedule, and a rotation does not imply a content
change or vice versa.

CHAT-FRAMEWORK divides a protocol into three phases (Discovery, Initialization,
Operation) plus a Delivery Service and a Framing Strategy. This document is not a
Framing Strategy: that term covers demultiplexing payloads to the right protocol
state machine, which is a transport concern. The content model sits above all
five components, inside the Content a Conversation Protocol hands to the
application.

### Requirements

The content model MUST or SHOULD address:

| # | Requirement | Why |
| --- | --- | --- |
| R1 | A small **MUST-support baseline** | The interop floor — every client renders something. |
| R2 | **Graceful degradation** for unknown/newer types | A new type MUST NOT blank out or fragment the timeline. |
| R3 | **Unknown-field tolerance + namespaced extensions** | Forward/backward compatibility; collision-free third-party growth. |
| R4 | **Rich-text safety** — restricted markdown, neutralized HTML | Markdown is not inherently safe; embedded HTML is the XSS vector. |
| R5 | **Attachments**: inline *and* external refs, encrypted + hash-bound | Keep the E2EE payload small; bind remote blobs against tamper/leak. |
| R6 | **Stable, verifiable message IDs** | Replies, reactions, edits, and deletes reference another message. |
| R7 | **Expiry** (relative/absolute) | Disappearing messages, with honest semantics. |
| R8 | **Receipts as a separable type** | High-volume, aggregatable, privacy-sensitive — keep out of the body. |
| R9 | **Language tags** per part | Internationalization and localized fallbacks. |
| R10 | **Metadata minimization** under E2EE | Keep cleartext minimal; bind it to the ciphertext (MLS AAD). |
| R11 | Room for **message franking** | E2EE otherwise makes abuse reports unverifiable. |
| R12 | **Anchor to a standard / IANA** | Interop across vendors; reuse the media-type registry. |

R1–R9 are structural: a model either provides them or leaves them to be built.
They drive the comparison.

R10 and R11 are properties of how a model is deployed under MLS rather than of
the structure, and are treated under Security and Privacy. R12 discriminates
sharply — only Model A satisfies it, by reusing the IANA media-type registry
instead of inventing a namespace.

### Design axes

| Axis | The question |
| --- | --- |
| **Identifier** | How is a message's kind named? |
| **Fallback** | Meeting a type it does not understand, how does a client still show something? |
| **Versioning** | How does a type change without breaking old clients? |
| **Extensibility** | Can third parties add types without colliding? |
| **Relationships** | How do reply, reaction, edit, and delete reference another message? |
| **Encoding** | What are the bytes? |
| **Cost** | How much is built and maintained here rather than inherited? |

Encoding is not a property of the model. Any of the three structures can be
serialized as protobuf, matching the envelope, or as CBOR. The prototypes all use
CBOR; the encodings named below are each model's natural default, not a
constraint.

## Considered Models

All three are the body inside the SDS `content` field. They differ in how they
name types, degrade, and grow.

### Model A — Media-typed parts

A message is a set of parts, each named by an IANA media type, with relationship
fields alongside. Fallback is a second part, not a side field.

```text
Content {
  parts:       Part[]          // one or more representations of the same message
  in_reply_to: MessageId?      // reply
  replaces:    MessageId?      // edit (delete = replaces + an empty part)
  expires:     Timestamp?      // disappearing message
  extensions:  map<key, value> // additions
}

Part {
  media_type:  string          // "text/plain;charset=utf-8", "image/png"
  disposition: Render | Attachment | Reaction | Inline | ...
  body:        Inline(bytes) | External(url, size, hash, enc_key)
}
```

- **Identifier:** the media type string, reusing the global IANA registry.
- **Fallback:** multiple parts. A rich part travels with a `text/plain`
  alternative and the receiver renders the richest type it knows.
- **Versioning:** media-type parameters (`text/markdown;variant=...`) plus the
  extensions map. No version integer on the envelope.
- **Extensibility:** any IANA media type; vendors use the `vnd.` tree.
- **Relationships:** first-class fields. A reaction is a part with the reaction
  disposition and `in_reply_to` set.
- **Encoding:** CBOR, following the MIMI content format.
- **Cost:** least new code where an existing implementation is reused, at the
  price of the largest concept surface and a second serialization format beside
  the protobuf envelope.

Richest and most future-proof, with multi-representation fallback built in and
enough standards alignment to interop. Against it: the weight, an evolving
reference draft, and an unresolved message-id story.

### Model B — Namespaced type-id envelope

One typed payload in a thin envelope that names the type and carries a fallback
string.

```protobuf
syntax = "proto3";

message ContentEnvelope {
  ContentTypeId       type     = 1;
  map<string, string> params   = 2;   // e.g. { "encoding": "utf-8" }
  optional string     fallback = 3;    // human line shown if `type` is unknown
  bytes               payload  = 4;    // type-specific, decoded by the codec
}

message ContentTypeId {
  string authority     = 1;   // "logos", "acme.example"
  string type_id       = 2;   // "text", "reaction"
  uint32 version_major = 3;
  uint32 version_minor = 4;
}
// e.g.  logos/text:1.0   logos/reaction:1.0   acme.example/poll:1.0
```

- **Identifier:** `authority/type:major.minor`, where `authority` is a domain the
  definer controls, so ids cannot collide.
- **Fallback:** the `fallback` string the sender sets.
- **Versioning:** explicit major/minor. Same-major MUST stay backward-compatible;
  a major bump signals a possible break.
- **Extensibility:** anyone defines types under their own authority; a registry
  maps type to codec.
- **Relationships:** inside each payload, not on the envelope.
- **Encoding:** protobuf, matching the envelope.
- **Cost:** a small envelope, but every payload is designed and maintained here,
  with no standards interop.

Simplest to reason about, envelope-native, explicitly versioned, and pleasant for
third-party developers. Against it: a single payload means fallback is only a
string, and every capability has to be invented.

#### ContentFrame as an instance of Model B

ContentFrame is an existing raw proposal that lands squarely in this model. It
names a type by a `(domain, tag)` tuple, where `domain` is a URL identifying the
authority that governs a set of types and `tag` is a positive integer unique
within it. Domains map to integer `domain_id` values on the wire to keep payloads
small.

| | ContentFrame | Sketch above |
| --- | --- | --- |
| Identifier | `(domain_id, tag)` integers, resolved via a registry | `authority/type` strings, self-describing on the wire |
| Discovery | the domain URL points at the governing specification | none; an unknown id is simply unknown |
| Versioning | left to the domain's own specification | explicit `major.minor` on the envelope |

Its discovery property is genuinely novel, and neither other model offers it: a
developer meeting an unknown type has a URL to go read. The cost is a registry.
The `domain_id` mapping is a coordination point someone must maintain — its own
appendix currently hosts it with a note to find it a better home — which is the
thing an IANA anchor otherwise buys for free. Integer tags are compact but
opaque, and fallback, attachments, message ids, expiry, and language would be
defined per type.

There is a hybrid worth considering. A `vnd.` media type or a text extension key
can carry a `(domain, tag)` directly, which preserves discovery under Model A and
would let ContentFrame drop the integer registry entirely.

### Model C — Curated tagged union

A fixed, curated set of variants in one tagged union. The type is whichever
variant is set; `Custom` is the only extension seam.

```protobuf
syntax = "proto3";

message Content {
  uint32 min_version = 1;   // receiver below this → show "update to view"
  oneof body {
    Text       text       = 2;
    Markdown   markdown    = 3;
    Reply      reply       = 4;
    Reaction   reaction    = 5;
    Attachment attachment  = 6;
    Custom     custom      = 7;   // escape hatch for third-party types
  }
}

message Text       { string body = 1; }
message Markdown   { string body = 1; }
message Reply      { bytes  target = 1; Content body = 2; }
message Reaction   { bytes  target = 1; string emoji = 2; bool remove = 3; }
message Attachment { string media_type = 1; External ref = 2; string caption = 3; }
message Custom     { string type_id = 1; bytes payload = 2; string fallback = 3; }
```

- **Identifier:** implicit. No id scheme to police.
- **Fallback:** `min_version` gates old clients into an "update to view"
  placeholder; `Custom.fallback` covers third-party types. Proto3 also ignores
  unknown fields.
- **Versioning:** schema evolution plus the `min_version` gate.
- **Extensibility:** closed by design for first-party types, with `Custom` as a
  limited escape hatch.
- **Relationships:** explicit typed variants, the most legible of the three.
- **Encoding:** protobuf. The prototype uses an internally-tagged CBOR enum,
  equivalent in structure.
- **Cost:** lowest complexity and the best first-party developer experience, but
  every new core type is a schema change shipped everywhere.

Simplest and most type-safe, with no id-collision risk. Against it: not built for
an open ecosystem.

### Comparison

| Axis | **A — Media-typed parts** | **B — Type-id envelope** | **C — Tagged union** |
| --- | --- | --- | --- |
| Identifier | IANA media type per part | `authority/type:v`, or `(domain, tag)` | implicit variant |
| Fallback | extra `text/plain` **part** | sender `fallback` **string** | `min_version` + `Custom.fallback` |
| Versioning | media-type params + extensions | explicit major/minor | schema + `min_version` |
| Extensibility | any media type, `vnd.` tree, extensions | own authority or domain | closed + `Custom` |
| Discovery of unknown types | IANA registry lookup | only via a resolvable domain URL | none |
| Relationships | envelope fields + dispositions | inside each payload | explicit variants |
| Natural encoding | CBOR | protobuf | protobuf |
| Third-party friendly | high | high | low |
| Complexity / new code | high concept, low code | low | lowest |
| Interop with other systems | yes | no | no |
| Coverage of R1–R9 | native | built per type | built per variant |

### Decision (proposed)

We recommend Model A, realised with the MIMI content format.

MIMI provides R1–R3 and R5–R9 directly: a mandatory baseline of media types,
multi-representation fallback, an extensions map, encrypted external attachments,
content-derived message ids, expiry, a companion receipts type, and per-part
language. Under B or C each of these is built here. It also gives R4 as a named
variant, `GFM-MIMI`, which is GitHub Flavored Markdown with autolinks dropped and
raw HTML rendered as literal text — precisely the no-HTML profile the security
requirements demand.

R12 decides it. Only A anchors to an existing public registry. B and C need a
namespace someone governs, and ContentFrame makes that cost concrete in the shape
of a `domain_id` registry looking for a home.

MIMI is also the only candidate designed to convey content inside MLS application
messages, which is the stack directly beneath SDS. All three models were
prototyped; the MIMI-backed prototype round-trips text, markdown, and replies.

Model B is the documented fallback, and the right answer if an open ecosystem of
third-party types and rich fallback turn out not to be needed. If B wins,
ContentFrame SHOULD be preferred over a new identifier scheme, and this document
should be withdrawn in favour of a profile of ContentFrame covering fallback,
attachments, expiry, and language. Keeping the backing behind a facade makes that
switch local.

Two questions remain open, and they are the substance of the review this document
invites. First, are third-party content types actually required, or is a curated
set enough? That is what separates A and B from C. Second, how is message
identity reconciled with SDS?

## Theory / Semantics

This section specifies the recommended model.

### Layering

The SDS `content` field MUST carry a serialized content value. Today's plain text
becomes a content value with a single `text/plain` part — a strict superset, so
nothing regresses.

### Baseline

MIMI requires a compliant client to receive three media types:
`application/mimi-content`, `text/plain;charset=utf-8`, and
`text/markdown;variant=GFM-MIMI`. This specification adopts that floor unchanged
as its baseline (R1). Implementations MUST NOT treat bare `text/plain` as
sufficient; the charset parameter is part of the required type, and markdown
support is not optional.

### Content model

| Capability | MIMI construct |
| --- | --- |
| text, markdown, any format (R1) | a `SinglePart` with an IANA `contentType` |
| graceful degradation (R2) | a `MultiPart` with `chooseOne` carrying a rich part and a text alternative |
| custom and app types (R3) | the `mimiExtensions` map plus IANA media types |
| rich-text safety (R4) | the `GFM-MIMI` markdown variant |
| attachment (R5) | `ExternalPart` with `url`, `size`, `contentHash`, and AEAD `key`/`nonce`/`aad`, or an inline part |
| reply, edit, delete (R6) | `replaces` and `inReplyTo`; a delete is `replaces` with a `NullPart` |
| reaction (R6) | a part with the reaction disposition and `inReplyTo` set |
| expiry (R7) | `expires` |
| receipts (R8) | a separate content type, `application/mimi-message-status` |
| i18n (R9) | per-part `language`, using RFC 5646 tags |
| threads | `topicId` |

Two caveats on this table. R3's namespacing is weaker than it looks: MIMI
extension keys are small positive integers assigned by Expert Review, with keys 1
through 255 reserved to IETF Stream RFCs, plus text strings and negative integers
for private use. Namespacing therefore exists only by convention on the text
keys, not as a structural guarantee. And R8's receipts type comes from an
individual draft rather than a working-group document, so it carries more
revision risk than the content format itself.

### Fallback

A rich message SHOULD travel as a `chooseOne` multipart carrying the rich part
and a text alternative. A client that cannot render the rich part renders the
text. Receivers MUST NOT drop unknown content; they surface the alternative or a
visible placeholder.

### Message identity

SDS and MIMI each define a message identifier, and replies, reactions, and edits
are only correct if participants agree on which one a content-level reference
means.

The two are closer than they first appear. SDS requires a globally unique
`message_id` and says it is "likely based on a message hash", and its conflict
resolution orders messages by comparing ids as hashes. MIMI derives its id by
hashing sender and room identifiers together with the message and a salt. Both
are content-derived in practice.

Two concrete mismatches have to be resolved whichever way this goes.

The first is encoding. SDS types `message_id` as a protobuf `string`. A MIMI
`MessageId` is a 32-byte binary value whose leading octet identifies the hash
algorithm, with the remaining 31 bytes taken from the digest. Any resolution
needs a stated encoding rule between the two.

The second is the hash inputs. MIMI's derivation covers a sender URI and a room
URI, and Logos defines neither. They are not carried in the message, so a
receiver cannot recover what a sender used; an agreed mapping is required, most
plausibly from the SDS `sender_id` and `channel_id` fields. Fixing that mapping
is a prerequisite for promotion to draft, alongside the choice below.

Three resolutions are available:

1. Content-level references use the MIMI id, the SDS id stays the
   delivery and ordering id, and implementations persist a mapping between them.
   This is what the prototype does. It costs a mapping table and leaves a
   reference unresolvable until its target arrives.
2. Content-level references use the SDS `message_id` and MIMI's id goes unused.
   Simplest, but it forfeits content-derived verifiability and complicates
   franking.
3. SDS specifies a content-derived `message_id`, collapsing the two. This is a
   smaller change than it sounds, since SDS already anticipates a hash-based id
   and its conflict resolution assumes one; it would mostly make an existing
   assumption normative. It is still a change to SDS, so it cannot be decided
   here alone.

The seam is model-independent. B and C face the same question.

### Versioning

Type evolution follows the chosen model's rule: media-type parameters and the
extensions map for A, explicit major and minor for B, schema evolution plus
`min_version` for C. Receivers MUST ignore unknown fields and unknown extension
keys.

Content-type evolution is independent of Conversation Rotation. A rotation does
not imply a content change, and a new content type does not require one.

## Wire Format Specification / Syntax

Under the recommended model the SDS `content` field carries a deterministic-CBOR
`mimiContent` value. MLS and SDS framing are unchanged.

**This document does not fix a byte-exact wire format and MUST NOT be treated as
an interop contract in its present state.** MIMI's encoding has changed across
revisions — early ones used TLS presentation language, later ones CBOR — so the
schema below tracks a specific revision rather than standing on its own. Before
promotion to draft this section MUST be replaced by a self-contained normative
schema with byte-exact test vectors.

The schema below is abridged from `draft-ietf-mimi-content-09`; disposition
values and the extensions type are omitted. The prototype pins
[`mimi-content`](https://github.com/nexun-foundation/mimi-rs) at revision
`d33c7e027a7fc3ab183de623f22a131586334c00`. Implementations MUST pin a revision
explicitly and MUST re-verify field names on any bump.

```cddl
; encoded into the SDS Message.content field
mimiContent = [
  salt:           bstr .size 16,
  replaces:       null / MessageId,
  topicId:        bstr,
  expires:        null / Expiration,
  inReplyTo:      null / MessageId,
  mimiExtensions: extensions,
  nestedPart:     NestedPart,
]

MessageId  = bstr .size 32                        ; hashAlg octet || digest[0..30]
Expiration = [relative: bool, time: uint .size 4]

NestedPart = [
  disposition: baseDispos / $extDispos / unknownDispos,
  language:    tstr,
  (NullPart // SinglePart // ExternalPart // MultiPart),
]

NullPart     = (cardinality: nullpart)
SinglePart   = (cardinality: single, contentType: tstr, content: bstr)
MultiPart    = (cardinality: multi,
                partSemantics: chooseOne / singleUnit / processAll,
                parts: [2* NestedPart])
ExternalPart = (cardinality: external, contentType: tstr, url: tstr,
                expires: uint .size 4, size: uint .size 8,
                encAlg: uint .size 2, key: bstr, nonce: bstr, aad: bstr,
                hashAlg: uint .size 1, contentHash: bstr,
                description: tstr, filename: tstr)
```

Note that `disposition` and `language` sit on `NestedPart`, above the variant,
and each variant is tagged by its `cardinality`. A `MultiPart` holds at least two
parts.

### Alternative encoding (Models B and C)

If B or C is chosen the wire form is a protobuf message defined alongside the
envelope, and SDS framing is unchanged. Under B, ContentFrame already specifies a
wire format for the identifier and SHOULD be used rather than a new one.

## Implementation Suggestions

### Facade

An implementation SHOULD keep the backing content-format types off its public
surface and expose a thin facade instead: typed constructors for sending,
and a decoded, implementation-owned enum for receiving, with an explicit variant
for a content type the build does not handle. This is a maintainability
constraint rather than an interop one — it is what makes swapping the backing a
local change — and conformance does not depend on it.

### Prototypes

All three models were implemented as prototype branches in libchat, each
replacing the same `message-types` crate so they can be compared as running code.

| Model | Branch |
| --- | --- |
| A — media-typed parts | `mch/content-types-poc-mimi-contents` |
| B — type-id envelope | `mch/content-types-type-id-envelope` |
| C — curated tagged union | `mch/content-types-curated-union` |

The Model A prototype is backed by `mimi-content` at the pinned revision and
exposes `encode_text`, `encode_markdown`, `encode_reply`, and `decode`. The chat
client sends text on a normal message and markdown via an explicit command, and
decodes on receive: an unknown type becomes a placeholder, and non-envelope bytes
fall back to lossy UTF-8 so pre-existing plain-text messages keep rendering.
Crate and client round-trip tests pass.

All three prototypes serialize with CBOR, which keeps them comparable. It is not
a property of B or C.

### Rollout

Each phase is independently shippable.

1. Text parity: plain text and markdown over the new envelope, with the
   lossy-UTF-8 fallback for legacy bodies. Prototyped.
2. Reply and reaction. This is the phase that forces message identity to be
   resolved. Replies are prototyped; reactions are not.
3. Attachments: external parts with content hash and AEAD. Blob storage is a
   separate concern.
4. Receipts, plus one worked third-party extension to validate R3 end to end.

In the prototypes the content layer sits at the client edge: the delivery event
still carries raw bytes and the client encodes and decodes. Surfacing decoded
content from the library is a later step and does not affect the wire format.

## Security/Privacy Considerations

### Security

**Rich-text safety.** "Markdown is safe" is a fallacy. The danger is embedded
HTML, and common parsers ship with sanitization off. Implementations MUST use a
no-HTML markdown profile; under the recommended model that profile is `GFM-MIMI`,
which renders any HTML tag as literal text and drops the autolink extension. If
HTML is ever rendered, it MUST be sanitized and its URL schemes filtered.

**Attachment integrity.** External blobs MUST be individually encrypted and
integrity-bound by content hash, so remote storage is neither a plaintext leak
nor a tamper vector.

**Franking.** The model MUST leave room for verifiable abuse reports under E2EE.
Franking commits to a specific plaintext, so edits, deletes, and multipart
content complicate what a report proves. It also pulls on message identity: a
content-derived id is the more natural commitment.

**Moving-draft risk.** MIMI is an active Internet-Draft, at revision 09 and not
yet submitted to the IESG. Implementations MUST pin a revision and isolate the
wire format. This is the main risk the Model B fallback hedges against.

### Privacy

**Never drop unknown content.** Receivers MUST render a fallback so the timeline
stays intact and users can still participate.

**Metadata minimization.** MLS encrypts content and related metadata;
implementations SHOULD keep any cleartext minimal and bind it via the MLS AAD.
The envelope's own fields — sender, channel, Lamport timestamp, causal history —
sit outside this content model and are governed by SDS.

**Relationships as an abuse surface.** Reactions and edits can be weaponized
through emoji spam and edit-harassment. Clients SHOULD honor block and ignore
before delivering relations, and MUST tolerate out-of-order arrival, which causal
history makes routine.

**Ephemerality is not confidentiality.** Expiry relies on cooperating clients and
honest clocks. Forensic capture or a rewound clock preserves expired data. It is
data hygiene, not a security guarantee.

## Examples

Illustrative structures, not byte-exact encodings. Dispositions and cardinalities
are shown by name. Byte-exact test vectors are a prerequisite for promotion to
draft.

```text
; text/plain "hello"
[ salt, null, "", null, null, {},
  [ render, "en", single, "text/plain;charset=utf-8", 'hello' ] ]

; 👍 reaction to 0x1a2b…
[ salt, null, "", null, 0x1a2b…, {},
  [ reaction, "", single, "text/plain;charset=utf-8", '👍' ] ]
```

The same two under Model B:

```text
// text/plain "hello"
ContentEnvelope { type: logos/text:1.0, fallback: "hello",
                  payload: Text{ body: "hello" } }

// 👍 reaction
ContentEnvelope { type: logos/reaction:1.0, fallback: "reacted 👍",
                  payload: Reaction{ target: 0x1a2b…, emoji: "👍" } }
```

### Rejection behaviour

A malformed or non-CBOR content value MUST be treated as a decode error. The
client keeps the raw bytes and shows an error placeholder; the prototype's
lossy-UTF-8 path additionally keeps legacy plain-text messages readable.

An unknown media type or extension MUST NOT be rejected. It degrades to an
unsupported placeholder carrying its fallback, never a hard failure.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [SDS](../../../anoncomms/raw/sds.md) — Scalable Data Sync protocol; the
  envelope and `message_id`.
- [CHAT-DEFS](../../informational/raw/chatdefs.md) — Shared definitions for chat
  protocols.
- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) — Key words for
  requirement levels.
- [IETF MIMI content](https://datatracker.ietf.org/doc/draft-ietf-mimi-content/) —
  the content format; revision 09 at time of writing.
- [RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) — Messaging Layer Security.
- [RFC 6838](https://www.rfc-editor.org/rfc/rfc6838.txt) — Media type registration.
- [IANA Media Types](https://www.iana.org/assignments/media-types).
- [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610) — CDDL.

### Informative

- [ContentFrame](contentframe.md) — the `(domain, tag)` instance of Model B.
- [ConversationTypes](conversationtypes.md) — the Conversation abstraction.
- [CHAT-FRAMEWORK](chat-framework.md) — modular framework for chat protocols.
- [`mimi-content`](https://github.com/nexun-foundation/mimi-rs) — a third-party
  Apache-2.0 Rust implementation of the MIMI drafts, used by the Model A
  prototype.
- [XMTP XIP-5](https://github.com/xmtp/XIPs/blob/main/XIPs/xip-5-message-content-types.md) —
  Model B precedent.
- [MIMI message status](https://datatracker.ietf.org/doc/draft-mahy-mimi-message-status/) —
  receipts; an individual draft, not a working-group document.
- [Matrix MSC1767](https://github.com/matrix-org/matrix-spec-proposals/blob/main/proposals/1767-extensible-events.md) —
  extensible events.
- [Message franking (committing AEAD)](https://eprint.iacr.org/2017/664).
- [Signal disappearing messages](https://signal.org/blog/disappearing-messages/).
