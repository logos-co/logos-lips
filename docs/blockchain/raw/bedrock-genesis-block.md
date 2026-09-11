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
| 1.1.3 | Replaced the `block_root` header field with `body_root`, taken over an empty uncle header list and the initial transaction, due to updated [Block Construction, Validation and Execution](bedrock-v1.1-block-construction.md). | 2026-08-06 |
| 1.1.4 | Stated which validations apply when the Genesis Mantle Transaction is processed: the ordinary Mantle rules apply to every Operation, minus a closed list of exemptions that the absence of any state before Genesis makes impossible to satisfy. | 2026-08-25 |
| 1.1.5 | Renamed locked notes into service notes: the Blend declarations of the Genesis Mantle Transaction name a `service_note_id` | 2026-08-27 |
| 1.2.0 | Removed the `bedrock_version` header field and moved `slot` first ([Bedrock Eras](bedrock-eras.md)). | 2026-09-04 |

# Introduction

The Genesis Block defines the starting state for the Bedrock chain, including the initial bedrock service providers, LGO token distribution and protocol parameters. Its design draws from best practices in the Ouroboros family of protocols (notably Praos and Genesis), as well as privacy and resilience advances from Cryptarchia and related research. The Genesis Block is the **root of trust** for all subsequent protocol operations and must be constructed in a way that is deterministic, verifiable, and robust against long-range or bootstrap attacks.

# Overview

The Genesis Block establishes the initializing values for the various protocols and services. This includes the initial token distribution, initial nodes participating in Blend Network and the result of running the epoch nonce ceremony.

The block body is a single Mantle Transaction (see [Mantle](bedrock-v1.1-mantle-specification.md)) containing a Transfer Operation distributing the notes to initial token holders. The bedrock services are initialized through `SDP_DECLARE` Operations embedded in the Mantle Transaction’s Operations list and protocol initializing constants are encoded through a `CHANNEL_INSCRIBE` Operation also embedded in the Operations list.

Not all protocol constants are encoded in the Genesis block. The principle we use to decide whether a value should be in the Genesis block or not is whether it is a value that is derived from blockchain activity or whether it is updated through an era change ([Bedrock Eras](bedrock-eras.md)). For example, the epoch nonce is updated through normal blockchain Operations and therefore it should be specified in the Genesis block. Gas constants are only changed through an era change and therefore they will be hardcoded in the node implementation.

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
        service_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
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

These parameters are encoded in the Genesis block as an inscription sent to the null channel, signed by the null key. The null channel is the channel whose `ChannelId` is 32 zero bytes and the null key is the Ed25519 public key made of 32 zero bytes, written `Ed25519PublicKey_ZERO` in the examples below. No one holds the secret key behind it, so the null channel receives the Genesis inscription and nothing else ever after.

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

- `slot`: 0 (the Genesis slot).
- `parent_block`: 0 (as this is the first block).
- `body_root`: the body commitment over an empty `uncle_headers` list (as the Genesis Block references no uncle, it encodes as a zero element count) and the Merkle root over the (single) initial transaction.
- `proof_of_leadership`: Stubbed leadership proof.
  - `leader_voucher`: 0 (as there is no leader block reward for the initial block).
  - `entropy_contribution`: 0 (no entropy is provided through the initial PoL).
  - `proof`: Null Groth16Proof, all values are set to zero.
  - `leader_key`: Null PublicKey.

**Example**

