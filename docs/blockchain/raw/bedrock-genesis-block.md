# BEDROCK-GENESIS-BLOCK

| Field | Value |
| --- | --- |
| Name | Bedrock Genesis Block Specification |
| Slug | 90 |
| Status | raw |
| Category | Standards Track |
| Editor | David Rusu <davidrusu@logos.co> |
| Contributors | Hong-Sheng Zhou, Thomas Lavaur <thomaslavaur@logos.co>, Marcin Pawlowski <marcin@logos.co>, Mehmet Gonen <mehmet@logos.co>, Álvaro Castro-Castilla <alvaro@logos.co>, Daniel Sanchez Quiros <danielsq@logos.co>, Filip Dimitrijevic <filip@logos.co> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/bedrock-genesis-block.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/bedrock-genesis-block.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This specification defines the Genesis Block for the Bedrock chain,
including the initial bedrock service providers, NMO token distribution,
and protocol parameters.
The Genesis Block is the root of trust for all subsequent protocol operations
and must be constructed in a way that is deterministic, verifiable,
and robust against long-range or bootstrap attacks.

**Keywords:** genesis block, token distribution, epoch nonce, service providers,
Cryptarchia initialization, ledger state

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Definitions

| Terminology | Description |
| ----------- | ----------- |
| Genesis Block | The first block in the Bedrock chain establishing the initial state. |
| NMO | The native token of the Nomos network. |
| Epoch Nonce | The source of randomness for the Cryptarchia lottery. |
| Service Provider | A node participating in DA or Blend network services. |
| Ledger Transaction | A transaction that modifies the token ledger state. |
| Mantle Transaction | A transaction containing operations and a ledger transaction. |

## Background

The block body is a single Mantle Transaction
containing a Ledger Transaction distributing the notes to initial token holders.
The bedrock services are initialized through `SDP_DECLARE` Operations
embedded in the Mantle Transaction's Operations list
and protocol initializing constants are encoded through a `CHANNEL_INSCRIBE` Operation
also embedded in the Operations list.

Not all protocol constants are encoded in the Genesis block.
The principle used to decide
whether a value should be in the Genesis block or not
is whether it is a value that is derived from blockchain activity
or whether it is updated through a protocol update (hard / soft fork).
For example, the epoch nonce is updated through normal blockchain Operations
and therefore it should be specified in the Genesis block.
Gas constants are only changed through protocol updates and hard forks
and therefore they will be hardcoded in the node implementation.

## Genesis Block Data Structure

The Genesis Block is composed of the Genesis Block Header
and the Genesis Mantle Transaction
(there is a single transaction in the genesis block).
The Mantle Transaction contains all information necessary
for initializing Bedrock Services and Cryptarchia state,
as well as distributing the initial tokens to stakeholders.

### Initial Token Distribution

Initial tokens will be distributed through a Ledger Transaction
containing zero inputs and one output note for each initial stakeholder.
Note that since the Ledger is transparent,
the initial stake allocation is visible to everyone.
Those wishing to hide their initial stake may opt to subdivide their note
into a few different notes of equal value.

In order to participate in the Cryptarchia lottery,
stakeholders must generate their note keys in accordance with
the Proof of Leadership protocol specified at
[Proof of Leadership Specification - Protocol][pol-protocol].

The initial state of the Ledger will be derived
through normal execution of this Ledger Transaction,
that is, each output's note ID will be added to the unspent notes set.

#### Initial Token Distribution Example

```python
STAKE_DISTRIBUTION_TX = LedgerTx(
    inputs=[],
    outputs=[
        Note(value=1000, public_key=STAKE_HOLDER_0_PK),
        Note(value=2000, public_key=STAKE_HOLDER_1_PK),
        Note(value=1500, public_key=STAKE_HOLDER_2_PK),
        # ...
    ]
)
```

### Initial Service Declarations

Data Availability (DA) and Blend Network MUST initialize their set of providers.
This is done through a set of `SDP_DECLARE` Operations
in the Genesis Mantle Transaction.

Both Blend and DA enforce a minimal network size for the service to be active.
Thus, in order to have active Blend and DA services at Genesis,
there MUST be at least as many declarations for each service
in the Genesis block to meet each service's minimal network size:

- **DA** — [NomosDA Specification - Minimum Network Size][nomosda-min-size]
- **Blend** — [Blend Protocol - Minimal Network Size][blend-min-size]

#### Initial Service Declarations Example

```python
DA_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(
            ServiceType.DA,
            ["ip://1.1.1.1:3000"],
            PROVIDER_ID_0,
            ZK_ID_0
        ),
        locked_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
    ),
    # ... 40 total declarations
]

BLEND_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(
            ServiceType.BLEND,
            ["ip://1.1.1.1:3000"],
            PROVIDER_ID_0,
            ZK_ID_0
        ),
        locked_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
    ),
    # ... 32 total declarations
]

SERVICE_DECLARATIONS = DA_DECLARATIONS + BLEND_DECLARATIONS
```

