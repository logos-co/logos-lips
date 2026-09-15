# MIX-PATH-SELECTION

| Field | Value |
| --- | --- |
| Name | Mix Path Selection |
| Slug | 246 |
| Status | raw |
| Category | Standards Track |
| Editor | Mohammed Alghazwi <mohalghazwi@logos.co> |
| Contributors | Balázs Kőműves <balazs@logos.co> |

## Abstract

This document defines a generic/pluggable component for selecting a Mix path and lists the path selection strategies that a mix user/application/service can select based on their anonymity and communication requirements.

The default Mix Protocol selects a fresh random path for every message. This provides strong route diversity against a global passive adversary, but can result in a high probability of selecting a fully malicious path when a communication session requires a large number of Mix packets.

This specification introduces a generic path-selection interface and defines three path-selection modes:

- **Random mode:** intended for short or unrelated communication where paths are sampled independently.
- **Session mode:** intended for sessions that may generate many (related) Mix packets, such as anonymous downloads.
- **Time-based mode:** intended for long-lived identities or services that communicate over many sessions and potentially with many anonymous clients, such as hidden services.

The strategies specified here build on previous research on [path selection strategies for anonymous download](https://forum.research.logos.co/t/mix-path-selection/721), [time-based path selection](https://forum.research.logos.co/t/hidden-service-time-based-path-selection/730) and [hidden services](https://forum.research.logos.co/t/hidden-service-time-based-path-selection/730/1). Deanonymization probabilities listed in this document are supported by simulation experiments done using [the freeroutesim simulator](https://github.com/logos-storage/hs-mix-sim).

## Definitions

### mixnet adversaries

**Global Passive Adversary (GPA).** An adversary that is able to observe the network traffic globally.

**Mix Node Adversary (MNA).** An adversary that controls a fraction \(\beta\) of the eligible Mix nodes. A path is considered fully compromised when every Mix node on the relevant path is controlled by the adversary.

**Adaptive adversary (AA).** An adversary that may compromise additional Mix nodes over time and may choose which nodes to target based on information learned from previously compromised nodes. This includes attacks against persistent paths or topologies in which the adversary attempts to progressively compromise nodes toward an endpoint.

### the de-anonymization likelihood metric (`DLM`)
The metric we use to measure the expected anonymity provided by each path selection mode is the de-anonymization likelihood metric (`DLM`). This metric was introduced in the [NDSS paper](https://www.ndss-symposium.org/wp-content/uploads/2026-f2384-paper.pdf) and we use it with some slight modifications:
- **packet-based DLM (P-DLM)** is the probability that a single selected path is fully controlled by the adversary.
- **session-based DLM (S-DLM)** is the probability that at least one packet in a session uses a fully compromised path.
- **time-based DLM (T-DLM)** is the probability that a long-lived identity or service becomes deanonymized during a time period `T`.


### Path selection strategy
A **path-selection strategy** is a way to construct a Mix path from the currently eligible Mix nodes. A strategy may be stateless, or it may maintain a local state in order to reuse selected nodes/paths across multiple path requests.

### Sessions
We can define a session as a single or multiple transport layer sessions where a client sends or receives multiple chunks/files that are related, i.e., the chunks are all related to the same file or multiple files but all belong to the same content category/type which an adversary can correlate.

### Local topology
A local topology maintained by the path selector and consists of layers of (possibly trusted) mix nodes and edges connecting these layers. Paths are then constructed by traversing this local topology. Selector may rotate nodes on this topology or keep it for the entire selector lifetime. 

Example local topology with 3 layers

```
Layer 1          Layer 2          Layer 3

  A1 ─────────►    B1 ─────────►    C1
   └──────────►    B2 ─────────►    C2

  A2 ─────────►    B2 ─────────►    C2
   └──────────►    B3 ─────────►    C3

  A3 ─────────►    B3 ─────────►    C3
   └──────────►    B1 ─────────►    C1
```

## Path selection as a generic pluggable component

Path selection can be treated as an optional pluggable component with the default being random selection. Instead of Sphinx construction embedding the path selection into its internal function, it requests a path from a configured `PathSelector`. Different `PathSelector`-s can be chosen based on the anonymity and communication requirements and assumptions about the mixnet.

The selector type and selector state are local to the initiating node and don't change the encoding of Sphinx packets. A selected path is passed to the existing Sphinx packet-construction procedure defined by the Mix Protocol.

The path selector can be initialized using a config that is `PathSelector`-specific along with the mix node pool which the selector can use when selecting paths:

```
type PathSelector* = ref object of RootObj
    nodePool: MixNodePool
    config: PathSelectorConfig
    rng: CSPRNG
```

The `PathSelector` interface API should expose path selection and return the resulting mix path which will be passed to the normal Sphinx packet-construction procedure. Path selection might require applying some constraints such as fixing some exit hops and excluding the destination from the path. This is especially needed since forward, cover, and surb paths are constructed differently. In general, the path selection function can be abstracted as follows:

```

PathConstraints {
    excludedNodeIds: Set<NodeId>
    fixedHops: Map<HopIndex, MixNode>
}

SelectPath(
    nodePool: MixNodePool
    constraints: PathConstraints
    ...
) -> MixPath
```

Mix requires three path types, and different types result in different strategies and path structures:

```
PathPurpose =
    FORWARD
    SURB
    COVER
```

### forward packets (`FORWARD`)

For forward packets:

```text
purpose = FORWARD
pathLength = L
excludedNodeIds = { destinationId }
```

The selector chooses all L hops. The node at index L - 1 is the exit. A caller can then encode the final destination after that exit. If the exit is the destination, then it can be added to the list of fixed hops as a path selection constraint.

```
fixedHops[L-1] = destinationId
```

### SURB return path (`SURB`)

For a SURB created by the original initiating node:

~~~text
purpose = SURB
pathLength = L
excludedNodeIds = {
    InitiatorId,
    forwardExitId,
    forwardDestinationId
}
fixedHops[L - 1] = InitiatorId
~~~

The selector fills L - 1 positions and the return path terminates at the initiator. `forwardExitId` is the exit node that will receive and use the SURBs. `forwardDestinationId` is the destination node for the forward message, this could also be the same node as the `forwardExitId` when the `exit==destination`.

### Cover loop (`COVER`)

For a cover packet that returns to its origin:

~~~text
purpose = COVER
pathLength = L
excludedNodeIds = { InitiatorId }
fixedHops[L - 1] = InitiatorId
~~~

The selector fills L - 1 positions. Cover traffic path loops back to the initiator as specified in the [mix cover traffic specification](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html). Additionally, cover traffic path selection does not require a specified strategy and can fall back to uniform random selection of mix nodes. Note that future versions of the spec might specify a way to use cover traffic for [path health monitoring](https://lip.logos.co/anoncomms/raw/mix-cover-traffic.html#112-path-health-monitoring). 


### Path validity

The Path selector must validate/ensure the selected path satisfies all of the following:

1. it contains exactly L nodes and satisfies the minimum and maximum supported by the Mix Protocol.
2. every node in the path is present in the mix node pool
3. no node identifier appears more than once.
4. Every node has the addressing and key material required for Sphinx construction.
5. The path meets the conditions defined in `PathConstraints`, see next subsection for more details on this.

### Path constraints

Path constraints need to be handled carefully so as not to help adversary with confirmation attacks, i.e., confirming certain mix nodes are used within the fixed paths. Therefore the path selector must not behave predectibly based on the constraints. For example, path selector failing to produce a path for some destinations/exits would confirm that these destinations/exists are likely used in the path selector state since requests involving that node repeatedly fail. 

As can be seen above, both forward and SURB path creation require excluding the destination and exit addresses. For path selection strategies with fixed nodes or paths, this could lead to failure to create a path where all `L` hops being unique thus confirming to an adversary that it is used by the user/service. Path selector must be able to handle such cases by having alterantive paths/nodes to choose from.

### Path Selector Types

This specification document defines three path selection strategies/modes. A higher-layer protocol may select one of the following:

```text
PathSelectorType =
    RANDOM
    SESSION
    TIME_BASED
```

The selector type determines the lifetime of the path-selection strategy.

| Selector | lifetime | Typical use |
|---|---|---|
| `RANDOM` | One packet | unrelated or short messages |
| `SESSION` | One logical session | anonymous download |
| `TIME_BASED` | Multiple sessions within time `T` | hidden service |

Defining when a session/service starts and ends is done when initializing the path selector.

## Random Path Selection (`RANDOM`)

The random selector follows the current Mix Protocol path-selection behavior. For every path-selection request:

1. obtain the set of eligible live Mix nodes
2. place all `F` caller-fixed hops from `PathConstraints`
3. select $`L-F`$ distinct nodes uniformly at random excluding the nodes from the `exclusionList` and the `fixedNodes`
4. order the selected nodes randomly
5. return the resulting path

No state is maintained between requests. Every packet therefore receives an independently selected path.

For an adversary controlling fraction $`\beta`$ of the eligible Mix pool, the probability that one $`L`$-hop path is fully malicious is approximately

$`
q \approx \beta^L
`$

This is the probability that only a single packet will be de-anonymized. However, if the node sends single packets over time, after $`N`$ independently selected paths, the probability that at least one fully malicious path is selected is approximately:

$`
\texttt{S-DLM}_{\mathrm{Random}}(N)
\approx
1-(1-\beta^L)^N
`$

This is the probability that a user should expect for one of its packets to be deanonymized. The packets do not necessarily need to be sent at the same time and can be separated over time. Random selection provides the highest route diversity among the strategies defined in this document but causes the number of independent malicious-path opportunities to grow with the number of packets.

## Session-Based Path Selection (`SESSION`)

The session selector is intended for applications that generate many logically related Mix packets during a bounded period.

Examples include:

- anonymous downloads
- anonymous uploads
- large request/response exchanges implemented using the Mix transport layer.

The session selector combines fixed-hop selection (similar to the K-HF in the [research post](https://forum.research.logos.co/t/mix-path-selection/721)) with ordered K-sized sets (i.e., the K/W strategy). It follows the fixed-hop approach because fixing one or more hop positions limits the number of opportunities for a session to encounter a fully malicious path. The K-sized sets allow the selector to tolerate realistic node churn without sampling a new node whenever the active fixed node is temporarily unavailable. The set also helps to set an upperbound on the deanonymization probability that we can tolerate, and the session would only be valid as long as we don't exceed this set.

`SessionSelector` can be created at the beginning of the session:

```text
SessionSelector.init(
    config: SessionSelectorConfig,
) -> SessionSelector
```

A distinct session-selector instance must be initialized for each independent session. However, all forward packets, control packets, acknowledgements, and SURBs belonging to the same session must use the same selector instance. The selector instance must be discarded when the session ends and must not be reused by an unrelated session. This prevents the path-selection layer itself from introducing linkability between otherwise independent sessions, although initializing more independent selectors also increases the node's cumulative exposure to new candidates.

### Path selection algorithm
The session-based path selection algorithm takes the following inputs, which can be set as configuration parameters:
- The number of hops in the path: `L`
- The number of fixed hops: `F`
- The size of the set for each fixed hop: `K`

Algorithm steps:

#### 1. Initialize fixed sets
For each fixed position $`j \in \{0..F\}`$, the selector samples an ordered set of $`K`$ distinct candidates:

$`
S_j=(n_{j,1},n_{j,2},\ldots,n_{j,K}).
`$

The first candidate $`n_{j,1}`$ is initially active. The selector stores the candidate sets and active indices in the selector state:

```text
SessionState {
    candidateSets
    activeCandidateIndex
}
```
#### 2. Path construction
For each path request, the selector:

1. places the active candidate for each fixed position into the path
2. If any of the active candidates are offline, replace it with the next available candidate in the candidate set. If none are available, return an error.
3. samples every non-fixed position without replacement from the current eligible Mix pool.
4. excludes all nodes already placed in the path.
5. returns the resulting valid path.

Example with path length $`L=3`$, fixed position 1, and candidate set for position 1 is $`(A,B,C)`$:

```text
packet 1: A -> X -> Y
packet 2: A -> D -> E
packet 3: B -> F -> G   // A unavailabl, B becomes active
packet 4: A -> H -> I  // A is back online
```

The active candidate is only rotated when it is unavailable. When it is back online, it will be the active candidate again. If none of the candidates are online for any of the hop $`K`$ nodes in the set then the session should ends to preserve the anonymity requirement as specified when constructing the path selector.

#### De-anonymization probability

Let $`h_f`$ be the number of fixed positions and let $`\beta_f`$ be the estimated malicious fraction in the pool from which fixed-hop candidates are selected. If no fallback is activated, the approximate session de-anonymization likelihood for $`N`$ paths is

$`
\texttt{S-DLM}_{\mathrm{Session}}(N)
\approx
\beta_f^{h_f}
\left(
1-
\left(1-\beta^{L-h_f}\right)^N
\right)
`$

where $`\beta`$ is the estimated malicious fraction for the remaining positions. For sufficiently large $`N`$, this approaches $`\beta_f^{h_f}`$.

Because we are using the fixed-hop candidate sets for each hop, we can estimate the upper bound for the `DLM` value we expect with this path selection strategy:

$`
\texttt{S-DLM}_{\mathrm{Session}}(N)
\lesssim
\left(1-(1-\beta_f)^K\right)^F
\left(
1-
\left(1-\beta^{L-F}\right)^N
\right)
`$

This formula is a bit conservative for the probability that a session encounters at least one fully malicious path. It has two parts:

$`
\underbrace{\left(1-(1-\beta_f)^K\right)^F}_{\text{malicious candidates in all fixed-hop sets}}
\quad
\underbrace{\left(1-\left(1-\beta^{L-F}\right)^N\right)}_{\text{fully malicious random hops at least once}}
`$

This upper bound is a bit pessimistic because just having a malicious node in a candidate set does not mean that node will become active. This bound assumes that churn or adversarial behavior can eventually cause a malicious candidate in every set to be selected. That assumption might be unrealistic in some cases and nodes in these fixed positions are most likely chosen from a pool of stable/trusted nodes, but it helps to set an upper bound. Realistically, the expected `DLM` is somewhere between the above two formulas.

### Session anonymity profiles
To simplify the anonymity requirement, we can structure it as multiple anonymity profiles. A user can select one of three profiles when initializing the session selector:

```text
SessionProfile =
    LITE
  | STANDARD
  | STRICT
```

- `LITE` favors path diversity and availability by fixing fewer hops and having large candidate sets. It is the least likely to interrupt a session because of unavailable candidates.
- `STANDARD` is the default profile and balances path diversity, availability, and exposure to candidates.
- `STRICT` prioritizes anonymity and limiting exposure to new nodes/candidates at the cost of lower path diversity and a greater chance that the session might end when candidates are unavailable.

Each profile normatively determines:

- the path length $`L`$
- the number of fixed hop positions $`F`$
- the ordered candidate-set size $`K`$
- the liveness, recovery, and what happens when the candidate set is all offline.

The recommended concrete values for these profiles are listed below with estimates of the de-anonymization probability for each profile.

Profile | $`L`$ | $`F`$ | $`K`$ |
|---|---:|---:|---:|
| `LITE` | 3 | 1 | 5 |
| `STANDARD` | 3 | 2 | 5 |
| `STRICT` | 4 | 3 | 3 |

All three profiles use the same policy:

1. each ordered candidate set is initialized once when the session selector is created
2. the selector doesn't extend, replace, or reorder a candidate set during the session
3. for every path request, the selector chooses the first currently eligible candidate in the set's original order
4. if an earlier candidate becomes eligible again after a backup candidate was used, the earlier candidate regains priority.
5. if no candidate is eligible/online at any of the fixed positions, then path selection fails and the session aborts.

Assuming $`\beta_f=0.1`$ and $`N = \infty`$, the resulting probability of de-anonymization for each profile are:

| Profile | $`\texttt{S-DLM}_{\mathrm{Session}}`$ | $`\texttt{S-DLM}_{\mathrm{Session}}`$ upper bound |
|---|---:|---:|
| `LITE` | 0.1 = 10% | 0.41 = 41% |
| `STANDARD` | 0.01 = 1% | 0.17 = 17% |
| `STRICT` | 0.001 = 0.1% | 0.02 = 2% |


## Time-based Path Selection (`TIME_BASED`)

Time-based selection extends selector state across application sessions and possibly across multiple time epochs. Its intended use includes long-lived anonymous identities or services.

The time-based selector defined here maintains a fixed, sparse topology of Mix nodes and a smaller set of active complete paths within that topology. The topology uses a set of somewhat trusted and high-bandwidth nodes possibly supplied by the service which limits cumulative exposure to new nodes. Active paths provide route diversity without independently rotating individual nodes and exposing arbitrary new combinations.

A distinct selector instance is initialized for each long-lived service identity:

```text
TimeBasedSelector.init(
    profile: TimeBasedProfile,
    expiresAt: Timestamp,
    nodePool: MixNodePool,
    rng: CSPRNG
) -> TimeBasedSelector
```

The selector state is shared by all application sessions and path requests associated with that service identity. It must not be shared by unrelated identities. `expiresAt` defines the end of the period $`T`$ for which the selector is valid. The selector takes a set of mix nodes `MixNodePool` which could be provided by the service or randomly selected from the mix network. The pool must be large enough to fill the fixed topology.

### Parameters

Let:

- $`L`$ be the number of consecutive path positions controlled by the time-based selector
- $`K`$ be the number of candidate nodes in each topology layer;
- $`d`$ be the out-degree and in-degree between consecutive layers
- $`M`$ be the number of active complete paths
- $`\mathcal{P}`$ be the set of complete paths allowed by the fixed topology with size $`R=|\mathcal{P}|`$
- $`r_i`$ the rotation time for path $`i`$ in $`\mathcal{P}`$

For the fixed topology:

$`
R=K \cdot d^{L-1}
`$

### Topology initialization

When initialized, the selector:

1. obtains the currently eligible nodes from `MixNodePool`
2. samples $`L`$ disjoint layer sets $`S_1,\ldots,S_L`$, each containing $`K`$ distinct nodes
3. constructs a degree-$`d`$ topology by connecting every pair of consecutive layers
4. enumerates the possible complete paths $`\mathcal{P}`$ through that topology
5. samples $`M`$ distinct active paths uniformly without replacement from $`\mathcal{P}`$
6. assigns every active path an independent rotation time $`r_i`$.

A node identifier appears in at most one topology layer. The selector must enforce the general path validity and supplied constraint rules. The topology construction must give each node exactly $`d`$ outgoing edges to the next layer and exactly $`d`$ incoming edges from the previous layer. An example fixed topology is shown below:

```
               Fixed 5-5-5 topology, degree d=2

      L1                    L2                    L3

     [A1] ───────────────► [B1] ───────────────► [C1]
       └─────────────────► [B2] ───────────────► [C2]

     [A2] ───────────────► [B2] ───────────────► [C2]
       └─────────────────► [B3] ───────────────► [C3]

     [A3] ───────────────► [B3] ───────────────► [C3]
       └─────────────────► [B4] ───────────────► [C4]

     [A4] ───────────────► [B4] ───────────────► [C4]
       └─────────────────► [B5] ───────────────► [C5]

     [A5] ───────────────► [B5] ───────────────► [C5]
       └─────────────────► [B1] ───────────────► [C1]
```

### Path rotation

Every active path has its own independent duration

$`
\tau=\max(X_1,X_2),
\qquad
X_1,X_2\sim U(r_{min},r_{max})\text{ hours}
`$

Based on simulation the recommended rotation values for a lifetime of less than 30 days:

$`
r_{min} = 1 \qquad r_{max} = 48
`$

When an active path expires, the selector:

1. removes that complete path from the active set
2. samples one replacement path uniformly from the set $`\mathcal{P}`$ excluding nodes that are not already active
3. assigns the replacement a newly sampled independent rotation time.

Note: The topology and its nodes remain the same after an active path expires and a previously chosen path may be selected again after expiry since selection is random and the set $`\mathcal{P}`$ is expected to be smaller in size than the expected number of paths requested.

### Path selection

For every path request, the selector:

1. applies `PathConstraints` and removes any active path that does not satisfy them.
2. removes any active path containing a node that is currently offline or unavailable.
3. samples uniformly from the remaining active paths.
4. add any additional hops, e.g. a requested exist node.
5. returns the selected path.

Temporary unavailability should not cause path rotation. If no active path is usable, depending on the availability requirement, the selection fails or an additional path is sampled from the fixed topology and added to the set $`\mathcal{P}`$.

### Time-based anonymity profiles

To simplify the parameters for services/applications, we can define three profiles:

```text
TimeBasedProfile =
    LITE
  | STANDARD
  | STRICT
```

Each profile determines $`L`$, $`K`$, $`d`$, $`M`$, and the rotation values $`r_{min}`$ and $`r_{max}`$

Profile | $`L`$ | $`K`$ | $`d`$ | $`M`$ | num of paths $`R`$ | Path rotation |
|---|---:|---:|---:|---:|---:|---|
| `LITE` | 3 | 5 | 3 | 5 | 45 | $`\max(X_1,X_2)`$, $`X_i\sim U(1,48\text{ h})`$ |
| `STANDARD` | 4 | 5 | 3 | 5 | 135 | $`\max(X_1,X_2)`$, $`X_i\sim U(1,48\text{ h})`$ |
| `STRICT` | 4 | 5 | 2 | 5 | 40 | $`\max(X_1,X_2)`$, $`X_i\sim U(1,48\text{ h})`$ |

- `LITE` uses three fixed topology layers and degree 3.
- `STANDARD` is the recommended default. Its four fixed layers lower the fully malicious-path probability, while degree 3 gives more route diversity.
- `STRICT` keeps the four fixed layers but reduces the degree to 2. It allows fewer routes in exchange for the lowest expected T-DLM.

Simulations with malicious control $`\beta=0.10`$, a 30-day hidden service lifetime, five active paths, and 20,000 trials show the following expected deanonymization probabilities:

| Profile | Sybil | Basic | APT | FVEY | Rubberhose1 | Rubberhose2 |
|---|---:|---:|---:|---:|---:|---:|
| `LITE` | 3.600% | 33.480% | 40.880% | 40.215% | 33.760% | 24.830% |
| `STANDARD` | 0.620% | 19.960% | 36.670% | 39.245% | 17.880% | 7.350% |
| `STRICT` | 0.320% | 17.980% | 36.900% | 37.090% | 16.930% | 6.690% |

where we define these threat models as follows:

| Model | behavior |
| --- | --- |
| `Sybil` | Sybil a percentage $`\beta`$ of the mix nodes |
| `basic` | 50% chance of compromise within 15 days, otherwise never |
| `APT` | 75% within 15 days and 100% by 30 days |
| `FVEY` | 50% within 2 days, 75% within 7 days, otherwise never |
| `rubberhose1` | 50% between 2 and 14 days, otherwise never |
| `rubberhose2` | 50% between 7 and 21 days, otherwise never

## Security Consideration

- The strategies proposed in this document do not define how a node pool establishes that a candidate is trustworthy. Constructing a pool of trusted nodes depends on each service and can be specified in a separate specification document.
- Both session- and time-based selection strategies reduce cumulative exposure within a bounded session or time $`T`$. However, running multiple sessions and operating multiple hidden service instances would increase the probability of deanonymization.
- Repeated use of fixed paths may allow nodes on these paths to infer that they belong to some fixed path. The degree of certainty depends on multiple factors, including traffic volume, path reuse, mixing delays, and the cover-traffic strategy. Further research is required to determine whether this creates a practical side channel.
- Concentrating traffic on a small set of fixed nodes may increase load and create congestion. Nodes selected for fixed paths should provide sufficient bandwidth and are expected to tolerate rate-limit/RLN restrictions. The selector can then choose the appropriate nodes for the mix pool passed to the selector.
- Restricting traffic to a smaller set of paths may also give a global passive adversary (GPA) more opportunities to link observations over time. Mixing and cover traffic may reduce this advantage, but their effectiveness under persistent path reuse requires further research and analysis.
