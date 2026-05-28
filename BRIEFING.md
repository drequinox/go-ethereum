# THORChain Asgard Vault Compromise — Technical Briefing

**Incident date:** 15 May 2026
**Loss:** ~$10.7M–$10.8M (1 of 6 Asgard vaults)
**Attack class:** TSSHOCK-family vulnerability in the GG20 threshold signature scheme
**Status:** Network halted via Mimir governance; remaining 5 vaults structurally exposed pending TSS protocol migration

This briefing answers four questions: what happened, how it happened at the cryptographic level, what the root cause was, and what mitigations prevent recurrence. It is paired with a runnable proof-of-concept (`thorchain_poc.py`) that reproduces the cryptographic primitive end-to-end in ~15 seconds.

---

## 1. What happened

On 15 May 2026, a node operator that had joined the THORChain network days earlier drained roughly $10.7 million from one of THORChain's six Asgard vaults across Bitcoin, Ethereum, BNB Chain, and Base. The drain occurred through legitimate-looking `transferOut` calls signed with the vault's real ECDSA key — no smart contract was exploited, no signature was forged.

Per THORChain's published exploit report (ADR-028) and a converging set of independent analyses from Ledger, PeckShield, and Cyvers, the attacker recovered the full private key of an Asgard vault by participating as a legitimate member of the TSS committee that controls that vault. The cryptographic protocol that distributes vault keys across 18 nodes — and is supposed to prevent any single node from ever holding the full key — failed at the implementation layer. The other 17 honest nodes saw a normal-looking key-generation ceremony followed by normal-looking signing operations. The attacker, working alone, reconstructed the master vault key offline.

Key incident facts from primary sources:

- **Attacker node:** `thor16ucjv3v695mq283me7esh0wdhajjalengcn84q`. Joined the active validator set on 13 May 2026.
- **Loss composition:** ~36.75 BTC (~$3M) on Bitcoin; ~$7M in tokens across Ethereum, BNB Chain, Base. PeckShield's estimate was ~$10M; THORChain's own report and Hypernative's report put the figure at $10.7–10.8M.
- **Detection:** THORChain's automated solvency monitoring detected abnormal vault balances within minutes of the first unauthorized outbound. Node operators triggered `make pause` via Mimir governance, halting trading, swaps, LP actions, and signing across the network at block 26190429.
- **User funds:** unaffected. Loss limited to one protocol-owned vault.

---

## 2. How it happened (cryptographic mechanics)

### 2.1 The protocol THORChain was running

THORChain uses **GG20** — Gennaro & Goldfeder's 2020 threshold ECDSA protocol — implemented as a fork of Binance's open-source `tss-lib`. The fork branched from `bnb-chain/tss-lib` in late 2020 and has been maintained as a separate codebase since.

A GG20 ceremony involves three phases that matter for this attack:

1. **Distributed Key Generation (DKG)** — Each of 18 nodes generates its own Paillier keypair `(N_i, λ_i)` plus a secret share of the joint ECDSA private key. The shares are committed and verified via several zero-knowledge proofs.
2. **MtA (Multiplicative-to-Additive) sub-protocol** — During signing (and parts of keygen), pairs of nodes need to compute additive shares of the product of their values. This is done by having one party encrypt their value under the other party's Paillier public key, exploiting Paillier's additive homomorphism.
3. **Signature assembly** — The honest nodes combine their partial signatures into a standard ECDSA signature.

The security of the entire scheme depends on a critical invariant: **each peer's Paillier modulus N_i must be well-formed**, specifically a product of exactly two large primes with no hidden small factors. Without this, the homomorphism leaks rather than protects.

### 2.2 The attack primitive

The attacker constructs a Paillier modulus of the form:

```
N = p × q × r
```

where:
- `r` is a small prime (e.g. 40–300 bits) that the attacker retains as a secret
- `p` and `q` are larger primes such that `N` has the expected total bit length (2048 bits in production)

This `N` is broadcast to the other 17 honest committee members during keygen Round 1 as the attacker's claimed Paillier public key. The honest members run their library's structural check on `N` during Round 2.

