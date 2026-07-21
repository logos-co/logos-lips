# [RFC] Improve Mantle Transaction hash

This RFC follows an older schema and will be updated when time allows.

**Authors:** Thomas Lavaur
**Approvals (research):** Marcin Pawlowski
**Approvals (engineering):** Daniel Sanchez Quiros, Youngjoon Lee

---

## Motivation

As Mantle Transactions grow (notably with large `CHANNEL_INSCRIBE` Operations), computing `ZkHash` over the whole transaction becomes a noticeable cost during transaction construction and verification. This RFC proposes a small change that preserves the use of `ZkHash` while reducing the amount of data hashed inside the circuit.

## Proposal

In version [Mantle](../../../deprecated/v1.2.0-mantle.md), the Mantle Transaction hash is defined as the `ZkHash` of the entire Mantle Transaction, excluding the Ledger Transaction proof and the Operation proofs.
Currently we perform a zero-knowledge hashing on a Mantle Transaction (without proofs):
`tx_hash = ZkHash(mantle_tx_without_proofs)`.
However, execution of this hashing algorithm is time consuming and grows with the size of the input. Therefore, we propose instead hashing the Mantle Transaction using the classic hash defined in [Common Cryptographic Components](../../common-cryptographic-components.md), then hashing the result with `ZkHash`:
`tx_hash = ZkHash(classic_hash(mantle_tx_without_proofs))`,
where `classic_hash()` is the classic hash defined in [Common Cryptographic Components](../../common-cryptographic-components.md).

## Justification

The proposed change speeds up computation of the Mantle Transaction hash by moving most of the work out of `ZkHash` and into a classic hash, while still committing to the result inside `ZkHash`. This becomes an issue as Mantle Transactions grow, since hashing can take a substantial amount of time (for example, if the transaction contains a large `CHANNEL_INSCRIBE` Operation).
Here we show the difference of computation speed for Mantle Transactions encoding and hashing containing a single Ledger Transaction and a single Inscription varying the size of the inscription to make the transaction longer.

```text
+--------------+-----------------------+------------------+-------------------------------+---------------------------+
| payload_size | blake2b_poseidon2_avg | poseidon2_avg    | poseidon2 / blake2b_poseidon2 | blake2b+poseidon2 faster  |
+--------------+-----------------------+------------------+-------------------------------+---------------------------+
|           64 | 10.84 us              | 65.89 us         | 6.08x                         | 83.55%                    |
|          256 | 10.40 us              | 62.14 us         | 5.98x                         | 83.26%                    |
|        1,024 | 10.89 us              | 142.30 us        | 13.07x                        | 92.35%                    |
|        4,096 | 13.02 us              | 561.00 us        | 43.09x                        | 97.68%                    |
|       65,536 | 71.34 us              | 8.851 ms         | 124.07x                       | 99.19%                    |
|      524,288 | 657.20 us             | 70.69 ms         | 107.56x                       | 99.07%                    |
|    1,048,576 | 1.315 ms              | 143.30 ms        | 108.97x                       | 99.08%                    |
|    2,097,152 | 2.652 ms              | 283.90 ms        | 107.05x                       | 99.07%                    |
|    4,194,304 | 5.981 ms              | 563.70 ms        | 94.25x                        | 98.94%                    |
+--------------+-----------------------+------------------+-------------------------------+---------------------------+
```

We can clearly see that combining the classic and zk hashes yields a significant improvement.
The material used for the benchmarks is the following:
- CPU       : 13th Gen Intel(R) Core(TM) i9-13980HX (24 cores / 32 threads)
- RAM       : 32GB - Speed: 5600 MT/s
- Motherboard: Micro-Star International Co., Ltd. MS-17S1
- OS        : Ubuntu 22.04.5 LTS
- Kernel    : 6.8.0-59-generic

The code of the benchmarks can be found [here](https://github.com/logos-blockchain/logos-blockchain/pull/2405).

## Specifications Update

- [v1.2.1] Mantle Specification
