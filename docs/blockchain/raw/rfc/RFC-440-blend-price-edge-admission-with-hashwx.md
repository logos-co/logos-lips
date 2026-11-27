# [RFC] Blend: Price edge admission with HashWX

**Motivation and proposal:** [PR #440](https://github.com/logos-co/logos-lips/pull/440)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC. A core node prices its edge share with HashWX. It replaces the PR's earlier design, which priced admission by the measured load with Equi-X and also had nodes report their load to set the Blend difficulty | 2026-11-27 |

## Reviewer Orientation

Read the PR's Motivation first.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here** — [Blend Protocol](#affected-specifications), [Edge Admission](#1-edge-admission) | the challenge, the quote and the nonce on the edge stream; the three checks and the spent-nonce cache |
| 2 | Critical | **Start here** — [Common Cryptographic Components](#affected-specifications), [HashWX](#5-hashwx) | the ticket of a nonce for a challenge; 463 nonces per seed; `HASHWX_MACHINE_RATE`; the test values |
| 3 | High | [Blend Protocol](#affected-specifications), [Edge Difficulty](#2-edge-difficulty) | each node's price retarget on distinct presentations |
| 4 | High | [Blend Protocol](#affected-specifications), [the parameters](#3-the-parameters) | `price^Min`, `price^Max`, `G` and `T_R`, each with its constraint |
| 5 | High | [Blend Protocol](#affected-specifications), [the connection](#4-the-connection) | protocol name `2.0.0`; `T_E` covers the quote and the nonce |

# Discussion

## Why a price at the edge

A core node serves at most $`r_E`$ = 24 edge connections a round, and connecting costs an edge node nothing. So anyone can take a node's whole edge share for free. A proof-of-work price makes the share cost work, and each node sets the price from the demand it meets. A refused edge node, a block proposer among them, can pay and come back.

## Why HashWX

HashWX is a client puzzle: a 64-bit nonce whose ticket must fall below a 64-bit target. It builds a new program for every 463 nonces and runs it over a 16 KB scratchpad, so solving stays on general-purpose processors. Checking a nonce costs one ticket at every price, and the nonce adds 8 bytes to the stream. The PR first proposed Equi-X, which its author deprecated on 2026-10-15.

## The bounds of the price

- $`\text{price}^{Min} = \lfloor 20 \cdot R_F / r_E \rfloor`$ = 358,333 hashes. At that price, filling one node's edge share takes twenty cores of the fastest solver measured, an Intel Core Ultra 9 285HX at $`R_F`$ = 430,000 hashes a second per core.
- $`\text{price}^{Max} = \lfloor T_M \cdot \text{HASHWX\_MACHINE\_RATE} / 6 \rfloor`$ = 2,425,000 hashes. Three solves, the reference value of $`\Phi_{EC}`$, then take $`T_M / 2`$ on average on all four cores of a Raspberry Pi 5, the target machine. Their mean must stay below $`T_M`$, or an edge node that solves at its slot releases its proposal later than a message crosses the network.
- $`G = 4 \cdot T_M`$ = 60 rounds is at least the 95th percentile of the solving time at $`\text{price}^{Max}`$ on one core of the target machine, 30 rounds. So a solver that began against a quoted price is not refused when it finishes.

The measurements behind $`R_F`$ and `HASHWX_MACHINE_RATE` are in the [HashWX benchmark](https://github.com/logos-blockchain/research/blob/hashwx-benchmark/reports/EmPoWering/HashWX/findings.md).

## The retarget

A node counts distinct pairs of a challenge and a nonce. A replayed nonce therefore cannot raise its price. The price doubles above twice the nonces the node can serve and falls by a quarter below what it can serve. So it rises fast under a flood and falls slowly back.

## Open questions

- **Audit.** No audit of HashWX is known. A weak instance would make tickets cheap and lower the price.
- **Graphics cards.** The GPU figures come from the author's non-public solver, and nobody has reproduced them.
- **Slots.** A silent connection holds one of the $`\Phi_{CE}^{Max}`$ edge slots for $`T_E`$, at the cost of a TLS handshake. The price covers the edge share but not the slots.
- **Checks per round.** No rule bounds the checks a node runs in a round. A garbage nonce costs two tickets.
- **No acknowledgement.** An edge node cannot tell a served connection from one refused at check 3 once its message is written.
- **Restarts.** A restart empties the spent-nonce cache while the two challenges stay valid. Up to $`2 \cdot r_E \cdot T_R`$ = 28,800 spent nonces can then be served again, within the share.
- **Licence.** The known implementations of HashWX are under the LGPL, which the node's licence policy does not allow. A permissive reimplementation is planned.
- **The author's caution.** HashWX's author advises against using it for proof-of-work consensus. Here it prices admission.

## Compatibility

The edge stream gains a quote and a nonce, so the libp2p protocol name moves to `/logos-blockchain/blend/2.0.0` for mainnet and `/logos-blockchain-testnet/blend/2.0.0` for testnet. Bedrock has no genesis yet, so the change needs no migration.

# Details

## 1. Edge Admission

A core node serves an edge connection only against a HashWX nonce that satisfies its price. A price $`x`$ gives the target $`\lfloor 2^{64} / x \rfloor`$. The challenge of node $`n`$ for the window $`w = \lfloor t / T_R \rfloor`$ is:

$$
\text{challenge}_n^w = H(\text{"BLEND\_EDGE\_V1"} \| provider\_id_n \| epoch\_nonce_e \| w)
$$

On the edge stream, the core node sends its **edge quote**: the price as 4 bytes, then $`w`$ as 8 bytes, both little-endian. The edge node sends its nonce as 8 bytes little-endian, then its message. It need not wait for the quote. It closes the connection if the quoted price lies outside $`[\text{price}^{Min}, \text{price}^{Max}]`$, or if it holds no nonce that satisfies it. It releases a message, for Detection, in the round it first sends it with a nonce.

The core node serves the connection when these hold, in order:

1. The ticket of the nonce for $`\text{challenge}_n^w`$, or for $`\text{challenge}_n^{w-1}`$ when $`w \gt 0`$, is below the target of the lowest price of the past $`G`$ rounds.
2. The pair of that challenge and the nonce is not in the spent-nonce cache.
3. Fewer than $`r_E`$ edge connections have been served in the current round.

The cache holds the pairs of the current and the previous window, at most $`2 \cdot r_E \cdot T_R`$ entries. The cache check, the insertion and the count are one indivisible step. A refusal at check 3 attributes nothing to the peer. A restarted node holds no pairs and returns to $`\text{price}^{Min}`$.

## 2. Edge Difficulty

Each core node sets $`\text{price}_n`$, an unsigned 32-bit integer, starting at $`\text{price}^{Min}`$. Every $`W`$ rounds, with $`P_n`$ the distinct pairs that passed checks 1 and 2 over those rounds:

1. If $`P_n \gt 2 \cdot r_E \cdot W`$, then $`\text{price}_n \leftarrow \min(2 \cdot \text{price}_n,\ \text{price}^{Max})`$.
2. If $`P_n \lt r_E \cdot W`$, then $`\text{price}_n \leftarrow \max(\lfloor 3 \cdot \text{price}_n / 4 \rfloor,\ \text{price}^{Min})`$.
3. Otherwise it is unchanged.

A node holds at most $`2 \cdot r_E \cdot W + 1`$ pairs for this count.

## 3. The parameters

Blend's global parameters gain:

- $`T_R`$ = 600 rounds, the challenge rotation period. It must divide $`E`$ and be at least $`G`$.
- $`R_F`$ = 430,000 hashes a second, one core of the 285HX with all 24 cores busy, rounded down from the 431,000 measured.
- $`\text{price}^{Min}`$, which must be at least 2 and below $`\text{price}^{Max}`$.
- $`\text{price}^{Max}`$, which must be below $`2^{31}`$ so that doubling a price fits 32 bits.
- $`G = 4 \cdot T_M`$ = 60 rounds, the price grace window.

The notation gains $`\text{price}_n`$, $`P_n`$ and $`R_F`$.

## 4. The connection

- The libp2p protocol name becomes `/logos-blockchain/blend/2.0.0`, and `/logos-blockchain-testnet/blend/2.0.0` on testnet.
- $`T_E`$ covers the edge quote and the nonce, 20 bytes more, still within one round.
- A core node *serves* at most $`r_E`$ edge connections in a round, through Edge Admission. Only a connection above $`\Phi_{CE}^{Max}`$ is closed on arrival.

## 5. HashWX

Common Cryptographic Components defines HashWX v1.0.0 once, for every protocol that uses it:

```python
HASHWX_NONCES_PER_SEED: uint64 = 463

def hashwx_ticket(challenge: bytes, nonce: uint64) -> uint64:
    group = nonce // HASHWX_NONCES_PER_SEED
    seed = Hash(challenge + group.to_bytes(8, "little"))  # 32-byte output
    return hashwx_exec(hashwx_make(seed), nonce)
```

- A nonce satisfies a target $`T`$ when its ticket is below $`T`$. Finding one takes $`2^{64} / T`$ hashes in expectation.
- `HASHWX_NONCES_PER_SEED` must stay 463. A larger value gives a GPU more nonces over which to recover the cost of compiling a function.
- `HASHWX_MACHINE_RATE` is 970,000 hashes a second: all four cores of a Raspberry Pi 5, rounded down from the 977,000 measured.
- A ticket must not be used as an identifier, and a protocol that uses the puzzle enforces single use.
- Test values give the seed and the ticket for nonces 0, 462 and 463.

## Chores

- A round is numbered by its slot.
- The edge flows say that an edge proposer pays each core node's price.
- "Accepts" becomes "serves" for edge connections throughout.

# Implementation

- [ ] Implement HashWX under a licence the node's policy allows.
- [ ] Derive each window's challenge, send the edge quote, and read the nonce before the message on the edge stream, under protocol `2.0.0`.
- [ ] Run the three checks in order as one indivisible step, with a spent-nonce cache bounded by $`2 \cdot r_E \cdot T_R`$.
- [ ] Retarget the price every $`W`$ rounds on distinct pairs, holding at most $`2 \cdot r_E \cdot W + 1`$ of them, and reset it on restart.
- [ ] In the edge node, solve for the quoted window, close on a price outside the bounds, and release at the first send with a nonce.
- [ ] Add tests: the HashWX test values, compiled and interpreted modes returning the same ticket, nonces 462 and 463 using different seeds, the price bounds, and the retarget up and down.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Blend Protocol](../blend-protocol.md) | Modified | Revision 1.9.0 |
| [Common Cryptographic Components](../common-cryptographic-components.md) | Modified | Revision 1.3.0 |
