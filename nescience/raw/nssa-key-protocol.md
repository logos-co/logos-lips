--- 
title: NSSA-KEY-PROTOCOL
name: NSSA Key Protocol 
status: raw
category:
tags:
editor:
contributors:
- Filip Dimitrijevic <filip@status.im>
---

## NSSA Key Protocol Overview

This page outlines the key protocol for the Nescience State Separation Architecture (NSSA),
inspired by the Zcash and Aztec approaches.

NSSA employs multiple types of cryptographic keys to manage the lifecycle of assets,
handle private transaction visibility,
and enforce ownership and privacy across its unique execution types
(public, private, shielded, and deshielded).
Each key has a specific role,
contributing to the flexible yet secure structure of NSSA.

1. **Spending Key**: This key is responsible for generating all private keys.
The Spending Key itself is broken down into 2 components that should be kept locally:
Seed (` seed `): A high-entropy seed used to derive the Secret Spending Key.
Secret spending key (` ssk `): Generated from the seed,
this key is responsible for creating the necessary private keys for NSSA operations.

2. **Viewing Key**: Used for viewing transaction details without granting control over assets.
It allows decryption of transaction information
but doesn't compromise the user's ability to spend or modify UTXOs.
The Viewing Key pair consists of viewing secret key (` vsk `)
and viewing public key (` Vpk `) both used respectively in the private and public keys.

3. **Nullifier Key**: Manages the lifecycle of UTXOs by identifying UTXO ownership
and nullifying UTXOs once spent.
The Nullifier Key pair consists of nullifier secret key (` nsk `)
and nullifier public key (` Npk `) both used respectively in the private and public keys.

4. **Private Key**: NSSA relies on different private keys,
each with its specific role in maintaining privacy and security:
Nullifier secret key (` nsk `): Derived from the spending key,
the nullifier secret key is responsible for verifying the ownership of a UTXO
and creating the nullifier that nullifies the UTXO when it is consumed.
Viewing secret key (` vsk `): A secret key derived from the Spending Key,
used for creating the symmetric encryption key for encrypted UTXO exchanges
and for signing transactions It also decrypts the details of encrypted transactions.

5. **Public Key**: Derived from the private keys,
public keys are openly shared for verification purposes:
Nullifier Public Key (` Npk `): Derived from the nullifier secret key (` nsk `),
it is responsible for labeling UTXOs for ownership
and proving that ownership publicly without revealing the secret key.
The nullifier public key is shared publicly for verification purposes,
ensuring that the UTXO’s ownership can be verified securely.
Viewing Public Key (` Vpk `): Derived from the viewing secret key,
the receiver's `Vpk` is used to create a symmetric encryption key for UTXO exchanges
and to verify transaction signatures.
It allows viewing of transaction details (both incoming and outgoing)
without granting control over the assets.

6. **Ephemeral Key**: A temporary key used for secure communication during transactions.
This key is utilized in NSSA's key agreement protocol,
in combination with the receiver’s viewing public key,
to establish a shared secret for encrypted transaction details.

> The keys that must be kept secret typically start with lowercase letters (e.g., ` vsk `, ` nsk `),
> while public keys begin with capital letters (e.g., ` Vpk `, ` Npk `).
> This naming convention helps distinguish between private and public keys in documentation and implementation.

## Spending Key

This serves as a detailed construction of the spending key.

