# ETH-DCGKA

| Field | Value |
| --- | --- |
| Name | Decentralized Key and Session Setup for Secure Messaging over Ethereum |
| Slug | 103 |
| Status | raw |
| Category | informational |
| Editor | Ramses Fernandez-Valencia <ramses@status.im> |

<!-- timeline:start -->

## Timeline

- **2026-01-19** — [`f24e567`](https://github.com/logos-co/logos-lips/blob/f24e567d0b1e10c178bfa0c133495fe83b969b76/docs/anoncomms/raw/decentralized-messaging-ethereum.md) — Chore/updates mdbook (#262)
- **2026-01-16** — [`f01d5b9`](https://github.com/logos-co/logos-lips/blob/f01d5b9d9f2ef977b8c089d616991b24f2ee4efe/docs/anoncomms/raw/decentralized-messaging-ethereum.md) — chore: fix links (#260)
- **2026-01-16** — [`89f2ea8`](https://github.com/logos-co/logos-lips/blob/89f2ea89fc1d69ab238b63c7e6fb9e4203fd8529/docs/anoncomms/raw/decentralized-messaging-ethereum.md) — Chore/mdbook updates (#258)
- **2025-12-22** — [`0f1855e`](https://github.com/logos-co/logos-lips/blob/0f1855edcf68ef982c4ce478b67d660809aa9830/docs/vac/raw/decentralized-messaging-ethereum.md) — Chore/fix headers (#239)
- **2025-12-22** — [`b1a5783`](https://github.com/logos-co/logos-lips/blob/b1a578393edf8487ccc97a5f25b25af9bf41efb3/docs/vac/raw/decentralized-messaging-ethereum.md) — Chore/mdbook updates (#237)
- **2025-12-18** — [`d03e699`](https://github.com/logos-co/logos-lips/blob/d03e699084774ebecef9c6d4662498907c5e2080/docs/vac/raw/decentralized-messaging-ethereum.md) — ci: add mdBook configuration (#233)
- **2025-04-04** — [`517b639`](https://github.com/logos-co/logos-lips/blob/517b63984c875670e437d50359f2f67331104974/vac/raw/decentralized-messaging-ethereum.md) — Update the RFCs: Vac Raw RFC (#143)
- **2024-10-03** — [`c655980`](https://github.com/logos-co/logos-lips/blob/c655980494a5943634c372009bbea71c13196a8f/vac/raw/decentralized-messaging-ethereum.md) — Eth secpm splitted (#91)
- **2024-09-13** — [`3ab314d`](https://github.com/logos-co/logos-lips/blob/3ab314d87d4525ff1296bf3d9ec634d570777b91/vac/raw/decentralized-messaging-ethereum.md) — Fix Files for Linting (#94)
- **2024-05-27** — [`7e3a625`](https://github.com/logos-co/logos-lips/blob/7e3a625812bd954696b7facc29a205053d1acc3c/vac/raw/decentralized-messaging-ethereum.md) — ETH-SECPM-DEC (#28)

<!-- timeline:end -->

## Abstract

This document introduces a decentralized group messaging protocol
using Ethereum adresses as identifiers.
It is based in the proposal
[DCGKA](https://eprint.iacr.org/2020/1281) by Weidner et al.
It includes also approximations to overcome limitations related to using PKI and
the multi-device setting.

## Motivation

The need for secure communications has become paramount.
Traditional centralized messaging protocols are susceptible to various security
threats, including unauthorized access, data breaches, and single points of
failure.
Therefore a decentralized approach to secure communication becomes increasingly
relevant, offering a robust solution to address these challenges.

Secure messaging protocols used should have the following key features:

1. **Asynchronous Messaging:** Users can send messages even if the recipients
are not online at the moment.

2. **Resilience to Compromise:** If a user's security is compromised,
the protocol ensures that previous messages remain secure through forward
secrecy (FS). This means that messages sent before the compromise cannot be
decrypted by adversaries. Additionally, the protocol maintains post-compromise
security (PCS) by regularly updating keys, making it difficult for adversaries
to decrypt future communication.

3. **Dynamic Group Management:** Users can easily add or remove group members
at any time, reflecting the flexible nature of communication within the app.

In this field, there exists a *trilemma*, similar to what one observes in
blockchain, involving three key aspects:

1. security,
2. scalability, and
3. decentralization.

For instance, protocols like the [MLS](https://messaginglayersecurity.rocks)
perform well in terms of scalability and security.
However, they falls short in decentralization.

Newer studies such as [CoCoa](https://eprint.iacr.org/2022/251)
improve features related to security and scalability,
but they still rely on servers, which may not be fully trusted though they are necessary.

On the other hand,
older studies like [Causal TreeKEM](https://mattweidner.com/assets/pdf/acs-dissertation.pdf)
exhibit decent scalability (logarithmic)
but lack forward secrecy and have weak post-compromise security (PCS).

The creators of [DCGKA](https://eprint.iacr.org/2020/1281) introduce a decentralized,
asynchronous secure group messaging protocol that supports dynamic groups.
This protocol operates effectively on various underlying networks
without strict requirements on message ordering or latency.
It can be implemented in peer-to-peer or anonymity networks,
accommodating network partitions, high latency links, and
disconnected operation seamlessly.
Notably, the protocol doesn't rely on servers or
a consensus protocol for its functionality.

This proposal provides end-to-end encryption with forward secrecy and
post-compromise security,
even when multiple users concurrently modify the group state.

## Theory

### Protocol overview

This protocol makes use of ratchets to provide FS
by encrypting each message with a different key.

In the figure one can see the ratchet for encrypting a sequence of messages.
The sender requires an initial update secret `I_1`, which is introduced in a PRG.
The PRG will produce two outputs, namely a symmetric key for AEAD encryption, and
a seed for the next ratchet state.
The associated data needed in the AEAD encryption includes the message index `i`.
The ciphertext `c_i` associated to message `m_i`
is then broadcasted to all group members.
The next step requires deleting `I_1`, `k_i` and any old ratchet state.

After a period of time the sender may replace the ratchet state with new update secrets
`I_2`, `I_3`, and so on.

To start a post-compromise security update,
a user creates a new random value known as a seed secret and
shares it with every other group member through a secure two-party channel.
Upon receiving the seed secret,
each group member uses it to calculate an update secret for both the sender's ratchet
and their own.
Additionally, the recipient sends an unencrypted acknowledgment to the group
confirming the update.
Every member who receives the acknowledgment updates
not only the ratchet for the original sender but
also the ratchet for the sender of the acknowledgment.
Consequently, after sharing the seed secret through `n - 1` two-party messages and
confirming it with `n - 1` broadcast acknowledgments,
every group member has derived an update secret and updated their ratchet accordingly.

When removing a group member,
the user who initiates the removal conducts a post-compromise security update
by sending the update secret to all group members except the one being removed.
To add a new group member,
each existing group member shares the necessary state with the new user,
enabling them to derive their future update secrets.

Since group members may receive messages in various orders,
it's important to ensure that each sender's ratchet is updated consistently
with the same sequence of update secrets at each group member.

The network protocol used in this scheme ensures that messages from the same sender
are processed in the order they were sent.

### Components of the protocol

This protocol relies in 3 components:
authenticated causal broadcast (ACB),
decentralized group membership (DGM) and
2-party secure messaging (2SM).

#### Authenticated causal broadcast

A causal order is a partial order relation `<` on messages.
Two messages `m_1` and `m_2` are causally ordered, or
`m_1` causally precedes `m_2`
(denoted by `m_1 < m_2`), if one of the following contiditions hold:

1. `m_1` and `m_2` were sent by the same group member, and
`m_1` was sent before `m_2`.
2. `m_2` was sent by a group member U, and `m_1` was received and
processed by `U` before sending `m_2`.
3. There exists `m_3` such that `m_1 < m_3` and `m_3 < m_2`.

Causal broadcast requires that before processing `m`, a group member must
process all preceding messages `{m' | m' < m}`.

The causal broadcast module used in this protocol authenticates the sender of
each message, as well as its causal ordering metadata, using a digital
signature under the sender’s identity key.
This prevents a passive adversary from impersonating users or affecting
causally ordered delivery.

#### Decentralized group membership

This protocol assumes the existence of a decentralized group membership
function (denoted as DGM) that takes a set of membership change messages and
their causal order relantionships, and returns the current set of group
members’ IDs. It needs to be deterministic and depend only on causal order, and
not exact order.

#### 2-party secure messaging (2SM)

This protocol makes use of bidirectional 2-party secure messaging schemes,
which consist of 3 algorithms: `2SM-Init`, `2SM-Send` and `2SM-Receive`.

##### Function 2SM-Init

This function takes two IDs as inputs:
`ID1` representing the local user and `ID2` representing the other party.
It returns an initial protocol state `sigma`.
The 2SM protocol relies on a Public Key Infrastructure (PKI) or
a key server to map these IDs to their corresponding public keys.
In practice, the PKI should incorporate ephemeral prekeys.
This allows users to send messages to a new group member,
even if that member is currently offline.

##### Function 2SM-Send

This function takes a state `sigma` and a plaintext `m` as inputs, and returns
a new state `sigma’` and a ciphertext `c`.

##### Function 2SM-Receive

This function takes a state `sigma` and a ciphertext `c`, and
returns a new state `sigma’` and a plaintext `m`.

This function takes a state `sigma` and a ciphertext `c`, and returns a new
state `sigma’` and a plaintext `m`.

#### Function 2SM Syntax

The variable `sigma` denotes the state consisting in the variables below:

```text
sigma.mySks[0] = sk
sigma.nextIndex = 1 
sigma.receivedSk = empty_string
sigma.otherPk = pk`<br> 
sigma.otherPksender = “other”
sigma.otherPkIndex = 0

```

#### 2SM-Init

On input a key pair `(sk, pk)`, this functions otuputs a state `sigma`.

#### 2SM-Send

This function encrypts the message `m` using `sigma.otherPk`, which represents
the other party’s current public key.
This key is determined based on the last public key generated for the other
party or the last public key received from the other party,
whichever is more recent. `sigma.otherPkSender` is set to `me` in the former
case and `other` in the latter case.

Metadata including `otherPkSender` and `otherPkIndex` are included in the
message to indicate which of the recipient’s public keys is being utilized.

Additionally, this function generates a new key pair for the local user,
storing the secret key in `sigma.mySks` and sending the public key.
Similarly, it generates a new key pair for the other party,
sending the secret key (encrypted) and storing the public key in
`sigma.otherPk`.

```text
sigma.mySks[sigma.nextIndex], myNewPk) = PKE-Gen()
(otherNewSk, otherNewPk) = PKE-Gen()
plaintext = (m, otherNewSk, sigma`.nextIndex, myNewPk)
msg = (PKE-Enc(sigma.otherPk, plaintext), sigma.otherPkSender, sigma.otherPkIndex)
sigma.nextIndex++
(sigma.otherPk, sigma.otherPkSender, sigma.otherPkIndex) = (otherNewPk, "me", empty_string)
return (sigma`, msg)

```

#### 2SM-Receive

This function utilizes the metadata of the message `c` to determine which
secret key to utilize for decryption, assigning it to `sk`.
If the secret key corresponds to one generated by ourselves,
that secret key along with all keys with lower index are deleted.
This deletion is indicated by `sigma.mySks[≤ keyIndex] = empty_string`.
Subsequently, the new public and secret keys contained in the message are
stored.

```text
(ciphertext, keySender, keyIndex) = c
if keySender = "other" then 
sk = sigma.mySks[keyIndex] 
sigma.mySks[≤ keyIndex] = empty_string
else sk = sigma.receivedSk
(m, sigma.receivedSk, sigma.otherPkIndex, sigma.otherPk) = PKE-Dec(sk, ciphertext)
sigma.otherPkSender = "other"
return (sigma, m)

```

### PKE Syntax

The required PKE that MUST be used is ElGamal with a 2048-bit modulus `p`.

#### Parameters

The following parameters must be used:

```text
p = 308920927247127345254346920820166145569
g = 2

```

#### PKE-KGen

Each user `u` MUST do the following:

```text
PKE-KGen():
a = randint(2, p-2)
pk = (p, g, g^a)
sk = a
return (pk, sk)

```

#### PKE-Enc

A user `v` encrypting a message `m` for `u` MUST follow these steps:

```text
PKE-Enc(pk):
k = randint(2, p-2)
eta = g^k % p
delta = m * (g^a)^k % p
return ((eta, delta))

```

#### PKE-Dec

The user `u` recovers a message `m` from a ciphertext `c`
by performing the following operations:

```text
PKE-Dec(sk):
mu = eta^(p-1-sk) % p
return ((mu * delta) % p)

```

### DCGKA Syntax

#### Auxiliary functions

There exist 6 functions that are auxiliary for the rest of components of the
protocol, namely:

#### init

This function takes an `ID` as input and returns its associated initial state,
denoted by `gamma`:

```text
gamma.myId = ID
gamma.mySeq = 0
gamma.history = empty
gamma.nextSeed = empty_string
gamma.2sm[·] = empty_string
gamma.memberSecret[·, ·, ·] = empty_string
gamma.ratchet[·] = empty_string
return (gamma)

```

#### encrypt-to

Upon reception of the recipient’s `ID` and a plaintext, it encrypts a direct
message for another group member.
Should it be the first message for a particular `ID`,
then the `2SM` protocol state is initialized and stored in
`gamma.2sm[recipient.ID]`.
One then uses `2SM_Send` to encrypt the message and store the updated protocol
in `gamma`.

```text
if gamma.2sm[recipient_ID] = empty_string then
 gamma.2sm[recipient_ID] = 2SM_Init(gamma.myID, recipient_ID)
(gamma.2sm[recipient_ID], ciphertext) = 2SM_Send(gamma.2sm[recipient_ID], plaintext)
return (gamma, ciphertext)

```

#### decrypt-from

After receiving the sender’s `ID` and a ciphertext, it behaves as the reverse
function of `encrypt-to` and has a similar initialization:

```text
if gamma.2sm[sender_ID] = empty_string then
gamma.2sm[sender_ID] = 2SM_Init(gamma.myID, sender_ID)
(gamma.2sm[sender_ID], plaintext) = 2SM_Receive(gamma.2sm[sender_ID], ciphertext)
return (gamma, plaintext)

```

#### update-ratchet

This function generates the next update secret `I_update` for the group member
`ID`.
The ratchet state is stored in `gamma.ratchet[ID]`.
It is required to use a HMAC-based key derivation function HKDF to combine the
ratchet state with an input, returning an update secret and a new ratchet
state.

```text
(updateSecret, gamma.ratchet[ID]) = HKDF(gamma.ratchet[ID], input)
return (gamma, updateSecret)

```

#### member-view

This function calculates the set of group members
based on the most recent control message sent by the specified user `ID`.
It filters the group membership operations
to include only those observed by the specified `ID`, and
then invokes the DGM function to generate the group membership.

```text
ops = {m in gamma.history st. m was sent or acknowledged by ID}
return DGM(ops)

```

#### generate-seed

This functions generates a random bit string and
sends it encrypted to each member of the group using the `2SM` mechanism.
It returns the updated protocol state and
the set of direct messages (denoted as `dmsgs`) to send.

```text
gamma.nextSeed = random.randbytes()
dmsgs = empty
for each ID in recipients:
(gamma, msg) = encrypt-to(gamma, ID, gamma.nextSeed)
dmsgs = dmsgs + (ID, msg)
return (gamma, dmsgs)

```

### Creation of a group

A group is generated in a 3 steps procedure:

1. A user calls the `create` function and broadcasts a control message of type
*create*.
2. Each receiver of the message processes the message and broadcasts an *ack*
control message.
3. Each member processes the *ack* message received.

#### create

This function generates a *create* control message and calls `generate-seed` to
define the set of direct messages that need to be sent.
Then it calls `process-create` to process the control message for this user.
The function `process-create` returns a tuple including an updated state gamma
and an update secret `I`.

```text
control = (“create”, gamma.mySeq, IDs)
(gamma, dmsgs) = generate-seed(gamma, IDs)
(gamma, _, _, I, _) = process-create(gamma, gamma.myId, gamma.mySeq, IDs, empty_string)
return (gamma, control, dmsgs, I)

```

#### process-seed

This function initially employs `member-view` to identify the users who were
part of the group when the control message was dispatched.
Then, it attempts to acquire the seed secret through the following steps:

1. If the control message was dispatched by the local user, it uses the most
recent invocation of `generate-seed` stored the seed secret in
`gamma.nextSeed`.
2. If the `control` message was dispatched by another user, and the local user
is among its recipients, the function utilizes `decrypt-from` to decrypt the
direct message that includes the seed secret.
3. Otherwise, it returns an `ack` message without deriving an update secret.

Afterwards, `process-seed` generates separate member secrets for each group
member from the seed secret by combining the seed secret and
each user ID using HKDF.
The secret for the sender of the message is stored in `senderSecret`, while
those for the other group members are stored in `gamma.memberSecret`.
The sender's member secret is immediately utilized to update their KDF ratchet
and compute their update secret `I_sender` using `update-ratchet`.
If the local user is the sender of the control message, the process is
completed, and the update secret is returned.
However, if the seed secret is received from another user, an `ack` control
message is constructed for broadcast, including the sender ID and sequence
number of the message being acknowledged.

The final step computes an update secret `I_me` for the local user invoking the
`process-ack` function.

```text
recipients = member-view(gamma, sender) - {sender}
if sender =  gamma.myId then seed = gamma.nextSeed; gamma.nextSeed =
empty_string
else if  gamma.myId in recipients then (gamma, seed) = decrypt-from(gamma,
sender, dmsg)
else
return (gamma, (ack, ++gamma.mySeq, (sender, seq)), empty_string ,
empty_string , empty_string)

for ID in recipients do gamma.memberSecret[sender, seq, ID] = HKDF(seed, ID)
senderSecret = HKDF(seed, sender)
(gamma, I_sender) = update-ratchet(gamma, sender, senderSecret)
if sender = gamma.myId then return (gamma, empty_string , empty_string ,
I_sender, empty_string)
control = (ack, ++gamma.mySeq, (sender, seq))
members = member-view(gamma, gamma.myId)
forward = empty
for ID in {members - (recipients + {sender})}
    s = gamma.memberSecret[sender, seq, gamma.myId]
    (gamma, msg) = encrypt-to(gamma, ID, s)
    forward = forward + {(ID, msg)}
    (gamma, _, _, I_me, _) = process-ack(gamma, gamma.myId, gamma.mySeq, 
    (sender, seq), empty_string)
    return (gamma, control, forward, I_sender, I_me)

```

#### process-create

This function is called by the sender and each of the receivers of the `create`
control message.
First, it records the information from the create message in the
`gamma.history+ {op}`, which is used to track group membership changes. Then,
it proceeds to call `process-seed`.

```text
op = (”create”, sender, seq, IDs)
gamma.history = gamma.history + {op}
return (process-seed(gamma, sender, seq, dmsg))

```

#### process-ack

This function is called by those group members once they receive an ack
message.
In `process-ack`, `ackID` and `ackSeq` are the sender and sequence number of
the acknowledged message.
Firstly, if the acknowledged message is a group membership operation, it
records the acknowledgement in `gamma.history`.

Following this, the function retrieves the relevant member secret from
`gamma.memberSecret`, which was previously obtained from the seed secret
contained in the acknowledged message.

Finally, it updates the ratchet for the sender of the `ack` and returns the
resulting update secret.

```text
if (ackID, ackSeq) was a create / add / remove then
op = ("ack", sender, seq, ackID, ackSeq)
gamma.history = gamma.history + {op}`
s = gamma.memberSecret[ackID, ackSeq, sender]
gamma.memberSecret[ackID, ackSeq, sender] = empty_string
if (s = empty_string) & (dmsg = empty_string) then return (gamma, empty_string,
empty_string, empty_string, empty_string)
if (s = empty_string) then (gamma, s) = decrypt-from(gamma, sender, dmsg)
(gamma, I) = update-ratchet(gamma, sender, s)
return (gamma, empty_string, empty_string, I, empty_string)

```

The HKDF function MUST follow RFC 5869 using the hash function SHA256.

### Post-compromise security updates and group member removal

The functions `update` and `remove` share similarities with `create`:
they both call the function `generate-seed` to encrypt a new seed secret for
each group member.
The distinction lies in the determination of the group members using `member
view`.
In the case of `remove`, the user being removed is excluded from the recipients
of the seed secret.
Additionally, the control message they construct is designated with type
`update` or `remove` respectively.

Likewise, `process-update` and `process-remove` are akin to `process-create`.
The function `process-update` skips the update of `gamma.history`,
whereas `process-remove` includes a removal operation in the history.

#### update

```text
control = ("update", ++gamma.mySeq, empty_string)
recipients = member-view(gamma, gamma.myId) - {gamma.myId}
(gamma, dmsgs) = generate-seed(gamma, recipients)
(gamma, _, _, I , _) = process-update(gamma, gamma.myId, gamma.mySeq,
empty_string, empty_string)
return (gamma, control, dmsgs, I)

```

#### remove

```text
control = ("remove", ++gamma.mySeq, empty)
recipients = member-view(gamma, gamma.myId) - {ID, gamma.myId}
(gamma, dmsgs) = generate-seed(gamma, recipients)
(gamma, _, _, I , _) = process-update(gamma, gamma.myId, gamma.mySeq, ID,
empty_string)
return (gamma, control, dmsgs, I)

```

#### process-update

`return process-seed(gamma, sender, seq, dmsg)`

#### process-remove

```text
op = ("remove", sender, seq, removed)
gamma.history = gamma.history + {op}
return process-seed(gamma, sender, seq, dmsg)

```

### Group member addition

#### add

When adding a new group member, an existing member initiates the process by
invoking the `add` function and providing the ID of the user to be added.
This function prepares a control message marked as `add` for broadcast to the
group. Simultaneously, it creates a welcome message intended for the new member
as a direct message.
This `welcome` message includes the current state of the sender's KDF ratchet,
encrypted using `2SM`, along with the history of group membership operations
conducted so far.

```text
control = ("add", ++gamma.mySeq, ID)
(gamma, c) = encrypt-to(gamma, ID, gamma.ratchet[gamma.myId])
op = ("add", gamma.myId, gamma.mySeq, ID)
welcome = (gamma.history + {op}, c)
(gamma, _, _, I, _) = process-add(gamma, gamma.myId, gamma.mySeq, ID, empty_string)
return (gamma, control, (ID, welcome), I)

```

#### process-add

This function is invoked by both the sender and each recipient of an `add`
message, which includes the new group member. If the local user is the newly
added member, the function proceeds to call `process-welcome` and then exits.
Otherwise, it extends `gamma.history` with the `add` operation.

Line 5 determines whether the local user was already a group member at the time
the `add` message was sent; this condition is typically true but may be false
if multiple users were added concurrently.

On lines 6 to 8, the ratchet for the sender of the *add* message is updated
twice. In both calls to `update-ratchet`, a constant string is used as the
ratchet input instead of a random seed secret.

The value returned by the first ratchet update is stored in
`gamma.memberSecret` as the added user’s initial member secret. The result of
the second ratchet update becomes `I_sender`, the update secret for the sender
of the `add` message. On line 10, if the local user is the sender, the update
secret is returned.

If the local user is not the sender, an acknowledgment for the `add` message is
required.
Therefore, on line 11, a control message of type `add-ack` is constructed for
broadcast.
Subsequently, in line 12 the current ratchet state is encrypted using `2SM` to
generate a direct message intended for the added user, allowing them to decrypt
subsequent messages sent by the sender.
Finally, in lines 13 to 15, `process-add-ack` is called to calculate the local
user’s update secret (`I_me`), which is then returned along with `I_sender`.

```text
if added = gamma.myId then return process-welcome(gamma, sender, seq, dmsg)
op = ("add", sender, seq, added)
gamma.history = gamma.history + {op}
if gamma.myId in member-view(gamma, sender) then
    (gamma, s) = update-ratchet(gamma, sender, "welcome")
    gamma.memberSecret[sender, seq, added] = s
    (gamma, I_sender) = update-ratchet(gamma, sender, "add")
    else I_sender = empty_string
    if sender = gamma.myId then return (gamma, empty_string, empty_string,
    I_sender, empty_string)
    control = ("add-ack", ++gamma.mySeq, (sender, seq))
    (gamma, c) = encrypt-to(gamma, added, ratchet[gamma.myId])
    (gamma, _, _, I_me, _) = process-add-ack(gamma, gamma.myId, gamma.mySeq,
    (sender, seq), empty_string)
    return (gamma, control, {(added, c)}, I_sender, I_me)

```

#### process-add-ack

This function is invoked by both the sender and each recipient of an `add-ack`
message, including the new group member. Upon lines 1–2, the acknowledgment is
added to `gamma.history`, mirroring the process in `process-ack`.
If the current user is the new group member, the `add-ack` message includes the
direct message constructed in `process-add`; this direct message contains the
encrypted ratchet state of the sender of the `add-ack`, then it is decrypted on
lines 3–5.

Upon line 6, a check is performed to check if the local user was already a
group member at the time the `add-ack` was sent. If affirmative, a new update
secret `I` for the sender of the `add-ack` is computed on line 7 by invoking
`update-ratchet` with the constant string `add`.

In the scenario involving the new member,  the ratchet state was recently
initialized on line 5. This ratchet update facilitates all group members,
including the new addition, to derive each member’s update by obtaining any
update secret from before their inclusion.

```text
op = ("ack", sender, seq, ackID, ackSeq)
gamma$.history = gamma.history + {op}
if dmsg != empty_string then
    (gamma, s) = decrypt-from(gamma, sender, dmsg)
    gamma.ratchet[sender] = s
if gamma.myId in member-view(gamma, sender) then
    (gamma, I) = update-ratchet(gamma, sender, "add")
    return (gamma, empty_string, empty_string, I, empty_string)
else return (gamma, empty_string, empty_string, empty_string, empty_string)

```

#### process-welcome

This function serves as the second step called by a newly added group member.
In this context, `adderHistory` represents the adding user’s copy of
`gamma.history` sent in their welcome message, which is utilized to initialize
the added user’s history.
Here, `c` denotes the ciphertext of the adding user’s ratchet state, which is
decrypted on line 2 using `decrypt-from`.

Once `gamma.ratchet[sender]` is initialized, `update-ratchet` is invoked twice
on lines 3 to 5 with the constant strings `welcome` and `add` respectively.
These operations mirror the ratchet operations performed by every other group
member in `process-add`.
The outcome of the first `update-ratchet` call becomes the first member secret
for the added user,
while the second call returns `I_sender`, the update secret for the sender of
the add operation.

Subsequently, the new group member constructs an *ack* control message to
broadcast on line 6 and calls `process-ack` to compute their initial update
secret I_me. The function `process-ack` reads from `gamma.memberSecret` and
passes it to `update-ratchet`. The previous ratchet state for the new member is
the empty string `empty`, as established by `init`, thereby initializing the
new member’s ratchet.
Upon receiving the new member’s `ack`, every other group member initializes
their copy of the new member’s ratchet in a similar manner.

By the conclusion of `process-welcome`, the new group member has acquired
update secrets for themselves and the user who added them.
The ratchets for other group members are initialized by `process-add-ack`.

```text
gamma.history = adderHistory
(gamma, gamma.ratchet[sender]) = decrypt-from(gamma, sender, c)
(gamma, s) = update-ratchet(gamma, sender, "welcome")
gamma.memberSecret[sender, seq, gamma.myId] = s
(gamma, I_sender) = update-ratchet(gamma, sender, "add")
control = ("ack", ++gamma.mySeq, (sender, seq))
(gamma, _, _, I_me, _) = process-ack(gamma, gamma.myId, gamma.mySeq, (sender,
seq), empty_string)
return (gamma, control, empty_string , I_sender, I_me)

```

## Privacy Considerations

### Dependency on PKI

The [DCGKA](https://eprint.iacr.org/2020/1281) proposal presents some
limitations highlighted by the authors.
Among these limitations one finds the requirement of a PKI (or a key server)
mapping IDs to public keys.

One method to overcome this limitation is adapting the protocol SIWE (Sign in
with Ethereum) so a user `u_1` who wants to start a communication with a user
`u_2` can interact with latter’s wallet to request a public key using an
Ethereum address as `ID`.

#### SIWE

The [SIWE](https://docs.login.xyz/general-information/siwe-overview) (Sign In
With Ethereum) proposal was a suggested standard for leveraging Ethereum to
authenticate and authorize users on web3 applications.
Its goal is to establish a standardized method for users to sign in to web3
applications using their Ethereum address and private key,
mirroring the process by which users currently sign in to web2 applications
using their email and password.
Below follows the required steps:

1. A server generates a unique Nonce for each user intending to sign in.
2. A user initiates a request to connect to a website using their wallet.
3. The user is presented with a distinctive message that includes the Nonce and
details about the website.
4. The user authenticates their identity by signing in with their wallet.
5. Upon successful authentication, the user's identity is confirmed or
approved.
6. The website grants access to data specific to the authenticated user.

#### Our approach

The idea in the [DCGKA](https://eprint.iacr.org/2020/1281) setting closely
resembles the procedure outlined in SIWE. Here:

1. The server corresponds to user D1,who initiates a request (instead of
generating a nonce) to obtain the public key of user D2.
2. Upon receiving the request, the wallet of D2 send the request to the user,
3. User D2 receives the request from the wallet, and decides whether accepts or
rejects.
4. The wallet and responds with a message containing the requested public key
in case of acceptance by D2.

This message may be signed, allowing D1 to verify that the owner of the
received public key is indeed D2.

### Multi-device setting

One may see the set of devices as a group and create a group key for internal
communications.
One may use treeKEM for instance, since it provides interesting properties like
forward secrecy and post-compromise security.
All devices share the same `ID`, which is held by one of them, and from other
user’s point of view, they would look as a single user.

Using servers, like in the paper
[Multi-Device for Signal](https://eprint.iacr.org/2019/1363), should be
avoided; but this would imply using a particular device as receiver and
broadcaster within the group.
There is an obvious drawback which is having a single device working as a
“server”. Should this device be attacked or without connection, there should be
a mechanism for its revocation and replacement.

Another approach for communications between devices could be using the keypair
of each device. This could open the door to use UPKE, since keypairs should be
regenerated frequently.

Each time a device sends a message, either an internal message or an external
message, it needs to replicate and broadcast it to all devices in the group.

The mechanism for the substitution of misbehaving leader devices follows:

1. Each device within a group knows the details of other leader devices. This
information may come from metadata in received messages, and is replicated by
the leader device.
2. To replace a leader, the user should select any other device within its
group and use it to send a signed message to all other users.
3. To get the ability to sign messages, this new leader should request the
keypair associated to the ID to the wallet.
4. Once the leader has been changed, it revocates access from DCGKA to the
former leader using the DCGKA protocol.
5. The new leader starts a key update in DCGKA.

Not all devices in a group should be able to send messages to other users. Only
the leader device should be in charge of sending and receiving messages.
To prevent other devices from sending messages outside their group, a
requirement should be signing each message. The keys associated to the `ID`
should only be in control of the leader device.

The leader device is in charge of setting the keys involved in the DCGKA. This
information must be replicated within the group to make sure it is updated.

To detect missing messages or potential misbehavior, messages must include a
counter.

### Using UPKE

Managing the group of devices of a user can be done either using a group key
protocol such as treeKEM or using the keypair of each device.
Setting a common key for a group of devices under the control of the same actor
might be excessive, furthermore it may imply some of the problems one can find
in the usual setting of a group of different users;
for example: one of the devices may not participate in the required updating
processes, representing a threat for the group.

The other approach to managing the group of devices is using each device’s
keypair, but it would require each device updating these materia frequently,
something that may not happens.

[UPKE](https://eprint.iacr.org/2022/068) is a form of asymetric cryptography
where any user can update any other user’s key pair by running an update
algorithm with (high-entropy) private coins. Any sender can initiate a *key
update* by sending a special update ciphertext.
This ciphertext updates the receiver’s public key and also, once processed by
the receiver, will update their secret key.

To the best of my knowledge, there exists several efficient constructions both
[UPKE from ElGamal](https://eprint.iacr.org/2019/1189) (based in the DH
assumption) and [UPKE from Lattices](https://eprint.iacr.org/2023/1400)
(based in lattices).
None of them have been implemented in a secure messaging protocol, and this
opens the door to some novel research.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [DCGKA](https://eprint.iacr.org/2020/1281)
- [MLS](https://messaginglayersecurity.rocks)
- [CoCoa](https://eprint.iacr.org/2022/251)
- [Causal TreeKEM](https://mattweidner.com/assets/pdf/acs-dissertation.pdf)
- [SIWE](https://docs.login.xyz/general-information/siwe-overview)
- [Multi-device for Signal](https://eprint.iacr.org/2019/1363)
- [UPKE](https://eprint.iacr.org/2022/068)
- [UPKE from ElGamal](https://eprint.iacr.org/2019/1189)
- [UPKE from Lattices](https://eprint.iacr.org/2023/1400)
