# BEDROCK-GENESIS-BLOCK

| Field | Value |
| --- | --- |
| Name | Bedrock Genesis Block |
| Slug | 90 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <davidrusu@logos.co> |
| Contributors | Hong-Sheng Zhou, Thomas Lavaur <thomaslavaur@logos.co>, Marcin Pawlowski <marcin@logos.co>, Mehmet Gonen <mehmet@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Daniel Sanchez Quiros <danielsq@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-05-27** — [`b7602ed`](https://github.com/logos-co/logos-lips/blob/b7602ed8a225d41ca0bfaaa432524dc84d2ded7e/docs/blockchain/raw/bedrock-genesis-block.md) — chore: move blockchain specs from notion to github
- **2026-05-18** — [`58b5698`](https://github.com/logos-co/logos-lips/blob/58b56988429f4d69a9e10a9fc118725e229e37c5/docs/blockchain/raw/bedrock-genesis-block.md) — chore(blockchain): migrate contributor emails to @logos.co (#338)
- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-genesis-block.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-genesis-block.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

# Revisions History

| **Version** | **Changes** | **Date** |
| --- | --- | --- |
| 1.0.0 | Initial revision. | 2026-02-12 |
| 1.1.0 | [[RFC] Make Ledger Transaction an Operation](mantle-transaction-encoding/appendices/rfc-make-ledger-transaction-an-operation.md) Renamed Nomos to Logos Blockchain Remove notions of DA Minor fix in gas price | 2026-03-27 |
| 1.1.1 | [[RFC] Simplify Mantle Transaction and Refactor Ledger Operations](mantle-transaction-encoding/appendices/rfc-simplify-mantle-transaction-and-refactor-ledger-operations.md) | 2026-05-06 |
| 1.1.2 | Encode `genesis_time` as a u32 unix timestamp instead of an ISO 8601 datetime. Encode the `chain_id` length prefix as a u8 instead of a u64. | 2026-07-06 |
| 1.2.0 | Seed the proof of work reward pool at genesis from the initial token distribution | 2026-08-10 |

# Introduction

The Genesis Block defines the starting state for the Bedrock chain, including the initial bedrock service providers, LGO token distribution and protocol parameters. Its design draws from best practices in the Ouroboros family of protocols (notably Praos and Genesis), as well as privacy and resilience advances from Cryptarchia and related research. The Genesis Block is the **root of trust** for all subsequent protocol operations and must be constructed in a way that is deterministic, verifiable, and robust against long-range or bootstrap attacks.

# Overview

The Genesis Block establishes the initializing values for the various protocols and services. This includes the initial token distribution, initial nodes participating in Blend Network and the result of running the epoch nonce ceremony.

The block body is a single Mantle Transaction (see [Mantle](bedrock-v1.1-mantle-specification.md)) containing a Transfer Operation distributing the notes to initial token holders. The bedrock services are initialized through `SDP_DECLARE` Operations embedded in the Mantle Transaction’s Operations list and protocol initializing constants are encoded through a `CHANNEL_INSCRIBE` Operation also embedded in the Operations list.

Not all protocol constants are encoded in the Genesis block. The principle we use to decide whether a value should be in the Genesis block or not is whether it is a value that is derived from blockchain activity or whether it is updated through a protocol update (hard / soft fork). For example, the epoch nonce is updated through normal blockchain Operations and therefore it should be specified in the Genesis block. Gas constants are only changed through protocol updates and hard forks and therefore they will be hardcoded in the node implementation.

# Genesis Block Data Structure

The Genesis Block is composed of the Genesis Block Header and the Genesis Mantle Transaction (there is a single transaction in the genesis block). The Mantle Transaction contains all information necessary for initializing Bedrock Services and Cryptarchia state, as well as distributing the initial tokens to stakeholders.

## Initial Token Distribution

Initial tokens will be distributed through a Transfer Operation containing zero inputs and one output note for each initial stakeholder. Note that since the Ledger is transparent, the initial stake allocation is visible to everyone. Those wishing to hide their initial stake may opt to subdivide their note into a few different notes of equal value.

In order to participate in the Cryptarchia lottery, stakeholders must generate their note keys in accordance with the Proof of Leadership protocol specified at [Protocol](cryptarchia-proof-of-leadership.md#protocol).

The initial state of the Ledger will be derived through normal execution of this Transfer Operation, that is, each output’s note ID will be added to the unspent notes set.

**Example**

```python
STAKE_DISTRIBUTION = Transfer(
    inputs=[],
    outputs=[
        Note(value=1000, public_key=STAKE_HOLDER_0_PK),
        Note(value=2000, public_key=STAKE_HOLDER_1_PK),
        Note(value=1500, public_key=STAKE_HOLDER_2_PK),
        # ...
    ]
)
```

## Initial Proof of Work Reward Pool

The proof of work reward pool is seeded once, at genesis, with a fixed quantity of tokens:

```python
POW_REWARD_POOL_GENESIS: TokenValue   # Initial balance of the proof of work reward pool
                                      # = 5/1000 of the supply at network launch
```

The seed is **five thousandths of the supply at network launch**. It is stated as a fraction of that supply because that is the form in which it is a decision about how the initial supply is divided: the reward the pool yields per claim follows from the fraction, the distribution rate and the target claim rate alone. Whether that reward is generous enough depends on the price level the fee markets are initialised at, not on the seed, and the constraint that places on genesis governance is given in [Genesis](bedrock-v1.1-mantle-specification.md#genesis) along with the reasoning behind the size.

This allocation is **drawn from the initial token distribution**, not minted in addition to it. The tokens exist from genesis and the seed determines how many of them are held in the pool rather than distributed to stakeholders directly. This is what keeps claiming outside the protocol's emission envelope, as described in [Reward Pool](bedrock-v1.1-mantle-specification.md#reward-pool), and it means the seed is a decision about how the initial supply is divided rather than about how much supply exists.

The pool holds a balance rather than notes, so unlike the stakeholder allocations above it does not appear as an output of the initial Transfer Operation. It is consensus state maintained by Mantle, and after genesis it changes only through the epoch-boundary refill and through claims.

The seed is not part of the Cryptarchia parameter inscription, because it is not a Cryptarchia parameter. It is established during [Mantle Ledger Initialization](#mantle-ledger-initialization).

Its size governs how generous claiming is during the network's earliest epochs, and therefore how quickly a participant with no tokens can accumulate a usable balance.

## Initial Service Declarations

Blend Network MUST initialize its set of providers. This is done through a set of `SDP_DECLARE` Operations in the Genesis Mantle Transaction.

Blend enforces a minimal network size for the service to be active. Thus, in order to have an active Blend service at Genesis, we MUST have at least as many declarations in the Genesis block to meet Blend service’s minimal network size [Minimal Network Size](blend-protocol.md#minimal-network-size).

**Example**

```python
BLEND_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(
            ServiceType.BLEND, ["ip://1.1.1.1:3000"], PROVIDER_ID_0, ZK_ID_0
        ),
        locked_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
    ),
    # ... 32 total declarations
]

SERVICE_DECLARATIONS = BLEND_DECLARATIONS
```

## Cryptarchia Parameters

Cryptarchia is initialized with the following parameters:

- `genesis_time`: u32 unix timestamp (seconds since the Unix epoch).
  A unix timestamp is conventionally an `i64`; `genesis_time` is restricted to the `u32` range (0 to 2^32 - 1), which covers all plausible genesis dates (through February 2106).
  Cryptarchia uses slots as a measure of time offset from some start time. This timestamp must be agreed upon by all nodes in order to have a common clock.

- `chain_id`: UTF-8 string, encoded with a u8 length prefix (at most 255 bytes).
  It is useful to differentiate testnets from mainnet. To avoid confusion, we place the chain ID in the Genesis block to guarantee that the networks are disjoint.

- `genesis_epoch_nonce`: 32 bytes, hex encoded.
  The initial source of randomness for the Cryptarchia lottery. The process for selecting this value is described in detail at [Epoch Nonce Ceremony](#epoch-nonce-ceremony).

These parameters are encoded in the Genesis block as an inscription sent to the null channel.

**Example**

```python
CHAIN_ID = "logos-blockchain-mainnet"
GENESIS_TIME = 1767640835  # 2026-01-05T19:20:35Z
GENESIS_EPOCH_NONCE = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

chain_id_enc = CHAIN_ID.encode("utf-8")
chain_id_len = len(chain_id_enc).to_bytes(1, "little")
genesis_time = GENESIS_TIME.to_bytes(4, "little")
genesis_epoch_nonce = bytes.fromhex(GENESIS_EPOCH_NONCE)

inscription = chain_id_len + chain_id_enc + genesis_time + genesis_epoch_nonce

# >>> inscription.hex()
# '186c6f676f732d626c6f636b636861696e2d6d61696e6e6574030f5c69abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'

CRYPTARCHIA_INSCRIPTION = Inscribe(
    channel=bytes(32),
    inscription=inscription,
    parent=bytes(32),
    signer=Ed25519PublicKey_ZERO,
)
```

### Epoch Nonce Ceremony

The initial epoch nonce value governs the Cryptarchia lottery randomness for the first epoch. It must be revealed AFTER the initial stake distribution has been frozen. This is done to prevent any stakeholders from gaining an unfair advantage from prior knowledge of the lottery randomness.

The protocol for generating the initial randomness nonce can be found below.

1. **Schedule Epoch Nonce Ceremony Event:**
  We must fix well in advance when this epoch nonce ceremony will take place, let `t` denote the time of the Epoch Nonce Ceremony, broadcast `t` widely.

  The `STAKE_DISTRIBUTION` must be finalized before `t` to ensure a fair Cryptarchia slot lottery.

2. **Randomness Collection:**
  We collect the entropy from multiple randomness sources:

| Entropy Source | Details |
| --- | --- |
| Bitcoin block hash immediately after time `t`, denoted as $`r_1`$. | Block hash can be found on [`blockchain.com`](http://blockchain.com) ’s bitcoin block explorer, e.g. [https://www.blockchain.com/explorer/blocks/btc/905030](https://www.blockchain.com/explorer/blocks/btc/905030) |
| Ethereum block hash immediately after time `t`, denoted as $`r_2`$. | Block hash can be found in the `more details` section of when viewing a block on etherscan, e.g. [https://etherscan.io/block/22894116](https://etherscan.io/block/22894116) |
| DRAND beacon value for the round immediately after `t`, denoted as $`r_3`$. | Use the `default` beacon, and find the round number corresponding to `t`. [https://api.drand.sh/v2/beacons/default/rounds/1234](https://api.drand.sh/v2/beacons/default/rounds/1234) |

3. **Randomness Derivation:**
  Once all above entropy contributions, i.e., $`r_1,r_2,r_3`$ are collected, then we can compute the initial epoch randomness $`\eta_{\text{GENESIS}}`$ as:

$$
\eta_\text{GENESIS}={H}(r_1,r_2,r_3)
$$

  where $`H`$ is a collision-resistant zkhash function.

## Genesis Mantle Transaction

The initial stake distribution, service declarations and Cryptarchia inscription are components of the Genesis Mantle Transaction. This is the single transaction that forms the body of the Genesis block.

```python
GENESIS_MANTLE_TX = MantleTx(
    ops=[STAKE_DISTRIBUTION, CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
)
```

## Block Header Fields

The Genesis Block header fields are set to the following values:

- `bedrock_version`: Protocol version (e.g., 1).
- `parent_block`: 0 (as this is the first block).
- `slot`: 0 (the Genesis slot).
- `block_root`: Block Merkle root over the (single) initial transaction.
- `proof_of_leadership`: Stubbed leadership proof.
  - `leader_voucher`: 0 (as there is no leader block reward for the initial block).
  - `entropy_contribution`: 0 (no entropy is provided through the initial PoL).
  - `proof`: Null Groth16Proof, all values are set to zero.
  - `leader_key`: Null PublicKey.

**Example**

```python
GENESIS_HEADER = Header(
    bedrock_version=1,
    parent_block=0,
    slot=0,
    block_root=block_merkle_root([GENESIS_MANTLE_TX]),
    proof_of_leadership=ProofOfLeadership(
        leader_voucher=bytes(32),
        entropy_contribution=bytes(32),
        proof=Groth16Proof(G1_ZERO, G2_ZERO, G1_ZERO),
        leader_key=Ed25519PublicKey_ZERO,
    )
)
```

```python
# distribute NMO to all stakeholders
STAKE_DISTRIBUTION = Transfer(
    inputs=[],
    outputs=[
        Note(value=1000, public_key=STAKE_HOLDER_0_PK),
        Note(value=2000, public_key=STAKE_HOLDER_1_PK),
        Note(value=1500, public_key=STAKE_HOLDER_2_PK),
        # ...
    ]
)

# set Cryptarchia parameters
CHAIN_ID = "logos-blockchain-mainnet"
GENESIS_TIME = 1767640835  # 2026-01-05T19:20:35Z
GENESIS_EPOCH_NONCE = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

chain_id_enc = CHAIN_ID.encode("utf-8")
inscription = (
    len(chain_id_enc).to_bytes(1, "little")
    + chain_id_enc
    + GENESIS_TIME.to_bytes(4, "little")
    + bytes.fromhex(GENESIS_EPOCH_NONCE)
)

CRYPTARCHIA_INSCRIPTION = Inscribe(
    channel=bytes(32),
    inscription=inscription,
    parent=bytes(32),
    signer=Ed25519PublicKey_ZERO,
)

# service declarations
BLEND_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(ServiceType.BLEND, ["ip://1.1.1.1:3000"], PROVIDER_ID_0, ZK_ID_0),
        locked_note_id=STAKE_DISTRIBUTION.output_note_id(0)
    ),
    # ... more declarations
]
SERVICE_DECLARATIONS = BLEND_DECLARATIONS

# build the genesis Mantle Transaction
GENESIS_MANTLE_TX = MantleTx(
    ops=[STAKE_DISTRIBUTION, CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
)

GENESIS_HEADER = Header(
    bedrock_version=1,
    parent_block=bytes(32),
    slot=0,
    block_root=block_merkle_root([GENESIS_MANTLE_TX]),
    proof_of_leadership=ProofOfLeadership(
        leader_voucher=bytes(32),
        entropy_contribution=bytes(32),
        proof=Groth16Proof(G1.ZERO, G2.ZERO, G1.ZERO),
        leader_key=Ed25519PublicKey_ZERO,
    )
)

GENESIS_BLOCK = (GENESIS_HEADER, [GENESIS_MANTLE_TX])
```

# Sample Genesis Block

# Initializing Bedrock

Bedrock is initialized by executing the Mantle Transaction without validating the Mantle Operations. No validation or execution is done for the Genesis block header; in particular, processing of `proof_of_leadership` is skipped.

## Mantle Ledger Initialization

The Transfer Operation should be executed without checking that the transaction is balanced. However, other validations are checked, e.g. that output note values are positive and smaller than the maximum allowed value. The result of normal transfer execution adds all outputs to the Ledger.

The proof of work reward pool is initialized at the same time:

1. `pow_reward_pool` is set to `POW_REWARD_POOL_GENESIS`, as described in [Initial Proof of Work Reward Pool](#initial-proof-of-work-reward-pool).
2. `epoch_pow_reward` is derived from it by the computation given in [Reward Pool](bedrock-v1.1-mantle-specification.md#reward-pool), so that claiming is productive from the first epoch rather than waiting for the first refill.
3. `difficulty_blend` is set to `BLEND_DIFFICULTY_BASE` for **epochs 0 and 1**, as given in [Blend Difficulty](bedrock-v1.1-mantle-specification.md#blend-difficulty): the value for an epoch is fixed at the preceding epoch's nonce snapshot from the load of the epoch before that, and no complete input epoch exists before epoch 2. The schedule begins with epoch 2's value, computed during epoch 1 from epoch 0's load.
4. `difficulty_reward` is set to the genesis value given in [Reward Difficulty](bedrock-v1.1-mantle-specification.md#reward-difficulty), which is deliberately on the hard side so that the controller's first correction loosens rather than tightens, and `pow_nullifiers` is empty.

## Cryptarchia Initialization

The Mantle Transaction contains an inscription sent to the null channel containing the parameters for initializing Cryptarchia.

The Cryptarchia slot clock is initialized to `genesis_time`, `LIB` is set to the Genesis block and the epoch state is then initialized:

### Initial Epoch State

Cryptarchia progresses in epochs where the variables governing the lottery are fixed for the duration of an epoch and the activity during that epoch is used to derive the values of those variables for the next epoch. These variables taken together are called the Epoch State. (see [Epoch State](cryptarchia-v1-protocol.md#epoch-state)).

To initialize the Epoch State, we derive the epoch variables from the genesis block.

1. $`\eta`$ : the epoch nonce is taken directly from the `genesis_epoch_nonce`.
2. $`\mathbb{C}_\text{LEAD}`$: Eligible leader commitment is set to the the Ledger Root over all notes from the initial token distribution. The derivation of this root is specified in [Ledger Root](cryptarchia-proof-of-leadership.md#ledger-root).
3. $`D`$: The initial estimate of total stake will be the total tokens distributed at genesis.

## Bedrock Services Initialization

Blend network is initialized through normal Mantle Transaction execution. The `SDP_DECLARE` Operations in the Genesis Mantle Transaction will create the initial set of providers in each service.

During normal operations, Blend services would wait until a block is deep enough to be finalized, but for the Genesis block, we consider it finalized by definition and so Blend will immediately use the provider set without the usual finalization delay.

# References

- Ouroboros Praos: [https://eprint.iacr.org/2017/573.pdf](https://eprint.iacr.org/2017/573.pdf)
- Ouroboros Genesis: [https://eprint.iacr.org/2018/378.pdf](https://eprint.iacr.org/2018/378.pdf)
- Ouroboros Crypsinous: [https://eprint.iacr.org/2018/1132.pdf](https://eprint.iacr.org/2018/1132.pdf)
- Cardano Shelley Genesis File Format: [https://cardano-course.gitbook.io/cardano-course/handbook/protocol-parameters-and-configuration-files/shelley-genesis-file](https://cardano-course.gitbook.io/cardano-course/handbook/protocol-parameters-and-configuration-files/shelley-genesis-file)
- Cardano CIP-16 Key Serialisation: [https://cips.cardano.org/cip/CIP-16](https://cips.cardano.org/cip/CIP-16)
