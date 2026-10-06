# [RFC] Cryptoeconomics: Define the LEPTON as the indivisible token unit

**Motivation and proposal:** [PR #477](https://github.com/logos-co/logos-lips/pull/477)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-10-06 |

## Reviewer Orientation

Read the PR's Motivation first. The Mantle and Execution Market specifications are unchanged but assumed: the unit rules apply to every amount they define.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | Critical | **Start here**: [Overview Cryptoeconomics → Token Units and Precision](../overview-cryptoeconomics.md#token-units-and-precision) ([details](#1-the-lepton-and-the-precision-of-nine)) | $10^{10} \cdot 10^{9} = 10^{19} \le 2^{64}-1$, so the hard cap fits one note. The denomination ladder names each quantity once |
| 2 | Critical | [Block Rewards → Float Precision for Implementation](../block-rewards.md#float-precision-for-implementation) ([details](#2-block-rewards-rescale-the-integer-rule)) | $c^{\ast}$ and $\Lambda^{\ast}$ rescale from $10^{18}$ to $10^{9}$. Check that no other constant in the rule still reads $10^{d}$ |
| 3 | High | [\[Analysis\] LOGOS Token Units and Precision](../analysis-logos-token-units-and-precision.md) ([details](#3-encoding-parsing-and-rounding)) | the parser rejects a tenth fractional digit. The rounding direction of each class of quantity |
| 4 | Medium | [Storage Markets → Initial Price](../storage-markets.md) ([details](#4-storage-markets-initial-price)) | the initial price of 1 LOGOS against the floor of 1 LEPTON per gas unit |
| 5 | Low | Five specifications ([details](#5-uniform-naming)) | skim: LGO becomes LOGOS or LEPTA |

# Discussion

## Why nine

Two bounds meet at 9. The hard cap fits a `uint64` only if $d \le 9$. The gas price floor needs $d \ge \log_{10}(p \cdot 2^{33} / c^{\ast})$, with $p$ the token price and $c^{\ast}$ the target cost of one GiB of permanent storage.

The upper bound is the largest integer in the admissible set, so 9 is admissible whenever any precision is. Choosing it commits to no value of $p / c^{\ast}$. The analysis tabulates the bounds in [Choice of Precision](../analysis-logos-token-units-and-precision.md#choice-of-precision).

## Where nine stops working

Nine holds while one LOGOS buys at most $10^{9} / 2^{33} = 0.1164$ GiB of permanent storage at the target cost. Above that ratio no precision meets both bounds, and the remedy lies in the Permanent Storage Gas unit, not in the precision. The target cost $c^{\ast}$ is a design parameter in the analysis, not a calibrated price.

## Headroom

At $d = 9$ the hard cap uses 54.2% of the `uint64` range, which leaves 1.8447 times the cap in headroom. A cap above 18,446,744,073 LOGOS forces $d \le 8$. No path in Block Rewards raises the supply above the cap, so the headroom is not consumed.

## Compatibility

The encoding does not change. `Note.value` is already a `uint64`, and this change names what the integer counts. Block Rewards changes only the scale of two constants in its integer rule. Bedrock has no deployed network, so the change needs no migration.

## Specifications the change leaves unmodified

The analysis lists every quantity in [Mantle](../bedrock-v1.1-mantle-specification.md) and [Execution Market](../execution-market.md) as counted in LEPTA, but neither specification names the unit. Both are candidates for a one-line statement of the unit.

# Details

## 1. The LEPTON and the precision of nine

[Overview Cryptoeconomics](../overview-cryptoeconomics.md#token-units-and-precision) gains the section Token Units and Precision. It fixes four requirements, **R1** to **R4**, and the denominations:

| Unit (singular / plural) | Symbol | In LEPTA | In LOGOS |
| --- | --- | --- | --- |
| lepton / lepta | `LEPTON` | $10^{0}$ | $10^{-9}$ |
| kilolepton / kilolepta | `kLEPTON` | $10^{3}$ | $10^{-6}$ |
| megalepton / megalepta | `MLEPTON` | $10^{6}$ | $10^{-3}$ |
| logos | `LOGOS` | $10^{9}$ | $1$ |

- The LEPTON is the indivisible unit at every layer of the protocol.
- Symbols are never pluralized. `500 LEPTON` is correct and `500 LEPTA` is not.
- $\mu\text{LOGOS}$ and mLOGOS are display aliases only. They are not permitted in protocol interfaces, RPC payloads, or specification text.
- `GLEPTON` is invalid, because it would denote the LOGOS.

## 2. Block Rewards: rescale the integer rule

The Float Precision section of [Block Rewards](../block-rewards.md) counts in LEPTA, with $1 \text{ LOGOS} = 10^{9}$ LEPTA:

```diff
-All quantities are in base units, $1$ LGO $= 10^{d}$ base units with $d = 18$.
+All quantities are in base units, $1$ LOGOS $= 10^{9}$ LEPTA.
 ...
-c^{\ast} = \lfloor 62500 \cdot 10^{d} / 657 \rfloor, \Lambda^{\ast} = 5 \cdot 10^{8} \cdot 10^{d}, M = 2^{32}
+c^{\ast} = \lfloor 62500 \cdot 10^{9} / 657 \rfloor, \Lambda^{\ast} = 5 \cdot 10^{8} \cdot 10^{9}, M = 2^{32}
```

The truncation of $c^{\ast}$ stays below one base unit. That is now one LEPTON, $10^{-9}$ LOGOS, where it was $10^{-18}$ LGO. The parameter table states each constant in LOGOS.

## 3. Encoding, parsing, and rounding

[\[Analysis\] LOGOS Token Units and Precision](../analysis-logos-token-units-and-precision.md) is new. It specifies four rules that other specifications inherit:

- **Encoding.** Every amount is an unsigned integer count of LEPTA. `Value` stays `UINT64`, and no new numeric type is added.
- **Parsing.** A parser rejects a decimal string with more than nine fractional digits, and one above $2^{64}-1$ LEPTA. The largest amount is 18,446,744,073.709551615 LOGOS. No step uses floating point.
- **Rounding.** Every reduction goes to a whole LEPTON. Amounts charged to a user round away from zero. Credits and measurements round toward zero.
- **Residues.** A mechanism that splits an amount across several roundings must state where the residue goes.

The document also lists the unit of each protocol quantity and the naming of the token: LOGOS, with the proposed ISO 4217 form XLG, which is not an assigned code.

## 4. Storage Markets: initial price

[Storage Markets](../storage-markets.md) states the price in LEPTA per Permanent Storage Gas unit. The price is an integer, and its floor is 1 LEPTON per gas unit.

- The initial price $P_{\text{storage}}(0)$ is 1 LOGOS, which is $10^{9}$ LEPTA, per gas unit. It was 1 LGO.
- At 8 gas per byte, the initial price is 8 LOGOS per permanently stored byte. The text said 1 LGO per byte.
- Rounding the price upwards makes 1 LEPTON per gas unit the effective floor. A price that reached 1 LEPTON would otherwise round to 0 and stay there.

## 5. Uniform naming

Each amount names LOGOS or LEPTA, as its context requires. Every touched specification gains a revision row dated 2026-10-06.

- [\[Analysis\] Static Minimum Stake Estimation for the Service Declaration Protocol](../analysis-static-minimum-stake-estimation-for-service-declaration-protocol.md) changes its example maximum supply from 10 million to 10 billion LOGOS.

## Chores

- LGO becomes LOGOS in prose in [Bedrock Genesis Block](../bedrock-genesis-block.md), [\[Analysis\] Block Rewards](../analysis-block-rewards.md), and [\[Analysis\] Block Reward Parameter Calibration](../analysis-block-reward-parameter-calibration.md).
- The heading $\text{Stake}_{LGO}$ becomes $\text{Stake}_{\text{LOGOS}}$, with its anchor.
- [Overview Cryptoeconomics](../overview-cryptoeconomics.md) lists the new analysis among its references.

# Implementation

- [ ] Represent every protocol amount as a `uint64` count of LEPTA, and add no new numeric type
- [ ] Rescale the constants $c^{\ast}$ and $\Lambda^{\ast}$ of the Block Rewards integer rule to $10^{9}$
- [ ] Implement amount parsing and rendering per Encoding and Parsing, with the two rejection rules and no floating point
- [ ] Apply the rounding direction of each class of quantity, and state where each residue goes
- [ ] Use the canonical unit names in protocol interfaces and RPC payloads, and reject `GLEPTON`
- [ ] Add test vectors for parsing and rendering at 0, one LEPTON, $10^{9}-1$ LEPTA, and the largest amount, 18,446,744,073.709551615 LOGOS
- [ ] Verify the implementation matches this specification

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [\[Analysis\] LOGOS Token Units and Precision](../analysis-logos-token-units-and-precision.md) | Created | version `1.0.0` |
| [\[Overview\] Cryptoeconomics](../overview-cryptoeconomics.md) | Modified | version `1.3.0`, the Token Units and Precision section |
| [Block Rewards](../block-rewards.md) | Modified | version `1.2.1`, the Float Precision section and unit names |
| [Storage Markets](../storage-markets.md) | Modified | version `1.1.3`, unit names |
| [Bedrock Genesis Block](../bedrock-genesis-block.md) | Modified | version `1.2.1`, terminology only |
| [\[Analysis\] Block Rewards](../analysis-block-rewards.md) | Modified | version `1.0.3`, unit names |
| [\[Analysis\] Block Reward Parameter Calibration](../analysis-block-reward-parameter-calibration.md) | Modified | version `1.0.1`, unit names |
| [\[Analysis\] Static Minimum Stake Estimation for the Service Declaration Protocol](../analysis-static-minimum-stake-estimation-for-service-declaration-protocol.md) | Modified | version `1.0.2`, unit names and one example value |

Version numbers to watch when merging: `master` already carries Overview Cryptoeconomics at `1.3.0` and Storage Markets at `1.2.0`, so those rows renumber.
