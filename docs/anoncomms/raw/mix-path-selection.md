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

**Mix Node Adversary (MNA).** An adversary that controls a fraction $`\beta`$ of the eligible Mix nodes. A path is considered fully compromised when every Mix node on the relevant path is controlled by the adversary.

**Adaptive adversary (AA).** An adversary that may compromise additional Mix nodes over time and may choose which nodes to target based on information learned from previously compromised nodes. This includes attacks against persistent paths or topologies in which the adversary attempts to progressively compromise nodes toward an endpoint.

### the de-anonymization likelihood metric (`DLM`)
The metric we use to measure the expected anonymity provided by each path selection mode is the de-anonymization likelihood metric (`DLM`). This metric was introduced in the [NDSS paper](https://www.ndss-symposium.org/wp-content/uploads/2026-f2384-paper.pdf) and we use it with some slight modifications:
- **packet-based DLM (P-DLM)** is the probability that a single selected path is fully controlled by the adversary.
- **session-based DLM (S-DLM)** is the probability that at least one packet in a session uses a fully compromised path.
- **time-based DLM (T-DLM)** is the probability that a long-lived identity or service becomes deanonymized during a time period `T`.


### Path selection strategy
A path-selection strategy is a way to construct a Mix path from the currently eligible Mix nodes. A strategy may be stateless, or it may maintain a local state in order to reuse selected nodes/paths across multiple path requests.

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

This specification defines three path selection strategies/modes. A higher-layer protocol may select one of the following:

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
3. select $`R = L-F`$ distinct nodes uniformly at random excluding the nodes from the `exclusionList` and the `fixedNodes`
4. order the selected nodes randomly in the remaining $`R`$ hops
5. return the resulting path

No state is maintained between requests. Every packet therefore receives an independently selected path.

For an adversary controlling fraction $`\beta`$ of the eligible Mix pool, the probability that one $`L`$-hop path is fully malicious is approximately

$`
\texttt{P-DLM} \approx \beta^R
`$

Where $`R = L-F`$ is the number of randomly selected intermediary Mix nodes. Fixed hops are not counted as independently sampled intermediaries. For intance, $`R=L`$ for a forward path with a separate destination, while $`R=L-1`$ when the destination is also the exit (`exit==destination`). $`\texttt{P-DLM}`$ is the probability that only a single packet will be de-anonymized. However, if a mix node sends packets over time, after $`N`$ independently selected paths, the probability that at least one fully malicious path is selected is approximately:

$`
\texttt{P-DLM}(N)
\approx
1-(1-\beta^R)^N
`$

This is the probability that a user should expect for one of its packets to be deanonymized. The packets do not necessarily need to be sent at the same time and can be separated over time. Random selection provides the highest route diversity among the strategies defined in this document but causes the number of independent malicious-path opportunities to grow with the number of packets.

## Session-Based Path Selection (`SESSION`)

The session selector is intended for applications that generate many related Mix packets during a short period of time.

Examples include:

- anonymous downloads
- anonymous uploads
- large request/response exchanges implemented using the Mix transport layer.

The session selector combines fixed-hop selection (similar to the K-HF in the [research post](https://forum.research.logos.co/t/mix-path-selection/721)) with ordered K-sized sets (i.e., the K/W strategy). It follows the fixed-hop approach because fixing one or more hop positions limits the number of opportunities for a session to encounter a fully malicious path. The K-sized sets allow the selector to tolerate realistic node churn without sampling a new node whenever the active fixed node is temporarily unavailable. An example of 2 fixed hops, each fixed hop containing a set of nodes $`S`$ of size $`K`$, with a third hop $`R`$ chosen at random: 

```
Sender -> [S_1] -> [S_2] -> R -> receiver
```

We can use the notation X-X-...-R, where X is the size of the set. e.g., 5-5-R would mean 3 hops, two fixed each with 5 possible nodes to select from, and a third hop with a random node sampled from the mix network. The set of mix nodes for fixed hop set could come from a trusted pool chosen by the user and it also helps to set an upperbound on the deanonymization probability that we can tolerate. The session would only be valid as long as we don't exceed this set.

A distinct session-selector instance must be initialized for each independent session. However, all forward packets, control packets, acknowledgements, and SURBs belonging to the same session must use the same selector instance. The selector instance must be discarded when the session ends and must not be reused by an unrelated session. This prevents the path-selection layer itself from introducing linkability between otherwise independent sessions, although initializing more independent selectors also increases the node's cumulative exposure to new candidates.

### Path selection algorithm
The session-based path selection algorithm takes the following inputs, which can be set as configuration parameters:
- The number of hops in the path: $`L`$
- The number of fixed hops: $`L_f`$
- The size of the set for each fixed hop: `K`

Algorithm steps:

#### 1. Initialize fixed sets
For each fixed position $`j \in \{1, \cdots ,L_f\}`$, the selector samples a set of $`K`$ distinct candidates:

$`
S_j=(n_{j,1},n_{j,2},\ldots,n_{j,K}).
`$

The selector stores the candidate sets $`\{S_0,\cdots,S_{L_f} \}`$ in the selector state:

```text
SessionState {
    candidateSets
}
```

#### 2. Path construction
For each path request, the selector:

1. places any $`F`$ caller-fixed hops specified by `PathConstraints` at their required positions
2. For each $`L_f`$ session-fixed hops, first filter candidate set to exclude offline, nodes in the exclusion list, and nodes already placed in the path.
3. Select one candidate uniformly at random from each filtered set, ensuring that no node appears more than once.
4. Fill any the remaining $`r`$ random positions by sampling uniformly from the Mix pool, excluding nodes from `PathConstraints` or already placed in the path.
5. Returns the path after checking the general path-validity requirements.

If none of the candidates are usable/online in any of the sets then the session should ends to preserve the anonymity requirement as specified when constructing the path selector.

#### De-anonymization probability

Let:
- $`L_f`$ be the number of fixed positions 
- $`\beta_f`$ be the estimated malicious fraction in the pool from which fixed-hop candidates are selected. 
- $`\beta`$ be the estimated malicious fraction

The upper bound for session de-anonymization likelihood for $`N`$ paths is:

$`
\texttt{S-DLM}(N)
\lesssim
\left(1-(1-\beta_f)^K\right)^{L_f}
\left(
1-
\left(1-\beta^{L-{L_f}}\right)^N
\right)
`$

This formula is a bit conservative for the probability that a session encounters at least one fully malicious path. It has two parts:

$`
\underbrace{\left(1-(1-\beta_f)^K\right)^{L_f}}_{\text{malicious candidates in all fixed-hop sets}}
\quad
\underbrace{\left(1-\left(1-\beta^{L-{L_f}}\right)^N\right)}_{\text{fully malicious random hops at least once}}
`$

For arbitrarily many paths, this simplifies to:


$`
\lim_{N\to\infty}\texttt{S-DLM}(N)
\approx
\left[1-(1-\beta_f)^K\right]^{L_f}
`$


### Session anonymity profiles
To simplify the anonymity requirement, we can structure it as multiple anonymity profiles. A user can select one of three profiles when initializing the session selector:

```text
SessionProfile =
    LITE
  | STANDARD
  | STRICT
```

- `LITE` favors path diversity and availability by fixing fewer hops and having large candidate sets. It is the least likely to interrupt a session because of unavailable candidates.
- `STANDARD` is the default profile and balances path diversity, availability, and exposure to malicious candidates.
- `STRICT` prioritizes anonymity and limiting exposure to new nodes/candidates at the cost of lower path diversity and a greater chance that the session might end when candidates are unusable/offline.

Each profile determines:

- the path length $`L`$
- the number of fixed hop positions $`L_f`$
- the candidate-set size $`K`$

The recommended concrete values for these profiles are listed below with estimates of the de-anonymization probability for each profile.

Profile | $`L`$ | $`L_f`$ | $`K`$ |
|---|---:|---:|---:|
| `LITE` (`5-R-R`) | 3 | 1 | 5 |
| `STANDARD` (`5-5-R`) | 3 | 2 | 5 |
| `STRICT` (`3-3-3-R`) | 4 | 3 | 3 |

All three profiles use the same policy:

1. each candidate set is initialized once when the session selector is created
2. the selector doesn't extend, replace, or reorder a candidate set during the session
3. for every path request, the selector follows the path selection algorithm specified earlier
4. if no candidate is usable/online at any of the fixed positions, then path selection fails and the session aborts.

Assuming $`\beta_f=0.1`$ and $`N = \infty`$, the resulting probability of de-anonymization for each profile are:


| Profile | $`\texttt{S-DLM}`$ |
|---|---:|
| `LITE` (`5-R-R`) | 41% |
| `STANDARD` (`5-5-R`) | 17% |
| `STRICT` (`3-3-3-R`) | 2% |

## Time-based Path Selection (`TIME_BASED`)

Time-based selection extends selector state across application sessions, all within some bounded service lifetime $`T`$. Its intended use includes long-lived anonymous identities or services.

The time-based selector specified here maintains a fixed, sparse topology of Mix nodes and a smaller set of active complete paths within that topology. The topology uses a set of somewhat trusted and high-bandwidth nodes possibly supplied by the service which limits cumulative exposure to new nodes. Active paths provide route diversity without independently rotating individual nodes and exposing arbitrary new combinations.

A distinct selector instance is initialized for each long-lived service identity:

```text
TimeBasedSelector.init(
    profile: TimeBasedProfile,
    expiresAt: Timestamp,
    nodePool: MixNodePool,
    ...
) -> TimeBasedSelector
```

The selector state is shared by all application sessions and path requests associated with that service identity. It must not be shared by unrelated identities. `expiresAt` defines the end of the period $`T`$ for which the selector is valid. The selector takes a set of mix nodes `MixNodePool` which could be provided by the service or randomly selected from the mix network. The pool must be large enough to fill the fixed topology.

### Parameters

Let:

- $`L_f`$ be the number of consecutive path positions controlled by the time-based selector and does not include called-supplied fixed hops, i.e., $`L_f \le L`$.
- $`K`$ be the number of candidate nodes in each topology layer
- $`d`$ be the number of distinct outgoing connections from each node in a layer (expect the last) to the next layer
- $`M`$ be the number of active complete paths
- $`R`$ be the size of the set containing random rotating mix nodes
- $`\mathcal{P}`$ be the set of complete paths allowed by the fixed topology with size $`A=|\mathcal{P}|`$
- $`\tau_i`$ the rotation time for path $`i`$ in $`\mathcal{P}`$

For the fixed topology:

$`
A=K \cdot d^{L-1}
`$

and for mesh:
$`
A=K^{L_f}
`$

### Topology initialization

When initialized, the selector:

1. obtains the currently eligible nodes from `MixNodePool`
2. samples $`L`$ layer sets $`S_1,\ldots,S_L`$, each containing $`K`$ distinct nodes
3. constructs the configured mesh or degree-$`d`$ topology by connecting every pair of consecutive layers. Neighbor selection prefers nodes that have not yet received an incoming edge so that the resulting topology must give every internal candidate at least one complete route
4. assigns each node in the topology a lifetime based on the policy of its layer
5. enumerates the possible complete paths $`\mathcal{P}`$ through that topology
6. samples $`M`$ distinct active paths uniformly without replacement from $`\mathcal{P}`$, ensuring that no single node is present in all $`M`$ paths
7. assigns every active path an independent rotation time $`\tau_i`$


A node identifier appears in at most one topology layer. The selector must enforce the general path validity and supplied constraint rules. The topology construction must give each node exactly $`d`$ outgoing edges to the next layer. An example fixed topology is shown below:

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
X_1,X_2\sim U(\tau_{min},\tau_{max})\text{ hours}
`$

Based on simulation the recommended rotation values for a service lifetime of less than 30 days:

$`
\tau_{min} = 1 \qquad \tau_{max} = 48
`$

When an active path expires, the selector:

1. removes that complete path from the active set
2. samples one replacement path uniformly from the set $`\mathcal{P}`$ excluding path that are already active
3. assigns the replacement a newly sampled independent rotation time ($`\tau`$).

*Notes: 
- Path rotation does not change topology nodes, connections, or node-expiry timers.
- A previously chosen path may be selected again after expiry since selection is random and the set $`\mathcal{P}`$ is expected to be smaller in size than the expected number of paths requested.

### Node rotation

All nodes in a layer share the same lifetime policy, but sample their durations independently. Depending on the selector strategy/profiles, nodes lifetimes in some layers may or may not have an expiry. 

When a node with a lifetime expires, the selector:

1. samples a replacement uniformly from eligible nodes outside the current topology excluding nodes that used in the current local topology
2. places the replacement in the same layer and same index (this helps fixed paths stay consistent).
3. all incoming and outgoing connections of that layer and index are preserved
4. the replacement's lifetime is sampled based on the layer's policy

Every active path using that slot immediately resolves to the replacement node since its placed in the same layer and index. The active path-expiry timers remain unchanged.

### Path selection

For every path request, the selector:

1. applies `PathConstraints` and removes any active path that does not satisfy them.
2. removes any active path containing a node that is currently offline or unavailable.
3. samples uniformly from the remaining active paths.
4. add any additional hops, e.g. a requested exist node.
5. returns the selected path.

Note: removal above refer to removal from sampling for a given request. Temporary unavailability should not cause path rotation or node replacement. If no active path is usable, depending on the availability requirement, the selection fails or an additional path is sampled from the fixed topology and added to the set $`\mathcal{P}`$.

### Time-based anonymity profiles

To simplify the parameters for services/applications, we can define three profiles:

```text
TimeBasedProfile =
    LITE
  | STANDARD
  | STRICT
```

Each profile determines $`L_f`$, $`K`$, $`d`$, $`M`$, and the rotation values $`\tau_{min}`$ and $`\tau_{max}`$. $`R`$ refers to a hop with random mix node sampled from the mixnet, whereas, $`R5`$ refers to a fixed set of randomly selected mix nodes, each with independet lifetime sampled from the same $`\tau_{min}`$ and $`\tau_{max}`$ range.

Profile | $`L_f`$ | $`K`$ | $`d`$ | $`M`$ | $`R`$ | num of fixed nodes | Path rotation ($`\tau_{min}`,`\tau_{max}`$) |
|---|---:|---:|---:|---:|---:|---:|---| 
| `LITE` (`5_5_R`) | 3 | 5 | mesh | 5 | 0 | 10 | $`(1,48)`$ hours |
| `STANDARD` (`5_5_R5`) | 3 | 5 | 3 | 5 | 5 | 10 | $`(1,48)`$ hours |
| `STRICT` (`5_5_5_R5`) | 4 | 5 | 3 | 5 | 5 | 15 | $`(1,48)`$ hours |

Profile | $`L_f`$ | Connections | $`M`$ | Permanent nodes | Rotating nodes |
|---|---|---:|---|---:|---:|
| `LITE` (`5_5_R`) | 3 | Mesh | 5 | 10 | 0 | 
| `STANDARD` (`5_5_R5`) | 3 | Degree 3 | 5 | 10 | 5 |
| `STRICT` (`5_5_5_R5`) | 4 | Degree 3 | 5 | 15 | 5 |


- `LITE` uses 2 fixed topology layers, mesh connections between layers, and 5 active paths. The third hop is randomly selected from the mix pool. 
- `STANDARD` is the default. It has 2 fixed layers with degree 3, however, it's random third hop uses a fixed set of 5 nodes each with it's own independent lifetime. 
- `STRICT` uses the same structure as `STANDARD` but with 3 fixed layer instead of 2 to resist sybil and path walking attacks for a longer period of time. The three fixed layers would mean that this profile requires more trusted nodes (15 nodes).

`STANDARD` and `STRICT` place an additional fixed layer of rotating nodes $`R5`$ at the client-facing side. The purpose of $`R5`$ layer is to incentivize the adversary to sybil that layer and give the service more time to operate. This is because exit nodes are sampled from the general mixnet pool and rotate slowly, therefore, making it more attractive for the adversary to sybil attack instead of the more expensive compromise attack. Additionally, rotation limits how long a sybiled exit remains useful in its position, potentially reducing the usefulness of compromises that finish after it rotates.

The $R5$ layer follows these rules:
- Initialize five distinct nodes, excluding all nodes in the other layers.
- Assign each node an independent lifetime equal to the maximum of two uniform draws between 1-48 hours.
- Connect the preceding layer to $R5$ using the topology's configured degree.
- When a node expires, replace it with a uniformly selected eligible node outside the current topology. The replacement inherits the connections and active paths the used the expired node.
- Keep node and path timers independent: replacing a node does not reset path timers, and rotating a path does not reset node timers.

#### De-anonymization probability

To estimate the $`\texttt{T-DLM}`$ value for each profile, we used the [mixpathsim](https://github.com/logos-storage/hs-mix-sim) simulator. Simulations with malicious control $`\beta=0.10`$, a 30-day hidden service lifetime, five active paths, and 5,000 trials show the following expected $`\texttt{T-DLM}`$ and median time to service identification.`NR` means that the 50% threshold was not reached within the 30-day observation period.

| Profile | Sybil only | Basic | APT | FVEY | Rubberhose1 | Rubberhose2 |
|---|---:|---:|---:|---:|---:|---:|
| `LITE` (`5_5_R`) | 16.60% / NR | 48.34% / NR | 84.36% / 14.39 d | 72.54% / 5.64 d | 48.96% / NR | 43.42% / NR |
| `STANDARD` (`5_5_R5`) | 10.10% / NR | 27.62% / NR | 44.30% / NR | 55.52% / 24.04 d | 26.82% / NR | 20.56% / NR |
| `STRICT` (`5_5_5_R5`) | 1.52% / NR | 6.84% / NR | 12.44% / NR | 24.46% / NR | 6.10% / NR | 3.90% / NR |


where we define these adversary models (following Tor's naming convention here) as follows:

| Model | behavior |
| --- | --- |
| `Sybil` | Sybil a percentage $`\beta`$ of the mix nodes |
| `basic` | 50% chance of compromise within 15 days, otherwise never |
| `APT` | 75% within 15 days and 100% by 30 days |
| `FVEY` | 50% within 2 days, 75% within 7 days, otherwise never |
| `rubberhose1` | 50% between 2 and 14 days, otherwise never |
| `rubberhose2` | 50% between 7 and 21 days, otherwise never


The suggested lifetime `T` for hidden service using each of these profiles considering the strogest adversary model (FVEY):

Profile | measured median lifetime | Suggested lifetime range |
|---|---|---|
| `LITE` (`5_5_R`) | 5.64 days | 1-5 days | 
| `STANDARD` (`5_5_R5`) | 24.04 days | 1-15 days |
| `STRICT` (`5_5_5_R5`) |  NR | 1-30 days |

## Security Consideration

- The strategies proposed in this document do not define how a user/service establishes that a candidate is trustworthy. Constructing a pool of trusted nodes depends on each user/service and can be specified in a separate specification document.
- Both session- and time-based selection strategies reduce cumulative exposure within a bounded session or time $`T`$. However, running multiple sessions and operating multiple hidden service instances would increase the probability of deanonymization. For users expecting multiple sessions within some bounded it, it might make sense to use the time-based selection strategy as it would reduce the cumulative exposure at the cost of possibly linking these sessions. 
- Repeated use of fixed paths may allow nodes on these paths to infer that they belong to some fixed path. The degree of certainty depends on multiple factors, including traffic volume, path reuse, mixing delays, and the cover-traffic strategy. Further research is required to determine whether this creates a practical side channel.
- Concentrating traffic on a small set of fixed nodes may increase load and create congestion. Nodes selected for fixed paths should provide sufficient bandwidth and are expected to tolerate rate-limit/RLN restrictions. The selector can then choose the appropriate nodes for the mix pool passed to the selector.
- Restricting traffic to a smaller set of paths may also give a global passive adversary (GPA) more opportunities to link observations over time. Mixing and cover traffic may reduce this advantage, but their effectiveness under persistent path reuse requires further research and analysis.


## References:

- [Reference implementation and simulation](https://github.com/logos-storage/hs-mix-sim)
- [Path selection strategies for anonymous download](https://forum.research.logos.co/t/mix-path-selection/721)
- [Time-based path selection](https://forum.research.logos.co/t/hidden-service-time-based-path-selection/730) 
- [Hidden services](https://forum.research.logos.co/t/hidden-service-time-based-path-selection/730/1)