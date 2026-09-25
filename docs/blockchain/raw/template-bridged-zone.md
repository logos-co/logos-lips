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

This document shows how a Zone uses its channel's bridged funds under [Channels](channels.md#bridging): what its users sign, what its sequencers post and what its followers compute. It shows how the rules of Channels and Mantle are used together, and links to them.

The bridged value is LGO held as channel notes. Every channel note carries the key of its holder, and no inscription moves it for good without that holder's authorization. A Zone keeps its own state and logic; the ledger only checks that the notes moved as their holders allowed.

# Overview

| Role | Holds | Does |
| --- | --- | --- |
| Holder | the key of channel notes | signs authorizations, leaves with a withdrawal |
| Sequencer | an accredited key and notes to [bond](channels.md#collateral) | nets authorizations into the note moves of the Zone's inscriptions, posts them, answers challenges |
| Watcher | a channel note to bond | checks posted inscriptions against published authorizations and challenges the ones that do not hold |
| Follower | a copy of the Zone | follows the channel's note moves and credits what they back |

A payment inside a Zone goes through these states:

```
signed       the holder signed an authorization and sent it to the sequencer
posted       an inscription applying it is on chain; its outputs are locked
challenged   someone bonded against the inscription; an answer within the response window closes the challenge
final        the inscription's deadline passed, unchallenged or answered
```

| Inscription | Final after |
| --- | --- |
| Not challenged | `CHALLENGE_WINDOW`, 2 days, once the inscriptions it depends on are final |
| Challenged and answered | the block after the answer, once the inscriptions it depends on are final |
| Challenged and not answered | never: it is undone and its inputs are re-created under the same keys |

A Zone may show a payment as soon as it is posted, but everything that touches bridged value stays provisional until the inscription is final.

# Holders

## Depositing

A holder moves an ordinary note into the channel with `CHANNEL_DEPOSIT`. The note is re-created under the holder's key as a channel note, and the Zone credits the holder's key. To make a Zone message conditional on the deposit, the sequencer consumes the deposited note in the same inscription (see [`CHANNEL_DEPOSIT`](bedrock-v1.1-mantle-specification.md#channel_deposit)).

## Paying

The holder signs, next to the Zone transaction they were already signing, an authorization of the channel notes it spends:

```python
auth = ZkSignature_sign(auth_msg(inputs=[alice_note_id],
                                 outputs=[Note(25, carol_pk), Note(24, alice_pk), Note(1, sequencer_pk)]),
                        [alice_sk])
```

The outputs name every note that must come out: the payment, the change and the Zone's fee, which is how a sequencer gets paid. The holder sends the Zone transaction and the authorization to the sequencer. The change comes back locked: the holder can spend it in the next inscription at once. The holder may also name it in a withdrawal at once, and it leaves once the inscription is final and the delay has passed.

A payment can also spend what another payment of the same inscription creates. The notes an authorization creates have [identifiers](channels.md#authorizations) derived from the authorization, so Carol can sign, before anything is posted, an authorization consuming the note of 25 Alice's authorization gives her. Only what no later authorization consumes is created on the ledger.

## Leaving

A holder leaves with a `CHANNEL_WITHDRAW` over the `mantle_txhash`, the only way out of a channel. It names unlocked notes and the locked outputs of pending inscriptions; a note the holder bonded waits for its release. No sequencer takes part. Each note leaves `WITHDRAW_DELAY` slots later, at the first moment it is unlocked, re-created as an ordinary note under the same key with its ageing restarted, and the Zone debits the holder's key when it sees it leave. The delay is the Zone's notice: during it the sequencer may still apply an authorization the holder gave over the notes, and after it nothing may consume them:

```
slot s               CHANNEL_WITHDRAW(channel, inputs)   signed by the holder; from now on nobody may bond the inputs, and the
                                                         sequencer may still consume them with an authorization of the holder
s + WITHDRAW_DELAY   due: no inscription may consume the inputs any more; each leaves at the first moment it is unlocked,
                     in the resolution of a block and before its transactions
```

## When the Sequencers Ignore You

Nobody answers for a withdrawal, and the sequencers cannot hold it past the first unlock after its due. An input locked as the output of a pending inscription leaves once that inscription is final; if that inscription is undone, the input is removed with it, and its value comes back with the notes the undo re-creates. What a hostile sequencer can do during the delay is consume the withdrawn notes without authorization, at the cost of a bond, and relock them as the outputs of its inscription. The holder, or a watcher, challenges: the lost challenge restores the notes under their withdrawal, and they leave in the same resolution (see [Security Considerations](channels.md#security-considerations) of Channels). Exiting against a hostile channel therefore takes a bond, deposited and bonded in one Mantle Transaction as under [Watching](#watching). A holder whose note was consumed without authorization and relocked as an output withdraws the notes it still holds and challenges the relock. Withdrawing the relocked output alone does not bring the value back: a created note drops out of its withdrawal when its inscription is lost (see [Withdrawals](channels.md#withdrawals) of Channels), and it is the restored input that inherits the holder's withdrawal.

## Watching

A holder, or a watcher on their behalf, checks each posted inscription of the channel before its deadline: every input it consumes must be covered by an authorization, and its outputs must be exactly the claims of those authorizations, in their order. A holder leaving checks the inscriptions posted during the delay of its withdrawal the same way, since one consuming its notes without authorization must be challenged for them to leave. When they are not, the watcher challenges, bonding the inscription's `required`, and receives half of it when nobody can answer. That holds even when the inscription depends on one that is about to lose: undone or not, an inscription forfeits only through its own challenge. The bond is made of unlocked channel notes of the channel, and it keeps taking part in Proof of Stake while it is locked. A watcher holding none deposits and challenges in one Mantle Transaction, the `CHANNEL_DEPOSIT` before the `CHANNEL_CHALLENGE`, so that the bond is the channel notes the deposit creates and no inscription can consume them first (see the [`CHANNEL_CHALLENGE` example](bedrock-v1.1-mantle-specification.md#channel_challenge)).

# Sequencers

## Bonding

A sequencer bonds, with every inscription that moves notes, notes of its own worth the inscription's `required` (see [\[Analysis\] Channel Collateral](analysis-channel-collateral.md) for how much that is). Only unlocked channel notes of the channel serve, so a sequencer deposits what it bonds. A deposit that lands alone is an unlocked channel note another sequencer's inscription may consume, so a sequencer bonds what it deposits in the same Mantle Transaction, the `CHANNEL_DEPOSIT` before the `CHANNEL_INSCRIBE`. The bond is locked until the inscription is final, so a sequencer needs enough notes for the inscriptions of a whole challenge window, and it keeps earning Proof of Stake rewards on them.

## Netting and Posting

On its turn, the sequencer applies the Zone transactions it received and builds the note moves of one inscription out of their authorizations:

1. The inputs are the notes of the channel the authorizations spend.
2. The outputs are the notes the authorizations create and no later authorization consumes, in the order of the authorizations. The Zone's fees, one claim per payment, are merged by an authorization of the sequencer's own consuming them.

The moves ride in the inscription carrying the Zone's message, so both land or neither does.

## Answering

A sequencer keeps, for each pending inscription, everything an answer needs, that is its authorizations. It publishes the authorizations so that watchers can check them and anyone can answer. When challenged, it answers within the response window, and the challenger's bond forfeits the inscription's `required` to it; an inscription nobody answers for is undone and the sequencer forfeits its `required`, even if the inscription was valid.

## Building on Pending Inscriptions

Consuming a locked note makes the new inscription depend on the one that created it. If that inscription loses, every inscription depending on it is undone with it. An undone inscription stays challengeable until its own deadline, and its sequencer keeps its bond as long as it can answer for it. What is lost is the work, and the users' payments have to be signed and posted again. A sequencer therefore builds only on pending inscriptions it could answer for itself.

# Zone State

A follower applies the channel's inscriptions and note moves in chain order, with one rule: **credit only what the same Mantle Transaction backs**. The unit is the transaction because Mantle executes a transaction atomically, which lets a deposit sit next to the receiving channel's inscription in a [cross-channel transfer](template-cross-channel-messaging.md#synchronous-messaging).

- **Accounts and keys.** Bridged balances belong to keys, since authorizations are per key. A Zone that wants richer accounts maps them to keys, and must credit a payment to the key the output names, not to an account the message claims.
- **Messages and moves.** An inscription's message describes Zone effects, and its note moves back the ones that touch bridged value. A message crediting value no output backs is not credited.
- **Moves without a message.** A withdrawal debits the keys of the channel notes it takes out, when they leave.
- **Lost inscriptions.** When an inscription is lost, the ledger undoes it and the inscriptions depending on it, while they stay on chain. The follower re-executes the Zone from the lost inscription, by a rule the Zone specifies. The rule must be deterministic, so that every follower lands on the same state. The default rule below is the simplest one.
- **Provisional effects.** Anything built on bridged value, a purchase, a loan, a swap, is provisional until its inscription is final. The Zone decides what it shows before then.

## Default Rule for Lost Inscriptions

When the resolution of a block loses an inscription `L`, the follower:

1. returns to the Zone state it held just before `L`;
2. goes again through the channel's Operations from `L` to the end of the previous block, applying no message. Of each inscription it keeps only the note moves, when the ledger did not undo them: they debit and credit keys as moves without a message do. Deposits and withdrawals apply as they did;
3. resumes with the transactions of that block, messages included. The resolution runs before them, so a sequencer posting in that block already builds on the re-executed state.

The bridged balances then match the ledger, since every note move that stands is still followed. What the rule gives up is every Zone effect that lived only in the messages posted since `L`, related to the lost inscription or not, which users submit again. It behaves as if the channel's tip had been reverted to before `L`, without the ledger reverting payments that were valid.

A Zone can keep more with a finer rule, dropping only the messages that depended on the undone moves, but it then has to define that dependence for its own state. Either way a follower keeps the states of the last `CHALLENGE_WINDOW + RESPONSE_WINDOW`, 3 days, to return to.

# Checklist

- Publish the authorizations of every posted inscription, so watchers can check and anyone can answer.
- Keep the authorizations of every pending inscription, and stay able to answer within the response window.
- Build only on pending inscriptions you could answer for.
- Treat a withdrawal on chain as the notice that its notes leave at its `due`: apply an authorization over them before `due`, or drop it.
- Adopt the default rule for lost inscriptions or specify a finer one, keep the states to return to, and show bridged effects as provisional until final.
- Hold enough notes to bond the inscriptions of a full challenge window.

# References

- [Channels](channels.md): Bridging, Authorizations, Moving Notes, Challenges and Answers, Collateral, Withdrawals
- [Mantle](bedrock-v1.1-mantle-specification.md): the channel Operations and the [Channel Resolution](bedrock-v1.1-mantle-specification.md#channel-resolution)
- [\[Analysis\] Channel Collateral](analysis-channel-collateral.md)
- [\[Template\] Cross-Channel Messaging](template-cross-channel-messaging.md)
- [Mantle Transaction Encoding](mantle-transaction-encoding.md)