THORChain's `tss-lib` (v1.x-era fork) performs only a **trial division by primes below 1000**. Since `r` is much larger than 1000 (smallest meaningful variant uses ~40 bits), the malicious `N` passes the check. The 17 honest peers proceed with the ceremony as if Node 7 were honest.

### 2.3 The recovery math

During the MtA sub-protocol, each honest peer encrypts their secret share `x_i ∈ Z_q` (where `q` is the secp256k1 curve order, ~256 bits) under every other peer's Paillier modulus, including the attacker's malicious `N`. The Paillier ciphertext is:

```
c = (1 + N)^{x_i} × s^N   mod N²
```

where `s` is random in `Z_N*`. Reducing the entire equation modulo `r²` (where `r` divides `N`):

- `s^N mod r²` collapses to 1, because the multiplicative order of `Z_{r²}*` is `r(r-1)`, which divides `N(r-1)` since `r | N`.
- `(1+N)^{x_i} mod r²` equals `1 + x_i · N mod r²` by the binomial expansion. Since `r | N`, we can write `N = r · k mod r²` where `k = (N/r) mod r`. So the expression equals `1 + x_i · r · k mod r²`.

Putting these together:

```
c mod r² = 1 + x_i · r · k   mod r²
c^(r-1) mod r² = 1 + x_i · (r-1) · r · k   mod r²
```

Apply the Paillier `L` function (`L_r(u) = (u-1)/r`) and the equation becomes:

```
L_r(c^(r-1) mod r²) = x_i · (r-1) · k   mod r
                    = -x_i · k          mod r       (since r-1 ≡ -1 mod r)
```

Therefore:

```
x_i mod r = -L_r(c^(r-1) mod r²) · k⁻¹   mod r
```

This is a constant number of modular operations — completes in **~0.07 milliseconds** in the PoC. If `r > x_i` (which the attacker arranges by sizing `r` appropriately), `x_i mod r = x_i` exactly, and the honest peer's share is recovered in a single ciphertext.

If `r` is smaller than `x_i`, the attacker recovers `x_i` modulo `r` from each ciphertext. Across multiple signing sessions (the Fireblocks advisory cites "as little as sixteen signing attempts" for two-party recovery), the attacker accumulates enough information to recover `x_i` in full via the Chinese Remainder Theorem.

### 2.4 What the secondary sources describe

Both variants — single-shot keygen extraction and gradual signing-time accumulation — are within the same attack family. Different secondary sources point to slightly different specific variants:

- **Ledger CTO Charles Guillemet's published analysis:** *"compromise one operator, wait for it to churn into an active vault, send malformed proofs during keygen or signing, reconstruct the key offline, and sweep in a single transaction"* — could be either variant.
- **CryptoTimes:** *"the attack appears to have involved the gradual leakage of vault key material during keygen or signing rounds"* — points to the gradual variant.
- **SpazioCrypto:** *"A validator had operated honestly for days, accumulating fragments of cryptographic material during routine GG20 TSS signing ceremonies."* — also points to the gradual variant.

The exact variant cannot be definitively identified without the bifrost peer-to-peer logs from honest committee members. The Hypernative report explicitly hedges on this point. From the defender's perspective the distinction is academic: both variants share the same root cause and are closed by the same fix.

### 2.5 From extracted share to drained vault

Once the attacker has the master vault private key, the rest is mechanically simple. The extracted key is a standard secp256k1 private key — usable on any blockchain that uses ECDSA on this curve, which means Bitcoin, Ethereum, BNB Chain, and Base. The attacker signs `transferOut` transactions from the vault to attacker-controlled addresses. To every node verifying these transactions, the signatures look legitimate, because they are legitimate ECDSA signatures from the vault's actual private key. There is no cryptographic mechanism that can distinguish "vault key signature by the honest committee" from "vault key signature by an attacker who recovered the key offline."

---

## 3. Root cause

There are three levels of root cause. All three are necessary for the incident to occur; addressing only one is insufficient.