| **Type**               | **Name** | **Construction**               |
|------------------------|----------|--------------------------------|
| [Seed](#seed-generation-seed)              | `seed`   | **seed** = `CSPRNG(𝔽ₚ)`        |
| [Secret spending key](#secret-spending-key-generation-ssk) | `ssk`    | **ssk** = `Hash(seed)`         |

The *spending key* serves as the root of all private key generation.  
The construction of the spending key is based on cryptographic principles,  
using a seed to generate the secret spending key (`ssk`).

## Mathematical requirements for spending key construction

Finite field $\mathbb {F}_{p}$ contains all elements used for scalar values,
including the seed,secret spending key,
and any other derived keys.
This field consistent with the elliptic curve secp256k1 where $p=2^{256}-2^{32}-977$

Elliptic curve secp256k1 defines the group used for public key generation
and other cryptographic operations.
This curve is chosen due to its well-established security properties
and wide adoption in blockchain cryptography.

A cryptographic secure pseudo-random number generator ( CSPRNG ),
used to generate the seed securing source of randomness
to prevent any possibility of predictability or bias.
The CSPRNG ensures that the seed is chosen randomly from the field $\mathbb {F}_{p}$
providing high entropy and unpredictability.

A cryptographic hash function used to derive the secret spending key from the seed.
SHA256 will be used, it takes seed in input and outputs a hashed binary string
that will be converted into a field element: Hash(seed) $\rightarrow \mathbb {F}_{p}$

## Seed generation (` seed `)

The seed is the master secret from which the secret spending key ( ssk ) is derived.
It is a randomly selected field element from the group $\left(\mathbb {F}_{p}\right)$,
ensuring that it has sufficient entropy and security to be unpredictable.

$$\text {seed}=\text {CSPRNG}\left(\mathbb {F}_{p}\right)$$

## Secret spending key generation (` ssk `)

The secret spending key ( ssk ) is derived from the seed using a hash function.
This key is a scalar in the same finite field as the elliptic curve ( secp256k1 ).
$\left(\mathbb {F}_{p}\right)$
The purpose of the ssk is to generate the various private keys needed for
transaction signing, encryption, and key derivation in NSSA.

The secret spending key is computed as follows:

$$\mathrm {ssk}=\mathrm {Hash}(\text {seed})$$

> ℹ️ **Note:** After generating the hash of the `seed`, the result must be converted into a scalar value within the field ℱₚ.  
> This ensures the secret spending key (`ssk`) is a valid element in the finite field used for elliptic curve operations.
>
> - `**to_repr(binary_string)** → ℱₚ`: converts a binary string into its scalar representation.
> - `**ssk = from_repr(Hash(seed))**`: converts a binary string into a field element in ℱₚ.

## Potential improvements in terms of implementation

- HD key structure: BIP32/42 where the spending key acts as a master seed
from which all other keys are derived using deterministic paths.

- Multi-signature support: multiple keys to authorize transactions (threshold signatures: Schnorr, BLS).

- Shamir's secret sharing: split the master seed into multiple parts that require a threshold number to recover.

- Key derivation functions (KDF): HKDF with SHA-256.

## Private Keys

This serves as a detailed construction of the private keys.

| [Nullifier secret key](#nullifier-secret-key-generation-nsk)  | nsk  | $\mathrm {nsk}=\text {Hash}(\mathrm {ssk},\mathrm {const}1)$ |
| --- | --- | --- |
| [Viewing secret key](#viewing-secret-key-generation-vsk)  | vsk  | $\mathrm {vsk}=\text {Hash}(\mathrm {ssk},\mathrm {const}2)$ |

The private keys are used for managing UTXOs and ensuring secure, anonymous transactions.
Each private key serves a distinct purpose,
and all are derived from the secret spending key ( ssk )
using the constants the secret spending key ( ssk )
using the constants () and ( )const1const2( ).

### Mathematical requirements for private keys construction

- The *constants* (`const1`) and (`const2`) are predefined field elements within (ℱₚ),  
  used to differentiate the *nullifier secret key* (`nsk`) and *viewing secret key* (`vsk`)  
  from the *spending secret key* (`ssk`). These constants help prevent key collisions and  
  ensure distinct cryptographic roles for each key.

  ◦ `const1` is used for generating the nullifier secret key.  
  ◦ `const2` is used for generating the viewing secret key.

### Nullifier secret key generation (`nsk`)

The *nullifier secret key* (`nsk`) allows a user to prove ownership of a UTXO without signing it directly,  
providing an essential element for creating nullifiers when UTXOs are spent.  
It is a field element in ℱₚ, and is derived from the *spending secret key* (`ssk`) and `const1`.

```text
nsk = Hash(ssk, const1) ∈ ℱₚ
```

> ℹ️ **Note:** The following process ensures that `nsk` is distinct from `ssk`:
>
> 1. Convert the `ssk` into its binary representation:  
>    *t₀ = to_repr(ssk)*
>
> 2. Hash the constant `0x01` (the integer 1 in hexadecimal form)  
>    concatenated with *t₀* using **SHA-256**:  
>    *t₁ = SHA256(t₀, 0x01)*
>
> 3. Convert the resulting binary string back into a field element in ℱₚ:  
>    ***nsk = from_repr(t₁)***

### Viewing secret key generation (` vsk `)

The *viewing secret key* (`vsk`) is responsible for enabling the creation of temporary secret shares used in the encryption of UTXO exchanges.  
It also allows the user to sign transactions while maintaining the privacy of the transaction details.  
It is a field element in ℱₚ, and is derived from the *spending secret key* (`ssk`) and `const2`.

```text
vsk = Hash(ssk, const2) ∈ ℱₚ
```

> ℹ️ **Note:** The following process ensures that `vsk` is distinct from `ssk`:
>
> 1. Convert the `ssk` into its binary representation:  
>    *t₀ = to*repr(ssk)*
>
> 2. Hash the constant `0x02` (the integer 2 in hexadecimal form)  
>    concatenated with *t₀* using **SHA-256**:  
>    *t₁ = SHA256(t₀, 0x02)*
>
> 3. Convert the resulting binary string back into a field element in ℱₚ:  
>    ***vsk = from*repr(t₁)***

## Public Keys

This serves as a detailed construction of the public keys.

| **Type**               | **Name** | **Construction**          |
|------------------------|----------|---------------------------|
| [Nullifier public key](#nullifier-public-key-npk) | `Npk`    | **Npk** = *nsk* · **G**     |
| [Viewing public key](#viewing-public-key-vpk)   | `Vpk`    | **Vpk** = *vsk* · **G**     |

The public keys are derived from their corresponding private keys and serve for verification and ownership proofs.  
These keys do not expose sensitive information and allow others to verify transaction validity.

---

### Mathematical requirements for public keys construction

- The *generator* (**G**) is a fixed point on the elliptic curve `secp256k1`,  
  used for scalar multiplication to generate public keys from their corresponding private keys.

- To derive public keys from private keys, *scalar multiplication* is used.  
  This operation involves multiplying the private key (a scalar) by the generator point (**G**) on the elliptic curve.

### Nullifier public key (` Npk `)

The *nullifier public key* (` Npk `) is responsible for labeling UTXOs to prove ownership without exposing sensitive information.  
It is derived from `nsk` using scalar multiplication of `nsk` by the elliptic curve generator (**G**).

```text
Npk = nsk · G
```

> ℹ️ `secp256k1` function implementation:  
> **Npk = mul_by_generator(nsk)**
>
> This construction ensures that the `Npk` is securely tied to the ownership of UTXOs  
> and can be used to prove the validity of transactions.

### Viewing public key (`Vpk`)

The *viewing public key* (`Vpk`) enables secure encryption for UTXO exchanges and  
allows for transaction verification by third parties.  
It is derived from the `vsk` using scalar multiplication of `vsk` by the elliptic curve generator (**G**).

```text
Vpk = vsk · G
```

> ℹ️ `secp256k1` function implementation:  
> **Vpk = mul_by_generator(vsk)**
>
> This construction ensures that the `Vpk` is securely linked to `vsk`  
> and can be used to facilitate encrypted communication and signature verification in transactions.

### Potential improvements in terms of public keys implementation

- Combine multiple public keys into a single signature for multi-signature transactions,  
  which could reduce the data size and improve verification efficiency.

- Rotate public keys to prevent their reuse in multiple transactions,  
  which can link transactions and reduce privacy (similar to Bitcoin’s approach  
  of generating new addresses, thus reducing linkability).

- Explore protocols like linkable ring signatures or stealth addresses to enhance privacy  
  (prove that users own a public key without revealing which specific public key is theirs —  
  into shielded or deshielded transactions).

## Ephemeral Keys

This serves as a detailed construction of the ephemeral keys.

| **Type**                   | **Name** | **Construction**           |
|----------------------------|----------|----------------------------|
| [Ephemeral secret key](#ephemeral-secret-key-esk) | `esk`    | **esk** = `CSPRNG(ℱₚ)`     |
| [Ephemeral public key](#ephemeral-public-key-epk) | `Epk`    | **Epk** = `esk · G`        |

The *ephemeral keys* are temporary cryptographic keys used for secure communication  
between sender and receiver in transactions. These keys are not reused,  
making them highly resistant to replay attacks and ensuring the privacy of individual transactions.  
They consist of a private portion (`esk`) and a public portion (`Epk`).

---

### Ephemeral secret key (` esk `)

The *ephemeral secret key* (` esk `) is a temporary key used by the sender to generate a shared secret  
in the key agreement protocol. The shared secret allows the encryption of transaction details  
that only the sender and receiver can decrypt.  
It is generated randomly from the finite field (ℱₚ) using a `CSPRNG`.

```text
esk = CSPRNG(ℱₚ)
```

### Ephemeral public key (` Epk `)

The ephemeral public key (` Epk `) is derived from esk
and is used by the receiver to generate the shared secret in the key agreement protocol.
It enables the secure exchange of encrypted transaction details.
It is derived using scalar multiplication of esk by the elliptic curve generator (G).

```text
Epk = esk  · G
```

> ℹ️ `secp256k1` function implementation:  
> **Epk = mul_by_generator(esk)**
>
> This construction ensures that the `Epk` is securely linked to `esk`  
> and can be used for secure transaction communication.
> ⚠️ The public portion of the ephemeral public key (`Epk`) is shared with the receiver,  
> usually as part of the transaction message. The receiver uses their viewing secret key (`vsk`)  
> and the ephemeral public key (`Epk`) to derive the shared secret for decrypting the transaction data.

### Potential improvements in terms of ephemeral Keys implementation

- Automatic key rotation for long transactions to limit the exposure of any single ephemeral key,
adding another layer of security.

- In shielded transactions, ephemeral keys must securely manage encryption
while ensuring transaction privacy.

- In deshielded transactions, ephemeral keys must still protect private data during selective disclosure.

- The ephemeral key should seamlessly integrate with the zkVM’s ZKP generation
and validation processes, ensuring secure
and private communication between the virtual machine and the network.

## Viewing Keys

This serves as a list of indication for the viewing keys.

The viewing key in NSSA allow users to access transaction details
without compromising their ability to control assets or exposing their private keys.
It enables users or authorized third parties to decrypt UTXO data
and monitor both incoming and outgoing UTXO exchanges without granting control over the assets.

The viewing key is designed to allow users to view encrypted UTXO details,
such as the amount, memory slot,
and owner of the UTXO. Importantly,
it preserves the unlinkability of UTXO exchanges in shielded, deshielded,
and private executions,ensuring that sensitive information,
such as the source or destination of funds, remains hidden from unauthorized parties.

In some cases, users can share their viewing key with trusted third parties,
allowing them to verify transaction validity without granting them control over the funds.

## Functions of the viewing key

- Decrypting UTXO details: The viewing key allows users to decrypt exchanged UTXO data
without revealing the spending key or sensitive details of the UTXO.
This function is particularly useful for monitoring private and shielded transactions,
enabling users to see details like amounts
and the other parties involved without exposing these details to the network or untrusted third parties.

- Visibility without control: The viewing key provides visibility into transaction history
without granting control over the funds.
This ensures that even if the viewing key is compromised,
an attacker cannot move funds or alter transaction data.
Users can share viewing keys with external entities, such as auditors,
who need to verify transactions without compromising the user's control over their assets.

- Private and shielded transactions: The viewing key allows users to decrypt the details of private transactions
that are otherwise hidden from the network.
In shielded transactions,
the viewing key decrypts transaction outputs without revealing sensitive information,
such as transaction amounts or recipient identities.

- Transaction history review: The viewing key can be used to monitor the transaction history,
both incoming and outgoing.
This enables users to track transaction flows, verify successful transfers, or review transaction records
without exposing sensitive information to unauthorized parties.

### Considerations for the viewing key in NSSA

- The viewing key should be kept separate from the spending key and other private keys (e.g., `nsk` , `ssk` ),
meaning that it does not enable control of funds.
This separation ensures that even if the viewing key is exposed,
it cannot be used for unauthorized transactions.

- Implementing an ephemeral viewing key could provide temporary access to transaction details.
This ensures that the viewing key can be revoked after a predefined period or number of transactions,
reducing the risk of long-term exposure.

- Users could be given the option to selectively disclose transaction details via the viewing key.
For instance, a user may choose to reveal only the transaction amount without exposing the recipient’s address. This could be implemented through partial disclosure,
where users configure the viewing key to reveal specific aspects of transaction data based on their preferences.

- Time-sensitive viewing keys could be generated to expire after a certain period,
ensuring that third-party access to transaction data is temporary
and does not persist indefinitely.

- Users should have full control over who can access their viewing key and what data they can view,
ensuring that sensitive information is only shared under the user's terms.

## Address Generation

This serves as a generation of the NSSA address.

Once a user’s public keys are generated, the user’s public address (`addr`)  
can then be computed:

```text
Addr = SHA256(Npk, Vpk)
```

> ⚠️ Although the address is not currently used for any transactions or key exchanges,  
> it can potentially be utilised in the future to explore transactions more efficiently using a block explorer.

### How Keys Are Used

This page outlines the usage of keys in NSSA.

In NSSA, cryptographic keys play a fundamental role in ensuring security, privacy,
and confidentiality of transactions.
To better understand how these keys interact in different types of transactions,
we will break down their usage into specific contexts: key agreement, full protocol for UTXO exchange,
private execution, and shielded execution.

## Key Agreement

This is to show an example of key agreement for creating shared secrets between two parties in NSSA,
used for secure encryption of transaction details.

A key agreement scheme is an algorithm that allows two parties to securely generate the same shared secret.
This shared secret is then used for symmetric encryption,
ensuring that the data exchanged between the parties remains confidential.
NSSA uses the [Elliptic Curve Integrated Encryption Scheme](https://cryptobook.nakov.com/asymmetric-key-ciphers/ecies-public-key-encryption) (ECIES)for key agreement,
which allows both the sender and receiver of a transaction
to independently generate the same shared secret
using their respective public and private keys.

The idea behind key agreement is simple: each party generates their public key
by multiplying a private key with a known generator.
By exchanging these public keys,
both parties can compute the same shared secret,
which is used for encrypting and decrypting transaction data.
The secret is never directly exchanged between parties,
ensuring its confidentiality.

### Example of key agreement

#### Elliptic curve group setup

Let **G** be a generator for the group **G** used in elliptic curve cryptography.  
Suppose Alice has her private key *a*, and her corresponding public key is  
**A = a · G**.
Similarly, Bob has his private key *b*, and his corresponding public key is  
**B = b · G**.

When Alice and Bob exchange their public keys, they can both generate the same shared secret **S**:

```text
S = b · A = a · B = ab · G
```

> Neither Alice nor Bob directly knows the product of their private keys ( $(ab)$ ),
> but they can both calculate the shared secret, which is .S $S$

### Application in NSSA

In NSSA, key agreement is used during transactions to ensure that
the senderand recipient can privately exchange data.
The sender uses their ephemeral secret key (` esk `)
and the recipient’s viewing public key (` Vpk `) to generate a shared secret (` ss `).
The recipient uses their own viewing secret key (` vsk `)
and the sender’s ephemeral public key (` Epk `) to generate the same shared secret.

Once the shared secret is established,
the transaction data can be encrypted by the sender
and later decrypted by the recipient.

### Sender’s key agreement process

The sender uses their esk and the recipient’s Vpk to generate the shared secret.
This is done using scalar multiplication,
as provided by the secp256k1 curve implementation:

$$\mathrm {ss}=\text {mul}\left(\mathrm {Vpk}_{\text {recipient}},\mathrm {esk}\right)$$

Here, the recipient’s viewing public key $\mathrm {Vpk}_{\text {recipient}}$
is multiplied by the sender’s ephemeral secret key esk
to generate the shared secret `ss`.

### Recipient’s key agreement process

On the recipient's side, they use their vsk and the sender’s Epk to generate the same shared secret.
The process is identical,
with the recipient performing the following calculation:

$$\mathrm {ss}=\text {mul}\left(\mathrm {Epk}_{\text {sender}},\mathrm {vsk}\right)$$

Here, the sender’s ephemeral public key $\mathrm {Epk}_{\text {sender}}$
is multiplied by the recipient’s viewing secret key vsk to derive the shared secret `ss`.

### Key agreement in action

Once the shared secret is established,
the sender can securely encrypt the transaction using the shared secret,
ensuring that only the intended recipient can decrypt and access the transaction details.
The recipient, having generated the same shared secret,
can decrypt the transaction data without having direct access to the sender’s private keys.

This secure key agreement ensures privacy during transactions,
especially in shielded and private executions,
where transaction details must remain confidential.

In the next section,
we will expand this key agreement mechanism into the [Full Protocol for UTXO Exchange](#full-protocol-for-the-utxo-exchange),
illustrating how the key agreement integrates into the broader transaction workflow in NSSA.

## Full Protocol for the UTXO Exchange

This is to show how keys are used in a full protocol for UTXO exchange

In NSSA, the full protocol for UTXO exchange ensures the private
and shielded transfer of assets between a sender and a receiver.
This section explains how the protocol works,
assuming that the sender already possesses the recipient’s viewing public key (` Vpk `).

The UTXO exchange protocol leverages key agreement to establish a shared secret,
which is used to encrypt the transaction data,
ensuring that only the intended recipient can decrypt it.
Below are the detailed steps for both the sender
and receiver during the UTXO exchange process.

## Sender’s steps

1. Generate ephemeral secret key ( esk ): The sender generates a random esk $\mathbb {F}_{p}$ from the elliptic curve field.
This key is used to establish secure communication with the receiver for this specific transaction.

2. Generate ephemeral public key ( Epk ): Using the esk,
the sender calculates the corresponding Epk by multiplying the ephemeral secret key with the elliptic curve generator G.
This public key will be shared with the receiver: $Epk=$ $esk·G$ .

3. Calculate shared secret ( ss ): The sender uses their esk and the recipient’s Vpk to calculate ss through scalar multiplication.
This shared secret will be used to encrypt the transaction data: $\mathrm {ss}=\text {mul}\left(\mathrm {Vpk}_{\text {recipient}},\mathrm {esk}\right)$.

4. Encrypt the output UTXO: The output UTXO,
which contains transaction data such as the amount and ownership information,
is encrypted using the shared secret ss.
This ensures that only the recipient can decrypt and view the transaction details.

5. Broadcast the encrypted message and Epk: The sender broadcasts the encrypted message,
which includes the ciphertext of the output UTXO and the ephemeral public key ( Epk ).
This ensures that anyone on the network can receive the message,
but only the intended recipient will be able to decrypt it.

## Receiver’s steps

1. Download ciphertext and Epk: The receiver listens to the network
and downloads the broadcasted ciphertext and the ephemeral public key ( Epk )from the sender.

2. Calculate shared secret ( ss ): Using their vsk and the sender’s Epk,
the receiver calculates the same shared secret ( ss ) through scalar multiplication.
This allows the receiver to decrypt the message: $\mathrm {ss}=\mathrm {mul}\left(\mathrm {Epk}_{\text {sender}},\mathrm {vsk}\right).$

3. Decrypt the ciphertext: The receiver attempts to decrypt the ciphertext using the shared secret ( ss ).
If the shared secret matches the one used by the sender,
the decryption succeeds, allowing the receiver to view the details of the UTXO,
such as the amount and ownership.
If successful, the transaction is completed.

This protocol ensures that UTXO exchanges between sender and receiver remain private,
with transaction details securely encrypted during transfer.
The use of ephemeral keys for each transaction enhances security
and reduces the risk of key compromise.

Next, we will explore how these keys interact in private executions.

## Private Execution

This is to show how keys are used in a private execution.

In a private execution, both the spending of input UTXOs and the creation of new output UTXOs
are kept confidential between the sender and receiver.
The sender only needs to know the receiver's address (` addr `)
and corresponding public keys (` Npk ` and ` Vpk `).
The core purpose of private execution is to ensure that the transaction is private,
with the input UTXOs being spent and the output UTXOs being created
without revealing sensitive information to the rest of the network.

### Steps of private execution

1. Determination of input and output UTXOs: The sender determines the input and output UTXOs
based on the rules set by the Nescience application.
These UTXOs represent the assets or data being transferred in the private transaction.

1. Attaching the receivers public key: The sender attaches the hash of the receiver’s nullifier public key (` Npk `) to the output UTXOs.
This step is crucial as it ensures that only the recipient (the owner of ` Npk `) can spend the output UTXO,
thus preventing unauthorized access.

1. Calling the zkVM and initializing the private kernel circuit:  
   The sender calls the zkVM and initiates the private kernel circuits to generate a proof.  
   This proof ensures that:

   - Each input UTXO has a valid commitment in the commitment tree (membership proof).
   - Each input UTXO has not been spent before (non-membership proof),  
     meaning its nullifier is absent from the nullifier tree.
   - A nullifier is created for each input UTXO as follows:  
     $\mathrm{UTXO}_{\text{nullifier}} = \text{Poseidon}(\mathrm{UTXO}_{\text{commitment}}, \text{Npk})$
   - Commitments for the output UTXOs are generated and appended to the commitment tree.
   - Ownership of the input UTXOs is proven by passing the sender’s `nsk` to the kernel circuit.  
     The kernel circuit computes the sender’s `Npk` and verifies the input UTXO’s nullifier.
   - If the nullifier doesn’t match the one previously appended, the circuit aborts the transaction.  
     If it matches, the circuit proceeds to produce a proof.

1. Exchanging UTXOs with the receiver:  
   The sender securely exchanges the output UTXOs with the receiver  
   by encrypting them with the receiver's `Vpk`.

1. Sending proof to sequencer:  
   Once the proof is generated by the kernel circuit,  
   the sender submits it to the sequencer along with the necessary public inputs.  
   The sequencer verifies the proof and, upon successful verification,  
   updates both the commitment tree and the nullifier tree.  
   This marks the end of the execution.

### Role of nullifier keys in private execution

- The nullifier secret key (` nsk `) plays a crucial role in proving ownership of the input UTXOs.
It allows the sender to create valid nullifiers for the UTXOs they want to spend.

- The nullifier public key (` Npk `), on the other hand,
is used to prove ownership to the network and ensure that only the rightful owner can spend the UTXO.

The nullifier prevents double-spending by ensuring that once a UTXO is spent,
its nullifier is recorded in the nullifier tree,
making any further attempts to spend the same UTXO invalid.

### Conclusion

In private execution, the combination of membership and non-membership proofs,nullifier creation,
and key exchanges ensures that transactions remain private and secure.
The use of zkVM circuits guarantees that no sensitive information (like addresses or amounts) is revealed,
while still allowing the transaction to be verified and executed properly.
This ensures that private UTXOs are exchanged securely and privately within NSSA.

Next, we will explore how these keys interact in shielded executions.

## Shielded Execution

This is to show how keys are used in a shielded execution.

In shielded executions, the public state is modified by running a transaction on the public VM,
while the output is used to create a private UTXO for the receiver.
The sender and receiver's respective key materials are used to facilitate the secure transfer of assets.
Here’s a breakdown of the shielded execution process,
which enables private UTXO creation without revealing sensitive information on the public chain.

### Steps of shielded execution

1. Call the public VM and execute the Nescience application: The sender interacts with a Nescience application,
executing its source code on the public VM.
The execution is directed toward a special locked address (similar to burning an asset).

- To validate this transaction, the sender signs the transaction with their ` vsk `.
- Once signed, the sender keeps the transaction to submit it to the sequencer later on.

1. Create the output UTXO: The sender then constructs the UTXO that will belong to the receiver on the private side:

- The balance slot is filled according to the rules specified by the Nescience application.
- The owner of the UTXO is set to the receiver’s Npk,
ensuring that only the recipient will be able to spend the UTXO in the future.

1. Generate proofs using zkVM: The sender calls the zkVM to generate cryptographic proofs that prove the following:

- Balance verification: The proof verifies that the balances in the public transaction match those of the UTXO being created.
- Commitment generation: The UTXO is committed using the Pedersen hash to ensure that its details remain private.

1. Submit the public transaction and proofs to the sequencer: The sender submits both the public transaction
and the generated proofs, including the public inputs, to the sequencer.
This submission also includes the commitment of the

1. Exchange UTXOs between sender and receiver: In parallel,
the sender UTXO that was created in the private state.exchanges the UTXO with the receiver,
following the full protocol for the UTXO exchange described earlier.

1. Sequencer processing: Once the sequencer receives the public transaction and proofs,
it proceeds as follows:

- Re-run the public transaction: The sequencer re-executes the public transaction using the provided inputs
and verifies that the output matches the expected result.
It then updates the public state according to the address provided.
- Verify proofs and update the commitment tree The sequencer verifies the cryptographic proofs against their public inputs
and updates the commitment UTXO tree with the new private UTXO.

### Shielded executions conclusion

In shielded executions, the sender operates on the public state but creates a private UTXO for the recipient.
The process utilizes both the public VM and the zkVM to ensure privacy
while maintaining the integrity of the public state.
The same key materials used for public executions are also used for shielded executions.
The proofs generated by the zkVM ensure that all balances and commitments are correct,
and the sequencer verifies the transaction before updating the public and private states.

The deshielded execution can be constructed in a similar manner,
allowing private UTXOs to be revealed back to the public state when necessary.

> ⚠️ The sequencer and other public entities can identify that this is a shielded execution (SE),  
> but they cannot link the encrypted message to any other transaction,  
> even when the UTXO is spent and nullified.  
> The public state is aware that changes have occurred, but it has no insight into the nature of those changes.  
> It's possible that the execution might simply involve sending tokens to a diversified or secondary address  
> belonging to the same user, without revealing further details.

## References

- EKey Agreement: [Elliptic Curve Integrated Encryption Scheme](https://cryptobook.nakov.com/asymmetric-key-ciphers/ecies-public-key-encryption)

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
