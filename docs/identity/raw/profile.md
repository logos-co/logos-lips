# Account Profile

| Field | Value |
| --- | --- |
| Name | Account Profile |
| Slug | TODO (assigned on promotion to draft) |
| Status | raw |
| Type | RFC |
| Category | Standards Track |
| Tags | logos-chat |
| Editor | jazzz <jazz@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

Users want to publish a small amount of information about themselves that other
accounts resolve.
This document claims the `profile` namespace in the [AccountLog](#references),
defines the contexts within it, and states which values a consumer considers.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Terms from the AccountLog — account, log, entry, live, live set, context,
namespace, label, index — are used as defined there.

- **Profile** — user related metadata attached to an account.
  The account is the entity itself; the profile is the data that describes
  the owner.

## Motivation

In an identity system, accounts represent more than just keys;
they carry metadata that describes the owner as well.
The AccountLog defines how data is stored and updated,
but provides no semantics about what data may be attached to describe the
account itself.
Without a canonical definition for this metadata, developers will create their
own mechanisms, which leads to fragmentation and to different user experiences
across applications.

## Theory / Semantics

### Overview

This document defines the `profile` namespace within the AccountLog.

A profile contains data about the owner, exclusively for displaying and
rendering accounts to other users.
User preferences, and synchronising data between installations of the same
account, are out of scope.

The AccountLog settles whether a log is valid and which of its entries are live.
This document applies to the live set alone,
and settles what the entries selected under a profile context mean.
The two never overlap: nothing here makes a log invalid,
and no condition described here is grounds for rejecting one.

Profile data is published by the account and is provided as is.
It is unverified, and nothing here obliges a consumer to use it.
An account that publishes nothing under a context is the ordinary case,
and a consumer encountering it decides for itself what to show.

### Entry Validity

This document determines only what values are valid in the defined contexts.
An entry that fails a requirement below MUST be ignored,
and has no bearing on the validity of the log itself.

An entry in this namespace is valid only if it satisfies these requirements:

- The context MUST be one listed in this document.
- The `entry_data` MUST match the type defined for that context.
- The value MUST satisfy the requirements stated for that context below.

Invalid entries MUST NOT be considered when determining recency
or any other criteria.

### Recency

A log MAY contain multiple entries under the same context.
Removing an earlier entry is an acceptable way to replace it,
but is not required.
Where several share a context, a consumer MUST use the most recent valid
value — the one occurring latest in the log.

### Namespace

All labels defined by this document use the namespace `profile`.

**Requirements:**

- A specification other than this one MUST NOT allocate a label in the
  `profile` namespace.

### Contexts

| Context | `entry_data` | Description |
| --- | --- | --- |
| `profile.displayname` | Text | A short name for applications to use when displaying the account |

#### displayname

A display name is a short label an account publishes for others to show
in place of its address.
It is not unique, not registered, and not verified.
It carries no claim beyond that the account endorsed it.

An account has at most one display name, though there may be several entries.
The most recent is the canonical one.

**Requirements:**

- A `profile.displayname` value MUST NOT be empty.
- Where several entries share this context, a consumer MUST treat the one
  with the highest index as current.
- A consumer MAY use non-current entries to display previous aliases.

## Wire Format Specification / Syntax

This document defines no encoding.
Profile entries are AccountLog entries and are encoded as the AccountLog
specifies.

## Security/Privacy Considerations

### Security

- **A display name is not an identifier.**
  Two accounts may endorse the same name, and a name may be chosen to
  resemble another through similar-looking characters, mixed scripts, or
  invisible ones. A consumer MUST NOT use a display name to decide which
  account it is talking to. Identity is the account address.
- **Presentation is where impersonation succeeds.**
  Nothing in this document prevents a misleading name;
  it can only be addressed where the name is shown, alongside
  something the account cannot choose.

### Privacy

- **A display name is public and permanent.**
  The log is append-only and never compacted, so every name an account has
  ever endorsed remains readable after it is removed.
  A removed name is withdrawn, not erased.
- **Name changes are observable.**
  Anyone holding the address can fetch the log repeatedly and see when a name
  changed, and to what, without any interaction with the account.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) —
  Key words for use in RFCs to Indicate Requirement Levels
- AccountLog — `docs/identity/raw/accountlog.md`