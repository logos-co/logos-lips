# Immutable Protocol Rotation

| Field | Value |
| --- | --- |
| Name | Immutable Protocol Rotation |
| Status | raw |
| Type | RFC |
| Category | Informational |
| Tags | logos-chat |
| Editor | jazzz <jazz@logos.co> |

<!-- timeline:start -->

## Timeline

<!-- timeline:end -->

## Abstract

In a decentralized network no operator can force an upgrade,
so a breaking change cannot be used
until most of the network has adopted it.
This document describes an approach that removes that wait
by not versioning protocols at all:
functionality is composed from smaller protocols, each immutable,
and a change is published as a new protocol
rather than a new version of an existing one.
A stable listening protocol settles which of them an interaction uses,
and participants take up a change by rotation —
establishing a new interaction under a newer protocol
and leaving the old one behind.
Because agreement is scoped to a single interaction,
a change obliges no one outside it,
and a change to an operational protocol stops being an event
the whole network has to live through together.

## Terminology

This document uses the shared terminology defined in
[CHAT-DEFINITIONS](chatdefs.md), including **Client** and **Application**.

The following terms are specific to this document:

- **Interaction** — a bounded exchange of information between a known set of
  parties. In messaging, a conversation.
- **Participant** — a party to an interaction.
- **Protocol** — a specification that defines how parties interact.
  A protocol is immutable: once published it does not change.
  A protocol may be composed of other protocols,
  each replaced independently of the others.
- **Interop-domain** — for a given protocol, the minimal set of parties
  that must agree on it to avoid a partition.
- **Macro protocol** — a protocol that bundles the listening and operational
  roles into a single indivisible unit rather than composing them from
  separately replaceable protocols. Most existing communication protocols
  are macro protocols.
- **Listening protocol** — the protocol by which parties establish an
  interaction with one another, and settle which operational protocol it will
  use. In messaging, this covers key material and invitations.
- **Operational protocol** — the protocol under which an established
  interaction is conducted. In messaging, a ConversationType.
- **Rotation** — taking up a change by establishing a new interaction
  under a newer operational protocol and leaving the old one behind.
  Nothing upgrades in place: neither an established interaction
  nor a published protocol ever changes. Distinct from key rotation,
  which replaces mutable state within an existing interaction.
- **Supported set** — the protocols a given client or application is willing
  to speak. Each chooses its own.
- **Network** — every party that can be reached, whether or not any interaction
  exists between them.

## Motivation

The standard deployment cycle for new decentralized protocol features is slow.
Commits are written, tested and merged quickly.
Those changes do not reach users until enough of the network has adopted them,
and there is no operator who can force that adoption —
no service to upgrade and no old endpoint to close.

For two applications to interoperate they must understand the same payloads,
and an older client simply cannot read a newer one.
In the decentralized context version deployment is a sequence of independent
tasks, each performed by a party the one before it cannot compel:
client developers implement the change,
application developers import the new library and ship a release,
and individual users update their applications.

Enabling a breaking change partitions the network into two sets —
those who can process the new payloads and those who cannot.
The longer a change is left to soak, the smaller the second set becomes.

Two costs follow from this model.

The first is that the pace is set by the least current members of the network.
The most active users may update within days,
but they cannot use what they have until the bulk of the network has followed,
often around 80%.
In practice a change takes three to six months to deploy.
The capability exists on both ends of an interaction and cannot be exercised,
because a third party has not moved.

The second is that contributors and developers spend their time coordinating.
Choosing a soak period, aligning release schedules and tracking adoption
are not protocol work,
and every layer of the stack pays the cost.
Worse, they recur on every breaking change,
so the cost scales with the number of changes rather than being paid once.

The end result is a slow ossification of the protocol.
The overhead of deployment is roughly fixed regardless of the size of the change,
so only large ones are worth putting through it.
Small improvements queue behind them,
and the protocol advances in rare, heavy steps rather than continuously.

The goal of the approach described here is not to eliminate breaking changes
altogether.
It is to allow changes to reach end users without waiting on the rest of the
network, while minimizing the workload of protocol contributors and app
developers alike.

