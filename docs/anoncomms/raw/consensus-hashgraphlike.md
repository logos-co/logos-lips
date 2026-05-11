# HASHGRAPHLIKE CONSENSUS

| Field | Value |
| --- | --- |
| Name | Hashgraphlike Consensus Protocol |
| Slug | 73 |
| Status | raw |
| Category | Standards Track |
| Editor | Ugur Sen [ugur@status.im](mailto:ugur@status.im) |
| Contributors | seemenkina [ekaterina@status.im](mailto:ekaterina@status.im) |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/anoncomms/raw/consensus-hashgraphlike.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/anoncomms/raw/consensus-hashgraphlike.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/consensus-hashgraphlike.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/consensus-hashgraphlike.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/consensus-hashgraphlike.md) — ci: add mdBook configuration (#233)
- **2025-09-15** — [`f051117`](https://github.com/logos-co/logos-lips/blob/f051117d3782f66d773aaf27845c60a066ac10b6/vac/raw/consensus-hashgraphlike.md) — VAC-RAW/Consensus-hashgraphlike RFC (#142)

<!-- timeline:end -->

## Abstract

This document specifies a scalable, decentralized, and Byzantine Fault Tolerant (BFT)
consensus mechanism inspired by Hashgraph, designed for binary decision-making in P2P networks.

## Motivation

Consensus is one of the essential components of decentralization.
In particular, in the decentralized group messaging application is used for
binary decision-making to govern the group.
Therefore, each user contributes to the decision-making process.
Besides achieving decentralization, the consensus mechanism MUST be strong:

- Under the assumption of at least `2/3` honest users in the network.

- Each user MUST conclude the same decision and scalability:
message propagation in the network MUST occur within `O(log n)` rounds,
where `n` is the total number of peers,
in order to preserve the scalability of the messaging application.

## Format Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”,
“SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document
are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

## Flow

Any user in the group initializes the consensus by creating a proposal.
Next, the user broadcasts the proposal to the whole network.
Upon each user receives the proposal, validates the proposal,
adds its vote as yes or no and with its signature and timestamp.
The user then sends the proposal and vote to a random peer in a P2P setup,
or to a subscribed gossipsub channel if gossip-based messaging is used.
Therefore, each user first validates the signature and then adds its new vote.
Each sending message counts as a round.
After `log(n)` rounds all users in the network have the others vote
if at least `2/3` number of users are honest where honesty follows the protocol.

In general, the voting-based consensus consists of the following phases:

1. Initialization of voting
2. Exchanging votes across the rounds
3. Counting the votes

### Assumptions

- The users in the P2P network can discover the nodes or they are subscribing same channel in a gossipsub.
- We MAY have non-reliable (silent) nodes.
- Proposal owners MUST know the number of voters.

## 1. Initialization of voting

A user initializes the voting with the proposal payload which is
implemented using [protocol buffers v3](https://protobuf.dev/) as follows:

```bash
syntax = "proto3";

package vac.voting;

message Proposal {
  string name = 10;                  // Proposal name
  string payload = 11;               // Proposal description
  uint32 proposal_id = 12;           // Unique identifier of the proposal
  bytes proposal_owner = 13;         // Public key of the creator 
  repeated Vote votes = 14;              // Vote list in the proposal
  uint32 expected_voters_count = 15; // Maximum number of distinct voters
  uint32 round = 16;                 // Number of rounds 
  uint64 timestamp = 17;             // Creation time of proposal
  uint64 expiration_timestamp = 18;  // The timestamp at which the proposal becomes outdated  
  bool liveness_criteria_yes = 19;   // Shows how managing the silent peers vote
}

message Vote {
  uint32 vote_id = 20;            // Unique identifier of the vote
  bytes vote_owner = 21;          // Voter's public key
  uint32 proposal_id = 22;        // Linking votes and proposals
  uint64 timestamp = 23;          // Time when the vote was cast
  bool vote = 24;                 // Vote bool value (true/false)
  bytes parent_hash = 25;         // Hash of previous owner's Vote
  bytes received_hash = 26;       // Hash of previous received Vote
  bytes vote_hash = 27;           // Hash of all previously defined fields in Vote
  bytes signature = 28;           // Signature of vote_hash
}

```

To initiate a consensus for a proposal,
a user MUST complete all the fields in the proposal, including attaching its `vote`
and the `payload` that shows the purpose of the proposal.
Notably, `parent_hash` and `received_hash` are empty strings because there is no previous or received hash.
Then the initialization section ends when the user who creates the proposal sends it
to the random peer from the network or sends it to the proposal to the specific channel.

## 2. Exchanging votes across the peers

Once the peer receives the proposal message `P_1` from a 1-1 or a gossipsub channel does the following checks:

1. Check the signatures of the each votes in proposal, in particular for proposal `P_1`,
verify the signature of `V_1` where `V_1 = P_1.votes[0]` with `V_1.signature` and `V_1.vote_owner`
2. Do `parent_hash` check: If there are repeated votes from the same sender,
check that the hash of the former vote is equal to the `parent_hash` of the later vote.
3. Do `received_hash` check: If there are multiple votes in a proposal, check that the hash of a vote is equal to the `received_hash` of the next one.
4. After successful verification of the signature and hashes, the receiving peer proceeds to generate `P_2` containing a new vote `V_2` as following:

   4.1. Add its public key as `P_2.vote_owner`.

   4.2. Set `timestamp`.

   4.3. Set boolean `vote`.

   4.4. Define `V_2.parent_hash = 0` if there is no previous peer's vote, otherwise hash of previous owner's vote.

   4.5. Set `V_2.received_hash = hash(P_1.votes[0])`.
  
   4.6. Set `proposal_id` for the `vote`.
  
   4.7. Calculate `vote_hash` by hash of all previously defined fields in Vote:
  `V_2.vote_hash = hash(vote_id, owner, proposal_id, timestamp, vote, parent_hash, received_hash)`

   4.8. Sign `vote_hash` with its private key corresponding the public key as `vote_owner` component then adds `V_2.vote_hash`.

5. Create `P_2` with by adding `V_2` as follows:
  
   5.1. Assign `P_2.name`, `P_2.proposal_id`, and `P_2.proposal_owner` to be identical to those in `P_1`.
  
   5.2. Add the `V_2` to the `P_2.Votes` list.
  
   5.3. Increase the round by one, namely `P_2.round = P_1.round + 1`.
  
   5.4. Verify that the proposal has not expired by checking that: `current_time in [P_timestamp, P_expiration_timestamp]`.
    If this does not hold, other peers ignore the message.

After the peer creates the proposal `P_2` with its vote `V_2`,
sends it to the random peer from the network or
sends it to the proposal to the specific channel.

## 3. Determining the result

Because consensus depends on meeting a quorum threshold,
each peer MUST verify the accumulated votes to determine whether the necessary conditions have been satisfied.
The voting result is set YES if the majority of the `2n/3` from the distinct peers vote YES.

To verify, the `findDistinctVoter` method processes the proposal by traversing its `Votes` list to determine the number of unique voters.

If this method returns true, the peer proceeds with strong validation,
which ensures that if any honest peer reaches a decision,
no other honest peer can arrive at a conflicting result.

1. Check each `signature` in the vote as shown in the [Section 2](#2-exchanging-votes-across-the-peers).

2. Check the `parent_hash` chain if there are multiple votes from the same owner namely `vote_i` and `vote_i+1` respectively,
the parent hash of `vote_i+1` should be the hash of `vote_i`

3. Check the `previous_hash` chain, each received hash of `vote_i+1` should be equal to the hash of `vote_i`.

4. Check the `timestamp` against the replay attack.
In particular, the `timestamp` cannot be the old in the determined threshold.

5. Check that the liveness criteria defined in the Liveness section are satisfied.

If a proposal is verified by all the checks,
the `countVote` method counts each YES vote from the list of Votes.

## 4. Properties

The consensus mechanism satisfies liveness and security properties as follows:

### Liveness

Liveness refers to the ability of the protocol to eventually reach a decision when sufficient honest participation is present.
In this protocol, if `n > 2` and more than `n/2` of the votes among at least `2n/3` distinct peers are YES,
then the consensus result is defined as YES; otherwise, when `n ≤ 2`, unanimous agreement (100% YES votes) is required.

The peer calculates the result locally as shown in the [Section 3](#3-determining-the-result).
From the [hashgraph property](https://hedera.com/learning/hedera-hashgraph/what-is-hashgraph-consensus),
if a node could calculate the result of a proposal,
it implies that no peer can calculate the opposite of the result.
Still, reliability issues can cause some situations where peers cannot receive enough messages,
so they cannot calculate the consensus result.

Rounds are incremented when a peer adds and sends the new proposal.
Calculating the required number of rounds, `2n/3` from the distinct peers' votes is achieved in two ways:

1. `2n/3` rounds in pure P2P networks
2. `2` rounds in gossipsub

Since the message complexity is `O(1)` in the gossipsub channel,
in case the network has reliability issues,
the second round is used for the peers cannot receive all the messages from the first round.

If an honest and online peer has received at least one vote but not enough to reach consensus,
it MAY continue to propagate its own vote — and any votes it has received — to support message dissemination.
This process can continue beyond the expected round count,
as long as it remains within the expiration time defined in the proposal.
The expiration time acts as a soft upper bound to ensure that consensus is either reached or aborted within a bounded timeframe.

#### Equality of votes

An equality of votes occurs when verifying at least `2n/3` distinct voters and
applying `liveness_criteria_yes` the number of YES and NO votes is equal.

Handling ties is an application-level decision. The application MUST define a deterministic tie policy:

RETRY: re-run the vote with a new proposal_id, optionally adjusting parameters.

REJECT: abort the proposal and return voting result as NO.

The chosen policy SHOULD be consistent for all peers via proposal's `payload` to ensure convergence on the same outcome.

### Silent Node Management

Silent nodes are the nodes that not participate the voting as YES or NO.
There are two possible counting votes for the silent peers.

1. **Silent peers means YES:**
Silent peers counted as YES vote, if the application prefer the strong rejection for NO votes.
2. **Silent peers means NO:**
Silent peers counted as NO vote, if the application prefer the strong acception for NO votes.

The proposal is set to default true, which means silent peers' votes are counted as YES namely `liveness_criteria_yes` is set true by default.

### Security

This RFC uses cryptographic primitives to prevent the
malicious behaviours as follows:

- Vote forgery attempt: creating unsigned invalid votes
- Inconsistent voting: a malicious peer submits conflicting votes (e.g., YES to some peers and NO to others)
in different stages of the protocol, violating vote consistency and attempting to undermine consensus.
- Integrity breaking attempt: tampering history by changing previous votes.
- Replay attack: storing the old votes to maliciously use in fresh voting.

## 5. Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/)

## 6. References

- [Hedera Hashgraph](https://hedera.com/learning/hedera-hashgraph/what-is-hashgraph-consensus)
- [Gossip about gossip](https://docs.hedera.com/hedera/core-concepts/hashgraph-consensus-algorithms/gossip-about-gossip)
- [Simple implementation of hashgraph consensus](https://github.com/conanwu777/hashgraph)