### Cryptarchia Parameters

Cryptarchia is initialized with the following parameters:

- `genesis_time`: ISO 8601 encoded timestamp.

  Cryptarchia uses slots as a measure of time offset from some start time.
  This timestamp must be agreed upon by all nodes in order to have a common clock.

- `chain_id`: string.

  It is useful to differentiate testnets from mainnet.
  To avoid confusion, the chain ID is placed in the Genesis block
  to guarantee that the networks are disjoint.

- `genesis_epoch_nonce`: 32 bytes, hex encoded.

  The initial source of randomness for the Cryptarchia lottery.
  The process for selecting this value is described in detail
  at [Epoch Nonce Ceremony](#epoch-nonce-ceremony).

These parameters are encoded in the Genesis block
as an inscription sent to the null channel.

#### Cryptarchia Parameters Example

```python
CRYPTARCHIA_PARAMS = {
    "chain_id": "nomos-mainnet",
    "genesis_time": "2026-01-05T19:20:35Z",
    "genesis_epoch_nonce": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
}

CRYPTARCHIA_INSCRIPTION = Inscribe(
    channel=bytes(32),
    inscription=json.dumps(CRYPTARCHIA_PARAMS).encode("utf-8"),
    parent=bytes(32),
    signer=Ed25519PublicKey_ZERO,
)
```

## Epoch Nonce Ceremony

The initial epoch nonce value governs the Cryptarchia lottery randomness
for the first epoch.
It must be revealed AFTER the initial stake distribution has been frozen.
This is done to prevent any stakeholders from gaining an unfair advantage
from prior knowledge of the lottery randomness.

The protocol for generating the initial randomness nonce can be found below.

### Schedule Epoch Nonce Ceremony Event

The time of the epoch nonce ceremony must be fixed well in advance;
let `t` denote the time of the Epoch Nonce Ceremony, broadcast `t` widely.

The `STAKE_DISTRIBUTION_TX` must be finalized before `t`
to ensure a fair Cryptarchia slot lottery.

### Randomness Collection

The entropy is collected from multiple randomness sources:

- **Bitcoin block hash** immediately after time `t`, denoted as r₁.
  Block hash can be found on `blockchain.com`'s bitcoin block explorer,
  e.g. [blockchain.com/explorer/blocks/btc/905030][btc-block].

- **Ethereum block hash** immediately after time `t`, denoted as r₂.
  Block hash can be found in the `more details` section
  when viewing a block on etherscan,
  e.g. [etherscan.io/block/22894116][eth-block].

- **DRAND beacon value** for the round immediately after `t`, denoted as r₃.
  Use the `default` beacon, and find the round number corresponding to `t`.
  [api.drand.sh/v2/beacons/default/rounds/1234][drand-beacon].

[btc-block]: https://www.blockchain.com/explorer/blocks/btc/905030
[eth-block]: https://etherscan.io/block/22894116
[drand-beacon]: https://api.drand.sh/v2/beacons/default/rounds/1234

### Randomness Derivation

Once all above entropy contributions, i.e., r₁, r₂, r₃ are collected,
the initial epoch randomness η_GENESIS is computed as:

```text
η_GENESIS = H(r₁, r₂, r₃)
```

where H is a collision-resistant zkhash function.

## Genesis Mantle Transaction

The initial stake distribution, service declarations and Cryptarchia inscription
are components of the Genesis Mantle Transaction.
This is the single transaction that forms the body of the Genesis block.

```python
GENESIS_MANTLE_TX = MantleTx(
    ops=[CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
    ledger_tx=STAKE_DISTRIBUTION_TX,
    permanent_storage_gas_price=0,
    execution_gas_price=0
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

### Block Header Fields Example

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

## Sample Genesis Block

```python
# distribute NMO to all stakeholders
STAKE_DISTRIBUTION_TX = LedgerTx(
    inputs=[],
    outputs=[
        Note(value=1000, public_key=STAKE_HOLDER_0_PK),
        Note(value=2000, public_key=STAKE_HOLDER_1_PK),
        Note(value=1500, public_key=STAKE_HOLDER_2_PK),
        # ...
    ]
)

# set Cryptarchia parameters
CRYPTARCHIA_PARAMS = {
    "chain_id": "nomos-mainnet",
    "genesis_time": "2026-01-05T19:20:35Z",
    "genesis_epoch_nonce": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
}

CRYPTARCHIA_INSCRIPTION = Inscribe(
    channel=bytes(32),
    inscription=json.dumps(CRYPTARCHIA_PARAMS).encode("utf-8"),
    parent=bytes(32),
    signer=Ed25519PublicKey_ZERO,
)

# service declarations
DA_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(ServiceType.DA, ["ip://1.1.1.1:3000"], PROVIDER_ID_0, ZK_ID_0),
        locked_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
    ),
    # ... more declarations
]

