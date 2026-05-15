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

# Order in which topics appear on the site (under "Logos Blockchain — The Bedrock").
TOPIC_ORDER = [
    "P2P Network",
    "Consensus",
    "Mantle",
    "Cryptoeconomics",
    "Blend Network",
    "Cryptography",
    "Data Availability",
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

# File path (relative to `docs/`) -> (topic, Notion display label).
# Bucket is taken from the file's `Status` metadata at generation time.
FILE_ASSIGNMENTS = {
    # P2P Network
    "blockchain/draft/p2p-network.md": ("P2P Network", "P2P Network"),
    "blockchain/raw/p2p-nat-solution.md": ("P2P Network", "P2P Nat Solution"),
    "blockchain/raw/p2p-network-bootstrapping.md": ("P2P Network", "P2P Network Bootstrapping"),
    "blockchain/raw/p2p-hardware-requirements.md": ("P2P Network", "Hardware Requirements"),

    # Consensus
    "blockchain/raw/nomos-cryptarchia-v1-protocol.md": ("Consensus", "Cryptarchia Protocol"),
    "blockchain/raw/cryptarchia-v1-bootstr-sync.md": ("Consensus", "Cryptarchia Bootstrapping & Synchronization"),
    "blockchain/raw/fork-choice.md": ("Consensus", "Cryptarchia Fork Choice Rule"),
    "blockchain/raw/cryptarchia-total-stake-inference.md": ("Consensus", "Total Stake Inference"),
    "blockchain/raw/cryptarchia-proof-of-leadership.md": ("Consensus", "Proof of Leadership"),
    "blockchain/deprecated/claro.md": ("Consensus", "Claro Consensus Protocol"),

    # Mantle
    "blockchain/raw/bedrock-architecture-overview.md": ("Mantle", "[Overview] Bedrock Architecture"),
    "blockchain/raw/bedrock-v1.1-mantle-specification.md": ("Mantle", "Mantle"),
    "blockchain/raw/bedrock-v1.1-block-construction.md": ("Mantle", "Block Construction, Validation and Execution"),
    "blockchain/raw/bedrock-genesis-block.md": ("Mantle", "Bedrock Genesis Block"),
    "blockchain/raw/bedrock-service-declaration-protocol.md": ("Mantle", "Service Declaration Protocol"),
    "blockchain/raw/bedrock-service-reward-distribution.md": ("Mantle", "Service Reward Distribution Protocol"),
    "blockchain/raw/nomos-wallet-technical-standard.md": ("Mantle", "Wallet Technical Standard"),
    "blockchain/raw/bedrock-anonymous-leaders-reward.md": ("Mantle", "Anonymous Leaders Reward Protocol"),

    # Blend Network
    "blockchain/raw/nomos-blend-protocol.md": ("Blend Network", "Blend Protocol"),
    "blockchain/raw/nomos-key-types-and-generation.md": ("Blend Network", "Key Types and Generation"),
    "blockchain/raw/nomos-proof-of-quota.md": ("Blend Network", "Proof of Quota"),
    "blockchain/raw/nomos-message-encapsulation.md": ("Blend Network", "Message Encapsulation Mechanism"),
    "blockchain/raw/nomos-message-formatting.md": ("Blend Network", "Message Formatting"),
    "blockchain/raw/nomos-payload-formatting.md": ("Blend Network", "Payload Formatting"),

    # Cryptography
    "blockchain/raw/digital-signature.md": ("Cryptography", "Digital Signature"),

    # Data Availability (not in current Notion outline; confirm placement with team).
    "blockchain/raw/nomosda-network.md": ("Data Availability", "DA Network"),
    "blockchain/raw/da-cryptographic-protocol.md": ("Data Availability", "DA Cryptographic Protocol"),
    "blockchain/raw/da-rewarding.md": ("Data Availability", "DA Rewarding"),
}

# Entries that exist in Notion but have not yet been migrated to GitHub.
# Render as draft (greyed) links so the full target structure stays visible.
PLACEHOLDERS = {
    "P2P Network": {
        "Merged": ["Network Wire Format"],
    },
    "Consensus": {
        "Merged": [
            "[Analysis] Cryptarchia De-anonymisation of Relative Stake",
            "[Analysis] Total Stake Inference",
            "[Analysis] Block Times & Blend Network",
        ],
    },
    "Mantle": {
        "Merged": [
            "Mantle Transaction Encoding",
            "[Template] Cross-Channel Messaging",
            "[Analysis] Gas Cost Determination",
        ],
    },
    "Cryptoeconomics": {
        "Merged": [
            "[Overview] Cryptoeconomics",
            "Block Rewards",
            "Execution Market",
            "Storage Markets",
            "[Analysis] Block Rewards",
            "[Analysis] Static Minimum Stake Estimation for Service Declaration Protocol",
            "[Analysis] Block Reward Parameter Calibration",
            "[Analysis] Storage Market",
            "[Analysis] Execution Market",
        ],
    },
    "Blend Network": {
        "Merged": [
            "[Analysis] Impact of the Service Declaration Protocol on the Statistical Inference",
            "[Analysis] Queuing System in the Mix Node",
            "[Analysis] Anonymity",
            "[Analysis] Correlation Functions",
            "[Analysis] Communication on Trees",
            "[Analysis] Resilience and Anonymity",
            "[Analysis] Latency",
        ],
    },
    "Cryptography": {
        "Merged": [
            "Common Cryptographic Components",
            "Trusted Setup Ceremony",
        ],
    },
}

# Label for the group containing all topics.
BEDROCK_LABEL = "Logos Blockchain — The Bedrock"


def buckets_for_topic(topic: str) -> list:
    return TOPIC_BUCKETS.get(topic, DEFAULT_BUCKETS)
