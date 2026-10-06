# [RFC] Cryptoeconomics: Define the LEPTON as the indivisible token unit

> **Based on [#430](https://github.com/logos-co/logos-lips/pull/430).**
The diff shows only what this change adds. #430 rewrites the block rewards, and this change fixes the unit those rewards are counted in. The base retargets to `master` once #430 merges.

**Full RFC:** [`docs/blockchain/raw/rfc/RFC-NNN-cryptoeconomics-define-the-lepton-as-the-indivisible-token-unit.md`](https://github.com/logos-co/logos-lips/blob/logos-precision-units/docs/blockchain/raw/rfc/RFC-NNN-cryptoeconomics-define-the-lepton-as-the-indivisible-token-unit.md)

# Motivation

The ledger holds integers only. `Note.value` is a `uint64`, but no specification says what one integer counts. [Block Rewards](https://github.com/logos-co/logos-lips/blob/logos-precision-units/docs/blockchain/raw/block-rewards.md) assumed $10^{18}$ base units per token. At the hard cap of $10^{10}$ LOGOS that is $10^{28}$ units, and a `uint64` holds at most $2^{64}-1 \approx 1.8 \cdot 10^{19}$.

The unit also sets the price floor of both gas markets, because each price is an integer of at least one unit per gas unit. A unit that is too coarse prices permanent storage above its target cost. The specifications also name the token two ways, LGO and LOGOS.

# Proposal

The indivisible unit is the LEPTON, plural LEPTA, and $1 \text{ LOGOS} = 10^{9} \text{ LEPTA}$. [Overview Cryptoeconomics](https://github.com/logos-co/logos-lips/blob/logos-precision-units/docs/blockchain/raw/overview-cryptoeconomics.md#token-units-and-precision) specifies the unit, and a new analysis derives it.

- **Precision.** The hard cap bounds the precision exponent from above at 9. The gas price floor bounds it from below. Nine is admissible whenever any value is.
- **Denominations.** Kilolepton and megalepton are display aliases. `GLEPTON` is invalid, because it would name the LOGOS twice.
- **Encoding and rounding.** Every amount is an unsigned integer count of LEPTA. A fractional digit beyond the ninth is rejected, not rounded.
- **Block Rewards.** The integer rule rescales its constants from $10^{18}$ to $10^{9}$.
- **Naming.** Every amount in the touched specifications names LOGOS or LEPTA, replacing LGO.

## Status tracker

- [ ]  🚧 **Raw (make sure that all below is completed)**
    -  Template applied
    -  RFC document added under the domain's `raw/rfc/`, numbered by this PR
    -  Authors filled in
    -  Authors agree on the RFC content
- [ ]  📘 **Draft (make sure that all below is completed)**
    -  All dependent specifications added (Notion backlinks checked)
    -  Specifications to deprecate added, if applicable
    -  Specifications to retire added, if applicable
    -  **Leads assigned** — Research Lead and Engineering Lead. Where the Research Lead is an author, the Project Lead stands in
- [ ]  ⚙️ **Verified (make sure that all below is completed)**
    -  **Domain experts assigned** — research and engineering, as the change requires; cannot be authors
    -  Reviewers' comments addressed
    -  All logical changes documented
    -  **Required approvals collected on the latest revision**
- [ ]  🔀 **Merged (make sure that all below is completed)**
    -  Every change added to the change log, and the change log's order checked
    -  Specification version numbers assigned
    -  Implementation reviewed and merged
    -  Branch updated to master and all conflicts resolved
    -  PR merged