## Background

### Observations

The approach rests on the following observations.

**The pain point of upgrades is: old clients cannot understand new data**
Until a client updates it cannot understand newly formatted data.
Technologies like Protobuf guarantee that future changes will always be parsable for past clients — though the data will be meaningless.

**Not all parts of a protocol change at the same rate.**
Breaking changes are not uniformly distributed — they occur in some regions more than others.
See [Interoperability domains](#interoperability-domains).

**Centralized services provide a point at which protocol rules can be enforced**
Every exchange passes through one operator, so that operator can validate payloads,
refuse clients below a minimum version, translate at the boundary,
observe what the population is running, and close the old path when it chooses.
Decentralized systems have no such point.
Rules are applied at the edge, by each party, for itself.
A peer cannot be compelled to apply them — it can only be refused,
and refusal ends an interaction rather than upholding a rule across the network.

**Breaking changes come from mutating shared resources**
Adding a resource breaks nobody; altering an existing one breaks everyone relying on it.

**Immutable protocols make compatibility trivial.**
Two parties either speak a given protocol or they do not;
there is no version range to reconcile and no behavior to detect.
Publishing a new protocol adds an option and removes nothing,
so an interaction under an old one continues undisturbed.

**Capability negotiation is an easier task than coordinating upgrades.**
Upgrading requires all entities to coordinate when to switch.
Whereas capability negotiation can occur asynchronously offline.

### Interoperability domains

Every protocol has an interop-domain:
the set of parties that must understand it for the protocol instance to work.
These domains are not the same size, and they scale with different things.
This document writes `I(x)` for a domain that grows with x,
by analogy with complexity notation.

Listening protocols must be understood by everyone or a partition will occur.
Two parties who cannot resolve each other's identity cannot interact at all,
so the domain covers the whole network and grows with the number of accounts (`I(accounts)`).

The operational protocols — in messaging, a ConversationType — are different.
Only their participants need to agree on the protocol for a given instance,
and no party outside it is affected by what they use.
That domain grows with the number of participants and nothing else (`I(participants)`).

The size of a protocol's interop-domain sets the cost of changing it.
A protocol that connects everyone can only be changed by agreement of everyone;
a protocol that connects five people needs the agreement of five.
The difference is not only size but growth: `I(accounts)` rises with the network,
while `I(participants)` stays put however large the network becomes.
A macro protocol treats the whole of its functionality as one indivisible unit,
which gives each of its parts the largest domain that any one of them requires.
Every change is then priced at `I(accounts)`, including the changes that only needed `I(participants)`.

## Theory / Semantics

### Overview

Rather than trying to control all members of a decentralized and distributed network, embrace their autonomy.
Modifying existing code and services in a breaking manner requires coordination across all its consumers. This might be possible in a centralized system, but quickly becomes unrealistic when code spans multiple organizations.
Instead leave existing code and infrastructure in place and create new resources.

The problem space then becomes helping developers manage adoption rather than trying to achieve consensus. Adoption occurs asynchronously on a developer's own timeline. Developers are incentivized by new features and keeping their users happy — which provides forward progress on the network.

This approach side-steps upgrade and migration issues, but opens new areas of complexity:
- Developers need to update their applications to support new protocols, including refactors and mapping features.
- Deploying new protocols is potentially disruptive to the user experience.
- New protocols require new pathways.
- Clients need to perform capability discovery.
- Protocol fragmentation leads to network fragmentation, which results in interaction failure.

These problems are local to a single implementation and payable on one team's schedule, whereas consensus-based rollouts require agreement between parties that cannot compel one another.

### Approach

First adopt the invariant that once deployed a protocol is immutable — it cannot change — a client that understands that protocol will understand it forever.

As a protocol cannot be changed, it's important to minimize the impact of changes. By sub-dividing a large protocol into smaller protocols, the affected surface area is reduced.

In general protocols can be divided into two categories:
- **Listening protocols**: Handles first interaction between two clients. Its purpose is to define how one client "calls" another.
- **Operational protocols**: Defines functionality desired by clients.

A messaging protocol, for example, can be decomposed into the component that listens for incoming messages (Listening), and the component which decrypts and handles new payloads (Operational). Operational protocols can be further decomposed into other operational protocols (e.g. Encryption vs Content handling). The dividing line here is whether or not the protocol must handle payloads from clients without any prior coordination.

Listening protocols provide payload discovery, and also provide payload routing. Inbound messages are received by the listening protocol and then forwarded to the operational protocol which can process them. This means that a client can support multiple operational protocols simultaneously — spinning up multiple operational protocols is the same as defining a handler, and registering the type with the listening protocol.

### Breaking Change Landscape

The split between listening and operational protocols falls on a natural fault line — listening protocols are almost always "breaking changes" because any change here has no mitigation. It's the first opportunity to process data: any disagreement in payload type will result in interaction failure. Adding additional fields to a payload is not in itself a breaking change, but those are almost always accompanied by protocol changes. Other than trivial changes, most new protocol features are accompanied by a required change to behavior.

Decomposing a macro protocol into a listening protocol does not change the number of breaking changes this code will experience. If a change is needed to the listening code it would be a breaking change in both approaches.

Operational protocols are anecdotally where most of the breaking changes come from, as that's where protocol features are implemented. With the chaotic changes removed — listening protocols become lightweight and more stable compared to macro protocols due to their reduced surface area. Having a stable entry point means there are fewer breaking changes that cause fragmentation, and keeps fallback and negotiation possible.

### Consent

Underneath the mechanics is a single principle:
no one in the system has a change imposed on them by another.

The system has four layers of choice, and each is free.
Protocol contributors publish what they think is worth publishing.
Client developers decide which of those protocols to expose.
Application developers choose a client, and change clients if another
serves them better.
Users choose an application, and leave if it stops serving them.

Nothing above binds anything below.
A contributor cannot oblige a client to carry a protocol,
a client cannot oblige an application to use one,
and an application cannot oblige a user to stay.
The final decision belongs to users,
and it is exercised by leaving rather than by negotiating.

The mechanics in this document exist to make that principle true in practice
rather than in name.
Immutability means a protocol cannot change under someone who chose it.
Interaction-scoped interoperability means one group's decision
does not reach another group.
A coordinated network upgrade is the opposite of all of this:
it is a moment at which everyone is made to accept a change
chosen on their behalf.

This also bounds what the system can promise.
An application that handles a user's messages can misuse them,
and no protocol prevents that.
What a protocol can do is keep the cost of leaving low,
which means ensuring a user who moves to another application
keeps their identity, remains reachable,
and can still talk to the people they could talk to before.
Exit is only a real choice if it is cheap.

### Protocol Selection

A new interaction is conducted under one operational protocol,
and someone has to pick it.
Initialization via the listening protocol establishes which operational protocols the participants have in common;
the party that initiates the interaction chooses among them —
in messaging, whoever creates the group.

Because a client supports many protocols at once,
several may be available to a given set of participants,
and the initiator may pick any of them, including the oldest.
This is not a problem that selection has to solve.
It is a problem the supported set has already solved.

A client's supported set is its security policy.
A protocol nobody is willing to speak cannot be selected,
and a client that has withdrawn a protocol cannot be steered onto it
by a peer, an administrator, or an attacker.
If the only protocol another party will speak is one this client
does not trust, the correct outcome is that no interaction is established.

Once the set has been curated, what remains is preference rather than safety.
Later protocols generally carry the fixes of earlier ones
along with whatever was added since,
so the newest protocol available to all participants is usually the best one,
and often the only sensible choice.
Where two protocols are genuinely incomparable, the choice is a matter of
taste, and the initiator breaks the tie.

Ordering is held by client developers.
A client sits between protocol contributors and application developers,
and is the natural place for a stated preference over the protocols it exposes.
Contributors should make clear, in changelogs and in libraries,
which protocol they consider current;
that guidance is advisory and binds no one.

### Protocol Deprecation

Adding a protocol costs nobody anything.
Withdrawing one is a breaking change, and it retains all of the old properties:
whoever is still relying on it loses the ability to interoperate.
The coordination cost does not disappear, it moves to the end
of a protocol's life rather than the beginning.
Two cases are worth separating.

**Disuse.** Use has fallen far enough that carrying the code is not worth it.
Nothing here is urgent, so withdrawal can happen on whatever schedule
suits the developer doing it —
including the slow schedule a network upgrade used to require,
now with far less at stake.
The decision has also moved to a better place.
It is no longer a protocol contributor deciding which of the network's users
to strand, but an application developer deciding for their own users,
who can leave if they disagree.

**Compromise.** A protocol is found to be unsafe and should no longer
be reachable.
Here timing matters, and the benefit does not arrive by publishing the fix.
Publishing a replacement protects nobody on its own,
because the unsafe protocol remains valid and remains selectable.
Protection begins when a client refuses the unsafe protocol,
and that refusal is the interoperability break.

The tradeoff is real, but this arrangement improves it in two ways.
Publishing the replacement and withdrawing the original are separate actions
that can happen at different times.
In a coordinated upgrade they are the same event,
which is why the cutover has to be planned and why it is expensive.
Here the replacement can be published immediately
and adopted at whatever rate clients update,
while the unsafe protocol is still supported.
By the time it is withdrawn, fewer parties are still relying on it,
because the population using it has been draining the whole time.

Second, withdrawal requires nobody's agreement.
Any client may refuse a protocol at any moment, unilaterally,
and the cost is limited to the peers who have not yet caught up.
There is no button that disables an unsafe protocol network-wide;
in a decentralized system there never was one.
What this arrangement offers is a response that is itself decentralized,
and that reaches the most active users first.

Users who never update are never protected.
That is true of any decentralized system and is not improved here.

## Costs

**Increased API Complexity**
Managing a single API that covers a wide collection of protocols requires careful planning.
This work falls on contributors and client developers. It is unfortunately the cost of fewer breaking changes, and faster development.
It also puts the complexity where it is easiest to solve. Deferring upgrade complexity to app developers makes sense for homogenous applications where there is a single supported app, for a given protocol. In an interoperable environment that's the worst place to tackle this problem. Instead allow engineering teams to do what they do best — solve problems and build stable APIs.

## Implementation Suggestions

A client should make the supported set a matter of configuration —
a list of protocols passed in, with a sensible default provided —
so that adding or withdrawing a protocol is a configuration change
for an application developer rather than an engineering project.

The default should reflect what contributors currently recommend,
and should be revisited when a protocol is withdrawn for compromise.
Most applications will take the default, which makes it the point at which
the network's behaviour is in practice decided.
It is worth being deliberate about that:
the default is advisory and binds no one,
but it is where coordination has gone,
and it should be maintained with that in mind.

Contributors should state clearly when a protocol Pareto-dominates an existing protocol.
A strict well order is not required between protocols, but most development follows this pattern and it's worth being explicit.

## Security/Privacy Considerations

### Security

The security of an interaction is determined by the supported sets
of its participants, not by the selection made within them.
A client that continues to support a protocol can be steered onto it,
and should assume it will be.
Withdrawal, not publication, is what removes exposure.

Because clients support several protocols simultaneously,
a party choosing among them may choose the weakest that all participants share.
This is a surface the approach introduces:
where a single protocol is in force, the choice does not exist.
The mitigation is the supported set, and it is the only mitigation.

Withdrawing a compromised protocol strands the parties still using it.
This is a genuine cost and it falls on the least active users,
who are also the least likely to have received the replacement.
Withdrawing early protects more of the active population sooner;
withdrawing late strands fewer people.
The approach narrows the blast radius of that decision to one application's
users and moves the decision to the developer who serves them,
but it does not remove it.

## Copyright

Copyright and related rights waived via
[CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

### Informative

- [CHAT-DEFINITIONS](chatdefs.md)
- [ConversationTypes](../../application/raw/conversationtypes.md)