BLEND_DECLARATIONS = [
    Declaration(
        msg=DeclarationMessage(ServiceType.BLEND, ["ip://1.1.1.1:3000"], PROVIDER_ID_0, ZK_ID_0),
        locked_note_id=STAKE_DISTRIBUTION_TX.output_note_id(0)
    ),
    # ... more declarations
]

SERVICE_DECLARATIONS = DA_DECLARATIONS + BLEND_DECLARATIONS

# build the genesis Mantle Transaction
GENESIS_MANTLE_TX = MantleTx(
    ops=[CRYPTARCHIA_INSCRIPTION] + SERVICE_DECLARATIONS,
    ledger_tx=STAKE_DISTRIBUTION_TX,
    gas_price=0,
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

## Initializing Bedrock

Bedrock is initialized by executing the Mantle Transaction
without validating the Ledger Transaction and Mantle Operations.
No validation or execution is done for the Genesis block header;
in particular, processing of `proof_of_leadership` is skipped.

### Mantle Ledger Initialization

The Ledger Transaction should be executed
without checking that the transaction is balanced.
However, other validations are checked,
e.g. that output note values are positive and smaller than the maximum allowed value.
The result of normal transaction execution adds all transaction outputs to the Ledger.

### Cryptarchia Initialization

The Mantle Transaction contains an inscription sent to the null channel
containing the parameters for initializing Cryptarchia.

The Cryptarchia slot clock is initialized to `genesis_time`,
`LIB` is set to the Genesis block and the epoch state is then initialized:

#### Initial Epoch State

Cryptarchia progresses in epochs
where the variables governing the lottery are fixed for the duration of an epoch
and the activity during that epoch is used
to derive the values of those variables for the next epoch.
These variables taken together are called the Epoch State.
(see [Cryptarchia v1 Protocol Specification - Epoch State][cryptarchia-epoch-state]).

To initialize the Epoch State, the epoch variables are derived from the genesis block.

1. η: the epoch nonce is taken directly from the `genesis_epoch_nonce`.

1. C_LEAD: Eligible leader commitment is set to the Ledger Root
   over all notes from the initial token distribution.
   The derivation of this root is specified in
   [Proof of Leadership Specification - Ledger Root][pol-ledger-root].

1. D: The initial estimate of total stake
   will be the total tokens distributed at genesis.

### Bedrock Services Initialization

DA and Blend network are initialized through normal Mantle Transaction execution.
The `SDP_DECLARE` Operations in the Genesis Mantle Transaction
will create the initial set of providers in each service.

During normal operations, DA/Blend services would wait until a block is deep enough
to be finalized,
but for the Genesis block, it is considered finalized by definition
and so DA/Blend will immediately use the provider set
without the usual finalization delay.

## References

### Normative

- [Proof of Leadership Specification][pol-protocol] - Protocol for generating note keys
- [NomosDA Specification][nomosda-min-size] - Minimum Network Size requirements
- [Blend Protocol][blend-min-size] - Minimal Network Size requirements
- [Cryptarchia v1 Protocol Specification][cryptarchia-epoch-state] - Epoch State specification

### Informative

- [Bedrock Genesis Block][origin-ref] - Original specification document
- [Ouroboros Praos](https://eprint.iacr.org/2017/573.pdf) - Ouroboros Praos protocol
- [Ouroboros Genesis](https://eprint.iacr.org/2018/378.pdf) - Ouroboros Genesis protocol
- [Ouroboros Crypsinous](https://eprint.iacr.org/2018/1132.pdf) - Ouroboros Crypsinous protocol
- [Cardano Shelley Genesis File Format](https://cardanocourse.gitbook.io/cardano-course/handbook/protocol-parameters-and-configuration-files/shelley-genesis-file) - Cardano genesis file format
- [Cardano CIP-16 Key Serialisation](https://cips.cardano.org/cip/CIP-16) - Cardano key serialisation

[pol-protocol]: https://nomos-tech.notion.site/Proof-of-Leadership-Specification
[pol-ledger-root]: https://nomos-tech.notion.site/Proof-of-Leadership-Specification
[nomosda-min-size]: https://nomos-tech.notion.site/NomosDA-Specification
[blend-min-size]: https://nomos-tech.notion.site/Blend-Protocol
[cryptarchia-epoch-state]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification
[origin-ref]: https://nomos-tech.notion.site/Bedrock-Genesis-Block-21d261aa09df80bb8dc3c768802eb527

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
