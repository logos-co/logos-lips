# BEDROCK-ANONYMOUS-LEADERS-REWARD

| Field | Value |
| --- | --- |
| Name | Bedrock Anonymous Leaders Reward Protocol |
| Slug | 85 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomaslavaur@status.im> |
| Contributors | David Rusu <davidrusu@status.im>, Mehmet Gonen <mehmet@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Frederico Teixeira <frederico@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-anonymous-leaders-reward.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-anonymous-leaders-reward.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the mechanism for anonymous reward distribution
based on voucher commitments, nullifiers, and zero-knowledge (ZK) proofs.
Block leaders can claim their rewards
without linking them to specific blocks and without revealing their identities.
The protocol removes any direct link between block production
and the recipient of the reward, preventing self-censorship behaviors.

**Keywords:** anonymous rewards, voucher commitment, nullifier, zero-knowledge proof,
leader reward, Merkle tree, block production, self-censorship

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Definitions

<!-- markdownlint-disable MD013 -->

| Terminology | Description |
| ----------- | ----------- |
| Voucher | A one-time random secret used to claim a block reward anonymously. |
| Voucher Commitment | A cryptographic commitment (zkhash) to a voucher secret. |
| Voucher Nullifier | A unique identifier derived from a voucher, prevents double claims. |
| Leader Claim Operation | A Mantle Operation allowing a leader to claim their reward. |
| Reward Voucher Set | A Merkle tree containing all voucher commitments. |
| Voucher Nullifier Set | A searchable database of nullifiers for claimed vouchers. |
| Anonymity Set | The set of unclaimed vouchers from which a claim could originate. |

<!-- markdownlint-enable MD013 -->

## Background

In many blockchain designs, leaders receive rewards for producing valid blocks.
Traditionally, this reward is linked directly to the block or its producer,
potentially opening the door to manipulation or self-censorship,
where leaders may avoid including certain transactions or messages
out of fear of retaliation or reputational harm.
As Nomos protects its nodes
and ensures that they do not need to engage in self-censorship,
the reward mechanism preserves the anonymity of block leaders
while maintaining correctness and preventing double rewards.

### Design Overview

The protocol introduces a concept of *vouchers*
to unlink the block reward claim from the block itself.
Instead of directly crediting themselves in the block,
leaders include a commitment (a zkhash in this protocol) to a secret voucher.
These commitments are gathered into a Merkle tree.
In the first block of an epoch,
all vouchers from the previous epoch are added to the voucher Merkle tree,
accumulating the vouchers together in a set
and guaranteeing a minimal anonymity set.
Leaders MAY anonymously claim their reward using a ZK proof later,
proving the ownership of their voucher.

```text
┌──────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│ Leader block │───▶│ Reward voucher  │───▶│ Wait until next     │
└──────────────┘    └─────────────────┘    │ epoch               │
                                           └──────────┬──────────┘
                                                      │
                                                      ▼
┌──────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│    Reward    │◀───│ Claim with      │◀───│ Voucher added to    │
│              │    │ ZK proof        │    │ Merkle tree         │
└──────────────┘    └─────────────────┘    └─────────────────────┘
```

By anonymizing the identity of block leaders at the time of reward claiming,
the protocol removes any direct link
between block production and the recipient of the reward.
This is essential to prevent self-censorship behaviors.
With anonymous claiming,
leaders are free to act honestly according to protocol rules
without concern for external consequences,
thus improving the overall neutrality and robustness of the network.

Key properties of the protocol:

- **Anonymity**: Block rewards are unlinkable to the blocks they originate from
  (avoiding deanonymization).
- **Soundness**: No reward can be claimed twice.

In parallel, the blockchain maintains the value `leaders_rewards`
accumulating the rewards for leaders over time.
Each voucher included in the Merkle tree represents the same share of `leaders_rewards`.
Just like for voucher inclusion,
more rewards are added to this variable on an epoch-by-epoch basis,
which guarantees a stable and equal claimable reward for leaders over an epoch.

## Protocol Specification

### Voucher Creation and Inclusion

When producing a block, a leader performs the following:

1. Generate a one-time random secret $voucher \xleftarrow{\$} \mathbb{F}_{p}$.

1. Compute the commitment: `voucher_cm := zkHash(b"LEAD_VOUCHER_CM_V1", voucher)`.

1. Include the `voucher_cm` in the block header.

Each `voucher_cm` is added to a Merkle tree of voucher commitments by validators
during the execution of the first block of the following epoch,
maintained throughout the entire blockchain history by everyone.

### Claiming the Reward

Each leader MAY submit a Leader Claim Operation to claim their reward.
This Operation includes:

- The Merkle root of the global voucher set
  when the Mantle Transaction containing the claim is submitted.
