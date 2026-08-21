# MEMPOOL

| Field | Value |
| --- | --- |
| Name | Mempool |
| Slug | 245 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@logos.co> |
| Contributors |  |

# Revision History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-08-21 |

# Introduction

The **mempool** is the node-local store of Mantle Transactions that have been submitted to the network but are not yet part of the canonical chain, together with the gossip protocol that disseminates them. Every Logos Blockchain node runs one.

The mempool is not merely a staging buffer for a block builder. Because a Bedrock block proposal carries *references* to transactions rather than the transactions themselves — a 16-byte prefix of each transaction hash, as defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#references) — the mempool is also the store against which a validator resolves those references. A validator that cannot resolve a reference cannot reconstruct the block, and must reject the proposal, though only as a statement about the copy it received (see [Failure to Resolve Is Not a Verdict](#failure-to-resolve-is-not-a-verdict)). The mempool therefore sits on the consensus critical path: the degree to which node mempools agree bounds the rate at which proposals are accepted.

This document specifies the contents of the mempool, the rules by which transactions enter and leave it, the way it is disseminated, and the interfaces it exposes to block construction and to proposal reconstruction.

# Overview

The mempool serves five distinct purposes, and its design is a consequence of all five.

1. **Dissemination.** A transaction submitted to any node must reach every other node's mempool. This is what makes reference-based proposals viable, and it is achieved by gossiping transactions over a dedicated pubsub topic — the **push** half of dissemination.
2. **Confirmation.** A node must be able to tell whether a transaction it holds actually reached the network, rather than assume it. This is the **pull** half: the node asks randomly sampled, stake-backed members of the network whether they hold the transaction, and collects their signed answers as attestations.
3. **Block building.** A leader draws the transactions for its proposal from its local mempool — only confirmed ones — subject to the block limits defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md).
4. **Reference resolution.** A validator receiving a proposal resolves each reference prefix against its local mempool to recover the transaction body and reconstruct the block. Resolution must be a deterministic function of the proposal and the mempool alone, so that two validators holding the same transactions decide alike.
5. **Reorganisation resilience.** Transactions that leave the canonical chain during a fork switch return to the mempool so they can be included again.

Two protocol-level properties frame the design:

