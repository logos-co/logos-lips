# LON-ORACLE-ZONE

| Field | Value |
| --- | --- |
| Name | Logos Oracle Network (LON) Oracle Zone |
| Slug | 244 |
| Status | raw |
| Category | Standards Track |
| Editor | Ugur Sen [ugur@status.im](mailto:ugur@status.im) |
| Contributors |  |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

The following document specifies the Logos Oracle Network (LON),
a dedicated Logos Blockchain zone that aggregates and attests external price data
and delivers it to consumers in the Logos ecosystem,
in particular the Logos Execution Zone (LEZ).
A set of oracle nodes fetch prices from external sources, sign their observations,
and publish them as inscriptions on the Logos Blockchain.
Bedrock totally orders and finalizes these inscriptions,
which makes the input data immutable and identical for every reader.
Because the input is immutable and the aggregation code is fixed and deterministic,
every honest indexer that reads the same finalized inscriptions computes the same attested price.

The oracle nodes double as indexers that read the finalized inscriptions and compute the attested price.
Aggregation follows an optimistic model, since an indexer can be malicious and cannot be trusted.
In each round, one indexer acts as the proposer.
It computes the attested price as the median of the valid observations and writes it to LEZ,
which opens a dispute window.
If no dispute is raised before the window closes,
the proposed price is accepted as final.
If a dispute is raised, LEZ verifies the signatures and membership of the observations,
recomputes the median itself, and compares it with the proposed value.
The faulty proposer is slashed by LEZ contracts.

The Oracle Zone deliberately holds no general-purpose execution environment.
Therefore, economic security with oracle node registration by staking and slashing is anchored in LEZ contracts.
This RFC specifies the price-fetching format, the aggregation and attestation logic,
the round and timing model, the optimistic delivery and dispute model, the incentivization bridge, and the parameters.

## Motivation

A decentralized price oracle must verify multiple independent signed observations
per update while sustaining a reasonable update frequency.
Two categorical design approaches are significant:

LEZ-native design:
- All oracle nodes and logic live in the LEZ environment.
Research shows that ECDSA signature verification exhausts the LEZ cycle budget
at a relatively small committee size which is too small for a decentralized oracle.
It is still doable, but the verification must be split across several transactions and blocks, which breaks atomicity.
Aggregate-signature schemes relax the per-signature cost
but still couple the price-update load to the general-purpose execution layer.

Separate Oracle Zone:
- This approach removes the signature verification load from LEZ.
Prices are published as inscriptions on the Logos Blockchain,
and the heavy work of checking them runs off the LEZ execution path.
LEZ consumes only the final attested price on the optimistic path,
and performs signature verification only when a dispute is raised.
This raises the achievable signer count and the update frequency,
which improves both liveness, since more oracle nodes and faster rounds are possible,
and price accuracy, since more independent sources feed a robust median.

The rationale for a separate zone is therefore performance.
Feeding price data does not load the LEZ execution layer,
and the zone can be tuned for fast aggregation and high verification throughput independently of LEZ.

The trade-off introduced by this separation is that the Oracle Zone has no execution environment
in which to custody stake or run slashing logic.
This RFC resolves that by keeping all economic security
in LEZ contracts for stake and slash operations.

## Format Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Assumptions

- At least more than half of the oracle nodes (indexers) are honest,
who fetch-then-forward price data by following this protocol.
- No indexer can manipulate observation ordering.
Ordering authority is delegated entirely to Bedrock's immutable inscription order.
- Indexers have no immutable execution logic beyond aggregation.
Stake custody and slashing enforcement are delegated entirely to LEZ contracts.
- At least one honest indexer disputes a wrong proposal before the dispute window closes,
by sending the observations to LEZ.
LEZ resolves the dispute by recomputing the median.
Correctness of the attested price rests on this one honest indexer existing.
- The active oracle set is large enough that the quorum `N` is reached every round.
Liveness of attestation depends on this oversizing.

## Roles