```python
GENESIS_HEADER = Header(
    slot=0,
    parent_block=0,
    body_root=body_root([], [GENESIS_MANTLE_TX]),
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
        service_note_id=STAKE_DISTRIBUTION.output_note_id(0)
    ),
    # ... more declarations
]
SERVICE_DECLARATIONS = BLEND_DECLARATIONS

# build the genesis Mantle Transaction
GENESIS_MANTLE_TX = MantleTx(
    ops=[STAKE_DISTRIBUTION, CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
)

GENESIS_HEADER = Header(
    slot=0,
    parent_block=bytes(32),
    body_root=body_root([], [GENESIS_MANTLE_TX]),
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

Bedrock is initialized by validating and executing the Genesis Mantle Transaction under the ordinary Mantle rules, [Validation](bedrock-v1.1-mantle-specification.md#validation) and [Execution](bedrock-v1.1-mantle-specification.md#execution), with the exemptions listed in [Genesis Validation Exemptions](#genesis-validation-exemptions) and no others. Its Operations are validated and executed one after the other in the order they appear, each against the state the preceding ones left, which is what makes the `SDP_DECLARE` Operations able to lock notes the Transfer Operation before them created.

The Genesis block is not a block proposal and is not validated as one: none of the checks of [Block Proposal Validation](bedrock-v1.1-block-construction.md#block-proposal-validation) apply, and no validation or execution is done for the Genesis block header, in particular processing of `proof_of_leadership` is skipped.

Validating the Genesis Mantle Transaction is not what makes the Genesis block trustworthy. The block is agreed upon out of band, every node starts from the same one, and a node that rejected it would have no chain to join. The checks are kept for two reasons: a malformed or inconsistent Genesis block is then reported when a node is set up rather than surfacing later as unexplained runtime behaviour, and Genesis stays on the ordinary Operation processing path instead of needing an unvalidated path of its own. This is why the exemptions below are a closed list rather than a general licence to skip validation.

The Genesis Mantle Transaction holds, in this order, the Transfer Operation distributing the initial tokens, the `CHANNEL_INSCRIBE` Operation carrying the Cryptarchia parameters, and one `SDP_DECLARE` Operation per initial service provider. A Genesis Mantle Transaction whose Operations do not follow that shape, or that holds an Operation of any other opcode, is invalid.

## Genesis Validation Exemptions

The checks below, and only these, are skipped when the Genesis Mantle Transaction is processed. Each one is skipped because the Genesis block, having no state before it and no signer the chain knows about, cannot satisfy it.

1. **Every proof and signature.** No Operation proof is verified at Genesis: neither the `ZkSignature` of the Transfer Operation, nor the `Ed25519Signature` of the inscription, nor the `DeclarationProof` of the `SDP_DECLARE` Operations. The Transfer Operation consumes no note and therefore has no public key to verify against, the inscription is signed by the null key whose secret key nobody holds, and the keys a declaration would prove ownership of are already fixed by the out of band agreement on the Genesis block, so verifying them would establish nothing a node does not already have to trust. The `op_proofs` list still holds one entry per Operation, of the type that Operation requires, and those entries are placeholders.

2. **The transaction balance covering the mandatory fees.** The whole initial token supply is created out of nothing by the Transfer Operation, so the balance of the Genesis Mantle Transaction is negative and no fee can be paid from it. Step 3 of [Validation](bedrock-v1.1-mantle-specification.md#validation) is skipped, no mandatory fee is charged and no `tx_priority_tip` is derived. The Genesis Mantle Transaction is accounted as costing no gas.

3. **The Transfer Operation inputs.** The Genesis Transfer Operation has no inputs, no note existing before it, so the requirement that inputs be non-empty ([Input Notes Spendability Validation](bedrock-v1.1-mantle-specification.md#input-notes-spendability-validation)) does not apply and there is no spendability to check. It is the only Transfer Operation of the chain allowed to consume nothing.

Everything else is validated as it would be in any other block, against the state the Operations preceding it left, the transaction level check that there is one `op_proofs` entry per Operation included.

## Mantle Ledger Initialization

The Transfer Operation distributing the initial tokens is validated and executed as any other Transfer Operation, minus the two exemptions covering its inputs and the transaction balance. Its outputs are validated as [Output Notes Validation](bedrock-v1.1-mantle-specification.md#output-notes-validation) requires. The result of normal transfer execution adds all outputs to the Ledger, their `NoteId` derived from the Operation as usual.

## Cryptarchia Initialization

The Mantle Transaction contains an inscription sent to the null channel containing the parameters for initializing Cryptarchia. It is validated as an ordinary `CHANNEL_INSCRIBE` Operation minus its signature: the null channel does not exist yet, so the inscription must carry a `parent` of `ZERO`, and its execution creates that channel with the null key as its only accredited key.

Two conditions are specific to Genesis. The inscription must be addressed to the null channel and signed by the null key, an inscription anywhere else not being a set of Cryptarchia parameters. It must also decode to exactly the three parameters, encoded as [Cryptarchia Parameters](#cryptarchia-parameters) specifies and with no trailing bytes. A node that cannot decode them has no clock, no chain identifier and no lottery randomness, and must reject the Genesis block.

The Cryptarchia slot clock is initialized to `genesis_time`, `LIB` is set to the Genesis block and the epoch state is then initialized:

### Initial Epoch State

Cryptarchia progresses in epochs where the variables governing the lottery are fixed for the duration of an epoch and the activity during that epoch is used to derive the values of those variables for the next epoch. These variables taken together are called the Epoch State. (see [Epoch State](cryptarchia-v1-protocol.md#epoch-state)).

To initialize the Epoch State, we derive the epoch variables from the genesis block.

1. $`\eta`$ : the epoch nonce is taken directly from the `genesis_epoch_nonce`.
2. $`\mathbb{C}_\text{LEAD}`$: Eligible leader commitment is set to the the Ledger Root over all notes from the initial token distribution. The derivation of this root is specified in [Ledger Root](cryptarchia-proof-of-leadership.md#ledger-root).
3. $`D`$: The initial estimate of total stake will be the total tokens distributed at genesis.

## Bedrock Services Initialization

Blend network is initialized through normal Mantle Transaction execution. The `SDP_DECLARE` Operations in the Genesis Mantle Transaction will create the initial set of providers in each service.

Beyond their proofs, the declarations carry no exemption: each is validated as [SDP_DECLARE](bedrock-v1.1-mantle-specification.md#sdp_declare) requires, against the state the Operations preceding it left, and executed with `created` set to epoch 0, the epoch the Genesis block belongs to. The service note a declaration names is an output of the Transfer Operation that precedes it, which is why the Operation order of the Genesis Mantle Transaction is normative, and the minimum stake that note is measured against is the one the node implementation starts with, the Genesis block encoding no service parameter.

The number of declarations is a property of the Genesis block rather than of any single Operation, and is the one [Initial Service Declarations](#initial-service-declarations) requires.

During normal operations, Blend services would wait until a block is deep enough to be finalized, but for the Genesis block, we consider it finalized by definition and so Blend will immediately use the provider set without the usual finalization delay.

# References

- Ouroboros Praos: [https://eprint.iacr.org/2017/573.pdf](https://eprint.iacr.org/2017/573.pdf)
- Ouroboros Genesis: [https://eprint.iacr.org/2018/378.pdf](https://eprint.iacr.org/2018/378.pdf)
- Ouroboros Crypsinous: [https://eprint.iacr.org/2018/1132.pdf](https://eprint.iacr.org/2018/1132.pdf)
- Cardano Shelley Genesis File Format: [https://cardano-course.gitbook.io/cardano-course/handbook/protocol-parameters-and-configuration-files/shelley-genesis-file](https://cardano-course.gitbook.io/cardano-course/handbook/protocol-parameters-and-configuration-files/shelley-genesis-file)
- Cardano CIP-16 Key Serialisation: [https://cips.cardano.org/cip/CIP-16](https://cips.cardano.org/cip/CIP-16)
