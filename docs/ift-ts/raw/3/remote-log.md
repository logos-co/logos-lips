# 3/REMOTE-LOG

| Field | Value |
| --- | --- |
| Name | Remote log specification |
| Slug | 3 |
| Status | draft |
| Type | RFC |
| Category | Standards Track |
| Editor | Oskar Thorén <oskarth@titanproxy.com> |
| Contributors | Dean Eigenmann <dean@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-16** — [`f01d5b9`](https://github.com/vacp2p/rfc-index/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/ift-ts/raw/3/remote-log.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/vacp2p/rfc-index/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/3/remote-log.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/vacp2p/rfc-index/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/3/remote-log.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/vacp2p/rfc-index/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/3/remote-log.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/vacp2p/rfc-index/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/3/remote-log.md) — ci: add mdBook configuration (#233)
- **2024-09-13** — [`3ab314d`](https://github.com/vacp2p/rfc-index/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/3/remote-log.md) — Fix Files for Linting (#94)
- **2024-02-01** — [`3fd8b5a`](https://github.com/vacp2p/rfc-index/blob/3fd8b5ac65996eb49a0da2a1e232678727c09a75/vac/3/remote-log.md) — Update and rename README.md to remote-log.md
- **2024-01-30** — [`dce61fe`](https://github.com/vacp2p/rfc-index/blob/dce61fe029550810b83b075145e8a0130048344b/vac/3/README.md) — Create README.md

<!-- timeline:end -->

A remote log is a replication of a local log.
This means a node can read data that originally came from a node that is offline.

This specification is complemented by a proof of concept implementation[^1].

## Definitions

| Term        | Definition                                                                                   |
| ----------- | --------------------------------------------------------------------------------------       |
| CAS         | Content-addressed storage. Stores data that can be addressed by its hash.                    |
| NS          | Name system. Associates mutable data to a name.                                              |
| Remote log  | Replication of a local log at a different location.                                          |

## Wire Protocol

### Secure Transport, storage, and name system

This specification does not define anything related to: secure transport,
content addressed storage, or the name system. It is assumed these capabilities
are abstracted away in such a way that any such protocol can easily be
implemented.

<!-- TODO: Elaborate on properties required here. -->

### Payloads

Payloads are implemented using [protocol buffers v3](https://developers.google.com/protocol-buffers/).

**CAS service**:

```protobuf
syntax = "proto3";

package vac.cas;

service CAS {
  rpc Add(Content) returns (Address) {}
  rpc Get(Address) returns (Content) {}
}

message Address {
  bytes id = 1;
}

message Content {
  bytes data = 1;
}
```

<!-- XXX/TODO: Can we get rid of the id/data complication and just use bytes? -->

**NS service**:

```protobuf
syntax = "proto3";

package vac.cas;

service NS {
  rpc Update(NameUpdate) returns (Response) {}
  rpc Fetch(Query) returns (Content) {}
}

message NameUpdate {
  string name = 1;
  bytes content = 2;
}

message Query {
  string name = 1;
}

message Content {
  bytes data = 1;
}

message Response {
  bytes data = 1;
}
```

<!-- XXX: Response and data type a bit weird, Ok/Err enum? -->
<!-- TODO: Do we want NameInit here? -->

**Remote log:**

```protobuf
syntax = "proto3";

package vac.cas;

message RemoteLog {
  repeated Pair pair = 1;
  bytes tail = 2;

  message Pair {
    bytes remoteHash = 1;
    bytes localHash = 2;
    bytes data = 3;
  }
}
```

<!-- TODO: Better name for Pair, Mapping? -->

<!-- TODO: Consider making more useful in conjunction with metadata field.
It makes sense to explicitly list what sequence a message is <local hash,
remote hash, data, seqid> this way I can easily sync a messages prior or
after a specific number.
To enable this to be dynamic it might make sense to add page info so
that I am aware which page I can find seqid on -->

## Synchronization

### Roles

There are four fundamental roles:

1. Alice
2. Bob
3. Name system (NS)
4. Content-addressed storage (CAS)

The *remote log* protobuf is what is stored in the name system.

"Bob" can represent anything from 0 to N participants. Unlike Alice,
Bob only needs read-only access to NS and CAS.

<!-- TODO: Document random node as remote log -->
<!-- TODO: Document how to find initial remote log (e.g. per sync contexts -->

### Flow

<!-- diagram -->

![notification](images/remote-log.png)

<!-- Document the flow wrt operations -->

### Remote log

The remote log lets receiving nodes know what data they are missing. Depending
on the specific requirements and capabilities of the nodes and name system, the
information can be referred to differently. We distinguish between three rough
modes:

1. Fully replicated log
2. Normal sized page with CAS mapping
3. "Linked list" mode - minimally sized page with CAS mapping

**Data format:**

```yaml
| H1_3 | H2_3 |
| H1_2 | H2_2 |
| H1_1 | H2_1 |
| ------------|
| next_page   |
```

Here the upper section indicates a list of ordered pairs, and the lower section
contains the address for the next page chunk. `H1` is the native hash function,
and `H2` is the one used by the CAS. The numbers corresponds to the messages.

To indicate which CAS is used, a remote log SHOULD use a multiaddr.

**Embedded data:**

A remote log MAY also choose to embed the wire payloads that corresponds to the
native hash. This bypasses the need for a dedicated CAS and additional
round-trips, with a trade-off in bandwidth usage.

```yaml
| H1_3 | | C_3 |
| H1_2 | | C_2 |
| H1_1 | | C_1 |
| -------------|
| next_page    |
```

Here `C` stands for the content that would be stored at the CAS.

Both patterns can be used in parallel, e,g. by storing the last `k` messages
directly and use CAS pointers for the rest. Together with the `next_page` page
semantics, this gives users flexibility in terms of bandwidth and
latency/indirection, all the way from a simple linked list to a fully replicated
log. The latter is useful for things like backups on durable storage.

### Next page semantics

The pointer to the 'next page' is another remote log entry, at a previous point
in time.

<!-- TODO: Determine requirement re overlapping, adjacent, 
and/or missing entries -->

<!-- TODO: Document message ordering append only requirements -->

### Interaction with MVDS

[vac.mvds.Message](../2/mvds.md/#payloads) payloads are the only payloads
that MUST be uploaded.
Other messages types MAY be uploaded, depending on the implementation.

## Acknowledgments

TBD.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## Footnotes

[^1]:  <https://github.com/vacp2p/research/tree/master/remote_log>
