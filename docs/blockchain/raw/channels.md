# CHANNELS

| Field | Value |
| --- | --- |
| Name | Channels |
| Slug | 248 |
| Status | raw |
| Category | Standards Track |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors |  |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision | 2026-09-21 |
| 1.1.0 | Added [pools](#pools): declared pool transitions, pool steps in answers, the collateral of a declared transition, and the pool parameters | 2026-09-21 |

# Introduction

Channels allow Zones to post their updates on chain. Channels form virtual chains that overlay on top of the Cryptarchia blockchain. Clients and Followers of a Zone can watch its channel to learn the state of that Zone. Each channel holds notes, which is what lets funds be bridged between Zones and Bedrock.

This document specifies how channels order their messages, how their sequencers take turns, and how the notes bridged into a channel move. The Operations that implement it and the state they maintain are specified in [Mantle](bedrock-v1.1-mantle-specification.md#channel-operations), to which `ChannelState`, `PendingInscription` and the Ledger belong, and the [Channel Resolution](bedrock-v1.1-mantle-specification.md#channel-resolution) that finalizes, undoes or takes out what they leave pending.

# Message Ordering

Channels form virtual chains by having each message reference its parent message. The order of messages in these channels is enforced by the sequencer by building a hash chain of messages, i.e. new messages reference the previous messages through a parent hash. Given that Cryptarchia has long finality times, these message parent references allow Zone sequencers to continue to post new updates to channels without having to wait for finality. No matter how Cryptarchia forks and reorgs, the channel messages from honest sequencers will eventually be re-included in a way that satisfies the virtual chain order.

A channel has a list of accredited keys, the keys allowed to write to it. The first time a message is sent to an unclaimed channel, the key that signs the initial message becomes the only accredited key in the list (note that this key may correspond to a threshold signature key). The accredited keys form a committee that can configure the channel and take turns to write messages to it following a round-robin algorithm. Configuring a channel includes modifying the list of accredited keys, the round-robin parameters and the required number of signatures to establish a new configuration.

Configurations form a second hash chain within the channel: each configuration names the configuration it supersedes, so a pending reconfiguration stays valid while the sequencer keeps posting inscriptions.

# Decentralized Sequencing

To determine which sequencer is currently authorized to send messages, we use a round-robin algorithm. When a message is posted to a channel, the following algorithm is used to determine who the sequencer actually is:

```python
# Round Robin algorithm determining the new sequencer index and the
# new sequencer starting slot
def round_robin(block_slot: Slot, channel: ChannelState) -> (uint16, uint64):
    elapsed_slots = block_slot - channel.tip_slot
    if elapsed_slots >= channel.posting_timeout and channel.posting_timeout != 0:
        # Get the number of sequencers that get timed out
        sequencers_timed_out = elapsed_slots // channel.posting_timeout
        index = (
            (channel.tip_sequencer + sequencers_timed_out)
            % len(channel.accredited_keys)
        )
        starting_slot = (
            channel.tip_slot
            + sequencers_timed_out * channel.posting_timeout
        )
    else:
        # Get the number of timeframes elapsed to get who is the sequencer
        tip_sequencer_duration = block_slot - channel.tip_sequencer_starting_slot
        index = (
            (channel.tip_sequencer + (tip_sequencer_duration // channel.posting_timeframe))
            % len(channel.accredited_keys)
        )
        starting_slot = (
            channel.tip_sequencer_starting_slot
            + (tip_sequencer_duration // channel.posting_timeframe) * channel.posting_timeframe
        )
    return (index, starting_slot)
```

# Bridging

Channels let their bridged funds keep participating in Proof of Stake. When a user deposits funds into a channel, the deposited notes stay on the ledger and are not turned into inert collateral. They are consumed and immediately re-created as channel notes that continue to count toward Proof of Stake and can still be used to create PoLs (see [Channel Notes](bedrock-v1.1-mantle-specification.md#channel-notes)). Two goals motivate this design:

- **More PoS participation, stronger security.** Funds deposited into a channel would otherwise leave the staking set. Keeping them as channel notes means the capital backing the application layer also backs consensus security, so bridging does not shrink the stake that secures the chain.
- **No split between security and application.** A user no longer has to choose between staking funds or using them in a channel. The same funds do both at once. They stay usable inside the channel while still earning Proof of Leadership rewards, so capital is never fragmented between the two.

**Custody and authorization.** A `CHANNEL_DEPOSIT` consumes the deposited notes and re-creates them with the same value and `ZkPublicKey` under a new `NoteId` derived from the deposit's `OpId`, registered in the ledger's `channel_notes` set. From then on the channel has custody: only the inscriptions of its sequencers move the note inside the channel, and they do so without any proof of the holder. That is what a channel note is: a note an inscription of its channel may consume. The `ZkPublicKey` keeps the meaning it has on an ordinary note. Its holder creates the note's PoLs, earns their rewards, and must [authorize](#authorizations) any move of the note. The ledger does not check authorizations when the inscription is posted. It checks them when someone [challenges](#challenges-and-answers) the inscription, and a move they do not back is undone.

**Ageing.** Because the deposit re-creates the notes under a new `NoteId`, a deposited note restarts the ageing process and must age again before it can create a PoL. Bridged funds still count toward Proof of Stake, so the goals above hold, but the participation is not continuous across the deposit. The same holds for every inscription that moves notes, which consumes its inputs and creates new notes.

**What each party can do.**

| Party | Can | Cannot |
|---|---|---|
| Holder of the note's `ZkPublicKey` | Create a PoL with the note and earn its rewards. Authorize a sequencer to move the note. Bond the note while it is neither [locked](#moving-notes) nor under withdrawal. Take the note out of the channel with a [withdrawal](#withdrawals), unless the holder bonded it | Use the note as service stake while it is a channel note. Take it out of the channel any other way |
| Channel sequencers | Post, on their turn, inscriptions applying authorizations, netting many of them into one move | Move a note for good without its holder's authorization |

What the ledger guarantees is consent: whatever the channel's configuration, no channel note is moved for good without its holder's authorization. It does not guarantee liveness. Sequencers holding the configuration threshold can refuse to post, and holders then leave with a [withdrawal](#withdrawals), which the sequencers cannot hold past the first unlock after its delay. Capturing a channel stalls it but does not give access to its funds. Value that no holder owns, an AMM reserve for instance, sits in a [pool](#pools), where the proof that a program ran stands for the authorization. The sections below describe the mechanism, [Parameters](#parameters) gives its constants, and [Mantle](bedrock-v1.1-mantle-specification.md#channel-operations) the state it keeps. [\[Template\] Bridged Zone](template-bridged-zone.md) shows how a Zone uses it and follows its channel, with a swap pool as an example.

## Authorizations

An authorization is a [`ZkSignature`](bedrock-v1.1-mantle-specification.md#zero-knowledge-signature-scheme-zksignature) by the keys of the channel notes it consumes over

```python
def auth_msg(inputs: list[NoteId], outputs: list[Note]) -> zkhash:
    return zkhash(
        FiniteField(b"CHANNEL_NOTE_AUTH_V1", byte_order="little", modulus=p),
        FiniteField(len(inputs), byte_order="little", modulus=p),
        *inputs,
        FiniteField(len(outputs), byte_order="little", modulus=p),
        *[x for note in outputs
            for x in (FiniteField(note.value, byte_order="little", modulus=p), note.public_key)])
```

It states which notes may be consumed and which notes must come out of them. The inputs determine the channel: a channel note belongs to one channel from its creation until it is consumed, and the outputs are created in that channel.

A holder hands an authorization to the Zone off chain, before the Mantle Transaction that will use it exists, which is why it signs the notes and not a transaction. The ledger sees it as payload data, in the steps of a `CHANNEL_ANSWER`. Each input can be consumed once, so an authorization applies once.

The notes an authorization creates have identifiers of their own, derived as if the authorization were an Operation:

```python
derive_note_id(auth_msg(inputs, outputs), index, outputs[index])
```

A later authorization may consume such a note by that identifier, which lets a Zone chain payments within one inscription: what one payment creates, the next one spends, and only what is left is created on the ledger.

## Moving Notes

A `CHANNEL_INSCRIBE` moves notes when its `inputs` are non-empty: it consumes them and creates its `outputs` in the channel. It advances the pools it names in `declared`. Posting checks only what is cheap: the inputs are notes of the channel that no withdrawal names, value is conserved, the declared pool states match the ledger, and the sequencer bonds the inscription's `required` collateral. No authorization or proof is checked. The outputs get their identifiers as the outputs of any Operation do, from the inscription's `OpId` and their index.

The inscription executes at once, but its outputs are **locked**. A locked note stays on the ledger, ages like any note, and may be consumed by a later inscription of the channel, but by no other Operation. Executing and locking, rather than delaying, lets a lost challenge be repaired by moving notes again instead of re-inserting consumed `NoteId`s, which must stay unique. For that repair, the pending inscription keeps the value and key of every input it consumed.

An inscription **depends on** the pending inscription that created each locked input it consumes, and on the most recent pending inscription that advanced each pool it declares, the one that wrote its `state_before`. Without the second edge, a pool could be drained in two steps: a false jump to a state where the poster owns the reserves, then a genuine transition out of it. A lost inscription is undone with every inscription that consumed a note it created, and with every inscription that consumed a note those created, and so on: every move built on the lost one is reverted. What is not reverted is the channel itself: the inscriptions stay on chain, the tip is unchanged, and an inscription that consumed only final notes stands, even if it was posted after the lost one.

An inscription is **final** once its own deadline has passed and every inscription it depends on is final. Its deadline is the end of its `CHALLENGE_WINDOW`; a challenge extends it by `RESPONSE_WINDOW`, and a proven inscription resolves at the start of the next block. Its lock then lifts, its bond is released, and nothing else changes.

An inscription is **lost** when its deadline passes with a challenge still open. It is undone together with every pending inscription that depends on it. The notes they consumed from outside that set are re-created under the same keys, the notes they created are removed, and the pools they advanced return to the state before the first of them. The re-created notes have new identifiers, so an authorization naming the old ones has to be signed again.

An inscription undone this way moves nothing any more, but its sequencer still answers for it. It stays challengeable until its own deadline, and forfeits its `required` only if its own challenge goes unanswered. Otherwise it is dropped once its deadline has passed. An answer reads only what the pending inscription recorded, so it stays possible after the undo.

A sequencer that built on an inscription later lost therefore loses its work, not its bond, provided it can answer for what it posted. An inscription nobody can answer for forfeits whether or not it was undone first, which is why an invalid one is worth challenging even when it is about to be undone. To spare its users the undo, a sequencer builds only on a pending inscription it could answer for itself, holding and having checked its authorizations and, for a pool, the transition it declares.

The [Channel Resolution](bedrock-v1.1-mantle-specification.md#channel-resolution) applies finality and losses at the start of each block, as a function of the chain and the slot alone.

## Challenges and Answers

Anyone may challenge a pending inscription before its deadline, bonding unlocked channel notes of the channel worth the inscription's `required`. Anyone may answer until the end of the response window. A bond is a list of notes, so that nobody has to merge notes to post one, and what it earns is paid to the key of its first note. An answer is an Operation like any other: a wrong one is invalid, and a valid one proves the inscription, the challenger's bond forfeiting the inscription's `required` to its sequencer under the inscription's forfeit identifier (see [Collateral](#collateral)). An inscription is challenged at most once. A proven one cannot be challenged again and resolves at the start of the next block whatever happens, so nobody can hold it pending, and whoever holds the authorizations of an inscription can finalize it early by challenging it and answering.

An inscription consumes any unlocked note of its channel without its holder's signature, so a challenger that deposited its bond in an earlier transaction could see a sequencer consume it in an inscription ordered first. A watcher therefore deposits and challenges in one Mantle Transaction: the Operations of a transaction execute in order, each against the state the preceding ones left, so the `CHANNEL_CHALLENGE` bonds the channel notes the `CHANNEL_DEPOSIT` before it creates, and nothing can consume them in between (see the [`CHANNEL_CHALLENGE` example](bedrock-v1.1-mantle-specification.md#channel_challenge)).

An answer is the full accounting of the inscription, as a list of steps: whether each input is consumed exactly once, and whether the outputs are exactly what the steps leave, can only be checked over all of them.

A **user step** applies one authorization: it consumes notes and creates notes. A `ZkSignature` proves every key of its list at once, so two authorizations signed apart cannot be combined in one step. A **pool step** applies one pool transition (see [Pools](#pools)). The notes a step consumes are inputs of the inscription or notes created by earlier steps, under the identifiers of [Authorizations](#authorizations) and of pool transitions.

Every note a step creates and no later step consumes is a **claim**. The inscription's outputs are the claims, in the order the steps created them, one note each: a recipient of several payments receives several notes. A zone fee is a claim written in a user's authorization, and a sequencer that wants one note out of its many fees consumes them in a step of its own, under an authorization it signs itself. Since the outputs are fully determined by the steps, a sequencer that posts other outputs loses the challenge.

An answer is valid when all of the following hold (see [`answer_holds`](bedrock-v1.1-mantle-specification.md#channel_answer)):

1. every note a step consumes is an input of the inscription, or a note created by an earlier step;
2. every input of the inscription is consumed by exactly one step, and every note a step creates by at most one;
3. every step conserves value and creates notes of positive value;
4. the claims, in the order the steps created them, equal the inscription's outputs;
5. every user step carries a valid authorization of its inputs and outputs;
6. every declared pool transition is proven by exactly one pool step, from notes whose value and key match, and every pool step proves a declared one.

The first check matters most, since an inscription is challenged once and a closed challenge is final: a step consuming a note the inscription never consumed would count value that is still on the ledger, and nothing would catch it later. Conservation holds per step because the outputs only balance in total. The last check stops an inscription from declaring a pool transition that no answer proves.

## Collateral

A sequencer bonds, with every inscription that moves notes or advances a pool, unlocked channel notes of the channel that it owns. Bonding a note locks it with the inscription, until the inscription is final, and the bond is forfeited if the inscription is lost. The inscription requires, at the prices of the block that includes it, the amount below, where the constants are the [parameters](#parameters) of the protocol and the prices those of the block:

```python
# TokenValue is the uint64 value of a Note, see Mantle
def fee_cost(execution_gas: uint64, storage_gas: uint64) -> TokenValue:
    return checked_uint64(execution_gas * execution_gas_base_price
                          + storage_gas * permanent_storage_gas_price)

def required_collateral(inputs: list[NoteId], declared: list[PoolTransition]) -> TokenValue:
    n, d = len(inputs), len(declared)
    # The value of every input, locked or not: consuming a locked note extends the lock
    # on its value, and each extension costs what the first lock cost. The reserves of
    # the declared pools carry a pool key and never stake.
    reserves = {pool_key(pools[transition.instance_id].image_id, transition.instance_id, 0) for transition in declared}
    input_value = sum(ledger.get_note(input).value for input in inputs
                      if ledger.get_note(input).public_key not in reserves)
    return checked_uint64(
        COLLATERAL_MARGIN * fee_cost(FLOOR_EXECUTION_GAS + INPUT_EXECUTION_GAS * n + STATE_EXECUTION_GAS * d,
                                     FLOOR_STORAGE_GAS + INPUT_STORAGE_GAS * n + STATE_STORAGE_GAS * d)
        + STATE_PROVING * d
        + uint128(input_value) * VALUE_RATE_PPM // 1_000_000)   # the product on 128 bits
```

and may be posted only with a bond worth at least that amount. The amount is recorded with the inscription, so later price changes do not alter it.

Each part pays for something, derived in [\[Analysis\] Channel Collateral](analysis-channel-collateral.md):

- The fee-priced part, with its margin, pays for the dispute. Its floor makes a right challenge worth a transaction and makes a wrong one pay for the fixed part of the answer it forced; each input and each declared transition adds what its step adds to that answer.
- `STATE_PROVING` pays for the off-chain proof a pool step needs, which gas does not price.
- The value part pays for the lock itself. An inscription that consumes a note locks its value until its own deadline, and one that consumes a final note restarts its ageing besides, even when it is later undone; keeping value out of the leadership lottery raises every other participant's share of the rewards. The value rate makes that unprofitable, and it is paid on every input, locked or not, so that extending a lock by consuming a locked note costs what the first lock cost. It is `VALUE_RATE_PPM` parts per million of the value, so the part is zero only for a value below 200 units, and the product is taken on 128 bits so that it cannot overflow.

A bond is made of unlocked channel notes of the channel, and bonding locks them as the inscription's outputs are locked, until the inscription is final. A locked note cannot be bonded: it belongs to a pending inscription, and its value is already at stake there. Bonded notes keep taking part in Proof of Stake, so collateral costs a sequencer liquidity rather than yield.

The requirement counts inputs, not outputs. Merging lets an inscription consume a thousand notes into one output, and it is the holders of the inputs who are locked out.

A lost inscription forfeits its `required`: half pays the challenger and the rest goes to the pending rewards pool, as fees do (see [Block Rewards](block-rewards.md)). The challenger gets only half because the challenger may be the sequencer itself, under a second key: paid in full, it would recover its forfeit and lock any number of notes for the price of gas. An inscription undone with it keeps its bond at risk and is judged on its own challenge, so a large inscription cannot escape its requirement by depending on a small one made to lose, and an honest one loses nothing. Locking `n` notes therefore costs `n` times the per-input requirement, while one challenge covers the whole inscription.

The forfeit is taken from the bond notes in order. The last note taken is split: the excess is re-created under the same key, in the channel, and the rest of the bond is released. The challenger's share is created in the channel too. A wrong challenge forfeits by the same rule: an answer takes exactly the inscription's `required` from the challenger's bond and pays it to the sequencer, in the channel, at the key of the first note of the inscription's bond. Everything a forfeit creates is created under the forfeit identifier of the inscription, derived from its `OpId`: an inscription is challenged at most once, so it forfeits at most once.

## Pools

A pool is value in a zone that no single user owns, such as an AMM reserve. Nobody can sign for it, so a Risc0 program governs it and a proof that the program ran replaces the authorization. The ledger keeps one `PoolEntry` per pool: its channel, its `image_id`, which names the program, and its state, which the ledger does not interpret. `instance_id` names the pool among those running the same program.

```python
def pool_key(image_id: ImageId, instance_id: InstanceId, intent_hash: zkhash) -> ZkPublicKey:
    return zkhash(
        FiniteField(b"RISC0_PROGRAM", byte_order="little", modulus=p),
        FiniteField(image_id, byte_order="little", modulus=p),
        instance_id,
        intent_hash)
```

Every note held by or sent to a pool carries a pool key. Reserves use `intent_hash = 0`. A deposit uses `intent_hash = zkhash(intent)`, the intent being what the sender wants done, in a form the program defines, typically a recipient, a minimum output, a refund key and a salt. Sending to a pool is an ordinary authorization with an output under the pool key. No secret key exists behind a pool key, so pool notes move only through pool steps.

The intent in the key ties the program's inputs to the deposit paying for them. A pool step gives the `intent_hash` of each note it consumes, and the ledger recomputes the note's key from it. The same `intent_hash` is in the journal the proof commits to, so the program was handed exactly the intent the note carries, and an answer cannot drop a swap and treat the deposit as a gift to the reserves. Two deposits with byte-identical intents would share a key and merge, which is why an intent carries a salt.

The ledger keeps each pool's state, so an answer cannot start from a state of its choosing, and only inscriptions of the pool's channel may advance it. An inscription declares, for each pool it advances, `state_before` and `new_state`; posting checks the first against the entry and writes the second, as it does for the channel tip. A pool advances at most once per inscription, everything that happened to it in the meantime folding into one transition. An inscription may declare a transition without moving any note, which a private pool needs to advance its roots, and the per-transition part of the collateral prices it, since it would otherwise cost nothing to post.

A pool step for the declared transition `s`, consuming `notes`, is valid when:

```python
image_id = pools[step.instance_id].image_id
for note, consumed in zip(notes, step.consumed):
    assert note.value == consumed.value
    assert note.public_key == pool_key(image_id, step.instance_id, consumed.intent_hash)
journal = PoolJournal(step.instance_id, s.state_before, s.new_state, step.consumed, step.created)
assert risc0_verify(image_id, sha256(encode(journal)), step.seal)
```

The value check matters as much as the key. Without it, an answer could state a deposit smaller than it is, the program would pay less, and the step would still balance against the real value, the difference going to an output of the answer's choice. The ledger checks ownership by hashing and the program checks intent and logic by proving. The ledger guarantees that the program ran from the recorded state and was handed every intent, not that it honours them: a program that ignores intents still produces valid proofs. [Risc0 Receipt Verification](bedrock-v1.1-mantle-specification.md#risc0-receipt-verification) specifies `risc0_verify`.

The notes a pool step creates have identifiers of their own, as the notes of an authorization do, derived from the transition:

```python
def transition_msg(s: PoolTransition) -> zkhash:
    return zkhash(
        FiniteField(b"POOL_TRANSITION_V1", byte_order="little", modulus=p),
        s.instance_id, s.state_before, s.new_state)

derive_note_id(transition_msg(s), index, created[index])
```

`POOL_CREATE` creates a pool with derived identifiers:

```python
def derive_instance_id(channel: ChannelId, image_id: ImageId, params_hash: zkhash) -> InstanceId:
    return zkhash(
        FiniteField(b"POOL_INSTANCE", byte_order="little", modulus=p),
        FiniteField(channel, byte_order="little", modulus=p),
        FiniteField(image_id, byte_order="little", modulus=p),
        params_hash)

def derive_pool_genesis(image_id: ImageId, params_hash: zkhash) -> zkhash:
    return zkhash(
        FiniteField(b"POOL_GENESIS", byte_order="little", modulus=p),
        FiniteField(image_id, byte_order="little", modulus=p),
        params_hash)
```

The ledger derives both. A creator choosing them could register the identifier users compute for themselves, so their deposits land, with a starting state in which it already owns the reserves, and no challenge would catch it. With derived identifiers, whoever creates a pool first creates the pool others wanted. A salt in the parameters separates two pools running the same program. Entries are never removed, and since creation is not part of an inscription, a lost inscription does not undo it.

## Withdrawals

A holder leaves without the sequencers, and only this way: no other Operation takes a note out of a channel. `CHANNEL_WITHDRAW` names channel notes of the holder, proven by the holder's `ZkSignature` over the `mantle_txhash`. `WITHDRAW_DELAY` slots later, at its `due`, the [Channel Resolution](bedrock-v1.1-mantle-specification.md#channel-resolution) takes each of them out as an ordinary note under the same key, at the first moment it is unlocked. What each state of a note allows:

| Note | Consumable by an inscription of the channel | Bondable | Nameable by `CHANNEL_WITHDRAW` | Consumable by any other Operation | The resolution |
| --- | --- | --- | --- | --- | --- |
| Unlocked | yes | yes | yes | no | nothing |
| Locked as a created output | yes | no | yes | no | unlocks it when final, removes it when lost |
| Bonded, by an inscription or a challenge | no | no | no | no | releases it, or forfeits from it |
| Under withdrawal, before `due` | yes | no | no | no | nothing yet |
| Under withdrawal, at or after `due` | no | no | no | no | takes it out at its first unlock |

The delay is a grace period for the sequencers, then a hard exit. A sequencer holding an authorization over a note is not denied it by a withdrawal posted before it had time to apply it. During the delay an inscription consumes a withdrawn note as if it were not withdrawn, its authorization checked on challenge as usual, and the note leaves the withdrawal as any consumed note does. After `due` nothing consumes it, and it leaves at the first moment it is unlocked, in the resolution of a block and before its transactions, so that nothing can relock it. A sequencer therefore applies an authorization over a withdrawn note before `due`, or drops it.

An undo treats the two kinds of withdrawn notes differently. A note consumed during the delay comes back under its withdrawal: the note the undo re-creates for it, same value and key under a new identifier, inherits it. That note leaves in the same resolution if `due` has passed and no standing creator relocks it, and at its first release if one does. A withdrawn note that an undone inscription created is removed with it and drops out of the withdrawal. Its value goes back to the inputs the undo re-creates, whose holders withdraw those again if they wish.

```
slot s               CHANNEL_WITHDRAW(channel, [a, b, c])   posted by the holder; a is unlocked, b is a locked output,
                                                            c is unlocked; none may be bonded any more
s + x, x < DELAY     an inscription consumes a with the holder's authorization; a leaves the withdrawal, b and c stay in it
s + WITHDRAW_DELAY   due: no inscription may consume b or c any more; c leaves in this resolution, b is still locked and stays
first unlock of b    b leaves in the resolution that unlocks it, before that block's transactions
later                the inscription that consumed a is lost: the note re-created for a inherits the withdrawal and
                     leaves in that same resolution, or at its first release if a standing creator relocks it
```

# Parameters

| Parameter | Value | Role |
| --- | --- | --- |
| `CHALLENGE_WINDOW` | 172,800 slots, 2 days | How long a posted inscription may be challenged |
| `RESPONSE_WINDOW` | 86,400 slots, 1 day | How long after the challenge window an answer may still arrive |
| `WITHDRAW_DELAY` | 86,400 slots, 1 day | How long a withdrawal waits before the ledger takes its notes out |
| `COLLATERAL_MARGIN` | 2 | Margin on the fee prices of the dispute |
| `FLOOR_EXECUTION_GAS`, `FLOOR_STORAGE_GAS` | 4,490, 796 | Fee-priced collateral of any inscription that moves notes or advances a pool |
| `INPUT_EXECUTION_GAS`, `INPUT_STORAGE_GAS` | 590, 395 | Fee-priced collateral per input |
| `STATE_EXECUTION_GAS`, `STATE_STORAGE_GAS` | 590, 275 | Fee-priced collateral per declared pool transition |
| `STATE_PROVING` | one GPU-hour, in LGO at the genesis price | Collateral per declared pool transition for its off-chain proof |
| `VALUE_RATE_PPM` | 5,000 parts per million, that is 0.5% | Collateral per unit of value of the inputs, the reserves of the declared pools excluded |
| `RISC0_CONTROL_ROOT`, `RISC0_BN254_CONTROL_ID`, `RISC0_GROTH16_VK` | those of the pinned Risc0 release | [Risc0 receipt verification](bedrock-v1.1-mantle-specification.md#risc0-receipt-verification) |

The windows are ledger parameters and not part of a channel's configuration, since a captured configuration would set them to zero. Each is longer than the finality depth $`\lfloor k/f \rfloor`$ of [Cryptarchia](cryptarchia-v1-protocol.md#constants), 64,800 slots or 18 hours. Keeping a challenge or an answer out of the chain for a whole window therefore takes every leader of that period refusing it, and a watcher that goes offline for a day still finds its inscriptions challengeable. `CHALLENGE_WINDOW + RESPONSE_WINDOW`, 3 days, stays below one epoch, 648,000 slots, and every inscription is resolved by that many slots after its posting.

The collateral parameters are derived in [\[Analysis\] Channel Collateral](analysis-channel-collateral.md). The fee-priced ones follow the Execution Gas and the Permanent Storage Gas of a challenge, of an answer's fixed part and of its steps. `STATE_PROVING` sizes the heaviest proof, a private pool's transition, and awaits a measurement on reference hardware. `VALUE_RATE_PPM` makes suppressing stake from the leadership lottery unprofitable while the inferred stake is below its target, and can fall towards 1,700 once it is reached. A challenger bonds what the inscription requires, so the same amounts are what a wrong challenge pays the sequencer for the answer it forced.

# Security Considerations

- **Watchtowers.** An unchallenged inscription becomes final, so a holder that does not watch the channel relies on someone challenging the inscriptions that move its notes without authorization. That includes its exit: a withdrawn note can be consumed until the withdrawal's `due`, and only a challenge returns it.
- **Delaying an exit.** A sequencer does not need to win a mempool race against a withdrawal. During the delay it may consume the withdrawn note without authorization and relock it, as the output of an inscription, for a challenge window. That costs it the bond of the inscription, `required`. Only a challenge turns that cost into a forfeit, half of it to the challenger. Only a lost challenge restores the note with its withdrawal inherited, so that it leaves in the same resolution once the delay has passed. A holder exiting against a hostile channel must therefore challenge, and so needs a bond: unlocked channel notes of the channel, deposited and bonded in one Mantle Transaction as the [`CHANNEL_CHALLENGE` example](bedrock-v1.1-mantle-specification.md#channel_challenge) shows. Without a challenge, the sequencer can repeat the move on the relocked output at each turn, for a bond each time.
- **Sequencer availability.** An inscription nobody answers for within the response window loses, even if it was valid. Running a sequencer means keeping the authorizations of every pending inscription and being able to answer at any time.
- **Pool liveness.** A holder can get their own notes out without the sequencers, but pool value moves only when a sequencer posts. Under round-robin sequencing, a group holding the configuration threshold can remove every honest sequencer and hold pool value hostage. A single accredited sequencer can also stall a pool for up to both windows by declaring a transition nobody can prove: the others cannot build on it, and cannot declare from another state. It forfeits its `required` each time, which does not grow with the pool's value, so the remedy is to remove its key with a `CHANNEL_CONFIG`.
- **Programs.** A pool's `image_id` is in the key of every note it holds, so a pool cannot be upgraded: only a migration path the program provides can move its value. Anything a program reads that is neither in its state nor in the keys of the notes it consumes, an oracle price for instance, is chosen by whoever answers.
- **Lost keys.** Nobody can move a channel note whose key is lost.