- **Transaction maturity.** [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#block-proposal-reconstruction) assumes that a transaction referenced by a proposal has had time to spread to every node. The delay the Blend network imposes on the proposal carries most of that assumption: by the time a proposal is delivered, the transactions it names have been gossiping for far longer. Confirmation turns the remainder of the assumption into evidence — a leader does not merely hope that a transaction has spread, it holds signed statements from `PULL_CONFIRMATIONS` independent providers that it has.
- **View uniformity.** [Blend Protocol](blend-protocol.md#privacy-of-proof-of-stake-systems) identifies the mempool as the surface for a *tagging attack*: an adversary that submits a transaction to exactly one node, and then observes which proposal first carries it, learns that the proposer was that node. Blend calls for the mitigation directly — a mempool in which "the node has an attestation that the transaction was seen by the majority of the network". [Confirmation: Pull](#confirmation-pull) is that attestation. Beyond it, every mechanism that makes one node's mempool differ from its peers' — selective delivery, divergent admission rules, divergent eviction — widens the same side channel, which is why admission is stateless and resolution reads nothing but the mempool.

## Lifecycle

```text
  submit (node API)                gossip (mempool topic)             reorg re-insertion
          |                                  |                                  |
          +----------------+-----------------+----------------------------------+
                           |
                    +------v-------+
                    |  admission   |  decode -> stateless validation -> size -> duplicate
                    +------+-------+
                           |
                           +--------> push: relay to mesh neighbours
                           |
                    +------v-------+
                    |   pending    |------> reference resolution
                    |  unconfirmed |        (proposal reconstruction)
                    +------+-------+
                           |
                           |  pull: after PULL_DELAY, query sampled providers,
                           |        collect PULL_CONFIRMATIONS attestations
                           |
                    +------v-------+
                    |   pending    |<--------------------------------+
                    |   confirmed  |------> reference resolution     |
                    +------+-------+                                 |
                           |                                         |
           block building  |  (confirmed only)                       |
                           |                                         |
                    +------v-------+                                 |
                    |   retirement |  included in a canonical block, |
                    |              |  inapplicable, or expired       |
                    +--------------+---------------------------------+
                                      (reorg returns transactions)
```

Reference resolution reads both states: confirmation gates what this node *proposes*, never what it can *reconstruct*.

# Protocol

## Constants

| Constant | Name | Description | Value |
| --- | --- | --- | --- |
| `MEMPOOL_TOPIC` | Mempool Topic | The gossipsub topic on which transactions are disseminated, as defined in [P2P Network](../draft/p2p-network.md#gossiping). | `/logos-blockchain/mempool/{version}` for mainnet, `/logos-blockchain-testnet/mempool/{version}` for testnet |
| `MAX_TRANSACTION_SIZE` | Maximum Transaction Size | The largest encoded signed transaction the mempool admits. Equal to `MAX_BLOCK_SIZE`, since a larger transaction could never be included in a block. | 2 MiB (2,097,152 bytes) |
| `TRANSACTION_TTL` | Transaction Time To Live | How long a transaction may remain pending before it is evicted. | 24 hours |
| `RETIREMENT_GRACE_PERIOD` | Retirement Grace Period | How long the body of a retired transaction is kept in the shared transaction store before being discarded. | 10 minutes |
| `REFERENCE_PREFIX_LENGTH` | Reference Prefix Length | The number of leading transaction-hash bytes a proposal reference carries, as defined in [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md#references). This is the key on which the mempool answers reference lookups. | 16 bytes |
| `MAX_BLOCK_TXS` | Maximum Block Transactions | The largest number of transactions a block may carry, and therefore the largest number of references a proposal may bear, as defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants). | 1024 |
| `MAX_BLOCK_SIZE` | Maximum Block Size | The largest total size of a block's transactions, as defined in [Cryptarchia Protocol](cryptarchia-v1-protocol.md#constants). | 2 MiB (2,097,152 bytes) |
| `PULL_PROTOCOL` | Pull Protocol | The libp2p request-response protocol on which confirmation queries are exchanged. | `/logos-blockchain/mempool-pull/{version}` for mainnet, `/logos-blockchain-testnet/mempool-pull/{version}` for testnet |
| `PULL_DELAY` | Pull Delay | How long after admission a transaction must age before it is asked about, so that a negative answer means "has not arrived" rather than "has not arrived yet". | 10 seconds (to be calibrated) |
| `PULL_INTERVAL` | Pull Interval | How often a node runs a confirmation round. | 2 seconds |
| `PULL_SAMPLE_SIZE` | Pull Sample Size | How many providers a node queries in one confirmation round. | 32 |
| `PULL_MAX_BATCH` | Pull Batch Size | The most transactions one query may ask about. | 1024 |
| `PULL_MAX_ROUNDS` | Maximum Pull Rounds | How many rounds a node spends on one transaction before it stops asking. | 8 |
| `PULL_CONFIRMATIONS` | Confirmation Threshold | How many distinct providers must attest to a transaction before it is confirmed. | 134 |

`PULL_SAMPLE_SIZE`, `PULL_MAX_ROUNDS` and `PULL_CONFIRMATIONS` are one calibrated triple and must be changed together — see [Sampling and the Threshold](#sampling-and-the-threshold). In particular the product `PULL_SAMPLE_SIZE * PULL_MAX_ROUNDS` is a security parameter rather than a budget: raising it while holding the threshold fixed makes the protocol *less* safe, not more.

## Mempool State

A node's mempool consists of:

```python
class Mempool:
    pending: OrderedSet[TxHash]         # admitted, not yet retired, in admission order
    bodies: Map[TxHash, SignedMantleTx] # transaction bodies, durably stored
    admitted_at: Map[TxHash, Timestamp] # admission time, per pending transaction
    retired_at: Map[TxHash, Timestamp]  # retirement time, per recently retired transaction
    by_prefix: Map[bytes, Set[TxHash]]  # pending hashes, keyed by reference prefix
    commitment: Map[TxHash, Hash]       # body commitment, computed once at admission
    attesters: Map[TxHash, Set[ProviderId]]  # providers that have attested to holding it
    queried: Map[TxHash, Set[ProviderId]]    # providers ever queried about it, answered or not
    received_from: Map[TxHash, Set[PeerId]]  # peers this transaction arrived from
    rounds: Map[TxHash, uint8]          # confirmation rounds spent so far
```

A node additionally keeps a table of its **outstanding queries** — the fresh `nonce` of each query in flight and the provider and transactions it named. This table is deliberately ephemeral session state, not part of `Mempool`: a restart voids it, and a response whose `nonce` matches no outstanding query is discarded, so attestations can never be smuggled in across a restart under a nonce the node no longer remembers issuing.

- `pending` is the set the node considers available for block building and for reference resolution. It is **ordered by admission time**; the order is what block building consumes and what makes the FIFO discipline of [Block Building View](#block-building-view) well defined.
- `bodies` outlives `pending`. A transaction that has been retired keeps its body for `RETIREMENT_GRACE_PERIOD`. The store holding it is shared with the chain — a transaction that a block has just taken into the chain is the same stored object the mempool admitted — so retirement must not delete the body out from under a block that has just been applied, and a transaction re-admitted within the window needs no second write.
- `retired_at` is the record that drives that grace period. It is **not** a rejection list: a retired hash that is gossiped again is admitted again (see [Retirement](#retirement)).
- `commitment`, `attesters`, `queried`, `received_from` and `rounds` are the state of [Confirmation: Pull](#confirmation-pull). A transaction is **confirmed** when `len(attesters[key]) >= PULL_CONFIRMATIONS`. `queried` is a superset of `attesters` — it also records providers that answered negatively, declined or timed out — and is what makes the without-replacement sampling of [Sampling and the Threshold](#sampling-and-the-threshold) well defined: a provider is asked about a transaction at most once, whatever it answered. `received_from` records the peers a transaction arrived from, for exclusion from sampling. All of these are local observations, not facts about the transaction, and none of them may enter a decision that has to agree across nodes.
- `by_prefix` indexes `pending` by `prefix(hash, REFERENCE_PREFIX_LENGTH)` — the key a proposal reference carries. It is a **derived** index, maintained alongside `pending` and rebuilt rather than persisted (see [Persistence and Recovery](#persistence-and-recovery)), so that a change to `REFERENCE_PREFIX_LENGTH` cannot be contradicted by a stale on-disk index. Each bucket holds a set, not a single hash: at `REFERENCE_PREFIX_LENGTH = 16` a bucket holding more than one transaction is infeasible to manufacture, but the mempool represents the case rather than assuming it away, because [Reference Resolution](#reference-resolution) must be able to tell a unique match from an ambiguous one.

A transaction is keyed by its Mantle transaction hash, `mantle_txhash(tx)`, as defined in [Mantle](bedrock-v1.1-mantle-specification.md#mantle-transaction-hash). The hash covers the unsigned transaction, so it is stable across the transports the transaction travels over.

## Transaction Admission

A transaction reaches the mempool from one of three sources:

- **Local submission**, through the node's transaction API.
- **Gossip**, over `MEMPOOL_TOPIC`.
- **Re-insertion**, when a chain reorganisation displaces a block whose transactions return to the pool.

All three go through the same admission procedure. Admission is deliberately **stateless**: it depends only on the transaction and on the current contents of the mempool, never on the ledger state. This is what keeps admission decisions identical across nodes that disagree about the tip, and therefore keeps mempool views converging rather than forking with the chain.

```python
def admit(mempool, encoded: bytes) -> Result:
    # 1. Decode.
    tx = decode_signed_mantle_tx(encoded)     # reject if malformed or trailing bytes remain

    # 2. Stateless validation.
    preverify(tx)                             # reject on failure

    # 3. Size.
    if len(encoded) > MAX_TRANSACTION_SIZE:
        return Reject(TransactionTooLarge)

    # 4. Duplicate.
    key = mantle_txhash(tx)
    if key in mempool.pending:
        return Reject(AlreadyPending)

    # 5. Admit.
    mempool.bodies[key] = tx
    mempool.retired_at.pop(key, None)
    mempool.admitted_at[key] = now()
    mempool.pending.append(key)
    mempool.by_prefix[prefix(key, REFERENCE_PREFIX_LENGTH)].add(key)
    mempool.commitment[key] = H("LOGOS_MEMPOOL_BODY_V1" || encoded)
    return Accept
```

The body commitment is computed here, once, and cached: [Confirmation: Pull](#confirmation-pull) needs it to answer queries in constant time rather than re-hashing the transaction on demand.

### Decoding

The gossiped payload is the canonical encoding of the signed transaction defined in [Mantle Transaction Encoding](mantle-transaction-encoding.md), carried in the network envelope defined in [Network Wire Format](network-wire-format.md). A payload that fails to decode, or that decodes with trailing bytes left over, must be discarded. Requiring the whole payload to be consumed keeps the encoding injective on the wire: two byte strings that differ cannot decode to the same transaction and so cannot be used to inflate one transaction into several gossip messages.

### Stateless Validation

Before a transaction is admitted it must pass **stateless validation** — the subset of the [Mantle validation rules](bedrock-v1.1-mantle-specification.md#validation) that can be decided without reading ledger state:

1. The transaction carries exactly one proof entry per operation, where an entry may be the `None` proof for an opcode that admits one, as [Mantle validation](bedrock-v1.1-mantle-specification.md#validation) rule 1 defines.
2. Each proof entry is of the type its operation's opcode requires.
3. Each proof that is self-contained — a signature or proof bound only to the transaction hash and the operation payload — verifies.

What stateless validation deliberately does **not** cover is every rule that needs a ledger view: that the notes an operation consumes exist and are unspent, that the transaction's excess balance covers its mandatory fees, that it does not conflict with another pending transaction, and that the declared gas price clears the prevailing base fee. Those are decided when a block is built and when it is executed.

The consequence is explicit and intended: **a transaction in the mempool is well-formed, not valid**. A node must not treat mempool membership as evidence that a transaction can be applied. See [Open Issues](#open-issues) for what this costs.

### Size

A transaction whose received encoding is longer than `MAX_TRANSACTION_SIZE` is rejected. The measure is the length of the canonical encoding — the same bytes the payload carried and the body commitment is taken over — so every node measures the same number. The bound is the same as the maximum total size of a block's transactions, so the rule excludes exactly those transactions that no valid block could ever carry.

### Duplicate Suppression

A transaction whose hash is already pending is not admitted a second time. Duplicate suppression happens at two layers, and both are needed:

- At the **gossip layer**, the message identity of a `MEMPOOL_TOPIC` message is the Blake2b-256 digest of its payload bytes — not gossipsub's default source-and-sequence-number identity, which would let every re-publisher mint a fresh identity for the same bytes. A router that has seen an identity within its duplicate-cache window drops later copies before they reach the mempool at all.
- At the **mempool layer**, the `pending` check catches the same transaction arriving from a different source, arriving after the routers' caches have expired, or arriving on the local API while already gossiping.

A duplicate arriving by **gossip** is dropped silently. A duplicate arriving by **local submission** is answered as a success and the transaction is broadcast again. The two layers make that re-broadcast exactly the recovery it is meant to be: routers that saw the first broadcast recently suppress the copy, while routers that never saw it — the lost-broadcast case the resubmission exists for — forward it. Resubmitting is therefore harmless when the first broadcast succeeded and effective when it did not.

## Dissemination: Push

Transactions are disseminated by gossipsub over `MEMPOOL_TOPIC`, as specified in [P2P Network](../draft/p2p-network.md#gossiping). This is the **push** half of dissemination: a node relays every transaction it receives to its mesh neighbours, immediately and unconditionally.

- A transaction that a node **admits from local submission or re-insertion** is broadcast on `MEMPOOL_TOPIC` by the mempool itself.
- A transaction that a node **receives from gossip** is relayed by the pubsub router as part of delivering it. The mempool does not re-broadcast it: that would duplicate the router's work and produce a second message with the same content but a different origin.

Push is **immediate and precedes admission**. The router forwards a received message to the mesh before the mempool has decoded it, let alone validated it, so relay is not conditional on the transaction being well-formed. This is what makes propagation fast enough for [Confirmation: Pull](#confirmation-pull) to have something to observe, and it is deliberate — a node that withheld relay until it had validated would slow dissemination by one validation per hop, and would make its relay behaviour a function of its own state. It is also a cost: an invalid transaction is amplified network-wide before any node rejects it, which is recorded in [Open Issues](#open-issues).

Because message identity is the digest of the payload, and because the payload is the canonical transaction encoding, the same transaction submitted twice produces the same message identity — so it is suppressed by every router that has seen it within its duplicate-cache window, and costs a router nothing more than a cache hit otherwise (see [Duplicate Suppression](#duplicate-suppression)).

## Confirmation: Pull

Push spreads a transaction but tells the pushing node nothing about how far it got. A node that has only pushed cannot distinguish a transaction the whole network holds from one it alone was handed — and that distinction is exactly what the tagging attack of [Blend Protocol](blend-protocol.md#privacy-of-proof-of-stake-systems) exploits. **Pull** supplies the missing evidence: after allowing time for propagation, a node asks randomly chosen members of the network whether they hold the transaction, and treats signed positive answers as attestations that it has spread.

A transaction that has collected `PULL_CONFIRMATIONS` attestations from distinct providers is **confirmed**. Confirmation gates one thing only: whether this node will select the transaction when it builds a proposal. It is a local decision, not a consensus rule — see [Confirmation Gates Inclusion, Never Resolution](#confirmation-gates-inclusion-never-resolution).

### Who May Attest

The attester set is the set of [Service Declaration Protocol](bedrock-service-declaration-protocol.md) declarations that are **active in the current epoch's snapshot**. A declaration carries a `provider_id` — an `Ed25519PublicKey` that is also the node's libp2p identity — and a non-empty list of `locators`, so the set is simultaneously an eligibility list, a key list and an address book, and every node derives the same one from the same finalized chain state without any additional agreement.

Two properties follow, and both are why this set rather than any other:

- **Sybil resistance is the declaration's collateral.** Manufacturing an attester means making a declaration, which means locking the minimum stake. Attestations cannot be minted for free.
- **Attesting reveals no stake quantity.** Eligibility is per declaration, not per unit of stake, so every active provider attests with the same weight. A node's attestation behaviour is therefore not a stake-proportional observable, which is what allows attesters to sign in the clear.

The snapshot changes only at epoch boundaries and lags by up to two epochs, so the sampling set is stable and identical across nodes for the whole epoch.

[Service Declaration Protocol](bedrock-service-declaration-protocol.md) currently defines one service type, `BN`, so in practice the attester set is the declared Blend Network providers. Every Blend node is also a validator, so the set is a stake-backed subset of the nodes that run a mempool — which is all the sampling argument needs. What it does mean is that the adversarial fraction the threshold is calibrated against is the adversarial fraction *within the declared set*, not within the validator population at large, and that a service type covering validators directly would make the sample space wider without changing anything else here.

### The Pull Exchange

A **query** names the transactions the querier is asking about and a fresh challenge:

```python
class PullQuery:
    nonce: bytes32                  # fresh, unpredictable, chosen by the querier
    tx_hashes: list[TxHash]         # up to PULL_MAX_BATCH entries
```

A **response** answers each entry, proves possession of the ones answered positively, and is signed:

```python
class PullResponse:
    nonce: bytes32                  # copied from the query
    held: bitmap                    # one bit per queried hash, in query order
    witness: hash                   # proof of possession over the held entries
    provider_id: Ed25519PublicKey
    signature: Ed25519Signature
```

Where, writing `body_commitment(tx) = H("LOGOS_MEMPOOL_BODY_V1" || encode(signed_tx))` for the value each node computes once when it admits a transaction and caches thereafter:

```python
witness = H("LOGOS_MEMPOOL_PULL_WITNESS_V1"
            || nonce
            || uint16(count(held))
            || concat(body_commitment(tx) for tx in queried where held))

signature = Ed25519.sign(provider_sk,
                         H("LOGOS_MEMPOOL_PULL_RESPONSE_V1"
                           || nonce || held || witness))
```

The querier accepts a response as an attestation for a given transaction when all of the following hold:

1. `provider_id` is the provider that was queried, and was active in the snapshot the query sampled it from. Activity is judged at query time, never re-judged at acceptance: an honest response crossing an epoch boundary must not be voided by a snapshot change, for the reason given in [Persistence and Recovery](#persistence-and-recovery).
2. `nonce` matches an outstanding query, and no response to that query has already been accepted.
3. `signature` verifies under `provider_id`.
4. `witness` equals the value recomputed from the querier's own copies of the transactions the `held` bitmap marks.
5. The bit for that transaction is set.

Verification therefore costs one Ed25519 verification and one hash over `count(held)` 32-byte commitments, per response, however many transactions the response covers.

### Why the Witness

Without proof of possession a provider could answer "yes" to any hash at no cost, and confirmation would measure nothing. The witness binds the answer to the transaction body: `body_commitment` is taken over the full signed encoding, which no one can produce from `tx_hash` alone, since `mantle_txhash` covers the unsigned transaction and not the proofs.

What the witness does **not** do is stop a provider that genuinely holds the transaction from being adversarial. An adversary who authored a transaction holds its body and can answer any challenge about it truthfully. The witness excludes the uninformed liar; it is [random sampling](#sampling-and-the-threshold) that excludes the informed one.

The witness is computed over cached commitments rather than over the transaction bodies. Hashing the bodies would let a 32-byte query entry compel a hash over as much as `MAX_TRANSACTION_SIZE`, which is precisely the work asymmetry a query protocol must not have. The cost is a small weakening — a party holding only the commitment could answer without the body — which is acceptable because obtaining the commitment already requires having been given the body by someone who had it.

### Sampling and the Threshold

A round of confirmation proceeds as follows. Every `PULL_INTERVAL`, a node:

1. Collects its pending, unconfirmed transactions whose age is at least `PULL_DELAY`, up to `PULL_MAX_BATCH`. The delay is what makes a negative answer meaningful: asked too early, an honest provider truthfully says no simply because push has not arrived yet.
2. Samples `PULL_SAMPLE_SIZE` providers uniformly at random from the active snapshot, **excluding** itself, the providers in `queried` for these transactions — asked before, whatever they answered — and the peers in `received_from`: a node that handed you a transaction is a known holder, and its answer attests to nothing.
3. Sends each sampled provider a query with a fresh `nonce`.
4. Credits each transaction with the distinct providers whose responses attest to it.

A transaction reaching `PULL_CONFIRMATIONS` distinct attesting providers becomes confirmed. Confirmations accumulate across rounds; a provider counts once. A node stops asking about a transaction after `PULL_MAX_ROUNDS` rounds, after which the transaction stays pending, stays resolvable and stays gossiped — it is simply never selected by this node.

The sample must be drawn from local randomness and never from a chain-derived seed. A publicly computable sample would let an adversary know in advance which providers a given node will ask, and position itself to be all of them.

### Why the Threshold Is What It Is

One honest attestation is sufficient evidence. A provider that truthfully holds the transaction received it by push, and having received it, pushed it on — so a single honest "yes" means the transaction is already spreading through the honest network, and including it identifies nothing. The threshold exists to bound the probability that *every* attester was adversarial.

That bound is not the whole story, because the threshold is squeezed from both sides.

- **Security.** For a transaction delivered to one node alone, honest providers hold nothing and say so, so only adversarial providers can attest. The attack succeeds exactly when a run draws `PULL_CONFIRMATIONS` or more adversarial providers. A **higher** threshold is safer.
- **Liveness.** For a genuinely broadcast transaction, the run fails when fewer than `PULL_CONFIRMATIONS` of the providers it sampled attest. A **lower** threshold is safer.

The threshold must therefore sit strictly between the adversarial providers a run is likely to draw and the attesters it is likely to draw, and the width of that window — not the threshold alone — is what sets how many providers must be sampled. Two consequences follow that a $`f^{t}`$ estimate does not show:

- **The total sample is a security parameter, not a budget.** Querying more providers at a fixed threshold gives the adversary more draws from which to accumulate attestations, so it makes the attack *more* likely. `PULL_SAMPLE_SIZE`, `PULL_MAX_ROUNDS` and `PULL_CONFIRMATIONS` move as one.
- **Withholding sets the cost.** An adversary that refuses to attest cannot make a tagged transaction confirm, so withholding does not enter the security bound. It does remove the adversary's whole share of every sample from the attesting pool, which is what liveness is measured against — and that raises the required sample by roughly an order of magnitude. The constants here assume a withholding adversary, because an adversary that can censor by refusing to answer is not a weaker assumption than one that answers honestly.

Since sampling is without replacement from a finite declaration set, both counts are hypergeometric rather than binomial. The distinction is material at Bedrock's set sizes — the binomial approximation overstates the security tail here by roughly $`3\times`$ — and its direction means the exact model is what makes the calibrated sample genuinely minimal: a binomial calibration would have been safe but would have demanded a larger sample than the protocol needs. The constants above are the smallest configuration satisfying a security failure of at most $`10^{-9}`$ and a liveness failure of at most $`10^{-6}`$, at 5000 active declarations, $`f = 1/3`$, and an honest provider holding a broadcast transaction with probability $`0.99`$ when asked. They achieve $`4.4 \times 10^{-11}`$ and $`7.5 \times 10^{-7}`$ respectively.

The tolerance degrades sharply past the design point, which is a property of the mechanism rather than of the parameter choice — above $`f = 1/2`$ no threshold satisfies both bounds at any sample size:

| adversarial fraction | security failure | liveness failure |
| --- | --- | --- |
| 0.20 | $`1.9 \times 10^{-32}`$ | $`1.5 \times 10^{-23}`$ |
| 0.33 | $`4.4 \times 10^{-11}`$ | $`7.5 \times 10^{-7}`$ |
| 0.40 | $`2.8 \times 10^{-5}`$ | $`8.0 \times 10^{-3}`$ |

### Confirmation Latency

Confirmation is not instant, and the delay is charged to every transaction before it can be included. A transaction becomes eligible no earlier than `PULL_DELAY` after admission, and then needs enough rounds at `PULL_INTERVAL` to gather its attestations — at the constants above, typically around six rounds and at most eight. Submission to eligibility is therefore on the order of twenty to thirty seconds. This is the price of turning the transaction-maturity assumption into evidence, and it is paid in parallel by every node holding the transaction, so it does not compound.

### A Negative Answer Must Not Transfer the Transaction

A provider that does not hold a queried transaction answers that it does not, and the exchange ends. It must not request the transaction, and the querier must not offer it.

This rule is what keeps confirmation honest. If a query caused the transaction to be sent to the provider, then querying would propagate it, the provider would hold it, and a subsequent query would confirm it — the mechanism would confirm every transaction it asked about, including one that no one but the querier had ever seen. Confirmation must measure push, not cause it.

The consequence is that pull cannot double as a repair mechanism for a node missing a transaction. Repair, if it is wanted, has to be a separate exchange whose results never count toward confirmation.

### Confirmation Gates Inclusion, Never Resolution

Confirmation state is local: it depends on which providers this node happened to sample and what they happened to answer. It must therefore never enter any decision that has to be identical across nodes.

- **Block building** consults it. A leader selects only confirmed transactions ([Block Building View](#block-building-view)).
- **Reference resolution** does not. A reference resolves against `pending`, confirmed or not ([Reference Resolution](#reference-resolution)). A validator that rejected proposals over its own confirmation state would be rejecting them over a private observation, which would break the property that two validators holding the same mempool decide alike.

Block validity is unchanged by this section. A leader that includes an unconfirmed transaction produces a perfectly valid block; it has simply forfeited the protection, and risks a proposal that other nodes cannot reconstruct. Since the only party harmed by that choice is the leader making it, the rule needs no enforcement.

## Block Building View

A leader constructing a proposal requests the mempool's **view**: the bodies of every pending transaction, in admission order, each marked with whether it is confirmed.

The confirmation gate is the whole of the tagging-attack defence: **only a confirmed transaction may be selected into a proposal**. A transaction that has not collected `PULL_CONFIRMATIONS` attestations remains pending, remains gossiped and remains resolvable — it is withheld from selection only.

Confirmation gates *selection* and nothing else. In particular it must not leak into retirement: which transactions a node holds must not come to depend on which providers that node happened to sample, or nodes' mempools would diverge along exactly the axis the confirmation machinery is private on. Block building therefore makes two separate determinations, and only the first may remove anything from the pool:

**Applicability — decided over every pending transaction, confirmed or not.** The leader applies the header to its ledger state to obtain the state the block's transactions would execute against, then repeatedly passes over *all* pending transactions in admission order, applying each that succeeds to the working state, until a pass applies nothing new. Multiple passes resolve **intra-block dependencies**: a transaction spending a note created by another pending transaction only becomes applicable once its predecessor has been applied, and its position in admission order need not respect that. No block limit constrains this computation — it is a statement about the ledger, not about block room. Transactions that never became applicable at this fixpoint are invalid against this branch's state regardless of confirmation, and the leader retires them (see [Retirement](#retirement)).

**Selection — decided over the applicable, confirmed transactions only.** The leader then builds the block by the same multi-pass discipline restricted to confirmed transactions, stopping at the first transaction that would exceed `MAX_BLOCK_TXS` or `MAX_BLOCK_SIZE`. Transactions left out here are **not** retired, whatever the reason they were left out: the block was full, they are awaiting confirmation, or they depend on an unconfirmed predecessor that could not be included before them. All of those are transactions some other leader — or this one, later — can validly include, and evicting them would break this node's ability to resolve that leader's references to them.

Selection carries no obligation to avoid prefix collisions among the transactions it picks: at `REFERENCE_PREFIX_LENGTH = 16` no adversary can place two transactions sharing a prefix in a mempool to be selected together, so the leader may select on merit alone and the mempool need not offer a collision-aware view.

Ordering within the view is admission order. A node's mempool therefore behaves as first-come-first-served, and a transaction's fee has no bearing on when it is included. This diverges from the block builder algorithm in [Execution Market](execution-market.md#block-builder-mechanism-block-construction), which specifies filtering by base fee and ordering by revenue; see [Open Issues](#open-issues).

## Reference Resolution

A proposal carries references to transactions rather than the transactions themselves. Each reference is a `REFERENCE_PREFIX_LENGTH`-byte prefix of the transaction hash, as defined in [References](bedrock-v1.1-block-construction.md#references). The mempool is the store against which those prefixes are resolved:

```python
def resolve(mempool, reference) -> Optional[SignedMantleTx]:
    matches = mempool.by_prefix.get(reference, empty_set)
    if len(matches) != 1:
        return None                      # absent, or ambiguous — both unresolved
    return mempool.bodies[single(matches)]
```

A reference resolves **only when the match is unique**. Zero matches means the transaction has not reached this node. Two or more would mean a prefix collision, which at `REFERENCE_PREFIX_LENGTH = 16` is infeasible to manufacture and vanishingly unlikely to occur by chance; it is reported as unresolved rather than searched, so that resolution never branches and never depends on the order in which the mempool is scanned. This is why the mempool must expose *how many* transactions a prefix matches rather than simply returning one of them.

The validator then, as specified in [Block Proposal Reconstruction](bedrock-v1.1-block-construction.md#block-proposal-reconstruction):

1. Resolves every entry of `references`, in the order the entries appear. The same reference may appear more than once; each occurrence resolves independently to the same transaction, so the lookup is idempotent and the mempool draws no conclusion from repetition.
2. Rejects the proposal if any reference fails to resolve. This is unconditional: one unresolvable reference rejects the whole proposal, which is what confines the chain to transactions the network has actually seen.
3. Otherwise reconstructs the block from the proposal's header, its carried uncle headers, and the resolved transactions in reference order, and checks that the body root over them reproduces `header.body_root`. That check — taken over the **full** transaction hashes — is the backstop for the residual random collision: a set that resolved to the wrong transaction never reproduces the root.

Two properties of this procedure are the mempool's responsibility to preserve.

**Resolution must be deterministic in the mempool.** It is a function of the proposal and the node's mempool alone, so two validators holding the same mempool always reach the same decision. Nothing about the node's chain state, its peer set, or the order in which it received transactions may enter it. This is the same requirement that makes admission stateless (see [Why Admission Is Stateless](#why-admission-is-stateless)), applied at the read side.

**Resolution must not be reachable cheaply.** A mempool lookup is the expensive part of accepting a proposal, and a proposal's references are unauthenticated — `signature` covers the header alone. A node must therefore not touch the mempool until the proposal has been decoded within its declared bounds and its header has been authenticated: the `references` count must be checked against `MAX_BLOCK_TXS` at decode time, before any allocation proportional to it, and signature and proof-of-leadership verification must precede any lookup. [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation) fixes this order; the mempool interface must not offer a path around it.

Resolution is served by `pending` alone. A retired transaction keeps its body for `RETIREMENT_GRACE_PERIOD`, but it is dropped from `by_prefix` the moment it is retired and is therefore no longer a candidate. This has a consequence worth stating plainly: a node that has already included a transaction on its own branch can no longer resolve a reference to it in a proposal built on a competing branch, so a node's branch position does affect which proposals it can reconstruct. The effect is bounded — a fork switch re-admits the displaced transactions ([Reorganisation](#reorganisation)), and the rejection is local rather than a verdict on the block ([Failure to Resolve Is Not a Verdict](#failure-to-resolve-is-not-a-verdict)) — but closing it entirely would mean resolving against recently retired transactions as well; see [Open Issues](#open-issues).

## Failure to Resolve Is Not a Verdict

A reference that resolves to nothing means the transaction has not reached this node's mempool — a local condition, not a defect of the block. The validator rejects the proposal and does not build on it, but it **must not** record that outcome as a verdict on the block's identity: the same block may arrive later in full through chain synchronisation, carrying its transactions with it and needing no mempool at all, and is then judged on its merits. [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation) gives the full classification of which rejections condemn a block and which condemn only the received copy.

This is what keeps a mempool gap from becoming censorship. A node that has missed one transaction loses the ability to reconstruct one proposal; it does not lose the ability to ever accept the block that proposal named.

## Retirement

A transaction leaves `pending` — is **retired** — for one of three reasons.

### Inclusion in a Canonical Block

When a block is applied and becomes the node's tip, every transaction it carries is retired. When a block is applied but does **not** become the tip — it extends a branch the node is not following — its transactions stay pending, because a later fork switch may make this node the one that has to build on that branch.

### Reorganisation

When a fork switch displaces blocks from the canonical chain, the transactions those blocks carried are re-admitted through [Transaction Admission](#transaction-admission), including the broadcast that local admission performs. They are ordinary pending transactions again and may be included in a later block.

### Expiry

A pending transaction whose age exceeds `TRANSACTION_TTL` is retired. Expiry is what bounds the residency of a transaction that is never includable — one whose fee never clears, or whose inputs were spent by a competing transaction — without requiring the mempool to understand why it is not includable.

A node also retires the transactions that block building found inapplicable at the all-transactions fixpoint, as described in [Block Building View](#block-building-view) — never transactions merely left unselected there.

### Effects of Retirement

Retirement removes the hash from `pending` and from `by_prefix`, discards its `attesters` and `rounds`, and records it in `retired_at`. The body and its `commitment` are retained for `RETIREMENT_GRACE_PERIOD` and then discarded — the commitment outlives the pending state because a provider must be able to answer a query about a transaction it has just retired, and answering that it holds one it still has is truthful.

Dropping the hash from `by_prefix` is what stops a retired transaction from being offered as a second match for a prefix and turning a resolvable reference into an ambiguous one. Discarding its attestations means that a transaction returning by [Reorganisation](#reorganisation) must be confirmed again before this node will re-include it: the attestations it held were evidence about a propagation that has since been overtaken by a block, and re-confirming costs the ordinary confirmation latency of [Confirmation Latency](#confirmation-latency) — typically around six rounds — against a transaction the network already holds.

Retirement is **not** rejection. A retired hash carries no memory once its grace period lapses, and even during the grace period a re-gossiped copy is admitted again and clears the retirement record. A transaction that has already been included therefore can re-enter a node's mempool; it will be found inapplicable the next time that node builds a block, and retired again. This is a deliberate simplification — a permanent rejection set would have to be bounded and would itself become a divergence between nodes — but it has a cost, recorded in [Open Issues](#open-issues).

## Persistence and Recovery

The mempool survives a node restart. A node persists:

- the pending hashes together with their admission timestamps,
- the retirement records and their timestamps,
- the body commitments, and — for every pending transaction, confirmed ones included — the attester, queried and received-from sets and the round count; confirmed status is derived from the attester set, so persisting it only for unconfirmed transactions would strip confirmed ones of exactly the evidence that made them confirmed,
- the transaction bodies.

Persisting admission timestamps rather than recomputing them on recovery is what makes `TRANSACTION_TTL` measure a transaction's true age: a node that restarts repeatedly must not thereby extend the residency of transactions it is holding. Persisting attester sets is what keeps a restart from discarding confirmation evidence and re-querying the network for transactions it already had confirmed.

An attestation, once accepted, stays valid for as long as the transaction is pending. It is not re-evaluated against later snapshots: the security argument concerns the set the provider was sampled from at query time, so a declaration lapsing afterwards says nothing about whether the provider held the transaction when it said so.

The `by_prefix` index is **not** persisted; it is rebuilt from the recovered pending set, so that a change to `REFERENCE_PREFIX_LENGTH` takes effect on restart and cannot be contradicted by an index built under the previous parameter.

## Node API

A node exposes the mempool to local clients. These endpoints are operational rather than consensus-bearing; they are listed here because they are the submission path for every transaction that originates at this node.

| Operation | Description |
| --- | --- |
| Submit transaction | Admit a transaction as a local submission and broadcast it. Answers with the outcome of [Transaction Admission](#transaction-admission). |
| View | The hashes of the currently pending transactions. |
| Status | For each queried hash, whether the transaction is unknown to this node, pending and unconfirmed, or pending and confirmed. |
| Metrics | The number of pending transactions, how many of them are confirmed, and the time of the most recent admission. |

`Status` answers only about this node's mempool. A transaction reported as unknown may be pending at every other node, and a transaction reported as pending may be one that this node alone received. Confirmation is the useful signal for a submitter: it is the point at which the transaction has been shown to have reached the network and becomes eligible for inclusion by any honest leader that holds it.

# Details

## Why Admission Is Stateless

Admission could plausibly check the transaction against the node's ledger state — rejecting transactions that spend notes that do not exist, or that cannot pay their fees. It does not, and the reason is view uniformity rather than cost.

A stateful admission rule makes mempool contents a function of chain state. Two nodes on different branches of a fork, or one node lagging the other by a block, would then reach different admission decisions on the same transaction. Every such disagreement is a reference that one node can resolve and the other cannot — that is, a proposal that some validators accept and others reject for reasons unrelated to the proposal's validity. Statelessness confines admission disagreement to what nodes have actually received.

The cost is that the mempool holds transactions that can never be applied, and that it does so at no charge to whoever submitted them. That trade is currently resolved in favour of uniformity, bounded only by `MAX_TRANSACTION_SIZE` and `TRANSACTION_TTL`.

## Transaction Maturity

Transaction maturity is the assumption that a referenced transaction has reached every node before the proposal referencing it arrives. It is not enforced by the mempool; it is produced by the latency asymmetry between the two paths a message can take:

1. A transaction is admitted at one node and gossiped directly over `MEMPOOL_TOPIC`, reaching the network in the time gossipsub takes to flood a mesh.
2. A proposal referencing it is routed through the Blend network, which delays it by design across multiple hops.

The gap between the two is what the maturity assumption spends. The mempool's contribution is to not add avoidable delay on the first path — hence admission that is stateless and cheap, and broadcast that happens as soon as the transaction is admitted rather than after any deferred check.

## Privacy Considerations

[Blend Protocol](blend-protocol.md#privacy-of-proof-of-stake-systems) observes that the tagging attack is mitigated by "designing a mempool in such a way that the node has an attestation that the transaction was seen by the majority of the network". [Confirmation: Pull](#confirmation-pull) provides that attestation, and [Block Building View](#block-building-view) is where it bites: a selectively delivered transaction never reaches `PULL_CONFIRMATIONS`, so it is never offered for selection, so it never appears in a proposal, so it never identifies a proposer. The channel the attack depends on is closed at its source.

Three further properties keep the mempool from leaking a node's view by other routes:

- Admission rules that do not depend on node-local state, so that mempool contents differ only by what a node has received.
- Prompt, unconditional relay of every transaction on receipt, which shortens the window during which a selectively delivered transaction is held by one node alone.
- Reference resolution that reads the mempool and the proposal alone, so that two nodes holding the same transactions reach the same decision about every proposal.

**A residual observable remains, and it is created by pull itself.** A query tells the provider being asked that the querier holds the named transactions. An adversary that delivers a transaction to exactly one node therefore learns which node that is, as soon as that node queries a provider the adversary controls — which, over a round of `PULL_SAMPLE_SIZE` providers, is likely rather than rare.

This does not restore the attack. The tagging chain runs *tag a node → see the tag in a block → conclude that node proposed the block → measure its proposal rate → infer its stake*, and the leak yields only the first link. Every node queries about every transaction it holds, whether or not it will ever propose, so query behaviour is uncorrelated with leadership and carries no stake signal. What the adversary learns is that a particular node holds a particular transaction — a fact about mempool contents, not about block production.

Two properties of the design keep it that way, and both are load-bearing:

- **Every node pulls for every transaction it admits**, not only for transactions it intends to include. A node that queried only when preparing to propose would make its queries a direct signal of leadership, which is a worse leak than the one it was closing.
- **Queries are made continuously from admission**, not at block-building time, so query timing carries no information about when a node is about to build.

Reducing the residual leak further — by routing queries through the Blend network, or by mixing cover queries about transactions the node does not hold — is left open.

## Denial of Service Considerations

The mempool's exposure follows from stateless admission. An adversary can occupy a node's mempool with well-formed transactions that are not applicable, at the cost of producing valid stateless proofs for each. The mitigations currently in place are:

- `MAX_TRANSACTION_SIZE`, bounding the cost of any single admission.
- Duplicate suppression at both the gossip and mempool layers, bounding amplification of a single transaction.
- `TRANSACTION_TTL`, bounding residency.
- Stateless validation before storage, so that a malformed or unprovable transaction is rejected before it consumes durable storage.

A second surface is the **read** side. A mempool lookup is the expensive step in accepting a proposal, and a proposal reaches a node unauthenticated below its header, so an adversary who can make a node scan its mempool cheaply can make it work on demand. Two rules keep that from being free, and both are stated as constraints on the caller in [Reference Resolution](#reference-resolution):

- The reference count is bounded at decode time, before any allocation proportional to it and before any lookup, so a forged count cannot be turned into work.
- Signature and proof-of-leadership verification precede any lookup, so only a proposal an actual leader signed can reach the mempool at all.

A third surface is the **pull protocol**, which by construction lets any peer make a node do work. It is bounded so that the work is constant and the exchange cannot amplify:

- Answering costs one map lookup per queried hash, one hash over the marked commitments, and one signature — no work proportional to transaction size, which is why the witness is taken over cached commitments rather than over bodies.
- A query carries at most `PULL_MAX_BATCH` hashes and a response is a bitmap plus fixed-size fields, so amplification is bounded: a large query provokes a smaller response, and even the worst case — a single-hash query of 64 bytes against a ~161-byte response — is under $`3\times`$. What actually rules out reflection is the transport, not the sizes: the exchange runs over an established, mutually authenticated libp2p connection, so a response can never be directed at a spoofed third-party address.
- A provider rate-limits queries per peer and may decline to answer. A declined query is not a negative answer: it yields no attestation and the querier samples a different provider, so declining is never a way to make a transaction look unseen.
- A response is only ever accepted against an outstanding `nonce` the querier itself chose, so unsolicited responses cost one map lookup to discard.

A fourth surface has been closed by the choice of `REFERENCE_PREFIX_LENGTH`. A shorter prefix would let an adversary grind two transactions sharing one — a birthday search, not a preimage search — and inject both, so that a reference to either matches twice and every validator holding both fails to reconstruct. At 16 bytes that search costs about $`2^{64}`$ candidate transactions, which puts it out of reach; the mempool consequently needs no ambiguity accounting of its own, and can treat a multiply-matched prefix as the unreachable case that it reports and does not attempt to resolve. See [Prefix length and collision resistance](bedrock-v1.1-block-construction.md#prefix-length-and-collision-resistance).

What is absent is any bound on the *number* of pending transactions, and any cost imposed on the submitter. See [Open Issues](#open-issues).

# Open Issues

The following are known gaps: places where this specification is silent, where the mechanism is incomplete, or where the referenced specifications and the current implementation disagree.

1. **Pull is specified but not implemented.** [Confirmation: Pull](#confirmation-pull) has no counterpart in the current implementation: there is no `PULL_PROTOCOL` behaviour, no confirmation state, and block building selects from all pending transactions. Until it exists, the tagging-attack mitigation this specification relies on is absent.
2. **`PULL_DELAY` rests on an unmeasured assumption.** `PULL_SAMPLE_SIZE`, `PULL_MAX_ROUNDS` and `PULL_CONFIRMATIONS` are calibrated, but that calibration takes as input the probability that an honest provider already holds a broadcast transaction when asked — assumed here to be 0.99, which is a statement about `PULL_DELAY` against gossipsub propagation on the mempool topic. Nobody has measured it. Setting `PULL_DELAY` too low makes honest negative answers common and forces a larger sample; setting it too high delays every transaction's eligibility. `PULL_INTERVAL` is likewise a plausible value rather than a derived one.
3. **Anyone may query.** The protocol does not require a querier to be declared, so any peer at all may poll any provider about any transaction hash and receive a signed answer — a view-mapping primitive available for free. Restricting queriers to the active declared set would close it, but leadership follows from stake through the leader lottery rather than from an SDP declaration, so that restriction would make a node's ability to confirm — and therefore to propose safely — depend on holding a declaration it is not otherwise required to hold. The trade has not been made.
4. **Relay precedes validation.** Push forwards a transaction to the mesh before the mempool has decoded or validated it, so a malformed or stateless-invalid transaction is amplified network-wide before any node rejects it. Deferring relay until after validation would close that amplification, at the cost of one validation per hop of added propagation delay and of making relay behaviour depend on node state. The current setting is deliberate but the cost has not been measured.
5. **No capacity bound.** `pending` grows without limit. `TRANSACTION_TTL` bounds how long any one transaction is held but not how many are held at once, so a node's memory and storage footprint is set by the arrival rate rather than by a configured maximum. A capacity bound requires an eviction order, which in turn requires a notion of transaction value the mempool does not currently have.
6. **No fee-aware selection.** [Execution Market](execution-market.md#block-builder-mechanism-block-construction) specifies that a block builder filters the mempool to transactions whose gas price clears the base fee and orders the remainder by revenue. The mempool view is ordered by admission time and carries no fee information, and block building consumes it first-come-first-served. Closing this requires deciding whether ordering is a mempool concern or a block-builder concern, and — if the mempool is to rank transactions — how a ranking that depends on the base fee is kept from reintroducing the state dependence that [Why Admission Is Stateless](#why-admission-is-stateless) avoids.
7. **A retired transaction cannot resolve a reference.** Resolution reads `pending` only, so a node that has included a transaction on its own branch cannot reconstruct a competing branch's proposal that references it, until a fork switch re-admits it. Extending resolution to transactions retired within `RETIREMENT_GRACE_PERIOD` would remove this last dependence of reconstruction on branch position, at the cost of making a retired transaction a second candidate for its prefix — harmless at 16 bytes, but it has to be stated rather than assumed.
8. **Re-admission of included transactions.** A transaction that has already been included in a canonical block can be gossiped back into a node's mempool, where it occupies space until block building finds it inapplicable or its TTL expires — and it must be confirmed again before this node would re-include it, spending pull rounds on a transaction the chain already carries. A bounded rejection set would address this, at the cost of introducing state that must not diverge between nodes.
9. **Expiry has no independent clock.** In the current implementation, expiry is evaluated when transactions are retired for another reason — that is, when a block is applied. A node that applies no blocks performs no expiry, which is exactly the situation (a stalled or partitioned node) in which unbounded retention is least affordable. Expiry should be driven by a clock of its own.
10. **Re-broadcast policy is unspecified.** A transaction admitted from local submission is broadcast once, and again on each duplicate local submission. There is no periodic re-broadcast of pending transactions, so a transaction lost by the gossip layer before reaching a block builder is not retried until the submitter resubmits it.

# References

- [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md)
- [Cryptarchia Protocol](cryptarchia-v1-protocol.md)
- [Service Declaration Protocol](bedrock-service-declaration-protocol.md)
- [Mantle](bedrock-v1.1-mantle-specification.md)
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
- [Execution Market](execution-market.md)
- [Blend Protocol](blend-protocol.md)
- [P2P Network](../draft/p2p-network.md)
- [Network Wire Format](network-wire-format.md)
- [Cryptarchia Bootstrapping and Synchronization](cryptarchia-v1-bootstr-sync.md)
