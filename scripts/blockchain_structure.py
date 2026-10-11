"""
Topic groupings for the Blockchain section in lip.logos.co.

Mirrors the layout at
https://nomos-tech.notion.site/Specifications-345261aa09df80bf968cd21b1e3e9563

`gen_summary.py` reads this config when building SUMMARY.md entries for
blockchain. Each existing spec file is placed under its mapped topic, and
the bucket is derived from the file's `Status` metadata field at
generation time. Notion-only entries that have not yet been migrated to
GitHub are emitted as draft (greyed) links so the full target structure
stays visible to readers and reviewers.
"""

# Order in which topics appear on the site (under "Bedrock").
TOPIC_ORDER = [
    "P2P Network",
    "Consensus",
    "Mantle",
    "Cryptoeconomics",
    "Blend Network",
    "Cryptography",
    "Data Availability",
]

# Top-level topic groups under Blockchain.
GROUPS = [
    ("Bedrock", TOPIC_ORDER),
    ("LEZ", ["LEZ"]),
]

# Default per-topic bucket order. Override below if a topic uses a different set.
DEFAULT_BUCKETS = ["Merged", "Stable", "Deprecated", "Retired", "Deleted"]

# Per-topic bucket overrides where Notion uses a different set.
TOPIC_BUCKETS = {
    "P2P Network": ["Merged", "Stable", "Deprecated", "Retired"],
}

# COSS `Status` field -> Notion bucket name.
STATUS_TO_BUCKET = {
    "raw": "Merged",
    "draft": "Merged",
    "approved": "Merged",
    "stable": "Stable",
    "verified": "Stable",
    "deprecated": "Deprecated",
    "retired": "Retired",
    "deleted": "Deleted",
}