### 3.1 Cryptographic root cause: missing structural ZK proofs

GG20 (and its predecessor GG18) is **secure as a protocol specification when all zero-knowledge proofs are present**. The implementation that THORChain ran was missing two critical proofs that should have run during keygen Round 2:

- **`modProof` (Paillier-Blum)**: proves in zero knowledge that `N` is a product of exactly two primes, each ≡ 3 (mod 4). Catches multi-prime `N = p·q·r` constructions immediately.
- **`facProof` (NoSmallFactor)**: proves in zero knowledge that `N` has no prime factor below a safe threshold (Fireblocks' advisory cites 2^100; CGGMP21 formally proves 2^256). Catches the small-`r` variants.

Either proof alone catches the attack class. Both are present in the upstream Binance `tss-lib` as of v2.0.0 (2023), and were never backported to THORChain's fork.

### 3.2 Software supply chain root cause: forked-and-forgotten library

THORChain's `gitlab.com/thorchain/tss/tss-lib` is a fork of `github.com/bnb-chain/tss-lib`, branched from a late-2020 commit. Subsequent security work on Binance's upstream did not flow into the fork:

| Date | Binance upstream | THORChain fork |
|---|---|---|
| 2021–2022 | Routine bug fixes, security updates | Tracking partially |
| Aug 2023 | **v2.0.0 ships modProof + facProof** (PR #206 "Thor chain") | 78-line tactical patch (v0.1.5) — does NOT include modProof or facProof |
| 2024 | v2.0.2, v3.x updates | No security-relevant updates |
| Nov 2025 | — | Engagement with Silence Labs to migrate to DKLS, delivery targeted Q1–Q2 2026 |
| 15 May 2026 | — | **Incident** |

The fork drifted from the upstream security baseline for approximately 33 months between Binance v2.0.0 and the May 2026 incident.

### 3.3 Organizational root cause: no named upstream-tracking owner

The deepest layer: there is no evidence that THORChain operated a named function with responsibility for tracking upstream security commits on their forked cryptographic library. The lesson is not "they were careless" — they explicitly patched both the 2021 Alpha-Rays disclosure and the 2023 TSSHOCK disclosure with reactive fixes. The lesson is that **reactive patching of disclosed CVEs is insufficient when the structural defense exists in upstream but has not been merged**.

Tracking upstream security commits on a forked cryptographic library is itself a load-bearing security function. Without a named owner and a documented review cadence, every fork drifts. Every drift becomes an exposure. THORChain's drift was 33 months. The exposure manifested at $10.7M.

---

## 4. Mitigation

Mitigations are layered by what root cause they address.

### 4.1 Immediate (addresses cryptographic root cause)

1. **Apply the structural ZK proofs.** Implementing `modProof` and `facProof` in keygen Round 2 closes the entire attack class. The reference implementation lives in `bnb-chain/tss-lib/crypto/modproof/proof.go` and `bnb-chain/tss-lib/crypto/facproof/proof.go`, with the merged PR at `bnb-chain/tss-lib#206`.

2. **Regenerate every active vault key.** Critical: once a key has been generated under the vulnerable protocol, it may already be silently compromised. A TSS extraction attack leaves no on-chain trace inside the keygen ceremony itself — the only signal is when funds start moving. THORChain's other five vaults are structurally exposed precisely because they were generated under the same vulnerable library. **Patching the library does not heal already-generated keys.**

3. **Slash and exclude known-malicious operators.** Apply governance mechanisms to remove identified attacker nodes from future committees.

### 4.2 Short-term (addresses supply chain root cause)

4. **SBOM the cryptographic libraries.** Every signing system should have an explicit Software Bill of Materials covering: library name, version, commit hash, last upstream review date, named human owner.

5. **Diff against upstream.** For every forked cryptographic library, generate a diff against the current upstream HEAD. Every security-relevant commit on the upstream side must either be merged or formally declined with documented rationale.

6. **Fuzz the keygen verification path.** Property-based testing: generate 10,000 malformed Paillier moduli (multi-prime, small-factor, non-Blum) and confirm every one is rejected at Round 2 verification.

### 4.3 Long-term (addresses organizational root cause)

7. **Establish a named upstream-tracking function.** One named human, paged on upstream security commits, with a documented review SLA (e.g. 14 days from upstream commit to either merge or documented decline). This is the control THORChain didn't have.

8. **Migrate to a TSS protocol with formal security proofs.** GG20 is now considered legacy; modern alternatives include **CGGMP21** (Canetti et al., 2021) and **DKLS23** (Doerner, Kondi, Lee, shelat, 2023). Both have machine-checkable security proofs and are designed against the post-2023 threat model. THORChain has been migrating to DKLS via Silence Labs since November 2025 — this migration was already planned independent of the incident.

9. **Architectural redundancy.** Consider dual-protocol custody — for example, MPC threshold signing combined with an independent HSM attestation. The attack class demonstrated here breaks one cryptographic protocol; if a second independent protocol must also sign, a single protocol break is insufficient to move funds. This is the architectural pattern that retires the failure mode rather than patching it.

### 4.4 What would NOT have prevented this

For completeness, several familiar controls would have had no effect on this incident:

- **Smart contract audits** — the contracts worked as designed; the failure was in off-chain cryptographic protocol code.
- **More node operators / greater decentralization** — the attack requires only one malicious participant; growing the network does not reduce the probability of one bad actor.
- **Better consensus algorithm** — consensus has no opinion on the cryptographic provenance of a signature.
- **Multisig wallets** — TSS *is* a multisig pattern; the underlying cryptography is what failed.
- **Phishing protection / OpSec hardening** — no human in the loop was social-engineered; the attacker exploited cryptographic protocol code directly.
- **Bug bounty program** — THORChain co-funded the original Alpha-Rays bounty in 2021. The class was known. The fix was available. Money is not the issue.

The bitter irony: THORChain helped pay for the discovery of this attack class four years before being exploited by it. The fix existed in upstream for two years before the incident. The organizational mechanism to merge available fixes is what was missing.

---

## 5. References

- THORChain ADR-028 exploit report (May 2026)
- Hypernative Incident Report 2026-05-15
- Ledger CTO Charles Guillemet's published analysis (May 2026)
- `bnb-chain/tss-lib` v2.0.0 release notes: https://github.com/bnb-chain/tss-lib/releases
- `bnb-chain/tss-lib` PR #206 ("Thor chain"): https://github.com/bnb-chain/tss-lib/pull/206
- Fireblocks BitForge disclosure (CVE-2023-33241, GHSA-5cjx-95fx-68q9, May 2023)
- Verichains TSSHOCK disclosure (Black Hat USA 2023)
- Gennaro, R. & Goldfeder, S. (2020). "One Round Threshold ECDSA with Identifiable Abort." IACR ePrint 2020/540.
- Canetti, R., Gennaro, R., Goldfeder, S., Makriyannis, N., Peled, U. (2020). "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts." ACM CCS 2020. (CGGMP21 update: ePrint 2021/060.)
- Doerner, J., Kondi, Y., Lee, E., shelat, abhi. (2023). "Threshold ECDSA in Three Rounds." ePrint 2023/765 / IEEE S&P 2024.

---

## Appendix: running the PoC

```bash
pip install gmpy2
python3 thorchain_poc.py
```

Total execution time: ~15 seconds on a laptop. No network access required. The script:

1. Generates an honest Paillier keypair and verifies the additive homomorphism (baseline)
2. Constructs a malicious modulus `N = p × q × r` with a 300-bit hidden factor
3. Confirms the vulnerable check accepts it
4. Recovers an honest peer's secret share via partial decryption in ~0.07 ms
5. Demonstrates `modProof` rejecting the malicious modulus
6. Demonstrates `facProof` rejecting a small-`r` variant
7. Runs the full attack scenario with v2.x defenses active, showing the ceremony aborts at Round 2

All cryptographic claims in this briefing are reproducible by running the script.