- A Proof of Claim.

This Operation increases the balance of a Mantle Transaction
by the leader reward amount,
letting the leader move the funds as desired
through the Ledger transaction or another Operation.

> **Note**: This means that a leader MAY use their funds directly,
> getting their reward and using them atomically.

Every leader receives a reward that is independent of the block content
to avoid de-anonymization.
This means that the fees of the block cannot be collected by the leader directly,
or need to be pooled for all the leaders.

### Leaders Reward Calculation

At the start of epoch N+1,
validators aggregate the leaders rewards of epoch N into the leader rewards variable.
The amount of the reward claimable with a voucher
corresponds to a share of the `leaders_rewards`.
This share is exactly equal to the total value of rewards
divided by the size of the anonymity set of leaders, that is:

<!-- markdownlint-disable MD013 -->

$$
share = \begin{cases}
0 & \textbf{if } |voucher\_cm| = |voucher\_nf| \\
\frac{leader\_rewards}{|voucher\_cm| - |voucher\_nf|} & \textbf{if } |voucher\_cm| \neq |voucher\_nf|
\end{cases}
$$

<!-- markdownlint-enable MD013 -->

This amount is stable through an epoch
because when a leader withdraws,
both the pool value and the number of unclaimed vouchers decrease proportionally,
so the price per share remains unchanged.
However, the share value will vary across epochs if the leader rewards are variable.

### LEADER_CLAIM Validation

Nodes validate a `LEADER_CLAIM` Operation by:

1. Verifying the ZK proof.

1. Checking that `voucher_nf` is not already in the voucher nullifier set.

1. Executing the reward logic:
   - Add the `voucher_nf` to the voucher nullifier set
     to prevent claiming the same reward more than once.
   - Increase the balance of the Mantle Transaction by the share amount.
   - Decrease the value of the `leaders_rewards` by the same amount.

## Design Details

### Unlinking Block Rewards from Proposals

Each reward voucher is a cryptographic commitment derived from a voucher secret.
This commitment, when included in the block header,
reveals no information about the block producer's identity
or the actual secret voucher.
It is computationally infeasible to reverse the commitment
to retrieve the voucher secret.

Crucially, when the leader reward is claimed and the voucher nullifier revealed,
a third party cannot link this nullifier to the initial voucher commitment.
A reward is claimable if its reward voucher is in the reward voucher set
and its voucher nullifier is not in the voucher nullifier set.

The reward voucher set is maintained as a Merkle tree of depth 32,
and validators are required to hold the frontier of the MMR in memory
to continue appending to the set.
The voucher nullifier set is maintained as a searchable database.

### ZK Proof of Membership

When claiming a reward, the leader provides a ZK proof
that they know a leaf in the global Merkle tree of reward vouchers
and the preimage of that leaf.
Crucially, the ZK proof does not reveal which leaf is being proven.
The verifier only learns that *some* valid leaf exists in the tree
for which the prover knows the secret voucher.
This property ensures that the claim cannot be linked
to any specific block header or reward voucher commitment.

### Preventing Double Claims Without Breaking Privacy

To prevent double claiming, the leader derives a voucher nullifier.
This nullifier is unique to the voucher
but reveals nothing about the original reward voucher or block.
It acts as a one-way identifier
that allows nodes to track whether a voucher has already been claimed,
without compromising the anonymity of the claim.

## Security Considerations

### Anonymity Guarantees

The protocol provides anonymity through the following mechanisms:

- Voucher commitments reveal no information about the block producer's identity.
- ZK proofs do not reveal which leaf in the Merkle tree is being claimed.
- Nullifiers cannot be linked back to voucher commitments.

The anonymity set size is determined by the number of unclaimed vouchers.
Implementations SHOULD ensure a sufficient anonymity set size
before allowing claims to prevent timing-based deanonymization attacks.

### Double Claim Prevention

The nullifier mechanism ensures that each voucher can only be claimed once.
Nodes MUST verify that a nullifier is not in the voucher nullifier set
before accepting a `LEADER_CLAIM` Operation.

### Reward Independence

Leaders receive a reward independent of block content
to prevent correlation attacks based on block fees or transaction patterns.

## References

### Normative

- [BEDROCK-MANTLE-SPECIFICATION][mantle] - Mantle Transaction and Operation specification

### Informative

- [Anonymous Leaders Reward Protocol][origin-ref] - Original specification document

[mantle]: https://nomos-tech.notion.site/v1-1-Mantle-Specification-269261aa09df80dda501f568697930fd
[origin-ref]: https://nomos-tech.notion.site/Anonymous-Leaders-Reward-Protocol-206261aa09df8120a49ffa49c71ba70d

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
