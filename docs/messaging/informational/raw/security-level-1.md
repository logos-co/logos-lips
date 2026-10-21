

# Security Level: SL-1 (ASTRO)

| Field | Value |
| --- | --- |
| Name | Security Level: SL-1 (ASTRO) |
| Status | raw |
| Type | RFC |
| Category | informational |
| Tags | chat/informational |
| Editor | Jazzz <jazz@status.im> |

SL-1 is the baseline security level for group chats. It keeps message content confidential and authentic against outsiders and malicious providers, and it limits the damage when a member's keys leak. A system qualifies for SL-1 only if it meets every goal, given the SL1-A assumptions.

## Scope and terms

Every goal is a promise about a group communication protocol. SL-1 states properties, not mechanisms. How a particular system meets them belongs in that system's own design docs. Other docs cite the level as "SL-1" and a single item by its ID, for example SL1-PCS.

| Term | Meaning |
| --- | --- |
| Identity | A long-term key that represents one person. It authorizes that person's members. |
| Member | One installation in the group, with its own keys. |
| Group state | The agreed membership and keys of a group at a point in time. Each change produces a new state. |
| Provider | Any party that runs a service the group depends on, such as relaying, storage, key distribution, or ordering. |

## Assumptions

The goals only have to hold while these do. If one fails, the goals that depend on it fail too.

| ID | Assumption | Why it's needed |
| --- | --- | --- |
| SL1-A1 | Identity keys are never compromised or lost. | Identity keys authorize and revoke members. Whoever holds one controls that person's members. |
| SL1-A2 | Members are honest but faulty. They act in good faith, but may crash, go offline, fall behind, or keep stale state. | SL-1 limits what outsiders can do. It doesn't defend a group against its own members. |
| SL1-A3 | Compromised members stay under the fault threshold of the group's ordering mechanism. | Above that threshold, compromised members can block or fork group state changes. |
| SL1-A4 | All clients see the same history of keys for each identity. | Without this, an attacker could show different members different keys for the same person. |
| SL1-A5 | Clients implement the protocol correctly, including deleting key material when required. | Forward secrecy and post-compromise security depend on old keys actually being deleted. |
| SL1-A6 | The cryptographic primitives are secure. | Every goal rests on them. |

## Goals

Every goal must hold against every threat below. Attackers may delay progress, but they must never break a goal.

| ID | Goal | A qualifying system ensures that… | Why it matters |
| --- | --- | --- | --- |
| SL1-CC | Content confidentiality | Only members at the time a message is sent can read it. | Private messages stay private. Only the people in the conversation can read what was said. |
| SL1-SA | Sender authenticity | Every message traces to the specific member that sent it. | No one can masquerade as someone else. Every message can be verified as coming from a valid member, so outsiders can't inject messages. |
| SL1-INT | Integrity | Members reject any message that was altered or replayed. | Members can't be tricked into believing something that wasn't said. No one can alter or backdate a message: what is received is exactly what was sent. |
| SL1-FSE | Forward secrecy (epoch) | A key compromised today does not expose messages from a previous epoch. | A phone stolen or seized today can't decrypt traffic that was recorded before. |
| SL1-PCS | Post-compromise security | After a compromise, confidentiality is eventually restored. Once that member's keys are refreshed and the other members have processed the change, whoever holds the leaked state can no longer read new messages. | A leaked key heals itself. It doesn't keep exposing messages far into the future. |
| SL1-GA | Group agreement | All members converge on the same membership for each group state. | When someone is removed, every member can be sure they are really gone. Without agreement, members can't be certain who is in the group, so they can't know who is reading. |
| SL1-MSU | Member-only state updates | Members accept a group state update only if a valid member made it. A valid member is a current member that has not been revoked. | A stranger or a provider can't slip into a private group to read along, or kick members out. |
| SL1-REV | Revocation | A member its owner revokes is eventually removed from the group. | Without revocation, a lost device would give permanent access to an unintended participant. |
| SL1-CR1 | Censorship resistance (single provider) | No single malicious provider can stop members from communicating. If one provider withholds or drops traffic, members still reach each other through another. | One provider going down, or dropping traffic can't silence the group. |

## Threats

| Source | Who | Tries to | Stopped by |
| --- | --- | --- | --- |
| Outsider | Anyone who is not a member | Read, forge, replay, or inject messages; change group state | CC, SA, INT, MSU |
| Provider | Any party that runs a service the group depends on | Everything an outsider can, plus withhold, drop, delay, or partition delivery | GA, CR1 |
| Compromise | Whoever holds a copy of a member's state | Read past messages; keep reading new ones; keep acting as the member; act as another member | FSE, PCS, REV, SA |

**Known limits**

- Forward secrecy doesn't protect messages still stored on a compromised device.
- A compromised member stays exposed until its keys are refreshed or it is revoked.
- An accomplice added by a compromised member stays in the group after that member is revoked.

## Non-goals

- **Real-world identity binding:** proving that an identity belongs to a particular person.
- **Availability:** guaranteed delivery or progress despite colluding providers or faulty members.
- **Deniability, and history for new members.**
- **Copying by readers:** a member who can read a message can always copy it. No level can prevent that.