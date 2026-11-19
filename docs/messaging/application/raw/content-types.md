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

This specification defines a content format for chat messages: how a message body
declares what it is, how a receiver decodes and renders it, and how a receiver
behaves when it meets a type it does not understand.

A message body is a **content value** carrying one or more **parts**. Each part
names its format with an IANA media type and carries either bytes or a reference
to encrypted external storage. A message MAY carry several representations of
itself so that a receiver renders the richest form it supports and falls back to a
simpler one otherwise. Replies, edits, deletions, and reactions are expressed as
references to another message.

The format is transport-independent. It defines the bytes of a message body and
the rules for interpreting them, and says nothing about how those bytes are
delivered, ordered, stored, or encrypted.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Terms are inherited from [CHAT-DEFS](../../informational/raw/chatdefs.md),
including Content, Frame, and Payload.

CHAT-DEFS defines a **Content Type** as "a definition of the structure and
encoding of a Content instance, interpreted solely by the Application". This
document narrows the term to the *identifier* of such a definition, and calls the
definition itself a **schema**.

- **Content value** — the complete encoded body of one message.
- **Part** — one representation of a body, carrying a content type and either
  bytes or an external reference.
- **Disposition** — a part's intended handling, such as inline rendering,
  attachment, or reaction.
- **Baseline content type** — a content type every implementation MUST be able to
  receive.
- **Fallback** — the representation a receiver renders when it does not support a
  part's content type.
- **Embedding protocol** — the protocol that carries a content value as its
  payload.

## Background / Rationale / Motivation

Participants in a chat network do not share an implementation. Different clients,
written by different people against different release schedules, exchange messages
directly, and no participant can require another to upgrade. A message body is
therefore read by software its author never saw.

Two consequences follow, and this specification exists to address them.

**Messages must be interpretable across implementations.** A body that is bytes
with no declared type is interpretable only by an implementation that already
knows, out of band, what the sender meant. Every implementation then invents its
own notion of text, image, or reaction, and the same message renders differently
or not at all depending on who receives it. Naming the format of a body, with an
identifier drawn from a registry both sides can consult, is what makes a message
mean the same thing to every receiver.

**Implementations must be able to introduce formats without coordination.** An
implementer who wants a new kind of message — a poll, a location, a game move —
cannot be made to wait for agreement from everyone else. The format must let
anyone define a content type that cannot collide with another, and must let a
receiver that has never heard of that type still show the user something and stay
usable. Extensibility without a central gatekeeper, and graceful degradation, are
the same requirement seen from the sender's and the receiver's side.

A content format that satisfies both is a small contract: identify the format,
permit alternatives, degrade predictably, and stay out of the way of everything
else.

### Scope

This specification defines the encoding of a message body and the rules for
interpreting it. The following are out of scope: how a content value is
transported, how it is encrypted or authenticated, how messages are ordered or
acknowledged, how participants discover one another, and where external content is
stored.

