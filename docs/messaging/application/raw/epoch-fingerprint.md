# Epoch Fingerprint

| Field | Value |
| --- | --- |
| Name | Epoch Fingerprint for MLS |
| Status | raw |
| Type | RFC |
| Category | Standards Track |
| Tags |  |
| Editor | jazzz <jazz@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

An Epoch Fingerprint is a short public identifier used to identify an MLS epoch state. Group members can compare fingerprints to confirm they are referring to the same epoch/commit, rather than assuming commits are well-ordered.

## Terminology

The key words MUST, MUST NOT and SHOULD are to be interpreted as described in RFC 2119.

## Background

MLS identifies epochs by a counter, which assumes all members applied the same commit. If members apply different commits, they reach the same epoch number with different group state (a fork). Comparing epoch numbers can't detect this, so members need a canonical way to compare epoch state.

`epoch_authenticator` (RFC 9420 §8.7) is a secret derived from the epoch state that allows members to validate that they share the same view of the group-state. Using this as a fingerprint alone would give a deterministic canonical value, but limits where and how it can be used as it is a secret. Having a value which can appear in cleartext is desirable to minimize security impacts from logs, debug output and UIs.

## Definition

```
fingerprint = lower_hex( SHA-256( DOMAIN || epoch_authenticator )[:7] )
```

| Term                  | Value                                                    |
|-----------------------|----------------------------------------------------------|
| `DOMAIN`              | ASCII `epoch-fingerprint-v1` followed by one `0x00` byte (21 bytes) |
| `epoch_authenticator` | The epoch's `epoch_authenticator` (RFC 9420, §8.7), as raw bytes |
| `[:7]`                | The first 7 bytes of the digest                          |
| `lower_hex`           | Lowercase hexadecimal, no prefix or separators           |

The result is always 14 characters long.

## Requirements

- Implementations MUST use SHA-256, regardless of the group's cipher suite.
- Implementations MUST compare fingerprints as exact strings.
- A fingerprint mismatch means the two members are in different epochs, or in different forks of the same epoch.
- A fingerprint match MUST NOT be relied on to authenticate epoch state against a malicious member (see Security).

## Security

- **Disclosure.** Publishing a fingerprint does not reveal `epoch_authenticator` or any other group secret.
- **Accidental collisions.** The fingerprint has 56 bits. Two unrelated epochs share a fingerprint with probability 2⁻⁵⁶, which is negligible for detecting inconsistencies.
- **Adversarial collisions.** A malicious member who can create commits can search about 2²⁸ candidate commits to find two forks with matching fingerprints. The fingerprint detects faults; it does not authenticate. Use the full `epoch_authenticator` where authentication is required.
- **Versioning.** Any change to this construction MUST use a new `DOMAIN`.

## Test Vectors

`DOMAIN` (hex): `65706f63682d66696e6765727072696e742d763100`

| `epoch_authenticator` (hex)                                         | Fingerprint      |
|---------------------------------------------------------------------|------------------|
| `0000000000000000000000000000000000000000000000000000000000000000` | `a9d71953d26500` |
| `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f` | `0aab9ca29e3711` |
| `ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff` | `35697b5a569500` |