# File path (relative to `docs/`) -> (topic/group key, Notion display label).
# Bucket is taken from the file's `Status` metadata at generation time.
FILE_ASSIGNMENTS = {
    # P2P Network
    "blockchain/draft/p2p-network.md": ("P2P Network", "P2P Network"),
    "blockchain/raw/p2p-nat-solution.md": ("P2P Network", "P2P Nat Solution"),
    "blockchain/raw/p2p-network-bootstrapping.md": ("P2P Network", "P2P Network Bootstrapping"),
    "blockchain/deprecated/p2p-hardware-requirements.md": ("P2P Network", "Hardware Requirements"),
    "blockchain/raw/network-wire-format.md": ("P2P Network", "Network Wire Format"),

    # Consensus
    "blockchain/raw/cryptarchia-v1-protocol.md": ("Consensus", "Cryptarchia Protocol"),
    "blockchain/raw/cryptarchia-v1-bootstr-sync.md": ("Consensus", "Cryptarchia Bootstrapping & Synchronization"),
    "blockchain/raw/fork-choice.md": ("Consensus", "Cryptarchia Fork Choice Rule"),
    "blockchain/raw/cryptarchia-total-stake-inference.md": ("Consensus", "Total Stake Inference"),
    "blockchain/raw/cryptarchia-proof-of-leadership.md": ("Consensus", "Proof of Leadership"),
    "blockchain/deprecated/v1.0.0-cryptarchia-proof-of-leadership.md": ("Consensus", "[1.0.0] Proof of Leadership"),
    "blockchain/deprecated/claro.md": ("Consensus", "Claro Consensus Protocol"),
    "blockchain/raw/analysis-cryptarchia-de-anonymisation-of-relative-stake.md": ("Consensus", "[Analysis] Cryptarchia De-anonymisation of Relative Stake"),
    "blockchain/raw/analysis-total-stake-inference.md": ("Consensus", "[Analysis] Total Stake Inference"),
    "blockchain/raw/analysis-block-times-blend-network.md": ("Consensus", "[Analysis] Block Times & Blend Network"),

    # Mantle
    "blockchain/raw/bedrock-architecture-overview.md": ("Mantle", "[Overview] Bedrock Architecture"),
    "blockchain/deprecated/v1.0.0-bedrock-architecture-overview.md": ("Mantle", "[1.0.0] [Overview] Bedrock Architecture"),
    "blockchain/raw/bedrock-v1.1-mantle-specification.md": ("Mantle", "Mantle"),
    "blockchain/raw/proof-of-work.md": ("Mantle", "Proof of Work"),
    "blockchain/deprecated/v1.4.0-mantle.md": ("Mantle", "[1.4.0] Mantle"),
    "blockchain/deprecated/v1.3.0-mantle.md": ("Mantle", "[1.3.0] Mantle"),
    "blockchain/deprecated/v1.2.1-mantle.md": ("Mantle", "[1.2.1] Mantle"),
    "blockchain/deprecated/v1.2.0-mantle.md": ("Mantle", "[1.2.0] Mantle"),
    "blockchain/deprecated/v1.1.0-mantle.md": ("Mantle", "[1.1.0] Mantle"),
    "blockchain/deprecated/v1.0.0-mantle.md": ("Mantle", "[1.0.0] Mantle"),
    "blockchain/raw/bedrock-v1.1-block-construction.md": ("Mantle", "Block Construction, Validation and Execution"),
    "blockchain/deprecated/v1.1.0-bedrock-block-construction.md": ("Mantle", "[1.1.0] Block Construction, Validation and Execution"),
    "blockchain/deprecated/v1.1.0-bedrock-block-construction-alt.md": ("Mantle", "[1.1.0] Block Construction, Validation and Execution_2"),
    "blockchain/deprecated/v1.0.0-bedrock-block-construction.md": ("Mantle", "[1.0.0] Block Construction, Validation and Execution"),
    "blockchain/raw/bedrock-genesis-block.md": ("Mantle", "Bedrock Genesis Block"),
    "blockchain/deprecated/v1.1.0-bedrock-genesis-block.md": ("Mantle", "[1.1.0] Bedrock Genesis Block"),
    "blockchain/deprecated/v1.0.0-bedrock-genesis-block.md": ("Mantle", "[1.0.0] Bedrock Genesis Block"),
    "blockchain/raw/bedrock-service-declaration-protocol.md": ("Mantle", "Service Declaration Protocol"),
    "blockchain/raw/bedrock-service-reward-distribution.md": ("Mantle", "Service Reward Distribution Protocol"),
    "blockchain/deprecated/v1.1.0-bedrock-service-reward-distribution.md": ("Mantle", "[1.1.0] Service Reward Distribution Protocol"),
    "blockchain/deprecated/v1.0.0-bedrock-service-reward-distribution.md": ("Mantle", "[1.0.0] Service Reward Distribution Protocol"),
    "blockchain/raw/wallet-technical-standard.md": ("Mantle", "Wallet Technical Standard"),
    "blockchain/raw/bedrock-anonymous-leaders-reward.md": ("Mantle", "Anonymous Leaders Reward Protocol"),
    "blockchain/raw/mantle-transaction-encoding.md": ("Mantle", "Mantle Transaction Encoding"),
    "blockchain/deprecated/v1.3.0-mantle-transaction-encoding.md": ("Mantle", "[1.3.0] Mantle Transaction Encoding"),
    "blockchain/deprecated/v1.2.0-mantle-transaction-encoding.md": ("Mantle", "[1.2.0] Mantle Transaction Encoding"),
    "blockchain/deprecated/v1.1.0-mantle-transaction-encoding.md": ("Mantle", "[1.1.0] Mantle Transaction Encoding"),
    "blockchain/deprecated/v1.0.0-mantle-transaction-encoding.md": ("Mantle", "[1.0.0] Mantle Transaction Encoding"),
    "blockchain/raw/template-cross-channel-messaging.md": ("Mantle", "[Template] Cross-Channel Messaging"),
    "blockchain/deprecated/v1.1.0-template-cross-channel-messaging.md": ("Mantle", "[1.1.0][Template] Cross-Channel Messaging"),
    "blockchain/deprecated/v1.0.0-template-cross-channel-messaging.md": ("Mantle", "[1.0.0] [Template] Cross-Channel Messaging"),
    "blockchain/raw/analysis-gas-cost-determination.md": ("Mantle", "[Analysis] Gas Cost Determination"),
    "blockchain/deprecated/v1.4.0-analysis-gas-cost-determination.md": ("Mantle", "[1.4.0][Analysis] Gas Cost Determination"),
    "blockchain/deprecated/v1.3.0-analysis-gas-cost-determination.md": ("Mantle", "[1.3.0] [Analysis] Gas Cost Determination"),
    "blockchain/deprecated/v1.2.0-analysis-gas-cost-determination.md": ("Mantle", "[1.2.0] [Analysis] Gas Cost Determination"),
    "blockchain/deprecated/v1.1.0-analysis-gas-cost-determination.md": ("Mantle", "[1.1.0] [Analysis] Gas Cost Determination"),
    "blockchain/deprecated/v1.0.0-analysis-gas-cost-determination.md": ("Mantle", "[1.0.0] [Analysis] Gas Cost Determination"),

    # Cryptoeconomics
    "blockchain/raw/overview-cryptoeconomics.md": ("Cryptoeconomics", "[Overview] Cryptoeconomics"),
    "blockchain/raw/block-rewards.md": ("Cryptoeconomics", "Block Rewards"),
    "blockchain/raw/execution-market.md": ("Cryptoeconomics", "Execution Market"),
    "blockchain/raw/storage-markets.md": ("Cryptoeconomics", "Storage Markets"),
    "blockchain/raw/analysis-block-rewards.md": ("Cryptoeconomics", "[Analysis] Block Rewards"),
    "blockchain/raw/analysis-static-minimum-stake-estimation-for-service-declaration-protocol.md": ("Cryptoeconomics", "[Analysis] Static Minimum Stake Estimation for Service Declaration Protocol"),
    "blockchain/raw/analysis-block-reward-parameter-calibration.md": ("Cryptoeconomics", "[Analysis] Block Reward Parameter Calibration"),
    "blockchain/raw/analysis-storage-market.md": ("Cryptoeconomics", "[Analysis] Storage Market"),
    "blockchain/raw/analysis-execution-market.md": ("Cryptoeconomics", "[Analysis] Execution Market"),

    # Blend Network
    "blockchain/raw/blend-protocol.md": ("Blend Network", "Blend Protocol"),
    "blockchain/raw/key-types-and-generation.md": ("Blend Network", "Key Types and Generation"),
    "blockchain/raw/proof-of-quota.md": ("Blend Network", "Proof of Quota"),
    "blockchain/deprecated/v1.0.0-proof-of-quota.md": ("Blend Network", "[1.0.0] Proof of Quota"),
    "blockchain/raw/message-encapsulation.md": ("Blend Network", "Message Encapsulation Mechanism"),
    "blockchain/raw/message-formatting.md": ("Blend Network", "Message Formatting"),
    "blockchain/raw/payload-formatting.md": ("Blend Network", "Payload Formatting"),
    "blockchain/raw/analysis-impact-of-the-service-declaration-protocol-on-the-statistical-inference-of-relative-stake.md": ("Blend Network", "[Analysis] Impact of the Service Declaration Protocol on the Statistical Inference of Relative Stake"),
    "blockchain/raw/analysis-queuing-system-in-the-mix-node.md": ("Blend Network", "[Analysis] Queuing System in the Mix Node"),
    "blockchain/raw/analysis-anonymity.md": ("Blend Network", "[Analysis] Anonymity"),
    "blockchain/raw/analysis-correlation-functions.md": ("Blend Network", "[Analysis] Correlation Functions"),
    "blockchain/raw/analysis-communication-on-trees.md": ("Blend Network", "[Analysis] Communication on Trees"),
    "blockchain/raw/analysis-resilience-and-anonymity.md": ("Blend Network", "[Analysis] Resilience and Anonymity"),
    "blockchain/raw/analysis-latency.md": ("Blend Network", "[Analysis] Latency"),

    # Cryptography
    "blockchain/deprecated/digital-signature.md": ("Cryptography", "Digital Signature"),
    "blockchain/raw/common-cryptographic-components.md": ("Cryptography", "Common Cryptographic Components"),
    "blockchain/raw/trusted-setup-ceremony.md": ("Cryptography", "Trusted Setup Ceremony"),

    # Data Availability
    "blockchain/deprecated/da-network.md": ("Data Availability", "DA Network"),
    "blockchain/deprecated/da-cryptographic-protocol.md": ("Data Availability", "DA Cryptographic Protocol"),
    "blockchain/deprecated/da-rewarding.md": ("Data Availability", "DA Rewarding"),

    # LEZ
    "blockchain/raw/lez/lee-v0.3-specifications.md": ("LEZ", "LEE v0.3 Specifications"),
}

# Entries that exist in Notion but have not yet been migrated to GitHub.
# Render as draft (greyed) links so the full target structure stays visible.
# All Notion-only specs from the initial structure PR (#339) have now been
# imported as real spec files (see FILE_ASSIGNMENTS); this dict is currently
# empty but kept for future Notion additions.
PLACEHOLDERS = {}

# Label for the group containing all topics.
BEDROCK_LABEL = "Bedrock"


def buckets_for_topic(topic: str) -> list:
    return TOPIC_BUCKETS.get(topic, DEFAULT_BUCKETS)
