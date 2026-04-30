# DECENTRALIZED-MLS-OFFCHAIN-CONSENSUS

| Field | Value |
| --- | --- |
| Name | Secure channel setup using decentralized MLS |
| Slug | 104 |
| Status | raw |
| Category | Standards Track |
| Editor | Ugur Sen [ugur@status.im](mailto:ugur@status.im) |
| Contributors | seemenkina [ekaterina@status.im](mailto:ekaterina@status.im) |

<!-- timeline:start -->

## Timeline

- **2026-04-02** — [`155c310`](https://github.com/logos-co/logos-lips/blob/155c310d7bfad6ea3cd9f68e45c68dad731ff629/docs/ift-ts/raw/decentralized-mls-offchain-consensus.md) — de-MLS RFC name change (#303)
- **2026-03-29** — [`ff05dbd`](https://github.com/logos-co/logos-lips/blob/ff05dbd51176443b3e548e9575c3610685c32d63/docs/ift-ts/raw/eth-mls-offchain.md) — ETH-MLS-OFFCHAIN RFC multi-steward follow up (#298)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/ift-ts/raw/eth-mls-offchain.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/ift-ts/raw/eth-mls-offchain.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/eth-mls-offchain.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/eth-mls-offchain.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/eth-mls-offchain.md) — ci: add mdBook configuration (#233)
- **2025-11-26** — [`e39d288`](https://github.com/logos-co/logos-lips/blob/e39d2884fee1b8a0b1b20a430d7004945ce919f6/vac/raw/eth-mls-offchain.md) — VAC/RAW/ ETH-MLS-OFFCHAIN RFC multi-steward support (#193)
- **2025-08-21** — [`3b968cc`](https://github.com/logos-co/logos-lips/blob/3b968ccce3848da67cddb0295a9cdcb37d63d18c/vac/raw/eth-mls-offchain.md) — VAC/RAW/ ETH-MLS-OFFCHAIN RFC  (#166)

<!-- timeline:end -->

## Abstract

The following document specifies scalable
and decentralized secure group messaging application by
integrating Message Layer Security (MLS) backend.
Decentralization refers each user is a node in P2P network and
each user has voice for any changes in group.
This is achieved by integrating a consensus mechanism.
Lastly, this RFC can also be referred to as de-MLS,
decentralized MLS, to emphasize its deviation
from the centralized trust assumptions of traditional MLS deployments.

## Motivation

Group messaging is a fundamental part of digital communication,
yet most existing systems depend on centralized servers,
which introduce risks around privacy, censorship, and unilateral control.
In restrictive settings, servers can be blocked or surveilled;
in more open environments, users still face opaque moderation policies,
data collection, and exclusion from decision-making processes.
To address this, a decentralized, scalable peer-to-peer
group messaging system is proposed, where each participant runs a node, contributes
to message propagation, and takes part in governance autonomously.
Group membership changes are decided collectively through a lightweight
partially synchronous, fault-tolerant consensus protocol without a centralized identity.
This design enables truly democratic group communication and is well-suited
for use cases like activist collectives, research collaborations, DAOs, support groups,
and decentralized social platforms.

## Format Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

### Assumptions

- At least $2n/3$ of the members are honest and follow the de-MLS protocol as specified.
- The nodes in the P2P network can discover other nodes or will connect to other nodes when subscribing to same topic in a gossipsub.
- The presence of non-reliable (silent) nodes MAY be assumed.
- A lightweight, scalable consensus mechanism with deterministic finality within a specific time MUST be employed.
- The network MUST enforce a rate-limiting mechanism for all entities in order to mitigate spam.
- $\Delta$ (Delta) is a protocol parameter denoting a bounded time interval (in seconds)
that defines the maximum synchronization window of the system.
- At least $2n/3$ of the members MUST become synchronized within $\Delta$ time, where $n$ is the group size.

## Roles

The three roles used in de-MLS is as follows:

- `node`: Nodes are participants in the network that are not currently members
of any secure group messaging session but remain available as potential candidates for group membership.
- `member`: Members are special nodes in the secure group messaging who
obtains current group key of secure group messaging.
Each node is assigned a unique identity represented as a 20-byte value named `member id`.
- `steward`: Stewards are special and transparent members in the secure group
messaging who organize the changes by releasing commit messages upon the voted proposals.
There are two special subsets of steward as epoch and backup steward,
which are defined in the section de-MLS Objects.

## MLS Background

The de-MLS consists of MLS backend, so the MLS services and other MLS components
are taken from the original [MLS specification](https://datatracker.ietf.org/doc/rfc9420/), with or without modifications.

### MLS Services

MLS is operated in two services authentication service (AS) and delivery service (DS).
Authentication service enables group members to authenticate the credentials presented by other group members.
The delivery service routes MLS messages among the nodes or
members in the protocol in the correct order and
manage the `keyPackage` of the users where the `keyPackage` is the objects
that provide some public information about a user as specified in [MLS specification](https://datatracker.ietf.org/doc/rfc9420/).

### MLS Objects

Following section presents the MLS objects and components that used in this RFC:

`Epoch`: Time intervals that changes the state that is defined by members,
section 3.4 in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/).
An epoch is represented as a monotonically increasing integer.
It does not correspond to a fixed wall-clock time interval.
Instead, the epoch is incremented upon each valid `commit message` that results in a state transition.

`MLS proposal message:` Members MUST receive the proposal message prior to the
corresponding commit message that initiates a new epoch with key changes,
in order to ensure the intended security properties, section 12.1 in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/).
Here, the add and remove proposals are used.

`Application message`: This message type used in arbitrary encrypted communication between group members.
This is restricted by [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) as if there is pending proposal,
the application message should be cut.
Note that: Since the MLS is based on servers, this delay between proposal and commit messages are very small.

`Commit message:` After members receive the proposals regarding group changes,
the committer, who may be any member of the group, as specified in  [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/),
generates the necessary key material for the next epoch, including the appropriate welcome messages
for new joiners and new entropy for removed members. In this RFC, the committers only MUST be stewards.

### de-MLS Objects

This section presents the de-MLS objects:

`Voting proposal`: Similar to MLS proposals, but processed only if approved through a voting process.
They function as application messages in the MLS group,
allowing the steward to collect them without halting the protocol.
There are three types of `voting proposal` according to the type of consensus as in shown [Consensus Types section](#consensus-types),
these are, `commit proposal`, `steward election proposal` and `emergency criteria proposal`.

`Epoch steward`: The steward assigned to commit in `epoch E` according to the steward list.
Holds the primary responsibility for creating commit in that epoch.

`Backup steward`: The steward next in line after the `epoch steward` on the `steward list` in `epoch E`.
Only becomes active if the `epoch steward` is malicious or fails,
in which case it completes the commitment phase.
If unused in `epoch E`, it automatically becomes the `epoch steward` in `epoch E+1`.

`Steward list`: It is an ordered list that contains the `member id`s of authorized stewards.
Each steward in the list becomes main responsible for creating the commit message when its turn arrives,
according to this order for each epoch.
For example, suppose there are two stewards in the list `steward A` first and `steward B` last in the list.
`steward A` is responsible for creating the commit message for first epoch.
Similarly, `steward B` is for the last epoch.
Since the `epoch steward` is the primary committer for an epoch,
it holds the main responsibility for producing the commit.
However, other stewards MAY also generate a commit within the same epoch to preserve liveness
in case the epoch steward is inactive or slow.
Duplicate commits are not re-applied and only the single valid commit for the epoch is accepted by the group,
as in described in [commit validation service](#commit-validation-service) against the multiple comitting.

Therefore, if a malicious steward occurred, the `backup steward` will be charged with committing.
Lastly, the size of the list named as `sn`, which also shows the epoch interval for steward list determination.

## Flow

General flow is as follows:

- Each `node` creates and sends their `credential` includes `keyPackage`.
- Each `member` creates `voting proposals` sends them to from MLS group during `epoch E`.
- Proposals are voted on during the $\Delta$ time window.
During this period, the system enters a freezing phase (no new proposals are accepted) to ensure
that at least 2n/3 members become synchronized, thereby preserving the
health and correctness of the [commit validation service](#commit-validation-service).
- Meanwhile, the `steward` collects finalized `voting proposals` from MLS group and converts them into
`MLS proposals` then sends them with corresponding `commit messages`
- Eventually, upon receiving `commit messages`, each member applies the
[commit validation service](#commit-validation-service) locally.
After successful validation, the member transitions to the next `epoch E+1`.

## Creating Voting Proposal

A `member` MAY initializes the voting with the proposal payload
which is implemented using [protocol buffers v3](https://protobuf.dev/) as follows:

```protobuf

syntax = "proto3";

message Proposal {
string name = 10;                 // Proposal name
string payload = 11;              // Describes the what is voting fore 
int32 proposal_id = 12;           // Unique identifier of the proposal
bytes proposal_owner = 13;        // Public key of the creator
repeated Vote votes = 14;         // Vote list in the proposal
int32 expected_voters_count = 15; // Maximum number of distinct voters
int32 round = 16;                 // Number of Votes
int64 timestamp = 17;             // Creation time of proposal
int64 expiration_time = 18;       // Time interval that the proposal is active
bool liveness_criteria_yes = 19;  // Shows how managing the silent peers vote
}
```

```protobuf
message Vote {
int32 vote_id = 20;             // Unique identifier of the vote
bytes vote_owner = 21;          // Voter's public key
int64 timestamp = 22;           // Time when the vote was cast
bool vote = 23;                 // Vote bool value (true/false)
bytes parent_hash = 24;         // Hash of previous owner's Vote
bytes received_hash = 25;       // Hash of previous received Vote
bytes vote_hash = 26;           // Hash of all previously defined fields in Vote
bytes signature = 27;           // Signature of vote_hash
}
```

The voting proposal MAY include adding a `node` or removing a `member`.
After the `member` creates the voting proposal,
it is emitted to the network via the MLS `Application message` with a lightweight,
epoch based voting such as [hashgraphlike consensus.](https://github.com/logos-co/logos-lips/blob/consensus-hashgraph-like/vac/raw/consensus-hashgraphlike.md)
This consensus result MUST be finalized within the epoch as YES or NO.

If the voting result is YES, this points out the voting proposal will be converted into
the MLS proposal by the `steward` and following commit message that starts the new epoch.

All `members` including `stewards` MUST maintain a local store of finalized voting proposals
for at least the duration `threshold_duration` mentioned in [Steward Violation List](#steward-violation-list),
required to validate incoming commits and perform [Commit validation service](#commit-validation-service).

## Creating welcome message

When a MLS `MLS proposal message` is created by the `steward`,
a `commit message` SHOULD follow,
as in section 12.04 [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) to the members.
In order for the new `member` joining the group to synchronize with the current members
who received the `commit message`,
the `steward` sends a welcome message to the node as the new `member`,
as in section 12.4.3.1. [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/).

## Single steward

To naive way to create a decentralized secure group messaging is having a single transparent `steward`
who only applies the changes regarding the result of the voting.

This is mostly similar with the general flow and specified in voting proposal and welcome message creation sections.

1. Each time a single `steward` initializes a group with group parameters with parameters
as in section 8.1. Group Context in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/).
2. The each `node` who wants to be a `member` needs to obtain this anouncement and create `credential`
includes `keyPackage` that is specified in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) section 10.
3. The `node` MUST send the plaintext `KeyPackage`, as defined in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/),
accompanied by its signature, and publish it to the Welcome topic.
This ensures that all current group members are aware that a new participant intends to join.
Upon receipt, the `steward` MUST initiate a voting proposal to decide on admitting the new member.
It also provides flexibility for liveness in multi-steward settings,
allowing more than one steward to obtain `KeyPackages` to commit.
4. The `steward` aggregates all `KeyPackages` utilizes them to provision group additions for new members,
based on the outcome of the voting process.
5. Any `member` start to create `voting proposals` for adding or removing users,
and present them to the voting in the MLS group as an application message.
However, unlimited use of `voting proposals` within the group may be misused by
malicious or overly active members.
Therefore, an application-level constraint MAY be introduced to limit the number
or frequency of proposals initiated by each member in order to prevent spam or abuse.
6. After waiting for the $\Delta$ synchronization window, the `steward` collects
finalized `voting proposals` within epoch `E` that have received affirmative votes
from members via application messages.
The `steward` includes only those proposals that have obtained a majority of "YES" votes.
Since voting proposals are transmitted as application messages, omitting
non-finalized proposals does not affect the protocol’s correctness or
consistency.
7. The `steward` converts all approved `voting proposals` into
corresponding `MLS proposals` and `commit message`, and
transmits both in a single operation as in [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) section 12.4,
including welcome messages for the new members.
Therefore, the `commit message` ends the previous epoch and create new ones.
8. Upon receiving a `commit message`, the `members` first execute the [commit validation service](#commit-validation-service),
including verification of signatures and associated `voting proposals`.
If the commit is deemed valid, the `members` apply the commit and synchronize to the upcoming epoch.

## Multi stewards

Decentralization has already been achieved in the previous section.
However, to improve availability and ensure censorship resistance,
the single steward protocol is extended to a multi steward architecture.
In this design, each epoch is coordinated by a designated steward,
operating under the similar protocol as the single steward model.
Thus, the multi steward approach primarily defines how steward roles
rotate across epochs while preserving the underlying structure and logic of the original protocol.
Two variants of the multi steward design are introduced to address different system requirements.

In the multi steward setting, multiple stewards MAY issue `commit messages` within the same epoch.
As a result, members may receive different numbers of commit messages with potentially differing contents.
For all received commits, the [commit validation service](#commit-validation-service) is executed locally and
MUST deterministically output at most one valid commit to be applied for the epoch transition.

### Buffering KeyPackages

In the multi-steward setting, to preserve liveness in the presence of a silent or inactive epoch steward,
all members MUST locally buffer `KeyPackages` received for 3 epochs after the KeyPackage was received,
or until a commit referencing that `KeyPackages` has been successfully validated and applied, whichever comes first.

### Consensus Types

Consensus is agnostic with its payload; therefore, it can be used for various purposes.
Note that each message for the consensus of proposals is an `application message` in the MLS object section.
It is used in three ways as follows:

1. `Commit proposal`:  It is the proposal instance that is specified in Creating Voting Proposal section
with `Proposal.payload` MUST show the commit request from `members`.
Any member MAY create this proposal in any epoch and `epoch steward` MUST collect and commit YES voted proposals.
This is the only proposal type common to both single steward and multi steward designs.
2. `Steward election proposal`: This is the process that finalizes the `steward list`,
which sets and orders stewards responsible for creating commits over a predefined number of range in (`sn_min`,`sn_max`).
The validity of the choosen `steward list` ends
when the last steward in the list (the one at the final index) completes its commit.
At that point, a new `steward election proposal` MUST be initiated again by any member during the corresponding epoch.
The `Proposal.payload` field MUST represent the ordered identities of the proposed stewards.
Each steward election proposal MUST be verified and finalized through the consensus process
so that members can identify which steward will be responsible in each epoch
and detect any unauthorized steward commits.
3. `Emergency criteria proposal`: If there is a malicious member or steward,
this event MUST be finalized through a governance vote,
reflecting the expectation of active participation from members in the decentralized governance process.
If the proposal returns YES, a score penalty MUST be applied to the targeted member or steward
by decreasing their peer score, and a score reward MUST be granted to the creator of the proposal;
if the proposal returns NO, a score penalty MUST be applied to the creator of the proposal.
If the targeted member is the `epoch steward`,
the `backup steward` MUST assume the `epoch steward` role and MUST include the removal of the former `epoch steward`
in the subsequent commit without requiring an additional voting round,
as the finalized emergency criteria proposal serves as sufficient authorization for the removal.
`Proposal.payload` MUST include evidence of dishonesty as defined in the Steward Violation List,
along with the identifier of the malicious member or steward.
This proposal can be created by any member in any epoch.

The order of consensus proposal messages is important to achieving a consistent result.
Therefore, messages MUST be prioritized by type in the following order, from highest to lowest priority:

- `Emergency criteria proposal`

- `Steward election proposal`

- `Commit proposal`

This means that if a higher-priority consensus proposal is present in the network,
lower-priority messages MUST be withheld from transmission until the higher-priority proposals have been finalized.

#### Partial Freeze Semantics

This prioritization is realized through a partial freeze of lower-priority governance traffic.
When an active `Emergency criteria proposal` is observed and has not yet been finalized,
honest nodes MUST temporarily suspend the propagation and creation of lower-priority consensus proposal messages,
including Steward election proposals and Commit proposals.
Such messages MUST be dropped and MUST NOT be forwarded over the network until the emergency proposal is finalized.

This partial freeze applies only to governance-related messages,
MLS application messages MAY continue to be transmitted normally.

If a malicious member attempts to generate or propagate
lower-priority proposals during an active emergency,
these messages will not be observed by the majority of honest nodes
due to deterministic message filtering.
Implementations MAY additionally penalize such behavior using peer scoring mechanisms.

To enforce this behavior, members MUST be able to identify the type of incoming consensus messages
and apply priority-based filtering accordingly.

### Steward list creation

The `steward list` consists of steward nominees who will become actual stewards
if the `steward election proposal` is finalized with YES,
is arbitrarily chosen from `member` and OPTIONALLY adjusted depending on the needs of the implementation.
The `steward list` size, defined by the minimum `sn_min` and maximum `sn_max` bounds,
is determined at the time of group creation.
The `sn_min` requirement is applied only when the total number of members exceeds `sn_min`;
if the number of available members falls below this threshold,
the list size automatically adjusts to include all existing members.

The actual size of the list MAY vary within this range as `sn`, with the minimum value being at least 1.

The index of the slots shows epoch info and value of index shows `member id`s.
The next in line steward for the `epoch E` is named as `epoch steward`, which has index E.
And the subsequent steward in the `epoch E` is named as the `backup steward`.
For example, let's assume steward list is (S3, S2, S1) if in the previous epoch the roles were
(`backup steward`: S2, `epoch steward`: S1), then in the next epoch they become
(`backup steward`: S3, `epoch steward`: S2) by shifting.

If the `epoch steward` is honest, the `backup steward` does not involve the process in epoch,
and the `backup steward` will be the `epoch steward` within the `epoch E+1`.

If the `epoch steward` is malicious, the `backup steward` is involved in the commitment phase in `epoch E`
and the former steward becomes the `backup steward` in `epoch E`.

Liveness criteria:

Once the active `steward list` has completed its assigned epochs,

members MUST proceed to elect the next set of stewards
(which MAY include some or all of the previous members).
This election is conducted through a type 2 consensus procedure, `steward election proposal`.

A `Steward election proposal` is considered valid only if the resulting `steward list`
is produced through a deterministic process that ensures an unbiased distribution of steward assignments,
since allowing bias could enable a malicious participant to manipulate the list
and retain control within a favored group for multiple epochs.

The list MUST consist of at least `sn_min` members, including retained previous stewards,
sorted according to the ascending value of `SHA256(epoch E || retry_round || member id || group id)`,
where `epoch E` is the epoch in which the election proposal is initiated,
`retry_round` is a counter for having different shuffling in the same epoch for recovering situation,
and `group id` for shuffling the list across the different groups.
Any proposal with a list that does not adhere to this generation method MUST be rejected by all members.

It is assumed that that there are no recurring entries in `SHA256(epoch E || member id || group id)`,
since the SHA256 outputs are unique when there is no repetition in the `member id` values,
against the conflicts on sorting issues.

#### Three-Layer Steward Protection Mechanism

de-MLS employs a three-layer protection mechanism to preserve liveness while maintaining security guarantees.
Mitigation of malicious behavior proceeds progressively across layers.
Layer 1 applies local prevention and recovery strategies; if the issue cannot be resolved at this level,
Layer 2 introduces coordinated fallback mechanisms;
finally, Layer 3 enforces network-wide corrective actions.
Each layer is activated only if the previous layer fails to restore normal operation,
ensuring minimal intervention while maintaining system continuity.

##### Layer 1 - Local steward rotation
Layer 1 ensures that a finalized voting proposal is committed by locally rotating over the active `steward list` in deterministic order.

A steward is eligible to act as the `epoch steward` if it is a current group member and not pending removal.
Misbehavior per the [Steward Violation List](#steward-violation-list) does not affect eligibility directly;
it decrements peer score per the [Peer Scoring section](#peer-scoring),
and a steward becomes ineligible only once a `Emergency Criteria Proposal (ECP)` finalizes the removal.

When the nominal epoch steward is ineligible,
members MUST walk the steward list in deterministic order and accept the commit produced by the first eligible steward.
The `backup steward` or any subsequent eligible steward MAY commit without an Emergency Criteria Proposal.

Even when individual stewards are silent or have been removed,
Layer 1 preserves liveness by walking the steward list until an eligible steward produces the commit.
Misbehaving stewards continue to participate in rotation until accumulated scoring triggers `Emergency Criteria Proposal (ECP)`,
at which point removal makes them ineligible and Layer 1 walks past them on subsequent rounds.
If no eligible steward exists across the entire list, the protocol escalates to Layer 2.

##### Layer 2 - Re-election

Layer 2 enables re-election when Layer 1 fails to produce an eligible steward from the active `steward list`.
In this layer, the members MAY initiate a new `steward election proposal` within the same MLS epoch.
Since the MLS epoch does not advance in this case,
the proposer MUST increment the local `retry_round` value and generate a new deterministic steward ordering using:

`SHA256(epoch E || retry_round || member id || group id)`.

Members that are pending removal, self-removal,
or otherwise ineligible MUST be excluded from the proposed steward list.

If the re-election proposal is finalized with YES, the new `steward list` is installed and Layer 1 is applied again.
Otherwise, if the proposal is finalized with NO, `retry_round` MUST be incremented
and the re-election process MAY be repeated until `max_reelection_attempts` is reached.
Note that `max_reelection_attempts` is the parameter that is set during group creation.

If no new `steward list` can be established after exhausting `max_reelection_attempts`,
the system enters a steward deadlock condition, and Layer 3 MUST be activated.

##### Layer 3 — Anti-deadlock ECP

Layer 3 is the final layer of the liveness mechanism and is triggered only
when Layer 2 fails after `max_reelection_attempts` many re-elections.

At this point, any member MAY submit an `Emergency Criteria Proposal` with deadlock `violation_type`.
This proposal does not target a specific member for removal.
Instead, it signals that the protocol cannot produce a valid commit
through the active steward list or through bounded re-election.

If the deadlock `Emergency Criteria Proposal` is finalized with YES, 
the protocol enters a temporary recovery mode.
During recovery mode, the steward gate is relaxed and any remaining member MAY produce the next valid commit.
The first valid commit that is accepted by the commit validation service ends
recovery mode and returns the protocol to the normal working state.
Finally, under the assumption that at least `2n/3` honest members follow the de-MLS protocol,
the deadlock `Emergency Criteria Proposal` cannot be finalized with NO.

### Multi steward with big consensuses

In this model, all group modifications, such as adding or removing members,
must be approved through consensus by all participants,
including the steward assigned for `epoch E`.
A configuration with multiple stewards operating under a shared consensus protocol offers
increased decentralization and stronger protection against censorship.
However, this benefit comes with reduced operational efficiency.
The model is therefore best suited for small groups that value
decentralization and censorship resistance more than performance.

To create a multi steward with a big consensus,
the group is initialized with a single steward as specified as follows:

1. The steward initialized the group with the config file.
This config file MUST contain (`sn_min`,`sn_max`) as the `steward list` size range.
2. The steward adds the members as a centralized way till the number of members reaches the `sn_min`.
Then, members propose lists by voting proposal with size `sn`
as a consensus among all members, as mentioned in the consensus section 2, according to the checks:
the size of the proposed list `sn` is in the interval (`sn_min`,`sn_max`).
Note that if the total number of members is below `sn_min`,
then the steward list size MUST be equal to the total member count.
3. After the voting proposal ends up with a `steward list`,
and group changes are ready to be committed as specified in single steward section
with a difference which is members also check the committed steward is `epoch steward` or `backup steward`,
otherwise anyone can create `emergency criteria proposal`.

A large consensus group provides better decentralization, but it requires significant coordination,
which MAY not be suitable for groups with more than 1000 members.

### Multi steward with small consensuses

The small consensus model offers improved efficiency with a trade-off in decentralization.
In this design, group changes require consensus only among the stewards, rather than all members.
Regular members participate by periodically selecting the stewards by `steward election proposal`
but do not take part in commit decision by `commit proposal`.
This structure enables faster coordination since consensus is achieved within a smaller group of stewards.
It is particularly suitable for large user groups, where involving every member in each decision would be impractical.

The flow is similar to the big consensus including the `steward list` finalization with all members consensus
only the difference here, the commit messages requires `commit proposal` only among the stewards.

### Commit validation service

Since `stewards` are allowed to produce a commit even when they are not the designated `epoch steward`,
multiple commits may appear within the same commit context, often reflecting recurring versions of the same proposals.
To ensure a consistent and deterministic outcome, all members MUST locally perform
commit validation over the set of candidate commits.

This validation process takes as input the set of `finalized voting proposals` locally stored by the member,
as remarked in [Creating Voting Proposal](#creating-voting-proposal), and multiple candidate `commit messages`
with different lengths and contents, each containing `voting proposals`.
The process deterministically selects at most a single valid commit as output.
In cases where protocol violations are detected, the process MAY additionally trigger peer scoring penalties.

For all candidate commits entering validation, the `creator ID` MUST be identified
and verified against the local epoch context to ensure that the commit is eligible for the current epoch.
Commits originating from unauthorized or context-inconsistent creators MUST be rejected.
The `creator ID` MAY additionally be used for peer scoring purposes, including optional slashing or rewarding mechanisms,
depending on whether the commit is determined to be valid or invalid.

A commit is considered valid only if it references governance proposals
that have been finalized through voting and are known to the member.
Commits that reference non-finalized voting proposals MUST be rejected and
MUST trigger a peer score penalty for the commit author,
as this behavior constitutes a protocol violation.

Among the valid candidate commits, the commit derived from the longest
deterministic proposal sequence SHOULD be selected as the single valid commit.
Any other competing commits that do not match the selected commit MUST be
classified as misbehaviour and penalized with a lower reputation score
according to the misbehaviour scoring rules defined in this specification.
The proposal sequence is ordered by the ascending value of each proposal as `SHA256(proposal)`.
Therefore, commit messages that contain the same set of voting proposals
are identical in content and can be easily deduplicated.

Since MLS derives new group secrets from the committer’s contribution,
two `commit messages` containing the exact same ordered set of `voting proposals`
but produced by different `stewards` will generate different group keys.
Therefore, proposal equivalence alone does not guarantee state equivalence.
If multiple valid commits contain the identical deterministic proposal sequence,
the commit validation service MUST select first, if there is `Epoch steward`,
otherwise the commit whose `committer ID` is lexicographically smallest (according to canonical ordering)
the commit validation service MUST select the epoch steward's commit when present;
otherwise (e.g. during Layer 3 recovery mode, where any member MAY commit) 
the commit with the lexicographically smallest committer ID is selected, avoiding different state forks.
Competing commits that contain the same deterministic proposal sequence
but differ only due to steward-generated MLS commit entropy MUST NOT be classified as misbehaviour
and MAY instead be treated as honest participation for peer scoring purposes.

## Self-Removal

A `steward` MUST NOT produce a commit that includes its own removal.
This is not a protocol violation but an inherent constraint of [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/):
a member cannot apply a commit that removes itself from the group;
otherwise, the resulting group key would be accessible to the removed member again,
which is a contradiction of removal.

A member's request to leave the group is not subject to voting.
A removal voting proposal is auto-finalized YES only if its sender,
proposal_owner, and RemoveMember.target all reference the same identity;
members MUST reject any proposal claiming auto-YES status that fails this check
and MAY apply a peer-score penalty against the sender.
Qualifying proposals MUST be processed by the epoch steward in the subsequent commit.

The offload mechanism is implementation-defined,
examples include queuing the removal for the next eligible steward to commit on their next turn,
or triggering an epoch transition (e.g. via a key rotation) so that role rotation hands off naturally.
The originating steward MUST NOT be penalized for omitting its own removal from its commits,
this is a recognized exception to the rule that finalized voting proposals MUST be committed.

Implementations MAY choose either approach. Both are compliant with this specification.

## Steward violation list

A steward’s activity is called a violation if the action is one or more of the following:

1. Broken commit: The steward releases a different commit message from the voted `commit proposal`.
This activity is identified by the `members` since the [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/) provides the methods
that members can use to identify the broken commit messages that are possible in a few situations,
such as commit and proposal incompatibility. Specifically, the broken commit can arise as follows:
    1. The commit belongs to the earlier epoch.
    2. The commit message should equal the latest epoch
    3. The commit needs to be compatible with the previous epoch’s `MLS proposal`.
2. Broken MLS proposal: The steward prepares a different `MLS proposal` for the corresponding `voting proposal`.
This activity is identified by the `members` since both `MLS proposal` and `voting proposal` are visible
and can be identified by checking the hash of `Proposal.payload` and `MLSProposal.payload` is the same as RFC9240 section 12.1. Proposals.
3. Censorship and inactivity: The situation where there is a voting proposal that is visible for every member,
and the Steward does not provide an MLS proposal and commit within the configured `threshold_duration`,
after which the voting process is considered finalized by the majority timer.
This activity is again identified by the `members`since `voting proposals` are visible to every member in the group,
therefore each member can verify that there is no `MLS proposal` corresponding to `voting proposal`,
or commit was produced for a voting proposal that has already been finalized due to timer expiration.

All three violation types are detected locally by members;
each detection contributes a peer-score decrement per the [Peer Scoring section](#peer-scoring).
Removal occurs only after the steward's accumulated score drops below `threshold_peer_score`,
triggering a `Emergency Criteria Proposal (ECP)`.

## Peer Scoring

To improve fairness in member and steward management, de-MLS SHOULD incorporate a
lightweight peer scoring mechanism.
Unfairness is not an intrinsic property of a member.
Instead, it arises as a consequence of punitive actions such as removal following an observed malicious behavior.
However, behaviors that appear malicious are not always the result of intent.
Network faults, temporary partitions, message delays, or client-side failures may lead to unintended protocol deviations.
A peer scoring mechanism allows de-MLS to account for such transient and non-adversarial conditions by accumulating evidence over time.
This enables the system to distinguish persistent and intentional misbehavior from accidental faults.
Member removal should be triggered only in cases of sustained and intentional malicious activity,
thereby preserving fairness while maintaining security and liveness.

In this approach, each node maintains a local peer score table mapping `member_id` to a score,
with new members starting from a configurable default value `default_peer_score`.
Peer score updates MUST be performed only for stewards that are active in the current epoch context.
Peer scores may decrease due to violations and increase due to honest behavior;
such score adjustments are derived from observable protocol events, such as
successful commits or emergency criteria proposals, and each peer updates its local table accordingly.
In particular, peer score updates MAY be triggered either by direct local observation of protocol violations.
Regardless of the trigger, score updates are applied locally by each peer to its own peer score table.

Members MUST periodically evaluate peer scores against the predefined threshold `threshold_peer_score`.
A removal operation based on the `threshold_peer_score` MUST be initiated as an `emergency criteria proposal`
by at least one member and, only after being finalized with a YES outcome, MUST be included in the subsequent commit.
To prevent abuse, if such a removal emergency criteria proposal is finalized with a NO outcome,
a low score MAY be applied to the proposal owner.
This mechanism allows accidental or transient failures to be tolerated while still enabling
decisive action against repeated or harmful behavior.
The exact scoring rules, recovery mechanisms, and escalation criteria are left for future discussion.

## Timer-Based Anti-Deadlock Mechanism

In de-MLS, an epoch deadlock refers to a prolonged period during which no valid commit is produced
despite the presence of at least one `finalized commit proposal` that require a group state change.
To mitigate epoch deadlock risks in de-MLS, a timer-based anti-deadlock mechanism SHOULD be applied in Layer 1,
as it enables recovery while the current steward list is still active.

Each member maintains a local timer with a configured `threshold_duration`.
The timer MUST start when the member observes a `finalized commit proposal` that requires a corresponding commit
(e.g., add/remove membership changes) and MUST reset only when
the [commit validation service](#commit-validation-service) outputs a valid commit for the current commit context.

If the `threshold_duration` is exceeded, the member waits an additional buffer period to account for network delays
and then triggers a high-priority `emergency proposal` indicating a potential deadlock.
If the proposal returns YES, as `emergency proposal` logic, it iterates the `epoch steward` to provide liveness.
Since timers may expire at different times in a P2P setting,
the buffer period mitigates false positives, while commit filtering is required
to prevent commit flooding during recovery.
Emergency proposals that return NO, MUST incur a peer score penalty for the creator of the proposal to reduce abuse.

## Security Considerations

In this section, the security considerations are shown as de-MLS assurance.

1. Malicious Steward: A Malicious steward can act maliciously,
as in the Steward violation list section.
Therefore, de-MLS enforces that any steward only follows the protocol under the consensus order
and commits without emergency criteria application.
2. Malicious Member: A member is only marked as malicious
when the member acts by releasing a commit message.
3. Steward list election bias: Although SHA256 is used together with two global variables
to shuffle stewards in a deterministic and verifiable manner,
this approach only minimizes election bias; it does not completely eliminate it.
This design choice is intentional, in order to preserve the efficiency advantages provided by the MLS mechanism.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/)

### References

- [MLS RFC 9420](https://datatracker.ietf.org/doc/rfc9420/)
- [Hashgraphlike Consensus](https://github.com/logos-co/logos-lips/blob/consensus-hashgraph-like/vac/raw/consensus-hashgraphlike.md)
- [vacp2p/de-mls](https://github.com/vacp2p/de-mls)
