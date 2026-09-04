---
title: SNT-STAKING-STREAMER
name: Status Network Staking Streamer Protocol
status: raw
category: Standards Track
tags: status-network
editor: 
contributors: 
- Jimmy Debe <jimmy@status.im>
---

## Abstract

This specification describes the components used for the Status Network Staking Streamer protocol.
The protocol is a set of smart contract protocols currently used in [Status Network](https://status.network/).

## Background/Motivation

Traditional layer 2 blockchains generate revenue from gass fees required to make transactions on the network.
This can introduce a barrier of entry for users wanting to build and
interact with that blockchain.
The Status Network is a layer 2 roll up where applications and
users do not blockchain with gasless transactions.
Revenue is derived from a few sources including native yield commission.
Assests bridged to the Status Network are rehypothecated into yield-bearing equivalents and
users earn an [ERC-20 token](https://eips.ethereum.org/EIPS/eip-20) called Karma.
Karma is an goverance token in the Status Network that gives the user access to a certain throughput of free transactions,
votings and other network benefits.
The SNT token can also be staked with the staking streamer protocol to earn Karma.

The goal is to have a staking mechanism that is fair to all participants based on the stake amount and time staked.
Participants will have significant increases in voting power after committing their stake for a longer period,
even if their stake is not the largest among all participants.

## Specification

The key words “MUST”, “MUST NOT”, “REQUIRED”,
“SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [2119](https://www.ietf.org/rfc/rfc2119.txt).

The staking streamer protocol is a set of smart contracts that implements the staking system.
The protocol consists of the following components:

- accounts
- staking operator
- multipler points
- reward mechanism
- staking vaults

The staking system MUST be supported by an `OPERATOR` who will introduce reward amounts,
reward periods, the token defined by its contract address REQUIRED for use in the system and
making updates to the staking smart contracts.
It is the responsibility of the `OPERATOR` to keep accounts informed about the requirements
and intended changes to the staking system.

### Accounts

Accounts are users who contribute a token, ERC-20 standard, to the staking protocol.
Accounts SHOULD interact with the protocol through a layer-1 blockchain smart contract.
To participate,
users MAY use an external owned account (EOA) and/or a smart account to interact with a `stakeVault` contract.
A `stakeVault` is a smart contract that records and
maintains the current amount of tokens transferred by accounts to the protocol.
Each `stakeVault` MUST have one registered as the owner.
Once registered, the user is considered as an account.
Accounts MAY be the owner of one or more `stakeVault`s.

#### Account Staking Flow

When joining a staking system,
accounts MUST use a `stakeVault` to transfer a token amount to the `stakingManager` contract,
which is described [below](#operator-role).
The account MUST use the same token, identitied by the token address,
as registered in the `stakeVault` by the `OPERATOR`.
Accounts MAY set a predefined duration to lock those tokens.
Tokens will not be retrievable by accounts until the set duration expires.
This is designed to improve the rewards accrued by accounts deciding to lock funds.

After tokens have successfully been transferred to the `stakeVault`,
the account responsible will start to accumulate multiper points.
The rewards and multipler points are described in the [Rewards section](#rewards) below.
If staked tokens are not locked, the account MAY withdraw the full amount of tokens at any time.

### Operator Role

The `OPERATOR` is the owner of the staking system by registering an address on the `stakeManager` contract.
The `OPERATOR` MUST deploy a `stakeManager` smart contract and
facilitate the requirements of the system.
Each account MUST use a `stakeVault` to interact with the `stakeManager`.
This includes transferring to and from the staking system.

The operator MAY set a preferred minimum lock duration for all tokens entering the system.
Accounts transaction MUST fail if the minimum lock duration is not set.
After a minimum lock duration is set,
the operator SHOULD NOT be able to update this amount until the set period is complete.

The `stakeManager` SHOULD be upgradable only by the registered operator.
Contract upgrades will occur when an operator wants to add and/or
change the requirements of the system.
When accounts are aware of changes, either by the operator informing accounts or
accounts reading the blockchain state,
accounts MAY leave the system if they do not agree with the changes.
Including when the operator enables `emergencyMode`.

- The operator decides the amount of rewards that should be awarded to stakers.
- The operator MUST specify the amount of time for rewards to be distributed.

#### Emergency Mode

In some cases,
an operator may choose to stop the functionality of the staking system.
When `emergencyMode` is enabled, the following SHOULD apply:

- new vaults can not register,
- current registered vaults can not stake or stake additional tokens with a lock period,
- operators can not update the global state
- accounts can not claim accrued rewards.

### Rewards

Accounts participate in the staking protocol to earn rewards.
The staking system implements a rewards distribution mechanism,
that works in conjunction with a internal accouting system called multiplier points.

#### Multiplier Points

When accounts have staked for a certain amount of time,
multipler points (MP) are accrued.
The accrued MP is counted toward the account's weight for reward distribution, as described [below](#account-weight).
This ensures that participants are rewarded fairly based on the stake amount
and time staked.
The MP is accumulated over time and MUST not be transferable.
The calculation is based on two factors, Initial MP and Accured MP.

##### Initial MP

Initial MP SHOULD be issued immediately when tokens are staked with or
without a lock-up period.
It is based on the stake amount and lock-up duration.
The formula for Initial MP is derived as follows:

$$
\text{MP}_ \text{Initial} = \text{Stake} \times \left( 1 + \frac{\text{APY} \times T_ \text{lock}}{100 \times T_ \text{year}} \right)
$$

Where:

- $Stake$ = The amount of tokens staked.
- $APY$ = Annual Percentage Yield, set at 100%.
- $T_{lock}$ = Lock-up duration in seconds.
- $T_{year}$ = Total seconds in a year.

This formula calculates the Initial MP issued immediately when tokens are staked with a lock-up period.
The longer the lock-up period, the more MP are issued.
Accounts locking stake MAY earn bonus MP, which  MAY be added to the initial MP amount.
For example, Alice stakes 100 tokens with no lock-up time:

$$
\text{MP}_ \text{Initial} = 100 \times \left( 1 + \frac{100 \times 0}{100 \times 365} \right)
$$

$$
\text{MP}_ \text{Initial} = 100 \times \left( 1 + 0\right) = 100
$$

Alice receives 100 MP.

Another example, Alice stakes 100 tokens with a 30 day lock-up period:

$$
\text{MP}_ \text{Initial} = 100 \times \left( 1 + \frac{100 \times 30}{100 \times 365} \right)
$$

$$
\text{MP}_ \text{Initial} = 100 \times \left( 1 + 0.082 \right) = 108.2
$$

Alice receives 108.2 MP.
By locking up the stake for 30 days,
Alice receives an additional 8.2 MP.
Alice cannot access the tokens until the lock-up period has passed.

##### Accrued MP

The Accrued MP SHOULD be accumulated over time as a function of the stake amount,
elapsed time, and annual percentage yield (APY).
The Accrued MP formula is derived as follows:

$$
\text{MP}_ \text{Accrued} = \text{Stake} \times \frac{\text{APY} \times T_ \text{elapsed}}{100 \times T_ \text{year}}
$$

Where:

- $T_{elapsed}$: Time elapsed since staking began, measured in seconds.

This formula adds MP as a function of time,
rewarding accounts with locked stake.
The Accrued MP is calculated based on the stake amount.
Already accrued MP SHOULD not affect the calculation of new accrued MP.
For example, Alice stakes 100 tokens for 15 days:

$$
\text{MP}_ \text{Accrued} = 100 \times \frac{100 \times 15}{100 \times 365} = 4.1
$$

Alice receives 4.1 MP for the 15 days of staked tokens.
This is exactly half of the MP that would have been received if tokens were
locked for 30 days.
Another example, Alice stakes 100 tokens for 30 days:

$$
\text{MP}_ \text{Accrued} = 100 \times \frac{100 \times 30}{100 \times 365} = 8.2
$$

Alice receives 8.2 MP for the 30 days she has staked.

The `stakingManager` contract SHOULD account for all MP accrued by all accounts in the system.
Accounts are REQUIRED to make an on-chain transaction to claim MP.
At any time, accounts MUST be able to retrieve the total MP accrued by the staking system by reading the contract state.
Total MP combines both accrued MP and pending MP.
The accrued MP contains the initial MP and the MP accrued over time.
Pending MP are MP that have yet to be "claimed" by the accounts:

$$
\text{MP}_ \text{Total} = \text{MP}_ \text{Accrued} + \text{MP}_ \text{Pending}
$$

Accounts SHOULD be limited to a total maximum amount of MP that can accrue.
This will prevent accounts from accumulating large amounts of MP over time compared to other accounts.
The maximum amount of MP an account can accrue is capped at:

$$
\text{MP}_\text{Maximum} = \text{MP}_ \text{Initial} + \text{MP}_ \text{Potential}
$$

- $\text{MP}_ \text{Initial}$: The initial MP an account receives when staking, \*_including the bonus MP_.
- $\text{MP}_ \text{Potential}$: The initial MP amount multiplied by a $MAX\_MULTIPLIER$ factor.
- $MAX\_MULTIPLIER$: A constant that determines the multiplier for the maximum amount of MP in the system.

For example, assuming a $MAX\_MULTIPLIER$ of `4`, an account that stakes 100 tokens would have a maximum of:

$$
\mathrm{MP}_{\text{Maximum}} = 100 + (100 \times 4) = 500
$$

This means that the account can never have more than 500 MP,
no matter how long they stake.

#### Reward Distribution

The system distributes rewards based on a few main factors:

- The amount of tokens staked
- The account's Multiplier Points (MP)
- the account's system weight
- The account's reward index

#### Account Weight

Every account in the system has a weight associated with it.
This weight is calculated as the sum of the staked tokens
and the MP:

$$
\text{Account Weight} = \text{Staked Balance} + \text{MP Balance}
$$

In addition, the system MUST track the total weight of all accounts in the system:

$$
\text{Total System Weight} = \sum_{i=1}^{n} \text{Account Weight}_i
$$

The account's MP grows linearly with time,
which means, account weights increase with time, which in turn means,
the total weight of the system increases with time as well.
With the weights mechanism implemented,
the system can now calculate the rewards for each account.
For an individual account,
divide the account's weight by the total system weight and
multiply it by the total reward amount:

$$
\text{Reward Amount} = \text{Account Weight} \times \frac{\text{Total Reward Amount}}{\text{Total System Weight}}
$$

The rewards are calculated in real-time,
they don't actually need to be claimed by any account.
However, whenever an account performs blockchain state change,
such as staking or unstaking funds,
the rewards that have been accrued up to this point are updated in the account's storage.

Any real-time rewards are considered as pending rewards,
until the account interacts with the system.
Pending rewards are calculated as:

$$
\text{Pending Rewards} = \text{Account Weight} \times \left( \text{Current Reward Index} - \text{Account's Last Reward Index} \right)
$$

Rewards are accrued by accounts over time and
SHOULD be available for withdrawal at the end of each reward period.
Based on the reward duration and amount of rewards,
stakers will accrue rewards in real-time based on the rate of rewards which is calculated:

$$
\text{Reward Rate} = \frac{\text{Total Reward Amount}}{\text{Reward Duration}}
$$

- When the `rewardEndTime` period has occurred,
the operator MUST set the new reward ratio.
- account weights increase with
time, which in turn means,
the total weight of the system increases with time as well.

#### Reward Indices

The reward system uses an accounting mechanism based on indices to track and
distribute rewards accurately.
This approach ensures fair distribution even as accounts enter and
exit the system or change their stakes over time.

##### Global Reward Index

The global reward index represents the cumulative rewards per unit of weight since the system's inception.
It increases whenever new rewards are added to the system:

$$
\text{New Index} = \text{Current Index} + \frac{\text{New Rewards} \times \text{Scale Factor}}{\text{Total System Weight}}
$$

Where:

- `Scale Factor` is 1e18 (used for precision)
- `Total System Weight` is the sum of all staked tokens and MP in the system

##### Account Reward Indices

Each account maintains its own reward index,
which represents the point at which they last "claimed" rewards.
The difference between the global index and
an account's index is multiplied by the account's
weight determines their unclaimed rewards:

$$
\text{Unclaimed Rewards} = \text{Account Weight} \times (\text{Global Index} - \text{Account Index})
$$

#### Reward Index Updates

The system MUST update indices in the following situations:

- When new rewards are added by the operator
- When accounts stake or unstake tokens

This mechanism ensures that historical rewards are preserved accurately and
accounts receive their fair share based on their weight over time.
Also, accounts MUST NOT receive the rewards that were accounted for in the system
at the time the account entered the system.

##### Index Adjustment Example

For example, the system has:

- Total Weight: 1000 units
- Current Index: 0.5
- New Rewards: 100 tokens

The index would increase by:

```text
Increase = (100 × 1e18) / 1000 = 0.1e18
New Index = 0.5e18 + 0.1e18 = 0.6e18
```

If an account has:

- Weight: 200 units
- Last Index: 0.5e18

Their unclaimed rewards would be:

```text
Unclaimed = 200 × (0.6e18 - 0.5e18) / 1e18 = 20 tokens
```

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## References

- [Status Network](https://status.network/)
- [ERC-20 token](https://eips.ethereum.org/EIPS/eip-20)
