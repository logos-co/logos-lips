# STATUS-RLN-DEPLOYMENT

| Field | Value |
| --- | --- |
| Name | RLN deployment to the Status network for gasless L2 |
| Slug | 156 |
| Status | raw |
| Category | Standards Track |
| Editor | Ugur Sen [ugur@status.im](mailto:ugur@status.im) |
| Contributors | Sylvain [sylvain@status.im](mailto:sylvain@status.im) |

<!-- timeline:start -->

## Timeline

- **2026-04-01** — [`b042c3e`](https://github.com/logos-co/logos-lips/blob/b042c3eb64faa0202b3c80d8726d57aacf8ec82c/docs/ift-ts/raw/status-rln-deployment.md) — docs: Initial PR for SN RLN deployment RFC (#286)

<!-- timeline:end -->

## Abstract

This document specifies the Status L2 RLN deployment
architecture for enabling gasless transactions with
built-in spam resistance based on the RLN-V2 protocol.
The specification defines system roles, on-chain and off-chain components,
and the end-to-end transaction flow across users, smart contracts, Layer2 services,
prover and verifier modules, and decentralized slashers.
It describes Karma-based tier management, RLN membership registration,
RLN proof generation and verification, deny-list enforcement, gas-aware message accounting,
and decentralized slashing.
The document further outlines storage requirements and synchronization mechanisms
between on-chain events and off-chain state, providing a cohesive framework
for scalable and abuse-resistant transaction processing on Status L2.

The architecture separates cryptographic soundness from operational deployment.
While operational components may be centralized in this version,
cryptographic enforcement of rate limits and slashing remains verifiable and non-custodial.

## Roles

Status L2 RLN deployment consists of six roles: `user`, `Karma contract`,
`RLN contract`,  `Layer2`, and `Linea ecosystem`, `Slashers`.

- `user`: Uses the Status L2 in a gasless manner who MAY pay premium gas for the transaction (TX).
- `Karma contract`: The contract maintains user karma balances, enforces karma slashing, and manages updateable tier limits.
- `RLN contract`: The contract that stores the RLN memberships.
- `Layer2`: Trusted components that are operated by Status L2 team.
- `Linea ecosystem:` : Linea L2 components
- `Slashers` : External identities responsible for tracking RLN proofs
and related metadata in order to identify spam and trigger slashing when applicable.

## General Flow

- `User` creates a TX send it to the network
- The RPC node submits the TX to the mempool, where it is forwarded to the Prover via gRPC,
before P2P propagation to the sequencer.
- `Prover module` bootstraps by querying the `Karma contract` for current user tier limits,
then listens to events and updates the local tier limit table upon any changes.
- `Prover module` checks user has enough Karma `minK` (which equals the `minKarma` of the first tier)
for registration, if so prover module registers RLN membership on behalf of user, otherwise skips registration.
- Prover creates the RLN proof using the [Zerokit](https://github.com/vacp2p/zerokit) backend `prover module`
if user is registered and is in Tier limit and stores in a database.
If registered user exceeds the tier limit, the user needs to pay premium gas. Then prover streams the proofs and metadata via gRPC.
- RLN [verifier module](#2-verifier-module) fetches the RLN proofs and metadata from
prover module and try to find of RLN proof for each submitted Transaction (TX).
The Sequencer forwards the transaction to the mempool if the RLN verifier module
has not detected spam and the transaction is accompanied by a valid RLN proof.
- In parallel with the sequencer’s operation, `slashers` independently subscribe
to and fetch RLN proofs from the prover and monitor them for spam behavior.
Upon detecting spam, `slashers` extract corresponding `secret-hash` from proofs
and submit it to the `RLN contract` . As result, the spammer’s RLN membership is revoked on-chain
by removing the registration, and the prover module updates its local state accordingly
by removing the user based on the emitted slashing event.
Finally, spammers Karma amount is mapped to the `minK`-1.

The tier table is as follows:

| Tier | Daily Quota (Tier limits) | Equivalent Rate | Karma Range |
| --- | --- | --- | --- |
| Entry | 1 tx/day | 1 tx every 24 hours | 0-1 |
| Newbie | 5 tx/day | 1 tx every ~5 hours | 2-49 |
| Basic | 15 tx/day | 1 tx every 90 minutes | 50-499 |
| Active | 96 tx/day | 1 tx every 15 minutes | 500-4999 |
| Regular | 480 tx/day | 1 tx every 3 minutes | 5000-19999 |
| Power User | 960  tx/day | 1 tx every 90 seconds | 20000-99999 |
| Pro User | 10080  tx/day | 1 tx every 9 seconds | 100000-499999 |
| High-Throughput | 108000 tx/day | 1 TPS | 500000-4999999 |
| S-Tier | 240000 tx/day | 5 TPS | 5000000-9999999 |
| Legendary | 480000 tx/day | 10 TPS | 10000000-∞  |

## 1. Prover module

Prover module is a stand-alone gRPC service module
that is mainly responsible for three functionality,
Karma service, RLN registration, creating RLN proofs.
This module is operated by `Layer2`.

### 1.1. Karma service

Prover module requires to amounts of Karma
of users to manage tier levels.
To this Karma service has two functionality with querying `Karma contract`,

- Get amount of Karma for a user
- Get Tier limits

Karma service query is triggered if the user has no more free TX right,
in case the user can move to higher tier without user interaction.
Otherwise, if the  `user` has enough free TX, we don’t update `user`'s tier.

Tier proto file for Tier Query info:

```protobuf
message GetUserTierInfoRequest {
Address user = 1;
}
```

```protobuf
message GetUserTierInfoReply {
oneof resp {
UserTierInfoResult res = 1;
UserTierInfoError error = 2;
}
}
```

```protobuf
message UserTierInfoResult {
sint64 current_epoch = 1;
sint64 current_epoch_slice = 2;
uint64 tx_count = 3;
optional Tier tier = 4;
}
```

```protobuf
message Tier {
string name = 1;
uint64 quota = 2;
}
```

```protobuf
message UserTierInfoError {
string message = 1;
}
```

### 1.2. RLN registration

Prover module MUST register the users who has at least `minK` Karma
to the RLN contract for corresponding global rate limit `rateR` automatically,
where `minK` and `rateR` are fixed for every user.
After setting this values, the registration as follows:

- Creates the `id-commitment` based on `rateR` on behalf of `user`.
- Sends the `id-commitment` to the RLN contract without Karma stake.
- Receive and stores the membership proof information such as leaf index
from the RLN contract in `registeredUsers` list.

Finally, `registeredUsers` consists of as follows:

- User address: `0xabc...`
- User `treeInfo`: (`treePath`,`treeIndex`) since `id-commitment` are stored in multiple tree in DB.

With the registration, user allows to use free gas transaction within its Tier

```protobuf
enum RegistrationStatus {
Success = 0;
Failure = 1;
AlreadyRegistered = 2;
}
```

```protobuf
message RegisterUserReply {
RegistrationStatus status = 1;
}
```

### 1.3. Proof generation

Prover module MUST create `RLNproof` for user who is in `registeredUsers` table,
upon a TX as shown in previous step for a gasless TX.
For `RLNproof` generation for the TX done by Prover module as follows:

- Receive the TX from the RPC node asynchronously, user is the owner of the TX
- Checks the user is indeed in `registeredUsers`
- Creates RLN proof on TX by using Zerokit with checking membership information `treeInfo` in `registeredUsers`
then streams the proof for a specific epoch.
- Serializes then streams RLN proofs via gRPC.
- Outputs `RLNProof` metadata named `proof_value` contains `y` and `internal_nullifier` value
see the [RLN specification](https://rfc.vac.dev/vac/raw/rln-v2/) for details.

```protobuf
message RlnProofFilter {
optional string address = 1;
}
```

```protobuf
message RlnProofReply {
oneof resp {
RlnProof proof = 1;
RlnProofError error = 2;
}
}
```

```protobuf
message RlnProof {
bytes sender = 1;
bytes tx_hash = 2;
bytes proof = 3;
}
```

```protobuf
message RlnProofError {
string error = 2;
}
```

Note that the prover module always creates an RLN proof upon user request,
regardless of whether the user exceeds tier or RLN limits.
Enforcement of tier limits is performed via deny-list interactions,
while RLN limits are enforced by revealing the `secret-hash` extracted
from spam proofs and submitting it to the `RLN contract`.

### 1.4. Storage

RLN proofs are stored in a persistent database (DB) with other informations as follows:

- **table “user”**: Stores the `RlnUserIdentity` which consists of three field elements: `id-commitment`, `secret-hash` and `rateR`.
  - key = Serialized(`User address`)
  - value = Serialized (`RlnUserIdentity` , `TreeIndex` , `IndexInMerkleTree`)

    Since `RlnUserIdentity` are stored in multiple merkle tree, prover locates them with `TreeIndex` and `IndexInMerkleTree.`

- table “idx”:
  - there is only 1 key = “COUNT” and value = “Number of Merkle tree”
- table “tx_counter”:
  - key = Serialized (User adress)
  - value = Serialized(EpochCounters structure) = Serialized(~ `Epoch`, `tx_counter`)
- table “tier_limits”:
  - **Key** = Only 2 keys `CURRENT` ‖ `NEXT`
  - **Value** = Serialized `Tier Limit list`

### 1.5. Tier List Management

Tiers list are stored on-chain in `Karma contract` and this is a dynamic list
that is adjusted by Status L2 team according to the inflation of Karma bound.
This section specifies the changes that initiates by `Karma contract` then affects prover module.
Each update starts by invoking the tier list in `Karma contract` with some requirements as follows:

- Each updates MUST be contiguous which means no gap or overlap between different tiers.
Other saying, the intersection of two sequential tiers’ maxKarma and minKarma range should be distinct,
where minKarma and MaxKarma values are the local values for each karma tier
unlike `minK` is the minimum Karma amount for user can use gasless transaction.
- For a tier, minKarma MUST less than maxKarma.
- First tier’s minKarma MUST be equal to  `minK`

```solidity
struct Tier {
    uint256 minKarma;
    uint256 maxKarma;
    string name;
    uint32 txPerEpoch;
}
```

Updating tiers phase starts with updating tier list in `Karma contract`
which is static writing the new tiers that MAY be change the number of tiers and their bounds.
Then, the check method in `Karma contract` checks three requirements above.

As the second phase, prover module listen for a specific event then fetch
the new tier list from `Karma contract` and update the local list.
Note that, updating the contract require a delay till updating the local tier table of prover.

### 1.6 Gas Checking

Prover is also responsible for checking that the gas requirements of TXs are at the limit
since the RLN protects the network in terms of number of TXs not the total gas consumptions.
When a TX is submitted to the prover, it has a field named: `estimated_gas_used` (type uint64 - unit  gas unit e.g. not in wei).

For now, prover has TX and its gas estimation , namely `currentGas`.
Prover checks that `gasQuota` cannot be larger than `currentGas` for a single proof.
If `currentGas` is equal or lower than the `gasQuota`,
the prover continues with the [proof generation section](#13-proof-generation).

Otherwise, prover calculates the `txCounterIncrease` as the number of ceil (==`currentGas`/`gasQuota`),
expecting a value greater than 2 since the `currentGas` > `gasQuota`.
Then the prover creates a proof burns `txCounterIncrease` many message allocation
for the TX due to the [multi-message_id burn RLN](https://lip.logos.co/ift-ts/raw/multi-message_id-burn-rln.html).

## 2. Verifier Module

The verifier module is composed of an identity operating
in the sequencer environment together the decentralized external slashers.
Also verifier module manually conducts the slashing by invoking the `Karma contract`
with authorized callers as owner in case spamming.
Prover module outputs `RLNproof` with proof metadata named `proof_values`
that includes `y` and `internal_nullifier` value.
The verifier module MUST record and store all `internal_nullifier` to use them for detecting spam.

The detection of spam is requiring the `internal_nullifier` in an epoch.
In this case, when verifier module detects the recurring them,
verifier module MUST extracts the `secret-hash` from two different message with same `message_id`
(see [RLN Specification](https://lip.logos.co/ift-ts/raw/rln-v2.html)), and invoke the `Karma contract`
for slashing which maps user’s Karma to `MinK-1` then adds the `user` to `denylist`.

Note that, Zerokit contains [a function named comput_id_secret](https://github.com/vacp2p/zerokit/blob/master/rln/src/protocol.rs#L526)
for extracting the secret-hash for a given two recurring `internal_nullifier`.

## 3. Smart Contracts

There are two contracts as `Karma contract` and `RLN contract` that former regulates
the tier management and slashing in case spam and later holds the RLN membership tree.
Prover is listening slashing event so that update its state by removing the slashed user
as spammer from the local DB. Prover also listening the tier-limits from `karma contract` to update local tier limits.

`Karma contract`:

- Modified ERC20 contract without transfer option.
- Can be queried to get any user’s Karma balance.
- Stored updatable tier table that shows min and max Karma that prover module fetches this information.

`RLN contract`:

- Stores the RLN membership tree that consists of `id-commitment`
- Does not store stake since Karma is non-transferable
- Contains the slashing function as mentioned in [Decentralized Slashing](#5-decentralized-slashing) section which takes a `secret-hash` and get reward
for invoker also spammers `id-commitment` is dropped off from contract and prover.

## 4. Deny List

Deny list behaves a black list for a `user` who act maliciously in two ways:

1. Exceeds the tier limit and still trying to use gasless TX.
The prover module marked as this user as in deny list but still continue to create the RLN proof for the TX.
2. Exceeds the global rate limit `rateR` that results with slashing by mapping user’s Karma to `MinK-1.`

The `user` who is on the deny list MUST NOT be able to submit gasless transactions.
A user can regain access to gasless transactions only after being removed from the deny list.
Escaping from the deny list is possible under the following conditions

- **TTL expiration:** Deny list entries MAY be configured with an expiration time.
If a deny list participation is not intended to be permanent, the entry is assigned a predefined time window.
Upon expiration of this period, the user address is automatically considered removed from the deny list.
The sequencer is responsible for checking expiration timestamps and removing expired user addresses from the deny list accordingly.
- **Explicit removal:** In this type removel of deny list occurs in two cases: **(i)** when a user submits a transaction
with a gas price exceeding the configured premium gas threshold, in which case the sequencer removes the user from the deny list,
and **(ii)** through manual deletion performed by the Layer2 operator.

## 5. Decentralized Slashing

Decentralized slashing is a capability provided by specialized nodes,
called `slashers`, which operate alongside sequencer-side RLN verifiers
to externally detect RLN-based spam.

In `RLN contract`, the user `id-commitment` is stored as mapping.
The `slashers` receive all proofs by subscribing gRPC to the prover.
In the event of spam, any `slasher` can extract the `secret-hash`
from the proof and submit it to the `RLN contract`.

`RLN Contract` does as following:

- Receives the `secret-hash` in plaintext
- Calculates the `id-commitment` by hashing `secret-hash` with Poseidon hash.
- Look up the list whether it includes the `id-commitment` returns 1 if there is, returns 0 otherwise.
- If it returns 1, the slasher who is the caller of the contract, is rewarded with Karma tokens.
- The prover module listens this activity (an event is sent by the smart contract when slashing)
and drop the particular `id-commitment` from its local DB.
- Upon detecting spam, the `RLN Contract` invokes the slashing function in the `Karma Contract`,
which burns the spammer’s Karma tokens. 

Note that the `secret-hash` are derived by a high entropy randomness
that implies all `id-commitment`  are unique.
Plus, the spammers’ `id-commitment` are dropped from the list.
Under this conditions, double slashing is not feasible.

### 5.1. Proof Aggregation Layer

Instead of having slashers connect directly to the prover,
an intermediate aggregation layer is introduced between the prover and the slashers.
An `aggregator` is an entity that subscribes to the prover via gRPC,
collects RLN proofs and associated metadata, and forwards them to slashers.

The aggregator MUST:

- Subscribe to the prover module via gRPC to receive all RLN proofs and metadata.
- Maintain an up-to-date list of active slashers and forward received proofs to each of them.
- Be stateless with respect to slashing decisions. The aggregator is responsible only
for proof distribution, not detection or submission.

To avoid a single point of failure, multiple aggregator instances MAY be deployed.
Each aggregator instance operates independently and subscribes to the prover separately.
Slashers MAY connect to one or more aggregators to ensure redundant proof delivery.

The prover module MUST NOT impose a connection limit on aggregators.
Any entity MAY act as a slasher by connecting to an aggregator without restrictions
under normal operating conditions.
In cases where slasher capacity limits are exceeded,
access control MAY be enforced based on the Karma balance of the requesting entity,
prioritizing slashers with higher Karma amounts.

## References

- [Zerokit](https://github.com/vacp2p/zerokit)
- [Linea](https://linea.build/)
- [RLN-Prover](https://github.com/vacp2p/status-rln-prover)
- [RLN Specification](https://lip.logos.co/ift-ts/raw/rln-v2.html)
- [Multi-message_id burn RLN](https://lip.logos.co/ift-ts/raw/multi-message_id-burn-rln.html)
