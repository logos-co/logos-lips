# NOMOSDA-REWARDING

| Field | Value |
| --- | --- |
| Name | NomosDA Rewarding |
| Slug | 149 |
| Status | raw |
| Category | Standards Track |
| Editor | Marcin Pawlowski <marcin@status.im> |
| Contributors | Alexander Mozeika <alexander.mozeika@status.im>, Mehmet Gonen <mehmet@status.im>, Daniel Sanchez Quiros <danielsq@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-30** — [`0ef87b1`](https://github.com/logos-co/logos-lips/blob/0ef87b1ba9491c854e48c8dfd7574d34ec69c704/docs/blockchain/raw/da-rewarding.md) — New RFC: CODEX-MANIFEST (#191)
- **2026-01-30** — [`3f76dd8`](https://github.com/logos-co/logos-lips/blob/3f76dd87a0b6580c16caa401c7fd5ec7dd9a7d6b/docs/blockchain/raw/da-rewarding.md) — Add NomosDA Rewarding specification (#269)

<!-- timeline:end -->

## Abstract

This document specifies the opinion-based rewarding mechanism
for the NomosDA (Nomos Data Availability) service.
The mechanism incentivizes DA nodes to maintain consistent and high-quality service
through peer evaluation using a binary opinion system.
Nodes assess the service quality of their counterparts across different subnetworks,
and rewards are distributed based on accumulated positive opinions
exceeding a defined activity threshold.

**Keywords:** NomosDA, data availability, rewarding, incentives, peer evaluation,
activity proof, quality of service, sampling

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119][rfc-2119].

### Definitions

| Terminology | Description |
| ----------- | ----------- |
| Block Finality | A period expressed in number of blocks (2160) after which a block is considered finalized, as defined by parameter $k$ in Cryptarchia. |
| Session | A time period during which the same set of nodes executes the protocol. Session length is two block finalization periods (4320 blocks). |
| Activity Proof | A data structure containing binary opinion vectors about other nodes' service quality. |
| Active Message | A message registered on the ledger that contains a node's activity proof for a session. |
| Opinion Threshold | The ratio of positive to negative opinions required for a node to be positively opinionated (default: 10). |
| Activity Threshold | The number of positive opinions ($\theta = N_s/2$) a node must collect to be considered active. |
| DA Node | A node providing data availability service, identified by a unique `ProviderId`. |
| SDP | Service Declaration Protocol, used to retrieve the list of active DA nodes. |

### Notations

| Symbol | Description |
| ------ | ----------- |
| $s$ | Current session number. |
| $N_s$ | Set of DA nodes (unique `ProviderId`s) active during session $s$. |
| $S$ | Session length in blocks (4320). |
| $b$ | Block number. |
| $\theta$ | Activity threshold ($N_s/2$). |
| $R_s$ | Base reward for session $s$. |
| $I_s$ | Total income for DA service during session $s$. |
| $R(n)$ | Reward for node $n$. |

## Background

The NomosDA service is a crucial component of the Nomos architecture,
responsible for ensuring accessibility and retrievability of blockchain data.
This specification defines an opinion-based rewarding mechanism
that incentivizes DA nodes to maintain consistent and high-quality service.

The approach uses peer evaluation through a binary opinion system,
where nodes assess the service quality of their counterparts
across different subnetworks of DA.
This mechanism balances simplicity and effectiveness
by integrating with the existing Nomos architecture
while promoting decentralized quality control.

The strength of this approach comes from its economic design,
which reduces possibilities for dishonest behaviour and collusion.
The reward calculation method divides rewards based on the total number of nodes
rather than just active ones,
further discouraging manipulation of the opinion system.

### Three-Session Operation

The mechanism operates across three consecutive sessions:

1. **Session $s$**: NomosDA nodes perform sampling of data blobs referenced in blocks.
   While sampling, nodes interact with and evaluate the service quality
   of other randomly selected nodes from different subnetworks.
   Nodes sample both new blocks and old blocks.

1. **Session $s + 1$**: Nodes formalize their evaluations by submitting Activity Proofs—
   binary vectors where each bit represents their opinion (positive or negative)
   about other nodes' service quality.
   These opinions are tracked separately for new and old blocks.
   The proofs are recorded on the ledger through Active Messages.

1. **Session $s + 2$**: Rewards are distributed.
   Nodes that accumulate positive opinions above the activity threshold
   receive a fixed reward calculated as a portion of the session's DA service income.

## Protocol Specification

### Session $s$: Sampling Phase

1. If the number of DA nodes (unique `ProviderId`s from declarations)
   retrieved from the SDP is below the minimum,
   then do not perform sampling for **new blocks**.

1. If the number of DA nodes retrieved from the SDP for session $s - 1$
   was below the minimum,
   then do not perform sampling for **old blocks**.

1. If the number of DA nodes retrieved from the SDP is below the minimum
   for both session $s$ and $s - 1$,
   then stop and do not execute this protocol.

1. The DA node performs sampling for every new block $b$ it receives,
   and for an old block $b - S$ for every new block received
   (where $S = 4320$ is the session length).

   1. The node selects at random (without replacement) 20 out of 2048 subnetworks.

      > **Note**: The set of nodes selected does not have to be the same
      > for old and new blocks.

   1. The node connects to a random node in each of the selected subnetworks.
      If a node does not respond to a sampling request,
      another node is selected from the same subnetwork
      and the sampling request is repeated until success is achieved
      or a specified limit is reached.

1. During sampling, the node measures the quality of service
   provided by selected nodes as defined in
   [Quality of Service Measurement](#quality-of-service-measurement).

### Session $s + 1$: Opinion Submission Phase

1. The DA node generates an Activity Proof that contains opinion vectors,
   where all DA nodes are rated for positive or negative quality of service
   for new and old blocks.

1. The DA node sends an Active Message that is registered on the ledger
   and contains the node's Activity Proof.

### Session $s + 2$: Reward Distribution Phase

1. Every node that collected above $\theta$ positive opinions
   receives a fixed reward as defined in [Reward Calculation](#reward-calculation).

1. The rewards are distributed by the Service Reward Distribution Protocol.

## Constructions

### Quality of Service Measurement

A node MUST measure the quality of service for each sampling it performs
to gather opinions about the quality of service of the entire DA network.
These opinions are used to construct the Activity Proof.

The global parameter `opinion_threshold` is set to 10,
meaning a node must receive 10 positive opinions for each negative opinion
to be positively opinionated (at least 90% positive opinions).

To build an opinions vector describing the quality of data availability sampling,
a node MUST:

1. Retrieve $\mathcal{N}_s$, a list of active DA nodes (unique `ProviderId`s)
   for session $s$, from the SDP.

1. Retrieve $\mathcal{N}_{s-1}$, a list of active DA nodes for session $s - 1$,
   from the SDP (can be retained from the previous session).

1. Order $\mathcal{N}_s$ and $\mathcal{N}_{s-1}$ in ascending lexicographical order
   by `ProviderId` of each node from both lists.

1. Create for each session and independently for old ($\mathcal{N} = \mathcal{N}_{s-1}$)
   and new ($\mathcal{N} = \mathcal{N}_s$) blocks:

   1. `positive_opinions` vector of size $N = \text{length}(\mathcal{N})$
      where the $i$-th element (integer) represents positive opinions
      about the $i$-th node from list $\mathcal{N}$.

   1. `negative_opinions` vector of size $N = \text{length}(\mathcal{N})$
      where the $i$-th element (integer) represents negative opinions
      about the $i$-th node from list $\mathcal{N}$.

   1. `blacklist` vector of size $N = \text{length}(\mathcal{N})$
      where the $i$-th element (bool) marks whether the $i$-th node
      is blacklisted due to providing an invalid response.

1. Send a sampling request to a node $n \in \mathcal{N}$ such that `blacklist[n]==0`:

   1. If the node $n$ responds:
      1. If the response is valid, then `positive_opinions[n]++`
      1. If the response is not valid, then:
         1. Clear positive opinions about the node: `positive_opinions[n]=0`
         1. Mark the node as blacklisted: `blacklist[n]=1`

   1. If the node does not respond, then `negative_opinions[n]++`

1. When the next session starts, create an opinions binary for every node $i \in \mathcal{N}$:

   ```python
   previous_session_opinions[i] = opinion(i, old.positive_opinions,
                                          old.negative_opinions,
                                          old.opinions_threshold)

   current_session_opinions[i] = opinion(i, new.positive_opinions,
                                         new.negative_opinions,
                                         new.opinions_threshold)

   def opinion(i, positive_opinions, negative_opinions, opinion_threshold):
       return (positive_opinions[i] > (negative_opinions[i] * opinion_threshold))
   ```

1. A node sets a positive opinion about itself in the `current_session_opinions` vector.

1. A node sets a positive opinion about itself in the `previous_session_opinions`
   if the node was taking part in the protocol during the previous session.

### Activity Proof

The Activity Proof structure is:

```python
class ActivityProof:
    current_session: SessionNumber
    previous_session_opinions_length: int
    previous_session_opinions: Opinions
    current_session_opinions_length: int
    current_session_opinions: Opinions
```

`Opinions` is a binary vector of length $N_s$
(total number of nodes identified by unique `ProviderId`s from declarations)
where each bit represents a node providing DA service for the session.
A bit is set to 1 only when the node considers the sampling service
provided by the DA node to meet quality standards.

#### Field Descriptions

- `current_session`: The session number of the assignations used for forming opinions.

- `previous_session_opinions_length`: The number of bytes used by `previous_session_opinions`.

- `previous_session_opinions`: Opinions gathered from sampling old blocks.
  When there are no old blocks (first session after genesis
  or after a non-operational DA period),
  these opinions SHOULD NOT be collected nor validated.

- `current_session_opinions_length`: The number of bytes used by `current_session_opinions`.

- `current_session_opinions`: Opinions gathered from sampling new blocks.

#### Validity Rules

The Activity Proof is **valid** when:

- The `current_session_opinions` vector is not provided
  (and `current_session_opinions_length==0`)
  when the DA service was not operational during that session.

- The byte-length of the `previous_session_opinions` vector is:

  $$|\text{previous\_session\_opinions}| = \left\lceil \frac{\log_2(N_{s-1} + 1)}{8} \right\rceil$$

- The `previous_session_opinions` vector is not provided
  (and `previous_session_opinions_length==0`)
  when the DA service was not operational during that session.

- The byte-length of the `current_session_opinions` vector is:

  $$|\text{current\_session\_opinions}| = \left\lceil \frac{\log_2(N_s + 1)}{8} \right\rceil$$

- The $n$-th node (note that $n \in \mathcal{N}_s \not\Rightarrow n \in \mathcal{N}_{s-1}$)
  is represented by the $n$-th bit of the vector (counting nodes from 0),
  with the vector encoded as little-endian.
  The rightmost byte of the vector MAY contain bits not mapped to any node;
  these bits are disregarded.

### Activity Threshold

The activity threshold $\theta$ defines the number of positive opinions
a node must collect from peers to be considered active for session $s$.

$$\theta = N_s / 2$$

Where $\theta$ controls the number of positive opinions
a node must collect to be considered active.

### Active Message

Each node for every session constructs an `active_message`
that MUST follow the specified format.

A node MAY stop sending `active_message`
when the DA service is non-operational for more than a single session.

The `active_message` metadata field MUST be populated with:

- A `header` containing a one-byte `version` field fixed to `0x01` value.
- The `activity_proof` as defined above.

#### Active Message Rules

- An Active Message is stored on the ledger.
- An Active Message is used for calculating the node reward.
- An Active Message for session $s$ MUST only be sent during session $s + 1$;
  otherwise, it MUST be rejected.
- The ledger MUST only accept a single Active Message per node per session;
  any duplicate MUST be rejected.

### Reward Calculation

The reward calculation follows these steps:

#### Step 1: Calculate Base Reward

Calculate the base reward for session $s$:

$$R_s = \frac{I_s}{N_s}$$

Where $I_s$ is the income for DA service during session $s$,
and $N_s$ is the number of nodes providing DA service during session $s$.

> **Note**: The base reward is fixed to the total number of nodes providing the service
> instead of the number of active nodes.
> This disincentivizes nodes from providing dishonest opinions about other nodes
> to increase their own reward.

The income leftovers MUST be burned or consumed
in such a way that will not benefit the nodes.

#### Step 2: Count Positive Opinions

Count the number of positive opinions for node $n$ in session $s$:

$$\text{opinions}(n, s) = \sum_{i=1}^{N} \text{valid}(\text{activity\_proof}(i, n, s))$$

Where $\text{valid}()$ returns true only when the `activity_proof` for node $n$ is valid
and the opinion about node $n$ is **positive** for session $s$.

#### Step 3: Calculate Node Reward

Calculate the reward for node $n$ based on node activity:

$$R(n) = \frac{R_s}{2} \cdot \text{active}(n, s) + \frac{R_{s-1}}{2} \cdot \text{active}(n, s - 1)$$

Where $\text{active}(n, s)$ returns true only when $n \in \mathcal{N}_s$
and the number of positive opinions on node $n$ for session $s$
is greater than or equal to $\theta$:

$$\text{opinions}(n, s) \geq \theta$$

The reward is a function of the node's capacity (quality)
to respond to sampling requests for both new and old blocks.
Therefore, the reward draws from half of the income from session $s$ (for new blocks)
and half of the income from session $s - 1$ (for old blocks).

The base reward $R_s$ is distributed to nodes that both:

- Submitted a valid Activity Proof
- Received positive opinions exceeding the activity threshold
  for at least one of the sessions

> **Note**: Inactive nodes are not rewarded.
> Nodes that have not participated in the previous session
> are not rewarded for the past session.

## Security Considerations

### Subjective Opinions

The mechanism intentionally uses subjective node opinions
rather than strict performance metrics.
While this introduces some arbitrariness,
it provides a simple and flexible approach
that aligns with Nomos' architectural goals.

### Dishonest Evaluation

The system has potential for dishonest evaluation.
However, the economic design reduces possibilities
for dishonest behaviour and collusion:

- The reward calculation divides rewards based on total number of nodes
  rather than just active ones,
  discouraging manipulation of the opinion system.
- Income leftovers are burned to prevent benefit from underreporting.

### Collusion Resistance

The activity threshold of $N_s/2$ requires a node
to receive positive opinions from at least half of all nodes.
This makes collusion attacks expensive,
as an attacker would need to control a majority of nodes
to guarantee rewards for malicious nodes.

## References

### Normative

- [Service Declaration Protocol][sdp] - Protocol for declaring DA node participation

### Informative

- [NomosDA Rewarding][origin-ref] - Original specification document
- [Analysis of Sampling Strategy][sampling-analysis] - Motivation for sampling 20 subnetworks

[rfc-2119]: https://www.ietf.org/rfc/rfc2119.txt
[origin-ref]: https://nomos-tech.notion.site/NomosDA-Rewarding-203261aa09df80af8c77dfb3dc593673
[sdp]: https://nomos-tech.notion.site/Service-Declaration-Protocol
[sampling-analysis]: https://nomos-tech.notion.site/Analysis-of-Sampling-Strategy

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
