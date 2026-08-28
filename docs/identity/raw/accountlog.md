# AccountLog

| Field | Value |
| --- | --- |
| Name | AccountLog |
| Slug | TODO (assigned on promotion to draft) |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Tags | logos-chat, identity |
| Editor | jazzz <jazz@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

An account is used from more than one place — a phone, a laptop,
a second application — and each of them needs a key of its own.
Keys get added as installations come and go, and revoked when one is lost.
Anyone who wants to reach the account needs to know which keys are currently good,
and needs to be sure that list really came from the account.

This document specifies the **AccountLog**: a list of keys and records
an account signs and publishes, which anyone can fetch and check.

An account is an Ed25519 keypair, and its verifying key is the account address.
The account signs the whole list every time it changes.
A consumer fetches it, checks the signature against the address it already has,
and reads off the keys that are still valid.

Each key is endorsed for a stated purpose,
so an application takes the keys meant for it and ignores the rest.
Revoking one key leaves the others alone.

The list only ever grows — revoking appends a tombstone rather than deleting.
That means that an updated log must be prefixed with
a byte for byte copy of the previous,
which ensures that the log's history is not re-written.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

- **Account** — an Ed25519 keypair. The verifying key is the account's identity.
- **Account Address** — the identifier an account's log is published and fetched under;
  see [Account Address](#account-address).
- **Account Log** — the append-only list of entries an account has signed.
- **Entry** — one operation in the log: an addition of data, or the removal of an earlier addition.
- **Live Entry** — an `Add` entry that no valid `Remove` targets.
- **EndorsedKey** — an Ed25519 verifying key that the account has endorsed
  by signing it into the log. An EndorsedKey is *live* while no `Remove` targets it,
  and *revoked* once one does.
- **Live Set** — the ordered sequence of live entries; the account's current state.
- **Consumer** — any party that reads an account's log:
  fetching it, verifying it, decoding it, replaying it,
  and taking from it what it needs.
- **Owner** — the party holding the account signing key,
  and so the only party that can extend the log.
  An owner is also a consumer of its own log:
  it must fetch and validate the current log before extending it.
- **Context** — a short ASCII string naming what an endorsement is *for*.

## Motivation

A user wants multiple application installations to act on behalf of their account.

The simplest way to allow that is to give each installation a copy of the account key.
Every installation then holds full control of the account:
it can do anything the user can, for as long as it keeps the copy,
and its actions are indistinguishable from the user's own.
Removing one installation means changing the account key,
which removes every other installation with it
and changes the account for everyone who knew it.
Applications are not trusted with that,
and users should not have to trust them with it.

What is wanted instead is for every installation to operate under its own key:
unique to it, never shared, and limited to what that installation is for.
The account can then withdraw any one of those keys
without affecting the others and without changing the account itself.

An account is therefore not a key.
It is a set of keys that changes over the account's life,
together with associated metadata about the account.

## Theory / Semantics

### Overview

An AccountLog is a list of operations signed as a whole by the account key.
`Add` endorses data under a context; `Remove` withdraws an earlier `Add`.
Replaying the log in order — applying each `Remove` to its target —
yields the **live set**: what the account currently stands behind.

To read an account, a consumer:

```text
1. fetches the signed log stored under an address it already holds
2. verifies the signature under that address
3. decodes the payload and replays the entries
4. uses the data in the live set relevant to its own use case
```

A signed log nests:

```text
signed log      64-byte signature, then the payload it signs
└── payload     the canonical wire encoding (see Wire Format)
    └── log     the decoded sequence of entries
        └── entry    opcode + length + body; body is
                     Add { context, entry_data } | Remove { index }
            └── entry_data     Ed25519Key | Text
```

Two things the log determines rather than stores:

- **No entry count.**
  Entries are self-delimiting, so a consumer parses until the payload runs out.
- **No sequence number.**
  The log only grows, so a longer log is a newer log.
- **No entry index.**
  An entry's index is its position in the log.

The account key is absent as well, for a different reason:
it is the address, which a consumer holds before it fetches anything —
see [Account Address](#account-address).

Because the log only grows and is never rewritten,
two versions of one account's log stand in a single correct relation:
the older is a byte-prefix of the newer.
Anything longer that is not an extension is a divergent branch,
refused rather than adopted —
see [Freshness and Extension](#freshness-and-extension).

### Assumptions

Each of the following is relied on;
a deployment that cannot meet one is out of scope.

**The account key is trusted.**
It is under the sole control of its owner
and remains available to that owner for the life of the account.
Neither compromise nor loss is in scope —
the first because nothing here detects it,
the second because nothing here repairs it,
and under loss the account is frozen with its EndorsedKeys permanently irrevocable.

**EndorsedKeys are not trusted.**
An EndorsedKey may be compromised, and revocation is the response.

**The owner keeps one history.**
An account extends a single log rather than maintaining several.
Conflicting versions do occur — an old backup, a stale copy,
two publishes without a re-fetch in between. AccountLogs that different at the end are considered mistakes, not an account deliberately showing
different histories to different readers.

**Account logs reach consumers somehow.**
Some means exists to publish a signed log and fetch one by address.
This document neither specifies it nor depends on it:
a signed log is self-contained, so how its bytes were obtained changes nothing.

**Addresses are exchanged out of band.**
How a consumer comes to hold an address is out of scope;
this document begins once it holds one.
Every guarantee here is relative to that address being the right one,
and nothing in the log corrects a wrong one.
Address exchange is therefore the system's only trust decision,
and belongs to the protocol that makes it.

**The log is public.**
Anyone holding an address can fetch the log at any time.
No entry is confidential. See [Privacy](#privacy).


### Account Address

Every account is backed by an Ed25519 signing key, and the address is its Ed25519 verifying key.

A consumer uses the address to verify the log's signature, and ensure it belongs to the account.
How it came to hold that address is out of scope (see [Assumptions](#assumptions)).

**Requirements:**

- A consumer MUST NOT use an address until it has established that
  the address belongs to the account it intends to reach.
  An address obtained from the same source that supplied the log
  has not been established.

### Signing and Verification

```text
signature := Ed25519_sign(account_signing_key, payload)
```

The signature and payload travel together as one artifact;
see [Signed Log](#signed-log) for its layout.

**Requirements:**

- An owner MUST sign the exact payload bytes it transmits,
  and a consumer MUST verify over the exact bytes it received.
  There is no re-serialization on either side.
- A consumer MUST verify the signature under the address it holds for
  the account it intends to reach; see [Account Address](#account-address).
  A validly-signed log for account A cannot then be passed off as account B's.
- A consumer MUST verify the signature **before** decoding the payload,
  so that decoding is never applied to unauthenticated bytes.

#### Ed25519 Verification Profile

[RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) permits both
cofactored and cofactorless verification and is silent on several encoding
edge cases, so two conformant implementations can disagree on whether the
same signature verifies. The profile is therefore pinned.

**Requirements:**

- A consumer MUST use cofactorless verification.
- A consumer MUST reject a signature whose scalar component `S` is not
  canonically reduced, i.e. `S` MUST satisfy `0 <= S < L`.
- A consumer MUST reject any Ed25519 point that is not a canonical compressed
  Edwards point encoding, or that is small-order.
  This covers the account address, the commitment `R`, and every
  `Ed25519Key` in the log.

These rules correspond to `ed25519-dalek`'s `verify_strict` and
to libsodium's `crypto_sign_verify_detached`.
Implementations MUST NOT use a permissive `verify` path.

### Log Data Model

A log is an ordered sequence of entries, numbered from zero by position.
An entry either endorses data under the account
or withdraws an endorsement made earlier in the log, and does nothing else:

```text
Add { context, entry_data }   endorse `entry_data` under `context`
Remove { index: u32 }         tombstone the Add at position `index`
```

`entry_data` is one of:

```text
Ed25519Key([u8; 32])   an Ed25519 verifying key
Text(String)           a UTF-8 record
```

**Requirements:**

- A consumer MUST derive an entry's index from its position in the log.
  An index is never stored or transmitted separately.
- Entries MUST NOT be deleted, reordered, or rewritten.
  A log is only ever extended.


### Contexts

All entry_data in an AccountLog carries a **context**: a short string naming what the endorsement
is for and how it can be used.

```text
context   := <namespace> "." <label>
```

The **namespace**, up to the first `.`, names the specification that defines
the context. The **label** is the rest, and names one context within that
namespace. Any further `.` are part of the label. The context `chat.messaging` is the
label `messaging` in the namespace `chat`.

A consumer selects data it needs by its context and ignores the rest, including contexts it does not recognize.

This document defines and allocates no context. There is no registry —
a specification defines its own namespace.

**Requirements:**

- A consumer MUST only use a key or record for the purpose defined by its context specification.


### Unknown Entries

A consumer must be able to skip an entry it does not recognize, or the first
unrecognized entry locks it out of the account permanently. An entry's `len`
gives its extent without the consumer understanding it, and `Remove` is the
only subtractive operation — so an unrecognized entry can only be endorsing
something, and a consumer that ignores it acts on less authority, never more.

**Requirements:**

- A consumer that does not recognize an entry's opcode MUST retain the entry
  as an opaque live slot: counted, indexed, targetable by a later `Remove`,
  and never surfaced to the application.
  It MUST NOT reject the log.
- A consumer that does not recognize an `Add`'s `data_tag`
  MUST retain the entry as an opaque live slot rather than reject it.
- A future opcode MUST only add. There will never be an operation other than
  `Remove` that takes something away, because an old consumer would skip it
  and go on trusting what it was meant to withdraw.
  To change what an old consumer honours, remove the entry and add a new one
  under a different context.

The last requirement is a constraint on this document's future editors.
A consumer acts only on entries it understands, so the only way to change what
an old consumer does is `Remove`, which every consumer understands by construction.

### Log Updates

The history of an AccountLog cannot be rewritten.
Every update appends to the end of the log, and a new version cannot differ
from a previous version except for at the end.

A consumer checks this on every fetch: it only adopts a newly fetched candidate
payload if its bytes start with the same bytes of the one it currently holds.
Where the bytes match the fetched log is a continuation and is the newer of the two.
Where the bytes do not match, the two are different histories —
the account has equivocated.

A fetched payload identical to the one held is a valid candidate that adds nothing,
and adopting it changes nothing.

**Requirements:**

- A consumer MUST retain the latest verified payload.
- A consumer MUST verify that the retained payload is a byte-prefix of any new
  candidate; if not the candidate MUST be discarded.
- A longer log is a newer log. A consumer MUST use the newest log it has seen.
- A protocol MAY provide an out-of-band check that two parties hold the same
  log for an account. This document defines none.

### Validity and the Live Set

A log is valid when every `Remove` targets a strictly earlier, still-live `Add`.
Any other `Remove` makes the whole log invalid.

To derive the live set, walk the log in order and mark each `Remove`'s target
as dead. The live set is every unmarked `Add`, in log order, including opaque
slots the consumer could not decode. The *typed* live set — the keys and
records an application acts on — is the live set restricted to entries the
consumer understands.

**Requirements:**

- A consumer MUST reject the whole log if any part of it is invalid.
- A consumer MUST reject a `Remove` whose index is at or after its own position.
- A consumer MUST reject a `Remove` targeting an entry that is not an `Add`.
- A consumer MUST reject a `Remove` targeting an entry already removed.
- An owner MUST validate a log before signing it.
- Only this document states what makes a log invalid.
  A specification built on the AccountLog MUST NOT add a condition,
  and a consumer MUST ignore an entry it cannot use rather than reject the log.
  
### Versioning

The encoding version lives in the domain string (`logos:accounts:1`).
A layout change is a new domain, which is a new signature domain,
so payloads of different versions cannot be confused, by construction.

The framing in [Entry Encoding](#entry-encoding) means most future changes
do not need a version bump at all:
a new opcode or data variant is an allocation,
not a new encoding.
The version is reserved for changes to the payload or entry *framing* itself.

**Requirements:**

- A consumer MUST reject a payload whose domain does not match byte-for-byte.
- A consumer SHOULD distinguish, in the error it reports,
  a payload bearing `logos:accounts:` with an unrecognized version
  from a payload that is malformed,
  so that an operator can tell "newer than me" from "corrupt".

## Wire Format Specification / Syntax

This section defines four encodings:
the **account address**, the identifier used to refer to the account;
the **signed log**, the artifact that is stored and transmitted;
the **log encoding**, which frames a sequence of entries within it;
and the **entry encoding**, which defines the bytes of a single entry.
All integers are little-endian.

### Address Encoding

```text
address := 32 bytes, an Ed25519 verifying key
```

An address is transmitted and stored in binary. Where it appears in text —
a URI, a config file, a log line — it is 64 lowercase hexadecimal characters
with no prefix.

**Requirements:**

- A consumer MUST accept an address in string form only as 64 lowercase
  hexadecimal characters with no prefix, and MUST reject any other form.

### Signed Log

```text
signed log := signature || payload

signature : 64 bytes, Ed25519 over `payload`
payload   : the remainder, to the end of the artifact
```

The signature comes first because it is fixed-width:
a consumer takes the first 64 bytes and knows the rest is the payload,
whose extent is the artifact's own.
No length is carried.
A length would sit outside the signature and could disagree with it,
and a payload of the wrong extent fails verification anyway.

**Requirements:**

- A consumer MUST reject an artifact shorter than 65 bytes:
  64 for the signature and at least the domain.

### Log Encoding

The payload — the bytes that are signed:

```text
payload := domain || entry*

domain : "logos:accounts:1\0"   constant prefix; the segment after the
                                second colon is the encoding version
entry* : zero or more entries, concatenated, filling the payload exactly
```

The domain provides domain separation: the account key may live in an external
signer (wallet, enclave) that signs other things, and the prefix stops a
signature obtained for another purpose from being replayed as an account-log
signature, and vice-versa. The trailing NUL keeps the domain from being a
prefix of any other domain.

There is no entry count.
Entries are self-delimiting, so a consumer parses until the payload is exhausted;
a stored count could only ever agree or disagree with what is already there.

Every entry is individually framed with its own length,
so a consumer finds each entry boundary without interpreting the entry's contents.
This is what makes an unrecognized entry skippable rather than fatal
(see [Unknown Entries](#unknown-entries)).

**Requirements:**

- A consumer MUST reject a payload whose domain prefix does not match byte-for-byte,
  including the trailing NUL.
- A consumer MUST reject a payload whose final entry does not end
  exactly at the end of the payload.

### Entry Encoding

#### Entry

Every entry is an opcode byte, a body length, and a body:

```text
entry := opcode || len || body

opcode : u8      the operation; high nibble reserved, MUST be zero
len    : u16 LE  length of `body` in bytes
body   : exactly `len` bytes
```

**Requirements:**

- A consumer MUST reject a payload in which an entry's `len`
  runs past the end of the payload.
- A consumer MUST reject an entry whose opcode byte has any of its
  high four bits set.
- Trailing bytes inside an entry are not permitted.
- An owner MUST produce exactly the layout above;
  there is no alternative serialization of the same entry.

#### Opcodes

```text
 7 6 5 4   3 2 1 0
+---------+---------+
| reserved| opcode  |
+---------+---------+
```

The high nibble is reserved against a future need for
per-entry flags alongside the opcode.
Sixteen opcodes is more than this format is expected to allocate;
recovering those bits later would require a new encoding version, so they are held now.

| `opcode` | Operation | `body` |
| --- | --- | --- |
| `0x01` | Add | a context and tagged data |
| `0x02` | Remove | `u32 LE` index of the target entry |

Opcodes not assigned above are reserved.

#### Add

An `Add` body carries the context first, then a tagged data variant:

```text
Add body := ctx_len || context || data_tag || data_body

ctx_len  : u8      length of `context` in bytes, 1-255
context  : ASCII   what this endorsement is for, `<namespace>.<label>`
data_tag : u8      selects the variant below
data_body: variant, to the end of the entry body
```

| `data_tag` | Data | `data_body` |
| --- | --- | --- |
| `0x01` | Ed25519Key | 32 bytes, fixed width |
| `0x02` | Text | UTF-8 value, to the end of the entry body |

```text
0x01 <len> <u8 ctx_len> <context> 0x01 <32 bytes>   Add(Ed25519Key)
0x01 <len> <u8 ctx_len> <context> 0x02 <value>      Add(Text), UTF-8
```

The two tag spaces are independent:
`data_tag` is only read after an `Add` opcode,
so a future data variant and a future operation are separate allocations.
`data_tag` values not assigned above are reserved.

**Requirements:**

- A consumer MUST reject an `Add` whose `ctx_len` is zero,
  or whose `context` extends to or past the end of the entry body,
  leaving no room for `data_tag`.
  A context is at most 255 bytes; `ctx_len` cannot express more.
- A consumer MUST reject a `context` whose namespace does not begin with
  a character in `a`-`z`, that contains no `.`,
  or that contains any byte outside `a`-`z`, `0`-`9`, `.`, `-`, `_`.
- A consumer MUST compare contexts as raw bytes.
- A consumer MUST reject a `Text` whose `value` is not valid UTF-8.
  A `Text` with an empty `value` is permitted and means the record is present but blank.

#### Remove

```text
Remove body := index

index : u32 LE   position of the target entry
```

```text
0x02 <len=0x0004> <u32 LE index>                    Remove
```

**Requirements:**

- A consumer MUST reject a `Remove` whose `len` is not 4.

### Resource Limits

An account log grows for the life of the account and is never compacted,
so its size is unbounded.
As AccountLogs need to be cached,
an artificial limit is imposed to keep log sizes manageable.

**Requirements:**

- A consumer MUST reject a payload larger than 131072 bytes.
- An owner MUST NOT publish a payload larger than 131072 bytes.

The limit is a lifetime budget, not a per-update one:
an account that reaches it can neither endorse nor revoke again,
and nothing in this document recovers the space.

## Implementation Suggestions

- Validate in one pass.
  Because `Remove.index < position` is required,
  a single forward walk carrying a liveness bitmap suffices;
  no second pass or backpatching is needed.
- Keep the verified payload, not the decoded log, as the retained per-account state.
  The extension check operates on bytes,
  and storing the bytes means the retained copy cannot drift from what was signed.
- Expose key selection as `keys_for(context)` and provide no `keys()`.
  The scoping guarantee is a property of how callers reach the live set,
  so an API that can return every live key will eventually be used that way,
  and the reason the caller was wrong will not be visible at the call site.
- Signal freshness with the entry count.
  It is monotonic, non-secret, and derivable from any log a consumer holds,
  so a protocol can carry the count it last saw alongside its own messages,
  and a consumer holding fewer entries than claimed re-fetches.
  Act on such a claim only when it exceeds what you hold:
  a higher claim is safe even unauthenticated, since inflating it
  gains an attacker nothing but a needless fetch,
  while an equal or lower claim is exactly what a revoked key would send
  to stop you looking.
- Expect publish races. Where two publishes extend the same log, at most one lands.
  An owner whose publish is refused re-fetches, re-applies its intended entries
  to the log it received, re-signs, and retries. This is a lost race, not a fork.
- Represent an opaque slot explicitly in the decoded log —
  an `Unknown { opcode, body }` variant, not a hole or a `None`.
  Replay has to count it, and a representation that can lose it
  reintroduces the index-shift bug the framing exists to prevent.
- Treat "fork detected" as a distinct error type all the way up the stack.
  Collapsing it into a generic verification failure loses the one signal
  this design exists to produce.
- Endorse a key under one context only.
  Nothing here rejects a log with the same key live for two different purposes, 
  but that ought to be avoided for good key hygiene. 

## Security/Privacy Considerations

### Security

- **No account key rotation or recovery.**
  There is no mechanism to rotate an account key.
  Both compromise and loss are permanent for the lifetime of the address.
- **No identity binding.**
  An account is just a keypair, so anyone can make one and publish a log under
  it. Nothing here says whose account it is.
  A log fetched under the wrong address verifies and replays cleanly, because
  it is a real log — of someone else's account.
  Until you have established that an address belongs to the person you mean,
  the log tells you nothing about them (see [Assumptions](#assumptions)).
- **A compromised account key defeats every check.**
  An attacker holding it extends the log arbitrarily — revoking every
  legitimate key and endorsing its own — without ever diverging from the
  history consumers hold, because a clean extension is exactly what a
  legitimate owner produces. Consumers accept it as a normal update.
- **A consumer can never know its log is the most recent.**
  The log carries no time, and whatever served it may have served an older copy.
  An attacker holding a revoked key exploits this: it keeps presenting the key
  and says nothing about the log, which is indistinguishable from an account
  that has not changed.
  A protocol whose security depends on revocation must specify how its
  consumers learn that a log has advanced.
- **First contact is unprotected.**
  A consumer with no retained payload has nothing to compare against,
  so it can detect neither staleness nor a rewritten history.
  The guarantee is relative to what a consumer has already seen, never absolute.
- **Key Context Binding in Consumers**
  A consumer that accepts any live key, rather than the ones endorsed for what
  it is doing, gives an attacker who has stolen one key access to everything
  that consumer does. The context is what limits the damage,
  and only the consumer can apply it.

### Privacy

- **Revocation is a tombstone, not an erasure.**
  Revoked keys remain visible in the log forever.
  This is deliberate — history is the audit trail —
  but it publishes the account's full endorsement history to anyone who can fetch it.
- **The log is a linkable, pollable, permanent record.**
  Anyone holding an address can fetch it repeatedly and observe,
  without any interaction with the user:
  how many keys are live, under which purposes, when each was endorsed,
  when each was retired (and therefore when a device was lost or replaced),
  and the history of any `Text` records such as display names.
  Entry count alone fingerprints an account across observations.
- **Interaction with sender anonymity.**
  Where this is deployed alongside a protocol providing sender unlinkability,
  the AccountLog is a per-account identifier that is by design long-lived and
  publicly accessible.
  Deployments MUST consider whether fetch patterns against whatever serves logs
  reintroduce linkability that the messaging layer removes.

## Test Vectors

All vectors use the [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032)
Section 7.1 test keys, so they are independently reproducible.
Contexts are illustrative; this document allocates none.

```text
account signing key (seed):  9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60
account address (verifying): d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a
endorsed key 1:              3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
endorsed key 2:              fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025
domain:                      6c6f676f733a6163636f756e74733a3100
opcode Add    = 0x01
opcode Remove = 0x02
contexts used:               chat.messaging, profile.displayname, storage.vault
```

An `Add(Ed25519Key)` under context `chat.messaging` decomposes as:

```text
01              opcode: Add
3000            len = 48
0e              ctx_len = 14
636861742e...   context "chat.messaging"
01              data_tag: Ed25519Key
3d4017c3...     32-byte key
```

**V1 — empty log** (domain only, live set empty)

```text
payload:   6c6f676f733a6163636f756e74733a3100
signature: d58b9c39e92232bfa686a6b60b445168162a11ea8a47730289085f51ac161f4b
           b57bda68f65eb0f7e7c5dd8345fb6fb5375a65d4086385da76a383213800940e
```

**V2 — one EndorsedKey** under `chat.messaging`

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
signature: a2b0384fc0b3b738e830f86ecd5b34c8139f9d0c2084ff57fee84e71ad1b47aa
           83b5ec9f7c38403234390c86be534349d07a045a5e239c6f9c648a262e9a9f04
```

**V3 — two EndorsedKeys**, same context (strictly extends V2)

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           0130000e636861742e6d6573736167696e6701
           fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025
signature: 18ca203291c5f9ad74142635174113a4619f125ca05d4d0dafda46081096ddae
           bc10c05d10ddf29caa5e444bd975f2f0cc05dca9b34e3ea18d2e21fda5c85a02
```

**V4 — first EndorsedKey revoked** (`Remove { index: 0 }`)

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           0130000e636861742e6d6573736167696e6701
           fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025
           02040000000000
signature: 060ec48ee5c7d245417c5af6a433b7451cd325ab80547bd377b070b54871a5f6
           8e3b207e3ea678408ff9ace88caa1cfd774cb2bdb45f27b3091fd02387fc4501
```

**V5 — EndorsedKey plus a record** under `profile.displayname`, value `alice`

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           011a001370726f66696c652e646973706c61796e616d6502616c696365
signature: 9f23adb7cdc9da09b5831f86707888fcfedc884def1c148cf41efe73095168ca
           9c3f19fa29e6acc1a2d2601670dd5fe5c65c11e9df56048e93cd7a823c82830b
```

**V6 — unknown entry, skipped** (opcode `0x0f`)

A v1 consumer does not know opcode 15.
It is not `Remove`, so it is additive:
index 1 is retained as an opaque live slot,
the `Remove` at index 2 validly targets index 0,
and the typed live set is empty.
A consumer that skipped index 1 *without counting it*
would match the `Remove` to the wrong slot and MUST NOT do so.

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           0f0400deadbeef
           02040000000000
signature: f8e9e2a71ea777f111f3ccd84f6429493101de77d65b4baa3450bb1d45c591e5
           2e100bdc7ef6b9ba8d035e464c656d21dccbfee97f52a66f9cb94c9b2cf05d00
```

**V7 — two live entries sharing one context** (`profile.displayname`)

Both are live; neither is removed.
A consumer working under `profile.displayname` selects both, in log order:
`alice` then `alice j`.
Which of them the account's display name actually is
is a question for whatever defines that context, not for this document.

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           011a001370726f66696c652e646973706c61796e616d6502616c696365
           011c001370726f66696c652e646973706c61796e616d6502616c696365206a
signature: 744f0eef44732a307ea89c784d04fa34d43f0c6314c2ec5222e5c7db81a4380b
           a5d3326c4c25f4163432d4a267f40a9e4c2071e90308a5976f6ec897587a5f08
```

**V8 — two key contexts** (`chat.messaging` and `storage.vault`)

Both keys are live. A consumer working under `chat.messaging` selects key 1 only;
key 2 does not match and MUST NOT be used for messaging.
A consumer that knows neither context selects nothing and rejects nothing.

```text
payload:   6c6f676f733a6163636f756e74733a3100
           0130000e636861742e6d6573736167696e6701
           3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
           012f000d73746f726167652e7661756c7401
           fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025
signature: b5a0171ebd934937724db4a8385021f53a2552c5b00a0c2e0da496ee76c1c821
           ec24e7de828fcf784d2dbc6b6303cb01a82f0555dfefbbb32936788067cd9f03
```

Payload hex is line-wrapped and internally spaced for presentation only;
concatenate the fragments to recover the exact signed bytes.
A signed log is the 64-byte signature followed by the payload,
so each artifact above is `signature || payload`.

### Rejection Vectors

Each vector below is a payload that a consumer MUST reject for the reason given.
All are signed by the same account key as the vectors above,
so every signature verifies under address
`d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a`.
A consumer that rejects one at the signature check has failed the test
for the wrong reason.

**N1 mismatched domain** — domain byte-compare fails

```text
payload:   6c6f676f733a6163636f756e74733a32000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c
signature: 66001bafa87f11b844ef6d10f6f685d5cbb87e052c2a1c93eea806b60ef2c250
           f1f8c177eac8a650d65479470b9b87e67b03c326302d4eb641674e48cc462d00
```

**N2 last entry ends before payload does** — final entry len=48, only 10 bytes follow

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c01300000000000000000000000
signature: 21f218241cba752ccaab652261620e279413df561f68e3133fb6f44f96234ca5
           cd2d1240b284784e703339be28ecfbbce5fed4bf752718f19227ae3b001b0c0f
```

**N3 trailing bytes after last entry** — two bytes remain, not a parseable entry

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660cffff
signature: ab5501ace7945c63ff25df8680a64977d37af34910c781177a82acf49dceb7d7
           32454118a603f31a649ce9d8410c356239eddc08ee9abfb821287cdf132f8d0e
```

**N4 entry len runs past payload** — len=65535 with 4 bytes available

```text
payload:   6c6f676f733a6163636f756e74733a310001ffff00000000
signature: c9ce34c9ae7a6448277db4f864e5fef89125b47e9a2bd9b72ffc25b967a06009
           d07c34650fa5f34aa5509e317bae668b9db7cebb11373ee42525f1fcf736b109
```

**N5 opcode high bit set** — opcode 0x81, high nibble non-zero

```text
payload:   6c6f676f733a6163636f756e74733a31008130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c
signature: 3b5188eb2218ecb0465ac2ac4cc9cf8b40cb12c9655c70f04aa5addc6184d001
           45f619b90db9461bc332e2660d96889743cbc43a89adabec74e7add203eb510c
```

**N6 Remove with wrong len** — Remove body is 5 bytes, must be 4

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c0205000000000000
signature: a4ca08ef15de1ed782b32e2cf6fd50cb9e2e59158513f714f81bc16e848cb358
           9ed6cb168a2eb6c1d4d3afd164a77b407c821802cd6495025103d36538690b01
```

**N7 Add ctx_len zero** — ctx_len = 0

```text
payload:   6c6f676f733a6163636f756e74733a310001220000013d4017c3e843895a92b7
           0aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
signature: a60390e07cd2b1fc01197e207647c665586eed63c849b2ad42bb8ac129382ddf
           79057d418e00d845a354157f88287153a82a32e8ed3f0a117569c0b421218b0e
```

**N8 context leaves no room for data_tag** — body ends after context

```text
payload:   6c6f676f733a6163636f756e74733a3100010f000e636861742e6d6573736167
           696e67
signature: e4abccb6d6570e237fd465d2cff39ca06c7364f428518331aa8d633a46a0fc9a
           cdeb571b09fc9ef7636e379461c179ee2be88fa342bc6a4689ce2ae5c955cc0a
```

**N9 context has illegal byte** — '@' outside a-z 0-9 . - _

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573734067
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c
signature: 9bc59f4e2928a474af39caa45b379486554fa94a158ca78e27ace1b97a5727aa
           6c66fd954b01d956ee501af2d463226977b98b9499496fd7fabb939a1cbf600d
```

**N10 context has no namespace boundary** — no '.' present

```text
payload:   6c6f676f733a6163636f756e74733a3100012b00096d6573736167696e67013d
           4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
signature: 09457e5c68e846f1362343e4eaa7dd5371d48359328ec9987ffc80ad5d7d3a18
           ae46232bc4515d3584f541af36c27dfab077b1192030ce9f425e6792064c4b09
```

**N11 namespace does not begin with a letter** — leading digit

```text
payload:   6c6f676f733a6163636f756e74733a31000131000f31636861742e6d65737361
           67696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55
           f12af4660c
signature: b3c3b71783b1da9686f485a323b455c0a4eaf78ff3a596b5e3c5af60b6a0c4b8
           b97a37c0f2dd0e6dad55590cfb22a91969fa08bd2b06b37d0afde0adcceabf0e
```

**N12 invalid UTF-8 in Text** — 0xff 0xfe is not UTF-8

```text
payload:   6c6f676f733a6163636f756e74733a31000117001370726f66696c652e646973
           706c61796e616d6502fffe
signature: d6c35f646506187cb3e1fce7fc36eb226be953ea2ec9b22b12249e67bdcd3d03
           31992d19347ad07c9bd0b38668d8420b93814fa4d6b8e03702e419c80cedec0b
```

**N13 Remove index at its own position** — index 1 == its own position

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c02040001000000
signature: cc625f45f42f9cce8fa0fa53997fb67e5a844e3af9b8fa43804fe22a57fb2cb1
           075a541f815062ad85787279a0ae9b442c7968bce84da42cf1c598b0cf87260b
```

**N14 Remove of an already-removed entry** — index 0 already dead

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c0204000000000002040000000000
signature: aae22448caae0f4f0fcbbe0557efe2bdfbf2e1f636cbbbcfbd75bf2a7a534d7f
           499e3f04f36204c5f127b4b3114554c7da0c5548573eb4866f3563554db8250f
```

**N15 Remove targeting a Remove** — index 1 is a Remove

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c0204000000000002040001000000
signature: 1904b4216f8eee78035951706be188bbdd8d3250d37f2015cb81e9bc60dfa826
           1b152ea351d672108e22c14703fd4d3f0e3439ad68c093c5e7e69764749c5200
```

**N16 same key live twice** — K1 live under two contexts

```text
payload:   6c6f676f733a6163636f756e74733a31000130000e636861742e6d6573736167
           696e67013d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f1
           2af4660c012f000d73746f726167652e7661756c74013d4017c3e843895a92b7
           0aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
signature: 9c16135b9414ee4302d15fa274c4616f43a88668d7d7efa0de07c6b7cc8ed5f5
           5dd1134534ef56aeb1a37a1cc98eb3be80c10745a94896b406a24dbd0f6fbd07
```

Two further cases are not payloads and so have no vector here:
an artifact shorter than 65 bytes, which carries no room for a payload,
and a replacement log that does not extend the one a consumer holds,
which is a relation between two logs rather than a property of one.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Normative

- [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) —
  Key words for use in RFCs to Indicate Requirement Levels
- [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) —
  Edwards-Curve Digital Signature Algorithm (EdDSA)

### Informative

- [1/COSS](https://lip.logos.co/research/draft/1/coss.html) —
  Consensus-Oriented Specification System
- [ZIP-215](https://zips.z.cash/zip-0215) —
  Explicitly Defined Validity Criteria for Ed25519 Signatures
- [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446) Appendix E —
  on the value of pinning verification behavior rather than inheriting it
