# Logos LIP (Logos Improvement Proposals) Index

NOTE: This repo is still evolving while the LIP process is refined.

This repository contains specifications from the Messaging, Blockchain, Storage,
and AnonComms components of the IFT portfolio. LIPs are Requests for Comments that
document protocols, processes, and system interfaces in a consistent, reviewable
format.

## LIP process

This repository replaces the old rfc.vac.dev resource. Specs are maintained in
Markdown here and progress through statuses such as raw, draft, stable, or
deprecated. The process and lifecycle are defined in:

- 1/COSS: `docs/research/draft/1/coss.md`

## Contributing

1. Open a pull request against this repo.
2. Add or update the LIP in the appropriate component folder.
3. Include status and category metadata in the header table.

If you are unsure where a document belongs, open an issue first and we will
help route it.

## Component indexes

- Messaging: `docs/messaging/README.md`
- Blockchain: `docs/blockchain/README.md`
- Storage: `docs/storage/README.md`
- AnonComms: `docs/anoncomms/README.md`
- Research: `docs/research/README.md`

## Local setup

1. Install mdBook (pick the version that matches your Rust toolchain).
2. Install Python dependencies if needed.

To install mdBook via Make:

```bash
make install
```

## Build and serve

Run the generators before building or serving:

```bash
python scripts/run_runtime_generators.py
mdbook build
```

To serve locally:

```bash
make serve
```

Or run the commands directly:

```bash
python scripts/run_runtime_generators.py
mdbook serve -p 3000 -n 0.0.0.0
```

## CI/CD

- [CI builds](https://ci.infra.status.im/job/website/job/lip.logos.co/) `master` and pushes to `deploy-master` branch, which is hosted at <https://lip.logos.co/>.
- [CI builds](https://ci.infra.status.im/job/website/job/dev-lip.logos.co/) `develop` and pushes to `deploy-develop` branch, which is hosted at <https://dev-lip.logos.co.dev/>.

The hosting is done using [Caddy server with Git plugin for handling GitHub webhooks](https://github.com/status-im/infra-sites/blob/b930491f44b4958957b998d20ca222b1e10c4d67/ansible/vars/sites/caddy_git.yml#L123-L149).

Information about deployed build can be also found in `/build.json` available on the website.