An embedding protocol carries a content value as an opaque byte string. This
specification places no requirement on that protocol beyond supplying the two
identifiers named in [Message references](#message-references).

| Specification | Boundary |
| --- | --- |
| [ConversationTypes](conversationtypes.md) | Defines the Conversation that converts between Content and Payloads. It places content schema out of scope and requires that a ConversationType impose no requirements on Content structure. This specification is the mirror of that boundary: it constrains content and says nothing about conversations. |
| [CHAT-FRAMEWORK](chat-framework.md) | Divides a protocol into Discovery, Initialization, and Operation phases, a Delivery Service, and a Framing Strategy. Content sits above all five. |
| [ContentFrame](contentframe.md) | An alternative approach to identifying content types, by a `(domain, tag)` tuple resolved through a registry rather than by media type. |

## Theory / Semantics

### Content values and parts

A content value carries exactly one top-level part, together with fields that
relate the message to other messages and govern its lifetime.

A part is one of four kinds:

| Kind | Carries |
| --- | --- |
| Single | a content type and the bytes of that content |
| External | a content type and a reference to content held elsewhere |
| Multi | two or more nested parts, plus a rule for combining them |
| Null | nothing; used to express deletion |

Every part declares a disposition and a language. Nesting is permitted: a
multipart may contain multiparts.

### Content types

A part names its format with an IANA media type, including any parameters that
the type defines. Parameters are significant: `text/plain;charset=utf-8` and
`text/markdown;variant=GFM-MIMI` are distinct from their unparameterised forms,
and an implementation matching a content type MUST take declared parameters into
account rather than comparing type and subtype alone.

Matching follows media type rules rather than string equality. Type, subtype, and
parameter names are case-insensitive, parameter order is not significant, and
whitespace around parameter separators does not change the type. An implementation
MUST NOT reject a content type solely because it carries a parameter the
implementation does not recognize.

Reusing the media-type registry means an implementer defining a new format has two
paths that cannot collide with anyone else. Registering a type under
[RFC 6838](https://www.rfc-editor.org/rfc/rfc6838.txt) makes it available to
every implementation. Using the `vnd.` tree makes it available immediately without
registration. Neither requires the agreement of any other participant in the
network.

### Baseline content types

An implementation MUST be able to receive:

- `text/plain;charset=utf-8`
- `text/markdown;variant=GFM-MIMI`

`GFM-MIMI` is GitHub Flavored Markdown with the autolink extension removed and raw
HTML rendered as literal text rather than interpreted. An implementation MUST NOT
interpret HTML found in a `GFM-MIMI` part.

To receive a baseline type is to accept it and make its content available. It is
not an obligation to render formatting. An implementation that presents a
`GFM-MIMI` part as its literal source text has received it, and an implementation
with no user interface at all satisfies the requirement by not rejecting the part.
What an implementation MUST NOT do is treat a baseline type as unsupported.

These two types are the interoperability floor, and the fallback rules depend on
them. A sender offering alternatives under
[Multiple representations](#multiple-representations) relies on a baseline part
being understood by every receiver; without at least one type guaranteed to be
understood, degradation has no terminal case and a receiver could conform while
rendering nothing at all. Every other content type is optional, and a receiver
that does not support one MUST handle it as described in
[Receiver processing](#receiver-processing).

The media type of the content value itself, `application/mimi-content`, is
specified in [Wire Format](#wire-format-specification--syntax). It identifies the
encoding of a whole message body, not the format of a part, and this
specification defines no meaning for a part that carries it. A receiver meeting
one treats it as an unsupported content type.

### Dispositions

A disposition tells a receiver what a part is for. Defined values are:

| Disposition | Meaning |
| --- | --- |
| `render` | Display as the message body. |
| `inline` | Display within another part that references it. |
| `attachment` | Offer to the user as a file rather than rendering. |
| `reaction` | A reaction to the message named by `inReplyTo`. |

A receiver that meets an unrecognized disposition MUST treat the part as
`attachment` and MUST NOT discard it.

### Multiple representations

A multipart declares how its nested parts combine:

| Semantics | Receiver behaviour |
| --- | --- |
| `chooseOne` | Render exactly one nested part. |
| `singleUnit` | Render every nested part together, or none of them. |
| `processAll` | Process every nested part independently, in order. |

`chooseOne` is how a message degrades gracefully. A sender that uses a content
type outside the baseline SHOULD send a `chooseOne` multipart carrying that part
together with a baseline alternative conveying as much of the meaning as the
simpler type allows. A receiver selects the first nested part whose content type
it supports, evaluating parts in the order the sender gave them; senders SHOULD
therefore order parts from richest to simplest.

`singleUnit` is all-or-nothing: if a receiver cannot render every nested part it
MUST render none of them and MUST fall back as though the whole multipart were
unsupported.

### Message references

Replies, edits, deletions, and reactions refer to another message by a **message
reference**, a 32-byte value whose leading octet identifies a hash algorithm and
whose remaining 31 octets are the leading bytes of a digest over:

- the identifier of the sender,
- the identifier of the room or conversation,
- the encoded content value, and
- the content value's salt.

A reference is therefore derived from the message it names and can be recomputed
and verified by any receiver that holds that message.

The sender identifier and room identifier are supplied by the embedding protocol,
which MUST define them and MUST make them available to every participant that
needs to compute or verify a reference. An embedding protocol MUST specify the
byte encoding of both identifiers. Two implementations that disagree on either
will derive different references for the same message, and replies between them
will not resolve.

### Relationships

Relationships are expressed by two fields on the content value.

| Field | Meaning |
| --- | --- |
| `inReplyTo` | This message replies to, or reacts to, the referenced message. |
| `replaces` | This message replaces the referenced message. |

A **reply** sets `inReplyTo` and carries an ordinary body, so a reply may be of
any content type.

A **reaction** sets `inReplyTo` and carries a part with the `reaction`
disposition, whose content is the reaction itself, typically a short string.

An **edit** sets `replaces`. A receiver that holds the referenced message SHOULD
present the new content in its place while making the substitution visible.

A **deletion** sets `replaces` and carries a null part. A receiver SHOULD remove
the referenced content from display. Deletion is a request to a receiver, not a
guarantee: a receiver that has already shown, copied, or stored the content cannot
be compelled to forget it.

A receiver MUST tolerate a reference to a message it does not hold. Ordering is
the embedding protocol's concern, and a reply, edit, reaction, or deletion MAY
arrive before its target or when its target never arrives at all. Such a message
MUST NOT be discarded; a receiver SHOULD hold it and resolve the reference if the
target arrives later.

### External parts

An external part references content held outside the message. It carries the
retrieval URL, the size, an AEAD algorithm with its key, nonce, and associated
data, a hash algorithm with the content hash, and optionally a filename and a
description.

External content MUST be encrypted under a key carried in the part and MUST NOT
be readable by the storage holding it. A receiver MUST verify the content hash
after retrieval and decryption, and MUST reject content whose hash does not match.

An external part MAY carry its own expiry, indicating when the sender expects the
reference to stop resolving.

### Expiry

A content value MAY declare an expiry, either as an absolute time or as a duration
measured from receipt. A receiver SHOULD stop displaying the content once it has
expired.

Expiry is a cooperative signal. It depends on receivers honouring it and on clocks
being honest, and it offers no protection against a receiver that chooses to
retain the content. See [Security and Privacy](#securityprivacy-considerations).

### Language

Every part declares a language tag as defined in
[RFC 5646](https://www.rfc-editor.org/rfc/rfc5646), or the empty string when no
language applies, as for an image or a reaction.

A `chooseOne` multipart whose nested parts differ only by language allows a
receiver to select the one matching its user's preferences. A receiver that
supports no offered language MUST select by content type as usual rather than
rendering nothing.

### Extensions

A content value carries a map of extensions. Keys are either integers assigned
through IANA registration, or values in the private-use ranges available to any
implementer without registration.

Private-use keys are not namespaced by the format. Two implementations MAY choose
the same private-use key for different purposes, and a receiver MUST NOT assume
that a private-use key it recognizes was written by an implementation that shares
its meaning. An extension intended for use between independent implementations
SHOULD be registered rather than left in the private-use range.

A receiver MUST ignore extension keys it does not recognize, and MUST NOT treat an
unrecognized key as an error.

### Receiver processing

A receiver processes a content value as follows.

1. Decode the content value. If it cannot be decoded, the message MUST be treated
   as a decode error: the receiver MUST NOT discard it silently, and SHOULD
   indicate to the user that a message arrived that could not be read.
2. Ignore any unrecognized extension key.
3. Resolve the top-level part:
   - For a **single** or **external** part, determine whether the content type is
     supported. If it is, render according to the disposition. If it is not,
     treat the part as unsupported.
   - For a **multipart**, apply its semantics: select one supported nested part
     under `chooseOne`; render all or none under `singleUnit`; process each in
     order under `processAll`. Resolve each nested part by this same procedure.
   - For a **null** part, apply the deletion described by `replaces`.
4. An unsupported part MUST NOT cause the message to be dropped. The receiver MUST
   present a visible placeholder identifying the content type it could not render,
   so that the conversation remains intact and the user can see that something was
   said.
5. If `inReplyTo` or `replaces` is set, resolve the reference. An unresolved
   reference MUST NOT cause the message to be discarded.

The governing rule is that no property of a message may cause a receiver to
silently drop it. An unknown content type, an unknown disposition, an unknown
extension, and an unresolved reference are all conditions a conformant receiver
survives.

## Wire Format Specification / Syntax

A content value is encoded as deterministic CBOR, as specified by the
[MIMI content format](https://datatracker.ietf.org/doc/draft-ietf-mimi-content/)
and identified by the media type `application/mimi-content`.

The schema below is reproduced from `draft-ietf-mimi-content-09`. Disposition
values and the extensions type are abridged. Where this document and the
referenced draft disagree, the draft is authoritative.

```cddl
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

`disposition` and `language` sit on `NestedPart`, above the variant; each variant
is tagged by its `cardinality`. A multipart holds at least two parts.

### Examples

Dispositions and cardinalities are shown by name rather than by their encoded
integer values. These illustrate structure and are not byte-exact vectors.

```text
; text/plain "hello"
[ salt, null, "", null, null, {},
  [ render, "en", single, "text/plain;charset=utf-8", 'hello' ] ]

; a reaction to the message 0x1a2b…
[ salt, null, "", null, 0x1a2b…, {},
  [ reaction, "", single, "text/plain;charset=utf-8", '👍' ] ]

; markdown with a plain-text alternative
[ salt, null, "", null, null, {},
  [ render, "en", multi, chooseOne,
    [ [ render, "en", single, "text/markdown;variant=GFM-MIMI", '**hi**' ],
      [ render, "en", single, "text/plain;charset=utf-8",       'hi' ] ] ] ]
```

## Security/Privacy Considerations

### Rendering untrusted content

A message body is written by another participant and MUST be treated as
untrusted input.

Markdown is not a safe format by default. The hazard is embedded HTML, and
widely used parsers accept it unless explicitly configured otherwise. An
implementation MUST render `text/markdown;variant=GFM-MIMI` with HTML disabled, so
that any tag appears to the user as literal text. An implementation that renders
any content type capable of carrying HTML MUST sanitize it and MUST restrict which
URL schemes are permitted in links and embedded references.

An implementation MUST NOT execute content, MUST NOT resolve external references
automatically where doing so would disclose the recipient's presence or network
address to a third party without consent, and MUST bound the resources any single
message may consume while being decoded or rendered.

### External content

External content is held by storage the sender does not control and the receiver
does not trust. Encrypting each external part under its own key keeps the storage
from reading it, and binding the part to a content hash keeps the storage from
substituting it. A receiver that skips hash verification accepts content chosen by
whoever holds the storage.

A retrieval URL discloses that a participant is fetching a particular object, and
to whom. Implementations SHOULD treat retrieval as an action with its own privacy
cost rather than as a transparent read.

### Relationships as an abuse surface

Reactions and edits let one participant attach content to another participant's
messages. Both can be used to harass: reactions at volume, and edits that change
what a quoted message appears to have said. An implementation SHOULD apply a
user's blocking and muting decisions before presenting a relationship, and SHOULD
make an edit visible as an edit rather than silently substituting content.

### Deletion and expiry are requests

Deletion and expiry ask a receiver to stop displaying content. Neither can compel
it. An implementation that has rendered content cannot guarantee it was not
captured, and an implementation under the control of an adversary will do whatever
it chooses regardless of what the message says. Both features are hygiene for
cooperating participants, and neither is a confidentiality mechanism. Users
SHOULD NOT be shown language that implies a stronger guarantee than the format can
deliver.

### Verifiable reporting

A participant who receives abusive content may need to report it to someone. Where
the embedding protocol encrypts messages between participants, a report is
inherently unverifiable: the recipient can produce any plaintext and claim it was
sent, and the sender can deny any plaintext that was.

Message references in this format are derived from the message content, which
makes them a commitment a report can be built on: a reference binds to one exact
content value, and a third party holding both can confirm they correspond.

This specification defines no reporting mechanism and names no authority to
receive a report. Whether reports exist at all, who receives them, and what
follows from one are questions for the embedding protocol and the systems built
around it, and none of them are settled here. What this format provides is the
commitment such a system would need; two limits on that commitment are worth
recording. A commitment binds one content value, so an edit or a deletion does not
retract what was committed to, and a multipart commits to every alternative it
carries rather than to the one a given receiver rendered.

### Metadata

A content value is an opaque byte string to its transport. This format defines no
cleartext header and exposes no field outside the encoded value, so it adds no
metadata beyond the length of the encoding and whatever the embedding protocol
chooses to expose. Any metadata a participant is exposed to in practice comes from
that protocol, not from this format.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [CHAT-DEFS](../../informational/raw/chatdefs.md) — Shared definitions for chat
  protocols.
- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) — Key words for
  requirement levels.
- [IETF MIMI content](https://datatracker.ietf.org/doc/draft-ietf-mimi-content/) —
  the content format; revision 09 at the time of writing.
- [RFC 6838](https://www.rfc-editor.org/rfc/rfc6838.txt) — Media type
  specifications and registration procedures.
- [IANA Media Types](https://www.iana.org/assignments/media-types) — the media
  type registry.
- [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646) — Tags for identifying
  languages.
- [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610) — CDDL, the schema notation
  used above.

### Informative

- [ContentFrame](contentframe.md) — an alternative content type identifier.
- [ConversationTypes](conversationtypes.md) — the Conversation abstraction.
- [CHAT-FRAMEWORK](chat-framework.md) — modular framework for chat protocols.
- [MIMI message status](https://datatracker.ietf.org/doc/draft-mahy-mimi-message-status/) —
  delivery and read receipts as a separate content type; an individual draft, not
  a working-group document.
- [Matrix MSC1767](https://github.com/matrix-org/matrix-spec-proposals/blob/main/proposals/1767-extensible-events.md) —
  extensible events.
- [XMTP XIP-5](https://github.com/xmtp/XIPs/blob/main/XIPs/xip-5-message-content-types.md) —
  content types identified by a namespaced string.
- [Message franking (committing AEAD)](https://eprint.iacr.org/2017/664).
