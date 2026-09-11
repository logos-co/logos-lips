# MESSAGE-SEGMENTATION-AND-RECONSTRUCTION

| Field | Value |
| --- | --- |
| Name | Message Segmentation and Reconstruction |
| Slug | 243 |
| Version | 0.1 |
| Status | raw |
| Type | RFC |
| Category | application |
| Tags | segmentation |

## Abstract

This specification defines an application-layer protocol for **segmentation** and **reconstruction**
of messages carried over a transport/delivery service with a message-size limitation,
when the original payload exceeds said limitation.
Applications partition the payload into multiple transport messages and reconstruct the original on receipt,
even when segments arrive out of order.
Optional Reed–Solomon erasure coding additionally tolerates the loss
of up to a predefined percentage of segments.

## Motivation

Many message transport and delivery protocols impose a maximum message size
that restricts the size of application payloads.
For example, Logos Delivery propagates messages up to 150 KiB
as per [64/WAKU2-NETWORK - Message](../../core/draft/64/network.md#message-size).
To support larger application payloads, a segmentation layer is required.
This specification enables larger messages by partitioning them into multiple envelopes
and reconstructing them at the receiver.
Erasure-coded parity segments provide resilience against partial loss or reordering.

## Terminology

- **original payload**: the full application payload before segmentation.
- **data segment**: one chunk of the original payload.
- **parity segment**: an erasure-coded segment derived from the set of data segments.
- **segment type**: either data or parity.
- **segment message**: a [`SegmentMessage`](#wire-format) carrying either data or parity segment.
- **segmentSizeBytes**: maximum size of a serialized segment message, see [Configuration](#configuration).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Wire Format

Each segment message is encoded as:

```protobuf
syntax = "proto3";

message SegmentMessage {
  bytes           original_payload_hash   = 1;  // Keccak256 of the original payload, 32 bytes
  uint32          original_payload_length = 2;  // length in bytes of the original payload
  uint32          index                   = 3;  // zero-based position among the segments of its type (data or parity)
  uint32          data_segment_count      = 4;  // number of data segments
  optional uint32 parity_segment_count    = 5;  // number of parity segments, unset if no parity
  bool            is_parity               = 6;  // false for a data segment, true for a parity one
  bytes           payload                 = 7;  // this segment's data chunk or parity shard
}
```

### Validity

A **segment message** is valid only if all of the following hold:
- `original_payload_hash` is exactly 32 bytes.
- `data_segment_count >= 1`.
- `data_segment_count + parity_segment_count <= maxTotalSegments`, the receiver's configured limit,
  counting an unset `parity_segment_count` as zero.
- `index < data_segment_count` on a data segment, `index < parity_segment_count` on a parity one.

An invalid segment message MUST be discarded.
A payload that fits one segment is still wrapped, as `data_segment_count == 1`, `index == 0`, `is_parity == false`.

## Reed–Solomon Coding

A sender that uses parity applies [Reed–Solomon erasure coding](https://github.com/catid/leopard)
over its data segments to produce `ceil(parityRate * data_segment_count)` more parity segments.
Reed–Solomon recovers from any `data_segment_count` segments of a set, data and parity alike,
so a set reconstructs even where every segment held is a parity one.
Implementations cap parity at the data-segment count, which `parityRate` respects.

Reed–Solomon operates on equal-length inputs, called shards, of the chunk size the payload was split into.
Only the last data segment may be shorter, and the encoder zero-pads it.
That padding never reaches the wire, data segments being sent at their true length,
which leaves parity segments as the only ones always exactly shard-length.
A decoding receiver therefore takes the shard length from a parity segment,
re-pads any data segments it holds to that length, and decodes.

Receivers SHOULD support Reed–Solomon decoding, and MUST where the application sets `parityRate > 0`;
without it a set reconstructs only once every data segment has arrived.

## Segmentation

To transmit an original payload, the sender:

- MUST compute `original_payload_hash = Keccak256(original payload)`.
- MUST split the payload into one or more data segments, at a chunk size such that every segment
  it sends, data and parity alike, serializes to at most `segmentSizeBytes`.
- MAY generate parity segments at `parityRate` as defined in [Reed–Solomon Coding](#reedsolomon-coding).
- MUST encode every segment as a `SegmentMessage` that satisfies [Validity](#validity).
- MUST send each segment message as an individual transport message; the order is unconstrained.

## Reconstruction

A receiver retains every valid segment message.

Two valid segment messages belong to the same **segment set** only if all of the following hold:
- they carry equal `original_payload_hash`.
- they carry equal `original_payload_length`.
- they carry equal `data_segment_count` and equal `parity_segment_count`.

Within a set, `(is_parity, index)` MUST be unique;
a segment message repeating one already held MUST be ignored.

Every segment message of a set carries its `data_segment_count`:
- A set reaching that count in data segments alone
  reconstructs by [concatenation](#all-data-segments-are-received-successfully).
- A set reaching that count in data plus parity segments together
  reconstructs [through parity](#recovery-through-parity).
- Else, [expires](#expiry) after a configured timeout.

### All data segments are received successfully

The receiver produces the original payload following these steps:

1. Concatenate the data segments' `payload` fields in ascending `index` order,
   which yields exactly `original_payload_length` bytes;
   fewer mean the set is incomplete and MUST NOT be delivered to the application.
2. Verify that `Keccak256` of the result equals the set's `original_payload_hash`.

An invalid payload MUST be discarded; only a valid one is delivered to the application.
Any parity segments the set holds are unused, and the set MAY be released once the payload is delivered.

### Recovery through parity

Where a data segment is missing, parity segments stand in for it.
The receiver [Reed–Solomon decodes](#reedsolomon-coding) the missing data segments from the ones it holds,
concatenates as [above](#all-data-segments-are-received-successfully),
then truncates the result to `original_payload_length` before verifying the hash.

Decoding returns every data segment at the [shard length](#reedsolomon-coding),
so a recovered last data segment comes back carrying zero padding the sender never transmitted.
Truncating to `original_payload_length` removes it;
a receiver holding every data segment assembles exactly that many bytes and truncates nothing.

### Expiry

The receiver MUST NOT wait indefinitely for all the required segments to arrive.
It MUST drop a set that has received no further segments
within a reconstruction timeout without delivering anything to the application.

A later segment message of a dropped set starts a new one,
which reconstructs only if enough are retransmitted.

## Configuration

- `segmentSizeBytes`: chosen by the application so that a segment fits the transport's maximum message size.
- `parityRate`: parity segments as a fraction of the data segments,
  so `0.125` is one parity segment per eight data ones.
  MUST NOT exceed `1`, parity segments never outnumbering the data ones,
  see [Reed–Solomon Coding](#reedsolomon-coding).
  Defaults to `0`, which disables parity.
  `0.125` is RECOMMENDED where the [guidance below](#when-to-use-parity) favours parity.
- `reconstructionTimeoutSeconds`: how long a segment set may go without a new segment message
  before the receiver drops it, see [Expiry](#expiry).
- `maxTotalSegments`: greatest number of segments a set may hold, data and parity together.
  Bounds how much memory one sender can make a receiver buffer, see [Segment Caching](#segment-caching).
  **256** is RECOMMENDED, the shard ceiling of the smaller field a Reed–Solomon implementation may use,
  so that any implementation can encode a conforming set.
  An application MAY raise it where its receivers can absorb the larger buffer
  and its Reed–Solomon implementation has the shards for it.
  All participants in an application MUST use the same value,
  so participants interoperate within an application and not across applications.

## Implementation Suggestions

### When to Use Parity

Parity costs `parityRate` extra bandwidth on every message, whether or not anything is lost,
and pays off only where losses are independent and a retransmission would cost more;
[RFC 3453](https://www.rfc-editor.org/rfc/rfc3453) covers the general trade-off.
Where an end-to-end reliability layer already retransmits missing segments, set `parityRate = 0`.

`ceil` rounds small sets up sharply: at `parityRate = 0.125` two data segments still get one parity segment,
a 50% overhead to tolerate a single loss.

### Segment Caching

Received segments accumulate until their set is reconstructible. Implementations typically:

- Index the cache by `original_payload_hash`,
  and additionally by sender where the transport authenticates one.
  Authenticating the sender is out of scope of this specification.
- Bound both the number of segment sets held and the total buffered bytes,
  per sender as well as globally where a sender identity is available.
  Capping the sets bounds the bytes at that cap times `maxTotalSegments * segmentSizeBytes`.
- Evict the least recently updated set first,
  in addition to the `reconstructionTimeoutSeconds` expiry every receiver applies.

Segments can be persisted in a local storage, so that partial reconstructions survive application restarts.
In-memory buffering is sufficient otherwise.

## Security/Privacy Considerations

### Privacy

`original_payload_hash` links the segments of one payload to each other, but does not reveal the payload.
This specification does not enforce encryption, but applications SHOULD encrypt each serialized
`SegmentMessage` before transmission, which hides the hash and the segment counts from observers
and denies an attacker the hash it would need to [poison a set](#integrity).
Traffic analysis may still identify a segmented flow by its timing and volume.

### Integrity

This specification provides no sender authentication.
The `original_payload_hash` check on the reconstructed payload
detects accidental corruption and mismatched segments,
but an attacker able to inject transport messages can compute a consistent hash over a payload of their own.
Such an attacker can also deny reconstruction outright: injecting a segment message that occupies an
`(is_parity, index)` of a set already in flight makes the receiver ignore the genuine one, so the set fails
its hash check and never reconstructs until it [expires](#expiry).
Encrypting each segment message, as [Privacy](#privacy) recommends, keeps `original_payload_hash` out of an
observer's reach and so out of reach of this attack.
Applications requiring authenticity MUST obtain it from another layer.

### Denial of Service

A remote sender controls how much memory a receiver buffers, so implementations MUST bound it.
The limits and timeouts in [Segment Caching](#segment-caching) are the mitigation.
Rate limiting at the transport,
for example [17/WAKU2-RLN-RELAY](../../core/draft/17/rln-relay.md) in Logos Delivery,
additionally bounds how fast an attacker can create pending reconstructions.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

1. [64/WAKU2-NETWORK](../../core/draft/64/network.md#message-size)
2. [17/WAKU2-RLN-RELAY](../../core/draft/17/rln-relay.md)
3. [nim-leopard](https://github.com/status-im/nim-leopard) – Nim bindings for Leopard-RS
4. [Leopard-RS](https://github.com/catid/leopard) – Fast Reed–Solomon erasure coding library
5. [RFC 3453](https://www.rfc-editor.org/rfc/rfc3453) – The Use of Forward Error Correction (FEC) in Reliable Multicast
6. [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) – Key words for use in RFCs to Indicate Requirement Levels
