# [RFC] Wallet: Hierarchical key management for one-time keys

**Motivation and proposal:** [PR #452](https://github.com/logos-co/logos-lips/pull/452)

## Change log

| **Revision** | **Description** | **Date** |
| --- | --- | --- |
| v1 | Initial RFC | 2026-09-14 |

## Reviewer Orientation

Stacked on #437 (Wallet Technical Standard 1.1.0, constants fix). Everything normative is in the Wallet Technical Standard; the Anonymous Leaders Reward Protocol only gains a pointer to it.

| # | Priority | Document / Change | What to look for |
| --- | --- | --- | --- |
| 1 | High | **Start here** — Wallet → [Key Hierarchy](#1-key-hierarchy) | the fixed path and role table; once implemented this cannot change |
| 2 | High | **Start here** — Wallet → [Voucher Secret Derivation](#3-voucher-secret-derivation) | `voucher_secret = zkhash("VOUCHER_SECRET_V1", vm, i)` in hash mode; `voucher_cm`, `voucher_nf` and the Proof of Claim are untouched |
| 3 | High | Wallet → [Wallet Recovery](#4-wallet-recovery) | `GAP_LIMIT = 20`; spent notes count as used, so the scan covers the chain history, not the UTXO set |
| 4 | Medium | Wallet → [One-Time Note Keys](#2-one-time-note-keys) | the MUST rules for receive and change leaves; what one-time keys do not hide |
| 5 | Medium | Wallet → [Test Vectors](#5-test-vectors) | recompute independently: BIP-39 `abandon…about` seed, BLAKE2b with `Logos_MasterKGen` / `Logos_ExpandSeed`, Poseidon2 via the reference crate; field elements are little-endian bytes |
| 6 | Low | Anonymous Leaders Reward → [Voucher creation, step 1](#6-anonymous-leaders-reward-protocol-voucher-creation) | "random or derived per Wallet Technical Standard"; a voucher secret is never reused |

# Discussion

## Hardened-only keys

`pk = zkhash(KDF, sk)` has no homomorphism, so there are no non-hardened children, no extended public key that derives anything, no diversified addresses and no viewing key. One-time keys are therefore hardened leaves, and recovery is a derive-and-look-up scan, which only works if every wallet scans the same way. The upside is that a leaked leaf exposes one note, never the account.

## Path layout

`154'` is the spec slug, following BIP-43's "purpose = the standard's number". There is no `coin_type` level: its BIP-44 job is to keep one tree from producing the same key on two chains, and this tree is already personalized with `Logos_ExpandSeed` and `Logos_MasterKGen`. Roles `3'` and above are reserved so that node identity keys (`zk_id`, `provider_id`, swarm key) can be added later without breaking the layout. They are operator-side keys with their own custody and rotation needs, so whether they belong in the wallet tree is a decision for the Blend and SDP owners.

## Vouchers: master plus counter, not one leaf per voucher

The node needs a voucher at every block it proposes and its key management holds field elements, not byte trees. Keeping the derivation inside Poseidon2 matches the current implementation (one added DST), keeps the counter unbounded, and lets `vm` alone be handed to a hot node: its compromise costs unclaimed rewards and nothing else. Consensus is unchanged; only where the secret comes from becomes normative.

## Recovery

`GAP_LIMIT = 20` matches BIP-44. The history-scan rule is specific to a UTXO ledger: a spent note leaves the current set, so scanning unspent notes only would misplace the gap after a spend-and-idle period and hide later funds. The wallet service already indexes notes by public key and sees every block, so this costs an "ever seen" index, not a new data path. Vouchers are simpler because the commitment MMR is append-only. Wallets may persist their indices to skip the scan, but must still be able to recover from the seed alone.

## What one-time keys do not give

Unlinkability of received notes across time, nothing more. The transaction graph stays public. The specification says so to keep wallets from advertising privacy Mantle does not have.

## Forward compatibility

#442 adds a second, STARK-field key to every leaf; the tree, the roles and the counters are untouched. The specification is therefore written per leaf, not per key: a fresh leaf is a fresh set of keys, and recovery marks a leaf as used when any of its public keys appears on chain. What #442 adds on top (a second voucher master, the legacy voucher set after the transition) is left to #442 and the transition work.

## Backwards compatibility

No shipped wallet implements HD derivation. The voucher change alters neither `voucher_cm`, `voucher_nf` nor any circuit, but vouchers issued with the old derivation are not recoverable from the mnemonic, so nodes switch before rewards carry value or claim first. Node configuration (`known_keys`, `voucher_master_key_id`) needs a migration to accounts, tracked in Implementation.

# Details

All changes are additions to the Wallet Technical Standard unless stated otherwise. The specification text is the reference; the snippets show the normative core of each section.

### 1. Key Hierarchy

New section. The path is fixed, all levels hardened:

```text
m / 154' / account' / role' / index'
```

`154'` is the purpose (the slug of this specification, BIP-43 convention). Wallets MUST support account `0'` and MAY expose more. Roles:

| `role` | Name | Leaf usage | One-time |
| --- | --- | --- | --- |
| `0'` | Receive | one leaf, hence one set of note keys, per received note | yes |
| `1'` | Change | one leaf, hence one set of note keys, per change note | yes |
| `2'` | Voucher | the voucher master of the account; this role has no `index'` level | n/a |
| `3'` – `(2^{31}-1)'` | Reserved | future roles (e.g. node identity keys); wallets MUST NOT derive keys under them | |

### 2. One-Time Note Keys

New section. A wallet MUST use a fresh receive leaf (the next unused `index'` under `0'`) for every payment request it hands out, and MAY reuse a leaf whose public key was published but never received a note. A wallet MUST use a fresh change leaf (next unused `index'` under `1'`) for every change output and MUST NOT send change back to the public key of a consumed input by default. The section states what one-time keys do not hide (the transaction graph).

### 3. Voucher Secret Derivation

New section. The voucher leaf is `m / 154' / account' / 2'`; the voucher master `vm` is its `ZkSecretKey`. The `i`-th voucher secret is:

```python
def voucher_secret(vm: ZkSecretKey, i: int) -> Fr:  # i is a uint64
    return zkhash(
        FiniteField(b"VOUCHER_SECRET_V1", byte_order="little", modulus=p),
        vm,
        FiniteField(i, byte_order="little", modulus=p),
    )  # Poseidon2 hash mode
```

A wallet MUST keep a counter `next_voucher_index` per account, use `voucher_secret(vm, next_voucher_index)` for the next block it proposes and increment the counter before the block is released. A voucher secret MUST NOT be reused. `voucher_cm`, `voucher_nf` and the Proof of Claim are unchanged.

### 4. Wallet Recovery

New section. `GAP_LIMIT = 20`.

- **Note keys.** For each of roles `0'` and `1'`, derive leaves `0', 1', 2', …`; a leaf is *used* if any of its public keys appears in any `Note` ever created on chain, even if the note's other keys are not the leaf's. Stop after `GAP_LIMIT` consecutive unused leaves. The lookup MUST cover chain history, not only the current unspent set. Wallets MAY scan further on user request but MUST NOT stop earlier.
- **Vouchers.** Derive `voucher_secret(vm, i)` and `voucher_cm` for `i = 0, 1, 2, …`; a voucher is *issued* if its commitment is in the (append-only) voucher commitment set, and *claimed* if its nullifier is in the nullifier set. Stop after `GAP_LIMIT` consecutive unissued indices. Vouchers of the current epoch are not yet in the set, so a recovering wallet that also produces blocks MUST account for the vouchers it issued since the last epoch boundary.
- **Accounts.** Recover account 0; recover account `a + 1` only if account `a` has at least one used leaf or issued voucher.

### 5. Test Vectors

New section: seed (BIP-39 `abandon … about`, empty passphrase), master key, three note leaves (`m/154'/0'/0'/0'`, `m/154'/0'/0'/1'`, `m/154'/0'/1'/0'`) with `k`, `c`, `k_logos`, `public_key`, the voucher master and vouchers 0 and 1 with `voucher_cm` / `voucher_nf`, and the five DSTs as little-endian field elements. Produced with Python `hashlib` (BLAKE2b, PBKDF2) and the `logos-blockchain-poseidon2` crate; the tool reproduces the Poseidon2 values of the Common Cryptographic Components annex and an existing node `sk → pk` pair.

### 6. Anonymous Leaders Reward Protocol, voucher creation

Step 1 of voucher creation no longer requires a random secret:

```diff
-1. Generate a one-time random secret voucher <-$- F_p.
+1. Obtain a one-time secret voucher in F_p, either drawn uniformly at random or derived from the
+   wallet seed as specified in the Wallet Technical Standard, which makes it recoverable.
+   A voucher secret MUST NOT be used for more than one block.
```

## Chores

- Anonymous Leaders Reward Protocol: `$`r < n`$` → `$`r \lt n`$` so the rendering validator passes on the touched file.
- Wallet Technical Standard tags and revision history (1.1.0 → 1.2.0); Anonymous Leaders Reward Protocol revision history (1.1.0 → 1.1.1).
- `scripts/validate_metadata.py`: exclude `rfc/` from the metadata-table check so RFC documents can live beside the specs, the same one-line change as #448.

# Implementation

Integration into the node in the order agreed with the wallet implementer (each step is usable on its own):

- [ ] Derive every ZK key in `user_config.yaml` from one mnemonic: BIP-39 seed → `Logos_MasterKGen` → hardened `CDKpriv` along `m / 154' / account' / role' / index'` → `WALLET_ZK_SK_V1` leaf compression. Keep old static keys as imported keys during migration.
- [ ] Rotate keys: the wallet picks the next unused change leaf instead of a caller-supplied `change_pk` and hands out a fresh receive leaf per payment request. First version persists `next_index` per role in the node state.
- [ ] Recovery from the seed alone: history scan with `GAP_LIMIT = 20` for roles `0'`/`1'` (needs an "ever seen" public key index, not only the UTXO set), voucher scan over the commitment MMR and nullifier set. Persisted indices become a shortcut, not a requirement.
- [ ] Vouchers last: replace `UnsafeVoucherOperator` (`zkhash(master, index)`) with `zkhash(VOUCHER_SECRET_V1, vm, index)`, `vm` from role `2'`. Vouchers issued with the old derivation are not recoverable from the mnemonic, so switch before rewards carry value or claim them all first.
- [ ] Add the specification's test vectors as implementation tests.
- [ ] Verify the implementation matches this specification.

# Affected Specifications

| Specification | Status | Note |
| --- | --- | --- |
| [Wallet Technical Standard](../wallet-technical-standard.md) | Modified | 1.1.0 → 1.2.0; all normative additions |
| [Anonymous Leaders Reward Protocol](../bedrock-anonymous-leaders-reward.md) | Modified | 1.1.0 → 1.1.1; voucher secret origin, reuse prohibition |