The roles used in the Oracle Zone are as follows:

- `Bedrock`: The Logos Blockchain ordering layer, acting as the L1.
It totally orders and finalizes the inscriptions,
giving every indexer the same immutable input to aggregate over.
- `oracle node`: An off-chain agent run by an oracle operator.
It fetches prices from external sources, computes a local price observation,
signs and publishes it as an inscription on `Bedrock`.
Each `oracle node` is identified by its public key as `oracle id`.
The same key is its channel key on Bedrock and its staking identity in LEZ.
- `indexer`: An `oracle node` in its second role.
It reads the finalized inscription stream from `Bedrock` and computes the attested price
as the median of the valid observations.
Because the input is immutable and the aggregation code is fixed and deterministic,
every honest indexer MUST derive the same value.
- `proposer`: The one indexer that, in a given round,
writes the attested price to LEZ and opens the dispute window.
Only one proposer acts per round.
- `challenger`: Any indexer that reads the proposed price from LEZ, recomputes it from the same finalized inscriptions,
if the proposed value is wrong, disputes it before the window closes.

## Flow

Before a round begins, each `oracle node` must be a member of the active oracle set.
A node joins by bonding stake in the LEZ contract and registering its `oracle id` in the membership tree held in LEZ.
Only observations from registered nodes are aggregated. 

The general flow of a round is as follows:

- Each `oracle node` fetches prices from external sources for the feed,
computes a local price observation, signs and publishes it as an inscription on `Bedrock`.
Bedrock totally orders and finalizes the inscriptions.
- Every `indexer` reads the finalized inscriptions of the current round
and computes the attested price as the median of the valid observations.
Because the input is immutable and the code is deterministic,
all honest indexers MUST reach the same value.
- One `indexer` acts as the `proposer` for the round.
On the optimistic path it writes to the LEZ contract its attested price together
with the observations and their membership proofs,
and this opens a dispute window.
During the window, the contract waits for a dispute from any other `indexer`.
- Every other `indexer` acts as a `challenger`.
It reads the proposed value from the LEZ contract and compares it with the value it computed itself.
- If the proposed value differs, a `challenger` disputes it before the window closes.
To dispute, it sends the observations to the LEZ contract.
The contract verifies their signatures and membership, recomputes the median itself,
and compares it with the proposed value.
If they differ, the proposed value is rejected and the faulty `proposer` is slashed.
- If no dispute is raised before the window closes,
this is the optimistic path, and the LEZ contract finalizes the proposed value as the attested price.

## Price Fetching

Each `oracle node` fetches the price of the feed from external sources.
The protocol is agnostic to the specific sources and to the local pre-aggregation method.
It is RECOMMENDED that a node query at least three independent sources and submit a local median,
to reduce the chance of its observation being discarded as an outlier.

A node builds its observation deterministically,
so that two honest nodes reading the same prices produce the same value. First, it reads its sources.
How it connects to each source, which endpoints or APIs it uses, is left to the operator, and the protocol does not constrain the source side.
A node MUST validate each source value before using it.
A value that is not a positive number, or that deviates grossly from the others,
MUST be dropped, so a broken or malicious source cannot enter the local median.
Second, it reduces the remaining source values to one local value by taking their median.
Sources report prices at different decimal precisions,
so the node normalizes each to the fixed `decimals` of the feed, rounding half up.
If the number of values is even, it takes the lower of the two middle values,
so the result is always one of the observed prices and never an average.
Third, it encodes that value as an integer at the fixed `decimals`.

As an example, a node reads four sources for BTC/USDT and gets `67123.1`, `67124.2071`, `67125.40215`, and `67126.0`.
Each is a valid positive number, and none is a gross outlier, so all are kept. 
The feed fixes `decimals = 6`, so the node normalizes each to six decimals rounding half up,
giving `67123.100000`, `67124.207100`, `67125.402150`, and `67126.000000`.
Since the count is even, it takes the lower of the two middle values, `67124.207100`.
It scales that to an integer at six decimals, `67124.207100 * 10^6 = 67124207100`,
and sets `price = 67124207100` and `decimals = 6`.
The indexer applies the same normalization and even-count rule when it takes the median over observations.

