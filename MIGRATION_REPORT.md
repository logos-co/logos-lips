# Migration Report: `logos-messaging/specs` → `logos-co/logos-lips`

Migration of [`logos-messaging/specs`](https://github.com/logos-messaging/specs)
into `logos-co/logos-lips` under `docs/messaging/`.

Each source file falls into one of three buckets:

- **NEW**: nothing similar exists in the destination, so it is migrated as a new
  raw RFC.
- **SUCCESSOR**: a newer version of an already-numbered spec; the historical
  numbered version stays in place.
- **SKIPPED**: the destination already holds a more developed or more recent
  version, so nothing is written.

Migrated files have their YAML frontmatter rewritten as a COSS pipe-table.
Status starts at `raw`, type at `RFC`.

## NEW (18 specs)

### `standards/core/`

- `incentivization.md` → `docs/messaging/standards/core/incentivization.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/incentivization.md))
- `relay-sharding.md` → `docs/messaging/standards/core/relay-sharding.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/relay-sharding.md))
- `rendezvous.md` → `docs/messaging/standards/core/rendezvous.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/rendezvous.md))
- `rln-contract.md` → `docs/messaging/standards/core/rln-contract.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/rln-contract.md))
- `store-sync.md` → `docs/messaging/standards/core/store-sync.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/store-sync.md))
- `sync.md` → `docs/messaging/standards/core/sync.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/sync.md))

### `standards/application/`

- `OpChan.md` → `docs/messaging/standards/application/opchan.md` (lowercased to match dest convention)
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/OpChan.md))
- `dandelion.md` → `docs/messaging/standards/application/dandelion.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/dandelion.md))
- `device-pairing.md` → `docs/messaging/standards/application/device-pairing.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/device-pairing.md))
- `messaging-api.md` → `docs/messaging/standards/application/messaging-api.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/messaging-api.md))
- `noise.md` → `docs/messaging/standards/application/noise.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/noise.md))
- `noise-sessions.md` → `docs/messaging/standards/application/noise-sessions.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/noise-sessions.md))
- `p2p-reliability.md` → `docs/messaging/standards/application/p2p-reliability.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/p2p-reliability.md))
- `rln-keystore.md` → `docs/messaging/standards/application/rln-keystore.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/application/rln-keystore.md))

### `informational/`

- `adversarial-models.md` → `docs/messaging/informational/adversarial-models.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/informational/adversarial-models.md))
- `chat_cast.md` → `docs/messaging/informational/chat-cast.md` (underscore changed to hyphen)
  ([source](https://github.com/logos-messaging/specs/blob/master/informational/chat_cast.md))
- `chatdefs.md` → `docs/messaging/informational/chatdefs.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/informational/chatdefs.md))
- `relay-static-shard-alloc.md` → `docs/messaging/informational/relay-static-shard-alloc.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/informational/relay-static-shard-alloc.md))

## SUCCESSOR (1 spec)

- `standards/core/lightpush.md` (v3.0.0)
  → `docs/messaging/standards/core/lightpush.md`
  ([source](https://github.com/logos-messaging/specs/blob/master/standards/core/lightpush.md))

The historical v2.0.0-beta1 spec stays at `docs/messaging/standards/core/19/lightpush.md`
(slug 19, draft). The new spec links back to it as the previous version.

## SKIPPED (3 specs)

`standards/core/enr.md` — source's last content commit is 2025-06-19. The dest
copy at `docs/messaging/standards/core/31/enr.md` had a real content update on
2025-10-16 ("Move to Draft", #180), so dest is newer.

`standards/core/mix.md` — source is a 143-line skeleton (Abstract, Background,
Terminology, Theory/Semantics, Node Roles, ENR updates, Spam Protection,
Tradeoffs, Future Work). Dest at `docs/ift-ts/raw/mix.md` is a 1682-line spec
by the same editor with numbered sections covering Mixing Strategy and Packet
Format, Protocol Overview, Pluggable Components, Core Mix Protocol
Responsibilities, and a recent content commit ("changes to how per-hop proof is
added to sphinx packet", 2026-01-29).

`standards/application/tor-push.md` — source is 42 lines, last touched
2024-07-09. Dest at `docs/ift-ts/raw/gossipsub-tor-push.md` is the same protocol
under a renamed identifier (slug 105, same editor), 243 lines, with a full
Specification section (Wire Format, Receiving, Sending, Connection
Establishment, Epochs) and expanded Security analysis.

## Cross-reference fixes

Two migrated specs use relative paths that worked under the source's flat
layout but miss by one level under the destination's nested layout. Fixed:

- `docs/messaging/standards/application/dandelion.md` — 5 refs going to
  `../../informational/adversarial-models.md` corrected to `../../../informational/...`
- `docs/messaging/standards/core/relay-sharding.md` — 3 refs going to
  `../../informational/{adversarial-models,relay-static-shard-alloc}.md`
  corrected to `../../../informational/...`

Some other relative cross-refs were already broken in the source repo
(e.g. `../../../11/relay.md`); those are left for the spec authors.

## Body link rewrites

Body links in migrated files now point to `logos-co/logos-lips`:

- `vacp2p/rfc-index/blob/main/waku/...` → `/blob/master/docs/messaging/...`
- `vacp2p/rfc-index/tree/main/waku/...` → `/tree/master/docs/messaging/...`
- `vacp2p/rfc-index/blob/main/vac/...` → `/blob/master/docs/ift-ts/raw/...`
- Pinned-hash URLs got the repo host renamed only; the historical paths still
  resolve via GitHub's repo-rename redirect.
- `waku-org/specs/blob/<ref>/<path>` and `logos-messaging/specs/blob/<ref>/<path>`
  now point to the corresponding path under `docs/messaging/`.
- `rfc.vac.dev/waku/<path>` rewritten to the matching `docs/messaging/<path>.md`
  GitHub link (per review feedback — no link to specs repos should remain).

## Assets

Three images copied from `images/` to `docs/messaging/images/`:

- `N11M.png`
- `NM.png`
- `protocol.svg`

## Not migrated

- `README.md`: the destination already has its own index under `docs/messaging/`.
- `template.md`: `docs/ift-ts/template.md` already covers this.
- `LICENSE`, `.spellcheck.yml`, `.wordlist.txt`, `.github/workflows/`: repo
  infrastructure, not spec content.

## Notes for reviewers

- Everything lands at `Status: raw`. Slugs get assigned when a spec is
  promoted to `draft` (the metadata validator does that automatically).
- Five specs in this PR have not been touched in the source repo for over a
  year and could use a freshness pass from their owners before further work:
  `noise.md`, `noise-sessions.md`, `dandelion.md`, `adversarial-models.md`,
  `relay-static-shard-alloc.md`.
- mdbook timeline blocks will be added to the new files in the next mdbook
  chore pass; nothing to do for this PR.
- After merge, `logos-messaging/specs` should be archived with a pointer back
  to this commit. That is a separate task.

## Verification

- `scripts/validate_metadata.py --check` → `[OK] metadata validation passed`
- No matches for `vacp2p/rfc-index`, `waku-org/specs`, `logos-messaging/specs`,
  or `rfc.vac.dev` in the 19 migrated files.
- Pre-existing (non-migrated) files in `docs/messaging/` still contain such
  references; those are handled in a separate follow-up PR.
