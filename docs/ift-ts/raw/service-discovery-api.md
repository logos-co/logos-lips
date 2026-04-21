# SERVICE-DISCOVERY-API

| Field | Value |
| --- | --- |
| Name | Service Discovery API |
| Slug | 145  |
| Status | raw |
| Category | Standards Track |
| Editor | Simon-Pierre Vivier <simvivier@status.im> |
| Contributors | Hanno Cornelius <hanno@status.im>|

## Abstract

TODO

## Motivation

TODO

## Semantic

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## API Specification

The aim is to define an API that is compatible with most discovery protocols
that supports service-specific discovery,
maintaining similar function signatures even if the underlying protocol differs.

The API is defined in the form of C-style bindings.
However, this simply serves to illustrate the exposed functions
and can be adapted into the conventions of any strongly typed language.
Although unspecified in the API below,
all functions SHOULD return an error result type appropriate to the implementation language.

### Type Definitions

```

typedef struct {
    const uint8_t* bytes;
    size_t   len;
} Advertisement;

typedef struct {
    const Advertisement* ads;
    size_t                  len;
} AdvertisementList;

```

### `start()`

Start the discovery protocol,
including all tasks related to bootstrapping and maintenance
of the underlying discovery protocol (such as initialising the routing table).

### `stop()`

Stop the discovery protocol,
including all tasks related to maintenance
of the underlying discovery protocol (such as advertising or discovery loops).

### `start_advertising(const char* service_id, const Advertisement* advertisement)`

Start advertising the encoded `advertisement`
against any service encoded as a `service_id` string.
For peer discovery,
the node MUST encode sufficient connection information in the `Advertisement`
for discoverers to connect to it.

### `stop_advertising(const char* service_id)`

Stop advertising this node against the service
encoded in the input `service_id` string.

### `start_discovering(const char* service_id)`

Start discovering and maintaining search tables
for the service encoded in the input `service_id` string.

### `stop_discovering(const char* service_id)`

Stop discovering and maintenance of search tables
for the service encoded in the input `service_id` string.

### `AdvertisementList lookup(const char* service_id)`

Lookup and return advertisements for peers supporting
the service encoded in the input `service_id` string,
using the underlying discovery protocol.

It is RECOMMENDED to use `start_discovering`
in advance of any `lookup` for each `service_id`
as a way to speed up search.

### `AdvertisementList lookup_random()`

Unused, reserved for future use.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [logos service discovery](https://github.com/logos-co/logos-lips/blob/155c310d7bfad6ea3cd9f68e45c68dad731ff629/docs/ift-ts/raw/logos-service-discovery.md)