Each observation is encoded as a `PriceObservation`.
The price is carried as an integer `price` together with a `decimals` field,
so that no floating-point value crosses the protocol boundary.
The real value is `price * 10^(-decimals)`.
Authentication of an observation on the optimistic path comes from Bedrock.
An oracle node publishes to its own channel,
so Bedrock verifies the writer signature at the inscription level and records who wrote each observation.

The `signature` field carries a [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) Schnorr signature
over the SHA-256 hash of the canonical serialization of fields 1 to 6.
The indexer verifies this signature off-chain during aggregation.
On the optimistic path LEZ does not verify it.
LEZ verifies it only when a dispute is raised, without depending on Bedrock,
which is what lets the dispute be resolved inside LEZ.
The `membership_proof` is a separate witness and is not covered by the signature.

The `PriceObservation` is specified using [protocol buffers v3](https://protobuf.dev/):

```protobuf
syntax = "proto3";

message PriceObservation {
  string feed_id           = 1;  // asset pair identifier, e.g. "BTC/USDT"
  int64  price             = 2;  // integer-encoded price, real value = price * 10^(-decimals)
  int32  decimals          = 3;  // number of decimal places in `price` which is 6
  int64  round             = 4;  // round identifier, in Bedrock block-height terms
  int64  timestamp         = 5;  // observation time (unix milliseconds), advisory only
  bytes  oracle_id         = 6;  // the node's 32-byte BIP-340 x-only public key, also its channel key and staking identity
  bytes  signature         = 7;  // BIP-340 Schnorr signature over SHA-256 of fields 1 to 6, verified off-chain by the indexer and on-chain by LEZ only on dispute
  bytes  membership_proof  = 8;  // Merkle inclusion proof of oracle_id under the LEZ membership root (outside signature scope)
}
```

## Aggregation

The `indexer` is the core logic of the Oracle Zone.
Within each round it performs the following steps deterministically over the ordered inscription stream.

1. **Deserialize.** Decode each finalized inscription from `Bedrock` into a `PriceObservation`.
2. **Verify signature.** Verify the `signature` field against `oracle_id` as in [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki).
Observations with an invalid signature are discarded.
This runs off-chain in the indexer.
3. **Check membership.** Confirm `oracle_id` is a member of the active oracle set by verifying
its `membership_proof` against the membership root.
Observations from non-members are discarded.
4. **Compute median.** Once the number of observations in the round reaches the quorum threshold `N`,
compute the `attested price` as the median of all observations in the round, not only the first `N`.
The median structurally tolerates up to half the observations being adversarial without moving outside the honest range.

LEZ does not verify signatures on the optimistic path.
The indexer checks them off-chain during aggregation,
and LEZ verifies them only when a dispute is raised,
over the observations behind the disputed value.
This keeps the heavy per-signature cost off LEZ.

Every honest indexer runs these steps over the same finalized inscriptions and,
because the input is immutable and the code is deterministic, derives the same `attested price`.

The attested price is specified as follows:

```protobuf
syntax = "proto3";

message AttestedPrice {
  string feed_id      = 1;  // asset pair identifier, e.g. "BTC/USDT"
  int64  price        = 2;  // attested median, real value = price * 10^(-decimals)
  int32  decimals     = 3;  // number of decimal places in `price`
  uint32 valid_count  = 4;  // number of observations aggregated in this round
  int64  round        = 5;  // round identifier, in Bedrock block-height terms
  int64  confidence   = 6;  // OPTIONAL: dispersion of observations, scaled like `price`
}
```

The indexer MAY also compute an optional `confidence` value
that reports how tightly the observations cluster around the median.
It is the median absolute deviation scaled to standard-deviation units, `1.4826 * median(|xᵢ - median|)`.
The constant `1.4826` is the standard factor that rescales the median absolute deviation so that,
for normally distributed data, it matches the ordinary standard deviation,
which makes the value easier to read against familiar volatility figures.
A small value means the observations agree closely,
a large value means they are dispersed.
LEZ MAY use it to widen margins or pause when dispersion is high.

## Rounds and Timing

The Logos Oracle Zone has no separate zone-level blocks,
since it runs no independent consensus.
Ordering and finality come entirely from the `Bedrock`.
Every reference to block height or block time in this document is to the `Bedrock`.

The Oracle Zone operates in rounds of length `R_round`.
Two rules govern the timing:

1. **Deterministic windowing.** Round boundaries MUST be defined by block height, not by wall-clock time.
A wall-clock window is non-deterministic across indexer replicas.
Defining the window as a fixed block range lets every replica derive the identical attested price.
2. **Delivery cadence.** Once per round the proposer writes the attested price to LEZ,
which opens the dispute window `W_dispute`.
An on-chain write cannot occur faster than the Logos Blockchain produces blocks, so `R_round >= T_block`.
With the default `T_block = 30 s`, the default round is one block, about `30 s`.

The price is not final the moment it is written.
It becomes final only after `W_dispute` passes with no dispute in LEZ contract.
The effective freshness of a price is therefore the round cadence plus `W_dispute`.
This design targets applications that tolerate this latency.
It does not offer sub-second or high-frequency updates
 and that is a deliberate limitation of the current version.

If fewer than `N` observations are finalized within a round,
no new price is attested for that round, and the last attested price remains the current value
until a round again reaches quorum.
Handling of a proposer that attests incorrectly,
or before quorum, is covered in [Incentivization](#incentivization).

## Oracle Set Membership

Membership of the active oracle set determines which `oracle id`s submit observations that indexers will accept.
Membership is also the basis of incentivization.
To join, an `oracle node` MUST bond stake in a LEZ contract and register its `oracle id` in the membership tree held in LEZ.Registration is a LEZ-only operation and does not require a cross-zone write into the Oracle Zone.

An indexer does not query LEZ state live, which would make aggregation non-deterministic across replicas.
Instead, each observation carries a `membership_proof`,
a Merkle inclusion proof of its `oracle id` against the LEZ membership root,
and the indexer verifies the proof against the membership root it holds.
The indexer is assumed to hold the latest membership root.
Each `oracle id` is the node's BIP-340 x-only public key,
and the membership tree stores these public keys directly.

During aggregation, every indexer discards observations whose `membership_proof` does not verify,
so observations from non-members never enter the median.
On the dispute path the LEZ contract checks the same proofs against its own membership root,
so only registered nodes count toward the disputed value.

## Incentivization

The Oracle Zone has no execution environment of its own,
so it custodies no stake and runs no slashing logic.
All economic security lives in `LEZ contracts`.
Setting membership by staking, reward settlement, and slashing all happen in `LEZ contracts`.
The Oracle Zone only produces the data that these contracts act on.

### Rewards and Revenue

`oracle nodes` earn from serving the feed, and this reward stream is not just compensation but a security primitive.
An `oracle node`'s admission right (see [Oracle Set Membership](#oracle-set-membership)) is a scarce,
income-producing, transferable seat whose market value approximates the net present value of its future reward stream.
This franchise value raises the cost of acquiring a median-controlling set and
makes misbehavior economically self-defeating, since a fault forfeits that future income.
For this to hold, rewards SHOULD be fee-backed (funded by consumers of the feed) rather than pure emissions,
so that the seat's value reflects real, sustainable income rather than speculation.

Reward accounting is computed in the Oracle Zone,
since only the indexer knows which `oracle nodes` submitted valid,
within-bound observations in the epoch.
At each epoch boundary the indexer commits a reward table, for example a Merkle root of `oracle node` amounts,
to a LEZ settlement contract in a single cross-zone transaction.
This keeps reward traffic off the per-round path.
The settlement contract does not run a scheduler.
Each `oracle node` claims against the committed root,
so payout is pull-based and per-epoch rather than a per-round push,
and the claimant pays its own settlement cost.

Reward eligibility is assessed against a soft deviation band around the round's attested median.
The indexer marks each observation as reward-eligible if it lies
within a small deviation `D_reward` of the attested median, and reward-ineligible otherwise.
An eligible observation earns a full, equal share regardless of its exact distance from the median (validity, not proximity),
so `oracle nodes` are not pushed to herd toward the median,
while an ineligible observation earns nothing for that round but is not slashed.
This soft band is distinct from, and much tighter than, the hard validity bound whose breach is a slashable out-of-bound fault.
The band affects reward accounting only.
The attested median is always the plain median of all valid observations, unaffected by `D_reward`.

### Slashing

Slashing MUST fire only on strict and provable conditions.
A slash is triggered by submitting fault evidence to the LEZ contract,
which verifies it and applies the penalty.
Four slashable faults are defined:

1. **Equivocation.** An `oracle id` produces two conflicting signed observations
for the same feed and round.
The two BIP-340 signatures are a self-contained fraud proof,
verified in LEZ, and non-malleable signatures make this unambiguous.
Because the proof is cryptographic and false positives are effectively impossible,
this fault SHOULD carry the highest penalty.

2. **Out-of-bound value.** A signed observation lies outside the hard validity bound `D_slash` for the round.
The signed value plus the round context is itself the proof.
`D_slash` is an absolute sanity bound checked during slashing,
and it is much wider than the tight `D_reward` band used for reward eligibility (`D_reward < D_slash`),
so that an honest node stays well inside it and a value outside it indicates malice or gross malfunction.
Because bound-checking can still have edge cases,
a stale reference or a genuine market dislocation may make an honest value appear out of bound,
this fault SHOULD carry a capped fraction rather than the full stake,
and MAY be paired with a challenge window.

3. **Premature attestation.** A proposer attests a price before the round reaches the quorum `N`.
The number of observations finalized in a round is fixed and provable from the immutable Bedrock inscriptions,
so a challenger proves that fewer than `N` observations existed when the proposer attested.
The fault is objective and cheaply proven.
The proposed price is rejected and the proposer is slashed.

4. **Wrong median.** A proposer attests a value that is not the median of the valid observations of the round,
where valid means correctly signed and from a registered member.
On a dispute, the LEZ contract discards observations that fail signature or membership,
recomputes the median over the rest, and compares.
If the proposed value does not match, the proposer is slashed and LEZ takes
its own recomputed median as the correct value.
Including a non-member or badly signed observation is therefore only a fault when it changes the median.
If it does not change the result, the attestation is still correct and nothing is slashed.
A failed round is not re-proposed.
The feed continues from the next round,
so a proposer that forces a failed round pays a slash for each attempt,
which makes stalling the feed economically unsustainable.

Slashed stake MAY be burnt or split between a bounty to the party that submitted the fault evidence,
which funds a permissionless watchdog economy, and burn or treasury for the remainder.
Liveness and non-participation are NOT slashed.
Missing `oracle nodes` are tolerated by a sufficiently large active set
and are handled through reward eligibility rather than penalties.
Falling outside the `D_reward` band is likewise NOT a slashable fault.
It only forfeits that round's reward.
Subjective incorrect price and within-bound majority bias are also deliberately excluded,
since no trust-minimized programmatic predicate for them exists.
These are addressed economically rather than by slashing,
through the franchise value of the reward stream above,
the unbonding period below, and randomized selection,
as discussed in [Security Considerations](#security-considerations).

## Parameters

The parameters below are drawn from values used by comparable oracle systems and adjusted for this design.
Block-time and finality parameters are properties of the LEZ and are listed for reference.

| Parameter | Symbol | Default | Notes |
| --- | --- | --- | --- |
| Feed |  | `BTC/USDT` | Single feed, more added later. |
| Feed decimals |  | 6 | Fixed integer scale for the feed. Every observation uses it, so the indexer needs no rescaling. |
| Quorum threshold | `N` | 50 | Minimum observations required to attest a price for a round. |
| Honest-majority assumption |  | majority of the aggregated observations | Over the observations aggregated per attestation, not the total pool. |
| Heartbeat / round cadence | `R_round` | 1 block (`~30 s`) | Defined in block-height terms; must be `>= T_block`. |
| Dispute window | `W_dispute` | 3 Bedrock blocks (`~90 s`) | Time a proposed price waits for a dispute before it finalizes. |
| LEZ block time |  | `~1 s` | Consumer zone block time, faster than the host chain block. |
| Aggregation function |  | median | Plain median of all signature and membership-observations. |
| Reward band | `D_reward` | 0.5%* | Tight band around the median for reward eligibility; `D_reward < D_slash`.  |
| Hard validity bound | `D_slash` | 2.5%* | Wide sanity bound; a signed value outside it is a slashable out-of-bound fault.  |
| Signature scheme | | BIP-340 Schnorr | `oracle_id` is the node's 32-byte x-only public key. |
| Active oracle set size | `AOS` | 500* | Scarce, transferable seats (~10x `N`) so a random per-round subset resists majority capture|
| Stake requirement |  | fixed floor, greater of token amount or USD value* | Hybrid floor to resist token-price drawdown; magnitude set with tokenomics. |
| Slash fraction (equivocation) |  | up to 100%* | Cryptographic proof, effectively zero false positives, so the highest tier is justified. |
| Slash fraction (out-of-bound) |  | 5% cap* | Capped due to edge-case risk; MAY use a challenge window. |
| Slash fraction (premature attestation) |  | up to 100%* | Provable from immutable inscriptions, effectively zero false positives. |
| Slash fraction (wrong median) |  | capped* | Proposer attested a value a successful dispute proved wrong. |
| Unbonding / cooldown period |  | 21 days* | Cosmos/Band anchor; must exceed fault-proving window plus deep-finality horizon. |
| Reward settlement |  | per epoch, pull-based | Claim against a committed Merkle root|
| Epoch length |  | 7 days* | Weekly settlement. |
| Reward backing |  | fee-backed preferred* | Fees over pure emissions for sustainable franchise value. |
| Host chain block time | `T_block` | 30 s | Logos default assumed here; verify against spec. |
| Host chain finality depth | `k` | immutable bound (reference) | Worst-case bound; practical confirmation depth is much shallower. |

## Security Considerations

Two properties matter most for a price oracle network.
One is liveness, meaning a fresh price is attested every round.
The other is accuracy, meaning the attested price tracks the real market.
Running as a separate zone serves both.
It lifts the per-round signature-verification load off LEZ,
so the zone can aggregate many more observations per round than an LEZ-native design.
More observations per round improves liveness,
since the quorum `N` is easily reached even when many `oracle nodes` are absent,
and improves accuracy, since more independent observations feed the median.
Accuracy is further backed by the median itself
and by the slashing conditions in [Incentivization](#incentivization).
The points below expand on the assumptions this relies on.

1. **Quorum and honest majority.** The quorum `N` is the minimum number
of valid observations needed before a price is attested.
It is a floor, so every valid observation in the round is aggregated.
The security assumption is that a majority of the aggregated observations are honest,
which keeps the median within the honest range.
A large active set makes it unlikely that a whole round is majority-malicious,
since an attacker would need to control more than half of many independent observations.

2. **Indexer liveness is not oracle node liveness.** Replicating the indexer keeps the indexer layer live.
It does not ensure that enough `oracle nodes` submit each round.
`Oracle node` liveness is handled by keeping the active set large and by rewards,
not by replication or by slashing non-participation.

3. **The optimistic path rests on honest indexers.** On the optimistic path LEZ accepts
the proposer's value without checking it.
A wrong value is caught only if at least one honest indexer,
having recomputed the median offchain from the same finalized inscriptions,
sees the mismatch and raises a dispute.
To dispute, the indexer only sends the observations to LEZ.
LEZ then resolves it, by verifying signatures and membership and recomputing the median
over the immutable observations, so the resolution is trust-minimized and does not rely on any indexer's word.
Safety therefore rests on a one-of-many honest assumption to raise the dispute, and on LEZ to resolve it correctly.

4. **Cross-zone boundary.** The attested price and the slashing evidence
both cross into LEZ over a cross-zone transaction.
Bedrock guarantees that an inscription is validly ordered and finalized,
but not that the sending side computed correctly,
so the correctness of what LEZ consumes is re-established inside LEZ.
On a dispute LEZ verifies the BIP-340 signatures and membership of the observations itself
and recomputes the median, so a slash rests on evidence LEZ checks directly,
not on trusting the party that delivered it.

5. **Completeness of the observation set.** A proposer could omit valid observations to shift the median.
Because the same observations are finalized on Bedrock and carry their own signatures,
an honest indexer can present an omitted observation,
with its `round` field and signature, to LEZ during the dispute window.
LEZ contract verifies it and sees it should have been included.
The `round` field prevents a proposer from claiming a valid observation arrived too late.
Completeness therefore reduces to the same one-of-many honest assumption as the optimistic path.

## Dispute Detection

Every indexer runs the same loop each round for catching wrong attestations.
This section specifies that loop.

Correctness of the feed is guaranteed by the dispute detection mechanism.
On the optimistic path the LEZ contract only stores what the proposer wrote, without any verification.
A wrong value is caught only if at least one indexer runs this loop and raises a dispute within the window.

### The loop

After each round closes, every indexer runs these steps.

1. **Read.** An indexer follows every new Bedrock block
and caches its `PriceObservation` inscriptions in canonical order,
so once a round closes the cache already holds every observation for it.
2. **Recompute.** Run the aggregation over the cached observations and produce the indexer's own attested price.
This is the deterministic median logic described in [Aggregation](#aggregation).
3. **Fetch.** Once round `round` closes in Bedrock, poll the LEZ contract for the accepted attestation.
Polling every few seconds through `W_dispute` is enough; there is no need to read every LEZ block.
4. **Compare.** If the fetched value equals the recomputed one, do nothing.
If they differ, raise a dispute before `W_dispute` closes.

### Raising a dispute

The dispute mechanism requires all observations of the round to be delivered to LEZ,
assuming a majority of indexers is honest.
Since one transaction cannot hold and verify the full set at once,
the delivery is split across multiple transactions inside `W_dispute`.

At least `N` indexers submit the observations it has for the round.
Once the window closes, LEZ deduplicates the collected set by `oracle_id` and `round`,
since the same observation is immutable regardless of who carried it.
LEZ then verifies each unique observation once, requires at least `N` valid ones,
computes the median over the valid set, and compares it to the proposer's written value.
See [Slashing](#slashing) for verification, comparison, and fault definitions.

## Future Work

This section records design directions deferred beyond this version.

- **Randomized selection.** This version fixes neither which nodes attest in a round
nor which node proposes, and both are currently predictable.
Two selections are left to future work, and both need a shared randomness source with a specified construction.
First, the attesting set.
Accepting observations in inscription order until quorum is adequate
while the set is small and curated, but as it grows an attacker holding many seats could place a majority
into a round and bias the median.
Selecting each round's attesting set at random from the larger registered set
forces an attacker to control a large fraction of the whole set rather than a bare majority.
Second, the proposer. A simple round-robin is the starting point,
but a proposer that is unpredictable in advance stops an attacker from targeting the known next writer.

- **Cooldown and unbonding period.** The unbonding period must be long enough that stake stays locked
until any fault can be detected, proven, and settled in LEZ, plus the Logos Blockchain deep-finality margin.
The exact duration is left to tokenomics and should be set well above the deep-finality bound.
The LEZ contracts that hold stake and enforce the cooldown and unbonding are also left to be specified,
since this version covers only the Oracle Zone side.

- **Volatility handling.** In fast markets, honest prices spread out.
A fixed `D_reward` band can then mark many honest observations ineligible for reward exactly when fresh prices matter most.
A mechanism to widen the band or grow the attesting set during high volatility is left to future work.

- **Slash proof submission.** The slashing flow is not yet specified formally.
Who submits the fault evidence is one, and this is an open watcher role paid by the bounty.
What the evidence holds is another.
For equivocation it is the two conflicting signed observations.
For an out-of-bound value it is the signed observation and the round context.
For premature attestation it is the finalized inscriptions showing fewer than `N` observations.
For a wrong median it is the observations behind the disputed value.
How the LEZ contract checks each kind of evidence, and the challenge window for the faults that need one, are open.
Slashing is never automatic. An oracle node or watcher always starts it by sending evidence to the LEZ contract.

- **Reward and slash amount analysis.** This version fixes the reward and slashing mechanisms
but not their exact economic parameters.
Several values are left to future work.
These are the concrete stake requirement, the four slash fractions,
the reward rate and its fee backing, the epoch length, and the unbonding duration.
Each must be sized against the value the feed secures.
The goal is to keep the cost of corruption above the profit from corruption.
This work also covers how the reward table is committed.
It covers whether that commitment needs the same optimistic-proposer-and-dispute protection as the attested price.

- **LEZ contract specification.** This version defines what the LEZ contracts must achieve but not their implementation.
On the optimistic path a contract only stores the proposed price, opens the dispute window,
and finalizes if the window closes clean, so this path does no computation and must be cheap.
On the dispute path the contract does real work.
It verifies signatures, checks membership, recomputes the median, and applies the slash.
This is the heavy path that a separate zone was meant to keep rare.
Left to future work are the concrete contracts for registration and staking, price finalization,
dispute resolution, and reward settlement, and a check that the dispute-path computation fits within the LEZ cycle budget.

- **Confidence threshold.** The `confidence` value reports how tightly observations cluster around the median,
but this version does not fix what counts as an acceptable value.
A normal spread in a fast market can look too wide in a calm one.
Defining this threshold, or a rule that adapts it, is left to future work together with the volatility handling above.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/)

### References

- Logos Improvement Proposals (LIPs) index: [https://lip.logos.co/](https://lip.logos.co/)
- Cryptarchia and Bedrock (Logos): [https://lip.logos.co/blockchain/raw/bedrock-architecture-overview.html?highlight=Cryptarchia#cryptarchia](https://lip.logos.co/blockchain/raw/bedrock-architecture-overview.html?highlight=Cryptarchia#cryptarchia)
- [BIP-340: Schnorr Signatures for secp256k1](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
- [RFC 2119: Key words for use in RFCs](https://www.ietf.org/rfc/rfc2119.txt)
- [protocol buffers v3](https://protobuf.dev/)
- Flare Time Series Oracle (FTSO): [https://docs.flare.network/tech/ftso/](https://docs.flare.network/tech/ftso/)
- Supra DORA (Distributed Oracle Agreement): [https://docs.supra.com/oracles/dora-price-feeds](https://docs.supra.com/oracles/dora-price-feeds)
- LON proof-of-concept 1: [https://github.com/sydhds/lon_poc](https://github.com/sydhds/lon_poc)
- LON proof-of-concept 2: [https://github.com/seugu/lon_oracle_zone_bench](https://github.com/seugu/lon_oracle_zone_bench)
- LON proof-of-concept 3, mocked zone: [https://github.com/seugu/lon_oracle_zone_bench/tree/mocked-zone](https://github.com/seugu/lon_oracle_zone_bench/tree/mocked-zone)
