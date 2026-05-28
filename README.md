# THORChain Asgard Vault Compromise — Proof of Concept

A reproducible technical demonstration of the May 15, 2026 THORChain incident, prepared for a team review of what happened and what needs to change to prevent recurrence.

## Files

| File | Purpose |
|---|---|
| `thorchain_poc.py` | Runnable cryptographic demonstration. Reproduces the attack and the defense end-to-end in ~15 seconds. |
| `BRIEFING.md` | Written explainer (5 pages). Covers what happened, how, root cause, and mitigation. |
| `README.md` | This file. |

## How to use this

**For a team meeting:** read `BRIEFING.md` first (10–15 minutes), then run `thorchain_poc.py` live to show the cryptography working. The script prints clear stage-by-stage output so the audience can follow along without needing to read the code.

**For a written review:** `BRIEFING.md` is self-contained. Every cryptographic claim it makes is backed by a corresponding section of the PoC script that any reader can run themselves.

**For independent verification:** every fact in the briefing is sourced. Primary sources include THORChain's own ADR-028 exploit report, Binance's tss-lib v2.0.0 release notes, the merged PR #206, the Fireblocks BitForge advisory (CVE-2023-33241), and Ledger CTO Charles Guillemet's published analysis. See the References section of `BRIEFING.md`.

## Running the PoC

```bash
pip install gmpy2
python3 thorchain_poc.py
```

The script has zero external runtime dependencies beyond `gmpy2` for arbitrary-precision arithmetic. It runs offline, with no network access required. Output is plain text written to stdout in seven stages:

1. Healthy Paillier operations (baseline)
2. Constructing the malicious modulus
3. Bypassing the vulnerable check
4. Recovering an honest peer's secret share
5. The defense (Binance v2.0.0 structural ZK proofs)
6. End-to-end with v2.x defenses active
7. What THORChain didn't merge (disclosure timeline)

Each stage prints its own narrative and the actual computed values, so the cryptographic claims are visible to anyone watching the script execute.

## What the PoC demonstrates

In one sentence: **a single malicious participant in a GG20 threshold signature ceremony can extract the full master private key, in milliseconds, if the library does not enforce structural zero-knowledge proofs on the Paillier moduli — and THORChain's tss-lib fork never adopted these proofs.**

In three observations:

1. **The vulnerable check is insufficient.** THORChain's tss-lib performed only a trial-division check by primes < 1000 on peer-submitted Paillier moduli. The attack uses a modulus `N = p × q × r` where `r` is a 40–300 bit prime — comfortably above the small-prime bound, so it passes. This is the `vulnerable_modulus_check()` function in the script.

2. **The recovery primitive is fast and silent.** Given any Paillier ciphertext encrypted under the malicious `N`, and the secret factor `r`, the attacker recovers the plaintext modulo `r` in ~0.07 milliseconds via partial decryption. This is the `attacker_extract_share()` function. The honest peer that produced the ciphertext has no way to detect the recovery.

3. **The defense exists and is small.** Two zero-knowledge proofs — `modProof` (Paillier-Blum biprimality) and `facProof` (NoSmallFactor) — are sufficient to reject the malicious modulus during keygen Round 2. These are the `mod_proof_verify()` and `fac_proof_verify()` functions. Both proofs were merged into Binance's upstream `tss-lib` via PR #206 in 2023. THORChain's fork did not adopt them.

## What this PoC is not

- It is not the exact bit-for-bit reproduction of the THORChain attacker's specific variant. The exact variant cannot be publicly identified without bifrost peer-to-peer logs from honest committee members. The attack family is the same, and the defense is identical regardless of variant.
- It is not a runnable exploit against THORChain. The mathematics is the same as the real attack, but the script operates entirely on locally generated values — no real keys, no real vault, no network access.
- It is not a Go-language reproduction against the actual tss-lib codebase. The Python implementation focuses on the cryptographic primitive for clarity and auditability. The structural defenses are implemented semantically (the check that determines accept vs. reject) rather than as full Fiat-Shamir zero-knowledge proofs.

## Honest scope limitations

The Python defense implementations (`mod_proof_verify`, `fac_proof_verify`) check the structural properties directly rather than running the full cryptographic apparatus of the real ZK proofs. The real proofs use Pedersen commitments, sigma protocols, and Fiat-Shamir transformations to verify the same structural properties in zero knowledge from a prover who controls the witness. The criterion that determines accept vs. reject is identical — what differs is the cryptographic machinery for verifying it. For production use, audit `bnb-chain/tss-lib/crypto/modproof/proof.go` and `bnb-chain/tss-lib/crypto/facproof/proof.go` directly.

## Questions this PoC is designed to answer

After running it, the team should be able to answer:

- What is the specific cryptographic operation that fails?
- Why does the current check pass when it shouldn't?
- What does the fix look like, concretely?
- Is the fix small or large? (Answer: small — a few hundred lines of Go code total, available in upstream since 2023.)
- What do we need to do in our own infrastructure to make sure this can't happen to us?

The last question is the operational question and is addressed in Section 4 of `BRIEFING.md`.
