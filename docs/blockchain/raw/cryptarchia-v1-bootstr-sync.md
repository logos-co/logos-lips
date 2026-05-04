# CRYPTARCHIA-V1-BOOTSTRAPPING-SYNCHRONIZATION

| Field | Value |
| --- | --- |
| Name | Cryptarchia v1 Bootstrapping & Synchronization |
| Slug | 96 |
| Status | raw |
| Category | Standards Track |
| Editor | Youngjoon Lee <youngjoon@status.im> |
| Contributors | David Rusu <david@status.im>, Giacomo Pasini <giacomo@status.im>, Álvaro Castro-Castilla <alvaro@status.im>, Daniel Sanchez Quiros <daniel@status.im>, Filip Dimitrijevic <filip@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/blockchain/raw/cryptarchia-v1-bootstr-sync.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/blockchain/raw/cryptarchia-v1-bootstr-sync.md) — Chore/mdbook updates (#258)

<!-- timeline:end -->

## Abstract

This document specifies the bootstrapping and synchronization protocol
for Cryptarchia v1 consensus.
When a new node joins the network or a previously-bootstrapped node has been offline,
it must catch up with the most recent honest chain
by fetching missing blocks from peers before listening for new blocks.
The protocol defines mechanisms for setting fork choice rules,
downloading blocks, and handling orphan blocks
while mitigating long range attacks.

**Keywords:** bootstrapping, synchronization, fork choice, initial block download,
orphan blocks, long range attacks, checkpoint

## Semantics

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## Background

This protocol defines the bootstrapping mechanism
that covers all of the following cases:

- From the **Genesis** block
- From the **checkpoint** block obtained from a trusted checkpoint provider
- From the **local block tree**
  (with $B_\text{imm}$ newer than the Genesis and the checkpoint)

Additionally, the protocol defines the synchronization mechanism
that handles orphan blocks while listening for new blocks
after the bootstrapping is completed.

The protocol consists of the following key components:

- Determining the fork choice rule (Bootstrap or Online) at startup
- Switching the fork choice rule from Bootstrap to Online
- Downloading blocks from peers

Upon startup, a node **determines the fork choice rule**,
as defined in Setting the Fork Choice Rule.
If the Bootstrap rule is selected, it is maintained for the Prolonged Bootstrap Period,
after which the node switches to the Online rule.

Using the chosen fork choice rule, a node will **download blocks**
to catch up with the head (also known as the tip) of each peer's local chain $c_{loc}$.

After downloading is done, the node starts **listening for new blocks**.
Upon receiving a new block, the node validates and adds it to its local block tree.
If the ancestors of the block are missing from the local block tree,
the node downloads missing ancestors using the same mechanism as above.

## Protocol

### Constants

| Constant | Name | Description | Value |
| -------- | ---- | ----------- | ----- |
| $T_\text{offline}$ | Offline Grace Period | A period during which a node can be restarted without switching to the Bootstrap rule. | 20 minutes |
| $T_\text{boot}$ | Prolonged Bootstrap Period | A period during which Bootstrap fork choice rule must be continuously used after Initial Block Download is completed. This gives nodes additional time to compare their synced chain with a broader set of peers. | 24 hours |
| $s_\text{gen}$ | Density Check Slot Window | A number of slots used by density check of Bootstrap rule. This constant is defined in Cryptarchia Fork Choice Rule - Definitions. | $\lfloor\frac{k}{4f}\rfloor$ (=4h30m) |

### Setting the Fork Choice Rule

Upon startup, a node sets the fork choice rule to the **Bootstrap** rule
in one of the following cases.
Otherwise, the node uses the **Online** fork choice rule.

- **A node is starting with $B_\text{imm}$ set to the Genesis block
  or from a checkpoint block.**

  The node is setting its latest immutable block $B_\text{imm}$
  to the Genesis or a checkpoint,
  which clearly indicates that the node intends to catch up with the subsequent blocks.
  Regardless of how many subsequent blocks remain,
  the node SHOULD use the Bootstrap rule to mitigate long range attacks.

- **A node is restarting after being offline longer than $T_\text{offline}$ (20 minutes).**

  Unlike starting from Genesis or checkpoint, in the case where a node is restarted
  while preserving its existing block tree,
  the node MUST choose a fork choice rule depending on how long it has been offline.

  If it is certain that a node has been offline longer than the offline grace period
  $T_\text{offline}$ since it last used the Online rule,
  the node uses the Bootstrap rule upon startup.
  Otherwise, it starts with the Online rule.

  Details of $T_\text{offline}$ are described in Offline Grace Period.
  A recommended way how to measure the offline duration
  is introduced in Offline Duration Measurement.

- **A node operator set the Bootstrap rule explicitly (e.g., by `--bootstrap` flag).**

  In any case where the node operator is clearly aware that the node has fallen behind
  by more than $k$ blocks,
  they SHOULD be able to start the node with the Bootstrap rule.
  For example, the operator may obtain the latest block height
  from another trusted operator
  and realize that their node has fallen significantly behind due to some issue.

### Initial Block Download

If peers for Initial Block Download (IBD) are configured,
a node performs IBD by downloading blocks to catch up with the tip
of the local chain $c_{loc}$ of each peer
using the fork choice rule chosen in Setting the Fork Choice Rule.

Blocks are downloaded in parent-to-child order,
as defined in the Downloading Blocks mechanism.
This mechanism applies not only when a node starts from the Genesis block,
but also when it already has the local block tree (or a checkpoint block).

```python
def initial_block_download(peers, local_tree):
    # In real implementation, these downloadings can be run in parallel.
    # Also, any optimization can be applied to minimize downloadings,
    # such as grouping peers by tip.
    for peer in peers:
        download_blocks(local_tree, peer, target_block=None)
```

The downloaded blocks are validated and added to the local block tree
using the fork choice rule determined above.

According to Cryptarchia v1 Protocol Specification - Block Header Validation,
the downloaded blocks are validated and added to the local block tree
using the fork choice rule determined above.

If all IBD peers become unavailable before the node catches up
with at least one of the IBD peers,
the node is terminated with an error,
allowing the operator to restart the node with other IBD peers.

If downloading is done successfully,
the node starts listening for new blocks as described in Listening for New Blocks.

### Prolonged Bootstrap Period

After Initial Block Download is completed,
a node MUST maintain the Bootstrap fork choice rule during the Bootstrap Period $T_\text{boot}$,
if the node chose the Bootstrap rule at Setting the Fork Choice Rule.

The purpose of the Prolonged Bootstrap Period is giving a syncing node
additional time
to compare its synced chain with a broader set of peers.
In other words, it provides the node with an opportunity
to connect to different peers
and verify whether they are on the same chain.
If the syncing node has downloaded blocks only from peers within an isolated network,
the result of Initial Block Download may not reflect the honest chain
followed by the majority of the entire network.
To resolve such situations, the node SHOULD continue using the Bootstrap rule
while discovering additional peers,
allowing it to switch to a better chain if one is found.

Theoretically, the Bootstrap rule should be prolonged
until the node has seen a sufficient number of blocks
beyond the $s_\text{gen}$ slot window,
which is required for the density check of the Bootstrap rule to be meaningful.
However, if the node has seen a fork longer than $k$ blocks
from its divergence block during Initial Block Download,
it means that the node has already seen more slots than $s_\text{gen}$
with very high probability, considering the small size of $s_\text{gen} = k/(4f)$.
If the node has never seen any fork longer than $k$ blocks,
it means that all forks could have been handled by the longest chain rule,
which is part of the Bootstrap rule.
Therefore, this protocol does not explicitly wait $s_\text{gen}$ slots
after Initial Block Download.
In other words, the protocol does not use $s_\text{gen}$
to configure the Prolonged Bootstrap Period.

This protocol configures the Bootstrap Period to 24 hours.

A timer MUST be started when Listening for New Blocks is started
after Initial Block Download is completed.
Once the timer is completed, the fork choice rule is switched to the Online rule.

### Listening for New Blocks

Once Initial Block Download is complete and Prolonged Bootstrap Period is started,
a node starts listening for new blocks relayed by its peers.

Upon receiving a new block,
the node tries to validate and add it to its local block tree,
as defined in Cryptarchia v1 Protocol Specification - Chain Maintenance.

If the parent of the block is missing from the local block tree,
the block cannot be fully validated and added.
These blocks are called *orphan blocks*.
To handle an orphan block,
the node downloads missing blocks from a randomly selected peer,
as described in Downloading Blocks.
If the request fails, the node MAY retry with different peers
before abandoning the orphan block.
The retry policy can be configured by implementers.

Note that downloading missing blocks does not need to be triggered
if it is clear that the orphan block is in a fork
diverged before the latest immutable (committed) block,
as the node MUST never revert immutable blocks.

```python
def listen_and_process_new_blocks(fork_choice: ForkChoice,
                                  local_tree: Tree,
                                  peers: List[Node]):
    for block in listen_for_new_blocks():
        try:
            # Run the chain maintenance defined in the Cryptarchia spec.
            local_tree.on_block(block, fork_choice)
        except InvalidBlock:
            continue
        except ParentNotFound:
            # Ignore the orphan block proactively,
            # if it's clear that the orphan block is in a fork
            # behind the latest immutable block
            # because immutable blocks should never be reverted.
            # This check doesn't cover all cases, but the uncovered cases
            # will be handled by the Cryptarchia block validation
            # during the `download_blocks` below.
            if block.height <= local_tree.latest_immutable_block().height:
                continue
            # In real implementation, downloading can be run in background
            # with the retry policy.
            download_blocks(local_tree, random.choice(peers),
                            target_block=block.id)
```

### Downloading Blocks

For performing Initial Block Download and handling orphan blocks
while Listening for New Blocks,
a node sends a `DownloadBlocksRequest` to a peer,
which MUST respond with blocks in parent-to-child order.
This communication should be implemented based on Libp2p streaming.

#### Libp2p Protocol ID

- Mainnet: `/nomos/cryptarchia/sync/1.0.0`
- Testnet: `/nomos-testnet/cryptarchia/sync/1.0.0`

```python
class DownloadBlocksRequest:
    # Ask blocks up to the target block.
    # The response may not contain the target block
    # if the responder limits the number of blocks returned.
    # In that case, the requester must repeat the request.
    target_block: BlockId
    # To allow the peer to determine the starting block to return.
    known_blocks: KnownBlocks

class KnownBlocks:
    local_tip: BlockId
    latest_immutable_block: BlockId
    # Additional known blocks.
    # A responder will reject a request if this list contains more than 5.
    additional_blocks: list[BlockId]

class DownloadBlocksResponse:
    # A stream of blocks in parent-to-child order.
    # The max number of blocks to be returned can be limited by implementers.
    # A requester can read the stream until the stream returns "NoMoreBlock".
    blocks: Stream[Block | "NoMoreBlock"]
```

The responding peer uses `KnownBlocks` to determine the optimal starting block
for the response stream, aiming to minimize the number of blocks to be returned.
The requesting node can include any block it believes could assist in this process
to the `KnownBlocks.additional_blocks`.
To avoid spamming responders,
the size of `KnownBlocks.additional_blocks` is limited to 5.

The responding peer finds the latest common ancestor (i.e. LCA)
between the `target_block` and each of the known blocks.
Then, it returns a stream of blocks, starting from the highest LCA.
To mitigate malicious downloading requests,
the peer limits the number of blocks to be returned.
The detailed implementation is up to implementers,
depending on their internal architecture (e.g. storage design).

The requesting node SHOULD repeat `DownloadBlocksRequest`s
by updating the `KnownBlocks` in order to download the next batches of blocks.
The following code shows how the requesting node can be implemented.

```python
def download_blocks(local_tree: Tree, peer: Node,
                    target_block: Optional[BlockId]):
    latest_downloaded: Optional[Block] = None
    while True:
        # Fetch the peer's tip if target is not specified.
        target_block = target_block if target_block is not None else peer.tip()
        # Don't start downloading if target is already in local.
        if local_tree.has(target_block):
            return

        req = DownloadBlocksRequest(
            # If target_block is None, specify the current peer's tip
            # each time when building DownloadBlocksRequest,
            # so that the node can catch up with the most recent peer's tip.
            target_block=target_block,
            known_blocks=KnownBlocks(
                local_tip=local_tree.tip().id,
                latest_immutable_block=local_tree.latest_immutable_block().id,
                # Provide the latest downloaded block as well
                # to avoid downloading duplicate blocks
                additional_blocks=[latest_downloaded.id]
                    if latest_downloaded is not None else [],
            )
        )
        resp = send_request(peer, req)

        for block in resp.blocks():
            latest_downloaded = block
            try:
                # Run the chain maintenance defined in the Cryptarchia spec.
                local_tree.on_block(block)
                # Early stop if the target has been reached.
                if block == req.target_block:
                    break
            except:
                return
```

If the node is continuing from a previous `DownloadBlocksRequest`,
it is important to include the latest downloaded block
to the `KnownBlocks.additional_blocks` to avoid downloading duplicate blocks.

If the requesting node is downloading blocks up to the peer's tip $c_{loc}$
(e.g. Initial Block Download) by repeating `DownloadBlocksRequest`s,
the $c_{loc}$ may switch between requests.
The algorithm described above also handles this case
by specifying the most recent peer's tip each time
when a `DownloadBlocksRequest` is constructed.

### Bootstrapping from Checkpoint

Instead of bootstrapping from the Genesis block or from the local block tree,
a node can choose to bootstrap the honest chain
starting from a checkpoint block obtained from a trusted checkpoint provider.
A checkpoint provider is a trusted service (which MAY be a Nomos node
or a dedicated server) that provides recent blockchain snapshots.
In this case, the node fully trusts the checkpoint provider
and considers blocks deeper than the checkpoint block as immutable
(including the checkpoint block itself).

A trusted checkpoint provider exposes a HTTP endpoint,
allowing nodes to download the checkpoint block and the corresponding ledger state.
The details are defined in Checkpoint Provider HTTP API.

The bootstrapping node imports the downloaded checkpoint block and ledger state
before starting bootstrapping.
The imported checkpoint block is used as the latest immutable block $B_{imm}$
and the local chain tip $c_{loc}$.
Starting from the checkpoint block,
the same Initial Block Download is used to download blocks
up to the tip of the local chain of each peer.
As defined in Setting the Fork Choice Rule,
the Bootstrap fork choice rule MUST be used upon startup.

If it turns out that none of the peers' local chains are connected
to the checkpoint block,
the node is terminated with an error,
allowing the node operator to select a new checkpoint.

## Details

### Offline Grace Period

The offline grace period $T_\text{offline}$ is a period during which
a node can be restarted without switching to the Bootstrap rule.

This protocol configures $T_\text{offline}$ to 20 minutes.
Here are the advantages and disadvantages of a short period:

**Advantages:**

- Limits chances for malicious peers to build long alternative chains
  beyond the scope of the Online rule.
- Conservatively enables the Bootstrap rule to handle long forks.

**Disadvantages:**

- Even a short offline duration can too sensitively trigger the Bootstrap rule,
  which then lasts for the long Prolonged Bootstrap Period.

The following example explains why $T_\text{offline}$ SHOULD NOT be set too long:

- A local node stopped in the following situation.
  A malicious peer is building a fork which is now a little shorter ($k - d$)
  than the honest chain.
- The local node has been offline shorter than $T_\text{offline}$ and just restarted.
  As defined in this protocol, the Online fork choice rule is used
  because the offline duration is short.
- During the offline duration, the malicious peer made its fork longer
  by adding $k - d$ blocks.
  Now the fork is in the same length as the honest chain.
- If the malicious peer sends the fork to the restarted node
  faster than the honest peer,
  the restarted node will commit to the fork because it has $k$ new blocks.
  Even if the node later receives the honest chain from the honest peer,
  it cannot revert blocks that are already immutable.

### Offline Duration Measurement

As defined in [Setting the Fork Choice Rule](#setting-the-fork-choice-rule),
when a node is restarted,
it should be able to choose a proper fork choice rule
depending on how long it has been offline since it last used the Online rule.

It is considered unsafe to rely on any external information
(e.g. the slot or height of peer's tip) to check how long the node has been offline,
since such information could be manipulated as an attack vector.
Instead, it is recommended to employ a local method to measure the offline duration.

While the specific implementation is left to the discretion of implementers,
one approach is for the node to periodically record the current time to a local file
while it is running with the **Online** fork choice rule.
Upon restart, it can use this timestamp to calculate how long it has been offline.

### Checkpoint Provider HTTP API

A trusted checkpoint provider serves the `GET /checkpoint` API,
allowing users (which are not connected via p2p)
to download the latest checkpoint block and its corresponding ledger state.

```yaml
openapi: 3.0

paths:
  /checkpoint:
    get:
      responses:
        '200':
          description: OK
          content:
            multipart/mixed:
              schema:
                type: object
                properties:
                  checkpoint_block:
                    type: string
                    format: binary
                  checkpoint_ledger_state:
                    type: string
                    format: binary
```

## References

### Normative

- [Cryptarchia v1 Protocol Specification][cryptarchia-v1]
  \- Parent protocol specification
- [Cryptarchia Fork Choice Rule][fork-choice]
  \- Fork choice rule specification

### Informative

- [Cryptarchia v1 Bootstrapping & Synchronization][bootstrap-origin]
  \- Original bootstrapping and synchronization documentation
- [Libp2p Streaming][libp2p]
  \- Peer-to-peer networking library

[cryptarchia-v1]: https://nomos-tech.notion.site/Cryptarchia-v1-Protocol-Specification-21c261aa09df810cb85eff1c76e5798c
[fork-choice]: https://nomos-tech.notion.site/Cryptarchia-Fork-Choice-Rule
[bootstrap-origin]: https://nomos-tech.notion.site/Cryptarchia-v1-Bootstrapping-Synchronization-1fd261aa09df81ac94b5fb6a4eff32a6
[libp2p]: https://docs.libp2p.io/

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
