# TEMPLATE-BRIDGED-ZONE

| Field | Value |
| --- | --- |
| Name | [Template] Bridged Zone |
| Slug | 246 |
| Status | raw |
| Category | Informational |
| Editor | Thomas Lavaur <thomas@logos.co> |
| Contributors |  |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

# Revision History

| Version | Changes | Date |
| --- | --- | --- |
| 1.0.0 | Initial revision | 2026-09-18 |

# Introduction

This document shows how a Zone uses its channel's bridged funds under [Mantle](bedrock-v1.1-mantle-specification.md#bridging): what its users sign, what its sequencers post, what its followers compute, and how a pool, here a swap, is built on top. It adds no rule to Mantle: it shows how its rules are used together, and links to them.

The bridged value is LGO held as channel notes. Every channel note carries the key of its holder, and no transfer moves it for good without that holder's authorization. A Zone keeps its own state and logic; the ledger only checks that the notes moved as their holders allowed.

# Overview

| Role | Holds | Does |
| --- | --- | --- |
| Holder | the key of channel notes | signs authorizations, leaves with a `TRANSFER`, forces an ignored authorization |
| Sequencer | an accredited key and a [stake](bedrock-v1.1-mantle-specification.md#collateral) | nets authorizations into transfers, posts them with the Zone's inscriptions, answers challenges |
| Watcher | nothing but an ordinary note to bond | checks posted transfers against published authorizations and challenges the ones that do not hold |
| Pool program | a Risc0 image | governs value no single holder owns, and proves it followed its rules when challenged |
| Follower | a copy of the Zone | follows the channel's note moves and credits what they back |

A payment inside a Zone goes through these states:

```
signed       the holder signed an authorization and sent it to the sequencer
posted       a transfer applying it is on chain; its outputs are locked
final        the transfer's window is over, or a valid answer settled it early
```

| Transfer | Final after |
| --- | --- |
| Not challenged | `CHALLENGE_WINDOW`, about 18 hours, once the transfers it depends on are final |
| Challenged and answered | the answer, once the transfers it depends on are final |
| Challenged and not answered | never: it is undone and its inputs are re-created under the same keys |

A Zone may show a payment as soon as it is posted, but everything that touches bridged value stays provisional until the transfer is final.

# Holders

## Depositing

A holder moves an ordinary note into the channel with `CHANNEL_DEPOSIT`. The note is re-created under the holder's key as a channel note, and the Zone credits the holder's key. To make a Zone message conditional on the deposit, the sequencer consumes the deposited note in the transfer part of the same inscription (see [`CHANNEL_DEPOSIT`](bedrock-v1.1-mantle-specification.md#channel_deposit)).

## Paying

The holder signs, next to the Zone transaction they were already signing, an authorization of the channel notes it spends:

```python
auth = ZkSignature_sign(auth_msg(ZONE, inputs=[alice_note_id],
                                 outputs=[Note(25, carol_pk), Note(24, alice_pk), Note(1, sequencer_pk)]),
                        [alice_sk])
```

The outputs name every note that must come out: the payment, the change and the Zone's fee, which is how a sequencer gets paid. The holder sends the Zone transaction and the authorization to the sequencer. The change comes back locked: the holder can spend it in the next transfer at once, but cannot take it out of the channel until the transfer is final.

## Leaving

Once a note is not locked, its holder leaves with an ordinary `TRANSFER` over the `mantle_txhash`, like any note. No sequencer takes part. The note is re-created as an ordinary note, and its ageing restarts. The Zone debits the holder's key when it sees the note leave.

## When the Sequencers Ignore You

To pay inside the channel without the sequencers, the holder, or the recipient holding the authorization, forces it:

```
slot s          CHANNEL_REGISTER_AUTH(auth)          the authorization becomes public
s + FORCE_DELAY CHANNEL_FORCE_TRANSFER(auth)         until s + 2 * FORCE_DELAY
```

If a sequencer applied the authorization in the meantime, its inputs are gone and forcing fails, which is the intended outcome. A forced transfer is final at once, and the Zone applies it without a message: it debits the keys of the notes consumed and credits the keys of the channel notes created.

## Watching

A holder, or a watcher on their behalf, checks each posted transfer of the channel within `CHALLENGE_WINDOW`: every input it consumes must be covered by an authorization, and its outputs must be exactly the claims of those authorizations, summed per key and sorted by key. When they are not, the watcher challenges, bonding the transfer's `required`, and receives half of it when nobody can answer. That holds even when the transfer depends on one that is about to lose: undone or not, a transfer forfeits only through its own challenge. The bond stays an ordinary note that keeps taking part in Proof of Stake while it is held.

# Sequencers

## Staking

A sequencer stakes ordinary notes of its own with `CHANNEL_STAKE`. The stake serves every channel where its key is accredited, and caps the collateral of its pending transfers (see [\[Analysis\] Channel Collateral](analysis-channel-collateral.md) for how much a transfer requires).

## Netting and Posting

On its turn, the sequencer applies the Zone transactions it received and builds one transfer out of their authorizations:

1. The inputs are the notes the authorizations spend.
2. The outputs are the notes the authorizations create, summed per key and sorted by key. Notes consumed by a pool step inside the same transfer are left out.
3. Each pool the transfer moves is declared, from the state the ledger holds to the state its program reaches.

The transfer rides in the inscription carrying the Zone's message, so both land or neither does.

## Answering

A sequencer keeps, for each pending transfer, everything an answer needs: the authorizations, the intent preimages, the pool inputs, and the ability to produce each pool proof. It publishes the authorizations so that watchers can check them and anyone can answer. When challenged, it answers within the response window; a transfer nobody answers is undone and the sequencer forfeits its collateral, even if the transfer was valid.

## Building on Pending Transfers

Consuming a locked note makes the new transfer depend on the one that created it, and declaring a pool depends on its last pending transition. If that transfer loses, every transfer depending on it is undone with it. An undone transfer does not forfeit for that: it stays challengeable until its own window ends, and its sequencer keeps its collateral as long as it can answer for it. What is lost is the work, and the users' payments have to be signed and posted again. A sequencer therefore builds only on pending transfers it could answer for itself.

# Zone State

A follower applies the channel's inscriptions and note moves in chain order, with one rule: **credit only what the same Mantle Transaction backs** (see [Following a Channel](bedrock-v1.1-mantle-specification.md#following-a-channel)).

- **Accounts and keys.** Bridged balances belong to keys, since authorizations are per key. A Zone that wants richer accounts maps them to keys, and must credit a payment to the key the output names, not to an account the message claims.
- **Messages and moves.** An inscription's message describes Zone effects, and its transfer part backs the ones that touch bridged value. A message crediting value no output backs is not credited.
- **Moves without a message.** A `TRANSFER` out of the channel and a forced transfer debit the keys of the channel notes they consume and credit the keys of the channel notes they create.
- **Lost transfers.** When a transfer is lost, the ledger undoes it and the transfers depending on it, while their inscriptions stay on chain. The follower re-executes the Zone from the lost inscription, by a rule the Zone specifies. The rule must be deterministic, so that every follower lands on the same state. The default rule below is the simplest one.
- **Provisional effects.** Anything built on bridged value, a purchase, a loan, a swap, is provisional until its transfer is final. The Zone decides what it shows before then.

## Default Rule for Lost Transfers

When the resolution of a block loses the transfer of an inscription `L`, the follower:

1. returns to the Zone state it held just before `L`;
2. goes again through the channel's Operations from `L` to the end of the previous block, applying no message. Of each inscription it keeps only the transfer, when the ledger did not undo it: its note moves debit and credit keys as moves without a message do, and its pool transitions are applied by running the pool programs. Deposits, `TRANSFER`s out of the channel and forced transfers apply as they did;
3. resumes with the transactions of that block, messages included. The resolution runs before them, so a sequencer posting in that block already builds on the re-executed state.

The bridged balances then match the ledger, since every note move that stands is still followed, and the pools match the states the ledger holds: a pool the lost transfer touched has all its later transitions undone with it, and a pool it did not touch keeps its whole chain. What the rule gives up is every Zone effect that lived only in the messages posted since `L`, related to the lost transfer or not, which users submit again. It behaves as if the channel's tip had been reverted to before `L`, without the ledger reverting payments that were valid.

A Zone can keep more with a finer rule, dropping only the messages that depended on the undone moves, but it then has to define that dependence for its own state. Either way a follower keeps the states of the last `CHALLENGE_WINDOW + RESPONSE_WINDOW`, about 36 hours, to return to.

A follower does not need the proofs. It runs the pool programs natively on the inputs the sequencer publishes, and the proof is only produced for the ledger when a transfer is challenged.

# Example: a Swap Pool

A Zone runs a market between LGO and its own token, TKN. The LGO side is channel notes, which the ledger protects. The TKN side is Zone state, which the ledger does not see: a note carries no asset type, so only LGO is protected ([Bridging Security Considerations](bedrock-v1.1-mantle-specification.md#bridging-security-considerations)).

## The Program

The pool is a Risc0 program with image `AMM`. Its state is a hash committing to both reserves and to the TKN balances it holds for its users, since anything a program reads outside its state and the notes it consumes is chosen by whoever answers. One run is one transition:

```
inputs:  the state and its preimage
         the notes consumed, as (value, intent_hash), and the intent preimages
         the TKN orders of its users, signed with their Zone keys
outputs: the new state
         the notes created, as (value, public_key)
```

It commits the journal `(instance_id, state, new_state, consumed, created)`. For every deposit it consumes, it opens the intent and applies it:

```python
intent = (kind="swap", recipient=alice_tkn_account, min_out=180, refund_pk=alice_pk, salt=random())
```

A swap whose output falls below `min_out` is refunded to `refund_pk`. The salt keeps two identical intents from sharing a key, which would merge their deposits into one note.

## Creating the Pool

```python
params_hash = zkhash(fee_bps=30, salt=zone_salt)
create = PoolCreate(channel=ZONE, image_id=AMM, params_hash=params_hash)
instance = derive_instance_id(ZONE, AMM, params_hash)
reserve_pk = pool_key(AMM, instance, 0)
```

Anyone may post it; the ledger derives the instance and the genesis state, so the pool cannot start from a state in which its creator owns anything. Liquidity arrives the same way as swaps, through deposits whose intent asks to add it.

## Alice Swaps 60 LGO for TKN

Alice holds a channel note of 100 LGO. She computes the key of her deposit and authorizes her own note only:

```python
intent_hash = zkhash(intent)
deposit_pk = pool_key(AMM, instance, intent_hash)
alice_auth = ZkSignature_sign(auth_msg(ZONE, [alice_note_id],
                                       [Note(60, deposit_pk), Note(40, alice_pk)]), [alice_sk])
```

She sends the sequencer the Zone transaction, `alice_auth` and the intent preimage. She never signs the TKN she will get, which she cannot know in advance: the program computes it and checks it against `min_out`.

The sequencer nets her swap with others in one transfer. With the reserve note `reserve_id` of 10,000 LGO and Alice's swap alone:

```python
swap = Inscribe(
    channel=ZONE, inscription=b"<zone transition>", parent=zone_tip, signer=sequencer_pk,
    inputs=[alice_note_id, reserve_id],
    outputs=sorted([Note(40, alice_pk), Note(10_060, reserve_pk)], key=lambda n: n.public_key),
    declared=[PoolTransition(instance, state_before=s0, new_state=s1)])
```

The deposit note never reaches the ledger: Alice's step creates it, the pool step consumes it in the same transfer, so it is an intermediate note. The new reserve is a claim under the reserve key. A pool advances once per transfer, so with several swaps the one pool step consumes every deposit and re-creates a single reserve. Alice's TKN is credited in the pool state `s1`, which followers compute by running the program.

## If Someone Challenges

The answer accounts for the whole transfer, one step per authorization and one per pool transition:

```python
answer = ChannelAnswer(transfer=derive_op_id(swap), bond=answerer_bond_id, steps=[
    UserStep(inputs=[alice_note_id],
             outputs=[Note(60, deposit_pk), Note(40, alice_pk)],
             proof=alice_auth),
    PoolStep(instance_id=instance,
             consumed=[PoolInput(ref=reserve_id, value=10_000, intent_hash=0),
                       PoolInput(ref=(0, 0), value=60, intent_hash=intent_hash)],
             created=[Note(10_060, reserve_pk)],
             seal=prove(AMM, journal))])
```

The ledger recomputes each consumed note's key from its `intent_hash` and checks its value, then verifies the receipt against the journal built from the declared transition. What is left unconsumed is Alice's change and the new reserve, which are exactly the posted outputs.

Had the TKN output fallen below `min_out`, the program would have refunded instead: the pool step creates `Note(60, alice_pk)` and the reserve stays at 10,000. Alice's refund and her change are both claims to `alice_pk` and merge, so the transfer's outputs are `Note(100, alice_pk)` and `Note(10_000, reserve_pk)`.

## Bob Sells TKN for LGO

Bob holds TKN, not a note, so his order carries no deposit. It is a Zone transaction he signs with his Zone key, over a nonce the pool state tracks, and the program checks that signature, the nonce and his TKN balance in the pool state before paying him. Without the nonce, a sequencer could apply the same signed order twice. The pool step consumes the reserve and creates two claims, `Note(payout, bob_pk)` and the smaller reserve. Only the program's proof authorizes the payout, and the program pays only an order Bob signed, so a sequencer cannot invent one; it can only leave Bob's order out, which Bob sees.

## A Private Pool

A shielded pool fits the same pattern. Its state is the commitment and nullifier roots, all its LGO sits under its reserve key, and the ledger sees a total, never an account. Shielding is a deposit whose intent names the commitment to create; unshielding is a pool step paying a note to a key. A private transfer moves no note but advances the roots, so the transfer still declares the transition, and its proof on challenge aggregates the private receipts of the period. That proof is the heaviest a Zone produces, and it is what `STATE_PROVING` is sized for.

# Checklist

- Salt every intent, and include a refund key.
- Keep inside the pool state everything the program reads, other than the notes it consumes, including a nonce per signed order.
- Publish the authorizations of every posted transfer, so watchers can check and anyone can answer.
- Keep, for every pending transfer, what an answer needs, and a prover able to produce its pool proofs within the response window.
- Build only on pending transfers you could answer for.
- Adopt the default rule for lost transfers or specify a finer one, keep the states to return to, and show bridged effects as provisional until final.
- Stake enough for the pending transfers of a full challenge window, and plan for the pool proofs a challenge can force.

# References

- [Mantle](bedrock-v1.1-mantle-specification.md): Bridging, Authorizations, Transfers, Challenges and Answers, Collateral, Pools, Forced Transfers, Following a Channel
- [\[Analysis\] Channel Collateral](analysis-channel-collateral.md)
- [\[Template\] Cross-Channel Messaging](template-cross-channel-messaging.md)
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
